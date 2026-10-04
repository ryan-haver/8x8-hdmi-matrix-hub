"""Follow-ups to API-22/API-27 on the real hub app, a real OreiMatrix and the simulator.

* API-29: recall and scene profile steps apply a profile's saved ``scaler_mode``
  (``set video scaler``, API value 1-5 -> device code 0-4) and ``arc`` (``set arc``)
  through the one shared state writer; a profile without them leaves them alone.
* API-30: ``PUT /api/profile/{id}`` refuses out-of-range outputs/inputs like ``POST``.
* API-31: save-current records each output's real stream state (``allout``).
"""

from __future__ import annotations

import json

import pytest

from .conftest import body, sim_writes

_SET = {"1": {"input": 3, "scaler_mode": 5, "arc": True}, "2": {"input": 4, "scaler_mode": 1, "arc": False}}


async def _create(hub, pid, outputs):
    resp = await hub.post("/api/profile", json={"id": pid, "name": pid, "outputs": outputs})
    assert resp.status == 200, await resp.text()


def _state(simulator, idx):
    out = simulator.state.outputs[idx]
    return out.scaler, out.arc


# ============================================================================= API-29


async def test_recall_applies_scaler_and_arc(data_hub, simulator):
    simulator.state.outputs[0].scaler, simulator.state.outputs[0].arc = 0, 0
    simulator.state.outputs[1].scaler, simulator.state.outputs[1].arc = 3, 1
    await _create(data_hub, "api29", _SET)
    resp = await data_hub.post("/api/profile/api29/recall")
    assert resp.status == 200, await resp.text()
    assert _state(simulator, 0) == (4, 1)  # API 5 (audio only) -> device 4, ARC on
    assert _state(simulator, 1) == (0, 0)  # API 1 (passthrough) -> device 0, ARC off
    assert [e["payload"]["scaler"] for e in sim_writes(simulator, "set video scaler")] == [[1, 4], [2, 0]]
    assert [e["payload"]["arc"] for e in sim_writes(simulator, "set arc")] == [[1, 1], [2, 0]]


async def test_recall_without_the_settings_leaves_them_untouched(data_hub, simulator):
    simulator.state.outputs[0].scaler, simulator.state.outputs[0].arc = 2, 1
    await _create(data_hub, "plain", {"1": {"input": 3}})
    resp = await data_hub.post("/api/profile/plain/recall")
    assert resp.status == 200, await resp.text()
    assert _state(simulator, 0) == (2, 1)
    assert sim_writes(simulator, "set video scaler") == []
    assert sim_writes(simulator, "set arc") == []


async def test_recall_reports_a_refused_scaler_write(data_hub, simulator):
    await _create(data_hub, "api29", {"1": {"input": 3, "scaler_mode": 5}})
    simulator.faults.update({"reject_writes": True, "comheads": ["set video scaler"]})
    resp = await data_hub.post("/api/profile/api29/recall")
    assert resp.status in (207, 500), await resp.text()
    data = await body(resp)
    assert any("scaler 5" in e for e in data["data"]["errors"])


async def test_scene_profile_step_applies_the_same_state(data_hub, simulator):
    await _create(data_hub, "api29", _SET)
    resp = await data_hub.post("/api/v2/scenes", json={"name": "S", "steps": [{"type": "profile", "id": "api29"}]})
    assert resp.status == 201, await resp.text()
    sid = (await body(resp))["data"]["scene"]["id"]
    resp = await data_hub.post(f"/api/v2/scenes/{sid}/execute")
    assert resp.status == 200, await resp.text()
    assert _state(simulator, 0) == (4, 1)
    assert _state(simulator, 1) == (0, 0)


