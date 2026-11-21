"""``POST /api/settings/matrix-host``: bad bodies, the password rule on the runtime, DNS rebinding.

- A body that is not a JSON object was a 500.
- On the shared runtime, a first target or a new port without a password
  passed the handler, was refused by ``runtime.reconfigure`` and was still
  answered "Matrix host updated".
- A host name must stay preserved as configured/displayed while settings saves
  (including same-host port changes) and transport connects validate every answer.
- ``GET /api/settings`` reported the Telnet port 23 as the default matrix port.
"""

from __future__ import annotations

import asyncio
import json
import socket
from unittest.mock import AsyncMock, MagicMock

import pytest

from hub.runtime.config import MatrixAddress, ReconfigureResult
from rest_api import settings, utils
from rest_api.app import create_rest_app

JSON = {"Content-Type": "application/json"}


def matrix(host="192.168.1.20", password="old-secret"):
    device = MagicMock()
    device.host = host
    device.port = 443
    device.password = password
    device.connected = True
    device.connect = AsyncMock(return_value=True)
    device.disconnect = AsyncMock()
    return device


def request(body):
    req = MagicMock()
    req.json = AsyncMock(return_value=body)
    return req


class FakeRuntime:
    """The part of the hub runtime the handler uses: the current address and ``reconfigure``."""

    def __init__(self, address: MatrixAddress | None, result: ReconfigureResult) -> None:
        self.address = address
        self.result = result
        self.calls: list[MatrixAddress] = []

    async def reconfigure(self, address: MatrixAddress) -> ReconfigureResult:
        self.calls.append(address)
        return self.result


def answers(monkeypatch, table: dict[str, list[str]]) -> list[str]:
    """Make the loop resolve names from ``table``; returns the names it was asked for."""
    asked: list[str] = []

    async def getaddrinfo(host, port, **_kwargs):
        asked.append(host)
        return [
            (socket.AF_INET6 if ":" in ip else socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port))
            for ip in table[host]
        ]

    monkeypatch.setattr(asyncio.get_running_loop(), "getaddrinfo", getaddrinfo)
    return asked


async def data(response) -> dict:
    return json.loads(response.text)


# ----------------------------------------------------------------------------- bad bodies, defaults


@pytest.mark.parametrize("raw", [b"{", b"[]", b"null", b'"192.168.1.30"', b"443"])
async def test_a_body_that_is_not_a_json_object_is_400(aiohttp_client, tmp_path, monkeypatch, raw):
    # Arrange
    for name in ("ADMIN_PIN", "CONTROL_PIN", "ADMIN_PIN_RESET"):
        monkeypatch.delenv(name, raising=False)
    client = await aiohttp_client(create_rest_app(tmp_path))
    device = matrix()
    monkeypatch.setattr(utils, "_matrix_device", device)

    # Act
    resp = await client.post("/api/settings/matrix-host", data=raw, headers=JSON)

    # Assert
    assert resp.status == 400, await resp.text()
    assert (await resp.json())["success"] is False
    device.disconnect.assert_not_awaited()


async def test_the_default_matrix_port_is_https(monkeypatch):
    monkeypatch.setattr(settings, "get_matrix_device", lambda: None)

    response = await settings.handle_get_settings(request({}))

    assert (await data(response))["data"] == {"matrix_host": None, "matrix_port": 443, "connected": False}


# ----------------------------------------------------------------------------- the password rule on the runtime


