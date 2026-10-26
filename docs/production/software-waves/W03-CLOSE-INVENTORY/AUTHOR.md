# W03-CLOSE-INVENTORY — bounded preservation and evidence inventory

Task `task_feae2579595e`, Dispatch `ctx_82ee9bfe90aa`, existing Run
`run_37205f6095b3`; worker terminal `term_9f86e1f1-d613-488b-84a6-f47812d03542`.

- Exact base: `310d8b65a9fce3c9069523d4ac5ce21157e75c9f`.
- Own worktree: `wp-w03-close-inventory`, branch `ryan-haver/wp-w03-close-inventory`,
  HEAD `310d8b65a9fce3c9069523d4ac5ce21157e75c9f` (verified equal to the base
  before any work).
- Requested and observed effective route: native `minimax-coding-plan` /
  `MiniMax-M3`, **thinking** variant. **Native attestation:** the coordinator
  independently exported the session `ses_e85ada578ffeU6KEQv3Z3jI2ky` and
  observed every assistant message attributed to
  `MiniMax-M3` / `minimax-coding-plan` / `thinking`. That coordinator export
  is the execution-side attestation; a worker's self-report is **not** native
  attestation on its own and is not relied on here. No helper, subagent,
  fallback, broker, MCP server, Anthropic/Claude model or nested worker was
  used.
- Scope: **report-only bounded inventory.** No source, test, tooling, registry,
  ledger, finding, manifest, evidence, archive, quarantine or runtime change was
  made. This report does **not** qualify anything: it is not a core/security
  source review, not an evidence import, not a finding closure and not a
  release approval.

Exclusive writes performed by this task: this file only, plus ignored
`build/phase-resume-20261026/inventory/**` inside this worker's own tree.
The root repository `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration`
and the four older wave03 worktrees were read as **read-only evidence
sources**. Nothing under `C:/scripts/.../build/software-wave-03-20261020` or
any other archival destination was written, overwritten, moved or deleted.

---

## 1. Scope boundary and what this report is not

This task reconciles the *original bytes* of the accepted wave03 records, proves
that the accepted functional source blobs still exist in the integration base,
and inventories the preservation state of the four released wave03 workspaces.
It does not import records, does not relabel attribution, does not register or
close findings, does not regenerate a ledger, does not run the combined
pipeline, and does not authorise or perform cleanup.

Every record inspected is **client `api`, target `sim`, level `V2`, image digest
`null`**. Nothing here is browser/Remote/HA V3, image, physical HIL, 72-hour
soak, week field sign-off, Tron visual approval or final version/artifact
release evidence. No API-as-browser or API-as-image qualification is claimed or
implied.

---

## 2. Sources read

| Source | Role | Treatment |
| --- | --- | --- |
| `AGENTS.md`, `docs/ORCHESTRATION_PROTOCOL.md`, `docs/agent-process/state/HANDOFF.md`, `docs/validation/README.md` | standing rules and policy | read |
| `docs/production/software-waves/SW-API-READ-04-C1/AUTHOR.md` + `REVIEW.md` | header author + independent review | read |
| `docs/production/software-waves/SW-API-CLIENT-02-C1/AUTHOR.md` + `REVIEW.md` + `FINDING.md` | controller author + independent review + finding | read |
| `docs/production/software-waves/SW-SEC-DATA-02-C1/FINDING.md` | VAL-15 source | read |
| `docs/planning/software-waves/manifest.json` | 30 packages / 65 dispatch units / 268 features | read |
| `docs/validation/features.yaml`, `docs/validation/findings_pending.yaml`, `docs/REMEDIATION_PLAN.md` §4.10 | registry and finding registers | read |
| `C:/scripts/.../build/software-wave-03-20261020/**` | private preservation receipts, bundles, archives | read-only |
| `wp-sw-api-header-proof`, `wp-sw-api-header-review`, `wp-sw-api-offline-events`, `wp-sw-api-offline-review` build trees | original campaign records | read-only |

Machine-readable outputs (ignored, own tree only):
`build/phase-resume-20261026/inventory/records-inventory.json`,
`.../blob-survival.json`, `.../workspace-inventory.json`,
`.../record-tables.md`, and the three scripts that produced them
(`inventory_records.py`, `blob_survival.py`, `workspace_inventory.py`).

---

## 3. Commands actually run, with exits

Interpreter: the existing root virtualenv
`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`
(Python 3.12.10, Windows 11). No project import was needed, so no `PYTHONPATH`
override was required; where a project import could have been needed it would
have been process-local only. No test suite was executed: this task is
inspection-only, so `route_inventory` was never enabled or disabled.

| Command (own worktree) | Exit | Result |
| --- | --- | --- |
| `git status` / `git rev-parse HEAD` / `git branch --show-current` / `git worktree list` | 0 | clean tree; HEAD `310d8b65…`; branch `ryan-haver/wp-w03-close-inventory`; nine registered worktrees listed |
| `python build/phase-resume-20261026/inventory/inventory_records.py` | 0 | 57 evidence records inventoried across 8 declared sets |
| `python build/phase-resume-20261026/inventory/blob_survival.py` | 0 | 12 package paths checked at the base |
| `python build/phase-resume-20261026/inventory/workspace_inventory.py` | 0 | 4 worktrees + bundles + archives + publication receipts inventoried |
| `git cat-file -p <rev>:<path>` / `git rev-parse <rev>:<path>` (via the script) | 0 | blob identity at base, functional source, submitted candidate and report commit |
| `git status --porcelain` in each of the 4 wave03 worktrees | 0 | all empty (clean) |
| `git check-ignore -v build/phase-resume-20261026/inventory/probe.txt` | 0 | `.gitignore:7:build/` → own build tree is ignored |
| `python build/phase-resume-20261026/inventory/report_checks.py` | 0 | report-only pre-commit gate: structure, local links (0 markdown links, 0 broken), cited repository-relative paths (36 checked, 0 missing, 5 intentionally absent placeholders/proposed destinations), CR-aware whitespace (0 CR bytes, 0 trailing-whitespace lines, final newline present), path characters → PASS |
| `git rev-parse 310d8b65:docs/production/software-waves/SW-API-READ-04-C1/REVIEW.md` and the offline `REVIEW.md` counterpart, cross-checked against `c8910ee5` / `0bd3d76f` | 0 | both review blobs are present at the base and byte-identical to their review commits (corrects an earlier draft error) |
| `Get-ChildItem` / Python read of `wp-w03-close-evidence/build/phase-resume-20261026/evidence/**` and its receipts | 0 | 31 fresh combined records / 206 assertions inspected read-only (§6.5) |
| Python read of `build/project-file-cleanup-20261022/reversible-relocation-plan-complete.json` and `verified-quarantine-post-state.json` | 0 | both original external temp roots relocated reversibly into quarantine; quarantine copies confirmed present on disk |

