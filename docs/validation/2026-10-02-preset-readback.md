# Preset routing readback: BE-36 baseline evidence

`wp-preset-readback-validation` records 24 packaged-image API scenarios:
**16 pass and eight fail**, all failures linked to the new medium-severity
BE-36 finding. Application code is unchanged. The C0 campaign records failures
before remediation, as described in [the validation plan](VALIDATION_PLAN.md#5-campaigns).

The gap is in `GET /api/presets`: `routing` comes from the hub's device-settings
cache, without a Telnet `r preset N` query. Every independently seeded device
slot has a complete eight-output mapping, but the API reports the fixture's
empty or partial hub mapping. Both device-read expectations fail for every
slot: correct routing and a Telnet preset query. All other checks pass,
including HTTP 200, independent device state, unchanged matrix and no
unsupported HTTP `preset get` or `get routing status` commands.

This proves the API does not read independently stored preset routing. It
also explains why an external preset edit cannot be reflected in that catalog;
live external changes and clears were not exercised in this batch. Telnet-only
driver tests remain the existing V1 proof. F-MTX-030 receives only the eight
failure records and stays at **V1**; cache reads are not treated as device
readback proof.

The passing scenarios exercise all eight slots in two ways. A current-routing
save stores a full device slot and full hub mapping, and the catalog reads that
mapping. A partial custom save stores a full device slot while the API returns
only the submitted mapping, with live routes restored after saving. The read
actions send no writes or preset query and preserve all device state. These
16 passes link to the save features F-MTX-004, F-DOM-034 and F-API-008. The latter two gain V2 from their first committed scenario evidence.

The [run summary](evidence/F-MTX-030/2026-10-02-preset-readback/run-summary.json)
and [audit](evidence/F-MTX-030/2026-10-02-preset-readback/audit.json) retain the
actual failed outcomes and checks. Source: `f4f417bfed08303c1b0cb38bc0af92eb0dbec999`. Image:
`hdmi-matrix-hub:wp-simulator-evidence-refresh`,
`sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0`.
All records have clean source and the measured image identity. The retained
image matches all 176 application, web, runtime and requirement files after
line-ending normalization.

Ruff and **1,605 backend tests** passed through the implementation commit hook,
with 3 skipped and 26 deselected, in 341.21 seconds. Strict route coverage
is **163/163 (100%)**. The evidence commit runs the same mandatory hook. The
[ledger/gate snapshot](evidence/F-MTX-030/2026-10-02-preset-readback/ledger-check.json)
reports **130 features with fresh passing evidence**, **one feature with fresh
failure evidence**, and **zero stale features**. Levels are V0 27, V1 103,
V2 46 and V3 92. The validation gate accepts the eight explicitly linked known
failures; this does not establish that device preset readback works. C0 remains
incomplete, and BE-36 remains open.

The [reproduction bundle](evidence/F-MTX-030/2026-10-02-preset-readback/REPRODUCE.md)
uses fresh fixture data and simulator resets. It audits exact failing scenario
IDs and finding links as well as passing results, schemas and identities.
Proof containers, network and data volume were removed; the work container is
removed after committing. Images and ignored caches remain.

Next: remaining CEC simulator checks. Device-backed preset reads require
remediation and new proof. Owner-present hardware checks, WP-C4 scene visual
approval and the SEC-01-03 release-gate decision remain pending.
