"""JSON command handlers for ``POST /cgi-bin/instr``.

Pure functions over :class:`~tools.simulator.state.DeviceState`: no I/O, no
sessions, no faults (those live in :mod:`tools.simulator.server`). Each handler
takes the parsed request payload and returns the response document.

Read responses use the exact key names ``src/orei_matrix.py`` parses and
``docs/OREI_API_COMMANDS.md`` documents. Every guess is marked
``ASSUMPTION(HIL-A)``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from . import protocol as proto
from .state import DeviceState

Payload = dict[str, Any]


@dataclass
class CommandResult:
    """Outcome of one JSON command."""

    response: dict[str, Any]
    recognised: bool = True
    mutated: bool = False
    reboot: bool = False
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
        result.response = {"comhead": comhead, "result": proto.UNKNOWN_COMMAND_RESULT}
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


def _port_array(payload: Payload, key: str) -> list[int]:
    value = payload.get(key)
    if not isinstance(value, list) or len(value) != proto.PORT_COUNT or any(v not in (0, 1) for v in value):
        raise _RejectError(f"{key}={value!r} is not an 8-element 0/1 array")
    return list(value)


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


def _with_ninth(values: list[int], state: DeviceState, key: str) -> list[int]:
    """A per-output array plus the ninth entry V1.10.01 appends (HIL-04)."""
    return [*values, state.ninth_output[key]]


@command("get video status", read=True)
def _get_video_status(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # Not in OREI_API_COMMANDS.md. The names are 8 plain strings (no "IN01-"
    # prefix). ``allsource`` has 9 entries (HIL-04). The hub reads ``allname``
    # as the preset names; V1.10.01 sends "Out1".."Out8" there.
    return {
        "power": state.system["power"],
        "allsource": _with_ninth(state.routing, state, "source"),
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
        "allscaler": _with_ninth(state.column("outputs", "scaler"), state, "scaler"),
        "allhdr": _with_ninth(state.column("outputs", "hdr"), state, "hdr"),
        "allhdcp": _with_ninth(state.column("outputs", "hdcp"), state, "hdcp"),
        "allarc": _with_ninth(state.column("outputs", "arc"), state, "arc"),
        "allout": _with_ninth(state.column("outputs", "stream"), state, "stream"),
        "allaudiomute": _with_ninth(state.column("outputs", "audio_mute"), state, "audio_mute"),
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
    # ``baudrate`` is a code (6 on V1.10.01), not bits per second; ``mode`` is
    # an undocumented code (3 on V1.10.01).
    s = state.system
    return {
        "power": s["power"],
        "baudrate": s["baudrate"],
        "beep": s["beep"],
        "lock": s["panel_lock"],
        "mode": s["mode"],
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
        # ASSUMPTION(HIL-A): meaning of "index" is unknown; the doc shows 1.
        "index": 1,
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


@command("video switch")
def _video_switch(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    source = payload.get("source")
    if not isinstance(source, list) or len(source) != 2:
        raise _RejectError(f"source={source!r}")
    out, inp = source
    if not isinstance(out, int) or not 0 <= out <= proto.PORT_COUNT:
        raise _RejectError(f"output {out!r}")
    if not isinstance(inp, int) or not 1 <= inp <= proto.PORT_COUNT:
        raise _RejectError(f"input {inp!r}")
    targets = state.outputs if out == 0 else [state.outputs[out - 1]]
    for o in targets:
        o.source = inp
    r.mutated = True
    return _ok("video switch")


@command("preset set")
def _preset_set(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    idx = _int(payload, "index", 1, proto.PORT_COUNT)
    for o, src in zip(state.outputs, state.presets[idx - 1].routing, strict=True):
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


@command("set poweronoff")
def _set_power(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # ASSUMPTION(HIL-A): other commands keep working while in standby; reads
    # simply report power 0.
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


@command("set lcd on time")
def _set_lcd(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    state.system["lcd_timeout"] = _int(payload, "time", *proto.LCD_RANGE)
    r.mutated = True
    return _ok("set lcd on time")


@command("set input name")
def _set_input_name(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    idx = _int(payload, "index", 1, proto.PORT_COUNT)
    name = payload.get("name")
    if not isinstance(name, str):
        raise _RejectError(f"name={name!r}")
    # ASSUMPTION(HIL-A): the device truncates to 32 characters like the hub does.
    state.inputs[idx - 1].name = name[:32]
    r.mutated = True
    return _ok("set input name")


@command("set output name")
def _set_output_name(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    idx = _int(payload, "index", 1, proto.PORT_COUNT)
    name = payload.get("name")
    if not isinstance(name, str):
        raise _RejectError(f"name={name!r}")
    state.outputs[idx - 1].name = name[:32]
    r.mutated = True
    return _ok("set output name")


def _output_setting(comhead: str, key: str, attr: str, lo: int, hi: int) -> None:
    def handler(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
        out = _int(payload, "output", 1, proto.PORT_COUNT)
        setattr(state.outputs[out - 1], attr, _int(payload, key, lo, hi))
        r.mutated = True
        return _ok(comhead)

    command(comhead)(handler)


_output_setting("set output stream", "enable", "stream", 0, 1)
_output_setting("set output hdcp", "hdcp", "hdcp", *proto.HDCP_RANGE)
_output_setting("set output hdr", "hdr", "hdr", *proto.HDR_RANGE)
_output_setting("set output scaler", "scaler", "scaler", *proto.SCALER_RANGE)
_output_setting("set output arc", "arc", "arc", 0, 1)
_output_setting("set output mute", "mute", "audio_mute", 0, 1)


@command("set input edid")
def _set_input_edid(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    inp = _int(payload, "input", 1, proto.PORT_COUNT)
    state.inputs[inp - 1].edid = _int(payload, "edid", *proto.EDID_RANGE)
    r.mutated = True
    return _ok("set input edid")


@command("copy edid")
def _copy_edid(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # Documented, not sent by the hub (it uses "set input edid" 14+N, BE-25).
    # ASSUMPTION(HIL-A): equivalent to EDID mode 14 + output.
    inp = _int(payload, "input", 1, proto.PORT_COUNT)
    out = _int(payload, "output", 1, proto.PORT_COUNT)
    state.inputs[inp - 1].edid = 14 + out
    r.mutated = True
    return _ok("copy edid")


@command("set cec index")
def _set_cec_index(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    if "inputindex" in payload or "outputindex" in payload:
        # Documented shape: full 8-element arrays for both port types.
        inputs = _port_array(payload, "inputindex")
        outputs = _port_array(payload, "outputindex")
        for p, v in zip(state.inputs, inputs, strict=True):
            p.cec_enabled = v
        for o, v in zip(state.outputs, outputs, strict=True):
            o.cec_enabled = v
    else:
        # ASSUMPTION(HIL-A): the single-port shape sent by
        # OreiMatrix.set_cec_enable ({"port": "input", "index": n, "enable": 0/1},
        # orei_matrix.py:1915, BE-13) is accepted so the web UI works, but it
        # is undocumented and flagged in the command log.
        r.warnings.append("undocumented 'set cec index' single-port payload (BE-13)")
        port_type = payload.get("port")
        if port_type not in ("input", "output"):
            raise _RejectError(f"port={port_type!r}")
        idx = _int(payload, "index", 1, proto.PORT_COUNT)
        enable = _int(payload, "enable", 0, 1)
        ports = state.inputs if port_type == "input" else state.outputs
        ports[idx - 1].cec_enabled = enable
    r.mutated = True
    return _ok("set cec index")


@command("cec command")
def _cec_command(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    obj = _int(payload, "object", 0, 1)
    ports = _port_array(payload, "port")
    _int(payload, "index", *proto.CEC_INDEX_RANGE)  # validated only
    if not any(ports):
        raise _RejectError("no target port")
    # ASSUMPTION(HIL-A): commands are accepted even when CEC is disabled on the
    # target port (open question in the API doc); the log records whether it
    # was enabled so tests can assert on it.
    table = state.outputs if obj == 1 else state.inputs
    disabled = [i + 1 for i, v in enumerate(ports) if v and not table[i].cec_enabled]
    if disabled:
        r.warnings.append(f"CEC disabled on {'output' if obj else 'input'} port(s) {disabled}")
    return _ok("cec command")


@command("set output exa mode")
def _set_exa_mode(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # ASSUMPTION(HIL-A): comhead and payload taken from the hub (derived from
    # the Control4 driver); never verified over HTTP.
    state.ext_audio["mode"] = _int(payload, "mode", *proto.EXT_AUDIO_MODE_RANGE)
    r.mutated = True
    return _ok("set output exa mode")


@command("set output exa")
def _set_exa(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    # ASSUMPTION(HIL-A): exa 1 = enable, 2 = disable (hub comment, Control4 driver).
    out = _int(payload, "output", 1, proto.PORT_COUNT)
    exa = _int(payload, "exa", 1, 2)
    state.outputs[out - 1].ext_audio_enabled = 1 if exa == 1 else 0
    r.mutated = True
    return _ok("set output exa")


@command("set output exa in source")
def _set_exa_source(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    out = _int(payload, "output", 1, proto.PORT_COUNT)
    state.outputs[out - 1].ext_audio_source = _int(payload, "input", 1, proto.PORT_COUNT)
    r.mutated = True
    return _ok("set output exa in source")


@command("set reboot")
def _set_reboot(state: DeviceState, payload: Payload, r: CommandResult) -> dict[str, Any]:
    r.reboot = True
    return _ok("set reboot")


def recognised_comheads() -> set[str]:
    """Every comhead the simulator implements (plus ``login``)."""
    return set(HANDLERS) | {"login"}
