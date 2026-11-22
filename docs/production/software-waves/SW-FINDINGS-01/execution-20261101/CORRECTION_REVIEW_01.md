# SW-FINDINGS-01 correction 01 independent exact-commit review

Verdict: **require_changes** at MiniMax author commit `487a6ca7afaf65882fb490880421f0026ae59cc5`, parent `f2af2f38f1ea95891de39b8e64fd0ab7826336de`. Six correction items are accepted; R3 and R5 retain two narrow factual errors in the newly corrected prose. This is a completed bounded factual review, not finding closure or source qualification.

Reviewer: native OpenAI gpt-6-astra/high, different underlying family from MiniMax M3; injected Task `task_f76d52b72a2e`, Dispatch `ctx_3ae35200ca22`, Run `run_37205f6095b3`, gen5, runtime `e8ce3460-a9d4-4897-8e4f-10a8e3cdc400`, Orca 1.4.246. Only this new report is a tracked write. Coordinator owns allocation-ledger maintenance, acceptance, settlement, preservation and publication.

## Exact inputs and preserved structure

Read the entire 57-insertion/32-deletion correction diff and changed context, the exact prior review `00b7b04994a08d45961c67619d402506ba2a65a3:docs/production/software-waves/SW-FINDINGS-01/execution-20261101/REVIEW.md`, and the shared-root `docs/production/software-waves/MVP-EXECUTION-20261102/FINDINGS_CORRECTION01_TASK.txt`. The canonical tracked [AUTHOR.md](AUTHOR.md), not the private commit-identity receipt, is the deliverable.

Canonical AUTHOR: **25951 bytes**, SHA256 `dd49ef4d02a4abd2b2389cc330eb59c98ba5b59b6dbfc95d90f34515deb8d3c7`. Exact prior REVIEW: **16381 bytes**, SHA256 `6468f423229750512a97ac637a113314fd654c9788a6cf2bb2be947165baeaa5`. This new reviewer checkout has a CRLF AUTHOR representation: **26146 bytes**, SHA256 `a00d0f679d30b9ab2e998817775262f5570202076c8e625e0b3231fa85d98b0d`; removing its 195 CRLF carriage returns matches canonical Git bytes exactly. It was not rewritten. The author's LF working identity remains a separate observation.

The prior independently verified **265 total / 61 open / 204 closed** is preserved: count-table bytes are unchanged, the exact 61 IDs equal the prior review's JSON list once each, partitioned as **12 detailed + 47 inherited + 2 new**. The 47-row crosswalk table is byte-identical to the candidate parent, as are the register, pending YAML and feature registry. These are structural preservation checks, not a repeat of the 47-row audit or renewed parser/runtime qualification. Historical 59-row DeepSeek authorship, triage-only acceptance and limits remain attributed to `8f23ae8976a4056f7dd7793ad3733c730594f42d` / `b008297b1a3c988789e92c2cb4c32f3396bcd07f` and [the historical coordinator disposition](../COORDINATOR_RECONCILIATION.md). Every finding remains open; BE-22 and the external-gate-count inconsistency remain unaccepted.

## R1-R8 dispositions

| Item | Disposition | Exact bounded assessment |
| --- | --- | --- |
| R1 | Accept | Historical `97e617c2276c7b1e015bb4a9419cb9820deafdee` to entry `3602a4e4ad3333d4be989ce34b8285e73cbd472c` reproduces 331 full paths and 14 filtered src/tests/tools paths. The report names changed control.py/API-19 and model.py, and no longer renews acceptance of 47 inherited rows from unchanged bytes. |
| R2 | Accept | driver.py:1935 is one `set_macro_cec_sender(macro_cec_sender)` call containing two substrings; 642-643 define/document a top-level async function. The actual factory reference is src/hub/integrations/unfolded_circle/entities.py:1279/1281, which delegates to the two builders. Name absence proves no architecture; both original duplication conditions remain unverified. Canonical driver size 103001 is verified and 105469 is explicitly labeled CRLF. |
| R3 | Require changes | Dict/list/string handling, Response.describe omission of caller header values, historical synthetic-marker provenance and privacy/full-chain gates are now properly bounded. But the sentence attributes the anchored PIN boundary to the wrong regex: see residual R3 below. |
| R4 | Accept | FSEC007 is now an unresolved numeric V2/V3 mismatch with cause unestablished and assigned diagnosis owed. No defect or freshness-cause diagnosis is asserted. |
| R5 | Require changes | The exact typecheck job/mypy step has no continue-on-error; unrelated occurrences are correctly excluded and no fresh CI pass is claimed. The new Ruff path list misstates the actual loop: see residual R5 below. |
| R6 | Accept | UI-09 is M and its register lists all nine filenames including settings-panel.js. The invented eight-versus-nine discrepancy is removed; presence is explicitly not deadness proof. |
| R7 | Accept | The one `set output stream` occurrence at src/orei_matrix.py:2550 is a comment describing the rejected family, explicitly distinguished from executable support and hardware proof. |
| R8 | Accept | Both carried-row sections point to exact assertions, original source/image/client attribution and all surviving acceptance conditions before reconciliation. API-25 is scoped to the local structure/string-list/boolean validator without a whole-hub diagnosis or mandated implementation. UC-10 behavior is attributed to historical prose, with test/scenario presence distinguished from fresh proof and the agreed DI-9 residual preserved. |

