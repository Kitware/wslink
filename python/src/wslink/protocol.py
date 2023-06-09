import asyncio
import copy
import inspect
import json
import logging
import re
import traceback

from wslink import schedule_coroutine
from wslink import publish as pub


class AbstractWebApp:
    def __init__(self, server_config):
        self._last_active_client_id = None
        self._config = server_config
        self._shutdown_task = None
        self._completion = asyncio.get_event_loop().create_future()

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
    # Legacy / deprecated
    # -------------------------------------------------------------------------

    def set_app(self, *args):
        print("DEPRECATED: set_app()")

    def get_config(self):
        print("DEPRECATED: get_config() use property instead")
        return self.config

    def set_config(self, config):
        print("DEPRECATED: set_config() use constructor instead")

    def get_app(self):
        print("DEPRECATED: get_app()")
        return self

    @property
    def app(self):
        print("DEPRECATED: .app.")

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
            logging.info("Canceling shutdown task")
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
            self.publishManager.registerProtocol(self)

    def setServerProtocol(self, protocol):
        self.serverProtocol = protocol

    def getServerProtocol(self):
        return self.serverProtocol

    @property
    def publishManager(self):
        return pub.publishManager

    @property
    def reverse_connection_client_id(self):
        return "reverse_connection_client_id"

    async def onConnect(self, request, client_id):
        if not self.serverProtocol:
            return
        if hasattr(self.serverProtocol, "onConnect"):
            self.serverProtocol.onConnect(request, client_id)
        for linkProtocol in self.serverProtocol.getLinkProtocols():
            if hasattr(linkProtocol, "onConnect"):
                linkProtocol.onConnect(request, client_id)

    async def onClose(self, client_id):
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
                    await self.sendWrappedMessage(
                        rpcid,
                        {"clientID": "c{0}".format(client_id)},
                        client_id=client_id,
                    )
                else:
                    await self.sendWrappedError(
                        rpcid,
                        pub.AUTHENTICATION_ERROR,
                        "Authentication failed",
                        client_id=client_id,
                    )
            else:
                await self.sendWrappedError(
                    rpcid,
                    pub.METHOD_NOT_FOUND,
                    "Unknown system method called",
                    client_id=client_id,
                )
            return True
        return False

    async def onMessage(self, is_binary, msg, client_id):
        payload = msg.data

        if is_binary:
            if self.isClientAuthenticated(client_id):
                # assume all binary messages are attachments
                try:
                    key = self.attachmentsRecvQueue.pop(0)
                    self.attachmentsReceived[key] = payload
                except:
                    pass
                return

        # handles issue https://bugs.python.org/issue10976
        # `payload` is type bytes in Python 3. Unfortunately, json.loads
        # doesn't support taking bytes until Python 3.6.
        if type(payload) is bytes:
            payload = payload.decode("utf-8")

        rpc = json.loads(payload)
        logging.debug("wslink incoming msg %s" % self.payloadWithSecretStripped(rpc))
        if "id" not in rpc:
            # should be a binary attachment header
            if rpc.get("method") == "wslink.binary.attachment":
                keys = rpc.get("args", [])
                if isinstance(keys, list):
                    for k in keys:
                        # wait for an attachment by it's order
                        self.attachmentsRecvQueue.append(k)
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
                pub.AUTHENTICATION_ERROR,
                "Unauthorized: Skip message processing",
                client_id=client_id,
            )
            return

        # No matching method found
        if not methodName in self.functionMap:
            await self.sendWrappedError(
                rpcid,
                pub.METHOD_NOT_FOUND,
                "Unregistered method called",
                methodName,
                client_id=client_id,
            )
            return

        obj, func = self.functionMap[methodName]
        try:
            # get any attachments
            def findAttachments(o):
                if (
                    isinstance(o, str)
                    and re.match(r"^wslink_bin\d+$", o)
                    and o in self.attachmentsReceived
                ):
                    attachment = self.attachmentsReceived[o]
                    del self.attachmentsReceived[o]
                    return attachment
                elif isinstance(o, list):
                    for i, v in enumerate(o):
                        o[i] = findAttachments(v)
                elif isinstance(o, dict):
                    for k in o:
                        o[k] = findAttachments(o[k])
                return o

            args = findAttachments(args)
            kwargs = findAttachments(kwargs)

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
                logging.error("Exception raised")
                logging.error(repr(e_inst))
                logging.error(captured_trace)
                await self.sendWrappedError(
                    rpcid,
                    pub.EXCEPTION_ERROR,
                    "Exception raised",
                    {
                        "method": methodName,
                        "exception": repr(e_inst),
                        "trace": captured_trace,
                    },
                    client_id=client_id,
                )

        except Exception as e:
            await self.sendWrappedError(
                rpcid,
                pub.EXCEPTION_ERROR,
                "Exception raised",
                {
                    "method": methodName,
                    "exception": repr(e),
                    "trace": traceback.format_exc(),
                },
                client_id=client_id,
            )
            return

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
            encMsg = json.dumps(wrapper, ensure_ascii=False)
        except TypeError as e:
            # the content which is not serializable might be arbitrarily large, don't include.
            # repr(content) would do that...
            await self.sendWrappedError(
                rpcid,
                pub.RESULT_SERIALIZE_ERROR,
                "Method result cannot be serialized",
                method,
                client_id=client_id,
            )
            return

        websockets = self.getAuthenticatedWebsockets(client_id, skip_last_active_client)

        # Check if any attachments in the map go with this message
        attachments = self.publishManager.getAttachmentMap()
        found_keys = []
        if attachments:
            for key in attachments:
                # string match the encoded attachment key
                if key in encMsg:
                    if key not in found_keys:
                        found_keys.append(key)
                    # increment  for key
                    self.publishManager.registerAttachment(key)

            for key in found_keys:
                # send header
                header = {
                    "wslink": "1.0",
                    "method": "wslink.binary.attachment",
                    "args": [key],
                }
                json_header = json.dumps(header, ensure_ascii=False)

                # aiohttp can not handle pending ws.send_bytes()
                # tried with semaphore but got exception with >1
                # https://github.com/aio-libs/aiohttp/issues/2934
                async with self.attachment_atomic:
                    for ws in websockets:
                        if ws is not None:
                            # Send binary header
                            await ws.send_str(json_header)
                            # Send binary message
                            await ws.send_bytes(attachments[key])

                # decrement for key
                self.publishManager.unregisterAttachment(key)

        for ws in websockets:
            if ws is not None:
                await ws.send_str(encMsg)

        loop = asyncio.get_event_loop()
        loop.call_soon(self.publishManager.freeAttachments, found_keys)

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
        encMsg = json.dumps(wrapper, ensure_ascii=False)
        websockets = (
            [self.connections[client_id]]
            if client_id
            else [self.connections[c] for c in self.connections]
        )
        for ws in websockets:
            if ws is not None:
                await ws.send_str(encMsg)

    def publish(self, topic, data, client_id=None, skip_last_active_client=False):
        client_list = [client_id] if client_id else [c_id for c_id in self.connections]
        for client in client_list:
            if self.isClientAuthenticated(client):
                self.publishManager.publish(
                    topic,
                    data,
                    client_id=client,
                    skip_last_active_client=skip_last_active_client,
                )

    def addAttachment(self, payload):
        return self.publishManager.addAttachment(payload)

    def setSecret(self, newSecret):
        self.secret = newSecret
