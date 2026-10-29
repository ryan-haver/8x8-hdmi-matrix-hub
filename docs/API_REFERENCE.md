# REST API Reference

> **Status**: ✅ Implemented (v2.10.0 - Profiles & CEC Macros)

The REST API provides HTTP endpoints for external integrations, enabling control from:
- **Flic smart buttons** - via HTTP requests
- **Home Assistant** - via REST commands or custom component
- **Custom scripts** - curl, Python, Node.js, etc.
- **Any HTTP-capable device** - IoT devices, automation platforms
- **WebSocket** - Real-time status updates: the contract (every event, payload and when it is sent) is [`api/WEBSOCKET.md`](api/WEBSOCKET.md)
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

## Breaking Changes

v2.10.0 introduced the following breaking changes:

### Error Response Semantics

- **`POST /api/settings/test-connection`**: Returns `200` with `success: true` on successful connection, or `503` with `success: false` on failure (previously returned `200` with `connected: false`)
- **Handler errors**: Internal errors now return a correlation ID instead of raw exception text for security

### Input Validation

- **`POST /api/cec/macro`**: Validates all commands against a whitelist and all targets against the format `input_N` or `output_N`. Invalid commands or targets return `400` with descriptive error messages
- **`PUT /api/profile/{id}`**: Only whitelisted fields are accepted. Unknown fields are silently ignored with a warning log

### Accepted Fields Whitelist (Profile Update)

The following fields are accepted by `PUT /api/profile/{id}`:
`name`, `icon`, `outputs`, `cec_config`, `macros`, `power_on_macro`, `power_off_macro`, `pinned`, `pin_order`, `favorite`, `dashboard_visible`, `password_protected`, `passcode_hash`, `description`

## Base URL

```
http://<host>:8080/api
```

Default port: `8080`. Use the hub host's address; configure `API_PORT` to change it.

## Response Format & OpenAPI 3.1 Contract

Core JSON control responses use `ApiResponseEnvelope` (`#/components/schemas/ApiResponseEnvelope` in `GET /api/openapi.json`). Scene v2 handlers omit absent `data` or `error` fields and use `SceneV2ResponseEnvelope`; execution failures can carry partial-result data. The specification endpoint returns a raw OpenAPI document; `/api/docs` returns HTML.

`POST /api/input/next` and `/api/input/previous` accept `output=1` through `8`
(default `1`) and optional `cycle=true|false`. Omitted `cycle` wraps between
inputs 1 and 8; lowercase `false` clamps at either boundary. Other explicit
values return `400` before routing changes. Responses preserve the operation's
`previous_input` and `current_input`, including during concurrent requests.

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

Error responses include a client-safe message and, for unexpected server errors (`500`), an `error_id` correlation identifier that matches the server log line:
```json
{
  "success": false,
  "data": null,
  "error": "Error message here",
  "error_id": "a1b2c3d4"
}
```

HTTP Status Codes:
- `200` - Success
- `201` - Created (e.g., `POST /api/auth/api-keys`, `POST /api/v2/scenes`)
- `207` - Multi-Status (partial profile recall)
- `400` - Bad request (invalid parameters or validation failure)
- `401` - Unauthorized (session unlock, PIN, or API key required)
- `403` - Forbidden (cross-origin mutation denied or insufficient access level)
- `404` - Resource not found
- `415` - Unsupported Media Type (JSON `Content-Type: application/json` required for non-empty mutation bodies)
- `421` - Misdirected Request (`Host` header not in `ALLOWED_HOSTS`, localhost, `.local`, or IP literal)
- `429` - Too Many Requests (rate limit or PIN lockout)
- `500` - Internal server error (includes `error_id`)
- `503` - Service unavailable (matrix not connected)

### Authentication & Security Schemes

Read endpoints (`GET`) are open by default (except `GET /api/auth/devices` and `GET /api/auth/api-keys`, which require `admin` when `ADMIN_PIN` is set). Mutation endpoints (`POST`, `PUT`, `DELETE`, `PATCH`) enforce two access tiers when `ADMIN_PIN` or `CONTROL_PIN` is configured:

| Scheme | OpenAPI Name | Location | Tier | Description |
|--------|--------------|----------|------|-------------|
| Session Cookie | `AdminSessionCookie` | Cookie: `orei_session` | `admin` or `control` | Set by `POST /api/auth/unlock` (or `/api/auth/login`). Refreshed on activity (`30m` idle timeout). |
| API Key Header | `ControlApiKeyHeader` | Header: `X-API-Key` | `control` | API key created via `POST /api/auth/api-keys` or configured via `API_KEY` / `CONTROL_API_KEY`. |
| API Key Query | `ControlApiKeyQuery` | Query: `?key=<token>` | `control` | Same API key passed in URL query string for clients that cannot set HTTP headers. |
| Admin PIN Header | `AdminPinHeader` | Header: `X-Admin-PIN` | `admin` | Direct Admin PIN verification for stateless admin requests when `ADMIN_PIN` is configured. |
| Remembered device | `RememberedDeviceCookie` | Cookie: `orei_device_token` | `control` | A device remembered during unlock; never grants admin access. |

---

## Endpoints

### Health, OpenAPI & Status

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
    "service": "orei-hdmi-matrix",
    "api_version": "2.10.0",
    "version": "2.10.0",
    "matrix": {
      "configured": true,
      "connected": true,
      "host": "192.168.0.100",
      "last_successful_poll": "2026-10-17T12:00:00+00:00",
      "telnet_connected": true
    },
    "runtime": {
      "uptime_s": 120.5,
      "loop_lag_ms": 0.4,
      "task_count": 6,
      "ws_clients": 1
    }
  },
  "error": null
}
```

#### GET /api/openapi.json
Returns the live OpenAPI 3.1.0 specification document generated from the application's registered routes (`src/hub/openapi.py`). Default server URL is relative (`/`).

```bash
curl http://localhost:8080/api/openapi.json
```

#### GET /api/docs
Serves the interactive Swagger UI HTML page backed by `/api/openapi.json` (with an offline route-catalog fallback for air-gapped LANs).

```bash
curl http://localhost:8080/api/docs
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
List all presets with their display names and the routing each slot holds.

`routing` is read from the matrix itself: each slot with Telnet
`r preset N` (the only preset read the BK-808 firmware answers). Slots changed
outside the hub (front panel, another client) are reported as stored, and a
custom save reports the whole slot it stored. The reads are cached for
`OREI_STATUS_CACHE_TTL` seconds (default 3); preset saves and other writes
expire the cache. `routing_source` says where the routing came from:

- `"matrix"`: read from the matrix slot. An empty mapping means the slot is empty.
- `"saved"`: the slot could not be read (Telnet not connected, no or incomplete
  answer); `routing` is the copy the hub saved last, which may be stale or
  empty. It is never presented as read from the matrix.

Names (and favourites) are the hub's (web app) data (BE-36).

```bash
curl http://localhost:8080/api/presets
```

