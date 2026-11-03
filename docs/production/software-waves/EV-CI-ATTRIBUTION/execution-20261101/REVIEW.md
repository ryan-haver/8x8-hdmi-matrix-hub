# EV-CI-ATTRIBUTION independent factual review

**Verdict: require_changes.** All 56 unit mappings, the 11 cover sets, zero path intersections and the nonancestor freshness consequence reproduce. The full report needs seven bounded corrections below; a correct table does not validate its next-action and gate claims.

Reviewed [AUTHOR.md](AUTHOR.md) at exact commit `d86b65c271cc06d95895b8abdce53e24210bc6d9`, parent and declared entry `638a226a49b9cc0ead952a4a787d12c26dfcd35e`. Canonical author bytes: **23009**, SHA-256 `ba109a43eda015d24f8d1d33b93209711a82bcae9df829bef36f3012be44baca`. This reviewer checkout has a 23281-byte CRLF working copy, SHA-256 `56c2ac71298c54277ceba8de9d1277368dfe29303ca1fc4350a29a856352d04f`; replacing its 272 CRLF sequences with LF gives the canonical bytes exactly. That checkout conversion is not author drift; no author file was changed.

Authority: Task `task_e8646aacd637`, Dispatch `ctx_a83af2c61fa3`, worker `term_a775a4c0-605e-499c-b5d2-518a14b61870`, coordinator `term_6ed8131e-3ab3-4693-8094-56cc10acd412`, Run `run_37205f6095b3`. Assigned native OpenAI `gpt-6-astra/high`, different underlying family from MiniMax-M3 author; no helpers. Scope is factual metadata review, not source or privacy qualification. Shared-root task direction and current handoff govern historical worktree copies. Coordinator alone updates the allocation ledger and acceptance records.

## Verified scope and provenance

The accepted [OpenAI intake](../../SW-AUDIT-01/CI_EVIDENCE_INTAKE.md), report `9036ecffe2b5e18ccb6d636eba55edfbd0d6a80a` at frozen `490a879bd346773cca64fac861eaaab29e703628`, and [MiniMax independent review](../../SW-AUDIT-01/CI_EVIDENCE_REVIEW.md) retain their original inventory-only provenance. I reused their accepted record-own-covers equality to source definitions (56/56); I did not reopen original records, invent record hashes or reconstruct evidence. Accepted historical assertion, source/image/client/dirty/screenshot facts and 470 pass / 2 nonapplicable remain historical, not new execution or released-image proof.

New direct Git checks use explicit **entry638**, not this report-containing HEADd86. Source `bdcf06dc6723aad7da63ecfed3d3555ab0d02e55` is not an ancestor (exit 1); published `e16ec6af4d13c76c7024d42b605afec0c8ae9bf4` and frozen490 are ancestors (exit 0 each). Source and published trees equal `7fa5c9d99731349b0705fa2ef7818d5eb5a11350`; entry tree is `202fc21e0c514eb94e733a32846a09f026f2c4f7`. One reviewer-cached source-to-entry diff has 136 paths and equals the published-to-entry diff. Correct categories: AGENTS.md 1; docs/agent-process 39; docs/ORCHESTRATION_PROTOCOL.md 1; docs/planning 20; docs/production 75. Thus docs total 135 and overall total 136.

All 16 named objects match at source, entry and reviewer-start HEAD; the exact identities below make the declarative definition/client/target comparison bounded to those sources. Entry-to-d86 adds only AUTHOR.md. I imported seven own-checkout scenario declaration modules only after proving that identity, and read metadata without calling scenario.run or Expectation predicates. No source export or CI archive extraction was needed in this review.

