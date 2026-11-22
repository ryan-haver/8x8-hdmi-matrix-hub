# SW-API-READ-03 intake record (report / evidence inventory)

Bounded intake for **F-API-039** (WS status snapshot), **F-API-040** (WS live matrix
events) and **F-API-042** (WS heartbeat), prepared under the existing P1/API-security
plan. This is an inventory of what the repository actually asserts today, what it
does not, and what a following implementation child would have to do. It is **not**
core source implementation, **not** a fresh feature qualification, and **not** the
completion of the SW-API-READ-03 unit.

## Authority and boundaries

- Task `task_abb0caba9fdf`, Dispatch `ctx_32f5f2ecfabe`, existing Run
  `run_37205f6095b3`; dispatched terminal `term_52b7a031-e38e-483d-84fd-2a56eed2614a`.
- Live Dispatch confirmed by `orca orchestration worker-show --dispatch
  ctx_32f5f2ecfabe --json`: `status: dispatched`, `depth: 1`, `hostScope: local`,
  `assigneeHandle: term_52b7a031-e38e-483d-84fd-2a56eed2614a`, worktree effect
  `reused` at `.../wp-api-read-03-intake`, `startOptions.agent: opencode2`. Orca
  records `launch.effective.model: null`, so the control plane does **not** attest
  an effective model. The configured route of record was
  `minimax-coding-plan/MiniMax-M3/thinking`; that configured pin alone is **not**
  independent proof of the model that actually answered and is not treated as
  such here. The effective-model evidence is a **separate coordinator export** of
  the original native session `ses_e7b4c6d4affe8DcdYrsP51cVwD`, which the
  coordinator reports to show all **85** assistant turns on
  `M3/minimax-coding-plan/thinking`; this intake did **not** run that export and
  does not restate it as a check of its own. The OpenCode model catalogue does
  expose `minimax-coding-plan/MiniMax-M3` with variants `none` and `thinking`; the
  neighbouring `MiniMax-M3.1-Flash` entry was **not** used and no variant was
  substituted. No Anthropic/Claude, no broker alias, no nested helper or subagent.
  This attribution is **not** a core/security-review qualification for the author
  or for any later reader.
- Worktree
  `C:/Users/ryanh/orca/workspaces/unfoldedcircle-orei-hdmi-matrix-integration/wp-api-read-03-intake`,
  branch `ryan-haver/wp-api-read-03-intake`, `HEAD` =
  `d6e78e0b6ab1dab5216443584d810a7a24af32b2`,
  which is the exact prepared worker base. `git rev-parse --abbrev-ref HEAD` and
  `git rev-parse HEAD` were the commands used.
- Entry head: `git -C C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration rev-parse
  wp-runtime-completion` -> `e16ec6af4d13c76c7024d42b605afec0c8ae9bf4`; and
  `git merge-base --is-ancestor d6e78e0b6ab1dab5216443584d810a7a24af32b2
  e16ec6af4d13c76c7024d42b605afec0c8ae9bf4` exited **0**, so the pinned base is a
  published ancestor of the entry head. Remote: `origin
  https://github.com/ryan-haver/8x8-hdmi-matrix-hub.git`. The branch has **no**
  upstream; nothing was pushed.
- Exclusive writes actually used: the new `docs/production/software-waves/SW-API-READ-03/INTAKE.md`
  and the new ignored `build/software-waves/SW-API-READ-03-intake/**`.
- Read-only and untouched: product source, tests, scenarios, client bridges, the
  runner, the validation model, the schema, shared fixtures, the canonical registry
  (`docs/validation/features.yaml`), the ledger, findings, manifests, lockfiles,
  historical evidence, baselines and private runtime data. No new test, no helper
  implementation, no record import, no service deployment, no push/merge/tag/cleanup,
  no root data access, no `tools.validate check`, no ledger generation.
- This record asserts **no** implementation, **no** qualification, **no** level
  promotion and **no** completion of SW-API-READ-03, and it infers **no** core or
  security review competence for itself or for any future author of this unit.

## Sources actually inspected

| Area | Anchors |
| --- | --- |
| WS endpoint | `src/rest_api/websocket.py:26` (`HEARTBEAT_SECONDS = 30.0`), `:67` (`web.WebSocketResponse(heartbeat=...)`), `:94-111` (`_handle_command`), `:114-124` (`_reply_status`) |
| Event stream / poller | `src/rest_api/events.py:154-169` (`add_client`: welcome -> snapshot -> `request_poll`), `:224-245` (`status_snapshot`, `_send_snapshot`), `:274-295` (poll wake/settle), `:313-319` (`refresh`), `:321-349` (`poll_once`), `:367-400` (`_follow`, matrix listeners), `:420-449` (`_apply` diffing + "first reading" snapshot), `:451-545` (per-field publishers) |
| Contract | `docs/api/WEBSOCKET.md:24,26,28,43`; `docs/api/websocket.schema.json` (`$defs.status`, `$defs.pong`, `$defs.output_name_change`, ...) |
| Runner | `tools/validate/runner.py:62-79` (`ws_contract_check`), `:202-291` (`WsObserver`), `:584,610,613,647` (observer lifecycle and the action mark), `:674-675` (the only unconditional WS check), `:796-813` (`_device_change`), `:972-986` (`WsEvent` / `NoWsEvent`) |
| Model / expectations | `tools/validate/model.py:199` (`RUNNER_INTENTS`), `:400-418` (`WsEvent`, `NoWsEvent`), `:424-494` (`Scenario`) |
| Scenarios | `tests/validation/scenarios/live.py:25-113`, `power.py:7-25`, `outputs.py:7-44`, `matrix_status.py:164`, `_paths.py:4-22` |
| Registry | `docs/validation/features.yaml:4803-4820` (F-API-032), `:4905-4916` (F-API-039), `:4917-4934` (F-API-040), `:4948-4960` (F-API-042); `tests/validation/test_registry.py:90-98` (symmetry) |
| Simulator | `tools/simulator/server.py:665-683` (`POST /_sim/event`: cable/signal/push), `tools/simulator/README.md:73,80-81` (`PATCH /_sim/state`, `POST /_sim/event` for cable and signal), `tools/validate/device.py:117-123` |
| Browser client | `web/js/websocket.js:11-19,178-185` (25 s `{command:'ping'}`), loaded by `web/index.html:677` and `web/kiosk.html:1525`; second copy `web/js/core/ws.js:14-20,199-205` |

