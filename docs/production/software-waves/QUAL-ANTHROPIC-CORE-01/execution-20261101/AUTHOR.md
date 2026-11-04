# QUAL-ANTHROPIC-CORE-01 — candidate evaluation (Anthropic `claude-opus-4-7/high`)

Independent candidate evaluation of the committed changes within the frozen
`QUAL-ANTHROPIC-CORE-01` rubric. This report is the only new tracked deliverable
from this task; it is not a self-qualification pass, not `RV-API034` source
acceptance and not a bounded competence disposition. The coordinator's named
OpenAI-family judge inspects this report and its evidence at its exact commit.

## Authority, worktree and frozen rubric

- Task `task_e0fda51b39e2`, Dispatch `ctx_cd0f4f2bae5c`, existing Run
  `run_37205f6095b3`; worker terminal
  `term_7040d13e-e1b6-4393-9a82-9849134af6d5`, coordinator terminal
  `term_6ed8131e-3ab3-4693-8094-56cc10acd412` (generation 5), runtime
  `e8ce3460-a9d4-4897-8e4f-10a8e3cdc400`, Orca 1.4.246.
- Candidate under evaluation: Anthropic `claude-opus-4-7/high` (native, no
  helper, subagent, fallback or route substitution). Owner's 2026-11-02
  authorization permits Anthropic, Gemini, OpenAI Codex and MiniMax; the
  historical no-Anthropic rule in older checked-out worktree copies is
  superseded prospectively. DeepSeek is exhausted and not dispatched.
- Worktree: `wp-exec-qual-anthropic-core-01` on this Windows host at
  `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-exec-qual-anthropic-core-01`,
  branch `execution/wp-exec-qual-anthropic-core-01`, HEAD
  `caaa4faabe9ede1e3aed37d2269efd4a4d691e04`, `git status --short` clean before
  work.
- Review boundary (fixed by rubric): base
  `938ae30339790c361abdda6fdd01b11a4e498518` → candidate
  `caaa4faabe9ede1e3aed37d2269efd4a4d691e04`, source commits
  `386872316cb60130b06dd704557ae6ca1a92b5c8` and
  `ee3f2e7f034a9ace64553e942f328dff921a1e04`. `060769b7...` is an author
  record entry only and is not the independent review boundary.
- Frozen rubric
  `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/docs/production/software-waves/MVP-EXECUTION-20261102/QUALIFICATION_RUBRIC.json`
  SHA256
  `66f37090564007afebe29cdfd095af7fa85c4321a8420016ada8633dc0563672`
  (verified READONLY).

Writes in this task are restricted to this new `AUTHOR.md` and the private
`build/software-waves/QUAL-ANTHROPIC-CORE-01/execution-20261101/author/**`
retention tree (gitignored under `build/`), plus temporary artifacts under
`C:/t/exec-qual-anthropic-core-01/nov02-attempt01/**`. No source, test, tool,
fixture, scenario, schema, registry, ledger, evidence, baseline, hooks or
settings file was changed; no package install, hardware, Docker, external
network, global settings, version/tag/main/release operation was performed; the
root ignored routing config is coordinator-owned/read-only.

## Review boundary and inspected files

`git diff --stat 938ae303..caaa4faa` (full list, byte-equal to committed state):

| Path | Lines |
| --- | --- |
| `docs/production/software-waves/SW-API-CLIENT-02-C1/AUTHOR.md` | +212 |
| `docs/production/software-waves/SW-API-CLIENT-02-C2/AUTHOR.md` | +219 |
| `docs/production/software-waves/SW-API-CLIENT-02-C2/INTAKE.md` | +105 |
| `docs/validation/features.yaml` | ±1 |
| `tests/validation/scenarios/sw_api_client_02_c1.py` | +35 |
| `tests/validation/test_sw_api_client_02_c1.py` | +220 |
| `tests/validation/test_sw_api_client_02_c2.py` | +224 |
| `tools/validate/model.py` | +12 |
| `tools/validate/runner.py` | +26 / −2 |

Boundary commits:

- `3868723` — `test(validation): assert unavailable route-all refusal`
  (new C1 scenario, test module, features.yaml map `F-API-034 → sw_api_client_02_c1.switch_all_failed`).
