"""run.py, the one runtime entry (WP-D2: DEP-03, DEP-07, D4, D11, UC-03).

Unit tests for the environment contract, plus one real start of ``python run.py``
in core-only mode proving that the Remote integration (``ucapi``) is not imported
when it is disabled. The Docker image is tested in tests/deploy (``-m docker``).
"""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

import run
import run_server

ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Environment contract
# ---------------------------------------------------------------------------


def test_defaults_are_core_only() -> None:
    settings = run.load_settings({})
    assert settings.uc_enabled is False
    assert settings.api_port == 8080
    assert settings.matrix_port == 443
    assert settings.matrix_host is None
    assert settings.data_dir is None and settings.uc_config_home is None
    assert settings.log_level == "INFO"
    assert settings.notes == ()


@pytest.mark.parametrize("value", ["true", "TRUE", "1", "yes", "on"])
def test_uc_enabled_values(value: str) -> None:
    assert run.load_settings({"UC_ENABLED": value}).uc_enabled is True


@pytest.mark.parametrize("value", ["false", "0", "no", "", "off"])
def test_uc_disabled_values(value: str) -> None:
    assert run.load_settings({"UC_ENABLED": value}).uc_enabled is False


@pytest.mark.parametrize(
    ("alias", "canonical", "value", "field", "expected"),
    [
        ("OREI_HOST", "MATRIX_HOST", "10.0.0.5", "matrix_host", "10.0.0.5"),
        ("OREI_PORT", "MATRIX_PORT", "8443", "matrix_port", 8443),
        ("REST_API_PORT", "API_PORT", "9000", "api_port", 9000),
        ("OREI_API_PORT", "API_PORT", "9001", "api_port", 9001),
        ("MATRIX_DATA_DIR", "DATA_DIR", "/srv/hub", "data_dir", Path("/srv/hub")),
        ("UC_PORT", "UC_INTEGRATION_HTTP_PORT", "9096", "uc_port", 9096),
        ("UC_DISABLE_MDNS", "UC_DISABLE_MDNS_PUBLISH", "true", "uc_disable_mdns", True),
    ],
)
def test_deprecated_alias_is_used_with_a_note(alias, canonical, value, field, expected) -> None:
    settings = run.load_settings({alias: value})
    assert getattr(settings, field) == expected
    assert settings.notes == (f"{alias} -> use {canonical}",)


def test_canonical_name_wins_over_alias() -> None:
    settings = run.load_settings({"API_PORT": "8080", "REST_API_PORT": "9000", "MATRIX_HOST": "a", "OREI_HOST": "a"})
    assert settings.api_port == 8080
    assert settings.matrix_host == "a"
    # the same value under both names is not worth a note; a different one is
    assert settings.notes == ("REST_API_PORT ignored (API_PORT is set)",)


@pytest.mark.parametrize("name", ["USE_MODULAR", "WEBUI_ENABLED"])
def test_retired_variables_are_ignored_with_a_note(name: str) -> None:
    for value in ("true", "false"):
        settings = run.load_settings({name: value})
        assert settings.uc_enabled is False
        assert len(settings.notes) == 1 and settings.notes[0].startswith(f"{name} is ignored")


def test_rest_api_cannot_be_disabled() -> None:
    settings = run.load_settings({"REST_API_ENABLED": "false"})
    assert "REST_API_ENABLED=false is ignored" in settings.notes[0]
    env: dict[str, str] = {"REST_API_ENABLED": "false"}
    run.export_env(settings, env)
    assert env["REST_API_ENABLED"] == "true"


def test_uc_config_home_defaults_to_data_dir() -> None:
    assert run.load_settings({"DATA_DIR": "/data"}).uc_config_home == Path("/data")
    assert run.load_settings({"DATA_DIR": "/data", "UC_CONFIG_HOME": "/uc"}).uc_config_home == Path("/uc")


@pytest.mark.parametrize("url", ["http://1.2.3.4:9095", "1.2.3.4:9095", "ws:/x"])
def test_driver_url_must_be_a_websocket_url(url: str) -> None:
    with pytest.raises(run.ConfigError, match="UC_DRIVER_URL"):
        run.load_settings({"UC_DRIVER_URL": url})


