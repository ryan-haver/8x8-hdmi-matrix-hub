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
python -m tools.validate run --feature F-MTX-001                # only scenarios that prove this feature
python -m tools.validate run --scenario presets.recall --client browser
python -m tools.validate ledger --evidence build/validation/evidence --run-summary build/validation/run-summary.json \
                                --out build/validation/LEDGER.md
python -m tools.validate check  --evidence build/validation/evidence --run-summary build/validation/run-summary.json
python -m tools.validate ledger                                 # regenerate docs/validation/LEDGER.md (committed evidence only)
```

`run` writes to `build/validation/` by default: `evidence/` (records plus screenshots next to them), `logs/` (hub and simulator logs), and `run-summary.json`. `--record` writes the records into `docs/validation/evidence/` so you can commit them at a milestone.

**Simulator target (`--target sim`, the default).** The runner starts the simulator (`python -m tools.simulator`) and the real hub (`run.py`, modular API-only mode, the same way as `tools/dev_stack.py`) on free ports. The hub data is a fresh copy of `tests/e2e/fixtures/data` (profiles, macros, scenes and so on). Before each scenario, the simulator is reset to its seed state through `PUT /_sim/state`. The hub keeps its session because `/_sim/reset` would trigger BE-04. After a fault-injection scenario the hub is restarted.

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
| sim | `browser` (Chromium drives the shipped web UI), later `ha`, `uc`, `flic` | V3 |
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
- **Expectations:** `Device` / `DeviceUnchanged` (device state), `CommandSent` / `NoCommand` / `NoProtocolWarnings` (simulator command log; `n/a` on hardware), `Response` (the client's HTTP result), `Hub` (read back through the hub API, e.g. a name shown afterwards), `WsEvent` / `NoWsEvent` (what a `/ws` client received). `clients=("api",)` limits a check to one client.
- **Failure paths** are scenarios with `kind="failure"`, `faults={...}` (simulator fault injection, see `tools/simulator/README.md`) and `targets=("sim",)`.
- Scenarios that fail because of a known bug stay in. Link the finding on the failing check. If the bug is new, add it to `findings_pending.yaml` first.

## Adding a client

Subclass `tools.validate.clients.base.Client`. It needs `name`, the `intents` it can perform, `start(hub)`, `perform(action) -> ActionResult` and `stop()`. Register it in `clients/__init__.py`. Before each action the runner sets `client.context` (`label`, `forwarded_for`, `artifacts_dir`). The `ha`, `uc` and `flic` clients are placeholders that raise `NotImplementedError` naming their work package (WP-D1, WP-B1). A PASS with a real client counts as V3.

## Recorded baseline (C-pre, 2026-09-25)

`current` in `features.yaml` was set from the proof that existed before this framework, and set conservatively:

- **V1** for unit and mocked tests, for driver-level simulator tests (a real `OreiMatrix` against the simulator, with no user interface in the path), and for visual baselines (screenshots only).
- **V2** where `tests/sim/test_sim_e2e.py` drives REST, the real hub and the simulator, and asserts the device state.
- **V3** where `tests/e2e/smoke.spec.ts` asserts the effect from a browser.
- **V0** where a test is a strict xfail that proves the feature broken, or where nothing exists.

The home assistant tests use `aioclient_mock`, so they give V1 at most. Scenario evidence added since then shows up in the ledger's Level column next to the recorded baseline.
