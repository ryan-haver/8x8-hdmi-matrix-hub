"""R8-01: independent profile and unified-scene catalogs survive real restarts."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import aiohttp
import pytest

from config import Scene as LegacyScene
from config import SceneOutput
from hub.persistence import MigrationError, prepare_runtime_storage, reset_preparation
from hub.persistence.migrations import save_versioned_json
from hub.runtime.managers import create_managers
from scene_manager import SceneManager, SceneStep
from tools.simulator import DeviceState, Simulator
from tools.validate.stack import free_port

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def isolated_storage(monkeypatch):
    import hub.persistence.startup as startup

    assert Path(startup.__file__).resolve().is_relative_to(ROOT / "src")
    monkeypatch.setattr("persistence.get_legacy_data_paths", lambda: [])
    reset_preparation()
    yield
    reset_preparation()


def seed_legacy(data):
    data.mkdir(parents=True, exist_ok=True)
    record = LegacyScene("legacy", "Legacy route", {1: SceneOutput(input=3)}).to_dict()
    record["private_record"] = {"owner": "synthetic"}
    record["outputs"]["1"]["private_output"] = [1, 2]
    source = data / "scenes.json"
    # Deliberate noncanonical whitespace: a separate config copy has new bytes.
    source.write_text(json.dumps({"scenes": [record], "private_top": 17}, indent=3) + "\n", encoding="utf-8")
    return source


def snapshot(root):
    return {p.relative_to(root): (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}


@pytest.mark.parametrize("separate_config", [False, True])
def test_import_create_edit_and_repeated_fresh_preparation(tmp_path, separate_config):
    data = tmp_path / "data"
    config = tmp_path / "config" if separate_config else data
    source = seed_legacy(data)
    original = source.read_bytes()
    managers = create_managers(prepare_runtime_storage(config_dir=config, data_dir=data))
    assert managers.profiles.get_profile("legacy").outputs[1].input == 3
    assert not (data / "scenes_v2.json").exists()
    profile_path = config / "profiles.json"
    imported = json.loads(profile_path.read_text(encoding="utf-8"))
    assert imported["_runtime_imports"]["scenes.json"] == hashlib.sha256((config / "scenes.json").read_bytes()).hexdigest()
    if separate_config:
        assert (config / "scenes.json").read_bytes() != original
    scene, error = managers.scenes.create_scene("New scene", steps=[SceneStep("wait", "", {"seconds": 0.5})])
    assert error is None and scene is not None
    scene_id = scene.id
    # Exercise real disk encoders preserving private fields across later edits.
    canonical = data / "scenes_v2.json"
    stored = json.loads(canonical.read_text(encoding="utf-8"))
    stored["private_v2_top"] = {"keep": True}
    stored["scenes"][0]["private_v2_record"] = 29
    assert save_versioned_json(canonical, stored)
    assert managers.profiles.update_profile("legacy", name="Edited profile", outputs={1: {"input": 6}})
    for cycle in range(3):
        reset_preparation()
        managers = create_managers(prepare_runtime_storage(config_dir=config, data_dir=data))
        assert managers.profiles.get_profile("legacy").name == "Edited profile"
        assert managers.profiles.get_profile("legacy").outputs[1].input == 6
        assert managers.scenes.get_scene(scene_id).name == ("New scene" if cycle == 0 else "Edited scene")
        assert SceneManager(data).get_scene(scene_id) is not None
        if cycle == 0:
            updated, error = managers.scenes.update_scene(scene_id, name="Edited scene")
            assert error is None and updated is not None
        before = snapshot(tmp_path)
        create_managers(prepare_runtime_storage(config_dir=config, data_dir=data))
        assert snapshot(tmp_path) == before
    profiles = json.loads(profile_path.read_text(encoding="utf-8"))
    assert profiles["_runtime_imports"] == imported["_runtime_imports"]
    assert profiles["private_top"] == 17
    assert profiles["profiles"][0]["private_record"] == {"owner": "synthetic"}
    assert profiles["profiles"][0]["outputs"]["1"]["private_output"] == [1, 2]
    stored = json.loads(canonical.read_text(encoding="utf-8"))
    assert stored["private_v2_top"] == {"keep": True}
    assert stored["scenes"][0]["private_v2_record"] == 29
    assert source.read_bytes() == (data / "scenes.json.v0.bak").read_bytes() == original
    assert (config / "scenes.json.v0.bak").read_bytes() == (config / "scenes.json").read_bytes()


@pytest.mark.parametrize("separate_config", [False, True])
@pytest.mark.parametrize("damage", ["missing_provenance", "bad_provenance", "wrong_digest", "missing_profiles", "changed_source", "changed_config_copy", "corrupt_profiles", "future_profiles", "corrupt_v2", "future_v2", "mixed_source"])
def test_restart_refuses_unproven_or_unsafe_coexistence(tmp_path, separate_config, damage):
    data = tmp_path / "data"
    config = tmp_path / "config" if separate_config else data
    source = seed_legacy(data)
    managers = create_managers(prepare_runtime_storage(config_dir=config, data_dir=data))
    scene, error = managers.scenes.create_scene("New scene", steps=[SceneStep("wait", "", {"seconds": 0.5})])
    assert error is None and scene is not None
    target = config / "profiles.json"
    payload = json.loads(target.read_text(encoding="utf-8"))
    if damage == "missing_provenance":
        payload.pop("_runtime_imports")
    elif damage == "bad_provenance":
        payload["_runtime_imports"] = ["scenes.json"]
    elif damage == "wrong_digest":
        payload["_runtime_imports"]["scenes.json"] = "0" * 64
    elif damage in ("changed_source", "changed_config_copy", "mixed_source"):
        target = (config / "scenes.json") if damage == "changed_config_copy" else source
        payload = json.loads(target.read_text(encoding="utf-8"))
        payload["scenes"][0]["name"] = "Unimported edit"
        if damage == "mixed_source":
            payload["scenes"].append({"id": "other", "steps": []})
    elif damage == "future_profiles":
        payload["schema_version"] = 999
    elif damage.endswith("v2"):
        target = data / "scenes_v2.json"
        payload = {"schema_version": 999, "scenes": []}
    if damage == "missing_profiles":
        target.unlink()
    else:
        target.write_text("{broken" if damage.startswith("corrupt") else json.dumps(payload), encoding="utf-8")
    before = snapshot(tmp_path)
    reset_preparation()
    with pytest.raises(MigrationError):
        prepare_runtime_storage(config_dir=config, data_dir=data)
    assert snapshot(tmp_path) == before
    with pytest.raises(MigrationError):
        save_versioned_json(data / "scenes_v2.json", {"scenes": []})
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("separate_config", [False, True])
def test_unimported_legacy_and_existing_v2_remain_a_conflict(tmp_path, separate_config):
    data = tmp_path / "data"
    config = tmp_path / "config" if separate_config else data
    seed_legacy(data)
    (data / "scenes_v2.json").write_text(json.dumps({"scenes": [{"id": "other", "steps": []}]}), encoding="utf-8")
    before = snapshot(tmp_path)
    with pytest.raises(MigrationError, match="conflicting"):
        prepare_runtime_storage(config_dir=config, data_dir=data)
    assert snapshot(tmp_path) == before


def test_prepared_other_installation_cannot_supply_profile_provenance(tmp_path):
    first = tmp_path / "first"
    source = seed_legacy(first)
    create_managers(prepare_runtime_storage(config_dir=first, data_dir=first))
    second = tmp_path / "second"
    second.mkdir()
    (second / "scenes.json").write_bytes(source.read_bytes())
    (second / "scenes_v2.json").write_text('{"scenes": []}', encoding="utf-8")
    before = snapshot(tmp_path)
    with pytest.raises(MigrationError):
        SceneManager(second)
    assert snapshot(tmp_path) == before


def test_two_prepared_split_installations_keep_their_own_profile_paths(tmp_path):
    config, data = tmp_path / "first-config", tmp_path / "first-data"
    seed_legacy(data)
    first = create_managers(prepare_runtime_storage(config_dir=config, data_dir=data))
    scene, error = first.scenes.create_scene("First", steps=[SceneStep("wait", "", {"seconds": 0.5})])
    assert error is None and scene is not None
    other = tmp_path / "other"
    create_managers(prepare_runtime_storage(config_dir=other / "config", data_dir=other / "data"))
    before = snapshot(other)
    reloaded = SceneManager(data)
    updated, error = reloaded.update_scene(scene.id, name="First edited")
    assert error is None and updated.name == "First edited"
    assert snapshot(other) == before


@pytest.mark.parametrize("separate_config", [False, True])
def test_profile_pin_rehash_and_deletion_remain_authoritative(tmp_path, separate_config, monkeypatch):
    from password import verify_passcode

    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    data = tmp_path / "data"
    config = tmp_path / "config" if separate_config else data
    source = seed_legacy(data)
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["scenes"][0].update(password_protected=True, passcode_hash="1234")
    source.write_text(json.dumps(payload), encoding="utf-8")
    original = source.read_bytes()
    managers = create_managers(prepare_runtime_storage(config_dir=config, data_dir=data))
    profile = managers.profiles.get_profile("legacy")
    assert profile.passcode_hash != "1234" and verify_passcode("1234", profile.passcode_hash)
    scene, error = managers.scenes.create_scene("Independent", steps=[SceneStep("wait", "", {"seconds": 0.5})])
    assert error is None and scene is not None
    reset_preparation()
    managers = create_managers(prepare_runtime_storage(config_dir=config, data_dir=data))
    assert verify_passcode("1234", managers.profiles.get_profile("legacy").passcode_hash)
    assert managers.profiles.delete_profile("legacy")
    reset_preparation()
    managers = create_managers(prepare_runtime_storage(config_dir=config, data_dir=data))
    assert managers.profiles.get_profile("legacy") is None
    assert managers.scenes.get_scene(scene.id) is not None
    assert source.read_bytes() == (data / "scenes.json.v0.bak").read_bytes() == original


@asynccontextmanager
async def normal_process(env, logfile):
    with logfile.open("wb") as output:
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(ROOT / "run.py"), cwd=ROOT, env=env, stdout=output, stderr=asyncio.subprocess.STDOUT
        )
        try:
            yield process
        finally:
            if process.returncode is None:
                process.terminate()
            await asyncio.wait_for(process.wait(), 10)


async def connected(session, url, process, logfile):
    deadline = asyncio.get_running_loop().time() + 15
    while asyncio.get_running_loop().time() < deadline:
        assert process.returncode is None, logfile.read_text(encoding="utf-8", errors="replace")
        try:
            async with session.get(url + "/api/health", timeout=aiohttp.ClientTimeout(total=1)) as response:
                body = await response.json()
                if response.status == 200 and body["data"]["matrix"]["connected"]:
                    return
        except (aiohttp.ClientError, TimeoutError):
            pass
        await asyncio.sleep(0.05)
    pytest.fail(logfile.read_text(encoding="utf-8", errors="replace"))


@pytest.mark.parametrize("separate_config", [False, True])
@pytest.mark.parametrize("uc", [False, True])
async def test_normal_process_http_create_restart_and_execute(tmp_path, separate_config, uc):
    data = tmp_path / "data"
    config = tmp_path / "config" if separate_config else data
    source = seed_legacy(data)
    original = source.read_bytes()
    async with Simulator(DeviceState.default(), https_port=0, telnet_port=0, control_port=0) as sim:
        api_port = free_port()
        env = dict(os.environ)
        for key in ("OREI_USER", "OREI_PASSWORD", "OREI_VERIFY_SSL", "OREI_TLS_CA", "OREI_TLS_FINGERPRINT"):
            env.pop(key, None)
        env.update({
            "DATA_DIR": str(data), "MATRIX_DATA_DIR": str(data), "UC_CONFIG_HOME": str(config),
            "MATRIX_HOST": "127.0.0.1", "MATRIX_PORT": str(sim.https_port),
            "OREI_TELNET_PORT": str(sim.telnet_port), "API_PORT": str(api_port),
            "UC_ENABLED": str(uc).lower(), "UC_INTEGRATION_HTTP_PORT": str(free_port()),
            "UC_DISABLE_MDNS_PUBLISH": "true", "FLIC_ENABLED": "false", "HA_DISCOVERY_ENABLED": "false",
            "STATUS_POLL_INTERVAL": "0.2", "PYTHONPATH": os.pathsep.join((str(ROOT / "src"), str(ROOT))),
        })
        url = f"http://127.0.0.1:{api_port}"
        async with aiohttp.ClientSession() as session:
            log = tmp_path / "first-start.log"
            async with normal_process(env, log) as process:
                await connected(session, url, process, log)
                async with session.get(url + "/api/profiles") as response:
                    assert response.status == 200
                    assert "Legacy route" in await response.text()
                async with session.post(url + "/api/v2/scenes", json={
                    "name": "New scene", "steps": [{"type": "wait", "id": "", "params": {"seconds": 0.5}}]
                }) as response:
                    created = await response.json()
                    assert response.status == 201 and created["success"], created
                    scene_id = created["data"]["scene"]["id"]
            profile_bytes = (config / "profiles.json").read_bytes()
            scene_bytes = (data / "scenes_v2.json").read_bytes()
            log = tmp_path / "fresh-restart.log"
            async with normal_process(env, log) as process:
                await connected(session, url, process, log)
                assert (config / "profiles.json").read_bytes() == profile_bytes
                assert (data / "scenes_v2.json").read_bytes() == scene_bytes
                async with session.get(url + "/api/profiles") as response:
                    assert response.status == 200 and "Legacy route" in await response.text()
                async with session.get(url + "/api/v2/scenes") as response:
                    assert response.status == 200 and scene_id in await response.text()
                async with session.post(url + f"/api/v2/scenes/{scene_id}/execute") as response:
                    executed = await response.json()
                    assert response.status == 200 and executed["success"], executed
                assert process.returncode is None
            assert source.read_bytes() == (data / "scenes.json.v0.bak").read_bytes() == original
