"""Managed disconnected preparation, strict observations, defaults and safety boundaries."""

import asyncio
import json
import sys
from dataclasses import replace

import pytest
from aiohttp import web

from tests.validation.scenarios.sw_api_client_02_c1 import SCENARIOS
from tools.validate.clients import make_client
from tools.validate.clients.api import ApiClient
from tools.validate.clients.base import HubInfo
from tools.validate.evidence import SCHEMA_PATH, iter_records
from tools.validate.model import act
from tools.validate.runner import Runner, RunOptions
from tools.validate.scenarios import discover
from tools.validate.stack import HubProcess

SCENARIO = SCENARIOS[0]


@pytest.mark.parametrize("changes", [
    {"matrix_connection": "skip"}, {"matrix_connection": None},
    {"targets": ("sim", "hardware")}, {"targets": ("hardware",)},
    {"clients": ("browser",)}, {"clients": ("api", "uc")}, {"kind": "happy"},
    {"writes": ("routing",)}, {"setup": (act("route_all", input=1),)},
    {"cleanup": (act("route_all", input=1),)}, {"faults": {"drop_http": True}},
])
def test_disconnected_profile_rejects_unsafe_declarations(changes):
    with pytest.raises(ValueError, match="matrix_connection|disconnected preparation"):
        replace(SCENARIO, **changes)


@pytest.mark.parametrize("target,client_name", [("hardware", "api"), ("sim", "browser"), ("sim", "uc")])
async def test_runtime_guards_also_apply_to_direct_preparation(tmp_path, target, client_name):
    runner = Runner(RunOptions(target=target, out_dir=tmp_path))
    client = make_client(client_name)
    assert "disconnected preparation" in runner._refusal(SCENARIO, client)
    # No helper HTTP session exists: the scope guard must run before any read.
    with pytest.raises(RuntimeError, match="simulator-only API failure"):
        await runner._prepare_sim_matrix(SCENARIO, client, ApiClient())


@pytest.mark.parametrize("status,body", [
    (200, None), (200, []), (200, "not a mapping"), (200, {}), (200, {"success": True}),
    (200, {"success": True, "data": []}),
    (200, {"success": True, "data": {"matrix": []}}),
    *[(200, {"success": success, "data": {"matrix": {"configured": True, "connected": False}}})
      for success in (False, 1, "true", None)],
    *[(200, {"success": True, "data": {"matrix": matrix}}) for matrix in (
        {}, {"configured": True}, {"configured": False, "connected": False},
        {"configured": 1, "connected": False}, {"configured": "true", "connected": False},
        {"configured": True, "connected": True}, {"configured": True, "connected": 0},
        {"configured": True, "connected": "false"}, {"configured": True, "connected": None},
    )],
    (503, {"success": True, "data": {"matrix": {"configured": True, "connected": False}}}),
])
async def test_health_precondition_rejects_inexact_observations(tmp_path, aiohttp_server, status, body):
    calls = []

    async def health(request):
        calls.append(request.path)
        return web.json_response(body, status=status)

    app = web.Application()
    app.router.add_get("/api/health", health)
    server = await aiohttp_server(app)
    helper = ApiClient()
    await helper.start(HubInfo(str(server.make_url("/")).rstrip("/")))
    try:
        with pytest.raises(RuntimeError, match="HTTP 200 health"):
            await Runner(RunOptions(out_dir=tmp_path))._prepare_sim_matrix(SCENARIO, helper, helper)
        assert calls == ["/api/health"]  # Immediate requirement, no wait for a fault to arrive.
    finally:
        await helper.stop()


async def test_health_transport_failure_is_not_disconnected_evidence(tmp_path, aiohttp_server):
    server = await aiohttp_server(web.Application())
    url = str(server.make_url("/")).rstrip("/")
    await server.close()
    helper = ApiClient()
    await helper.start(HubInfo(url))
    try:
        with pytest.raises(OSError):
            await Runner(RunOptions(out_dir=tmp_path))._prepare_sim_matrix(SCENARIO, helper, helper)
    finally:
        await helper.stop()


@pytest.mark.parametrize("external", (False, True))
async def test_default_preparation_preserves_actual_telnet_wait_and_external_behavior(tmp_path, aiohttp_server, external):
    calls = []

    async def cables(request):
        calls.append(request.path)
        return web.json_response({"success": True})

    app = web.Application()
    app.router.add_get("/api/status/cables", cables)
    server = await aiohttp_server(app)
    runner = Runner(RunOptions(out_dir=tmp_path, hub_url=str(server.make_url("/")) if external else None))
    runner.hub = HubProcess("unused", 443, 23, tmp_path,
                            external_url=str(server.make_url("/")) if external else None)
    scenario = discover()["contracts.cables"]
    assert scenario.matrix_connection == "ready"
    helper = ApiClient()
    await helper.start(HubInfo(str(server.make_url("/")).rstrip("/")))
    try:
        await runner._prepare_sim_matrix(scenario, helper, helper)
        assert calls == ([] if external else ["/api/status/cables"])
        assert runner.hub.starts == 0
    finally:
        await helper.stop()