- `ee3f2e7f` — `fix(validation): require observed disconnected preparation`
  (adds `Scenario.matrix_connection`, `__post_init__` scope guard,
  `Runner._prepare_sim_matrix` + call-site swap, `_refusal` disconnected
  guard, C2 test module, updates C1 scenario note/covers to add
  `matrix_connection="disconnected"`).
- `caaa4faa` — `docs(validation): record C2 managed proof and failed global gate`
  (prose-only append to `SW-API-CLIENT-02-C2/AUTHOR.md`).

File SHA256 at `HEAD caaa4faa`:

| File | SHA256 |
| --- | --- |
| `tests/validation/scenarios/sw_api_client_02_c1.py` | `360ed66a76c44794a3e94b5644202c68a6c6e5867f78dbdc07473df60281004b` |
| `tests/validation/test_sw_api_client_02_c1.py` | `f53a36885a4232c0634e884b33187f38951cfae43b3f3e7a26b44ed0f78c1ac3` |
| `tests/validation/test_sw_api_client_02_c2.py` | `03f204ea453afa1e865f116b904e42e2bdb1f7b3f05015ae07d76ee9766f3179` |
| `tools/validate/model.py` | `f24dcd3c30841d5e78e8fe55e7ed2bb8a977bdaca738a1dc210f5aeb480c4a6e` |
| `tools/validate/runner.py` | `c2c60ecba1cab1533a713f5f461c5e856fb175d3dc1e361777e9a653de94e6e2` |
| `docs/validation/features.yaml` | `4b69d22cc999c79eb0f2569038ad95aff50e5e7fe7d3115a7bec074a68010332` |

## Static analysis of the candidate changes

### `tools/validate/model.py` (Scenario field addition)

`tools/validate/model.py:472` appends `matrix_connection: Literal["ready",
"disconnected"] = "ready"` after the existing scenario fields; the default
preserves every existing scenario's behavior at the type level
(no `replace` needed in registry). `__post_init__` validates:

- `tools/validate/model.py:476-477` — enum guard rejects any value outside
  `{"ready","disconnected"}`.
- `tools/validate/model.py:478-483` — scope guard: `matrix_connection ==
  "disconnected"` requires `targets == ("sim",)`, `clients == ("api",)`,
  `kind == "failure"`, and empty `writes/setup/cleanup/faults`. Any violation
  raises with the message `scenario {id}: disconnected preparation requires a
  simulator-only API failure without writes, setup, cleanup or faults`.

Scope invariant: a disconnected preparation can only express a failure path.
No oracle for writes/setup/cleanup/faults can be declared alongside it, which
is the structural reason the matrix stays unmodified during the refusal.

### `tools/validate/runner.py` (preparation helper, call-site swap, refusal
guard)

- `tools/validate/runner.py:467-485` adds
  `Runner._prepare_sim_matrix(sc, client, helper) -> str | None`:
  - `matrix_connection == "ready"`: delegates to the existing
    `_wait_hub_telnet` (unchanged, lines `451-465`) and appends the existing
    procedure string
    `"wait for the simulator Telnet link before setup and fault injection"`
    only when `self.stack` is truthy. Equivalent to the pre-patch body
    (`if self.stack is not None: procedure.append(...)`); the terse form
    `if self.stack` matches the project's `_runner_started_hub` idiom.
  - Non-ready path repeats the scope guard before any I/O: target `sim`,
    client `api`, `targets == ("sim",)`, `clients == ("api",)`, `kind ==
    "failure"`, no writes/setup/cleanup/faults, otherwise `RuntimeError:
    disconnected preparation requires a simulator-only API failure ...` is
    raised **before** the helper HTTP session is used. This is defense-in-
    depth over the `_refusal` and `__post_init__` guards.
  - Observed-health branch issues exactly one `GET /api/health` and strictly
    requires HTTP 200, `isinstance(body, dict)`, `body["success"] is True`,
    `isinstance(matrix, dict)`, `matrix["configured"] is True` and
    `matrix["connected"] is False`. The `is True`/`is False` checks reject
    truthy non-bool values (`1`, `"true"`, `0`) rather than coercing. A
    non-mapping body, missing keys, truthy-non-bool fields or HTTP 503 all
    fail with `RuntimeError: disconnected preparation requires HTTP 200
    health with success=true, configured=true and connected=false`.
  - Returns the bounded procedure string `"observe /api/health: HTTP 200,
    success=true, matrix configured=true, connected=false"` — purely
    descriptive, no payload values and no new record keys.
