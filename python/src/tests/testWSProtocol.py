#!/usr/bin/env python
import json, os, sys
import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

try:
    from wslink import schedule_callback, schedule_coroutine, register as exportRPC
except ImportError:
    print("loading wslink directly from src/ directory, as fallback")
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from wslink import schedule_callback, schedule_coroutine, register as exportRPC

from wslink.websocket import LinkProtocol, ServerProtocol
from wslink.aiohttp_websocket_server_protocol import create_wslink_server

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
        self.subscribers['loopTask'] = schedule_callback(2, self.pushImage)

    @exportRPC("myprotocol.stream")
    def startStream(self, topic):
        print("start", topic)
        # set up repeated send of images until unsubscribed.
        if not self.subscribers['loopTask']:
            self.subscribers['loopTask'] = schedule_callback(0, self.pushImage)
            self.subscribers['topic'] = topic
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
        self.protocol = MyProtocol()
        self.registerLinkProtocol(self.protocol)
        self.updateSecret("vtkweb-secret")

    def pushImage(self):
        self.protocol.pushImage()

class MockRequest(object):
    def __init__(self, app):
        self.app = app

class MockMessage(object):
    def __init__(self, msg_type, msg_data):
        self.type = msg_type
        self.data = msg_data

def encMsg(msg_type=None, msg_data=None):
    if not msg_type:
        import aiohttp
        msg_type = aiohttp.WSMsgType.TEXT

    # return json.dumps(msg, ensure_ascii = False).encode('utf8')
    return MockMessage(msg_type, json.dumps(msg_data, ensure_ascii = False).encode('utf8'))


class TestWSProtocol(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.server = ExampleServer()

        config = {
            "host": "0.0.0.0",
            "port": 4567,
            "timeout": 300,
            "handle_signals": False,
            "ws": {
                "/websock": self.server
            }
        }

        self.wslink_server = create_wslink_server(config)
        self.server_config = self.wslink_server.get_config()
        self.protocol = self.server_config["ws"]["/websock"]
        self.mock_request = MockRequest(self.wslink_server.get_app())

        schedule_coroutine(0, self.wslink_server.start)

    async def asyncTearDown(self):
        await self.wslink_server.stop()

    def test_pushBeforeConnect(self):
        self.server.pushImage()
        # test for no exceptions, otherwise no-op.

    async def test_messageNoConnect(self):
        msg = {
            "wslink": "1.0",
            "id": "rpc:c0:0",
            "method": "myprotocol.add",
            "args": [1,2],
        }
        msgMock = MagicMock(spec=self.protocol.sendWrappedMessage)
        self.protocol.sendWrappedMessage = msgMock
        await self.protocol.onMessage(encMsg(msg_data=msg), False)
        msgMock.assert_called()
        self.assertIsNotNone(msgMock.call_args[0])
        self.assertIsNotNone(msgMock.call_args[0][0])
        msg_bytes = msgMock.call_args[0][0]
        self.assertIn(b'"error":', msg_bytes)
        self.assertIn(b"Unregistered method called", msg_bytes)

    async def handshake(self):
        await self.protocol.onConnect(self.mock_request)
        msg = {
            "wslink": "1.0",
            "id": "system:c0:0",
            "method": "wslink.hello",
            "args": [{ "secret": "vtkweb-secret" }],
            "kwargs": {},
        }
        msgMock = MagicMock(spec=self.protocol.sendWrappedMessage)
        self.protocol.sendWrappedMessage = msgMock
        await self.protocol.onMessage(encMsg(msg_data=msg), False)
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

    async def message(self, msgMock, method, args, kwargs):
        msg = {
            "wslink": "1.0",
            "id": "rpc:{0}:{1}".format(self.clientID, self.msgCount),
            "method": method,
            "args": args,
            "kwargs": kwargs,
        }
        await self.protocol.onMessage(encMsg(msg_data=msg), False)
        return msgMock.call_args[0][0]

    async def test_hello(self):
        await self.handshake()

    async def test_badSecret(self):
        await self.protocol.onConnect(self.mock_request)
        msg = {
            "wslink": "1.0",
            "id": "system:c0:0",
            "method": "wslink.hello",
            "args": [{ "secret": "bad-secret" }],
            "kwargs": {},
        }
        msgMock = MagicMock(spec=self.protocol.sendWrappedMessage)
        self.protocol.sendWrappedMessage = msgMock
        await self.protocol.onMessage(encMsg(msg_data=msg), False)
        msgMock.assert_called()
        self.assertIsNotNone(msgMock.call_args[0])
        self.assertIsNotNone(msgMock.call_args[0][0])
        msg_bytes = msgMock.call_args[0][0]
        self.assertIn(b'"error":', msg_bytes)
        self.assertNotIn(b'"result":', msg_bytes)
        self.assertIn(b"Authentication failed", msg_bytes)
        # how about no "secret" key?
        msg["args"] = [{ "foo": "bar" }]
        await self.protocol.onMessage(encMsg(msg_data=msg), False)
        msg_bytes = msgMock.call_args[0][0]
        self.assertIn(b'"error":', msg_bytes)
        self.assertIn(b"Authentication failed", msg_bytes)

    async def test_badRPC(self):
        msgMock = await self.handshake()

        msg_bytes = await self.message(msgMock, "bogus.rpc.method", [1, 2, 3], {})
        self.assertIn(b'"error":', msg_bytes)
        self.assertNotIn(b'"result":', msg_bytes)
        self.assertIn(b"Unregistered method called", msg_bytes)

    async def test_goodRPC(self):
        msgMock = await self.handshake()
        msg_bytes = await self.message(msgMock, "myprotocol.add", [[1, 2, 3]], {})
        self.assertEqual(msg_bytes,
            b'{"wslink": "1.0", "id": "rpc:c0:0", "result": 6}')

    async def test_nonReturnRPC(self):
        msgMock = await self.handshake()
        msg_bytes = await self.message(msgMock, "myprotocol.nothing", [], {})
        self.assertEqual(msg_bytes,
            b'{"wslink": "1.0", "id": "rpc:c0:0", "result": null}')

    async def test_throwsRPC(self):
        msgMock = await self.handshake()
        # with self.assertRaisesRegex(Exception, "I don't like"):
        # exception issued with raise()
        msg_bytes = await self.message(msgMock, "myprotocol.throw", [[1, 2, 3]], {})
        self.assertIn(b'"error":', msg_bytes)
        self.assertIn(b"Exception raised", msg_bytes)
        self.assertIn(b"I don't like args", msg_bytes)
        # illegal operation
        msg_bytes = await self.message(msgMock, "myprotocol.throw", [0], {})
        self.assertIn(b'"error":', msg_bytes)
        self.assertIn(b"Exception raised", msg_bytes)
        self.assertIn(b"TypeError", msg_bytes)
        # result of method can't be made into JSON
        msg_bytes = await self.message(msgMock, "myprotocol.throw", [1], {})
        self.assertIn(b'"error":', msg_bytes)
        self.assertNotIn(b'"result":', msg_bytes)
        self.assertIn(b"cannot be serialized", msg_bytes)
        self.assertIn(b"myprotocol.throw", msg_bytes)

    async def test_goodBinaryRPC(self):
        msgMock = await self.handshake()
        msg_bytes = await self.message(msgMock, "myprotocol.binary", [5], {})
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

