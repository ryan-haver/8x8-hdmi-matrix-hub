"""Comprehensive unit tests for `src/hub/integrations/unfolded_circle/` (Phase 4 / WP-C3 / R3)."""

from __future__ import annotations

import json
import socket
from collections import deque
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import ucapi

from hub import __version__
from src.hub.integrations.unfolded_circle import (
    APPROVED_GOLDEN_ENTITY_IDS,
    STANDARD_CEC_COMMANDS,
    SURVIVING_GOLDEN_ENTITY_IDS,
    UC_MDNS_SERVICE_TYPE,
    EntityStateProjector,
    UCCommandDispatcher,
    UCIntegrationConfig,
    UCMdnsPublisher,
    UnfoldedCircleIntegration,
    build_compatible_entities,
    build_entities,
    build_ucapi_entities,
    config_from_env,
    migrate_legacy_config_state,
)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


# =============================================================================
# 1. config.py tests
# =============================================================================


def test_config_defaults() -> None:
    cfg = config_from_env({})
    assert isinstance(cfg, UCIntegrationConfig)
    assert cfg.enabled is False
    assert cfg.port == 9095
    assert cfg.http_port == 9095
    assert cfg.interface is None
    assert cfg.disable_mdns_publish is False
    assert cfg.disable_mdns is False
    assert cfg.config_home == Path("./config")
    assert cfg.driver_url is None
    assert cfg.auth_token is None
    assert cfg.hub_url == "http://127.0.0.1:8080"
    assert cfg.hub_api_key is None


def test_config_parses_all_canonical_env_vars(tmp_path: Path) -> None:
    env = {
        "UC_ENABLED": "true",
        "UC_INTEGRATION_HTTP_PORT": "9100",
        "UC_INTEGRATION_INTERFACE": "192.168.1.50",
        "UC_DISABLE_MDNS_PUBLISH": "1",
        "UC_CONFIG_HOME": str(tmp_path / "uc_home"),
        "UC_DRIVER_URL": "ws://192.168.1.50:9100",
        "UC_AUTH_TOKEN": "secret-token-123",
        "HUB_URL": "http://192.168.1.50:8080",
        "HUB_API_KEY": "hub-key-xyz",
    }
    cfg = config_from_env(env)
    assert cfg.enabled is True
    assert cfg.port == 9100
    assert cfg.interface == "192.168.1.50"
    assert cfg.disable_mdns_publish is True
    assert cfg.config_home == tmp_path / "uc_home"
    assert cfg.driver_url == "ws://192.168.1.50:9100"
    assert cfg.auth_token == "secret-token-123"
    assert cfg.hub_url == "http://192.168.1.50:8080"
    assert cfg.hub_api_key == "hub-key-xyz"


def test_config_supports_deprecated_aliases(tmp_path: Path) -> None:
    env = {
        "UC_ENABLED": "yes",
        "UC_PORT": "9099",
        "UC_DISABLE_MDNS": "true",
        "DATA_DIR": str(tmp_path),
        "ADMIN_PIN": "pin-456",
    }
    cfg = config_from_env(env)
    assert cfg.enabled is True
    assert cfg.port == 9099
    assert cfg.disable_mdns_publish is True
    assert cfg.config_home == tmp_path
    assert cfg.auth_token == "pin-456"


def test_config_canonical_overrides_alias() -> None:
    env = {
        "UC_INTEGRATION_HTTP_PORT": "9095",
        "UC_PORT": "9999",
        "UC_DISABLE_MDNS_PUBLISH": "false",
        "UC_DISABLE_MDNS": "true",
    }
    cfg = config_from_env(env)
    assert cfg.port == 9095
    assert cfg.disable_mdns_publish is False


def test_config_rejects_invalid_port_and_driver_url() -> None:
    with pytest.raises(ValueError, match="port"):
        config_from_env({"UC_PORT": "not-a-port"})
    with pytest.raises(ValueError, match="port"):
        config_from_env({"UC_PORT": "70000"})
    with pytest.raises(ValueError, match="UC_DRIVER_URL"):
        config_from_env({"UC_DRIVER_URL": "http://192.168.1.10:9095"})


# =============================================================================
# 2. entities.py tests (BE-22, DI-9, UC-10, UC-12, UC-13)
# =============================================================================


