"""WP-A4 part 2: the hub sends the commands this firmware implements (HIL-09..12).

Every setter is checked against the simulator's command log: the exact payload
(comhead, key order, ``[port, value]`` pairs, device codes) the device's own
web interface sends, and the state change it causes. The commands are
web-UI-derived: these tests prove the hub sends them as designed, not that
the hardware accepts them (that is the capture tool's write run,
tools/hil/README.md).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import orei_matrix
from device_codes import (
    CEC_OUTPUT_COMMANDS,
    EDID_MODES,
    HDR_DEVICE_MODES,
    SCALER_DEVICE_MODES,
    hdr_from_device,
    hdr_to_device,
    scaler_from_device,
    scaler_to_device,
)
from tools.simulator import protocol as proto

SRC = Path(__file__).resolve().parents[2] / "src"


def sent(simulator, comhead: str) -> list[dict]:
    """Payloads the hub sent with ``comhead`` (login excluded)."""
    return [e["payload"] for e in simulator.log if e.get("channel") == "http" and e.get("command") == comhead]


# ------------------------------------------------------------------ setters

#: (method, args, comhead, exact payload, (state path, expected value))
SETTERS = [
    ("set_output_enable", (3, False), "tx stream", {"out": [3, 0]}, ("outputs", 2, "stream", 0)),
    ("set_output_enable", (3, True), "tx stream", {"out": [3, 1]}, ("outputs", 2, "stream", 1)),
    ("set_output_hdcp", (3, 2), "tx hdcp", {"hdcp": [3, 2]}, ("outputs", 2, "hdcp", 2)),
    ("set_output_hdcp", (3, 5), "tx hdcp", {"hdcp": [3, 5]}, ("outputs", 2, "hdcp", 5)),
    # HDR: API 1-3 -> device 0-2 (HIL-02)
    ("set_output_hdr", (3, 1), "set hdr conversion", {"hdr": [3, 0]}, ("outputs", 2, "hdr", 0)),
    ("set_output_hdr", (3, 2), "set hdr conversion", {"hdr": [3, 1]}, ("outputs", 2, "hdr", 1)),
    ("set_output_hdr", (3, 3), "set hdr conversion", {"hdr": [3, 2]}, ("outputs", 2, "hdr", 2)),
    # scaler: API 1-5 -> device 0-4; audio only is 4 on the device (BE-15)
    ("set_output_scaler", (3, 1), "set video scaler", {"scaler": [3, 0]}, ("outputs", 2, "scaler", 0)),
    ("set_output_scaler", (3, 5), "set video scaler", {"scaler": [3, 4]}, ("outputs", 2, "scaler", 4)),
    ("set_output_arc", (3, True), "set arc", {"arc": [3, 1]}, ("outputs", 2, "arc", 1)),
    ("set_output_audio_mute", (2, True), "set output audio mute", {"mute": [2, 1]}, ("outputs", 1, "audio_mute", 1)),
    ("set_input_edid", (4, 12), "set edid", {"edid": [4, 12]}, ("inputs", 3, "edid", 12)),
    ("copy_edid_from_output", (4, 3), "set edid", {"edid": [4, 42]}, ("inputs", 3, "edid", 42)),  # BE-25
    ("set_lcd_timeout", (1,), "set lcd on time", {"lcd on time": 1}, ("system", None, "lcd_timeout", 1)),
    ("set_ext_audio_mode", (2,), "set ext-audio mode", {"mode": 2}, ("ext_audio", None, "mode", 2)),
    ("set_ext_audio_enable", (4, False), "set ext-audio out", {"out": [4, 0]},
     ("outputs", 3, "ext_audio_enabled", 0)),
    ("set_ext_audio_source", (4, 6), "ext-audio switch", {"source": [4, 6]}, ("outputs", 3, "ext_audio_source", 6)),
    ("set_ext_audio_index", (5,), "set ext-audio index", {"index": 5}, ("ext_audio", None, "index", 5)),
    ("set_preset_name", (3, "Movie"), "preset name", {"index": 3, "name": "Movie"}, ("presets", 2, "name", "Movie")),
    ("save_preset", (7,), "preset save", {"index": 7}, ("presets", 6, "saved", True)),
]


def _state_value(simulator, where):
    group, index, attr, _ = where
    if index is None:
        return getattr(simulator.state, group)[attr]
    return getattr(getattr(simulator.state, group)[index], attr)


@pytest.mark.parametrize("method, args, comhead, payload, where", SETTERS,
                         ids=[f"{s[0]}{s[1]}" for s in SETTERS])
async def test_setter_sends_the_web_interface_command(matrix, simulator, method, args, comhead, payload, where):
    await matrix.connect()
    assert await getattr(matrix, method)(*args) is True
    assert sent(simulator, comhead)[-1] == {"comhead": comhead, "language": 0, **payload}
    assert list(sent(simulator, comhead)[-1]) == ["comhead", "language", *payload]  # key order
    assert _state_value(simulator, where) == where[3]
    assert simulator.unrecognised() == []


@pytest.mark.parametrize("method, args", [
    ("set_output_hdr", (3, 0)), ("set_output_hdr", (3, 4)), ("set_output_scaler", (3, 0)),
    ("set_output_scaler", (3, 6)), ("set_output_hdcp", (3, 0)), ("set_output_hdcp", (0, 1)),
    ("set_input_edid", (1, 0)), ("set_input_edid", (1, 48)), ("copy_edid_from_output", (1, 9)),
    ("set_lcd_timeout", (5,)), ("set_ext_audio_mode", (3,)), ("set_ext_audio_source", (1, 9)),
    ("set_ext_audio_index", (9,)), ("set_preset_name", (9, "x")), ("set_output_audio_mute", (9, True)),
])
async def test_setters_validate_before_sending(matrix, simulator, method, args):
    await matrix.connect()
    simulator.log.clear()
    assert await getattr(matrix, method)(*args) is False
    assert [e for e in simulator.log if e.get("channel") == "http"] == []


async def test_system_reboot_http_uses_the_reboot_command(matrix, simulator):
    """The device web interface's `reboot` {"reboot": 1}; `set reboot` was never captured."""
    await matrix.connect()
    assert await matrix.system_reboot() is True
    assert sent(simulator, "reboot")[-1] == {"comhead": "reboot", "language": 0, "reboot": 1}
    assert sent(simulator, "set reboot") == []


