"""Small Docker CLI helpers for the deployment tests (no SDK dependency)."""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ._evidence import RECORDER

ROOT = Path(__file__).resolve().parents[2]

#: TEST-NET-1 (RFC 5737): never a real device. Used where a test needs a matrix address but no matrix.
NO_MATRIX = "192.0.2.1"

#: Host address container ports are published on (``-p ADDR:PORT:PORT``, fixed free ports: Docker Desktop
#: does not forward randomly assigned host ports into its VM). Loopback by default; set
#: DEPLOY_TEST_PUBLISH_IP=0.0.0.0 when the tests themselves run in a container on Docker Desktop,
#: where loopback-only publishes are reachable from Windows/macOS but not from inside the VM.
PUBLISH_IP = os.environ.get("DEPLOY_TEST_PUBLISH_IP", "127.0.0.1")


def docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        return subprocess.run(["docker", "info"], capture_output=True, timeout=30).returncode == 0  # noqa: S607
    except (OSError, subprocess.TimeoutExpired):
        return False


def docker(*args: str, check: bool = True, timeout: float = 120, env: dict[str, str] | None = None,
           cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(  # noqa: S603
        ["docker", *args], capture_output=True, text=True, encoding="utf-8", errors="replace",  # noqa: S607
        timeout=timeout, env={**os.environ, **(env or {})}, cwd=cwd,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(f"docker {' '.join(args)} failed ({proc.returncode}):\n{proc.stdout}\n{proc.stderr}")
    return proc


def unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def http(url: str, *, method: str = "GET", body: Any = None, timeout: float = 10) -> tuple[int, bytes]:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method,  # noqa: S310 - local test containers
                                 headers={"Content-Type": "application/json"} if data else {})
    path = "/" + url.split("/", 3)[3] if url.count("/") >= 3 else url
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            result = resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        result = exc.code, exc.read()
    if "/_sim/" not in path:
        RECORDER.request(method, path, result[0])
    return result


def http_json(url: str, **kwargs: Any) -> tuple[int, Any]:
    status, raw = http(url, **kwargs)
    return status, json.loads(raw)


def wait_http(url: str, timeout: float = 60, is_alive: Any = None) -> tuple[int, bytes]:
    deadline = time.monotonic() + timeout
    last: Exception | None = None
    while time.monotonic() < deadline:
        if is_alive is not None and not is_alive():
            raise RuntimeError(f"container exited while waiting for {url}")
        try:
            return http(url, timeout=3)
        except (OSError, ValueError) as exc:  # connection refused/reset while starting
            last = exc
            time.sleep(0.5)
    raise TimeoutError(f"{url} did not answer within {timeout}s ({last})")


def port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    with socket.socket() as s:
        s.settimeout(timeout)
        return s.connect_ex((host, port)) == 0


@dataclass
class Container:
    """A running container started by a test; removed by :meth:`remove`."""

    name: str
    image: str
    started: float = field(default_factory=time.monotonic)

    def host_port(self, container_port: int) -> int:
        out = docker("port", self.name, f"{container_port}/tcp").stdout.strip().splitlines()
        return int(out[0].rsplit(":", 1)[1])

    def url(self, container_port: int = 8080) -> str:
        return f"http://127.0.0.1:{self.host_port(container_port)}"

    def running(self) -> bool:
        proc = docker("inspect", "-f", "{{.State.Running}}", self.name, check=False)
        return proc.stdout.strip() == "true"

    def inspect(self, fmt: str) -> str:
        return docker("inspect", "-f", fmt, self.name).stdout.strip()

    def logs(self) -> str:
        proc = docker("logs", self.name, check=False, timeout=60)
        return proc.stdout + proc.stderr

    def exec(self, *cmd: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return docker("exec", self.name, *cmd, check=check)

    def wait_healthy_api(self, timeout: float = 60) -> dict[str, Any]:
        status, body = wait_http(f"{self.url()}/api/health", timeout, self.running)
        assert status == 200, body
        return json.loads(body)["data"]

    def wait_docker_health(self, timeout: float = 60) -> str:
        deadline = time.monotonic() + timeout
        state = ""
        while time.monotonic() < deadline:
            state = self.inspect("{{.State.Health.Status}}")
            if state in ("healthy", "unhealthy"):
                return state
            time.sleep(1)
        return state

    def stop(self, timeout: int = 10) -> float:
        t0 = time.monotonic()
        docker("stop", "-t", str(timeout), self.name, timeout=timeout + 30)
        return time.monotonic() - t0

    def remove(self) -> None:
        docker("rm", "-f", "-v", self.name, check=False)
