"""Actual R1 transaction + R3 SDK sockets, transport doubles and an explicit R2 barrier shim.

The imported builder substitutes only the not-yet-integrated R2 barrier; these
tests are not normal-entry, migration, image or hardware acceptance evidence.
"""

from __future__ import annotations

import asyncio
import json
import socket
from unittest.mock import AsyncMock, Mock

import pytest
import ucapi

import _file_io
from hub.integrations.unfolded_circle import UnfoldedCircleIntegration, config_from_env
from hub.runtime.config import MatrixAddress
from tests import test_runtime_composition_r1 as shared
from tools.uc_remote_sim import UcRemoteSim

runtime_builder = shared.runtime_builder


def seed_state():
    return {
        "host": "simulator",
        "port": 443,
        "telnet_port": 2323,
        "user": "saved-user",
        "password": "saved-secret",
        "input_names": {"1": "Saved console"},
        "output_names": {"1": "Saved theater"},
        "extension": {"preserve": [1, 2]},
    }


@pytest.fixture
async def setup_runtime(runtime_builder, tmp_path, monkeypatch):
    resources = []
    original_video = shared.MatrixDouble.get_video_status

    async def named_video(matrix):
        result = await original_video(matrix)
        result["allinputname"] = [f"{matrix.host} source {i}" for i in range(1, 9)]
        result["alloutputname"] = [f"{matrix.host} display {i}" for i in range(1, 9)]
        return result

    monkeypatch.setattr(shared.MatrixDouble, "get_video_status", named_video)

    async def make(saved=None, *, bootstrap="simulator", mdns=None, auth_token="setup-token"):
        config_dir = tmp_path / "config"
        config_dir.mkdir(exist_ok=True)
        if saved is not None:
            (config_dir / "config_state.json").write_text(json.dumps(saved, indent=3) + "\n")
        runtime, factory = runtime_builder(UC_ENABLED="true", MATRIX_HOST=bootstrap)
        await runtime.connect()
        cfg = config_from_env({
            "UC_ENABLED": "true",
            "UC_CONFIG_HOME": str(config_dir),
            "UC_INTEGRATION_HTTP_PORT": str(shared.free_port()),
            "UC_INTEGRATION_INTERFACE": "127.0.0.1",
            "UC_DISABLE_MDNS_PUBLISH": "true",
            "UC_AUTH_TOKEN": auth_token,
        })
        integration = UnfoldedCircleIntegration(cfg, probe_fn=AsyncMock(return_value=None), mdns_publisher=mdns)
        integration.bind_runtime(reconfigure=runtime.reconfigure, current_address=lambda: runtime.address)
        resources.append((integration, runtime))
        await integration.start(runtime.local)
        return runtime, factory, integration, config_dir / "config_state.json"

    yield make
    for integration, runtime in reversed(resources):
        await integration.stop()
        await runtime.stop()


def track_saves(monkeypatch):
    original = _file_io.atomic_write_json
    calls = []

    def save(path, payload, **kwargs):
        calls.append((path, payload))
        return original(path, payload, **kwargs)

    monkeypatch.setattr(_file_io, "atomic_write_json", save)
    return calls


async def login(remote, host="new-target", password="new-secret"):
    first = await remote.setup_driver({"host": host, "port": 443, "auth_token": "setup-token"})
    assert first.state == "WAIT_USER_ACTION"
    return await remote.set_driver_user_data(input_values={"user": "new-user", "password": password})


async def drain_deliveries(runtime, integration):
    """Wait through actual local-adapter and bridge queues, not a timing sleep."""
    await runtime.bus.drain(timeout=1)
    while runtime.local._tasks or integration.bridge._background_tasks:
        tasks = set(runtime.local._tasks) | set(integration.bridge._background_tasks)
        await asyncio.wait_for(asyncio.gather(*tasks), 2)
        await asyncio.sleep(0)  # Run the queues' done callbacks before inspecting them again.


async def test_runtime_setup_has_exactly_one_save_and_no_post_commit_writer(setup_runtime, monkeypatch):
    runtime, factory, integration, path = await setup_runtime(seed_state())
    calls = track_saves(monkeypatch)
    forbidden = Mock(side_effect=OSError("would-be second save failed"))
    monkeypatch.setattr("hub.integrations.unfolded_circle.bridge.save_config_state", forbidden)
    async with UcRemoteSim(f"ws://127.0.0.1:{integration.config.port}") as remote:
        result = await remote.setup_driver({"host": "simulator", "auth_token": "setup-token"})
        assert result.state == "OK"
        assert len(await remote.get_available_entities()) == 74
    await drain_deliveries(runtime, integration)
    assert len(calls) == 1
    forbidden.assert_not_called()
    saved = json.loads(path.read_text())
    assert saved["password"] == runtime.address.password == "saved-secret"
    assert saved["user"] == runtime.address.user == "saved-user"
    assert saved["telnet_port"] == runtime.address.telnet_port == 2323
    assert saved["input_names"]["1"] == "Saved console"
    assert saved["output_names"]["1"] == "Saved theater"
    assert saved["extension"] == seed_state()["extension"]
    assert factory.maximum == 1


