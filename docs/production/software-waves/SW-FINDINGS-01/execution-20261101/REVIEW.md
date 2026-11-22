# SW-FINDINGS-01 bounded independent factual review

Verdict: **require_changes** at author commit `f2af2f38f1ea95891de39b8e64fd0ab7826336de`, parent `3602a4e4ad3333d4be989ce34b8285e73cbd472c`. The inventory delta is verified; several new source interpretations and counts need correction before accepting this prose delta.

Reviewer: native OpenAI gpt-6-astra/high under injected Task `task_14ca62be7c5f`, Dispatch `ctx_f5097c9b3ca5`, Run `run_37205f6095b3`, gen5, runtime `e8ce3460-a9d4-4897-8e4f-10a8e3cdc400`, Orca 1.4.246. MiniMax M3 authored the reviewed report, a different underlying family. This is factual prose review only, not source/security qualification or register closure.

## Inputs and verified delta

Read the original FINDINGS_DELTA_TASK, shared-root standing protocol/current handoff and allocation context, [new author report](AUTHOR.md), [historical DeepSeek report](../AUTHOR.md) and [OpenAI coordinator disposition](../COORDINATOR_RECONCILIATION.md). Historical commits `8f23ae8976a4056f7dd7793ad3733c730594f42d` and `b008297b1a3c988789e92c2cb4c32f3396bcd07f` remain accepted **as triage only with limits**, with actual authorship preserved. No old report was edited.

Canonical new AUTHOR.md: 22552 bytes, SHA256 `647ec87929e485f6df45151a03a528214644cfb8b610c012fd9792289df9e3e8`. This reviewer checkout has a CRLF AUTHOR working copy: 22722 bytes, SHA256 `c982c5bef9d9229d6b5d716095867e6649a70846d68f4b02775f3bd12e8cefb6`; removing its 170 CRLF carriage returns exactly matches the canonical bytes. An initial exact-working-equality assertion therefore failed; canonical identity remained verified and the working file was not rewritten. Independent existing-parser enumeration gives **265 total / 61 open / 204 closed**. Historical register at `97e617c2276c7b1e015bb4a9419cb9820deafdee` gives **263 / 59 / 204**; its pending list is empty. The complete register bytes match the author parent, proving no row-text/severity/state/addition/removal changes there. Current pending YAML contains only open VAL-14 and VAL-15. All historical open IDs are carried, no removal; the current table covers each of the 61 exactly once: 12 detailed carried + 47 inherited + 2 new.

Feature links reproduce: VAL-14 on F-API-033/F-API-034/F-REL-009; VAL-15 on F-SEC-014. F-API-002/F-API-031 V1 to V2 and F-SEC-007 V1 to V3 are recorded registry changes with evidence references, not fresh qualification by this review.

VAL-14 correction `3788353e` and review `0bd3d76f` are ancestors of the exact parent; pending disposition still requires assembly review and combined CI/publication. VAL-15 retained submissions `11f305b1`, `615d3c84`, `2d02004d` exist and are not ancestors: non-ancestry alone proves no integration into this base, while delivered/unreviewed status is inherited from the assigned accepted coordination record. Stale undispatched YAML must not trigger duplicate implementation. Qualified exact-chain review, privacy admission and register reconciliation remain prerequisites.

## Required report corrections

### R1: Sections 3, 6, 9: qualify path universe and byte identity

The full historical-to-parent diff has 331 paths; 14 is exactly the src/tests/tools filter. src/rest_api/control.py changed and is explicitly cited for carried API-19, so every cited source of all 59 being identical is false. tools/validate/model.py changed too. State the filter and exception; retain the 47 inherited rows without implying renewed acceptance from unchanged bytes.

### R2: Sections 5 and 8: BE-22 occurrence count is not closure proof

