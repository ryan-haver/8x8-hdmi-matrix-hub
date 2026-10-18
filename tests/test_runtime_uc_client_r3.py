"""Targeted R3 tests for typed `HubSnapshot` / `HubEvent` consumption and `HubClientLocal` contract in UC integration."""

from __future__ import annotations

import json
import socket
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

from hub.integrations.hub_client import HubEvent, HubSnapshot
from hub.integrations.unfolded_circle import (
    UnfoldedCircleIntegration,
    config_from_env,
)
from tools.uc_remote_sim import UcRemoteSim


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@dataclass
class _ExtendedHubSnapshot(HubSnapshot):
    """Typed `HubSnapshot` carrying both existing `power` and R2 contract fields."""

    on: bool = True
    preset_names: dict[int, str] = field(default_factory=dict)
    favorite_presets: list[int] = field(default_factory=list)
    input_signals: Any = field(default_factory=list)
    output_displays: Any = field(default_factory=list)
    input_cables: Any = field(default_factory=list)
    output_cables: Any = field(default_factory=list)
    connection_state: str = "CONNECTED"
    catalog: dict[str, list[dict[str, Any]]] = field(default_factory=dict)


def _make_typed_snapshot(*, connected: bool = True, on: bool = True) -> _ExtendedHubSnapshot:
    return _ExtendedHubSnapshot(
        connected=connected,
        power=on,
        on=on,
        routing=[1, 2, 3, 4, 5, 6, 7, 8],
        input_names={
            1: "Apple TV",
            2: "Chromecast",
            3: "Blu-ray",
            4: "Switch",
            5: "PC",
            6: "PS5",
            7: "Camera",
            8: "Guest HDMI",
        },
        output_names={
            1: "Living Room TV",
            2: "Bedroom TV",
            3: "Kitchen",
            4: "Office",
            5: "Patio",
            6: "Den",
            7: "Gym",
            8: "Rec Room",
        },
        preset_names={
            1: "Apple TV Everywhere",
            2: "Movie Night",
            3: "PS5",
            4: "Preset 4",
            5: "Preset 5",
            6: "Preset 6",
            7: "Preset 7",
            8: "Preset 8",
        },
        favorite_presets=[1, 2],
        input_signals=[1, 1, 0, 0, 1, 1, 0, 0],
        output_displays=[1, 1, 1, 0, 0, 1, 0, 0],
        input_cables=[1, 1, 1, 0, 1, 1, 0, 0],
        output_cables=[1, 1, 1, 0, 0, 1, 0, 0],
        connection_state="CONNECTED" if connected else "BACKOFF",
        catalog={
            "profiles": [
                {"id": "movie", "name": "Movie Profile", "password_protected": False},
                {"id": "parental", "name": "Parental Profile", "password_protected": True},
            ],
            "scenes": [
                {"id": "night", "name": "Night Scene", "password_protected": False},
                {"id": "locked_scene", "name": "Locked Scene", "requires_pin": True},
            ],
            "macros": [{"id": "warmup", "name": "Warmup"}],
            "shortcuts": [{"id": "mute_all", "name": "Mute All"}],
        },
    )


class _TypedHubClientFake:
    """Structural `HubClientLocal` test double emitting typed `HubSnapshot` and `HubEvent`."""

    def __init__(self) -> None:
        self.state = _make_typed_snapshot()
        self.subscribers: list[Any] = []
        self.switch = AsyncMock(return_value=True)
        self.recall_preset = AsyncMock(return_value=True)
        self.power = AsyncMock(return_value=True)
        self.send_cec = AsyncMock(return_value=True)
        self.run_action = AsyncMock(side_effect=self._run_action)

    @property
    def connected(self) -> bool:
        return self.state.connected

    async def snapshot(self) -> HubSnapshot:
        return self.state

    def subscribe(self, callback: Any) -> Any:
        self.subscribers.append(callback)
        return lambda: self.subscribers.remove(callback) if callback in self.subscribers else None

    def emit(self, kind: str, data: dict[str, Any]) -> None:
        ev = HubEvent(kind=kind, data=data)
        for cb in list(self.subscribers):
            cb(ev)

    async def _run_action(self, kind: str, action_id: str | int, *, pin: str | None = None) -> dict[str, Any]:
        if str(action_id) in ("parental", "locked_scene", "runner_only_locked") and not pin:
            return {"success": False, "data": None, "error": "Passcode required", "status": 403}
        return {"success": True, "data": {"id": action_id}, "error": None, "status": 200}


