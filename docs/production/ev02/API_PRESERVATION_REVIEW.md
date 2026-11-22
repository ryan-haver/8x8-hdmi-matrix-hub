# EV-02 original API-evidence preservation audit

Status: **read-only independent reconciliation audit; six-row disposition recorded.
No evidence import, target promotion, or gate closure.** The final input-name
mapped-SHA review remains separate and pending; this audit does not claim it.

## Authority, identity and scope

| Field | Observation |
| --- | --- |
| Reviewer | DeepSeek Pro `deepseek/deepseek-v4-pro` (DeepSeek family; same proven session) |
| Task / Dispatch | `task_c339a58870e0` / `ctx_0f509ee13c00`; existing Run `run_37205f6095b3` |
| Worktree base HEAD | `c384dff856752fc5724834974cb703ba34c7af06` (verified `git rev-parse HEAD`) |
| Original evidence source | `1baac3dec660f41345869c126cfca94d6731c5a0` (not the current candidate) |
| Reviewed implementation | `0a7d71b2` vs `3979d602` (unchanged; prior review) |
| Exclusive writable | `docs/production/ev02/API_PRESERVATION_REVIEW.md`, `build/ev02-api-preservation/**` |

No product, test, runner, registry, root manifest/lock or prior-report files were
changed. No hardware, `--record`, runtime campaign, publishing, merge or cleanup.

## Scope of the audit

Independently verify the six **primary-disposition-1 (preserve)** features from
[EV01_EVIDENCE_RECONCILIATION.md](../../validation/EV01_EVIDENCE_RECONCILIATION.md)
and the portable `docs/validation/runs/ev01-20261020/reconciliation.json`:

F-API-014, F-API-016, F-API-026, F-API-028, F-API-036, F-API-038.

The coordinator copied 144 original source records hash-exact into
`build/ev02-api-preservation/originals-utf8/`, indexed by
`copied-original-utf8-index.json`. The earlier `originals/` directory is an
incomplete 142-file copy (missing `F-MTX-007`/`outputs.audio_mute` and
`F-REL-008`/`outputs.audio_mute_rejected`, the two F-API-036 records) from the
Windows default-encoding error. It was left untouched; `originals-utf8/` is the
only source used here.

## Method

Structural enumeration of the 144 indexed records (not full-JSON dumping);
per-record byte SHA-256 against the index and the reconciliation `record_hash`;
schema validation with the project's own `docs/validation/evidence.schema.json`
(`jsonschema.Draft202012Validator`, as in `tests/validation/test_evidence_schema.py`);
per-client `Scenario.features_for("api")` from the live scenario DSL
(`tools.validate.scenarios.discover`); and source-attribution / environment-digest
inspection. Distinct assertion contracts were read from the records' `checks`
(the generators are `tests/validation/scenarios/{contracts,writes,cec,cec_capabilities,cec_controls,outputs}.py`).
Original-vs-HEAD scenario/cover drift was compared with
`git diff 1baac3de..3979d602`.

## Verification results (explicit counts, all zero)

| Check | Result |
| --- | --- |
| Copied file byte SHA-256 == index `sha256` | 0 / 144 mismatches |
| Index `sha256` == reconciliation `record_hash` (`source-1ba`) | 0 / 144 mismatches |
| Scenario present in live `discover()` | 0 / 144 missing |
| Record `features` field == `Scenario.features_for("api")` | 0 / 144 mismatches |
| Schema-valid (`evidence.schema.json`) | 0 / 144 invalid |
| `commit.sha` == `1baac3de…` | 0 / 144 not-1baac3de |
| `environment.hub.image_digest` non-null | 0 / 144 (all `null`) |
| `level == V2` and `result == pass` | 0 / 144 non-V2/non-pass |

Additional structural facts across all 144 records: `hub.version` 2.10.0,
`simulator.source_sha256` `23f7439ea94f5fcc`, seed `tools/simulator/states/default.json`,
`freshness == fresh`, `mapping_matches == true`, `changed_covers == []`.
No image digest is attached to any of the 144 records, so they are source API
(V2) passes, not image/V3/V4 proof.

**Image overlap:** the five image campaigns in `reconciliation.json`
(`image-campaigns-*.json`, 139+17+18+1+18 = 193 passing image outcomes) all report
`selected_feature_overlap: []` — none of the six features is attributed by any
image outcome. Source API passes must not be re-labelled image/V3 proof.

**Scenario/cover drift 1baac3de → 3979d602:** `git diff --stat 1baac3de..3979d602 -- tests/ tools/ src/`
shows only three `tests/e2e/visual/__snapshots__/…/paused-frame.png` files (the
owner-approved Tron paused-frames). `src/`, `tools/`, `tests/validation/scenarios/`
and `tests/sim/` are byte-identical. Therefore the original records were produced
against the same product source, scenario definitions, and validation tooling as
the current candidate, and every cover path is unchanged. This is the basis for
preserving (not rerunning) these records.

## Six-row per-feature disposition

### F-API-014 — System info and storage routes (2 records, both happy, 5 checks)
- **Valid original scope:** `contracts.system_info` asserts `GET /api/system/info`
  returns `rest_api_version == "2.10.0"`; `contracts.storage` asserts
  `GET /api/system/storage` returns `data_dir_exists`/`config_dir_exists == true`.
  Each also asserts no device write, device unchanged, no protocol warnings, WS schema.
- **Assertion/client limits:** API-only (sim, V2); read-only routes with no device
  effect; no browser/UC/HA or hardware claim.