---

# F-API-039 - WS status snapshot (after connect, after a first reading, get_status)

## Registry claim vs. actual assertions

`docs/validation/features.yaml:4905-4916`: `ws: [status]`, target V2, current V2,
`evidence: []`, `scenarios: []`. The basis names two simulator tests and
`tests/sim/test_sim_status_broadcast.py`, and adds that "every scenario's observer
receives the snapshot and the runner checks it against the schema".

What the source actually does:

- Connect snapshot: `src/rest_api/events.py:154-169` sends `connected` first, then a
  `status` snapshot if the hub already has one, and otherwise asks for a poll so the
  snapshot follows (`events.py:224-245` builds it from the last complete read).
- Requested `get_status`: `src/rest_api/websocket.py:106-109` -> `:114-124` reads the
  matrix fresh and answers `status`, or `error` ("Matrix status not available") when
  the read fails.
- "after a first reading": `src/rest_api/events.py:436-449` - a value the hub learns
  for the first time is **not** a change event; every client gets a fresh `status`
  snapshot instead.

What is actually asserted today (test-only, no scenario, no evidence record):

| Assertion | File | What it proves |
| --- | --- | --- |
| welcome `protocol == 1`, `matrix.connected is True`, snapshot `routing` equals the simulator routing, `outputs_detail[:2]` names are the real names (BE-31), `connected is True` | `tests/sim/test_sim_ws_contract.py:281-292` | the connect welcome + the connect snapshot, real hub app + simulator, schema-checked |
| `get_status` reply carries `input_names["2"] == "AppleTV"` | `tests/sim/test_sim_ws_contract.py:295-303` | the requested snapshot reply, schema-checked |
| the connect snapshot carries the real names; three warm-cache reads send **no further** `status`; nothing is named "Output N" | `tests/sim/test_sim_status_broadcast.py:49-66` | the connect snapshot and the absence of re-broadcast (WP-E1 / BE-31) |
| first read -> one snapshot with `cableConnected: None`; Telnet cables learned -> **no** `cable_change` and a **second** snapshot with the real values; a later real change -> exactly one `cable_change` | `tests/test_hub_events.py:77-92` | the "after a first reading" clause - but only at **unit** level with a `FakeWs`, not with a real client |
| `get_status` answers the hub's status snapshot | `tests/test_rest_api.py:890-898` | V1, mocked matrix |

Not asserted anywhere:

- The **second** snapshot of the "after a first reading" clause is proven only by a
  fake WebSocket. No real hub app + simulator assertion shows a real client
  receiving a *second* snapshot when the hub learns a value for the first time.
  `test_sim_status_broadcast.py` pins the *first* snapshot and the *absence* of
  re-broadcast, not the second snapshot.
- The refusal paths of the `get_status` contract (`src/rest_api/websocket.py:121-122`
  -> `error`) and the command error paths (`:98` invalid JSON, `:100` non-object,
  `:111` unknown command) have **no** assertion in any test.

## Disposition: PRESERVE + MISSING-SUPPORT (attribution). No defect found.

- **Preserve**: the simulator and unit assertions above are real, current and
  correct. They must not be duplicated, and they must not be re-labelled as
  scenario evidence.
- **Actual defect**: none reproduced. Nothing in the inspected source contradicts
  the contract, and the rerun of the existing basis passed unchanged.
- **Mapping / attribution**: no discoverable scenario attributes this feature
  (`scenarios: []`, `evidence: []`). `docs/validation/EV01_EVIDENCE_RECONCILIATION.md:166`
  already recorded disposition 3 for exactly this reason; this intake confirms and
  sharpens it rather than superseding it.
- **Missing support**: see "The boundary analysis" - no runner expectation can
  currently address the connect snapshot or the `get_status` reply.
- **Registry overlap to note (coordinator-owned)**: `F-API-032`
  (`docs/validation/features.yaml:4803-4820`) already claims `connected`, `status`,
  `matrix_connection` and `error` with scenario attribution and five evidence
  records. F-API-039 claims `status` only, and its distinguishing content is the
  snapshot's *content* and the "first reading" behaviour, which F-API-032's
  evidence does not establish. The two rows should not be collapsed by the
  coordinator without deciding which one owns the snapshot content.

---

# F-API-040 - WS live matrix events from the hub's own poller

## Registry claim vs. actual assertions

`docs/validation/features.yaml:4917-4934`: `ws: [routing_change, power_change,
signal_change, connection_change, cable_change, audio_mute, input_name_change,
output_name_change]`, `telnet: ['push: hdmi input|output N: connect|disconnect']`,
target V2, current V2, `findings: [BE-24]`, five evidence records, `scenarios:
[live.front_panel_route, live.input_signal, live.display_unplugged,
live.rename_elsewhere, power.standby]`.

