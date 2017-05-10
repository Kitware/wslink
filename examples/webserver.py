import json, os, sys

# from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from wslink.websocket import ServerProtocol, TimeoutWebSocketServerFactory, WslinkWebSocketServerProtocol
from autobahn.twisted.resource import WebSocketResource

from myProtocol import MyProtocol

class ExampleServer(ServerProtocol):
    def initialize(self):
        self.registerLinkProtocol(MyProtocol())
        self.updateSecret("vtkweb-secret")

# -----------------------------------------------------------------------------
# Web server definition
# -----------------------------------------------------------------------------
from twisted.web.static import File
from twisted.python import log
from twisted.web.server import Site
from twisted.internet import reactor

log.startLogging(sys.stdout)

exampleServer = ExampleServer()

# Static file delivery
root = File(os.path.join(os.path.dirname(__file__), "../client/www"))

# WS endpoint
factory = TimeoutWebSocketServerFactory(url=u"ws://127.0.0.1:8080", timeout=60)
factory.protocol = WslinkWebSocketServerProtocol
factory.setServerProtocol(exampleServer)
resource = WebSocketResource(factory)
root.putChild(b"ws", resource)

# WebServer
print("launching webserver")
site = Site(root)
reactor.listenTCP(8080, site)
reactor.run()
