"""HTTP action scenes execute the unified catalog through the registered app."""

from unittest.mock import AsyncMock
from urllib.parse import quote

import pytest

from hub.integrations.hub_client_http import HubClientHttp
from password import get_pin_tracker
from tests import test_runtime_action_parity_r4 as shared

action_runtime = shared.action_runtime


@pytest.fixture
async def http_client(action_runtime):
    _, client, _ = action_runtime
    remote = HubClientHttp(str(client.make_url("/")))
    try:
        yield remote
    finally:
        await remote.close()


async def create_scene(client, *, protected=False, missing_step=False):
    await shared.profile(client)
    steps = [{"type": "profile", "id": "movie"}]
    if missing_step:
        steps.append({"type": "profile", "id": "absent_profile"})
    body = {"name": "Unified scene only", "steps": steps}
    if protected:
        body.update(password_protected=True, passcode="5678")
    response = await client.post("/api/v2/scenes", json=body)
    assert response.status == 201, await response.text()
    return (await response.json())["data"]["scene"]["id"]


async def test_http_unified_scene_matches_local_without_a_profile_alias(action_runtime, http_client):
    runtime, client, sim = action_runtime
    scene_id = await create_scene(client)
    assert runtime.managers.profiles.get_profile(scene_id) is None
    # This is the old mapping: a unique unified scene cannot be recalled as a profile.
    legacy = await client.post(f"/api/scene/{scene_id}/recall")
    assert legacy.status == 404
    sim.log.clear()
    http = await http_client.run_action("scene", scene_id)
    assert http["success"] is True, http
    assert set(http) == {"success", "data"}
    assert http["data"]["scene_id"] == scene_id
    expected_commands = shared.commands(sim)
    assert len(expected_commands) == 7
    sim.log.clear()
    local = await runtime.local.run_action("scene", scene_id)
    assert local["success"] is True
    assert http["data"] == local["data"]["result"]
    assert shared.commands(sim) == expected_commands
    assert [o.source for o in sim.state.outputs[:2]] == [4, 5]
    assert len(runtime.managers.scenes.get_scene(scene_id).execution_history) == 2


async def test_scene_mapping_cannot_recall_an_identically_named_profile(action_runtime, http_client):
    runtime, client, sim = action_runtime
    scene_id = await create_scene(client)
    response = await client.post("/api/profile", json={
        "id": scene_id, "name": "Decoy profile", "outputs": {"1": {"input": 8}}})
    assert response.status == 200
    sim.log.clear()
    result = await http_client.run_action("scene", scene_id)
    assert result["success"] is True
    assert result["data"]["scene_id"] == scene_id
    assert sim.state.outputs[0].source == 4
    assert len(shared.commands(sim)) == 7
    assert len(runtime.managers.scenes.get_scene(scene_id).execution_history) == 1


@pytest.mark.parametrize("pin,code", [(None, "passcode_required"), ("9999", "invalid_passcode")])
async def test_http_scene_pin_refusal_matches_local_and_preserves_no_effects(action_runtime, http_client, pin, code):
    runtime, client, sim = action_runtime
    scene_id = await create_scene(client, protected=True)
    sim.log.clear()
    http = await http_client.run_action("scene", scene_id, passcode=pin)
    assert http == {"success": False, "data": {
        "error": code, "scene_id": scene_id, "requires_scene_passcode": True}}
    assert get_pin_tracker().failures(f"scene:{scene_id}") == (0 if pin is None else 1)
    local = await runtime.local.run_action("scene", scene_id, passcode=pin)
    assert local["success"] is False
    assert local["status"] == 403
    assert local["data"]["result"]["code"] == code
    assert get_pin_tracker().failures(f"scene:{scene_id}") == (0 if pin is None else 2)
    assert shared.commands(sim) == []
    assert not runtime.managers.scenes.get_scene(scene_id).execution_history


async def test_http_scene_passcode_is_forwarded_to_shared_execution(action_runtime, http_client):
    runtime, client, sim = action_runtime
    scene_id = await create_scene(client, protected=True)
    http = await http_client.run_action("scene", scene_id, passcode="5678")
    assert http["success"] is True, http
    local = await runtime.local.run_action("scene", scene_id, passcode="5678")
    assert local["success"] is True
    assert http["data"] == local["data"]["result"]
    assert get_pin_tracker().failures(f"scene:{scene_id}") == 0
    assert sim.state.outputs[0].source == 4


async def test_http_scene_preserves_partial_execution_result_and_effects(action_runtime, http_client):
    runtime, client, sim = action_runtime
    scene_id = await create_scene(client, missing_step=True)
    sim.log.clear()
    http = await http_client.run_action("scene", scene_id)
    assert http["success"] is False
    assert set(http) == {"success", "data"}
    assert http["data"]["scene_id"] == scene_id
    assert http["data"]["steps_completed"] == 1
    assert http["data"]["total_steps"] == 2
    assert [step["success"] for step in http["data"]["step_results"]] == [True, False]
    assert http["data"]["step_results"][1]["error"] == "Profile not found"
    expected_commands = shared.commands(sim)
    assert len(expected_commands) == 7
    assert [o.source for o in sim.state.outputs[:2]] == [4, 5]
    sim.log.clear()
    local = await runtime.local.run_action("scene", scene_id)
    assert local["status"] == 207 and local["data"]["partial"] is True
    assert http["data"] == local["data"]["result"]
    assert shared.commands(sim) == expected_commands
    response = await client.post(f"/api/v2/scenes/{scene_id}/execute")
    assert response.status == 207 and await response.json() == http


@pytest.mark.parametrize("kind,path", [
    ("scene", "/api/v2/scenes/{}/execute"),
    ("profile", "/api/profile/{}/recall"),
    ("macro", "/api/cec/macro/{}/execute"),
    ("shortcut", "/api/shortcuts/{}/execute"),
])
async def test_http_action_url_encoding_and_non_scene_mappings_are_preserved(monkeypatch, kind, path):
    remote = HubClientHttp("http://unused.invalid")
    response = {"success": False, "data": {"detail": "retained"}, "error": "retained"}
    post = AsyncMock(return_value=response)
    monkeypatch.setattr(remote, "_post", post)
    try:
        action_id = "night / café?%"
        result = await remote.run_action(kind, action_id, passcode="1234")
        assert result is response
        post.assert_awaited_once_with(path.format(quote(action_id, safe="")), {"passcode": "1234"})
        post.reset_mock()
        await remote.run_action(kind, action_id)
        post.assert_awaited_once_with(path.format(quote(action_id, safe="")), None)
    finally:
        await remote.close()
