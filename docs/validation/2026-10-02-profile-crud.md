# Profile CRUD and visibility baseline

`wp-profile-crud-validation` records **51 packaged-image API scenarios:
49 pass and two fail**, both linked to the existing medium-severity API-22
finding. Application code is unchanged. C0 records failures before remediation
([validation plan](VALIDATION_PLAN.md#5-campaigns)).

The passing cases cover profile creation with defaults, all eight matching
input/output port pairs, explicit enable/mute/HDR/HDCP settings and macro/CEC
assignments. Creation over an existing ID replaces its name/output mapping.
Editing verifies metadata, output replacement, assignments and clearing macro
references. Missing IDs, required create fields, empty/unknown-only edits,
and input/output boundaries on creation return the expected errors. Deletion
is followed by a separate missing-profile read.

Visibility checks exercise both directions of favorite/dashboard toggles and
explicit boolean sets, missing fields/profiles, direct pin editing, reorder,
empty reorder and partial reorder with missing IDs. A favorite list excludes
nonfavorites and sorts by pin order then case-insensitive name. Checks verify
exact list lengths for those fixture cases. Temporary profiles are removed
by cleanup. Every record has an unchanged matrix snapshot and no matrix write.

The **two API-22 failures** request `scaler_mode: 4` and `arc: true`, once
through creation and once through editing. Both requests return HTTP 200,
but separate reads omit those fields. Each record retains exactly one failed
round-trip expectation, linked to API-22; all other checks pass. The existing
finding stays open, now with packaged-image evidence. This batch does not
recall these profiles or measure scaler/ARC effects on hardware.

The [summary](evidence/F-DOM-001/2026-10-02-profile-crud/run-summary.json)
and [audit](evidence/F-DOM-001/2026-10-02-profile-crud/audit.json) retain all
outcomes. Source: `0b9cbe878608cff9780edf42fe8c0efd4a90668d`. Image:
`hdmi-matrix-hub:wp-simulator-evidence-refresh`,
`sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0`.
It matches all 176 application/web/runtime/dependency files after line-ending
normalization. Every record validates against the evidence schema and has
clean source and the measured image identity. UC is disabled; actual Docker
configuration verifies `OREI_USE_TELNET_CEC=false`.

Ruff and **1,605 backend tests** passed through the source commit hook in
371.38 seconds (3 skipped, 26 deselected), with strict route coverage
**163/163 (100%)**. The evidence commit runs the same mandatory hook.
The [ledger snapshot](evidence/F-DOM-001/2026-10-02-profile-crud/ledger-check.json)
reports **139 fresh passing features**, **five fresh failing features** and
**zero stale features**. F-DOM-001 and F-DOM-006 gain their first committed V2
proof. Levels: V0 27, V1 94, V2 55 and V3 92. F-API-019 retains its SEC-04 cap.
Fresh failures affect F-DOM-001/F-API-019 (API-22), F-MTX-030 (BE-36), and
F-CEC-010/F-API-015 (BE-37). The gate accepts linked failures; it does not
establish that these features are fixed. API-20 remains open: visibility flag
readback does not prove dashboard layout reconciliation.

This is running-hub API readback. Browser behavior, restart persistence,
storage-failure behavior, pin-capacity policy, description handling and
exhaustive malformed/type/range checks on edits are outside this batch.
The [reproduction bundle](evidence/F-DOM-001/2026-10-02-profile-crud/REPRODUCE.md)
creates disposable fixture data and removes its own stack resources. The work
container is removed after committing. Images and ignored build helpers remain.

Next: per-profile CEC targets/auto-resolve, execution history and save-current
routing. C0 remains incomplete. API-22/BE-36/BE-37 remediation, owner-present
hardware checks, WP-C4 visual approval and the SEC-01-03 release-gate decision
remain pending.
