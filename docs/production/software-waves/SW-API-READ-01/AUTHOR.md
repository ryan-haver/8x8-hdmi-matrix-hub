# SW-API-READ-01 author record

## Authority and boundaries

- Task `task_3853c93e69ef`, Dispatch `ctx_41f75bc23079`, existing Run
  `run_37205f6095b3`; dispatched terminal
  `term_f176e63d-c1df-4f09-9916-11aa9b530699`.
- Exact base: `97e617c2276c7b1e015bb4a9419cb9820deafdee` on integration
  `wp-runtime-completion`; author branch `ryan-haver/wp-sw-api-root`, dedicated
  Orca child worktree `wp-sw-api-root` on local Windows host.
- Origin: `https://github.com/ryan-haver/8x8-hdmi-matrix-hub.git`.
- Requested and observed effective launch: Codex/OpenAI `gpt-6.1-sol`, high.
  `worker-show` confirms the exact Task/Dispatch, base and effective selection;
  this is control-plane provenance, not independent backend attestation.
- Managed Codex pool `fc27561f-3138-4936-b99d-950f3ade4ed0` matches the worker
  home and coordinator pool. Supported `orca account list --json` reports
  weekly 3% used / 97% remaining, 10,080-minute window, reset
  `2026-10-27T06:33:16Z`, observed source update about `16:35:30Z` on October 20.
  No session limit reported; no quota discrepancy or limit response observed.
  Coordinator separately reports 16:35:44Z capacity and reserves DeepSeek Pro
  review from USD 18.78 available with USD 5 bounded review/fix allowance.
- No helpers, subagents, alternate models, Claude/Anthropic, hardware, pushes,
  merges, cleanup, tags or release actions. Project ceiling remains four,
  including coordinator and one older retained process, maximum two new workers.
- Owned source: new `tests/validation/scenarios/sw_api_read_01.py` and this
  report. Artifacts live in `build/software-waves/SW-API-READ-01/` (ignored).
  Registry, ledger, existing scenarios, product code, manifests and lockfiles
  remain coordinator-owned. Allocation updates are supplied through Orca for
  the coordinator's ledger, rather than editing the prohibited shared file.

## Contract and implementation

EV-01's F-API-002 row correctly identifies missing root proof, not an assumed
product defect. `src/rest_api/app.py` registers `/` and `/api` with
`static.handle_api_root`; `/api/info` uses `core.handle_info`.
`docs/API_REFERENCE.md` identifies the two public index routes and API version
2.10.0. Application version (`src/hub/__init__.py`, currently 1.0.0rc1) is a
separate contract from the API version.

Existing direct assertions in `tests/test_rest_api.py::TestHealthEndpoints`
require the API version and websocket/EDID/scenes catalog groups.
`tests/test_openapi_and_config_docs.py` additionally requires both root aliases
to advertise OpenAPI and Swagger endpoints and info to expose the canonical hub
version and API version. Existing simulator reads independently cover served
OpenAPI/Swagger content and absent/corrupt manifest identity fallback.

New `contracts.api_root` and `contracts.api_root_alias` each exercise their
actual route through the API client. They require successful response envelope,
documented API name/version, advertised OpenAPI/Swagger and websocket links,
nonempty EDID/scenes catalogs, matching info API version, unchanged matrix,
zero mutating device commands and no protocol warnings. Only selected stable
public catalog descriptions are pinned; the full inventory is not duplicated.
The existing `contracts.api_info` is reused unchanged for canonical application
version and driver identity, avoiding a duplicate scenario. The extra info read
inside each root scenario is enclosed by the new state/write checks.

All three actual discovered scenarios were inspected using
`Scenario.features_for("api")`: each attributes only F-API-002, allows only API
and sim, and declares no device writes. The new scenarios declare relevant hub,
static/core/security, canonical version/manifest/helper, direct and simulator
tests, scenario inputs, validation tooling, simulator and seed fixture paths
for freshness. No shared DSL change or inventory expansion is needed.

