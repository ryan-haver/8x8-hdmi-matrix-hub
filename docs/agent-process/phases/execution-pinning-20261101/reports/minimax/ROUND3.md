# Round 3 final decision — execution pinning 2026-11-01 (MiniMax / OpenCode 2)

Route `minimax-coding-plan/MiniMax-M3` via native OpenCode 2 (variant `thinking`; CLI effort unsupported). Planning only.
Task `task_2549113a8ba4`, Dispatch `ctx_53a31ed6e909`, Run `run_37205f6095b3`; worktree `wp-pins-minimax-20261101` at
`ed4bbd934a4059dd5c750351b7d86e54b8bb0342` (clean). **This is one family's explicit decision; I claim no consensus and
no agreement with the other two families.**

## 1. Basis

`FINAL_PACKET.json` SHA-256 is `52ed758e711891ee57be0bbadb87c688333049733e697a52829cf0ba87d7b15e`, matching the required
value. All 12 declared member hashes reproduce exactly against raw bytes (`FINAL_EXECUTION_PINS.json`, `FINAL_PROGRAM.md`,
`RECONCILIATION_R2.md`, `FEATURE_CONTRACTS.json`, `INPUT_INTEGRITY_ERRATUM.json`, `RECONCILIATION_R1.md` and all six
R1/R2 reports). I read `FINAL_PROGRAM.md`, `RECONCILIATION_R2.md` and the anthropic/openai/minimax R2 reports, then
verified the final rows and fields directly against the shared read-only packet.

## 2. Decision on this exact packet

```json
{
  "packet_sha256": "52ed758e711891ee57be0bbadb87c688333049733e697a52829cf0ba87d7b15e",
  "program": "accept",
  "P0_residual": "accept",
  "P1_remainder": "accept",
  "P2": "accept",
  "P3": "accept",
  "P4": "accept",
  "P5": "accept"
}
```

Accept means the allocation and plan are accepted **with their encoded future gates**. It does not mean any future
execution, source qualification, evidence admission, physical action or release has occurred or is approved.

## 3. Reasons and risks

**The Round 2 corrections land as claimed.** B1: `RV-API034` reviews the chain against `938ae303` (including original
`386872` and follow-up `ee3f2e7f`) at submitted `caaa4faa`, and names `060769` only as the C2 author entry, never the review
boundary; `base_pin.review_base_sha` is `938ae303`, git confirms `caaa4faa` descends from it, and the parent of `060769`
is `386872`. B2: `SW-REPO-01` carries 60 completion dependencies in both `completion_dependencies` and
`completion_dependency_unit_ids`, and its `dependency_resolver.binding_fields` names both completion fields with
semantics that separate early inventory from completion. B3: `SW-SOFTWARE-GATE-01` is `coordinator_only` with
`worker_routes_scope`. B4: `SW-DOCS-01` binds `SW-SEC-AUTH-01/02`, `SW-API-CLIENT-01/02`, `SW-API-READ-01` and
`SW-DOM-PROFILE-01` alongside its write/privacy/UI dependencies.

**Anthropic R2's three requirements are met.** `SW-HARNESS-01` has `scoped_intake_slices` with `published_sha`,
`accepted_receipt` and `coordinator_authority` null, state "unbound; not launch authority", and explicit remaining
obligations; `pending_scoped_intake_ref` is null and the historical `F-API-002` intake is a dated reference only — no
fabricated future proof. `SW-REPO-01.completion` names its enforcement and the P5 refresh. `concurrent_batch_bound=2`,
`launch_batch.max_active_workers=2` and `slot_accounting` are on all 85 rows, so the two-worker ceiling is machine-readable
rather than a wave label.

**Structure holds.** 85 rows = 65 mapped + 9 followup + 3 review + 1 acceptance closure + 7 owner gates; 0 cycles, 0
dangling refs; 268 feature contracts 1:1 with `feature_ids`; 170 unique author/review workspace and branch
reservations; 0 same-family author/reviewer pairs. `P1-ACCEPTANCE-CLOSURE` reaches all 29 other P1 rows transitively and
all 17 mapped P1 units directly. `SW-SOFTWARE-GATE-01`, `P1-ACCEPTANCE-CLOSURE`, `P1-PUBLISH-CHECKPOINT` and
`SW-VERSION-01` are coordinator-owned; the seven owner rows are `human_owner_only`, `dispatch_allowed_now=false`,
assistance-only routes. `task_id`/`dispatch_id` are null on all 85 rows and `fixed_sha` is populated only on the 5
fixed-candidate rows; 73 future bases resolve from accepted dependency heads.

**Risks that survive acceptance (already encoded, not new defects).** All 75 `claude`-reviewer rows depend on
`QUAL-ANTHROPIC-CORE-01`, whose accepted author/reviewer artifacts are null and whose status states planning grants no
source qualification; a declined or unknown qualification holds only affected source reviews, while the six named
independent inventory routes (`SW-AUDIT-01`, `SW-FINDINGS-01`, `SW-REPO-01`, `SW-DOCS-01`, `EV-CI-ATTRIBUTION`,
`EV-PRESERVATION-GAPS`) continue under fresh capacity. A future qualified Anthropic-authored/OpenAI-reviewed combination
must be assessed before writing and never relabels retained OpenAI source. P0_residual and P1_remainder are therefore
partly QUAL-gated (`SW-HARNESS-01`, all RV rows, the qualification row itself); P2 and P3 are entirely `claude`-reviewed,
so their effective start is bounded by the same serialized Anthropic capacity, and wave 10's 14 rows are a dependency
tier with disjoint exclusive paths, not a simultaneous launch set. P4/P5 stay owner- and coordinator-gated: the 120
physical and 1 field features and the 72-hour soak and owner week remain unearned, and simulator proof cannot promote
physical effects. Minor non-blocking observations: `dependencies` arrays mix package-ref objects with bare unit-ID
strings (every string also appears in `dependency_unit_ids` and every package ref fully expands, so nothing is lost);
nine mapped units leave `new_test_scenario_reservations` empty (acceptance still discriminates them via unique
`unit_focus` and 1:1 feature refs); `SW-BUILD-01` lacks the `worker_routes_scope` field the coordinator-only rows carry.

## 4. Limits

I did not run a global master-plan audit, inspect historical native/private evidence, or modify any shared packet, pin,
source, test, tooling, schema, manifest, lock, registry, ledger, evidence, baseline or earlier report. I did not
dispatch, create worktrees, run services or campaigns, or touch physical, field or release actions. The five existing
documentation modules only were run for this report-only commit (489 passed; originals preserved and hashed under
`build/execution-pinning-20261101/minimax/round3/checks/`). Nothing here qualifies a source reviewer, admits evidence,
accepts product behaviour, authorizes a dispatch, or satisfies any physical, soak, field or release gate.
