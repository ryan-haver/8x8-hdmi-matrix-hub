"""``/ws`` ``get_status`` is bounded and drained (CR-01), over real WebSocket connections.

Every ``{"command": "get_status"}`` frame used to start one task, kept in a
module-global set: a client could start as many matrix reads as it sent
frames, and nothing cancelled them when its socket closed or the app stopped.

These tests run the real app (``create_rest_app``) with the real handler and
replace only ``EventStream.refresh``, the matrix read, by one that waits for
the test. Evidence is what the server did: how often ``refresh`` was entered,
which reads were cancelled, which messages a client received. Waits are on
events, never on a delay; ``pong`` is used as a barrier, because the server
handles the frames of one socket in order.
"""

from __future__ import annotations

import asyncio

import pytest

from rest_api import websocket
from rest_api.app import create_rest_app
from rest_api.websocket import WS_REQUEST_WORK

SNAPSHOT = {"connected": True, "routing": {"1": 2}}


class GatedRefresh:
    """Stands in for ``EventStream.refresh``: every read waits until the test releases it."""

    def __init__(self) -> None:
        self.entered = 0
        self.cancelled = 0
        self.finished = 0
        self.started = asyncio.Event()
        self.release = asyncio.Event()
        self.all_cancelled = asyncio.Event()

    async def __call__(self) -> dict:
        self.entered += 1
        self.started.set()
        try:
            await self.release.wait()
        except asyncio.CancelledError:
            self.cancelled += 1
            if self.cancelled == self.entered:
                self.all_cancelled.set()
            raise
        self.finished += 1
        return SNAPSHOT


@pytest.fixture
def app(tmp_path, monkeypatch):
    for name in ("ADMIN_PIN", "CONTROL_PIN", "ADMIN_PIN_RESET", "CORS_ALLOWED_ORIGINS", "MAX_WS_CLIENTS"):
        monkeypatch.delenv(name, raising=False)
    return create_rest_app(tmp_path)


@pytest.fixture
async def client(aiohttp_client, app):
    return await aiohttp_client(app)


@pytest.fixture
def refresh(app, client) -> GatedRefresh:
    """The gate, installed on the started app's own event stream."""
    gate = GatedRefresh()
    app["event_stream"].refresh = gate
    return gate


async def connect(client):
    """A connected socket, past its ``connected`` greeting."""
    ws = await client.ws_connect("/ws")
    assert (await ws.receive_json(timeout=5))["event"] == "connected"
    return ws


async def barrier(ws) -> list[dict]:
    """Messages received until the ``pong`` that shows the server handled every earlier frame."""
    await ws.send_json({"command": "ping"})
    seen = []
    while True:
        msg = await ws.receive_json(timeout=5)
        if msg["event"] == "pong":
            return seen
        seen.append(msg)


async def test_a_burst_of_get_status_frames_starts_one_read(client, app, refresh):
    # Arrange
    ws = await connect(client)

    # Act: 25 frames while the first read has not answered
    for _ in range(25):
        await ws.send_json({"command": "get_status"})
    await asyncio.wait_for(refresh.started.wait(), 5)
    during = await barrier(ws)

    # Assert: one read, one task, nothing answered yet and no error for the coalesced frames
    assert refresh.entered == 1
    assert app[WS_REQUEST_WORK].active_count == 1
    assert len([t for t in asyncio.all_tasks() if t.get_name() == "ws_get_status"]) == 1
    assert during == []

    # Act: the read ends
    refresh.release.set()
    answer = await ws.receive_json(timeout=5)

    # Assert: one status for the burst, and the slot is free again
    assert answer == {"event": "status", "data": SNAPSHOT}
    assert await barrier(ws) == []
    assert app[WS_REQUEST_WORK].active_count == 0
    await ws.send_json({"command": "get_status"})
    assert (await ws.receive_json(timeout=5))["event"] == "status"
    assert refresh.entered == 2
    await ws.close()


async def test_closing_the_socket_cancels_its_read(client, app, refresh):
    # Arrange: a read in flight for this socket
    ws = await connect(client)
    await ws.send_json({"command": "get_status"})
    await asyncio.wait_for(refresh.started.wait(), 5)

    # Act
    await ws.close()

    # Assert: the read was cancelled, not left running against a closed socket
    await asyncio.wait_for(refresh.all_cancelled.wait(), 5)
    assert (refresh.entered, refresh.cancelled, refresh.finished) == (1, 1, 0)
    assert app[WS_REQUEST_WORK].active_count == 0
    assert not [t for t in asyncio.all_tasks() if t.get_name() == "ws_get_status" and not t.done()]


