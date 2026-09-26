"""Remote lifecycle: standby, wake, disconnect, and what the hub does without a Remote (audit §7 case 9).

The hub's own live updates (``/ws`` events for the web app and Home Assistant)
must not depend on a Remote being connected and awake (UC-17).
"""

from __future__ import annotations

import asyncio
import time

import aiohttp

from tools.uc_remote_sim import UcRemoteSim
from tools.validate.device import SimDevice
from tools.validate.runner import WsObserver
from tools.validate.stack import port_open

from ._helpers import CYCLE, INPUT_NAMES, POLL, sent, wait_for


async def _hub_connected(hub_api: aiohttp.ClientSession) -> bool:
    async with hub_api.get("/api/status") as resp:
        body = await resp.json()
    return resp.status == 200 and bool((body.get("data") or {}).get("connected"))


async def _routing_change_reaches_web_clients(sim: SimDevice, ws: WsObserver, output: int, source: int) -> bool:
    """Change routing on the front panel; does the hub tell its /ws clients?

    The poller reports a routing change by comparing two polls, so the change is made only after the poller
    (if it runs) had time for two polls.
    """
    await asyncio.sleep(2 * POLL + 0.5)
    t0 = time.time()
    await sim.patch_state({"outputs": {str(output - 1): {"source": source}}})

    async def seen() -> bool:
        return any(e["event"] == "routing_change" and (e["data"] or {}).get("output") == output
                   for e in ws.since(t0))

    return await wait_for(seen, timeout=3 * POLL + CYCLE)


# ---------------------------------------------------------------------- standby / wake


async def test_remote_standby_keeps_the_matrix_connected(uc_remote: UcRemoteSim,
                                                         hub_api: aiohttp.ClientSession) -> None:
    """UC-17: the hub (web app, Home Assistant, kiosk) keeps the matrix while the Remote sleeps."""
    assert await _hub_connected(hub_api)
    await uc_remote.enter_standby()
    await asyncio.sleep(POLL + 1)
    assert await _hub_connected(hub_api)


async def test_no_pushes_while_the_remote_is_in_standby(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    await uc_remote.wait_event("entity_change", lambda d: d["entity_id"] == "media_player.output_8", timeout=CYCLE)
    await asyncio.sleep(POLL)
    since = uc_remote.mark()
    await uc_remote.enter_standby()
    await sim.patch_state({"outputs": {"0": {"source": 4}}})  # something to report
    await asyncio.sleep(3 * POLL + 1)
    assert uc_remote.entity_changes(since) == []
    assert uc_remote.events_since(since) == []


async def test_wake_resyncs_with_exactly_one_poller(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    """exit_standby: what changed during standby reaches the Remote, and polling runs once (not doubled, UC-06)."""
    await uc_remote.enter_standby()
    await sim.patch_state({"outputs": {"0": {"source": 4}}})
    await asyncio.sleep(POLL + 1)
    since = uc_remote.mark()
    await uc_remote.exit_standby()
    await uc_remote.wait_event(
        "entity_change",
        lambda d: d["entity_id"] == "media_player.output_1" and d["attributes"].get("source") == INPUT_NAMES[3],
        since=since, timeout=CYCLE + 2)
    await sim.clear_log()
    window = 5 * POLL
    await asyncio.sleep(window)
    polls = len(sent(await sim.log(), "get video status"))
    assert 1 <= polls <= window / POLL + 1, f"{polls} routing reads in {window}s with a {POLL}s poll interval"


# ---------------------------------------------------------------------- hub liveness without a Remote (UC-17)


async def test_front_panel_change_reaches_web_clients_while_a_remote_is_attached(
        uc_remote: UcRemoteSim, sim: SimDevice, hub_ws: WsObserver) -> None:
    """Baseline for the two UC-17 tests below: with an attached Remote the poller feeds /ws."""
    assert await _routing_change_reaches_web_clients(sim, hub_ws, output=3, source=5)


async def test_front_panel_change_reaches_web_clients_after_the_remote_disconnects(
        uc_remote: UcRemoteSim, sim: SimDevice, hub_ws: WsObserver) -> None:
    """UC-17: the Remote's `disconnect` does not stop the hub's poller."""
    await uc_remote.send_disconnect()
    assert await _routing_change_reaches_web_clients(sim, hub_ws, output=3, source=5)


async def test_front_panel_change_reaches_web_clients_after_the_remote_goes_away(
        uc_remote: UcRemoteSim, sim: SimDevice, hub_ws: WsObserver) -> None:
    """UC-17: the Remote's WebSocket closing (ucapi CLIENT_DISCONNECTED) does not stop the hub's poller."""
    await uc_remote.enter_standby()
    await uc_remote.close()
    assert await _routing_change_reaches_web_clients(sim, hub_ws, output=3, source=5)


async def test_front_panel_change_reaches_web_clients_without_any_remote(uc_hub, sim: SimDevice,
                                                                         hub_ws: WsObserver) -> None:
    """UC-17: the poller starts with the hub; no Remote has to attach for the web app to get live events."""
    assert await _routing_change_reaches_web_clients(sim, hub_ws, output=3, source=5)


async def test_repeated_connects_and_wakes_keep_one_poller(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    """UC-06: `connect`, standby and wake never start another poller (they used to double the traffic)."""
    for _ in range(3):
        since = uc_remote.mark()
        await uc_remote.send_connect()
        await uc_remote.wait_event("device_state", since=since, timeout=15)
        await uc_remote.enter_standby()
        await uc_remote.exit_standby()
    await asyncio.sleep(POLL + 0.5)
    await sim.clear_log()
    window = 5 * POLL
    await asyncio.sleep(window)
    polls = len(sent(await sim.log(), "get video status"))
    assert 1 <= polls <= window / POLL + 1, f"{polls} routing reads in {window}s with a {POLL}s poll interval"


# ---------------------------------------------------------------------- start-up (UC-19)


async def test_integration_port_opens_promptly_when_the_matrix_hangs(uc_hub_factory, sim: SimDevice) -> None:
    baseline = await uc_hub_factory(wait=False)
    t0 = time.monotonic()
    await asyncio.to_thread(baseline.wait_ready, 60)
    normal = time.monotonic() - t0
    await asyncio.to_thread(baseline.stop)

    await sim.set_faults({"hang_http": True})
    hub = await uc_hub_factory(wait=False)
    t0 = time.monotonic()
    budget = normal + 2.0

    async def listening() -> bool:
        return await asyncio.to_thread(port_open, hub.host, hub.uc_port)

    opened = await wait_for(listening, timeout=budget + 10, interval=0.25)
    took = time.monotonic() - t0
    assert opened, "integration port never opened"
    assert took <= budget, f"integration port opened after {took:.1f}s (normal start-up {normal:.1f}s)"
    # The entities were restored from the saved configuration without waiting for the matrix.
    async with UcRemoteSim(hub.uc_url) as remote:
        assert len(await remote.get_available_entities()) == 74
