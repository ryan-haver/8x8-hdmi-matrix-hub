"""
WebSocket support for real-time status updates.
"""

import asyncio
import json
import logging
import time
from typing import Any

from aiohttp import WSMsgType, web

from .utils import get_matrix_device, get_ws_clients

_LOG = logging.getLogger("rest_api.websocket")


async def broadcast_status_update(event_type: str, data: dict[str, Any]):
    """
    Broadcast a status update to all connected WebSocket clients.

    :param event_type: Type of event (e.g., "routing_change", "connection_change", "signal_change")
    :param data: Event data to send
    """
    ws_clients = get_ws_clients()
    if not ws_clients:
        return

    message = json.dumps({"event": event_type, "data": data})

    # Copy the set to avoid iteration issues if clients are added/removed during broadcast
    clients_snapshot = set(ws_clients)

    # Send to all clients, removing disconnected ones
    disconnected = set()
    for ws in clients_snapshot:
        try:
            if not ws.closed:
                await ws.send_str(message)
            else:
                disconnected.add(ws)
        except Exception as e:
            _LOG.debug(f"Error sending to WebSocket client: {e}")
            disconnected.add(ws)

    # Clean up disconnected clients
    ws_clients.difference_update(disconnected)

    if disconnected:
        _LOG.debug(f"Removed {len(disconnected)} disconnected WebSocket client(s)")


def get_connected_client_count() -> int:
    """Get the number of connected WebSocket clients."""
    return len(get_ws_clients())


async def _heartbeat(ws, ws_clients, last_pong_time):
    """Heartbeat coroutine that pings the client every 30 seconds and checks for pong response."""
    import time
    try:
        while not ws.closed:
            await asyncio.sleep(30)
            if ws.closed:
                break
            # Check if client responded to last ping within 10 seconds
            if last_pong_time[0] > 0 and (time.monotonic() - last_pong_time[0]) > 10:
                _LOG.warning("Client pong timeout, closing connection")
                await ws.close()
                break
            try:
                await ws.send_str(json.dumps({"event": "ping"}))
            except Exception:
                break
    except asyncio.CancelledError:
        pass
    except Exception:
        pass


async def handle_websocket(request: web.Request) -> web.WebSocketResponse:
    """
    WebSocket endpoint for real-time status updates.

    Clients connect to /ws and receive JSON messages:
    - {"event": "connected", "data": {"message": "...", "client_count": N}}
    - {"event": "routing_change", "data": {"output": N, "input": M, "input_name": "..."}}
    - {"event": "connection_change", "data": {"output": N, "connected": bool, "has_signal": bool}}
    - {"event": "signal_change", "data": {"input": N, "has_signal": bool}}
    - {"event": "status_update", "data": {...full status...}}
    """
    ws_clients = get_ws_clients()
    matrix_device = get_matrix_device()

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Send welcome message FIRST, only add to set if successful
    try:
        await ws.send_json(
            {
                "event": "connected",
                "data": {"message": "Connected to OREI Matrix WebSocket", "client_count": len(ws_clients) + 1},
            }
        )
    except Exception as e:
        _LOG.warning(f"Failed to send welcome: {e}")
        return ws  # Don't add to set if welcome failed

    # Only add to set after successful welcome
    ws_clients.add(ws)
    client_count = len(ws_clients)
    _LOG.info(f"WebSocket client connected (total: {client_count})")

    # Track last pong time for timeout detection
    last_pong_time = [0.0]

    # Create heartbeat task after welcome message
    heartbeat_task = asyncio.create_task(_heartbeat(ws, ws_clients, last_pong_time))

    # Keep connection open and handle incoming messages
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                # Handle incoming commands (optional - clients can send commands via WebSocket)
                try:
                    data = json.loads(msg.data)
                    command = data.get("command")

                    if command == "ping":
                        await ws.send_json({"event": "pong", "data": {}})
                    elif command == "pong":
                        import time
                        last_pong_time[0] = time.monotonic()
                    elif command == "get_status":
                        if matrix_device and matrix_device.connected:
                            status = await matrix_device.get_status()
                            await ws.send_json({"event": "status_update", "data": status})
                        else:
                            await ws.send_json({"event": "error", "data": {"message": "Matrix not connected"}})
                    else:
                        await ws.send_json({"event": "error", "data": {"message": f"Unknown command: {command}"}})
                except json.JSONDecodeError:
                    await ws.send_json({"event": "error", "data": {"message": "Invalid JSON"}})
            elif msg.type == WSMsgType.ERROR:
                _LOG.warning(f"WebSocket error: {ws.exception()}")
    except Exception as e:
        _LOG.debug(f"WebSocket connection error: {e}")
    finally:
        # Cancel heartbeat task
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
        # Remove from connected clients
        ws_clients.discard(ws)
        _LOG.info(f"WebSocket client disconnected (remaining: {len(ws_clients)})")

    return ws
