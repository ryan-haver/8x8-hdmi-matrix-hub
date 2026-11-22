# Round 1 independent assessment — execution pinning 2026-11-01 (MiniMax / OpenCode 2)

Author: MiniMax-M3 via native OpenCode 2 (`minimax-coding-plan/MiniMax-M3`, variant `thinking`; CLI
effort unsupported). Actual identity must be attested at dispatch — this report asserts the route
selection, not a verified native identity receipt. Round 1 independent assessment only: no
consensus, no phase approval, no source/code/security review, no dispatch authority.

## 1. Basis and verification

| Check | Result |
| --- | --- |
| Frozen entry HEAD | `19ee8be994eb2d4630aead8a7eec8f6a22140224` ("docs: prepare complete execution pins and current provider policy"); worktree clean |
| Planning floor | `e2161484459da65aee14433136a14963507b499c`; ancestor of frozen HEAD: yes |
| Row count | 84 = 65 mapped + 9 followup + 3 review + 7 external_gate; 65 + 12 P1 followups + 7 owner gates matches the brief |
| Coverage vs `manifest.json` | All 65 `dispatch_units` present; id sets equal; package, wave, `feature_ids`, `scope`, `acceptance`, `exclusive_writable`, `reviewer_writable` all identical to manifest; no extras, no omissions |
| Base honesty | 65 mapped rows use `accepted_integration_after_dependencies`, `fixed_sha: null`, `resolve_to_exact_full_sha_before_creation: true`, `requires_ancestor_floor: true`; `dependency_outputs` mirrors `dependencies` exactly; no fabricated future SHA found |
| Fixed candidates | `2d02004d…`, `1fbfee11…`, `caaa4faa…` equal `BASELINE.current_review_candidates`; all three resolve as commits; observed heads of `wp-sec-data-02-c3`, `wp-api-read-03-c1`, `wp-api-client-02-c2` match exactly and are clean |
| Documentation checks | 5 documentation modules (`core_documentation`, `client_guides_docs`, `openapi_and_config_docs`, `security_docs`, `license_and_protocol_docs`), `-p no:tests.route_inventory -p no:cacheprovider`, fresh forward-slash basetemp/JUnit: **489 passed** on the pre-commit run (JUnit SHA-256 `06280b15…`) and **489 passed** again after the report edit (`8990aa21…`); both JUnit copies retained in the private subtree |
| Route policy | DeepSeek: 0 rows, `dispatch_allowed: false` everywhere. Gemini: `dispatch_allowed: false`, Antigravity absent from PATH — held unverified, **not** counted as available headroom. Anthropic allowed for future roles but planning ≠ source/security-review qualification |
| Worktree reservations | 168 unique reserved names, `actual_worktree_id: null` except the 3 retained read-only source references |

**Hash finding (material).** `DRAFT_PACKET.json` declares input hashes that do **not** match the
committed bytes at the frozen commit. Declared `73bddf6b…` / `39de9d9e…` / `e59faf7e…` equal the
CRLF-normalised text hashes; the committed LF blobs hash `17bdf32d…` / `0e92683a…` / `72d1aa31…`.
The same CRLF/LF split appears in `BASELINE.historical_source_hashes` for `manifest.json` and
`LEDGER.md`. Separately, `BASELINE.json` records the HANDOFF hash `b415ea6f…`, which is the
**parent** commit's `HANDOFF.md`, not the pinned commit's (`88f6b214…` after the preparation commit
appended to it). A peer family hashing committed bytes will not reproduce the frozen packet.

Coordinator disposition (2026-11-01, after this finding was reported): the declared hashes were
taken from pre-stage Windows CRLF working files, while Git `19ee8be9` stores LF under the existing
attributes; canonical file content is unchanged and identified by `19ee8be9`. The hashes I observed
are preserved above as recorded, not corrected. The residual requirement is unchanged in substance:
successor packets must carry exact LF-byte hashes so peers can reproduce them directly.

## 2. Findings summary

