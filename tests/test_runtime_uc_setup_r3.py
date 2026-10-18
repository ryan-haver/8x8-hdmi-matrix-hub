"""Targeted R3 tests for `UCSetupHandler` and `UnfoldedCircleIntegration.bind_runtime` setup/auth/reconfigure flows."""

from __future__ import annotations

import json
import logging
import socket
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from hub.integrations.unfolded_circle import (
    UnfoldedCircleIntegration,
    config_from_env,
)
from tools.uc_remote_sim import UcRemoteSim


@dataclass(frozen=True)
class _FakeMatrixAddress:
    """Structural fake matching R1's frozen 5-field `hub.runtime.config.MatrixAddress`."""

    host: str
    port: int = 443
    telnet_port: int | None = None
    user: str | None = None
    password: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class _FakeReconfigureResult:
    """Structural fake matching R1's `hub.runtime.config.ReconfigureResult`."""

    success: bool
    error_kind: str | None = None
    connected: bool = False


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class _FakeRuntimeCoordinator:
    """Structural fake for R1 runtime hooks (`current_address` and `reconfigure`)."""

    def __init__(self, initial: _FakeMatrixAddress | None = None) -> None:
        self.address: _FakeMatrixAddress | None = initial
        self.reconfigure_calls: list[tuple[Any, bool]] = []
        self.next_error_kind: str | None = None
        self.hub = MagicMock()
        self.hub.connected = bool(self.address is not None and self.address.host)
        self.hub.snapshot = AsyncMock(
            return_value={
                "connected": True,
                "power": 1,
                "routing": [1, 2, 3, 4, 5, 6, 7, 8],
                "input_names": {n: f"Source {n}" for n in range(1, 9)},
                "output_names": {n: f"Zone {n}" for n in range(1, 9)},
            }
        )
        self.hub.switch = AsyncMock(return_value=True)
        self.hub.recall_preset = AsyncMock(return_value=True)
        self.hub.power = AsyncMock(return_value=True)
        self.hub.send_cec = AsyncMock(return_value=True)
        self.hub.run_action = AsyncMock(return_value={"success": True, "data": {}, "error": None, "status": 200})
        self.hub.subscribe = MagicMock(return_value=lambda: None)

    def current_address(self) -> _FakeMatrixAddress | None:
        return self.address

    async def reconfigure(self, address: Any, *, persist: bool = True) -> _FakeReconfigureResult:
        self.reconfigure_calls.append((address, persist))
        if self.next_error_kind is not None:
            err = self.next_error_kind
            return _FakeReconfigureResult(success=False, error_kind=err, connected=False)
        self.address = address
        self.hub.connected = True
        return _FakeReconfigureResult(success=True, error_kind=None, connected=True)


async def test_blank_setup_login_page_persists_credentials_and_publishes_entities(tmp_path: Path) -> None:
    port = _free_port()
    cfg = config_from_env(
        {
            "UC_ENABLED": "true",
            "UC_INTEGRATION_HTTP_PORT": str(port),
            "UC_INTEGRATION_INTERFACE": "127.0.0.1",
            "UC_DISABLE_MDNS_PUBLISH": "true",
            "DATA_DIR": str(tmp_path),
        }
    )
    coord = _FakeRuntimeCoordinator(None)
    integration = UnfoldedCircleIntegration(cfg, probe_fn=AsyncMock(return_value=None))
    integration.bind_runtime(reconfigure=coord.reconfigure, current_address=coord.current_address)

    await integration.start(coord.hub)
    try:
        async with UcRemoteSim(f"ws://127.0.0.1:{port}") as remote:
            # Unconfigured at start: 0 entities
            assert await remote.get_available_entities() == []

            # Step 1: address page only probes; does not call reconfigure or write config_state.json
            first = await remote.setup_driver({"host": "192.168.10.50", "port": 443})
            assert first.state == "WAIT_USER_ACTION"
            settings = {s["id"]: s for s in first.final["require_user_action"]["input"]["settings"]}
            assert list(settings.keys()) == ["info", "user", "password"]
            assert settings["user"]["field"] == {"text": {"value": "Admin"}}
            assert settings["password"]["field"] == {"password": {}}
            assert coord.reconfigure_calls == []
            assert not (tmp_path / "config_state.json").exists()

            # Step 2: submit login credentials
            second = await remote.set_driver_user_data(
                input_values={"user": "Admin", "password": "matrix-login-pw"}
            )
            assert second.final == {"event_type": "STOP", "state": "OK"}
            assert len(coord.reconfigure_calls) == 1
            called_addr, persist = coord.reconfigure_calls[0]
            assert persist is True
            assert (called_addr.host, called_addr.port) == ("192.168.10.50", 443)
            assert (called_addr.user, called_addr.password) == ("Admin", "matrix-login-pw")

            assert len(await remote.get_available_entities()) == 74
            assert (await remote.get_device_state())["msg_data"]["state"] == "CONNECTED"

            saved = json.loads((tmp_path / "config_state.json").read_text(encoding="utf-8"))
            assert (saved["host"], saved["port"]) == ("192.168.10.50", 443)
            assert (saved["user"], saved["password"]) == ("Admin", "matrix-login-pw")
            assert saved["input_names"]["1"] == "Source 1"
    finally:
        await integration.stop()