def _sample_snapshot() -> dict[str, Any]:
    return {
        "connected": True,
        "power": 1,
        "input_names": {1: "Apple TV", 2: "PS5", 3: "Switch", 4: "PC"},
        "output_names": {1: "Living Room", 2: "Bedroom"},
        "routing": [1, 2, 3, 4, 1, 2, 3, 4],
        "presets": [
            {"number": 1, "name": "Movie Night", "favorite": True, "visible": True},
            {"number": 2, "name": "Game Mode", "favorite": False, "visible": True},
            {"number": 3, "name": "Hidden Preset", "favorite": False, "visible": False},
        ],
        "profiles": [
            {"id": "cinema", "name": "Cinema Profile", "has_pin": False},
            {"id": "kids_locked", "name": "Locked Profile", "has_pin": True, "allow_remote": False},
            {"id": "vip_allowed", "name": "VIP Profile", "has_pin": True, "allow_remote": True},
        ],
        "scenes": [
            {"id": "evening", "name": "Evening Scene"},
            {"id": "secret_scene", "name": "Secret Scene", "pin_protected": True},
        ],
        "shortcuts": [
            {"key": "all_mute", "name": "Mute All"},
        ],
        "macros": [
            {"id": "tv_warmup", "name": "TV Warmup"},
        ],
    }


def test_build_entities_preserves_all_surviving_golden_ids() -> None:
    entities = build_entities(_sample_snapshot())
    ids = {e["entity_id"] for e in entities}
    assert SURVIVING_GOLDEN_ENTITY_IDS.issubset(ids)


def test_build_entities_includes_select_and_binary_sensors() -> None:
    entities = build_entities(_sample_snapshot(), include_select=True)
    by_id = {e["entity_id"]: e for e in entities}

    for n in range(1, 9):
        sel = by_id[f"select.output_{n}_source"]
        assert sel["entity_type"] == "select"
        assert sel["attributes"]["options"][0] == "Apple TV"

        disp = by_id[f"sensor.output_{n}_display"]
        assert disp["entity_type"] == "sensor"
        assert disp["device_class"] == "binary"

        sig = by_id[f"sensor.input_{n}_signal"]
        assert sig["entity_type"] == "sensor"
        assert sig["device_class"] == "binary"


def test_build_entities_without_select_and_with_legacy_sensors() -> None:
    entities = build_entities(_sample_snapshot(), include_select=False, include_legacy_sensors=True)
    ids = {e["entity_id"] for e in entities}
    assert ids == APPROVED_GOLDEN_ENTITY_IDS
    assert len(entities) == 74
    assert not any(eid.startswith("select.") for eid in ids)
    assert "sensor.input_1_cable" in ids
    assert "sensor.output_1_connected" in ids
    assert "sensor.output_1_cable" in ids
    assert "sensor.output_1_source" in ids


def test_build_compatible_and_ucapi_entities_match_approved_golden_catalog() -> None:
    compat = build_compatible_entities(_sample_snapshot())
    assert len(compat) == 74
    assert {e["entity_id"] for e in compat} == APPROVED_GOLDEN_ENTITY_IDS

    uc_entities = build_ucapi_entities(_sample_snapshot(), compatible=True)
    assert len(uc_entities) == 74
    assert {e.id for e in uc_entities} == APPROVED_GOLDEN_ENTITY_IDS
    assert all(isinstance(e, ucapi.Entity) for e in uc_entities)


def test_cec_remotes_use_standard_uc_commands_button_mapping_and_icons() -> None:
    entities = build_entities(_sample_snapshot())
    by_id = {e["entity_id"]: e for e in entities}

    in_cec = by_id["remote.input_1_cec"]
    out_cec = by_id["remote.output_1_cec"]

    for std_cmd in STANDARD_CEC_COMMANDS:
        assert std_cmd in in_cec["simple_commands"]
        assert std_cmd in out_cec["simple_commands"]

    # Legacy aliases remain available
    assert "UP" in in_cec["simple_commands"]
    assert "SELECT" in in_cec["simple_commands"]
    assert "ACTIVE" in out_cec["simple_commands"]

    # Button mapping is populated and maps physical buttons
    in_buttons = {m["button"] for m in in_cec["button_mapping"]}
    assert {"DPAD_UP", "DPAD_DOWN", "DPAD_LEFT", "DPAD_RIGHT", "DPAD_MIDDLE", "VOLUME_UP", "MUTE"}.issubset(
        in_buttons
    )

    # Icons use uc: prefix
    assert in_cec["icon"].startswith("uc:")
    assert out_cec["icon"].startswith("uc:")
    for page in in_cec["ui_pages"]:
        for item in page["items"]:
            assert item["icon"].startswith("uc:")


