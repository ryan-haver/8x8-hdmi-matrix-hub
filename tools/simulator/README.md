# BK-808 matrix simulator

A deterministic stand-in for the OREI BK-808 8x8 HDMI matrix, so the hub (REST API, web UI, kiosk, integrations) can be run and tested without hardware. This is simulator v1 from `docs/REMEDIATION_PLAN.md` §5.1. It was built from `docs/OREI_API_COMMANDS.md` and from what `src/orei_matrix.py` / `src/telnet_client.py` send and parse, then corrected against the real captures of a BK-808 with MCU V1.10.01 / web V2.00.03 (HIL Session 1, `tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/`, WP-A4): every read, the login, the Telnet banner and reads match byte for byte, and every probe and write answer (errors, rejected writes, unanswered commands, Telnet acknowledgements) matches too (`--report`: 0 contradicted). The setting commands the hub sends since WP-A4 part 2 come from the device's own web interface; they are implemented here but not captured on hardware yet (see [Replacing assumptions with HIL captures](#replacing-assumptions-with-hil-captures)).

It runs three listeners:

| Listener | Default | What it does |
| --- | --- | --- |
| Device HTTPS | `127.0.0.1:8443` | `POST /cgi-bin/instr` JSON commands, self-signed TLS, `text/plain` responses: compact JSON + CR LF (like the device) |
| Device Telnet | `127.0.0.1:2323` | the port-23 text protocol (`command!\r\n`): option negotiation and banner on connect, command echo, push notifications |
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
| `--captures DIR` | none | legacy: flat `<comhead>.json` response files applied on top of `--state` |
| `--golden DIR` | none | HIL-A capture folder (`tests/fixtures/device/<fw>/`): seed the state from it and answer with the captured bytes ([golden mode](#golden-mode-hil-a-captures)) |
| `--report` | off | with `--golden`: print which `ASSUMPTION(HIL-A)` guesses the captures confirm or contradict, then exit |
| `--user` / `--password` | from the state file (`Admin` / `admin`) | login credentials |
| `--no-tls` | off | plain HTTP device API |
| `--no-auth` | off | accept commands without a login |
| `--session-ttl SECONDS` | never expires | login session lifetime |
| `--reboot-seconds` | `5` | how long `reboot` keeps the device offline |
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

- Reads: `get video status`, `get output status`, `get input status`, `get cec status`, `get system status`, `get status`, `get network`, `get ext-audio status`. Key sets, key order and formatting are those of V1.10.01: `get output status` names the outputs in `name` and has no `allsource`; the per-output settings arrays and `get video status.allsource` have a ninth entry, the device web interface's "All Output" row: the common value of the 8 outputs, or 255 when they differ (HIL-04, `DeviceState.ninth`); HDR and scaler are device codes (HDR 0 = pass-through, scaler 0 = pass-through, 4 = audio only); `get system status.mode` is the LCD on-time code; `get video status.allname` are the preset names; `get ext-audio status.index` is the audio output set with `set ext-audio index`.
- Captured writes: `login` (wrong password: `result 0`), `video switch` (output `0` = all), `set poweronoff`, `set beep`, `set panel lock`, `set input name`, `set output name` (40 characters stored as sent), `set cec index` (only the 8-element array form; the single-port form is answered `result 0`, BE-13), `cec command` (only `object` is checked: any index and an empty port array get `result 1`), and the rejection of the old `set lcd on time {"time": N}`. Bad parameters get `result 0`.
- Web-UI-derived writes (what the hub sends since WP-A4 part 2; not captured on hardware yet): `tx stream`, `tx hdcp`, `set hdr conversion`, `set video scaler`, `set arc`, `set output audio mute` (`{key: [output, code]}`, output 0 = all), `set edid` (`[input, 1-47]`, 40-47 = copy from output 1-8), `set lcd on time` (`{"lcd on time": 0-4}`), `set ext-audio mode|out|index`, `ext-audio switch` (`[audio output, 1-16]`), `preset set` (an empty slot is answered `result 0`), `preset save`, `preset name`, `preset clear`, `reboot` (`{"reboot": 1}`).
- **Never answered**, like V1.10.01: any comhead the simulator does not know, a body that is not JSON (HIL-12), the unimplemented reads `get routing status` and `preset get` (HIL-01), and the commands the old hub sent (`set output stream|hdcp|hdr|scaler|arc|mute`, `set input edid`, `copy edid`, `set output exa*`, HIL-09). The request is held open until the client gives up, as the device does, and the log entry carries `"unanswered": true`. `Simulator(unanswered_comheads=...)` changes the set of *known* comheads that go unanswered: `frozenset()` answers the two reads (the capture-tool tests use this), and adding a comhead such as `"tx hdcp"` makes the device ignore it (the HIL-12 tests).

Unknown comheads are also logged as unrecognised. `tests/sim/test_sim_commands.py` scans `src/orei_matrix.py` and `src/telnet_client.py` and fails if the hub sends anything the simulator does not recognise (plan §5, L2).

**Telnet commands:** `status`, `r fw version`, `r type`, `r link in|out <n>` (`r link out 0` = all outputs), `r preset <n>`, `s cec in <n> <word>`, `s cec hdmi out <n> <word>`, `s output <n|0> in source <m>`, `s save|recall|clear preset <n>`, `s preset save|recall <n>`, `power <0|1>`, `s beep <0|1>`, `s lock <0|1>`, `reboot`. Every command line is echoed (`r link in 1!`) before the answer, as on V1.10.01. The banner (with the device's Telnet option negotiation), the `status` dump, `r fw version`, `r type`, `r link`, `r preset` (8 routing lines, or `preset N is none,please save a preset`), the routing/beep/lock acknowledgements and `power 0|1` (`power off`; `power on` plus the start-up text) use the captured wording. Captured error answers: `E00` for unknown commands (also an unknown CEC word, `s av`, `s out N stream`), `E01` for bad parameters (and `s power N`); `r preset 9` prints `E01` before the echo and `E00` after it. Cable events are pushed as `hdmi input|output <n>: connect|disconnect`.

## State files

`states/default.json` is the seed: inputs PS3, AppleTV, Computer, Switch, Shield, PS5, Analogue and Input 8; outputs TV, Soundbar and Output 3-8; TV and Soundbar connected; signal on inputs 2, 5 and 6; the Soundbar is in audio-only scaler mode (4, as the real device reports it). Device values follow the V1.10.01 capture: firmware V1.10.01, HDR 0 and scaler 0 (pass-through) on the other outputs, `mode` 3 and `baudrate` 6 (codes), the ninth array entry.

The format is grouped per port, so it is easy to edit by hand:

```json
{
  "schema_version": 1,
  "auth":    {"user": "Admin", "password": "admin"},
  "device":  {"model": "BK-808", "firmware_version": "V1.10.01", "type": "8x8 hdmi2.1 matrix", "...": "..."},
  "system":  {"power": 1, "beep": 1, "panel_lock": 0, "lcd_timeout": 3, "baudrate": 6},
  "inputs":  [{"name": "PS3", "edid": 36, "signal": 0, "cable": 1, "cec_enabled": 0}, "... 8 total"],
  "outputs": [{"name": "TV", "source": 2, "connected": 1, "stream": 1, "hdcp": 3, "hdr": 0, "scaler": 0,
               "arc": 1, "audio_mute": 0, "cec_enabled": 1, "ext_audio_enabled": 0, "ext_audio_source": 1}, "..."],
  "ext_audio": {"mode": 0, "index": 1},
  "presets": [{"name": "Apple TV", "routing": [2, 2, 2, 2, 2, 2, 2, 2], "saved": true}, "... 8 total"]
}
```

Missing keys fall back to defaults. Invalid values (wrong port counts, out-of-range modes, unknown keys) are rejected with the path of the bad field. Values are device codes: HDR 0-2, scaler 0-4, EDID 1-47, `lcd_timeout` 0-4 (reported as `get system status.mode`), `ext_audio_source` 1-16. Older state files may still carry `system.mode` (read as `lcd_timeout`) and `ninth_output` (ignored: the ninth entry is derived).

## In tests

`tests/sim/conftest.py` provides:

- `simulator`: a fresh instance per test on ephemeral ports.
- `matrix`: a real `OreiMatrix` pointed at the simulator, HTTP only.
- `matrix_with_telnet`: the same, with the real Telnet client connected.
- `make_simulator(golden_dir)`: build one yourself, optionally in golden mode. `tests/sim/test_golden_hub.py` overrides `simulator` with the real-capture golden simulator, so the real hub (HTTP, Telnet and REST) runs against the device's own bytes.

`SIM_GOLDEN=tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03 pytest tests/sim` runs the whole simulator suite in golden mode. Tests that assume the default seed (names, routing, cable states, CEC flags, preset routing) then fail by design; everything else must pass.

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

Everything the simulator guesses is marked `# ASSUMPTION(HIL-A)`. Run `grep -rn "ASSUMPTION(HIL-A)" tools/simulator` to list the guesses. Wire-level constants (result codes, login answers, session behaviour, Telnet banner and error codes, value wording) live in `protocol.py`, so most corrections are one-line edits there.

**Resolved by the V1.10.01 read capture (WP-A4).** Login success is `result: 1`; every read's keys, order and formatting (compact JSON + CR LF); `get output status` uses `name`; `get network` uses `subnet`; `get routing status` and `preset get` are never answered; the Telnet option negotiation and banner; the command echo; the `status` dump; and the `r fw version`, `r type`, `r link` and `r preset` answers. Their markers are gone; the registry entries stay, so `--report` keeps checking them against every capture folder. The report compares the capture's `***REDACTED***` values (MAC, hostname) as wildcards.

**Resolved by the probe and write captures (WP-A4 part 2).** The wrong-password answer (`result 0`), rejected writes (`result 0`), unknown commands and non-JSON bodies (no answer), names up to 40 characters, the single-port `set cec index` (rejected), what `cec command` validates, E00/E01, the Telnet routing/beep/lock acknowledgements, bare `power N`, standby behaviour, and the old hub's unanswered commands.

The open questions (the next write run with `tools/hil/README.md` "Verify the WP-A4 part 2 commands" answers most of them):

- The web-UI-derived writes: answer and read-back of each (`web-ui-commands`), LCD codes and wording (`lcd-codes`), `set edid` range and copy (`edid-range`, `copy-edid`), ext-audio (`exa-commands`, `ext-audio-index`), recall of an empty preset (`preset-set-empty`), the Telnet wording of every HDCP/HDR/scaler code (`output-mode-text`).
- A command without a session or after it expires, and the session lifetime (BE-04, HIL-14).
- The output CEC table on a real display and the Telnet output words (BE-14, `--include cec-live`); whether CEC commands need the port enabled.
- Preset acknowledgements over Telnet, push lines, what `reboot` answers before dropping off.

Every marker has an entry in `tools/hil/capture/assumptions.py`, and `tests/hil_tools/test_capture_catalog.py` fails if a marker is added without one, or if a registered marker disappears.

HIL-A workflow (plan §5.2; operator runbook in [`tools/hil/README.md`](../hil/README.md)):

1. Capture with `python -m tools.hil.capture --host <ip> --mode probe|read|write`. The records go to `tests/fixtures/device/<firmware>/`; the format is described in [`tests/fixtures/device/README.md`](../../tests/fixtures/device/README.md).
2. Run `python -m tools.simulator --golden tests/fixtures/device/<firmware> --report` to see which guesses the captures contradict, which need a human, and which have no evidence yet.
3. Correct `protocol.py` and the marked handlers until the report shows them as confirmed, then remove each `ASSUMPTION(HIL-A)` marker and its registry marker.
4. Add a contract test that loads the golden folder and compares simulator responses with the captures (see `tests/hil_tools/test_capture_golden.py` for the pattern). That is the §5 L2 exit criterion.

## Golden mode (HIL-A captures)

`python -m tools.simulator --golden tests/fixtures/device/<firmware>` (implementation and details in `golden.py`):

- **Seed.** The captured reads (routing, names, output settings, EDID, CEC, ext-audio, presets) and the Telnet cable and LCD lines overwrite the `--state` file. If a captured value is outside the simulator's ranges, the seed is skipped with a warning.
- **Byte-identical reads.** At start-up the simulator computes its own answer to each captured read for the seed state (the baseline). While its current answer still equals the baseline, it sends the captured body unchanged: same bytes, status and `Content-Type`.
- **State still moves.** Once a write (or `/_sim/state`, or an event) changes the state, the captured document is patched. Only the values that differ from the baseline are replaced, list elements one by one. Fields only the device sends keep their captured values, and the document is serialised in the device's JSON style. So routing, names and settings follow the writes, and device-only details such as extra keys, name prefixes and spacing survive.
- **Telnet.** The banner and every captured command (reads, set-command acks, error probes) are answered with the captured bytes. A read whose state changed falls back to the simulator's own text, because free text is not patched.
- **Login, no-session and writes.** The login success and wrong-password answers, the "not logged in" answer, and the write results by outcome (applied or rejected) come from the captures too.
- Anything not captured is answered as without `--golden`. The control API reports the golden folder in `GET /_sim/health`, and log entries served from captures carry `"golden": "verbatim"` or `"patched"`.

In code: `golden = GoldenSet.load(path); golden.seed(state); Simulator(state, golden=golden)`.