This commit is **report-only**: one new file,
`docs/production/software-waves/W03-CLOSE-INVENTORY/AUTHOR.md`, and no other
tracked change. It uses the documented **invocation-only** hook exception
(`git -c core.hooksPath= commit …`) after the real checks above. No
implementation hook was bypassed: no source, test, tooling, registry, ledger,
manifest, evidence or archive byte is in this commit, so no implementation
hook applies to it. The configured hook path
(`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.githooks`) was not
modified and no persistent hook configuration was changed.

Observed limits, stated honestly:

- A recursive sweep of the whole root `build/` tree for archives **timed out at
  120 s** (exit 124) because of the large EV-02/Playwright artefact trees. The
  archive sweep was therefore **re-run bounded** to
  `build/software-wave-03-20261020` only, which is the wave03 receipt
  directory; that bounded sweep completed and is the basis of §6. No claim is
  made about archives outside the wave03 receipt directory.
- No archive was re-hashed. All archive/bundle integrity statements come from
  the **existing** manifests and verify logs, as instructed; only existence,
  size and recorded receipt content were inspected.
- Junction/symlink targets inside the archived external temp roots were **not**
  followed; the recorded reconciliation states the archive preserves junction
  metadata without following it.

---

## 4. Reconciliation of the original records

### 4.1 Observed record sets (by actual run summary, not by summary prose)

`inventory_records.py` grouped every `evidence/**/*.json` found under each
declared root and read the record fields directly.

| Set | Role | Records | Assertions | `result` | Source SHA in the records | Branch |
| --- | --- | --- | --- | --- | --- | --- |
| A `SW-API-READ-04-C1/clean/campaign/evidence` | accepted functional-source campaign | **13** | **65** | 13 pass / 0 other | `7b07e1cb7e7eb29a38b55d3b050703149f1b797c` | `ryan-haver/wp-sw-api-header-proof` |
| B `SW-API-READ-04-C1-review/campaign/evidence` | independent reviewer campaign at the submitted candidate | **13** | **65** | 13 pass / 0 other | `cb87427bd2646fc686e1cff02692a4240dcf51c1` | `ryan-haver/wp-sw-api-header-review` |
| C `SW-API-READ-04-C1/diagnostic/campaign/evidence` | author **diagnostic** campaign, uncommitted source at the base | 13 | 65 | 13 pass / 0 other | `411c66429df3b813072e736c41c3a8aa83043a70` | `ryan-haver/wp-sw-api-header-proof` |
| D `SW-API-READ-04-C1/focused-tmp` | focused negative controls | 3 | 9 | 1 pass / **2 fail** | `411c6642…` | `ryan-haver/wp-sw-api-header-proof` |
| D2 `SW-API-READ-04-C1/focused2-tmp` | focused negatives + unrelated scenarios | 12 | 97 | 10 pass / **2 fail** | `411c6642…` | `ryan-haver/wp-sw-api-header-proof` |
| E `SW-API-CLIENT-02-C1/campaign-clean-01/evidence` | accepted functional-source campaign (controller) | **1** | **7** | 1 pass / 0 other | `3788353ef2ef92cf52cf266f3e356dd6840d00da` | `ryan-haver/wp-sw-api-offline-events` |
| F `SW-API-CLIENT-02-C1-review/campaign/evidence` | independent reviewer campaign at the submitted candidate | **1** | **7** | 1 pass / 0 other | `4baef5743b0e970328a979f181d701361f58da70` | `ryan-haver/wp-sw-api-offline-review` |
| G `docs/validation/runs/software-waves/SW-API-CLIENT-02-C1/failed-ci` | committed historical CI failure | 1 | 7 | **0 pass / 1 fail** (`gate: regression`) | `a7818f2054a57e4e5ee9176f2539e3155dff41d8` | `HEAD` |

Expected counts reconcile exactly for the accepted sets: **A = 13 records /
65 assertions** (5 declared + 1 automatic observer-schema check per record),
**E = 1 record / 7 assertions**. Every record in A, B, C, D, D2, E, F and G has
`image_digest: null`, `dirty: false`, `dirty_files: []`, level `V2`, client
`api`, target `sim`, and `state_diff` empty (no device mutation).

Four further sets (H, H2, H3, H4) hold the **fresh combined** campaign at the
integration base produced by the Sol worktree; they are inventoried in §6.5.
Total evidence records inspected across all twelve declared sets: **88**.

### 4.2 Author-receipt cross-check

The author's own `clean/audit.json` declares `records: 13`, `checks: 65`,
`schema_valid: true`, `image_digest: null`, `head_at_audit:
7b07e1cb7e7eb29a38b55d3b050703149f1b797c`. All **13** per-record SHA-256 values
in that file were independently recomputed from the original bytes here:
**13 matched, 0 mismatched, 0 missing**. The author's `clean/commands.json`
records the campaign `run` at exit **0** and the subsequent global `check` at
exit **1**; the recorded single reason is `F-SEC-007 dropped below its recorded
level: level V2 < recorded V3`. That failed global gate is consistent with the
independent review and remains an open coordinator-owned refresh, not a defect
of this inventory.

### 4.3 Original CORS record bytes — set A (functional source `7b07e1cb`)

Source root (read-only):
`C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-sw-api-header-proof/build/software-waves/SW-API-READ-04-C1/clean/campaign/evidence/F-API-031/`

