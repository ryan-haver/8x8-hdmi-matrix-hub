# Runtime integration contract (R0)

Status: implementation contract for coordinator review, not runtime completion.
Inspected base: `6debe5a9d1ce3b5993bbd1f6c16d14550d11141b`, 2026-10-18.
Scope: [next development phases](NEXT_DEVELOPMENT_PHASES.md) R1–R6 under the
[unified plan](UNIFIED_MASTER_PLAN.md). R0 changes this document only.

The signatures below are **target interfaces**, except where explicitly marked
current. They freeze the boundaries needed for concurrent work. Passing existing
framework tests does not prove the shipped application uses those interfaces.
No release, baseline, hardware acceptance, registry or ledger approval is implied.

## 1. Source findings that change the implementation briefs

| Inspected source | Current behavior and required consequence |
| --- | --- |
| `run.py`: `main`, `run_core`, `run_uc_driver` | Core constructs `OreiMatrix`, calls `set_matrix_device`, starts REST, then connects. UC uses `runpy` to execute `src/driver.py`, which owns another startup architecture. Replace the mode fork with one asynchronous composition root; preserve CLI, healthcheck, environment aliases and health-before-connect. |
| `src/driver.py`: `restore_from_config`, setup handlers, `main`, lifecycle handlers | This is the working `ucapi.IntegrationAPI.init(metadata, setup_handler)` server/setup bridge. It registers eight Remote lifecycle listeners, converts entities, restores credentials/configuration, publishes attributes/device states, and handles setup authorization. Its poller and global matrix cannot be started alongside the new runtime. Keep the file unchanged as a reference until the coordinator decides its retirement. |
| `src/hub/integrations/unfolded_circle/__init__.py` | `start` builds dict descriptions, appends diffs to `pushed_updates`, subscribes and announces mDNS. It never starts a UC server or sends those diffs to a Remote. It also has no `routes()` although `IntegrationLoader.routes()` calls it. R3 owns the actual bridge, not merely a loader registration. |
| `src/hub/core/matrix_service.py`, `event_bus.py` | `MatrixService` owns cached state and publishes core `HubEvent(topic, data, timestamp)`; it has no lifetime refresh loop or raw matrix-event subscription. `EventBus.publish` only shallow-copies data and `drain` has no shutdown deadline. R1 must own lifecycle, immutable delivery and refresh scheduling. |
| `src/hub/integrations/hub_client.py`, `hub_client_local.py` | Integration snapshots are `HubSnapshot` dataclasses and events are a different `HubEvent(kind, data)`. Local client expects a callable `power(on)` and typed snapshots. Passing `MatrixService` directly fails: its `power` is a property, its snapshot is a dict, and it has no `send_cec` with the expected signature. UC currently rejects non-dict snapshots and does not consume typed events correctly. Explicit adapters are required on both sides. |
| `src/rest_api/app.py`, `utils.py`, `events.py` | `set_matrix_device` constructs managers; `create_rest_app` constructs another unified scene manager and initializes stores. `EventStream` owns `hub_status_poller`, follows raw matrix events and publishes WS changes. Merely adding a service poller duplicates reads/publishers. R1 owns all these seams, including the package wrapper in `rest_api/__init__.py`. |
| `src/hub/domain/action_runner.py`, REST action handlers | Runner already supports five kinds, but REST executes managers directly. Its normalized result is not the existing public response. `from_runtime()` gets the legacy scene manager from REST globals, whereas v2 needs `scene_manager.SceneManager`. Inject the correct managers explicitly and translate results at each surface. |
| `src/hub/persistence/migrations.py`, real readers | Registry covers `scenes_v2.json`; both `config.SceneManager` and `scene_manager.SceneManager` currently read/write `scenes.json`. Runtime shortcut filename is `system_shortcuts.json`, registry canonical name is `shortcuts.json`. Constructor reads and PIN rehash writes happen before any migration barrier today. |
| Same migration module | Backup failure does not prevent migration writes; unsupported reads can return the future payload; saves can overwrite it. Flat-map migration can drop non-mapping unknown values. Returning `unreadable` is insufficient if a manager subsequently seeds/saves defaults. R2 must enforce the boundary end to end. |
| `src/rest_api/integrations.py`, Flic package, loader | REST eagerly imports Flic and owns a default singleton; Flic config defaults enabled, generic registry filters unset flags out. Its registry would count `schema_version` as a button. R5 removes the duplicate active instance and honors explicit disable without changing the unset default. |
| HA package; `tools/validate/clients/__init__.py` | HA discovery exists but has no startup call. Flic validation is an `UnimplementedClient`, not V3 evidence. R5 wires optional discovery; R6 implements a distinct exact-request replay client. |
| Flic drawer `updateFlicOutput`; REST route table | The generated all-output action is `POST /api/input/{n}`, but that route is absent. The supported all-output route is `POST /api/switch` with JSON `{"input": n}`. R6 must expose this real template defect; a coordinator-owned template correction and subsequent exact replay are required before that action can pass. |

## 2. Compatibility decisions

### Flags and import boundaries

Normalize the environment once in `run.py`, retaining canonical-over-alias
precedence and existing warning behavior. Pass a **private effective mapping** to
the loader; do not mutate global flags to hide behavior differences.

| Setting | Unset or blank | Explicit values |
| --- | --- | --- |
| `UC_ENABLED` | false | Existing true spellings enable; false disables. No UC package/`ucapi` import or UC listener when false. |
| `HA_DISCOVERY_ENABLED` | false | Enable only existing true spellings. False/unset imports no HA discovery package or Zeroconf dependency for HA. |
| `FLIC_ENABLED` | **true** | `false`, `0`, `no`, `off`, case-insensitive after trimming, disable. Preserve Flic config's existing permissive behavior for other nonblank values; warn on an unrecognized spelling. |

