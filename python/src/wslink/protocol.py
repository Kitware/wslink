import asyncio
import copy
import inspect
import logging
import msgpack
import os
import traceback

from wslink import schedule_coroutine
from wslink.publish import PublishManager
from wslink.chunking import generate_chunks, UnChunker

# from http://www.jsonrpc.org/specification, section 5.1
METHOD_NOT_FOUND = -32601
AUTHENTICATION_ERROR = -32000
EXCEPTION_ERROR = -32001
RESULT_SERIALIZE_ERROR = -32002
# used in client JS code:
CLIENT_ERROR = -32099

# 4MB is the default inside aiohttp
MAX_MSG_SIZE = int(os.environ.get("WSLINK_MAX_MSG_SIZE", 4194304))

logger = logging.getLogger(__name__)


class AbstractWebApp:
    def __init__(self, server_config):
        self._last_active_client_id = None
        self._config = server_config
        self._shutdown_task = None
        self._completion = asyncio.get_event_loop().create_future()
        self._app = None

    # -------------------------------------------------------------------------
    # Config helper
    # -------------------------------------------------------------------------

    @property
    def config(self):
        return self._config

    @property
    def timeout(self):
        return int(self.config.get("timeout", "0"))

    @property
    def host(self):
        return self.config.get("host", "127.0.0.1")

    @property
    def port(self):
        return int(self.config.get("port", "8080"))

    @property
    def handle_signals(self):
        return self.config.get("handle_signals", True)

    @property
    def ssl_context(self):
        return self.config.get("ssl", None)

    # -------------------------------------------------------------------------
    # In flight state
    # -------------------------------------------------------------------------

    @property
    def last_active_client_id(self):
        return self._last_active_client_id

    @last_active_client_id.setter
    def last_active_client_id(self, value):
        self._last_active_client_id = value

    # -------------------------------------------------------------------------
    # Implementation server class
    # -------------------------------------------------------------------------

    def set_app(self, app):
        self._app = app

    def get_app(self):
        return self._app

    @property
    def app(self):
        return self._app

    # -------------------------------------------------------------------------
    # Legacy / deprecated
    # -------------------------------------------------------------------------

    def get_config(self):
        print("DEPRECATED: get_config() use property instead")
        return self.config

    def set_config(self, config):
        print("DEPRECATED: set_config() use constructor instead")

    def get_last_active_client_id(self):
        print(
            "DEPRECATED: get_last_active_client_id() should be replaced by last_active_client_id"
        )
        return self.last_active_client_id

    # -------------------------------------------------------------------------
    # Life cycles
    # -------------------------------------------------------------------------

    def shutdown_schedule(self):
        self._shutdown_task = (
            schedule_coroutine(self.timeout, self.stop) if self.timeout > 0 else None
        )

    def shutdown_cancel(self):
        if self._shutdown_task is not None:
            logger.info("Canceling shutdown task")
            self._shutdown_task.cancel()
            self._shutdown_task = None

    # -------------------------------------------------------------------------
    # Server status
    # -------------------------------------------------------------------------

    @property
    def completion(self):
        return self._completion

    def get_port(self):
        return 0

    # -------------------------------------------------------------------------
    # Need override
    # -------------------------------------------------------------------------

    async def start(self, port_callback=None):
        pass

    async def stop(self):
        pass


