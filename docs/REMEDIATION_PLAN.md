# Remediation & Hardening Plan

> **Created:** 2026-09-24 · **Source:** full-project review of `main` @ `57b3401` (plus uncommitted `acquire_lock` fix)
> **Goal:** fix every review finding, make the core reliable, prove it with real validation (simulator + real hardware + real clients), and simplify the web UI while keeping its core concepts and visual aesthetic.
> **Status tracking:** tick the checkboxes in this file as work lands; every PR references the finding IDs it closes.

---

## 1. Principles

1. **Stabilize before extending.** No new features until Phase 3 exits. The backlog (MQTT, scheduling, IR, etc.) waits.
2. **Every fix ships with a test that fails before the fix.** Most of the current bugs survived because tests mocked the wrong shapes or skipped entirely.
3. **Contracts come from reality, not from mocks.** Device responses come from captures of the real BK-808; API shapes come from the real server; test fixtures are generated, not hand-written.
4. **Keep the concepts, cut the layers.** Presets, Profiles, Scenes, Macros, Shortcuts, Dashboard, Kiosk, CEC remote, and the Tron/glass look all stay. Duplicate paths, dead code, and parallel implementations go.
5. **Small, reviewable PRs.** One workstream per branch, PR per logical fix group, CI green before merge.
6. **Proof, not assumption.** Passing tests are not proof that something works. Every feature's status and every closed finding is backed by an evidence record showing the real effect, at the verification levels defined in [`docs/validation/VALIDATION_PLAN.md`](validation/VALIDATION_PLAN.md) (V0 claimed → V5 field-proven).

---

## 2. Decisions

### 2.1 Confirmed (2026-09-24)

| ID | Decision | Outcome | Affects |
| --- | --- | --- | --- |
| D1 | Release scope | **Free public release.** Users self-host in their own home or lab via **Docker**. Optimise for easy first run, safe defaults, and clear docs; no hosted/cloud component. | All phases; Phase 6-8 release work |
| D2 | Auth model | **Simple, optional PIN gate.** Users can protect admin functions with a PIN; kiosk/everyday control must work without any login. Invisible protections (CSRF/origin checks, no secret leakage) are always on. See Phase 3. | Phase 3 |
| D3 | Vendor binaries | **Remove from the repo and rewrite history.** Repo is public (0 forks, single `main` branch) — purge + force-push + ask GitHub Support to drop cached views. | Phase 6 (moved earlier: see note) |
| D4 | `src/integrations/` modular path | **Finish it.** Integrations are modular and **only enabled when the user sets them via Docker environment variables.** Core (matrix control, REST, web UI, kiosk) always runs. See Phase 4. | Phases 2, 4 |
| D5 | Overlapping features | **Fix everything that is incorrect** (Phase 2, no behaviour redesign). **Any consolidation or feature change is discussed first** — see §2.3 Discussion items. Nothing in §2.3 is implemented until agreed. | Phases 2, 4, 5 |
| D10 | Hardware validation | **Confirmed**: 3 HIL sessions (Phase 1, Phase 3 exit, Phase 8). | §5 |

### 2.2 Working defaults (not yet discussed; change any time)

| ID | Decision | Default | Affects |
| --- | --- | --- | --- |
| D6 | UI tech | Stay vanilla JS; move to native ES modules, no bundler, no framework. | Phase 5 |
| D7 | Kiosk | Thin separate page built on the shared modules. | Phase 5 |
| D8 | Minimum Home Assistant version | 2025.1 | Phase 2 |
| D9 | 4-port / multi-matrix | Out of scope; Phase 4 adds the port-count abstraction that makes it cheap later. | Phase 4 |
| D11 | Docker images | **One image** with all integration dependencies (ucapi is small); integrations toggled by env vars. The separate `api-only` target is retired. | Phases 2, 4 |

### 2.3 Discussion items (per D5) — **agreed 2026-09-24: all recommendations adopted**

These are places where features overlap or where fixing the bug properly changes behaviour. Phase 2 still fixes bugs *within current behaviour*; the agreed outcomes below are implemented in Phase 4/5. Any *new* overlap or behaviour change found during the work gets a new DI row and is discussed before implementation.

| ID | Topic | What overlaps / what's wrong | Agreed outcome |
| --- | --- | --- | --- |
| DI-1 | **Scene v1 routes** (`/api/scene*`) | Pure alias of Profiles, kept for compatibility; shares `scenes.json` filename with v2 Scenes. | Deprecate v1 routes (keep as aliases with a `Deprecation` header for one release), migrate any legacy file once. |
| DI-2 | **Profiles vs Scenes (v2)** | Profiles already carry `power_on`/`power_off` macros and a macro list; Scenes also sequence macros *and* profiles. Two ways to build "movie night". | Keep both, with sharp roles: **Profile = desired state** (routing + output settings + CEC config), **Scene = sequence** (profiles, macros, shortcuts, delays). Profile power-on/off macros **stay as a convenience** (no data migration); docs and UI steer multi-step sequences to Scenes. |
| DI-3 | **User Shortcuts vs Scenes** | User shortcuts have 5 action types, several of which are single-step scenes; system actions are also scene step types. | Shortcuts become "one-tap launchers" that point at *any* action (built-in system action, profile, scene, macro, preset) instead of defining their own action types. |
| DI-4 | **Custom preset save** | Saving a named preset temporarily re-routes live displays, then restores from possibly stale routing. Also overlaps with Profiles as "named routing". | Confirm on hardware whether the matrix can save a preset without switching live outputs. If not: either warn before saving or save the current live routing only. |
| DI-5 | **Three visibility systems** | Per-entity favorite/dashboard flags, the Dashboard layout file, and kiosk pins in browser localStorage. | Dashboard layout becomes the single store for main UI *and* kiosk (kiosk gets its own layout section); entity flags migrated then removed. |
| DI-6 | **PINs: per-item vs admin** | Profiles/Scenes have per-item PINs today; D2 adds an admin PIN. | Keep per-item PINs for "don't let the kids run this", admin PIN for configuration. Document the difference in the UI. |
| DI-7 | **Settings UI** | 9 settings drawers + a hidden legacy modal + `settings-panel.js`. | Single Settings drawer with sections (Phase 5), looks the same section by section. Review via the §5.3 capture process. |
| DI-8 | **Inputs / Outputs tabs** | Mostly status views that overlap with Matrix grid and dashboard cards. | Keep as-is for now; revisit after Phase 5 baseline review. |
| DI-9 | **Remote 3 design** *(direction set by the owner 2026-09-25)* | 74 entities, 24 redundant; routing mixed with TV CEC; non-standard command names; presets, profiles and kiosk content from the web app not reachable from the Remote. | **The Remote is another front end of the web app** (`docs/audits/UC_INTEGRATION_AUDIT.md` §4): presets (names, order, visibility) from the web app, a matrix remote whose pages mirror kiosk mode, per-output source select, CEC remotes matching the web app's CEC remote with standard names and button mapping, CEC macros, binary status sensors; configuration done in the web app; official UC patterns. Surviving entity IDs kept; the exact removal/rename list is approved before implementation. |
| DI-10 | **On-Remote deployment** *(recommendation accepted 2026-09-25)* | The UC integration could also run on the Remote 3 itself (aarch64 custom integration) talking to the hub over HTTP, avoiding Docker host networking. | Keep in-hub as the default; add the on-device build as an optional release artifact after Phase 4, once packaging limits are verified against official docs. |

---

## 3. Target end state

