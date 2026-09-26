"""``--mode write`` (DANGEROUS): every write command, verified and restored.

Each test is a list of :class:`Step` built from the initial snapshot, so the
plan printed before anything is sent shows every exact command. For each test:

1. snapshot the device;
2. run the steps: send, wait for pushes, snapshot again, compare;
3. restore the pre-test snapshot (``finally``: also on errors and Ctrl+C) and
   verify it with another snapshot.

After the last test (or an abort) the initial snapshot is restored once more.
Every restore write is appended to ``write/restore-log.jsonl`` immediately.

The per-output, EDID, LCD, ext-audio and preset tests send the commands the
hub sends since WP-A4 part 2 (the device web interface's commands) and read
each setting back from the status reads: ``get output status``
(``allout``/``allhdcp``/``allhdr``/``allscaler``/``allarc``/``allaudiomute``),
``get input status.edid``, ``get system status.mode`` (LCD),
``get ext-audio status`` (``mode``/``allout``/``allsource``/``index``),
``get video status.allname`` (preset names) and Telnet ``r preset N``. The
``legacy`` group sends each command the old hub used once, as evidence that
the firmware ignores it (HIL-09); skip it with ``--skip legacy``.
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
    #: read (a read, e.g. during standby), noop (same value), cec (no readback),
    #: unanswered (a legacy command the firmware is expected to ignore)
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
    #: read the test preset over Telnet in every snapshot of this test
    with_presets: bool = False


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


def _preset(now: Snapshot, p: int) -> dict[str, Any]:
    presets = now.presets or [None] * 8
    return presets[p - 1] or {}


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
    """Save a known routing into P, move away from it, recall it (readback: routing and ``r preset P``)."""
    p, t = o.test_preset, o.test_output
    routing = _need(s.routing, "routing")
    slot = _need(_preset(s, p) or None, f"preset {p} (Telnet r preset {p})")
    new = _other(routing[t - 1], o.test_input)
    away = _other(new, routing[t - 1])
    saved = list(routing)
    saved[t - 1] = new
    steps = []
    if not slot.get("saved"):
        steps.append(_http(cmd.preset_set(p), f"recall preset {p} while it is empty (expected: result 0)",
                           kind="invalid"))
    steps += [
        _http(cmd.video_switch(t, new), f"stage: output {t} -> input {new}", expect=_at("routing", t, new)),
        _http(cmd.preset_save(p), f"stage: save preset {p}", expect=lambda prev, now: _preset(now, p).get("routing") == saved),
        _http(cmd.video_switch(t, away), f"stage: output {t} -> input {away}", expect=_at("routing", t, away)),
        _http(cmd.preset_set(p), f"recall preset {p} (routing -> {saved}, ALL outputs)",
              expect=lambda prev, now: now.routing == saved),
        _http(cmd.preset_set(9), "invalid preset 9", kind="invalid"),
        _http(cmd.preset_set(0), "invalid preset 0", kind="invalid"),
    ]
    return steps


def _preset_save(s: Snapshot, o: Options) -> list[Step]:
    p, t = o.test_preset, o.test_output
    routing = _need(s.routing, "routing")
    slot = _need(_preset(s, p) or None, f"preset {p} (Telnet r preset {p})")
    current = (slot.get("routing") or [None] * 8)[t - 1]
    new = _other(routing[t - 1], o.test_input, avoid=(current,) if current else ())
    return [
        _http(cmd.video_switch(t, new), f"stage: output {t} -> input {new}", expect=_at("routing", t, new)),
        _http(cmd.preset_save(p), f"save live routing into preset {p} (overwrites it; restored afterwards)",
              expect=lambda prev, now: _preset(now, p).get("routing") == now.routing),
        _http(cmd.preset_save(9), "invalid preset 9", kind="invalid"),
    ]


def _preset_name(s: Snapshot, o: Options) -> list[Step]:
    p = o.test_preset
    names = _need(s.preset_names, "preset names (get video status.allname)")
    return [
        _http(cmd.preset_name(p, TEST_NAME), f"preset {p} name {names[p - 1]!r} -> {TEST_NAME!r}",
              expect=_at("preset_names", p, TEST_NAME)),
        _http(cmd.preset_name(p, LONG_NAME), f"preset {p} name -> {len(LONG_NAME)}-char name (truncation?)",
              expect=lambda prev, now: (now.preset_names or [None] * 8)[p - 1] != TEST_NAME),
        _http(cmd.preset_name(9, "HIL"), "invalid index 9", kind="invalid"),
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


def _output_setting(setting: str, bad: tuple[int, ...]) -> Callable[[Snapshot, Options], list[Step]]:
    """Every device code of one per-output setting on T, read back from ``get output status``."""
    lo, hi = cmd.OUTPUT_RANGES[setting]

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


def _set_edid(s: Snapshot, o: Options) -> list[Step]:
    """``set edid``: a built-in EDID, copy from output 1 (id 40), back; readback ``get input status.edid``."""
    i = o.test_input
    edid = _need(s.edid, "EDID")
    first = _other(edid[i - 1], 36, 1, 36)
    copy1 = cmd.EDID_COPY_BASE + 1
    return [
        _http(cmd.set_edid(i, first), f"input {i} EDID {edid[i - 1]} -> {first}", expect=_at("edid", i, first)),
        _http(cmd.set_edid(i, copy1), f"input {i} EDID -> {copy1} (copy from output 1, BE-25)",
              expect=_at("edid", i, copy1)),
        _http(cmd.set_edid(i, edid[i - 1]), f"input {i} EDID -> {edid[i - 1]} (back to the original)",
              expect=_at("edid", i, edid[i - 1])),
        _http(cmd.set_edid(i, 0), "invalid EDID 0", kind="invalid"),
        _http(cmd.set_edid(i, 48), "invalid EDID 48", kind="invalid"),
        _http(cmd.set_edid(9, 1), "invalid input 9", kind="invalid"),
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
    """The old hub's single-port ``set cec index``: rejected on V1.10.01 (BE-13, HIL-10)."""
    i, t = o.test_input, o.test_output
    cin, cout = _need(s.cec_in, "CEC input enable"), _need(s.cec_out, "CEC output enable")
    vi, vo = 0 if cin[i - 1] else 1, 0 if cout[t - 1] else 1
    return [
        _http(cmd.cec_index_single("input", i, vi), f"old single-port shape: CEC input {i} -> {vi} (expected: result 0)",
              kind="invalid"),
        _http(cmd.cec_index_single("output", t, vo),
              f"old single-port shape: CEC output {t} -> {vo} (expected: result 0)", kind="invalid"),
    ]


