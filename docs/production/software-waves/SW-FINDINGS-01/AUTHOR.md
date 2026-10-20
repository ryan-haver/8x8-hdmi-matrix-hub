# SW-FINDINGS-01 — parser-open register reconciliation (author report)

**Task:** `task_e1bec78af179` · **Dispatch:** `ctx_07bca220949e` · **Base SHA:** `97e617c2276c7b1e015bb4a9419cb9820deafdee`
**Worktree:** `ryan-haver/wp-sw-findings` · **Authored:** 2026-10-20 UTC · **Effective provider/model:** `deepseek/deepseek-v4-pro` (default variant)

## 1. Scope and authority

Independent source/evidence reconciliation of the **59 parser-open findings** returned by
`tools.validate.registry.load_findings()` at the exact base. This is a **report-author
task only**: no product, test, runner, client, registry, ledger, finding, plan, baseline,
or metadata edit. Product/tests/runner/clients/registry/ledger/findings/plans/baselines/
root metadata/old evidence/settings/private runtime are read-only. The sole writable new
file is this report (`docs/production/software-waves/SW-FINDINGS-01/AUTHOR.md`).

This report does **not** close any finding, regenerate the ledger, edit the register, or
approve hardware/visual/field gates. It feeds corrective software scopes by stating, per
finding, whether the source now reflects an accepted resolution (awaiting register
reconciliation), a still-reproducible software defect, missing proof, or an external
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
  `RUNTIME_REVIEW_RESTORATION.md` (referenced), `planning-manifest.json` (static allocation
  only; not treated as evidence). No test was run and no physical/visual gate was performed.
- **Limits:** line-level code presence was verified for every "resolved" claim in §6. Full
  re-execution of the 4,041-test campaign or physical HIL is out of scope here. Where a
  claim rests on the accepted R-track records rather than a fresh run, §6 says so. The
  `config-sources.txt` inherited credential data was **not** read or exported.

## 3. Disposition summary

| Bucket | Count | Meaning |
| --- | --- | --- |
| Resolved (register reconciliation) | 16 | Code/evidence now reflects the fix; only the register row text is stale |
| Resolved, physical proof pending | 5 | Code fix landed (WP-A4/R-track); a hardware write/live-CEC run is the missing proof |
| Resolved, owner action pending | 2 | Code/repo fixed; an owner-only step (visual approval, GitHub Support purge) remains |
| Partial | 5 | Fix landed in the active path but a residual (legacy file, hard-coded range, DI-9 split) remains |
| Current reproducible defect | 27 | Still present in source (mostly Phase 5 UI + a few Phase-1/4 residuals) |
| External restriction | 4 | Owner DI-9 decision / SDK limit / hardware session required |

Total **59**. There is **no** assertion that all rows are fixed; 27 remain reproducible
defects and 9 are gated on hardware/owner/SDK.

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
so the parser keeps them open.

