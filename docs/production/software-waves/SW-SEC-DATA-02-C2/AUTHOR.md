# SW-SEC-DATA-02-C2 author delivery

The two leased structured-body formatting leaks are corrected and tested.
Inherited C1 and this child remain **unreviewed, unintegrated and unqualified**;
qualified different-family exact-final-commit review is held for unknown current
DeepSeek Pro quota. This delivery does not close VAL-15 or admit private artifacts.

## Authority and source

- Base: `11f305b16c4c95e27682d13df4b02c8de33354d7` (preserved/published C1 candidate).
- Source/test commit: `47b0bbb86a1dfd36726e60ab2ccf24b867883160`.
- Branch: `ryan-haver/wp-sec-data-02-c2`.
- Worktree: `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-sec-data-02-c2`.
- Existing Run: `run_37205f6095b3`; Task: `task_4e33d0624489`;
  Dispatch: `ctx_a35145bc2f5d`.
- Worker: `term_bb233940-b557-4000-b3b5-c3652f2ac3bc`;
  coordinator: `term_dcf96b5a-bb99-4ecb-b887-eb53f7f01662`.
- Live preamble selected OpenAI `gpt-6.1-sol/high`, local Windows, with separately
  checked bounded author/correction capacity (supplied 02:06Z observation: 81%
  weekly remaining; other commitments unknown). No independent author-side quota
  attestation, reviewer reserve, provider substitution, helper or new phase is claimed.

The source/base diff contains exactly three authorized paths: modified
`tools/validate/clients/api.py` and `tools/validate/runner.py`, and new
`tests/validation/test_sw_sec_data_02_c2.py` (136 insertions, two deletions).
This subsequent report-only commit adds only this document. Inherited C1's
redactor, tests and report, model, other clients, schemas, fixtures, REST source,
registries/ledgers/findings, manifests/locks, history and baselines are unchanged.
No push, merge, tag, evidence import, dependency installation or cleanup occurred.
Coordinator owns allocation/acceptance records, publication and preservation.

## Behavior and acceptance

`ApiClient.perform` now applies the existing recursive redactor to a copy of
the request body before interpolating it into procedure steps. `Runner._check`
does the same before JSON serialization/truncation of Response body detail.
Outbound arguments, captured raw exchanges, `ActionResult.body` and comparison
inputs remain original. No arbitrary-string regex or redactor behavior was added.

Four new cases run real loopback HTTP through `ApiClient.perform`, actual
`Runner._run_one` procedure/check construction and actual `write_record` output.
They cover dictionary and root-list bodies with nested dictionaries/lists,
credential fields and public body values, plus matched/mismatched public response
checks. They assert transmitted method/path/headers/body equality, unchanged
caller objects and raw response values/references, expected pass/fail verdicts,
schema validity, public diagnostic values, retained Vary/Content-Type values and
existing masked-cookie observation. They never sanitize assertion or HTTP input.
Additional direct Response checks prove raw credential equality passes and masked
replacement equality fails; those checks are not persisted (see residual below).

Before the fix, all four cases reached their actual written-record byte oracle
and failed. All four receipts recorded `record_safe=false`,
`procedure_safe=false`, and `checks_safe=false`, after transmission, object,
verdict and schema assertions had passed. After the fix, all four receipts were
true. The clean committed-source rerun produced four records at the full source
SHA with `dirty=false`, zero schema errors, zero unsafe records and zero copied
byte/hash mismatches. This is bounded persistence testing with a synthetic device
state provider and WebSocket doubles, not browser, physical or V2/V3 qualification;
generated evidence-level labels are fixture output only.

## Actual verification

Python was `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`,
version 3.12.10. `PYTHONPATH` contained this task's absolute `src` followed by
this checkout root; import receipts confirm this checkout's client, evidence and
runner. `PYTHONDONTWRITEBYTECODE=1`, `PYTHONIOENCODING=utf-8`, and isolated own
MATRIX_DATA_DIR/UC_CONFIG_HOME were set. No root/private runtime data or credential
store was used. Supplemental runs disabled route inventory and cacheprovider;
no ledger-generation command ran.

The focused command was `python -m pytest` with these six explicit modules:

```text
tests/validation/test_sw_sec_data_02_c2.py
tests/validation/test_sw_sec_data_02_c1.py
tests/validation/test_evidence_schema.py
tests/validation/test_model.py
tests/validation/test_registry.py
tests/validation/test_runner.py
```

Its common options were `-q -p no:tests.route_inventory -p no:cacheprovider
--tb=short`, with distinct new basetemp paths and XML destinations recorded in
the artifacts/scripts below. The before-fix command selected only the new C2
module, used `--tb=no`, and retained its own distinct failure log and exit.

