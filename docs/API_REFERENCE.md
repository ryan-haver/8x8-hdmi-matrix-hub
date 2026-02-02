# REST API Reference

> **Status**: ✅ Implemented (v2.10.0 - Profiles & CEC Macros)

The REST API provides HTTP endpoints for external integrations, enabling control from:
- **Flic smart buttons** - via HTTP requests
- **Home Assistant** - via REST commands or custom component
- **Custom scripts** - curl, Python, Node.js, etc.
- **Any HTTP-capable device** - IoT devices, automation platforms
- **WebSocket** - Real-time status updates
- **Web UI** - Responsive browser-based control panel

## API Version

**Current Version: 2.10.0**

| Version | Features Added |
|---------|--------------|
| 2.10.0 | Profiles (enhanced scenes with macro support) |
| 2.9.0 | CEC Macros (multi-step command sequences) |
| 2.8.0 | Web UI, /api/info endpoint, debug panel |
| 2.7.0 | Scenes (activity-based routing) |
| 2.6.0 | External audio matrix routing |
| 2.5.0 | EDID management, LCD timeout |
| 2.4.0 | System reboot, route to all |
| 2.3.0 | WebSocket real-time updates |
| 2.2.0 | Advanced output control (HDCP, HDR, scaler, ARC) |
| 2.1.0 | Input cycling, per-output source |
| 2.0.0 | Initial REST API |

## Base URL

```
http://<host>:8080/api
```

Default: `http://192.168.1.145:8080/api` (Docker host IP)

## Response Format

All responses are JSON with consistent structure:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

Error responses:
```json
{
  "success": false,
  "data": null,
  "error": "Error message here"
}
```

HTTP Status Codes:
- `200` - Success
- `400` - Bad request (invalid parameters)
- `500` - Server error
- `503` - Service unavailable (matrix not connected)

---

## Endpoints

### Health & Status

#### GET /api/health
Health check endpoint for monitoring.

```bash
curl http://localhost:8080/api/health
```

Response:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "orei-hdmi-matrix"
  }
}
```

#### GET /api/status
Get full matrix status including power, routing, and device names.

```bash
curl http://localhost:8080/api/status
```

Response:
```json
{
  "success": true,
  "data": {
    "connected": true,
    "host": "192.168.0.100",
    "port": 443,
    "power": "on",
    "routing": [1, 2, 3, 4, 5, 6, 7, 8],
    "input_names": ["IN01-PS3", "IN02-AppleTV", ...],
    "output_names": ["OUT01-Living Room", ...],
    "preset_names_map": {
      "1": "PS3",
      "2": "AppleTV",
      ...
    }
  }
}
```

#### GET /api/presets
List all presets with their names.

```bash
curl http://localhost:8080/api/presets
```

Response:
```json
{
  "success": true,
  "data": {
    "presets": [
      {"number": 1, "name": "PS3", "endpoint": "/api/preset/1"},
      {"number": 2, "name": "AppleTV", "endpoint": "/api/preset/2"},
      ...
    ]
  }
}
```

#### GET /api/inputs
List all inputs with their names and CEC endpoints.

```bash
curl http://localhost:8080/api/inputs
```

#### GET /api/outputs
List all outputs with their names and CEC endpoints.

```bash
curl http://localhost:8080/api/outputs
```

---

### Control

#### POST /api/preset/{1-8}
Recall a preset (switch all outputs to match the preset configuration).

```bash
# Switch to AppleTV (preset 2)
curl -X POST http://localhost:8080/api/preset/2
```

Response:
```json
{
  "success": true,
  "data": {
    "preset": 2,
    "name": "AppleTV",
    "message": "Preset 2 (AppleTV) activated"
  }
}
```

#### POST /api/switch
Route a specific input to a specific output.

```bash
# Route input 3 (Computer) to output 1
curl -X POST http://localhost:8080/api/switch \
  -H "Content-Type: application/json" \
  -d '{"input": 3, "output": 1}'
