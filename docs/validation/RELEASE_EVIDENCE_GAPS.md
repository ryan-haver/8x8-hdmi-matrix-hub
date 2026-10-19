# Release evidence-gap inventory

Status: **read-only planning snapshot; no feature levels promoted**. Updated 2026-10-19.
Computed at `621288b11580f348d24481a2973622a4f1f1855a` using the existing ledger policy and committed evidence.
This is an inventory of qualification gaps, **not a list of confirmed code defects**.
No scenarios, model workers, hardware actions or soak collectors were launched for this inventory.

Authorities: [registry](features.yaml), [generated ledger](LEDGER.md),
[validation policy](README.md), [target definitions](VALIDATION_PLAN.md),
[release checklist](RELEASE_VALIDATION_CHECKLIST.md),
[runtime evidence](RUNTIME_VALIDATION_INDEX.md) and
[standing coordination protocol](../ORCHESTRATION_PROTOCOL.md).

## Method and limits

The local read-only audit loads `tools.validate.registry.load_features` and
`load_findings`, validates feature/scenario references, discovers declarative
scenarios and calls `tools.validate.ledger.compute` with only
`docs/validation/evidence`. It does not regenerate the ledger, modify the
registry or import evidence from local/CI artifacts. Input hashes, complete
268-row observations and exact scenario mappings are retained locally in
`build/release-readiness/evidence-gap-snapshot-refined.json`; the initial
calculation and command receipts are retained alongside it. These local
artifacts are supplemental; the portable feature results are listed below.

**Effective level** follows the existing policy: highest fresh passing
record, otherwise recorded baseline, capped at V1 by open critical/high
findings. A numerically at-target baseline can still lack fresh proof.
Freshness is evaluated at the snapshot commit, not guaranteed for a later
candidate. The audit is not a rerun or a fresh evidence-schema qualification.

Scenario mappings use `Scenario.features_for(client)`, not the union of
all clients in the scenario. For example, `routing.switch_one` attributes
F-API-005/F-API-033 to API only and F-UI-002 to the browser. A browser run
therefore cannot be silently relabeled V3 API-contract evidence. Mapped
means declared scenario/target/client linkage, not verified driver support,
adequate assertions, an executed pass or complete coverage of the feature.

## Gap totals

| Exclusive bucket | Features | Meaning |
| --- | ---: | --- |
| Software targets below V2/V3 requirement | 89 | Evidence reconciliation, appropriate client assertions or narrowly scoped corrections |
| Hardware targets below V4 requirement | 120 | Real matrix/deployment/client proof; software prerequisites may also be missing |
| Field target below V5 requirement | 1 | F-REL-018: 72-hour resource soak and owner field acceptance |
| Numerically at target | 58 | Still inspect freshness and accepted evidence; not blanket release qualification |
| **All** | **268** | **210 below target**, unchanged from the committed ledger |

| Area | Total | Software gap | Hardware gap | Field gap | At target |
| --- | ---: | ---: | ---: | ---: | ---: |
| Matrix control | 31 | 0 | 31 | 0 | 0 |
| CEC control | 11 | 0 | 11 | 0 | 0 |
| REST/WebSocket contract | 42 | 29 | 0 | 0 | 13 |
| Domain features | 36 | 18 | 6 | 0 | 12 |
| Web UI | 36 | 22 | 0 | 0 | 14 |
| Kiosk | 14 | 7 | 0 | 0 | 7 |
| Remote 3 integration | 17 | 0 | 17 | 0 | 0 |
| Home Assistant component | 18 | 0 | 18 | 0 | 0 |
| Flic | 10 | 0 | 0 | 0 | 10 |
| Deployment, configuration, persistence | 20 | 0 | 20 | 0 | 0 |
| Security controls | 15 | 13 | 0 | 0 | 2 |
| Reliability | 18 | 0 | 17 | 1 | 0 |

The 89 software gaps partition into **14 with a target-level scenario/client
mapping**, **29 with existing scenarios but no mapped target-level client**,
and **46 with no discoverable scenario mapping**. These are planning routes,
not accepted checks. The 43 existing-scenario features include 26 stale rows;
reconcile real current source/image records before deciding which need reruns
or new assertions. All mapped-target cases are V2; the 29 other mapped cases
need V3 client proof, not just another API run.

### Overlapping evidence risks

| Bucket | Stale features | No discoverable scenarios | Capped by finding | With fresh passing record |
| --- | ---: | ---: | ---: | ---: |
| Software gaps | 26 | 46 | 0 | 6 |
| Hardware gaps | 39 | 42 | 12 | 46 |
| Field gap | 0 | 1 | 0 | 0 |
| At target | 3 | 12 | 0 | 43 |

These columns overlap and must not be added to the 210-gap count. Overall:
**68 stale features**, **101 without discoverable scenarios**, **12 capped**,
**95 with a fresh passing record**, and **zero with a fresh failing record**.
Zero fresh failing records does not establish all features work or are tested.

All 12 caps are HIL-09: F-MTX-007 through F-MTX-017, plus F-MTX-020.
Their real-device setting/protocol finding remains open; scenario passes
alone cannot remove the V1 cap. Other linked findings remain visible below.

The three numerically at-target **stale** features are F-API-021 (scene v2
routes), F-API-036 (audio_mute WS event) and F-API-038 (cec_command WS event).
Additionally, the following 15 at-target rows lack any fresh passing scenario
record (the three stale rows are included, not added):

