# REST write contracts and complete route coverage

This batch continues the [REST read contracts](2026-10-01-rest-reads.md) on
`wp-rest-write-contracts`. All 21 remaining write-route gaps now have tests
through the registered REST app, real `OreiMatrix`, simulator and disposable
hub data. The full backend inventory is **163/163 routes (100%)**, with strict
coverage enabled for both commit hooks. The default inventory mode remains
report-only until the broader Phase 2 exit requirements are met.

## Changes and regression proof

The 40 new tests verify device/custom preset settings, profile CEC and macro
assignments, profile ordering, shortcut creation/editing/flags/order/deletion,
themes/reset, UI preferences, Flic registration and connection testing. Saved
files and manager reloads prove persistence. Output naming, CEC enable and
shortcut execution are checked against actual simulator state and commands.
Invalid requests preserve saved values. The shared fixture now provides a
config file for physical port-name persistence, matching runtime wiring.

The tests exposed and fixed three behaviors:

- Bulk device settings previously ignored save failures and claimed every
  port was updated. A failed save now returns HTTP 500, lists only persisted
  ports, and restores the failed port's cached value. Individual input/output
  customizations and preset names also restore cached values after a refusal.
  Mixed-success regression checks prove earlier saved entries remain applied.
- Flic registration previously returned success after a failed save. It now
  returns HTTP 500 and restores the prior registry, including renamed buttons.
- Explicit JSON `null` could not clear a profile's power macro. Both profile
  update routes now clear it; omitted fields preserve existing assignments.
  Tests cover both power-on/off fields, both routes, and saved readback.

The API reference documents bulk-save behavior and explicit macro clearing.
Approved visual baselines and release/security gates are unchanged.

## Verification and evidence

Ruff passed. The implementation commit's required backend hook passed
**1,579 tests**, with 3 skipped and 26 deselected, in 338.58 seconds.
The [strict route inventory](evidence/F-API-017/2026-10-01-rest-writes-image/route-coverage.json)
has no uncovered routes. All **41 diagnostic read/write scenarios** passed.

The shipped-image [run summary](evidence/F-API-017/2026-10-01-rest-writes-image/run-summary.json)
contains **60 passing records: 50 API/V2 and 10 browser/V3**. It includes the
20 read contracts, 21 new write contracts, and refreshed profile, preset and
kiosk flows affected by the changed code paths. The gate passed with zero
known failures. Every record passed schema, source, exact image ID and
`commit.dirty=false` checks. Gitleaks found no secrets in the 60 records.

Source: `dba2f21d3333f63a2b13917fdfbaf308e3c9aaa5`.
Image: `hdmi-matrix-hub:wp-rest-write-contracts`.
Image ID: `sha256:807413ccf61a729f9d867c6522f878ce923bc05ebfb87ee0369df2cc2f190ebc`.

The regenerated ledger has **84 features at V3, 29 at V2 and zero at V4**,
with 221 below target and 63 with stale evidence. Recorded baselines and
critical/high finding caps remain unchanged. Profile API F-API-019 and settings
API F-API-027 remain capped at V1 by SEC-04 and SEC-03 respectively.

Route coverage means each registered route was exercised; it does not prove
every branch or physical hardware behavior. Successful user-shortcut deletion,
storage refusals, manager reloads and reconnect are verified by pytest. The
shipped-image deletion scenario checks built-in deletion refusal, and its
connection-test scenario checks an already connected matrix.

## Reproduction and next work

The [stack harness](evidence/F-API-017/2026-10-01-rest-writes-image/stack.ps1),
[record runner](evidence/F-API-017/2026-10-01-rest-writes-image/record.sh),
[selection](evidence/F-API-017/2026-10-01-rest-writes-image/selection.json) and
[metadata](evidence/F-API-017/2026-10-01-rest-writes-image/stack.json) are archived.
Copy them to `build/rest-writes-image.ps1`, `build/rest-writes-record.sh` and
`build/rest-writes-selection.json`, build the named image and run the harness.
It uses this checkout path, cached Playwright node/Python volumes and
`hdmi-matrix-hub-sim:deploy-test`; adjust `$taskRoot` on another machine.
Use fresh fixture data: shortcut creation leaves a test shortcut behind.
The disposable hub, simulator, data volume and network were removed after
verification. No real matrix, Remote or Flic hardware was contacted.

Next is enabled-reboot lifecycle and recovery proof. WP-C4 visual approval,
owner-present hardware checks and the SEC-01–03 release-gate decision remain
pending. C0 is incomplete.
