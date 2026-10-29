# SW-AUDIT-01 / SW-CLI-FLIC: independent bounded evidence-metadata review

**Disposition: ACCEPT** the bounded functional/evidence inventory at exact candidate `67d80ae997a988ce6d9983d541205e8ca432a57c`, **with PRIVACY / ARTIFACT-ADMISSION HOLD preserved and unchanged**. This review confirms inventory and metadata only. It clears no privacy gate, no canonical admission, no new feature qualification and no physical acceptance.

## Authority, reviewer scope and limits

- Run `run_37205f6095b3`; Task `task_c20c74f1c8fa`; Dispatch `ctx_6855b88f3e18`; reviewer terminal `term_9d0fcb9d-6b31-46d6-901d-7a65958dc58b`; coordinator `term_dcf96b5a-bb99-4ecb-b887-eb53f7f01662`.
- Reviewer worktree `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-flic-proof-review`, branch `ryan-haver/wp-flic-proof-review`, clean base and HEAD `67d80ae997a988ce6d9983d541205e8ca432a57c`.
- Reviewed subject: the author report `docs/production/software-waves/SW-AUDIT-01/FLIC_REFRESH.md` at that candidate, against the read-only private attempt `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-flic-proof-refresh/build/software-waves/SW-AUDIT-01-flic-refresh/attempt-01/` on the same host.
- Author attribution: OpenAI `gpt-6.1-sol` / high (author receipt `task_442e2245e0a1`, Dispatch `ctx_33cdb9118f04`, worker `term_2085a94f-b9c4-4a36-9823-4497561dc5b7`).
- Reviewer qualification: native MiniMax-M3 / thinking, **bounded inventory and evidence metadata only**. This is explicitly **not** a source code review, **not** a privacy review, and **not** a different-family review. It therefore cannot satisfy the different-family code/privacy gate for `source11f`, cannot clear the VAL-15 free-form Action/Response gaps, and cannot grant privacy clearance. No Anthropic, helper, nested worker, model substitution, global configuration change or dependency install was used.
- Method: read-only recomputation over the four-record inventory and its metadata receipts. **No test or validation campaign was rerun, no service was started, no source/contract/registry/ledger/finding/canonical-evidence file was modified, and no script supplied in the artifact input was executed.** Declarative scenario metadata was re-derived by importing only the pinned scenario declarations from the reviewed checkout (the candidate's `src/`, `tools/`, `web/`, `tests/` and `docs/api/` tree was verified byte-identical to the run's source commit).
- Exclusive writes: this report and the new ignored `build/software-waves/SW-AUDIT-01-flic-review/` subtree. Everything else was read-only.

## Verification inventory

90 independent checks were executed (81 PASS, 9 INFO, **0 FAIL**): 70 in `scripts/02_verify.py` (manifest, records, provenance, run/check, privacy, report attribution, transport, WebSocket counts, author audit) and 20 in `scripts/05_remaining_checks.py` (report hygiene, links, scope, fingerprints, open gates). Declarative re-derivation is in `scripts/04_declarative_compare.py`; the structure probe is `scripts/01_explore_structure.py`. Machine output is retained under `build/software-waves/SW-AUDIT-01-flic-review/attempt-01/out/`.

### Final manifest and retained bytes

| Item | Expected | Recomputed | Result |
| --- | --- | --- | --- |
| `artifact-hashes-final.json` SHA-256 | `d474cf5ecbbfd6c3e396439223da883ced8f1750fa7bd6b89d970f673c897134` | identical | PASS |
| Manifest members | 36 | 36 | PASS |
| Member byte length + SHA-256 (all 36) | match | all match | PASS |
| Attempt files not indexed | manifest only | 37 on disk = 36 indexed + the manifest itself | PASS |

Every byte the manifest indexes is present and unmodified; nothing indexed is missing, and no unindexed file other than the manifest itself exists in the attempt root.

### The four records

All four records are genuine `client=flic`, `target=sim`, `level=V3`, `result=pass`, `gate=ok` artifacts. Byte length and SHA-256 match the author table and the manifest exactly:

