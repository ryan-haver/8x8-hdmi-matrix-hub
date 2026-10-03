# Enabled reboot and automatic recovery

This batch continues the REST write contracts on `wp-enabled-reboot-validation`.
Enabled reboot now has integration checks through the real registered REST app,
`OreiMatrix`, HTTP/Telnet transports and disposable simulator.

The 16 new tests cover the direct reboot route and both shortcut aliases with
HTTP-only and Telnet connections. Each successful path sends one reboot command
on the selected transport, actually reboots the simulator, announces link loss
and recovery, preserves device settings and permits a subsequent REST routing
write. Recovery uses the matrix supervisor; the tests never manually reconnect.
Persistent HTTP refusal and a dropped HTTP response return failure without a
second HTTP reboot attempt. WebSocket messages pass the contract schema.

The tests reproduced BE-34: the Telnet client previously returned success for a
silent command that never rebooted the simulator. It now uses the same
acknowledgement check as other Telnet writes. Error codes, silence and an echo
alone return false; the existing driver fallback can then use HTTP. The silent
simulator regression proves one Telnet attempt that was ignored, one HTTP
attempt and one actual reboot. This differs from the normal path's one attempt.

Ruff and the required implementation commit hook passed **1,595 backend tests**,
with 3 skipped and 26 deselected, in 392.54 seconds. The archived
[strict route inventory](evidence/F-MTX-021/2026-10-01-enabled-reboot-image/route-coverage.json)
remains **163/163 (100%)**.

The packaged-image [run summary](evidence/F-MTX-021/2026-10-01-enabled-reboot-image/run-summary.json)
contains **seven passing checks: four API/V2 and three browser/V3**, with zero
known failures in the validation gate. They cover enabled reboot through the
direct route and both aliases, enabled and disabled browser shortcuts, and
recovery after a 30-second simulated outage. All records pass schema, clean
source and exact image checks. Two referenced browser captures are retained
with Git LFS. The [supplemental lifecycle audit](evidence/F-MTX-021/2026-10-01-enabled-reboot-image/lifecycle-check.json)
checks the four enabled-reboot records for exactly one actual simulator reboot,
one Telnet attempt, ordered disconnect/recovery events and unchanged device
state. Its helper was corrected to tolerate archived JSON lists and UTF-8 BOMs
before the audit passed.

Gitleaks found no secrets in the seven records. The regenerated ledger reports
81 features at V3, 25 at V2 and zero at V4, with 234 below target and 98 with
stale evidence. The shared Telnet change makes previous simulator records stale
until refreshed; the lower totals reflect that evidence rule. Recorded
baselines and finding caps remain unchanged.

Source: `b0c1a32e98796a00c2fc07e843148d99253e3dad`.
Image: `hdmi-matrix-hub:wp-enabled-reboot-validation`.
Image ID: `sha256:1d7eee094200943ea52175bf58a56893e7a713122e02a29fc3fb51f73810f7af`.
The image's source, web and runtime files match the checkout, allowing checkout
line-ending normalization.

Reproduction uses the archived [stack harness](evidence/F-MTX-021/2026-10-01-enabled-reboot-image/stack.ps1),
[record runner](evidence/F-MTX-021/2026-10-01-enabled-reboot-image/record.sh),
[selection](evidence/F-MTX-021/2026-10-01-enabled-reboot-image/selection.json),
[metadata](evidence/F-MTX-021/2026-10-01-enabled-reboot-image/stack.json) and
[audit helper](evidence/F-MTX-021/2026-10-01-enabled-reboot-image/check-lifecycle.py).
Copy them to their `build/reboot-*` paths, build the named image and run the
stack harness. Adjust its checkout path on another machine; it requires the
cached Playwright Python/node volumes and simulator image. All hub/device data
is disposable. Cleanup restores the fixture's disabled shortcut and removes
the task's hub, simulator, data volume and network.

This is simulator proof. Physical reboot timing and Telnet acknowledgement
remain uncaptured. A missing acknowledgement cannot establish whether real
hardware ignored a command; an accepted command followed by a lost reply can
make fallback ambiguous. Confirmation-dialog UI, HA/Flic reboot triggers and
physical power-cycle behavior need separate checks. No real hardware was
contacted. Visual baselines and owner/security approval gates are unchanged.

Next: refresh simulator evidence affected by the transport change and continue
C0 coverage. WP-C4 visual approval, owner-present hardware checks and the
SEC-01–03 release-gate decision remain pending; C0 is incomplete.
