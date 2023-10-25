import asyncio
import os
import logging
import sys
import uuid

from wslink.protocol import WslinkHandler, AbstractWebApp

# Backend specific imports
import aiohttp
import aiohttp.web as aiohttp_web


# 4MB is the default inside aiohttp
MAX_MSG_SIZE = int(os.environ.get("WSLINK_MAX_MSG_SIZE", 4194304))
HEART_BEAT = int(os.environ.get("WSLINK_HEART_BEAT", 30))  # 30 seconds

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# HTTP helpers
# -----------------------------------------------------------------------------


async def _root_handler(request):
    if request.query_string:
        return aiohttp.web.HTTPFound(f"index.html?{request.query_string}")
    return aiohttp.web.HTTPFound("index.html")


def _fix_path(path):
    if not path.startswith("/"):
        return "/{0}".format(path)
    return path


# -----------------------------------------------------------------------------


class WebAppServer(AbstractWebApp):
    def __init__(self, server_config):
        AbstractWebApp.__init__(self, server_config)
        self.set_app(aiohttp_web.Application())
        self._ws_handlers = []
        self._site = None
        self._runner = None

        if "ws" in server_config:
            routes = []
            for route, server_protocol in server_config["ws"].items():
                protocol_handler = AioHttpWsHandler(server_protocol, self)
                self._ws_handlers.append(protocol_handler)
                routes.append(
                    aiohttp_web.get(_fix_path(route), protocol_handler.handleWsRequest)
                )

            self.app.add_routes(routes)

        if "static" in server_config:
            static_routes = server_config["static"]
            routes = []

            # Ensure longer path are registered first
            for route in sorted(static_routes.keys(), reverse=True):
                server_path = static_routes[route]
                routes.append(
                    aiohttp_web.static(
                        _fix_path(route), server_path, append_version=True
                    )
                )

            # Resolve / => index.html
            self.app.router.add_route("GET", "/", _root_handler)
            self.app.add_routes(routes)

        self.app["state"] = {}

    # -------------------------------------------------------------------------
    # Server status
    # -------------------------------------------------------------------------

    @property
    def runner(self):
        return self._runner

    @property
    def site(self):
        return self._site

    def get_port(self):
        """Return the actual port used by the server"""
        return self.runner.addresses[0][1]

    # -------------------------------------------------------------------------
    # Life cycles
    # -------------------------------------------------------------------------

    async def start(self, port_callback=None):
        self._runner = aiohttp_web.AppRunner(
            self.app, handle_signals=self.handle_signals
        )

        logger.info("awaiting runner setup")
        await self._runner.setup()

        self._site = aiohttp_web.TCPSite(
            self._runner, self.host, self.port, ssl_context=self.ssl_context
        )

        logger.info("awaiting site startup")
        await self._site.start()

        if port_callback is not None:
            port_callback(self.get_port())

        logger.info("Print WSLINK_READY_MSG")
        STARTUP_MSG = os.environ.get("WSLINK_READY_MSG", "wslink: Starting factory")
        if STARTUP_MSG:
            # Emit an expected log message so launcher.py knows we've started up.
            print(STARTUP_MSG)
            # We've seen some issues with stdout buffering - be conservative.
            sys.stdout.flush()

        logger.info(f"Schedule auto shutdown with timout {self.timeout}")
        self.shutdown_schedule()

        logger.info("awaiting running future")
        await self.completion

    async def stop(self):
        # Disconnecting any connected clients of handler(s)
        for handler in self._ws_handlers:
            await handler.disconnectClients()

        # Neither site.stop() nor runner.cleanup() actually stop the server
        # as documented, but at least runner.cleanup() results in the
        # "on_shutdown" signal getting sent.
        logger.info("Performing runner.cleanup()")
        await self.runner.cleanup()

        # So to actually stop the server, the workaround is just to resolve
        # the future we awaited in the start method.
        logger.info("Stopping server")
        self.completion.set_result(True)


class ReverseWebAppServer(AbstractWebApp):
    def __init__(self, server_config):
        super().__init__(server_config)
        self._url = server_config.get("reverse_url")
        self._server_protocol = server_config.get("ws_protocol")
        self._ws_handler = AioHttpWsHandler(self._server_protocol, self)

    async def start(self, port_callback=None):
        if port_callback is not None:
            port_callback(0)

        await self._ws_handler.reverse_connect_to(self._url)

    async def stop(self):
        client_id = self._ws_handler.reverse_connection_client_id
        ws = self._ws_handler.connections[client_id]
        await ws.close()


def create_webserver(server_config):
    if "logging_level" in server_config and server_config["logging_level"]:
        logging.getLogger("wslink").setLevel(server_config["logging_level"])

    # Shortcut for reverse connection
    if "reverse_url" in server_config:
        return ReverseWebAppServer(server_config)

    # Normal web server
    return WebAppServer(server_config)


# -----------------------------------------------------------------------------
# WS protocol definition
# -----------------------------------------------------------------------------


def is_binary(msg):
    return msg.type == aiohttp.WSMsgType.BINARY


class AioHttpWsHandler(WslinkHandler):
    async def disconnectClients(self):
        logger.info("Closing client connections:")
        keys = list(self.connections.keys())
        for client_id in keys:
            logger.info("  {0}".format(client_id))
            ws = self.connections[client_id]
            await ws.close(
                code=aiohttp.WSCloseCode.GOING_AWAY, message="Server shutdown"
            )

        self.publishManager.unregisterProtocol(self)

    async def handleWsRequest(self, request):
        client_id = str(uuid.uuid4()).replace("-", "")
        current_ws = aiohttp_web.WebSocketResponse(
            max_msg_size=MAX_MSG_SIZE, heartbeat=HEART_BEAT
        )
        self.connections[client_id] = current_ws

        logger.info("client {0} connected".format(client_id))

        self.web_app.shutdown_cancel()

        try:
            await current_ws.prepare(request)
            await self.onConnect(request, client_id)
            async for msg in current_ws:
                await self.onMessage(is_binary(msg), msg, client_id)
        finally:
            await self.onClose(client_id)

            del self.connections[client_id]
            self.authentified_client_ids.discard(client_id)

            logger.info("client {0} disconnected".format(client_id))

            if not self.connections:
                logger.info("No more connections, scheduling shutdown")
                self.web_app.shutdown_schedule()

        return current_ws

    async def reverse_connect_to(self, url):
        logger.debug("reverse_connect_to: running with url %s", url)
        client_id = self.reverse_connection_client_id
        async with aiohttp.ClientSession() as session:
            logger.debug("reverse_connect_to: client session started")
            async with session.ws_connect(url) as current_ws:
                logger.debug("reverse_connect_to: ws started")
                self.connections[client_id] = current_ws
                logger.debug("reverse_connect_to: onConnect")
                await self.onConnect(url, client_id)

                async for msg in current_ws:
                    if not current_ws.closed:
                        await self.onMessage(is_binary(msg), msg, client_id)

                logger.debug("reverse_connect_to: onClose")
                await self.onClose(client_id)
                del self.connections[client_id]

        logger.debug("reverse_connect_to: exited")