async def test_scene_override_leaves_scaler_and_arc_alone(data_hub, simulator):
    simulator.state.outputs[0].scaler, simulator.state.outputs[0].arc = 2, 0
    await _create(data_hub, "api29", _SET)
    resp = await data_hub.post("/api/v2/scenes", json={"name": "S", "steps": [{"type": "profile", "id": "api29"}]})
    assert resp.status == 201, await resp.text()
    sid = (await body(resp))["data"]["scene"]["id"]
    resp = await data_hub.put(f"/api/v2/scenes/{sid}",
                              json={"overrides": {"api29": {"1": {"scaler": True, "arc": True}}}})
    assert resp.status == 200, await resp.text()
    assert (await data_hub.post(f"/api/v2/scenes/{sid}/execute")).status == 200
    assert _state(simulator, 0) == (2, 0)  # overridden: unchanged
    assert _state(simulator, 1) == (0, 0)  # output 2 still applied


async def test_scene_validation_reports_scaler_and_arc_conflicts(data_hub):
    await _create(data_hub, "a29", {"1": {"input": 3, "scaler_mode": 5, "arc": True}})
    await _create(data_hub, "b29", {"1": {"input": 3, "scaler_mode": 4, "arc": False}})
    resp = await data_hub.post("/api/v2/scenes", json={
        "name": "S", "steps": [{"type": "profile", "id": "a29"}, {"type": "profile", "id": "b29"}]})
    sid = (await body(resp))["data"]["scene"]["id"]
    resp = await data_hub.post(f"/api/v2/scenes/{sid}/validate")
    conflicts = (await body(resp))["data"]["conflicts"]
    assert {c["setting"] for c in conflicts} == {"scaler", "arc"}


# ============================================================================= API-30


@pytest.mark.parametrize("outputs", [{"9": {"input": 1}}, {"0": {"input": 1}}, {"1": {"input": 9}},
                                     {"1": {"input": 0}}, {"1": {}}, {"x": {"input": 1}}])
async def test_put_refuses_what_post_refuses(data_hub, outputs):
    before = (await body(await data_hub.get("/api/profile/movie_night")))["data"]
    post = await data_hub.post("/api/profile", json={"id": "movie_night", "name": "X", "outputs": outputs})
    put = await data_hub.put("/api/profile/movie_night", json={"outputs": outputs})
    assert post.status == put.status == 400, (await post.text(), await put.text())
    assert (await body(post))["error"] == (await body(put))["error"]
    assert (await body(await data_hub.get("/api/profile/movie_night")))["data"] == before
    saved = json.loads((data_hub.data_dir / "profiles.json").read_text(encoding="utf-8"))
    assert next(p for p in saved["profiles"] if p["id"] == "movie_night")["outputs"] == before["outputs"]


async def test_put_accepts_valid_outputs(data_hub):
    resp = await data_hub.put("/api/profile/movie_night", json={"outputs": {"8": {"input": 8}}})
    assert resp.status == 200, await resp.text()


# ============================================================================= API-31


async def test_save_current_records_the_real_stream_state(data_hub, simulator):
    from rest_api.utils import get_matrix_device

    get_matrix_device()._status_cache_ttl = 0.0
    for i, out in enumerate(simulator.state.outputs):
        out.stream = 0 if i in (2, 5) else 1
    resp = await data_hub.post("/api/scene/save-current", json={"id": "cap", "name": "Cap"})
    assert resp.status == 200, await resp.text()
    outputs = (await body(await data_hub.get("/api/profile/cap")))["data"]["outputs"]
    assert {k: v["enabled"] for k, v in outputs.items()} == {str(o): o not in (3, 6) for o in range(1, 9)}


async def test_save_current_refuses_an_unknown_stream_state(data_hub, simulator, monkeypatch):
    """A stream value that is neither 0 nor 1 is not guessed (no ``enabled: true`` by default)."""
    from rest_api.utils import get_matrix_device

    device = get_matrix_device()
    real = device.get_output_status

    async def odd(force_refresh: bool = False):
        status = await real(force_refresh=True)
        status["allout"] = [1, 1, 7, 1, 1, 1, 1, 1, 255]
        return status

    monkeypatch.setattr(device, "get_output_status", odd)
    resp = await data_hub.post("/api/scene/save-current", json={"id": "cap", "name": "Cap"})
    assert resp.status == 502, await resp.text()
    assert (await data_hub.get("/api/profile/cap")).status == 404
