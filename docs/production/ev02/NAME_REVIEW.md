# EV-02 input-name evidence independent cross-family review

Status: **preliminary code verdict; final combined gate still held.** This is the
independent DeepSeek review of the author's input-name scenario package for
F-API-018. It records a source/assertion/behavior review at the exact author
commit; it does **not** close the package gate or promote F-API-018, because the
coordinator's registry mapping and the final combined SHA are still pending.

## Authority, identity and scope

| Field | Observation |
| --- | --- |
| Reviewer | DeepSeek Pro, exact route `deepseek/deepseek-v4-pro` (DeepSeek family) |
| Author | Sol 6.1 `codex:gpt-6.1-sol`, effort high (OpenAI family) |
| Cross-family | Satisfied: DeepSeek (reviewer) ≠ OpenAI (author) |
| Task / Dispatch | `task_515977753dd0` / `ctx_15fe6f7a06be`; existing Run `run_37205f6095b3` |
| Reviewed code SHA | `0a7d71b2e509b558263bc164a384f157195d96e9` |
| Assigned base SHA | `3979d6020165bcf31f0f44f21de6bb5b3648dc1e` |
| Worktree | `ryan-haver/wp-ev02-name-review` (coordinator fast-forwarded to the code SHA) |
| Exclusive writable | `docs/production/ev02/NAME_REVIEW.md`, `build/ev02-name-review/**` |

### Model/route evidence (not self-report alone)

- Worktree-local `opencode.json` pins `model: deepseek/deepseek-v4-pro` (primary,
  title, summary, compaction and build agents), and policy denies every provider
  except `deepseek`, denies `mcp:*`, denies `subagent:*` and the Anthropic plugin.
- `opencode models --standalone` exposes exactly `deepseek/deepseek-flash` and
  `deepseek/deepseek-v4-pro`.
- `opencode debug agents` shows the primary `build` agent model
  `{id: deepseek-v4-pro, providerID: deepseek}`.
- Session metadata reports provider `deepseek`, model `deepseek-v4-pro`.
- Coordinator independently exported this session
  (`ses_ea88fe6a2ffe2yi6G6o2RDRYR4`): `info/model` and assistant messages confirm
  `providerID deepseek`, `id deepseek-v4-pro`, variant `default`; cost observed
  ≈ USD 0.13, within the reserved USD 5.
- No helpers, subagents, MCP, or alternate/opaque routes were used. No
  `--record`, hardware, or network model probe was run.

## Method

1. Confirmed `git rev-parse HEAD` equals the reviewed SHA and inspected
   `git diff 3979d602..0a7d71b2` (`--stat`, `--name-status`, full file diff).
2. Read the author's `docs/production/ev02/NAME_AUTHOR.md`, the EV-01
   F-API-018 disposition, the scenario DSL (`tools/validate/model.py`), the
   scenario paths (`tests/validation/scenarios/_paths.py`), the simulator seed
   state, and the product route/command source.
3. Ran the three assigned commands exactly, then inspected the actual evidence
   records (outcomes, checks, state diffs, device log, WS events) rather than
   relying on the CLI exit codes alone.

## Git diff audit (no unrelated changes)

`git diff --name-status 3979d602..0a7d71b2` shows exactly two files:

- `A docs/production/ev02/NAME_AUTHOR.md` (150 insertions, prose report only)
- `M tests/validation/scenarios/writes.py` (40 insertions)

No product source, registry/ledger, manifest/lockfile, runner/contract, baseline
or historical evidence file changed. `git diff --check` exits 0 (no whitespace
errors). `git status --short` is clean at the reviewed SHA. The scenario module
adds a shared `_NAMES` covers tuple (lines 28-29), one happy `Scenario`
(`writes.input_name`, lines 79-99) and a two-element loop appending two failure
scenarios (lines 187-202). The existing `writes.output_name` and all other
scenarios are unchanged.

## Source review — behavior matches the asserted product code

The product route `POST /api/input/{input}/name` is registered in
`src/rest_api/app.py:327` and handled by `handle_set_input_name`
(`src/rest_api/core.py:459-505`):

