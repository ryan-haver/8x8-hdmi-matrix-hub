# EV-CI-ATTRIBUTION: current attribution/scope disposition of the 56 historical CI records

**Bounded metadata scope disposition at the exact entry base
`638a226a49b9cc0ead952a4a787d12c26dfcd35e`. This admits nothing, refreshes nothing, qualifies
nothing and promotes nothing.** Every record keeps its actual source identity
`bdcf06dc6723aad7da63ecfed3d3555ab0d02e55`; the current-rule outcome is an explicit **unknown /
stale** for all 56, with a precisely scoped refresh as a separately gated next action.

| Authority | Observation |
| --- | --- |
| Task / Dispatch | `task_5fa43f7367b0` / `ctx_c2550304397b` |
| Run / worker / coordinator | `run_37205f6095b3` / `term_094e24b1-1986-40c1-9324-a0d7b800a00a` / `term_6ed8131e-3ab3-4693-8094-56cc10acd412` |
| Host / runtime / Orca | Windows local; runtime `e8ce3460-a9d4-4897-8e4f-10a8e3cdc400`; Orca 1.4.246 |
| Model / routing | native MiniMax-M3 via OpenCode 2, project `main`/`small`/`internal`; no helper, fallback, nested worker or unsupported CLI model/effort override; DeepSeek not dispatched |
| Worktree / branch | `wp-exec-ev-ci-attribution` / `ryan-haver/wp-exec-ev-ci-attribution` |
| Entry HEAD (exact, verified) | `638a226a49b9cc0ead952a4a787d12c26dfcd35e`; tracked source clean at start |
| Accepted inputs reused, unmodified | [CI_EVIDENCE_INTAKE.md](../../SW-AUDIT-01/CI_EVIDENCE_INTAKE.md) (OpenAI `gpt-6.1-sol`/high; report `9036ecffe2b5e18ccb6d636eba55edfbd0d6a80a` at frozen base `490a879bd346773cca64fac861eaaab29e703628`) and [CI_EVIDENCE_REVIEW.md](../../SW-AUDIT-01/CI_EVIDENCE_REVIEW.md) (independent MiniMax-M3 review; **ACCEPT**, inventory/metadata only) |
| New report commit | the commit that adds this file; the exact SHA is recorded in the delivery receipt and is verifiable with `git log -1 -- docs/production/software-waves/EV-CI-ATTRIBUTION/execution-20261101/AUTHOR.md` |
| Correction authority (this commit) | Task `task_f88cda2cf757` / Dispatch `ctx_c3d0257ab154`, worker `term_e65e8a7b-e69d-4cfd-8040-3c76188451be`; parent `d86b65c271cc06d95895b8abdce53e24210bc6d9`. Bounded prose corrections R1–R7 only, against the independent review at `81ac391cdc07ca8885b3b2237aa467aee0625675` (`REVIEW.md`, verdict `require_changes`): no new CI execution, source qualification, admission or failed-qualification retry, and no change to any 56-row, cover, object, ancestry or freshness fact below |

## Scope, and the three limits that bound it

This report answers one question per unit: *relative to this entry base, did anything the unit's
own `covers` claim change, and do its definition or client/target binding differ?*

It is **not** a CI run, re-execution, source implementation, qualification, privacy admission,
ledger generation or feature promotion, and it does **not** re-audit raw archives, assertion
predicates, screenshots or credentials: those were accepted as historical facts at the frozen base
and are carried forward unchanged and labelled historical. Nothing was freshly fetched, and no old
download is claimed to be current.

- **Covered-path equivalence is not functional equivalence.** Zero intersections means the units
  are *not invalidated by path*, not that their recorded behaviour still holds.
- **Covered-path equivalence is not ordinary freshness.** Freshness here is an ancestry test.
- **Covered-path equivalence is not canonical admission, and not a source relabel.** No SHA,
  record, cover, feature or level was rewritten to the integration SHA.

## Method (bounded, static, read-only metadata inspection)

