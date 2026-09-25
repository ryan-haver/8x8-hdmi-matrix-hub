"""Unit tests for the simulator's HTTP and Telnet command handlers.

Includes the plan's L2 contract checks: every command the hub can send must be
recognised by the simulator, and simulator output must parse with the hub's
own parsers.
"""

import re
from pathlib import Path

import pytest

from orei_matrix import OreiMatrix
from telnet_client import TelnetClient
from tools.simulator import DeviceState
from tools.simulator import protocol as proto
from tools.simulator.http_commands import READ_COMMANDS, dispatch, recognised_comheads
from tools.simulator.telnet_commands import banner, banner_bytes, handle

SRC = Path(__file__).resolve().parents[2] / "src"


@pytest.fixture
def state() -> DeviceState:
    return DeviceState.default()


def run(state, **payload):
    return dispatch(state, payload)


# ============================================================ HTTP reads

#: Keys, in order, that MCU V1.10.01 sends (tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/http).
DEVICE_READ_KEYS = {
    "get video status": ["comhead", "power", "allsource", "allinputname", "alloutputname", "allname"],
    "get output status": [
        "comhead", "power", "allconnect", "name", "allscaler", "allhdr", "allhdcp", "allarc", "allout",
        "allaudiomute",
    ],
    "get input status": ["comhead", "power", "edid", "inactive", "inname"],
    "get cec status": ["comhead", "power", "allinputname", "alloutputname", "inputindex", "outputindex"],
    "get system status": ["comhead", "power", "baudrate", "beep", "lock", "mode"],
    "get status": ["comhead", "power", "version", "hostname", "ipaddress", "subnet", "gateway", "macaddress",
                   "model", "webversion"],
    "get network": ["comhead", "power", "dhcp", "ipaddress", "subnet", "gateway", "telnetport", "tcpport",
                    "macaddress", "hostname", "username", "model"],
    "get ext-audio status": ["comhead", "power", "mode", "allsource", "allout", "allinputname", "alloutputname",
                             "index"],
}
#: Per-output arrays with the ninth entry V1.10.01 appends (HIL-04).
NINE_ENTRIES = {"allsource", "allscaler", "allhdr", "allhdcp", "allarc", "allout", "allaudiomute"}
ARRAYS = {"name", "edid", "inactive", "inname", "inputindex", "outputindex"}


@pytest.mark.parametrize("comhead", sorted(DEVICE_READ_KEYS))
def test_read_responses_have_the_device_keys_in_order(state, comhead):
    r = run(state, comhead=comhead, language=0)
    assert r.recognised and not r.mutated
    assert list(r.response) == DEVICE_READ_KEYS[comhead]
    for key, value in r.response.items():
        if key.startswith("all") or key in ARRAYS:
            nine = key in NINE_ENTRIES and comhead != "get ext-audio status"
            assert len(value) == (9 if nine else 8), key


def test_documented_preset_reads_keep_their_shape(state):
    """`get routing status` / `preset get`: the server never answers them (HIL-01), the handlers keep the doc shape."""
    assert list(run(state, comhead="get routing status", language=0, index=1).response) == [
        "comhead", "power", "allpreset",
    ]
    assert proto.UNANSWERED_COMHEADS == {"get routing status", "preset get"}


def test_read_values_reflect_state(state):
    video = run(state, comhead="get video status").response
    assert video["allsource"] == [2, 2, 1, 1, 5, 6, 1, 1, state.ninth_output["source"]]
    assert video["allinputname"][1] == "AppleTV"
    assert video["allname"][0] == "Apple TV"
    inp = run(state, comhead="get input status").response
    assert inp["inactive"] == [0, 1, 0, 0, 1, 1, 0, 0]  # 1 = signal present
    out = run(state, comhead="get output status").response
    assert out["allconnect"] == [1, 1, 0, 0, 0, 0, 0, 0]
    assert out["name"][1] == "Soundbar" and out["allscaler"][1] == 4  # 4 = audio only (V1.10.01)
    routing = run(state, comhead="get routing status").response
    assert routing["allpreset"][0] == {"allsource": [2] * 8, "name": "Apple TV"}
    assert run(state, comhead="preset get", index=3).response["allsource"] == [6] * 8


