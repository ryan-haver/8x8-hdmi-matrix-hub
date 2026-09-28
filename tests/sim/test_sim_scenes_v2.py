"""REST ``/api/v2/scenes``: the full route set, on the real hub app, a real OreiMatrix and the simulator.

The hub data is ``tests/e2e/fixtures/data`` (see ``data_hub``): profiles
``movie_night`` (input 2 -> outputs 1-2, HDR 1 / HDCP 3 on output 1, output 2
muted, quick-access macro ``macro_tv_on``), ``game_day`` (input 5 -> outputs
1-3, output 3 muted), ``kids_gaming`` (protected, input 6 -> output 1); scenes
``scene_movienight01``, ``scene_kidslocked`` (passcode 1234) and
``scene_goodnight01`` (mute all + macro ``macro_all_off``).

Every execution test asserts the effect on the simulator (routing, output
settings, CEC frames in its command log), not only the HTTP answer. WP-C1
regressions: API-01, API-02, API-03, API-04, API-05, API-06, API-08, API-13,
VAL-02.
"""

from __future__ import annotations

import json

import pytest

from .conftest import CEC_IN_POWER_OFF as IN_POWER_OFF
from .conftest import CEC_IN_POWER_ON as IN_POWER_ON
from .conftest import CEC_OUT_POWER_OFF as OUT_POWER_OFF
from .conftest import CEC_OUT_POWER_ON as OUT_POWER_ON
from .conftest import body, cec_frames, sim_writes

PASSCODE = "1234"  # the fixture's hash of scene_kidslocked / kids_gaming


async def create(hub, **scene) -> dict:
    resp = await hub.post("/api/v2/scenes", json=scene)
    assert resp.status == 201, await resp.text()
    return (await body(resp))["data"]["scene"]


# ============================================================================= CRUD


async def test_list_returns_the_saved_scenes(data_hub):
    resp = await data_hub.get("/api/v2/scenes")
    assert resp.status == 200
    data = (await body(resp))["data"]
    assert data["count"] == 3
    assert [s["id"] for s in data["scenes"]] == ["scene_movienight01", "scene_kidslocked", "scene_goodnight01"]


async def test_get_one_scene_and_404(data_hub):
    resp = await data_hub.get("/api/v2/scenes/scene_goodnight01")
    assert resp.status == 200
    scene = (await body(resp))["data"]["scene"]
    assert scene["steps"] == [{"type": "system_action", "id": "mute_all_audio"}, {"type": "macro", "id": "macro_all_off"}]
    assert (await data_hub.get("/api/v2/scenes/nope")).status == 404


async def test_create_with_a_profile_step_while_profiles_exist(data_hub):
    """API-05: the protected-profile check used ``p.id`` on the dicts ``list_profiles()`` returns -> 500."""
    scene = await create(data_hub, name="Game", steps=[{"type": "profile", "id": "game_day"}])
    assert scene["id"].startswith("scene_")
    assert scene["steps"] == [{"type": "profile", "id": "game_day"}]
    # persisted
    saved = json.loads((data_hub.data_dir / "scenes.json").read_text(encoding="utf-8"))
    assert scene["id"] in [s["id"] for s in saved["scenes"]]


async def test_create_rejects_a_protected_profile_in_an_unprotected_scene(data_hub):
    resp = await data_hub.post("/api/v2/scenes", json={"name": "Kids", "steps": [{"type": "profile", "id": "kids_gaming"}]})
    assert resp.status == 400
    assert "password-protected" in (await body(resp))["error"]
    resp = await data_hub.post(
        "/api/v2/scenes",
        json={"name": "Kids", "steps": [{"type": "profile", "id": "kids_gaming"}], "password_protected": True,
              "passcode": "4321"},
    )
    assert resp.status == 201, await resp.text()


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Bad", "steps": [{"type": "delay", "id": "x"}]},
        {"name": "Bad", "steps": [{"type": "profile", "id": ""}]},
        {"name": "Dup", "steps": [{"type": "profile", "id": "game_day"}, {"type": "profile", "id": "game_day"}]},
        {"name": "Locked", "password_protected": True},
    ],
)
async def test_create_rejects_invalid_scenes(data_hub, payload):
    resp = await data_hub.post("/api/v2/scenes", json=payload)
    assert resp.status == 400, await resp.text()
    assert (await body(await data_hub.get("/api/v2/scenes")))["data"]["count"] == 3


async def test_create_rejects_a_body_that_is_not_json(data_hub):
    resp = await data_hub.post("/api/v2/scenes", data="{nope", headers={"Content-Type": "application/json"})
    assert resp.status == 400


