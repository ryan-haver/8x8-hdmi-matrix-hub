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


async def test_api_key_is_sent_on_rest_requests() -> None:
    seen: list[str | None] = []

    async def record(request: web.Request) -> web.Response:
        seen.append(request.headers.get("X-API-Key"))
        return web.json_response({"success": True, "data": {}, "error": None})

    app = web.Application()
    app.router.add_get("/api/health", record)
    app.router.add_post("/api/power/on", record)
    async with TestServer(app, host="127.0.0.1") as server, aiohttp.ClientSession() as session:
        client = HubClient(session, "127.0.0.1", server.port, "ha-key")
        await client.health()
        await client.set_power(True)
    assert seen == ["ha-key", "ha-key"]


async def test_unreachable_hub_is_a_connection_error() -> None:
    async with aiohttp.ClientSession() as session:
        client = HubClient(session, "127.0.0.1", 9)  # discard port: connection refused
        with pytest.raises(HubConnectionError):
            await client.status()


@pytest.mark.parametrize(
    ("host", "url"),
    [
        ("192.0.2.10", "http://192.0.2.10:8080"),
        ("hub.local", "http://hub.local:8080"),
        ("fd00::10", "http://[fd00::10]:8080"),
        ("[fd00::10]", "http://[fd00::10]:8080"),
    ],
)
async def test_base_url_brackets_ipv6(host: str, url: str) -> None:
    """An IPv6 hub address must be bracketed in the URL (the ha validation client's reconfigure run
    on Docker Desktop, which resolves the host to IPv6, found this). The HA test harness only allows
    127.0.0.1, so the connection itself is not exercised here."""
    async with aiohttp.ClientSession() as session:
        assert HubClient(session, host, 8080).base_url == url


async def test_auth_status_reads_the_bare_answer_of_the_auth_routes() -> None:
    """``/api/auth/*`` answers a bare object: requiring ``success`` made it an error."""
    locked = {"admin_pin_set": False, "control_pin_set": True, "session_level": "none", "device_remembered": False}
    seen: list[str | None] = []

    async def status(request: web.Request) -> web.Response:
        key = request.headers.get("X-API-Key")
        seen.append(key)
        return web.json_response({**locked, "session_level": "control" if key == "ha-key" else "none"})

    app = web.Application()
    app.router.add_get("/api/auth/status", status)
    server = TestServer(app, host="127.0.0.1")
    await server.start_server()
    try:
        async with aiohttp.ClientSession() as session:
            without = HubClient(session, "127.0.0.1", server.port)
            wrong = HubClient(session, "127.0.0.1", server.port, "wrong-key")
            right = HubClient(session, "127.0.0.1", server.port, "ha-key")

            assert await without.auth_status() == locked
            assert [await client.control_allowed() for client in (without, wrong, right)] == [False, False, True]
            assert seen == [None, None, "wrong-key", "ha-key"]
            assert not session.connector._acquired, "a response was not released"  # noqa: SLF001
    finally:
        await server.close()


async def test_auth_status_errors_are_hub_errors() -> None:
    async def missing(_request: web.Request) -> web.Response:
        return web.Response(text="404: Not Found", status=404)

    app = web.Application()
    app.router.add_get("/api/auth/status", missing)
    server = TestServer(app, host="127.0.0.1")
    await server.start_server()
    try:
        async with aiohttp.ClientSession() as session:
            with pytest.raises(HubResponseError) as error:
                await HubClient(session, "127.0.0.1", server.port).auth_status()
            assert error.value.status == 404
    finally:
        await server.close()


@pytest.mark.parametrize(
    ("content_type", "raw_body"),
    [
        ("text/plain", "ok"),
        ("application/json", "null"),
        ("application/json", "[]"),
        ("application/json", "{}"),
        ("application/json", '{"success": true, "data": {"control_pin_set": false}}'),
        ("application/json", '{"control_pin_set": "false", "session_level": "none"}'),
        ("application/json", '{"control_pin_set": 0, "session_level": "none"}'),
        ("application/json", '{"control_pin_set": null, "session_level": "none"}'),
        ("application/json", '{"control_pin_set": false}'),
        ("application/json", '{"control_pin_set": false, "session_level": "superuser"}'),
        ("application/json", '{"control_pin_set": false, "session_level": 1}'),
        ("application/json", '{"control_pin_set": false, "session_level": "none", "admin_pin_set": "no"}'),
        ("application/json", '{"control_pin_set": false, "session_level": "none", "device_remembered": 1}'),
    ],
)
async def test_auth_status_and_control_allowed_reject_malformed_200_payloads(
    content_type: str, raw_body: str
) -> None:
    """Malformed HTTP 200 answers on ``/api/auth/status`` raise ``HubResponseError`` (fail closed)."""

    async def malformed(_request: web.Request) -> web.Response:
        return web.Response(text=raw_body, content_type=content_type, status=200)

    app = web.Application()
    app.router.add_get("/api/auth/status", malformed)
    async with TestServer(app, host="127.0.0.1") as server, aiohttp.ClientSession() as session:
        client = HubClient(session, "127.0.0.1", server.port, "ha-key")
        with pytest.raises(HubResponseError) as auth_err:
            await client.auth_status()
        assert auth_err.value.status == 200
        with pytest.raises(HubResponseError) as ctrl_err:
            await client.control_allowed()
        assert ctrl_err.value.status == 200
        connector = session.connector
        assert connector is not None
        assert not connector._acquired, "a response was not released"  # noqa: SLF001
