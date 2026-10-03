# HTTP CEC commands and per-port enable flags

`wp-cec-command-validation` adds **273 passing packaged-image API scenarios**
for nine CEC features and three existing API features. Application code is
unchanged. Five CEC features gain their first committed V2 evidence:
F-CEC-002 navigation, F-CEC-003 playback, F-CEC-004 source volume/mute,
F-CEC-008 explicit enable/disable and F-CEC-009 enabled-port status.

The batch sends all 19 source-table entries to each of the eight inputs and
all six display-table entries to each output: **200 dispatch cases**. Expected
indices are literal captured/device-web table values, independent of the
production constants. Each case starts with the target disabled, refreshes the
hub's CEC cache, and proves one complete enable write followed by one exact
HTTP frame to the intended port. Independent matrix flag readback and raw API
readback agree; all other device state is preserved. Power commands also emit
the matching success WebSocket event. Uppercase command names are exercised
on port eight. Display `active` dispatch is included without claiming its
physical effect as display power or volume proof.

Another **16 cases** prove pre-enabled targets receive one frame without an
enable write. **32 explicit flag edits** cover true and false on every input
and output, preserving every other flag, with both raw and formatted readback.
Two additional checks prove omitted `enabled` defaults to true. The remaining
23 cases cover out-of-range/noninteger command ports, enable-port boundaries,
unsupported commands, device refusals and enabled-port status. Refused CEC
frames are sent only once, return HTTP failure and emit no success event;
refused flag writes preserve the whole matrix. Status covers all-off, all-on,
mixed arrays and an unavailable device read.

The [run summary](evidence/F-CEC-002/2026-10-02-cec-controls/run-summary.json)
and [audit](evidence/F-CEC-002/2026-10-02-cec-controls/audit.json) retain every
outcome. Source: `d434d3d88943ef5faf3452c219a3ec3b0bfdad25`. Hub image:
`hdmi-matrix-hub:wp-simulator-evidence-refresh`,
`sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0`.
The image matches all 176 source/web/runtime/dependency files after line-ending
normalization. Every record has clean source, this exact image ID, a valid
schema and passing checks. The stack explicitly selects
`OREI_USE_TELNET_CEC=false`; this is HTTP proof, not Telnet proof.

Ruff and **1,605 backend tests** passed through the implementation commit hook
in 378.15 seconds (3 skipped, 26 deselected). Strict route coverage is
**163/163 (100%)**. The evidence commit runs the same mandatory checks.
The [ledger/gate snapshot](evidence/F-CEC-002/2026-10-02-cec-controls/ledger-check.json)
reports **135 fresh passing features**, **one fresh failing feature**, and
**zero stale features**. Levels are V0 27, V1 98, V2 51 and V3 92. The batch has
no failures or unlinked regressions. BE-36 and its eight preset failures remain
open; C0 remains incomplete. Recorded baselines and finding caps are preserved.

The [reproduction bundle](evidence/F-CEC-002/2026-10-02-cec-controls/REPRODUCE.md)
uses isolated simulator containers and fresh fixture data, with per-case
resets and cache setup. Proof containers, network and data volume were removed;
the work container is removed after committing. Cached images and ignored
build files remain.

Next: CEC capability/catalog reporting and opt-in Telnet transport proof.
Actual TV/source power, navigation, playback and volume effects still need
owner-present hardware validation. Device-backed preset remediation, WP-C4
scene visual approval and the SEC-01-03 release-gate decision remain pending.
