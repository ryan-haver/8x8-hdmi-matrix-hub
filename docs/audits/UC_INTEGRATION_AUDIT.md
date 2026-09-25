# Unfolded Circle Remote Integration — Audit

> **Date:** 2026-09-25 · **Scope:** the Unfolded Circle Remote 3 integration: `src/driver.py`, `driver.json`, `src/integrations/unfolded_circle/`, `run.py`, the Docker packaging, and the vendored UC API docs · **Code base:** `main` @ `12866ff` (v0.1.0)
>
> **Method:** three read-only reviews. (1) Protocol, library, metadata, and security conformance against the current upstream sources. (2) Entity model, UX, and lifecycle, including live runs of the driver against the matrix simulator with a scripted WebSocket client acting as the Remote. (3) Architecture and deployment, including a gap analysis of the unfinished modular path. Findings were checked in code. The critical command crash was reproduced by two reviews independently.
>
> **Related:** `docs/REMEDIATION_PLAN.md`. Register rows `UC-01`…`UC-21` point here, and earlier `BE-*` rows are cross-referenced.

---

## 1. Summary

The integration covers a lot of ground (74 entities, CEC remotes for every port, presets, routing). But a Remote 3 user hits real problems:

1. **A single power command disconnects the integration.** Any `on`/`off`/`toggle` or command sequence sent to any of the 16 CEC remotes raises an exception that `ucapi` does not catch, and the Remote's WebSocket closes (code 1011). An activity that powers a TV on through its CEC remote takes every entity offline (UC-01).
2. **The Remote is told everything is fine when it isn't.** Device state is always reported as CONNECTED. Entities never go unavailable when the matrix is lost. During an outage the poller pushes made-up values ("Input 0", "Disconnected") (UC-04).
3. **Hub liveness depends on the Remote.** The status poller is the only source of routing, signal, cable, and connection events for the web UI and Home Assistant, and it only runs while a Remote is connected. Remote standby disconnects the matrix (UC-17).
4. **Port 9095 is open to the LAN with no authentication.** Anyone on the network can send `setup_driver` with a different host. The hub then sends the matrix password to that host and saves the change permanently (UC-02).
5. **Setup always ends in an error**, even though it succeeded (BE-02). A mistyped reconfigure replaces the working connection (UC-05).
6. **The modular path (`src/integrations/unfolded_circle`) doesn't work against the real REST API.** Its mocked tests hide this (UC-18).
7. **The library and docs are behind.** `ucapi` is 0.5.1 against 0.7.0 upstream, with a low-risk upgrade (UC-15). The vendored API docs are several spec versions old (UC-20).
8. **UX:** 74 entities, 24 of them duplicates. Non-standard command names and no button mapping, so the physical keys don't work. Preset names are thrown away. Profiles and Scenes can't be triggered from the Remote.

**What works well:** entity IDs are index-based and stable across restarts and renames. Source selection, preset recall, and CEC `send_cmd` work. Restart/restore works. Commands return 503 while disconnected. Front-panel changes show up within one poll.

## 2. Findings

Severity: **C** critical · **H** high · **M** medium · **L** low. "Phase" refers to the remediation plan. Phase 1 wave 2 is the `driver.py` work that follows the transport fixes.

