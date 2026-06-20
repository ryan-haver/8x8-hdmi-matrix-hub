# OREI BK-808 API Command Reference

This document tracks all known API commands for the OREI BK-808 HDMI Matrix, their verification status, and implementation notes.

## Communication Protocol

- **Endpoint**: `https://<ip>:443/cgi-bin/instr`
- **Method**: POST
- **Content-Type**: application/json
- **SSL**: Self-signed certificate (verify=False required)
- **Authentication**: Session-based, login required first

## Command Status Legend

| Status | Description |
|--------|-------------|
| ✅ | Verified working in our integration |
| 🔄 | Implemented but needs testing |
| ⚠️ | Discovered but not yet implemented |
| ❓ | Discovered from drivers, unverified |

---

## Authentication Commands

### Login
**Status**: ✅ Verified

```json
Request:  {"comhead": "login", "user": "Admin", "password": "admin"}
Response: {"comhead": "login", "result": "success"}
```

**Notes**: Required before any other commands. Default credentials are Admin/admin.

---

## Status/Query Commands

### Get System Status
**Status**: ✅ Verified

```json
Request:  {"comhead": "get system status", "language": 0}
Response: {
  "comhead": "get system status",
  "power": 1,           // 1=on, 0=standby
  "beep": 1,            // 1=enabled, 0=disabled
  "lock": 0,            // 1=panel locked, 0=unlocked
  "mode": 0,            // Display mode
  "baudrate": 115200    // Serial baud rate
}
```

**Notes**: Primary status endpoint. Power state affects other commands.

---

### Get Output Status
**Status**: ✅ Verified

```json
Request:  {"comhead": "get output status", "language": 0}
Response: {
  "comhead": "get output status",
  "power": 1,
  "allconnect": [1,1,0,0,0,0,0,0],    // Display connected per output (HOT PLUG DETECT)
  "allscaler": [1,1,1,1,1,1,1,1],     // Scaler mode per output
  "allhdr": [3,3,3,3,3,3,3,3],        // HDR mode (1=passthrough, 2=HDR→SDR, 3=auto)
  "allhdcp": [3,3,3,3,3,3,3,3],       // HDCP mode (1=1.4, 2=2.2, 3=follow sink, 4=follow src, 5=user)
  "allarc": [0,0,0,0,0,0,0,0],        // ARC enabled per output
  "allout": [1,1,1,1,1,1,1,1],        // Output enabled per output (stream on/off)
  "allaudiomute": [0,0,0,0,0,0,0,0],  // Audio mute per output
  "allsource": [1,1,1,1,1,1,1,1],     // Current input per output (1-indexed)
  "allinputname": ["PS3","AppleTV","Computer","Switch","Shield","PS5","Analogue","TDB"],
  "alloutputname": ["TV","Soundbar","Output 3","Output 4","Output 5","Output 6","Output 7","Output 8"]
}
```

**Notes**: 
- `allconnect` is the key array for detecting which displays are physically connected
- `allsource` shows current routing (which input goes to which output)
- Names are configurable via web UI

---

### Get Input Status
**Status**: ✅ Verified

```json
Request:  {"comhead": "get input status", "language": 0}
Response: {
  "comhead": "get input status",
  "power": 1,
  "edid": [3,3,3,3,3,3,3,3],        // EDID mode per input
  "inactive": [0,0,1,0,0,0,1,1],    // 1=signal present, 0=no signal
  "inname": ["PS3","AppleTV","Computer","Switch","Shield","PS5","Analogue","TDB"]
}
```

**Notes**:
- `inactive` array indicates signal detection per input (1=signal present, 0=no signal)
- Despite the confusing name, `inactive[i]=1` means the input IS receiving a video signal
- This can be used to show which source devices are powered on and outputting video

---

### Get CEC Status
**Status**: ✅ Verified

