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
  records `launch.effective.model: null`, so the control plane does **not** attest a
  model; the coordinator's pinned route (`minimax-coding-plan/MiniMax-M3/thinking`)
  is the only authority for it. The OpenCode model catalogue does expose
  `minimax-coding-plan/MiniMax-M3` with variants `none` and `thinking`; the
  neighbouring `MiniMax-M3.1-Flash` entry was **not** used and no variant was
  substituted. No Anthropic/Claude, no broker alias, no nested helper or subagent.
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
| Simulator | `tools/simulator/server.py:665-683` (`POST /_sim/event`: cable/signal/push), `tools/simulator/README.md:73,80` (`PATCH /_sim/state`, `POST /_sim/event`), `tools/validate/device.py:117-123` |
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

Every one of these records holds exactly four observer messages
(`connected`, `status`, `status`, and the one change event) and every one of them
carries exactly one behavioural WS check plus the schema check.

## The distinctions the intake was asked to keep apart

- **True device-poller change** - the matrix changed by itself and the hub's
  scheduled read noticed it: `live.front_panel_route`, `live.input_signal`,
  `live.rename_elsewhere`. These actions are `act("device_change", patch=...)`,
  executed by the runner directly against the simulator
  (`tools/validate/runner.py:796-813` -> `PATCH /_sim/state`), so nothing goes
  through the hub.
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
asserted behaviourally**. This is exactly the "a connection or schema pass alone is
not complete behavioural proof" boundary, and it applies to every WS record in the
repository.

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
connect `status` and the `get_status` `status` in **every** scenario (visible as
the four `ws_events` of the original `live.front_panel_route` record). What is
missing is an **expectation surface** that can address them, and a way to
**command** the WS from a scenario.

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

Blast radius: every scenario's evidence record changes shape and
`ws_contract_check` must keep tolerating control frames. That is a
whole-suite change, which is precisely why it needs its own serial lease, its own
child scope and its own different-family review, and why it must not be smuggled
into this unit.

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
- The four-message `ws_events` quoted for `live.front_panel_route` and
  `power.standby` come from the **existing committed records**, not from a new
  run; their original SHAs and `dirty: false` state are reported as found.
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