@pytest.mark.parametrize(("name", "value"), [("API_PORT", "http"), ("MATRIX_PORT", "0"), ("API_PORT", "70000")])
def test_bad_ports_are_config_errors(name: str, value: str) -> None:
    with pytest.raises(run.ConfigError, match=name):
        run.load_settings({name: value})


def test_bad_log_level_falls_back_to_info() -> None:
    settings = run.load_settings({"LOG_LEVEL": "loud"})
    assert settings.log_level == "INFO"
    assert "LOG_LEVEL=LOUD" in settings.notes[0]


def test_export_env_uses_the_names_the_modules_read() -> None:
    settings = run.load_settings({
        "MATRIX_DATA_DIR": "/data", "REST_API_PORT": "9000", "OREI_HOST": "10.1.1.1",
        "UC_INTEGRATION_INTERFACE": "", "UC_PORT": "9999",
    })
    env: dict[str, str] = {"UC_INTEGRATION_INTERFACE": ""}
    run.export_env(settings, env)
    assert env["MATRIX_DATA_DIR"] == env["DATA_DIR"] == env["UC_CONFIG_HOME"] == str(Path("/data"))
    assert env["API_PORT"] == env["REST_API_PORT"] == "9000"
    assert env["MATRIX_HOST"] == "10.1.1.1"
    assert env["UC_INTEGRATION_HTTP_PORT"] == "9999"
    assert "UC_INTEGRATION_INTERFACE" not in env  # empty would be used as a bind address by ucapi
    assert env["UC_DISABLE_MDNS_PUBLISH"] == "false"
    assert env["UC_ENABLED"] == "false"


def test_saved_matrix_address(tmp_path: Path) -> None:
    assert run.saved_matrix_address(tmp_path) is None
    (tmp_path / "config_state.json").write_text(json.dumps({"host": "10.2.2.2", "port": 8443}), encoding="utf-8")
    assert run.saved_matrix_address(tmp_path) == ("10.2.2.2", 8443)
    (tmp_path / "config_state.json").write_text("{not json", encoding="utf-8")
    assert run.saved_matrix_address(tmp_path) is None


def test_check_writable_creates_the_directory(tmp_path: Path) -> None:
    run.check_writable(tmp_path / "a" / "b")
    assert (tmp_path / "a" / "b").is_dir()
    assert list((tmp_path / "a" / "b").iterdir()) == []


def test_check_writable_explains_an_unwritable_directory(tmp_path: Path) -> None:
    blocker = tmp_path / "file"
    blocker.write_text("x", encoding="utf-8")
    with pytest.raises(run.ConfigError, match="not writable"):
        run.check_writable(blocker / "data")


def test_main_rejects_bad_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UC_DRIVER_URL", "http://nope")
    assert run.main([]) == 2


# ---------------------------------------------------------------------------
# UC_DRIVER_URL (UC-03)
# ---------------------------------------------------------------------------


def test_driver_json_has_no_driver_url() -> None:
    """An empty driver_url made ucapi advertise ws://<container id>:9095 (UC-03)."""
    assert "driver_url" not in json.loads((ROOT / "driver.json").read_text(encoding="utf-8"))


def test_driver_metadata_copy_carries_the_url() -> None:
    path = run.write_driver_metadata("ws://192.0.2.7:9095")
    try:
        meta = json.loads(path.read_text(encoding="utf-8"))
    finally:
        path.unlink()
    original = json.loads((ROOT / "driver.json").read_text(encoding="utf-8"))
    assert meta == {**original, "driver_url": "ws://192.0.2.7:9095"}


