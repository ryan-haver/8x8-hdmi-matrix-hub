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

from ._helpers import CYCLE, INPUT_NAMES, POLL, known_bug, sent, wait_for


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


@known_bug("UC-17", "enter_standby disconnects the matrix, so the hub itself (web app, Home Assistant, kiosk) "
           "loses the matrix whenever the Remote sleeps")
async def test_remote_standby_keeps_the_matrix_connected(uc_remote: UcRemoteSim,
                                                         hub_api: aiohttp.ClientSession) -> None:
    assert await _hub_connected(hub_api)
    await uc_remote.enter_standby()
    await asyncio.sleep(POLL + 1)
    assert await _hub_connected(hub_api)


@known_bug("UC-06", "the driver keeps pushing while the Remote is in standby (here the UNAVAILABLE caused by "
           "disconnecting the matrix; pushes wake a sleeping Remote and drain its battery)")
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


@known_bug("UC-17", "the status poller (the only source of routing/signal/cable events on /ws) stops when the "
           "Remote sends `disconnect`")
async def test_front_panel_change_reaches_web_clients_after_the_remote_disconnects(
        uc_remote: UcRemoteSim, sim: SimDevice, hub_ws: WsObserver) -> None:
    await uc_remote.send_disconnect()
    assert await _routing_change_reaches_web_clients(sim, hub_ws, output=3, source=5)


@known_bug("UC-17", "the status poller only starts on a Remote `connect`; a hub no Remote has attached to never "
           "reports front-panel changes to the web app or Home Assistant")
async def test_front_panel_change_reaches_web_clients_without_any_remote(uc_hub, sim: SimDevice,
                                                                         hub_ws: WsObserver) -> None:
    assert await _routing_change_reaches_web_clients(sim, hub_ws, output=3, source=5)


# ---------------------------------------------------------------------- start-up (UC-19)


@known_bug("UC-19", "restore_from_config talks to the matrix before api.init(): a matrix that does not answer "
           "keeps the integration port closed until the HTTP timeouts expire")
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