| Record | Bytes | SHA-256 (recomputed) | Report table |
| --- | ---: | --- | --- |
| `evidence/F-FLIC-001/2026-10-29-V3-865ec9c6-flic.preset-flic.json` | 43315 | `ecb55542ac239f383c26ec8da569d1b2f8d1c64909cfe11a2549a068a9c090ff` | identical |
| `evidence/F-FLIC-002/2026-10-29-V3-865ec9c6-flic.power_off-flic.json` | 33723 | `28a4934b2b511784feb97a84345d6ff9427977bf5c3168bf8806402eca51e1e4` | identical |
| `evidence/F-FLIC-002/2026-10-29-V3-865ec9c6-flic.power_on-flic.json` | 33497 | `a12583e4e6ba0a88ab87273fd4484c4d8ccba5dd344bb24d4e5b5cac5c678355` | identical |
| `evidence/F-FLIC-008/2026-10-29-V3-865ec9c6-flic.all_outputs-flic.json` | 37907 | `a31bd1d180ee14e29f6d250d220dc3724eade9eda6f98992988c87796458bc8d` | identical |

Assertion inventory recomputed from the records themselves: **26 checks = 25 pass + 1 n/a + 0 fail**, distributed 6 / 7 / 6 / 7 across preset, power-off, power-on and all-outputs, exactly as the report states. No record carries a blocked reason, a finding, a linked finding, a note, a screenshot or an operator observation. The single n/a is the inherited `WsEvent("power_change", {"power": "off"}, clients=("api",))` expectation in `tests/validation/scenarios/power.py:21`, restricted to the `api` client — precisely the report's explanation, and the reason the four power-off `pass` assertions still stand.

### Declarative re-derivation against the pinned source

Scenario declarations were re-derived from the reviewed checkout and compared field by field:

- **Features**: `flic.preset` → `F-FLIC-001, F-FLIC-010`; `flic.power_off` and `flic.power_on` → `F-FLIC-002, F-FLIC-010`; `flic.all_outputs` → `F-FLIC-008, F-FLIC-010`. Identical in declaration, record and report.
- **Covers**: the declared ordered `covers` tuple matches each record's ordered `covers` array exactly, **including the repeated entries inherited through `_replay`** (lengths 32 / 25 / 25 / 33, duplicates preserved). The report's distinct common-path list and its per-scenario additional-path lists match the records exactly.
- **Titles**: every record's `scenario_title` equals the declared title.
- **Expectation descriptions**: every declared expectation description appears in the corresponding record, and the only description beyond the declaration is the client-injected `every WebSocket message follows docs/api/websocket.schema.json`. The report's per-scenario check lists are a faithful rendering (it adds sentence-final punctuation to each description).
- **State deltas**: the `state_diff` paths match the declared `DeviceUnchanged(allow=...)` allowances in each case (`outputs[*].source` + `routing` for preset and all-outputs; `system.power` for the two power cases).

### Generated drawer / Node action transport versus the API helper

The central functional claim — that the action request is genuinely produced by the shipped drawer generator through the Flic client's own transport, and not by the runner's `ApiClient` helper — is supported by the artifacts and by the pinned source:

- Each record carries exactly one request, and the method/path/status match the report's table: `POST /api/preset/3` → 200; `POST /api/power/off` → 200; `POST /api/power/on` → 200; `POST /api/switch` → 200.
- Every request's `metadata.request_type` is `generated_drawer`, and its `metadata.drawer_source_sha256` is `7611f24baea47c81496ef18a57172d72e819c48fb5593f40d178e41fb87d6224`, which equals the recomputed SHA-256 of `web/js/components/integrations-drawer.js` at the reviewed checkout. `client_diagnostics.success` is true with no error in all four records.
- `tools/validate/clients/flic.py` states that it "Does NOT inherit from or delegate to ApiClient; owns its request builder and HTTP transport" and "Executes real updateFlicOutput and updateFlicSdkSnippet via narrow Node driver (flic_driver.mjs)"; its `build_drawer_request()` shells out to that Node driver and consumes the returned method, path and body.
- `tools/validate/runner.py` instantiates one `ApiClient` helper used for setup and readback only — the recorded procedure steps are `setup (api)` and `snapshot the matrix state (readback)`, and hub readbacks are collected separately. The helper does not carry the action request.

### WebSocket schema coverage

Message counts were recomputed from `observations.ws_events` lengths: **13 / 4 / 4 / 11** for preset / power-off / power-on / all-outputs. These match the report exactly, and the report correctly presents them as message counts rather than additional assertions.

### Provenance, environment and node facts

