"""Unit tests for the simulator's device state model."""

import json

import pytest

from tools.simulator import DeviceState, StateError, load_capture_dir


def test_default_state_matches_seed_spec():
    s = DeviceState.default()
    assert s.column("inputs", "name") == [
        "PS3", "AppleTV", "Computer", "Switch", "Shield", "PS5", "Analogue", "Input 8",
    ]
    assert s.column("outputs", "name") == ["TV", "Soundbar"] + [f"Output {i}" for i in range(3, 9)]
    assert s.column("outputs", "connected") == [1, 1, 0, 0, 0, 0, 0, 0]
    assert [i for i, p in enumerate(s.inputs, 1) if p.signal] == [2, 5, 6]
    assert s.routing[:2] == [2, 2]  # TV and Soundbar watch the Apple TV
    assert len(s.presets) == 8 and all(len(p.routing) == 8 for p in s.presets)
    assert s.auth == {"user": "Admin", "password": "admin"}


def test_round_trip():
    s = DeviceState.default()
    again = DeviceState.from_dict(json.loads(json.dumps(s.to_dict())))
    assert again.to_dict() == s.to_dict()


def test_partial_document_uses_defaults():
    s = DeviceState.from_dict({"system": {"power": 0}})
    assert s.system["power"] == 0
    assert s.column("inputs", "name")[0] == "Input 1"
    assert s.routing == [1] * 8


@pytest.mark.parametrize(
    "doc, fragment",
    [
        ({"schema_version": 99}, "schema_version"),
        ({"inputs": [{}] * 7}, "inputs"),
        ({"outputs": [{"source": 9}] + [{}] * 7}, "outputs[0].source"),
        ({"outputs": [{"hdcp": 0}] + [{}] * 7}, "outputs[0].hdcp"),
        ({"inputs": [{"bogus": 1}] + [{}] * 7}, "unknown keys"),
        ({"system": {"lcd_timeout": 9}}, "lcd_timeout"),
        ({"presets": [{"routing": [1] * 7}] + [{}] * 7}, "presets[0].routing"),
    ],
)
def test_invalid_documents_rejected(doc, fragment):
    with pytest.raises(StateError, match=fragment.replace("[", r"\[").replace("]", r"\]")):
        DeviceState.from_dict(doc)


def test_merged_patches_ports_by_index():
    s = DeviceState.default()
    patched = s.merged({"outputs": {"0": {"connected": 0}}, "system": {"beep": 0}})
    assert patched.outputs[0].connected == 0
    assert patched.outputs[1].connected == 1
    assert patched.system["beep"] == 0
    assert s.outputs[0].connected == 1  # original untouched


def test_apply_http_captures_from_documented_examples(tmp_path):
    """Golden captures (HIL-A) seed the state; shapes from OREI_API_COMMANDS.md."""
    captures = {
        "get_output_status.json": {
            "comhead": "get output status",
            "allconnect": [1, 0, 1, 0, 0, 0, 0, 0],
            "allscaler": [1, 1, 1, 1, 1, 1, 1, 4],  # device codes 0-4
            "allhdr": [2] * 8,  # device codes 0-2
            "allhdcp": [2] * 8,
            "allarc": [0] * 8,
            "allout": [1] * 8,
            "allaudiomute": [0] * 8,
            "allsource": [3, 3, 3, 3, 3, 3, 3, 3],
        },
        "get_input_status.json": {"comhead": "get input status", "edid": [3] * 8, "inactive": [0, 0, 1, 0, 0, 0, 1, 1]},
        "get_cec_status.json": {"comhead": "get cec status", "inputindex": [1] + [0] * 7, "outputindex": [1, 1] + [0] * 6},
        "get_status.json": {"comhead": "get status", "version": "V1.10.01", "webversion": "V2.00.03"},
        "get_video_status.json": {
            "comhead": "get video status",
            "power": 1,
            "allsource": [4] * 8,
            "allinputname": [f"Src{i}" for i in range(1, 9)],
            "alloutputname": [f"Dst{i}" for i in range(1, 9)],
            "allname": [f"P{i}" for i in range(1, 9)],
        },
        "_notes.json": {"ignored": True},
    }
    for name, doc in captures.items():
        (tmp_path / name).write_text(json.dumps(doc), encoding="utf-8")

    loaded = load_capture_dir(tmp_path)
    assert "get output status" in loaded and len(loaded) == 5

    s = DeviceState.default()
    s.apply_http_captures(loaded)
    assert s.column("outputs", "connected") == [1, 0, 1, 0, 0, 0, 0, 0]
    assert s.column("outputs", "hdcp") == [2] * 8
    assert s.column("inputs", "signal") == [0, 0, 1, 0, 0, 0, 1, 1]
    assert s.column("inputs", "cec_enabled")[0] == 1
    assert s.device["firmware_version"] == "V1.10.01"
    # video status is applied first, output status' allsource wins afterwards
    assert s.routing == [3] * 8
    assert s.column("inputs", "name")[0] == "Src1"
    assert s.presets[0].name == "P1"
