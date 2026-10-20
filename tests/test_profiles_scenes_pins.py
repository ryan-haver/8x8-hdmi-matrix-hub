"""
Per-item PINs for Profiles and Scenes over REST (WP-F1).

- F-SEC-004: passcodes are stored only as PBKDF2 hashes (a plaintext PIN on
  disk is hashed on load).
- F-SEC-005 / SEC-04: ``passcode_hash`` is never sent to a client, on any
  profile or scene route; scenes report inherited protection.
- F-SEC-006 / SEC-05: setting a PIN is possible on create and update;
  changing or removing it, or deleting a protected item, needs the current PIN.
- F-SEC-007 / SEC-06: wrong PINs lock the item out (429), and PBKDF2 runs off
  the event loop.
- UI-47: ``GET /api/profiles`` summaries carry ``password_protected``.
"""

import asyncio
import json
import os
import threading
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

import password
from password import MAX_PIN_FAILURES, get_pin_tracker, reset_pin_lockout
from rest_api import create_rest_app, set_matrix_device

PIN = "1234"
OTHER_PIN = "5678"


class FakeClock:
    def __init__(self):
        self.now = 10_000.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture(autouse=True)
def _fast_pins(monkeypatch):
    """Cheap hashing, a clean limiter and a controllable limiter clock for every test."""
    import persistence

    monkeypatch.setattr(persistence, "get_legacy_data_paths", lambda: [])
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    clock = FakeClock()
    monkeypatch.setattr(get_pin_tracker(), "clock", clock)
    reset_pin_lockout()
    yield clock
    reset_pin_lockout()


@pytest.fixture
def clock(_fast_pins) -> FakeClock:
    return _fast_pins


@pytest.fixture
def matrix(mock_matrix):
    mock_matrix.switch = AsyncMock(return_value=True)
    mock_matrix.get_output_status = AsyncMock(
        return_value={
            "allsource": [1, 2, 3, 4, 5, 6, 7, 8],
            "allout": [1, 1, 1, 1, 1, 1, 1, 1],
            "allaudiomute": [0, 0, 0, 0, 0, 0, 0, 0],
            "allhdr": [3, 3, 3, 3, 3, 3, 3, 3],
            "allhdcp": [3, 3, 3, 3, 3, 3, 3, 3],
        }
    )
    mock_matrix.set_audio_mute = AsyncMock(return_value=True)
    mock_matrix.set_hdr_mode = AsyncMock(return_value=True)
    mock_matrix.set_hdcp_mode = AsyncMock(return_value=True)
    return mock_matrix


@pytest.fixture
async def client(aiohttp_client, matrix):
    set_matrix_device(matrix, {i: f"Input {i}" for i in range(1, 9)})
    return await aiohttp_client(create_rest_app())


@pytest.fixture
def data_dir() -> Path:
    return Path(os.environ["MATRIX_DATA_DIR"])


async def make_profile(client, profile_id: str, pin: str | None = None, **extra) -> dict:
    body = {"id": profile_id, "name": profile_id.title(), "outputs": {"1": {"input": 2}}, **extra}
    if pin:
        body["passcode"] = pin
    resp = await client.post("/api/profile", json=body)
    assert resp.status == 200, await resp.text()
    return (await resp.json())["data"]


async def make_scene(client, pin: str | None = None, **body) -> dict:
    body.setdefault("name", "Scene")
    if pin:
        body.update(password_protected=True, passcode=pin)
    resp = await client.post("/api/v2/scenes", json=body)
    assert resp.status == 201, await resp.text()
    return (await resp.json())["data"]["scene"]


def assert_no_hash(text: str) -> None:
    """Neither the field nor any PBKDF2 string is in a response body."""
    assert "passcode_hash" not in text
    assert "pbkdf2" not in text


async def status_and_error(resp) -> tuple[int, str | None]:
    body = await resp.json()
    data = body.get("data")
    return resp.status, (data or {}).get("error") if isinstance(data, dict) else body.get("error")


# =============================================================================
# F-SEC-005: the hash never leaves the hub
# =============================================================================


