# W03 exact canonical-evidence metadata review

**Candidate reviewed (exact):** `78ce344800a9d1b3088bb8e886f65e2c8dfa0918`
**Assigned base (exact):** `28fce729ca4ea08bfc2f19805b36e13ae8c184f2`
**Candidate relationship:** exactly one commit above the base (`78ce3448`, *"docs(validation): prepare byte-exact wave03 evidence assembly"*); no intermediate commits.
**Review worktree:** `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/w03-final-metadata-review`, branch `ryan-haver/w03-final-metadata-review`, HEAD `78ce3448`, clean tree at review start.
**Reviewer:** native `minimax-coding-plan` / `MiniMax-M3` / `thinking` through opencode2 (no effort override, no Anthropic, no plugin/MCP, no subagent, no hidden/broker route, no model substitution, no new spending). The coordinator holds the native attestation for this session.
**Author of the candidate:** coordinator/metadata author, OpenAI family. Reviewer family (MiniMax) differs from the author family (OpenAI).
**Reviewer role:** report only. No source, test, scenario, schema, canonical record, feature row, ledger, finding, manifest, lock or private-runtime byte was edited by this review. The only file this review adds is this report.

---

## 1. Scope, and what this review is *not*

In scope: the **new canonical metadata and imported records** of candidate `78ce3448` — the byte manifest, the 44 imported JSON evidence records, the 32 imported PNG screenshots, the `docs/validation/features.yaml` field changes, the `docs/validation/findings_pending.yaml` rows, the regenerated `docs/validation/LEDGER.md`, the new `docs/validation/W03_EVIDENCE_ASSEMBLY.md`, and the `docs/production/AGENT_ALLOCATION.md` readiness entry.

Explicitly **not** in scope, and **not** claimed by this report:

- This is **not** a general security/core source review, and nothing here qualifies the reviewer for that domain. The prior M3-authored inventory prose is background only; this review does not self-approve it.
- No assertion weakening, target lowering, cap waiver, owner gate, baseline change, image qualification, browser/UI qualification, hardware/HIL, 72-hour soak, week field sign-off, final version/artifact release is approved. The three **Tron paused-frame owner approvals were already closed by the owner on 2026-10-20** (`docs/validation/TRON_OWNER_APPROVAL_20261020.md`, covering desktop, kiosk-tab-a11 and kiosk-iphone16promax only); this review does **not** reopen them, does **not** grant or extend them, and does **not** treat them as a release approval — the remaining release gates stay open.
- The original source reviews keep their own attribution and are **not** re-attributed: CORS `7b07e1cb` authored by Sol 6.1/high, functional `7b07e1cb`, submitted `cb87427b`, independently reviewed by DeepSeek (`c8910ee5`); offline routing functional `3788353e`, submitted `4baef574`, independently reviewed by Sol (`0bd3d76f`). This review confirms those sources are present and unchanged; it does not re-review them.
- No current-head CI, image, broader-client or future-evidence gate is pre-approved.

---

## 2. Material actually inspected

Base → candidate diff: **82 files changed, 61,090 insertions(+), 91 deletions(-)**.

| Class | Paths | Note |
| --- | ---: | --- |
| New evidence JSON | 44 | under `docs/validation/evidence/software-waves/W03-CLOSEOUT-20261028/` |
| New evidence PNG | 32 | git-LFS tracked, same namespace |
| `docs/validation/features.yaml` | 1 modified | registry |
| `docs/validation/findings_pending.yaml` | 1 modified | register |
| `docs/validation/LEDGER.md` | 1 modified | generated report |
| `docs/validation/W03_EVIDENCE_ASSEMBLY.md` | 1 new | packet description |
| `docs/validation/runs/.../import-manifest.json` | 1 new | byte manifest |
| `docs/production/AGENT_ALLOCATION.md` | 1 modified | dated readiness record |

**The whole candidate diff is confined to `docs/`.** No path outside `docs/` changed; no `src/`, `tools/`, `tests/`, `web/`, `custom_components/`, root manifest or lockfile (`package.json`, `package-lock.json`, `pyproject.toml`, `requirements*.txt`) was touched. `docs/validation/runs/.../import-manifest.json` is the new **evidence byte manifest**, not a build/packaging manifest.

Evidence namespace integrity (`git diff --name-status BASE CANDIDATE -- docs/validation/evidence`): **76 entries, all status `A`**. Zero modified, zero deleted, zero renamed old evidence records; every added path is inside `docs/validation/evidence/software-waves/W03-CLOSEOUT-20261028/`.

---

## 3. Commands actually run, with exits

Interpreter: the existing root virtualenv `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe` (Python 3.12.10), used **read-only**. Process-local `PYTHONPATH` = this worktree root + `src`; isolated pytest `--basetemp` under this reviewer's own ignored `build/fanout-readiness-20261028/review/`. No private root data/config was read or written.

