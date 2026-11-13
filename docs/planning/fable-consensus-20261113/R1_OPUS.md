verdict=blocking sha=f2a122f955def578960303bc15242fed00d01be3 scope=planning-only

# R1 (Opus): Fable remediation planning assessment

Not source acceptance, qualification, visual approval or landing approval. "blocking" means two material decisions below (CR-01 wiring disposition; settings-host contract) belong to the coordinator/hub/owner and must not be settled by an R1/R2 vote.

## Identity, inputs, limits

- Model `claude-opus-5-5` (harness system identity); **Anthropic family, same family as the author (Fable 5.2) and as the original CR-01 component author (Opus 5.5, `task_38756b76bd12`)**. I am not an independent-family reviewer of any of this source; family coverage from this seat is Anthropic only. Effort "high" is the dispatch/launch setting; I cannot measure it natively. No helpers, subagents or alternative routing used.
- Verified: HEAD `f2a122f9…`, tree `3384886f…`; `ROUND1_INPUTS.json` `43a42fd0…`, `ROUND1_PACKET.md` `1262b3c2…`, `FABLE_HANDOFF.md` `ffece03c…` (all match). Gemini review present at the host-local path (32,974 bytes) and read for H1–H5/M5/L2 scope only.
- My checks are static reading of the diff `680e93b8..f2a122f9` and contracts, plus one read-only fetch of HA `2025.1.0` `homeassistant/config_entries.py` (github.com/home-assistant/core tag source). No tests, builds, Docker, hooks or probes. All pass counts below are **author claims**.

## Q1 CR-01 / WebSocket — agree (retain as unaccepted candidate) + human decision

