"""Deployment tests (WP-D2, V3 deployment): the shipped Docker image, started for real.

    pytest -m docker tests/deploy                 # builds the image from this checkout
    HUB_IMAGE=hdmi-matrix-hub:ci pytest -m docker tests/deploy   # test an image built elsewhere (CI)

Everything runs in containers on a private Docker network:

    simulator container (BK-808 simulator, tools/simulator)  <-- matrix-sim:8443 / :2323
      ^
      hub container(s) from the image under test, published on free 127.0.0.1 ports

No test contacts a real matrix: the hub is pointed at the simulator, or at a
TEST-NET-1 address (192.0.2.1) where only start-up is being checked. The tests
are marked ``docker`` and deselected by default (pyproject addopts); CI runs
them in the docker-build job. Without Docker they skip, unless CI is set.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Iterator
from dataclasses import dataclass

import pytest

from ._docker import PUBLISH_IP, ROOT, Container, docker, docker_available, free_port, unique, wait_http
from ._evidence import RECORDER

SIM_ALIAS = "matrix-sim"
SIM_HTTPS_PORT = 8443
SIM_TELNET_PORT = 2323
SIM_CONTROL_PORT = 8444


@pytest.fixture(scope="session")
def hub_image() -> str:
    if not docker_available():
        if os.environ.get("CI"):
            pytest.fail("Docker is not available but the deployment tests were selected in CI")
        pytest.skip("Docker is not available")
    image = os.environ.get("HUB_IMAGE")
    if image:
        docker("image", "inspect", image)
        return image
    image = "hdmi-matrix-hub:deploy-test"
    docker("build", "-t", image, str(ROOT), timeout=1200)
    return image


@pytest.fixture(scope="session")
def network(hub_image: str) -> Iterator[str]:
    name = unique("hubtest")
    docker("network", "create", name)
    try:
        yield name
    finally:
        docker("network", "rm", name, check=False)


@dataclass
class Simulator:
    container: Container
    host: str = SIM_ALIAS
    https_port: int = SIM_HTTPS_PORT
    telnet_port: int = SIM_TELNET_PORT

    @property
    def control_url(self) -> str:
        return self.container.url(SIM_CONTROL_PORT)


@pytest.fixture(scope="session")
def simulator(hub_image: str, network: str, tmp_path_factory: pytest.TempPathFactory) -> Iterator[Simulator]:
    """The BK-808 simulator in a container built on the image under test (plus `cryptography` for its TLS cert)."""
    ctx = tmp_path_factory.mktemp("sim-image")
    shutil.copy(ROOT / "tools" / "__init__.py", ctx / "__init__.py")
    shutil.copytree(ROOT / "tools" / "simulator", ctx / "simulator",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (ctx / "Dockerfile").write_text(
        "ARG BASE\n"
        "FROM ${BASE}\n"
        "USER root\n"
        "RUN pip install 'cryptography>=42'\n"
        "COPY __init__.py /app/tools/__init__.py\n"
        "COPY simulator/ /app/tools/simulator/\n"
        "USER appuser\n",
        encoding="utf-8",
    )
    sim_image = f"{hub_image.split(':')[0]}-sim:deploy-test"
    docker("build", "--build-arg", f"BASE={hub_image}", "-t", sim_image, str(ctx), timeout=900)
    container = Container(unique("hubtest-sim"), sim_image)
    try:
        docker(
            "run", "-d", "--name", container.name, "--network", network, "--network-alias", SIM_ALIAS,
            "-p", f"{PUBLISH_IP}:{free_port()}:{SIM_CONTROL_PORT}", "--no-healthcheck",
            sim_image, "python", "-m", "tools.simulator", "--host", "0.0.0.0",
            "--https-port", str(SIM_HTTPS_PORT), "--telnet-port", str(SIM_TELNET_PORT),
            "--control-port", str(SIM_CONTROL_PORT),
        )
        wait_http(f"{container.url(SIM_CONTROL_PORT)}/_sim/health", 60, container.running)
        yield Simulator(container)
    finally:
        container.remove()


# ---------------------------------------------------------------------------
# Evidence (docs/validation/README.md): every test is one check of its scenario
# ---------------------------------------------------------------------------


def _scenario_of(item: pytest.Item) -> str | None:
    module = item.module.__name__.rsplit(".", 1)[-1] if getattr(item, "module", None) else ""
    if module == "test_compose":
        return "deploy.compose"
    if module == "test_docker_image":
        mode = getattr(item, "callspec", None) and item.callspec.params.get("hub")
        return f"deploy.image_{mode}" if mode else None
    return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()
    scenario = _scenario_of(item)
    if scenario is None:
        return
    # the call phase, or a setup that failed/skipped (the test body never ran)
    if report.when == "call" or (report.when == "setup" and not report.passed):
        doc = (getattr(item, "function", None).__doc__ or "").strip().splitlines()  # type: ignore[union-attr]
        name = item.originalname if hasattr(item, "originalname") else item.name
        description = name + (f": {doc[0]}" if doc else "")
        if report.passed:
            detail = f"passed in {report.duration:.1f}s"
        elif report.skipped:
            detail = f"skipped: {report.longrepr[2] if isinstance(report.longrepr, tuple) else report.longrepr}"
        else:
            detail = str(report.longrepr)[-1500:]
        RECORDER.get(scenario).check(description, report.outcome, detail)


def pytest_sessionfinish(session: pytest.Session) -> None:
    for path in RECORDER.write():
        print(f"deployment evidence: {path}")