- The run summary and every record attribute a clean tree (`dirty=false`, `dirty_files=[]`) to source `865ec9c6d0df56e0a0b72dcaee8cc0b5c95f468b`; `invocation-environment.json` carries the same `source_sha`. That object is a commit in this repository and the **sole parent** of the candidate `67d80ae997a988ce6d9983d541205e8ca432a57c`. `git diff 865ec9c6 67d80ae9 -- src tools web tests docs/api` is empty: the candidate changed no code, only the report.
- All 64 digests in `covered-source-and-fixture-hashes.json` and all 15 digests in `invocation-environment.json` were recomputed on disk in the author checkout and match. The report's six quoted key digests (Flic client, Node driver, drawer, `api-copy.js`, `flic_replay.py`, Node executable) all match.
- Environment facts confirmed from the records and receipts: Python 3.12.10; `Windows-11-10.0.26300-SP0`; Node `v24.22.1` with executable SHA-256 `d702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5`; aiohttp 3.13.3; hub 2.10.0 / API 2.10.0; hub entry `run.py -> hub.cli shared runtime (UC_ENABLED=false)` with `UC_ENABLED=false` and `FLIC_ENABLED=true`; **no container/image digest claimed** (`image_digest` is null); simulator fingerprint `23f7439ea94f5fcc`, seed `tools/simulator/states/default.json`, BK-808 / firmware V1.10.01 / web V2.00.03 as simulator-reported metadata; templates `[integrations-drawer.js, api-copy.js, docs/FLIC_SETUP.md]`; node stubs "used for generated SDK callback replay (buttons/http and DOM/state)". `package.json` declares `engines.node ">=20"`. `sdk_version`, `physical_buttons` and `flic_sdk_runtime` are honestly recorded as `unknown` — no fabricated hardware observation.

### Run and supported check

`run-exit.json` = 0 and `check-exit.json` = 0. Both stdouts/stderrs are retained: the run stdout lists the four `PASS` lines in execution order (preset, power_off, power_on, all_outputs) and `done: {'pass': 4}`; the run stderr is empty; the check stdout is exactly `[validate] gate OK (0 known failure(s) linked to open findings)` and the check stderr is empty. Both recorded argvs and cwds match the report verbatim, including the absolute `--out` path and the author checkout as cwd.

The check scope is bounded exactly as the report states: `tools.validate check --evidence <private attempt>/evidence --run-summary <private attempt>/run-summary.json --expect-clients flic`. It carries no global release-acceptance flag; it validates the canonical committed evidence plus this one extra directory against the registry/finding/recorded-level regression logic and the run summary. It is **not** a global release acceptance test, and no ledger generation ran.

### Report attribution: CRLF and LF forms

Both attribution forms were retained and independently recomputed:

- Author worktree file, CRLF form: SHA-256 `fa99efc55c5df11f2a517eb9547286ddc688c674eb7cf5b2d84edb29e0142d7d` — **reproduced exactly** (15444 bytes, 173 CRLF sequences, 0 bare LF).
- LF-normalised content: SHA-256 `293088059c2e9627c7288478227aba12ecb1b051436097aec338a001a555c626` — **reproduced exactly** (15271 bytes).
- Round-trip CRLF → LF → CRLF is byte-identical to the file, so the two forms differ **only** by line endings. **No tampering is inferred from CRLF alone.**
- The Git blob object id at the candidate, `05467dfcb8ef4cdc3b12f589c16d8e74c5909835`, matches `closeout.json.report_git_blob`. The candidate commit touches exactly one file, the report itself.

### Privacy observation — bounded, HOLD preserved

Independently confirmed **by path, count and boolean only; no value was printed**:

- Exactly **8** unmasked `observations.state_before.auth.password` / `observations.state_after.auth.password` fields exist — two per record, in all four records. An independent raw-string scan of the record bytes finds the same total of 8 unmasked occurrences.
- All **8 of 8** compare equal to the checked-in simulator seed value in `tools/simulator/states/default.json` (`equal_count=8`, `evaluated=8`, `all_equal=true`).
- The author report contains no fixture-password value.
- The raw private bytes are **unchanged**: every record still hashes to its manifest digest and the 8 unmasked occurrences are still present — nothing was sanitized, rewritten, imported or published.
- The author's own classification agrees and itself records `privacy_review_complete=false`, `evidence_modified=false`, `values_printed=false`.

**This establishes fixture attribution, not privacy clearance.** The ARTIFACT ADMISSION / PUBLICATION HOLD stands exactly as the author left it. Privacy classification is an input to the coordinator's disposition, never an authority to clear privacy, and this review does not clear it.

## Findings, limits and observations

None of these block the bounded inventory; all are recorded for the coordinator's disposition.