Response:
```json
{
  "success": true,
  "data": {
    "presets": [
      {"number": 1, "name": "PS3", "routing": {"1": 1, "2": 1, "3": 2, "4": 2, "5": 5, "6": 6, "7": 1, "8": 1},
       "routing_source": "matrix", "endpoint": "/api/preset/1", "save_endpoint": "/api/preset/1/save"},
      {"number": 2, "name": "AppleTV", "routing": {}, "routing_source": "matrix",
       "endpoint": "/api/preset/2", "save_endpoint": "/api/preset/2/save"},
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
      "1": "1080p 2.0CH", "2": "1080p 5.1CH", "3": "1080p 7.1CH",
      "4": "4K30 2.0CH", ...
      "34": "8K FRL 12G HDR 2.0CH", "35": "8K FRL 12G HDR 5.1CH", "36": "8K FRL 12G HDR 7.1CH",
      "37": "User EDID 1", "38": "User EDID 2", "39": "User EDID 3",
      "40": "Copy from Output 1", ... "47": "Copy from Output 8"
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
      "1": {"mode": 36, "mode_name": "8K FRL 12G HDR 7.1CH"},
      "2": {"mode": 36, "mode_name": "8K FRL 12G HDR 7.1CH"},
      ...
    }
  }
}
```

#### POST /api/input/{1-8}/edid
Set EDID mode for a specific input. The ids are the matrix's own EDID list (1-47, see `GET /api/edid/modes` and `docs/OREI_API_COMMANDS.md`); 40-47 copy the EDID of output 1-8. Before WP-A4 part 2 the hub used a made-up table in which 15-22 meant "copy"; on the device 15-22 are built-in HDR EDIDs (BE-25).

```bash
# Set input 1 to 8K FRL 12G HDR 7.1CH
curl -X POST http://localhost:8080/api/input/1/edid \
  -H "Content-Type: application/json" \
  -d '{"mode": 36}'

# Copy EDID from output 1 to input 3 (same as {"mode": 40})
curl -X POST http://localhost:8080/api/input/3/edid \
  -H "Content-Type: application/json" \
  -d '{"copy_from_output": 1}'
```

Any other `mode` is rejected with 400.

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

### Scenes (v2.7.0+ — Legacy v1 Compatibility Aliases)

> **Deprecation / Compatibility Note**: The `/api/scenes` and `/api/scene/*` endpoints are **legacy v1 compatibility aliases** backed by the same storage as Profiles (`/api/profiles` and `/api/profile/*`). New integrations should use **Profiles** (`/api/profiles`, `/api/profile/{profile_id}`) for saved matrix configurations with macro/icon support, or **Scenes v2** (`/api/v2/scenes`, `/api/v2/scenes/{scene_id}`) for multi-step orchestrated scenes with step validation, per-profile overrides, and execution history.

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

The profile is created only from a complete read of the matrix: the routing
(`get video status`) and the output settings (`get output status`) of all
eight outputs. If either read fails or is incomplete, the answer is `502`
(`success: false`, the reason in `error`) and no profile is created (API-27).
Each output's `enabled` is its stream state as the matrix reports it
(`allout`: 1 on, 0 off); any other value is refused the same way (API-31).

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

**Accepted fields**: `name`, `icon`, `outputs`, `cec_config`, `macros`, `power_on_macro`, `power_off_macro`, `pinned`, `pin_order`, `favorite`, `dashboard_visible`, `password_protected`, `passcode_hash`, `description`. Unknown fields are silently ignored.

**Output settings** (create and edit): each output takes `input` (1-8),
`enabled`, `audio_mute`, and the optional `hdr_mode` (1-3), `hdcp_mode`,
`scaler_mode` (1-5: 1 passthrough, 2 8K to 4K, 3 8K/4K to 1080p, 4 auto,
5 audio only) and `arc` (`true`/`false`). Optional settings that are omitted
or `null` stay unset and are not returned. An invalid `scaler_mode` or `arc`
is answered with `400` and nothing is saved (API-22). Create and edit apply the
same checks: an output or input outside 1-8, or an output without `input`, is
answered with `400` and the profile is not changed (API-30). Profile recall and
scene profile steps apply a saved `scaler_mode` (`set video scaler`) and `arc`
(`set arc`); when a profile does not set them they are left as they are (API-29).

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
    "failed_outputs": [],
    "errors": null,
    "power_on_macro": {"success": true, "steps_executed": 2}
  },
  "error": null
}
```

Status: `200` when every output (routing, stream, mute, HDR, HDCP, scaler, ARC) and the
power-on macro were applied; `207` when only part was (`success: false`,
`failed_outputs` and `errors` say what the matrix did not accept); `500` when
nothing was; `403` with `passcode_required` / `invalid_passcode` for a
protected profile.

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

`PUT` is also supported. Set `power_on_macro` or `power_off_macro` to `null`
to clear that assignment; omitting a field preserves its current value. The
same clearing behavior applies to `PUT /api/profile/{id}`.

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

With `OREI_USE_TELNET_CEC=true`, commands use Telnet when connected. They fall
back to HTTP only when the matrix certainly did not run the Telnet command:
Telnet was not connected, or the matrix answered with an error code
(`E00`/`E01`). When the command was written but its acknowledgement was lost,
cut short or never came, the matrix may already have run it. Then only power on
and power off, which set a state and are safe to send twice, go on to HTTP
(BE-38); every other command (volume, mute, navigation, playback, `active`) is
not resent and the request fails with `500` (BE-37).

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

**Available commands** (the matrix's display CEC table has six keys, BE-14):
- Power: `power_on`, `power_off`
- Volume: `volume_up`, `volume_down`, `mute`
- `active` (make the display select the matrix)

Any other command (navigation, playback) is answered with 400 for outputs; send those to the source device on an input instead.

```bash
# Power on TV (output 1)
curl -X POST http://localhost:8080/api/cec/output/1/power_on

# Mute TV
curl -X POST http://localhost:8080/api/cec/output/1/mute
```

#### POST /api/cec/input/{1-8}/enable and /api/cec/output/{1-8}/enable

Set a port's CEC enable flag with `{"enabled": true}` or `{"enabled": false}`.
The hub reads the current input/output flags before replacing the device's
arrays, preserving other ports and serializing concurrent single-port edits.
If a complete current snapshot cannot be read, the route returns HTTP 500
without sending the write. Another controller can still change the device
between the read and write; the device protocol provides no atomic port edit.

---

## CEC Macros (v2.9.0+) ⭐

CEC Macros are saved sequences of CEC commands that can be executed atomically with optional delays between steps.

Creation (`POST`) and editing (`PUT`) apply the same limits: a name of at most
200 characters and a description of at most 2000. A longer one is answered with
`400` and the macro is not changed (API-28).

### Macro Step Format

Each macro consists of ordered steps. Each step specifies:
- `command`: CEC command name (e.g., `POWER_ON`, `POWER_OFF`, `MUTE`, `PLAY`)
- `targets`: List of target strings (e.g., `["input_1", "output_2"]`)
- `delay_ms`: Delay in milliseconds AFTER this step executes (default: 0)

### Target String Format

Targets use the format: `{type}_{port}` where type is `input` or `output` and port is 1-8.
Examples: `input_1`, `input_2`, `output_5`

#### GET /api/cec/macros
List all CEC macros.

```bash
curl http://localhost:8080/api/cec/macros
```

Response:
```json
{
  "success": true,
  "data": {
    "macros": [
      {
        "id": "theater-on",
        "name": "Theater On",
        "description": "Power on TV and soundbar, switch to movie input",
        "steps": [...],
        "created_at": "2026-06-19T10:30:00Z",
        "updated_at": "2026-06-19T10:30:00Z"
      }
    ]
  }
}
```

#### POST /api/cec/macro
Create a new CEC macro.

```bash
curl -X POST http://localhost:8080/api/cec/macro \
  -H "Content-Type: application/json" \
  -d '{
    "id": "theater-on",
    "name": "Theater On",
    "description": "Power on TV and soundbar, switch to movie input",
    "steps": [
      {"command": "POWER_ON", "targets": ["output_1", "output_2"], "delay_ms": 0},
      {"command": "POWER_ON", "targets": ["input_2"], "delay_ms": 3000},
      {"command": "ACTIVE", "targets": ["input_2"], "delay_ms": 1000}
    ]
  }'
