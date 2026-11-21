"""Security regression tests for matrix host changes, logging, and TLS."""

import asyncio
import ipaddress
import json
import logging
import socket
import ssl
from unittest.mock import AsyncMock, MagicMock
from urllib.parse import urlsplit

import aiohttp
import pytest
from aiohttp.abc import AbstractResolver

from orei_matrix import _LOG, OreiMatrix, _matrix_tls_policy
from rest_api import settings
from telnet_client import TelnetClient


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
    from rest_api import utils

    monkeypatch.setattr(utils, "get_runtime", lambda: None)
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
    from rest_api import utils

    monkeypatch.setattr(utils, "get_runtime", lambda: None)
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


@pytest.mark.asyncio
async def test_http_connect_pins_validated_ip_while_preserving_hostname_url_and_sni(monkeypatch, tmp_path):
    loop = asyncio.get_running_loop()
    asked: list[tuple[str, int]] = []

    async def fake_getaddrinfo(host, port, **_kwargs):
        asked.append((host, port))
        return [
            (socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("fd00::77", port, 0, 0)),
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("192.168.1.77", port)),
        ]

    monkeypatch.setattr(loop, "getaddrinfo", fake_getaddrinfo)

    ca_file = tmp_path / "matrix-ca.pem"
    ca_file.write_text("test-ca")
    monkeypatch.setattr(
        ssl,
        "create_default_context",
        lambda *, cafile: ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT) if cafile == str(ca_file) else None,
    )
    digest_hex = ":".join(f"{b:02x}" for b in range(32))

    captured_connectors: list[dict[str, object]] = []
    monkeypatch.setattr("orei_matrix.aiohttp.TCPConnector", lambda **kwargs: captured_connectors.append(kwargs))
    monkeypatch.setattr("orei_matrix.aiohttp.ClientSession", lambda **_kwargs: MagicMock())

    for env_setup, use_https, check_ssl in (
        ({"OREI_VERIFY_SSL": "true"}, True, lambda s: s is True),
        ({"MATRIX_CA_CERT": str(ca_file)}, True, lambda s: isinstance(s, ssl.SSLContext)),
        ({"MATRIX_TLS_FINGERPRINT": digest_hex}, True, lambda s: isinstance(s, aiohttp.Fingerprint)),
        ({}, False, lambda s: s is None),
    ):
        for key in ("OREI_VERIFY_SSL", "MATRIX_CA_CERT", "MATRIX_TLS_FINGERPRINT"):
            monkeypatch.delenv(key, raising=False)
        for key, value in env_setup.items():
            monkeypatch.setenv(key, value)

        matrix = OreiMatrix("matrix.lan", port=443 if use_https else 80, use_https=use_https)
        matrix._login = AsyncMock(return_value=False)
        assert not await matrix._connect_once()
        assert matrix.host == "matrix.lan"
        expected_scheme = "https" if use_https else "http"
        expected_port = 443 if use_https else 80
        assert matrix._url() == f"{expected_scheme}://matrix.lan:{expected_port}/cgi-bin/instr"

        conn_kwargs = captured_connectors[-1]
        assert conn_kwargs["use_dns_cache"] is False
        assert isinstance(conn_kwargs["resolver"], AbstractResolver)
        assert check_ssl(conn_kwargs.get("ssl"))

    resolver = captured_connectors[0]["resolver"]
    assert isinstance(resolver, AbstractResolver)
    resolved = await resolver.resolve("matrix.lan", 443)
    assert asked == [("matrix.lan", 443)]
    assert [entry["host"] for entry in resolved] == ["192.168.1.77", "fd00::77"]
    assert [entry["hostname"] for entry in resolved] == ["matrix.lan", "matrix.lan"]
    assert all(bool(entry["flags"] & socket.AI_NUMERICHOST) for entry in resolved)


@pytest.mark.asyncio
async def test_http_connect_and_reconnect_block_dns_rebinding_and_mixed_answers(monkeypatch):
    for env_key in ("ALLOW_PUBLIC_MATRIX_HOST", "OREI_VERIFY_SSL", "MATRIX_CA_CERT", "MATRIX_TLS_FINGERPRINT"):
        monkeypatch.delenv(env_key, raising=False)
    loop = asyncio.get_running_loop()
    dns_answers = ["192.168.1.77", "127.0.0.1"]

    async def fake_getaddrinfo(host, port, **_kwargs):
        return [
            (
                socket.AF_INET6 if ":" in ip else socket.AF_INET,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                (ip, port, 0, 0) if ":" in ip else (ip, port),
            )
            for ip in dns_answers
        ]

    monkeypatch.setattr(loop, "getaddrinfo", fake_getaddrinfo)

    for use_https, case_ips in (
        (True, ["192.168.1.77", "127.0.0.1"]),
        (False, ["::ffff:169.254.169.254"]),
    ):
        dns_answers[:] = case_ips
        unmocked = OreiMatrix("matrix.lan", port=443 if use_https else 80, use_https=use_https)
        unmocked.auto_reconnect = False
        try:
            assert await unmocked.connect() is False
            assert unmocked.host == "matrix.lan"
        finally:
            await unmocked.disconnect()

    dialed_targets: list[tuple[str, str, str]] = []
    closed_sessions: list[bool] = []
    connector_records: list[dict[str, object]] = []
    real_tcp_connector = aiohttp.TCPConnector

    def tracking_tcp_connector(**kwargs):
        connector = real_tcp_connector(**kwargs)
        connector_records.append({"connector": connector, **kwargs})
        return connector

    class _FakeSession:
        def __init__(self, *, connector=None, **_kwargs):
            self.connector = connector
            self.record = connector_records[-1]

        def post(self, url, **_kwargs):
            record = self.record

            class _PostCtx:
                async def __aenter__(self):
                    assert record["use_dns_cache"] is False
                    resolver = record["resolver"]
                    assert isinstance(resolver, AbstractResolver)
                    parsed = urlsplit(url)
                    assert parsed.hostname is not None
                    resolved = await resolver.resolve(parsed.hostname, parsed.port or 443)
                    dialed_targets.append((url, resolved[0]["host"], resolved[0]["hostname"]))
                    resp = MagicMock()
                    resp.status = 200
                    resp.text = AsyncMock(return_value='{"comhead":"login","result":1}')
                    return resp

                async def __aexit__(self, *_exc):
                    return False

            return _PostCtx()

        async def close(self):
            closed_sessions.append(True)
            if self.connector is not None:
                await self.connector.close()

    monkeypatch.setattr("orei_matrix.aiohttp.TCPConnector", tracking_tcp_connector)
    monkeypatch.setattr("orei_matrix.aiohttp.ClientSession", _FakeSession)

    dns_answers[:] = ["192.168.1.77"]
    matrix = OreiMatrix("matrix.lan", port=443, use_https=True)
    matrix.auto_reconnect = False
    matrix._connect_telnet = AsyncMock(return_value=False)
    try:
        assert await matrix.connect() is True
        assert matrix.connected is True
        assert matrix.host == "matrix.lan"
        assert dialed_targets == [("https://matrix.lan:443/cgi-bin/instr", "192.168.1.77", "matrix.lan")]

        matrix._link_lost("simulated socket drop")
        dns_answers[:] = ["127.0.0.1"]
        assert await matrix.connect() is False
        assert closed_sessions == [True]
        assert len(dialed_targets) == 1
        assert matrix.host == "matrix.lan"

        dns_answers[:] = ["169.254.169.254"]
        matrix.port = 8443
        assert await matrix.connect() is False
        assert len(dialed_targets) == 1
    finally:
        await matrix.disconnect()


