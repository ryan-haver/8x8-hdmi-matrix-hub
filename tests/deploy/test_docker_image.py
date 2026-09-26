"""The shipped image, started the two ways a user runs it (V3 deployment, WP-D2).

``core``: integrations off (the default). ``uc``: the Remote 3 integration on, in
bridge networking (mDNS off, UC_DRIVER_URL set), with ``config_state.json`` in the
data volume the way a completed Remote setup leaves it. Both point at the
simulator container. Tests run in file order for each mode; the last one stops
the container.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from dataclasses import dataclass

import pytest

from tools.uc_remote_sim import UcRemoteSim

from ._docker import PUBLISH_IP, Container, docker, free_port, http, http_json, unique
from ._evidence import RECORDER
from .conftest import Simulator

pytestmark = pytest.mark.docker

THEMES = {
    "presets": [{"primaryH": 10 * i, "secondaryH": 20 * i, "name": f"Deploy {i}"} for i in range(1, 5)],
    "activePresetIndex": 2,
    "cardOpacity": 0.5,
}
PROFILE = {"id": "deploy-test", "name": "Deploy test", "outputs": {"1": {"input": 3}, "2": {"input": 4}}}


@dataclass
class Hub:
    mode: str
    container: Container
    volume: str
    uc_host_port: int | None = None

    @property
    def url(self) -> str:
        return self.container.url(8080)

    @property
    def uc_url(self) -> str:
        return f"ws://127.0.0.1:{self.uc_host_port}"


def _seed_remote_setup(image: str, volume: str, sim: Simulator) -> None:
    """What driver.py save_config() leaves after a Remote setup against the simulator."""
    config = {"host": sim.host, "port": sim.https_port}
    docker("run", "--rm", "-v", f"{volume}:/data", "--entrypoint", "python", image, "-c",
           f"import json; json.dump({json.dumps(config)}, open('/data/config_state.json', 'w'))")


@pytest.fixture(scope="module", params=["core", "uc"])
def hub(request: pytest.FixtureRequest, hub_image: str, network: str, simulator: Simulator) -> Iterator[Hub]:
    mode = request.param
    volume = unique("hubtest-data")
    docker("volume", "create", volume)
    container = Container(unique(f"hubtest-{mode}"), hub_image)
    args = [
        "run", "-d", "--name", container.name, "--network", network,
        "-p", f"{PUBLISH_IP}:{free_port()}:8080", "-v", f"{volume}:/data",
        # The image's own HEALTHCHECK command, checked more often so the test does not wait 30 s.
        "--health-interval", "2s", "--health-start-period", "30s",
        "-e", f"MATRIX_HOST={simulator.host}", "-e", f"MATRIX_PORT={simulator.https_port}",
        "-e", f"OREI_TELNET_PORT={simulator.telnet_port}",
        # Every import is traced to stderr: proves which modules the process loaded.
        "-e", "PYTHONPROFILEIMPORTTIME=1",
    ]
    uc_host_port = None
    record = RECORDER.start(f"deploy.image_{mode}")
    try:
        if mode == "uc":
            _seed_remote_setup(hub_image, volume, simulator)
            record.procedure.append(f"seed /data/config_state.json (a completed Remote setup): {simulator.host}:"
                                    f"{simulator.https_port}")
            uc_host_port = free_port()
            args += [
                "-p", f"{PUBLISH_IP}:{uc_host_port}:9095",
                "-e", "UC_ENABLED=true", "-e", "UC_DISABLE_MDNS_PUBLISH=true",
                "-e", f"UC_DRIVER_URL=ws://127.0.0.1:{uc_host_port}",
            ]
        record.procedure.append("docker " + " ".join(args + [hub_image]))
        record.entry = f"docker image {hub_image} (python run.py, UC_ENABLED={'true' if mode == 'uc' else 'unset'})"
        record.image_digest = docker("image", "inspect", "-f", "{{.Id}}", hub_image).stdout.strip()
        record.hub_env = {a.split("=", 1)[0]: a.split("=", 1)[1] for a in args[args.index("-e"):] if "=" in a}
        record.state_before = {"routing": _sim_routing(simulator)}
        docker(*args, hub_image)
        container.wait_healthy_api(90)
        yield Hub(mode, container, volume, uc_host_port)
        record.state_after = {"routing": _sim_routing(simulator)}
    finally:
        if request.node.session.testsfailed:
            lines = [line for line in container.logs().splitlines() if not line.startswith("import time:")]
            print(f"----- {container.name} logs (tail) -----")
            print("\n".join(lines[-80:]))
        container.remove()
        docker("volume", "rm", "-f", volume, check=False)


def _wait_connected(hub: Hub, timeout: float = 45) -> dict:
    import time

    deadline = time.monotonic() + timeout
    data: dict = {}
    while time.monotonic() < deadline:
        status, body = http_json(f"{hub.url}/api/status")
        data = body.get("data") or {}
        if status == 200 and data.get("connected"):
            return data
        time.sleep(1)
    raise AssertionError(f"hub never reported the simulator connected: {data}")


def _sim_routing(sim: Simulator) -> dict[str, int]:
    status, state = http_json(f"{sim.control_url}/_sim/state")
    assert status == 200
    return {str(i + 1): out["source"] for i, out in enumerate(state["outputs"])}


# ---------------------------------------------------------------------------


def test_health_endpoint_is_healthy(hub: Hub) -> None:
    status, body = http_json(f"{hub.url}/api/health")
    assert status == 200 and body["data"]["status"] == "healthy"


def test_image_healthcheck_reports_healthy(hub: Hub) -> None:
    assert hub.container.wait_docker_health(60) == "healthy"


def test_web_ui_and_kiosk_are_served(hub: Hub) -> None:
    for path, marker in (("/ui", b"<html"), ("/kiosk", b"<html"), ("/css/style.css", b"{")):
        status, body = http(f"{hub.url}{path}")
        assert status == 200, path
        assert marker in body.lower(), path


def test_status_comes_from_the_simulator(hub: Hub, simulator: Simulator) -> None:
    data = _wait_connected(hub)
    assert data["routing"] == _sim_routing(simulator)


def test_switch_reaches_the_simulator(hub: Hub, simulator: Simulator) -> None:
    _wait_connected(hub)
    before = _sim_routing(simulator)
    target = 7 if before["1"] != 7 else 6
    status, body = http_json(f"{hub.url}/api/switch", method="POST", body={"input": target, "output": 1})
    assert status == 200, body
    assert _sim_routing(simulator)["1"] == target
    # put it back for the other mode
    http_json(f"{hub.url}/api/switch", method="POST", body={"input": before["1"], "output": 1})


def test_integration_port_open_only_with_uc(hub: Hub) -> None:
    probe = ("import socket, sys; s = socket.socket(); s.settimeout(2); "
             "sys.exit(0 if s.connect_ex(('127.0.0.1', 9095)) == 0 else 1)")
    listening = hub.container.exec("python", "-c", probe, check=False).returncode == 0
    assert listening is (hub.mode == "uc")


async def test_remote_reaches_the_integration_at_the_driver_url(hub: Hub) -> None:
    if hub.mode != "uc":
        pytest.skip("integration disabled")
    async with UcRemoteSim(hub.uc_url) as remote:
        meta = (await remote.get_driver_metadata())["msg_data"]
        entities = await remote.get_available_entities()
    assert meta["driver_url"] == hub.uc_url  # UC_DRIVER_URL (UC-03), not ws://<container id>:9095
    assert hub.container.name not in json.dumps(meta)
    assert len(entities) > 0


def test_ucapi_imported_only_with_uc(hub: Hub) -> None:
    logs = hub.container.logs()
    imported = set(re.findall(r"^import time:.*\|\s+(\S+)\s*$", logs, flags=re.MULTILINE))
    assert "rest_api" in imported  # the trace is there
    ucapi_modules = {m for m in imported if m == "ucapi" or m.startswith("ucapi.")}
    if hub.mode == "uc":
        assert "ucapi" in ucapi_modules
    else:
        assert ucapi_modules == set()
        assert "ucapi imported: False" in logs


def test_runs_as_non_root(hub: Hub) -> None:
    assert hub.container.inspect("{{.Config.User}}") == "appuser"
    status = hub.container.exec("cat", "/proc/1/status").stdout
    uids = re.search(r"^Uid:\s+(\d+)\s+(\d+)", status, flags=re.MULTILINE)
    assert uids and uids.group(1) == uids.group(2) == "1000"
    # the application code is not writable by the hub
    assert hub.container.exec("sh", "-c", "test -w /app/run.py", check=False).returncode != 0


def test_data_persists_across_restart(hub: Hub) -> None:
    status, body = http_json(f"{hub.url}/api/themes", method="PUT", body=THEMES)
    assert status == 200, body
    status, body = http_json(f"{hub.url}/api/profile", method="POST", body=PROFILE)
    assert status == 200, body

    docker("restart", "-t", "10", hub.container.name, timeout=60)
    hub.container.wait_healthy_api(90)

    status, body = http_json(f"{hub.url}/api/themes")
    assert status == 200 and body["data"]["activePresetIndex"] == 2
    assert [p["name"] for p in body["data"]["presets"]] == [p["name"] for p in THEMES["presets"]]
    status, body = http_json(f"{hub.url}/api/profile/{PROFILE['id']}")
    assert status == 200, body
    assert body["data"]["name"] == PROFILE["name"]
    files = hub.container.exec("sh", "-c", "cd /data && ls").stdout.split()
    assert "themes.json" in files and "profiles.json" in files


def test_stops_cleanly_on_sigterm(hub: Hub) -> None:
    seconds = hub.container.stop(timeout=10)
    assert seconds < 8, f"docker stop took {seconds:.1f}s (SIGTERM not handled, killed after the grace period)"
    assert hub.container.inspect("{{.State.ExitCode}}") == "0"