`F-API-021`, `F-API-029`, `F-API-036`, `F-API-038`, `F-API-039`, `F-API-042`, `F-UI-001`, `F-UI-015`, `F-UI-025`, `F-UI-026`, `F-UI-031`, `F-KIO-001`, `F-KIO-004`, `F-SEC-012`, `F-SEC-015`.

Their baseline/test basis needs inspection against the final fresh-evidence
requirement. Do not present all 58 as fully release-qualified.

## Proposed follow-up packages

**All packages are planned, unlaunched and unqualified.** Quota remains
unknown. Exact host/model catalogs, access, quota/headroom and independent
reviewer qualification must be refreshed before any implementation dispatch.
Use disjoint task paths and coordinator-owned registry/contract integration;
do not create worktrees simply to fill a model roster.

| Priority / package | Scope and first action | Candidate staffing, subject to preflight | Observable acceptance |
| --- | --- | --- | --- |
| P0 / EV-01 evidence reconciliation | Inspect original source/image/CI records for the 14 target-mapped software gaps, 26 stale software rows and 15 at-target rows without fresh proof. Compare feature/client attribution, covers, source SHA and actual assertions before any import or rerun. | Coordinator owns registry/import decisions; Luna can inventory bounded records after verified headroom. Evidence review must not claim runtime reruns. | Source-linked per-feature disposition: valid original evidence, required rerun, missing assertions or actual finding; preserved bytes and no unsupported promotion. |
| P1 / EV-02 API and security proof | 29 API gaps and 13 security gaps; inspect absent mappings, API-only versus V3-client assertions and no-PIN/admin/admin+control cases. Coordinate shared negative/auth fixtures serially. | Sol for consequential contract/security changes; Flash may own bounded tests only after domain qualification. Implementation review requires a verified different underlying family. | Required API/event/client and negative effects verified on the actual candidate; reviewed tests/evidence and applicable full regression checks. |
| P1 / EV-03 domain and UI/kiosk proof | 18 domain, 22 UI and seven kiosk software gaps. Inspect existing browser tests first; connect actual user flows to feature assertions without weakening or merely relabeling them. Agree exclusive files before separating UI/domain tracks. | Sol for domain semantics, Argon for complex UI after provider/family proof, Flash for bounded QA; no automatic qualification from labels. | Real-client state/effect proof, failure/cancel paths where relevant, approved visual handling and independent cross-family review of new implementation. |
| P2 / EV-04 physical protocol and clients | All 120 V4 gaps, including 12 HIL-09 caps and 42 features without scenario mappings. Map read-only/write/restore/physical-observation needs before the owner session. | Coordinator prepares bounded runbooks; qualified protocol reviewer may assist. Owner supplies real-device observations; models cannot attest physical effects. | Accepted HIL-B/C/E observations, actual firmware/topology, restored state, findings disposition and feature-attributed V4 evidence. |
| P2 / EV-05 soak and field sign-off | F-REL-018 plus owner daily-use requirements. Use the existing field collector/runbook; no new collector is assumed necessary. | Owner/deployment operator executes; coordinator analyzes preserved measurements. Any new tooling needs qualified cross-family review. | Continuous 72-hour resource record, explained gaps/restarts, metrics analysis and dated week-of-use sign-off for the accepted candidate. |

EV-01 findings determine whether EV-02/03 need implementation or only reviewed
evidence capture. New tests/fixtures/tooling are implementation and require
qualified cross-family review. Astra can supplement Sol concurrency analysis
but cannot satisfy that family gate. MiniMax M3/M3.1 Flash and DeepSeek Pro/
Flash remain conditional candidates until exact selection, access, capacity
and task/review qualification are proven. Claude/Anthropic remains excluded.

## Complete feature inventory

Each feature appears exactly once below. `Map` is the number of discoverable
scenarios attributing the feature to any declared client, not passing tests.
`Target map` means declared simulator API for V2, declared real client for
V3, or declared hardware scenario for V4. It is never field proof. `—` in
freshness means no recognized scenario records, not a freshness pass.
Open finding IDs are read using the existing register parser; caps are
indicated explicitly. See the [ledger](LEDGER.md) for original evidence links.

### Software targets: 89 below target

