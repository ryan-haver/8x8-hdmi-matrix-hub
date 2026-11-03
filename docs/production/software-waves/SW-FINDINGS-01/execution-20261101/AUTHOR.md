# SW-FINDINGS-01 — current findings inventory (bounded DELTA to accepted historical triage)

**Task:** `task_003f9f06ee62` · **Dispatch:** `ctx_8f2f304eeed7` · **Run:** `run_37205f6095b3` (gen5) ·
**Coordinator terminal:** `term_6ed8131e-3ab3-4693-8094-56cc10acd412` · **Orca** 1.4.246 ·
**Runtime** `e8ce3460-a9d4-4897-8e4f-10a8e3cdc400`
**Exact entry base:** `3602a4e4ad3333d4be989ce34b8285e73cbd472c` · **Branch:** `ryan-haver/wp-exec-sw-findings-01`
**Author:** native MiniMax-M3 via OpenCode 2 (CLI model/effort override unsupported; inherited project routing) · **2026-11-02**

## 1. Scope and authority

This is a **prose DELTA to the accepted historical triage**, not new source/security qualification and not
implementation. It answers one question: *what is the current parser-open set at my exact base, and how does
it differ from the accepted 59-row triage?*

The accepted historical input is reused, not repeated:
[`docs/production/software-waves/SW-FINDINGS-01/AUTHOR.md`](../AUTHOR.md) (DeepSeek Pro report
`8f23ae8976a4056f7dd7793ad3733c730594f42d`, correction `b008297b1a3c988789e92c2cb4c32f3396bcd07f`,
base `97e617c2276c7b1e015bb4a9419cb9820deafdee`), accepted **as triage only, with limits**, by the OpenAI
coordinator in [`COORDINATOR_RECONCILIATION.md`](../COORDINATOR_RECONCILIATION.md). Those bytes, that report,
that correction and that disposition are **immutable and unmodified**. This report closes **no** finding,
edits **no** register/ledger/registry/pending-YAML row, and asserts **no** reproduced runtime defect.

The global SW-AUDIT-01 inventory remains `require_changes` (`EXECUTION_GATE_STATUS.json` → `inventory.verdict`;
re-review `d44ad2b…` require_changes; re-review at `394dd867…` require_changes). It is therefore **not** an
accepted source of finding closure and is not used as one here. Core reviewer qualification remains
**FAIL, attempt 1, `qualified_domains: []`**, owner retake decision pending; unrelated metadata work does not
override source or owner gates.

## 2. Method

- **Reused:** the accepted 59-row triage, its dispositions, its limits, and the coordinator's disposition
  (including its explicit non-acceptance of the BE-22 residual and of the §7 shorthand external-gate count).
- **Newly done, read-only:** parser enumeration via the existing `tools.validate.registry.load_findings()` at my
  exact base; an independent row-level diff of `docs/REMEDIATION_PLAN.md` §4 between the historical base and
  my base; a `features.yaml` delta read; and **fresh static source-reference checks only** for changed or
  unsupported claims.
- **Environment:** root `.venv` Python 3.12.10 (`C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv`);
  `PYTHONPATH` = own checkout root + `src`; `PYTHONUTF8=1`; `PYTHONDONTWRITEBYTECODE=1`; created fresh
  `data/`, `config/`, `temp/` and an explicit forward-slash `--basetemp` under `C:/t/exec-sw-findings-01/nov02-attempt01/`.
- **Not done, by scope:** no runtime test, campaign, probe or reproduction for any finding; no source/test/tool/
  fixture/scenario/schema edit; no ledger or gate generation/import; no service, install, hardware, Docker,
  version, release, cleanup, push or merge. No credentials, raw validation/image/archive payloads or purged bytes read.
- **Size:** 1 259 prose words plus a compact current-ID crosswalk table (1 540 table words; 2 799 total).

## 3. Current parser state at base `3602a4e`

| Measure | Historical base `97e617c` | **Current base `3602a4e`** | Delta |
| --- | --- | --- | --- |
| Total findings | 263 | **265** | +2 |
| Parser-open | 59 | **61** | **+2** |
| Closed | 204 | 204 | 0 |
| Open IDs | 59 register rows | **59 register rows + 2 pending-YAML rows** | +VAL-14, +VAL-15 |

**Additions (2):** `VAL-14`, `VAL-15`. Both come from `docs/validation/findings_pending.yaml`, which was
`findings: []` at the historical base and now carries both rows. **Removals: 0.** The intersection of the
historical 59 with the current 61 is exactly the historical 59 — **every previously open row is still open**.