| # | Finding | Class |
| --- | --- | --- |
| F1 | 73 of 84 rows name `claude` as reviewer; **none** of them encodes the `QUAL-ANTHROPIC-CORE-01` gate or dependency that `routes.claude.qualification_gate` requires for source/security review | Material |
| F2 | Only dispatchable different-family reviewer for those 73 rows is Gemini, which is held unverified — a program-wide single-reviewer-route dependency with no usable alternate | Material |
| F3 | `SW-API-READ-04-C1`, `SW-API-CLIENT-02-C1`, `SW-SEC-DATA-02-C1` corrective children (independently reviewed source, evidence qualification/assembly pending, reproduced finding) have **no** pin row | Material |
| F4 | 5 already-accepted units share one uniform `remaining_disposition` string with the 60 planned ones, including `SW-API-READ-01` (`qualified_published_api_v2`) | Material |
| F5 | 8 followup rows and 7 owner-gate rows lack `requires_ancestor_floor` and `dependency_outputs`; owner gates omit `SW-BUILD` although their base resolves from it | Material |
| F6 | `P1-PUBLISH-CHECKPOINT` and `EV-FLIC-ADMISSION` are dependency leaves — nothing downstream waits for P1 candidate publication, and Flic admission is absent from `EV-COMBINED-P1` | Material |
| F7 | Per-unit `shared_path_lease` text from the manifest was collapsed to two generic strings; `SW-SEC-AUTH-01`'s live serial lease on `tools/validate/clients/browser.py` + `browser_driver.mjs` is lost | Material |
| F8 | Existing accepted files (`sw_api_read_01.py`, `sw_api_read_04.py`, `sw_sec_auth_01.py`, `test_sw_api_read_04.py`, `test_sw_sec_auth_01.py`) are listed as free `exclusive_writable` | Material |
| F9 | Package-level `scope`/`acceptance` duplicated verbatim across 52 units in 17 packages — not unit-discriminating | Material |
| F10 | Three-way count disagreement: ledger/BASELINE 210 below-target & 96 stale; manifest counts 205/57; `EV-CI-ATTRIBUTION` scope says "56 CI records" | Material |
| F11 | `suggested_wave` is inherited from the manifest package wave; no field encodes launch batching under the ≤2-worker ceiling (wave 10 alone reserves 28 worktrees) | Material |
| F12 | 7 owner-gate rows carry `author_route`/`reviewer_route` and 14 model worktree reservations although execution authority is the human owner | Material |
| F13 | RV-* rows reuse `author_worktree` for a read-only source reference, and their author/reviewer writable sets are identical | Material |
| F14 | No correction-reserve field; reviewer (not author) session demand is the real bottleneck | Material |
| F15 | `routes.gemini.model` states an exact model string while the same entry says the selectable ID is unverified | Optional |
| F16 | Capacity percentages are recorded without remaining/used direction or reset window | Optional |
| F17 | `SW-VERSION-01` needs an explicit "author prepares, coordinator applies" field | Optional |
| F18 | Row-level `capacity_gate` text for followups differs from mapped units without stating why | Optional |

## 3. Per-phase assessment

**P0 residual (3 rows: `SW-AUDIT-01`, `SW-FINDINGS-01`, `SW-HARNESS-01`).** Coverage of the three
P0 obligations (source/finding inventory, minimal harness) is present and correctly sequenced
(`SW-HARNESS-01` depends on both inventories). MiniMax authoring both inventories matches the
route's demonstrated bounded-inventory competence; `sol` review is cross-family and appropriate.
Two defects: the uniform `remaining_disposition` erases the fact that `SW-FINDINGS-01` is
`integrated_triage_not_qualified` (F4), and P0 dispositions must be pinned to one count source
given F10. `SW-HARNESS-01` is the only row gating the whole P1 API/security block — accept it only
after the count reconciliation, or every downstream disposition inherits the ambiguity.

**P1 remainder (17 mapped + 12 followups).** Structurally the strongest phase: the followup chain
`QUAL → RV-* → EV-* → INTEGRATE-P1-CANDIDATES → EV-COMBINED-P1 → P1-PUBLISH-CHECKPOINT` is
explicit, acyclic, and its fixed candidates are exact. But it is the phase that carries F1–F6.
`QUAL-ANTHROPIC-CORE-01` is authored by `claude` (the route under test) with `sol` review and a
`claude` candidate-review dependency — acceptable only if the coordinator's disposition is
recorded as independent; the packet does not require that record. The three RV rows reuse the
retained candidate worktrees as read-only references while their author and reviewer writable sets
are the same paths (F13), and the 15 EV/integration rows carry no `prohibited` list, unlike all 65
mapped rows. The 17 mapped P1 units sit on `sol → claude` with no qualification dependency (F1).

**P2 (18 rows).** Broadest user-facing surface — UI, kiosk, scenes, macros, shortcuts, dashboard,
onboarding, editors, Flic. Route assignment (`sol → claude`) is consistent and the acceptance text
carries real negative controls (denied/cancel, hostile names, disconnect, duplicate-action checks).
Coverage gaps by text search: "accessibility" appears only in `SW-KIOSK-STATE-01/02` (touch
accessibility) and "onboarding"/"editor" only in `SW-UI-MANAGE-01/02`; no row names
onboarding/accessibility as a first-class deliverable, and no row mentions Remote 3 except
`OWNER-HIL-E`. With 6 feature IDs carried only in `feature_ids`, the duplicated package acceptance
(F9) leaves the actual per-unit deliverable ambiguous. P2 must not start until F1/F2 are settled,
because its 18 reviews all depend on the Anthropic reviewer route.

