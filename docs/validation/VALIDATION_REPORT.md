# Release validation report

**Disposition: release candidate; final v1.0.0 gates remain open.**

**Scope:** this is the historical Phase 6/7 candidate report for the commits
listed below. Later runtime changes need a new validation campaign; their
current implementation and unresolved checks are tracked in the
[runtime execution record](../planning/RUNTIME_EXECUTION.md). The results here
do not establish acceptance of the current runtime branch.

This report records available evidence and its limits. The release gate in [VALIDATION_PLAN.md](VALIDATION_PLAN.md) requires every feature at its target with fresh evidence, hardware regression/fault/client sessions, and the 72-hour soak plus owner sign-off. Passing the CI regression gate does not establish those release gates.

## Candidate checks

Candidate metadata is **1.0.0rc1**, with expected Git tag **v1.0.0-rc1**. Neither the RC nor final release tag has been pushed. [PR #37](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/pull/37) is a draft pending the Phase 5 dependency and CI.

| Check | Result |
| --- | --- |
| Full local Python regression suite | 3,329 passed, 4 skipped, 28 deselected; dedicated HA/UC/Docker jobs run separately |
| REST route inventory | 177/177 covered (100%) |
| Scripted-Remote test suite | 100 passed with locked dependencies |
| Packaging, versions, wheels and sdists | 22 passed, including RC builds, installed resources and editable-install coexistence |
| Validation-discovery follow-up | 86 passed; discovery also succeeds in the requirements-only Linux container |
| Final image/compose/context tests | 26 passed, 2 expected skips; [deployment records](runs/rc1/deployment/) |
| Swagger through shipped image | 177 routes rendered online and with CDN blocked; zero page errors; synthetic admin PIN absent from localStorage after authorization; [record](runs/rc1/swagger.json) |
| Static checks | Ruff, mypy, JavaScript lint and actionlint passed; CSS findings stayed at the checked-in 521 baseline |
| Repository hygiene | Full committed tree: zero errors and warnings |
| Combined scenario regression gate | Passed; zero known or unexplained failures; expected clients api, browser, uc and ha all ran |

Focused documentation/protocol checks also passed: 435 tests. The combined regression [gate log](runs/rc1/regression-gate.log) is retained with the summaries.

The 1,546 passing scenario outcomes below include repeated feature/client checks; they are not 1,546 distinct features. The Flic placeholder contributes one explicit skip.

Both image architectures built with the candidate version label. The arm64 build also started under BuildKit QEMU, returned the canonical version/identity, and passed `run.py healthcheck`. These are emulation results, not a real Remote or arm64 deployment-host observation. Local Docker image IDs:

- amd64: `sha256:e0ab773c06ec8ff69d6cbd0416630072943cf49d8279b6539fa6b1c3e5cf7beb`
- arm64: `sha256:46b45d675a75fef217f786ae7bb8d8c9c8f96f7d0db609a0d3ec9f1e603b53a6`

Multiarch registry publication is pending the authorized merge/tag sequence. Source and image-backed summaries are retained under [runs/rc1](runs/rc1/README.md). The harness-only follow-up `f55660e` removes an installed-package requirement during scenario discovery; application code is unchanged from `ec850d2`.

**Visual release gate:** [PR #36 CI run 39083178584](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/actions/runs/39083178584) passed 1,098 UI tests with 33 skips and exactly three snapshot failures; all other applicable jobs passed. PR #36 still requires owner approval of three Tron paused-frame baselines affected by the requested 30-fps cap. Five API-modal deployment-port differences were normalized only after asserting the actual page origin. The approved image files remain unchanged. See the local before/after review at `build/phase5-visual-review/index.html`; no visual approval has been inferred.

## Scenario runs

| Summary | Source commit | Tracked changes at capture | Client | Pass | Fail | Blocked | Skipped |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| [source](runs/rc1/source.json) | `ec850d29815f2d7020261ccd8ccc3c3895810372` | clean | api | 1411 | 0 | 0 | 0 |
| [source](runs/rc1/source.json) | `ec850d29815f2d7020261ccd8ccc3c3895810372` | clean | browser | 54 | 0 | 0 | 0 |
| [source](runs/rc1/source.json) | `ec850d29815f2d7020261ccd8ccc3c3895810372` | clean | uc | 18 | 0 | 0 | 0 |
| [source](runs/rc1/source.json) | `ec850d29815f2d7020261ccd8ccc3c3895810372` | clean | flic | 0 | 0 | 0 | 1 |
| [home-assistant](runs/rc1/home-assistant.json) | `ec850d29815f2d7020261ccd8ccc3c3895810372` | clean | ha | 19 | 0 | 0 | 0 |
| [shipped-image](runs/rc1/shipped-image.json) | `f55660ee088408e368d5d7e4f1f7a0c1a7cfe7b3` | clean | api | 27 | 0 | 0 | 0 |
| [shipped-image](runs/rc1/shipped-image.json) | `f55660ee088408e368d5d7e4f1f7a0c1a7cfe7b3` | clean | browser | 17 | 0 | 0 | 0 |

A source-process scenario run is identified separately from shipped-image checks. A browser or scripted Remote is a real client, but source-process evidence alone does not establish the validation plan’s shipped-image condition. The scripted Remote is not a physical Remote 3. A real Home Assistant container is not the owner’s deployment. The dedicated Flic replay client is a placeholder; API template coverage does not establish V3 Flic-client proof.

## Hardware and reliability gates

| Gate | Status | Required evidence |
| --- | --- | --- |
| HIL-B regression | Pending | Real matrix readback and timestamped owner observations |
| HIL-C fault injection | Pending | Outage/recovery observations on the deployment host |
| HIL-E clients | Pending | Physical Remote 3, owner HA, real browser/kiosk checks |
| HIL-D 72-hour soak and field sign-off | Pending | Resource metrics across 72 hours and owner sign-off after daily use |
| Every feature at its target | Pending | Fresh evidence meeting each row’s target in the ledger |

Existing BK-808 captures identify MCU firmware **V1.10.01** and web firmware **V2.00.03**. These anchor the simulator/protocol reference; they are not a completed release hardware campaign. No other matrix model is claimed as hardware-validated for this candidate.

| Physical CEC behavior | Release observation |
| --- | --- |
| Input power, navigation and playback | Pending physical source observation |
| Output power, volume and mute | Pending TV/receiver observation |
| CEC configuration/readback | Simulator results do not establish physical effects |

## Runtime limitations

`run.py` still starts `OreiMatrix` and `RestApiServer` directly, or invokes the legacy UC driver. The Phase 4 `MatrixService`, `ActionRunner`, `IntegrationLoader`, and migration framework are library modules awaiting runtime consolidation. `FLIC_ENABLED` does not gate the mounted compatibility routes; `HA_DISCOVERY_ENABLED` does not start discovery. See [Architecture](../ARCHITECTURE.md) and [Configuration](../CONFIGURATION.md). These gaps remain visible in the candidate and must not be described as completed runtime behavior.

## Feature × client results

The cells below summarize only the supplied scenario runs. “—” means no result in these runs, not a pass. Levels describe the recorded scenario result; consult [LEDGER.md](LEDGER.md) for freshness, blocking findings, and the effective proof level. Multiple clients touching one feature do not raise it to hardware/field validation.

| Feature | Target | API | Browser | Scripted Remote | HA | Flic |
| --- | --- | --- | --- | --- | --- | --- |
| F-MTX-001 Route one input to one output | V4 | V2 pass (1) | V3 pass (1) | V3 pass (1) | V3 pass (1) | — |
| F-MTX-002 Route one input to every output | V4 | V2 pass (1) | V3 pass (1) | — | — | — |
| F-MTX-003 Recall a matrix preset (1-8) | V4 | V2 pass (1) | V3 pass (1) | V3 pass (1) | V3 pass (1) | — |
| F-MTX-004 Save the current routing to a matrix preset | V4 | V2 pass (11) | — | — | — | — |
| F-MTX-005 Name presets in the web app (names shown by the API, UI, kiosk) | V4 | V2 pass (1) | V3 pass (1) | — | — | — |
| F-MTX-006 Matrix power on / standby | V4 | V2 pass (2) | — | V3 pass (1) | V3 pass (2) | — |
| F-MTX-007 Mute / unmute the audio of an output | V4 | V2 pass (1) | — | — | V3 pass (1) | — |
| F-MTX-008 Enable / disable an output's video stream | V4 | V2 pass (5) | — | — | — | — |
| F-MTX-009 Set an output's HDCP mode | V4 | V2 pass (11) | — | — | — | — |
| F-MTX-010 Set an output's HDR mode | V4 | V2 pass (9) | — | — | — | — |
| F-MTX-011 Set an output's scaler mode (incl. audio-only) | V4 | V2 pass (11) | — | — | — | — |
| F-MTX-012 Enable / disable ARC on an output | V4 | V2 pass (5) | — | — | — | — |
| F-MTX-013 Set an input's EDID | V4 | V2 pass (10) | — | — | — | — |
| F-MTX-014 Copy EDID from a connected display | V4 | V2 pass (11) | — | — | — | — |
| F-MTX-015 External audio: matrix mode | V4 | V2 pass (9) | — | — | — | — |
| F-MTX-016 External audio: enable per output | V4 | V2 pass (20) | — | — | — | — |
| F-MTX-017 External audio: source per output | V4 | V2 pass (71) | — | — | — | — |
| F-MTX-018 Front-panel beep on / off | V4 | V2 pass (3) | — | — | — | — |
| F-MTX-019 Front-panel lock | V4 | V2 pass (3) | — | — | — | — |
| F-MTX-020 Front-panel LCD timeout | V4 | V2 pass (8) | — | — | — | — |
| F-MTX-021 Reboot the matrix | V4 | V2 pass (3) | V3 pass (1) | — | — | — |
| F-MTX-022 Rename inputs (names stored on the matrix) | V4 | V2 pass (6) | — | — | — | — |
| F-MTX-023 Rename outputs (names stored on the matrix) | V4 | V2 pass (6) | — | — | — | — |
| F-MTX-024 Read the current routing and names | V4 | V2 pass (4) | — | — | — | — |
| F-MTX-025 Show which inputs have an active signal | V4 | V2 pass (16) | — | — | — | — |
| F-MTX-026 Show which cables are plugged in (Telnet link status) | V4 | V2 pass (4) | — | — | — | — |
| F-MTX-027 Show which outputs have a display connected | V4 | V2 pass (16) | — | — | — | — |
| F-MTX-028 Show device info (model, firmware, network) | V4 | V2 pass (5) | — | — | — | — |
| F-MTX-029 Cycle an output to the next / previous input | V4 | V2 pass (138) | — | — | — | — |
| F-MTX-030 Read a preset's stored routing | V4 | V2 pass (9) | — | — | — | — |
| F-MTX-031 Notice changes made outside the hub (front panel, cable plugged, source on/off) | V4 | — | V3 pass (4) | — | V3 pass (1) | — |
| F-CEC-001 Power a source on / off over CEC | V4 | V2 pass (17) | — | — | — | — |
| F-CEC-002 Navigate a source's menus over CEC (up/down/left/right/select/menu/back) | V4 | V2 pass (56) | — | — | — | — |
| F-CEC-003 Control playback on a source over CEC | V4 | V2 pass (56) | — | — | — | — |
| F-CEC-004 Source volume / mute over CEC | V4 | V2 pass (24) | — | — | — | — |
| F-CEC-005 Turn a display (TV) on / off over CEC | V4 | V2 pass (17) | — | V3 pass (1) | V3 pass (1) | — |
| F-CEC-006 Display / soundbar volume and mute over CEC | V4 | V2 pass (25) | — | — | — | — |
| F-CEC-007 Enable CEC on the target port automatically before a command | V4 | V2 pass (417) | — | — | — | — |
| F-CEC-008 Enable / disable CEC per port | V4 | V2 pass (40) | — | — | — | — |
| F-CEC-009 Read which ports have CEC enabled | V4 | V2 pass (4) | — | — | — | — |
| F-CEC-010 Send CEC over Telnet (OREI_USE_TELNET_CEC) | V4 | V2 pass (206) | — | — | — | — |
| F-CEC-011 List CEC commands and per-port capabilities (incl. audio-only outputs) | V4 | V2 pass (88) | — | — | — | — |
| F-API-001 GET /api/health, /api/openapi.json, /api/docs (liveness, matrix connection, runtime metrics, OpenAPI 3.1 & Swagger UI) | V3 | V2 pass (3) | — | — | — | — |
| F-API-002 API info and root (GET /, /api, /api/info) | V2 | V2 pass (1) | — | — | — | — |
| F-API-003 GET /api/status | V3 | — | — | — | — | — |
| F-API-004 Detailed status (GET /api/status/full/inputs/outputs/cables/edid/ext-audio/system/device/cec) | V3 | V2 pass (6) | — | — | — | — |
| F-API-005 POST /api/switch (one output or all) | V3 | V2 pass (2) | — | — | — | — |
| F-API-006 POST /api/output/{output}/source and input cycling | V3 | — | — | — | — | — |
| F-API-007 POST /api/preset/{preset} (recall) | V3 | V2 pass (1) | — | — | — | — |
| F-API-008 POST /api/preset/{preset}/save | V2 | V2 pass (17) | — | — | — | — |
| F-API-009 POST /api/power/on/off | V3 | V2 pass (2) | — | — | — | — |
| F-API-010 Output setting routes (mute, enable, hdcp, hdr, scaler, arc) | V2 | — | — | — | — | — |
| F-API-011 EDID routes | V2 | — | — | — | — | — |
| F-API-012 External audio routes | V2 | — | — | — | — | — |
| F-API-013 System setting routes (beep, panel lock, LCD, reboot) | V2 | V2 pass (3) | V3 pass (1) | — | — | — |
| F-API-014 System info and storage routes | V2 | V2 pass (2) | — | — | — | — |
| F-API-015 CEC command routes | V3 | V2 pass (438) | — | — | — | — |
| F-API-016 CEC catalogue, capability and enable routes | V2 | V2 pass (132) | — | — | — | — |
| F-API-017 Device settings routes (icons, display names, preset names, favourite/dashboard presets) | V2 | V2 pass (9) | — | — | — | — |
| F-API-018 Name routes (POST /api/input/output/{n}/name) | V2 | V2 pass (1) | — | — | — | — |
| F-API-019 Profile routes | V2 | V2 pass (106) | — | — | — | — |
| F-API-020 Scene v1 alias routes (/api/scene*, /api/scenes) | V2 | V2 pass (69) | — | — | — | — |
| F-API-021 Scene v2 routes (/api/v2/scenes*) | V2 | V2 pass (44) | — | — | — | — |
| F-API-022 Response envelope and input validation (4xx before anything reaches the matrix) | V2 | V2 pass (1) | — | — | — | — |
| F-API-023 Macro routes | V2 | V2 pass (71) | — | — | — | — |
| F-API-024 Shortcut routes (/api/system-shortcuts* and the /api/shortcuts* aliases) | V2 | V2 pass (11) | — | — | — | — |
| F-API-025 Dashboard layout routes | V2 | V2 pass (2) | — | — | — | — |
| F-API-026 Themes and UI preference routes | V2 | V2 pass (5) | — | — | — | — |
| F-API-027 Settings routes (matrix host, test connection) | V2 | V2 pass (2) | — | — | — | — |
| F-API-028 Flic integration routes | V2 | V2 pass (2) | — | — | — | — |
| F-API-029 Web UI, kiosk and static asset routes | V3 | — | — | — | — | — |
| F-API-030 Rate limiting (60 requests / 10 s per client) | V2 | — | — | — | — | — |
| F-API-031 CORS headers | V2 | — | — | — | — | — |
| F-API-032 WebSocket /ws: welcome, status snapshot, get_status, matrix link, errors | V2 | V2 pass (3) | V3 pass (2) | — | — | — |
| F-API-033 WS event routing_change (one per changed output, whoever routed) / switch_failed | V3 | V2 pass (2) | — | — | — | — |
| F-API-034 Route to all: routing_change per output that changed / switch_all_failed | V3 | V2 pass (1) | — | — | — | — |
| F-API-035 WS event preset_recall / preset_recall_failed | V3 | V2 pass (1) | — | — | — | — |
| F-API-036 WS event audio_mute | V2 | V2 pass (2) | — | — | — | — |
| F-API-037 WS events device_settings / device_settings_full | V2 | V2 pass (1) | — | — | — | — |
| F-API-038 WS event cec_command | V2 | V2 pass (1) | — | — | — | — |
| F-API-039 WS status snapshot (after connect, after a first reading, get_status) | V2 | — | — | — | — | — |
| F-API-040 WS live matrix events from the hub's own poller (routing, power, signal, display, cable, mute, names) | V2 | V2 pass (1) | V3 pass (4) | — | — | — |
| F-API-041 WS event scene_execution_error | V2 | V2 pass (2) | — | — | — | — |
| F-API-042 WS heartbeat (ping / pong) | V2 | — | — | — | — | — |
| F-DOM-001 Create, edit and delete profiles | V3 | V2 pass (48) | — | — | — | — |
| F-DOM-002 Recall a profile: its routing is applied | V4 | V2 pass (8) | V3 pass (4) | — | — | — |
| F-DOM-003 Recall a profile: its output settings (mute, HDR, HDCP, enable) are applied | V4 | V2 pass (8) | V3 pass (6) | — | — | — |
| F-DOM-004 Recall a profile: its power-on macro runs | V4 | V2 pass (2) | V3 pass (2) | — | — | — |
| F-DOM-005 Protect a profile with a passcode (per-item PIN) | V3 | V2 pass (3) | V3 pass (5) | — | — | — |
| F-DOM-006 Favourite, pin, reorder profiles and show them on the dashboard | V3 | V2 pass (20) | — | — | — | — |
| F-DOM-007 Per-profile CEC targets (nav/playback/volume/power) and auto-resolve | V3 | V2 pass (83) | — | — | — | — |
| F-DOM-008 Profile execution log | V3 | V2 pass (6) | — | — | — | — |
| F-DOM-009 Save the current routing as a new profile | V3 | V2 pass (12) | — | — | — | — |
| F-DOM-010 Create, edit and delete scenes (sequences of steps) | V3 | V2 pass (46) | — | — | — | — |
| F-DOM-011 Run a scene: profile steps | V4 | V2 pass (12) | V3 pass (8) | — | — | — |
| F-DOM-012 Run a scene: macro steps | V4 | V2 pass (8) | V3 pass (4) | — | — | — |
| F-DOM-013 Run a scene: wait and shortcut steps | V3 | V2 pass (4) | V3 pass (4) | — | — | — |
| F-DOM-014 Scene overrides (per-run changes to a profile step) | V3 | V2 pass (8) | V3 pass (4) | — | — | — |
| F-DOM-015 Protect a scene with a passcode | V3 | V2 pass (3) | V3 pass (2) | — | — | — |
| F-DOM-016 Validate a scene and detect conflicting steps | V3 | V2 pass (4) | V3 pass (2) | — | — | — |
| F-DOM-017 Scene execution history | V3 | V2 pass (2) | V3 pass (2) | — | — | — |
| F-DOM-018 Legacy 'scenes' (v1) as aliases of profiles | V2 | V2 pass (2) | — | — | — | — |
| F-DOM-019 Create, edit, delete and validate CEC macros | V3 | V2 pass (62) | — | — | — | — |
| F-DOM-020 Run a CEC macro (steps, targets, delays) | V4 | V2 pass (8) | V3 pass (8) | — | — | — |
| F-DOM-021 Test / dry-run a macro | V3 | V2 pass (2) | — | — | — | — |
| F-DOM-022 Favourite macros and show them on the dashboard | V3 | V2 pass (7) | — | — | — | — |
| F-DOM-023 Built-in shortcuts: route all to an output, one-to-one routing | V3 | V2 pass (3) | V3 pass (1) | — | — | — |
| F-DOM-024 Built-in shortcut: power everything off | V3 | V2 pass (1) | V3 pass (1) | — | — | — |
| F-DOM-025 Built-in shortcuts: mute / unmute all outputs | V3 | V2 pass (3) | V3 pass (3) | — | — | — |
| F-DOM-026 Built-in shortcuts: recall preset 1-8 | V3 | V2 pass (1) | V3 pass (1) | — | — | — |
| F-DOM-027 Built-in shortcuts: beep, panel lock, reboot | V3 | V2 pass (9) | V3 pass (8) | — | — | — |
| F-DOM-028 Built-in shortcuts: LCD timeout | V3 | V2 pass (6) | V3 pass (6) | — | — | — |
| F-DOM-029 Create, rename, reorder and delete user shortcuts | V3 | — | — | — | — | — |
| F-DOM-030 Favourite shortcuts and show them on the dashboard | V3 | — | — | — | — | — |
| F-DOM-031 Dashboard layout (add, remove, reorder cards) | V3 | V2 pass (2) | — | — | — | — |
| F-DOM-032 Input/output icons, colours and display names (device settings) | V3 | — | — | — | — | — |
| F-DOM-033 Favourite presets and choose which presets the dashboard shows | V3 | — | — | — | — | — |
| F-DOM-034 Save a custom routing mapping into a preset | V3 | V2 pass (9) | — | — | — | — |
| F-DOM-035 Theme presets and custom themes | V3 | — | — | — | — | — |
| F-DOM-036 UI preferences stored on the hub | V3 | — | — | — | — | — |
| F-UI-001 Open the web UI; the header shows the matrix connection | V3 | — | — | — | — | — |
| F-UI-002 Route by clicking a cell in the matrix grid | V3 | — | V3 pass (1) | — | — | — |
| F-UI-003 Route from the matrix card view (routing sheet) | V3 | — | — | — | — | — |
| F-UI-004 Route one input to every output from the Route To All drawer | V3 | — | V3 pass (1) | — | — | — |
| F-UI-005 Recall a preset from the Presets drawer | V3 | — | V3 pass (1) | — | — | — |
| F-UI-006 Rename a preset in the Presets drawer | V3 | — | V3 pass (1) | — | — | — |
| F-UI-007 Overwrite a preset / save a custom mapping from the Presets drawer | V3 | — | — | — | — | — |
| F-UI-008 Run profiles, scenes, presets, shortcuts and macros from dashboard cards | V3 | — | V3 pass (2) | — | — | — |
| F-UI-009 Customise the dashboard (card picker, pin, reorder) | V3 | — | — | — | — | — |
| F-UI-010 Inputs tab: signal/cable status and input settings (name, icon, EDID) | V3 | — | — | — | — | — |
| F-UI-011 Outputs tab: display status and output settings (HDCP, HDR, scaler, ARC, mute) | V3 | — | — | — | — | — |
| F-UI-012 Profiles tab and profile manager | V3 | — | V3 pass (2) | — | — | — |
| F-UI-013 Create and edit a profile in the profile editor | V3 | — | — | — | — | — |
| F-UI-014 Run a passcode-protected profile (passcode prompt) | V3 | — | V3 pass (3) | — | — | — |
| F-UI-015 Build a scene in the scene editor | V3 | — | — | — | — | — |
| F-UI-016 Build a CEC macro in the macro editor | V3 | — | — | — | — | — |
| F-UI-017 CEC remote on output/input tiles and the CEC tray | V3 | — | — | — | — | — |
| F-UI-018 Theme presets, customisation and card opacity | V3 | — | — | — | — | — |
| F-UI-019 General settings: matrix host and connection test | V3 | — | — | — | — | — |
| F-UI-020 Hardware settings: beep, panel lock, LCD, reboot | V3 | — | — | — | — | — |
| F-UI-021 Interface settings | V3 | — | — | — | — | — |
| F-UI-022 Shortcuts drawer: run, rename, reorder | V3 | — | — | — | — | — |
| F-UI-023 Integrations drawer (Flic request builder, HA YAML, Remote 3 info) | V3 | — | — | — | — | — |
| F-UI-024 Live updates when another client or the matrix changes something | V3 | — | V3 pass (5) | — | — | — |
| F-UI-025 Reconnect and resync after the WebSocket drops | V3 | — | — | — | — | — |
| F-UI-026 Show an error state when the matrix is unreachable | V3 | — | — | — | — | — |
| F-UI-027 Toasts and confirmation dialogs | V3 | — | V3 pass (2) | — | — | — |
| F-UI-028 Keyboard shortcuts | V3 | — | — | — | — | — |
| F-UI-029 Accessibility (keyboard, focus, ARIA, contrast, zoom) | V3 | — | — | — | — | — |
| F-UI-030 Debug panel | V3 | — | — | — | — | — |
| F-UI-031 About dialog | V3 | — | — | — | — | — |
| F-UI-032 Animated Tron background (opt-in) | V3 | — | — | — | — | — |
| F-UI-033 Tablet and phone layouts | V3 | — | — | — | — | — |
| F-UI-034 Personalise tabs in the Control Deck (pin, reorder) | V3 | — | — | — | — | — |
| F-UI-035 Copy an API endpoint for automation (API button / modal) | V3 | — | — | — | — | — |
| F-UI-036 First-run setup wizard (matrix connection) | V3 | — | — | — | — | — |
| F-KIO-001 Open the kiosk; it shows the matrix connection | V3 | — | — | — | — | — |
| F-KIO-002 Route a source to one display with the routing wizard | V3 | — | V3 pass (1) | — | — | — |
| F-KIO-003 Route a source to every display from the kiosk | V3 | — | V3 pass (1) | — | — | — |
| F-KIO-004 Input and output status tiles | V3 | — | — | — | — | — |
| F-KIO-005 Recall a preset from the kiosk | V3 | — | — | — | — | — |
| F-KIO-006 Configure which presets the kiosk shows (edit mode) | V3 | — | — | — | — | — |
| F-KIO-007 Run shortcuts from the kiosk and map them to slots | V3 | — | — | — | — | — |
| F-KIO-008 Run profiles from the kiosk; create one with the profile wizard | V3 | — | V3 pass (2) | — | — | — |
| F-KIO-009 CEC remote in the kiosk | V3 | — | — | — | — | — |
| F-KIO-010 Kiosk live updates | V3 | — | V3 pass (2) | — | — | — |
| F-KIO-011 Kiosk disconnected state | V3 | — | V3 pass (1) | — | — | — |
| F-KIO-012 Kiosk layout and pins persist | V3 | — | — | — | — | — |
| F-KIO-013 Kiosk follows the selected theme | V3 | — | — | — | — | — |
| F-KIO-014 Kiosk touch accessibility (targets, ARIA, contrast) | V3 | — | — | — | — | — |
| F-UC-001 Discover the integration and register the driver (mDNS, driver URL) | V4 | — | — | — | — | — |
| F-UC-002 Set up the integration on the Remote | V4 | — | — | — | — | — |
| F-UC-003 Reconfigure the integration (new matrix address) | V4 | — | — | — | — | — |
| F-UC-004 Preset buttons on the Remote | V4 | — | — | V3 pass (2) | — | — |
| F-UC-005 Matrix remote entity with a preset page | V4 | — | — | V3 pass (2) | — | — |
| F-UC-006 Per-input CEC remotes (source power, navigation, playback) | V4 | — | — | V3 pass (3) | — | — |
| F-UC-007 Per-output CEC remotes (TV power, volume) | V4 | — | — | V3 pass (5) | — | — |
| F-UC-008 Choose an output's source from the Remote (media player source list) | V4 | — | — | V3 pass (3) | — | — |
| F-UC-009 TV power / volume / mute from the output media player | V4 | — | — | V3 pass (2) | — | — |
| F-UC-010 Matrix power switch on the Remote | V4 | — | — | V3 pass (2) | — | — |
| F-UC-011 Input signal and cable sensors | V4 | — | — | — | — | — |
| F-UC-012 Output connected, cable and source sensors | V4 | — | — | — | — | — |
| F-UC-013 Entities go unavailable while the matrix is unreachable | V4 | — | — | — | — | — |
| F-UC-014 Remote standby and wake | V4 | — | — | — | — | — |
| F-UC-015 Only changed attributes are sent to the Remote | V4 | — | — | — | — | — |
| F-UC-016 Renamed inputs/outputs show up on the Remote | V4 | — | — | V3 pass (1) | — | — |
| F-UC-017 Restore the configuration at startup (also with the matrix offline) | V4 | — | — | — | — | — |
| F-HA-001 Add the hub in Home Assistant (config flow) | V4 | — | — | — | V3 pass (1) | — |
| F-HA-002 Choose each output's source (select entities) | V4 | — | — | — | V3 pass (2) | — |
| F-HA-003 Matrix power switch | V4 | — | — | — | V3 pass (2) | — |
| F-HA-004 Output audio mute switches | V4 | — | — | — | V3 pass (1) | — |
| F-HA-005 Output stream enable switches | V4 | — | — | — | V3 pass (1) | — |
| F-HA-006 Preset buttons | V4 | — | — | — | V3 pass (1) | — |
| F-HA-007 Reboot button | V4 | — | — | — | V3 pass (1) | — |
| F-HA-008 Input signal binary sensors | V4 | — | — | — | V3 pass (1) | — |
| F-HA-009 Output connected binary sensors | V4 | — | — | — | V3 pass (1) | — |
| F-HA-010 Service hdmi_matrix.recall_preset | V4 | — | — | — | V3 pass (1) | — |
| F-HA-011 Service hdmi_matrix.switch_input | V4 | — | — | — | V3 pass (1) | — |
| F-HA-012 Service hdmi_matrix.send_cec_command | V4 | — | — | — | V3 pass (3) | — |
| F-HA-013 Poll the hub; entities go unavailable when it is unreachable | V4 | — | — | — | V3 pass (5) | — |
| F-HA-014 Install through HACS (custom repository) | V4 | — | — | — | — | — |
| F-HA-015 Device and entity naming in Home Assistant | V4 | — | — | — | V3 pass (1) | — |
| F-HA-016 Change the hub address of a configured matrix (reconfigure flow) | V4 | — | — | — | V3 pass (1) | — |
| F-HA-017 Polling interval option (options flow) | V4 | — | — | — | V3 pass (1) | — |
| F-HA-018 Services target one matrix (config entry or device) | V4 | — | — | — | V3 pass (2) | — |
| F-FLIC-001 Button click recalls a preset | V3 | — | — | — | — | — |
| F-FLIC-002 Button hold powers the matrix off / on | V3 | — | — | — | — | — |
| F-FLIC-003 Button powers a source on over CEC | V3 | — | — | — | — | — |
| F-FLIC-004 Flic Twist cycles an output through its inputs | V3 | — | — | — | — | — |
| F-FLIC-005 Flic Twist controls TV volume and mute over CEC | V3 | — | — | — | — | — |
| F-FLIC-006 Button recalls a profile or runs a macro | V3 | — | — | — | — | — |
| F-FLIC-007 Register Flic buttons with the hub (button registry) | V3 | — | — | — | — | — |
| F-FLIC-008 Button switches every output to input N (POST /api/input/{n}) | V3 | — | — | — | — | — |
| F-FLIC-009 Flic Hub SDK JavaScript module templates | V3 | — | — | — | — | — |
| F-FLIC-010 Generate Flic request URLs in the web UI | V3 | — | — | — | — | — |
| F-OPS-001 Run the hub from the Docker image | V4 | — | — | — | — | — |
| F-OPS-002 Run the hub without the Remote integration (UC_ENABLED=false, the default) | V4 | — | — | — | — | — |
| F-OPS-003 docker compose quick start | V4 | — | — | — | — | — |
| F-OPS-004 Remote 3 discovery works from Docker | V4 | — | — | — | — | — |
| F-OPS-005 Container health check and auto-restart | V4 | — | — | — | — | — |
| F-OPS-006 Point the hub at the matrix (MATRIX_HOST / MATRIX_PORT) | V4 | — | — | — | — | — |
| F-OPS-007 Choose the API port (API_PORT) | V4 | — | — | — | — | — |
| F-OPS-008 Matrix credentials (OREI_USER / OREI_PASSWORD) | V4 | — | — | — | — | — |
| F-OPS-009 Verify the matrix TLS certificate (OREI_VERIFY_SSL) | V4 | — | — | — | — | — |
| F-OPS-010 Log level (LOG_LEVEL) | V4 | — | — | — | — | — |
| F-OPS-011 Enable/disable integrations (UC_ENABLED) | V4 | — | — | — | — | — |
| F-OPS-012 Background polling (POLLING_ENABLED / POLLING_INTERVAL) | V4 | — | — | — | — | — |
| F-OPS-013 Telnet options (OREI_TELNET_PORT, OREI_USE_TELNET_CEC) | V4 | — | — | — | — | — |
| F-OPS-014 Cache and retry tuning (OREI_STATUS_CACHE_TTL, OREI_CEC_CACHE_TTL, OREI_*RETR*) | V4 | — | — | — | — | — |
| F-OPS-015 Hub data persists across restarts (DATA_DIR) | V4 | — | — | — | — | — |
| F-OPS-016 Writes are atomic and safe under concurrency | V4 | — | — | — | — | — |
| F-OPS-017 Migrate legacy data files (scenes -> profiles) | V4 | — | — | — | — | — |
| F-OPS-018 Only one hub instance runs (process lock) | V4 | — | — | — | — | — |
| F-OPS-019 One consistent version everywhere | V4 | — | — | — | — | — |
| F-OPS-020 Multi-arch images (amd64 + arm64) | V4 | — | — | — | — | — |
| F-SEC-001 Optional admin / control PIN gate | V3 | V2 pass (12) | — | — | — | — |
| F-SEC-002 Cross-site request protection (CORS, Origin, Content-Type, Host allow-list) | V3 | V2 pass (5) | — | — | — | — |
| F-SEC-003 Matrix host changes cannot leak the matrix password (SSRF guard) | V3 | V2 pass (6) | — | — | — | — |
| F-SEC-004 Profile/scene passcodes are stored as PBKDF2 hashes | V3 | V2 pass (2) | — | — | — | — |
| F-SEC-005 Passcode hashes are never sent to clients | V3 | V2 pass (2) | — | — | — | — |
| F-SEC-006 Changing or removing a PIN needs the current PIN | V3 | V2 pass (11) | — | — | — | — |
| F-SEC-007 Wrong-PIN attempts are limited and do not stall the hub | V3 | V2 pass (2) | — | — | — | — |
| F-SEC-008 Rate limiting per client | V3 | — | — | — | — | — |
| F-SEC-009 Proxy headers trusted only from configured proxies | V3 | — | — | — | — | — |
| F-SEC-010 Static files cannot escape the web root | V3 | V2 pass (2) | — | — | — | — |
| F-SEC-011 Error responses do not leak internals | V3 | V2 pass (2) | — | — | — | — |
| F-SEC-012 User-provided names are escaped in the UI (no XSS) | V3 | — | — | — | — | — |
| F-SEC-013 TLS certificate verification / pinning for the matrix | V3 | — | — | — | — | — |
| F-SEC-014 No credentials in logs | V3 | — | — | — | — | — |
| F-SEC-015 Remote 3 integration port requires authentication | V3 | — | — | — | — | — |
| F-REL-001 Reconnect automatically after a matrix outage | V4 | V2 pass (3) | V3 pass (1) | — | — | — |
| F-REL-002 Report the connection state truthfully on errors and timeouts | V4 | — | — | — | — | — |
| F-REL-003 Detect a wrong matrix password | V4 | — | — | — | — | — |
| F-REL-004 Log in again when the matrix session expires | V4 | — | — | — | — | — |
| F-REL-005 Recover after the matrix reboots or is power-cycled | V4 | V2 pass (3) | V3 pass (1) | — | — | — |
| F-REL-006 Detect a dropped Telnet connection and reconnect | V4 | — | — | — | — | — |
| F-REL-007 Shut down and disconnect cleanly | V4 | — | — | — | — | — |
| F-REL-008 A command the matrix rejects is reported as failed | V4 | V2 pass (1) | — | — | — | — |
| F-REL-009 Matrix unreachable: commands fail visibly and no state is made up | V4 | V2 pass (1) | V3 pass (1) | — | V3 pass (1) | — |
| F-REL-010 Status stays fresh (caches expire, one refresh at a time) | V4 | — | — | — | — | — |
| F-REL-011 API calls are not blocked while the hub reconnects | V4 | — | — | — | — | — |
| F-REL-012 Background polling keeps state live without a Remote connected | V4 | — | V3 pass (1) | — | — | — |
| F-REL-013 The event loop never stalls (loop-lag metric) | V4 | — | — | — | — | — |
| F-REL-014 A slow WebSocket client cannot stall commands | V4 | — | — | — | — | — |
| F-REL-015 Tolerate slow and malformed matrix responses | V4 | — | — | — | — | — |
| F-REL-016 Standby does not start reconnect storms or duplicate pollers | V4 | — | — | — | — | — |
| F-REL-017 No leaked sessions, sockets or tasks after reconfiguration | V4 | — | — | — | — | — |
| F-REL-018 72-hour soak with flat memory, tasks and sockets | V5 | — | — | — | — | — |

## Closing the final gate

Attach the owner-observed hardware and soak evidence using the schema and procedures in [the validation guide](README.md), regenerate the ledger, resolve any unexplained failures and below-target features, and update this report before tagging `v1.0.0`. Do not infer approval or a hardware observation from the passage of time.
