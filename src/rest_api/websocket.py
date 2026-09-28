"""
The /ws endpoint: live events for the web UI, the kiosk and any other client.

The message contract (every event, its payload and when it is sent) is
docs/api/WEBSOCKET.md, with the JSON schema docs/api/websocket.schema.json.
The events come from the hub's event stream (rest_api/events.py): its status
poller and the matrix's own change notifications, whatever made the change.
"""

import asyncio
import json
import logging
from typing import Any

from aiohttp import WSMsgType, web

from .events import get_event_stream
from .utils import get_ws_clients

_LOG = logging.getLogger("rest_api.websocket")

#: Protocol-level ping every N seconds; a client that does not answer within half of it is closed (API-10).
#: Browsers answer ping frames by themselves.
HEARTBEAT_SECONDS = 30.0

#: get_status replies in flight (a reference keeps each task alive until it has answered).
_replies: set[asyncio.Task[None]] = set()


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
    ws = web.WebSocketResponse(heartbeat=HEARTBEAT_SECONDS)
    await ws.prepare(request)

    stream = get_event_stream()
    ws_clients = get_ws_clients()
    ws_clients.add(ws)
    stream.add_client(ws)
    _LOG.info(f"WebSocket client connected (total: {stream.client_count})")

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                _handle_command(stream, ws, msg.data)
            elif msg.type == WSMsgType.ERROR:
                _LOG.warning(f"WebSocket error: {ws.exception()}")
    except Exception as e:
        _LOG.debug(f"WebSocket connection error: {e}")
    finally:
        ws_clients.discard(ws)
        await stream.remove_client(ws)
        _LOG.info(f"WebSocket client disconnected (remaining: {stream.client_count})")

    return ws


def _handle_command(stream: Any, ws: web.WebSocketResponse, text: str) -> None:
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
        task = asyncio.get_running_loop().create_task(_reply_status(stream, ws), name="ws_get_status")
        _replies.add(task)
        task.add_done_callback(_replies.discard)
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
