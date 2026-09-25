"""Integration: the real ``OreiMatrix`` (+ ``TelnetClient``) against the simulator."""

import asyncio

import telnet_client


async def test_connect_and_status(matrix, simulator):
    assert await matrix.connect()
    assert matrix.connected
    status = await matrix.get_status(force_refresh=True)
    assert status["power"] == "on"
    assert status["routing"] == [2, 2, 1, 1, 5, 6, 1, 1]
    assert status["input_names"][:3] == ["PS3", "AppleTV", "Computer"]
    assert status["output_names"][:2] == ["TV", "Soundbar"]
    assert status["preset_names"][0] == "Apple TV"
    assert matrix.last_successful_poll is not None
    assert simulator.unrecognised() == []


async def test_names_helpers(matrix):
    await matrix.connect()
    assert (await matrix.get_all_input_names())[7] == "Analogue"
    assert (await matrix.get_output_names())[2] == "Soundbar"


async def test_switch_input(matrix, simulator):
    await matrix.connect()
    assert await matrix.switch_input(6, 1)
    assert simulator.state.outputs[0].source == 6
    assert await matrix.get_current_input_for_output(1) == 6


async def test_switch_input_to_all(matrix, simulator):
    await matrix.connect()
    assert await matrix.switch_input_to_all(3)
    assert simulator.state.routing == [3] * 8


async def test_recall_and_save_preset(matrix, simulator):
    await matrix.connect()
    assert await matrix.recall_preset(2)
    assert simulator.state.routing == [5] * 8
    assert matrix.current_scene == 2
    assert await matrix.switch_input(1, 8)
    assert await matrix.save_preset(7)
    assert simulator.state.presets[6].routing == [5] * 7 + [1]
    assert not await matrix.recall_preset(9)  # validated client-side


async def test_power(matrix, simulator):
    await matrix.connect()
    assert await matrix.power_off()
    assert simulator.state.system["power"] == 0
    assert (await matrix.get_status(force_refresh=True))["power"] == "off"
    assert await matrix.power_on()
    assert (await matrix.get_status(force_refresh=True))["power"] == "on"


async def test_set_names(matrix, simulator):
    await matrix.connect()
    assert await matrix.set_input_name(8, "Xbox Series X")
    assert await matrix.set_output_name(3, "Projector")
    assert simulator.state.inputs[7].name == "Xbox Series X"
    status = await matrix.get_status(force_refresh=True)
    assert status["input_names"][7] == "Xbox Series X"
    assert status["output_names"][2] == "Projector"


async def test_output_settings(matrix, simulator):
    await matrix.connect()
    assert await matrix.set_output_enable(3, False)
    assert await matrix.set_output_hdcp(3, 2)
    assert await matrix.set_output_hdr(3, 1)
    assert await matrix.set_output_scaler(3, 4)
    assert await matrix.set_output_arc(3, True)
    assert await matrix.set_output_audio_mute(3, True)
    o = simulator.state.outputs[2]
    assert (o.stream, o.hdcp, o.hdr, o.scaler, o.arc, o.audio_mute) == (0, 2, 1, 4, 1, 1)
    status = await matrix.get_output_status(force_refresh=True)
    assert status["allout"][2] == 0 and status["allhdcp"][2] == 2 and status["allaudiomute"][2] == 1


async def test_edid(matrix, simulator):
    await matrix.connect()
    assert await matrix.set_input_edid(4, 12)
    assert await matrix.copy_edid_from_output(5, 1)
    assert simulator.state.inputs[3].edid == 12
    assert simulator.state.inputs[4].edid == 15
    edid = await matrix.get_edid_status()
    assert edid["inputs"][4]["mode"] == 12


async def test_system_settings(matrix, simulator):
    await matrix.connect()
    assert await matrix.set_beep(False)
    assert await matrix.set_panel_lock(True)
    assert await matrix.set_lcd_timeout(0)
    assert simulator.state.system["beep"] == 0
    assert simulator.state.system["panel_lock"] == 1
    assert simulator.state.system["lcd_timeout"] == 0
    full = await matrix.get_full_status()
    assert full["beep_enabled"] is False and full["panel_locked"] is True
    assert full["firmware_version"] == "V1.10.01" and full["model"] == "BK-808"
    assert (await matrix.get_network_info())["ipaddress"] == "192.168.0.100"


async def test_ext_audio(matrix, simulator):
    await matrix.connect()
    assert await matrix.set_ext_audio_mode(2)
    assert await matrix.set_ext_audio_enable(4, True)
    assert await matrix.set_ext_audio_source(4, 6)
    status = await matrix.get_ext_audio_status()
    assert status["mode"] == 2 and status["allout"][3] == 1 and status["allsource"][3] == 6


async def test_cec_http_auto_enables_port(matrix, simulator):
    await matrix.connect()
    assert simulator.state.inputs[0].cec_enabled == 0
    assert await matrix.send_cec("PLAY", 1)
    assert simulator.state.inputs[0].cec_enabled == 1  # ensure_cec_enabled flipped it
    cec_calls = [e for e in simulator.log if e["command"] == "cec command"]
    assert cec_calls[-1]["payload"]["index"] == matrix.CEC_COMMAND_MAP["PLAY"]
    assert cec_calls[-1]["warnings"] == []