The wiring module maps effective Flic enablement to `"true"`/`"false"` before
passing it to the generic opt-in loader. Do not globally change the loader's
default to enabled. Explicit Flic disable removes only its registration/list
routes and registry lifecycle, not core HTTP actions that Flic can also invoke.
No process-wide assertion that Zeroconf is absent is valid if UC mDNS is enabled;
assert absence per disabled integration. HA manual custom-component installation
and ordinary REST access remain usable with discovery off or failed.

### Matrix address and configuration paths

Resolve before the first connect, without importing UC when disabled:

| Mode | Address precedence |
| --- | --- |
| UC off | Explicit canonical/aliased `MATRIX_HOST` with configured `MATRIX_PORT`; otherwise valid saved `config_state.json` host/port; otherwise `192.168.0.100` with configured/default port. |
| UC on | Valid saved Remote setup host/port/credentials; otherwise explicit environment host/port as an unsaved bootstrap; otherwise **unconfigured**, serving REST health/UI and the Remote setup server without connecting to a default address. |

Preserve saved Telnet port when using that saved address; otherwise use
`OREI_TELNET_PORT`, then 23. Preserve matrix credentials only for the address they
belong to. UC restore uses saved `user`/`password` where present; an environment
bootstrap uses the matrix client's normal credential environment. Core-only
saved-address fallback currently does not load saved credentials: retain that
behavior for this refactor and test it, rather than silently expanding secret use.

`UC_CONFIG_HOME` is authoritative for Remote state; explicit `DATA_DIR` is exported
through existing aliases and supplies the default UC home, **not `DATA_DIR/uc`**.
The modular UC config's current `/uc` fallback must not move a shipped install.
Without either, `run.py` uses project `config` for configuration. Data stores use
existing resolution after export: `MATRIX_DATA_DIR`, else `UC_CONFIG_HOME/data`,
else project `data`. Preserve separate config/data directories; do not flatten an
installation because the Docker defaults happen to make them equal.

Successful authorized Remote setup persists `config_state.json` atomically and
takes effect immediately for every surface; it wins on the next UC startup too.
REST matrix-host changes remain transient, with their current validation and
response contract; do not silently make them permanent Remote setup. A later
restart still follows the table. R1 provides the sole serialized reconfiguration
operation, and R3 translates setup requests/results to it. Same-address
reconfigure retains the working login; a different address requires its own
login, never forwarding the old one. Preserve the address page, credential page,
abort, authorization token/current-password checks, error categories, saved
names and subscribed IDs from `tests/uc/test_setup.py`.

Do not run `migrate_legacy_config_state()` as currently written during UC start:
it unlinks `config_state.json`, breaking core fallback/restart readers. R3 changes
it to non-destructive import; accept `.migrated` only when the primary is absent,
never overwrite either conflicting file, and keep the supported primary filename.

### Public contracts and action results

Keep the security middleware order, origin checks, API keys/header and query
forms, admin/control separation, rate limiting and public reads. Loading an
integration does not create a privileged HTTP bypass. Internal UC calls still
enforce item passcodes/lockouts; a caller cannot self-assert `allow_remote` to
bypass a protected profile. Never include credentials or passcode hashes in
snapshots, errors, logs or replay artifacts.

`ActionRunResult` is internal. Preserve current wire envelopes and error order:

| Existing route family / source | Required projection |
| --- | --- |
| Profile recall (`profiles.handle_recall_profile`) | 200 all applied, 207 partial, 500 none; `data.profile`, `applied`, `failed_outputs`, `errors` (null on success), `power_on_macro`, joined top-level error. Preserve 503 preconditions and 400/404 input/target errors. |
| Legacy scene recall (`scenes.handle_recall_scene`) | Execute the **profile** kind once and retain the alias's key renaming and headers. It is not a unified v2 scene. |
| V2 scene execute (`scenes_v2.handle_execute_scene`) | Existing `ExecutionResult.to_dict()` payload with 200/207/500, existing PIN error data and headers. Keep resolved overrides, step ordering, waits, missing references and cancellation semantics. |
| Macro execute (`macros.handle_execute_macro`) | Existing 200 + manager result on success; 500 + existing error envelope on failure, even if internal steps were partial. Retain timeout validation/default. `handle_test_macro` remains validation-only. |
| Shortcut execute (`system_shortcuts.handle_execute_shortcut`) | 200 or 500 + existing result data; disabled 400, absent 404. Do not replace its detailed per-output result with a generic runner blob. |
| Preset recall (`control.handle_preset`) | Existing 200 data with preset/name/message; 400 invalid slot (even if runner uses 404), 500 refusal, 503 disconnected. Preset save remains its existing save/temporary-route/restore transaction, not a recall action. |

Missing/wrong item passcode remains 403; lockout remains 429 with `Retry-After`
and existing error data. Share the existing tracker keys across REST and UC.
Check execution authorization once: the runner owns the execution check; route
CRUD PIN checks remain. Fix the runner's scene path so it does not perform a
second blocking PBKDF2 check in `SceneExecutor`; use the established verified
manager-view pattern, with no externally supplied bypass flag. A failing
power-on macro does not silently prevent the profile's existing best-effort
output application. Cancellation must propagate, never become success or cause
an automatic retry of a partially executed action.

## 3. Target composition and frozen interfaces

### Modules and signatures

Names in this section define imports between tracks. New dataclasses/protocols
may be placed only in their assigned module; do not create parallel competing
factories. Use `TYPE_CHECKING` or structural protocols for cross-track annotations
so R3 can be tested without importing R1's unfinished modules.