- Records: base `e54228c0` integrated the reviewed component only; HANDOFF.md:479/416 keep "no wiring grant", first-authorship `NOT_GRANTED`, WSR03. Fable wired it anyway (`websocket.py:31,106,142`, `app.py:269,630`). This is a **process conflict, human-only**: coordinator/hub decides (a) retain `3eb45919` as a candidate for fresh non-Anthropic exact-SHA review (my recommendation; the wiring matches the component's own proposed wiring text and is small), or (b) set the commit aside. No qualification is inferred either way.
- Technical: per-app `WsRequestWork` via `cleanup_ctx` plus explicit drain before stream stop is correct in shape; `open_owner()` never raises (`ws_request_work.py:396-403`), so the owner created outside `try` (`websocket.py:106`) cannot leak the client entry. Wired calls use default timeouts (1 s owner, 5 s shutdown), not configured ones; acceptable but undocumented.
- Coalescing (`OWNER_BUSY` silently answered by the in-flight read) — **agree**, but it is a **contract change** to `docs/api/WEBSOCKET.md`; requires explicit coordinator acceptance and API-registry note. Alternative (`error`) makes compliant clients retry into the same busy state. Stale-by-one-read is bounded because `refresh()` broadcasts found changes.
- Global cap: `_ws_clients` stays process-global (`utils.py:162`, `websocket.py:99`); H3 bullet 3 only partly addressed. **Defer** to a separate item; not required for bounding work.
- Acceptance check: the existing bounds test file plus a non-Anthropic reviewer re-running WSR01-style eager/reserved-admission negative controls against the wired path.

## Q2 Settings host and TLS — reject current pinning as final; unresolved contract

- Confirmed by code (not executed): `_connect_host` (`settings.py:74,162`) stores an IP; `_matrix_tls_policy` (`orei_matrix.py:129-139`) returns `create_default_context(cafile=…)` **or `True` when `OREI_VERIFY_SSL=true`**. Both verify the hostname, so a name entered in the UI fails TLS by IP unless the cert carries an IP SAN. The risk is wider than the handoff states (it covers verify-true, not only custom CA). Fingerprint mode and the default unverified mode are unaffected. Failure is closed (rollback, `applied:false`), not a security hole.
- Recommendation: keep and display the **name**; enforce the allowlist at every resolution through a validating aiohttp resolver on the connector (`orei_matrix.py:717`) and a resolve-validate-connect step in `telnet_client.py:258`. This preserves SNI/hostname verification and handles reconnects and address changes. Residual: in unverified mode a hostile DNS can still move to another *private* host; that already applies to the configured name Fable keeps unpinned. Alternative: pin the IP but pass `server_hostname` for verified modes (smaller, but keeps "save again on address change"). The choice of saved/displayed semantics is **owner/coordinator contract**.
- Backend password requirement (`settings.py:149-160`): **agree, keep**; the runtime-path `new_target` also covers the first target.
- `applied` field, scene 404 (three new sites, `scenes_v2.py:519,557,637`), GET default port 23→443 (`settings.py:98`): **agree technically**; all three are contract changes needing coordinator-owned registry/OpenAPI/ledger updates (`src/hub/openapi.py`, `docs/validation/features.yaml`). No Fable grant.

## Q3 HA — agree, floor partly resolved

- 2025.1.0 source has `async_update_reload_and_abort(entry, *, unique_id, title, data, data_updates, options, reason, reload_even_if_entry_is_unchanged=True)`; `data`+`data_updates` together raise, and the candidate uses `data`/`options` only (`config_flow.py:161`). `async_update_entry` fires listeners only on change, so the options flow (`config_flow.py:204`, then `async_create_entry` with identical options) should reload once. **Inferred, not executed**; the floor still needs a real `tests/ha` run on 2025.1.0.
- Reconfigure path: `async_update_reload_and_abort` schedules a reload and the update listener (`__init__.py:58`) also reloads, so it may reload twice (same pattern existed before). Low; add assertion.
- 404 on `/api/auth/status` treated as no locks (`config_flow.py:101`): **agree** (health already succeeded); document.

## Q4 UI / H1 password input — agree option (a), visual held

- `s` → General drawer **agree** (`index.html:705` loads it; the unified drawer is unloaded). Two visible text changes (help line, Power Cycle toast) are **unapproved**: before/after captures plus owner approval required before landing.
- H1: **agree (a)** password field in `#settings-modal` and General drawer, sent only on host/port change; never relax the backend, no baseline edits. Capture plan: both forms, empty/error/success, before/after, owner-only approval.

## Q5 H5 — defer

`remediation/privacy-c4` (`a8fdbaa3`, Sol-authored) is not in HEAD and shares **no files** with this candidate (`tools/validate/*` vs none here). Smallest action: the held privacy-c4 qualified review (non-OpenAI). No copy or cherry-pick. Note for that review: its diff includes `.codex/config.toml`, which looks unrelated.

## Q6 M5 / L2 — agree (a) via coordinator

`pyproject.toml:12,21` claim 3.11; `pyee==14.0.0` (`requirements.txt:641`) needs ≥3.12; CI runs 3.12/3.13 only; Dockerfile is 3.12. **Agree `>=3.12`** (honest, no re-lock). Paths `pyproject.toml`, `CONTRIBUTING.md:44`, `docs/agent-process/REPO_CONFIG.json:156` (handoff's `REPO_CONFIG.json` is at this path) need a coordinator lease. L2 (`ci.yml:450-455`): **defer** to the coordinator; the author claims both lints exit 0.

## Q7 Dispositions

| ID | Disposition |
| --- | --- |
| H1 backend/JSON/port | agree, author-claimed; contract items above |
| H1 rebinding | unresolved (Q2) |
| H1 UI lockout | defer, owner visual |
| H2 | agree; floor run outstanding |
| H3 | candidate; human decision (Q1) |
| H4 | agree; additional unlisted contract: `MAX_DEVICES` silently evicts the oldest remembered device (`security.py:295`); `_trim_failures` can evict locked keys past 4096 peers (low, LAN) |
| H4 `?key=` | refuted, preserve |
| H5 | defer |
| M1–M4, L1 | agree, author-claimed |
| M5 pyee | agree (a), coordinator |
| M5 Dockerfile | refuted (accept author reasoning; not re-verified) |
| L2 | defer, coordinator |
| L3, L4 | no action |

Combined validation gaps: per-commit isolation untested; `tests/ha` not at `f2a122f9`; `tests/uc`, Docker image tests (including `matrix-host` posts), browser, `tools.validate` and HIL not run; 6 skips unexamined. Meaningful negative controls: TLS by name with a name-only SAN cert under CA and verify-true; resolver refusing loopback/link-local on reconnect; WS flood of 1,000 frames leaving at most 8 reads and 0 tasks after close; HA invalid key returning `invalid_auth` with the control lock set.

## Proposed exact-file/test grants (no permission granted)

| Work | Owner | Writable paths | Tests |
| --- | --- | --- | --- |
| Settings resolver (after contract decision) | Fable | `src/rest_api/settings.py`, `src/orei_matrix.py`, `src/telnet_client.py`, `SECURITY.md` | `tests/test_settings_matrix_host.py`, `tests/test_security_ssrf_tls.py` (CA + verify-true by name, rebind on reconnect) |
| H1 UI (a) | Fable, visual held | `web/index.html`, `web/js/components/settings-panel.js`, `web/js/components/general-drawer.js` | `tests/test_ui_classic_api_and_shortcuts.py`; before/after captures |
| HA reload asserts | Fable | `tests/ha/test_config_flow.py` | run on HA 2025.1.0 and 2026.2.3 |
| CR-01 | none until decision | — | `tests/test_ws_get_status_bounds.py` (reviewer) |
| Contracts (`applied`, 404, port, WS coalescing) | coordinator | `src/hub/openapi.py`, `docs/validation/features.yaml`, ledger | registry/route checks |
| M5 (a) / L2 | coordinator | `pyproject.toml`, `CONTRIBUTING.md`, `docs/agent-process/REPO_CONFIG.json`, `.github/workflows/ci.yml` | `tests/test_packaging_version_sync.py` |
| H5 | none | — | privacy-c4 review |
