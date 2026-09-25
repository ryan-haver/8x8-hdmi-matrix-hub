"""JSON command handlers for ``POST /cgi-bin/instr``.

Pure functions over :class:`~tools.simulator.state.DeviceState`: no I/O, no
sessions, no faults (those live in :mod:`tools.simulator.server`). Each handler
takes the parsed request payload and returns the response document.

Reads have the key sets and key order captured on MCU V1.10.01. Writes are
the commands the device's own web interface sends (``{"comhead": ...,
"language": 0, <key>: [port, value]}``, port 0 = all outputs): the captured
ones are byte-exact, the others are web-UI-derived until a write capture
proves them (marked ``ASSUMPTION(HIL-A)``). A comhead with no handler is never
answered, like on the device (HIL-09/HIL-12): :func:`dispatch` flags it
``unanswered`` and the server holds the request open.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from . import protocol as proto
from .state import NINTH_KEYS, DeviceState

Payload = dict[str, Any]


@dataclass
class CommandResult:
    """Outcome of one JSON command."""

    response: dict[str, Any]
    recognised: bool = True
    mutated: bool = False
    reboot: bool = False
    #: the device does not answer this command at all (unknown comhead)
    unanswered: bool = False
    warnings: list[str] = field(default_factory=list)


class _RejectError(Exception):
    """Invalid parameters: answer with RESULT_FAIL."""


Handler = Callable[[DeviceState, Payload, CommandResult], dict[str, Any]]
HANDLERS: dict[str, Handler] = {}
#: comheads that only read state
READ_COMMANDS: set[str] = set()


def command(name: str, *, read: bool = False) -> Callable[[Handler], Handler]:
    def deco(fn: Handler) -> Handler:
        HANDLERS[name] = fn
        if read:
            READ_COMMANDS.add(name)
        return fn

    return deco


def dispatch(state: DeviceState, payload: Payload) -> CommandResult:
    """Run one command (login is handled by the server, not here)."""
    comhead = payload.get("comhead")
    result = CommandResult(response={})
    handler = HANDLERS.get(comhead) if isinstance(comhead, str) else None
    if handler is None:
        result.recognised = False
        result.unanswered = proto.UNKNOWN_COMMANDS_UNANSWERED
        result.response = {"comhead": comhead, "result": proto.UNKNOWN_COMMAND_RESULT}
        why = ("not implemented by MCU V1.10.01 (captured: no answer)"
               if comhead in proto.LEGACY_UNANSWERED_WRITES else "unknown comhead")
        result.warnings.append(why)
        return result
    try:
        body = handler(state, payload, result)
    except _RejectError as exc:
        result.warnings.append(f"rejected: {exc}")
        result.mutated = False
        return CommandResult(
            response={"comhead": comhead, "result": proto.RESULT_FAIL},
            warnings=result.warnings,
        )
    result.response = {"comhead": comhead, **body}
    return result


# --------------------------------------------------------------------- utils


def _int(payload: Payload, key: str, lo: int, hi: int) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
        raise _RejectError(f"{key}={value!r} not in {lo}..{hi}")
    return value


def _port_value(payload: Payload, key: str, ports: tuple[int, int], values: tuple[int, int]) -> tuple[int, int]:
    """``key: [port, value]`` of the web-interface write commands."""
    pair = payload.get(key)
    if not isinstance(pair, list) or len(pair) != 2:
        raise _RejectError(f"{key}={pair!r} is not a [port, value] pair")
    port, value = pair
    for what, v, (lo, hi) in (("port", port, ports), ("value", value, values)):
        if isinstance(v, bool) or not isinstance(v, int) or not lo <= v <= hi:
            raise _RejectError(f"{key} {what} {v!r} not in {lo}..{hi}")
    return port, value


def _port_array(payload: Payload, key: str) -> list[int]:
    value = payload.get(key)
    if not isinstance(value, list) or len(value) != proto.PORT_COUNT or any(v not in (0, 1) for v in value):
        raise _RejectError(f"{key}={value!r} is not an 8-element 0/1 array")
    return list(value)


def _name(payload: Payload) -> str:
    name = payload.get("name")
    if not isinstance(name, str):
        raise _RejectError(f"name={name!r}")
    # ASSUMPTION(HIL-A): names are stored as sent up to protocol.NAME_MAX
    # characters. V1.10.01 kept a 40-character name unchanged (captured); a
    # longer limit is unknown.
    return name[: proto.NAME_MAX]


def _ok(comhead: str) -> dict[str, Any]:
    return {"result": proto.WRITE_RESULT_OVERRIDES.get(comhead, proto.RESULT_OK)}


def _names(state: DeviceState) -> dict[str, Any]:
    return {
        "allinputname": state.column("inputs", "name"),
        "alloutputname": state.column("outputs", "name"),
    }


# ----------------------------------------------------------------- reads
#
# Every read below has the key set and key order the BK-808 sends on MCU
# V1.10.01 / web V2.00.03 (tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/
# http/). The server serialises them compactly and appends CR LF, so for the
# same state the body is byte-identical to the capture.


def _with_ninth(state: DeviceState, key: str) -> list[int]:
    """A per-output array plus the ninth ("all outputs") entry V1.10.01 appends (HIL-04)."""
    assert key in NINTH_KEYS
    return [*state.column("outputs", key), state.ninth(key)]


@command("get video status", read=True)
def _get_video_status(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # The names are 8 plain strings (no "IN01-" prefix). ``allsource`` has 9
    # entries (HIL-04). ``allname`` holds the preset names ("Out1".."Out8" on
    # the captured device; the web interface edits them with ``preset name``).
    return {
        "power": state.system["power"],
        "allsource": _with_ninth(state, "source"),
        **_names(state),
        "allname": [p.name for p in state.presets],
    }


@command("get output status", read=True)
def _get_output_status(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # The output names are in ``name``; the API doc's allinputname,
    # alloutputname and allsource are not sent. Every settings array has the
    # ninth entry (HIL-04); ``allconnect`` and ``name`` do not.
    return {
        "power": state.system["power"],
        "allconnect": state.column("outputs", "connected"),
        "name": state.column("outputs", "name"),
        "allscaler": _with_ninth(state, "scaler"),
        "allhdr": _with_ninth(state, "hdr"),
        "allhdcp": _with_ninth(state, "hdcp"),
        "allarc": _with_ninth(state, "arc"),
        "allout": _with_ninth(state, "stream"),
        "allaudiomute": _with_ninth(state, "audio_mute"),
    }


@command("get input status", read=True)
def _get_input_status(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    return {
        "power": state.system["power"],
        "edid": state.column("inputs", "edid"),
        # Despite the name, 1 = signal present (documented and relied on).
        "inactive": state.column("inputs", "signal"),
        "inname": state.column("inputs", "name"),
    }


@command("get cec status", read=True)
def _get_cec_status(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    return {
        "power": state.system["power"],
        **_names(state),
        "inputindex": state.column("inputs", "cec_enabled"),
        "outputindex": state.column("outputs", "cec_enabled"),
    }


@command("get system status", read=True)
def _get_system_status(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # ``baudrate`` is a code (6 = 115200); ``mode`` is the LCD on-time code
    # (3 = "lcd on 30 seconds" in the V1.10.01 capture; the device web
    # interface binds it to its LCD setting).
    s = state.system
    return {
        "power": s["power"],
        "baudrate": s["baudrate"],
        "beep": s["beep"],
        "lock": s["panel_lock"],
        "mode": s["lcd_timeout"],
    }


@command("get status", read=True)
def _get_status(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    d = state.device
    return {
        "power": state.system["power"],
        "version": d["firmware_version"],
        "hostname": d["hostname"],
        "ipaddress": d["ip_address"],
        "subnet": d["netmask"],
        "gateway": d["gateway"],
        "macaddress": d["mac_address"],
        "model": d["model"],
        "webversion": d["web_version"],
    }


@command("get network", read=True)
def _get_network(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # ``subnet``, not the API doc's ``netmask``. ``username`` is an integer
    # (1 on V1.10.01), not the login name.
    d = state.device
    return {
        "power": state.system["power"],
        "dhcp": d["dhcp"],
        "ipaddress": d["ip_address"],
        "subnet": d["netmask"],
        "gateway": d["gateway"],
        "telnetport": d["telnet_port"],
        "tcpport": d["tcp_port"],
        "macaddress": d["mac_address"],
        "hostname": d["hostname"],
        "username": d["network_username"],
        "model": d["model"],
    }


@command("get ext-audio status", read=True)
def _get_ext_audio_status(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    return {
        "power": state.system["power"],
        "mode": state.ext_audio["mode"],
        "allsource": state.column("outputs", "ext_audio_source"),
        "allout": state.column("outputs", "ext_audio_enabled"),
        **_names(state),
        # The audio output selected with ``set ext-audio index`` (the device
        # web interface's current audio output; 1 on the captured device).
        "index": state.ext_audio["index"],
    }


# ``get routing status`` is documented and ``preset get`` was sent by older hub
# code, but V1.10.01 never answers either (HIL-01). The server holds both open
# without an answer (protocol.UNANSWERED_COMHEADS); these handlers only keep
# the documented shape for reference.


@command("get routing status", read=True)
def _get_routing_status(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    return {
        "power": state.system["power"],
        "allpreset": [{"allsource": list(p.routing), "name": p.name} for p in state.presets],
    }


@command("preset get", read=True)
def _preset_get(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    idx = _int(payload, "index", 1, proto.PORT_COUNT)
    preset = state.presets[idx - 1]
    return {"index": idx, "name": preset.name, "allsource": list(preset.routing)}


# ---------------------------------------------------------------- writes
# Captured on V1.10.01: video switch, set poweronoff, set beep, set panel lock,
# set input name, set output name, set cec index, cec command, the rejection of
# the old ``set lcd on time`` payload.


@command("video switch")
def _video_switch(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    out, inp = _port_value(payload, "source", (0, proto.PORT_COUNT), (1, proto.PORT_COUNT))
    targets = state.outputs if out == 0 else [state.outputs[out - 1]]
    for o in targets:
        o.source = inp
    r.mutated = True
    return _ok("video switch")


@command("set poweronoff")
def _set_power(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # Captured: reads keep answering in standby (power 0), and writes are
    # still accepted.
    state.system["power"] = _int(payload, "power", 0, 1)
    r.mutated = True
    return _ok("set poweronoff")


@command("set beep")
def _set_beep(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    state.system["beep"] = _int(payload, "beep", 0, 1)
    r.mutated = True
    return _ok("set beep")


@command("set panel lock")
def _set_panel_lock(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    state.system["panel_lock"] = _int(payload, "lock", 0, 1)
    r.mutated = True
    return _ok("set panel lock")


@command("set input name")
def _set_input_name(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    idx = _int(payload, "index", 1, proto.PORT_COUNT)
    state.inputs[idx - 1].name = _name(payload)
    r.mutated = True
    return _ok("set input name")


@command("set output name")
def _set_output_name(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    idx = _int(payload, "index", 1, proto.PORT_COUNT)
    state.outputs[idx - 1].name = _name(payload)
    r.mutated = True
    return _ok("set output name")


@command("set cec index")
def _set_cec_index(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # Only the form with both 8-element arrays works (captured). The old hub's
    # single-port form ({"port": "input", "index": n, "enable": 0/1}) and a
    # short array are answered with result 0 and change nothing (BE-13, HIL-10).
    if "inputindex" not in payload and "outputindex" not in payload:
        raise _RejectError("single-port payload (BE-13): the device rejects it")
    inputs = _port_array(payload, "inputindex")
    outputs = _port_array(payload, "outputindex")
    for p, v in zip(state.inputs, inputs, strict=True):
        p.cec_enabled = v
    for o, v in zip(state.outputs, outputs, strict=True):
        o.cec_enabled = v
    r.mutated = True
    return _ok("set cec index")


@command("cec command")
def _cec_command(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # Captured: the device only validates ``object`` (2 -> result 0). Any
    # index and an empty port array are answered with result 1 (HIL-13: the
    # hub validates instead).
    obj = _int(payload, "object", *proto.CEC_OBJECT_RANGE)
    ports = payload.get("port")
    index = payload.get("index")
    if not isinstance(ports, list):
        r.warnings.append(f"port={ports!r} is not a port array")
        ports = []
    if not any(ports):
        r.warnings.append("no target port (the device accepts it anyway)")
    table_size = 6 if obj == 1 else 20
    if not isinstance(index, int) or not 0 <= index < table_size:
        r.warnings.append(f"index {index!r} is not in the {'output' if obj else 'input'} CEC table")
    # ASSUMPTION(HIL-A): commands are accepted even when CEC is disabled on the
    # target port (open question in the API doc); the log records whether it
    # was enabled so tests can assert on it.
    table = state.outputs if obj == 1 else state.inputs
    disabled = [i + 1 for i, v in enumerate(ports[: proto.PORT_COUNT]) if v and not table[i].cec_enabled]
    if disabled:
        r.warnings.append(f"CEC disabled on {'output' if obj else 'input'} port(s) {disabled}")
    return _ok("cec command")


@command("preset set")
def _preset_set(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    idx = _int(payload, "index", 1, proto.PORT_COUNT)
    preset = state.presets[idx - 1]
    # ASSUMPTION(HIL-A): recalling an empty slot is answered with result 0 (the
    # device web interface shows "Set failed, please save a preset" when
    # ``result`` is not 1).
    if not preset.saved:
        raise _RejectError(f"preset {idx} is empty")
    for o, src in zip(state.outputs, preset.routing, strict=True):
        o.source = src
    r.mutated = True
    return _ok("preset set")


@command("preset save")
def _preset_save(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    idx = _int(payload, "index", 1, proto.PORT_COUNT)
    state.presets[idx - 1].routing = state.routing
    state.presets[idx - 1].saved = True
    r.mutated = True
    return _ok("preset save")


# ------------------------------------------------ web-UI-derived writes
# The commands the device's own web interface sends (WP-A4 part 2). Payloads,
# value ranges and port 0 = all outputs come from that interface; the answers
# are the ASSUMPTION(HIL-A) in protocol.WRITE_RESULT_OVERRIDES.


@command("preset name")
def _preset_name(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    idx = _int(payload, "index", 1, proto.PORT_COUNT)
    state.presets[idx - 1].name = _name(payload)
    r.mutated = True
    return _ok("preset name")


@command("preset clear")
def _preset_clear(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    idx = _int(payload, "index", 1, proto.PORT_COUNT)
    state.presets[idx - 1].routing = list(range(1, proto.PORT_COUNT + 1))
    state.presets[idx - 1].saved = False
    r.mutated = True
    return _ok("preset clear")


def _output_setting(comhead: str, key: str, attr: str, lo: int, hi: int) -> None:
    """``{comhead, key: [output, value]}``; output 0 = all outputs."""

    def handler(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
        out, value = _port_value(payload, key, (0, proto.PORT_COUNT), (lo, hi))
        for o in state.outputs if out == 0 else [state.outputs[out - 1]]:
            setattr(o, attr, value)
        r.mutated = True
        return _ok(comhead)

    command(comhead)(handler)


_output_setting("tx stream", "out", "stream", 0, 1)
_output_setting("tx hdcp", "hdcp", "hdcp", *proto.HDCP_RANGE)
_output_setting("set hdr conversion", "hdr", "hdr", *proto.HDR_RANGE)
_output_setting("set video scaler", "scaler", "scaler", *proto.SCALER_RANGE)
_output_setting("set arc", "arc", "arc", 0, 1)
_output_setting("set output audio mute", "mute", "audio_mute", 0, 1)


@command("set edid")
def _set_edid(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # 1-36 built-in EDIDs, 37-39 user EDIDs, 40-47 copy the EDID of output
    # 1-8 (BE-25). The stored id is what ``get input status.edid`` reports.
    inp, edid = _port_value(payload, "edid", (1, proto.PORT_COUNT), proto.EDID_RANGE)
    state.inputs[inp - 1].edid = edid
    r.mutated = True
    return _ok("set edid")


@command("set lcd on time")
def _set_lcd(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # The value goes in a key named "lcd on time" (web interface); the old
    # hub's {"time": N} is rejected for every code (captured, API-07/HIL-09).
    if "lcd on time" not in payload:
        raise _RejectError("no 'lcd on time' value (the old {'time': N} payload is rejected)")
    state.system["lcd_timeout"] = _int(payload, "lcd on time", *proto.LCD_RANGE)
    r.mutated = True
    return _ok("set lcd on time")


@command("set ext-audio mode")
def _set_exa_mode(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    state.ext_audio["mode"] = _int(payload, "mode", *proto.EXT_AUDIO_MODE_RANGE)
    r.mutated = True
    return _ok("set ext-audio mode")


@command("set ext-audio out")
def _set_exa_out(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    out, enabled = _port_value(payload, "out", (1, proto.PORT_COUNT), (0, 1))
    state.outputs[out - 1].ext_audio_enabled = enabled
    r.mutated = True
    return _ok("set ext-audio out")


@command("set ext-audio index")
def _set_exa_index(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    state.ext_audio["index"] = _int(payload, "index", 1, proto.PORT_COUNT)
    r.mutated = True
    return _ok("set ext-audio index")


@command("ext-audio switch")
def _ext_audio_switch(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    out, source = _port_value(payload, "source", (1, proto.PORT_COUNT), proto.EXT_AUDIO_SOURCE_RANGE)
    state.outputs[out - 1].ext_audio_source = source
    if state.ext_audio["mode"] != 2:
        r.warnings.append("ext-audio switch outside matrix mode (the device web interface only offers it in mode 2)")
    r.mutated = True
    return _ok("ext-audio switch")


@command("reboot")
def _reboot(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    _int(payload, "reboot", 1, 1)
    r.reboot = True
    return _ok("reboot")


def recognised_comheads() -> set[str]:
    """Every comhead the simulator implements (plus ``login``)."""
    return set(HANDLERS) | {"login"}
