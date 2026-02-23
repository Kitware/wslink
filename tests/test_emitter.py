import asyncio

import pytest

from wslink.emitter import EventEmitter


def _create_listeners(emitter):
    payloads = {}

    def on_foo(val):
        payloads["foo"] = val

    async def on_bar(val):
        await asyncio.sleep(0.05)
        payloads["bar"] = val

    emitter.add_event_listener("foo", on_foo)
    emitter.add_event_listener("bar", on_bar)

    return payloads, on_foo, on_bar


@pytest.mark.asyncio
async def test_add_listener():
    emitter = EventEmitter()
    payloads, on_foo, on_bar = _create_listeners(emitter)

    emitter.emit("foo", 0)
    emitter.emit("bar", 1)

    await asyncio.sleep(0.1)

    assert payloads.get("foo") == 0
    assert payloads.get("bar") == 1


@pytest.mark.asyncio
async def test_remove_listeners():
    emitter = EventEmitter()
    payloads, on_foo, on_bar = _create_listeners(emitter)

    emitter.remove_event_listener("bar", on_bar)

    emitter.emit("foo", 0)
    emitter.emit("bar", 1)

    await asyncio.sleep(0.1)

    assert payloads.get("foo") == 0
    assert payloads.get("bar") is None


@pytest.mark.asyncio
async def test_clear_listeners():
    emitter = EventEmitter()
    payloads, on_foo, on_bar = _create_listeners(emitter)

    emitter.clear()

    emitter.emit("foo", 0)
    emitter.emit("bar", 1)

    await asyncio.sleep(0.1)

    assert payloads.get("foo") is None
    assert payloads.get("bar") is None


def test_event_type_runtime():
    emitter = EventEmitter(allowed_events=("foo", "bar"))

    emitter.emit("foo")
    emitter.emit("bar")

    with pytest.raises(ValueError):
        emitter.emit("baz")

    assert emitter.allowed_events == {"foo", "bar"}


@pytest.mark.asyncio
async def test_event_emit_call():
    emitter = EventEmitter(allowed_events=("foo", "bar"))
    payloads, on_foo, on_bar = _create_listeners(emitter)

    assert emitter.allowed_events == {"foo", "bar"}

    emitter("foo", 0)
    emitter("bar", 1)

    with pytest.raises(ValueError):
        emitter("baz", 2)

    await asyncio.sleep(0.1)

    assert payloads.get("foo") == 0
    assert payloads.get("bar") == 1


@pytest.mark.asyncio
async def test_event_emit_attribute():
    emitter = EventEmitter(allowed_events=("foo", "bar"))
    payloads, on_foo, on_bar = _create_listeners(emitter)

    assert emitter.allowed_events == {"foo", "bar"}

    emitter.foo(0)
    emitter.bar(1)

    with pytest.raises(AttributeError):
        emitter.baz()

    await asyncio.sleep(0.1)

    assert payloads.get("foo") == 0
    assert payloads.get("bar") == 1
