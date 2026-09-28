"""Custom preset save (``POST /api/preset/{n}/save {routing}``) on the real hub app, a real OreiMatrix and the simulator.

The matrix can only save its live routing, so a custom save routes the
displays, saves and routes them back (whether that can be avoided is DI-4).
API-14: one save at a time, the routing to restore read fresh from the
matrix, and nothing touched when it cannot be read.
"""

from __future__ import annotations

import asyncio

from .conftest import sim_writes


async def test_custom_preset_save_restores_the_live_routing(data_hub, simulator):
    simulator.state.outputs[0].source = 3
    simulator.state.outputs[1].source = 4
    resp = await data_hub.post("/api/preset/6/save", json={"routing": {"1": 8, "2": 7}})
    assert resp.status == 200, await resp.text()
    assert simulator.state.presets[5].routing[:2] == [8, 7]
    assert [o.source for o in simulator.state.outputs[:2]] == [3, 4]


async def test_custom_preset_save_restores_from_fresh_routing(data_hub, simulator):
    """API-14: the routing to restore came from the hub's status cache, which can be stale."""
    await data_hub.get("/api/status")  # warms the hub's status cache: output 1 = input 2
    simulator.state.outputs[0].source = 5  # changed on the front panel; no write through the hub
    resp = await data_hub.post("/api/preset/6/save", json={"routing": {"1": 8}})
    assert resp.status == 200, await resp.text()
    assert simulator.state.presets[5].routing[0] == 8
    assert simulator.state.outputs[0].source == 5  # not the stale 2


async def test_custom_preset_saves_do_not_interleave(data_hub, simulator):
    """API-14: two concurrent custom saves interleaved their temporary routing and restores."""
    simulator.state.outputs[0].source = 3
    r1, r2 = await asyncio.gather(
        data_hub.post("/api/preset/6/save", json={"routing": {"1": 8}}),
        data_hub.post("/api/preset/7/save", json={"routing": {"1": 7}}),
    )
    assert (r1.status, r2.status) == (200, 200)
    assert simulator.state.presets[5].routing[0] == 8
    assert simulator.state.presets[6].routing[0] == 7
    assert simulator.state.outputs[0].source == 3
    # each save ran as one block (route, save, route back), never another save's routing in between
    seq = [e["command"] for e in sim_writes(simulator)]
    assert seq == ["video switch", "preset save", "video switch"] * 2


async def test_custom_preset_save_is_refused_when_the_routing_cannot_be_read(data_hub, simulator, monkeypatch):
    """API-14: without a readable routing there is nothing to restore -> refuse before touching the displays."""
    from rest_api.utils import get_matrix_device

    matrix = get_matrix_device()

    async def no_routing(force_refresh=False):
        return {"connected": True}

    monkeypatch.setattr(matrix, "get_status", no_routing)
    resp = await data_hub.post("/api/preset/6/save", json={"routing": {"1": 8}})
    assert resp.status >= 500
    assert sim_writes(simulator) == []


async def test_custom_preset_is_not_saved_when_the_temporary_routing_fails(data_hub, simulator, monkeypatch):
    """Saving after a refused switch would store the wrong routing in the preset."""
    from rest_api.utils import get_matrix_device

    matrix = get_matrix_device()
    real = matrix.switch_input
    calls = []

    async def refuse_first(input_num, output_num):
        calls.append((input_num, output_num))
        return False if len(calls) == 1 else await real(input_num, output_num)

    monkeypatch.setattr(matrix, "switch_input", refuse_first)
    before = list(simulator.state.presets[5].routing)
    resp = await data_hub.post("/api/preset/6/save", json={"routing": {"1": 8}})
    assert resp.status == 500
    assert simulator.state.presets[5].routing == before
    assert not sim_writes(simulator, "preset save")
    assert simulator.state.outputs[0].source == 2  # routed back (seed routing)


async def test_custom_preset_save_validates_before_touching_the_matrix(data_hub, simulator):
    resp = await data_hub.post("/api/preset/6/save", json={"routing": {"1": 9}})
    assert resp.status == 400
    assert sim_writes(simulator) == []
