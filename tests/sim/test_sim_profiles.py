"""Profile recall, CEC macros and the scene CEC auto-resolve on the real hub app, a real OreiMatrix and the simulator.

Hub data: ``tests/e2e/fixtures/data`` (``data_hub``): ``movie_night`` routes
input 2 to outputs 1-2, sets HDR 1 / HDCP 3 on output 1, mutes output 2 and
has the power-on macro ``macro_tv_on`` (CEC power on to output 1, then input
2); ``game_day`` routes input 5 to outputs 1-3 and mutes output 3;
``macro_volume_up`` sends three volume-up frames to output 2.

WP-C1 regressions: VAL-01, VAL-02, API-08, API-23. Each test asserts the
effect on the simulator, not only the HTTP answer.
"""

from __future__ import annotations

from .conftest import CEC_IN_POWER_ON, CEC_OUT_POWER_ON, CEC_OUT_VOL_UP, body, cec_frames, sim_writes

# ============================================================================= profile recall


async def test_recall_applies_mute_hdr_and_hdcp(data_hub, simulator):
    """VAL-01: recall looked for ``set_audio_mute`` / ``set_hdr_mode`` / ``set_hdcp_mode``, which do not exist."""
    out1 = simulator.state.outputs[0]
    out1.hdr, out1.hdcp = 2, 1
    resp = await data_hub.post("/api/profile/movie_night/recall")
    assert resp.status == 200, await resp.text()
    assert out1.hdr == 0  # profile HDR 1 (API, passthrough) -> device code 0
    assert out1.hdcp == 3
    assert simulator.state.outputs[1].audio_mute == 1
    assert out1.audio_mute == 0
    assert [e["payload"]["mute"] for e in sim_writes(simulator, "set output audio mute")] == [[1, 0], [2, 1]]


async def test_recall_runs_the_power_on_macro(data_hub, simulator):
    """VAL-02: modular mode never wired the macro CEC sender ("CEC sender not configured")."""
    resp = await data_hub.post("/api/profile/movie_night/recall")
    assert resp.status == 200, await resp.text()
    data = (await body(resp))["data"]
    assert data["power_on_macro"]["success"] is True
    assert cec_frames(simulator, obj=1, index=CEC_OUT_POWER_ON, to=1) == 1
    assert cec_frames(simulator, obj=0, index=CEC_IN_POWER_ON, to=2) == 1


async def test_recall_with_every_write_rejected_is_500(data_hub, simulator):
    """API-08: recall answered 200 ``success: true`` when every output failed."""
    simulator.faults.reject_writes = True
    resp = await data_hub.post("/api/profile/game_day/recall")
    assert resp.status == 500, await resp.text()
    payload = await body(resp)
    assert payload["success"] is False
    assert payload["data"]["failed_outputs"] == [1, 2, 3]
    assert payload["data"]["applied"] == []
    assert [o.source for o in simulator.state.outputs[:3]] == [2, 2, 1]


async def test_recall_reports_a_failed_setting_as_partial(data_hub, simulator, monkeypatch):
    """API-08: one output whose mute write is refused -> 207, that output listed as failed."""
    from rest_api.utils import get_matrix_device

    matrix = get_matrix_device()
    real = matrix.set_output_audio_mute

    async def refuse_output_3(output_num, mute):
        return False if output_num == 3 else await real(output_num, mute)

    monkeypatch.setattr(matrix, "set_output_audio_mute", refuse_output_3)
    resp = await data_hub.post("/api/profile/game_day/recall")
    assert resp.status == 207, await resp.text()
    payload = await body(resp)
    assert payload["success"] is False
    assert payload["data"]["failed_outputs"] == [3]
    assert [o.source for o in simulator.state.outputs[:3]] == [5, 5, 5]


async def test_recall_reports_a_missing_power_on_macro(data_hub, simulator):
    """API-08: a power-on macro that does not exist used to be skipped silently."""
    resp = await data_hub.put("/api/profile/game_day", json={"power_on_macro": "macro_nope"})
    assert resp.status == 200, await resp.text()
    resp = await data_hub.post("/api/profile/game_day/recall")
    assert resp.status == 207, await resp.text()
    data = (await body(resp))["data"]
    assert data["power_on_macro"]["success"] is False
    assert data["failed_outputs"] == []
    assert [o.source for o in simulator.state.outputs[:3]] == [5, 5, 5]


# ============================================================================= macros


async def test_macro_execute_sends_cec_frames(data_hub, simulator):
    """VAL-02: ``POST /api/cec/macro/{id}/execute`` in modular mode."""
    resp = await data_hub.post("/api/cec/macro/macro_volume_up/execute")
    assert resp.status == 200, await resp.text()
    assert cec_frames(simulator, obj=1, index=CEC_OUT_VOL_UP, to=2) == 3


async def test_macro_sender_refuses_without_a_connected_matrix(data_hub, simulator):
    from rest_api.utils import get_matrix_device, matrix_cec_sender

    await get_matrix_device().disconnect()
    assert await matrix_cec_sender("output", 1, "POWER_ON") is False
    assert await matrix_cec_sender("bogus", 1, "POWER_ON") is False
    assert cec_frames(simulator, obj=1, index=CEC_OUT_POWER_ON, to=1) == 0


# ============================================================================= scene CEC auto-resolve (v1 alias)


async def test_scene_cec_auto_resolve(data_hub, simulator):
    """API-23: the endpoint called the resolver with the wrong arguments -> always 500."""
    resp = await data_hub.post("/api/scene/game_day/cec/auto-resolve")
    assert resp.status == 200, await resp.text()
    cfg = (await body(resp))["data"]
    assert cfg["auto_resolved"] is True
    assert cfg["nav_targets"] == ["input_5"] and cfg["playback_targets"] == ["input_5"]
    # output 2 is the audio-only soundbar in the seed state (scaler device code 4)
    assert cfg["volume_targets"] == ["output_2"]
    assert cfg["power_on_targets"] == ["input_5", "output_1", "output_2", "output_3"]
    assert cfg["power_off_targets"] == ["output_1", "output_2", "output_3"]
    saved = (await body(await data_hub.get("/api/profile/game_day/cec")))["data"]["cec_config"]
    assert saved["volume_targets"] == ["output_2"]
    assert (await data_hub.post("/api/scene/nope/cec/auto-resolve")).status == 404


async def test_scene_cec_auto_resolve_without_a_matrix_answer(data_hub, simulator):
    """With no output status (matrix unreachable) the resolver still answers from the profile alone."""
    simulator.faults.drop_http = True
    resp = await data_hub.post("/api/scene/game_day/cec/auto-resolve")
    assert resp.status == 200, await resp.text()
    cfg = (await body(resp))["data"]
    assert cfg["volume_targets"] == ["output_1"]
