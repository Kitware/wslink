from typing import TypeVar, Generic, LiteralString

import asyncio
import functools


T = TypeVar("T", bound=LiteralString)


class EventEmitter(Generic[T]):
    def __init__(self):
        self._listeners = {}

    def clear(self):
        self._listeners = {}

    def __call__(self, event: T, *args, **kwargs):
        self.emit(event, *args, **kwargs)

    def __getattr__(self, name: T):
        return functools.partial(self.emit, name)

    def emit(self, event: T, *args, **kwargs):
        listeners = self._listeners.get(event)
        if listeners is None:
            return

        loop = asyncio.get_running_loop()
        coroutine_run = (
            loop.create_task if (loop and loop.is_running()) else asyncio.run
        )

        for listener in listeners:
            if asyncio.iscoroutinefunction(listener):
                coroutine_run(listener(*args, **kwargs))
            else:
                listener(*args, **kwargs)

    def add_event_listener(self, event: T, listener):
        listeners = self._listeners.get(event)
        if listeners is None:
            listeners = set()
            self._listeners[event] = listeners

        listeners.add(listener)

    def remove_event_listener(self, event: T, listener):
        listeners = self._listeners.get(event)
        if listeners is None:
            return

        if listener in listeners:
            listeners.remove(listener)

    def has(self, event: T):
        return self.listeners_count(event) > 0

    def listeners_count(self, event: T):
        listeners = self._listeners.get(event)
        if listeners is None:
            return 0

        return len(listeners)
