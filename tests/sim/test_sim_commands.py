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
    assert proto.UNANSWERED_READS == {"get routing status", "preset get"}
    assert proto.UNANSWERED_READS <= proto.UNANSWERED_COMHEADS


def test_read_values_reflect_state(state):
    video = run(state, comhead="get video status").response
    assert video["allsource"] == [2, 2, 1, 1, 5, 6, 1, 1, proto.MIXED]  # outputs differ -> 255 (HIL-04)
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


def test_presets_recall_save_name_clear(state):
    run(state, comhead="preset set", language=0, index=2)
    assert state.routing == [5] * 8
    run(state, comhead="video switch", language=0, source=[1, 1])
    run(state, comhead="preset save", language=0, index=8)
    assert state.presets[7].routing == [1] + [5] * 7
    assert run(state, comhead="preset set", index=9).response["result"] == proto.RESULT_FAIL
    assert run(state, comhead="preset name", language=0, index=8, name="Movie").response["result"] == 1
    assert run(state, comhead="get video status").response["allname"][7] == "Movie"
    run(state, comhead="preset clear", language=0, index=8)
    assert not state.presets[7].saved
    # web-UI-derived: recalling an empty slot fails and changes nothing
    before = state.routing
    assert run(state, comhead="preset set", language=0, index=8).response["result"] == proto.RESULT_FAIL
    assert state.routing == before


def test_power_beep_lock_lcd(state):
    run(state, comhead="set poweronoff", language=0, power=0)
    assert run(state, comhead="get video status").response["power"] == 0
    run(state, comhead="set beep", language=0, beep=0)
    run(state, comhead="set panel lock", language=0, lock=1)
    assert run(state, comhead="set lcd on time", language=0, **{"lcd on time": 1}).response["result"] == 1
    sysr = run(state, comhead="get system status").response
    assert (sysr["beep"], sysr["lock"], sysr["mode"]) == (0, 1, 1)  # mode = LCD on-time code
    assert state.system["lcd_timeout"] == 1
    assert run(state, comhead="set lcd on time", **{"lcd on time": 5}).response["result"] == proto.RESULT_FAIL


def test_old_lcd_payload_is_rejected_like_the_device(state):
    """Captured (write/http_lcd): `{"time": N}` is answered with result 0 for every code (API-07, HIL-09)."""
    for code in range(6):
        assert run(state, comhead="set lcd on time", time=code).response == {
            "comhead": "set lcd on time", "result": proto.RESULT_FAIL}
    assert state.system["lcd_timeout"] == 3


def test_names(state):
    run(state, comhead="set input name", language=0, name="Xbox", index=8)
    run(state, comhead="set output name", language=0, name="Projector" * 5, index=3)
    video = run(state, comhead="get video status").response
    assert video["allinputname"][7] == "Xbox"
    # V1.10.01 kept a 40-character name (captured); the simulator stores up to NAME_MAX
    assert video["alloutputname"][2] == "Projector" * 5


@pytest.mark.parametrize(
    "comhead, key, value, attr",
    [
        ("tx stream", "out", 0, "stream"),
        ("tx hdcp", "hdcp", 2, "hdcp"),
        ("set hdr conversion", "hdr", 1, "hdr"),
        ("set video scaler", "scaler", 3, "scaler"),
        ("set arc", "arc", 1, "arc"),
        ("set output audio mute", "mute", 1, "audio_mute"),
    ],
)
def test_output_settings(state, comhead, key, value, attr):
    r = run(state, comhead=comhead, language=0, **{key: [1, value]})
    assert r.response == {"comhead": comhead, "result": proto.RESULT_OK} and r.mutated
    assert getattr(state.outputs[0], attr) == value
    assert getattr(state.outputs[1], attr) != value or attr == "hdcp"
    for bad in ([9, value], [1, 99], [1], value):
        assert run(state, comhead=comhead, **{key: bad}).response["result"] == proto.RESULT_FAIL


