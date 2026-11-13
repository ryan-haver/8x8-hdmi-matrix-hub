"""``/api/auth/*`` and the PIN check under bad input, parallel requests and growth.

- A body that is not a JSON object was an unhandled 500 on unlock, pin and
  api-keys.
- ``SecurityManager.verify_pin`` read the lockout, hashed and recorded the
  failure without a lock: requests sent in parallel all passed the lockout
  check before the first hash ended, so the five-attempt limit did not hold
  and every request held a hashing thread.
- Sessions, failure records, remembered devices and API keys had no ceiling.
"""

from __future__ import annotations

import asyncio
import threading
import time

import pytest

from rest_api import security
from rest_api.app import create_rest_app
from rest_api.security import SESSION_IDLE, SecurityManager

PIN = "1234"
JSON = {"Content-Type": "application/json"}


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    for name in ("ADMIN_PIN", "CONTROL_PIN", "ADMIN_PIN_RESET", "CORS_ALLOWED_ORIGINS", "API_KEY", "CONTROL_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    return create_rest_app(tmp_path)


@pytest.fixture
async def client(aiohttp_client, app):
    return await aiohttp_client(app)


class HashProbe:
    """Wraps ``verify_passcode``: counts the calls and how many ran at the same time."""

    def __init__(self, monkeypatch) -> None:
        self.calls = 0
        self.running = 0
        self.most_at_once = 0
        self._guard = threading.Lock()
        self._real = security.verify_passcode
        monkeypatch.setattr(security, "verify_passcode", self)

    def __call__(self, passcode, stored):
        with self._guard:
            self.calls += 1
            self.running += 1
            self.most_at_once = max(self.most_at_once, self.running)
        try:
            time.sleep(0.02)  # long enough for parallel requests to overlap if nothing serializes them
            return self._real(passcode, stored)
        finally:
            with self._guard:
                self.running -= 1


# ----------------------------------------------------------------------------- bad bodies


@pytest.mark.parametrize("path", ["/api/auth/unlock", "/api/auth/login", "/api/auth/pin", "/api/auth/api-keys"])
@pytest.mark.parametrize("raw", [b"{", b"[]", b"null", b'"text"', b"123", b"\xff\xfe"])
async def test_a_body_that_is_not_a_json_object_is_400(client, path, raw):
    resp = await client.post(path, data=raw, headers=JSON)

    assert resp.status == 400, await resp.text()


async def test_bad_bodies_do_not_count_as_wrong_pins(client, app):
    # Arrange
    await client.post("/api/auth/pin", json={"pin": PIN})

    # Act: more malformed unlock requests than the lockout allows wrong PINs
    for _ in range(8):
        assert (await client.post("/api/auth/unlock", data=b"[]", headers=JSON)).status == 400

    # Assert: nothing was recorded, and the right PIN still unlocks
    assert app["security_manager"].failures == {}
    assert (await client.post("/api/auth/unlock", json={"pin": PIN})).status == 200


async def test_an_api_key_can_be_created_without_a_body(client):
    resp = await client.post("/api/auth/api-keys")

    assert resp.status == 201
    assert set(await resp.json()) == {"id", "key"}


@pytest.mark.parametrize("pin", [1234, ["1234"], {"pin": "1234"}, True])
async def test_setting_a_pin_that_is_not_a_string_is_400(client, app, pin):
    resp = await client.post("/api/auth/pin", json={"pin": pin})

    assert resp.status == 400
    assert not app["security_manager"].pin_set("admin")


# ----------------------------------------------------------------------------- what a client's key may do


async def test_auth_status_reports_what_an_api_key_may_do(client):
    """The answer Home Assistant's setup reads to check its key (tests/ha uses this exact shape).

    It is a bare object, it needs no access level, and reading it with a wrong
    key is not a PIN attempt.
    """
    # Arrange: a control lock and one API key
    await client.post("/api/auth/pin", json={"level": "control", "pin": PIN})
    key = await (await client.post("/api/auth/api-keys", json={"name": "HA"})).json()

    async def status(headers=None) -> dict:
        resp = await client.get("/api/auth/status", headers=headers or {})
        assert resp.status == 200
        return await resp.json()

    # Act
    without = await status()
    wrong = await status({"X-API-Key": "not-a-key"})
    right = await status({"X-API-Key": key["key"]})
    await client.delete(f"/api/auth/api-keys/{key['id']}")
    revoked = await status({"X-API-Key": key["key"]})

    # Assert
    locked = {"admin_pin_set": False, "control_pin_set": True, "session_level": "none", "device_remembered": False}
    assert without == wrong == revoked == locked
    assert right == {**locked, "session_level": "control"}


# ----------------------------------------------------------------------------- parallel wrong PINs


async def test_parallel_wrong_pins_cannot_pass_the_lockout(client, monkeypatch):
    # Arrange
    await client.post("/api/auth/pin", json={"pin": PIN})
    probe = HashProbe(monkeypatch)

    # Act: 20 wrong PINs at once from one peer
    answers = await asyncio.gather(*(client.post("/api/auth/unlock", json={"pin": "0000"}) for _ in range(20)))
    statuses = sorted(resp.status for resp in answers)

    # Assert: four free wrong PINs, the fifth locks; the rest never reach the hash
    assert statuses == [401] * 4 + [429] * 16
    assert probe.calls == 5
    assert probe.most_at_once == 1
    assert (await client.post("/api/auth/unlock", json={"pin": PIN})).status == 429


async def test_parallel_wrong_admin_pin_headers_cannot_pass_the_lockout(client, monkeypatch):
    """The ``X-Admin-PIN`` header of an admin route goes through the same check."""
    # Arrange
    await client.post("/api/auth/pin", json={"pin": PIN})
    probe = HashProbe(monkeypatch)

    # Act
    answers = await asyncio.gather(*(
        client.post("/api/settings/test-connection", json={}, headers={"X-Admin-PIN": "0000"}) for _ in range(20)
    ))

    # Assert
    assert sorted(resp.status for resp in answers) == [401] * 4 + [429] * 16
    assert probe.calls == 5
    assert probe.most_at_once == 1


async def test_parallel_right_pins_all_unlock(client, app, monkeypatch):
    # Arrange
    await client.post("/api/auth/pin", json={"pin": PIN})
    probe = HashProbe(monkeypatch)

    # Act
    answers = await asyncio.gather(*(client.post("/api/auth/unlock", json={"pin": PIN}) for _ in range(6)))

    # Assert: serialized, none refused, and no lock entry is left behind
    assert [resp.status for resp in answers] == [200] * 6
    assert probe.most_at_once == 1
    assert app["security_manager"]._pin_checks == {}


async def test_one_peers_lockout_does_not_delay_another_peer(tmp_path, monkeypatch):
    # Arrange
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    manager = SecurityManager(tmp_path)
    manager.state["admin_pin"] = security.hash_passcode(PIN)
    for _ in range(4):
        assert await manager.verify_pin("admin", "0000", "10.0.0.1") is False
    with pytest.raises(security.web.HTTPTooManyRequests):
        await manager.verify_pin("admin", "0000", "10.0.0.1")

    # Act / Assert
    assert await manager.verify_pin("admin", PIN, "10.0.0.2") is True
    with pytest.raises(security.web.HTTPTooManyRequests):
        await manager.verify_pin("admin", PIN, "10.0.0.1")


# ----------------------------------------------------------------------------- ceilings


async def test_failure_records_are_capped_and_locked_peers_are_kept(tmp_path, monkeypatch):
    # Arrange: room for three peers, one of them locked out
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    monkeypatch.setattr(security, "MAX_FAILURE_KEYS", 3)
    manager = SecurityManager(tmp_path)
    manager.state["admin_pin"] = security.hash_passcode(PIN)
    manager.failures["admin:locked"] = (9, time.monotonic() + 600)

    # Act: six more peers each send one wrong PIN
    for n in range(6):
        await manager.verify_pin("admin", "0000", f"10.0.0.{n}")

    # Assert: the newest peers and the locked one remain
    assert list(manager.failures) == ["admin:locked", "admin:10.0.0.4", "admin:10.0.0.5"]


def test_idle_sessions_are_forgotten_and_sessions_are_capped(tmp_path, monkeypatch):
    # Arrange: one idle session, room for three
    monkeypatch.setattr(security, "MAX_SESSIONS", 3)
    manager = SecurityManager(tmp_path)
    manager.sessions["idle"] = ("admin", time.monotonic() - SESSION_IDLE - 1)
    manager.sessions["oldest"] = ("control", time.monotonic() - 60)

    # Act
    for _ in range(3):
        manager.new_session(security.web.Response(), "control")

    # Assert: the idle one went first, then the least recently used
    assert "idle" not in manager.sessions and "oldest" not in manager.sessions
    assert len(manager.sessions) == 3


async def test_remembered_devices_are_capped_at_the_oldest(client, app, monkeypatch):
    # Arrange
    monkeypatch.setattr(security, "MAX_DEVICES", 2)
    await client.post("/api/auth/pin", json={"level": "control", "pin": PIN})

    # Act: three devices are remembered
    for name in ("first", "second", "third"):
        resp = await client.post(
            "/api/auth/unlock", json={"level": "control", "pin": PIN, "remember_device": True, "device_name": name}
        )
        assert resp.status == 200

    # Assert
    devices = app["security_manager"].state["devices"]
    assert [item["name"] for item in devices.values()] == ["second", "third"]


async def test_api_keys_are_capped_without_dropping_a_key_in_use(client, monkeypatch):
    # Arrange: a control lock and a full key list
    monkeypatch.setattr(security, "MAX_API_KEYS", 2)
    await client.post("/api/auth/pin", json={"level": "control", "pin": PIN})
    keys = [await (await client.post("/api/auth/api-keys", json={"name": f"k{n}"})).json() for n in range(2)]

    # Act
    resp = await client.post("/api/auth/api-keys", json={"name": "one too many"})

    # Assert: refused, and both existing keys still work
    assert resp.status == 400
    assert "limit" in await resp.text()
    assert len(await (await client.get("/api/auth/api-keys")).json()) == 2
    for key in keys:
        assert (await client.post("/api/power/on", headers={"X-API-Key": key["key"]})).status != 401
    await client.delete(f"/api/auth/api-keys/{keys[0]['id']}")
    assert (await client.post("/api/auth/api-keys", json={"name": "fits now"})).status == 201
