"""Installed console bootstrap proof; real startup awaits the R2 merge explicitly."""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import sysconfig
import time
import urllib.request
import venv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest

import run
from hub import cli
from hub.runtime_paths import SOURCE_ROOT, default_config_dir
from tests import test_packaging_version_sync as packaging

distributions = packaging.distributions

FIXTURES = Path(__file__).parent / "fixtures" / "runtime_installed_r1p"


def test_root_import_alias_preserves_bootstrap_globals(monkeypatch):
    assert run is cli
    called = []
    monkeypatch.setattr(run, "healthcheck", lambda env: called.append(env) or 17)
    assert cli.main(["healthcheck"]) == 17
    assert called == [os.environ]


def test_source_paths_and_installed_storage_requirement(monkeypatch, tmp_path):
    assert SOURCE_ROOT == Path(__file__).resolve().parents[1]
    assert default_config_dir() == SOURCE_ROOT / "config"
    assert run.load_settings({}).data_dir is None
    monkeypatch.setattr(cli, "SOURCE_ROOT", None)
    with pytest.raises(cli.ConfigError, match="explicit writable DATA_DIR"):
        cli.load_settings({"UC_CONFIG_HOME": str(tmp_path)})
    settings = cli.load_settings({"MATRIX_DATA_DIR": str(tmp_path), "UC_CONFIG_HOME": str(tmp_path / "uc")})
    assert settings.data_dir == tmp_path and settings.uc_config_home == tmp_path / "uc"


def clean_env():
    return {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("UC_", "OREI_", "MATRIX_", "PYTHON", "R1P_"))
        and key not in {"DATA_DIR", "API_PORT", "REST_API_PORT", "FLIC_ENABLED", "HA_DISCOVERY_ENABLED"}
    }


