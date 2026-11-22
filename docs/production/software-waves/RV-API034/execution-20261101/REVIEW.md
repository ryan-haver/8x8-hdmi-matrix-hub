# RV-API034 independent source review — SW-API-CLIENT-02 C1/C2

## Identity, authority and pinned inputs

- Reviewer: Anthropic `claude-opus-5-5`, high effort, launched as a genuine Orca
  worker (Task `task_43fbf6bb49a2`, Dispatch `ctx_4e0e187682b0`, worker terminal
  `term_de68c145-2d0c-400e-84dc-fbda8d79a0fc`, coordinator
  `term_6ed8131e-3ab3-4693-8094-56cc10acd412`). No helpers, subagents, teams,
  MCP, plugins or nesting were used. This is an actual source review. It is not
  a qualification retake, source integration or acceptance.
- Checkout: dedicated worktree `wp-exec-rv-api034-review`, branch
  `execution/wp-exec-rv-api034-review`, clean at entry on the exact candidate
  `caaa4faabe9ede1e3aed37d2269efd4a4d691e04`.
- Coordinator inputs were read through Git at the published integration ref
  `origin/wp-runtime-completion`. `git ls-remote` was checked once at
  shortly before 2026-11-04T01:39Z, and the full hash
  `a62b1b85bcce97de17a2fc6cde6eac8800cf3cef` was pinned for every input:
  `SOURCE_REVIEW_TASK_20261103.md`, `SOURCE_REVIEW_PREFLIGHT_20261103.json`, the
  QUAL-ANTHROPIC-CORE-01 `COORDINATOR_DISPOSITION.json` (scope fields only) and
  `AGENTS.md`. At the candidate, `AGENTS.md` still has the retired "No
  Claude/Anthropic" line. At the pinned integration ref, the owner routing
  direction of 2026-11-01 explicitly supersedes it. The preflight assigns this
  exact Anthropic route. No current integration source was imported into this
  tree, and no other tree's private runtime was read.
- Qualification PASS gives domain eligibility only: "bounded Python
  validation-runner/model offline simulator API refusal preparation and
  relevant compatibility guards". It does not approve these commits. I did not
  read the qualification evaluator or judge reports. The analysis below is my
  own.

## Candidate, base, lineage and authorship

| Commit | Subject | Paths | Actual author (from the records, not inferred from Git metadata) |
| --- | --- | --- | --- |
| `386872316cb60130b06dd704557ae6ca1a92b5c8` | test(validation): assert unavailable route-all refusal | C1 AUTHOR (append), `features.yaml`, scenario, C1 test | OpenAI `gpt-6.1-sol/high`; the one-line F-API-034 registry link is coordinator-authored (composite authorship recorded in C1 AUTHOR) |
| `060769b724e7a546b8df22eac82f3b288d9bbbe8` | docs(validation): record route-all partial acceptance | C1 AUTHOR (append only, +111/−0) | OpenAI `gpt-6.1-sol/high` |
| `ee3f2e7f034a9ace64553e942f328dff921a1e04` | fix(validation): require observed disconnected preparation | `model.py`, `runner.py`, scenario, C2 test, C2 AUTHOR, C2 INTAKE | OpenAI `gpt-6.1-sol/high` |
| `caaa4faabe9ede1e3aed37d2269efd4a4d691e04` | docs(validation): record C2 managed proof and failed global gate | C2 AUTHOR (append only, +103/−0) | OpenAI `gpt-6.1-sol/high` |

The review base is `938ae30339790c361abdda6fdd01b11a4e498518`. Each commit's
parent is the previous row, and the first row's parent is the base. The Git
author field is the repository owner on all four commits. The C1 AUTHOR sections
before line 180 are earlier DeepSeek product-handler work and are outside this
window. I verified that the base blob, 11,878 bytes with SHA-256
`c25692409f8d4f7ae38a21695571821475b1ec097de995517b266c2b59c4e9ff`, is the
exact byte prefix of the candidate file. Reviewer family (Anthropic) differs
from author family (OpenAI). The full base→candidate diff is exactly the nine
assigned paths: +1,053/−4. `git diff --check` exits 0.