At the same time, several rows are **still accurate current defects**: API-16
(`sys.path.insert` in 9 handlers), API-21 (`scenes_v2.py` still defines its own async
`_json_response` at line 212), API-18 (`config.SceneManager` still present), and all 25
Phase-5 UI rows (dead JS files still present; `index.html` still uses 53 classic `<script>`
tags with 0 ES modules). The Phase-4 retirement of `driver.py`/`src/integrations/` was
deliberately deferred ("keep the file unchanged as a reference until the coordinator
decides its retirement", RUNTIME_CONTRACT §1), so BE-20/22/23 residual dead code is real.

### 4.1 SEC-14 (H) — vendor history / LICENSE

Repo purge **done** and verifiable: `git rev-list --objects --all` shows no `XP3.exe`,
`.exe`, `.c4z`, `.har`, `.bin`, `RTI`/`Control4`/`User_Manual`/`Firmware` blobs; the only
"BK-808" paths are the project's own golden capture fixtures
(`tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/`). `LICENSE` is full **MPL-2.0**;
`docs/vendor/README.md` documents the removal with SHA-256 checksums (project's own words).
Remaining item is **owner-only**: ask GitHub Support to purge cached views/refs (register §6
checkbox, still `[ ]`). Disposition: **resolved + owner action**.

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
is a next-HIL-session observation. These are **not** closable from simulator/header prose.

### 4.4 BE-16 (M) / TST-03 (M)

BE-16: `NameStore` (`src/hub/core/name_store.py`) is wired into `MatrixService`
(`matrix_service.py`), and rename propagation to the Remote is covered by UC-08
(`tests/uc/test_state_sync.py`). TST-03: every previously-untested module now has a suite —
`tests/sim/test_sim_scenes_v2.py` (scenes v2), `tests/test_security_v3_auth_scenarios.py` +
`test_security_access_and_guards.py` (settings), `tests/test_task_supervisor.py`,
`tests/sim/test_sim_ws_contract.py` + `tests/test_hub_events.py` (WS broadcast/state push),
`tests/uc/*` (UC setup handler, poller, api_client/entities), `tests/test_hub_integrations_framework.py`
+ `tests/test_flic_registry.py` (`/api/integrations`). Both are **resolved, awaiting register
reconciliation**.

### 4.5 Protocol rows whose fix is code-only, proof deferred

BE-14 (`OUTPUT_CEC_COMMANDS` six-key display table in `src/cec_commands.py`), BE-15
(`device_codes.py` audio-only scaler 4↔5), BE-25 (`edid_copy_from_output` = 39+N), API-07
(`LCD_TIMEOUT_15S` + "LCD: 15s" label, key `lcd_timeout_10s` preserved) are all present in
code. Their open status is a **hardware (BE-14/15/25) or owner-visual (API-07)** proof gap,
not a code defect.

## 5. Full reconciliation table

Legend: **R** resolved (register reconciliation) · **R+HW** resolved, physical proof pending ·
**R+OW** resolved, owner action pending · **P** partial · **D** current reproducible defect ·
**X** external restriction. "Next owner" is the party that can move it: **coordinator**
(register/ledger text), **author** (future software wave), **validation/HW** (physical
evidence), **owner** (decision/access/legal).

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
| API-07 | M | R+OW | `src/system_shortcuts.py` `LCD_TIMEOUT_15S`, "LCD: 15s" | owner visual approval of catalog entries | owner |
| API-12 | M | R | `src/scene_manager.py` `_SCENES_FILE="scenes_v2.json"` + `migrate_legacy_file` | register text reconciliation | coordinator |
| API-16 | L | D | `sys.path.insert` still in `audio.py`(5)/`outputs.py`(3)/`cec.py`(1) | remove per-request insert; regression test | author |
| API-18 | L | D | `src/config.py:258` `class SceneManager` still present | delete v1 SceneManager | author |
| API-19 | M | R | `run_rest_action` used in profiles/scenes_v2/scenes/macros/system_shortcuts/control; `domain/action_runner.py` | register text reconciliation | coordinator |
| API-20 | M | R | `src/hub/domain/visibility.py` wired (hub/domain/__init__.py; cec_macros.py, config.py) | register text reconciliation | coordinator |
| API-21 | L | D | `src/rest_api/scenes_v2.py:212` still defines async `_json_response` | unify on one envelope | author |
| API-25 | M | R | `src/rest_api/profiles.py:192` `_validate_cec_config` + call at 516 | register text reconciliation | coordinator |
| PER-04 | M | R | `src/hub/persistence/migrations.py` + `startup.py` (R2) | register text reconciliation | coordinator |
| SEC-14 | H | R+OW | purge verified (`git rev-list`); `LICENSE` MPL-2.0; `docs/vendor/README.md` | owner asks GitHub Support to purge cached views | owner |
| SEC-15 | L | R | `.github/workflows/ci.yml` gitleaks job; `Dockerfile` digest-pinned; SHA-pinned actions | register text reconciliation | coordinator |
| DEP-05 | M | R | ci.yml: gitleaks/hassfest/HACS jobs (SHA-pinned), pull_request | register text reconciliation | coordinator |
| DEP-07 | M | R | `src/hub/runtime/config.py` address precedence (RUNTIME_CONTRACT §2) | register text reconciliation | coordinator |
| TST-03 | M | R | suites listed in §4.4 | register text reconciliation | coordinator |
| TST-04 | M | R | `tests/e2e/*.spec.ts` (7) + `smoke.spec.ts` | register text reconciliation | coordinator |
| UC-10 | M | P | first-toggle fixed (WP-B2); DI-9 routing/CEC split still pending | owner DI-9 entity-model decision | owner |
| UC-11 | M | R | `src/hub/integrations/unfolded_circle/mdns.py` clean unregister | register text reconciliation | coordinator |
| UC-12 | L | X | `entities.py` legacy IDs/names retained (R3 "preserve approved IDs") | owner DI-9 rename/button-map approval | owner |
| UC-13 | L | X | `entities.py` still `ucapi.Sensor` (`sensor.input_N_signal` etc.), not binary | owner DI-9 binary-sensor decision | owner |
| UC-18 | H | R | `src/hub/integrations/unfolded_circle/bridge.py` + `hub_client*`; 100 UC tests | register text reconciliation (+ old path removal) | coordinator |
| UC-28 | M | X | ucapi has no entity-change event; `entity_change` attributes-only | verify on real Remote (V4); then DI-9 | validation/HW |
| HIL-03 | M | R+HW | `tests/test_telnet_real_captures.py` reads; set-command acks need write capture | hardware write capture | validation/HW |
| HIL-09 | C | R+HW | real command set in `src/` (WP-A4 part 2) | capture-tool write run + readback | validation/HW |
| HIL-14 | L | X | `probe/http_no_session`, `probe/session_idle_expiry` | next HIL session | validation/HW |
| UI-05 | M | D | 9 drawers + hidden `#settings-modal` + `settings-panel.js` still present | single settings drawer (DI-7) | author |
| UI-06 | M | D | `keyboard-shortcuts.js` still present (broken ids) | fix keyboard shortcuts | author |
| UI-07 | M | D | 27 Escape listeners; no focus-trap/ARIA on overlays | overlay stack + a11y (Phase 5) | author |
| UI-08 | M | D | `dashboard-manager.js` localStorage pins still live | single dashboard store (DI-5) | author |
| UI-09 | M | D | dead files present: `quick-actions-drawer.js`, `floatable.js`, `presets-panel.js`, `system-shortcuts-panel.js`, `about-dialog.js`, `setup-wizard.js`, `empty-state.js`, `context-menu.js`, `settings-panel.js` | delete dead JS | author |
| UI-10 | L | D | ~12k CSS lines; `components.css` 6.8k lines | CSS consolidation | author |
| UI-11 | M | D | `kiosk.html` still a parallel app | rebuild kiosk on shared core | author |
| UI-12 | M | D | two trackpads in `cec-tray.js`; two render paths in `routing-drawer.js` | one CEC remote component | author |
| UI-13 | L | D | `index.html`: 53 classic `<script>`, 0 `type="module"` (core modules exist in `web/js/core/` but unwired) | ES-module migration | author |
| UI-14 | L | D | three settings generations, 9 drawers | single settings drawer | author |
| UI-15 | L | D | `overlay-manager.js` hard-codes drawer list incl. dead drawer | remove dead drawer | author |
| UI-16 | L | P | WP-E2 partial (30 fps cap, reduced-motion, blur cap) in `tron-background.js`; render-while-moves + lazy-load open | finish perf items | author |
| UI-18 | L | D | `api-copy.js` hard-codes `http://host:8080` | relative base URL | author |
| UI-19 | L | D | `scene-editor.js` uses `prompt()` for step targets | searchable picker | author |
| UI-20 | L | D | `about-dialog`/`integrations-drawer` call `fetch` directly | route through api.js | author |
| UI-21 | L | D | PWA manifest absent | add manifest or drop claim | author |
| UI-33 | L | D | phone 390 px grid clips last column | responsive fix | author |
| UI-34 | L | D | kiosk ignores theme presets | apply theme presets | author |
| UI-35 | M | D | axe violations (aria-required-parent, contrast ×22, zoom disabled) | a11y pass | author |
| UI-36 | L | D | native `window.prompt()` passcode | styled prompt (with UI-01) | author |
| UI-38 | M | D | kiosk footer grows sideways with long names | responsive fix | author |
| UI-39 | M | D | iPhone kiosk header/edit strip wrap | responsive fix | author |
| UI-40 | L | D | iPhone kiosk "Keep Unchanged" clipped | responsive fix | author |
| UI-41 | M | D | iPhone grid input labels clipped | responsive fix | author |
| UI-42 | L | D | Tab A11 routing modal full-height clip | responsive fix | author |

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
verification basis for the "resolved" and "defect" columns in §5.

## 7. Honest gaps and non-boilerplate notes

- This is **not** a claim that all 59 rows are fixed. **27 remain current reproducible
  defects** (almost all Phase-5 UI simplification/responsive/a11y work, plus API-16/18/21),
  **5 are partial**, and **9 are gated on hardware/owner/SDK**. A "register reconciliation"
  close is appropriate only for the 16 "R" rows plus the code-complete parts of the R+HW/R+OW
  rows, and even those need the register text itself updated — which this task does not do.
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
- HIL-03/09/14 are **not** closed here and are not closable from simulator/header prose; they
  need the capture-tool hardware write-run and the next HIL session. No universal quiescence
  claim is added to the red alternate-client pre-fence disconnect probe.
- SEC-14's history purge and MPL-2.0 license are verified; the remaining GitHub-Support cache
  purge is an owner action and no legal conclusion is drawn. Public-history/license actions
  stay with the owner.

## 8. Publication

Author only; no push/merge/tag/cleanup performed. Commit recorded in the completion message
(`worker_done`). The register, ledger, and evidence bytes are unchanged.
