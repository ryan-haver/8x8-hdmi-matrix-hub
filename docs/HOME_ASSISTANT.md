# Home Assistant Integration Guide

> **Status**: Hub REST API current (`v0.4.0`) | HACS component `hdmi_matrix` (Home Assistant 2025.1+)
>
> Sources of truth: `src/rest_api/app.py` (every route) and
> `src/rest_api/security.py` (access model). This guide covers the two ways
> to expose the hub to Home Assistant: **Option A** — built-in `rest_command`
> and `rest` sensor with the plain HTTP API — and **Option B** — the proper
> HACS custom component under `custom_components/hdmi_matrix/`.

## Integration Options

### Option A: REST Commands / sensor (no install required)

Use Home Assistant's built-in `rest_command` and `rest` integrations against
the hub's plain HTTP API.

**Pros**: no custom code, works immediately, full API access
**Cons**: manual configuration, no automatic entity discovery

### Option B: HACS custom component (recommended)

A proper Home Assistant integration: a device in the device registry, entities,
services, polling, options flow and device tracking.

**Pros**: full functionality, proper UI, automations, device tracking
**Cons**: installed through HACS (custom repository)

The hub's `manifest.json` field `iot_class` is `local_polling`; the integration
is a local hub that polls the device. There is no cloud dependency.

---

## Option A: REST Commands

### Prerequisites

- OREI Matrix hub running (Docker or `python run.py`).
- REST API reachable on port 8080 (the hub default `API_PORT`).
- Home Assistant installed (any current release; the `rest` integration has
  been part of HA for years).

### Available endpoints

The route table mirrors `src/rest_api/app.py`. The hub answers every URL
below by default; on a locked hub the *control* group requires an API key
(`X-API-Key` header or `?key=` query) and the *admin* group requires an
admin session (see "API key / control PIN" below).

#### Reads

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/status` | GET | Matrix status, power state, all inputs/outputs/presets |
| `/api/info` | GET | Hub info, version, capabilities |
| `/api/health` | GET | Health check (used by Docker `HEALTHCHECK`) |
| `/api/inputs` | GET | Input names |
| `/api/outputs` | GET | Output names |
| `/api/presets` | GET | Preset names |
| `/api/edid/modes` | GET | Available EDID modes |
| `/api/system/lcd/modes` | GET | Available LCD timeout modes |
| `/api/system/storage` | GET | Path-free storage diagnostics: source, existence, writability and file count |
| `/api/system/info` | GET | Python/platform/API versions and storage diagnostics |
| `/api/ext-audio/modes` | GET | External audio binding modes |
| `/api/cec/commands` | GET | CEC command list |
| `/api/cec/commands/{type}` | GET | CEC commands for `input` or `output` |
| `/api/cec/capabilities` | GET | CEC capabilities summary |
| `/api/cec/input/{n}/capabilities` | GET | Capabilities for input N |
| `/api/cec/output/{n}/capabilities` | GET | Capabilities for output N |

#### Routing & control (control-level on a locked hub)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/switch` | POST | Body `{"input": 2, "output": 1}` routes one output; omit `output` to route all outputs |
| `/api/input/next?output=N` | POST | Cycle to next input on output N |
| `/api/input/previous?output=N` | POST | Cycle to previous input on output N |
| `/api/output/{n}/source` | POST | Set output N to a specific input (`{"input": N}`) |
| `/api/output/{n}/enable` | POST | Enable/disable the output stream (`{"enabled": bool}`) |
| `/api/output/{n}/arc` | POST | Enable/disable ARC (`{"enabled": bool}`) |
| `/api/output/{n}/mute` | POST | Mute/unmute audio (`{"muted": bool}`) |
| `/api/preset/{n}` | POST | Recall preset N (1-8) |
| `/api/power/on` | POST | Power on matrix |
| `/api/power/off` | POST | Power off matrix |
| `/api/system/beep` | POST | Beep the matrix buzzer |
| `/api/system/lcd` | POST | Set LCD timeout mode (`{"mode": 0-4}`) |
| `/api/cec/input/{n}/enable` | POST | Enable/disable CEC on input N |
| `/api/cec/output/{n}/enable` | POST | Enable/disable CEC on output N |
| `/api/cec/input/{n}/{command}` | POST | CEC command on input N (e.g. `play`, `pause`, `power_on`) |
| `/api/cec/output/{n}/{command}` | POST | CEC command on output N (e.g. `volume_up`, `mute`, `power_on`) |
| `/api/profile/{id}/recall` | POST | Activate a saved profile |
| `/api/scene/{id}/recall` | POST | Apply a saved scene |
| `/api/cec/macro/{id}/execute` | POST | Run a CEC macro |
| `/api/cec/macro/{id}/test` | POST | Test (dry-run) a CEC macro |
| `/api/ext-audio/{n}/enable` | POST | Enable/disable ext-audio for output N |
| `/api/ext-audio/{n}/source` | POST | Bind ext-audio input for output N |
| `/api/ext-audio/mode` | POST | Set binding mode (`{"mode": 0-2}`) |
| `/api/integrations/flic/buttons` | GET | List registered Flic buttons |
| `/api/integrations/flic/register` | POST | Register Flic buttons from a Flic Hub (admin) |