@pytest.mark.parametrize(
    ("current", "body"),
    [
        (None, {"host": "192.168.1.30"}),  # first target of an unconfigured hub
        (MatrixAddress("192.168.1.20", 443), {"host": "192.168.1.30"}),  # new host
        (MatrixAddress("192.168.1.20", 443), {"host": "192.168.1.20", "port": 8443}),  # same host, new port
        (MatrixAddress("192.168.1.20", 443), {"host": "192.168.1.30", "password": ""}),
        (MatrixAddress("192.168.1.20", 443), {"host": "192.168.1.30", "password": 1234}),
    ],
)
async def test_runtime_new_target_without_a_password_is_refused_before_reconfigure(monkeypatch, current, body):
    # Arrange: what the runtime itself would answer is "auth", with nothing changed
    runtime = FakeRuntime(current, ReconfigureResult(False, "auth", False))
    device = matrix(host=current.host if current else "", password=None if current is None else "old-secret")
    monkeypatch.setattr(settings, "get_matrix_device", lambda: device)
    monkeypatch.setattr(utils, "get_runtime", lambda: runtime)

    # Act
    response = await settings.handle_set_matrix_host(request(body))

    # Assert: a 400 that names the reason, not a 200 "Matrix host updated"
    assert response.status == 400
    assert "Password is required" in (await data(response))["error"]
    assert runtime.calls == []


async def test_runtime_same_target_needs_no_password(monkeypatch):
    # Arrange
    runtime = FakeRuntime(MatrixAddress("192.168.1.20", 443), ReconfigureResult(True, connected=True))
    monkeypatch.setattr(settings, "get_matrix_device", lambda: matrix())
    monkeypatch.setattr(utils, "get_runtime", lambda: runtime)

    # Act
    response = await settings.handle_set_matrix_host(request({"host": "192.168.1.20", "telnet_port": 2323}))

    # Assert
    assert response.status == 200
    assert runtime.calls == [MatrixAddress("192.168.1.20", 443, 2323, None, None)]
    body = (await data(response))["data"]
    assert (body["applied"], body["connected"]) == (True, True)


async def test_runtime_rollback_is_not_reported_as_an_update(monkeypatch):
    # Arrange: the new matrix refuses the login; the runtime restores the old one
    runtime = FakeRuntime(MatrixAddress("192.168.1.20", 443), ReconfigureResult(False, "auth", True))
    monkeypatch.setattr(settings, "get_matrix_device", lambda: matrix())
    monkeypatch.setattr(utils, "get_runtime", lambda: runtime)

    # Act
    response = await settings.handle_set_matrix_host(request({"host": "192.168.1.30", "password": "wrong"}))

    # Assert: still 200 (the request was carried out), but it says nothing was changed
    assert response.status == 200
    body = (await data(response))["data"]
    assert (body["applied"], body["connected"]) == (False, False)
    assert body["message"].startswith("Matrix host not changed")
    assert "updated" not in body["message"]


# ----------------------------------------------------------------------------- hostname preservation & DNS rebinding


async def test_new_hostname_preserves_saved_displayed_and_response_host(monkeypatch):
    asked = answers(monkeypatch, {"matrix.lan": ["fd00::77", "192.168.1.77"]})
    device = matrix()
    monkeypatch.setattr(settings, "get_matrix_device", lambda: device)
    monkeypatch.setattr(utils, "get_runtime", lambda: None)

    response = await settings.handle_set_matrix_host(request({"host": "matrix.lan", "password": "new-secret"}))

    assert response.status == 200
    body = (await data(response))["data"]
    assert device.host == "matrix.lan"
    assert device.password == "new-secret"
    assert body["host"] == "matrix.lan"
    assert body["applied"] is True
    assert asked == ["matrix.lan"]
    device.connect.assert_awaited_once()

    shown = await settings.handle_get_settings(request({}))
    assert (await data(shown))["data"]["matrix_host"] == "matrix.lan"


