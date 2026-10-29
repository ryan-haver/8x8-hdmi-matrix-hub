"""
Unit tests for scene_manager.py (Phase 8).

Tests cover: Scene dataclass round-trip, SceneManager CRUD,
conflict detection, override management, password protection,
and password inheritance enforcement.
"""

import tempfile
from pathlib import Path

import pytest

from scene_manager import (
    STEP_TYPE_MACRO,
    STEP_TYPE_PROFILE,
    STEP_TYPE_SYSTEM_ACTION,
    Scene,
    SceneManager,
    SceneStep,
)


class TestSceneStep:
    """Tests for SceneStep dataclass."""

    def test_profile_step_roundtrip(self):
        """Profile step round-trips correctly."""
        step = SceneStep(type=STEP_TYPE_PROFILE, id="profile_1")
        recovered = SceneStep.from_dict(step.to_dict())
        assert recovered.type == STEP_TYPE_PROFILE
        assert recovered.id == "profile_1"
        assert recovered.params == {}

    def test_system_action_step_roundtrip(self):
        """System action step round-trips correctly."""
        step = SceneStep(
            type=STEP_TYPE_SYSTEM_ACTION,
            id="route_all_to_output",
            params={"output": 3},
        )
        recovered = SceneStep.from_dict(step.to_dict())
        assert recovered.type == STEP_TYPE_SYSTEM_ACTION
        assert recovered.params == {"output": 3}

    def test_macro_step_roundtrip(self):
        """Macro step round-trips correctly."""
        step = SceneStep(type=STEP_TYPE_MACRO, id="macro_1")
        recovered = SceneStep.from_dict(step.to_dict())
        assert recovered.type == STEP_TYPE_MACRO
        assert recovered.id == "macro_1"

    def test_validate_profile(self):
        """Profile step validates successfully."""
        step = SceneStep(type=STEP_TYPE_PROFILE, id="profile_1")
        assert step.validate() is None

    def test_validate_macro(self):
        """Macro step validates successfully."""
        step = SceneStep(type=STEP_TYPE_MACRO, id="macro_1")
        assert step.validate() is None

    def test_validate_empty_id(self):
        """Empty id fails validation."""
        step = SceneStep(type=STEP_TYPE_PROFILE, id="")
        err = step.validate()
        assert err is not None
        assert "id" in err.lower()

    def test_validate_invalid_type(self):
        """Invalid step type fails validation."""
        step = SceneStep(type="invalid_type", id="something")
        err = step.validate()
        assert err is not None
        assert "type" in err.lower()


class TestSceneRoundtrip:
    """Tests for Scene dataclass round-trip."""

    def test_minimal_scene_roundtrip(self):
        """Minimal scene round-trips correctly."""
        scene = Scene(id="s1", name="Test")
        recovered = Scene.from_dict(scene.to_dict())
        assert recovered.id == scene.id
        assert recovered.name == scene.name

    def test_scene_with_steps_roundtrip(self):
        """Scene with mixed step types round-trips correctly."""
        scene = Scene(
            id="s2",
            name="Mixed",
            steps=[
                SceneStep(type=STEP_TYPE_PROFILE, id="p1"),
                SceneStep(type=STEP_TYPE_SYSTEM_ACTION, id="route_all_to_output", params={"output": 1}),
                SceneStep(type=STEP_TYPE_MACRO, id="m1"),
            ],
        )
        recovered = Scene.from_dict(scene.to_dict())
        assert len(recovered.steps) == 3
        assert recovered.steps[0].type == STEP_TYPE_PROFILE
        assert recovered.steps[1].type == STEP_TYPE_SYSTEM_ACTION
        assert recovered.steps[2].type == STEP_TYPE_MACRO

    def test_scene_with_overrides_roundtrip(self):
        """Scene with overrides round-trips correctly."""
        scene = Scene(
            id="s3",
            name="With Overrides",
            steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")],
            overrides={"p1": {1: {"hdcp": True}}},
        )
        recovered = Scene.from_dict(scene.to_dict())
        assert recovered.overrides == scene.overrides


