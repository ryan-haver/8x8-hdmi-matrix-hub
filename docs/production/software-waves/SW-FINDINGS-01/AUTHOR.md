# SW-FINDINGS-01 — parser-open register reconciliation (author report, corrected)

**Task:** `task_185e93ca5a0c` (correction) / original audit `task_e1bec78af179` · **Dispatch:** `ctx_6cee9d4ae624` (correction) / original `ctx_07bca220949e`
**Original base SHA:** `97e617c2276c7b1e015bb4a9419cb9820deafdee` · **Original report commit (preserved, unamended):** `8f23ae8976a4056f7dd7793ad3733c730594f42d`
**Correction base:** `8f23ae8976a4056f7dd7793ad3733c730594f42d` · **Worktree:** `ryan-haver/wp-sw-findings` · **Corrected:** 2026-10-20 UTC
**Effective provider/model:** `deepseek/deepseek-v4-pro` (default variant)

## 0. Coordinator independent review correction

This report was corrected after coordinator independent review. The original
report commit `8f23ae8976a4056f7dd7793ad3733c730594f42d` is **preserved and not
amended**; this is a new report-only commit under the live correction authority.
Three corrections are made, and no source/test/registry/ledger/baseline/private
data was changed:

1. **"Current reproducible defect" → source-inspection candidate.** The method
   explicitly ran **no test**, yet 27 rows were labelled "current reproducible
   defect" and 25 UI rows were presented as confirmed-remaining. Source presence
   (dead files still in the tree, classic `<script>` counts, `sys.path.insert`
   still present, etc.) proves only that a change has **not landed** — it does
   not reproduce behaviour and does not establish the active runtime path, since
   legacy/reference files are deliberately retained. All 27 rows are re-labelled
   **S — source-inspection candidate (behavior not reproduced)** and the summary
   now states **zero new runtime defects were reproduced in this audit**.
2. **API-07 owner step restated exactly.** The LCD label rename (`"LCD: 10s"` →
   `"LCD: 15s"`) was already owner-approved in WP-C1. The single outstanding
   owner requirement is the register's own close condition: *"close once the
   owner approves the visual diff of the affected catalog entries"*. No new or
   broader owner-visual gate is invented.
3. **DI-9 pending-decision claims corrected.** UC-10/12/13 were classified as
   "owner DI-9 decision pending". In fact the DI-9 direction was **set by the
   owner 2026-09-25** (Remote = another front end of the web app; official UC
   patterns; binary sensors; button mapping; standard command names) and is
   **agreed**, not an unresolved owner choice. R3's "preserve approved IDs" is an
   already-agreed compatibility constraint. These are **Phase-4 (WP-C3)
   implementation** items; the only owner involvement is the §4.3 "exact
   removal/rename list approved before implementation", a future implementation
   gate. UC-28 remains a genuine physical gate (verify on a real Remote, V4).

The recalibrated 59-row summary (Section 3) and full table (Section 5) reflect
these corrections; counts add to 59.

## 1. Scope and authority

Independent source/evidence reconciliation of the **59 parser-open findings** returned by
`tools.validate.registry.load_findings()` at the exact base. This is a **report-author
task only**: no product, test, runner, client, registry, ledger, finding, plan, baseline,
or metadata edit. Product/tests/runner/clients/registry/ledger/findings/plans/baselines/
root metadata/old evidence/settings/private runtime are read-only. The writable files are
this report (`docs/production/software-waves/SW-FINDINGS-01/AUTHOR.md`) and the correction
note under `build/software-waves/SW-FINDINGS-01/correction/`.

This report does **not** close any finding, regenerate the ledger, edit the register, or
approve hardware/visual/field gates. It feeds corrective software scopes by stating, per
finding, whether the source now reflects an accepted resolution (awaiting register
reconciliation), a change that has not landed (source-inspection candidate only), missing
proof, planned Phase-4 work under an agreed direction, or an external
owner/hardware/licensing/SDK restriction. No Anthropic route, helper, subagent, MCP, or
fallback was used. Future software fixes need a separate exact-commit different-family
review; I am the author, not that reviewer.

## 2. Method, counts and limits

