# Scene and macro management baseline

`wp-domain-management-validation` records **117 packaged-image API scenarios:
116 pass and one fails**, linked to the new medium-severity API-28 finding.
Application code is unchanged. C0 records failures before remediation
([validation plan](VALIDATION_PLAN.md#5-campaigns)).

The **71 macro checks** cover creation, replacement, reads, metadata/step
edits, deletion, missing IDs, favorite/dashboard toggles and favorite list
ordering. Validation covers invalid names, step shapes, commands, target
shapes and ports, source/display command restrictions, step/target count
limits and delay types/ranges. Invalid updates preserve the prior name and
steps. Accepted boundaries include 200-character names, 2000-character
descriptions, 100 steps, 16 targets and 60000 ms delays. Lowercase command
input is accepted. A 25-step sequence represents all 19 source commands
and six display commands. Its dry-run reports 25 steps, no issues and a
1500 ms duration; complete saved steps remain unchanged. Command logs
confirm that neither management nor dry-run sends CEC commands.

The **44 scene checks** cover list/read, creation with profile/macro/system/
wait steps, metadata/step edits, add/remove, overrides and deletion. Invalid
requests include malformed bodies/steps, unknown types, missing profile
IDs, duplicate profiles, protected profiles without a passcode and invalid
wait durations. Failed creates preserve the collection count; failed edits
preserve prior name/steps. Wait boundaries 0.5 and 30 seconds are accepted.
The audit matches the generated scene ID and complete step list against
independent list readback. The final fixture deletion returns a missing
read for Good Night while Movie Night remains available.

The **two legacy alias checks** cover list and recall with independent
canonical readback. Recall actually routes Output 1 to Input 5; this is
the only scenario that changes matrix state. All other 116 records retain
identical before/after state. No real hardware is contacted.

**API-28:** a macro description edit of 2001 characters returns HTTP 200
success and persists the oversized value, while POST rejects the same
length. The record retains exactly two failed safeguards: HTTP 400
rejection and preservation of the previous description. API-28 is linked
to F-DOM-019/F-API-023 and remains open under C0. Passing cases provide V2
proof without establishing that every macro validation path is correct.

The [summary](evidence/F-DOM-019/2026-10-02-domain-management/run-summary.json)
and [audit](evidence/F-DOM-019/2026-10-02-domain-management/audit.json) retain
all outcomes. Source: `1aafbbf4ec1d4d1897ec4b7ee19d1602082584a5`. Image:
`hdmi-matrix-hub:wp-simulator-evidence-refresh`,
`sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0`.
It matches all 176 application/web/runtime/dependency files after line-ending
normalization. Actual Docker configuration verifies UC disabled and
`OREI_USE_TELNET_CEC=false`; the default status cache TTL is retained.
All records have valid schemas, clean source, measured image identity
and no not-applicable checks. All recorded cleanup requests return HTTP 200.

Ruff and **1,605 backend tests** passed through the source commit hook in
371.54 seconds (3 skipped, 26 deselected), with strict route coverage
**163/163 (100%)**. The evidence commit runs the same mandatory hook.
The [ledger snapshot](evidence/F-DOM-019/2026-10-02-domain-management/ledger-check.json)
reports **150 fresh passing features**, **nine fresh failing features** and
**zero stale features**. F-DOM-018/019/021/022 and F-API-023 gain their first
committed V2 proof. Levels: V0 26, V1 86, V2 64 and V3 92. Fresh failures
remain linked to API-22, API-27, API-28, BE-36 and BE-37. High-severity caps
are retained. The gate accepts linked failures; it does not establish fixes.

The [reproduction bundle](evidence/F-DOM-019/2026-10-02-domain-management/REPRODUCE.md)
uses fresh disposable data and removes its own stack resources. The selection
must run sorted on fresh hub fixtures: rejected creates precede the one
successful create, and deletion runs last. The generated scene and fixture
deletion live only in the disposable volume. Other scene edits are restored
and temporary macros/profiles are deleted. The work container is removed
after committing. Images and ignored build helpers remain.

Browser rendering, restart persistence, storage failure handling, scene
execution and physical CEC effects are outside this batch. API-20 dashboard
layout semantics remain open. Next: remaining simulator domain gaps and
management browser proof. C0 remains incomplete; finding remediation,
owner-present hardware checks, WP-C4 visual approval and the SEC-01-03
release-gate decision remain pending.
