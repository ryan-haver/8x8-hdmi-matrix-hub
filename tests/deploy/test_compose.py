"""The compose files as documented (DEP-01, DEP-02, UC-11): `docker compose up -d` starts the hub.

Each variant runs as its own compose project with a unique container name, free
host ports and a temporary data folder, using the image under test (a test-only
override replaces `build:`). The matrix address is TEST-NET-1 (192.0.2.1), so no
real device is contacted; the image tests cover the simulator-backed behaviour.
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from tools.uc_remote_sim import UcRemoteSim

from ._docker import NO_MATRIX, ROOT, Container, docker, free_port, http, http_json, port_open, unique

pytestmark = pytest.mark.docker

PROBE_9095 = ("import socket, sys; s = socket.socket(); s.settimeout(2); "
              "sys.exit(0 if s.connect_ex(('127.0.0.1', 9095)) == 0 else 1)")


class Project:
    def __init__(self, files: list[str], env: dict[str, str], override: Path) -> None:
        self.name = unique("hubtest-compose")
        self.files = [str(ROOT / f) for f in files] + [str(override)]
        self.env = env
        self.container = Container(env["HUB_CONTAINER_NAME"], "")

    def compose(self, *args: str, check: bool = True):
        file_args = [a for f in self.files for a in ("-f", f)]
        return docker("compose", "-p", self.name, "--project-directory", str(ROOT), *file_args, *args,
                      env=self.env, check=check, timeout=300)

    def up(self) -> None:
        self.compose("up", "-d", "--no-build", "--pull", "never")

    def down(self) -> None:
        self.compose("down", "-v", "--timeout", "10", check=False)


@pytest.fixture
def project(hub_image: str, tmp_path: Path) -> Iterator[Callable[..., Project]]:
    projects: list[Project] = []
    override = tmp_path / "compose.test-image.yml"
    override.write_text(
        f"services:\n  hdmi-matrix-hub:\n    image: {hub_image}\n    build: !reset null\n", encoding="utf-8"
    )
    data = tmp_path / "data"
    data.mkdir()
    data.chmod(0o777)  # the container's UID 1000 must be able to write a host folder owned by the test user

    def make(*files: str, **extra: str) -> Project:
        env = {
            "HUB_CONTAINER_NAME": unique("hubtest-compose-hub"),
            "HUB_PORT": str(free_port()),
            "MATRIX_HOST": NO_MATRIX,
            "MATRIX_DATA_DIR": str(data),
            **extra,
        }
        for name in ("HUB_HOST_IP", "UC_HOST_PORT", "COMPOSE_FILE", "COMPOSE_PROFILES"):
            if name not in extra:
                env[name] = ""
        p = Project(list(files), env, override)
        projects.append(p)
        return p

    try:
        yield make
    finally:
        for p in projects:
            if p.container.running() and os.environ.get("CI"):
                print(p.container.logs()[-4000:])
            p.down()


def _wait_api(port: int, container: Container) -> dict:
    from ._docker import wait_http

    status, body = wait_http(f"http://127.0.0.1:{port}/api/health", 90, container.running)
    assert status == 200
    return json.loads(body)["data"]


def test_default_compose_starts_the_hub(project: Callable[..., Project]) -> None:
    """DEP-01: plain `docker compose up -d` starts the hub (no profiles); the integration is off."""
    p = project("docker-compose.yml")
    p.up()
    health = _wait_api(int(p.env["HUB_PORT"]), p.container)
    assert health["status"] == "healthy"
    assert http(f"http://127.0.0.1:{p.env['HUB_PORT']}/ui")[0] == 200
    assert p.container.exec("python", "-c", PROBE_9095, check=False).returncode != 0
    services = p.compose("ps", "--format", "json").stdout
    assert p.container.name in services


async def test_uc_bridge_compose_advertises_the_driver_url(project: Callable[..., Project]) -> None:
    """DEP-02/UC-11 bridge variant: mDNS off, 9095 published, driver URL from HUB_HOST_IP."""
    uc_port = free_port()
    p = project("docker-compose.yml", "docker-compose.uc-bridge.yml", HUB_HOST_IP="127.0.0.1", UC_HOST_PORT=str(uc_port))
    p.up()
    _wait_api(int(p.env["HUB_PORT"]), p.container)
    async with UcRemoteSim(f"ws://127.0.0.1:{uc_port}") as remote:
        meta = (await remote.get_driver_metadata())["msg_data"]
    assert meta["driver_url"] == f"ws://127.0.0.1:{uc_port}"
    assert "UC_DISABLE_MDNS_PUBLISH=true" in p.container.exec("env").stdout.splitlines()


def test_uc_compose_files_require_the_host_ip(project: Callable[..., Project]) -> None:
    for extra in ("docker-compose.uc-host.yml", "docker-compose.uc-bridge.yml"):
        p = project("docker-compose.yml", extra)
        proc = p.compose("config", check=False)
        assert proc.returncode != 0 and "HUB_HOST_IP" in proc.stderr, extra


@pytest.mark.skipif(sys.platform != "linux", reason="host networking needs a Linux Docker host")
async def test_uc_host_compose_listens_on_the_host(project: Callable[..., Project]) -> None:
    """DEP-02 recommended variant: host networking, mDNS published, API and 9095 directly on the host."""
    if port_open("127.0.0.1", 9095):
        pytest.skip("port 9095 is in use on this host")
    p = project("docker-compose.yml", "docker-compose.uc-host.yml", HUB_HOST_IP="127.0.0.1")
    p.up()
    assert p.container.inspect("{{.HostConfig.NetworkMode}}") == "host"
    _wait_api(int(p.env["HUB_PORT"]), p.container)
    status, _ = http_json(f"http://127.0.0.1:{p.env['HUB_PORT']}/api/health")
    assert status == 200
    async with UcRemoteSim("ws://127.0.0.1:9095") as remote:
        meta = (await remote.get_driver_metadata())["msg_data"]
    assert "driver_url" not in meta  # discovered by mDNS, no fixed URL
    assert "mDNS on, address 127.0.0.1" in p.container.logs()
