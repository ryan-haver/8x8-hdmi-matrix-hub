"""
WebSocket support for real-time status updates.
"""

import json
import logging
from typing import Any

from aiohttp import web, WSMsgType

from .utils import get_ws_clients, get_matrix_device

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
    
    message = json.dumps({
        "event": event_type,
        "data": data
    })
    
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
    
    # Add to connected clients
    ws_clients.add(ws)
    client_count = len(ws_clients)
    _LOG.info(f"WebSocket client connected (total: {client_count})")
    
    # Send welcome message
    try:
        await ws.send_json({
            "event": "connected",
            "data": {
                "message": "Connected to OREI Matrix WebSocket",
                "client_count": client_count
            }
        })
    except Exception as e:
        _LOG.warning(f"Error sending welcome message: {e}")
    
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
        # Remove from connected clients
        ws_clients.discard(ws)
        _LOG.info(f"WebSocket client disconnected (remaining: {len(ws_clients)})")
    
    return ws