All publishers are in `src/rest_api/events.py:451-545`; the poll that drives them
is `events.py:321-349` with the wake/settle logic at `:274-295` and the matrix
event listeners at `:367-400`.

## Event-by-event inventory (scenario -> client -> cause -> record)

The five scenarios the registry names for F-API-040 are `live.front_panel_route`,
`live.input_signal`, `live.display_unplugged`, `live.rename_elsewhere` and
`power.standby`. Two further scenarios prove two of the same events under
**other** feature rows (F-API-033 and F-API-036), which is why the interface list
above overlaps other rows.

| Event | Scenario | Row(s) the record attributes | Client | Cause of the change | Original record |
| --- | --- | --- | --- | --- | --- |
| `routing_change` | `live.front_panel_route` | F-MTX-031, F-REL-012, **F-API-040**, F-UI-024, F-KIO-010 | browser | **device-side** (front panel) | `docs/validation/evidence/runtime-r8b/F-MTX-031/2026-10-19-V3-1baac3de-live.front_panel_route-browser.json` - V3, pass, source `1baac3dec660f41345869c126cfca94d6731c5a0`, `dirty: false` |
| `routing_change` | `routing.switch_one` | F-MTX-001, F-API-005, **F-API-033** | api | REST write | `docs/validation/evidence/runtime-r8b/F-MTX-001/2026-10-19-V2-1baac3de-routing.switch_one-api.json` - V2, pass, source `1baac3dec660f41345869c126cfca94d6731c5a0`, `dirty: false` |
| `signal_change` | `live.input_signal` | F-MTX-031, **F-API-040**, F-UI-024, F-KIO-010 | browser | **device-side** | `docs/validation/evidence/runtime-r8b/F-MTX-031/2026-10-19-V3-1baac3de-live.input_signal-browser.json` - V3, pass, same source SHA |
| `connection_change` | `live.display_unplugged` | F-MTX-031, **F-API-040**, F-UI-024 | browser | **Telnet push** | `docs/validation/evidence/runtime-r8b/F-MTX-031/2026-10-19-V3-1baac3de-live.display_unplugged-browser.json` - V3, pass, same source SHA |
| `cable_change` | `live.display_unplugged` | as above | browser | **Telnet push** | same record |
| `input_name_change` | `live.rename_elsewhere` | F-MTX-031, **F-API-040**, F-UI-024 | browser | **device-side** | `docs/validation/evidence/runtime-r8b/F-MTX-031/2026-10-19-V3-1baac3de-live.rename_elsewhere-browser.json` - V3, pass, same source SHA |
| `power_change` | `power.standby` | F-MTX-006, F-API-009, **F-API-040** | api | **REST write** (`POST /api/power/off`) | `docs/validation/evidence/F-MTX-006/2026-10-04-V2-7dbc4dc7-power.standby-api.json` - V2, pass, source `7dbc4dc70c70610f5e7f0f9becff1c0b7c3c8f23`, `dirty: false` |
| `audio_mute` | `outputs.audio_mute` | F-MTX-007, **F-API-036** | api | **REST write** | `docs/validation/evidence/F-MTX-007/2026-10-04-V2-7dbc4dc7-outputs.audio_mute-api.json` - V2, pass, source `7dbc4dc70c70610f5e7f0f9becff1c0b7c3c8f23`, `dirty: false` |
| `audio_mute` (refusal control) | `outputs.audio_mute_rejected` | F-REL-008, F-API-036 | api | refused write | `docs/validation/evidence/F-REL-008/2026-10-04-V2-7dbc4dc7-outputs.audio_mute_rejected-api.json`; the check is `NoWsEvent("audio_mute", timeout=3)` at `tests/validation/scenarios/outputs.py:26-44` |
| **`output_name_change`** | **none** | - | - | - | **no assertion in any test or scenario** |

The observer messages and the behavioural WS checks are **not** uniform across
these records. The counts below are read from each record's
`observations.ws_events` list and `checks` array - there is **no** top-level
`ws_events` key in these records. A record's `t_ms` is the message's own offset
from the action mark (`tools/validate/runner.py:760`), so a negative `t_ms` is
a message recorded **before** the action and a non-negative one **after** it;
that split agrees with the `events after the action: [...]` detail of the
behavioural checks in every record listed here.

| Record | `observations.ws_events` | Before the action | After the action | Behavioural WS checks | Schema check |
| --- | --- | --- | --- | --- | --- |
| `live.front_panel_route` | 4 | `connected`, `status`, `status` | `routing_change` | 1 (`routing_change`) | `4 message(s) checked` |
| `live.input_signal` | 5 | `connected`, `status`, `routing_change`, `status` | `signal_change` | 1 (`signal_change`) | `5 message(s) checked` |
| `live.display_unplugged` | 6 | `connected`, `status`, `signal_change`, `status` | `cable_change`, `connection_change` | 2 (`cable_change` **and** `connection_change`) | `6 message(s) checked` |
| `live.rename_elsewhere` | 6 | `connected`, `status`, `cable_change`, `connection_change`, `status` | `input_name_change` | 1 (`input_name_change`) | `6 message(s) checked` |
| `routing.switch_one` | 4 | `connected`, `status`, `status` | `routing_change` | 1 (`routing_change`) | `4 message(s) checked` |
| `power.standby` | 4 | `connected`, `status`, `status` | `power_change` | 1 (`power_change`) | `4 message(s) checked` |
| `outputs.audio_mute` | 4 | `connected`, `status`, `status` | `audio_mute` | 1 (`audio_mute`) | `4 message(s) checked` |
| `outputs.audio_mute_rejected` | 4 | `connected`, `status`, `audio_mute`, `status` | (none) | 1 (`no WebSocket event 'audio_mute'`) | `4 message(s) checked` |

