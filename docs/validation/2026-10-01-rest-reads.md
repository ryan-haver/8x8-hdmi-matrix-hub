# REST read contracts and route coverage

This batch continues the [system shortcut validation](2026-10-01-system-shortcuts.md)
on `wp-rest-read-contracts`. It adds tests and scenarios, corrects the shared
simulator fixture and records evidence. Application code and approved visual
baselines are unchanged.

## Scope and fixture corrections

The 34 new tests use the registered REST routes, real `OreiMatrix`, simulator
and disposable hub data. They check the complete JSON envelope and content
type, saved device customizations, boundary/invalid port numbers, shortcut
read alias equivalence and enabled filtering, nondefault saved themes and UI
preferences, registered Flic buttons, runtime/storage diagnostics and settings
connection state. CEC status checks all eight input and output flags. Cable
status checks actual Telnet observations and reports 503 when Telnet or the
matrix connection is unavailable. Both kiosk aliases serve the exact HTML bytes.

The first focused run exposed a fixture mismatch: `data_hub` passed its data
directory to the app but left `MATRIX_DATA_DIR` pointing to the autouse fixture's
other directory. Environment-based Flic and diagnostic modules therefore read
different storage. The fixture now exports the same directory before wiring
the app, as `run.py` does, and resets the persistence cache. It also closes the
app before disconnecting its matrix/simulator, so the poller cannot reconnect
during teardown. Kiosk comparisons now use bytes to preserve Windows line endings.
No shipped-app behavior was changed to address those test-harness failures.

The 20 `contracts.*` scenarios record focused read and invalid-read contracts:

| Feature group | Recorded reads |
| --- | --- |
| F-API-004 | Cable and CEC status, including every port's flags |
| F-API-014 | Runtime info and storage availability |
| F-API-016 | Input/output CEC catalogs and an invalid type |
| F-API-017 | All/individual saved device settings and invalid ports |
| F-API-024 | Favorite/dashboard shortcut lists, the built-in alias and an unknown key |
| F-API-026 | Default themes and saved UI preferences |
| F-API-027 | Settings connection state |
| F-API-028 | Saved fixture Flic registrations |

Each scenario requires the expected response data, unchanged matrix state,
no mutating device commands and no protocol warnings. Fixture-specific cases
are simulator-only. The pytest suite adds checks beyond the recorded scenarios,
including custom preferences, disconnected errors and HTML serving.

## Verification and evidence

The corrected focused run passed **68 tests** (34 new simulator tests plus
34 model/registry checks), and all **20 diagnostic scenarios** passed with a
clean gate. The full implementation hook passed **1,539 tests**, with 3 skipped
and 26 deselected, in 369.92 seconds. Ruff and the Docker build passed.

The final shipped-image run passed **20 API/V2 records**, with a clean gate and
zero known failures. All records have `commit.dirty=false`, the exact source
and image ID, and pass the evidence schema. Gitleaks found no secrets in the
20 new records.

Source: `9ef6d31f69bfd0e251475ea93ea09126f85ea243`.
Image: `hdmi-matrix-hub:wp-rest-read-contracts`.
Image ID: `sha256:bc0c66e35cc2dffe0d6dbcc18f42f65d89f524927bd2d4d14c3fb18ba1e9acea`.

The [run summary](evidence/F-API-004/2026-10-01-rest-reads-image/run-summary.json)
links every record. The [route inventory](evidence/F-API-004/2026-10-01-rest-reads-image/route-coverage.json)
shows **142/163 routes (87.1%)**, up from 125/163 (76.7%). All 17 previously
uncovered read routes now have tests; 21 uncovered write routes remain.
Inventory remains report-only because the Phase 2 exit requires all routes.

The regenerated ledger has **82 features at V3, 28 at V2 and zero at V4**.
Seven API feature groups gain fresh V2 read evidence. F-API-027 remains capped
at V1 by SEC-03. Recorded baselines and security caps are unchanged, with no
level regression. There are 223 features below target and 67 with stale evidence.
These aggregate levels do not prove the write routes sharing those feature IDs.

## Reproduction and remaining work

The [stack metadata](evidence/F-API-004/2026-10-01-rest-reads-image/stack.json),
[PowerShell harness](evidence/F-API-004/2026-10-01-rest-reads-image/stack.ps1)
and [record runner](evidence/F-API-004/2026-10-01-rest-reads-image/record.sh)
are preserved. Copy the harness and runner to `build/rest-reads-image.ps1` and
`build/rest-reads-record.sh`, build the named image and invoke the harness.
It assumes this checkout path, cached Playwright node/Python volumes and
`hdmi-matrix-hub-sim:deploy-test`; change `$taskRoot` elsewhere. The disposable
hub, simulator, fixture-data volume and network are removed after the run.
No real matrix, Remote or Flic hardware is contacted.

Next coverage work is the 21 remaining write routes, including shortcut
aliases, device settings, themes/UI preference persistence and Flic registration.
Enabled-reboot recovery still needs its separate simulator lifecycle scenario.
WP-C4 visual approval, owner-present hardware checks and the SEC-01–03
release-gate decision remain pending. C0 is not complete.
