import asyncio

import aiohttp
import pytest
from aiohttp import web

from wslink.backends.aiohttp import WebAppServer
from wslink.websocket import ServerProtocol


def _text_handler(text):
    async def handler(_request):
        return web.Response(text=text)

    return handler


async def _start(server):
    port = asyncio.get_running_loop().create_future()
    task = asyncio.create_task(server.start(port.set_result))
    return await asyncio.wait_for(port, timeout=5), task


async def _get(port, path, allow_redirects=False):
    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:{port}{path}"
        async with session.get(url, allow_redirects=allow_redirects) as response:
            return response.status, await response.text()


@pytest.fixture
def www(tmp_path):
    (tmp_path / "index.html").write_text("static index")
    (tmp_path / "app.js").write_text("static js")
    return tmp_path


def _create_server(www):
    return WebAppServer(
        {
            "host": "localhost",
            "port": 0,
            "timeout": 0,
            "handle_signals": False,
            "static": {"/": str(www)},
        }
    )


@pytest.mark.asyncio
async def test_default_routes(www):
    server = _create_server(www)
    port, task = await _start(server)
    try:
        assert await _get(port, "/app.js") == (200, "static js")
        assert await _get(port, "/index.html") == (200, "static index")
        assert (await _get(port, "/"))[0] == 302
        assert (await _get(port, "/?ui=dark"))[0] == 302
        # Following the redirect resolves to index.html
        assert await _get(port, "/", allow_redirects=True) == (200, "static index")
        assert await _get(port, "/?ui=dark", allow_redirects=True) == (
            200,
            "static index",
        )
    finally:
        await server.stop()
        await task


@pytest.mark.asyncio
async def test_routes_added_before_start_take_precedence(www):
    server = _create_server(www)

    # Routes registered between creation and start (e.g. trame's on_server_bind)
    server.app.router.add_routes(
        [
            web.get("/", _text_handler("custom root")),
            web.get("/index.html", _text_handler("custom index")),
            web.get("/api/hello", _text_handler("hello")),
        ]
    )

    port, task = await _start(server)
    try:
        assert await _get(port, "/") == (200, "custom root")
        assert await _get(port, "/index.html") == (200, "custom index")
        assert await _get(port, "/api/hello") == (200, "hello")
        # Static content is still served for everything else
        assert await _get(port, "/app.js") == (200, "static js")
    finally:
        await server.stop()
        await task


async def _ws_compress(port):
    url = f"ws://localhost:{port}/ws"
    async with (
        aiohttp.ClientSession() as session,
        session.ws_connect(url, compress=15) as ws,
    ):
        # Negotiated permessage-deflate window bits (0 => disabled)
        compress = ws.compress
        await ws.close()
        return compress


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("env", "config", "expected"),
    [
        ("1", {}, True),
        ("0", {}, False),
        ("1", {"ws_compress": False}, False),
        ("0", {"ws_compress": True}, True),
    ],
)
async def test_ws_compression(monkeypatch, env, config, expected):
    monkeypatch.setenv("WSLINK_WS_COMPRESS", env)
    server = WebAppServer(
        {
            "host": "localhost",
            "port": 0,
            "timeout": 0,
            "handle_signals": False,
            "ws": {"ws": ServerProtocol()},
            **config,
        }
    )
    port, task = await _start(server)
    try:
        assert bool(await _ws_compress(port)) == expected
    finally:
        await server.stop()
        await task