| scenario | file | bytes | sha256 | source | client/target/level | result | assertions | dirty | image_digest | state_diff |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sw_api_read_04.configured_allowed | 2026-10-20-V2-7b07e1cb-sw_api_read_04.configured_allowed-api.json | 39511 | 0d1996df3464805691ec438197713a87c331979ca79e7d7bba1946e2c24e63f6 | 7b07e1cb | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.configured_allowed_preflight | 2026-10-20-V2-7b07e1cb-sw_api_read_04.configured_allowed_preflight-api.json | 30243 | 13b9b77df4ec7b6e68b9594db6ea99cd0fa1be95c2f284e0ea41d45055acb7c3 | 7b07e1cb | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.configured_denied | 2026-10-20-V2-7b07e1cb-sw_api_read_04.configured_denied-api.json | 31314 | e6259473794138c7758b3c03e60be195d15efae55ce7fcb5a3004bec0229c39f | 7b07e1cb | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.configured_denied_preflight | 2026-10-20-V2-7b07e1cb-sw_api_read_04.configured_denied_preflight-api.json | 30172 | bef05f287ac9a4421e169693d70150f486c8086f851ddab55eed0d765b93e862 | 7b07e1cb | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.default_denied_mutation | 2026-10-20-V2-7b07e1cb-sw_api_read_04.default_denied_mutation-api.json | 29978 | 27a67cf1b8ed377f036ec34846cce5340fced392f24c25ab2283f95596139b37 | 7b07e1cb | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.default_denied_origin | 2026-10-20-V2-7b07e1cb-sw_api_read_04.default_denied_origin-api.json | 31295 | 0ede42833071f8fb91d6419756f715554803f9ba6dcda66c211057b52a3cac35 | 7b07e1cb | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.default_no_origin | 2026-10-20-V2-7b07e1cb-sw_api_read_04.default_no_origin-api.json | 39383 | b002824e078dade6deb0868859cba8962200aca3d84a075c757c3767005e0fad | 7b07e1cb | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.default_no_origin_preflight | 2026-10-20-V2-7b07e1cb-sw_api_read_04.default_no_origin_preflight-api.json | 30114 | b1fe326de917d7248d27a146960654bd2e7ab0d0b284e5bd77a63b5d5152104f | 7b07e1cb | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.default_preflight | 2026-10-20-V2-7b07e1cb-sw_api_read_04.default_preflight-api.json | 30128 | 7c6ebe4c8f09e8f191aa0c69ddc4ffda1eaba10759b0d8edc77321c2687226b9 | 7b07e1cb | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.default_same_origin | 2026-10-20-V2-7b07e1cb-sw_api_read_04.default_same_origin-api.json | 31372 | c212f2dcdeecb1d1e048fb74a6d3cfe66ce4dbc75b46e5f0cfae55c125eecc7f | 7b07e1cb | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.wildcard_no_origin | 2026-10-20-V2-7b07e1cb-sw_api_read_04.wildcard_no_origin-api.json | 31307 | 9e499474732c0ff467d61bba49519472d4deaf1effe8d1cd3abaee89d8cd770c | 7b07e1cb | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.wildcard_origin | 2026-10-20-V2-7b07e1cb-sw_api_read_04.wildcard_origin-api.json | 39171 | cabc0c8427b17268baa95de04e212d8a57be4b8d23472d5ff3c65838fc1baeea | 7b07e1cb | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.wildcard_preflight | 2026-10-20-V2-7b07e1cb-sw_api_read_04.wildcard_preflight-api.json | 30180 | 2df9bf886cb1d71e797dc070e7f8e337efbfcd5218c8ec37c6ec4d55c1b51c6a | 7b07e1cb | api/sim/V2 | pass | 5 | false | null | 0 |

### 4.4 Reviewer record bytes — set B (submitted candidate `cb87427b`)

Source root (read-only):
`C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-sw-api-header-review/build/software-waves/SW-API-READ-04-C1-review/campaign/evidence/F-API-031/`

| scenario | file | bytes | sha256 | source | client/target/level | result | assertions | dirty | image_digest | state_diff |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sw_api_read_04.configured_allowed | 2026-10-21-V2-cb87427b-sw_api_read_04.configured_allowed-api.json | 38367 | 78197bfadf6c28f5d8806a3c09752200a679eecd8a18e8fbf6cd613207e3a831 | cb87427b | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.configured_allowed_preflight | 2026-10-21-V2-cb87427b-sw_api_read_04.configured_allowed_preflight-api.json | 30246 | 8ad3ce3dd018de445ff72c4904a5d84ce13ddf20216171f7451675df9d69fbe7 | cb87427b | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.configured_denied | 2026-10-21-V2-cb87427b-sw_api_read_04.configured_denied-api.json | 31314 | f97b71e957afdc485e336845bf3bcd945aacade4a36e1e09961a0689b40c4b50 | cb87427b | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.configured_denied_preflight | 2026-10-21-V2-cb87427b-sw_api_read_04.configured_denied_preflight-api.json | 30173 | c2ff1f1e3bc86cc79f64cf0a92ef552bfe1510bd945deb2a642ea9916f0b92c0 | cb87427b | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.default_denied_mutation | 2026-10-21-V2-cb87427b-sw_api_read_04.default_denied_mutation-api.json | 29981 | f2e5081f6a9dab495341d7e335b2f339a64e9589e6909ddad3b3db83d493cf08 | cb87427b | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.default_denied_origin | 2026-10-21-V2-cb87427b-sw_api_read_04.default_denied_origin-api.json | 31295 | b26804ff299641151b08dbf83e158a86da47ede4a8a4a6e1b80f8578d07f0fc7 | cb87427b | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.default_no_origin | 2026-10-21-V2-cb87427b-sw_api_read_04.default_no_origin-api.json | 38238 | 42b1a6d00b93c6fc726113c955aaf38c0d47dfb7402d469d22f943680c274390 | cb87427b | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.default_no_origin_preflight | 2026-10-21-V2-cb87427b-sw_api_read_04.default_no_origin_preflight-api.json | 30114 | f5936a3b9238846e55fe880e31464a60d90b58fe0fe909644f9e16bb4f2d1d5e | cb87427b | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.default_preflight | 2026-10-21-V2-cb87427b-sw_api_read_04.default_preflight-api.json | 30131 | efe645c0d272afc9348aa35827188a1cd10a6a54c50c49d153469870a66ec505 | cb87427b | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.default_same_origin | 2026-10-21-V2-cb87427b-sw_api_read_04.default_same_origin-api.json | 31373 | d4465737c17f102f2f7ee3330b9a1e6b4255fda2e521bc74d00ec079fdc276d2 | cb87427b | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.wildcard_no_origin | 2026-10-21-V2-cb87427b-sw_api_read_04.wildcard_no_origin-api.json | 31307 | 3e03d7c8483a9e73b0b01d0ae5e67501758925104f5077683b38751b3730782b | cb87427b | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.wildcard_origin | 2026-10-21-V2-cb87427b-sw_api_read_04.wildcard_origin-api.json | 38316 | 0c099e065f643f640cc43aeb959c1daa369ecf59ca3aa97feb76729c5909e6fc | cb87427b | api/sim/V2 | pass | 5 | false | null | 0 |
| sw_api_read_04.wildcard_preflight | 2026-10-21-V2-cb87427b-sw_api_read_04.wildcard_preflight-api.json | 30181 | edfae3b3dde85fa4c8e5e6a8f5df427143d04eb96c0f44ec9c69b1fc56e6e4e9 | cb87427b | api/sim/V2 | pass | 5 | false | null | 0 |