class TestHashNeverSent:
    async def test_profile_routes_never_return_the_hash(self, client, data_dir):
        created = await client.post(
            "/api/profile", json={"id": "kids", "name": "Kids", "outputs": {"1": {"input": 6}}, "passcode": PIN}
        )
        assert created.status == 200
        assert_no_hash(await created.text())
        assert (await created.json())["data"]["password_protected"] is True

        for path in ("/api/profile/kids", "/api/profiles", "/api/profiles/favorites", "/api/scene/kids", "/api/scenes"):
            resp = await client.get(path)
            assert resp.status == 200, path
            assert_no_hash(await resp.text())

        updated = await client.put("/api/profile/kids", json={"name": "Kids room", "favorite": True})
        assert updated.status == 200
        assert_no_hash(await updated.text())
        favorites = await client.get("/api/profiles/favorites")
        assert_no_hash(await favorites.text())
        assert "Kids room" in await favorites.text()

    async def test_profile_hash_is_still_persisted(self, client, data_dir):
        await make_profile(client, "kids", PIN)
        saved = json.loads((data_dir / "profiles.json").read_text(encoding="utf-8"))
        stored = saved["profiles"][0]["passcode_hash"]
        assert password.is_passcode_hash(stored) and stored != PIN
        assert password.verify_passcode(PIN, stored)

    async def test_scene_routes_never_return_the_hash(self, client, data_dir):
        scene = await make_scene(client, PIN, name="Locked")
        assert scene["password_protected"] is True
        assert "passcode_hash" not in scene

        for path in ("/api/v2/scenes", f"/api/v2/scenes/{scene['id']}"):
            resp = await client.get(path)
            assert resp.status == 200
            assert_no_hash(await resp.text())

        resp = await client.put(f"/api/v2/scenes/{scene['id']}", json={"name": "Renamed", "password_protected": True})
        assert resp.status == 200
        assert_no_hash(await resp.text())

        saved = json.loads((data_dir / "scenes_v2.json").read_text(encoding="utf-8"))
        assert saved["scenes"][0]["passcode_hash"].startswith("pbkdf2_sha256$")

    async def test_scene_reports_protection_inherited_from_a_profile(self, client):
        """SEC-04: a scene running a profile that was protected later shows as protected."""
        await make_profile(client, "kids")
        scene = await make_scene(client, name="Kids", steps=[{"type": "profile", "id": "kids"}])
        assert scene["password_protected"] is False
        resp = await client.put("/api/profile/kids", json={"passcode": PIN})
        assert resp.status == 200

        listed = (await (await client.get("/api/v2/scenes")).json())["data"]["scenes"][0]
        one = (await (await client.get(f"/api/v2/scenes/{scene['id']}")).json())["data"]["scene"]
        for view in (listed, one):
            assert (view["password_protected"], view["passcode_inherited"]) == (True, True)
            assert "passcode_hash" not in view


# =============================================================================
# UI-47: protected profiles are marked in the list
# =============================================================================


class TestProfileListMarksProtection:
    async def test_list_summaries_carry_password_protected(self, client):
        await make_profile(client, "open")
        await make_profile(client, "kids", PIN)
        profiles = (await (await client.get("/api/profiles")).json())["data"]["profiles"]
        flags = {p["id"]: p["password_protected"] for p in profiles}
        assert flags == {"open": False, "kids": True}

    async def test_legacy_scene_list_carries_it_too(self, client):
        await make_profile(client, "kids", PIN)
        scenes = (await (await client.get("/api/scenes")).json())["data"]["scenes"]
        assert scenes[0]["password_protected"] is True


# =============================================================================
# F-SEC-004: stored only as hashes
# =============================================================================


class TestStoredAsHashes:
    def test_plaintext_profile_pin_on_disk_is_hashed_on_load(self, data_dir):
        from config import ProfileManager

        (data_dir / "profiles.json").write_text(
            json.dumps({"version": 2, "profiles": [
                {"id": "kids", "name": "Kids", "outputs": {}, "password_protected": True, "passcode_hash": "8642"},
            ]}),
            encoding="utf-8",
        )
        pm = ProfileManager(str(data_dir))
        stored = pm.get_profile("kids").passcode_hash
        assert stored.startswith("pbkdf2_sha256$")
        assert password.verify_passcode("8642", stored)
        on_disk = json.loads((data_dir / "profiles.json").read_text(encoding="utf-8"))
        assert on_disk["profiles"][0]["passcode_hash"] == stored

    async def test_pin_set_over_rest_is_hashed(self, client, data_dir):
        await make_profile(client, "kids")
        assert (await client.put("/api/profile/kids", json={"passcode": "97531"})).status == 200
        text = (data_dir / "profiles.json").read_text(encoding="utf-8")
        assert "97531" not in text and "pbkdf2_sha256$" in text


