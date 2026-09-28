# WebSocket contract (`/ws`, protocol 1)

The hub pushes live events to the web UI, the kiosk and any other client over `ws://<hub>:<API_PORT>/ws`. This document is the contract: every message, its payload and when it is sent. The machine-readable form is [`websocket.schema.json`](websocket.schema.json) (JSON Schema 2020-12). The tests check every received message against it: `tests/sim/test_sim_ws_contract.py`, and the validation runner in every scenario (`tools/validate/runner.py`, check "every WebSocket message follows ...").

Implementation: `src/rest_api/events.py` (event stream and status poller), `src/rest_api/websocket.py` (endpoint). Browser client: `web/js/websocket.js` (used by `web/js/app.js` and `web/kiosk.html`).

## Principles

1. **The hub owns the stream (UC-17).** Live events come from the hub itself, never from a client. A status poller reads the matrix every `STATUS_POLL_INTERVAL` seconds (default 5). It also reads at once when:
   - the matrix accepted a write, from any caller (REST, the Remote 3 integration, Home Assistant, Flic, scenes, shortcuts). A burst of writes (route to all, preset save) is read once, 0.15 s after the last write;
   - the matrix pushed an event over Telnet (a cable plugged or unplugged);
   - the matrix link went up or down.

   The poller runs in every mode (core only or with the Remote integration), whether or not a Remote or any WebSocket client is connected.
2. **Each change is announced once, whoever made it.** An event is the difference between two reads of the matrix. A route made through REST, the Remote, Home Assistant, Flic or the front panel produces the same single `routing_change`. The hub never announces a change before the matrix confirmed it: there are no optimistic events.
3. **Nothing is made up.** A value the matrix did not report, such as a failed read or routing input `0`, is "unknown". The hub keeps the last known value and announces nothing. A value read for the first time is not a change. When the hub learns something it did not know before a client connected (cables once Telnet is up, say), every client gets a fresh `status` snapshot instead.
4. **A slow client cannot stall the hub (API-09).** Each client has its own queue (256 messages) and writer. Publishing never waits. A client that does not take a message within 5 s, or falls 256 messages behind, is disconnected. It reconnects and resyncs from the snapshot.

## Connection

| Step | Direction | Message |
| --- | --- | --- |
| 1 | server → client | `connected` (always first) |
| 2 | server → client | `status` snapshot, as soon as the hub has read the matrix (at once if it already has) |
| 3 | server → client | change events, as they happen |
| any | client → server | `{"command": "ping"}` → `pong`; `{"command": "get_status"}` → `status` after a fresh read of the matrix (status caches bypassed); changes that read finds are announced to every client first, as usual |

**Heartbeat (API-10):** the server sends a WebSocket **protocol** ping every 30 s and closes a client that does not answer within 15 s. Browsers answer these pings by themselves. A client can also send `{"command": "ping"}` and gets `pong`. The form `{"type": "ping"}` that older web clients sent is accepted too. The web client pings every 25 s and reconnects if it has received nothing for 60 s.

**Reconnect:** clients reconnect for as long as they run, with a delay of 1 s that doubles up to 30 s. Every reconnect starts with `connected` and `status`, so a reconnect is also a full resync.

## Envelope

Every server message is one JSON object: `{"event": "<name>", "data": {...}}`. No other top-level keys. Port numbers are integers 1-8. Maps keyed by port (`routing`, `*_names`) use string keys `"1"`..`"8"`, because they are JSON object keys.

## Events

### Connection and state

| Event | Payload (`data`) | Sent |
| --- | --- | --- |
| `connected` | `message`, `client_count` (int), `protocol` (`1`), `matrix`: link | first message on every connection |
| `status` | the `/api/status` data plus `inputs` and `outputs_detail` (below) | after `connected` once the hub has read the matrix; in answer to `get_status` (after a fresh read); to every client when the hub learns a value for the first time (e.g. cables after Telnet came up) |
| `matrix_connection` | `connected` (bool), `state`, `host` | the matrix link went up or down, or changed between `connected` and `degraded` (Telnet lost or back) |

**Link** (`matrix` in `connected`, the `/api/status` degraded answer and `matrix_connection`): `connected` (bool: HTTP commands can be sent), `state` (`connected` · `degraded` (HTTP up, Telnet down) · `connecting` · `backoff` (lost, waiting to retry) · `disconnected` · `not_configured`), `host` (string or null), and `configured` (bool) where given.

**`status` payload:** `connected`, `state`, `host`, `power` (`"on"`/`"off"`), `routing` (`{"1": 2, ...}`), `outputs` (the routing as an array, older clients), `input_names`, `output_names`, `preset_names` (`{"1": "..."}`), `inputs` (array of `{number, name, signalActive, inactive, cableConnected, sourceDetected, edid}`), `outputs_detail` (array of `{number, name, connected, cableConnected, enabled, muted, hdcp, hdr, scaler, arc}`). `cableConnected` is `null` while unknown (no Telnet). The port details carry the same names as `input_names`/`output_names` (BE-31).