#### Profile / scene / macro management

The GET methods in this group are public reads; mutations require admin
access when an admin PIN is configured. Recall and execution are control-level
operations as listed above.

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/profiles` | GET | List profiles |
| `/api/profile/{id}` | GET / PUT / DELETE | Profile CRUD |
| `/api/profile` | POST | Create profile |
| `/api/profiles/reorder` | POST | Reorder profiles |
| `/api/profile/{id}/cec` | GET / POST / PUT | Profile CEC config |
| `/api/profile/{id}/macros` | GET / POST / PUT | Profile macros |
| `/api/scenes` | GET | List scenes (v1) |
| `/api/scene/{id}` | GET / DELETE | Scene detail / delete |
| `/api/scene` | POST | Create / update scene |
| `/api/scene/{id}/cec` | GET / POST / PUT | Scene CEC config |
| `/api/scene/save-current` | POST | Save current state as a scene |
| `/api/v2/scenes` | GET / POST | List / create v2 scenes |
| `/api/v2/scenes/{id}` | GET / PUT / DELETE | v2 scene CRUD |
| `/api/v2/scenes/{id}/execute` | POST | Run a v2 scene |
| `/api/cec/macros` | GET | List CEC macros |
| `/api/cec/macro` | POST | Create CEC macro |
| `/api/cec/macro/{id}` | GET / PUT / DELETE | Manage macro |

#### Settings and authentication

Settings reads are public. Settings mutations and authentication-management
reads (`/api/auth/devices`, `/api/auth/api-keys`) require admin access when a
PIN is configured. Unlock/status/lock are public authentication endpoints;
PIN changes apply their own current-admin verification.

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/auth/status` | GET | `{admin_pin_set, control_pin_set, session_level, device_remembered}` |
| `/api/auth/unlock` | POST | `{"level": "admin"\|"control", "pin": "..."}` — opens a session |
| `/api/auth/login` | POST | Alias for `/api/auth/unlock` |
| `/api/auth/lock` | POST | Ends the current session |
| `/api/auth/pin` | POST | Set / change / clear an admin or control PIN (admin session required to touch admin) |
| `/api/auth/devices` | GET | List "remembered device" tokens |
| `/api/auth/devices/{id}` | DELETE | Forget a device |
| `/api/auth/api-keys` | GET / POST | List / create named API keys (admin) |
| `/api/auth/api-keys/{id}` | DELETE | Revoke an API key |
| `/api/settings` | GET | Hub settings |
| `/api/settings/matrix-host` | POST | Update the matrix address (admin) |
| `/api/settings/test-connection` | POST | Probe an address (admin) |
| `/api/themes` | GET / PUT | Theme tokens |
| `/api/themes/reset` | POST | Reset themes to defaults |
| `/api/ui/preferences` | GET / PUT | UI preferences |
| `/api/dashboard/layout` | GET / POST / PUT | Replace the dashboard layout |
| `/api/dashboard/cards` | POST / DELETE | Add / remove a card |
| `/api/device-settings` | GET / POST | Bulk update device settings |
| `/api/device-settings/input/{n}` | GET / POST | Input settings |
| `/api/device-settings/output/{n}` | GET / POST | Output settings |
| `/api/device-settings/preset/{n}/name` | POST | Rename preset |
| `/api/input/{n}/name` | POST | Rename input (admin) |
| `/api/input/{n}/edid` | POST | Set EDID mode (admin) |
| `/api/output/{n}/name` | POST | Rename output (admin) |
| `/api/output/{n}/hdcp` | POST | HDCP mode (admin) |
| `/api/output/{n}/hdr` | POST | HDR mode (admin) |
| `/api/output/{n}/scaler` | POST | Scaler mode (admin) |
| `/api/system/reboot` | POST | Reboot the matrix (admin) |
| `/api/system/panel_lock` | POST | Front-panel lock (admin) |

