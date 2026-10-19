"""Independent R8 reproductions; strict xfails identify unresolved release findings.

Use --runxfail to see the required behavior fail on the reviewed candidate.
The Docker case uses the normal immutable image command and mounts data only.
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import aiohttp
import pytest

from config import Scene as LegacyScene
from config import SceneOutput
from hub import cli
from hub.persistence import MigrationError, prepare_runtime_storage, reset_preparation
from hub.runtime.composition import build_runtime
from hub.runtime.managers import create_managers
from scene_manager import SceneStep
from tools.simulator import DeviceState, Simulator
from tools.validate.stack import free_port

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "sha256:1a5de3b5b58a3e1c56d3269bd5c1c6e3e12be2d6fea1abceea36067d733df69e"


class ReviewFindingError(AssertionError):
    """Only the demonstrated final invariant, never a broken setup, may xfail."""


@pytest.fixture(autouse=True)
def review_isolation(monkeypatch):
    import hub.runtime.composition as composition

    assert Path(composition.__file__).resolve().is_relative_to(ROOT / "src")
    monkeypatch.setattr("rest_api.utils._runtime", None)
    for key in ("OREI_USER", "OREI_PASSWORD", "OREI_VERIFY_SSL", "OREI_TLS_CA", "OREI_TLS_FINGERPRINT"):
        monkeypatch.delenv(key, raising=False)
    reset_preparation()
    yield
    reset_preparation()


def seed_legacy(directory):
    directory.mkdir(parents=True, exist_ok=True)
    scene = LegacyScene("legacy", "Legacy route", {1: SceneOutput(input=3)})
    path = directory / "scenes.json"
    path.write_text(json.dumps({"scenes": [scene.to_dict()]}), encoding="utf-8")
    return path, path.read_bytes()


@pytest.mark.xfail(
    strict=True, raises=ReviewFindingError, reason="R8-01: new v2 scene makes a migrated legacy installation unbootable"
)
@pytest.mark.parametrize("separate_config", [False, True])
def test_migrated_legacy_scenes_accept_new_scene_and_restart(tmp_path, separate_config):
    data = tmp_path / "data"
    config = tmp_path / "config" if separate_config else data
    legacy, original = seed_legacy(data)
    managers = create_managers(prepare_runtime_storage(config_dir=config, data_dir=data))
    assert managers.profiles.get_profile("legacy").outputs[1].input == 3
    scene, error = managers.scenes.create_scene("New scene", steps=[SceneStep("wait", "", {"seconds": 0.5})])
    assert error is None and scene is not None
    assert legacy.read_bytes() == original
    assert legacy.with_name("scenes.json.v0.bak").read_bytes() == original
    assert json.loads((data / "scenes_v2.json").read_text())["scenes"][0]["id"] == scene.id
    # A fresh process has no preparation cache. Both independently owned catalogs
    # must remain usable after an ordinary successful scene creation.
    reset_preparation()
    try:
        restarted = create_managers(prepare_runtime_storage(config_dir=config, data_dir=data))
    except MigrationError as exc:
        raise ReviewFindingError(str(exc)) from exc
    assert restarted.profiles.get_profile("legacy").outputs[1].input == 3
    assert restarted.scenes.get_scene(scene.id).name == "New scene"


@pytest.mark.xfail(
    strict=True,
    raises=ReviewFindingError,
    reason="R8-02: failed rollback login abandons the transport reconnect supervisor",
)
async def test_failed_reconfigure_recovers_after_transient_login_outage(tmp_path, monkeypatch):
    import orei_matrix

    monkeypatch.setattr(orei_matrix, "INITIAL_RETRY_DELAY", 0.02)
    monkeypatch.setattr(orei_matrix, "MAX_RETRY_DELAY", 0.04)
    async with Simulator(DeviceState.default(), https_port=0, telnet_port=0, control_port=0) as sim:
        env = {
            "DATA_DIR": str(tmp_path / "data"),
            "UC_CONFIG_HOME": str(tmp_path / "config"),
            "MATRIX_HOST": "127.0.0.1",
            "MATRIX_PORT": str(sim.https_port),
            "OREI_TELNET_PORT": str(sim.telnet_port),
            "API_PORT": str(free_port()),
            "UC_ENABLED": "false",
            "FLIC_ENABLED": "false",
            "HA_DISCOVERY_ENABLED": "false",
            "STATUS_POLL_INTERVAL": "0.2",
        }
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        settings = cli.load_settings(env)
        cli.export_env(settings, os.environ)
        runtime = build_runtime(settings, environ=env)
        try:
            await runtime.start()
            await asyncio.wait_for(runtime._connect_task, 10)
            assert runtime.snapshot().connected
            old_client, address = runtime.service.client, runtime.address
            # A real transient HTTP failure, limited to the candidate login and
            # the old client's rollback login; the simulator then heals itself.
            sim.faults.update({"http_status": 503, "comheads": ["login"], "http_fault_count": 2})
            result = await runtime.reconfigure(address)
            assert not result.success
            assert runtime.service.client is old_client and runtime.address == address
            assert not sim.faults.any_http
            assert not runtime._refresh_task.done()
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline and not runtime.snapshot().connected:
                await asyncio.sleep(0.05)
            if not runtime.snapshot().connected:
                raise ReviewFindingError(
                    "Simulator recovered, but runtime stayed disconnected; "
                    f"old client reconnect task={old_client._reconnect_task!r}"
                )
        finally:
            await runtime.stop()


async def docker(*args, check=True):
    result = await asyncio.to_thread(subprocess.run, ["docker", *args], capture_output=True, text=True, timeout=45)
    if check:
        assert result.returncode == 0, result.stderr
    output = result.stdout + (result.stderr if args[0] == "logs" else "")
    return output.strip()


async def wait_health(session, url, *, seconds=20):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            async with session.get(url + "/api/health", timeout=aiohttp.ClientTimeout(total=1)) as response:
                body = await response.json()
                if response.status == 200 and body["data"]["matrix"]["connected"]:
                    return True
        except (aiohttp.ClientError, TimeoutError):
            pass
        await asyncio.sleep(0.1)
    return False


@asynccontextmanager
async def shipped_image(tmp_path, *, legacy=False, uc=False):
    assert await docker("image", "inspect", IMAGE, "--format", "{{.Id}}") == IMAGE
    data = tmp_path / "volume"
    data.mkdir()
    if legacy:
        seed_legacy(data)
    name = "runtime-review-r8-" + uuid.uuid4().hex[:12]
    api_port = free_port()
    url = f"http://127.0.0.1:{api_port}"
    async with Simulator(DeviceState.default(), host="0.0.0.0", https_port=0, telnet_port=0, control_port=0) as sim:
        await docker(
            "run",
            "-d",
            "--name",
            name,
            "-p",
            f"127.0.0.1:{api_port}:8080",
            "--mount",
            f"type=bind,source={data},target=/data",
            "-e",
            "DATA_DIR=/data",
            "-e",
            f"UC_ENABLED={str(uc).lower()}",
            "-e",
            "FLIC_ENABLED=false",
            "-e",
            "UC_DISABLE_MDNS_PUBLISH=true",
            "-e",
            "HA_DISCOVERY_ENABLED=false",
            "-e",
            "MATRIX_HOST=host.docker.internal",
            "-e",
            f"MATRIX_PORT={sim.https_port}",
            "-e",
            f"OREI_TELNET_PORT={sim.telnet_port}",
            "-e",
            "STATUS_POLL_INTERVAL=0.2",
            IMAGE,
        )
        try:
            async with aiohttp.ClientSession() as session:
                assert await wait_health(session, url), await docker("logs", name)
                yield sim, session, url, name, data
        finally:
            await docker("stop", "--time", "15", name, check=False)
            state = await docker("inspect", name, "--format", "{{json .State}}")
            logs = await docker("logs", name)
            (tmp_path / "image-state.json").write_text(state, encoding="utf-8")
            (tmp_path / "image.log").write_text(logs, encoding="utf-8")
            await docker("rm", name)


@pytest.mark.docker
@pytest.mark.xfail(
    strict=True,
    raises=ReviewFindingError,
    reason="R8-01: normal shipped image exits on restart after successful scene creation",
)
@pytest.mark.parametrize("uc", [False, True])
async def test_shipped_image_legacy_upgrade_scene_creation_restart(tmp_path, uc):
    async with shipped_image(tmp_path, legacy=True, uc=uc) as (_, session, url, name, data):
        legacy = data / "scenes.json"
        original = legacy.read_bytes()
        async with session.get(url + "/api/profiles") as response:
            assert response.status == 200
            assert "Legacy route" in await response.text()
        async with session.post(
            url + "/api/v2/scenes",
            json={"name": "New scene", "steps": [{"type": "wait", "id": "", "params": {"seconds": 0.5}}]},
        ) as response:
            created = await response.json()
            assert response.status == 201, created
            assert created["success"]
        assert legacy.read_bytes() == original
        assert (data / "scenes_v2.json").exists()
        await docker("restart", "--time", "15", name)
        healthy = await wait_health(session, url, seconds=6)
        state = await docker("inspect", name, "--format", "{{json .State}}")
        if not healthy:
            raise ReviewFindingError(f"Normal image restart failed: {state}\n{await docker('logs', name)}")


@pytest.mark.docker
@pytest.mark.xfail(
    strict=True,
    raises=ReviewFindingError,
    reason="R8-02: shipped image does not recover after reconfigure rollback login fails",
)
async def test_shipped_image_reconfigure_recovers_after_login_outage(tmp_path):
    async with shipped_image(tmp_path) as (sim, session, url, name, _):
        sim.faults.update({"http_status": 503, "comheads": ["login"], "http_fault_count": 2})
        async with session.post(
            url + "/api/settings/matrix-host",
            json={
                "host": "host.docker.internal",
                "port": sim.https_port,
                "telnet_port": sim.telnet_port,
            },
        ) as response:
            result = await response.json()
            assert response.status == 200, result
            assert result["data"]["connected"] is False
        assert not sim.faults.any_http
        recovered = await wait_health(session, url, seconds=12)
        # An explicit connection test proves the now-healthy simulator is reachable
        # from the image. It is a manual workaround, not automatic recovery.
        async with session.post(url + "/api/settings/test-connection") as response:
            manual = await response.json()
            assert response.status == 200 and manual["data"]["connected"], manual
        assert await wait_health(session, url, seconds=2)
        if not recovered:
            raise ReviewFindingError(f"Only manual reconnect recovered the image\n{await docker('logs', name)}")
