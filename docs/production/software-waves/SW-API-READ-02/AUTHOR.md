# SW-API-READ-02 — bounded READONLY preservation audit (author report)

Status: **read-only source/evidence reconciliation for F-API-014, F-API-016,
F-API-026, F-API-028 only.** Default disposition is **PRESERVE** on the accepted
original API V2 source proof. No code, scenario, test, fixture, registry,
ledger, evidence, baseline or metadata byte was created or changed. No test or
scenario run was executed — this is a static audit, **not** a reproduced result.

## Authority, identity, model and capacity

| Field | Observation |
| --- | --- |
| Task / Dispatch | `task_a75ae30df852` / `ctx_de4764241ae7` (injected IDs) |
| Worktree / base | `wp-sw-api-preservation`, `git rev-parse HEAD` = `51275723846e4b126ccdc48c71d1727cabca4dbc` |
| Original evidence source | `1baac3dec660f41345869c126cfca94d6731c5a0` |
| Reviewer model | MiniMax-M3, provider `minimax-coding-plan` |
| Effective model check | Worktree `opencode.json` pins `model` and `small_model` = `minimax-coding-plan/MiniMax-M3`, and `build`/`title`/`summary`/`compaction` agents to the same; runtime effective model is MiniMax-M3. **No mismatch.** No model override was passed; this is the verified local configured route, not a silent global default. `opencode` v2.1.1. Local `--standalone` catalog lists only `MiniMax-M3` and `MiniMax-M3.1-Flash`; M3.1 was **not** authorized and **not** used. |
| Provider policy | Worktree `opencode.json` denies `provider.use *` except `minimax-coding-plan`, denies `integration.use mcp:*`, the three unqualified plugins, and `tool.use subagent:*`; `opencode.provider.anthropic` disabled. No MCP server, subagent, helper or alternate-family tool was invoked. No Claude/Anthropic route exists or was used. |
| Capacity | Assigned budget 15 minutes, bounded. No broad or repeated campaign was run. No fallback model was invoked and no silent model change occurred; independent review remains with a different-family coordinator reviewer (OpenAI). |
| Exclusive writable | `docs/production/software-waves/SW-API-READ-02/AUTHOR.md`, `build/software-waves/SW-API-READ-02/**` (gitignored, private, not committed). |

## Scope and method (read-only)

Read `AGENTS.md`/protocol, the SW-API-READ-02 unit row in
`docs/planning/software-waves/PACKAGES.md`, `EV02_API_EVIDENCE_QUALIFICATION.md`,
`docs/production/ev02/API_PRESERVATION_REVIEW.md` and `FINAL_API_REVIEW.md`, the
registry objects for the four features, the live scenario DSL
(`tools.validate.scenarios.discover()`), and the accepted original records under
`docs/validation/evidence/ev02-original-api/`. F-API-002 (SW-API-READ-01) and
F-API-031/032 (SW-API-READ-04) were not touched. Prior red/alternate-client probe
results and the no-universal-quiescence limitation are carried forward unchanged.

Private receipts (gitignored, not committed):
`verify_four_features.json`, `route_coverage.json`, `subgroups.json`,
`index_integrity.json`, `rollup_digests.json`, `covers_drift.json`,
`live_covers.json`, plus the four generator scripts, all under
`build/software-waves/SW-API-READ-02/`.

## Cross-cutting verification (all counts zero except the stated totals)

| Check (141 records across the four features) | Result |
| --- | --- |
| Working-tree byte SHA-256 == `manifest.json` `sha256` | 0 / 141 mismatches |
| **HEAD blob** byte SHA-256 == manifest `sha256` | 0 / 141 mismatches |
| Working-tree SHA-256 == HEAD blob SHA-256 (no in-place rewrite) | 0 / 141 |
| Index OID == `HEAD:<path>` OID | 0 / 141 |
| `git status --porcelain` over the four features' evidence paths | clean |
| `evidence.schema.json` valid | 0 / 141 invalid |
| `commit.sha == 1baac3de…` | 0 / 141 not-1baac3de |
| `commit.dirty == false`, `dirty_files == []` | 0 / 141 |
| `environment.hub.image_digest` non-null | 0 / 141 (all `null`) |
| `level == V2`, `result == pass`, `gate == ok` | 0 / 141 off-spec |
| `timestamp.started < timestamp.finished`, both present | 0 / 141 |
| record `features` == live `Scenario.features_for("api")` | 0 / 141 mismatches |
| scenario resolvable in live `discover()` | 0 / 141 missing |
| `freshness == fresh`, `mapping_matches == true`, `changed_covers == []` | 0 / 141 exceptions |