1. **Private-attempt link is workspace-local (documentation limit).** The report links `../../../../build/software-waves/SW-AUDIT-01-flic-refresh/attempt-01/`. That resolves in the author checkout, but `build/` is git-ignored and the directory is private and unpublished, so the link does not resolve for a reader of the committed report. It should stay labelled as a private path in any canonical publication rather than being presented as a consumer-facing link. The other local link, `FRESHNESS_DELTA.md`, resolves in the reviewed checkout.
2. **CRLF/LF dual attribution — keep both forms.** The CRLF worktree SHA-256 and the LF content SHA-256 are both correct and mutually consistent by line endings alone. Both must be retained in any downstream record; neither alone should be treated as the canonical file identity, and CRLF must not be read as tampering evidence.
3. **Argv order versus execution order (precision, not defect).** The recorded run argv lists scenarios `all_outputs, power_off, power_on, preset`, while execution ran `preset, power_off, power_on, all_outputs` and the report describes the latter as the discovery order. Both statements are correct and mutually consistent; a downstream reader should not treat the argv list and the execution order as the same list.
4. **Scanner breadth is explicitly narrow (already disclosed by the author).** The retained conservative scan reports 8 sensitive-named and 8 unmasked fields, 2 WARNING / 0 ERROR / 0 CRITICAL log markers and 10 loopback URL occurrences. This is a narrow lexical scan, not a complete free-form-string audit, and it is not evidence that no owner credential appears anywhere in the retained bytes.
5. **Classification of the private diagnostic scripts is a coordinator judgment, not settled by this review.** The author characterises `private-invocation.py`, `private-inspection.py` and `private-report-invocation.py` as private invocation diagnostics rather than implementation or tooling deliverables. I did not execute them and express no view on their content. If the coordinator classifies them as tooling deliverables, the qualified different-family review requirement applies to them and is not met by this metadata review.
6. **This review is bounded by design.** It covers inventory and evidence metadata for this four-record set only. It re-derives declarations declaratively; it does not audit `tools/validate/clients/flic.py`, the Node driver, the drawer source, the runner, the evidence schema or the ledger generator for code quality, safety or privacy.

## Explicit non-claims and gates that stay open

- **Privacy / artifact admission: HOLD.** Eight unchanged simulator-fixture password fields remain in the raw private state snapshots. No privacy clearance, no canonical adoption, no import, no publication.
- **VAL-15** free-form Action/Response string gaps remain open; this review does not close them and grants no repair authority.
- **`source11f`** remains out of integration pending qualified different-family code/privacy review, which this metadata review does not provide.
- **F-API-034 / `switch_all_failed`** remains a separate, unchanged assertion gap. `tests/validation/scenarios/flic_replay.py` never claims `F-API-034`; `flic.all_outputs` carries `F-FLIC-008`, and the route-all proof in these records does not assert the disconnected `switch_all_failed` event/payload, 503, unchanged device or no routing write. `FRESHNESS_DELTA.md` still carries the gap.
- **The three Tron paused-frame owner approvals closed by the owner on 2026-10-20** remain historical, closed and not re-granted, extended or treated as released. This review reopens nothing.
- **No** new feature qualification, no source acceptance, no physical Flic Hub / SDK version / button / display / CEC / hardware observation, no visual baseline or visual approval, no browser or UI qualification, no HIL, no 72-hour soak, no week field sign-off, no final version or artifact release acceptance, no global release-acceptance claim and no ledger generation.
- V3 here is the existing runner's simulator/client level, not HIL attestation. These four cases are Node execution of the shipped drawer generator with narrow DOM/state stubs followed by local HTTP request replay and simulator device readback.

## Method and retained review artifacts

All review scripts and their machine output are confined to the new ignored subtree `build/software-waves/SW-AUDIT-01-flic-review/attempt-01/` (`scripts/`, `out/`). No failed diagnostic is discarded: the first verification pass surfaced five expectation-model errors in my own harness (trailing-period normalisation, request location under `observations.requests`, the full Python version string, and the string-typed `UC_ENABLED`/`FLIC_ENABLED` values); those attempts are retained and the corrected harness produced zero failures. No artifact-supplied script was executed at any point.

## Disposition

**ACCEPT** the bounded functional/evidence inventory and the author report's factual claims at exact candidate `67d80ae997a988ce6d9983d541205e8ca432a57c`: every functional, inventory, provenance, environment, transport, schema-coverage and attribution claim that this review could test was reproduced independently, with no discrepancy found. **PRIVACY and ARTIFACT ADMISSION/PUBLICATION HOLD remain in force** and are unaffected by this acceptance. Coordinator retains canonical admission, privacy disposition, artifact preservation and publication, worker release, sequential integration and all release gates.
