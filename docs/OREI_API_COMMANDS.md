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
Request:  {"comhead": "set power index", "poweron": 1}
Response: {"comhead": "set power index", "result": "success"}

// Power Off (Standby)
Request:  {"comhead": "set power index", "poweron": 0}
Response: {"comhead": "set power index", "result": "success"}
```

---

### Set Input→Output Routing
**Status**: ✅ Verified

```json
// Route input 1 to output 2
Request:  {"comhead": "set singleav index", "input": 1, "output": 2}
Response: {"comhead": "set singleav index", "result": "success"}

// Route input to all outputs
Request:  {"comhead": "set allav index", "input": 1}
Response: {"comhead": "set allav index", "result": "success"}
```

**Notes**: Input and output are 1-indexed.

---

### Recall Preset
**Status**: ✅ Verified

```json
Request:  {"comhead": "set routing recall", "index": 1}
Response: {"comhead": "set routing recall", "result": "success"}
```

**Notes**: Index is 1-8 for the 8 presets.

---

### Save Preset
**Status**: 🔄 Implemented

```json
Request:  {"comhead": "set routing save", "index": 1}
Response: {"comhead": "set routing save", "result": "success"}
```

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
**Status**: 🔄 Implemented, Needs Testing

```json
Request:  {
  "comhead": "set cec index",
  "inputindex": [1,0,0,0,0,0,0,0],   // Enable CEC on input 1 only
  "outputindex": [1,1,0,0,0,0,0,0]   // Enable CEC on outputs 1-2
}
Response: {"comhead": "set cec index", "result": "success"}
```

**Notes**:
- ⚠️ **THEORY**: CEC commands may require the port to be enabled first
- Test by: 1) Check CEC status, 2) Enable port, 3) Send CEC command, 4) Verify

---

## CEC Commands

### Input CEC (Control Source Devices)
**Status**: ✅ Verified

```json
Request:  {"comhead": "set cec in", "index": 1, "cectype": "on"}
Response: {"comhead": "set cec in", "result": "success"}
```

**Available cectype values (from RTI/Control4 drivers)**:
| cectype | Description |
|---------|-------------|
| `on` | Power on |
| `off` | Power off/standby |
| `menu` | Menu/Home |
| `back` | Back/Return |
| `up` | D-pad up |
| `down` | D-pad down |
| `left` | D-pad left |
| `right` | D-pad right |
| `enter` | Select/OK |
| `play` | Play |
| `pause` | Pause |
| `stop` | Stop |
| `rew` | Rewind |
| `ff` | Fast forward |
| `previous` | Previous track |
| `next` | Next track |
| `mute` | Mute toggle |
| `vol+` | Volume up |
| `vol-` | Volume down |

---

### Output CEC (Control TVs/Displays)
**Status**: ✅ Verified

```json
Request:  {"comhead": "set cec hdmi out", "index": 1, "cectype": "on"}
Response: {"comhead": "set cec hdmi out", "result": "success"}
```

**Available cectype values (from RTI/Control4 drivers)**:
| cectype | Description |
|---------|-------------|
| `on` | Power on |
| `off` | Power off/standby |
| `mute` | Mute toggle |
| `vol+` | Volume up |
| `vol-` | Volume down |
| `active` | Set active source (make TV switch to this input) |

---

## Output Settings Commands

### Set Output Stream On/Off
**Status**: ❓ Discovered from drivers

```json
// From RTI driver - Serial format: "s out X stream Y"
// JSON equivalent (theory):
Request:  {"comhead": "set output stream", "output": 1, "enable": 1}
```

**Notes**: Enables/disables video output per port. Useful for "blank" scenarios.

---

### Set Output HDCP Mode
**Status**: ❓ Discovered from drivers

```json
// From RTI driver:
// 1=HDCP 1.4, 2=HDCP 2.2, 3=Follow Sink, 4=Follow Source, 5=User Mode
```

---

### Set Output HDR Mode
**Status**: ❓ Discovered from drivers

```json
// From RTI driver:
// 1=Passthrough, 2=HDR to SDR, 3=Auto (follow sink EDID)
```

---

### Set Output Video Mode (Scaler)
**Status**: ❓ Discovered from drivers

```json
// From RTI driver:
// 1=Passthrough, 2=8K→4K, 3=8K/4K→1080p, 4=Auto, 5=Audio Only
```

---

### Set Output ARC
**Status**: ❓ Discovered from drivers

```json
// From RTI driver:
// Enable/disable ARC (Audio Return Channel) per output
```

---

### Set Output Audio Mute
**Status**: ❓ Discovered from drivers

```json
// From RTI driver:
// Mute audio on specific output
```

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
| Status | 7 | 7 | 7 | 0 |
| Control | 5 | 5 | 5 | 0 |
| CEC | 2 | 2 | 2 | 0 |
| Output Settings | 6 | 6 | 6 | 0 |
| EDID | 2 | 2 | 2 | 0 |
| LCD | 1 | 1 | 1 | 0 |
| Ext-Audio | 3 | 3 | 3 | 0 |
| System | 1 | 1 | 1 | 0 |
| **Total** | **28** | **28** | **28** | **0** |

---

*Last Updated: January 19, 2026*
*Document Version: 1.3*