Record roll-up digests (SHA-256 over the sorted `"<path>  <sha256>\n"` lines of
each feature's accepted original records): F-API-014 `b1c4f50f…73ff6b` (2),
F-API-016 `a0e2a09f…2fd7d5` (132), F-API-026 `b17afcb1…c607cf` (5),
F-API-028 `d8758e34…03db5a` (2), **all four `fff1a5f12f8e61c3627bb8b14ea4166bac4a9d73f8961d1e48a49bd367701e08` (141)**.

`.gitattributes` line 17 keeps `docs/validation/evidence/ev02-original-api/**`
`-text`; `git ls-files --eol` shows `i/lf w/lf attr/-text` on the sampled
records, so the preserved original bytes were not renormalized. No record was
promoted to V3, relabelled onto `51275723`, or given an image digest.

## Source-scope drift between the original source and the current base

`git diff --name-status 1baac3de..51275723 -- src/ tools/ tests/validation/scenarios/ tests/sim/`
returns exactly two entries: `A tests/validation/scenarios/sw_api_read_01.py`
and `M tests/validation/scenarios/writes.py`. Git **tree** objects confirm
`src/` (`d884ac6f…`), `tools/` (`b1f72ea0…`) and `tests/sim/` (`7dcf0638…`) are
byte-identical at both commits. Within the scenarios tree, `contracts.py`
(`7aa82d53`), `cec_capabilities.py` (`6f9fb0dc`), `cec_controls.py`
(`306a09c3`), `cec.py`, `outputs.py` and `_paths.py` are byte-identical blobs;
the `writes.py` change is purely additive — a new `_NAMES` constant plus three
F-API-018 rename scenarios (`writes.input_name`, `writes.input_name_invalid_port`,
`writes.input_name_blank`), with **zero** deleted or modified lines.

**Concrete covers drift for the four assigned features: none.** No `covers`
tuple, expectation, `client_features` mapping or scenario definition attributed
to F-API-014/016/026/028 differs between `1baac3de` and `51275723`. This is the
basis for **PRESERVE** rather than rerun: the product source, the validation
tooling and these four features' assertions are the same bytes that produced the
accepted records. 30 distinct covers paths are declared across the four features;
29 resolve at the current base (see the informational note below).

## Per-feature and per-subgroup disposition

All four features are already `current: V2` / `target: V2`. Nothing here
advances a level. Every registered interface below is registered in
`src/rest_api/app.py` at `51275723` and is exercised by the accepted records.

| Feature | Registered interfaces | Scenarios | Original records | Kinds | Actual checks | Covers universe | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-API-014 System info and storage | `GET /api/system/info`, `GET /api/system/storage` | 2 | 2 | 2 happy | 10 | 18 | **PRESERVE** |
| F-API-016 CEC catalogue/capability/enable | 7 (`/api/cec/commands`, `/api/cec/commands/{type}`, `/api/cec/capabilities`, `/api/cec/input/{input}/capabilities`, `/api/cec/output/{output}/capabilities`, `POST /api/cec/input/{port}/enable`, `POST /api/cec/output/{port}/enable`) | 132 | 132 | 115 happy / 17 failure | 1029 | 22 | **PRESERVE** |
| F-API-026 Themes and UI preferences | 5 (`GET`/`PUT /api/themes`, `POST /api/themes/reset`, `GET`/`PUT /api/ui/preferences`) | 5 | 5 | 5 happy | 29 | 22 | **PRESERVE** |
| F-API-028 Flic integration | `GET /api/integrations/flic/buttons`, `POST /api/integrations/flic/register` | 2 | 2 | 2 happy | 11 | 20 | **PRESERVE** |

Subgroup detail (records / distinct scenarios / kinds / checks / routes):

- **F-API-014** — `contracts` 2 / 2 / 2 happy / 10 / one `GET /api/system/info`
  (asserts `rest_api_version == "2.10.0"`), one `GET /api/system/storage`
  (asserts `data_dir_exists`/`config_dir_exists == true`). Both additionally
  assert no device write command, device otherwise unchanged, no simulator
  protocol warnings, and WebSocket-schema conformance. No failure/refusal case
  and no second-field assertion beyond those is present.
- **F-API-016** — `cec_caps` 88 / 88 / 78 happy + 10 failure / 602 checks —
  literal command catalogues, whole-table `GET /api/cec/capabilities` (4×),
  per-input (35×) and per-output (43×) capability reads, plus
  `…/input/invalid/capabilities` and `…/output/invalid/capabilities` refusals.
  `cec_controls` 40 / 40 / 34 happy + 6 failure / 404 checks — 20
  `POST /api/cec/input/{port}/enable` and 20 output equivalents with raw
  index-array readback (96 `GET /api/status/cec` hub reads), covering
  enable 0/1 per port 1–8, default-port, port 0, port 9 and refused cases.
  `contracts` 3 / 3 / 2 happy + 1 failure / 16 checks — literal
  `GET /api/cec/commands/input` and `/output` tables and the
  `GET /api/cec/commands/nope` → 400 refusal. `writes` 1 / 1 / 1 happy /
  7 checks — `POST /api/cec/output/{port}/enable` with the exact
  `set cec index` device command and hub readback. Registered-scenario set and
  original-record set are identical at 132; the registry additionally lists 133
  older historical records, the known stale duplicate `writes.cec_output_enable`
  (commits `72cc71dc` and `7dbc4dc7`), correctly not counted as fresh source.
- **F-API-026** — `contracts` 2 / 2 / 2 happy / 11 checks (saved `presets` /
  `activePresetIndex` / `cardOpacity` / `hoverPreference` and pinned tab
  order/tab order readback); `writes` 3 / 3 / 3 happy / 18 checks (`PUT
  /api/themes`, `POST /api/themes/reset`, `PUT /api/ui/preferences`, each with a
  separate hub readback). All 5 registered routes exercised; hub-data
  persistence only, no browser rendering.
- **F-API-028** — `contracts` 1 / 1 / 1 happy / 5 checks (reads the two fixture
  buttons); `writes` 1 / 1 / 1 happy / 6 checks (`POST
  /api/integrations/flic/register` renaming a button, then an independent
  `GET /api/integrations/flic/buttons` readback of the saved name). No physical
  button or SDK behaviour is exercised.

## Source, image and client limits (unchanged by this audit)

- **Client:** API only (`client: "api"`, aiohttp 3.13.3). No browser (V3), no
  Home Assistant, no UC/Remote, no real-image client. HA scenario count in
  CI 39467476091 is 19 actual HA scenarios and does not touch these four
  features.
- **Image:** every one of the 141 records has `environment.hub.image_digest ==
  null`. These are **source** API V2 passes, never V3/V4 image proof.
  Static version metadata (`hub.version` / `api_version` `2.10.0`) is not a
  matching-image proof.
- **Target:** `sim` source simulator only (seed `tools/simulator/states/default.json`,
  `simulator.source_sha256 23f7439ea94f5fcc`, BK-808 / firmware V1.10.01 /
  web V2.00.03). No physical HIL, no soak, no field, no final release.
- **Head:** the records are attributed to `1baac3de…`, not to `51275723`. CI
  39467476091 ran at head `2b10e000…` with merge source `564346be…` and tree
  `27325b45…`; that CI merge source is **not** treated as an ancestor head for
  these records and nothing was imported from it. CI's 1507-record audit
  (0 errors) and its counts (API 1416, browser 54, UC 18, HA 19) describe the CI
  run, not a new qualification of these four features.
- Findings linked by the registry (`SEC-11`, `BE-13`, `BE-35`, `PER-02`,
  `API-15`, `TST-03`) and all HIL-09 caps, hardware, SDK, soak and week
  field gates **remain open**. `docs/validation/findings_pending.yaml` is
  `findings: []`; the register rows stay in `docs/REMEDIATION_PLAN.md`. No
  open finding is claimed fixed by this audit.

## Gaps and proposed minimal corrective packets (NOT applied — no fresh lease)

No defect or overclaim was found in the four features' accepted proof. Two
bounded, non-blocking observations are recorded for coordinator decision:

1. **Dangling covers entry (F-API-026).** `contracts.themes` declares the cover
   `tests/e2e/fixtures/data/themes.json`, which does not exist at `51275723` and
   never existed in any commit in history (`git log --all` for that path is
   empty). It is byte-identical at both `1baac3de` and `51275723`, so there is
   **no drift** and no preservation impact; the sibling fixture covers
   (`ui_preferences.json`, `flic_buttons.json`, `device_settings.json`) all
   resolve. Minimal corrective packet (coordinator-owned, requires a serial
   lease): either add the fixture under `tests/e2e/fixtures/data/` or drop that
   one cover entry in `tests/validation/scenarios/contracts.py`, then re-run the
   scoped registry/schema tests. Not done here — scenarios are read-only.
2. **Historical duplicate still listed (F-API-016).** The registry lists 133
   pre-`1baac3de` records for 132 registered scenarios because
   `writes.cec_output_enable` exists at both `72cc71dc` and `7dbc4dc7`. The
   accepted source record is the single `1baac3de` one and the counts reconcile
   exactly (132 = 132); no action is required for correctness. A future
   registry-only cleanup could retire the older duplicate, but that is a
   coordinator-owned evidence decision with no proof value change.

Nothing here needs a rerun: no assigned feature has a missing assertion, an
actual defect, or a covers/assertion drift that preservation cannot carry.

## What was NOT run

**Tests NOT RUN. No `python -m tools.validate run`, no `pytest`, no `ruff`, no
CI.** This is a bounded READONLY audit; every count above comes from reading the
committed evidence records, the live scenario DSL metadata and Git object
comparison. `static source comparison is not a reproduced runtime result` — no
runtime defect is asserted or reproduced here. The independent Cross-family
review of this report, and any separate scenario replay, remain pending with the
coordinator.

## Required next acceptance

1. Qualified **different-family** review of this report and its receipts at the
   exact commit that adds it (MiniMax-M3 author ≠ OpenAI-family reviewer).
2. Coordinator decision on corrective observation 1 (serial lease) if desired.
3. No level promotion, no V3/image/cross-client claim, no ledger or manifest
   edit by this unit. Image/V3 proof for these four features, the HIL-09 caps,
   BE-13/BE-35/TST-03 hardware follow-ups and the 72-hour soak and week field
   gates remain separate and unclosed.

## Repository state

`git status --short` is clean at `51275723` before this report. The only
committed change from this unit will be this prose file; all analysis output is
under the gitignored `build/software-waves/SW-API-READ-02/`. No amend, push,
merge, tag or cleanup was performed.