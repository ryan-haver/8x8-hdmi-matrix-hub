"""Start the system under test: the real hub (``run.py``) and, for ``--target sim``, the simulator.

Same mechanics as ``tools/dev_stack.py`` (whose wait/stop helpers are reused):
the simulator runs as ``python -m tools.simulator`` and the hub through its real
entry point ``run.py``, both as subprocesses on free ports. Hub data is a fresh
copy of the Playwright fixture data (``tests/e2e/fixtures/data``: profiles,
macros, scenes, shortcuts, ...).

The hub runs in one of two modes:

* ``api`` (default): modular API-only mode (``USE_MODULAR=true UC_ENABLED=false``).
* ``uc``: the shipped default, legacy mode, in which ``run.py`` executes
  ``src/driver.py``: REST API + web UI + the Unfolded Circle integration
  WebSocket (``ucapi``). The integration listens on its own free port with mDNS
  publishing disabled, and ``config_state.json`` is seeded with the matrix
  address, so the driver restores its entities at start-up the way an installed
  and configured integration does. ``uc_restore=False`` starts it unconfigured,
  for the setup flow. Used by ``tests/uc`` and the ``uc`` validation client.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
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
    "REST_API_PORT", "UC_INTEGRATION_HTTP_PORT", "UC_INTEGRATION_INTERFACE", "UC_DISABLE_MDNS_PUBLISH",
    "POLLING_INTERVAL",
)

HUB_MODES = ("api", "uc")


#: Ports this process already handed out. The OS may return the same free port
#: twice in a row (it is only reserved while bound), e.g. for a hub's REST and
#: integration ports picked back to back, so hand each one out once.
_HANDED_OUT: set[int] = set()


def free_port(host: str = "127.0.0.1") -> int:
    for _ in range(50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, 0))
            port = int(s.getsockname()[1])
        if port not in _HANDED_OUT:
            _HANDED_OUT.add(port)
            return port
    raise RuntimeError("no unused free port found")


def port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


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
    #: ``api`` (modular API-only) or ``uc`` (legacy ``driver.py`` with the UC integration).
    mode: str = "api"
    #: UC mode: integration WebSocket port (0 = pick a free one).
    uc_port: int = 0
    #: UC mode: seed ``config_state.json`` so the driver restores the matrix at start-up.
    uc_restore: bool = True
    #: UC mode: more ``config_state.json`` fields, e.g. the ``input_names``/``output_names`` a setup saved.
    uc_config_extra: dict[str, Any] = field(default_factory=dict)
    #: UC mode: status polling interval in whole seconds (``driver.py`` reads it with ``int()``).
    polling_interval: int = 30
    #: Seconds ``stop()`` waits after terminating the hub before killing it.
    stop_timeout: float = 8.0
    #: Keep the data directory across :meth:`restart` (a restarted driver keeps its configuration).
    keep_data_on_restart: bool = False
    _proc: subprocess.Popen[bytes] | None = None
    _data_dir: str | None = None
    _log: IO[bytes] | None = None
    starts: int = 0

    def __post_init__(self) -> None:
        if self.mode not in HUB_MODES:
            raise ValueError(f"hub mode must be one of {HUB_MODES}, not {self.mode!r}")

    @property
    def base_url(self) -> str:
        return self.external_url or f"http://{self.host}:{self.api_port}"

    @property
    def uc_url(self) -> str:
        """The integration WebSocket a Remote connects to (UC mode)."""
        return f"ws://{self.host}:{self.uc_port}"

    @property
    def data_dir(self) -> Path | None:
        return Path(self._data_dir) if self._data_dir else None

    @property
    def entry(self) -> str:
        """How the hub was started, for evidence records."""
        if self.external_url:
            return self.external_url
        if self.mode == "uc":
            return "run.py legacy mode (src/driver.py: REST API + UC integration, UC_ENABLED=true)"
        return "run.py (USE_MODULAR=true, UC_ENABLED=false)"

    @property
    def log_path(self) -> Path:
        suffix = "-uc" if self.mode == "uc" else ""
        return self.log_dir / f"hub{suffix}-{self.starts}.log"

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
        }
        if self.mode == "uc":
            env.update({
                "USE_MODULAR": "false",
                "UC_ENABLED": "true",
                # driver.py reads REST_API_PORT (run.py's API_PORT is modular mode only).
                "REST_API_PORT": str(self.api_port),
                # ucapi reads these: WebSocket port and bind address; never publish mDNS from tests.
                "UC_INTEGRATION_HTTP_PORT": str(self.uc_port),
                "UC_INTEGRATION_INTERFACE": self.host,
                "UC_DISABLE_MDNS_PUBLISH": "true",
                "POLLING_INTERVAL": str(self.polling_interval),
            })
        env.update(self.extra_env)
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
        self.launch()
        return self.wait_ready()

    def launch(self) -> None:
        """Start the process without waiting for it (see :meth:`wait_ready`).

        Split from :meth:`start` so a caller that serves the simulator on its own
        event loop can wait asynchronously: the UC driver talks to the matrix
        before it opens its ports.
        """
        if not self.api_port:
            self.api_port = free_port(self.host)
        if self.mode == "uc" and not self.uc_port:
            self.uc_port = free_port(self.host)
        if self._data_dir is None:
            self._data_dir = tempfile.mkdtemp(prefix="hub-validate-data-")
            shutil.copytree(FIXTURE_DATA, self._data_dir, dirs_exist_ok=True)
            if self.mode == "uc" and self.uc_restore:
                # What a completed setup leaves behind (driver.py save_config); the driver
                # restores the matrix connection and its entities from it at start-up.
                config = {"host": self.matrix_host, "port": self.matrix_port, **self.uc_config_extra}
                Path(self._data_dir, "config_state.json").write_text(json.dumps(config), encoding="utf-8")
        env = self.env()
        env["MATRIX_DATA_DIR"] = self._data_dir
        env["UC_CONFIG_HOME"] = self._data_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.starts += 1
        self._log = open(self.log_path, "wb")  # noqa: SIM115 - closed in stop()
        self._proc = subprocess.Popen(  # noqa: S603 - fixed argv
            [sys.executable, "run.py"], cwd=ROOT, env=env, stdout=self._log, stderr=subprocess.STDOUT
        )

    def ready(self) -> bool:
        """One non-blocking readiness probe (``/api/health`` port and, in UC mode, the integration port)."""
        if self._proc is None or self._proc.poll() is not None:
            raise RuntimeError(f"hub exited early with code {self.returncode} (log: {self.log_path})")
        if not port_open(self.host, self.api_port):
            return False
        return self.mode != "uc" or port_open(self.host, self.uc_port)

    def wait_ready(self, timeout: float = 60) -> dict[str, Any]:
        """Block until ``/api/health`` answers and, in UC mode, the integration port accepts."""
        assert self._proc is not None, "launch() first"
        try:
            health = _wait_for(f"{self.base_url}/api/health", self._proc, timeout, "hub")
        except RuntimeError as exc:
            raise RuntimeError(f"{exc}\n--- {self.log_path} (tail) ---\n{self.log_tail()}") from None
        if self.mode == "uc":
            # driver.py starts the REST API after api.init(), so the WebSocket is normally up already.
            deadline = time.monotonic() + 10
            while not port_open(self.host, self.uc_port):
                if time.monotonic() > deadline or self._proc.poll() is not None:
                    raise RuntimeError(f"UC integration not listening on {self.uc_url} (log: {self.log_path})")
                time.sleep(0.1)
        return health.get("data", {})

    def log_tail(self, lines: int = 40) -> str:
        try:
            text = self.log_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return "(no log)"
        return "\n".join(text.splitlines()[-lines:])

    @property
    def returncode(self) -> int | None:
        return self._proc.poll() if self._proc else None

    @property
    def pid(self) -> int | None:
        return self._proc.pid if self._proc else None

    def stop(self, *, keep_data: bool = False) -> None:
        _stop(self._proc, "hub", timeout=self.stop_timeout)
        self._proc = None
        if self._log:
            self._log.close()
            self._log = None
        if self._data_dir and not keep_data:
            shutil.rmtree(self._data_dir, ignore_errors=True)
            self._data_dir = None

    def restart(self) -> dict[str, Any]:
        self.stop(keep_data=self.keep_data_on_restart)
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

    def _new_hub(self, mode: str) -> HubProcess:
        return HubProcess(
            matrix_host=self.host,
            matrix_port=self.sim.https_port,
            telnet_port=self.sim.telnet_port,
            log_dir=self.log_dir,
            host=self.host,
            mode=mode,
            # UC scenarios: poll fast enough that pushes land within a scenario.
            polling_interval=2 if mode == "uc" else 30,
        )

    def start(self, mode: str = "api") -> None:
        self.sim.start()
        self.hub = self._new_hub(mode)
        self.health = self.hub.start()

    def use_hub_mode(self, mode: str) -> None:
        """Make sure the hub runs in ``mode`` (restart it in the other mode if needed)."""
        if self.hub is not None and self.hub.mode == mode:
            return
        if self.hub is not None:
            self.hub.stop()
        self.hub = self._new_hub(mode)
        self.health = self.hub.start()

    def restart_hub(self) -> None:
        assert self.hub is not None
        self.health = self.hub.restart()

    def stop(self) -> None:
        if self.hub:
            self.hub.stop()
        self.sim.stop()
