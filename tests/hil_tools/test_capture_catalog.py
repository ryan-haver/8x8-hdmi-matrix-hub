"""The capture tool covers everything the hub sends; the assumption registry matches the simulator."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tools.hil.capture import Options
from tools.hil.capture import catalog as cmd
from tools.hil.capture.assumptions import ASSUMPTIONS, BY_ID
from tools.hil.capture.snapshot import Snapshot
from tools.hil.capture.write_mode import TESTS
from tools.simulator import DeviceState
from tools.simulator.golden import _Checks
from tools.simulator.http_commands import dispatch

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
SIM = ROOT / "tools" / "simulator"


def _default_snapshot() -> Snapshot:
    state = DeviceState.default()
    reads = {c: dispatch(state.copy(), cmd.snapshot_payload(c)).response for c in cmd.SNAPSHOT_READS}
    return Snapshot.from_reads(reads, lcd_line="lcd on 30 seconds")


def _all_steps():
    snap = _default_snapshot()
    opts = Options(host="x")
    for test in TESTS:
        yield from test.build(snap, opts)


# ------------------------------------------------------------------ HTTP


def _hub_comheads() -> set[str]:
    text = (SRC / "orei_matrix.py").read_text(encoding="utf-8")
    return set(re.findall(r'"comhead":\s*"([^"]+)"', text))


def _capture_comheads() -> set[str]:
    comheads = {r.payload["comhead"] for r in cmd.HTTP_READS} | {"login"}
    comheads |= {s.request["comhead"] for s in _all_steps() if s.channel == "http"}
    return comheads


def test_every_hub_comhead_is_captured():
    missing = _hub_comheads() - _capture_comheads()
    assert not missing, f"the capture tool never sends {missing}: add them to catalog/write_mode"


def test_payloads_match_the_hub_shapes():
    """Key order and the `language` field matter for byte-level captures."""
    assert list(cmd.video_switch(1, 2)) == ["comhead", "language", "source"]
    assert list(cmd.input_name(1, "x")) == ["comhead", "language", "name", "index"]
    assert "language" not in cmd.output_setting("hdcp", 1, 3)
    assert list(cmd.cec_index_single("input", 1, 1)) == ["comhead", "port", "index", "enable"]
    assert cmd.exa_enable(3, False) == {"comhead": "set output exa", "output": 3, "exa": 2}


# ------------------------------------------------------------------ Telnet


def _norm(command: str) -> str:
    command = re.sub(r"\s+", " ", command.strip().lower())
    command = re.sub(r"^(s cec (?:in|hdmi out) \d+) \S+$", r"\1 WORD", command)
    return re.sub(r"\b\d+\b", "N", command)


def _hub_telnet_templates() -> set[str]:
    text = (SRC / "telnet_client.py").read_text(encoding="utf-8")
    out = set()
    # Commands are sent inline (`_send_raw(f"...")`) or built first
    # (`telnet_cmd = f"..."`, then `_send_raw(telnet_cmd)`); catch both forms.
    for template in re.findall(r'(?:_send_raw\(|telnet_cmd\s*=\s*)f?"([^"]+)"', text):
        example = re.sub(r"\{[a-z_]+\}", "1", template.replace("{command}", "on"))
        out.add(_norm(example))
    return out


def _capture_telnet() -> set[str]:
    commands = [r.command for r in cmd.TELNET_READS] + [p.command for p in cmd.TELNET_ERROR_PROBES]
    commands += [s.request for s in _all_steps() if s.channel == "telnet"]
    return {_norm(c) for c in commands}


def test_every_hub_telnet_command_is_captured():
    hub = _hub_telnet_templates()
    assert hub == set(cmd.TELNET_COVERAGE), "update catalog.TELNET_COVERAGE"
    missing = hub - _capture_telnet()
    assert not missing, f"the capture tool never sends {missing}"


# ------------------------------------------------------------ assumptions


def _marker_lines() -> list[tuple[str, str]]:
    out = []
    for path in sorted(SIM.glob("*.py")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if re.search(r"(?<!`)ASSUMPTION\(HIL-A\):", line):
                out.append((path.name, line.strip()))
    return out


@pytest.mark.parametrize("file_name, line", _marker_lines())
def test_every_simulator_assumption_is_registered(file_name, line):
    owners = [a.id for a in ASSUMPTIONS for f, text in a.markers if f == file_name and text in line]
    assert owners, f"{file_name}: {line!r} has no entry in tools/hil/capture/assumptions.py"


def test_registered_markers_exist_in_the_simulator():
    lines = _marker_lines()
    for a in ASSUMPTIONS:
        for file_name, text in a.markers:
            assert any(f == file_name and text in line for f, line in lines), (
                f"{a.id}: marker {text!r} not found in {file_name}; resolved? update the registry")


def test_every_assumption_has_a_report_check_and_evidence():
    ids = {a.id for a in ASSUMPTIONS}
    assert len(ids) == len(ASSUMPTIONS)
    for a in ASSUMPTIONS:
        assert callable(getattr(_Checks, a.id.replace("-", "_"), None)), f"no golden check for {a.id}"
        assert a.modes, a.id
    answered = {aid for r in cmd.HTTP_READS for aid in r.answers} | {aid for r in cmd.TELNET_READS for aid in r.answers}
    answered |= {aid for t in TESTS for aid in t.answers}
    assert answered <= set(BY_ID)