class ReceiptRunner(Runner):
    """Observe genuine child handles while leaving preparation and stop mechanics unchanged."""

    def __init__(self, options):
        super().__init__(options)
        self.children = {}

    def remember(self):
        if self.stack is None:
            return
        for name, owner in (("simulator", self.stack.sim), ("hub", self.stack.hub)):
            if owner is None or owner._proc is None:
                continue
            process = owner._proc
            if process.pid not in self.children:
                self.children[process.pid] = (process, {
                    "kind": name, "pid": process.pid, "argv": process.args,
                    "recorded_env": owner.recorded_env() if name == "hub" else {},
                    "log": str(owner.log_path) if name == "hub" else str(owner.log_dir / "simulator.log"),
                })

    def _start_system(self):
        try:
            super()._start_system()
        finally:
            self.remember()

    def _restart_hub(self):
        self.remember()
        try:
            super()._restart_hub()
        finally:
            self.remember()

    def _stop_system(self):
        self.remember()
        super()._stop_system()

    def write_receipt(self, path):
        children = [{**facts, "exit_code": proc.poll()} for proc, facts in self.children.values()]
        receipt = {"source": self.commit, "python": sys.executable, "children": children}
        path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        assert children and all(child["exit_code"] is not None for child in children)


def assert_refusal_record(record):
    import jsonschema

    jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))).validate(record)
    assert (record["scenario"], record["result"], record["gate"], record["level"]) == (
        SCENARIO.id, "pass", "ok", "V2")
    assert len(record["checks"]) == 8
    assert all(check["result"] == "pass" for check in record["checks"])
    assert any("configured=true, connected=false" in step for step in record["procedure"])
    obs = record["observations"]
    assert obs["requests"][0]["body"] == {"input": 6}
    assert obs["response_status"] == 503
    assert obs["requests"][0]["response"] == {
        "success": False, "data": None, "error": "Matrix not connected"}
    assert obs["state_before"] == obs["state_after"] and not obs["state_diff"]
    assert not any(entry.get("command") == "video switch" or entry.get("mutated") for entry in obs["device_log"])
    events = [event for event in obs["ws_events"] if event["t_ms"] >= 0]
    assert [event["data"] for event in events if event["event"] == "switch_all_failed"] == [{"input": 6}]
    assert not any(event["event"] in ("routing_change", "switch_failed") for event in events)
    assert record["environment"]["hub"]["env"]["OREI_VERIFY_SSL"] == "true"
    assert record["environment"]["hub"]["image_digest"] is None


def test_inherited_scenario_in_real_managed_mixed_lifecycle(tmp_path):
    scenarios = discover()
    assert scenarios[SCENARIO.id] == SCENARIO
    chosen = [scenarios["contracts.cables"], SCENARIO, scenarios["routing.switch_one"]]
    runner = ReceiptRunner(RunOptions(target="sim", clients=("api",), out_dir=tmp_path))
    try:
        outcomes = asyncio.run(runner.run(chosen))
    finally:
        runner.write_receipt(tmp_path / "managed-process-receipt.json")
    assert [(outcome.status, outcome.gate) for outcome in outcomes] == [("pass", "ok")] * 3, outcomes
    records = {record.data["scenario"]: record.data for record in iter_records([tmp_path / "evidence"])}
    assert_refusal_record(records[SCENARIO.id])
    for name in ("contracts.cables", "routing.switch_one"):
        assert any("Telnet link" in step for step in records[name]["procedure"])
        assert records[name]["environment"]["hub"]["env"].get("OREI_VERIFY_SSL") != "true"
    assert len(runner.children) >= 4  # One simulator and distinct actual hub generations.


@pytest.mark.parametrize("profile,hub_env,reason", [
    ("ready", SCENARIO.hub_env, "Telnet link"),
    ("disconnected", {}, "HTTP 200 health"),
])
def test_wrong_actual_managed_precondition_blocks_before_action(tmp_path, profile, hub_env, reason):
    scenario = replace(SCENARIO, matrix_connection=profile, hub_env=hub_env)
    runner = ReceiptRunner(RunOptions(target="sim", clients=("api",), out_dir=tmp_path))
    # Establish real healthy connectivity first for the connected negative.
    # Listener readiness alone can briefly report disconnected during startup.
    chosen = [scenario] if profile == "ready" else [discover()["contracts.cables"], scenario]
    try:
        outcomes = asyncio.run(runner.run(chosen))
    finally:
        runner.write_receipt(tmp_path / "managed-process-receipt.json")
    assert outcomes[-1].status == "blocked" and outcomes[-1].gate == "regression"
    assert reason in outcomes[-1].reason
    record = next(record.data for record in iter_records([tmp_path / "evidence"])
                  if record.data["scenario"] == SCENARIO.id)
    assert not record["observations"]["requests"]
    assert not any(step.startswith("action (") for step in record["procedure"])