| ID | Sev | Finding | Location | User impact | Fix | Phase |
| --- | --- | --- | --- | --- | --- | --- |
| UC-01 | C | The CEC remote command map references `RemoteCommands.CURSOR_UP`, `MENU`, `POWER_ON`, and others, which don't exist in `ucapi.remote.Commands` (only `on`, `off`, `toggle`, `send_cmd`, `send_cmd_sequence`, in both 0.5.1 and 0.7.0). Any command other than `send_cmd` raises `AttributeError`, which `ucapi` doesn't catch, so the WebSocket closes with 1011 (reproduced). | `driver.py:232-250` | An activity power step or a command-sequence macro disconnects the whole integration | Map `on`/`off`/`toggle` to CEC power. Implement `send_cmd_sequence` with `repeat`/`delay`/`hold`. Wrap every handler so exceptions return `SERVER_ERROR`. Harness test covering every `cmd_id`. | 1 (wave 2) |
| UC-02 | H | Integration WebSocket 9095 is unauthenticated (`ucapi` always answers auth 200) and bound to `0.0.0.0`. `setup_driver` from any client creates `OreiMatrix(new_host)`, which logs in with the stored credentials (TLS verify off), saves the host, and clears configured entities. | `driver.py:1873-1896,2011`, `Dockerfile:74`, `docker-compose.yml` | Anyone on the LAN can control the matrix or steal its password | Short term: a host change in setup requires re-entering the matrix password, and the stored password is never sent to a new host. Then token auth (subclass `IntegrationAPI._authenticate`, `auth-token` header against `UC_AUTH_TOKEN`), `pwd` in the mDNS TXT record, and driver registration with a token. Document firewalling. | 2 (setup) / 3 (token) |
| UC-03 | H | `driver_url: ""` makes `ucapi` advertise `ws://<socket hostname>:<port>`. In bridge-mode Docker that is the container ID. | `driver.json:12` | The Remote may be unable to reach the driver (confirm on hardware) | Remove the key. Optional `UC_DRIVER_URL` env var, written into metadata at startup. | 2 |
| UC-04 | H | Device and entity state don't reflect reality. `on_connect` always sends CONNECTED. Matrix loss never sends DISCONNECTED/ERROR and never marks entities UNAVAILABLE. Sensors are seeded from `[0]*8`. During an outage the poller pushes `source: "Input 0"` and "Disconnected". `CLIENT_DISCONNECTED` (ucapi ≥ 0.4) isn't handled. | `driver.py:1519-1610,1344,1742,1804-1829` | The Remote shows live-looking state while the matrix is down | Map the matrix state machine (BE-04) to `DeviceStates` (CONNECTING/CONNECTED/ERROR). Mark all entities UNAVAILABLE while disconnected. Keep last-known values. Treat input 0 as unknown. Handle `CLIENT_DISCONNECTED`. | 1 (wave 2) |
| UC-05 | H | Setup/reconfigure swaps the working device before probing the new one. It clears `configured_entities`, so subscribed entities return 404 until the Remote resubscribes. `AbortDriverSetup` and `UserDataResponse` aren't handled. Every failure is reported as `CONNECTION_REFUSED`/`OTHER`. Setup payloads are logged. There's no credential step. Plus BE-02 (setup always ends in ERROR). | `driver.py:1854-2065` | A typo in reconfigure breaks a working install. Setup always looks failed. | Probe with a temporary client and swap only on success. Update entities in place, never clear. Handle abort. Multi-step setup with a password field and `AUTHORIZATION_ERROR`. Stop logging setup data. | 1 (wave 2: BE-02, probe-before-swap, no clearing) / 2 (full flow) |
| UC-06 | M | Standby: the supervisor restarts the poller immediately after `enter_standby` (BE-01), `matrix.disconnect()` hangs, pushes continue during standby, and `exit_standby` starts a second poller (traffic doubled). | `driver.py:1622-1644` | Battery and network use while the Remote sleeps. Duplicate events. | BE-01 fix, plus a Remote-standby flag that pauses pushes. One poller owner (UC-17). Resync on wake. | 1 (wave 2) |
| UC-07 | M | Every poll re-sends every attribute of 48–72 entities whether or not it changed (~8.6k messages/hour at 30 s). | poller `driver.py:1328-1462` | Battery drain on the Remote, log noise | Send only changed attributes (as the official Denon integration does) | 1 (wave 2) |
| UC-08 | M | Renames rebuild only `available_entities`. Subscribed `configured_entities` keep a stale `source_list` and handlers that capture old names, so after a rename `select_source "<new name>"` returns 400 (reproduced). A failed name query rebuilds entities with generic names. | `driver.py:1536-1549` | Renames break source selection until restart | Update attributes in place and read names from shared state at call time. Never rebuild on a transient failure. (Full fix: NameStore, BE-16.) | 2 / 4 |
| UC-09 | M | `switch.matrix_power` starts ON and is never synced, although `power` is polled. The handler ignores connection state. | `driver.py:983-1037` | Wrong power state shown | Sync from polled power. Return 503 when disconnected. | 2 |
| UC-10 | M | `media_player.output_N` mixes routing (source) with TV power and volume (CEC). State stays UNKNOWN. Toggle from UNKNOWN sends CEC OFF (BE-24). | `driver.py:848-980` | First toggle turns the TV off. Confusing entity. | Part of the entity model (DI-9) | 4 |
| UC-11 | M | mDNS/Docker: `UC_INTEGRATION_INTERFACE=0.0.0.0` is published as the service address. SRV target is `<container-id>.local` in bridge mode. IPv4 only. `ucapi` never unregisters its zeroconf, which is the root cause of the `NonUniqueNameException` retry loop and the `clear_stale_mdns` workaround. Each `api.init` retry adds a duplicate attribute listener, so every `entity_change` is sent twice. Env var names in docs and plan don't match what `ucapi` reads (`UC_DISABLE_MDNS_PUBLISH`, `UC_INTEGRATION_HTTP_PORT`). | `driver.py:363-402,2185-2214`, `Dockerfile`, `run.py:17` | Discovery fails or duplicates. Double events after a restart race. | Host networking + `UC_INTEGRATION_INTERFACE=<LAN IP>` + `UC_MDNS_LOCAL_HOSTNAME`. In bridge mode, disable mDNS publish and register by `driver_url`. Correct env var names. Later, publish mDNS ourselves and unregister on shutdown. | 2 / 4 |
| UC-12 | L | Remote command names don't follow the UC patterns (`POWER_ON`, `UP`, `SELECT`, `PLAY`, `MUTE` instead of `on_off` feature, `CURSOR_UP`, `CURSOR_ENTER`, `PLAY_PAUSE`, `MUTE_TOGGLE`). No `button_mapping`. UI tiles use text/emoji, not `uc:` icons. | `driver.py:686-845` | Physical D-pad and volume keys do nothing unless mapped by hand | Standard names + `button_mapping` + icons. Command renames break users' macros, so handled with DI-9. | 4 (DI-9) |
| UC-13 | L | Status sensors are `CUSTOM` text sensors. `binary` exists even in 0.5.1. `output_N_connected` and `output_N_cable` report the same thing. `output_N_source` duplicates the media player source. | `driver.py:1040-1173` | 40 status entities, 24 redundant | Binary sensors, merge duplicates (DI-9) | 4 (DI-9) |
| UC-14 | L | Preset names are hard-coded "Preset N" although the device reports them (`get video status.allname`). | `driver.py:630,1185` | Generic preset buttons | Use real preset names, updating in place on change | 2 |
| UC-15 | M | `ucapi` pinned to 0.5.1 (latest 0.7.0, 2026-05-10). `pyproject.toml`/`setup.py` say `>=0.5.0`, so installs resolve to different versions. 0.7.0 adds log sanitising, queued WebSocket processing, Select/IR entities (0.5.2), entity icons/descriptions (0.6.0), and supported-entity filtering. The reviewers tested all 11 entity factories on 0.7.0 with no changes. | `requirements-uc.txt:8`, `pyproject.toml:26` | Missing fixes. Inconsistent installs. | Pin `ucapi==0.7.0` everywhere. Keep listener parameter names (`entity_ids`). Retest with the harness. | 2 |
| UC-16 | L | `driver.json`: `min_core_api` not chosen deliberately; generic `driver_id` (also the mDNS instance name); host default `192.168.0.100` with no validation; the info text says the matrix must be on the Remote's network (it must be reachable from the hub); stale `release_date`; English only. | `driver.json` | Minor setup confusion | Correct the text and validation. Set `min_core_api` deliberately when adopting new setup errors. Version and date from the single version source (DEP-06). Keep `driver_id` (changing it breaks installs). | 2 / 6 |
| UC-17 | H | Hub liveness is tied to the Remote. The poller, the only thing that emits `routing_change`/`connection_change`/`signal_change`/`cable_change` over `/ws`, is started only by UC `on_connect`/`on_exit_standby`/reconnect and stops when the Remote disconnects. `on_enter_standby` disconnects the matrix. In API-only mode nothing emits these events at all. | `driver.py:1608-1644,1745` | Web UI and HA lose live updates whenever the Remote sleeps or isn't connected | Start the poller with the hub, independent of any Remote. UC standby only pauses UC pushes. Long term, MatrixService owns polling (Phase 4). | 1 (wave 2) / 4 |
| UC-18 | H | The modular path doesn't work against the real API. It ignores the `{success,data,error}` envelope (health check always fails, names never load, profiles/scenes always empty); maps routing into `allconnect` (BE-20); reads signal from the wrong endpoint; posts `output: 0` for switch-all (rejected); sends next/previous output in the body (the handler reads the query string); its WS client has no reconnect, resync, or auth. Only 3 of 11 entity types exist. Mocked tests hide all of this. | `src/integrations/unfolded_circle/*`, `tests/test_integrations_adapter.py` | None today (unused), but it blocks D4 | Rewrite `api_client.py` as `HubClientHttp` against the contract fixtures. Delete `adapter.py`. Implement the design in §5. | 4 |
| UC-19 | L | `restore_from_config` runs before `api.init` and blocks on an unreachable matrix. `CONFIG_FILE` ignores `ucapi`'s `config_dir_path`. Hard-coded 9095 port check (BE-21). `driver.json` loaded relative to the CWD. `api` is a `__main__`-only global (works when run via `run.py`, breaks when imported). | `driver.py:443-627,2120-2214` | Slow start when the matrix is down. Fragile packaging. | Start the WS server first and restore asynchronously. Use `api.config_dir_path`. Package-relative paths. `_driver_state.api` everywhere. | 1 (wave 2) / 4 |
| UC-20 | M | Vendored UC API docs are stale: integration API 0.12.1-beta vs 0.16.0-beta upstream, core WS API 0.31.0 vs 0.45.0, REST 0.40.0 vs 0.52.0. `UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md` misses the 0.4.0 `CLIENT_DISCONNECTED` change. | `docs/remote3-*.md` | Development against outdated contracts | Refresh with a source/version header, or link upstream instead of vendoring. Move to `docs/vendor/`. | 7 |
| UC-21 | H | No automated test exercises the integration as a Remote would. Every bug above was found manually. | `tests/` | Regressions go unnoticed | Scripted-Remote harness (§7) as a blocking CI job, built before any `driver.py` change | 1 (wave 2, first) |