```python
# R2: hub.persistence.startup (new)
@dataclass(frozen=True)
class PersistencePaths:
    config_dir: Path
    data_dir: Path

@dataclass(frozen=True)
class PreparedPersistence:
    paths: PersistencePaths
    results: tuple[MigrationResult, ...]  # actual paths, no alias-key collision

def prepare_runtime_storage(*, config_dir: Path, data_dir: Path) -> PreparedPersistence: ...
# Raises MigrationError for unsafe data/backup/write failures before manager construction.

# R1: hub.runtime.config (new; no optional integration imports)
@dataclass(frozen=True)
class MatrixAddress:
    host: str
    port: int = 443
    telnet_port: int | None = None
    user: str | None = None
    password: str | None = field(default=None, repr=False)

def resolve_matrix_address(settings: Settings) -> MatrixAddress | None: ...

# R1: hub.runtime.managers (new)
@dataclass
class RuntimeManagers:
    profiles: ProfileManager
    scenes: SceneManager  # scene_manager.SceneManager, NOT config.SceneManager
    macros: MacroManager
    shortcuts: SystemShortcutManager
    dashboard: DashboardLayoutManager

def create_managers(prepared: PreparedPersistence) -> RuntimeManagers: ...

# R1: hub.runtime.composition (new)
def build_runtime(settings: Settings, *, environ: Mapping[str, str],
                  matrix_factory: Callable[..., OreiMatrix] = OreiMatrix) -> HubRuntime: ...

class HubRuntime:
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    def snapshot(self) -> HubSnapshot: ...
    def subscribe(self, callback: Callable[[HubEvent], Any]) -> Callable[[], None]: ...
    def notify_catalog_changed(self) -> None: ...
    async def refresh(self) -> None: ...
    async def reconfigure(self, address: MatrixAddress, *,
                          persist: bool = False) -> ReconfigureResult: ...
    async def run_action(self, kind: str, action_id: str, *,
                         passcode: str | None = None,
                         params: dict[str, Any] | None = None) -> ActionRunResult: ...

# ReconfigureResult in runtime.config: success: bool, error_kind: str | None,
# connected: bool; error_kind is auth/timeout/not_found/refused/other, no secrets.
# HubEvent here means hub.integrations.hub_client.HubEvent.

# R1: hub.runtime.integrations (new; transferred to R5 after acceptance)
def build_integration_loader(environ: Mapping[str, str]) -> IntegrationLoader: ...
def bind_integrations(loader: IntegrationLoader, runtime: HubRuntime) -> None: ...

# R3: unfolded_circle integration (new keyword dependency, old constructor retained)
class UnfoldedCircleIntegration:
    def __init__(self, config: UCIntegrationConfig | None = None, *,
                 mdns_publisher=None, include_select=True,
                 include_legacy_sensors=False, api_factory=None) -> None: ...
    def bind_runtime(self, *, reconfigure: Callable[..., Awaitable[Any]],
                     current_address: Callable[[], Any],
                     driver_metadata: Path) -> None: ...
    async def start(self, hub: HubClient) -> None: ...
    async def stop(self) -> None: ...
    def routes(self) -> list[Any]: ...  # [] for the separate ucapi server

# R1: rest_api.app (old callers remain valid)
def create_rest_app(data_dir: Path | None = None, *,
                    runtime: HubRuntime | None = None,
                    integration_routes: Sequence[tuple[str, str, Callable]] | None = None
                    ) -> web.Application: ...
class RestApiServer:
    def __init__(self, host="0.0.0.0", port=8080, *, data_dir=None,
                 runtime=None, integration_routes=None) -> None: ...

# R1: rest_api.utils
def bind_runtime(runtime: HubRuntime) -> None: ...
def get_action_runner() -> ActionRunner: ...
def get_hub_client() -> HubClient: ...
# Keep set_matrix_device signature for legacy/tests; runtime binding injects
# existing managers without invoking their constructors a second time.
```

`build_runtime` resolves paths/address, calls R2's barrier, then constructs
managers. It creates one `EventBus`, one `MatrixService`, one stable matrix
compatibility facade, one `ActionRunner`, one `HubClientLocal` and one loader.
An unconfigured UC runtime uses a disconnected/null client until setup, not a
real default-address connection. The stable facade delegates to the current
service/client so replacing a device never leaves managers with stale references.

Use current constructors explicitly:

```python
service = MatrixService(client, model=model, names=names, bus=bus)
runner = ActionRunner(matrix_facade,
    profile_manager=managers.profiles, scene_manager=managers.scenes,
    macro_manager=managers.macros, shortcut_manager=managers.shortcuts,
    preset_executor=service)
local = HubClientLocal(command_provider,
    snapshot_provider=runtime.snapshot,
    action_runner=run_action_envelope,
    event_subscribe=runtime.subscribe)
loader = IntegrationLoader(registry, effective_environ)
```

Current `IntegrationRegistry.register(name, env_flag, "module:Class")`,
`load()`, `start(hub)`, `routes()`, `health_summary()`, `stop()` stay compatible.
R1 registers import strings, calls `load`, binds UC hooks, and mounts returned
`(method, path, handler)` tuples before aiohttp freezes its router. R5 finishes
flag/lifecycle behavior without requiring a new generic factory protocol.

R1's `command_provider` (in `hub/runtime/adapters.py`) has `snapshot()` returning
`HubSnapshot`, `switch(input_num, output_num=None)`, `power(on)`,
`send_cec(target_kind, port, command)`, `recall_preset(preset)`,
`save_preset(preset)` and `cycle_input(direction, output_num=1)`, all commands
async returning bool. It translates to service `set_power`, `switch`, etc.; CEC
uses the same underlying client's existing target-aware protocol implementation.
Cycle uses one per-output lock shared by REST and UC, not separate read/modify
locks in two front ends. Macro sender is bound once to this provider's `send_cec`.
`run_action_envelope(kind, action_id, *, passcode=None)` returns the existing
`success/data/error` mapping expected by `HubClientLocal`, including safe result
details/status for UC translation. R4 owns its final compatibility projection in
new `hub/runtime/actions.py`, initially created by R1.

The matrix facade preserves the legacy `OreiMatrix` method surface required by
profile/scene/shortcut executors and REST. Known state-changing operations enter
`MatrixService`; other protocol operations delegate to the **same client** and
schedule the one service refresh. Never let a facade call back into its own
runner (preset recursion) or create a second transport. Settings uses
`runtime.reconfigure`, not facade property assignment/disconnect/connect. R1
adds an explicit service client-replacement/reset seam if needed; its ownership
includes `matrix_service.py`. A transaction/generation guard prevents a read
from an old client from overwriting the new state.

