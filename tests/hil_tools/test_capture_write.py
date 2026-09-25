"""HIL capture tool, write mode, against the simulator: plan, verify, restore."""

from __future__ import annotations

import asyncio
import io
import json
import signal

import pytest

from tests.hil_tools.helpers import FW, ScriptedConsole, load, make_opts, quiet
from tools.hil.capture import Console, cli, run_capture
from tools.hil.capture import catalog as cmd
from tools.hil.capture.fixtures import RESTORE_LOG, RecordIds
from tools.hil.capture.snapshot import Snapshot, plan_restore
from tools.hil.capture.write_mode import OPT_IN_GROUPS, TESTS, select_tests


def _restore_log(root):
    path = root / RESTORE_LOG
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


async def test_full_write_run_verifies_every_command_and_restores(sim, tmp_path):
    opts = make_opts(sim, tmp_path / "{firmware}", mode="write", i_understand=True)
    code, cap = await run_capture(opts, quiet())
    assert code == cli.EXIT_OK, cap.errors
    assert sim.state.to_dict() == sim.initial_state.to_dict()

    root = tmp_path / FW
    default_tests = [t for t in TESTS if t.group not in OPT_IN_GROUPS]
    for test in default_tests:
        record = load(root, RecordIds.write(test.id))
        assert record["restored"] is True, test.id
        outcomes = [s["outcome"] for s in record["steps"]]
        if test.id not in _EXPECTED_NOT_APPLIED:
            assert "not-applied" not in outcomes, (test.id, [(s["describe"], s["outcome"]) for s in record["steps"]])
        assert "accepted-invalid" not in outcomes, test.id
    assert not (root / "write" / "http_reboot.json").exists()  # opt-in only

    # Findings the report relies on.
    assert load(root, RecordIds.write("http_input_name"))["findings"]["long_name_stored_len"] == 32
    lcd = load(root, RecordIds.write("http_lcd"))["findings"]["lcd_lines"]
    assert lcd == {"0": "lcd off", "1": "lcd on always", "2": "lcd on 15 seconds", "3": "lcd on 30 seconds",
                   "4": "lcd on 60 seconds"}
    power = load(root, RecordIds.write("telnet_power_bare"))["steps"]
    assert power[0]["outcome"] == "not-applied" and power[0]["exchange"]["response"]["text"] == "E00\r\n"

    log = _restore_log(root)
    assert log and all(e["verified"] for e in log if "verified" in e)
    assert load(root, RecordIds.WRITE_SNAPSHOT_FINAL)["differences_from_initial"] == []
    manifest_run = json.loads((root / "manifest.json").read_text(encoding="utf-8"))["runs"][-1]
    assert manifest_run["write_outcome"]["restored"] is True


#: Steps that the simulator deliberately does not apply (so "not-applied" is right).
_EXPECTED_NOT_APPLIED = {"http_input_edid", "telnet_power_bare"}


async def test_write_mode_refuses_without_the_flag(sim, tmp_path):
    code, _ = await run_capture(make_opts(sim, tmp_path / "out", mode="write"), quiet())
    assert code == cli.EXIT_USAGE
    assert not sim.log


async def test_write_mode_prints_the_plan_and_stops_without_confirmation(sim, tmp_path):
    console = ScriptedConsole(answers=["no"])
    opts = make_opts(sim, tmp_path / "out", mode="write", i_understand=True, yes=False, only=["routing"])
    code, cap = await run_capture(opts, console)
    assert code == cli.EXIT_FAILED
    assert "not confirmed" in cap.errors[0]
    assert "WRITE MODE PLAN" in console.text
    assert '{"comhead":"video switch","language":0,"source":[8,8]}' in console.text
    assert console.prompts == ['This changes the live matrix. Type "yes" to start: ']
    assert not [e for e in sim.log if e.get("mutated")]
    # The restore target was saved before asking.
    assert (tmp_path / "out" / "write" / "snapshot-initial.json").exists()


async def test_injected_failure_mid_test_is_restored_and_the_run_continues(sim, tmp_path):
    def boom(test_id: str, index: int) -> None:
        if test_id == "http_output_hdcp" and index == 1:
            raise RuntimeError("injected failure")

    opts = make_opts(sim, tmp_path / "out", mode="write", i_understand=True, only=["output"])
    code, cap = await run_capture(opts, quiet(), after_step=boom)
    assert code == cli.EXIT_FAILED
    assert sim.state.to_dict() == sim.initial_state.to_dict()
    root = tmp_path / "out"
    record = load(root, RecordIds.write("http_output_hdcp"))
    assert record["error"] == {"type": "RuntimeError", "message": "injected failure"}
    assert len(record["steps"]) == 2 and record["restored"] is True
    # hdcp was left at a non-original value when the failure hit, and restored.
    restores = [e for e in _restore_log(root) if e.get("reason") == "after http_output_hdcp" and "field" in e]
    assert [(e["field"], e["port"], e["to"]) for e in restores] == [("hdcp", 8, 3)]
    assert load(root, RecordIds.write("http_output_mute"))["restored"] is True  # later tests still ran


