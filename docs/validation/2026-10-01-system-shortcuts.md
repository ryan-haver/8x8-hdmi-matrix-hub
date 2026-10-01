# System shortcut modes and failure feedback

This batch continues the [direct macro/shortcut validation](2026-10-01-domain-ui.md)
on `wp-system-shortcut-validation`. It extends scenarios and records evidence;
application code and approved visual baselines are unchanged.

## Scope

REST and Chromium execute the saved shortcuts through the same user flows as
the previous batch. Beep on/off and panel lock/unlock now have browser proof.
Every LCD setting is exercised: off, always on, 15 seconds, 30 seconds and
60 seconds. Each happy case starts from a different simulator value, requires
the correct command payload exactly once, reads back the changed device field,
checks that unrelated state is unchanged, and requires the browser success toast.
The existing `lcd_timeout_10s` key still sets code 2 and displays `LCD: 15s`.

Persistent refusal of beep, lock and LCD writes must return HTTP 500, preserve
device state, and show an error without a success toast. The transport's
documented session-recovery policy treats `result: 0` as a possible expired
session: it re-logs in and retries once. The scenarios require exactly two
refused attempts. The initial diagnostic incorrectly expected one; inspecting
the command log and `_send_command` contract resolved that assertion, and
the corrected failure/disabled subset passed all eight API/browser records.

The fixture's disabled reboot shortcut must return HTTP 400, send no reboot
command over either HTTP or Telnet, leave device state unchanged, and show an
error without success feedback. This proves the disabled guard only.

## Verification and evidence

The focused model/registry suite passed all 34 tests, and Ruff passed. The
implementation commit's required full backend hook passed **1,505 tests**, with
3 skipped and 26 deselected, in 319.80 seconds. The Docker build passed.

The final shipped-image run passed **26 records: 13 REST/V2 and 13 Chromium/V3**,
with a clean validation gate and zero known failures. Every record has
`commit.dirty=false` and the image ID. All 26 JSON records passed the evidence
schema; Gitleaks found no secrets in the new records.

Source: `7aa17c95d9b62ea63581ecccc03a4448660704ec`.
Image: `hdmi-matrix-hub:wp-system-shortcut-validation`.
Image ID: `sha256:75952b42546eac673d865264c77c2da46ad1740d50bf7e489335b5e960ce08e3`.

Representative browser evidence:

- [Beep on](evidence/F-DOM-027/2026-10-01-V3-7aa17c95-shortcuts.beep_on-browser.json)
- [Panel unlock](evidence/F-DOM-027/2026-10-01-V3-7aa17c95-shortcuts.panel_unlock-browser.json)
- [LCD always on](evidence/F-DOM-028/2026-10-01-V3-7aa17c95-shortcuts.lcd_always_on-browser.json)
- [Refused LCD write](evidence/F-DOM-028/2026-10-01-V3-7aa17c95-shortcuts.lcd_rejected-browser.json)
- [Disabled reboot](evidence/F-DOM-027/2026-10-01-V3-7aa17c95-shortcuts.disabled_reboot-browser.json)

The [run summary](evidence/F-DOM-027/2026-10-01-system-shortcuts-image/run-summary.json)
lists every record. The [stack metadata](evidence/F-DOM-027/2026-10-01-system-shortcuts-image/stack.json),
[PowerShell harness](evidence/F-DOM-027/2026-10-01-system-shortcuts-image/stack.ps1)
and [record runner](evidence/F-DOM-027/2026-10-01-system-shortcuts-image/record.sh)
are preserved. The harness creates an isolated simulator, hub, fixture-data
volume and network, then removes them. It assumes this checkout path and the
cached Playwright node/Python volumes; change `$taskRoot` elsewhere. Reproduce
by copying the harness and runner to their `build/system-shortcuts-*` paths,
building the named image, then invoking `build/system-shortcuts-image.ps1`.
It requires `hdmi-matrix-hub-sim:deploy-test` and never contacts real hardware.

The regenerated ledger has **82 features at V3, 21 at V2 and zero at V4**.
F-DOM-027 gains browser evidence for beep and panel lock. LCD evidence now
covers every stored mode. Recorded baselines stay unchanged; no feature's
level drops. There are 229 features below target and 67 with stale evidence.
The ledger's aggregate F-DOM-027 level does not prove an enabled reboot.

## Remaining work

Physical beep, panel behavior and LCD timing need owner-present hardware
observations. An enabled reboot and recovery need a separate simulator
lifecycle scenario, followed by hardware proof. The backend route inventory
still reports 125/163 routes (76.7%), with 38 uncovered; extending REST contract
coverage is a useful next coding batch. C0 is not complete.

WP-C4 scene-editor visual approval, the other hardware checks and the
SEC-01–03 release-gate decision remain pending.