def _cec_invalid(s: Snapshot, o: Options) -> list[Step]:
    i = o.test_input
    return [
        _http(cmd.cec_command(0, i, 99), "cec command index 99", kind="invalid"),
        _http(cmd.cec_command(0, 0, 1), "cec command with no target port", kind="invalid"),
        _http(cmd.cec_command(2, i, 1), "cec command object 2", kind="invalid"),
    ]


#: The output (display) CEC table of the device web interface (BE-14).
_CEC_OUTPUT_INDEX = {"on": 0, "off": 1, "mute": 2, "vol-": 3, "vol+": 4, "active": 5}


def _cec_live(s: Snapshot, o: Options) -> list[Step]:
    port = o.cec_output
    q = f"What did the display on output {port} do? (Enter = nothing) "
    words = sorted((set(_CEC_WORDS) | {"active"}) - {"on", "off"}) + ["off", "on"]
    steps = [_telnet(f"s cec hdmi out {port} {w}", f"Telnet CEC '{w}' to output {port}", kind="cec", ask=q)
             for w in words]
    order = ["mute", "mute", "vol-", "vol+", "active", "off", "on"]
    steps += [_http(cmd.cec_command(1, port, _CEC_OUTPUT_INDEX[w]),
                    f"HTTP cec command object 1 index {_CEC_OUTPUT_INDEX[w]} ({w}) to output {port}", kind="cec", ask=q)
              for w in order]
    return steps


