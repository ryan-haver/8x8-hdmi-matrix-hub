"""Start the system under test: the real hub (``run.py``) and, for ``--target sim``, the simulator.

Same mechanics as ``tools/dev_stack.py`` (whose wait/stop helpers are reused):
the simulator runs as ``python -m tools.simulator`` and the hub through its real
entry point ``run.py`` in modular API-only mode, both as subprocesses on free
ports. Hub data is a fresh copy of the Playwright fixture data
(``tests/e2e/fixtures/data``: profiles, macros, scenes, shortcuts, ...).
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Any, cast

from tools.dev_stack import _stop, _wait_for

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DATA = ROOT / "tests" / "e2e" / "fixtures" / "data"
SEED_STATE = ROOT / "tools" / "simulator" / "states" / "default.json"

#: Hub environment recorded in every evidence record (values, not secrets).
RECORDED_ENV = (
    "USE_MODULAR", "UC_ENABLED", "MATRIX_HOST", "MATRIX_PORT", "OREI_TELNET_PORT", "OREI_VERIFY_SSL",
    "OREI_USE_TELNET_CEC", "OREI_STATUS_CACHE_TTL", "TRUST_PROXY_HEADERS", "TRUSTED_PROXY_IPS", "LOG_LEVEL",
)


def free_port(host: str = "127.0.0.1") -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return int(s.getsockname()[1])


@dataclass
class HubProcess:
    """The hub under test, started from ``run.py`` (or an already running hub via ``external_url``)."""

    matrix_host: str
    matrix_port: int
    telnet_port: int
    log_dir: Path
    host: str = "127.0.0.1"
    api_port: int = 0
    matrix_user: str | None = None
    matrix_password: str | None = None
    external_url: str | None = None
    extra_env: dict[str, str] = field(default_factory=dict)
    _proc: subprocess.Popen[bytes] | None = None
    _data_dir: str | None = None
    _log: IO[bytes] | None = None
    starts: int = 0

    @property
    def base_url(self) -> str:
        return self.external_url or f"http://{self.host}:{self.api_port}"

    def env(self) -> dict[str, str]:
        env = {
            **os.environ,
            "USE_MODULAR": "true",
            "UC_ENABLED": "false",
            "MATRIX_HOST": self.matrix_host,
            "MATRIX_PORT": str(self.matrix_port),
            "OREI_TELNET_PORT": str(self.telnet_port),
            "API_PORT": str(self.api_port),
            "LOG_LEVEL": os.environ.get("VALIDATE_HUB_LOG_LEVEL", "INFO"),
            # Each client sends its own X-Forwarded-For, so browser page loads
            # and API scenarios get separate rate-limit buckets (60 req/10 s).
            "TRUST_PROXY_HEADERS": "true",
            "TRUSTED_PROXY_IPS": "127.0.0.1",
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            **self.extra_env,
        }
        for key in ("OREI_USER", "OREI_PASSWORD", "OREI_PORT", "OREI_HOST"):
            env.pop(key, None)
        if self.matrix_user:
            env["OREI_USER"] = self.matrix_user
        if self.matrix_password:
            env["OREI_PASSWORD"] = self.matrix_password
        return env

    def recorded_env(self) -> dict[str, str]:
        env = self.env()
        return {k: env[k] for k in RECORDED_ENV if k in env}

    def start(self) -> dict[str, Any]:
        """Start the hub; returns its ``/api/health`` data."""
        if self.external_url:
            never = cast("subprocess.Popen[bytes]", _NeverExits())
            return _wait_for(f"{self.external_url}/api/health", never, 15, "hub").get("data", {})
        if not self.api_port:
            self.api_port = free_port(self.host)
        self._data_dir = tempfile.mkdtemp(prefix="hub-validate-data-")
        shutil.copytree(FIXTURE_DATA, self._data_dir, dirs_exist_ok=True)
        env = self.env()
        env["MATRIX_DATA_DIR"] = self._data_dir
        env["UC_CONFIG_HOME"] = self._data_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.starts += 1
        self._log = open(self.log_dir / f"hub-{self.starts}.log", "wb")  # noqa: SIM115 - closed in stop()
        self._proc = subprocess.Popen(  # noqa: S603 - fixed argv
            [sys.executable, "run.py"], cwd=ROOT, env=env, stdout=self._log, stderr=subprocess.STDOUT
        )
        health = _wait_for(f"{self.base_url}/api/health", self._proc, 45, "hub")
        return health.get("data", {})

    def stop(self) -> None:
        _stop(self._proc, "hub")
        self._proc = None
        if self._log:
            self._log.close()
            self._log = None
        if self._data_dir:
            shutil.rmtree(self._data_dir, ignore_errors=True)
            self._data_dir = None

    def restart(self) -> dict[str, Any]:
        self.stop()
        return self.start()


class _NeverExits:
    """``Popen`` stand-in for waiting on an external hub."""

    returncode = None

    def poll(self) -> None:
        return None


@dataclass
class SimulatorProcess:
    """``python -m tools.simulator`` on free ports."""

    log_dir: Path
    host: str = "127.0.0.1"
    https_port: int = 0
    telnet_port: int = 0
    control_port: int = 0
    _proc: subprocess.Popen[bytes] | None = None
    _log: IO[bytes] | None = None

    @property
    def control_url(self) -> str:
        return f"http://{self.host}:{self.control_port}"

    def start(self) -> dict[str, Any]:
        self.https_port = self.https_port or free_port(self.host)
        self.telnet_port = self.telnet_port or free_port(self.host)
        self.control_port = self.control_port or free_port(self.host)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._log = open(self.log_dir / "simulator.log", "wb")  # noqa: SIM115 - closed in stop()
        cmd = [
            sys.executable, "-m", "tools.simulator",
            "--host", self.host,
            "--https-port", str(self.https_port),
            "--telnet-port", str(self.telnet_port),
            "--control-port", str(self.control_port),
            "--state", str(SEED_STATE),
            "--log-level", "INFO",
        ]
        self._proc = subprocess.Popen(cmd, cwd=ROOT, stdout=self._log, stderr=subprocess.STDOUT)  # noqa: S603
        return _wait_for(f"{self.control_url}/_sim/health", self._proc, 30, "simulator")

    def stop(self) -> None:
        _stop(self._proc, "simulator")
        self._proc = None
        if self._log:
            self._log.close()
            self._log = None


class SimStack:
    """Simulator + hub. Stop order matters: hub first (a hub whose Telnet peer
    disappears busy-loops, BE-28)."""

    def __init__(self, log_dir: Path, host: str = "127.0.0.1") -> None:
        self.sim = SimulatorProcess(log_dir=log_dir, host=host)
        self.hub: HubProcess | None = None
        self.log_dir = log_dir
        self.host = host
        self.health: dict[str, Any] = {}

    def start(self) -> None:
        self.sim.start()
        self.hub = HubProcess(
            matrix_host=self.host,
            matrix_port=self.sim.https_port,
            telnet_port=self.sim.telnet_port,
            log_dir=self.log_dir,
            host=self.host,
        )
        self.health = self.hub.start()

    def restart_hub(self) -> None:
        assert self.hub is not None
        self.health = self.hub.restart()

    def stop(self) -> None:
        if self.hub:
            self.hub.stop()
        self.sim.stop()
