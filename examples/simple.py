from wslink.websocket import ServerProtocol
from wslink.server import *

from myProtocol import MyProtocol

class ExampleServer(ServerProtocol):
    def initialize(self):
        self.registerLinkProtocol(MyProtocol())
        self.updateSecret("vtkweb-secret")

def simple_start(argv=None):
    start(argv, ExampleServer)

if __name__ == "__main__":
    simple_start()