| Feature | Description | Level -> target | Freshness | Map | Target map | Open findings / cap |
| --- | --- | --- | --- | ---: | --- | --- |
| F-API-001 | GET /api/health, /api/openapi.json, /api/docs (liveness, matrix connection, runtime metrics, integration lifecycle, OpenAPI 3.1 & Swagger UI) | V2 -> V3 | — | 3 | no | — |
| F-API-002 | API info and root (GET /, /api, /api/info) | V1 -> V2 | — | 1 | yes | — |
| F-API-003 | GET /api/status | V2 -> V3 | — | 0 | no | — |
| F-API-004 | Detailed status (GET /api/status/full\|inputs\|outputs\|cables\|edid\|ext-audio\|system\|device\|cec) | V1 -> V3 | stale | 6 | no | — |
| F-API-005 | POST /api/switch (one output or all) | V2 -> V3 | fresh | 2 | no | — |
| F-API-006 | POST /api/output/{output}/source and input cycling | V1 -> V3 | — | 0 | no | — |
| F-API-007 | POST /api/preset/{preset} (recall) | V2 -> V3 | fresh | 1 | no | — |
| F-API-009 | POST /api/power/on\|off | V1 -> V3 | stale | 2 | no | — |
| F-API-010 | Output setting routes (mute, enable, hdcp, hdr, scaler, arc) | V1 -> V2 | — | 0 | no | — |
| F-API-011 | EDID routes | V1 -> V2 | — | 0 | no | — |
| F-API-012 | External audio routes | V1 -> V2 | — | 0 | no | — |
| F-API-014 | System info and storage routes | V1 -> V2 | stale | 2 | yes | — |
| F-API-015 | CEC command routes | V1 -> V3 | stale | 438 | no | — |
| F-API-016 | CEC catalogue, capability and enable routes | V1 -> V2 | stale | 132 | yes | — |
| F-API-017 | Device settings routes (icons, display names, preset names, favourite/dashboard presets) | V1 -> V2 | stale | 9 | yes | — |
| F-API-018 | Name routes (POST /api/input\|output/{n}/name) | V0 -> V2 | stale | 1 | yes | BE-16 |
| F-API-019 | Profile routes | V1 -> V2 | stale | 106 | yes | — |
| F-API-022 | Response envelope and input validation (4xx before anything reaches the matrix) | V1 -> V2 | stale | 1 | yes | API-21 |
| F-API-023 | Macro routes | V1 -> V2 | stale | 71 | yes | — |
| F-API-024 | Shortcut routes (/api/system-shortcuts* and the /api/shortcuts* aliases) | V1 -> V2 | stale | 11 | yes | — |
| F-API-025 | Dashboard layout routes | V1 -> V2 | stale | 2 | yes | API-20 |
| F-API-026 | Themes and UI preference routes | V1 -> V2 | stale | 5 | yes | — |
| F-API-027 | Settings routes (matrix host, test connection) | V1 -> V2 | stale | 2 | yes | TST-03 |
| F-API-028 | Flic integration routes | V0 -> V2 | stale | 2 | yes | TST-03 |
| F-API-030 | Rate limiting (60 requests / 10 s per client) | V1 -> V2 | — | 0 | no | — |
| F-API-031 | CORS headers | V1 -> V2 | — | 0 | no | — |
| F-API-033 | WS event routing_change (one per changed output, whoever routed) / switch_failed | V2 -> V3 | fresh | 2 | no | — |
| F-API-034 | Route to all: routing_change per output that changed / switch_all_failed | V2 -> V3 | fresh | 1 | no | — |
| F-API-035 | WS event preset_recall / preset_recall_failed | V2 -> V3 | fresh | 1 | no | — |
| F-DOM-001 | Create, edit and delete profiles | V1 -> V3 | stale | 48 | no | — |
| F-DOM-006 | Favourite, pin, reorder profiles and show them on the dashboard | V1 -> V3 | stale | 20 | no | API-20 |
| F-DOM-007 | Per-profile CEC targets (nav/playback/volume/power) and auto-resolve | V1 -> V3 | stale | 83 | no | — |
| F-DOM-008 | Profile execution log | V0 -> V3 | stale | 6 | no | — |
| F-DOM-009 | Save the current routing as a new profile | V1 -> V3 | stale | 12 | no | API-12 |
| F-DOM-010 | Create, edit and delete scenes (sequences of steps) | V2 -> V3 | stale | 46 | no | API-12 |
| F-DOM-018 | Legacy 'scenes' (v1) as aliases of profiles | V1 -> V2 | stale | 2 | yes | API-12 |
| F-DOM-019 | Create, edit, delete and validate CEC macros | V1 -> V3 | stale | 62 | no | — |
| F-DOM-021 | Test / dry-run a macro | V1 -> V3 | stale | 2 | no | — |
| F-DOM-022 | Favourite macros and show them on the dashboard | V1 -> V3 | stale | 7 | no | API-20 |
| F-DOM-029 | Create, rename, reorder and delete user shortcuts | V1 -> V3 | — | 0 | no | — |
| F-DOM-030 | Favourite shortcuts and show them on the dashboard | V1 -> V3 | — | 0 | no | API-20 |
| F-DOM-031 | Dashboard layout (add, remove, reorder cards) | V1 -> V3 | stale | 2 | no | API-20, UI-08 |
| F-DOM-032 | Input/output icons, colours and display names (device settings) | V0 -> V3 | — | 0 | no | BE-16 |
| F-DOM-033 | Favourite presets and choose which presets the dashboard shows | V1 -> V3 | — | 0 | no | — |
| F-DOM-034 | Save a custom routing mapping into a preset | V2 -> V3 | fresh | 9 | no | — |
| F-DOM-035 | Theme presets and custom themes | V1 -> V3 | — | 0 | no | — |
| F-DOM-036 | UI preferences stored on the hub | V1 -> V3 | — | 0 | no | — |
| F-UI-003 | Route from the matrix card view (routing sheet) | V1 -> V3 | — | 0 | no | — |
| F-UI-007 | Overwrite a preset / save a custom mapping from the Presets drawer | V1 -> V3 | — | 0 | no | — |
| F-UI-009 | Customise the dashboard (card picker, pin, reorder) | V1 -> V3 | — | 0 | no | UI-08, API-20 |
| F-UI-010 | Inputs tab: signal/cable status and input settings (name, icon, EDID) | V1 -> V3 | — | 0 | no | — |
| F-UI-011 | Outputs tab: display status and output settings (HDCP, HDR, scaler, ARC, mute) | V1 -> V3 | — | 0 | no | — |
| F-UI-013 | Create and edit a profile in the profile editor | V1 -> V3 | — | 0 | no | — |
| F-UI-016 | Build a CEC macro in the macro editor | V1 -> V3 | — | 0 | no | — |
| F-UI-017 | CEC remote on output/input tiles and the CEC tray | V1 -> V3 | — | 0 | no | UI-12 |
| F-UI-018 | Theme presets, customisation and card opacity | V1 -> V3 | — | 0 | no | — |
| F-UI-019 | General settings: matrix host and connection test | V1 -> V3 | — | 0 | no | UI-05 |
| F-UI-020 | Hardware settings: beep, panel lock, LCD, reboot | V1 -> V3 | — | 0 | no | UI-05 |
| F-UI-021 | Interface settings | V1 -> V3 | — | 0 | no | UI-05 |
| F-UI-022 | Shortcuts drawer: run, rename, reorder | V1 -> V3 | — | 0 | no | — |
| F-UI-023 | Integrations drawer (Flic request builder, HA YAML, Remote 3 info) | V1 -> V3 | — | 0 | no | — |
| F-UI-028 | Keyboard shortcuts | V1 -> V3 | — | 0 | no | UI-06 |
| F-UI-029 | Accessibility (keyboard, focus, ARIA, contrast, zoom) | V1 -> V3 | — | 0 | no | UI-07, UI-35 |
| F-UI-030 | Debug panel | V1 -> V3 | — | 0 | no | — |
| F-UI-032 | Animated Tron background (opt-in) | V1 -> V3 | — | 0 | no | UI-16 |
| F-UI-033 | Tablet and phone layouts | V1 -> V3 | — | 0 | no | UI-33 |
| F-UI-034 | Personalise tabs in the Control Deck (pin, reorder) | V1 -> V3 | — | 0 | no | — |
| F-UI-035 | Copy an API endpoint for automation (API button / modal) | V1 -> V3 | — | 0 | no | UI-18 |
| F-UI-036 | First-run setup wizard (matrix connection) | V1 -> V3 | — | 0 | no | UI-09 |
| F-KIO-005 | Recall a preset from the kiosk | V1 -> V3 | — | 0 | no | — |
| F-KIO-006 | Configure which presets the kiosk shows (edit mode) | V1 -> V3 | — | 0 | no | UI-08 |
| F-KIO-007 | Run shortcuts from the kiosk and map them to slots | V1 -> V3 | — | 0 | no | — |
| F-KIO-009 | CEC remote in the kiosk | V1 -> V3 | — | 0 | no | — |
| F-KIO-012 | Kiosk layout and pins persist | V1 -> V3 | — | 0 | no | UI-08 |
| F-KIO-013 | Kiosk follows the selected theme | V1 -> V3 | — | 0 | no | UI-34 |
| F-KIO-014 | Kiosk touch accessibility (targets, ARIA, contrast) | V1 -> V3 | — | 0 | no | UI-07, UI-35 |
| F-SEC-001 | Optional admin / control PIN gate | V1 -> V3 | — | 12 | no | — |
| F-SEC-002 | Cross-site request protection (CORS, Origin, Content-Type, Host allow-list) | V1 -> V3 | — | 5 | no | — |
| F-SEC-003 | Matrix host changes cannot leak the matrix password (SSRF guard) | V1 -> V3 | — | 6 | no | — |
| F-SEC-004 | Profile/scene passcodes are stored as PBKDF2 hashes | V1 -> V3 | — | 2 | no | — |
| F-SEC-005 | Passcode hashes are never sent to clients | V1 -> V3 | — | 2 | no | — |
| F-SEC-006 | Changing or removing a PIN needs the current PIN | V1 -> V3 | — | 11 | no | — |
| F-SEC-007 | Wrong-PIN attempts are limited and do not stall the hub | V1 -> V3 | — | 2 | no | — |
| F-SEC-008 | Rate limiting per client | V1 -> V3 | — | 0 | no | — |
| F-SEC-009 | Proxy headers trusted only from configured proxies | V1 -> V3 | — | 0 | no | — |
| F-SEC-010 | Static files cannot escape the web root | V1 -> V3 | — | 2 | no | — |
| F-SEC-011 | Error responses do not leak internals | V1 -> V3 | — | 2 | no | — |
| F-SEC-013 | TLS certificate verification / pinning for the matrix | V1 -> V3 | — | 0 | no | — |
| F-SEC-014 | No credentials in logs | V1 -> V3 | — | 0 | no | — |

