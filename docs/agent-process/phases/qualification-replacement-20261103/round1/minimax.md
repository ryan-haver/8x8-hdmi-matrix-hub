# Qualification replacement 20261103 — Round 1 independent assessment (MiniMax)

Participant MiniMax, native `minimax-coding-plan/MiniMax-M3`; effort thinking inherited, CLI effort override unsupported. Frozen input `INPUT_PACKET.json` SHA256 `fc658cfb4d6223f8f7015733da95b3456192755a2daef818141fe5980dbb9bc9` verified; `AUTHORIZATION.json` read beside it. Base `d00bf26b0bf5fca45ffed6f3e32b4cc7f5767de1`, branch `planning/qr-20261103-r1-minimax`. No peer R1/R2/R3 report, native trace or peer synthesis read; no candidate execution, source review, test rerun or campaign; no source or qualification acceptance claimed.

## Verified scope facts (Git metadata only)

- The nine-path population is complete only at `caaa4fa`. At base `d00bf26` five paths are absent (C2 AUTHOR/INTAKE, `sw_api_client_02_c1.py`, the c1/c2 tests). An evaluator worktree based on `d00bf26` or the integration branch under-covers.
- Window deltas: `3868723` adds C1 AUTHOR, a features.yaml line, c1 scenario+test; `060769b7` edits **only** C1 AUTHOR (+111, "route-all partial acceptance") — the commit attempt-02's evaluator denied reading; `ee3f2e7` adds C2 AUTHOR/INTAKE, edits the c1 scenario, adds the c2 test, edits `tools/validate/model.py` and `runner.py` (the only in-window code changes); `caaa4fa` edits **only** C2 AUTHOR (+103) claiming "managed proof and failed global gate".
- Both Opus 4.7 FAILs stand: attempt-01 (behavior_and_tools/calibration/review_quality), attempt-02 (provenance/calibration/review_quality; J1 un-reviewed `060769`, J2 ignored/private proof called published, J3 mis-stated population).

## Assessment — proceed, with binding conditions

The candidate/judge split matches demonstrated competence: OpenAI authored this C1/C2 window and judged both 4.7 attempts; Anthropic 5.5 has no evidence here, so its run is a competence test, not a formality; MiniMax is planning/inventory only and must not judge or candidate-qualify. The final hashed packet must carry these controls or R3 is require_changes.

**Goals / non-goals.** Goal: one bounded qualification decision for Opus 5.5 under the unchanged six-axis rubric at `caaa4fa`, with one fresh OpenAI judgement. Non-goals: source acceptance, any privacy/HA/hardware/release change, retry of either 4.7 attempt, new accounts or credit.

**Entry.** Native `claude-opus-5-5/high` attested at dispatch (catalog presence is not availability); verified judge route with headroom ≥30% plus correction reserve; evaluator worktree pinned at `caaa4fa` with diff review from `938ae3`; all four lineage commits reachable.

**Exit/acceptance.** Six explicit axis verdicts (unknown = hold) at the exact evaluator report commit; no lost or relabelled bytes; one fresh OpenAI report; coordinator records a bounded domain only.

**Controls.** (a) Coverage: full four-commit window diff including `060769b7`; all nine paths read at `caaa4fa`; populations derived from actual records including blocked controls. (b) Proof: ignored or private artifacts labelled ignored; a published claim needs tracked bytes. (c) Calibration: the FSEC007 global freshness/level failure stays historical — no unchanged retry, no waiver; no termination cause asserted without direct exit evidence.

**Risks and boundaries.** Recurrence of provenance/calibration/review_quality failure is the modal outcome; a second FAIL ends this route pending owner direction, with no automatic retry. Exclusive paths: evaluator = own new report path plus ignored scratch; judge = own new review path at the evaluator commit; source, tests, tools, features.yaml, registry, ledger and root manifests immutable.

**require_changes / hold.** Hold if the final packet omits the evaluator base `caaa4fa` with a nine-path manifest, omits the four-commit/`060769` coverage obligation, treats ignored artifacts as published proof, leaves F-API-034-style populations unverified, or lacks natively attested routes with checked headroom.

```json
{
  "round": 1,
  "participant_family": "MiniMax",
  "actual_model": "minimax-coding-plan/MiniMax-M3",
  "effort_or_native_limit": "thinking inherited; CLI effort override unsupported",
  "frozen_input_sha256": "fc658cfb4d6223f8f7015733da95b3456192755a2daef818141fe5980dbb9bc9",
  "recommendation": "proceed",
  "material_conditions": [
    "evaluator base caaa4fa + nine-path manifest; d00bf26 lacks 5 paths",
    "full four-commit window diff incl. 060769b7 must be read, not excluded",
    "ignored/private artifacts labelled ignored; published claims need tracked bytes",
    "populations derived from actual records incl. blocked controls",
    "FSEC007 failure historical; no retry/waiver; no unproved termination cause",
    "one attested native candidate, one fresh OpenAI judge, no auto-retry",
    "no source, domain, privacy, HA, hardware or release acceptance from this stage"
  ],
  "peer_reports_read": false,
  "source_or_qualification_acceptance": false
}
```