@pytest.mark.asyncio
async def test_http_connect_blocks_disallowed_literals_and_legacy_hosts(monkeypatch):
    monkeypatch.delenv("ALLOW_PUBLIC_MATRIX_HOST", raising=False)
    loop = asyncio.get_running_loop()

    async def fail_dns(*_args, **_kwargs):
        raise AssertionError("unexpected DNS lookup for literal or legacy host")

    monkeypatch.setattr(loop, "getaddrinfo", fail_dns)

    for bad_host in (
        "127.0.0.1",
        "::1",
        "::ffff:127.0.0.1",
        "169.254.169.254",
        "fe80::1",
        "0.0.0.0",
        "224.0.0.1",
        "8.8.8.8",
        "127.1",
        "2130706433",
        "0177.0.0.1",
        "0x7f.0.0.1",
    ):
        matrix = OreiMatrix(bad_host)
        matrix.auto_reconnect = False
        assert await matrix.connect() is False

    mutated = OreiMatrix("192.168.1.20")
    mutated._session = MagicMock()
    mutated.host = "127.0.0.1"
    result = await mutated._post({"comhead": "get system status"})
    assert result.kind == "transport"
    mutated._session.post.assert_not_called()


@pytest.mark.asyncio
async def test_telnet_connect_and_reconnect_validate_destination_and_preserve_hostname(monkeypatch):
    monkeypatch.delenv("ALLOW_PUBLIC_MATRIX_HOST", raising=False)
    loop = asyncio.get_running_loop()
    dns_plan = [
        ["fd00::77", "192.168.1.77"],
        ["192.168.1.77", "127.0.0.1"],
        ["127.0.0.1"],
    ]
    asked: list[tuple[str, int]] = []
    dialed: list[tuple[str, int]] = []

    async def planned_getaddrinfo(host, port, **_kwargs):
        asked.append((host, port))
        ips = dns_plan.pop(0)
        return [
            (
                socket.AF_INET6 if ":" in ip else socket.AF_INET,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                (ip, port, 0, 0) if ":" in ip else (ip, port),
            )
            for ip in ips
        ]

    async def fake_open_connection(host, port):
        dialed.append((host, port))
        writer = MagicMock()
        writer.wait_closed = AsyncMock()
        return MagicMock(), writer

    monkeypatch.setattr(loop, "getaddrinfo", planned_getaddrinfo)
    monkeypatch.setattr(asyncio, "open_connection", fake_open_connection)

    client = TelnetClient("matrix.lan", port=23)
    client._read_available = AsyncMock(return_value="fw version: v1.10\r\n")
    client._listen_for_push = AsyncMock(return_value=None)

    assert await client.connect() is True
    assert client.host == "matrix.lan"
    assert asked == [("matrix.lan", 23)]
    assert dialed == [("192.168.1.77", 23)]
    await client.disconnect()

    assert await client.connect() is False
    assert len(dialed) == 1
    assert await client.connect() is False
    assert len(dialed) == 1
    assert client.host == "matrix.lan"

    for bad_literal in ("127.0.0.1", "::ffff:169.254.169.254"):
        assert await TelnetClient(bad_literal, port=23).connect() is False
    assert len(asked) == 3
    assert len(dialed) == 1


_TLS_QA_PKI_MAX_BYTES, _TLS_QA_LOG_MAX_BYTES, _TLS_QA_ROOT_MAX_BYTES = 262_144, 5 * 1024 * 1024, 20 * 1024 * 1024
_TLS_IPV4_LINK_LOCAL = ipaddress.IPv4Network("169.254.0.0/16")
_TLS_ENV_KEYS = ("ALLOW_PUBLIC_MATRIX_HOST", "OREI_VERIFY_SSL", "MATRIX_CA_CERT", "MATRIX_TLS_FINGERPRINT")


_TLS_PREREQ_DIAGNOSTICS: dict[str, str] = {
    "prereq_incomplete": "OREI_REQUIRE_REAL_TLS / OREI_TLS_QA_OWNED / OREI_TLS_QA_INTERFACE / OREI_TLS_QA_BIND_IP / OREI_TLS_QA_ROOT incomplete or invalid.", "ownership_unattested": "OREI_TLS_QA_OWNED rejected: positive ownership attestation required.",
    "bind_ip_zone": "OREI_TLS_QA_BIND_IP rejected: scope zone ID disallowed.", "bind_ip_literal": "OREI_TLS_QA_BIND_IP rejected: valid IPv4 or IPv6 literal required.",
    "bind_ip_policy": "OREI_TLS_QA_BIND_IP rejected: outside permitted private or TEST-NET ranges.", "iface_loopback": "OREI_TLS_QA_INTERFACE rejected: loopback interface disallowed.",
    "iface_unavailable": "OREI_TLS_QA_INTERFACE rejected: interface missing, down, or unreadable.", "bind_ip_unassigned": "OREI_TLS_QA_BIND_IP rejected: not assigned to OREI_TLS_QA_INTERFACE.",
    "qa_root_invalid": "OREI_TLS_QA_ROOT rejected: existing non-root owned directory required.", "qa_root_overlap": "OREI_TLS_QA_ROOT rejected: overlaps worktree outside owned build subdir.",
    "qa_root_symlink": "OREI_TLS_QA_ROOT rejected: symlink escapes root or fails resolution.", "qa_root_budget": "OREI_TLS_QA_ROOT rejected: exceeds per-log or total storage budget.",
    "qa_root_io": "OREI_TLS_QA_ROOT rejected: filesystem traversal or stat failed.", "prereq_unexpected": "Real-TLS QA prerequisite check failed unexpectedly.",
}


