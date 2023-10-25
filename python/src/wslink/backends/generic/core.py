import asyncio
import logging
import uuid
from pathlib import Path
import shutil

from wslink.protocol import WslinkHandler, AbstractWebApp


class WsConnection:
    def __init__(self):
        self._id = str(uuid.uuid4()).replace("-", "")
        self._ws = None
        self._on_message_fn = None
        self.closed = True

    # -------------------------------------------------------------------------
    # Method to be used by user
    # -------------------------------------------------------------------------

    def on_message(self, callback):
        self._on_message_fn = callback

    async def send(self, is_binary, msg):
        await self._ws.onMessage(is_binary, msg, self.client_id)

    def close(self):
        self._ws.disconnect(self)

    # -------------------------------------------------------------------------
    # Method used by FakeWS
    # -------------------------------------------------------------------------

    @property
    def client_id(self):
        return self._id

    def on_connect(self, ws):
        self.closed = False
        self._ws = ws

    def on_close(self, ws):
        self.closed = True
        if self._ws == ws:
            self._ws = None

    async def send_str(self, value):
        await self._on_message_fn(False, value)

    async def send_bytes(self, value):
        await self._on_message_fn(True, value)


class WsEndpoint(WslinkHandler):
    def __init__(self, protocol=None, web_app=None):
        super().__init__(protocol, web_app)

    def connect(self):
        conn = WsConnection()
        self.connections[conn.client_id] = conn
        conn.on_connect(self)
        return conn

    def disconnect(self, client_or_id):
        client_or_id = (
            client_or_id if isinstance(client_or_id, str) else client_or_id.client_id
        )
        if client_or_id in self.connections:
            client = self.connections.pop(client_or_id)
            client.on_close(self)


class GenericServer(AbstractWebApp):
    def __init__(self, server_config):
        AbstractWebApp.__init__(self, server_config)
        self._websockets = {}
        self._stop_event = asyncio.Event()

        if "ws" in server_config:
            for route, server_protocol in server_config["ws"].items():
                protocol_handler = WsEndpoint(server_protocol, self)
                self._websockets[route] = protocol_handler

    def write_static_content(self, dest_directory):
        dest = Path(dest_directory)
        dest.mkdir(exist_ok=True, parents=True)
        if "static" in self._config:
            static_routes = self._config["static"]
            for route in sorted(static_routes.keys()):
                server_path = static_routes[route]
                if route == "/":
                    src = Path(server_path)
                    for child in src.iterdir():
                        if child.is_dir():
                            shutil.copytree(child, dest / child.name)
                        else:
                            shutil.copy2(child, dest / child.name)
                else:
                    shutil.copytree(server_path, dest / route)

    def __getattr__(self, attr):
        return self._websockets.get(attr, None)

    def __getitem__(self, name):
        return self._websockets.get(name, None)

    @property
    def ws_endpoints(self):
        return list(self._websockets.keys())

    async def start(self, port_callback):
        if port_callback is not None:
            port_callback(self.get_port())

        self._stop_event.clear()
        await self._stop_event.wait()

    async def stop(self):
        self._stop_event.set()


def startWebServer(*args, **kwargs):
    raise NotImplementedError("Generic backend does not provide a launcher")


def create_webserver(server_config):
    if "logging_level" in server_config and server_config["logging_level"]:
        logging.getLogger("wslink").setLevel(server_config["logging_level"])

    # Reverse connection
    if "reverse_url" in server_config:
        raise NotImplementedError("Generic backend does not support reverse_url")

    return GenericServer(server_config)