### Startup sequence through run.py

1. Parse/export settings and aliases; retain `healthcheck` without building the
   runtime. Validate directories and acquire any existing process-lifetime
   exclusion required by UC startup, without importing/running legacy driver.
2. Resolve the address and actual storage paths. Prepare all relevant persisted
   files before constructing managers, creating REST stores, or loading Flic.
   Fatal migration errors stop startup with a useful path/schema diagnostic;
   an unreachable matrix is a separate nonfatal condition.
3. Construct shared objects and attach a single raw-event listener group that
   requests coalesced service refreshes. No legacy UC polling loop starts.
4. Load enabled integrations, bind UC runtime hooks, build REST with injected
   managers/client/routes, and start REST health/UI first. Preserve default
   8080, configured port and `/ui`, `/kiosk`, `/ws` behavior. Starting REST must
   not synchronously wait for matrix login or full snapshot.
5. Start integrations once against the same local client; UC listens on its
   configured port (9095 default), with metadata/driver URL/setup handler and
   listeners installed before mDNS advertises it. HA advertises the actual REST
   port only after REST is listening. Flic loads one registry instance.
6. Schedule one initial connect and one supervised refresh worker. Client-owned
   transport reconnect remains the reconnect authority; the runtime does not
   implement a competing retry loop. Honor existing polling configuration
   (`STATUS_POLL_INTERVAL`; UC's `POLLING_INTERVAL` as its fallback when unset).
   Remote connect/disconnect/standby never starts/stops the shared matrix.
7. Wait on the stop event; exceptions/cancellation unwind registered resources.
   `main` uses this path for both UC modes, never `runpy` plus another runtime.

Initial R1 isolated tests may stub the frozen R2 barrier and R3 integration
factory; that proves only its composition. Its completion report must say so.
After the parallel wave is accepted, coordinator reruns real `run.py` with all
three tracks and no factory/migration substitutes before R4/R5 acceptance.

### State, refresh, events and shutdown

R1 owns service-to-`HubSnapshot` projection: omit unknown port values, maintain
one-based integers internally, include redacted profile/v2-scene/macro/shortcut
catalogs and effective preset visibility/names. Core `power`/`names`/`signal`
payloads must be translated to integration `on`/`input_names`/`input_signals`,
not passed through based on matching topic names. R3 maps typed snapshots/events
to its projector dictionary shape and recognizes actual protection fields such
as `password_protected`, not just its current mock `has_pin` convention.

`runtime.snapshot()` is an in-memory copy, not a fresh hardware poll.
`runtime.subscribe` wraps the core bus with typed immutable event copies;
`HubClientLocal` alone projects its initial snapshot and subsequent diffs for
integration subscribers. Its command-triggered refresh reads this memory, not
the device. Catalog/settings changes must invalidate and republish catalogs as
well as matrix state: `notify_catalog_changed()` emits a typed `catalog` event
with redacted `profiles`, `scenes`, `macros`, `shortcuts` lists. R4 makes the
local client's event path forward this event (its current eight-topic projector
omits catalogs); R3 accepts it to rebuild available entities without losing
subscriptions. R4 calls the hook at affected CRUD/action sites; R1 bridges
existing device-settings notifications, R5 handles registry notifications.
Subscribing during a write must not
miss a change or deliver a stale initial snapshot after a newer event.

`rest_api.events.EventStream` retains its WS queues/backpressure/wire formatting
but in runtime mode becomes a consumer of this shared state. Its `refresh` and
`request_poll` delegate to the runtime; its independent raw poller/listeners are
off. R1 must preserve raw fields used by REST status/full and WS port details,
either in a service-owned read cache or a lossless projection; the current
service's smaller snapshot is not sufficient to drop scaler/HDCP/HDR/audio or
connection diagnostics. REST reads may request refresh but do not publish a
second state change. Direct protocol diagnostic reads can still use the sole
client. Existing non-runtime test compatibility mode may retain the old stream.

Preserve WS `connected` then `status`, later change events, first-known-value
snapshot behavior, reconnect resync, client queue limits, and
`docs/api/websocket.schema.json`. Translate service preset notifications once;
remove the duplicate success announcement at REST recall when R4 takes it over.
Command failures/CEC acknowledgments are distinct existing event contracts, not
state changes to discard. Async consumers must not share mutable nested maps.

Reconfiguration is serialized with commands and refreshes: stop old refresh/
connect work, close the old active transport before connecting a replacement,
reset service state, then rebind through stable facades. A setup address probe
may open a short-lived unauthenticated reachability socket; it is not a second
matrix poller/session. On failed setup, close the candidate and restore the old
address/session and saved configuration; never leave a candidate reconnect task.
On success, persist before reporting setup complete. Aborts and save failures
also roll back. No more than one active matrix transport owner exists; tests
must measure this through failed/repeated setup, not just normal startup.

Shutdown order: mark stopping and reject new mutations; stop listener ingress
and reverse-stop integrations (HA, Flic, UC for registration UC/Flic/HA), including
mDNS and UC command tasks; cancel/await in-flight actions with a bounded cleanup
window (preset temporary-route restoration included); cancel/await startup,
refresh and reconfiguration tasks; unsubscribe REST/raw listeners and close WS
queues/server; close the local client's callback tasks; disconnect the service
and client reconnect/Telnet tasks; drain/cancel remaining bus deliveries with a
deadline; release process locks/temp metadata. Each phase runs in `finally`
even after another cleanup fails. Stop is idempotent, also after a partially
started REST runner or a cancelled integration start. No blanket cancellation
of all process tasks or swallowed `CancelledError` is an acceptance substitute.

## 4. Persistence contract and migration inventory

R2 owns preparation and safe readers/writers, including old direct constructors.
Use the existing atomic file writer, preserve original bytes before conversion,
and do not bump release versions or `CURRENT_SCHEMA_VERSION` merely to wire it.

