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
    # http_timeout: each old-hub command in the `legacy` group waits it out (no answer, HIL-09)
    opts = make_opts(sim, tmp_path / "{firmware}", mode="write", i_understand=True, http_timeout=0.5)
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
    assert load(root, RecordIds.write("http_input_name"))["findings"]["long_name_stored_len"] == 40
    assert load(root, RecordIds.write("http_preset_name"))["findings"]["long_name_stored_len"] == 40
    lcd = load(root, RecordIds.write("http_lcd_on_time"))["findings"]
    assert lcd["lcd_lines"] == {"0": "lcd off", "1": "lcd on always", "2": "lcd on 15 seconds",
                                "3": "lcd on 30 seconds", "4": "lcd on 60 seconds"}
    assert set(lcd["lcd_outcomes"].values()) == {"applied"}
    power = load(root, RecordIds.write("telnet_power_bare"))["steps"]
    assert power[0]["outcome"] == "applied" and power[0]["exchange"]["response"]["text"] == "power 0!\r\npower off\r\n"
    # every new command read back from the status reads
    for test_id in ("http_tx_stream", "http_tx_hdcp", "http_hdr_conversion", "http_video_scaler", "http_arc",
                    "http_output_audio_mute", "http_set_edid", "http_ext_audio_mode", "http_ext_audio_out",
                    "http_ext_audio_switch", "http_ext_audio_index", "http_preset_name", "http_preset_recall",
                    "http_preset_save", "telnet_presets"):
        steps = load(root, RecordIds.write(test_id))["steps"]
        assert {s["outcome"] for s in steps if s["kind"] == "write"} == {"applied"}, test_id
        assert {s["outcome"] for s in steps if s["kind"] == "invalid"} <= {"rejected"}, test_id
    # the old hub's commands: never answered (or rejected: the old LCD payload), nothing changed
    legacy = load(root, RecordIds.write("http_legacy_commands"))["findings"]["legacy"]
    assert {e["command"]: e["outcome"] for e in legacy}["set lcd on time"] == "rejected"
    assert {e["outcome"] for e in legacy if e["command"] != "set lcd on time"} == {"unanswered"}
    assert {e["outcome"] for e in load(root, RecordIds.write("telnet_legacy_commands"))["findings"]["legacy"]} == {
        "rejected"}
    assert not [e for e in sim.log if e.get("command") == "get routing status"]  # presets come from `r preset`

    log = _restore_log(root)
    assert log and all(e["verified"] for e in log if "verified" in e)
    assert load(root, RecordIds.WRITE_SNAPSHOT_FINAL)["differences_from_initial"] == []
    manifest_run = json.loads((root / "manifest.json").read_text(encoding="utf-8"))["runs"][-1]
    assert manifest_run["write_outcome"]["restored"] is True


async def test_preset_tests_read_presets_over_telnet_and_restore_an_empty_slot(device_like_sim, tmp_path):
    """V1.10.01 never answers `get routing status` (HIL-01): presets are read with `r preset N`.

    The test preset starts empty (like preset 8 on the captured device): the
    recall of the empty slot is rejected, the tests save into it, and the
    restore empties it again with `preset clear`.
    """
    sim = device_like_sim
    sim.state.presets[7].saved = False
    sim.initial_state.presets[7].saved = False
    opts = make_opts(sim, tmp_path / "out", mode="write", i_understand=True, only=["routing", "presets", "telnet"])
    code, cap = await run_capture(opts, quiet())
    assert code == cli.EXIT_OK, cap.errors
    assert not [e for e in sim.log if e.get("command") in ("get routing status", "preset get")]
    root = tmp_path / "out"
    recall = load(root, RecordIds.write("http_preset_recall"))
    assert recall["steps"][0]["describe"].startswith("recall preset 8 while it is empty")
    assert recall["steps"][0]["outcome"] == "rejected"
    assert recall["steps"][0]["exchange"]["response"]["json"]["result"] == 0
    assert {s["outcome"] for s in recall["steps"] if s["kind"] == "write"} == {"applied"}
    assert load(root, RecordIds.write("telnet_presets"))["restored"] is True
    assert any(e.get("field") == "preset_saved" for e in _restore_log(root))
    assert sim.state.to_dict() == sim.initial_state.to_dict()


