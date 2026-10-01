# Validation: how proof of function works here

This directory implements [`VALIDATION_PLAN.md`](VALIDATION_PLAN.md). The short version: a feature counts as working only when a scenario has made it happen and read the effect back from the device. A 200 response isn't proof.

| File | What it is |
| --- | --- |
| [`features.yaml`](features.yaml) | The registry: every user-facing feature (265), its interfaces, target level, **recorded** level with the reason (`basis`), linked findings and scenarios. Maintained by hand. |
| [`LEDGER.md`](LEDGER.md) | Generated report: level per feature from fresh evidence, freshness, open findings, summary per area. Never edit it by hand. |
| [`evidence.schema.json`](evidence.schema.json) | JSON schema of an evidence record. |
| [`evidence/`](evidence/README.md) | Committed evidence records (milestones, hardware sessions). CI evidence is an artifact. |
| [`findings_pending.yaml`](findings_pending.yaml) | Bugs found by validation that still need a row in the register (`REMEDIATION_PLAN.md` §4). They count as open findings. |
| `../../tools/validate/` | The runner, clients, ledger generator and CI gate. |
| `../../tests/validation/scenarios/` | The scenarios. |

## Commands

```bash
python -m tools.validate list                                   # scenarios, their features, clients, targets
python -m tools.validate run                                    # every scenario, api client, simulator (V2)
python -m tools.validate run --client api --client browser      # + the web UI in Chromium (V3); needs `npm ci`
python -m tools.validate run --client uc                        # the scripted Remote 3 (V3); needs requirements-uc.txt
python -m tools.validate run --client ha                        # a real Home Assistant container (V3); needs Docker
python -m tools.validate run --feature F-MTX-001                # only scenarios that prove this feature
python -m tools.validate run --scenario presets.recall --client browser
python -m tools.validate ledger --evidence build/validation/evidence --run-summary build/validation/run-summary.json \
                                --out build/validation/LEDGER.md
python -m tools.validate check  --evidence build/validation/evidence --run-summary build/validation/run-summary.json
python -m tools.validate ledger                                 # regenerate docs/validation/LEDGER.md (committed evidence only)
```

`run` writes to `build/validation/` by default: `evidence/` (records plus screenshots next to them), `logs/` (hub and simulator logs), and `run-summary.json`. `--record` writes the records into `docs/validation/evidence/` so you can commit them at a milestone.

