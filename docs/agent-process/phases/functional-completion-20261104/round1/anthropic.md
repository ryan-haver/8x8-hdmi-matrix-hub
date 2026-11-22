# functional-completion-20261104 — Round 1 independent assessment (Anthropic)

**Status: an independent R1 planning contribution only.** This is not a consensus, an adopted plan, a qualification, a source acceptance, a dispatch, or any owner approval. It does not change product source, tests, registry, ledger, manifests, baselines or release state. The three-family R2 challenge, one complete hashed final plan and allocation, and the three R3 decisions on it are all still to come.

## 0. Provenance

| Item | Value |
| --- | --- |
| Task / Dispatch | `task_db6cadf2bd1b` / `ctx_0c24940765ab` (from the Orca preamble; the coordinator handle is `term_6ed8131e-3ab3-4693-8094-56cc10acd412`) |
| Assigned route | `claude` / `claude-opus-5-5` / `high`. The session reports model `claude-opus-5-5`. Scoped `.claude/settings.local.json` (SHA-256 `53d75479…bdfd`, unchanged, ignored) sets `effortLevel: high` and denies Agent/Task/Team/SendMessage/MCP. This is a self-report, not backend attestation. Native per-turn effort is not visible to me. |
| `wp-runtime-completion`, resolved once on entry (2026-11-04T16:46:39Z) | `afe24d4d202e6a0ae0a5102b15f76fb95ea9fe22` (local branch = `origin/wp-runtime-completion`). Its parent is the product baseline `9b783d723c81cc56ec86810b789fa31be41e75cc`. |
| Input packet | `docs/agent-process/phases/functional-completion-20261104/INPUT_PACKET.json` at `afe24d4d`: canonical Git LF SHA-256 `cb6a9871fdf8a4adfb181ab1fbf3abafb6c265323c27b543ebd62f9c68857dc4`, 22,328 bytes. **Verified equal.** |
| Packet inputs | All ten `inputs[]` Git blob SHA-256 values were recomputed at `9b783d72` and **all match** the packet (private receipt `input_hashes_at_9b783d72.txt`). |
| Worktree / branch | `wp-remediation-recovery-r1-anthropic` / `planning/remediation-recovery-r1-anthropic`, entry head `5097650314502686a845a714e638643d66087971` (my previous R3), clean. Earlier R1/R2/R3 reports, source and config are untouched. No checkout, reset or rebase. |
| Product reads | Everything was read from `9b783d72` with `git show` / `git grep`. My worktree's product code is an **older, untouched historical snapshot**: its `src/rest_api` and `src/hub` differ from `9b783d72`. I neither executed it nor cite it as product evidence. |
| Peer independence | I did not open, search for or read any new-phase peer R1 report path, and I did not read the OpenAI or MiniMax R1 task briefs. Only my own brief (`tasks/R1_anthropic.md`), the packet and the `ROUND1_PREFLIGHT.json` bindings record were read. |
| Private evidence | `build/remediation-functional-20261104/anthropic-r1/**` (ignored) and `C:/t/remediation-functional/anthropic-r1/**`. These hold metadata probes and receipts only, no production tooling or tests. |

## 1. Scope actually read, and what is not covered

**Read in full at `9b783d72` (semantic reads, not line counts):**

- **Packet and preflight:** `INPUT_PACKET.json` (every field and all 14 CR acceptance lists), `ROUND1_PREFLIGHT.json`, my task brief.
- **Plan:**
  - `COMPREHENSIVE_REMEDIATION_20261104.md`.
  - `REMEDIATION_PLAN.json`: all 14 issues with their evidence pointers, pins, status and dispatch state; all 8 stages; all 30 packages and 65 units with author/review route reservations, base rules and dependencies (tabulated privately in `package_unit_table.txt`); metadata, CI binding and capacity observation.
- **Recovery records:** `WS_COMPONENT_INTAKE_RESULT.json`, `PRIV_JUDGE_DELIVERY.json`, `D6_PROVENANCE_HOLD.json`, `PRIVACY_REASSESSMENT_BUDGET_REQUEST.json`.
- **Process config:** `REPO_CONFIG.json` (every key) and current `AGENTS.md` instructions.
- **Execution pins:** `EXECUTION_PINS.json`: routes, `review_bottleneck`, `qualification_failure_policy`, and pins `QUAL-ANTHROPIC-CORE-01`, `SW-API-READ-02/03`, `SW-SEC-AUTH-03`, `SW-UI-PRESENT-01`, `SW-HA-PREP-01/03`.
- **Gate status:** `EXECUTION_GATE_STATUS.json` (qualification, review, remediation and privacy-domain fields).
- **API034:** `RV-API034/.../SOURCE_REVIEW_DISPOSITION_20261103.json`.
- **CR-01 source:**
  - `src/rest_api/websocket.py` (all).
  - `src/rest_api/ws_request_work.py` (all, including the "Wiring (proposed)" section).
  - `src/rest_api/events.py` client, refresh and lifecycle (lines 120–335 and 550–581).
  - `src/hub/runtime/composition.py` refresh, operation and command (lines 180–320).
  - `src/hub/core/matrix_service.py::refresh_snapshot` start.
  - `src/rest_api/app.py::create_rest_app` (lines 230–300).
  - `docs/api/WEBSOCKET.md` `get_status` and `error` contract lines.
  - Callers: `tools/validate/runner.py::sync` (250–290), `web/js/core/ws.js::requestStatus`, `web/js/websocket.js::requestStatus`.
  - `tests/test_ws_request_work.py`: test inventory plus the 1,000-frame burst test body.
