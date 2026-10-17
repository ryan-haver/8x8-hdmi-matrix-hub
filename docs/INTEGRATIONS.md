# Integrations

> How the hub talks to the outside world. Every module below is **opt-in**
> (an environment variable turns it on; a disabled one is never imported
> and opens no port); every module sees the matrix through the same
> `HubClient` regardless of whether that client is in-process
> (`HubClientLocal`) or remote (`HubClientHttp`).
>
> **Validation:** the registry under
> [`docs/validation/features.yaml`](validation/features.yaml) splits the
> integration surface into `F-UC` (Unfolded Circle), `F-HA` (Home Assistant),
> `F-FLIC` (Flic), and the cross-cutting security rows `F-SEC-*`. The
> row-by-row status is in
> [`docs/validation/LEDGER.md`](validation/LEDGER.md); no claim here is
> "proved on hardware" — see
> [`../ROADMAP.md`](../ROADMAP.md) §5 and
> [`../CHANGELOG.md`](../CHANGELOG.md) §"Pending hardware validation".

---

## 1. The opt-in framework

### What every integration gets

```python
class Integration(ABC):
    name: str          # registry name (e.g. "unfolded_circle")
    env_flag: str      # the env var that turns it on ("UC_ENABLED")

    @classmethod
    def config_from_env(cls, environ) -> Any: ...

    async def start(self, hub: HubClient) -> None: ...
    async def stop(self) -> None: ...
    def health(self) -> dict[str, Any]: ...
    def routes(self) -> list[tuple[str, str, Callable]]: ...
```

* **`start(hub)`** — receives the hub-owned client. The integration must
  not touch `OreiMatrix` directly; it speaks to the matrix only through
  the client (see [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) §6).
* **`stop()`** — release subscriptions, cancel background tasks,
  close any HTTP session the integration opened. Designed to be
  re-entrant so `IntegrationLoader.stop()` is idempotent.
* **`health()`** — dict included by `/api/health`'s per-integration
  block. Optional fields (`enabled`, `connected`, `tasks_running`,
  `last_error`) are surfaced by whichever integrations support them.
* **`routes()`** — optional list of `(METHOD, PATH, HANDLER)` mounted
  on the aiohttp app **after** the core REST routes. Used by the
  Unfolded Circle integration for `GET /api/integrations/<name>/status`
  and similar.

### Discovery & lifecycle — `IntegrationRegistry` / `IntegrationLoader`

* **Register by `name`, `env_flag`, `import_path` (`module:Class`)**;
  never register an imported class, so the integration's third-party
  dependencies and module side effects stay behind its flag.
* **Imports happen at `load()` time, only for the ones enabled.**
  An environment where `HA_DISCOVERY_ENABLED=false` and
  `FLIC_ENABLED=false` never imports `aiohttp` HA code or the Flic
  SDK code.
* **`loader.start(hub)`** is transactional: a partial start is
  stopped, and the integrations that already started are also
  stopped, so a broken start is the same as no start.
* **`loader.stop()`** attempts every integration even when one stop
  fails, aggregating the failures into an `ExceptionGroup`.
* **`/api/integrations`** reports the registered integrations and
  their health summary (`IntegrationLoader.health_summary()`).

### Configuration

* Every integration reads a frozen `IntegrationConfig` (or a richer
  subclass) from `config_from_env(environ)` so the loader can hold
  the configuration without re-reading the environment at start time.
* Boolean flags accept `1`, `true`, `yes`, `on` as truthy and
  `0`, `false`, `no`, `off` as falsy; anything else falls back to the
  default.

For the canonical "building a new integration" walkthrough (a complete
copy-pasteable skeleton, the test requirements and the registry
plumbing) see [`docs/INTEGRATION_TEMPLATE.md`](INTEGRATION_TEMPLATE.md).

---

## 2. `HubClient` — the contract every integration sees

The two transport implementations keep the *shape* identical, so an
integration does not need to know which one the loader gave it.

### `HubClientLocal` (in-process)

* Inherits `EventPublisher`; subscribers get the snapshot-then-events
  model.
* When the underlying provider is `OreiMatrix` (the legacy shape, not
  the `HubClient` shape itself), the wrapper wires the optional
  `snapshot_provider`, `action_runner` and `event_subscribe` callbacks
  to include catalogs, the visibility store, and to follow
  front-panel changes.
* **The local client never starts a poller** and never disconnects
  the shared matrix on close — those are owned by the core.

### `HubClientHttp` (cross-process)

* Implements the same surface over the hub's REST + WebSocket.
* Used by remote-host integrations and by the test suite to drive an
  isolated hub container.
