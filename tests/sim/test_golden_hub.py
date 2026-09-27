"""The real hub against the real BK-808's answers (simulator in golden mode).

The simulator is seeded from the HIL Session 1 read capture of the owner's
matrix (MCU V1.10.01, web V2.00.03, ``tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03``)
and answers every captured read, the login and every Telnet read with the
captured bytes (``tools/simulator/golden.py``). So these tests run the hub's
real HTTP and Telnet parsing, and the REST API on top, against what the
device really sends: V2 evidence against real data (not V4: no live device,
and nothing here writes).

No test here talks to a device.
"""

from __future__ import annotations

import pytest

import rest_api.utils as api_utils
from rest_api import reset_rate_limiter, set_matrix_device
from rest_api.app import create_rest_app
from rest_api.core import _format_status
from tests.sim.conftest import DEVICE_CAPTURES, make_simulator

NAMES_IN = ["NES", "SNES", "Sega", "N64", "Switch", "PS3", "Apple", "Switcher"]
NAMES_OUT = ["TV", "Sound", "Out3", "Out4", "Out5", "Out6", "Out7", "Out8"]
INPUT_CABLES = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: True, 8: True}
OUTPUT_CABLES = {1: True, 2: True, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False}


@pytest.fixture
async def simulator():
    """Overrides tests/sim/conftest.py: the golden simulator (so `matrix` and co. use it)."""
    sim = make_simulator(DEVICE_CAPTURES)
    await sim.start()
    try:
        yield sim
    finally:
        await sim.stop()


def served_from_captures(sim, command: str) -> list[str]:
    return [e.get("golden") for e in sim.log if e.get("command") == command]


# ------------------------------------------------------------------ HTTP


async def test_login_and_status_reads_parse_the_device_bytes(matrix, simulator):
    assert await matrix.connect()  # the device answers {"comhead":"login","result":1}
    assert served_from_captures(simulator, "login") == ["verbatim"]

    status = await matrix.get_status(force_refresh=True)
    # allsource has 9 entries on this firmware (HIL-04); the hub keeps the 8 outputs.
    assert status["routing"] == [7] * 8
    assert status["input_names"] == NAMES_IN and status["output_names"] == NAMES_OUT
    assert status["power"] == "on"

    full = await matrix.get_full_status()
    assert (full["firmware_version"], full["web_version"], full["model"]) == ("V1.10.01", "V2.00.03", "BK-808")
    assert full["outputs_connected"] == [1, 1, 0, 0, 0, 0, 0, 0]
    # API values (1-based): the device reports scaler 0/4 and HDR 0 (HIL-02, BE-15)
    assert full["output_scaler"] == [1, 5, 1, 1, 1, 1, 1, 1]  # 1 = passthrough, 5 = audio only
    assert full["output_hdr"] == [1] * 8  # 1 = passthrough
    assert full["output_hdcp"] == [3] * 8  # follow sink
    assert full["output_enabled"] == [1, 1, 0, 0, 0, 0, 0, 0]
    assert full["input_edid"] == [36] * 8 and full["inputs_inactive"] == [0] * 8
    assert full["cec_inputs_enabled"] == [1, 0, 0, 0, 0, 0, 0, 0]
    assert full["beep_enabled"] is True and full["panel_locked"] is False

    caps = await matrix.get_output_capabilities(2)
    assert caps["is_audio_only"] is True  # scaler 4 = "audio only" in the device's Telnet status (BE-15)
    network = await matrix.get_network_info()
    assert network["subnet"] == "255.255.254.0" and "netmask" not in network

    for comhead in ("get video status", "get output status", "get input status", "get cec status",
                    "get system status", "get status", "get network"):
        assert set(served_from_captures(simulator, comhead)) == {"verbatim"}, comhead
    assert simulator.unrecognised() == []


async def test_get_preset_info_never_uses_the_http_preset_read(matrix, simulator):
    """HIL-01: V1.10.01 never answers `preset get`; without Telnet there is no preset read."""
    assert await matrix.connect()
    assert await matrix.get_preset_info(1) is None
    assert not [e for e in simulator.log if e.get("command") in ("preset get", "get routing status")]


# ------------------------------------------------------------------ REST


_GLOBALS = (
    "_matrix_device", "_input_names", "_output_names", "_config_file", "_scene_manager", "_profile_manager",
    "_macro_manager", "_system_shortcut_manager", "_dashboard_layout_manager",
)


@pytest.fixture
async def hub(aiohttp_client, matrix, monkeypatch, tmp_path):
    """The hub's REST API wired to a real OreiMatrix on the golden simulator."""
    for name in _GLOBALS:
        monkeypatch.setattr(api_utils, name, getattr(api_utils, name))
    monkeypatch.setattr(api_utils, "_input_names", {})
    monkeypatch.setattr(api_utils, "_output_names", {})
    reset_rate_limiter()
    assert await matrix.connect()
    set_matrix_device(matrix, config_dir=str(tmp_path), data_dir=str(tmp_path))
    client = await aiohttp_client(create_rest_app(data_dir=tmp_path))
    yield client
    reset_rate_limiter()


async def test_rest_status_from_real_device_answers(hub, simulator):
    data = (await (await hub.get("/api/status")).json())["data"]
    assert data["connected"] is True
    assert data["routing"] == {str(i): 7 for i in range(1, 9)}
    assert data["input_names"] == {str(i): n for i, n in enumerate(NAMES_IN, 1)}
    assert data["output_names"] == {str(i): n for i, n in enumerate(NAMES_OUT, 1)}
    assert data["power"] == "on"  # HA-03: clients read matrix power from /api/status

    outputs = (await (await hub.get("/api/status/outputs")).json())["data"]["outputs"]
    assert [o["number"] for o in outputs] == list(range(1, 9))
    assert [o["connected"] for o in outputs] == [True, True] + [False] * 6
    assert [o["enabled"] for o in outputs] == [True, True] + [False] * 6
    # HIL-02: read values are API values, so a client can write back what it read
    assert [o["hdr"] for o in outputs] == [1] * 8
    assert [o["scaler"] for o in outputs] == [1, 5, 1, 1, 1, 1, 1, 1]
    assert [o["hdcp"] for o in outputs] == [3] * 8


