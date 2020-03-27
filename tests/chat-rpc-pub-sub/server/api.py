import os, time

from wslink import register as exportRpc
from wslink.websocket import LinkProtocol
from twisted.internet import task

# import Twisted reactor for later callback
from twisted.internet import reactor

MESSAGE_LIST = [
    'Nice to meet you',
    "What's your name?",
    'Mine is wslink.py',
]

class PubSubAPI(LinkProtocol):
    def __init__(self, **kwargs):
      super(PubSubAPI, self).__init__()
      self.topic = 'wslink.communication.channel'
      self.msgIdx = 0
      self.keepTalking = True
      self.frequency = 5 # 5 seconds
      self.startTalking()


    def saySomething(self):
        if not self.keepTalking:
            return

        if self.msgIdx + 1 < len(MESSAGE_LIST):
            self.msgIdx += 1
        else:
            self.msgIdx = 0

        self.publish(self.topic, MESSAGE_LIST[self.msgIdx])

        if self.keepTalking:
            reactor.callLater(self.frequency, lambda: self.saySomething())


    @exportRpc("wslink.say.hello")
    def sayHello(self, message):
        msgToPost = 'py server: %s' % message
        self.publish(self.topic, msgToPost)
        return msgToPost


    @exportRpc("wslink.start.talking")
    def startTalking(self):
        self.keepTalking = True
        self.saySomething()


    @exportRpc("wslink.stop.talking")
    def stopTalking(self):
        self.keepTalking = False
        self.msgIdx = 0
