"""The evidence pipeline must distinguish a filtered callback from failed replay.

Uses the real REST app and simulator, without requiring the unfinished runtime
composition startup. Actual run.py/image acceptance remains a separate gate.
"""

from __future__ import annotations

import asyncio
import shutil

import pytest

from rest_api.app import create_rest_app
from tools.validate.clients import flic
from tools.validate.evidence import iter_records
from tools.validate.model import DeviceUnchanged, NoCommand, Scenario, act
from tools.validate.runner import Runner, RunOptions
from tools.validate.stack import SimulatorProcess


@pytest.mark.parametrize("missing_node", [True, False])
async def test_failed_replay_cannot_pass_an_unchanged_device_scenario(
    tmp_path, aiohttp_server, monkeypatch, missing_node,
):
    if not missing_node and not shutil.which("node"):
        pytest.skip("Actual callback replay requires Node.js")
    if missing_node:
        def unavailable(*_args, **_kwargs):
            raise flic.FlicReplayError("Flic replay requires Node.js; executable not found")

        monkeypatch.setattr(flic, "run_flic_driver", unavailable)
    server = await aiohttp_server(create_rest_app())
    sim = SimulatorProcess(log_dir=tmp_path / "sim")
    await asyncio.to_thread(sim.start)
    try:
        scenario = Scenario(
            id="selftest.filtered_flic", title="A mismatching button produces no matrix writes",
            features=("F-FLIC-009",), clients=("flic",), targets=("sim",),
            action=act("flic_sdk_event", button_identifier="Other Button", target_type="switch_output",
                       input_num=6, output_num=1,
                       button_registry={"AA:BB:CC:DD:EE:02": {
                           "name": "Validation", "bdaddr": "AA:BB:CC:DD:EE:02", "serial": "sim",
                       }}, event={"bdaddr": "AA:BB:CC:DD:EE:02", "is_single_click": True}),
            expect=(NoCommand("*"), DeviceUnchanged()),
            covers=("tools/validate/clients/flic.py", "tools/validate/runner.py"),
        )
        runner = Runner(RunOptions(
            clients=("flic",), out_dir=tmp_path / "proof", hub_url=str(server.make_url("/")).rstrip("/"),
            sim_control_url=sim.control_url,
        ))
        outcomes = await runner.run([scenario])
        assert len(outcomes) == 1
        assert outcomes[0].status == ("fail" if missing_node else "pass")
        record = iter_records([tmp_path / "proof" / "evidence"])[0].data
        checks = {c["description"]: c for c in record["checks"]}
        assert checks[NoCommand("*").describe()]["result"] == "pass"
        assert checks[DeviceUnchanged().describe()]["result"] == "pass"
        if missing_node:
            assert outcomes[0].gate == "regression"
            assert any("replay or transport error" in c["description"] for c in outcomes[0].failed_checks)
        else:
            assert record["observations"]["requests"] == []
            assert record["observations"]["response_status"] is None
    finally:
        await asyncio.to_thread(sim.stop)