def test_matrix_remote_populates_kiosk_commands_and_ui_pages() -> None:
    entities = build_entities(_sample_snapshot())
    matrix_remote = next(e for e in entities if e["entity_id"] == "remote.orei_matrix")
    cmds = set(matrix_remote["simple_commands"])

    for n in range(1, 9):
        assert f"PRESET_{n}" in cmds
        assert f"ROUTE_ALL_IN_{n}" in cmds

    assert "PROFILE_cinema" in cmds
    assert "PROFILE_vip_allowed" in cmds
    assert "SCENE_evening" in cmds
    assert "SHORTCUT_all_mute" in cmds
    assert "MACRO_tv_warmup" in cmds

    page_ids = [p["page_id"] for p in matrix_remote["ui_pages"]]
    assert "orei_matrix_favourites" in page_ids
    assert "orei_matrix_main" in page_ids
    assert "orei_matrix_routing" in page_ids
    assert "orei_matrix_profiles" in page_ids
    assert "orei_matrix_scenes" in page_ids
    assert "orei_matrix_shortcuts" in page_ids
    assert "orei_matrix_macros" in page_ids


def test_matrix_remote_hides_pin_protected_profiles_and_scenes_unless_allowed() -> None:
    entities = build_entities(_sample_snapshot())
    matrix_remote = next(e for e in entities if e["entity_id"] == "remote.orei_matrix")
    cmds = set(matrix_remote["simple_commands"])

    assert "PROFILE_kids_locked" not in cmds
    assert "SCENE_secret_scene" not in cmds
    assert "PROFILE_vip_allowed" in cmds


def test_media_players_and_cec_remotes_start_in_unknown_state() -> None:
    entities = build_entities(_sample_snapshot())
    by_id = {e["entity_id"]: e for e in entities}

    for n in range(1, 9):
        assert by_id[f"media_player.output_{n}"]["attributes"]["state"] == "UNKNOWN"
        assert by_id[f"remote.input_{n}_cec"]["attributes"]["state"] == "UNKNOWN"
        assert by_id[f"remote.output_{n}_cec"]["attributes"]["state"] == "UNKNOWN"


# =============================================================================
# 3. state.py tests (UC-04, UC-07, UC-08, BE-24)
# =============================================================================


def test_projector_initial_states_and_toggle_from_unknown_resolves_to_on() -> None:
    proj = EntityStateProjector()
    assert proj.get_power_state("media_player.output_1") == "UNKNOWN"
    assert proj.get_power_state("remote.input_1_cec") == "UNKNOWN"
    assert proj.get_power_state("remote.output_1_cec") == "UNKNOWN"

    # Toggle from UNKNOWN resolves to ON (BE-24, UC-10)
    assert proj.resolve_toggle("media_player.output_1") == "ON"
    assert proj.resolve_toggle("remote.input_1_cec") == "ON"

    diff = proj.record_power("output", 1, on=True)
    assert diff["media_player.output_1"]["state"] == "ON"
    assert diff["remote.output_1_cec"]["state"] == "ON"
    assert proj.resolve_toggle("media_player.output_1") == "OFF"

    diff2 = proj.record_power("output", 1, on=False)
    assert diff2["media_player.output_1"]["state"] == "OFF"
    assert proj.resolve_toggle("media_player.output_1") == "ON"


def test_projector_disconnected_marks_all_entities_unavailable_without_input_0() -> None:
    proj = EntityStateProjector()
    proj.project_snapshot(_sample_snapshot(), force=True)

    diff = proj.project_snapshot({"connected": False, "connection_state": "BACKOFF", "routing": [0] * 8})
    assert proj.connected is False
    assert proj.device_state == "ERROR"
    assert diff["remote.orei_matrix"]["state"] == "UNAVAILABLE"
    assert diff["media_player.output_1"]["state"] == "UNAVAILABLE"
    assert diff["switch.matrix_power"]["state"] == "UNAVAILABLE"

    # Never fabricated "Input 0"
    assert proj.projected_attributes("media_player.output_1")["source"] == "Apple TV"
    for attrs in proj.truth.values():
        assert attrs.get("source") != "Input 0"
        assert attrs.get("current_option") != "Input 0"