```

**Validation**: Commands are validated against a whitelist. Valid input commands: `POWER_ON`, `POWER_OFF`, `UP`, `DOWN`, `LEFT`, `RIGHT`, `SELECT`, `MENU`, `BACK`, `PLAY`, `PAUSE`, `STOP`, `REWIND`, `FAST_FORWARD`, `PREVIOUS`, `NEXT`, `VOLUME_UP`, `VOLUME_DOWN`, `MUTE`. Valid output commands: `POWER_ON`, `POWER_OFF`, `MUTE`, `VOLUME_UP`, `VOLUME_DOWN`, `ACTIVE`. Targets must be formatted as `input_N` or `output_N` (N=1-8). Returns `400` with descriptive error message if validation fails.

#### GET /api/cec/macro/{id}
Get a specific CEC macro.

```bash
curl http://localhost:8080/api/cec/macro/theater-on
```

#### PUT /api/cec/macro/{id}
Update an existing CEC macro.

```bash
curl -X PUT http://localhost:8080/api/cec/macro/theater-on \
  -H "Content-Type: application/json" \
  -d '{"name": "Theater On (Updated)", "steps": [...]}'
```

#### DELETE /api/cec/macro/{id}
Delete a CEC macro.

```bash
curl -X DELETE http://localhost:8080/api/cec/macro/theater-on
```

#### POST /api/cec/macro/{id}/execute
Execute a CEC macro on the live matrix.

Uses the macro's saved `continue_on_error` policy. When true, later steps run
after a refusal, but the overall result still reports failure. An optional
JSON body can set `timeout_s`; when omitted the limit is 300 seconds.

```bash
curl -X POST http://localhost:8080/api/cec/macro/theater-on/execute
```

Response:
```json
{
  "success": true,
  "data": {
    "macro_id": "theater-on",
    "total_steps": 3,
    "successful_steps": 3,
    "failed_steps": 0,
    "duration_ms": 4523,
    "step_results": [
      {"step": 0, "command": "POWER_ON", "targets": ["output_1", "output_2"], "success": true},
      {"step": 1, "command": "POWER_ON", "targets": ["input_2"], "success": true, "delay_ms": 3000},
      {"step": 2, "command": "ACTIVE", "targets": ["input_2"], "success": true, "delay_ms": 1000}
    ]
  }
}
```

#### POST /api/cec/macro/{id}/test
Test a macro (dry run, no actual CEC commands sent).

```bash
curl -X POST http://localhost:8080/api/cec/macro/theater-on/test
```

Response:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "step_count": 3,
    "estimated_duration_ms": 4000,
    "warnings": []
  }
}
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
| `API_PORT` | `8080` | Port for the REST API, web UI and kiosk (`REST_API_PORT` and `OREI_API_PORT` are deprecated aliases) |

The REST API is the core of the hub and always runs (`REST_API_ENABLED=false` is
ignored). For the complete environment variable reference (canonical core variables, integration variables, deprecated aliases, retired flags, and transport/security tuning knobs), see [CONFIGURATION.md](CONFIGURATION.md) and [DOCKER.md](DOCKER.md#environment-variables).

---

## Backend Settings (v2.10.0+)

Backend configuration endpoints for matrix connection and system settings.

#### POST /api/settings/test-connection
Test the connection to the currently configured matrix device.

```bash
curl -X POST http://localhost:8080/api/settings/test-connection
```

**Response (success):**
```json
{
  "success": true,
  "data": {
    "connected": true,
    "host": "192.168.0.100",
    "port": 443,
    "model": "BK-808",
    "firmware_version": "1.0.5"
  }
}
```

**Response (failure - HTTP 503):**
```json
{
  "success": false,
  "data": {
    "connected": false,
    "host": "192.168.0.100",
    "port": 443,
    "error": "Connection failed"
  }
}
```

Returns `200` with `success: true` on successful connection, or `503` with `success: false` on failure.

---

## Device Settings (v2.10.0+) ⭐

Persistent per-device customizations (names, icons, colors) that survive across sessions and integrate with the UI.

#### GET /api/device-settings
Get all device settings.

```bash
curl http://localhost:8080/api/device-settings
```

#### POST /api/device-settings
Update all device settings.

The response lists persisted ports in `updated_inputs` and `updated_outputs`
and rejected entries in `errors`. Invalid entries do not prevent valid entries
from being saved. A storage failure returns HTTP 500 with `success: false`;
earlier saved entries remain applied and failed entries retain their previous
values. Individual input/output settings and preset names also retain their
previous values when saving fails.

```bash
curl -X POST http://localhost:8080/api/device-settings \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {"1": {"name": "PS5", "icon": "playstation"}, "2": {"name": "AppleTV"}},
    "outputs": {"1": {"name": "Living Room TV", "icon": "tv"}}
  }'
```

#### GET /api/device-settings/input/{input}
Get settings for a specific input.

```bash
curl http://localhost:8080/api/device-settings/input/1
```

#### POST /api/device-settings/input/{input}
Update settings for a specific input.

```bash
curl -X POST http://localhost:8080/api/device-settings/input/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "PS5", "icon": "playstation", "color": "#0066cc"}'
```

#### GET /api/device-settings/output/{output}
Get settings for a specific output.

```bash
curl http://localhost:8080/api/device-settings/output/1
```

#### POST /api/device-settings/output/{output}
Update settings for a specific output.

```bash
curl -X POST http://localhost:8080/api/device-settings/output/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Living Room TV", "icon": "tv", "color": "#cc0066"}'
```

---

## Themes (v2.10.0+) ⭐

UI theme preferences (color palette, glow intensity, etc.) that sync across devices.

#### GET /api/themes
Get current theme settings.

```bash
curl http://localhost:8080/api/themes
```

Response:
```json
{
  "success": true,
  "data": {
    "preset": "tron",
    "primary_color": "#00ffff",
    "secondary_color": "#ff00ff",
    "card_opacity": 0.8,
    "hover_effect": "primary"
  }
}
```

#### PUT /api/themes
Update theme settings.

```bash
curl -X PUT http://localhost:8080/api/themes \
  -H "Content-Type: application/json" \
  -d '{
    "preset": "neon",
    "primary_color": "#ff00ff",
    "secondary_color": "#00ff00",
    "card_opacity": 0.9
  }'