1. **Accepted inventory first.** The 56 unit tuples (unit, scenario, client, level, state) were
   parsed from the accepted table in `CI_EVIDENCE_INTAKE.md`; the accepted `B`/`M` state column
   was honoured — 60 requested units, 56 matched (`B`), 4 missing (`M`).
2. **Git facts re-derived** at this worktree by fixed argv `subprocess.run`, retaining return
   codes and full stdout/stderr.
3. **Finite cached source→entry diff.** The source→entry comparison
   `git diff --name-only bdcf06dc… 638a226a…` was executed and cached in **both** retained
   receipts (`probe_01` and `probe_02`); the comparison was finite and reused rather than
   re-derived, so one historical source SHA means no quadratic blob scan and no repeated global
   audit. The diff was not re-run here to restate wording.
4. **Covers re-derived from the historical source definitions.** `tools`, `tests/validation` and
   `docs/api` were exported read-only from `bdcf06dc…` via `git archive` into this worker's
   private subtree and the scenario metadata imported there. The accepted review had established
   that each record's `covers` equal its scenario's `covers` exactly (56/56) across 11 distinct
   cover sets; both numbers reproduce here, so the derived covers are the historical own-covers.
5. **The repository's own rule was applied** — `tools/validate/gitinfo.matches` (exact path,
   directory prefix, `fnmatch` glob), imported from the source export — then re-tested with a
   **second, independent implementation**.
6. **The current freshness rule was evaluated at the entry checkout** by calling the
   repository's own `tools/validate/ledger.freshness` with the historical source SHA and each
   unit's accepted covers. It creates, reconstructs, re-runs and re-reads nothing.

Not done: no scenario or `Expectation` executed; no raw ZIP, log, payload, screenshot or
credential opened; no ledger, registry or finding generated; no network refetch, CI dispatch,
campaign, probe, service, install, hardware, Docker, release, push, merge, cleanup or history
manipulation.

## Verified Git facts at the entry base (NEW)

- `git rev-parse HEAD` → `638a226a49b9cc0ead952a4a787d12c26dfcd35e` — equals the injected entry
  SHA; the tracked tree is clean.
- Source `bdcf06dc…`, published head `e16ec6af…` and the entry are all real `commit` objects.
- **`git merge-base --is-ancestor bdcf06dc… 638a226a…` → exit 1 — the source is NOT an ancestor
  of the entry.** The published head and the frozen base are both ancestors of the entry
  (exit 0 each).
- Trees: entry `202fc21e0c514eb94e733a32846a09f026f2c4f7`; source = published head
  `7fa5c9d99731349b0705fa2ef7818d5eb5a11350` — equal to each other, **different from entry**.
- Source→entry changed paths: **136**, identical to the published-head→entry diff (consistent
  with that tree equality).
- `gitinfo.changed_since` at the entry checkout: `bdcf06dc…` → `None` (not in this history);
  `e16ec6af…` → 136 paths.

**Changed-path scope (NEW).** The 136 changed paths are `AGENTS.md` (1) plus 135 `docs/**` paths
(`docs/agent-process/**` 39, `docs/ORCHESTRATION_PROTOCOL.md` 1, `docs/planning/**` 20,
`docs/production/**` 75), and **zero** of them are covered by any unit's `covers`. The historical
six-path documentation diff **does not carry over** to this base — the changed set is now 136
paths, still entirely documentation plus the root `AGENTS.md`, and still intersecting **zero** unit
covers. That is a re-derived result at the new base, not an inherited assumption.

**Subtree identity (NEW).** Every subtree a unit's `covers` can name is **byte-identical**
between `bdcf06dc…` and `638a226a…` (`git rev-parse <sha>:<path>`): `tests/`, `tests/validation/`,
`tests/validation/scenarios/`; `tools/`, `tools/validate/`; `src/`, `config/`, `scripts/`,
`run.py`; `web/`, `custom_components/`; `docs/api/`, `docs/validation/`,
`docs/validation/features.yaml`; `pyproject.toml`, `requirements.txt`. So no scenario
**definition** changed; no client, hub runtime, HA component, API-schema or validation-tooling
code changed; and the feature registry/baseline is unchanged, so the accepted 38-row feature table
carries forward unaltered.