- `core.py:469-473` rejects an out-of-range or non-integer port with
  `400 "Input must be between 1 and 8"` (out-of-range) or
  `400 "Invalid input number"` (ValueError/KeyError).
- `core.py:478-484` rejects a non-string name (`"'name' must be a string"`),
  strips whitespace (`name = name.strip()`), rejects a blank result
  (`400 "Name is required"`), and rejects >32 chars.
- `core.py:488` sends `matrix_device.set_input_name(input_num, name)` and
  `core.py:499-501` returns `{"input", "name", "message": "Input N renamed to 'name'"}`.
- `src/orei_matrix.py:2505` builds the exact device command
  `{"comhead": "set input name", "language": 0, "name": name, "index": input_num}`.

Each scenario's assertions are therefore source-correct:

- **`writes.input_name`** posts `{"name": "  Media PC  "}` and asserts the
  trimmed `"Media PC"` in the response (`core.py:480` trim), in the simulator
  device (`inputs[7].name`), in the hub readback (`GET /api/status` →
  `data.input_names.8`), and in the exact command payload
  `{"index": 8, "name": "Media PC", "language": 0}` (subset-match against the
  `comhead` command, per `CommandSent` "payload contains"). It also asserts
  exactly one `set input name` command total (catching any extra rename with a
  different port/name) and `DeviceUnchanged(allow=("inputs[7].name",))`.
- **`writes.input_name_invalid_port`** posts `/api/input/9/name` and asserts
  `400 "Input must be between 1 and 8"`, device name unchanged, hub name
  unchanged, `NoCommand("set input name")`, `NoCommand("*")`, `DeviceUnchanged()`.
- **`writes.input_name_blank`** posts `{"name": "  "}` and asserts
  `400 "Name is required"` with the same no-mutation checks.

## Executed commands and results

Python 3.12.10, Ruff 0.17.1, pytest 9.1.1; hub version 2.10.0 (matches
`API_VERSION`), app `hub.__version__` 1.0.0rc1. No installs or global changes.

| Command | Exit | Result |
| --- | --- | --- |
| `python -m ruff check tests/validation/scenarios/writes.py` | 0 | All checks passed |
| `python -m pytest -q -p no:tests.route_inventory tests/sim/test_sim_rest_writes.py tests/validation/test_model.py` | 0 | 59 passed, 5.14 s |
| `python -m tools.validate run --target sim --client api --scenario writes.input_name --scenario writes.input_name_invalid_port --scenario writes.input_name_blank --out build/ev02-name-review/campaign --operator automation` | 0 | 3 pass, all V2 |
| `git diff --check 3979d602..HEAD` | 0 | no whitespace errors |

## Evidence inspection (not CLI-zero alone)

`build/ev02-name-review/campaign/run-summary.json` records
`commit.sha = 0a7d71b2…`, `dirty = false`, three `pass`/`V2`/`F-API-018`
outcomes with `gate: ok` and no `failed_checks`. Each record was inspected:

- **`writes.input_name`** (happy): 8 checks pass. The response body is
  `{"success": true, "data": {"input": 8, "name": "Media PC", "message": "Input 8 renamed to 'Media PC'", "error": null}}`.
  `state_diff` contains exactly one entry — `inputs[7].name` `"Before source" →
  "Media PC"`. `device_log` shows one mutating `set input name` with payload
  `{"comhead": "set input name", "language": 0, "name": "Media PC", "index": 8}`
  (plus read-only `get video status`/`get input status`). A WS
  `input_name_change {input: 8, name: "Media PC"}` event is emitted and passes
  the `websocket.schema.json` check (6 messages). Cleanup restores input 8 to
  `Input 8` via the API outside the measured window.
- **`writes.input_name_invalid_port`**: 8 checks pass. HTTP 400 with
  `error: "Input must be between 1 and 8"`, `data: null`. `state_diff` is `[]`
  and `device_log` shows only read commands — no `set input name` write.
