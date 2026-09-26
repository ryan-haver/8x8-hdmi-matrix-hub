# OREI BK-808 API Command Reference

This page lists the commands the hub sends to an OREI BK-808 HDMI matrix, what the device answers, and how sure we are. It separates what a real device has been **seen** doing from what is only expected.

## Communication Protocol

- **Endpoint**: `https://<ip>:443/cgi-bin/instr`
- **Method**: POST, JSON body (`{"comhead": "...", "language": 0, ...}`)
- **Answer**: `text/plain`; compact JSON (no spaces, fixed key order) followed by CR LF
- **SSL**: self-signed certificate (verify=False required)
- **Authentication**: `login` first. Sessions appear to be tracked per client IP (no cookie is set); whether reads need a login at all is still open (HIL-14).
- **Unknown commands get no answer at all.** The device accepts the request and never replies; the client times out. The same happens for a body that is not JSON. Right after such a request the web server can stall for one more request. The hub therefore treats a timeout on one command as a failed command and checks the link with a status read before it calls the matrix unreachable (HIL-12).

## Status legend

| Status | Meaning |
| --- | --- |
| ✅ **Verified** | A real device answered exactly this command. Captured byte-exact from a BK-808 with MCU V1.10.01 / web V2.00.03 (HIL Session 1, 2026-09-25, `tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/`). For writes: sent, answered and read back. |
| 🌐 **Web-UI-derived** | The command, payload and value codes the device's own configuration web interface uses. The hub sends it since WP-A4 part 2, the simulator implements it, but **no device answer has been captured yet**. Proof: the capture tool's write run (`tools/hil/README.md`). |
| ❌ **Not implemented** | Captured on V1.10.01: no answer (timeout) or rejected. The hub does not send it. |
| ❓ **Unverified** | From vendor drivers or older notes; never captured, not sent by the hub. |

Earlier versions of this page claimed "33/33 verified". That was wrong: the output, EDID, ext-audio and LCD commands were never answered by the device (HIL-09), and several value tables were guesses. The table at the end is the honest count.

Per-port writes of the web interface send `[port, value]` pairs; port **0 means all outputs**. That is also what the ninth entry of the per-output read arrays is: the web interface's "All Output" row (HIL-04, below).

---

## Authentication

### Login — ✅ Verified

```json
Request:  {"comhead": "login", "user": "Admin", "password": "admin"}
Response: {"comhead":"login","result":1}          (correct password)
Response: {"comhead":"login","result":0}          (wrong password)
```

The device echoes `"comhead":"login"` in both cases, so only `result` tells them apart (BE-05; `http/login.json`, `probe/login_wrong_password.json`). The API doc's `"result":"success"` never appears on V1.10.01.

---

## Reads

All reads are ✅ Verified (`tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/http/`); the simulator reproduces every one byte for byte.

### `get system status`

```json
{"comhead":"get system status","power":1,"baudrate":6,"beep":1,"lock":0,"mode":3}
```

- `baudrate` is a code: 1-6 = 4800, 9600, 19200, 38400, 57600, 115200 (device web interface).
- **`mode` is the front-panel LCD on-time code** (0 off, 1 always on, 2 = 15 s, 3 = 30 s, 4 = 60 s): the device web interface binds it to its LCD setting, and the captured 3 matches the Telnet line `lcd on 30 seconds`. The hub reads the LCD setting back from here.

### `get output status`

```json
{"comhead":"get output status","power":1,"allconnect":[1,1,0,0,0,0,0,0],"name":["TV","Sound","Out3","Out4","Out5","Out6","Out7","Out8"],"allscaler":[0,4,0,0,0,0,0,0,255],"allhdr":[0,0,0,0,0,0,0,0,0],"allhdcp":[3,3,3,3,3,3,3,3,3],"allarc":[0,0,0,0,0,0,0,0,0],"allout":[1,1,0,0,0,0,0,0,255],"allaudiomute":[0,0,0,0,0,0,0,0,0]}
```