- **Attribution:** SHA `1baac3de…`, hub 2.10.0, `image_digest` null.
- **Additional proof:** none for the V2 target. Registry `current` level is still
  V1 — the V2 level reflection is coordinator-owned, not this audit.

### F-API-016 — CEC catalogue, capability and enable routes (132 records)
- **Valid original scope:** 4 direct scenarios (`contracts.cec_input_catalog`,
  `contracts.cec_invalid_type`, `contracts.cec_output_catalog`, `writes.cec_output_enable`)
  + 88 `cec_caps.*` + 40 `cec_controls.*_enable_*` (115 happy / 17 failure). Asserts
  literal catalogue tables (`GET /api/cec/commands[/input|output]`), per-port and
  whole-table capability values (`GET /api/cec/{input|output}/{n}/capabilities`),
  and enable effects/refusals (`POST /api/cec/{input|output}/{n}/enable`) with exact
  `set cec index` device commands, raw index-array readback, and unchanged-device.
- **Assertion/client limits:** API-only (sim, V2). Physical CEC effects remain V4;
  the grouped feature spans three route families and is proven at V2 only.
- **Attribution:** SHA `1baac3de…`, hub 2.10.0, `image_digest` null.
- **Additional proof:** none for V2. Note the committed historical set has a
  duplicate `writes.cec_output_enable` (commits `72cc71dc` and `7dbc4dc7`), giving a
  133-committed vs 132-source count; the single fresh `1baac3de` record is the one
  preserved. The extra committed record is a stale historical duplicate, correctly
  excluded.

### F-API-026 — Themes and UI preference routes (5 records, all happy)
- **Valid original scope:** `contracts.themes`, `contracts.ui_preferences`,
  `writes.themes`, `writes.themes_reset`, `writes.ui_preferences` assert GET/PUT/reset
  saved-value readback (`presets`, `activePresetIndex`, `cardOpacity`, tab order) with
  unchanged-device/no-command checks.
- **Assertion/client limits:** API-only (sim, V2); hub-data persistence, not browser
  rendering.
- **Attribution:** SHA `1baac3de…`, hub 2.10.0, `image_digest` null.
- **Additional proof:** none for V2.

### F-API-028 — Flic integration routes (2 records, both happy)
- **Valid original scope:** `contracts.flic_buttons` reads the two fixture buttons;
  `writes.flic_register` renames a button and reads it back via a separate
  `GET /api/integrations/flic/buttons`. No device write in either.
- **Assertion/client limits:** API-only (sim, V2); fixture registration, no physical
  button or SDK claim.
- **Attribution:** SHA `1baac3de…`, hub 2.10.0, `image_digest` null.
- **Additional proof:** none for V2. Note registry `current` level is still V0
  (claimed), so the V2 records are preserved but not yet reflected as the feature's
  level — that reconciliation/import is coordinator-owned and out of scope here.

### F-API-036 — WS event audio_mute (2 records: 1 happy + 1 failure)
- **Valid original scope:** `outputs.audio_mute` asserts `POST /api/output/2/mute` →
  device `audio_mute == 1`, exact `set output audio mute` command, WS event
  `audio_mute {output:2, muted:true}`, hub readback. `outputs.audio_mute_rejected`
  asserts the refused case leaves the device unchanged and emits no WS event.
  Attribution to F-API-036 is via `client_features["api"]` (base feature `F-MTX-007`
  / `F-REL-008`), correctly API-scoped.
- **Assertion/client limits:** API-only (sim, V2); the separate hardware
  audio-mute feature remains capped by HIL-09 (this row does not close it).
- **Attribution:** SHA `1baac3de…`, hub 2.10.0, `image_digest` null.
- **Additional proof:** none for the V2 API scope; physical mute is HIL-09 gated.

### F-API-038 — WS event cec_command (1 record, happy)
- **Valid original scope:** `cec.output_power_on` asserts `POST /api/cec/output/1/power_on`
  → exact `cec command` frame (`object:1, port:[1,0,…], index:0`), WS event
  `cec_command {type:output, port:1, command:power_on}`, device unchanged.
  Attribution via `client_features["api"]` (base `F-CEC-005`, plus `F-API-015`,
  `F-API-038`).
- **Assertion/client limits:** API-only (sim, V2); the TV is not actually powered on.
- **Attribution:** SHA `1baac3de…`, hub 2.10.0, `image_digest` null.
- **Additional proof:** none for V2 (F-API-038). F-API-015 is a separate
  primary-disposition-3 feature (438 scenarios) — preserving this one record for
  F-API-038 does **not** close F-API-015.

## Findings and limitations

No evidence defects or factual overclaims were found. All 144 records are
internally consistent, schema-valid, correctly attributed to `1baac3de`, V2/pass,
with null image digest, and their per-client feature mapping matches the live
`Scenario.features_for("api")` exactly. Four informational notes (none requiring
fix or blocking):

1. The earlier `originals/` copy is incomplete (142 files) and was preserved, not
   touched; `originals-utf8/` (144 files) is authoritative.
2. F-API-016 committed history carries a duplicate `writes.cec_output_enable`
   record (two commits); the fresh source record is the one preserved.
3. F-API-036 and F-API-038 are attributed through `client_features["api"]` — the
   records correctly carry the base feature plus the API-only feature; this is a
   per-client mapping, not an overclaim.
4. `cec.output_power_on` carries F-API-015 as well; F-API-015 is disposition 3 and
   is not closed by this preservation.

Preservation is bounded to the six disposition-1 API features. No rerun, import,
level promotion, or stale-relabelling was performed, and the historical
committed-failure scope is untouched. The final input-name mapped-SHA review and
the author's full normal-hook completion remain separate and pending.