def test_projector_explicit_disconnect_sets_disconnected_device_state() -> None:
    proj = EntityStateProjector()
    proj.apply_event("hub_connection", {"connected": False, "state": "DISCONNECTED"})
    assert proj.connected is False
    assert proj.device_state == "DISCONNECTED"
    assert proj.projected_attributes("button.preset_1")["state"] == "UNAVAILABLE"


def test_projector_ignores_input_zero_in_routing() -> None:
    proj = EntityStateProjector()
    proj.project_snapshot(_sample_snapshot(), force=True)
    assert proj.projected_attributes("media_player.output_1")["source"] == "Apple TV"

    diff = proj.apply_event("routing", {"output": 1, "input": 0})
    assert diff == {}
    assert proj.projected_attributes("media_player.output_1")["source"] == "Apple TV"


def test_projector_returns_only_changed_attributes() -> None:
    proj = EntityStateProjector()
    first = proj.project_snapshot(_sample_snapshot(), force=True)
    assert len(first) > 0

    # Identical snapshot produces empty diff (UC-07)
    second = proj.project_snapshot(_sample_snapshot())
    assert second == {}

    # Changing a single output route only emits that output's media_player & select
    third = proj.apply_event("routing", {"output": 1, "input": 2})
    assert set(third.keys()) == {"media_player.output_1", "select.output_1_source"}
    assert third["media_player.output_1"] == {"source": "PS5"}
    assert third["select.output_1_source"] == {"current_option": "PS5"}


def test_projector_resync_returns_full_attributes() -> None:
    proj = EntityStateProjector()
    proj.project_snapshot(_sample_snapshot(), force=True)
    assert proj.project_snapshot(_sample_snapshot()) == {}

    resynced = proj.resync(["media_player.output_1"])
    assert "media_player.output_1" in resynced
    assert "source_list" in resynced["media_player.output_1"]
    assert resynced["media_player.output_1"]["source"] == "Apple TV"


def test_projector_live_renames_update_in_place_without_clearing_configured_entities() -> None:
    proj = EntityStateProjector()
    proj.project_snapshot(_sample_snapshot(), force=True)
    # Entities are not marked configured merely because they are available
    assert proj.configured_entities == {}

    proj.subscribe_entities(["remote.input_1_cec", "media_player.output_1", "select.output_1_source"])
    configured_before = set(proj.configured_entities.keys())

    diff = proj.apply_event("names", {"inputs": {1: "Xbox Series X"}, "outputs": {1: "Theater OLED"}})

    # configured_entities was updated in place, never cleared (UC-08)
    assert set(proj.configured_entities.keys()) == configured_before
    assert proj.configured_entities["remote.input_1_cec"]["name"] == {"en": "Xbox Series X CEC"}
    assert proj.configured_entities["media_player.output_1"]["name"] == {"en": "Theater OLED"}

    # Subscribed media_player and select got updated source_list/options and routed source
    assert diff["media_player.output_1"]["source"] == "Xbox Series X"
    assert diff["media_player.output_1"]["source_list"][0] == "Xbox Series X"
    assert diff["select.output_1_source"]["current_option"] == "Xbox Series X"
    assert diff["select.output_1_source"]["options"][0] == "Xbox Series X"


def test_projector_ignores_transient_generic_name_fallback() -> None:
    proj = EntityStateProjector()
    proj.project_snapshot(_sample_snapshot(), force=True)
    assert proj.input_names[1] == "Apple TV"

    generic = {n: f"Input {n}" for n in range(1, 9)}
    diff = proj.apply_event("names", {"inputs": generic})
    assert diff == {}
    assert proj.input_names[1] == "Apple TV"


def test_projector_standby_buffers_updates_and_flushes_on_wake() -> None:
    proj = EntityStateProjector()
    proj.project_snapshot(_sample_snapshot(), force=True)

    proj.enter_standby()
    assert proj.standby is True

    # While in standby, events produce no immediate push
    assert proj.apply_event("routing", {"output": 2, "input": 4}) == {}
    assert proj.apply_event("power", {"power": 0}) == {}

    # Exiting standby flushes accumulated changes
    flushed = proj.exit_standby()
    assert proj.standby is False
    assert flushed["media_player.output_2"]["source"] == "PC"
    assert flushed["select.output_2_source"]["current_option"] == "PC"
    assert flushed["switch.matrix_power"]["state"] == "OFF"