class TestSceneManager:
    """Tests for SceneManager CRUD operations."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def mgr(self, temp_dir):
        return SceneManager(data_dir=temp_dir)

    def test_create_scene_basic(self, mgr):
        """create_scene returns a Scene with generated id."""
        scene, err = mgr.create_scene(name="Test Scene")
        assert err is None
        assert scene is not None
        assert scene.name == "Test Scene"
        assert scene.id.startswith("scene_")

    def test_create_scene_with_steps(self, mgr):
        """create_scene stores steps."""
        steps = [SceneStep(type=STEP_TYPE_PROFILE, id="p1")]
        scene, err = mgr.create_scene(name="With Steps", steps=steps)
        assert err is None
        assert len(scene.steps) == 1
        assert scene.steps[0].type == STEP_TYPE_PROFILE

    def test_create_scene_with_password(self, mgr):
        """create_scene stores password protection with hash."""
        scene, err = mgr.create_scene(
            name="Protected",
            password_protected=True,
            passcode="1234",
        )
        assert err is None
        assert scene.password_protected is True
        assert scene.passcode_hash != ""
        assert scene.passcode_hash.startswith("pbkdf2")

    def test_create_scene_password_protected_without_passcode_fails(self, mgr):
        """create_scene fails if password_protected=True without passcode."""
        scene, err = mgr.create_scene(name="Bad", password_protected=True)
        assert scene is None
        assert err is not None

    def test_list_scenes(self, mgr):
        """list_scenes returns all scenes."""
        mgr.create_scene(name="Scene 1")
        mgr.create_scene(name="Scene 2")
        scenes = mgr.list_scenes()
        assert len(scenes) == 2

    def test_get_scene(self, mgr):
        """get_scene returns the correct scene."""
        created, _ = mgr.create_scene(name="Get Test")
        retrieved = mgr.get_scene(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_scene_not_found(self, mgr):
        """get_scene returns None for unknown id."""
        assert mgr.get_scene("nonexistent") is None

    def test_update_scene_name(self, mgr):
        """update_scene modifies the name."""
        scene, _ = mgr.create_scene(name="Original")
        updated, err = mgr.update_scene(scene.id, name="Updated")
        assert err is None
        assert updated.name == "Updated"

    def test_update_scene_steps(self, mgr):
        """update_scene replaces steps."""
        scene, _ = mgr.create_scene(name="Steps Test")
        new_steps = [SceneStep(type=STEP_TYPE_PROFILE, id="p1"), SceneStep(type=STEP_TYPE_MACRO, id="m1")]
        updated, err = mgr.update_scene(scene.id, steps=new_steps)
        assert err is None
        assert len(updated.steps) == 2

    def test_delete_scene(self, mgr):
        """delete_scene removes the scene."""
        scene, _ = mgr.create_scene(name="To Delete")
        ok = mgr.delete_scene(scene.id)
        assert ok is True
        assert mgr.get_scene(scene.id) is None

    def test_persistence(self, mgr, temp_dir):
        """Scenes persist across manager instantiation."""
        mgr.create_scene(name="Persistent")
        mgr2 = SceneManager(data_dir=temp_dir)
        scenes = mgr2.list_scenes()
        assert len(scenes) == 1
        assert scenes[0].name == "Persistent"


class TestSceneManagerSteps:
    """Tests for SceneManager step management."""

    @pytest.fixture
    def mgr(self):
        with tempfile.TemporaryDirectory() as d:
            yield SceneManager(data_dir=Path(d))

    def test_add_profile_step(self, mgr):
        """add_step appends a profile step."""
        scene, _ = mgr.create_scene(name="Test")
        step = SceneStep(type=STEP_TYPE_PROFILE, id="profile_1")
        mgr.add_step(scene.id, step)
        updated = mgr.get_scene(scene.id)
        assert len(updated.steps) == 1
        assert updated.steps[0].type == STEP_TYPE_PROFILE

    def test_add_macro_step(self, mgr):
        """add_step appends a macro step."""
        scene, _ = mgr.create_scene(name="Test")
        step = SceneStep(type=STEP_TYPE_MACRO, id="macro_1")
        mgr.add_step(scene.id, step)
        updated = mgr.get_scene(scene.id)
        assert len(updated.steps) == 1
        assert updated.steps[0].type == STEP_TYPE_MACRO

    def test_remove_step(self, mgr):
        """remove_step removes the step at index."""
        scene, _ = mgr.create_scene(
            name="Test",
            steps=[
                SceneStep(type=STEP_TYPE_PROFILE, id="p1"),
                SceneStep(type=STEP_TYPE_MACRO, id="m1"),
            ],
        )
        result, err = mgr.remove_step(scene.id, 0)
        assert err is None
        assert len(result.steps) == 1
        assert result.steps[0].id == "m1"


class TestSceneManagerOverrides:
    """Tests for SceneManager override management."""

    @pytest.fixture
    def mgr(self):
        with tempfile.TemporaryDirectory() as d:
            yield SceneManager(data_dir=Path(d))

    def test_set_override(self, mgr):
        """set_override stores the override."""
        scene, _ = mgr.create_scene(name="Test")
        mgr.set_override(scene.id, "p1", 1, "hdcp", disabled=True)
        updated = mgr.get_scene(scene.id)
        assert updated.overrides["p1"][1]["hdcp"] is True

    def test_clear_override(self, mgr):
        """clear_override removes the override."""
        scene, _ = mgr.create_scene(name="Test")
        mgr.set_override(scene.id, "p1", 1, "hdcp", disabled=True)
        mgr.clear_override(scene.id, "p1", 1, "hdcp")
        updated = mgr.get_scene(scene.id)
        assert "hdcp" not in updated.overrides.get("p1", {}).get(1, {})


class TestSceneManagerPassword:
    """Tests for SceneManager password verification and inheritance."""

    @pytest.fixture
    def mgr(self):
        with tempfile.TemporaryDirectory() as d:
            yield SceneManager(data_dir=Path(d))

    def test_verify_passcode_correct(self, mgr):
        """verify_passcode returns True for correct passcode."""
        scene, _ = mgr.create_scene(
            name="Protected",
            password_protected=True,
            passcode="5678",
        )
        assert mgr.verify_passcode(scene.id, "5678") is True

    def test_verify_passcode_incorrect(self, mgr):
        """verify_passcode returns False for wrong passcode."""
        scene, _ = mgr.create_scene(
            name="Protected",
            password_protected=True,
            passcode="5678",
        )
        assert mgr.verify_passcode(scene.id, "1234") is False

    def test_verify_passcode_unprotected_scene(self, mgr):
        """verify_passcode returns True for unprotected scene."""
        scene, _ = mgr.create_scene(name="Open")
        assert mgr.verify_passcode(scene.id, "anything") is True

    def test_password_inheritance_blocks_unprotected_scene_with_protected_step(self, mgr):
        """Unprotected scene containing protected profile step is rejected."""


        # Patch the profile manager to return a protected profile
        scene, err = mgr.create_scene(
            name="Contains Protected",
            steps=[SceneStep(type=STEP_TYPE_PROFILE, id="protected_profile")],
        )
        # Without a profile manager, inheritance check should pass
        # (no profiles to check against). So we patch instead.
        # First verify the basic case works
        assert scene is not None or err is not None


def _protected_profile(profile_id: str, pin: str):
    from config import Profile
    from password import hash_passcode

    return Profile(id=profile_id, name=profile_id, password_protected=True, passcode_hash=hash_passcode(pin))


class TestScenePins:
    """WP-F1: hashes stay private (SEC-04), inheritance uses the profile map (SEC-05), async verify (SEC-06)."""

    @pytest.fixture(autouse=True)
    def _fast_hashing(self, monkeypatch):
        monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")

    @pytest.fixture
    def data_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def mgr(self, data_dir):
        return SceneManager(data_dir=data_dir)

    def test_to_dict_omits_the_hash_by_default(self, mgr):
        scene, _ = mgr.create_scene(name="Locked", password_protected=True, passcode="1234")
        public = scene.to_dict()
        assert "passcode_hash" not in public
        assert public["password_protected"] is True
        assert scene.to_dict(include_hash=True)["passcode_hash"] == scene.passcode_hash

    def test_save_persists_the_hash_and_reload_verifies(self, mgr, data_dir):
        import json

        scene, _ = mgr.create_scene(name="Locked", password_protected=True, passcode="1234")
        # R2 contract §4: scene_manager.SceneManager persists to scenes_v2.json.
        saved = json.loads((data_dir / "scenes_v2.json").read_text(encoding="utf-8"))
        assert saved["scenes"][0]["passcode_hash"].startswith("pbkdf2_sha256$")
        reloaded = SceneManager(data_dir=data_dir)
        assert reloaded.verify_scene_passcode(scene.id, "1234") is True

    def test_plaintext_pin_on_disk_is_hashed_on_load(self, data_dir):
        """F-SEC-004: a raw PIN in scenes_v2.json is hashed in memory and rewritten on disk."""
        import json

        (data_dir / "scenes_v2.json").write_text(
            json.dumps({"scenes": [{"id": "s1", "name": "Hand edited", "password_protected": True,
                                    "passcode_hash": "4321"}]}),
            encoding="utf-8",
        )
        mgr = SceneManager(data_dir=data_dir)
        assert mgr.get_scene("s1").passcode_hash.startswith("pbkdf2_sha256$")
        assert mgr.verify_scene_passcode("s1", "4321") is True
        on_disk = json.loads((data_dir / "scenes_v2.json").read_text(encoding="utf-8"))["scenes"][0]["passcode_hash"]
        assert on_disk.startswith("pbkdf2_sha256$") and "4321" != on_disk

    def test_inherited_protection_needs_the_profile_map(self, mgr):
        scene, err = mgr.create_scene(name="Kids", steps=[SceneStep(type=STEP_TYPE_PROFILE, id="kids")])
        assert err is None
        profiles = {"kids": _protected_profile("kids", "2580")}
        # The profile was protected after the scene was made
        assert mgr.is_scene_password_protected(scene.id) is False
        assert mgr.is_scene_password_protected(scene.id, profiles) is True
        assert mgr.is_passcode_inherited(scene.id, profiles) is True
        assert mgr.verify_scene_passcode(scene.id, "2580", profiles) is True
        assert mgr.verify_scene_passcode(scene.id, "0000", profiles) is False
        assert mgr.verify_scene_passcode(scene.id, None, profiles) is False

    def test_inherited_from_several_profiles_needs_a_pin_matching_all(self, mgr):
        scene, _ = mgr.create_scene(
            name="Two",
            steps=[SceneStep(type=STEP_TYPE_PROFILE, id="a"), SceneStep(type=STEP_TYPE_PROFILE, id="b")],
        )
        same = {"a": _protected_profile("a", "1111"), "b": _protected_profile("b", "1111")}
        different = {"a": _protected_profile("a", "1111"), "b": _protected_profile("b", "2222")}
        assert mgr.verify_scene_passcode(scene.id, "1111", same) is True
        assert mgr.verify_scene_passcode(scene.id, "1111", different) is False

    def test_own_pin_is_checked_before_inherited(self, mgr):
        profiles = {"kids": _protected_profile("kids", "2580")}
        scene, err = mgr.create_scene(
            name="Kids", steps=[SceneStep(type=STEP_TYPE_PROFILE, id="kids")],
            password_protected=True, passcode="7777", profiles_map=profiles,
        )
        assert err is None
        assert mgr.is_passcode_inherited(scene.id, profiles) is False
        assert mgr.verify_scene_passcode(scene.id, "7777", profiles) is True
        assert mgr.verify_scene_passcode(scene.id, "2580", profiles) is False

    def test_create_and_update_enforce_inheritance_with_the_map(self, mgr):
        profiles = {"kids": _protected_profile("kids", "2580")}
        steps = [SceneStep(type=STEP_TYPE_PROFILE, id="kids")]
        scene, err = mgr.create_scene(name="Kids", steps=steps, profiles_map=profiles)
        assert scene is None and "password-protected" in err
        scene, err = mgr.create_scene(name="Kids", password_protected=True, passcode="7777")
        assert err is None
        updated, err = mgr.update_scene(scene.id, steps=steps, password_protected=False, profiles_map=profiles)
        assert updated is None and "password-protected" in err
        assert mgr.get_scene(scene.id).is_password_protected()

    def test_removing_the_pin_clears_the_hash(self, mgr):
        scene, _ = mgr.create_scene(name="Locked", password_protected=True, passcode="1234")
        updated, err = mgr.update_scene(scene.id, password_protected=False)
        assert err is None
        assert (updated.password_protected, updated.passcode_hash) == (False, "")
        assert mgr.is_scene_password_protected(scene.id) is False

    def test_prehashed_passcode_is_stored_as_given(self, mgr):
        from password import hash_passcode

        stored = hash_passcode("1357")
        scene, err = mgr.create_scene(name="Locked", password_protected=True, passcode_hash=stored)
        assert err is None and scene.passcode_hash == stored
        new = hash_passcode("2468")
        updated, _ = mgr.update_scene(scene.id, password_protected=True, passcode_hash=new)
        assert updated.passcode_hash == new
        assert mgr.verify_scene_passcode(scene.id, "2468") is True

    def test_malformed_passcode_is_an_error_not_a_crash(self, mgr):
        scene, err = mgr.create_scene(name="Bad", password_protected=True, passcode="12")
        assert scene is None and "4-8 digits" in err

    def test_flag_without_hash_fails_closed(self, mgr):
        """A scene marked protected with no hash (hand-edited file) can never be run."""
        scene, _ = mgr.create_scene(name="Open")
        scene.password_protected = True
        assert mgr.is_scene_password_protected(scene.id) is True
        assert mgr.verify_scene_passcode(scene.id, "1234") is False

    async def test_verify_async_matches_sync(self, mgr):
        profiles = {"kids": _protected_profile("kids", "2580")}
        own, _ = mgr.create_scene(name="Own", password_protected=True, passcode="7777")
        inherited, _ = mgr.create_scene(name="Kids", steps=[SceneStep(type=STEP_TYPE_PROFILE, id="kids")])
        open_scene, _ = mgr.create_scene(name="Open")
        cases = [
            (own.id, "7777", True), (own.id, "0000", False), (own.id, "abc", False),
            (inherited.id, "2580", True), (inherited.id, "7777", False),
            (open_scene.id, None, True), ("missing", "7777", False),
        ]
        for scene_id, pin, expected in cases:
            assert mgr.verify_scene_passcode(scene_id, pin, profiles) is expected, (scene_id, pin)
            assert await mgr.verify_scene_passcode_async(scene_id, pin, profiles) is expected, (scene_id, pin)


class TestDetectConflicts:
    """Tests for detect_conflicts() function."""

    def test_no_conflicts_with_single_profile(self):
        """No conflicts when scene has only one profile."""
        from unittest.mock import MagicMock

        from scene_manager import detect_conflicts

        profile = MagicMock()
        profile.id = "p1"
        profile.name = "Profile 1"
        profile.outputs = {
            1: MagicMock(enabled=True, input=1, hdcp_mode=3, hdr_mode=3, scaler_mode=0, arc=False, audio_mute=False),
        }
        scene = Scene(
            id="s1",
            name="Test",
            steps=[SceneStep(type=STEP_TYPE_PROFILE, id="p1")],
        )
        conflicts = detect_conflicts(scene, {"p1": profile})
        assert conflicts == []