**The register did not move.** `git diff --stat 97e617c 3602a4e -- docs/REMEDIATION_PLAN.md` is **empty**, and
an independent parse of both revisions yields identical results: 263 rows, 59 open, **0 row-text changes, 0
severity changes, 0 open/closed transitions, 0 added/removed rows**. Register §4 contains `VAL-01`…`VAL-13`
only; it has no `VAL-14`/`VAL-15` row, so both new IDs are genuinely pre-register.

**The registry did move.** `docs/validation/features.yaml` gained `VAL-14` on `F-API-033`, `F-API-034`,
`F-REL-009` and `VAL-15` on `F-SEC-014`, plus level promotions `F-API-002` V1→V2, `F-API-031` V1→V2,
`F-SEC-007` V1→V3 with new evidence links. This is the mechanism by which the ledger/CI treat the two rows as open.

**Product-source delta is one file.** Between the two bases exactly 14 files changed, of which only
`src/rest_api/control.py` is product source (the rest are `tests/**` and `tools/validate/**`). Consequently
every cited source file of the carried 59 rows is byte-identical to the historical base, and the inherited
source-inspection statements still hold **as source presence**.

## 4. New rows — current retained state and next exact acceptance action

| ID | Accepted historical triage | Current state at `3602a4e` (source presence only) | Next exact acceptance action |
| --- | --- | --- | --- |
| **VAL-14** (M) — already-disconnected routing requests omitted documented failure events | **None.** Row post-dates the accepted 59; it was never in the historical triage. | Source correction `3788353e` and its independent review `0bd3d76f` **are ancestors of this base** → the correction is integrated. Fresh static check: `src/rest_api/control.py` contains `switch_failed` (4) and `switch_all_failed` (2). `features.yaml` links it to F-API-033/F-API-034/F-REL-009. Pending-YAML disposition: *"Source correction independently accepted; formal closeout awaits final assembly review and combined CI/publication. No V3 target promotion or historical failure waiver."* | **Coordinator** records the assembly/combined CI publication, then performs register closure of VAL-14 (rename into `REMEDIATION_PLAN.md` §4 and update `features.yaml` + scenario `finding=` links per the pending-file header). **No new implementation, no new author.** Retain "open" until that recorded closeout exists. |
| **VAL-15** (M) — validation request artifacts / action descriptions do not redact X-Admin-PIN | **None.** Row post-dates the accepted 59. | The pending-YAML wording *"Corrective package SW-SEC-DATA-02-C1 remains undispatched"* is **stale**: the retained C1/C2/C3 submissions `11f305b1` / `615d3c84` / `2d02004d` exist, but **none is an ancestor of this base** → delivered, **unreviewed and unintegrated**. Fresh static check: `tools/validate/evidence.py` is **byte-identical** to the historical base and its `redact()` masks only secret-looking dict **keys**; `x-admin-pin` (case-insensitive) and `ADMIN_PIN` occur **0 times** in `tools/validate/evidence.py` and `tools/validate/model.py` → the credential-header redaction is **not present at this base**. The historical synthetic-marker reproduction is **not** a current reproduction and **not** an observed owner-credential leak. | Route to the **qualified full-chain review → privacy admission → register reconciliation** path. Needs an independent qualified different-family review of the retained C1/C2/C3 chain at its exact commits, then coordinator privacy disposition and register closure. **No duplicate implementation, no finding closure here.** Retain "open" + source-inspection lead. |

**FSEC007 is a separate parallel gate, not a VAL-14/VAL-15 closure event.** The recorded actual failure is
`actual global gate exit1 FSEC007 V2<recordedV3` (Sol package `ee3f2e7f…`, `task_14b35f83dc26`). Meanwhile
`features.yaml` now records `F-SEC-007` at `current: V3` with SW-SEC-AUTH-01 evidence. So a **recorded V3
exceeds the V2 the actual global gate observed**, and the freshness mismatch is unresolved. That is a
level-freshness defect in the F-SEC-007 gate chain and belongs to the existing FSEC007 diagnosis/refresh
scope (`SW-API-CLIENT-02-C2`, `task_f441e3251dbd`) — **not** to this unit, and not a closure of either new row.

## 5. Carried 59 — material deltas and non-inherited labels

Where the current register text conflicts with the accepted triage's evidence string, I re-checked the source
statically. **A fresh check never upgrades a row to "resolved"; it only records what source presence shows.**