| File/path | Reader and target decision |
| --- | --- |
| Config directory `profiles.json`, `cec_macros.json` | `config.ProfileManager`, `cec_macros.MacroManager`; prepare before constructor; preserve PIN hashes, macro steps/targets, output settings, unknown keys. |
| Config directory legacy `scenes.json` | Profile migration source only when demonstrably legacy output-state scenes and `profiles.json` absent. Never reinterpret a unified scene's steps as a profile or overwrite an existing profile catalog. Legacy scene HTTP routes already alias profiles. |
| Data directory `scenes.json` / `scenes_v2.json` | `scene_manager.SceneManager` uses `scenes_v2.json` as target. Import recognized unified `scenes.json` data non-destructively with backup before the reader switches. If both exist, preserve both: use canonical only if legacy content is already represented; conflicting IDs/content or ambiguous/mixed shapes fail with a diagnostic rather than pick/merge silently. Empty scenes may initialize empty without deleting source. This fixes the current two-writer filename collision. |
| Data directory `system_shortcuts.json` / `shortcuts.json` | Keep the shipped manager filename `system_shortcuts.json` for compatibility. Registry alias resolves its schema, not a destructive rename. If only `shortcuts.json` exists, copy/import safely to the shipped filename; if both differ, block rather than hide one. |
| Data directory `dashboard_layout.json`, `device_settings.json` | Existing layout manager and settings initializer; migrate before any default seeding or PIN-related startup writes. Preserve favorites, pinned/dashboard fields, ordering and per-port settings. |
| Data directory `flic_buttons.json` | R2 prepares format; R5 adapts reader/saver. Flat map skips `schema_version` for listing/counting/updating and preserves unknown metadata on save. |
| UC home `config_state.json` and `.migrated` | R1 reads without optional imports, R3 owns setup/import writes. Not a generic catalog migration; retain address-bound secrets and primary filename. |
| Themes/UI/security configuration | Preserve existing paths and contracts; do not sweep unrelated files into schema migration. Existing legacy-copy behavior remains, without treating corrupt input as empty valid state. |

Preparation processes resolved config/data paths once each, including legacy
copy locations from `persistence.get_legacy_data_paths`, and records results by
actual path. Do not let the current `migrate_all_data_files` alias dictionary
collapse two distinct conflicting files into one reported success.

Missing files permit defaults. Future schema, corrupt JSON, invalid known record
shapes, unreadable source, backup failure, and failed atomic replacement block
the affected manager's writes and fail runtime preparation. Returning defaults
then overwriting is forbidden. Standalone manager calls must also refuse a save
over such files. Retain unknown top-level and record fields through load/edit/
save, including scalar extension metadata in flat maps; don't invent records
from it. Existing valid target files win over legacy *locations*; do not overwrite
them because an older copy exists. The existing explicit corrupt-target recovery
from a valid legacy copy must retain its backup and be tested; it is not license
for automatic rollback from arbitrary backups. Never delete backups or downgrade
a future schema. Repeat startup must produce no further migration/write churn.

The profile fallback and unified-scene import need shape fixtures from real
serializers, not just the migration module's illustrative bare lists. Ambiguous
operator data is an actionable runtime error, not a design question requiring
new user approval for implementation. Unexpected shape conflicts found in tests
go to the coordinator with preserved fixture bytes.

## 5. Disjoint ownership and acceptance graph

All source paths below are literal repository paths. New paths are marked
`(new)`. Test paths in each **owned tests** row belong only to that worker;
existing regression paths are read/run-only unless explicitly assigned. No
worker edits shared `tests/conftest.py`, simulator fixtures, registry, ledger,
OpenAPI, baselines, version metadata, Dockerfiles, dependencies or legacy driver.
Request a coordinator-owned change if one proves necessary. No push/merge/tag.

```text
R0 accepted -> R1, R2, R3, R6 concurrently (four disjoint checkouts)
R1 + R2 + R3 accepted and integrated -> R4 and R5 concurrently on that base
R4 + R5 + R6 integrated -> coordinator shipped-image/client gates -> R7 -> R8
R6 replay reruns after R4/R5; physical Remote/Flic and 72-hour soak remain V.
```

An acceptance arrow includes review and integration, not merely a worker's
commit. R1's parallel-wave startup proofs are provisional until R2/R3 are linked.
Coordinator records each ownership transfer in the dispatch; no overlapping
edits are authorized by a general directory assignment.

### R1 — core composition brief

**Target files:** `run.py`; new `src/hub/runtime/__init__.py`, `config.py`,
`composition.py`, `managers.py`, `adapters.py`, `actions.py`, `integrations.py`
under `src/hub/runtime/`; `src/hub/core/matrix_service.py`,
`src/hub/core/event_bus.py`; `src/rest_api/app.py`, `src/rest_api/__init__.py`,
`src/rest_api/utils.py`, `src/rest_api/events.py`, `src/rest_api/core.py`,
`src/rest_api/settings.py`. This is a closed list, not ownership of every file
under either package.

**Owned tests:** new `tests/test_runtime_composition_r1.py`,
`tests/test_runtime_state_bridge_r1.py`, `tests/test_runtime_shutdown_r1.py`;
existing `tests/test_run_entry.py` for entry-point expectation changes only.

**Change:** implement section 3, including the package-level REST wrapper,
runtime-aware settings/reconfigure path, one manager bundle, snapshot adapter,
one refresh worker, bounded rollback/stop, integration route injection, lazy
imports, and health-before-connect. Keep `set_matrix_device` usable for existing
direct tests. Add integration health via an additive field on existing health
data, with the provider installed now so R5 need not edit `core.py` later.

**No touch:** R2 readers/migrations, R3 UC implementation, R4 action handlers,
R5 integration implementations/base, low-level transport and coordinator files.
Use R2's frozen `prepare_runtime_storage` contract; do not create a second
migration implementation or a production fallback that skips it.