# =============================================================================
# F-SEC-006: setting, changing and removing a PIN
# =============================================================================


class TestProfilePinChanges:
    async def test_create_with_a_pin_protects_recall(self, client):
        created = await make_profile(client, "kids", PIN)
        assert created["password_protected"] is True
        assert await status_and_error(await client.post("/api/profile/kids/recall")) == (403, "passcode_required")
        assert (await client.post("/api/profile/kids/recall", json={"passcode": PIN})).status == 200

    @pytest.mark.parametrize(
        ("body", "message"),
        [
            ({"passcode": "12"}, "4-8 digits"),
            ({"password_protected": True}, "passcode required"),
            ({"passcode": PIN, "password_protected": False}, "Conflicting"),
        ],
    )
    async def test_create_rejects_bad_pin_fields(self, client, body, message):
        resp = await client.post("/api/profile", json={"id": "p", "name": "P", "outputs": {"1": {"input": 1}}, **body})
        assert resp.status == 400
        assert message in (await resp.json())["error"]
        assert (await client.get("/api/profile/p")).status == 404

    async def test_set_a_pin_on_an_unprotected_profile(self, client):
        await make_profile(client, "kids")
        resp = await client.put("/api/profile/kids", json={"password_protected": True, "passcode": PIN})
        assert resp.status == 200
        assert (await resp.json())["data"]["password_protected"] is True
        assert (await client.post("/api/profile/kids/recall")).status == 403

    async def test_change_needs_the_current_pin(self, client):
        await make_profile(client, "kids", PIN)
        assert await status_and_error(await client.put("/api/profile/kids", json={"passcode": OTHER_PIN})) == (
            403,
            "passcode_required",
        )
        assert await status_and_error(
            await client.put("/api/profile/kids", json={"passcode": OTHER_PIN, "current_passcode": "0000"})
        ) == (403, "invalid_passcode")
        # nothing changed
        assert (await client.post("/api/profile/kids/recall", json={"passcode": PIN})).status == 200

        resp = await client.put("/api/profile/kids", json={"passcode": OTHER_PIN, "current_passcode": PIN})
        assert resp.status == 200
        assert (await client.post("/api/profile/kids/recall", json={"passcode": PIN})).status == 403
        assert (await client.post("/api/profile/kids/recall", json={"passcode": OTHER_PIN})).status == 200

    @pytest.mark.parametrize(
        "clear",
        [{"remove_passcode": True}, {"passcode": None}, {"passcode": ""}, {"password_protected": False}],
    )
    async def test_remove_needs_the_current_pin(self, client, clear):
        await make_profile(client, "kids", PIN)
        assert (await client.put("/api/profile/kids", json=clear)).status == 403
        assert (await client.put("/api/profile/kids", json={**clear, "current_passcode": "9999"})).status == 403
        assert (await (await client.get("/api/profile/kids")).json())["data"]["password_protected"] is True

        resp = await client.put("/api/profile/kids", json={**clear, "current_passcode": PIN})
        assert resp.status == 200
        assert (await resp.json())["data"]["password_protected"] is False
        assert (await client.post("/api/profile/kids/recall")).status == 200

    async def test_current_pin_in_the_header(self, client):
        await make_profile(client, "kids", PIN)
        resp = await client.put("/api/profile/kids", json={"remove_passcode": True}, headers={"X-Passcode": PIN})
        assert resp.status == 200
        assert (await resp.json())["data"]["password_protected"] is False

    async def test_editor_save_without_pin_change_needs_no_pin(self, client):
        """The profile editor sends password_protected: true with every save."""
        await make_profile(client, "kids", PIN)
        resp = await client.put("/api/profile/kids", json={"name": "Kids room", "password_protected": True})
        assert resp.status == 200
        data = (await resp.json())["data"]
        assert (data["name"], data["password_protected"]) == ("Kids room", True)
        only_flag = await client.put("/api/profile/kids", json={"password_protected": True})
        assert only_flag.status == 200

    async def test_hash_cannot_be_mass_assigned(self, client, data_dir):
        await make_profile(client, "kids", PIN)
        before = (data_dir / "profiles.json").read_text(encoding="utf-8")
        resp = await client.put("/api/profile/kids", json={"passcode_hash": "pbkdf2_sha256$1$00$00"})
        assert resp.status == 400
        assert (data_dir / "profiles.json").read_text(encoding="utf-8") == before

    async def test_post_overwrite_keeps_the_pin(self, client):
        """SEC-05: POST /api/profile over a protected profile used to drop its protection."""
        await make_profile(client, "kids", PIN)
        resp = await client.post("/api/profile", json={"id": "kids", "name": "Kids", "outputs": {"1": {"input": 3}}})
        assert resp.status == 200
        assert (await resp.json())["data"]["password_protected"] is True
        assert (await client.post("/api/profile/kids/recall")).status == 403

    async def test_post_overwrite_cannot_clear_or_change_without_the_pin(self, client):
        await make_profile(client, "kids", PIN)
        body = {"id": "kids", "name": "Kids", "outputs": {"1": {"input": 3}}}
        assert (await client.post("/api/profile", json={**body, "password_protected": False})).status == 403
        assert (await client.post("/api/profile", json={**body, "passcode": OTHER_PIN})).status == 403
        resp = await client.post("/api/profile", json={**body, "passcode": OTHER_PIN, "current_passcode": PIN})
        assert resp.status == 200
        assert (await client.post("/api/profile/kids/recall", json={"passcode": OTHER_PIN})).status == 200

    @pytest.mark.parametrize("route", ["/api/profile/kids", "/api/scene/kids"])
    async def test_delete_needs_the_pin(self, client, route):
        await make_profile(client, "kids", PIN)
        assert await status_and_error(await client.delete(route)) == (403, "passcode_required")
        assert await status_and_error(await client.delete(route, json={"passcode": "0000"})) == (
            403,
            "invalid_passcode",
        )
        assert (await client.get("/api/profile/kids")).status == 200
        assert (await client.delete(route, json={"passcode": PIN})).status == 200
        assert (await client.get("/api/profile/kids")).status == 404

    @pytest.mark.parametrize(
        "how", [{"json": {"current_passcode": PIN}}, {"headers": {"X-Passcode": PIN}}]
    )
    async def test_delete_accepts_current_passcode_or_header(self, client, how):
        await make_profile(client, "kids", PIN)
        assert (await client.delete("/api/profile/kids", **how)).status == 200

    async def test_unprotected_profile_delete_needs_nothing(self, client):
        await make_profile(client, "open")
        assert (await client.delete("/api/profile/open")).status == 200