def test_projector_signal_display_and_power_events() -> None:
    proj = EntityStateProjector()
    proj.project_snapshot(_sample_snapshot(), force=True)

    sig_diff = proj.apply_event("signal", {"port": 3, "present": True})
    assert sig_diff == {"sensor.input_3_signal": {"state": "ON", "value": True}}

    disp_diff = proj.apply_event("display", {"port": 2, "connected": False})
    assert disp_diff == {"sensor.output_2_display": {"state": "ON", "value": False}}

    pwr_diff = proj.apply_event("power", {"power": "off"})
    assert pwr_diff == {"switch.matrix_power": {"state": "OFF"}}


# =============================================================================
# 4. handlers.py tests (UC-01, UC-08, UC-10, UC-12, DI-9)
# =============================================================================


def _make_mock_hub() -> MagicMock:
    hub = MagicMock()
    hub.connected = True
    hub.snapshot = AsyncMock(return_value=_sample_snapshot())
    hub.switch = AsyncMock(return_value=True)
    hub.cycle_input = AsyncMock(return_value=True)
    hub.recall_preset = AsyncMock(return_value=True)
    hub.power = AsyncMock(return_value=True)
    hub.send_cec = AsyncMock(return_value=True)
    hub.run_action = AsyncMock(return_value=True)
    return hub


async def test_dispatcher_select_source_and_select_option() -> None:
    hub = _make_mock_hub()
    proj = EntityStateProjector()
    proj.project_snapshot(_sample_snapshot(), force=True)
    disp = UCCommandDispatcher(hub, proj)

    code = await disp.dispatch("media_player.output_1", "select_source", {"source": "PS5"})
    assert code == 200
    hub.switch.assert_awaited_once_with(2, 1)

    hub.switch.reset_mock()
    code2 = await disp.dispatch("select.output_2_source", "select_option", {"option": "Switch"})
    assert code2 == 200
    hub.switch.assert_awaited_once_with(3, 2)

    # Unknown source returns 400 without calling hub
    hub.switch.reset_mock()
    assert await disp.dispatch("media_player.output_1", "select_source", {"source": "Nonexistent"}) == 400
    hub.switch.assert_not_awaited()


async def test_dispatcher_select_source_after_live_rename() -> None:
    hub = _make_mock_hub()
    proj = EntityStateProjector()
    proj.project_snapshot(_sample_snapshot(), force=True)
    disp = UCCommandDispatcher(hub, proj)

    proj.apply_event("names", {"inputs": {3: "Steam Deck"}})
    code = await disp.dispatch("media_player.output_4", "select_source", {"source": "Steam Deck"})
    assert code == 200
    hub.switch.assert_awaited_once_with(3, 4)


async def test_dispatcher_select_first_last_next_previous() -> None:
    hub = _make_mock_hub()
    proj = EntityStateProjector()
    proj.project_snapshot(_sample_snapshot(), force=True)
    disp = UCCommandDispatcher(hub, proj)

    assert await disp.dispatch("select.output_1_source", "select_first") == 200
    hub.switch.assert_awaited_with(1, 1)

    assert await disp.dispatch("select.output_1_source", "select_last") == 200
    hub.switch.assert_awaited_with(8, 1)

    assert await disp.dispatch("select.output_1_source", "select_next", {"cycle": True}) == 200
    hub.cycle_input.assert_awaited_once_with("next", 1, cycle=True)
    assert hub.switch.await_count == 2

    assert await disp.dispatch("select.output_1_source", "select_previous", {"cycle": True}) == 200
    hub.cycle_input.assert_awaited_with("previous", 1, cycle=True)
    assert hub.switch.await_count == 2


async def test_dispatcher_preset_button_push() -> None:
    hub = _make_mock_hub()
    disp = UCCommandDispatcher(hub)

    assert await disp.dispatch("button.preset_5", "push") == 200
    hub.recall_preset.assert_awaited_once_with(5)
    assert await disp.dispatch("button.preset_5", "on") == 501


