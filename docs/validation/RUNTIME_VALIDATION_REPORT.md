# Runtime validation report

**Disposition: software candidate; final independent review, PR checks, owner visual approval and physical/field gates remain separate.**

The [archived manifest](runs/runtime-r8b/manifest.json) retains each actual run commit, artifact root, timestamp, scope and outcome count. These are multiple explicitly attributed runs, not a claim that every historical test ran at one final SHA. The [Phase 6/7 report](VALIDATION_REPORT.md) remains historical evidence.

The [formal combined evidence gate](runs/runtime-r8b/formal-gate.txt) passed with zero known failures linked to open findings. It consumed all five client types and the actual source, image and deployment evidence roots. The [gate context](runs/runtime-r8b/formal-gate-context.json) records its consolidation scope. This regression gate does not establish that every feature has reached its hardware/field target.

## Independent restoration review and evidence history

The [accepted independent review](RUNTIME_REVIEW_RESTORATION.md) records exact source/image identities and focused findings dispositions. The complete campaigns below then test the clean integrated candidate; a source-only correction is not treated as shipped-image acceptance.

R2D validates legacy migration provenance before accepting v2 coexistence. R1G/R1H restore the sole transport reconnect owner after failed or timed-out rollback login. R1I restores original logical identity across interrupted cleanup and retains one public retirement owner. Uncertified disconnect errors retain an explicit error and traffic/reconnect fence until a supported successful lifecycle drain or restart; they are not reported as recovered connectivity. Actual successful late disposal hands off under current-client/generation/shutdown/reconnect-policy guards. Production cleanup remains five seconds with a separately bounded settling phase of at most five more; this does not impose one global ten-second transaction deadline. Existing review oracles and visual baselines remain unchanged.

The supported Orei transport applies its intentional-close fence before its first await. A separate conditional probe replaces that public call with a failure before its body runs; an already-running supervisor can then continue while composition retains the command fence. The probe remains preserved with its failing outcome and passing after-disposal control. No natural Orei in-body bypass was demonstrated, and the actual in-body error control passes. Independent public quiescence for an alternate disconnect implementation is a documented extension limit, not an accepted universal arbitrary-client guarantee or a relabeled supported-product pass.

The [earlier campaign archive](runs/runtime/manifest.json) remains immutable and tied to 4adbc13. Its [attributed report at the pre-restoration checkpoint](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/40da5376/docs/validation/RUNTIME_VALIDATION_REPORT.md) preserves the earlier complete counts and known CI/UI limits. Failed original R8/R8B/R8C reproductions remain in their reports and local evidence; later passes do not relabel those attempts. Historical source/image proof and physical/field approval retain their distinct scopes.

## Software checks

| Check | Actual commit | Result | Scope |
| --- | --- | --- | --- |
| Complete core (includes actual installed package entry checks) | `1baac3dec660f41345869c126cfca94d6731c5a0` | 4041 passed, 4 skipped | Windows local core; excludes HA component and dedicated UC suites; expected platform skips retained |
| Dedicated scripted Remote | `1baac3dec660f41345869c126cfca94d6731c5a0` | 100 passed, 0 skipped | 100 actual SDK/simulator tests; no physical Remote claim |
| Actual amd64 deployment | `1baac3dec660f41345869c126cfca94d6731c5a0` | 26 passed, 3 skipped | Normal built-image command, health, actual SDK/discovery/volume/context checks; explicit configuration skips |
| R8 and R8B image release regressions | `1baac3dec660f41345869c126cfca94d6731c5a0` | 4 passed, 0 skipped | Current normal amd64 image; both UC restarts and immediate/deadline rollback recovery; zero xfail/skip |

Registered REST route coverage was 177/177 (100.0%) in the enabled configuration; the [original complete-core log](runs/runtime-r8b/final-source-rerun.log) records its actual run and result.
The [external-image route diagnostic context](runs/runtime-r8b/r8-image-targeted-route-inventory-context.json) retains the supplemental non-strict zero count from tests outside the instrumented application process. That invocation overwrote the shared diagnostic after the complete strict core run; the original complete JSON was not separately retained. The actual complete result remains in its original log and independent CI log. Future helpers disable the supplemental writer; no replacement JSON was reconstructed.
The final source browser smoke/flow project passed 59 tests with 0 unexpected results, 0 flaky results and 0 skips. Visual baseline acceptance is separate.

[CI at 1baac3de](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/actions/runs/39228762775) completed with all twelve non-UI required jobs passing. Its core run separately passed 4,023 tests with 22 skips, 35 deselections and 177/177 routes in 690.90 seconds; the actual HA container passed all 19 scenarios. Main UI passed 1,098 tests with 33 skips and failed the three existing owner-pending Tron paused-frame snapshots in 25.3 minutes. The review gallery passed all 62 cases in 3.4 minutes. Actual raw/sanitized logs, final job metadata and both UI artifacts remain under build/runtime-completion/pr38-1baac-*. CI and local counts have distinct environments; this is not a visual approval or a claim about a later documentation-only CI head.

Older core, installed-package, component and platform supplements retain their original commits; their individual scopes are listed above. They do not by themselves prove later UI code or shipped-image behavior. Windows filesystem skips and optional dependency skips remain visible. The dedicated HA component unit suite is distinct from actual HA containers below.

## Application images

Both local images were built from clean tracked `1baac3dec660f41345869c126cfca94d6731c5a0` with product version `1.0.0rc1`:

- amd64: `sha256:558c2677c65995598d7b06a2f1726c2a254ae1afac74b1f34060f336bac0fd8e`
- arm64: `sha256:c7d017fbcbf61e47b64aeab12cab0d153fe92b9ca74ecf0823b32cb551e14c93`

The archived input-parity record verifies the actual tracked shipped bytes on both architectures. The normal-command amd64 deployment checks include real SDK source selection/readback/restore and separate discovery observers. Arm64/QEMU scope is offline startup, canonical metadata, Docker health and graceful SIGTERM; it does not establish arm64 device actions or physical hardware.

No application source is mounted over the client-test image. These local image IDs do not imply a registry publication or Git release tag. API contract version and product version are separate.

## Client campaigns

Every archived outcome below passed; none failed, blocked or skipped. Counts describe scenario/client outcomes, not unique features.

Individual checks explicitly scoped to another client remain recorded as non-applicable (for example browser toasts during API requests). The milestone import verifies each such exclusion against the unchanged scenario definition; it does not turn non-applicable assertions into passes or accept failed checks. The milestone journal lists them.

| Summary | Original commit | Passing outcomes | Scope |
| --- | --- | --- | --- |
| [source-campaigns](runs/runtime-r8b/source-campaigns.json) | `1baac3dec660f41345869c126cfca94d6731c5a0` | api: 1411, browser: 54, uc: 18, flic: 23 | Normal source run.py: all declared simulator API/browser/scripted-Remote/Flic outcomes |
| [source-ha-current](runs/runtime-r8b/source-ha-current.json) | `1baac3dec660f41345869c126cfca94d6731c5a0` | ha: 19 | Normal source runtime through actual HA 2026.9.3 container |
| [source-ha-minimum-line](runs/runtime-r8b/source-ha-minimum-line.json) | `1baac3dec660f41345869c126cfca94d6731c5a0` | ha: 19 | Normal source runtime through actual HA 2025.1.4 container; supported line, not exact 2025.1.0 floor |
| [image-campaigns-cached](runs/runtime-r8b/image-campaigns-cached.json) | `1baac3dec660f41345869c126cfca94d6731c5a0` | api: 70, browser: 47, flic: 22 | Normal amd64 image: representative API plus full browser/Flic cached-setting scenarios |
| [image-campaigns-fresh](runs/runtime-r8b/image-campaigns-fresh.json) | `1baac3dec660f41345869c126cfca94d6731c5a0` | api: 9, browser: 7, flic: 1 | Same amd64 image: declared fresh-cache fault/recovery API/browser/Flic scenarios |
| [image-ha-campaigns-cached](runs/runtime-r8b/image-ha-campaigns-cached.json) | `1baac3dec660f41345869c126cfca94d6731c5a0` | ha: 18 | Same amd64 image through actual current HA container, declared cached settings |
| [image-ha-campaigns-fresh](runs/runtime-r8b/image-ha-campaigns-fresh.json) | `1baac3dec660f41345869c126cfca94d6731c5a0` | ha: 1 | Same amd64 image through actual current HA container, declared fresh settings |
| [image-uc-campaigns](runs/runtime-r8b/image-uc-campaigns.json) | `1baac3dec660f41345869c126cfca94d6731c5a0` | uc: 18 | Same amd64 image, real SDK socket and unchanged 18 scripted-Remote scenario oracles |

Image campaigns exercise every declared simulator browser, scripted Remote, Flic and HA scenario. The API image selection covers representative domain behavior plus all preset-read scenarios; it does not repeat all source API scenarios. Two image groups use the scenarios' declared cache/fault settings. The image Remote harness explicitly supplies the real Docker-published SDK socket to the unchanged RemoteClient/scenario oracles.

Source-only client results do not meet the shipped-image condition for V3 by themselves. Flic validation executes generated JavaScript against a Node SDK stub and replays actual HTTP requests through the hub into simulator state; it does not prove physical button/radio behavior. A scripted Remote is not a physical Remote 3. Actual disposable HA containers are distinct from the owner's HA deployment, and Docker discovery is distinct from physical LAN mDNS.

The minimum-line HA run uses 2025.1.4; it does not certify the exact 2025.1.0 floor. The current HA campaign is pinned to 2026.9.3. Both versions and their real run commits remain explicit.

SDK 0.7 does not advertise the optional select entities. Direct dispatcher cycling checks are not Remote WebSocket cycling proof; actual Remote media-player source selection is tested separately.

Swagger browser records cover 177 documented operations with Flic enabled and 175 with it disabled, online and with the CDN blocked, without page errors or persistence of the synthetic admin PIN. This establishes catalog/rendering behavior, not execution of every disabled-configuration handler. Separate runtime tests check disabled-route absence and retained core reads.

## UI routing correction and rejected runs

The independent read-only source review and actual-source JavaScript probes demonstrated a sufficient persistent ordering race: a newer WebSocket route could be overwritten by a delayed REST status during startup or manual refresh. This is bounded causal proof, not exact attribution of every packet in the first failed CI run. The correction preserves newer WS routes received during each status request, both map/array aliases, later REST fallback and out-of-order load completion. Existing initial-route, offline-no-update and reconnect-resync smoke expectations remain unchanged.

The correction report records exact worker/coordinator commands, revisions, red/green checks and artifact limits. Pre-refinement flow runs remain distinct from final-code evidence. No visual baseline was regenerated or approved by these tests.

