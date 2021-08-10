r"""
Wslink allows easy, bi-directional communication between a python server and a
javascript client over a websocket.

wslink.server creates the python server
wslink.websocket handles the communication
"""
import asyncio
import functools

from .uri import checkURI

__license__ = "BSD-3-Clause"


def register(uri):
    """
    Decorator for RPC procedure endpoints.
    """

    def decorate(f):
        # called once when method is decorated, because we return 'f'.
        assert callable(f)
        if not hasattr(f, "_wslinkuris"):
            f._wslinkuris = []
        f._wslinkuris.append({"uri": checkURI(uri)})
        return f

    return decorate


#############################################################################
#
#                         scheduling methods
#
# Allow scheduling both callbacks and coroutines from both sync and async
# methods.
#
#############################################################################


def schedule_callback(delay, callback, *args, **kwargs):
    """
    Schedule callback (which is passed args and kwargs) to be called on
    running event loop after delay seconds (can be floating point).  Returns
    asyncio.TimerHandle on which cancel() can be called to cancel the
    eventual invocation of the callback.
    """
    # Using "asyncio.get_running_loop()" requires the event loop to be running
    # already, so we use "asyncio.get_event_loop()" here so that we can support
    # scheduling tasks before the server is started.
    loop = asyncio.get_event_loop()
    return loop.call_later(delay, functools.partial(callback, *args, **kwargs))


def schedule_coroutine(delay, coro_func, *args, **kwargs):
    """
    Creates a coroutine out of the provided coroutine function coro_func and
    the provided args and kwargs, then schedules the coroutine to be called
    on the running event loop after delay seconds (delay can be float or int).

    Returns asyncio.Task on which cancel() can be called to cancel the running
    of the coroutine.

    The coro_func parameter should not be a coroutine, but rather a coroutine
    function (a function defined with async).  The reason for this is we want
    to defer creation of the actual coroutine until we're ready to schedule it
    with "ensure_future".  Otherwise every time we cancel a TimerTask
    returned by "call_later", python prints "RuntimeWarning: coroutine
    '<coro-name>' was never awaited".
    """
    # See method above for comment on "get_event_loop()" vs "get_running_loop()".
    loop = asyncio.get_event_loop()
    coro_partial = functools.partial(coro_func, *args, **kwargs)
    return loop.call_later(delay, lambda: asyncio.ensure_future(coro_partial()))