```

Request body:
```json
{
  "input": 3,
  "output": 1
}
```

Response:
```json
{
  "success": true,
  "data": {
    "input": 3,
    "output": 1,
    "message": "Input 3 routed to output 1"
  }
}
```

#### POST /api/power/on
Power on the matrix.

```bash
curl -X POST http://localhost:8080/api/power/on
```

#### POST /api/power/off
Power off the matrix (standby).

```bash
curl -X POST http://localhost:8080/api/power/off
```

---

### EDID Management (v2.5.0+)

Configure EDID settings per input to ensure optimal compatibility with source devices.

#### GET /api/edid/modes
List all available EDID modes.

```bash
curl http://localhost:8080/api/edid/modes
```

Response:
```json
{
  "success": true,
  "data": {
    "modes": {
      "1": "1080p 2CH", "2": "1080p 5.1CH", "3": "1080p 7.1CH",
      "4": "1080p 3D 2CH", "5": "1080p 3D 5.1CH", "6": "1080p 3D 7.1CH",
      "7": "4K30 2CH", "8": "4K30 5.1CH", "9": "4K30 7.1CH",
      "10": "4K60 420 2CH", "11": "4K60 420 5.1CH", "12": "4K60 420 7.1CH",
      "13": "4K60 444 2CH", "14": "4K60 444 7.1CH",
      "15": "Copy from Output 1", "16": "Copy from Output 2", ...
      "33": "4K60 HDR 2CH", "34": "4K60 HDR 5.1CH", "35": "4K60 HDR 7.1CH",
      "36": "4K60 HDR Atmos", "37": "8K30", "38": "8K60"
    }
  }
}
```

#### GET /api/status/edid
Get current EDID configuration for all inputs.

```bash
curl http://localhost:8080/api/status/edid
```

Response:
```json
{
  "success": true,
  "data": {
    "inputs": {
      "1": {"mode": 36, "mode_name": "4K60 HDR Atmos"},
      "2": {"mode": 36, "mode_name": "4K60 HDR Atmos"},
      ...
    }
  }
}
```

#### POST /api/input/{1-8}/edid
Set EDID mode for a specific input.

```bash
# Set input 1 to 4K60 HDR with Atmos
curl -X POST http://localhost:8080/api/input/1/edid \
  -H "Content-Type: application/json" \
  -d '{"mode": 36}'

# Copy EDID from output 1 to input 3
curl -X POST http://localhost:8080/api/input/3/edid \
  -H "Content-Type: application/json" \
  -d '{"mode": 15}'
```

---

### LCD Display Settings (v2.5.0+)

Control the front panel LCD display timeout.

#### GET /api/system/lcd/modes
List available LCD timeout modes.

```bash
curl http://localhost:8080/api/system/lcd/modes
```

Response:
```json
{
  "success": true,
  "data": {
    "modes": {
      "0": "Off",
      "1": "Always On",
      "2": "15 seconds",
      "3": "30 seconds",
      "4": "60 seconds"
    }
  }
}
```

#### POST /api/system/lcd
Set LCD display timeout.

```bash
# Set LCD to 30-second timeout
curl -X POST http://localhost:8080/api/system/lcd \
  -H "Content-Type: application/json" \
  -d '{"mode": 3}'
```

---

### External Audio Routing (v2.6.0+)

Control the external audio matrix for independent audio routing.

#### GET /api/ext-audio/modes
List available ext-audio modes.

```bash
curl http://localhost:8080/api/ext-audio/modes
```

Response:
```json
{
  "success": true,
  "data": {
    "modes": {
      "0": "Bind to Input",
      "1": "Bind to Output", 
      "2": "Matrix Mode"
    }
  }
}
```

**Mode Descriptions:**
- **Bind to Input (0)**: Audio follows video input selection
- **Bind to Output (1)**: Audio follows video output routing  
- **Matrix Mode (2)**: Independent audio routing (set per-output source)

#### GET /api/status/ext-audio
Get current external audio configuration.

```bash
curl http://localhost:8080/api/status/ext-audio
```

Response:
```json
{
  "success": true,
  "data": {
    "mode": 2,
    "mode_name": "Matrix Mode",
    "outputs": {
      "1": {"enabled": true, "source": 3, "source_name": "Computer"},
      "2": {"enabled": false, "source": 1, "source_name": "PS3"},
      ...
    }
  }
}
```

#### POST /api/ext-audio/mode
Set the global ext-audio mode.

```bash
# Enable Matrix Mode for independent audio routing
curl -X POST http://localhost:8080/api/ext-audio/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": 2}'
```

#### POST /api/ext-audio/{1-8}/enable
Enable or disable ext-audio on a specific output.

```bash
# Enable ext-audio on output 1
curl -X POST http://localhost:8080/api/ext-audio/1/enable \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

