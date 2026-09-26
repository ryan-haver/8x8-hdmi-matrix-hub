"""Driver setup and reconfigure, as the Remote's setup wizard runs it (audit §7 case 2).

Flow per core-api doc/integration-driver/driver-setup.md: ``setup_driver`` is
acknowledged, then the driver reports progress and the result with
``driver_setup_change`` events (``STOP`` + ``OK``/``ERROR``, or
``WAIT_USER_ACTION`` for another page).
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from tools.uc_remote_sim import UcRemoteSim
from tools.validate.device import SimDevice
from tools.validate.stack import SimulatorProcess, free_port

from ._helpers import CYCLE, INPUT_NAMES, POLL, known_bug, sent


def _config(hub) -> dict:
    return json.loads(Path(hub.data_dir, "config_state.json").read_text(encoding="utf-8"))


async def test_unconfigured_driver_offers_no_entities(uc_hub_factory) -> None:
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        assert await remote.get_available_entities() == []
        meta = (await remote.get_driver_metadata())["msg_data"]
        assert [s["id"] for s in meta["setup_data_schema"]["settings"]] == ["info", "host", "port"]


async def test_setup_connects_creates_entities_and_saves_the_configuration(
        uc_hub_factory, uc_simulator: SimulatorProcess, sim: SimDevice) -> None:
    """Setup works functionally (whatever it reports, see BE-02): entities, persisted config, control."""
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        outcome = await remote.setup_driver({"host": uc_simulator.host, "port": uc_simulator.https_port})
        assert outcome.response["code"] == 200 and outcome.response["msg"] == "result"
        assert outcome.events and outcome.events[-1]["event_type"] == "STOP"
        assert len(await remote.get_available_entities()) == 74
        config = _config(hub)
        assert (config["host"], config["port"]) == (uc_simulator.host, uc_simulator.https_port)
        assert config["input_names"]["6"] == "PS5"
        await remote.attach()
        assert (await remote.select_source("media_player.output_2", "PS5"))["code"] == 200
        assert (await sim.state())["outputs"][1]["source"] == 6


async def test_setup_reports_success(uc_hub_factory, uc_simulator: SimulatorProcess) -> None:
    """BE-02: a successful setup ends in STOP/OK (it used to end in ERROR 'OTHER')."""
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        outcome = await remote.setup_driver({"host": uc_simulator.host, "port": uc_simulator.https_port})
    assert outcome.final == {"event_type": "STOP", "state": "OK"}


async def test_setup_starts_live_updates_without_a_remote_connect(uc_hub_factory, uc_simulator: SimulatorProcess,
                                                                  sim: SimDevice) -> None:
    """After setup the entities follow the device at once (the poller starts with the configured matrix,
    not with a later Remote `connect`) and the device state is CONNECTED."""
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        outcome = await remote.setup_driver({"host": uc_simulator.host, "port": uc_simulator.https_port})
        assert outcome.state == "OK"
        assert (await remote.get_device_state())["msg_data"]["state"] == "CONNECTED"
        await remote.get_available_entities()
        await remote.subscribe_events(["media_player.output_2"])
        since = remote.mark()
        await sim.patch_state({"outputs": {"1": {"source": 7}}})
        await remote.wait_event("entity_change", lambda d: d["entity_id"] == "media_player.output_2"
                                and d["attributes"].get("source") == INPUT_NAMES[6], since=since, timeout=CYCLE)


async def test_setup_with_an_unreachable_matrix_fails_cleanly(uc_hub_factory) -> None:
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        outcome = await remote.setup_driver({"host": "127.0.0.1", "port": free_port()}, timeout=60)
        assert outcome.final == {"event_type": "STOP", "state": "ERROR", "error": "CONNECTION_REFUSED"}
        assert await remote.get_available_entities() == []
        assert not remote.closed
    assert not Path(hub.data_dir, "config_state.json").exists()


async def test_reconfigure_with_a_bad_address_keeps_the_working_setup(uc_remote: UcRemoteSim, uc_hub,
                                                                      sim: SimDevice) -> None:
    """UC-05: the new address is probed first; a typo leaves the working installation untouched."""
    before = _config(uc_hub)
    outcome = await uc_remote.setup_driver({"host": "127.0.0.1", "port": free_port()}, reconfigure=True, timeout=60)
    assert outcome.state == "ERROR"
    assert _config(uc_hub) == before
    assert len(await uc_remote.get_available_entities()) == 74
    resp = await uc_remote.select_source("media_player.output_1", "PS5")
    assert resp["code"] == 200
    assert (await sim.state())["outputs"][0]["source"] == 6


async def test_reconfigure_keeps_the_subscribed_entities_working(uc_remote: UcRemoteSim,
                                                                 uc_simulator: SimulatorProcess,
                                                                 sim: SimDevice) -> None:
    """UC-05: reconfigure never clears the subscribed entities (they used to answer 404 until resubscribed)."""
    outcome = await uc_remote.setup_driver({"host": uc_simulator.host, "port": uc_simulator.https_port},
                                           reconfigure=True)
    assert outcome.state == "OK"
    resp = await uc_remote.select_source("media_player.output_1", "PS5")
    assert resp["code"] == 200
    assert (await sim.state())["outputs"][0]["source"] == 6


async def test_reconfigure_to_another_matrix_disposes_the_old_connection(uc_remote: UcRemoteSim, uc_hub,
                                                                         uc_log_dir, sim: SimDevice) -> None:
    """BE-10: after a successful reconfigure to a new address the subscribed entities control the new matrix,
    and the old matrix client is disposed: the old device gets no more requests (no leaked poller/session)."""
    other = SimulatorProcess(log_dir=uc_log_dir / "new-matrix")
    await asyncio.to_thread(other.start)
    try:
        outcome = await uc_remote.setup_driver({"host": other.host, "port": other.https_port}, reconfigure=True)
        assert outcome.state == "OK"
        assert (_config(uc_hub)["host"], _config(uc_hub)["port"]) == (other.host, other.https_port)
        async with SimDevice(other.control_url) as new:
            await sim.clear_log()
            await new.clear_log()
            assert (await uc_remote.select_source("media_player.output_1", "PS5"))["code"] == 200
            assert (await new.state())["outputs"][0]["source"] == 6
            await asyncio.sleep(3 * POLL)
            assert sent(await new.log(), "get video status"), "the new matrix is polled"
            # HTTP only: the harness points every matrix client at the first simulator's Telnet port.
            old_http = [e.get("command") for e in await sim.log() if e.get("channel") == "http"]
            assert old_http == [], f"the old matrix is still used: {old_http}"
    finally:
        await asyncio.to_thread(other.stop)


async def test_abort_driver_setup_keeps_the_driver_usable(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    await uc_remote.abort_driver_setup("USER_CANCELLED")
    await asyncio.sleep(0.5)
    assert not uc_remote.closed
    assert (await uc_remote.select_source("media_player.output_1", "PS5"))["code"] == 200
    assert (await sim.state())["outputs"][0]["source"] == 6


@known_bug("UC-02", "port 9095 is unauthenticated: any LAN client's setup_driver repoints the hub at a new host, "
           "which receives the stored matrix credentials (login), and the change is saved")
async def test_unauthenticated_client_cannot_repoint_the_matrix(uc_remote_factory, uc_hub, uc_log_dir) -> None:
    attacker = SimulatorProcess(log_dir=uc_log_dir / "attacker")
    await asyncio.to_thread(attacker.start)
    try:
        before = _config(uc_hub)
        intruder = await uc_remote_factory(attach=False)  # no token, no pairing: just a WebSocket
        await intruder.setup_driver({"host": attacker.host, "port": attacker.https_port}, reconfigure=True)
        async with SimDevice(attacker.control_url) as evil:
            logins = [e for e in await evil.log() if e.get("command") == "login"]
        assert logins == [], "the hub logged in to the intruder's host with the stored matrix credentials"
        assert _config(uc_hub) == before
    finally:
        await asyncio.to_thread(attacker.stop)
