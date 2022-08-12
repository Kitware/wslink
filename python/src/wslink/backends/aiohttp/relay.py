import argparse
import asyncio
import os
import logging
import aiohttp
from aiohttp import web

# -----------------------------------------------------------------------------
# 4MB is the default inside aiohttp
# -----------------------------------------------------------------------------

MAX_MSG_SIZE = int(os.environ.get("WSLINK_MAX_MSG_SIZE", 4194304))
HEART_BEAT = int(os.environ.get("WSLINK_HEART_BEAT", 30))  # 30 seconds

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -----------------------------------------------------------------------------
# Helper classes
# -----------------------------------------------------------------------------


class WsClientConnection:
    def __init__(self, propagate_disconnect=True):
        self._url = None
        self._session = None
        self._ws = None
        self._connected = 0
        self._destination = None
        self._ready = asyncio.get_running_loop().create_future()
        self.propagate_disconnect = propagate_disconnect

    def bind(self, value):
        self._destination = value

    @property
    def ready(self):
        return self._ready

    async def connect(self, url):
        logger.debug("client::connect::%s", url)
        self._url = url
        if self._session is None:
            async with aiohttp.ClientSession() as session:
                logger.debug("client::connect::session")
                self._session = session
                try:
                    async with session.ws_connect(self._url) as ws:
                        logger.debug("client::connect::ws")
                        self._ws = ws
                        self._connected += 1
                        self._ready.set_result(True)
                        async for msg in ws:
                            logger.debug("client::connect::ws::msg")
                            if self._connected < 1:
                                logger.debug("client::connect::ws::msg::disconnect")
                                break

                            if self._destination:
                                logger.debug("client::connect::ws::msg::send")
                                await self._destination.send(msg)
                            else:
                                logger.error("ws-client: No destination for message")

                        # Disconnect
                        self.disconnect()

                        # Cleanup connection
                        if not self._ws.closed:
                            await self._ws.close()
                        self._ws = None
                        self._session = None
                finally:
                    self._ready.set_result(False)

        logger.debug("client::connect::exit")

    async def send(self, msg):
        if self._connected > 0 and not self._ws.closed:
            logger.debug("client::send")
            if msg.type == aiohttp.WSMsgType.TEXT:
                await self._ws.send_str(msg.data)
            elif msg.type == aiohttp.WSMsgType.BINARY:
                await self._ws.send_bytes(msg.data)
            elif msg.type == aiohttp.WSMsgType.PING:
                await self._ws.ping(msg.data)
            elif msg.type == aiohttp.WSMsgType.PONG:
                await self._ws.pong(msg.data)
            elif msg.type == aiohttp.WSMsgType.CLOSE:
                await self._ws.close()
            else:
                logger.error("Invalid message to forward")
        else:
            logger.error("client::send - NO SEND")
            logger.error("%s - %s", self._connected, self._ws.closed)
            logger.error("-" * 60)

    def disconnect(self):
        logger.debug("client::disconnect %s", self._connected)
        if self._connected > 0:
            self._connected = -1
            if self._destination and self.propagate_disconnect:
                self._destination.disconnect()

    async def close(self):
        if self._ws is not None:
            await self._ws.close()


# -----------------------------------------------------------------------------


class WsServerConnection:
    def __init__(self, propagate_disconnect=True):
        self._ws = None
        self._destination = None
        self._connected = 0
        self.propagate_disconnect = propagate_disconnect

    def bind(self, value):
        self._destination = value

    async def connect(self, request):
        logger.debug("server::connect")
        self._ws = web.WebSocketResponse(
            max_msg_size=MAX_MSG_SIZE, heartbeat=HEART_BEAT
        )
        await self._ws.prepare(request)
        logger.debug("server::connect::prepare")
        self._connected += 1

        if self._connected > 0:
            async for msg in self._ws:
                logger.debug("server::connect::ws::msg")
                if self._connected < 1:
                    break

                if self._destination:
                    logger.debug("server::connect::ws::msg::send-begin")
                    await self._destination.send(msg)
                    logger.debug("server::connect::ws::msg::send-end")
                else:
                    logger.error("ws-server: No destination for message")

        # Disconnect
        self.disconnect()

        # Cleanup connection
        if not self._ws.closed:
            await self._ws.close()
        self._ws = None

        logger.debug("server::connect::exit")

    async def send(self, msg):
        if self._connected > 0 and not self._ws.closed:
            logger.debug("server::send")
            if msg.type == aiohttp.WSMsgType.TEXT:
                await self._ws.send_str(msg.data)
            elif msg.type == aiohttp.WSMsgType.BINARY:
                await self._ws.send_bytes(msg.data)
            elif msg.type == aiohttp.WSMsgType.PING:
                await self._ws.ping(msg.data)
            elif msg.type == aiohttp.WSMsgType.PONG:
                await self._ws.pong(msg.data)
            elif msg.type == aiohttp.WSMsgType.CLOSE:
                await self._ws.close()
            else:
                logger.error("Invalid message to forward")
        else:
            logger.error("server::send - NO SEND")
            logger.error("%s - %s", self._connected, self._ws.closed)
            logger.error("-" * 60)

    def disconnect(self):
        logger.debug("server::disconnect %s", self._connected)
        if self._connected > 0:
            self._connected = -1
            if self._destination and self.propagate_disconnect:
                self._destination.disconnect()

    async def close(self):
        if self._ws is not None:
            await self._ws.close()