* Subscribers receive snapshots and events through the same
  `HubSnapshot` / `HubEvent` projection that ships to the WebSocket
  client.

### `HubSnapshot` / `HubEvent`

* **`HubSnapshot`** has one-based integer port numbers. Unknown
  signals, cables and displays are **absent**, not `false` — the
  absence carries information, the `false` would not.
* **`HubEvent`** carries a `kind` and a `data` dict. The set of
  `kind` values mirrors the topics in
  [`hub.core.EventBus`](ARCHITECTURE.md#hubcore--state-owner) —
  `hub_connection`, `routing`, `power`, `names`, `presets`, `signal`,
  `cable`, `display`.
* Snapshots are emitted once on `subscribe` (initial projection), then
  changes are emitted as `HubEvent` frames; the WebSocket schema in
  [`docs/api/websocket.schema.json`](api/websocket.schema.json) is the
  wire format.

### Calling patterns

* **Read state:** `await hub.snapshot()` → `HubSnapshot`.
* **Subscribe:** `unsubscribe = hub.subscribe(callback)`; call
  `unsubscribe()` to detach.
* **Run an action:**
  `result = await hub.run_action("profile", profile_id, passcode=...)` →
  the `ActionRunResult` shape from
  [`hub.domain.ActionRunner`](ARCHITECTURE.md#hubdomain--action-execution).
* **Route a single output / a cycle / a preset:**
  `await hub.switch(input, output)`, `await hub.cycle_input("next",
  output)`, `await hub.recall_preset(slot)`.
* **Power:** `await hub.power(True)`.
* **CEC:** `await hub.send_cec(target_kind, port, command)` where
  `target_kind` is `"input"` or `"output"` and `command` is one of the
  verbs from `src/cec_commands.py`.

---

## 3. `unfolded_circle` — Remote 3 integration

> **Env:** `UC_ENABLED` (default `false`). When enabled, the
> integration is discovered and started by `IntegrationLoader`.
>
> **See also:** the user-facing guide for the operator is owned by
> `wp-g2-client-guides-doc-archive`
> ([`docs/UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md`](UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md));
> the operator-facing device-pairing flow is in `driver.json`'s
> `setup_data_schema`.

### What the integration owns

* **WebSocket listener on `UC_INTEGRATION_HTTP_PORT`** (default
  `9095`) speaking the Unfolded Circle Remote 3 protocol.
* **mDNS advertisement** of `uc_integration` on the integration's
  configured interface; `UC_DISABLE_MDNS_PUBLISH=true` skips it for
  bridge networking.
* **Entity factory** (`entities.py`) generating every UI entity the
  Remote shows: `remote.matrix`, `button.preset_1..8`, per-input
  `remote.input_N_cec`, per-output `media_player.output_N`,
  `binary_sensor.matrix_connection`, and the sensors, switches and
  shortcuts the profile / scene / macro surfaces need.
* **State projector** (`state.py`) keeping every entity's state in
  step with the hub's `HubSnapshot` and `HubEvent` frames.
* **Handlers** (`handlers.py`) translating Remote commands
  (`select_source`, `send_cmd`, `button.press`, `switch.toggle`)
  into `HubClient` calls and back into the `ActionRunResult`-shaped
  responses the Remote expects.
* **One-shot password entry** (`migration.py`) for the pre-v0.4
  setup that used to set `orei_password` in clear text. With
  `UC_ENABLED=true` the password flows through the Remote's
  setup screen only.
* **Configuration** (`config.py`) reading the deployment env vars
  (`UC_INTEGRATION_INTERFACE`, `UC_DRIVER_URL`, `UC_CONFIG_HOME`,
  `UC_INTEGRATION_HTTP_PORT`).

### What it does *not* do

* It does **not** import `OreiMatrix`. Every matrix read or write goes
  through the hub's `HubClient`. The `adapter.py` removed in v0.4 is
  the proof of that contract.
* It does **not** keep the matrix connection itself. The core owns
  the connection; this module is a Remote-facing façade.

### Validation evidence

* See [`docs/validation/LEDGER.md` — Remote 3 integration](validation/LEDGER.md#remote-3-integration-f-uc).
* `F-UC` features at V1 today (entity definition + scripted Remote),
  some V3 (the scripted UC client against the hub against the
  simulator). **V4 (real Remote 3 against a real OREI BK-808) is not
  yet recorded**; that is the operator-present step in HIL Session 2.
* `tests/uc/` exercises the protocol handshake, lifecycle, state
  sync and the entity commands used by the scripted Remote client.

---

## 4. `flic` — Flic buttons

> **Env:** `FLIC_ENABLED` (default `false`). New deployments ship
> with it `false`; existing Flic integrations had the route live by
> default and may set `FLIC_ENABLED=false` to opt out.
>
> **See also:** the user-facing guide
> ([`docs/FLIC_SETUP.md`](FLIC_SETUP.md), owned by
> `wp-g2-client-guides-doc-archive`).

### What the integration owns

* **HTTP listener** for the Flic Hub's `Internet Request` template
  (Flic Original, Flic 2; single/double-click, hold).
* **Zone-based multi-room button mapping** for Flic Duo
  (left-click, right-click, both-click), tied to named profiles.
* **Flic Twist** rotation handlers mapped to
  `POST /api/input/next` / `POST /api/input/previous` on the hub, and
  the Twist press handler mapped to the configured volume / CEC /
  mute action.
* **State subscription** to `HubEvent` so the dashboard reflects the
  last routed zone without polling.
* **Pre-built Flic Hub SDK JavaScript templates** for in-hub custom
  modules — the user-facing guide ships the snippets.

### Validation evidence

* See [`docs/validation/LEDGER.md` — Flic](validation/LEDGER.md#flic).
* `F-FLIC` features are V1 unit + V3 (request replay against the
  hub's hub listening on `FLIC_ENABLED=true`). **V4 (real Flic Hub)
  is not recorded** for v0.5.0 — the "available when the owner plugs
  it in" bucket.

---

## 5. `homeassistant` — Home Assistant discovery

> **Env:** `HA_DISCOVERY_ENABLED` (default `false`). When disabled,
> the discovery payload is never generated and the integration ships
> zero extra routes.
>
> **Note:** the HACS component installed in `custom_components/
> hdmi_matrix/` is *not* behind this flag — it is a regular HACS
> integration that talks to the hub over REST. The flag governs the
> optional MQTT-style auto-discovery payload that bridges an HA
> install to this hub without going through HACS.

### What the integration owns

* **HA-style discovery payload** built from the live `HubSnapshot`,
  naming every entity the HACS component would create
  (`select.output_N_source`, `button.preset_N`, `media_player.input_N`,
  `switch.matrix_power`, `switch.output_N_stream`,
  `binary_sensor.output_N_connected`, `binary_sensor.input_N_signal`,
  the per-output HDCP/HDR/scaler selects, and the `hdmi_matrix.*`
  service bundle).
* **Polling-friendly HTTP endpoints** for any HA install that wants
  to scrape rather than install the HACS component.

### Validation evidence

* See [`docs/validation/LEDGER.md` — Home Assistant component](validation/LEDGER.md#home-assistant-component-f-ha).
* The HACS component at `custom_components/hdmi_matrix/` has V3
  evidence on the simulator (a real HA container onboarded through
  `/api/onboarding`, the config flow, the service calls and the
  entity state changes checked against the simulator).
  **V4 (the operator's HA deployment) is not yet recorded.**

---

## 6. Adding a new integration

The copy-pasteable skeleton, the registry plumbing, the test
requirements and the lifecycle invariants are documented in
[`docs/INTEGRATION_TEMPLATE.md`](INTEGRATION_TEMPLATE.md). The short
checklist:

* Define `<MyConfig>` (frozen dataclass) and `MyIntegration` under
  `src/hub/integrations/<my_name>/__init__.py`.
* Set `name` and `env_flag` on the class.
* Implement `config_from_env(environ)`, `start(hub)`, `stop()`,
  `health()` and (optionally) `routes()`.
* Register it in the registry file with `import_path="hub.integrations.
  <my_name>:MyIntegration"`.
* Add unit tests under `tests/test_hub_<my_name>_integration.py` for
  the lifecycle, health, and route shapes.
* Add a `scenarios/` block under `tests/validation/scenarios/` for the
  scenarios the integration must hold up in CI; link them from
  `docs/validation/features.yaml` so the ledger refreshes.
* Update the README's "Flic/HA/UC equivalents" list and the Focused UI
  if the integration exposes new routes.

---

## 7. What this document does *not* cover

* **Built-in shortcuts** (the toggleable items in the Quick Actions
  drawer) are part of the core, not an integration — see
  `src/system_shortcuts.py` and the API reference.
* **The `HACS` Home Assistant component**
  (`custom_components/hdmi_matrix/`) is *not* under the integrations
  framework's env flag; install it through HACS like any other
  integration. It speaks to the core REST and WebSocket surfaces.
* **Schedule / MQTT / Alexa skill** are *not* in the in-flight
  worktrees. See [`../ROADMAP.md`](../ROADMAP.md) §6.
