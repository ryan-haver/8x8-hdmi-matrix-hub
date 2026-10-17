"""Security regression tests for matrix host changes, logging, and TLS."""

import ipaddress
import json
import logging
import ssl
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from orei_matrix import _LOG, OreiMatrix, _matrix_tls_policy
from rest_api import settings


def _request(body):
    request = MagicMock()
    request.json = AsyncMock(return_value=body)
    return request


def _matrix(host="192.168.1.20", password="old-secret"):
    matrix = MagicMock()
    matrix.host = host
    matrix.port = 443
    matrix.password = password
    matrix.connected = True
    matrix.connect = AsyncMock(return_value=True)
    matrix.disconnect = AsyncMock()
    return matrix


@pytest.mark.asyncio
@pytest.mark.parametrize("host", [
    "127.1", "127.0.0.2", "::1", "169.254.169.254", "169.254.1.1", "fe80::1",
    "0.0.0.0", "::", "224.0.0.1", "ff02::1", "240.0.0.1", "8.8.8.8",
    "https://192.168.1.10/", "2130706433", "0177.0.0.1", "0x7f.0.0.1",
])
async def test_ssrf_rejects_disallowed_literals(host, monkeypatch):
    monkeypatch.delenv("ALLOW_PUBLIC_MATRIX_HOST", raising=False)
    assert not await settings._is_safe_host(host, 443)


@pytest.mark.asyncio
@pytest.mark.parametrize("host", [
    "10.2.3.4", "172.16.0.1", "172.31.255.254", "192.168.1.5", "fc00::1",
    "192.0.2.50", "198.51.100.8", "203.0.113.7",
])
async def test_ssrf_allows_lan_and_test_net_literals(host):
    assert await settings._is_safe_host(host, 443)


@pytest.mark.asyncio
async def test_ssrf_checks_every_dns_answer(monkeypatch):
    loop = __import__("asyncio").get_running_loop()

    async def mixed_answers(*_args, **_kwargs):
        return [(2, 1, 6, "", (address, 443)) for address in ("192.168.1.5", "127.0.0.1")]

    monkeypatch.setattr(loop, "getaddrinfo", mixed_answers)
    assert not await settings._is_safe_host("matrix.lan", 443)

    async def safe_answers(*_args, **_kwargs):
        return [(2, 1, 6, "", ("192.168.1.5", 443))]

    monkeypatch.setattr(loop, "getaddrinfo", safe_answers)
    assert await settings._is_safe_host("matrix.lan", 443)


@pytest.mark.asyncio
async def test_ssrf_public_override_keeps_inherently_unsafe_ranges_blocked(monkeypatch):
    monkeypatch.setenv("ALLOW_PUBLIC_MATRIX_HOST", "true")
    assert await settings._is_safe_host("8.8.8.8", 443)
    for host in ("127.0.0.1", "169.254.169.254", "fe80::1", "0.0.0.0", "224.0.0.1", "100.64.0.1"):
        assert not await settings._is_safe_host(host, 443)


@pytest.mark.asyncio
@pytest.mark.parametrize("port", [True, False, "443", 0, -1, 65536, 1.5, None])
async def test_matrix_host_rejects_invalid_port(port, monkeypatch):
    matrix = _matrix()
    monkeypatch.setattr(settings, "get_matrix_device", lambda: matrix)
    response = await settings.handle_set_matrix_host(_request({"host": "192.168.1.30", "port": port}))
    assert response.status == 400
    matrix.disconnect.assert_not_awaited()


@pytest.mark.asyncio
async def test_matrix_host_requires_fresh_password_before_disconnecting(monkeypatch):
    matrix = _matrix()
    monkeypatch.setattr(settings, "get_matrix_device", lambda: matrix)
    for password in (None, "", 123):
        body = {"host": "192.168.1.30"}
        if password is not None:
            body["password"] = password
        response = await settings.handle_set_matrix_host(_request(body))
        assert response.status == 400
        assert "Password is required" in json.loads(response.text)["error"]
        matrix.disconnect.assert_not_awaited()
    response = await settings.handle_set_matrix_host(
        _request({"host": "192.168.1.30", "password": "new-secret"})
    )
    assert response.status == 200
    assert matrix.password == "new-secret"
    matrix.connect.assert_awaited_once()