| ID | Accepted triage label (inherited, **not authoritative**) | Current delta found | Retained state now | Next exact acceptance action |
| --- | --- | --- | --- | --- |
| **BE-22** (L) | `R` in the accepted table — **explicitly unaccepted by the coordinator** (table R vs partial prose). | Register's original close criteria cite `driver.py:516-590, 1553-1598, 1929-2002` with *"Entity creation duplicated 3x, `cec_sender` closure 2x"*. Fresh: only **1929-2002** carries `cec_sender` (**2 occurrences — reproduces**); **516-590 and 1553-1598 contain no entity-creation and no `cec_sender` code**. `driver.py` (105 469 B) now holds `_power_entities` (407), `build_entities` (879), `install_entities` (902), `cec_sender` at lines 79/642/643/1935. The accepted triage's evidence string *"entities.py single factory"* does **not** reproduce under that name: `entities.py` (46 672 B) has **no** `EntityFactory` class and three build functions (`build_compatible_entities`, `build_entities`, `build_ucapi_entities`). | **Unaccepted residual.** Neither `R` nor `P` is inherited. The "3× duplication" element is an **unverified source-inspection lead** (cited anchors do not carry it); the "`cec_sender` closure 2×" element **does** reproduce. | **Coordinator** re-evaluates BE-22 against the **original register condition** (not either label) via scoped source review; the 3× element needs a current line-anchored re-statement before any close. |
| **BE-26** (L) | `P` | Fresh exact counts: `range(1, 9)` = **68 in `src/`**, **13 in `src/hub/`**, literal `[0]*8` = **0**, `192.168.0.100` = **2**. The count is **identical at the historical base (68/68)**. The register text says *"~62 range(1, 9) / [0]*8"* and the accepted triage said *"13× in src/hub, 35× in src"* — **the "35×" figure does not reproduce**. | Underlying condition (hard-coded range present) is **source-supported**; the **numeric figures** in both the register text and the accepted triage are **unverified/approximate**. | Coordinator register-text correction (counts) — **text only**; the residual hard-coded range is the existing author-scope item. |
| **API-19** (M) | `R` | `src/rest_api/control.py` is the one changed product file. Fresh: `run_rest_action` ×2 in it → the cited presence **still holds**. | `R` (source + scoped accepted R-track/campaign proof) remains **source-supported**; unchanged by the VAL-14 correction. | Coordinator register-text reconciliation, as inherited. |
| **API-25** (M) | `R` | Register condition: two target formats (`"input:3"` vs `"input_3"`) and *"the hub validates neither"*. Fresh: `profiles.py` has **0** `input:` and **4** `input_`; `input:` appears in `src/config.py` and `src/rest_api/static.py`; `_validate_cec_config` validates **structure only** (known keys, list fields) and **never the target format** → *"validates neither"* **still holds**. | The accepted `R` label does **not** meet the register's stated condition. **Retain as source-inspection lead**, not resolved. | Author-scope format normalisation + the register's own validation condition; coordinator close only after the **original** condition is met. |
| **SEC-14** (H) | `R+OW` (owner: GitHub-Support cache purge) | Fresh: `LICENSE` = **16 726 B**, contains "Mozilla Public License", contains **no** "stub" → the register clause *"LICENSE is a stub"* is **stale**. The public-history purge verification is **inherited** from the accepted historical report and was **not re-run here** (no exhaustive public-history/secret-scan authority). | Vendor-history/licensing element: **accepted historical reference, unchanged**; the remaining owner action (GitHub Support cache purge) is **unchanged**. No legal conclusion is drawn. | Owner-only cache purge (exact register checkbox). Coordinator register-text fix for the stale LICENSE clause. |
| **SEC-15** (L) | `R` | Fresh: **42/42** `uses:` entries are **SHA-pinned** (0 tag-pinned); the single external base image is digest-pinned (`python:3.12-slim@sha256:a6e34c…`; other `FROM` lines are internal stages) → register clauses *"CI actions tag-pinned"* and *"base image not digest-pinned"* are **stale**. | `R` **source-supported**; register text stale on two clauses. | Coordinator register-text reconciliation (text only). |
| **DEP-05** (M) | `R` | The register's cited location `.github/workflows/docker-publish.yml` **no longer exists** — only `ci.yml` is tracked (last commit touching it `d1889c62`). Fresh: `ci.yml` has `pull_request`/`push`/`workflow_dispatch` and jobs `lint, typecheck, test, uc, ha-test, hassfest, hacs, hygiene, gitleaks, docker-build, ui, validation…`; `mypy src/` with `continue-on-error: true` nearby → clauses *"no pull_request trigger"*, *"no hassfest/HACS validation"*, *"no gitleaks"* are **stale**; *"mypy non-blocking"* is source-supported; *"ruff only on `src/`"* not re-verified (ruff runs `ruff check --output-format=github $paths`). | `R` **source-supported** for the CI-scope clauses; the ruff-scope clause remains a **source-inspection lead**; the register **location** is stale. | Coordinator register-text reconciliation (location + clauses, text only). |
| **UI-09** (L) | `S` | Fresh: **9** named dead JS files still present (`about-dialog`, `context-menu`, `empty-state`, `floatable`, `presets-panel`, `quick-actions-drawer`, `settings-panel`, `setup-wizard`, `system-shortcuts-panel`) → register's *8* listed names (one "mostly") are **approximate**; the accepted triage's 9 reproduce. | `S` (source presence; **behaviour not reproduced**) **unchanged**; register list count approximate. | Author Phase-5 scope, as inherited. |
| **UI-13** (L) | `S` | Fresh: **53** `<script` tags, **0** `type="module"` → the accepted triage's 53 reproduces; the register's *"~50"* is approximate. | `S` unchanged. | Author Phase-5 scope, as inherited. |
| **UI-16** (L) | `P` | Register **text** says *"no reduced-motion check"* — **stale**. Fresh `web/js/tron-background.js` (39 882 B): `prefers-reduced-motion` ×2, `this.maxFps = 30`, `this.frameInterval = 1000 / this.maxFps`, `setShadowBlur()` capped at `lowPowerMaxShadowBlur = 4` → the **Phase column's** WP-E2 claims are source-confirmed. The register's remaining open items (*"render only while the cycles move"*, *"lazy-load the editors"*) were **not** verified here. | `P` **confirmed and unchanged** (WP-E2 landed); register text stale; residual items **unverified** → retained lead. | Author scope: finish the two residual items; coordinator text fix for the stale clause. |
| **UC-10** (M) | `P` | Register **text** says the strict xfail *"XPASSed without a fix"*; the **Phase cell** says *"the first-toggle bug is fixed in WP-B2"*. Fresh: `tests/uc/test_commands.py::test_media_player_first_toggle_does_not_turn_the_tv_off` **present**; scenario `remote.media_player_toggle` referenced in `tests/validation/scenarios/remote.py` → source presence supports the **Phase cell**; the text cell's caveat is not re-verified behaviourally. | `P` **source-supported**; the register cell pair is internally mixed. Routing/CEC split remains **agreed DI-9** work. | Author scope under the agreed DI-9 direction (unchanged); coordinator text reconciliation for the cell pair. |
| **HIL-09** (C) | `R+HW` | Fresh: the WP-A4 web-interface family **is** in source (`tx stream` 2, `tx hdcp` 2, `set hdr conversion` 3, `set video scaler` 4, `set arc` 3, `set output audio mute` 2, `set edid` 4, `lcd on time` 5, `set ext-audio` 10) **and** part of the old family remains (`copy edid` 2, `copy_edid_from_output` 2, `edid_copy_from_output` 6), while `set output stream/hdcp/hdr/scaler/mute`, `set input edid`, `set output exa*` are **absent (0)**. So **both** families coexist — the register's own text lists `copy edid` among commands that "get no answer". | Still a **genuine physical gate**: source presence cannot decide which commands the firmware answers. The accepted `R+HW` label is **not** a hardware proof. | Capture-tool hardware write run + read-back (`tools/hil/README.md`); validation/HW. **No simulator/header prose close.** |

