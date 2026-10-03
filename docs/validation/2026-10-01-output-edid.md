# Output settings and EDID simulator proof

`wp-output-edid-validation` adds 62 REST scenarios for seven matrix features,
then records all 62 passing against the verified packaged image. Application
code is unchanged. The scenarios check exact command payloads, independently
read simulator state, REST readback, protocol warnings and unchanged unrelated
settings. Every valid setting starts from a different device value.

| Feature | Proof |
| --- | --- |
| F-MTX-008 | Stream disabled/enabled; raw and REST readback; refusal; output ports 0 and 9 rejected without writes |
| F-MTX-009 | All five HDCP modes; raw/API values agree; refusal; missing/out-of-range mode and invalid port |
| F-MTX-010 | All three HDR modes; API 1–3 maps to device 0–2 and reads back as API values; same refusal/boundary checks |
| F-MTX-011 | All five scaler modes; API 1–5 maps to device 0–4, including audio-only; same refusal/boundary checks |
| F-MTX-012 | ARC disabled/enabled; raw and REST readback; refusal and invalid ports |
| F-MTX-013 | EDID IDs 1, 12, 36 and user EDID ID 39; invalid input/mode bounds, missing mode and device refusal |
| F-MTX-014 | All eight copy sources select EDID code 39 + output; invalid sources and device refusal |

Invalid requests require HTTP 400 and no device write. Persistent device
refusals require HTTP 500, unchanged device state and two command attempts
(one re-login/retry). Copy scenarios start with the selected simulated display
connected and require `set edid`; the unsupported `copy edid` and
`set input edid` commands must never appear. These tests prove selection codes,
not the EDID bytes copied from a physical display or negotiation with a source.

The [run summary](evidence/F-MTX-008/2026-10-01-output-edid/run-summary.json)
contains 62 passing V2 API records. The
[identity/schema audit](evidence/F-MTX-008/2026-10-01-output-edid/audit.json)
confirms clean source and the measured image ID on every record. Source:
`972b8c40f5a25e0d8a66c3038eb54af0cacc9c64`. Image:
`hdmi-matrix-hub:wp-simulator-evidence-refresh`,
`sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0`.
All 176 application, web, runtime and requirement files match the checkout after
line-ending normalization. The scenario commit changes validation code and
registry links; the retained application image therefore remains applicable.

The implementation commit hook passed Ruff and **1,605 backend tests**, with
3 skipped and 26 deselected, in 352.61 seconds. Strict route coverage is
**163/163 (100%)**. The evidence commit also runs the mandatory hook. The
[ledger/gate snapshot](evidence/F-MTX-008/2026-10-01-output-edid/ledger-check.json)
reports **119 features with fresh passing evidence**, up from 112, and **zero
stale features**. All seven added features have V2 simulator proof but remain
capped at V1 by HIL-09. Levels remain V0 27, V1 110, V2 39 and V3 92; 217
features are below target. Recorded baselines and finding caps are unchanged.
C0 remains incomplete.

The [reproduction bundle](evidence/F-MTX-008/2026-10-01-output-edid/REPRODUCE.md)
retains the selection, stack harness, record runner, schema audit and ledger
gate helper. It uses fresh fixture data, an isolated simulator and a state reset
before each scenario. Evidence filenames use UTC 2026-10-02; this handoff uses
the local session date 2026-10-01. Proof containers, network and data volume
were removed; the work container is removed after committing. Local images and
ignored caches are retained.

Physical video output, HDCP behavior, HDR/scaling, ARC audio and EDID negotiation
still require owner-present hardware proof. Browser settings and real client
behavior require separate scenarios. Next: external audio settings on the
simulator, preserving HIL-09 caps. WP-C4 scene visual approval and the
SEC-01–03 release-gate decision remain pending.
