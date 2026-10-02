# External audio simulator proof

`wp-external-audio-validation` adds 100 REST scenarios for three external audio
features and records all 100 passing against the verified packaged application
image. Application code is unchanged. Each setting begins with a different
value, checks the exact device command, independently reads simulator state,
checks raw and formatted REST readback, and preserves unrelated settings.

| Feature | Proof |
| --- | --- |
| F-MTX-015 | All three mode codes and names, mode catalog, invalid/missing/noninteger mode, device refusal |
| F-MTX-016 | Enable and disable on all eight outputs, invalid ports, missing flag, device refusal |
| F-MTX-017 | All 64 output/input routes in matrix mode, invalid ports/input bounds, missing/noninteger input, device refusal |

Invalid requests require HTTP 400 without a device write. A persistent device
refusal requires HTTP 500, two command attempts (one re-login/retry), and no
state changes. Every scenario checks for protocol warnings. The routing proof
uses mode 2, matching the device web interface. REST currently exposes HDMI
inputs 1-8; device ARC source codes 9-16 and routing outside matrix mode are
outside this batch. Mode selection proves the stored code and names; actual
binding and physical audio behavior still need hardware proof. The driver-only
`set ext-audio index` command has no REST action and is not exercised here.

The [run summary](evidence/F-MTX-015/2026-10-01-external-audio/run-summary.json)
contains 100 passing V2 API records. The
[identity/schema audit](evidence/F-MTX-015/2026-10-01-external-audio/audit.json)
confirms clean source and the measured image ID on every record. Source:
`f7afdac1d3b18da109c1144bcef93c1240e33520`. Image: `hdmi-matrix-hub:wp-simulator-evidence-refresh`,
`sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0`.
All 176 application, web, runtime and requirement files match the checkout after
line-ending normalization. Only validation code and registry links changed in
the scenario commit, so the retained application image remains applicable.

The implementation commit hook passed Ruff and **1,605 backend tests**, with
3 skipped and 26 deselected, in 385.48 seconds. Strict route coverage is
**163/163 (100%)**. The evidence commit also runs the mandatory hook. The
[ledger/gate snapshot](evidence/F-MTX-015/2026-10-01-external-audio/ledger-check.json)
reports **122 features with fresh passing evidence**, up from 119, and **zero
stale features**. All three added features have V2 simulator proof but retain
their HIL-09 cap at V1. Levels remain V0 27, V1 110, V2 39 and V3 92; 217
features remain below target. Recorded baselines and finding caps are unchanged.
C0 remains incomplete.

The [reproduction bundle](evidence/F-MTX-015/2026-10-01-external-audio/REPRODUCE.md)
retains the selection, isolated stack harness, record runner, schema audit and
ledger helper. It uses fresh fixture data and resets device state before every
scenario. Evidence filenames use UTC 2026-10-02; this handoff uses the local
session date 2026-10-01. Proof containers, network and data volume were removed;
the work container is removed after committing. Images and ignored caches remain.

Next: matrix status/readback and input cycling simulator proof. Owner-present
hardware proof, WP-C4 scene visual approval and the SEC-01–03 release-gate
decision remain pending.