| # | Command (this worktree) | Exit | Result |
| --- | --- | ---: | --- |
| 1 | `git rev-parse HEAD` / `git log` / `git diff --name-status --stat BASE CANDIDATE` | 0 | HEAD `78ce3448`; base `28fce729`; single candidate commit; 82 files |
| 2 | `git diff --name-status BASE CANDIDATE -- docs/validation/evidence` | 0 | **76 `A`**, 0 non-`A`; all inside the new namespace |
| 3 | `git diff --name-only BASE CANDIDATE` (non-`docs/` filter) | 0 | **no non-`docs/` path changed** |
| 4 | `git rev-parse <rev>:<path>` for the 9 functional source paths at candidate / base / functional source | 0 | all 9 identical (see §5.1) |
| 5 | `git rev-parse` for the two prior `REVIEW.md` blobs vs their review commits | 0 | `40e18f23…` == `c8910ee5`; `85c18d24…` == `0bd3d76f` |
| 6 | `check_manifest.py` (own helper, read-only) — **sections A (candidate blob bytes vs manifest), A2 (PNG worktree bytes) and B (original-source comparison) completed and are relied upon; the helper's later B2 "base-byte lookup" sweep was interrupted by the coordinator, so the helper as a whole is NOT a PASS** (§6) | A/A2/B sections completed; B2 interrupted | manifest self-consistency (76 entries, 44 JSON + 32 PNG); 44/44 JSON SHA-256 match; 32/32 LFS OID + size match; 32/32 working-tree PNG SHA-256 match; 63/76 matched against the delivery root before the original-CORS root was added in #7 |
| 7 | `check_original_sources.py` (own helper, read-only) | 0 | **76/76 byte-identical** to the READ-ONLY originals; 13/13 SHA-256 cross-match against the inventory report table |
| 8 | `check_evidence_content.py` (own helper, read-only) | 0 | 44/44 schema-valid; source SHA / dirty / image digest / features / covers / screenshots / assertions |
| 9 | `check_codepoints.py` + `check_encoding_scan.py` (own helpers, read-only) | 0 | encoding scan over every changed path — **1 defective file** (see §4, F-01) |
| 10 | `check_blobs_and_yaml.py` (own helper, read-only) | 0 | 9 functional blobs; `features.yaml` per-feature changed-field map |
| 11 | `check_semantics.py` (own helper, read-only) | 0 | CORS assertion inventory; `features_for` mapping; VAL-14 linkage; historical failed-CI record |
| 12 | `python -m pytest tests/validation/test_registry.py tests/validation/test_evidence_schema.py tests/validation/test_ledger.py -q --basetemp=<own> ` | **0** | **42 passed** (matches the coordinator's stated 42) |
| 13 | `python -m pytest tests/test_openapi_and_config_docs.py tests/test_core_documentation.py -q -p no:tests.route_inventory --basetemp=<own>` | **0** | **65 passed** |
| 14 | `python -m tools.validate check` (committed evidence) | **0** | `[validate] gate OK (0 known failure(s) linked to open findings)` |
| 15 | `python -m tools.validate ledger --out build/fanout-readiness-20261028/review/LEDGER-regenerated.md` | **0** | fresh regeneration; run **serially** after #12–#14, never concurrently with registry checks |
| 16 | `git diff --no-index docs/validation/LEDGER.md <scratch>/LEDGER-regenerated.md` | 1 (differences found) | 167 changed lines, **all** of them the relative-link base and the `Commit` stamp; no content difference |
| 17 | `check_ledger_compare.py` (own helper, read-only) | 0 | decisive attribution: the two **generated** ledger files parsed per feature and diffed — 40 freshness flips (39 `fresh→stale`, 1 `—→fresh` = `F-API-031`), 15 level changes, and the 11 non-docs paths changed between the old stamp `141bffb2` and the base `28fce729` with their covering scenarios |

**Report-only commit:** this file is added with an invocation-scoped hook exception, `git -c core.hooksPath= commit`, after the real report checks described in §7. The persistent `core.hooksPath` (`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.githooks`) was **not** modified and no persistent hook configuration was changed. The configured pre-commit hook runs `ruff` plus the **full core pytest suite**; it does not apply to a one-file report-only commit whose diff contains no source, test, tooling, registry, ledger, finding, manifest or evidence byte, and the task explicitly declines to re-run the 4,084-test core / 100-test Remote suites absent a new concern. No implementation hook was bypassed.

---

## 4. Findings

### F-01 — MEDIUM — `docs/validation/features.yaml` — UTF-8 → latin-1 double-encoding corruption in 14 lines, touching 10 feature rows outside the authorized change set

**Evidence (byte-level, own measurement, `build/fanout-readiness-20261028/review/features-yaml-codepoints.txt` and `.../encoding-scan.txt`):**

| Blob | U+00A7 SECTION SIGN | U+00C2 LATIN CAPITAL A WITH CIRCUMFLEX | U+FFFD REPLACEMENT CHARACTER |
| --- | ---: | ---: | ---: |
| base `28fce729` | 14 | **0** | 0 |
| candidate `78ce3448` | 14 | **14** | 0 |

Every `§` in the file was re-encoded from UTF-8 (`C2 A7`) to UTF-8-encoded-latin-1 (`C3 82 C2 A7`), i.e. the classic "read as cp1252, write as UTF-8" round-trip defect. Base line 1 is `… VALIDATION_PLAN.md \xa73.`; candidate line 1 is `… VALIDATION_PLAN.md \xc2\xa73.`

**14 affected lines — 3 header comment lines and 11 `claim:` values:**

- header comments: lines 1, 10, 15 (`VALIDATION_PLAN.md §3`, `VALIDATION_PLAN §2`, `REMEDIATION_PLAN.md §4`);
- `claim:` rows: `F-UC-008` (§3), `F-UC-009` (§3), `F-UC-011` (§3), `F-UC-012` (§3), `F-UC-013` (§9 item 7), `F-UC-014` (§9 item 9), `F-UC-016` (§9 item 5), `F-REL-005` (§9 item 8), `F-REL-009` (`VALIDATION_PLAN §1.5`), `F-REL-015` (`REMEDIATION_PLAN.md §5.1`), `F-REL-018` (`VALIDATION_PLAN §2`).

**Why this is a real finding and not noise:**

1. It violates acceptance question 2's constraint *"Exact allowed feature-field diff only FAPI002, FAPI031, FAPI033, FAPI034, FREL009, FSEC007, FSEC014"*. The candidate's registry diff changes **17** feature rows, not 7: the 7 authorized rows plus **10 out-of-scope rows** whose only change is this corruption (`F-REL-005`, `F-REL-015`, `F-REL-018`, `F-UC-008`, `F-UC-009`, `F-UC-011`, `F-UC-012`, `F-UC-013`, `F-UC-014`, `F-UC-016`). `F-REL-009` is in the authorized set, but its `claim` change is itself the corruption and is not one of that row's intended edits (`evidence`, `findings`).
2. It is an **unintended, non-semantic regression** in committed registry text, introduced by exactly the candidate commit (the base is clean; `78ce3448` is the only commit in the range).
3. It is **not** detected by any automated check — 42 metadata tests and 65 documentation/config tests pass at the candidate — so it can only be caught by byte/codepoint inspection. That is why this review performed one.

**What it does *not* affect (measured, not assumed):** no feature `target` changed anywhere in the file; the only `current` change is `F-API-031` V1→V2; no evidence path, level, freshness disposition, finding link, gate outcome, ledger number or manifest byte depends on a `claim:` string. The corruption is confined to human-readable documentation pointers.

**Required correction (coordinator-authored, in the coordinator's owned metadata):** restore the 14 lines to the base's single `U+00A7` form, so the registry diff is limited to the seven authorized rows and their intended fields. No other file in the candidate shows any encoding defect — `encoding-scan.txt` reports `features.yaml` as the **only** defective file among all 82 changed paths.

### F-02 — INFORMATIONAL — `docs/production/AGENT_ALLOCATION.md` — dated binding, already superseded at review time

The readiness entry records `Live root 28fce729…, origin 411c66429df3b813072e736c41c3a8aa83043a70`. At review time the local remote-tracking ref `origin/wp-runtime-completion` still equals `411c6642…` (so the record is accurate as written), while the **root** worktree has already advanced locally to `6228b273df5822b63b6d516121ab9a3f169f598e`. This is exactly the standing-rule case — dated ledger bindings are observations, not permanent launch args — and it is not a defect in the metadata candidate. Recorded only so the coordinator re-observes the live head before publication. No finding is raised.

### No other findings

No other defect was found in the imported bytes, the manifest, the registry mapping, the finding rows, the ledger, or the packet description. In particular there is **no** assertion weakening, target lowering, cap waiver, owner gate, baseline change, image-digest claim, old-failure import, diagnostic import, attribution change, or pre-approval of a future gate.

---

## 5. Acceptance questions — measured answers

### 5.1 Question 1 — manifest coverage, byte-exactness, LFS OIDs, original-source comparison

**Manifest self-consistency:** `prepared_at_base = 28fce729ca4ea08bfc2f19805b36e13ae8c184f2`, `original_cors_source = 7b07e1cb7e7eb29a38b55d3b050703149f1b797c`, `combined_source = 310d8b65a9fce3c9069523d4ac5ce21157e75c9f`, `records = 44`, `screenshots = 32`, `files[] = 76` → actual 44 `.json` + 32 `.png` + **0** other-extension entries, **0** duplicate destinations. Groups: `auth` 46 (14 JSON + 32 PNG), `cors` 13, `original-cors` 13, `api-root` 3, `offline` 1 = 76.

**Candidate Git blob bytes vs manifest:** 76/76 blobs present at `78ce3448`; **44/44 JSON SHA-256 match**; **0** length mismatches for JSON; **0** missing blobs. The 32 PNGs are **git-LFS pointers** in the blob (131 B each): **32/32** `oid sha256:` equal the manifest `sha256`, **32/32** `size` equal the manifest `bytes`, and **32/32** smudged working-tree PNG files hash to the manifest SHA-256 with matching length (**0** mismatches). No PNG is a non-pointer.

**Original READ-ONLY sources — byte-exact, not self-generated expectations:** all **76/76** files are byte-identical to their originals (**0** missing, **0** differing):

- the **13 original CORS records** to `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-sw-api-header-proof/build/software-waves/SW-API-READ-04-C1/clean/campaign/evidence/F-API-031/`;
- the **31 combined records + 32 screenshots** to `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/build/phase-resume-20261026/evidence-delivery/` (`api-root`, `auth`, `cors`, `offline`).

As a third, independent check, the **13 original-CORS SHA-256 values cross-match the table recorded in `docs/production/software-waves/W03-CLOSE-INVENTORY/AUTHOR.md` §4.3**: 13/13 matched, **0** mismatches.

**Record content (all 44, from the candidate's own bytes):** 44/44 valid against `docs/validation/evidence.schema.json` (**0** schema failures); `result = pass` and `gate = ok` for **44/44**; `environment.hub.image_digest = null` for **44/44**; `commit.dirty = false` and `commit.dirty_files = []` for **44/44**; `commit.sha` = `7b07e1cb…` for the 13 original-CORS records and `310d8b65…` for the 31 combined records (**0** mismatches against the manifest group); **0** failed checks; **265 pass + 6 expected n/a = 271** assertions (the 6 n/a are 2× `"not checked for client 'api'"` and 4× `"not checked for client 'browser'"`, i.e. declared not-applicable, not failures and not re-scored as passes). Clients/levels: **36 × (V2, api, sim)** + **8 × (V3, browser, sim)**.

**Fresh-outcome arithmetic reproduces exactly:** 14 auth (6 API V2 + 8 real Chromium V3) = 114 checks = 108 pass + 6 n/a; 3 root/info API = 20; 13 combined CORS = 65; 1 unreachable API = 7 → **31 outcomes, 206 checks = 200 pass + 6 n/a**; plus the 13 original CORS at 65 checks → 44 records / 271 checks. 32 screenshots accompany the 8 browser V3 records; **every** screenshot referenced by a record exists, is listed in the manifest, and hashes to the manifest value (0 missing, 0 unlisted, 0 byte differences).

**No old failure or diagnostic imported:** the historical CI failure `docs/validation/runs/software-waves/SW-API-CLIENT-02-C1/failed-ci/2026-10-20-V2-a7818f20-failures.unreachable_switch-api.json` is **byte-identical base → candidate** (37,876 B, SHA-256 `a3ff5c68c366334e6b0c647396745ffa5e9021fa00219be1c6bdf358eb490a04`, `result = fail`, `gate = regression`, `linked_finding = null`) and is **not** imported. No diagnostic-campaign record was imported (all 44 imports match the accepted clean campaign or the delivery roots byte-for-byte).

**Source tree integrity:** all **nine** accepted functional source blobs are present at the candidate with Git blob OIDs **identical** to the base **and** to their accepted functional-source commits — CORS `7b07e1cb`: `tools/validate/clients/api.py`, `tools/validate/model.py`, `tools/validate/runner.py`, `tools/validate/stack.py`, `tests/validation/scenarios/sw_api_read_04.py`, `tests/validation/test_sw_api_read_04.py`; offline `3788353e`: `src/rest_api/control.py`, `tests/sim/test_sim_rest_reads.py`, `tests/sim/test_sim_offline_switch_events.py`. The two prior independent review reports are present byte-identical to their review commits (`c8910ee5`, `0bd3d76f`).

**Verdict Q1: ACCEPT** (no finding against byte-exactness, manifest coverage, LFS OIDs, attribution, digests, dirty state, or the nine functional blobs).

### 5.2 Question 2 — allowed feature-field diff, the single V1→V2 advance, client mapping, strongest claim vs actual checks

**Measured registry diff:** 268 features before and after. **17** feature rows have any changed field:

| Feature | Changed fields | Authorized? |
| --- | --- | --- |
| `F-API-002` | `basis`, `evidence` | yes |
| `F-API-031` | `basis`, **`current`**, `evidence` | yes |
| `F-API-033` | `evidence`, `findings` | yes |
| `F-API-034` | `findings` | yes |
| `F-REL-009` | `claim` (corruption), `evidence`, `findings` | row yes / `claim` is F-01 |
| `F-SEC-007` | `basis`, `evidence` | yes |
| `F-SEC-014` | `findings` | yes |
| `F-REL-005`, `F-REL-015`, `F-REL-018`, `F-UC-008`, `F-UC-009`, `F-UC-011`, `F-UC-012`, `F-UC-013`, `F-UC-014`, `F-UC-016` | `claim` only (corruption) | **no — F-01** |

**Levels/targets:** features whose `target` changed anywhere in the file: **none**. Features whose `current` changed: **`F-API-031` V1 → V2 only**. `F-SEC-007` remains **V3** (target V3); `F-API-002` remains **V2** (target V2); `F-API-031` is now **V2** against target **V2**.

**`F-API-031` V1→V2 rests on the actual 13 header assertions.** The scenario `sw_api_read_04.py` defines 13 cases (`default_no_origin`, `default_same_origin`, `default_denied_origin`, `default_preflight`, `default_no_origin_preflight`, `default_denied_mutation`, `configured_allowed`, `configured_denied`, `configured_allowed_preflight`, `configured_denied_preflight`, `wildcard_origin`, `wildcard_no_origin`, `wildcard_preflight`) with `features=("F-API-031",)`, `clients=("api",)`, `targets=("sim",)`. The 13 imported original-source records and the 13 imported combined-source records each carry **5** checks per case, namely: response status + exact header equality/absence (e.g. `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`, `Access-Control-Max-Age`, `Vary`, `Access-Control-Allow-Origin` equal; `Access-Control-Allow-Credentials` absent; and for denied-origin cases `Access-Control-Allow-Origin` absent), `device otherwise unchanged`, `no write command reached the device`, `simulator raised no protocol warnings`, and the WebSocket schema-contract check. The **denied mutation** case returns **HTTP 403** with all six CORS headers absent. The new `basis` text — *"configured/default/wildcard origins, preflight header equality and absence, denied mutation, unchanged device state and no write commands"* — is **exactly** what the assertions demonstrate; no stronger claim is made ("does not qualify browser, deployed-image, hardware, soak or field targets").

**Client mapping (`Scenario.features_for(client)`) verified per record, 44/44:** every record's `features` set equals `Scenario.features_for(record.client)` and every record's `covers` tuple equals `Scenario.covers` — **0** mismatches, **0** records whose client is not in the scenario's `clients`. Concretely: `sw_api_read_04.*` → `("F-API-031",)` for the `api` client only; `contracts.api_info` / `api_root` / `api_root_alias` → `("F-API-002",)`; `sw_sec_auth_01.*` and `security_hardening.*` → `("F-SEC-007",)`; `failures.unreachable_switch` → `("F-REL-009", "F-API-033")` for the `api` client only (its `client_features` is `{"api": ("F-API-033",)}`, so `features_for("browser")` is `("F-REL-009",)`).

**`F-API-033` / `F-REL-009` remain named API refreshes, not target qualification.** `F-API-033` target V3 / current V2 (unchanged); `F-REL-009` target V4 / current V3 (unchanged); `F-API-034` target V3 / current V2 (unchanged, no new scenario or level claim, only the `VAL-14` finding link). Their `basis` strings still describe the existing scenario/unit-test proof and were not upgraded.

**Verdict Q2: HOLD on this exact candidate** — solely because of **F-01** (10 out-of-scope rows changed, all by encoding corruption). Every substantive part of Q2 passes: the only level advance is `F-API-031` V1→V2 on the real 13 header cases, `F-SEC-007` stays V3, `F-API-002` stays V2, no target was lowered, and the client mapping is exact.

### 5.3 Question 3 — VAL-14 and VAL-15 semantics

**VAL-14** (M, open): *"Already-disconnected routing requests omitted documented failure events"*, location `src/rest_api/control.py`, proof points at `SW-API-CLIENT-02-C1/FINDING.md`, the original failed CI bytes, the accepted correction at `3788353e`, the independent review `0bd3d76f`, the fresh `310d8b65` unreachable scenario and 18 offline regressions. Disposition: *"Source correction independently accepted; formal closeout awaits final assembly review and combined CI/publication. No V3 target promotion or historical failure waiver."* — **matches the required wording**: medium/open, source correction independently accepted, final CI/publication still pending, linked to `F-API-033`, `F-API-034` and `F-REL-009`, and the historical failed-CI record is neither re-labelled nor imported (verified byte-identical, `gate = regression`, `linked_finding = null`).

**The imported offline record asserts the corrected behaviour, and its boundaries are not conflated.** `failures.unreachable_switch` at `310d8b65` passes 7 checks: HTTP ≥ 500 with `success: False` (observed **500**), `device outputs[0].source == 2`, `device otherwise unchanged`, **WebSocket event `switch_failed` with `{'input': 3}`** (the check the historical record failed), `GET /api/health → data.matrix.connected == False`, `GET /api/status → success == False` (linked `VAL-04`), plus the WebSocket schema-contract check. Its scenario `covers` include `src/rest_api/control.py`, so the finding is tied to the right code path. It is an **API** record (`clients=("api",)`), and `F-API-034`'s `switch_all_failed` remains explicitly **V1 / "no scenario yet"** in the basis — the ordinary-unreachable scenario and the 18 focused regressions are not presented as interchangeable.

**VAL-15** (M, open): *"Validation request artifacts and action descriptions do not redact X-Admin-PIN"*, location `tools/validate/evidence.py` and `tools/validate/model.py`, proof `SW-SEC-DATA-02-C1/FINDING.md`. Disposition: *"Reproduced with synthetic markers only; not an observed owner credential leak or a finding against all product logging. Corrective package SW-SEC-DATA-02-C1 remains undispatched."* — **matches the required wording**: it is scoped to validation request artifacts / action descriptions, is explicitly **not** an observed owner credential leak, is **not** a finding against all product logging, and the corrective child remains **unimplemented and undispatched**. The row is linked to `F-SEC-014` only (whose `current` stays V1, target V3, evidence `[]`).

**No assertion weakening, target lowering, cap waiver, owner gate or baseline change** is present: the diff contains no `tools/` or `tests/` byte at all, no feature `target` changed, no `capped_by`/cap logic was touched (the tool is unchanged), `findings_pending.yaml` adds only two open M rows with no owner/approval field, and the only `current` change is the evidence-backed `F-API-031` V1→V2.

**Verdict Q3: ACCEPT.**

### 5.4 Question 4 — the regenerated ledger 268 / 210 / 96 vs the previous 203 / 57

**The committed ledger is honestly generated, not hand-edited.** A fresh `python -m tools.validate ledger` at the candidate reproduces `docs/validation/LEDGER.md` **exactly**: the only differences are the `> Commit \`78ce3448\`` stamp (the committed file was generated at the base `28fce729` and then committed on top of it) and the evidence-link base, which is an artifact of my `--out` path lying outside `docs/validation/` (167 changed lines, every one of them that link rewrite; **no** content difference). The committed summary is `| **All** | **268** | **18** | **122** | **32** | **96** | **0** | **0** | **210** | **96** |`, with "Features with fresh passing scenario evidence: **70** of 268", "Features with a fresh failing scenario: **0**", "Features capped at V1 by an open critical/high finding: **12**". The previous committed ledger (base) carries the stamp `141bffb2` and `| **All** | **268** | **15** | **113** | **34** | **106** | **0** | **0** | **203** | **57** |`.

**Why the count moved — measured, not asserted (it is not 38 new defects).** I parsed the per-feature rows out of the **two generated ledger files themselves** (the base ledger, stamp `141bffb2`, and the candidate ledger, stamp `28fce729`) and diffed them (`build/fanout-readiness-20261028/review/ledger-attribution.txt`):

| | base ledger (stamp `141bffb2`) | candidate ledger (stamp `28fce729`) |
| --- | ---: | ---: |
| features | 268 | 268 |
| below target | **203** | **210** |
| stale evidence | **57** | **96** |
| features with fresh passing scenario evidence | 108 | 70 |
| features with a fresh failing scenario | 0 | 0 |
| capped at V1 by an open critical/high finding | 12 | 12 |

- **Freshness flips: 40** — **39 `fresh → stale`** and **1 `— → fresh`**. The single `— → fresh` is **`F-API-031`**, i.e. the only feature that gained fresh proof, and it is exactly the feature whose 13 cases were imported. The `+39` stale count equals the 39 `fresh → stale` flips exactly.
- **Level changes: 15 features** — 14 fall back from their previously proven level to their recorded baseline (because their only fresh proof went stale), and 1 (`F-API-031`) rises V1→V2. **7** of those 14 drops cross their target, which is exactly the `+7` below-target movement (203→210).
- **Cause.** Staleness is defined mechanically by `tools/validate/gitinfo.py::changed_since` as `git diff --name-only <evidence commit>..HEAD` over the scenario's `covers` paths, so it is always measured against the **current** tree. Between the old report's stamp `141bffb2` and the base `28fce729`, **11 non-docs paths** changed, of which **8 are covered by scenarios**:
  - `src/rest_api/control.py` — covered by **217 scenarios** (the wave03 offline-routing correction);
  - `tools/validate/clients/api.py`, `tools/validate/model.py`, `tools/validate/runner.py` — 23 scenarios each;
  - `tools/validate/stack.py` — 15 scenarios;
  - `tests/validation/scenarios/sw_api_read_04.py`, `tests/validation/test_sw_api_read_04.py` — 13 scenarios each;
  - `tests/sim/test_sim_rest_reads.py` — 2 scenarios (`contracts.api_root`, `contracts.api_root_alias`);
  - `.gitattributes` and `AGENTS.md` — covered by 0 scenarios (no effect).
  The 39 flipped features are exactly the ones whose scenarios cover those paths (`F-HA-001…018`, `F-UI-002/004/005`, `F-KIO-002/003`, `F-MTX-002/004/021/030`, `F-FLIC-001/002/008`, `F-REL-001/005`, `F-DOM-026/034`, `F-API-005/007/008/013/034/035`).
- **Nothing was fabricated, re-scored or hidden.** The evidence diff base→candidate is **76 additions and nothing else**; no old record was modified or deleted; no fresh failing scenario exists in either ledger; no finding was closed. The change is a **re-computation of covered-path staleness against previously merged source**, and the wider qualification stays pending.

**The packet does not over-claim.** `docs/validation/W03_EVIDENCE_ASSEMBLY.md` states the 268 / 210 / 96 numbers, names the previous 203 / 57 report as *predating* the source changes, says "existing rows and stale records are preserved, with no fabricated refresh", and says "Do not require broad unrelated evidence promotions to accept this bounded metadata import" in effect by keeping "wider qualification pending". The ledger also shows **0** features with a fresh failing scenario, and the two new findings are M (medium), so they do not cap any level.

**Verdict Q4: ACCEPT** — the numbers are the honest output of the unchanged generator against the current tree, and the change is wider covered-path staleness, not new defects.

### 5.5 Question 5 — independent validation actually run, with raw counts and limits

**Actually run by this reviewer, at the candidate, with fresh output:**

| Check | Result |
| --- | --- |
| `python -m tools.validate check` (committed evidence) | exit **0** — `gate OK (0 known failure(s) linked to open findings)` |
| `python -m pytest tests/validation/test_registry.py tests/validation/test_evidence_schema.py tests/validation/test_ledger.py` | exit **0** — **42 passed** |
| `python -m pytest tests/test_openapi_and_config_docs.py tests/test_core_documentation.py` | exit **0** — **65 passed** |
| `python -m tools.validate ledger --out <own scratch>` (serial, after the registry checks) | exit **0**; committed ledger reproduced exactly |
| Manifest/blob/LFS/original-source byte checks | 76/76 byte-exact; 44/44 JSON SHA-256 match; 32/32 LFS OID + size match; 32/32 worktree PNG SHA-256 match |
| Evidence schema + content checks (own helper, `jsonschema`) | 44/44 schema-valid; 0 failures in every negative class |
| Registry diff map + encoding scan | 17 changed feature rows; **1** defective file (F-01) among all 82 changed paths |
| Ledger markdown links | 367 links; **0** genuinely broken (the single naive-checker hit is `README.md#recorded-baseline-c-pre-2026-09-25`, an anchor whose target file exists); 10/10 W03 evidence links resolve |

**Raw counts:** 44 imported records / 271 checks / 265 pass + 6 expected n/a / 0 failed; 36 (V2, api, sim) + 8 (V3, browser, sim); 44 null image digests; 44 clean `dirty`/`dirty_files`; 0 scenario/feature/covers mismatches; 0 missing or unlisted screenshots; 9/9 functional blobs identical; 42 + 65 tests passed; formal gate exit 0.

**Limits — stated honestly, not waived:**

- The **4,084-test core suite, 100 dedicated Remote tests, Ruff, mypy (91 files), 177/177 strict REST route coverage, current-head CI, image and broader-client gates were not re-run** by this reviewer. The candidate diff contains **zero** source, test, tooling, UI, root-manifest or lockfile bytes, so those results retain their original attribution and date; the packet's claim about them is carried forward, not re-verified here. No new concern arose that would justify re-running them.
- The **31-outcome campaign was not re-executed**; the imported bytes are the delivered ones, verified byte-for-byte against the original delivery tree and the original clean campaign tree.
- The **underlying CORS / offline-routing source behaviour was not re-reviewed**. The nine functional blobs are byte-identical to the accepted functional sources, so any source-level defect remains attributable to the prior independent reviews (`c8910ee5`, `0bd3d76f`) and to the original authors, not to this metadata packet.
- The `docs/production/AGENT_ALLOCATION.md` fleet/quota/provider observations (Orca version, fleet census, MiniMax/Codex remaining usage, DeepSeek/Antigravity unknowns) were **not** independently attested by this reviewer; only the recorded Git/Run references were checked, and `origin/wp-runtime-completion = 411c6642…` still matches the entry.
- Physical HIL, deployment-host 72-hour soak, week owner field use, and final version/artifact release acceptance remain **open and untouched** by this review. The three Tron paused-frame owner approvals closed on 2026-10-20 are **historical and unchanged** by this review; they are not re-granted and are not a release approval.
- Three optional helpers of mine were interrupted or stopped and replaced (see §6): the `check_manifest.py` B2 sweep (interrupted by the coordinator) and the two attribution recomputations (stopped by me for budget). None of their incomplete outputs is counted as a pass; each question they targeted was answered instead by a completed, cheaper equivalent proof — respectively the `git diff --name-status` evidence-namespace proof plus the 76/76 original-source byte comparison, and the direct comparison of the two committed generated ledgers.

**Verdict Q5: ACCEPT** (the checks actually run are meaningful, independent and green; the declared non-verifications are recorded rather than implied).

---

## 6. Owned background jobs — exact disposition

| Job | Owner | Disposition |
| --- | --- | --- |
| `check_manifest.py` B2 "base-byte lookup" sweep | this reviewer | **Interrupted, not PASS.** The coordinator positively identified and stopped only this task-exclusive probe (launcher PID 34388 / child PID 44108; receipt `build/fanout-readiness-20261028/reviewer-optional-probe-stop.json` **in the root repository** `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration`, recording `"scope": "exact Python launcher/child chain for reviewer optional read-only check_manifest.py"`, `"reason": "bounded review: duplicated 44x full old-evidence scan; preserve partial output; other review checks already independent"` and `"workerAndSharedServicesUnchanged": true`). Its optional output was not used. It was **replaced** by two completed, cheaper equivalent proofs: the `git diff --name-status BASE CANDIDATE -- docs/validation/evidence` proof (76 `A`, 0 non-`A`) and the direct original-source byte comparison (76/76 byte-identical). |
| `check_ledger_attribution.py` (four-case, un-cached) | this reviewer | **Stopped by this reviewer.** After ~10 minutes of wall-clock (child `python3.12` at 207 s CPU, no output) the helper was judged non-converging because it spawned three git subprocesses per evidence record. It was stopped (launcher PID 66416), then a cached replacement was started. Its partial output was empty and is **not** counted as a result. |
| `check_ledger_attribution_fast.py` (cached replacement) | this reviewer | **Stopped by this reviewer** after ~22 minutes (child `python3.12` at 340 s CPU, no output). Its `fnmatch`-heavy per-record coverage test was the remaining cost. It produced no output file and is **not** counted as a result. |
| `check_ledger_compare.py` (final, cheap replacement) | this reviewer | **Completed, exit 0.** Replaced both attribution helpers with a direct comparison of the two **generated** ledger files plus a scenario-coverage map of the changed paths. This produced the decisive attribution quoted in §5.4 (40 freshness flips, 15 level changes, 11 changed non-docs paths and their covering scenarios) at a fraction of the cost, without simulating a diff endpoint. |

**Disposition of the interrupted helpers:** both were optional, both were mine, both were stopped deliberately rather than left running, and neither result is claimed. The attribution question they were built to answer was answered instead by `check_ledger_compare.py`, which reads the two committed generated reports directly — a *stronger* evidence source than a re-simulation, because it compares the artifacts that were actually committed.

No other worker's process, the shared OpenCode server, any minimax MCP process, any other workspace, or any repository outside this worktree was touched. No push, merge, tag, cleanup, branch deletion or worktree removal was performed. **No background job of this reviewer was left running at settlement**: after the final stop, a process sweep for `*check_ledger_attribution*` returned only the transient PowerShell wrapper of the sweep command itself, and no `python.exe` of this reviewer remained.

**Incidental ignored artifacts.** Running the required checks created Python bytecode caches (`__pycache__/` directories under `scripts/`, `src/`, `tests/`, `tools/`) in this worktree. They are git-ignored, contain no unique data, and were left in place rather than deleted, because cleanup is explicitly out of scope for this task. No tracked file, and no file under `docs/`, was modified by this review other than the addition of this report.

### 6.1 Attribution helper — final result and residual limit

The attribution is **complete and decisive**, obtained by comparing the two committed **generated** ledger reports rather than by re-simulating a diff endpoint (see §5.4 and `build/fanout-readiness-20261028/review/ledger-attribution.txt`): **40** freshness flips (**39** `fresh → stale`, **1** `— → fresh` = `F-API-031`), **15** level changes (**14** falling back to the recorded baseline, **1** rising `F-API-031` V1→V2), `+39` stale and `+7` below target, and the changed non-docs paths between the old stamp `141bffb2` and the base `28fce729` with the scenarios that cover them (`src/rest_api/control.py` → 217 scenarios; `tools/validate/{clients/api,model,runner}.py` → 23 each; `tools/validate/stack.py` → 15; `tests/validation/{scenarios/sw_api_read_04.py,test_sw_api_read_04.py}` → 13 each; `tests/sim/test_sim_rest_reads.py` → 2).

**Residual limit (honest):** the two *stopped* helpers would additionally have re-derived the old 203/57 figures by re-running the generator against a simulated `141bffb2` diff endpoint. That re-derivation was **not completed and is not claimed**. It is not needed for the disposition: the old 203/57 figures are read directly out of the committed base ledger (stamp `141bffb2`), and the new 210/96 figures are reproduced exactly by a fresh regeneration of the unchanged generator at the candidate (§3 rows 14–16). What the completed comparison establishes is that the difference between the two committed reports is **entirely** covered-path staleness against the source merged in between, plus the single new `F-API-031` proof — not new defects, not deleted or re-scored records.

---

## 7. Report checks performed before commit (report-only gate)

- The report is a single new file, `docs/production/software-waves/W03-CLOSEOUT-20261028/REVIEW.md`; no other tracked path is touched by this review's commit.
- Local Markdown targets and anchors used by the report resolve (repository-relative paths cited were checked to exist); no absolute host paths are used as links.
- CR-aware whitespace check: no CR bytes, no trailing-whitespace lines, final newline present.
- Path-character check: all cited repository-relative paths use plain ASCII and exist at the candidate.
- Non-ASCII: the report contains no mojibake-prone byte sequence. Measured inventory: `§` (U+00A7) ×25, `×` (U+00D7) ×5, `–` (U+2013) ×2, `—` (U+2014) ×55, `…` (U+2026) ×12, `→` (U+2192) ×37, `≥` (U+2265) ×1 — **0** occurrences of U+00C2 and **0** of U+FFFD (the exact corruption markers reported as F-01). Every non-ASCII character in the report is intentional and is used as a single, correctly encoded code point.
- Commit made with an invocation-scoped hook exception (`git -c core.hooksPath= commit …`); the persistent hook configuration was not changed and no implementation hook was bypassed.

---

## 8. Disposition

**HOLD — candidate `78ce344800a9d1b3088bb8e886f65e2c8dfa0918` as-is.**

**One required correction (coordinator-authored, coordinator-owned metadata):** repair **F-01** — restore the 14 corrupted lines in `docs/validation/features.yaml` to their base single-`U+00A7` encoding so that the registry diff is limited to the seven authorized feature rows and their intended fields. This is a mechanical re-encoding of `docs/validation/features.yaml` only; no evidence byte, manifest, ledger number, finding row, level or target changes.

**Everything else is accepted at this exact candidate**, on the evidence recorded above:

1. 76/76 imported files byte-identical to the READ-ONLY originals (13 original CORS + 31 combined + 32 screenshots), with independent SHA-256 cross-match against the inventory report table; 44/44 JSON SHA-256 match the manifest; 32/32 git-LFS OIDs and sizes match the manifest; 32/32 working-tree PNG SHA-256 match.
2. 44/44 records schema-valid, all `pass`/`gate ok`, all `image_digest` null, all `dirty=false`/`dirty_files=[]`, source attribution correct per group, 265 pass + 6 expected n/a, 0 failed checks; `features`/`covers` match the live scenario registry for all 44; every screenshot reference resolves and is manifested.
3. All nine accepted functional source blobs and both prior independent review reports are present and byte-identical; the whole diff is confined to `docs/`; no source, test, tooling, UI, root-manifest or lockfile byte changed; the historical failed-CI record is untouched and not imported.
4. The only recorded level advance is `F-API-031` V1→V2, backed by the real 13 header-assertion cases; `F-SEC-007` stays V3, `F-API-002` stays V2, no target lowered, `F-API-033`/`F-REL-009`/`F-API-034` remain named API refreshes.
5. VAL-14 and VAL-15 are medium/open with the required wording, the required links, no historical-failure waiver, no owner-leak claim, no all-product-logging claim, and the VAL-15 corrective child still undispatched.
6. The 268 / 210 / 96 ledger is the honest output of the unchanged generator at the current tree; the 203 / 57 predecessor predates the merged source; no fabricated refresh, no deleted old record, no new defect.
7. Independent validation actually run: formal gate exit 0 with 0 known failures, 42 metadata tests passed, 65 documentation/config tests passed, committed ledger reproduced exactly by a fresh scratch regeneration.

**Reviewer disposition:** bounded **metadata** review at the exact candidate, performed by a different underlying model family from the author (MiniMax M3 / thinking vs OpenAI). This disposition covers **only** the canonical-evidence metadata of `78ce3448`. It is **not** a core or security source-review qualification, **not** an image/browser/hardware/soak/field qualification, **not** a release approval, and **not** a pre-approval of any future evidence, CI or publication gate. Reviewers report; the coordinator authors the fix in its owned metadata.
