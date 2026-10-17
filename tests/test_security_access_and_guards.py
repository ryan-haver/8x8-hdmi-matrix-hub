"""Security access levels and always-on browser request protections."""

from __future__ import annotations

import importlib.util
import json

import pytest
from aiohttp import WSServerHandshakeError

from rest_api import utils
from rest_api.app import create_rest_app
from rest_api.security import route_level


@pytest.fixture
def security_app(tmp_path, monkeypatch):
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    monkeypatch.delenv("ADMIN_PIN", raising=False)
    monkeypatch.delenv("CONTROL_PIN", raising=False)
    monkeypatch.delenv("ADMIN_PIN_RESET", raising=False)
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    return create_rest_app(tmp_path)


@pytest.fixture
async def client(aiohttp_client, security_app):
    return await aiohttp_client(security_app)


async def test_open_defaults_and_admin_pin_session_lock(client):
    status = await (await client.get("/api/auth/status")).json()
    assert status["session_level"] == "none"
    assert not status["admin_pin_set"]
    assert (await client.post("/api/settings/test-connection", json={})).status != 401
    response = await client.post("/api/auth/pin", json={"level": "admin", "pin": "1234"})
    assert response.status == 200
    assert (await client.post("/api/settings/test-connection", json={})).status == 401
    response = await client.post("/api/auth/unlock", json={"pin": "1234"})
    assert response.status == 200
    assert "HttpOnly" in response.headers["Set-Cookie"]
    assert "SameSite=Strict" in response.headers["Set-Cookie"]
    assert (await client.get("/api/auth/status")).status == 200
    assert (await (await client.get("/api/auth/status")).json())["session_level"] == "admin"
    assert (await client.post("/api/settings/test-connection", json={})).status != 401
    await client.post("/api/auth/lock")
    assert (await client.post("/api/settings/test-connection", json={})).status == 401
    assert (await client.post("/api/settings/test-connection", json={}, headers={"X-Admin-PIN": "1234"})).status != 401


async def test_control_cookie_keys_and_revocation(client):
    await client.post("/api/auth/pin", json={"level": "control", "pin": "5678"})
    assert (await client.post("/api/power/on")).status == 401
    response = await client.post("/api/auth/unlock", json={"level": "control", "pin": "5678", "remember_device": True, "device_name": "Kiosk"})
    assert response.status == 200
    assert any("orei_device_token=" in value for value in response.headers.getall("Set-Cookie"))
    assert (await client.post("/api/power/on")).status != 401
    devices = await (await client.get("/api/auth/devices")).json()
    assert devices[0]["name"] == "Kiosk"
    key_response = await client.post("/api/auth/api-keys", json={"name": "HA"})
    assert key_response.status == 201
    key = await key_response.json()
    assert (await client.post("/api/power/on", headers={"X-API-Key": key["key"]})).status != 401
    assert (await client.post(f"/api/power/on?key={key['key']}")).status != 401
    assert key["key"] not in json.dumps(await (await client.get("/api/auth/api-keys")).json())
    await client.delete(f"/api/auth/api-keys/{key['id']}")
    await client.delete(f"/api/auth/devices/{devices[0]['id']}")
    await client.post("/api/auth/lock")
    assert (await client.post("/api/power/on", headers={"X-API-Key": key["key"]})).status == 401
    assert (await client.post("/api/power/on")).status == 401


async def test_pin_lockout(client):
    await client.post("/api/auth/pin", json={"pin": "1234"})
    for _ in range(4):
        assert (await client.post("/api/auth/unlock", json={"pin": "0000"})).status == 401
    assert (await client.post("/api/auth/unlock", json={"pin": "0000"})).status == 429
    assert (await client.post("/api/auth/unlock", json={"pin": "1234"})).status == 429


async def test_pin_change_with_current_pin_and_idle_timeout(client):
    await client.post("/api/auth/pin", json={"pin": "1234"})
    assert (await client.post("/api/auth/pin", json={"pin": "4321", "current_pin": "0000"})).status == 401
    assert (await client.post("/api/auth/pin", json={"pin": "4321", "current_pin": "1234"})).status == 200
    assert (await client.post("/api/auth/unlock", json={"pin": "1234"})).status == 401
    assert (await client.post("/api/auth/unlock", json={"pin": "4321"})).status == 200
    security = client.server.app["security_manager"]
    assert security.sessions
    for token, (level, _) in list(security.sessions.items()):
        security.sessions[token] = (level, 0)
    assert (await (await client.get("/api/auth/status")).json())["session_level"] == "none"


async def test_admin_pin_reset(tmp_path, monkeypatch, aiohttp_client):
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    first = await aiohttp_client(create_rest_app(tmp_path))
    await first.post("/api/auth/pin", json={"pin": "1234"})
    assert json.loads((tmp_path / "security.json").read_text())["admin_pin"].startswith("pbkdf2_sha256$")
    monkeypatch.setenv("ADMIN_PIN_RESET", "true")
    second = await aiohttp_client(create_rest_app(tmp_path))
    assert not (await (await second.get("/api/auth/status")).json())["admin_pin_set"]