async def test_cancel_mid_run_restores_before_exiting(sim, tmp_path):
    """Ctrl+C cancels the capture task; the finally blocks put everything back."""
    task: asyncio.Task | None = None

    def interrupt(test_id: str, index: int) -> None:
        if test_id == "http_output_scaler" and index == 2:
            assert task is not None
            task.cancel()

    opts = make_opts(sim, tmp_path / "out", mode="write", i_understand=True, only=["output", "names"])
    task = asyncio.ensure_future(run_capture(opts, quiet(), after_step=interrupt))
    code, cap = await task
    assert code == cli.EXIT_INTERRUPTED
    assert sim.state.to_dict() == sim.initial_state.to_dict()
    root = tmp_path / "out"
    assert load(root, RecordIds.write("http_output_scaler"))["restored"] is True
    assert not (root / "write" / "http_output_arc.json").exists()  # nothing ran after the interrupt
    run = json.loads((root / "manifest.json").read_text(encoding="utf-8"))["runs"][-1]
    assert run["interrupted"] is True
    assert load(root, RecordIds.WRITE_SNAPSHOT_FINAL)["differences_from_initial"] == []


async def test_a_restore_that_fails_is_reported_loudly(sim, tmp_path):
    def device_stops_accepting_writes(test_id: str, index: int) -> None:
        if test_id == "http_video_switch" and index == 0:
            sim.faults.update({"reject_writes": True})

    console = Console(interactive=False, stream=io.StringIO())
    opts = make_opts(sim, tmp_path / "out", mode="write", i_understand=True, only=["routing"])
    code, cap = await run_capture(opts, console, after_step=device_stops_accepting_writes)
    assert code == cli.EXIT_NOT_RESTORED
    out = console.stream.getvalue()
    assert "THE MATRIX WAS NOT FULLY RESTORED" in out and "routing port 8" in out
    record = load(tmp_path / "out", RecordIds.write("http_video_switch"))
    assert record["restored"] is False and record["restore_remaining"][0][:2] == ["routing", 8]
    assert not (tmp_path / "out" / "write" / "http_video_switch_all.json").exists()


async def test_interrupt_handler_cancels_once_then_protects_the_restore():
    console = Console(interactive=False, stream=io.StringIO())

    async def body() -> None:
        previous = cli._install_interrupt_handler(console)
        try:
            handler = signal.getsignal(signal.SIGINT)
            assert callable(handler)
            handler(signal.SIGINT, None)
            handler(signal.SIGINT, None)
            await asyncio.sleep(5)
        finally:
            for sig, old in previous.items():
                signal.signal(sig, old)

    with pytest.raises(asyncio.CancelledError):
        await asyncio.ensure_future(body())
    text = console.stream.getvalue()
    assert "restoring the matrix" in text and "Restore in progress" in text


def test_group_selection():
    from tools.hil.capture import Options

    ids = [t.id for t in select_tests(Options(host="x"))]
    assert "http_reboot" not in ids and "cec_live_output" not in ids
    ids = [t.id for t in select_tests(Options(host="x", include=["reboot"]))]
    assert "http_reboot" in ids and "telnet_reboot" in ids
    ids = [t.id for t in select_tests(Options(host="x", only=["names"], skip=["http_output_name"]))]
    assert ids == ["http_input_name"]
    from tools.hil.capture import CaptureError

    with pytest.raises(CaptureError):
        select_tests(Options(host="x", only=["nope"]))


def test_plan_restore_order_and_warnings():
    reads = {
        "get video status": {"power": 0, "allsource": [1, 2, 3, 4, 5, 6, 7, 8]},
        "get system status": {"power": 0, "beep": 0, "lock": 0},
        "get routing status": {"allpreset": [{"name": "X", "allsource": [1] * 8}] * 8},
    }
    current = Snapshot.from_reads(reads)
    target_reads = json.loads(json.dumps(reads))
    target_reads["get video status"]["power"] = 1
    target_reads["get system status"] = {"power": 1, "beep": 1, "lock": 0}
    target_reads["get routing status"]["allpreset"] = [{"name": "Y", "allsource": [2] * 8}] + [
        {"name": "X", "allsource": [1] * 8}] * 7
    target = Snapshot.from_reads(target_reads, lcd_line="lcd on 30 seconds")
    current.lcd_line = "lcd off"
    actions, warnings = plan_restore(current, target, {"lcd on 30 seconds": 3})
    fields_ = [a.field for a in actions]
    assert fields_[0] == "power" and actions[0].payload == cmd.power(1)
    assert "preset_routing" in fields_ and fields_.index("preset_routing") > fields_.index("routing")
    # staging routes all 8 outputs to input 2, saves preset 1, then routes back
    assert actions[fields_.index("preset_routing")].payload == cmd.preset_save(1)
    assert actions[-1].field == "lcd" and actions[-1].payload == cmd.lcd_time(3)
    assert any("preset 1 name" in w for w in warnings)
