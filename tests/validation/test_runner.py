"""The scenario runner end to end: real hub (run.py) + simulator, api client, evidence on disk.

Also runs the *hardware* mode against the simulator's device address (there is
no hardware here, and the tool must never be pointed at a real matrix by
tests): write refusal, snapshot/restore, operator observations.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from tools.validate.device import SimDevice
from tools.validate.evidence import SCHEMA_PATH, iter_records
from tools.validate.ledger import gate
from tools.validate.model import Device, Scenario, act
from tools.validate.registry import Finding, load_findings
from tools.validate.runner import Runner, RunOptions
from tools.validate.scenarios import discover
from tools.validate.stack import SimulatorProcess

jsonschema = pytest.importorskip("jsonschema")


@pytest.fixture(scope="module")
def schema_validator():
    return jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))


def _outcomes(runner: Runner) -> dict[tuple[str, str], object]:
    return {(o.scenario, o.client): o for o in runner.outcomes}


def test_sim_run_produces_evidence(tmp_path: Path, schema_validator):
    scenarios = discover()
    impossible = Scenario(
        id="selftest.impossible", title="An expectation nobody explains must fail the gate",
        features=("F-MTX-001",), action=act("route", input=6, output=1),
        expect=(Device("outputs[0].source", equals=7, timeout=0.3),), covers=("src/rest_api/control.py",),
        targets=("sim",),
    )
    # A failing check linked to an open finding is a known failure, not a regression. The finding is
    # synthetic so this self-test does not depend on which real register rows are still open.
    known_bug = Scenario(
        id="selftest.known", title="A failing check linked to an open finding is a known failure",
        features=("F-MTX-001",), action=act("route", input=6, output=1),
        expect=(Device("outputs[0].source", equals=7, timeout=0.3, finding="SELFTEST-1"),),
        covers=("src/rest_api/control.py",), targets=("sim",),
    )
    findings = {**load_findings(), "SELFTEST-1": Finding("SELFTEST-1", "M", "runner self-test", True, "test")}
    chosen = [scenarios["routing.switch_one"], scenarios["profiles.recall_output_settings"],
              scenarios["failures.bad_input"], known_bug, impossible]
    runner = Runner(RunOptions(target="sim", clients=("api",), out_dir=tmp_path, findings=findings))
    asyncio.run(runner.run(chosen))
    out = _outcomes(runner)

    ok = out[("routing.switch_one", "api")]
    assert (ok.status, ok.level, ok.gate) == ("pass", "V2", "ok")
    # VAL-01 was fixed in WP-C1: the scenario that used to be this test's known failure passes
    assert (out[("profiles.recall_output_settings", "api")].status,
            out[("profiles.recall_output_settings", "api")].gate) == ("pass", "ok")
    known = out[("selftest.known", "api")]
    assert (known.status, known.gate) == ("fail", "known-failure")
    assert {c["finding"] for c in known.failed_checks} == {"SELFTEST-1"}
    assert out[("failures.bad_input", "api")].status == "pass"
    bad = out[("selftest.impossible", "api")]
    assert (bad.status, bad.gate) == ("fail", "regression")

    records = {r.data["scenario"]: r.data for r in iter_records([tmp_path / "evidence"])}
    assert set(records) == {"routing.switch_one", "profiles.recall_output_settings", "failures.bad_input",
                            "selftest.known", "selftest.impossible"}
    for rec in records.values():
        assert list(schema_validator.iter_errors(rec)) == [], rec["scenario"]
    switch = records["routing.switch_one"]
    obs = switch["observations"]
    assert obs["requests"][0]["path"] == "/api/switch" and obs["requests"][0]["status"] == 200
    assert {"path": "outputs[0].source", "before": 2, "after": 6} in obs["state_diff"]
    assert any(e["command"] == "video switch" for e in obs["device_log"])
    assert any(e["event"] == "switch" for e in obs["ws_events"])
    assert switch["features"] == ["F-MTX-001", "F-API-005", "F-API-033"]
    assert switch["environment"]["simulator"]["source_sha256"]
    assert switch["commit"]["sha"]

    summary = json.loads((tmp_path / "run-summary.json").read_text(encoding="utf-8"))
    errors = gate([], summary)
    assert len(errors) == 1 and "selftest.impossible" in errors[0]


@pytest.fixture
def fake_matrix(tmp_path: Path):
    """The simulator, used as if it were a real BK-808 (only its device ports are given to the runner)."""
    sim = SimulatorProcess(log_dir=tmp_path / "sim-logs")
    sim.start()
    try:
        yield sim
    finally:
        sim.stop()


async def _sim_state(sim: SimulatorProcess) -> dict:
    async with SimDevice(sim.control_url) as dev:
        return await dev.state()


def _hw_options(sim: SimulatorProcess, out: Path, **kw) -> RunOptions:
    return RunOptions(target="hardware", clients=("api",), out_dir=out, operator="pytest (simulator as fake matrix)",
                      matrix_host="127.0.0.1", matrix_port=sim.https_port, telnet_port=sim.telnet_port,
                      findings=load_findings(), **kw)


def test_hardware_mode_safety(tmp_path: Path, fake_matrix, schema_validator):
    scenarios = discover()
    before = asyncio.run(_sim_state(fake_matrix))
    chosen = [scenarios[s] for s in ("routing.switch_one", "presets.recall", "failures.bad_input",
                                     "cec.output_power_on", "failures.unreachable_switch")]

    # 1) no --allow-writes: nothing that changes the matrix runs
    runner = Runner(_hw_options(fake_matrix, tmp_path / "ro"))
    asyncio.run(runner.run(chosen))
    out = _outcomes(runner)
    assert out[("routing.switch_one", "api")].status == "skipped"
    assert "--allow-writes" in out[("routing.switch_one", "api")].reason
    assert "--allow-unrestorable" in out[("cec.output_power_on", "api")].reason or \
        "--allow-writes" in out[("cec.output_power_on", "api")].reason
    assert "target 'hardware'" in out[("failures.unreachable_switch", "api")].reason
    ro = out[("failures.bad_input", "api")]
    assert (ro.status, ro.level) == ("pass", "V4")
    assert asyncio.run(_sim_state(fake_matrix))["outputs"] == before["outputs"]

    # 2) --allow-writes, scripted operator answers for one scenario, none for the other
    answers = {"routing.switch_one": [{"answer": "y", "media": ["photos/tv-output1.jpg"]}]}
    runner = Runner(_hw_options(fake_matrix, tmp_path / "rw", allow_writes=True, answers=answers))
    asyncio.run(runner.run([scenarios["routing.switch_one"], scenarios["presets.recall"]]))
    out = _outcomes(runner)
    assert (out[("routing.switch_one", "api")].status, out[("routing.switch_one", "api")].level) == ("pass", "V4")
    assert out[("presets.recall", "api")].status == "blocked"  # the operator never answered
    assert runner.aborted is None

    rec = {r.data["scenario"]: r.data for r in iter_records([tmp_path / "rw" / "evidence"])}["routing.switch_one"]
    assert list(schema_validator.iter_errors(rec)) == []
    assert rec["operator"] == "pytest (simulator as fake matrix)"
    assert rec["observations"]["operator"][0]["confirmed"] is True
    assert rec["observations"]["operator"][0]["media"] == ["photos/tv-output1.jpg"]
    assert rec["observations"]["restore"]["verified"] is True
    assert {"path": "outputs[0].source", "before": 2, "after": 6} in rec["observations"]["state_diff"]
    assert all(c["result"] == "n/a" for c in rec["checks"] if "received" in c["description"])  # no command log
    assert rec["environment"]["matrix"]["firmware_version"]

    # every change was restored on the "matrix"
    assert asyncio.run(_sim_state(fake_matrix))["outputs"] == before["outputs"]


def test_uc_client_runs_against_the_hub_with_the_integration(tmp_path: Path, schema_validator):
    """The scripted Remote (WP-B1): the runner restarts the hub in UC mode for it and back for the api client."""
    scenarios = discover()
    chosen = [scenarios["remote.select_source"], scenarios["remote.output_cec_on"], scenarios["routing.switch_one"]]
    runner = Runner(RunOptions(target="sim", clients=("uc", "api"), out_dir=tmp_path, findings=load_findings()))
    asyncio.run(runner.run(chosen))
    out = _outcomes(runner)

    ok = out[("remote.select_source", "uc")]
    assert (ok.status, ok.level, ok.gate) == ("pass", "V3", "ok")
    known = out[("remote.output_cec_on", "uc")]
    assert (known.status, known.gate) == ("fail", "known-failure")
    assert {c["finding"] for c in known.failed_checks} == {"UC-01"}
    assert out[("routing.switch_one", "api")].status == "pass"  # back on the API-only hub
    assert ("routing.switch_one", "uc") not in out  # not a uc scenario

    records = {(r.data["scenario"], r.data["client"]): r.data for r in iter_records([tmp_path / "evidence"])}
    for rec in records.values():
        assert list(schema_validator.iter_errors(rec)) == [], rec["scenario"]
    select = records[("remote.select_source", "uc")]
    assert select["environment"]["hub"]["entry"].startswith("run.py legacy mode")
    assert select["environment"]["hub"]["env"]["UC_DISABLE_MDNS_PUBLISH"] == "true"
    assert select["observations"]["requests"][0]["body"]["cmd_id"] == "select_source"
    assert select["observations"]["requests"][0]["body"]["params"] == {"source": "PS5"}  # the name the Remote lists
    assert {"path": "outputs[0].source", "before": 2, "after": 6} in select["observations"]["state_diff"]
    crash = records[("remote.output_cec_on", "uc")]
    assert crash["observations"]["requests"][0]["closed"] == 1011
    assert records[("routing.switch_one", "api")]["environment"]["hub"]["entry"].startswith("run.py (USE_MODULAR")