class TestScenePinChanges:
    async def test_change_needs_the_current_pin(self, client):
        scene = await make_scene(client, PIN)
        url = f"/api/v2/scenes/{scene['id']}"
        change = {"password_protected": True, "passcode": OTHER_PIN}
        assert await status_and_error(await client.put(url, json=change)) == (403, "passcode_required")
        assert (await client.put(url, json={**change, "current_passcode": "0000"})).status == 403
        resp = await client.put(url, json={**change, "current_passcode": PIN})
        assert resp.status == 200, await resp.text()
        assert (await client.post(f"{url}/execute", json={"passcode": OTHER_PIN})).status == 200
        assert (await client.post(f"{url}/execute", json={"passcode": PIN})).status == 403

    @pytest.mark.parametrize(
        "clear",
        [{"remove_passcode": True}, {"passcode": ""}, {"passcode": None}, {"password_protected": False}],
    )
    async def test_remove_needs_the_current_pin(self, client, clear):
        scene = await make_scene(client, PIN)
        url = f"/api/v2/scenes/{scene['id']}"
        assert (await client.put(url, json=clear)).status == 403
        assert (await (await client.get(url)).json())["data"]["scene"]["password_protected"] is True
        resp = await client.put(url, json={**clear, "current_passcode": PIN})
        assert resp.status == 200, await resp.text()
        assert (await resp.json())["data"]["scene"]["password_protected"] is False
        assert (await client.post(f"{url}/execute")).status == 200

    async def test_editor_save_without_pin_change_needs_no_pin(self, client):
        scene = await make_scene(client, PIN)
        resp = await client.put(
            f"/api/v2/scenes/{scene['id']}", json={"name": "Renamed", "password_protected": True, "steps": []}
        )
        assert resp.status == 200
        assert (await resp.json())["data"]["scene"]["password_protected"] is True

    async def test_set_a_pin_on_an_unprotected_scene(self, client):
        scene = await make_scene(client)
        url = f"/api/v2/scenes/{scene['id']}"
        resp = await client.put(url, json={"password_protected": True, "passcode": PIN})
        assert resp.status == 200
        assert (await client.post(f"{url}/execute")).status == 403

    async def test_own_pin_on_an_inherited_scene_needs_the_profile_pin(self, client):
        """Otherwise anyone could wrap a protected profile's scene in a PIN of their own."""
        await make_profile(client, "kids")
        scene = await make_scene(client, name="Kids", steps=[{"type": "profile", "id": "kids"}])
        await client.put("/api/profile/kids", json={"passcode": PIN})
        url = f"/api/v2/scenes/{scene['id']}"
        own = {"password_protected": True, "passcode": OTHER_PIN}
        assert (await client.put(url, json=own)).status == 403
        resp = await client.put(url, json={**own, "current_passcode": PIN})
        assert resp.status == 200

    async def test_removing_own_pin_still_honours_inheritance(self, client):
        await make_profile(client, "kids", PIN)
        scene = await make_scene(client, OTHER_PIN, name="Kids", steps=[{"type": "profile", "id": "kids"}])
        resp = await client.put(
            f"/api/v2/scenes/{scene['id']}", json={"remove_passcode": True, "current_passcode": OTHER_PIN}
        )
        assert resp.status == 400
        assert "password-protected" in (await resp.json())["error"]

    async def test_create_rejects_bad_pin_fields(self, client):
        resp = await client.post("/api/v2/scenes", json={"name": "S", "password_protected": True, "passcode": "12"})
        assert resp.status == 400
        assert "4-8 digits" in (await resp.json())["error"]

    @pytest.mark.parametrize(
        "how",
        [{"json": {"passcode": PIN}}, {"json": {"current_passcode": PIN}}, {"headers": {"X-Passcode": PIN}}],
    )
    async def test_delete_needs_the_pin(self, client, how):
        scene = await make_scene(client, PIN)
        url = f"/api/v2/scenes/{scene['id']}"
        assert await status_and_error(await client.delete(url)) == (403, "passcode_required")
        assert (await client.delete(url, json={"passcode": "0000"})).status == 403
        assert (await client.get(url)).status == 200
        assert (await client.delete(url, **how)).status == 200
        assert (await client.get(url)).status == 404

    async def test_delete_of_an_inherited_scene_needs_the_profile_pin(self, client):
        await make_profile(client, "kids")
        scene = await make_scene(client, name="Kids", steps=[{"type": "profile", "id": "kids"}])
        await client.put("/api/profile/kids", json={"passcode": PIN})
        url = f"/api/v2/scenes/{scene['id']}"
        assert (await client.delete(url)).status == 403
        assert (await client.delete(url, json={"passcode": PIN})).status == 200

    async def test_unprotected_scene_delete_needs_nothing(self, client):
        scene = await make_scene(client)
        assert (await client.delete(f"/api/v2/scenes/{scene['id']}")).status == 200