**Simulator target (`--target sim`, the default).** The runner starts the simulator (`python -m tools.simulator`) and the real hub (`run.py`, modular API-only mode, the same way as `tools/dev_stack.py`) on free ports. The hub data is a fresh copy of `tests/e2e/fixtures/data` (profiles, macros, scenes and so on). For the `uc` client the runner restarts the hub the way it ships with the Remote integration enabled (`run.py` legacy mode, `src/driver.py`, integration WebSocket on a free port, mDNS off, `config_state.json` seeded with the simulator's address), and switches back for the next client; the record's `environment.hub.entry` says which. Before each scenario, the simulator is reset to its seed state through `PUT /_sim/state`. The hub keeps its session because `/_sim/reset` would trigger BE-04. After a fault-injection scenario the hub is restarted.

**Hardware target (`--target hardware`).** This runs the same scenarios against a real matrix:

```bash
python -m tools.validate run --target hardware --matrix-host 192.168.1.50 --operator "Ryan" \
    [--allow-writes] [--allow-unrestorable] [--answers answers.json] [--hub-url http://hub:8080] [--record]
```

- By default nothing that changes the matrix runs. `--allow-writes` enables scenarios whose changes can be restored. Before each one the runner reads the matrix state, and afterwards it writes back every field that changed and verifies the restore by reading back again. If a restore does not verify, the session stops. Scenarios that change something that cannot be restored (preset slots, CEC enable flags, a TV turned on by CEC, marked `presets`, `cec` or `physical`) also need `--allow-unrestorable`. Fault-injection scenarios run only on the simulator.
- The runner reads the device state directly from the matrix's HTTP API (read-only comheads), independently of the hub under test. There is no command log on hardware, so the effect is proven by that readback and by the operator.
- `observe` questions are asked in the terminal, for example "Does the display on output 1 now show …? [y/n]", followed by an optional path to a photo or video. You can also supply the answers in a JSON file: `{"routing.switch_one": [{"answer": "y", "media": ["photos/out1.jpg"]}]}`. A scenario whose question is left unanswered is recorded as `blocked`, and a "no" answer fails it. V4 records need a named `--operator`.
- The tests in `tests/validation/test_runner.py` exercise this mode by pointing it at the simulator's device port. No test ever contacts a real device.

## Levels a run can prove

| Target | Client | Level of a PASS |
| --- | --- | --- |
| sim | `api` (REST exactly as HA/Flic/scripts use it) | V2 |
| sim | `browser` (Chromium drives the shipped web UI), `uc` (the scripted Remote 3, `tools/uc_remote_sim.py`), `ha` (a real Home Assistant container), later `flic` | V3 |
| hardware | any | V4 |

The ledger computes each feature's **level** as the highest level of *fresh passing* evidence. If there is none, it uses the registry's recorded `current`. An open critical or high finding linked to the feature caps it at V1. Evidence is *stale* when a file listed in the scenario's `covers` changed after the evidence commit, or had uncommitted changes when the scenario ran.

## CI gate (`python -m tools.validate check`)

The gate fails when:

- **(a)** a scenario fails and one of its failed checks is not linked to an open finding (`gate: regression`). This includes simulator runs that end `blocked`, which means the infrastructure broke.
- **(b)** a feature drops below its recorded level: its fresh evidence is lower than `current`, or a scenario for it failed at a level at or below `current`.
- `--expect-clients api,browser`: a client ran no scenario, for example because Chromium was missing.

Known bugs don't fail CI. Their checks carry `finding="BE-12"`, and the run records FAIL evidence linked to that finding. When the finding is fixed, the check passes and the evidence shows it. Before closing the register row, check the scenario passes. Then remove the link.

## Adding a scenario

Create or extend a module in `tests/validation/scenarios/` with a `SCENARIOS` list:

```python
from tools.validate.model import CommandSent, Device, DeviceUnchanged, Response, Scenario, WsEvent, act
from ._paths import HUB_CORE, OUTPUTS

SCENARIOS = [
    Scenario(
        id="outputs.hdcp",                       # <area>.<flow>, unique
        title="Set output 3 to HDCP 2.2",
        features=("F-MTX-009",),                 # what it proves (all clients)
        client_features={"api": ("F-API-010",)}, # proven only with this client (e.g. the REST contract)
        clients=("api",),                        # add "browser" once the browser client has the intent
        writes=("outputs",),                     # hardware safety: domains the action changes
        sim_state={"outputs": {"2": {"hdcp": 3}}},  # optional simulator precondition (sim only)
        action=act("output_setting", output=3, setting="hdcp", body={"mode": 2}),
        expect=(
            Response(status=200),
            Device("outputs[2].hdcp", equals=2),             # read back from the device, polled
            DeviceUnchanged(allow=("outputs[2].hdcp",)),     # and nothing else changed
            CommandSent("set output hdcp", {"output": 3, "hdcp": 2}, count=1),  # simulator command log
            WsEvent("status_update", finding="API-XX"),      # a check that fails today: link its finding
        ),
        observe=("Does the display on output 3 still show a picture?",),  # asked on hardware
        covers=(*HUB_CORE, *OUTPUTS),            # evidence goes stale when these change
    ),
]
```

Then add the scenario id to the feature's `scenarios:` in `features.yaml` (a test checks that the links go both ways) and run `python -m tools.validate run --scenario outputs.hdcp`.

- Available **intents** are listed in `tools/validate/model.py` (`INTENTS`). The api client maps each one to its REST call in `clients/api.py::rest_call`. For failure paths and edge cases use `act("request", method=..., path=..., json=...)`.
- **Expectations:** `Device` / `DeviceUnchanged` (device state), `CommandSent` / `NoCommand` / `NoProtocolWarnings` (simulator command log; `n/a` on hardware), `Response` (the client's HTTP result), `Hub` (read back through the hub API, e.g. a name shown afterwards), `WsEvent` / `NoWsEvent` (what a `/ws` client received), `ClientState` (what the client itself shows, e.g. a Home Assistant entity state; `before=` makes the runner wait for the old value first, so the check proves a change; `n/a` for clients that cannot observe). `clients=("api",)` limits a check to one client.
- **Changes behind the hub's back** (a cable, a signal, the front panel, a power loss): `act("device_change", event={...})` (`POST /_sim/event`), `patch={...}` or `reboot=<seconds offline>` (`POST /_sim/reboot`). The runner makes the change on the simulator itself (`targets=("sim",)`), and only clients that observe (`Client.observes`: `ha`, `browser`) run the scenario, checking the effect with `ClientState`.
- **The WebSocket contract** (`docs/api/WEBSOCKET.md`, WP-C2): the runner's `/ws` observer connects before each action and sends `get_status`, so the hub has read the reset simulator before the action (changes the reset made are announced before it, not during the scenario). Every message it records is checked against `docs/api/websocket.schema.json`; that check is added to every scenario that received messages, and a contract violation fails it.
- **Failure paths** are scenarios with `kind="failure"`, `faults={...}` (simulator fault injection, see `tools/simulator/README.md`) and `targets=("sim",)`.
- Scenarios that fail because of a known bug stay in. Link the finding on the failing check. If the bug is new, add it to `findings_pending.yaml` first.

## Adding a client

Subclass `tools.validate.clients.base.Client`. It needs `name`, the `intents` it can perform, `start(hub)`, `perform(action) -> ActionResult` and `stop()`. Register it in `clients/__init__.py`. Before each action the runner sets `client.context` (`label`, `forwarded_for`, `artifacts_dir`). Set `hub_mode = "uc"` if the client needs the hub with the Remote integration (the runner then passes `HubInfo.uc_url`). A client that shows state sets `observes = True` and implements `observe(key)` (for `ClientState`). The `flic` client is a placeholder that raises `NotImplementedError` naming its work package. A PASS with a real client counts as V3.

**The `browser` client** (`clients/browser.py` + `browser_driver.mjs`) drives the shipped web UI in Chromium, one fresh
page per action: `route` (matrix grid), `route_all` (Route To All drawer), `preset_recall` / `preset_rename` (Presets
drawer), `profile_recall` (Profiles tab), `scene_run` (the scene's dashboard card, else the Settings drawer's Scenes
tab) and `kiosk_route` (the kiosk routing wizard, `/kiosk`). A passcode prompt is answered with the action's
`passcode`, or cancelled when it has none. `ClientState` keys (WP-E1) are a snapshot of what the page showed at the
end of the action: `toast.<success|warning|error|info>` (the last toast of that type), `toasts`, `dialogs` (prompt
messages).

`macro_run` clicks Run on a saved macro's dashboard card, adding it through the card picker if needed;
`shortcut_run` opens the Control Deck's
Shortcuts drawer and clicks Execute on a built-in shortcut. Browser runs use the saved shortcut parameters.
Nonempty REST parameter overrides are unsupported in the browser client, because the drawer has no inputs
for them. System shortcuts cover beep on/off, panel lock/unlock and all five LCD device codes, each starting
from a different device value. Rejected beep, lock and LCD writes require unchanged state and failure feedback;
the fixture's disabled reboot must send no matrix command. LCD timing and an enabled reboot still need
separate proof. These scenarios check simulator readback or CEC command counts and the visible success/error toast;
rejection cases verify that the device state stays unchanged and no success toast appears.

**The `uc` client** (`clients/uc.py`, WP-B1) connects like a Remote 3 (authenticate, `connect`, subscribe every entity) and maps intents to entity commands: `route` → `media_player.output_N` `select_source` with the name from the entity's source list, `preset_recall` → `button.preset_N` `push`, `matrix_power` → `switch.matrix_power`, `cec_input`/`cec_output` → `remote.input_N_cec`/`remote.output_N_cec` `send_cmd` (`power_on` → `POWER_ON`), and `uc_command` for any other entity command. A driver that drops the connection is a result, recorded with its close code (`requests[].closed`), not a blocked run; the next action reconnects. Its scenarios are in `tests/validation/scenarios/remote.py`; the protocol and lifecycle cases (setup, standby, outages, renames, the golden entity set) are the pytest suite `tests/uc`.

**The `browser` client as an observer** (WP-C2): besides the per-action pages, it keeps one `/ui` page and one `/kiosk` page open for the whole run, like screens on a wall. After they load, their status reads (`/api/status*`, the kiosk's 5 s poll) still reach the hub, but the answers are stripped of all matrix state, so anything they show later can only have come over `/ws`. `ClientState` keys: `ui.route.N` (the input the grid shows for output N), `ui.input.N` / `ui.output.N` (status colour: `signal`, `cable`, `disconnected`, `unknown`), `ui.input_name.N`, `ui.header` (`connected`/`disconnected`), `kiosk.route.N`, `kiosk.input.N`, `kiosk.status` (`Connected`/`Disconnected`). Scenarios: `tests/validation/scenarios/live.py`.

**The `ha` client** (`clients/ha.py`, WP-D1) runs a real Home Assistant: it creates a container from a pinned
`homeassistant/home-assistant` image (`VALIDATE_HA_IMAGE` overrides it; `homeassistant/home-assistant:2025.1.4` checks
the minimum version, D8), copies a minimal `configuration.yaml` and `custom_components/hdmi_matrix` into `/config`
(`docker cp`, nothing is bind-mounted), maps `host.docker.internal` to the Docker host (`host-gateway`, where the hub
listens on all interfaces) and onboards Home Assistant through `/api/onboarding`. Scenario `ha.config_flow` adds the hub
through `/api/config/config_entries/flow` like the UI does and sets a 5 s polling interval through the options flow.
Intents become service calls over the WebSocket API (`route` -> `select.select_option` with the input's name from the
entity's options, `preset_recall` -> `button.press`, `matrix_power` / `output_mute` / `output_setting` `enable` ->
`switch.turn_on/off`, `cec_*` -> `hdmi_matrix.send_cec_command`, `ha_service` -> any service, `ha_reconfigure` -> the
reconfigure flow); the result maps to 200 / 400 (validation error) / 404 / 500 (Home Assistant error) for `Response`.
`ClientState` keys: `<platform>.<unique-id suffix>` (`select.output_1_source`, `@attr` for an attribute),
`device.<field>`, `entry.<field>`, `log.errors`. The Home Assistant log is saved as `logs/home-assistant.log`.
Scenarios: `tests/validation/scenarios/home_assistant.py`.

## Recorded baseline (C-pre, 2026-09-25)

WP-C4 adds browser intents `scene_wait_edit` (edit, prompt for a duration, save)
and `scene_conflicts` (open a saved scene and read its real conflicts). Browser
observations `scene.conflict_count` and `scene.values` come from the visible
conflict rows. `CommandGap(before, after, seconds)` checks simulator command
timestamps, so a wait is proven by the pause between device writes. Fault
`reject_write_count` scopes `reject_writes` to the next N writes; `comheads`
can limit it to CEC while subsequent commands succeed.

To prove a flow against the shipped Docker image, start an isolated simulator
and hub container with the seeded `tests/e2e/fixtures/data`, then use
`run --target sim --sim-control-url <control URL> --hub-url <hub URL>
--hub-image-digest <docker image inspect ID> --client browser --record`.
The runner resets that **disposable simulator** between scenarios. It does not
start or stop those external containers, and cannot switch them to UC mode.

`current` in `features.yaml` was set from the proof that existed before this framework, and set conservatively:

- **V1** for unit and mocked tests, for driver-level simulator tests (a real `OreiMatrix` against the simulator, with no user interface in the path), and for visual baselines (screenshots only).
- **V2** where `tests/sim/test_sim_e2e.py` drives REST, the real hub and the simulator, and asserts the device state.
- **V3** where `tests/e2e/smoke.spec.ts` asserts the effect from a browser.
- **V0** where a test is a strict xfail that proves the feature broken, or where nothing exists.

The home assistant tests use `aioclient_mock`, so they give V1 at most. Scenario evidence added since then shows up in the ledger's Level column next to the recorded baseline.