_CEC_WORDS = ("menu", "back", "up", "down", "left", "right", "enter", "play", "pause", "stop", "previous", "next",
              "rew", "ff", "vol+", "vol-", "mute", "on", "off")


def _exa_mode(s: Snapshot, o: Options) -> list[Step]:
    mode = _need(s.exa_mode, "ext-audio mode")
    steps = [_http(cmd.exa_mode(m), f"ext-audio mode -> {m}", expect=_scalar("exa_mode", m)) for m in _cycle(mode, 0, 2)]
    steps.append(_http(cmd.exa_mode(3), "invalid mode 3", kind="invalid"))
    return steps


def _exa_out(s: Snapshot, o: Options) -> list[Step]:
    t = o.test_output
    en = _need(s.exa_enable, "ext-audio enable")
    new = 0 if en[t - 1] else 1
    return [
        _http(cmd.exa_out(t, new), f"ext-audio output {t} enable {en[t - 1]} -> {new}", expect=_at("exa_enable", t, new)),
        _http(cmd.exa_out(t, en[t - 1]), f"ext-audio output {t} enable -> {en[t - 1]} (back to the original)",
              expect=_at("exa_enable", t, en[t - 1])),
        _http(cmd.exa_out(9, 1), "invalid output 9", kind="invalid"),
        _http(cmd.exa_out(t, 2), "invalid value 2", kind="invalid"),
    ]


def _exa_switch(s: Snapshot, o: Options) -> list[Step]:
    """``ext-audio switch`` in matrix mode (the only mode the device web interface offers it in)."""
    t = o.test_output
    mode = _need(s.exa_mode, "ext-audio mode")
    src = _need(s.exa_source, "ext-audio source")
    new = _other(src[t - 1], o.test_input)
    steps = []
    if mode != 2:
        steps.append(_http(cmd.exa_mode(2), "stage: ext-audio mode -> 2 (matrix)", expect=_scalar("exa_mode", 2)))
    steps += [
        _http(cmd.exa_switch(t, new), f"ext-audio output {t} source {src[t - 1]} -> input {new}",
              expect=_at("exa_source", t, new)),
        _http(cmd.exa_switch(t, 16), f"ext-audio output {t} source -> 16 (ARC of output 8)",
              expect=_at("exa_source", t, 16)),
        _http(cmd.exa_switch(t, 17), "invalid source 17", kind="invalid"),
        _http(cmd.exa_switch(9, 1), "invalid output 9", kind="invalid"),
    ]
    return steps


def _exa_index(s: Snapshot, o: Options) -> list[Step]:
    t = o.test_output
    index = _need(s.exa_index, "ext-audio index")
    new = _other(index, t)
    return [
        _http(cmd.exa_index(new), f"ext-audio selected output {index} -> {new}", expect=_scalar("exa_index", new)),
        _http(cmd.exa_index(9), "invalid index 9", kind="invalid"),
    ]


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
    """Every LCD code, read back from ``get system status.mode`` and the Telnet ``lcd`` line."""
    mode = _need(s.lcd, "LCD code (get system status.mode)")
    steps = [_http(cmd.lcd_time(m), f"LCD on time -> code {m}" + (" (back to the original)" if m == mode else ""),
                   expect=_scalar("lcd", m), status_text=True, lcd_mode=m) for m in _cycle(mode, 0, 4)]
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
    new_all = _other(routing[0], o.test_input)
    return [
        _telnet(f"s output {t} in source {new}", f"output {t} -> input {new} (hub syntax)",
                expect=_at("routing", t, new)),
        _telnet(f"s output 0 in source {new_all}", f"ALL outputs -> input {new_all}",
                expect=lambda p, n: n.routing == [new_all] * 8),
    ]


