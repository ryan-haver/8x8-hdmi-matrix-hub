"""BE-31: the background status refresh broadcasts the matrix's output names.

A ``GET /api/status/outputs`` served from a warm cache schedules a background
refresh (``rest_api/core.py`` ``background_status_refresh``) that broadcasts a
``status`` event to every WebSocket client. Its ``outputs_detail`` used to take
the names from the hub's name cache only, which is empty in modular mode
(``run.py``), so every open web UI saw its output names reset to "Output 1",
"Output 2", ... Real hub app, real ``OreiMatrix``, simulator (seed names: TV,
Soundbar).
"""

from __future__ import annotations

import asyncio
import json

import pytest

pytestmark = pytest.mark.asyncio


async def _next_status_event(ws, timeout: float = 10.0) -> dict:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while True:
        msg = await asyncio.wait_for(ws.receive(), timeout=max(0.1, deadline - loop.time()))
        if msg.type.name != "TEXT":
            continue
        body = json.loads(msg.data)
        if body.get("event") == "status":
            return body["data"]


async def test_background_refresh_keeps_the_matrix_output_names(data_hub):
    ws = await data_hub.ws_connect("/ws")
    try:
        # First read fills the matrix's output-status cache; the second is served
        # from it and schedules the background refresh + broadcast.
        assert (await data_hub.get("/api/status/outputs")).status == 200
        resp = await data_hub.get("/api/status/outputs")
        assert resp.status == 200
        rest_names = [o["name"] for o in (await resp.json())["data"]["outputs"]]
        assert rest_names[:2] == ["TV", "Soundbar"]

        data = await _next_status_event(ws)
        broadcast_names = [o["name"] for o in data["outputs_detail"]]
        assert broadcast_names == rest_names
        assert data["output_names"]["1"] == "TV"
    finally:
        await ws.close()
