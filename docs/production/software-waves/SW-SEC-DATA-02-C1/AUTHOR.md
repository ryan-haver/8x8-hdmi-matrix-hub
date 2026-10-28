# SW-SEC-DATA-02-C1 author delivery

The bounded credential-header/mapping correction is implemented and verified.
VAL-15 remains open: free-form body steps and Response check details still expose
synthetic credentials, and qualified different-family review/integration is held.
This report does not qualify F-SEC-014 or all product logging.

## Authority and exact source

- Base: `d6e78e0b6ab1dab5216443584d810a7a24af32b2`.
- Source commit: `8b9f5623b3b5a12c55ed6b9da0ae59662bd6b873`.
- Actual branch: `ryan-haver/wolffish`.
- Worktree: `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-sec-data-02-c1`.
- Run `run_37205f6095b3`, Task `task_cf272c0e3b6c`, Dispatch `ctx_a52a1d96ad08`;
  worker `term_77194263-f9fb-465a-a5be-960323466d96`, coordinator
  `term_dcf96b5a-bb99-4ecb-b887-eb53f7f01662`.
- Live activation supplied Codex `gpt-6.1-sol/high`, local Windows,
  Orca 1.4.243/runtime `14c5d968-cfad-4ebc-b071-19d297a7c1f4` and checked
  author/correction capacity. No author-created dispatch, helper, substitution or
  independent quota/backend attestation is claimed here. DeepSeek Pro review
  remains held because its supported current headroom is unknown.

The source/base diff contains exactly two leased paths: modified
`tools/validate/evidence.py` and added
`tests/validation/test_sw_sec_data_02_c1.py` (143 insertions, two deletions).
This subsequent report-only commit adds only this document. No model, runner,
client, schema, shared fixture, REST, registry, ledger, finding, manifest, lock,
baseline or existing evidence file was changed. No push, merge, tag or cleanup
was performed; publication, preservation and settlement belong to the coordinator.

## Behavior and tests

Inspection found real auth consumers for `X-API-Key` and `X-Admin-PIN` at
`src/rest_api/security.py:210` and `:255`, plus session/device cookies.
The existing redactor already covered API keys, Authorization, Cookie and bare
secret fields. The change adds exact case-insensitive `X-Admin-PIN` matching.
`Action.describe` already imports this redactor lazily; its source was unchanged.
With explicit coordinator authorization, `write_record` now sanitizes a recursive
copy before JSON serialization, covering structured diagnostics that callers did
not sanitize. Record naming/path construction still uses the original metadata.
No arbitrary-text credential regex was introduced.

Six new behavioral cases cover lower/upper/mixed header names, nested dictionaries
and lists, old password/PIN/passcode/query masking, unchanged caller objects,
and retained Origin, Vary, correlation, Content-Type and similarly named public
header controls. Actual loopback HTTP through `ApiClient.perform` confirms the
original credential/public values are transmitted unchanged. Actual
`Runner._run_one` record/procedure construction and `write_record` bytes are
examined, without manually redacting before writing.

The runner cases use a synthetic state provider and WebSocket doubles; a renamed
HTTP client exercises the non-API diagnostic branch. They are unit persistence
tests, not browser or V2/V3 qualification. Their generated level labels are fixture
output only. They intentionally do not stringify response bodies into Response
expectations; the separate negative oracle below retains that failing acceptance
path and documents its unsafe persisted bytes.

Three baseline records contained markers; zero of three corrected records did.
Both corrected runner records validate against the unchanged schema. The clean
rerun produced two runner records with the exact source SHA and `dirty=false`;
all three copied records have matching hashes and zero credential-marker records.

## Actual verification

