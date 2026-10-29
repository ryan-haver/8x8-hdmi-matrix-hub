"""Real simulator/HTTP/WS observations and failure-sensitive refusal oracles."""

import asyncio
import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

import jsonschema
import pytest

from orei_matrix import OreiMatrix
from rest_api import create_rest_app, set_matrix_device
from tests.sim.conftest import make_simulator
from tests.validation.scenarios.sw_api_client_02_c1 import SCENARIOS
from tools.validate.clients.api import ApiClient
from tools.validate.clients.base import HubInfo
from tools.validate.device import SimDevice
from tools.validate.evidence import SCHEMA_PATH, iter_records
from tools.validate.model import DeviceUnchanged, NoCommand, NoWsEvent, Response, WsEvent, act
from tools.validate.runner import Runner, RunOptions, WsObserver, ws_contract_check
from tools.validate.stack import HubProcess, SimulatorProcess

SCENARIO = SCENARIOS[0]


@pytest.fixture
async def live(aiohttp_client, monkeypatch, tmp_path):
    """Local fixtures only: real matrix transport, hub, API and WS observer."""
    sim = make_simulator()
    await sim.start()
    monkeypatch.setenv("OREI_TELNET_PORT", str(sim.telnet_port))
    monkeypatch.setenv("OREI_VERIFY_SSL", "false")
    monkeypatch.delenv("MATRIX_CA_CERT", raising=False)
    monkeypatch.delenv("MATRIX_TLS_FINGERPRINT", raising=False)
    matrix = OreiMatrix("127.0.0.1", port=sim.https_port)
    api = ApiClient()
    ws = None
    try:
        assert await matrix.connect()
        set_matrix_device(matrix, config_dir=str(tmp_path), data_dir=str(tmp_path))
        hub = await aiohttp_client(create_rest_app(data_dir=tmp_path))
        url = str(hub.make_url("/")).rstrip("/")
        await api.start(HubInfo(url))
        ws = WsObserver(url.replace("http://", "ws://") + "/ws", "127.0.0.1")
        await ws.start()
        assert ws.error is None
        assert await ws.sync()
        async with SimDevice(sim.control_url) as device:
            runner = Runner(RunOptions(target="sim", clients=("api",), out_dir=tmp_path))
            runner.device = device
            yield matrix, api, ws, device, runner
    finally:
        if ws is not None:
            await ws.stop()
        await api.stop()
        if "hub" in locals():
            await hub.close()
        await matrix.disconnect()
        await sim.stop()


async def check(live, expectation, result, before, mark, cursor):
    _, api, ws, _, runner = live
    return await runner._check(expectation, SCENARIO, api, result, before, mark, ws, api, cursor, [])


@pytest.mark.parametrize("requested", (1, 4, 8, " 6 "))
async def test_disconnected_route_all_exact_payload_and_no_effect(live, requested):
    matrix, api, ws, device, _ = live
    await matrix.disconnect()
    assert matrix.connected is False
    before, cursor = await device.state(), len(await device.log())
    mark = ws.now()
    result = await api.perform(act("route_all", input=requested))
    assert result.status == 503 and not result.ok
    assert result.body == {"success": False, "data": None, "error": "Matrix not connected"}
    expected = int(requested)
    for exp in SCENARIO.expect:
        if isinstance(exp, WsEvent):
            exp = replace(exp, data={"input": expected})
        outcome = await check(live, exp, result, before, mark, cursor)
        assert outcome["result"] == "pass", outcome
    failure = [e["data"] for e in ws.since(mark) if e["event"] == "switch_all_failed"]
    assert failure == [{"input": expected}]
    assert type(failure[0]["input"]) is int
    assert await device.state() == before
    assert ws_contract_check(ws.events)["result"] == "pass"

    # Evaluate counterfactual expectations over the actual refused exchange.
    for wrong in (Response(status=200), Response(status=503, json={"success": True}),
                  WsEvent("switch_all_failed", {"input": 2}, timeout=0),
                  WsEvent("routing_change", timeout=0), NoWsEvent("switch_all_failed", timeout=0)):
        assert (await check(live, wrong, result, before, mark, cursor))["result"] == "fail"


@pytest.mark.parametrize("payload", ({"input": 9}, {"input": True}, {"input": 1.5}, {},
                                     {"input": "oops"}, {"input": 6, "extra": True}))
async def test_invalid_offline_input_has_no_failure_payload_or_success(live, payload):
    matrix, api, ws, device, _ = live
    await matrix.disconnect()
    before, cursor = await device.state(), len(await device.log())
    mark = ws.now()
    result = await api.perform(act("request", method="POST", path="/api/switch", json=payload))
    assert result.status == 503
    assert result.body == {"success": False, "data": None, "error": "Matrix not connected"}
    for exp in (NoWsEvent("switch_all_failed", timeout=0.2), NoWsEvent("switch_failed", timeout=0),
                NoWsEvent("routing_change", timeout=0), NoCommand("video switch"), NoCommand(), DeviceUnchanged()):
        assert (await check(live, exp, result, before, mark, cursor))["result"] == "pass"
    # A malformed request cannot satisfy the registered valid-input oracle.
    assert (await check(live, WsEvent("switch_all_failed", {"input": 6}, timeout=0),
                        result, before, mark, cursor))["result"] == "fail"


