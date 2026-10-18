# Integrations

> How the hub talks to the outside world. This document splits the
> framework's opt-in `Integration` contract from the shipped
> integration surface so a reader cannot confuse the two — that
> confusion is what tripped up the previous pass.
>
> **Two layers, kept apart on purpose:**
>
> 1. **Shipped integrations** — what `run.py` and `src/driver.py`
>    actually start today. The Unfolded Circle driver is the
>    legacy `src/integrations/unfolded_circle/` package; Flic is
>    the always-mounted REST handlers at
>    `POST /api/integrations/flic/register` and
>    `GET /api/integrations/flic/buttons`; Home Assistant is the
>    HACS component at `custom_components/hdmi_matrix/` (manual
>    config flow).
> 2. **Framework integration libraries** — the opt-in
>    `Integration` contract under `src/hub/integrations/`
>    (`base.py`, `hub_client*.py`, plus the Flic, Home Assistant
>    discovery, and Unfolded Circle framework modules). These
>    modules are importable, unit-tested, and what the
>    `IntegrationRegistry` / `IntegrationLoader` would discover
>    by env flag. **The shipped `run.py` / `src/driver.py` do not
>    load them yet.** Until the wiring lands, the framework is
>    library-only.
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
> Framework-level tests live in `tests/test_hub_*_integration.py`;
> they prove the libraries work in isolation, not that the runtime
> uses them.

---

## 1. The opt-in integration framework (library-only today)

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
* **`health()`** — dict (currently unused in the shipped runtime;
  the live `/api/health` returns `matrix` and `runtime` summary,
  not a per-integration block).
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

### Framework defaults — what each flag actually does

> These flags are declared by the framework modules under
> `src/hub/integrations/`. **They are not read by the shipped
> `run.py` or `src/driver.py` startup today.** Setting any of
> these does not turn the corresponding integration on or off in
> the shipped binary; it adjusts framework-level state that the
> not-yet-wired startup would consult.

| Flag                    | Framework module                  | Library default | Effect when `false`                                                                                                              | Effect when `true` (in the framework)                                                                                  |
| ----------------------- | --------------------------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `UC_ENABLED`            | `hub.integrations.unfolded_circle`| `False`        | The framework Unfolded Circle integration would not be loaded by `IntegrationLoader`.                                            | The framework Unfolded Circle integration would be loaded and started against the `HubClient`.                          |
| `FLIC_ENABLED`           | `hub.integrations.flic`           | **`True`**     | The framework Flic integration would not be loaded. The legacy REST handlers `POST /api/integrations/flic/register` and `GET /api/integrations/flic/buttons` are **always** mounted in the shipped app and are unaffected. | The framework Flic integration would be loaded and started against the `HubClient`.                                       |
| `HA_DISCOVERY_ENABLED` | `hub.integrations.homeassistant` | **`False`**     | The framework HA discovery integration would not be loaded.                                                                       | The framework HA discovery integration would be loaded and started against the `HubClient`.                              |

The shipped runtime contracts — the ones the operator experiences
today — are different:

* **`UC_ENABLED`** *is* read by `run.py`: with `true`, it switches
  to `run_uc()` and runs the **legacy** `src/driver.py` (not the
  framework module).
* **`FLIC_ENABLED`** is *not* read by `run.py`. The REST handlers
  ship always-mounted.
* **`HA_DISCOVERY_ENABLED`** is *not* read by `run.py`. There is
  no auto-discovery payload at runtime. The HA component is the
  HACS install at `custom_components/hdmi_matrix/` (manual setup).

---

## 2. Shipped UC integration — `src/integrations/unfolded_circle/`

> **Env:** `UC_ENABLED` (default `false`). When `true`,
> `run.py` switches to `run_uc()` and runs `src/driver.py`.
>
> **User-facing guide:** [`docs/UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md`](UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md),
> owned by `wp-g2-client-guides-doc-archive`.

### What it owns

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
  step with the matrix.
* **Handlers** (`handlers.py`) translating Remote commands
  (`select_source`, `send_cmd`, `button.press`, `switch.toggle`)
  into `OreiMatrix` calls and back into response envelopes.