#### POST /api/ext-audio/{1-8}/source
Set audio source for ext-audio output (Matrix Mode only).

```bash
# Route input 3's audio to ext-audio output 1
curl -X POST http://localhost:8080/api/ext-audio/1/source \
  -H "Content-Type: application/json" \
  -d '{"input": 3}'
```

---

### Scenes (v2.7.0+)

Save and recall named routing configurations (activity-based presets).

Scenes allow you to:
- Save complete matrix configurations with custom names
- Store routing plus optional settings (HDR, HDCP, audio mute)
- Recall configurations instantly
- Have unlimited scenes (vs. 8 hardware presets)

#### GET /api/scenes
List all saved scenes.

```bash
curl http://localhost:8080/api/scenes
```

Response:
```json
{
  "success": true,
  "data": {
    "scenes": [
      {"id": "movie_night", "name": "Movie Night", "output_count": 3},
      {"id": "gaming", "name": "Gaming Setup", "output_count": 2},
      {"id": "work", "name": "Work Mode", "output_count": 4}
    ]
  }
}
```

#### GET /api/scene/{id}
Get details of a specific scene.

```bash
curl http://localhost:8080/api/scene/movie_night
```

Response:
```json
{
  "success": true,
  "data": {
    "id": "movie_night",
    "name": "Movie Night",
    "outputs": {
      "1": {"input": 2, "enabled": true, "audio_mute": false, "hdr_mode": 1},
      "2": {"input": 2, "enabled": true, "audio_mute": true}
    }
  }
}
```

#### POST /api/scene
Create or update a scene.

```bash
curl -X POST http://localhost:8080/api/scene \
  -H "Content-Type: application/json" \
  -d '{
    "id": "movie_night",
    "name": "Movie Night",
    "outputs": {
      "1": {"input": 2, "hdr_mode": 1},
      "2": {"input": 2, "audio_mute": true}
    }
  }'
```

**Output configuration options:**
- `input` (required): Input number 1-8
- `enabled`: Enable/disable output (default: true)
- `audio_mute`: Mute audio (default: false)
- `hdr_mode`: HDR mode 1-3 (optional)
- `hdcp_mode`: HDCP mode 1-5 (optional)

#### DELETE /api/scene/{id}
Delete a scene.

```bash
curl -X DELETE http://localhost:8080/api/scene/movie_night
```

#### POST /api/scene/{id}/recall
Apply a scene's settings to the matrix.

```bash
curl -X POST http://localhost:8080/api/scene/movie_night/recall
```

Response:
```json
{
  "success": true,
  "data": {
    "scene": "Movie Night",
    "applied": ["Output 1 → Input 2", "Output 2 → Input 2"],
    "errors": null
  }
}
```

#### POST /api/scene/save-current
Save the current matrix state as a new scene.

```bash
curl -X POST http://localhost:8080/api/scene/save-current \
  -H "Content-Type: application/json" \
  -d '{"id": "current", "name": "Current Setup"}'
```

---

### Profiles (v2.10.0+)

Enhanced scenes with macro support. Profiles are the preferred API for saving and recalling configurations.

Profiles extend scenes with:
- **Icon support**: Display custom emoji or text icons
- **Macro assignments**: Associate macros with a profile for quick access
- **Power-on macro**: Auto-execute a macro when profile is recalled
- **Power-off macro**: Execute a macro before switching away (future use)

> **Note:** Scene endpoints (`/api/scenes/*`) remain available for backward compatibility.

#### GET /api/profiles
List all saved profiles.

```bash
curl http://localhost:8080/api/profiles
```