async def test_update_steps_while_profiles_exist(data_hub):
    """API-05: PUT with steps ran the same broken ``p.id`` check -> 500."""
    resp = await data_hub.put(
        "/api/v2/scenes/scene_goodnight01",
        json={"name": "Good Night 2", "steps": [{"type": "profile", "id": "game_day"}]},
    )
    assert resp.status == 200, await resp.text()
    scene = (await body(resp))["data"]["scene"]
    assert scene["name"] == "Good Night 2"
    assert scene["steps"] == [{"type": "profile", "id": "game_day"}]


async def test_update_rejects_a_protected_profile_in_an_unprotected_scene(data_hub):
    resp = await data_hub.put("/api/v2/scenes/scene_goodnight01", json={"steps": [{"type": "profile", "id": "kids_gaming"}]})
    assert resp.status == 400
    scene = (await body(await data_hub.get("/api/v2/scenes/scene_goodnight01")))["data"]["scene"]
    assert scene["steps"][0] == {"type": "system_action", "id": "mute_all_audio"}


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "", "icon": "X"},  # empty name
        {"name": "Renamed", "steps": [{"type": "profile", "id": "game_day"}, {"type": "profile", "id": "game_day"}]},
        {"name": "Renamed", "password_protected": True},  # no passcode
    ],
)
async def test_invalid_update_leaves_the_scene_unchanged(data_hub, payload):
    """API-13: update_scene mutated the in-memory scene before validating it."""
    before = (await body(await data_hub.get("/api/v2/scenes/scene_goodnight01")))["data"]["scene"]
    resp = await data_hub.put("/api/v2/scenes/scene_goodnight01", json=payload)
    assert resp.status == 400, await resp.text()
    after = (await body(await data_hub.get("/api/v2/scenes/scene_goodnight01")))["data"]["scene"]
    assert after == before
    # and the next successful save does not persist the rejected values either
    assert (await data_hub.put("/api/v2/scenes/scene_goodnight01", json={"favorite": True})).status == 200
    saved = json.loads((data_hub.data_dir / "scenes.json").read_text(encoding="utf-8"))
    persisted = next(s for s in saved["scenes"] if s["id"] == "scene_goodnight01")
    assert persisted["name"] == "Good Night" and persisted["icon"] == before["icon"]
    assert persisted["steps"] == before["steps"] and persisted["password_protected"] is False


async def test_update_unknown_scene_is_rejected(data_hub):
    resp = await data_hub.put("/api/v2/scenes/nope", json={"name": "x"})
    assert resp.status in (400, 404)
    assert (await body(resp))["success"] is False


async def test_delete(data_hub):
    resp = await data_hub.delete("/api/v2/scenes/scene_goodnight01")
    assert resp.status == 200
    assert (await data_hub.get("/api/v2/scenes/scene_goodnight01")).status == 404
    assert (await data_hub.delete("/api/v2/scenes/scene_goodnight01")).status == 404


async def test_add_and_remove_steps(data_hub):
    resp = await data_hub.post("/api/v2/scenes/scene_goodnight01/steps", json={"type": "profile", "id": "game_day"})
    assert resp.status == 200, await resp.text()
    assert (await body(resp))["data"]["scene"]["steps"][-1] == {"type": "profile", "id": "game_day"}
    # invalid step
    assert (await data_hub.post("/api/v2/scenes/scene_goodnight01/steps", json={"type": "nope", "id": "x"})).status == 400
    # protected profile into an unprotected scene
    resp = await data_hub.post("/api/v2/scenes/scene_goodnight01/steps", json={"type": "profile", "id": "kids_gaming"})
    assert resp.status == 400
    # remove
    resp = await data_hub.delete("/api/v2/scenes/scene_goodnight01/steps/2")
    assert resp.status == 200
    assert len((await body(resp))["data"]["scene"]["steps"]) == 2
    assert (await data_hub.delete("/api/v2/scenes/scene_goodnight01/steps/9")).status == 400
    assert (await data_hub.delete("/api/v2/scenes/scene_goodnight01/steps/x")).status == 400


async def test_set_and_clear_an_override(data_hub):
    override = {"profile_id": "game_day", "output_num": 3, "setting_key": "audio_mute"}
    resp = await data_hub.put("/api/v2/scenes/scene_goodnight01/override", json={**override, "disabled": True})
    assert resp.status == 200
    assert (await body(resp))["data"]["scene"]["overrides"] == {"game_day": {"3": {"audio_mute": True}}}
    resp = await data_hub.delete("/api/v2/scenes/scene_goodnight01/override", json=override)
    assert resp.status == 200
    assert (await body(resp))["data"]["scene"]["overrides"] == {}
    resp = await data_hub.put("/api/v2/scenes/scene_goodnight01/override", json={"profile_id": "game_day"})
    assert resp.status == 400
    resp = await data_hub.put("/api/v2/scenes/nope/override", json={**override, "disabled": True})
    assert resp.status == 400