async def test_environment_pins_and_api_key(tmp_path, monkeypatch, aiohttp_client):
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    monkeypatch.setenv("ADMIN_PIN", "1234")
    monkeypatch.setenv("CONTROL_PIN", "5678")
    monkeypatch.setenv("CONTROL_API_KEY", "configured-key")
    client = await aiohttp_client(create_rest_app(tmp_path))
    status = await (await client.get("/api/auth/status")).json()
    assert status["admin_pin_set"] and status["control_pin_set"]
    assert (await client.post("/api/power/on")).status == 401
    assert (await client.post("/api/power/on", headers={"X-API-Key": "configured-key"})).status != 401
    assert (await client.post("/api/settings/test-connection", json={}, headers={"X-API-Key": "configured-key"})).status == 401
    assert (await client.post("/api/settings/test-connection", json={}, headers={"X-Admin-PIN": "1234"})).status != 401


async def test_host_origin_content_type_and_cors(client, monkeypatch):
    assert (await client.get("/api/health", headers={"Host": "evil.example.com"})).status in (403, 421)
    assert (await client.options("/api/power/on", headers={"Host": "evil.example.com"})).status in (403, 421)
    assert (await client.get("/api/health", headers={"Host": "hub.local"})).status == 200
    assert (await client.post("/api/power/on", headers={"Origin": "http://evil.example.com"})).status == 403
    assert (await client.post("/api/power/on", headers={"Referer": "http://evil.example.com/page"})).status == 403
    assert (await client.post("/api/power/on", data="hello", headers={"Content-Type": "text/plain"})).status == 415
    assert (await client.post("/api/power/on")).status != 415
    assert "Access-Control-Allow-Origin" not in (await client.get("/api/health", headers={"Origin": "http://evil.example.com"})).headers
    origin = str(client.make_url("/")).rstrip("/")
    assert (await client.get("/api/health", headers={"Origin": origin})).headers["Access-Control-Allow-Origin"] == origin
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://allowed.example")
    assert (await client.get("/api/health", headers={"Origin": "http://allowed.example"})).headers["Access-Control-Allow-Origin"] == "http://allowed.example"
    assert (await client.post("/api/power/on", headers={"Origin": "http://allowed.example"})).status != 403
    monkeypatch.setenv("ALLOWED_HOSTS", "evil.example.com")
    assert (await client.get("/api/health", headers={"Host": "evil.example.com"})).status == 200


async def test_rate_buckets_and_three_ui_bursts(client):
    utils.reset_rate_limiter()
    for _ in range(78):
        assert (await client.get("/api/status")).status != 429
    for _ in range(3):
        for _ in range(26):
            assert (await client.get("/api/inputs")).status != 429
    for _ in range(60):
        await utils._check_rate_limit("192.0.2.99")
    assert not await utils._check_rate_limit("192.0.2.99")
    assert await utils._check_rate_limit("192.0.2.99", "read")


async def test_websocket_origin_and_cap(client, monkeypatch):
    with pytest.raises(WSServerHandshakeError) as denied:
        await client.ws_connect("/ws", headers={"Origin": "http://evil.example.com"})
    assert denied.value.status == 403
    monkeypatch.setenv("MAX_WS_CLIENTS", "1")
    first = await client.ws_connect("/ws")
    assert first.closed is False
    assert next(iter(utils.get_ws_clients()))["access_level"] == "none"
    with pytest.raises(WSServerHandshakeError) as full:
        await client.ws_connect("/ws")
    assert full.value.status == 503
    await first.close()


async def test_websocket_inherits_admin_session(client):
    await client.post("/api/auth/pin", json={"pin": "1234"})
    await client.post("/api/auth/unlock", json={"pin": "1234"})
    ws = await client.ws_connect("/ws")
    assert next(iter(utils.get_ws_clients()))["access_level"] == "admin"
    await ws.close()


def test_xff_without_trusted_proxy_ips(monkeypatch):
    from unittest.mock import Mock

    monkeypatch.setattr(utils, "TRUST_PROXY_HEADERS", True)
    monkeypatch.delenv("TRUSTED_PROXY_IPS", raising=False)
    request = Mock(headers={"X-Forwarded-For": "8.8.8.8"})
    request.transport.get_extra_info.return_value = ("192.0.2.1", 1234)
    assert utils._get_client_ip(request) == "192.0.2.1"


def test_ha_api_key_config_schema():
    if importlib.util.find_spec("homeassistant") is None:
        pytest.skip("Home Assistant test dependencies are unavailable")
    from custom_components.hdmi_matrix.config_flow import _schema
    from custom_components.hdmi_matrix.const import CONF_API_KEY

    assert _schema()(dict(host="hub.local", port=8080, api_key="ha-key"))[CONF_API_KEY] == "ha-key"


@pytest.mark.parametrize(
    ("method", "path", "level"),
    [
        ("POST", "/api/settings/matrix-host", "admin"),
        ("POST", "/api/input/1/edid", "admin"),
        ("POST", "/api/output/1/hdcp", "admin"),
        ("PUT", "/api/profile/abc", "admin"),
        ("POST", "/api/cec/macro/abc/execute", "control"),
        ("POST", "/api/v2/scenes/abc/execute", "control"),
        ("POST", "/api/profile/abc/recall", "control"),
        ("POST", "/api/system/reboot", "admin"),
        ("POST", "/api/output/1/source", "control"),
        ("POST", "/api/preset/1/save", "admin"),
    ],
)
def test_route_access_classification(method, path, level):
    assert route_level(method, path) == level
