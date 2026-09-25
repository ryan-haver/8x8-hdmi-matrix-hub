# BK-808 matrix simulator

A deterministic stand-in for the OREI BK-808 8x8 HDMI matrix, so the hub (REST API, web UI, kiosk, integrations) can be run and tested without hardware. This is simulator v1 from `docs/REMEDIATION_PLAN.md` §5.1. It was built from `docs/OREI_API_COMMANDS.md` and from what `src/orei_matrix.py` / `src/telnet_client.py` send and parse. HIL-A captures from the real device will replace its guesses (see [Replacing assumptions with HIL captures](#replacing-assumptions-with-hil-captures)).

It runs three listeners:

| Listener | Default | What it does |
| --- | --- | --- |
| Device HTTPS | `127.0.0.1:8443` | `POST /cgi-bin/instr` JSON commands, self-signed TLS, `text/plain` responses (like the device) |
| Device Telnet | `127.0.0.1:2323` | the port-23 text protocol (`command!\r\n`), banner, push notifications |
| Control HTTP | `127.0.0.1:8444` | `/_sim/*`: state, fault injection, reboot, events, command log. It stays up while the device "reboots". |

## Quick start

```bash
pip install -e ".[dev]"          # needs the `cryptography` package for the TLS cert
python -m tools.simulator        # from the repo root
```

Options (`python -m tools.simulator --help`):

| Option | Default | |
| --- | --- | --- |
| `--host` | `127.0.0.1` | bind address |
| `--https-port` / `--telnet-port` / `--control-port` | `8443` / `2323` / `8444` | `0` = any free port |
| `--state FILE` | `tools/simulator/states/default.json` | seed state |
| `--captures DIR` | none | golden HTTP captures applied on top of `--state` |
| `--user` / `--password` | from the state file (`Admin` / `admin`) | login credentials |
| `--no-tls` | off | plain HTTP device API |
| `--no-auth` | off | accept commands without a login |
| `--session-ttl SECONDS` | never expires | login session lifetime |
| `--reboot-seconds` | `5` | how long `set reboot` keeps the device offline |
| `--log-level` | `INFO` | every command received is logged at INFO; unrecognised commands at WARNING |

## Running the hub against it

The whole stack (simulator + hub REST API + web UI on port 8080) in one command:

```bash
python tools/dev_stack.py              # then open http://127.0.0.1:8080/ui
python tools/dev_stack.py --api-port 8090 --data-dir .dev-data   # other port, keep hub data
```

`dev_stack.py` starts the hub through its real entry point, `run.py` in modular API-only mode. Hub data (profiles, scenes, settings) goes to a temp directory that is deleted on exit, unless you pass `--data-dir`. Ctrl+C stops both processes. Use it for local UI work and for the Playwright UI capture.

To run the two by hand (simulator already running with the defaults above):

```bash
# bash
USE_MODULAR=true UC_ENABLED=false MATRIX_HOST=127.0.0.1 MATRIX_PORT=8443 OREI_TELNET_PORT=2323 \
  MATRIX_DATA_DIR=.dev-data UC_CONFIG_HOME=.dev-data python run.py
```

```powershell
# PowerShell
$env:USE_MODULAR='true'; $env:UC_ENABLED='false'; $env:MATRIX_HOST='127.0.0.1'; $env:MATRIX_PORT='8443'; $env:OREI_TELNET_PORT='2323'; $env:MATRIX_DATA_DIR='.dev-data'; $env:UC_CONFIG_HOME='.dev-data'; python run.py
```

`MATRIX_PORT` was added to `run.py`'s modular mode for this; it previously always used port 443. `run_server.py --host 127.0.0.1 --matrix-port 8443` also works, but it has the duplicate-module problem BE-19, so some routes (v2 scenes) misbehave.

The hub accepts the simulator's self-signed certificate because `OREI_VERIFY_SSL` defaults to `false`.

`/_sim/reboot` and `telnet_refuse` are safe against a live hub: the Telnet client treats EOF as a dropped connection and reconnects with backoff (SIM-02 / BE-28, fixed in Phase 1).

## Control API (`http://127.0.0.1:8444/_sim/...`)

| Method & path | Body | Effect |
| --- | --- | --- |
| `GET /_sim/health` | | ports, TLS, sessions, Telnet clients, current faults, `rebooting` |
| `GET /_sim/state` | | full state document |
| `PUT /_sim/state[?as_default=true]` | state doc | replace the state (validated); `as_default` also makes it the reset baseline |
| `PATCH /_sim/state` | partial doc | deep merge; patch ports by index, e.g. `{"outputs": {"0": {"connected": 0}}}` |
| `POST /_sim/reset` | | back to the seed state; clears faults, sessions and the log |
| `GET /_sim/faults` | | current faults |
| `POST /_sim/faults` | fault fields | set faults (merged with the current ones) |
| `DELETE /_sim/faults` | | clear all faults |
| `POST /_sim/reboot` | `{"seconds": 3}` | both device listeners go offline, then come back; sessions are lost |
| `POST /_sim/sessions/expire` | | forget every login (the next command gets the "not logged in" answer) |
| `POST /_sim/event` | `{"type": "cable", "port_type": "output", "port": 1, "connected": false}` | (un)plug a cable: updates state and pushes `hdmi output 1: disconnect` to Telnet clients |
| | `{"type": "signal", "port": 3, "present": true}` | source signal on/off (`inactive` array) |
| | `{"type": "push", "line": "..."}` | send an arbitrary line to every Telnet client |
| `GET /_sim/log[?channel=http\|telnet&limit=N]` | | command log (passwords redacted); entries carry `recognised`, `mutated`, `warnings`, `fault` |
| `DELETE /_sim/log` | | clear the log |

### Faults

`POST /_sim/faults` with any of:

| Field | Effect |
| --- | --- |
| `latency_ms` | delay every HTTP and Telnet response |
| `http_status` | answer `/cgi-bin/instr` with this status (e.g. `500`) |
| `malformed_json` | send a truncated JSON body |
| `drop_http` | abort the TCP connection without answering |
| `hang_http` | never answer (the client times out); released when faults are cleared |
| `comheads` | list: apply the four HTTP faults above only to these comheads |
| `http_fault_count` | apply the HTTP faults to the next N matching requests, then clear them |
| `wrong_password` | reject every login, even with correct credentials |
| `reject_writes` | answer every write with `result: 0` and leave the state unchanged |
| `session_expired_style` | how "not logged in" looks: `json` (default), `html` (login page) or `http401` |
| `telnet_refuse` | accept Telnet connections and close them at once |
| `telnet_close_mid_command` | send half of the next response, then close |
| `telnet_silent` | read commands but never answer |
| `telnet_fault_count` | apply the two Telnet command faults to the next N commands only |

Example: make the next two status reads fail with HTTP 500:

```bash
curl -X POST localhost:8444/_sim/faults -H 'Content-Type: application/json' \
     -d '{"http_status": 500, "comheads": ["get video status"], "http_fault_count": 2}'
```

## What it implements

**HTTP comheads** (every one the hub sends, plus the documented extras):

- Reads: `get video status`, `get output status`, `get input status`, `get cec status`, `get system status`, `get status`, `get network`, `get ext-audio status`, `get routing status`, `preset get`.
- Writes: `login`, `video switch` (output `0` = all), `preset set`, `preset save`, `set poweronoff`, `set beep`, `set panel lock`, `set lcd on time`, `set input name`, `set output name`, `set output stream|hdcp|hdr|scaler|arc|mute`, `set input edid`, `copy edid`, `set cec index` (documented array shape and the hub's single-port shape, the latter flagged as BE-13), `cec command`, `set output exa mode`, `set output exa`, `set output exa in source`, `set reboot`.

Unknown comheads get `{"comhead": X, "result": 0}` and are logged as unrecognised. `tests/sim/test_sim_commands.py` scans `src/orei_matrix.py` and `src/telnet_client.py` and fails if the hub sends anything the simulator does not recognise (plan §5, L2).

**Telnet commands:** `status`, `r fw version`, `r type`, `r link in|out <n>`, `r preset <n>`, `s cec in <n> <word>`, `s cec hdmi out <n> <word>`, `s output <n|0> in source <m>`, `s av <in> <out|0>`, `s save|recall|clear preset <n>`, `s preset save|recall <n>`, `s power <0|1>`, `s beep <0|1>`, `s lock <0|1>`, `s out <n> stream <0|1>`, `reboot`. Unknown commands get `E00`, and bad parameters get `E01`. Cable events are pushed as `hdmi input|output <n>: connect|disconnect`.

## State files

`states/default.json` is the seed: inputs PS3, AppleTV, Computer, Switch, Shield, PS5, Analogue and Input 8; outputs TV, Soundbar and Output 3-8; TV and Soundbar connected; signal on inputs 2, 5 and 6; the Soundbar is in audio-only scaler mode.

The format is grouped per port, so it is easy to edit by hand:

```json
{
  "schema_version": 1,
  "auth":    {"user": "Admin", "password": "admin"},
  "device":  {"model": "BK-808", "firmware_version": "V1.10.02", "...": "..."},
  "system":  {"power": 1, "beep": 1, "panel_lock": 0, "lcd_timeout": 3, "mode": 0, "baudrate": 115200},
  "inputs":  [{"name": "PS3", "edid": 36, "signal": 0, "cable": 1, "cec_enabled": 0}, "... 8 total"],
  "outputs": [{"name": "TV", "source": 2, "connected": 1, "stream": 1, "hdcp": 3, "hdr": 3, "scaler": 1,
               "arc": 1, "audio_mute": 0, "cec_enabled": 1, "ext_audio_enabled": 0, "ext_audio_source": 1}, "..."],
  "ext_audio": {"mode": 0},
  "presets": [{"name": "Apple TV", "routing": [2, 2, 2, 2, 2, 2, 2, 2]}, "... 8 total"]
}
```

Missing keys fall back to defaults. Invalid values (wrong port counts, out-of-range modes, unknown keys) are rejected with the path of the bad field.

## In tests

`tests/sim/conftest.py` provides:

- `simulator`: a fresh instance per test on ephemeral ports.
- `matrix`: a real `OreiMatrix` pointed at the simulator, HTTP only.
- `matrix_with_telnet`: the same, with the real Telnet client connected.

```python
async def test_switch(matrix, simulator):
    await matrix.connect()
    assert await matrix.switch_input(6, 1)
    assert simulator.state.outputs[0].source == 6
```

Embedding it elsewhere:

```python
from tools.simulator import DeviceState, Simulator

async with Simulator(DeviceState.default(), https_port=0, telnet_port=0, control_port=0) as sim:
    print(sim.device_url, sim.telnet_port, sim.control_url)
```

## Replacing assumptions with HIL captures

Everything the simulator guesses is marked `# ASSUMPTION(HIL-A)`. Run `grep -rn "ASSUMPTION(HIL-A)" tools/simulator` to list the guesses. Wire-level constants (result codes, login answers, session behaviour, Telnet banner and error codes, value wording) live in `protocol.py`, so most corrections are one-line edits there. The main open questions are:

- Login success and failure `result` values. The success value is `"success"` per the doc, and the failure value is guessed as `"fail"` (BE-05).
- What a command gets without a session or after the session expires, and the session lifetime (BE-04).
- The `result` value of the unverified writes: beep, panel lock, EDID, and LCD.
- The `get output status` name field (`alloutputname` in the doc vs `name` per a hub comment), and the `get video status` name format (the hub strips an `IN01-` prefix).
- The `set cec index` single-port shape (BE-13), the output CEC table (BE-14), and the audio-only scaler code (BE-15).
- Telnet wording: banner, `status` dump lines, set-command acknowledgements, `E00`/`E01` meaning (BE-07), push lines, and whether bare `power N` works.
- Whether the device accepts commands in standby, and what `set reboot` answers before dropping off.

HIL-A workflow (`tools/hil/capture.py`, plan §5.2):

1. Store each raw read response as `tests/fixtures/device/<firmware>/<comhead with _ for spaces>.json`, for example `get_output_status.json`. Files starting with `_` are ignored, so keep notes there.
2. Seed the simulator from them with `python -m tools.simulator --captures tests/fixtures/device/V1.10.02` (or `DeviceState.apply_http_captures(load_capture_dir(...))`).
3. Correct `protocol.py` and the marked handlers so their responses match the captures, then remove the `ASSUMPTION(HIL-A)` marker.
4. Add a contract test that compares simulator responses with the captures (same keys, same types, and byte-identical for a state seeded from the same capture). That is the §5 L2 exit criterion.