### What it does *not* do

* It does **not** import `hub.integrations.unfolded_circle`. The
  shipped integration is the legacy `src/driver.py`-driven
  implementation; the framework module shares the same name but is
  a separate library.
* It does **not** keep the matrix connection itself. `OreiMatrix`
  is shared with the core; `src/driver.py` starts it.

### Validation evidence

* See [`docs/validation/LEDGER.md` — Remote 3 integration](validation/LEDGER.md#remote-3-integration-f-uc).
* `F-UC` features at V1 today (entity definition + scripted Remote),
  some V3 (the scripted UC client against the hub against the
  simulator). **V4 (real Remote 3 against a real OREI BK-808) is not
  yet recorded.**
* `tests/uc/` exercises the protocol handshake, lifecycle, state
  sync and the entity commands used by the scripted Remote client.

---

## 3. Shipped Flic integration — REST handlers in `src/rest_api/`

> **What ships today:** two routes, both **always mounted** by
> `src/rest_api/app.py::create_rest_app`. There is no env flag that
  toggles them.
>
> **User-facing guide:** [`docs/FLIC_SETUP.md`](FLIC_SETUP.md),
> owned by `wp-g2-client-guides-doc-archive`.

### Routes

* **`POST /api/integrations/flic/register`** — Flic Hub button
  discovery (handler `handle_register_flic_buttons` in
  `src/rest_api/integrations.py`).
* **`GET /api/integrations/flic/buttons`** — read the registered
  Flic buttons (`handle_get_flic_buttons`).

These are the only `/api/integrations/*` paths in the shipped app.
There is no general `/api/integrations` and no `/api/integrations/
<name>/status`. The `/api/health` endpoint returns `matrix` and
`runtime` summaries, not per-integration health.

### Framework-level module — `src/hub/integrations/flic/`

`hub.integrations.flic` is a separate, library-only module that
implements the `Integration` contract for Flic on top of
`HubClient`. It is what the `IntegrationRegistry` would discover if
`FLIC_ENABLED=true`. **It is not what the shipped REST handlers
are.** `FLIC_ENABLED` defaults to `true` in this library (so legacy
Flic installations remain opted-in when the framework start-up path
lands), but does not currently gate the always-mounted REST routes.

### Validation evidence

* See [`docs/validation/LEDGER.md` — Flic](validation/LEDGER.md#flic).
* `F-FLIC` features are V1 unit + V3 (request replay against the
  hub's REST routes listening unconditionally). **V4 (real Flic
  Hub) is not recorded** for v0.5.x.

---

## 4. Shipped Home Assistant integration — HACS component

> **What ships today:** the HACS component at
> [`custom_components/hdmi_matrix/`](custom_components/hdmi_matrix/),
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

* **It is not behind `HA_DISCOVERY_ENABLED`.** That framework-level
  flag exists in `src/hub/integrations/homeassistant/` for a future
  MQTT-style auto-discovery payload, but **nothing in the shipped
  runtime reads it.** There is no auto-discovery payload emitted by
  the running hub today.
* The `HACS` component installed in `custom_components/hdmi_matrix/`
  is a normal HACS integration that talks to the hub over REST; it
  is not an opt-in module of the running `run.py`.

### Framework-level module — `src/hub/integrations/homeassistant/`

`hub.integrations.homeassistant` is a separate, library-only module
that implements the `Integration` contract for the HA discovery
flow on top of `HubClient`. It is what `IntegrationRegistry` would
discover when (and only when) startup is wired. **It is not in the
shipped runtime path.**

### Validation evidence

* See [`docs/validation/LEDGER.md` — Home Assistant component](validation/LEDGER.md#home-assistant-component-f-ha).
* The HACS component at `custom_components/hdmi_matrix/` has V3
  evidence on the simulator (a real HA container onboarded through
  `/api/onboarding`, the config flow, the service calls and the
  entity state changes checked against the simulator).
  **V4 (the operator's HA deployment) is not yet recorded.**

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
* **Run an action:** `result = await hub.run_action(...)` (the
  framework module returns an `ActionRunResult`; not the path
  REST takes today).
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