async def test_cec_enable_single_port_shape(matrix, simulator):
    """BE-13: set_cec_enable sends an undocumented payload; the simulator accepts and flags it."""
    await matrix.connect()
    assert await matrix.set_cec_enable("output", 5, True)
    assert simulator.state.outputs[4].cec_enabled == 1
    assert any("BE-13" in w for w in simulator.log[-1]["warnings"])


async def test_capabilities(matrix, simulator):
    await matrix.connect()
    caps = await matrix.get_all_capabilities()
    assert caps["inputs"][1]["signal_detected"] is True
    assert caps["outputs"][0]["connected"] is True and caps["outputs"][0]["arc_enabled"] is True


async def test_audio_only_output_detected(matrix, simulator):
    """BE-15 (read side): MCU V1.10.01 reports scaler 4 for an audio-only output (its Telnet
    status prints "audio only"), which is what the hub checks. The setter's 5 is still unverified."""
    await matrix.connect()
    assert simulator.state.outputs[1].scaler == 4  # Soundbar is audio-only in the seed
    caps = await matrix.get_output_capabilities(2)
    assert caps["is_audio_only"] is True


# ------------------------------------------------------------------ Telnet


async def test_telnet_connects_and_reads_firmware(matrix_with_telnet):
    assert await matrix_with_telnet.connect()
    assert matrix_with_telnet.telnet_connected
    assert matrix_with_telnet._telnet.firmware_version == "1.10.01"


async def test_telnet_cable_and_full_status(matrix_with_telnet, simulator):
    m = matrix_with_telnet
    await m.connect()
    cables = await m.get_all_cable_status(force_refresh=True)
    assert cables["inputs"] == {i + 1: bool(p.cable) for i, p in enumerate(simulator.state.inputs)}
    assert cables["outputs"] == {i + 1: bool(o.connected) for i, o in enumerate(simulator.state.outputs)}
    assert await m.get_input_cable_status(3) is False
    assert await m.get_output_cable_status(1) is True
    full = await m.get_telnet_full_status()
    assert full.routing == {i + 1: s for i, s in enumerate(simulator.state.routing)}
    info = await m.get_preset_info(1)
    assert info == {"preset": 1, "routing": {i: 2 for i in range(1, 9)}, "saved": True}


async def test_telnet_push_cable_event_reaches_client(matrix_with_telnet, simulator):
    m = matrix_with_telnet
    await m.connect()
    seen = []
    m._telnet._on_status_update = seen.append
    await simulator.cable_event("output", 2, False)
    for _ in range(40):
        if seen:
            break
        await asyncio.sleep(0.05)
    assert seen and seen[0].outputs[2].connected is False


async def test_telnet_cec(matrix_with_telnet, simulator, monkeypatch):
    """OREI_USE_TELNET_CEC path."""
    m = matrix_with_telnet
    await m.connect()
    monkeypatch.setattr(m, "_use_telnet_cec", True)
    assert await m.send_cec("POWER_ON", 1, is_output=True)
    telnet_cmds = [e["command"] for e in simulator.log if e["channel"] == "telnet"]
    assert "s cec hdmi out 1 on" in telnet_cmds


async def test_telnet_set_commands_complete_on_ack(matrix_with_telnet, simulator, monkeypatch):
    """BE-07: set commands return on the acknowledgement, not after COMMAND_TIMEOUT."""
    monkeypatch.setattr(telnet_client, "COMMAND_TIMEOUT", 5.0)  # the production value
    m = matrix_with_telnet
    await m.connect()
    telnet = m._telnet
    loop = asyncio.get_running_loop()
    start = loop.time()
    assert await telnet.cec_output_power_on(1)
    assert await telnet.cec_input_play(2)
    assert await telnet.switch_input(4, 3)
    assert await telnet.save_preset(3)
    assert await telnet.recall_preset(3)
    assert loop.time() - start < 2.0, "set commands waited for the command timeout"
    assert simulator.state.outputs[2].source == 4


async def test_telnet_error_codes_mean_failure(matrix_with_telnet, simulator, monkeypatch):
    """BE-07: E01 (bad parameter) and E00 (unknown command) are failures, returned promptly."""
    monkeypatch.setattr(telnet_client, "COMMAND_TIMEOUT", 5.0)
    m = matrix_with_telnet
    await m.connect()
    telnet = m._telnet
    loop = asyncio.get_running_loop()
    start = loop.time()
    assert await telnet._send_cec_input(1, "bogus") is False  # E01
    assert await telnet.power_on() is False  # "power 1" -> E00 in the simulator (HIL-A)
    assert loop.time() - start < 1.0
    assert m.telnet_connected


async def test_telnet_unanswered_set_command_is_failure(matrix_with_telnet, simulator):
    m = matrix_with_telnet
    await m.connect()
    simulator.faults.update({"telnet_silent": True, "telnet_fault_count": 1})
    assert await m._telnet.cec_output_power_off(1) is False
    assert m.telnet_connected  # silence is a timeout, not a dropped connection