class TestInheritedPinOnExecute:
    async def test_scene_running_a_later_protected_profile_needs_its_pin(self, client, matrix):
        """SEC-04: profiles_map was never passed, so an inherited PIN was ignored."""
        await make_profile(client, "kids")
        scene = await make_scene(client, name="Kids", steps=[{"type": "profile", "id": "kids"}])
        await client.put("/api/profile/kids", json={"passcode": PIN})
        url = f"/api/v2/scenes/{scene['id']}/execute"
        matrix.switch.reset_mock()

        assert await status_and_error(await client.post(url)) == (403, "passcode_required")
        assert await status_and_error(await client.post(url, json={"passcode": "0000"})) == (403, "invalid_passcode")
        matrix.switch.assert_not_called()

        resp = await client.post(url, json={"passcode": PIN})
        assert resp.status == 200, await resp.text()


# =============================================================================
# F-SEC-007: wrong PINs are limited and do not stall the hub
# =============================================================================


class TestLockout:
    async def test_profile_recall_locks_out_after_five_wrong_pins(self, client, clock):
        await make_profile(client, "kids", PIN)
        url = "/api/profile/kids/recall"
        for _ in range(MAX_PIN_FAILURES):
            assert await status_and_error(await client.post(url, json={"passcode": "0000"})) == (
                403,
                "invalid_passcode",
            )
        # Even the right PIN is refused while locked out, without being checked
        resp = await client.post(url, json={"passcode": PIN})
        assert resp.status == 429
        body = await resp.json()
        assert body["data"]["error"] == "passcode_locked"
        assert body["data"]["retry_after"] == 30
        assert resp.headers["Retry-After"] == "30"
        # No passcode at all: still told it is locked
        assert (await client.post(url)).status == 429

        clock.now += 30
        assert (await client.post(url, json={"passcode": PIN})).status == 200
        # Success reset the count: four more wrong PINs are free again
        for _ in range(MAX_PIN_FAILURES - 1):
            assert (await client.post(url, json={"passcode": "0000"})).status == 403
        assert (await client.post(url, json={"passcode": PIN})).status == 200

    async def test_lockout_grows_after_the_first(self, client, clock):
        await make_profile(client, "kids", PIN)
        url = "/api/profile/kids/recall"
        for _ in range(MAX_PIN_FAILURES):
            await client.post(url, json={"passcode": "0000"})
        clock.now += 30
        assert (await client.post(url, json={"passcode": "0000"})).status == 403
        resp = await client.post(url, json={"passcode": PIN})
        assert resp.status == 429
        assert (await resp.json())["data"]["retry_after"] == 120

    async def test_malformed_pins_count_as_wrong(self, client):
        await make_profile(client, "kids", PIN)
        for bad in ("abc", "12", 1234, "123456789"):
            assert (await client.post("/api/profile/kids/recall", json={"passcode": bad})).status == 403
        assert (await client.post("/api/profile/kids/recall", json={"passcode": "0000"})).status == 403
        assert (await client.post("/api/profile/kids/recall", json={"passcode": PIN})).status == 429

    async def test_lockout_is_per_item(self, client):
        await make_profile(client, "kids", PIN)
        await make_profile(client, "teens", PIN)
        for _ in range(MAX_PIN_FAILURES):
            await client.post("/api/profile/kids/recall", json={"passcode": "0000"})
        assert (await client.post("/api/profile/kids/recall", json={"passcode": PIN})).status == 429
        assert (await client.post("/api/profile/teens/recall", json={"passcode": PIN})).status == 200

    async def test_wrong_current_pins_on_update_and_delete_share_the_limit(self, client):
        await make_profile(client, "kids", PIN)
        for _ in range(2):
            await client.put("/api/profile/kids", json={"remove_passcode": True, "current_passcode": "0000"})
        for _ in range(2):
            await client.delete("/api/profile/kids", json={"passcode": "0000"})
        await client.post("/api/profile/kids/recall", json={"passcode": "0000"})
        resp = await client.put("/api/profile/kids", json={"remove_passcode": True, "current_passcode": PIN})
        assert resp.status == 429
        assert (await client.delete("/api/profile/kids", json={"passcode": PIN})).status == 429

    async def test_scene_execute_locks_out(self, client, clock):
        scene = await make_scene(client, PIN)
        url = f"/api/v2/scenes/{scene['id']}/execute"
        for _ in range(MAX_PIN_FAILURES):
            assert (await client.post(url, json={"passcode": "0000"})).status == 403
        resp = await client.post(url, json={"passcode": PIN})
        assert resp.status == 429
        body = await resp.json()
        assert (body["data"]["error"], body["data"]["requires_scene_passcode"]) == ("passcode_locked", True)
        assert resp.headers["Retry-After"] == "30"
        assert (await client.put(f"/api/v2/scenes/{scene['id']}", json={"remove_passcode": True,
                                                                       "current_passcode": PIN})).status == 429
        assert (await client.delete(f"/api/v2/scenes/{scene['id']}", json={"passcode": PIN})).status == 429
        clock.now += 30
        assert (await client.post(url, json={"passcode": PIN})).status == 200

    async def test_deleting_an_item_forgets_its_lockout(self, client):
        scene = await make_scene(client, PIN)
        for _ in range(MAX_PIN_FAILURES - 1):
            await client.post(f"/api/v2/scenes/{scene['id']}/execute", json={"passcode": "0000"})
        assert get_pin_tracker().failures(f"scene:{scene['id']}") == MAX_PIN_FAILURES - 1
        assert (await client.delete(f"/api/v2/scenes/{scene['id']}", json={"passcode": PIN})).status == 200
        assert get_pin_tracker().failures(f"scene:{scene['id']}") == 0

    async def test_parallel_wrong_pins_cannot_outrun_the_limiter(self, client):
        await make_profile(client, "kids", PIN)
        responses = await asyncio.gather(
            *(client.post("/api/profile/kids/recall", json={"passcode": "0000"}) for _ in range(30))
        )
        statuses = [r.status for r in responses]
        assert set(statuses) <= {403, 429}
        assert statuses.count(403) <= MAX_PIN_FAILURES
        assert get_pin_tracker().failures("profile:kids") <= MAX_PIN_FAILURES