```

#### POST /api/themes/reset
Reset themes to default values.

```bash
curl -X POST http://localhost:8080/api/themes/reset
```

---

## UI Preferences (v2.10.0+) ⭐

User UI customization preferences (tab pinning, tab order) that persist per user.

#### GET /api/ui/preferences
Get current UI preferences.

```bash
curl http://localhost:8080/api/ui/preferences
```

Response:
```json
{
  "success": true,
  "data": {
    "pinnedTabs": ["matrix", "dashboard", "inputs", "outputs", "profiles"],
    "tabOrder": ["matrix", "dashboard", "inputs", "outputs", "profiles"]
  }
}
```

#### PUT /api/ui/preferences
Update UI preferences.

```bash
curl -X PUT http://localhost:8080/api/ui/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "pinnedTabs": ["matrix", "dashboard", "outputs"],
    "tabOrder": ["matrix", "dashboard", "outputs", "inputs", "profiles"]
  }'
```

---

## CEC Capabilities (v2.10.0+) ⭐

Query CEC capabilities for inputs and outputs.

#### GET /api/cec/capabilities
Get global CEC capabilities.

```bash
curl http://localhost:8080/api/cec/capabilities
```

#### GET /api/cec/input/{input}/capabilities
Get CEC capabilities for a specific input.

```bash
curl http://localhost:8080/api/cec/input/1/capabilities
```

#### GET /api/cec/output/{output}/capabilities
Get CEC capabilities for a specific output.

```bash
curl http://localhost:8080/api/cec/output/1/capabilities
```

---

## Scene Profile Reordering (v2.10.0+) ⭐

#### POST /api/profiles/reorder
Reorder profiles for display in the UI.

```bash
curl -X POST http://localhost:8080/api/profiles/reorder \
  -H "Content-Type: application/json" \
  -d '{"order": ["movie-night", "gaming", "work-from-home"]}'