### Configuration

Add to `configuration.yaml`:

```yaml
# OREI Matrix REST Commands
rest_command:
  # Preset switching
  orei_preset_1:
    url: "http://192.168.1.145:8080/api/preset/1"
    method: POST
  orei_preset_2:
    url: "http://192.168.1.145:8080/api/preset/2"
    method: POST
  orei_preset_3:
    url: "http://192.168.1.145:8080/api/preset/3"
    method: POST
  orei_preset_4:
    url: "http://192.168.1.145:8080/api/preset/4"
    method: POST
  orei_preset_5:
    url: "http://192.168.1.145:8080/api/preset/5"
    method: POST
  orei_preset_6:
    url: "http://192.168.1.145:8080/api/preset/6"
    method: POST
  orei_preset_7:
    url: "http://192.168.1.145:8080/api/preset/7"
    method: POST
  orei_preset_8:
    url: "http://192.168.1.145:8080/api/preset/8"
    method: POST

  # Power control
  orei_power_on:
    url: "http://192.168.1.145:8080/api/power/on"
    method: POST
  orei_power_off:
    url: "http://192.168.1.145:8080/api/power/off"
    method: POST

  # Input cycling
  orei_input_next:
    url: "http://192.168.1.145:8080/api/input/next?output={{ output }}"
    method: POST
  orei_input_previous:
    url: "http://192.168.1.145:8080/api/input/previous?output={{ output }}"
    method: POST

  # Direct output control
  orei_set_output_source:
    url: "http://192.168.1.145:8080/api/output/{{ output }}/source"
    method: POST
    content_type: "application/json"
    payload: '{"input": {{ input }}}'

  # Global input switching (legacy)
  orei_switch_all_to_input:
    url: "http://192.168.1.145:8080/api/input/{{ input }}"
    method: POST

  # Advanced output control
  orei_set_hdcp:
    url: "http://192.168.1.145:8080/api/output/{{ output }}/hdcp"
    method: POST
    content_type: "application/json"
    payload: '{"mode": {{ mode }}}'  # 1=HDCP1.4, 2=HDCP2.2, 3=Follow Sink, 4=Follow Source, 5=User
  orei_set_hdr:
    url: "http://192.168.1.145:8080/api/output/{{ output }}/hdr"
    method: POST
    content_type: "application/json"
    payload: '{"mode": {{ mode }}}'  # 1=Passthrough, 2=HDR to SDR, 3=Auto
  orei_set_scaler:
    url: "http://192.168.1.145:8080/api/output/{{ output }}/scaler"
    method: POST
    content_type: "application/json"
    payload: '{"mode": {{ mode }}}'  # 1=Passthrough, 2=8K→4K, 3=8K/4K→1080p, 4=Auto, 5=Audio Only
  orei_set_arc:
    url: "http://192.168.1.145:8080/api/output/{{ output }}/arc"
    method: POST
    content_type: "application/json"
    payload: '{"enabled": {{ enabled }}}'
  orei_mute_output:
    url: "http://192.168.1.145:8080/api/output/{{ output }}/mute"
    method: POST
    content_type: "application/json"
    payload: '{"muted": {{ muted }}}'
  orei_enable_output:
    url: "http://192.168.1.145:8080/api/output/{{ output }}/enable"
    method: POST
    content_type: "application/json"
    payload: '{"enabled": {{ enabled }}}'

  # Preset Management
  orei_save_preset:
    url: "http://192.168.1.145:8080/api/preset/{{ preset }}/save"
    method: POST

  # System Control
  orei_reboot:
    url: "http://192.168.1.145:8080/api/system/reboot"
    method: POST

  # EDID Control
  orei_set_edid:
    url: "http://192.168.1.145:8080/api/input/{{ input }}/edid"
    method: POST
    content_type: "application/json"
    payload: '{"mode": {{ mode }}}'

  # LCD Control
  orei_set_lcd_timeout:
    url: "http://192.168.1.145:8080/api/system/lcd"
    method: POST
    content_type: "application/json"
    payload: '{"mode": {{ mode }}}'  # 0=Off, 1=Always, 2=15s, 3=30s, 4=60s

  # External Audio Control
  orei_set_ext_audio_mode:
    url: "http://192.168.1.145:8080/api/ext-audio/mode"
    method: POST
    content_type: "application/json"
    payload: '{"mode": {{ mode }}}'  # 0=Bind Input, 1=Bind Output, 2=Matrix
  orei_set_ext_audio_enable:
    url: "http://192.168.1.145:8080/api/ext-audio/{{ output }}/enable"
    method: POST
    content_type: "application/json"
    payload: '{"enabled": {{ enabled }}}'
  orei_set_ext_audio_source:
    url: "http://192.168.1.145:8080/api/ext-audio/{{ output }}/source"
    method: POST
    content_type: "application/json"
    payload: '{"input": {{ input }}}'

  # Scene Control
  orei_recall_scene:
    url: "http://192.168.1.145:8080/api/scene/{{ scene_id }}/recall"
    method: POST
  orei_save_current_scene:
    url: "http://192.168.1.145:8080/api/scene/save-current"
    method: POST
    content_type: "application/json"
    payload: '{"id": "{{ scene_id }}", "name": "{{ scene_name }}"}'

  # Profile & Macro (control level)
  orei_recall_profile:
    url: "http://192.168.1.145:8080/api/profile/{{ profile_id }}/recall"
    method: POST
  orei_run_cec_macro:
    url: "http://192.168.1.145:8080/api/cec/macro/{{ macro_id }}/execute"
    method: POST

  # CEC commands
  orei_cec_play:
    url: "http://192.168.1.145:8080/api/cec/input/{{ input }}/play"
    method: POST
  orei_cec_pause:
    url: "http://192.168.1.145:8080/api/cec/input/{{ input }}/pause"
    method: POST
  orei_cec_power_on:
    url: "http://192.168.1.145:8080/api/cec/input/{{ input }}/power_on"
    method: POST
  orei_cec_power_off:
    url: "http://192.168.1.145:8080/api/cec/input/{{ input }}/power_off"
    method: POST
  orei_cec_volume_up:
    url: "http://192.168.1.145:8080/api/cec/output/{{ output }}/volume_up"
    method: POST
  orei_cec_volume_down:
    url: "http://192.168.1.145:8080/api/cec/output/{{ output }}/volume_down"
    method: POST
  orei_cec_mute:
    url: "http://192.168.1.145:8080/api/cec/output/{{ output }}/mute"
    method: POST
```

