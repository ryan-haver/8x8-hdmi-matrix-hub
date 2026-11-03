# QUAL-ANTHROPIC-CORE-01 — manual attempt 02

Owner-approved controlled single Anthropic qualification retake. The qualifying
verdict is the independent OpenAI judge's at the exact commit of this report,
then the coordinator's; delivery of this document does not qualify the
candidate. The first-attempt FAIL (evaluator `97c47be3…`, judge `5b70c916…`,
first disposition SHA `4a9f1da6…`) remains unchanged and this attempt grants
no further retake. Authority: owner reply "approved" recorded in
`docs/production/software-waves/MVP-EXECUTION-20261102/QUALIFICATION_MANUAL02_AUTHORIZATION.json`.

## Scope and inputs

- Candidate model: `claude-opus-4-7` at effort `high`, via Orca `agentclaude`.
  Native route verified from the active session's model-id reminder. No
  fallback, alias, inherited, nested, subagent, MCP, plugin or helper launch
  was used; no new accounts, credentials, spend, installs or global settings.
- Candidate source: `caaa4faabe9ede1e3aed37d2269efd4a4d691e04` (confirmed with
  `git rev-parse HEAD` in the dedicated `wp-exec-qual-anthropic-core-01-manual02`
  worktree; clean working tree at start).
- Review base: `938ae30339790c361abdda6fdd01b11a4e498518` (frozen packet value).
- Rubric: `docs/production/software-waves/MVP-EXECUTION-20261102/QUALIFICATION_RUBRIC.json`
  SHA256 `66f37090564007afebe29cdfd095af7fa85c4321a8420016ada8633dc0563672`
  (recomputed locally and matches). All six mandatory axes evaluated.
- Review window diff: nine changed paths observed with
  `git diff --stat 938ae303..caaa4faa`:
  - `docs/production/software-waves/SW-API-CLIENT-02-C1/AUTHOR.md` (+212)
  - `docs/production/software-waves/SW-API-CLIENT-02-C2/AUTHOR.md` (+219)
  - `docs/production/software-waves/SW-API-CLIENT-02-C2/INTAKE.md` (+105)
  - `docs/validation/features.yaml` (+1/-1)
  - `tests/validation/scenarios/sw_api_client_02_c1.py` (+35)
  - `tests/validation/test_sw_api_client_02_c1.py` (+220)
  - `tests/validation/test_sw_api_client_02_c2.py` (+224)
  - `tools/validate/model.py` (+12)
  - `tools/validate/runner.py` (+24/-4)
- Commit chain inside the window: `38687231` original author entry,
  `ee3f2e7f` managed-health follow-up, `caaa4faa` C2 managed proof +
  retained global-gate failure. The earlier commit `060769` is outside the
  review boundary and was not reviewed. Original DeepSeek/OpenAI authorship on
  the C1/C2 AUTHOR.md and INTAKE.md files is preserved and attributed in those
  documents.

## Native route, isolation and plugin disables

