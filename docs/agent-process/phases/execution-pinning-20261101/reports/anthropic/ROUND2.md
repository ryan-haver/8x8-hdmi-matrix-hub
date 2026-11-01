# Round 2 peer challenge — Anthropic

- Native Claude Code `claude-opus-4-7` effort `high`; planning only. No source/security review qualification claimed; no consensus asserted.
- Task `task_ed036ba1631f`, Dispatch `ctx_873c66e53a6c`, Run `run_37205f6095b3`, coordinator `term_15310037-…` gen4.
- Worktree `wp-pins-anthropic-20261101`, HEAD `a973922ae39821e8e30e912dc59aeaddcf78f6ed` (clean), planning floor `e2161484…`. R1 preserved unchanged.
- Observed Anthropic weekly usage before this round: 86%.
- Scope: bounded peer challenge of the three R1 reports and the `RECONCILIATION_R1.md` / `PROGRAM_V2.md` / `CHALLENGE_SUMMARY.md` / `CHALLENGE_EXECUTION_PINS.json` revision. No source, test, tooling, registry, ledger, canonical-pin, baseline or peer-report edits.

## Input integrity

`CHALLENGE_PACKET.json` sha256 **`c1ed1f07…8293`** matches the brief. All nine declared member hashes reproduce exactly against raw UTF-8 LF bytes (`Path.read_bytes`). `INPUT_INTEGRITY_ERRATUM.json` preserves the original R1 CRLF-vs-LF drift honestly without rewriting the old packet. **No substantive drift**: all three R1 reports were bound at `19ee8be9…`, which is the packet's `source_floor`.

## Challenges to peers

**Anthropic R1 (my own):** P4 prose swaps SW-DOCS/SW-BUILD author labels — actual rows are `m3→sol` for SW-DOCS and `astra→claude` for SW-BUILD. Prose mislabel only; the row-level M-7/M-8 corrections remain valid.

**MiniMax R1:**
- F2 understates: `fallbacks[1]` carries a conditional `claude→sol` route (future *new* authorship after qualification and settlement) — bounded, but more than "Gemini only".
- F11 ("no field encodes batching") is wrong against R2: `launch_batch.max_active_workers = 2` plus a strategy string (shortcut-before-present, exclusive-paths overlap) is on each mapped row. The residue — wave 10 still packs ≥14 rows under a 2-worker ceiling — stays as an operational point.
- F7's "live" lease on `tools/validate/clients/browser.py` + `browser_driver.mjs` is reframed as *historical* text preserved for traceability, with `historical_manifest_shared_path_lease` fields present on affected rows (spot-checked). The "live" wording is no longer accurate.
- F3 (missing C1 corrective pin rows) is dispositioned as parent residual entries with each submitted SHA and pending state in `corrective_child_dispositions` on SW-API-READ-04 / SW-SEC-DATA-02 / SW-API-CLIENT-02. A new row per child would duplicate accepted history.

**OpenAI R1:**
- P0 scoped-intake escape **not fully resolved**: SW-HARNESS-01's `dependencies` still read `required_state: accepted_integrated_published` on the SW-AUDIT and SW-FINDINGS *packages*. The reconciliation prose adopts scoped intake, but the row carries no `scoped_intake_slices` field encoding the escape. Thin but real structural gap.
- RV path-collision concern resolved: RV rows now split source-reference, review workspace and evaluation workspace (`wp-exec-rv-*-review` vs `wp-exec-rv-*-review-evaluation`).
- P5 ask satisfied: OFR deps now include HIL-B/C/E, PHYSICAL-CEC, SOAK-72H, FIELD-WEEK plus SW-SOFTWARE-GATE-01/VERSION/BUILD and QUAL.

**Shared agreement:** all three R1 reports converged on QUAL-ANTHROPIC-CORE-01 as the gate; the revised matrix now carries it as an explicit `dependencies` entry on **all 75** `claude`-reviewer rows (verified by direct JSON scan). The invariant is at the scheduler, not only in prose.

## Position by phase

| Scope | Position | Material residual |
| --- | --- | --- |
| Program direction (PROGRAM_V2) | Honest: reservations, three-family three-round, no DeepSeek, Gemini held, Anthropic conditional, owner gates human-only. | None material. |
| P0 residual (3 rows) | Coverage and sequencing sound; SW-HARNESS-01's QUAL dep now present. | OpenAI P0 scoped-intake escape not encoded as a row field. |
| P1 remainder (30 rows: 17 mapped + 13 follow/review/closure) | P1-ACCEPTANCE-CLOSURE depends on all 15 mapped P1 units + 2 corrective children + Flic admission + CI + preservation gaps + publish checkpoint + QUAL. EV-COMBINED-P1 now includes EV-FLIC-ADMISSION. RV rows split review vs evaluation. | SW-REPO-01 completion still only names SW-FINDINGS at the dependency level (reconciliation defers to acceptance prose). |
| P2 (18 rows) | All sol→claude with QUAL dep; launch_batch encodes shortcut-before-present. | Wave 10 (P3) and dense P2 waves still exceed the 2-worker ceiling at the dep-tier label; concurrency is bounded only at launch, not in the row. |
| P3 (22 rows) | SW-SOAK-PREP-01 reassigned m3→sol with qualified cross-family review. SW-DOM-HIL-PREP-01 shortcut dependency added. | None material beyond the wave-10 observation. |
| P4 (4 rows) | SW-VERSION-01 now depends on P1-ACCEPTANCE-CLOSURE + P1-PUBLISH-CHECKPOINT + 24 packages. | SW-REPO-01 inventory-first scope accepted; verify in Round 3 that its *completion* acceptance names remaining-source dispositions. |
| P5 (1 row) | SW-SOFTWARE-GATE-01 has 67 explicit deps covering every mapped software/prep row, both P1 closures and QUAL. | None material. |
| Owner gates (7 rows) | `dispatch_allowed_now: False`, `owner_gate: True`, `execution_authority = explicit owner session`, `model_operator = human owner` on all seven. Author/reviewer slots retained as runbook/evidence assistance. | None material; the retained model slots are explicitly non-dispatch. |

## Residual material requirements (Round 3 prerequisites)

1. **R2-M1 (P0):** encode OpenAI's scoped-intake escape as a row-level field on SW-HARNESS-01 (`scoped_intake_slices: [slice_id, published_sha, remaining_obligations]`) so the resolver cannot wait for a full-package close that the program has already said is not required.
2. **R2-M2 (P4):** either add explicit remaining-source dispositions to `SW-REPO-01.completion` dependencies or state in `scope` that P5 is the enforcement point for roll-up (reconciliation implies this; row does not).
3. **R2-M3 (P2/P3 waves):** add `concurrent_batch_bound` or equivalent to each row inheriting a dense wave label (10, 7, 8, 9) so the 2-worker ceiling is machine-enforced, not relied on only at wave preflight.

## Optional (non-blocking)

- Spell out in `fallbacks[0].status` that Gemini is **not available headroom** (current text "held until … verified" is correctly non-committal but reads thinner than MiniMax R2 asked).
- Record a per-wave reviewer-session budget (correction_reserve already exists per row; a wave-level roll-up would help the two-worker scheduler).

## Statements I am not making

I do not claim consensus, final approval, Anthropic source/security review qualification, admission of any private evidence body, or authorization of any owner gate. No peer R2 reports were opened. The private subtree `build/execution-pinning-20261101/anthropic/round2/` holds no raw evidence, credentials, native transcripts or baselines; only this report is tracked.
