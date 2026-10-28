"""R1F: explicit status synchronization expires warm CEC enable decisions.

Real runtime, HTTP/Telnet simulator and runner reset/WS synchronization; no
transport replacements, synthetic events, retries or cache-clock changes.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import hub.core.matrix_service as service_module
import hub.runtime.adapters as adapters
import hub.runtime.composition as composition
import orei_matrix
import run
from rest_api.app import create_rest_app
from tools.simulator import DeviceState, Simulator
from tools.validate.device import SimDevice
from tools.validate.runner import WsObserver


@pytest.fixture
async def cec_stack(tmp_path, monkeypatch, aiohttp_client):
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
        "OREI_CEC_CACHE_TTL": "300",
        "OREI_USE_TELNET_CEC": "false",
    }
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("MATRIX_DATA_DIR", env["DATA_DIR"])
    monkeypatch.delenv("OREI_USER", raising=False)
    monkeypatch.delenv("OREI_PASSWORD", raising=False)

    def factory(host, **_kwargs):
        return orei_matrix.OreiMatrix(host, port=sim.https_port, use_https=sim.tls)

    runtime = composition.build_runtime(run.load_settings(env), environ=env, matrix_factory=factory)
    client = await aiohttp_client(create_rest_app(runtime=runtime))
    try:
        assert await runtime.connect()
        assert runtime.service.client.telnet_connected
        assert runtime.service.client._cec_cache_ttl == 300
        async with SimDevice(sim.control_url) as device:
            yield SimpleNamespace(runtime=runtime, client=client, sim=sim, device=device)
    finally:
        await client.close()
        await runtime.stop()
        await sim.stop()


def test_module_origins_are_owned_checkout():
    root = Path(__file__).resolve().parents[1]
    for module in (orei_matrix, composition, adapters, service_module, run):
        assert Path(module.__file__).resolve().is_relative_to(root)


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
            assert await observer.sync(), "runner WS pre-sync must complete"
        finally:
            await observer.stop()
    entries = list(stack.sim.log)[cursor:]
    assert not [e for e in entries if e["command"] in {"get cec status", "set cec index", "cec command"}], (
        "explicit synchronization should expire CEC decisions without prefetching or changing flags"
    )


@pytest.mark.parametrize("surface", ["protocol", "facade", "ws"])
@pytest.mark.parametrize("kind,port", [("input", 1), ("output", 8)])
async def test_forced_sync_expires_cec_enable_after_real_reset(cec_stack, surface, kind, port):
    stack = cec_stack
    matrix = stack.runtime.service.client
    is_output = kind == "output"
    assert await matrix.set_cec_enabled(port, True, is_output)
    assert await matrix.is_cec_enabled(port, is_output) is True
    await stack.device.reset()
    before = await stack.device.state()
    assert before[f"{kind}s"][port - 1]["cec_enabled"] == 0
    assert await matrix.is_cec_enabled(port, is_output) is True
    await _force_status(stack, surface)
    cursor = len(stack.sim.log)
    response = await stack.client.post(f"/api/cec/{kind}/{port}/power_on")
    assert response.status == 200, await response.text()
    assert (await response.json())["success"] is True
    after = await stack.device.state()
    entries = [e for e in list(stack.sim.log)[cursor:] if e["channel"] == "http"]
    writes = [e["payload"] for e in entries if e["command"] in {"set cec index", "cec command"}]
    warnings = [w for e in entries for w in e.get("warnings", [])]
    print(json.dumps({"surface": surface, "kind": kind, "port": port, "http": response.status,
                      "commands": [e["command"] for e in entries], "writes": writes,
                      "warnings": warnings, "enabled": after[f"{kind}s"][port - 1]["cec_enabled"]}))
    inputs = [p["cec_enabled"] for p in before["inputs"]]
    outputs = [p["cec_enabled"] for p in before["outputs"]]
    (outputs if is_output else inputs)[port - 1] = 1
    assert writes == [
        {"comhead": "set cec index", "language": 0, "inputindex": inputs, "outputindex": outputs},
        {"comhead": "cec command", "language": 0, "object": int(is_output),
         "port": [int(i == port) for i in range(1, 9)], "index": 0 if is_output else 1},
    ]
    assert not warnings
    before[f"{kind}s"][port - 1]["cec_enabled"] = 1
    assert after == before


async def test_ordinary_snapshot_reads_and_refresh_preserve_cec_ttl(cec_stack):
    stack = cec_stack
    matrix = stack.runtime.service.client
    assert await matrix.refresh_cec_status()
    stamp = matrix._cec_enabled_cache["last_updated"]
    stack.sim.log.clear()
    await stack.runtime.refresh()
    await stack.runtime.matrix.get_status()
    await stack.runtime.matrix.get_input_status()
    await stack.runtime.matrix.get_output_status()
    assert await matrix.is_cec_enabled(2) is True
    assert await matrix.send_cec("POWER_ON", 2)
    assert await matrix.send_cec("POWER_ON", 2)
    assert matrix._cec_enabled_cache["last_updated"] == stamp
    assert not [e for e in stack.sim.log if e["command"] == "get cec status"]
    assert len([e for e in stack.sim.log if e["command"] == "cec command"]) == 2
    assert not [e for e in stack.sim.log if e["command"] == "set cec index"]
