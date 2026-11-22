# SW-API-READ-01 independent review

## Verdict

**Accepted** — exact scope F-API-002, API V2 simulator evidence only. No
blocking, high, medium or low findings. The two new root-alias scenarios, the
single coordinator F-API-002 registry change, the three byte-exact evidence
records and the coordinator evidence/registry/ledger assembly are all
internally consistent and reproduce at the exact candidate SHA.

## Reviewer identity and family evidence

- Effective provider/model: **deepseek/deepseek-v4-pro** (DeepSeek V4 Pro),
  native default route, no `--model`/effort override, no fallback, helper,
  subagent, MCP server or non-project plugin used.
- Observed via the OpenCode model catalog
  (`tools.opencode.models({provider:"deepseek"})`): `deepseek/deepseek-v4-pro`
  is `active` with variants `none/low/high/max`; the only other DeepSeek model
  is `deepseek/deepseek-flash`. The session harness reports this worker as
  DeepSeek V4 Pro (provider `deepseek`, model `deepseek-v4-pro`).
- Family: **DeepSeek**, distinct from the OpenAI GPT family of the Sol author
  (`gpt-6.1-sol`) and the OpenAI coordinator. This satisfies the
  different-underlying-family review gate.
- Quota: coordinator pre-authenticated USD 16.56 available at 17:13:03Z with
  Pro/Flash unchanged; this bounded review reserved USD 3 for review/corrections.
  `orca account list --json` shows no DeepSeek rate-limit section (DeepSeek is
  credit-billed); Codex pool (Sol's home) weekly 6% used. No limit response was
  observed during this review. No resets, rate-limit or shared-commitment
  surface was touched.

## Reviewed artifacts

| Role | Full SHA |
| --- | --- |
| Combined candidate (reviewed) | `3622dc9a82893981feddc2e84ae7784eca3cdede` |
| Original base | `97e617c2276c7b1e015bb4a9419cb9820deafdee` |
| Implementation | `afe344a0e6a17392ccda90bab140284dd512267e` |
| Submitted author tip | `0dd2c25ea866fd56fbe6046e03f0172499b70080` |

Worktree `ryan-haver/wp-sw-api-review` was already fast-forwarded clean to
`3622dc9a…`; `git status` clean at review start and end. The full candidate
diff from `97e617c2` is 11 in-scope files (no product code, existing tests,
registry schema, root manifests or lockfiles changed):

- `tests/validation/scenarios/sw_api_read_01.py` (new, 76 lines)
- `docs/validation/features.yaml` (F-API-002 only)
- `docs/validation/LEDGER.md` (regenerated)
- three `docs/validation/evidence/software-waves/SW-API-READ-01/F-API-002/*.json`
  (new, byte-exact)
- `docs/validation/runs/software-waves/SW-API-READ-01/{manifest,run-summary}.json`
  (new)
- `docs/production/software-waves/SW-API-READ-01/{AUTHOR,COORDINATOR_PREPARATION}.md`
  (new)
- `.gitattributes` (two scoped `-text` lines)

## Source review

The new scenario (`tests/validation/scenarios/sw_api_read_01.py`) declares two
scenarios, `contracts.api_root` (`GET /`) and `contracts.api_root_alias`
(`GET /api`), each `features=("F-API-002",)`, `clients=("api",)`,
`targets=("sim",)`, no `writes`, no `client_features`. Verified against the DSL
(`tools/validate/model.py`):

- `Scenario.features_for("api")` returns `("F-API-002",)` only; `all_features`
  is `{F-API-002}` (the existing `contracts.api_info` also attributes
  F-API-002). The scenario-id/feature/shape invariants in
  `Scenario.__post_init__` all hold.
- `Response(status=200, json=…)` is a subset match pinning `data.name`, the
  documented API `version` `"2.10.0"`, and the `status` OpenAPI/Swagger plus
  `websocket` endpoint descriptions. It is **not** tautological: it asserts the
  served `data.version` equals the pinned `_API_VERSION` `"2.10.0"`
  (`src/rest_api/utils.py:86`, `src/rest_api/static.py:104-107`), independent of
  the handler under test (the value is re-pinned in the scenario, not imported).
- `Hub(path, "data.endpoints.edid_control", not_equals={})` and the `scenes`
  counterpart are meaningful non-empty catalog assertions: `resolve()` in
  `model.py` raises `KeyError` for a missing `data.endpoints.edid_control` path,
  and `not_equals={}` fails for an empty map, so a missing key or empty catalog
  fails the check rather than passing vacuously. The records show the actual
  populated `edid_control` / `scenes` maps.
- `Hub("/api/info", "data.api_version", equals="2.10.0")` cross-checks the API
  version through the info route; the canonical application version
  (`1.0.0rc1`, `src/hub/__init__.py:9`) and driver identity remain the job of
  the reused `contracts.api_info` scenario (`tests/validation/scenarios/api_documentation.py`),
  so API version and application version are kept distinct and not mislabeled.
- `DeviceUnchanged()`, `NoCommand("*")` and `NoProtocolWarnings()` are meaningful
  for a read-only route: records show `state_diff: []`, `device_log` containing
  only the recognised `get status` read, `write commands seen: []`, and no
  protocol warnings. An 8th automatic WebSocket-schema check is added per
  scenario.
- `covers` (via `_COVERS`) includes `HUB_CORE`, `src/rest_api/{static,core,security}.py`,
  `src/hub/__init__.py`, `driver.json`, `scripts/bump_version.py`,
  `docs/API_REFERENCE.md`, the three existing read test modules, the scenario
  module itself, `tools/validate`, `tools/simulator` and `tests/e2e/fixtures/data`
  — sufficient for staleness freshness of these routes.

The new scenario source is byte-identical between the full-hook implementation
commit `afe344a0` and the candidate `3622dc9a` (empty `git diff` on that file).

## Coordinator assembly review

- **Registry.** Semantic comparison of `docs/validation/features.yaml` at
  `97e617c2` vs `3622dc9a` (268 features both sides, identical id sets): only
  `F-API-002` changed, and only in `scenarios` (`[contracts.api_info]` →
  `[contracts.api_info, contracts.api_root, contracts.api_root_alias]`),
  `current` (`V1` → `V2`), `basis` and `evidence` (`[]` → three paths).
  `target` (`V2`), `interfaces`, `findings` (`[DEP-06]`) and every other feature
  are unchanged. Between `afe344a0` and `3622dc9a` the only feature change is
  `current`/`basis`/`evidence`; the `scenarios` mapping is untouched.
- **Evidence records.** The three committed records' file SHA-256 exactly match
  the `manifest.json` entries and the author's retained
  `campaign-final-01/evidence` bytes (read-only, user-owned):
  `api_info` `d3b99730…`, `api_root` `5dba87ae…`,
  `api_root_alias` `90d3f83e…`. `git hash-object` equals `git rev-parse HEAD:`
  for each (`BLOB-MATCH`) and `check-attr text` reports `text: unset`, so the
  scoped `.gitattributes` `-text` rules preserve the original bytes with no
  CRLF/LF normalization. Records carry `source_sha 0dd2c25e`, `dirty: false`,
  `dirty_files: []`, `client: api`, `level: V2`, `target: sim`,
  `image_digest: null`, `operator: automation`. Schema validity is covered by
  `test_committed_evidence_is_schema_valid` (below).
- **`.gitattributes`.** Adds only
  `docs/validation/evidence/software-waves/** -text` and
  `docs/validation/runs/software-waves/** -text` — the exact new path
  boundaries, no broader `-text` expansion.
- **Ledger.** Committed `LEDGER.md` reflects F-API-002 `V2 fresh` with three
  evidence links and summary `204 below target / 57 stale` (was 205/57). This
  matches the expected "204 below, 57 stale" and was **not** regenerated during
  review (canonical ledger already generated serially by the coordinator).

## Verification commands and results

All commands run from the review worktree at `3622dc9a` using Python 3.12.10 at
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
(abbreviated `PYTHON`), with an isolated short build parent `build/swapi-review/`
created before any `--basetemp`, `MATRIX_DATA_DIR`/`UC_CONFIG_HOME` pointed at
`build/swapi-review/{data,config}`, and `PYTHONUTF8=1`.

1. `PYTHON -m pytest tests/test_rest_api.py::TestHealthEndpoints
   tests/test_openapi_and_config_docs.py tests/sim/test_sim_rest_reads.py
   -p no:tests.route_inventory -p no:cacheprovider -q -rA
   --basetemp=build/swapi-review/temp/cases
   --junitxml=build/swapi-review/targeted.xml` → **81 passed, 2 warnings,
   exit 0** (11.40 s). Log/JUnit at `build/swapi-review/targeted.{log,xml}`.
2. `PYTHON -m pytest tests/validation/test_registry.py
   tests/validation/test_evidence_schema.py -p no:tests.route_inventory
   -p no:cacheprovider -q -rA --basetemp=build/swapi-review/temp/cases
   --junitxml=build/swapi-review/registry.xml` → **33 passed, exit 0**
   (16.99 s). Includes `test_registry_is_valid`,
   `test_scenario_links_are_symmetric`, `test_every_rest_route_is_in_the_registry`
   and `test_committed_evidence_is_schema_valid` (validates all three new
   records against `docs/validation/evidence.schema.json`).
3. Clean feature campaign at the exact candidate:
   `PYTHON -m tools.validate run --target sim --client api --feature F-API-002
   --out build/swapi-review/campaign-01` → **3 pass / 0 fail / 0 skip /
   0 abort, exit 0**. Fresh `run-summary.json` reports `commit.sha
   3622dc9a…`, `dirty: false`, `dirty_files: []`, API/sim/V2, null image digest.
   Raw record inspection confirms for each: populated before/after state,
   `state_diff: []`, only the recognised `get status` read in `device_log`,
   no mutating command or protocol warning, request paths `/api/info`, `/`,
   `/api`; the root records' captured hub reads include the non-empty
   `edid_control`/`scenes` catalogs and the `/api/info` API-version cross-check.
4. Formal gate after the scenario:
   `PYTHON -m tools.validate check --run-summary
   build/swapi-review/campaign-01/run-summary.json --expect-clients api` →
   **`[validate] gate OK (0 known failure(s) …)`, exit 0** (191.9 s). The
   anticipated "two historical capped V3 drops" did **not** materialize: the
   gate reported zero drops. No `--record`, no hardware, no ledger generation.

## Limits (not defects)

- Proof is **API V2 only** (`sim` + `api`). No browser/Remote/HA client, image
  build, physical HIL, 72-hour soak, week field sign-off or V3/V4/V5
  qualification is established or implied by this pass.
- The records' `environment.hub.version` is `"2.10.0"` because the runner reads
  `/api/health`'s `version` field (the API version), not the canonical
  application version `1.0.0rc1`; the candidate correctly distinguishes the two
  via `contracts.api_info` (`/api/info` `data.version`). This is a pre-existing
  runner characteristic, not a mislabel introduced here.
- No new committed test/tooling/fixture was authored by this reviewer; the
  source commit is unamended and this report is prose only.