@pytest.mark.asyncio
async def test_matrix_host_error_does_not_expose_exception(monkeypatch):
    matrix = _matrix(password=None)
    matrix.disconnect = AsyncMock(side_effect=RuntimeError("private disconnect detail"))
    matrix.events.emit.side_effect = RuntimeError("private detail")
    monkeypatch.setattr(settings, "get_matrix_device", lambda: matrix)
    response = await settings.handle_set_matrix_host(_request({"host": "192.168.1.30"}))
    assert response.status == 500
    assert "private detail" not in response.text
    matrix.connected = False
    matrix.connect = AsyncMock(side_effect=RuntimeError("private test detail"))
    response = await settings.handle_test_matrix_connection(_request({}))
    assert response.status == 503
    assert "private test detail" not in response.text


def test_login_logs_redact_structured_and_string_passwords(caplog):
    with caplog.at_level(logging.DEBUG, logger=_LOG.name):
        _LOG.warning("payload: %s", {"password": "unique-secret-one", "nested": [{"Password": "unique-secret-two"}]})
        _LOG.error('login response: {"password":"unique-secret-three"}')
        _LOG.info("login password=unique-secret-four")
        _LOG.info("login password: unique-secret-five")
    rendered = "\n".join(record.getMessage() for record in caplog.records if record.name == _LOG.name)
    assert "***REDACTED***" in rendered
    assert "unique-secret" not in rendered


def test_login_response_is_not_logged_raw(caplog):
    with caplog.at_level(logging.DEBUG, logger=_LOG.name):
        OreiMatrix._classify_response({"comhead": "login"}, 200,
                                      '{"comhead":"login","password":"server-secret","result":0}')
    assert "server-secret" not in caplog.text


def test_tls_default_and_fingerprint(monkeypatch):
    monkeypatch.delenv("MATRIX_CA_CERT", raising=False)
    monkeypatch.delenv("MATRIX_TLS_FINGERPRINT", raising=False)
    monkeypatch.delenv("OREI_VERIFY_SSL", raising=False)
    assert _matrix_tls_policy() is False
    digest = bytes(range(32))
    monkeypatch.setenv("MATRIX_TLS_FINGERPRINT", ":".join(f"{b:02x}" for b in digest))
    policy = _matrix_tls_policy()
    assert isinstance(policy, aiohttp.Fingerprint)
    assert policy.fingerprint == digest
    monkeypatch.setenv("MATRIX_TLS_FINGERPRINT", "invalid")
    with pytest.raises(ValueError):
        _matrix_tls_policy()


def test_tls_custom_ca_uses_verified_context(monkeypatch, tmp_path):
    monkeypatch.delenv("MATRIX_TLS_FINGERPRINT", raising=False)
    ca = tmp_path / "ca.pem"
    ca.write_text("test certificate")
    seen = []

    def fake_create_default_context(*, cafile):
        seen.append(cafile)
        return ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    monkeypatch.setattr(ssl, "create_default_context", fake_create_default_context)
    monkeypatch.setenv("MATRIX_CA_CERT", str(ca))
    assert isinstance(_matrix_tls_policy(), ssl.SSLContext)
    assert seen == [str(ca)]


@pytest.mark.asyncio
async def test_tls_policy_is_passed_to_http_connector(monkeypatch):
    seen = []
    fingerprint = aiohttp.Fingerprint(bytes(range(32)))
    monkeypatch.setattr("orei_matrix._matrix_tls_policy", lambda: fingerprint)
    monkeypatch.setattr("orei_matrix.aiohttp.TCPConnector", lambda **kwargs: seen.append(kwargs["ssl"]))
    monkeypatch.setattr("orei_matrix.aiohttp.ClientSession", lambda **_kwargs: MagicMock())
    matrix = OreiMatrix("192.168.1.20")
    matrix._login = AsyncMock(return_value=False)
    assert not await matrix._connect_once()
    assert seen == [fingerprint]


def test_matrix_password_property_covers_environment_default(monkeypatch):
    monkeypatch.setenv("OREI_PASSWORD", "environment-secret")
    matrix = OreiMatrix("192.168.1.20")
    assert matrix.password == "environment-secret"
    matrix.password = "new-secret"
    assert matrix.credentials()[1] == "new-secret"


def test_matrix_url_supports_allowed_ipv6_literal():
    assert OreiMatrix("fc00::1")._url() == "https://[fc00::1]:443/cgi-bin/instr"


def test_ssrf_address_helper_blocks_mapped_loopback():
    assert not settings._is_allowed_address(ipaddress.ip_address("::ffff:127.0.0.1"))