#: Steps that the simulator deliberately does not apply (so "not-applied" is right).
_EXPECTED_NOT_APPLIED = {"telnet_power_s"}


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
        if test_id == "http_tx_hdcp" and index == 1:
            raise RuntimeError("injected failure")

    opts = make_opts(sim, tmp_path / "out", mode="write", i_understand=True, only=["output"])
    code, cap = await run_capture(opts, quiet(), after_step=boom)
    assert code == cli.EXIT_FAILED
    assert sim.state.to_dict() == sim.initial_state.to_dict()
    root = tmp_path / "out"
    record = load(root, RecordIds.write("http_tx_hdcp"))
    assert record["error"] == {"type": "RuntimeError", "message": "injected failure"}
    assert len(record["steps"]) == 2 and record["restored"] is True
    # hdcp was left at a non-original value when the failure hit, and restored.
    restores = [e for e in _restore_log(root) if e.get("reason") == "after http_tx_hdcp" and "field" in e]
    assert [(e["field"], e["port"], e["to"]) for e in restores] == [("hdcp", 8, 3)]
    assert restores[0]["payload"] == cmd.output_setting("hdcp", 8, 3)
    assert load(root, RecordIds.write("http_output_audio_mute"))["restored"] is True  # later tests still ran


async def test_cancel_mid_run_restores_before_exiting(sim, tmp_path):
    """Ctrl+C cancels the capture task; the finally blocks put everything back."""
    task: asyncio.Task | None = None

    def interrupt(test_id: str, index: int) -> None:
        if test_id == "http_video_scaler" and index == 2:
            assert task is not None
            task.cancel()

    opts = make_opts(sim, tmp_path / "out", mode="write", i_understand=True, only=["output", "names"])
    task = asyncio.ensure_future(run_capture(opts, quiet(), after_step=interrupt))
    code, cap = await task
    assert code == cli.EXIT_INTERRUPTED
    assert sim.state.to_dict() == sim.initial_state.to_dict()
    root = tmp_path / "out"
    assert load(root, RecordIds.write("http_video_scaler"))["restored"] is True
    assert not (root / "write" / "http_arc.json").exists()  # nothing ran after the interrupt
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


def test_plan_restore_order_and_payloads():
    reads = {
        "get video status": {"power": 0, "allsource": [1, 2, 3, 4, 5, 6, 7, 8], "allname": ["X"] * 8},
        "get system status": {"power": 0, "beep": 0, "lock": 0, "mode": 0},
        "get output status": {"allhdr": [0] * 9, "allscaler": [0] * 9},
        "get input status": {"edid": [36] * 8},
        "get ext-audio status": {"mode": 0, "allsource": [1] * 8, "allout": [1] * 8, "index": 1},
    }
    presets = [{"saved": True, "routing": [1] * 8}] + [None] * 6 + [{"saved": True, "routing": [3] * 8}]
    current = Snapshot.from_reads(reads, presets=presets)
    target_reads = json.loads(json.dumps(reads))
    target_reads["get video status"]["power"] = 1
    target_reads["get video status"]["allname"] = ["Y"] + ["X"] * 7
    target_reads["get system status"] = {"power": 1, "beep": 1, "lock": 0, "mode": 3}
    target_reads["get output status"]["allhdr"] = [2] + [0] * 8
    target_reads["get input status"]["edid"] = [40] + [36] * 7
    target_reads["get ext-audio status"]["allsource"] = [9] + [1] * 7
    target_presets = [{"saved": True, "routing": [2] * 8}] + [None] * 6 + [{"saved": False, "routing": None}]
    target = Snapshot.from_reads(target_reads, presets=target_presets)
    actions, warnings = plan_restore(current, target)
    assert warnings == []
    fields_ = [a.field for a in actions]
    payloads = {a.field: a.payload for a in actions}
    assert fields_[0] == "power" and actions[0].payload == cmd.power(1)
    assert "preset_routing" in fields_ and fields_.index("preset_routing") > fields_.index("routing")
    # staging routes all 8 outputs to input 2, saves preset 1, then routes back
    assert payloads["preset_routing"] == cmd.preset_save(1)
    assert payloads["preset_saved"] == {"comhead": "preset clear", "language": 0, "index": 8}
    assert payloads["preset_names"] == cmd.preset_name(1, "Y")
    assert payloads["hdr"] == {"comhead": "set hdr conversion", "language": 0, "hdr": [1, 2]}  # device codes
    assert payloads["edid"] == cmd.set_edid(1, 40)
    # ext-audio sources are switched in matrix mode, then the mode goes back
    exa = [(a.field, a.payload) for a in actions if a.field.startswith("exa")]
    assert exa == [("exa_mode", cmd.exa_mode(2)), ("exa_source", cmd.exa_switch(1, 9)), ("exa_mode", cmd.exa_mode(0))]
    assert payloads["lcd"] == cmd.lcd_time(3)