@pytest.fixture(scope="module")
def installed_runtime(distributions, tmp_path_factory):
    """A real wheel install with dependencies read from, never installed into, the test env."""
    wheel, _, version = distributions
    root = tmp_path_factory.mktemp("installed-runtime")
    target = root / "venv"
    venv.EnvBuilder(with_pip=False).create(target)
    scripts = target / ("Scripts" if os.name == "nt" else "bin")
    python = scripts / ("python.exe" if os.name == "nt" else "python")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "--python", str(python), "install", "--no-deps", str(wheel)],
        cwd=root,
        env=clean_env(),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    site = target / (
        "Lib/site-packages"
        if os.name == "nt"
        else f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    # A path-only .pth exposes dependencies without processing the shared env's
    # editable-install hooks. This venv's own wheel remains first on sys.path.
    (site / "00-test-dependencies.pth").write_text(sysconfig.get_path("purelib") + "\n", encoding="utf-8")
    entry = scripts / ("orei-matrix-driver.exe" if os.name == "nt" else "orei-matrix-driver")
    assert entry.is_file()
    return root, python, site, entry, version


def installed_python(installed_runtime, code, *args, env=None):
    root, python, _, _, _ = installed_runtime
    result = subprocess.run(
        [str(python), "-I", "-c", code, *map(str, args)],
        cwd=root,
        env=clean_env() if env is None else env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


def test_installed_metadata_resources_and_storage(installed_runtime):
    root, _, site, entry, version = installed_runtime
    code = """
import importlib.util, json, sys
from importlib.metadata import distribution
from importlib.resources import files
from pathlib import Path
import hub, version
from hub import cli
from hub.runtime_paths import SOURCE_ROOT, driver_metadata_path
site, expected, data = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
assert SOURCE_ROOT is None
assert importlib.util.find_spec('run') is None
assert importlib.util.find_spec('run_server') is None
assert Path(hub.__file__).is_relative_to(site)
assert Path(cli.__file__).is_relative_to(site)
dist = distribution('ucapi-orei-hdmi-matrix')
entry, = [e for e in dist.entry_points if e.name == 'orei-matrix-driver']
assert entry.value == 'hub.cli:main' and entry.load() is cli.main
assert hub.__version__ == version.__version__ == dist.version == expected
manifest = driver_metadata_path()
assert json.loads(manifest.read_text())['version'] == expected
assert files('web').joinpath('index.html').is_file()
assert files('web').joinpath('js/app.js').is_file()
try:
    cli.load_settings({})
except cli.ConfigError as exc:
    assert 'explicit writable DATA_DIR' in str(exc)
else:
    raise AssertionError('installed startup must require writable storage')
settings = cli.load_settings({'DATA_DIR': str(data)})
assert settings.data_dir == settings.uc_config_home == data
before = manifest.read_bytes()
copy = cli.write_driver_metadata('ws://127.0.0.1:19095')
try:
    assert copy != manifest
    assert json.loads(copy.read_text()) == {**json.loads(before), 'driver_url': 'ws://127.0.0.1:19095'}
finally:
    copy.unlink()
assert manifest.read_bytes() == before
assert 'ucapi' not in sys.modules and 'driver' not in sys.modules
"""
    installed_python(installed_runtime, code, site, version, root / "data")
    result = subprocess.run([str(entry)], cwd=root, env=clean_env(), capture_output=True, text=True, timeout=30)
    assert result.returncode == 2
    assert "explicit writable DATA_DIR" in result.stderr


def test_installed_console_healthcheck_without_runtime_substitutes(installed_runtime, tmp_path):
    """The console healthcheck reaches a local HTTP fixture without constructing a runtime."""
    root, _, _, entry, _ = installed_runtime

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - stdlib handler contract
            self.send_response(200 if self.path == "/api/health" else 404)
            self.end_headers()

        def log_message(self, *args):
            pass

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        env = clean_env()
        env.update(DATA_DIR=str(tmp_path / "data"), API_PORT=str(server.server_port))
        try:
            result = subprocess.run(
                [str(entry), "healthcheck"],
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            assert result.returncode == 0, result.stdout + result.stderr
            assert not (tmp_path / "data").exists()
        finally:
            server.shutdown()
            thread.join(timeout=5)


@pytest.mark.parametrize("uc", [False, True])
def test_installed_console_reaches_factory_and_clean_shutdown_with_double(installed_runtime, tmp_path, uc):
    """Factory double only: no migration, REST, or SDK startup proof is claimed."""
    root, _, site, entry, _ = installed_runtime
    probe = site / "runtime_installed_probe.py"
    hook = site / "zz-runtime-probe.pth"
    probe.write_bytes((FIXTURES / "factory_probe.py").read_bytes())
    hook.write_text("import runtime_installed_probe\n", encoding="utf-8")
    env = clean_env()
    result_path = tmp_path / "factory.json"
    env.update(DATA_DIR=str(tmp_path / "data"), UC_ENABLED=str(uc), R1P_RESULT=str(result_path))
    try:
        result = subprocess.run([str(entry)], cwd=root, env=env, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stdout + result.stderr
        result = json.loads(result_path.read_text())
        assert result["uc_enabled"] is uc
        assert result["data_dir"] == str(tmp_path / "data")
        assert result["events"] == ["factory", "start", "stop"]
        assert result["ucapi_imported"] is False and result["legacy_imported"] is False
        assert Path(result["cli"]).is_relative_to(site)
        assert Path(result["composition"]).is_relative_to(site)
    finally:
        hook.unlink()
        probe.unlink()


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_real_installed_start_health_ui_uc_off_and_shutdown(installed_runtime, tmp_path):
    """No factory/migration/REST substitutes; automatically applies after R2 merges."""
    root, _, site, entry, _ = installed_runtime
    if not (site / "hub/persistence/startup.py").is_file():
        pytest.skip("R2 prerequisite pending: wheel lacks hub.persistence.startup; real installed startup unproven")
    control = site / "runtime_installed_control.py"
    hook = site / "zz-runtime-control.pth"
    control.write_bytes((FIXTURES / "shutdown_control.py").read_bytes())
    hook.write_text("import runtime_installed_control\n", encoding="utf-8")
    api_port, matrix_port, uc_port = free_port(), free_port(), free_port()
    stop, record = tmp_path / "stop", tmp_path / "exit.json"
    env = clean_env()
    env.update(
        DATA_DIR=str(tmp_path / "data"),
        UC_ENABLED="false",
        FLIC_ENABLED="false",
        HA_DISCOVERY_ENABLED="false",
        MATRIX_HOST="127.0.0.1",
        MATRIX_PORT=str(matrix_port),
        API_PORT=str(api_port),
        OREI_AUTO_RECONNECT="false",
        UC_INTEGRATION_HTTP_PORT=str(uc_port),
        R1P_STOP=str(stop),
        R1P_RESULT=str(record),
        PYTHONPROFILEIMPORTTIME="1",
        PYTHONUNBUFFERED="1",
    )
    log = tmp_path / "installed.log"
    proc = None
    try:
        with log.open("wb") as output:
            proc = subprocess.Popen([str(entry)], cwd=root, env=env, stdout=output, stderr=output)
            deadline = time.monotonic() + 30
            while True:
                assert proc.poll() is None, log.read_text(errors="replace")[-5000:]
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{api_port}/api/health", timeout=1) as response:
                        assert json.loads(response.read())["data"]["status"] == "healthy"
                    break
                except OSError:
                    assert time.monotonic() < deadline, log.read_text(errors="replace")[-5000:]
                    time.sleep(0.05)
            for path in ("/ui", "/kiosk"):
                with urllib.request.urlopen(f"http://127.0.0.1:{api_port}{path}", timeout=5) as response:
                    assert response.status == 200 and b"<html" in response.read().lower()
            health = subprocess.run([str(entry), "healthcheck"], cwd=root, env=env, capture_output=True, timeout=15)
            assert health.returncode == 0, health.stderr
            with socket.socket() as sock:
                assert sock.connect_ex(("127.0.0.1", uc_port)) != 0
            stop.touch()
            assert proc.wait(timeout=15) == 0, log.read_text(errors="replace")[-5000:]
        text = log.read_text(errors="replace")
        imported = re.findall(r"^import time:.*\|\s+(\S+)\s*$", text, re.MULTILINE)
        assert "rest_api" in imported and "ucapi imported: False" in text
        assert not any(name == "ucapi" or name.startswith("ucapi.") for name in imported)
        modules = json.loads(record.read_text())
        assert modules and all(Path(path).is_relative_to(site) for path in modules.values())
        assert "hub.runtime.composition" in modules and "driver" not in modules
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait(timeout=10)
        hook.unlink()
        control.unlink()
