"""Entity commands from the Remote (audit §7 case 5): the effect is read back from the simulator.

Every test checks what reached the device (simulator state and command log) and
what the Remote was told, not only the response code.
"""

from __future__ import annotations

import pytest

from tools.uc_remote_sim import ConnectionClosedError, UcRemoteSim
from tools.validate.device import SimDevice

from ._helpers import CYCLE, INPUT_NAMES, SEED_STATE, cec_frames, known_bug, port_mask, sent, wait_for, writes

#: CEC command name -> index in the matrix's `cec command` frame. Written out here on purpose
#: (a change must show up as a deliberate test change). Both tables are the BK-808's own, from its
#: web interface's control pads (docs/OREI_API_COMMANDS.md "cec command"; VAL-03, BE-14):
#: sources (object 0) use the 1-based 19-key table ...
PINNED_INPUT_CEC_INDEX = {
    "POWER_ON": 1, "POWER_OFF": 2, "UP": 3, "LEFT": 4, "SELECT": 5, "RIGHT": 6, "MENU": 7, "DOWN": 8,
    "BACK": 9, "PREVIOUS": 10, "PLAY": 11, "NEXT": 12, "REWIND": 13, "PAUSE": 14, "FAST_FORWARD": 15,
    "STOP": 16, "MUTE": 17, "VOLUME_DOWN": 18, "VOLUME_UP": 19,
}
#: ... displays (object 1) a different, 0-based table of six keys. Source index 1 (power on) is
#: display index 1 = power OFF: sending the source table to a TV turns it off (BE-14).
PINNED_OUTPUT_CEC_INDEX = {"POWER_ON": 0, "POWER_OFF": 1, "MUTE": 2, "VOLUME_DOWN": 3, "VOLUME_UP": 4, "ACTIVE": 5}
#: The simple commands each CEC remote advertises (tests/uc/golden/entities.json). A display
#: remote offers exactly the display table: no navigation or playback keys.
OUTPUT_CEC_COMMANDS = list(PINNED_OUTPUT_CEC_INDEX)
INPUT_CEC_COMMANDS = ["POWER_ON", "POWER_OFF", "UP", "DOWN", "LEFT", "RIGHT", "SELECT", "MENU", "BACK", "PLAY",
                      "PAUSE", "STOP", "PREVIOUS", "NEXT", "REWIND", "FAST_FORWARD", "VOLUME_UP", "VOLUME_DOWN",
                      "MUTE"]


# ---------------------------------------------------------------------- routing (media player)