## Inspection scope (per path and hunk)

I read every changed hunk in full, together with the underlying declarations,
callers and assertions named below.

| Path | Hunks read | Underlying code traced |
| --- | --- | --- |
| `tools/validate/model.py` | docstring 447-449; field 472; `__post_init__` guard 475-482 | Full `Scenario` dataclass 424-510; `NoCommand`/`NoWsEvent`/`WsEvent`/`Response`/`DeviceUnchanged` definitions |
| `tools/validate/runner.py` | `_prepare_sim_matrix` 467-485; `_refusal` 553-554; `_run_one` call site 623-625 | `Runner` lifecycle 296-509 (`_start_system`, `_use_hub_mode`, `_restart_hub`, `_stop_system`, `_scenario_environment*`, `_runner_started_hub`, `_wait_hub_telnet`), `_run_client` 511-550, all of `_run_one` 596-800 including verdict/gate, `_is_expected_application_error`, `_check` 850-1020, `_subset` |
| `tests/validation/scenarios/sw_api_client_02_c1.py` | Whole new file, plus the C2 delta (`matrix_connection`, notes, covers) | `src/rest_api/control.py::handle_switch` 86-174; `src/rest_api/core.py::_matrix_health` 202-228; `src/orei_matrix.py::_matrix_tls_policy` 129-139, `connected`/`telnet_connected`/`_link_lost`/reconnect 445-560; `tools/simulator/http_commands.py` `video switch`; `tools/validate/stack.py` `HubProcess.env/recorded_env/start/restart/stop`, `SimStack` |
| `tests/validation/test_sw_api_client_02_c1.py` | Whole new file (13 tests) | `ApiClient.request`, `WsObserver`, `SimDevice`, `run_external_scenario` external-stack interface (`_start_system` `sim_control_url` branch) |
| `tests/validation/test_sw_api_client_02_c2.py` | Whole new file (41 tests) | Same runner paths; `make_client`; `discover()` |
| `docs/validation/features.yaml` | F-API-034 `scenarios` line 4848 | Full F-API-034 row; `tools/validate/registry.py::validate_features` scenario-existence check 204-207 |
| C1 `AUTHOR.md` | Appended lines 180-391 (OpenAI addendum and final disposition) | Verified prefix and checkable counts (see the claims check below) |
| C2 `INTAKE.md` | Whole new file | Verified against the actual `ee3f2e7f` diff |
| C2 `AUTHOR.md` | Whole new file, including the `caaa` addendum | Verified against the diff, my control run and the static freshness analysis |

## Invariant, compatibility and control matrix

