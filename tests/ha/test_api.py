"""The hub client against a real HTTP server: every response is released (HA-08).

``aioclient_mock`` has no connection pool, so these tests serve real HTTP on
localhost and check the session's connector: a response that is not released
keeps its connection "acquired".
"""

from __future__ import annotations

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from custom_components.hdmi_matrix.api import HubClient, HubConnectionError, HubResponseError

# Real sockets on localhost (the HA test harness blocks sockets by default).
pytestmark = pytest.mark.usefixtures("socket_enabled")


def _app() -> web.Application:
    async def ok(_request: web.Request) -> web.Response:
        return web.json_response({"success": True, "data": {"routing": {"1": 2}}, "error": None})

    async def unavailable(_request: web.Request) -> web.Response:
        return web.json_response({"success": False, "data": None, "error": "Matrix not connected"}, status=503)

    async def refused(_request: web.Request) -> web.Response:
        return web.json_response({"success": False, "data": None, "error": "bad"}, status=200)

    async def not_json(_request: web.Request) -> web.Response:
        return web.Response(text="<html>proxy error</html>", status=502)

    app = web.Application()
    app.router.add_get("/api/status", ok)
    app.router.add_get("/api/status/outputs", unavailable)
    app.router.add_post("/api/preset/1", refused)
    app.router.add_get("/api/health", not_json)
    return app


@pytest.fixture
async def server():
    srv = TestServer(_app(), host="127.0.0.1")
    await srv.start_server()
    yield srv
    await srv.close()


async def test_every_response_is_released(server: TestServer) -> None:
    async with aiohttp.ClientSession() as session:
        client = HubClient(session, "127.0.0.1", server.port)
        assert (await client.status())["routing"] == {"1": 2}
        with pytest.raises(HubResponseError, match="Matrix not connected"):
            await client.outputs()
        with pytest.raises(HubResponseError, match="bad"):
            await client.recall_preset(1)
        with pytest.raises(HubResponseError, match="no JSON"):
            await client.health()
        connector = session.connector
        assert connector is not None
        assert not connector._acquired, "a response was not released"  # noqa: SLF001


async def test_unreachable_hub_is_a_connection_error() -> None:
    async with aiohttp.ClientSession() as session:
        client = HubClient(session, "127.0.0.1", 9)  # discard port: connection refused
        with pytest.raises(HubConnectionError):
            await client.status()