### Hardware targets: 120 below target

| Feature | Description | Level -> target | Freshness | Map | Target map | Open findings / cap |
| --- | --- | --- | --- | ---: | --- | --- |
| F-MTX-001 | Route one input to one output | V3 -> V4 | fresh | 3 | yes | — |
| F-MTX-002 | Route one input to every output | V3 -> V4 | fresh | 1 | yes | — |
| F-MTX-003 | Recall a matrix preset (1-8) | V3 -> V4 | fresh | 3 | yes | — |
| F-MTX-004 | Save the current routing to a matrix preset | V2 -> V4 | fresh | 11 | no | — |
| F-MTX-005 | Name presets in the web app (names shown by the API, UI, kiosk) | V3 -> V4 | fresh | 1 | yes | BE-16 |
| F-MTX-006 | Matrix power on / standby | V3 -> V4 | fresh | 5 | yes | — |
| F-MTX-007 | Mute / unmute the audio of an output | V1 -> V4 | fresh | 2 | yes | HIL-09; **capped HIL-09** |
| F-MTX-008 | Enable / disable an output's video stream | V1 -> V4 | stale | 5 | no | HIL-09; **capped HIL-09** |
| F-MTX-009 | Set an output's HDCP mode | V1 -> V4 | stale | 11 | no | HIL-09; **capped HIL-09** |
| F-MTX-010 | Set an output's HDR mode | V1 -> V4 | stale | 9 | no | HIL-09; **capped HIL-09** |
| F-MTX-011 | Set an output's scaler mode (incl. audio-only) | V1 -> V4 | stale | 11 | no | BE-15, HIL-09; **capped HIL-09** |
| F-MTX-012 | Enable / disable ARC on an output | V1 -> V4 | stale | 5 | no | HIL-09; **capped HIL-09** |
| F-MTX-013 | Set an input's EDID | V1 -> V4 | stale | 10 | no | HIL-09; **capped HIL-09** |
| F-MTX-014 | Copy EDID from a connected display | V1 -> V4 | stale | 11 | no | BE-25, HIL-09; **capped HIL-09** |
| F-MTX-015 | External audio: matrix mode | V1 -> V4 | stale | 9 | no | HIL-09; **capped HIL-09** |
| F-MTX-016 | External audio: enable per output | V1 -> V4 | stale | 20 | no | HIL-09; **capped HIL-09** |
| F-MTX-017 | External audio: source per output | V1 -> V4 | stale | 71 | no | HIL-09; **capped HIL-09** |
| F-MTX-018 | Front-panel beep on / off | V1 -> V4 | stale | 3 | no | — |
| F-MTX-019 | Front-panel lock | V1 -> V4 | stale | 3 | no | — |
| F-MTX-020 | Front-panel LCD timeout | V1 -> V4 | stale | 8 | no | API-07, HIL-09; **capped HIL-09** |
| F-MTX-021 | Reboot the matrix | V3 -> V4 | fresh | 3 | no | — |
| F-MTX-022 | Rename inputs (names stored on the matrix) | V1 -> V4 | stale | 6 | no | BE-16 |
| F-MTX-023 | Rename outputs (names stored on the matrix) | V1 -> V4 | stale | 6 | no | BE-16 |
| F-MTX-024 | Read the current routing and names | V2 -> V4 | stale | 4 | no | — |
| F-MTX-025 | Show which inputs have an active signal | V1 -> V4 | stale | 16 | no | — |
| F-MTX-026 | Show which cables are plugged in (Telnet link status) | V1 -> V4 | stale | 4 | no | HIL-03 |
| F-MTX-027 | Show which outputs have a display connected | V1 -> V4 | stale | 16 | no | — |
| F-MTX-028 | Show device info (model, firmware, network) | V1 -> V4 | stale | 5 | no | — |
| F-MTX-029 | Cycle an output to the next / previous input | V1 -> V4 | stale | 138 | no | — |
| F-MTX-030 | Read a preset's stored routing | V2 -> V4 | fresh | 9 | yes | — |
| F-MTX-031 | Notice changes made outside the hub (front panel, cable plugged, source on/off) | V3 -> V4 | fresh | 5 | no | — |
| F-CEC-001 | Power a source on / off over CEC | V1 -> V4 | stale | 17 | yes | — |
| F-CEC-002 | Navigate a source's menus over CEC (up/down/left/right/select/menu/back) | V1 -> V4 | stale | 56 | no | — |
| F-CEC-003 | Control playback on a source over CEC | V1 -> V4 | stale | 56 | no | — |
| F-CEC-004 | Source volume / mute over CEC | V1 -> V4 | stale | 24 | no | — |
| F-CEC-005 | Turn a display (TV) on / off over CEC | V3 -> V4 | fresh | 19 | yes | BE-14 |
| F-CEC-006 | Display / soundbar volume and mute over CEC | V1 -> V4 | stale | 25 | yes | BE-14 |
| F-CEC-007 | Enable CEC on the target port automatically before a command | V1 -> V4 | stale | 417 | yes | — |
| F-CEC-008 | Enable / disable CEC per port | V1 -> V4 | stale | 40 | no | — |
| F-CEC-009 | Read which ports have CEC enabled | V1 -> V4 | stale | 4 | no | — |
| F-CEC-010 | Send CEC over Telnet (OREI_USE_TELNET_CEC) | V1 -> V4 | stale | 206 | no | — |
| F-CEC-011 | List CEC commands and per-port capabilities (incl. audio-only outputs) | V1 -> V4 | stale | 88 | no | BE-15 |
| F-DOM-002 | Recall a profile: its routing is applied | V3 -> V4 | fresh | 4 | yes | API-19 |
| F-DOM-003 | Recall a profile: its output settings (mute, HDR, HDCP, enable) are applied | V3 -> V4 | fresh | 4 | yes | — |
| F-DOM-004 | Recall a profile: its power-on macro runs | V3 -> V4 | fresh | 1 | yes | — |
| F-DOM-011 | Run a scene: profile steps | V3 -> V4 | fresh | 6 | yes | — |
| F-DOM-012 | Run a scene: macro steps | V3 -> V4 | fresh | 4 | yes | — |
| F-DOM-020 | Run a CEC macro (steps, targets, delays) | V3 -> V4 | fresh | 4 | yes | — |
| F-UC-001 | Discover the integration and register the driver (mDNS, driver URL) | V0 -> V4 | — | 0 | no | UC-11 |
| F-UC-002 | Set up the integration on the Remote | V1 -> V4 | — | 0 | no | — |
| F-UC-003 | Reconfigure the integration (new matrix address) | V3 -> V4 | — | 0 | no | — |
| F-UC-004 | Preset buttons on the Remote | V3 -> V4 | fresh | 2 | yes | UC-28 |
| F-UC-005 | Matrix remote entity with a preset page | V3 -> V4 | fresh | 2 | yes | UC-12 |
| F-UC-006 | Per-input CEC remotes (source power, navigation, playback) | V3 -> V4 | fresh | 3 | yes | UC-12 |
| F-UC-007 | Per-output CEC remotes (TV power, volume) | V3 -> V4 | fresh | 5 | yes | BE-14 |
| F-UC-008 | Choose an output's source from the Remote (media player source list) | V3 -> V4 | fresh | 3 | yes | UC-10 |
| F-UC-009 | TV power / volume / mute from the output media player | V3 -> V4 | fresh | 2 | yes | UC-10, BE-24 |
| F-UC-010 | Matrix power switch on the Remote | V3 -> V4 | fresh | 2 | yes | — |
| F-UC-011 | Input signal and cable sensors | V1 -> V4 | — | 0 | no | UC-13 |
| F-UC-012 | Output connected, cable and source sensors | V3 -> V4 | — | 0 | no | UC-13 |
| F-UC-013 | Entities go unavailable while the matrix is unreachable | V3 -> V4 | — | 0 | no | — |
| F-UC-014 | Remote standby and wake | V3 -> V4 | — | 0 | no | — |
| F-UC-015 | Only changed attributes are sent to the Remote | V3 -> V4 | — | 0 | no | — |
| F-UC-016 | Renamed inputs/outputs show up on the Remote | V3 -> V4 | fresh | 1 | yes | UC-28, BE-16 |
| F-UC-017 | Restore the configuration at startup (also with the matrix offline) | V3 -> V4 | — | 0 | no | — |
| F-HA-001 | Add the hub in Home Assistant (config flow) | V3 -> V4 | fresh | 1 | yes | — |
| F-HA-002 | Choose each output's source (select entities) | V3 -> V4 | fresh | 2 | yes | — |
| F-HA-003 | Matrix power switch | V3 -> V4 | fresh | 2 | yes | — |
| F-HA-004 | Output audio mute switches | V3 -> V4 | fresh | 1 | yes | — |
| F-HA-005 | Output stream enable switches | V3 -> V4 | fresh | 1 | yes | — |
| F-HA-006 | Preset buttons | V3 -> V4 | fresh | 1 | yes | — |
| F-HA-007 | Reboot button | V3 -> V4 | fresh | 1 | no | — |
| F-HA-008 | Input signal binary sensors | V3 -> V4 | fresh | 1 | no | — |
| F-HA-009 | Output connected binary sensors | V3 -> V4 | fresh | 1 | no | — |
| F-HA-010 | Service hdmi_matrix.recall_preset | V3 -> V4 | fresh | 1 | yes | — |
| F-HA-011 | Service hdmi_matrix.switch_input | V3 -> V4 | fresh | 1 | yes | — |
| F-HA-012 | Service hdmi_matrix.send_cec_command | V3 -> V4 | fresh | 3 | yes | — |
| F-HA-013 | Poll the hub; entities go unavailable when it is unreachable | V3 -> V4 | fresh | 5 | no | — |
| F-HA-014 | Install through HACS (custom repository) | V1 -> V4 | — | 0 | no | — |
| F-HA-015 | Device and entity naming in Home Assistant | V3 -> V4 | fresh | 1 | yes | — |
| F-HA-016 | Change the hub address of a configured matrix (reconfigure flow) | V3 -> V4 | fresh | 1 | no | — |
| F-HA-017 | Polling interval option (options flow) | V3 -> V4 | fresh | 1 | yes | — |
| F-HA-018 | Services target one matrix (config entry or device) | V3 -> V4 | fresh | 2 | yes | — |
| F-OPS-001 | Run the hub from the Docker image | V3 -> V4 | stale | 0 | no | — |
| F-OPS-002 | Run the hub without the Remote integration (UC_ENABLED=false, the default) | V3 -> V4 | stale | 0 | no | — |
| F-OPS-003 | docker compose quick start | V3 -> V4 | stale | 0 | no | — |
| F-OPS-004 | Remote 3 discovery works from Docker | V2 -> V4 | — | 0 | no | UC-11 |
| F-OPS-005 | Container health check and auto-restart | V3 -> V4 | stale | 0 | no | — |
| F-OPS-006 | Point the hub at the matrix (MATRIX_HOST / MATRIX_PORT) | V3 -> V4 | stale | 0 | no | DEP-07, BE-26 |
| F-OPS-007 | Choose the API port (API_PORT) | V2 -> V4 | — | 0 | no | DEP-07 |
| F-OPS-008 | Matrix credentials (OREI_USER / OREI_PASSWORD) | V1 -> V4 | — | 0 | no | — |
| F-OPS-009 | Verify the matrix TLS certificate (OREI_VERIFY_SSL) | V0 -> V4 | — | 0 | no | — |
| F-OPS-010 | Log level (LOG_LEVEL) | V1 -> V4 | — | 0 | no | — |
| F-OPS-011 | Enable/disable integrations (UC_ENABLED) | V3 -> V4 | stale | 0 | no | DEP-07, BE-20 |
| F-OPS-012 | Background polling (POLLING_ENABLED / POLLING_INTERVAL) | V0 -> V4 | — | 0 | no | TST-03 |
| F-OPS-013 | Telnet options (OREI_TELNET_PORT, OREI_USE_TELNET_CEC) | V1 -> V4 | — | 0 | no | — |
| F-OPS-014 | Cache and retry tuning (OREI_STATUS_CACHE_TTL, OREI_CEC_CACHE_TTL, OREI_*RETR*) | V1 -> V4 | — | 0 | no | — |
| F-OPS-015 | Hub data persists across restarts (DATA_DIR) | V3 -> V4 | stale | 0 | no | DEP-07 |
| F-OPS-016 | Writes are atomic and safe under concurrency | V1 -> V4 | — | 0 | no | — |
| F-OPS-017 | Migrate legacy data files (scenes -> profiles) | V1 -> V4 | — | 0 | no | API-12, PER-04 |
| F-OPS-018 | Only one hub instance runs (process lock) | V1 -> V4 | — | 0 | no | — |
| F-OPS-019 | One consistent version everywhere | V1 -> V4 | — | 0 | no | — |
| F-OPS-020 | Multi-arch images (amd64 + arm64) | V0 -> V4 | — | 0 | no | — |
| F-REL-001 | Reconnect automatically after a matrix outage | V3 -> V4 | fresh | 3 | no | — |
| F-REL-002 | Report the connection state truthfully on errors and timeouts | V0 -> V4 | — | 0 | no | — |
| F-REL-003 | Detect a wrong matrix password | V0 -> V4 | — | 0 | no | — |
| F-REL-004 | Log in again when the matrix session expires | V0 -> V4 | — | 0 | no | — |
| F-REL-005 | Recover after the matrix reboots or is power-cycled | V3 -> V4 | fresh | 3 | no | — |
| F-REL-006 | Detect a dropped Telnet connection and reconnect | V0 -> V4 | — | 0 | no | — |
| F-REL-007 | Shut down and disconnect cleanly | V0 -> V4 | — | 0 | no | — |
| F-REL-008 | A command the matrix rejects is reported as failed | V0 -> V4 | stale | 1 | no | — |
| F-REL-009 | Matrix unreachable: commands fail visibly and no state is made up | V3 -> V4 | fresh | 3 | no | — |
| F-REL-010 | Status stays fresh (caches expire, one refresh at a time) | V1 -> V4 | — | 0 | no | — |
| F-REL-011 | API calls are not blocked while the hub reconnects | V0 -> V4 | — | 0 | no | — |
| F-REL-012 | Background polling keeps state live without a Remote connected | V3 -> V4 | fresh | 1 | no | — |
| F-REL-013 | The event loop never stalls (loop-lag metric) | V1 -> V4 | — | 0 | no | — |
| F-REL-014 | A slow WebSocket client cannot stall commands | V2 -> V4 | — | 0 | no | — |
| F-REL-015 | Tolerate slow and malformed matrix responses | V1 -> V4 | — | 0 | no | — |
| F-REL-016 | Standby does not start reconnect storms or duplicate pollers | V0 -> V4 | — | 0 | no | — |
| F-REL-017 | No leaked sessions, sockets or tasks after reconfiguration | V0 -> V4 | — | 0 | no | — |

