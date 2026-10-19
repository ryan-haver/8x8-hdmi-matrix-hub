"""R1E: explicit status refresh expires preset slots across the shared runtime.

Real HTTP/Telnet simulator traffic, runner reset and WS sync, with only the
protocol cache clock controlled so crossing the 3-second TTL cannot mask a bug.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import orei_matrix
import run
from hub.runtime.composition import build_runtime
from orei_matrix import OreiMatrix
from rest_api.app import create_rest_app
from tools.simulator import DeviceState, Simulator
from tools.validate.device import SimDevice
from tools.validate.runner import WsObserver, compare_preset_catalog


@pytest.fixture
async def preset_stack(tmp_path, monkeypatch, aiohttp_client):
    import persistence
    import rest_api.utils as utils

    monkeypatch.setattr(utils, "_runtime", None)
    monkeypatch.setattr(persistence, "get_legacy_data_paths", lambda: [])
    sim = Simulator(DeviceState.default(), host="127.0.0.1", https_port=0, telnet_port=0, control_port=0)
    await sim.start()
    env = {
        "DATA_DIR": str(tmp_path / "data"),
        "UC_CONFIG_HOME": str(tmp_path / "config"),
        "MATRIX_HOST": "127.0.0.1",
        "MATRIX_PORT": str(sim.https_port),
        "OREI_TELNET_PORT": str(sim.telnet_port),
        "UC_ENABLED": "false",
        "FLIC_ENABLED": "false",
        "HA_DISCOVERY_ENABLED": "false",
        "OREI_STATUS_CACHE_TTL": "3",
        "OREI_USE_TELNET_CEC": "false",
    }
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("MATRIX_DATA_DIR", env["DATA_DIR"])
    monkeypatch.delenv("OREI_USER", raising=False)
    monkeypatch.delenv("OREI_PASSWORD", raising=False)
    clock = [1000.0]
    monkeypatch.setattr(orei_matrix, "time", SimpleNamespace(time=lambda: clock[0]))

    def factory(host, **_kwargs):
        return OreiMatrix(host, port=sim.https_port, use_https=sim.tls)

    runtime = build_runtime(run.load_settings(env), environ=env, matrix_factory=factory)
    client = await aiohttp_client(create_rest_app(runtime=runtime))
    try:
        assert await runtime.connect()
        assert runtime.service.client.telnet_connected
        assert runtime.service.client._status_cache_ttl == 3
        for module in (orei_matrix, run, __import__("hub.runtime.adapters", fromlist=["_"])):
            assert Path(module.__file__).resolve().is_relative_to(Path(__file__).resolve().parents[1])
        async with SimDevice(sim.control_url) as device:
            yield SimpleNamespace(runtime=runtime, client=client, sim=sim, device=device, clock=clock)
    finally:
        await client.close()
        await runtime.stop()
        await sim.stop()


async def _catalog(stack):
    response = await stack.client.get("/api/presets")
    assert response.status == 200, await response.text()
    payload = await response.json()
    assert payload["success"] is True
    return payload["data"]["presets"]


def _commands(stack):
    return [e["command"] for e in stack.sim.log if e["channel"] in {"http", "telnet"}]


def _preset_reads(stack):
    return [e["command"] for e in stack.sim.log if e["channel"] == "telnet" and e["command"].startswith("r preset ")]


async def _force_status(stack, surface):
    cursor = len(stack.sim.log)
    if surface == "protocol":
        await stack.runtime.service.client.get_status(force_refresh=True)
    elif surface == "facade":
        await stack.runtime.matrix.get_status(force_refresh=True)
    else:
        observer = WsObserver(str(stack.client.make_url("/ws")), "127.0.0.1")
        await observer.start()
        try:
            assert not observer.error
            cursor = len(stack.sim.log)
            assert await observer.sync(), "the runner's real /ws get_status precondition must complete"
        finally:
            await observer.stop()
    commands = list(stack.sim.log)[cursor:]
    assert [e["command"] for e in commands if e["command"] == "get video status"] == ["get video status"]
    assert not [e for e in commands if e["command"].startswith("r preset ")], "refresh must not prefetch slots"


@pytest.mark.parametrize("surface", ["protocol", "facade", "ws"])
@pytest.mark.parametrize("case", ["device_slot_8", "catalog_matches_device"])
async def test_forced_status_after_runner_reset_reads_device_slots(preset_stack, surface, case):
    stack = preset_stack
    if case == "device_slot_8":
        patch = {"presets": {"7": {"routing": list(range(1, 9)), "saved": True}}}
        await stack.device.reset(patch)
    else:
        patch = {"presets": {
            "0": {"routing": [2, 4, 4, 4, 4, 4, 4, 4], "saved": True},
            "3": {"routing": [8, 7, 6, 5, 4, 3, 2, 1], "saved": True},
            "7": {"routing": [1] * 8, "saved": False},
        }}
    warm = await _catalog(stack)
    assert _preset_reads(stack) == [f"r preset {n}" for n in range(1, 9)]
    await stack.device.reset(patch)
    before = await stack.device.state()
    await _force_status(stack, surface)
    cursor = len(stack.sim.log)
    catalog = await _catalog(stack)
    commands = list(stack.sim.log)[cursor:]
    reads = [e["command"] for e in commands if e["channel"] == "telnet"]
    disagreements = compare_preset_catalog(catalog, await stack.device.preset_slots())
    print(json.dumps({"case": case, "surface": surface, "cache_age": stack.clock[0] - stack.runtime.service.client._preset_cache_time,
                      "reads": reads, "disagreements": disagreements, "warm_equals_response": warm == catalog}))
    assert await stack.device.state() == before
    assert not [e for e in commands if e["channel"] in {"http", "telnet"} and not e["command"].startswith(("get ", "r "))]
    assert not disagreements
    assert reads == [f"r preset {n}" for n in range(1, 9)]


async def test_normal_reads_and_runtime_poll_preserve_cache_until_ttl(preset_stack):
    stack = preset_stack
    first = await _catalog(stack)
    stack.sim.log.clear()
    stack.sim.state.presets[0].routing = [8] * 8
    stack.sim.state.presets[0].saved = True
    await stack.runtime.refresh()
    assert await _catalog(stack) == first
    assert _preset_reads(stack) == []
    stack.clock[0] += 3
    fresh = await _catalog(stack)
    assert fresh[0]["routing"] == {str(o): 8 for o in range(1, 9)}
    assert _preset_reads(stack) == [f"r preset {n}" for n in range(1, 9)]


async def test_save_expires_cache_and_followup_catalog_remains_cached(preset_stack):
    stack = preset_stack
    await _catalog(stack)
    response = await stack.client.post("/api/preset/8/save", json={"routing": {"1": 8}})
    assert response.status == 200, await response.text()
    stack.sim.log.clear()
    before = await stack.device.state()
    catalog = await _catalog(stack)
    assert not compare_preset_catalog(catalog, await stack.device.preset_slots())
    assert _preset_reads(stack) == [f"r preset {n}" for n in range(1, 9)]
    stack.sim.log.clear()
    assert await _catalog(stack) == catalog
    assert _commands(stack) == []
    assert await stack.device.state() == before


async def test_concurrent_catalogs_share_one_slot_pass(preset_stack):
    stack = preset_stack
    stack.sim.log.clear()
    catalogs = await asyncio.gather(*(_catalog(stack) for _ in range(4)))
    assert all(catalog == catalogs[0] for catalog in catalogs)
    assert _preset_reads(stack) == [f"r preset {n}" for n in range(1, 9)]