```json
Request:  {"comhead": "get cec status", "language": 0}
Response: {
  "comhead": "get cec status",
  "power": 1,
  "allinputname": ["PS3","AppleTV","Computer","Switch","Shield","PS5","Analogue","TDB"],
  "alloutputname": ["TV","Soundbar","Output 3","Output 4","Output 5","Output 6","Output 7","Output 8"],
  "inputindex": [0,0,0,0,0,0,0,0],   // CEC enabled per input (1=enabled)
  "outputindex": [0,0,0,0,0,0,0,0]   // CEC enabled per output (1=enabled)
}
```

**Notes**:
- ⚠️ **IMPORTANT**: CEC commands may only work if the port has CEC enabled!
- Use `set cec index` to enable CEC on specific ports before sending CEC commands
- This needs verification - does CEC need to be enabled for commands to work?

---

### Get Network Info
**Status**: ✅ Verified

```json
Request:  {"comhead": "get network", "language": 0}
Response: {
  "comhead": "get network",
  "ipaddress": "193.168.0.100",
  "netmask": "255.255.255.0",
  "gateway": "193.168.0.1",
  "macaddress": "XX:XX:XX:XX:XX:XX",
  "hostname": "BK-808",
  "model": "BK-808"
}
```

---

### Get Device Info (Firmware)
**Status**: ✅ Verified

```json
Request:  {"comhead": "get status", "language": 0}
Response: {
  "comhead": "get status",
  "version": "V1.10.01",    // MCU firmware version
  "webversion": "V2.00.03"  // Web UI version
}
```

---

### Get Ext-Audio Status
**Status**: 🔄 Implemented

```json
Request:  {"comhead": "get ext-audio status", "language": 0}
Response: {
  "comhead": "get ext-audio status",
  "power": 1,
  "mode": 0,                         // 0=bind to input, 1=bind to output, 2=matrix
  "allsource": [1,2,3,4,5,6,7,8],    // Audio source per ext-audio output
  "allout": [0,0,0,0,0,0,0,0],       // Ext-audio enabled per output
  "allinputname": [...],
  "alloutputname": [...],
  "index": 1
}
```

**Notes**: Controls external analog audio outputs (separate from HDMI audio).

---

### Get Preset Status
**Status**: ✅ Verified

```json
Request:  {"comhead": "get routing status", "language": 0, "index": 1}
Response: {
  "comhead": "get routing status",
  "power": 1,
  "allpreset": [
    {"allsource": [1,2,3,4,5,6,7,8], "name": "Preset 1"},
    {"allsource": [1,1,1,1,1,1,1,1], "name": "Preset 2"},
    ...
  ]
}
```

---

## Control Commands

### Set Power
**Status**: ✅ Verified

```json
// Power On
Request:  {"comhead": "set poweronoff", "language": 0, "power": 1}
Response: {"comhead": "set poweronoff", "result": 1}

// Power Off (Standby)
Request:  {"comhead": "set poweronoff", "language": 0, "power": 0}
Response: {"comhead": "set poweronoff", "result": 1}
```

**Source**: Verified against `src/orei_matrix.py` (line 573) and HAR file captures.

---

### Set Input→Output Routing
**Status**: ✅ Verified

```json
// Route input 2 to output 1
Request:  {"comhead": "video switch", "language": 0, "source": [1, 2]}
Response: {"comhead": "video switch", "result": 1}

// Route input 2 to ALL outputs (output index 0 = all)
Request:  {"comhead": "video switch", "language": 0, "source": [0, 2]}
Response: {"comhead": "video switch", "result": 1}
```

**Notes**: 
- `source` is `[output_index, input_index]` (output first, then input)
- Use `output_index = 0` to route to all outputs
- Both indices are 1-indexed (except the "all outputs" case uses 0)
- **Source**: Verified against `src/orei_matrix.py` (line 506) and HAR file `docs/route all http calls.har`

---

### Recall Preset
**Status**: ✅ Verified

```json
Request:  {"comhead": "preset set", "language": 0, "index": 1}
Response: {"comhead": "preset set", "result": 1}
```

**Notes**: 
- Index is 1-8 for the 8 hardware presets
- **Source**: Verified against `src/orei_matrix.py` (line 357)

---

### Save Preset
**Status**: ✅ Implemented

