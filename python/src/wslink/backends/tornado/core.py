# -----------------------------------------------------------------------------
# DISCLAIMER
# -----------------------------------------------------------------------------
# This implementation is not full featured but just aim to showcase
# the generic backend in a way that it can be used by anything.
# For real integration, using inheritance like for aiohttp is recommended.
# -----------------------------------------------------------------------------
import tornado
import tempfile

from tornado.websocket import WebSocketHandler


class GenericMessage:
    def __init__(self, data):
        self.data = data


class WsLinkWebSocket(WebSocketHandler):
    def __init__(self, application, request, generic_server=None, **kwargs):
        super().__init__(application, request, **kwargs)
        self._ws = generic_server[generic_server.ws_endpoints[0]]
        self._me = None

    async def on_msg_from_generic(self, binary, content):
        self.write_message(content, binary)

    def open(self):
        self._me = self._ws.connect()
        self._me.on_message(self.on_msg_from_generic)

    async def on_message(self, message):
        is_binary = not isinstance(message, str)
        await self._me.send(is_binary, GenericMessage(message))

    def on_close(self):
        self._me.close()


def startWebServer(*args, **kwargs):
    raise NotImplementedError("Generic backend does not provide a launcher")


def create_webserver(server_config):
    # Reverse connection
    if "reverse_url" in server_config:
        raise NotImplementedError("Generic backend does not support reverse_url")

    from ..generic.core import create_webserver as create_generic_webserver

    generic_server = create_generic_webserver(server_config)

    # Handle static content
    www = tempfile.mkdtemp()
    generic_server.write_static_content(www)

    # Tornado specific
    handlers = [
        (r"/ws", WsLinkWebSocket, {"generic_server": generic_server}),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": www}),
    ]

    application = tornado.web.Application(handlers)
    application.listen(generic_server.port)

    return generic_server