```
                  ┌──────────────────────── Hub container (one image, one entry point: run.py) ────────────────────────┐
                  │  CORE (always on)                                                                                  │
 Web UI / Kiosk ─▶│   rest_api/ + ws  ──▶  core.MatrixService ──▶ transport.http ───HTTPS──▶ BK-808                    │
 Home Assistant ─▶│   (PIN gate, CSRF)      • connection state machine      transport.telnet ─Telnet─▶                 │
                  │                         • status snapshot (TTL, single-flight) · NameStore · event bus             │
                  │   domain/ ActionRunner ◀── Presets · Profiles · Scenes · Macros · Shortcuts                        │
                  │   persistence/ (schema_version + migrations, real locking)                                         │
                  │ ─────────────────────────────────────────────────────────────────────────────────────────────────  │
                  │  INTEGRATIONS (opt-in via env vars, each implements the Integration interface)                     │
 Remote 3 ─ws:9095▶│   integrations/unfolded_circle   UC_ENABLED=true                                                  │
 Flic Hub ────────▶│   integrations/flic              FLIC_ENABLED=true   (button registry, discovery, endpoints)       │
 HA (discovery) ◀──│   integrations/homeassistant     HA_DISCOVERY_ENABLED=true (mDNS advert for HA config flow)       │
                  │   … future: mqtt, webhooks, scheduler — same interface                                             │
                  └────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- **One runtime, modular integrations (D4, D11).** `run.py` always starts the core; it then loads each integration whose env var is set. Disabled integrations are not imported, open no ports, and register no routes. `USE_MODULAR` and the legacy/modular split disappear.
- **Integration interface.** Each integration is a package under `src/hub/integrations/<name>/` exposing `config_from_env()`, `async start(hub: HubClient)`, `async stop()`, `health()`, and optional `routes()`. Integrations talk to the core only through `HubClient` (a narrow facade: status, commands, actions, events subscription). The existing `src/integrations/unfolded_circle/api_client.py` work is reused: `HubClient` has an in-process implementation (default) and an HTTP implementation, so an integration could later run in its own container without code changes.
- **One owner of device state.** `MatrixService` owns the connection, reconnect supervision, status snapshot, and names. REST, WebSocket, integrations, and the poller all read from it.
- **One execution path.** Profile recall, scene steps, shortcuts, Flic, and UC actions all go through `ActionRunner`, with uniform success/failure reporting.
- **One source of UI visibility.** Dashboard layout is the only place card visibility lives.
- **Model-aware ports.** `MatrixModel(inputs=8, outputs=8, capabilities=…)` replaces ~62 hard-coded `range(1, 9)` loops.
- **Web UI on ES modules** with a shared core (api, ws, state, escaping template helper, overlay stack) used by both `index.html` and `kiosk.html`.

---

## 4. Findings register

Severity: **C** critical · **H** high · **M** medium · **L** low. "Phase" is where it is fixed. `HIL` = needs hardware confirmation before/while fixing.

### 4.1 Backend core & UC driver (BE)

| ID | Sev | Finding | Location | Phase |
| --- | --- | --- | --- | --- |
| BE-01 | C | Supervisor restarts coroutines that *return* normally with no delay → event-loop spin; also makes polling unstoppable (poller swallows cancel) and `disconnect()`/`shutdown()` hang | `_task_supervisor.py:26-39`, `telnet_client.py:485,589`, `driver.py:1484` | 1 / WP-A1 ✅ fixed (PR #5): restart only after a crash, 1–30 s backoff, cancel propagates, `disconnect()` completes (strict xfail removed) |
| BE-02 | C | `await set_matrix_device(...)` on a sync function → every UC setup/reconfigure returns an error; macro CEC sender never wired | `driver.py:2015` | 1 / WP-B2 ✅ fixed: `set_matrix_device` is called synchronously, setup ends in STOP/OK and the macro CEC sender is wired (`tests/uc/test_setup.py::test_setup_reports_success`) |
| BE-03 | H | Output/input/cable status caches never expire (cache time written, never read) → sensors frozen | `orei_matrix.py:1023,1053,1139` | 1 / WP-A1 ✅ fixed (PR #5): all status caches expire (`OREI_STATUS_CACHE_TTL`, default 3 s), writes invalidate them |
| BE-04 | H | `connected` not cleared on timeouts/transport errors; no re-login on session expiry; reconnect never triggers | `orei_matrix.py:~366` | 1 / WP-A1 ✅ fixed (PR #5): explicit `ConnectionState`; transport errors leave CONNECTED; one re-login on session expiry; the matrix owns its reconnect (reboot and drop scenarios at V2) |
| BE-05 | H | Login treated as success when `comhead == "login"` (echoed even on bad password) | `orei_matrix.py:251` | 1 / WP-A1 ✅ fixed (PR #5): login requires `result == 1`; proven on the real BK-808: a wrong password answers `result: 0` (HIL session 1 probe) |
| BE-06 | H | Reconnect loop cancels itself via CONNECTED → `_stop_reconnection()`; Telnet never reconnected, polling not restarted | `driver.py:~1777` | 1 / WP-B2 ✅ fixed: the driver has no reconnect loop of its own any more; the matrix reconnects itself (BE-04) and the driver follows its CONNECTED/DISCONNECTED events, and the hub-owned poller never stops, so updates resume after a real link loss (`tests/uc/test_state_sync.py::test_live_updates_resume_after_a_transient_failure`, `::test_recovery_reports_connected_and_restores_the_last_known_state`; `tests/test_driver.py::TestConnectionEvents`) |
| BE-07 | H | Telnet completion logic contradicts itself (waits for E00/E01, then treats them as failure); set commands always wait full 5 s | `telnet_client.py:403-426,884,933` | 1 (HIL) / WP-A1 ✅ fixed (PR #5): set commands complete on their acknowledgement, E00/E01 are failures; Telnet semantics confirmed on the real BK-808 (HIL session 1: echo before answer, E00 unknown, E01 bad parameter) |
| BE-08 | M | `conn_state` unbound in poller when a sensor is not configured → poll aborts forever | `driver.py:1338` | 1 / WP-B2 ✅ fixed: the poller no longer depends on which entities are subscribed (`tests/uc/test_state_sync.py::test_a_partial_subscription_still_gets_updates`) |
| BE-09 | M | Standby/shutdown disconnect emits DISCONNECTED → reconnect loop restarts ~5 s into standby | `driver.py:~1829` | 1 / WP-B2 ✅ fixed: Remote standby no longer disconnects the matrix and the driver has no reconnect loop to restart (`tests/uc/test_lifecycle.py::test_remote_standby_keeps_the_matrix_connected`, `tests/test_driver.py::TestConnectionEvents::test_the_driver_has_no_reconnect_loop_of_its_own`) |
| BE-10 | M | Setup creates a new `OreiMatrix` without disposing the old one (session, socket, listeners leak; old events drive reconnect) | `driver.py:~1884` | 1 / WP-B2 ✅ fixed: setup probes the new address with a temporary client and disposes the old matrix (listeners, session, Telnet, reconnect task) only after a successful swap (`tests/uc/test_setup.py::test_reconfigure_to_another_matrix_disposes_the_old_connection`) |
| BE-11 | M | `_connect_telnet` replaces client without disconnecting the old one; concurrent `connect()` races; `_send_raw` error path leaves writer open | `orei_matrix.py:139`, `telnet_client.py` | 1 / WP-A1 ✅ fixed (PR #5): single-flight connect; the old Telnet client is disposed |
| BE-12 | M | Write methods report success on HTTP 200 regardless of `result`; `switch_input_to_all` returns True on failure | `orei_matrix.py:582-585,864,1791-1896` | 1 / WP-A1 ✅ fixed (PR #5): every write checks the matrix's `result` |
| BE-13 | M | `set_cec_enable` sends an unverified payload shape; two divergent enable implementations | `orei_matrix.py:1377,1915`, `driver.py:615,2035` | 1 (HIL) / WP-A4 part 2 ✅ fixed: `set_cec_enable` delegates to the array form (captured working; the single-port form is rejected, HIL-10) |
| BE-14 | M | Output-side CEC uses the input command table/indices; captures show a different output table | `cec_commands.py`, `orei_matrix.py` | 1 (HIL) / WP-A4 part 2: displays use the device web interface's 0-based output table (0 on, 1 off, 2 mute, 3 vol-, 4 vol+, 5 active); open until the live CEC run (`--include cec-live`). Remote: `remote.output_N_cec` offers exactly this table and `media_player.output_N` power/volume/mute send its indices (UC-23); web app: UI-37 |
| BE-15 | M | Audio-only detection uses scaler==4; docs and setter say 5 | `cec_commands.py:251`, `orei_matrix.py:2301` | 1 (HIL) / WP-A4 part 2: consistent now: detection reads device code 4 (captured), the setter maps API 5 to device 4 (`src/device_codes.py`); the write is proven with HIL-09 |
| BE-16 | M | Two name stores (driver vs REST); web renames never reach UC; failed name query rebuilds entities with generic names; stale `configured_entities` | `driver.py:~1536`, `rest_api/utils.py` | 4 |
| BE-17 | M | `_command_lock` held across reconnect + backoff → all HTTP callers stall 15-20 s during outages | `orei_matrix.py:~327` | 1 / WP-A1 ✅ fixed (PR #5): the command lock is never held across reconnect or backoff; `/api/health` answered in ≤ 16 ms during a simulated reboot |
| BE-18 | M | Lock file: non-atomic check; stale PID reuse; ImportError path deletes unconditionally (uncommitted fix is a stopgap) | `driver.py:acquire_lock` | 1 |
| BE-19 | M | `run_server.py` imports `src.rest_api.*` while modules import `rest_api.*` → duplicate module instances, uninitialised managers | `run_server.py:38-40`, `scenes_v2.py:58,73` | 4 / WP-D2 ✅ fixed: `run_server.py` is a thin deprecated alias of `run.py` (top-level imports only) |
| BE-20 | M | `src/integrations/unfolded_circle` unused parallel path (to be **finished** per D4); adapter maps `current_input` into `allconnect` | `src/integrations/`, `run.py:113-147` | 4 (D4) |
| BE-21 | L | `check_port_available` only handles Windows errno; port 9095 hard-coded; `driver.json` path depends on CWD | `driver.py:371` | 1 / WP-B2 ✅ fixed: EADDRINUSE on Linux/macOS/Windows, the port from `UC_INTEGRATION_HTTP_PORT` or `driver.json`, `driver.json` found next to the package (`tests/test_driver.py::TestStartupHelpers`) |
| BE-22 | L | Entity creation duplicated 3×, `cec_sender` closure 2× | `driver.py:516-590,1553-1598,1929-2002` | 4 |
| BE-23 | L | Dead code: unused `DriverState` fields, non-existent entity IDs in `on_matrix_connected`, `handle_exit_signal`, duplicate `get_ext_audio_status`, `route_input_to_all_outputs`, 38 per-command CEC wrappers, `_push_buffer`, unwired `on_status_update`, `Events.RECONNECTING`, `_reconnect_task`; `ConnectionError` shadows builtin; shallow-copy default CEC config | `driver.py`, `orei_matrix.py`, `telnet_client.py`, `config.py` | 4 |
| BE-24 | L | MediaPlayer state not updated by poller; first poll broadcasts `signal_change` for every active input | `driver.py` poller | 4 |
| BE-25 | L | `copy_edid_from_output` uses `set input edid` 14+N; docs describe `copy edid` | `orei_matrix.py` | 1 (HIL) / WP-A4 part 2: `copy edid` and `set input edid 14+N` get no answer (captured); copy is `set edid` 39+N (web-UI-derived, proven with HIL-09) |
| BE-26 | L | Hard-coded default host `192.168.0.100`; ~62 `range(1, 9)` / `[0]*8` | many | 4 |
| BE-27 | L | Runtime leftovers in `src/` (`driver.lock`, `config_state.json`, egg-info) | `src/` | 6 |
| BE-28 | C | Telnet push listener busy-loops at EOF (`read()` returns `b""`, loop `continue`s without yielding) → hub event loop frozen at 100% CPU after a matrix reboot or network drop (found by simulator, SIM-02) | `telnet_client.py:478-495` | 1 / WP-A1 ✅ fixed (PR #5): EOF is a lost connection (no spin); loop lag ≤ 16 ms during a simulated reboot |
| BE-29 | H | Telnet EOF never detected: `_send_raw` spins to timeout and `telnet_connected` stays true; truncated `status` dump makes every missing port read as disconnected (SIM-01) | `telnet_client.py:271-273,667-671,685-689` | 1 / WP-A1 ✅ fixed (PR #5): EOF detected, state → disconnected; missing ports read as unknown |
| BE-30 | L | `get_all_cable_status` sends `status!` twice per poll | `orei_matrix.py:1148-1150` | 1 / WP-A1 ✅ fixed (PR #5): one `status!` per cable poll |
| BE-31 | M | Background status refresh formats outputs from the hub name cache, which is empty in modular mode → WebSocket broadcast resets output names to "Output 1/2" in every open UI (symptom of BE-16) | `rest_api/outputs.py:59`, `rest_api/core.py:115` | 2 |
| BE-32 | L | `OREI_TELNET_PORT` is read from the process environment for every matrix, so one override (e.g. for the simulator) applies to every host; it should be per matrix config (found in WP-B2) | `orei_matrix.py:295` | 2 |

### 4.2 REST API, domain & persistence (API / PER)

| ID | Sev | Finding | Location | Phase |
| --- | --- | --- | --- | --- |
| API-01 | C | `matrix_device.switch()` does not exist → every scene profile step and route shortcuts fail | `scene_execution.py:161`, `system_shortcuts.py:697,702` | 2 |
| API-02 | C | `profile_manager._save()` does not exist → 500, steps skipped, no history | `scene_execution.py:455` | 2 |
| API-03 | H | Macro step execution calls `.get()` on a dataclass and expects `input:3` targets (macros use `input_1`) | `scene_execution.py:190-195` | 2 |
| API-04 | H | Scene overrides apply defaults instead of "leave unchanged" (disabling input override routes Input 1) | `scene_execution.py:111-127` | 2 |
| API-05 | H | `p.id` on dicts from `list_profiles()` → `POST/PUT /api/v2/scenes` 500 whenever profiles exist | `scenes_v2.py:126,193` | 2 |
| API-06 | H | `power_off_all` powers off the matrix 8× | `system_shortcuts.py:705-707` | 2 |
| API-07 | M | LCD timeout mode map in shortcuts contradicts device mapping ("Always on" sets 60 s) | `system_shortcuts.py:22-34` vs `orei_matrix.py:1972` | 2 (HIL) / WP-A4 part 2: shortcut map uses the device codes (0 off, 1 always, 2/3/4 = 15/30/60 s; read back as `get system status.mode`, 3 = 30 s captured); the old `{"time": N}` payload is rejected, the hub sends `{"lcd on time": N}` (proven with HIL-09). The shortcut label "LCD: 10s" (sets 15 s) needs a UI-approved rename |
| API-08 | M | Boolean results ignored; `execute_scene` returns 200/`success:true` on failure; profile recall 200 when all outputs fail | `system_shortcuts.py`, `scenes_v2.py:275`, `profiles.py` | 2 |
| API-09 | M | WS broadcast is sequential with no per-client timeout; handlers broadcast *before* sending the command → one stalled client hangs `/api/switch` | `websocket.py:481-489`, `control.py:41,102,133` | 2 |
| API-10 | M | WS heartbeat broken (client sends `{type:'ping'}`, server expects `{command}`; pong check logic drops clients) | `websocket.py:512`, `web/js/websocket.js:223` | 2 |
| API-11 | M | Every `/api/status` cache hit spawns an untracked, non-deduplicated refresh task (4 sequential matrix calls) | `core.py:225-236` | 1 / WP-A1 ✅ fixed (PR #5): single-flight refresh, one tracked background refresh |
| API-12 | M | v1 and v2 scenes share `scenes.json` with different schemas; profile "migration" can ingest v2 scenes | `scene_manager.py:28`, `config.py:221,486` | 4 |
| API-13 | M | `update_scene` mutates in memory before validating → corrupt in-memory state | `scene_manager.py:590-616` | 2 |
| API-14 | M | Custom preset save re-routes live TVs, restores from stale routing, no lock | `control.py:383-424` | 2 |
| API-15 | L | Input validation: body types, truthy-string booleans (`"false"` enables), unchecked output numbers/override keys, unbounded Flic registration | `outputs.py:367`, `config.py:667`, `integrations.py:67-84` | 3 |
| API-16 | L | `sys.path.insert` on every request (9 handlers) | `audio.py`, `outputs.py`, `cec.py` | 1 |
| API-17 | L | `config/*.json` seed files contain personal test data in legacy schema | `config/` | 6 |
| API-18 | L | `config.SceneManager` (v1) dead | `config.py`, `utils.py:388-395` | 4 |
| API-19 | M | Three divergent "apply profile" paths (recall handler, scene executor, shortcut executor) | `profiles.py`, `scene_execution.py`, `system_shortcuts.py` | 4 |
| API-20 | M | Dashboard layout claims to be source of truth, but 5 entity types carry their own favorite/dashboard flags; deletes orphan cards | `dashboard_layout.py`, managers | 4 |
| API-21 | L | Two response envelope implementations (sync `_json_response` vs async in `scenes_v2`) | `utils.py`, `scenes_v2.py` | 4 |
| API-22 | M | Profile outputs lack `scaler_mode`/`arc` fields that the executor reads via `getattr` | `config.py:127-130`, `scene_execution.py:126-175` | 4 |
| API-23 | H | `POST` scene CEC auto-resolve calls `resolve_scene_cec_config(profile)` but the resolver takes `(active_inputs, active_outputs, status)` and returns a dict (then `.to_dict()` is called on it) → endpoint always returns 500 (found by mypy in Phase 0) | `rest_api/scenes.py:~257`, `cec_resolver.py` | 2 |
| API-24 | L | `GET /api/info` reads `Path("driver.json")` relative to the working directory, so it silently falls back to defaults when the hub is started from another directory (the driver itself was fixed in WP-B2, BE-21) | `rest_api/core.py:245` | 2 |
| PER-01 | M | `_file_io` locks the unique temp file (no mutual exclusion); Windows `os.replace` fails under concurrent readers (the failing test); no directory fsync | `_file_io.py:196-205` | 1 |
| PER-02 | M | Flic button registry written non-atomically | `rest_api/integrations.py:50-56` | 1 |
| PER-03 | M | `migrate_legacy_file` deletes target on any read OSError → possible data loss | `persistence.py:184-196` | 1 |
| PER-04 | M | No `schema_version` / migration framework for persisted JSON | all managers | 4 |

### 4.3 Security (SEC)

| ID | Sev | Finding | Location | Phase |
| --- | --- | --- | --- | --- |
| SEC-01 | C | No authentication on any of 163 routes or `/ws`; bound to `0.0.0.0` (reboot, power, EDID, host change all open) | `app.py:512`, `driver.py:2220` | 3 |
| SEC-02 | C | CORS `*` + `request.json()` ignores Content-Type → cross-site "simple" POSTs from any LAN browser; no Host allow-list (DNS rebinding); no WS Origin check | `app.py:249-270` | 3 |
| SEC-03 | C | `POST /api/settings/matrix-host` repoints the bridge, which then sends matrix credentials to the new host (TLS verify off); SSRF filter bypassable (`localhost`, `127.1`, decimal IPs, DNS); port unvalidated | `settings.py:290,332-372`, `orei_matrix.py:224-242` | 3 |
| SEC-04 | H | `passcode_hash` returned by profile and scene GETs → 4-digit PIN cracked offline | `config.py:391`, `scene_manager.py:177` | 3 |
| SEC-05 | H | PIN can be removed/changed without the old PIN; DELETE unguarded; POST overwrite resets protection; no API to set a profile PIN; inheritance check never receives a profile map | `scene_manager.py:514-516,602-606,641`, `config.py:580-633`, `profiles.py:21` | 3 |
| SEC-06 | H | PBKDF2 (600k) runs on the event loop → wrong-PIN spam stalls the server | `profiles.py:286`, `scene_manager.py:711` | 3 |
| SEC-07 | H | `escapeHtml` does not escape quotes but is used in 22 attribute contexts | `web/js/utils/helpers.js:11-17`, `kiosk.html:1537` | 2 |
| SEC-08 | H | Unescaped user-controlled names and free-form icons rendered via `innerHTML` (main UI + kiosk) | `integrations-drawer.js`, `cec-macro-editor.js`, `settings-panel.js`, `routing-drawer.js`, `renderers.js`, `shortcuts-drawer.js`, `settings-drawer.js`, `kiosk.html` | 2 (patch) / 5 (structural) |
| SEC-09 | M | TLS verification off by default, no pinning option | `orei_matrix.py:224-227` | 3 |
| SEC-10 | M | Credentials silently default to Admin/admin; UC setup has no credential fields; raw login response logged at DEBUG; running `driver.py` directly forces DEBUG | `orei_matrix.py:247`, `driver.py:2126` | 3 |
| SEC-11 | L | ~90 handlers return `str(e)`; `/api/system/storage` and `/info` expose absolute paths and file listings | `rest_api/*` | 3 |
| SEC-12 | L | Rate limiter exempts any path ending in an image extension; WS unlimited/uncapped; XFF trusted without proxy allow-list | `utils.py:338-346` | 3 |
| SEC-13 | L | Static-file traversal guard is a substring `..` check | `static.py:41` | 3 |
| SEC-14 | H | Vendor firmware, `XP3.exe`, Control4/RTI drivers, and copyrighted manual committed (public) since the first commit; LICENSE is a stub | `docs/BK-808 */`, `LICENSE` | 0 (D3) |
| SEC-15 | L | gitleaks configured but never run; CI actions tag-pinned; base image not digest-pinned | `.github/`, `Dockerfile` | 6 |

### 4.4 Home Assistant component (HA)

| ID | Sev | Finding | Location | Phase |
| --- | --- | --- | --- | --- |
| HA-01 | C | `hass.helpers.aiohttp_client` (removed API) in 10 places → every write/service fails | `switch.py`, `select.py`, `button.py`, `__init__.py` | 2 / WP-D1 ✅ fixed: one hub client on `async_get_clientsession` (`api.py`); V3 in a real Home Assistant container (`ha.*` scenarios) |
| HA-02 | H | Expects `routing` as a list; API returns a dict → `current_option` always `None` | `select.py:51-63,89-90` | 2 / WP-D1 ✅ fixed: routing read as the `{"1": 2}` mapping from the contract fixture; V3 in a real Home Assistant container (`ha.*` scenarios) (`ha.select_source`) |
| HA-03 | H | Power switch reads `power` key that `/api/status` never returns | `switch.py:56`, `core.py:24-66` | 2 / WP-D1 ✅ fixed: `/api/status` now carries `power` (`on`/`off`, `rest_api/core.py`); the switch reads it and is unavailable without it; V3 (`ha.power_off`, `ha.power_on`) |
| HA-04 | M | No `translations/en.json` (custom integrations don't compile `strings.json`) | component root | 2 / WP-D1 ✅ fixed: `translations/en.json` = `strings.json` (tested), exception/selector translations, `icons.json` |
| HA-05 | M | `AbortFlow` swallowed by broad `except` in config flow | `config_flow.py:27-43` | 2 / WP-D1 ✅ fixed: only the probe is in `try`; abort/create outside it (`test_user_flow_already_configured`) |
| HA-06 | M | Services registered per entry (last entry wins), errors only logged, non-200 ignored | `__init__.py:32-91` | 2 / WP-D1 ✅ fixed: services in `async_setup`, `config_entry_id`/`device_id` targeting, `ServiceValidationError`/`HomeAssistantError`; V3 (`ha.service_*`) |
| HA-07 | M | Legacy `hass.data` storage instead of `entry.runtime_data` | all platforms | 2 / WP-D1 ✅ fixed: `entry.runtime_data` |
| HA-08 | M | Coordinator responses not released on early-raise/non-200 paths | `coordinator.py:45-58` | 2 / WP-D1 ✅ fixed: every request in `async with` (released on all paths; `tests/ha/test_api.py` checks the connector against a real server) |
| HA-09 | L | `UpdateFailed` re-wrapped without `from err`; redundant `_poll_lock` | `coordinator.py:99-100` | 2 / WP-D1 ✅ fixed: `raise UpdateFailed(...) from err`; lock removed |
| HA-10 | L | No `has_entity_name`/`translation_key`; `device_info` copy-pasted 7×; hard-coded `sw_version`; no `configuration_url` | all entities | 2 / WP-D1 ✅ fixed: `HdmiMatrixEntity` (has_entity_name, translation keys, one DeviceInfo with model/firmware from `/api/status/device`, MAC connection, `configuration_url`); V3 (`ha.config_flow`) |
| HA-11 | L | unique_id is the IP; port not range-validated; no reconfigure/options flow | `config_flow.py` | 2 / WP-D1 ✅ fixed: unique id = matrix MAC (address-keyed entries migrate at setup), port 1-65535, reconfigure + options flows; V3 (`ha.reconfigure`, `ha.config_flow`) |
| HA-12 | L | CEC command interpolated into URL unvalidated; schema doesn't enforce allowed values | `__init__.py:82` | 2 / WP-D1 ✅ fixed: `vol.In` of the hub's CEC tables + the display table for outputs; V3 (`ha.service_cec_invalid`) |
| HA-13 | L | `manifest.json` missing `integration_type` | manifest | 2 / WP-D1 ✅ fixed: `integration_type: hub` (no zeroconf: the hub does not advertise itself yet) |
| HA-14 | M | HACS validation fails: no `hacs.json`, no GitHub repository topics (owner action: add e.g. `home-assistant`, `hacs`, `hdmi-matrix`), no brand assets (icon/logo via the HA brands repo or bundled with the integration); licence check passes once the full LICENSE is on `main` | repo root, GitHub settings | 2 / WP-D1: `hacs.json` added (Home Assistant 2025.1, D8), topics are set, the HACS action passes every check except brands; ✅ fixed: brand icons (`custom_components/hdmi_matrix/brand/icon.png` 256 px, `icon@2x.png` 512 px) rendered from the web UI favicon (owner chose this 2026-09-26); HACS `ignore: brands` removed, so every HACS check is blocking (`tests/ha/test_init.py::test_brand_icons`) |
| HA-15 | L | Unused imports; `custom_components/` not linted in CI | component | 2 / WP-D1 ✅ fixed: unused imports gone; ruff already lints `custom_components/` in CI and the pre-commit hook |
| HA-16 | — | Needs optional API-key field once SEC-01 lands (only required when the hub has a control PIN) | component | 3 |

### 4.5 Deployment, packaging & CI (DEP)

| ID | Sev | Finding | Location | Phase |
| --- | --- | --- | --- | --- |
| DEP-01 | H | Every compose service has `profiles:` (`default` is not special) → `docker-compose up` starts nothing | `docker-compose.yml:36-38,80-81` | 2 / WP-D2 ✅ fixed: one service, no profiles; `tests/deploy/test_compose.py` |
| DEP-02 | H | Bridge networking, but UC mDNS discovery requires host networking (per DOCKER.md) | `docker-compose.yml` | 2 / WP-D2 ✅ fixed: `docker-compose.uc-host.yml` (host networking, mDNS on `HUB_HOST_IP`) and `docker-compose.uc-bridge.yml` (mDNS off, `UC_DRIVER_URL`); discovery by a real Remote is still HIL-E (F-OPS-004) |
| DEP-03 | C | API-only image runs legacy `driver.py` (imports `ucapi`), but `ucapi` is not installed → cannot start | `run.py:138-147`, `Dockerfile:42-60` | 2 / WP-D2 ✅ fixed: one image; `UC_ENABLED=false` runs the core without importing `ucapi` (`tests/deploy`, `tests/test_run_entry.py`) |
| DEP-04 | M | `setup.py` and `pyproject.toml` both present; both omit `_file_io`, `_task_supervisor`, `_telnet_proto` | root | 6 |
| DEP-05 | M | CI: no `pull_request` trigger; ruff only on `src/`; mypy non-blocking; no hassfest/HACS validation; no gitleaks; QEMU set up but no multi-arch platforms | `.github/workflows/docker-publish.yml` | 0 |
| DEP-06 | M | Five version numbers (0.1.0, 1.0.0, 2.10.0, README 2.7.0, HA sw 1.0.0); `driver_id` fallback mismatch | `driver.json`, `pyproject.toml`, `utils.py:86`, `manifest.json`, `core.py:170` | 6 |
| DEP-07 | M | Env-var surface inconsistent: `API_PORT` vs `REST_API_PORT`, `MATRIX_HOST` ignored in default mode, `WEBUI_ENABLED` no-op, `USE_MODULAR` | `run.py`, `driver.py:60` | 4 (WP-D2: `run.py` reads one set of names, old names are warned aliases, `USE_MODULAR`/`WEBUI_ENABLED` ignored; still open: with UC on, `driver.py` takes the matrix address from the Remote setup, not `MATRIX_HOST`) |
| DEP-08 | L | No lockfile/hashes for transitive deps; base image not digest-pinned; no dev requirements file | `requirements*.txt` | 6 |
| DEP-09 | L | `.dockerignore` misses `docs/`, `archive/`, `tests/`, agent/cache dirs | `.dockerignore` | 6 / WP-D2 ✅ fixed: allow-list (`src/`, `web/`, entry scripts, `driver.json`, requirements) |
| DEP-10 | L | `.gitignore` misses `.playwright-mcp/`, tool caches | `.gitignore` | 0 |
| DEP-11 | L | Pre-commit hook runs the full suite, silently skips `test_atomic_writes.py`, silently passes without ruff | `.githooks/pre-commit` | 0 |
| DEP-12 | L | One-off scripts (`_upgrade_log_calls.py`, ad-hoc telnet scripts) | `scripts/` | 6 |
| DEP-13 | L | `full_codebase_audit_prompt.md` at repo root | root | 6 |

### 4.6 Tests (TST)

| ID | Sev | Finding | Location | Phase |
| --- | --- | --- | --- | --- |
| TST-01 | H | HA tests skip (HA not installed) and mock `hass` as `MagicMock`, hiding HA-01…03 | `test_hacs_integration.py`, `test_ha_robustness.py` | 0 / 2 |
| TST-02 | H | Tests mock API shapes that the real API doesn't return (e.g. list `routing`) | HA tests, others | 0 |
| TST-03 | M | No tests: `/api/v2/scenes*`, `/api/integrations`, `/api/settings`, `_task_supervisor`, UC setup handler, poller, WS broadcast/state push, `api_client`/`entities` | `tests/` | 1-2 |
| TST-04 | M | No JS tests of any kind | `web/` | 0 / 5 |
| TST-05 | L | Hardware scripts collected as tests (fixture errors when `MATRIX_HOST` set); conftest defaults to a real IP | `test_manual.py`, `test_connection.py`, `test_all_formats.py`, `test_http_vs_https.py`, `test_all_features.py`, `test_input_names.py`, `conftest.py:43-44,68` | 0 |
| TST-06 | L | Module-global state (matrix device, managers, rate limiter) not reset between tests | `test_rest_api.py` | 0 |
| TST-07 | L | Lint config ignores F401/F811/E722; 10 ruff errors; 43 mypy errors | `pyproject.toml:80` | 0 / 1 |
| TST-08 | M | Atomic-write concurrency test fails on Windows (symptom of PER-01) | `test_atomic_writes.py:110` | 1 |

### 4.7 Web UI (UI)

| ID | Sev | Finding | Location | Phase |
| --- | --- | --- | --- | --- |
| UI-01 | H | `api.executeProfile()` doesn't exist; errors carry no `.status`; UI checks 401, server returns 403 → passcode flow unusable | `settings-drawer.js:339,342,372,436`, `dashboard-manager.js:915`, `api.js:121` | 2 |
| UI-02 | H | WS protocol drift: `active` vs `has_signal`; `*_failed`, `connection_change`, `cable_change`, `device_settings`, `scene_execution_error` unhandled; `cec_command` dropped; `optimistic` stripped; kiosk ignores `switch`/`switch_all`, listens for events never sent | `web/js/websocket.js`, `app.js:440-490`, `kiosk.html:2596` | 2 |
| UI-03 | M | No resync after WS reconnect; reconnect stops after 50 attempts (~23 min) | `app.js:149`, `websocket.js:18,190` | 2 |
| UI-04 | M | No fetch timeouts; `preset_recall` triggers refresh toasts on every client | `api.js:95,114`, `app.js:490,720,748` | 2 |
| UI-05 | M | New settings drawers drive a hidden legacy `#settings-modal` via synthetic `change` events | `hardware-drawer.js:145-178`, `general-drawer.js`, `interface-drawer.js`, `index.html:352-598` | 5 |
| UI-06 | M | Keyboard shortcuts broken (`scenes` tab id, `window.settingsPanel` never set) | `keyboard-shortcuts.js:34,42` | 5 |
| UI-07 | M | Accessibility: 27 independent Escape listeners; few `role="dialog"`/`aria-modal`; focus trap missing on 9+ overlays; kiosk has no ARIA and `div onclick` tiles; `user-scalable=no`; 22 px hover-only preset actions; one reduced-motion rule | many | 5 |
| UI-08 | M | Dashboard config in two stores (localStorage key still live after "migration"); kiosk pins localStorage-only | `app.js:74-78`, `dashboard-manager.js:71,1102,1126`, `kiosk.html:2164` | 5 |
| UI-09 | M | ~2,800 lines of dead JS: `quick-actions-drawer.js`, `floatable.js`, `presets-panel.js`, `system-shortcuts-panel.js`, `about-dialog.js`, `setup-wizard.js`, `empty-state.js`, `context-menu.js` (mostly), `settings-panel.js` + hidden modal | `web/js/` | 5 |
| UI-10 | L | 15-25% of ~12k CSS lines unused; `components.css` is 6.8k lines | `web/css/` | 5 |
| UI-11 | M | Kiosk is a parallel app (own API client, WS, theme, CEC remote, `escapeHtml`) | `kiosk.html:1464-2754` | 5 |
| UI-12 | M | Duplication: two trackpads in `cec-tray.js`, two render paths in `routing-drawer.js` | `cec-tray.js:280-388,1468-1580`, `routing-drawer.js:59-95,385-437` | 5 |
| UI-13 | L | No module system: ~50 ordered `<script>` tags, `window.*` globals | `index.html:660-715` | 5 |
| UI-14 | L | Three generations of settings UI; nine separate right-side drawers | `side-nav-drawer.js`, drawers | 5 |
| UI-15 | L | `overlay-manager` hard-codes drawer list including dead `quick-actions-drawer` | `overlay-manager.js:35-46` | 5 |
| UI-16 | L | `tron-background.js` redraws every frame with heavy `shadowBlur`; no reduced-motion check | `tron-background.js:978-1104` | 5 |
| UI-17 | L | `cec-tray` outside-click handler leaks | `cec-tray.js:1236-1244` | 2 |
| UI-18 | L | `api-copy.js` hard-codes `http://host:8080` | `api-copy.js:13` | 5 |
| UI-19 | L | `scene-editor` uses `prompt()` for step targets | `scene-editor.js:263-278` | 5 |
| UI-20 | L | `about-dialog`/`integrations-drawer` call `fetch` directly | — | 5 |
| UI-21 | L | PWA manifest marked done in plan, not present | `web/` | 5 |
| UI-22 | M | Device icon set is a bitmap trace of a PNG sprite of unknown origin/licence (`device_icons_set.png.svg`); `_icon-paths.json` is 2.9 MB and single icons reach 376 KB | `web/assets/icons/svg/`, `scripts/convert-icons-to-svg.js` | 5 / 6 |
| UI-23 | H | Kiosk "Apply" sends `{mute}`/`{enable}` but the hub reads `muted`/`enabled` (default true) → can mute/unmute outputs unintentionally; kiosk HDR/scaler/HDCP option values don't match the API | `kiosk.html` | 2 |
| UI-24 | H | Kiosk calls non-existent `/api/inputs/status` and `/api/outputs/status` (real: `/api/status/*`) → input tiles always grey, footer tiles always dimmed | `kiosk.html:2514` | 2 |
| UI-25 | M | Kiosk profile wizard never opens (reads the macros response shape wrong); routing wizard step 1 "Next" has no handler | `kiosk.html:2469` | 2 |
| UI-26 | H | Scene editor always fails "Scene name is required" (duplicate `id="scene-name"`) | `scene-editor.js:90` | 2 |
| UI-27 | M | Profiles tab never loads profiles; `state.profiles`/`state.cecMacros` never loaded; dashboard cards race the layout fetch (100 ms timer) and don't render on load | `app.js:591`, `dashboard-manager.js` | 2 |
| UI-28 | M | Runtime errors: CEC tray FAB TypeError (`.target-name` vs `.target-abbrev`); tooltip capture listener throws `closest is not a function` on first pointer; API button throws on first click | `cec-tray.js:1186`, `tooltip.js:25-35`, `api-copy.js:134` | 2 |
| UI-29 | M | No error state when the matrix is unreachable or status is pending: grid shows fabricated 1:1 routing and default names while the header stays green; "reconnecting" is visually identical to "disconnected" | `app.js`, `matrix-grid.js`, header | 2 (logic) / 5 (visual) |
| UI-30 | L | Scene-CEC modal never becomes visible; About dialog always shows WebSocket "Disconnected"; hardware drawer shows HTML defaults instead of device values; settings drawer `open('scenes'\|'system')` highlights the Profiles tab | `scene-cec-modal.js:204`, `about-dialog.js`, `hardware-drawer.js`, `settings-drawer.js` | 2 |
| UI-31 | M | Theme preset edit buttons are nested `<button>`s → clicking edit on preset 1 hits preset 4 | `theme-drawer.js:122-136` | 2 |
| UI-32 | M | Layering: confirm dialogs and toasts render under drawers/modals; scene editor opens under the settings drawer | CSS z-index | 5 |
| UI-33 | L | Phone (390 px): matrix grid view clips the last column; kiosk footer and edit bar clip | `responsive.css`, `kiosk.html` | 5 |
| UI-34 | L | Kiosk ignores the theme presets (always Tron Classic) | `kiosk.html` | 5 |
| UI-35 | M | axe: `aria-required-parent` on desktop tabs, unlabeled tab-pin checkboxes, `aria-hidden-focus` in closed drawers, unnamed tooltip, kiosk `color-contrast` ×22, zoom disabled | `index.html`, `kiosk.html` | 5 |
| UI-36 | L | Passcode prompt is a native `window.prompt()` (unstyled, can't be captured) | `settings-drawer.js`, `dashboard-manager.js` | 5 (with UI-01) |
| UI-37 | M | Since BE-14 the hub refuses navigation/playback CEC keys for displays (REST 400), but the web app's CEC dropdown renders the D-pad and Menu/Back for a display too (no per-target filtering found in the CEC tray or the kiosk remote either); `GET /api/cec/output/{n}/capabilities` lists the six supported keys. Needs a UI change through the UI review process | `cec-controls.js:renderDropdownContent`, `cec-tray.js`, `kiosk.html` | 2 |

### 4.8 Documentation (DOC)

| ID | Finding | Phase |
| --- | --- | --- |
| DOC-01 | `PROJECT_ROADMAP.md` frozen at 2026-01-22 (HACS "NEXT", entity count 58 vs 74, 283 tests, `rest_api.py`) | 7 |
| DOC-02 | README: wrong API-only instructions, env-var table (≈20 vars missing, 3 wrong), `orei_matrix` component path, test counts, API version, root-level paths, `s recall scene X!` table, legacy "Original Setup" half, duplicate future-features lists | 7 |
| DOC-03 | `API_REFERENCE.md` covers 62/163 routes; WebSocket undocumented; `/api/scene*` presented as a feature; `POST /api/input/{n}` documented in FLIC/HA docs but doesn't exist | 7 |
| DOC-04 | `HOME_ASSISTANT.md` calls the component "planned"; entity/service names don't exist | 7 |
| DOC-05 | `DOCKER.md` networking, container name, non-existent `docker-compose.multi.yml` | 7 |
| DOC-06 | `CEC_CONTROL_ARCHITECTURE.md` self-contradictory statuses, plural paths | 7 |
| DOC-07 | `PHASE_8_SPEC.md` diverges from implementation (routes, PBKDF2, shortcuts kept, system_actions files) | 7 |
| DOC-08 | `WEB_UI_IMPLEMENTATION_PLAN.md` stale file tree, PWA falsely ✅ | 7 |
| DOC-09 | `IR_CONTROL_ROADMAP.md` version plan collides with used versions | 7 |
| DOC-10 | `MASTER_INDEX.md` + `docs/README.md` overlap; external "Antigravity" references; four phase-numbering schemes | 7 |
| DOC-11 | `OREI_API_COMMANDS.md` claims 33/33 verified but body says unverified; no Telnet section | 7 (after HIL) |
| DOC-12 | Missing: CONFIGURATION, ARCHITECTURE, CHANGELOG, VALIDATION report, SECURITY | 7 |
| DOC-13 | `CONTRIBUTING.md` outdated (container name, install path, hooks, mypy) | 7 |

### 4.9 Unfolded Circle Remote integration (UC)

Full detail (location, user impact, fix) in [`docs/audits/UC_INTEGRATION_AUDIT.md`](audits/UC_INTEGRATION_AUDIT.md) §2.

| ID | Sev | Finding (short) | Phase |
| --- | --- | --- | --- |
| UC-01 | C | Any CEC remote command other than `send_cmd` (incl. `on`/`off`) raises `AttributeError` and drops the Remote's WebSocket | 1 (wave 2) / WP-B2 ✅ fixed: `on`/`off` send CEC power on/off (source table for inputs, display table for outputs), `toggle` uses the tracked power state (unknown → on), `send_cmd_sequence` is implemented, and every command handler turns an exception into 500 instead of a closed WebSocket (`tests/uc/test_commands.py::test_cec_remote_power_and_sequence_commands`, `::test_cec_remote_toggle_follows_the_tracked_power_state`, `::test_bad_parameters_answer_400_and_no_connection_closes`; scenarios `remote.output_cec_on`, `remote.input_cec_off`, `remote.output_cec_toggle`, `remote.input_cec_sequence`) |
| UC-02 | H | Port 9095 unauthenticated; `setup_driver` from anyone repoints the matrix host and sends the stored password to it | 2 / 3 (WP-B2 note: reconfigure now probes the new host first, and that probe also sends the stored credentials to it) |
| UC-03 | H | `driver_url: ""` → advertised `ws://<container-id>:9095` | 2 / WP-D2 ✅ fixed: key removed; optional `UC_DRIVER_URL` (`tests/uc/test_handshake.py`, `tests/deploy`) |
| UC-04 | H | Device state always CONNECTED; entities never UNAVAILABLE; poller pushes fabricated values during outages; `CLIENT_DISCONNECTED` unhandled | 1 (wave 2) / WP-B2 ✅ fixed: device state follows the matrix connection state (CONNECTED/CONNECTING/ERROR), every entity is UNAVAILABLE while the link is down and keeps its last known values, routing input 0 is unknown, sensors start UNKNOWN, `CLIENT_CONNECTED`/`CLIENT_DISCONNECTED` handled (`tests/uc/test_state_sync.py` outage, recovery and offline-start tests; `tests/uc/test_lifecycle.py::test_front_panel_change_reaches_web_clients_after_the_remote_goes_away`) |
| UC-05 | H | Reconfigure swaps device before probing, clears configured entities; abort/user-data unhandled; generic errors; setup payload logged; no credential step | 1 (wave 2) / 2 (wave 2 part done in WP-B2: the new address is probed with a temporary client and swapped in only on success, subscribed entities are never cleared, abort is logged (`tests/uc/test_setup.py` reconfigure tests); still open for Phase 2 / WP-B3: credential step, `AUTHORIZATION_ERROR` and specific errors, user-data handling, no setup-payload logging) |
| UC-06 | M | Standby keeps pushing; wake starts a second poller | 1 (wave 2) / WP-B2 ✅ fixed: standby only pauses the pushes to the Remote, wake sends what changed meanwhile, one hub-owned poller (`tests/uc/test_lifecycle.py::test_no_pushes_while_the_remote_is_in_standby`, `::test_wake_resyncs_with_exactly_one_poller`, `::test_repeated_connects_and_wakes_keep_one_poller`) |
| UC-07 | M | Every poll re-sends all attributes (~8.6k msgs/h) | 1 (wave 2) / WP-B2 ✅ fixed: only changed attributes are sent (`tests/uc/test_state_sync.py::test_unchanged_attributes_are_not_resent`, `tests/test_driver.py::TestEntityStateSync`) |
| UC-08 | M | Renames leave stale source lists in subscribed entities (select by new name fails) | 2 / 4 (WP-B2: a rename the driver sees, at the next Remote `connect` or at start-up, now replaces the subscribed entities in place and sends the new source list, so select by the new name works: `tests/uc/test_state_sync.py::test_select_source_by_new_name_after_rename`. Still open: a web-app rename does not reach the Remote live, `::test_input_rename_updates_the_source_list` strict xfail) |
| UC-09 | M | Matrix power switch never synced | 2 |
| UC-10 | M | Media player mixes routing and TV CEC; first toggle turns the TV off (still open: the strict xfail compared against the source table's power off, index 2; with the display table the first toggle sends display power off, index 1, which that assertion missed, so it XPASSed without a fix. The test now checks for display power off) | 4 (DI-9) (the first-toggle bug is fixed in WP-B2: display power is tracked per output and shared with `remote.output_N_cec`, and a toggle from UNKNOWN powers on; `tests/uc/test_commands.py::test_media_player_first_toggle_does_not_turn_the_tv_off`, scenario `remote.media_player_toggle`. The routing/CEC split stays with the DI-9 entity model) |
| UC-11 | M | mDNS publishes `0.0.0.0`, never unregisters (root of retry loop + duplicate events); env var names wrong in docs/plan | 2 / 4 (WP-D2: the image no longer sets `UC_INTEGRATION_INTERFACE=0.0.0.0`, the host-networking compose publishes `HUB_HOST_IP`, env names corrected in DOCKER.md; still open: unregister on shutdown, Phase 4) |
| UC-12 | L | Non-standard remote command names, no button mapping, text/emoji UI tiles | 4 (DI-9) |
| UC-13 | L | Text sensors instead of binary; duplicate sensors | 4 (DI-9) |
| UC-14 | M | Preset names hard-coded "Preset N"; web app preset names/favourites/visibility ignored | 2 |
| UC-15 | M | `ucapi` 0.5.1 vs 0.7.0; inconsistent pins | 2 |
| UC-16 | L | `driver.json` text/validation/`min_core_api`/release date | 2 / 6 |
| UC-17 | H | Hub liveness tied to the Remote: poller (only source of live WS events) runs only while a Remote is connected; standby disconnects the matrix | 1 (wave 2) / 4 (WP-B2 ✅ fixed: the poller starts with the hub and is never stopped by a Remote; standby keeps the matrix connected; `tests/uc/test_lifecycle.py` UC-17 tests. MatrixService ownership of polling remains Phase 4) |
| UC-18 | H | Modular path non-functional against the real API (envelope, allconnect, switch-all, next/previous, WS client); mocked tests hide it | 4 |
| UC-19 | L | Restore blocks startup before the WS server; config path ignores `ucapi`; CWD-relative `driver.json`; `__main__`-only `api` global | 1 (wave 2) / 4 (WP-B2 ✅ fixed: the WebSocket starts before the restore, which never waits for the matrix; the config file is in `api.config_dir_path` (legacy location still read); `driver.json` next to the package; `_driver_state.api` only, `main(driver_json=...)` entry point (a caller can pass adjusted metadata); without a saved setup `MATRIX_HOST` gives the hub its matrix before any Remote setup (never saved; a saved setup wins); REST port from `API_PORT` (`REST_API_PORT` fallback); `tests/uc/test_lifecycle.py::test_integration_port_opens_promptly_when_the_matrix_hangs`, `tests/test_driver.py::TestStartupHelpers`) |
| UC-20 | M | Vendored UC API docs several spec versions stale (official sources now pinned locally via `tools/uc_reference.py`) | 7 |
| UC-21 | H | No scripted-Remote test harness (✅ built in WP-B1: `tools/uc_remote_sim.py`, `tests/uc/`) | 1 (wave 2, first) |
| UC-22 | M | CEC remote `send_cmd` ignores `repeat`/`delay`/`hold`: holding a volume key sends a single CEC step (found by the WP-B1 harness) | 1 (wave 2, with UC-01) / WP-B2 ✅ fixed: `repeat`, `delay` and `hold` are honoured for `send_cmd` and `send_cmd_sequence` (bounded: repeat 20, 5 s) (`tests/uc/test_commands.py::test_send_cmd_repeat_sends_the_command_repeatedly`, `::test_send_cmd_sequence_repeat_and_the_button_mapping_form`; scenario `remote.output_cec_volume_repeat`) |
| UC-23 | M | After BE-14 (displays use the device's six-key output table), `remote.output_N_cec` still advertised 12 simple commands; 7 of them (UP, DOWN, LEFT, RIGHT, SELECT, MENU, BACK) have no display index, so the Remote showed keys that always failed (500) | 1 / WP-A4 part 2 ✅ fixed: the remote's simple commands are the display table (POWER_ON, POWER_OFF, MUTE, VOLUME_DOWN, VOLUME_UP, ACTIVE), its UI page shows only those, and other keys answer 400 without a frame (`tests/uc/test_commands.py`; golden entity set updated) |
| UC-24 | L | CEC remote entities advertise `SEND_CMD` and `ON_OFF` but not `TOGGLE`, so the Remote has no power-toggle for TVs and sources (found in WP-B2) | 4 (DI-9) |

### 4.10 Found by validation (VAL)

Findings from running features against the real hub and simulator (`docs/validation/VALIDATION_PLAN.md`). Each one is demonstrated by a failing scenario with committed evidence in `docs/validation/evidence/`.

| ID | Sev | Finding | Location | Proof (scenario) | Phase / WP |
| --- | --- | --- | --- | --- | --- |
| VAL-01 | H | Profile recall never applies audio mute, HDR or HDCP: it checks `hasattr(matrix_device, "set_audio_mute" / "set_hdr_mode" / "set_hdcp_mode")`, but the methods are named `set_output_*`, so the settings are silently skipped and recall still returns 200 | `rest_api/profiles.py:322-329` | `profiles.recall_output_settings` | 2 / WP-C1 |
| VAL-02 | M | Modular mode (`run.py`, the target architecture) never wires the macro CEC sender, so CEC macros, profile power macros and scene macro steps fail with "CEC sender not configured" while recall reports success | `run.py:88-106`, `rest_api/utils.py:461` | `profiles.recall_power_macro` | 2 / WP-C1 |
| VAL-03 | M | The CEC index table in `OREI_API_COMMANDS.md` contradicts the hub's `CEC_COMMAND_MAP` on 15 of 19 indices; one of them is wrong | `orei_matrix.py:717-759`, `docs/OREI_API_COMMANDS.md:329-351` | (hardware needed) | 1 / WP-H1, WP-A4 ✅ resolved: the hub's input table matches the device web interface's input pad; `OREI_API_COMMANDS.md` rewritten from it (and the separate output table, BE-14). Physical effect: live CEC run |
| VAL-04 | H | With the matrix unreachable, `/api/status` returns 200 with `connected: true` and made-up names "Input 1…8" | `rest_api/core.py:28` | `failures.unreachable_switch` | 2 / WP-C2 (with UI-29) |
| VAL-05 | M | `POST /api/output/{n}/source`, used by the matrix grid, never broadcasts a WebSocket event, so other open clients don't see the change | `rest_api/control.py:312-356` | `routing.grid_notifies_other_clients` (browser) | 2 / WP-C2 |
| VAL-06 | L | One `/ui` load makes 20–26 API calls against a limit of 60 per 10 s per client, so a third reload within 10 s fails with 429 errors | `rest_api/utils.py`, `web/js/app.js` | observed in the first browser run | 3 / WP-F1 (rate limiter), WP-E2 (fewer calls) |

### 4.11 Found on hardware (HIL)

From HIL sessions against the real BK-808 (MCU V1.10.01, web V2.00.03). Session reports: `docs/validation/*-hil-session-*.md`; captures: `tests/fixtures/device/`.

| ID | Sev | Finding | Location | Evidence | Phase / WP |
| --- | --- | --- | --- | --- | --- |
| HIL-01 | M | `get routing status` and `preset get` are not implemented by this firmware (no answer, timeout). `get_preset_info` falls back to them over HTTP when Telnet is unavailable, and `OREI_API_COMMANDS.md` documents them as working | `orei_matrix.py:~776-783`, `docs/OREI_API_COMMANDS.md` | `http/get_routing_status`, `http/preset_get_*` | 1 / WP-A4 ✅ fixed (no HTTP fallback, doc marks both unsupported, simulator never answers them) |
| HIL-02 | M | The device reports HDR mode **0**; the hub (`set_output_hdr` accepts 1–3), the UI and the simulator assume 1–3. The meaning of 0 is unknown | `orei_matrix.py:set_output_hdr`, `rest_api/outputs.py`, `tools/simulator/state.py` | `http/get_output_status` | 1 / WP-A4 part 2 ✅ resolved: 0 = pass-through (read, Telnet wording and the device web interface's list 0-2); API values 1-3 map to device 0-2 in `src/device_codes.py`, REST reads report API values |
| HIL-03 | M | Telnet differs from the assumptions the hub's parser and the simulator were built on: the banner starts with IAC negotiation, every command is echoed before its answer, and `status` is a 111-line dump headed "get the unit all status:". The hub's parsing must be proven against the real captures | `telnet_client.py`, `_telnet_proto.py`, `tools/simulator/telnet_commands.py` | `telnet/*` | 1 / WP-A4 (reads proven against the captures: `tests/test_telnet_real_captures.py`; set-command acknowledgements need the write capture) |
| HIL-04 | L | `get video status.allsource` has 9 entries (8 outputs + one more, likely the external audio output). The hub slices to 8, but the ninth value's meaning is undocumented | `rest_api/core.py:_format_status` | `http/get_video_status` | 1 / WP-A4 part 2 ✅ resolved: the ninth entry is the device web interface's "All Output" row (port 0): the common value, 255 when the outputs differ (matches all 7 captured arrays); the hub keeps outputs 1-8 |
| HIL-09 | C | ✅ Fixed and proven on hardware 2026-09-25 (WP-A4 part 2, `write` run with read-back). Every output/input setting command the hub sends is unknown to this firmware: `set output stream/hdcp/hdr/scaler/arc/mute`, `set input edid`, `copy edid`, `set output exa*` get **no answer** and change nothing; `set lcd on time` with `time` is rejected. The device's own web interface uses different commands and `[port, value]` payloads (`tx hdcp`, `tx stream`, `set output audio mute`, `set arc`, `set hdr conversion`, `set video scaler`, `set edid`, `"lcd on time"` …). Output settings, EDID, external audio and LCD have never worked on this hardware | `orei_matrix.py` output/input/ext-audio/LCD setters, `docs/OREI_API_COMMANDS.md`, simulator | `write/*`, session report part 2 | 1 / WP-A4 part 2 (critical): the hub sends the device web interface's commands (`tx stream`, `tx hdcp`, `set hdr conversion`, `set video scaler`, `set arc`, `set output audio mute`, `set edid`, `set lcd on time` with `"lcd on time"`, `set ext-audio *`, `ext-audio switch`, `reboot`); open until the capture tool's write run proves them on hardware (`tools/hil/README.md`) |
| HIL-10 | H | ✅ Fixed and proven on hardware 2026-09-25 (WP-A4 part 2, `write` run with read-back). The single-port `set cec index` payload is rejected (`result: 0`); only the 8-element array form works (confirms BE-13). CEC enable/disable via macros never works | `orei_matrix.py:set_cec_enable`, `driver.py` | `probe/cec_enable_shapes`, `write/http_cec_index_single` | 1 / WP-A4 part 2 ✅ fixed: only the array form is sent (`set_cec_enable` -> `set_cec_enabled`) |
| HIL-11 | M | ✅ Fixed and proven on hardware 2026-09-25 (WP-A4 part 2, `write` run with read-back). Telnet `s out N stream …` is an unknown command (`E00`) | `telnet_client.py` | `probe/telnet_noop_set_acks`, `write/telnet_system` | 1 / WP-A4 part 2 ✅ fixed: the hub never sent it; the simulator answers `E00` and the docs no longer list it |
| HIL-12 | H | Unknown or malformed HTTP commands get no answer at all, and the web server can stall briefly afterwards. With WP-A1's truthful connection state, one unsupported command times out and is treated as a lost connection (reconnect cascade). Unsupported commands must be removed (HIL-09) and "no answer to a command" distinguished from "device unreachable" | `orei_matrix.py:_post`/`_send_command` | `probe/http_unknown_comhead`, `probe/http_garbage_body` | 1 / WP-A4 part 2 ✅ fixed: a timeout / HTTP error / unparseable answer is a failed command ("device did not answer"); the link is only lost when a health read (`get system status`, one retry) fails too; tests in `tests/sim/test_sim_real_commands.py`; on the Remote: `tests/uc/test_state_sync.py::test_one_unanswered_status_read_keeps_the_remote_live`. To check with BE-06/UC-04: a host that silently drops packets (connect timeout, no reset) is now classified as "no answer", so by the code it is marked lost only after the command and both health reads time out (~15 s instead of 5 s) |
| HIL-13 | L | `cec command` accepts invalid indices and missing target ports (`result: 1`): the device doesn't validate, so the hub must | `orei_matrix.py:send_cec`, REST CEC handlers | `write/http_cec_command_invalid` | 2 / WP-A4 part 2 ✅ fixed: the hub validates the port (1-8) and the index against the input or output table before sending |
| HIL-14 | L | Reads answered without a login from the capture PC, and sessions stayed alive over 300 s idle; whether a login is needed at all is unconfirmed | `orei_matrix.py` login/session handling | `probe/http_no_session`, `probe/session_idle_expiry` | 1 / next HIL session |
| HIL-05 | M | Telnet answers that arrive line by line were cut short: `r preset N` completed on its first routing line (one output instead of 8), and the three lines `r fw version` sends after its first one were read as the next command's answer. Replayed against the real device's segments, the old client returned `{}` for preset 1 after a firmware read and the echo `r preset 1!` as the device type; `get_device_type` also returned the echo | `_telnet_proto.py:is_response_complete`, `telnet_client.py:_send_raw`, `get_device_type` | `telnet/r_preset_1`, `telnet/r_fw_version`; `tests/test_telnet_real_captures.py` | 1 / WP-A4 ✅ fixed |
| HIL-06 | M | `POST /api/scene/save-current` took the routing from `get output status.allsource`, which the device does not send, so every saved output was "input 1"; the device's 9-entry arrays also added an output 9 | `rest_api/scenes.py:handle_save_current_as_scene` | `http/get_output_status`; `tests/sim/test_golden_hub.py` | 2 / WP-A4 ✅ fixed |
| HIL-07 | M | `--redact` in the capture tool matched case-sensitively. The Telnet `status` dump prints the MAC in lower case, so HIL Session 1's committed `telnet/status.json` still contains the matrix's MAC address | `tools/hil/capture/context.py:Capture.secrets` | `telnet/status.json` | 1 / WP-A4 (tool fixed; the committed fixture needs an owner decision: re-capture or rewrite before merge) |
| HIL-08 | L | `get_all_input_names` cut every input name at its first `-`, assuming an `IN01-` prefix the device does not send (so "Sega-CD" became "CD") | `orei_matrix.py:get_all_input_names` | `http/get_video_status` (plain names) | 1 / WP-A4 ✅ fixed |

---

## 5. Validation strategy ("full real validation")

Validation is layered so that fast checks catch most regressions in CI and the real hardware/clients prove the rest. Each layer has explicit exit criteria.

| Level | What | Runs | Exit criteria |
| --- | --- | --- | --- |
| **L0 Static** | ruff (src, tests, custom_components, tools), mypy (blocking, baseline then ratchet), ESLint for `web/`, gitleaks, hassfest + HACS action | CI on every PR | Zero errors; no ignores without a comment |
| **L1 Unit** | pytest unit tests; fixture resets module globals; no network | CI | ≥ 85% line coverage on `core/`, `domain/`, `persistence/`; every register ID with a code fix has a named regression test |
| **L2 Device contract** | **Matrix simulator** (HTTPS `/cgi-bin/instr` + Telnet server) seeded with golden responses captured from the real BK-808 | CI | Every command the code sends is recognised by the simulator; simulator responses byte-match golden captures |
| **L3 API integration** | Full REST + WS suite against the simulator; **route-inventory test** fails if any registered route lacks a test; WS event contract test (schema shared with the web client) | CI | 163/163 routes covered (or explicitly deprecated); all WS events schema-validated both directions |
| **L4 Client integration** | HA via `pytest-homeassistant-custom-component` (real `hass` fixture); UC integration via a scripted Remote-3 WS client (setup, reconfigure, subscribe, commands, standby/wake); Web UI + kiosk E2E with Playwright against the simulator; **UI capture & review** per §5.3 | CI | All flows pass; every visual diff approved per §5.3 |
| **L5 Deployment smoke** | Build the image; start it with integrations off / UC only / all on; hit `/api/health`; confirm 9095 open only when UC enabled and disabled integrations register no routes; multi-arch build | CI | Healthy in < 30 s in every combination |
| **L6 Hardware-in-the-loop** | Real BK-808 + real sources/sinks + real Remote 3 + real HA + Flic + kiosk device | Manual sessions + scripted `tools/hil/` | See §5.2; results recorded in `docs/validation/` |

### 5.1 Matrix simulator (new, `tools/simulator/`)

- aiohttp HTTPS server implementing every `comhead` in `OREI_API_COMMANDS.md` against an in-memory device state (routing, names, presets, EDID, HDCP/HDR/scaler, ARC, mute, ext-audio, CEC enable, LCD, power).
- asyncio Telnet server implementing the CEC and routing command set, including push notifications as observed on hardware.
- Fault injection API: latency, dropped connections, HTTP 5xx, bad JSON, wrong password, session expiry, Telnet close mid-command, device reboot.
- Golden responses stored under `tests/fixtures/device/<firmware>/` and loaded by the simulator; version 1 is built from the docs, then replaced by HIL captures.
- Used by pytest, Playwright, Docker smoke tests, and local UI development (`python -m tools.simulator`). Replaces `archive/mock-server.js`.

### 5.2 Hardware-in-the-loop sessions

Record for each session: date, BK-808 MCU + IP-module firmware versions, hub commit SHA, host OS, results table. Store in `docs/validation/YYYY-MM-DD-<session>.md`.

#### HIL-A — Protocol conformance & capture (Session 1, during Phase 1)

- [ ] Script `tools/hil/capture.py` sends every read command and stores raw responses as golden fixtures.
- [ ] For every write command: send, read back, assert state changed, restore. Record the actual `result` codes for success and failure.
- [ ] Resolve open protocol questions: CEC enable payload (BE-13), output CEC command table/indices (BE-14), scaler code for audio-only (BE-15), EDID copy command (BE-25), LCD timeout codes (API-07), Telnet E00/E01 semantics and response terminators (BE-07), push notifications emitted on front-panel changes.
- [ ] Login with a wrong password → record the exact response (BE-05).
- [ ] Session expiry: leave idle past cookie lifetime → record behaviour (BE-04).

#### HIL-B — Functional (Sessions 2 & 3)

- [ ] Routing: every input → every output via REST, UC, HA, web UI, kiosk; verify on the physical display.
- [ ] Presets 1-8 recall/save/rename; custom preset save does not disturb live displays (API-14).
- [ ] Profiles, Scenes (all step types, overrides, PIN), Macros (power on/off sequences on real TV/Apple TV/Shield/PS5), Shortcuts (all 25 built-ins).
- [ ] CEC to every CEC-capable input device and the TV on output 1 (power, nav, playback, volume, mute); record per-device support matrix.
- [ ] Output settings: HDCP, HDR, scaler, ARC, stream enable, audio mute, ext-audio routing — each verified physically (picture/audio).
- [ ] Physical-change detection: front-panel routing change, TV HDMI unplug, source power-off → UC sensors, HA entities, web UI, and kiosk update within one poll interval.

#### HIL-C — Fault injection

- [ ] Unplug matrix Ethernet for 30 s and 5 min → state goes DISCONNECTED within one poll, entities unavailable, automatic recovery within 15 s of link restore, no duplicate tasks.
- [ ] Power-cycle the matrix; reboot it via API; restart the hub during a matrix outage.
- [ ] Kill Telnet only (block port 23) → hub reports DEGRADED, HTTP control keeps working.
- [ ] Throughout: event-loop lag watchdog stays < 100 ms; no unhandled exceptions.

#### HIL-D — Soak (Phase 8)

- [ ] 72 h run with polling + scripted random commands every 60 s + one scheduled outage per 12 h.
- [ ] Track RSS, asyncio task count, open sockets/fds, loop lag, error count via `/api/health` — all flat (no growth trend).

#### HIL-E — Real clients (Phase 8)

- [ ] Remote 3: the 14-point checklist in `docs/audits/UC_INTEGRATION_AUDIT.md` §9 (install/discovery, setup and reconfigure, every CEC remote command incl. power and sequences, physical keys, source selection and renames, live changes, outages, matrix reboot, sleep/wake, restart with matrix off, presets/profiles/scenes, power switch, battery drain, activity migration).
- [ ] Home Assistant (≥ D8): install via HACS custom repository, config flow, every entity type, all services, options/reconfigure, reload, remove.
- [ ] Flic: single/double/hold, Duo, Twist rotation (if hardware available — otherwise mark "not validated" in the report).
- [ ] Web UI on desktop Chrome/Firefox/Safari, iPad, phone; kiosk on the actual kiosk device for 24 h.
- [ ] Docker on the real deployment host with each integration combination (none, UC only, all); arm64 if the host is ARM.

### 5.3 UI change capture & review (look-and-feel governance)

Goal: every change to how the UI looks is **captured automatically, shown side-by-side, and explicitly approved** — nothing visual changes by accident, and "correct" is defined in writing, not from memory.

#### 1. Define "correct" — `docs/ui/LOOK_AND_FEEL.md` (Phase 0, from the current UI)

- Palette and token reference (backgrounds, text, borders, accent + secondary HSL system, status colours, glass/opacity, glow).
- The four theme presets (Tron Classic, Neon, Royal, Vaporwave) with swatches.
- Typography scale, spacing scale, radii, shadows/glow recipes, motion durations/easings.
- Component anatomy: header + status border line, tab bar, Control Deck, drawers, matrix grid tiles, dashboard cards, CEC remote, toasts, dialogs, kiosk tiles/tabs/footer.
- Do / don't examples taken from baseline screenshots.
- This document is reviewed with you and signed off before Phase 5 starts; changing it is itself a reviewed change.

#### 2. Capture — a UI state catalog + deterministic screenshots

- `tests/e2e/visual/catalog` enumerates every reviewable UI element and state as a named entry, e.g. `matrix/grid/default`, `matrix/grid/disconnected`, `drawer/settings/hardware`, `editor/scene/validation-error`, `cec-remote/output-1`, `kiosk/routing/edit-mode`, `dialog/passcode`. The catalog *is* the checklist of UI elements; a new component or state is not done until it has an entry.
- States covered per element where applicable: default, empty, loading, populated (8 named inputs/outputs), long names, error, disconnected/reconnecting, passcode prompt, hover/focus (desktop), pressed (touch).
- Deterministic rendering: simulator with seeded state, frozen clock, fixed random seed, web fonts awaited, animations/transitions disabled, Tron background off (plus one dedicated paused-frame snapshot with it on).
- Matrix, kept to a reviewable size (~300 images):
  - Default theme (Tron Classic) × every catalog entry × 4 viewports (desktop 1440×900, tablet 1024×768 landscape, phone 390×844, kiosk device resolution).
  - Other three presets × ~10 key screens × 2 viewports (desktop, kiosk).
- Baselines are generated **only inside the pinned Playwright Linux container** (locally via `npm run visual:update` which runs in Docker; and in CI) so font rendering never differs between Windows and CI. Stored under `tests/e2e/visual/__snapshots__/` via **Git LFS**.
- A dev-only **UI gallery page** (`/ui/gallery`, served only when `DEV_GALLERY=true`) renders every component in every catalog state from fixture data, plus live token swatches — for reviewing components in isolation and for design work.

#### 3. Review — every PR that changes any snapshot

- CI runs the visual suite on every PR. Any snapshot diff above threshold fails the check and uploads the Playwright report (baseline / actual / diff with slider) as an artifact.
- A bot comment on the PR lists every changed catalog entry with before/after thumbnails and a link to the full report.
- Style lint (Stylelint) blocks raw colours, spacing, and durations outside `tokens.css`, so the look can't drift through one-off values that don't show up in covered states.
- Automated a11y (axe) and contrast checks run on every catalog entry for all four presets.

#### 4. Approve — explicit, reviewed, recorded

- Intended changes are approved by running `npm run visual:approve` (in the container) and committing the updated baselines in a separate commit titled `visual: approve <catalog entries> — <reason>`.
- `CODEOWNERS` makes you the required reviewer for `tests/e2e/visual/__snapshots__/`, `web/css/tokens.css`, and `docs/ui/LOOK_AND_FEEL.md`.
- For AI-assisted UI work: before and after every UI change, the session captures the affected catalog entries and presents a before/after review page for sign-off *before* the PR is opened.

#### 5. Real-device check at milestones

- At v0.2.0, v0.3.0, end of Phase 5, and v1.0.0: capture the key screens on the real kiosk device, an iPad, and a phone; attach them to the validation report alongside the CI baselines to confirm the emulated viewports match reality.

---

## 6. Phased plan

Estimates assume one developer working with AI assistance; they are sizing, not commitments.

### Phase 0 — Foundations & safety net (4-5 days)

Goal: make it impossible for the bugs below to come back silently.

- [x] Commit the pending `acquire_lock` fix as-is (stopgap; proper fix in Phase 1).
- [x] **History purge first (SEC-14, D3)** — done now, while `main` is the only branch and there are no forks, so no rebasing is ever needed:
  - [x] Full mirror backup of the repo kept offline (not pushed anywhere).
  - [x] `git filter-repo` removing `docs/BK-808 Firmware/`, `docs/BK-808 RTI Driver/`, `docs/BK-808 Control4 Driver/`, `docs/BK-808 Control4 Driver.c4z`, `docs/BK-808_User_Manual.pdf`.
  - [x] Replace with `docs/vendor/README.md`: links to vendor downloads, file names, versions, SHA-256 checksums, and a short summary of protocol facts we derived (our own words, no copied content).
  - [x] Verify with `git rev-list --objects --all` that no purged blob remains; force-push `main` (done 2026-09-25, `469c013`). Commit emails also rewritten to the GitHub no-reply address (required by the account's email-privacy push protection).
  - [ ] *(owner)* Ask GitHub Support to purge cached views/refs of the removed blobs (the repo has been public since 2026-02-02) — draft provided; to be sent by the repo owner.
  - [x] Commit full MPL-2.0 `LICENSE` text (official Mozilla text; copyright line moves to the README licence section in Phase 7).
- [x] Branch strategy: `fix/phase-N-<topic>`; PR template listing register IDs + test evidence + (for UI) the §5.3 review link.
- [x] CI (DEP-05): add `pull_request` trigger; lint `src tests custom_components tools`; mypy blocking against a baseline file; gitleaks; hassfest + HACS validation; separate HA test job with `pytest-homeassistant-custom-component`; Docker build of both targets. *(done: `ci.yml`; mypy fixed to zero instead of a baseline; hassfest/HACS non-blocking until Phase 2)*
- [x] Remove `F401/F811/E722` ignores; fix the 10 ruff errors; record mypy baseline (TST-07).
- [x] Move hardware scripts to `tools/hil/`; conftest defaults to mock; add `hardware` pytest marker, deselected by default (TST-05).
- [x] Autouse fixture resetting REST module globals and rate limiter (TST-06).
- [x] **Contract fixtures:** generate API response fixtures from the real `_format_status` etc., and make HA/web tests consume them (TST-02). *(HA tests consume them; web tests will in Phase 0 UI capture)*
- [x] Route-inventory test (initially reports coverage; becomes blocking at Phase 2 exit). *(baseline 107/163)*
- [x] Minimal JS tooling: `package.json` (dev-only) with ESLint, Stylelint, Playwright, axe; one smoke E2E that loads `/ui` and `/kiosk` against the simulator (TST-04). *(lint findings baselined: ESLint 19, Stylelint 539; new violations fail)*
- [x] **UI capture baseline (§5.3)** — *before any UI code changes, including Phase 2 fixes*:
  - [x] Write `docs/ui/LOOK_AND_FEEL.md` from the current UI; review and sign off together.
  - [x] Build the UI state catalog covering every current page, tab, drawer, modal, editor, CEC remote, dashboard card type, and kiosk panel. *(170 entries, 763 snapshots; the component-isolation gallery page `/ui/gallery` moves to Phase 5 with ES modules — Phase 0 uses a screenshot gallery)*
  - [x] Capture baselines in the pinned Playwright container; Git LFS for snapshots; CODEOWNERS; PR bot comment with before/after thumbnails.
  - [x] Publish the baseline as a browsable gallery for a one-time walkthrough, so we both agree it represents the look to preserve (and note anything that is currently *wrong* and should change).
- [x] Simulator v1 from docs (§5.1) — enough for status, routing, presets, login. *(done beyond v1 scope: all comheads, Telnet, fault API, `tools/dev_stack.py`)*
- [x] Pre-commit hook: fast unit tests + ruff; fail loudly if tools are missing (DEP-11). `.gitignore` additions (DEP-10).
- [x] Add `/api/health` detail: connection state, last successful poll, loop lag, task count, version (needed by HIL-C/D).

**Exit:** history purged and verified; CI runs on PRs and is green; HA tests actually execute (and fail on HA-01…03, proving they now catch them); look-and-feel doc signed off and UI baselines committed.

### Phase 1 — Core reliability (4-6 days, includes HIL Session 1)

Goal: the hub stays connected, reports truthfully, and never freezes.

- [ ] **Telnet EOF handling** (BE-28, BE-29, BE-30): treat `b""` as disconnect (transition state, stop listener, trigger reconnect); parse `status` dumps defensively (missing port = unknown, not disconnected); one `status!` per poll. Simulator reboot/drop tests un-xfailed.
- [ ] **Supervisor** (BE-01): restart only on exception with backoff; normal return ends supervision; always re-raise `CancelledError`; remove `except CancelledError: break` in loops. Tests: returning coroutine not restarted; cancel stops it; crash restarts after delay; `disconnect()` completes within 1 s.
- [x] **UC setup** (BE-02): drop the stray `await`; test the full `handle_driver_setup` flow. (WP-B2)
- [ ] **Connection state machine** (BE-04, BE-05, BE-06, BE-09, BE-17): explicit states `DISCONNECTED → CONNECTING → CONNECTED ↔ DEGRADED (telnet down) → BACKOFF`; one reconnect supervisor owned by the matrix object; transport errors transition state; one re-login attempt on auth failure; login success = explicit `result` check (per HIL-A capture); intentional disconnect (standby/shutdown) does not trigger reconnect; command lock not held during backoff. Tests use simulator fault injection.
- [ ] **Resource lifecycle** (BE-10, BE-11): dispose old matrix/telnet before replacing; single-flight `connect()`; close writers on error.
- [ ] **Status snapshot** (BE-03, API-11): TTL on all caches; single-flight refresh (one in-flight request, others await it); poller is the only background refresher; writes invalidate + apply optimistic state.
- [ ] **Truthful writes** (BE-12): every write checks `result`; returns a typed `CommandResult(ok, code, detail)`.
- [ ] **Telnet protocol** (BE-07): rewrite completion detection from HIL-A captures; set commands complete on acknowledgement, not timeout.
- [ ] **Protocol corrections from HIL-A** (BE-13, BE-14, BE-15, BE-25, API-07): single CEC-enable implementation; correct output CEC table; correct audio-only scaler code; correct EDID copy; correct LCD map — each with a golden-fixture test.
- [ ] **Poller** (BE-08): fix unbound variable; per-output error isolation.
- [ ] **Lock file** (BE-18): replace PID file with an OS advisory lock held for process lifetime (`fcntl.flock` / `msvcrt.locking`).
- [ ] **Persistence** (PER-01…03, TST-08): per-file in-process `asyncio.Lock` + cross-process lock on a stable `.lock` sidecar; Windows-safe replace with retry; directory fsync on POSIX; atomic Flic writes; never delete on read error.
- [ ] Misc: Linux EADDRINUSE handling and configurable UC port (BE-21); remove per-request `sys.path.insert` (API-16).
- [ ] Update simulator with HIL-A golden captures.
- [ ] **Wave 2: Remote integration fixes in `driver.py`** (after wave 1 merges; per `docs/audits/UC_INTEGRATION_AUDIT.md`):
  - [ ] Scripted-Remote test harness `tools/uc_remote_sim.py` + `tests/uc/`, blocking CI job (UC-21) — built first, pinning current behaviour.
  - [x] Command handling: `on`/`off`/`toggle`/`send_cmd_sequence` on CEC remotes; every handler wrapped (UC-01, UC-22). (WP-B2)
  - [x] Device state + availability from the matrix state machine; no fabricated values; `CLIENT_DISCONNECTED` (UC-04). (WP-B2)
  - [x] Hub-owned poller started at hub startup, independent of any Remote; UC standby only pauses UC pushes; single poller (UC-17, UC-06, BE-08, BE-09; BE-06: no driver reconnect loop). (WP-B2)
  - [x] Push only changed attributes (UC-07). (WP-B2)
  - [x] Setup: BE-02; probe the new host before swapping; update entities in place instead of clearing (UC-05 part, BE-10). (WP-B2)
  - [x] Restore after the WS server is up; `api.config_dir_path`; package-relative `driver.json`; `_driver_state.api` (UC-19, BE-21). (WP-B2)

**Exit:** all BE/PER items in scope closed with tests; simulator fault-injection suite green; event-loop lag < 100 ms under injected faults; HIL-A report committed.

### Phase 2 — Broken features & client fixes (3-4 days)

Goal: every advertised feature actually works end to end.

- [ ] **Scenes & shortcuts** (API-01…08, API-13, API-14, API-23): `switch_input`; `save()`; macro steps via `MacroManager` with the real target format; overrides mean "leave unchanged"; `list_profiles` usage; `power_off_all` once; LCD map; honest status codes (`207`/`500` with per-step results); validate-then-mutate; custom preset save gets a routing lock and restores from fresh (not cached) routing — any change to *what* it does waits for DI-4. Full `/api/v2/scenes` test suite. All fixes preserve current behaviour and data formats (D5).
- [ ] **WebSocket** (API-09, API-10): per-client send with timeout, concurrent fan-out, drop dead clients; broadcast after the command result; use aiohttp's built-in `heartbeat`; publish a **WS event schema** (`docs/api/ws-events.json`) used by server tests and the web client.
- [x] **Home Assistant** (HA-01…15; WP-D1): `async_get_clientsession`; consume `outputs` list / dict correctly from contract fixtures; power from the right endpoint (add `power` to status); `translations/en.json`; `AbortFlow` handling; services in `async_setup` with device/entry targeting and `HomeAssistantError`; `runtime_data`; `async with` responses; base `HdmiMatrixEntity` with `has_entity_name`, shared `DeviceInfo`, firmware version, `configuration_url`; reconfigure + options flow; validated CEC command; `integration_type: "hub"`; `hacs.json`.
- [x] **Docker** (DEP-01…03, D11): single compose service, no profiles; one image with all integration deps; `UC_ENABLED` defaults to `false` and gates the `ucapi` import (interim guard until Phase 4's integration loader); compose example documents `network_mode: host` as required only when `UC_ENABLED=true` (mDNS); smoke tests for UC on/off.
- [ ] **Web UI breakages** (UI-01…04, UI-17, SEC-07, SEC-08 patch) — each PR goes through §5.3 capture & review; these fixes should produce **no** visual diffs except where a broken state (e.g. passcode prompt) now renders:
  - [ ] `executeProfile` → real endpoint; `ApiError` with `status`/`code`; passcode prompt on 403/`passcode_required`.
  - [ ] `escapeHtml` escapes `& < > " '`; patch every unescaped sink listed in SEC-08; icons restricted to emoji or icon-library keys.
  - [ ] Align WS client with the schema; handle all server events; resync (`refresh()`) on reconnect; infinite capped backoff with "reconnecting" indicator; kiosk handles `switch`/`switch_all`.
  - [ ] Fetch timeout via `AbortController`; only the originating client shows refresh toasts.
  - [ ] Fix `cec-tray` handler leak.
  - [ ] Fix the functional UI bugs found by the baseline capture (UI-23…UI-31, BE-31); each fix un-skips or updates its catalog entry through §5.3 review.
- [ ] **Remote integration** (per the UC audit): multi-step setup with a matrix password field, `AUTHORIZATION_ERROR`, abort handling, no setup-payload logging, host change requires the password (UC-05, UC-02 short-term); remove `driver_url` / add `UC_DRIVER_URL` (UC-03); rename propagation in place (UC-08); power switch sync (UC-09); correct UC env var names + host-networking compose example for UC (UC-11, DEP-02); real preset names (UC-14); `ucapi==0.7.0` everywhere (UC-15); `driver.json` text and validation (UC-16).

**Exit:** route inventory 100% (becomes blocking); HA test job green with real `hass`; Playwright suite covers passcode flow, routing, presets, profiles, scenes, CEC remote; image passes smoke with UC on and off; all visual diffs reviewed and approved; tag **v0.2.0 "Stabilize"**.

### Phase 3 — Security baseline (3-5 days)

Goal (D2): **simple.** A home/lab user can optionally gate admin functions with a PIN; kiosk and everyday control keep working with no login; invisible protections are always on.

**Access model — two levels, one optional PIN each:**

| Level | Covers | Default | When a PIN is set |
| --- | --- | --- | --- |
| **Control** | Status, routing, presets recall, run profiles/scenes/shortcuts/macros, CEC, matrix power | **Open** — kiosk, Flic, HA work with zero setup | Only if the user also enables `CONTROL_PIN` ("lock everyday control too"). Devices unlock once and are remembered; HA/Flic use an API key. |
| **Admin** | Settings, matrix host & credentials, create/edit/delete profiles/scenes/macros/shortcuts, integrations config, EDID/HDCP/HDR/scaler, reboot, dashboard layout editing | Open until an admin PIN is set; first-run prompt + persistent banner recommends setting one | Web UI shows the existing passcode-pad style dialog → admin session (30 min idle, "Lock" button). |

- [ ] **Admin PIN** (SEC-01): set on first run in the web UI (skippable) or via `ADMIN_PIN` env var; 4-8 digits; PBKDF2 in a thread executor; 5 wrong attempts → exponential lockout; recovery by restarting with `ADMIN_PIN_RESET=true` (documented) — no email, no accounts.
- [ ] **Admin session:** `HttpOnly`, `SameSite=Strict` cookie; WS connections inherit the level of their cookie; admin-only WS commands rejected otherwise.
- [ ] **Optional control lock:** `CONTROL_PIN` (or toggle in settings). Kiosk/browser devices enter it once → long-lived "remembered device" cookie, listed and revocable in settings. HA and Flic use an **API key** generated in settings (header `X-API-Key`; query-param `?key=` accepted for Flic simple requests, redacted from logs). When no control lock is set, keys are not needed at all.
- [ ] **Kiosk:** always operates at Control level and never exposes admin screens; its "Full UI" link lands on the main UI, which prompts for the admin PIN only when an admin action is attempted.
- [ ] **Always-on protections, regardless of PIN settings** (SEC-02): mutating routes require `Content-Type: application/json` and a same-origin `Origin`/`Referer` (blocks cross-site requests from other tabs); CORS same-origin by default (`CORS_ALLOWED_ORIGINS` to extend); Host header must be an IP literal, `localhost`, `*.local`, or in `ALLOWED_HOSTS` (blocks DNS rebinding) with a clear error page explaining how to add a hostname; WS Origin check.
- [ ] **Matrix host & credentials** (SEC-03, SEC-09, SEC-10): host change is an admin action **and always requires re-entering the matrix password** (so a stored password can never be sent to a new host, even with no admin PIN); resolve-then-validate the target (private-range allow-list, no loopback/link-local/metadata, port 1-65535 int); credentials configurable in UC setup, web settings, and env; never log login payloads/responses (redaction filter); remove forced DEBUG; optional TLS certificate pinning (store fingerprint on first successful connect, warn on change).
- [ ] **PINs** (SEC-04…06): never serialize `passcode_hash` to clients (separate internal/external DTOs); changing/removing a PIN or deleting a protected item requires the current PIN; add API to set/clear profile PINs; pass the profile map to inheritance checks; hash/verify in a thread executor; per-item attempt limiter with exponential lockout.
- [ ] **Hardening** (SEC-11…13, API-15): generic error responses with correlation IDs (details in logs only); remove path listings; strict body validation (types, ranges, known keys) via a small schema layer; rate limiter keyed on route class, WS connection cap, XFF only from `TRUSTED_PROXY_IPS`; static serving via `resolve()` + `is_relative_to`.
- [ ] HA config flow gets an optional API-key field (HA-16); Flic docs show both keyless and keyed setups.
- [ ] Remote integration token auth: subclass `IntegrationAPI` authentication against `UC_AUTH_TOKEN`, `pwd` in mDNS TXT, driver registration with token; document firewalling port 9095 to the Remote's IP (UC-02).
- [ ] Per-item Profile/Scene PINs kept alongside the admin PIN (DI-6), fixed as above; the UI labels the difference.
- [ ] Add `SECURITY.md`: threat model for a home/lab LAN, what the PINs do and don't protect, "don't expose port 8080 to the internet; use a VPN/reverse proxy with its own auth", vulnerability reporting.

**Exit:** security test suite covering all three configurations (no PIN / admin PIN / admin + control PIN): admin routes denied without session when PIN set; control routes open or keyed as configured; cross-site simple request rejected in every configuration; DNS-rebinding Host rejected; SSRF bypass corpus rejected; stored matrix password never sent to a changed host; hash never serialized; brute-force lockout. Kiosk E2E passes with zero configuration. HIL Session 2 (HIL-B) passes with an admin PIN set; tag **v0.3.0 "Secure"**.

### Phase 4 — Backend consolidation (6-10 days)

Goal: one runtime, one owner of state, one execution path, **modular opt-in integrations** (D4) — same concepts, less code.

Work items marked *(DI-n)* implement the agreed outcome in §2.3.

- [ ] **Single runtime + integration loader** (BE-19, BE-20, DEP-07, D4, D11): `run.py` always starts the core (MatrixService + REST + WS + web UI + kiosk), then loads each integration whose env var is enabled. Disabled integrations are never imported, open no ports, and register no routes. Delete `run_server.py` (or thin alias) and `USE_MODULAR`.
- [ ] **Finish `src/integrations/` as the integration framework:** Detailed design, HubClient surface, migration rules and refactor sequence: `docs/audits/UC_INTEGRATION_AUDIT.md` §5. Rewrite `api_client.py` as `HubClientHttp` against the contract fixtures and delete `adapter.py` (UC-18); implement the agreed entity model (DI-9: UC-10, UC-12, UC-13); publish/unregister mDNS ourselves (UC-11).
  - [ ] `Integration` interface (`config_from_env`, `start(hub)`, `stop`, `health`, optional `routes`) + registry + loader; per-integration health in `/api/health`; startup log lists enabled/disabled integrations.
  - [ ] `HubClient` facade with an **in-process** implementation (default) and the existing **HTTP** `api_client.py` finished as the second implementation (fix the `allconnect` mapping, add auth-key support, contract tests against both implementations).
  - [ ] **`integrations/unfolded_circle`** (`UC_ENABLED`, `UC_PORT`, `UC_DISABLE_MDNS`) — the Remote 3 driver moved out of `driver.py` onto `HubClient`: one entity factory (BE-22), media-player state updates (BE-24), no rebuild on transient name failures, dead code removed (BE-23), entities update from hub events instead of its own poller.
  - [ ] **`integrations/flic`** (`FLIC_ENABLED`) — button registry, auto-discovery and Flic-specific endpoints moved out of `rest_api/integrations.py`; convenience routes (`/api/input/next|previous`) stay in core.
  - [ ] **`integrations/homeassistant`** (`HA_DISCOVERY_ENABLED`) — advertises the hub over mDNS/zeroconf so the HA component's config flow discovers it (adds `zeroconf` to the HA manifest). The HA component itself stays in `custom_components/`.
  - [ ] Template + docs for adding an integration (future MQTT/webhooks/scheduler use the same interface).
- [ ] **One env-var set** documented in CONFIGURATION.md: core (`MATRIX_HOST`, `MATRIX_PORT`, `MATRIX_USER`, `MATRIX_PASSWORD`, `MATRIX_VERIFY_TLS`, `API_PORT`, `DATA_DIR`, `LOG_LEVEL`, `ADMIN_PIN`, `CONTROL_PIN`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`) + one block per integration; old names (`OREI_*`, `REST_API_PORT`, `UC_CONFIG_HOME`, …) accepted as deprecated aliases with a single warning.
- [ ] **Package layout:** `src/hub/{core,transport,domain,persistence,rest_api,integrations}` with proper package imports (no `sys.path` tricks, no dual `try: from x / except: from .x`).
- [ ] **`MatrixService`** owns connection, snapshot, `NameStore` (BE-16), event bus. REST, WS, and integrations subscribe to events; renames propagate everywhere.
- [ ] **`MatrixModel`** port/capability abstraction (BE-26, D9); remove hard-coded default host (first run asks for it in the web UI if `MATRIX_HOST` is unset).
- [ ] **Domain model** — concepts stay (Preset, Profile, Macro, Scene, Shortcut, Dashboard); roles and overlaps per the agreed outcomes of DI-1…DI-6:
  - Profile gains `scaler`/`arc` fields (API-22) — not a behaviour change, fixes a latent bug.
  - Scene/Profile roles *(DI-2)*; Shortcut targets *(DI-3)*; custom preset save *(DI-4)*; single visibility store *(DI-5, API-20)*; PIN semantics *(DI-6)*.
- [ ] **`ActionRunner`** (API-19): the single executor for profiles, scenes, macros, shortcuts, presets; structured per-step results; used by REST, WS, and every integration. Behaviour of each action type is pinned by Phase 2 tests before the refactor, so this is a pure consolidation.
- [ ] Scene v1 routes and legacy `scenes.json` handled per *DI-1*; delete dead `config.SceneManager` (API-18); v2 data file gains `schema_version` (API-12).
- [ ] **Persistence migrations** (PER-04): every file gets `schema_version`; ordered migration functions with backup-before-migrate; tests for each migration from real old files.
- [ ] One response envelope (API-21); OpenAPI spec generated from route definitions + schemas (closes roadmap TD-09 and feeds DOC-03).

**Exit:** coverage targets met on new packages; mypy strict on `core/`, `domain/`, `persistence/`; all L1-L5 green; no behavioural diffs in the Playwright suite; line count of `src/` reduced (target ≥ 20%).

### Phase 5 — UI simplification (8-12 days)

Goal: fewer layers, same concepts, same look.

**What stays (explicitly preserved):**

- Dark glassmorphism palette, HSL accent + secondary accent system, the four Tron-style presets and swatch picker, card opacity control, the opt-in Tron background.
- Tabs: Matrix · Dashboard · Inputs · Outputs · Profiles (pinning/reordering stays).
- Control Deck side-nav, matrix grid routing, CEC bottom-drawer remote on output tiles, dashboard cards, kiosk swipe tabs (Routing · Presets · Shortcuts · Profiles).

**Guardrail for the aesthetic:** the §5.3 capture & review process (baselines taken in Phase 0, before any UI code changed). Every Phase 5 PR shows before/after for each affected catalog entry and needs your approval of the baseline update. Structural refactors (ES modules, overlay stack, tokens extraction, CSS split, dead-code removal) must produce **zero** visual diffs; only items explicitly intended to change the look (e.g. consolidated Settings drawer, 44 px touch targets) may produce approved diffs.

Per DI-7, the consolidated Settings drawer is mocked up first and reviewed via a before/after page before it is built.

**Work items:**

- [ ] **Design tokens** — extract all colour/spacing/radius/shadow/motion tokens to `web/css/tokens.css` (single source for main UI and kiosk).
- [ ] **ES modules, no build step** (UI-13) — `web/js/core/` (`api.js`, `ws.js`, `state.js`, `html.js`, `overlay.js`, `toast.js`), one `main.js` per page via `<script type="module">`. Remove `window.*` globals.
- [ ] **Safe rendering by construction** (SEC-08 structural) — tagged-template `html\`` helper that auto-escapes interpolations; ESLint rule forbidding raw `innerHTML` outside the helper.
- [ ] **Delete dead code** (UI-09, UI-15, UI-20) — the files listed in UI-09; direct `fetch` calls routed through `api.js`.
- [ ] **One Settings drawer** *(DI-7)* (UI-05, UI-14) — replace General/Hardware/Interface/Theme/Integrations/Shortcuts drawers + hidden modal + `settings-panel.js` with a single drawer with sections and hash routes (`#settings/general`, …). Control Deck keeps four quick actions: Route All, Presets, Refresh, Settings. Overlay count drops from ~11 to ~5.
- [ ] **One overlay stack** (UI-07) — stack-based manager: single Escape handler closes the top layer only, focus trap + `role="dialog"` + `aria-modal` + labelled titles for every overlay, focus restore on close.
- [ ] **Unified editor shell** — Profile, Scene, and Macro editors share a drawer shell (header, validation summary, sticky Save/Cancel), replace `prompt()` pickers with searchable pickers (UI-19).
- [ ] **One CEC remote component** (UI-12) — shared by the cec-tray and the kiosk bottom drawer; single trackpad implementation.
- [ ] **Kiosk rebuilt on shared core** (UI-11, UI-08, D7) — `kiosk.html` becomes a thin shell importing core + kiosk views; pins and layout server-backed via Dashboard *(DI-5)*; works with zero configuration, or with a one-time remembered-device unlock when `CONTROL_PIN` is set (Phase 3).
- [ ] **Dashboard single store** *(DI-5)* (UI-08) — remove the localStorage config path; migrate once.
- [ ] **Accessibility** (UI-07) — 44 px minimum touch targets; preset actions visible on touch devices; remove `user-scalable=no`; buttons instead of `div onclick`; ARIA in kiosk; `prefers-reduced-motion` disables Tron background and non-essential transitions; contrast check on all 4 presets.
- [ ] **Feedback consistency** — one connection indicator (header border line, keep current style) + "reconnecting" state; optimistic updates roll back on `*_failed` events; toast de-duplication.
- [ ] **Performance** (UI-16) — Tron background renders only when cycles move, capped at 30 fps, blur reduced on low-power/kiosk; lazy-load editors.
- [ ] **CSS consolidation** (UI-10) — split `components.css` into per-component files; remove unused selectors (verified by visual regression, not by guesswork).
- [ ] **Device icons** (UI-22) — establish provenance of the current set; if the licence can't be confirmed, replace it with a permissively licensed set (e.g. MIT/ISC line icons) or redraw in-house as clean vector paths, matching the current style; reviewed via §5.3. Target < 5 KB per icon.
- [ ] Fix keyboard shortcuts (UI-06), `api-copy` base URL (UI-18), add a real PWA manifest + icons (UI-21) or drop the claim.

**Exit:** every visual diff reviewed and approved per §5.3, with the catalog updated for any new states; real-device capture (kiosk, iPad, phone) reviewed; `LOOK_AND_FEEL.md` still accurate; Playwright E2E + axe accessibility checks pass on all pages; JS size reduced (target ≥ 25%); kiosk shares ≥ 90% of its logic with the main UI.

### Phase 6 — Repository hygiene & release engineering (1-2 days)

- [ ] (History purge and LICENSE moved to Phase 0.) Re-verify no vendor binaries or HAR captures crept back in; add a CI check rejecting `*.bin`, `*.exe`, `*.c4z`, `*.har`, and files > 2 MB outside LFS-tracked snapshot paths.
- [ ] Licence audit of every bundled asset (icons, fonts, images) with a `THIRD_PARTY_NOTICES.md`; release blocked until UI-22 is resolved.
- [ ] Delete `setup.py`; `pyproject.toml` as sole metadata with correct packages (DEP-04).
- [ ] Single version source (e.g. `hub/__init__.py:__version__`) feeding `driver.json`, HA `manifest.json`, `/api/info`, Docker labels; release script bumps all (DEP-06).
- [ ] Locked, hashed requirements (`pip-compile`), `requirements-dev.txt`, digest-pinned base image, SHA-pinned actions, Dependabot/Renovate (DEP-08, SEC-15).
- [ ] `.dockerignore`, remove `src/` leftovers, remove one-off scripts, remove `full_codebase_audit_prompt.md`, replace `config/*.json` seeds with clean examples (DEP-09, DEP-12, DEP-13, BE-27, API-17).
- [ ] Multi-arch images (amd64 + arm64) published on tag.

### Phase 7 — Documentation (2-3 days)

- [ ] `README.md` rewritten: what it is, supported hardware, a copy-paste `docker-compose.yml` quick start for a home/lab host, first-run walkthrough (matrix host, credentials, optional admin PIN), enabling integrations via env vars (Remote 3, Flic, HA discovery), clients (HA component via HACS, Web/Kiosk), security note, troubleshooting (DOC-02).
- [ ] New: `docs/CONFIGURATION.md` (every env var, generated or checked by a test against the code), `docs/ARCHITECTURE.md` (§3 of this plan, updated), `CHANGELOG.md` (from git history + this plan), `SECURITY.md`, `docs/INTEGRATIONS.md` (one section per integration: env vars, ports, network requirements, setup steps) (DOC-12).
- [ ] `docs/API_REFERENCE.md` generated from OpenAPI + WS event schema; Swagger UI served at `/api/docs` (DOC-03).
- [ ] Rewrite `HOME_ASSISTANT.md` around the real component (REST examples as appendix) (DOC-04); fix `DOCKER.md` (DOC-05), `FLIC_SETUP.md` routes, `CONTRIBUTING.md` (DOC-13).
- [ ] `OREI_API_COMMANDS.md` updated from HIL-A captures + new Telnet section (DOC-11).
- [ ] Merge `MASTER_INDEX.md` + `docs/README.md` into one index (DOC-10); replace `PROJECT_ROADMAP.md` with a short `ROADMAP.md` of open items (DOC-01).
- [ ] Refresh or replace the vendored UC API docs with a source/version header; update or retire `UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md` (UC-20).
- [ ] Archive `WEB_UI_IMPLEMENTATION_PLAN.md`, `CEC_CONTROL_ARCHITECTURE.md`, `PHASE_8_SPEC.md` to `docs/archive/design/` with a banner listing deviations (DOC-06…08); move `IR_CONTROL_ROADMAP.md` to `docs/proposals/` without version numbers (DOC-09); move vendored UC API docs to `docs/vendor/`.

### Phase 8 — Validation campaign & 1.0 release (3-5 days + 72 h soak)

- [ ] Full L0-L5 green on the release candidate.
- [ ] HIL Session 3: HIL-B regression, HIL-C fault injection, HIL-D 72 h soak, HIL-E real clients.
- [ ] `docs/validation/VALIDATION_REPORT.md`: matrix of every feature × every client with pass/fail/not-validated, firmware versions, known limitations, per-device CEC support table.
- [ ] Update the "Supported Models" table only with what was actually tested.
- [ ] Tag **v1.0.0**; publish images; publish HACS repository; publish release notes; announce to the UC community and HA forums (D1).

---

## 7. Execution roadmap

Work is organised into work packages (WPs) in parallel lanes. Each WP closes register findings and **exits with evidence**: the affected features in the ledger ([`docs/validation/VALIDATION_PLAN.md`](validation/VALIDATION_PLAN.md) §3) reach the stated level. Phase numbers in §6 are kept for reference. The WPs below are the execution order.

**Lanes:** **V** validation · **A** core/transport · **B** Remote integration · **C** domain/API · **D** clients and deployment (HA, Flic, Docker) · **E** web UI · **F** security · **G** release and docs.

| WP | Lane | Scope (register IDs) | Depends on | Exit evidence | Status |
| --- | --- | --- | --- | --- | --- |
| WP-V1 | V | ✅ Validation framework: `features.yaml` registry (every feature, ~200), evidence schema, scenario runner (`tools/validate/`), `LEDGER.md` generator, CI enforcement | — | Ledger generated in CI; every feature listed with its current honest level | next |
| WP-V2 | V | **C0 baseline truth:** run every feature at V2/V3 on the simulator against current code; failures become findings | WP-V1 | First `LEDGER.md`; new register rows | after V1 |
| WP-A1 | A | Transport reliability (BE-01, 03, 04, 05, 07, 11, 12, 17, 28–30, API-11) | — | Transport and reliability features at V2 with fault injection; loop lag < 100 ms under faults | ✅ merged 2026-09-25 |
| WP-A2 | A | Persistence and process lock (PER-01–03, TST-08, BE-18) | — | Persistence features at V2 on Windows and Linux | ✅ merged 2026-09-25 |
| WP-A3 | A | Hardware capture tooling (HIL-A) | — | Capture round-trip proven on the simulator | ✅ merged 2026-09-25 |
| WP-H1 | A | **HIL Session 1 / C0-HW:** capture + first V4 runs (routing, presets, power, TV CEC power, one profile) | WP-A3, owner hardware access | Golden captures committed; first V4 evidence | read + probe + write done 2026-09-25 (HIL-01…14); push window, live CEC, reboot and V4 runs need the owner |
| WP-A4 | A | Protocol corrections from captures (BE-13, 14, 15, 25, API-07, VAL-03, HIL-01…14); part 2: implement the device's real setting commands and prove each on hardware | WP-H1 | Affected features at V2 against golden data, V4 re-run | part 2 proven on hardware 2026-09-25: every new setting command applied and read back on the real BK-808, invalid values rejected, device restored |
| WP-B1 | B | ✅ Scripted-Remote harness + blocking `uc` CI job; evaluate the UC core simulator (UC-21) | WP-A1 merged | Every Remote entity type exercised at V3; current behaviour pinned | ✅ merged with UC-22 filed |
| WP-B2 | B | Remote integration fixes in `driver.py` (UC-01, 22, 04, 05 part, 06, 07, 17, 19, BE-02, 06, 08, 09, 10, 21) | WP-B1 | Remote features at V3; UC-01 proven fixed through the harness | ✅ done on `wp-b2-remote-fixes` (also UC-10's first toggle); UC-05 rest, UC-10 model with WP-B3/C3 |
| WP-C1 | C | Scenes, shortcuts, profile execution (API-01–08, 13, 14, 23, VAL-01, VAL-02) | WP-V2 | Domain features at V3 | after V2 |
| WP-C2 | C | WebSocket contract and schema; hub-owned event stream; truthful `/api/status` (API-09, 10, UI-02, UC-17 part, VAL-04, VAL-05) | WP-A1 | Every WS event at V2; live updates proven in the browser and HA at V3 | after A1 |
| WP-D1 | D | Home Assistant fixes + real-HA-container E2E (HA-01–15) | WP-V1 | HA features at V3 in a real HA container | done on `wp-d1-home-assistant`: HA-01…13, 15 fixed; F-HA-001…013, 015…018 at V3 (HA 2026.9.3 and 2025.1.4); HA-14 brand icons added from the favicon |
| WP-D2 | D | Docker/deployment (DEP-01–03, D11, UC-03, UC-11) | WP-A1 | Deployment features at V3 on the shipped image, UC on and off | after A1 |
| WP-B3 | B | Remote setup flow, `ucapi` 0.7.0, names, power switch, presets (UC-02 short-term, 05, 08, 09, 14, 15, 16) | WP-B2 | Remote features at V3; setup V4 on a real Remote | after B2 |
| WP-E1 | E | UI functional fixes (UI-01–04, 17, 23–31, BE-31, SEC-07/08 patch), each with visual review | WP-C2 | UI/kiosk flows at V3 with approved visuals | after C2 |
| **Gate** | | **v0.2.0 "Stabilize"** (VALIDATION_PLAN §6) | WP-A1…E1 | | |
| WP-F1 | F | Security baseline incl. Remote token auth (SEC-01–13, API-15, HA-16, UC-02, VAL-06) | v0.2.0 | Security features at V3 in all three auth configurations | |
| **Gate** | | **v0.3.0 "Secure"** | WP-F1 | | |
| WP-C3 | C/B | Backend consolidation and modular integrations (Phase 4; UC-10, 12, 13, 18; DI-9 entity model after approval of the exact change list) | v0.3.0 | No feature drops below its level; Remote entity migration proven on a real Remote | |
| WP-E2 | E | UI simplification (Phase 5) | WP-C2, v0.3.0 | Visual review approved; UI flows at V3; V4 on real devices | |
| WP-G1 | G | Hygiene and release engineering incl. optional on-Remote build (Phase 6, DI-10) | WP-C3 | Release pipeline proven; on-Remote build installed on a real Remote | |
| WP-G2 | G | Documentation (Phase 7, UC-20) | WP-C3 | Every documented feature links its ledger entry | |
| WP-V3 | V | **C8 release validation:** HIL-B/C/D/E, 72 h soak, validation report | all | Every feature at target; V5 soak | |
| **Gate** | | **v1.0.0** | WP-V3 | | |

**Running in parallel now:** WP-A1, WP-A2, WP-A3. **Next:** WP-V1 (touches only `tools/validate/`, `tests/validation/`, `docs/validation/`, CI), then WP-V2. Then WP-B1, WP-C2 and WP-D2 once WP-A1 merges. WP-D1 can start as soon as WP-V1 lands.

## 8. Definition of done (every PR)

- [ ] Register IDs listed in the PR description; checkboxes ticked here.
- [ ] Regression test that failed before the fix.
- [ ] **Evidence:** affected features have fresh evidence records at the WP's exit level (simulator scenarios in CI; hardware records for V4). The ledger shows no feature below its previous level.
- [ ] L0-L3 green (L4/L5 when touching clients or deployment).
- [ ] **UI PRs:** before/after captures for every affected catalog entry reviewed and approved (§5.3); new components/states added to the catalog; no raw colours/spacing outside `tokens.css`.
- [ ] No behaviour or data-format change to an existing feature unless its discussion item (§2.3) was agreed.
- [ ] No new `innerHTML` without the safe template helper; no new env var without CONFIGURATION.md; no new route without OpenAPI + test.
- [ ] Docs touched in the same PR when behaviour changes.

## 9. Deferred until after v1.0.0

OpenAPI-driven Python client SDK · HA `media_player`/`sensor` entities and profile buttons · scheduling engine, MQTT, outgoing webhooks (each as an opt-in integration on the Phase 4 framework) · 4-port models (cheap after `MatrixModel`) · multi-matrix · IR control · control zones · Alexa/Google/HomeKit.