**Observable acceptance:** new tests plus targeted
`tests/test_run_entry.py`, `tests/test_health.py`,
`tests/test_hub_core_matrix_service.py`, `tests/test_hub_events.py`,
`tests/sim/test_sim_ws_contract.py`, `tests/test_security_ssrf_tls.py`.
Use real subprocess `run.py` for both modes after integration: count transport,
connect, refresh tasks and events; mutate simulator/front panel and observe REST
and UC; disconnect/reconnect; SIGTERM; bind failure and cancellation at each
startup phase; repeated REST/UC reconfigure with no stale writes/tasks.
Coordinator later builds the shipped image and proves ports/health/volume paths
and bounded SIGTERM under the same cases. A mocked `build_runtime` test alone
does not accept this track.

**Transfers after acceptance:** `hub/runtime/actions.py` to R4;
`hub/runtime/integrations.py` and `rest_api/app.py` to R5. All other R1 files
remain frozen while R4/R5 run; fixes return through a serialized R1 follow-up.

### R2 — persistence and readers brief

**Target files:** `src/hub/persistence/__init__.py`, `migrations.py`, new
`startup.py` in that package; `src/persistence.py`, `src/config.py`,
`src/scene_manager.py`, `src/cec_macros.py`, `src/system_shortcuts.py`,
`src/dashboard_layout.py`, `src/rest_api/device_settings.py`. Only storage,
reader/serialization and path-selection portions of manager/REST modules.

**Owned tests:** new `tests/test_runtime_persistence_r2.py`,
`tests/test_runtime_persistence_readers_r2.py`, fixtures only under new
`tests/fixtures/runtime_persistence_r2/`. Existing
`tests/test_hub_persistence_openapi_env.py` is coordinator-owned because it mixes
registry/OpenAPI/environment expectations; send required expectation changes.

**Change:** implement the barrier and inventory in section 4; retain metadata
on save; prevent invalid/future input from entering default-seeding writers;
resolve scene filename/shape collisions; keep aliases/backups/restarts safe.
Do not construct Flic as part of preparation. Preserve existing constructor
arguments so R1 can bind managers without changing this track's files.

**No touch:** runtime composition, REST mounting/security/action code, UC setup
state, Flic reader, shared test fixtures/registry. No execution policy changes
inside `MacroManager`/`execute_shortcut` or PIN algorithms under storage work.

**Observable acceptance:** new tests plus `tests/test_persistence.py`,
`tests/test_atomic_writes.py`, `tests/test_config.py`,
`tests/test_scene_manager.py`, `tests/test_cec_macros.py`,
`tests/test_system_shortcuts.py`, `tests/test_dashboard_layout.py`,
`tests/test_device_settings_presets.py`, and the persistence cases in
`tests/test_hub_persistence_openapi_env.py`. Construct each actual manager after
preparation, edit/save/reload and compare records plus unknown fields. Inject
backup/replace failures; assert unchanged originals and no manager writes.
Coordinator later seeds an old-version mounted volume, starts the shipped image
twice, reads all catalogs through REST/UC, and checks original bytes/backups,
retained PIN behavior and restart idempotence. A successful migration return is
not sufficient evidence. No ownership transfer to R4/R5; R5 calls these helpers.

### R3 — working UC server and adapter brief

**Target files:** `src/hub/integrations/unfolded_circle/__init__.py`, `config.py`,
`entities.py`, `handlers.py`, `mdns.py`, `migration.py`, `state.py`; new `bridge.py`
and `setup.py` inside that package. Only this package.

**Owned tests:** new `tests/test_runtime_uc_bridge_r3.py`,
`tests/test_runtime_uc_setup_r3.py`, `tests/test_runtime_uc_client_r3.py`;
existing `tests/test_hub_uc_integration.py` for replacing dict-only assumptions
and destructive-migration expectations, with explicit compatibility assertions.

**Change:** satisfy loader lifecycle, consume the real `HubClientLocal` contract,
instantiate `ucapi.IntegrationAPI` on the running loop, initialize real metadata
and setup handler, convert dict descriptions into actual ucapi entities, attach
command handlers, implement available/configured entity subscriptions and push
device/attribute updates. Port working setup/auth/reconfigure behavior from
legacy driver through the injected runtime hook. Keep no independent matrix
client/poller; don't import driver for its globals. Preserve approved IDs and
CEC target-specific command behavior, standby and names/preset metadata.
Do not mark every entity configured simply because it is available. Replace
unbounded `pushed_updates` accumulation with actual delivery/bounded diagnostic
state. Advertise mDNS only after listening and clean up both on partial failure.

**No touch:** `run.py`, runtime/base/client modules, persistence catalogs,
`src/driver.py`, `driver.json`, dependency versions or UC golden baselines.
Use `bind_runtime` with structural fake hooks in isolated tests; no R1 imports
required for those tests. Keep protected actions on runner checks even when the
projector filters them out of the UI.

**Observable acceptance:** new tests plus `tests/test_hub_uc_integration.py`,
`tests/uc/test_handshake.py`, `tests/uc/test_setup.py`,
`tests/uc/test_commands.py`, `tests/uc/test_entities.py`,
`tests/uc/test_state_sync.py`, `tests/uc/test_lifecycle.py`. The existing
`tests/uc/conftest.py` launches `run.py` via `HubProcess`; after integration this
must reach the modular runtime, verified in logs/trace, not silently the old
driver. Exercise blank setup, saved setup, wrong credentials, abort, changed
address, restart, subscribe/unsubscribe and standby while REST keeps working.
Assert actual simulator commands and Remote readback; `start()` returning and
`health()['running']` are not Remote proof. Coordinator repeats through the built
UC-enabled image; physical Remote 3 verification remains pending V4. Existing
74-entity fixture assertions are not silently weakened to accommodate new
entities: send any intentional catalog delta for coordinator review.

### R4 — shared execution and call-site parity brief