def _telnet_presets(s: Snapshot, o: Options) -> list[Step]:
    """Hub (and vendor) preset syntax, read back with ``r preset P``."""
    p, t = o.test_preset, o.test_output
    routing = _need(s.routing, "routing")
    _need(_preset(s, p) or None, f"preset {p} (Telnet r preset {p})")
    new = _other(routing[t - 1], o.test_input)
    away = _other(new, routing[t - 1])
    saved: Expect = lambda prev, now: _preset(now, p).get("routing") == now.routing  # noqa: E731
    return [
        _http(cmd.video_switch(t, new), f"stage: output {t} -> input {new}", expect=_at("routing", t, new)),
        _telnet(f"s save preset {p}", f"save preset {p} (hub syntax)", expect=saved),
        _http(cmd.video_switch(t, away), f"stage: output {t} -> input {away}", expect=_at("routing", t, away)),
        _telnet(f"s recall preset {p}", f"recall preset {p} (hub syntax; ALL outputs)",
                expect=lambda prev, now: now.routing == _preset(prev, p).get("routing")),
        _telnet(f"s clear preset {p}", f"clear preset {p} (hub syntax)",
                expect=lambda prev, now: _preset(now, p) != _preset(prev, p)),
        _http(cmd.video_switch(t, away), f"stage: output {t} -> input {away}"),
        _telnet(f"s preset save {p}", f"save preset {p} (vendor syntax)", expect=saved),
        _http(cmd.video_switch(t, new), f"stage: output {t} -> input {new}"),
        _telnet(f"s preset recall {p}", f"recall preset {p} (vendor syntax)",
                expect=lambda prev, now: now.routing == _preset(prev, p).get("routing")),
    ]


def _telnet_system(s: Snapshot, o: Options) -> list[Step]:
    steps = []
    if s.beep is not None:
        steps.append(_telnet(f"s beep {0 if s.beep else 1}", "beep toggle", expect=_scalar("beep", 0 if s.beep else 1)))
    if s.lock is not None:
        steps.append(_telnet(f"s lock {0 if s.lock else 1}", "panel lock toggle",
                             expect=_scalar("lock", 0 if s.lock else 1)))
    if not steps:
        raise SkipTestError("system state could not be read")
    return steps


def _legacy_http(s: Snapshot, o: Options) -> list[Step]:
    """One step per comhead the old hub sent (HIL-09), with the current value: expected no answer, no change."""
    t, i = o.test_output, o.test_input
    steps = []
    for setting in cmd.LEGACY_OUTPUT_SETTINGS:
        values = getattr(s, setting)
        value = values[t - 1] if values else 1
        steps.append(_http(cmd.legacy_output_setting(setting, t, value),
                           f"old '{cmd.LEGACY_OUTPUT_SETTINGS[setting][0]}' (current value {value})", kind="unanswered"))
    edid = (s.edid or [36] * 8)[i - 1]
    steps.append(_http(cmd.legacy_input_edid(i, edid), f"old 'set input edid' (current value {edid})",
                       kind="unanswered"))
    steps.append(_http(cmd.legacy_copy_edid(i, 1), "documented 'copy edid' (BE-25)", kind="unanswered"))
    steps.append(_http(cmd.legacy_lcd_time(s.lcd if s.lcd is not None else 3),
                       "old 'set lcd on time' {\"time\": N} (captured: result 0)", kind="unanswered"))
    if s.exa_mode is not None:
        steps.append(_http(cmd.legacy_exa_mode(s.exa_mode), f"old 'set output exa mode' (current {s.exa_mode})",
                           kind="unanswered"))
    if s.exa_enable is not None:
        steps.append(_http(cmd.legacy_exa_enable(t, bool(s.exa_enable[t - 1])), "old 'set output exa' (current)",
                           kind="unanswered"))
    if s.exa_source is not None:
        steps.append(_http(cmd.legacy_exa_source(t, s.exa_source[t - 1]), "old 'set output exa in source' (current)",
                           kind="unanswered"))
    return steps


