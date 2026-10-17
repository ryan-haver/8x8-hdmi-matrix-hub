# OREI BK-808 API Command & Protocol Reference

This document provides a comprehensive protocol specification for the OREI BK-808 8×8 HDMI 2.1 matrix switch across both its **HTTP JSON** API (`/cgi-bin/instr`) and **Telnet** interface (port 23).

It reflects the shipped implementation in `src/orei_matrix.py`, `src/telnet_client.py`, and `src/_telnet_proto.py`, cross-referenced with exact real-device network captures from a physical BK-808 matrix with MCU firmware **V1.10.01** and Web GUI **V2.00.03** (`tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/`).

---

## Protocol Verification vs. Physical Hardware Effects

To maintain strict engineering rigor, this specification distinguishes between **wire-level protocol verification** and **physical hardware effects**:

| Domain | What is Verified (Wire Protocol) | What is Unverified (Physical Hardware Effect) |
| --- | --- | --- |
| **CEC Control** | The matrix MCU receives `{"comhead": "cec command", ...}` over HTTP or `s cec in\|hdmi out ...` over Telnet and returns `result: 1` / echo acknowledgement. | Whether a specific attached television (e.g. Samsung, LG, Sony) or source (e.g. Apple TV, Shield) physically powers on, changes volume, or switches input. Physical CEC execution depends on TV firmware quirks and HDMI CEC line physical state; live display testing requires an in-person operator (HIL-E / Phase 8). |
| **Video Routing** | `video switch` updates internal routing registers read back byte-for-byte in `get video status.allsource` and Telnet `status`. | Sink picture sync time, HDMI 2.1 FRL/TMDS clock stabilization, and HDCP 2.2/2.3 physical key exchange on a connected display monitor. |
| **EDID Management** | `set edid` writes the EDID table ID (1–47) to the specified input port, verified via `get input status.edid` readback. | Whether a connected physical PC/source graphics card immediately renegotiates resolution without an electrical Hot-Plug Detect (HPD) toggle or physical cable replug. |
| **LCD Timeout** | `set lcd on time` updates the front-panel timer register read back in `get system status.mode` and Telnet `status`. | Physical darkening or extinguishing of the matrix front-panel LCD backlight. |
| **Matrix Reboot** | The payload `{"comhead": "reboot", "reboot": 1}` or Telnet `reboot` is accepted. | Physical hardware reboot duration, PHY link drop, and warm-restart network recovery time. |
| **Front-Panel Push** | Read queries over Telnet return current front-panel lock and beep registers. | Real-time push broadcast over Telnet when an operator physically presses front-panel buttons (skipped in automated HIL session). |

---

## Status Legend

| Status | Definition |
| --- | --- |
| ✅ **Verified** | Verified byte-for-byte on physical hardware (BK-808 MCU V1.10.01 / Web V2.00.03, HIL Session 1). For write commands: sent, acknowledged, and verified via independent readback. |
| 🌐 **Web-UI-derived** | Observed in the matrix's embedded web management interface and supported by the hub implementation, but pending physical hardware capture proof. |
| ❌ **Not implemented** | Rejected by firmware V1.10.01 (answers `result: 0`, times out with no answer, or returns Telnet error `E00`/`E01`). Not sent by the hub. |
| ❓ **Unverified** | Described in vendor documentation or legacy driver notes; not verified on hardware and not sent by the hub. |

---

## HTTP Communication Protocol (`/cgi-bin/instr`)