- **`writes.input_name_blank`**: 8 checks pass. HTTP 400 with
  `error: "Name is required"`, `data: null`. `state_diff` is `[]` and
  `device_log` shows only read commands — no write.

## Scenario-shape checks

- `Scenario.features_for("api")` returns `("F-API-018",)` for all three;
  `clients=("api",)`, `targets=("sim",)`, `client_features` empty. No browser/UC/
  HA/physical claim; `level_for("sim","api")` is V2, so nothing is over-promoted.
- The happy scenario declares `writes=("names",)` (a valid device-state domain);
  the failure scenarios declare `writes=()` — correct, since refused writes do
  not mutate.
- `test_model.py::test_every_scenario_is_well_formed` (which discovers and
  validates all scenarios) passes, as do the module's construction-time
  `__post_init__` checks (id/feature regex, non-empty covers).
- Covers (`_NAMES`) include all paths the route actually depends on —
  `src/rest_api/core.py`, `src/rest_api/utils.py`, `src/rest_api/app.py`,
  `src/orei_matrix.py`, `src/_file_io.py`, `src/hub/core`, and the WebSocket
  schema — so staleness tracking is complete for the rename path.

## Findings

No blocking findings. The scenarios are well-formed, source-correct, and their
behavior is independently confirmed by the evidence records. Three informational
observations follow (none require a product/scenario fix):

1. **Informational — redundant seed in the failure scenarios.**
   `writes.py:194` seeds `sim_state={"inputs": {"7": {"name": "Input 8"}}}` for
   both failure cases, but `tools/simulator/states/default.json` already names
   input 8 `"Input 8"`. The seed is harmless and makes intent explicit, and the
   refusal assertions (`NoCommand("*")`, `DeviceUnchanged()`, unchanged hub/device
   name) remain meaningful regardless.
2. **Informational — over-declared covers.**
   `_NAMES` (`writes.py:28-29`) inherits `DEVICE_SETTINGS`
   (`src/rest_api/device_settings.py`) and adds `src/persistence.py`, neither of
   which is in the `handle_set_input_name` write path. This is conservative
   over-coverage (evidence goes stale if those files change), not under-coverage;
   every required path is present.
3. **Limitation — refusal coverage is not exhaustive.**
   `core.py:472-473, 478-479, 483-484` additionally refuse non-integer ports
   (`"Invalid input number"`), non-string names (`"'name' must be a string"`),
   and >32-char names (`"Name cannot exceed 32 characters"`). These paths are not
   asserted by the new scenarios. This is acceptable bounded scope (the package
   targets "an actual input rename/readback case plus meaningful refusals" from
   the EV-01 disposition); the device-level refusal matrix stays with the
   existing `matrix.input_*` F-MTX-022 scenarios.

## Preliminary verdict and required follow-up

**Preliminary code verdict: accepted** for the three-scenario F-API-018 API V2
effects/refusals scope at `0a7d71b2`. The additions correctly attribute a real
input rename (with trimming), independent device readback, hub readback, the
exact device command and its single occurrence, plus two meaningful refusals
(invalid port, blank name) with proven no-mutation, and they make no
cross-client or physical-device claim.

**Final gate is still held.** Required follow-up, coordinator-owned, before the
combined package can be accepted:

1. Integrate the coordinator's `docs/validation/features.yaml` mapping
   (`scenarios: [writes.output_name, writes.input_name, writes.input_name_invalid_port,
   writes.input_name_blank]` for F-API-018), retaining the existing BE-16 finding
   and current/target levels.
2. Re-run the registry symmetry check (`tests/validation/test_registry.py::
   test_scenario_links_are_symmetric`) after the mapping, plus the applicable
   route-inventory / serial ledger generation.
3. Re-review the **final combined SHA** (author's full normal-hook completion is
   still in progress); this review is of the author's preliminary commit only.
4. Any future feature-level promotion or evidence import remains a separate,
   gated decision — no V2 → higher promotion is claimed here.

The three informational findings above are recorded for completeness and do not
block acceptance; the author is not required to change product or scenario files.