async def test_another_client_is_served_while_one_read_is_pending(client, app, refresh):
    # Arrange: client A waits for its read
    ws_a = await connect(client)
    await ws_a.send_json({"command": "get_status"})
    await asyncio.wait_for(refresh.started.wait(), 5)

    # Act: client B pings and asks for its own status
    ws_b = await connect(client)
    assert await barrier(ws_b) == []
    await ws_b.send_json({"command": "get_status"})
    assert await barrier(ws_b) == []

    # Assert: B has its own read; A's flood protection does not block B
    assert refresh.entered == 2
    assert app[WS_REQUEST_WORK].active_count == 2
    refresh.release.set()
    assert (await ws_a.receive_json(timeout=5))["event"] == "status"
    assert (await ws_b.receive_json(timeout=5))["event"] == "status"
    await ws_a.close()
    await ws_b.close()


async def test_reads_beyond_the_application_limit_are_refused_with_an_error(aiohttp_client, tmp_path, monkeypatch):
    # Arrange: an app that allows two reads at a time, both taken
    monkeypatch.setattr(websocket, "MAX_STATUS_READS", 2)
    app = create_rest_app(tmp_path)
    client = await aiohttp_client(app)
    gate = GatedRefresh()
    app["event_stream"].refresh = gate
    sockets = [await connect(client) for _ in range(3)]
    for ws in sockets[:2]:
        await ws.send_json({"command": "get_status"})
        assert await barrier(ws) == []
    assert gate.entered == 2

    # Act: a third client asks
    await sockets[2].send_json({"command": "get_status"})
    refused = await barrier(sockets[2])

    # Assert: no third read; the client is told to ask again (the contract's ``error`` event)
    assert gate.entered == 2
    assert refused == [{"event": "error", "data": {"message": "Server busy; send get_status again"}}]
    gate.release.set()
    for ws in sockets[:2]:
        assert (await ws.receive_json(timeout=5))["event"] == "status"
    for ws in sockets:
        await ws.close()


async def test_stopping_the_app_cancels_pending_reads(client, app, refresh):
    # Arrange: two sockets, each with a read in flight
    sockets = [await connect(client) for _ in range(2)]
    for ws in sockets:
        await ws.send_json({"command": "get_status"})
        assert await barrier(ws) == []
    assert refresh.entered == 2
    work = app[WS_REQUEST_WORK]

    # Act: the app stops (the test client closes its server, which runs the app's cleanup)
    await client.close()

    # Assert: every read was cancelled and awaited; nothing is admitted any more
    assert (refresh.cancelled, refresh.finished) == (2, 0)
    assert work.closing and work.active_count == 0
    assert not [t for t in asyncio.all_tasks() if t.get_name() == "ws_get_status" and not t.done()]


async def test_rest_api_server_stop_drains_reads_before_the_stream_stops(tmp_path, unused_tcp_port):
    """``RestApiServer.stop`` stops the stream itself: the reads must be drained first."""
    import aiohttp

    from rest_api.app import RestApiServer

    # Arrange: the real server, one socket with a read in flight
    server = RestApiServer("127.0.0.1", unused_tcp_port, data_dir=tmp_path)
    await server.start()
    try:
        gate = GatedRefresh()
        stream = server.app["event_stream"]
        stream.refresh = gate
        order: list[str] = []
        stop = stream.stop

        async def recording_stop():
            order.append(f"stream.stop with {gate.entered - gate.cancelled} read(s) pending")
            await stop()

        stream.stop = recording_stop
        async with aiohttp.ClientSession() as session:
            ws = await session.ws_connect(f"http://127.0.0.1:{unused_tcp_port}/ws")
            assert (await ws.receive_json(timeout=5))["event"] == "connected"
            await ws.send_json({"command": "get_status"})
            await asyncio.wait_for(gate.started.wait(), 5)

            # Act
            await server.stop()

            # Assert
            assert order[0] == "stream.stop with 0 read(s) pending"
            assert (gate.entered, gate.cancelled, gate.finished) == (1, 1, 0)
            await ws.close()
    finally:
        await server.stop()


async def test_each_app_serves_its_sockets_from_its_own_stream(aiohttp_client, tmp_path):
    """The handler took the process-wide stream, which is the stream of the app started last."""
    # Arrange: two apps in one process, B started after A
    app_a = create_rest_app(tmp_path / "a")
    client_a = await aiohttp_client(app_a)
    app_b = create_rest_app(tmp_path / "b")
    await aiohttp_client(app_b)

    # Act: a socket connects to A
    ws = await connect(client_a)

    # Assert: it is A's client, with A's work, and B has none
    assert app_a["event_stream"].client_count == 1
    assert app_b["event_stream"].client_count == 0
    assert app_a[WS_REQUEST_WORK] is not app_b[WS_REQUEST_WORK]
    gate = GatedRefresh()
    app_a["event_stream"].refresh = gate
    await ws.send_json({"command": "get_status"})
    await asyncio.wait_for(gate.started.wait(), 5)
    assert (app_a[WS_REQUEST_WORK].active_count, app_b[WS_REQUEST_WORK].active_count) == (1, 0)
    await ws.close()
