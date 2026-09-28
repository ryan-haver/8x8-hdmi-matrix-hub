"""BE-31: a warm-cache status read never resets the output names in open clients.

A ``GET /api/status/outputs`` served from a warm cache schedules a background
refresh (``rest_api/core.py`` ``background_status_refresh``). It used to
broadcast a full ``status`` whose ``outputs_detail`` took the names from the
hub's name cache, empty in modular mode (``run.py``), so every open web UI saw
its outputs renamed "Output 1", "Output 2", ... Since WP-C2 the refresh only
refreshes the caches and the event stream announces what changed; the
snapshot's names are covered by ``test_sim_ws_contract.py``. This test pins the
refresh side: after the connect snapshot, repeated warm-cache reads send no
further ``status`` and nothing on /ws names an output "Output N". Real hub
app, real ``OreiMatrix``, simulator (seed names: TV, Soundbar).
"""

from __future__ import annotations

import asyncio
import json

import pytest

pytestmark = pytest.mark.asyncio


async def _collect(ws, seconds: float) -> list[dict]:
    """Every JSON message received within ``seconds``."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + seconds
    out: list[dict] = []
    while (left := deadline - loop.time()) > 0:
        try:
            msg = await asyncio.wait_for(ws.receive(), timeout=left)
        except TimeoutError:
            break
        if msg.type.name == "TEXT":
            out.append(json.loads(msg.data))
    return out


def _output_names(messages: list[dict]) -> list[str]:
    names: list[str] = []
    for m in messages:
        data = m.get("data") or {}
        names += [o.get("name", "") for o in data.get("outputs_detail") or []]
        names += list((data.get("output_names") or {}).values())
    return names


async def test_warm_cache_reads_do_not_rebroadcast_or_reset_output_names(data_hub):
    ws = await data_hub.ws_connect("/ws")
    try:
        first = await _collect(ws, 2.0)  # welcome + connect snapshot
        snapshot = [m for m in first if m.get("event") == "status"]
        assert snapshot, [m.get("event") for m in first]
        assert [o["name"] for o in snapshot[0]["data"]["outputs_detail"][:2]] == ["TV", "Soundbar"]

        for _ in range(3):  # the first read warms the cache; the others schedule background refreshes
            resp = await data_hub.get("/api/status/outputs")
            assert resp.status == 200
            assert [o["name"] for o in (await resp.json())["data"]["outputs"][:2]] == ["TV", "Soundbar"]
        later = await _collect(ws, 2.0)

        assert [m for m in later if m.get("event") == "status"] == []
        assert not [n for n in _output_names(later) if n.startswith("Output ") and n in ("Output 1", "Output 2")]
    finally:
        await ws.close()