Set B is an **independent second set of 13 clean records at the submitted
candidate**, produced by a different family on a different branch. It is
duplicate coverage of the same feature at a later commit; it is **not** the
accepted functional-source set and must not be merged with set A. Set A stays
the accepted-source record set (source `7b07e1cb`); set B stays the reviewer's
own campaign, attributed to `cb87427b`.

### 4.5 Controller records — sets E, F, G

| set | file | bytes | sha256 | source | result / gate | assertions | features |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E | `2026-10-21-V2-3788353e-failures.unreachable_switch-api.json` | 39265 | fba2bdf50a422155bf2965224cd10588ea537a2eeed6f062b2369956d03212af | 3788353e | pass / ok | 7 | F-REL-009, F-API-033 |
| F | `2026-10-21-V2-4baef574-failures.unreachable_switch-api.json` | 38954 | 6ef5ab7cea5047ee7846a4327d9db6bdde1c6d4c330d18458be8465ab09438a4 | 4baef574 | pass / ok | 7 | F-REL-009, F-API-033 |
| G | `2026-10-20-V2-a7818f20-failures.unreachable_switch-api.json` | 37876 | a3ff5c68c366334e6b0c647396745ffa5e9021fa00219be1c6bdf358eb490a04 | a7818f20 | **fail / regression** | 7 | F-REL-009, F-API-033 |

Set G's single failing assertion is
`WebSocket event 'switch_failed' with {'input': 3}` with
`linked_finding: null`. That is the original defect reproduced byte-for-byte;
its SHA-256 matches the committed `finding-receipt.json`
(`original_record_sha256: a3ff5c68c366334e6b0c647396745ffa5e9021fa00219be1c6bdf358eb490a04`).

### 4.6 Excluded sets and why (duplicate diagnostics retained separately)

| set | reason for exclusion | disposition |
| --- | --- | --- |
| C (13 records / 65 assertions at `411c6642`) | the author's own report states these ran against an **uncommitted** working tree and "are not accepted clean proof"; the source SHA is the pre-package base | retained separately; must **not** be imported; would duplicate set A at the wrong source attribution |
| D / D2 (2 + 2 failing records) | intentionally red negative controls for wrong-value and unexpected-presence header assertions | retained separately as diagnostic evidence; a failing record is never imported as accepted feature evidence |
| G | the original failing CI record for the defect that was then corrected | retained under `docs/validation/runs/software-waves/SW-API-CLIENT-02-C1/failed-ci`, already committed, not accepted feature evidence |

No original record bytes were rewritten, renamed, re-serialised or relabelled.

### 4.7 Proposed destination mapping (mapping only — nothing was copied)

Canonical evidence convention observed in `docs/validation/evidence/<FEATURE>/`
is `<YYYY-MM-DD>-V<level>-<short-sha>-<scenario>-<client>.json`. The original
filenames already conform, so a mapping is a **path move plus a registry
entry**, not a rewrite.

| set | proposed canonical destination | collision state at base `310d8b65` |
| --- | --- | --- |
| A (13) | `docs/validation/evidence/F-API-031/<original filename>` | directory **does not exist**; 13 new files; no overwrite possible |
| B (13) | *not proposed for canonical import* — reviewer campaign, attributable to `cb87427b`; if the coordinator wants it retained it needs its own non-canonical destination | n/a |
| E (1) | `docs/validation/evidence/F-REL-009/2026-10-21-V2-3788353e-failures.unreachable_switch-api.json` | directory exists with 4 files; this filename is **not** among them → no overwrite |
| F (1) | *not proposed for canonical import* — reviewer campaign at `4baef574`; coordinator decision | n/a |
| G (1) | already committed at `docs/validation/runs/software-waves/SW-API-CLIENT-02-C1/failed-ci/…` | already in place; do not move |
| H/H2/H3/H4 (31) | the **fresh combined** records at `310d8b65` are the coordinator's canonical-import candidates (§6.5). Their filenames already follow the convention (`2026-10-26-V2-310d8b65-…`, `2026-10-26-V3-310d8b65-…`). Proposed destinations are `docs/validation/evidence/F-API-031/`, `docs/validation/evidence/F-SEC-007/`, `docs/validation/evidence/F-API-002/`, `docs/validation/evidence/F-REL-009/` and `docs/validation/evidence/F-API-033/`. | **Verified at base `310d8b65`: `F-API-002`, `F-API-031`, `F-API-033` and `F-SEC-007` directories are all ABSENT** (new directories, 30 new files, no overwrite possible); `F-REL-009` **exists** with 4 files and the proposed name `2026-10-26-V2-310d8b65-failures.unreachable_switch-api.json` is **not** among them → no overwrite. Following the existing pattern, the single offline record is filed under `F-REL-009/` and referenced from `F-API-033`'s `evidence:` list, exactly as `2026-10-04-V2-7dbc4dc7-failures.unreachable_switch-api.json` already is |

`docs/validation/evidence/F-REL-009/` currently contains exactly:
`2026-09-25-V2-d6668000-…`, `2026-10-04-V2-7dbc4dc7-…`,
`2026-10-04-V3-d6baf3ca-live.matrix_offline-browser.json`,
`2026-10-19-V3-4adbc136-live.matrix_offline-browser.json`.
No proposed destination collides with an existing file, so no populated
archival destination needs to be overwritten.

Registry rows that the coordinator (and only the coordinator) owns:

- `F-API-031`: `target: V2`, `current: V1`, `evidence: []`,
  `findings: [SEC-02]`, 13 scenarios already registered. Importing set A would
  be the first canonical evidence for this feature.
- `F-API-033`: `target: V3`, `current: V2`, `evidence:` lists only the
  `2026-10-04` records, `findings: []`.
- `F-REL-009`: `target: V4`, `current: V3`, `existing_evidence:` lists the
  `2026-10-04`/`2026-10-19` records; the new record is an **additional**
  API-V2 record for a scenario that already has V3 browser evidence, so it
  does not by itself promote the feature.

---

## 5. Accepted functional blobs survive at the base `310d8b65`

`blob_survival.py` compared Git **blob object IDs** at four revisions per path.
Object IDs are line-ending independent, which is the correct comparison for a
Windows checkout.

### SW-API-READ-04-C1 (functional `7b07e1cb`, submitted `cb87427b`, report `c8910ee5`)