async def test_validate_reports_conflicts(data_hub):
    resp = await data_hub.post("/api/v2/scenes/scene_movienight01/validate")
    assert resp.status == 200
    data = (await body(resp))["data"]
    assert data["scene_id"] == "scene_movienight01" and isinstance(data["conflicts"], list)
    assert (await data_hub.post("/api/v2/scenes/nope/validate")).status == 404


async def test_history_404(data_hub):
    assert (await data_hub.get("/api/v2/scenes/nope/history")).status == 404


# ============================================================================= execution


async def test_execute_unknown_scene_is_404(data_hub, simulator):
    """API-08: answered 200 ``success: true`` with an error inside."""
    resp = await data_hub.post("/api/v2/scenes/nope/execute")
    assert resp.status == 404
    assert (await body(resp))["success"] is False
    assert sim_writes(simulator) == []


async def test_execute_protected_scene_needs_its_passcode(data_hub, simulator):
    resp = await data_hub.post("/api/v2/scenes/scene_kidslocked/execute")
    assert resp.status == 403
    assert (await body(resp))["data"]["error"] == "passcode_required"
    resp = await data_hub.post("/api/v2/scenes/scene_kidslocked/execute", json={"passcode": "0000"})
    assert resp.status == 403
    assert (await body(resp))["data"]["error"] == "invalid_passcode"
    assert sim_writes(simulator) == []


async def test_execute_profile_and_route_steps(data_hub, simulator):
    """API-01: profile steps and ``route_all_to_output`` called ``matrix.switch()``, which does not exist."""
    simulator.state.outputs[0].source = 1
    resp = await data_hub.post("/api/v2/scenes/scene_kidslocked/execute", json={"passcode": PASSCODE})
    assert resp.status == 200, await resp.text()
    data = (await body(resp))["data"]
    assert data["success"] is True and data["steps_completed"] == 2 and data["total_steps"] == 2
    assert [r["success"] for r in data["step_results"]] == [True, True]
    assert simulator.state.outputs[0].source == 6
    assert len(sim_writes(simulator, "video switch")) == 2  # the profile, then the shortcut


async def test_execute_profile_step_applies_output_settings_and_logs(data_hub, simulator):
    """A profile step applies routing, HDR/HDCP (API 1-based HDR -> device code) and mute; API-02 logs it."""
    simulator.state.outputs[0].hdr, simulator.state.outputs[0].hdcp = 2, 1
    simulator.state.outputs[1].source = 8
    scene = await create(data_hub, name="Movie", steps=[{"type": "profile", "id": "movie_night"}])
    resp = await data_hub.post(f"/api/v2/scenes/{scene['id']}/execute")
    assert resp.status == 200, await resp.text()
    out1, out2 = simulator.state.outputs[0], simulator.state.outputs[1]
    assert (out1.source, out2.source) == (2, 2)
    assert out1.hdr == 0  # API HDR 1 (passthrough) is device code 0
    assert out1.hdcp == 3
    assert (out1.audio_mute, out2.audio_mute) == (0, 1)
    # API-02: the profile's execution log is written (and saved)
    entries = (await body(await data_hub.get("/api/profile/movie_night/execution-log")))["data"]["log"]
    assert entries[-1]["scene_id"] == scene["id"] and entries[-1]["status"] == "success"
    saved = json.loads((data_hub.data_dir / "profiles.json").read_text(encoding="utf-8"))
    movie = next(p for p in saved["profiles"] if p["id"] == "movie_night")
    assert movie["execution_log"][-1]["scene_id"] == scene["id"]
    # and the scene's own history
    hist = (await body(await data_hub.get(f"/api/v2/scenes/{scene['id']}/history")))["data"]
    assert hist["execution_history"][-1]["status"] == "success"
    assert hist["last_executed"] is not None


async def test_execute_profile_step_runs_the_profile_macros_through_the_macro_manager(data_hub, simulator):
    """API-03 + VAL-02: the profile's macros send real CEC frames (targets ``output_1`` / ``input_2``)."""
    scene = await create(data_hub, name="Movie", steps=[{"type": "profile", "id": "movie_night"}])
    resp = await data_hub.post(f"/api/v2/scenes/{scene['id']}/execute")
    assert resp.status == 200, await resp.text()
    assert cec_frames(simulator, obj=1, index=OUT_POWER_ON, to=1) == 1
    assert cec_frames(simulator, obj=0, index=IN_POWER_ON, to=2) == 1