### API key (only needed when the hub's control lock is on)

The hub has an optional **control lock** (`CONTROL_PIN`) and an optional
**admin PIN** (`ADMIN_PIN`). With neither set, every URL above works as-is.

When the control lock is on, control-level requests (most of what Flic/HA
send) need an API key; admin requests always need an admin session when an
admin PIN is set. `X-API-Key` is the header the integration uses; `?key=…`
is the equivalent on a URL (the Flic guide uses this form).

```bash
# Create a key (admin session required; cookies carry the session)
curl -X POST http://192.168.1.145:8080/api/auth/api-keys \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name": "Home Assistant"}'
# => {"id": "6f1c…", "key": "u3k…<the key value>…"}   (201 Created)
```

```yaml
# Use it on a rest_command
rest_command:
  orei_preset_2:
    url: "http://192.168.1.145:8080/api/preset/2?key=u3k…"
    method: POST
```

```yaml
# Or in the rest sensor (header form)
sensor:
  - platform: rest
    name: OREI Matrix Status
    resource: "http://192.168.1.145:8080/api/status"
    headers:
      X-API-Key: "u3k…"
    value_template: "{{ value_json.power_state }}"
    json_attributes:
      - outputs
      - input_names
      - output_names
    scan_interval: 30
```

`src/rest_api/security.py:api_key_valid` accepts the key from `X-API-Key`
or `?key=`; the access model is documented in `SECURITY.md` §"Two-level
access model".

