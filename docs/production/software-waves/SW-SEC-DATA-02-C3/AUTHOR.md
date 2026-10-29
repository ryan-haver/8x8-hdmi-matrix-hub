# SW-SEC-DATA-02-C3 author delivery

The leased expected-JSON description leak is corrected and exercised through
actual loopback HTTP, `Runner._run_one`, `_check` and `write_record` output.
Inherited C1/C2 and C3 remain **UNREVIEWED / UNINTEGRATED / UNQUALIFIED**.
Qualified different-family exact-final-commit review remains held for unknown
DeepSeek source-review quota; no family substitution or reviewer reserve is claimed.
This bounded child does not close VAL-15 or approve raw/private evidence admission.

## Authority and scope

- Base: `615d3c8403b237dd117c8032697c9b58895f9217`, preserved/published C2 candidate.
- Source/test commit: `8fc65e052954a30f89be209d2d8f04e58ac1266f`.
- Branch: `ryan-haver/wp-sec-data-02-c3`.
- Worktree: `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-sec-data-02-c3`.
- Run: `run_37205f6095b3`; Task: `task_242c1cc61b92`; Dispatch: `ctx_793d3e4da3c3`.
- Worker: `term_ea66eadb-b85d-499f-ac92-0d6536d97288`;
  coordinator: `term_dcf96b5a-bb99-4ecb-b887-eb53f7f01662`.
- Selected OpenAI `gpt-6.1-sol/high`, local Windows, no helpers/nested workers.
  Supplied 2026-10-29T03:01Z author-headroom observation: 78% weekly remaining;
  shared demand unknown, bounded author/correction capacity only. This worker
  makes no independent quota or genuine different-family-review attestation.

The source commit changes exactly `tools/validate/model.py::Response.describe`
and adds `tests/validation/test_sw_sec_data_02_c3.py`; the report-only follow-up
adds this document. `Response.describe` lazily imports the existing redactor
inside its nonempty expected-JSON branch and formats the returned structured
copy. This preserves the existing model/evidence import-cycle constraint.
No Response JSON, raw ActionResult/body, caller inputs, status/header-name
formatting, comparison, schema, record shape or other expectation description
changes. The inherited source/tests/reports, runner, clients, evidence redactor,
fixtures, scenarios, canonical registry/evidence, manifests and locks are unchanged.
Coordinator alone owns allocation records, acceptance, publication and settlement.

## Synthetic acceptance

Five new lifecycle cases use sensitive raw expected JSON containing nested
mappings, lists and lists of mappings. The matched subset passes against an
actual HTTP response with an extra public field. Independent top-level, nested
mapping and nested-list mismatches fail; replacing a raw expected credential
with the display mask also fails. No assertion input is sanitized or weakened.
Every case verifies original request transmission, caller values/references,
`Response.json` identity/nested identities, raw response values and request/response
capture identities before evaluating the byte-safety oracle.

All cases validate the actual written schema and check verdict, test the expected
description, persisted procedure/check/whole-record byte safety, retain public
body fields and Vary/Content-Type values, preserve expected header-name/status
formatting, and verify the existing cookie mask. Three additional public-format
controls cover absent/empty expected JSON, tuple status, minimum status and
public structured values.

Before the fix, five lifecycle tests failed the description oracle after raw
inputs, actual check verdicts and schema controls passed; three format controls
passed. All five receipts showed description/check/record safety false and
procedure safety true. The already-corrected procedure boundary did not regress.
After correction and at clean committed source, all five records are safe and
all raw matched/mismatched verdicts remain correct. These synthetic tests double
only device readback and unrelated WebSocket/Telnet startup/synchronization.
They make no physical, browser, hardware, simulator V2 or real-client V3
qualification claim; generated level labels are fixture metadata only.

## Verification

Test, lint and type-check execution used
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
(Python 3.12.10), own
absolute `src;checkout` PYTHONPATH, `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONIOENCODING=utf-8`, isolated MATRIX_DATA_DIR/UC_CONFIG_HOME and separately
NEW empty owned TEMP/TMP parents under `C:/t/c3-20261029-a`. Each pytest had a
new absent basetemp. The first full-hook attempt's path parsing error and exact
preservation-first recovery are disclosed below; no populated basetemp was reused.

