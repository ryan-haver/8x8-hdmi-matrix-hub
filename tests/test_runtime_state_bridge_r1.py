"""Shared state/readback with real REST/WS and a single transport double."""

import asyncio

import aiohttp

from hub.core.event_bus import EventBus
from tests import test_runtime_composition_r1 as shared
from tests.test_runtime_composition_r1 import MatrixDouble

runtime_builder = shared.runtime_builder


async def test_snapshot_is_redacted_copied_and_omits_unknowns(runtime_builder, monkeypatch):
    runtime, _ = runtime_builder()
    monkeypatch.setattr(
        runtime.managers.profiles,
        "list_profiles",
        lambda: [
            {"id": "p1", "password_protected": True, "passcode_hash": "private", "nested": {"password": "private"}}
        ],
    )
    await runtime.connect()
    state = runtime.snapshot()
    assert 2 not in state.input_signals and 2 not in state.input_cables
    assert state.input_signals[1] is True
    assert state.profiles == [{"id": "p1", "password_protected": True, "nested": {}}]
    state.routing[1] = 8
    state.profiles[0]["id"] = "changed"
    assert runtime.snapshot().routing[1] == 1
    assert runtime.snapshot().profiles[0]["id"] == "p1"
    await runtime.stop()


async def test_typed_events_use_integration_payloads_and_independent_nested_copies(runtime_builder):
    runtime, _ = runtime_builder()
    received = []
    runtime.subscribe(lambda event: event.data.get("routing", {}).update({1: 99}))
    remove = runtime.subscribe(received.append)
    await runtime.connect()
    await runtime.commands.power(False)
    await runtime.commands.switch(3, 1)
    by_kind = {event.kind: event.data for event in received}
    assert by_kind["power"] == {"on": False}
    assert by_kind["signal"]["input_signals"][1] is True
    assert by_kind["names"]["input_names"][1] == "Source 1"
    assert by_kind["routing"]["routing"][1] == 3
    remove()
    await runtime.stop()


async def test_bus_deliveries_do_not_share_nested_state():
    bus = EventBus()
    received = []
    bus.subscribe(lambda event: event.data["nested"].update(value="mutated"))
    bus.subscribe(lambda event: received.append(event.data))
    original = {"nested": {"value": "kept"}}
    bus.publish("test", original)
    assert received == [original]
    assert original["nested"]["value"] == "kept"


async def test_rest_ws_and_local_commands_share_readback(runtime_builder):
    runtime, factory = runtime_builder()
    await runtime.start()
    await runtime._connect_task
    url = f"http://127.0.0.1:{runtime.settings.api_port}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(url + "/ws") as ws:
                assert (await ws.receive_json())["event"] == "connected"
                assert (await ws.receive_json())["event"] == "status"
                factory.instances[0].routes[0] = 4  # front panel / another controller
                await runtime.refresh()
                changed = await ws.receive_json(timeout=2)
                assert changed["event"] == "routing_change"
                assert changed["data"]["input"] == 4
                assert (await runtime.local.snapshot()).routing[1] == 4
                await runtime.local.switch(6, 1)
                changed = await ws.receive_json(timeout=2)
                assert changed["event"] == "routing_change" and changed["data"]["input"] == 6
                async with session.get(url + "/api/status") as response:
                    assert (await response.json())["data"]["routing"]["1"] == 6
                async with session.get(url + "/api/status/full") as response:
                    data = (await response.json())["data"]
                    assert data["output_hdcp"] == [2] * 8
                    assert data["input_edid"] == [1] * 8
                    assert data["firmware_version"] == "test"
        assert len(factory.instances) == 1
        assert sum(c == ("switch", 6, 1) for c in factory.instances[0].calls) == 1
    finally:
        await runtime.stop()


async def test_shared_cycle_lock_serializes_rest_and_uc(runtime_builder):
    runtime, factory = runtime_builder()
    await runtime.start()
    await runtime._connect_task
    from rest_api import control

    assert control._cycle_locks[1] is runtime.commands.cycle_locks[1]
    await asyncio.gather(*(runtime.commands.cycle_input("next", 1) for _ in range(3)))
    assert runtime.snapshot().routing[1] == 4
    assert factory.instances[0].routes[0] == 4
    await runtime.stop()


async def test_old_read_cannot_overwrite_replacement(runtime_builder):
    runtime, factory = runtime_builder()
    old = factory.instances[0]
    await runtime.connect()
    old.read_entered.clear()
    old.read_gate = asyncio.Event()
    old.routes = [8] * 8
    read = asyncio.create_task(runtime.service.refresh_snapshot())
    await old.read_entered.wait()
    new = MatrixDouble("new")
    runtime.service.replace_client(new)
    old.read_gate.set()
    assert await read is False
    assert runtime.service.routing[1] is None
    assert runtime.service.raw_snapshot() == {}
    await runtime.stop()


async def test_catalog_and_preset_settings_notification(runtime_builder, monkeypatch):
    runtime, _ = runtime_builder()
    await runtime.start()
    await runtime._connect_task
    seen = []
    runtime.subscribe(seen.append)
    monkeypatch.setattr(runtime.managers.profiles, "list_profiles", lambda: [{"id": "new", "passcode_hash": "secret"}])
    runtime.notify_catalog_changed()
    catalog = next(event.data for event in seen if event.kind == "catalog")
    assert catalog["profiles"] == [{"id": "new"}]
    from rest_api.device_settings import set_preset_name

    assert set_preset_name(1, "Custom")
    assert runtime.snapshot().preset_names[1] == "Custom"
    await runtime.stop()


async def test_saved_names_restore_and_survive_failed_reconfigure(runtime_builder):
    import json

    runtime, _ = runtime_builder()
    (runtime.prepared.paths.config_dir / "config_state.json").write_text(
        json.dumps({"host": "simulator", "input_names": {"1": "Saved source"}, "output_names": {"1": "Saved display"}})
    )
    runtime._restore_names()
    await runtime.connect()
    assert runtime.snapshot().input_names[1] == "Saved source"
    result = await runtime.reconfigure(shared.MatrixAddress("refused", password="candidate-secret"))
    assert not result.success
    assert runtime.snapshot().input_names[1] == "Saved source"
    assert runtime.snapshot().output_names[1] == "Saved display"
    await runtime.stop()


def test_modified_modules_resolve_to_this_checkout():
    from pathlib import Path

    import hub.core.matrix_service
    import hub.runtime.composition
    import rest_api.app

    root = Path(__file__).resolve().parents[1]
    for module in (hub.runtime.composition, hub.core.matrix_service, rest_api.app):
        assert Path(module.__file__).resolve().is_relative_to(root / "src")
