"""The exact commands the hub sends, plus the documented extras.

Payload builders copy ``src/orei_matrix.py`` key for key (including key order
and the ``language`` field, or its absence), so a capture shows what the hub
will really get back. ``tests/sim/test_capture_catalog.py`` scans ``src/`` and
fails if the hub sends a comhead or Telnet command the capture tool does not
cover.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PORTS = range(1, 9)

# ------------------------------------------------------------------ payloads
# One builder per hub method (orei_matrix.py line numbers as of Phase 0).


def login(user: str, password: str) -> dict[str, Any]:  # connect()
    return {"comhead": "login", "user": user, "password": password}


def read(comhead: str) -> dict[str, Any]:  # get_*_status / get_network_info / get_device_info
    return {"comhead": comhead, "language": 0}


def preset_get(index: int) -> dict[str, Any]:  # old get_preset_info HTTP fallback (removed, HIL-01)
    return {"comhead": "preset get", "index": index}


def routing_status() -> dict[str, Any]:  # documented, not sent by the hub
    return {"comhead": "get routing status", "language": 0, "index": 1}


def video_switch(output: int, input_: int) -> dict[str, Any]:  # switch_input / switch_input_to_all (output 0)
    return {"comhead": "video switch", "language": 0, "source": [output, input_]}


def preset_set(index: int) -> dict[str, Any]:  # recall_scene
    return {"comhead": "preset set", "language": 0, "index": index}


def preset_save(index: int) -> dict[str, Any]:  # save_preset
    return {"comhead": "preset save", "language": 0, "index": index}


def power(on: int) -> dict[str, Any]:  # power_on / power_off
    return {"comhead": "set poweronoff", "language": 0, "power": on}


def panel_lock(lock: int) -> dict[str, Any]:  # set_panel_lock
    return {"comhead": "set panel lock", "language": 0, "lock": lock}


def beep(value: int) -> dict[str, Any]:  # set_beep
    return {"comhead": "set beep", "language": 0, "beep": value}


def lcd_time(mode: int) -> dict[str, Any]:  # set_lcd_timeout
    return {"comhead": "set lcd on time", "time": mode}


def input_name(index: int, name: str) -> dict[str, Any]:  # set_input_name
    return {"comhead": "set input name", "language": 0, "name": name, "index": index}


def output_name(index: int, name: str) -> dict[str, Any]:  # set_output_name
    return {"comhead": "set output name", "language": 0, "name": name, "index": index}


#: snapshot field -> (comhead, payload key) for per-output settings.
OUTPUT_SETTINGS: dict[str, tuple[str, str]] = {
    "stream": ("set output stream", "enable"),
    "hdcp": ("set output hdcp", "hdcp"),
    "hdr": ("set output hdr", "hdr"),
    "scaler": ("set output scaler", "scaler"),
    "arc": ("set output arc", "arc"),
    "mute": ("set output mute", "mute"),
}


def output_setting(setting: str, output: int, value: int) -> dict[str, Any]:  # set_output_* methods
    comhead, key = OUTPUT_SETTINGS[setting]
    return {"comhead": comhead, "output": output, key: value}


def input_edid(input_: int, mode: int) -> dict[str, Any]:  # set_input_edid / copy_edid_from_output (14+N)
    return {"comhead": "set input edid", "input": input_, "edid": mode}


def copy_edid(input_: int, output: int) -> dict[str, Any]:  # documented, not sent by the hub (BE-25)
    return {"comhead": "copy edid", "input": input_, "output": output}


def cec_index_bulk(inputs: list[int], outputs: list[int]) -> dict[str, Any]:  # set_cec_enabled_bulk / toggle
    return {"comhead": "set cec index", "language": 0, "inputindex": list(inputs), "outputindex": list(outputs)}


def cec_index_single(port_type: str, index: int, enable: int) -> dict[str, Any]:  # set_cec_enable (BE-13)
    return {"comhead": "set cec index", "port": port_type, "index": index, "enable": enable}


def cec_command(obj: int, port: int, index: int) -> dict[str, Any]:  # send_cec_command (HTTP path)
    ports = [0] * 8
    if 1 <= port <= 8:
        ports[port - 1] = 1
    return {"comhead": "cec command", "language": 0, "object": obj, "port": ports, "index": index}


def exa_mode(mode: int) -> dict[str, Any]:  # set_ext_audio_mode
    return {"comhead": "set output exa mode", "mode": mode}


def exa_enable(output: int, enabled: bool) -> dict[str, Any]:  # set_ext_audio_enable
    return {"comhead": "set output exa", "output": output, "exa": 1 if enabled else 2}


def exa_source(output: int, input_: int) -> dict[str, Any]:  # set_ext_audio_source
    return {"comhead": "set output exa in source", "output": output, "input": input_}


def reboot() -> dict[str, Any]:  # reboot
    return {"comhead": "set reboot"}


# ------------------------------------------------------------------- reads


@dataclass(frozen=True)
class HttpRead:
    slug: str
    payload: dict[str, Any]
    answers: tuple[str, ...] = ()
    note: str = ""


@dataclass(frozen=True)
class TelnetRead:
    slug: str
    command: str
    answers: tuple[str, ...] = ()


_SHAPES = ("http-read-shapes",)

HTTP_READS: tuple[HttpRead, ...] = (
    HttpRead("get_video_status", read("get video status"), _SHAPES + ("video-status-names", "ninth-entry")),
    HttpRead("get_output_status", read("get output status"),
             _SHAPES + ("output-status-name-field", "ninth-entry", "output-mode-text")),
    HttpRead("get_input_status", read("get input status"), _SHAPES),
    HttpRead("get_cec_status", read("get cec status"), _SHAPES),
    HttpRead("get_system_status", read("get system status"), _SHAPES),
    HttpRead("get_status", read("get status"), _SHAPES + ("get-status-fields",)),
    HttpRead("get_network", read("get network"), _SHAPES + ("get-network-fields",)),
    HttpRead("get_ext_audio_status", read("get ext-audio status"), _SHAPES + ("ext-audio-index",)),
    HttpRead("get_routing_status", routing_status(), _SHAPES + ("preset-get-shape",), "documented; not sent by the hub"),
    *(HttpRead(f"preset_get_{n}", preset_get(n), _SHAPES + ("preset-get-shape",)) for n in PORTS),
)

#: Reads the hub does not need. A timeout on one of them means "this firmware
#: does not implement it" (V1.10.01, HIL-01): a warning, not a capture error.
OPTIONAL_READS = frozenset({"get routing status", "preset get"})

_TREAD = ("telnet-read-wording", "telnet-terminators")

TELNET_READS: tuple[TelnetRead, ...] = (
    TelnetRead("status", "status", ("telnet-status-wording", "telnet-terminators", "output-mode-text")),
    TelnetRead("r_fw_version", "r fw version", _TREAD),
    TelnetRead("r_type", "r type", _TREAD),
    *(TelnetRead(f"r_link_in_{n}", f"r link in {n}", _TREAD) for n in PORTS),
    *(TelnetRead(f"r_link_out_{n}", f"r link out {n}", _TREAD) for n in PORTS),
    *(TelnetRead(f"r_preset_{n}", f"r preset {n}", _TREAD) for n in PORTS),
)

#: Comheads read for a state snapshot (write mode).
SNAPSHOT_READS: tuple[str, ...] = (
    "get video status",
    "get output status",
    "get input status",
    "get cec status",
    "get system status",
    "get ext-audio status",
    "get routing status",
)


def snapshot_payload(comhead: str) -> dict[str, Any]:
    return routing_status() if comhead == "get routing status" else read(comhead)


# --------------------------------------------------------- Telnet templates

#: Every Telnet command template the hub's TelnetClient can send, and where the
#: capture tool exercises it. Checked against src/telnet_client.py by tests.
TELNET_COVERAGE: dict[str, str] = {
    "status": "read",
    "r fw version": "read",
    "r type": "read",
    "r link in N": "read",
    "r link out N": "read",
    "r preset N": "read",
    "s cec in N WORD": "probe (invalid) / write [cec-live]",
    "s cec hdmi out N WORD": "probe (invalid) / write [cec-live]",
    "s save preset N": "write telnet",
    "s recall preset N": "write telnet",
    "s clear preset N": "write telnet",
    "s output N in source N": "probe (no-op) / write telnet",
    "power N": "write power",
    "reboot": "write [reboot]",
}


@dataclass
class ProbeTelnetError:
    command: str
    why: str
    answers: tuple[str, ...] = field(default=("telnet-error-codes",))


#: Commands that should be rejected without side effects.
TELNET_ERROR_PROBES: tuple[ProbeTelnetError, ...] = (
    ProbeTelnetError("hilcapture unknown", "unknown command"),
    ProbeTelnetError("r link in 9", "input port out of range"),
    ProbeTelnetError("r link out 0", "output port out of range"),
    ProbeTelnetError("r preset 9", "preset out of range"),
    ProbeTelnetError("r link in x", "non-numeric port"),
    ProbeTelnetError("s cec in 9 on", "CEC input port out of range"),
    ProbeTelnetError("s cec hdmi out 1 hilbogus", "unknown CEC word"),
    ProbeTelnetError("s output 9 in source 1", "routing output out of range"),
)