- **CR-02 source:**
  - `custom_components/hdmi_matrix/config_flow.py` (all), `api.py` (all), `__init__.py` (setup/unload/options).
  - `coordinator.py` error paths, `strings.json` config/options sections.
  - `src/rest_api/security.py` route levels, access level, middleware and `auth_status`/`auth_api_keys`.
  - `tests/ha/helpers.py` header and `tests/ha/test_config_flow.py` test inventory; `tools/validate/clients/ha.py` image pins.
- **CR-03 source:**
  - `web/js/components/keyboard-shortcuts.js` (all).
  - `web/js/app.js` component wiring (125–160) and tab rendering (286–300).
  - `web/index.html` viewport and tab buttons; `side-nav-drawer.js` tab specs.
  - `settings-panel.js` method list and `setupModal`; `profile-editor.js` `openNew`.
  - Visual catalog note for `dialog/keyboard-shortcuts`.
- **CR-04:** `tools/validate/evidence.py::redact` (95–140), `findings_pending.yaml` VAL-15, and the privacy chain `d6e78e0b..53853257` commit list and path stat.
- **CR-09/10:** `web/kiosk.html` viewport, `hacs.json`, HA `manifest.json`, `pyproject.toml` Python declarations, `requirements-test-ha.txt`, CI `PYTHON_VERSION` and HA-related job lines, `Dockerfile` `FROM`.
- **Attribution metadata:** `Co-Authored-By` trailers on every CR-01/02/03/04 target file and on every path the privacy chain modifies (private `authorship-trailers.txt` and `privacy-chain-paths-trailers.txt`).

**Not read, or only partly read (coverage limits):**

- `tests/test_ws_request_work.py` beyond its inventory and the burst test.
- `TransactionLock`'s implementation (I make no FIFO claim).
- The full `REMEDIATION_PLAN.json` package acceptance pointers in `FEATURE_CONTRACTS.json`.
- `docs/REMEDIATION_PLAN.md` §4, the 61 open findings individually, `EXECUTION_READINESS.md`, `RUNTIME_EXECUTION.md`, and the 545 KB `AGENT_ALLOCATION.md` beyond targeted qualification searches.
- The full comprehensive review report, CI artifact contents, and the UI CSS/ESLint debt baselines.
- HIL/soak runbooks beyond plan references; the D6 target `12ad507e` diff.
- The HA 2025.1.0 source. **My statements about which HA APIs exist in 2025.1.0 are memory, not verification.**

**Not run, by mandate:** product tests, runtime/canonical campaigns, ledger generation, the full core suite, the source hook, containers, browsers or HA. The only execution is the single docs-module prose check in §10, which runs against my historical checkout and is **not** product-baseline verification.

## 2. Bottom line

