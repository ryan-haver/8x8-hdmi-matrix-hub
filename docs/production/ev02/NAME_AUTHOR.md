# EV-02 input-name evidence author report

Implemented bounded F-API-018 input-name evidence in `writes.py`; no product
defect reproduced. Author delivery is complete subject to the coordinator's
registry integration and qualified independent DeepSeek review at the submitted
commit. These API/simulator results do not close BE-16 or any release gate.

## Authority and scope

- Task `task_9341adb87ed9`, Dispatch `ctx_f12cb2321b79`, existing Run
  `run_37205f6095b3`; local Windows execution through Orca.
- Immutable base: `3979d6020165bcf31f0f44f21de6bb5b3648dc1e`.
- Actual branch: `ryan-haver/wp-ev02-input-name`; initial checkout was clean.
- Orca worker receipt requests and selects `codex:gpt-6.1-sol`, effort `high`;
  terminal observation also identifies GPT-6.1-Sol high. No helpers/subagents.
- Own inherited managed account pool suffix `4ed0` matched the coordinator.
  Supported read-only `account/rateLimits/read` at 2026-10-20T03:45:10Z showed
  38% used / 62% remaining in the 10,080-minute weekly window, reset
  2026-10-25T20:07:49Z, ordinary usage allowed, no secondary window and no
  additional credit. Sanitized receipts are under the artifact directory's
  `preflight/`; credentials were not read or exported.
- Changed tracked paths: `tests/validation/scenarios/writes.py` and this new
  report only. The scenario file adds 40 lines; existing output-name evidence
  is unchanged. No registry/ledger, runner/model/contracts, manifests/locks,
  product, baseline or historical evidence edits.
- Disposable output is under `build/ev02-name-author/`. TMP/TEMP, pytest base
  directories/cache and Ruff cache were redirected there; bytecode writes
  were disabled for validation invocations. Fresh hub fixture copies and
  simulator reset data were used, without root/private runtime data.

The submitted full commit, full base diff, path/status audit and committed-run
assertion inspection are recorded in `build/ev02-name-author/submission.json`
and `build/ev02-name-author/base-to-submission.patch`. These receipts are
created after the commit they identify to avoid a self-hash cycle. The exact
commit is also sent through the authoritative Orca completion message.

## Scenario assertions and mapping

All three additions explicitly declare `clients=("api",)`,
`targets=("sim",)` and `features=("F-API-018",)`; `client_features` is empty.
No browser, UC, HA, image-digest or physical-device proof is claimed.

`writes.input_name` is a happy scenario, with `writes=("names",)`. It seeds
input 8 as `Before source`, then POSTs `/api/input/8/name` with
`{"name": "  Media PC  "}`. Seven explicit checks assert:

1. HTTP 200 with success true, null error, and data containing input 8,
   name `Media PC` and message `Input 8 renamed to 'Media PC'`.
2. Independent simulator `inputs[7].name == "Media PC"`.
3. GET `/api/status`, HTTP 200, `data.input_names.8 == "Media PC"`.
4. Exactly one HTTP `set input name` command matching index 8, name `Media PC`
   and language 0.
5. Exactly one HTTP `set input name` command overall, excluding additional
   rename attempts with other parameters.
6. No other device-state leaf changes (only `inputs[7].name` allowed).
7. No simulator protocol warnings.

Cleanup restores input 8 to `Input 8` through the API, outside the measured
action window. Existing runner WebSocket-schema validation adds an eighth
check. The inspected initial run had exactly the intended before/after name
change, one mutating command, and eight passing checks.

`writes.input_name_invalid_port` POSTs `/api/input/9/name` with
`{"name": "Rejected source"}`. `writes.input_name_blank` POSTs
`/api/input/8/name` with `{"name": "  "}`. Both are failure scenarios and
seed input 8 as `Input 8`. Each has seven explicit checks: HTTP 400 with
success false, null data and the exact error (`Input must be between 1 and 8`
or `Name is required`); independent input-8 device name unchanged; hub GET
name unchanged; no `set input name` command (including non-mutating rejected
attempts); no mutating device command; entire device unchanged; and no
protocol warnings. The runner adds its WebSocket-schema check. Each initial
record had eight passes, an empty device diff and zero mutating commands.