```json
Request:  {"comhead": "preset save", "language": 0, "index": 1}
Response: {"comhead": "preset save", "result": 1}
```

**Notes**: Saves the current routing configuration to the specified preset slot.

---

### Set Beep
**Status**: 🔄 Implemented

```json
Request:  {"comhead": "set beep", "beep": 1}  // 1=on, 0=off
Response: {"comhead": "set beep", "result": "success"}
```

---

### Set Panel Lock
**Status**: 🔄 Implemented

```json
Request:  {"comhead": "set panel lock", "lock": 1}  // 1=locked, 0=unlocked
Response: {"comhead": "set panel lock", "result": "success"}
```

---

### Set CEC Enable
**Status**: ✅ Implemented

```json
Request:  {
  "comhead": "set cec index",
  "language": 0,
  "inputindex": [1,0,0,0,0,0,0,0],   // Enable CEC on input 1 only (8-element array)
  "outputindex": [1,1,0,0,0,0,0,0]   // Enable CEC on outputs 1-2 (8-element array)
}
Response: {"comhead": "set cec index", "result": 1}
```

**Notes**:
- Use `get cec status` first to check current CEC enable state
- `inputindex` and `outputindex` are 8-element arrays (one entry per port)
- Value 1 = CEC enabled on that port, 0 = CEC disabled
- **Source**: Verified against `src/orei_matrix.py` (line 1297)

---

## CEC Commands

### CEC Command Format
**Status**: ✅ Verified

The matrix uses a unified `cec command` format with an `index` field that maps to specific commands.

```json
// General format
Request:  {
  "comhead": "cec command",
  "language": 0,
  "object": 0,           // 0 = input device, 1 = output device
  "port": [0,0,1,0,0,0,0,0],  // 8-element array, target port = 1
  "index": 1             // Command index (see tables below)
}
Response: {"comhead": "cec command", "result": 1}
```

**Source**: Verified against `src/orei_matrix.py` (line 823).

### Input CEC Commands (Control Source Devices)

| Index | Description |
|-------|-------------|
| 1 | Power on |
| 2 | Power off/standby |
| 3 | Menu/Home |
| 4 | Back/Return |
| 5 | D-pad up |
| 6 | D-pad down |
| 7 | D-pad left |
| 8 | D-pad right |
| 9 | D-pad enter (Select/OK) |
| 10 | Play |
| 11 | Pause |
| 12 | Stop |
| 13 | Rewind |
| 14 | Fast forward |
| 15 | Previous track |
| 16 | Next track |
| 17 | Mute toggle |
| 18 | Volume up |
| 19 | Volume down |

---

### Output CEC Commands (Control TVs/Displays)

| Index | Description |
|-------|-------------|
| 1 | Power on |
| 2 | Power off/standby |
| 3 | Mute toggle |
| 4 | Volume up |
| 5 | Volume down |
| 6 | Set active source (make TV switch to this input) |

---

## Output Settings Commands

### Set Output Stream On/Off
**Status**: ✅ Implemented

```json
Request:  {"comhead": "set output stream", "output": 1, "enable": 1}
Response: {"comhead": "set output stream", "result": 1}
```

**Notes**: 
- Enables/disables video output per port. Useful for "blank" scenarios.
- `enable: 1` = on, `enable: 0` = off
- **Source**: Verified against `src/orei_matrix.py` (line 1731)

---

### Set Output HDCP Mode
**Status**: ✅ Implemented

```json
Request:  {"comhead": "set output hdcp", "output": 1, "hdcp": 3}
Response: {"comhead": "set output hdcp", "result": 1}
```

**HDCP Modes**:
| Value | Description |
|-------|-------------|
| 1 | HDCP 1.4 |
| 2 | HDCP 2.2 |
| 3 | Follow Sink |
| 4 | Follow Source |
| 5 | User Mode |

**Source**: Verified against `src/orei_matrix.py` (line 1758)

---

### Set Output HDR Mode
**Status**: ✅ Implemented

