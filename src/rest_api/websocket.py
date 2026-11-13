"""
The /ws endpoint: live events for the web UI, the kiosk and any other client.

The message contract (every event, its payload and when it is sent) is
docs/api/WEBSOCKET.md, with the JSON schema docs/api/websocket.schema.json.
The events come from the hub's event stream (rest_api/events.py): its status
poller and the matrix's own change notifications, whatever made the change.
"""

import json
import logging
import os
from collections.abc import AsyncIterator
from typing import Any

from aiohttp import WSMsgType, web

from .events import EventStream, get_event_stream
from .security import allowed_origin, manager
from .utils import _ws_clients_lock, get_ws_clients
from .ws_request_work import RejectReason, WorkOwner, WsRequestWork

_LOG = logging.getLogger("rest_api.websocket")

#: Protocol-level ping every N seconds; a client that does not answer within half of it is closed (API-10).
#: Browsers answer ping frames by themselves.
HEARTBEAT_SECONDS = 30.0

#: ``get_status`` reads in flight across all /ws clients (CR-01). Each client has at most one of
#: its own, so a client that floods ``get_status`` frames cannot start one task per frame.
MAX_STATUS_READS = 8

#: The app's bounded ``get_status`` work. It belongs to the app, never to the module, so every
#: app drains its own tasks when it stops.
WS_REQUEST_WORK = web.AppKey("ws_request_work", WsRequestWork)


def install_ws_request_work(app: web.Application) -> None:
    """Give ``app`` its bounded ``get_status`` work and drain it when the app stops.

    Install it after the event stream: cleanup contexts exit in reverse order,
    so the reads are cancelled and awaited before the stream they answer on stops.
    """

    async def _ctx(app: web.Application) -> AsyncIterator[None]:
        work = WsRequestWork(application_limit=MAX_STATUS_READS, name="ws_get_status")
        app[WS_REQUEST_WORK] = work
        yield
        await work.shutdown()

    app.cleanup_ctx.append(_ctx)


def _event_stream(app: web.Application) -> EventStream:
    """The app's own stream; the process-wide one only for an app built without it."""
    stream = app.get("event_stream")
    return stream if stream is not None else get_event_stream()


async def broadcast_status_update(event_type: str, data: dict[str, Any]) -> None:
    """Send ``event_type`` to every /ws client.

    Returns at once: each client has its own queue, so a slow client never
    holds up the caller (API-09). Kept as a coroutine for existing callers.

    :param event_type: an event of the contract (docs/api/WEBSOCKET.md)
    :param data: its payload
    """
    get_event_stream().publish(event_type, data)


def get_connected_client_count() -> int:
    """Number of connected WebSocket clients."""
    return get_event_stream().client_count


async def handle_websocket(request: web.Request) -> web.WebSocketResponse:
    """
    WebSocket endpoint for live updates (docs/api/WEBSOCKET.md).

    Server -> client: ``connected`` first (protocol version and the matrix
    link), then a ``status`` snapshot as soon as the hub has read the matrix,
    then change events (``routing_change``, ``signal_change``, ...).

    Client -> server: ``{"command": "ping"}`` -> ``pong``;
    ``{"command": "get_status"}`` -> ``status`` after a fresh read of the
    matrix (or ``error`` when the hub cannot read it). ``{"type": "ping"}``,
    the form older web clients send, is answered too.
    """
    origin = request.headers.get("Origin")
    if origin and not allowed_origin(request, origin):
        raise web.HTTPForbidden(text="WebSocket Origin denied")
    stream = _event_stream(request.app)
    work = request.app[WS_REQUEST_WORK]
    ws_clients = get_ws_clients()
    ws = web.WebSocketResponse(heartbeat=HEARTBEAT_SECONDS)
    ws["access_level"] = manager(request).access_level(request)
    async with _ws_clients_lock:
        if len(ws_clients) >= int(os.environ.get("MAX_WS_CLIENTS", "32")):
            raise web.HTTPServiceUnavailable(text="WebSocket client limit reached")
        await ws.prepare(request)
        ws_clients.add(ws)
    stream.add_client(ws)
    _LOG.info(f"WebSocket client connected (total: {stream.client_count})")
    # One owner per connection: its get_status read ends with the socket.
    owner = work.open_owner()

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                _handle_command(stream, owner, ws, msg.data)
            elif msg.type == WSMsgType.ERROR:
                _LOG.warning(f"WebSocket error: {ws.exception()}")
    except Exception as e:
        _LOG.debug(f"WebSocket connection error: {e}")
    finally:
        try:
            # Cancel and await this socket's read before its client entry goes.
            await owner.aclose()
        finally:
            async with _ws_clients_lock:
                ws_clients.discard(ws)
            await stream.remove_client(ws)
        _LOG.info(f"WebSocket client disconnected (remaining: {stream.client_count})")

    return ws


def _handle_command(stream: Any, owner: WorkOwner, ws: web.WebSocketResponse, text: str) -> None:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        stream.send(ws, "error", {"message": "Invalid JSON"})
        return
    if not isinstance(data, dict):
        stream.send(ws, "error", {"message": "Expected a JSON object"})
        return
    command = data.get("command", data.get("type"))
    if command == "ping":
        stream.send(ws, "pong", {})
    elif command == "get_status":
        started = owner.try_start(lambda: _reply_status(stream, ws))
        if started is RejectReason.APPLICATION_BUSY:
            stream.send(ws, "error", {"message": "Server busy; send get_status again"})
        # OWNER_BUSY: this client's read is in flight, and its ``status`` answers this frame too
        # (a change after that read still arrives as a change event). OWNER_CLOSED and
        # SHUTTING_DOWN: the socket is going away, so there is nobody to answer.
    else:
        stream.send(ws, "error", {"message": f"Unknown command: {command}"})


async def _reply_status(stream: Any, ws: web.WebSocketResponse) -> None:
    """``get_status``: read the matrix now (changes found are announced to every client first), then answer."""
    try:
        snapshot = await stream.refresh()
    except Exception as e:  # noqa: BLE001 - the client gets an error, the hub keeps running
        _LOG.warning(f"get_status: reading the matrix failed: {e}")
        snapshot = None
    if snapshot is None:
        stream.send(ws, "error", {"message": "Matrix status not available"})
    else:
        stream.send(ws, "status", snapshot)