src/driver.py:1935 has set_macro_cec_sender(macro_cec_sender): two substrings on one call line, not two closures. Lines 642-643 define/document a top-level async function. EntityFactory name absence cannot disprove a single-factory architecture: build_ucapi_entities delegates to build_compatible_entities/build_entities at 1279/1281. Keep both original duplication conditions unverified; remove the reproduced-closure inference and architectural inference from names. Canonical driver bytes are 103001; 105469 is the CRLF working-file size, which needs labeling if retained.

### R3: Section 4: VAL-15 redaction scope

tools/validate/evidence.py:112-132 masks secret-looking dict keys, recursively handles lists, AND applies _SECRET_QUERY to strings. Thus only dict keys is false. Literal x-admin-pin/ADMIN_PIN absence is not proof of generic redaction absence: explain the actual regex boundary (anchored pin does not match X-Admin-PIN) and keep the claim scoped to the recorded header gap. model.py Response.describe omits caller header values; do not imply all credential-header handling is absent. Retain historical synthetic-marker provenance, unreviewed chain and privacy admission; no fresh reproduction or owner leak.

### R4: Section 4: FSEC007 cause remains unknown

Recorded exit 1 and observed V2 below recorded V3 support a numeric mismatch only. They do not establish a level-freshness defect or its cause. Replace the causal diagnosis with unresolved mismatch, diagnosis pending in its assigned parallel scope.

### R5: Section 5: DEP-05 mypy and ruff scope

ci.yml:63-87 typecheck job and mypy step have no continue-on-error; occurrences at 450/454/459/527 belong elsewhere. Remove mypy non-blocking is source-supported. The nearby ruff loop at 53-60 explicitly selects existing src/tests/custom_components/tools/run.py/run_server.py; this source scope is inspectable, without claiming a fresh CI result.

### R6: Sections 5 and 8: UI-09 count and severity

Current register UI-09 is M, not L, and lists all nine filenames including settings-panel.js. There is no eight-versus-nine discrepancy. Correct severity and remove the invented register-list discrepancy; file presence does not establish deadness.

### R7: Section 5: HIL-09 absence count

The literal set output stream occurs once in src/orei_matrix.py:2550, in a comment describing the rejected command family. Other listed obsolete literals are absent in the inspected Python scope. Correct the zero claim or explicitly exclude comments with a demonstrated method; this comment is not executable support or hardware proof.

### R8: Sections 5-6: retain evidence admission in action wording

The historical coordinator disposition requires exact row assertions, original source/image/client attribution and every surviving acceptance condition before reconciliation. Make that prerequisite explicit beside inherited R/text-only actions. API-25 structure validation includes list string types and auto_resolved boolean, without target syntax validation in this function; that supports a scoped lead, not a new whole-hub diagnosis or mandatory implementation prescription. UC-10 test/scenario presence is not fresh proof of the Phase-cell behavioral fix; attribute that fix to accepted historical prose and retain the DI-9 residual.

## Other bounded source checks and limits

On canonical tracked Python files under src/, exact substring counts reproduce BE-26: 68 `range(1, 9)` (13 under src/hub), zero literal `[0]*8`, two `192.168.0.100`; unchanged src bytes except control.py preserve these historical counts. These are literal scope counts, not exhaustive hard-coding or architectural proof. API-19 has two `run_rest_action` substrings; VAL-14 control.py has four `switch_failed` and two `switch_all_failed` substrings. These are presence only.

API-25 profiles.py has zero `input:` and four `input_`; inspected `_validate_cec_config` checks known fields, arrays of strings and boolean auto_resolved, not target syntax. Uninspected whole-path/storage behavior remains unknown. UI-13 counts are specifically web/index.html: 53 `<script` and zero literal `type="module"`. The nine UI-09 named files exist. UI-16's two reduced-motion references, 30 fps setting, frame interval and blur cap are present; render-only-while-moving and editor lazy loading were not qualified. UC-10 named test/scenario references are present, with no behavioral execution here.