| Concern | Source behaviour observed | Evidence |
| --- | --- | --- |
| Typed/declarative validation | `matrix_connection` is appended last with default `ready`, so existing positional and keyword construction is unchanged. Invalid values such as `"skip"` or `None` raise. `disconnected` requires `targets == ("sim",)`, `clients == ("api",)`, `kind == "failure"` and no writes, setup, cleanup or faults. Frozen `replace()` re-runs `__post_init__`. All 1,508 discovered scenarios still load, and exactly one is `disconnected`. | model.py 472-482; C2 `test_disconnected_profile_rejects_unsafe_declarations` (11 cases); `inspect-registry-01` |
| Runtime guard (defence in depth) | `_refusal` skips `disconnected` on a non-sim target or non-API client before any environment restart. `_prepare_sim_matrix` re-checks every declaration guard and raises before issuing any HTTP request. | runner.py 472-476, 553-554; C2 `test_runtime_guards_also_apply_to_direct_preparation` (3; it uses an unstarted `ApiClient`, so a request would fail with an assertion rather than the asserted `RuntimeError`) |
| Typed health observation | Requires `status == 200`, a dict body, `success is True`, dict `data.matrix`, `configured is True` and `connected is False`, all by identity. Truthy look-alikes (`1`, `"true"`, `0`, `"false"`, `None`), a missing body, malformed envelopes, connected, unconfigured and 503 all reject. A transport failure propagates `OSError` and is never treated as "disconnected". The check makes one immediate read with no wait. | runner.py 477-485; C2 `test_health_precondition_rejects_inexact_observations` (21), `test_health_transport_failure_is_not_disconnected_evidence` |
| Default `ready` compatibility | Delegates to the unchanged `_wait_hub_telnet`. The procedure text is identical to the base for the managed stack and `None` otherwise, as in the base code. The hardware `else` branch is byte-unchanged. | runner.py 469-471, 626-631 (diff); C2 `test_default_preparation_…` (2); mixed lifecycle records for `contracts.cables` and `routing.switch_one` show the Telnet procedure step |
| External (`--hub-url` + `--sim-control-url`) | `ready`: no wait, unchanged. `disconnected`: the health read still happens, and `hub_env` is not applied (operator-owned, as documented). | runner.py 429-433, 447-449; C1 `test_registered_scenario_with_real_source_runner` PASS; see I-1 |
| Hardware | The scenario is skipped through `_refusal` with a new reason text (previously "does not run on target"). Nothing is restarted, and `_use_scenario_environment` is a no-op without a stack. | runner.py 429-431, 553-554; C2 runtime-guard test (`hardware`, `api`) |
| Startup/restart/stop lifecycle | `_run_client` applies the first scenario's environment. A scenario whose desired `extra_env` differs triggers a hub restart, and the next scenario's different environment restarts the hub back. No `restart_after`/faults restart is added for this scenario, and `_stop_system` runs in `finally`. My run observed 1 simulator and 4 hub generations (default → cables env → TLS-verify env → switch_one env). Every child had exited when the receipt was written, with launcher exit 1 for all of them, including connected hubs. That is recorded as observed, with no termination cause inferred. | `focused-01/preserved/basetemp/test_inherited_scenario_in_rea0/managed-process-receipt.json`, `logs/hub-1..4.log` |
| Disconnected cause | With `OREI_VERIFY_SSL=true` and blank CA/fingerprint, `_matrix_tls_policy` returns `True`. HTTP login fails with `CERTIFICATE_VERIFY_FAILED` and the client enters backoff. Telnet connects only after HTTP auth, so it is never attempted. `handle_switch` takes the `not connected` branch: `switch_all_failed {"input": n}` plus a 503 response, with no `direct_command`. | `orei_matrix.py` 129-139, 549-555; `control.py` 124-132; `hub-3.log` (`CERTIFICATE_VERIFY_FAILED` → `disconnected -> backoff`); record WS `connected` event `state=backoff` |
| Simulator connected/disconnected negatives | Disconnected route-all: exact 503 body, a single integer-normalised `switch_all_failed` for inputs 1/4/8/`" 6 "`, no `routing_change`/`switch_failed`, no `video switch`, no mutated write, identical state and a schema-valid WS stream. Each `NoCommand`/`NoWsEvent`/`DeviceUnchanged` oracle is shown to fail against a real connected route, and wrong status/body/event expectations fail against the real refusal (30 counterfactual oracle failures in total: 20 + 6 + 4). Invalid offline inputs give 503 without publishing a failure event. A wrong actual precondition (ready + TLS env, or disconnected + default env after a cables warm-up) is BLOCKED with gate `regression`, no recorded request and no action step. | C1 tests (13); C2 `test_wrong_actual_managed_precondition_blocks_before_action` (2); C2 `test_inherited_scenario_in_real_managed_mixed_lifecycle` (8/8 checks PASS in the retained record) |
| Feature link consistency / no promotion | The scenario's features are exactly `("F-API-034",)`, and exactly one registry row (F-API-034) links it. Relative to the base, F-API-034 differs only in `scenarios`: `current` V2 and `target` V3 are unchanged and no evidence was added. `validate_features` reports no problems. | `inspect-registry-01/stdout.txt`; see L-2 |
| Global freshness | `ee3f2e7f` makes all F-SEC-007 V3 evidence stale under the existing covers rule. | See M-1; `inspect-fsec007-01` |