async def test_rest_output_status_endpoint_reports_api_values(hub, simulator):
    body = (await (await hub.get("/api/status/outputs")).json())["data"]
    assert [o["hdr"] for o in body["outputs"]] == [1] * 8
    assert [o["scaler"] for o in body["outputs"]] == [1, 5, 1, 1, 1, 1, 1, 1]
    assert body["raw"]["allscaler"] == [0, 4, 0, 0, 0, 0, 0, 0, 255]  # the device's own codes stay in `raw`


# ------------------------------------------------------------------ writes


@pytest.mark.parametrize("method, args, comhead", [
    ("set_beep", (False,), "set beep"),
    ("set_panel_lock", (True,), "set panel lock"),
    ("set_input_name", (8, "HIL-CAPTURE"), "set input name"),
    ("set_output_name", (8, "HIL-CAPTURE"), "set output name"),
    ("switch_input", (8, 8), "video switch"),
    ("switch_input_to_all", (8,), "video switch"),
    ("power_off", (), "set poweronoff"),
])
async def test_captured_writes_are_answered_with_the_device_bytes(matrix, simulator, method, args, comhead):
    """The writes captured on V1.10.01 get the device's own answer (result 1), and the hub accepts it."""
    assert await matrix.connect()
    assert await getattr(matrix, method)(*args) is True
    assert served_from_captures(simulator, comhead)[-1] == "verbatim"


async def test_cec_enable_bulk_answer_from_the_device(matrix, simulator):
    """HIL-10: the array form got result 1 on the device; the hub now always sends it."""
    assert await matrix.connect()
    assert await matrix.set_cec_enable("input", 8, True) is True
    sent = [e for e in simulator.log if e.get("command") == "set cec index"][-1]
    assert "inputindex" in sent["payload"] and sent.get("golden") == "verbatim"
    assert simulator.state.inputs[7].cec_enabled == 1


async def test_rest_save_current_scene_stores_api_hdr_values(hub, simulator):
    """HIL-02: the device reports HDR 0; a saved scene stores API value 1, which the setter accepts."""
    resp = await hub.post("/api/scene/save-current", json={"id": "hdr", "name": "HDR"})
    assert resp.status == 200, await resp.text()
    outputs = (await resp.json())["data"]["outputs"]
    assert {o["hdr_mode"] for o in outputs.values()} == {1}


async def test_rest_save_current_scene_uses_the_real_routing(hub, simulator):
    """Regression: the device's `get output status` has no allsource and 9-entry arrays, so the
    captured scene had every output on input 1 and an output 9."""
    resp = await hub.post("/api/scene/save-current", json={"id": "real", "name": "Real"})
    assert resp.status == 200, await resp.text()
    outputs = (await resp.json())["data"]["outputs"]
    assert sorted(int(k) for k in outputs) == list(range(1, 9))
    assert {o["input"] for o in outputs.values()} == {7}


def test_format_status_keeps_eight_outputs_of_a_nine_entry_allsource():
    """HIL-04: even if a 9-entry allsource reaches the REST formatter, only outputs 1-8 come out."""
    raw = {"routing": [7] * 9, "input_names": NAMES_IN, "output_names": NAMES_OUT, "preset_names": []}

    class _Device:
        host = "matrix"

    out = _format_status(raw, _Device(), {}, {})
    assert out["routing"] == dict.fromkeys(range(1, 9), 7) and len(out["outputs"]) == 8


@pytest.mark.parametrize(("raw_power", "expected"), [("on", "on"), ("off", "off"), (None, None)])
def test_format_status_reports_matrix_power(raw_power, expected):
    """HA-03: /api/status carries the matrix power ("on"/"off"); absent when the read had none."""
    raw = {"routing": [1] * 8, "input_names": NAMES_IN, "output_names": NAMES_OUT, "preset_names": []}
    if raw_power is not None:
        raw["power"] = raw_power

    class _Device:
        host = "matrix"

    assert _format_status(raw, _Device(), {}, {}).get("power") == expected


# ------------------------------------------------------------------ Telnet


async def test_telnet_banner_cables_and_presets_from_real_device_bytes(matrix_with_telnet, simulator):
    m = matrix_with_telnet
    assert await m.connect()
    assert m.telnet_connected
    assert m._telnet.firmware_version == "1.10.01"  # parsed from the banner behind the IAC negotiation
    cables = await m.get_all_cable_status(force_refresh=True)
    assert cables["inputs"] == INPUT_CABLES and cables["outputs"] == OUTPUT_CABLES
    assert await m.get_input_cable_status(7) is True
    assert await m.get_output_cable_status(3) is False
    assert await m.get_preset_info(1) == {
        "preset": 1, "routing": {1: 2, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4}, "saved": True,
    }
    assert await m.get_preset_info(5) == {"preset": 5, "routing": {}, "saved": False}
    assert await m._telnet.get_firmware_version() == "1.10.01"
    assert await m._telnet.get_device_type() == "8x8 hdmi2.1 matrix"
    served = {e["command"]: e.get("golden") for e in simulator.log if e["channel"] == "telnet" and "golden" in e}
    assert served["status"] == "verbatim" and served["r preset 1"] == "verbatim"