async def test_runtime_reconfigure_preserves_hostname_and_validates_same_host_port_change(monkeypatch):
    asked = answers(monkeypatch, {"matrix.lan": ["192.168.1.77"]})
    runtime = FakeRuntime(MatrixAddress("192.168.1.20", 443), ReconfigureResult(True, connected=True))
    monkeypatch.setattr(settings, "get_matrix_device", lambda: matrix())
    monkeypatch.setattr(utils, "get_runtime", lambda: runtime)

    first = await settings.handle_set_matrix_host(
        request({"host": "matrix.lan", "port": 443, "password": "new-secret"})
    )
    assert first.status == 200
    assert runtime.calls[-1] == MatrixAddress("matrix.lan", 443, None, None, "new-secret")
    assert (await data(first))["data"]["host"] == "matrix.lan"

    runtime.address = MatrixAddress("matrix.lan", 443)
    runtime.result = ReconfigureResult(False, "refused", True)
    second = await settings.handle_set_matrix_host(
        request({"host": "matrix.lan", "port": 8443, "password": "port-secret"})
    )
    assert second.status == 200
    body = (await data(second))["data"]
    assert (body["host"], body["port"], body["applied"], body["connected"]) == ("matrix.lan", 8443, False, False)
    assert body["message"].startswith("Matrix host not changed")
    assert runtime.calls[-1] == MatrixAddress("matrix.lan", 8443, None, None, "port-secret")
    assert asked == ["matrix.lan", "matrix.lan"]


async def test_same_host_port_or_telnet_port_change_rejects_rebound_or_mixed_dns(monkeypatch):
    dns_records = ["127.0.0.1"]

    async def rebinding_getaddrinfo(host, port, **_kwargs):
        assert host == "matrix.lan"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port)) for ip in dns_records]

    monkeypatch.setattr(asyncio.get_running_loop(), "getaddrinfo", rebinding_getaddrinfo)
    runtime = FakeRuntime(MatrixAddress("matrix.lan", 443), ReconfigureResult(True, connected=True))
    device = matrix(host="matrix.lan")
    monkeypatch.setattr(settings, "get_matrix_device", lambda: device)
    monkeypatch.setattr(utils, "get_runtime", lambda: runtime)

    telnet_change = await settings.handle_set_matrix_host(request({"host": "matrix.lan", "telnet_port": 2323}))
    assert telnet_change.status == 400

    dns_records[:] = ["192.168.1.77", "169.254.169.254"]
    port_change = await settings.handle_set_matrix_host(
        request({"host": "matrix.lan", "port": 8443, "password": "secret"})
    )
    assert port_change.status == 400
    assert runtime.calls == []
    device.disconnect.assert_not_awaited()


async def test_a_name_with_any_unsafe_address_is_still_refused(monkeypatch):
    """Negative control: pinning does not weaken the every-answer check."""
    answers(monkeypatch, {"matrix.lan": ["192.168.1.77", "127.0.0.1"]})
    device = matrix()
    monkeypatch.setattr(settings, "get_matrix_device", lambda: device)

    response = await settings.handle_set_matrix_host(request({"host": "matrix.lan", "password": "new-secret"}))

    assert response.status == 400
    assert device.host == "192.168.1.20"
    device.disconnect.assert_not_awaited()


async def test_the_name_the_hub_already_uses_is_kept(monkeypatch):
    """A name from the hub's own configuration is not rewritten by a save that does not change it."""
    monkeypatch.setattr(utils, "get_runtime", lambda: None)
    answers(monkeypatch, {"matrix.lan": ["192.168.1.77"]})
    device = matrix(host="matrix.lan")
    monkeypatch.setattr(settings, "get_matrix_device", lambda: device)

    response = await settings.handle_set_matrix_host(request({"host": "matrix.lan", "telnet_port": 2323}))

    assert response.status == 200
    assert device.host == "matrix.lan"


async def test_allowed_address_literals_preserved_and_standalone_port_change_requires_password(monkeypatch):
    monkeypatch.setattr(utils, "get_runtime", lambda: None)
    device = matrix(host="192.168.1.30", password="old-secret")
    monkeypatch.setattr(settings, "get_matrix_device", lambda: device)

    missing_pw = await settings.handle_set_matrix_host(request({"host": "192.168.1.30", "port": 8443}))
    assert missing_pw.status == 400
    device.disconnect.assert_not_awaited()

    allowed_v6 = await settings.handle_set_matrix_host(request({"host": "fc00::30", "password": "v6-secret"}))
    assert allowed_v6.status == 200
    assert device.host == "fc00::30"
    assert (await data(allowed_v6))["data"]["host"] == "fc00::30"