async def test_wrong_credentials_abort_and_unreachable_errors(tmp_path: Path, caplog: Any) -> None:
    port = _free_port()
    cfg = config_from_env(
        {
            "UC_ENABLED": "true",
            "UC_INTEGRATION_HTTP_PORT": str(port),
            "UC_INTEGRATION_INTERFACE": "127.0.0.1",
            "UC_DISABLE_MDNS_PUBLISH": "true",
            "DATA_DIR": str(tmp_path),
        }
    )
    coord = _FakeRuntimeCoordinator(None)
    integration = UnfoldedCircleIntegration(cfg, probe_fn=AsyncMock(return_value=None))
    integration.bind_runtime(reconfigure=coord.reconfigure, current_address=coord.current_address)

    await integration.start(coord.hub)
    try:
        async with UcRemoteSim(f"ws://127.0.0.1:{port}") as remote:
            # Invalid hostname and out-of-range port fail with NOT_FOUND before probing
            bad_host = await remote.setup_driver({"host": "https://bad-host/", "port": 443})
            assert bad_host.final == {"event_type": "STOP", "state": "ERROR", "error": "NOT_FOUND"}
            bad_port = await remote.setup_driver({"host": "127.0.0.1", "port": 70000})
            assert bad_port.state == "ERROR"

            # Wrong password on login page returns AUTHORIZATION_ERROR and never logs password
            secret_marker = "NeverLogThisPassword-9912"
            coord.next_error_kind = "auth"
            with caplog.at_level(logging.DEBUG):
                first = await remote.setup_driver({"host": "192.168.10.55", "port": 443})
                assert first.state == "WAIT_USER_ACTION"
                denied = await remote.set_driver_user_data(
                    input_values={"user": "Admin", "password": secret_marker}
                )
            assert denied.final == {"event_type": "STOP", "state": "ERROR", "error": "AUTHORIZATION_ERROR"}
            assert secret_marker not in caplog.text
            assert await remote.get_available_entities() == []
            assert not (tmp_path / "config_state.json").exists()

            # Abort on login page discards pending setup so late user data is rejected
            coord.next_error_kind = None
            coord.reconfigure_calls.clear()
            first2 = await remote.setup_driver({"host": "192.168.10.60", "port": 443})
            assert first2.state == "WAIT_USER_ACTION"
            await remote.abort_driver_setup("USER_CANCELLED")
            late = await remote.set_driver_user_data(
                input_values={"user": "Admin", "password": "admin"}
            )
            assert late.state == "ERROR"
            assert coord.reconfigure_calls == []
    finally:
        await integration.stop()


