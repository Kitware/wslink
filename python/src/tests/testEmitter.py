import unittest

import asyncio

from wslink.emitter import EventEmitter


class TestEventEmitter(unittest.IsolatedAsyncioTestCase):
    def _create_listeners(self, emitter):
        payloads = {}

        def on_foo(val):
            payloads["foo"] = val

        async def on_bar(val):
            await asyncio.sleep(0.05)
            payloads["bar"] = val

        emitter.add_event_listener("foo", on_foo)
        emitter.add_event_listener("bar", on_bar)

        return payloads, on_foo, on_bar

    async def test_add_listener(self):
        emitter = EventEmitter()
        payloads, on_foo, on_bar = self._create_listeners(emitter)

        emitter.emit("foo", 0)
        emitter.emit("bar", 1)

        await asyncio.sleep(0.1)

        self.assertEqual(payloads.get("foo"), 0)
        self.assertEqual(payloads.get("bar"), 1)

    async def test_remove_listeners(self):
        emitter = EventEmitter()
        payloads, on_foo, on_bar = self._create_listeners(emitter)

        emitter.remove_event_listener("bar", on_bar)

        emitter.emit("foo", 0)
        emitter.emit("bar", 1)

        await asyncio.sleep(0.1)

        self.assertEqual(payloads.get("foo"), 0)
        self.assertEqual(payloads.get("bar"), None)

    async def test_clear_listeners(self):
        emitter = EventEmitter()
        payloads, on_foo, on_bar = self._create_listeners(emitter)

        emitter.clear()

        emitter.emit("foo", 0)
        emitter.emit("bar", 1)

        await asyncio.sleep(0.1)

        self.assertEqual(payloads.get("foo"), None)
        self.assertEqual(payloads.get("bar"), None)

    def test_event_type_runtime(self):
        emitter = EventEmitter(allowed_events=("foo", "bar"))

        emitter.emit("foo")
        emitter.emit("bar")
        self.assertRaises(ValueError, emitter.emit, "baz")

        self.assertSetEqual(emitter.allowed_events, {"foo", "bar"})

    async def test_event_emit_call(self):
        emitter = EventEmitter(allowed_events=("foo", "bar"))
        payloads, on_foo, on_bar = self._create_listeners(emitter)

        self.assertSetEqual(emitter.allowed_events, {"foo", "bar"})

        emitter("foo", 0)
        emitter("bar", 1)
        self.assertRaises(ValueError, emitter, "baz", 2)

        await asyncio.sleep(0.1)

        self.assertEqual(payloads.get("foo"), 0)
        self.assertEqual(payloads.get("bar"), 1)

    async def test_event_emit_attribute(self):
        emitter = EventEmitter(allowed_events=("foo", "bar"))
        payloads, on_foo, on_bar = self._create_listeners(emitter)

        self.assertSetEqual(emitter.allowed_events, {"foo", "bar"})

        emitter.foo(0)
        emitter.bar(1)
        self.assertRaises(AttributeError, lambda: emitter.baz)

        await asyncio.sleep(0.1)

        self.assertEqual(payloads.get("foo"), 0)
        self.assertEqual(payloads.get("bar"), 1)


if __name__ == "__main__":
    unittest.main()
