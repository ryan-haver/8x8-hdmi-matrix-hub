# EV-02 final combined-candidate independent review

Status: **accepted for the API-only V2 scope at the exact candidate SHA.** This is
the independent DeepSeek cross-family review of the final combined EV-02
candidate `e5ebb376230d1dc6bbb62e07f38b7d4cf8221b32` against base
`3979d6020165bcf31f0f44f21de6bb5b3648dc1e`. It records a substantive
source/assertion/evidence/metadata/registry/ledger review at the exact committed
SHA; it does **not** close BE-16, TST-03, any HIL-09 cap, F-API-015 (target V3),
or any image/browser/UC/HA/physical/soak/field/release gate.

## Authority, identity and family evidence

| Field | Observation |
| --- | --- |
| Reviewer | DeepSeek Pro, exact route `deepseek/deepseek-v4-pro` (DeepSeek family) |
| Author | Sol 6.1 `codex:gpt-6.1-sol`, effort high (OpenAI family) |
| Coordinator metadata | OpenAI (family of the author) |
| Cross-family | Satisfied: DeepSeek (reviewer) ≠ OpenAI (author/coordinator) |
| Task / Dispatch | `task_2f3700b530a4` / `ctx_294f9d071a03` (live injected IDs) |
| Reviewed candidate SHA | `e5ebb376230d1dc6bbb62e07f38b7d4cf8221b32` (verified `git rev-parse HEAD`) |
| Assigned base SHA | `3979d6020165bcf31f0f44f21de6bb5b3648dc1e` |
| Reviewed implementation | `0a7d71b2e509b558263bc164a384f157195d96e9` (unchanged since prior review) |
| Worktree | `ryan-haver/wp-ev02-final-review` (clean working tree) |
| Exclusive writable | `docs/production/ev02/FINAL_API_REVIEW.md`, `build/ev02-final-review/**` |

Model/route evidence (not self-report alone): the worktree `opencode.json` pins
`model: deepseek/deepseek-v4-pro` (primary, small, title, summary, compaction and
build agents), denies every provider except `deepseek`, and denies `mcp:*`,
`subagent:*` and the Anthropic plugin. Session metadata reports provider
`deepseek`, model `deepseek-v4-pro`. No helpers, subagents, MCP, or alternate
routes were used; no `--record`, hardware, or paid model probe was run.

## Method

1. Confirmed `git rev-parse HEAD` equals the reviewed SHA and audited
   `git diff 3979d602..HEAD` (`--stat`, `--name-status`, full diffs of the
   source, `.gitattributes` and `features.yaml`).
2. Confirmed the only source-code change is the 40-line `writes.py` addition,
   byte-identical to the independently reviewed `0a7d71b2` commit.
3. Verified all 148 immutable evidence records byte-exact against the manifest
   SHA-256, schema, per-client feature mapping, results, timestamps and null
   image digests using the project's own `tools.validate` and
   `evidence.schema.json`.
4. Ran the four-name source campaign at the exact clean HEAD and inspected the
   actual checks, state diffs, device commands and commit metadata (not CLI exit
   codes alone).
5. Ran scoped Ruff and the registry/evidence-schema/ledger/model/hygiene tests
   (route plugin disabled), and one `ledger.compute` pass compared to the
   canonical committed `LEDGER.md`.

## Git diff audit (no unrelated changes)

`git diff --stat 3979d602..HEAD` = 158 files, 194,367 insertions, 34 deletions.
`git diff --name-status` shows:

- `M tests/validation/scenarios/writes.py` — the only source-code change
  (`40` insertions, `0` deletions in `3979..0a7d71b2`; **empty** in
  `0a7d71b2..HEAD`, i.e. unchanged since independent review).
- `A` 148 immutable evidence records (144 `ev02-original-api` + 4
  `ev02-input-name`), plus `manifest.json` and `input-name-run-summary.json`.
- `M docs/validation/features.yaml` (7 feature IDs only), `M docs/validation/LEDGER.md`,
  `M .gitattributes` (three scoped `-text` rules).