### Field target: one below target

| Feature | Description | Level -> target | Freshness | Map | Target map | Open findings / cap |
| --- | --- | --- | --- | ---: | --- | --- |
| F-REL-018 | 72-hour soak with flat memory, tasks and sockets | V0 -> V5 | — | 0 | no | — |

### Numerically at target: 58, with freshness caveats

| Feature | Description | Level -> target | Freshness | Map | Target map | Open findings / cap |
| --- | --- | --- | --- | ---: | --- | --- |
| F-API-008 | POST /api/preset/{preset}/save | V2 -> V2 | fresh | 17 | yes | — |
| F-API-013 | System setting routes (beep, panel lock, LCD, reboot) | V3 -> V2 | fresh | 3 | yes | — |
| F-API-020 | Scene v1 alias routes (/api/scene*, /api/scenes) | V2 -> V2 | fresh | 68 | yes | API-12 |
| F-API-021 | Scene v2 routes (/api/v2/scenes*) | V2 -> V2 | stale | 44 | yes | TST-03 |
| F-API-029 | Web UI, kiosk and static asset routes | V3 -> V3 | — | 0 | no | — |
| F-API-032 | WebSocket /ws: welcome, status snapshot, get_status, matrix link, errors | V3 -> V2 | fresh | 4 | yes | — |
| F-API-036 | WS event audio_mute | V2 -> V2 | stale | 2 | yes | — |
| F-API-037 | WS events device_settings / device_settings_full | V2 -> V2 | fresh | 1 | yes | — |
| F-API-038 | WS event cec_command | V2 -> V2 | stale | 1 | yes | — |
| F-API-039 | WS status snapshot (after connect, after a first reading, get_status) | V2 -> V2 | — | 0 | no | — |
| F-API-040 | WS live matrix events from the hub's own poller (routing, power, signal, display, cable, mute, names) | V3 -> V2 | fresh | 5 | yes | BE-24 |
| F-API-041 | WS event scene_execution_error | V2 -> V2 | fresh | 1 | yes | — |
| F-API-042 | WS heartbeat (ping / pong) | V2 -> V2 | — | 0 | no | — |
| F-DOM-005 | Protect a profile with a passcode (per-item PIN) | V3 -> V3 | fresh | 5 | yes | — |
| F-DOM-013 | Run a scene: wait and shortcut steps | V3 -> V3 | fresh | 2 | yes | — |
| F-DOM-014 | Scene overrides (per-run changes to a profile step) | V3 -> V3 | fresh | 4 | yes | — |
| F-DOM-015 | Protect a scene with a passcode | V3 -> V3 | fresh | 2 | yes | — |
| F-DOM-016 | Validate a scene and detect conflicting steps | V3 -> V3 | fresh | 2 | yes | — |
| F-DOM-017 | Scene execution history | V3 -> V3 | fresh | 1 | yes | — |
| F-DOM-023 | Built-in shortcuts: route all to an output, one-to-one routing | V3 -> V3 | fresh | 3 | yes | — |
| F-DOM-024 | Built-in shortcut: power everything off | V3 -> V3 | fresh | 1 | yes | — |
| F-DOM-025 | Built-in shortcuts: mute / unmute all outputs | V3 -> V3 | fresh | 3 | yes | — |
| F-DOM-026 | Built-in shortcuts: recall preset 1-8 | V3 -> V3 | fresh | 1 | yes | — |
| F-DOM-027 | Built-in shortcuts: beep, panel lock, reboot | V3 -> V3 | fresh | 9 | yes | — |
| F-DOM-028 | Built-in shortcuts: LCD timeout | V3 -> V3 | fresh | 6 | yes | API-07 |
| F-UI-001 | Open the web UI; the header shows the matrix connection | V3 -> V3 | — | 0 | no | — |
| F-UI-002 | Route by clicking a cell in the matrix grid | V3 -> V3 | fresh | 1 | yes | — |
| F-UI-004 | Route one input to every output from the Route To All drawer | V3 -> V3 | fresh | 1 | yes | — |
| F-UI-005 | Recall a preset from the Presets drawer | V3 -> V3 | fresh | 1 | yes | — |
| F-UI-006 | Rename a preset in the Presets drawer | V3 -> V3 | fresh | 1 | yes | — |
| F-UI-008 | Run profiles, scenes, presets, shortcuts and macros from dashboard cards | V3 -> V3 | fresh | 1 | yes | — |
| F-UI-012 | Profiles tab and profile manager | V3 -> V3 | fresh | 1 | yes | — |
| F-UI-014 | Run a passcode-protected profile (passcode prompt) | V3 -> V3 | fresh | 3 | yes | UI-36 |
| F-UI-015 | Build a scene in the scene editor | V3 -> V3 | — | 0 | no | UI-19 |
| F-UI-024 | Live updates when another client or the matrix changes something | V3 -> V3 | fresh | 5 | yes | — |
| F-UI-025 | Reconnect and resync after the WebSocket drops | V3 -> V3 | — | 0 | no | — |
| F-UI-026 | Show an error state when the matrix is unreachable | V3 -> V3 | — | 0 | no | — |
| F-UI-027 | Toasts and confirmation dialogs | V3 -> V3 | fresh | 1 | yes | — |
| F-UI-031 | About dialog | V3 -> V3 | — | 0 | no | — |
| F-KIO-001 | Open the kiosk; it shows the matrix connection | V3 -> V3 | — | 0 | no | — |
| F-KIO-002 | Route a source to one display with the routing wizard | V3 -> V3 | fresh | 1 | yes | — |
| F-KIO-003 | Route a source to every display from the kiosk | V3 -> V3 | fresh | 1 | yes | — |
| F-KIO-004 | Input and output status tiles | V3 -> V3 | — | 0 | no | — |
| F-KIO-008 | Run profiles from the kiosk; create one with the profile wizard | V3 -> V3 | fresh | 2 | yes | — |
| F-KIO-010 | Kiosk live updates | V3 -> V3 | fresh | 2 | yes | — |
| F-KIO-011 | Kiosk disconnected state | V3 -> V3 | fresh | 1 | yes | — |
| F-FLIC-001 | Button click recalls a preset | V3 -> V3 | fresh | 1 | yes | — |
| F-FLIC-002 | Button hold powers the matrix off / on | V3 -> V3 | fresh | 2 | yes | — |
| F-FLIC-003 | Button powers a source on over CEC | V3 -> V3 | fresh | 1 | yes | — |
| F-FLIC-004 | Flic Twist cycles an output through its inputs | V3 -> V3 | fresh | 3 | yes | — |
| F-FLIC-005 | Flic Twist controls TV volume and mute over CEC | V3 -> V3 | fresh | 2 | yes | BE-14 |
| F-FLIC-006 | Button recalls a profile or runs a macro | V3 -> V3 | fresh | 5 | yes | — |
| F-FLIC-007 | Register Flic buttons with the hub (button registry) | V3 -> V3 | fresh | 1 | yes | — |
| F-FLIC-008 | Button switches every output to input N (POST /api/switch with JSON input) | V3 -> V3 | fresh | 1 | yes | — |
| F-FLIC-009 | Flic Hub SDK JavaScript module templates | V3 -> V3 | fresh | 9 | yes | — |
| F-FLIC-010 | Generate Flic request URLs in the web UI | V3 -> V3 | fresh | 16 | yes | — |
| F-SEC-012 | User-provided names are escaped in the UI (no XSS) | V3 -> V3 | — | 0 | no | — |
| F-SEC-015 | Remote 3 integration port requires authentication | V3 -> V3 | — | 0 | no | — |

## Scope kept separate from this inventory

- The accepted source/image software campaign and its negative historical
  findings remain attached to their actual commits and digests. Read-only
  inventory is not fresh runtime verification or full model qualification.
- Current-head CI status and the three owner Tron decisions are separate
  checklist items. This document neither approves snapshots nor predicts
  the result of in-progress or future CI.
- Physical Flic, owner HA/LAN, Remote firmware, real arm64 hardware and the
  exact supported HA-version floor retain their documented limits. An
  at-target Flic V3 row is request-replay proof, not physical-button proof.
- The red conditional alternate-disconnect reproduction remains preserved;
  this inventory does not expand the supported Orei guarantee or infer a
  new supported defect from that unchanged conditional case.
- RC/final tag order, canonical final version and matching rebuilt artifact
  proof follow the [release checklist](RELEASE_VALIDATION_CHECKLIST.md) and
  master plan. No merge, tag, hardware action or field run occurred here.