## 6. Carried 59 — no material delta (47 rows)

For these, the register text is byte-identical to the historical base **and** every cited source file is
byte-identical, so the accepted triage's source-presence statements carry over unchanged. They are **inherited
triage, not re-qualified by this report**; any row whose acceptance depends on original evidence bytes rather
than source presence was **not** re-verified here.

| Class (accepted label) | IDs | Next exact acceptance action (unchanged) |
| --- | --- | --- |
| `R` (resolved, register reconciliation pending) | BE-16, BE-24, BE-33, API-12, API-20, PER-04, DEP-07, TST-03, TST-04, UC-11, UC-18 | **Coordinator** register-text reconciliation (text only). |
| `R+HW` (code present, physical proof pending) | BE-14, BE-15, BE-25, HIL-03 | Hardware write run + read-back; validation/HW. |
| `R+OW` (owner action pending) | API-07 | **Owner**: the register's exact close condition — *"close once the owner approves the visual diff of the affected catalog entries"* (verbatim condition present in the current register). No broader/invented owner gate. |
| `P` (partial, residual remains) | BE-20, BE-23 | Author scope for residual removal of the retained legacy path. |
| `S` (source-inspection candidate, **behaviour not reproduced**) | API-16 (5+3+1 = 9 handlers), API-18, API-21, UI-05, UI-06, UI-07, UI-08, UI-10, UI-11, UI-12, UI-14, UI-15, UI-18, UI-19, UI-20, UI-21, UI-33, UI-34, UI-35, UI-36, UI-38, UI-39, UI-40, UI-41, UI-42 | Author Phase-5 scope. **Not** current defects — no behaviour was exercised. |
| `DI9` (planned Phase-4 under the **agreed** DI-9 direction) | UC-12, UC-13 | Author scope under the owner-set 2026-09-25 direction; R3 "preserve approved IDs" compatibility preserved. Owner involvement only at the §4.3 exact removal/rename list before implementation. |
| `PHY` (physical / SDK observation pending) | UC-28, HIL-14 | Real Remote (V4) / next HIL session; validation/HW. HIL-14's fixtures `tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/probe/{http_no_session,session_idle_expiry}.json` **exist** (source presence), which is not a fresh observation. |