- **Parser:** `python -c "from tools.validate.registry import load_findings"` at the base.
  It reads `docs/REMEDIATION_PLAN.md` §4 tables plus `docs/validation/findings_pending.yaml`
  (empty). Result: **263 total, 59 open, 204 closed**.
- **Register source read:** all of `docs/REMEDIATION_PLAN.md` §4 (BE/API/PER/SEC/HA/DEP/TST/
  UI/DOC/UC/VAL/HIL). The 59 open rows are exactly: BE 10, API 8, PER 1, SEC 2, DEP 2, TST 2,
  UC 6, HIL 3, UI 25.
- **Source inspection (read-only):** `src/hub/**`, `src/rest_api/**`, `src/integrations/**`,
  `src/*.py`, `run.py`, `.github/workflows/ci.yml`, `Dockerfile`, `web/`, `docs/vendor/`,
  `LICENSE`; `git rev-list --objects --all` for vendor blobs. Targeted greps listed in §6.
- **Evidence read:** `docs/planning/RUNTIME_CONTRACT.md`, `RUNTIME_EXECUTION.md`,
  `docs/validation/RUNTIME_VALIDATION_INDEX.md`, `RUNTIME_FINAL_GATE_REVIEW.md`,
  `RUNTIME_REVIEW_RESTORATION.md` (referenced), `docs/audits/UC_INTEGRATION_AUDIT.md`,
  `planning-manifest.json` (static allocation only; not treated as evidence).
- **No test was run and no runtime defect was reproduced in this audit.** No physical/visual
  gate was performed. Every "S" disposition below is a **source-inspection candidate**: the
  source still contains the pre-change state, but no behaviour was exercised.
- **Limits:** line-level code presence was verified for every "resolved" claim in §6. Full
  re-execution of the 4,041-test campaign or physical HIL is out of scope here. Where a
  claim rests on the accepted R-track records rather than a fresh run, §6 says so. The
  `config-sources.txt` inherited credential data was **not** read or exported.

## 3. Disposition summary (recalibrated)

| Bucket | Count | Meaning |
| --- | --- | --- |
| Resolved — register reconciliation pending | 16 | Source inspected at this base **plus** scoped accepted original proof (named in §4); the coordinator validates and closes the register text — not automatic final acceptance from code presence |
| Resolved — physical/hardware proof pending | 5 | Code fix is in source; a hardware write/live-CEC run is the missing proof |
| Resolved — owner action pending | 2 | Code/repo fixed; an exact documented owner step remains (API-07 visual diff of affected catalog entries; SEC-14 GitHub Support cache purge) |
| Partial | 5 | Fix landed in the active path but a residual remains (legacy file, hard-coded range, DI-9 split, WP-E2 remainder) |
| Source-inspection candidate — behavior not reproduced | 27 | Source presence shows the change has **not landed** (mostly Phase-5 UI + API-16/18/21); no runtime behavior was reproduced in this audit |
| Planned Phase-4 implementation — agreed DI-9 direction | 2 | Owner set the DI-9 direction 2026-09-25; the exact removal/rename list is approved before implementation (WP-C3) |
| Physical/SDK observation pending | 2 | Requires a real Remote (V4) or the next HIL session |

Total **59** (16 + 5 + 2 + 5 + 27 + 2 + 2). **Zero new runtime defects were reproduced in
this audit.** The 27 "source-inspection candidate" rows are not asserted as confirmed
defects; the 23 "resolved" rows (16 R + 5 R+HW + 2 R+OW) are pending coordinator
register/ledger validation and are not closed by this report.

## 4. Key findings

The register is materially stale relative to the source at this base. The **Phase 4 "one
runtime" architecture is implemented** (`src/hub/` with `core/matrix_service.py`,
`core/name_store.py`, `core/event_bus.py`, `core/models.py`, `domain/action_runner.py`,
`domain/visibility.py`, `persistence/migrations.py`, `integrations/hub_client*.py`,
`integrations/unfolded_circle/bridge.py`), accepted through the R1–R6 tracks
(`docs/planning/RUNTIME_EXECUTION.md`) and exercised by the frozen `1baac3de` campaign
(4,041 core + 100 UC). `run.py` now delegates to `hub.cli`. Consequently many Phase-4
register rows (BE-16/24/33, API-12/19/20/25, PER-04, DEP-07, UC-11/18) describe an
architecture that has since been replaced, while their Phase columns still lack `✅`/`closed`
so the parser keeps them open. These are stated as **source inspected plus the scoped
accepted R-track/campaign proof, pending register reconciliation** — not as an automatic
close from code presence.