async def test_select_source_routes_the_output(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    await sim.clear_log()
    since = uc_remote.mark()
    resp = await uc_remote.select_source("media_player.output_1", "PS5")
    assert resp["code"] == 200
    state = await sim.state()
    assert state["outputs"][0]["source"] == 6
    assert state["routing"][1:] == [o["source"] for o in SEED_STATE["outputs"]][1:], "other outputs unchanged"
    log = await sim.log()
    assert writes(log) == [("video switch", {"comhead": "video switch", "language": 0, "source": [1, 6]})]
    # The Remote is told about the new source.
    change = await uc_remote.wait_event(
        "entity_change", lambda d: d["entity_id"] == "media_player.output_1" and d["attributes"].get("source") == "PS5",
        since=since, timeout=CYCLE)
    assert change.data["cat"] == "ENTITY"


async def test_select_source_on_another_output(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    resp = await uc_remote.select_source("media_player.output_7", INPUT_NAMES[2])
    assert resp["code"] == 200
    assert (await sim.state())["outputs"][6]["source"] == 3


async def test_select_unknown_source_is_rejected_without_a_write(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    await sim.clear_log()
    resp = await uc_remote.select_source("media_player.output_1", "No Such Input")
    assert resp["code"] == 400
    assert writes(await sim.log()) == []
    assert (await sim.state())["outputs"][0]["source"] == SEED_STATE["outputs"][0]["source"]
    assert not uc_remote.closed


# ---------------------------------------------------------------------- presets


async def test_preset_button_recalls_the_preset(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    await sim.clear_log()
    resp = await uc_remote.button_push("button.preset_3")
    assert resp["code"] == 200
    assert (await sim.state())["routing"] == SEED_STATE["presets"][2]["routing"]
    assert sent(await sim.log(), "preset set") == [{"comhead": "preset set", "language": 0, "index": 3}]


async def test_matrix_remote_preset_command_recalls_the_preset(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    resp = await uc_remote.remote_send_cmd("remote.orei_matrix", "PRESET_2")
    assert resp["code"] == 200
    assert (await sim.state())["routing"] == SEED_STATE["presets"][1]["routing"]


async def test_matrix_remote_rejects_bad_commands_and_stays_connected(uc_remote: UcRemoteSim,
                                                                      sim: SimDevice) -> None:
    """remote.orei_matrix has only SEND_CMD: on/off answer 501 (audit §3), an invalid preset 400."""
    await sim.clear_log()
    assert (await uc_remote.remote_send_cmd("remote.orei_matrix", "PRESET_X"))["code"] == 400
    assert (await uc_remote.entity_command("remote.orei_matrix", "on"))["code"] == 501
    assert (await uc_remote.entity_command("remote.orei_matrix", "off"))["code"] == 501
    assert writes(await sim.log()) == []
    assert not uc_remote.closed


# ---------------------------------------------------------------------- CEC remotes: send_cmd


async def test_output_cec_remote_send_cmd_sends_exact_frames(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    """Every simple command of remote.output_1_cec reaches the matrix as one CEC frame for output 1."""
    await sim.clear_log()
    for command in OUTPUT_CEC_COMMANDS:
        resp = await uc_remote.remote_send_cmd("remote.output_1_cec", command)
        assert resp["code"] == 200, command
    assert cec_frames(await sim.log()) == [
        {"object": 1, "port": port_mask(1), "index": PINNED_OUTPUT_CEC_INDEX[c]} for c in OUTPUT_CEC_COMMANDS
    ]


async def test_output_cec_remote_advertises_only_the_display_table(uc_remote: UcRemoteSim) -> None:
    """The display remote offers the six keys a display has on the BK-808, nothing the hub would refuse."""
    entities = {e["entity_id"]: e for e in await uc_remote.get_available_entities()}
    for n in range(1, 9):
        assert entities[f"remote.output_{n}_cec"]["options"]["simple_commands"] == OUTPUT_CEC_COMMANDS


async def test_source_only_keys_on_the_output_cec_remote_are_rejected(uc_remote: UcRemoteSim,
                                                                      sim: SimDevice) -> None:
    """Navigation/playback keys have no display index (BE-14): 400 and no frame, never a source-table index."""
    await sim.clear_log()
    for command in ("UP", "SELECT", "MENU", "BACK", "PLAY"):
        assert (await uc_remote.remote_send_cmd("remote.output_1_cec", command))["code"] == 400, command
    assert cec_frames(await sim.log()) == []
    assert not uc_remote.closed


async def test_input_cec_remote_send_cmd_sends_exact_frames(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    """Every simple command of remote.input_2_cec reaches the matrix as one CEC frame for input 2."""
    await sim.clear_log()
    for command in INPUT_CEC_COMMANDS:
        resp = await uc_remote.remote_send_cmd("remote.input_2_cec", command)
        assert resp["code"] == 200, command
    assert cec_frames(await sim.log()) == [
        {"object": 0, "port": port_mask(2), "index": PINNED_INPUT_CEC_INDEX[c]} for c in INPUT_CEC_COMMANDS
    ]


async def test_cec_send_cmd_targets_the_entity_port(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    await sim.clear_log()
    assert (await uc_remote.remote_send_cmd("remote.output_8_cec", "POWER_OFF"))["code"] == 200
    assert (await uc_remote.remote_send_cmd("remote.input_8_cec", "POWER_ON"))["code"] == 200
    assert cec_frames(await sim.log()) == [
        {"object": 1, "port": port_mask(8), "index": PINNED_OUTPUT_CEC_INDEX["POWER_OFF"]},  # 1
        {"object": 0, "port": port_mask(8), "index": PINNED_INPUT_CEC_INDEX["POWER_ON"]},  # 1
    ]


async def test_unknown_cec_command_is_rejected_without_a_frame(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    await sim.clear_log()
    resp = await uc_remote.remote_send_cmd("remote.output_1_cec", "SELF_DESTRUCT")
    assert resp["code"] == 400
    assert cec_frames(await sim.log()) == []
    assert not uc_remote.closed


@known_bug("UC-22", "send_cmd ignores `repeat` (and `delay`/`hold`): a held volume key sends one step")
async def test_send_cmd_repeat_sends_the_command_repeatedly(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    await sim.clear_log()
    resp = await uc_remote.remote_send_cmd("remote.output_1_cec", "VOLUME_UP", repeat=3, delay=50)
    assert resp["code"] == 200
    assert cec_frames(await sim.log()) == [
        {"object": 1, "port": port_mask(1), "index": PINNED_OUTPUT_CEC_INDEX["VOLUME_UP"]}] * 3


# ---------------------------------------------------------------------- CEC remotes: UC-01

#: remote entity command -> the CEC frame(s) a correct driver sends (entity_remote.md; power maps to CEC power).
#: Displays use the display table (0 power on, 1 power off, 4 volume up), sources the source table.
UC01_CASES = [
    ("remote.output_1_cec", "on", None, [{"object": 1, "port": port_mask(1), "index": 0}]),
    ("remote.output_1_cec", "off", None, [{"object": 1, "port": port_mask(1), "index": 1}]),
    ("remote.output_1_cec", "toggle", None, None),
    ("remote.output_1_cec", "send_cmd_sequence", {"sequence": ["POWER_ON", "VOLUME_UP"], "delay": 50},
     [{"object": 1, "port": port_mask(1), "index": 0}, {"object": 1, "port": port_mask(1), "index": 4}]),
    ("remote.input_3_cec", "on", None, [{"object": 0, "port": port_mask(3), "index": 1}]),
    ("remote.input_3_cec", "off", None, [{"object": 0, "port": port_mask(3), "index": 2}]),
    ("remote.input_3_cec", "toggle", None, None),
    ("remote.input_3_cec", "send_cmd_sequence", {"sequence": ["UP", "SELECT"]},
     [{"object": 0, "port": port_mask(3), "index": 3}, {"object": 0, "port": port_mask(3), "index": 5}]),
    ("remote.input_3_cec", "send_cmd", None, None),  # send_cmd without the `command` parameter
]


@known_bug("UC-01", "every remote command except send_cmd raises AttributeError in the CEC handler; ucapi does "
           "not catch it and closes the Remote's WebSocket with 1011", raises=ConnectionClosedError)
@pytest.mark.parametrize(("entity_id", "cmd_id", "params", "frames"), UC01_CASES,
                         ids=[f"{e.split('.')[1]}-{c}" + ("-noparams" if c == "send_cmd" else "")
                              for e, c, _, _ in UC01_CASES])
async def test_cec_remote_power_and_sequence_commands(uc_remote: UcRemoteSim, sim: SimDevice, entity_id: str,
                                                      cmd_id: str, params: dict | None,
                                                      frames: list | None) -> None:
    """on/off/toggle/send_cmd_sequence answer (200, or 400 for a malformed send_cmd), the frames reach the
    matrix, and the connection stays open (audit §7 case 5)."""
    await sim.clear_log()
    try:
        resp = await uc_remote.entity_command(entity_id, cmd_id, params)
    except ConnectionClosedError as exc:
        # Today's failure mode, pinned exactly: the driver drops the connection with 1011 (internal error).
        assert exc.code == 1011, f"connection closed with {exc.code}, expected the known 1011"
        raise
    assert not uc_remote.closed
    expected_code = 400 if cmd_id == "send_cmd" else 200
    assert resp["code"] == expected_code
    if frames is not None:
        assert cec_frames(await sim.log()) == frames
    elif cmd_id == "toggle":
        assert len(cec_frames(await sim.log())) == 1
    assert (await uc_remote.get_driver_version())["code"] == 200


async def test_a_crashing_command_takes_down_only_that_connection(uc_remote_factory, sim: SimDevice) -> None:
    """Pins the UC-01 blast radius: the WebSocket that sent the command is closed with 1011 (a real Remote
    then marks every entity of the integration unavailable and reconnects); other connections survive."""
    bystander = await uc_remote_factory()
    victim = await uc_remote_factory()
    try:
        await victim.remote_on("remote.output_1_cec")
        pytest.fail("UC-01 fixed? remote_on answered; delete this test with the UC-01 fix")
    except ConnectionClosedError as exc:
        assert exc.code == 1011
    assert victim.close_code == 1011
    assert (await bystander.get_driver_version())["code"] == 200
    # The driver keeps serving new connections.
    again = await uc_remote_factory()
    assert (await again.remote_send_cmd("remote.output_1_cec", "POWER_ON"))["code"] == 200


# ---------------------------------------------------------------------- media player (TV power / volume)


async def test_media_player_power_volume_and_mute_send_output_cec(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    """The media player's TV power/volume/mute are display commands: the display table, not the source one."""
    await sim.clear_log()
    for cmd_id, command in (("on", "POWER_ON"), ("off", "POWER_OFF"), ("volume_up", "VOLUME_UP"),
                            ("volume_down", "VOLUME_DOWN"), ("mute_toggle", "MUTE")):
        resp = await uc_remote.entity_command("media_player.output_2", cmd_id)
        assert resp["code"] == 200, cmd_id
        assert cec_frames(await sim.log())[-1] == {
            "object": 1, "port": port_mask(2), "index": PINNED_OUTPUT_CEC_INDEX[command]}, cmd_id
    assert len(cec_frames(await sim.log())) == 5
    assert (await uc_remote.entity_state("media_player.output_2"))["state"] == "OFF"


@known_bug("UC-10", "the media player starts UNKNOWN, and toggle from UNKNOWN sends CEC power OFF (BE-24): "
           "the first toggle turns a TV that is off... off")
async def test_media_player_first_toggle_does_not_turn_the_tv_off(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    assert (await uc_remote.entity_state("media_player.output_1"))["state"] == "UNKNOWN"
    await sim.clear_log()
    assert (await uc_remote.entity_command("media_player.output_1", "toggle"))["code"] == 200
    # Power off is display index 1 (BE-14). Before WP-A4 part 2 this compared against the source
    # table's power off (2), so the new, correct index made the still-present bug look fixed.
    power_off = {"object": 1, "port": port_mask(1), "index": PINNED_OUTPUT_CEC_INDEX["POWER_OFF"]}
    assert power_off not in cec_frames(await sim.log())


# ---------------------------------------------------------------------- matrix power switch


async def test_power_switch_turns_the_matrix_off_and_on(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    assert (await uc_remote.switch("switch.matrix_power", "off"))["code"] == 200
    assert (await sim.state())["system"]["power"] == 0
    assert (await uc_remote.entity_state("switch.matrix_power"))["state"] == "OFF"
    assert (await uc_remote.switch("switch.matrix_power", "toggle"))["code"] == 200
    assert (await sim.state())["system"]["power"] == 1
    assert (await uc_remote.entity_state("switch.matrix_power"))["state"] == "ON"


@known_bug("UC-09", "switch.matrix_power starts ON and is never synced from the polled power state")
async def test_power_switch_follows_a_front_panel_power_change(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    await sim.patch_state({"system": {"power": 0}})

    async def synced() -> bool:
        return (await uc_remote.entity_state("switch.matrix_power"))["state"] == "OFF"

    assert await wait_for(synced, timeout=CYCLE + 2)


@known_bug("UC-09", "the switch handler ignores the connection state: 500 instead of 503 while the matrix is "
           "unreachable")
async def test_power_switch_reports_unavailable_while_the_matrix_is_unreachable(uc_remote: UcRemoteSim,
                                                                              sim: SimDevice) -> None:
    await _matrix_unreachable(uc_remote, sim)
    await sim.clear_log()
    assert (await uc_remote.switch("switch.matrix_power", "on"))["code"] == 503
    assert writes(await sim.log()) == []


async def _matrix_unreachable(remote: UcRemoteSim, sim: SimDevice) -> None:
    """Drop every HTTP request and wait until the driver noticed (it marks remote.orei_matrix UNAVAILABLE)."""
    await sim.set_faults({"drop_http": True})
    await remote.wait_event("entity_change", lambda d: d["entity_id"] == "remote.orei_matrix"
                            and d["attributes"].get("state") == "UNAVAILABLE", timeout=CYCLE)


# ---------------------------------------------------------------------- unavailable / unknown targets


async def test_commands_answer_503_while_the_matrix_is_unreachable(uc_remote: UcRemoteSim, sim: SimDevice) -> None:
    await _matrix_unreachable(uc_remote, sim)
    await sim.clear_log()
    assert (await uc_remote.select_source("media_player.output_1", "PS5"))["code"] == 503
    assert (await uc_remote.button_push("button.preset_1"))["code"] == 503
    assert (await uc_remote.remote_send_cmd("remote.output_1_cec", "POWER_ON"))["code"] == 503
    assert (await uc_remote.remote_send_cmd("remote.orei_matrix", "PRESET_1"))["code"] == 503
    assert sent(await sim.log(), "video switch") == sent(await sim.log(), "preset set") == []


async def test_unknown_and_unsubscribed_entities_answer_404(uc_remote_factory, sim: SimDevice) -> None:
    remote = await uc_remote_factory(entity_ids=["media_player.output_1"])
    assert (await remote.select_source("media_player.output_9", "PS5"))["code"] == 404
    assert (await remote.button_push("button.preset_1"))["code"] == 404  # available, not subscribed
    await remote.unsubscribe_events(["media_player.output_1"])
    await sim.clear_log()
    assert (await remote.select_source("media_player.output_1", "PS5"))["code"] == 404
    assert writes(await sim.log()) == []