Existing `matrix.input_blank_name`, `matrix.input_long_name`,
`matrix.input_invalid_port` and `matrix.input_name_refused` already cover
F-MTX-022 request boundaries and device refusal. They do not attribute those
assertions to F-API-018. The two bounded additions make invalid port and blank
name refusal discoverable for this API feature; they do not duplicate the
whole F-MTX refusal matrix or invent new product requirements.

All three additions declare the same exact covers sequence:

```text
run.py
src/hub/cli.py
src/hub/runtime_paths.py
src/hub/runtime
src/hub/core
src/hub/persistence
src/hub/domain/action_runner.py
src/hub/integrations/hub_client_local.py
src/orei_matrix.py
src/telnet_client.py
src/_task_supervisor.py
src/rest_api/app.py
src/rest_api/utils.py
src/rest_api/websocket.py
src/rest_api/events.py
docs/api/websocket.schema.json
src/rest_api/device_settings.py
src/rest_api/core.py
src/persistence.py
src/_file_io.py
tests/validation/scenarios/writes.py
```

Coordinator proposal for `docs/validation/features.yaml`, F-API-018 only:

```yaml
scenarios: [writes.output_name, writes.input_name, writes.input_name_invalid_port, writes.input_name_blank]
```

Retain the existing BE-16 finding, current/target levels and historical evidence.
Any evidence import/level decision, registry reconciliation, applicable route
inventory and serial ledger generation remain coordinator-owned.

## Executed validation

Python 3.12.10, Ruff 0.17.1; source hub version 2.10.0. No hardware, `--record`,
push, merge, cleanup or persistent hook change was performed.

| Command | Exit | Actual result |
| --- | --- | --- |
| `python -m ruff check tests/validation/scenarios/writes.py` | 0 | All checks passed |
| `python -m pytest -q -p no:tests.route_inventory tests/sim/test_sim_rest_writes.py --basetemp=build/ev02-name-author/pytest-writes -o cache_dir=build/ev02-name-author/pytest-cache --junitxml=build/ev02-name-author/rest-writes.xml` | 0 | 40 passed, zero skipped, 5.50 s |
| `python -m pytest -q -p no:tests.route_inventory tests/validation/test_model.py tests/validation/test_registry.py tests/validation/test_runner_timing.py tests/sim/test_sim_commands.py --basetemp=build/ev02-name-author/pytest-model -o cache_dir=build/ev02-name-author/pytest-cache --junitxml=build/ev02-name-author/scenario-model.xml` | 1 | 169 passed, one expected failure, zero skipped, 10.28 s |
| `python -m tools.validate run --target sim --client api --scenario writes.input_name --scenario writes.input_name_invalid_port --scenario writes.input_name_blank --out build/ev02-name-author/campaign --operator automation` | 0 | Three pass/V2 outcomes; 24 passing checks; no failed/skipped/n/a checks; aborted null |
| `git diff --check` | 0 | No whitespace errors |

The single pytest failure is
`tests/validation/test_registry.py::test_scenario_links_are_symmetric`:
`F-API-018 does not list scenario writes.input_name`. The test stops at that
first missing link; all three IDs require the proposed mapping above. The
registry was intentionally not patched. This is an incomplete integration
check, not a claimed full-suite pass or a reproduced product defect.

The first campaign records the immutable base with dirty `writes.py` and is
preserved as initial author verification, not fresh clean-commit evidence.
The exact submitted-commit rerun uses the same scenario command with
`--out build/ev02-name-author/campaign-committed`; its full SHA, exit, actual
counts and check/device-log inspections are in `submission.json`. Original
campaign bytes are preserved.

The task explicitly authorizes an invocation-only hook exception after the
assigned checks. The scoped commit uses `git -c core.hooksPath= commit` because
the broad hook would run coordinator-owned registry integration checks before
the mapping is integrated and may generate unowned route artifacts. This
does not claim hook/full-suite success; persistent hook configuration remains
unchanged. Independent cross-family review, coordinator acceptance/integration,
combined validation, publication/preservation and all wider gates remain open.