A **behavioural** WS check is a check whose `description` names a `WebSocket
event ...` (or its negative form); the **schema** check is the one whose
`description` is `every WebSocket message follows
docs/api/websocket.schema.json` and whose detail is `N message(s) checked`. The
extra pre-action entries (`routing_change`, `signal_change`, `cable_change` /
`connection_change`, and the `audio_mute` with `{'output': 2, 'muted': false}`)
are messages the hub emitted during the setup window after the simulator reset,
**not** results of the scenario action, and none of them is asserted
behaviourally. These counts are **per record**: this intake makes no blanket
"four messages and one behavioural check" claim, for these records or for the
repository as a whole.

## The distinctions the intake was asked to keep apart

- **True device-poller change** - the matrix changed by itself and the hub's
  scheduled read noticed it: `live.front_panel_route`, `live.input_signal`,
  `live.rename_elsewhere`. The runner performs these actions itself, directly
  against the simulator (`tools/validate/runner.py:796-813` ->
  `tools/validate/device.py:117-123`), so nothing goes through the hub - but the
  simulator call **differs per scenario** and the difference must not be
  flattened:
  - `live.front_panel_route` and `live.rename_elsewhere` are
    `act("device_change", patch=...)` -> `PATCH /_sim/state`
    (`tools/validate/device.py:117-119`, `tools/simulator/README.md:73`): the
    simulator state changes silently, with **no** Telnet push;
  - `live.input_signal` is `act("device_change", event={"type": "signal", ...})`
    -> `POST /_sim/event` (`tools/validate/device.py:121-123`), whose `signal`
    branch only sets the simulator's input signal state
    (`tools/simulator/server.py:671-676`) and likewise **does not** push to
    Telnet.
  All three are device-side changes that the hub's poller observes, but only two
  of them are a simulator *state patch*; `live.input_signal` is a simulator
  *event*.
- **Telnet-push change** - a distinct trigger from the interval poll:
  `live.display_unplugged` sends `POST /_sim/event {"type":"cable"}`
  (`tests/validation/scenarios/live.py:63`), the simulator pushes
  `hdmi output 1: disconnect` to Telnet, and the hub reads at once
  (`src/rest_api/events.py:390`). This proves the *push* path, not the interval
  poll path; the registry row lists the Telnet push as an interface of its own.
- **REST-write-caused event** - `power.standby` and `outputs.audio_mute`. The
  *event* is still produced by the hub's read/diff, but the *cause* is the hub's own
  accepted write, and the read is triggered by that write. These must not be
  counted as proof that the hub notices changes made **behind its back**.
- The four original browser records confirm this split at the record level: in
  `live.front_panel_route` the observer's `procedure` reads "action (browser):
  device_change(patch={'outputs': {'1': {'source': 6}}})", while in
  `power.standby` it reads "action (api): matrix_power(on=False) -> POST
  /api/power/off -> HTTP 200".

## What the original records actually contain (and do not contain)

`live.front_panel_route` (V3, browser) holds **four** observer messages:
`connected`, `status`, `status`, `routing_change`. The only **behavioural** check
is `WebSocket event 'routing_change' with {'output': 2, 'input': 6, 'input_name':
'PS5'} | pass | events after the action: ['routing_change']`. The remaining check
is `every WebSocket message follows docs/api/websocket.schema.json | pass | 4
message(s) checked`. The welcome and the two snapshots are **captured but never
asserted behaviourally**. This is exactly the "a connection or schema pass alone
is not complete behavioural proof" boundary. The boundary is **structural, not a
count**: the schema check is appended unconditionally
(`tools/validate/runner.py:674-675`) and asserts only that each recorded message
matches the schema, so it holds for every record the runner produces - while the
**number** of observer messages and of behavioural checks differs per record, as
the table above shows.

## Disposition: PRESERVE + RERUN (already fresh) + MISSING-SUPPORT (one named gap). No defect found.

- **Preserve**: the four V3 browser records and the api V2 records are original,
  clean and correctly attributed. They must not be re-run-and-relabelled or
  duplicated.
- **Actual defect**: none reproduced.
- **Named coverage gap (registry claim vs. reality)**: `output_name_change` is
  listed in the F-API-040 interface list and in the schema, is published by
  `src/rest_api/events.py:463-465` and consumed by the Remote integration
  (`src/hub/integrations/hub_client_http.py:298`), but **no test and no scenario
  asserts it anywhere in the repository**. This is a gap in the *claim*, not a
  product defect. The simulator can inject it: `device_change(patch={"outputs":
  {"0": {"name": "..."}}})` makes the hub read `alloutputname` and diff it.
- **Two further cause gaps** (behaviour is proven, the *device-side cause* is not):
  `power_change` and `audio_mute` are only ever proven after a REST write.
- **Client-attribution gap**: every device-side F-API-040 event is attributed to
  the browser client only; the api client has no device-side F-API-040 scenario.
- **Control gaps**: "announced once, no optimistic event" is proven only by
  `tests/sim/test_sim_ws_contract.py:148-159` (test-only); the "no event when
  nothing changed" negative control exists only for `routing_change`
  (`tests/validation/scenarios/matrix_status.py:164`).
