"""WP-F1: real REST/matrix simulator contracts, TLS and scripted UC setup.

Despite the filename these API cases prove V2; the UC protocol case exercises
the shipped driver as a real client. Strict xfails identify source gaps that
cannot be fixed under this work package's two-file ownership constraint.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
import shutil
import ssl
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from yarl import URL

import orei_matrix
import password
from orei_matrix import OreiMatrix, _matrix_tls_policy
from rest_api import create_rest_app, scenes_v2, set_matrix_device, utils
from rest_api import static as static_module
from rest_api.runtime import RUNTIME_MONITOR_KEY
from tests.validation.scenarios.security_hardening import NEW_PIN, PIN, SCENARIOS
from tools.simulator import DeviceState, Simulator
from tools.simulator.tls import generate_self_signed
from tools.uc_remote_sim import UcRemoteSim
from tools.validate.clients.api import ApiClient
from tools.validate.clients.base import HubInfo
from tools.validate.model import DeviceUnchanged, Hub, NoCommand, Response, resolve
from tools.validate.runner import _subset
from tools.validate.scenarios import discover
from tools.validate.stack import HubProcess

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/e2e/fixtures/data"
KINDS = ("profile", "scene")


@pytest.fixture(autouse=True)
def security_environment(monkeypatch):
    # Never inherit local deployment secrets, TLS policy, or proxy settings.
    for key in ("MATRIX_CA_CERT", "MATRIX_TLS_FINGERPRINT", "OREI_VERIFY_SSL", "OREI_USER", "OREI_PASSWORD",
                "ADMIN_PIN", "CONTROL_PIN", "UC_AUTH_TOKEN", "ALLOWED_HOSTS", "CORS_ALLOWED_ORIGINS"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    monkeypatch.setattr(utils, "TRUST_PROXY_HEADERS", False)
    password.reset_pin_lockout()
    yield
    password.reset_pin_lockout()


@pytest.fixture
async def simulator():
    async with Simulator(DeviceState.default(), https_port=0, telnet_port=0, control_port=0) as sim:
        yield sim


@pytest.fixture
async def hub(aiohttp_client, simulator, tmp_path, monkeypatch):
    shutil.copytree(FIXTURES, tmp_path, dirs_exist_ok=True)
    matrix = OreiMatrix("127.0.0.1", port=simulator.https_port)
    # These contracts concern HTTP/PIN/TLS, so avoid the unrelated Telnet startup.
    monkeypatch.setattr(matrix, "_connect_telnet", AsyncMock(return_value=False))
    try:
        assert await matrix._connect_once()
        set_matrix_device(matrix, config_dir=str(tmp_path), data_dir=tmp_path)
        app = create_rest_app(data_dir=tmp_path)
        app[RUNTIME_MONITOR_KEY].interval = 0.01
        client = await aiohttp_client(app)
        yield client, matrix, simulator, tmp_path
    finally:
        await matrix.disconnect()


def _assert_no_hash(value):
    if isinstance(value, dict):
        assert "passcode_hash" not in value
        for child in value.values():
            _assert_no_hash(child)
    elif isinstance(value, list):
        for child in value:
            _assert_no_hash(child)


def _assert_no_device_writes(sim, cursor):
    writes = [entry for entry in list(sim.log)[cursor:]
              if entry.get("channel") in ("http", "telnet") and entry.get("mutated")]
    assert not writes, writes


@asynccontextmanager
async def protected_item(client, kind):
    """Capture server-generated scene IDs and always delete with the current PIN."""
    if kind == "profile":
        response = await client.post("/api/profile", json={
            "id": "validation_security_dynamic", "name": "PIN integration", "passcode": PIN,
            "outputs": {"1": {"input": 2}},
        })
        assert response.status == 200
        item = (await response.json())["data"]
        path = f"/api/profile/{item['id']}"
    else:
        response = await client.post("/api/v2/scenes", json={
            "name": "PIN integration", "passcode": PIN, "steps": [{"type": "wait", "params": {"seconds": 0.5}}],
        })
        assert response.status == 201, await response.text()
        item = (await response.json())["data"]["scene"]
        path = f"/api/v2/scenes/{item['id']}"
    resource = {"path": path, "id": item["id"], "pin": PIN, "created": item}
    try:
        yield resource
    finally:
        # A successful delete inside a case is idempotent at cleanup (404).
        response = await client.delete(path, json={"current_passcode": resource["pin"]})
        assert response.status in (200, 404), await response.text()
        assert (await client.get(path)).status == 404


def test_discovery_loads_security_hardening_without_duplicate_ids():
    found = discover()
    loaded = {key: value for key, value in found.items() if key.startswith("security_hardening.")}
    assert len(loaded) == len(SCENARIOS) > 0
    assert loaded == {scenario.id: scenario for scenario in SCENARIOS}
    assert {feature for scenario in SCENARIOS for feature in scenario.features} == {
        "F-SEC-004", "F-SEC-005", "F-SEC-006", "F-SEC-007", "F-SEC-010", "F-SEC-011",
    }
    for scenario in SCENARIOS:
        assert scenario.clients == ("api",)
        assert scenario.findings == ()
        if scenario.setup:
            assert scenario.cleanup, scenario.id


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda scenario: scenario.id)
async def test_declarative_scenarios_against_simulator(hub, scenario):
    client, _, sim, _ = hub
    api = ApiClient()
    await api.start(HubInfo(str(client.make_url("/"))))
    before_scene = (await (await client.get("/api/v2/scenes/scene_goodnight01")).json())["data"]["scene"]
    created_profiles = set()
    try:
        for step in scenario.setup:
            result = await api.perform(step)
            assert result.ok, result
            if step.params.get("path") == "/api/profile":
                created_profiles.add(step.params["json"]["id"])
        before = sim.state.to_dict()
        cursor = len(sim.log)
        result = await api.perform(scenario.action)
        assert result.error is None
        _assert_no_hash(result.body)
        for expected in scenario.expect:
            if isinstance(expected, Response):
                statuses = expected.status if isinstance(expected.status, tuple) else (expected.status,)
                assert result.status in statuses, result
                if expected.json:
                    assert _subset(expected.json, result.body), result.body
            elif isinstance(expected, Hub):
                status, body, _ = await api.request("GET", expected.path)
                assert status == expected.status
                assert resolve(body, expected.field_path) == expected.equals
                _assert_no_hash(body)
            elif isinstance(expected, DeviceUnchanged):
                assert sim.state.to_dict() == before
            elif isinstance(expected, NoCommand):
                _assert_no_device_writes(sim, cursor)
            else:
                pytest.fail(f"Unexercised expectation: {expected}")
    finally:
        try:
            for step in scenario.cleanup:
                result = await api.perform(step)
                assert result.status in (200, 404), result
        finally:
            await api.stop()
    for profile_id in created_profiles:
        assert (await client.get(f"/api/profile/{profile_id}")).status == 404
    after_scene = (await (await client.get("/api/v2/scenes/scene_goodnight01")).json())["data"]["scene"]
    assert after_scene == before_scene


async def test_scenario_cleanup_runs_when_an_assertion_fails(hub):
    """The generated-ID path releases its protected resource even on failure."""
    client, _, _, _ = hub
    for kind in KINDS:
        with pytest.raises(AssertionError, match="injected check failure"):
            async with protected_item(client, kind) as resource:
                raise AssertionError("injected check failure")
        assert (await client.get(resource["path"])).status == 404


@pytest.mark.parametrize("kind", KINDS)
async def test_created_pin_is_hashed_on_disk_and_never_exposed(hub, kind):
    """F-SEC-004/005: creation, detail and list use public serialization."""
    client, _, _, directory = hub
    async with protected_item(client, kind) as resource:
        detail = await (await client.get(resource["path"])).json()
        item = detail["data"] if kind == "profile" else detail["data"]["scene"]
        assert resource["created"]["password_protected"] is True
        assert item["password_protected"] is True
        _assert_no_hash(resource["created"])
        _assert_no_hash(detail)
        listing = await (await client.get("/api/profiles" if kind == "profile" else "/api/v2/scenes")).json()
        _assert_no_hash(listing)
        stored = json.loads((directory / ("profiles.json" if kind == "profile" else "scenes.json")).read_text(encoding="utf-8"))
        saved = next(item for item in stored["profiles" if kind == "profile" else "scenes"]
                     if item["id"] == resource["id"])
        encoded = saved["passcode_hash"]
        assert password.is_passcode_hash(encoded)
        algorithm, iterations, salt, digest = encoded.split("$")
        assert algorithm == "pbkdf2_sha256"
        assert int(iterations) == 1000
        assert len(bytes.fromhex(salt)) == 16
        assert len(bytes.fromhex(digest)) == 32
        assert encoded != PIN
        assert password.verify_passcode(PIN, encoded)
        assert not password.verify_passcode("9999", encoded)


async def test_profile_and_scene_hashes_use_independent_salts(hub):
    client, _, _, _ = hub
    async with protected_item(client, "profile") as profile, protected_item(client, "scene") as scene:
        profile_hash = utils.get_profile_manager().get_profile(profile["id"]).passcode_hash
        scene_hash = scenes_v2._get_scene_manager().get_scene(scene["id"]).passcode_hash
        assert profile_hash.split("$")[2] != scene_hash.split("$")[2]
        assert password.verify_passcode(PIN, profile_hash)
        assert password.verify_passcode(PIN, scene_hash)


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("operation", ["change", "remove", "delete"])
async def test_mutations_require_current_pin_and_succeed_with_it(hub, kind, operation):
    """F-SEC-006: rejected changes leave the saved hash intact."""
    client, _, sim, _ = hub
    async with protected_item(client, kind) as resource:
        path = resource["path"]
        manager = utils.get_profile_manager() if kind == "profile" else scenes_v2._get_scene_manager()
        getter = manager.get_profile if kind == "profile" else manager.get_scene
        original_hash = getter(resource["id"]).passcode_hash
        method = "DELETE" if operation == "delete" else "PUT"
        body = {"passcode": NEW_PIN} if operation == "change" else {"remove_passcode": True}
        if operation == "delete":
            body = {}
        before = sim.state.to_dict()
        cursor = len(sim.log)
        for extra, code in (({}, "passcode_required"), ({"current_passcode": "9999"}, "invalid_passcode")):
            response = await client.request(method, path, json={**body, **extra})
            assert response.status == 403
            assert (await response.json())["data"]["error"] == code
            assert getter(resource["id"]).passcode_hash == original_hash
            assert sim.state.to_dict() == before
            _assert_no_device_writes(sim, cursor)
        response = await client.request(method, path, json={**body, "current_passcode": PIN})
        assert response.status == 200, await response.text()
        _assert_no_hash(await response.json())
        if operation == "change":
            resource["pin"] = NEW_PIN
            assert password.verify_passcode(NEW_PIN, getter(resource["id"]).passcode_hash)
            assert not password.verify_passcode(PIN, getter(resource["id"]).passcode_hash)
        elif operation == "remove":
            assert not getter(resource["id"]).passcode_hash
            assert not getter(resource["id"]).password_protected
        else:
            assert (await client.get(path)).status == 404


@pytest.mark.parametrize("kind", KINDS)
async def test_wrong_pin_keeps_health_responsive_during_pbkdf2(hub, kind, monkeypatch):
    """F-SEC-007: hold the real verifier in its worker while health is served.

    The worker rendezvous proves health ran *during* verification. A synchronous
    regression times out the rendezvous and records a >100 ms loop stall.
    """
    client, _, sim, _ = hub
    async with protected_item(client, kind) as resource:
        entered, release = threading.Event(), threading.Event()
        verify = password.verify_passcode
        loop_thread = threading.get_ident()
        worker_threads = []

        def held_verify(*args):
            worker_threads.append(threading.get_ident())
            entered.set()
            assert release.wait(3), "PIN verification blocked the event loop"
            return verify(*args)

        monkeypatch.setattr(password, "verify_passcode", held_verify)
        await asyncio.sleep(0.03)
        suffix = "recall" if kind == "profile" else "execute"
        before = sim.state.to_dict()
        pending = asyncio.create_task(client.post(f"{resource['path']}/{suffix}", json={"passcode": "9999"}))
        try:
            assert await asyncio.to_thread(entered.wait, 2)
            response = await asyncio.wait_for(client.get("/api/health"), timeout=1)
            assert response.status == 200
            runtime = (await response.json())["data"]["runtime"]
            assert runtime["loop_lag_ms"] is not None
            assert runtime["loop_lag_ms"] < 100
            assert runtime["loop_lag_max_ms"] < 100
            assert not pending.done()
            assert worker_threads and loop_thread not in worker_threads
        finally:
            release.set()
            response = await pending
        assert response.status == 403
        assert (await response.json())["data"]["error"] == "invalid_passcode"
        assert sim.state.to_dict() == before


@pytest.mark.parametrize("kind", KINDS)
async def test_wrong_pin_lockout_is_per_item_and_expires(hub, kind, monkeypatch):
    """F-SEC-007: fifth failure locks, correct PIN cannot bypass, expiry resets."""
    client, _, _, _ = hub
    now = [100.0]
    tracker = password.PasscodeAttemptTracker(clock=lambda: now[0])
    monkeypatch.setattr(password, "_PIN_TRACKER", tracker)
    async with protected_item(client, kind) as resource:
        suffix = "recall" if kind == "profile" else "execute"
        path = f"{resource['path']}/{suffix}"
        try:
            for _ in range(password.MAX_PIN_FAILURES):
                response = await client.post(path, json={"passcode": "9999"})
                assert response.status == 403
                assert (await response.json())["data"]["error"] == "invalid_passcode"
            key = f"{kind}:{resource['id']}"
            assert tracker.failures(key) == 5
            assert tracker.check("profile:unrelated") == 0
            for pin in (PIN, "9999"):
                response = await client.post(path, json={"passcode": pin})
                assert response.status == 429
                assert int(response.headers["Retry-After"]) == 30
                assert (await response.json())["data"]["error"] == "passcode_locked"
            now[0] += 31
            # Authenticate a metadata/PIN update without applying device state.
            response = await client.put(resource["path"], json={"passcode": PIN, "current_passcode": PIN})
            assert response.status == 200
            assert tracker.failures(key) == 0
        finally:
            tracker.reset()


async def test_rate_limits_writes_without_starving_reads_or_health(hub, monkeypatch):
    """F-SEC-008/009: spoofed XFF cannot bypass a direct peer's budget."""
    client, _, sim, _ = hub
    monkeypatch.setattr(utils, "RATE_LIMIT_REQUESTS", 2)
    monkeypatch.setattr(utils, "RATE_LIMIT_READ_REQUESTS", 2)
    utils.reset_rate_limiter()
    before = sim.state.to_dict()
    for index in range(3):
        response = await client.post("/api/switch", json=[], headers={"X-Forwarded-For": f"198.51.100.{index + 1}"})
        assert response.status == (400 if index < 2 else 429)
    for index in range(3):
        response = await client.get("/api/info")
        assert response.status == (200 if index < 2 else 429)
    for _ in range(3):
        assert (await client.get("/api/health")).status == 200
    assert sim.state.to_dict() == before


