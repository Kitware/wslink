import asyncio
import functools


class EventEmitter:
    def __init__(self, allowed_events=None):
        self._listeners = {}

        if allowed_events is None:
            allowed_events = []

        self._allowed_events = set(allowed_events)

        for event in self._allowed_events:
            setattr(self, event, functools.partial(self.emit, event))

    def clear(self):
        self._listeners = {}

    def __call__(self, event, *args, **kwargs):
        self.emit(event, *args, **kwargs)

    def emit(self, event, *args, **kwargs):
        self._validate_event(event)

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
        self._validate_event(event)

        listeners = self._listeners.get(event)
        if listeners is None:
            listeners = set()
            self._listeners[event] = listeners

        listeners.add(listener)

    def remove_event_listener(self, event, listener):
        self._validate_event(event)

        listeners = self._listeners.get(event)
        if listeners is None:
            return

        if listener in listeners:
            listeners.remove(listener)

    def has(self, event):
        return self.listeners_count(event) > 0

    def listeners_count(self, event):
        self._validate_event(event)

        listeners = self._listeners.get(event)
        if listeners is None:
            return 0

        return len(listeners)

    @property
    def allowed_events(self):
        return self._allowed_events

    def _validate_event(self, event):
        if len(self.allowed_events) == 0:
            return

        if event not in self.allowed_events:
            raise ValueError(
                f"'{event}' is not a known event of this EventEmitter: {self.allowed_events}"
            )
