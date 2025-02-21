import asyncio
import functools


class EventEmitter:
    def __init__(self):
        self._listeners = {}

    def clear(self):
        self._listeners = {}

    def __call__(self, event, *args, **kwargs):
        self.emit(event, *args, **kwargs)

    def __getattr__(self, name):
        return functools.partial(self.emit, name)

    def exception(self, *args, **kwargs):
        self.emit("exception", *args, **kwargs)

    def error(self, *args, **kwargs):
        self.emit("error", *args, **kwargs)

    def critical(self, *args, **kwargs):
        self.emit("critical", *args, **kwargs)

    def info(self, *args, **kwargs):
        self.emit("info", *args, **kwargs)

    def debug(self, *args, **kwargs):
        self.emit("debug", *args, **kwargs)

    def emit(self, event, *args, **kwargs):
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

    def add_event_listener(self, event, listener):
        listeners = self._listeners.get(event)
        if listeners is None:
            listeners = set()
            self._listeners[event] = listeners

        listeners.add(listener)

    def remove_event_listener(self, event, listener):
        listeners = self._listeners.get(event)
        if listeners is None:
            return

        if listener in listeners:
            listeners.remove(listener)

    def has(self, event):
        return self.listeners_count(event) > 0

    def listeners_count(self, event):
        listeners = self._listeners.get(event)
        if listeners is None:
            return 0

        return len(listeners)