- Output names are in `name`; there is no `allsource`, `allinputname` or `alloutputname` here (read routing from `get video status`).
- `allconnect`: display connected (hot-plug) per output. `allout`: stream on/off. `allarc`, `allaudiomute`: 0/1.
- `allhdcp`, `allhdr`, `allscaler`: the device codes of the tables under [Output settings](#output-settings). HDR 0 and scaler 0 = pass-through, scaler 4 = audio only (the Telnet `status` dump prints exactly that).
- **Ninth entry (HIL-04)**: every settings array has 9 values. The device web interface shows the ninth as its "All Output" row and writes it with port 0. Its value is the common value of the 8 outputs, or 255 when they differ (all 7 captured arrays follow this: `allscaler` [0,4,0,...] → 255, `allhdcp` all 3 → 3). The hub uses the first 8 entries.

### `get input status`

```json
{"comhead":"get input status","power":1,"edid":[36,36,36,36,36,36,36,36],"inactive":[0,0,0,0,0,0,0,0],"inname":["NES","SNES","Sega","N64","Switch","PS3","Apple","Switcher"]}
```

- `edid`: the EDID id per input (table under [EDID](#edid)). 36 is "8K FRL 12G HDR 7.1CH"; the Telnet dump prints `input 1 edid:frl12g_8k_hdr,7.1ch`.
- `inactive[i] = 1` means a signal **is** present (the name is misleading).

### `get video status`

```json
{"comhead":"get video status","power":1,"allsource":[7,7,7,7,7,7,7,7,7],"allinputname":[...8 names...],"alloutputname":[...8 names...],"allname":["Out1","Out2","Out3","Out4","Out5","Out6","Out7","Out8"]}
```

`allsource` is the routing (9 entries, see ninth entry above). `allname` holds the **preset names** (the device web interface edits them with `preset name`). Names are plain strings (no `IN01-` prefix).

### `get cec status`

```json
{"comhead":"get cec status","power":1,"allinputname":[...],"alloutputname":[...],"inputindex":[1,0,0,0,0,0,0,0],"outputindex":[1,0,0,0,0,0,0,0]}
```

`inputindex` / `outputindex`: 1 = CEC selected/enabled on that port. The device web interface toggles these with `set cec index` and sends CEC keys to the selected ports.

### `get ext-audio status`

```json
{"comhead":"get ext-audio status","power":1,"mode":0,"allsource":[1,2,3,4,5,6,7,8],"allout":[1,1,1,1,1,1,1,1],"allinputname":[...],"alloutputname":[...],"index":1}
```

`mode`: 0 bind to input, 1 bind to output, 2 matrix. `allsource`: source per audio output (1-8 = input N, 9-16 = the ARC of output N-8). `allout`: audio output enabled. `index`: the audio output selected with `set ext-audio index` (the device web interface's "current" output).

### `get status`, `get network`

```json
{"comhead":"get status","power":1,"version":"V1.10.01","hostname":"…","ipaddress":"192.168.0.100","subnet":"255.255.254.0","gateway":"192.168.1.254","macaddress":"…","model":"BK-808","webversion":"V2.00.03"}
{"comhead":"get network","power":1,"dhcp":1,"ipaddress":"192.168.0.100","subnet":"255.255.254.0","gateway":"192.168.1.254","telnetport":23,"tcpport":8000,"macaddress":"…","hostname":"…","username":1,"model":"BK-808"}
```

The mask is `subnet`, not `netmask`; `username` is an integer (1), not the login name. (MAC and hostname redacted in the capture.)

### `get routing status`, `preset get` — ❌ Not implemented

```json
{"comhead": "get routing status", "language": 0, "index": 1}
{"comhead": "preset get", "index": 1}
```

No answer for either (HIL-01; `http/get_routing_status.json`, `http/preset_get_1..8.json`). The hub reads presets over Telnet with `r preset N` and never sends these.

---

## Routing, presets, power, names, panel

| Command | Payload | Status | Evidence |
| --- | --- | --- | --- |
| `video switch` | `"source": [output, input]`; output 0 = all | ✅ | `write/http_video_switch*`: applied, `result:1`; output 9, input 0 or 9 → `result:0` |
| `set poweronoff` | `"power": 0\|1` | ✅ | `write/http_power`: applied; reads and writes keep working in standby |
| `set input name` / `set output name` | `"name": "...", "index": n` | ✅ | `write/http_*_name`: applied; a 40-character name was stored unchanged; index 9 → `result:0` |
| `set beep` | `"beep": 0\|1` | ✅ | `write/http_beep`; 2 → `result:0` |
| `set panel lock` | `"lock": 0\|1` | ✅ | `write/http_panel_lock`; 2 → `result:0` |
| `preset set` (recall) | `"index": 1-8` | ✅ answered `result:1` in earlier HAR captures; 🌐 the web interface reports "please save a preset" when a recall of an empty slot fails | recall of an empty slot is not captured yet |
| `preset save` | `"index": 1-8` | 🌐 | not captured on V1.10.01 (the preset tests needed `get routing status`; they now read back with Telnet `r preset N`) |
| `preset name` | `"index": n, "name": "..."` (read back in `get video status.allname`) | 🌐 | `OreiMatrix.set_preset_name`; the REST rename keeps hub-local names |
| `preset clear` | `"index": n` | 🌐 | used only by the capture tool to restore an empty slot |

All writes carry `"language": 0` like the device web interface.

---

## Output settings

All six are 🌐 **Web-UI-derived**. The commands the hub sent before (`set output stream|hdcp|hdr|scaler|arc|mute` with `{"output": n, <key>: v}`) are ❌: V1.10.01 never answered any of them for any value and nothing changed (HIL-09; `write/http_output_*`).

| Setting | Command | Payload | Device codes (read = write) |
| --- | --- | --- | --- |
| Stream on/off | `tx stream` | `"out": [output, 0\|1]` | 0 off, 1 on (`allout`) |
| HDCP | `tx hdcp` | `"hdcp": [output, code]` | 1 HDCP 1.4, 2 HDCP 2.2, 3 follow sink, 4 follow source, 5 user mode (`allhdcp`) |
| HDR conversion | `set hdr conversion` | `"hdr": [output, code]` | 0 bypass (pass-through), 1 HDR to SDR, 2 auto / follow sink EDID (`allhdr`) |
| Video mode (scaler) | `set video scaler` | `"scaler": [output, code]` | 0 bypass (pass-through), 1 8K→4K, 2 8K/4K→1080p, 3 auto / follow sink EDID, 4 audio only (`allscaler`) |
| ARC | `set arc` | `"arc": [output, 0\|1]` | `allarc` |
| Audio mute | `set output audio mute` | `"mute": [output, 0\|1]` | `allaudiomute` |

- Output 0 applies the value to all outputs (not used by the hub).
- Read and write codes are the same: the device web interface fills its selectors from the read arrays and sends the selected code back unchanged. The captured reads agree for every code they contain (HDR 0, scaler 0 and 4, HDCP 3).
- `set output resolution` (`"resolution": [output, code]`, 0-15) also exists in the web interface; the hub does not use it.

### Hub API values vs. device codes

`src/device_codes.py` is the only place that translates. The REST API and `OreiMatrix.set_output_*` keep the values they always had:

| Setting | API value (REST, OreiMatrix, scenes, profiles) | Device code |
| --- | --- | --- |
| HDCP | 1-5 | same |
| HDR | 1 passthrough, 2 HDR→SDR, 3 auto | API − 1 (0-2) |
| Scaler | 1 passthrough, 2 8K→4K, 3 8K/4K→1080p, 4 auto, 5 audio only | API − 1 (0-4) |
| Stream, ARC, mute | booleans | 0/1 |

REST reads (`/api/status/outputs`, `/api/status/full`, the web UI status) report HDR and scaler as **API values** since WP-A4 part 2, so a value read can be written back; the `raw` block keeps the device codes. (Before, reads returned device codes, so a pass-through output read as HDR 0, which the setter rejected, and scenes saved with "save current" could not be recalled: HIL-02.)

---

## EDID

### `set edid` — 🌐 Web-UI-derived

```json
{"comhead": "set edid", "language": 0, "edid": [input, id]}
```

The id is read back in `get input status.edid`. The device's list (device web interface; id = API value):

| Id | EDID | Id | EDID |
| --- | --- | --- | --- |
| 1-3 | 1080p 2.0 / 5.1 / 7.1CH | 22-24 | 4K60 4:4:4 HDR 2.0 / 5.1 / 7.1CH |
| 4-6 | 4K30 2.0 / 5.1 / 7.1CH | 25-27 | 4K120 4:2:0 HDR 2.0 / 5.1 / 7.1CH |
| 7-9 | 4K60 4:2:0 2.0 / 5.1 / 7.1CH | 28-30 | 4K120 4:4:4 HDR 2.0 / 5.1 / 7.1CH |
| 10-12 | 4K60 4:4:4 2.0 / 5.1 / 7.1CH | 31-33 | 8K FRL 10G HDR 2.0 / 5.1 / 7.1CH |
| 13-15 | 1080p HDR 2.0 / 5.1 / 7.1CH | 34-36 | 8K FRL 12G HDR 2.0 / 5.1 / 7.1CH (36 ✅ read on V1.10.01) |
| 16-18 | 4K30 HDR 2.0 / 5.1 / 7.1CH | 37-39 | User EDID 1-3 |
| 19-21 | 4K60 4:2:0 HDR 2.0 / 5.1 / 7.1CH | **40-47** | **Copy the EDID of output 1-8** |

- **EDID copy (BE-25)** is `set edid` with id 39 + output. The documented `copy edid` and the old hub's `set input edid` (`{"input": n, "edid": m}`, "copy" as 14 + N) are ❌: never answered (`write/http_input_edid`, `write/http_copy_edid`).
- The previous table on this page (15-22 = copy, 36 = "4K60 HDR Atmos", 37/38 = 8K30/60) was a guess and wrong. REST `POST /api/input/{n}/edid` takes `{"mode": 1-47}` or `{"copy_from_output": 1-8}`; 15-22 are now plain HDR EDIDs.
- User EDID upload (`set user edid`) and download (`download edid`) exist in the web interface; the hub does not use them.

---

## System

| Command | Payload | Status | Notes |
| --- | --- | --- | --- |
| `set lcd on time` | `"lcd on time": code` (0 off, 1 always on, 2 = 15 s, 3 = 30 s, 4 = 60 s) | 🌐 | read back as `get system status.mode`. The old `{"time": code}` payload is ❌: `result:0` for every code (`write/http_lcd`, API-07). |
| `reboot` | `"reboot": 1` | 🌐 | the device web interface then polls `get status` until the device is back. The old hub's `set reboot` was never captured; the hub now sends `reboot`. Telnet `reboot` is preferred when Telnet is up (not captured either). |
| `set hdcp`, `set baudrate`, `set factory`, `set tpg`, `set network`, `set defaults network` | | 🌐 exist in the web interface | not used by the hub |

---

## CEC

### `set cec index` — ✅ Verified (array form only)

```json
{"comhead": "set cec index", "language": 0, "inputindex": [8 × 0|1], "outputindex": [8 × 0|1]}
```

Applied with `result:1` (`write/http_cec_index_bulk`, `probe/cec_enable_shapes`). A 7-element array → `result:0`. The old hub's single-port form `{"port": "input", "index": n, "enable": 1}` is ❌ **rejected** (`result:0`, nothing changes; BE-13, HIL-10). `OreiMatrix.set_cec_enable` now always reads the current arrays and sends both.

### `cec command` — ✅ answered; key tables 🌐

```json
{"comhead": "cec command", "language": 0, "object": 0|1, "port": [8 × 0|1], "index": n}
```

- `object`: 0 = source device on an input, 1 = display on an output. Object 2 → `result:0`.
- The device does **not** validate `index` or `port`: index 99 and an all-zero port array were answered `result:1` (HIL-13; `write/http_cec_command_invalid`). The hub validates both.
- The hub sends a one-hot `port` array for the target. The device web interface sends its current selection (`inputindex`/`outputindex`) instead; whether the device uses the payload's array or its stored selection is settled by the live CEC run.

**Source (input) table, object 0** — the hub's table, identical to the device web interface's input pad (VAL-03: the table this page showed before was wrong on 15 of 19 indices):

| Index | Key | Index | Key | Index | Key |
| --- | --- | --- | --- | --- | --- |
| 1 | power on | 8 | down | 15 | fast forward |
| 2 | power off | 9 | back / return | 16 | stop |
| 3 | up | 10 | previous | 17 | mute |
| 4 | left | 11 | play | 18 | volume down |
| 5 | select / OK | 12 | next | 19 | volume up |
| 6 | right | 13 | rewind | | |
| 7 | menu | 14 | pause | | |

**Display (output) table, object 1** — a different, 0-based table of six keys (device web interface's output pad, BE-14):

| Index | Key |
| --- | --- |
| 0 | power on |
| 1 | power off |
| 2 | mute |
| 3 | volume down |
| 4 | volume up |
| 5 | active / input (make the display select the matrix) |

The hub used the source table for displays until WP-A4 part 2, so "power on" to a TV sent index 1, which is **power off** on this table. Navigation and playback keys have no output index; the hub refuses them for outputs (REST answers 400). Proof on a real display: `--include cec-live` in the capture tool.

---

## External audio

All 🌐 **Web-UI-derived**; the old hub's `set output exa mode`, `set output exa` (`exa` 1/2) and `set output exa in source` are ❌ (no answer, `write/http_exa_*`).

| Command | Payload | Read back |
| --- | --- | --- |
| `set ext-audio mode` | `"mode": 0-2` (bind to input, bind to output, matrix) | `mode` |
| `set ext-audio out` | `"out": [audio output 1-8, 0\|1]` | `allout` |
| `ext-audio switch` | `"source": [audio output, source 1-16]` (1-8 input, 9-16 ARC of output 1-8); offered by the web interface only in matrix mode | `allsource` |
| `set ext-audio index` | `"index": 1-8` | `index` |

---

## Telnet (port 23)

Captured on V1.10.01 (`telnet/`, `probe/telnet_*`, `write/telnet_*`):

- On connect: Telnet option negotiation (`IAC WILL SGA`, `IAC WONT ECHO`, `IAC DONT ECHO`, `IAC DONT BINARY`, `IAC WONT SGA`), then the banner `****************welcome **************`, `fw version :v1.10.01` (padded), a line of `*`, an empty line.
- A command needs both `!` and CR LF (`r type!\r\n`, what the hub sends). `r type!` without CR LF gets only the echo and no answer; a line without `!` (`r type\r\n`) is echoed and answered `E00`. The device echoes each command line (`r link in 1!`) before the answer. Lines end with CR LF, there is no prompt. Upper case works, pipelined commands work, and a second concurrent session works.
- `E00` = unknown command (also an unknown CEC word); `E01` = known command with a bad parameter (port out of range, non-numeric port). `r preset 9` prints `E01` *before* the echo and `E00` after it.
- Reads: `status` (111 lines headed `get the unit all status:`, ending with the MAC line and an empty line), `r fw version` (4 lines), `r type`, `r link in|out N` (`r link out 0` lists all outputs), `r preset N` (8 routing lines, or `preset N is none,please save a preset`).

| Command | Status | Answer after the echo |
| --- | --- | --- |
| `s output N in source M` (N = 0: all) | ✅ | `outputN->inputM` (8 lines for 0) |
| `s beep 0\|1` | ✅ | `beep off` / `beep on` |
| `s lock 0\|1` | ✅ | `panel button lock on` / `off` |
| `power 0\|1` (what the hub's TelnetClient sends) | ✅ | `power off`; `power on` followed by the start-up text (`8x8 hdmi2.1 matrix`, `system initializing...`, `initialization finished!`, `mcu fw version : v1.10.01`) |
| `s power 0\|1` (vendor syntax) | ❌ | `E01` |
| `s av <in> <out>` (vendor syntax) | ❌ | `E00` |
| `s out N stream 0\|1` (vendor syntax) | ❌ | `E00` (HIL-11; the hub does not send it) |
| `s save\|recall\|clear preset N` | ❓ | not captured yet (preset tests now read back with `r preset`) |
| `s cec in N <word>`, `s cec hdmi out N <word>` | ❓ | not captured (live CEC run); a bad port is `E01`, an unknown word `E00` |
| `reboot` | ❓ | not captured (opt-in reboot run) |

Push notifications from front-panel changes are not captured yet.

---

## Status summary

| Group | ✅ Verified | 🌐 Web-UI-derived (pending hardware proof) | ❌ Not implemented (captured) |
| --- | --- | --- | --- |
| Login | 1 | | |
| Reads | 8 (`get system/output/input/video/cec/ext-audio status`, `get status`, `get network`) | | 2 (`get routing status`, `preset get`) |
| Routing, power, names, beep, lock | 6 (`video switch`, `set poweronoff`, `set input name`, `set output name`, `set beep`, `set panel lock`) | | |
| Presets | 1 (`preset set`, from earlier HAR captures) | 3 (`preset save`, `preset name`, `preset clear`) | |
| Output settings | | 6 | 6 (`set output stream/hdcp/hdr/scaler/arc/mute`) |
| EDID | | 1 (`set edid`, incl. copy) | 2 (`set input edid`, `copy edid`) |
| LCD, reboot | | 2 (`set lcd on time` with `"lcd on time"`, `reboot`) | 1 (`set lcd on time` with `"time"`) |
| CEC | 2 (`set cec index` arrays, `cec command` answer) | 2 key tables (input, output) | 1 (single-port `set cec index`) |
| External audio | | 4 | 3 (`set output exa*`) |
| Telnet | 4 set commands + all reads | | 3 (`s power`, `s av`, `s out N stream`) |

To move a 🌐 row to ✅: run the capture tool's write mode (`tools/hil/README.md`, "Verify the WP-A4 part 2 commands") and then `python -m tools.simulator --golden tests/fixtures/device/<folder> --report`; the `web-ui-commands`, `lcd-codes`, `edid-range`, `copy-edid`, `exa-commands` and `output-mode-text` rows turn CONFIRMED (or CONTRADICTED with the difference).

## Sources

1. HIL Session 1 captures of the owner's BK-808 (`tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/`, reports `docs/validation/2026-09-25-hil-session-1-*.md`).
2. The device's own configuration web interface (served by the matrix): the commands, payload shapes and option lists described above, in our own words; no vendor code is copied into this repository.
3. Older HAR captures of the web UI and the RTI / Control4 drivers (not redistributed, see [vendor/README.md](vendor/README.md)); several of their commands turned out not to exist on V1.10.01.

*Last updated: 2026-09-25 (WP-A4 part 2)*
