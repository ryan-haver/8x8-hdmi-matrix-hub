"""Shared runtime execution against a disposable in-process matrix simulator."""

import asyncio
from copy import deepcopy
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

import run
from hub.runtime.composition import build_runtime
from orei_matrix import OreiMatrix
from password import reset_pin_lockout
from rest_api.app import create_rest_app
from tests.sim.conftest import make_simulator


@pytest.fixture
async def action_runtime(tmp_path, monkeypatch, aiohttp_client):
    import persistence
    import rest_api.utils as utils

    monkeypatch.setattr(utils, "_runtime", None)
    monkeypatch.setattr(persistence, "get_legacy_data_paths", lambda: [])
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    reset_pin_lockout()
    sim = make_simulator()
    await sim.start()
    env = {
        "DATA_DIR": str(tmp_path / "data"), "UC_CONFIG_HOME": str(tmp_path / "config"),
        "MATRIX_HOST": "127.0.0.1", "MATRIX_PORT": str(sim.https_port),
        "FLIC_ENABLED": "false", "UC_ENABLED": "false", "HA_DISCOVERY_ENABLED": "false",
    }
    for key in ("MATRIX_DATA_DIR", "UC_CONFIG_HOME"):
        monkeypatch.setenv(key, env["DATA_DIR" if key == "MATRIX_DATA_DIR" else key])

    def factory(host, **kwargs):
        matrix = OreiMatrix(host, port=sim.https_port, use_https=sim.tls)
        monkeypatch.setattr(matrix, "_connect_telnet", AsyncMock(return_value=False))
        return matrix

    runtime = build_runtime(run.load_settings(env), environ=env, matrix_factory=factory)
    assert Path(__import__("hub.runtime.actions", fromlist=[""]).__file__).resolve().is_relative_to(
        Path(__file__).resolve().parents[1])
    client = await aiohttp_client(create_rest_app(runtime=runtime))
    try:
        assert await runtime.connect()
        await runtime.refresh()
        yield runtime, client, sim
    finally:
        await client.close()
        await runtime.stop()
        await sim.stop()
        reset_pin_lockout()


def commands(sim):
    return [(row["command"], deepcopy(row.get("payload"))) for row in sim.log
            if row.get("channel") == "http" and (row.get("mutated") or row.get("command") == "cec command")]


async def profile(client, *, protected=False, macro=None):
    body = {"id": "movie", "name": "Movie", "outputs": {
        "1": {"input": 4, "hdr_mode": 2}, "2": {"input": 5, "audio_mute": True}}}
    if protected:
        body.update(password_protected=True, passcode="1234")
    if macro:
        body["power_on_macro"] = macro
    response = await client.post("/api/profile", json=body)
    assert response.status == 200, await response.text()


async def test_rest_and_local_profile_have_identical_ordered_effects(action_runtime):
    runtime, client, sim = action_runtime
    await profile(client)
    sim.log.clear()
    response = await client.post("/api/profile/movie/recall")
    assert response.status == 200
    rest = commands(sim)
    assert [item[0] for item in rest] == [
        "video switch", "tx stream", "set output audio mute", "set hdr conversion",
        "video switch", "tx stream", "set output audio mute"]
    sim.log.clear()
    result = await runtime.local.run_action("profile", "movie")
    assert result["success"]
    assert commands(sim) == rest
    assert [o.source for o in sim.state.outputs[:2]] == [4, 5]


async def test_macro_failure_keeps_profile_effects_and_runs_once(action_runtime, monkeypatch):
    runtime, client, sim = action_runtime
    await profile(client, macro="wake")
    manager = runtime.managers.macros
    monkeypatch.setattr(manager, "get_macro", lambda _: object())
    execute = AsyncMock(side_effect=TimeoutError("macro timed out"))
    monkeypatch.setattr(manager, "execute_macro", execute)
    response = await client.post("/api/profile/movie/recall")
    assert response.status == 207
    payload = await response.json()
    assert payload["data"]["power_on_macro"] == {"success": False, "error": "macro timed out"}
    assert [o.source for o in sim.state.outputs[:2]] == [4, 5]
    assert execute.await_count == 1
    execute.reset_mock()
    result = await runtime.local.run_action("profile", "movie")
    assert not result["success"] and result["data"]["status_code"] == 207
    assert execute.await_count == 1