## Findings

### M-1 Medium (integration-blocking consequence): the C2 shared runner/model edit stales all F-SEC-007 V3 evidence and is the onset of the recorded global gate failure

- Location: `ee3f2e7f` changes `tools/validate/model.py` and
  `tools/validate/runner.py`. No other commit in the window touches them.
- Mechanism: `tools/validate/ledger.py::freshness` marks a record stale when
  any path in `git diff --name-only <record sha>..HEAD` matches its `covers`.
  The F-SEC-007 row lists 28 records. All 16 V3 browser records (8 at
  `2ae46e6c`, 8 at `310d8b65`) and the 8 V2 `sw_sec_auth_01.*` API records
  declare `covers` that match both edited paths. At the base, the `310d8b65`
  set had zero covered changes, so it was fresh. The 12 `2ae46e6c`
  `sw_sec_auth_01.*` records were already stale at the base, with three covered
  paths each. At the candidate, every V3
  record is stale. Only the four `security_hardening.*_wrong_pin-api` V2
  records, which do not cover runner/model, stay fresh. The proven level is
  therefore V2, below the recorded V3. That is exactly the single gate line the
  author observed once: `(b) F-SEC-007 dropped below its recorded level: level
  V2 < recorded V3`.
- Reproduction: a static, read-only inspection through the repository's own
  `gitinfo.matches`, receipt `inspect-fsec007-01` (exit 0). Ancestry of both
  record commits to the base was verified with `git merge-base --is-ancestor`.
  I did not rerun the global gate. It is not authorized here, and the
  historical FSEC007 failure remains failed with no retry or waiver.
- Impact: integrating `ee3f2e7f`/`caaa` as-is makes the existing global
  `tools.validate check` fail on F-SEC-007. This is a deterministic evidence
  freshness consequence of editing a covered shared tool. It is not a product
  security regression, and it is not a logic defect in the new runner code.
  The author recorded "not its historical onset"; this analysis supplies the
  onset.
- Disposition: HELD for the coordinator and for appropriately qualified
  security/V3 review. Fresh F-SEC-007 browser/API proof at a post-change
  commit, or another explicit registry decision, is outside my qualified
  runner/model/refusal scope. I did not enumerate other features whose evidence
  covers these files but which stayed at or above their recorded level, because
  that would be broad validation.

### L-1 Low: the disconnected precondition is a point-in-time snapshot, not proof of a durable or caused disconnect

- Location: `runner.py` 477-485.
- Observation: a single immediate health read is accepted. Normal startup
  passes through `disconnected -> connecting` and can briefly report
  `connected=false`. C2 INTAKE/AUTHOR record exactly that in focused
  attempt01, which is why the negative control first warms up with
  `contracts.cables`.
- Impact: for this scenario the TLS setting makes the disconnect durable. The
  hub log shows `CERTIFICATE_VERIFY_FAILED` and the WS `connected` event shows
  `state=backoff`. The refusal/no-write oracles also fail closed if a
  connection completes before the action, as attempt01 demonstrated. I found
  no false-PASS path. However, the procedure line "observe /api/health … connected=false" does not by
  itself establish why the matrix is unavailable, and a future `disconnected`
  scenario whose `hub_env` does not durably prevent connection could race.
- Optional follow-up for the author/coordinator: also require a non-startup
  link state (for example the WS `connected` event `matrix.state` of
  `backoff`/`disconnected`) or re-observe health after the action, or state the
  limitation in the docstring. Non-blocking.

### L-2 Low (coordinator-owned registry prose): F-API-034 `basis` is stale

