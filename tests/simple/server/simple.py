import argparse

from wslink.websocket import ServerProtocol
from wslink import server

from myProtocol import MyProtocol


class ExampleServer(ServerProtocol):
    authKey = "wslink-secret"

    @staticmethod
    def configure(options):
        ExampleServer.authKey = options.authKey

    def initialize(self):
        self.registerLinkProtocol(MyProtocol())

        # Update authentication key to use
        self.updateSecret(ExampleServer.authKey)


def simple_start(argv=None):
    server.start(argv, ExampleServer)


if __name__ == "__main__":
    simple_start()
