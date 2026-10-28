"""Targeted R3 tests for `UCBridge` and `UnfoldedCircleIntegration` over live `ucapi` WebSocket and loader lifecycle."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from hub.integrations.base import IntegrationLoader, IntegrationRegistry
from hub.integrations.unfolded_circle import (
    APPROVED_GOLDEN_ENTITY_IDS,
    UCMdnsPublisher,
    UnfoldedCircleIntegration,
    config_from_env,
)
from hub.integrations.unfolded_circle.bridge import MAX_DIAGNOSTIC_UPDATES
from tools.uc_remote_sim import UcRemoteSim

GOLDEN_PATH = Path(__file__).parent / "uc" / "golden" / "entities.json"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def _golden_view(entity: dict[str, Any]) -> dict[str, Any]:
    view: dict[str, Any] = {
        "entity_id": entity["entity_id"],
        "entity_type": entity["entity_type"],
        "features": entity.get("features") or [],
    }
    if entity.get("device_class"):
        view["device_class"] = entity["device_class"]
    commands = (entity.get("options") or {}).get("simple_commands")
    if commands:
        view["simple_commands"] = commands
    return view


def _seed_snapshot() -> dict[str, Any]:
    return {
        "connected": True,
        "power": 1,
        "routing": [1, 2, 3, 4, 5, 6, 7, 8],
        "input_names": {
            1: "Apple TV",
            2: "Chromecast",
            3: "Blu-ray",
            4: "Switch",
            5: "PC",
            6: "PS5",
            7: "Camera",
            8: "Guest HDMI",
        },
        "output_names": {
            1: "Living Room TV",
            2: "Bedroom TV",
            3: "Kitchen",
            4: "Office",
            5: "Patio",
            6: "Den",
            7: "Gym",
            8: "Rec Room",
        },
        "preset_names": {
            1: "Apple TV Everywhere",
            2: "Movie Night",
            3: "PS5",
            4: "Preset 4",
            5: "Preset 5",
            6: "Preset 6",
            7: "Preset 7",
            8: "Preset 8",
        },
        "favorite_presets": [1, 2],
        "input_signals": [1, 1, 0, 0, 1, 1, 0, 0],
        "output_displays": [1, 1, 1, 0, 0, 1, 0, 0],
        "input_cables": [1, 1, 1, 0, 1, 1, 0, 0],
        "output_cables": [1, 1, 1, 0, 0, 1, 0, 0],
    }


def _make_hub_double() -> MagicMock:
    hub = MagicMock()
    hub.connected = True
    hub.snapshot = AsyncMock(return_value=_seed_snapshot())
    hub.switch = AsyncMock(return_value=True)
    hub.recall_preset = AsyncMock(return_value=True)
    hub.power = AsyncMock(return_value=True)
    hub.send_cec = AsyncMock(return_value=True)
    hub.run_action = AsyncMock(return_value={"success": True, "data": {}, "error": None, "status": 200})
    hub._subscribers = []

    def _sub(cb: Any) -> Any:
        hub._subscribers.append(cb)
        return lambda: hub._subscribers.remove(cb) if cb in hub._subscribers else None

    hub.subscribe = MagicMock(side_effect=_sub)
    return hub


async def test_loader_lifecycle_and_golden_catalog_over_live_ucapi_ws(tmp_path: Path) -> None:
    port = _free_port()
    env = {
        "UC_ENABLED": "true",
        "UC_INTEGRATION_HTTP_PORT": str(port),
        "UC_INTEGRATION_INTERFACE": "127.0.0.1",
        "UC_DISABLE_MDNS_PUBLISH": "true",
        "DATA_DIR": str(tmp_path),
    }
    (tmp_path / "config_state.json").write_text(
        json.dumps({"host": "127.0.0.1", "port": 443, "telnet_port": 23}),
        encoding="utf-8",
    )

    registry = IntegrationRegistry()
    registry.register(
        "unfolded_circle",
        "UC_ENABLED",
        "hub.integrations.unfolded_circle:UnfoldedCircleIntegration",
    )
    loader = IntegrationLoader(registry, env)
    hub = _make_hub_double()

    await loader.start(hub)
    try:
        assert loader.routes() == []
        summary = loader.health_summary()["unfolded_circle"]
        assert summary["status"] == "ok"
        assert summary["entity_count"] == 74
        assert summary["configured_entity_count"] == 0

        async with UcRemoteSim(f"ws://127.0.0.1:{port}") as remote:
            ver = await remote.get_driver_version()
            assert ver["code"] == 200
            assert ver["msg_data"]["name"] == "HDMI Matrix"

            meta = (await remote.get_driver_metadata())["msg_data"]
            assert "driver_url" not in meta
            assert [s["id"] for s in meta["setup_data_schema"]["settings"]] == [
                "info",
                "host",
                "port",
                "current_password",
            ]

            available = await remote.get_available_entities()
            assert len(available) == 74
            assert {e["entity_id"] for e in available} == APPROVED_GOLDEN_ENTITY_IDS

            golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
            views = sorted((_golden_view(e) for e in available), key=lambda x: x["entity_id"])
            assert views == golden["entities"]

            # Available entities are NOT configured until subscribed
            assert await remote.get_entity_states() == []
            assert (await remote.button_push("button.preset_1"))["code"] == 404

            # Subscribe a subset of entities and verify only those become configured
            await remote.subscribe_events(
                [
                    "media_player.output_1",
                    "remote.output_1_cec",
                    "remote.input_2_cec",
                    "switch.matrix_power",
                    "button.preset_3",
                ]
            )
            states = {s["entity_id"]: s["attributes"] for s in await remote.get_entity_states()}
            assert set(states.keys()) == {
                "media_player.output_1",
                "remote.output_1_cec",
                "remote.input_2_cec",
                "switch.matrix_power",
                "button.preset_3",
            }
            assert states["media_player.output_1"]["source"] == "Apple TV"
            assert states["switch.matrix_power"]["state"] == "ON"

            # Unsubscribed entity still returns 404
            assert (await remote.button_push("button.preset_1"))["code"] == 404
            # Subscribed preset button succeeds
            assert (await remote.button_push("button.preset_3"))["code"] == 200
            hub.recall_preset.assert_awaited_once_with(3)

            # Output CEC remote accepts display commands and rejects source-only commands with 400
            hub.send_cec.reset_mock()
            assert (await remote.remote_send_cmd("remote.output_1_cec", "VOLUME_UP"))["code"] == 200
            hub.send_cec.assert_awaited_once_with("output", 1, "VOLUME_UP")

            hub.send_cec.reset_mock()
            for invalid_display_cmd in ("UP", "SELECT", "MENU", "BACK", "PLAY"):
                resp = await remote.remote_send_cmd("remote.output_1_cec", invalid_display_cmd)
                assert resp["code"] == 400, invalid_display_cmd
            hub.send_cec.assert_not_awaited()

            # Input CEC remote accepts navigation and playback keys
            assert (await remote.remote_send_cmd("remote.input_2_cec", "SELECT"))["code"] == 200
            hub.send_cec.assert_awaited_once_with("input", 2, "SELECT")

            # Unsubscribing removes from configured_entities so subsequent commands return 404
            await remote.unsubscribe_events(["button.preset_3"])
            assert (await remote.button_push("button.preset_3"))["code"] == 404
    finally:
        await loader.stop()

    assert not _port_open("127.0.0.1", port)


async def test_mdns_advertises_only_after_ws_listening_and_rolls_back_on_failure(tmp_path: Path) -> None:
    port = _free_port()
    (tmp_path / "config_state.json").write_text(
        json.dumps({"host": "127.0.0.1", "port": 443}),
        encoding="utf-8",
    )
    cfg = config_from_env(
        {
            "UC_ENABLED": "true",
            "UC_INTEGRATION_HTTP_PORT": str(port),
            "UC_INTEGRATION_INTERFACE": "127.0.0.1",
            "UC_DISABLE_MDNS_PUBLISH": "false",
            "DATA_DIR": str(tmp_path),
        }
    )

    port_open_at_mdns_register: list[bool] = []
    fake_zc = MagicMock()

    async def _register(_info: Any) -> None:
        port_open_at_mdns_register.append(_port_open("127.0.0.1", port))

    fake_zc.async_register_service = AsyncMock(side_effect=_register)
    fake_zc.async_unregister_service = AsyncMock()

    mdns = UCMdnsPublisher(cfg, zeroconf=fake_zc)
    integration = UnfoldedCircleIntegration(cfg, mdns_publisher=mdns)
    hub = _make_hub_double()

    await integration.start(hub)
    assert port_open_at_mdns_register == [True]
    assert integration.mdns.published is True
    await integration.stop()
    assert integration.mdns.published is False
    assert not _port_open("127.0.0.1", port)

    # Now simulate mDNS failure during start and verify WebSocket server and hub subscription roll back
    failing_zc = MagicMock()
    failing_zc.async_register_service = AsyncMock(side_effect=RuntimeError("mDNS register boom"))
    failing_zc.async_unregister_service = AsyncMock()
    failing_mdns = UCMdnsPublisher(cfg, zeroconf=failing_zc)
    integration2 = UnfoldedCircleIntegration(cfg, mdns_publisher=failing_mdns)

    with pytest.raises(RuntimeError, match="mDNS register boom"):
        await integration2.start(hub)

    assert integration2.running is False
    assert integration2.mdns.published is False
    assert hub._subscribers == []
    assert not _port_open("127.0.0.1", port)


async def test_pushed_updates_diagnostic_buffer_is_bounded(tmp_path: Path) -> None:
    port = _free_port()
    (tmp_path / "config_state.json").write_text(
        json.dumps({"host": "127.0.0.1", "port": 443}),
        encoding="utf-8",
    )
    cfg = config_from_env(
        {
            "UC_ENABLED": "true",
            "UC_INTEGRATION_HTTP_PORT": str(port),
            "UC_INTEGRATION_INTERFACE": "127.0.0.1",
            "UC_DISABLE_MDNS_PUBLISH": "true",
            "DATA_DIR": str(tmp_path),
        }
    )
    hub = _make_hub_double()
    integration = UnfoldedCircleIntegration(cfg)
    await integration.start(hub)
    try:
        cb = hub._subscribers[0]
        for i in range(150):
            in_port = (i % 8) + 1
            cb("routing", {"output": 1, "input": in_port})
        assert len(integration.pushed_updates) == MAX_DIAGNOSTIC_UPDATES
    finally:
        await integration.stop()