At the same time, several rows are **still not landed in source, but are not reproduced
here**: API-16 (`sys.path.insert` still in 9 handlers), API-21 (`scenes_v2.py` still
defines its own async `_json_response` at line 212), API-18 (`config.SceneManager` still
present), and 24 Phase-5 UI rows (dead JS files still present; `index.html` still uses 53
classic `<script>` tags with 0 ES modules). UI-16 is **partial**, not a confirmed defect:
WP-E2 already landed the 30 fps cap, reduced-motion and blur cap. None of these 27 rows
were behaviourally reproduced in this audit; they are source-inspection candidates. The
Phase-4 retirement of `driver.py`/`src/integrations/` was deliberately deferred ("keep the
file unchanged as a reference until the coordinator decides its retirement",
RUNTIME_CONTRACT §1), so BE-20/22/23 residual dead code is real **residual work**, not a
freshly reproduced defect.

### 4.1 SEC-14 (H) — vendor history / LICENSE

Repo purge **done** and verifiable: `git rev-list --objects --all` shows no `XP3.exe`,
`.exe`, `.c4z`, `.har`, `.bin`, `RTI`/`Control4`/`User_Manual`/`Firmware` blobs; the only
"BK-808" paths are the project's own golden capture fixtures
(`tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/`). `LICENSE` is full **MPL-2.0**;
`docs/vendor/README.md` documents the removal with SHA-256 checksums (project's own words).
Remaining item is **owner-only**: ask GitHub Support to purge cached views/refs (register §6
checkbox, still `[ ]`). Disposition: **resolved + owner action** (owner, GitHub Support
cache purge).

### 4.2 UC-18 (H) — modular path non-functional

The modular UC path is now the shipped path and functional: `src/hub/integrations/unfolded_circle/`
(bridge.py 37 KB, entities.py 48 KB, setup.py, state.py, mdns.py) + `hub_client*.py`; accepted
via R3/R4 (100 dedicated UC tests, plus the `1baac3de` campaign). Residual: the old
`src/integrations/unfolded_circle/` (`api_client.py`, `entities.py`) is still present as
unused dead code. Disposition: **resolved + residual dead-code cleanup** (BE-20).

### 4.3 HIL-09 (C) / HIL-03 / HIL-14 — hardware caps

HIL-09's code fix is present: `tx stream`, `tx hdcp`, `set hdr conversion`, `set video
scaler`, `set arc`, `set output audio mute`, `set edid`, `lcd on time`, `set ext-audio`,
`ext-audio switch` are all in `src/` (device web-interface command set, WP-A4 part 2). The
missing proof is the **capture tool's hardware write-run with readback**
(`tools/hil/README.md`). HIL-03 reads are proven (`tests/test_telnet_real_captures.py`) but
set-command acknowledgements still need a write capture. HIL-14 (whether login is required)
is a next-HIL-session observation. These are **not** closable from simulator/header prose;
they remain genuine physical gates.

### 4.4 BE-16 (M) / TST-03 (M)

BE-16: `NameStore` (`src/hub/core/name_store.py`) is wired into `MatrixService`
(`matrix_service.py`), and rename propagation to the Remote is covered by UC-08
(`tests/uc/test_state_sync.py`). TST-03: every previously-untested module now has a suite —
`tests/sim/test_sim_scenes_v2.py` (scenes v2), `tests/test_security_v3_auth_scenarios.py` +
`test_security_access_and_guards.py` (settings), `tests/test_task_supervisor.py`,
`tests/sim/test_sim_ws_contract.py` + `tests/test_hub_events.py` (WS broadcast/state push),
`tests/uc/*` (UC setup handler, poller, api_client/entities), `tests/test_hub_integrations_framework.py`
+ `tests/test_flic_registry.py` (`/api/integrations`). Both are **resolved in source with
scoped accepted proof, awaiting register reconciliation** (not auto-closed).

### 4.5 Protocol rows whose fix is code-only, proof deferred

BE-14 (`OUTPUT_CEC_COMMANDS` six-key display table in `src/cec_commands.py`), BE-15
(`device_codes.py` audio-only scaler 4↔5), BE-25 (`edid_copy_from_output` = 39+N) are all
present in code. Their open status is a **hardware (BE-14/15/25)** proof gap, not a code
defect.

API-07 (`LCD_TIMEOUT_15S` + "LCD: 15s" label, key `lcd_timeout_10s` preserved) is present in
code and the label rename was already owner-approved in WP-C1. The single outstanding item is
the register's exact close condition: **"close once the owner approves the visual diff of the
affected catalog entries"** (`docs/REMEDIATION_PLAN.md` §4.2, API-07). Disposition:
**resolved + owner action**, with no new or broader owner-visual gate invented.

### 4.6 DI-9 rows — agreed direction, not an unresolved owner decision

The DI-9 "Remote 3 design" direction was **set by the owner 2026-09-25** and is agreed, not
pending: the Remote is another front end of the web app, following official UC patterns
(binary status sensors, `button_mapping`, standard command names). R3's "preserve approved
IDs" is an already-agreed compatibility constraint, not an unresolved owner choice.
Accordingly:

- **UC-10** (media player mixes routing with TV CEC): the first-toggle bug is fixed (WP-B2);
  the routing/CEC split is **Phase-4 DI-9 implementation work** (WP-C3), next owner = author.
- **UC-12** (non-standard command names / no button mapping) and **UC-13** (text sensors
  instead of binary): Phase-4 DI-9 implementation work (WP-C3), next owner = author. The
  legacy IDs/names and non-binary sensors remain because R3 deliberately preserves approved
  IDs — an agreed constraint, not a pending owner decision. The only owner involvement is the
  §4.3 "exact removal/rename list approved before implementation".
- **UC-28** remains a genuine physical gate: verify on a real Remote (V4) whether renamed
  presets/ports update entities already added there, then decide with DI-9.

## 5. Full reconciliation table

Legend: **R** resolved (source inspected + scoped accepted original proof; register
reconciliation pending) · **R+HW** resolved, physical proof pending · **R+OW** resolved, owner
action pending (exact register close condition) · **P** partial · **S** source-inspection
candidate (change not landed; **behavior not reproduced in this audit**) · **DI9** planned
Phase-4 implementation under the agreed DI-9 direction · **PHY** physical/SDK observation
pending. "Next owner" is the party that can move it: **coordinator** (register/ledger text),
**author** (future software wave), **validation/HW** (physical evidence), **owner**
(decision/access/legal).

For **S** rows, the "Verified source/evidence" cell records **source presence only**
(file/count inspection) — it is not a behavioural reproduction and does not establish the
active runtime path.

| ID | Sev | Disposition | Verified source/evidence | Required acceptance | Next owner |
| --- | --- | --- | --- | --- | --- |
| BE-14 | M | R+HW | `src/cec_commands.py` `OUTPUT_CEC_COMMANDS` (6 display keys); UC-23 | live CEC run (`--include cec-live`) on BK-808 | validation/HW |
| BE-15 | M | R+HW | `src/device_codes.py` audio-only scaler 4↔5 | HIL-09 write/readback | validation/HW |
| BE-16 | M | R | `src/hub/core/name_store.py` → `matrix_service.py`; `tests/uc/test_state_sync.py` (UC-08) | register text reconciliation | coordinator |
| BE-20 | M | P | new `src/hub/integrations/unfolded_circle/` functional; old `src/integrations/unfolded_circle/` still present | remove dead `src/integrations/unfolded_circle` | author |
| BE-22 | L | R | `src/hub/integrations/unfolded_circle/entities.py` single factory; `driver.py` retained as reference | retire `driver.py` (coordinator decision) | coordinator |
| BE-23 | L | P | dead code still in retained `driver.py`/`orei_matrix.py`/`telnet_client.py` | retire legacy files | author/coordinator |
| BE-24 | L | R | `src/hub/integrations/unfolded_circle/entities.py` media_player state; R1 event bus | register text reconciliation | coordinator |
| BE-25 | L | R+HW | `src/device_codes.py` `edid_copy_from_output` = 39+N | HIL-09 write/readback | validation/HW |
| BE-26 | L | P | `src/hub/core/models.py` MatrixModel wired; `range(1,9)` still 13× in src/hub, 35× in src; `192.168.0.100` fallback in `cli.py`/`runtime/config.py` | remove hard-coded ranges/fallback (Phase 4) | author |
| BE-33 | L | R | R1 single refresh worker; R3 "no independent matrix poller" | register text reconciliation | coordinator |
| API-07 | M | R+OW | `src/system_shortcuts.py` `LCD_TIMEOUT_15S`, "LCD: 15s" (label rename owner-approved WP-C1) | owner approves the visual diff of the affected catalog entries | owner |
| API-12 | M | R | `src/scene_manager.py` `_SCENES_FILE="scenes_v2.json"` + `migrate_legacy_file` | register text reconciliation | coordinator |
| API-16 | L | S | `sys.path.insert` still in `audio.py`(5)/`outputs.py`(3)/`cec.py`(1) | remove per-request insert; regression test | author |
| API-18 | L | S | `src/config.py:258` `class SceneManager` still present | delete v1 SceneManager | author |
| API-19 | M | R | `run_rest_action` used in profiles/scenes_v2/scenes/macros/system_shortcuts/control; `domain/action_runner.py` | register text reconciliation | coordinator |
| API-20 | M | R | `src/hub/domain/visibility.py` wired (hub/domain/__init__.py; cec_macros.py, config.py) | register text reconciliation | coordinator |
| API-21 | L | S | `src/rest_api/scenes_v2.py:212` still defines async `_json_response` | unify on one envelope | author |
| API-25 | M | R | `src/rest_api/profiles.py:192` `_validate_cec_config` + call at 516 | register text reconciliation | coordinator |
| PER-04 | M | R | `src/hub/persistence/migrations.py` + `startup.py` (R2) | register text reconciliation | coordinator |
| SEC-14 | H | R+OW | purge verified (`git rev-list`); `LICENSE` MPL-2.0; `docs/vendor/README.md` | owner asks GitHub Support to purge cached views | owner |
| SEC-15 | L | R | `.github/workflows/ci.yml` gitleaks job; `Dockerfile` digest-pinned; SHA-pinned actions | register text reconciliation | coordinator |
| DEP-05 | M | R | ci.yml: gitleaks/hassfest/HACS jobs (SHA-pinned), pull_request | register text reconciliation | coordinator |
| DEP-07 | M | R | `src/hub/runtime/config.py` address precedence (RUNTIME_CONTRACT §2) | register text reconciliation | coordinator |
| TST-03 | M | R | suites listed in §4.4 | register text reconciliation | coordinator |
| TST-04 | M | R | `tests/e2e/*.spec.ts` (7) + `smoke.spec.ts` | register text reconciliation | coordinator |
| UC-10 | M | P | first-toggle fixed (WP-B2); routing/CEC split is Phase-4 DI-9 work (agreed direction) | DI-9 entity model (WP-C3) | author |
| UC-11 | M | R | `src/hub/integrations/unfolded_circle/mdns.py` clean unregister | register text reconciliation | coordinator |
| UC-12 | L | DI9 | `entities.py` legacy IDs/names retained (R3 "preserve approved IDs" — agreed) | Phase-4 DI-9 standard names + button_mapping; exact rename list approved before implementation | author |
| UC-13 | L | DI9 | `entities.py` still `ucapi.Sensor` (`sensor.input_N_signal` etc.), not binary | Phase-4 DI-9 binary sensors; exact removal list approved before implementation | author |
| UC-18 | H | R | `src/hub/integrations/unfolded_circle/bridge.py` + `hub_client*`; 100 UC tests | register text reconciliation (+ old path removal) | coordinator |
| UC-28 | M | PHY | ucapi has no entity-change event; `entity_change` attributes-only | verify on real Remote (V4); then DI-9 | validation/HW |
| HIL-03 | M | R+HW | `tests/test_telnet_real_captures.py` reads; set-command acks need write capture | hardware write capture | validation/HW |
| HIL-09 | C | R+HW | real command set in `src/` (WP-A4 part 2) | capture-tool write run + readback | validation/HW |
| HIL-14 | L | PHY | `probe/http_no_session`, `probe/session_idle_expiry` | next HIL session | validation/HW |
| UI-05 | M | S | 9 drawers + hidden `#settings-modal` + `settings-panel.js` still present | single settings drawer (DI-7, Phase 5) | author |
| UI-06 | M | S | `keyboard-shortcuts.js` still present (broken ids) | fix keyboard shortcuts (Phase 5) | author |
| UI-07 | M | S | 27 Escape listeners; no focus-trap/ARIA on overlays | overlay stack + a11y (Phase 5) | author |
| UI-08 | M | S | `dashboard-manager.js` localStorage pins still live | single dashboard store (DI-5, Phase 5) | author |
| UI-09 | M | S | dead files present: `quick-actions-drawer.js`, `floatable.js`, `presets-panel.js`, `system-shortcuts-panel.js`, `about-dialog.js`, `setup-wizard.js`, `empty-state.js`, `context-menu.js`, `settings-panel.js` | delete dead JS (Phase 5) | author |
| UI-10 | L | S | ~12k CSS lines; `components.css` 6.8k lines | CSS consolidation (Phase 5) | author |
| UI-11 | M | S | `kiosk.html` still a parallel app | rebuild kiosk on shared core (Phase 5) | author |
| UI-12 | M | S | two trackpads in `cec-tray.js`; two render paths in `routing-drawer.js` | one CEC remote component (Phase 5) | author |
| UI-13 | L | S | `index.html`: 53 classic `<script>`, 0 `type="module"` (core modules exist in `web/js/core/` but unwired) | ES-module migration (Phase 5) | author |
| UI-14 | L | S | three settings generations, 9 drawers | single settings drawer (Phase 5) | author |
| UI-15 | L | S | `overlay-manager.js` hard-codes drawer list incl. dead drawer | remove dead drawer (Phase 5) | author |
| UI-16 | L | P | WP-E2 partial (30 fps cap, reduced-motion, blur cap) in `tron-background.js`; render-while-moves + lazy-load open | finish perf items | author |
| UI-18 | L | S | `api-copy.js` hard-codes `http://host:8080` | relative base URL (Phase 5) | author |
| UI-19 | L | S | `scene-editor.js` uses `prompt()` for step targets | searchable picker (Phase 5) | author |
| UI-20 | L | S | `about-dialog`/`integrations-drawer` call `fetch` directly | route through api.js (Phase 5) | author |
| UI-21 | L | S | PWA manifest absent | add manifest or drop claim (Phase 5) | author |
| UI-33 | L | S | phone 390 px grid clips last column | responsive fix (Phase 5) | author |
| UI-34 | L | S | kiosk ignores theme presets | apply theme presets (Phase 5) | author |
| UI-35 | M | S | axe violations (aria-required-parent, contrast ×22, zoom disabled) | a11y pass (Phase 5) | author |
| UI-36 | L | S | native `window.prompt()` passcode | styled prompt (with UI-01, Phase 5) | author |
| UI-38 | M | S | kiosk footer grows sideways with long names | responsive fix (Phase 5) | author |
| UI-39 | M | S | iPhone kiosk header/edit strip wrap | responsive fix (Phase 5) | author |
| UI-40 | L | S | iPhone kiosk "Keep Unchanged" clipped | responsive fix (Phase 5) | author |
| UI-41 | M | S | iPhone grid input labels clipped | responsive fix (Phase 5) | author |
| UI-42 | L | S | Tab A11 routing modal full-height clip | responsive fix (Phase 5) | author |

## 6. Inspection commands (read-only, no writes)

```powershell
python -c "from tools.validate.registry import load_findings; ..."   # 263 total / 59 open / 204 closed
git rev-list --objects --all | Select-String -Pattern "\.exe$|\.c4z$|\.har$|\.bin$|XP3|RTI|Control4|User_Manual|Firmware"
Get-ChildItem src -Recurse -Filter *.py | Select-String -Pattern "name_store|visibility|MatrixModel|sys.path|range\(1, ?9\)|192.168.0.100|tx stream|tx hdcp|set hdr conversion|set video scaler|set arc|set output audio mute|set edid|lcd on time|set ext-audio|ext-audio switch"
Select-String .github/workflows/ci.yml -Pattern "gitleaks|hassfest|hacs"; Select-String Dockerfile -Pattern "@sha256"
Select-String src/scene_manager.py -Pattern "scenes_v2.json"; Select-String src/rest_api/profiles.py -Pattern "_validate_cec_config"
Get-ChildItem src/rest_api -Filter *.py | Select-String -Pattern "run_rest_action" | Group-Object Filename
Select-String web/index.html -Pattern '<script'; Get-ChildItem web/js -Recurse
```

No test was executed; no fixture/tooling/output was generated or committed. The
`git rev-list --objects --all` vendor sweep and the `Select-String` greps above are the
verification basis for the "resolved" and "source-inspection candidate" columns in §5.
Source presence is not a behavioural reproduction.

## 7. Honest gaps and non-boilerplate notes

- This is **not** a claim that all 59 rows are fixed. **Zero new runtime defects were
  reproduced in this audit.** 27 rows are **source-inspection candidates** (24 Phase-5 UI
  rows plus API-16/18/21) — the source still contains the pre-change state, but no behaviour
  was exercised, and legacy/reference files are deliberately retained. **5 are partial** and
  **4 are gated on physical/owner/SDK evidence** (BE-14/15/25 + HIL-03/09/14 are hardware;
  UC-28 is a real-Remote observation; SEC-14's GitHub-Support cache purge and API-07's visual
  diff are owner actions). A "register reconciliation" close is appropriate only for the 16
  "R" rows plus the code-complete parts of the R+HW/R+OW rows, and even those need the
  register text itself updated — which this task does not do.
- The single largest stale-text cluster is **Phase 4**: the register still frames BE-16/24/33,
  API-12/19/20/25, PER-04, DEP-07, UC-11/18 as "Phase 4" open work, but `src/hub/` implements
  it and `run.py` already runs `hub.cli`. That architecture is accepted (RUNTIME_EXECUTION)
  and campaign-tested (`1baac3de`, 4,041 core + 100 UC). The register needs the rows
  re-marked against the new architecture, not a code change.
- The **retained-legacy** items are real residual work, not falsely-closed: `driver.py`
  (105 KB), `src/integrations/unfolded_circle/`, `config.SceneManager`, and the hard-coded
  `range(1,9)`/`192.168.0.100` fallback remain in the tree (RUNTIME_CONTRACT §1 explicitly
  defers `driver.py` retirement to a coordinator decision). BE-20/22/23/26 are therefore
  **partial**, not resolved.
- **DI-9 is agreed, not pending.** The owner set the Remote-3 direction 2026-09-25 and the
  R3 "preserve approved IDs" constraint is already agreed. UC-10/12/13 are Phase-4 (WP-C3)
  implementation items; only the §4.3 exact removal/rename list awaits approval before that
  implementation. UC-28 remains a genuine real-Remote (V4) observation gate.
- HIL-03/09/14 are **not** closed here and are not closable from simulator/header prose; they
  need the capture-tool hardware write-run and the next HIL session. No universal quiescence
  claim is added to the red alternate-client pre-fence disconnect probe.
- SEC-14's history purge and MPL-2.0 license are verified; the remaining GitHub-Support cache
  purge is an owner action and no legal conclusion is drawn. Public-history/license actions
  stay with the owner.

## 8. Publication

Author only; no push/merge/tag/cleanup performed. Commit recorded in the completion message
(`worker_done`). The register, ledger, and evidence bytes are unchanged. The original report
commit `8f23ae8976a4056f7dd7793ad3733c730594f42d` remains preserved; this correction is a
separate report-only commit.
