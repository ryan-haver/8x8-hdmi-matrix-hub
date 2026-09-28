"""Driver setup and reconfigure, as the Remote's setup wizard runs it (audit §7 case 2).

Flow per core-api doc/integration-driver/driver-setup.md: ``setup_driver`` is
acknowledged, then the driver reports progress and the result with
``driver_setup_change`` events (``STOP`` + ``OK``/``ERROR``, or
``WAIT_USER_ACTION`` for another page).

Since WP-B3 (UC-05, UC-02 short term) the setup has a credential step: the
first page gives the matrix address; for a new address the hub checks that it
accepts a connection (sending nothing), then asks for that matrix's login
(``user`` / ``password``) and logs in with exactly that login. The same
address as the working matrix needs no login page (its login already goes
there). The configured login is never sent to a new address.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import aiohttp

from tools.uc_remote_sim import SetupOutcome, UcRemoteSim
from tools.validate.device import SimDevice
from tools.validate.stack import HubProcess, SimulatorProcess, free_port

from ._helpers import CYCLE, INPUT_NAMES, POLL, known_bug, sent, wait_for

SEED_LOGIN = {"user": "Admin", "password": "admin"}  # tools/simulator/states/default.json "auth"


def _config(hub) -> dict:
    return json.loads(Path(hub.data_dir, "config_state.json").read_text(encoding="utf-8"))


def _login_page(outcome: SetupOutcome) -> list[dict[str, Any]]:
    """The settings of the WAIT_USER_ACTION page the driver sent (fails if it sent none)."""
    assert outcome.state == "WAIT_USER_ACTION", outcome.events
    return outcome.final["require_user_action"]["input"]["settings"]


async def _setup_with_login(remote: UcRemoteSim, host: str, port: int, *, reconfigure: bool = False,
                            login: dict[str, str] | None = None) -> SetupOutcome:
    """Address page, then the login page with ``login`` (the seed login by default)."""
    first = await remote.setup_driver({"host": host, "port": port}, reconfigure=reconfigure)
    _login_page(first)
    return await remote.set_driver_user_data(input_values=login or SEED_LOGIN)


def _logins(log: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [e for e in log if e.get("command") == "login"]


async def test_unconfigured_driver_offers_no_entities(uc_hub_factory) -> None:
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        assert await remote.get_available_entities() == []
        meta = (await remote.get_driver_metadata())["msg_data"]
        assert [s["id"] for s in meta["setup_data_schema"]["settings"]] == ["info", "host", "port"]


async def test_setup_connects_creates_entities_and_saves_the_configuration(
        uc_hub_factory, uc_simulator: SimulatorProcess, sim: SimDevice) -> None:
    """Setup works functionally: login page, entities, persisted config (with the entered login), control."""
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        outcome = await _setup_with_login(remote, uc_simulator.host, uc_simulator.https_port)
        assert outcome.response["code"] == 200 and outcome.response["msg"] == "result"
        assert outcome.events and outcome.events[-1]["event_type"] == "STOP"
        assert len(await remote.get_available_entities()) == 74
        config = _config(hub)
        assert (config["host"], config["port"]) == (uc_simulator.host, uc_simulator.https_port)
        assert (config["user"], config["password"]) == (SEED_LOGIN["user"], SEED_LOGIN["password"])
        assert config["input_names"]["6"] == "PS5"
        await remote.attach()
        assert (await remote.select_source("media_player.output_2", "PS5"))["code"] == 200
        assert (await sim.state())["outputs"][1]["source"] == 6


async def test_setup_reports_success(uc_hub_factory, uc_simulator: SimulatorProcess) -> None:
    """BE-02: a successful setup ends in STOP/OK (it used to end in ERROR 'OTHER')."""
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        outcome = await _setup_with_login(remote, uc_simulator.host, uc_simulator.https_port)
    assert outcome.final == {"event_type": "STOP", "state": "OK"}


async def test_a_new_address_asks_for_its_login_before_anything_is_sent(uc_hub_factory,
                                                                        uc_simulator: SimulatorProcess,
                                                                        sim: SimDevice) -> None:
    """UC-05 credential step: the first page only checks the address; the login page asks for the matrix's
    user and password (hidden field, never pre-filled) and nothing logs in before it is answered."""
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        await sim.clear_log()
        first = await remote.setup_driver({"host": uc_simulator.host, "port": uc_simulator.https_port})
        settings = {s["id"]: s for s in _login_page(first)}
        assert list(settings) == ["info", "user", "password"]
        assert settings["user"]["field"] == {"text": {"value": "Admin"}}
        assert settings["password"]["field"] == {"password": {}}  # hidden input, no default value
        assert _logins(await sim.log()) == [], "the hub logged in before the user entered the login"
        assert not Path(hub.data_dir, "config_state.json").exists()


async def test_a_wrong_password_is_an_authorization_error(uc_hub_factory, uc_simulator: SimulatorProcess,
                                                          sim: SimDevice) -> None:
    """UC-05 specific errors: a rejected login ends in AUTHORIZATION_ERROR and nothing is set up."""
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        outcome = await _setup_with_login(remote, uc_simulator.host, uc_simulator.https_port,
                                          login={"user": "Admin", "password": "not-the-password"})
        assert outcome.final == {"event_type": "STOP", "state": "ERROR", "error": "AUTHORIZATION_ERROR"}
        assert [e["login_ok"] for e in _logins(await sim.log())] == [False]
        assert await remote.get_available_entities() == []
        assert not remote.closed
    assert not Path(hub.data_dir, "config_state.json").exists()


async def test_setup_starts_live_updates_without_a_remote_connect(uc_hub_factory, uc_simulator: SimulatorProcess,
                                                                  sim: SimDevice) -> None:
    """After setup the entities follow the device at once (the poller starts with the configured matrix,
    not with a later Remote `connect`) and the device state is CONNECTED."""
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        outcome = await _setup_with_login(remote, uc_simulator.host, uc_simulator.https_port)
        assert outcome.state == "OK"
        assert (await remote.get_device_state())["msg_data"]["state"] == "CONNECTED"
        await remote.get_available_entities()
        await remote.subscribe_events(["media_player.output_2"])
        since = remote.mark()
        await sim.patch_state({"outputs": {"1": {"source": 7}}})
        await remote.wait_event("entity_change", lambda d: d["entity_id"] == "media_player.output_2"
                                and d["attributes"].get("source") == INPUT_NAMES[6], since=since, timeout=CYCLE)


async def test_matrix_host_serves_the_hub_before_any_remote_setup(uc_hub_factory,
                                                                   uc_simulator: SimulatorProcess) -> None:
    """Without a saved setup the driver uses MATRIX_HOST, so the web app has the matrix before a Remote is set up
    (the variable is never saved; the Remote's setup then saves the configuration as usual). The same address
    needs no login page: the hub's login already goes there."""
    hub = await uc_hub_factory(restore=False, extra_env={"MATRIX_HOST": uc_simulator.host,
                                                         "MATRIX_PORT": str(uc_simulator.https_port)})
    async with aiohttp.ClientSession(base_url=hub.base_url, headers={"X-Forwarded-For": "10.88.0.3"}) as web:
        async def web_connected() -> bool:
            async with web.get("/api/status") as resp:
                return bool(((await resp.json()).get("data") or {}).get("connected"))

        assert await wait_for(web_connected, timeout=CYCLE + 5)
    assert not Path(hub.data_dir, "config_state.json").exists()
    async with UcRemoteSim(hub.uc_url) as remote:
        assert len(await remote.get_available_entities()) == 74
        outcome = await remote.setup_driver({"host": uc_simulator.host, "port": uc_simulator.https_port})
        assert outcome.state == "OK"
    assert _config(hub)["host"] == uc_simulator.host
    assert "password" not in _config(hub)  # the environment's login (OREI_PASSWORD) is never written to the file


async def test_setup_with_an_unreachable_matrix_fails_cleanly(uc_hub_factory) -> None:
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        outcome = await remote.setup_driver({"host": "127.0.0.1", "port": free_port()}, timeout=60)
        assert outcome.final == {"event_type": "STOP", "state": "ERROR", "error": "CONNECTION_REFUSED"}
        assert await remote.get_available_entities() == []
        assert not remote.closed
    assert not Path(hub.data_dir, "config_state.json").exists()


async def test_setup_errors_name_the_problem(uc_hub_factory) -> None:
    """UC-05 specific errors: a name that does not resolve and an address that is not one are NOT_FOUND."""
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        unknown = await remote.setup_driver({"host": "no-such-matrix.invalid", "port": 443}, timeout=60)
        assert unknown.final == {"event_type": "STOP", "state": "ERROR", "error": "NOT_FOUND"}
        garbage = await remote.setup_driver({"host": "https://192.0.2.1/", "port": 443}, timeout=60)
        assert garbage.final == {"event_type": "STOP", "state": "ERROR", "error": "NOT_FOUND"}
        bad_port = await remote.setup_driver({"host": "127.0.0.1", "port": 70000}, timeout=60)
        assert bad_port.state == "ERROR"
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
    """UC-05: reconfigure never clears the subscribed entities (they used to answer 404 until resubscribed).
    The same address completes without a login page."""
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
        outcome = await _setup_with_login(uc_remote, other.host, other.https_port, reconfigure=True)
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


async def test_the_login_entered_for_a_matrix_is_used_after_a_restart(uc_remote: UcRemoteSim, uc_hub: HubProcess,
                                                                      uc_log_dir) -> None:
    """The login entered in the setup belongs to that matrix: saved with its address and used after a restart
    (the environment's OREI_PASSWORD, the seed 'admin', would be rejected by this matrix)."""
    other = SimulatorProcess(log_dir=uc_log_dir / "own-login")
    await asyncio.to_thread(other.start)
    try:
        async with SimDevice(other.control_url) as new:
            await new.patch_state({"auth": {"user": "Admin", "password": "matrix-2-login"}})
            outcome = await _setup_with_login(uc_remote, other.host, other.https_port, reconfigure=True,
                                              login={"user": "Admin", "password": "matrix-2-login"})
            assert outcome.state == "OK"
            await uc_remote.close()
            await asyncio.to_thread(uc_hub.restart)
            await new.clear_log()
            async with UcRemoteSim(uc_hub.uc_url) as remote:
                await remote.attach(["media_player.output_1"])
                assert (await remote.get_device_state())["msg_data"]["state"] == "CONNECTED"
                assert (await remote.select_source("media_player.output_1", "PS5"))["code"] == 200
            assert (await new.state())["outputs"][0]["source"] == 6
    finally:
        await asyncio.to_thread(other.stop)


async def test_abort_driver_setup_keeps_the_driver_usable(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    await uc_remote.abort_driver_setup("USER_CANCELLED")
    await asyncio.sleep(0.5)
    assert not uc_remote.closed
    assert (await uc_remote.select_source("media_player.output_1", "PS5"))["code"] == 200
    assert (await sim.state())["outputs"][0]["source"] == 6


async def test_abort_on_the_login_page_discards_the_new_address(uc_remote: UcRemoteSim, uc_hub, uc_log_dir,
                                                                sim: SimDevice) -> None:
    """UC-05 abort handling: an abort on the login page drops the pending address; a late login answer
    afterwards is refused and changes nothing."""
    other = SimulatorProcess(log_dir=uc_log_dir / "aborted")
    await asyncio.to_thread(other.start)
    try:
        before = _config(uc_hub)
        first = await uc_remote.setup_driver({"host": other.host, "port": other.https_port}, reconfigure=True)
        _login_page(first)
        await uc_remote.abort_driver_setup("OTHER")
        late = await uc_remote.set_driver_user_data(input_values=SEED_LOGIN)
        assert late.state == "ERROR"
        async with SimDevice(other.control_url) as new:
            assert _logins(await new.log()) == []
        assert _config(uc_hub) == before
        assert (await uc_remote.select_source("media_player.output_1", "PS5"))["code"] == 200
        assert (await sim.state())["outputs"][0]["source"] == 6
    finally:
        await asyncio.to_thread(other.stop)


async def test_the_setup_login_is_never_logged(uc_hub_factory, uc_simulator: SimulatorProcess) -> None:
    """UC-05: no setup payload in the hub's log (the driver never logs it; ucapi 0.7.0 redacts `password`)."""
    marker = "Pw-UC05-never-logged-7f3a"
    hub = await uc_hub_factory(restore=False)
    async with UcRemoteSim(hub.uc_url) as remote:
        outcome = await _setup_with_login(remote, uc_simulator.host, uc_simulator.https_port,
                                          login={"user": "Admin", "password": marker})
        assert outcome.error == "AUTHORIZATION_ERROR"
    await asyncio.to_thread(hub.stop)
    logs = "".join(p.read_text(encoding="utf-8", errors="replace") for p in hub.log_dir.glob("hub-uc-*.log"))
    assert "set_driver_user_data" in logs or "Setup: login" in logs  # the log is the right one and has the setup
    assert marker not in logs


async def test_a_new_host_never_receives_the_stored_credentials(uc_remote_factory, uc_hub, uc_log_dir) -> None:
    """UC-02 short term (WP-B3): a setup_driver naming another host gets the login page; the hub opens no login
    to that host with the configured credentials, and nothing is saved."""
    attacker = SimulatorProcess(log_dir=uc_log_dir / "attacker-short")
    await asyncio.to_thread(attacker.start)
    try:
        before = _config(uc_hub)
        intruder = await uc_remote_factory(attach=False)  # no token, no pairing: just a WebSocket
        outcome = await intruder.setup_driver({"host": attacker.host, "port": attacker.https_port}, reconfigure=True)
        _login_page(outcome)
        # A guess at the login page never makes the hub send the stored login either.
        await intruder.set_driver_user_data(input_values={"user": "Admin", "password": "a-guess"})
        async with SimDevice(attacker.control_url) as evil:
            logins = _logins(await evil.log())
        assert [e["login_ok"] for e in logins] == [False], "only the guessed login reached the other host"
        assert _config(uc_hub) == before
    finally:
        await asyncio.to_thread(attacker.stop)


@known_bug("UC-02", "port 9095 is unauthenticated: any LAN client can still repoint the hub at a host whose "
           "login it knows (its own device) and the change is saved; token auth is Phase 3 (WP-F1)")
async def test_unauthenticated_client_cannot_repoint_the_matrix(uc_remote_factory, uc_hub, uc_log_dir) -> None:
    attacker = SimulatorProcess(log_dir=uc_log_dir / "attacker")
    await asyncio.to_thread(attacker.start)
    try:
        before = _config(uc_hub)
        intruder = await uc_remote_factory(attach=False)  # no token, no pairing: just a WebSocket
        await _setup_with_login(intruder, attacker.host, attacker.https_port, reconfigure=True)
        assert _config(uc_hub) == before
    finally:
        await asyncio.to_thread(attacker.stop)