## 3. Entity inventory (current, confirmed live: 74 entities)

| Type (count) | entity_id | Name | Features / class | State and attributes | Commands |
| --- | --- | --- | --- | --- | --- |
| Remote (1) | `remote.orei_matrix` | "OREI Matrix" | SEND_CMD | ON; UNAVAILABLE only on explicit disconnect | `PRESET_1..8`; `on`/`off` → 501; one "Presets" page with generic labels |
| Button (8) | `button.preset_N` | "Preset N" | press | AVAILABLE | recall preset N |
| Remote (8) | `remote.input_N_cec` | "{input} CEC" | SEND_CMD, ON_OFF | always ON | 19 simple commands → input CEC; `on`/`off` crash (UC-01) |
| Sensor (8) | `sensor.input_N_signal` | "{input} Signal" | CUSTOM | "Active" / "No Signal" | — |
| Sensor (8) | `sensor.input_N_cable` | "{input} Cable" | CUSTOM | Connected / Disconnected / Unknown | — |
| Switch (1) | `switch.matrix_power` | "Matrix Power" | ON_OFF, TOGGLE | ON at start, never synced | power on/off |
| Media player (8) | `media_player.output_N` | "{output}" | ON_OFF, TOGGLE, SELECT_SOURCE, VOLUME_UP_DOWN, MUTE_TOGGLE; TV | UNKNOWN until a command; source list = input names | select source → routing; power/volume/mute → output CEC |
| Remote (8) | `remote.output_N_cec` | "{output} TV" (e.g. "TV TV") | SEND_CMD, ON_OFF | always ON | 12 simple commands → output CEC; `on`/`off` crash |
| Sensor (24) | `sensor.output_N_connected` / `_cable` / `_source` | "{output} Connected / Cable / Source" | CUSTOM | strings | — |