async def test_typed_hub_snapshot_and_events_drive_uc_entities_and_runner_pin_checks(tmp_path: Path) -> None:
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
    hub = _TypedHubClientFake()
    integration = UnfoldedCircleIntegration(cfg)

    await integration.start(hub)
    try:
        async with UcRemoteSim(f"ws://127.0.0.1:{port}") as remote:
            available = {e["entity_id"]: e for e in await remote.get_available_entities()}
            assert len(available) == 74
            assert available["button.preset_1"]["name"] == {"en": "Apple TV Everywhere"}
            assert available["button.preset_3"]["name"] == {"en": "PS5"}

            pages = {
                p["page_id"]: [(i["text"], i["command"]["cmd_id"]) for i in p["items"]]
                for p in available["remote.orei_matrix"]["options"]["user_interface"]["pages"]
            }
            assert pages["orei_matrix_favourites"] == [
                ("Apple TV Everywhere", "PRESET_1"),
                ("Movie Night", "PRESET_2"),
            ]

            await remote.subscribe_events(
                [
                    "switch.matrix_power",
                    "media_player.output_1",
                    "sensor.input_1_signal",
                    "sensor.output_1_connected",
                    "remote.orei_matrix",
                ]
            )
            states = {s["entity_id"]: s["attributes"] for s in await remote.get_entity_states()}
            assert states["switch.matrix_power"]["state"] == "ON"
            assert states["media_player.output_1"]["source"] == "Apple TV"
            assert states["sensor.input_1_signal"]["value"] == "Active"
            assert states["sensor.output_1_connected"]["value"] == "Connected"

            # Unprotected profile succeeds; PIN-protected profile is rejected by projector AND by runner check
            assert (await remote.remote_send_cmd("remote.orei_matrix", "PROFILE_movie"))["code"] == 200
            assert (await remote.remote_send_cmd("remote.orei_matrix", "PROFILE_parental"))["code"] == 400
            # Even if an action was not in projector's blocked set, runner PIN rejection returns 400
            assert (await remote.remote_send_cmd("remote.orei_matrix", "PROFILE_runner_only_locked"))["code"] == 400

            # Live HubEvent("names") updates available entities and subscribed media_player in place
            since = remote.mark()
            hub.emit("names", {"inputs": {3: "Xbox Series X"}, "outputs": {1: "Cinema TV"}})
            await remote.wait_event(
                "entity_change",
                lambda d: d["entity_id"] == "media_player.output_1"
                and "Xbox Series X" in d["attributes"].get("source_list", []),
                since=since,
                timeout=3.0,
            )
            available_after = {e["entity_id"]: e for e in await remote.get_available_entities()}
            assert available_after["remote.input_3_cec"]["name"] == {"en": "Xbox Series X CEC"}
            assert available_after["media_player.output_1"]["name"] == {"en": "Cinema TV"}
            assert (await remote.select_source("media_player.output_1", "Xbox Series X"))["code"] == 200
            hub.switch.assert_awaited_with(3, 1)

            # Live HubEvent("presets") updates preset button names and favourites page in place
            hub.emit(
                "presets",
                {
                    "preset_names": {1: "Apple TV Everywhere", 2: "Movie Night", 3: "Game Night"},
                    "favorite_presets": [1, 2, 3],
                },
            )
            avail_presets = {e["entity_id"]: e for e in await remote.get_available_entities()}
            assert avail_presets["button.preset_3"]["name"] == {"en": "Game Night"}
            fav_items = avail_presets["remote.orei_matrix"]["options"]["user_interface"]["pages"][0]["items"]
            assert [(i["text"], i["command"]["cmd_id"]) for i in fav_items] == [
                ("Apple TV Everywhere", "PRESET_1"),
                ("Movie Night", "PRESET_2"),
                ("Game Night", "PRESET_3"),
            ]

            # Outage and recovery via HubEvent("connection")
            since_outage = remote.mark()
            hub.state.connected = False
            hub.state.connection_state = "BACKOFF"
            hub.emit("connection", {"connected": False, "state": "BACKOFF"})
            await remote.wait_event(
                "entity_change",
                lambda d: d["entity_id"] == "remote.orei_matrix" and d["attributes"].get("state") == "UNAVAILABLE",
                since=since_outage,
                timeout=3.0,
            )
            assert (await remote.get_device_state())["msg_data"]["state"] == "ERROR"
            assert (await remote.select_source("media_player.output_1", "Apple TV"))["code"] == 503

            since_rec = remote.mark()
            hub.state.connected = True
            hub.state.connection_state = "CONNECTED"
            hub.emit("connection", {"connected": True, "state": "CONNECTED"})
            await remote.wait_event(
                "device_state",
                lambda d: d.get("state") == "CONNECTED",
                since=since_rec,
                timeout=3.0,
            )
            assert (await remote.get_device_state())["msg_data"]["state"] == "CONNECTED"
    finally:
        await integration.stop()
