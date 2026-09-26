"""What the Remote is told about the matrix (audit §7 cases 4, 6, 7, 8, 10).

Entity states are compared with the simulator's ground truth; changes made
behind the hub's back (front panel, cable, signal) must reach the Remote within
one poll cycle; outages must be reported, not papered over.
"""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from tools.uc_remote_sim import UcRemoteSim
from tools.validate.device import SimDevice

from ._helpers import CYCLE, INPUT_NAMES, POLL, known_bug, wait_for

#: Entities whose state follows the device (buttons are stateless).
STATEFUL = ("media_player.", "sensor.", "switch.", "remote.")


def expected_attributes(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The attributes the driver's own mapping yields for a simulator state document."""
    names = [p["name"] for p in state["inputs"]]
    exp: dict[str, dict[str, Any]] = {}
    for n, out in enumerate(state["outputs"], 1):
        source = names[out["source"] - 1]
        exp[f"media_player.output_{n}"] = {"source": source, "source_list": names}
        exp[f"sensor.output_{n}_source"] = {"value": source}
        exp[f"sensor.output_{n}_connected"] = {"value": "Connected" if out["connected"] else "Disconnected"}
    for n, inp in enumerate(state["inputs"], 1):
        exp[f"sensor.input_{n}_signal"] = {"value": "Active" if inp["signal"] else "No Signal"}
    return exp


def mismatches(states: list[dict[str, Any]], expected: dict[str, dict[str, Any]]) -> list[str]:
    actual = {e["entity_id"]: e["attributes"] for e in states}
    out = []
    for eid, attrs in expected.items():
        for key, value in attrs.items():
            if actual.get(eid, {}).get(key) != value:
                out.append(f"{eid}.{key}: {actual.get(eid, {}).get(key)!r} != {value!r}")
    return out


async def test_subscribed_entity_states_reflect_the_device(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    expected = expected_attributes(await sim.state())
    last: list[str] = []

    async def in_sync() -> bool:
        nonlocal last
        last = mismatches(await uc_remote.get_entity_states(), expected)
        return not last

    assert await wait_for(in_sync), last
    states = {e["entity_id"]: e for e in await uc_remote.get_entity_states()}
    assert len(states) == 74, "every subscribed entity has a state"
    assert all(e["entity_type"] == eid.split(".")[0] for eid, e in states.items())


async def test_front_panel_routing_change_reaches_the_remote(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    """A change the hub did not make (front panel, IR) shows up within one poll cycle."""
    since = uc_remote.mark()
    await sim.patch_state({"outputs": {"1": {"source": 7}}})
    event = await uc_remote.wait_event(
        "entity_change",
        lambda d: d["entity_id"] == "media_player.output_2" and d["attributes"].get("source") == INPUT_NAMES[6],
        since=since, timeout=CYCLE)
    assert event.t - since <= CYCLE
    assert (await uc_remote.entity_state("sensor.output_2_source"))["value"] == INPUT_NAMES[6]


async def test_signal_and_cable_changes_reach_the_remote(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    since = uc_remote.mark()
    await sim.event({"type": "signal", "port": 3, "present": True})
    await sim.event({"type": "cable", "port_type": "output", "port": 1, "connected": False})
    await uc_remote.wait_event(
        "entity_change", lambda d: d["entity_id"] == "sensor.input_3_signal" and d["attributes"]["value"] == "Active",
        since=since, timeout=CYCLE)
    await uc_remote.wait_event(
        "entity_change",
        lambda d: d["entity_id"] == "sensor.output_1_connected" and d["attributes"]["value"] == "Disconnected",
        since=since, timeout=CYCLE)


@known_bug("UC-07", "every poll re-sends every attribute of every subscribed entity, changed or not")
async def test_unchanged_attributes_are_not_resent(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    # Let the first poll after subscribing sync everything, then change nothing for three cycles.
    await uc_remote.wait_event("entity_change", lambda d: d["entity_id"] == "media_player.output_8", timeout=CYCLE)
    await asyncio.sleep(POLL + 0.5)
    since = uc_remote.mark()
    await asyncio.sleep(3 * POLL + 0.5)
    changes = uc_remote.entity_changes(since)
    assert changes == [], f"{len(changes)} entity_change messages for a device that did not change"


# ---------------------------------------------------------------------- outages (UC-04)


async def _outage(remote: UcRemoteSim, sim: SimDevice, faults: dict[str, Any] | None = None) -> float:
    since = remote.mark()
    await sim.set_faults(faults or {"drop_http": True})
    await remote.wait_event("entity_change", lambda d: d["entity_id"] == "remote.orei_matrix"
                            and d["attributes"].get("state") == "UNAVAILABLE", since=since, timeout=CYCLE)
    return since


@known_bug("UC-04", "device state is always CONNECTED: a matrix outage never sends DISCONNECTED/ERROR")
async def test_matrix_outage_changes_the_device_state(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    since = await _outage(uc_remote, sim)
    await asyncio.sleep(POLL + 1)
    assert set(uc_remote.device_states(since)) & {"ERROR", "DISCONNECTED", "CONNECTING"}
    assert (await uc_remote.get_device_state())["msg_data"]["state"] != "CONNECTED"


@known_bug("UC-04", "during an outage only remote.orei_matrix goes UNAVAILABLE; every other entity keeps "
           "showing live-looking values")
async def test_entities_are_unavailable_during_an_outage(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    await _outage(uc_remote, sim)
    await asyncio.sleep(POLL + 1)
    states = [e for e in await uc_remote.get_entity_states() if e["entity_id"].startswith(STATEFUL)]
    live = [e["entity_id"] for e in states if e["attributes"].get("state") != "UNAVAILABLE"]
    assert live == []


@known_bug("UC-04", "the poll that hits the outage still pushes placeholders: when the routing read fails but "
           "the output status comes from the cache, every output's source becomes 'Input 0' (media player and "
           "source sensor)")
async def test_no_values_are_made_up_during_an_outage(uc_hub_factory, sim: SimDevice) -> None:
    """Nothing the Remote is told during an outage may contradict the device: last known values stay.

    The output-status cache (OREI_STATUS_CACHE_TTL, default 3 s) decides whether the failing poll still has
    data to push; a long TTL makes that deterministic here (with the default it happens on most outages).
    """
    hub = await uc_hub_factory(extra_env={"OREI_STATUS_CACHE_TTL": "600"})
    truth = expected_attributes(await sim.state())
    async with UcRemoteSim(hub.uc_url) as remote:
        await remote.attach()
        await remote.wait_event("entity_change", lambda d: d["entity_id"] == "media_player.output_8", timeout=CYCLE)
        since = await _outage(remote, sim)
        await asyncio.sleep(3 * POLL)
        made_up = [
            c for c in remote.entity_changes(since)
            if any(truth.get(c["entity_id"], {}).get(k, v) != v for k, v in c["attributes"].items())
        ]
        assert made_up == []
        assert mismatches(await remote.get_entity_states(), truth) == []


async def test_one_unanswered_status_read_keeps_the_remote_live(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    """HIL-12: the BK-808 can leave a request unanswered (captured on V1.10.01). One unanswered status read is a
    failed read, not an outage: the health read answers, the link stays up, the Remote is never told the
    matrix is unavailable, and live updates keep coming."""
    await uc_remote.wait_event("entity_change", lambda d: d["entity_id"] == "media_player.output_8", timeout=CYCLE)
    since = uc_remote.mark()
    await sim.clear_log()
    await sim.set_faults({"hang_http": True, "comheads": ["get video status"], "http_fault_count": 1})

    async def health_read_after_the_fault() -> bool:
        comheads = [(e.get("command"), e.get("fault")) for e in await sim.log() if e.get("channel") == "http"]
        hung = [i for i, (_, fault) in enumerate(comheads) if fault == "hang_http"]
        return bool(hung) and ("get system status", None) in comheads[hung[0] + 1:]

    # The poll that hits the fault waits out the hub's HTTP timeout (5 s); then the health read answers.
    assert await wait_for(health_read_after_the_fault, timeout=CYCLE + 5 + 2)
    await sim.patch_state({"outputs": {"2": {"source": 8}}})

    async def updated() -> bool:
        return any(c["entity_id"] == "media_player.output_3" and c["attributes"].get("source") == INPUT_NAMES[7]
                   for c in uc_remote.entity_changes(since))

    assert await wait_for(updated, timeout=CYCLE + 2)
    unavailable = [c for c in uc_remote.entity_changes(since)
                   if c["entity_id"] == "remote.orei_matrix" and c["attributes"].get("state") == "UNAVAILABLE"]
    assert unavailable == []


@known_bug("BE-06", "after the matrix link drops once, the driver's reconnect loop stops itself (the matrix's "
           "own reconnect emits CONNECTED -> _stop_reconnection) and the poller is never restarted, so the "
           "Remote gets no more updates (UC-04)")
async def test_live_updates_resume_after_a_transient_failure(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    await uc_remote.wait_event("entity_change", lambda d: d["entity_id"] == "media_player.output_8", timeout=CYCLE)
    # A real, short link loss: the matrix drops the connection. (Since HIL-12 a single failed status read is
    # no longer a lost link -- test_one_unanswered_status_read_keeps_the_remote_live -- so it cannot trigger
    # the reconnect path any more.)
    await _outage(uc_remote, sim, {"drop_http": True})
    await sim.clear_faults()
    await asyncio.sleep(8)  # the hub's reconnect back-off (5 s) plus a poll
    since = uc_remote.mark()
    await sim.patch_state({"outputs": {"2": {"source": 8}}})

    async def updated() -> bool:
        return any(c["entity_id"] == "media_player.output_3" and c["attributes"].get("source") == INPUT_NAMES[7]
                   for c in uc_remote.entity_changes(since))

    assert await wait_for(updated, timeout=CYCLE + 5)


@known_bug("UC-04", "a driver started while the matrix is unreachable reports CONNECTED and seeds its sensors "
           "with made-up values ([0]*8: every display 'Disconnected', every source 'No Signal')")
async def test_starting_with_the_matrix_offline_reports_no_made_up_state(uc_hub_factory, sim: SimDevice) -> None:
    await sim.set_faults({"drop_http": True})
    hub = await uc_hub_factory()
    async with UcRemoteSim(hub.uc_url) as remote:
        await remote.attach()
        states = {e["entity_id"]: e["attributes"] for e in await remote.get_entity_states()}
        # The seed has the TV connected to output 1 and a signal on input 2. Unknown is fine, wrong is not.
        assert states["sensor.output_1_connected"].get("value") != "Disconnected"
        assert states["sensor.input_2_signal"].get("value") != "No Signal"
        assert (await remote.get_device_state())["msg_data"]["state"] != "CONNECTED"


# ---------------------------------------------------------------------- names (UC-08, UC-14)


async def _rename_input(hub_api: aiohttp.ClientSession, port: int, name: str) -> None:
    async with hub_api.post(f"/api/input/{port}/name", json={"name": name}) as resp:
        assert resp.status == 200, await resp.text()


@known_bug("UC-08", "a rename in the web app never reaches the subscribed media players: their source_list keeps "
           "the old names")
async def test_input_rename_updates_the_source_list(uc_remote: UcRemoteSim, sim: SimDevice,
                                                    hub_api: aiohttp.ClientSession) -> None:
    await _rename_input(hub_api, 3, "Xbox")
    assert (await sim.state())["inputs"][2]["name"] == "Xbox"

    async def renamed() -> bool:
        state = await uc_remote.entity_state("media_player.output_1")
        return "Xbox" in (state or {}).get("source_list", [])

    assert await wait_for(renamed, timeout=CYCLE + 2)


@known_bug("UC-08", "after a rename and a Remote reconnect the driver rebuilds available_entities only; the "
           "subscribed media player still matches sources against the old names, so the new name is rejected (400)")
async def test_select_source_by_new_name_after_rename(uc_remote: UcRemoteSim, sim: SimDevice,
                                                      hub_api: aiohttp.ClientSession) -> None:
    await _rename_input(hub_api, 3, "Xbox")
    since = uc_remote.mark()
    await uc_remote.send_connect()  # what the Remote sends when it reconnects / wakes
    await uc_remote.wait_event("device_state", since=since, timeout=15)
    available = {e["entity_id"]: e for e in await uc_remote.get_available_entities()}
    assert available["remote.input_3_cec"]["name"] == {"en": "Xbox CEC"}  # the rebuilt entity has the new name
    resp = await uc_remote.select_source("media_player.output_1", "Xbox")
    assert resp["code"] == 200
    assert (await sim.state())["outputs"][0]["source"] == 3


@known_bug("UC-14", "preset names on the Remote are hard-coded 'Preset N'; the web app's preset names (device "
           "settings) are ignored")
async def test_preset_names_match_the_web_app(uc_remote: UcRemoteSim, hub_api: aiohttp.ClientSession) -> None:
    async with hub_api.get("/api/presets") as resp:
        body = await resp.json()
    web_names = {p["number"]: p["name"] for p in body["data"]["presets"]}
    assert web_names[1] == "Apple TV Everywhere"  # tests/e2e/fixtures/data/device_settings.json
    available = {e["entity_id"]: e for e in await uc_remote.get_available_entities()}
    remote_names = {n: available[f"button.preset_{n}"]["name"]["en"] for n in range(1, 9)}
    assert remote_names == web_names

