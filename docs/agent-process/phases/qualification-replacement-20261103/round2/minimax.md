# Qualification replacement 20261103 — Round 2 peer challenge (MiniMax)

Participant MiniMax, native `minimax-coding-plan/MiniMax-M3`; effort thinking inherited, CLI effort override unsupported. Frozen input `ROUND2_INPUT_PACKET.json` SHA256 `a1d5beb25ba6ff7b493b498c9974f8e7b4c834b2629097233b55228243d9e84c` verified first; `AUTHORIZATION.json` and `ROUND1_BARRIER.json` read beside it. All three R1 reports read in full via `git show <head>:<path>`, canonical SHA256 and bytes matching (4458/4931/5138). No R2/R3 peer report read; no candidate execution or acceptance claim.

## Dispositions C1–C7

- **C1 accept+strengthen.** The `caaa` checkout is right; Anthropic's integration-base worktree is rejectable — `merge-base(caaa4faa,a2f85019)`=`938ae303` (review base), so no window commit is on that line and only four of nine paths exist there. Bind the window to the rubric's frozen `review_base_sha`→`candidate_sha`; evaluator pinned at `caaa4faa`; judge at its report commit whose parent is `caaa4faa`. Rubric and dispositions are absent there: supply coordinator-pinned bytes.
- **C2 accept.** Frozen rubric bytes unchanged; four-commit/nine-path window governs; per-path/per-commit coverage with real tool reads. Rubric `source_commits`=[`38687231`,`ee3f2e7f`], but its frozen base/candidate SHAs span all four commits. Drop the implication the shorthand caused J1: attempt-02 J1 says the evaluator claimed `060769b7` outside scope; cause not established.
- **C3 accept.** `38687231` adds the 220-line C1 test and 35-line scenario, so my R1 parenthetical ("only `ee3f2e7f` has code changes") was wrong; correct prospectively, keep R1 bytes.
- **C4 accept+correct.** No probability or weighted majority; "two different-family FAILs" is wrong — both judges OpenAI family. Attempt-01 failed behavior_and_tools/calibration/review_quality, attempt-02 failed provenance/calibration/review_quality; recurrence is calibration+review_quality only, and n=2 supports no rate. Disclose candidate-family conflict; three explicit R3 acceptances required.
- **C5 accept+additions.** Derive populations from commands; never hard-code "54" or "489". Static, unexecuted, parametrize counting of the two committed modules at `caaa4faa`/`ee3f2e7f` gives 13+30=43 cases against the historical 54 passed — record the gap, don't reconcile silently. Keep blocked counts, tracked-at-commit vs task-ref-published vs ignored/private labels (`build/` tracked=0), unknown termination cause/descendant census, no absolute no-side-effect claims.
- **C6 accept.** One documentation invocation after prose is final; `os.environ.copy()` with SystemDrive/SystemRoot/USERPROFILE intact, sanitize receipts not OS variables, no `-I`; keep both 4.7 FAILs; reserve is not retry authority.
- **C7 accept+additions.** Refresh pool and reset before R3 and the judge: at 18:14Z codex weekly was 62% used (38% remaining), other-host demand unknown, and R3 planning, judge and corrections share it. Require ≥30% remaining before judge dispatch; unknown/below holds only the affected dispatch; no family substitution; one attempt, one judge.

OpenAI's require_changes, coverage matrix, unanimity and refresh-before-stage accepted; its headroom (79/40/76%) predates the packet's 79/38/75%. My R1 errors stay visible: the `ee3f2e7f` parenthetical (C3), the recurring-axes set (C4), "OpenAI authored this window" (C1 was DeepSeek-authored).

## Recommendation

**require_changes** on the coordinator's draft, not blocked: fold the C1/C4/C5/C7 amendments into the single hashed final packet, then all three R3 accept it. No source or qualification acceptance.

```json
{
  "round": 2,
  "participant_family": "MiniMax",
  "actual_model": "minimax-coding-plan/MiniMax-M3",
  "effort_or_native_limit": "thinking inherited; CLI effort override unsupported",
  "frozen_input_sha256": "a1d5beb25ba6ff7b493b498c9974f8e7b4c834b2629097233b55228243d9e84c",
  "peer_reports_read": [
    "9108174ed78056ca1732228b33b8379ae7fca6b8",
    "6307afb565a8b564536185079d9e16118512dab9",
    "914103e8ba5707ac203959ebf5e5c59d57a3a1c5"
  ],
  "recommendation": "require_changes",
  "challenge_dispositions": {
    "C1": "accept+strengthen: evaluator at caaa4faa; rubric/dispositions pinned as bytes",
    "C2": "accept: frozen rubric; four-commit nine-path window; no J1 causal claim",
    "C3": "accept: 38687231 also adds scenario and test code",
    "C4": "accept+correct: no weighted majority; one judge family; recurrence calibration+review_quality",
    "C5": "accept+add: no fixed 54/489 populations; 43 static cases; labels kept",
    "C6": "accept: one docs invocation; env.copy with Windows vars; no -I; no retry",
    "C7": "accept+add: refresh pool before R3/judge; 30% codex headroom; one attempt one judge"
  },
  "unresolved_material_conditions": [
    "rubric and prior dispositions absent from caaa4faa; pinned bytes needed",
    "54 focused passes versus 43 static cases must be derived",
    "codex headroom and other-host demand refresh before R3/judge",
    "candidate-family conflict disclosure; three R3 acceptances",
    "no verified alternate qualification pair; no second attempt/judge"
  ],
  "source_or_qualification_acceptance": false
}
```
