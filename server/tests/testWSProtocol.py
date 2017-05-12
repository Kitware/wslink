#!/usr/bin/env python
import json, os, sys
import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from wslink.websocket import LinkProtocol, ServerProtocol, TimeoutWebSocketServerFactory, WslinkWebSocketServerProtocol
from autobahn.twisted.resource import WebSocketResource
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory

from wslink import register as exportRPC
from twisted.internet import reactor, task

class MyProtocol(LinkProtocol):
    def __init__(self, publish=None, addAttachment=None):
        super(MyProtocol, self).__init__()
        self.subscribers = {}
        self.subMsgCount = 0
        self.publish = publish
        self.addAttachment = addAttachment
        self.app = None

    def init(self, publish, addAttachment):
        self.publish = publish
        self.addAttachment = addAttachment

    def setApplication(self, app):
        self.app = app

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

    @exportRPC("myprotocol.nothing")
    def sendNone(self):
        return

    @exportRPC("myprotocol.throw")
    def causeException(self, listOfNumbers):
        if (listOfNumbers == 1):
            return RuntimeError("This cannot be serialized")
        elif (listOfNumbers == 0):
            # cause a type error
            listOfNumbers['foo'] = 3;
        elif (listOfNumbers):
            raise RuntimeError("I don't like args")
        return 0

    @exportRPC("myprotocol.binary")
    def binary(self, size):
        someData = bytearray([0, 1, 2, 254, 255])
        contents = memoryview(someData)
        return { "blob": self.addAttachment(contents) }

    def pushImage(self):
        print("push image", self.subMsgCount)
        msg = self.binary(5 if self.subMsgCount % 2 is 0 else 2)
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

class ExampleServer(ServerProtocol):
    def initialize(self):
        self.registerLinkProtocol(MyProtocol())
        self.updateSecret("vtkweb-secret")


# Client is created for each test, connects and disconnects.
# class MyClientProtocol(WebSocketClientProtocol):

#    def onOpen(self):
#       self.sendMessage(u"Hello, world!".encode('utf8'))

#    def onMessage(self, payload, isBinary):
#       if isBinary:
#          print("Binary message received: {0} bytes".format(len(payload)))
#       else:
#          print("Text message received: {0}".format(payload.decode('utf8')))

# clientFactory = WebSocketClientFactory(u"ws://127.0.0.1:9090")
# clientFactory.protocol = MyClientProtocol

# -----------------------------------------------------------------------------
# Testing Taken from autobahn/test/__init__.py
# -----------------------------------------------------------------------------
class FakeTransport(object):
    _written = b""
    _open = True

    def write(self, msg):
        if not self._open:
            raise Exception("Can't write to a closed connection")
        self._written = self._written + msg

    def loseConnection(self):
        self._open = False

def encMsg(msg):
    return json.dumps(msg, ensure_ascii = False).encode('utf8')