async def test_preset_uses_runner_once_without_recursive_provider_calls(action_runtime, monkeypatch):
    runtime, client, sim = action_runtime
    original = runtime.action_runner.run
    observed = AsyncMock(wraps=original)
    monkeypatch.setattr(runtime.action_runner, "run", observed)
    sim.log.clear()
    response = await client.post("/api/preset/3")
    assert response.status == 200, await response.text()
    rest = commands(sim)
    assert len(rest) == 1 and rest[0][0] == "preset set"
    sim.log.clear()
    assert await asyncio.wait_for(runtime.local.recall_preset(3), 2)
    assert commands(sim) == rest
    assert observed.await_count == 2


async def test_runtime_preset_has_one_service_event_and_no_manual_success_broadcast(action_runtime, monkeypatch):
    runtime, client, _ = action_runtime
    manual = AsyncMock()
    monkeypatch.setattr("rest_api.control.broadcast_status_update", manual)
    events = []
    unsubscribe = runtime.bus.subscribe(events.append)
    try:
        response = await client.post("/api/preset/3")
        assert response.status == 200
        await runtime.bus.drain(timeout=1)
        recalls = [event for event in events if event.topic == "presets" and event.data.get("action") == "recall"]
        assert len(recalls) == 1 and recalls[0].data["preset"] == 3
        manual.assert_not_awaited()
    finally:
        unsubscribe()


async def test_shared_pin_attempts_and_lockout_across_rest_and_local(action_runtime):
    from password import MAX_PIN_FAILURES

    runtime, client, sim = action_runtime
    await profile(client, protected=True)
    sim.log.clear()
    for index in range(MAX_PIN_FAILURES):
        if index % 2:
            result = await runtime.local.run_action("profile", "movie", passcode="9999")
            status = result["data"]["status_code"]
        else:
            response = await client.post("/api/profile/movie/recall", json={"passcode": "9999"})
            status = response.status
        assert status == 403
        from password import get_pin_tracker
        assert get_pin_tracker().failures("profile:movie") == index + 1
    # Missing PIN and correct PIN both remain locked on either surface.
    response = await client.post("/api/profile/movie/recall")
    assert response.status == 429 and int(response.headers["Retry-After"]) > 0
    assert (await response.json())["data"]["error"] == "passcode_locked"
    result = await runtime.local.run_action("profile", "movie", passcode="1234")
    assert result["data"]["status_code"] == 429
    assert commands(sim) == []


async def test_scene_checks_pin_once_off_loop_and_preserves_history(action_runtime, monkeypatch):
    import threading

    import password

    runtime, client, sim = action_runtime
    await profile(client, protected=True)
    response = await client.post("/api/v2/scenes", json={
        "name": "Evening", "password_protected": True, "passcode": "5678",
        "steps": [{"type": "profile", "id": "movie"}]})
    assert response.status == 201, await response.text()
    scene_id = (await response.json())["data"]["scene"]["id"]
    real = password.verify_passcode
    entered = threading.Event()
    release = threading.Event()
    calls = []

    def verify(pin, hashed):
        calls.append(threading.get_ident())
        entered.set()
        assert release.wait(3)
        return real(pin, hashed)

    monkeypatch.setattr(password, "verify_passcode", verify)
    request = asyncio.create_task(runtime.local.run_action("scene", scene_id, passcode="5678"))
    try:
        async with asyncio.timeout(2):
            while not entered.is_set():
                await asyncio.sleep(0.001)
        # The event loop can serve health while PBKDF2 is blocked in its worker thread.
        response = await asyncio.wait_for(client.get("/api/health"), 1)
        assert response.status == 200
    finally:
        release.set()
    assert (await request)["success"]
    assert len(calls) == 1 and calls[0] != threading.get_ident()
    scene = runtime.managers.scenes.get_scene(scene_id)
    assert len(scene.execution_history) == 1
    assert len(runtime.managers.profiles.get_profile("movie").execution_log) == 1


