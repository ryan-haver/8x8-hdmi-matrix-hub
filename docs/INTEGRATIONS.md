# Integrations

> How the shared runtime connects to Remote 3, Flic and Home Assistant. The
> opt-in `Integration` lifecycle uses the same hub client as REST.
>
> **Integration surfaces:**
>
> 1. **Remote 3 adapter** — optional (`UC_ENABLED`, off by default), started
>    by the shared runtime. It uses the shared client and setup/reconfigure
>    path, with no second matrix connection.
> 2. **Flic** — enabled by default (`FLIC_ENABLED=true`); registration and
>    list routes are mounted with its registry. Explicit false disables those
>    integration routes, while core actions remain available.
> 3. **Home Assistant** — the HACS component at
>    `custom_components/hdmi_matrix/` is installed and configured manually.
>    Optional mDNS discovery is disabled by default and is controlled by
>    `HA_DISCOVERY_ENABLED`.
>
> **Validation:** the registry at
> [`docs/validation/features.yaml`](validation/features.yaml) splits
> the shipped surface into `F-UC` (Unfolded Circle), `F-HA` (Home
> Assistant), `F-FLIC` (Flic), and the cross-cutting security rows
> `F-SEC-*`. The row-by-row status is in
> [`docs/validation/LEDGER.md`](validation/LEDGER.md); no claim here
> is "proved on hardware" — see
> [`../ROADMAP.md`](../ROADMAP.md) §5 and
> [`../CHANGELOG.md`](../CHANGELOG.md) §"Pending hardware validation".
> Older candidate artifacts retain their tested commit provenance. Fresh
> integrated runtime evidence is indexed at
> [`docs/validation/RUNTIME_VALIDATION_INDEX.md`](validation/RUNTIME_VALIDATION_INDEX.md).

---

## 1. The opt-in integration framework

### What every framework integration gets

```python
class Integration(ABC):
    name: str          # registry name (e.g. "unfolded_circle")
    env_flag: str      # env var that turns it on ("UC_ENABLED")

    @classmethod
    def config_from_env(cls, environ) -> Any: ...

    async def start(self, hub: HubClient) -> None: ...
    async def stop(self) -> None: ...
    def health(self) -> dict[str, Any]: ...
    def routes(self) -> list[tuple[str, str, Callable]]: ...
```

* **`start(hub)`** — receives the hub-owned client. The integration
  must not touch `OreiMatrix` directly; it speaks to the matrix only
  through the client.
* **`stop()`** — release subscriptions, cancel background tasks,
  close any HTTP session the integration opened.
* **`health()`** — integration status dict available through the loader's
  health summary at `data.integrations` in `/api/health`.
* **`routes()`** — optional list of `(METHOD, PATH, HANDLER)` that
  an `IntegrationLoader` would mount on the aiohttp app.

### Discovery & lifecycle — `IntegrationRegistry` / `IntegrationLoader`

* **Register by `name`, `env_flag`, `import_path`
  (`module:Class`)** so the integration's third-party dependencies
  and module side effects stay behind its flag.
* **Imports happen at `load()` time, only for the ones enabled.**
* **`loader.start(hub)`** is transactional: a partial start is
  stopped, and the integrations that already started are also
  stopped, so a broken start is the same as no start.
* **`loader.stop()`** attempts every integration even when one
  stop fails, aggregating the failures into an `ExceptionGroup`.

### `HubClient` (Protocol) and the two transports

Both `HubClientLocal` and `HubClientHttp` keep the *shape* identical,
so an integration does not need to know which one the loader gave it.

* **`HubClient`** (Protocol) — `async def` `snapshot`,
  `switch`, `cycle_input`, `recall_preset`, `save_preset`,
  `power`, `send_cec`, `run_action`, `subscribe`, `close`.
* **`HubSnapshot`** has one-based integer port numbers; unknown
  signals / cables / displays are absent, not `false`.
* **`HubEvent`** carries a `kind` and a `data` dict; the
  set of `kind` values mirrors `hub.core.EventBus` topics
  (`hub_connection`, `routing`, `power`, `names`, `presets`,
  `signal`, `cable`, `display`).

### Runtime flags — defaults and lifecycle

The integration loader lazily imports enabled modules. Disabled integrations
do not create listeners or lifecycle tasks.

| Flag | Integration | Default | Disabled behavior |
| --- | --- | --- | --- |
| `UC_ENABLED` | `hub.integrations.unfolded_circle` | `false` | No UC/`ucapi` import, listener or advertisement. |
| `FLIC_ENABLED` | `hub.integrations.flic` | `true` | Flic routes and registry lifecycle are omitted; core REST actions remain. |
| `HA_DISCOVERY_ENABLED` | `hub.integrations.homeassistant` | `false` | No discovery import or Zeroconf dependency for HA; manual HACS setup remains. |