**Target files:** `src/hub/domain/action_runner.py`,
`src/hub/integrations/hub_client_local.py`; transferred
`src/hub/runtime/actions.py`; `src/rest_api/profiles.py`, `scenes.py`,
`scenes_v2.py`, `macros.py`, `system_shortcuts.py`, `control.py`, `cec.py` under
`src/rest_api/`; `src/scene_execution.py` only for executor authorization/
cancellation integration. No persistence-reader ownership transfers.

**Owned tests:** new `tests/test_runtime_action_parity_r4.py`,
`tests/test_runtime_action_wire_r4.py`, `tests/test_runtime_action_cancel_r4.py`;
existing `tests/test_hub_domain_action_runner.py` for runner corrections.

**Change:** route profile/legacy-scene/v2-scene/macro/shortcut/preset recall
through one runner and section 2 projections. Make local preset recall use that
same runner without recursive provider calls. Use shared direct-command provider
for switch/all/output-source, power, cycle and CEC; these remain matrix protocol
operations, not new domain action kinds. Preset custom save/restore stays a
single serialized operation and restores on cancellation. Remove duplicate
success events, retain existing failure/CEC event contracts and notify catalog
changes without adding another publisher.

Precise write seams: `profiles.handle_recall_profile`,
`scenes.handle_recall_scene`, `scenes_v2.handle_execute_scene`,
`macros.handle_execute_macro`, `system_shortcuts.handle_execute_shortcut`,
`control.handle_preset`, `handle_preset_save`, `handle_switch` (including its
all-output branch), `handle_output_source`, `handle_input_next`,
`handle_input_previous`, `handle_power_on`, `handle_power_off`; CEC target
handlers `handle_cec_input`, `handle_cec_output`, `handle_cec_enable`,
`handle_cec_enable_input`, `handle_cec_enable_output` in `cec.py`.
Other direct writes in `outputs.py`, `audio.py`, `system.py`, and rename
handlers in `core.py` use the R1 matrix facade; leave those files frozen and
report any discovered bypass to R1/coordinator for a sequential fix.

**No touch:** R1 composition/app/utils/events, R2 serialization,
R3 entity/setup code, R5 lifecycle files, security middleware/password module,
shared route/schema artifacts. Never normalize public bodies by returning
`ActionRunResult.to_dict()` everywhere. Update execution-log behavior through
existing manager APIs; do not drop it in the refactor.

**Observable acceptance:** new tests plus `tests/test_hub_domain_action_runner.py`,
`tests/test_profiles_scenes_pins.py`, `tests/test_scene_execution.py`,
`tests/test_security_access_and_guards.py`, `tests/test_hub_integrations_framework.py`,
`tests/sim/test_sim_profiles.py`, `tests/sim/test_sim_profile_followups.py`,
`tests/sim/test_sim_scenes_v2.py`, `tests/sim/test_sim_shortcuts.py`,
`tests/sim/test_sim_preset_save.py`. Compare exact old/new HTTP status, headers
and body for success/refusal/partial/missing/timeout, and ordered simulator
commands for REST versus UC. Count PIN attempts across both surfaces, verify
event-loop responsiveness and no duplicate macros/preset commands. Later run
the same paths through the shipped image and dedicated UC/Flic clients; report
route inventory deltas to the coordinator for registration/ledger updates.

### R5 — Flic/HA flags and lifecycle brief

**Target files:** `src/hub/integrations/base.py`,
`src/hub/integrations/flic/__init__.py`,
`src/hub/integrations/homeassistant/__init__.py`,
`src/rest_api/integrations.py`; transferred `src/hub/runtime/integrations.py`
and `src/rest_api/app.py`. No general ownership of runtime or REST packages.

**Owned tests:** new `tests/test_runtime_integration_flags_r5.py`,
`tests/test_runtime_integration_lifecycle_r5.py`,
`tests/test_runtime_flic_storage_r5.py`; existing
`tests/test_hub_flic_ha_integrations.py` for lifecycle expectation corrections.

**Change:** apply section 2 flags with one loaded registry and route mount,
remove the eager compatibility import from active app construction, preserve
legacy import symbols for standalone callers without making a second runtime
registry. Adapt Flic versioned readers/savers using R2's safe boundary and skip
schema metadata. Complete restart-safe loader rollback and reverse cleanup,
including cancellation. HA discovery failure reports degraded health on the
existing surface while manual REST/custom-component use remains available;
do not claim a swallowed import/registration error is healthy discovery.

**No touch:** R1 core/utils/settings/events, R3 bridge, R4 handlers/actions,
R2 migrations/readers, HA custom component, shared registry/schema files.
Coordinator owns any manifest/dependency adjustment discovered by testing.

**Observable acceptance:** new tests plus `tests/test_flic_registry.py`,
`tests/test_hub_flic_ha_integrations.py`, `tests/test_hub_integrations_framework.py`,
`tests/test_integrations_adapter.py`; `tests/ha/test_config_flow.py`,
`tests/ha/test_init.py`, `tests/ha/test_api.py` in the dedicated HA environment.
Test all eight UC/Flic/HA boolean combinations, unset/blank defaults and explicit
false spellings, route counts/absence, import traces, one registry, advertisements,
subscriptions, startup failure/cancellation and repeated start/stop. Preserve
Flic auth/body contracts. Coordinator later repeats flags with the shipped image
and proves manual HA installation/control with discovery disabled; mock Zeroconf
alone is not network discovery proof. Registry inventory is per configuration,
not always the historical 177 routes.

### R6 — dedicated Flic replay client brief

**Target files:** new `tools/validate/clients/flic.py` and
`tools/validate/clients/__init__.py` registration only.
**Owned tests:** new `tests/validation/test_flic_replay_r6.py`,
`tests/validation/test_flic_templates_r6.py`,
`tests/validation/test_flic_replay_live_r6.py`; fixtures only under new
`tests/fixtures/flic_replay_r6/`. No production UI/template edits.

**Change:** implement `Client.start(HubInfo)`, `perform(Action) -> ActionResult`,
`stop()`, accurate `intents`/`supports`, and useful `environment()` evidence.
Use its own request builder/transport; sharing low-level HTTP utilities is fine,
subclassing/delegating all intents to `ApiClient` is not Flic replay. Explicit
`NotSupportedError` identifies unsupported intents/observations, never blanket
success. Simulator readback is independent assertion evidence, not a claim a
physical Flic button can display matrix state.