# ============================================================ HTTP writes


def test_video_switch_single_and_all(state):
    assert run(state, comhead="video switch", language=0, source=[3, 7]).response["result"] == proto.RESULT_OK
    assert state.outputs[2].source == 7
    run(state, comhead="video switch", language=0, source=[0, 4])
    assert state.routing == [4] * 8


@pytest.mark.parametrize("source", [[9, 1], [1, 0], [1, 9], "1,2", [1], [1, "2"]])
def test_video_switch_rejects_bad_source(state, source):
    before = state.routing
    r = run(state, comhead="video switch", language=0, source=source)
    assert r.response == {"comhead": "video switch", "result": proto.RESULT_FAIL}
    assert state.routing == before


def test_presets_recall_and_save(state):
    run(state, comhead="preset set", language=0, index=2)
    assert state.routing == [5] * 8
    run(state, comhead="video switch", language=0, source=[1, 1])
    run(state, comhead="preset save", language=0, index=8)
    assert state.presets[7].routing == [1] + [5] * 7
    assert run(state, comhead="preset set", index=9).response["result"] == proto.RESULT_FAIL


def test_power_beep_lock_lcd(state):
    run(state, comhead="set poweronoff", language=0, power=0)
    assert run(state, comhead="get video status").response["power"] == 0
    run(state, comhead="set beep", language=0, beep=0)
    run(state, comhead="set panel lock", language=0, lock=1)
    run(state, comhead="set lcd on time", time=0)
    sysr = run(state, comhead="get system status").response
    assert (sysr["beep"], sysr["lock"]) == (0, 1)
    assert state.system["lcd_timeout"] == 0
    assert run(state, comhead="set lcd on time", time=5).response["result"] == proto.RESULT_FAIL


def test_names(state):
    run(state, comhead="set input name", language=0, name="Xbox", index=8)
    run(state, comhead="set output name", language=0, name="Projector" * 5, index=3)
    video = run(state, comhead="get video status").response
    assert video["allinputname"][7] == "Xbox"
    assert video["alloutputname"][2] == ("Projector" * 5)[:32]


@pytest.mark.parametrize(
    "comhead, key, value, attr",
    [
        ("set output stream", "enable", 0, "stream"),
        ("set output hdcp", "hdcp", 2, "hdcp"),
        ("set output hdr", "hdr", 1, "hdr"),
        ("set output scaler", "scaler", 5, "scaler"),
        ("set output arc", "arc", 0, "arc"),
        ("set output mute", "mute", 1, "audio_mute"),
    ],
)
def test_output_settings(state, comhead, key, value, attr):
    r = run(state, comhead=comhead, output=1, **{key: value})
    assert r.response["result"] == proto.RESULT_OK and r.mutated
    assert getattr(state.outputs[0], attr) == value
    assert run(state, comhead=comhead, output=9, **{key: value}).response["result"] == proto.RESULT_FAIL


def test_edid(state):
    run(state, comhead="set input edid", input=4, edid=12)
    assert state.inputs[3].edid == 12
    run(state, comhead="copy edid", input=4, output=2)
    assert state.inputs[3].edid == 16
    assert run(state, comhead="set input edid", input=4, edid=0).response["result"] == proto.RESULT_FAIL


def test_cec_index_documented_shape(state):
    r = run(state, comhead="set cec index", language=0, inputindex=[1] * 8, outputindex=[0] * 8)
    assert r.response["result"] == proto.RESULT_OK and not r.warnings
    cec = run(state, comhead="get cec status").response
    assert cec["inputindex"] == [1] * 8 and cec["outputindex"] == [0] * 8
    assert run(state, comhead="set cec index", inputindex=[1] * 7, outputindex=[0] * 8).response["result"] == 0


def test_cec_index_single_port_shape_is_flagged(state):
    """BE-13: OreiMatrix.set_cec_enable sends an undocumented shape."""
    r = run(state, comhead="set cec index", port="input", index=3, enable=1)
    assert r.response["result"] == proto.RESULT_OK
    assert state.inputs[2].cec_enabled == 1
    assert any("BE-13" in w for w in r.warnings)