- Location: `docs/validation/features.yaml` 4844.
- Observation: the basis still says `switch_all_failed: V1 (sent by the handler
  on a refused write; no scenario yet)`, while line 4848 now links
  `sw_api_client_02_c1.switch_all_failed`. Leaving `current`/`target`
  unchanged is correct non-promotion. The prose is now inaccurate. The C1
  AUTHOR record states the coordinator deliberately left the basis unchanged.
- Suggested disposition: the coordinator updates the prose without changing
  the level once evidence admission is decided. Non-blocking.

### L-3 Low: stale comments after C2

- `tests/validation/test_sw_api_client_02_c1.py` 141-143: the docstring says
  "Managed preparation requires healthy Telnet, so it cannot prepare this
  deliberately unavailable hub". Since `ee3f2e7f` that is false: C2 makes
  managed preparation work.
- `tests/validation/scenarios/sw_api_client_02_c1.py` 12-14: the comment says
  the approach works "without … changes to the shared runner". C2 changed the
  shared runner for this scenario.
- Impact: misleading to future maintainers only, with no behaviour change.
  Non-blocking.

### I-1 Informational: external-hub mode with a connected operator hub blocks as a regression

`hub_env` is never applied to external hubs, consistent with existing hub_env
precedent and documented in the scenario notes. An image or external simulator
campaign that selects F-API-034, or all scenarios, against a normally
connected hub gets BLOCKED with gate `regression` for this scenario. That is
fail-closed, not a false pass, but the operator must launch a separately
configured hub or exclude the scenario. No existing test exercises the
external-connected blocked path directly. The managed equivalent is covered.

### I-2 Informational: evidence-record completeness

The precondition health exchange is summarised only in `procedure`. It is not
appended to the existing `observations.hub_reads` list, which would need no
schema change. `MATRIX_CA_CERT`/`MATRIX_TLS_FINGERPRINT` are absent from
`stack.py::RECORDED_ENV`, so a record alone shows only `OREI_VERIFY_SSL=true`
and cannot show the blank CA/fingerprint overrides. The cause is visible in
private hub logs. This was a lease-bounded author choice, and the change is
optional.

### I-3 Informational: unreachable arm and skip text

`_run_client` filters by `sc.clients` before `_refusal`, so the
`client.name != "api"` arm of `_refusal` is reachable only through direct calls,
which C2 exercises. On hardware the scenario's skip reason changes text only.

### Checks of the author records' claims (where checkable)

I confirmed the following:

- the 13 C1 and 54 combined focused tests;
- the 30 counterfactual oracle failures;
- inputs 1/4/8/`" 6 "`;
- that the Telnet waiter and hardware branch are unchanged and that runner
  changes are confined to the three leased sites;
- that the scenario's identity and expectations are unchanged by C2;
- that both report-only commits are pure appends;
- the C1 prefix hash;
- F-SEC-007 at `current`/`target` V3;
- one simulator and four hub generations with launcher exit 1.

The following claims cannot be verified from this checkout and are held,
neither accepted nor disputed:

- private build receipts, native transcripts and their hashes;
- hook runs (4,095 and 4,136 complete-core passes, 177/177 routes, Mypy);
- campaign record SHA-256s;
- coordinator messages and the lost C1 managed-failure bytes.

The lost original C1 bytes stay lost. My fresh run does not reconstruct them,
and the C1 historical failed/partial disposition is unchanged.

## Controls executed (this checkout, exact candidate)