async def test_integration_api_loads_the_metadata_copy(tmp_path: Path) -> None:
    ucapi = pytest.importorskip("ucapi")
    seen: list[str] = []

    async def fake_init(self, driver_path, setup_handler=None):
        seen.append(driver_path)

    original = ucapi.IntegrationAPI.init
    ucapi.IntegrationAPI.init = fake_init
    try:
        restore = run.use_driver_metadata(tmp_path / "meta.json")
        await ucapi.IntegrationAPI.init(object(), "driver.json", None)
        restore()
        assert ucapi.IntegrationAPI.init is fake_init
    finally:
        ucapi.IntegrationAPI.init = original
    assert seen == [str(tmp_path / "meta.json")]


# ---------------------------------------------------------------------------
# run_server.py is a thin alias of run.py
# ---------------------------------------------------------------------------


def test_run_server_maps_options_onto_run(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for name in ("MATRIX_HOST", "API_PORT", "MATRIX_PORT", "DATA_DIR", "UC_CONFIG_HOME", "UC_ENABLED", "LOG_LEVEL"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("UC_ENABLED", "true")
    calls: list[dict[str, str]] = []
    monkeypatch.setattr(run, "main", lambda argv: calls.append(dict(os.environ)) or 0)
    args = ["--host", "10.3.3.3", "--port", "9100", "--matrix-port", "8443", "--config-dir", str(tmp_path), "--debug"]
    assert run_server.main(args) == 0
    env = calls[0]
    assert env["MATRIX_HOST"] == "10.3.3.3" and env["API_PORT"] == "9100" and env["MATRIX_PORT"] == "8443"
    assert env["DATA_DIR"] == env["UC_CONFIG_HOME"] == str(tmp_path)
    assert env["LOG_LEVEL"] == "DEBUG"
    assert env["UC_ENABLED"] == "false"


# ---------------------------------------------------------------------------
# A real start: core only, ucapi never imported
# ---------------------------------------------------------------------------


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _get(url: str) -> tuple[int, bytes]:
    with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310 - local test server
        return resp.status, resp.read()


def test_core_only_start_serves_ui_and_never_imports_ucapi(tmp_path: Path) -> None:
    """UC_ENABLED unset: /api/health, /ui and /kiosk answer; `python -X importtime` shows no ucapi import."""
    api_port = _free_port()
    closed_port = _free_port()  # nothing listens: the matrix is unreachable, the hub must still come up
    env = {k: v for k, v in os.environ.items() if not k.startswith(("UC_", "OREI_", "MATRIX_"))}
    env.update({
        "MATRIX_HOST": "127.0.0.1", "MATRIX_PORT": str(closed_port),
        "REST_API_PORT": str(api_port),  # deprecated alias on purpose: one warning, still honoured
        "DATA_DIR": str(tmp_path / "data"), "PYTHONUNBUFFERED": "1", "PYTHONDONTWRITEBYTECODE": "1",
        "OREI_AUTO_RECONNECT": "false",
    })
    env.pop("API_PORT", None)
    log = tmp_path / "hub.log"
    with open(log, "wb") as out:
        proc = subprocess.Popen(  # noqa: S603 - fixed argv
            [sys.executable, "-X", "importtime", "run.py"], cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT
        )
        try:
            deadline = time.monotonic() + 45
            while True:
                assert proc.poll() is None, log.read_text(encoding="utf-8", errors="replace")[-3000:]
                try:
                    status, body = _get(f"http://127.0.0.1:{api_port}/api/health")
                    break
                except OSError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.25)
            assert status == 200 and json.loads(body)["data"]["status"] == "healthy"
            for path in ("/ui", "/kiosk"):
                status, body = _get(f"http://127.0.0.1:{api_port}{path}")
                assert status == 200 and b"<html" in body.lower()
        finally:
            proc.terminate()
            proc.wait(timeout=15)
    text = log.read_text(encoding="utf-8", errors="replace")
    imported = re.findall(r"^import time:.*\|\s+(\S+)\s*$", text, flags=re.MULTILINE)
    assert "rest_api" in imported  # the import trace is really there
    assert not [m for m in imported if m == "ucapi" or m.startswith("ucapi.")]
    assert "ucapi imported: False" in text
    assert text.count("Deprecated or ignored environment variables") == 1
    assert "REST_API_PORT -> use API_PORT" in text
    assert (tmp_path / "data").is_dir()
