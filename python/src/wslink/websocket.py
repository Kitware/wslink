r"""
This module implements the core RPC and publish APIs. Developers can extend
LinkProtocol to provide additional RPC callbacks for their web-applications. Then extend
ServerProtocol to hook all the needed LinkProtocols together.
"""

import logging

from . import register as exportRpc
from . import schedule_callback


# =============================================================================
#
# Base class for objects that can accept RPC calls or publish over wslink
#
# =============================================================================


class LinkProtocol(object):
    """
    Subclass this to communicate with wslink clients. LinkProtocol
    objects provide rpc and pub/sub actions.
    """

    def __init__(self):
        # need a no-op in case they are called before connect.
        self.publish = lambda x, y: None
        self.addAttachment = lambda x: None
        self.coreServer = None

    def init(self, publish, addAttachment, stopServer):
        self.publish = publish
        self.addAttachment = addAttachment
        self.stopServer = stopServer

    def getSharedObject(self, key):
        if self.coreServer:
            return self.coreServer.getSharedObject(key)
        return None

    def onConnect(self, request, client_id):
        """Called when a new websocket connection is established.

        request is the HTTP request header, and client_id an opaque string that
        identifies the connection.  The default implementation is a noop. A
        subclass may redefine it.

        """

        pass

    def onClose(self, client_id):
        """Called when a websocket connection is closed.
        """

        pass

# =============================================================================
#
# Base class for wslink ServerProtocol objects
#
# =============================================================================


class ServerProtocol(object):
    """
    Defines the core server protocol for wslink. Gathers a list of LinkProtocol
    objects that provide rpc and publish functionality.
    """

    def __init__(self):
        self.linkProtocols = []
        self.secret = None
        self.initialize()

    def init(self, publish, addAttachment, stopServer):
        self.publish = publish
        self.addAttachment = addAttachment
        self.stopServer = stopServer

    def initialize(self):
        """
        Let sub classes define what they need to do to properly initialize
        themselves.
        """
        pass

    def setSharedObject(self, key, shared):
        if not hasattr(self, "sharedObjects"):
            self.sharedObjects = {}
        if shared == None and key in self.sharedObjects:
            del self.sharedObjects[key]
        else:
            self.sharedObjects[key] = shared

    def getSharedObject(self, key):
        if key in self.sharedObjects:
            return self.sharedObjects[key]
        else:
            return None

    def registerLinkProtocol(self, protocol):
        assert isinstance(protocol, LinkProtocol)
        protocol.coreServer = self
        self.linkProtocols.append(protocol)

    # Note: this can only be used _before_ a connection is made -
    # otherwise the WslinkWebSocketServerProtocol will already have stored references to
    # the RPC methods in the protocol.
    def unregisterLinkProtocol(self, protocol):
        assert isinstance(protocol, LinkProtocol)
        protocol.coreServer = None
        try:
            self.linkProtocols.remove(protocol)
        except ValueError as e:
            logging.error("Link protocol missing from registered list.")

    def getLinkProtocols(self):
        return self.linkProtocols

    def updateSecret(self, newSecret):
        self.secret = newSecret

    def onConnect(self, request, client_id):
        """Called when a new websocket connection is established.

        request is the HTTP request header, and client_id an opaque string that
        identifies the connection.  The default implementation is a noop. A
        subclass may redefine it.

        """

        pass

    def onClose(self, client_id):
        """Called when a websocket connection is closed.
        """

        pass

    @exportRpc("application.exit")
    def exit(self):
        """RPC callback to exit"""
        self.stopServer()

    @exportRpc("application.exit.later")
    def exitLater(self, secondsLater=60):
        """RPC callback to exit after a short delay"""
        print(f"schedule exit for {secondsLater} seconds from now")
        schedule_callback(secondsLater, self.stopServer)