**P3 (22 rows).** `SW-PROTOCOL-PREP-*` (7) and `SW-RUNTIME-PREP-*` (7) share one package scope each
(F9) — a single "reconcile all ops/reliability paths" acceptance repeated seven times is not a
per-unit acceptance gate. `astra` authorship on runtime/UC prep and `sol` on protocol/HA is
defensible by the recorded specialisms (concurrency/lifecycle vs source/command semantics), but
`SW-UC-PREP-*` inherits `claude` review with no gate (F1). `SW-SOAK-PREP-01` is correctly bounded to
"audit the existing collector before proposing tooling" with no synthetic dataset admitted as soak
evidence; `SW-DOM-HIL-PREP-01` correctly defers physical effects and V4 acceptance.

**P4 (4 rows).** `SW-REPO-01` and `SW-DOCS-01` on `m3 → sol` fit the route's bounded
documentation/inventory competence; `SW-VERSION-01` (`sol`) and `SW-BUILD-01` (`astra`) correctly
refuse release/tag publication. Two real defects: the 5 already-accepted units' statuses are lost
in the uniform `remaining_disposition` (F4, `SW-REPO-01` is `integrated_source_inventory_not_qualified`),
and `SW-VERSION-01` has 24 package dependencies but no dependency on the P1 publication checkpoint,
so a version candidate could be assembled from a branch that omits the accepted P1 candidate source
(F6). P4 also lists `SW-DOCS-01` with 7 dependencies and `tests/validation` reuse implied by
`SW-SEC-AUTH-01`'s real browser-driver lease (F7).

**P5 (1 row) + owner gates (7 rows).** `SW-SOFTWARE-GATE-01` is the only P5 row and correctly requires
147 software-target proofs, 120 V4 + 1 V5 prerequisite dispositions, current-head CI and exact push
equality. Package reachability verified: all 65 packages reach the P5 gate transitively. The seven
owner gates (HIL-B/C/E, physical CEC, 72h soak, field week, final release) correctly declare
`execution_authority` = explicit owner session and `model_operator` = human owner, and correctly
keep RC digests unresolved (`fixed_sha: null`, "resolve from accepted SW-BUILD output"). The three
original Tron approvals remain closed: `visual baselines` is in every mapped row's `prohibited`
list and no row proposes a visual change. Defects: the 7 rows still name model author/reviewer
routes and reserve 14 model worktrees (F12); their base omits the floor assertion and the explicit
`SW-BUILD` dependency (F5); and `OWNER-SOAK-72H`/`OWNER-FIELD-WEEK`/`OWNER-FINAL-RELEASE` are
mutually ordered only by prose.

## 4. Overall staffing decision

Do not authorise the pinned matrix as-is. The coverage, dependency and base-pinning structure is
sound and the manifest fidelity is exact, but two conditions block execution:

1. **Reviewer qualification is a program gate, not a per-row footnote (F1).** 73 of 84 rows — every
   source, security, protocol, runtime, UI, build and P5 audit row — route review to Anthropic
   while Anthropic's source/security-review competence is still unproven. `QUAL-ANTHROPIC-CORE-01`
   is `not_launched`, sits in P1, and no row declares it. Encoding it as a dependency on all 73
   rows (or as a program-level prerequisite that blocks P1–P5 authoring) is required before any
   reviewer session is dispatched.
2. **There is no dispatchable fallback reviewer (F2).** Gemini is held and unverified; MiniMax has
   no core/security review qualification; `sol`/`astra` are one family and cannot review each
   other's work. If Anthropic qualification fails or headroom drops below 30%, 73 rows have no
   eligible reviewer and the affected dispatches must be held, not reassigned silently. This must
   be recorded as an explicit program risk with the hold rule, not as an implicit fallback array.

Also blocking (both mechanical, both cheap to fix): the packet hash normalisation (Section 1) and
the P1 publication dependency (F6). Author capacity itself is adequate: the observed 89% weekly /
98% session MiniMax headroom covers the bounded inventory/prose rows only, and the packet's
`capacity_commitment` correctly refuses to fund the whole backlog — that honesty should be kept.
Wave packing (F11) and correction reserve (F14) must be settled before the first wave opens.

## 5. Material requirements (with exact row/field corrections)