| path | present at base | base OID == functional OID | base OID == submitted OID | checkout bytes == Git blob | checkout CRLF-normalised == Git blob | checkout CRLF count |
| --- | --- | --- | --- | --- | --- | --- |
| `tools/validate/clients/api.py` | yes | yes | yes | no | **yes** | 166 |
| `tools/validate/model.py` | yes | yes | yes | no | **yes** | 498 |
| `tools/validate/runner.py` | yes | yes | yes | no | **yes** | 1036 |
| `tools/validate/stack.py` | yes | yes | yes | no | **yes** | 486 |
| `tests/validation/scenarios/sw_api_read_04.py` | yes | yes | yes | no | **yes** | 67 |
| `tests/validation/test_sw_api_read_04.py` | yes | yes | yes | no | **yes** | 184 |
| `docs/validation/features.yaml` | yes | yes | yes | no | **yes** | 8110 |
| `docs/production/software-waves/SW-API-READ-04-C1/AUTHOR.md` | yes | no (expected: the report-only follow-up) | **yes** | no | **yes** | 237 |

### SW-API-CLIENT-02-C1 (functional `3788353e`, submitted `4baef574`, report `0bd3d76f`)

| path | present at base | base OID == functional OID | base OID == submitted OID | checkout bytes == Git blob | checkout CRLF-normalised == Git blob | checkout CRLF count |
| --- | --- | --- | --- | --- | --- | --- |
| `src/rest_api/control.py` | yes | yes | yes | no | **yes** | 533 |
| `tests/sim/test_sim_rest_reads.py` | yes | yes | yes | no | **yes** | 598 |
| `tests/sim/test_sim_offline_switch_events.py` | yes | yes | yes | no | **yes** | 248 |
| `docs/production/software-waves/SW-API-CLIENT-02-C1/AUTHOR.md` | yes | n/a (added by the report commit) | **yes** | no | **yes** | 179 |

Findings:

- **All six** SW-API-READ-04-C1 functional paths and **all three**
  SW-API-CLIENT-02-C1 functional paths are present at `310d8b65` with a Git blob
  OID **identical** to the accepted functional source *and* to the submitted
  candidate. The accepted source therefore survives intact in the integration
  base.
- The two `AUTHOR.md` report paths at the base carry the **submitted** OID
  (`cb87427b`, `4baef574`), i.e. the report-only follow-up commits are merged
  and the reports are preserved in their final submitted form. They differ from
  the functional-source OID, which is expected and correct.
- **Correction (after coordinator feedback): both independent review reports
  ARE present in the base.** Verified directly:
  `git rev-parse 310d8b65:docs/production/software-waves/SW-API-READ-04-C1/REVIEW.md`
  → `40e18f2338c26d6f3ee4aa3f492b4c4dc5b80e08`, identical to the blob in the
  review commit `c8910ee5a05a26a2eb53f88d96cbdc080a385886`; and
  `git rev-parse 310d8b65:docs/production/software-waves/SW-API-CLIENT-02-C1/REVIEW.md`
  → `85c18d2443c758fe78964c6c2098b1317eb41036`, identical to the blob in
  `0bd3d76f8bc965753849f804abb876f0511dfe65`. The review commits are therefore
  **content-merged** into the base. An earlier draft of this report asserted
  the opposite; that assertion was wrong and is withdrawn. No gap G7 remains
  on this point.
- **Checkout vs Git blob discrepancy, explained.** For all 12 paths the
  working-tree bytes differ from the Git blob bytes, and for every path the
  CRLF-normalised working-tree bytes are **byte-identical** to the Git blob
  bytes. The only difference is Windows checkout line-ending conversion
  (`core.autocrlf`). This is a checkout artefact, not a source divergence, and
  it must not be mistaken for one. Git blob OIDs are the authoritative
  comparison.

---

## 6. Workspace, publication and preservation inventory

### 6.1 The four released wave03 workspaces (read-only inspection)

| worktree | role | on disk | HEAD | head == expected | branch | `git status --porcelain` | files excl. `.git` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `wp-sw-api-header-proof` | header author | yes | `cb87427b…` | **yes** | `ryan-haver/wp-sw-api-header-proof` | empty (clean) | 17980 |
| `wp-sw-api-header-review` | header reviewer | yes | `c8910ee5…` | **yes** | `ryan-haver/wp-sw-api-header-review` | empty (clean) | 4516 |
| `wp-sw-api-offline-events` | controller author | yes | `4baef574…` | **yes** | `ryan-haver/wp-sw-api-offline-events` | empty (clean) | 29581 |
| `wp-sw-api-offline-review` | controller reviewer | yes | `0bd3d76f…` | **yes** | `ryan-haver/wp-sw-api-offline-review` | empty (clean) | 7415 |

All four workers were released before completion acknowledgment
(`headers-author-release.json`, `headers-review-release.json`,
`offline-author-release.json`, `offline-review-release.json`; each records
`state: released`, `processAction: closed_agent_terminal`, transcript/terminal
archive `captured`). All four are still present on disk and clean; no worktree
was removed, no branch was deleted, no resource was released by this task.

### 6.2 Verified Git bundles and archives

| artefact | path under `build/software-wave-03-20261020/` | present | recorded sha256 | verify log |
| --- | --- | --- | --- | --- |
| header author bundle | `headers-author-full.bundle` (11,702,117 B) | yes | `600547110630cec845eedfd9ecadf8df330398aa690ba74250f29e9e99de300a` | `…is okay`, "complete history" |
| header reviewer bundle | `headers-review-full.bundle` (11,712,875 B) | yes | `cba006f4233dc9c700b2df53051958eeb031cb022327c9c01b4ace3afe65e452` | `…is okay` |
| controller bundle | `offline-author-full.bundle` (11,731,212 B) | yes | `c524a46c6f5a2747c75101d0dbd31142a3d5ab06aca8d58b8df159899e3271da` | `…is okay` |
| controller-reviewer bundle | `offline-review-full.bundle` (11,723,496 B) | yes | `a68e49835419eb06b45f2330ab354a4f19ddd5c6ca2ec75c84c0ba31f8465cfe` | `…is okay` |
| header author **whole workspace** | `headers-author-complete-workspace.tar` (454,113,280 B) + `headers-author-complete-workspace-manifest.json` (6,052,507 B) | yes | manifest-recorded | manifest present |
| external temp root #1 archive | `headers-external-temp2-complete.tar` (117,729,280 B) + manifest (6,250,789 B) | yes | manifest-recorded | source `C:\Users\ryanh\AppData\Local\Temp\c1-hook-v90b4ka3` (20,006 files / 65,452,341 B) |
| external temp root #2 archive | `headers-external-temp3-complete.tar` (125,880,320 B) + manifest (6,612,234 B) | yes | manifest-recorded | source `C:\Users\ryanh\AppData\Local\Temp\c1-hook3-erf6axvs` (21,207 files / 70,080,576 B) |

