"""Exact REST envelopes on the runtime shared with integration clients."""

import asyncio
from copy import deepcopy
from unittest.mock import AsyncMock

import pytest

from hub.integrations.hub_client import HubEvent, HubSnapshot
from hub.integrations.hub_client_local import HubClientLocal
from tests import test_runtime_action_parity_r4 as shared
from tests.test_runtime_action_parity_r4 import profile

action_runtime = shared.action_runtime


@pytest.mark.parametrize("refused,status", [(set(), 200), ({2}, 207), ({1, 2}, 500)])
async def test_profile_exact_success_partial_and_failure(action_runtime, monkeypatch, refused, status):
    runtime, client, sim = action_runtime
    await profile(client)
    real = runtime.service.client.set_output_audio_mute

    async def mute(output, value):
        return False if output in refused else await real(output, value)

    monkeypatch.setattr(runtime.service.client, "set_output_audio_mute", mute)
    response = await client.post("/api/profile/movie/recall")
    errors = [f"output {out}: {'mute' if out == 2 else 'unmute'} not applied" for out in sorted(refused)]
    payload = {"success": not refused, "data": {
        "profile": "Movie", "applied": [f"Output {out} → Input {out + 3}" for out in (1, 2) if out not in refused],
        "failed_outputs": sorted(refused), "errors": errors or None, "power_on_macro": None},
        "error": "; ".join(errors) or None}
    assert response.status == status
    assert response.headers["Content-Type"] == "application/json; charset=utf-8"
    assert await response.json() == payload
    alias = await client.post("/api/scene/movie/recall")
    payload["data"]["scene"] = payload["data"].pop("profile")
    assert alias.status == status and await alias.json() == payload
    assert alias.headers["Content-Type"] == "application/json"
    assert [o.source for o in sim.state.outputs[:2]] == [4, 5]


@pytest.mark.parametrize("pin,error", [(None, "passcode_required"), ("9999", "invalid_passcode")])
async def test_pin_wire_and_legacy_alias(action_runtime, pin, error):
    _, client, _ = action_runtime
    await profile(client, protected=True)
    for path in ("profile", "scene"):
        response = await client.post(f"/api/{path}/movie/recall", json={} if pin is None else {"passcode": pin})
        assert response.status == 403
        assert "Retry-After" not in response.headers
        assert await response.json() == {
            "success": False, "data": {"error": error, "profile_id": "movie"}, "error": None}


async def test_missing_invalid_and_disconnected_wire(action_runtime):
    runtime, client, _ = action_runtime
    for path, status, error in [
        ("/api/profile/missing/recall", 404, "Profile 'missing' not found"),
        ("/api/v2/scenes/missing/execute", 404, "Scene not found"),
        ("/api/cec/macro/missing/execute", 404, "Macro 'missing' not found"),
        ("/api/shortcuts/missing/execute", 404, "Shortcut 'missing' not found"),
        ("/api/preset/9", 400, "Preset must be 1-8"),
    ]:
        response = await client.post(path)
        assert response.status == status
        expected = {"success": False, "error": error}
        if not path.startswith("/api/v2/"):
            expected["data"] = None
        assert await response.json() == expected
    await runtime.service.disconnect()
    response = await client.post("/api/preset/1")
    assert response.status == 503
    assert await response.json() == {"success": False, "data": None, "error": "Matrix not connected"}


async def test_macro_timeout_keeps_historical_failure_envelope_and_single_call(action_runtime, monkeypatch):
    runtime, client, _ = action_runtime
    manager = runtime.managers.macros
    monkeypatch.setattr(manager, "get_macro", lambda _: object())
    outcome = {"success": False, "error": "Execution timed out", "results": [{"success": True}]}
    execute = AsyncMock(return_value=outcome)
    monkeypatch.setattr(manager, "execute_macro", execute)
    response = await client.post("/api/cec/macro/wake/execute", json={"timeout_s": 0.1})
    assert response.status == 500
    assert await response.json() == {"success": False, "data": None, "error": "Execution timed out"}
    execute.assert_awaited_once_with("wake", timeout_s=0.1)


