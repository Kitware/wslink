from __future__ import annotations

import contextlib
import json
import logging
import mimetypes
import os
import socket
import threading
import uuid
from pathlib import Path
from urllib.parse import urlencode

# Backend specific imports
from robyn import Robyn
from robyn.robyn import Headers, Response
from robyn.ws import WebSocketDisconnect

from wslink.protocol import AbstractWebApp, WslinkHandler

HTTP_HEADERS = os.environ.get("WSLINK_HTTP_HEADERS")  # path to json file
STARTUP_TIMEOUT = float(os.environ.get("WSLINK_ROBYN_STARTUP_TIMEOUT", "30"))

if HTTP_HEADERS and Path(HTTP_HEADERS).exists():
    HTTP_HEADERS = json.loads(Path(HTTP_HEADERS).read_text())

logger = logging.getLogger(__name__)


def reload_settings():
    global HTTP_HEADERS  # noqa: PLW0603

    HTTP_HEADERS = os.environ.get("WSLINK_HTTP_HEADERS", HTTP_HEADERS)


# -----------------------------------------------------------------------------
# HTTP helpers
# -----------------------------------------------------------------------------


def _fix_path(path):
    if not path.startswith("/"):
        return f"/{path}"
    return path


def _resolve_host(host):
    """Robyn's socket binding (SocketHeld) requires a literal IP address and
    does not resolve hostnames itself, unlike the other backends, so
    "localhost" (wslink's own default) must be turned into "127.0.0.1"."""
    try:
        return socket.gethostbyname(host)
    except OSError:
        return host


def _response_headers(extra=None):
    headers = {}
    if HTTP_HEADERS:
        headers.update(HTTP_HEADERS)
    if extra:
        headers.update(extra)
    return Headers(headers)


def _guess_mime(name):
    return mimetypes.guess_type(name)[0] or "application/octet-stream"


def _serve_bytes(data, filename):
    return Response(
        status_code=200,
        headers=_response_headers({"content-type": _guess_mime(filename)}),
        description=data,
    )


# -----------------------------------------------------------------------------
# WS protocol definition
# -----------------------------------------------------------------------------


class _IncomingMessage:
    """Minimal wrapper so WslinkHandler.onMessage() can read `.data`, like the
    message objects the other backends hand it."""

    __slots__ = ("data",)

    def __init__(self, data):
        self.data = data


class RobynWsConnection:
    """Adapts robyn's WebSocketAdapter to the send_bytes()/close() interface
    that WslinkHandler expects from an entry in `self.connections`."""

    def __init__(self, adapter):
        self._adapter = adapter
        self.closed = False

    async def send_bytes(self, data):
        if self.closed:
            return
        with contextlib.suppress(Exception):
            await self._adapter.send_bytes(data)

    async def close(self, code=None, message=None):  # noqa: ARG002
        self.closed = True
        with contextlib.suppress(Exception):
            await self._adapter.close()


class RobynWsHandler(WslinkHandler):
    async def disconnectClients(self):
        logger.info("Closing client connections:")
        for client_id, ws in list(self.connections.items()):
            logger.info("  %s", client_id)
            await ws.close()

        self.publishManager.unregisterProtocol(self)

    async def handle_connection(self, adapter):
        client_id = str(uuid.uuid4()).replace("-", "")
        self.connections[client_id] = RobynWsConnection(adapter)

        logger.info("client %s connected", client_id)

        self.web_app.shutdown_cancel()

        try:
            await self.onConnect(adapter, client_id)
            while True:
                data = await adapter.receive_bytes()
                await self.onMessage(True, _IncomingMessage(data), client_id)
        except WebSocketDisconnect:
            pass
        finally:
            await self.onClose(client_id)

            self.connections.pop(client_id, None)
            self.authentified_client_ids.discard(client_id)

            logger.info("client %s disconnected", client_id)

            if not self.connections:
                logger.info("No more connections, scheduling shutdown")
                self.web_app.shutdown_schedule()


# -----------------------------------------------------------------------------
# Web application
# -----------------------------------------------------------------------------


