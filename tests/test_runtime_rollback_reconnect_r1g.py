"""Rollback recovery through the real runtime and loopback HTTPS/Telnet simulator."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

import hub.runtime.composition as composition
import orei_matrix
from hub import cli
from hub.persistence import reset_preparation
from hub.runtime.config import MatrixAddress
from tools.simulator import DeviceState, Simulator
from tools.validate.stack import free_port


class LoginGateSimulator(Simulator):
    """Gate delivery of a real login response, after normal fault dispatch."""

    def __init__(self):
        state = DeviceState.default()
        state.auth = {"user": "original-user", "password": "original-secret"}
        super().__init__(state, https_port=0, telnet_port=0, control_port=0)
        self.login_count = 0
        self.hold_login = None
        self.received = asyncio.Event()
        self.release = asyncio.Event()

    async def _handle_instr(self, request):
        login = (await request.json()).get("comhead") == "login"
        if login:
            self.login_count += 1
        hold = login and self.login_count == self.hold_login
        response = await super()._handle_instr(request)
        if hold:
            self.received.set()
            await self.release.wait()
        return response


async def ready(predicate):
    """Wait for an observable state under a deadline; no elapsed-delay oracle."""
    async with asyncio.timeout(3):
        while not predicate():
            await asyncio.sleep(0.01)


@pytest.fixture
async def runtime_sim(tmp_path, monkeypatch):
    assert Path(composition.__file__).resolve().is_relative_to(Path(__file__).resolve().parents[1] / "src")
    monkeypatch.setattr("rest_api.utils._runtime", None)
    monkeypatch.setattr(orei_matrix, "INITIAL_RETRY_DELAY", 0.02)
    monkeypatch.setattr(orei_matrix, "MAX_RETRY_DELAY", 0.04)
    for key in ("OREI_VERIFY_SSL", "OREI_TLS_CA", "OREI_TLS_FINGERPRINT"):
        monkeypatch.delenv(key, raising=False)
    reset_preparation()
    runtimes = []
    async with LoginGateSimulator() as sim:

        async def make(*, auto_reconnect=True, initial_faults=0):
            config = tmp_path / "config"
            config.mkdir()
            saved = config / "config_state.json"
            saved.write_text(
                json.dumps(
                    {
                        "host": "127.0.0.1",
                        "port": sim.https_port,
                        "telnet_port": sim.telnet_port,
                        "user": "original-user",
                        "password": "original-secret",
                        "input_names": {"1": "Saved console"},
                        "output_names": {"1": "Saved screen"},
                        "extension": {"retained": True},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            env = {
                "DATA_DIR": str(tmp_path / "data"),
                "UC_CONFIG_HOME": str(config),
                "MATRIX_HOST": "127.0.0.1",
                "MATRIX_PORT": str(sim.https_port),
                "OREI_TELNET_PORT": str(sim.telnet_port),
                "API_PORT": str(free_port()),
                "OREI_USER": "original-user",
                "OREI_PASSWORD": "original-secret",
                "OREI_AUTO_RECONNECT": str(auto_reconnect).lower(),
                "UC_ENABLED": "false",
                "FLIC_ENABLED": "false",
                "HA_DISCOVERY_ENABLED": "false",
                "STATUS_POLL_INTERVAL": "0.2",
            }
            for key, value in env.items():
                monkeypatch.setenv(key, value)
            clients = []

            def factory(*args, **kwargs):
                client = orei_matrix.OreiMatrix(*args, **kwargs)
                clients.append(client)
                return client

            runtime = composition.build_runtime(cli.load_settings(env), environ=env, matrix_factory=factory)
            runtimes.append(runtime)
            if initial_faults:
                sim.faults.update({"http_status": 503, "comheads": ["login"], "http_fault_count": initial_faults})
            await runtime.start()
            await asyncio.wait_for(runtime._connect_task, 3)
            return runtime, sim, clients, saved

        try:
            yield make
        finally:
            sim.release.set()
            for runtime in runtimes:
                await asyncio.wait_for(runtime.stop(), 3)
            reset_preparation()


def outage(sim):
    sim.faults.update({"http_status": 503, "comheads": ["login"], "http_fault_count": 2})


def assert_no_candidate_owner(clients):
    for client in clients[1:]:
        assert not client.connected
        assert client._reconnect_task is None
        assert client._connect_task is None
        assert client._session is None
        assert client._telnet is None


def assert_one_owner(runtime, original):
    assert [task for task in asyncio.all_tasks() if task.get_name() == "matrix_reconnect"] == [original._reconnect_task]
    assert len([task for task in asyncio.all_tasks() if task.get_name() == "hub_runtime_refresh"]) == 1
    assert runtime.service.client is original


async def assert_recovered(runtime, sim, original):
    await ready(
        lambda: runtime.snapshot().connected
        and original.telnet_connected
        and runtime.snapshot().routing.get(1) == sim.state.outputs[0].source
    )
    assert original.connected and original.telnet_connected
    assert sum(entry.get("fault") == "http_503" for entry in sim.log) == 2
    logins = [entry for entry in sim.log if entry["channel"] == "http" and entry["command"] == "login"]
    assert len(logins) == 4
    assert logins[-1]["login_ok"]
    assert logins[-1]["payload"]["user"] == "original-user"


@pytest.mark.parametrize("new_address", [False, True])
async def test_two_login_failures_restore_original_and_automatically_read_actual_state(runtime_sim, new_address):
    runtime, sim, clients, saved = await runtime_sim()
    original, address, names = clients[0], runtime.address, runtime.service.names
    before = saved.read_bytes()
    assert runtime.snapshot().connected
    sim.state.outputs[0].source = 6
    outage(sim)
    candidate_address = (
        MatrixAddress("localhost", sim.https_port, sim.telnet_port, "candidate-user", "candidate-secret")
        if new_address
        else MatrixAddress(address.host, address.port)
    )
    result = await runtime.reconfigure(candidate_address, persist=True)
    assert not result.success and not result.connected
    assert not sim.faults.any_http
    assert runtime.address == address and runtime.service.names is names
    assert saved.read_bytes() == before
    assert original.credentials() == ("original-user", "original-secret")
    assert_no_candidate_owner(clients)
    assert_one_owner(runtime, original)
    reconnect = original._reconnect_task
    await assert_recovered(runtime, sim, original)
    await asyncio.wait_for(reconnect, 3)
    assert original._reconnect_task is reconnect
    assert runtime.snapshot().input_names[1] == "Saved console"
    assert runtime.snapshot().output_names[1] == "Saved screen"
    assert saved.read_bytes() == before
    assert sum(client.connected for client in clients) == 1


async def test_disabled_auto_reconnect_keeps_rollback_offline(runtime_sim):
    runtime, sim, clients, _ = await runtime_sim(auto_reconnect=False)
    outage(sim)
    result = await runtime.reconfigure(runtime.address)
    assert not result.success and not result.connected and not sim.faults.any_http
    assert clients[0].auto_reconnect is False
    assert clients[0]._reconnect_task is None
    count = sim.login_count
    await runtime.refresh()
    assert not runtime.snapshot().connected and sim.login_count == count == 3
    assert_no_candidate_owner(clients)


async def test_cancelled_candidate_propagates_and_rollback_automatically_recovers(runtime_sim):
    runtime, sim, clients, saved = await runtime_sim()
    original, address = clients[0], runtime.address
    before = saved.read_bytes()
    sim.hold_login = 2
    outage(sim)
    setup = asyncio.create_task(runtime.reconfigure(address, persist=True))
    await asyncio.wait_for(sim.received.wait(), 3)
    setup.cancel()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(setup, 3)
    sim.release.set()
    assert runtime.address == address and saved.read_bytes() == before
    assert_no_candidate_owner(clients)
    assert_one_owner(runtime, original)
    await assert_recovered(runtime, sim, original)


@pytest.mark.parametrize("during_rollback", [False, True])
async def test_stop_during_rollback_or_backoff_closes_all_transport_owners(runtime_sim, during_rollback):
    runtime, sim, clients, saved = await runtime_sim()
    before, address = saved.read_bytes(), runtime.address
    outage(sim)
    if during_rollback:
        sim.hold_login = 3
    setup = asyncio.create_task(runtime.reconfigure(address, persist=True))
    if during_rollback:
        await asyncio.wait_for(sim.received.wait(), 3)
    else:
        assert not (await asyncio.wait_for(setup, 3)).success
        assert_one_owner(runtime, clients[0])
    await asyncio.wait_for(runtime.stop(), 3)
    sim.release.set()
    await asyncio.gather(setup, return_exceptions=True)
    assert saved.read_bytes() == before
    assert runtime.address == address
    assert_no_candidate_owner(clients)
    for client in clients:
        assert not client.connected
        assert client._session is None and client._telnet is None
        assert client._reconnect_task is None and client._connect_task is None
    assert not [task for task in asyncio.all_tasks() if task.get_name() in {"matrix_reconnect", "hub_runtime_refresh"}]
    with pytest.raises(RuntimeError, match="stopping"):
        await runtime.connect()


async def test_following_reconfigure_drains_restored_supervisor_before_replacement(runtime_sim):
    runtime, sim, clients, _ = await runtime_sim()
    outage(sim)
    assert not (await runtime.reconfigure(runtime.address)).success
    reconnect = clients[0]._reconnect_task
    assert_one_owner(runtime, clients[0])
    assert (await runtime.reconfigure(runtime.address)).success
    assert reconnect.done()
    assert not clients[0].connected and clients[0]._reconnect_task is None
    assert runtime.service.client is clients[-1] and clients[-1].connected
    assert sum(client.connected for client in clients) == 1
    assert not [task for task in asyncio.all_tasks() if task.get_name() == "matrix_reconnect"]


async def test_initial_offline_uses_same_transport_supervisor(runtime_sim):
    runtime, sim, clients, _ = await runtime_sim(initial_faults=1)
    assert not runtime.snapshot().connected
    assert_one_owner(runtime, clients[0])
    await ready(lambda: runtime.snapshot().connected and runtime.snapshot().routing.get(1) is not None)
    assert clients[0].connected and sim.login_count == 2


async def test_structural_client_without_reconnect_seam_preserves_failed_rollback(tmp_path, monkeypatch):
    from tests import test_runtime_composition_r1 as shared

    # The existing double deliberately implements only the structural service
    # protocol; the real-network cases above prove actual reconnect behavior.
    monkeypatch.setattr("rest_api.utils._runtime", None)
    env = {
        "DATA_DIR": str(tmp_path),
        "UC_CONFIG_HOME": str(tmp_path),
        "MATRIX_HOST": "refused",
        "UC_ENABLED": "false",
        "FLIC_ENABLED": "false",
    }
    factory = shared.MatrixFactory()
    runtime = composition.build_runtime(cli.load_settings(env), environ=env, matrix_factory=factory)
    try:
        assert not hasattr(factory.instances[0], "start_auto_reconnect")
        result = await runtime.reconfigure(runtime.address)
        assert not result.success and not result.connected
        assert runtime.service.client is factory.instances[0]
    finally:
        await runtime.stop()