class WslinkHandler(object):
    def __init__(self, protocol=None, web_app=None):
        self.serverProtocol = protocol
        self.web_app = web_app
        self.functionMap = {}
        self.attachmentsReceived = {}
        self.attachmentsRecvQueue = []
        self.connections = {}
        self.authentified_client_ids = set()
        self.attachment_atomic = asyncio.Lock()
        self.pub_manager = PublishManager()
        self.unchunkers = {}

        # Build the rpc method dictionary, assuming we were given a serverprotocol
        if self.getServerProtocol():
            protocolList = self.getServerProtocol().getLinkProtocols()
            protocolList.append(self.getServerProtocol())
            for protocolObject in protocolList:
                protocolObject.init(
                    self.publish,
                    self.addAttachment,
                    lambda: schedule_coroutine(0, self.web_app.stop),
                )
                test = lambda x: inspect.ismethod(x) or inspect.isfunction(x)
                for k in inspect.getmembers(protocolObject.__class__, test):
                    proc = k[1]
                    if "_wslinkuris" in proc.__dict__:
                        uri_info = proc.__dict__["_wslinkuris"][0]
                        if "uri" in uri_info:
                            uri = uri_info["uri"]
                            self.functionMap[uri] = (protocolObject, proc)
            self.pub_manager.registerProtocol(self)

    def setServerProtocol(self, protocol):
        self.serverProtocol = protocol

    def getServerProtocol(self):
        return self.serverProtocol

    @property
    def publishManager(self):
        return self.pub_manager

    @property
    def reverse_connection_client_id(self):
        return "reverse_connection_client_id"

    async def onConnect(self, request, client_id):
        self.unchunkers[client_id] = UnChunker()

        if not self.serverProtocol:
            return
        if hasattr(self.serverProtocol, "onConnect"):
            self.serverProtocol.onConnect(request, client_id)
        for linkProtocol in self.serverProtocol.getLinkProtocols():
            if hasattr(linkProtocol, "onConnect"):
                linkProtocol.onConnect(request, client_id)

    async def onClose(self, client_id):
        del self.unchunkers[client_id]

        if not self.serverProtocol:
            return
        if hasattr(self.serverProtocol, "onClose"):
            self.serverProtocol.onClose(client_id)
        for linkProtocol in self.serverProtocol.getLinkProtocols():
            if hasattr(linkProtocol, "onClose"):
                linkProtocol.onClose(client_id)

    async def handleSystemMessage(self, rpcid, methodName, args, client_id):
        rpcList = rpcid.split(":")
        if rpcList[0] == "system":
            if methodName == "wslink.hello":
                if (
                    args
                    and args[0]
                    and (type(args[0]) is dict)
                    and ("secret" in args[0])
                    and await self.validateToken(args[0]["secret"], client_id)
                ):
                    self.authentified_client_ids.add(client_id)
                    # Once a client is authenticated let the unchunker allocate memory unrestricted
                    self.unchunkers[client_id].set_max_message_size(
                        4 * 1024 * 1024 * 1024
                    )  # 4GB
                    await self.sendWrappedMessage(
                        rpcid,
                        {
                            "clientID": "c{0}".format(client_id),
                            "maxMsgSize": MAX_MSG_SIZE,
                        },
                        client_id=client_id,
                    )
                else:
                    await self.sendWrappedError(
                        rpcid,
                        AUTHENTICATION_ERROR,
                        "Authentication failed",
                        client_id=client_id,
                    )
            else:
                await self.sendWrappedError(
                    rpcid,
                    METHOD_NOT_FOUND,
                    "Unknown system method called",
                    client_id=client_id,
                )
            return True
        return False

    async def onMessage(self, is_binary, msg, client_id):
        if not is_binary:
            return

        full_message = self.unchunkers[client_id].process_chunk(msg.data)
        if full_message is not None:
            await self.onCompleteMessage(full_message, client_id)

    async def onCompleteMessage(self, rpc, client_id):
        logger.debug("wslink incoming msg %s", self.payloadWithSecretStripped(rpc))
        if "id" not in rpc:
            return

        # TODO validate
        # version = rpc["wslink"]
        rpcid = rpc["id"]
        methodName = rpc["method"]

        args = []
        kwargs = {}
        if ("args" in rpc) and isinstance(rpc["args"], list):
            args = rpc["args"]
        if ("kwargs" in rpc) and isinstance(rpc["kwargs"], dict):
            kwargs = rpc["kwargs"]

        # Check for system messages, like hello
        if await self.handleSystemMessage(rpcid, methodName, args, client_id):
            return

        # Prevent any further processing if token is not valid
        if not self.isClientAuthenticated(client_id):
            await self.sendWrappedError(
                rpcid,
                AUTHENTICATION_ERROR,
                "Unauthorized: Skip message processing",
                client_id=client_id,
            )
            return

        # No matching method found
        if not methodName in self.functionMap:
            await self.sendWrappedError(
                rpcid,
                METHOD_NOT_FOUND,
                "Unregistered method called",
                methodName,
                client_id=client_id,
            )
            return

        obj, func = self.functionMap[methodName]
        args.insert(0, obj)

        try:
            self.web_app.last_active_client_id = client_id
            results = func(*args, **kwargs)
            if inspect.isawaitable(results):
                results = await results

            if self.connections[client_id].closed:
                # Connection was closed during RPC call.
                return

            await self.sendWrappedMessage(
                rpcid, results, method=methodName, client_id=client_id
            )
        except Exception as e_inst:
            captured_trace = traceback.format_exc()
            logger.error("Exception raised")
            logger.error(repr(e_inst))
            logger.error(captured_trace)
            await self.sendWrappedError(
                rpcid,
                EXCEPTION_ERROR,
                "Exception raised",
                {
                    "method": methodName,
                    "exception": repr(e_inst),
                    "trace": captured_trace,
                },
                client_id=client_id,
            )

    def payloadWithSecretStripped(self, payload):
        payload = copy.deepcopy(payload)
        if "args" in payload:
            for arg in payload["args"]:
                if type(arg) is dict and "secret" in arg:
                    arg["secret"] = "*****"
        return payload

    async def validateToken(self, token, client_id):
        if not self.serverProtocol:
            return True
        token_tested = False
        if hasattr(self.serverProtocol, "validateToken"):
            token_tested = True
            if not await self.serverProtocol.validateToken(token, client_id):
                return False
        for linkProtocol in self.serverProtocol.getLinkProtocols():
            if hasattr(linkProtocol, "validateToken"):
                token_tested = True
                if not await linkProtocol.validateToken(token, client_id):
                    return False
        if token_tested:
            return True
        return token == self.serverProtocol.secret

    def isClientAuthenticated(self, client_id):
        return client_id in self.authentified_client_ids

    def getAuthenticatedWebsockets(self, client_id=None, skip_last_active_client=False):
        if skip_last_active_client:
            last_c = self.web_app.last_active_client_id
            return [
                self.connections[c]
                for c in self.connections
                if self.isClientAuthenticated(c) and c != last_c
            ]

        if client_id:
            if self.isClientAuthenticated(client_id):
                return [self.connections.get(client_id)]
            else:
                return []

        return [
            self.connections[c]
            for c in self.connections
            if self.isClientAuthenticated(c)
        ]

    async def sendWrappedMessage(
        self, rpcid, content, method="", client_id=None, skip_last_active_client=False
    ):
        wrapper = {
            "wslink": "1.0",
            "id": rpcid,
            "result": content,
        }

        try:
            packed_wrapper = msgpack.packb(wrapper)
        except Exception:
            # the content which is not serializable might be arbitrarily large, don't include.
            # repr(content) would do that...
            await self.sendWrappedError(
                rpcid,
                RESULT_SERIALIZE_ERROR,
                "Method result cannot be serialized",
                method,
                client_id=client_id,
            )
            return

        websockets = self.getAuthenticatedWebsockets(client_id, skip_last_active_client)

        # aiohttp can not handle pending ws.send_bytes()
        # tried with semaphore but got exception with >1
        # https://github.com/aio-libs/aiohttp/issues/2934
        async with self.attachment_atomic:
            for chunk in generate_chunks(packed_wrapper, MAX_MSG_SIZE):
                for ws in websockets:
                    if ws is not None:
                        await ws.send_bytes(chunk)

    async def sendWrappedError(self, rpcid, code, message, data=None, client_id=None):
        wrapper = {
            "wslink": "1.0",
            "id": rpcid,
            "error": {
                "code": code,
                "message": message,
            },
        }
        if data:
            wrapper["error"]["data"] = data

        try:
            packed_wrapper = msgpack.packb(wrapper)
        except Exception:
            del wrapper["error"]["data"]
            packed_wrapper = msgpack.packb(wrapper)

        websockets = (
            [self.connections[client_id]]
            if client_id
            else [self.connections[c] for c in self.connections]
        )
        # aiohttp can not handle pending ws.send_bytes()
        # tried with semaphore but got exception with >1
        # https://github.com/aio-libs/aiohttp/issues/2934
        async with self.attachment_atomic:
            for chunk in generate_chunks(packed_wrapper, MAX_MSG_SIZE):
                for ws in websockets:
                    if ws is not None:
                        await ws.send_bytes(chunk)

    def publish(self, topic, data, client_id=None, skip_last_active_client=False):
        client_list = [client_id] if client_id else [c_id for c_id in self.connections]
        for client in client_list:
            if self.isClientAuthenticated(client):
                self.pub_manager.publish(
                    topic,
                    data,
                    client_id=client,
                    skip_last_active_client=skip_last_active_client,
                )

    def addAttachment(self, payload):
        return self.pub_manager.addAttachment(payload)

    def setSecret(self, newSecret):
        self.secret = newSecret