async def test_changed_address_names_credentials_metadata_and_repeated_setup(setup_runtime, monkeypatch):
    runtime, factory, integration, path = await setup_runtime(seed_state())
    calls = track_saves(monkeypatch)
    async with UcRemoteSim(f"ws://127.0.0.1:{integration.config.port}") as remote:
        await remote.subscribe_events(["button.preset_3", "media_player.output_1"])
        assert (await login(remote)).state == "OK"
        saved = json.loads(path.read_text())
        assert (saved["host"], saved["user"], saved["password"]) == ("new-target", "new-user", "new-secret")
        assert saved["input_names"]["1"] == runtime.snapshot().input_names[1] == "new-target source 1"
        assert saved["output_names"]["1"] == runtime.snapshot().output_names[1] == "new-target display 1"
        assert saved["extension"] == seed_state()["extension"]
        assert (await remote.setup_driver({"host": "new-target", "auth_token": "setup-token"})).state == "OK"
        assert {state["entity_id"] for state in await remote.get_entity_states()} == {"button.preset_3", "media_player.output_1"}
    await drain_deliveries(runtime, integration)
    assert len(calls) == 2
    assert factory.instances[-1].password == "new-secret"
    assert factory.maximum == 1
    assert sum(client.connected for client in factory.instances) == 1


async def test_changed_address_setup_ignores_would_be_second_save_failure(setup_runtime, monkeypatch):
    runtime, factory, integration, path = await setup_runtime(seed_state())
    old_client = runtime.service.client
    await drain_deliveries(runtime, integration)
    calls = track_saves(monkeypatch)
    forbidden = Mock(side_effect=OSError("would-be second save failed"))
    monkeypatch.setattr("hub.integrations.unfolded_circle.bridge.save_config_state", forbidden)
    async with UcRemoteSim(f"ws://127.0.0.1:{integration.config.port}") as remote:
        result = await login(remote)
        assert result.state == "OK"
    await drain_deliveries(runtime, integration)
    forbidden.assert_not_called()
    assert len(calls) == 1 and factory.maximum == 1
    assert runtime.address.host == json.loads(path.read_text())["host"] == "new-target"
    assert not old_client.connected and runtime.service.connected


async def test_transaction_save_failure_restores_transport_address_and_original_bytes(setup_runtime, monkeypatch):
    runtime, factory, integration, path = await setup_runtime(seed_state())
    old_client, old_address, old_names = runtime.service.client, runtime.address, runtime.service.names
    before = path.read_bytes()
    save = Mock(side_effect=OSError("transactional save refused"))
    monkeypatch.setattr(_file_io, "atomic_write_json", save)
    async with UcRemoteSim(f"ws://127.0.0.1:{integration.config.port}") as remote:
        result = await login(remote)
        assert result.state == "ERROR"
        assert result.final["error"] == "OTHER"
    await drain_deliveries(runtime, integration)
    assert save.call_count == 1
    assert runtime.service.client is old_client and old_client.connected
    assert runtime.address == old_address
    assert runtime.service.names is old_names
    assert path.read_bytes() == before
    assert factory.maximum == 1
    assert not factory.instances[-1].connected


async def test_environment_bootstrap_adoption_does_not_persist_environment_login(setup_runtime, monkeypatch):
    monkeypatch.setenv("OREI_USER", "environment-user")
    monkeypatch.setenv("OREI_PASSWORD", "environment-secret")
    runtime, factory, integration, path = await setup_runtime()
    runtime.service.names.set_input_name(1, "Unsaved bootstrap name")
    await drain_deliveries(runtime, integration)
    assert not path.exists()
    calls = track_saves(monkeypatch)
    async with UcRemoteSim(f"ws://127.0.0.1:{integration.config.port}") as remote:
        assert (await remote.setup_driver({"host": "simulator", "auth_token": "setup-token"})).state == "OK"
    saved = json.loads(path.read_text())
    assert "user" not in saved and "password" not in saved
    assert runtime.address.user is None and runtime.address.password is None
    assert len(calls) == 1 and factory.maximum == 1