def test_cec_command(state):
    r = run(state, comhead="cec command", language=0, object=1, port=[1] + [0] * 7, index=1)
    assert r.response["result"] == proto.RESULT_OK and not r.warnings
    r = run(state, comhead="cec command", language=0, object=0, port=[0, 0, 1] + [0] * 5, index=5)
    assert r.response["result"] == proto.RESULT_OK and "disabled" in r.warnings[0]
    for bad in ({"index": 20}, {"port": [0] * 8}, {"object": 2}):
        payload = {"comhead": "cec command", "object": 0, "port": [1] + [0] * 7, "index": 1, **bad}
        assert dispatch(state, payload).response["result"] == proto.RESULT_FAIL


def test_ext_audio(state):
    run(state, comhead="set output exa mode", mode=2)
    run(state, comhead="set output exa", output=3, exa=1)
    run(state, comhead="set output exa in source", output=3, input=6)
    ext = run(state, comhead="get ext-audio status").response
    assert ext["mode"] == 2 and ext["allout"][2] == 1 and ext["allsource"][2] == 6
    run(state, comhead="set output exa", output=3, exa=2)
    assert state.outputs[2].ext_audio_enabled == 0


def test_reboot_and_unknown(state):
    assert run(state, comhead="set reboot").reboot
    r = run(state, comhead="get bogus")
    assert not r.recognised and r.response == {"comhead": "get bogus", "result": proto.UNKNOWN_COMMAND_RESULT}


def test_read_commands_never_mutate(state):
    before = state.to_dict()
    for comhead in READ_COMMANDS:
        run(state, comhead=comhead, language=0, index=1)
    assert state.to_dict() == before


# ============================================================ Telnet


def test_status_dump_parses_with_hub_parser(state):
    state.outputs[0].hdcp = 2
    state.outputs[1].audio_mute = 1
    state.system["panel_lock"] = 1
    text = handle(state, "status").text
    assert text.rstrip().splitlines()[-1].startswith("mac address:")
    parsed = TelnetClient("sim")._parse_status_response(text)
    assert parsed.power and parsed.beep and parsed.panel_lock
    assert parsed.lcd_timeout == 30
    assert {i: p.connected for i, p in parsed.inputs.items()} == {
        i + 1: bool(p.cable) for i, p in enumerate(state.inputs)
    }
    assert {i: o.connected for i, o in parsed.outputs.items()} == {
        i + 1: bool(o.connected) for i, o in enumerate(state.outputs)
    }
    assert parsed.routing == {i + 1: src for i, src in enumerate(state.routing)}
    assert parsed.outputs[1].hdcp == proto.HDCP_TEXT[2]
    assert parsed.outputs[2].audio_mute is True
    assert parsed.outputs[1].stream_enabled is True


def test_banner_carries_firmware_version(state):
    text = banner(state)
    match = re.search(r"fw version\s*:\s*v?([\d.]+)", text, re.IGNORECASE)
    assert match and match.group(1) == "1.10.01"
    raw = banner_bytes(state)
    assert raw.startswith(proto.TELNET_IAC_NEGOTIATION) and raw.endswith(text.encode())


def test_telnet_link_queries(state):
    assert handle(state, "r link in 3").text == "r link in 3!\r\nhdmi input 3: disconnect\r\n"
    assert handle(state, "r link out 1").lines == ["hdmi output 1: connect"]
    assert handle(state, "r link out 9").lines == [proto.TELNET_ERR_PARAM]


def test_telnet_routing_and_presets(state):
    r = handle(state, "s output 2 in source 6")
    assert r.mutated and r.lines == ["output2->input6"] and state.outputs[1].source == 6
    handle(state, "s output 0 in source 3")
    assert state.routing == [3] * 8
    handle(state, "s recall preset 1")
    assert state.routing == [2] * 8
    handle(state, "s av 7 1")
    handle(state, "s save preset 6")
    assert state.presets[5].routing == [7] + [2] * 7
    assert handle(state, "r preset 6").lines == ["output1->input7"] + [f"output{i}->input2" for i in range(2, 9)]
    handle(state, "s clear preset 6")
    assert state.presets[5].routing == list(range(1, 9))
    assert handle(state, "r preset 6").lines == ["preset 6 is none,please save a preset"]


