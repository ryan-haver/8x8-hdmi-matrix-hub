# Matrix status and input cycling simulator proof

`wp-matrix-status-cycling-validation` adds 183 REST scenarios for six matrix
features and records them against the verified packaged image. Application
code is unchanged. The batch contains 45 read scenarios and 138 cycling
scenarios, checking independently seeded simulator state, API responses,
unchanged unrelated settings and protocol warnings.

| Feature | Proof |
| --- | --- |
| F-MTX-024 | Mixed, one-to-one and uniform routes, all eight input/output names, exactly eight formatted routing entries |
| F-MTX-025 | Active/inactive signal on each input, raw `inactive` codes, inverse cable state to keep signal and cable detection distinct |
| F-MTX-026 | All/none and alternating cable patterns on both sides, Telnet availability, no writes |
| F-MTX-027 | Display connected/disconnected on each output, raw `allconnect`, inverse stream enable to distinguish connection from stream state |
| F-MTX-028 | Device/firmware/network readback, both DHCP flags, on/standby system fields and separate hub runtime information |
| F-MTX-029 | Next/previous from every input on each output (128 combinations), default output and wraparound, invalid output requests and device refusals |

Successful cycling requires the exact `video switch` payload, one command,
independent device readback, matching REST routing, and a WebSocket routing
announcement. Invalid requests require HTTP 400 and no write. Persistent
refusals require HTTP 500, two command attempts (one re-login/retry), unchanged
state and no routing announcement. Source reads reset the simulator and sync
the hub before the action; they test readback, not physical signal detection.

The source smoke run passed the 147 routing/device/system/cycling checks. Its
36 port-array expectations initially failed because the framework compares
lists exactly, while these expectations supplied partial port dictionaries.
The corrected scenarios use explicit field checks and exact raw arrays. Their
rerun also identified a harness readiness prerequisite: HTTP health can be
ready before Telnet. The harness now waits for connected HTTP and Telnet before
these cable-dependent checks. All 36 corrected checks pass. Neither smoke
issue required an application change or constitutes device failure evidence.

The [run summary](evidence/F-MTX-024/2026-10-01-matrix-status/run-summary.json)
contains 183 passing V2 API records. The
[identity/schema audit](evidence/F-MTX-024/2026-10-01-matrix-status/audit.json)
confirms clean source and the measured image ID on every record. Source:
`31f5c05af505d010aa90aaad61798e45ef2e5ef6`. Image: `hdmi-matrix-hub:wp-simulator-evidence-refresh`,
`sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0`.
All 176 application, web, runtime and requirement files match the checkout
after line-ending normalization, so the retained image remains applicable.

The implementation commit hook passed Ruff and **1,605 backend tests**, with
3 skipped and 26 deselected, in 330.27 seconds. Strict route coverage is
**163/163 (100%)**. The evidence commit also runs the mandatory hook. The
[ledger/gate snapshot](evidence/F-MTX-024/2026-10-01-matrix-status/ledger-check.json)
reports **128 features with fresh passing evidence**, up from 122, and **zero
stale features**. Five features gain V2, while F-MTX-024 retains its V2 level.
Levels are V0 27, V1 105, V2 44 and V3 92; 217 features remain below target.
Recorded baselines, hardware caps and findings are unchanged; HIL-03 remains
open on cable detection. C0 remains incomplete.

The [reproduction bundle](evidence/F-MTX-024/2026-10-01-matrix-status/REPRODUCE.md)
retains the selection, isolated stack, record runner, audit and ledger helpers.
The stack uses fresh fixture data, HTTP/Telnet readiness checks and device state
resets. Evidence filenames use UTC 2026-10-02; the handoff uses local session
date 2026-10-01. Proof containers, network and data volume were removed; the
work container is removed after committing. Images and ignored caches remain.

`GET /api/inputs` and `/api/outputs` are name catalogs; signal and connection
proof here uses `/api/status/inputs` and `/api/status/outputs`. `/api/system/info`
reports hub runtime information; device information comes from
`/api/status/device`. The preset endpoint returns hub-saved routing and is
outside this batch. Real displays/signals, physical cable detection, Flic
hardware, concurrent cycling and other clients remain separate proof.

Next: reconcile preset routing semantics, then remaining CEC simulator gaps.
Owner-present hardware proof, WP-C4 scene visual approval and the SEC-01-03
release-gate decision remain pending.
