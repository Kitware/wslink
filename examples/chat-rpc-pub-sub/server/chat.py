r"""
# -----------------------------------------------------------------------------
# This WebServer aims to provide a good starting point when creating
# wslink based service.
#
# $ python ./server/server.py --content ./www
# -----------------------------------------------------------------------------
"""

import argparse

from api import PubSubAPI

from wslink import server
from wslink.websocket import ServerProtocol

# -----------------------------------------------------------------------------


class WebServer(ServerProtocol):
    authKey = "wslink-secret"

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            "--virtual-env", default=None, help="Path to virtual environment to use"
        )

    @staticmethod
    def configure(options):
        WebServer.authKey = options.authKey

    def initialize(self):
        self.registerLinkProtocol(PubSubAPI())

        # Update authentication key to use
        self.updateSecret(WebServer.authKey)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="WSLink sample application")

    # Add arguments
    server.add_arguments(parser)
    WebServer.add_arguments(parser)
    args = parser.parse_args()
    WebServer.configure(args)

    # Start web server
    server.start(None, WebServer)
