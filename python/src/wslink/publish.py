from . import schedule_coroutine

# =============================================================================
# singleton publish manager


class PublishManager(object):
    def __init__(self):
        self.protocols = []
        self.attachmentMap = {}
        self.attachmentRefCounts = {}  # keyed same as attachment map
        self.attachmentId = 0
        self.publishCount = 0

    def registerProtocol(self, protocol):
        self.protocols.append(protocol)

    def unregisterProtocol(self, protocol):
        if protocol in self.protocols:
            self.protocols.remove(protocol)

    def getAttachmentMap(self):
        return self.attachmentMap

    def clearAttachmentMap(self):
        self.attachmentMap.clear()

    def registerAttachment(self, attachKey):
        self.attachmentRefCounts[attachKey] += 1

    def unregisterAttachment(self, attachKey):
        self.attachmentRefCounts[attachKey] -= 1

    def freeAttachments(self, keys=None):
        keys_to_delete = []
        keys_to_check = keys if keys is not None else [k for k in self.attachmentMap]

        for key in keys_to_check:
            if self.attachmentRefCounts[key] == 0:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            self.attachmentMap.pop(key)
            self.attachmentRefCounts.pop(key)

    def addAttachment(self, payload):
        # print("attachment", self, self.attachmentId)
        # use a string flag in place of the binary attachment.
        binaryId = "wslink_bin{0}".format(self.attachmentId)
        self.attachmentMap[binaryId] = payload
        self.attachmentRefCounts[binaryId] = 0
        self.attachmentId += 1
        return binaryId

    def publish(self, topic, data, client_id=None):
        for protocol in self.protocols:
            # The client is unknown - we send to any client who is subscribed to the topic
            rpcid = "publish:{0}:{1}".format(topic, self.publishCount)
            schedule_coroutine(
                0, protocol.sendWrappedMessage, rpcid, data, client_id=client_id
            )


# singleton, used by all instances of WslinkWebSocketServerProtocol
publishManager = PublishManager()

# from http://www.jsonrpc.org/specification, section 5.1
METHOD_NOT_FOUND = -32601
AUTHENTICATION_ERROR = -32000
EXCEPTION_ERROR = -32001
RESULT_SERIALIZE_ERROR = -32002
# used in client JS code:
CLIENT_ERROR = -32099
