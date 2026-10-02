# Matrix-control simulator proof

`wp-matrix-control-validation` adds 29 direct REST scenarios for six matrix
features and records all 29 passing against the packaged image. These extend
feature proof beyond the driver-level tests without changing application code.

| Feature | Proof |
| --- | --- |
| F-MTX-004 | Save all eight current routes into an empty preset; preserve live routing and other device state; hub metadata matches the saved routes; invalid slot and device refusal |
| F-MTX-018 | Beep off/on from the opposite device value; hub readback; device refusal preserves state |
| F-MTX-019 | Panel unlock/lock from the opposite device value; hub readback; device refusal preserves state |
| F-MTX-020 | All five LCD codes from a different starting code; hub readback; missing/invalid mode and device refusal |
| F-MTX-022 | Device input name and hub readback; accepted 32-character boundary; blank/33-character names and invalid port send no write; device refusal |
| F-MTX-023 | Device output name and hub readback; the same name/port boundaries and refusal checks |

Successful cases require the expected command and no unrelated device-state
changes. Invalid requests require no write command. Persistent device refusals
require HTTP failure, unchanged device state and the driver's two attempted
commands (one re-login/retry). Every scenario checks protocol warnings; the
runner also validates received WebSocket messages against the existing schema.
Name scenarios restore the seed name after checking it. The fixture data and
simulator are disposable, with state reset before each scenario.

The [run summary](evidence/F-MTX-004/2026-10-01-matrix-controls/run-summary.json)
contains 29 passing V2 API records. The
[identity/schema audit](evidence/F-MTX-004/2026-10-01-matrix-controls/audit.json)
confirms clean source and the exact image ID on every record. Source:
`e015d3e127fba07f1393aa5e5a4c457d555794b3`. Image:
`hdmi-matrix-hub:wp-simulator-evidence-refresh`,
`sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0`.
All 176 application, web, runtime and requirement files again matched the
checkout after line-ending normalization. Only validation scenarios and their
registry links changed before recording, so rebuilding the application image
was unnecessary.

The required implementation commit hook passed Ruff and **1,605 backend
tests**, with 3 skipped and 26 deselected, in 386.27 seconds. Strict route
coverage remains **163/163 (100%)**. The final evidence commit also runs the
mandatory hook. The [ledger check](evidence/F-MTX-004/2026-10-01-matrix-controls/ledger-check.json)
uses one registry/evidence snapshot for generated ledger output and the gate.
It reports **112 features with fresh passing evidence**, up from 106, and
**zero stale features**. Five features gain V2 proof. LCD has V2 simulator
evidence but remains capped at V1 by HIL-09. Levels are V0 27, V1 110, V2 39
and V3 92; 217 remain below target. Recorded baselines and finding caps are
unchanged. C0 remains incomplete.

The [reproduction bundle](evidence/F-MTX-004/2026-10-01-matrix-controls/REPRODUCE.md)
retains the selection, stack harness, record runner and audit/gate helpers.
Evidence filenames use the UTC date 2026-10-02; this handoff uses the local
session date 2026-10-01. The proof stack's containers, network and data volume
were removed; the work container is removed after committing. Local images and
ignored caches are retained.

Physical preset recall, front-panel effects and LCD timing need owner-present
hardware proof. Browser settings behavior and cross-client name propagation
need separate scenarios. Next: direct output-setting and EDID simulator proof,
keeping HIL-09 caps until hardware validation. WP-C4 scene visual approval and
the SEC-01–03 release-gate decision remain pending.