@pytest.mark.parametrize(("enabled", "trusted", "peer", "forwarded", "expected"), [
    (False, "127.0.0.1", "127.0.0.1", "198.51.100.9", "127.0.0.1"),
    (True, "10.0.0.0/8", "192.0.2.1", "198.51.100.9", "192.0.2.1"),
    (True, "", "127.0.0.1", "198.51.100.9", "127.0.0.1"),
    (True, "10.0.0.0/8", "10.0.0.2", "198.51.100.9, 10.0.0.3", "198.51.100.9"),
    (True, "10.0.0.0/8", "10.0.0.2", "198.51.100.9, 192.0.2.8, 10.0.0.3", "192.0.2.8"),
    (True, "10.0.0.0/8", "10.0.0.2", "garbage", "10.0.0.2"),
])
def test_proxy_headers_only_trust_configured_peers(monkeypatch, enabled, trusted, peer, forwarded, expected):
    """F-SEC-009: choose the rightmost untrusted address, never the spoofed leftmost."""
    monkeypatch.setattr(utils, "TRUST_PROXY_HEADERS", enabled)
    monkeypatch.setenv("TRUSTED_PROXY_IPS", trusted)
    request = MagicMock(headers={"X-Forwarded-For": forwarded})
    request.transport.get_extra_info.return_value = (peer, 12345)
    assert utils._get_client_ip(request) == expected


