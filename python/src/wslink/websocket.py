r"""
This module implements the core RPC and publish APIs. Developers can extend
LinkProtocol to provide additional RPC callbacks for their web-applications. Then extend
ServerProtocol to hook all the needed LinkProtocols together.
"""

import logging
import asyncio

from wslink import register as exportRpc
from wslink import schedule_callback
from wslink.emitter import EventEmitter

logger = logging.getLogger(__name__)


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
        """Called when a websocket connection is closed."""

        pass


# =============================================================================
#
# Base class for wslink ServerProtocol objects
#
# =============================================================================


class NetworkMonitor:
    """
    Provide context manager for increase/decrease pending request
    either synchronously or asynchronously.

    The Asynchronous version also await completion.
    """

    def __init__(self):

        self.pending = 0
        self.event = asyncio.Event()

    def network_call_completed(self):
        """Trigger completion event"""
        self.event.set()

    def on_enter(self, *args, **kwargs):
        """Increase pending request"""
        self.pending += 1

    def on_exit(self, *args, **kwargs):
        """Decrease pending request and trigger completion event if we reach 0 pending request"""
        self.pending -= 1
        if self.pending == 0 and not self.event.is_set():
            self.event.set()

    # Sync ctx manager
    def __enter__(self):
        self.on_enter()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.on_exit()

    # Async ctx manager
    async def __aenter__(self):
        self.on_enter()
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        self.on_exit()
        await self.completion()

    async def completion(self):
        """Await completion of any pending network request"""
        while self.pending:
            self.event.clear()
            await self.event.wait()


class ServerProtocol(object):
    """
    Defines the core server protocol for wslink. Gathers a list of LinkProtocol
    objects that provide rpc and publish functionality.
    """

    def __init__(self):
        self.network_monitor = NetworkMonitor()
        self.log_emitter = EventEmitter(
            allowed_events=["exception", "error", "critical", "info", "debug"]
        )
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
            error_message = "Link protocol missing from registered list."
            logger.error(error_message)
            self.log_emitter("error", error_message)

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
        """Called when a websocket connection is closed."""

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