@pytest.mark.parametrize("comhead, key, value, attr", [
    ("tx stream", "out", 0, "stream"), ("set video scaler", "scaler", 2, "scaler"),
    ("set output audio mute", "mute", 1, "audio_mute"),
])
def test_output_settings_port_0_is_all_outputs(state, comhead, key, value, attr):
    run(state, comhead=comhead, language=0, **{key: [0, value]})
    assert state.column("outputs", attr) == [value] * 8
    ninth = run(state, comhead="get output status").response
    assert value in ninth["allscaler" if attr == "scaler" else "allout" if attr == "stream" else "allaudiomute"][8:]


@pytest.mark.parametrize("comhead, payload", [
    ("set output stream", {"output": 1, "enable": 0}),
    ("set output hdcp", {"output": 1, "hdcp": 2}),
    ("set output hdr", {"output": 1, "hdr": 1}),
    ("set output scaler", {"output": 1, "scaler": 5}),
    ("set output arc", {"output": 1, "arc": 0}),
    ("set output mute", {"output": 1, "mute": 1}),
    ("set input edid", {"input": 4, "edid": 12}),
    ("copy edid", {"input": 4, "output": 2}),
    ("set output exa mode", {"mode": 2}),
    ("set output exa", {"output": 3, "exa": 1}),
    ("set output exa in source", {"output": 3, "input": 6}),
])
def test_old_hub_commands_are_never_answered(state, comhead, payload):
    """HIL-09: MCU V1.10.01 ignored every one of these (captured timeouts); so does the simulator."""
    before = state.to_dict()
    r = run(state, comhead=comhead, **payload)
    assert r.unanswered and not r.recognised and not r.mutated
    assert state.to_dict() == before
    assert comhead in proto.LEGACY_UNANSWERED_WRITES


def test_edid(state):
    assert run(state, comhead="set edid", language=0, edid=[4, 12]).response["result"] == proto.RESULT_OK
    assert state.inputs[3].edid == 12
    run(state, comhead="set edid", language=0, edid=[4, 41])  # 39 + 2: copy from output 2 (BE-25)
    assert run(state, comhead="get input status").response["edid"][3] == 41
    for bad in ([4, 0], [4, 48], [0, 1], [9, 1]):
        assert run(state, comhead="set edid", edid=bad).response["result"] == proto.RESULT_FAIL


def test_cec_index_documented_shape(state):
    r = run(state, comhead="set cec index", language=0, inputindex=[1] * 8, outputindex=[0] * 8)
    assert r.response["result"] == proto.RESULT_OK and not r.warnings
    cec = run(state, comhead="get cec status").response
    assert cec["inputindex"] == [1] * 8 and cec["outputindex"] == [0] * 8
    assert run(state, comhead="set cec index", inputindex=[1] * 7, outputindex=[0] * 8).response["result"] == 0


def test_cec_index_single_port_shape_is_rejected(state):
    """BE-13 / HIL-10: the device answers the old single-port shape with result 0 and changes nothing."""
    r = run(state, comhead="set cec index", port="input", index=3, enable=1)
    assert r.response == {"comhead": "set cec index", "result": proto.RESULT_FAIL}
    assert state.inputs[2].cec_enabled == 0


def test_cec_command(state):
    r = run(state, comhead="cec command", language=0, object=1, port=[1] + [0] * 7, index=0)
    assert r.response["result"] == proto.RESULT_OK and not r.warnings
    r = run(state, comhead="cec command", language=0, object=0, port=[0, 0, 1] + [0] * 5, index=5)
    assert r.response["result"] == proto.RESULT_OK and "disabled" in r.warnings[0]
    # Captured (write/http_cec_command_invalid): only `object` is checked.
    for accepted in ({"index": 99}, {"port": [0] * 8}):
        payload = {"comhead": "cec command", "object": 0, "port": [1] + [0] * 7, "index": 1, **accepted}
        assert dispatch(state, payload).response["result"] == proto.RESULT_OK
    payload = {"comhead": "cec command", "object": 2, "port": [1] + [0] * 7, "index": 1}
    assert dispatch(state, payload).response["result"] == proto.RESULT_FAIL