- **Support**: a scenario for all of the above is expressible with the **existing**
  shared contracts (`device_change` + `WsEvent` / `NoWsEvent` / `Device` /
  `DeviceUnchanged`). Nothing in `tools/validate/model.py` or
  `tools/validate/runner.py` has to change for F-API-040.

---

# F-API-042 - WS heartbeat (ping / pong)

## Registry claim vs. actual assertions

`docs/validation/features.yaml:4948-4960`: `rest: [GET /ws]`, `ws: [ping, pong]`,
target V2, current V2, `evidence: []`, `scenarios: []`.

Three different things must not be blurred:

1. **Application ping/pong.** `src/rest_api/websocket.py:103` reads
   `data.get("command", data.get("type"))`, so both `{"command": "ping"}` and the
   legacy `{"type": "ping"}` are answered with `pong` (`:104-105`). This is an
   application message and it is in the schema (`$defs.pong`).
2. **The protocol heartbeat.** `src/rest_api/websocket.py:26` sets
   `HEARTBEAT_SECONDS = 30.0` and `:67` passes it to
   `web.WebSocketResponse(heartbeat=...)`, so aiohttp sends a WebSocket **control
   PING frame** every 30 s and closes a client that has not answered within half of
   that (15 s). A control frame has no JSON body and is **not** covered by
   `docs/api/websocket.schema.json`, which describes JSON messages only.
   Contract text: `docs/api/WEBSOCKET.md:28`.
3. **The web client's own liveness probe.** `web/js/websocket.js:11-19,178-185`
   (shipped by `web/index.html:677` and `web/kiosk.html:1525`) sends
   `{"command": "ping"}` every 25 s and reconnects after 60 s of silence. That is a
   third thing again - a client-side probe, not the server's protocol heartbeat.

Actual assertions today (test-only, no scenario, no evidence record):

- `tests/sim/test_sim_ws_contract.py:322-333` - `{"command": "ping"}` -> `pong`;
  `{"type": "ping"}` -> `pong`; **no** `error` event; schema-checked.
- `tests/sim/test_sim_ws_contract.py:336-350` - monkeypatches
  `rest_api.websocket.HEARTBEAT_SECONDS` to **0.3 s**, connects with
  `autoping=False`, and asserts a `WSMsgType.PING` frame arrives and is answered
  with `ws.pong(...)`. This proves the *mechanism*, not the production 30 s
  interval, and it is explicitly **not** an elapsed production-duration soak.
- `tests/test_rest_api.py:882-888` - V1, mocked matrix.

## Disposition: PRESERVE + MISSING-SUPPORT (attribution). No defect found.