The earlier source preset failures remain archived as failed evidence. R1E restored explicit status-refresh invalidation of preset slots through the sole runtime owner, retaining ordinary polling TTL behavior. The original HA 17-pass/two-failure summary is also retained: R6C corrected typed application-error classification in the validation harness without accepting unexpected transport failures. R5C replaced Linux Docker-network/log assumptions with explicit isolated networks and actual discovery observations. Original/interim results were not relabeled as passes for later code.

The complete 55d4fe0 image batch was rejected when flic.source_power returned HTTP 200 but omitted the required CEC-enable write, produced a disabled-port protocol warning and left input 1 disabled. R1F reproduced the explicit-sync cache gap through actual protocol, facade and WS paths and expires cached enable decisions on explicit refresh. Ordinary polling/cache controls remain intact. The worker's focused source/image proofs honestly identify dirty precommit source and are bound to final production bytes by hashes; they are distinct from the clean complete campaigns listed above. Coordinator registered REST cases fail before and pass after the fix for both an input and an output. Original failed image evidence is preserved.

A separate validation metadata correction preserves leading Git porcelain status whitespace. Actual disposable Git tests reproduce the first unstaged filename truncation and verify complete paths with inherited Git location variables. Historical worker dirty-path records remain unmodified; their report supplies the exact file list and hashes. These focused proofs were never relabeled as clean-commit full campaigns.

The earlier discovery of legacy tests touching checkout runtime files is retained in the execution history. No pre-run backup was available; the later 16-file name/hash checkpoint only establishes integrity relative to that post-discovery point. It does not prove those files were unchanged before the initial broad run. Runtime-file values and credentials are not included in the report.

## Remaining release gates

- Final independent disposition after complete campaign/evidence consolidation and final PR checks.
- The pending three Tron paused-frame owner visual decisions for PR #36/#37 and the approved merge/tag sequence.
- Owner HIL-B regression, HIL-C recovery and HIL-E deployed/physical client evidence, including matrix/attached-device firmware and physical CEC effects.
- HIL-D continuous 72-hour resource measurements and the owner's week of daily use/sign-off; follow the field runbook.
- Every feature at its required target with fresh accepted evidence. Software checks do not substitute for physical/field proof.
- Synchronize canonical metadata to `1.0.0`, rebuild matching images and refresh affected evidence before final publication. An RC image must not be published as a final-version artifact.

## Feature and client outcomes

Each cell counts passing source (`S`) and shipped-image (`I`) scenario/client outcomes. The current HA source run is counted once; its minimum-line support run is listed separately above. A dash means no direct run cell; unit/component/platform checks retain their own scopes. Counts do not promote registry baselines or grant hardware levels.

