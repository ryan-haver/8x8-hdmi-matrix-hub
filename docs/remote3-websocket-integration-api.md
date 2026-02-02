# Remote Two/3 WebSocket Integration API

**Version:** 0.12.1-beta  
**License:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)  
**Documentation:** https://www.unfoldedcircle.com/  
**Support:** https://github.com/unfoldedcircle/core-api/issues  
**ID:** urn:com:unfoldedcircle:integration

## Overview

The UCR Integration-API allows writing device integration drivers for the Unfolded Circle Remotes.

ℹ️ Starting with the UCR2 firmware beta release 1.9.0, custom integration drivers can be installed on the UC Remote.

The integration driver acts as **server** and the UC Remote as **client**. The remote connects to the integration when an integration instance is configured. Whenever the remote enters standby it may choose to disconnect and connect again after wakeup.

The goal of the Integration-API is to cover simple static drivers like controlling GPIOs on a Raspberry Pi, up to integrating existing home automation hubs like Home Assistant, Homey, ioBroker, openHAB etc.

**The focus of the integration API is on entity integration, not on controlling or configuring the UC Remote.** Please refer to the Core-API for other functionality.

## API Versioning

The API is versioned according to [SemVer](https://semver.org/). The initial public release will be `1.0.0` once it is considered stable enough with some initial integration implementations and developer examples.

**Any major version zero (`0.y.z`) is for initial development and may change at any time!** Backward compatibility for minor releases is not yet established, anything MAY change at any time!

## Security

### HTTP API Key

The API token is either provided in the `auth-token` header while upgrading to a WebSocket connection, or with an authentication message.

- **Header name:** `AUTH-TOKEN`
- **Location:** HEADER

**Authentication Flow:**
1. If the integration driver doesn't support header based authentication, it must send the `auth_required` message event after the WebSocket connection is established. The UC Remote will then authenticate with the `auth` request message.
2. If the driver doesn't support or require authentication, it still needs to send the `authentication` message with `code: 200` and `req_id: 0` after the WebSocket connection has been established by the UC Remote.

## Server Configuration

**Default Ports:**
- `localhost:8443` - WSS (secure WebSocket)
- `localhost:8001` - WS (insecure WebSocket for testing)

## Required Messages

Simple integrations with static entities don't need to implement all messages. All required messages are tagged with the 🍕 emoji.

### Authentication

#### auth_required (Event)
🚀 Authentication request event after connection is established.

This event is only sent if the integration doesn't support header based authentication during connection setup. The UC Remote will then authenticate with the `auth` request message.

#### auth (Request)
🚀 Authenticate a connection.

Sent by the UC Remote after an `auth_required` request by the integration driver.

#### authentication (Response)
🚀 🍕 **REQUIRED** Authentication response.

The authentication result is provided in the `code` attribute:
- `200`: success, API can be used and message requests are accepted.
- `401`: authentication failed, the provided token is not valid. The UC Remote will close the connection.

**If the driver doesn't support or require authentication, it still needs to send the `authentication` message with `code: 200` and `req_id: 0` after the WebSocket connection has been established.**

It's recommended to send the optional driver version object in the `msg_data` payload to avoid eventual additional message exchanges.

### Driver Information

#### get_driver_version (Request)
🚀 🍕 **REQUIRED** Get version information about the integration driver.

#### driver_version (Response)
🚀 🍕 **REQUIRED** Integration driver version information response.

#### get_driver_metadata (Request)
🚀 🍕 **REQUIRED** Retrieve the integration driver metadata.

The metadata is used to setup the driver in the remote / web-configurator and start the setup flow.

#### driver_metadata (Response)
🧪 🍕 **REQUIRED** Integration driver metadata response.

**Driver Metadata Structure:**
```json
{
  "driver_id": "string",
  "name": { "en": "Driver Name" },
  "version": "0.1.0",
  "icon": "uc:icon-name",
  "description": { "en": "Description" },
  "developer": {
    "name": "Developer Name",
    "email": "email@example.com",
    "url": "https://example.com"
  },
  "home_page": "https://example.com",
  "setup_data_schema": { /* JSON Schema for setup form */ },
  "release_date": "2024-01-01"
}
```

### Device State Management

#### get_device_state (Request)
🚀 🍕 **REQUIRED** Get the current integration driver or device state.

Called by the UC Remote when it needs to synchronize the device state, e.g. after waking up from standby, or if it doesn't receive regular `device_state` events.

The `device_id` property is only required if the driver supports multiple device instances.

**Note:** This request will not be answered with a response message but with an event.

For simple drivers without dynamic devices the `msg_data` object can be omitted.

#### device_state (Event)
🚀 🍕 **REQUIRED** Current integration driver or device state event.

If there's a device communication issue or other error, this state will inform the user with a UI notification about the issue.

This event should be triggered by the integration driver whenever the state changes. Furthermore, the UC Remote can request the current state with the `get_device_state` request.

**Device States:**
- `CONNECTED`: Device is connected and ready
- `CONNECTING`: Device connection in progress
- `DISCONNECTED`: Device is disconnected
- `ERROR`: Device error state

#### connect (Event)
🧪 Event to establish connection to entities or devices.

**Optional:** This event instructs the integration to establish the required connections to interact with the provided entities or devices.

#### disconnect (Event)
🧪 Event to stop the connection to entities or devices.

**Optional:** This event instructs the integration to stop the interactions with the provided entities or devices.

### Driver Setup

#### setup_driver (Request)
🚀 Start driver setup.

If a driver includes a `setup_data_schema` object in its driver metadata, it enables the dynamic driver setup process.

The `reconfigure` flag indicates if the user wants to reconfigure an already configured driver.

After confirming the `setup_driver` request, the integration driver has to send `driver_setup_change` events:
- `event_type: SETUP` with `state: SETUP` is a progress event to keep the process running.
- `event_type: SETUP` with `state: WAIT_USER_ACTION` can be sent to request user interaction.
- `event_type: STOP` with `state: OK` finishes the setup process.
- `event_type: STOP` with `state: ERROR` aborts the setup process.

**⚠️ Important Timeouts:**
- Setup progress (watchdog): 60 seconds
- User action timeout: 3 minutes
- Overall setup timeout: 5 minutes

#### driver_setup_change (Event)
🚀 Driver setup state change event.

Emitted for all driver setup flow state changes.

**Setup States:**
- `SETUP`: setup in progress
- `WAIT_USER_ACTION`: setup flow is waiting for user input
- `OK`: setup finished successfully
- `ERROR`: setup error

**Setup Error Codes:**
- `NONE`
- `NOT_FOUND`
- `CONNECTION_REFUSED`
- `AUTHORIZATION_ERROR`
- `TIMEOUT`
- `OTHER`

#### set_driver_user_data (Request)
🚀 Provide requested driver setup data.

Defined user actions:
- `input_values`: if the user was requested to enter settings.
- `confirm`: response to the user action `confirmation`.

#### abort_driver_setup (Event)
🚀 Abort a driver setup.

If the user aborts the setup process, the UC Remote sends this event.

### Entity Management

#### get_available_entities (Request)
🚀 🍕 **REQUIRED** Retrieve the available entities from the integration driver.

Called while configuring profiles and assigning entities to pages or groups in the web-configurator or the embedded editor of the remote UI.

With the optional filter, only entities of a given type can be requested.

#### available_entities (Response)
🚀 🍕 **REQUIRED** Available entities response.

This message contains the available entities from the integration driver the UC Remote can configure.

#### subscribe_events (Request)
🚀 🍕 **REQUIRED** Subscribe to events.

Subscribe to entity state change events to receive `entity_change` events from the integration driver.

If no entity IDs are specified then events for all available entities are sent to the UC Remote.

#### unsubscribe_events (Request)
🧪 Unsubscribe from events.

If no entity IDs are specified then all events for all available entities are stopped.

#### get_entity_states (Request)
🚀 🍕 **REQUIRED** Get the current state of the configured entities.

Called by the UC Remote when it needs to synchronize the dynamic entity attributes, e.g. after connection setup or waking up from standby.

The integration should only send the state of the configured entities to reduce communication overhead.

⚠️ **Future change:** This request will be enhanced with a `force` flag to signal that all entity states are required.

#### entity_states (Response)
🚀 🍕 **REQUIRED** Current state of the entities.

Response message of the `get_entity_states` request. Contains the dynamic attributes of all entities.

The `msg_data` payload is an array of the `entity_change` event.

#### entity_command (Request)
🚀 🍕 **REQUIRED** Execute an entity command.

Instruct the integration driver to execute a command like "turn on" or "change temperature". Optional command data can be provided in the `params` array.

The `result` response is to acknowledge the command and to return any immediate failures.

**After successfully executing a command, the UC Remote expects an `entity_change` event with the updated feature value(s).**

#### entity_change (Event)
🚀 🍕 **REQUIRED** Entity state change event.

Emitted when an attribute of an entity changes, e.g. is switched off. Either after an `entity_command` or if the entity is updated manually through a user or an external system.

**Event Structure:**
```json
{
  "entity_id": "string",
  "entity_type": "switch",
  "attributes": {
    "state": "ON",
    /* other entity-specific attributes */
  }
}
```

### Standby Management

#### enter_standby (Event)
🚀 UC Remote goes into standby event.

Notification event that the UC Remote goes into standby mode and won't process incoming events anymore.

#### exit_standby (Event)
🚀 UC Remote leaves standby event.

Notification event that the UC Remote is out of standby. The integration should resume operation if it suspended it while receiving the `enter_standby` event.

### Optional Messages

#### get_version (Request)
🧪 Get UC Remote version information. ℹ️ implemented in firmware 0.9.2.

#### version (Response)
🧪 Remote version information response.

#### get_supported_entity_types (Request)
🧪 Get supported entities in the UC Remote. ℹ️ implemented in firmware 0.9.2.

This is a metadata request for supported entities in the UC Remote and allows the client to check if it's still compatible.

#### supported_entity_types (Response)
🚀 Supported entity types response.

#### get_configured_entities (Request)
🧪 Retrieve configured entities from this integration. ℹ️ implemented in firmware 0.9.2.

Request the configured entities in the UC Remote originating from this integration.

⚠️ This doesn't mean that all entities are actively being used (assigned in a profile and shown in the user interface).

#### configured_entities (Response)
🚀 Configured entities response.

#### get_localization_cfg (Request)
🧪 Retrieve the localization settings of the UC Remote. ℹ️ implemented in firmware 0.9.2.

#### localization_cfg (Response)
🧪 Active localization settings of the UC Remote.

**Language code format:** Two-letter [ISO-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) code, optionally followed by an [ISO-3166 country code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes) separated by underscore.

Examples: `en`, `en_UK`, `en_US`, `de`, `de_DE`, `de_CH`

#### get_runtime_info (Request)
🔍 Retrieve driver runtime information from the Remote. ℹ️ implemented in firmware 0.9.2.

#### runtime_info (Response)
🔍 Driver runtime information from the UC Remote.

#### entity_available (Event)
🔍 New entity available event.

Optional event to notify the UC Remote that new entities are available.

#### entity_removed (Event)
🔍 Entity removed event.

Optional event to notify the UC Remote that entities were removed and no longer available.

## Entity Types

Supported entities as extensible enum:

### Core Entity Types

#### button
A button entity can fire an event or start an action which cannot be further controlled once started. Used for "fire and forget" commands.

A button is stateless. To represent something that can be turned on and off, use the `switch` entity.

[Button entity documentation](https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_button.md)

#### switch
A switch entity can turn something on or off and the current state should be readable by the integration driver.

If the state can't be read, the `readable` option property can be set to `false`.

[Switch entity documentation](https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_switch.md)

#### climate
A climate entity controls heating, ventilation and air conditioning (HVAC) devices.

[Climate entity documentation](https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_climate.md)

#### cover
Entity for covering or opening things like blinds, window covers, curtains, etc. The entity `features` specify the abilities of the cover.

[Cover entity documentation](https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_cover.md)

#### light
A light entity can be switched on and off and depending on its features, the light source can be further controlled like setting brightness, hue, color saturation and color temperature.

The [HSV color model](https://en.wikipedia.org/wiki/HSL_and_HSV) is used for adjusting color and brightness.

[Light entity documentation](https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_light.md)

#### media_player
A media player entity controls playback of media on a device.

[Media player entity documentation](https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_media_player.md)

#### remote
A remote entity can send commands to a controllable device.

[Remote entity documentation](https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_remote.md)

#### sensor
A sensor entity provides measured values from devices or dedicated hardware sensors.

The device class specifies the type of sensor:
- The `custom` device class allows arbitrary UI labels and units.
- The `temperature` device class performs automatic conversion between °C and °F.

[Sensor entity documentation](https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_sensor.md)

#### ir_emitter
An IR-emitter entity allows to send IR commands in PRONTO hex format.

This entity allows to integrate external IR blasters and emitters.

[IR-emitter entity documentation](https://github.com/unfoldedcircle/core-api/blob/main/doc/entities/entity_ir_emitter.md)

## Setup Data Schema

Integration drivers can define a `setup_data_schema` object in their metadata to enable dynamic setup. This uses a settings page concept with various input types:

### Setting Types

#### Number
Number input with optional `min`, `max`, `steps` and `decimals` properties. An optional `units` field can be displayed next to the input.

#### Text
Single line of text input.

#### TextArea
Multi-line text input, e.g. for providing a description.

#### Password
Password or pin entry field with the input text hidden from the user.

#### Checkbox
Checkbox setting with `true` / `false` values.

#### Dropdown
Dropdown setting to pick a single value from a list. All values must be strings.

#### Label
Additional read-only text for information purpose between other settings. Supports Markdown formatting.

### Confirmation Page

A confirmation screen can be shown with:
- Title
- Message text (supports Markdown)

Used for requiring user to perform an action (e.g., "Press the button on the device").

## User Interface Definition

Integrations can define custom user interfaces for remote and media player entities:

### User Interface Structure
```json
{
  "pages": [
    {
      "page_id": "string",
      "name": "Page Name",
      "grid": { "width": 4, "height": 6 },
      "items": [
        {
          "command": "entity_id.command_name",
          "type": "icon",
          "icon": "uc:icon-name",
          "text": { "en": "Button Text" },
          "location": { "x": 0, "y": 0 },
          "size": { "width": 1, "height": 1 }
        }
      ]
    }
  ]
}
```

### UI Item Types
- **Icon:** Button with icon
- **Text:** Button with text label
- **Icon + Text:** Button with both icon and text
- **Media info:** Display media player information

### Grid Layout
- Default button size: 1x1
- 0-based coordinates for placement
- Customizable grid dimensions per page

## Device Button Mapping

Remote and activity entities can map physical buttons on the UC Remote to entity commands:

```json
{
  "button_id": "DPAD_UP",
  "short_press": {
    "command": "entity_id.command_name",
    "params": { /* optional parameters */ }
  },
  "long_press": {
    "command": "entity_id.other_command"
  }
}
```

**Button Press Types:**
- `short_press`: Quick button press
- `long_press`: Hold button for extended time

## Message Structure

All messages follow a common structure:

### Request Message
```json
{
  "kind": "req",
  "id": 1,
  "msg": "get_driver_version",
  "msg_data": {}
}
```

### Response Message
```json
{
  "kind": "resp",
  "req_id": 1,
  "code": 200,
  "msg": "driver_version",
  "msg_data": {}
}
```

### Event Message
```json
{
  "kind": "event",
  "msg": "device_state",
  "msg_data": {}
}
```

## Common Response Codes

- `200`: Success
- `400`: Invalid data in request
- `401`: Authentication failed
- `404`: Not found
- `409`: Conflict (e.g., already exists)
- `422`: Unprocessable entity
- `500`: Internal error
- `503`: Service unavailable / Communication error

## Status Legend

- 🚀 Ready to use - feedback welcomed
- 🧪 API has been implemented and is currently being tested
- 🔍 API definition review & implementation
- 👷 API definition is work in progress, not ready yet for implementation
- 🚧 Planned feature not yet fully implemented
- 💡 Idea, not yet official part of API definition
- 🍕 **REQUIRED MESSAGE** - Must be implemented

## Best Practices

1. **Always send `device_state` events** when the device connection state changes
2. **Respond to `entity_command`** requests quickly with a result code, then send `entity_change` event when complete
3. **Send `driver_setup_change` progress events** during setup to prevent timeouts
4. **Implement `get_entity_states`** efficiently - only send changed data when possible
5. **Handle `enter_standby` / `exit_standby`** to optimize resource usage
6. **Use `subscribe_events`** to know which entities are actively being used
7. **Keep entity IDs stable** - don't change them between driver restarts
8. **Provide meaningful error messages** in response codes and device_state events
9. **Test with standby cycles** - ensure proper reconnection after Remote wakes up
10. **Implement authentication** if your driver communicates over the network