Interpreter: `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
(CPython 3.12, pytest 9.1.1, aiohttp 3.13.3, jsonschema 4.26.0). The probe
confirms that `tools.validate.*`, the scenario module, `rest_api` and
`orei_matrix` import from this worktree. A venv editable finder is present, but
the `PYTHONPATH` entries take precedence for every module probed. Every child
ran `-B` with `PYTHONPATH=<root>;<root>/src`, `PYTHONDONTWRITEBYTECODE=1` and
`PYTHONUTF8=1`. Each run inherited the Windows environment through
`os.environ.copy()`, with its own fresh `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`,
`TEMP`/`TMP`, basetemp and JUnit under `C:/t/exec-rv-api034/<label>/`. Pytest
runs added `-p no:tests.route_inventory -p no:cacheprovider`. The child is
launched by direct `subprocess.run` (no shell, no pipeline). `-I` was used only
for the reviewer's wrapper process, not for the pytest children. The wrapper
also gained a `script` kind after `focused-01` and before the inspections.

| Label | Command (abridged; full argv in receipt) | UTC | Direct exit | Result |
| --- | --- | --- | --- | --- |
| `probe-01` | `python -B -c <origin probe>` | 01:39:07–01:39:08 | 0 | Origins as above |
| `collect-01` | `pytest tests/validation/test_sw_api_client_02_c1.py tests/validation/test_sw_api_client_02_c2.py --collect-only -q` | 01:39:17–01:39:18 | 0 | **54 collected** (C1 13, C2 41) |
| `focused-01` | Same two modules, `-q -rA` | 01:39:23–01:40:19 | 0 | **54 passed** in 55.63 s; JUnit tests=54 failures=0 errors=0 skipped=0; 174 temp files preserved, all SHA-256 copies matched |
| `inspect-registry-01` | `python -B registry_inspect.py` (read-only) | 01:41:06–01:41:07 | 0 | No registry problems; only F-API-034 `scenarios` changed |
| `inspect-fsec007-01` | `python -B fsec007_covers_inspect.py` (read-only) | 01:41:53–01:41:55 | 0 | M-1 data |
| `docs-01` | Five documentation modules (final prose check of this report) | see receipt | see receipt / Orca `worker_done` | This report is the subject of that check, so its result is not embedded here |

There were no failed, blocked or unknown control outcomes and no retries. All
dates are 2026-11-04.

## Limitations and blind spots

- I ran no global gate, ledger generation, broad suite, hook, browser, image,
  hardware, LAN or deployment work. M-1 is static analysis that matches the
  author's single observed gate line, not a fresh gate run.
- The tests prove behaviour on Windows loopback only. Timing (the 10 s Telnet
  wait, 0.2 s and 1 s negative-event windows) was not stress-tested. The
  absence-of-event oracles are bounded by those windows.
- The external-connected blocked path (I-1) and post-action durability (L-1)
  have no direct test.
- Security semantics of F-SEC-007, VAL-14/VAL-15 admission and any V3
  claim are outside my qualified scope and are held.

## Verdict

**PASS — bounded source review only.** In my qualified scope
(validation-runner/model offline simulator API refusal preparation and
compatibility guards), I found no blocking defect and request no author source
change. The declaration and runtime guards fail closed. The typed health
precondition is exact. Default, external and hardware behaviour is preserved.
The managed lifecycle restores the normal environment. The refusal and
no-effect oracles are failure-sensitive. The feature link does not promote the
level. L-1 to L-3 and I-1 to I-3 are optional, non-blocking follow-ups.

This is **not** integration or source acceptance. M-1 means that integrating
these commits makes the existing global gate fail on F-SEC-007. That
disposition is HELD for the coordinator and for an appropriately qualified
security/V3 review. Historical failed/partial outcomes are unchanged:
FSEC007, the lost C1 managed bytes and both author FAILED outcomes. I make no
V3, privacy, client, HIL, soak, hardware or release claim. The OpenAI
author-fix and secondary evaluation remain held below 30%. Nothing was
dispatched and no funding is implied.

## Artifacts (ignored/private; retained for coordinator preservation)

- Receipts, stdout/stderr, manifests and preserved temp bytes:
  `build/software-waves/RV-API034/execution-20261101/author/<label>/`
- Reviewer wrapper and inspection scripts:
  `build/software-waves/RV-API034/execution-20261101/author/tools/`
- Original invocation directories: `C:/t/exec-rv-api034/<label>/` and the
  C1-prefix check `C:/t/exec-rv-api034/prefix-check-01/`

Nothing was cleaned up. This tracked report is the only change. The
coordinator owns publication of the report commit; local commit is not remote
publication.