| Feature | Target | API | Browser | Scripted Remote | HA | Flic |
| --- | --- | --- | --- | --- | --- | --- |
| F-MTX-001 Route one input to one output | V4 | S:1, I:1 | S:1, I:1 | S:1, I:1 | S:1, I:1 | - |
| F-MTX-002 Route one input to every output | V4 | S:1, I:1 | S:1, I:1 | - | - | - |
| F-MTX-003 Recall a matrix preset (1-8) | V4 | S:1, I:1 | S:1, I:1 | S:1, I:1 | S:1, I:1 | - |
| F-MTX-004 Save the current routing to a matrix preset | V4 | S:11, I:8 | - | - | - | - |
| F-MTX-005 Name presets in the web app (names shown by the API, UI, kiosk) | V4 | S:1, I:1 | S:1, I:1 | - | - | - |
| F-MTX-006 Matrix power on / standby | V4 | S:2 | - | S:1, I:1 | S:2, I:2 | - |
| F-MTX-007 Mute / unmute the audio of an output | V4 | S:1 | - | - | S:1, I:1 | - |
| F-MTX-008 Enable / disable an output's video stream | V4 | S:5 | - | - | - | - |
| F-MTX-009 Set an output's HDCP mode | V4 | S:11 | - | - | - | - |
| F-MTX-010 Set an output's HDR mode | V4 | S:9 | - | - | - | - |
| F-MTX-011 Set an output's scaler mode (incl. audio-only) | V4 | S:11 | - | - | - | - |
| F-MTX-012 Enable / disable ARC on an output | V4 | S:5 | - | - | - | - |
| F-MTX-013 Set an input's EDID | V4 | S:10 | - | - | - | - |
| F-MTX-014 Copy EDID from a connected display | V4 | S:11 | - | - | - | - |
| F-MTX-015 External audio: matrix mode | V4 | S:9 | - | - | - | - |
| F-MTX-016 External audio: enable per output | V4 | S:20 | - | - | - | - |
| F-MTX-017 External audio: source per output | V4 | S:71 | - | - | - | - |
| F-MTX-018 Front-panel beep on / off | V4 | S:3 | - | - | - | - |
| F-MTX-019 Front-panel lock | V4 | S:3 | - | - | - | - |
| F-MTX-020 Front-panel LCD timeout | V4 | S:8 | - | - | - | - |
| F-MTX-021 Reboot the matrix | V4 | S:3, I:1 | S:1, I:1 | - | - | - |
| F-MTX-022 Rename inputs (names stored on the matrix) | V4 | S:6 | - | - | - | - |
| F-MTX-023 Rename outputs (names stored on the matrix) | V4 | S:6 | - | - | - | - |
| F-MTX-024 Read the current routing and names | V4 | S:4 | - | - | - | - |
| F-MTX-025 Show which inputs have an active signal | V4 | S:16 | - | - | - | - |
| F-MTX-026 Show which cables are plugged in (Telnet link status) | V4 | S:4 | - | - | - | - |
| F-MTX-027 Show which outputs have a display connected | V4 | S:16 | - | - | - | - |
| F-MTX-028 Show device info (model, firmware, network) | V4 | S:5 | - | - | - | - |
| F-MTX-029 Cycle an output to the next / previous input | V4 | S:138 | - | - | - | - |
| F-MTX-030 Read a preset's stored routing | V4 | S:9, I:9 | - | - | - | - |
| F-MTX-031 Notice changes made outside the hub (front panel, cable plugged, source on/off) | V4 | - | S:4, I:4 | - | S:1, I:1 | - |
| F-CEC-001 Power a source on / off over CEC | V4 | S:17 | - | - | - | - |
| F-CEC-002 Navigate a source's menus over CEC (up/down/left/right/select/menu/back) | V4 | S:56 | - | - | - | - |
| F-CEC-003 Control playback on a source over CEC | V4 | S:56 | - | - | - | - |
| F-CEC-004 Source volume / mute over CEC | V4 | S:24 | - | - | - | - |
| F-CEC-005 Turn a display (TV) on / off over CEC | V4 | S:17 | - | S:1, I:1 | S:1, I:1 | - |
| F-CEC-006 Display / soundbar volume and mute over CEC | V4 | S:25 | - | - | - | - |
| F-CEC-007 Enable CEC on the target port automatically before a command | V4 | S:417 | - | - | - | - |
| F-CEC-008 Enable / disable CEC per port | V4 | S:40 | - | - | - | - |
| F-CEC-009 Read which ports have CEC enabled | V4 | S:4 | - | - | - | - |
| F-CEC-010 Send CEC over Telnet (OREI_USE_TELNET_CEC) | V4 | S:206 | - | - | - | - |
| F-CEC-011 List CEC commands and per-port capabilities (incl. audio-only outputs) | V4 | S:88 | - | - | - | - |
| F-API-001 GET /api/health, /api/openapi.json, /api/docs (liveness, matrix connection, runtime metrics, integration lifecycle, OpenAPI 3.1 & Swagger UI) | V3 | S:3 | - | - | - | - |
| F-API-002 API info and root (GET /, /api, /api/info) | V2 | S:1 | - | - | - | - |
| F-API-003 GET /api/status | V3 | - | - | - | - | - |
| F-API-004 Detailed status (GET /api/status/full\|inputs\|outputs\|cables\|edid\|ext-audio\|system\|device\|cec) | V3 | S:6 | - | - | - | - |
| F-API-005 POST /api/switch (one output or all) | V3 | S:2, I:2 | - | - | - | - |
| F-API-006 POST /api/output/{output}/source and input cycling | V3 | - | - | - | - | - |
| F-API-007 POST /api/preset/{preset} (recall) | V3 | S:1, I:1 | - | - | - | - |
| F-API-008 POST /api/preset/{preset}/save | V2 | S:17, I:16 | - | - | - | - |
| F-API-009 POST /api/power/on\|off | V3 | S:2 | - | - | - | - |
| F-API-010 Output setting routes (mute, enable, hdcp, hdr, scaler, arc) | V2 | - | - | - | - | - |
| F-API-011 EDID routes | V2 | - | - | - | - | - |
| F-API-012 External audio routes | V2 | - | - | - | - | - |
| F-API-013 System setting routes (beep, panel lock, LCD, reboot) | V2 | S:3, I:1 | S:1, I:1 | - | - | - |
| F-API-014 System info and storage routes | V2 | S:2 | - | - | - | - |
| F-API-015 CEC command routes | V3 | S:438 | - | - | - | - |
| F-API-016 CEC catalogue, capability and enable routes | V2 | S:132 | - | - | - | - |
| F-API-017 Device settings routes (icons, display names, preset names, favourite/dashboard presets) | V2 | S:9 | - | - | - | - |
| F-API-018 Name routes (POST /api/input\|output/{n}/name) | V2 | S:1 | - | - | - | - |
| F-API-019 Profile routes | V2 | S:106 | - | - | - | - |
| F-API-020 Scene v1 alias routes (/api/scene*, /api/scenes) | V2 | S:68, I:1 | - | - | - | - |
| F-API-021 Scene v2 routes (/api/v2/scenes*) | V2 | S:44 | - | - | - | - |
| F-API-022 Response envelope and input validation (4xx before anything reaches the matrix) | V2 | S:1 | - | - | - | - |
| F-API-023 Macro routes | V2 | S:71 | - | - | - | - |
| F-API-024 Shortcut routes (/api/system-shortcuts* and the /api/shortcuts* aliases) | V2 | S:11 | - | - | - | - |
| F-API-025 Dashboard layout routes | V2 | S:2 | - | - | - | - |
| F-API-026 Themes and UI preference routes | V2 | S:5 | - | - | - | - |
| F-API-027 Settings routes (matrix host, test connection) | V2 | S:2 | - | - | - | - |
| F-API-028 Flic integration routes | V2 | S:2 | - | - | - | - |
| F-API-029 Web UI, kiosk and static asset routes | V3 | - | - | - | - | - |
| F-API-030 Rate limiting (60 requests / 10 s per client) | V2 | - | - | - | - | - |
| F-API-031 CORS headers | V2 | - | - | - | - | - |
| F-API-032 WebSocket /ws: welcome, status snapshot, get_status, matrix link, errors | V2 | S:3, I:1 | S:2, I:2 | - | - | - |
| F-API-033 WS event routing_change (one per changed output, whoever routed) / switch_failed | V3 | S:2, I:1 | - | - | - | - |
| F-API-034 Route to all: routing_change per output that changed / switch_all_failed | V3 | S:1, I:1 | - | - | - | - |
| F-API-035 WS event preset_recall / preset_recall_failed | V3 | S:1, I:1 | - | - | - | - |
| F-API-036 WS event audio_mute | V2 | S:2 | - | - | - | - |
| F-API-037 WS events device_settings / device_settings_full | V2 | S:1, I:1 | - | - | - | - |
| F-API-038 WS event cec_command | V2 | S:1 | - | - | - | - |
| F-API-039 WS status snapshot (after connect, after a first reading, get_status) | V2 | - | - | - | - | - |
| F-API-040 WS live matrix events from the hub's own poller (routing, power, signal, display, cable, mute, names) | V2 | S:1 | S:4, I:4 | - | - | - |
| F-API-041 WS event scene_execution_error | V2 | S:1, I:1 | - | - | - | - |
| F-API-042 WS heartbeat (ping / pong) | V2 | - | - | - | - | - |
| F-DOM-001 Create, edit and delete profiles | V3 | S:48 | - | - | - | - |
| F-DOM-002 Recall a profile: its routing is applied | V4 | S:4, I:4 | S:2, I:2 | - | - | - |
| F-DOM-003 Recall a profile: its output settings (mute, HDR, HDCP, enable) are applied | V4 | S:4, I:4 | S:3, I:3 | - | - | - |
| F-DOM-004 Recall a profile: its power-on macro runs | V4 | S:1, I:1 | S:1, I:1 | - | - | - |
| F-DOM-005 Protect a profile with a passcode (per-item PIN) | V3 | S:3, I:3 | S:5, I:5 | - | - | - |
| F-DOM-006 Favourite, pin, reorder profiles and show them on the dashboard | V3 | S:20 | - | - | - | - |
| F-DOM-007 Per-profile CEC targets (nav/playback/volume/power) and auto-resolve | V3 | S:83 | - | - | - | - |
| F-DOM-008 Profile execution log | V3 | S:6 | - | - | - | - |
| F-DOM-009 Save the current routing as a new profile | V3 | S:12 | - | - | - | - |
| F-DOM-010 Create, edit and delete scenes (sequences of steps) | V3 | S:46 | - | - | - | - |
| F-DOM-011 Run a scene: profile steps | V4 | S:6, I:6 | S:4, I:4 | - | - | - |
| F-DOM-012 Run a scene: macro steps | V4 | S:4, I:4 | S:2, I:2 | - | - | - |
| F-DOM-013 Run a scene: wait and shortcut steps | V3 | S:2, I:2 | S:2, I:2 | - | - | - |
| F-DOM-014 Scene overrides (per-run changes to a profile step) | V3 | S:4, I:4 | S:2, I:2 | - | - | - |
| F-DOM-015 Protect a scene with a passcode | V3 | S:2, I:1 | S:1, I:1 | - | - | - |
| F-DOM-016 Validate a scene and detect conflicting steps | V3 | S:2, I:2 | S:1, I:1 | - | - | - |
| F-DOM-017 Scene execution history | V3 | S:1, I:1 | S:1, I:1 | - | - | - |
| F-DOM-018 Legacy 'scenes' (v1) as aliases of profiles | V2 | S:2 | - | - | - | - |
| F-DOM-019 Create, edit, delete and validate CEC macros | V3 | S:62 | - | - | - | - |
| F-DOM-020 Run a CEC macro (steps, targets, delays) | V4 | S:4, I:4 | S:4, I:4 | - | - | - |
| F-DOM-021 Test / dry-run a macro | V3 | S:2 | - | - | - | - |
| F-DOM-022 Favourite macros and show them on the dashboard | V3 | S:7 | - | - | - | - |
| F-DOM-023 Built-in shortcuts: route all to an output, one-to-one routing | V3 | S:3, I:1 | S:1, I:1 | - | - | - |
| F-DOM-024 Built-in shortcut: power everything off | V3 | S:1, I:1 | S:1, I:1 | - | - | - |
| F-DOM-025 Built-in shortcuts: mute / unmute all outputs | V3 | S:3, I:3 | S:3, I:3 | - | - | - |
| F-DOM-026 Built-in shortcuts: recall preset 1-8 | V3 | S:1, I:1 | S:1, I:1 | - | - | - |
| F-DOM-027 Built-in shortcuts: beep, panel lock, reboot | V3 | S:9, I:8 | S:8, I:8 | - | - | - |
| F-DOM-028 Built-in shortcuts: LCD timeout | V3 | S:6, I:6 | S:6, I:6 | - | - | - |
| F-DOM-029 Create, rename, reorder and delete user shortcuts | V3 | - | - | - | - | - |
| F-DOM-030 Favourite shortcuts and show them on the dashboard | V3 | - | - | - | - | - |
| F-DOM-031 Dashboard layout (add, remove, reorder cards) | V3 | S:2 | - | - | - | - |
| F-DOM-032 Input/output icons, colours and display names (device settings) | V3 | - | - | - | - | - |
| F-DOM-033 Favourite presets and choose which presets the dashboard shows | V3 | - | - | - | - | - |
| F-DOM-034 Save a custom routing mapping into a preset | V3 | S:9, I:8 | - | - | - | - |
| F-DOM-035 Theme presets and custom themes | V3 | - | - | - | - | - |
| F-DOM-036 UI preferences stored on the hub | V3 | - | - | - | - | - |
| F-UI-001 Open the web UI; the header shows the matrix connection | V3 | - | - | - | - | - |
| F-UI-002 Route by clicking a cell in the matrix grid | V3 | - | S:1, I:1 | - | - | - |
| F-UI-003 Route from the matrix card view (routing sheet) | V3 | - | - | - | - | - |
| F-UI-004 Route one input to every output from the Route To All drawer | V3 | - | S:1, I:1 | - | - | - |
| F-UI-005 Recall a preset from the Presets drawer | V3 | - | S:1, I:1 | - | - | - |
| F-UI-006 Rename a preset in the Presets drawer | V3 | - | S:1, I:1 | - | - | - |
| F-UI-007 Overwrite a preset / save a custom mapping from the Presets drawer | V3 | - | - | - | - | - |
| F-UI-008 Run profiles, scenes, presets, shortcuts and macros from dashboard cards | V3 | - | S:1, I:1 | - | - | - |
| F-UI-009 Customise the dashboard (card picker, pin, reorder) | V3 | - | - | - | - | - |
| F-UI-010 Inputs tab: signal/cable status and input settings (name, icon, EDID) | V3 | - | - | - | - | - |
| F-UI-011 Outputs tab: display status and output settings (HDCP, HDR, scaler, ARC, mute) | V3 | - | - | - | - | - |
| F-UI-012 Profiles tab and profile manager | V3 | - | S:1, I:1 | - | - | - |
| F-UI-013 Create and edit a profile in the profile editor | V3 | - | - | - | - | - |
| F-UI-014 Run a passcode-protected profile (passcode prompt) | V3 | - | S:3, I:3 | - | - | - |
| F-UI-015 Build a scene in the scene editor | V3 | - | - | - | - | - |
| F-UI-016 Build a CEC macro in the macro editor | V3 | - | - | - | - | - |
| F-UI-017 CEC remote on output/input tiles and the CEC tray | V3 | - | - | - | - | - |
| F-UI-018 Theme presets, customisation and card opacity | V3 | - | - | - | - | - |
| F-UI-019 General settings: matrix host and connection test | V3 | - | - | - | - | - |
| F-UI-020 Hardware settings: beep, panel lock, LCD, reboot | V3 | - | - | - | - | - |
| F-UI-021 Interface settings | V3 | - | - | - | - | - |
| F-UI-022 Shortcuts drawer: run, rename, reorder | V3 | - | - | - | - | - |
| F-UI-023 Integrations drawer (Flic request builder, HA YAML, Remote 3 info) | V3 | - | - | - | - | - |
| F-UI-024 Live updates when another client or the matrix changes something | V3 | - | S:5, I:5 | - | - | - |
| F-UI-025 Reconnect and resync after the WebSocket drops | V3 | - | - | - | - | - |
| F-UI-026 Show an error state when the matrix is unreachable | V3 | - | - | - | - | - |
| F-UI-027 Toasts and confirmation dialogs | V3 | - | S:1, I:1 | - | - | - |
| F-UI-028 Keyboard shortcuts | V3 | - | - | - | - | - |
| F-UI-029 Accessibility (keyboard, focus, ARIA, contrast, zoom) | V3 | - | - | - | - | - |
| F-UI-030 Debug panel | V3 | - | - | - | - | - |
| F-UI-031 About dialog | V3 | - | - | - | - | - |
| F-UI-032 Animated Tron background (opt-in) | V3 | - | - | - | - | - |
| F-UI-033 Tablet and phone layouts | V3 | - | - | - | - | - |
| F-UI-034 Personalise tabs in the Control Deck (pin, reorder) | V3 | - | - | - | - | - |
| F-UI-035 Copy an API endpoint for automation (API button / modal) | V3 | - | - | - | - | - |
| F-UI-036 First-run setup wizard (matrix connection) | V3 | - | - | - | - | - |
| F-KIO-001 Open the kiosk; it shows the matrix connection | V3 | - | - | - | - | - |
| F-KIO-002 Route a source to one display with the routing wizard | V3 | - | S:1, I:1 | - | - | - |
| F-KIO-003 Route a source to every display from the kiosk | V3 | - | S:1, I:1 | - | - | - |
| F-KIO-004 Input and output status tiles | V3 | - | - | - | - | - |
| F-KIO-005 Recall a preset from the kiosk | V3 | - | - | - | - | - |
| F-KIO-006 Configure which presets the kiosk shows (edit mode) | V3 | - | - | - | - | - |
| F-KIO-007 Run shortcuts from the kiosk and map them to slots | V3 | - | - | - | - | - |
| F-KIO-008 Run profiles from the kiosk; create one with the profile wizard | V3 | - | S:2, I:2 | - | - | - |
| F-KIO-009 CEC remote in the kiosk | V3 | - | - | - | - | - |
| F-KIO-010 Kiosk live updates | V3 | - | S:2, I:2 | - | - | - |
| F-KIO-011 Kiosk disconnected state | V3 | - | S:1, I:1 | - | - | - |
| F-KIO-012 Kiosk layout and pins persist | V3 | - | - | - | - | - |
| F-KIO-013 Kiosk follows the selected theme | V3 | - | - | - | - | - |
| F-KIO-014 Kiosk touch accessibility (targets, ARIA, contrast) | V3 | - | - | - | - | - |
| F-UC-001 Discover the integration and register the driver (mDNS, driver URL) | V4 | - | - | - | - | - |
| F-UC-002 Set up the integration on the Remote | V4 | - | - | - | - | - |
| F-UC-003 Reconfigure the integration (new matrix address) | V4 | - | - | - | - | - |
| F-UC-004 Preset buttons on the Remote | V4 | - | - | S:2, I:2 | - | - |
| F-UC-005 Matrix remote entity with a preset page | V4 | - | - | S:2, I:2 | - | - |
| F-UC-006 Per-input CEC remotes (source power, navigation, playback) | V4 | - | - | S:3, I:3 | - | - |
| F-UC-007 Per-output CEC remotes (TV power, volume) | V4 | - | - | S:5, I:5 | - | - |
| F-UC-008 Choose an output's source from the Remote (media player source list) | V4 | - | - | S:3, I:3 | - | - |
| F-UC-009 TV power / volume / mute from the output media player | V4 | - | - | S:2, I:2 | - | - |
| F-UC-010 Matrix power switch on the Remote | V4 | - | - | S:2, I:2 | - | - |
| F-UC-011 Input signal and cable sensors | V4 | - | - | - | - | - |
| F-UC-012 Output connected, cable and source sensors | V4 | - | - | - | - | - |
| F-UC-013 Entities go unavailable while the matrix is unreachable | V4 | - | - | - | - | - |
| F-UC-014 Remote standby and wake | V4 | - | - | - | - | - |
| F-UC-015 Only changed attributes are sent to the Remote | V4 | - | - | - | - | - |
| F-UC-016 Renamed inputs/outputs show up on the Remote | V4 | - | - | S:1, I:1 | - | - |
| F-UC-017 Restore the configuration at startup (also with the matrix offline) | V4 | - | - | - | - | - |
| F-HA-001 Add the hub in Home Assistant (config flow) | V4 | - | - | - | S:1, I:1 | - |
| F-HA-002 Choose each output's source (select entities) | V4 | - | - | - | S:2, I:2 | - |
| F-HA-003 Matrix power switch | V4 | - | - | - | S:2, I:2 | - |
| F-HA-004 Output audio mute switches | V4 | - | - | - | S:1, I:1 | - |
| F-HA-005 Output stream enable switches | V4 | - | - | - | S:1, I:1 | - |
| F-HA-006 Preset buttons | V4 | - | - | - | S:1, I:1 | - |
| F-HA-007 Reboot button | V4 | - | - | - | S:1, I:1 | - |
| F-HA-008 Input signal binary sensors | V4 | - | - | - | S:1, I:1 | - |
| F-HA-009 Output connected binary sensors | V4 | - | - | - | S:1, I:1 | - |
| F-HA-010 Service hdmi_matrix.recall_preset | V4 | - | - | - | S:1, I:1 | - |
| F-HA-011 Service hdmi_matrix.switch_input | V4 | - | - | - | S:1, I:1 | - |
| F-HA-012 Service hdmi_matrix.send_cec_command | V4 | - | - | - | S:3, I:3 | - |
| F-HA-013 Poll the hub; entities go unavailable when it is unreachable | V4 | - | - | - | S:5, I:5 | - |
| F-HA-014 Install through HACS (custom repository) | V4 | - | - | - | - | - |
| F-HA-015 Device and entity naming in Home Assistant | V4 | - | - | - | S:1, I:1 | - |
| F-HA-016 Change the hub address of a configured matrix (reconfigure flow) | V4 | - | - | - | S:1, I:1 | - |
| F-HA-017 Polling interval option (options flow) | V4 | - | - | - | S:1, I:1 | - |
| F-HA-018 Services target one matrix (config entry or device) | V4 | - | - | - | S:2, I:2 | - |
| F-FLIC-001 Button click recalls a preset | V3 | - | - | - | - | S:1, I:1 |
| F-FLIC-002 Button hold powers the matrix off / on | V3 | - | - | - | - | S:2, I:2 |
| F-FLIC-003 Button powers a source on over CEC | V3 | - | - | - | - | S:1, I:1 |
| F-FLIC-004 Flic Twist cycles an output through its inputs | V3 | - | - | - | - | S:3, I:3 |
| F-FLIC-005 Flic Twist controls TV volume and mute over CEC | V3 | - | - | - | - | S:2, I:2 |
| F-FLIC-006 Button recalls a profile or runs a macro | V3 | - | - | - | - | S:5, I:5 |
| F-FLIC-007 Register Flic buttons with the hub (button registry) | V3 | - | - | - | - | S:1, I:1 |
| F-FLIC-008 Button switches every output to input N (POST /api/switch with JSON input) | V3 | - | - | - | - | S:1, I:1 |
| F-FLIC-009 Flic Hub SDK JavaScript module templates | V3 | - | - | - | - | S:9, I:9 |
| F-FLIC-010 Generate Flic request URLs in the web UI | V3 | - | - | - | - | S:16, I:16 |
| F-OPS-001 Run the hub from the Docker image | V4 | - | - | - | - | - |
| F-OPS-002 Run the hub without the Remote integration (UC_ENABLED=false, the default) | V4 | - | - | - | - | - |
| F-OPS-003 docker compose quick start | V4 | - | - | - | - | - |
| F-OPS-004 Remote 3 discovery works from Docker | V4 | - | - | - | - | - |
| F-OPS-005 Container health check and auto-restart | V4 | - | - | - | - | - |
| F-OPS-006 Point the hub at the matrix (MATRIX_HOST / MATRIX_PORT) | V4 | - | - | - | - | - |
| F-OPS-007 Choose the API port (API_PORT) | V4 | - | - | - | - | - |
| F-OPS-008 Matrix credentials (OREI_USER / OREI_PASSWORD) | V4 | - | - | - | - | - |
| F-OPS-009 Verify the matrix TLS certificate (OREI_VERIFY_SSL) | V4 | - | - | - | - | - |
| F-OPS-010 Log level (LOG_LEVEL) | V4 | - | - | - | - | - |
| F-OPS-011 Enable/disable integrations (UC_ENABLED) | V4 | - | - | - | - | - |
| F-OPS-012 Background polling (POLLING_ENABLED / POLLING_INTERVAL) | V4 | - | - | - | - | - |
| F-OPS-013 Telnet options (OREI_TELNET_PORT, OREI_USE_TELNET_CEC) | V4 | - | - | - | - | - |
| F-OPS-014 Cache and retry tuning (OREI_STATUS_CACHE_TTL, OREI_CEC_CACHE_TTL, OREI_*RETR*) | V4 | - | - | - | - | - |
| F-OPS-015 Hub data persists across restarts (DATA_DIR) | V4 | - | - | - | - | - |
| F-OPS-016 Writes are atomic and safe under concurrency | V4 | - | - | - | - | - |
| F-OPS-017 Migrate legacy data files (scenes -> profiles) | V4 | - | - | - | - | - |
| F-OPS-018 Only one hub instance runs (process lock) | V4 | - | - | - | - | - |
| F-OPS-019 One consistent version everywhere | V4 | - | - | - | - | - |
| F-OPS-020 Multi-arch images (amd64 + arm64) | V4 | - | - | - | - | - |
| F-SEC-001 Optional admin / control PIN gate | V3 | S:12 | - | - | - | - |
| F-SEC-002 Cross-site request protection (CORS, Origin, Content-Type, Host allow-list) | V3 | S:5 | - | - | - | - |
| F-SEC-003 Matrix host changes cannot leak the matrix password (SSRF guard) | V3 | S:6 | - | - | - | - |
| F-SEC-004 Profile/scene passcodes are stored as PBKDF2 hashes | V3 | S:2 | - | - | - | - |
| F-SEC-005 Passcode hashes are never sent to clients | V3 | S:2 | - | - | - | - |
| F-SEC-006 Changing or removing a PIN needs the current PIN | V3 | S:11 | - | - | - | - |
| F-SEC-007 Wrong-PIN attempts are limited and do not stall the hub | V3 | S:2 | - | - | - | - |
| F-SEC-008 Rate limiting per client | V3 | - | - | - | - | - |
| F-SEC-009 Proxy headers trusted only from configured proxies | V3 | - | - | - | - | - |
| F-SEC-010 Static files cannot escape the web root | V3 | S:2 | - | - | - | - |
| F-SEC-011 Error responses do not leak internals | V3 | S:2 | - | - | - | - |
| F-SEC-012 User-provided names are escaped in the UI (no XSS) | V3 | - | - | - | - | - |
| F-SEC-013 TLS certificate verification / pinning for the matrix | V3 | - | - | - | - | - |
| F-SEC-014 No credentials in logs | V3 | - | - | - | - | - |
| F-SEC-015 Remote 3 integration port requires authentication | V3 | - | - | - | - | - |
| F-REL-001 Reconnect automatically after a matrix outage | V4 | S:3, I:1 | S:1, I:1 | - | - | - |
| F-REL-002 Report the connection state truthfully on errors and timeouts | V4 | - | - | - | - | - |
| F-REL-003 Detect a wrong matrix password | V4 | - | - | - | - | - |
| F-REL-004 Log in again when the matrix session expires | V4 | - | - | - | - | - |
| F-REL-005 Recover after the matrix reboots or is power-cycled | V4 | S:3, I:1 | S:1, I:1 | - | - | - |
| F-REL-006 Detect a dropped Telnet connection and reconnect | V4 | - | - | - | - | - |
| F-REL-007 Shut down and disconnect cleanly | V4 | - | - | - | - | - |
| F-REL-008 A command the matrix rejects is reported as failed | V4 | S:1 | - | - | - | - |
| F-REL-009 Matrix unreachable: commands fail visibly and no state is made up | V4 | S:1 | S:1, I:1 | - | S:1, I:1 | - |
| F-REL-010 Status stays fresh (caches expire, one refresh at a time) | V4 | - | - | - | - | - |
| F-REL-011 API calls are not blocked while the hub reconnects | V4 | - | - | - | - | - |
| F-REL-012 Background polling keeps state live without a Remote connected | V4 | - | S:1, I:1 | - | - | - |
| F-REL-013 The event loop never stalls (loop-lag metric) | V4 | - | - | - | - | - |
| F-REL-014 A slow WebSocket client cannot stall commands | V4 | - | - | - | - | - |
| F-REL-015 Tolerate slow and malformed matrix responses | V4 | - | - | - | - | - |
| F-REL-016 Standby does not start reconnect storms or duplicate pollers | V4 | - | - | - | - | - |
| F-REL-017 No leaked sessions, sockets or tasks after reconfiguration | V4 | - | - | - | - | - |
| F-REL-018 72-hour soak with flat memory, tasks and sockets | V5 | - | - | - | - | - |