async def test_dispatcher_matrix_power_switch_on_off_toggle() -> None:
    hub = _make_mock_hub()
    proj = EntityStateProjector()
    disp = UCCommandDispatcher(hub, proj)

    # Toggle from UNKNOWN resolves to ON
    assert await disp.dispatch("switch.matrix_power", "toggle") == 200
    hub.power.assert_awaited_with(True)
    assert proj.get_power_state("switch.matrix_power") == "ON"

    # Second toggle resolves to OFF
    assert await disp.dispatch("switch.matrix_power", "toggle") == 200
    hub.power.assert_awaited_with(False)
    assert proj.get_power_state("switch.matrix_power") == "OFF"

    assert await disp.dispatch("switch.matrix_power", "on") == 200
    hub.power.assert_awaited_with(True)


async def test_dispatcher_cec_remote_on_off_toggle_and_send_cmd() -> None:
    hub = _make_mock_hub()
    proj = EntityStateProjector()
    disp = UCCommandDispatcher(hub, proj)

    # Toggle from UNKNOWN on input 2 CEC sends POWER_ON
    assert await disp.dispatch("remote.input_2_cec", "toggle") == 200
    hub.send_cec.assert_awaited_with("input", 2, "POWER_ON")
    assert proj.get_power_state("input", 2) == "ON"

    # Standard UC command CURSOR_ENTER maps to SELECT
    assert await disp.dispatch("remote.input_2_cec", "send_cmd", {"command": "CURSOR_ENTER"}) == 200
    hub.send_cec.assert_awaited_with("input", 2, "SELECT")

    # Output CEC remote MUTE_TOGGLE maps to MUTE
    assert await disp.dispatch("remote.output_3_cec", "send_cmd", {"command": "MUTE_TOGGLE"}) == 200
    hub.send_cec.assert_awaited_with("output", 3, "MUTE")


async def test_dispatcher_media_player_power_and_volume_use_output_cec() -> None:
    hub = _make_mock_hub()
    proj = EntityStateProjector()
    disp = UCCommandDispatcher(hub, proj)

    assert await disp.dispatch("media_player.output_2", "toggle") == 200
    hub.send_cec.assert_awaited_with("output", 2, "POWER_ON")
    assert proj.get_power_state("output", 2) == "ON"

    assert await disp.dispatch("media_player.output_2", "volume_up") == 200
    hub.send_cec.assert_awaited_with("output", 2, "VOLUME_UP")

    assert await disp.dispatch("media_player.output_2", "mute_toggle") == 200
    hub.send_cec.assert_awaited_with("output", 2, "MUTE")


async def test_dispatcher_cec_send_cmd_sequence_and_repeat() -> None:
    hub = _make_mock_hub()
    disp = UCCommandDispatcher(hub)

    code = await disp.dispatch(
        "remote.input_1_cec",
        "send_cmd_sequence",
        {"sequence": "CURSOR_UP,CURSOR_ENTER", "repeat": 2, "delay": 0},
    )
    assert code == 200
    calls = [c.args for c in hub.send_cec.await_args_list]
    assert calls == [
        ("input", 1, "UP"),
        ("input", 1, "UP"),
        ("input", 1, "SELECT"),
        ("input", 1, "SELECT"),
    ]


async def test_dispatcher_cec_rejects_unknown_command_without_partial_send() -> None:
    hub = _make_mock_hub()
    disp = UCCommandDispatcher(hub)

    code = await disp.dispatch(
        "remote.input_1_cec",
        "send_cmd_sequence",
        {"sequence": ["POWER_ON", "INVALID_BOGUS_CMD"]},
    )
    assert code == 400
    hub.send_cec.assert_not_awaited()


async def test_dispatcher_matrix_remote_commands() -> None:
    hub = _make_mock_hub()
    proj = EntityStateProjector()
    disp = UCCommandDispatcher(hub, proj)
    disp.update_pin_blocks(_sample_snapshot())

    assert await disp.dispatch("remote.orei_matrix", "send_cmd", {"command": "PRESET_3"}) == 200
    hub.recall_preset.assert_awaited_once_with(3)

    assert await disp.dispatch("remote.orei_matrix", "send_cmd", {"command": "ROUTE_ALL_IN_6"}) == 200
    hub.switch.assert_awaited_once_with(6, None)

    assert await disp.dispatch("remote.orei_matrix", "send_cmd", {"command": "PROFILE_cinema"}) == 200
    hub.run_action.assert_awaited_with("profile", "cinema")

    assert await disp.dispatch("remote.orei_matrix", "send_cmd", {"command": "SCENE_evening"}) == 200
    hub.run_action.assert_awaited_with("scene", "evening")

    assert await disp.dispatch("remote.orei_matrix", "send_cmd", {"command": "SHORTCUT_all_mute"}) == 200
    hub.run_action.assert_awaited_with("shortcut", "all_mute")

    assert await disp.dispatch("remote.orei_matrix", "send_cmd", {"command": "MACRO_tv_warmup"}) == 200
    hub.run_action.assert_awaited_with("macro", "tv_warmup")

    # PIN-protected profile is rejected with 400 unless allowed
    assert await disp.dispatch("remote.orei_matrix", "send_cmd", {"command": "PROFILE_kids_locked"}) == 400
    assert await disp.dispatch("remote.orei_matrix", "send_cmd", {"command": "PROFILE_vip_allowed"}) == 200


