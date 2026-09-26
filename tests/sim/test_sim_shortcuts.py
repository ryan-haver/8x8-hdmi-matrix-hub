"""Built-in shortcuts (``POST /api/system-shortcuts/{key}/execute``) on the real hub app, a real OreiMatrix and the simulator.

Hub data: ``tests/e2e/fixtures/data`` (``data_hub``); its
``system_shortcuts.json`` still stores the old default label "LCD: 10s".
WP-C1 regressions: API-01, API-06, API-07, API-08. Each test asserts the
effect on the simulator, not only the HTTP answer.
"""

from __future__ import annotations

import pytest

from .conftest import body, sim_writes


async def execute_shortcut(hub, key: str, params: dict | None = None):
    return await hub.post(f"/api/system-shortcuts/{key}/execute", json={"params": params or {}})


async def test_route_all_to_output_shortcut(data_hub, simulator):
    """API-01: route shortcuts called ``matrix.switch()``."""
    resp = await execute_shortcut(data_hub, "route_all_to_output", {"input": 3, "output": 2})
    assert resp.status == 200, await resp.text()
    assert simulator.state.outputs[1].source == 3


async def test_route_one_to_one_shortcut(data_hub, simulator):
    resp = await execute_shortcut(data_hub, "route_one_to_one")
    assert resp.status == 200, await resp.text()
    assert simulator.state.routing == [1, 2, 3, 4, 5, 6, 7, 8]


async def test_power_off_all_shortcut_sends_one_command(data_hub, simulator):
    """API-06."""
    resp = await execute_shortcut(data_hub, "power_off_all")
    assert resp.status == 200, await resp.text()
    assert simulator.state.system["power"] == 0
    assert len(sim_writes(simulator, "set poweronoff")) == 1


@pytest.mark.parametrize(("key", "value"), [("mute_all_audio", 1), ("unmute_all_audio", 0)])
async def test_mute_shortcuts(data_hub, simulator, key, value):
    for o in simulator.state.outputs:
        o.audio_mute = 1 - value
    resp = await execute_shortcut(data_hub, key)
    assert resp.status == 200, await resp.text()
    assert [o.audio_mute for o in simulator.state.outputs] == [value] * 8


@pytest.mark.parametrize(
    ("key", "lcd"),
    [("lcd_timeout_off", 0), ("lcd_timeout_always_on", 1), ("lcd_timeout_10s", 2), ("lcd_timeout_30s", 3),
     ("lcd_timeout_60s", 4)],
)
async def test_lcd_shortcuts_set_the_device_code(data_hub, simulator, key, lcd):
    """API-07: device codes 0 off, 1 always on, 2/3/4 = 15/30/60 s."""
    simulator.state.system["lcd_timeout"] = 3 if lcd != 3 else 0
    resp = await execute_shortcut(data_hub, key)
    assert resp.status == 200, await resp.text()
    assert simulator.state.system["lcd_timeout"] == lcd


async def test_lcd_15s_shortcut_is_labelled_15s(data_hub):
    """API-07 (owner-approved rename): the key stays ``lcd_timeout_10s``; the fixture's stored
    default label "LCD: 10s" is migrated, so the UI shows what the device does."""
    data = (await body(await data_hub.get("/api/system-shortcuts/lcd_timeout_10s")))["data"]
    assert data["key"] == "lcd_timeout_10s"
    assert data["label"] == "LCD: 15s"
    listed = (await body(await data_hub.get("/api/shortcuts")))["data"]["shortcuts"]
    assert {s["key"]: s["label"] for s in listed}["lcd_timeout_10s"] == "LCD: 15s"


@pytest.mark.parametrize(
    ("key", "check"),
    [
        ("preset_recall_3", lambda s: s.routing == [6] * 8),
        ("beep_off", lambda s: s.system["beep"] == 0),
        ("panel_lock_on", lambda s: s.system["panel_lock"] == 1),
    ],
)
async def test_other_shortcuts(data_hub, simulator, key, check):
    resp = await execute_shortcut(data_hub, key)
    assert resp.status == 200, await resp.text()
    assert check(simulator.state)


@pytest.mark.parametrize("key", ["route_one_to_one", "mute_all_audio", "power_off_all", "preset_recall_2",
                                 "beep_on", "lcd_timeout_30s", "route_all_to_output"])
async def test_a_rejected_shortcut_is_reported_as_failed(data_hub, simulator, key):
    """API-08: shortcut results were ignored, so every shortcut answered success."""
    simulator.faults.reject_writes = True
    resp = await execute_shortcut(data_hub, key)
    assert resp.status == 500, await resp.text()
    assert (await body(resp))["success"] is False
