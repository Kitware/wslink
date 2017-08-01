import os

from wslink import register as exportRPC
from wslink.websocket import LinkProtocol
from twisted.internet import task

# -----------------------------------------------------------------------------
# WS protocol definition
# -----------------------------------------------------------------------------

class MyProtocol(LinkProtocol):
    def __init__(self):
        super(MyProtocol, self).__init__()
        self.subscribers = {}
        self.subMsgCount = 0

    @exportRPC("myprotocol.add")
    def add(self, listOfNumbers):
        if (type(listOfNumbers) is list):
            result = 0
            for value in listOfNumbers:
                result += value
            return result

        # How should a client return an error? Probably throw()
        print("Unexpected arg", listOfNumbers)
        return 0

    @exportRPC("myprotocol.mult")
    def mult(self, listOfNumbers):
        if (type(listOfNumbers) is list):
            result = 1
            for value in listOfNumbers:
                result *= value
            return result

        print("Unexpected arg", listOfNumbers)
        return 0

    @exportRPC("myprotocol.image")
    def image(self, alt = False):
        filename = "kitware.png" if not alt else "kitware2.png"
        filename = os.path.join(os.path.dirname(__file__), filename)
        with open(filename, mode='rb') as file:
            contents = file.read()
            return { "blob": self.addAttachment(contents) }

    def pushImage(self):
        print("push image", self.subMsgCount)
        msg = self.image(self.subMsgCount % 2 is 0)
        # publish binary message. TODO, how to get topic?
        self.publish("image", msg)
        self.subMsgCount += 1

    @exportRPC("myprotocol.stream")
    def startStream(self, topic):
        print("start", topic)
        # set up repeated send of images until unsubscribed.
        # http://twistedmatrix.com/documents/current/core/howto/time.html
        loopTask = task.LoopingCall(self.pushImage)
        loopTask.start(2.0)
        self.subscribers['topic'] = topic
        self.subscribers['loopTask'] = loopTask
        return { "subscribed": topic }

    @exportRPC("myprotocol.stop")
    def stopStream(self, topic):
        print("stop", topic)
        if 'topic' in self.subscribers and self.subscribers['topic'] == topic:
            loopTask = self.subscribers['loopTask']
            loopTask.stop()
            self.subscribers.clear()
            return { "unsubscribed": topic }
        return 0

    # test nesting attachments
    @exportRPC("myprotocol.nested.image")
    def testNesting(self):
        img = self.image()
        # just using 'bytes' only works in Py3
        bytes_list1 = bytes(bytearray([1, 2, 3, 4]))
        bytes_list2 = bytes(bytearray([5, 6, 7, 8, 9, 10]))
        msg = {
            "image": img,
            "bytesList": [
                self.addAttachment(bytes_list1),
                self.addAttachment(bytes_list2),
            ]
        }
        return msg