async def test_dispatcher_returns_503_when_disconnected_and_500_on_exception() -> None:
    hub = _make_mock_hub()
    proj = EntityStateProjector()
    disp = UCCommandDispatcher(hub, proj)

    proj.connected = False
    assert await disp.dispatch("button.preset_1", "push") == 503

    proj.connected = True
    hub.recall_preset.side_effect = RuntimeError("boom")
    assert await disp.dispatch("button.preset_1", "push") == 500


async def test_dispatcher_returns_501_for_unimplemented_commands() -> None:
    hub = _make_mock_hub()
    disp = UCCommandDispatcher(hub)

    assert await disp.dispatch("remote.orei_matrix", "on") == 501
    assert await disp.dispatch("remote.orei_matrix", "off") == 501
    assert await disp.dispatch("remote.input_1_cec", "cursor_up") == 501


# =============================================================================
# 5. migration.py tests
# =============================================================================


def test_migrate_legacy_config_state_preserves_primary_file_and_credentials(tmp_path: Path) -> None:
    legacy_file = tmp_path / "config_state.json"
    legacy_file.write_text(
        json.dumps(
            {
                "host": "192.168.1.200",
                "port": 443,
                "telnet_port": 2323,
                "user": "Admin",
                "password": "matrix-secret",
                "input_names": {"1": "Apple TV", "2": "Shield"},
                "output_names": {"1": "Living Room"},
            }
        ),
        encoding="utf-8",
    )

    migrated = migrate_legacy_config_state(tmp_path)
    assert migrated is not None
    assert migrated["host"] == "192.168.1.200"
    assert migrated["port"] == 443
    assert migrated["telnet_port"] == 2323
    assert migrated["user"] == "Admin"
    assert migrated["password"] == "matrix-secret"
    assert migrated["input_names"] == {1: "Apple TV", 2: "Shield"}
    assert migrated["output_names"] == {1: "Living Room"}
    # Non-destructive: primary config_state.json remains intact on disk
    assert legacy_file.exists()


def test_migrate_legacy_config_state_is_idempotent_and_recovers_migrated_fallback(tmp_path: Path) -> None:
    migrated_only = tmp_path / "config_state.json.migrated"
    migrated_only.write_text(
        json.dumps({"host": "10.0.0.50", "port": 8443, "telnet_port": 23}),
        encoding="utf-8",
    )

    first = migrate_legacy_config_state(tmp_path)
    second = migrate_legacy_config_state(tmp_path)
    assert first == second == {"host": "10.0.0.50", "port": 8443, "telnet_port": 23}
    # Restored primary config_state.json without deleting fallback
    assert (tmp_path / "config_state.json").exists()
    assert migrated_only.exists()


def test_migrate_legacy_config_state_returns_none_when_absent_or_invalid(tmp_path: Path) -> None:
    assert migrate_legacy_config_state(tmp_path) is None

    bad_file = tmp_path / "config_state.json"
    bad_file.write_text("{not valid json", encoding="utf-8")
    assert migrate_legacy_config_state(tmp_path) is None


# =============================================================================
# 6. mdns.py tests (UC-11, UC-02)
# =============================================================================


def test_mdns_service_info_without_auth_token_omits_pwd() -> None:
    pub = UCMdnsPublisher(port=9095, interface="192.168.1.25", auth_token=None)
    info = pub.build_service_info()
    assert info["type"] == UC_MDNS_SERVICE_TYPE
    assert info["name"] == f"hdmi_matrix.{UC_MDNS_SERVICE_TYPE}"
    assert info["port"] == 9095
    assert info["address"] == "192.168.1.25"
    assert info["properties"]["ver"] == __version__
    assert info["properties"]["developer"] == "Ryan Haver"
    assert "pwd" not in info["properties"]