- `tools/validate/runner.py:552-553` adds a refusal guard in `_refusal`:
  on `matrix_connection == "disconnected"` with a non-sim target or non-api
  client it returns `"disconnected preparation requires simulator target and
  API client"` **before** any other refusal check. This blocks the scenario
  earlier in `_run_client` than the existing scope checks.
- `tools/validate/runner.py:620-625` swaps the hard-coded SimDevice
  `_wait_hub_telnet`/procedure call site for `_prepare_sim_matrix(sc, client,
  helper)` and appends the returned procedure string if non-empty. The
  HardwareDevice branch (`runner.py:626-631`) is byte-identical to pre-patch;
  the explicit Telnet wait, hardware snapshot and existing procedure strings
  for hardware are unchanged.

### `tests/validation/scenarios/sw_api_client_02_c1.py`

- `scenarios/sw_api_client_02_c1.py:9` declares
  `sw_api_client_02_c1.switch_all_failed`, `features=("F-API-034",)`,
  `clients=("api",)`, `targets=("sim",)`, `kind="failure"`,
  `matrix_connection="disconnected"`.
- Hub env `OREI_VERIFY_SSL=true`, `MATRIX_CA_CERT=""`,
  `MATRIX_TLS_FINGERPRINT=""` (lines `16`): the disposable simulator's
  self-signed TLS leaves the real matrix client disconnected under normal
  verification — no mocks, no external addresses, no fixed ports.
- `expect` (lines `17-26`): HTTP 503 `{"success": False, "data": None,
  "error": "Matrix not connected"}`, exactly one WS `switch_all_failed`
  with `{"input": 6}`, `NoWsEvent("routing_change")`,
  `NoWsEvent("switch_failed", timeout=0.2)`, `NoCommand("video switch")`,
  `NoCommand()`, `DeviceUnchanged()`.
- `covers` (lines `27-30`) names the leased source paths and both test
  modules; `notes` describes managed preparation under declared TLS, plus
  the external disposable path, and labels proof as V2 only.

### `tests/validation/test_sw_api_client_02_c1.py`

Local fixture (`live`) stands up a real simulator, Telnet port override,
loose-TLS matrix connection, actual hub app via `aiohttp_client`, real
`ApiClient` and WsObserver. The disconnected observation is produced by
`await matrix.disconnect()` on the real matrix object, not by mocks. The
test parametrizes `requested in (1, 4, 8, " 6 ")` to assert input
normalization (string `" 6 "` → `switch_all_failed {"input": 6}`,
`type(input) is int`), oracle pass/fail polarity across six wrong oracles,
device unchanged after refusal, and `ws_contract_check` pass.
Also exercises invalid payloads (missing/wrong-type/extra keys) and asserts
no `switch_failed`, no `routing_change`, no command, no mutation.
The `test_connected_routing_and_invalid_input_controls` case drives real
routing success and HTTP 400 input-validation refusal through the same
fixture to prove the oracles distinguish accepted from refused.
`run_external_scenario` / `test_registered_scenario_with_real_source_runner`
launches `run.py` + simulator as owned subprocesses, writes an
`external-stack-receipt.json` with declared vs. recorded hub env, source
SHA256 and process metadata, and asserts the single V2 F-API-034 pass with
the registered evidence record validated against the frozen schema.
`test_scenario_scope_and_discovery` asserts the exact Scenario is present
in the discovery index with the expected features/clients/targets scope.

### `tests/validation/test_sw_api_client_02_c2.py`

Parametrized counterexample battery against the new field and the helper:

- `test_disconnected_profile_rejects_unsafe_declarations` — 11 `replace`
  mutations (invalid enum, `None`, hardware target, mixed targets, browser
  client, mixed clients, happy kind, non-empty writes, setup, cleanup,
  faults) must each raise `ValueError`.
- `test_runtime_guards_also_apply_to_direct_preparation` — asserts both
  `Runner._refusal` and `Runner._prepare_sim_matrix` raise/refuse for
  `(hardware, api)`, `(sim, browser)`, `(sim, uc)` **before** any HTTP read.
