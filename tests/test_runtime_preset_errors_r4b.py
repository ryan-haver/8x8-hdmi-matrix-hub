"""R4B tests for preset recall exception reference vs False refusal across runtime and standalone surfaces."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

import run
from hub.domain.action_runner import ActionRunner
from hub.runtime.actions import run_action_envelope
from hub.runtime.composition import build_runtime
from orei_matrix import OreiMatrix
from password import reset_pin_lockout
from rest_api.app import create_rest_app
from rest_api.utils import set_matrix_device
from tools.simulator import DeviceState, Simulator

SECRET = r"boom at C:\secret\matrix.cfg host 10.9.8.7"
REF_PATTERN = re.compile(r"^Internal server error \(ref: ([0-9a-f]{8})\)$")


def _assert_no_secret(value: object) -> None:
    text = value if isinstance(value, str) else repr(value)
    assert "boom" not in text
    assert "secret" not in text
    assert "10.9.8.7" not in text
    assert "RuntimeError" not in text


@pytest.fixture
async def preset_runtime(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, aiohttp_client):
    import persistence
    import rest_api.utils as utils

    monkeypatch.setattr(utils, "_runtime", None)
    monkeypatch.setattr(persistence, "get_legacy_data_paths", lambda: [])
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    reset_pin_lockout()
    sim = Simulator(
        DeviceState.default(),
        host="127.0.0.1",
        https_port=0,
        telnet_port=0,
        control_port=0,
        reboot_seconds=0.3,
    )
    await sim.start()
    env = {
        "DATA_DIR": str(tmp_path / "data"),
        "UC_CONFIG_HOME": str(tmp_path / "config"),
        "MATRIX_HOST": "127.0.0.1",
        "MATRIX_PORT": str(sim.https_port),
        "FLIC_ENABLED": "false",
        "UC_ENABLED": "false",
        "HA_DISCOVERY_ENABLED": "false",
    }
    monkeypatch.setenv("MATRIX_DATA_DIR", env["DATA_DIR"])
    monkeypatch.setenv("UC_CONFIG_HOME", env["UC_CONFIG_HOME"])

    def factory(host: str, **_kwargs):
        matrix = OreiMatrix(host, port=sim.https_port, use_https=sim.tls)
        monkeypatch.setattr(matrix, "_connect_telnet", AsyncMock(return_value=False))
        return matrix

    runtime = build_runtime(run.load_settings(env), environ=env, matrix_factory=factory)
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


async def test_runtime_preset_client_exception_preserves_safe_reference_and_hides_secret(
    preset_runtime, monkeypatch, caplog
):
    runtime, client, _ = preset_runtime
    manual_ws = AsyncMock()
    monkeypatch.setattr("rest_api.control.broadcast_status_update", manual_ws)
    monkeypatch.setattr(
        runtime.service.client,
        "recall_preset",
        AsyncMock(side_effect=RuntimeError(SECRET)),
    )
    events = []
    unsubscribe = runtime.bus.subscribe(events.append)
    try:
        with caplog.at_level(logging.ERROR):
            resp = await client.post("/api/preset/1")

        assert resp.status == 500
        raw = await resp.text()
        _assert_no_secret(raw)
        payload = json.loads(raw)
        assert payload["success"] is False
        assert payload["data"] is None
        match = REF_PATTERN.match(payload["error"] or "")
        assert match is not None, payload
        ref = match.group(1)
        assert any(ref in rec.getMessage() and SECRET in rec.getMessage() for rec in caplog.records)
        manual_ws.assert_not_awaited()
        await runtime.bus.drain(timeout=1)
        assert not [e for e in events if e.topic == "presets"]

        # Shared ActionRunner, HubClientLocal, and run_action_envelope also expose only the safe ref.
        caplog.clear()
        with caplog.at_level(logging.ERROR):
            run_res = await runtime.action_runner.run("preset", "1")
        assert run_res.success is False
        assert run_res.status_code == 500
        assert run_res.code == "execution_error"
        run_match = REF_PATTERN.match(run_res.error or "")
        assert run_match is not None
        assert run_res.data["error_id"] == run_match.group(1)
        _assert_no_secret(run_res)
        _assert_no_secret(run_res.to_response_dict())

        local_env = await runtime.local.run_action("preset", "1")
        assert local_env["success"] is False
        assert local_env["data"]["status_code"] == 500
        assert local_env["data"]["result"]["code"] == "execution_error"
        assert REF_PATTERN.match(local_env["error"] or "")
        _assert_no_secret(local_env)

        helper_env = await run_action_envelope(runtime, "preset", "1")
        assert helper_env["success"] is False
        assert REF_PATTERN.match(helper_env["error"] or "")
        _assert_no_secret(helper_env)

        assert await runtime.local.recall_preset(1) is False

        # Public health, status, and runtime/service snapshots must not carry the secret exception.
        _assert_no_secret(runtime.service.last_error)
        _assert_no_secret(runtime.service.snapshot())
        _assert_no_secret(runtime.snapshot())
        health_resp = await client.get("/api/health")
        assert health_resp.status == 200
        _assert_no_secret(await health_resp.text())
        status_resp = await client.get("/api/status")
        assert status_resp.status == 200
        _assert_no_secret(await status_resp.text())
    finally:
        unsubscribe()


async def test_runtime_preset_false_refusal_keeps_exact_family_body_and_recovers(
    preset_runtime, monkeypatch
):
    runtime, client, sim = preset_runtime
    manual_ws = AsyncMock()
    monkeypatch.setattr("rest_api.control.broadcast_status_update", manual_ws)
    real_recall = runtime.service.client.recall_preset
    monkeypatch.setattr(runtime.service.client, "recall_preset", AsyncMock(return_value=False))

    resp = await client.post("/api/preset/2")
    assert resp.status == 500
    assert await resp.json() == {
        "success": False,
        "data": None,
        "error": "Failed to recall preset 2",
    }
    manual_ws.assert_awaited_once_with("preset_recall_failed", {"preset": 2})

    run_res = await runtime.action_runner.run("preset", "2")
    assert run_res.success is False
    assert run_res.status_code == 500
    assert run_res.code is None
    assert run_res.error == "Failed to recall preset 2"
    assert run_res.errors == ["Failed to recall preset 2"]
    assert run_res.data == {"preset": 2, "name": "Preset 2"}

    local_env = await runtime.local.run_action("preset", "2")
    assert local_env["success"] is False
    assert local_env["error"] == "Failed to recall preset 2"
    assert local_env["data"]["result"] == {"preset": 2, "name": "Preset 2"}
    assert await runtime.local.recall_preset(2) is False

    # Restore real recaller and confirm normal preset activation still works.
    monkeypatch.setattr(runtime.service.client, "recall_preset", real_recall)
    sim.log.clear()
    ok_resp = await client.post("/api/preset/2")
    assert ok_resp.status == 200
    assert await ok_resp.json() == {
        "success": True,
        "data": {
            "preset": 2,
            "name": "Preset 2",
            "message": "Preset 2 activated",
        },
        "error": None,
    }


async def test_standalone_preset_exception_and_false_refusal_are_distinguished(
    aiohttp_client, tmp_path, monkeypatch, caplog
):
    import persistence

    monkeypatch.setattr(persistence, "get_legacy_data_paths", lambda: [])
    monkeypatch.setenv("MATRIX_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("UC_CONFIG_HOME", str(tmp_path / "config"))

    matrix = MagicMock()
    matrix.connected = True
    matrix.host = "192.0.2.10"
    matrix.port = 443
    set_matrix_device(
        matrix,
        config_file=tmp_path / "config" / "config.json",
        config_dir=str(tmp_path / "config"),
    )
    client = await aiohttp_client(create_rest_app(data_dir=tmp_path / "data"))
    try:
        # 1. Exception -> opaque correlation reference + server log with ref and secret
        matrix.recall_preset = AsyncMock(side_effect=RuntimeError(SECRET))
        with caplog.at_level(logging.ERROR):
            exc_resp = await client.post("/api/preset/1")
        assert exc_resp.status == 500
        exc_text = await exc_resp.text()
        _assert_no_secret(exc_text)
        exc_payload = json.loads(exc_text)
        match = REF_PATTERN.match(exc_payload["error"] or "")
        assert match is not None
        ref = match.group(1)
        assert any(ref in rec.getMessage() and SECRET in rec.getMessage() for rec in caplog.records)

        direct_res = await ActionRunner.from_runtime(matrix).run("preset", "1")
        assert direct_res.code == "execution_error"
        assert REF_PATTERN.match(direct_res.error or "")
        _assert_no_secret(direct_res.to_response_dict())

        # 2. Ordinary False refusal -> exact family body
        matrix.recall_preset = AsyncMock(return_value=False)
        refusal_resp = await client.post("/api/preset/1")
        assert refusal_resp.status == 500
        assert await refusal_resp.json() == {
            "success": False,
            "data": None,
            "error": "Failed to recall preset 1",
        }
    finally:
        await client.close()
        set_matrix_device(None)