async def test_connected_routing_and_invalid_input_controls(live):
    _, api, ws, device, _ = live
    before, cursor = await device.state(), len(await device.log())
    mark = ws.now()
    result = await api.perform(act("route", input=6, output=1))
    assert result.status == 200 and result.body["success"] is True
    assert (await check(live, WsEvent("routing_change", {"output": 1, "input": 6}),
                        result, before, mark, cursor))["result"] == "pass"
    assert (await device.state())["routing"] == [6, *before["routing"][1:]]
    # Actual accepted routing disproves each no-effect oracle independently.
    for exp in (NoCommand("video switch"), NoCommand(), DeviceUnchanged(), NoWsEvent("routing_change", timeout=0)):
        assert (await check(live, exp, result, before, mark, cursor))["result"] == "fail"
    assert (await check(live, NoWsEvent("switch_all_failed", timeout=0.2),
                        result, before, mark, cursor))["result"] == "pass"
    before, cursor = await device.state(), len(await device.log())
    mark = ws.now()
    invalid = await api.perform(act("route_all", input=9))
    assert invalid.status == 400 and invalid.body["success"] is False
    for exp in (NoCommand("video switch"), DeviceUnchanged(), NoWsEvent("switch_all_failed", timeout=0.2)):
        assert (await check(live, exp, invalid, before, mark, cursor))["result"] == "pass"


def run_external_scenario(out_dir):
    """Owned source processes via the existing external-stack runner interface.

    Managed preparation requires healthy Telnet, so it cannot prepare this
    deliberately unavailable hub. This explicit mode does not change that gate.
    The sidecar records settings omitted by external-hub evidence metadata.
    """
    root = Path(__file__).resolve().parents[2]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    assert not any(out_dir.iterdir()), "use a new empty attempt; preserve previous outputs"
    sim = SimulatorProcess(log_dir=out_dir / "process-logs")
    hub = None
    receipt = {"mode": "external disposable source stack", "source_root": str(root),
               "python": sys.executable, "parent_argv": sys.argv,
               "declared_hub_env": SCENARIO.hub_env,
               "source_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in (
                   "run.py", "src/rest_api/control.py", "tools/validate/runner.py", "tools/validate/stack.py",
                   "tests/validation/scenarios/sw_api_client_02_c1.py", "tests/validation/test_sw_api_client_02_c1.py",
               )}}
    try:
        sim.start()
        hub = HubProcess(matrix_host=sim.host, matrix_port=sim.https_port, telnet_port=sim.telnet_port,
                         log_dir=out_dir / "process-logs", extra_env=dict(SCENARIO.hub_env))
        health = hub.start()
        assert health["matrix"]["connected"] is False, health
        receipt.update({"hub_url": hub.base_url, "sim_control_url": sim.control_url,
                        "simulator_ports": {"https": sim.https_port, "telnet": sim.telnet_port,
                                            "control": sim.control_port},
                        "hub_port": hub.api_port, "hub_recorded_env": hub.recorded_env(),
                        "hub_data_dir": hub._data_dir, "initial_health": health,
                        "hub_process": {"pid": hub._proc.pid, "argv": hub._proc.args, "cwd": str(root)},
                        "simulator_process": {"pid": sim._proc.pid, "argv": sim._proc.args, "cwd": str(root)}})
        runner = Runner(RunOptions(target="sim", clients=("api",), out_dir=out_dir,
                                   hub_url=hub.base_url, sim_control_url=sim.control_url))
        receipt["commit"] = runner.commit
        asyncio.run(runner.run(SCENARIOS))
        receipt["summary_path"] = str(out_dir / "run-summary.json")
        return runner
    finally:
        if hub is not None:
            hub_proc = hub._proc
            hub.stop(keep_data=True)
            receipt["hub_exit_code"] = hub_proc.returncode if hub_proc else None
        sim_proc = sim._proc
        sim.stop()
        receipt["simulator_exit_code"] = sim_proc.returncode if sim_proc else None
        (out_dir / "external-stack-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def test_registered_scenario_with_real_source_runner(tmp_path):
    runner = run_external_scenario(tmp_path)
    receipt = json.loads((tmp_path / "external-stack-receipt.json").read_text(encoding="utf-8"))
    assert receipt["declared_hub_env"] == SCENARIO.hub_env
    assert receipt["hub_recorded_env"]["OREI_VERIFY_SSL"] == "true"
    assert receipt["initial_health"]["matrix"]["connected"] is False
    assert receipt["hub_process"]["argv"] == [sys.executable, "run.py"]
    assert [(o.scenario, o.status, o.gate, o.level, o.features) for o in runner.outcomes] == [
        (SCENARIO.id, "pass", "ok", "V2", ["F-API-034"]),
    ]
    records = list(iter_records([tmp_path / "evidence"]))
    assert len(records) == 1
    record = records[0].data
    jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))).validate(record)
    assert record["client"] == "api" and record["level"] == "V2" and record["target"] == "sim"
    assert record["features"] == ["F-API-034"]
    assert record["checks"] and all(c["result"] == "pass" for c in record["checks"])
    observed = record["observations"]
    assert observed["response_status"] == 503
    assert observed["state_before"] == observed["state_after"] and not observed["state_diff"]
    assert not any(e.get("command") == "video switch" for e in observed["device_log"])
    events = [e for e in observed["ws_events"] if e["t_ms"] >= 0]
    assert [e["data"] for e in events if e["event"] == "switch_all_failed"] == [{"input": 6}]
    assert not any(e["event"] in ("routing_change", "switch_failed") for e in events)


def test_scenario_scope_and_discovery():
    from tools.validate.scenarios import discover

    assert discover()[SCENARIO.id] == SCENARIO
    assert SCENARIO.features == ("F-API-034",) and not SCENARIO.client_features
    assert SCENARIO.clients == ("api",) and SCENARIO.targets == ("sim",)
    assert not SCENARIO.writes and not SCENARIO.findings and not SCENARIO.known_findings