```

---

## Scene CEC Auto-Resolve (v2.10.0+) ⭐

#### POST /api/scene/{scene_id}/cec/auto-resolve
Automatically resolve CEC targets for a scene based on its routing and output configuration.

```bash
curl -X POST http://localhost:8080/api/scene/movie-night/cec/auto-resolve
```

This analyzes the scene's routing and suggests CEC targets:
- Audio-only outputs (scaler mode 4) → volume targets
- ARC-enabled outputs → audio return channel targets
- Standard outputs → first available fallback

Response:
```json
{
  "success": true,
  "data": {
    "scene_id": "movie-night",
    "resolved_targets": {
      "volume": ["output_1"],
      "power": ["output_1", "input_2"],
      "navigation": ["input_2"]
    }
  }
}
```

---

## WebSocket Protocol 1 Reference (`/ws`)

The hub streams live matrix state and action notifications over `GET /ws` (Protocol `1`). Full prose contract: [`docs/api/WEBSOCKET.md`](api/WEBSOCKET.md); JSON Schema: [`docs/api/websocket.schema.json`](api/websocket.schema.json).

### Client -> Server Commands

| Command (`command` or `type`) | Payload | Response Event | Description |
|-------------------------------|---------|----------------|-------------|
| `ping` | `{"command": "ping"}` | `pong` | Heartbeat check; server answers `{"event": "pong", "data": {}}`. |
| `get_status` | `{"command": "get_status"}` | `status` or `matrix_connection` | Request an immediate full status snapshot (or link state when matrix is offline). |

### Server -> Client Events (21 Schema Events)

| Event (`event`) | Required `data` Fields | Description |
|-----------------|------------------------|-------------|
| `connected` | `message`, `client_count`, `protocol`, `matrix` | Sent immediately on WebSocket connection with client count, protocol version (1), and matrix link summary. |
| `status` | `connected`, `state`, `host`, `routing`, `input_names`, `output_names`, `inputs`, `outputs_detail` | Full matrix status snapshot (routing, input/output names, signal/connection state, power, HDCP/HDR/scaler/ARC). |
| `matrix_connection` | `connected`, `state`, `host` | Matrix link state transition (`connected`, `degraded`, `connecting`, `backoff`, `disconnected`, `not_configured`). |
| `routing_change` | `output`, `input`, `input_name`, `previous_input` | An output changed its routed input (`output`, `input`, `input_name`, `previous_input`). |
| `power_change` | `power` | Matrix power state changed (`on` or `off`). |
| `signal_change` | `input`, `has_signal`, `input_name` | Input active video signal detection changed (`input`, `has_signal`, `input_name`). |
| `connection_change` | `output`, `connected`, `output_name` | Output sink/HPD connection detection changed (`output`, `connected`, `output_name`). |
| `cable_change` | `type`, `port`, `connected`, `name` | Telnet physical cable state changed on an input or output (`type`, `port`, `connected`, `name`). |
| `audio_mute` | `output`, `muted` | Output audio mute state changed (`output`, `muted`). |
| `input_name_change` | `input`, `name` | Input port display name changed (`input`, `name`). |
| `output_name_change` | `output`, `name` | Output port display name changed (`output`, `name`). |
| `preset_recall` | `preset` | Hardware preset 1-8 recalled (`preset`). |
| `preset_recall_failed` | `preset` | Hardware preset 1-8 recall failed (`preset`). |
| `switch_failed` | `input`, `output` | Single output switch failed on the matrix (`input`, `output`). |
| `switch_all_failed` | `input` | Route-to-all switch failed on the matrix (`input`). |
| `cec_command` | `type`, `port`, `command` | CEC power command sent to an input or output port (`type`, `port`, `command`). |
| `device_settings` | `type`, `number` | Single input/output/preset customization updated (`type`, `number`, optional `name`, `icon`, `color`). |
| `device_settings_full` | *(none / optional)* | Bulk device settings updated (`inputs`, `outputs`, `presets`). |
| `scene_execution_error` | `scene_id`, `scene_name`, `steps_completed`, `total_steps`, `error` | Scene v2 execution encountered a step failure (`scene_id`, `scene_name`, `steps_completed`, `total_steps`, `error`). |
| `pong` | *(none / optional)* | Reply to client `ping` command. |
| `error` | `message` | Client command error (`message`). |

---

## Complete OpenAPI 3.1 Route Catalog

Every route registered by `src/rest_api/app.py::create_rest_app()` and emitted by `src/hub/openapi.py::build_openapi_spec()` (`GET /api/openapi.json`):

| Method & Path | Tag | Access Level | Operation ID | Summary |
|---------------|-----|--------------|--------------|---------|
| `DELETE /api/auth/api-keys/{key_id}` | `auth` | `admin` | `delete_api_auth_api_keys_key_id` | auth api keys |
| `DELETE /api/auth/devices/{device_id}` | `auth` | `admin` | `delete_api_auth_devices_device_id` | auth devices |
| `DELETE /api/cec/macro/{macro_id}` | `cec` | `admin` | `delete_api_cec_macro_macro_id` | Delete a CEC macro. |
| `DELETE /api/dashboard/cards` | `dashboard` | `admin` | `delete_api_dashboard_cards` | DELETE /api/dashboard/cards?type=profile&id=movie_night — remove a card. |
| `DELETE /api/profile/{profile_id}` | `profiles` | `admin` | `delete_api_profile_profile_id` | Delete a profile. |
| `DELETE /api/scene/{scene_id}` | `scenes` | `admin` | `delete_api_scene_scene_id` | handle delete profile *(legacy alias for `/api/profile*`)* |
| `DELETE /api/shortcuts/{key}` | `shortcuts` | `admin` | `delete_api_shortcuts_key` | DELETE /api/shortcuts/{key} — delete a user-defined shortcut. |
| `DELETE /api/system-shortcuts/{key}` | `system-shortcuts` | `admin` | `delete_api_system_shortcuts_key` | DELETE /api/shortcuts/{key} — delete a user-defined shortcut. |
| `DELETE /api/v2/scenes/{scene_id}` | `v2` | `admin` | `delete_api_v2_scenes_scene_id` | DELETE /api/v2/scenes/{scene_id} — delete a scene. |
| `DELETE /api/v2/scenes/{scene_id}/override` | `v2` | `admin` | `delete_api_v2_scenes_scene_id_override` | DELETE /api/v2/scenes/{scene_id}/override — remove an override. |
| `DELETE /api/v2/scenes/{scene_id}/steps/{index}` | `v2` | `admin` | `delete_api_v2_scenes_scene_id_steps_index` | DELETE /api/v2/scenes/{scene_id}/steps/{index} — remove step at index. |
| `GET /` | `root` | `public` | `get_root` | API documentation/index endpoint. |
| `GET /api` | `root` | `public` | `get_api` | API documentation/index endpoint. |
| `GET /api/auth/api-keys` | `auth` | `admin` | `get_api_auth_api_keys` | auth api keys |
| `GET /api/auth/devices` | `auth` | `admin` | `get_api_auth_devices` | auth devices |
| `GET /api/auth/status` | `auth` | `public` | `get_api_auth_status` | auth status |
| `GET /api/cec/capabilities` | `cec` | `public` | `get_api_cec_capabilities` | Get CEC capabilities for all input and output devices. |
| `GET /api/cec/commands` | `cec` | `public` | `get_api_cec_commands` | List available CEC commands. |
| `GET /api/cec/commands/{type}` | `cec` | `public` | `get_api_cec_commands_type` | Get supported CEC commands for a device type (input or output). |
| `GET /api/cec/input/{input}/capabilities` | `cec` | `public` | `get_api_cec_input_input_capabilities` | Get CEC capabilities for a specific input device. |
| `GET /api/cec/macro/{macro_id}` | `cec` | `public` | `get_api_cec_macro_macro_id` | Get details of a specific macro. |
| `GET /api/cec/macros` | `cec` | `public` | `get_api_cec_macros` | List all saved CEC macros. |
| `GET /api/cec/macros/favorites` | `cec` | `public` | `get_api_cec_macros_favorites` | GET /api/cec/macros/favorites — list macros marked as favorites. |
| `GET /api/cec/output/{output}/capabilities` | `cec` | `public` | `get_api_cec_output_output_capabilities` | Get CEC capabilities for a specific output device. |
| `GET /api/dashboard/layout` | `dashboard` | `public` | `get_api_dashboard_layout` | GET /api/dashboard/layout — return the current full layout. |
| `GET /api/device-settings` | `device-settings` | `public` | `get_api_device_settings` | GET /api/device-settings - Get all device settings. |
| `GET /api/device-settings/dashboard-presets` | `device-settings` | `public` | `get_api_device_settings_dashboard_presets` | GET /api/device-settings/dashboard-presets — list dashboard-pinned preset numbers. |
| `GET /api/device-settings/favorite-presets` | `device-settings` | `public` | `get_api_device_settings_favorite_presets` | GET /api/device-settings/favorite-presets — list favorite preset numbers. |
| `GET /api/device-settings/input/{input}` | `device-settings` | `public` | `get_api_device_settings_input_input` | GET /api/device-settings/input/{input} - Get settings for a specific input. |
| `GET /api/device-settings/output/{output}` | `device-settings` | `public` | `get_api_device_settings_output_output` | GET /api/device-settings/output/{output} - Get settings for a specific output. |
| `GET /api/docs` | `docs` | `public` | `get_api_docs` | Serve the interactive Swagger UI documentation page (DOC-03, TD-09). |
| `GET /api/edid/modes` | `status` | `public` | `get_api_edid_modes` | Get available EDID modes. |
| `GET /api/ext-audio/modes` | `audio` | `public` | `get_api_ext_audio_modes` | Get available ext-audio modes. |
| `GET /api/health` | `health` | `public` | `get_api_health` | Health check endpoint. |
| `GET /api/info` | `info` | `public` | `get_api_info` | Get API and matrix info for the Web UI. |
| `GET /api/inputs` | `matrix` | `public` | `get_api_inputs` | Get all inputs with their names. |
| `GET /api/integrations/flic/buttons` | `integrations` | `public` | `get_api_integrations_flic_buttons` | Retrieve all registered Flic buttons. |
| `GET /api/openapi.json` | `docs` | `public` | `get_api_openapi_json` | Serve the live OpenAPI 3.1.0 specification as JSON (DOC-03, TD-09). |
| `GET /api/outputs` | `matrix` | `public` | `get_api_outputs` | Get all outputs with their names. |
| `GET /api/presets` | `matrix` | `public` | `get_api_presets` | Get all presets with their names and routing configurations. |
| `GET /api/profile/{profile_id}` | `profiles` | `public` | `get_api_profile_profile_id` | Get details of a specific profile. |
| `GET /api/profile/{profile_id}/cec` | `profiles` | `public` | `get_api_profile_profile_id_cec` | Get or update CEC configuration for a profile. |
| `GET /api/profile/{profile_id}/execution-log` | `profiles` | `public` | `get_api_profile_profile_id_execution_log` | GET /api/profile/{profile_id}/execution-log — return last 7 days of executions. |
| `GET /api/profile/{profile_id}/macros` | `profiles` | `public` | `get_api_profile_profile_id_macros` | Get or update the macros assigned to a profile. |
| `GET /api/profiles` | `profiles` | `public` | `get_api_profiles` | List all saved profiles. |
| `GET /api/profiles/favorites` | `profiles` | `public` | `get_api_profiles_favorites` | GET /api/profiles/favorites — list profiles marked as favorites. |
| `GET /api/scene/{scene_id}` | `scenes` | `public` | `get_api_scene_scene_id` | handle get profile *(legacy alias for `/api/profile*`)* |
| `GET /api/scene/{scene_id}/cec` | `scenes` | `public` | `get_api_scene_scene_id_cec` | Alias for ``handle_profile_cec_config`` that normalizes the URL key. *(legacy alias for `/api/profile*`)* |
| `GET /api/scenes` | `scenes` | `public` | `get_api_scenes` | Alias for ``handle_list_profiles`` that renames ``profiles`` → ``scenes``. *(legacy alias for `/api/profile*`)* |
| `GET /api/settings` | `settings` | `public` | `get_api_settings` | Get current backend settings. |
| `GET /api/shortcuts` | `shortcuts` | `public` | `get_api_shortcuts` | GET /api/shortcuts — list all shortcuts (with custom name/icon/order/flags). |
| `GET /api/shortcuts/dashboard` | `shortcuts` | `public` | `get_api_shortcuts_dashboard` | GET /api/shortcuts/dashboard — list dashboard-visible shortcuts only. |
| `GET /api/shortcuts/favorites` | `shortcuts` | `public` | `get_api_shortcuts_favorites` | GET /api/shortcuts/favorites — list favorite shortcuts only. |
| `GET /api/shortcuts/{key}` | `shortcuts` | `public` | `get_api_shortcuts_key` | GET /api/shortcuts/{key} — get a single shortcut. |
| `GET /api/status` | `status` | `public` | `get_api_status` | Matrix status for the web UI and Home Assistant (docs/api/WEBSOCKET.md, "Status"). |
| `GET /api/status/cables` | `status` | `public` | `get_api_status_cables` | Get cable connection status for all inputs and outputs via Telnet. |
| `GET /api/status/cec` | `status` | `public` | `get_api_status_cec` | Get CEC configuration status. |
| `GET /api/status/device` | `status` | `public` | `get_api_status_device` | Get device/firmware information. |
| `GET /api/status/edid` | `status` | `public` | `get_api_status_edid` | Get EDID configuration status for all inputs. |
| `GET /api/status/ext-audio` | `status` | `public` | `get_api_status_ext_audio` | Get external audio matrix status. |
| `GET /api/status/full` | `status` | `public` | `get_api_status_full` | Get comprehensive matrix status from all status endpoints. |
| `GET /api/status/inputs` | `status` | `public` | `get_api_status_inputs` | Get detailed input status including signal and cable detection. |
| `GET /api/status/outputs` | `status` | `public` | `get_api_status_outputs` | Get detailed output/display status including connection detection. |
| `GET /api/status/system` | `status` | `public` | `get_api_status_system` | Get system settings status. |
| `GET /api/system-shortcuts` | `system-shortcuts` | `public` | `get_api_system_shortcuts` | GET /api/shortcuts — list all shortcuts (with custom name/icon/order/flags). |
| `GET /api/system-shortcuts/dashboard` | `system-shortcuts` | `public` | `get_api_system_shortcuts_dashboard` | GET /api/shortcuts/dashboard — list dashboard-visible shortcuts only. |
| `GET /api/system-shortcuts/favorites` | `system-shortcuts` | `public` | `get_api_system_shortcuts_favorites` | GET /api/shortcuts/favorites — list favorite shortcuts only. |
| `GET /api/system-shortcuts/{key}` | `system-shortcuts` | `public` | `get_api_system_shortcuts_key` | GET /api/shortcuts/{key} — get a single shortcut. |
| `GET /api/system/info` | `system` | `public` | `get_api_system_info` | GET /api/system/info - Return basic runtime system information. |
| `GET /api/system/lcd/modes` | `system` | `public` | `get_api_system_lcd_modes` | Get available LCD timeout modes. |
| `GET /api/system/storage` | `system` | `public` | `get_api_system_storage` | GET /api/system/storage - Report whether persistent storage is set up and usable. |
| `GET /api/themes` | `settings` | `public` | `get_api_themes` | Get current theme settings. |
| `GET /api/ui/preferences` | `settings` | `public` | `get_api_ui_preferences` | Get current UI preferences (pinned tabs and sorting order). |
| `GET /api/v2/scenes` | `v2` | `public` | `get_api_v2_scenes` | GET /api/v2/scenes — list all scenes. |
| `GET /api/v2/scenes/{scene_id}` | `v2` | `public` | `get_api_v2_scenes_scene_id` | GET /api/v2/scenes/{scene_id} — get a scene by ID. |
| `GET /api/v2/scenes/{scene_id}/history` | `v2` | `public` | `get_api_v2_scenes_scene_id_history` | GET /api/v2/scenes/{scene_id}/history — get execution history. |
| `GET /assets/{path}` | `static` | `public` | `get_assets_path` | Serve static files (CSS, JS, assets). |
| `GET /css/{path}` | `static` | `public` | `get_css_path` | Serve static files (CSS, JS, assets). |
| `GET /js/{path}` | `static` | `public` | `get_js_path` | Serve static files (CSS, JS, assets). |
| `GET /kiosk` | `web-ui` | `public` | `get_kiosk` | Serve the Kiosk Mode page for simple input switching on tablets. |
| `GET /kiosk/` | `web-ui` | `public` | `get_kiosk_index` | Serve the Kiosk Mode page for simple input switching on tablets. |
| `GET /manifest.json` | `web-ui` | `public` | `get_manifest_json` | Serve static files (CSS, JS, assets). |
| `GET /ui` | `web-ui` | `public` | `get_ui` | Serve the main Web UI page. |
| `GET /ui/` | `web-ui` | `public` | `get_ui_index` | Serve the main Web UI page. |
| `GET /ws` | `websocket` | `public` | `get_ws` | WebSocket endpoint for live updates (docs/api/WEBSOCKET.md). |
| `POST /api/auth/api-keys` | `auth` | `admin` | `post_api_auth_api_keys` | auth api keys |
| `POST /api/auth/lock` | `auth` | `public` | `post_api_auth_lock` | auth lock |
| `POST /api/auth/login` | `auth` | `public` | `post_api_auth_login` | auth unlock |
| `POST /api/auth/pin` | `auth` | `public` | `post_api_auth_pin` | auth pin |
| `POST /api/auth/unlock` | `auth` | `public` | `post_api_auth_unlock` | auth unlock |
| `POST /api/cec/input/{input}/{command}` | `cec` | `control` | `post_api_cec_input_input_command` | Send CEC command to an input device. |
| `POST /api/cec/input/{port}/enable` | `cec` | `control` | `post_api_cec_input_port_enable` | Enable or disable CEC for an input port. |
| `POST /api/cec/macro` | `cec` | `admin` | `post_api_cec_macro` | Create a new CEC macro. |
| `POST /api/cec/macro/{macro_id}/dashboard` | `cec` | `admin` | `post_api_cec_macro_macro_id_dashboard` | POST /api/cec/macro/{id}/dashboard — toggle dashboard-visible flag. |
| `POST /api/cec/macro/{macro_id}/execute` | `cec` | `control` | `post_api_cec_macro_macro_id_execute` | Execute a CEC macro. |
| `POST /api/cec/macro/{macro_id}/favorite` | `cec` | `admin` | `post_api_cec_macro_macro_id_favorite` | POST /api/cec/macro/{id}/favorite — toggle favorite flag. |
| `POST /api/cec/macro/{macro_id}/test` | `cec` | `control` | `post_api_cec_macro_macro_id_test` | Test/validate a CEC macro without executing (dry run). |
| `POST /api/cec/output/{output}/{command}` | `cec` | `control` | `post_api_cec_output_output_command` | Send CEC command to an output device (TV). |
| `POST /api/cec/output/{port}/enable` | `cec` | `control` | `post_api_cec_output_port_enable` | Enable or disable CEC for an output port. |
| `POST /api/dashboard/cards` | `dashboard` | `admin` | `post_api_dashboard_cards` | POST /api/dashboard/cards — add a single card. |
| `POST /api/dashboard/layout` | `dashboard` | `admin` | `post_api_dashboard_layout` | PUT /api/dashboard/layout — replace the full layout atomically. |
| `POST /api/device-settings` | `device-settings` | `admin` | `post_api_device_settings` | POST /api/device-settings - Bulk update device settings. |
| `POST /api/device-settings/dashboard-presets/{preset}/toggle` | `device-settings` | `admin` | `post_api_device_settings_dashboard_presets_preset_toggle` | POST /api/device-settings/dashboard-presets/{preset}/toggle — toggle one preset. |
| `POST /api/device-settings/favorite-presets/{preset}/toggle` | `device-settings` | `admin` | `post_api_device_settings_favorite_presets_preset_toggle` | POST /api/device-settings/favorite-presets/{preset}/toggle — toggle one preset. |
| `POST /api/device-settings/input/{input}` | `device-settings` | `admin` | `post_api_device_settings_input_input` | POST /api/device-settings/input/{input} - Update settings for a specific input. |
| `POST /api/device-settings/output/{output}` | `device-settings` | `admin` | `post_api_device_settings_output_output` | POST /api/device-settings/output/{output} - Update settings for a specific output. |
| `POST /api/device-settings/preset/{preset}/name` | `device-settings` | `admin` | `post_api_device_settings_preset_preset_name` | POST /api/device-settings/preset/{preset}/name - Rename a preset. |
| `POST /api/ext-audio/mode` | `audio` | `control` | `post_api_ext_audio_mode` | Set external audio routing mode. |
| `POST /api/ext-audio/{output}/enable` | `audio` | `control` | `post_api_ext_audio_output_enable` | Enable or disable ext-audio on a specific output. |
| `POST /api/ext-audio/{output}/source` | `audio` | `control` | `post_api_ext_audio_output_source` | Set audio source for a specific ext-audio output. |
| `POST /api/input/next` | `matrix` | `control` | `post_api_input_next` | Cycle to the next input on the specified output (default: output 1). |
| `POST /api/input/previous` | `matrix` | `control` | `post_api_input_previous` | Cycle to the previous input on the specified output (default: output 1). |
| `POST /api/input/{input}/edid` | `matrix` | `admin` | `post_api_input_input_edid` | Set EDID mode for a specific input. |
| `POST /api/input/{input}/name` | `matrix` | `admin` | `post_api_input_input_name` | Set the name of an input (sends to matrix and updates local cache). |
| `POST /api/integrations/flic/register` | `integrations` | `admin` | `post_api_integrations_flic_register` | Register Flic buttons reported by the Flic Hub SDK script. |
| `POST /api/output/{output}/arc` | `matrix` | `control` | `post_api_output_output_arc` | Enable or disable ARC for an output. |
| `POST /api/output/{output}/enable` | `matrix` | `control` | `post_api_output_output_enable` | Enable or disable output video stream. |
| `POST /api/output/{output}/hdcp` | `matrix` | `admin` | `post_api_output_output_hdcp` | Set HDCP mode for an output. |
| `POST /api/output/{output}/hdr` | `matrix` | `admin` | `post_api_output_output_hdr` | Set HDR mode for an output. |
| `POST /api/output/{output}/mute` | `matrix` | `control` | `post_api_output_output_mute` | Mute or unmute audio for an output. |
| `POST /api/output/{output}/name` | `matrix` | `admin` | `post_api_output_output_name` | Set the name of an output (sends to matrix and updates local cache). |
| `POST /api/output/{output}/scaler` | `matrix` | `admin` | `post_api_output_output_scaler` | Set scaler mode for an output. |
| `POST /api/output/{output}/source` | `matrix` | `control` | `post_api_output_output_source` | Set the input source for a specific output. |
| `POST /api/power/off` | `matrix` | `control` | `post_api_power_off` | Power off the matrix. |
| `POST /api/power/on` | `matrix` | `control` | `post_api_power_on` | Power on the matrix. |
| `POST /api/preset/{preset}` | `matrix` | `control` | `post_api_preset_preset` | Recall a preset. |
| `POST /api/preset/{preset}/save` | `matrix` | `admin` | `post_api_preset_preset_save` | Save current routing or a custom routing mapping to a preset. |
| `POST /api/profile` | `profiles` | `admin` | `post_api_profile` | Create or update a profile. |
| `POST /api/profile/{profile_id}/cec` | `profiles` | `admin` | `post_api_profile_profile_id_cec` | Get or update CEC configuration for a profile. |
| `POST /api/profile/{profile_id}/dashboard` | `profiles` | `admin` | `post_api_profile_profile_id_dashboard` | POST /api/profile/{id}/dashboard — toggle dashboard-visible flag. |
| `POST /api/profile/{profile_id}/favorite` | `profiles` | `admin` | `post_api_profile_profile_id_favorite` | POST /api/profile/{id}/favorite — toggle the favorite flag. |
| `POST /api/profile/{profile_id}/macros` | `profiles` | `admin` | `post_api_profile_profile_id_macros` | Get or update the macros assigned to a profile. |
| `POST /api/profile/{profile_id}/recall` | `profiles` | `control` | `post_api_profile_profile_id_recall` | Recall a profile, applying all its settings to the matrix. |
| `POST /api/profiles/reorder` | `profiles` | `admin` | `post_api_profiles_reorder` | Bulk update pin order and pinned status for profiles. |
| `POST /api/scene` | `scenes` | `admin` | `post_api_scene` | Create or update a profile. *(legacy alias for `/api/profile*`)* |
| `POST /api/scene/save-current` | `scenes` | `admin` | `post_api_scene_save_current` | POST /api/scene/save-current — capture current matrix state as a new profile. *(legacy alias for `/api/profile*`)* |
| `POST /api/scene/{scene_id}/cec` | `scenes` | `admin` | `post_api_scene_scene_id_cec` | Alias for ``handle_profile_cec_config`` that normalizes the URL key. *(legacy alias for `/api/profile*`)* |
| `POST /api/scene/{scene_id}/cec/auto-resolve` | `scenes` | `admin` | `post_api_scene_scene_id_cec_auto_resolve` | POST /api/scene/{scene_id}/cec/auto-resolve — resolve a profile's CEC targets from its routing. *(legacy alias for `/api/profile*`)* |
| `POST /api/scene/{scene_id}/recall` | `scenes` | `control` | `post_api_scene_scene_id_recall` | Alias for ``handle_recall_profile`` that normalizes the URL key and *(legacy alias for `/api/profile*`)* |
| `POST /api/settings/matrix-host` | `settings` | `admin` | `post_api_settings_matrix_host` | Set the matrix host address (reconfigures backend connection). |
| `POST /api/settings/test-connection` | `settings` | `admin` | `post_api_settings_test_connection` | Test connection to the currently configured matrix. |
| `POST /api/shortcuts` | `shortcuts` | `admin` | `post_api_shortcuts` | POST /api/shortcuts — create a user-defined shortcut. |
| `POST /api/shortcuts/{key}/dashboard` | `shortcuts` | `admin` | `post_api_shortcuts_key_dashboard` | POST /api/shortcuts/{key}/dashboard — toggle the dashboard_visible flag. |
| `POST /api/shortcuts/{key}/execute` | `shortcuts` | `control` | `post_api_shortcuts_key_execute` | POST /api/shortcuts/{key}/execute — execute the shortcut against the matrix. |
| `POST /api/shortcuts/{key}/favorite` | `shortcuts` | `admin` | `post_api_shortcuts_key_favorite` | POST /api/shortcuts/{key}/favorite — toggle the favorite flag. |
| `POST /api/switch` | `matrix` | `control` | `post_api_switch` | Route an input to an output, or to all outputs if output is not specified. |
| `POST /api/system-shortcuts` | `system-shortcuts` | `admin` | `post_api_system_shortcuts` | POST /api/shortcuts — create a user-defined shortcut. |
| `POST /api/system-shortcuts/{key}/dashboard` | `system-shortcuts` | `admin` | `post_api_system_shortcuts_key_dashboard` | POST /api/shortcuts/{key}/dashboard — toggle the dashboard_visible flag. |
| `POST /api/system-shortcuts/{key}/execute` | `system-shortcuts` | `control` | `post_api_system_shortcuts_key_execute` | POST /api/shortcuts/{key}/execute — execute the shortcut against the matrix. |
| `POST /api/system-shortcuts/{key}/favorite` | `system-shortcuts` | `admin` | `post_api_system_shortcuts_key_favorite` | POST /api/shortcuts/{key}/favorite — toggle the favorite flag. |
| `POST /api/system/beep` | `system` | `control` | `post_api_system_beep` | Enable or disable system beep. |
| `POST /api/system/lcd` | `system` | `control` | `post_api_system_lcd` | Set LCD display timeout. |
| `POST /api/system/panel_lock` | `system` | `admin` | `post_api_system_panel_lock` | Lock or unlock front panel. |
| `POST /api/system/reboot` | `system` | `admin` | `post_api_system_reboot` | Reboot the matrix. |
| `POST /api/themes/reset` | `settings` | `admin` | `post_api_themes_reset` | Reset theme settings to defaults. |
| `POST /api/v2/scenes` | `v2` | `admin` | `post_api_v2_scenes` | POST /api/v2/scenes — create a new scene. |
| `POST /api/v2/scenes/{scene_id}/execute` | `v2` | `control` | `post_api_v2_scenes_scene_id_execute` | POST /api/v2/scenes/{scene_id}/execute — execute a scene. |
| `POST /api/v2/scenes/{scene_id}/steps` | `v2` | `admin` | `post_api_v2_scenes_scene_id_steps` | POST /api/v2/scenes/{scene_id}/steps — add a step to a scene. |
| `POST /api/v2/scenes/{scene_id}/validate` | `v2` | `public` | `post_api_v2_scenes_scene_id_validate` | POST /api/v2/scenes/{scene_id}/validate — detect conflicts in scene steps. |
| `PUT /api/cec/macro/{macro_id}` | `cec` | `admin` | `put_api_cec_macro_macro_id` | Update an existing CEC macro. |
| `PUT /api/dashboard/layout` | `dashboard` | `admin` | `put_api_dashboard_layout` | PUT /api/dashboard/layout — replace the full layout atomically. |
| `PUT /api/device-settings/dashboard-presets` | `device-settings` | `admin` | `put_api_device_settings_dashboard_presets` | PUT /api/device-settings/dashboard-presets — replace the full dashboard list. |
| `PUT /api/device-settings/favorite-presets` | `device-settings` | `admin` | `put_api_device_settings_favorite_presets` | PUT /api/device-settings/favorite-presets — replace the full favorites list. |
| `PUT /api/profile/{profile_id}` | `profiles` | `admin` | `put_api_profile_profile_id` | Update an existing profile's properties. |
| `PUT /api/profile/{profile_id}/cec` | `profiles` | `admin` | `put_api_profile_profile_id_cec` | Get or update CEC configuration for a profile. |
| `PUT /api/profile/{profile_id}/dashboard` | `profiles` | `admin` | `put_api_profile_profile_id_dashboard` | PUT /api/profile/{id}/dashboard — explicitly set dashboard-visible flag. |
| `PUT /api/profile/{profile_id}/favorite` | `profiles` | `admin` | `put_api_profile_profile_id_favorite` | PUT /api/profile/{id}/favorite — explicitly set favorite flag. |
| `PUT /api/profile/{profile_id}/macros` | `profiles` | `admin` | `put_api_profile_profile_id_macros` | Get or update the macros assigned to a profile. |
| `PUT /api/scene/{scene_id}/cec` | `scenes` | `admin` | `put_api_scene_scene_id_cec` | Alias for ``handle_profile_cec_config`` that normalizes the URL key. *(legacy alias for `/api/profile*`)* |
| `PUT /api/shortcuts/reorder` | `shortcuts` | `admin` | `put_api_shortcuts_reorder` | PUT /api/shortcuts/reorder — bulk reorder shortcuts by key list. |
| `PUT /api/shortcuts/{key}` | `shortcuts` | `admin` | `put_api_shortcuts_key` | PUT /api/shortcuts/{key} — update label, icon, enabled, order, favorite, and dashboard flags. |
| `PUT /api/system-shortcuts/reorder` | `system-shortcuts` | `admin` | `put_api_system_shortcuts_reorder` | PUT /api/shortcuts/reorder — bulk reorder shortcuts by key list. |
| `PUT /api/system-shortcuts/{key}` | `system-shortcuts` | `admin` | `put_api_system_shortcuts_key` | PUT /api/shortcuts/{key} — update label, icon, enabled, order, favorite, and dashboard flags. |
| `PUT /api/themes` | `settings` | `admin` | `put_api_themes` | Update theme settings. |
| `PUT /api/ui/preferences` | `settings` | `admin` | `put_api_ui_preferences` | Update UI preferences persistently. |
| `PUT /api/v2/scenes/{scene_id}` | `v2` | `admin` | `put_api_v2_scenes_scene_id` | PUT /api/v2/scenes/{scene_id} — update a scene. |
| `PUT /api/v2/scenes/{scene_id}/override` | `v2` | `admin` | `put_api_v2_scenes_scene_id_override` | PUT /api/v2/scenes/{scene_id}/override — set a per-profile output override. |