The exact command arrays/environment/times/exits are preserved in private
`*-preserved/execution-receipt.json` and `run_check.py`. Focused pytest selected:

```text
tests/validation/test_sw_sec_data_02_c3.py
tests/validation/test_sw_sec_data_02_c2.py
tests/validation/test_sw_sec_data_02_c1.py
tests/validation/test_evidence_schema.py
tests/validation/test_model.py
tests/validation/test_registry.py
tests/validation/test_runner.py
```

Options: `-q -p no:tests.route_inventory -p no:cacheprovider --tb=short`, distinct
`--basetemp` and `--junitxml`. Before-fix used only the new C3 module and `--tb=no`.
No partial run writes route proof, and no ledger generation ran concurrently.

| Check | Actual result |
| --- | --- |
| Before-fix oracle | Exit 1; five failed, three passed, 1.16 s; five original unsafe records preserved. |
| Fixed seven-module focused run | Exit 0; 74 passed, 32.93 s; XML present. |
| `python -m ruff check src tests custom_components tools run.py run_server.py` | Exit 0. |
| `python -m mypy src/` with isolated cache | Exit 0; 91 source files. |
| First normal source hook (failed invocation) | Exit 1; 3,680 passed, one failed, four skipped, 35 deselected, four warnings; 642.64 s; actual routes 174/177 (98.3%). |
| Normal configured source `git commit` hook | Exit 0; Ruff passed; 4102 passed, 4 skipped, 35 deselected, 4 warnings in 888.39s; strict **177/177 routes (100%)**. |
| Clean committed-source seven-module run | Exit 0; 74 passed in 31.87s; XML present; five clean safe C3 records. |
| Five existing documentation modules | Exit 0; 489 passed in 3.05s; XML present. |

The source hook used `ROUTE_COVERAGE_STRICT=1`,
`SW_SEC_AUTH_BROWSER_TESTS=1`, the configured root `.githooks/pre-commit`, and
normal complete-core command `pytest tests/ --ignore=tests/ha --ignore=tests/uc
-q -x -p no:cacheprovider`. Root and task hook SHA-256 both equal
`e69e64194ca07a606718b5fea748f44a06ddf767b6f6756cef578b8565f544bc`.
There was no implementation hook bypass or repository/global hook setting change.
Complete stdout, exit, route proof and honest requested XML inventory are retained.
Corrected full-hook XML requested at its own external parent is present. Before/fixed/clean focused XML files are present. Full-hook times: `2026-10-29T03:27:56.652116+00:00` to `2026-10-29T03:42:48.449931+00:00`.
The four full-core skips cover POSIX permissions, POSIX unlink-while-open,
unavailable HA test dependencies and unavailable symlink creation. The four
warnings are existing aiohttp deprecations; hardware/Docker deselections remain
the normal configured exclusions.

The clean run occurred before creating this tracked report, with clean Git status
and full source SHA recorded in every C3 record. Dedicated HA/UC, combined
image/client campaigns, physical HIL, continuous soak, field and release gates
are not proved. The report-only follow-up uses the documented invocation-only
empty hooksPath exception after scoped documentation/path/whitespace checks;
it changes no source/test implementation and claims no second full-hook run.

## Byte preservation and remaining boundaries

Private own-build root: `build/software-waves/SW-SEC-DATA-02-C3/`.
Invocations retain surviving original temp files and immediate own-build copies,
including produced record/procedure/check/log/exit/XML/receipt bytes. The five
before-fix originals were copied before any later pytest
invocation; all 25 copied files were SHA-256 verified against originals while
present, then independently reverified. No bytes were lost or reconstructed.
Fixed run: 76 copied files, zero mismatches; five C3 records safe. The other fixed
records belong to inherited regressions and receive no blanket C3 safety claim.
Clean run: 76 copied files, zero mismatches, five safe C3 records; corrected full hook: 21695 copied file entries, zero byte mismatches. Native link metadata is recorded separately; a byte-copy traversal is not a native-link archive.

Private `before-audit.json`, `fixed-audit.json`, `clean-audit.json` and
`*-preservation.json` list exact source/copy hashes, counts, source/dirty facts
and boolean safety receipts without printing payload values in this report.