All Python commands used
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`.
`PYTHONPATH` was the task's absolute `src` followed by its root; import receipts
confirm this worktree's `tools.validate.evidence` and `rest_api`, not an installed
root package. MATRIX_DATA_DIR and UC_CONFIG_HOME used new task-owned build
directories before execution. Partial runs disabled `tests.route_inventory`;
no canonical ledger generation ran.

| Command/scope | Actual outcome |
| --- | --- |
| New test module, before fix, `-q -p no:tests.route_inventory -p no:cacheprovider --tb=no` | Exit 1; six redaction failures, 0.65 s. Initial harness attempt omitted required Scenario.covers; corrected before this baseline and retained separately. |
| New tests plus existing `test_evidence_schema.py`, `test_registry.py`, `test_model.py` | Exit 0; 58 passed, 5.97 s. |
| CI Ruff paths: `src tests custom_components tools run.py run_server.py` | Exit 0, including clean committed-source rerun. |
| `python -m mypy src/` | Exit 0; 91 source files, including clean rerun. |
| First normal configured source commit hook | Exit 1; 2,197 passed, one failed, two skipped, 35 deselected, two warnings, 290.96 s. Disposable hygiene fixture Git add failed with Windows MAX_PATH; partial strict 109/177 is preserved and is not acceptance. |
| Original deep fixture `git -c core.longpaths=false add tracked.txt` | Exit 128; positive Filename-too-long reproduction preserved. |
| Same failing hygiene test, fresh short isolated temp | Exit 0; one passed, 1.94 s; no assertion/source change. |
| Retried normal `git commit -m 'fix(validation): redact credential headers before evidence persistence'` | Exit 0; Ruff passed; 4,090 passed, four skipped, 35 deselected, four warnings, 953.34 s; strict **177/177 routes, 100%**. Source commit created normally. |
| Clean source focused rerun, same four modules | Exit 0; 58 passed, 4.63 s; clean XML and import/commit/schema/byte receipts retained. |
| Actual runner free-form negative oracle, before and after source commit | Exit 1 both times; one written record per run; action description and structured requests safe=true, body steps/Response details/all bytes safe=false. |

The normal configured hook is
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.githooks/pre-commit`,
byte-identical to the task checkout's hook (SHA-256
`e69e64194ca07a606718b5fea748f44a06ddf767b6f6756cef578b8565f544bc`).
It ran the full core pytest command with `ROUTE_COVERAGE_STRICT=1`,
`SW_SEC_AUTH_BROWSER_TESTS=1` and its normal HA/UC exclusions/default hardware and
Docker deselections. No source-hook exception or threshold reduction was used.
The four skips were POSIX permissions, POSIX unlink-while-open, unavailable HA
test dependencies, and unavailable symlink creation. Dedicated HA/UC, image,
browser campaigns, physical HIL, soak, field and release gates are not proved.

## Operational leases and preserved artifacts

Private artifacts are under this worktree's
`build/software-waves/SW-SEC-DATA-02-C1/`. They include actual commands/environment
in `execution.json`, baseline/initial harness logs and written JSON, fixed logs,
both full hook logs/exits and route reports, `maxpath-reproduction.log`,
`hygiene-short-temp.log`, `clean-tests.xml`, clean Ruff/mypy logs,
`clean-source-receipt.json`, copied `clean-records/`, byte/schema receipts,
`probe_remaining.py`, and both `remaining-freeform/` and `remaining-clean/`.
Raw failing artifacts contain synthetic fixtures only; public receipts/report use
booleans/counts. Supplemental hook XML was requested but is absent at the intended
destination; full hook stdout and its exact skip summary are retained. Clean
focused-run XML exists. No full-suite XML is claimed.

Coordinator-approved additional operational paths, preserved for no-follow
archival/cleanup:

- New ignored **junction** at the task root's `node_modules`, targeting
  `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/node_modules`, used only
  to read existing locked browser dependencies; no npm install/update or target
  mutation/deletion was performed.
- New exact task temp `C:/t/sec-c1-a52a1`, verified absent before creation, with
  distinct `hygiene-first`, `hook-retry` and `clean-tests` subdirectories. TEMP/TMP
  used this path for retry/clean runs; initial deep temp and failure are intact.
  The retry requested only additional basetemp/XML/`-ra` reporting flags.

The protected-byte checkpoint covers 3,591 tracked validation/e2e files and has
zero later mismatches. It was captured during the first hook, not before task
entry, and is not a pre-task integrity attestation. The complete base/source path
audit separately confirms no tracked historical evidence/baseline changes.
New task caches, ignored artifacts and external temp remain for coordinator
preservation; no old workspace or runtime data was removed or inspected.

## Residual finding and review hold

The real negative probe sends/echoes a synthetic credential mapping in a JSON
body. `tools/validate/clients/api.py:158` interpolates the raw body into
`result.steps`; `tools/validate/runner.py:919` interpolates `json.dumps(result.body)`
into Response detail. By persistence, those values are strings, outside this
structured redactor's supported boundary. The written procedure/check bytes
still contain the marker even though the mapped request and Action.describe
are masked. Original failed oracles remain preserved; they were not converted
into passing full-artifact claims.

Proposed separate minimal serial leases: those two exact source paths plus an
owned new regression module, sanitizing structured bodies before these formatting
sites. Acceptance should replay the current negative oracle with unchanged
transmission, public controls and no markers in both actual procedure and check
bytes, then repeat normal strict verification and different-family review. This
report does not authorize or implement that child, arbitrary-string handling,
or fixes to every log/client boundary.

This author delivery is completed only for the explicitly accepted bounded
header/mapping scope. It is **unreviewed, unintegrated, unqualified and not
worker-published**; broader VAL-15 disposition requires the coordinator and
qualified independent reviewer. The report-only follow-up uses scoped prose/
path/whitespace checks and an invocation-only empty hooksPath after the real
source hook and clean committed-source execution, with no source changes.