def _check_real_tls_qa_prereqs(env_in, addrs_in, stats_in, repo_in):
    import contextlib
    import os
    from pathlib import Path

    def _guard(category: str, fn=None, *, ok: bool = True):
        if ok:
            with contextlib.suppress(Exception):
                return fn() if fn is not None else None
        raise RuntimeError(category)

    try:
        true_vals, env_map = {"1", "true", "yes"}, _guard("prereq_unexpected", lambda: os.environ if env_in is None else env_in)
        req_raw = _guard("prereq_unexpected", lambda: str(env_map.get("OREI_REQUIRE_REAL_TLS", "") or "").strip().lower())
        owned_raw, iface, ip_raw, root_raw = _guard("prereq_unexpected", lambda: tuple(str(env_map.get(k, "") or "").strip() for k in ("OREI_TLS_QA_OWNED", "OREI_TLS_QA_INTERFACE", "OREI_TLS_QA_BIND_IP", "OREI_TLS_QA_ROOT")))
        _guard("prereq_incomplete", ok=req_raw in {"", "0", "false", "no"} | true_vals)
        if not any((owned_raw, iface, ip_raw, root_raw)) and req_raw not in true_vals:
            return None, None
        _guard("prereq_incomplete", ok=bool(owned_raw and iface and ip_raw and root_raw))
        _guard("ownership_unattested", ok=owned_raw.lower() in true_vals)
        _guard("bind_ip_zone", ok="%" not in ip_raw)
        bind_ip = _guard("bind_ip_literal", lambda: ipaddress.ip_address(ip_raw))
        is_v6_mapped, allowed_net = isinstance(bind_ip, ipaddress.IPv6Address) and bind_ip.ipv4_mapped is not None, any(net.version == bind_ip.version and bind_ip in net for net in settings._ALLOWED_MATRIX_NETWORKS)
        _guard("bind_ip_policy", ok=not (is_v6_mapped or bind_ip.is_loopback or bind_ip.is_link_local or bind_ip.is_unspecified or bind_ip.is_multicast or (bind_ip.version == 4 and bind_ip in _TLS_IPV4_LINK_LOCAL)) and allowed_net)
        _guard("iface_loopback", ok=iface.lower() != "lo" and "loopback" not in iface.lower())
        addrs_map, stats_map = (_guard("iface_unavailable", lambda: __import__("psutil").net_if_addrs()) if addrs_in is None else addrs_in), (_guard("iface_unavailable", lambda: __import__("psutil").net_if_stats()) if stats_in is None else stats_in)
        _guard("iface_unavailable", ok=_guard("iface_unavailable", lambda: iface in addrs_map and iface in stats_map and bool(getattr(stats_map[iface], "isup", False))))
        iface_ips: set[ipaddress.IPv4Address | ipaddress.IPv6Address] = set()
        for snic in _guard("iface_unavailable", lambda: [s for s in addrs_map[iface] if getattr(s, "family", None) in (socket.AF_INET, socket.AF_INET6)]):
            with contextlib.suppress(ValueError):
                iface_ips.add(ipaddress.ip_address(_guard("iface_unavailable", lambda s=snic: str(getattr(s, "address", ""))).split("%", 1)[0]))
        _guard("bind_ip_unassigned", ok=bind_ip in iface_ips)
        qa_root = _guard("qa_root_invalid", lambda: Path(root_raw).resolve())
        _guard("qa_root_invalid", ok=bool(_guard("qa_root_invalid", lambda: qa_root.exists() and qa_root.is_dir())) and qa_root != Path(qa_root.anchor) and not (len(qa_root.parts) >= 2 and qa_root.parts[1].lower() == "t"))
        checkout_root = _guard("qa_root_overlap", lambda: Path(repo_in).resolve() if repo_in is not None else Path(__file__).resolve().parents[1])
        _guard("qa_root_overlap", ok=qa_root != checkout_root and not checkout_root.is_relative_to(qa_root) and (not qa_root.is_relative_to(checkout_root) or (qa_root != checkout_root / "build" and qa_root.is_relative_to(checkout_root / "build"))))
        walk_err, total_bytes = [], 0
        for dirpath, dirnames, filenames in os.walk(qa_root, topdown=True, onerror=lambda _exc: walk_err.append(True), followlinks=False):
            for entry in (Path(dirpath) / name for name in (*tuple(dirnames), *filenames)):
                is_link = _guard("qa_root_io", lambda e=entry: e.is_symlink() or bool(getattr(e.lstat(), "st_reparse_tag", 0)))
                _guard("qa_root_symlink", ok=not is_link or _guard("qa_root_symlink", lambda e=entry: e.resolve(strict=True)).is_relative_to(qa_root))
                dirnames[:] = [d for d in dirnames if not (is_link and d == entry.name)]
                if _guard("qa_root_io", entry.is_file):
                    total_bytes += (size := _guard("qa_root_io", entry.stat).st_size)
                    _guard("qa_root_budget", ok=not ((entry.suffix.lower() == ".log" and size > _TLS_QA_LOG_MAX_BYTES) or total_bytes > _TLS_QA_ROOT_MAX_BYTES))
        _guard("qa_root_io", ok=not walk_err)
        return None, (bind_ip, iface, qa_root)
    except Exception as exc:
        return (exc.args[0] if type(exc) is RuntimeError and len(exc.args) == 1 and exc.args[0] in _TLS_PREREQ_DIAGNOSTICS else "prereq_unexpected"), None


def _validate_real_tls_qa_prereqs(*, env=None, if_addrs=None, if_stats=None, repo_root=None):
    """Validate positively owned policy-permitted private interface and QA root before any socket contact."""
    err, res = _check_real_tls_qa_prereqs(env, if_addrs, if_stats, repo_root)
    del env, if_addrs, if_stats, repo_root
    if err is not None:
        raise RuntimeError(_TLS_PREREQ_DIAGNOSTICS[err])
    return res


def _forward_real_tls_qa_prereqs(**kwargs):
    try:
        msg, res = None, _validate_real_tls_qa_prereqs(**kwargs)
    except Exception as exc:
        msg, res = (exc.args[0] if type(exc) is RuntimeError and len(exc.args) == 1 and exc.args[0] in _TLS_PREREQ_DIAGNOSTICS.values() else _TLS_PREREQ_DIAGNOSTICS["prereq_unexpected"]), None
    del kwargs
    return pytest.fail(msg, pytrace=False) if msg else (pytest.skip("Real-TLS endpoint prerequisites absent (OREI_TLS_QA_* / OREI_REQUIRE_REAL_TLS); skip is never real-TLS evidence.") if res is None else res)