# ------------------------------------------------------------------ CEC (HIL-10, BE-14, VAL-03)


async def test_set_cec_enable_sends_both_arrays_and_keeps_other_ports(matrix, simulator):
    """HIL-10 / BE-13: the device rejects the single-port shape; the hub only sends the array form."""
    await matrix.connect()
    before_out = simulator.state.column("outputs", "cec_enabled")
    assert await matrix.set_cec_enable("input", 3, True)
    payload = sent(simulator, "set cec index")[-1]
    assert list(payload) == ["comhead", "language", "inputindex", "outputindex"]
    assert payload["inputindex"][2] == 1 and payload["outputindex"] == before_out
    assert simulator.state.inputs[2].cec_enabled == 1
    assert await matrix.set_cec_enable("output", 1, False)
    assert simulator.state.outputs[0].cec_enabled == 0
    assert all("port" not in p for p in sent(simulator, "set cec index"))


@pytest.mark.parametrize("name, index", sorted(CEC_OUTPUT_COMMANDS.items()))
async def test_display_cec_commands_use_the_output_table(matrix, simulator, name, index):
    """BE-14: displays have their own 0-based table (0 on, 1 off, 2 mute, 3 vol-, 4 vol+, 5 active)."""
    await matrix.connect()
    assert await matrix.send_cec(name, 2, is_output=True)
    payload = sent(simulator, "cec command")[-1]
    assert (payload["object"], payload["port"], payload["index"]) == (1, [0, 1, 0, 0, 0, 0, 0, 0], index)


async def test_display_power_helpers_no_longer_send_the_input_indices(matrix, simulator):
    """Regression (BE-14): cec_output_power_on sent input index 1, which is *power off* for a display."""
    await matrix.connect()
    assert await matrix.cec_output_power_on(1)
    assert await matrix.cec_output_power_off(1)
    assert [p["index"] for p in sent(simulator, "cec command")] == [0, 1]


@pytest.mark.parametrize("name", ["UP", "SELECT", "PLAY", "BACK"])
async def test_navigation_to_a_display_is_refused_without_sending(matrix, simulator, name):
    await matrix.connect()
    assert await matrix.send_cec(name, 1, is_output=True) is False
    assert sent(simulator, "cec command") == []


async def test_source_cec_keeps_the_input_table(matrix, simulator):
    await matrix.connect()
    assert await matrix.send_cec("VOLUME_UP", 2)
    payload = sent(simulator, "cec command")[-1]
    assert (payload["object"], payload["index"]) == (0, 19)


# ------------------------------------------------------------------ regressions HIL-09 / HIL-11


def test_the_hub_never_sends_the_commands_the_firmware_ignores():
    """HIL-09: none of the comheads V1.10.01 left unanswered is in the hub any more."""
    text = (SRC / "orei_matrix.py").read_text(encoding="utf-8")
    sent_by_hub = set(re.findall(r'"comhead":\s*"([^"]+)"', text))
    assert sent_by_hub & proto.LEGACY_UNANSWERED_WRITES == set()
    assert "set reboot" not in sent_by_hub and not re.search(r'"comhead": "set lcd on time", "time"', text)


def test_the_telnet_client_never_sends_the_unknown_stream_command():
    """HIL-11: `s out N stream` is E00 on V1.10.01."""
    text = (SRC / "telnet_client.py").read_text(encoding="utf-8")
    assert not re.search(r"s out \{?\w*\}? stream", text)


# ------------------------------------------------------------------ API <-> device codes


def test_hdr_and_scaler_api_values_map_to_device_codes_and_back():
    for code in HDR_DEVICE_MODES:
        assert hdr_to_device(hdr_from_device(code)) == code
    for code in SCALER_DEVICE_MODES:
        assert scaler_to_device(scaler_from_device(code)) == code
    assert (hdr_from_device(0), scaler_from_device(4)) == (1, 5)  # the captured pass-through / audio only
    assert hdr_from_device(3) is None and scaler_from_device(255) is None  # 255 = the "all outputs" entry
    with pytest.raises(ValueError):
        hdr_to_device(0)


def test_edid_table_is_the_device_list():
    assert sorted(EDID_MODES) == list(range(1, 48))
    assert EDID_MODES[36] == "8K FRL 12G HDR 7.1CH"  # V1.10.01 reports 36; Telnet: frl12g_8k_hdr,7.1ch
    assert [EDID_MODES[39 + n] for n in (1, 8)] == ["Copy from Output 1", "Copy from Output 8"]


def test_shortcut_lcd_map_matches_the_device_codes():
    """API-07: "always on" used to send 4 (60 s)."""
    from system_shortcuts import LCD_TIMEOUT_MODES

    assert LCD_TIMEOUT_MODES == {"off": 0, "15s": 2, "10s": 2, "30s": 3, "60s": 4, "always_on": 1}
    assert orei_matrix.OreiMatrix.LCD_TIMEOUT_MODES[1] == "Always On"
