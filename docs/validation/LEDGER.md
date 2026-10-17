# Feature ledger

> **Generated** by `python -m tools.validate ledger` — do not edit by hand. Registry: [`features.yaml`](features.yaml) · Plan: [`VALIDATION_PLAN.md`](VALIDATION_PLAN.md) · How to add evidence: [`README.md`](README.md).
> Commit `5d5cd412`

**Level** = highest level with fresh passing evidence, else the recorded baseline (the registry's `current`), capped at V1 while an open critical/high finding is linked. **Recorded** = the registry baseline. **Fresh** = evidence commit not older than the last change to the scenario's `covers` paths.

## Summary

| Area | Features | V0 | V1 | V2 | V3 | V4 | V5 | Below target | Stale evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Matrix control | 31 | 1 | 24 | 1 | 5 | 0 | 0 | 31 | 31 |
| CEC control | 11 | 0 | 10 | 0 | 1 | 0 | 0 | 11 | 11 |
| REST/WebSocket contract | 42 | 2 | 23 | 16 | 1 | 0 | 0 | 32 | 30 |
| Domain features | 36 | 2 | 17 | 7 | 10 | 0 | 0 | 32 | 30 |
| Web UI | 36 | 0 | 25 | 0 | 11 | 0 | 0 | 25 | 9 |
| Kiosk | 14 | 0 | 8 | 0 | 6 | 0 | 0 | 8 | 5 |
| Remote 3 integration | 17 | 1 | 2 | 0 | 14 | 0 | 0 | 17 | 8 |
| Home Assistant component | 18 | 0 | 1 | 0 | 17 | 0 | 0 | 18 | 17 |
| Flic | 10 | 3 | 7 | 0 | 0 | 0 | 0 | 10 | 0 |
| Deployment, configuration, persistence | 20 | 3 | 8 | 2 | 7 | 0 | 0 | 20 | 7 |
| Security controls | 15 | 0 | 13 | 0 | 2 | 0 | 0 | 13 | 0 |
| Reliability | 18 | 12 | 3 | 1 | 2 | 0 | 0 | 18 | 5 |
| **All** | **268** | **24** | **141** | **27** | **76** | **0** | **0** | **235** | **153** |

Levels: **V0** Claimed · **V1** Unit · **V2** Simulated integration · **V3** End-to-end · **V4** Hardware · **V5** Field

Recorded baseline (the registry's `current`: proof that existed before scenario evidence, see [`README.md`](README.md#recorded-baseline-c-pre-2026-09-25)):

| Area | V0 | V1 | V2 | V3 | V4 | V5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Matrix control | 1 | 24 | 1 | 5 | 0 | 0 |
| CEC control | 0 | 10 | 0 | 1 | 0 | 0 |
| REST/WebSocket contract | 2 | 23 | 16 | 1 | 0 | 0 |
| Domain features | 2 | 17 | 7 | 10 | 0 | 0 |
| Web UI | 0 | 25 | 0 | 11 | 0 | 0 |
| Kiosk | 0 | 8 | 0 | 6 | 0 | 0 |
| Remote 3 integration | 1 | 2 | 0 | 14 | 0 | 0 |
| Home Assistant component | 0 | 1 | 0 | 17 | 0 | 0 |
| Flic | 3 | 7 | 0 | 0 | 0 | 0 |
| Deployment, configuration, persistence | 3 | 8 | 2 | 7 | 0 | 0 |
| Security controls | 0 | 13 | 0 | 2 | 0 | 0 |
| Reliability | 12 | 3 | 1 | 2 | 0 | 0 |
| **All** | **24** | **141** | **27** | **76** | **0** | **0** |

- Features with fresh passing scenario evidence: **0** of 268.
- Features with a fresh failing scenario: **0**.
- Features capped at V1 by an open critical/high finding: **12**.

## Matrix control (F-MTX)

| ID | Feature | Target | Level | Recorded | Freshness | Evidence | Open findings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-MTX-001 | Route one input to one output | V4 | V3 | V3 | stale | [ha.select_source·ha·pass](evidence/F-HA-002/2026-10-04-V3-7dbc4dc7-ha.select_source-ha.json)<br>[routing.switch_one·api·pass](evidence/F-MTX-001/2026-10-04-V2-d6baf3ca-routing.switch_one-api.json) | — |
| F-MTX-002 | Route one input to every output | V4 | V3 | V3 | stale | [routing.route_all·api·pass](evidence/F-MTX-002/2026-10-04-V2-d6baf3ca-routing.route_all-api.json)<br>[routing.route_all·browser·pass](evidence/F-MTX-002/2026-10-04-V3-d6baf3ca-routing.route_all-browser.json) | — |
| F-MTX-003 | Recall a matrix preset (1-8) | V4 | V3 | V3 | stale | [ha.preset_button·ha·pass](evidence/F-HA-006/2026-10-04-V3-7dbc4dc7-ha.preset_button-ha.json)<br>[presets.recall·api·pass](evidence/F-MTX-003/2026-10-04-V2-d6baf3ca-presets.recall-api.json) | — |
| F-MTX-004 | Save the current routing to a matrix preset | V4 | V1 | V1 | stale | [matrix.preset_invalid_slot·api·pass](evidence/F-MTX-004/2026-10-04-V2-7dbc4dc7-matrix.preset_invalid_slot-api.json)<br>[matrix.preset_refused·api·pass](evidence/F-MTX-004/2026-10-04-V2-7dbc4dc7-matrix.preset_refused-api.json) | — |
| F-MTX-005 | Name presets in the web app (names shown by the API, UI, kiosk) | V4 | V0 | V0 | stale | [presets.rename·api·pass](evidence/F-MTX-005/2026-10-04-V2-d6baf3ca-presets.rename-api.json)<br>[presets.rename·browser·pass](evidence/F-MTX-005/2026-10-04-V3-d6baf3ca-presets.rename-browser.json) | BE-16(M) |
| F-MTX-006 | Matrix power on / standby | V4 | V3 | V3 | stale | [ha.power_off·ha·pass](evidence/F-HA-003/2026-10-04-V3-7dbc4dc7-ha.power_off-ha.json)<br>[ha.power_on·ha·pass](evidence/F-HA-003/2026-10-04-V3-7dbc4dc7-ha.power_on-ha.json) | — |
| F-MTX-007 | Mute / unmute the audio of an output | V4 | V1 (capped) | V1 | stale | [ha.mute_switch·ha·pass](evidence/F-HA-004/2026-10-04-V3-7dbc4dc7-ha.mute_switch-ha.json)<br>[outputs.audio_mute·api·pass](evidence/F-MTX-007/2026-10-04-V2-7dbc4dc7-outputs.audio_mute-api.json) | HIL-09(C) |
| F-MTX-008 | Enable / disable an output's video stream | V4 | V1 (capped) | V1 | stale | [settings.enable_0·api·pass](evidence/F-MTX-008/2026-10-04-V2-7dbc4dc7-settings.enable_0-api.json)<br>[settings.enable_1·api·pass](evidence/F-MTX-008/2026-10-04-V2-7dbc4dc7-settings.enable_1-api.json) | HIL-09(C) |
| F-MTX-009 | Set an output's HDCP mode | V4 | V1 (capped) | V1 | stale | [settings.hdcp_1·api·pass](evidence/F-MTX-009/2026-10-04-V2-7dbc4dc7-settings.hdcp_1-api.json)<br>[settings.hdcp_2·api·pass](evidence/F-MTX-009/2026-10-04-V2-7dbc4dc7-settings.hdcp_2-api.json) | HIL-09(C) |
| F-MTX-010 | Set an output's HDR mode | V4 | V1 (capped) | V1 | stale | [settings.hdr_1·api·pass](evidence/F-MTX-010/2026-10-04-V2-7dbc4dc7-settings.hdr_1-api.json)<br>[settings.hdr_2·api·pass](evidence/F-MTX-010/2026-10-04-V2-7dbc4dc7-settings.hdr_2-api.json) | HIL-09(C) |
| F-MTX-011 | Set an output's scaler mode (incl. audio-only) | V4 | V1 (capped) | V1 | stale | [settings.scaler_1·api·pass](evidence/F-MTX-011/2026-10-04-V2-7dbc4dc7-settings.scaler_1-api.json)<br>[settings.scaler_2·api·pass](evidence/F-MTX-011/2026-10-04-V2-7dbc4dc7-settings.scaler_2-api.json) | BE-15(M), HIL-09(C) |
| F-MTX-012 | Enable / disable ARC on an output | V4 | V1 (capped) | V1 | stale | [settings.arc_0·api·pass](evidence/F-MTX-012/2026-10-04-V2-7dbc4dc7-settings.arc_0-api.json)<br>[settings.arc_1·api·pass](evidence/F-MTX-012/2026-10-04-V2-7dbc4dc7-settings.arc_1-api.json) | HIL-09(C) |
| F-MTX-013 | Set an input's EDID | V4 | V1 (capped) | V1 | stale | [settings.edid_input_0·api·pass](evidence/F-MTX-013/2026-10-04-V2-7dbc4dc7-settings.edid_input_0-api.json)<br>[settings.edid_input_9·api·pass](evidence/F-MTX-013/2026-10-04-V2-7dbc4dc7-settings.edid_input_9-api.json) | HIL-09(C) |
| F-MTX-014 | Copy EDID from a connected display | V4 | V1 (capped) | V1 | stale | [settings.edid_copy_invalid_0·api·pass](evidence/F-MTX-014/2026-10-04-V2-7dbc4dc7-settings.edid_copy_invalid_0-api.json)<br>[settings.edid_copy_invalid_9·api·pass](evidence/F-MTX-014/2026-10-04-V2-7dbc4dc7-settings.edid_copy_invalid_9-api.json) | BE-25(L), HIL-09(C) |
| F-MTX-015 | External audio: matrix mode | V4 | V1 (capped) | V1 | stale | [audio.mode_0·api·pass](evidence/F-MTX-015/2026-10-04-V2-7dbc4dc7-audio.mode_0-api.json)<br>[audio.mode_1·api·pass](evidence/F-MTX-015/2026-10-04-V2-7dbc4dc7-audio.mode_1-api.json) | HIL-09(C) |
| F-MTX-016 | External audio: enable per output | V4 | V1 (capped) | V1 | stale | [audio.enable_1_0·api·pass](evidence/F-MTX-016/2026-10-04-V2-7dbc4dc7-audio.enable_1_0-api.json)<br>[audio.enable_1_1·api·pass](evidence/F-MTX-016/2026-10-04-V2-7dbc4dc7-audio.enable_1_1-api.json) | HIL-09(C) |
| F-MTX-017 | External audio: source per output | V4 | V1 (capped) | V1 | stale | [audio.source_1_1·api·pass](evidence/F-MTX-017/2026-10-04-V2-7dbc4dc7-audio.source_1_1-api.json)<br>[audio.source_1_2·api·pass](evidence/F-MTX-017/2026-10-04-V2-7dbc4dc7-audio.source_1_2-api.json) | HIL-09(C) |
| F-MTX-018 | Front-panel beep on / off | V4 | V1 | V1 | stale | [matrix.beep_off·api·pass](evidence/F-MTX-018/2026-10-04-V2-7dbc4dc7-matrix.beep_off-api.json)<br>[matrix.beep_on·api·pass](evidence/F-MTX-018/2026-10-04-V2-7dbc4dc7-matrix.beep_on-api.json) | — |
| F-MTX-019 | Front-panel lock | V4 | V1 | V1 | stale | [matrix.panel_lock_off·api·pass](evidence/F-MTX-019/2026-10-04-V2-7dbc4dc7-matrix.panel_lock_off-api.json)<br>[matrix.panel_lock_on·api·pass](evidence/F-MTX-019/2026-10-04-V2-7dbc4dc7-matrix.panel_lock_on-api.json) | — |
| F-MTX-020 | Front-panel LCD timeout | V4 | V1 (capped) | V1 | stale | [matrix.lcd_invalid_mode·api·pass](evidence/F-MTX-020/2026-10-04-V2-7dbc4dc7-matrix.lcd_invalid_mode-api.json)<br>[matrix.lcd_missing_mode·api·pass](evidence/F-MTX-020/2026-10-04-V2-7dbc4dc7-matrix.lcd_missing_mode-api.json) | API-07(M), HIL-09(C) |
| F-MTX-021 | Reboot the matrix | V4 | V1 | V1 | stale | [reboot.direct·api·pass](evidence/F-MTX-021/2026-10-04-V2-d6baf3ca-reboot.direct-api.json)<br>[reboot.enabled_shortcut·api·pass](evidence/F-MTX-021/2026-10-04-V2-d6baf3ca-reboot.enabled_shortcut-api.json) | — |
| F-MTX-022 | Rename inputs (names stored on the matrix) | V4 | V1 | V1 | stale | [matrix.input_blank_name·api·pass](evidence/F-MTX-022/2026-10-04-V2-7dbc4dc7-matrix.input_blank_name-api.json)<br>[matrix.input_invalid_port·api·pass](evidence/F-MTX-022/2026-10-04-V2-7dbc4dc7-matrix.input_invalid_port-api.json) | BE-16(M) |
| F-MTX-023 | Rename outputs (names stored on the matrix) | V4 | V1 | V1 | stale | [matrix.output_blank_name·api·pass](evidence/F-MTX-023/2026-10-04-V2-7dbc4dc7-matrix.output_blank_name-api.json)<br>[matrix.output_invalid_port·api·pass](evidence/F-MTX-023/2026-10-04-V2-7dbc4dc7-matrix.output_invalid_port-api.json) | BE-16(M) |
| F-MTX-024 | Read the current routing and names | V4 | V2 | V2 | stale | [status.routing_all_1·api·pass](evidence/F-MTX-024/2026-10-04-V2-7dbc4dc7-status.routing_all_1-api.json)<br>[status.routing_all_8·api·pass](evidence/F-MTX-024/2026-10-04-V2-7dbc4dc7-status.routing_all_8-api.json) | — |
| F-MTX-025 | Show which inputs have an active signal | V4 | V1 | V1 | stale | [status.signal_1_0·api·pass](evidence/F-MTX-025/2026-10-04-V2-7dbc4dc7-status.signal_1_0-api.json)<br>[status.signal_1_1·api·pass](evidence/F-MTX-025/2026-10-04-V2-7dbc4dc7-status.signal_1_1-api.json) | — |
| F-MTX-026 | Show which cables are plugged in (Telnet link status) | V4 | V1 | V1 | stale | [status.cables_all·api·pass](evidence/F-MTX-026/2026-10-04-V2-7dbc4dc7-status.cables_all-api.json)<br>[status.cables_alternating·api·pass](evidence/F-MTX-026/2026-10-04-V2-7dbc4dc7-status.cables_alternating-api.json) | HIL-03(M) |
| F-MTX-027 | Show which outputs have a display connected | V4 | V1 | V1 | stale | [status.display_1_0·api·pass](evidence/F-MTX-027/2026-10-04-V2-7dbc4dc7-status.display_1_0-api.json)<br>[status.display_1_1·api·pass](evidence/F-MTX-027/2026-10-04-V2-7dbc4dc7-status.display_1_1-api.json) | — |
| F-MTX-028 | Show device info (model, firmware, network) | V4 | V1 | V1 | stale | [status.device_dhcp_0·api·pass](evidence/F-MTX-028/2026-10-04-V2-7dbc4dc7-status.device_dhcp_0-api.json)<br>[status.device_dhcp_1·api·pass](evidence/F-MTX-028/2026-10-04-V2-7dbc4dc7-status.device_dhcp_1-api.json) | — |
| F-MTX-029 | Cycle an output to the next / previous input | V4 | V1 | V1 | stale | [status.cycle_next_1_1·api·pass](evidence/F-MTX-029/2026-10-04-V2-7dbc4dc7-status.cycle_next_1_1-api.json)<br>[status.cycle_next_1_2·api·pass](evidence/F-MTX-029/2026-10-04-V2-7dbc4dc7-status.cycle_next_1_2-api.json) | — |
| F-MTX-030 | Read a preset's stored routing | V4 | V1 | V1 | stale | [preset_read.device_slot_1·api·fail](evidence/F-MTX-030/2026-10-02-V2-f4f417bf-preset_read.device_slot_1-api.json)<br>[preset_read.device_slot_2·api·fail](evidence/F-MTX-030/2026-10-02-V2-f4f417bf-preset_read.device_slot_2-api.json) | — |
| F-MTX-031 | Notice changes made outside the hub (front panel, cable plugged, source on/off) | V4 | V3 | V3 | stale | [ha.front_panel_route·ha·pass](evidence/F-HA-002/2026-10-04-V3-7dbc4dc7-ha.front_panel_route-ha.json)<br>[live.display_unplugged·browser·pass](evidence/F-MTX-031/2026-10-04-V3-d6baf3ca-live.display_unplugged-browser.json) | — |

## CEC control (F-CEC)

| ID | Feature | Target | Level | Recorded | Freshness | Evidence | Open findings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-CEC-001 | Power a source on / off over CEC | V4 | V1 | V1 | stale | [cec.input_power_on·api·pass](evidence/F-CEC-001/2026-10-04-V2-7dbc4dc7-cec.input_power_on-api.json)<br>[cec_controls.input_1_power_off·api·pass](evidence/F-CEC-001/2026-10-04-V2-7dbc4dc7-cec_controls.input_1_power_off-api.json) | — |
| F-CEC-002 | Navigate a source's menus over CEC (up/down/left/right/select/menu/back) | V4 | V1 | V1 | stale | [cec_controls.input_1_back·api·pass](evidence/F-CEC-002/2026-10-04-V2-7dbc4dc7-cec_controls.input_1_back-api.json)<br>[cec_controls.input_1_down·api·pass](evidence/F-CEC-002/2026-10-04-V2-7dbc4dc7-cec_controls.input_1_down-api.json) | — |
| F-CEC-003 | Control playback on a source over CEC | V4 | V1 | V1 | stale | [cec_controls.input_1_fast_forward·api·pass](evidence/F-CEC-003/2026-10-04-V2-7dbc4dc7-cec_controls.input_1_fast_forward-api.json)<br>[cec_controls.input_1_next·api·pass](evidence/F-CEC-003/2026-10-04-V2-7dbc4dc7-cec_controls.input_1_next-api.json) | — |
| F-CEC-004 | Source volume / mute over CEC | V4 | V1 | V1 | stale | [cec_controls.input_1_mute·api·pass](evidence/F-CEC-004/2026-10-04-V2-7dbc4dc7-cec_controls.input_1_mute-api.json)<br>[cec_controls.input_1_volume_down·api·pass](evidence/F-CEC-004/2026-10-04-V2-7dbc4dc7-cec_controls.input_1_volume_down-api.json) | — |
| F-CEC-005 | Turn a display (TV) on / off over CEC | V4 | V3 | V3 | stale | [cec.output_power_on·api·pass](evidence/F-CEC-005/2026-10-04-V2-7dbc4dc7-cec.output_power_on-api.json)<br>[cec_controls.output_1_power_off·api·pass](evidence/F-CEC-005/2026-10-04-V2-7dbc4dc7-cec_controls.output_1_power_off-api.json) | BE-14(M) |
| F-CEC-006 | Display / soundbar volume and mute over CEC | V4 | V1 | V1 | stale | [cec.output_volume_up·api·pass](evidence/F-CEC-006/2026-10-04-V2-7dbc4dc7-cec.output_volume_up-api.json)<br>[cec_controls.output_1_mute·api·pass](evidence/F-CEC-006/2026-10-04-V2-7dbc4dc7-cec_controls.output_1_mute-api.json) | BE-14(M) |
| F-CEC-007 | Enable CEC on the target port automatically before a command | V4 | V1 | V1 | stale | [cec_controls.output_1_active·api·pass](evidence/F-API-015/2026-10-04-V2-7dbc4dc7-cec_controls.output_1_active-api.json)<br>[cec_controls.output_2_active·api·pass](evidence/F-API-015/2026-10-04-V2-7dbc4dc7-cec_controls.output_2_active-api.json) | — |
| F-CEC-008 | Enable / disable CEC per port | V4 | V1 | V1 | stale | [cec_controls.input_1_enable_0·api·pass](evidence/F-CEC-008/2026-10-04-V2-7dbc4dc7-cec_controls.input_1_enable_0-api.json)<br>[cec_controls.input_1_enable_1·api·pass](evidence/F-CEC-008/2026-10-04-V2-7dbc4dc7-cec_controls.input_1_enable_1-api.json) | — |
| F-CEC-009 | Read which ports have CEC enabled | V4 | V1 | V1 | stale | [cec_controls.status_mixed·api·pass](evidence/F-CEC-009/2026-10-04-V2-7dbc4dc7-cec_controls.status_mixed-api.json)<br>[cec_controls.status_off·api·pass](evidence/F-CEC-009/2026-10-04-V2-7dbc4dc7-cec_controls.status_off-api.json) | — |
| F-CEC-010 | Send CEC over Telnet (OREI_USE_TELNET_CEC) | V4 | V1 | V1 | stale | [cec_telnet.input_interrupted_volume·api·fail](evidence/F-CEC-010/2026-10-02-V2-a538a8ef-cec_telnet.input_interrupted_volume-api.json)<br>[cec_telnet.output_interrupted_volume·api·fail](evidence/F-CEC-010/2026-10-02-V2-a538a8ef-cec_telnet.output_interrupted_volume-api.json) | — |
| F-CEC-011 | List CEC commands and per-port capabilities (incl. audio-only outputs) | V4 | V1 | V1 | stale | [cec_caps.all_pattern_0·api·pass](evidence/F-CEC-011/2026-10-04-V2-7dbc4dc7-cec_caps.all_pattern_0-api.json)<br>[cec_caps.all_pattern_1·api·pass](evidence/F-CEC-011/2026-10-04-V2-7dbc4dc7-cec_caps.all_pattern_1-api.json) | BE-15(M) |

## REST/WebSocket contract (F-API)

| ID | Feature | Target | Level | Recorded | Freshness | Evidence | Open findings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-API-001 | GET /api/health (liveness, matrix connection, runtime metrics) | V3 | V2 | V2 | — | — | — |
| F-API-002 | API info and root (GET /, /api, /api/info) | V2 | V1 | V1 | — | — | DEP-06(M) |
| F-API-003 | GET /api/status | V3 | V2 | V2 | — | — | — |
| F-API-004 | Detailed status (GET /api/status/full\|inputs\|outputs\|cables\|edid\|ext-audio\|system\|device\|cec) | V3 | V1 | V1 | stale | [contracts.cables·api·pass](evidence/F-API-004/2026-10-04-V2-7dbc4dc7-contracts.cables-api.json)<br>[contracts.cec_status·api·pass](evidence/F-API-004/2026-10-04-V2-7dbc4dc7-contracts.cec_status-api.json) | — |
| F-API-005 | POST /api/switch (one output or all) | V3 | V2 | V2 | stale | [routing.switch_one·api·pass](evidence/F-MTX-001/2026-10-04-V2-d6baf3ca-routing.switch_one-api.json)<br>[routing.route_all·api·pass](evidence/F-MTX-002/2026-10-04-V2-d6baf3ca-routing.route_all-api.json) | — |
| F-API-006 | POST /api/output/{output}/source and input cycling | V3 | V1 | V1 | — | — | — |
| F-API-007 | POST /api/preset/{preset} (recall) | V3 | V2 | V2 | stale | [presets.recall·api·pass](evidence/F-MTX-003/2026-10-04-V2-d6baf3ca-presets.recall-api.json)<br>[presets.recall·api·pass](evidence/F-MTX-003/2026-10-10-V2-b6dbfaca-presets.recall-api.json) | — |
| F-API-008 | POST /api/preset/{preset}/save | V2 | V1 | V1 | stale | [preset_read.saved_partial_1·api·pass](evidence/F-DOM-034/2026-10-04-V2-7dbc4dc7-preset_read.saved_partial_1-api.json)<br>[preset_read.saved_partial_2·api·pass](evidence/F-DOM-034/2026-10-04-V2-7dbc4dc7-preset_read.saved_partial_2-api.json) | — |
| F-API-009 | POST /api/power/on\|off | V3 | V1 | V1 | stale | [power.standby·api·pass](evidence/F-MTX-006/2026-10-04-V2-7dbc4dc7-power.standby-api.json)<br>[power.wake·api·pass](evidence/F-MTX-006/2026-10-04-V2-7dbc4dc7-power.wake-api.json) | — |
| F-API-010 | Output setting routes (mute, enable, hdcp, hdr, scaler, arc) | V2 | V1 | V1 | — | — | — |
| F-API-011 | EDID routes | V2 | V1 | V1 | — | — | — |
| F-API-012 | External audio routes | V2 | V1 | V1 | — | — | — |
| F-API-013 | System setting routes (beep, panel lock, LCD, reboot) | V2 | V1 | V1 | stale | [reboot.direct·api·pass](evidence/F-MTX-021/2026-10-04-V2-d6baf3ca-reboot.direct-api.json)<br>[reboot.enabled_shortcut·api·pass](evidence/F-MTX-021/2026-10-04-V2-d6baf3ca-reboot.enabled_shortcut-api.json) | — |
| F-API-014 | System info and storage routes | V2 | V1 | V1 | stale | [contracts.storage·api·pass](evidence/F-API-014/2026-10-04-V2-7dbc4dc7-contracts.storage-api.json)<br>[contracts.system_info·api·pass](evidence/F-API-014/2026-10-04-V2-7dbc4dc7-contracts.system_info-api.json) | — |
| F-API-015 | CEC command routes | V3 | V1 | V1 | stale | [cec_controls.input_command_port_0·api·pass](evidence/F-API-015/2026-10-04-V2-7dbc4dc7-cec_controls.input_command_port_0-api.json)<br>[cec_controls.input_command_port_9·api·pass](evidence/F-API-015/2026-10-04-V2-7dbc4dc7-cec_controls.input_command_port_9-api.json) | — |
| F-API-016 | CEC catalogue, capability and enable routes | V2 | V1 | V1 | stale | [writes.cec_output_enable·api·fail](evidence/F-API-016/2026-10-01-V2-72cc71dc-writes.cec_output_enable-api.json)<br>[contracts.cec_input_catalog·api·pass](evidence/F-API-016/2026-10-04-V2-7dbc4dc7-contracts.cec_input_catalog-api.json) | — |
| F-API-017 | Device settings routes (icons, display names, preset names, favourite/dashboard presets) | V2 | V1 | V1 | stale | [contracts.device_settings·api·pass](evidence/F-API-017/2026-10-04-V2-7dbc4dc7-contracts.device_settings-api.json)<br>[contracts.input_settings·api·pass](evidence/F-API-017/2026-10-04-V2-7dbc4dc7-contracts.input_settings-api.json) | — |
| F-API-018 | Name routes (POST /api/input\|output/{n}/name) | V2 | V0 | V0 | stale | [writes.output_name·api·pass](evidence/F-API-018/2026-10-04-V2-7dbc4dc7-writes.output_name-api.json) | BE-16(M) |
| F-API-019 | Profile routes | V2 | V1 | V1 | stale | [writes.profile_cec·api·pass](evidence/F-API-019/2026-10-04-V2-7dbc4dc7-writes.profile_cec-api.json)<br>[writes.profile_macros·api·pass](evidence/F-API-019/2026-10-04-V2-7dbc4dc7-writes.profile_macros-api.json) | — |
| F-API-020 | Scene v1 alias routes (/api/scene*, /api/scenes) | V2 | V1 | V1 | stale | [profile_state.alias_create·api·pass](evidence/F-DOM-001/2026-10-04-V2-7dbc4dc7-profile_state.alias_create-api.json)<br>[profile_state.alias_create_invalid·api·pass](evidence/F-DOM-001/2026-10-04-V2-7dbc4dc7-profile_state.alias_create_invalid-api.json) | API-12(M) |
| F-API-021 | Scene v2 routes (/api/v2/scenes*) | V2 | **V2** | V2 | stale | [domain_manage.scene_a_list·api·pass](evidence/F-DOM-010/2026-10-04-V2-7dbc4dc7-domain_manage.scene_a_list-api.json)<br>[domain_manage.scene_b_create_reject_body_type·api·pass](evidence/F-DOM-010/2026-10-04-V2-7dbc4dc7-domain_manage.scene_b_create_reject_body_type-api.json) | TST-03(M) |
| F-API-022 | Response envelope and input validation (4xx before anything reaches the matrix) | V2 | V1 | V1 | stale | [failures.bad_input·api·pass](evidence/F-API-022/2026-10-04-V2-7dbc4dc7-failures.bad_input-api.json) | API-21(L) |
| F-API-023 | Macro routes | V2 | V1 | V1 | stale | [domain_manage.macro_update_description_long·api·fail](evidence/F-DOM-019/2026-10-02-V2-1aafbbf4-domain_manage.macro_update_description_long-api.json)<br>[domain_manage.macro_all_commands·api·pass](evidence/F-DOM-019/2026-10-04-V2-7dbc4dc7-domain_manage.macro_all_commands-api.json) | — |
| F-API-024 | Shortcut routes (/api/system-shortcuts* and the /api/shortcuts* aliases) | V2 | V1 | V1 | stale | [contracts.shortcut_alias·api·pass](evidence/F-API-024/2026-10-04-V2-7dbc4dc7-contracts.shortcut_alias-api.json)<br>[contracts.shortcut_dashboard·api·pass](evidence/F-API-024/2026-10-04-V2-7dbc4dc7-contracts.shortcut_dashboard-api.json) | — |
| F-API-025 | Dashboard layout routes | V2 | V1 | V1 | stale | [dashboard.widget_card_refused·api·pass](evidence/F-DOM-031/2026-10-10-V2-b3aced1b-dashboard.widget_card_refused-api.json)<br>[dashboard.widget_cards_dropped·api·pass](evidence/F-DOM-031/2026-10-10-V2-b3aced1b-dashboard.widget_cards_dropped-api.json) | API-20(M) |
| F-API-026 | Themes and UI preference routes | V2 | V1 | V1 | stale | [contracts.themes·api·pass](evidence/F-API-026/2026-10-04-V2-7dbc4dc7-contracts.themes-api.json)<br>[contracts.ui_preferences·api·pass](evidence/F-API-026/2026-10-04-V2-7dbc4dc7-contracts.ui_preferences-api.json) | — |
| F-API-027 | Settings routes (matrix host, test connection) | V2 | V1 | V1 | stale | [contracts.settings·api·pass](evidence/F-API-027/2026-10-04-V2-7dbc4dc7-contracts.settings-api.json)<br>[writes.connection_test·api·pass](evidence/F-API-027/2026-10-04-V2-7dbc4dc7-writes.connection_test-api.json) | TST-03(M) |
| F-API-028 | Flic integration routes | V2 | V0 | V0 | stale | [contracts.flic_buttons·api·pass](evidence/F-API-028/2026-10-04-V2-7dbc4dc7-contracts.flic_buttons-api.json)<br>[writes.flic_register·api·pass](evidence/F-API-028/2026-10-04-V2-7dbc4dc7-writes.flic_register-api.json) | TST-03(M) |
| F-API-029 | Web UI, kiosk and static asset routes | V3 | **V3** | V3 | — | — | — |
| F-API-030 | Rate limiting (60 requests / 10 s per client) | V2 | V1 | V1 | — | — | — |
| F-API-031 | CORS headers | V2 | V1 | V1 | — | — | — |
| F-API-032 | WebSocket /ws: welcome, status snapshot, get_status, matrix link, errors | V2 | **V2** | V2 | stale | [reboot.direct·api·pass](evidence/F-MTX-021/2026-10-04-V2-d6baf3ca-reboot.direct-api.json)<br>[reboot.enabled_shortcut·api·pass](evidence/F-MTX-021/2026-10-04-V2-d6baf3ca-reboot.enabled_shortcut-api.json) | — |
| F-API-033 | WS event routing_change (one per changed output, whoever routed) / switch_failed | V3 | V2 | V2 | stale | [routing.switch_one·api·pass](evidence/F-MTX-001/2026-10-04-V2-d6baf3ca-routing.switch_one-api.json)<br>[failures.unreachable_switch·api·pass](evidence/F-REL-009/2026-10-04-V2-7dbc4dc7-failures.unreachable_switch-api.json) | — |
| F-API-034 | Route to all: routing_change per output that changed / switch_all_failed | V3 | V2 | V2 | stale | [routing.route_all·api·pass](evidence/F-MTX-002/2026-10-04-V2-d6baf3ca-routing.route_all-api.json) | — |
| F-API-035 | WS event preset_recall / preset_recall_failed | V3 | V2 | V2 | stale | [presets.recall·api·pass](evidence/F-MTX-003/2026-10-04-V2-d6baf3ca-presets.recall-api.json)<br>[presets.recall·api·pass](evidence/F-MTX-003/2026-10-10-V2-b6dbfaca-presets.recall-api.json) | — |
| F-API-036 | WS event audio_mute | V2 | **V2** | V2 | stale | [outputs.audio_mute·api·pass](evidence/F-MTX-007/2026-10-04-V2-7dbc4dc7-outputs.audio_mute-api.json)<br>[outputs.audio_mute_rejected·api·pass](evidence/F-REL-008/2026-10-04-V2-7dbc4dc7-outputs.audio_mute_rejected-api.json) | — |
| F-API-037 | WS events device_settings / device_settings_full | V2 | **V2** | V2 | stale | [presets.rename·api·pass](evidence/F-MTX-005/2026-10-04-V2-d6baf3ca-presets.rename-api.json) | — |
| F-API-038 | WS event cec_command | V2 | **V2** | V2 | stale | [cec.output_power_on·api·pass](evidence/F-CEC-005/2026-10-04-V2-7dbc4dc7-cec.output_power_on-api.json) | — |
| F-API-039 | WS status snapshot (after connect, after a first reading, get_status) | V2 | **V2** | V2 | — | — | — |
| F-API-040 | WS live matrix events from the hub's own poller (routing, power, signal, display, cable, mute, names) | V2 | **V2** | V2 | stale | [power.standby·api·pass](evidence/F-MTX-006/2026-10-04-V2-7dbc4dc7-power.standby-api.json)<br>[live.display_unplugged·browser·pass](evidence/F-MTX-031/2026-10-04-V3-d6baf3ca-live.display_unplugged-browser.json) | BE-24(L) |
| F-API-041 | WS event scene_execution_error | V2 | **V2** | V2 | stale | [scenes.partial_failure·api·pass](evidence/F-DOM-011/2026-10-01-V2-97d0d2af-scenes.partial_failure-api.json)<br>[scenes.partial_failure·api·pass](evidence/F-DOM-011/2026-10-10-V2-b3aced1b-scenes.partial_failure-api.json) | — |
| F-API-042 | WS heartbeat (ping / pong) | V2 | **V2** | V2 | — | — | — |

## Domain features (F-DOM)

| ID | Feature | Target | Level | Recorded | Freshness | Evidence | Open findings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-DOM-001 | Create, edit and delete profiles | V3 | V1 | V1 | stale | [profile_crud.post_scaler_arc·api·fail](evidence/F-DOM-001/2026-10-02-V2-0b9cbe87-profile_crud.post_scaler_arc-api.json)<br>[profile_crud.put_scaler_arc·api·fail](evidence/F-DOM-001/2026-10-02-V2-0b9cbe87-profile_crud.put_scaler_arc-api.json) | — |
| F-DOM-002 | Recall a profile: its routing is applied | V4 | V3 | V3 | stale | [profiles.recall_disabled_output·api·pass](evidence/F-DOM-002/2026-10-01-V2-97d0d2af-profiles.recall_disabled_output-api.json)<br>[profiles.recall_rejected·api·pass](evidence/F-DOM-002/2026-10-01-V2-97d0d2af-profiles.recall_rejected-api.json) | API-19(M) |
| F-DOM-003 | Recall a profile: its output settings (mute, HDR, HDCP, enable) are applied | V4 | V3 | V3 | stale | [profiles.recall_disabled_output·api·pass](evidence/F-DOM-002/2026-10-01-V2-97d0d2af-profiles.recall_disabled_output-api.json)<br>[profiles.recall_disabled_output·browser·pass](evidence/F-DOM-002/2026-10-01-V3-97d0d2af-profiles.recall_disabled_output-browser.json) | — |
| F-DOM-004 | Recall a profile: its power-on macro runs | V4 | V3 | V3 | stale | [profiles.recall_power_macro·api·fail](evidence/F-DOM-004/2026-09-25-V2-22afc1a7-profiles.recall_power_macro-api.json)<br>[profiles.recall_power_macro·api·pass](evidence/F-DOM-004/2026-10-01-V2-97d0d2af-profiles.recall_power_macro-api.json) | — |
| F-DOM-005 | Protect a profile with a passcode (per-item PIN) | V3 | V1 | V1 | stale | [profiles.recall_needs_passcode·api·pass](evidence/F-DOM-005/2026-10-10-V2-b3aced1b-profiles.recall_needs_passcode-api.json)<br>[profiles.recall_with_passcode·api·pass](evidence/F-DOM-005/2026-10-10-V2-b3aced1b-profiles.recall_with_passcode-api.json) | — |
| F-DOM-006 | Favourite, pin, reorder profiles and show them on the dashboard | V3 | V1 | V1 | stale | [profile_crud.dashboard_missing_field·api·pass](evidence/F-DOM-006/2026-10-04-V2-7dbc4dc7-profile_crud.dashboard_missing_field-api.json)<br>[profile_crud.dashboard_post_false·api·pass](evidence/F-DOM-006/2026-10-04-V2-7dbc4dc7-profile_crud.dashboard_post_false-api.json) | API-20(M) |
| F-DOM-007 | Per-profile CEC targets (nav/playback/volume/power) and auto-resolve | V3 | V1 | V1 | stale | [profile_state.cec_profile_get_default·api·pass](evidence/F-DOM-007/2026-10-04-V2-7dbc4dc7-profile_state.cec_profile_get_default-api.json)<br>[profile_state.cec_profile_get_missing·api·pass](evidence/F-DOM-007/2026-10-04-V2-7dbc4dc7-profile_state.cec_profile_get_missing-api.json) | — |
| F-DOM-008 | Profile execution log | V3 | V0 | V0 | stale | [profile_state.history_empty·api·pass](evidence/F-DOM-008/2026-10-04-V2-7dbc4dc7-profile_state.history_empty-api.json)<br>[profile_state.history_failure·api·pass](evidence/F-DOM-008/2026-10-04-V2-7dbc4dc7-profile_state.history_failure-api.json) | — |
| F-DOM-009 | Save the current routing as a new profile | V3 | V1 | V1 | stale | [profile_state.capture_output_read_failure·api·fail](evidence/F-DOM-009/2026-10-02-V2-ed4cb0fb-profile_state.capture_output_read_failure-api.json)<br>[profile_state.capture_video_read_failure·api·fail](evidence/F-DOM-009/2026-10-02-V2-ed4cb0fb-profile_state.capture_video_read_failure-api.json) | API-12(M) |
| F-DOM-010 | Create, edit and delete scenes (sequences of steps) | V3 | V2 | V2 | stale | [domain_manage.scene_a_list·api·pass](evidence/F-DOM-010/2026-10-04-V2-7dbc4dc7-domain_manage.scene_a_list-api.json)<br>[domain_manage.scene_b_create_reject_body_type·api·pass](evidence/F-DOM-010/2026-10-04-V2-7dbc4dc7-domain_manage.scene_b_create_reject_body_type-api.json) | API-12(M) |
| F-DOM-011 | Run a scene: profile steps | V4 | V3 | V3 | stale | [scenes.disabled_output_state·api·pass](evidence/F-DOM-011/2026-10-01-V2-97d0d2af-scenes.disabled_output_state-api.json)<br>[scenes.partial_failure·api·pass](evidence/F-DOM-011/2026-10-01-V2-97d0d2af-scenes.partial_failure-api.json) | — |
| F-DOM-012 | Run a scene: macro steps | V4 | V3 | V3 | stale | [scenes.run_profile_macro_preset·api·pass](evidence/F-DOM-011/2026-10-01-V2-97d0d2af-scenes.run_profile_macro_preset-api.json)<br>[scenes.run_profile_macro_preset·browser·pass](evidence/F-DOM-011/2026-10-01-V3-97d0d2af-scenes.run_profile_macro_preset-browser.json) | — |
| F-DOM-013 | Run a scene: wait and shortcut steps | V3 | **V3** | V3 | stale | [scenes.wait_between_actions·api·pass](evidence/F-DOM-013/2026-10-01-V2-97d0d2af-scenes.wait_between_actions-api.json)<br>[scenes.wait_edit·api·pass](evidence/F-DOM-013/2026-10-01-V2-97d0d2af-scenes.wait_edit-api.json) | — |
| F-DOM-014 | Scene overrides (per-run changes to a profile step) | V3 | **V3** | V3 | stale | [scenes.run_profile_macro_preset·api·pass](evidence/F-DOM-011/2026-10-01-V2-97d0d2af-scenes.run_profile_macro_preset-api.json)<br>[scenes.run_profile_macro_preset·browser·pass](evidence/F-DOM-011/2026-10-01-V3-97d0d2af-scenes.run_profile_macro_preset-browser.json) | — |
| F-DOM-015 | Protect a scene with a passcode | V3 | V1 | V1 | stale | [scenes.run_protected·api·pass](evidence/F-DOM-011/2026-10-01-V2-97d0d2af-scenes.run_protected-api.json)<br>[scenes.run_protected·browser·pass](evidence/F-DOM-011/2026-10-01-V3-97d0d2af-scenes.run_protected-browser.json) | — |
| F-DOM-016 | Validate a scene and detect conflicting steps | V3 | **V3** | V3 | stale | [scenes.conflicts_visible·api·pass](evidence/F-DOM-016/2026-10-01-V2-97d0d2af-scenes.conflicts_visible-api.json)<br>[scenes.conflicts_visible·browser·pass](evidence/F-DOM-016/2026-10-01-V3-97d0d2af-scenes.conflicts_visible-browser.json) | — |
| F-DOM-017 | Scene execution history | V3 | **V3** | V3 | stale | [scenes.partial_failure·api·pass](evidence/F-DOM-011/2026-10-01-V2-97d0d2af-scenes.partial_failure-api.json)<br>[scenes.partial_failure·browser·pass](evidence/F-DOM-011/2026-10-01-V3-97d0d2af-scenes.partial_failure-browser.json) | — |
| F-DOM-018 | Legacy 'scenes' (v1) as aliases of profiles | V2 | V1 | V1 | stale | [domain_manage.legacy_list·api·pass](evidence/F-DOM-018/2026-10-04-V2-7dbc4dc7-domain_manage.legacy_list-api.json)<br>[domain_manage.legacy_recall·api·pass](evidence/F-DOM-018/2026-10-04-V2-7dbc4dc7-domain_manage.legacy_recall-api.json) | API-12(M) |
| F-DOM-019 | Create, edit, delete and validate CEC macros | V3 | V1 | V1 | stale | [domain_manage.macro_update_description_long·api·fail](evidence/F-DOM-019/2026-10-02-V2-1aafbbf4-domain_manage.macro_update_description_long-api.json)<br>[domain_manage.macro_all_commands·api·pass](evidence/F-DOM-019/2026-10-04-V2-7dbc4dc7-domain_manage.macro_all_commands-api.json) | — |
| F-DOM-020 | Run a CEC macro (steps, targets, delays) | V4 | V3 | V3 | stale | [scenes.macro_continues_after_refusal·api·pass](evidence/F-DOM-012/2026-10-01-V2-97d0d2af-scenes.macro_continues_after_refusal-api.json)<br>[scenes.macro_continues_after_refusal·browser·pass](evidence/F-DOM-012/2026-10-01-V3-97d0d2af-scenes.macro_continues_after_refusal-browser.json) | — |
| F-DOM-021 | Test / dry-run a macro | V3 | V1 | V1 | stale | [domain_manage.macro_dry_run·api·pass](evidence/F-DOM-021/2026-10-04-V2-7dbc4dc7-domain_manage.macro_dry_run-api.json)<br>[domain_manage.macro_dry_run_missing·api·pass](evidence/F-DOM-021/2026-10-04-V2-7dbc4dc7-domain_manage.macro_dry_run_missing-api.json) | — |
| F-DOM-022 | Favourite macros and show them on the dashboard | V3 | V1 | V1 | stale | [domain_manage.macro_dashboard_false·api·pass](evidence/F-DOM-022/2026-10-04-V2-7dbc4dc7-domain_manage.macro_dashboard_false-api.json)<br>[domain_manage.macro_dashboard_missing·api·pass](evidence/F-DOM-022/2026-10-04-V2-7dbc4dc7-domain_manage.macro_dashboard_missing-api.json) | API-20(M) |
| F-DOM-023 | Built-in shortcuts: route all to an output, one-to-one routing | V3 | V2 | V2 | stale | [shortcuts.route_one_to_one·browser·pass](evidence/F-DOM-023/2026-10-01-V3-9362fd00-shortcuts.route_one_to_one-browser.json)<br>[shortcuts.route_input_to_output·api·pass](evidence/F-DOM-023/2026-10-04-V2-d6baf3ca-shortcuts.route_input_to_output-api.json) | — |
| F-DOM-024 | Built-in shortcut: power everything off | V3 | V2 | V2 | stale | [shortcuts.power_off_all·browser·pass](evidence/F-DOM-024/2026-10-01-V3-9362fd00-shortcuts.power_off_all-browser.json)<br>[shortcuts.power_off_all·api·pass](evidence/F-DOM-024/2026-10-04-V2-d6baf3ca-shortcuts.power_off_all-api.json) | — |
| F-DOM-025 | Built-in shortcuts: mute / unmute all outputs | V3 | V2 | V2 | stale | [shortcuts.mute_all·browser·pass](evidence/F-DOM-025/2026-10-01-V3-9362fd00-shortcuts.mute_all-browser.json)<br>[shortcuts.mute_rejected·browser·pass](evidence/F-DOM-025/2026-10-01-V3-9362fd00-shortcuts.mute_rejected-browser.json) | — |
| F-DOM-026 | Built-in shortcuts: recall preset 1-8 | V3 | V2 | V2 | stale | [shortcuts.preset_recall·browser·pass](evidence/F-DOM-026/2026-10-01-V3-9362fd00-shortcuts.preset_recall-browser.json)<br>[shortcuts.preset_recall·api·pass](evidence/F-DOM-026/2026-10-04-V2-d6baf3ca-shortcuts.preset_recall-api.json) | — |
| F-DOM-027 | Built-in shortcuts: beep, panel lock, reboot | V3 | V2 | V2 | stale | [shortcuts.beep_on·browser·pass](evidence/F-DOM-027/2026-10-01-V3-7aa17c95-shortcuts.beep_on-browser.json)<br>[shortcuts.disabled_reboot·browser·pass](evidence/F-DOM-027/2026-10-01-V3-7aa17c95-shortcuts.disabled_reboot-browser.json) | — |
| F-DOM-028 | Built-in shortcuts: LCD timeout | V3 | V2 | V2 | stale | [shortcuts.lcd_always_on·browser·pass](evidence/F-DOM-028/2026-10-01-V3-7aa17c95-shortcuts.lcd_always_on-browser.json)<br>[shortcuts.lcd_rejected·browser·pass](evidence/F-DOM-028/2026-10-01-V3-7aa17c95-shortcuts.lcd_rejected-browser.json) | API-07(M) |
| F-DOM-029 | Create, rename, reorder and delete user shortcuts | V3 | V1 | V1 | — | — | — |
| F-DOM-030 | Favourite shortcuts and show them on the dashboard | V3 | V1 | V1 | — | — | API-20(M) |
| F-DOM-031 | Dashboard layout (add, remove, reorder cards) | V3 | V1 | V1 | stale | [dashboard.widget_card_refused·api·pass](evidence/F-DOM-031/2026-10-10-V2-b3aced1b-dashboard.widget_card_refused-api.json)<br>[dashboard.widget_cards_dropped·api·pass](evidence/F-DOM-031/2026-10-10-V2-b3aced1b-dashboard.widget_cards_dropped-api.json) | API-20(M), UI-08(M) |
| F-DOM-032 | Input/output icons, colours and display names (device settings) | V3 | V0 | V0 | — | — | BE-16(M), UI-22(M) |
| F-DOM-033 | Favourite presets and choose which presets the dashboard shows | V3 | V1 | V1 | — | — | — |
| F-DOM-034 | Save a custom routing mapping into a preset | V3 | V1 | V1 | stale | [preset_read.saved_partial_1·api·pass](evidence/F-DOM-034/2026-10-04-V2-7dbc4dc7-preset_read.saved_partial_1-api.json)<br>[preset_read.saved_partial_2·api·pass](evidence/F-DOM-034/2026-10-04-V2-7dbc4dc7-preset_read.saved_partial_2-api.json) | — |
| F-DOM-035 | Theme presets and custom themes | V3 | V1 | V1 | — | — | — |
| F-DOM-036 | UI preferences stored on the hub | V3 | V1 | V1 | — | — | — |

## Web UI (F-UI)

| ID | Feature | Target | Level | Recorded | Freshness | Evidence | Open findings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-UI-001 | Open the web UI; the header shows the matrix connection | V3 | **V3** | V3 | — | — | — |
| F-UI-002 | Route by clicking a cell in the matrix grid | V3 | **V3** | V3 | stale | [routing.switch_one·browser·pass](evidence/F-MTX-001/2026-10-04-V3-d6baf3ca-routing.switch_one-browser.json) | — |
| F-UI-003 | Route from the matrix card view (routing sheet) | V3 | V1 | V1 | — | — | — |
| F-UI-004 | Route one input to every output from the Route To All drawer | V3 | V1 | V1 | stale | [routing.route_all·browser·pass](evidence/F-MTX-002/2026-10-04-V3-d6baf3ca-routing.route_all-browser.json) | — |
| F-UI-005 | Recall a preset from the Presets drawer | V3 | V1 | V1 | stale | [presets.recall·browser·pass](evidence/F-MTX-003/2026-10-04-V3-d6baf3ca-presets.recall-browser.json)<br>[presets.recall·browser·pass](evidence/F-MTX-003/2026-10-10-V3-b6dbfaca-presets.recall-browser.json) | — |
| F-UI-006 | Rename a preset in the Presets drawer | V3 | V1 | V1 | stale | [presets.rename·browser·pass](evidence/F-MTX-005/2026-10-04-V3-d6baf3ca-presets.rename-browser.json) | — |
| F-UI-007 | Overwrite a preset / save a custom mapping from the Presets drawer | V3 | V1 | V1 | — | — | — |
| F-UI-008 | Run profiles, scenes, presets, shortcuts and macros from dashboard cards | V3 | **V3** | V3 | stale | [scenes.run_protected·browser·pass](evidence/F-DOM-011/2026-10-01-V3-97d0d2af-scenes.run_protected-browser.json)<br>[scenes.run_protected·browser·pass](evidence/F-DOM-011/2026-10-10-V3-b3aced1b-scenes.run_protected-browser.json) | — |
| F-UI-009 | Customise the dashboard (card picker, pin, reorder) | V3 | V1 | V1 | — | — | UI-08(M), API-20(M) |
| F-UI-010 | Inputs tab: signal/cable status and input settings (name, icon, EDID) | V3 | V1 | V1 | — | — | — |
| F-UI-011 | Outputs tab: display status and output settings (HDCP, HDR, scaler, ARC, mute) | V3 | V1 | V1 | — | — | — |
| F-UI-012 | Profiles tab and profile manager | V3 | **V3** | V3 | stale | [profiles.recall_routing·browser·pass](evidence/F-DOM-002/2026-10-01-V3-97d0d2af-profiles.recall_routing-browser.json)<br>[profiles.recall_routing·browser·pass](evidence/F-DOM-002/2026-10-10-V3-b3aced1b-profiles.recall_routing-browser.json) | — |
| F-UI-013 | Create and edit a profile in the profile editor | V3 | V1 | V1 | — | — | — |
| F-UI-014 | Run a passcode-protected profile (passcode prompt) | V3 | **V3** | V3 | stale | [profiles.recall_needs_passcode·browser·pass](evidence/F-DOM-005/2026-10-10-V3-b3aced1b-profiles.recall_needs_passcode-browser.json)<br>[profiles.recall_with_passcode·browser·pass](evidence/F-DOM-005/2026-10-10-V3-b3aced1b-profiles.recall_with_passcode-browser.json) | UI-36(L) |
| F-UI-015 | Build a scene in the scene editor | V3 | **V3** | V3 | — | — | UI-19(L) |
| F-UI-016 | Build a CEC macro in the macro editor | V3 | V1 | V1 | — | — | — |
| F-UI-017 | CEC remote on output/input tiles and the CEC tray | V3 | V1 | V1 | — | — | UI-12(M) |
| F-UI-018 | Theme presets, customisation and card opacity | V3 | V1 | V1 | — | — | — |
| F-UI-019 | General settings: matrix host and connection test | V3 | V1 | V1 | — | — | UI-05(M) |
| F-UI-020 | Hardware settings: beep, panel lock, LCD, reboot | V3 | V1 | V1 | — | — | UI-05(M) |
| F-UI-021 | Interface settings | V3 | V1 | V1 | — | — | UI-05(M) |
| F-UI-022 | Shortcuts drawer: run, rename, reorder | V3 | V1 | V1 | — | — | — |
| F-UI-023 | Integrations drawer (Flic request builder, HA YAML, Remote 3 info) | V3 | V1 | V1 | — | — | — |
| F-UI-024 | Live updates when another client or the matrix changes something | V3 | **V3** | V3 | stale | [live.display_unplugged·browser·pass](evidence/F-MTX-031/2026-10-04-V3-d6baf3ca-live.display_unplugged-browser.json)<br>[live.front_panel_route·browser·pass](evidence/F-MTX-031/2026-10-04-V3-d6baf3ca-live.front_panel_route-browser.json) | — |
| F-UI-025 | Reconnect and resync after the WebSocket drops | V3 | **V3** | V3 | — | — | — |
| F-UI-026 | Show an error state when the matrix is unreachable | V3 | **V3** | V3 | — | — | — |
| F-UI-027 | Toasts and confirmation dialogs | V3 | **V3** | V3 | stale | [scenes.partial_failure·browser·pass](evidence/F-DOM-011/2026-10-01-V3-97d0d2af-scenes.partial_failure-browser.json)<br>[scenes.partial_failure·browser·pass](evidence/F-DOM-011/2026-10-10-V3-b3aced1b-scenes.partial_failure-browser.json) | — |
| F-UI-028 | Keyboard shortcuts | V3 | V1 | V1 | — | — | UI-06(M) |
| F-UI-029 | Accessibility (keyboard, focus, ARIA, contrast, zoom) | V3 | V1 | V1 | — | — | UI-07(M), UI-35(M) |
| F-UI-030 | Debug panel | V3 | V1 | V1 | — | — | — |
| F-UI-031 | About dialog | V3 | **V3** | V3 | — | — | — |
| F-UI-032 | Animated Tron background (opt-in) | V3 | V1 | V1 | — | — | UI-16(L) |
| F-UI-033 | Tablet and phone layouts | V3 | V1 | V1 | — | — | UI-33(L) |
| F-UI-034 | Personalise tabs in the Control Deck (pin, reorder) | V3 | V1 | V1 | — | — | — |
| F-UI-035 | Copy an API endpoint for automation (API button / modal) | V3 | V1 | V1 | — | — | UI-18(L) |
| F-UI-036 | First-run setup wizard (matrix connection) | V3 | V1 | V1 | — | — | UI-09(M) |

## Kiosk (F-KIO)

| ID | Feature | Target | Level | Recorded | Freshness | Evidence | Open findings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-KIO-001 | Open the kiosk; it shows the matrix connection | V3 | **V3** | V3 | — | — | — |
| F-KIO-002 | Route a source to one display with the routing wizard | V3 | **V3** | V3 | stale | [kiosk.route_one_muted·browser·pass](evidence/F-KIO-002/2026-10-04-V3-7dbc4dc7-kiosk.route_one_muted-browser.json) | — |
| F-KIO-003 | Route a source to every display from the kiosk | V3 | **V3** | V3 | stale | [kiosk.route_all_apply·browser·pass](evidence/F-KIO-003/2026-10-04-V3-7dbc4dc7-kiosk.route_all_apply-browser.json) | — |
| F-KIO-004 | Input and output status tiles | V3 | **V3** | V3 | — | — | — |
| F-KIO-005 | Recall a preset from the kiosk | V3 | V1 | V1 | — | — | — |
| F-KIO-006 | Configure which presets the kiosk shows (edit mode) | V3 | V1 | V1 | — | — | UI-08(M) |
| F-KIO-007 | Run shortcuts from the kiosk and map them to slots | V3 | V1 | V1 | — | — | — |
| F-KIO-008 | Run profiles from the kiosk; create one with the profile wizard | V3 | V1 | V1 | stale | [kiosk.profile_with_passcode·browser·pass](evidence/F-KIO-008/2026-10-01-V3-97d0d2af-kiosk.profile_with_passcode-browser.json)<br>[kiosk.profile_wrong_passcode·browser·pass](evidence/F-KIO-008/2026-10-01-V3-97d0d2af-kiosk.profile_wrong_passcode-browser.json) | — |
| F-KIO-009 | CEC remote in the kiosk | V3 | V1 | V1 | — | — | — |
| F-KIO-010 | Kiosk live updates | V3 | **V3** | V3 | stale | [live.front_panel_route·browser·pass](evidence/F-MTX-031/2026-10-04-V3-d6baf3ca-live.front_panel_route-browser.json)<br>[live.input_signal·browser·pass](evidence/F-MTX-031/2026-10-04-V3-d6baf3ca-live.input_signal-browser.json) | — |
| F-KIO-011 | Kiosk disconnected state | V3 | **V3** | V3 | stale | [live.matrix_offline·browser·pass](evidence/F-REL-009/2026-10-04-V3-d6baf3ca-live.matrix_offline-browser.json) | — |
| F-KIO-012 | Kiosk layout and pins persist | V3 | V1 | V1 | — | — | UI-08(M) |
| F-KIO-013 | Kiosk follows the selected theme | V3 | V1 | V1 | — | — | UI-34(L) |
| F-KIO-014 | Kiosk touch accessibility (targets, ARIA, contrast) | V3 | V1 | V1 | — | — | UI-07(M), UI-35(M) |

## Remote 3 integration (F-UC)

| ID | Feature | Target | Level | Recorded | Freshness | Evidence | Open findings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-UC-001 | Discover the integration and register the driver (mDNS, driver URL) | V4 | V0 | V0 | — | — | UC-11(M) |
| F-UC-002 | Set up the integration on the Remote | V4 | V1 | V1 | — | — | — |
| F-UC-003 | Reconfigure the integration (new matrix address) | V4 | V3 | V3 | — | — | — |
| F-UC-004 | Preset buttons on the Remote | V4 | V3 | V3 | stale | [remote.preset_button·uc·pass](evidence/F-UC-004/2026-10-04-V3-7dbc4dc7-remote.preset_button-uc.json)<br>[remote.preset_names_from_web_app·uc·pass](evidence/F-UC-004/2026-10-04-V3-7dbc4dc7-remote.preset_names_from_web_app-uc.json) | UC-28(M) |
| F-UC-005 | Matrix remote entity with a preset page | V4 | V3 | V3 | stale | [remote.preset_names_from_web_app·uc·pass](evidence/F-UC-004/2026-10-04-V3-7dbc4dc7-remote.preset_names_from_web_app-uc.json)<br>[remote.matrix_preset_command·uc·pass](evidence/F-UC-005/2026-10-04-V3-7dbc4dc7-remote.matrix_preset_command-uc.json) | UC-12(L) |
| F-UC-006 | Per-input CEC remotes (source power, navigation, playback) | V4 | V3 | V3 | stale | [remote.input_cec_command·uc·pass](evidence/F-UC-006/2026-10-04-V3-7dbc4dc7-remote.input_cec_command-uc.json)<br>[remote.input_cec_off·uc·pass](evidence/F-UC-006/2026-10-04-V3-7dbc4dc7-remote.input_cec_off-uc.json) | UC-12(L) |
| F-UC-007 | Per-output CEC remotes (TV power, volume) | V4 | V3 | V3 | stale | [remote.cec_bad_sequence·uc·pass](evidence/F-UC-007/2026-10-04-V3-7dbc4dc7-remote.cec_bad_sequence-uc.json)<br>[remote.output_cec_on·uc·pass](evidence/F-UC-007/2026-10-04-V3-7dbc4dc7-remote.output_cec_on-uc.json) | BE-14(M) |
| F-UC-008 | Choose an output's source from the Remote (media player source list) | V4 | V3 | V3 | stale | [remote.select_source·uc·pass](evidence/F-UC-008/2026-10-04-V3-7dbc4dc7-remote.select_source-uc.json)<br>[remote.unknown_source·uc·pass](evidence/F-UC-008/2026-10-04-V3-7dbc4dc7-remote.unknown_source-uc.json) | UC-10(M) |
| F-UC-009 | TV power / volume / mute from the output media player | V4 | V3 | V3 | stale | [remote.media_player_toggle·uc·pass](evidence/F-UC-009/2026-10-04-V3-7dbc4dc7-remote.media_player_toggle-uc.json)<br>[remote.media_player_volume·uc·pass](evidence/F-UC-009/2026-10-04-V3-7dbc4dc7-remote.media_player_volume-uc.json) | UC-10(M), BE-24(L) |
| F-UC-010 | Matrix power switch on the Remote | V4 | V3 | V3 | stale | [remote.power_switch_follows_front_panel·uc·pass](evidence/F-UC-010/2026-10-04-V3-7dbc4dc7-remote.power_switch_follows_front_panel-uc.json)<br>[remote.power_switch_off·uc·pass](evidence/F-UC-010/2026-10-04-V3-7dbc4dc7-remote.power_switch_off-uc.json) | — |
| F-UC-011 | Input signal and cable sensors | V4 | V1 | V1 | — | — | UC-13(L) |
| F-UC-012 | Output connected, cable and source sensors | V4 | V3 | V3 | — | — | UC-13(L) |
| F-UC-013 | Entities go unavailable while the matrix is unreachable | V4 | V3 | V3 | — | — | — |
| F-UC-014 | Remote standby and wake | V4 | V3 | V3 | — | — | — |
| F-UC-015 | Only changed attributes are sent to the Remote | V4 | V3 | V3 | — | — | — |
| F-UC-016 | Renamed inputs/outputs show up on the Remote | V4 | V3 | V3 | stale | [remote.input_rename_live·uc·pass](evidence/F-UC-016/2026-10-04-V3-7dbc4dc7-remote.input_rename_live-uc.json) | UC-28(M), BE-16(M) |
| F-UC-017 | Restore the configuration at startup (also with the matrix offline) | V4 | V3 | V3 | — | — | — |

## Home Assistant component (F-HA)

| ID | Feature | Target | Level | Recorded | Freshness | Evidence | Open findings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-HA-001 | Add the hub in Home Assistant (config flow) | V4 | V3 | V3 | stale | [ha.config_flow·ha·pass](evidence/F-HA-001/2026-10-04-V3-7dbc4dc7-ha.config_flow-ha.json) | — |
| F-HA-002 | Choose each output's source (select entities) | V4 | V3 | V3 | stale | [ha.front_panel_route·ha·pass](evidence/F-HA-002/2026-10-04-V3-7dbc4dc7-ha.front_panel_route-ha.json)<br>[ha.select_source·ha·pass](evidence/F-HA-002/2026-10-04-V3-7dbc4dc7-ha.select_source-ha.json) | — |
| F-HA-003 | Matrix power switch | V4 | V3 | V3 | stale | [ha.power_off·ha·pass](evidence/F-HA-003/2026-10-04-V3-7dbc4dc7-ha.power_off-ha.json)<br>[ha.power_on·ha·pass](evidence/F-HA-003/2026-10-04-V3-7dbc4dc7-ha.power_on-ha.json) | — |
| F-HA-004 | Output audio mute switches | V4 | V3 | V3 | stale | [ha.mute_switch·ha·pass](evidence/F-HA-004/2026-10-04-V3-7dbc4dc7-ha.mute_switch-ha.json) | — |
| F-HA-005 | Output stream enable switches | V4 | V3 | V3 | stale | [ha.stream_switch·ha·pass](evidence/F-HA-005/2026-10-04-V3-7dbc4dc7-ha.stream_switch-ha.json) | — |
| F-HA-006 | Preset buttons | V4 | V3 | V3 | stale | [ha.preset_button·ha·pass](evidence/F-HA-006/2026-10-04-V3-7dbc4dc7-ha.preset_button-ha.json) | — |
| F-HA-007 | Reboot button | V4 | V3 | V3 | stale | [ha.reboot_button·ha·pass](evidence/F-HA-007/2026-10-04-V3-7dbc4dc7-ha.reboot_button-ha.json) | — |
| F-HA-008 | Input signal binary sensors | V4 | V3 | V3 | stale | [ha.input_signal·ha·pass](evidence/F-HA-008/2026-10-04-V3-7dbc4dc7-ha.input_signal-ha.json) | — |
| F-HA-009 | Output connected binary sensors | V4 | V3 | V3 | stale | [ha.display_unplugged·ha·pass](evidence/F-HA-009/2026-10-04-V3-7dbc4dc7-ha.display_unplugged-ha.json) | — |
| F-HA-010 | Service hdmi_matrix.recall_preset | V4 | V3 | V3 | stale | [ha.service_recall_preset·ha·pass](evidence/F-HA-010/2026-10-04-V3-7dbc4dc7-ha.service_recall_preset-ha.json) | — |
| F-HA-011 | Service hdmi_matrix.switch_input | V4 | V3 | V3 | stale | [ha.service_switch_input·ha·pass](evidence/F-HA-011/2026-10-04-V3-7dbc4dc7-ha.service_switch_input-ha.json) | — |
| F-HA-012 | Service hdmi_matrix.send_cec_command | V4 | V3 | V3 | stale | [ha.service_cec_display·ha·pass](evidence/F-HA-012/2026-10-04-V3-7dbc4dc7-ha.service_cec_display-ha.json)<br>[ha.service_cec_invalid·ha·pass](evidence/F-HA-012/2026-10-04-V3-7dbc4dc7-ha.service_cec_invalid-ha.json) | — |
| F-HA-013 | Poll the hub; entities go unavailable when it is unreachable | V4 | V3 | V3 | stale | [ha.front_panel_route·ha·pass](evidence/F-HA-002/2026-10-04-V3-7dbc4dc7-ha.front_panel_route-ha.json)<br>[ha.input_signal·ha·pass](evidence/F-HA-008/2026-10-04-V3-7dbc4dc7-ha.input_signal-ha.json) | — |
| F-HA-014 | Install through HACS (custom repository) | V4 | V1 | V1 | — | — | — |
| F-HA-015 | Device and entity naming in Home Assistant | V4 | V3 | V3 | stale | [ha.config_flow·ha·pass](evidence/F-HA-001/2026-10-04-V3-7dbc4dc7-ha.config_flow-ha.json) | — |
| F-HA-016 | Change the hub address of a configured matrix (reconfigure flow) | V4 | V3 | V3 | stale | [ha.reconfigure·ha·pass](evidence/F-HA-016/2026-10-04-V3-7dbc4dc7-ha.reconfigure-ha.json) | — |
| F-HA-017 | Polling interval option (options flow) | V4 | V3 | V3 | stale | [ha.config_flow·ha·pass](evidence/F-HA-001/2026-10-04-V3-7dbc4dc7-ha.config_flow-ha.json) | — |
| F-HA-018 | Services target one matrix (config entry or device) | V4 | V3 | V3 | stale | [ha.service_recall_preset·ha·pass](evidence/F-HA-010/2026-10-04-V3-7dbc4dc7-ha.service_recall_preset-ha.json)<br>[ha.service_switch_input·ha·pass](evidence/F-HA-011/2026-10-04-V3-7dbc4dc7-ha.service_switch_input-ha.json) | — |

## Flic (F-FLIC)

| ID | Feature | Target | Level | Recorded | Freshness | Evidence | Open findings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-FLIC-001 | Button click recalls a preset | V3 | V1 | V1 | — | — | — |
| F-FLIC-002 | Button hold powers the matrix off / on | V3 | V1 | V1 | — | — | — |
| F-FLIC-003 | Button powers a source on over CEC | V3 | V1 | V1 | — | — | — |
| F-FLIC-004 | Flic Twist cycles an output through its inputs | V3 | V1 | V1 | — | — | — |
| F-FLIC-005 | Flic Twist controls TV volume and mute over CEC | V3 | V1 | V1 | — | — | BE-14(M) |
| F-FLIC-006 | Button recalls a profile or runs a macro | V3 | V1 | V1 | — | — | — |
| F-FLIC-007 | Register Flic buttons with the hub (button registry) | V3 | V0 | V0 | — | — | — |
| F-FLIC-008 | Button switches every output to input N (POST /api/input/{n}) | V3 | V0 | V0 | — | — | DOC-03(—) |
| F-FLIC-009 | Flic Hub SDK JavaScript module templates | V3 | V0 | V0 | — | — | — |
| F-FLIC-010 | Generate Flic request URLs in the web UI | V3 | V1 | V1 | — | — | — |

## Deployment, configuration, persistence (F-OPS)

| ID | Feature | Target | Level | Recorded | Freshness | Evidence | Open findings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-OPS-001 | Run the hub from the Docker image | V4 | V3 | V3 | stale | [deploy.image_core·api·pass](evidence/F-OPS-001/2026-10-03-V3-b30436af-deploy.image_core-api.json)<br>[deploy.image_uc·uc·pass](evidence/F-OPS-001/2026-10-03-V3-b30436af-deploy.image_uc-uc.json) | — |
| F-OPS-002 | Run the hub without the Remote integration (UC_ENABLED=false, the default) | V4 | V3 | V3 | stale | [deploy.image_core·api·pass](evidence/F-OPS-001/2026-10-03-V3-b30436af-deploy.image_core-api.json) | — |
| F-OPS-003 | docker compose quick start | V4 | V3 | V3 | stale | [deploy.compose·api·pass](evidence/F-OPS-003/2026-10-03-V3-b30436af-deploy.compose-api.json) | — |
| F-OPS-004 | Remote 3 discovery works from Docker | V4 | V2 | V2 | — | — | UC-11(M) |
| F-OPS-005 | Container health check and auto-restart | V4 | V3 | V3 | stale | [deploy.image_core·api·pass](evidence/F-OPS-001/2026-10-03-V3-b30436af-deploy.image_core-api.json)<br>[deploy.image_uc·uc·pass](evidence/F-OPS-001/2026-10-03-V3-b30436af-deploy.image_uc-uc.json) | — |
| F-OPS-006 | Point the hub at the matrix (MATRIX_HOST / MATRIX_PORT) | V4 | V3 | V3 | stale | [deploy.image_core·api·pass](evidence/F-OPS-001/2026-10-03-V3-b30436af-deploy.image_core-api.json) | DEP-07(M), BE-26(L) |
| F-OPS-007 | Choose the API port (API_PORT) | V4 | V2 | V2 | — | — | DEP-07(M) |
| F-OPS-008 | Matrix credentials (OREI_USER / OREI_PASSWORD) | V4 | V1 | V1 | — | — | — |
| F-OPS-009 | Verify the matrix TLS certificate (OREI_VERIFY_SSL) | V4 | V0 | V0 | — | — | — |
| F-OPS-010 | Log level (LOG_LEVEL) | V4 | V1 | V1 | — | — | — |
| F-OPS-011 | Enable/disable integrations (UC_ENABLED) | V4 | V3 | V3 | stale | [deploy.image_core·api·pass](evidence/F-OPS-001/2026-10-03-V3-b30436af-deploy.image_core-api.json)<br>[deploy.image_uc·uc·pass](evidence/F-OPS-001/2026-10-03-V3-b30436af-deploy.image_uc-uc.json) | DEP-07(M), BE-20(M) |
| F-OPS-012 | Background polling (POLLING_ENABLED / POLLING_INTERVAL) | V4 | V0 | V0 | — | — | TST-03(M) |
| F-OPS-013 | Telnet options (OREI_TELNET_PORT, OREI_USE_TELNET_CEC) | V4 | V1 | V1 | — | — | — |
| F-OPS-014 | Cache and retry tuning (OREI_STATUS_CACHE_TTL, OREI_CEC_CACHE_TTL, OREI_*RETR*) | V4 | V1 | V1 | — | — | — |
| F-OPS-015 | Hub data persists across restarts (DATA_DIR) | V4 | V3 | V3 | stale | [deploy.image_core·api·pass](evidence/F-OPS-001/2026-10-03-V3-b30436af-deploy.image_core-api.json)<br>[deploy.image_uc·uc·pass](evidence/F-OPS-001/2026-10-03-V3-b30436af-deploy.image_uc-uc.json) | DEP-07(M) |
| F-OPS-016 | Writes are atomic and safe under concurrency | V4 | V1 | V1 | — | — | — |
| F-OPS-017 | Migrate legacy data files (scenes -> profiles) | V4 | V1 | V1 | — | — | API-12(M), PER-04(M) |
| F-OPS-018 | Only one hub instance runs (process lock) | V4 | V1 | V1 | — | — | — |
| F-OPS-019 | One consistent version everywhere | V4 | V1 | V1 | — | — | DEP-06(M) |
| F-OPS-020 | Multi-arch images (amd64 + arm64) | V4 | V0 | V0 | — | — | — |

## Security controls (F-SEC)

| ID | Feature | Target | Level | Recorded | Freshness | Evidence | Open findings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-SEC-001 | Optional admin / control PIN gate | V3 | V1 | V1 | — | — | — |
| F-SEC-002 | Cross-site request protection (CORS, Origin, Content-Type, Host allow-list) | V3 | V1 | V1 | — | — | — |
| F-SEC-003 | Matrix host changes cannot leak the matrix password (SSRF guard) | V3 | V1 | V1 | — | — | — |
| F-SEC-004 | Profile/scene passcodes are stored as PBKDF2 hashes | V3 | V1 | V1 | — | — | — |
| F-SEC-005 | Passcode hashes are never sent to clients | V3 | V1 | V1 | — | — | — |
| F-SEC-006 | Changing or removing a PIN needs the current PIN | V3 | V1 | V1 | — | — | — |
| F-SEC-007 | Wrong-PIN attempts are limited and do not stall the hub | V3 | V1 | V1 | — | — | — |
| F-SEC-008 | Rate limiting per client | V3 | V1 | V1 | — | — | — |
| F-SEC-009 | Proxy headers trusted only from configured proxies | V3 | V1 | V1 | — | — | — |
| F-SEC-010 | Static files cannot escape the web root | V3 | V1 | V1 | — | — | — |
| F-SEC-011 | Error responses do not leak internals | V3 | V1 | V1 | — | — | — |
| F-SEC-012 | User-provided names are escaped in the UI (no XSS) | V3 | **V3** | V3 | — | — | — |
| F-SEC-013 | TLS certificate verification / pinning for the matrix | V3 | V1 | V1 | — | — | — |
| F-SEC-014 | No credentials in logs | V3 | V1 | V1 | — | — | — |
| F-SEC-015 | Remote 3 integration port requires authentication | V3 | **V3** | V3 | — | — | — |

## Reliability (F-REL)

| ID | Feature | Target | Level | Recorded | Freshness | Evidence | Open findings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-REL-001 | Reconnect automatically after a matrix outage | V4 | V0 | V0 | stale | [reboot.direct·api·pass](evidence/F-MTX-021/2026-10-04-V2-d6baf3ca-reboot.direct-api.json)<br>[reboot.enabled_shortcut·api·pass](evidence/F-MTX-021/2026-10-04-V2-d6baf3ca-reboot.enabled_shortcut-api.json) | — |
| F-REL-002 | Report the connection state truthfully on errors and timeouts | V4 | V0 | V0 | — | — | — |
| F-REL-003 | Detect a wrong matrix password | V4 | V0 | V0 | — | — | — |
| F-REL-004 | Log in again when the matrix session expires | V4 | V0 | V0 | — | — | — |
| F-REL-005 | Recover after the matrix reboots or is power-cycled | V4 | V0 | V0 | stale | [reboot.direct·api·pass](evidence/F-MTX-021/2026-10-04-V2-d6baf3ca-reboot.direct-api.json)<br>[reboot.enabled_shortcut·api·pass](evidence/F-MTX-021/2026-10-04-V2-d6baf3ca-reboot.enabled_shortcut-api.json) | — |
| F-REL-006 | Detect a dropped Telnet connection and reconnect | V4 | V0 | V0 | — | — | — |
| F-REL-007 | Shut down and disconnect cleanly | V4 | V0 | V0 | — | — | — |
| F-REL-008 | A command the matrix rejects is reported as failed | V4 | V0 | V0 | stale | [outputs.audio_mute_rejected·api·fail](evidence/F-REL-008/2026-09-25-V2-d6668000-outputs.audio_mute_rejected-api.json)<br>[outputs.audio_mute_rejected·api·pass](evidence/F-REL-008/2026-10-04-V2-7dbc4dc7-outputs.audio_mute_rejected-api.json) | — |
| F-REL-009 | Matrix unreachable: commands fail visibly and no state is made up | V4 | V3 | V3 | stale | [ha.matrix_offline·ha·pass](evidence/F-HA-013/2026-10-04-V3-7dbc4dc7-ha.matrix_offline-ha.json)<br>[failures.unreachable_switch·api·fail](evidence/F-REL-009/2026-09-25-V2-d6668000-failures.unreachable_switch-api.json) | — |
| F-REL-010 | Status stays fresh (caches expire, one refresh at a time) | V4 | V1 | V1 | — | — | — |
| F-REL-011 | API calls are not blocked while the hub reconnects | V4 | V0 | V0 | — | — | — |
| F-REL-012 | Background polling keeps state live without a Remote connected | V4 | V3 | V3 | stale | [live.front_panel_route·browser·pass](evidence/F-MTX-031/2026-10-04-V3-d6baf3ca-live.front_panel_route-browser.json) | — |
| F-REL-013 | The event loop never stalls (loop-lag metric) | V4 | V1 | V1 | — | — | — |
| F-REL-014 | A slow WebSocket client cannot stall commands | V4 | V2 | V2 | — | — | — |
| F-REL-015 | Tolerate slow and malformed matrix responses | V4 | V1 | V1 | — | — | — |
| F-REL-016 | Standby does not start reconnect storms or duplicate pollers | V4 | V0 | V0 | — | — | — |
| F-REL-017 | No leaked sessions, sockets or tasks after reconfiguration | V4 | V0 | V0 | — | — | — |
| F-REL-018 | 72-hour soak with flat memory, tasks and sockets | V5 | V0 | V0 | — | — | — |