SEC-14 canonical LICENSE is 16726 bytes with MPL text and no literal stub; public-history purge, legal status and cache authority remain historical/owner-limited references, not reverified conclusions. SEC-15's 42 workflow `uses:` values are 40-hex SHA-pinned; Dockerfile has one external digest-pinned Python base and internal hub stages. DEP-05 triggers/jobs exist, but no fresh CI/security pass follows. HIL-09 new-command counts reproduce in tracked src Python text (2/2/3/4/3/2/4/5/10 in the author's order), as do copy-family counts 2/2/6; comment versus command behavior matters as R7 notes. Hardware write/readback and Remote/SDK gates stay open.

The 47 inherited rows are explicitly **not requalified**. Unchanged source presence does not refresh historical evidence. The BE-22 table/prose conflict and historical external-gate-count inconsistency remain unaccepted. Agreed DI-9 and approved-ID compatibility remain preserved; original three Tron decisions stay closed. Global SW-AUDIT remains require_changes; Core qualification attempt 1 remains FAIL with no qualified domain and explicit owner retake choice pending. No finding, feature, parent package, owner gate or release is closed by this review or Task success.

## Validation and preservation

Only the five authorized documentation modules are used, with route-inventory/cache plugins disabled, root .venv Python, own checkout root/src PYTHONPATH, UTF8 and bytecode disabled, fresh isolated data/config/temp and explicit forward-slash basetemp under `C:/t/exec-sw-findings-01/nov02-review01/`. Direct subprocess stdout, return code, JUnit and temp originals are retained; result: **489 passed in 3.97s, direct returncode 0**, with no failures or skips reported. Private reviewer inspection/check metadata stays under the assigned reviewer subtree. No runtime campaign, product test suite, source hook, ledger generation, raw evidence payload review or broader history/secret scan occurred.

The author's retained docs stdout says 489 passes; that is not content acceptance or my observation of its old process exit. I inspected metadata only as needed. Initial read probes used an incorrect root driver path and a PowerShell wildcard form unsupported by rg; corrected source reads used src/driver.py and direct paths, with failures retained in this transcript. A later file-presence check initially assumed flat web/js paths and failed before the remaining checks; recursive discovery confirmed the nine files under components/ and utils/, and the corrected report checks passed. An unsupported orchestration progress type was rejected; the subsequent supported heartbeat was confirmed. No product or historical data was changed.

Coordinator owns ledger updates, acceptance, settlement, preservation and publication; author owns corrections. This review changes only its new REVIEW.md. Invocation-only documentation hook exception is permitted after checks; no implementation-hook pass is claimed.