1. **CR-01, CR-02 and CR-03 are real, source-confirmed defects at `9b783d72`**, and each can be fixed in software with no hardware, credentials or owner input. The blocker for all three is staffing, not technique: there is **no currently demonstrated, conflict-free, task-qualified author/reviewer pair** for HA config-flow or browser-UI review. The pair for the WS wiring needs a staffing decision; it does not need new qualification for its reviewer.
2. **The WS (CR-01) wiring has a defensible path that respects D6.** It inverts the roles: Anthropic Opus, who authored the accepted component and is the conflicted family, *authors* the wiring, and OpenAI Astra, who already gave an accepted runtime review of the exact component, *reviews* it. The held Anthropic async-review qualification at `12ad507e` stays HELD and unnarrowed. This is a material staffing change, so it needs R2/R3.
3. **New disclosure for the pending owner privacy decision.** Every tool file the retained privacy chain modifies already carries Anthropic co-authorship trailers: `runner.py` 11 commits, `model.py` 10, `clients/api.py` 6, `evidence.py` 2, `clients/ha.py` 1. That is the same indicator class that holds D6. The proposed extra Opus privacy-review assessment would face this indicator. The owner should decide with that fact in view, and the coordinator should apply the D6 rule to it consistently.
4. **The same indicator affects CR-02.** `config_flow.py`, `api.py` and `__init__.py` carry Anthropic trailers. An Anthropic *review* of a Sol CR-02 fix needs an explicit, prospectively decided rule on historical-context conflicts. If peers reject that rule, CR-02 stays held. It must not be rerouted to an unqualified pair.
5. **Two packages can actually run while privacy and D6 are held:** CR-08 truth reconciliation (M3 author → Sol review; M3's earned planning/prose/inventory scope) and the CR-10 support-boundary probes (agent-run disposable containers, if the owner allows the image downloads). CR-03 is next ready once its first UI-review gate is decided.
6. CI green (14 success, 1 publish skipped) closes **none** of CR-01 to CR-13. The 89/120/198/96/12 counts are dated snapshots, not bug counts.

## 3. Findings by crosswalk item (CR-01 … CR-14)

Classes used below: **D** = real source defect; **E** = evidence, preparation or composition gap; **O** = owner gate; **P** = process/capacity.

### CR-01 — WebSocket `get_status` work bound (D, P1)

**Confirmed at `9b783d72`:**

- `websocket.py:29` keeps a module-global `_replies` set.
- `websocket.py:106-109` starts one unbounded `ws_get_status` task per TEXT frame.
- The `finally` block at `websocket.py:85-89` neither cancels nor waits for that connection's reply tasks.
- There is no app-owned shutdown for them: `install_event_stream`'s cleanup at `events.py:567-581` stops the poller and clients, not `_replies`.

**Refinement from the caller read.** The impact is more than task count. `EventStream.refresh` (`events.py:313-319`) calls `runtime.refresh(force_refresh=True)`. That runs inside `operation()` → `async with self.transaction` (`composition.py:225-243, 265-272`), the same guard every user `command()`/`protocol()` enters, and then forces `refresh_snapshot()`. A burst therefore **queues forced matrix reads that real user commands wait behind**. The client sees one `status` per frame, not one per burst. This is a latency and availability risk to matrix control, beyond memory. The magnitude is still unmeasured.

**Component state.** `ws_request_work.py` (exact reviewed blob `145845f4`, Anthropic-authored, Astra runtime review `ed697083` accepted) is integrated but **unwired**. `websocket.py` does not import it.

**Contract constraint the wiring must respect.** `docs/api/WEBSOCKET.md:26,88` defines `get_status` → `status` "after a fresh read", and `error` only for invalid JSON, an unknown command, or a failed read. The component's suggested wiring answers `OWNER_BUSY` with `error`. That is a **public contract change** for clients that legitimately send two requests (for example the web UI's `requestStatus()` after a failed command). `tools/validate/runner.py::sync` takes the first `status`/`error` after its mark as the answer, so a spurious busy `error` would turn into a false scenario precondition failure.

**Recommended policy:** coalesce, do not reject.

- Per owner, at most one read is in flight plus one "trailing" flag. A request arriving during an in-flight read sets the flag and is answered by exactly one fresh read that starts after that request.
- Per application, a single-flight forced refresh shared by every waiting owner, plus at most one trailing refresh.
- Admitted work is still bounded by `WsRequestWork`. Only `APPLICATION_BUSY` and `SHUTTING_DOWN` should ever produce `error` with the existing `"Matrix status not available"` message, which keeps the schema unchanged.
- If R2 prefers rejection, the contract and schema change is coordinator-owned and the docs must change in the same accepted candidate.