- `test_health_precondition_rejects_inexact_observations` — 23 parametrized
  bodies/statuses (non-dict, missing keys, truthy-non-bool `success`,
  `configured`, `connected`; HTTP 503) all raise with the exact `HTTP 200
  health` fragment; a local aiohttp server records exactly one `/api/health`
  call (no retry wait).
- `test_health_transport_failure_is_not_disconnected_evidence` — closed
  server causes `OSError` to propagate; a transport failure is not treated
  as valid disconnected evidence.
- `test_default_preparation_preserves_actual_telnet_wait_and_external_behavior`
  — for the discovery-fetched `contracts.cables` scenario
  (`matrix_connection == "ready"`), confirms the external-hub shortcut
  skips `/api/status/cables` while a managed-stack scenario would wait;
  `runner.hub.starts == 0` proves no restart was issued.
- `test_inherited_scenario_in_real_managed_mixed_lifecycle` — a
  `ReceiptRunner` runs three real scenarios (`contracts.cables`, the C1
  disconnected scenario, `routing.switch_one`) through the actual managed
  simulator + hub, hub generations restarted around the mid-sequence
  disconnected observation, with ≥4 child processes recorded; the C1
  record is schema-validated and asserts 8 passing checks, exact body
  `{"input": 6}`, equal `state_before == state_after`, no routing event,
  no `switch_failed`, no `video switch` command, and
  `hub.env["OREI_VERIFY_SSL"] == "true"`.
- `test_wrong_actual_managed_precondition_blocks_before_action` — two
  parametrized negative controls: (a) `ready` profile with the TLS env
  that enforces disconnection must block with reason containing
  `"Telnet link"`; (b) `disconnected` profile with the empty hub_env
  (connection succeeds) must block with reason containing `"HTTP 200
  health"`. Both are asserted to produce `status == "blocked"`,
  `gate == "regression"`, no `requests[]` observations and no `action (`
  procedure step.

### `docs/validation/features.yaml`

Line `4848` extends `F-API-034.scenarios` to
`[routing.route_all, sw_api_client_02_c1.switch_all_failed]`. No existing
evidence record, finding, claim, area or feature title is modified; the
existing `routing.route_all` entry and `VAL-14` finding reference are
preserved byte-for-byte.

## Live execution — focused modules (not a global campaign)

All invocations use the root venv interpreter, UTF-8, disabled bytecode,
isolated `MATRIX_DATA_DIR`/`UC_CONFIG_HOME`, a fresh child under
`C:/t/exec-qual-anthropic-core-01/nov02-attempt01/`, and PYTHONPATH of this
checkout plus `src`.

Private retained paths are under
`build/software-waves/QUAL-ANTHROPIC-CORE-01/execution-20261101/author/`:

| Attempt | Command | Result | Artifact |
| --- | --- | --- | --- |
| c1c2 | `pytest -p no:cacheprovider -p no:tests.route_inventory tests/validation/test_sw_api_client_02_c1.py tests/validation/test_sw_api_client_02_c2.py --junitxml=...c1c2.junit.xml` | **54 passed in 54.51s**, exit 0 | `c1c2.log`, `c1c2.junit.xml` (SHA256 `6b8403c5f06911b6dadafd550f65f3426c3d1e2715b741abc4f76bd69b64749b`; 54 testcases, 0 failures, 0 errors) |
| regression-sample | `pytest -p no:cacheprovider tests/validation/test_model.py tests/validation/test_registry.py tests/validation/test_runner.py` | **40 passed in 27.86s**, exit 0 | not retained to junit — stdout tail captured in this report |

The C1/C2 run was first executed without the route plugin disabled; it
produced a partial `route-coverage.json` at the repo root with
`covered=4, total=177, strict=false`. That file is `.gitignored`; it was
inspected (content captured here) and removed before the retained re-run so
no partial route proof could be mistaken for a committed global route
inventory. The retained re-run used `-p no:tests.route_inventory`.

The run matches the historical "about 54 tests" baseline of C2 attempt02 in
`docs/production/software-waves/SW-API-CLIENT-02-C2/AUTHOR.md`
(54 passed, exit 0) at the same `caaa4faa` HEAD. No new focused module was
authored. Discovery, registry construction and Runner `__init__` were not
observed to regress under the appended field.