IDs are index-based and stable, and any future model must keep every surviving ID. Names are fixed when entities are created. No entity sets an icon or `device_id`.

## 4. Target entity model (proposal, pending discussion item DI-9)

The official integrations expose a handful of entities per device. What users actually put in activities and macros is: route output X to input Y, recall a preset/profile/scene, and CEC control of TVs and sources. Proposed model (~35–45 entities; optional groups selectable at setup):

1. **`remote.orei_matrix`** — the activity anchor. Simple commands `PRESET_n`, `PROFILE_<slug>`, `SCENE_<slug>`, `ROUTE_ALL_IN_n`, `OUT<m>_IN<n>`, `ALL_TVS_ON/OFF`. UI pages for Presets (real names), Profiles, Scenes, Route-all. This makes Profiles and Scenes usable from the Remote.
2. **Per-output routing** — `select.output_N_source` (options = input names; needs ucapi ≥ 0.5.2 and Remote firmware support). If not adopted, `media_player.output_N` becomes routing-only, with state derived from the connection.
3. **Per-output TV control** — `remote.output_N_cec` with working power, standard command names, `button_mapping`, and icons.
4. **Per-input source control** — `remote.input_N_cec`, with the same fixes.
5. **Status** — `sensor.output_N_display` and `sensor.input_N_signal` as binary sensors (16). Cable, connected, and source sensors dropped or offered as opt-in extras.
6. **Buttons** — `button.preset_N` kept; optional `button.profile_<id>`.
7. **`switch.matrix_power`** — synced from the device.