### Matrix changes (from the event stream: any path)

| Event | Payload | Sent when the matrix reports |
| --- | --- | --- |
| `routing_change` | `output`, `input`, `input_name`, `previous_input` | an output shows another input |
| `power_change` | `power` (`"on"`/`"off"`) | the matrix went to standby or woke up |
| `signal_change` | `input`, `has_signal` (bool), `input_name` | a source's signal appeared or went away |
| `connection_change` | `output`, `connected` (bool), `output_name` | a display was detected or lost (hot-plug, `allconnect`) |
| `cable_change` | `type` (`input`/`output`), `port`, `connected` (bool), `name` | a cable was plugged or unplugged (Telnet detection) |
| `audio_mute` | `output`, `muted` (bool) | an output's audio was muted or unmuted |
| `input_name_change` | `input`, `name` | an input's name changed (hub name store or the matrix) |
| `output_name_change` | `output`, `name` | an output's name changed |

### Command outcomes (from the hub's REST handlers)

These say what a command through the hub did. The state it changed also arrives as matrix change events.

| Event | Payload | Sent |
| --- | --- | --- |
| `preset_recall` | `preset` | after the matrix accepted a preset recall |
| `preset_recall_failed` | `preset` | the matrix refused or did not answer a recall |
| `switch_failed` | `input`, `output` | a route (`POST /api/switch` with an output, or `POST /api/output/{n}/source`) failed |
| `switch_all_failed` | `input` | a route to all outputs failed |
| `cec_command` | `type` (`input`/`output`), `port`, `command` (`power_on`/`power_off`), `name` (inputs) | after the matrix accepted a CEC power command |
| `scene_execution_error` | `scene_id`, `scene_name`, `steps_completed`, `total_steps`, `error` | a scene stopped or had failed steps |

### Hub settings

| Event | Payload | Sent |
| --- | --- | --- |
| `device_settings` | `type` (`input`/`output`/`preset`), `number`, and the saved fields (`name`, `icon`, `color`, ...) | a port's or preset's hub-side settings were saved |
| `device_settings_full` | the full device settings document | a bulk settings update |

### Replies

| Event | Payload | Sent |
| --- | --- | --- |
| `pong` | `{}` | reply to `ping` |
| `error` | `message` | reply to invalid JSON, an unknown command, or `get_status` when the hub cannot read the matrix |

### Removed in protocol 1

`switch` and `switch_all` were optimistic, sent *before* the command, and the matrix grid route never sent one (VAL-05). They are replaced by `routing_change`, one per output that actually changed, whoever routed. `status_update` (the old `get_status` reply, raw device data) is replaced by `status`. The server's app-level `ping` message is replaced by protocol pings. Nothing ever sent `scene_recall`, `output_connection` or `status_update` broadcasts.

## Status over REST (`GET /api/status`)

`/api/status` answers **200 only with data the matrix reported**: `connected`, `state`, `host`, `power`, `routing`, `outputs`, `input_names`, `output_names`, `preset_names`.

Otherwise it answers **503** with `success: false`, an `error`, and the link in `data` (VAL-04). It never answers 200 with default names such as "Input 1…8" in place of the matrix's state:

| Situation | `error` | `data` |
| --- | --- | --- |
| no matrix configured | `Matrix device not configured` | `{configured: false, connected: false, state: "not_configured", host: null}` |
| link down | `Matrix not connected` | `{configured: true, connected: false, state: "backoff" \| "connecting" \| "disconnected", host}` |
| link up, but the status read failed | `The matrix did not answer the status read` | `{configured: true, connected: true, state, host}` |

Home Assistant turns any non-success into "unavailable" entities. The web UI keeps what it showed and marks the header disconnected (see below).

## What the web UI and kiosk do with it (UI-02)

`web/js/websocket.js` (`MatrixWebSocket`) connects, keeps the heartbeat, reconnects forever and tracks the matrix link from `connected.matrix`, `matrix_connection` and `status`. It hands every message to the page as `{type, data}`.

- **Web UI (`web/js/app.js`):** `status` → full state; `routing_change`, `signal_change`, `connection_change`, `cable_change`, `audio_mute`, `input_name_change`, `output_name_change` → that part of the state; `device_settings(_full)` → reload the hub's device settings; `preset_recall` → refresh; `*_failed` → ask for a fresh `status`. The header is green only while the WebSocket is up **and** the hub reports the matrix reachable. Its tooltip says which of the two is missing. `power_change`, `cec_command` and `scene_execution_error` are not shown yet (WP-E1).
- **Kiosk (`web/kiosk.html`):** the same shared client. `status`, `routing_change`, `signal_change`, `connection_change`, `cable_change` and the name events update the tiles. The status dot is "Connected" only while the WebSocket is up and the matrix reachable.

## Configuration

| Variable | Default | Effect |
| --- | --- | --- |
| `STATUS_POLL_INTERVAL` | `5` | Seconds between two status reads by the hub's poller (minimum 0.2). Writes, Telnet pushes and link changes trigger a read at once. |