async def test_overrides_leave_the_setting_unchanged(data_hub, simulator):
    """API-04: an override meant "set to the default" (an input override routed Input 1)."""
    simulator.state.outputs[0].source = 7
    simulator.state.outputs[2].audio_mute = 0
    simulator.state.outputs[2].source = 4
    scene = await create(data_hub, name="Game", steps=[{"type": "profile", "id": "game_day"}])
    resp = await data_hub.put(
        f"/api/v2/scenes/{scene['id']}",
        json={"overrides": {"game_day": {"1": {"input": True}, "3": {"audio_mute": True}, "2": {"input": False}}}},
    )
    assert resp.status == 200, await resp.text()
    resp = await data_hub.post(f"/api/v2/scenes/{scene['id']}/execute")
    assert resp.status == 200, await resp.text()
    outs = simulator.state.outputs
    assert outs[0].source == 7  # input override: routing left alone (not Input 1)
    assert outs[1].source == 5  # override present but not disabled -> applied
    assert outs[2].source == 5
    assert outs[2].audio_mute == 0  # mute override: left alone
    switched = [e["payload"]["source"] for e in sim_writes(simulator, "video switch")]
    assert [1, 1] not in switched and [1, 5] not in switched
    mutes = [e["payload"]["mute"] for e in sim_writes(simulator, "set output audio mute")]
    assert all(m[0] != 3 for m in mutes)


async def test_execute_macro_and_shortcut_steps(data_hub, simulator):
    """Macro steps send CEC frames (VAL-02); mute-all mutes every output."""
    resp = await data_hub.post("/api/v2/scenes/scene_goodnight01/execute")
    assert resp.status == 200, await resp.text()
    data = (await body(resp))["data"]
    assert data["success"] is True and data["steps_completed"] == 2
    assert [o.audio_mute for o in simulator.state.outputs] == [1] * 8
    for n in (1, 2, 6):
        assert cec_frames(simulator, obj=0, index=IN_POWER_OFF, to=n) == 1
    for n in (1, 2):
        assert cec_frames(simulator, obj=1, index=OUT_POWER_OFF, to=n) == 1


async def test_power_off_all_step_powers_the_matrix_off_once(data_hub, simulator):
    """API-06: ``power_off_all`` sent ``set poweronoff`` eight times."""
    scene = await create(data_hub, name="Off", steps=[{"type": "system_action", "id": "power_off_all"}])
    resp = await data_hub.post(f"/api/v2/scenes/{scene['id']}/execute")
    assert resp.status == 200, await resp.text()
    assert simulator.state.system["power"] == 0
    assert len(sim_writes(simulator, "set poweronoff")) == 1


async def test_partial_failure_is_207_with_step_results(data_hub, simulator):
    """API-08: a scene whose steps failed answered 200 ``success: true``."""
    scene = await create(
        data_hub,
        name="Half",
        steps=[{"type": "system_action", "id": "mute_all_audio"}, {"type": "profile", "id": "no_such_profile"}],
    )
    resp = await data_hub.post(f"/api/v2/scenes/{scene['id']}/execute")
    assert resp.status == 207, await resp.text()
    payload = await body(resp)
    assert payload["success"] is False
    data = payload["data"]
    assert data["steps_completed"] == 1 and data["total_steps"] == 2
    assert [r["success"] for r in data["step_results"]] == [True, False]
    assert "not found" in data["step_results"][1]["error"].lower()
    assert [o.audio_mute for o in simulator.state.outputs] == [1] * 8
    hist = (await body(await data_hub.get(f"/api/v2/scenes/{scene['id']}/history")))["data"]
    assert hist["execution_history"][-1]["status"] == "error"


async def test_every_step_failing_is_500(data_hub, simulator):
    """API-08: the matrix rejecting every write is a failed scene, not a 200."""
    simulator.faults.reject_writes = True
    resp = await data_hub.post("/api/v2/scenes/scene_goodnight01/execute")
    assert resp.status == 500, await resp.text()
    payload = await body(resp)
    assert payload["success"] is False
    assert payload["data"]["steps_completed"] == 0
    assert [r["success"] for r in payload["data"]["step_results"]] == [False, False]
    assert [o.audio_mute for o in simulator.state.outputs] == [0] * 8


async def test_a_failed_profile_output_fails_the_step(data_hub, simulator):
    """API-08: ``_execute_profile`` ignored the matrix's answers, so a rejected write still counted as success."""
    simulator.faults.reject_writes = True
    scene = await create(data_hub, name="Movie", steps=[{"type": "profile", "id": "movie_night"}])
    resp = await data_hub.post(f"/api/v2/scenes/{scene['id']}/execute")
    assert resp.status == 500, await resp.text()
    result = (await body(resp))["data"]["step_results"][0]
    assert result["success"] is False
    assert "output 1" in result["error"].lower()


async def test_empty_scene_succeeds(data_hub, simulator):
    scene = await create(data_hub, name="Empty")
    resp = await data_hub.post(f"/api/v2/scenes/{scene['id']}/execute")
    assert resp.status == 200
    assert (await body(resp))["data"]["total_steps"] == 0
    assert sim_writes(simulator) == []