### REST sensor for matrix status

```yaml
sensor:
  - platform: rest
    name: OREI Matrix Status
    resource: "http://192.168.1.145:8080/api/status"
    value_template: "{{ value_json.power_state }}"
    json_attributes:
      - outputs
      - input_names
      - output_names
    scan_interval: 30

# Template sensors for individual outputs
template:
  - sensor:
      - name: "Living Room TV Input"
        state: >
          {% set outputs = state_attr('sensor.orei_matrix_status', 'outputs') %}
          {% if outputs %}
            {{ outputs[0].input_name | default('Unknown') }}
          {% else %}
            Unknown
          {% endif %}
      - name: "Bedroom TV Input"
        state: >
          {% set outputs = state_attr('sensor.orei_matrix_status', 'outputs') %}
          {% if outputs %}
            {{ outputs[1].input_name | default('Unknown') }}
          {% else %}
            Unknown
          {% endif %}
```

### Using in automations

```yaml
automation:
  - alias: "Movie Night"
    trigger:
      - platform: state
        entity_id: input_boolean.movie_mode
        to: "on"
    action:
      - service: rest_command.orei_preset_5
      - service: light.turn_off
        target:
          area_id: living_room

  - alias: "Cycle Input on Button Press"
    trigger:
      - platform: state
        entity_id: input_button.next_input
    action:
      - service: rest_command.orei_input_next
        data:
          output: 1  # Living room TV

  - alias: "Power on PS5 and Switch to It"
    trigger:
      - platform: state
        entity_id: input_boolean.ps5_mode
        to: "on"
    action:
      - service: rest_command.orei_cec_power_on
        data:
          input: 6  # PS5 input
      - delay: "00:00:03"  # Wait for device to power on
      - service: rest_command.orei_preset_6

  - alias: "Set Office to PC Input"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: workday
    action:
      - service: rest_command.orei_set_output_source
        data:
          output: 3  # Office TV
          input: 7   # PC input

  - alias: "Recall Movie Night Scene"
    trigger:
      - platform: state
        entity_id: input_boolean.movie_night
        to: "on"
    action:
      - service: rest_command.orei_recall_scene
        data:
          scene_id: "movie_night"
      - service: light.turn_off
        target:
          area_id: living_room

  - alias: "Save Current Setup"
    trigger:
      - platform: state
        entity_id: input_button.save_matrix_scene
    action:
      - service: rest_command.orei_save_current_scene
        data:
          scene_id: "quick_save"
          scene_name: "Quick Save"
```

### Using in scripts

```yaml
script:
  watch_apple_tv:
    alias: "Watch Apple TV"
    sequence:
      - service: rest_command.orei_preset_2
      - delay: "00:00:02"
      - service: rest_command.orei_cec_play
        data:
          input: 2

  gaming_session:
    alias: "Gaming Session"
    sequence:
      - service: rest_command.orei_cec_power_on
        data:
          input: 6
      - delay: "00:00:03"
      - service: rest_command.orei_set_output_source
        data:
          output: 1
          input: 6

  cycle_living_room_input:
    alias: "Cycle Living Room Input"
    sequence:
      - service: rest_command.orei_input_next
        data:
          output: 1
```

### Dashboard cards

#### Preset button row

```yaml
type: horizontal-stack
cards:
  - type: button
    name: PS3
    icon: mdi:sony-playstation
    tap_action:
      action: call-service
      service: rest_command.orei_preset_1
  - type: button
    name: AppleTV
    icon: mdi:apple
    tap_action:
      action: call-service
      service: rest_command.orei_preset_2
  - type: button
    name: Shield
    icon: mdi:nvidia
    tap_action:
      action: call-service
      service: rest_command.orei_preset_5
  - type: button
    name: PS5
    icon: mdi:sony-playstation
    tap_action:
      action: call-service
      service: rest_command.orei_preset_6
```

#### Input navigation buttons

```yaml
type: horizontal-stack
cards:
  - type: button
    name: Previous
    icon: mdi:skip-previous
    tap_action:
      action: call-service
      service: rest_command.orei_input_previous
      data:
        output: 1
  - type: button
    name: Next
    icon: mdi:skip-next
    tap_action:
      action: call-service
      service: rest_command.orei_input_next
      data:
        output: 1
```

