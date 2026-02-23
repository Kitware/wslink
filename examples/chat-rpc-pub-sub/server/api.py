from wslink import register as exportRpc
from wslink import schedule_callback
from wslink.websocket import LinkProtocol

MESSAGE_LIST = [
    "Nice to meet you",
    "What's your name?",
    "Mine is wslink.py",
]


class PubSubAPI(LinkProtocol):
    def __init__(self, **_):
        super().__init__()
        self.topic = "wslink.communication.channel"
        self.msgIdx = 0
        self.keepTalking = True
        self.frequency = 5  # 5 seconds
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
            schedule_callback(self.frequency, self.saySomething)

    @exportRpc("wslink.say.hello")
    def sayHello(self, message):
        print("sayHello", message)
        msgToPost = f"py server: {message}"
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