def test_mdns_service_info_with_auth_token_includes_pwd() -> None:
    pub = UCMdnsPublisher(port=9095, interface="192.168.1.25", auth_token="my-token")
    info = pub.build_service_info()
    assert info["properties"]["pwd"] == "true"


async def test_mdns_start_and_stop_unregisters_cleanly() -> None:
    fake_zc = MagicMock()
    fake_zc.async_register_service = AsyncMock()
    fake_zc.async_unregister_service = AsyncMock()

    pub = UCMdnsPublisher(port=9095, interface="192.168.1.25", zeroconf=fake_zc)
    assert await pub.start() is True
    assert pub.published is True
    fake_zc.async_register_service.assert_awaited_once()

    await pub.stop()
    assert pub.published is False
    fake_zc.async_unregister_service.assert_awaited_once()


async def test_mdns_disabled_does_not_publish() -> None:
    fake_zc = MagicMock()
    fake_zc.async_register_service = AsyncMock()
    pub = UCMdnsPublisher(disable_mdns=True, zeroconf=fake_zc)
    assert await pub.start() is False
    assert pub.published is False
    fake_zc.async_register_service.assert_not_awaited()


# =============================================================================
# 7. UnfoldedCircleIntegration lifecycle tests (UC-06, UC-17)
# =============================================================================


async def test_integration_start_subscribes_migrates_and_reports_health(tmp_path: Path) -> None:
    (tmp_path / "config_state.json").write_text(
        json.dumps({"host": "192.168.1.100", "port": 443, "telnet_port": 23}),
        encoding="utf-8",
    )
    port = _free_port()
    cfg = config_from_env(
        {
            "UC_ENABLED": "true",
            "UC_PORT": str(port),
            "UC_DISABLE_MDNS": "true",
            "UC_CONFIG_HOME": str(tmp_path),
        }
    )
    hub = _make_mock_hub()
    unsub = MagicMock()
    hub.subscribe = MagicMock(return_value=unsub)

    integration = UnfoldedCircleIntegration(cfg)
    assert integration.name == "unfolded_circle"
    assert integration.env_flag == "UC_ENABLED"
    assert integration.health()["status"] == "stopped"

    await integration.start(hub)
    assert integration.running is True
    assert isinstance(integration.api, ucapi.IntegrationAPI)
    assert integration.migrated_config == {"host": "192.168.1.100", "port": 443, "telnet_port": 23}
    assert (tmp_path / "config_state.json").exists()
    assert integration.health()["status"] == "ok"
    assert integration.health()["device_state"] == "CONNECTED"
    assert integration.health()["entity_count"] == len(integration.entities) == 74
    assert integration.health()["configured_entity_count"] == 0
    assert len(integration.api.available_entities.get_all()) == 74
    assert await integration.api.configured_entities.get_states() == []
    assert isinstance(integration.pushed_updates, deque)
    hub.subscribe.assert_called_once()

    await integration.stop()
    assert integration.running is False
    assert integration.health()["status"] == "stopped"
    unsub.assert_called_once()


async def test_integration_standby_pauses_pushes_without_disconnecting_matrix_and_wake_resyncs(
    tmp_path: Path,
) -> None:
    port = _free_port()
    cfg = config_from_env(
        {
            "UC_ENABLED": "true",
            "UC_PORT": str(port),
            "UC_DISABLE_MDNS": "true",
            "UC_CONFIG_HOME": str(tmp_path),
        }
    )
    hub = _make_mock_hub()
    hub.disconnect = AsyncMock()
    captured_cb: list[Any] = []
    hub.subscribe = MagicMock(side_effect=lambda cb: captured_cb.append(cb))

    integration = UnfoldedCircleIntegration(cfg)
    await integration.start(hub)
    updates_before = len(integration.pushed_updates)

    await integration.on_enter_standby()
    assert integration.standby is True
    hub.disconnect.assert_not_awaited()

    # Hub event during standby does not push immediately
    event_cb = captured_cb[0]
    diff = event_cb("routing", {"output": 1, "input": 3})
    assert diff == {}
    assert len(integration.pushed_updates) == updates_before

    # Waking up flushes changes and resyncs
    flushed = await integration.on_exit_standby()
    assert integration.standby is False
    assert "media_player.output_1" in flushed
    assert len(integration.pushed_updates) == updates_before + 1
    await integration.stop()