**Migration rules:** keep every surviving entity ID. Profile and scene IDs are slug- or UUID-based so reordering doesn't break macros. Removed IDs and renamed commands are listed in the release notes and shown on a setup confirmation page.

## 5. Architecture: finishing the modular integration (decision D4)

**Current coupling.** The legacy driver owns more than the Remote: it starts and stops the only poller, disconnects the matrix on standby, and holds the lock file and the mDNS workarounds. These responsibilities move into the core (`MatrixService`) before the UC code is moved.

**Layout (Phase 4):**

```text
src/hub/integrations/base.py               Integration protocol, registry, loader
src/hub/integrations/hub_client.py         HubClient protocol + Snapshot/Event types
src/hub/integrations/hub_client_local.py   in-process (MatrixService, ActionRunner, event bus)
src/hub/integrations/hub_client_http.py    REST + /ws: envelope, X-API-Key, reconnect + resync
src/hub/integrations/unfolded_circle/
    __init__.py   config_from_env(), UnfoldedCircleIntegration(start/stop/health)
    config.py     UC_ENABLED, UC_INTEGRATION_HTTP_PORT, UC_INTEGRATION_INTERFACE,
                  UC_DISABLE_MDNS_PUBLISH, UC_CONFIG_HOME (default $DATA_DIR/uc), HUB_URL, HUB_API_KEY
    entities.py   one factory: build_entities(model, snapshot) (BE-22)
    handlers.py   command handlers → HubClient (fixed command map)
    state.py      event → attribute projection (pure, unit-tested)
    setup.py      setup flow
    migration.py  import legacy config_state.json
    __main__.py   standalone entry using HubClientHttp (on-device build)
```

**HubClient surface:** `snapshot()`; `switch(input, output|None)`, `recall_preset(n)`, `power(on)`, `send_cec(kind, port, cmd)`; `run_action(kind, id)`; `subscribe(callback)` with events `routing`, `signal`, `cable`, `display`, `power`, `names`, `presets`, `hub_connection`. Both implementations must pass one shared contract suite.

**Events instead of polling:** on subscribe, push the snapshot projection. After that, apply events. `names` updates entities in place. `hub_connection` maps to the device state and to UNAVAILABLE. Standby only pauses pushes.

**Migration:** `driver_id` and entity IDs unchanged. On first start, the legacy `config_state.json` is imported into core settings and renamed `.migrated`. Setup no longer asks for the matrix host (the core owns it).

**Refactor sequence:** (1) harness pins legacy behaviour → (2) minimal legacy fixes (Phase 1 wave 2) → (3) HubClient protocol + HTTP client against the contract fixtures → (4) local HubClient on MatrixService → (5) pure entity/state code with golden tests (entity ID set equals legacy) → (6) integration class + loader, harness unchanged → (7) delete `driver.py`, `USE_MODULAR`, `run_server.py`; migration test; real-Remote check.

## 6. Deployment options

| | In the hub container (default) | On the Remote (optional artifact) |
| --- | --- | --- |
| Networking | Needs host networking or manual driver-URL registration for discovery | No mDNS issues: the Remote core talks to localhost |
| Updates | One image, updates together | Second artifact installed on the Remote; version skew handled by a `min_hub_api` check |
| Security | In-process, no key | API key stored on the Remote when a control PIN is set |
| Latency | Lowest | One extra LAN hop (negligible) |
| Complexity | Simplest | Requires a production-quality `HubClientHttp` (needed for D4 anyway) |

**Recommendation (pending DI-10):** keep in-hub as the default. Offer an on-device aarch64 build (PyInstaller, packaged as `uc-intg-hdmi-matrix-<ver>-aarch64.tar.gz` and attached to releases) once `HubClientHttp` passes the contract suite. It's the better choice for users who can't use host networking (NAS, Kubernetes, Docker Desktop on macOS). *Unverified; confirm against the official docs and the build workflows of Unfolded Circle's integrations before committing: packaging layout, size and memory limits, the builder image, and whether switching an existing user from external to on-device creates a new integration instance (activities would need re-mapping).*

## 7. Test strategy: scripted Remote harness

