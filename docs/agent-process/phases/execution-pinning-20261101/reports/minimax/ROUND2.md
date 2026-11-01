# Round 2 peer challenge — execution pinning 2026-11-01 (MiniMax / OpenCode 2)

Route: `minimax-coding-plan/MiniMax-M3` via native OpenCode 2 (variant `thinking`; CLI effort unsupported). Genuine peer
challenge of the three Round 1 assessments and the coordinator's dispositions, tested against the actual rows. **No consensus,
phase approval, reviewer qualification, source acceptance or release readiness is claimed.**

## 1. Basis and integrity

`CHALLENGE_PACKET.json` SHA-256 is `c1ed1f07…82293`, matching the required value; all nine member hashes match their raw
UTF-8 LF bytes and every file on disk is LF. The erratum's CRLF claim reproduces: CRLF expansion of each legacy input
reproduces its old declared hash.

Census: 85 rows = 65 `mapped_unit` + 9 `followup` + 3 `review` + 1 `acceptance_closure` + 7 `external_gate`; phases P0=3,
P1=30, P2=18, P3=22, P4=4, P5=1, OWNER=7; 30 packages. Feature contracts: 268 unique, 268 `feature_contract_refs`, 1:1 with
`feature_ids`, no orphan or duplicate; V2+V3 = 147 software, V4=120, V5=1, all 121 hardware/field features carry owner-gate
`proof_scope`. Graph: 0 cycles, 0 dangling refs; `P1-ACCEPTANCE-CLOSURE` reaches all 29 other P1 rows, `SW-SOFTWARE-GATE-01`
all 65 mapped plus 13 residual rows. Independence: 0 same-family pairs (sol→claude 64, astra→claude 11, m3→sol 6, claude→sol
4), 0 writable-path collisions or intra-row overlap, 170 unique reserved worktree names. Nothing fabricated: `task_id`/
`dispatch_id` null everywhere, `dispatch_allowed_now=false` throughout, only the three retained read-only references carry a
real worktree id. Five documentation modules: 489 passed (`-p no:tests.route_inventory -p no:cacheprovider`, fresh
forward-slash basetemp; JUnit SHA-256 `60e47c58…e985fb`).

Peer R1 arithmetic re-checked against the **draft**: 84 rows = 65+12+7, Claude reviewer on 73, `QUAL-ANTHROPIC-CORE-01` in
dependencies on 3, Gemini fallback on 60 — Anthropic's and OpenAI's counts reproduce exactly. Anthropic's P4 prose does swap the
`SW-DOCS`/`SW-BUILD` routes; the coordinator's correction is right.

## 2. Where the revision genuinely closes Round 1

Verified as landed, not asserted: Anthropic M-1/M-2/M-3/M-5/M-6/M-9, OpenAI P1/P1-P5/P3/P4-P5 and MiniMax
F3/F4/F6/F7/F8/F10/F11/F13/F14/F16/O1 are satisfied in the rows. Spot-verified: all 75 Claude-reviewed rows carry both
`qualification_gate` and a `QUAL-ANTHROPIC-CORE-01` dependency; all 13 residual rows populate `review_independence`,
`prohibited` and `demand_class`; the three RV rows have a retained read-only source reference, a separate execution tree and
disjoint `REVIEW.md`/`EVALUATION.md` ownership; `P1-ACCEPTANCE-CLOSURE` is coordinator-executed and gates `SW-VERSION-01` and
the P5 gate; `SW-SOAK-PREP-01` moved off M3 and all 6 M3 rows are inventory-bounded; owner release depends on all six
physical/soak/week gates plus version/build; Gemini is `model=null`, held. All 85 rows list `visual baselines` in `prohibited`.

## 3. Remaining material blockers

**B1 — `RV-API034` scope still names the base the coordinator rejected.** `RECONCILIATION_R1.md` corrects RV-API034's review
base to `938ae303` (verified parent of `386872`), and `base_pin.review_base_sha` matches. But the scope's **first operative
clause** still reads "Review managed disconnected preparation source `ee3f2e7f` **against `060769`** at submitted `caaa4faa`",
with only a later clause disclaiming `060769`. Git confirms `060769`'s parent is `386872`, so diffing `ee3f2e7f` against
`060769` excludes the original unreviewed OpenAI commit — the error the correction rejected. `RV-WS040` and `RV-PRIVACY-CHAIN`
are consistent; this row is not. *Fix:* diff against `938ae303`.

**B2 — `SW-REPO-01`'s roll-up sits in a one-off field the resolver does not read.** `dependencies`/`dependency_unit_ids` show
only `SW-FINDINGS-01`; the 60-unit roll-up lives in `completion_dependencies`/`completion_dependency_unit_ids`, a key on exactly
1 of 85 rows, while `dependency_resolver` references only `dependencies`/`dependency_unit_ids`. A scheduler reading that field
treats `SW-REPO-01` as `SW-FINDINGS`-gated only. *Fix:* promote the roll-up into `dependency_unit_ids`, or declare
`completion_dependency_unit_ids` binding in `dependency_resolver`. (Omitting `SW-VERSION-01`/`SW-BUILD-01` is correct.)