- **Preserve**: both simulator tests are real and current; the 0.3 s heartbeat
  control must keep its stated limit ("the mechanism, not the production interval,
  not a soak").
- **Actual defect**: none reproduced.
- **Mapping / attribution**: no discoverable scenario attributes this feature;
  `docs/validation/EV01_EVIDENCE_RECONCILIATION.md:167` already recorded disposition
  3 and the same "not a soak" caveat.
- **Missing support**: two distinct gaps, see below. The runner can neither *send*
  an application ping nor *see* the protocol heartbeat.

---

# The boundary analysis (why F-API-039 and F-API-042 cannot become scenarios yet)

Runner mechanics, from source:

- `tools/validate/runner.py:584` - an observer is created for **every** scenario,
  independent of the client.
- `:610` `await ws.start()`, `:613` `await ws.sync()`.
- `:647` `t_action = WsObserver.now()` - the action mark is taken **after** the
  observer connected and **after** `sync()` finished.
- `:253-275` `sync()` waits for a `status` message, marks `len(self.events)`,
  sends `{"command": "get_status"}` and waits for the `status`/`error` answer.
  **The `get_status` exchange therefore happens during setup, before `t_action`.**
- `:972-981` `WsEvent` matches `ws.since(t_action)`; `:982-986` `NoWsEvent` likewise.
- `:674-675` the only unconditional WS check is `ws_contract_check(ws.events)`
  (`:62-79`) - a **schema** check over every recorded message. It asserts nothing
  about which message is which, or what it contains.

Consequences:

1. **`WsEvent("status", ...)` cannot observe the connect snapshot or the
   `get_status` reply.** Both messages are recorded before the action mark, so the
   check sees an empty post-action window and fails. A `status` message that *does*
   arrive inside the action window is a different thing - for example the
   "learned a value for the first time" fresh snapshot
   (`src/rest_api/events.py:436-449`) - and must not be relabelled as the connect
   snapshot or as the answer to a request. Equally, an old buffered frame must
   never be counted as a current action result.
2. **Nothing in the runner sends `{"command": "ping"}`.** The only WS command the
   runner ever sends is `get_status`, inside `sync()`.
3. **The runner's observer cannot observe the server's protocol PING frames.**
   `WsObserver.start()` connects with `ws_connect(url, heartbeat=None)`
   (`tools/validate/runner.py:230`) and aiohttp's client, with its default
   `autoping=True`, answers a server PING with a PONG and **does not surface the
   frame** (aiohttp 3.13.3, `client_ws.py::ClientWebSocketResponse.receive`:
   `elif msg.type is WSMsgType.PING and self._autoping: await self.pong(msg.data);
   continue`). `WsObserver` also records only `WSMsgType.TEXT` (`:233`).

The data itself is not missing: the observer already records `connected`, the
connect `status` and the `get_status` `status` in **every** scenario - they are
visible in the original `live.front_panel_route` record, whose
`observations.ws_events` holds four entries (`connected`, `status`, `status`,
`routing_change`). The number is **not** four everywhere: `live.input_signal`
holds five and `live.display_unplugged` / `live.rename_elsewhere` hold six, and
some of those extra entries are pre-action carryover messages rather than setup
messages (see the table above). What is missing is an **expectation surface**
that can address the setup messages, and a way to **command** the WS from a
scenario.

---

# Answer: can existing support express named clean source-simulator evidence?

Two different answers, and the difference must be preserved:

- **As a discoverable, feature-attributed scenario + evidence record: NO for
  F-API-039 and F-API-042.** Not because the product behaviour is unproven - it is
  proven by current simulator tests - but because the runner's expectation surface
  cannot address the connect-phase messages or a client-initiated WS command, and
  the observer cannot see protocol control frames. Producing scenario-attributed
  records for these two features requires a **shared-contract change** in
  `tools/validate/runner.py` **and** `tools/validate/model.py`. Those files are
  coordinator-owned; this intake grants no lease and proposes the change only.
- **As a self-contained unit-test deliverable inside the unit's own writable path:
  YES.** `tests/validation/test_sw_api_read_03.py` can build the real hub app +
  simulator directly - the pattern `tests/sim/test_sim_ws_contract.py` already
  uses - and assert the welcome, the connect snapshot content, the `get_status`
  reply, the application ping/pong in both forms, the protocol PING frame, and the
  refusal controls. This needs **no** shared contract, **no** registry change and
  **no** new dependency. It yields a V2-level test result in the same form as the
  features' current basis - not a scenario/evidence record and not a level
  promotion.
- **For F-API-040: YES**, with the single caveat that `output_name_change` needs a
  new scenario but no new contract. Adding scenario ids to
  `docs/validation/features.yaml` is a **coordinator-owned** change (the symmetry
  test `tests/validation/test_registry.py:90-98` requires both directions), exactly
  as SW-API-READ-01 obtained one staged registry line by an explicit coordinator
  message. This intake requests that lease; it does not take it.

---

# Exact missing capability (if scenario attribution is wanted)

Minimal shared-contract delta - **not granted by this intake**:

1. `tools/validate/runner.py::WsObserver`
   - keep the connect-phase messages (the welcome and the first `status` snapshot)
     in a separately addressable bucket with their own marks, instead of one
     append-only list;
   - add a method to send an application WS command (`{"command": "ping"}`,
     `{"command": "get_status"}`) and to wait for the named reply using a
     **positional** mark - the pattern `sync()` already uses at `:267` - so an old
     buffered frame can never be counted as the reply;
   - optionally connect with `autoping=False` and answer PING frames manually so
     the server's protocol heartbeat becomes observable, with the consequence that
     the observer must answer within 15 s or the server closes it.
2. `tools/validate/model.py`
   - new expectation types addressing the connect phase and a requested reply
     (e.g. `WsConnect(event=..., data=...)`, `WsReply(command=..., event=...)`),
     plus a protocol-frame expectation if the protocol heartbeat is to be proven in
     a scenario.

Blast radius: **not established by this intake; it depends on the design that
is actually chosen.** An additional expectation/observation capability does
**not** by itself prove that every existing evidence record must change shape,
nor that protocol control frames must be fed to the JSON `ws_contract_check`:
the observer records only `WSMsgType.TEXT` frames today
(`tools/validate/runner.py:233`), so control frames never reach the check, and
`ws_contract_check` (`tools/validate/runner.py:62-79`) validates only the
recorded `{"event", "data"}` JSON messages against
`docs/api/websocket.schema.json`. Possible designs - a separately addressable
connect-phase bucket, a new observation channel for protocol frames, or a
change to how `ws_events` is serialised - and their compatibility risks are
**proposals** that need their own serial scope, their own coordinator lease and
their own different-family review. Old evidence, schema and record shapes must
be preserved unless a separate justification says otherwise. This correction
grants no shared-contract lease and no implementation.

# Proposed minimal child scope (proposed only; not started)

- NEW `tests/validation/scenarios/sw_api_read_03.py` (does not exist yet) -
  F-API-040 attributed to the api client: `output_name_change` (the named gap),
  device-side `power_change` and `audio_mute`, the "announced once / no optimistic
  event" control and the "no event when nothing changed" negative control - using
  existing expectations only.
- NEW `tests/validation/test_sw_api_read_03.py` (does not exist yet) - the
  F-API-039 / F-API-042 behaviour that no expectation type can express: welcome
  fields, connect snapshot content, `get_status` reply, application ping/pong in
  both forms, the protocol PING frame, and the refusal controls (unknown command
  -> `error`; invalid JSON -> `error`; `get_status` while the matrix read fails
  -> `error`).
- Coordinator-owned, one exact line each, requested not taken:
  `docs/validation/features.yaml` `scenarios:` for F-API-040 (and for F-API-039 /
  F-API-042 only if the shared-contract child lands and actually produces
  scenario records).

Controls the child must carry, so the result is not a connection/schema pass:

- **positive** - a device-side change produces exactly one event with the right
  payload, and the value reads back over REST and on the device;
- **refusal** - a refused write produces **no** success event and leaves the
  device unchanged (the `outputs.audio_mute_rejected` pattern,
  `tests/validation/scenarios/outputs.py:26-44`);
- **negative** - nothing changed on the device -> no event at all in the window;
- **honesty** - a missed event must fail rather than be relabelled, and the
  F-API-042 protocol-heartbeat observation must state in the record that a
  shortened heartbeat run is not a soak.

---

# Verification actually run

Commands, exits and counts. Python 3.12.10 and aiohttp 3.13.3 from the project
virtualenv `C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/.venv/Scripts/python.exe`.

1. `git rev-parse HEAD` -> `d6e78e0b6ab1dab5216443584d810a7a24af32b2`;
   `git branch --show-current` -> `ryan-haver/wp-api-read-03-intake`;
   `git worktree list`; `git remote -v`; `git rev-parse --abbrev-ref --symbolic-full-name '@{u}'`
   -> fatal (no upstream configured).
2. `git -C C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration rev-parse
   wp-runtime-completion` -> `e16ec6af4d13c76c7024d42b605afec0c8ae9bf4`;
   `git merge-base --is-ancestor d6e78e0b6ab1dab5216443584d810a7a24af32b2
   e16ec6af4d13c76c7024d42b605afec0c8ae9bf4` -> exit **0**.
3. `orca orchestration worker-show --dispatch ctx_32f5f2ecfabe --json` -> `ok`,
   `status: dispatched`, `depth: 1`, worktree `reused`, `agent: opencode2`,
   `launch.effective.model: null`.
4. `orca orchestration models` equivalent via the OpenCode model catalogue:
   `minimax-coding-plan/MiniMax-M3` present, variants `none`, `thinking`;
   `MiniMax-M3.1-Flash` present but not used.
5. Bounded rerun of the **existing** basis (regression check only, not a
   qualification):

   ```
   $PY -m pytest tests/sim/test_sim_ws_contract.py tests/sim/test_sim_status_broadcast.py \
       tests/test_hub_events.py -p no:tests.route_inventory -p no:cacheprovider -q -rA \
       --basetemp=build/software-waves/SW-API-READ-03-intake/targeted-tmp/cases
   ```

   exit **0**, **27 passed**, 0 failed, 0 skipped, 26.90 s. Environment isolated
   to the assigned build tree: `MATRIX_DATA_DIR`, `UC_CONFIG_HOME`, `TEMP`, `TMP`
   under `build/software-waves/SW-API-READ-03-intake/`, `PYTHONUTF8=1`. The
   route-inventory writer was disabled, so **no** canonical route report and **no**
   ledger artifact was produced or overwritten. Full output preserved at
   `build/software-waves/SW-API-READ-03-intake/targeted-01.log`.
6. Two bounded probes (read-only; they write only inside the assigned build tree):
   `build/software-waves/SW-API-READ-03-intake/probe_boundary.py`, log
   `probe-boundary.log`, result `probe-boundary-and-autoping.json`, exit **0**:
   - **Action-since boundary** (calls the real `Runner._check` with a stand-in
     observer): a `status` event received **before** the action mark -> `fail`
     (`detail: "events after the action: []"`); the same event **after** the mark
     -> `pass` (`"events after the action: ['status']"`).
   - **Protocol ping visibility** (real aiohttp server + real aiohttp client from
     the project venv, default `autoping=True`): `message_types_seen_by_the_client:
     []`, `ping_surfaced: false`, connection still open - the client answered the
     server PING internally and never surfaced the frame.

Preserved build artifacts (ignored, all under
`build/software-waves/SW-API-READ-03-intake/`): `targeted-01.log`,
`probe_boundary.py`, `probe-boundary.log`, `probe-boundary-and-autoping.json`,
`check_links.py`, `link-check.log`, plus the isolated
`build/software-waves/SW-API-READ-03-intake/data/`,
`build/software-waves/SW-API-READ-03-intake/config/`,
`build/software-waves/SW-API-READ-03-intake/temp/` and
`build/software-waves/SW-API-READ-03-intake/targeted-tmp/` scratch trees
(460 files).

## Honest limits of what was done

- No full core suite, no browser client, no hardware run, no image build, no
  72-hour soak, no field sign-off, and **no** `tools.validate` campaign was run.
  No evidence record was produced, imported or promoted; no ledger was generated;
  the registry and the ledger are untouched.
- The 27-test rerun is a **regression check of the existing basis**. It is
  V2-level test evidence only and changes no level anywhere.
- The observer-message counts quoted for `live.front_panel_route`,
  `power.standby` and the other records tabulated above come from the
  **existing committed records** (`observations.ws_events` and `checks`), not
  from a new run; their original SHAs and `dirty: false` state are reported as
  found.
- The boundary probe drives the real `Runner._check` with a stand-in observer and
  the autoping probe uses a real aiohttp server/client pair, but neither is a
  scenario run and neither is a substitute for one.
- Nothing here establishes hardware behaviour, a browser-client behaviour, a soak,
  or a release gate.

---

# Blockers and coordinator decisions requested

1. **Registry/ledger ownership.** `docs/validation/features.yaml` `scenarios:`,
   `evidence:` and the level rows for F-API-039/040/042, and the ledger, are
   coordinator-owned. This intake changed nothing and grants no lease.
2. **Scenario attribution for F-API-039 / F-API-042** needs the shared-contract
   change described above in `tools/validate/runner.py` + `tools/validate/model.py`.
   Until that child lands, the honest registry state stays `scenarios: []`, and it
   must not be back-filled with an unrelated scenario id.
3. **`output_name_change`** is claimed in the registry interface list with zero
   assertions anywhere. The coordinator should either accept the proposed child
   scenario or narrow the interface list; the intake does not decide.
4. **F-API-039 vs F-API-032 overlap** on `status` / `get_status` needs a
   coordinator decision about which row owns the snapshot content.
5. **A protocol-heartbeat scenario at the production 30 s interval** is a bounded
   heartbeat run of at least ~31 s. It is **not** a soak, and the 72-hour soak gate
   stays with the coordinator.
6. `docs/validation/EV01_EVIDENCE_RECONCILIATION.md:166-167` already carries
   dispositions 3 for F-API-039 and F-API-042. This intake confirms and sharpens
   them; it does not supersede that document, and it is not a new global
   reconciliation.
7. **Separate concerns, unchanged.** The qualified DeepSeek core-review quota
   remains unknown and that dispatch/acceptance remains held - it is not this
   intake's independent author or intake. No integration or qualification of
   unreviewed code is implied here.

## What this record does not claim

No implementation, no new test, no fresh qualification, no level promotion, no
completion of SW-API-READ-03, no core/security review competence, no product
defect (none was reproduced), and no change to any shared contract, registry,
ledger, manifest, lockfile, source file, test file or evidence record. The only
tracked change is this report.

---

# Correction note (prose-only, same original author family)

- **Provenance of the original report.** The report above was authored by the
  original MiniMax author family under Task `task_abb0caba9fdf` / Dispatch
  `ctx_32f5f2ecfabe` (existing Run `run_37205f6095b3`, terminal
  `term_52b7a031-e38e-483d-84fd-2a56eed2614a`) on branch
  `ryan-haver/wp-api-read-03-intake`, from base
  `d6e78e0b6ab1dab5216443584d810a7a24af32b2`, and was committed as
  `d3b41e1a4e081ef657e0d2a7146bc073ccc61a8b` - "docs(validation): record the
  SW-API-READ-03 WebSocket intake inventory". That writer's Dispatch completed
  and was released through Orca before its completion acknowledgement; this
  correction does **not** re-open it and does **not** replace or re-label its
  delivery.
- **Who corrected it.** This correction was written by the **same original
  MiniMax author family**, as the sole report writer, under the new Task
  `task_2fa50807fa72` / Dispatch `ctx_efb4ba56611d`, in the **same preserved
  worktree** `.../wp-api-read-03-intake` on branch
  `ryan-haver/wp-api-read-03-intake`, at exact base
  `d3b41e1a4e081ef657e0d2a7146bc073ccc61a8b`. No reset, no replacement writer,
  no nested helper, no new agent, no fallback route.
- **What changed** - prose only, four factual corrections, each verified
  against the current source and the committed record bytes rather than against
  the report's own asserted counts:
  1. the blanket "every record holds four observer messages and exactly one
     behavioural WS check" statement was replaced by a per-record table read
     from `observations.ws_events` and `checks`, with the pre-action /
     post-action split taken from each record's own `t_ms`
     (`tools/validate/runner.py:760`);
  2. the device-side cause distinction was corrected: `live.input_signal` uses
     `device_change(event=...)` -> `POST /_sim/event` (signal branch, no
     Telnet push), **not** `PATCH /_sim/state`; only `live.front_panel_route`
     and `live.rename_elsewhere` are simulator state patches;
  3. the shared-contract blast-radius paragraph was qualified into a
     design-dependent **proposal**; the claim that every existing evidence
     record must change shape, and that protocol control frames must be fed to
     the JSON `ws_contract_check`, is withdrawn as unproven;
  4. the model-provenance wording was corrected: a null CLI model/effort is
     correctly **not** a model override, a configured pin alone is not
     independent effective-model proof, and the coordinator's separate export
     of the original native session `ses_e7b4c6d4affe8DcdYrsP51cVwD` (all
     **85** assistant turns on `M3/minimax-coding-plan/thinking`) is
     attributed to the coordinator and was **not** re-executed here.
- **What did not change.** No implementation, test, tooling, source, scenario,
  runner, model, schema, registry, ledger, finding, manifest, lockfile,
  evidence record or probe/log byte was added, edited, re-labelled or
  overwritten; no original failed or successful probe was overwritten or
  re-labelled. The original `live.front_panel_route` example (four messages,
  one behavioural check) was already correct and is unchanged. The 27-test
  basis rerun, the two bounded probes and any campaign were **not** re-run for
  this prose-only correction and no result is claimed from them here. Nothing
  was pushed, merged, tagged or cleaned up. No qualification, unit completion
  or reviewer acceptance is claimed or implied by this correction: it is a
  prose correction of the original author's own report and nothing else.
- **Correction checks actually run**, all read-only against the repository and
  all writing only inside the ignored
  `build/software-waves/SW-API-READ-03-intake/correction-01/` tree: a
  record-inspection script that printed `observations.ws_events`, every check
  `description`/`detail` and the `t_ms` split for the eight records named
  above; a source re-read of `tools/validate/runner.py`,
  `tools/validate/device.py`, `tools/simulator/server.py`,
  `tools/simulator/README.md`, `src/rest_api/events.py` and
  `tests/validation/scenarios/live.py` for the cited anchors; the
  repository-relative path/link check; a UTF-8 and line-ending check; and
  `git -c core.whitespace=cr-at-eol diff --check`. The diff against
  `d3b41e1a4e081ef657e0d2a7146bc073ccc61a8b` touches this report only. The
  commit uses the documented invocation-only `git -c core.hooksPath= commit`
  exception for instruction-only maintenance (`docs/ORCHESTRATION_PROTOCOL.md`,
  `CONTRIBUTING.md`); no persistent hook setting was changed and **no** source
  or full-suite hook pass is claimed.