async def test_reconfigure_same_address_changed_address_and_restore_on_restart(tmp_path: Path) -> None:
    port = _free_port()
    cfg = config_from_env(
        {
            "UC_ENABLED": "true",
            "UC_INTEGRATION_HTTP_PORT": str(port),
            "UC_INTEGRATION_INTERFACE": "127.0.0.1",
            "UC_DISABLE_MDNS_PUBLISH": "true",
            "DATA_DIR": str(tmp_path),
        }
    )
    initial_addr = _FakeMatrixAddress(
        host="192.168.1.10",
        port=443,
        telnet_port=23,
        user="Admin",
        password="old-password",
    )
    coord = _FakeRuntimeCoordinator(initial_addr)
    integration = UnfoldedCircleIntegration(cfg, probe_fn=AsyncMock(return_value=None))
    integration.bind_runtime(reconfigure=coord.reconfigure, current_address=coord.current_address)

    await integration.start(coord.hub)
    try:
        async with UcRemoteSim(f"ws://127.0.0.1:{port}") as remote:
            await remote.subscribe_events(["media_player.output_1"])
            assert (await remote.select_source("media_player.output_1", "Source 2"))["code"] == 200

            # Same-address reconfigure completes without login page and preserves subscribed entities
            same = await remote.setup_driver({"host": "192.168.1.10", "port": 443}, reconfigure=True)
            assert same.final == {"event_type": "STOP", "state": "OK"}
            assert (await remote.select_source("media_player.output_1", "Source 3"))["code"] == 200

            # Changing address without current_password or with wrong current_password fails with AUTHORIZATION_ERROR
            no_pw = await remote.setup_driver({"host": "192.168.1.20", "port": 443}, reconfigure=True)
            assert no_pw.error == "AUTHORIZATION_ERROR"
            wrong_pw = await remote.setup_driver(
                {"host": "192.168.1.20", "port": 443, "current_password": "wrong"},
                reconfigure=True,
            )
            assert wrong_pw.error == "AUTHORIZATION_ERROR"

            # Changing address with valid current_password prompts for new matrix login and preserves subscriptions
            step1 = await remote.setup_driver(
                {"host": "192.168.1.20", "port": 8443, "current_password": "old-password"},
                reconfigure=True,
            )
            assert step1.state == "WAIT_USER_ACTION"
            step2 = await remote.set_driver_user_data(
                input_values={"user": "Admin", "password": "new-matrix-password"}
            )
            assert step2.final == {"event_type": "STOP", "state": "OK"}

            saved = json.loads((tmp_path / "config_state.json").read_text(encoding="utf-8"))
            assert (saved["host"], saved["port"]) == ("192.168.1.20", 8443)
            assert (saved["user"], saved["password"]) == ("Admin", "new-matrix-password")
            assert (await remote.select_source("media_player.output_1", "Source 4"))["code"] == 200
    finally:
        await integration.stop()

    # Restart a fresh integration instance against the same DATA_DIR and verify saved state is restored
    port2 = _free_port()
    cfg2 = config_from_env(
        {
            "UC_ENABLED": "true",
            "UC_INTEGRATION_HTTP_PORT": str(port2),
            "UC_INTEGRATION_INTERFACE": "127.0.0.1",
            "UC_DISABLE_MDNS_PUBLISH": "true",
            "DATA_DIR": str(tmp_path),
        }
    )
    integration2 = UnfoldedCircleIntegration(cfg2)
    integration2.bind_runtime(reconfigure=coord.reconfigure, current_address=coord.current_address)
    await integration2.start(coord.hub)
    try:
        assert integration2.migrated_config is not None
        assert (integration2.migrated_config["host"], integration2.migrated_config["port"]) == ("192.168.1.20", 8443)
        assert integration2.migrated_config["password"] == "new-matrix-password"
        async with UcRemoteSim(f"ws://127.0.0.1:{port2}") as remote2:
            assert len(await remote2.get_available_entities()) == 74
            await remote2.subscribe_events(["media_player.output_1"])
            assert (await remote2.select_source("media_player.output_1", "Source 5"))["code"] == 200
    finally:
        await integration2.stop()


async def test_uc_auth_token_guards_setup_and_reconfigure(tmp_path: Path, caplog: Any) -> None:
    port = _free_port()
    token = "SecretSetupToken-UC02"
    cfg = config_from_env(
        {
            "UC_ENABLED": "true",
            "UC_INTEGRATION_HTTP_PORT": str(port),
            "UC_INTEGRATION_INTERFACE": "127.0.0.1",
            "UC_DISABLE_MDNS_PUBLISH": "true",
            "UC_AUTH_TOKEN": token,
            "DATA_DIR": str(tmp_path),
        }
    )
    coord = _FakeRuntimeCoordinator(None)
    integration = UnfoldedCircleIntegration(cfg, probe_fn=AsyncMock(return_value=None))
    integration.bind_runtime(reconfigure=coord.reconfigure, current_address=coord.current_address)

    await integration.start(coord.hub)
    try:
        async with UcRemoteSim(f"ws://127.0.0.1:{port}") as remote:
            meta = (await remote.get_driver_metadata())["msg_data"]
            assert meta["pwd"] is True
            assert meta["setup_data_schema"]["settings"][-1]["id"] == "auth_token"

            with caplog.at_level(logging.DEBUG):
                assert (await remote.setup_driver({"host": "192.168.1.30", "port": 443})).error == "AUTHORIZATION_ERROR"
                assert (
                    await remote.setup_driver({"host": "192.168.1.30", "port": 443, "auth_token": "wrong"})
                ).error == "AUTHORIZATION_ERROR"

                first = await remote.setup_driver({"host": "192.168.1.30", "port": 443, "auth_token": token})
                assert first.state == "WAIT_USER_ACTION"
                done = await remote.set_driver_user_data(
                    input_values={"user": "Admin", "password": "admin"}
                )
                assert done.state == "OK"

                # Reconfigure also requires token
                assert (
                    await remote.setup_driver({"host": "192.168.1.30", "port": 443}, reconfigure=True)
                ).error == "AUTHORIZATION_ERROR"
                assert (
                    await remote.setup_driver({"host": "192.168.1.30", "port": 443, "pin": token}, reconfigure=True)
                ).state == "OK"
            assert token not in caplog.text
    finally:
        await integration.stop()
