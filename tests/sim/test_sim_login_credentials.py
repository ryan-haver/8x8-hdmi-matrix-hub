"""Per-matrix login credentials and why a login failed (WP-B3: UC-02 short term, UC-05 specific setup errors).

A real ``OreiMatrix`` against the simulator. The Remote's setup gives a new
matrix address its own login; the environment's (``OREI_USER`` /
``OREI_PASSWORD``) is used only for a matrix created without one.
"""

from __future__ import annotations

import socket
from unittest.mock import AsyncMock

import orei_matrix
from tools.validate.stack import free_port


def _matrix(sim, **login) -> orei_matrix.OreiMatrix:
    m = orei_matrix.OreiMatrix("127.0.0.1", port=sim.https_port, use_https=sim.tls, **login)
    m._connect_telnet = AsyncMock(return_value=False)  # HTTP only: connect() is instant
    return m


def _login_log(sim) -> list[dict]:
    return [e for e in sim.log if e.get("command") == "login"]


async def test_own_credentials_are_sent_instead_of_the_environments(fast_hub, monkeypatch) -> None:
    fast_hub.state.auth = {"user": "Admin", "password": "own-login"}
    monkeypatch.setenv("OREI_PASSWORD", "environment-login")
    m = _matrix(fast_hub, user="Admin", password="own-login")
    try:
        assert m.has_own_credentials
        assert await m.connect()
        assert m.login_failure is None
        assert [e["login_ok"] for e in _login_log(fast_hub)] == [True]
    finally:
        await m.disconnect()


async def test_without_own_credentials_the_environment_is_used(fast_hub, monkeypatch) -> None:
    fast_hub.state.auth = {"user": "Admin", "password": "environment-login"}
    monkeypatch.setenv("OREI_PASSWORD", "environment-login")
    m = _matrix(fast_hub)
    try:
        assert not m.has_own_credentials
        assert m.credentials() == ("Admin", "environment-login")
        assert await m.connect()
    finally:
        await m.disconnect()


async def test_a_rejected_login_is_reported_as_auth(fast_hub) -> None:
    m = _matrix(fast_hub, user="Admin", password="wrong")
    try:
        assert not await m.connect()
        assert m.login_failure == "auth"
        assert [e["login_ok"] for e in _login_log(fast_hub)] == [False]
    finally:
        await m.disconnect()


async def test_no_connection_is_reported_as_refused_and_a_bad_name_as_not_found(monkeypatch) -> None:
    # The name must fail to resolve at once: real DNS for a `.invalid` name can take longer than the
    # login timeout on some networks (11 s seen on Windows), which reads as "timeout" (TST-17).
    real_getaddrinfo = socket.getaddrinfo

    def getaddrinfo(host, *args, **kwargs):
        if host == "no-such-matrix.invalid":
            raise socket.gaierror(socket.EAI_NONAME, "Name or service not known")
        return real_getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", getaddrinfo)
    refused = orei_matrix.OreiMatrix("127.0.0.1", port=free_port(), user="Admin", password="x")
    unknown = orei_matrix.OreiMatrix("no-such-matrix.invalid", port=443, user="Admin", password="x")
    try:
        assert not await refused.connect()
        assert refused.login_failure == "refused"
        assert not await unknown.connect()
        assert unknown.login_failure == "not_found"
    finally:
        await refused.disconnect()
        await unknown.disconnect()


def test_failure_kinds_from_transport_errors() -> None:
    kind = orei_matrix._login_failure_kind
    result = orei_matrix._HttpResult
    assert kind(result("transport", error="Cannot connect to host x:443 ssl:False [getaddrinfo failed]")) == "not_found"
    assert kind(result("transport", error="Cannot connect to host 1.2.3.4:443 [Connect call failed]")) == "refused"
    assert kind(result("auth", error="HTTP 401")) == "auth"
    assert kind(result("bad_response", error="Unparseable")) == "other"