async def test_failed_login_abort_and_public_authorization_preserve_saved_state(setup_runtime, monkeypatch):
    runtime, factory, integration, path = await setup_runtime(seed_state())
    before, old_client = path.read_bytes(), runtime.service.client
    calls = track_saves(monkeypatch)
    async with UcRemoteSim(f"ws://127.0.0.1:{integration.config.port}") as remote:
        unauthorized = await remote.setup_driver({"host": "new-target", "auth_token": "wrong"})
        assert unauthorized.state == "ERROR" and unauthorized.final["error"] == "AUTHORIZATION_ERROR"
        failed = await login(remote, host="refused")
        assert failed.state == "ERROR" and failed.final["error"] == "AUTHORIZATION_ERROR"
        assert (await remote.setup_driver({"host": "new-target", "auth_token": "setup-token"})).state == "WAIT_USER_ACTION"
        await remote.abort_driver_setup()
    assert integration.setup_handler.pending_setup is None
    assert path.read_bytes() == before and not calls
    assert runtime.service.client is old_client and old_client.connected
    assert factory.maximum == 1


async def test_current_password_authorization_uses_actual_runtime_login(setup_runtime, monkeypatch):
    monkeypatch.delenv("UC_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("ADMIN_PIN", raising=False)
    runtime, factory, integration, path = await setup_runtime(seed_state(), auth_token="")
    calls = track_saves(monkeypatch)
    before = path.read_bytes()
    async with UcRemoteSim(f"ws://127.0.0.1:{integration.config.port}") as remote:
        denied = await remote.setup_driver({"host": "new-target", "current_password": "wrong"})
        assert denied.state == "ERROR" and denied.final["error"] == "AUTHORIZATION_ERROR"
        assert path.read_bytes() == before and not calls
        allowed = await remote.setup_driver({"host": "new-target", "current_password": "saved-secret"})
        assert allowed.state == "WAIT_USER_ACTION"
        assert (await remote.set_driver_user_data(input_values={"user": "new-user", "password": "new-secret"})).state == "OK"
    await drain_deliveries(runtime, integration)
    assert len(calls) == 1 and factory.maximum == 1


@pytest.mark.parametrize("mode", ["cancel", "abort", "stop"])
async def test_cancel_abort_or_stop_inflight_setup_rolls_back_before_save(setup_runtime, monkeypatch, mode):
    runtime, factory, integration, path = await setup_runtime(seed_state())
    before, old_address, old_client = path.read_bytes(), runtime.address, runtime.service.client
    calls = track_saves(monkeypatch)
    entered, gate = asyncio.Event(), asyncio.Event()
    original_factory = runtime.matrix_factory

    def blocked_factory(*args, **kwargs):
        client = original_factory(*args, **kwargs)
        client.connect_entered = entered
        client.connect_gate = gate
        return client

    runtime.matrix_factory = blocked_factory
    handler = integration.setup_handler
    assert isinstance(await handler(ucapi.DriverSetupRequest(False, {"host": "new-target", "auth_token": "setup-token"})), ucapi.RequestUserInput)
    action = asyncio.create_task(handler(ucapi.UserDataResponse({"user": "new-user", "password": "new-secret"})))
    await asyncio.wait_for(entered.wait(), 2)
    if mode == "abort":
        assert isinstance(await handler(ucapi.AbortDriverSetup("USER_CANCELLED")), ucapi.SetupError)
    elif mode == "stop":
        await integration.stop()
    else:
        action.cancel()
    with pytest.raises(asyncio.CancelledError):
        await action
    await drain_deliveries(runtime, integration)
    assert path.read_bytes() == before and not calls
    assert runtime.address == old_address and runtime.service.client is old_client
    assert old_client.connected and not factory.instances[-1].connected
    assert factory.maximum == 1


async def test_effective_address_is_read_after_runtime_credential_merge(setup_runtime):
    runtime, _, integration, _ = await setup_runtime(seed_state())
    ok, error, address = await integration.setup_handler._invoke_reconfigure(MatrixAddress("simulator"))
    assert ok and error is None
    assert address is runtime.address
    assert (address.user, address.password, address.telnet_port) == ("saved-user", "saved-secret", 2323)


async def test_typeerror_inside_hook_never_retries_action(setup_runtime):
    _, _, integration, _ = await setup_runtime()
    calls = []

    def broken(address, *, persist=False):
        calls.append(address)
        raise TypeError("partially executed hook")

    integration.bridge.bind_runtime(reconfigure=broken)
    with pytest.raises(TypeError, match="partially executed"):
        await integration.setup_handler._invoke_reconfigure(MatrixAddress("simulator"))
    assert len(calls) == 1


async def test_cancelled_start_closes_real_socket_and_unsubscribes(setup_runtime):
    _, _, integration, _ = await setup_runtime(seed_state())
    await integration.stop()
    entered = asyncio.Event()

    async def blocked_mdns():
        entered.set()
        await asyncio.Event().wait()

    integration.mdns.start = blocked_mdns
    starting = asyncio.create_task(integration.start(integration.hub_client))
    await asyncio.wait_for(entered.wait(), 3)
    server_task = integration.api._server_task
    starting.cancel()
    with pytest.raises(asyncio.CancelledError):
        await starting
    assert server_task.done() and not integration.running
    assert integration.bridge._unsubscribe is None
    with socket.socket() as sock:
        assert sock.connect_ex(("127.0.0.1", integration.config.port)) != 0


async def test_cancelled_sdk_init_closes_partially_started_listener(setup_runtime, monkeypatch):
    _, _, integration, _ = await setup_runtime(seed_state())
    await integration.stop()
    entered = asyncio.Event()
    original_init = ucapi.IntegrationAPI.init

    async def partial_init(api, *args, **kwargs):
        await original_init(api, *args, **kwargs)
        entered.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(ucapi.IntegrationAPI, "init", partial_init)
    starting = asyncio.create_task(integration.start(integration.hub_client))
    await asyncio.wait_for(entered.wait(), 3)
    await asyncio.wait_for(integration.bridge._ws_ready_event.wait(), 3)
    sdk_task = integration.api._server_task
    starting.cancel()
    with pytest.raises(asyncio.CancelledError):
        await starting
    assert sdk_task.done() and not integration.running
    assert not integration.bridge._background_tasks
    with socket.socket() as sock:
        assert sock.connect_ex(("127.0.0.1", integration.config.port)) != 0


async def test_stop_closes_listener_and_mdns_before_resistant_background_task(setup_runtime, monkeypatch):
    _, _, integration, _ = await setup_runtime(seed_state())
    monkeypatch.setattr("hub.integrations.unfolded_circle.bridge.CLEANUP_TIMEOUT", 0.03)
    entered, cancelled, release = asyncio.Event(), asyncio.Event(), asyncio.Event()

    async def resistant():
        entered.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.set()
            await release.wait()

    task = integration.bridge._schedule_task(resistant())
    await entered.wait()
    mdns_stop = AsyncMock()
    integration.mdns.stop = mdns_stop
    try:
        await asyncio.wait_for(integration.stop(), 1)
        await cancelled.wait()
        mdns_stop.assert_awaited_once()
        assert not task.done()
        with socket.socket() as sock:
            assert sock.connect_ex(("127.0.0.1", integration.config.port)) != 0
    finally:
        release.set()
        await task


async def test_standalone_rename_writer_retains_metadata_and_remains_repeatable(setup_runtime):
    _, _, integration, path = await setup_runtime(seed_state())
    integration.bridge._reconfigure_hook = None
    for name in ("Renamed once", "Renamed twice"):
        integration.projector.input_names[1] = name
        integration.bridge._persist_renamed_ports()
        assert json.loads(path.read_text())["input_names"]["1"] == name
        assert integration.migrated_config["input_names"][1] == name
    assert json.loads(path.read_text())["extension"] == seed_state()["extension"]


async def test_live_runtime_names_persist_once_without_bridge_writer_or_transport_swap(setup_runtime, monkeypatch):
    runtime, factory, integration, path = await setup_runtime(seed_state())
    await drain_deliveries(runtime, integration)
    calls = track_saves(monkeypatch)
    forbidden = Mock(side_effect=AssertionError("runtime must own persistence"))
    monkeypatch.setattr("hub.integrations.unfolded_circle.bridge.save_config_state", forbidden)
    original_client = runtime.service.client
    runtime.service.names.set_input_name(2, "Live console")
    runtime.service.names.set_output_name(2, "Live theater")
    await drain_deliveries(runtime, integration)
    assert len(calls) == 1
    forbidden.assert_not_called()
    saved = json.loads(path.read_text())
    assert saved["input_names"]["2"] == "Live console"
    assert saved["output_names"]["2"] == "Live theater"
    assert saved["password"] == "saved-secret" and saved["extension"] == seed_state()["extension"]
    assert runtime.service.client is original_client and len(factory.instances) == 1
