"""The scripted Remote itself, against a scripted driver: the protocol paths ucapi 0.5.1 never takes.

ucapi always answers the connection with ``authentication`` (no token), so the
spec's message-based and header authentication, and the exact request shapes,
are checked here against an in-process WebSocket server that plays the driver
(core-api doc/integration-driver/websocket.md, UCR-integration-asyncapi.yaml).
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from aiohttp import WSCloseCode, web

from tools.uc_remote_sim import ConnectionClosedError, RemoteSimError, UcRemoteSim
from tools.validate.stack import free_port

Handler = Callable[[web.WebSocketResponse, list[dict[str, Any]]], Awaitable[None]]


@pytest.fixture
async def fake_driver():
    """Start a WebSocket server running ``handler(ws, received)``; returns ``(url, received)``."""
    runners: list[web.AppRunner] = []

    async def start(handler: Handler, *, token_header: str | None = None) -> tuple[str, list[dict[str, Any]]]:
        received: list[dict[str, Any]] = []

        async def ws_handler(request: web.Request) -> web.StreamResponse:
            if token_header is not None and request.headers.get("auth-token") != token_header:
                return web.Response(status=401)
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            await handler(ws, received)
            return ws

        app = web.Application()
        app.router.add_get("/", ws_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        port = free_port()
        await web.TCPSite(runner, "127.0.0.1", port).start()
        runners.append(runner)
        return f"ws://127.0.0.1:{port}/", received

    yield start
    for runner in runners:
        await runner.cleanup()


async def _recv(ws: web.WebSocketResponse, received: list[dict[str, Any]]) -> dict[str, Any] | None:
    msg = await ws.receive()
    if msg.type != web.WSMsgType.TEXT:
        return None
    data = json.loads(msg.data)
    received.append(data)
    return data


async def _no_auth(ws: web.WebSocketResponse) -> None:
    await ws.send_json({"kind": "resp", "req_id": 0, "code": 200, "msg": "authentication", "msg_data": {}})


async def test_message_authentication(fake_driver) -> None:
    """auth_required event -> `auth` request with the token -> `authentication` response (code 200)."""

    async def driver(ws: web.WebSocketResponse, received: list[dict[str, Any]]) -> None:
        await ws.send_json({"kind": "event", "msg": "auth_required",
                            "msg_data": {"name": "fake", "version": {"api": "0.16.0", "driver": "1.0.0"}}})
        req = await _recv(ws, received)
        assert req is not None
        code = 200 if req["msg_data"]["token"] == "s3cret" else 401
        await ws.send_json({"kind": "resp", "req_id": req["id"], "code": code, "msg": "authentication",
                            "msg_data": {}})
        await _recv(ws, received)

    url, received = await fake_driver(driver)
    async with UcRemoteSim(url, token="s3cret") as remote:
        assert remote.authentication is not None and remote.authentication["code"] == 200
    assert received[0] == {"kind": "req", "id": 1, "msg": "auth", "msg_data": {"token": "s3cret"}}


async def test_message_authentication_rejected(fake_driver) -> None:
    async def driver(ws: web.WebSocketResponse, received: list[dict[str, Any]]) -> None:
        await ws.send_json({"kind": "event", "msg": "auth_required", "msg_data": {}})
        req = await _recv(ws, received)
        assert req is not None
        await ws.send_json({"kind": "resp", "req_id": req["id"], "code": 401, "msg": "authentication",
                            "msg_data": {}})
        await ws.close()

    url, _ = await fake_driver(driver)
    remote = UcRemoteSim(url, token="wrong")
    with pytest.raises(RemoteSimError, match="authentication failed"):
        await remote.connect()
    await remote.close()


async def test_header_authentication(fake_driver) -> None:
    async def driver(ws: web.WebSocketResponse, received: list[dict[str, Any]]) -> None:
        await _no_auth(ws)
        await _recv(ws, received)

    url, _ = await fake_driver(driver, token_header="t0ken")
    async with UcRemoteSim(url, token="t0ken", header_auth=True) as remote:
        assert remote.authentication is not None
    with pytest.raises(Exception):  # noqa: B017 - aiohttp's handshake error type varies by version
        await UcRemoteSim(url, token="nope", header_auth=True).connect()


async def test_request_shapes_follow_the_spec(fake_driver) -> None:
    async def driver(ws: web.WebSocketResponse, received: list[dict[str, Any]]) -> None:
        await _no_auth(ws)
        while True:
            req = await _recv(ws, received)
            if req is None:
                return
            if req["kind"] == "req":
                await ws.send_json({"kind": "resp", "req_id": req["id"], "code": 200, "msg": "result",
                                    "msg_data": {}})

    url, received = await fake_driver(driver)
    async with UcRemoteSim(url) as remote:
        await remote.send_connect()
        await remote.subscribe_events(["remote.input_1_cec"])
        await remote.remote_send_cmd("remote.input_1_cec", "VOLUME_UP", repeat=3, delay=100, hold=0)
        await remote.remote_send_cmd_sequence("remote.input_1_cec", ["UP", "SELECT"], delay=200)
        await remote.select_source("media_player.output_1", "PS5")
        await remote.button_push("button.preset_1")
        await remote.enter_standby()
    assert received[0] == {"kind": "event", "msg": "connect", "cat": "DEVICE"}
    assert received[1] == {"kind": "req", "id": 1, "msg": "subscribe_events",
                           "msg_data": {"entity_ids": ["remote.input_1_cec"]}}
    assert received[2]["msg_data"] == {"entity_type": "remote", "entity_id": "remote.input_1_cec", "cmd_id": "send_cmd",
                                       "params": {"command": "VOLUME_UP", "repeat": 3, "delay": 100, "hold": 0}}
    assert received[3]["msg_data"]["params"] == {"sequence": ["UP", "SELECT"], "delay": 200}
    assert received[4]["msg_data"] == {"entity_type": "media_player", "entity_id": "media_player.output_1",
                                       "cmd_id": "select_source", "params": {"source": "PS5"}}
    assert received[5]["msg_data"] == {"entity_type": "button", "entity_id": "button.preset_1", "cmd_id": "push"}
    assert received[6] == {"kind": "event", "msg": "enter_standby", "cat": "REMOTE"}
    assert [m["id"] for m in received if m["kind"] == "req"] == [1, 2, 3, 4, 5]


async def test_close_code_is_reported(fake_driver) -> None:
    async def driver(ws: web.WebSocketResponse, received: list[dict[str, Any]]) -> None:
        await _no_auth(ws)
        await _recv(ws, received)
        await ws.close(code=WSCloseCode.INTERNAL_ERROR)

    url, _ = await fake_driver(driver)
    remote = UcRemoteSim(url)
    await remote.connect()
    with pytest.raises(ConnectionClosedError) as exc:
        await remote.remote_on("remote.output_1_cec")
    assert exc.value.code == 1011
    assert remote.closed and remote.close_code == 1011
    with pytest.raises(ConnectionClosedError):
        await remote.get_driver_version()
    await remote.close()


async def test_setup_flow_collects_setup_events(fake_driver) -> None:
    async def driver(ws: web.WebSocketResponse, received: list[dict[str, Any]]) -> None:
        await _no_auth(ws)
        req = await _recv(ws, received)
        assert req is not None
        await ws.send_json({"kind": "resp", "req_id": req["id"], "code": 200, "msg": "result", "msg_data": {}})
        await ws.send_json({"kind": "event", "msg": "driver_setup_change", "cat": "DEVICE",
                            "msg_data": {"event_type": "SETUP", "state": "SETUP"}})
        await asyncio.sleep(0.1)
        await ws.send_json({"kind": "event", "msg": "driver_setup_change", "cat": "DEVICE",
                            "msg_data": {"event_type": "STOP", "state": "OK"}})
        await _recv(ws, received)

    url, received = await fake_driver(driver)
    async with UcRemoteSim(url) as remote:
        outcome = await remote.setup_driver({"host": "10.0.0.5"}, reconfigure=True, language="de")
    assert received[0]["msg_data"] == {"setup_data": {"host": "10.0.0.5"}, "reconfigure": True, "language": "de"}
    assert outcome.state == "OK"
    assert [e["state"] for e in outcome.events] == ["SETUP", "OK"]