```json
Request:  {"comhead": "set output hdr", "output": 1, "hdr": 1}
Response: {"comhead": "set output hdr", "result": 1}
```

**HDR Modes**:
| Value | Description |
|-------|-------------|
| 1 | Passthrough |
| 2 | HDR to SDR |
| 3 | Auto (follow sink EDID) |

**Source**: Verified against `src/orei_matrix.py` (line 1784)

---

### Set Output Video Mode (Scaler)
**Status**: ✅ Implemented

```json
Request:  {"comhead": "set output scaler", "output": 1, "scaler": 1}
Response: {"comhead": "set output scaler", "result": 1}
```

**Scaler Modes**:
| Value | Description |
|-------|-------------|
| 1 | Passthrough |
| 2 | 8K→4K |
| 3 | 8K/4K→1080p |
| 4 | Auto (follow sink EDID) |
| 5 | Audio Only |

**Source**: Verified against `src/orei_matrix.py` (line 1810)

---

### Set Output ARC
**Status**: ✅ Implemented

```json
Request:  {"comhead": "set output arc", "output": 1, "arc": 1}
Response: {"comhead": "set output arc", "result": 1}
```

**Notes**: Enable/disable ARC (Audio Return Channel) per output. `arc: 1` = on, `arc: 0` = off.

**Source**: Verified against `src/orei_matrix.py` (line 1832)

---

### Set Output Audio Mute
**Status**: ✅ Implemented

```json
Request:  {"comhead": "set output mute", "output": 1, "mute": 1}
Response: {"comhead": "set output mute", "result": 1}
```

**Notes**: Mute audio on specific output. `mute: 1` = muted, `mute: 0` = unmuted.

**Source**: Verified against `src/orei_matrix.py` (line 1855)

---

## EDID Commands

### Set Input EDID Mode
**Status**: 🔄 Implemented (needs hardware testing)

```json
Request:  {"comhead": "set input edid", "input": 1, "edid": 36}
Response: {"comhead": "set input edid", "result": "success"}
```

**EDID Mode Values:**

| Mode | Description |
|------|-------------|
| 1 | 1080p 2CH |
| 2 | 1080p 5.1CH |
| 3 | 1080p 7.1CH |
| 4 | 1080p 3D 2CH |
| 5 | 1080p 3D 5.1CH |
| 6 | 1080p 3D 7.1CH |
| 7 | 4K30 2CH |
| 8 | 4K30 5.1CH |
| 9 | 4K30 7.1CH |
| 10 | 4K60 5.1CH |
| 11 | 4K60 7.1CH |
| 12 | 4K60 4:4:4 2CH |
| 13 | 4K60 4:4:4 5.1CH |
| 14 | 4K60 4:4:4 7.1CH |
| 15-22 | Copy from Output 1-8 |
| 33 | 4K60 HDR 2CH |
| 34 | 4K60 HDR 5.1CH |
| 35 | 4K60 HDR 7.1CH |
| 36 | 4K60 HDR Atmos |
| 37 | 8K30 |
| 38 | 8K60 |

**Notes**: 
- EDID settings are per-input and determine what the matrix reports to source devices
- Modes 15-22 copy EDID from connected displays (outputs 1-8)
- Higher modes (33-38) require compatible hardware

---

### Copy EDID from Output
**Status**: 🔄 Implemented (needs hardware testing)

```json
// Copies EDID from a connected display to an input
Request:  {"comhead": "copy edid", "input": 1, "output": 1}
Response: {"comhead": "copy edid", "result": "success"}
```

**Notes**: Useful for letting source devices see the actual capabilities of a connected display.

---

## System Commands

### Reboot
**Status**: ❓ Discovered from drivers

```json
Request:  {"comhead": "set reboot"}
Response: (connection will drop)
```

---

### Set LCD On Time
**Status**: 🔄 Implemented (needs hardware testing)

```json
Request:  {"comhead": "set lcd on time", "time": 3}
Response: {"comhead": "set lcd on time", "result": "success"}
```

**LCD Timeout Mode Values:**