async def test_real_macro_timeout_retains_partial_effects_without_retry(action_runtime):
    from tests.test_runtime_action_parity_r4 import commands

    runtime, client, sim = action_runtime
    runtime.managers.macros.create_macro("Slow", [
        {"command": "POWER_ON", "targets": ["output_1"], "delay_ms": 1000},
        {"command": "POWER_OFF", "targets": ["output_2"], "delay_ms": 0},
    ], macro_id="slow")
    sim.log.clear()
    response = await client.post("/api/cec/macro/slow/execute", json={"timeout_s": 0.5})
    assert response.status == 500
    assert await response.json() == {
        "success": False, "data": None, "error": "Macro execution timed out after 0.5s"}
    assert [name for name, _ in commands(sim)] == ["cec command"]


async def test_v2_scene_pin_and_lockout_keep_exact_optional_fields(action_runtime):
    from password import MAX_PIN_FAILURES

    runtime, client, _ = action_runtime
    response = await client.post("/api/v2/scenes", json={"name": "Locked", "password_protected": True,
        "passcode": "1234", "steps": [{"type": "wait", "params": {"seconds": 0.5}}]})
    assert response.status == 201, await response.text()
    scene_id = (await response.json())["data"]["scene"]["id"]
    path = f"/api/v2/scenes/{scene_id}/execute"
    for index in range(MAX_PIN_FAILURES):
        if index % 2:
            await runtime.local.run_action("scene", scene_id, passcode="9999")
        else:
            response = await client.post(path, json={"passcode": "9999"})
            assert response.status == 403
            assert await response.json() == {"success": False, "data": {
                "error": "invalid_passcode", "scene_id": scene_id, "requires_scene_passcode": True}}
    response = await client.post(path)
    seconds = int(response.headers["Retry-After"])
    assert response.status == 429
    assert await response.json() == {"success": False, "data": {
        "error": "passcode_locked", "scene_id": scene_id, "requires_scene_passcode": True,
        "retry_after": seconds}, "error": f"Too many wrong passcodes; try again in {seconds} s"}


async def test_catalog_event_and_initial_snapshot_order_are_preserved():
    captured = asyncio.Event()
    release = asyncio.Event()
    state = HubSnapshot(connected=True, routing={1: 1})
    source = []
    reads = 0

    async def snapshot():
        nonlocal reads
        reads += 1
        value = deepcopy(state)
        if reads == 1:
            captured.set()
            await release.wait()
        return value

    def subscribe(callback):
        source.append(callback)
        return lambda: source.remove(callback)

    client = HubClientLocal(object(), snapshot_provider=snapshot, event_subscribe=subscribe)
    events = []
    client.subscribe(events.append)
    try:
        await captured.wait()
        state.routing[1] = 5
        state.profiles = [{"id": "new", "name": "New"}]
        source[0](HubEvent("routing", {"routing": {1: 5}}))
        source[0](HubEvent("catalog", {
            "profiles": state.profiles, "scenes": [], "macros": [], "shortcuts": []}))
        await asyncio.sleep(0.01)
        assert not events
        release.set()
        async with asyncio.timeout(1):
            while len([e for e in events if e.kind == "routing"]) < 2:
                await asyncio.sleep(0)
        assert [e.data["routing"][1] for e in events if e.kind == "routing"] == [1, 5]
        assert [e.data["profiles"] for e in events if e.kind == "catalog"][-1] == state.profiles
    finally:
        release.set()
        await client.close()


async def test_http_cycle_urls_preserve_default_and_encode_clamping(monkeypatch):
    from hub.integrations.hub_client_http import HubClientHttp

    client = HubClientHttp("http://unused.invalid")
    post = AsyncMock(return_value={"success": True})
    monkeypatch.setattr(client, "_post", post)
    try:
        assert await client.cycle_input("next", 2)
        assert await client.cycle_input("previous", 3, cycle=True)
        assert await client.cycle_input("next", 4, cycle=False)
        assert [call.args[0] for call in post.await_args_list] == [
            "/api/input/next?output=2", "/api/input/previous?output=3", "/api/input/next?output=4&cycle=false"]
        with pytest.raises(ValueError, match="direction"):
            await client.cycle_input("other", cycle=False)
        assert post.await_count == 3
    finally:
        await client.close()


@pytest.mark.parametrize("value", ["", "0", "False", "yes", "null"])
async def test_invalid_explicit_cycle_query_is_refused_before_writing(action_runtime, value):
    from tests.test_runtime_action_parity_r4 import commands

    _, client, sim = action_runtime
    sim.log.clear()
    response = await client.post(f"/api/input/next?output=1&cycle={value}")
    assert response.status == 400
    assert (await response.json())["error"] == "'cycle' must be true or false"
    assert not commands(sim)