## Per-unit current attribution/scope disposition (56 units, NEW metadata)

**Cover set** is the unit's own `covers` tuple (count in parentheses), derived from the source
definitions. **Δ covers∩changed** is the number of source→entry changed paths matched by that
unit's own covers under the repository's rule. **Δ definition** and **Δ client/target** record
whether the declarative definition or the client/target binding differs at the entry base.
**freshness @entry** is what the repository's own `ledger.freshness` returns for that unit's
covers at the historical source SHA against this entry HEAD.

| Unit | Scenario | Client / level | Cover set | Δ covers∩changed | Δ definition | Δ client/target | freshness @entry | Next action |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| U05 | `ha.config_flow` | ha / V3 | C01 (22) | 0 | none | none | `unknown` | refresh-required (gated) |
| U06 | `ha.display_unplugged` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U07 | `ha.front_panel_route` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U08 | `ha.input_signal` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U09 | `ha.matrix_offline` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U10 | `ha.matrix_unreachable` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U11 | `ha.mute_switch` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U12 | `ha.power_off` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U13 | `ha.power_on` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U14 | `ha.preset_button` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U15 | `ha.reboot_button` | ha / V3 | C03 (22) | 0 | none | none | `unknown` | refresh-required (gated) |
| U16 | `ha.reconfigure` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U17 | `ha.select_source` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U18 | `ha.service_cec_display` | ha / V3 | C04 (23) | 0 | none | none | `unknown` | refresh-required (gated) |
| U19 | `ha.service_cec_invalid` | ha / V3 | C04 (23) | 0 | none | none | `unknown` | refresh-required (gated) |
| U20 | `ha.service_cec_source` | ha / V3 | C04 (23) | 0 | none | none | `unknown` | refresh-required (gated) |
| U21 | `ha.service_recall_preset` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U22 | `ha.service_switch_input` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U23 | `ha.stream_switch` | ha / V3 | C02 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U24 | `kiosk.route_all_apply` | browser / V3 | C05 (20) | 0 | none | none | `unknown` | refresh-required (gated) |
| U25 | `kiosk.route_one_muted` | browser / V3 | C05 (20) | 0 | none | none | `unknown` | refresh-required (gated) |
| U26 | `preset_read.catalog_matches_device` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U27 | `preset_read.device_slot_1` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U28 | `preset_read.device_slot_2` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U29 | `preset_read.device_slot_3` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U30 | `preset_read.device_slot_4` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U31 | `preset_read.device_slot_5` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U32 | `preset_read.device_slot_6` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U33 | `preset_read.device_slot_7` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U34 | `preset_read.device_slot_8` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U35 | `preset_read.saved_current_1` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U36 | `preset_read.saved_current_2` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U37 | `preset_read.saved_current_3` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U38 | `preset_read.saved_current_4` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U39 | `preset_read.saved_current_5` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U40 | `preset_read.saved_current_6` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U41 | `preset_read.saved_current_7` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U42 | `preset_read.saved_current_8` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U43 | `preset_read.saved_partial_1` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U44 | `preset_read.saved_partial_2` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U45 | `preset_read.saved_partial_3` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U46 | `preset_read.saved_partial_4` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U47 | `preset_read.saved_partial_5` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U48 | `preset_read.saved_partial_6` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U49 | `preset_read.saved_partial_7` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U50 | `preset_read.saved_partial_8` | api / V2 | C06 (21) | 0 | none | none | `unknown` | refresh-required (gated) |
| U51 | `presets.recall` | api / V2 | C07 (25) | 0 | none | none | `unknown` | refresh-required (gated) |
| U52 | `presets.recall` | browser / V3 | C07 (25) | 0 | none | none | `unknown` | refresh-required (gated) |
| U53 | `reboot.enabled_shortcut` | api / V2 | C08 (28) | 0 | none | none | `unknown` | refresh-required (gated) |
| U54 | `reboot.enabled_shortcut` | browser / V3 | C08 (28) | 0 | none | none | `unknown` | refresh-required (gated) |
| U55 | `routing.route_all` | api / V2 | C09 (26) | 0 | none | none | `unknown` | refresh-required (gated) |
| U56 | `routing.route_all` | browser / V3 | C09 (26) | 0 | none | none | `unknown` | refresh-required (gated) |
| U57 | `routing.switch_one` | api / V2 | C10 (24) | 0 | none | none | `unknown` | refresh-required (gated) |
| U58 | `routing.switch_one` | browser / V3 | C10 (24) | 0 | none | none | `unknown` | refresh-required (gated) |
| U59 | `shortcuts.preset_recall` | api / V2 | C11 (27) | 0 | none | none | `unknown` | refresh-required (gated) |
| U60 | `shortcuts.preset_recall` | browser / V3 | C11 (27) | 0 | none | none | `unknown` | refresh-required (gated) |

