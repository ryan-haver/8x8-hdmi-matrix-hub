"""BE-36: ``GET /api/presets`` reports the routing stored in the matrix's preset slots.

The real hub app, a real ``OreiMatrix`` with its Telnet client, and the
simulator. Each slot is read with Telnet ``r preset N`` (the only preset read
the BK-808 firmware answers, HIL-01/HIL-05). Names and favourites stay the
hub's; when a slot cannot be read the hub's saved routing is returned marked
``routing_source: "saved"``.
"""

from __future__ import annotations

import pytest

from .conftest import body


def _telnet(simulator) -> list[str]:
    return [e["command"] for e in simulator.log if e["channel"] == "telnet"]


def _set_routing(simulator, routes: list[int]) -> None:
    for out, src in zip(simulator.state.outputs, routes, strict=True):
        out.source = src


def _routes(slot: int) -> list[int]:
    return [(i + slot) % 8 + 1 for i in range(8)]


async def _presets(client) -> list[dict]:
    resp = await client.get("/api/presets")
    assert resp.status == 200, await resp.text()
    return (await body(resp))["data"]["presets"]


async def test_catalog_reads_every_slot_from_the_matrix(telnet_data_hub, simulator):
    """Slots changed behind the hub's back (front panel, another client) are reported as stored."""
    for idx, preset in enumerate(simulator.state.presets):
        preset.routing, preset.saved = _routes(idx + 1), True
    simulator.state.presets[4].saved = False  # an empty slot
    start = len(_telnet(simulator))

    presets = await _presets(telnet_data_hub)

    assert [f"r preset {n}" for n in range(1, 9)] == _telnet(simulator)[start:]
    for idx, preset in enumerate(presets):
        assert preset["routing_source"] == "matrix"
        expected = {} if idx == 4 else {str(o + 1): src for o, src in enumerate(_routes(idx + 1))}
        assert preset["routing"] == expected, preset
    # names stay the hub's (web app) data
    assert presets[0]["name"] == "Apple TV Everywhere"
    assert presets[1]["name"] == "Shield Night"
    assert set(presets[0]) >= {"number", "name", "routing", "endpoint", "save_endpoint"}


async def test_catalog_is_cached_and_a_save_invalidates_it(telnet_data_hub, simulator):
    await _presets(telnet_data_hub)
    start = len(_telnet(simulator))
    await _presets(telnet_data_hub)
    assert _telnet(simulator)[start:] == []  # served from the short cache (OREI_STATUS_CACHE_TTL)

    _set_routing(simulator, [3] * 8)
    resp = await telnet_data_hub.post("/api/preset/2/save", json={})
    assert resp.status == 200, await resp.text()
    start = len(_telnet(simulator))
    presets = await _presets(telnet_data_hub)
    assert len([c for c in _telnet(simulator)[start:] if c.startswith("r preset")]) == 8
    assert presets[1]["routing"] == {str(o): 3 for o in range(1, 9)}
    assert presets[1]["routing_source"] == "matrix"


async def test_custom_save_reports_the_full_stored_slot(telnet_data_hub, simulator):
    """A custom save of one output stores the whole live routing on the matrix; the catalog shows all of it."""
    _set_routing(simulator, [2, 3, 4, 5, 6, 7, 8, 1])
    resp = await telnet_data_hub.post("/api/preset/3/save", json={"routing": {"1": 8}})
    assert resp.status == 200, await resp.text()
    presets = await _presets(telnet_data_hub)
    expected = {str(o): src for o, src in enumerate([8, 3, 4, 5, 6, 7, 8, 1], 1)}
    assert simulator.state.presets[2].routing == [8, 3, 4, 5, 6, 7, 8, 1]
    assert presets[2]["routing"] == expected
    assert presets[2]["routing_source"] == "matrix"
    # the hub's fallback copy is the full mapping too, not just {"1": 8}
    settings = await body(await telnet_data_hub.get("/api/device-settings"))
    assert settings["data"]["presets"]["3"]["routing"] == expected


async def test_unreadable_slots_fall_back_to_saved_routing_marked_as_such(data_hub, simulator):
    """No Telnet link: the matrix cannot be asked, so the hub's own copy is returned and labelled."""
    presets = await _presets(data_hub)
    assert all(p["routing_source"] == "saved" for p in presets)
    assert presets[1]["routing"] == {"1": 5, "2": 5}  # the fixture's saved partial mapping
    assert presets[0]["routing"] == {}
    assert not [c for c in _telnet(simulator) if c.startswith("r preset")]


@pytest.mark.parametrize("fault", ["telnet_silent", "telnet_close_mid_command"])
async def test_a_failed_slot_read_is_never_reported_as_read(telnet_data_hub, simulator, fault, monkeypatch):
    import telnet_client

    monkeypatch.setattr(telnet_client, "COMMAND_TIMEOUT", 0.4)
    simulator.state.presets[0].routing, simulator.state.presets[0].saved = [4] * 8, True
    simulator.faults.update({fault: True, "telnet_fault_count": 1})
    start = len(_telnet(simulator))

    presets = await _presets(telnet_data_hub)

    # slot 1's answer was lost: the read stops there, and nothing is presented as read
    assert _telnet(simulator)[start:] == ["r preset 1"]
    assert all(p["routing_source"] == "saved" for p in presets)
    assert presets[0]["routing"] == {}