@pytest.mark.parametrize("path", ["/css/..%5c..%5csecret.txt", "/assets/..%2f..%2fsecret.txt"])
async def test_encoded_traversal_cannot_read_existing_secret(hub, monkeypatch, tmp_path, path):
    """F-SEC-010: an existing out-of-root file makes this a meaningful denial."""
    client, _, _, _ = hub
    root = tmp_path / "web"
    (root / "css").mkdir(parents=True)
    (root / "assets").mkdir()
    (root / "css" / "safe.css").write_text("body {}", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("security-outside-root-sentinel", encoding="utf-8")
    monkeypatch.setattr(static_module, "_WEB_DIR", root)
    safe = await client.get("/css/safe.css")
    assert safe.status == 200
    assert await safe.text() == "body {}"
    response = await client.get(URL(path, encoded=True))
    assert response.status in (403, 404)
    assert "security-outside-root-sentinel" not in await response.text()


@pytest.mark.parametrize(("raw", "message"), [
    (b'{"input":', "Invalid JSON body"),
    (b'[]', "Request body must be a JSON object"),
    (b'{"input":1,"output":9}', "Output must be 1-8"),
])
async def test_validation_errors_are_generic(hub, raw, message):
    """F-SEC-011: parse/schema failures are bounded client messages."""
    client, _, sim, _ = hub
    before = sim.state.to_dict()
    response = await client.post("/api/switch", data=raw, headers={"Content-Type": "application/json"})
    assert response.status == 400
    body = await response.json()
    assert body["success"] is False
    assert body["error"] == message
    text = await response.text()
    assert not re.search(r"Traceback|File \"|[A-Z]:\\|/home/|/Users/|site-packages", text)
    assert sim.state.to_dict() == before


@pytest.mark.parametrize("raw", [b'{"input":', b'{"input":1,"output":9}'])
async def test_validation_errors_include_correlation_id(hub, raw):
    client, _, _, _ = hub
    response = await client.post("/api/switch", data=raw, headers={"Content-Type": "application/json"})
    assert response.status == 400
    body = await response.json()
    reference = body.get("error_id") or response.headers.get("X-Error-Id")
    assert isinstance(reference, str) and reference
    if body.get("error_id") and response.headers.get("X-Error-Id"):
        assert body["error_id"] == response.headers["X-Error-Id"]


async def test_internal_error_reference_links_to_log_without_disclosing_exception(hub, monkeypatch, caplog):
    """F-SEC-011: the existing 500 ref form remains safe and traceable."""
    client, matrix, _, _ = hub
    secret = r"failure at C:\private\matrix.json with password=private-error-password"
    monkeypatch.setattr(matrix, "get_status", AsyncMock(side_effect=RuntimeError(secret)))
    response = await client.get("/api/status")
    assert response.status == 500
    body = await response.json()
    match = re.fullmatch(r"Internal server error \(ref: ([0-9a-f]{8})\)", body["error"])
    assert match
    assert "private" not in await response.text()
    assert any(match[1] in record.getMessage() for record in caplog.records)


@pytest.mark.parametrize(("policy", "succeeds"), [
    ("default", True), ("verify", False), ("ca", True), ("pin", True), ("wrong_pin", False),
])
async def test_matrix_tls_handshake_verification_and_fingerprint(simulator, monkeypatch, policy, succeeds):
    """F-SEC-013: real HTTPS login accepts trusted certificates/pins and fails closed."""
    certificate, _ = generate_self_signed(("localhost", "127.0.0.1", simulator.host))
    if policy == "verify":
        monkeypatch.setenv("OREI_VERIFY_SSL", "true")
    elif policy == "ca":
        monkeypatch.setenv("MATRIX_CA_CERT", str(certificate))
    elif policy in ("pin", "wrong_pin"):
        der = ssl.PEM_cert_to_DER_cert(certificate.read_text())
        digest = hashlib.sha256(der).digest() if policy == "pin" else bytes(32)
        monkeypatch.setenv("MATRIX_TLS_FINGERPRINT", ":".join(f"{byte:02x}" for byte in digest))
        # Pinning takes precedence over the otherwise invalid CA path.
        monkeypatch.setenv("MATRIX_CA_CERT", str(certificate.parent / "missing.pem"))
    matrix = OreiMatrix("127.0.0.1", port=simulator.https_port)
    monkeypatch.setattr(matrix, "_connect_telnet", AsyncMock(return_value=False))
    try:
        assert await matrix._connect_once() is succeeds
        assert matrix.connected is succeeds
        logins = [entry for entry in simulator.log if entry.get("command") == "login"]
        assert bool(logins) is succeeds
    finally:
        await matrix.disconnect()


@pytest.mark.parametrize("value", ["invalid", "00" * 31, "gg" * 32, "00" * 33])
def test_invalid_fingerprint_is_rejected(monkeypatch, value):
    monkeypatch.setenv("MATRIX_TLS_FINGERPRINT", value)
    with pytest.raises(ValueError):
        _matrix_tls_policy()


@pytest.mark.parametrize("key", ["password", "passcode", "key", "auth_token"])
@pytest.mark.parametrize("style", ["structured", "json", "assignment"])
def test_log_filter_redacts_credentials_without_losing_safe_fields(caplog, key, style):
    """F-SEC-014: exercise the installed filter through logging at DEBUG."""
    secret = "wp-f1-secret-never-log"
    payload = {"operation": "safe-operation", "nested": [{key.upper(): secret}]}
    with caplog.at_level(logging.DEBUG, logger=orei_matrix._LOG.name):
        if style == "structured":
            orei_matrix._LOG.debug("payload: %s", payload)
        elif style == "json":
            orei_matrix._LOG.debug(json.dumps(payload))
        else:
            orei_matrix._LOG.debug("safe-operation %s", f"{key}={secret}")
    rendered = "\n".join(record.getMessage() for record in caplog.records if record.name == orei_matrix._LOG.name)
    assert "safe-operation" in rendered
    assert secret not in rendered
    assert "***REDACTED***" in rendered


async def test_uc_auth_token_guards_setup_and_reconfigure(simulator, tmp_path):
    """F-SEC-015: use a real driver process and scripted Remote, with no auth mocks."""
    token = "wp-f1-uc-setup-secret"
    hub = HubProcess(
        matrix_host="127.0.0.1", matrix_port=simulator.https_port, telnet_port=simulator.telnet_port,
        log_dir=tmp_path / "uc", mode="uc", uc_restore=False, stop_timeout=3,
        extra_env={"UC_AUTH_TOKEN": token, "ADMIN_PIN": "", "CONTROL_PIN": "", "MATRIX_HOST": "",
                   "LOG_LEVEL": "DEBUG", "OREI_VERIFY_SSL": "false", "MATRIX_CA_CERT": "",
                   "MATRIX_TLS_FINGERPRINT": ""},
    )
    try:
        hub.launch()
        await asyncio.to_thread(hub.wait_ready, 60)
        async with UcRemoteSim(hub.uc_url) as remote:
            metadata = (await remote.get_driver_metadata())["msg_data"]
            assert metadata["pwd"] is True
            assert any(field["id"] == "auth_token" for field in metadata["setup_data_schema"]["settings"])
            address = {"host": "127.0.0.1", "port": simulator.https_port}
            for supplied in ({}, {"auth_token": "wrong"}, {"auth_token": 123}):
                outcome = await remote.setup_driver({**address, **supplied})
                assert outcome.error == "AUTHORIZATION_ERROR"
            assert not [entry for entry in simulator.log if entry.get("command") == "login"]
            accepted = await remote.setup_driver({**address, "auth_token": token})
            assert accepted.error is None
            outcome = await remote.set_driver_user_data(input_values={"user": "Admin", "password": "admin"})
            assert outcome.state == "OK", outcome
            for supplied in ({}, {"auth_token": "wrong"}):
                assert (await remote.setup_driver({**address, **supplied}, reconfigure=True)).error == "AUTHORIZATION_ERROR"
            assert (await remote.setup_driver({**address, "auth_token": token}, reconfigure=True)).state == "OK"
    finally:
        await asyncio.to_thread(hub.stop)
    assert token not in hub.log_path.read_text(encoding="utf-8", errors="replace")