# -----------------------------------------------------------------------------


class ForwardConnection:
    def __init__(self, request, url):
        self._req = request
        self._url = url
        self._ws_client = WsClientConnection()
        self._ws_server = WsServerConnection()
        self._ws_server.bind(self._ws_client)
        self._ws_client.bind(self._ws_server)

    async def connect(self):
        task = asyncio.create_task(self._ws_client.connect(self._url))
        task.add_done_callback(lambda *args, **kwargs: self._ws_server.disconnect())
        await self._ws_client.ready
        await self._ws_server.connect(self._req)

    def disconnect(self):
        self._ws_client.disconnect()
        self._ws_server.disconnect()


class SinkConnection:
    def __init__(self, request):
        self._process_req = request
        self._client_req = None
        self._process_ws = None
        self._client_ws = None

    def can_handle(self, request):
        if self._process_req == request:
            return True

        if self._client_req == request:
            return True

        if self._client_ws is None:
            return True

        return False

    async def connect(self, request):
        if self._process_req == request:
            # First connection is the actual server. Cannot reconnect.
            self._process_ws = WsServerConnection()
            await self._process_ws.connect(request)
            if self._client_ws is not None:
                await self._client_ws.close()

            return True
        elif self._client_req is None:
            # Second connection is the browser. Can reconnect.
            self._client_req = request
            self._client_ws = WsServerConnection(propagate_disconnect=False)
            self._client_ws.bind(self._process_ws)
            self._process_ws.bind(self._client_ws)
            await self._client_ws.connect(request)

            self._client_ws.bind(None)
            self._process_ws.bind(None)

            self._client_req = None
            self._client_ws = None

        return False


# -----------------------------------------------------------------------------
# Handlers
# -----------------------------------------------------------------------------


async def _root_handler(request):
    if request.query_string:
        return web.HTTPFound(f"index.html?{request.query_string}")
    return web.HTTPFound("index.html")


# -----------------------------------------------------------------------------


class WsHandler:
    def __init__(self):
        self._forward_map = {}
        self._relay_map = {}

    def get_handler(self, mode="forward"):
        logger.info("get_handler %s", mode)
        if mode == "forward":
            return self.forward_connect
        if mode == "relay":
            return self.relay_connect
        logger.error("No handler !!!")

    # -----------------------------
    # forward infrastructure
    # -----------------------------

    async def forward_connect(self, request):
        host = request.match_info.get("host", "localhost")
        port = int(request.match_info.get("port", "1234"))
        path = request.match_info.get("path", "ws")
        target_url = f"ws://{host}:{port}/{path}"
        logger.info("=> %s", target_url)

        if target_url in self._forward_map:
            raise web.HTTPForbidden()

        forwarder = ForwardConnection(request, target_url)
        self._forward_map[target_url] = forwarder
        await forwarder.connect()
        self._forward_map.pop(target_url)

    # -----------------------------
    # relay server infrastructure
    # -----------------------------

    async def relay_connect(self, request):
        id = request.path

        if id not in self._relay_map:
            handler = SinkConnection(request)
            self._relay_map[id] = handler

        handler = self._relay_map[id]
        if not handler.can_handle(request):
            raise web.HTTPForbidden()

        if await handler.connect(request):
            # Only pop when the server dies
            self._relay_map.pop(id)


# -----------------------------------------------------------------------------
# Executable
# -----------------------------------------------------------------------------


def main(host=None, port=None, www_path=None, proxy_route=None, mode=None):
    wsRelay = WsHandler()

    # Handle CLI
    parser = argparse.ArgumentParser(
        description="Start ws relay with static content delivery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="the interface for the web-server to listen on (default: 0.0.0.0)",
        dest="host",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8080,
        help="port number for the web-server to listen on (default: 8080)",
        dest="port",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="forward",
        help="Working mode [forward, relay] (default: forward)",
    )
    parser.add_argument("--www", type=str, help="Directory to serve", dest="www_path")
    parser.add_argument(
        "--proxy-route",
        type=str,
        help="Proxy URL pattern (default: /proxy/{port}) mode::forward(ws://{host=localhost}:{port=1234}/{path=ws})",
        default="/proxy/{port}",
        dest="proxy_route",
    )
    args, _ = parser.parse_known_args()

    if host is None:
        host = args.host

    if port is None:
        port = args.port

    if mode is None:
        mode = args.mode

    if www_path is None:
        www_path = args.www_path

    if proxy_route is None:
        proxy_route = args.proxy_route

    logging.basicConfig()

    # Manage routes
    routes = []

    # Need to be first: static delivery should be a fallback
    if proxy_route is not None:
        logger.info("Proxy route: %s", proxy_route)
        routes.append(web.get(proxy_route, wsRelay.get_handler(mode)))

    # Serve static content
    if www_path is not None:
        logger.info("WWW: %s", www_path)
        routes.append(web.get("/", _root_handler))
        routes.append(web.static("/", www_path))

    # Setup web app
    logger.info("Starting relay server: %s %s", host, port)
    web_app = web.Application()
    web_app.add_routes(routes)
    web.run_app(web_app, host=host, port=port)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