No global CLI validation campaign was launched. The historical `check` gate
failure recorded by the C2 author at `caaa4faa` (`F-SEC-007 dropped below
its recorded level: level V2 < recorded V3`) is **not** retried here —
rubric calibration explicitly forbids an automatic failed-gate retry, and
the FSEC007 regression is a global evidence-level freshness observation,
not a defect introduced by this candidate's changes. It remains a historical
hold the coordinator owns.

## Rubric axis observations

The rubric requires explicit per-axis observations with concrete evidence
at an exact evaluator commit, with holds for unknowns. The independent
OpenAI-family judge assigns pass/hold/fail. This section states what was
inspected and what remains unknown; it does **not** self-assign a pass.

### provenance

- Full diff `938ae303..caaa4faa` enumerated (9 files, 1057 line delta);
  three source commits in boundary order (`3868723`, `ee3f2e7f`, `caaa4faa`)
  byte-equal to the frozen rubric's `review_base_sha`, `source_commits` and
  `candidate_sha`.
- Candidate native: Anthropic `claude-opus-4-7/high` as authorized by
  owner on 2026-11-02; no fallback/helper/substitution.
- Historical DeepSeek authorship of the earlier `SW-API-CLIENT-02-C1`
  record and its own baseline (`411c66429df3b813072e736c41c3a8aa83043a70`,
  branch `ryan-haver/wp-sw-api-offline-events`) is distinguished from the
  current review boundary; the earlier author record is unchanged in this
  task.
- Reviewed worktree SHA matches the Dispatch's declared actual verified
  worktree `2d494566-13c3-4624-b834-7e0bc340801b` and base
  `caaa4faabe9ede1e3aed37d2269efd4a4d691e04`. Working tree was clean before
  work.

### invariants

- **Default compatibility** — `matrix_connection = "ready"` default makes
  every pre-existing Scenario still valid without constructor-call changes
  (`discover()["contracts.cables"].matrix_connection == "ready"` is
  asserted by the C2 default-preparation test). Verified by regression
  sample `test_model.py`/`test_registry.py` pass (40/40).
- **Declaration guard** (`__post_init__`) rejects every unsafe
  declaration tested (11 counterexamples) and the enum guard rejects
  invalid enum values; preserves scope-only guard semantics.
- **Direct runtime guard** (`_refusal` + `_prepare_sim_matrix` repeat
  scope checks) raises/refuses before any HTTP I/O; verified by the
  "no helper HTTP session" test.
- **Strict health envelope** — the `is True`/`is False` checks reject
  truthy non-bool values, non-mapping bodies and HTTP 503; a transport
  failure propagates `OSError` and is not accepted as evidence.
- **Simulator-only API failure scope** — scenario and runner guards jointly
  restrict disconnected to `(sim, api, failure)` with empty mutation sets.
- **Telnet/external/hardware behavior** — ready path still invokes
  `_wait_hub_telnet` with the external-hub early-return
  (`not _runner_started_hub()` → `return`) intact; hardware branch byte-
  identical. The one procedure-string gating differs textually between the
  pre-patch (`self.stack is not None`) and new (`self.stack`) forms; both
  are structurally equivalent for the project's `HubProcess`-backed
  stacks, and the regression sample observes no behavior change.
- **No side effects or evidence/schema weakening** — no change to
  `tools/validate/evidence.py`, schema, record keys or evidence files; the
  new procedure string is bounded descriptive text. Features.yaml append
  adds a scenario reference under an existing feature; no field, finding
  or evidence hash was mutated.

Unknown / out of scope: formal proof that no non-sim-non-api scenario
elsewhere in the repository has `matrix_connection != "ready"` at
construction (there are none in the diff, but the enum/scope guard raises
at construction so any future violation is self-detected). Judge may
reconfirm via a one-shot discovery enumeration.

### counterexamples

- `test_disconnected_profile_rejects_unsafe_declarations` — 11 negative
  declarations (invalid enum, None, hardware target, mixed targets,
  browser/uc clients, happy kind, writes, setup, cleanup, faults) all
  raise.
- `test_runtime_guards_also_apply_to_direct_preparation` — 3 negative
  runtime pairs refuse before HTTP.
- `test_health_precondition_rejects_inexact_observations` — 23 negative
  health observations (non-dict, missing, truthy-non-bool for `success`,
  `configured`, `connected`; 503) all raise with the exact fragment; one
  and only one `/api/health` call recorded per case (no retry).