| Path | Exact object at source = entry = d86 |
| --- | --- |
| `tests` | `4d88ac23cb6fd337098a556400318a346594ea23` |
| `tests/validation` | `ee5df750b039e419cb1f9b5d57dde653947bec4c` |
| `tests/validation/scenarios` | `6b57f0f945f48718e56eba9c0db5a5dec2e12246` |
| `tools` | `e474dabf5751b1b64deada5b5d6120f83553f3a3` |
| `tools/validate` | `820fe78054e328fa60369f86bd2851a196e02aeb` |
| `src` | `5b78baa117e7511a34c641f0f37bf9c9cfff7134` |
| `config` | `3c1fdbdb55adf628fb61cae365616b58c8a6296e` |
| `scripts` | `5238fac446f5e863a3926ac933266a9c21297638` |
| `run.py` | `2dac4fee22daab5ebf0212ed292c6d5bad08877b` |
| `web` | `9b0329a0a4453415000dc806673847cf1a76e10e` |
| `custom_components` | `49f8ee727125bcc64586915e72e6e3a2c71992d4` |
| `docs/api` | `b811e55fdb62045bb875dd2945ca5d8a0b0a3257` |
| `docs/validation` | `c143dd894290abc28cb00d49603b1f6841fb84f9` |
| `docs/validation/features.yaml` | `66720fb9b51dbf169239c7753a80d777d11d4de8` |
| `pyproject.toml` | `0781c6864d8df3897999eae9483f9b479220e3a6` |
| `requirements.txt` | `d805743975739e6f30c0847cb6d2358badca0abd` |

All U05-U60 scenario/client/level tuples match the accepted intake and author table, with 19 HA V3, 7 browser V3 and 30 API V2. Every declared client remains supported and target sim remains declared. The table below enumerates all 56 IDs; each group has zero intersections using the existing exact/prefix/fnmatch rule. Cover sizes and ordering also reproduce.

| Set | Covers | Verified units |
| --- | ---: | --- |
| C01 | 22 | U05 |
| C02 | 21 | U06, U07, U08, U09, U10, U11, U12, U13, U14, U16, U17, U21, U22, U23 |
| C03 | 22 | U15 |
| C04 | 23 | U18, U19, U20 |
| C05 | 20 | U24, U25 |
| C06 | 21 | U26, U27, U28, U29, U30, U31, U32, U33, U34, U35, U36, U37, U38, U39, U40, U41, U42, U43, U44, U45, U46, U47, U48, U49, U50 |
| C07 | 25 | U51, U52 |
| C08 | 28 | U53, U54 |
| C09 | 26 | U55, U56 |
| C10 | 24 | U57, U58 |
| C11 | 27 | U59, U60 |

Current [gitinfo.py](../../../../../tools/validate/gitinfo.py) returns None when source ancestry to HEAD fails; [ledger.py](../../../../../tools/validate/ledger.py), lines 33-45 and 98-100, returns unknown and collects nonfresh records as stale. Explicit entry ancestry plus unchanged rule objects establishes unknown/stale for all 56 at entry. Author private probe02 directly recorded head_at_check=entry638 and 56 unknown results; those are author receipts, distinct from my independent Git/static derivation. My additional changed_since(source) call ran at d86 and returned None; I do not present it as an entry-time call. No checkout/ref was changed to imitate entry and no ledger was generated.

A published-head source would be a **hypothetical metadata calculation**: its 136 changed paths have zero cover intersections. None of the actual records has that source, so its fresh result cannot relabel, admit or waive freshness for them. A legitimate refresh/admission remains separately gated; no CI execution is authorized by this review.

## Required corrections

**R1 — arithmetic.** AUTHOR lines 79-81 say 21 planning paths. The actual count is 20. Its stated category numbers sum to 137 overall, contradicting the otherwise correct 136. Correct that one category; no unit remapping is required.

**R2 — future behavior guarantee.** Lines 186-195 say a refresh from entry or a descendant would exercise the same covered code paths because subtrees are identical. Git identity proves static source identity at entry only. A descendant can change code; environment, inputs and scheduling can change exercised paths even at the same source. Replace the guarantee with a bounded statement of identical definitions and a separately gated real execution whose actual source/environment/behavior must be checked.

