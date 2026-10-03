"""Single-port CEC edits preserve current device flags, including concurrent edits."""

import asyncio
from copy import deepcopy
from unittest.mock import AsyncMock

import pytest

from .conftest import sim_commands


@pytest.mark.parametrize("kind", ("input", "output"))
@pytest.mark.parametrize("enabled", (False, True))
async def test_port_edit_preserves_external_changes_with_a_warm_cache(data_hub, matrix, simulator, kind, enabled):
    assert await matrix.refresh_cec_status()
    # Another controller changes both arrays while the five-minute cache is valid.
    for ports in (simulator.state.inputs, simulator.state.outputs):
        for port in ports:
            port.cec_enabled = 1 - port.cec_enabled
    target = getattr(simulator.state, f"{kind}s")[7]
    target.cec_enabled = int(not enabled)
    before = deepcopy(simulator.state.to_dict())
    simulator.log.clear()
    response = await data_hub.post(f"/api/cec/{kind}/8/enable", json={"enabled": enabled})
    assert response.status == 200
    assert (await response.json())["success"] is True
    before[f"{kind}s"][7]["cec_enabled"] = int(enabled)
    assert simulator.state.to_dict() == before
    assert len(sim_commands(simulator, "set cec index")) == 1
    commands = [e["command"] for e in simulator.log if e.get("channel") == "http"]
    assert commands.index("get cec status") < commands.index("set cec index")


async def test_concurrent_port_edits_preserve_both_changes(matrix, simulator):
    assert await matrix.connect()
    assert await matrix.refresh_cec_status()
    before = deepcopy(simulator.state.to_dict())
    assert before["inputs"][0]["cec_enabled"] == before["outputs"][7]["cec_enabled"] == 0
    results = await asyncio.gather(matrix.set_cec_enabled(1, True), matrix.set_cec_enabled(8, True, True))
    assert results == [True, True]
    before["inputs"][0]["cec_enabled"] = before["outputs"][7]["cec_enabled"] = 1
    assert simulator.state.to_dict() == before


async def test_failed_snapshot_does_not_write_cached_flags(matrix, simulator):
    assert await matrix.connect()
    assert await matrix.refresh_cec_status()
    before = deepcopy(simulator.state.to_dict())
    simulator.log.clear()
    simulator.faults.update({"http_status": 503, "comheads": ["get cec status"]})
    assert await matrix.set_cec_enabled(8, True, True) is False
    assert not sim_commands(simulator, "set cec index")
    assert simulator.state.to_dict() == before


@pytest.mark.parametrize("snapshot", ({}, [1], {"inputindex": [0] * 8, "outputindex": [1]},
    {"inputindex": [0] * 8, "outputindex": [0] * 7 + [2]}))
async def test_incomplete_snapshot_does_not_write_cached_flags(matrix, simulator, monkeypatch, snapshot):
    assert await matrix.connect()
    assert await matrix.refresh_cec_status()
    simulator.log.clear()
    monkeypatch.setattr(matrix, "get_cec_status", AsyncMock(return_value=snapshot))
    assert await matrix.set_cec_enabled(8, True, True) is False
    assert not sim_commands(simulator, "set cec index")
