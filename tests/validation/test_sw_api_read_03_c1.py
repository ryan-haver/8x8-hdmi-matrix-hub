"""Actual managed simulator/hub output-name observations and failure controls."""

import asyncio
import json
from dataclasses import replace

import jsonschema
import pytest

from tests.validation.scenarios.sw_api_read_03_c1 import NAME, POLL, QUIET_WINDOW, SCENARIOS
from tools.validate import runner as runner_module
from tools.validate.clients.api import ApiClient
from tools.validate.clients.base import ActionResult
from tools.validate.device import SimDevice
from tools.validate.evidence import SCHEMA_PATH, iter_records
from tools.validate.model import ClientState, Device, DeviceUnchanged, NoCommand, NoWsEvent, WsEvent, act
from tools.validate.runner import WS_SCHEMA, Runner, RunOptions, WsObserver
from tools.validate.scenarios import discover


def test_discovery_and_api_attribution():
    scenario = SCENARIOS[0]
    assert discover()[scenario.id] == scenario
    assert scenario.features == ("F-API-040",) and not scenario.client_features
    assert scenario.clients == ("api",) and scenario.targets == ("sim",)
    assert isinstance(scenario.expect[0], WsEvent)
    assert scenario.hub_env == {"STATUS_POLL_INTERVAL": str(POLL), "OREI_STATUS_CACHE_TTL": "0"}


@pytest.mark.parametrize(("expectations", "allowed"), [
    ((WsEvent("output_name_change"),), True),
    ((WsEvent("output_name_change", clients=("api",)),), True),
    ((WsEvent("output_name_change", clients=("browser",)),), False),
    ((WsEvent("output_name_change", clients=()),), False),
    ((NoWsEvent("output_name_change"),), False),
    ((Device("outputs[0].name", equals=NAME), NoCommand()), False),
    ((WsEvent("output_name_change"), ClientState("ui.output.1", equals=NAME)), False),
    ((WsEvent("output_name_change"), ClientState("ui.output.1", clients=("browser",))), True),
    ((WsEvent("output_name_change"), ClientState("ui.output.1", clients=())), True),
])
def test_api_device_change_requires_applicable_positive_ws_without_ui(tmp_path, expectations, allowed):
    runner = Runner(RunOptions(out_dir=tmp_path))
    scenario = replace(SCENARIOS[0], expect=expectations)
    assert (runner._refusal(scenario, ApiClient()) is None) is allowed
    assert ApiClient.observes is False


def test_other_runner_intent_cannot_use_api_ws_exception(tmp_path, monkeypatch):
    # A future runner intent must not inherit device_change's scoped exception.
    monkeypatch.setattr(runner_module, "RUNNER_INTENTS", runner_module.RUNNER_INTENTS | {"request"})
    scenario = replace(SCENARIOS[0], action=act("request", path="/api/status"))
    assert "cannot observe" in Runner(RunOptions(out_dir=tmp_path))._refusal(scenario, ApiClient())


def test_target_client_and_hardware_safeguards_still_refuse(tmp_path):
    scenario = SCENARIOS[0]
    runner = Runner(RunOptions(out_dir=tmp_path))
    assert runner._refusal(replace(scenario, clients=("browser",)), ApiClient())
    assert runner._refusal(replace(scenario, targets=()), ApiClient())
    hardware = Runner(RunOptions(target="hardware", out_dir=tmp_path))
    assert hardware._refusal(scenario, ApiClient())
    route = replace(scenario, action=act("route", input=6, output=1), targets=("hardware",), writes=("routing",))
    assert "allow-writes" in hardware._refusal(route, ApiClient())
    hardware.o.allow_writes = True
    assert "allow-unrestorable" in hardware._refusal(replace(route, writes=("presets",)), ApiClient())
    assert hardware._refusal(replace(route, writes=()), ApiClient()) is None