| Check | Actual outcome |
| --- | --- |
| Before-fix C2 oracle | pytest exit 1; four failures, 0.73 s; four original unsafe records preserved. |
| Fixed focused six modules | Exit 0; 66 passed, 33.03 s; XML exists. |
| `python -m ruff check src tests custom_components tools run.py run_server.py` | Exit 0. |
| `python -m mypy src/` | Exit 0; 91 source files. |
| Normal configured `git commit -m 'fix(validation): mask structured bodies before diagnostic formatting'` | Exit 0; Ruff passed; 4,094 passed, four skipped, 35 deselected, four warnings, 932.72 s; strict **177/177 routes (100%)**. |
| Clean source focused six modules | Exit 0; 66 passed, 32.71 s; XML and clean byte/source receipts exist. |
| Five existing documentation modules (core, client guides, OpenAPI/config, security, license/protocol), route/cache plugins disabled | Exit 0; 489 passed, 2.82 s. |

The source hook ran from 2026-10-29T02:17:35Z to 02:33:11Z with
`ROUTE_COVERAGE_STRICT=1`, `SW_SEC_AUTH_BROWSER_TESTS=1`, normal HA/UC exclusions
and normal hardware/Docker deselections. It was the configured root
`.githooks/pre-commit`, byte-identical to this checkout's hook (SHA-256
`e69e64194ca07a606718b5fea748f44a06ddf767b6f6756cef578b8565f544bc`).
No implementation hook bypass, global configuration change, assertion reduction
or full-suite retry was used. The skips were POSIX permission enforcement, POSIX
unlink-while-open, unavailable HA test dependencies and unavailable symlink
creation. The warnings were existing aiohttp deprecations. Dedicated HA/UC,
image/client campaigns, HIL, soak, field and release gates are not proved.

Supplemental full-hook XML was requested but is absent at its intended path;
no full-suite XML is claimed. Complete hook stdout, command/environment/time/exit
receipt and copied strict route report are preserved. Fixed and clean focused
XML files exist. The clean run was from 02:33:29Z to 02:34:02Z before this report
was created, with clean tracked/untracked Git status. Report-only follow-up uses
scoped documentation/path/whitespace checks and the documented invocation-only
empty hooksPath exception; it changes no implementation or test source.

## Preserved artifacts and operational paths

Private artifacts are in this worktree's
`build/software-waves/SW-SEC-DATA-02-C2/`. They include `before-fix.log`/`.exit`,
four byte-exact `before-fix-records/` originals and boolean receipts,
`fixed.log`/`.exit`/`.xml`, copied `fixed-records/`, Ruff/mypy logs/exits,
`run-source-hook.ps1`, `source-hook.log`, `source-hook-receipt.json`,
`source-hook-route-coverage.json`, `run-clean.ps1`, `clean.log`/`.xml`,
`clean-run-receipt.json`, four `clean-records/`, `initial-receipts.json`,
`clean-source-receipt.json`, `execution.json`, `docs.log`/`.exit`, and the private
expected-description reproduction.
The fixed copied directory also contains other generated runner-regression
records; C2 marker-safety claims apply only to the four C2 records.

All four before-fix copied hashes were reverified after the coordinator's
retention warning; no requested original failure bytes were lost. No originals
were reconstructed. Initial/fixed/hook runs used distinct new basetemps below
allocated `C:/t/c2-20261029-a`; none was reused. Following that warning, the clean
run used a separately new empty `clean-parent` TEMP/TMP parent and its own
`pytest` basetemp. Remaining documentation execution uses another fresh parent.
All earlier temp/artifact contents remain for coordinator preservation.

The coordinator-owned `node_modules` junction targets
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/node_modules` for existing
dependencies. No npm install/update, target write or junction cleanup was issued.
Task caches/ignored artifacts and the short external temp remain; no other
workspace was edited or removed. Existing immutable raw Flic evidence remains
unchanged, private and on HOLD; these synthetic artifacts authorize no admission.

## Residual boundary and hold

Readonly `model.py`'s `Response.describe` interpolates expected `json` values
directly. A separate direct synthetic description reproduction records
`description_safe=false` privately; this was not represented as a full persisted
runner reproduction or a corrected boundary. Coordinator explicitly confirmed
the two-site lease, public expected-JSON lifecycle acceptance, direct raw-value
comparison controls, and this residual report without a model lease expansion.
The new actual written lifecycle records use public expectations only.

This work does not sanitize arbitrary body strings, exception/error strings,
all expectation descriptions, every client/log/artifact form or VAL-15 globally.
Qualified different-family review must accept inherited C1 and this child's exact
final commit before integration or qualification. No same-family review or
inventory-only provider substitute is claimed. Source/report publication, full
native/bundle/workspace preservation and worker settlement remain coordinator-owned.