- `test_health_transport_failure_is_not_disconnected_evidence` — a closed
  server propagates `OSError`, not a false pass.
- Default/external delegation (`contracts.cables`, external hub) verified.
- Real managed mixed lifecycle verifies healthy→disconnected→healthy
  sequencing with hub restarts; wrong-precondition negatives (ready with
  TLS disconnection; disconnected with empty hub_env) block before the
  action with the exact reason fragment.
- The run was observed-execution (not static diff); the historical
  C1/C2 attempts remain labelled historical and the current controls
  are not mislabeled as fresh before-base runtime proof.

### behavior_and_tools

- Only existing managed controls used: disposable local simulator and
  hub; aiohttp local test clients. Isolated per-invocation
  data/config/temp directories; no real hardware, no external deployment,
  no outbound network beyond localhost loopback.
- Retained artifacts: `c1c2.log` and `c1c2.junit.xml` (SHA256
  `6b8403c5f06911b6dadafd550f65f3426c3d1e2715b741abc4f76bd69b64749b`,
  54 testcases, 0 failures, 0 errors). The initial C1/C2 run's
  informational `route-coverage.json` (gitignored) was captured as
  `covered=4/177, strict=false` then removed before the retained re-run.
- Process disposition: pytest exited 0; no lingering helper children
  (fixtures use local servers only). No new source/test/tool deliverable;
  no helper code shipped.

### calibration

- The historical `F-SEC-007` global gate failure recorded at `caaa4faa`
  is retained as a known hold; it was **not** retried, waived, admitted
  or reconstructed. It is a global evidence-level freshness observation
  on an unrelated security scenario (`V3 current` registry entry), not a
  product defect introduced by the disconnected-preparation changes.
- The SW-API-CLIENT-02-C1 "lost original" preservation failure and the
  older DeepSeek-attributed C1 attempt remain immutable; this task did
  not modify them.
- All failures observed in C2's own history (`focused-01` 52/1 fail
  before test setup correction) remain preserved in the earlier author
  record. This evaluation did not reproduce or claim them.
- No V3/parent/image/HIL/soak/field/final release gate is claimed. No
  automatic failed-qualification retry.

### review_quality

- Findings: no new product-defect finding opened; the inspected diff is
  behavior-preserving with strict construction and runtime guards. One
  minor observation (not a defect) is recorded for the judge's attention:
  `_prepare_sim_matrix` uses `if self.stack` (truthy test) where the
  pre-patch SimDevice branch used `if self.stack is not None`; equivalent
  for `HubProcess`-backed values but subtly different for a falsy non-None
  stack object. No such object is produced by `tools/validate/stack.py`;
  no behavior change was observed in the regression sample or the real
  managed-lifecycle test. This is reported as an informational style
  observation (severity: informational), not a defect requiring source
  action.
- All counterexample surface described in the rubric was observed to be
  exercised by existing C2 parametrizations; the actionable surface for
  the judge is to re-verify the scope-only semantics of the
  `_prepare_sim_matrix` non-ready branch against the published
  `__post_init__` guard, and the identity of the shadowed Telnet-wait
  procedure string between pre- and post-patch forms.
- This evaluator's report is submitted at commit SHA recorded below; the
  judge's acceptance tests this report's factual claims against the
  immutable boundary.

## Holds, limits and remaining gates

- **No bounded qualification is self-asserted**; coordinator alone grants
  it after judge disposition.
- **No RV-API034 source acceptance** is claimed by this task.
- The historical `F-SEC-007` global gate failure remains a hold.
- The historical C1 lost-original preservation failure remains immutable.
- Parent/V3 integration, hardware HIL, 72-hour soak, week-long field
  sign-off and final version/artifact release remain gated downstream and
  are not relitigated here.
- No push, no integration, no cleanup, no self-release, no new tracked
  implementation changes.

## Commit and settlement

This report is the only new tracked artifact. It will be committed with
`git -c core.hooksPath= commit` (invocation-only hooksPath empty)
per the dispatch brief for a prose-only report; existing hooks on new
implementation deliverables are not bypassed by this report. No push, no
tag, no merge, no cleanup follows. The coordinator settles the worker,
preserves artifacts and assigns independent OpenAI judgement.

Final values are recorded here immediately before the commit; the exact
report commit SHA is appended in the `worker_done` payload.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