- `A` four prose reports (author/review/preservation/qualification).

No product source, REST handler, shared contract, root manifest, lockfile,
runner, simulator read route, baseline or historical evidence file changed.
`git status --short` is clean at the reviewed SHA.

## Source review — `tests/validation/scenarios/writes.py`

The addition is exactly three `Scenario` objects (one happy, two failure) plus a
shared `_NAMES` covers tuple. Each declares `features=("F-API-018",)`,
`clients=("api",)`, `targets=("sim",)`, `client_features={}`, so
`Scenario.features_for("api") == ("F-API-018",)` for all three (verified against
the live `discover()` for all 148 records). Assertions match the product route
`POST /api/input/{n}/name` (`src/rest_api/core.py:459-505`, registered in
`src/rest_api/app.py:327`) and the device command built in
`src/orei_matrix.py:2505`.

- **`writes.input_name`** (happy, `writes=("names",)`): POST `/api/input/8/name`
  `{"name": "  Media PC  "}` asserts HTTP 200 `success true`/`error null`/`data`
  with trimmed `Media PC` and message; independent simulator `inputs[7].name ==
  "Media PC"`; hub `GET /api/status` `data.input_names.8 == "Media PC"`; exactly
  one `set input name` with payload `{"index": 8, "name": "Media PC",
  "language": 0}`; exactly one `set input name` overall; `DeviceUnchanged(allow=
  ("inputs[7].name",))`; `NoProtocolWarnings()`; plus the runner's WebSocket-schema
  check (8 checks total).
- **`writes.input_name_invalid_port`** (failure): POST `/api/input/9/name` →
  400 `Input must be between 1 and 8`, `data null`; device/hub name unchanged;
  `NoCommand("set input name")`, `NoCommand("*")`, `DeviceUnchanged()`,
  `NoProtocolWarnings()` (8 checks).
- **`writes.input_name_blank`** (failure): POST `/api/input/8/name`
  `{"name": "  "}` → 400 `Name is required`; same no-mutation checks (8 checks).

Covers (`_NAMES`) are over-declared (they inherit `DEVICE_SETTINGS` and add
`src/persistence.py`, neither on the write path) but include every inspected
handler-referenced path — conservative, not under-coverage. The existing
`matrix.input_*` F-MTX-022 refusal scenarios are not duplicated.

## Evidence verification — 148 immutable records

`build/ev02-final-review/verify_evidence.py` (project `tools.validate` +
`evidence.schema.json`) reports, with zero mismatches:

| Check | Result |
| --- | --- |
| Manifest record count == 148 (144 original + 4 mapped) | pass |
| Per-feature totals (014:2, 016:132, 018:4, 026:5, 028:2, 036:2, 038:1) | pass |
| Working-tree byte SHA-256 == manifest `sha256` | 0 / 148 |
| `evidence.schema.json` valid | 0 / 148 invalid |
| `features` == manifest `features` == live `Scenario.features_for("api")` | 0 / 148 |
| `level == V2`, `result == pass`, `gate == ok`, `target == sim`, `client == api` | 0 / 148 |
| `environment.hub.image_digest == null`, `api_version == 2.10.0` | 0 / 148 |
| `commit.sha == preserved source` (144×`1baac3de`, 4×`bb4d3fdc`), `dirty == false` | 0 / 148 |
| `timestamp.started < finished` present | 0 / 148 |

The 144 originals retain source `1baac3dec660f41345869c126cfca94d6731c5a0`,
original timestamps and null image digests; the 4 mapped records retain source
`bb4d3fdc972e7f556f29c6ed468accd4ff3b88b5`. No record is relabelled to this
newer candidate, V3, or image. The manifest tail carries `record_bytes_unchanged:
true`, `original_records: 144`, `clean_mapped_candidate_records: 4` and the
`shared_feature_hold` note.

## Registry audit — `docs/validation/features.yaml`

The diff touches exactly seven IDs and nothing else; five `current` values are
raised to V2, one `scenarios` list is extended, and no `target`, `interface` or
`findings` field changes:

| Feature | `current` change | Evidence added | Scenarios |
| --- | --- | --- | --- |
| F-API-014 | V1 → V2 | +2 originals | unchanged |
| F-API-016 | V1 → V2 | +132 originals | unchanged |
| F-API-018 | V0 → V2 | +4 mapped | +`writes.input_name`, `writes.input_name_invalid_port`, `writes.input_name_blank` |
| F-API-026 | V1 → V2 | +5 originals | unchanged |
| F-API-028 | V0 → V2 | +2 originals | unchanged |
| F-API-036 | V2 (unchanged) | +2 originals | unchanged |
| F-API-038 | V2 (unchanged) | +1 original | unchanged |

`F-API-015` remains `target V3`, `current V1` (unqualified) — the shared
`cec.output_power_on` record is partial grouped-route proof and does not close
it. `BE-16` (F-API-018), `TST-03` (F-API-028) and all HIL-09 caps are retained.
No feature is promoted above V2 or to image/V3/V4.

## Fresh campaign at the exact candidate SHA

`python -m tools.validate run --target sim --client api --feature F-API-018
--out build/ev02-final-review/campaign --operator automation` → exit 0.

`run-summary.json`: `commit.sha == e5ebb376…`, `dirty == false`, `dirty_files ==
[]`, `aborted == null`; 4 outcomes all `pass`/`V2`/`F-API-018`, `gate: ok`,
`failed_checks: []`. Inspected records total **31 checks**:

| Scenario | Checks | Key evidence |
| --- | --- | --- |
| `writes.output_name` | 7 | 200, trimmed `Living Room`, one `set output name` `{index:8, name:"Living Room", language:0}`, `state_diff=[outputs[7].name]` |
| `writes.input_name` | 8 | 200, trimmed `Media PC`, one `set input name` `{index:8, name:"Media PC", language:0}`, `state_diff=[inputs[7].name "Before source"→"Media PC"]`, simulator + hub readback |
| `writes.input_name_invalid_port` | 8 | 400 `Input must be between 1 and 8`, `state_diff=[]`, zero write commands |
| `writes.input_name_blank` | 8 | 400 `Name is required`, `state_diff=[]`, zero write commands |

The refusals prove no mutating device command and an entirely unchanged device
(`state_diff: []`), and the happy path proves the exact command payload and its
single occurrence, independent simulator readback, and hub readback — matching
the committed `bb4d3fdc` records and the prior review.

## Executed validation (actual exits and counts)

Python 3.12.10, Ruff 0.17.1, pytest 9.1.1, jsonschema 4.26.0; hub version
2.10.0 (matches `API_VERSION`), app `hub.__version__` 1.0.0rc1.

| Command | Exit | Result |
| --- | --- | --- |
| `python -m ruff check tests/validation/scenarios/writes.py` | 0 | all passed |
| `python -m pytest -q -p no:tests.route_inventory tests/validation/test_registry.py tests/validation/test_evidence_schema.py tests/validation/test_ledger.py tests/validation/test_model.py tests/test_repo_hygiene_and_docker.py` (output/cache/temp under `build/ev02-final-review`) | 0 | 122 passed, 2 deselected (`docker` marker) |
| `python -m tools.validate run --target sim --client api --feature F-API-018 --out build/ev02-final-review/campaign --operator automation` | 0 | 4 pass, 31 checks, no failed/skipped, `aborted: null` |
| `python build/ev02-final-review/compare_ledger.py` (one `ledger.compute` pass) | 0 | semantic rows identical to canonical |
| `python -m tools.validate check --run-summary build/ev02-final-review/campaign/run-summary.json` | 0 | `gate OK (0 known failure(s) linked to open findings)` |

The full unchanged 4,041-test core suite was not repeated (the source/test bytes
are unchanged since `d8e4e1ef`, where the normal hook recorded 4,041 pass /
4 skip / 35 deselect and 177/177 route coverage).

## Ledger recomputation and gate