@pytest.fixture(scope="module")
def observed(tmp_path_factory):
    directory = tmp_path_factory.mktemp("output-name-real")
    positive = SCENARIOS[0]
    wrong_name = replace(positive, id="selftest.output_wrong_name", expect=(
        WsEvent("output_name_change", {"output": 1, "name": "Wrong TV"}, timeout=2),))
    wrong_output = replace(positive, id="selftest.output_wrong_port", expect=(
        WsEvent("output_name_change", {"output": 2, "name": NAME}, timeout=2),))
    quiet = replace(positive, id="selftest.output_unchanged", action=act(
        "device_change", patch={"outputs": {"0": {"name": "TV"}}}), expect=(
            # An unchanged name cannot satisfy this required positive event.
            WsEvent("output_name_change", {"output": 1, "name": "TV"}, timeout=QUIET_WINDOW),
            NoWsEvent("output_name_change", timeout=QUIET_WINDOW),
            NoWsEvent("routing_change", timeout=QUIET_WINDOW),
            DeviceUnchanged(), NoCommand(), NoCommand("set output name"), NoCommand("video switch"),
        ))
    runner = Runner(RunOptions(out_dir=directory))
    asyncio.run(runner.run([positive, wrong_name, wrong_output, quiet]))
    assert [(o.status, o.gate, o.level) for o in runner.outcomes] == [
        ("pass", "ok", "V2"), *( ("fail", "regression", "V2") for _ in range(3)),
    ]
    records = {r.data["scenario"]: r.data for r in iter_records([directory / "evidence"])}
    assert len(records) == 4
    return records


def _after(record, event):
    return [e["data"] for e in record["observations"]["ws_events"] if e["t_ms"] >= 0 and e["event"] == event]


def test_actual_exact_event_without_routing_or_matrix_write(observed):
    record = observed[SCENARIOS[0].id]
    assert _after(record, "output_name_change") == [{"output": 1, "name": NAME}]
    assert _after(record, "routing_change") == []
    assert all(c["result"] == "pass" for c in record["checks"])
    obs = record["observations"]
    assert obs["state_diff"] == [{"path": "outputs[0].name", "before": "TV", "after": NAME}]
    assert not obs["requests"]  # action went directly to the simulator control API
    assert not any(e.get("mutated") for e in obs["device_log"] if e.get("channel") in ("http", "telnet"))
    assert not any(e.get("command") in ("set output name", "video switch") for e in obs["device_log"])
    assert any(e.get("channel") == "http" and e.get("command", "").startswith("get ")
               for e in obs["device_log"])
    assert len(obs["hub_reads"]) == 1
    assert obs["hub_reads"][0]["path"] == "/api/status"
    assert record["environment"]["hub"]["env"]["STATUS_POLL_INTERVAL"] == str(POLL)
    assert record["environment"]["hub"]["env"]["OREI_STATUS_CACHE_TTL"] == "0"
    assert any("in sync before the action" in step for step in record["procedure"])


def test_actual_wrong_payload_and_absent_event_are_failed_evidence(observed):
    for sid in ("selftest.output_wrong_name", "selftest.output_wrong_port"):
        record = observed[sid]
        assert _after(record, "output_name_change") == [{"output": 1, "name": NAME}]
        assert record["checks"][0]["result"] == "fail"
    quiet = observed["selftest.output_unchanged"]
    assert _after(quiet, "output_name_change") == []
    assert _after(quiet, "routing_change") == []
    assert quiet["observations"]["state_diff"] == []
    # Actual simulator reads establish that this was a polled quiet window,
    # rather than a disconnected hub that happened to emit nothing.
    assert sum(e.get("command") == "get output status"
               for e in quiet["observations"]["device_log"]) >= 3
    assert quiet["checks"][0]["result"] == "fail"
    assert all(c["result"] == "pass" for c in quiet["checks"][1:])


def test_all_recorded_real_json_messages_follow_schema(observed):
    evidence_validator = jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    ws_validator = jsonschema.Draft202012Validator(json.loads(WS_SCHEMA.read_text(encoding="utf-8")))
    for record in observed.values():
        evidence_validator.validate(record)
        assert record["features"] == ["F-API-040"]
        for event in record["observations"]["ws_events"]:
            ws_validator.validate({"event": event["event"], "data": event["data"]})


async def test_positive_ws_check_fails_without_an_observer_connection(tmp_path):
    runner = Runner(RunOptions(out_dir=tmp_path))
    runner.device = SimDevice("http://127.0.0.1:1")
    api = ApiClient()
    observer = WsObserver("ws://127.0.0.1:1/ws", "127.0.0.1")
    check = await runner._check(WsEvent("output_name_change", {"output": 1, "name": NAME}, timeout=0),
                                SCENARIOS[0], api, ActionResult(intent="device_change", ok=True),
                                {}, observer.now(), observer, api, 0, [])
    assert check["result"] == "fail" and observer.events == []
