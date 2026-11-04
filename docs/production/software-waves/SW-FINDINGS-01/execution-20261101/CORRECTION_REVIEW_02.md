# SW-FINDINGS-01 correction 02 independent exact-diff review

Verdict: **accept**, limited to the two residual factual prose corrections at MiniMax author commit `a2dab11cdc871d6a98c563b019a361371a9af710`, parent `487a6ca7afaf65882fb490880421f0026ae59cc5`. No residual correction is required in this delta. This supports coordinator acceptance of the bounded delta, not global report acceptance, finding closure or source qualification.

Reviewer: native OpenAI gpt-6-astra/high, different underlying family from MiniMax M3, under injected Task `task_5016bec03442` / Dispatch `ctx_b4174280ec27`; Run `run_37205f6095b3`, coordinator `term_6ed8131e-3ab3-4693-8094-56cc10acd412`, gen5, runtime `e8ce3460-a9d4-4897-8e4f-10a8e3cdc400`, Orca 1.4.246. Shared-root current handoff records native Astra/high attestation for this exact assignment. No helpers or model substitutions were used. Coordinator owns allocation-ledger updates, actual bounded acceptance, settlement, preservation and publication.

## Exact inputs and dispositions

Read the complete **4-insertion / 2-deletion** diff and changed context, exact prior review `43356a0c0d0948719bf989d7bd824631d8c89a0e:docs/production/software-waves/SW-FINDINGS-01/execution-20261101/CORRECTION_REVIEW_01.md`, and current shared-root `docs/production/software-waves/MVP-EXECUTION-20261102/FINDINGS_CORRECTION02_TASK.txt`. The prior review is 10806 canonical bytes, SHA256 `32cc23cb699ff38ed942a9bacc627f513ec8161a6f86894cf00438b68314a4e5`. Its require_changes verdict and `00b7b04994a08d45961c67619d402506ba2a65a3` provenance remain historical and unchanged.

| Item | Disposition | Source comparison and limits |
| --- | --- | --- |
| R3 | Accept | [AUTHOR.md](AUTHOR.md) line 84 now attributes `^(key|pin|pin_hash|authorization|cookie)$` to `_SECRET_KEYS`. In `tools/validate/evidence.py:113-116` that is the dictionary-key regex; line 126 uses it in the dictionary branch. `_SECRET_QUERY` is separately defined at 117-120 for query parameters beginning with `?` or `&`, and line 130 applies it to strings. The corrected distinction accurately identifies the source of the anchored PIN/header-name boundary. The recorded-header-gap scope, historical synthetic-marker/non-current-reproduction limit and non-owner-credential-leak limit remain unchanged; this comparison is not runtime or privacy qualification. |
| R5 | Accept | AUTHOR line 108 correctly transcribes `.github/workflows/ci.yml:55`: `for p in src tests custom_components tools run.py run_server.py; do`. These are six independent candidates: `src`, `tests`, `custom_components`, `tools`, root `run.py`, root `run_server.py`. Line 56 filters with `[ -e "$p" ]`, and line 60 passes the resulting paths to Ruff. The prose retains that filter and expressly limits the statement to a source declaration with no fresh CI result. No CI execution or behavior qualification is inferred. |

The added Correction 02 note at lines 186-187 accurately summarizes these two changes and retains the limits. It introduces no collateral source, closure or acceptance claim. Semantic acceptance above comes from reading the actual source branches and loop, not from passing documentation tests or matching hashes.

## Preservation

Canonical AUTHOR is **26988 bytes**, SHA256 `56989fd60a7817facde500511e6be0b05286a256679f940da07c91591af19798`. This review checkout's working representation is **27185 bytes**, SHA256 `41025fecfe0ef8a424be719a928e0096c395eaa93bb7200b54362b5eab73a762`; removing its 197 CRLF carriage returns matches canonical Git bytes exactly. It was not rewritten. The author's separately reported LF working representation is not confused with this checkout.

Canonical byte-line comparison proves there are exactly two single-line replacements (VAL-15 and DEP-05) and the two-line correction-note insertion; every other line is identical to the parent. The commit changes only AUTHOR. Consequently the prior verified **265 total / 61 open / 204 closed**, exact **61 IDs** and **12 detailed + 47 inherited + 2 new** structure, the 47 inherited rows and their limits, and accepted R1/R2/R4/R6/R7/R8 corrections are preserved. No 61-finding reparse, 47-row re-audit or runtime-proof rerun was performed. The two changed rows retain their IDs, dispositions and all unrelated clauses. Historical authorship/triage acceptance remains attributed as before; unchanged bytes do not renew source or finding acceptance. Old reports and original/private correction01 evidence remain untouched.

## Checks and delivery limits

Exactly one invocation of the five authorized existing documentation modules completed: **489 passed in 3.29s**, direct subprocess returncode **0**, no reported failures/skips. Modules: `tests/test_core_documentation.py`, `tests/test_client_guides_docs.py`, `tests/test_openapi_and_config_docs.py`, `tests/test_security_docs.py`, `tests/test_license_and_protocol_docs.py`; options `-q -p no:tests.route_inventory -p no:cacheprovider`. Used shared-root `.venv` Python, this checkout's root/src PYTHONPATH, UTF8 and bytecode-off, freshly created isolated data/config/temp, and forward-slash `--basetemp=C:/t/exec-sw-findings-01/nov02-rereview02/pytest`. Full stdout, direct exit/argv/environment record, JUnit and structural receipt are retained under `build/software-waves/SW-FINDINGS-01/execution-20261101/reviewer/re-review-02/`; original temporary contents remain in the assigned temp namespace.

Basic report checks cover UTF8/LF, fenced JSON, the local Markdown reference, CR-aware whitespace and exact one-new-report scope. Initial read-only discovery looked for the task text at the shared-root top level and failed; the correct documented production path was then read, with the failure retained in the session transcript. Documentation checks are not independent semantic proof, a source-hook pass or a new CI result. The author's roughly 6.5-minute run exceeded its 3-minute target; this review grants no deadline pass.

Only this new prose report is committed with the authorized invocation-only `core.hooksPath=` exception after checks. No source, tests, tools, registries, findings, ledger, manifests, locks, evidence or baselines were written; no raw private payload interpretation, services, runtime campaigns, probes, ledger generation, broad scans, source hooks, push, merge, cleanup or self-release occurred. Core qualification 1 remains formal FAIL/no domain, with owner manual-retake choice pending; there is no retry authority here. The original three Tron decisions remain closed; other unsatisfied source/privacy/physical/72-hour/week/final-release gates remain held/open. Reviewer reports; coordinator decides actual bounded acceptance and handles lifecycle/publication.

```json
{
  "reviewed_author_commit": "a2dab11cdc871d6a98c563b019a361371a9af710",
  "overall_verdict": "accept",
  "R3_R5_dispositions": {
    "R3": "accept",
    "R5": "accept"
  },
  "prior_verified_structure_preserved": true,
  "bounded_delta_acceptance_supported": true,
  "finding_or_source_qualification": false
}
```