def test_telnet_cec_never_sends_error_codes_on_success(state):
    for word in proto.TELNET_CEC_INPUT_WORDS:
        text = handle(state, f"s cec in 2 {word}").text
        assert "E0" not in text
    assert handle(state, "s cec hdmi out 1 active").lines == ["cec hdmi out 1 active"]
    assert handle(state, "s cec in 2 dance").lines == [proto.TELNET_ERR_PARAM]


def test_telnet_misc(state):
    assert handle(state, "r fw version").lines == [
        "mcu fw version: v1.10.01", "key mcu       : v1.00.08", "web gui       : v2.00.03", "cpld version  : v1.00.06",
    ]
    assert handle(state, "r type").lines == ["8x8 hdmi2.1 matrix"]
    handle(state, "s power 0")
    assert state.system["power"] == 0
    handle(state, "s beep 0")
    handle(state, "s lock 1")
    handle(state, "s out 4 stream 0")
    assert (state.system["beep"], state.system["panel_lock"], state.outputs[3].stream) == (0, 1, 0)
    assert handle(state, "reboot").reboot
    unknown = handle(state, "make coffee")
    assert not unknown.recognised and unknown.lines == [proto.TELNET_ERR_UNKNOWN]


# ============================================================ L2 contract


def _hub_comheads() -> set[str]:
    text = (SRC / "orei_matrix.py").read_text(encoding="utf-8")
    return set(re.findall(r'"comhead":\s*"([^"]+)"', text))


def test_hub_comhead_scan_finds_commands():
    assert {"login", "video switch", "get video status", "cec command"} <= _hub_comheads()


@pytest.mark.parametrize("comhead", sorted(_hub_comheads()))
def test_every_hub_comhead_is_recognised(comhead):
    assert comhead in recognised_comheads()


def _hub_telnet_commands() -> list[str]:
    text = (SRC / "telnet_client.py").read_text(encoding="utf-8")
    commands = []
    # Commands are passed inline (`_send_raw("status")`) or built first
    # (`telnet_cmd = f"s cec in {input_num} {command}"`) so the same string
    # can be checked for its acknowledgement.
    templates = re.findall(r'_send_raw\(f?"([^"]+)"\)', text) + re.findall(r'telnet_cmd = f?"([^"]+)"', text)
    for template in templates:
        cmd = re.sub(r"\{command\}", "on", template)
        cmd = re.sub(r"\{[a-z_]+\}", "1", cmd)
        commands.append(cmd)
    return sorted(set(commands))


def test_hub_telnet_scan_finds_commands():
    cmds = _hub_telnet_commands()
    assert "status" in cmds and "s cec in 1 on" in cmds and "r link out 1" in cmds


_TELNET_XFAIL = {
    # ASSUMPTION(HIL-A) in the simulator, not a confirmed hub bug: the vendor
    # serial reference uses "s power <0|1>"; TelnetClient.power_on/off send a
    # bare "power <n>" (telnet_client.py:1056,1065). Unused by the hub today.
    "power 1": "HIL-A: TelnetClient sends 'power N', vendor reference says 's power N'",
    "power 0": "HIL-A: TelnetClient sends 'power N', vendor reference says 's power N'",
}


@pytest.mark.parametrize(
    "command",
    [
        pytest.param(c, marks=pytest.mark.xfail(strict=True, reason=_TELNET_XFAIL[c])) if c in _TELNET_XFAIL else c
        for c in _hub_telnet_commands()
    ],
)
def test_every_hub_telnet_command_is_recognised(state, command):
    result = handle(state, command)
    assert result.recognised and proto.TELNET_ERR_UNKNOWN not in result.lines


@pytest.mark.parametrize("word", sorted(set(OreiMatrix._CEC_INDEX_TO_TELNET.values())))
def test_every_hub_cec_word_is_accepted(state, word):
    assert handle(state, f"s cec in 1 {word}").lines == [f"cec in 1 {word}"]
    assert handle(state, f"s cec hdmi out 1 {word}").lines == [f"cec hdmi out 1 {word}"]
