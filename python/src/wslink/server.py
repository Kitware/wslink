r"""server is a module that enables using python through a web-server.

This module can be used as the entry point to the application. In that case, it
sets up a web-server.
web-pages are determines by the command line arguments passed in.
Use "--help" to list the supported arguments.

"""
import argparse
import asyncio
import logging

from wslink import websocket as wsl
from wslink import backends

ws_server = None


# =============================================================================
# Setup default arguments to be parsed
#   -s, --nosignalhandlers
#   -d, --debug
#   -i, --host     localhost
#   -p, --port     8080
#   -t, --timeout  300 (seconds)
#   -c, --content  '/www'  (No content means WebSocket only)
#   -a, --authKey  vtkweb-secret
# =============================================================================


def add_arguments(parser):
    """
    Add arguments known to this module. parser must be
    argparse.ArgumentParser instance.
    """
    import os

    parser.add_argument(
        "-d", "--debug", help="log debugging messages to stdout", action="store_true"
    )
    parser.add_argument(
        "-s",
        "--nosignalhandlers",
        help="Prevent installation of signal handlers so server can be started inside a thread.",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--host",
        type=str,
        default="localhost",
        help="the interface for the web-server to listen on (default: 0.0.0.0)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8080,
        help="port number for the web-server to listen on (default: 8080)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=300,
        help="timeout for reaping process on idle in seconds (default: 300s, 0 to disable)",
    )
    parser.add_argument(
        "-c",
        "--content",
        default="",
        help="root for web-pages to serve (default: none)",
    )
    parser.add_argument(
        "-a",
        "--authKey",
        default="wslink-secret",
        help="Authentication key for clients to connect to the WebSocket.",
    )
    parser.add_argument(
        "-ws",
        "--ws-endpoint",
        type=str,
        default="ws",
        dest="ws",
        help="Specify WebSocket endpoint. (e.g. foo/bar/ws, Default: ws)",
    )
    parser.add_argument(
        "--no-ws-endpoint",
        action="store_true",
        dest="nows",
        help="If provided, disables the websocket endpoint",
    )
    parser.add_argument(
        "--fs-endpoints",
        default="",
        dest="fsEndpoints",
        help="add another fs location to a specific endpoint (i.e: data=/Users/seb/Download|images=/Users/seb/Pictures)",
    )

    return parser


# =============================================================================
# Parse arguments and start webserver
# =============================================================================


def start(argv=None, protocol=wsl.ServerProtocol, description="wslink web-server"):
    """
    Sets up the web-server using with __name__ == '__main__'. This can also be
    called directly. Pass the optional protocol to override the protocol used.
    Default is ServerProtocol.
    """
    parser = argparse.ArgumentParser(description=description)
    add_arguments(parser)
    args = parser.parse_args(argv)
    # configure protocol, if available
    try:
        protocol.configure(args)
    except AttributeError:
        pass

    start_webserver(options=args, protocol=protocol)


# =============================================================================
# Stop webserver
# =============================================================================
def stop_webserver():
    if ws_server:
        loop = asyncio.get_event_loop()
        return loop.create_task(ws_server.stop())

# =============================================================================
# Get webserver port (useful when 0 is provided and a dynamic one was picked)
# =============================================================================
def get_port():
    if ws_server:
        return ws_server.get_port()
    return -1


# =============================================================================
# Given a configuration file, create and return a webserver
#
# config = {
#     "host": "0.0.0.0",
#     "port": 8081
#     "ws": {
#         "/ws": serverProtocolInstance,
#         ...
#     },
#     static_routes: {
#         '/static': .../path/to/files,
#         ...
#     },
# }
# =============================================================================
def create_webserver(server_config, backend="aiohttp"):
    return backends.create_webserver(server_config, backend=backend)


# =============================================================================
# Generate a webserver config from command line options, create a webserver,
# and start it.
# =============================================================================
def start_webserver(
    options, protocol=wsl.ServerProtocol, disableLogging=False, backend="aiohttp",
    exec_mode="main", **kwargs
):
    """
    Starts the web-server with the given protocol. Options must be an object
    with the following members:
        options.host : the interface for the web-server to listen on
        options.port : port number for the web-server to listen on
        options.timeout : timeout for reaping process on idle in seconds
        options.content : root for web-pages to serve.
    """
    global ws_server

    # Create default or custom ServerProtocol
    wslinkServer = protocol()

    server_config = {
        "host": options.host,
        "port": options.port,
        "timeout": options.timeout,
    }

    # Configure websocket endpoint
    if not options.nows:
        server_config["ws"] = {}
        server_config["ws"][options.ws] = wslinkServer

    # Configure default static route if --content requested
    if len(options.content) > 0:
        server_config["static"] = {}
        # Static HTTP + WebSocket
        server_config["static"]["/"] = options.content

    # Configure any other static routes
    if len(options.fsEndpoints) > 3:
        if "static" not in server_config:
            server_config["static"] = {}

        for fsResourceInfo in options.fsEndpoints.split("|"):
            infoSplit = fsResourceInfo.split("=")
            server_config["static"][infoSplit[0]] = infoSplit[1]

    if disableLogging:
        server_config["logging_level"] = None
    else:
        # Set logging level.
        if options.debug:
            server_config["logging_level"] = logging.DEBUG
        else:
            server_config["logging_level"] = logging.ERROR

    server_config["handle_signals"] = not options.nosignalhandlers

    # Create the webserver and start it
    ws_server = create_webserver(server_config, backend=backend)

    # Once we have python 3.7 minimum, we can start the server with asyncio.run()
    # asyncio.run(ws_server.start())

    # Until then, we can start the server this way
    loop = asyncio.get_event_loop()

    port_callback = None
    if hasattr(wslinkServer, "port_callback"):
        port_callback = wslinkServer.port_callback

    if hasattr(wslinkServer, "set_server"):
        wslinkServer.set_server(ws_server)

    def create_coroutine():
        return ws_server.start(port_callback)

    def main_exec():
        # Block until the loop finishes and then close the loop
        try:
            loop.run_until_complete(create_coroutine())
        finally:
            loop.close()

    def task_exec():
        return loop.create_task(create_coroutine())

    exec_modes = {
        "main": main_exec,
        "task": task_exec,
        "coroutine": create_coroutine,
    }

    if exec_mode not in exec_modes:
        raise Exception(f"Unknown exec_mode: {exec_mode}")

    return exec_modes[exec_mode]()


if __name__ == "__main__":
    start()