#### Matrix status card

```yaml
type: entities
title: OREI Matrix Status
entities:
  - entity: sensor.orei_matrix_status
    name: Power State
  - entity: sensor.living_room_tv_input
    name: Living Room
  - entity: sensor.bedroom_tv_input
    name: Bedroom
```

#### Power control row

```yaml
type: horizontal-stack
cards:
  - type: button
    name: Power On
    icon: mdi:power-on
    tap_action:
      action: call-service
      service: rest_command.orei_power_on
  - type: button
    name: Power Off
    icon: mdi:power-off
    tap_action:
      action: call-service
      service: rest_command.orei_power_off
```

---

## Option B: HACS Custom Component

The `hdmi_matrix` integration in `custom_components/hdmi_matrix/` talks to the
hub's REST API (not to the matrix directly). Requires Home Assistant 2025.1 or
newer. Proof of function: `docs/validation/LEDGER.md` (area `ha`); the
integration is exercised in a real Home Assistant container by
`python -m tools.validate run --client ha`.

### Installation

1. HACS → Integrations → Custom repositories: add this repository (category *Integration*).
2. Install **HDMI Matrix** and restart Home Assistant.
3. Settings → Devices & services → Add integration → **HDMI Matrix**.
4. Enter the hub's host and port (default 8080). The matrix is identified by its
   MAC, so a later address change keeps entities and history. If the hub's control lock
   is enabled, enter an **API key** too (see [below](#api-key-required-only-when-the-hubs-control-lock-is-on)).

The integration is configured through the standard Home Assistant **config
flow** (`custom_components/hdmi_matrix/config_flow.py`): an initial *user*
form with host / port / api-key, a *reconfigure* flow for address changes,
and an *options* flow for the polling interval and the api-key.

**Reconfigure** (the entry's menu) changes the hub address; it refuses a hub that
controls a different matrix. **Options** set the polling interval (5-300 s,
default 15 s) and the same API key field.

### API key (required only when the hub's control lock is on)

The hub has an optional control lock (`CONTROL_PIN`). It is **off by default**, and
while it is off the API key field is not needed — leave it empty.

When the hub owner enables the control lock, control-level requests (polling, entities,
services) must carry an API key, or Home Assistant sees `401 Unauthorized` and the
entities go unavailable. Create one on the hub — its **Settings → Security → API keys**
page, or with `POST /api/auth/api-keys` (both step by step in
[FLIC_SETUP.md](FLIC_SETUP.md#generate-an-api-key)) — and paste it into the **API key**
field of:

| Flow | Where the field appears |
|------|-------------------------|
| Initial add | Settings → Devices & services → Add integration → **HDMI Matrix** |
| Reconfigure | The entry's menu → **Reconfigure** (changing the hub address) |
| Options | The entry's menu → **Configure** (alongside the polling interval) |

The field is optional in all three, stored as `api_key` in the config entry (options
override the entry value), and used like this:

- **Sent as a header, not a login.** Every hub request carries `X-API-Key: <key>`;
  there is no cookie, session, or re-authentication step. Nothing about the flow
  changes once it is set.
- **Used during setup too.** The config flow's connectivity check sends the key, so a
  locked hub completes setup instead of failing with *cannot_connect*.
- **Reconfigure keeps it.** Leaving the field as it is keeps the stored key; the flow
  is also the place to add one to an entry created before the hub was locked.
- **Control level only.** That is all the integration uses. An API key cannot unlock
  admin routes, so the **Reboot** button (an admin route) needs an admin PIN session
  and will report an error if the hub has an admin PIN set. Everything else —
  polling, output sources, presets, power, mute, stream, signal/display sensors, and
  all services — is control level and works with the key.
- **Rotating a key:** create the new key on the hub, paste it into **Options** (or
  **Reconfigure**), then delete the old one in the hub's settings.

Check what the hub requires at any time:

```bash
curl http://192.168.1.145:8080/api/auth/status
# => {"admin_pin_set": false, "control_pin_set": true, "session_level": "none", …}
```

**Option A (`rest_command`)?** Those calls are plain HTTP too: add
`headers: {"X-API-Key": "<key>"}` to the command, or append `?key=<key>` to the URL.

### Entities (one device per matrix, names include the hub's port names)

| Entity | What it does |
| --- | --- |
| `select` Output N source | Input shown on output N; options are the hub's input names |
| `switch` Power | Matrix on / standby |
| `switch` Output N mute / Output N stream | Audio mute and video stream of output N |
| `button` Recall preset N | Recalls preset slot N (1-8) |
| `button` Reboot | Restarts the matrix (admin route) |
| `binary_sensor` Input N signal | On while the source on input N sends video |
| `binary_sensor` Output N display | On while a display is connected to output N |

Entities become unavailable (not "off") when the hub or the matrix cannot be read.
Renaming an input, output or preset on the hub renames the entities after the next poll.

### Services

All three accept an optional `config_entry_id` or `device_id`; without one, the
only configured matrix is used. Invalid values are rejected before anything is
sent, and a failure reported by the hub is raised as an error.

| Service | Fields |
| --- | --- |
| `hdmi_matrix.recall_preset` | `preset` (1-8) |
| `hdmi_matrix.switch_input` | `output` (1-8), `input` (1-8) |
| `hdmi_matrix.send_cec_command` | `port_type` (`input` / `output`), `port_num` (1-8), `command`: sources accept `power_on`, `power_off`, `up`, `down`, `left`, `right`, `select`, `menu`, `back`, `previous`, `play`, `pause`, `stop`, `next`, `rewind`, `fast_forward`, `mute`, `volume_down`, `volume_up`; displays accept `power_on`, `power_off`, `mute`, `volume_down`, `volume_up`, `active` |

The full service schema lives in `custom_components/hdmi_matrix/services.yaml`.

---

## Alexa Integration (via Home Assistant)

Once integrated with Home Assistant, you can expose entities to Alexa:

### Using Home Assistant Cloud (Nabu Casa)

1. Subscribe to Nabu Casa
2. Link Alexa skill
3. Expose OREI entities

### Voice Commands

- *"Alexa, turn on PS5"* → Triggers preset 6
- *"Alexa, switch to Apple TV"* → Triggers preset 2
- *"Alexa, turn off the matrix"* → Power off

### Routine Examples

Create Alexa routines that trigger HA automations:

- *"Alexa, movie time"* → Dim lights + Switch to Shield + Start Plex
- *"Alexa, gaming mode"* → Switch to PS5 + Set game picture mode

---

## Troubleshooting

### Entities Unavailable, or setup fails to connect

The hub may have its control lock enabled, which requires an API key on every request:

1. Ask the hub owner whether `CONTROL_PIN` is set (or run
   `curl http://HUB:8080/api/auth/status` and look at `control_pin_set`).
2. If it is, get an API key from the hub (**Settings → Security → API keys**, or
   `POST /api/auth/api-keys` — see
   [FLIC_SETUP.md](FLIC_SETUP.md#generate-an-api-key)) and enter it in the
   integration's **Options** (or **Reconfigure**) as the **API key** field — see
   [API Key](#api-key-required-only-when-the-hubs-control-lock-is-on).
3. The integration reloads itself after the change; entities return on the next poll.

A `cannot_connect` error during initial setup usually means the host or port is wrong;
on a locked hub it can also mean the key was missing, so re-run the flow with it filled
in. The key travels as an HTTP header over the hub's plain-HTTP REST API, so keep Home
Assistant and the hub on a trusted LAN or a VPN.

### REST Commands Not Working

1. Verify the integration is running:
   ```bash
   curl http://192.168.1.145:8080/api/status
   ```
2. Check Home Assistant logs for REST command errors
3. Verify network connectivity from HA to Docker host

### Sensor Not Updating

- Check `scan_interval` setting (default 30 seconds)
- Verify the API returns valid JSON
- Check HA developer tools for sensor attributes

### Template Sensors Show "Unknown"

- Wait for first sensor update after restart
- Verify the REST sensor is returning data
- Check template syntax in developer tools

### Admin actions (`/api/system/reboot`, rename output, etc.) return 401

The admin PIN is set on the hub. The HACS integration does **not** store an
admin PIN: open the hub's Web UI (`http://HUB/ui`), sign in, and run the
action from there (or unlock the admin session programmatically with
`POST /api/auth/unlock` and pass the session cookie).