Response:
```json
{
  "success": true,
  "data": {
    "profiles": [
      {"id": "movie_night", "name": "Movie Night", "icon": "🎬", "output_count": 3, "has_macros": true},
      {"id": "gaming", "name": "Gaming Setup", "icon": "🎮", "output_count": 2}
    ]
  }
}
```

#### GET /api/profile/{id}
Get details of a specific profile.

```bash
curl http://localhost:8080/api/profile/movie_night
```

Response:
```json
{
  "success": true,
  "data": {
    "id": "movie_night",
    "name": "Movie Night",
    "icon": "🎬",
    "outputs": {
      "1": {"input": 2, "enabled": true, "audio_mute": false, "hdr_mode": 1},
      "2": {"input": 2, "enabled": true, "audio_mute": true}
    },
    "macros": ["all_tvs_on", "set_volume"],
    "power_on_macro": "all_tvs_on",
    "power_off_macro": null,
    "cec_config": {...}
  }
}
```

#### POST /api/profile
Create or update a profile.

```bash
curl -X POST http://localhost:8080/api/profile \
  -H "Content-Type: application/json" \
  -d '{
    "id": "movie_night",
    "name": "Movie Night",
    "icon": "🎬",
    "outputs": {
      "1": {"input": 2, "hdr_mode": 1},
      "2": {"input": 2, "audio_mute": true}
    },
    "macros": ["all_tvs_on"],
    "power_on_macro": "all_tvs_on"
  }'
```

**Profile configuration options:**
- `id` (required): Unique profile identifier
- `name` (required): Display name
- `outputs` (required): Output routing configuration
- `icon`: Display icon (emoji or text, default: "📺")
- `macros`: Array of macro IDs to show in profile
- `power_on_macro`: Macro ID to execute on recall
- `power_off_macro`: Macro ID to execute on switch (future)
- `cec_config`: CEC pinning configuration

#### PUT /api/profile/{id}
Update an existing profile's properties.

```bash
curl -X PUT http://localhost:8080/api/profile/movie_night \
  -H "Content-Type: application/json" \
  -d '{"icon": "🎥", "power_on_macro": "theater_mode"}'
```

#### DELETE /api/profile/{id}
Delete a profile.

```bash
curl -X DELETE http://localhost:8080/api/profile/movie_night
```

#### POST /api/profile/{id}/recall
Apply a profile's settings to the matrix and execute power-on macro.

```bash
curl -X POST http://localhost:8080/api/profile/movie_night/recall
```

Response:
```json
{
  "success": true,
  "data": {
    "profile": "Movie Night",
    "applied": ["Output 1 → Input 2", "Output 2 → Input 2"],
    "errors": null,
    "power_on_macro": {"success": true, "executed_steps": 3}
  }
}
```

#### GET /api/profile/{id}/macros
Get macros assigned to a profile.

```bash
curl http://localhost:8080/api/profile/movie_night/macros
```

Response:
```json
{
  "success": true,
  "data": {
    "profile_id": "movie_night",
    "macros": ["all_tvs_on", "set_volume"],
    "macro_details": [
      {"id": "all_tvs_on", "name": "All TVs On", "icon": "📺"},
      {"id": "set_volume", "name": "Set Volume", "icon": "🔊"}
    ],
    "power_on_macro": "all_tvs_on",
    "power_off_macro": null
  }
}
```

#### POST /api/profile/{id}/macros
Update macro assignments for a profile.

```bash
curl -X POST http://localhost:8080/api/profile/movie_night/macros \
  -H "Content-Type: application/json" \
  -d '{
    "macros": ["all_tvs_on", "set_volume", "dim_lights"],
    "power_on_macro": "theater_setup"
  }'
```

---

### CEC Control

Send CEC commands to input devices (sources) or output devices (TVs/displays).

#### GET /api/cec/commands
List all available CEC commands.

```bash
curl http://localhost:8080/api/cec/commands
```

Response:
```json
{
  "success": true,
  "data": {
    "input_commands": ["back", "down", "fast_forward", "left", "menu", "mute", ...],
    "output_commands": ["back", "down", "left", "menu", "mute", "power_off", ...],
    "usage": {
      "input": "POST /api/cec/input/{1-8}/{command}",
      "output": "POST /api/cec/output/{1-8}/{command}"
    }
  }
}
```