Both external-temp archives are recorded as fully verified:
`headers-external-temp-normalized-reconciliation.json` reports for each root
`regular_file_hash_mismatches: 0`, `unexplained_missing: 0`,
`unexplained_additional: 0`, `junctions_preserved: 1`,
`archive_all_hashes_and_targets_verified: true`. The single recorded alias is
the documented 10-byte `secret.css` junction target that the author's
inventory counted twice because it followed a junction; the archive preserves
the junction metadata without following it and contains the canonical target
file with an equal hash. **Junctions were not followed here either.**

Observed, after consulting the reversible relocation plan (see below): both
original external temp roots are **no longer at their original
`C:\Users\ryanh\AppData\Local\Temp` paths** (`c1-hook-v90b4ka3` and
`c1-hook3-erf6axvs` both absent there). **This is not data loss.** The
relocation plan `build/project-file-cleanup-20261022/reversible-relocation-plan-complete.json`
records both roots as moved **reversibly into quarantine**:

| original root | relocated to | recorded bytes | manifest referenced |
| --- | --- | --- | --- |
| `C:\Users\ryanh\AppData\Local\Temp\c1-hook-v90b4ka3` | `C:\scripts\unfoldedcircle-orei-hdmi-matrix-integration\build\project-file-cleanup-20261022\quarantine\temp-c1-hook-v90b4ka3` | 65,452,331 | `headers-external-temp2-manifest.json` |
| `C:\Users\ryanh\AppData\Local\Temp\c1-hook3-erf6axvs` | `...\quarantine\temp-c1-hook3-erf6axvs` | 70,080,566 | `headers-external-temp3-manifest.json` |

Both quarantine copies were confirmed **present on disk** here
(`temp-c1-hook-v90b4ka3`: 18,898 files / 64,338,445 bytes observed;
`temp-c1-hook3-erf6axvs`: 19,862 files / 68,740,126 bytes observed), and the
relocation entries point at exactly the two hash-verified archive manifests
above. Honest limit: my measured file/byte counts are ~1,108 files / ~1.11 MB
below the relocation plan's recorded byte totals, and that delta is **not
reconciled here** — no cause was investigated and no claim is made about it.
The hash-verified archives remain the binding artefact (0 unexplained missing,
0 hash mismatches); the quarantine copy difference is a coordinator
reconciliation item, not a proven loss. **Junctions were not followed** in
either the archives or this inspection.

### 6.3 Task branch publication (exact verification)

| branch | published ref | local == remote | receipt |
| --- | --- | --- | --- |
| `ryan-haver/wp-sw-api-header-proof` | `cb87427bd2646fc686e1cff02692a4240dcf51c1` | **yes** | `headers-author-publication.json` (`equal: true`, "unreviewed/unqualified; no integration publication") |
| `ryan-haver/wp-sw-api-offline-events` | `4baef5743b0e970328a979f181d701361f58da70` | **yes** | `accepted-task-refs-publication.json` |
| `ryan-haver/wp-sw-api-header-review` | `c8910ee5a05a26a2eb53f88d96cbdc080a385886` | **yes** | `accepted-task-refs-publication.json` |
| `ryan-haver/wp-sw-api-offline-review` | `0bd3d76f8bc965753849f804abb876f0511dfe65` | **yes** | `accepted-task-refs-publication.json` |

`accepted-task-refs-publication.json` records `integration_publication:
"pending"`. The three task refs were pushed as new branches
(`accepted-task-refs-push.log`) and the header author ref separately
(`headers-author-push.log`). **All four task branches are published and exact
verified.** These were read from the recorded receipts; no network push or
fetch was performed by this task.

Combined-source integration proof already on record
(`combined-source-integration-proof.json`, combined source
`c9938f1b2ce1a2481fd5ac40f39ed88170b52539`, header merge `cfe16633…`):
both packages `source_byte_identical: true` and `ancestor: true` for their
functional paths, with status "canonical evidence qualification/publication
pending".

### 6.4 Remaining preservation gaps (exact paths; next owner = coordinator)

These are reported, not remedied. No cleanup, deletion, archive write or
permission grant is performed or implied by this task.

| # | Gap | Exact paths | Evidence | Next owner |
| --- | --- | --- | --- | --- |
| G1 | **Whole-workspace archive missing for the controller author.** Git bundle `offline-author-full.bundle` covers tracked Git objects only; the controller's ignored build tree (campaign evidence, hook logs, attempt directories) has no whole-workspace archive. | `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-sw-api-offline-events/build/software-waves/SW-API-CLIENT-02-C1/` (29,581 files excl. `.git`) | `workspace-inventory.json` → `wp-sw-api-offline-events.workspace_archive = null` | coordinator |
| G2 | **Whole-workspace archive missing for the header reviewer.** Its independent 13-record reviewer campaign (set B) exists only inside that worktree's ignored build tree. | `.../wp-sw-api-header-review/build/software-waves/SW-API-READ-04-C1-review/` (4,516 files excl. `.git`) | `workspace-inventory.json` → `wp-sw-api-header-review.workspace_archive = null` | coordinator |
| G3 | **Whole-workspace archive missing for the controller reviewer.** Its independent 1-record reviewer campaign (set F) exists only inside that worktree's ignored build tree. | `.../wp-sw-api-offline-review/build/software-waves/SW-API-CLIENT-02-C1-review/` (7,415 files excl. `.git`) | `workspace-inventory.json` → `wp-sw-api-offline-review.workspace_archive = null` | coordinator |
| G4 | **Recovery-checkout proof missing for the controller reviewer.** `recovery-checkouts-proof.json` has rows for `headers-author`, `headers-review` and `offline-author` only. The bundle itself exists and its verify log says "is okay", so this is a proof-set gap, not a byte-loss gap. | `build/software-wave-03-20261020/recovery-checkouts-proof.json` | `workspace-inventory.json` → `workspaces_without_recovery_checkout_proof = ["wp-sw-api-offline-review"]` | coordinator |
| G5 | **Canonical import of the accepted records is still pending.** The 13 set-A records and the set-E record are not in `docs/validation/evidence/`; `F-API-031.evidence` is still `[]`. | `docs/validation/evidence/F-API-031/` (absent), `docs/validation/evidence/F-REL-009/` (4 files) | §4.7 mapping | coordinator |
| G6 | **Canonical import and final assembly are still pending.** The fresh combined evidence at the base **passes** the formal gate (§6.5); what remains is the coordinator's canonical import, registry/ledger reconciliation and final assembly — not a failed gate. | §6.5 | coordinator |
| G7 | **Withdrawn — not a gap.** An earlier draft claimed the review reports were absent from the base. Verified: both `REVIEW.md` blobs at `310d8b65` are byte-identical to their review commits `c8910ee5` and `0bd3d76f`. | §5 correction | closed by this report |

