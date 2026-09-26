"""Scripted-Remote harness (UC-21): simulator -> hub with the UC driver -> scripted Remote 3.

Fixture chain (docs/audits/UC_INTEGRATION_AUDIT.md §7)::

    uc_simulator (session)   python -m tools.simulator on free ports (HTTPS, Telnet, /_sim control)
      -> sim                 SimDevice: reset to the seed state before each test; ground truth for
                             assertions (state, command log, fault injection)
        -> uc_hub            the real hub, started the way it ships: `python run.py` in legacy mode,
                             which runs src/driver.py (REST API + web UI + ucapi integration). Free
                             ports, UC_DISABLE_MDNS_PUBLISH=true, a temp UC_CONFIG_HOME/MATRIX_DATA_DIR
                             seeded with config_state.json (a configured install), POLLING_INTERVAL=1.
          -> uc_remote       tools.uc_remote_sim.UcRemoteSim, connected, authenticated and attached
                             like a Remote after start-up: `connect` event, get_available_entities,
                             subscribe_events for every entity.

The driver runs as a subprocess because driver.py only works as ``__main__``
(its ``api`` global is created there, UC-19) and owns its event loop and signal
handlers. That is also the most faithful setup: nothing is imported or patched.
``uc_hub_factory`` starts more hubs, or hubs with other options (unconfigured
for the setup flow, extra environment). The simulator is a subprocess too, so
the driver keeps being served while a test blocks.

Tests assert effects on the simulator (state and command log) and on what the
Remote receives, never just a status code. Known bugs are strict xfails naming
their register row (``_helpers.known_bug``): when WP-B2/B3 fix one, its test
passes, pytest reports XPASS(strict), and the fixing PR removes the marker.

Run: ``pytest tests/uc`` (about 5 minutes; every test starts its own driver).
A failing test prints the tail of the driver log.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from pathlib import Path
from typing import Any

import aiohttp
import pytest

from tools.uc_remote_sim import UcRemoteSim
from tools.validate.device import SimDevice
from tools.validate.runner import WsObserver
from tools.validate.stack import HubProcess, SimulatorProcess

from ._helpers import INPUT_NAMES, OUTPUT_NAMES, POLL

HubFactory = Callable[..., Awaitable[HubProcess]]
RemoteFactory = Callable[..., Awaitable[UcRemoteSim]]


@pytest.fixture(scope="session")
def uc_log_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("uc-logs")


@pytest.fixture(scope="session")
def uc_simulator(uc_log_dir: Path) -> Any:
    """One simulator process for the session; every test resets it (see ``sim``)."""
    proc = SimulatorProcess(log_dir=uc_log_dir / "simulator")
    proc.start()
    try:
        yield proc
    finally:
        proc.stop()


@pytest.fixture
async def sim(uc_simulator: SimulatorProcess) -> AsyncIterator[SimDevice]:
    """The simulator in its seed state, with no faults and an empty command log."""
    async with SimDevice(uc_simulator.control_url) as dev:
        await dev.reset()
        try:
            yield dev
        finally:
            await dev.clear_faults()


@pytest.fixture
async def uc_hub_factory(uc_simulator: SimulatorProcess, sim: SimDevice, tmp_path: Path) -> AsyncIterator[HubFactory]:
    """Start hubs running the UC driver; all of them are stopped after the test.

    Keyword options: ``restore`` (seed config_state.json, default True),
    ``polling_interval`` (default ``POLL``), ``extra_env``, ``wait`` (wait for the
    ports, default True). The hub log is printed when the test fails.
    """
    hubs: list[HubProcess] = []

    async def start(*, restore: bool = True, polling_interval: int = POLL, extra_env: dict[str, str] | None = None,
                    wait: bool = True) -> HubProcess:
        hub = HubProcess(
            matrix_host=uc_simulator.host,
            matrix_port=uc_simulator.https_port,
            telnet_port=uc_simulator.telnet_port,
            log_dir=tmp_path / f"hub{len(hubs) + 1}",
            mode="uc",
            uc_restore=restore,
            # What driver.py save_config() leaves after a successful setup against the seed state.
            uc_config_extra={
                "input_names": {str(i): n for i, n in enumerate(INPUT_NAMES, 1)},
                "output_names": {str(i): n for i, n in enumerate(OUTPUT_NAMES, 1)},
            },
            polling_interval=polling_interval,
            stop_timeout=3,
            keep_data_on_restart=True,
            # An unconfigured hub has no matrix: without a saved setup the driver would otherwise use
            # MATRIX_HOST, which the stack always sets (tests that want that pass it in extra_env).
            extra_env={"LOG_LEVEL": "DEBUG", **({} if restore else {"MATRIX_HOST": ""}), **(extra_env or {})},
        )
        hubs.append(hub)
        hub.launch()
        if wait:
            await asyncio.to_thread(hub.wait_ready, 60)
        return hub

    try:
        yield start
    finally:
        for hub in hubs:
            await asyncio.to_thread(hub.stop)
            _print_log_tail(hub)


def _print_log_tail(hub: HubProcess, lines: int = 60) -> None:
    """pytest shows captured stdout only for failed tests."""
    for path in sorted(hub.log_dir.glob("hub-uc-*.log")):
        text = path.read_text(encoding="utf-8", errors="replace").splitlines()
        print(f"----- {path} (last {lines} of {len(text)} lines) -----")
        print("\n".join(text[-lines:]))


@pytest.fixture
async def uc_hub(uc_hub_factory: HubFactory) -> HubProcess:
    """A configured hub: the driver restored its matrix connection and 74 entities at start-up."""
    return await uc_hub_factory()


@pytest.fixture
async def uc_remote_factory(uc_hub: HubProcess) -> AsyncIterator[RemoteFactory]:
    """Open scripted-Remote connections (to ``uc_hub`` unless ``url`` is given)."""
    remotes: list[UcRemoteSim] = []

    async def open_remote(*, url: str | None = None, attach: bool = True,
                          entity_ids: list[str] | None = None) -> UcRemoteSim:
        remote = UcRemoteSim(url or uc_hub.uc_url)
        remotes.append(remote)
        await remote.connect()
        if attach:
            await remote.attach(entity_ids)
        return remote

    try:
        yield open_remote
    finally:
        for remote in remotes:
            await remote.close()


@pytest.fixture
async def uc_remote(uc_remote_factory: RemoteFactory) -> UcRemoteSim:
    """A Remote connected to ``uc_hub`` and subscribed to every available entity."""
    return await uc_remote_factory()


@pytest.fixture
async def hub_api(uc_hub: HubProcess) -> AsyncIterator[aiohttp.ClientSession]:
    """The same hub's REST API, as the web app uses it."""
    async with aiohttp.ClientSession(base_url=uc_hub.base_url, headers={"X-Forwarded-For": "10.88.0.1"},
                                     timeout=aiohttp.ClientTimeout(total=30)) as session:
        yield session


@pytest.fixture
async def hub_ws(uc_hub: HubProcess) -> AsyncIterator[WsObserver]:
    """A web-app client on the hub's /ws, recording every event (routing_change, ...)."""
    observer = WsObserver(uc_hub.base_url.replace("http", "ws", 1) + "/ws", "10.88.0.2")
    await observer.start()
    assert observer.error is None, observer.error
    try:
        yield observer
    finally:
        await observer.stop()