```json
{
  "reviewed_author_commit": "f2af2f38f1ea95891de39b8e64fd0ab7826336de",
  "overall_verdict": "require_changes",
  "verified_current_open_ids": [
    "API-07",
    "API-12",
    "API-16",
    "API-18",
    "API-19",
    "API-20",
    "API-21",
    "API-25",
    "BE-14",
    "BE-15",
    "BE-16",
    "BE-20",
    "BE-22",
    "BE-23",
    "BE-24",
    "BE-25",
    "BE-26",
    "BE-33",
    "DEP-05",
    "DEP-07",
    "HIL-03",
    "HIL-09",
    "HIL-14",
    "PER-04",
    "SEC-14",
    "SEC-15",
    "TST-03",
    "TST-04",
    "UC-10",
    "UC-11",
    "UC-12",
    "UC-13",
    "UC-18",
    "UC-28",
    "UI-05",
    "UI-06",
    "UI-07",
    "UI-08",
    "UI-09",
    "UI-10",
    "UI-11",
    "UI-12",
    "UI-13",
    "UI-14",
    "UI-15",
    "UI-16",
    "UI-18",
    "UI-19",
    "UI-20",
    "UI-21",
    "UI-33",
    "UI-34",
    "UI-35",
    "UI-36",
    "UI-38",
    "UI-39",
    "UI-40",
    "UI-41",
    "UI-42",
    "VAL-14",
    "VAL-15"
  ],
  "inherited_scope_not_requalified": true,
  "finding_or_source_qualification": false,
  "actionable_findings": [
    {
      "id": "R1",
      "location": "Sections 3, 6, 9: qualify path universe and byte identity",
      "finding": "The full historical-to-parent diff has 331 paths; 14 is exactly the src/tests/tools filter. src/rest_api/control.py changed and is explicitly cited for carried API-19, so every cited source of all 59 being identical is false. tools/validate/model.py changed too. State the filter and exception; retain the 47 inherited rows without implying renewed acceptance from unchanged bytes."
    },
    {
      "id": "R2",
      "location": "Sections 5 and 8: BE-22 occurrence count is not closure proof",
      "finding": "src/driver.py:1935 has set_macro_cec_sender(macro_cec_sender): two substrings on one call line, not two closures. Lines 642-643 define/document a top-level async function. EntityFactory name absence cannot disprove a single-factory architecture: build_ucapi_entities delegates to build_compatible_entities/build_entities at 1279/1281. Keep both original duplication conditions unverified; remove the reproduced-closure inference and architectural inference from names. Canonical driver bytes are 103001; 105469 is the CRLF working-file size, which needs labeling if retained."
    },
    {
      "id": "R3",
      "location": "Section 4: VAL-15 redaction scope",
      "finding": "tools/validate/evidence.py:112-132 masks secret-looking dict keys, recursively handles lists, AND applies _SECRET_QUERY to strings. Thus only dict keys is false. Literal x-admin-pin/ADMIN_PIN absence is not proof of generic redaction absence: explain the actual regex boundary (anchored pin does not match X-Admin-PIN) and keep the claim scoped to the recorded header gap. model.py Response.describe omits caller header values; do not imply all credential-header handling is absent. Retain historical synthetic-marker provenance, unreviewed chain and privacy admission; no fresh reproduction or owner leak."
    },
    {
      "id": "R4",
      "location": "Section 4: FSEC007 cause remains unknown",
      "finding": "Recorded exit 1 and observed V2 below recorded V3 support a numeric mismatch only. They do not establish a level-freshness defect or its cause. Replace the causal diagnosis with unresolved mismatch, diagnosis pending in its assigned parallel scope."
    },
    {
      "id": "R5",
      "location": "Section 5: DEP-05 mypy and ruff scope",
      "finding": "ci.yml:63-87 typecheck job and mypy step have no continue-on-error; occurrences at 450/454/459/527 belong elsewhere. Remove mypy non-blocking is source-supported. The nearby ruff loop at 53-60 explicitly selects existing src/tests/custom_components/tools/run.py/run_server.py; this source scope is inspectable, without claiming a fresh CI result."
    },
    {
      "id": "R6",
      "location": "Sections 5 and 8: UI-09 count and severity",
      "finding": "Current register UI-09 is M, not L, and lists all nine filenames including settings-panel.js. There is no eight-versus-nine discrepancy. Correct severity and remove the invented register-list discrepancy; file presence does not establish deadness."
    },
    {
      "id": "R7",
      "location": "Section 5: HIL-09 absence count",
      "finding": "The literal set output stream occurs once in src/orei_matrix.py:2550, in a comment describing the rejected command family. Other listed obsolete literals are absent in the inspected Python scope. Correct the zero claim or explicitly exclude comments with a demonstrated method; this comment is not executable support or hardware proof."
    },
    {
      "id": "R8",
      "location": "Sections 5-6: retain evidence admission in action wording",
      "finding": "The historical coordinator disposition requires exact row assertions, original source/image/client attribution and every surviving acceptance condition before reconciliation. Make that prerequisite explicit beside inherited R/text-only actions. API-25 structure validation includes list string types and auto_resolved boolean, without target syntax validation in this function; that supports a scoped lead, not a new whole-hub diagnosis or mandatory implementation prescription. UC-10 test/scenario presence is not fresh proof of the Phase-cell behavioral fix; attribute that fix to accepted historical prose and retain the DI-9 residual."
    }
  ]
}
```