**R3 — old-CI absence is not project-wide absence.** Lines 207-209 correctly retain U01-U04 absence from these old CI archives, then incorrectly prescribe a genuine Flic execution as still missing without acknowledging later retained proof. The actual local intake artifact is [FLIC_REFRESH.md](../../SW-AUDIT-01/FLIC_REFRESH.md), independently accepted in [FLIC_EVIDENCE_REVIEW.md](../../SW-AUDIT-01/FLIC_EVIDENCE_REVIEW.md), not a file named FLIC_EVIDENCE_INTAKE.md. Four genuine flic/sim V3 pass/ok records, 25 pass plus one n/a, were accepted as bounded execution facts; privacy/artifact admission remains HOLD. The [handoff](../../../../agent-process/state/HANDOFF.md) records their accepted integration at 2a7fe096/21a57813/862b9299. State the CI-specific absence and require coordinator disposition of existing proof before deciding whether a further refresh is needed; do not mandate duplicate execution solely from these archives.

Similarly, line 210 is accurate as an old-CI F-API-034 negative-path gap, but current next-action context must acknowledge the retained API-V2 candidate chain 386/ee3/caaa awaiting qualified review. The handoff and [runtime execution record](../../../../planning/RUNTIME_EXECUTION.md) record source `ee3f2e7f034a9ace64553e942f328dff921a1e04`, report `caaa4faabe9ede1e3aed37d2269efd4a4d691e04`, and failed/partial global gate FSEC007. Existing candidate work is not accepted source and is not proof that duplicate implementation is needed. This review reuses those metadata outcomes without reviewing candidate source or payloads.

**R4 — gate status.** The heading “Gates unchanged and closed” applies ambiguously to privacy/VAL-15, retained source reviews, FSEC007, HIL, visual approval, 72-hour soak, week sign-off and final release. Those unsatisfied gates remain held/open. Separate them from the **original three** Tron owner decisions, closed by [the 2026-10-20 approval](../../../../validation/TRON_OWNER_APPROVAL_20261020.md). Neither reopen those three nor imply general visual/release approval.

**R5 — qualification outcome.** Lines 270-272 reduce attempt 1 to “no review route/domain available.” Current shared-root handoff explicitly records formal core qualification attempt 1 FAIL: provenance/invariants/counterexamples passed; behavior_and_tools/calibration/review_quality failed, with no qualified domain. Preserve that actual outcome and pending explicit owner retake choice. Provider availability is a different issue and no automatic retry is authorized.

**R6 — contradictory method limits.** Lines 222-224 claim no test executed and no archive extracted, contradicting the report's own Git source tar export/extraction and five-module pytest receipt (489 passed). Say no raw CI archive interpretation and no runtime/scenario campaign, while disclosing Git SOURCE archive extraction and documentation tests. Neither event is a new CI or source qualification.

**R7 — method precision.** “Exactly one” source-to-entry diff execution is false: retained probe_01_git_receipts.json and probe_02_git_receipts.json each record that explicit diff. Correct the execution count while preserving the valid finite cached comparison; no quadratic audit was needed. Label the published-head freshness column hypothetical explicitly, with no record relabel/admission consequence. The underlying unknown/stale result is correct.

## Verification and limits

Private reviewer facts and individual Git stdout/stderr/exit originals are retained under `build/software-waves/EV-CI-ATTRIBUTION/execution-20261101/reviewer/`. Direct inspection script exit 0 verifies the exact canonical author hash, three ancestry results, trees/categories, 16 identities, 56 table rows and 11 finite cover sets. No failed metadata-verification attempt occurred. Initial read-only path lookups that missed CI_ATTRIBUTION_TASK.txt at root and a guessed API directory were corrected to discovered documentation locations; no missing-original inference followed.

