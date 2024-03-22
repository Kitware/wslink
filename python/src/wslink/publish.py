from . import schedule_coroutine

# =============================================================================
# singleton publish manager


class PublishManager(object):
    def __init__(self):
        self.protocols = []
        self.publishCount = 0

    def registerProtocol(self, protocol):
        self.protocols.append(protocol)

    def unregisterProtocol(self, protocol):
        if protocol in self.protocols:
            self.protocols.remove(protocol)

    def addAttachment(self, payload):
        """Deprecated method, keeping it to avoid breaking compatibility
        Now that we use msgpack to pack/unpack messages,
        We can have binary data directly in the object itself,
        without needing to transfer it separately from the rest."""
        return payload

    def publish(self, topic, data, client_id=None, skip_last_active_client=False):
        for protocol in self.protocols:
            # The client is unknown - we send to any client who is subscribed to the topic
            rpcid = "publish:{0}:{1}".format(topic, self.publishCount)
            schedule_coroutine(
                0,
                protocol.sendWrappedMessage,
                rpcid,
                data,
                client_id=client_id,
                skip_last_active_client=skip_last_active_client,
            )


# singleton, used by all instances of WslinkWebSocketServerProtocol
publishManager = PublishManager()
