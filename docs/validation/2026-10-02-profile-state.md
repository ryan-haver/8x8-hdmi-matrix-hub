# Profile CEC, execution history and capture-current baseline

`wp-profile-state-validation` records **108 packaged-image API scenarios:
106 pass and two fail**, both linked to the new medium-severity API-27
finding. Application code is unchanged. C0 records failures before remediation
([validation plan](VALIDATION_PLAN.md#5-campaigns)).

The **66 CEC configuration checks** cover canonical and legacy scene aliases,
POST/PUT, manual/empty/wrapped configurations, missing profiles and invalid
list/boolean/key shapes. Invalid writes preserve the previous configuration.
Explicit input/output targets are saved and read on all eight ports. The
**16 resolver checks** cover every port, audio-only over ARC priority,
multiple audio targets, ARC and default selection, disconnected outputs,
all-disabled profiles and a missing profile. Navigation chooses the lowest
active input; disabled outputs are excluded from all target lists. Literal
expected targets are compared with both the response and independent readback.
Target-string semantics and the API-25 format gap remain outside this proof.

The **six history checks** cover empty/missing profiles, separate reads after
scene execution, successful/failed execution and two entries in append order.
Entries name the scene that produced them, carry success/error and include
timestamps; the audit verifies UTC-aware times within each run, count/list
agreement, ordering and error content in all four populated cases. History
is produced by v2 scene profile steps. Seven-day expiry and persistence across
restart are not exercised. The edited fixture scene is restored afterward;
its generated scene history exists only in disposable fixture data.

The **nine healthy capture checks** include eight routing patterns covering
all 64 output/input pairs, with mixed mute, raw HDR and HDCP values on all
outputs. Stored HDR uses API values 1-3 for raw device values 0-2. Independent
reads equal the complete expected eight-output mapping; the audit recomputes
it from the pre-action device snapshot. A defaults check verifies the default
name/icon. All patterned outputs are enabled. The **nine alias checks** cover
create/read/list/delete/recall and missing/invalid requests, with canonical
readback and real matrix routing for recall.

The **two API-27 failures** inject HTTP 500 for output status or video status.
Both save-current requests return HTTP 200 success and create a profile. An
output-read failure saves an empty output map; a video-read failure saves
Input 1 on every output despite different device routing. Each record retains
exactly two failed safeguards, linked to API-27: reporting HTTP 502 failure
and leaving the profile absent. Matrix state stays unchanged. API-27 remains
open under C0; these records prove incomplete/fabricated capture data in software.

The [summary](evidence/F-DOM-007/2026-10-02-profile-state/run-summary.json)
and [audit](evidence/F-DOM-007/2026-10-02-profile-state/audit.json) retain all
outcomes. Source: `ed4cb0fb7876a468fc54b64eef420bd851c4fc38`. Image:
`hdmi-matrix-hub:wp-simulator-evidence-refresh`,
`sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0`.
It matches all 176 application/web/runtime/dependency files after line-ending
normalization. Every record has clean source, the measured image identity and
a valid schema. Actual Docker configuration verifies UC disabled,
`OREI_USE_TELNET_CEC=false` and **`OREI_STATUS_CACHE_TTL=0`**. Disabling caching
ensures device reads/faults are observed; normal-cache behavior is not proven.

Ruff and **1,605 backend tests** passed through the source commit hook in
427.44 seconds (3 skipped, 26 deselected), with strict route coverage
**163/163 (100%)**. The evidence commit runs the same mandatory hook.
The [ledger snapshot](evidence/F-DOM-007/2026-10-02-profile-state/ledger-check.json)
reports **143 fresh passing features**, **seven fresh failing features** and
**zero stale features**. F-DOM-007/008/009 and F-API-020 gain their first
committed V2 proof. Levels: V0 26, V1 91, V2 59 and V3 92. F-API-019 retains
its SEC-04 cap. Fresh failures are API-22 on F-DOM-001/F-API-019, API-27 on
F-DOM-009/F-API-020, BE-36 on F-MTX-030, and BE-37 on F-CEC-010/F-API-015.
The gate accepts linked failures; it does not establish that they are fixed.

The [reproduction bundle](evidence/F-DOM-007/2026-10-02-profile-state/REPRODUCE.md)
uses fresh disposable data and removes its own stack resources. The work
container is removed after committing. Images and ignored build helpers remain.
Browser behavior, restart persistence, aged history expiry, physical CEC
effects and disabled-stream capture are outside this batch.

Next: remaining scene/domain simulator gaps. C0 remains incomplete.
API-22/API-27/BE-36/BE-37 remediation, owner-present hardware checks,
WP-C4 visual approval and the SEC-01-03 release-gate decision remain pending.