True spellings are `1`, `true`, `yes`, `on`; false spellings are `0`, `false`,
`no`, `off`, trimmed and case-insensitive. An unknown nonblank Flic value
warns and retains the enabled default.

For example, disable Flic endpoints with `FLIC_ENABLED=false`. To advertise the
REST service for discovery, set `HA_DISCOVERY_ENABLED=true`. This does not
install or configure the HACS component.
---

## 2. Remote 3 integration — `src/hub/integrations/unfolded_circle/`

> **Env:** `UC_ENABLED` (default `false`). When true, the shared runtime
> starts the Remote adapter alongside REST.
>
> **User-facing guide:** [`docs/UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md`](UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md),
> owned by `wp-g2-client-guides-doc-archive`.

### What it owns

* **WebSocket listener on `UC_INTEGRATION_HTTP_PORT`** (default
  `9095`) speaking the Unfolded Circle Remote 3 protocol.
* **mDNS advertisement** of `uc_integration` on the integration's
  configured interface; `UC_DISABLE_MDNS_PUBLISH=true` skips it for
  bridge networking.
* **Entity factory** (`entities.py`) generating Remote entity IDs that match
  the approved catalog: `remote.orei_matrix`, `button.preset_1..8`, per-input
  `remote.input_N_cec`, per-output `media_player.output_N` and
  `remote.output_N_cec`, `switch.matrix_power`, and the input/output sensors.
  Profile, scene, shortcut and macro choices are commands/pages on
  `remote.orei_matrix`, not separate entity IDs. SDK 0.7 does not advertise
  the optional select entities.
* **State projector** (`state.py`) keeping every entity's state in
  step with the matrix.
* **Handlers** (`handlers.py`) translating Remote commands
  (`select_source`, `send_cmd`, `button.press`, `switch.toggle`)
  into shared hub-client commands and response envelopes.

### What it does *not* do

* It does not create a second matrix connection; the shared runtime owns the
  `OreiMatrix` client and serializes setup reconfiguration.

### Validation evidence