| ID | Requirement | Rows / fields |
| --- | --- | --- |
| R1 | Add `qualification_gate: "QUAL-ANTHROPIC-CORE-01"` and a `dependencies` entry to every row whose reviewer is `claude` and whose scope is source/security review | all 73 `claude`-reviewer rows |
| R2 | Record Gemini as **unavailable** fallback, not a fallback; state the hold rule when Anthropic qualification or headroom fails | `fallbacks[].status` on all 65 mapped rows |
| R3 | Add pin rows (or explicit parent residual entries) for the three corrective children with their exact submitted SHAs and pending states | `SW-API-READ-04-C1`, `SW-API-CLIENT-02-C1`, `SW-SEC-DATA-02-C1` |
| R4 | Make `remaining_disposition` per-unit and distinct for the five non-planned units; forbid reopening published scope | `SW-FINDINGS-01`, `SW-API-READ-01`, `SW-API-READ-02`, `SW-SEC-AUTH-01`, `SW-REPO-01` |
| R5 | Add `requires_ancestor_floor: true` and `dependency_outputs` to the 8 followup rows; add floor assertion plus explicit `SW-BUILD` dependency to the 7 owner gates | 15 rows |
| R6 | Make `P1-PUBLISH-CHECKPOINT` a dependency of `SW-VERSION-01` and `SW-SOFTWARE-GATE-01`; add `EV-FLIC-ADMISSION` to `EV-COMBINED-P1` | 3 rows |
| R7 | Restore each unit's manifest `shared_path_lease` text verbatim into `shared_paths` | all 65 mapped rows, esp. `SW-SEC-AUTH-01` |
| R8 | Mark pre-existing accepted files as preserve/lease rather than free-write | `SW-API-READ-01`, `SW-API-READ-04`, `SW-SEC-AUTH-01` path lists |
| R9 | Join `feature_ids` and the unit's own scenario/test files into per-unit acceptance | 52 units across 17 packages |
| R10 | Pin one authoritative count source and correct the divergent figure | `SW-AUDIT-01`, `SW-FINDINGS-01`, `EV-CI-ATTRIBUTION`; `BASELINE.json` vs `manifest.json` |
| R11 | Add a launch-batch/concurrency field sized to the ≤2-worker ceiling | all 65 mapped rows (`suggested_wave` retained as dependency tier only) |
| R12 | Model owner gates as owner-operated: no model author/reviewer route, no model worktree reservation | 7 `external_gate` rows |
| R13 | Split RV rows into `source_reference_worktree` + execution tree, with disjoint author/reviewer writable paths | `RV-PRIVACY-CHAIN`, `RV-WS040`, `RV-API034` |
| R14 | Add a `correction_reserve` (fix + re-review sessions) and a per-wave reviewer-session budget | all rows |
| R15 | Republish `DRAFT_PACKET.json` input hashes over committed LF bytes (content already confirmed unchanged and identified by `19ee8be9`), state the normalisation, and correct the HANDOFF hash to the pinned commit | `DRAFT_PACKET.json`, `BASELINE.json` |

## 6. Optional improvements

- **O1** Drop or explicitly alias the exact model string in `routes.gemini.model`.
- **O2** Record remaining-vs-used and reset windows for every capacity percentage.
- **O3** Add a "coordinator applies shared/root metadata" flag to `SW-VERSION-01`.
- **O4** Unify `capacity_gate` wording across kinds, noting why followups differ.
- **O5** State in `PROGRAM.md` that P2 accessibility/onboarding/Remote-3 text coverage is deliberate
  or add a row.
- **O6** Record the coordinator's independent disposition artifact for `QUAL-ANTHROPIC-CORE-01`.

## 7. Evidence and acceptance

Every claim above is derived from the frozen packet, `docs/planning/software-waves/manifest.json`,
`PACKAGES.md`, `docs/validation/LEDGER.md`, `docs/production/AGENT_ALLOCATION.md` and
`docs/agent-process/state/HANDOFF.md`, and from programmatic cross-checks (row/field diffing,
family matrix, dependency-graph and reachability analysis, path-collision analysis, git blob
hashing, worktree head/status verification) recorded in the private subtree
`build/execution-pinning-20261101/minimax/round1/` (analysis script, analysis outputs, and the
documentation-check JUnit copy with its SHA-256). No peers' reports were read. No source, tests,
tooling, registry, ledger, evidence, baseline, root manifests or canonical pins were modified; the
only tracked file added is this report.

## 8. Limits

Planning assessment only. This report does not claim consensus, phase approval, reviewer
qualification, source/security correctness, physical HIL, 72-hour soak, week field sign-off, or
release readiness; it does not evaluate any peer's findings, does not authorise any dispatch, and
does not assert verified native model identity for any route.