### Reading of the table

- **No covered path changed for any unit (56/56).** All 11 cover sets are disjoint from the 136
  source→entry changed paths, under both the repository's `gitinfo.matches` and an independent
  re-implementation; the distinct cover sets (11) and their sizes (20–28 entries each) reproduce
  the accepted review's independently recomputed count of 11.
- **No definition, client or target change for any unit (56/56).** Scenario packages, validation
  tooling, hub runtime, browser client, HA component and API schema are byte-identical between
  the historical source and this entry base, so each unit's declarative assertions and
  client/target binding are unchanged here. The accepted per-unit assertion descriptions, feature
  sets, client attribution, levels and dirty state remain valid **at the entry base** as
  *historical* facts.
- **Current-rule freshness at the entry base is `unknown` for 56/56.** `gitinfo.changed_since`
  returns `None` for a commit not in this history, so `ledger.freshness` returns `unknown` and
  `ledger.compute` puts every record in the row's `stale` collection. The repository's own module
  states that "evidence from a commit that is not an ancestor of HEAD counts as stale". The
  zero-intersection result does not soften this.
- **Scope mapping is therefore "no-intersection" for all 56 — and that is all it is.** It supports
  a later coordinator-owned admission review; it is not functional equivalence, not ordinary
  freshness, not canonical admission and not a source relabel.

### Precise next action (uniform for all 56; separately gated, not run here)

1. **Refresh-required; explicit unknown intake retained.** A compliant record for these 56 units
   needs a real CI execution whose source commit is an ancestor of the integration head —
   practically, a refresh from the current approved integration source (the entry base
   `638a226a…` or a descendant). Git identity here establishes **static definition identity at
   the exact entry base only**: the covered runtime/client/schema subtrees are byte-identical
   between the historical source and `638a226a…`. It does **not** predict what a later run would
   exercise — a descendant may change code, and environment, inputs and scheduling may change
   exercised paths even at an unchanged source. Any future refresh is therefore a separately
   gated real execution whose **actual** source, environment and behaviour must be checked and
   recorded, producing new record bytes and still needing the separate privacy/VAL-15, image,
   client and owner gates. No such execution is authorized, performed or claimed here.
2. **The coordinator-owned admission decision stays open and unsatisfied.** Under current rules
   there is no compliant admission route for a non-ancestor source; this report proposes none and
   records no waiver. No forced pass, no undocumented waiver.
3. **Not authorized here.** A CI refresh is a separately gated next action; it is not a CI run,
   dispatch, campaign, probe, service, refetch, ledger generation or import, and none occurred.

### Carried forward unchanged (historical, not re-executed)

- Accepted inventory quantities — 60 requested units, 55 scenarios, 38 requested features, 56
  matched (30 API V2 + 7 browser V3 + 19 HA V3), 4 Flic units absent because that CI never
  requested a Flic client — are historical facts of the accepted report and review. The 470
  passing / 2 nonapplicable / 0 failed tally and the two client-scope exclusions (U53, U59) are
  historical and were **not** re-executed here.