Only the five authorized documentation modules are run, with route-inventory/cache plugins disabled, root .venv Python, own checkout/root+src PYTHONPATH, UTF-8, bytecode disabled, and created data/config/temp under `C:/t/exec-ev-ci-attribution/nov02-review01/`. Their direct exit, complete stdout/stderr and JUnit are retained before another invocation. Report UTF-8/LF, fenced JSON, 56-ID coverage, local references, scope and CR-aware whitespace checks accompany them. The five documentation modules passed: **489 passed in 3.41s**, direct exit **0**. Final structural checks passed: UTF-8/LF, required JSON fields, all 56 IDs exactly once in the cover-group table, local references, and CR-aware staged whitespace/scope. The invocation-only hooksPath exception is for this new prose; no source-hook/full-suite pass is claimed.

No original archive/log/validation/screenshot/credential payload was interpreted; no assertion was re-evaluated. No CI run, runtime tests/service/campaign/probe, network refetch, ledger generation/import, source modification, qualification, publication, merge, cleanup or self-release occurred. The author exceeded its ten-minute target; its selfchecks/docs pass is not independent content proof or a deadline pass. Source/feature qualification, privacy admission, physical HIL, 72-hour, week and final-release gates remain unchanged. Coordinator owns actual acceptance, fixes assignment, settlement, preservation and publication; authors fix, reviewers report.

```json
{
  "reviewed_author_commit": "d86b65c271cc06d95895b8abdce53e24210bc6d9",
  "overall_verdict": "require_changes",
  "verified_units": 56,
  "current_entry_source_ancestry": {
    "entry": "638a226a49b9cc0ead952a4a787d12c26dfcd35e",
    "actual_source": "bdcf06dc6723aad7da63ecfed3d3555ab0d02e55",
    "is_ancestor": false,
    "merge_base_exit": 1
  },
  "freshness_admission": false,
  "source_or_feature_qualification": false,
  "actionable_findings": [
    {
      "id": "R1",
      "severity": "medium",
      "location": "AUTHOR.md:79-81",
      "correction": "docs/planning count is 20, not 21; 1 + (39 + 1 + 20 + 75) = 136."
    },
    {
      "id": "R2",
      "severity": "medium",
      "location": "AUTHOR.md:186-195",
      "correction": "Replace the guarantee that a refresh would exercise the same covered code paths with identical static definitions at the exact entry only; future runtime behavior and descendants need separate verification."
    },
    {
      "id": "R3",
      "severity": "high",
      "location": "AUTHOR.md:201-212",
      "correction": "Bound missing Flic and API034 assertions to these old CI archives; acknowledge accepted separate Flic proofs under admission hold and retained API-V2 candidate pending qualified review before prescribing new execution or implementation."
    },
    {
      "id": "R4",
      "severity": "high",
      "location": "AUTHOR.md:237-242",
      "correction": "Separate held/open unsatisfied privacy/source/HIL/72-hour/week/final-release gates from the closed original three Tron owner decisions; do not label the whole list closed."
    },
    {
      "id": "R5",
      "severity": "medium",
      "location": "AUTHOR.md:270-272",
      "correction": "State formal core qualification attempt 1 FAIL with no qualified domain and pending explicit owner retake decision; route availability is not the outcome."
    },
    {
      "id": "R6",
      "severity": "medium",
      "location": "AUTHOR.md:222-224",
      "correction": "Disclose Git source tar export/extraction and the five docs pytest modules; narrow no-archive/no-test claims to no raw CI archive interpretation and no runtime/scenario campaign."
    },
    {
      "id": "R7",
      "severity": "low",
      "location": "AUTHOR.md:44-45 and checks table",
      "correction": "Correct exactly one source-to-entry diff execution: probe01 and probe02 each executed it; describe finite cached metadata reuse without the false invocation count, and explicitly label published-source freshness hypothetical."
    }
  ]
}
```