- `before-preservation.json`: SHA-256 `3f7d395e47e59710faec820e97a988106ae698588f9e4794feb59c4d89e1e889`.
- `fixed-preservation.json`: SHA-256 `b49ed893f79d834645cf592d9882368f6972ff554b5ab3f26dcbb1adbf8a8529`.
- `clean-preservation.json`: SHA-256 `af088d68ff773e37fe9c814c493409eefa657b52fa3c3021238a4d64d1984b47`.
- `source-hook-preservation.json`: SHA-256 `58a36866977ca3eb92283e0166a9895c750cbae63c6d1556000d7144e63e981d`.
- `source-hook-misplaced-preservation.json`: SHA-256 `c88b518ccc7efb02734976329d89ed50020d3a7a7fc75a10edc424e679a5faeb`.
- `source-hook-02-preservation.json`: SHA-256 `101dbd2365977138870d2818db018cb9464a6ab41a0f35f98ece829fd580f502`.
- Corrected full-hook stdout SHA-256 `020063403452e6c2dfe838415dad96a0c576bdaaa68311524cd9e5a753296364`.
- Corrected strict route-proof SHA-256 `6f4d570ee7d899010ee1c982086130bebb882bb3323c1581e6573161ed38194a`.

One initial private audit-helper invocation failed its receipt-count assertion
because it included inherited C2 receipts. `audit-fixed-attempt-01.json` records
that diagnostic separately; its original console traceback remains in the native
worker transcript, and no separate original stdout log file existed. Filtering
the existing C3 receipt field corrected the helper; attempt 02 log/exit and
zero-mismatch audit are retained. This was an audit-helper error, not a lost
failure record, failed product qualification or replacement of original evidence.

The coordinator-created node_modules junction targets root existing dependencies
READONLY. No dependency installation/update, dependency-target write/removal,
push/merge/tag, canonical import,
cleanup, branch/worktree release or root/private modification was performed.
Original immutable Flic/private evidence and failed API artifacts remain untouched;
no recovery or admission is claimed. Existing arbitrary-string, exception/log,
other expectation/client/artifact and general VAL-15 boundaries remain explicit.
Qualified exact-final-commit different-family review and coordinator integration
are still required, including inherited C1/C2. Coordinator retains final native
transcript/full bundle/workspace/external temp/junction preservation and task-ref
publication; this worker does not self-release or turn fixture passes into gates.

The first normal source-hook attempt failed because this author's private wrapper
used backslash Windows paths inside `PYTEST_ADDOPTS`, whose shlex parsing consumed
the separators. Pytest consequently created exactly two untracked paths inside
the task checkout: `tc3-20261029-asource-hook-parentpytest/` and
`tc3-20261029-asource-hook-parentresults.xml`. The existing UI lint test scanned
installed-runtime JavaScript fixtures there and failed. This was an author
invocation error, not a product regression or a waived check. Before any later
pytest, 19,812 misplaced file entries/XML were copied to private own build
and source/copy SHA-256 verified with originals present; this copier followed
one native test junction once. The coordinator's no-follow audit identified
19,811 regular members plus one junction; the extra copy was one traversed
target file, not an additional native regular member. The intended external
parent's 687 surviving files were separately copied/hashverified. The original
wrapper is retained as `run_check-attempt-01.py` with matching pre-edit hash.
The coordinator's blocking ask reply explicitly granted preservation-first
relocation of only those two exact source paths and a corrected NORMAL hook
rerun within the bound. `relocate-misplaced.ps1` resolved/validated the sources
inside this child and used only PowerShell `Move-Item -LiteralPath` into a new
absent own-build `source-hook-misplaced-relocated/`. It verified all 19,811
relocated regular members without traversing the junction and captured the
native junction target/type/attributes and `fsutil reparsepoint query` before
and after; all metadata/query bytes matched. The original absolute target was
left stale, with no rewriting/repair/deletion. Independent copied bytes remain.
`relocation-receipt.json`, native link logs/JSON and separate failed-attempt
manifest preserve those facts. Targeted `npm run lint:js` then exited zero.
Final `native-link-inventory.json` records three native links with zero links
followed: the external corrected-hook fixture junction, the readonly dependency
junction and the relocated stale-target fixture junction.
The corrected wrapper uses forward-slash environment paths, preserving the
first attempt's actual logs/exit/route proof/XML separately. The first requested
XML was absent at its intended location but present at the exact misplaced path;
both facts are retained, and no historical failure is relabeled as the retry.