- **U01–U04 (Flic) are absent from these old CI archives, and are not relabelled.** That CI
  never requested a Flic client, so no Flic record could exist in it; that is an
  **archive-specific** absence, not a project-wide missing-Flic-proof finding. Separate, later
  proof already exists: [FLIC_REFRESH.md](../../SW-AUDIT-01/FLIC_REFRESH.md), independently
  accepted in [FLIC_EVIDENCE_REVIEW.md](../../SW-AUDIT-01/FLIC_EVIDENCE_REVIEW.md) as four
  genuine `flic`/`sim`/V3 `pass`/`gate=ok` records with 25 pass and one n/a, accepted as bounded
  execution facts, with **privacy/artifact admission on HOLD**; integrated at
  `2a7fe096`/`21a57813`/`862b9299`. That existing proof needs a **coordinator disposition
  before any further refresh decision**; no duplicate Flic execution is mandated by these
  archives, and nothing here admits or publishes the held artifacts.
- **F-API-034** remains a negative-path assertion gap **in the old CI archives**, untouched here.
  Current context: the retained API-V2 candidate chain (`938ae303…` → `386872…` → `ee3f2e7f…` →
  report `caaa4faa…`) is still **awaiting qualified review**, and the failed/partial parallel
  FSEC007 gate remains failed. Existing candidate work is **not** accepted source and is not proof
  that duplicate implementation is needed; no duplicate implementation is mandated here, and no
  V3-target or `F-MTX-002` attribution is made. This report reuses the recorded metadata outcomes
  only and reviews no candidate source or payload.
- Image, source, dirty and screenshot identities and the original record bytes are immutable and
  were not re-read. The null hub `image_digest` remains **source-run simulator proof, not
  release-image execution**; screenshot checks remain structural only.
- The accepted 38-row feature disposition table carries forward unaltered because
  `docs/validation/features.yaml` is byte-identical at the entry base; **no feature is qualified,
  promoted or admitted here.**

## Proof limits

- Bounded **current attribution/scope metadata** at one exact entry base; no implementation
  correctness opinion and no source or privacy code-review qualification claimed or inferred.
- Bounded Git and metadata inspection plus documentation-module tests only: **no raw CI archive was
  interpreted and no runtime/scenario campaign was run**. No scenario or `Expectation` predicate
  was evaluated, no CI record or payload was opened, no ledger, registry or finding was generated
  or imported, no secret was read or printed, and no network refetch occurred. Two bounded
  non-CI events did occur and are disclosed: a read-only **Git `archive` tar export and extraction
  of the historical *source* tree** (`tools`, `tests/validation`, `docs/api`) used for static
  definition comparison, and a **pytest run of the five existing documentation modules**
  (`core`, `client-guides`, `openapi-config`, `security`, `license-protocol`). Neither is a new CI
  execution, a source qualification or an admission.
- The zero-intersection result is a **path-scope** result about the paths each unit names. It is
  not a statement that the recorded behaviour still holds at the entry base, nor a substitute for
  a real refresh.
- Old downloads and metadata were **not** freshly fetched and are not claimed to be current. The
  old absolute `wp-ci-proof-intake` `analysis-01/units.json` path is absent at its former
  location, and that absence is **not** proof the originals were lost. The covers used here were
  derived from the accepted unit tuples and the source definitions at `bdcf06dc…`, which the
  accepted review had established as equal to the records' own covers (56/56).
- This report **cannot admit** the original bytes, waive the source/client/image/owner
  requirements, clear privacy/VAL-15, or resolve the retained API/WS/privacy source reviews or the
  actual parallel FSEC007 failure. Those remain held/unresolved.

## Gate status: held/open, with the original three Tron owner decisions closed

