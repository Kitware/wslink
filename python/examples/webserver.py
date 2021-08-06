import json, os, sys

from wslink.websocket import ServerProtocol

from myProtocol import MyProtocol

class ExampleServer(ServerProtocol):
    def initialize(self):
        self.protocol = MyProtocol()
        self.registerLinkProtocol(self.protocol)
        self.updateSecret("wslink-secret")

    def pushImage(self):
        self.protocol.pushImage()

# -----------------------------------------------------------------------------
# Web server definition
# -----------------------------------------------------------------------------
from wslink.aiohttp_websocket_server_protocol import create_wslink_server


# Warning if client examples haven't been built.
clientDir = os.path.join(os.path.dirname(__file__), "../../js/dist/examples")
if not os.path.exists(clientDir) or not os.path.exists(os.path.join(clientDir, "index.html")):
    print("Example client hasn't been built, please run 'npm run build:example' in ../js ")

exampleServer = ExampleServer()

config = {
    "host": "0.0.0.0",
    "port": 8080,
    "timeout": 300,
    "handle_signals": False,
    "ws": {
        "/ws": exampleServer
    }
    "static": {
        "/": clientDir
    }
}

wslink_server = create_wslink_server(config)
print("launching webserver")
wslink_server.start()