Not gaps: the four worktrees are present, clean and at their expected heads;
all four task branches are published and exact-verified; all four bundles are
present and verified; the header author whole workspace is archived; both
external temp roots are archived, hash-verified **and** relocated reversibly
into quarantine; the committed failed-CI record and its receipt are in place;
the manifests and receipts are retained.

### 6.5 Fresh combined evidence at the base (read-only inspection)

Per coordinator message `msg_2a85c9605614`, the Sol worktree
`wp-w03-close-evidence` produced a fresh combined campaign at the integration
base. Its build tree
`wp-w03-close-evidence/build/phase-resume-20261026/evidence/` was inspected
**read-only**; nothing there was copied, imported or modified.

| set | feature / purpose | records | assertions | clients | levels | results |
| --- | --- | --- | --- | --- | --- | --- |
| `cors` | F-API-031 | **13** | 65 | api 13 | V2 13 | 13 pass / 0 other |
| `auth` | F-SEC-007 | **14** | 114 | api 6, browser 8 | V2 6, V3 8 | 14 pass / 0 other |
| `api-root` | F-API-002 | **3** | 20 | api 3 | V2 3 | 3 pass / 0 other |
| `offline` | F-API-033, F-REL-009 | **1** | 7 | api 1 | V2 1 | 1 pass / 0 other |
| **total** | | **31** | **206** | api 23, browser 8 | V2 23, V3 8 | **31 pass / 0 non-pass** |

The **31** count reconciles exactly with the coordinator's statement
(14 auth + 3 root API + 13 CORS + 1 unreachable-switch), and every one of the
31 records was confirmed by me to carry:

- `commit.sha` = `310d8b65a9fce3c9069523d4ac5ce21157e75c9f` (the integration
  base), `dirty` = `false`, `dirty_files` = `[]`;
- `image_digest` = **null** in all 31 — the 32 PNG files that accompany the
  8 browser V3 auth records are **browser screenshots**, not container images,
  and no image digest is claimed anywhere in this fresh set;
- `result` = `pass` and `gate` = `ok` in all 31, `state_diff` empty in the API
  records.

Per-client mapping is therefore exactly as the registry expects: F-API-031 is
API-only V2, F-API-002 is API-only V2, F-API-033/F-REL-009 is API V2, and
F-SEC-007 carries **both** the API V2 records and the browser V3 records that
its recorded V3 level needs.

The recorded formal check at that base is now a **PASS**:
`formal-check.log` reads `[validate] gate OK (0 known failure(s) linked to open
findings)` and `formal-check-receipt.json` records `exit: 0`, `head:
310d8b65a9fce3c9069523d4ac5ce21157e75c9f`, `dirty_files: []`, with
`--expect-clients api,browser`.

**Distinction, stated precisely.** The historical global check that failed
after the *original* CORS source (`F-SEC-007 dropped below its recorded level:
level V2 < recorded V3`, exit 1, recorded in the author's
`clean/commands.json` and §4.2) was a **stale historical gate at that older
source**. It is now superseded by the fresh combined gate above, which passes
at the actual base. What genuinely remains open is **pending canonical import
and final assembly** (G6) — not a failed freshness gate. This report does not
pre-approve that import, does not modify any record and does not qualify
F-SEC-007; the coordinator retains canonical metadata, import and assembly.

No count or source gap was found in the fresh set: 31/31 records are present,
all at the exact base, all clean, all passing, with the expected client mix.

---

## 7. Findings: registered vs unregistered state (VAL-14, VAL-15)

No finding was registered, closed, re-linked or accepted by this task. This
section only records the precise state found.

### VAL-14 — offline routing failure event (SW-API-CLIENT-02-C1)

- **Registered: no.** `docs/REMEDIATION_PLAN.md` §4.10 "Found by validation"
  contains `VAL-01` … `VAL-13`; there is **no VAL-14 row**.
  `docs/validation/findings_pending.yaml` is `findings: []` — **no pending
  row** either.
