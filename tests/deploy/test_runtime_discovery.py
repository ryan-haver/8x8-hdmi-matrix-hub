"""Shipped HA discovery across a private Docker bridge; no physical LAN claim."""

from __future__ import annotations

import ipaddress
import json
import time

import pytest

from hub import __version__

from ._docker import PUBLISH_IP, ROOT, Container, docker, free_port, http_json, unique
from ._evidence import RECORDER
from .conftest import Simulator

pytestmark = pytest.mark.docker
SERVICE_TYPE = "_orei-hdmi-matrix._tcp.local."


def _events(observer: Container) -> list[dict]:
    return [json.loads(line) for line in observer.logs().splitlines() if line.startswith('{"event":')]


def test_image_announces_reachable_api_and_withdraws_on_sigterm(
    hub_image: str, network: str, simulator: Simulator,
) -> None:
    """Separate real Zeroconf sockets resolve TXT/address/port, GET health and observe goodbye."""
    # Use an explicit advertised address, as a host-network installation can.
    # This network is allocated by the Docker fixture, never a user's LAN.
    subnet = json.loads(docker("network", "inspect", network).stdout)[0]["IPAM"]["Config"][0]["Subnet"]
    advertised = str(ipaddress.ip_network(subnet).broadcast_address - 1)
    name = unique("hubtest-discovery")
    hub = Container(unique("hubtest-ha"), hub_image)
    observer = Container(unique("hubtest-mdns-observer"), hub_image)
    volume = unique("hubtest-discovery-data")
    env = {
        "UC_ENABLED": "false", "FLIC_ENABLED": "false", "HA_DISCOVERY_ENABLED": "true",
        "HOST_IP": advertised, "API_PORT": "8080", "HA_DISCOVERY_SERVICE_NAME": name,
        "MATRIX_HOST": simulator.host, "MATRIX_PORT": str(simulator.https_port),
        "OREI_TELNET_PORT": str(simulator.telnet_port),
    }
    record = RECORDER.start("deploy.discovery")
    record.entry = f"docker image {hub_image} (normal python run.py CMD, HA discovery enabled)"
    record.image_digest = docker("image", "inspect", "-f", "{{.Id}}", hub_image).stdout.strip()
    record.hub_env = env
    record.notes.append("Real mDNS on a private Docker bridge, not physical LAN visibility or HA config-flow discovery.")
    try:
        docker("volume", "create", volume)
        args = ["run", "-d", "--name", hub.name, "--network", network, "--ip", advertised,
                "-p", f"{PUBLISH_IP}:{free_port()}:8080", "-v", f"{volume}:/data"]
        for key, value in env.items():
            args += ["-e", f"{key}={value}"]
        record.procedure.append("docker " + " ".join([*args, hub_image]))
        docker(*args, hub_image)
        hub.wait_healthy_api(60)
        status, health = http_json(f"{hub.url()}/api/health")
        assert status == 200, health
        probe = ROOT / "tests/deploy/fixtures/discovery_probe.py"
        docker("run", "-d", "--name", observer.name, "--network", network,
               "--no-healthcheck", "-v", f"{probe}:/probe.py:ro", hub_image,
               "python", "/probe.py", f"{name}.{SERVICE_TYPE}")
        record.procedure.append("Separate observer container runs the checked-in discovery_probe.py against the unique service name.")
        deadline = time.monotonic() + 40
        while not (events := _events(observer)):
            assert observer.running(), observer.logs()
            assert time.monotonic() < deadline, observer.logs() + hub.logs()[-4000:]
            time.sleep(0.5)
        found = events[0]
        assert found["event"] == "found", found
        assert found["addresses"] == [advertised] and found["port"] == 8080, found
        assert found["properties"]["version"] == __version__
        assert found["properties"]["service"] == "orei_hdmi_matrix"
        assert found["properties"]["api_port"] == "8080" and found["properties"]["path"] == "/api"
        assert found["health"]["data"]["status"] == "healthy"
        record.state_before = {"advertisement": found}
        assert hub.stop(timeout=10) < 8
        assert hub.inspect("{{.State.ExitCode}}") == "0"
        result = docker("wait", observer.name, timeout=30)
        assert result.stdout.strip() == "0", observer.logs()
        events = _events(observer)
        assert events[-1] == {"event": "removed", "name": f"{name}.{SERVICE_TYPE}"}
        record.state_after = {"advertisement": events[-1]}
    finally:
        observer.remove()
        hub.remove()
        docker("volume", "rm", volume, check=False)