- **Endpoint:** `https://<ip>:443/cgi-bin/instr`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`
- **Request Format:** Compact JSON object with `"comhead"` and `"language": 0`:
  ```json
  {"comhead": "<command_name>", "language": 0, ...}
  ```
- **Response Format:** `text/plain` MIME type containing compact JSON followed by `\r\n`.
- **TLS/SSL:** The matrix presents a self-signed SSL certificate (`verify_ssl=False` required).
- **Session Authentication:** Login via `login` command. Sessions are tracked by the matrix per client IP address. Reads can be performed without session cookies.
- **Unrecognized Commands:** The device accepts the TCP connection but **never responds** (times out). The same occurs for non-JSON bodies. Following an unrecognized command, the matrix web server may temporarily stall for one subsequent request (HIL-12).

---

## HTTP Authentication

### `login` — ✅ Verified

```json
Request:  {"comhead": "login", "user": "Admin", "password": "admin"}
Response: {"comhead":"login","result":1}          (correct password)
Response: {"comhead":"login","result":0}          (wrong password)
```

The matrix echoes `"comhead": "login"` for both success and failure. The client must inspect `result` (1 = success, 0 = failure).

---

## HTTP Reads (Status Queries)

All eight primary read commands are ✅ **Verified** (`tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/http/`).

### `get system status` — ✅ Verified

```json
Request:  {"comhead": "get system status", "language": 0}
Response: {"comhead":"get system status","power":1,"baudrate":6,"beep":1,"lock":0,"mode":3}
```

- `power`: 1 = on, 0 = standby. Reads continue answering in standby.
- `baudrate`: RS-232 baud rate code (1=4800, 2=9600, 3=19200, 4=38400, 5=57600, 6=115200).
- `beep`: Buzzer state (1 = enabled, 0 = disabled).
- `lock`: Front-panel button lock (1 = locked, 0 = unlocked).
- `mode`: **Front-panel LCD timeout code** (0 = off, 1 = always on, 2 = 15 s, 3 = 30 s, 4 = 60 s).

### `get output status` — ✅ Verified

```json
Request:  {"comhead": "get output status", "language": 0}
Response: {"comhead":"get output status","power":1,"allconnect":[1,1,0,0,0,0,0,0],"name":["TV","Sound","Out3","Out4","Out5","Out6","Out7","Out8"],"allscaler":[0,4,0,0,0,0,0,0,255],"allhdr":[0,0,0,0,0,0,0,0,0],"allhdcp":[3,3,3,3,3,3,3,3,3],"allarc":[0,0,0,0,0,0,0,0,0],"allout":[1,1,0,0,0,0,0,0,255],"allaudiomute":[0,0,0,0,0,0,0,0,0]}
```

- `name`: Array of 8 output label strings.
- `allconnect`: Array of 8 booleans (1 = sink connected via hot-plug, 0 = disconnected).
- `allout`: Array of 9 values (stream enable: 1 = enabled, 0 = disabled).
- `allhdcp`: Array of 9 values (HDCP mode codes 1–5).
- `allhdr`: Array of 9 values (HDR conversion codes 0–2).
- `allscaler`: Array of 9 values (video scaler mode codes 0–4).
- `allarc`: Array of 9 values (ARC enable: 0/1).
- `allaudiomute`: Array of 9 values (audio mute: 0/1).
- **Ninth Entry Behavior (HIL-04):** Settings arrays contain 9 elements. Index 8 represents the "All Outputs" state in the matrix web GUI. When all 8 outputs share identical settings, index 8 holds that value; when outputs have differing settings, index 8 returns `255`.

### `get input status` — ✅ Verified

```json
Request:  {"comhead": "get input status", "language": 0}
Response: {"comhead":"get input status","power":1,"edid":[36,36,36,36,36,36,36,36],"inactive":[0,0,0,0,0,0,0,0],"inname":["NES","SNES","Sega","N64","Switch","PS3","Apple","Switcher"]}
```

- `inname`: Array of 8 input label strings.
- `edid`: Array of 8 EDID profile IDs (see [EDID Reference](#edid-reference)).
- `inactive`: Array of 8 signal detection flags (**1 = signal present/active**, 0 = no signal).

### `get video status` — ✅ Verified

```json
Request:  {"comhead": "get video status", "language": 0}
Response: {"comhead":"get video status","power":1,"allsource":[7,7,7,7,7,7,7,7,7],"allinputname":["..."],"alloutputname":["..."],"allname":["Out1","Out2","Out3","Out4","Out5","Out6","Out7","Out8"]}
```

- `allsource`: 9-element array mapping each output (0-indexed) to its selected input (0–7 representing inputs 1–8).
- `allname`: 8 preset slot name strings.

### `get cec status` — ✅ Verified

```json
Request:  {"comhead": "get cec status", "language": 0}
Response: {"comhead":"get cec status","power":1,"allinputname":["..."],"alloutputname":["..."],"inputindex":[1,0,0,0,0,0,0,0],"outputindex":[1,0,0,0,0,0,0,0]}
```

- `inputindex` / `outputindex`: 8-element arrays of 0/1 flags indicating which ports have CEC enabled.

### `get ext-audio status` — ✅ Verified

```json
Request:  {"comhead": "get ext-audio status", "language": 0}
Response: {"comhead":"get ext-audio status","power":1,"mode":0,"allsource":[1,2,3,4,5,6,7,8],"allout":[1,1,1,1,1,1,1,1],"allinputname":["..."],"alloutputname":["..."],"index":1}
```

- `mode`: External audio routing mode (0 = bind to input, 1 = bind to output, 2 = matrix).
- `allsource`: Audio source per output (1–8 = inputs 1–8, 9–16 = ARC from outputs 1–8).
- `allout`: Audio output enable (1 = enabled, 0 = disabled).
- `index`: Currently selected audio output channel (1–8).

### `get status` & `get network` — ✅ Verified

```json
Request:  {"comhead": "get status", "language": 0}
Response: {"comhead":"get status","power":1,"version":"V1.10.01","hostname":"...","ipaddress":"192.168.0.100","subnet":"255.255.254.0","gateway":"192.168.1.254","macaddress":"...","model":"BK-808","webversion":"V2.00.03"}

