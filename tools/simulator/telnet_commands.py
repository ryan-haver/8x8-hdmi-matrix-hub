"""Telnet command handlers (port 23 protocol).

Commands arrive as ``<command>!`` (the hub sends ``<command>!\\r\\n``).
Every response line ends with ``\\r\\n``. The whole response format is a guess
(marked ``ASSUMPTION(HIL-A)``) shaped to satisfy the parsers in
``src/telnet_client.py``; HIL-A must capture the real text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import protocol as proto
from .state import DeviceState

EOL = proto.TELNET_EOL


@dataclass
class TelnetResult:
    lines: list[str]
    recognised: bool = True
    mutated: bool = False
    reboot: bool = False
    warnings: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "".join(line + EOL for line in self.lines)


def banner(state: DeviceState) -> str:
    fmt = {"model": state.device["model"], "fw_version": state.device["firmware_version"]}
    return "".join(line.format(**fmt) + EOL for line in proto.TELNET_BANNER_LINES)


def _on_off(v: int) -> str:
    return "on" if v else "off"


def _lcd_line(mode: int) -> str:
    # ASSUMPTION(HIL-A): wording; the client only parses "lcd on <N> seconds".
    if mode == 0:
        return "lcd off"
    if mode == 1:
        return "lcd on always"
    return f"lcd on {proto.LCD_SECONDS[mode]} seconds"


def status_lines(state: DeviceState) -> list[str]:
    """``status!`` dump. ASSUMPTION(HIL-A): line wording and order.

    The client requires ``mac address:`` to be the last thing it sees
    (telnet_client.py:396).
    """
    s, d = state.system, state.device
    lines = [
        f"power {_on_off(s['power'])}",
        f"beep {_on_off(s['beep'])}",
        f"panel button lock {_on_off(s['panel_lock'])}",
        _lcd_line(s["lcd_timeout"]),
    ]
    lines += [f"hdmi input {i}: {'connect' if p.cable else 'disconnect'}" for i, p in enumerate(state.inputs, 1)]
    lines += [f"hdmi output {i}: {'connect' if o.connected else 'disconnect'}" for i, o in enumerate(state.outputs, 1)]
    lines += [f"output{i}->input{o.source}" for i, o in enumerate(state.outputs, 1)]
    for i, o in enumerate(state.outputs, 1):
        lines += [
            f"output {i} hdcp: {proto.HDCP_TEXT[o.hdcp]}",
            f"output {i} stream: {'enable' if o.stream else 'disable'}",
            f"output {i} video mode: {proto.SCALER_TEXT[o.scaler]}",
            f"output {i} hdr mode: {proto.HDR_TEXT[o.hdr]}",
            f"output {i} arc: {_on_off(o.arc)}",
            f"output {i} audio mute: {_on_off(o.audio_mute)}",
        ]
    lines += [f"input {i} edid: {p.edid}" for i, p in enumerate(state.inputs, 1)]
    lines += [
        f"ip address: {d['ip_address']}",
        f"subnet mask: {d['netmask']}",
        f"gateway: {d['gateway']}",
        f"mac address: {d['mac_address']}",
    ]
    return lines


def _port(token: str, lo: int = 1) -> int | None:
    if not token.isdigit():
        return None
    n = int(token)
    return n if lo <= n <= proto.PORT_COUNT else None


_SIMPLE = re.compile(r"\s+")


def handle(state: DeviceState, raw: str) -> TelnetResult:
    """Handle one command (without its ``!`` terminator)."""
    cmd = _SIMPLE.sub(" ", raw.strip().lower())
    words = cmd.split(" ") if cmd else []

    def err(code: str, why: str, recognised: bool = True) -> TelnetResult:
        return TelnetResult([code], recognised=recognised, warnings=[why])

    unknown = err(proto.TELNET_ERR_UNKNOWN, f"unrecognised telnet command {raw!r}", recognised=False)

    if cmd == "status":
        return TelnetResult(status_lines(state))

    if cmd == "r fw version":
        return TelnetResult([f"fw version: {state.device['firmware_version']}"])

    if cmd == "r type":
        return TelnetResult([state.device["model"]])

    if len(words) == 4 and words[:2] == ["r", "link"] and words[2] in ("in", "out"):
        n = _port(words[3])
        if n is None:
            return err(proto.TELNET_ERR_PARAM, f"bad port in {raw!r}")
        if words[2] == "in":
            return TelnetResult([f"hdmi input {n}: {'connect' if state.inputs[n - 1].cable else 'disconnect'}"])
        return TelnetResult([f"hdmi output {n}: {'connect' if state.outputs[n - 1].connected else 'disconnect'}"])

    if len(words) == 3 and words[:2] == ["r", "preset"]:
        n = _port(words[2])
        if n is None:
            return err(proto.TELNET_ERR_PARAM, f"bad preset in {raw!r}")
        routing = ", ".join(f"output{i}->input{src}" for i, src in enumerate(state.presets[n - 1].routing, 1))
        return TelnetResult([f"preset {n}: {routing}"])

    # CEC: "s cec in <n> <word>" / "s cec hdmi out <n> <word>"
    # ASSUMPTION(HIL-A): success is acknowledged by echoing the command without
    # "s " and without any E0x code. BE-07: the client then waits for its full
    # COMMAND_TIMEOUT because it only treats E00/E01 as "complete".
    if len(words) == 5 and words[:3] == ["s", "cec", "in"]:
        n = _port(words[3])
        if n is None or words[4] not in proto.TELNET_CEC_INPUT_WORDS:
            return err(proto.TELNET_ERR_PARAM, f"bad CEC input command {raw!r}")
        return TelnetResult([f"cec in {n} {words[4]}"])
    if len(words) == 6 and words[:4] == ["s", "cec", "hdmi", "out"]:
        n = _port(words[4])
        if n is None or words[5] not in proto.TELNET_CEC_OUTPUT_WORDS:
            return err(proto.TELNET_ERR_PARAM, f"bad CEC output command {raw!r}")
        return TelnetResult([f"cec hdmi out {n} {words[5]}"])

    # Routing: "s output <n|0> in source <m>"
    if len(words) == 6 and words[:2] == ["s", "output"] and words[3:5] == ["in", "source"]:
        out = _port(words[2], lo=0)
        inp = _port(words[5])
        if out is None or inp is None:
            return err(proto.TELNET_ERR_PARAM, f"bad routing {raw!r}")
        targets = range(1, proto.PORT_COUNT + 1) if out == 0 else [out]
        for o in targets:
            state.outputs[o - 1].source = inp
        return TelnetResult([f"output{o}->input{inp}" for o in targets], mutated=True)

    # Vendor serial reference: "s av <input> <output>"
    if len(words) == 4 and words[:2] == ["s", "av"]:
        inp, out = _port(words[2]), _port(words[3], lo=0)
        if inp is None or out is None:
            return err(proto.TELNET_ERR_PARAM, f"bad routing {raw!r}")
        targets = range(1, proto.PORT_COUNT + 1) if out == 0 else [out]
        for o in targets:
            state.outputs[o - 1].source = inp
        return TelnetResult([f"output{o}->input{inp}" for o in targets], mutated=True)

    # Presets: hub uses "s save|recall|clear preset N"; the vendor reference
    # uses "s preset save|recall N". Both accepted.
    # ASSUMPTION(HIL-A): acknowledgement wording.
    preset_op = None
    if len(words) == 4 and words[0] == "s" and words[2] == "preset" and words[1] in ("save", "recall", "clear"):
        preset_op, token = words[1], words[3]
    elif len(words) == 4 and words[:2] == ["s", "preset"] and words[2] in ("save", "recall"):
        preset_op, token = words[2], words[3]
    if preset_op:
        n = _port(token)
        if n is None:
            return err(proto.TELNET_ERR_PARAM, f"bad preset {raw!r}")
        preset = state.presets[n - 1]
        if preset_op == "save":
            preset.routing = state.routing
            return TelnetResult([f"save to preset {n}"], mutated=True)
        if preset_op == "recall":
            for out_port, src in zip(state.outputs, preset.routing, strict=True):
                out_port.source = src
            return TelnetResult([f"recall from preset {n}"], mutated=True)
        preset.routing = list(range(1, proto.PORT_COUNT + 1))
        return TelnetResult([f"clear preset {n}"], mutated=True)

    # Power: vendor reference is "s power <0|1>".
    # ASSUMPTION(HIL-A): the bare "power <0|1>" the hub's TelnetClient sends
    # (telnet_client.py:1056,1065) is NOT recognised (E00). Unused by the hub.
    if len(words) == 3 and words[:2] == ["s", "power"] and words[2] in ("0", "1", "on", "off"):
        state.system["power"] = 1 if words[2] in ("1", "on") else 0
        return TelnetResult([f"power {_on_off(state.system['power'])}"], mutated=True)

    if len(words) == 3 and words[0] == "s" and words[1] in ("beep", "lock") and words[2] in ("0", "1", "on", "off"):
        value = 1 if words[2] in ("1", "on") else 0
        if words[1] == "beep":
            state.system["beep"] = value
            return TelnetResult([f"beep {_on_off(value)}"], mutated=True)
        state.system["panel_lock"] = value
        return TelnetResult([f"panel button lock {_on_off(value)}"], mutated=True)

    # "s out <n> stream <0|1>" (vendor reference)
    if len(words) == 5 and words[:2] == ["s", "out"] and words[3] == "stream" and words[4] in ("0", "1"):
        n = _port(words[2])
        if n is None:
            return err(proto.TELNET_ERR_PARAM, f"bad port {raw!r}")
        state.outputs[n - 1].stream = int(words[4])
        return TelnetResult([f"output {n} stream: {'enable' if words[4] == '1' else 'disable'}"], mutated=True)

    # ASSUMPTION(HIL-A): "reboot" (what the hub sends) and "s reboot" both
    # reboot; the device acknowledges before dropping the connection.
    if cmd in ("reboot", "s reboot"):
        return TelnetResult(["reboot..."], reboot=True)

    return unknown


def recognised_command_patterns() -> list[str]:
    """Human-readable list of implemented commands (for the README / logs)."""
    return [
        "status",
        "r fw version",
        "r type",
        "r link in <n>",
        "r link out <n>",
        "r preset <n>",
        "s cec in <n> <word>",
        "s cec hdmi out <n> <word>",
        "s output <n|0> in source <m>",
        "s av <in> <out|0>",
        "s save|recall|clear preset <n>",
        "s preset save|recall <n>",
        "s power <0|1>",
        "s beep <0|1>",
        "s lock <0|1>",
        "s out <n> stream <0|1>",
        "reboot",
    ]