**Held / open and unsatisfied.** Privacy/VAL-15 admission; the retained API/WS/privacy qualified
source reviews; the actual parallel FSEC007 failure; physical hardware HIL; any outstanding
owner visual approval; the 72-hour soak; week field sign-off; and the final version/artifact
release. These remain open and this report changes none of them; software-level scope metadata
never satisfies them.

**Closed, separately.** The **original three** Tron paused-frame owner decisions were approved by
the owner on 2026-10-20
([TRON_OWNER_APPROVAL_20261020.md](../../../../validation/TRON_OWNER_APPROVAL_20261020.md)).
That closure covers only those three reported differences and the three named captures. It is not
a general visual approval and not a release approval, and it does not close any gate listed
above.

## Checks, invocations and exits

Every invocation ran as a direct `subprocess.run` with a fixed argv; the return code and full
stdout/stderr of each were captured before the next. No piped status was inferred.

| Invocation / check | Exit / result |
| --- | --- |
| `git rev-parse HEAD` / `--abbrev-ref` / `status --porcelain`; `git cat-file -t`; `git merge-base --is-ancestor` source→entry / published→entry / frozen→entry | 0; HEAD `638a226a…`, branch `ryan-haver/wp-exec-ev-ci-attribution`, tracked tree clean; all three are `commit`; ancestry **1** / 0 / 0 (the 1 is the intended finding) |
| `git rev-parse …^{tree}`; `git diff --name-only` source→entry (the cached diff recorded in probe 01 and probe 02) and published→entry; `git rev-parse <sha>:<path>` for 16 subtrees | 0; source == published ≠ entry; 136 paths, identical sets; all 16 subtrees identical |
| `git archive --format=tar bdcf06dc… tools tests/validation tests/__init__.py docs/api`; scenario metadata import; `gitinfo.matches` over 56 covers × 136 paths plus an independent re-implementation | 0; 0 unsafe member names; 101 scenarios across the 8 modules owning the 56 units; 0 intersections by both rule implementations |
| `ledger.freshness` at the entry checkout, 56 units | `unknown` × 56 at the historical source SHA (the actual result); `fresh` × 56 at the published-head SHA — **HYPOTHETICAL metadata only**, since no actual record carries that source: it relabels, admits and waives nothing — **not** an admission |
| Accepted-table parse; report UTF-8 / LF / JSON / 56-ID / reference / scope checks | 0; 60 rows, 56 `B`, 4 `M`; all report checks pass; receipts in the ignored build subtree |
| `pytest -p no:tests.route_inventory -p no:cacheprovider` over the five docs modules (`core`, `client-guides`, `openapi-config`, `security`, `license-protocol`) | all pass; receipt in the ignored build subtree |
| `git -c core.hooksPath= commit` | documented **invocation-only** exception for this prose-only report, after the checks above; no hook configuration change, **no source-hook or full-suite pass claimed** |

All worker diagnostics are confined to this worker's ignored build subtree
`build/software-waves/EV-CI-ATTRIBUTION/execution-20261101/author/` (this correction's own
subtree is `author/correction-01/`) and the fresh private scratch trees
`C:/t/exec-ev-ci-attribution/nov02-attempt01/` and
`C:/t/exec-ev-ci-attribution/nov02-correction01/`; every failed probe attempt is preserved under
its own numbered filename and no historical byte was overwritten. The only tracked deliverable is
this new report. Root source, tests, tools, fixtures, scenarios, schema, registry, ledger,
findings, manifests, lockfiles, evidence and baselines are unchanged.

## Review requirement

This new deliverable needs **independent factual review by a different underlying model family
at the exact report commit** (an OpenAI/Astra-family reviewer is the indicated route; the author is
MiniMax-M3). There is **no self-acceptance**. The prior attempt-1 outcome was a **formal core
qualification attempt-1 FAIL with no qualified domain** — provenance, invariants and
counterexamples passed, while `behavior_and_tools`, `calibration` and `review_quality` failed. It
is **not** retried automatically; the explicit owner retake choice is pending, and route
provider capacity is a separate concern from that outcome. The coordinator owns settlement,
preservation, publication and any actual acceptance or admission.