@pytest.mark.parametrize("kind", ["profile", "scene", "macro", "shortcut", "preset"])
async def test_actual_uc_dispatcher_matches_rest_order_without_duplicate_macros(action_runtime, kind):
    from hub.integrations.unfolded_circle.handlers import UCCommandDispatcher

    runtime, client, sim = action_runtime
    macro = runtime.managers.macros.create_macro("Wake", [
        {"command": "POWER_ON", "targets": ["output_1"], "delay_ms": 0},
        {"command": "POWER_ON", "targets": ["input_2"], "delay_ms": 0},
    ], macro_id="wake")
    await profile(client, macro=macro.id)
    scene_response = await client.post("/api/v2/scenes", json={"name": "Evening", "steps": [
        {"type": "profile", "id": "movie"}, {"type": "macro", "id": "wake"}]})
    assert scene_response.status == 201, await scene_response.text()
    scene_id = (await scene_response.json())["data"]["scene"]["id"]
    path, command = {
        "profile": ("/api/profile/movie/recall", "PROFILE_movie"),
        "scene": (f"/api/v2/scenes/{scene_id}/execute", f"SCENE_{scene_id}"),
        "macro": ("/api/cec/macro/wake/execute", "MACRO_wake"),
        "shortcut": ("/api/shortcuts/mute_all_audio/execute", "SHORTCUT_mute_all_audio"),
        "preset": ("/api/preset/3", "PRESET_3"),
    }[kind]
    sim.log.clear()
    response = await client.post(path)
    assert response.status == 200, await response.text()
    expected = commands(sim)
    assert expected
    if kind in {"profile", "scene", "macro"}:
        assert sum(name == "cec command" for name, _ in expected) == 2
    sim.log.clear()
    dispatcher = UCCommandDispatcher(runtime.local)
    dispatcher.projector.project_snapshot(runtime.snapshot())
    assert await dispatcher.dispatch("remote.orei_matrix", "send_cmd", {"command": command}) == 200
    assert commands(sim) == expected


@pytest.mark.parametrize("path,body,entity,cmd,params", [
    ("/api/switch", {"input": 7}, "remote.orei_matrix", "send_cmd", {"command": "ROUTE_ALL_IN_7"}),
    ("/api/output/2/source", {"input": 7}, "select.output_2_source", "select_option", {"option": "Input 7"}),
    ("/api/power/on", None, "switch.matrix_power", "on", None),
    ("/api/cec/input/2/power_on", None, "remote.input_2_cec", "send_cmd", {"command": "POWER_ON"}),
    ("/api/cec/output/2/power_off", None, "remote.output_2_cec", "send_cmd", {"command": "POWER_OFF"}),
])
async def test_direct_rest_and_uc_commands_use_same_provider(action_runtime, path, body, entity, cmd, params):
    from hub.integrations.unfolded_circle.handlers import UCCommandDispatcher

    runtime, client, sim = action_runtime
    sim.log.clear()
    response = await client.post(path, json=body)
    assert response.status == 200, await response.text()
    expected = commands(sim)
    sim.log.clear()
    dispatcher = UCCommandDispatcher(runtime.local)
    dispatcher.projector.project_snapshot(runtime.snapshot())
    assert await dispatcher.dispatch(entity, cmd, params) == 200
    assert commands(sim) == expected