**Additional acceptance (on top of the packet's):**

- The 1,000-frame burst on one socket yields ≤2 forced `refresh_snapshot` calls, not 1,000.
- A route command issued during the burst completes within a stated bound.
- `runner.sync()` and the UI `requestStatus()` double-send still receive `status`.
- The close and app-shutdown drain reports show `remaining == 0` for cooperative work.
- The `_replies` global is removed.
- `tests/test_ws_request_work.py:871` (`..._does_not_use_the_component_yet`) is intentionally inverted, with the rationale recorded rather than silently deleted.

**Staffing and D6:** see §6, package FC-WS.

### CR-02 — HA API-key capability validation (D, P1)

**Confirmed at `9b783d72`:**

- `config_flow.py:54-73` `_probe` validates only `/api/health` and `/api/status/device`. Both are public reads (`security.py:90-131`: GET routes have no level), so **any key passes**.
- `api.py:51-71` raises `HubResponseError` unless the body is an envelope with `success: true`.
- `security.py:267-269` `auth_status` returns **bare JSON**: `{admin_pin_set, control_pin_set, session_level, device_remembered}`. So it cannot be read through `HubClient.get()`. It needs a dedicated raw reader.
- `session_level` already resolves `X-API-Key` validity through `access_level` → `api_key_valid` (`security.py:209-223`), including the env `API_KEY`/`CONTROL_API_KEY`. That makes the check nonmutating and exact.

**Additional source gaps found by this read** (not in the packet's evidence list):

1. **Options flow bypass.** `config_flow.py:132-136` accepts and stores a new `api_key` with **no validation at all**, and `__init__.py:28-31` prefers `entry.options[api_key]` over `entry.data`. Fixing setup and reconfigure alone leaves this hole.
2. **No reauth path.** The coordinator polls only public reads (`coordinator.py:103-115`), so a revoked key is invisible until a write fails with 401. Writes surface as generic errors. There is no `async_step_reauth`, and no `ConfigEntryAuthFailed` anywhere (`git grep` found none).
3. **Strings.** `strings.json` has no `api_key` field label in the `user`, `reconfigure` or `options.init` steps, and no `invalid_auth` / `auth_required` error strings. HA would show raw keys and untranslated error codes.

**Proposed resolution** (no product change here):

- Add `HubClient.auth_status()`, a raw JSON dict reader that accepts the bare shape, rejects a non-dict, and treats 404 as "hub too old: capability unknown".
- In `_probe`, after `health()`:
  - `control_pin_set` and a key that resolves to `session_level == "none"` → `invalid_auth`.
  - `control_pin_set` and no key → `auth_required`, a correctable form error, not an abort.
  - Control not locked and no key → success, as today.
  - Control not locked and a supplied key that resolves to `"none"` → **recommend** `invalid_auth`. The user typed a key that the hub does not recognize, and a later lock would silently break control. This choice is for R2; it is not an owner gate.
  - Auth status 404 on an older hub → keep today's behaviour, with a debug log.
- Apply the same check in `reconfigure` and in the options flow when `api_key` changes.
- Add `async_step_reauth` / `reauth_confirm`, started when setup sees an invalid key on a locked hub and when a control write returns 401.
- All of this is **nonmutating**: there are no unlock or login probes, and no PIN attempts, so `verify_pin` rate limits are never touched.

**Acceptance (complements the packet):**

- `tests/ha` real-`hass` cases for wrong, missing and revoked keys and a valid key on a control-locked hub, across user, reconfigure, options and reauth.
- Unlocked/no-key and matrix-offline cases continue to work.
- A 404 auth-status case on an older hub.
- The bare-JSON shape test uses an `auth_status` contract fixture **generated by `tools/gen_contract_fixtures.py`**, not hand-written (TST-02). Fixture generation is shared → it needs an exact serial lease.
- An HA-container scenario on a disposable control-PIN-locked hub covers the same flows.

**Staffing:** §6, package FC-HA. This is where the attribution indicator applies.

### CR-03 — Keyboard shortcuts (D, P2; existing UI-06 scope)

**Confirmed at `9b783d72`:**

- `keyboard-shortcuts.js:41-45`: `s` calls `window.settingsPanel.toggle()`. `window.settingsPanel` is never assigned (`app.js:141` stores the panel in `this.components.settingsPanel`), and `SettingsPanel` has **no `toggle()` method** (it has only `open`/`close`, `settings-panel.js:380,401`). So `s` is a no-op today, and would throw if the global were merely set.
- The legacy modal's trigger `#settings-btn` does not exist in `web/index.html`. The current settings surface is reached through `window.sideNavDrawer.open()` (`presets-drawer.js:91-92` and others).
- `keyboard-shortcuts.js:33-35`: `4` targets `[data-tab="scenes"]`. The tab id is `profiles` (`index.html:165`, `side-nav-drawer.js` tab specs), so `4` is a no-op.
- **Additional (already recorded, not in CR-03's evidence):** `?` never opens help. `?` arrives with `shiftKey: true`, so the id is `shift+?` and does not match the registered `?` (`keyboard-shortcuts.js:53, 158-167`). The visual catalog note `dialog/keyboard-shortcuts` records exactly this.
- `n` → `window.profileEditor.openNew()` is valid (`profile-editor.js:322,818`). `1`/`2`/`3` map to existing tab ids.
- Tabs are user-orderable and hideable (`app.js:292-300`). `.click()` on a hidden tab may navigate to a tab the user hid. **Unverified, needs a browser check.**
- The help overlay is not registered with `overlayStack`/`overlayManager`, and has no dialog role or focus trap. This is CR-09 accessibility scope, unverified in a browser.

**Resolution:**

- `s` → the surface the UI's visible Settings entry actually opens. The author confirms by browser reproduction; the likely target is `sideNavDrawer.open()`.
- `4` → `profiles` (and keep the label "Profiles/Scenes").
- Register `?` shift-insensitively.
- Optionally skip hidden tabs.

**Acceptance:**

- Playwright positive and negative tests for `s`, `4`, `?`, `1` (positive control), field suppression on input, textarea, select and contenteditable, and Escape blur/close-topmost.
- No visual baseline changes unless rendering changes. Any newly changed help-overlay rendering needs owner approval of new captures only.

### CR-04 — Validation credential redaction (D tooling, P0) — HELD

**Confirmed at `9b783d72`:** `evidence.py:113-130`. `_SECRET_KEYS` anchors `^(key|pin|…)$`, so `X-Admin-PIN` and any `*-pin` header survive while `X-API-Key`/`Authorization` are masked. `_SECRET_QUERY` covers query strings only, so free-text procedure strings that contain a PIN are not scrubbed.

**Retained fix:** the chain `d6e78e0b..53853257` (C1–C4, 8 commits, 13 paths, Sol-authored, no trailers) is **not** an ancestor of `9b783d72`.

**Gate:** HELD by the terminal Opus and M3 privacy-review FAILs and the unapproved owner budget. The M3 judge's useful F1 (Low, C4 public-field overmasking) is retained as an input to correction. **New disclosure:** see §2 item 3, and owner decision O-1.

### CR-05 — Three retained chains, serial integration (E, P0)

The plan's facts stand: API C1 ⊂ C2, privacy C1 ⊂ C2 ⊂ C3 (⊂ C4), and the API-read chain is independent.

- RV-API034 has a bounded PASS (Opus) and an accepted report-quality evaluation (`c3fcace6`), but its M-1 integration hold remains.
- WS040 review status is outside what I read beyond the plan's pointer, so I do not claim it.
- Integration order: (1) API chain after M-1 resolves through CR-06; (2) the privacy chain only after a qualified review and admission; (3) the new FC-WS/FC-HA/FC-UI fixes as each is accepted. Shared runner/model hunks are resolved centrally under one serial lease at a time.

### CR-06 — F-SEC-007 freshness (E, P0)

M-1 is evidence staleness (`ee3f2e7f` changed the covered runner/model), not a demonstrated security defect. It can run only after the covered tool code is frozen, which means after the privacy chain resolves, because both touch `runner.py`/`model.py`. Running it earlier wastes a campaign and violates "no regenerate between unfinished shared-tool edits". Dependencies: CR-04 → CR-05 → CR-07 candidate ref.

### CR-07 — Candidate-bound evidence (E, P0)

No change to the plan. The CI records name the synthetic merge `c9dac37a` (a non-ancestor). A fresh canonical run must happen on an explicitly checked-out accepted candidate ref, after A3 freezes the source. Do not edit the records. Reconcile the 56 historical attribution units separately (metadata work suitable for M3 → Sol).

### CR-08 — Truth reconciliation (E/P, P1) — READY lane

**Additional stale item:** `EXECUTION_GATE_STATUS.json.remediation_authority.state` still says "wave1 active: NEW bounded WS component authorship assessment…", although the component is integrated (`e54228c0`). Add it to the dated current-summary correction. The 61 parser-open records keep the plan's disposition vocabulary; HIL-09 keeps its 12 caps.

### CR-09 — UI/kiosk accessibility, mobile, persistence (D + E, P2)

**Confirmed source settings:**

- `web/index.html:7`: `user-scalable=no`. This blocks pinch zoom and is a likely WCAG 1.4.4 conflict.
- `web/kiosk.html:5`: `maximum-scale=1.0, user-scalable=no`.

Main UI: recommend removing zoom suppression. Kiosk: a deliberate wall-panel choice is plausible, so that is an **owner decision (O-2)**.

Everything else in CR-09 is a **hypothesis until browser-reproduced**: focus, modal semantics, contrast, offline/recovery, persistence. The help-overlay semantics from CR-03 are a concrete first case. A reproduction-only package comes first (no source edits), and its output decides which fixes to write. CSS/ESLint baselines are debt, not MVP blockers.

### CR-10 — Support boundaries (E, P1) — partly READY

**Confirmed declarations:**

- `hacs.json` declares HA `2025.1.0`.
- `tools/validate/clients/ha.py:65-66` documents `2025.1.4` as the "minimum version (D8)" check and defaults to `2026.9.3`. **That is a doc/data mismatch with the declared 2025.1.0 floor.**
- `tests/ha` pins HA `2026.2.3` on Python 3.13.
- `pyproject.toml:12,21` claims Python 3.11; CI core runs 3.12 and the image is `python:3.12-slim`.

**Host facts (my private probe):** Docker 29.6.2 linux/amd64 is available. No Python 3.11 interpreter is installed; `py` is absent and `uv` is present.

**Recommended path:**

- **HA floor:** run the existing HA-container client with `VALIDATE_HA_IMAGE=homeassistant/home-assistant:2025.1.0` pinned by digest. Cover install, setup, auth/reconfigure/options, unload/reload and HACS custom-repo upgrade. Then fix the `2025.1.4` comment. The author must verify, against 2025.1.0 source rather than memory, that `_get_reconfigure_entry`, `_abort_if_unique_id_mismatch`, `async_update_reload_and_abort(data_updates=…)` and the implicit `OptionsFlow.config_entry` exist there.
- **Python 3.11:** either run the core suite in a digest-pinned `python:3.11-slim` container, or revise `requires-python` to `>=3.12` and drop the 3.11 classifier through a compatibility decision. `pyproject.toml` is a coordinator-owned root manifest.

Both options need image downloads but no accounts or spend → owner decisions O-3 and O-4.

### CR-11 / CR-13 — Real-client, physical, soak and field (O)

Unchanged. Software preparation (SDK replay, auth/error/recovery scripts, sampler qualification for SW-SOAK-PREP-01) can proceed after A3/A5. Physical, 72-hour and week evidence is owner-only. Nothing here substitutes for it.

### CR-12 — Release closure (E + O)

The version sync is healthy (`1.0.0rc1` in the manifest). The dependency-advisory audit returned HTTP 403. A no-account alternative is `pip-audit`/`osv-scanner` against the public OSV database and `npm audit` against the public registry. These send the dependency inventory to an external service, which counts as publication → **owner decision O-5**. Final version, artifacts and release are owner-gated (O-7).

### CR-14 — Capacity and qualification (P)

See §7 and §8. The central constraint is that demonstrated qualifications are narrow:

- **Opus:** scoped API-refusal runner/model review, plus an accepted WS component correction.
- **Astra:** async/diagnostic report judgment, plus an accepted WS component runtime review.
- **Sol:** core author, plus bounded REST review.
- **M3:** planning, prose and inventory.

No family has a demonstrated HA config-flow or browser-UI *review* qualification.

## 4. Attribution conflict indicators (new consolidated evidence)

`git log` trailers at `9b783d72` (private `authorship-trailers.txt`). These are indicators only: a missing trailer proves nothing about who wrote a commit (for example, Codex commits without trailers), and native family attribution is not established for any of them.

| Path | Anthropic-trailer commits | Consequence |
| --- | --- | --- |
| `src/rest_api/websocket.py` | `c39ee8d5`, `323af8e4`, `dbf5349e` | The D6 basis; Anthropic must not be the independent reviewer of WS lifecycle code |
| `src/rest_api/app.py` | `323af8e4`, `bc3b9353` | Same |
| `custom_components/hdmi_matrix/config_flow.py`, `__init__.py` | `0f7372d8`, `dbf5349e` | An Anthropic review of a CR-02 fix faces the D6-class indicator |
| `custom_components/hdmi_matrix/api.py` | `3efdec21`, `0f7372d8` | Same |
| `tools/validate/evidence.py` | `6e0b0c23`, `8bf7886a` | The privacy review subject |
| Privacy-chain paths `runner.py`/`model.py`/`clients/api.py`/`clients/ha.py` | 11 / 10 / 6 / 1 commits before `d6e78e0b` | Bears on the pending extra-Opus privacy proposal |
| `web/js/components/keyboard-shortcuts.js` | none | No indicator for CR-03 |
| `web/index.html` | `5bef0fd0` | Only if CR-03/09 edits `index.html` |

**Proposed rule for R2/R3 (not adopted; for decision).** Independence is assessed against the authorship of the **exact change under review**. A historical co-author indicator on unchanged surrounding lines is disclosed, and it **blocks** a review only when the review's acceptance claim covers those historical lines. For example, D6 certifies an existing target, and the privacy review accepts the whole chain plus the redaction behaviour of pre-existing code. Under this rule D6 and the privacy proposal stay blocked, and an Anthropic review of a new Sol-authored CR-02 diff is allowed with disclosure. If R2 rejects the rule, CR-02 stays held (see §6). Either way it is a prospective decision, not a relabel.

## 5. Recommended program order and parallelism

```
FC-0  coordinator: R2/R3 adopt plan + conflict rule + first-domain gates; CR-08 dated summary; fresh quota
      │
      ├─ FC-1a  CR-08 reconciliation (M3→Sol)                [ready lane, metadata only]
      ├─ FC-1b  FC-WS  CR-01 wiring (Opus→Astra)             [after FC-0 staffing decision]
      ├─ FC-1c  FC-UI  CR-03 shortcuts (Sol→Opus, Astra-judged first UI review)
      ├─ FC-1d  FC-HA  CR-02 auth (Sol→Opus under the rule, Astra-judged first HA review) [or HELD]
      ├─ FC-1e  CR-10 probes (container runs; Astra author of the run report → Opus review) [needs O-3/O-4]
      └─ FC-1f  CR-09 browser reproduction report (Sol → Opus)  [no source]
      │
FC-2  privacy chain review/admission (CR-04/05)              [HELD: owner O-1]
FC-3  coordinator serial composition + freeze (CR-05)        [after accepted FC-1/FC-2 items]
FC-4  candidate-bound evidence CR-06/CR-07 + client contracts
FC-5  software RC (CR-08 final, CR-12 software parts)
FC-6  owner HIL / CEC / 72 h / field week (CR-11/CR-13)
FC-7  owner final release decision
```

- At most **2 new workers** at a time, plus the coordinator and the protected external slot (4 total), with no nesting. A practical sequence follows. Each step needs a fresh quota check and the previous step's slot positively released.
  1. FC-1a (M3) + FC-1b author (Opus).
  2. FC-1b review (Astra) + FC-1c author (Sol).
  3. FC-1c review (Opus) + FC-1c judge (Astra) after release.
  4. FC-1d author (Sol) + FC-1e run (Astra).
  5. FC-1d review (Opus) + judge (Astra).
- FC-1b, FC-1c and FC-1d have **disjoint source paths** (§6), so composition conflicts are unlikely. They still integrate serially in FC-3, one at a time, with combined checks after each.
- FC-2 does **not** block FC-1. FC-3 can freeze a candidate without privacy only if the owner accepts a staged candidate. Otherwise FC-4 waits for FC-2, because CR-06 needs the frozen tool code.

## 6. Proposed packages and staffing (exact, but subject to the fresh gates)

Common rules for every package:

- **Base.** Resolve `wp-runtime-completion` to a full SHA at creation (today `afe24d4d`; product `9b783d72`), with an ancestor-of-floor check.
- **Worktrees.** Dedicated Orca worktrees created by `worker-start` only.
- **Leases.** Exclusive leases are listed per package. The coordinator keeps contracts, root manifests and locks, `features.yaml`, `LEDGER.md`, `findings_pending.yaml`, `REMEDIATION_PLAN.md`, the allocation/config/state files, and integration.
- **Review.** Exact-commit different-family review; reviewers report and authors fix.
- **Correction reserve.** One author correction round plus one exact changed-commit re-review per package. No automatic qualification retakes.
- **Evidence.** Raw argv, exits, stdout/stderr, JUnit and original-temp hashes are preserved. No baseline changes.

| Package | Author (family) | Reviewer (family) | Exclusive author paths | Dependencies | Acceptance / evidence | Gate status |
| --- | --- | --- | --- | --- | --- | --- |
| **FC-WS** (CR-01) | Opus 5.5/high (Anthropic), original component author | Astra/high (OpenAI); accepted runtime review of the exact component `ed697083` | `src/rest_api/websocket.py`, `tests/test_ws_request_work.py` (the inverted guard only), new `tests/test_ws_get_status_bound.py`, report path. **Serial lease:** `src/rest_api/app.py` `create_rest_app` cleanup_ctx hunk | FC-0 decision; none in source | §3 CR-01: packet plus added acceptance; registry/route 100%; applicable REST/WS pipeline; `docs/api/WEBSOCKET.md` unchanged under the coalescing policy | **Needs R2/R3 staffing decision** (Anthropic-author/OpenAI-review is an existing conditional fallback). The D6 Anthropic async-review qualification stays **HELD** and is not narrowed. Wiring authorship competence is decided only by Astra's exact review. |
| **FC-UI** (CR-03) | Sol 6.1/high (OpenAI), keeps the SW-UI-PRESENT-01 author reservation | Opus 5.5/high (Anthropic); no indicator on `keyboard-shortcuts.js` | `web/js/components/keyboard-shortcuts.js`, new `tests/e2e/keyboard-shortcuts.spec.ts`, report path. `index.html` excluded unless proven necessary | FC-0 | §3 CR-03; pinned Playwright container; no baseline changes | **Opus has no UI-review qualification.** Proposal: a genuine **first-attempt** bounded UI-behaviour review assessment on this exact commit, judged by Astra under a frozen rubric (precedent: QUAL-ANTHROPIC-CORE-01, an OpenAI judge of an Anthropic review of Sol source). FAIL is terminal for the domain; Sol's fix then waits for another qualified reviewer, with no retake. |
| **FC-HA** (CR-02) | Sol 6.1/high (OpenAI), keeps the SW-HA-PREP author reservation | Opus 5.5/high (Anthropic), with the disclosed historical-context indicator | `custom_components/hdmi_matrix/{config_flow.py,api.py,strings.json,translations/en.json}`, `__init__.py` reauth hook, `tests/ha/test_config_flow.py`, `tests/ha/test_api.py`, report path. **Serial leases:** `tests/fixtures/api/` auth-status fixtures through `tools/gen_contract_fixtures.py` | FC-0 conflict rule; best after FC-1e confirms the 2025.1.0 floor APIs | §3 CR-02; `tests/ha` on Py3.13; HA-container scenario on a locked disposable hub; hassfest/HACS | **HELD unless R2/R3 adopt the §4 rule.** Then a first-attempt HA-review assessment judged by Astra. Alternative, also held: Opus authors and Sol reviews, but then a non-OpenAI judge for Sol's first HA review is needed, and M3 is not a qualified judge while Opus would be judging review of its own code. |
| **FC-SUP** (CR-10) | Astra/high (OpenAI; "runtime/artifact composition" route): runs and reports; no product source | Opus 5.5/high (scoped runner/harness competence is narrowly relevant to reading the run evidence) | Owned run roots; report path. `ha.py:65` comment fix via lease only if accepted | O-3/O-4 image downloads | 2025.1.0 and current-HA container flows; Py3.11 core-suite run or a recorded compatibility decision; raw receipts | **READY after O-3/O-4**, subject to quota. A fix to the `ha.py` comment is tooling and needs normal review. |
| **FC-A11Y-R** (CR-09) | Sol 6.1/high: reproduction report only | Opus 5.5/high | Owned evidence roots; report | FC-0 | Phone/tablet/kiosk sizes, zoom, focus, modal semantics, contrast, offline/recovery, persistence; browser action/request/state controls | **READY as a report** (a review of a reproduction report, not of source). Any fixes become later packages with their own gates. |
| **CR-08** | M3 (MiniMax; earned planning/prose/inventory) | Sol 6.1/high (existing SW-FINDINGS-01 pair) | A proposed disposition table under its own report path; the coordinator applies canonical edits | none | 61 open IDs × assertions/conditions/proof/disposition; dated current summary; stale field list (§3 CR-08) | **READY** (quota permitting) |
| **CR-04/05 privacy** | Sol (original author, corrections) | No qualified reviewer | — | O-1 | Unchanged packet acceptance | **HELD** |
| CR-06/07/11/12/13 | per plan (Sol/Astra authors; coordinator composition) | per plan | per plan | FC-3 freeze / owner | per packet | Future, after FC-3 / owner |

**Alternatives checked and rejected for now:**

- **Gemini/Antigravity** as a third review family. Gemini CLI OAuth is disabled; Antigravity reports 20% weekly remaining and its backend/helper route is unresolved. Not a verified fallback.
- **M3 as a source or privacy reviewer.** Its privacy domain FAIL is terminal, and it holds no source-review qualification.
- **DeepSeek.** Exhausted; never.
- **Same-family review.** Sol and Astra are one family, so Astra cannot review Sol's FC-UI/FC-HA source.

## 7. Capacity (dated, not funding)

The preflight observation at 2026-11-04T16:40Z (from `ROUND1_PREFLIGHT.json`; I did not re-observe it):

| Provider | Weekly used | Remaining |
| --- | ---: | ---: |
| Codex (OpenAI) | 16% | 84% |
| Claude (Anthropic) | 25% (session 0%) | 75% |
| MiniMax | 34% (session 1%) | 66% |

All are above 30% for now; a fresh check is still required before every start.

Demand in §5 is serial on Anthropic (FC-WS author, FC-UI reviewer, FC-HA reviewer, FC-SUP and FC-A11Y-R reviewer) and on Astra (FC-WS reviewer, FC-UI/FC-HA judge, FC-SUP author). Those two routes are the **bottleneck**. Their correction reserves (above) must be counted before each start, and the whole backlog must not be reserved against one reading.

Anthropic's weekly reset (`resetsAt` 1793966400083, about Fri 2026-11-06) is close; re-check before FC-1b and FC-1c.

## 8. Risks

1. **UI and HA review-competence gates may fail.** A FAIL is terminal for that domain under policy, and FC-UI/FC-HA then wait for a new qualified reviewer family. The only candidate is Gemini, which is held. Mitigation: propose the gates on small, well-specified diffs where good review is checkable.
2. **Coalescing semantics.** A trailing-read bug could silently answer with a pre-request snapshot. The tests must assert the "read started after request" ordering, not just the count.
3. **Hidden coupling** of FC-WS with the runtime `TransactionLock` (not read). The author must read it fully.
4. **HA API drift at 2025.1.0** (my API-presence statements are unverified). FC-SUP should run before FC-HA lands.
5. **Privacy hold length.** CR-06/07 and the RC cannot complete without it. Staging an RC without privacy is not recommended.
6. **Attribution-rule controversy.** If peers read §4 as narrowing to evade D6, CR-02 stays held. That is acceptable; it is not a failure.

## 9. Owner-only decisions (exact)

| ID | Decision | Concrete options |
| --- | --- | --- |
| **O-1** | The pending privacy reassessment budget (one extra Opus assessment plus one Astra judge) | (a) Approve, knowing the subject files carry Anthropic trailers (§4) and the coordinator must apply the D6 rule to that review. (b) Decline and keep privacy HELD. (c) Authorize enabling a third family (Gemini CLI OAuth, owner's own existing account, no spend) for a first privacy-review assessment instead. **My recommendation: (b) or (c).** (a) risks a second D6-type conflict. |
| **O-2** | Kiosk zoom suppression | Keep `user-scalable=no` on `/kiosk` as a deliberate wall-panel choice, or allow zoom. Main `/ui` zoom restore is recommended either way; only newly changed visuals would need capture approval. |
| **O-3** | Python 3.11 claim | Permit a digest-pinned `python:3.11-slim` image download for a disposable test run, or approve revising the claim to `>=3.12` through the root-manifest compatibility decision. |
| **O-4** | HA floor | Permit a digest-pinned `homeassistant/home-assistant:2025.1.0` download for a disposable container test, or approve raising the declared floor. |
| **O-5** | Dependency advisory | Permit public OSV/npm advisory queries (the dependency inventory leaves the host), or keep the audit "unavailable" with no conclusion. |
| **O-6** | Physical and field gates (CR-11/CR-13) | When a candidate exists: device access and window, disruptive-action scope, restoration, 72-hour and week windows. |
| **O-7** | Final version, `main` merge, tag and artifact release | Separate and later. |

No credentials or hardware are needed for any FC-1 package.

## 10. Prose check and limits

- **Docs check.** The five existing docs modules are run exactly once, after this report's final bytes, against my **historical checkout**. This is a **prose/documentation check only**, not product-baseline or source qualification. Its exact argv, cwd, environment, timing, exit, output, JUnit and the measured import origins (`rest_api`/`hub` resolve to this worktree's older `src/`) are recorded in the separate owned completion record, because a report cannot contain its own post-commit results.
- **Native visibility.** The model is self-reported as `claude-opus-5-5` and effort `high` comes from the scoped config. No helpers, subagents, MCP or plugins were used.
- **Negative findings.** I found no evidence that CR-01/02/03 need hardware or credentials. I found no evidence that the WS component is wired anywhere, and no reauth or `ConfigEntryAuthFailed` in the HA component. Nothing in this read reopens or contradicts any recorded historical failure.