## Verification commands and preserved results

Commands run from the dedicated author worktree using Python 3.12.10 at
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
(abbreviated `PYTHON` below). Artifacts are relative to
`build/software-waves/SW-API-READ-01/`.

1. `PYTHON -m ruff check tests/validation/scenarios/sw_api_read_01.py`: exit 0.
2. `npm ci --ignore-scripts --no-audit --no-fund`: exit 0, 190 packages installed
   locally, log `npm-ci.log`. No package/lock/global configuration changes.
3. `PYTHON -m pytest tests/test_rest_api.py::TestHealthEndpoints
   tests/test_openapi_and_config_docs.py tests/sim/test_sim_rest_reads.py
   -p no:tests.route_inventory -p no:cacheprovider -q -rA
   --basetemp=build/software-waves/SW-API-READ-01/targeted-tmp/cases
   --junitxml=build/software-waves/SW-API-READ-01/targeted.xml`: exit 0,
   **81 passed, zero skips, two deprecation warnings, 16.80 seconds**.
   Complete `targeted.log`, `targeted.xml`, `targeted.exit.txt` retained.
   Isolated MATRIX_DATA_DIR/UC_CONFIG_HOME were set under this build tree;
   per-test fixtures additionally isolate each test's storage. Partial testing
   disables the route-inventory writer, preserving full-suite route reports.
4. Actual feature campaign:
   `PYTHON -m tools.validate run --target sim --client api --feature F-API-002
   --out build/software-waves/SW-API-READ-01/campaign-dirty-01`: exit 0,
   **three pass / zero fail / zero skip / zero abort**, API V2 only.
   This initial diagnostic preceded staging the new scenario. The runner uses
   tracked dirty metadata and reported base SHA with `dirty: false` despite
   the untracked new scenario. **Do not accept it as exact-base or clean-source
   proof.** Its original records and logs are preserved unchanged; a clean
   committed-source campaign is required below. This is an attribution limit,
   not a product defect or permission to modify shared evidence tooling.
5. `scenarios-inspected.json` contains actual discovered actions, expectations,
   per-API features, clients/targets/writes and covers (not registry inference).

Initial shell discovery also found plain PATH has Python but no pytest/ruff
executables; subsequent checks explicitly use the existing project venv.
Several broad `rg` discovery invocations used nonexistent Windows wildcard
paths and were replaced by concrete paths; no tests or setup failed thereby.
No failed campaign was overwritten and no populated evidence destination reused.

## Acceptance still pending at this checkpoint

Mandatory normal implementation hook, clean committed-source campaign, source
SHA and final boundary checks will be appended after completion. The configured
hook is the existing root `.githooks/pre-commit`, running repository Ruff and
complete core tests; it must run with strict route coverage and isolated data.
New scenario links initially require a coordinator-owned registry change:
`test_scenario_links_are_symmetric` otherwise rejects new scenarios. Escalation
`msg_7cabb5fe20c9` requests that exact dependency without modifying the registry.

At 16:43:04Z the coordinator applied, semantically audited and staged exactly
one F-API-002 scenario-list change in `docs/validation/features.yaml`, adding
`contracts.api_root` and `contracts.api_root_alias`. Messages
`msg_e8016ecf7bb8` and `msg_b22c51987e53` explicitly authorize including that
coordinator-authored staged line in this normal implementation commit. The
author inspected its exact diff and did not edit the registry. No other field,
evidence list, level or finding changed. This is an explicit addition to commit
scope, not a transfer of general registry ownership.

Different-family independent review at the submitted SHA remains pending with
the coordinator. This author report establishes neither review acceptance nor
integration, qualification, evidence import or publication. Browser/Remote/HA,
image builds, physical HIL, 72-hour soak, week field and final release gates
remain outside this bounded API V2 proof.
