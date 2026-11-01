# SW-API-CLIENT-02-C2 managed compatibility intake

Task `task_14b35f83dc26`, Dispatch `ctx_d658a8d62647`, Run
`run_37205f6095b3`; OpenAI `gpt-6.1-sol/high`, no helpers or fallback.
Dedicated `ryan-haver/wp-api-client-02-c2`, clean entry at exact base
`060769b724e7a546b8df22eac82f3b288d9bbbe8`. Coordinator generation 4:
`term_15310037-f316-4fe8-9bbd-012f4e5ce38f`.

## Observed source boundary

`Runner._use_scenario_environment` already applies the inherited scenario's TLS
settings to its managed simulator hub. `HubProcess.wait_ready` intentionally
requires listener readiness rather than matrix connectivity. However,
`Runner._run_one` resets the simulator then unconditionally calls
`_wait_hub_telnet`, which polls `/api/status/cables` for HTTP 200 for ten seconds.
TLS verification correctly prevents connecting to the self-signed simulator,
so this healthy-link requirement blocks before the action. Existing external
mode skips the waiter; no existing scenario-specific managed readiness control
was found. No new runtime reproduction has been performed during this intake.

The inherited scenario and refusal/no-write oracles are correct. Its original
managed failure and missing raw evidence remain failed/partial and immutable.
The separate historical external pass cannot establish managed compatibility.

## Proposed exact bounded change (pending coordinator lease)

Add `Scenario.matrix_connection: Literal["ready", "disconnected"] = "ready"`.
Reject invalid values and restrict `disconnected` to simulator-only API failure
scenarios with no declared writes, setup, cleanup or injected faults. This is an
explicit observed precondition, not an option to omit readiness checks.

Add a runner preparation helper: `ready` delegates to the existing unchanged
Telnet waiter; `disconnected` reads `/api/health` and requires HTTP 200 with an
actual configured matrix and `connected is False`, recording the observation
in the procedure. A connected, unconfigured, malformed or unreachable health
response blocks before action; do not sleep waiting for a fault to arrive.
Continue real WebSocket observation/synchronization, independent simulator
readback, refusal/event/no-command/state assertions and existing cleanup.
External operator settings remain untouched; hardware cannot select the new
precondition. Default and other clients keep the existing Telnet contract.

Set the inherited discovered C1 scenario's explicit precondition, update its
obsolete external-only note and include the new regression path in its covers.
No duplicate C2 scenario or feature-registry mapping is proposed.

Requested exact writable paths: `tools/validate/model.py`,
`tools/validate/runner.py`,
`tests/validation/scenarios/sw_api_client_02_c1.py`, NEW
`tests/validation/test_sw_api_client_02_c2.py`, NEW
`docs/production/software-waves/SW-API-CLIENT-02-C2/AUTHOR.md`, this intake and
own `build/software-waves/SW-API-CLIENT-02-C2/**`. Stack/client/product REST,
historical C1 tests/report, registry/ledger/findings, root/private/manifests,
locks, canonical evidence and baselines remain read-only.

## Proposed acceptance

Preserve a separately named current-base managed diagnostic before editing;
then prove the exact inherited scenario passes through genuine managed source
processes and all eight checks. Add default healthy/unhealthy readiness,
connected/unconfigured/malformed/transport-negative precondition and model
safety controls, plus mixed healthy/disconnected/healthy managed lifecycle.
Use meaningful real simulator/hub/WS observations and existing runner/environment,
model/registry/schema and offline-switch/WS regressions. Run configured Ruff,
Mypy, normal complete core source-commit hook with strict actual 100% registered
route coverage, then clean committed-source inherited managed CLI campaign and
actual global validation CLI gate. Record any global failure as failed/partial;
no automatic failing-gate retry or scoped substitute.

All invocations use the assigned root venv, own root/src PYTHONPATH, UTF-8,
disabled bytecode, isolated data/config and NEW empty TEMP/TMP parents under
`C:/t/f034-c2-20261031-a`. Immediately preserve produced JSON/log/exit/XML/process
receipts outside pytest retention with byte hashes before another invocation.
Record actual process exits without inventing graceful termination. Raw private
fixtures remain admission HOLD; API/sim V2 only. Review/integration/qualification,
publication and settlement are coordinator-owned; DeepSeek review quota remains
unknown and no review reserve is inferred.

Source/test/scenario work is paused pending the exact blocking-ask lease reply.

## Lease granted and intake disposition

At 2026-11-01T01:00Z the coordinator answered the blocking ask with the exact
bounded serial lease. The reply requires appending the model field compatibly,
leaving the Telnet waiter and hardware branch unchanged, runtime target/client
guards even for direct preparation calls, and strict HTTP 200 / `success is True`
/ configured true / connected false observations. Only bounded actual booleans
and status may be recorded in the existing procedure; no schema additions.
The initially proposed paths above are approved with these constraints. Full
source acceptance, review, integration and artifact admission remain separate.

The new `base-diagnostic-01` at exact060769b7 reproduced BLOCKED preparation;
CLI exit0 was not treated as success. Raw current JSON/hub logs and temp files
were immediately retained and hashed under the own private build tree before
pytest. This diagnostic is independent of the immutable lost C1 original.

Focused attempt01 passed52 and failed1: a connected negative control started a
normal hub but assumed listener readiness meant connection was already complete.
Actual startup health briefly satisfied configured/disconnected, then routing
completed; the refusal oracles failed correctly. The control was corrected to
establish connectivity using the real default cables scenario before requiring
disconnected health. Attempt01 remains preserved, without altered observations.
Focused attempt02 passed54 including the inherited external tests and genuine
healthy/disconnected/healthy managed lifecycle. All eight inherited managed
checks passed, and every observed child exited with actual code1 under the
unchanged Windows stop helper. See the new author record for final acceptance.
