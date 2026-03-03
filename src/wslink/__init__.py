r"""
Wslink allows easy, bi-directional communication between a python server and a
javascript client over a websocket.

wslink.server creates the python server
wslink.websocket handles the communication
"""

from wslink.core import register, schedule_callback, schedule_coroutine

__license__ = "BSD-3-Clause"
__version__ = "2.5.3"

__all__ = [
    "__license__",
    "__version__",
    "register",
    "schedule_callback",
    "schedule_coroutine",
]