Authoritative templates are `web/js/components/integrations-drawer.js`
`updateFlicOutput`/`updateFlicSdkSnippet`, `web/js/utils/api-copy.js`, and
`docs/FLIC_SETUP.md`. Capture and compare generated requests, not just a second
handwritten table that could drift together with the client:

| UI action | Exact base request |
| --- | --- |
| Hardware preset | `POST /api/preset/{n}`, absent body |
| Profile | `POST /api/profile/{id}/recall`, absent body in the current drawer |
| All outputs to input | `POST /api/input/{n}`, absent body |
| One output source | `POST /api/output/{out}/source`, JSON `{"input": n}` and `Content-Type: application/json` |
| Cycle | `POST /api/input/{next|previous}?output={out}`, absent body |
| Volume | `POST /api/cec/output/{out}/{volume_up|volume_down|mute}`, absent body |
| Matrix power | `POST /api/power/{on|off}`, absent body |
| CEC | `POST /api/cec/{input|output}/{port}/{command}`, absent body; unsupported target/command combinations must assert refusal |
| SDK startup registration | `POST /api/integrations/flic/register`, JSON `{"buttons":[{"name":...,"bdaddr":...,"serial":...}]}` and JSON content type |

The all-output template currently targets an absent route. Preserve an explicit
failing replay/reproduction for the coordinator, rather than silently replacing
the request in this client. Recommended coordinator correction: change the
drawer generator to `POST /api/switch` with the JSON input body, update its
template fixture in an R6 follow-up, and require a passing exact replay before
final acceptance. This does not require adding a new route. The coordinator
owns that isolated UI correction; R6 owns its tests and must distinguish the
old-template defect from unsupported physical-button verification.

The drawer currently emits **no credentials**. Replay those exact keyless forms;
under keyed mode assert their 401 failure. Separately replay documented manual
`X-API-Key` and `?key=` variants (use `&key=` when cycle already has a query),
including missing/wrong/revoked key. Do not silently inject a key and claim the
generated script worked unchanged. The drawer also cannot supply a protected
profile PIN: assert refusal rather than invent a bypass. Any explicitly tested
manual passcode request is labeled separately from generated-template proof.
Redact header/query keys and bodies containing secrets in `ActionResult.requests`
and saved evidence, retaining structure for comparison.

Exercise actual generated SDK callbacks with stubbed `buttons`/`http`: single,
double, hold; Duo left/right; rotation direction; configured button name/address
filter. Assert one request for the matching event, zero for mismatches, and one
startup registration. This distinguishes click replay from generic REST calls.

**No touch:** all hub/runtime/UI code, `tools/validate/runner.py`, stack/device,
scenario registry, `docs/validation/features.yaml`, ledger or reports. Send the
coordinator precise new scenario requirements and supported-intent matrix.

**Observable acceptance:** new tests plus `tests/validation/test_runner.py`,
`tests/validation/test_client_state.py`, `tests/test_flic_registry.py` (read/run
only). Live tests launch the existing simulator/hub stack, perform generated
requests, assert HTTP envelope, simulator state and ordered command-log deltas,
including duplicate/nonmatching gestures, auth failures, disabled registration,
unknown target, matrix refusal and partial profile effects. R6 can prove client
behavior on the existing base independently; final acceptance reruns against
R4/R5's shipped image. Record source SHA/image digest, exact scenario counts and
reasoned skips. HTTP replay does not close physical Flic/network reliability V4.

## 6. Review and integrated evidence gate

Coordinator owns `docs/validation/features.yaml`, validation scenario modules,
`tests/sim/test_sim_rest_reads.py`, OpenAPI/schema changes, shared tests/fixtures,
ledger regeneration, deployment/stack changes, release metadata and final
campaign scheduling. Workers supply route/behavior deltas and reproductions;
they do not regenerate shared artifacts. Existing test ownership transfers not
listed above require a recorded coordinator handoff, not simultaneous edits.

Known missing work is explicitly assigned: real UC server/setup bridge (R3),
typed state/event conversion and REST raw-state completeness (R1/R3), safe scene
file separation and write barriers (R2), executor response/PIN parity (R4),
eager Flic import/default mismatch and discovery shutdown (R5), generated-request
and gesture proof (R6). None requires a new product decision to start. If installed
ucapi lacks a needed cleanup API, R3 reports the exact version/API limitation;
the coordinator serializes a bridge/dependency fix, never treats mDNS success as
a working Remote. If a golden entity change or schema change is genuinely
necessary, it is an explicit coordinator review item, not automatic approval.

Each worker report must name base/commit, actual files, tests/results, any mocked
parallel seams, runtime/container evidence obtained and still pending. Use
targeted commands `python -m pytest <owned tests> <listed regression paths>` in
the repository's appropriate environments. Keep HA/deployment/heavy campaigns
in their dedicated environments and serialized at integration; no full suite
is required for R0's documentation-only change.

The later gate must launch **the built image's normal entry point** with a real
simulator, persistent volume and both UC modes; prove migration-before-reads,
health under unreachable matrix, setup/reconfigure, REST/WS/UC command/state
parity, auth/lockouts, enabled/disabled lifecycle, failure rollback and SIGTERM.
Count active transport sessions, refresh workers and command/event deliveries;
test a reconnect and process restart, not only a happy-path response. Run the
dedicated UC, HA and Flic clients against that image and refresh route coverage
for each configured inventory to 100%. Record logs, commands, image digest and
test counts against the integrated SHA. Physical matrix/CEC observations, Remote
3/Flic hardware, outage recovery, 72-hour soak and field sign-off remain pending
under the existing validation plan.

R0 review evidence consists of source/test inspection documented above and narrow
path/link/whitespace checks. No Python runtime test or container result is claimed
by this contract itself.
