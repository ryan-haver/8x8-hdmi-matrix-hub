"""``--mode write`` (DANGEROUS): every write command, verified and restored.

Each test is a list of :class:`Step` built from the initial snapshot, so the
plan printed before anything is sent shows every exact command. For each test:

1. snapshot the device;
2. run the steps: send, wait for pushes, snapshot again, compare;
3. restore the pre-test snapshot (``finally``: also on errors and Ctrl+C) and
   verify it with another snapshot.

After the last test (or an abort) the initial snapshot is restored once more.
Every restore write is appended to ``write/restore-log.jsonl`` immediately.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from . import catalog as cmd
from .context import Capture, CaptureError, Options, RestoreError, wait_until
from .fixtures import RecordIds
from .snapshot import Snapshot, diff, lcd_line, status_changes
from .transport import is_data_response

Expect = Callable[[Snapshot, Snapshot], bool]

#: Opt-in groups (not run unless named with --include).
OPT_IN_GROUPS = ("cec-live", "reboot")
LONG_NAME = ("HIL-LONG-NAME-" + "0123456789" * 3)[:40]
TEST_NAME = "HIL-CAPTURE"


class SkipTestError(Exception):
    """A test cannot run (missing data, no Telnet...)."""


@dataclass
class Step:
    channel: str  # "http" | "telnet"
    request: Any  # payload dict or Telnet command
    describe: str
    #: write (expected to change state), invalid (expected rejected),
    #: read (a read, e.g. during standby), noop (same value), cec (no readback)
    kind: str = "write"
    expect: Expect | None = None
    status_text: bool = False
    lcd_mode: int | None = None
    reboot: bool = False
    ask: str | None = None


@dataclass
class WriteTest:
    id: str
    group: str
    title: str
    answers: tuple[str, ...]
    build: Callable[[Snapshot, Options], list[Step]]
    needs_telnet: bool = False
    with_lcd: bool = False


# ------------------------------------------------------------------ helpers


def _other(current: int | None, preferred: int, lo: int = 1, hi: int = 8, avoid: tuple[int, ...] = ()) -> int:
    """A value in lo..hi different from ``current`` (and ``avoid``), preferring ``preferred``."""
    candidates = [preferred, *range(lo, hi + 1)]
    for c in candidates:
        if lo <= c <= hi and c != current and c not in avoid:
            return c
    raise SkipTestError(f"no alternative value to {current}")


def _need(value: Any, what: str) -> Any:
    if value is None:
        raise SkipTestError(f"{what} could not be read")
    return value


def _cycle(current: int | None, lo: int, hi: int) -> list[int]:
    """Every value lo..hi, with the current one last (so the last step changes it back)."""
    values = [v for v in range(lo, hi + 1) if v != current]
    if current is not None and lo <= current <= hi:
        values.append(current)
    return values


def _at(field_name: str, port: int, value: Any) -> Expect:
    return lambda prev, now: (getattr(now, field_name) or [None] * 8)[port - 1] == value


def _scalar(field_name: str, value: Any) -> Expect:
    return lambda prev, now: getattr(now, field_name) == value


def _http(payload: dict[str, Any], describe: str, **kw: Any) -> Step:
    return Step("http", payload, describe, **kw)


def _telnet(command: str, describe: str, **kw: Any) -> Step:
    return Step("telnet", command, describe, **kw)


# ------------------------------------------------------------------- tests
# T = --test-output, I = --test-input, P = --test-preset


def _routing(s: Snapshot, o: Options) -> list[Step]:
    t = o.test_output
    routing = _need(s.routing, "routing")
    new = _other(routing[t - 1], o.test_input)
    return [
        _http(cmd.video_switch(t, new), f"output {t}: input {routing[t - 1]} -> {new}", expect=_at("routing", t, new)),
        _http(cmd.video_switch(9, 1), "invalid output 9", kind="invalid"),
        _http(cmd.video_switch(t, 9), "invalid input 9", kind="invalid"),
        _http(cmd.video_switch(t, 0), "invalid input 0", kind="invalid"),
    ]


def _routing_all(s: Snapshot, o: Options) -> list[Step]:
    routing = _need(s.routing, "routing")
    new = _other(routing[0], o.test_input)
    return [_http(cmd.video_switch(0, new), f"ALL outputs -> input {new} (output 0 = all)",
                  expect=lambda p, n: n.routing == [new] * 8)]


def _preset_recall(s: Snapshot, o: Options) -> list[Step]:
    p = o.test_preset
    presets = _need(s.presets, "presets (get routing status)")
    target = presets[p - 1]["routing"]
    return [
        _http(cmd.preset_set(p), f"recall preset {p} (routing -> {target}, ALL outputs)",
              expect=lambda prev, now: now.routing == target),
        _http(cmd.preset_set(9), "invalid preset 9", kind="invalid"),
        _http(cmd.preset_set(0), "invalid preset 0", kind="invalid"),
    ]


def _preset_save(s: Snapshot, o: Options) -> list[Step]:
    p, t = o.test_preset, o.test_output
    routing = _need(s.routing, "routing")
    presets = _need(s.presets, "presets (get routing status)")
    new = _other(routing[t - 1], o.test_input, avoid=(presets[p - 1]["routing"][t - 1],))
    return [
        _http(cmd.video_switch(t, new), f"stage: output {t} -> input {new}", expect=_at("routing", t, new)),
        _http(cmd.preset_save(p), f"save live routing into preset {p} (overwrites it; restored afterwards)",
              expect=lambda prev, now: bool(now.presets) and now.presets[p - 1]["routing"] == now.routing),
        _http(cmd.preset_save(9), "invalid preset 9", kind="invalid"),
    ]


def _name_steps(kind: str, port: int, s: Snapshot) -> list[Step]:
    field_name = "input_names" if kind == "input" else "output_names"
    builder = cmd.input_name if kind == "input" else cmd.output_name
    names = _need(getattr(s, field_name), f"{kind} names")
    return [
        _http(builder(port, TEST_NAME), f"{kind} {port} name {names[port - 1]!r} -> {TEST_NAME!r}",
              expect=_at(field_name, port, TEST_NAME)),
        _http(builder(port, LONG_NAME), f"{kind} {port} name -> {len(LONG_NAME)}-char name (truncation?)",
              expect=lambda prev, now: (getattr(now, field_name) or [None] * 8)[port - 1] != TEST_NAME),
        _http(builder(9, "HIL"), "invalid index 9", kind="invalid"),
    ]


def _output_toggle(setting: str, lo: int, hi: int, bad: tuple[int, ...]) -> Callable[[Snapshot, Options], list[Step]]:
    def build(s: Snapshot, o: Options) -> list[Step]:
        t = o.test_output
        values = _need(getattr(s, setting), f"output {setting}")
        steps = [
            _http(cmd.output_setting(setting, t, v),
                  f"output {t} {setting} -> {v}" + (" (back to the original)" if v == values[t - 1] else ""),
                  expect=_at(setting, t, v), status_text=True)
            for v in _cycle(values[t - 1], lo, hi)
        ]
        steps.append(_http(cmd.output_setting(setting, 9, lo), "invalid output 9", kind="invalid"))
        steps += [_http(cmd.output_setting(setting, t, b), f"invalid {setting} {b}", kind="invalid") for b in bad]
        return steps

    return build


def _edid(s: Snapshot, o: Options) -> list[Step]:
    i = o.test_input
    edid = _need(s.edid, "EDID")
    first = _other(edid[i - 1], 1, 1, 38)
    steps = [_http(cmd.input_edid(i, first), f"input {i} EDID {edid[i - 1]} -> {first}", expect=_at("edid", i, first))]
    for v in (38, 39, 47, 48):
        steps.append(_http(cmd.input_edid(i, v), f"input {i} EDID -> {v} (accepted?)", expect=_at("edid", i, v)))
    steps.append(_http(cmd.input_edid(i, 0), "invalid EDID 0", kind="invalid"))
    return steps


def _copy_edid(s: Snapshot, o: Options) -> list[Step]:
    i = o.test_input
    edid = _need(s.edid, "EDID")
    base = _other(edid[i - 1], 1, 1, 14)
    changed: Expect = lambda prev, now: bool(now.edid) and now.edid[i - 1] != prev.edid[i - 1]  # noqa: E731
    return [
        _http(cmd.input_edid(i, base), f"stage: input {i} EDID -> {base}", expect=_at("edid", i, base)),
        _http(cmd.copy_edid(i, 1), f"copy edid output 1 -> input {i} (documented; BE-25)", expect=changed),
        _http(cmd.input_edid(i, base), f"stage: input {i} EDID -> {base}", expect=_at("edid", i, base)),
        _http(cmd.input_edid(i, 15), "set input edid 15 = 14+1, the hub's 'copy from output 1' (BE-25)",
              expect=_at("edid", i, 15)),
    ]


def _cec_bulk(s: Snapshot, o: Options) -> list[Step]:
    i = o.test_input
    cin, cout = _need(s.cec_in, "CEC input enable"), _need(s.cec_out, "CEC output enable")
    toggled = list(cin)
    toggled[i - 1] = 0 if cin[i - 1] else 1
    return [
        _http(cmd.cec_index_bulk(toggled, cout), f"CEC input {i} {cin[i - 1]} -> {toggled[i - 1]} (8-element arrays)",
              expect=lambda p, n: n.cec_in == toggled and n.cec_out == cout),
        _http(cmd.cec_index_bulk(cin[:7], cout), "invalid: 7-element inputindex", kind="invalid"),
    ]


def _cec_single(s: Snapshot, o: Options) -> list[Step]:
    i, t = o.test_input, o.test_output
    cin, cout = _need(s.cec_in, "CEC input enable"), _need(s.cec_out, "CEC output enable")
    vi, vo = 0 if cin[i - 1] else 1, 0 if cout[t - 1] else 1
    return [
        _http(cmd.cec_index_single("input", i, vi), f"hub single-port shape: CEC input {i} -> {vi} (BE-13)",
              expect=_at("cec_in", i, vi)),
        _http(cmd.cec_index_single("output", t, vo), f"hub single-port shape: CEC output {t} -> {vo} (BE-13)",
              expect=_at("cec_out", t, vo)),
    ]


def _cec_invalid(s: Snapshot, o: Options) -> list[Step]:
    i = o.test_input
    return [
        _http(cmd.cec_command(0, i, 99), "cec command index 99", kind="invalid"),
        _http(cmd.cec_command(0, 0, 1), "cec command with no target port", kind="invalid"),
        _http(cmd.cec_command(2, i, 1), "cec command object 2", kind="invalid"),
    ]


def _cec_live(s: Snapshot, o: Options) -> list[Step]:
    port = o.cec_output
    q = f"What did the display on output {port} do? (Enter = nothing) "
    words = sorted((set(_CEC_WORDS) | {"active"}) - {"on", "off"}) + ["off", "on"]
    steps = [_telnet(f"s cec hdmi out {port} {w}", f"Telnet CEC '{w}' to output {port}", kind="cec", ask=q)
             for w in words]
    steps += [_http(cmd.cec_command(1, port, idx), f"HTTP cec command object 1 index {idx} to output {port}",
                    kind="cec", ask=q) for idx in range(1, 7)]
    return steps


_CEC_WORDS = ("menu", "back", "up", "down", "left", "right", "enter", "play", "pause", "stop", "previous", "next",
              "rew", "ff", "vol+", "vol-", "mute", "on", "off")


def _exa_mode(s: Snapshot, o: Options) -> list[Step]:
    mode = _need(s.exa_mode, "ext-audio mode")
    steps = [_http(cmd.exa_mode(m), f"ext-audio mode -> {m}", expect=_scalar("exa_mode", m)) for m in _cycle(mode, 0, 2)]
    steps.append(_http(cmd.exa_mode(3), "invalid mode 3", kind="invalid"))
    return steps


def _exa_enable(s: Snapshot, o: Options) -> list[Step]:
    t = o.test_output
    en = _need(s.exa_enable, "ext-audio enable")
    new = 0 if en[t - 1] else 1
    return [_http(cmd.exa_enable(t, bool(new)), f"ext-audio output {t} enable {en[t - 1]} -> {new} "
                  f"(exa {1 if new else 2})", expect=_at("exa_enable", t, new))]


def _exa_source(s: Snapshot, o: Options) -> list[Step]:
    t = o.test_output
    src = _need(s.exa_source, "ext-audio source")
    new = _other(src[t - 1], o.test_input)
    return [_http(cmd.exa_source(t, new), f"ext-audio output {t} source {src[t - 1]} -> {new}",
                  expect=_at("exa_source", t, new))]


def _flag(name: str, builder: Callable[[int], dict[str, Any]]) -> Callable[[Snapshot, Options], list[Step]]:
    def build(s: Snapshot, o: Options) -> list[Step]:
        cur = _need(getattr(s, name), name)
        new = 0 if cur else 1
        return [
            _http(builder(new), f"{name} {cur} -> {new}", expect=_scalar(name, new)),
            _http(builder(2), f"invalid {name} 2", kind="invalid"),
        ]

    return build


def _lcd(s: Snapshot, o: Options) -> list[Step]:
    _need(s.lcd_line, "LCD line of the Telnet status dump")
    steps = [_http(cmd.lcd_time(m), f"LCD on time -> code {m}", status_text=True, lcd_mode=m) for m in range(5)]
    steps.append(_http(cmd.lcd_time(5), "invalid code 5", kind="invalid"))
    return steps


def _power(s: Snapshot, o: Options) -> list[Step]:
    if s.power != 1:
        raise SkipTestError("the matrix is not powered on")
    return [
        _http(cmd.power(0), "STANDBY (all outputs go dark)", expect=_scalar("power", 0)),
        _http(cmd.read("get video status"), "read while in standby", kind="read"),
        _http(cmd.beep(int(s.beep if s.beep is not None else 1)), "no-op write (beep unchanged) while in standby",
              kind="noop"),
        _http(cmd.power(1), "power on", expect=_scalar("power", 1)),
        _http(cmd.power(2), "invalid power 2", kind="invalid"),
    ]


def _telnet_power(prefix: str) -> Callable[[Snapshot, Options], list[Step]]:
    def build(s: Snapshot, o: Options) -> list[Step]:
        if s.power != 1:
            raise SkipTestError("the matrix is not powered on")
        return [
            _telnet(f"{prefix}power 0", "STANDBY via Telnet", expect=_scalar("power", 0)),
            # Only a real 0 -> 1 transition proves the command works.
            _telnet(f"{prefix}power 1", "power on via Telnet (proves nothing if standby did not apply)",
                    expect=lambda p, n: p.power == 0 and n.power == 1),
        ]

    return build


def _telnet_routing(s: Snapshot, o: Options) -> list[Step]:
    t = o.test_output
    routing = _need(s.routing, "routing")
    new = _other(routing[t - 1], o.test_input)
    new2 = _other(new, routing[t - 1])
    new_all = _other(routing[0], o.test_input)
    return [
        _telnet(f"s output {t} in source {new}", f"output {t} -> input {new} (hub syntax)",
                expect=_at("routing", t, new)),
        _telnet(f"s av {new2} {t}", f"output {t} -> input {new2} (vendor 's av <in> <out>')",
                expect=_at("routing", t, new2)),
        _telnet(f"s output 0 in source {new_all}", f"ALL outputs -> input {new_all}",
                expect=lambda p, n: n.routing == [new_all] * 8),
    ]


def _telnet_presets(s: Snapshot, o: Options) -> list[Step]:
    p, t = o.test_preset, o.test_output
    routing = _need(s.routing, "routing")
    presets = _need(s.presets, "presets")
    target = presets[p - 1]["routing"]
    new = _other(routing[t - 1], o.test_input, avoid=(target[t - 1],))
    saved: Expect = lambda prev, now: bool(now.presets) and now.presets[p - 1]["routing"] == now.routing  # noqa: E731
    return [
        _telnet(f"s recall preset {p}", f"recall preset {p} (hub syntax; ALL outputs)",
                expect=lambda prev, now: now.routing == target),
        _http(cmd.video_switch(t, new), f"stage: output {t} -> input {new}", expect=_at("routing", t, new)),
        _telnet(f"s save preset {p}", f"save preset {p} (hub syntax)", expect=saved),
        _telnet(f"s clear preset {p}", f"clear preset {p} (hub syntax)",
                expect=lambda prev, now: bool(now.presets) and now.presets[p - 1] != prev.presets[p - 1]),
        _telnet(f"s preset recall {p}", f"recall preset {p} (vendor syntax)",
                expect=lambda prev, now: bool(now.presets) and now.routing == now.presets[p - 1]["routing"]),
        _http(cmd.video_switch(t, new), f"stage: output {t} -> input {new}"),
        _telnet(f"s preset save {p}", f"save preset {p} (vendor syntax)", expect=saved),
    ]


def _telnet_system(s: Snapshot, o: Options) -> list[Step]:
    t = o.test_output
    steps = []
    if s.beep is not None:
        steps.append(_telnet(f"s beep {0 if s.beep else 1}", "beep toggle", expect=_scalar("beep", 0 if s.beep else 1)))
    if s.lock is not None:
        steps.append(_telnet(f"s lock {0 if s.lock else 1}", "panel lock toggle",
                             expect=_scalar("lock", 0 if s.lock else 1)))
    if s.stream is not None:
        new = 0 if s.stream[t - 1] else 1
        steps.append(_telnet(f"s out {t} stream {new}", f"output {t} stream -> {new}", expect=_at("stream", t, new)))
    if not steps:
        raise SkipTestError("system state could not be read")
    return steps


def _reboot_http(s: Snapshot, o: Options) -> list[Step]:
    return [_http(cmd.reboot(), "REBOOT the matrix via HTTP (waits until it is back)", kind="write", reboot=True)]


def _reboot_telnet(s: Snapshot, o: Options) -> list[Step]:
    return [_telnet("reboot", "REBOOT the matrix via Telnet (waits until it is back)", kind="write", reboot=True)]


TESTS: tuple[WriteTest, ...] = (
    WriteTest("http_video_switch", "routing", "Route one output",
              ("write-ok-results", "write-fail-result", "push-wording"), _routing),
    WriteTest("http_video_switch_all", "routing", "Route all outputs (output 0)", ("write-ok-results",), _routing_all),
    WriteTest("http_preset_recall", "presets", "Recall a preset",
              ("write-ok-results", "write-fail-result"), _preset_recall),
    WriteTest("http_preset_save", "presets", "Save a preset", ("write-ok-results", "write-fail-result"), _preset_save),
    WriteTest("http_input_name", "names", "Rename an input",
              ("write-ok-results", "write-fail-result", "name-truncation"),
              lambda s, o: _name_steps("input", o.test_input, s)),
    WriteTest("http_output_name", "names", "Rename an output",
              ("write-ok-results", "write-fail-result", "name-truncation"),
              lambda s, o: _name_steps("output", o.test_output, s)),
    WriteTest("http_output_stream", "output", "Output stream on/off",
              ("write-ok-results", "write-fail-result"), _output_toggle("stream", 0, 1, (2,))),
    WriteTest("http_output_hdcp", "output", "Output HDCP mode (every code)",
              ("write-ok-results", "write-fail-result", "output-mode-text"), _output_toggle("hdcp", 1, 5, (0, 6))),
    WriteTest("http_output_hdr", "output", "Output HDR mode (every code)",
              ("write-ok-results", "write-fail-result", "output-mode-text"), _output_toggle("hdr", 1, 3, (0, 4))),
    WriteTest("http_output_scaler", "output", "Output scaler mode (every code; audio-only BE-15)",
              ("write-ok-results", "write-fail-result", "output-mode-text"), _output_toggle("scaler", 1, 5, (0, 6))),
    WriteTest("http_output_arc", "output", "Output ARC", ("write-ok-results", "write-fail-result"),
              _output_toggle("arc", 0, 1, (2,))),
    WriteTest("http_output_mute", "output", "Output audio mute", ("write-ok-results", "write-fail-result"),
              _output_toggle("mute", 0, 1, (2,))),
    WriteTest("http_input_edid", "edid", "Input EDID mode (range)",
              ("write-ok-results", "write-fail-result", "edid-range"), _edid),
    WriteTest("http_copy_edid", "edid", "EDID copy from output 1 (BE-25)", ("write-ok-results", "copy-edid"),
              _copy_edid),
    WriteTest("http_cec_index_bulk", "cec-enable", "CEC enable, documented array shape",
              ("write-ok-results", "write-fail-result"), _cec_bulk),
    WriteTest("http_cec_index_single", "cec-enable", "CEC enable, hub single-port shape (BE-13)",
              ("write-ok-results", "cec-index-single-port"), _cec_single),
    WriteTest("http_cec_command_invalid", "cec-invalid", "CEC command with invalid parameters",
              ("write-fail-result",), _cec_invalid),
    WriteTest("http_exa_mode", "ext-audio", "Ext-audio mode", ("write-ok-results", "write-fail-result", "exa-commands"),
              _exa_mode),
    WriteTest("http_exa_enable", "ext-audio", "Ext-audio enable", ("write-ok-results", "exa-commands"), _exa_enable),
    WriteTest("http_exa_source", "ext-audio", "Ext-audio source", ("write-ok-results", "exa-commands"), _exa_source),
    WriteTest("http_beep", "system", "Beep", ("write-ok-results", "write-fail-result"), _flag("beep", cmd.beep)),
    WriteTest("http_panel_lock", "system", "Front-panel lock", ("write-ok-results", "write-fail-result"),
              _flag("lock", cmd.panel_lock)),
    WriteTest("http_lcd", "system", "LCD on time (every code; API-07)",
              ("write-ok-results", "write-fail-result", "lcd-codes"), _lcd, needs_telnet=True, with_lcd=True),
    WriteTest("telnet_routing", "telnet", "Telnet routing commands", ("telnet-set-acks", "push-wording"),
              _telnet_routing, needs_telnet=True),
    WriteTest("telnet_presets", "telnet", "Telnet preset commands", ("telnet-set-acks",), _telnet_presets,
              needs_telnet=True),
    WriteTest("telnet_system", "telnet", "Telnet beep / lock / stream", ("telnet-set-acks",), _telnet_system,
              needs_telnet=True),
    WriteTest("http_power", "power", "Standby and power on; commands in standby",
              ("write-ok-results", "write-fail-result", "standby-behaviour"), _power),
    WriteTest("telnet_power_bare", "power", "Telnet 'power N' (what TelnetClient sends)",
              ("telnet-bare-power", "telnet-set-acks"), _telnet_power(""), needs_telnet=True),
    WriteTest("telnet_power_s", "power", "Telnet 's power N' (vendor syntax)",
              ("telnet-bare-power", "telnet-set-acks"), _telnet_power("s "), needs_telnet=True),
    WriteTest("cec_live_output", "cec-live", "Live CEC to the display on --cec-output (BE-14)",
              ("telnet-cec-output-words", "cec-disabled-port", "write-ok-results"), _cec_live, needs_telnet=True),
    WriteTest("http_reboot", "reboot", "Reboot via HTTP", ("reboot-replies-first",), _reboot_http),
    WriteTest("telnet_reboot", "reboot", "Reboot via Telnet", ("telnet-reboot",), _reboot_telnet, needs_telnet=True),
)

GROUPS = tuple(dict.fromkeys(t.group for t in TESTS))


def select_tests(opts: Options) -> list[WriteTest]:
    unknown = {g for g in [*opts.only, *opts.skip, *opts.include] if g not in GROUPS and g not in _ids()}
    if unknown:
        raise CaptureError(f"unknown write group/test {sorted(unknown)}; groups: {', '.join(GROUPS)}")
    chosen = []
    for test in TESTS:
        named = {test.group, test.id}
        if opts.only and not named & set(opts.only):
            continue
        if named & set(opts.skip):
            continue
        if test.group in OPT_IN_GROUPS and not named & set(opts.include) and not named & set(opts.only):
            continue
        chosen.append(test)
    return chosen


def _ids() -> set[str]:
    return {t.id for t in TESTS}


# ------------------------------------------------------------------ runner


@dataclass
class _Planned:
    test: WriteTest
    steps: list[Step] = field(default_factory=list)
    skip: str | None = None


def build_plan(cap: Capture, initial: Snapshot) -> list[_Planned]:
    plan = []
    for test in select_tests(cap.opts):
        if test.needs_telnet and cap.telnet is None:
            plan.append(_Planned(test, skip="needs Telnet"))
            continue
        try:
            plan.append(_Planned(test, test.build(initial, cap.opts)))
        except SkipTestError as exc:
            plan.append(_Planned(test, skip=str(exc)))
    return plan


def plan_lines(plan: list[_Planned]) -> list[str]:
    lines = []
    n = 0
    for item in plan:
        if item.skip:
            lines.append(f"  [skip] {item.test.id}: {item.skip}")
            continue
        lines.append(f"  {item.test.id} ({item.test.group}): {item.test.title}")
        for step in item.steps:
            n += 1
            req = step.request if isinstance(step.request, str) else _compact(step.request)
            lines.append(f"      {n:>3}. [{step.channel} {step.kind}] {step.describe}")
            lines.append(f"           {req}")
        lines.append("      then: restore every change and verify")
    return lines


def _compact(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload, separators=(",", ":"))


async def run_write(cap: Capture, *, confirm: bool = True) -> dict[str, Any]:
    """Run write mode. Returns the outcome summary (also stored in the manifest)."""
    con = cap.console
    if cap.opts.telnet:
        await cap.open_telnet()
    initial = await cap.snapshot(with_lcd=cap.telnet is not None)
    if initial.routing is None or initial.power is None:
        raise CaptureError(f"cannot read the device state ({initial.errors}); refusing to write")
    cap.add(RecordIds.WRITE_SNAPSHOT_INITIAL, {
        "title": "Device state before write mode (restore target)", "answers": [],
        "snapshot": initial.to_dict(),
    })
    plan = build_plan(cap, initial)
    runnable = [p for p in plan if not p.skip]
    con.print("")
    con.print(f"WRITE MODE PLAN - {sum(len(p.steps) for p in runnable)} commands in {len(runnable)} tests "
              f"against {cap.opts.host}:")
    for line in plan_lines(plan):
        con.print(line)
    con.print("")
    con.print(f"Initial state saved to {cap.writer.root / (RecordIds.WRITE_SNAPSHOT_INITIAL + '.json')}"
              if cap.writer else "")
    if confirm and not cap.opts.yes:
        answer = cap.console.ask('This changes the live matrix. Type "yes" to start: ')
        if (answer or "").strip().lower() != "yes":
            raise CaptureError("write mode not confirmed; nothing was changed")

    outcome: dict[str, Any] = {"tests": {}, "aborted": None, "restored": None}
    try:
        for item in plan:
            if item.skip:
                outcome["tests"][item.test.id] = f"skipped: {item.skip}"
                continue
            outcome["tests"][item.test.id] = await _run_test(cap, item)
    except BaseException as exc:
        outcome["aborted"] = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
        con.print(f"\nABORTED ({outcome['aborted']}) - restoring the initial state...")
        raise
    finally:
        remaining, interrupted = await _run_to_completion(
            cap.restore_to(initial, reason="final restore to the initial snapshot")
        )
        final = await cap.snapshot(with_lcd=cap.telnet is not None)
        outcome["restored"] = not remaining
        outcome["remaining"] = remaining
        cap.add(RecordIds.WRITE_SNAPSHOT_FINAL, {
            "title": "Device state after write mode", "answers": [],
            "snapshot": final.to_dict(), "differences_from_initial": diff(initial, final),
        })
        if remaining:
            cap.errors.append(f"NOT RESTORED: {remaining}")
            con.print("")
            con.print("!" * 72)
            con.print("THE MATRIX WAS NOT FULLY RESTORED. Differences from the initial state:")
            for d in remaining:
                con.print(f"  {d[0]} port {d[1]}: now {d[3]!r}, was {d[2]!r}")
            con.print(f"Initial state: {cap.writer.root / (RecordIds.WRITE_SNAPSHOT_INITIAL + '.json')}"
                      if cap.writer else "")
            con.print("!" * 72)
        else:
            con.print("Device restored to its initial state (verified).")
        if interrupted:
            con.print("(restore finished despite an interrupt)")
    return outcome


async def _run_to_completion(coro: Any) -> tuple[Any, bool]:
    """Await ``coro`` so that cancelling the caller cannot interrupt it."""
    task = asyncio.ensure_future(coro)
    interrupted = False
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            interrupted = True
            current = asyncio.current_task()
            if current is not None:
                current.uncancel()
    return task.result(), interrupted


async def _send(cap: Capture, step: Step) -> dict[str, Any]:
    role = {"write": "write", "invalid": "write-invalid", "read": "read-during-test", "noop": "write-noop",
            "cec": "write-cec"}[step.kind]
    if step.channel == "telnet":
        assert cap.telnet is not None
        if not cap.telnet.connected:
            await cap.reconnect_telnet()
        return await cap.telnet.command(step.request, role=role)
    return await cap.http.post(step.request, role=role)


async def _wait_for_reboot(cap: Capture) -> dict[str, Any]:
    """After a reboot command: wait for the device to go away and come back."""
    loop = asyncio.get_running_loop()
    t0 = loop.time()
    await asyncio.sleep(2)

    async def back() -> bool:
        client = cap.http.clone()
        try:
            await cap.login(client, role="reboot-poll")
            doc = await cap.read_json("get status", client=client, role="reboot-poll")
            return is_data_response(doc)
        finally:
            await client.close()

    ok = await wait_until(back, cap.opts.reboot_wait, interval=3)
    elapsed = round(loop.time() - t0, 1)
    await cap.login(role="relogin")
    if cap.telnet is not None:
        await cap.reconnect_telnet()
    return {"back_online": ok, "seconds": elapsed}


async def _run_test(cap: Capture, item: _Planned) -> str:
    test = item.test
    con = cap.console
    con.print(f"- {test.id}: {test.title}")
    await cap.ensure_session()
    before = await cap.snapshot(with_lcd=test.with_lcd)
    record: dict[str, Any] = {"title": test.title, "group": test.group, "answers": list(test.answers),
                              "before": before.to_dict(), "steps": []}
    status0 = await cap.telnet_status() if any(s.status_text for s in item.steps) else None
    prev = before
    verdicts: list[str] = []
    try:
        for index, step in enumerate(item.steps):
            if cap.telnet is not None:
                await cap.telnet.drain_unsolicited()
            ex = await _send(cap, step)
            entry: dict[str, Any] = {"describe": step.describe, "kind": step.kind, "exchange": ex}
            if step.reboot:
                entry["reboot"] = await _wait_for_reboot(cap)
            if cap.telnet is not None and cap.telnet.connected:
                pushes = await cap.telnet.drain_unsolicited(cap.opts.push_grace)
                if pushes:
                    entry["pushes"] = pushes
            now = await cap.snapshot(with_lcd=test.with_lcd)
            changes = diff(prev, now)
            entry["diff"] = changes
            if step.kind in ("write",):
                ok = step.expect(prev, now) if step.expect else bool(changes)
                outcome = "applied" if ok else "not-applied"
            elif step.kind == "invalid":
                outcome = "rejected" if not changes else "accepted-invalid"
            elif step.kind == "read":
                outcome = "data" if is_data_response((ex.get("response") or {}).get("json")) else "no-data"
            else:
                outcome = "sent"
            ex["outcome"] = outcome
            entry["outcome"] = outcome
            if step.status_text or step.lcd_mode is not None:
                status = await cap.telnet_status()
                if status is not None:
                    entry["status_changes"] = status_changes(status0 or "", status)
                    if step.lcd_mode is not None:
                        line = lcd_line(status)
                        entry["lcd_line"] = line
                        if line and (ex.get("response") or {}).get("status") == 200:
                            cap.lcd_modes.setdefault(line, step.lcd_mode)
            if step.ask:
                note = con.ask(step.ask)
                if note:
                    entry["operator_note"] = note
            record["steps"].append(entry)
            result = ((ex.get("response") or {}).get("json") or {}) if step.channel == "http" else None
            shown = result.get("result") if isinstance(result, dict) else (
                ((ex.get("response") or {}).get("analysis") or {}).get("last_line"))
            con.print(f"    {step.describe:<58} -> {outcome:<16} result={shown!r}")
            verdicts.append(outcome)
            prev = now
            if cap.after_step is not None:
                maybe = cap.after_step(test.id, index)
                if asyncio.iscoroutine(maybe):
                    await maybe
    except Exception as exc:  # noqa: BLE001 - record, restore, continue with the next test
        record["error"] = {"type": type(exc).__name__, "message": str(exc)}
        cap.errors.append(f"{test.id}: {type(exc).__name__}: {exc}")
        con.print(f"    ERROR {type(exc).__name__}: {exc}")
        verdicts.append("error")
    finally:
        remaining, _ = await _run_to_completion(cap.restore_to(before, reason=f"after {test.id}"))
        record["restored"] = not remaining
        record["restore_remaining"] = remaining
        record["findings"] = _findings(test, record)
        cap.add(RecordIds.write(test.id), record)
        con.print(f"    restored: {'yes' if not remaining else 'NO ' + str(remaining)}")
    if remaining:
        raise RestoreError(f"{test.id}: could not restore {remaining}")
    return ", ".join(verdicts)


def _findings(test: WriteTest, record: dict[str, Any]) -> dict[str, Any]:
    """Per-test facts the golden report reads (result codes by outcome, maps)."""
    results: dict[str, list[Any]] = {}
    for step in record["steps"]:
        ex = step["exchange"]
        resp = ex.get("response") or {}
        if ex.get("kind") == "http":
            doc = resp.get("json")
            value = doc.get("result") if isinstance(doc, dict) else (resp.get("body_text") or ex.get("error"))
        else:
            value = (resp.get("analysis") or {}).get("last_line")
        results.setdefault(step["outcome"], [])
        if value not in results[step["outcome"]]:
            results[step["outcome"]].append(value)
    findings: dict[str, Any] = {"results_by_outcome": results}
    if test.id == "http_lcd":
        findings["lcd_lines"] = {str(s["exchange"]["request"]["json"]["time"]): s.get("lcd_line")
                                 for s in record["steps"] if s["kind"] == "write"}
    if test.id in ("http_input_name", "http_output_name"):
        for s in record["steps"]:
            payload = s["exchange"]["request"]["json"]
            if payload.get("name") == LONG_NAME:
                field_name = "input_names" if test.id == "http_input_name" else "output_names"
                stored = [d[3] for d in s["diff"] if d[0] == field_name]
                findings["long_name_sent_len"] = len(LONG_NAME)
                findings["long_name_stored"] = stored[0] if stored else None
                findings["long_name_stored_len"] = len(stored[0]) if stored and isinstance(stored[0], str) else None
    if test.id in ("http_input_edid", "http_copy_edid"):
        findings["edid_steps"] = [
            {"payload": s["exchange"]["request"]["json"], "outcome": s["outcome"],
             "edid_after": [d for d in s["diff"] if d[0] == "edid"]}
            for s in record["steps"]
        ]
    if test.group == "output":
        findings["status_text"] = {
            str(next(v for k, v in s["exchange"]["request"]["json"].items() if k not in ("comhead", "output"))):
                s.get("status_changes", {}).get("added")
            for s in record["steps"] if s["kind"] == "write"
        }
    return findings
