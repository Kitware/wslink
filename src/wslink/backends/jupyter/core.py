from functools import partial

from IPython.core.getipython import get_ipython

from wslink.backends.generic.core import GenericServer
from wslink.emitter import EventEmitter


class WsJupyterComm(EventEmitter):
    def __init__(self, kernel=None):
        super().__init__()
        self.comm = None
        self.kernel = get_ipython().kernel if kernel is None else kernel
        self.kernel.comm_manager.register_target("wslink_comm", self.on_open)

    def send(self, data, buffers):
        if self.comm is not None:
            self.comm.send(data=data, buffers=buffers)

    def on_message(self, msg):
        self.emit("message", msg["content"]["data"], msg["buffers"])

    def on_close(self, _):
        self.comm = None

    def on_open(self, comm, _):
        self.comm = comm
        comm.on_msg(self.on_message)
        comm.on_close(self.on_close)


JUPYTER_COMM = None


def get_jupyter_comm(kernel=None):
    global JUPYTER_COMM  # noqa: PLW0603
    if JUPYTER_COMM is None:
        JUPYTER_COMM = WsJupyterComm(kernel)

    return JUPYTER_COMM


class GenericMessage:
    def __init__(self, data):
        self.data = data


class JupyterGenericServer(GenericServer):
    def __init__(self, server_config):
        super().__init__(server_config)

        self.trame_comm = get_jupyter_comm()
        self._endpoint = self[self.ws_endpoints[0]]
        self._name = self._endpoint.serverProtocol.server.name
        self._connections = {}
        self.trame_comm.add_event_listener("message", self.on_msg_from_comm)

    async def on_msg_from_server(self, client_id, binary, content):
        buffers = []
        data = {"server": self._name, "client": client_id}

        if binary:
            buffers.append(content)
        else:
            data["payload"] = content

        self.trame_comm.send(data, buffers)

    async def on_msg_from_comm(self, data, buffers):
        server_name = data["server"]
        client_id = data["client"]

        if server_name != self._name:
            return

        connection = self._connections.get(client_id, None)

        if connection is None:
            connection = await self._endpoint.connect()
            connection.on_message(partial(self.on_msg_from_server, client_id))
            self._connections[client_id] = connection

        is_binary = len(buffers) > 0

        message = None

        if is_binary:
            message = GenericMessage(buffers[0])
        else:
            message = GenericMessage(data["payload"])

        await connection.send(is_binary, message)


def startWebServer(*_, **__):
    msg = "Generic backend does not provide a launcher"
    raise NotImplementedError(msg)


def create_webserver(server_config):
    return JupyterGenericServer(server_config)
