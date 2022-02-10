from typing import Dict, List, Optional, TypedDict

from wslink.websocket import ServerProtocol


class ServerConfig(TypedDict, total=False):
    # The network interface to bind to. If None,
    # bind to all interfaces.
    host: Optional[str]
    # HTTP port to listen to.
    port: int
    # Idle shutdown timeout, in seconds.
    timeout: float
    # websocket routes.
    ws: Dict[str, ServerProtocol]
    # static file serving routes
    static: Dict[str, str]
    logging_level: Optional[int]
    handle_signals: bool