class TestPbkdf2OffTheEventLoop:
    @pytest.fixture
    def pbkdf2_threads(self, monkeypatch) -> list[threading.Thread]:
        threads: list[threading.Thread] = []
        real_verify, real_hash = password.verify_passcode, password.hash_passcode

        def spy_verify(*args):
            threads.append(threading.current_thread())
            return real_verify(*args)

        def spy_hash(*args):
            threads.append(threading.current_thread())
            return real_hash(*args)

        monkeypatch.setattr(password, "verify_passcode", spy_verify)
        monkeypatch.setattr(password, "hash_passcode", spy_hash)
        return threads

    async def test_every_rest_pin_operation_hashes_in_a_thread(self, client, pbkdf2_threads):
        await make_profile(client, "kids", PIN)
        await client.post("/api/profile/kids/recall", json={"passcode": "0000"})
        await client.post("/api/profile/kids/recall", json={"passcode": PIN})
        await client.put("/api/profile/kids", json={"passcode": OTHER_PIN, "current_passcode": PIN})
        scene = await make_scene(client, PIN)
        url = f"/api/v2/scenes/{scene['id']}"
        await client.post(f"{url}/execute", json={"passcode": "0000"})
        await client.post(f"{url}/execute", json={"passcode": PIN})
        await client.put(url, json={"passcode": OTHER_PIN, "current_passcode": PIN})
        await client.delete(url, json={"passcode": OTHER_PIN})

        # 4 hashes (profile create/change, scene create/change) + 7 verifications
        assert len(pbkdf2_threads) == 11
        assert threading.main_thread() not in pbkdf2_threads

    async def test_hub_answers_during_a_wrong_pin_burst(self, client, monkeypatch):
        """Slow PBKDF2 for many items at once; /api/health still answers promptly."""
        for i in range(4):
            await make_profile(client, f"p{i}", PIN)
        monkeypatch.setattr(password, "verify_passcode", _slow(password.verify_passcode, 0.4))

        burst = [
            asyncio.create_task(client.post(f"/api/profile/p{i}/recall", json={"passcode": "0000"})) for i in range(4)
        ]
        await asyncio.sleep(0.05)
        loop = asyncio.get_running_loop()
        started = loop.time()
        health = await client.get("/api/health")
        elapsed = loop.time() - started
        results = await asyncio.gather(*burst)

        assert health.status == 200
        assert [r.status for r in results] == [403] * 4
        assert elapsed < 0.3, elapsed


def _slow(fn, seconds: float):
    """Wrap a blocking function so it blocks its thread for ``seconds`` first."""
    import time

    def wrapper(*args):
        time.sleep(seconds)
        return fn(*args)

    return wrapper
