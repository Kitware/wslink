import os

from vtkrpc import register as exportRPC
from twisted.internet import task

# -----------------------------------------------------------------------------
# WS protocol definition
# -----------------------------------------------------------------------------

class MyProtocol(object):
    def __init__(self, publish=None, addAttachment=None):
        self.subscribers = {}
        self.subMsgCount = 0
        self.publish = publish
        self.addAttachment = addAttachment

    def init(self, publish, addAttachment):
        self.publish = publish
        self.addAttachment = addAttachment

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