One independent `ledger.compute` pass at HEAD `e5ebb376` over the committed
evidence produces **268 features, 205 below target, 57 stale, 106 fresh-passing**
— identical in every semantic row to the canonical `docs/validation/LEDGER.md`
(generated at `3539b190`); only the generator `Commit <sha>` header line differs.
Zero `⚠` dropped markers (no feature below its recorded level) and zero
fresh-failing scenarios, so the gate's regression checks are empty. Combined with
the fresh four-scenario summary (`aborted: null`, all `gate: ok`), the formal
evidence gate passes with zero failures. The canonical
`python -m tools.validate check --run-summary build/ev02-final-review/campaign/run-summary.json`
exits 0 with `gate OK (0 known failure(s) linked to open findings)`.

## Whitespace / CRLF preservation

The scoped `.gitattributes` rules (`ev02-original-api/**`, `ev02-input-name/**`,
`ev02-api-evidence/**` are `-text`) correctly disable normalization.
`git ls-files --eol` shows the originals `i/lf w/lf` and the mapped records +
manifest/run-summary `i/crlf w/crlf`, both `attr/-text`, matching their source
platforms. Working-tree byte SHA-256 == manifest SHA-256 (0 mismatches) confirms
no normalization occurred. `git diff --check` (working tree) exits 0; the default
`git diff --check 3979..HEAD` flags 15,692 CRLF lines as trailing whitespace
(expected for immutable CRLF bytes), while the invocation-only CRLF-aware check
`git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol
diff --check 3979..HEAD` exits 0 with zero flags, retaining the other default
whitespace checks. No persistent Git configuration was changed.

## Per-feature proposed V2 dispositions

All seven are accepted at **API simulator V2 only** (source API, `image_digest`
null, no cross-client claim):

- **F-API-014** — system info/storage read assertions (2 records). V2.
- **F-API-016** — CEC catalogues, capabilities, enable effects/refusals (132). V2.
- **F-API-018** — input/output rename + input invalid-port/blank-name refusal (4). V2.
- **F-API-026** — themes/reset/preferences saved readback (5). V2.
- **F-API-028** — fixture Flic read/registration readback (2). V2.
- **F-API-036** — audio-mute event + rejected-write no-event (2). V2.
- **F-API-038** — CEC command event/frame contract (1). V2.

**Not promoted:** F-API-015 (target V3, still unqualified); BE-16, TST-03 and
all HIL-09 caps remain open; the 205 below-target and 57 stale rows in the
numerical ledger are pre-existing release gaps, not introduced by this candidate.

## Invariants and counterexamples

Verified invariants: rename returns trimmed name; exactly one mutating device
command; refused writes emit no device command and leave device/hub state
unchanged; no unrelated device-state leaf changes; no simulator protocol
warnings; every WebSocket message conforms to the schema. Meaningful
counterexamples exercised: out-of-range port (`/api/input/9/name` → 400) and
blank name (`"  "` → 400). Not exercised (bounded scope, unchanged from prior
review): non-integer port (`"Invalid input number"`), non-string name, and
`>32`-char name refusals remain with the existing F-MTX-022 matrix scenarios.

## Findings

No blocking findings. The three informational observations from the prior
cross-family review remain valid and non-blocking: (1) the redundant seed in the
two failure scenarios is harmless and explicit; (2) `_NAMES` over-declares two
non-write-path covers (conservative staleness, not under-coverage); (3) refusal
coverage is not exhaustive (bounded scope, device-level matrix stays with
F-MTX-022). No product, test, scenario, registry, evidence or runtime byte was
changed by this review.

## Final verdict

**Accepted** for the API-only V2 scope at the exact candidate SHA
`e5ebb376230d1dc6bbb62e07f38b7d4cf8221b32`. The source change is byte-identical
to the independently reviewed `0a7d71b2`; all 148 evidence records are
byte-exact, schema-valid and correctly mapped; the registry edit is limited to
the seven scoped features; the fresh campaign at the exact SHA passes all 31
checks; and the independent ledger recomputation matches the canonical ledger
with a passing gate. Coordinator publication/integration and the qualified/
published state remain separate; no release, image, hardware, cross-client or
physical gate is closed by this review.