`tools/uc_remote_sim.py` plus a pytest fixture `uc_remote`: a WebSocket client that speaks the integration API, chained as simulator → hub core → UC integration (port 0, mDNS off) → `uc_remote`. `ucapi` ships no test helpers.

Test cases, run against both HubClient implementations once they exist:

1. Handshake: auth, `get_driver_version`, `get_driver_metadata` matches `driver.json`.
2. Setup flow: SETUP → OK; reconfigure keeps subscriptions; bad host keeps the working device; abort handled.
3. Entity set: available entities equal the golden ID set; names from the name store.
4. Subscribe → entity states reflect the simulator.
5. Commands: select source changes routing and emits `entity_change`; preset; CEC `send_cmd`; **`on`/`off`/`toggle`/`send_cmd_sequence` return 200 and the connection stays open**; unknown command returns 400/501 without disconnecting.
6. Front-panel change in the simulator → `entity_change` within one cycle.
7. Rename in the web UI → name and source list updated in place; `select_source` with the new name works.
8. Matrix outage (simulator faults) → ERROR + UNAVAILABLE, no fabricated values; recovery → CONNECTED + resync.
9. Standby → no pushes, matrix stays connected, web UI still gets events; wake → resync, exactly one poller.
10. Only changed attributes are pushed.
11. Legacy `config_state.json` import; entity IDs unchanged.
12. Auth: token required when configured; HTTP HubClient without a key fails with a clear setup error when a control PIN is set.

CI: a blocking `uc` job (`pytest tests/uc`). The Docker smoke test runs with UC on and off.

## 8. Upstream conformance and upgrade path

- **ucapi 0.7.0** (2026-05-10, Python ≥ 3.11). Since 0.5.1: Select and IR Emitter entities (0.5.2); breaking `MediaType` → `MediaContentType`, `StrEnum`, named optional arguments, entity icon/description, media browse (0.6.0); supported-entity-type filtering, version/localisation requests, queued WS processing, log sanitising (0.7.0). Still missing upstream: token auth, mDNS unregister.
- **Upgrade steps:** pin `0.7.0` in all three places; keep listener parameter names; fix UC-01 first (it crashes on both versions); retest with the harness. Adopting Select needs Remote firmware support.
- **Integration API spec 0.16.0-beta** (core-api `36fe94a`, 2026-09-20). Unreleased additions (new setup error values, `error_message`, setup keep-alive, `language` in `setup_driver`, `get_runtime_info`) aren't in `ucapi` yet. Watch for them before redesigning the setup flow.
- **Adopt:** token auth, multi-step setup with a password field and specific error codes, Select for routing, binary sensors, button mapping and standard command names, `send_cmd_sequence` semantics, entity icons, device state machine, changed-only updates.

## 9. Real Remote 3 validation checklist (HIL-E)

1. Install and discover; setup ends in SUCCESS; the entity picker matches the model.
2. Reconfigure with a wrong IP: the working setup survives. Correct IP: no duplicates, no 404s in existing activities.
3. Every CEC remote: power button, on/off in an activity, a command-sequence macro, hold-to-repeat volume. The integration stays connected.
4. Physical D-pad and volume keys work on CEC remote pages without manual mapping; UI pages show icons.
5. Source selection from the entity screen and from an activity; the source list updates after renaming an input in the matrix UI and in the hub web UI.
6. Front-panel routing change, cable unplug, and signal loss show within one cycle.
7. Unplug the matrix network: entities UNAVAILABLE within one poll, commands fail with a visible error, no fabricated values, recovery after reconnect.
8. Reboot the matrix: hub CPU normal, entities recover (BE-28).
9. Remote sleep/wake: no pushes during standby, exactly one poller after wake, state resynced.
10. Restart the driver with the matrix off, then power the matrix on: correct state throughout.
11. Preset buttons and remote commands show real preset names; profile and scene commands run and report errors.
12. Matrix power switch follows a front-panel power change.
13. 24 h Remote battery drain with and without the integration, before and after changed-only updates.
14. Existing activities keep working after any entity-model migration.

## 10. Sources

- ucapi library: <https://github.com/unfoldedcircle/integration-python-library> (CHANGELOG, releases)
- Integration API spec: <https://github.com/unfoldedcircle/core-api> (integration-api, entity docs, driver registration)
- Reference integrations: <https://github.com/unfoldedcircle/integration-denonavr>, <https://github.com/unfoldedcircle/integration-androidtv>, <https://github.com/unfoldedcircle/integration-appletv>
