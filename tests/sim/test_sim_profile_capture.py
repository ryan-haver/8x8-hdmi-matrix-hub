"""Profile output settings round trip (API-22).

The real hub app, a real ``OreiMatrix`` and the simulator, with the fixture
hub data (``data_hub``). Every claim is checked by an independent read: a
separate ``GET`` and the saved ``profiles.json``.
"""

from __future__ import annotations

import json

import pytest

from .conftest import body

_OUTPUTS = {"1": {"input": 2, "enabled": True, "audio_mute": False, "scaler_mode": 5, "arc": True},
            "2": {"input": 3, "enabled": True, "audio_mute": True, "scaler_mode": 1, "arc": False}}


def _saved_profile(client, profile_id):
    data = json.loads((client.data_dir / "profiles.json").read_text(encoding="utf-8"))
    return next(p for p in data["profiles"] if p["id"] == profile_id)


async def _get(client, path, status=200):
    resp = await client.get(path)
    assert resp.status == status, await resp.text()
    return await body(resp)


# ============================================================================= API-22


@pytest.mark.parametrize("method", ["POST", "PUT"])
async def test_scaler_and_arc_round_trip(data_hub, method):
    if method == "POST":
        resp = await data_hub.post("/api/profile", json={"id": "api22", "name": "API-22", "outputs": _OUTPUTS})
    else:
        resp = await data_hub.put("/api/profile/movie_night", json={"outputs": _OUTPUTS})
    assert resp.status == 200, await resp.text()
    profile_id = "api22" if method == "POST" else "movie_night"
    assert (await body(resp))["data"]["outputs"] == _OUTPUTS
    assert (await _get(data_hub, f"/api/profile/{profile_id}"))["data"]["outputs"] == _OUTPUTS
    assert _saved_profile(data_hub, profile_id)["outputs"] == _OUTPUTS


@pytest.mark.parametrize("method", ["POST", "PUT"])
@pytest.mark.parametrize("setting", [
    {"scaler_mode": 0}, {"scaler_mode": 6}, {"scaler_mode": "2"}, {"scaler_mode": True}, {"scaler_mode": 2.0},
    {"arc": 1}, {"arc": "on"},
])
async def test_invalid_scaler_or_arc_is_rejected_and_nothing_changes(data_hub, method, setting):
    before = (await _get(data_hub, "/api/profile/movie_night"))["data"]
    outputs = {"1": {"input": 2, **setting}}
    if method == "POST":
        resp = await data_hub.post("/api/profile", json={"id": "movie_night", "name": "X", "outputs": outputs})
    else:
        resp = await data_hub.put("/api/profile/movie_night", json={"outputs": outputs})
    assert resp.status == 400, await resp.text()
    assert (await _get(data_hub, "/api/profile/movie_night"))["data"] == before


async def test_profiles_without_the_settings_are_unchanged(data_hub):
    """Omitted (or null) scaler/ARC stay unset: existing profiles read exactly as before."""
    outputs = {"1": {"input": 4, "scaler_mode": None, "arc": None}}
    resp = await data_hub.post("/api/profile", json={"id": "plain", "name": "Plain", "outputs": outputs})
    assert resp.status == 200, await resp.text()
    assert (await _get(data_hub, "/api/profile/plain"))["data"]["outputs"] == {
        "1": {"input": 4, "enabled": True, "audio_mute": False}}