### Residual R3: name the dictionary-key regex correctly

AUTHOR section 4, VAL-15 currently says: “The anchored `_SECRET_QUERY` pin pattern does **not** match `X-Admin-PIN`”. In `tools/validate/evidence.py:112-130`, the anchored alternative `^(key|pin|pin_hash|authorization|cookie)$` belongs to **`_SECRET_KEYS`**, used by the dictionary branch. **`_SECRET_QUERY`** instead matches query parameters beginning with `?` or `&` and is applied to strings. Although the query regex also does not match the bare header name, it is not the anchored dictionary-key mechanism explaining the recorded header gap.

Required correction: identify `_SECRET_KEYS` for the anchored PIN/header-name boundary, while preserving the separate `_SECRET_QUERY` string-redaction statement and all existing limits. This is a factual source-attribution correction only; no new redaction implementation, runtime reproduction, generic-redaction-absence claim or owner-credential leak is established or requested.

### Residual R5: preserve the actual Ruff loop tokens

AUTHOR section 5, DEP-05 lists `src`, `tests`, `custom_components`, `tools/run.py` and `tools/run_server.py`. The actual `.github/workflows/ci.yml:55` is `for p in src tests custom_components tools run.py run_server.py; do`. Its existence check at line 56 selects **six independent candidates**: `src`, `tests`, `custom_components`, **`tools`**, **root `run.py`**, and **root `run_server.py`**. The prose drops the tools directory and relocates both root scripts, so it does not accurately state declared CI scope.

Required correction: transcribe the six separate path tokens and retain the existence filter/source-declaration-only limitation. The prior review/task used slash-delimited shorthand; that ambiguity does not supersede the actual source. The broader conclusion that Ruff is not restricted to src remains supported, and no new CI execution is required for this prose fix.

## Global status and honest limits

The dated SW-AUDIT update matches the shared-root execution `COORDINATOR_DISPOSITION.json`: author `f2ee085a37a40cf8e3fc67aef4bb6fec5e7ad731` / review `577bfe6b1475183ab0881a1f2d70a7691540e2b8` received bounded inventory-documentation acceptance, with source/feature qualification false. The original entry-3602 require_changes state remains historical. No global report or historical evidence was altered.

The author's 109 selfchecks are not semantic correction proof. Read-only metadata inspection retained awareness of both failed harness attempts (five and three failed expectations) and the later check record; no failed run is relabeled as passing. The assigned eight-minute author target was exceeded (about 18 minutes from first artifact, per delivery authority), with no deadline-pass claim. Core qualification attempt 1 remains formally FAIL, no qualified domain, owner retake choice pending. Original three Tron decisions stay closed; physical/HIL, 72-hour soak, week-field and final version/artifact release gates remain separate.

## Validation and delivery boundary

Ran exactly the five authorized existing documentation modules: core_documentation, client_guides_docs, openapi_and_config_docs, security_docs, license_and_protocol_docs. Result: **489 passed in 3.38s; direct subprocess returncode 0**, no reported failures/skips. Used root .venv Python, own checkout root/src PYTHONPATH, UTF8, bytecode off, created isolated data/config/temp, explicit forward-slash basetemp, and disabled route-inventory/cache plugins. Full direct stdout, returncode/argv/environment record, JUnit and original temp contents are retained under the assigned new reviewer/temp namespaces. These documentation passes do not accept the author prose or qualify product behavior.

Structural checks compare canonical hashes, full diff scope, unchanged counts and ID partition against the exact prior review/candidate; report checks cover UTF8/LF, fenced JSON, references and CR-aware whitespace. A first reviewer crosswalk extraction heuristic misread bold text in the inherited table and failed with [2,12,20]; explicit table-column extraction then verified [2,12,47]. The failed output remains retained as a transcript-derived copy, not a fabricated successful run. Initial read-only discovery used an unsupported inbox flag, an absent shared build path and incorrect entities path; corrected reads succeeded, with original failures preserved in the session transcript. No runtime tests/services, source hooks, ledger generation, raw evidence interpretation or broad audit occurred.

Reviewer reports; author fixes. Only the new CORRECTION_REVIEW_01.md is committed using the permitted invocation-only documentation hook exception after checks. Old AUTHOR/REVIEW and all register/source/evidence bytes remain unchanged. Coordinator decides actual bounded acceptance and owns settlement, preservation and publication; no push, merge, cleanup or self-release here.

```json
{
  "reviewed_author_commit": "487a6ca7afaf65882fb490880421f0026ae59cc5",
  "overall_verdict": "require_changes",
  "R1_R8_dispositions": {
    "R1": "accept",
    "R2": "accept",
    "R3": "require_changes",
    "R4": "accept",
    "R5": "require_changes",
    "R6": "accept",
    "R7": "accept",
    "R8": "accept"
  },
  "current_total_count": 265,
  "current_open_count": 61,
  "current_closed_count": 204,
  "inherited_scope_not_requalified": true,
  "finding_or_source_qualification": false,
  "bounded_delta_acceptance_supported": false,
  "remaining_corrections": [
    "R3: identify _SECRET_KEYS for the anchored dictionary-key PIN boundary",
    "R5: list tools, run.py and run_server.py as separate Ruff candidates"
  ],
  "historical_61_id_set_preserved": true
}
```
