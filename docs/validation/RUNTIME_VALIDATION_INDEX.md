# Runtime validation index

This index tracks the final integrated software campaign and separates its code candidate from the documentation archive commit. It summarizes coordinator-supplied evidence; use the linked records for original scopes, timestamps, artifact roots, and hashes.

## Candidate and evidence archive

| Item | Revision or result |
| --- | --- |
| Tested runtime and image source | [`4adbc136a4c1fb6be4b20b58530a47dd521efac8`](runs/runtime/manifest.json), clean tracked checkout, version `1.0.0rc1` |
| Documentation and evidence archive | [`b69a012811c7db13ddb2b1cd9bd0f84199a6954d`](RUNTIME_VALIDATION_REPORT.md); archive preserves original evidence bytes and history |
| Integrated formal evidence gate | [Passed, exit 0](runs/runtime/formal-gate.txt), with zero known failures linked to open findings; [context](runs/runtime/formal-gate-context.json) records source, image, deployment roots and 5 client types |
| Registry and ledger pytest checks | 26 passed within the complete core suite ([JUnit](runs/runtime/final-source-rerun.xml)); the formal gate separately checks evidence relationships and open findings |
| Feature and client ledger | See the [existing ledger](LEDGER.md), which retains feature-level targets and provenance |
| Full coordinator report | [Runtime validation report](RUNTIME_VALIDATION_REPORT.md) |

The tested runtime SHA is the code commit; `b69a012` is the documentation/evidence archive, not a new campaign run. Earlier candidate results and failures remain attached to their original revisions in the [archive manifest](runs/runtime/manifest.json) and report.

## Fresh software evidence

| Scope | Result | Evidence |
| --- | --- | --- |
| Core including installed-package entry checks | 3,966 passed, 4 skipped, 31 deselected; Windows local run, excludes HA component and dedicated UC suites | [JUnit](runs/runtime/final-source-rerun.xml), [manifest](runs/runtime/manifest.json) |
| Scripted Remote suite | 100 passed, no skips; SDK and simulator, no physical Remote claim | [JUnit](runs/runtime/final-uc.xml) |
| Built amd64 deployment | 26 passed, 3 explicit skips; normal image command, health, SDK/discovery/volume/context checks | [JUnit](runs/runtime/final-amd64-deploy.xml) |
| Source API/browser/UC/Flic campaigns | API 1,411; browser 54; UC 18; Flic 23 passed | [summary](runs/runtime/source-campaigns.json) |
| Source Home Assistant containers | 19 passed on 2026.9.3; 19 passed on 2025.1.4 | [current](runs/runtime/source-ha-current.json), [minimum supported line](runs/runtime/source-ha-minimum-line.json); 2025.1.4 does not certify the exact 2025.1.0 floor |
| amd64 image client campaigns | API 79, browser 54, Flic 23, HA 19, UC 18 passed (193 passing outcomes total) | [cached](runs/runtime/image-campaigns-cached.json), [fresh](runs/runtime/image-campaigns-fresh.json), [HA cached](runs/runtime/image-ha-campaigns-cached.json), [HA fresh](runs/runtime/image-ha-campaigns-fresh.json), [Remote](runs/runtime/image-uc-campaigns.json), [milestones](runs/runtime/milestone-records.json) |
| Source UI browser flows | 59 expected; zero unexpected, flaky, or skipped | [flow outcomes](runs/runtime/source-flows-results.json) |
| REST route coverage | 177/177 for the enabled configuration | Route coverage log path and scope in [manifest](runs/runtime/manifest.json) |
| Swagger rendering/catalog | 177 operations with Flic enabled; 175 with Flic disabled; online and CDN blocked, no page errors or persisted synthetic admin PIN | [enabled](runs/runtime/swagger-flic-true.json), [disabled](runs/runtime/swagger-flic-false.json), [image summary](runs/runtime/final-swagger-image.json) |
| Application images | amd64 `sha256:1a5de3b5b58a3e1c56d3269bd5c1c6e3e12be2d6fea1abceea36067d733df69e`; arm64 `sha256:a8ebd6f1a017322ff514e2051f1153f35d1ed0762034797ba4dbb2b6826668c6` | [amd64](runs/runtime/final-amd64-image.json), [arm64](runs/runtime/final-arm64-image.json) |
| Shipped input parity | Both images match all 257 tracked shipped input bytes; final archive audit matched all 213 hash-indexed evidence/supplemental files | [image parity](runs/runtime/final-image-input-parity.json), [manifest](runs/runtime/manifest.json) |
| arm64/QEMU smoke | Offline startup, canonical metadata, Docker health, graceful SIGTERM passed; no device action claim | [smoke record](runs/runtime/final-arm64-smoke.json) |

Image campaign counts are scenario/client outcomes, not unique features. Forty-two declared client-exclusion assertions remain `n/a`, verified against scenario definitions; they are not passes. Swagger results prove route catalog rendering, not execution of every handler in the disabled configuration. The source HA runs use actual disposable containers, not the owner's HA deployment. Flic replay uses a Node SDK stub and simulator-backed hub; scripted UC tests use the SDK/simulator. Neither proves physical device behavior. SDK 0.7 does not advertise optional select entities, and direct dispatcher cycling is not Remote WebSocket cycle evidence.

The formal gate checks evidence relationships and registry/ledger consistency; it does not elevate software results to hardware or field acceptance. Historical failures remain recorded as failures. In particular, the earlier 55d4fe0 image campaign and the original HA 17-pass/two-failure result were not rewritten; the report documents their correction and later clean campaign.

## CI and remaining gates

Coordinator-reported CI for `4adbc136` has 12/13 required checks passing; the remaining check has the three Tron paused-frame visual failures (main UI: 1,098 passed, 33 skipped, 3 visual failures; gallery: 62 passed). See the [CI run](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/actions/runs/39206732559). Owner visual acceptance is pending. Independent R8 review, PR checks and approved merge/tag sequence are pending.

Physical BK-808/matrix and CEC behavior, physical Remote and Flic operation, owner-deployed HA and physical LAN discovery, HIL-B/C/E, the HIL-D continuous 72-hour soak, and the owner's week-of-daily-use sign-off remain pending. The [field runbook](RUNTIME_FIELD_GATE_RUNBOOK.md) specifies owner execution and evidence. Final `1.0.0` metadata, rebuild and release publication remain future gates; these local RC1 images are not published tags.

See the [validation plan](VALIDATION_PLAN.md), [field runbook](RUNTIME_FIELD_GATE_RUNBOOK.md), and [complete runtime report](RUNTIME_VALIDATION_REPORT.md) for full scope, caveats and historical evidence.