## 7. Bounded intake references (no authority granted here)

- **Public history / licensing.** SEC-14's vendor-blob purge and MPL-2.0 status are **inherited accepted
  references** from the accepted historical report; the remaining GitHub-Support cache purge stays an **owner
  action**. This unit ran **no** exhaustive public-history or secret scan, drew **no** legal conclusion,
  restored **no** purged bytes, and read **no** credentials, raw validation, image or archive payloads.
- **Owner / SDK / hardware.** API-07 owner visual diff, UC-28 real-Remote (V4), HIL-03/09/14 hardware and the
  SEC-14 cache purge remain the stated gates. The **DI-9 direction and compatibility constraint are preserved as
  agreed**; no new or broad owner gate is invented; **closed original 3-Tron decisions are not reopened**.
- **Historical vendor/reference presence is not an active runtime defect.** Legacy/reference files are
  deliberately retained; their presence proves only that a change has not landed.
- New current static metadata (counts, greps, diffs) is **not** original evidence and **not** function proof.

## 8. Calibration items that remain unaccepted

1. **BE-22** — accepted-table `R` vs partial prose (already recorded unaccepted by the coordinator). Fresh
   checks add: the register's `cec_sender` **closure 2×** reproduces at `driver.py:1929-2002`, its other two
   cited ranges carry no entity-creation/`cec_sender` code, and the accepted triage's *"single factory"*
   evidence string does not reproduce under that name. Use the **original register condition**; inherit
   **neither** label.
2. **External-gate shorthand count** — the accepted report's §7 shorthand external-gate count does not
   enumerate its own listed gates consistently. It is **not** used as an authority here; this report uses the
   per-row original conditions only.
3. **Count figures** — BE-26's *"~62 / [0]*8"* and the accepted *"35× in src"* do not reproduce (fresh: 68 in
   `src/`, 13 in `src/hub/`, 0 literal `[0]*8`, identical at the historical base). UI-13's *"~50"* (fresh 53) and
   UI-09's 8-vs-9 file list are approximations of figures that otherwise reproduce.

## 9. Honest limits

- **Zero runtime defects reproduced. Zero product tests executed for findings.** Every "source present"
  statement above is file/count/presence inspection only; none establishes an active runtime path.
- Full row-level re-verification of the **47 no-delta rows** was **not** performed beyond the byte-identity
  proof of their cited source files; rows whose acceptance rests on original evidence bytes are **inherited,
  not re-qualified**.
- The historical 59-row triage remains **accepted as triage only, with limits**; this report neither
  strengthens nor weakens it, and it is **not** re-run as new qualification.
- Nothing here is a finding closure, a source/security qualification, a feature promotion, a parent/package
  close, or an owner/release approval. Missing exact proof remains **unknown**.
- Independent qualified **OpenAI/Astra** factual review at the **exact report commit** is required.
  **This report is not self-accepted.**

## 10. Publication

Author only. New tracked output: `docs/production/software-waves/SW-FINDINGS-01/execution-20261101/AUTHOR.md`
only; private inspection metadata under `build/software-waves/SW-FINDINGS-01/execution-20261101/author/**` and
`C:/t/exec-sw-findings-01/nov02-attempt01/**` (both ignored/untracked). No push, merge, tag, cleanup, ledger
generation or registry edit. The accepted historical report, correction and coordinator disposition, the
register, the pending YAML, `features.yaml`, the ledger and all evidence/baseline bytes are **unchanged**.