async def test_rest_and_local_cycles_share_serialization_and_response_readback(action_runtime):
    runtime, client, sim = action_runtime
    assert await runtime.local.switch(1, 1)
    responses = await asyncio.gather(*[client.post("/api/input/next?output=1") for _ in range(3)])
    payloads = [await response.json() for response in responses]
    assert all(response.status == 200 for response in responses)
    assert sorted((p["data"]["previous_input"], p["data"]["current_input"]) for p in payloads) == [
        (1, 2), (2, 3), (3, 4)]
    response, local = await asyncio.gather(
        client.post("/api/input/previous?output=1"), runtime.local.cycle_input("previous", 1))
    assert response.status == 200 and local
    assert runtime.snapshot().routing[1] == sim.state.outputs[0].source == 2


async def test_catalog_write_reaches_existing_local_subscriber(action_runtime):
    runtime, client, _ = action_runtime
    events = []
    unsubscribe = runtime.local.subscribe(events.append)
    try:
        async with asyncio.timeout(1):
            while not any(event.kind == "catalog" for event in events):
                await asyncio.sleep(0)
        events.clear()
        await profile(client)
        await runtime.bus.drain(timeout=1)
        async with asyncio.timeout(1):
            while not any(event.kind == "catalog" and any(p["id"] == "movie" for p in event.data["profiles"])
                          for event in events):
                await asyncio.sleep(0)
        assert "passcode_hash" not in repr([event.data for event in events if event.kind == "catalog"])
    finally:
        unsubscribe()


@pytest.mark.parametrize("direction,start,expected", [("next", 8, 8), ("previous", 1, 1)])
async def test_cycle_clamp_preserves_exact_rest_readback(action_runtime, direction, start, expected):
    runtime, client, sim = action_runtime
    assert await runtime.local.switch(start, 1)
    response = await client.post(f"/api/input/{direction}?output=1&cycle=false")
    assert response.status == 200
    data = (await response.json())["data"]
    assert (data["previous_input"], data["current_input"]) == (start, expected)
    assert runtime.snapshot().routing[1] == sim.state.outputs[0].source == expected


async def test_http_and_local_clients_share_atomic_wrap_and_clamp(action_runtime):
    from hub.integrations.hub_client_http import HubClientHttp

    runtime, client, sim = action_runtime
    remote = HubClientHttp(str(client.make_url("/")))
    try:
        assert await runtime.local.switch(4, 1)
        operations = [client.post("/api/input/next?output=1&cycle=false") for _ in range(3)]
        responses = await asyncio.gather(*operations, remote.cycle_input("next", 1, cycle=False),
                                         runtime.local.cycle_input("next", 1, cycle=False))
        assert responses[-2:] == [True, True]
        pairs = []
        for response in responses[:3]:
            assert response.status == 200
            data = (await response.json())["data"]
            pairs.append((data["previous_input"], data["current_input"]))
        assert all(pair in {(4, 5), (5, 6), (6, 7), (7, 8), (8, 8)} for pair in pairs)
        assert len(pairs) == len(set(pairs))
        assert runtime.snapshot().routing[1] == sim.state.outputs[0].source == 8
        assert await remote.cycle_input("next", 1)
        assert sim.state.outputs[0].source == 1
        assert await runtime.local.cycle_input("previous", 1, cycle=False)
        assert sim.state.outputs[0].source == 1
        assert await runtime.local.cycle_input("previous", 1)
        assert sim.state.outputs[0].source == 8
    finally:
        await remote.close()


async def test_refused_cycle_does_not_leak_previous_observation(action_runtime, monkeypatch):
    from hub.runtime.actions import _cycle_observation
    from rest_api.control import _cycle_input

    runtime, _, sim = action_runtime
    assert await runtime.local.switch(3, 1)
    real = runtime.service.client.switch_input
    monkeypatch.setattr(runtime.service.client, "switch_input", AsyncMock(return_value=False))
    _cycle_observation.set((7, 8))
    assert await _cycle_input("next", 1, cycle=False) == (3, 4, False)
    assert _cycle_observation.get() is None
    monkeypatch.setattr(runtime.service.client, "switch_input", real)
    assert await _cycle_input("previous", 1, cycle=False) == (3, 2, True)
    assert _cycle_observation.get() is None
    assert sim.state.outputs[0].source == 2