- **Proposed:** `docs/production/software-waves/SW-API-CLIENT-02-C1/FINDING.md`
  ("provisional finding VAL-14; canonical registration and combined evidence
  qualification remain pending"), and
  `docs/planning/software-waves/manifest.json` → `corrective_children` →
  `SW-API-CLIENT-02-C1.finding = "VAL-14 proposed; registration pending"`.
- **Source evidence:** the original failing record, committed byte-for-byte at
  `docs/validation/runs/software-waves/SW-API-CLIENT-02-C1/failed-ci/2026-10-20-V2-a7818f20-failures.unreachable_switch-api.json`
  (37,876 B, SHA-256 `a3ff5c68c366334e6b0c647396745ffa5e9021fa00219be1c6bdf358eb490a04`),
  with the matching `finding-receipt.json` (same SHA, `provisional_finding:
  "VAL-14; not yet registered"`, `qualification: "Historical failing CI record
  retained outside accepted feature evidence; no promotion"`), and the CI run
  `39500840835` reference.
- **Concrete consequence of the unregistered state (measured, not inferred):**
  the failing check in the original record carries `linked_finding: null` and
  the record's `gate` is `regression`. Under the documented CI rule ("a
  scenario fails and one of its failed checks is not linked to an open finding
  (`gate: regression`)"), the original defect is currently an **unlinked
  regression** rather than a known-bug link. The corrected source makes the
  check pass (sets E and F), so the defect itself is corrected and reviewed;
  what remains open is the **register row and the check link**, both
  coordinator-owned.
- Registry rows affected but unchanged by this task: `F-API-033`
  (`findings: []`), `F-REL-009` (`findings: [UI-29]`), `F-API-034` (secondary
  impact).

### VAL-15 — request-header redaction gap (SW-SEC-DATA-02-C1)

- **Registered: no.** No VAL-15 row in `docs/REMEDIATION_PLAN.md` §4.10 and
  `findings_pending.yaml` is `findings: []`.
- **Proposed:** `docs/production/software-waves/SW-SEC-DATA-02-C1/FINDING.md`
  ("proposed finding VAL-15, registration and corrective dispatch pending");
  `manifest.json` → `corrective_children` → `SW-SEC-DATA-02-C1.finding =
  "VAL-15 proposed; registration pending"`, `state:
  "reproduced_finding_no_dispatch"`, `task_id: null`, `dispatch_id: null`.
- **Source evidence:** `docs/validation/runs/software-waves/SW-SEC-DATA-02-C1/request-redaction-observation.json`
  — synthetic, boolean-only calibration showing `X-Admin-PIN: true` survives
  `evidence.redact` while `X-API-Key`, `Authorization` and `Cookie` are
  `false`, `admin_pin_survives_action_describe: true`,
  `writer_changed: false`, `new_cors_scenarios_send_credentials: false` — plus
  `docs/validation/runs/software-waves/SW-SEC-DATA-02-C1/coordinator-confirmation.json`.
  The header author independently reported the same boundary as
  `msg_0b207923dadd` / `request-redaction-observation.json` in its own build
  tree.
- **No fix exists and none is claimed.** The defect predates the header
  package; the new response-header capture masks all non-allowlisted values,
  but the *request* boundary is unchanged and unfixed.
- Registry row affected but unchanged: `F-SEC-014` (`target: V3`,
  `current: V1`, `findings: [SEC-10]`, `evidence: []`).

### Additional source-linked closeout blockers (concrete evidence only)

1. **F-SEC-007 freshness — historical failure, now superseded.** The global
   check that ran **after the original CORS source** exited 1 with
   `F-SEC-007 dropped below its recorded level: level V2 < recorded V3`
   (recorded in the author's `clean/commands.json`, exit 1, and §4.2). That
   gate failed because the four changed tooling paths staled the existing
   browser-V3 evidence. The **fresh combined** formal check at the actual base
   now **passes** (§6.5: `[validate] gate OK`, exit 0, `--expect-clients
   api,browser`, 14 auth records of which 8 are browser V3). The historical
   failure is therefore **not** an open blocker; what remains is the
   coordinator's canonical import of the fresh records and final assembly.
   Until that import happens the fresh records are **not** canonical
   evidence, and this report does not pre-approve the import.
2. **The two `findings_pending.yaml` / REMEDIATION_PLAN rows** (VAL-14,
   VAL-15) are the only registration routes; both are coordinator-owned and
   both are demonstrably absent today (§7). No third proposed finding was
   found in the inspected material.
3. **Canonical evidence destination for F-API-031 does not exist.** Any
   import is a 13-file creation in a new directory; there is no existing
   populated destination to overwrite, and the proposed F-REL-009 filename
   does not collide with the 4 files already there.

No broader project re-inventory was performed and no new ceremonial
requirement is proposed.

---

## 8. Feature and manifest ownership preserved

Measured at base `310d8b65` in this worktree:

- `docs/validation/features.yaml`: **268** feature ids, 268 unique
  (`- id: F-…`). The 268 primary owners are unchanged by this task; no
  registry edit was made.
- `docs/planning/software-waves/manifest.json`: **30 packages**, **65
  dispatch units**, **268 feature** entries — matching the recorded
  "30 packages / 65 units, original 268 feature owners unchanged" statement
  in its own `execution_updates`. The authoritative unit list is the
  **top-level `dispatch_units`** array, and it is 65; the sum of each
  package's own `dispatch_units` is also 65, so the two agree and nothing is
  unallocated. A missing `units` property is not zero allocated units and no
  such inference is made here.
- `F-API-031` keeps its 13 registered scenarios and `findings: [SEC-02]`;
  `F-API-032` remains deferred; `F-SEC-014` and `F-API-033` keep their
  existing findings lists. Nothing was added, removed or relabelled.

---

## 9. Boundaries explicitly not crossed

- No API-as-browser and no API-as-image qualification. The 57 records of the
  original wave03 packages are all `client: api`, `target: sim`, `level: V2`,
  `image_digest: null`. The **fresh combined** set (§6.5) contains 23 API V2
  records and 8 **browser V3** records for F-SEC-007; those browser records
  are the Sol worker's own V3 evidence with browser screenshots, and this
  inventory neither re-attributes nor re-qualifies them.
- No evidence import, relabel, rewrite, re-serialisation, rename or move.
- No registry, ledger, findings, manifest, feature-owner or root-manifest
  change; no `python -m tools.validate ledger` run; no registry check run.
- No new test, no production tooling, no source change, no scenario change.
- No archive, quarantine, bundle or archival destination written or
  overwritten; no file deleted; no cleanup or removal performed or authorised.
- No push, merge, tag, branch deletion or remote mutation. No runtime
  service started. No credential store, private runtime data, account secret
  or other project's resource was read.
- No worker, helper, subagent or fallback launched; no Anthropic/Claude model
  used; no nested worker.
- No security/core review competence is inferred from this inventory, and no
  source-review qualification is granted by it.

---

## 10. Summary for the coordinator

1. The accepted functional-source records reconcile exactly: **13 CORS records
   / 65 assertions** at `7b07e1cb` (all 13 SHA-256 values independently
   recomputed and matched against the author's own `audit.json`), and
   **1 record / 7 assertions** at `3788353e`; the independent reviewer sets
   (13/65 at `cb87427b`, 1/7 at `4baef574`) match in count and are separately
   attributed. Duplicate diagnostics (13/65 at `411c6642`) and the retained
   failing records (2 + 2 focused negatives, 1 committed CI failure) are
   excluded from any import and stay separate.
2. **All nine accepted functional source blobs survive at `310d8b65`** with
   identical Git object IDs; the two report files match the *submitted*
   candidates; the only working-tree difference on all 12 paths is CRLF
   checkout conversion, proven by byte-identical CRLF-normalised comparison.
3. The concrete closeout blockers are: whole-workspace archives still missing
   for the controller and both reviewers (G1–G3), a missing recovery-checkout
   proof row for the controller reviewer (G4), **pending canonical import and
   final assembly** (G6 — the historical F-SEC-007 freshness failure is a
   stale historical gate at the older source and is now superseded by the
   fresh combined gate that **passes** at the base, §6.5), and **VAL-14 and
   VAL-15 both proposed but unregistered in either the REMEDIATION_PLAN
   register or `findings_pending.yaml`** — with VAL-14's original failing check
   currently carrying `linked_finding: null` and therefore a `gate:
   regression`. The earlier draft's claim that the review reports were absent
   from the base (G7) was **wrong** and is withdrawn: both review blobs are
   present at `310d8b65` and byte-identical to their review commits.
4. The fresh combined evidence reconciles exactly at **31 records / 206
   assertions, 31 pass / 0 non-pass**, all at source `310d8b65`, all clean, all
   `image_digest: null`, with the expected per-client split (23 API V2, 8
   browser V3) — no count or source gap found. The two original external temp
   roots are **not lost**: they were relocated reversibly into
   `build/project-file-cleanup-20261022/quarantine/`, their hash-verified
   archives are intact, and an unreconciled ~1.1 MB / ~1,108-file difference
   between the recorded relocation byte totals and my own measurement of the
   quarantine copies is reported for the coordinator, not resolved here.
   Every one of these is coordinator-owned; this task neither fixed nor
   authorised any of them.