def test_ext_audio(state):
    run(state, comhead="set ext-audio mode", language=0, mode=2)
    run(state, comhead="set ext-audio out", language=0, out=[3, 1])
    run(state, comhead="ext-audio switch", language=0, source=[3, 6])
    run(state, comhead="set ext-audio index", language=0, index=3)
    ext = run(state, comhead="get ext-audio status").response
    assert ext["mode"] == 2 and ext["allout"][2] == 1 and ext["allsource"][2] == 6 and ext["index"] == 3
    run(state, comhead="set ext-audio out", language=0, out=[3, 0])
    assert state.outputs[2].ext_audio_enabled == 0
    run(state, comhead="ext-audio switch", language=0, source=[3, 16])  # 9-16: ARC of output 1-8
    assert state.outputs[2].ext_audio_source == 16
    for comhead, payload in (("set ext-audio mode", {"mode": 3}), ("set ext-audio out", {"out": [9, 1]}),
                             ("ext-audio switch", {"source": [3, 17]}), ("set ext-audio index", {"index": 0})):
        assert run(state, comhead=comhead, **payload).response["result"] == proto.RESULT_FAIL


def test_reboot_and_unknown(state):
    assert run(state, comhead="reboot", language=0, reboot=1).reboot
    assert run(state, comhead="reboot", language=0).response["result"] == proto.RESULT_FAIL
    r = run(state, comhead="get bogus")
    assert not r.recognised and r.unanswered  # HIL-12: the device never answers unknown comheads
    assert run(state, comhead="set reboot").unanswered


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
    # captured: output 0 lists every output; a bad preset prints E01 before the echo, then E00
    assert len(handle(state, "r link out 0").lines) == 8
    assert handle(state, "r preset 9").text == "E01\r\nr preset 9!\r\nE00\r\n"


def test_telnet_routing_and_presets(state):
    r = handle(state, "s output 2 in source 6")
    assert r.mutated and r.lines == ["output2->input6"] and state.outputs[1].source == 6
    handle(state, "s output 0 in source 3")
    assert state.routing == [3] * 8
    handle(state, "s recall preset 1")
    assert state.routing == [2] * 8
    assert handle(state, "s av 7 1").lines == [proto.TELNET_ERR_UNKNOWN]  # captured: E00
    handle(state, "s output 1 in source 7")
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
    # captured: an unknown word is E00, a bad port E01
    assert handle(state, "s cec in 2 dance").lines == [proto.TELNET_ERR_UNKNOWN]
    assert handle(state, "s cec in 9 on").lines == [proto.TELNET_ERR_PARAM]


def test_telnet_misc(state):
    assert handle(state, "r fw version").lines == [
        "mcu fw version: v1.10.01", "key mcu       : v1.00.08", "web gui       : v2.00.03", "cpld version  : v1.00.06",
    ]
    assert handle(state, "r type").lines == ["8x8 hdmi2.1 matrix"]
    assert handle(state, "s power 0").lines == [proto.TELNET_ERR_PARAM]  # captured: E01
    assert state.system["power"] == 1
    assert handle(state, "power 0").lines == ["power off"]  # captured: the bare form works
    assert state.system["power"] == 0
    assert handle(state, "power 1").lines[:2] == ["power on", ""]
    handle(state, "s beep 0")
    handle(state, "s lock 1")
    assert handle(state, "s out 4 stream 0").lines == [proto.TELNET_ERR_UNKNOWN]  # captured: E00 (HIL-11)
    assert (state.system["beep"], state.system["panel_lock"], state.outputs[3].stream) == (0, 1, 1)
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


@pytest.mark.parametrize("command", _hub_telnet_commands())
def test_every_hub_telnet_command_is_recognised(state, command):
    result = handle(state, command)
    assert result.recognised and proto.TELNET_ERR_UNKNOWN not in result.lines


@pytest.mark.parametrize("word", sorted(set(OreiMatrix._CEC_INDEX_TO_TELNET.values())))
def test_every_hub_cec_word_is_accepted(state, word):
    assert handle(state, f"s cec in 1 {word}").lines == [f"cec in 1 {word}"]
    assert handle(state, f"s cec hdmi out 1 {word}").lines == [f"cec hdmi out 1 {word}"]