class WebAppServer(AbstractWebApp):
    """
    DISCLAIMER
    ----------
    Robyn owns its worker thread: its `Robyn.start()` call is blocking and
    sets up its own asyncio event loop, so it is run in a dedicated
    background thread here rather than sharing the loop the rest of wslink
    runs on. Any code that runs as a result of a client connecting/sending a
    message (RPC handlers, publish(), schedule_coroutine(), ...) therefore
    executes on that background thread's event loop, which is consistent as
    long as it is treated as *the* event loop for the lifetime of the
    connection. Robyn does not expose a way to cleanly stop its HTTP/WS
    listener once started (no `Server.stop()`), so `stop()` disconnects
    known clients and resolves the wslink completion future so the calling
    coroutine can return, but the background thread (a daemon thread) keeps
    listening until the whole process exits.
    """

    def __init__(self, server_config):
        reload_settings()
        AbstractWebApp.__init__(self, server_config)

        self._robyn_app = Robyn(__file__)
        self._robyn_app.config.disable_openapi = True
        self._robyn_app.config.log_level = os.environ.get(
            "WSLINK_ROBYN_LOG_LEVEL", "WARN"
        )
        self.set_app(self._robyn_app)

        self._ws_handlers = []
        self._thread = None
        self._ready_event = threading.Event()
        self._start_error = None
        self._static_mounts = []
        self._follow_symlinks = False

        if "ws" in server_config:
            for route, server_protocol in server_config["ws"].items():
                handler = RobynWsHandler(server_protocol, self)
                self._ws_handlers.append(handler)

                # The websocket decorator stashes on_connect/on_close callbacks
                # as attributes on the handler it receives, which a bound
                # method does not support, so route through a plain function.
                async def _ws_entry(adapter, _handler=handler):
                    await _handler.handle_connection(adapter)

                self._robyn_app.websocket(_fix_path(route))(_ws_entry)

        if "static" in server_config:
            static_routes = server_config["static"]
            self._follow_symlinks = server_config.get(
                "static_follow_symlinks", False
            ) or bool(int(os.environ.get("WSLINK_FOLLOW_SYMLINKS", "0")))

            # Ensure longer (more specific) mounts are matched first
            self._static_mounts = sorted(
                (
                    (_fix_path(route), Path(server_path))
                    for route, server_path in static_routes.items()
                ),
                key=lambda mount: len(mount[0]),
                reverse=True,
            )

            self._robyn_app.get("/")(self._root_handler)
            self._robyn_app.get("/*wslink_static_path")(self._static_handler)

        self._robyn_app.startup_handler(self._on_startup)

    # -------------------------------------------------------------------------
    # Static content
    # -------------------------------------------------------------------------

    def _resolve_static_file(self, request_path):
        request_path = _fix_path(request_path)
        for prefix, directory in self._static_mounts:
            mount_dir = prefix if prefix.endswith("/") else f"{prefix}/"
            if request_path != prefix.rstrip("/") and not request_path.startswith(
                mount_dir
            ):
                continue

            rel = request_path[len(prefix) :].lstrip("/")
            base = directory.resolve()
            candidate = (base / rel).resolve() if rel else base

            with contextlib.suppress(ValueError):
                candidate.relative_to(base)
                if candidate.is_file():
                    return candidate

        return None

    async def _root_handler(self, request):
        queries = getattr(request.query_params, "queries", None) or {}
        target = "index.html"
        if queries:
            target = f"index.html?{urlencode(queries, doseq=True)}"
        return Response(
            status_code=302,
            headers=_response_headers({"location": target}),
            description=b"",
        )

    async def _static_handler(self, request):
        rel = request.path_params.get("wslink_static_path", "")
        candidate = self._resolve_static_file(f"/{rel}")
        if candidate is None:
            return Response(
                status_code=404, headers=_response_headers(), description=b"Not found"
            )
        return _serve_bytes(candidate.read_bytes(), candidate.name)

    # -------------------------------------------------------------------------
    # Server status
    # -------------------------------------------------------------------------

    def get_port(self):
        """Return the actual port used by the server"""
        return self.port

    # -------------------------------------------------------------------------
    # Life cycles
    # -------------------------------------------------------------------------

    async def _on_startup(self):
        self._ready_event.set()

    def _run_robyn(self):
        try:
            self._robyn_app.start(
                host=_resolve_host(self.host), port=self.port, _check_port=False
            )
        except Exception as exc:
            self._start_error = exc
            self._ready_event.set()

    async def start(self, port_callback=None):
        loop = self._completion.get_loop()

        self._thread = threading.Thread(
            target=self._run_robyn, name="wslink-robyn", daemon=True
        )
        self._thread.start()

        ready = await loop.run_in_executor(
            None, self._ready_event.wait, STARTUP_TIMEOUT
        )
        if self._start_error is not None:
            raise self._start_error
        if not ready:
            msg = f"robyn backend did not start within {STARTUP_TIMEOUT}s"
            raise RuntimeError(msg)

        if port_callback is not None:
            port_callback(self.get_port())

        logger.info("Print WSLINK_READY_MSG")
        STARTUP_MSG = os.environ.get("WSLINK_READY_MSG", "wslink: Starting factory")
        if STARTUP_MSG:
            # Emit an expected log message so launcher.py knows we've started up.
            os.write(1, STARTUP_MSG.encode())

        logger.info("Schedule auto shutdown with timeout %s", self.timeout)
        self.shutdown_schedule()

        logger.info("awaiting running future")
        await self.completion

    async def stop(self):
        for handler in self._ws_handlers:
            await handler.disconnectClients()

        logger.info("Stopping server")
        loop = self._completion.get_loop()
        if not self._completion.done():
            loop.call_soon_threadsafe(self._completion.set_result, True)


def create_webserver(server_config):
    if server_config.get("logging_level"):
        logging.getLogger("wslink").setLevel(server_config["logging_level"])

    if "reverse_url" in server_config:
        msg = "Robyn backend does not support reverse_url"
        raise NotImplementedError(msg)

    return WebAppServer(server_config)


def startWebServer(*args, **kwargs):
    msg = "Robyn backend does not provide a launcher"
    raise NotImplementedError(msg)
