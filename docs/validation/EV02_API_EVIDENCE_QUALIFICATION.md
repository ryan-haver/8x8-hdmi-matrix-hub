# EV-02 API evidence candidate

Execution disposition (2026-10-20): the exact combined candidate
`e5ebb376230d1dc6bbb62e07f38b7d4cf8221b32` received
[independent DeepSeek acceptance](../production/ev02/FINAL_API_REVIEW.md).
The coordinator integrated it sequentially, followed by report-only review tip
`e5eb9831780742598a605da5adfb17d905377955`, without source or evidence changes.
The seven API V2 dispositions below are accepted in that bounded scope; five
below-target current values advance to V2. This does not complete the wider
EV-02 security/API package. The preparation narrative below retains its original
checkpoint scope. Publication and current-head CI are recorded separately in
the execution record and allocation ledger.

This preparation checkpoint proposes seven API V2 evidence dispositions for
final independent combined review. Integration, qualification and publication
must be recorded separately in the [execution record](../planning/RUNTIME_EXECUTION.md)
and [allocation ledger](../production/AGENT_ALLOCATION.md). It does not accept
hardware, real clients, images, soak, field use or a final release.

| Feature | Proposed V2 basis | Source evidence |
| --- | --- | --- |
| F-API-014 | System info and storage read assertions | Two original API records |
| F-API-016 | CEC catalogues, capabilities and enable effects/refusals | 132 original API records |
| F-API-018 | Input/output rename and input invalid-port/blank-name refusal | Four clean mapped-candidate API records |
| F-API-026 | Themes/reset/preferences saved readback | Five original API records |
| F-API-028 | Fixture Flic button read/registration readback | Two original API records |
| F-API-036 | Audio-mute event and rejected-write no-event behavior | Two original API records |
| F-API-038 | CEC command event/frame contract | One original API record |

The 144 unique original files retain source
`1baac3dec660f41345869c126cfca94d6731c5a0`, original timestamps, feature lists,
null image digests and exact bytes. They were independently audited at
`700a7d7e3eadc89748f0718ba43a462c2e96afcc`; see the
[per-feature review](../production/ev02/API_PRESERVATION_REVIEW.md).
Their declared product inputs match the published candidate, and old assertions
remain unchanged by the separate input-name additions. This preserves original
proof with justified attribution; it is not a new 144-scenario run.

The new input-name package was authored by Sol 6.1 high and independently
reviewed by DeepSeek Pro at code commit `0a7d71b2`. The
[review and transparent prose correction](../production/ev02/NAME_REVIEW.md)
retain the original verdict, nonblocking limitations and pending final review.
The final author commit is `d8e4e1eff6e394144b7a0d007f500579108c2c88`.
The normal configured hook passed repository Ruff and 4,041 core tests, with four
skips, 35 deselections and 177/177 route coverage. The failed first hook attempt
(missing local ESLint dependencies) and its locked local dependency repair are
preserved in the [author report](../production/ev02/NAME_AUTHOR.md).

Coordinator mapping commit `bb4d3fdc972e7f556f29c6ed468accd4ff3b88b5`
adds the symmetric scenario links. A separate clean campaign at that exact SHA
passes all four name-route scenarios and all 31 checks, with no failed/skipped
checks or aborted run. [Original run summary](runs/ev02-api-evidence/input-name-run-summary.json)
and [record hashes/attribution](runs/ev02-api-evidence/manifest.json) retain the
tested source; later evidence/documentation commits do not rewrite it.

Scoped `.gitattributes` entries disable text normalization only for the new
evidence/import and run-metadata directories. Staged Git blobs must match the
record hashes, retaining original Linux/Windows line endings; historical paths
are not renormalized.

The registry changes only these seven features' evidence/basis and five
below-target `current` levels. Targets, interfaces, scenarios (apart from the
separate reviewed name mapping), finding links and all other feature fields are
retained. Medium findings BE-16 and TST-03 remain open. No HIL-09 cap is closed.

The source records also retain their original shared feature tags. In particular
one CEC event record also proves part of **F-API-015**; that broader grouped-route
feature remains **unqualified**, even if a generated numerical ledger maximum
reaches V2; its target is V3. Numerical levels do not replace the per-feature
acceptance decision.

No REST handler, shared contract, root manifest, lockfile or simulator read route
was changed. The source test implementation passed the normal hook. Coordinator
commits containing registry metadata, immutable evidence, byte-preservation
attributes and review prose
use the documented invocation-only hook exception with serial ledger/registry
checks; they do not claim another full-hook run. The exact final combined
candidate still requires independent review before integration.

After canonical ledger generation, the serial registry, evidence-schema,
ledger and repository-hygiene test selection passed **103 tests**, with two
Docker-only cases deselected, in 35.34 seconds. The generated numerical ledger
contains 205 below-target features and 57 stale-feature rows; numerical target
attainment alone does not accept their remaining release requirements.

The subsequent formal evidence gate passed with zero known failures linked to
open findings, using the clean four-scenario run summary and API client check.
All 148 staged evidence Git blobs match their preserved source SHA-256 values.
The standard whitespace check flags immutable CRLF bytes; an invocation-only
CRLF-aware check retaining the other default whitespace checks passes. No
persistent Git configuration or evidence formatting was changed.