class TestWSProtocol(unittest.TestCase):
    """
    Taken from autobahn/websocket/test/test_protocol.py
    """
    def setUp(self):
        t = FakeTransport()
        exampleServer = ExampleServer()
        f = TimeoutWebSocketServerFactory(timeout=5)
        f.setServerProtocol(exampleServer)
        p = WslinkWebSocketServerProtocol()
        p.factory = f
        p.transport = t

        p._connectionMade()
        p.state = p.STATE_OPEN
        p.websocket_version = 18

        self.protocol = p
        self.transport = t

    def tearDown(self):
        for call in [
                self.protocol.autoPingPendingCall,
                self.protocol.autoPingTimeoutCall,
                self.protocol.openHandshakeTimeoutCall,
                self.protocol.closeHandshakeTimeoutCall,
        ]:
            if call is not None:
                call.cancel()

    # copied autobahn test
    def test_sendClose_none(self):
        """
        sendClose with no code or reason works.
        """
        self.protocol.sendClose()

        # We closed properly
        self.assertEqual(self.transport._written, b"\x88\x00")
        self.assertEqual(self.protocol.state, self.protocol.STATE_CLOSING)

    def test_onConnect(self):
        self.protocol.onConnect({})
        self.protocol.sendClose()
        self.protocol.onClose(True, None, None)
        self.assertEqual(self.transport._written, b"\x88\x00")
        # self.fail("see stdout")

    def test_messageNoConnect(self):
        msg = {
            "wslink": "1.0",
            "id": "rpc:c0:0",
            "method": "myprotocol.add",
            "args": [1,2],
        }
        msgMock = MagicMock(spec=self.protocol.sendMessage)
        self.protocol.sendMessage = msgMock
        self.protocol.onMessage(encMsg(msg), False)
        msgMock.assert_called()
        self.assertIsNotNone(msgMock.call_args[0])
        self.assertIsNotNone(msgMock.call_args[0][0])
        msg_bytes = msgMock.call_args[0][0]
        self.assertIn(b'"error":', msg_bytes)
        self.assertIn(b"Unregistered method called", msg_bytes)

    def handshake(self):
        self.protocol.onConnect({})
        msg = {
            "wslink": "1.0",
            "id": "system:c0:0",
            "method": "wslink.hello",
            "args": [{ "secret": "vtkweb-secret" }],
            "kwargs": {},
        }
        msgMock = MagicMock(spec=self.protocol.sendMessage)
        self.protocol.sendMessage = msgMock
        self.protocol.onMessage(encMsg(msg), False)
        msgMock.assert_called_once()
        self.assertIsNotNone(msgMock.call_args[0])
        self.assertIsNotNone(msgMock.call_args[0][0])
        msg_bytes = msgMock.call_args[0][0]
        self.assertEqual(b'{"wslink": "1.0", "id": "system:c0:0", "result": {"clientID": "c0"}}',
                         msg_bytes)
        # allow follow-on msg tests to use clientID
        self.clientID = "c0"
        self.msgCount = 0
        msgMock.reset_mock()
        return msgMock

    def message(self, msgMock, method, args, kwargs):
        msg = {
            "wslink": "1.0",
            "id": "rpc:{0}:{1}".format(self.clientID, self.msgCount),
            "method": method,
            "args": args,
            "kwargs": kwargs,
        }
        self.protocol.onMessage(encMsg(msg), False)
        return msgMock.call_args[0][0]

    def test_hello(self):
        self.handshake()

    def test_badSecret(self):
        self.protocol.onConnect({})
        msg = {
            "wslink": "1.0",
            "id": "system:c0:0",
            "method": "wslink.hello",
            "args": [{ "secret": "bad-secret" }],
            "kwargs": {},
        }
        msgMock = MagicMock(spec=self.protocol.sendMessage)
        self.protocol.sendMessage = msgMock
        self.protocol.onMessage(encMsg(msg), False)
        msgMock.assert_called()
        self.assertIsNotNone(msgMock.call_args[0])
        self.assertIsNotNone(msgMock.call_args[0][0])
        msg_bytes = msgMock.call_args[0][0]
        self.assertIn(b'"error":', msg_bytes)
        self.assertNotIn(b'"result":', msg_bytes)
        self.assertIn(b"Authentication failed", msg_bytes)
        # how about no "secret" key?
        msg["args"] = [{ "foo": "bar" }]
        self.protocol.onMessage(encMsg(msg), False)
        msg_bytes = msgMock.call_args[0][0]
        self.assertIn(b'"error":', msg_bytes)
        self.assertIn(b"Authentication failed", msg_bytes)

    def test_badRPC(self):
        msgMock = self.handshake()

        msg_bytes = self.message(msgMock, "bogus.rpc.method", [1, 2, 3], {})
        self.assertIn(b'"error":', msg_bytes)
        self.assertNotIn(b'"result":', msg_bytes)
        self.assertIn(b"Unregistered method called", msg_bytes)

    def test_goodRPC(self):
        msgMock = self.handshake()
        msg_bytes = self.message(msgMock, "myprotocol.add", [[1, 2, 3]], {})
        self.assertEqual(msg_bytes,
            b'{"wslink": "1.0", "id": "rpc:c0:0", "result": 6}')

    def test_nonReturnRPC(self):
        msgMock = self.handshake()
        msg_bytes = self.message(msgMock, "myprotocol.nothing", [], {})
        self.assertEqual(msg_bytes,
            b'{"wslink": "1.0", "id": "rpc:c0:0", "result": null}')

    def test_throwsRPC(self):
        msgMock = self.handshake()
        # with self.assertRaisesRegex(Exception, "I don't like"):
        # exception issued with raise()
        msg_bytes = self.message(msgMock, "myprotocol.throw", [[1, 2, 3]], {})
        self.assertIn(b'"error":', msg_bytes)
        self.assertIn(b"Exception raised", msg_bytes)
        self.assertIn(b"I don't like args", msg_bytes)
        # illegal operation
        msg_bytes = self.message(msgMock, "myprotocol.throw", [0], {})
        self.assertIn(b'"error":', msg_bytes)
        self.assertIn(b"Exception raised", msg_bytes)
        self.assertIn(b"TypeError", msg_bytes)
        # result of method can't be made into JSON
        msg_bytes = self.message(msgMock, "myprotocol.throw", [1], {})
        self.assertIn(b'"error":', msg_bytes)
        self.assertNotIn(b'"result":', msg_bytes)
        self.assertIn(b"cannot be serialized", msg_bytes)
        self.assertIn(b"myprotocol.throw", msg_bytes)

    def test_goodBinaryRPC(self):
        msgMock = self.handshake()
        msg_bytes = self.message(msgMock, "myprotocol.binary", [5], {})
        self.assertEqual(msgMock.call_count, 3)
        self.assertIn(b'"method": "wslink.binary.attachment"', msgMock.call_args_list[0][0][0])
        self.assertIn(b'"args": ["wslink_bin0"]', msgMock.call_args_list[0][0][0])

        binary_msg = msgMock.call_args_list[1][0][0].tolist()
        self.assertEqual(binary_msg, [0, 1, 2, 254, 255])
        self.assertEqual(msg_bytes,
            b'{"wslink": "1.0", "id": "rpc:c0:0", "result": {"blob": "wslink_bin0"}}')

    # TODO some bad binary behaviors:
    # creating an attachment and not using it.
    # use an attachment twice
    # use a non-existent attachment
    # If we allow multiple clients, possible attack: given an 'echo' rpc, add attachment strings,
    # hoping one is around

if __name__ == '__main__':
    unittest.main(buffer=True)