**B3 — `SW-SOFTWARE-GATE-01` contradicts itself on who runs the gate.** `executor=orca_supervised_worker`, yet its scope says
"**Coordinator** runs the complete applicable source/client/UI/UC/HA/Flic/image/packaging pipeline … and serial
registry/ledger/formal gate." The four sibling coordinator-owned rows use `executor=coordinator_only` with `worker_routes_scope`.
The P5 gate — where the serial ledger rules bind — is typed as a worker. *Fix:* set `executor=coordinator_only`, add
`worker_routes_scope`.

**B4 — `SW-DOCS-01` can document auth and clients against unaccepted source.** Its scope promises "exact flags/ports/**auth**"
and "**client** … docs with accepted software", but `dependency_unit_ids` includes `SW-API-WRITE-01..04`, `SW-SEC-DATA-01/02`
and the UI/kiosk/Flic/UC/HA units while excluding `SW-SEC-AUTH-01/02`, `SW-API-CLIENT-01/02`, `SW-API-READ-01`,
`SW-DOM-PROFILE-01`. M-8 closed the writes/privacy/UI portion only; the auth/client gap was missed. *Fix:* add those six units to
`SW-DOCS-01.dependencies`.

**B5 — the reviewer route remains a program-level single point of failure.** 75 of 85 rows require Claude; the only
different-family alternative is Gemini (held, `model=null`) or same-family (prohibited). The packet states this honestly
(`review_bottleneck`; `fallback_disposition`: "Unknown Gemini is not spare capacity and same-family review is prohibited"),
which satisfies disclosure — but it is a live risk: if `QUAL-ANTHROPIC-CORE-01` fails, 75 rows hold with no eligible reviewer.
*Requirement:* treat a declined qualification as a program-scoped hold, and pre-identify packages that can proceed on M3/OpenAI
routes without Claude review.

## 4. Optional improvements

- **O-a** OpenAI (Sol) evaluating Claude's review of OpenAI-authored code is a self-interest conflict;
  `secondary_evaluation_scope` bounds it, but no field names where the coordinator's pass/hold/fail disposition lives. Add
  `coordinator_disposition_artifact` to `QUAL-ANTHROPIC-CORE-01` and the `RV-*` rows.
- **O-b** `executor=candidate_evaluator_then_independent_judge` is a third executor value outside the vocabulary; enumerate
  executors in the schema.
- **O-c** `executor`/`auto_dispatch_allowed` gate the seven owner rows adequately, but `author_route`/`reviewer_route` still read
  `sol`/`claude` and 14 model worktrees stay reserved; rename to `assistance_*` so a route-keyed scheduler cannot misread them.
- **O-d** Wave 10 holds 14 P3 rows; the ≤2-worker `launch_batch` handles concurrency, but 10a/10b/10c aids legibility.
- **O-e** 52 of 65 mapped units still share their package's `scope` verbatim; `unit_focus`, `feature_contract_refs` and
  `new_test_scenario_reservations` are distinct per unit, so acceptance is unit-discriminating — say so.
- **O-f** Gemini is `model=null`, but 61 mapped rows still name Gemini in `fallbacks[]`; a separate `held_routes[]` list would
  remove the ambiguity.

## 5. Per-phase position

| Phase | Position | Blocking corrections before any Round 3 verdict |
| --- | --- | --- |
| Program | Sound: reservations, gates, honest capacity, no-fabrication posture verified | Carry B5 as a standing program risk, not a resolved risk |
| P0 residual | Coverage and sequence sound; M3 rows correctly inventory-bounded | None |
| P1 remainder | Closure complete and transitively sound; 75/75 Claude-review rows correctly gated | B1; B5 applies to every P1 review |
| P2 | Feature allocation verified (accessibility, editors, Remote 3 info all land in P2 rows) | None |
| P3 | Coverage sound; `SW-SOAK-PREP-01` correctly moved to qualified source authorship | B5; O-d optional |
| P4 | Docs/security scope honest, but dependency sets contradict stated scope | B2, B4; B3 is P5-adjacent |
| P5 | Gate reach complete and coordinator intent clear, but executor typing conflicts with scope | B3; B5 |

## 6. Limits

I do not claim consensus. The revision is a large, verifiable improvement over the draft, and the Round 1 dispositions carried
through are satisfied. **B1–B4 are concrete row/field corrections to apply before any Round 3 verdict; B5 must be recorded as a
standing program risk.** Nothing here qualifies a source reviewer, approves product behaviour, admits raw evidence, authorises a
dispatch, or satisfies any physical, soak, field or release gate.

Private evidence: `build/execution-pinning-20261101/minimax/round2/`. No shared packet, source, tests, tooling, registry, ledger,
baseline, manifest or earlier report was modified; this report is the only tracked file added.