For both invocations the executable was
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
(the root checkout's venv, 3.12.10). Each invocation had its own fresh parent
under `C:/t/exec-qual-anthropic-core-01/nov03-manual02/<label>/` with separate
`data/`, `config/`, `native-temp/`, `pytest-temp/` subdirectories;
`MATRIX_DATA_DIR`, `UC_CONFIG_HOME`, `TEMP` and `TMP` all pointed into that
parent so tempfile fixture bytes landed inside preservation scope.
`PYTHONPATH` was `<repo>` + `<repo>/src`; `PYTHONUTF8=1` and
`PYTHONDONTWRITEBYTECODE=1`. Plugin disables `-p no:tests.route_inventory`
and `-p no:cacheprovider` were passed from the first invocation. `pytest`
version string recorded in each `manifest.json`. Each invocation was a single
`subprocess.run(..., capture_output=True)` whose returncode, full stdout and
full stderr were preserved separately — no tee, no tail, no pipeline-exit
inference. The one-off capture driver lived in the session scratchpad and is
not a committed, reusable or tested harness.

## Observed test outcomes

### Validation C1 + C2 (one invocation, parent `val-01`)

- Argv (verbatim): `python -I -u -m pytest tests/validation/test_sw_api_client_02_c1.py tests/validation/test_sw_api_client_02_c2.py --basetemp=…/pytest-temp --junitxml=…/junit.xml -p no:cacheprovider -p no:tests.route_inventory -vv --tb=short --no-header`
- Direct subprocess returncode: `0`.
- JUnit (`junit.xml`, 8,433 B,
  SHA256 `recorded in val-01-receipts.json companion`):
  `tests=54 errors=0 failures=0 skipped=0 time=54.517s`.
- Pytest terminal line: `54 passed in 54.52s`.
- Wall duration: 55.2 s. Matches the historical 54-case expectation; no cases
  were forced on or off. No retry was performed.

### Documentation modules (one invocation, parent `docs-02`)

- Tests: `tests/test_core_documentation.py tests/test_client_guides_docs.py
  tests/test_openapi_and_config_docs.py tests/test_security_docs.py
  tests/test_license_and_protocol_docs.py` with identical isolation and plugin
  disables.
- Direct subprocess returncode: `0`.
- JUnit: `tests=489 errors=0 failures=0 skipped=0 time=3.145s`.
- Pytest terminal line: `489 passed in 3.17s`. Docs green is not source proof
  and does not repair attempt 1.

### Preserved fixture receipts (sanitized, bounded)

`build/software-waves/QUAL-ANTHROPIC-CORE-01/manual-attempt-02/author/val-01-receipts.json`
lists SHA256 hashes and byte sizes of every ordinary JSON file emitted into
`val-01/pytest-temp` (177 total files in the parent). Known child-process facts
drawn only from `external-stack-receipt.json` and `managed-process-receipt.json`
(the test fixtures' own receipts, unmodified):

- `test_registered_scenario_with_0/external-stack-receipt.json` — real
  managed `SimulatorProcess` (sim pid `93072`) and `HubProcess` (hub pid
  `49572`), both exited (exit code `1` is Windows-signal termination from the
  fixture's `stop()`; the receipt confirms both procs settled);
  `initial_health.matrix.connected = false` under the TLS-strict `hub_env`.
- `test_inherited_scenario_in_rea0/managed-process-receipt.json` — five
  recorded children (`ReceiptRunner` captured one simulator plus distinct hub
  generations across the mixed-lifecycle run), all with `exit_code = 1`.
- `test_wrong_actual_managed_prec0/managed-process-receipt.json` — three
  children all exited (`exit_code = 1`), confirming blocking before action.
- `test_wrong_actual_managed_prec1/managed-process-receipt.json` — three
  children all exited (`exit_code = 1`).

These receipts cover known fixture-controlled handles only, not a complete
descendant census, so unknown descendants remain unknown. No global process
scan or kill was executed; nothing was deleted or resurrected from attempt 1.
Raw receipt bytes, logs and test temp files remain private under
`C:/t/exec-qual-anthropic-core-01/nov03-manual02/val-01/**` and `docs-02/**`
(177 and 1 file respectively); only the sanitized hash/size manifest is
published here.

## Six-axis observations

```json
{
  "attempt": 2,
  "candidate_source": "caaa4faabe9ede1e3aed37d2269efd4a4d691e04",
  "review_base": "938ae30339790c361abdda6fdd01b11a4e498518",
  "rubric_sha256": "66f37090564007afebe29cdfd095af7fa85c4321a8420016ada8633dc0563672",
  "axis_observations": {
    "provenance": {
      "note": "9 changed paths observed via git diff --stat 938ae303..caaa4faa; three commits inside window (38687231, ee3f2e7f, caaa4faa); 060769 is outside and not reviewed. Candidate SHA matches rubric candidate_sha; review base matches rubric review_base_sha. Rubric SHA256 recomputed locally and matches declared value. Native route is claude-opus-4-7/high via Orca agentclaude, confirmed from the session's model-id reminder; no fallback or inherited substitution. Original DeepSeek/OpenAI authorship on C1/C2 wave AUTHOR.md and INTAKE.md stays accurate.",
      "unknowns": "Model-id reminder is a session-time attestation; the candidate cannot independently prove it to the OpenAI judge beyond this attestation and the git-attributed commit record."
    },
    "invariants": {
      "appended_field": "Scenario gains matrix_connection: Literal['ready','disconnected'] default 'ready' (tools/validate/model.py L472). Default preserves earlier behavior for every existing scenario; no existing scenario file was touched to add the field.",
      "declaration_guard": "Scenario.__post_init__ rejects any value outside the Literal and, for 'disconnected', requires targets==('sim',), clients==('api',), kind=='failure', empty writes/setup/cleanup/faults (model.py L475-L482).",
      "runtime_guard": "Runner._prepare_sim_matrix re-enforces the same shape at runtime (runner.py L467-L485), raising RuntimeError on any mismatch before any read; Runner._refusal shortcircuits (target!=sim or client!=api) for the disconnected profile before scenario dispatch (runner.py L553-L554).",
      "health_envelope": "Strict identity checks: status==200 AND isinstance(body, dict) AND body.get('success') is True AND isinstance(matrix, dict) AND matrix.get('configured') is True AND matrix.get('connected') is False. Non-identity truthy/falsy values are rejected (confirmed by the 21-case parametrization in C2).",
      "api_failure_scope": "Only the simulator-only API failure path consumes the new preparation; hardware path still calls _wait_hub_telnet directly, so Telnet/external/hardware behavior is unchanged.",
      "side_effects": "No change to evidence schema, record keys, Scenario schema (apart from the new field), features.yaml structure (one scenario id appended to F-API-034's scenarios list; routing.route_all preserved), or client/stack APIs. No evidence/schema weakening observed within the review scope.",
      "violations_found": "none"
    },
    "counterexamples": {
      "c1_payload_counterexamples": "test_disconnected_route_all_exact_payload_and_no_effect parametrizes requested over (1, 4, 8, ' 6 '): all return HTTP 503 with exact body {success:false, data:null, error:'Matrix not connected'}; WS emits switch_all_failed with int-typed input==expected; four counterfactual oracles must each fail (Response 200, Response 503 success:true, wrong-input WsEvent, routing_change event, NoWsEvent 'switch_all_failed'). test_invalid_offline_input_has_no_failure_payload_or_success parametrizes 6 malformed POST /api/switch bodies, each producing the same 503 refusal, no WS failure or routing event, no device write, and failing the registered valid-input oracle.",
      "c1_positive_control": "test_connected_routing_and_invalid_input_controls proves the oracles are not vacuously satisfied: connected matrix route(6->1) succeeds, no-command/unchanged/no-WS oracles fail; a connected 400 refusal on input=9 leaves device/log/WS silent.",
      "c2_declaration_counterexamples": "12 parametrized dataclass replacements against the disconnected scenario each raise ValueError (bad matrix_connection, hardware target, non-api client, happy kind, writes/setup/cleanup/faults).",
      "c2_runtime_refusal_counterexamples": "Three (target,client) combinations where _refusal returns a scoped message and _prepare_sim_matrix raises before any helper read.",
      "c2_envelope_counterexamples": "21 health-envelope rows parametrize body shape and status: non-mapping body, missing success, success in (False,1,'true',None), missing/wrong matrix shape, configured not identity True, connected not identity False (True,0,'false',None), status 503. Each raises RuntimeError 'HTTP 200 health'. test_health_transport_failure_is_not_disconnected_evidence proves a closed-port OSError is NOT swallowed as evidence of disconnected health.",
      "c2_default_preservation": "test_default_preparation_preserves_actual_telnet_wait_and_external_behavior proves ready scenarios keep calling /api/status/cables (managed) and skip it on an external hub.",
      "c2_managed_mixed_lifecycle": "test_inherited_scenario_in_real_managed_mixed_lifecycle runs three real scenarios (contracts.cables, sw_api_client_02_c1, routing.switch_one) under a real SimulatorProcess+HubProcess with environment restarts; the C2 refusal record is schema-validated and passes 8 checks; the earlier/later Telnet-prepared scenarios keep the ready preparation step and distinct OREI_VERIFY_SSL env.",
      "c2_blocked_precondition": "test_wrong_actual_managed_precondition_blocks_before_action proves ready-with-TLS-strict blocks on Telnet, disconnected-with-default-env blocks on health; both leave observations.requests empty and no procedure step with 'action ('.",
      "distinction": "Observed execution: 54 passed in 54.52s (JUnit tests=54 time=54.517s, returncode 0). Static before/after analysis: the diff and the fixture receipts, which are explicitly separated above from the dynamic run."
    },
    "behavior_and_tools": {
      "disposable_only": "Both validation tests exercise the shipped tools/simulator stack on loopback plus the real hub subprocess; no real hardware/network/external deployment or new source/test/tool deliverable was introduced.",
      "process_handles": "External-stack and managed-process receipts enumerate real pids/argv/exit codes/recorded env; all captured handles exited (code 1 is the fixtures' Windows signal termination path). Known fixture handles only — descendant census is incomplete and unknowns stay unknown.",
      "evidence_hashes": "Validation evidence records emitted into pytest-temp/evidence/F-API-034/ (and F-API-004, F-MTX-001 for the mixed lifecycle) are inventoried in val-01-receipts.json with per-file bytes and SHA256; six distinct F-API-034 records across sub-tests.",
      "docs_run": "489 docs tests passed in 3.17s (returncode 0); treated as hygiene, not source acceptance."
    },
    "calibration": {
      "preserved": "Commit caaa4faa title records the retained C2 managed proof alongside the failed global gate; the preceding ee3f2e7f commit records the stricter disconnected preparation. Historical FSEC007 global freshness/level gate failure is not waived or rerun. No V3 integration, canonical evidence admission or source acceptance follows this attempt. Original attempt 1 artifacts (evaluator 97c47be3, judge 5b70c916, first-disposition SHA 4a9f1da6…) are referenced only; nothing from attempt 1 was reconstructed, resurrected or relabeled.",
      "domain_bound": "If independently accepted, eligibility is only the bounded Python validation-runner/model offline simulator API refusal preparation and relevant compatibility guards; no blanket authentication/privacy/UI/HA/image/physical competence inferred."
    },
    "review_quality": {
      "findings": "none within the inspected boundary.",
      "reasoned_no_finding": "The appended Scenario field has a safe default so existing scenarios are untouched; declaration and runtime guards redundantly bar unsafe shapes (defense in depth, verified by test_runtime_guards_also_apply_to_direct_preparation); the health precondition uses identity comparisons that correctly reject coerced truthy/falsy values and non-200 statuses; the refusal path does not swallow transport errors (test_health_transport_failure_is_not_disconnected_evidence); the hardware path is unchanged; evidence schema and features.yaml change surface is minimal (one scenario id appended) and preserves routing.route_all under F-API-034; cleanup/setup/write prohibitions on the disconnected profile are enforced at both static and runtime layers so no mutating side effect is possible on the simulator for this scenario. No candidate counterexample was found within the review window that would make the oracles vacuous or allow a passing refusal when the matrix was in fact connected (the connected positive control proves non-vacuity).",
      "unknowns": "Qualification verdict is the fresh independent OpenAI judge's and the coordinator's; this report does not grant source acceptance (RV-API034) or any blanket authorization. No descendant process census beyond the fixtures' own receipts; no cross-run reproducibility beyond the single invocation each performed here."
    }
  },
  "qualified_domain": null,
  "source_acceptance": false,
  "first_attempt_status_preserved": "FAIL"
}
```

## Delivery and limits

- Report commit (filled in by the committing invocation; see git log on this
  file). Dispatch IDs for coordinator settlement: Task `task_1d3db0c0e0e8`,
  Dispatch `ctx_ea6771c3440b`.
- Delivery of this file does not qualify the candidate. The OpenAI judge
  decides at the exact commit of this report; the coordinator records the
  final bounded disposition. No further retry is authorized by this attempt.
- No push, merge, tag, release, source edit, test edit, tool edit, hardware
  test, Docker/HA/CI run, external network action or ownership deployment was
  performed. The source candidate, rubric and domain remain unchanged.
- Private evidence bytes (fixture logs, test receipts, full capture streams)
  remain under `C:/t/exec-qual-anthropic-core-01/nov03-manual02/val-01/**`
  (177 files, 764 KB) and `.../docs-02/**` and are not published; only the
  sanitized sidecar manifest `author/val-01-receipts.json` ships beside this
  report.