def _legacy_telnet(s: Snapshot, o: Options) -> list[Step]:
    """Vendor serial-reference commands V1.10.01 answers with E00 (captured); no-op values."""
    t = o.test_output
    routing = _need(s.routing, "routing")
    stream = (s.stream or [1] * 8)[t - 1]
    return [
        _telnet(f"s av {routing[t - 1]} {t}", f"vendor 's av {routing[t - 1]} {t}' (no-op; expected E00)",
                kind="unanswered"),
        _telnet(f"s out {t} stream {stream}", f"vendor 's out {t} stream {stream}' (no-op; expected E00, HIL-11)",
                kind="unanswered"),
    ]


def _reboot_http(s: Snapshot, o: Options) -> list[Step]:
    return [_http(cmd.reboot(), "REBOOT the matrix via HTTP (waits until it is back)", kind="write", reboot=True)]


def _reboot_telnet(s: Snapshot, o: Options) -> list[Step]:
    return [_telnet("reboot", "REBOOT the matrix via Telnet (waits until it is back)", kind="write", reboot=True)]


_WO = ("write-ok-results", "write-fail-result", "web-ui-commands")

TESTS: tuple[WriteTest, ...] = (
    WriteTest("http_video_switch", "routing", "Route one output",
              ("write-ok-results", "write-fail-result", "push-wording"), _routing),
    WriteTest("http_video_switch_all", "routing", "Route all outputs (output 0)", ("write-ok-results",), _routing_all),
    WriteTest("http_preset_recall", "presets", "Save a routing into the test preset, recall it (r preset readback)",
              ("write-ok-results", "write-fail-result", "preset-set-empty"), _preset_recall, needs_telnet=True,
              with_presets=True),
    WriteTest("http_preset_save", "presets", "Save a preset (r preset readback)",
              ("write-ok-results", "write-fail-result"), _preset_save, needs_telnet=True, with_presets=True),
    WriteTest("http_preset_name", "presets", "Rename a preset (preset name; get video status.allname readback)",
              _WO + ("name-truncation",), _preset_name),
    WriteTest("http_input_name", "names", "Rename an input",
              ("write-ok-results", "write-fail-result", "name-truncation"),
              lambda s, o: _name_steps("input", o.test_input, s)),
    WriteTest("http_output_name", "names", "Rename an output",
              ("write-ok-results", "write-fail-result", "name-truncation"),
              lambda s, o: _name_steps("output", o.test_output, s)),
    WriteTest("http_tx_stream", "output", "Output stream on/off (tx stream; allout)", _WO,
              _output_setting("stream", (2,))),
    WriteTest("http_tx_hdcp", "output", "Output HDCP, every code (tx hdcp; allhdcp)", _WO + ("output-mode-text",),
              _output_setting("hdcp", (0, 6))),
    WriteTest("http_hdr_conversion", "output", "Output HDR conversion, every code (set hdr conversion; allhdr, HIL-02)",
              _WO + ("output-mode-text",), _output_setting("hdr", (3,))),
    WriteTest("http_video_scaler", "output", "Output video mode, every code (set video scaler; allscaler, BE-15)",
              _WO + ("output-mode-text",), _output_setting("scaler", (5,))),
    WriteTest("http_arc", "output", "Output ARC (set arc; allarc)", _WO, _output_setting("arc", (2,))),
    WriteTest("http_output_audio_mute", "output", "Output audio mute (set output audio mute; allaudiomute)", _WO,
              _output_setting("mute", (2,))),
    WriteTest("http_set_edid", "edid", "Input EDID incl. copy from output 1 (set edid; edid, BE-25)",
              _WO + ("edid-range", "copy-edid"), _set_edid),
    WriteTest("http_cec_index_bulk", "cec-enable", "CEC enable, 8-element array shape",
              ("write-ok-results", "write-fail-result"), _cec_bulk),
    WriteTest("http_cec_index_single", "cec-enable", "CEC enable, old single-port shape (BE-13; expected rejected)",
              ("write-fail-result", "cec-index-single-port"), _cec_single),
    WriteTest("http_cec_command_invalid", "cec-invalid", "CEC command with invalid parameters",
              ("write-fail-result",), _cec_invalid),
    WriteTest("http_ext_audio_mode", "ext-audio", "Ext-audio mode (set ext-audio mode; mode)",
              _WO + ("exa-commands",), _exa_mode),
    WriteTest("http_ext_audio_out", "ext-audio", "Ext-audio output enable (set ext-audio out; allout)",
              _WO + ("exa-commands",), _exa_out),
    WriteTest("http_ext_audio_switch", "ext-audio", "Ext-audio source in matrix mode (ext-audio switch; allsource)",
              _WO + ("exa-commands",), _exa_switch),
    WriteTest("http_ext_audio_index", "ext-audio", "Ext-audio selected output (set ext-audio index; index)",
              _WO + ("exa-commands", "ext-audio-index"), _exa_index),
    WriteTest("http_beep", "system", "Beep", ("write-ok-results", "write-fail-result"), _flag("beep", cmd.beep)),
    WriteTest("http_panel_lock", "system", "Front-panel lock", ("write-ok-results", "write-fail-result"),
              _flag("lock", cmd.panel_lock)),
    WriteTest("http_lcd_on_time", "system", "LCD on time, every code (set lcd on time; mode, API-07)",
              _WO + ("lcd-codes",), _lcd, with_lcd=True),
    WriteTest("telnet_routing", "telnet", "Telnet routing commands", ("telnet-set-acks", "push-wording"),
              _telnet_routing, needs_telnet=True),
    WriteTest("telnet_presets", "telnet", "Telnet preset commands (r preset readback)", ("telnet-set-acks",),
              _telnet_presets, needs_telnet=True, with_presets=True),
    WriteTest("telnet_system", "telnet", "Telnet beep / lock", ("telnet-set-acks",), _telnet_system,
              needs_telnet=True),
    WriteTest("http_power", "power", "Standby and power on; commands in standby",
              ("write-ok-results", "write-fail-result", "standby-behaviour"), _power),
    WriteTest("telnet_power_bare", "power", "Telnet 'power N' (what TelnetClient sends)",
              ("telnet-bare-power", "telnet-set-acks"), _telnet_power(""), needs_telnet=True),
    WriteTest("telnet_power_s", "power", "Telnet 's power N' (vendor syntax; expected E01)",
              ("telnet-bare-power", "telnet-set-acks"), _telnet_power("s "), needs_telnet=True),
    WriteTest("http_legacy_commands", "legacy", "Old hub commands (HIL-09; expected: no answer, no change)",
              ("legacy-unanswered", "unknown-comhead-result"), _legacy_http),
    WriteTest("telnet_legacy_commands", "legacy", "Vendor Telnet commands V1.10.01 lacks (expected E00)",
              ("telnet-error-codes", "telnet-set-acks"), _legacy_telnet, needs_telnet=True),
    WriteTest("cec_live_output", "cec-live", "Live CEC to the display on --cec-output (BE-14)",
              ("telnet-cec-output-words", "cec-disabled-port", "write-ok-results"), _cec_live, needs_telnet=True),
    WriteTest("http_reboot", "reboot", "Reboot via HTTP (reboot)", ("reboot-replies-first",), _reboot_http),
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
    slots = _preset_slots(cap)
    initial = await cap.snapshot(with_lcd=cap.telnet is not None, preset_slots=slots)
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
        final = await cap.snapshot(with_lcd=cap.telnet is not None, preset_slots=slots)
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


def _preset_slots(cap: Capture) -> tuple[int, ...]:
    """The test preset, if a selected test reads presets (Telnet ``r preset``)."""
    if cap.telnet is None or not any(t.with_presets for t in select_tests(cap.opts)):
        return ()
    return (cap.opts.test_preset,)


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
            "cec": "write-cec", "unanswered": "write-legacy"}[step.kind]
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
    slots = (cap.opts.test_preset,) if test.with_presets and cap.telnet is not None else ()
    before = await cap.snapshot(with_lcd=test.with_lcd, preset_slots=slots)
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
            now = await cap.snapshot(with_lcd=test.with_lcd, preset_slots=slots)
            changes = diff(prev, now)
            entry["diff"] = changes
            if step.kind in ("write",):
                ok = step.expect(prev, now) if step.expect else bool(changes)
                outcome = "applied" if ok else "not-applied"
            elif step.kind == "invalid":
                outcome = "rejected" if not changes else "accepted-invalid"
            elif step.kind == "unanswered":
                outcome = _legacy_outcome(ex, changes)
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