Request:  {"comhead": "get network", "language": 0}
Response: {"comhead":"get network","power":1,"dhcp":1,"ipaddress":"192.168.0.100","subnet":"255.255.254.0","gateway":"192.168.1.254","telnetport":23,"tcpport":8000,"macaddress":"...","hostname":"...","username":1,"model":"BK-808"}
```

---

## HTTP Write Commands

### Video Routing & Power

| Command | Payload | Status | Evidence & Verification Notes |
| --- | --- | --- | --- |
| `video switch` | `"source": [output, input]` | ✅ Verified | Output 1–8, input 1–8. Output 0 routes input to all outputs. Verified by `write/http_video_switch*`. |
| `set poweronoff` | `"power": 0\|1` | ✅ Verified | 1 = on, 0 = standby. Verified by `write/http_power`. |
| `set input name` | `"name": str, "index": 1-8` | ✅ Verified | Stores up to 40 characters. Verified by `write/http_input_name`. |
| `set output name` | `"name": str, "index": 1-8` | ✅ Verified | Stores up to 40 characters. Verified by `write/http_output_name`. |
| `set beep` | `"beep": 0\|1` | ✅ Verified | 1 = enabled, 0 = disabled. Verified by `write/http_beep`. |
| `set panel lock` | `"lock": 0\|1` | ✅ Verified | 1 = locked, 0 = unlocked. Verified by `write/http_panel_lock`. |
| `set lcd on time` | `"lcd on time": code` (0-4) | ✅ Verified | Codes: 0 off, 1 on, 2 = 15 s, 3 = 30 s, 4 = 60 s. Read back in `get system status.mode`. Verified by `write/http_lcd_on_time`. |
| `reboot` | `"reboot": 1` | 🌐 Web-UI-derived | Sent to reboot the matrix. (Uncaptured in HIL Session 1 to avoid host disruption). |

### Output Settings

All output settings send a `[port, value]` array where port `1-8` targets a specific output and port `0` applies to all outputs:

| Setting | Command | Payload | Device Codes (Read/Write) | Status |
| --- | --- | --- | --- | --- |
| Stream Enable | `tx stream` | `"out": [out, 0\|1]` | 0 = disabled, 1 = enabled | ✅ Verified (`write/http_tx_stream`) |
| HDCP Mode | `tx hdcp` | `"hdcp": [out, code]` | 1 = HDCP 1.4, 2 = HDCP 2.2, 3 = Follow Sink, 4 = Follow Source, 5 = User Mode | ✅ Verified (`write/http_tx_hdcp`) |
| HDR Conversion | `set hdr conversion` | `"hdr": [out, code]` | 0 = Pass-through, 1 = HDR to SDR, 2 = Auto / Follow Sink | ✅ Verified (`write/http_hdr_conversion`) |
| Video Scaler | `set video scaler` | `"scaler": [out, code]` | 0 = Pass-through, 1 = 8K→4K, 2 = 8K/4K→1080p, 3 = Auto, 4 = Audio Only | ✅ Verified (`write/http_video_scaler`) |
| ARC Enable | `set arc` | `"arc": [out, 0\|1]` | 0 = disabled, 1 = enabled | ✅ Verified (`write/http_arc`) |
| Audio Mute | `set output audio mute` | `"mute": [out, 0\|1]` | 0 = unmuted, 1 = muted | ✅ Verified (`write/http_output_audio_mute`) |

#### Hub API Values vs. Device Codes

`src/device_codes.py` performs normalization between high-level REST API values and low-level device codes:
- **HDR:** API values 1–3 map to device codes 0–2 (`device = api - 1`).
- **Scaler:** API values 1–5 map to device codes 0–4 (`device = api - 1`).
- **HDCP:** 1–5 are identical.

### EDID Reference

#### `set edid` — ✅ Verified (`write/http_set_edid`)

```json
{"comhead": "set edid", "language": 0, "edid": [input_num, edid_id]}
```

| ID | Specification | ID | Specification |
| --- | --- | --- | --- |
| 1–3 | 1080p (2.0 / 5.1 / 7.1CH) | 22–24 | 4K60 4:4:4 HDR (2.0 / 5.1 / 7.1CH) |
| 4–6 | 4K30 (2.0 / 5.1 / 7.1CH) | 25–27 | 4K120 4:2:0 HDR (2.0 / 5.1 / 7.1CH) |
| 7–9 | 4K60 4:2:0 (2.0 / 5.1 / 7.1CH) | 28–30 | 4K120 4:4:4 HDR (2.0 / 5.1 / 7.1CH) |
| 10–12 | 4K60 4:4:4 (2.0 / 5.1 / 7.1CH) | 31–33 | 8K FRL 10G HDR (2.0 / 5.1 / 7.1CH) |
| 13–15 | 1080p HDR (2.0 / 5.1 / 7.1CH) | 34–36 | 8K FRL 12G HDR (2.0 / 5.1 / 7.1CH) |
| 16–18 | 4K30 HDR (2.0 / 5.1 / 7.1CH) | 37–39 | User EDID 1–3 |
| 19–21 | 4K60 4:2:0 HDR (2.0 / 5.1 / 7.1CH) | **40–47** | **Copy Output 1–8 EDID to Input** (`39 + output_num`) |

### Presets

| Command | Payload | Status | Notes |
| --- | --- | --- | --- |
| `preset save` | `"index": 1-8` | ✅ Verified | Saves current routing state to preset slot 1–8 (`write/http_preset_save`). |
| `preset set` | `"index": 1-8` | ✅ Verified | Recalls preset slot 1–8. Recalling an empty slot returns `result: 0` (`write/http_preset_recall`). |
| `preset name` | `"index": 1-8, "name": str` | ✅ Verified | Stores preset name, read back in `get video status.allname` (`write/http_preset_name`). |
| `preset clear` | `"index": 1-8` | 🌐 Web-UI-derived | Clears preset slot. |

### External Audio

| Command | Payload | Status | Notes |
| --- | --- | --- | --- |
| `set ext-audio mode` | `"mode": 0-2` | ✅ Verified | 0 = bind input, 1 = bind output, 2 = matrix (`write/http_ext_audio_mode`). |
| `set ext-audio out` | `"out": [out 1-8, 0\|1]` | ✅ Verified | Enables/disables audio output channel (`write/http_ext_audio_out`). |
| `ext-audio switch` | `"source": [out 1-8, src 1-16]` | ✅ Verified | Sources 1–8 = inputs 1–8; 9–16 = ARC from outputs 1–8 (`write/http_ext_audio_switch`). |
| `set ext-audio index` | `"index": 1-8` | ✅ Verified | Selects active channel in matrix web UI (`write/http_ext_audio_index`). |

### CEC Control

#### `set cec index` — ✅ Verified (Array format only)

```json
{"comhead": "set cec index", "language": 0, "inputindex": [8 × 0|1], "outputindex": [8 × 0|1]}
```

Single-port payloads (e.g. `{"port": "input", "index": n, "enable": 1}`) are ❌ **rejected** (`result: 0`, HIL-10). The client must always read existing state and send full 8-element arrays.

#### `cec command` — ✅ Verified Protocol; Physical Display Execution Unverified

```json
{"comhead": "cec command", "language": 0, "object": 0|1, "port": [8 × 0|1], "index": n}
```

- `object`: 0 = Source device (HDMI input); 1 = Display device (HDMI output).
- `port`: 8-element one-hot array selecting the target port.
- **Input Pad (Source, `object`: 0):** 1-based indexing:
  1: power on, 2: power off, 3: up, 4: left, 5: select/OK, 6: right, 7: menu, 8: down, 9: back, 10: previous, 11: play, 12: next, 13: rewind, 14: pause, 15: fast forward, 16: stop, 17: mute, 18: volume down, 19: volume up.
- **Output Pad (Display, `object`: 1):** 0-based indexing:
  0: power on, 1: power off, 2: mute, 3: volume down, 4: volume up, 5: active source.

---

## Unimplemented / Rejected HTTP Commands

The following commands from vendor documentation or legacy code are rejected or unanswered by MCU V1.10.01:
- `get routing status`, `preset get`: ❌ Unanswered (client times out).
- Legacy output writes: `set output stream|hdcp|hdr|scaler|arc|mute` (`{"output": n, ...}`): ❌ Unanswered.
- Legacy EDID writes: `set input edid`, `copy edid`: ❌ Unanswered.
- Legacy LCD payload: `set lcd on time` with `{"time": code}`: ❌ Rejected (`result: 0`).
- Legacy single-port CEC enable: `set cec index` with `{"port": ...}`: ❌ Rejected (`result: 0`).
- Legacy external audio: `set output exa*`: ❌ Unanswered.

---

## Telnet Protocol Reference (Port 23)

The matrix exposes an interactive ASCII Telnet command interface on port 23 (`src/telnet_client.py`, `src/_telnet_proto.py`).

### Connection, Negotiation & Framing

1. **Option Negotiation:** On connection, the matrix sends RFC 854 IAC sequences:
   `\xff\xfb\x03\xff\xfc\x01\xff\xfe\x01\xff\xfe\x00\xff\xfc\x03` (`IAC WILL SGA`, `IAC WONT ECHO`, `IAC DONT ECHO`, `IAC DONT BINARY`, `IAC WONT SGA`).
2. **Welcome Banner:**
   ```text
   ****************welcome **************
   fw version :v1.10.01          
   **************************************
   ```
3. **Command Framing:** Every command must be terminated with an exclamation mark and carriage return line feed: `!\r\n`.
   - A command sent without `!` (e.g., `r type\r\n`) is echoed and answered with `E00\r\n`.
   - A command sent with `!` but without CRLF produces no response until CRLF arrives.
4. **Command Echo:** The matrix echoes the incoming command line before sending the answer lines.
5. **Error Codes:**
   - `E00`: Unknown command or unknown CEC command word.
   - `E01`: Bad parameter (e.g. port out of range `r link in 9!`).
   - `E02`: Reserved error code.
6. **Concurrency:** Multiple concurrent Telnet connections are supported (`probe/telnet_second_session.json`).

### Telnet Query Commands (Reads)

| Command | Status | Description and Output Format |
| --- | --- | --- |
| `status!` | ✅ Verified | 111-line full system status dump. Begins with `get the unit all status:` and concludes with `mac address: <MAC>` and an empty line. Contains power, baudrate, beep, lock, lcd timeout, input/output connection states, names, EDID strings, routing, and audio configuration. |
| `r fw version!` | ✅ Verified | 4-line firmware version report (`fw version :v1.10.01`, `key mcu : v1.00.08`, `web gui : v2.00.03`, `cpld version : v1.00.06`). |
| `r type!` | ✅ Verified | Returns device model string: `8x8 hdmi2.1 matrix`. |
| `r link in <1-8>!` | ✅ Verified | Input cable detect: `hdmi input <n>: connect` or `disconnect`. |
| `r link out <0-8>!` | ✅ Verified | Output cable detect: `hdmi output <n>: connect` or `disconnect`. Port `0` lists all 8 outputs. |
| `r preset <1-8>!` | ✅ Verified | Returns 8 routing lines (`output<n>->input<m>`), or `preset <n> is none,please save a preset`. |

### Telnet Control Commands (Writes)

| Command | Status | Acknowledgement After Echo |
| --- | --- | --- |
| `s output <0-8> in source <1-8>!` | ✅ Verified | `output<n>->input<m>` (8 lines when output is 0) |
| `power 0!` | ✅ Verified | `power off` |
| `power 1!` | ✅ Verified | `power on` followed by startup boot text |
| `s beep 0\|1!` | ✅ Verified | `beep off` / `beep on` |
| `s lock 0\|1!` | ✅ Verified | `panel button lock off` / `on` |
| `s save preset <1-8>!` | ✅ Verified | `s save preset <n>` |
| `s recall preset <1-8>!` | ✅ Verified | `s recall preset <n>` followed by 8 routing lines |
| `s clear preset <1-8>!` | ✅ Verified | `s clear preset <n>` |
| `reboot!` | ❓ Unverified | Device reboot |
| `s cec in <1-8> <word>!` | ❓ Unverified | Send CEC key to source device on input (e.g. `power_on`, `menu`) |
| `s cec hdmi out <1-8> <word>!` | ❓ Unverified | Send CEC key to display on output (e.g. `power_on`, `volume_up`) |

*Note on Telnet Power Syntax:* Bare `power 0!` / `power 1!` is the valid syntax. Vendor syntax `s power 0!` is rejected with `E01`. Vendor routing `s av <in> <out>` is rejected with `E00`.

### Unsolicited Push Notifications

The matrix Telnet server can emit asynchronous event lines on state changes:
- **Cable Connect/Disconnect:** Emits `hdmi input <n>: connect` / `disconnect` or `hdmi output <n>: connect` / `disconnect`.
- These lines are processed by `TelnetClient._listen_for_push` to update the connection state cache in real time without polling.

---

## Status Summary

| Category | ✅ Verified | 🌐 Web-UI-derived | ❌ Not implemented / Rejected | ❓ Unverified |
| --- | --- | --- | --- | --- |
| **HTTP Authentication** | 1 (`login`) | 0 | 0 | 0 |
| **HTTP Status Reads** | 8 (`get system/output/input/video/cec/ext-audio status`, `get status`, `get network`) | 0 | 2 (`get routing status`, `preset get`) | 0 |
| **HTTP Routing & Names** | 6 (`video switch`, `set poweronoff`, `set input name`, `set output name`, `set beep`, `set panel lock`) | 0 | 0 | 0 |
| **HTTP Presets** | 3 (`preset save`, `preset set`, `preset name`) | 1 (`preset clear`) | 0 | 0 |
| **HTTP Output Settings** | 6 (`tx stream`, `tx hdcp`, `set hdr conversion`, `set video scaler`, `set arc`, `set output audio mute`) | 0 | 6 (legacy `set output *`) | 0 |
| **HTTP EDID** | 1 (`set edid` incl. copy) | 0 | 2 (`set input edid`, `copy edid`) | 0 |
| **HTTP LCD & Reboot** | 1 (`set lcd on time`) | 1 (`reboot`) | 1 (legacy `time` payload) | 0 |
| **HTTP External Audio** | 4 (`set ext-audio mode/out/index`, `ext-audio switch`) | 0 | 3 (legacy `set output exa*`) | 0 |
| **HTTP CEC Control** | 2 (`set cec index` array, `cec command` protocol) | 0 | 1 (single-port `set cec index`) | 0 |
| **Telnet Reads** | 6 (`status`, `r fw version`, `r type`, `r link in`, `r link out`, `r preset`) | 0 | 0 | 0 |
| **Telnet Writes** | 8 (`s output`, `power 0`, `power 1`, `s beep`, `s lock`, `s save preset`, `s recall preset`, `s clear preset`) | 0 | 3 (`s power`, `s av`, `s out N stream`) | 3 (`reboot`, `s cec in`, `s cec hdmi out`) |

---

## Sources & References

1. **Hardware Verification Captures:** Byte-exact captures from an OREI BK-808 (MCU V1.10.01 / Web V2.00.03), preserved in `tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/` and documented in HIL Session reports ([2026-09-25-hil-session-1-read.md](validation/2026-09-25-hil-session-1-read.md) and [2026-09-25-hil-session-1-probe-write.md](validation/2026-09-25-hil-session-1-probe-write.md)).
2. **Device Embedded Web Interface:** Analysis of the web GUI served by the matrix firmware (`/cgi-bin/instr`).
3. **Third-Party Notices & License Audit:** All proprietary vendor drivers, utilities, and copyrighted manuals were purged from the repository per SEC-14; see [../THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).
