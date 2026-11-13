"""CORS headers on answers that never reach a route handler.

The CORS middleware ran innermost, so the rate limiter's 429 and the security
guard's 401/403/415/421/429 left without ``Access-Control-Allow-Origin``. A
browser on an allowed origin could not read them and reported a network error
in place of "unlock required" or "slow down".
"""

from __future__ import annotations

import pytest

from rest_api import utils
from rest_api.app import create_rest_app

ALLOWED = "http://allowed.example"
PIN = "1234"


@pytest.fixture
async def client(aiohttp_client, tmp_path, monkeypatch):
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    for name in ("ADMIN_PIN", "CONTROL_PIN", "ADMIN_PIN_RESET", "API_KEY", "CONTROL_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", ALLOWED)
    return await aiohttp_client(create_rest_app(tmp_path))


def assert_cors(resp, origin: str | None = ALLOWED) -> None:
    assert resp.headers.get("Access-Control-Allow-Origin") == origin
    assert resp.headers["Vary"] == "Origin"
    assert "X-API-Key" in resp.headers["Access-Control-Allow-Headers"]


async def test_401_from_the_control_lock_carries_cors_headers(client):
    # Arrange
    await client.post("/api/auth/pin", json={"level": "control", "pin": PIN})

    # Act
    resp = await client.post("/api/power/on", headers={"Origin": ALLOWED})

    # Assert
    assert resp.status == 401
    assert_cors(resp)


async def test_401_from_the_admin_lock_carries_cors_headers(client):
    await client.post("/api/auth/pin", json={"pin": PIN})

    resp = await client.post("/api/settings/test-connection", json={}, headers={"Origin": ALLOWED})

    assert resp.status == 401
    assert_cors(resp)


async def test_429_from_the_pin_lockout_carries_cors_headers(client):
    # Arrange: a locked-out peer
    await client.post("/api/auth/pin", json={"pin": PIN})
    for _ in range(5):
        await client.post("/api/settings/test-connection", json={}, headers={"X-Admin-PIN": "0000"})

    # Act
    resp = await client.post(
        "/api/settings/test-connection", json={}, headers={"X-Admin-PIN": "0000", "Origin": ALLOWED}
    )

    # Assert
    assert resp.status == 429
    assert_cors(resp)


async def test_415_carries_cors_headers(client):
    resp = await client.post(
        "/api/switch", data=b"input=1", headers={"Origin": ALLOWED, "Content-Type": "text/plain"}
    )

    assert resp.status == 415
    assert_cors(resp)


async def test_421_carries_cors_headers(client):
    resp = await client.get("/api/health", headers={"Origin": ALLOWED, "Host": "rebound.example.com"})

    assert resp.status == 421
    assert_cors(resp)


async def test_429_from_the_rate_limiter_carries_cors_headers(client, monkeypatch):
    # Arrange: one write per window
    monkeypatch.setattr(utils, "RATE_LIMIT_REQUESTS", 1)
    first = await client.post("/api/system/beep", json={"enabled": True}, headers={"Origin": ALLOWED})
    assert first.status != 429

    # Act
    resp = await client.post("/api/system/beep", json={"enabled": True}, headers={"Origin": ALLOWED})

    # Assert
    assert resp.status == 429
    assert_cors(resp)


async def test_a_refused_origin_still_gets_no_allow_origin(client):
    """Negative control: the headers are added to every answer, the origin grant is not."""
    resp = await client.post("/api/power/on", headers={"Origin": "http://evil.example"})

    assert resp.status == 403
    assert_cors(resp, origin=None)


async def test_preflight_is_answered_and_still_passes_the_host_guard(client):
    # Act
    ok = await client.options("/api/power/on", headers={"Origin": ALLOWED, "Access-Control-Request-Method": "POST"})
    rebound = await client.options("/api/power/on", headers={"Origin": ALLOWED, "Host": "rebound.example.com"})

    # Assert: answered as before, and a rebound Host is refused as before
    assert ok.status == 200
    assert_cors(ok)
    assert rebound.status == 421
    assert_cors(rebound)