| Mode | Description |
|------|-------------|
| 0 | Off (LCD disabled) |
| 1 | Always on |
| 2 | 15 seconds |
| 3 | 30 seconds |
| 4 | 60 seconds |

**Notes**: Controls the front panel LCD display timeout. Useful for reducing light pollution in dark rooms.

---

## External Audio Commands

### Set Ext-Audio Mode
**Status**: ❓ Discovered from drivers

```json
// Modes: 
// 0 = Bind to input (audio follows video source)
// 1 = Bind to output (audio follows output)
// 2 = Matrix mode (independent audio routing)
```

---

### Set Ext-Audio Source
**Status**: ❓ Discovered from drivers

```json
// Select audio source (1-16) for each ext-audio output
```

---

### Set Ext-Audio Enable
**Status**: ❓ Discovered from drivers

```json
// Enable/disable ext-audio output per port
```

---

## Verification Needed

### High Priority
1. **CEC Enable Requirement**: Do CEC commands require the port to be enabled first?
   - Test plan: 
     1. Check current CEC status (`get cec status`)
     2. Try CEC command with port disabled
     3. Enable port (`set cec index`)
     4. Try CEC command again
     5. Compare results

2. **Output Stream Control**: Verify JSON format for enabling/disabling output streams

### Medium Priority
3. **HDCP/HDR/Scaler Settings**: Verify JSON command format from RTI serial commands
4. **ARC Control**: Test ARC enable/disable on supported outputs
5. **Audio Mute**: Verify per-output audio mute

### Low Priority
6. **LCD Settings**: Test LCD on-time settings
7. **Ext-Audio Routing**: Test external audio matrix features

---

## Source References

1. **HAR File** (`matrix more http payloads.har`): Captured from OREI web UI
2. **RTI Driver** (`BK-808_CN_AV.rtidriver`): Contains serial command formats and variables
3. **Control4 Driver** (`driver.lua`): Contains Lua implementation with serial commands
4. **Web UI**: Live testing at https://193.168.0.100/

---

## Serial Command Reference (from Drivers)

The Control4/RTI drivers use serial commands in this format:
```
s cec in <port> <command>      // Input CEC
s cec hdmi out <port> <command> // Output CEC
s out <port> stream <0|1>       // Output stream
s av <input> <output>           // Route input to output
s preset recall <index>         // Recall preset
s preset save <index>           // Save preset
s power <0|1>                   // Power control
s beep <0|1>                    // Beep control
s lock <0|1>                    // Panel lock
```

These translate to JSON `{"comhead": "...", ...}` format for HTTP API.

---

## Implementation Status Summary

| Category | Commands | Verified | Implemented | Discovered |
|----------|----------|----------|-------------|------------|
| Auth | 1 | 1 | 1 | 0 |
| Status | 9 | 9 | 9 | 0 |
| Control | 4 | 4 | 4 | 0 |
| Naming | 2 | 2 | 2 | 0 |
| Output Settings | 6 | 6 | 6 | 0 |
| External Audio | 3 | 3 | 3 | 0 |
| EDID | 1 | 1 | 1 | 0 |
| System | 4 | 4 | 4 | 0 |
| CEC Enable | 1 | 1 | 1 | 0 |
| CEC Commands | 2 | 2 | 2 | 0 |
| **Total** | **33** | **33** | **33** | **0** |

### Notes on Status
- **Verified**: Confirmed working with real hardware AND code implementation exists
- **Implemented**: Code exists in `src/orei_matrix.py` but not yet tested with hardware
- **Discovered**: Found in vendor drivers/HAR files but not yet implemented in code

### Commands NOT Yet Implemented
- **Network configuration** (IP/subnet/gateway) - vendor supports via telnet, no HTTP equivalent found
- **Factory reset** - vendor has `reset!` telnet command, no HTTP equivalent found
- **LCD logo customization** - vendor has `s logo1 *!` telnet command, no HTTP equivalent found
- **Firmware update** - vendor method not yet identified
- **User-defined EDID upload** - only preset EDID modes (1-47) currently supported

---

*Last Updated: June 19, 2026*
*Document Version: 2.0*
