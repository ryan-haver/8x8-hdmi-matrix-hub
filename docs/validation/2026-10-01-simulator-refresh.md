# Simulator evidence refresh and CEC flag preservation

This batch continues the enabled-reboot work on `wp-simulator-evidence-refresh`.
It refreshes the API, browser, Home Assistant and scripted Remote evidence
affected by shared transport changes. The new ledger has **seven stale
features, down from 98**; all seven concern deployment validation.

The refresh exposed BE-35. After another operation warmed the CEC cache,
enabling output 8 wrote an old input 1 flag back to the simulator. The
[original failure](evidence/F-API-016/2026-10-01-V2-72cc71dc-writes.cec_output_enable-api.json)
records input 1 changing from disabled to enabled, outside the requested edit.
The fixed driver reads the current arrays before a port edit and serializes
concurrent edits. It returns failure without writing if the read fails or
omits complete valid arrays. Successful writes update the cache under its
lock. The API reference documents these behaviors and the remaining external
read/write race inherent in the device's array protocol.

Ten new regression tests cover input/output enable and disable with a warm
cache and external changes, concurrent edits, failed reads, and malformed
snapshots. Existing golden-response tests pass. The required implementation
commit hook passed Ruff and **1,605 backend tests**, with 3 skipped and 26
deselected, in 330.11 seconds. The
[strict route inventory](evidence/F-API-016/2026-10-01-simulator-refresh/route-coverage.json)
remains **163/163 (100%)**.

The [combined run summary](evidence/F-API-016/2026-10-01-simulator-refresh/run-summary.json)
contains **192 passing checks** across 99 feature IDs:

| Client | Checks | Environment |
| --- | ---: | --- |
| API | 102 | Packaged hub image, simulator and fresh fixture data |
| Browser | 53 | Real Playwright browser against the packaged image |
| Home Assistant | 19 | Real pinned HA 2026.9.3 container, installed component, packaged hub |
| Remote 3 | 18 | Scripted Remote client, real legacy driver and simulator subprocesses |

The Remote checks run the source entry point; their image digest is empty.
They are not attributed to the Docker image or to physical Remote hardware.
All records pass schema and clean-source checks; API, browser and HA records
match the exact image ID. The validation gate passes with zero known failures.
All 48 referenced browser captures are retained with Git LFS. Gitleaks found
no secrets in the refreshed records and retained diagnostics.

The [CEC snapshot audit](evidence/F-API-016/2026-10-01-simulator-refresh/cec-snapshot-check.json)
compares the original failure with the corrected sequence: one port write,
a current read before it, and preservation of the input flags and other
output flags. The original failure remains historical evidence; it is stale
after the driver fix.

The first HA run tried reboot immediately after the unreachable-device case,
while its button was still unavailable. HA accepted the service call without
sending a device command. The harness now waits for both transports and the
button to recover before this action. The full 19-check HA rerun passed. The
[raw diagnostic](evidence/F-API-016/2026-10-01-simulator-refresh/ha-unavailable-diagnostic.txt)
and [readiness check](evidence/F-API-016/2026-10-01-simulator-refresh/ha-readiness.json)
are retained separately from the passing validation records.

Source: `2a28a93ea3243e412894ab2f84930c86c7f1aaf5`.
Image: `hdmi-matrix-hub:wp-simulator-evidence-refresh`.
Image ID: `sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0`.
All 176 source, web, runtime and requirement files in the image match the
checkout after line-ending normalization.

The regenerated ledger reports **92 features at V3, 34 at V2 and zero at V4**,
with 217 below target. Recorded baselines and security finding caps are
unchanged. These levels cover simulator effects and client behavior; physical
timing, display effects and owner hardware still require separate proof.

The [reproduction bundle](evidence/F-API-016/2026-10-01-simulator-refresh/REPRODUCE.md)
contains selections, their audit, runners, stack harnesses and per-client
summaries. Each packaged-image client uses a new simulator, hub and data
volume. The task's proof containers, networks and data volumes were removed;
no real matrix, Remote or Flic hardware was contacted. Visual baselines and
owner approval gates are unchanged.

Next: refresh the seven deployment features, then continue the remaining C0
gaps. WP-C4 visual approval, owner-present hardware validation and the
SEC-01–03 release-gate decision remain pending. C0 is incomplete.