@pytest.fixture
async def real_tls_qa_harness():
    """Provision confined synthetic X.509 material and owned private-interface TLS server factory."""
    import contextlib
    import datetime
    import hashlib
    import os
    import shutil
    import tempfile
    from pathlib import Path

    validated = _forward_real_tls_qa_prereqs()
    owned_ip, owned_iface, qa_root_obj = validated
    qa_root = Path(str(qa_root_obj)).resolve()
    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
    except ImportError as exc:
        pytest.fail(f"cryptography package is required for real-TLS verification tests: {exc}")
    now = datetime.datetime.now(datetime.UTC)
    pki_dir = Path(tempfile.mkdtemp(prefix="orei-tls-pki-", dir=str(qa_root))).resolve()
    assert pki_dir.is_relative_to(qa_root)

    def _mint_cert(cn: str, *, dns_san: str | None = None, issuer=None):
        is_ca, key = dns_san is None, ec.generate_private_key(ec.SECP256R1())
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
        sign_key, issuer_name = (key, subject) if issuer is None else (issuer[0], issuer[1].subject)
        ku = x509.KeyUsage(
            digital_signature=True, content_commitment=False, key_encipherment=False, data_encipherment=False,
            key_agreement=False, key_cert_sign=is_ca, crl_sign=is_ca, encipher_only=False, decipher_only=False,
        )
        exts = [
            (x509.BasicConstraints(ca=is_ca, path_length=0 if is_ca else None), True), (ku, True),
            (x509.SubjectKeyIdentifier.from_public_key(key.public_key()), False),
            (x509.AuthorityKeyIdentifier.from_issuer_public_key(sign_key.public_key()), False),
        ] + ([(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), False), (x509.SubjectAlternativeName([x509.DNSName(dns_san)]), False)] if dns_san else [])
        builder = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer_name).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(hours=1)).not_valid_after(now + datetime.timedelta(days=2))
        for ext, crit in exts:
            builder = builder.add_extension(ext, critical=crit)
        return key, builder.sign(private_key=sign_key, algorithm=hashes.SHA256())

    def _write_confined(name: str, payload: bytes, *, secret: bool = False) -> Path:
        dest = (pki_dir / name).resolve()
        assert dest.is_relative_to(qa_root)
        dest.write_bytes(payload)
        if secret:
            with contextlib.suppress(OSError):
                os.chmod(dest, 0o600)
        return dest

    def _pem_pair(prefix: str, key, cert, extra=None) -> tuple[Path, Path]:
        pem_enc = serialization.Encoding.PEM
        cert_bytes = cert.public_bytes(pem_enc) + (extra.public_bytes(pem_enc) if extra is not None else b"")
        key_bytes = key.private_bytes(pem_enc, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
        return _write_confined(f"{prefix}_cert.pem", cert_bytes), _write_confined(f"{prefix}_key.pem", key_bytes, secret=True)

    try:
        trusted_ca, untrusted_ca = _mint_cert("OREI QA Trusted Root CA"), _mint_cert("OREI QA Untrusted Root CA")
        pinned_pair = _mint_cert("appliance-selfsigned.invalid", dns_san="appliance-selfsigned.invalid")
        trusted_ca_pem = _write_confined("trusted_ca.pem", trusted_ca[1].public_bytes(serialization.Encoding.PEM))
        corrupt_ca_pem = _write_confined("corrupt_ca.pem", b"not-a-valid-ca-bundle\n")
        profiles: dict[str, tuple[Path, Path]] = {
            "valid": _pem_pair("valid", *_mint_cert("matrix.lan", dns_san="matrix.lan", issuer=trusted_ca)),
            "wrong_name": _pem_pair("wrong", *_mint_cert("wrong-matrix.lan", dns_san="wrong-matrix.lan", issuer=trusted_ca)),
            "untrusted_chain": _pem_pair("untrusted", *_mint_cert("matrix.lan", dns_san="matrix.lan", issuer=untrusted_ca), extra=untrusted_ca[1]),
            "pinned_selfsigned": _pem_pair("pinned", *pinned_pair),
        }
        pki_bytes = sum(p.stat().st_size for p in pki_dir.rglob("*") if p.is_file())
        qa_bytes = sum(p.stat().st_size for p in qa_root.rglob("*") if p.is_file())
        assert 0 < pki_bytes <= _TLS_QA_PKI_MAX_BYTES and pki_bytes <= qa_bytes <= _TLS_QA_ROOT_MAX_BYTES
        pinned_digest = hashlib.sha256(pinned_pair[1].public_bytes(serialization.Encoding.DER)).digest()

        @contextlib.asynccontextmanager
        async def open_endpoint(profile: str, monkeypatch, *, dns_hosts: list[str] | None = None):
            loop = asyncio.get_running_loop()
            sock_family = socket.AF_INET6 if owned_ip.version == 6 else socket.AF_INET
            client_hellos, http_requests, dns_queries = [], [], []
            dns_map: dict[str, list[str]] = {"matrix.lan": [str(owned_ip)] if dns_hosts is None else list(dns_hosts)}
            active_writers: set[asyncio.StreamWriter] = set()
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            ssl_ctx.load_cert_chain(certfile=str(profiles[profile][0]), keyfile=str(profiles[profile][1]))

            def _on_sni(_obj: object, server_name: str | None, _ctx: object) -> None:
                client_hellos.append(server_name)

            ssl_ctx.sni_callback = _on_sni

            async def _finish_writer(writer: asyncio.StreamWriter) -> None:
                active_writers.discard(writer)
                writer.close()
                with contextlib.suppress(Exception):
                    await writer.wait_closed()

            async def _handle_https(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
                active_writers.add(writer)
                try:
                    req_line = await asyncio.wait_for(reader.readline(), timeout=3.0)
                    parts = req_line.decode("latin-1").rstrip("\r\n").split(" ", 2) if req_line else []
                    if len(parts) < 2:
                        return
                    headers: dict[str, str] = {}
                    while (hline := await asyncio.wait_for(reader.readline(), timeout=3.0)) not in (b"\r\n", b"\n", b""):
                        if b":" in hline:
                            k, v = hline.decode("latin-1").rstrip("\r\n").split(":", 1)
                            headers[k.strip().lower()] = v.strip()
                    length = int(headers.get("content-length", "0"))
                    raw_body = await asyncio.wait_for(reader.readexactly(length), timeout=3.0) if length > 0 else b""
                    parsed = json.loads(raw_body) if raw_body else {}
                    peer, ssl_obj = writer.get_extra_info("peername"), writer.get_extra_info("ssl_object")
                    comhead = str(parsed.get("comhead", ""))
                    http_requests.append({
                        "method": parts[0], "path": parts[1], "host": headers.get("host", ""), "comhead": comhead, "has_password": bool(parsed.get("password")),
                        "peer_ip": str(peer[0]).split("%", 1)[0] if isinstance(peer, tuple) and peer else "", "tls_version": ssl_obj.version() if ssl_obj is not None else None,
                    })
                    resp_obj = {"comhead": "get system status", "power": 1, "beep": 1, "lock": 0, "mode": 0, "baudrate": 115200} if comhead == "get system status" else {"comhead": comhead, "result": 1}
                    resp_bytes = json.dumps(resp_obj).encode()
                    writer.write(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: {len(resp_bytes)}\r\nConnection: close\r\n\r\n".encode("ascii") + resp_bytes)
                    await writer.drain()
                except (OSError, ssl.SSLError, asyncio.IncompleteReadError, TimeoutError, ValueError):
                    return
                finally:
                    await _finish_writer(writer)

            async def _handle_telnet(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
                active_writers.add(writer)
                try:
                    writer.write(b"fw version: v1.10\r\n")
                    await writer.drain()
                    while await reader.read(256):
                        pass
                except OSError:
                    return
                finally:
                    await _finish_writer(writer)

            https_srv = await asyncio.start_server(_handle_https, str(owned_ip), 0, family=sock_family, ssl=ssl_ctx, reuse_address=False)
            telnet_srv = await asyncio.start_server(_handle_telnet, str(owned_ip), 0, family=sock_family, reuse_address=False)
            try:
                https_sock, telnet_sock = https_srv.sockets[0].getsockname(), telnet_srv.sockets[0].getsockname()
                assert ipaddress.ip_address(str(https_sock[0]).split("%", 1)[0]) == owned_ip == ipaddress.ip_address(str(telnet_sock[0]).split("%", 1)[0])
                https_port, telnet_port = int(https_sock[1]), int(telnet_sock[1])
                assert 1 <= https_port <= 65535 and 1 <= telnet_port <= 65535
                real_getaddrinfo = loop.getaddrinfo

                async def _controlled_getaddrinfo(host: str, port: int, *args: object, **kwargs: object):
                    if host in dns_map:
                        dns_queries.append((host, int(port)))
                        req_family = int(kwargs.get("family", args[0] if args else socket.AF_UNSPEC))
                        records = [
                            (af, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", (str(ip_obj), int(port), 0, 0) if ip_obj.version == 6 else (str(ip_obj), int(port)))
                            for target_raw in dns_map[host]
                            for ip_obj in (ipaddress.ip_address(target_raw),)
                            for af in (socket.AF_INET6 if ip_obj.version == 6 else socket.AF_INET,)
                            if req_family in (socket.AF_UNSPEC, af)
                        ]
                        if not records:
                            raise socket.gaierror(socket.EAI_NONAME, f"no matching family for {host!r}")
                        return records
                    if host == str(owned_ip):
                        return await real_getaddrinfo(host, port, *args, **kwargs)
                    raise AssertionError(f"Blocked unexpected DNS lookup outside owned QA target: {host!r}:{port!r}")

                async def _run_client(*, password: str = "tls-secret", read_status: bool = False, raw_cmd: bool = False):
                    dev = OreiMatrix("matrix.lan", port=https_port, use_https=True, password=password, telnet_port=telnet_port)
                    dev.auto_reconnect = False
                    try:
                        ok = await dev.connect()
                        extra = await dev.get_system_status() if read_status else (await dev._send_command({"comhead": "get system status"}) if raw_cmd else None)
                        return ok, dev.connected, dev.host, dev._url(), dev._last_error or "", extra
                    finally:
                        await dev.disconnect()

                monkeypatch.setattr(loop, "getaddrinfo", _controlled_getaddrinfo)
                yield {"owned_ip": owned_ip, "owned_iface": owned_iface, "https_port": https_port, "telnet_port": telnet_port, "client_hellos": client_hellos, "http_requests": http_requests, "dns_queries": dns_queries, "dns_map": dns_map, "run_client": _run_client}
            finally:
                https_srv.close()
                telnet_srv.close()
                for active in list(active_writers):
                    await _finish_writer(active)
                await asyncio.gather(https_srv.wait_closed(), telnet_srv.wait_closed())

        yield {"pki_dir": pki_dir, "trusted_ca_pem": trusted_ca_pem, "corrupt_ca_pem": corrupt_ca_pem, "pinned_hex_sha256": pinned_digest.hex(), "pinned_colon_sha256": ":".join(f"{b:02x}" for b in pinned_digest), "open_endpoint": open_endpoint}
    finally:
        shutil.rmtree(pki_dir, ignore_errors=True)


def test_real_tls_prerequisite_guard_fails_closed_before_network_contact(monkeypatch, tmp_path):
    import os
    import sys
    import traceback
    from collections.abc import Callable
    from pathlib import Path
    from types import SimpleNamespace
    from typing import NamedTuple

    class _FailureCase(NamedTuple):
        name: str
        category: str
        env: dict[str, str]
        patch_fn: Callable[[object], None] | None = None
        forward_only: bool = False

    sock_spy = MagicMock(side_effect=AssertionError("socket creation attempted"))
    monkeypatch.setattr(socket, "socket", sock_spy)
    assert len(set(_TLS_PREREQ_DIAGNOSTICS.values())) == len(_TLS_PREREQ_DIAGNOSTICS)
    assert _TLS_QA_PKI_MAX_BYTES == 262_144
    assert _TLS_QA_LOG_MAX_BYTES == 5 * 1024 * 1024
    assert _TLS_QA_ROOT_MAX_BYTES == 20 * 1024 * 1024

    sentinel_tag = "sntl" + "94d2"
    root_dir = tmp_path.resolve()
    owned_ipv4 = "192.0.2.42"
    owned_ipv6 = "fd00::42"
    unassigned_ipv4 = "198.51.100.77"
    public_ipv4 = "203.0.114.55"
    owned_iface = f"eth-{sentinel_tag}"
    loopback_iface = f"loopback-{sentinel_tag}"
    secret_token = f"oserr-{sentinel_tag}"
    fake_repo = root_dir / f"repo-{sentinel_tag}"
    qa_root = root_dir / f"qaroot-{sentinel_tag}"
    missing_root = root_dir / f"miss-{sentinel_tag}"
    fake_file = fake_repo / "tests" / "test_security_ssrf_tls.py"
    build_sub = fake_repo / "build" / f"sub-{sentinel_tag}"
    child_file = qa_root / f"child-{sentinel_tag}.log"
    sub_dir = qa_root / f"dir-{sentinel_tag}"
    for directory in (fake_file.parent, fake_repo / "src", build_sub, sub_dir):
        directory.mkdir(parents=True)
    fake_file.write_bytes(b"x")
    child_file.write_bytes(b"x" * 20)

    addrs = {
        owned_iface: [
            SimpleNamespace(family=socket.AF_INET, address=owned_ipv4),
            SimpleNamespace(family=socket.AF_INET6, address=f"{owned_ipv6}%{owned_iface}"),
            SimpleNamespace(family=socket.AF_INET, address=public_ipv4),
            SimpleNamespace(family=socket.AF_INET, address=f"bad-{sentinel_tag}"),
        ]
    }
    stats = {owned_iface: SimpleNamespace(isup=True)}
    synth_env: dict[str, str] = {}
    forbidden_tokens = (
        sentinel_tag, owned_ipv4, owned_ipv6, unassigned_ipv4,
        public_ipv4, str(tmp_path), str(root_dir), root_dir.as_posix(),
    )
    default_psutil = SimpleNamespace(net_if_addrs=lambda: addrs, net_if_stats=lambda: stats)
    monkeypatch.setattr(os, "environ", synth_env)
    monkeypatch.setitem(sys.modules, "psutil", default_psutil)
    monkeypatch.setitem(globals(), "__file__", str(fake_file))

    with pytest.raises(BaseException) as skip_info:
        _forward_real_tls_qa_prereqs()
    assert type(skip_info.value).__name__ == "Skipped"
    assert skip_info.value.__cause__ is None
    assert skip_info.value.__context__ is None
    assert _validate_real_tls_qa_prereqs() is None

    base_env = {
        "OREI_TLS_QA_OWNED": "1",
        "OREI_TLS_QA_INTERFACE": owned_iface,
        "OREI_TLS_QA_BIND_IP": owned_ipv4,
        "OREI_TLS_QA_ROOT": str(qa_root),
    }

    def _env(**overrides: str) -> dict[str, str]:
        return {**base_env, **overrides}

    explicit = _validate_real_tls_qa_prereqs(env=base_env, if_addrs=addrs, if_stats=stats, repo_root=fake_repo)
    assert explicit == (ipaddress.ip_address(owned_ipv4), owned_iface, qa_root)

    for valid_ip, valid_root in ((owned_ipv4, qa_root), (owned_ipv6, build_sub)):
        synth_env.update(_env(OREI_TLS_QA_BIND_IP=valid_ip, OREI_TLS_QA_ROOT=str(valid_root)))
        synth_env["ALLOW_PUBLIC_MATRIX_HOST"] = "true"
        assert _forward_real_tls_qa_prereqs() == (ipaddress.ip_address(valid_ip), owned_iface, valid_root)

    orig_is_symlink = Path.is_symlink
    orig_resolve = Path.resolve
    orig_stat = Path.stat
    orig_scandir = os.scandir
    chained_raw = RuntimeError(f"raw-{secret_token}")
    chained_raw.__cause__ = ValueError(f"cause-{sentinel_tag}")

    def _patch_iface_down(mp) -> None:
        down_stats = {owned_iface: SimpleNamespace(isup=False)}
        down_psutil = SimpleNamespace(net_if_addrs=lambda: addrs, net_if_stats=lambda: down_stats)
        mp.setitem(sys.modules, "psutil", down_psutil)

    def _patch_iface_addrs_oserror(mp) -> None:
        failing_addrs = MagicMock(side_effect=OSError(13, "denied", secret_token))
        broken_psutil = SimpleNamespace(net_if_addrs=failing_addrs, net_if_stats=lambda: stats)
        mp.setitem(sys.modules, "psutil", broken_psutil)

    def _install_child_symlink(mp, resolve_child: Callable[[], Path]) -> None:
        def _is_symlink(path_obj: Path) -> bool:
            return True if path_obj.name == child_file.name else orig_is_symlink(path_obj)

        def _resolve(path_obj: Path, *args: object, **kwargs: object) -> Path:
            if path_obj.name == child_file.name:
                return resolve_child()
            return orig_resolve(path_obj, *args, **kwargs)

        mp.setattr(Path, "is_symlink", _is_symlink)
        mp.setattr(Path, "resolve", _resolve)

    def _patch_escaping_symlink(mp) -> None:
        _install_child_symlink(mp, lambda: fake_file)

    def _patch_broken_symlink(mp) -> None:
        def _raise_missing() -> Path:
            raise FileNotFoundError(2, "missing", str(missing_root))

        _install_child_symlink(mp, _raise_missing)

    def _patch_looping_symlink(mp) -> None:
        def _raise_loop() -> Path:
            raise RuntimeError(f"Symlink loop from {child_file}")

        _install_child_symlink(mp, _raise_loop)

    def _patch_scandir_permission_error(mp) -> None:
        def _failing_scandir(directory):
            if Path(directory).name == sub_dir.name:
                raise PermissionError(13, "denied", str(sub_dir))
            return orig_scandir(directory)

        mp.setattr(os, "scandir", _failing_scandir)

    def _patch_stat_permission_error(mp) -> None:
        def _failing_stat(path_obj: Path, *args: object, **kwargs: object):
            if path_obj.name == child_file.name:
                raise PermissionError(13, "denied", str(child_file))
            return orig_stat(path_obj, *args, **kwargs)

        mp.setattr(Path, "stat", _failing_stat)

    def _patch_log_budget_cap(mp) -> None:
        mp.setattr(sys.modules[__name__], "_TLS_QA_LOG_MAX_BYTES", 10)

    def _patch_root_budget_cap(mp) -> None:
        mp.setattr(sys.modules[__name__], "_TLS_QA_ROOT_MAX_BYTES", 10)

    def _patch_broken_environ_get(mp) -> None:
        broken_env = SimpleNamespace(get=MagicMock(side_effect=RuntimeError(f"env-{secret_token}")))
        mp.setattr(os, "environ", broken_env)

    def _patch_chained_validator(mp) -> None:
        failing_validator = MagicMock(side_effect=chained_raw)
        mp.setattr(sys.modules[__name__], "_validate_real_tls_qa_prereqs", failing_validator)

    failure_cases = [
        _FailureCase("require_without_qa_vars", "prereq_incomplete", {"OREI_REQUIRE_REAL_TLS": "1"}),
        _FailureCase("blank_interface", "prereq_incomplete", _env(OREI_TLS_QA_INTERFACE="")),
        _FailureCase("bad_require_token", "prereq_incomplete", _env(OREI_REQUIRE_REAL_TLS=f"bad-{sentinel_tag}")),
        _FailureCase("ownership_zero", "ownership_unattested", _env(OREI_TLS_QA_OWNED="0")),
        _FailureCase("bind_ip_zone_id", "bind_ip_zone", _env(OREI_TLS_QA_BIND_IP=f"{owned_ipv4}%{owned_iface}")),
        _FailureCase("bind_ip_hostname", "bind_ip_literal", _env(OREI_TLS_QA_BIND_IP=f"host-{sentinel_tag}.lan")),
        _FailureCase("bind_ip_unassigned", "bind_ip_unassigned", _env(OREI_TLS_QA_BIND_IP=unassigned_ipv4)),
        _FailureCase("bind_ipv4_loopback", "bind_ip_policy", _env(OREI_TLS_QA_BIND_IP="127.0.0.1")),
        _FailureCase("bind_ipv6_loopback", "bind_ip_policy", _env(OREI_TLS_QA_BIND_IP="::1")),
        _FailureCase("bind_ipv4_mapped_v6", "bind_ip_policy", _env(OREI_TLS_QA_BIND_IP=f"::ffff:{owned_ipv4}")),
        _FailureCase("bind_ipv4_link_local", "bind_ip_policy", _env(OREI_TLS_QA_BIND_IP="169.254.1.10")),
        _FailureCase("bind_ipv6_link_local", "bind_ip_policy", _env(OREI_TLS_QA_BIND_IP="fe80::1")),
        _FailureCase("bind_ipv4_unspecified", "bind_ip_policy", _env(OREI_TLS_QA_BIND_IP="0.0.0.0")),
        _FailureCase("bind_ipv4_multicast", "bind_ip_policy", _env(OREI_TLS_QA_BIND_IP="224.0.0.1")),
        _FailureCase("bind_ipv6_doc_range", "bind_ip_policy", _env(OREI_TLS_QA_BIND_IP="2001:db8::1")),
        _FailureCase("bind_public_ipv4", "bind_ip_policy", _env(OREI_TLS_QA_BIND_IP=public_ipv4)),
        _FailureCase("iface_lo_literal", "iface_loopback", _env(OREI_TLS_QA_INTERFACE="lo")),
        _FailureCase("iface_loopback_named", "iface_loopback", _env(OREI_TLS_QA_INTERFACE=loopback_iface)),
        _FailureCase("iface_missing", "iface_unavailable", _env(OREI_TLS_QA_INTERFACE=f"miss-{sentinel_tag}")),
        _FailureCase("qa_root_missing", "qa_root_invalid", _env(OREI_TLS_QA_ROOT=str(missing_root))),
        _FailureCase("qa_root_regular_file", "qa_root_invalid", _env(OREI_TLS_QA_ROOT=str(fake_file))),
        _FailureCase("qa_root_nul_byte", "qa_root_invalid", _env(OREI_TLS_QA_ROOT=f"{qa_root}\x00{secret_token}")),
        _FailureCase("qa_root_repo_checkout", "qa_root_overlap", _env(OREI_TLS_QA_ROOT=str(fake_repo))),
        _FailureCase("qa_root_top_build_dir", "qa_root_overlap", _env(OREI_TLS_QA_ROOT=str(fake_repo / "build"))),
        _FailureCase("qa_root_repo_src_dir", "qa_root_overlap", _env(OREI_TLS_QA_ROOT=str(fake_repo / "src"))),
        _FailureCase("qa_root_contains_repo", "qa_root_overlap", _env(OREI_TLS_QA_ROOT=str(root_dir))),
        _FailureCase("iface_link_down", "iface_unavailable", base_env, _patch_iface_down),
        _FailureCase("iface_addrs_oserror", "iface_unavailable", base_env, _patch_iface_addrs_oserror),
        _FailureCase("qa_root_symlink_escape", "qa_root_symlink", base_env, _patch_escaping_symlink),
        _FailureCase("qa_root_symlink_broken", "qa_root_symlink", base_env, _patch_broken_symlink),
        _FailureCase("qa_root_symlink_loop", "qa_root_symlink", base_env, _patch_looping_symlink),
        _FailureCase("qa_root_scandir_denied", "qa_root_io", base_env, _patch_scandir_permission_error),
        _FailureCase("qa_root_stat_denied", "qa_root_io", base_env, _patch_stat_permission_error),
        _FailureCase("qa_root_log_budget", "qa_root_budget", base_env, _patch_log_budget_cap),
        _FailureCase("qa_root_total_budget", "qa_root_budget", base_env, _patch_root_budget_cap),
        _FailureCase("environ_get_error", "prereq_unexpected", base_env, _patch_broken_environ_get),
        _FailureCase("forwarder_chained_error", "prereq_unexpected", base_env, _patch_chained_validator, True),
    ]

    for case in failure_cases:
        expected_msg = _TLS_PREREQ_DIAGNOSTICS[case.category]
        with monkeypatch.context() as mp:
            mp.setattr(os, "environ", {**case.env, "ALLOW_PUBLIC_MATRIX_HOST": "true"})
            if case.patch_fn is not None:
                case.patch_fn(mp)

            invocations: list[tuple[Callable[[], object], type[BaseException], bool]] = []
            if not case.forward_only:
                invocations.append((_validate_real_tls_qa_prereqs, RuntimeError, False))
            invocations.append((_forward_real_tls_qa_prereqs, BaseException, True))

            for fn_call, expected_exc, is_forwarder in invocations:
                with pytest.raises(expected_exc) as exc_info:
                    fn_call()
                exc_value = exc_info.value
                if is_forwarder:
                    assert type(exc_value).__name__ == "Failed", case.name
                    assert getattr(exc_value, "pytrace", None) is False, case.name
                else:
                    assert type(exc_value) is RuntimeError, case.name
                    assert exc_value.args == (expected_msg,), case.name
                assert str(exc_value) == expected_msg, case.name
                assert exc_value.__cause__ is None, case.name
                assert exc_value.__context__ is None, case.name

                inner_tb = exc_value.__traceback__.tb_next if exc_value.__traceback__ is not None else None
                frame_locals = [repr(frame.f_locals) for frame, _lineno in traceback.walk_tb(inner_tb)]
                diagnostic_surface = " ".join([str(exc_value), repr(exc_value), *frame_locals])
                for token in forbidden_tokens:
                    assert token not in diagnostic_surface, case.name

    assert len({case.name for case in failure_cases}) == len(failure_cases)
    assert {case.category for case in failure_cases} == set(_TLS_PREREQ_DIAGNOSTICS)
    assert sock_spy.call_count == 0


@pytest.mark.asyncio
async def test_real_tls_trusted_ca_matching_hostname_preserves_validator_sni_and_url(real_tls_qa_harness, monkeypatch):
    for key in _TLS_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    for k, v in (("OREI_VERIFY_SSL", "false"), ("MATRIX_CA_CERT", str(real_tls_qa_harness["trusted_ca_pem"]))):
        monkeypatch.setenv(k, v)
    async with real_tls_qa_harness["open_endpoint"]("valid", monkeypatch) as ep:
        ep["dns_map"]["matrix.lan"] = [str(ep["owned_ip"]), "127.0.0.1"]
        ok, connected, _, _, _, _ = await ep["run_client"]()
        assert (ok, connected, ep["client_hellos"], ep["http_requests"]) == (False, False, [], [])
        ep["dns_map"]["matrix.lan"] = [str(ep["owned_ip"])]
        ep["dns_queries"].clear()
        ok, connected, host, url, _, status = await ep["run_client"](read_status=True)
        assert (ok, connected, host, url) == (True, True, "matrix.lan", f"https://matrix.lan:{ep['https_port']}/cgi-bin/instr")
        assert status is not None and status["power"] == 1 and ep["client_hellos"] == ["matrix.lan", "matrix.lan"]
        assert [req["comhead"] for req in ep["http_requests"]] == ["login", "get system status"]
        for req in ep["http_requests"]:
            assert (req["path"], req["host"], req["peer_ip"]) == ("/cgi-bin/instr", f"matrix.lan:{ep['https_port']}", str(ep["owned_ip"]))
            assert str(req["tls_version"]).startswith("TLSv1.")
        assert ("matrix.lan", ep["https_port"]) in ep["dns_queries"]


@pytest.mark.asyncio
async def test_real_tls_untrusted_chain_and_wrong_hostname_reach_tls_and_fail_closed(real_tls_qa_harness, monkeypatch):
    for key in _TLS_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    async with real_tls_qa_harness["open_endpoint"]("untrusted_chain", monkeypatch) as ep:
        for k, v in (("OREI_VERIFY_SSL", "false"), ("MATRIX_CA_CERT", str(real_tls_qa_harness["trusted_ca_pem"]))):
            monkeypatch.setenv(k, v)
        ok, connected, _, _, err, _ = await ep["run_client"](password="no-leak")
        assert (ok, connected, ep["client_hellos"], ep["http_requests"]) == (False, False, ["matrix.lan"], [])
        assert "certificate verify failed" in err.lower() and any(k in err.lower() for k in ("self-signed", "self signed", "issuer", "untrusted"))
        monkeypatch.delenv("MATRIX_CA_CERT", raising=False)
        monkeypatch.setenv("OREI_VERIFY_SSL", "true")
        ok, connected, _, _, err, cmd_res = await ep["run_client"](password="no-leak", raw_cmd=True)
        assert (ok, connected, cmd_res, ep["http_requests"]) == (False, False, (False, None), [])
        assert ep["client_hellos"] == ["matrix.lan"] * 3 and "certificate verify failed" in err.lower()
    async with real_tls_qa_harness["open_endpoint"]("wrong_name", monkeypatch) as ep:
        for k, v in (("OREI_VERIFY_SSL", "false"), ("MATRIX_CA_CERT", str(real_tls_qa_harness["trusted_ca_pem"]))):
            monkeypatch.setenv(k, v)
        ok, connected, _, _, err, _ = await ep["run_client"](password="no-leak")
        assert (ok, connected, ep["client_hellos"], ep["http_requests"]) == (False, False, ["matrix.lan"], [])
        assert "certificate verify failed" in err.lower() and any(k in err.lower() for k in ("hostname", "not valid for"))


@pytest.mark.asyncio
async def test_real_tls_fingerprint_pinning_precedence_and_no_invented_ca_or_name_checks(real_tls_qa_harness, monkeypatch):
    for key in _TLS_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    async with real_tls_qa_harness["open_endpoint"]("pinned_selfsigned", monkeypatch) as ep:
        for fp_value, verify_flag, ca_value in (
            (real_tls_qa_harness["pinned_colon_sha256"], "false", str(real_tls_qa_harness["corrupt_ca_pem"])),
            (real_tls_qa_harness["pinned_hex_sha256"], "true", str(real_tls_qa_harness["pki_dir"] / "missing-ca.pem")),
        ):
            for k, v in (("MATRIX_TLS_FINGERPRINT", fp_value), ("OREI_VERIFY_SSL", verify_flag), ("MATRIX_CA_CERT", ca_value)):
                monkeypatch.setenv(k, v)
            ok, connected, _, _, _, _ = await ep["run_client"](password="pin-secret")
            assert (ok, connected, ep["client_hellos"][-1], ep["http_requests"][-1]["host"]) == (True, True, "matrix.lan", f"matrix.lan:{ep['https_port']}")
        monkeypatch.delenv("MATRIX_CA_CERT", raising=False)
        for k, v in (("OREI_VERIFY_SSL", "false"), ("MATRIX_TLS_FINGERPRINT", "58" * 32)):
            monkeypatch.setenv(k, v)
        ok, connected, _, _, err, _ = await ep["run_client"](password="no-leak")
        assert (ok, connected, len(ep["client_hellos"]), len(ep["http_requests"])) == (False, False, 3, 2)
        assert any(token in err for token in ("X" * 16, "58" * 16, "Fingerprint", "fingerprint"))
    async with real_tls_qa_harness["open_endpoint"]("valid", monkeypatch) as ep:
        for k, v in (("MATRIX_CA_CERT", str(real_tls_qa_harness["trusted_ca_pem"])), ("OREI_VERIFY_SSL", "false"), ("MATRIX_TLS_FINGERPRINT", "58" * 32)):
            monkeypatch.setenv(k, v)
        ok, connected, _, _, err, _ = await ep["run_client"](password="no-leak")
        assert (ok, connected, ep["client_hellos"], ep["http_requests"]) == (False, False, ["matrix.lan"], [])
        assert any(token in err for token in ("X" * 16, "58" * 16, "Fingerprint", "fingerprint"))
        ep["client_hellos"].clear()
        monkeypatch.setenv("MATRIX_TLS_FINGERPRINT", "invalid-digest")
        ok, connected, _, _, err, _ = await ep["run_client"](password="no-leak")
        assert (ok, connected, ep["client_hellos"], ep["http_requests"]) == (False, False, [], []) and "sha-256 fingerprint" in err.lower()
        monkeypatch.delenv("MATRIX_TLS_FINGERPRINT", raising=False)
        monkeypatch.setenv("MATRIX_CA_CERT", str(real_tls_qa_harness["corrupt_ca_pem"]))
        ok, connected, _, _, err, _ = await ep["run_client"](password="no-leak")
        assert (ok, connected, ep["client_hellos"], ep["http_requests"]) == (False, False, [], []) and err != ""


@pytest.mark.asyncio
async def test_simulator_loopback_registration_is_exact_port_and_never_weakens_defaults(monkeypatch):
    import telnet_client

    monkeypatch.delenv("ALLOW_PUBLIC_MATRIX_HOST", raising=False)
    monkeypatch.delenv("OREI_SIMULATOR_LOOPBACK_PORTS", raising=False)

    # Default production policy blocks loopback on both HTTP and Telnet.
    with pytest.raises(ValueError, match="Disallowed matrix destination address"):
        telnet_client.validate_matrix_target_syntax("127.0.0.1", 54321)
    with pytest.raises(ValueError, match="Disallowed matrix destination address"):
        telnet_client.validate_matrix_target_syntax("::1", 54321)

    # Registering one exact simulator port permits ONLY canonical 127.0.0.1 / ::1 on that port.
    telnet_client.register_simulator_loopback_port(54321)
    try:
        assert telnet_client.validate_matrix_target_syntax("127.0.0.1", 54321) == ipaddress.IPv4Address("127.0.0.1")
        assert telnet_client.validate_matrix_target_syntax("::1", 54321) == ipaddress.IPv6Address("::1")
        # Other ports, non-canonical loopback, mapped IPv6, and REST settings remain blocked.
        for bad_host, bad_port in (
            ("127.0.0.1", 443),
            ("127.0.0.1", 54322),
            ("127.0.0.2", 54321),
            ("::ffff:127.0.0.1", 54321),
            ("169.254.169.254", 54321),
        ):
            with pytest.raises(ValueError, match="Disallowed matrix destination address"):
                telnet_client.validate_matrix_target_syntax(bad_host, bad_port)
        assert not telnet_client.is_permitted_matrix_ip(ipaddress.IPv4Address("127.0.0.1"))
        assert not await settings._is_safe_host("127.0.0.1", 54321)
        assert not await settings._is_safe_host("localhost", 54321)

        # DNS rebinding of non-localhost hostnames to 127.0.0.1 stays blocked even on the registered port.
        loop = asyncio.get_running_loop()

        async def fake_getaddrinfo(host, port, **_kwargs):
            return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("127.0.0.1", port))]

        monkeypatch.setattr(loop, "getaddrinfo", fake_getaddrinfo)
        with pytest.raises(OSError, match="Disallowed matrix destination address"):
            await telnet_client.resolve_matrix_endpoints("matrix.lan", 54321)
        assert await telnet_client.resolve_matrix_endpoints("localhost", 54321) == [ipaddress.IPv4Address("127.0.0.1")]
        with pytest.raises(OSError, match="Disallowed matrix destination address"):
            await telnet_client.resolve_matrix_endpoints("localhost", 443)
    finally:
        telnet_client.unregister_simulator_loopback_port(54321)

    # Unregistering restores full default blocking.
    with pytest.raises(ValueError, match="Disallowed matrix destination address"):
        telnet_client.validate_matrix_target_syntax("127.0.0.1", 54321)
