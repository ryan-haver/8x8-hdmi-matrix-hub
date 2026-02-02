# Home Assistant Integration Guide

> **Status**: ✅ REST API v2.7.0 Ready (with WebSocket & Scenes) | 🔲 HACS Component Planned (Phase 3.0)

This guide explains how to integrate the OREI HDMI Matrix with Home Assistant.

## Integration Options

### Option A: REST Commands (Available Now ✅)
Use Home Assistant's built-in REST integration with the REST API.

**Pros**: No custom code, works immediately, full API access
**Cons**: Manual configuration, no automatic entity discovery

### Option B: HACS Custom Component (Full Integration)
A proper Home Assistant integration with entities, services, and device registry.

**Pros**: Full functionality, proper UI, automations, device tracking
**Cons**: Requires development (Phase 3.0)

---

## Option A: REST Commands ✅ READY

### Prerequisites
- OREI Matrix integration running (Docker or standalone)
- REST API running on port 8080
- Home Assistant installed

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Get matrix status and routing |
| `/api/input/{n}` | POST | Switch all outputs to input N |
| `/api/input/next?output=N` | POST | Cycle to next input on output N |
| `/api/input/previous?output=N` | POST | Cycle to previous input on output N |
| `/api/output/{n}/source` | POST | Set specific output to specific input |
| `/api/preset/{n}` | POST | Recall preset N (1-8) |
| `/api/preset/{n}/save` | POST | Save current routing to preset N |
| `/api/power/on` | POST | Power on matrix |
| `/api/power/off` | POST | Power off matrix |
| `/api/output/{n}/enable` | POST | Enable/disable output stream |
| `/api/output/{n}/hdcp` | POST | Set HDCP mode (1-5) |
| `/api/output/{n}/hdr` | POST | Set HDR mode (1-3) |
| `/api/output/{n}/scaler` | POST | Set scaler mode (1-5) |
| `/api/output/{n}/arc` | POST | Enable/disable ARC |
| `/api/output/{n}/mute` | POST | Mute/unmute audio output |
| `/api/cec/{type}/{n}/enable` | POST | Enable/disable CEC per port |
| `/api/cec/input/{n}/power_on` | POST | CEC power on input device |
| `/api/cec/input/{n}/power_off` | POST | CEC power off input device |
| `/api/cec/input/{n}/play` | POST | CEC play command |
| `/api/cec/input/{n}/pause` | POST | CEC pause command |
| `/api/cec/output/{n}/volume_up` | POST | CEC volume up on output |
| `/api/cec/output/{n}/volume_down` | POST | CEC volume down on output |
| `/api/cec/output/{n}/mute` | POST | CEC mute on output |
| `/api/system/reboot` | POST | Reboot matrix |
| `/api/edid/modes` | GET | List EDID modes (v2.5+) |
| `/api/input/{n}/edid` | POST | Set EDID mode for input (v2.5+) |
| `/api/system/lcd/modes` | GET | List LCD timeout modes (v2.5+) |
| `/api/system/lcd` | POST | Set LCD timeout (v2.5+) |
| `/api/ext-audio/modes` | GET | List ext-audio modes (v2.6+) |
| `/api/ext-audio/mode` | POST | Set ext-audio mode (v2.6+) |
| `/api/ext-audio/{n}/enable` | POST | Enable/disable ext-audio (v2.6+) |
| `/api/ext-audio/{n}/source` | POST | Set ext-audio source (v2.6+) |
| `/api/scenes` | GET | List scenes (v2.7+) |
| `/api/scene/{id}` | GET | Get scene details (v2.7+) |
| `/api/scene` | POST | Create/update scene (v2.7+) |
| `/api/scene/{id}` | DELETE | Delete scene (v2.7+) |
| `/api/scene/{id}/recall` | POST | Apply scene (v2.7+) |
| `/api/scene/save-current` | POST | Save current state as scene (v2.7+) |

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

  # Input cycling (NEW in v2.1.0)
  orei_input_next:
    url: "http://192.168.1.145:8080/api/input/next?output={{ output }}"
    method: POST
  orei_input_previous:
    url: "http://192.168.1.145:8080/api/input/previous?output={{ output }}"
    method: POST

  # Direct output control (NEW in v2.1.0)
  orei_set_output_source:
    url: "http://192.168.1.145:8080/api/output/{{ output }}/source"
    method: POST
    content_type: "application/json"
    payload: '{"input": {{ input }}}'

  # Global input switching
  orei_switch_all_to_input:
    url: "http://192.168.1.145:8080/api/input/{{ input }}"
    method: POST

  # Advanced Output Control (NEW in v2.2.0)
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

  # Preset Management (NEW in v2.2.0)
  orei_save_preset:
    url: "http://192.168.1.145:8080/api/preset/{{ preset }}/save"
    method: POST

  # System Control (NEW in v2.2.0)
  orei_reboot:
    url: "http://192.168.1.145:8080/api/system/reboot"
    method: POST

  # EDID Control (NEW in v2.5.0)
  orei_set_edid:
    url: "http://192.168.1.145:8080/api/input/{{ input }}/edid"
    method: POST
    content_type: "application/json"
    payload: '{"mode": {{ mode }}}'

  # LCD Control (NEW in v2.5.0)
  orei_set_lcd_timeout:
    url: "http://192.168.1.145:8080/api/system/lcd"
    method: POST
    content_type: "application/json"
    payload: '{"mode": {{ mode }}}'  # 0=Off, 1=Always, 2=15s, 3=30s, 4=60s

  # External Audio Control (NEW in v2.6.0)
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

  # Scene Control (NEW in v2.7.0)
  orei_recall_scene:
    url: "http://192.168.1.145:8080/api/scene/{{ scene_id }}/recall"
    method: POST
  orei_save_current_scene:
    url: "http://192.168.1.145:8080/api/scene/save-current"
    method: POST
    content_type: "application/json"
    payload: '{"id": "{{ scene_id }}", "name": "{{ scene_name }}"}'

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

### REST Sensor for Matrix Status

Monitor matrix state in Home Assistant:

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

### Using in Automations

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

  # Scene-based automations (NEW in v2.7.0)
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

### Using in Scripts

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

### Dashboard Cards

#### Preset Button Row
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

#### Input Navigation Buttons
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

#### Matrix Status Card
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

#### Power Control Row
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

### Planned Features (Phase 3.0)
- Config flow for easy setup
- Device registry with proper device info
- Entities:
  - `select.orei_matrix_output_1_input` - Select input for each output
  - `button.orei_preset_1-8` - Preset buttons
  - `media_player.orei_input_1-8` - CEC control per input
  - `switch.orei_matrix_power` - Power control
  - `sensor.orei_matrix_routing` - Current routing state
- Services:
  - `orei_matrix.recall_preset`
  - `orei_matrix.switch_input`
  - `orei_matrix.set_output_source`
  - `orei_matrix.send_cec`

### Installation (Future)
1. Add custom repository to HACS
2. Install "OREI HDMI Matrix" integration
3. Restart Home Assistant
4. Add integration via UI
5. Enter matrix IP address and credentials

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

---

*Last updated: REST API v2.7.0*
