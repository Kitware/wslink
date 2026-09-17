import asyncio
import contextlib
import socket

import aiohttp
import msgpack
import pytest

from wslink import register as exportRPC
from wslink import server as wslink_server
from wslink.chunking import UnChunker, generate_chunks
from wslink.websocket import LinkProtocol, ServerProtocol

SECRET = "wslink-test-secret"


class _MathProtocol(LinkProtocol):
    @exportRPC("test.add")
    def add(self, values):
        return sum(values)


class _Protocol(ServerProtocol):
    def initialize(self):
        self.registerLinkProtocol(_MathProtocol())
        self.updateSecret(SECRET)


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def _rpc_call(ws, unchunker, rpc_id, method, args):
    payload = msgpack.packb(
        {"wslink": "1.0", "id": rpc_id, "method": method, "args": args}
    )
    for chunk in generate_chunks(payload, 0):
        await ws.send_bytes(chunk)

    async for msg in ws:
        full_message = unchunker.process_chunk(msg.data)
        if full_message is not None:
            return full_message
    return None


@contextlib.asynccontextmanager
async def _running_server(server_config):
    ws_server = wslink_server.create_webserver(server_config, backend="robyn")
    ready = asyncio.Event()
    start_task = asyncio.ensure_future(ws_server.start(lambda _port: ready.set()))
    try:
        await asyncio.wait_for(ready.wait(), timeout=15)
        yield ws_server
    finally:
        await ws_server.stop()
        await asyncio.wait_for(start_task, timeout=5)


@pytest.mark.asyncio
async def test_robyn_backend_ws_rpc_and_static_content(tmp_path):
    # Robyn's Rust logger can only be installed once per process (a second
    # `Server.start()` call panics and aborts the interpreter), so this
    # exercises websockets and static content through a single server
    # instance rather than one server per test.
    (tmp_path / "index.html").write_text("<html>hello wslink</html>")
    sub_dir = tmp_path / "assets"
    sub_dir.mkdir()
    (sub_dir / "app.js").write_text("console.log('hi')")

    port = _free_port()
    server_config = {
        "host": "127.0.0.1",
        "port": port,
        "timeout": 0,
        "ws": {"/ws": _Protocol()},
        "static": {"/": str(tmp_path)},
    }

    async with _running_server(server_config):
        async with (
            aiohttp.ClientSession() as session,
            session.ws_connect(f"http://127.0.0.1:{port}/ws") as ws,
        ):
            unchunker = UnChunker()
            unchunker.set_max_message_size(4 * 1024 * 1024)

            hello_reply = await _rpc_call(
                ws, unchunker, "system:0:0", "wslink.hello", [{"secret": SECRET}]
            )
            assert "clientID" in hello_reply["result"]

            add_reply = await _rpc_call(
                ws, unchunker, "rpc:add:0", "test.add", [[1, 2, 3]]
            )
            assert add_reply["result"] == 6

        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://127.0.0.1:{port}/") as resp:
                assert resp.status == 200
                assert "hello wslink" in await resp.text()
                assert resp.url.path == "/index.html"

            async with session.get(f"http://127.0.0.1:{port}/assets/app.js") as resp:
                assert resp.status == 200
                assert "console.log" in await resp.text()

            async with session.get(f"http://127.0.0.1:{port}/missing.txt") as resp:
                assert resp.status == 404