def _legacy_outcome(ex: dict[str, Any], changes: list[list[Any]]) -> str:
    """unanswered (the firmware ignored it), rejected (an error answer) or answered; "changed" if state moved."""
    if changes:
        return "changed"
    if ex.get("kind") == "http":
        if (ex.get("error") or {}).get("type") == "TimeoutError" and not ex.get("response"):
            return "unanswered"
        doc = (ex.get("response") or {}).get("json")
        return "rejected" if isinstance(doc, dict) and doc.get("result") in (0, "0") else "answered"
    analysis = (ex.get("response") or {}).get("analysis") or {}
    return "rejected" if analysis.get("error_codes_seen") else "answered"


def _payload_value(payload: dict[str, Any]) -> Any:
    """The value of a write payload (``[port, value]`` pairs give the value)."""
    for key, value in payload.items():
        if key in ("comhead", "language", "output"):
            continue
        return value[1] if isinstance(value, list) and len(value) == 2 else value
    return None


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
    if test.id == "http_lcd_on_time":
        steps = [s for s in record["steps"] if s["kind"] == "write"]
        findings["lcd_lines"] = {str(s["exchange"]["request"]["json"]["lcd on time"]): s.get("lcd_line")
                                 for s in steps if s["outcome"] == "applied"}
        findings["lcd_outcomes"] = {str(s["exchange"]["request"]["json"]["lcd on time"]): s["outcome"] for s in steps}
    if test.id in ("http_input_name", "http_output_name", "http_preset_name"):
        for s in record["steps"]:
            payload = s["exchange"]["request"]["json"]
            if payload.get("name") == LONG_NAME:
                field_name = {"http_input_name": "input_names", "http_output_name": "output_names",
                              "http_preset_name": "preset_names"}[test.id]
                stored = [d[3] for d in s["diff"] if d[0] == field_name]
                findings["long_name_sent_len"] = len(LONG_NAME)
                findings["long_name_stored"] = stored[0] if stored else None
                findings["long_name_stored_len"] = len(stored[0]) if stored and isinstance(stored[0], str) else None
    if test.id == "http_set_edid":
        findings["edid_steps"] = [
            {"payload": s["exchange"]["request"]["json"], "outcome": s["outcome"],
             "edid_after": [d for d in s["diff"] if d[0] == "edid"]}
            for s in record["steps"]
        ]
    if test.group == "output":
        findings["status_text"] = {
            str(_payload_value(s["exchange"]["request"]["json"])): s.get("status_changes", {}).get("added")
            for s in record["steps"] if s["kind"] == "write"
        }
    if test.group == "legacy":
        findings["legacy"] = [
            {"command": s["exchange"]["request"]["json"].get("comhead") if s["exchange"].get("kind") == "http"
             else s["exchange"].get("command"), "outcome": s["outcome"]}
            for s in record["steps"]
        ]
    return findings
