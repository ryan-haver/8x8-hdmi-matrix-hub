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
from tools.validate.registry import load_findings
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
    chosen = [scenarios["routing.switch_one"], scenarios["profiles.recall_output_settings"],
              scenarios["failures.bad_input"], impossible]
    runner = Runner(RunOptions(target="sim", clients=("api",), out_dir=tmp_path, findings=load_findings()))
    asyncio.run(runner.run(chosen))
    out = _outcomes(runner)

    ok = out[("routing.switch_one", "api")]
    assert (ok.status, ok.level, ok.gate) == ("pass", "V2", "ok")
    known = out[("profiles.recall_output_settings", "api")]
    assert (known.status, known.gate) == ("fail", "known-failure")
    assert {c["finding"] for c in known.failed_checks} == {"VAL-01"}
    assert out[("failures.bad_input", "api")].status == "pass"
    bad = out[("selftest.impossible", "api")]
    assert (bad.status, bad.gate) == ("fail", "regression")

    records = {r.data["scenario"]: r.data for r in iter_records([tmp_path / "evidence"])}
    assert set(records) == {"routing.switch_one", "profiles.recall_output_settings", "failures.bad_input",
                            "selftest.impossible"}
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