* See [`docs/validation/LEDGER.md` — Remote 3 integration](validation/LEDGER.md#remote-3-integration-f-uc).
* Earlier records for `F-UC` remain attached to their recorded candidate.
  Scripted UC tests do not validate this new runtime or a physical Remote;
  the current campaign is tracked in the runtime validation index.
* `tests/uc/` exercises the protocol handshake, lifecycle, state
  sync and the entity commands used by the scripted Remote client.

---

## 3. Flic integration — REST handlers in `src/rest_api/`

> **What ships:** two routes mounted when `FLIC_ENABLED` enables the Flic
> integration.
>
> **User-facing guide:** [`docs/FLIC_SETUP.md`](FLIC_SETUP.md),
> owned by `wp-g2-client-guides-doc-archive`.

### Routes

* **`POST /api/integrations/flic/register`** — Flic Hub button
  discovery (handler `handle_register_flic_buttons` in
  `src/rest_api/integrations.py`).
* **`GET /api/integrations/flic/buttons`** — read the registered
  Flic buttons (`handle_get_flic_buttons`).

These are the only `/api/integrations/*` paths in the shipped app when Flic
is enabled. There is no general `/api/integrations` route and no
`/api/integrations/<name>/status` route. `/api/health` exposes the loader's
integration lifecycle mapping under `data.integrations`, alongside its
`matrix` and `runtime` summaries.

### Framework-level module — `src/hub/integrations/flic/`

`hub.integrations.flic` implements the `Integration` contract on top of
`HubClient`. The runtime starts one registry instance when enabled and binds
the REST routes to it. `FLIC_ENABLED` defaults to `true`; explicit false omits
the registry and its registration/list routes, not the core matrix actions.

### Validation evidence

* See [`docs/validation/LEDGER.md` — Flic](validation/LEDGER.md#flic).
* Older Flic records remain linked to their recorded candidate. Runtime
  request replay uses explicit Node SDK stubs and is not physical button
  proof; see the [runtime validation index](validation/RUNTIME_VALIDATION_INDEX.md).

---

## 4. Home Assistant integration — HACS component and discovery

> **What ships today:** the HACS component at
> [`custom_components/hdmi_matrix/`](../custom_components/hdmi_matrix/),
> installed like any other HACS integration and configured manually
> in *Devices & Services*.

### What it owns

* **Config flow** (`config_flow.py`) for IP / port / options.
* **HA-style entities** — `select.output_N_source`,
  `button.preset_N`, `media_player.input_N`,
  `switch.matrix_power`, `switch.output_N_stream`,
  `binary_sensor.output_N_connected`, `binary_sensor.input_N_signal`,
  per-output HDCP/HDR/scaler selects, and the `hdmi_matrix.*`
  service bundle.
* **Coordinator** (`coordinator.py`) for polling (5 s default
  interval).

### What it does *not* do

* Optional REST-service mDNS discovery is controlled by
  `HA_DISCOVERY_ENABLED` (default false). Discovery advertises the service;
  it does not install or automatically configure the HACS component.
* The `HACS` component installed in `custom_components/hdmi_matrix/`
  is a normal HACS integration that talks to the hub over REST; it
  is not an opt-in module of the running `run.py`.

### Framework-level module — `src/hub/integrations/homeassistant/`

`hub.integrations.homeassistant` implements the `Integration` contract for
optional service discovery on top of `HubClient`. The runtime imports it only
when discovery is enabled. The HACS component remains a separate user-installed
REST client.

### Validation evidence

* See [`docs/validation/LEDGER.md` — Home Assistant component](validation/LEDGER.md#home-assistant-component-f-ha).
* Historical HACS component records include V3 evidence on the simulator (a real HA container onboarded through
  `/api/onboarding`, the config flow, the service calls and the
  entity state changes checked against the simulator). They do not validate
  current runtime discovery or physical-LAN HA setup; those gates are tracked
  separately in the runtime validation index.

---

## 5. `HubClient` — the contract every framework integration sees

The two transport implementations keep the *shape* identical, so an
integration does not need to know which one the loader gave it.

### `HubClientLocal` (`src/hub/integrations/hub_client_local.py`)

* Inherits `EventPublisher`; subscribers get the snapshot-then-events
  model.
* When the underlying provider is `OreiMatrix` (the legacy shape, not
  the `HubClient` shape itself), the wrapper wires the optional
  `snapshot_provider`, `action_runner` and `event_subscribe`
  callbacks.

### `HubClientHttp` (`src/hub/integrations/hub_client_http.py`)

* Implements the same surface over the hub's REST + WebSocket.
* Used by remote-host integrations and by the test suite.

### Calling patterns

* **Read state:** `await hub.snapshot()` → `HubSnapshot`.
* **Subscribe:** `unsubscribe = hub.subscribe(callback)`; call
  `unsubscribe()` to detach.
* **Run an action:** `result = await hub.run_action(...)`; the runtime
  action runner is also used by REST dispatch.
* **Route a single output / a cycle / a preset:**
  `await hub.switch(input, output)`,
  `await hub.cycle_input("next", output)`,
  `await hub.recall_preset(slot)`.
* **Power:** `await hub.power(True)`.
* **CEC:** `await hub.send_cec(target_kind, port, command)` where
  `target_kind` is `"input"` or `"output"` and `command` is one of
  the verbs from `src/cec_commands.py`.

---

## 6. Adding a new framework integration

The copy-pasteable skeleton, the registry plumbing, the test
requirements and the lifecycle invariants are documented in
[`docs/INTEGRATION_TEMPLATE.md`](INTEGRATION_TEMPLATE.md). The short
checklist:

* Define `<MyConfig>` (frozen dataclass) and `MyIntegration` under
  `src/hub/integrations/<my_name>/__init__.py`.
* Set `name` and `env_flag` on the class.
* Implement `config_from_env(environ)`, `start(hub)`, `stop()`,
  `health()` and (optionally) `routes()`.
* Register it in the registry file with
  `import_path="hub.integrations.<my_name>:MyIntegration"`.
* Add unit tests under `tests/test_hub_<my_name>_integration.py`
  for the lifecycle, health, and route shapes.
* Add a `scenarios/` block under `tests/validation/scenarios/` for
  the scenarios the integration must hold up in CI; link them from
  `docs/validation/features.yaml` so the ledger refreshes.
* Until the wiring lands, your integration ships as a tested library
  that nobody starts — the README's "what is shipped" table is the
  source of truth for what the operator sees today.

---

## 7. What this document does *not* cover

* **Built-in shortcuts** (the toggleable items in the Quick Actions
  drawer) are part of the core, not an integration — see
  `src/system_shortcuts.py` and the API reference.
* **The `HACS` Home Assistant component** (`custom_components/
  hdmi_matrix/`) is *not* under the framework's env flag; install
  it through HACS like any other integration. It speaks to the
  core REST and WebSocket surfaces. Setting `HA_DISCOVERY_ENABLED`
  has no effect on it.
* **Schedule / MQTT / Alexa skill** are *not* in the in-flight
  worktrees. See [`../ROADMAP.md`](../ROADMAP.md) §6.