#### POST /api/cec/input/{1-8}/{command}
Send CEC command to an input device (PS3, AppleTV, etc.).

**Available commands:**
- Navigation: `up`, `down`, `left`, `right`, `select`, `menu`, `back`
- Playback: `play`, `pause`, `stop`, `previous`, `next`, `rewind`, `fast_forward`
- Power: `power_on`, `power_off`
- Volume: `volume_up`, `volume_down`, `mute`

```bash
# Play on AppleTV (input 2)
curl -X POST http://localhost:8080/api/cec/input/2/play

# Power on PS5 (input 6)
curl -X POST http://localhost:8080/api/cec/input/6/power_on

# Navigate up on Shield (input 5)
curl -X POST http://localhost:8080/api/cec/input/5/up
```

Response:
```json
{
  "success": true,
  "data": {
    "input": 2,
    "name": "AppleTV",
    "command": "play",
    "message": "CEC play sent to AppleTV"
  }
}
```

#### POST /api/cec/output/{1-8}/{command}
Send CEC command to an output device (TV/display).

**Available commands:**
- Navigation: `up`, `down`, `left`, `right`, `select`, `menu`, `back`
- Power: `power_on`, `power_off`
- Volume: `volume_up`, `volume_down`, `mute`

```bash
# Power on TV (output 1)
curl -X POST http://localhost:8080/api/cec/output/1/power_on

# Mute TV
curl -X POST http://localhost:8080/api/cec/output/1/mute
```

---

## Integration Examples

### Flic Button

Configure your Flic button to make HTTP requests:

**Single click - AppleTV:**
```
POST http://192.168.1.145:8080/api/preset/2
```

**Double click - Play/Pause:**
```
POST http://192.168.1.145:8080/api/cec/input/2/play
```

### Home Assistant REST Commands

```yaml
# configuration.yaml
rest_command:
  orei_preset_appletv:
    url: "http://192.168.1.145:8080/api/preset/2"
    method: POST
    
  orei_preset_ps5:
    url: "http://192.168.1.145:8080/api/preset/6"
    method: POST
    
  orei_cec_play:
    url: "http://192.168.1.145:8080/api/cec/input/{{ input }}/play"
    method: POST
    
  orei_switch:
    url: "http://192.168.1.145:8080/api/switch"
    method: POST
    content_type: "application/json"
    payload: '{"input": {{ input }}, "output": {{ output }}}'
```

### Shell Script

```bash
#!/bin/bash
# Movie night script

OREI_API="http://192.168.1.145:8080/api"

# Switch to Shield
curl -X POST "$OREI_API/preset/5"

# Power on TV
curl -X POST "$OREI_API/cec/output/1/power_on"

# Start playback
sleep 2
curl -X POST "$OREI_API/cec/input/5/play"
```

### Python

```python
import requests

OREI_API = "http://192.168.1.145:8080/api"

def switch_to_appletv():
    r = requests.post(f"{OREI_API}/preset/2")
    return r.json()["success"]

def play_pause(input_num):
    r = requests.post(f"{OREI_API}/cec/input/{input_num}/play")
    return r.json()

# Switch and start playback
switch_to_appletv()
play_pause(2)
```

---

## Error Handling

### Matrix Not Connected

If the matrix is not connected, endpoints return:

```json
{
  "success": false,
  "data": null,
  "error": "Matrix not connected"
}
```

The integration will automatically reconnect when the matrix becomes available.

### Invalid Parameters

```json
{
  "success": false,
  "data": null,
  "error": "Preset must be 1-8"
}
```

```json
{
  "success": false,
  "data": null,
  "error": "Unknown command 'invalid'. Available: back, down, fast_forward, ..."
}
```

---

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `REST_API_PORT` | `8080` | Port for REST API server |
| `REST_API_ENABLED` | `true` | Enable/disable REST API |

To disable the REST API:
```bash
REST_API_ENABLED=false python src/driver.py
```

Or in docker-compose.yml:
```yaml
environment:
  - REST_API_ENABLED=false
```
