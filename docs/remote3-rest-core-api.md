# Remote Two/3 REST Core-API

**Version:** 0.40.0  
**OpenAPI:** OAS3  
**License:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)  
**Documentation:** https://www.unfoldedcircle.com/  
**Support:** https://github.com/unfoldedcircle/core-api/issues  

OpenAPI Spec: `/doc/core-rest/openapi.yaml`

## Overview

The Unfolded Circle REST Core-API for Remote Two/3 (UCR REST Core-API) allows to configure the remote and manage custom resource files. Furthermore, API-keys for the WebSocket & REST APIs can be created.

The Unfolded Circle Remote Core-APIs consist of:
- This REST API
- The [UCR WebSocket Core-API](https://github.com/unfoldedcircle/core-api/tree/main/core-api/websocket), providing asynchronous events

The focus of the Core-APIs is to provide all functionality for the UI application and the web-configurator. They allow to interact with the Unfolded Circle remote-core service and take full control of its features.

The Core-APIs may also be used by other external systems and integration drivers, if specific configuration or interaction features are required, which are not present in the [UCR Integration-API](https://github.com/unfoldedcircle/core-api/tree/main/integration-api).

## Authentication

All API endpoints besides `/api/pub` are secured. Available authentication methods:

### Basic Auth
For every request. Should only be used for simple testing.
- **User:** `web-configurator`
- **Password:** Generated pin shown in the remote-UI

### Bearer Token
**Preferred method for external systems.**
- See `/auth/api_keys` endpoints on how to create and manage API keys
- Only the `admin` role is supported at the moment
- Example: `curl 'http://$IP/api/system' --header 'Authorization: Bearer $API_KEY'`

### Cookie-based Session
**Preferred method for web frontends** like the web-configurator.
- Use `/api/pub/login` endpoint to establish session

## API Versioning

The API is versioned according to [SemVer](https://semver.org/). Any major version zero (`0.y.z`) is for initial development and may change at any time!

## API Endpoints

### Public Info (No Auth Required)

#### GET /api/pub/version
Get version information about installed components.

#### GET /api/pub/status
Get status information about the system.

#### GET /api/pub/health_check
Retrieve health check information about the system and running services.

#### POST /api/pub/login
Log in and create session.

#### POST /api/pub/logout
Log out from session.

---

### API Keys Management

#### HEAD /api/auth/api_keys
Get total number of available API keys.

#### GET /api/auth/api_keys
List available API keys.

#### POST /api/auth/api_keys
Create an API key for the UCR APIs.

**Request Body:**
```json
{
  "name": "My API Key",
  "scopes": ["admin"]
}
```

**Response:** Returns the API key - **save it immediately as it won't be shown again!**

#### DELETE /api/auth/api_keys
Delete all API keys.

#### GET /api/auth/api_keys/{apiKeyId}
Get information about an API key.

#### PATCH /api/auth/api_keys/{apiKeyId}
Update properties of an API key.

#### DELETE /api/auth/api_keys/{apiKeyId}
Revoke an API key.

#### GET /api/auth/scopes
Get available access scopes.

---

### External Token Management

#### GET /api/auth/external
🧪 Get registered external systems.

#### DELETE /api/auth/external
Remove all external access tokens.

#### POST /api/auth/external/{system}
🧪 Provide an access token of an external system.

#### HEAD /api/auth/external/{system}
🧪 Get total number of available tokens for an external system.

#### GET /api/auth/external/{system}
🧪 List available tokens for an external system.

#### DELETE /api/auth/external/{system}
Remove all access tokens of an external system.

#### GET /api/auth/external/{system}/{tokenId}
🧪 Get external access token.

#### PUT /api/auth/external/{system}/{tokenId}
🧪 Replace an existing access token of an external system.

#### DELETE /api/auth/external/{system}/{tokenId}
Remove an external access token.

---

### Resource Management

Media files handling, e.g. manage background images, icons or sound effects.

#### GET /api/resources
Get supported media resource types.

#### DELETE /api/resources
Delete all resources.

#### HEAD /api/resources/{type}
Get total number of available resources of a given type.

#### GET /api/resources/{type}
List available media resources of a given type.

#### POST /api/resources/{type}
Upload media or other resource files.

#### DELETE /api/resources/{type}
Delete all resources of a given type.

#### GET /api/resources/{type}/{id}
Download a media resource.

#### DELETE /api/resources/{type}/{id}
Delete a media resource.

---

### Integration Management

#### HEAD /api/intg
Get total number of configured and external integrations.

#### GET /api/intg
Get overview of configured and external integrations.

#### GET /api/intg/discover
Get external integration driver discovery status.

#### PUT /api/intg/discover
Start discovery of external integration drivers.

**Query Parameters:**
- `timeout` (optional): Discovery timeout in seconds (default: 30)

#### DELETE /api/intg/discover
Stop discovery of external integration drivers.

#### GET /api/intg/discover/{driverId}
Get integration driver discovery information.

#### PUT /api/intg/discover/{driverId}
🧪 Execute connection test and fetch metadata from discovered integration driver.

#### POST /api/intg/discover/{driverId}
Register a discovered integration driver.

**Request Body:**
```json
{
  "name": "Integration Name",
  "driver_url": "ws://driver:9090"
}
```

#### POST /api/intg/install
🧪 Upload and install a custom integration.

#### GET /api/intg/setup
Get current integration setup processes.

#### POST /api/intg/setup
Start setting up a new integration driver.

**Request Body:**
```json
{
  "driver_id": "driver_id",
  "setup_data": {
    "field1": "value1",
    "field2": "value2"
  },
  "reconfigure": false
}
```

#### DELETE /api/intg/setup
Abort and remove all setup processes.

#### GET /api/intg/setup/{driverId}
Get integration driver setup status.

#### PUT /api/intg/setup/{driverId}
Provide requested integration setup data.

#### DELETE /api/intg/setup/{driverId}
Abort the integration driver setup process.

#### HEAD /api/intg/drivers
Get total number of registered integration drivers.

#### GET /api/intg/drivers
Get all registered integration drivers.

#### POST /api/intg/drivers
🧪 Manually register a new integration driver.

#### GET /api/intg/drivers/{driverId}
Get integration driver metadata.

#### PATCH /api/intg/drivers/{driverId}
Modify connection parameters of an external integration driver.

#### PUT /api/intg/drivers/{driverId}
Execute a command on an integration driver.

**Commands:**
- `START`: Start the driver
- `STOP`: Stop the driver
- `RESTART`: Restart the driver

#### POST /api/intg/drivers/{driverId}
Create a new integration instance from driver.

#### DELETE /api/intg/drivers/{driverId}
Remove an integration driver.

⚠️ **Warning:** All instances and entities will be removed!

#### HEAD /api/intg/instances
Get total number of integration instances.

#### GET /api/intg/instances
Get all integration instances.

**Query Parameters:**
- `type` (optional): Filter by type (LOCAL or EXTERNAL)
- `enabled` (optional): Filter by enabled state (true/false)

#### PUT /api/intg/instances
Connect or disconnect all integration instances.

**Commands:**
- `CONNECT`: Connect all instances
- `DISCONNECT`: Disconnect all instances

#### GET /api/intg/instances/{intgId}
Get an integration instance.

#### PATCH /api/intg/instances/{intgId}
Modify a configured integration instance.

#### DELETE /api/intg/instances/{intgId}
Remove an integration instance.

⚠️ **Warning:** All configured entities will be removed!

#### PUT /api/intg/instances/{intgId}
Connect or disconnect an integration instance.

#### GET /api/intg/instances/{intgId}/entities
Get available entities from integration instance.

**Query Parameters:**
- `filter` (optional): Filter by entity type

#### POST /api/intg/instances/{intgId}/entities
Configure multiple available entities.

**Request Body:**
```json
{
  "entity_ids": ["entity1", "entity2"]
}
```

If `entity_ids` is empty or not provided, all entities from the integration are configured.

#### POST /api/intg/instances/{intgId}/entities/{entityId}
Configure an available entity.

**Request Body:**
```json
{
  "name": "Custom Name",
  "icon": "uc:icon-name"
}
```

---

### Entity Management

Common handling of configured entities.

#### HEAD /api/entities
Get total number of configured entities.

#### GET /api/entities
Search and retrieve configured entities.

**Query Parameters:**
- `filter.type` (optional): Filter by entity type(s)
- `filter.integration_id` (optional): Filter by integration ID(s)
- `filter.text` (optional): Text search in name, identifier, integration name
- `exclude` (optional): Exclude entities from activity/macro/page/group
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

#### DELETE /api/entities
Remove configured entities.

**Query Parameters:**
- `integration_id` (optional): Remove entities from specific integration

#### GET /api/entities/{entityId}
Get a configured entity.

#### PATCH /api/entities/{entityId}
Modify a configured entity.

**Request Body:**
```json
{
  "name": "New Name",
  "icon": "uc:new-icon"
}
```

#### DELETE /api/entities/{entityId}
Remove a configured entity.

#### PUT /api/entities/{entityId}/command
Execute an entity command.

**Request Body:**
```json
{
  "cmd_id": "on",
  "params": {}
}
```

---

### Activity Management

Combine multiple entities into an activity.

#### HEAD /api/activities
Get total number of activity entities.

#### GET /api/activities
Get activity entities overview with paging.

**Query Parameters:**
- `page` (optional): Page number
- `limit` (optional): Items per page

#### POST /api/activities
Create a new activity entity.

**Request Body:**
```json
{
  "name": { "en": "Watch TV" },
  "description": { "en": "Turn on TV and receiver" },
  "icon": "uc:tv",
  "options": {
    "included_entities": [
      { "entity_id": "entity1", "entity_type": "media_player" }
    ],
    "sequences": {
      "on": [
        { "entity_id": "entity1", "cmd_id": "on" }
      ],
      "off": [
        { "entity_id": "entity1", "cmd_id": "off" }
      ]
    }
  }
}
```

#### DELETE /api/activities
Delete all activity entities.

#### GET /api/activities/{entityId}
Get an activity by its entity_id.

#### PATCH /api/activities/{entityId}
Update an activity entity.

#### DELETE /api/activities/{entityId}
Delete an activity entity.

#### GET /api/activities/{entityId}/buttons
Get the physical button mappings.

#### DELETE /api/activities/{entityId}/buttons
Reset the physical button mappings to their default state.

#### GET /api/activities/{entityId}/buttons/{buttonId}
Get a physical button mapping.

**Button IDs:** `DPAD_UP`, `DPAD_DOWN`, `DPAD_LEFT`, `DPAD_RIGHT`, `DPAD_MIDDLE`, `BACK`, `HOME`, `VOLUME_UP`, `VOLUME_DOWN`, `MUTE`, `CHANNEL_UP`, `CHANNEL_DOWN`, `POWER`

#### PATCH /api/activities/{entityId}/buttons/{buttonId}
Update a physical button mapping.

#### DELETE /api/activities/{entityId}/buttons/{buttonId}
Remove a physical button mapping.

#### GET /api/activities/{entityId}/ui
Get the user interface definition of an activity.

#### DELETE /api/activities/{entityId}/ui
Reset an activity user interface to its default state.

#### POST /api/activities/{entityId}/ui/pages
Create a new user interface page.

#### GET /api/activities/{entityId}/ui/pages
Get the user interface pages of an activity.

#### PATCH /api/activities/{entityId}/ui/pages
Update the activity user interface page order.

#### DELETE /api/activities/{entityId}/ui/pages
Reset the activity user interface pages to the default state.

#### GET /api/activities/{entityId}/ui/pages/{pageId}
Get a specific page definition.

#### PATCH /api/activities/{entityId}/ui/pages/{pageId}
Update an activity user interface page.

#### DELETE /api/activities/{entityId}/ui/pages/{pageId}
Delete an activity user interface page.

#### HEAD /api/activity_groups
Get total number of activity groups.

#### GET /api/activity_groups
Get activity groups overview with paging.

#### POST /api/activity_groups
Create a new activity group.

#### DELETE /api/activity_groups
Delete all activity groups.

#### GET /api/activity_groups/{groupId}
Get an activity group by its group_id.

#### PATCH /api/activity_groups/{groupId}
Update an activity group.

#### DELETE /api/activity_groups/{groupId}
Delete an activity group.

---

### Macro Management

Macros execute a sequence of commands.

#### HEAD /api/macros
Get total number of macro entities.

#### GET /api/macros
Get macro entities overview with paging.

#### POST /api/macros
Create a new macro entity.

**Request Body:**
```json
{
  "name": { "en": "Good Night" },
  "icon": "uc:moon",
  "sequence": [
    { "entity_id": "entity1", "cmd_id": "off", "delay": 1000 }
  ]
}
```

#### DELETE /api/macros
Delete all macro entities.

#### GET /api/macros/{entityId}
Get a macro by its entity_id.

#### PATCH /api/macros/{entityId}
Update a macro entity.

#### DELETE /api/macros/{entityId}
Delete a macro entity.

---

### Infrared Management

#### GET /api/ir/codes/manufacturers
Search supported infrared device manufacturers.

**Query Parameters:**
- `search` (optional): Search text

#### GET /api/ir/codes/manufacturers/{manufacturerId}
Search for infrared device code sets by manufacturer.

**Query Parameters:**
- `search` (optional): Search text for device model

#### GET /api/ir/codes/manufacturers/{manufacturerId}/{codeSetId}
Retrieve IR codeset command information for testing.

#### HEAD /api/ir/codes/custom
Get total number of custom infrared code sets.

#### GET /api/ir/codes/custom
Get all custom infrared code sets or export as CSV.

**Query Parameters:**
- `format` (optional): `json` or `csv`

#### POST /api/ir/codes/custom
Create a new custom infrared code set.

#### DELETE /api/ir/codes/custom
Delete all custom infrared code sets.

#### GET /api/ir/codes/custom/{codeSetId}
Get custom infrared code set or export as CSV.

#### PATCH /api/ir/codes/custom/{codeSetId}
Modify a custom infrared code set.

#### POST /api/ir/codes/custom/{codeSetId}
Bulk upload infrared codes with a CSV file.

#### DELETE /api/ir/codes/custom/{codeSetId}
Delete custom infrared code set.

#### GET /api/ir/codes/custom/{codeSetId}/{key}
Get a code definition from a custom infrared code set.

#### POST /api/ir/codes/custom/{codeSetId}/{key}
Add a new key to a custom infrared code set.

**Request Body:**
```json
{
  "format": "PRONTO",
  "code": "0000 006D 0000 0022 ..."
}
```

#### PUT /api/ir/codes/custom/{codeSetId}/{key}
Modify a code in a custom infrared code set.

#### DELETE /api/ir/codes/custom/{codeSetId}/{key}
Delete an entry in a custom infrared code set.

#### GET /api/ir/convert/{format}
Convert an IR code into a different format.

**Formats:** `PRONTO`, `HEX`

#### HEAD /api/ir/emitters
Get total number of infrared emitter devices.

#### GET /api/ir/emitters
Get all infrared emitter devices.

#### GET /api/ir/emitters/{emitterId}
Get an IR emitter device.

#### PUT /api/ir/emitters/{emitterId}/send
Send IR command.

**Request Body:**
```json
{
  "format": "PRONTO",
  "code": "0000 006D 0000 0022 ...",
  "repeat": 1
}
```

#### PUT /api/ir/emitters/{emitterId}/stop_send
Stop sending an IR command.

#### GET /api/ir/emitters/{emitterId}/learn
Get IR learning status and results.

#### PUT /api/ir/emitters/{emitterId}/learn
Start IR learning.

#### DELETE /api/ir/emitters/{emitterId}/learn
Stop IR learning and clear results.

---

### Remote Entity Management

#### HEAD /api/remotes
Get total number of remote-entities.

#### GET /api/remotes
Get remote-entities overview with paging.

#### POST /api/remotes
Create a new BT- or IR-remote entity.

**Request Body for IR Remote:**
```json
{
  "entity_type": "remote",
  "name": { "en": "TV Remote" },
  "icon": "uc:tv",
  "options": {
    "simple_commands": ["POWER", "VOLUME_UP", "VOLUME_DOWN"],
    "button_mapping": [
      {
        "button": "DPAD_UP",
        "short_press": { "cmd_id": "CURSOR_UP" }
      }
    ],
    "user_interface": {
      "pages": [
        {
          "page_id": "main",
          "name": "Main",
          "grid": { "width": 4, "height": 6 },
          "items": []
        }
      ]
    }
  },
  "ir_codeset": {
    "manufacturer": "samsung",
    "codeset_id": "tv-1234",
    "emitter_id": "dock-ir1"
  }
}
```

#### DELETE /api/remotes
Delete all remote-entities.

#### GET /api/remotes/{entityId}
Get a remote-entity by its entity_id.

#### PATCH /api/remotes/{entityId}
Update a remote-entity.

#### DELETE /api/remotes/{entityId}
Delete a remote-entity.

#### GET /api/remotes/{entityId}/ir
Get the infrared dataset of the remote-entity.

#### POST /api/remotes/{entityId}/ir/{cmdId}
Add a custom infrared command to the codeset.

#### GET /api/remotes/{entityId}/ir/{cmdId}
Get an infrared code in the codeset.

#### PATCH /api/remotes/{entityId}/ir/{cmdId}
Update an infrared command in the codeset.

#### DELETE /api/remotes/{entityId}/ir/{cmdId}
Delete a custom ir code or reset a modified manufacturer code.

#### GET /api/remotes/{entityId}/bt
🧪 Get information about a Bluetooth remote-entity.

#### GET /api/remotes/{entityId}/bt/pairing
🧪 Get pairing information of a Bluetooth remote-entity.

#### PUT /api/remotes/{entityId}/bt/pairing
🧪 Enable or disable BT-remote pairing.

#### POST /api/remotes/{entityId}/bt/pairing
🧪 Send a pairing response.

#### GET /api/remotes/{entityId}/buttons
Get the physical button mappings.

#### DELETE /api/remotes/{entityId}/buttons
Reset the physical button mappings to default.

#### GET /api/remotes/{entityId}/buttons/{buttonId}
Get a physical button mapping.

#### PATCH /api/remotes/{entityId}/buttons/{buttonId}
Update a physical button mapping.

#### DELETE /api/remotes/{entityId}/buttons/{buttonId}
Remove a physical button mapping.

#### GET /api/remotes/{entityId}/ui
Get the user interface definition.

#### DELETE /api/remotes/{entityId}/ui
Reset user interface to default.

#### POST /api/remotes/{entityId}/ui/pages
Create a new user interface page.

#### GET /api/remotes/{entityId}/ui/pages
Get the user interface pages.

#### PATCH /api/remotes/{entityId}/ui/pages
Update page order.

#### DELETE /api/remotes/{entityId}/ui/pages
Reset pages to default.

#### GET /api/remotes/{entityId}/ui/pages/{pageId}
Get a page definition.

#### PATCH /api/remotes/{entityId}/ui/pages/{pageId}
Update a page.

#### DELETE /api/remotes/{entityId}/ui/pages/{pageId}
Delete a page.

---

### Profile Management

#### POST /api/profiles
Create a new profile.

#### PUT /api/profiles
Switch active profile.

#### GET /api/profiles
Get all profiles or the active profile.

**Query Parameters:**
- `active_only` (optional): Return only active profile

#### DELETE /api/profiles
Delete all profiles.

#### GET /api/profiles/{profileId}
Get profile.

#### PATCH /api/profiles/{profileId}
Update properties of a profile.

#### DELETE /api/profiles/{profileId}
Delete profile.

#### POST /api/profiles/{profileId}/pages
Create a new page in the profile.

#### GET /api/profiles/{profileId}/pages
Get all pages of the profile.

#### DELETE /api/profiles/{profileId}/pages
Delete all pages of the profile.

#### GET /api/profiles/{profileId}/pages/{pageId}
Get a page of the profile.

#### PATCH /api/profiles/{profileId}/pages/{pageId}
Update properties of a page.

#### DELETE /api/profiles/{profileId}/pages/{pageId}
Delete a page.

#### POST /api/profiles/{profileId}/groups
Create a new group in the profile.

#### GET /api/profiles/{profileId}/groups
Get all groups of the profile.

#### DELETE /api/profiles/{profileId}/groups
Delete all groups of the profile.

#### GET /api/profiles/{profileId}/groups/{groupId}
Get a group in the profile.

#### PATCH /api/profiles/{profileId}/groups/{groupId}
Update properties of a group.

#### DELETE /api/profiles/{profileId}/groups/{groupId}
Delete a group.

---

### Configuration Settings

#### GET /api/cfg
Get all configuration settings.

#### DELETE /api/cfg
Reset all settings to default values.

#### GET /api/cfg/bt
🧪 Get Bluetooth settings.

#### PATCH /api/cfg/bt
🧪 Modify Bluetooth settings.

#### GET /api/cfg/bt/profiles
Get Bluetooth device profiles.

#### GET /api/cfg/bt/profiles/{id}
Retrieve a Bluetooth device profile.

#### GET /api/cfg/button
Get button settings.

#### PATCH /api/cfg/button
Modify button settings.

**Request Body:**
```json
{
  "autorepeat": {
    "enabled": true,
    "delay_ms": 500,
    "interval_ms": 100
  },
  "backlight": {
    "mode": "ALWAYS_ON",
    "brightness": 75,
    "timeout_sec": 10
  }
}
```

#### GET /api/cfg/device
Get remote device settings.

#### PATCH /api/cfg/device
Modify remote device settings.

**Request Body:**
```json
{
  "name": "Living Room Remote",
  "wakeup_sensitivity": "MEDIUM"
}
```

#### GET /api/cfg/device/button_layout
Get the button layouts of the device.

#### GET /api/cfg/device/icon_mapping
Get the native icon mapping of the device.

#### GET /api/cfg/device/screen_layout
Get the screen layout of the device.

#### GET /api/cfg/display
Get display settings.

#### PATCH /api/cfg/display
Modify display settings.

**Request Body:**
```json
{
  "brightness": 80,
  "auto_brightness": true,
  "sleep_timeout_sec": 30
}
```

#### GET /api/cfg/entity/commands
Get entity command definitions.

#### GET /api/cfg/features
Get feature flag settings.

#### PATCH /api/cfg/features
Modify a feature flag.

#### GET /api/cfg/haptic
Get haptic settings.

#### PATCH /api/cfg/haptic
Modify haptic settings.

**Request Body:**
```json
{
  "enabled": true,
  "strength": "MEDIUM"
}
```

#### GET /api/cfg/localization
Get localization settings.

#### PATCH /api/cfg/localization
Modify localization settings.

**Request Body:**
```json
{
  "language": "en_US",
  "country": "US",
  "timezone": "America/New_York",
  "time_format_24h": true,
  "temperature_unit": "CELSIUS",
  "measurement_unit": "METRIC"
}
```

#### GET /api/cfg/localization/tz_names
Get all available time zone names.

#### GET /api/cfg/localization/countries
Get all available countries.

#### GET /api/cfg/localization/translations
Get all available translations.

#### GET /api/cfg/network
Get network settings.

#### PATCH /api/cfg/network
Modify network settings.

**Request Body:**
```json
{
  "hostname": "remote3",
  "mdns_enabled": true
}
```

#### DELETE /api/cfg/network
Reset network settings.

#### GET /api/cfg/network/wifi
Get advanced wifi network settings.

#### PATCH /api/cfg/network/wifi
Modify advanced wifi network settings.

#### DELETE /api/cfg/network/wifi
Reset advanced wifi network settings.

#### GET /api/cfg/power_saving
Get power settings.

#### PATCH /api/cfg/power_saving
Modify power settings.

**Request Body:**
```json
{
  "standby_timeout_sec": 60,
  "wakeup_enabled": true
}
```

#### GET /api/cfg/profile
Get profile settings.

#### PATCH /api/cfg/profile
Modify profile settings.

#### GET /api/cfg/software_update
Get software update settings.

#### PATCH /api/cfg/software_update
Modify software update settings.

**Request Body:**
```json
{
  "auto_update": true,
  "channel": "STABLE"
}
```

#### DELETE /api/cfg/software_update
Reset software update settings to default.

#### GET /api/cfg/sound
Get sound settings.

#### PATCH /api/cfg/sound
Modify sound settings.

**Request Body:**
```json
{
  "volume": 50,
  "muted": false,
  "sound_effects_enabled": true
}
```

#### GET /api/cfg/voice_control
Get voice control settings.

#### PATCH /api/cfg/voice_control
Modify voice control settings.

#### GET /api/cfg/voice_control/voice_assistants
Get available voice assistants.

---

### Dock Management

#### HEAD /api/docks
Get total number of configured docks.

#### GET /api/docks
List configured docks and their connection state.

**Query Parameters:**
- `active` (optional): Filter by active state

#### POST /api/docks
Create a new dock configuration.

#### PUT /api/docks
Connect or disconnect all active dock connections.

#### DELETE /api/docks
Delete all dock configurations.

#### GET /api/docks/discover
Get docking station discovery status.

#### PUT /api/docks/discover
Start discovery of new docking stations.

**Query Parameters:**
- `timeout_sec` (optional): Discovery timeout (default: 30)
- `bt` (optional): Enable Bluetooth discovery (default: true)
- `mdns` (optional): Enable mDNS discovery (default: true)
- `new` (optional): Return only new docks (default: true)

#### DELETE /api/docks/discover
Stop discovery of new docking stations.

#### GET /api/docks/discover/{dockId}
Get docking station discovery device status.

#### PUT /api/docks/discover/{dockId}
Execute command on a discovered docking station.

**Commands:** `IDENTIFY`, `TEST_CONNECTION`

#### GET /api/docks/setup
Get current dock setup processes.

#### POST /api/docks/setup
Start setting up a new docking station.

#### DELETE /api/docks/setup
Abort and remove all setup processes.

#### GET /api/docks/setup/{dockId}
Get docking station setup status.

**Setup States:**
- `NEW`: Setup not yet started
- `CONFIGURING`: Transferring setup data
- `RESTARTING`: Dock restarting
- `OK`: Setup completed successfully
- `ERROR`: Setup failed

#### PUT /api/docks/setup/{dockId}
Setup docking station - provide WiFi credentials and settings.

#### DELETE /api/docks/setup/{dockId}
Abort the dock setup process.

#### GET /api/docks/devices/{dockId}
Get dock configuration.

#### PATCH /api/docks/devices/{dockId}
Change dock configuration.

**Request Body:**
```json
{
  "name": "Bedroom Dock",
  "auto_connect": true
}
```

#### PUT /api/docks/devices/{dockId}
Start or stop a dock connection.

**Commands:** `CONNECT`, `DISCONNECT`

#### DELETE /api/docks/devices/{dockId}
Delete dock configuration.

#### POST /api/docks/devices/{dockId}/command
Send a dock command.

**Commands:**
- `GET_AMBIENT_LIGHT`: Get ambient light sensor reading
- `SET_VOLUME`: Set speaker volume (0-100)
- `IDENTIFY`: Blink status LED
- `REMOTE_LOW_BATTERY`: Trigger low battery indicator
- `REMOTE_CHARGED`: Trigger charged indicator
- `REMOTE_NORMAL`: Normal operation mode
- `REBOOT`: Reboot dock
- `RESET`: Factory reset dock (requires admin privileges)

#### GET /api/docks/devices/{dockId}/update
Check for dock firmware updates.

#### PUT /api/docks/devices/{dockId}/update
Force dock firmware update check.

#### POST /api/docks/devices/{dockId}/update
Update dock firmware.

#### DELETE /api/docks/devices/{dockId}/update
🚧 Abort the dock firmware update.

#### GET /api/docks/devices/{dockId}/update/{id}
Check for dock firmware update progress.

#### GET /api/docks/devices/{dockId}/ir/send
Test IR command.

#### POST /api/docks/devices/{dockId}/ir/send
Send IR command.

#### GET /api/docks/devices/{dockId}/ports
🧪 Get all external port configurations.

#### DELETE /api/docks/devices/{dockId}/ports
🧪 Reset all external ports to default.

#### GET /api/docks/devices/{dockId}/ports/{portId}
🧪 Get external dock port configuration.

#### PATCH /api/docks/devices/{dockId}/ports/{portId}
🧪 Configure an external dock port.

#### DELETE /api/docks/devices/{dockId}/ports/{portId}
🧪 Reset external port configuration to default.

---

### System Management

#### GET /api/system
Get system information.

**Response includes:**
- Serial number
- Model number
- Hardware revision
- MAC address
- Firmware version
- Uptime

#### POST /api/system
Perform a system command.

**Commands:**
- `STANDBY`: Enter standby mode
- `REBOOT`: Reboot device
- `POWER_OFF`: Power off device
- `RESTART`: Restart all applications
- `RESTART_UI`: Restart UI application
- `RESTART_CORE`: Restart core service

#### GET /api/system/backup/export
Create and export a device configuration backup.

**Response:** ZIP file containing configuration

#### PUT /api/system/backup/restore
Upload and restore a device configuration backup.

**Request:** Multipart form with ZIP file

#### GET /api/system/backup/snapshots
👷 Get information about available system backup snapshots.

#### POST /api/system/backup/snapshots
👷 Create a new system backup snapshot.

#### DELETE /api/system/backup/snapshots
👷 Remove all system backups.

#### GET /api/system/backup/snapshots/{id}
👷 Get information about a backup or download archive.

#### PUT /api/system/backup/snapshots/{id}
👷 Restore a system backup snapshot.

#### DELETE /api/system/backup/snapshots/{id}
👷 Remove a system backup snapshot.

#### PUT /api/system/bt
🧪 Perform a Bluetooth operation.

**Commands:** `ENABLE`, `DISABLE`, `SCAN_START`, `SCAN_STOP`

#### DELETE /api/system/bt
🧪 Perform a Bluetooth subsystem reset.

#### GET /api/system/factory_reset
Get factory reset token.

Token is valid for 60 seconds.

#### POST /api/system/factory_reset
Perform a factory reset.

⚠️ **Warning:** All user data will be erased!

**Request Body:**
```json
{
  "token": "factory-reset-token"
}
```

#### GET /api/system/install
Get installed custom components.

#### GET /api/system/install/{customComponent}
Get status of a custom component installation.

#### PUT /api/system/install/{customComponent}
Enable or disable a custom component.

#### DELETE /api/system/install/{customComponent}
Remove an installed custom component.

#### POST /api/system/install/{customComponent}
Upload and install a custom component.

#### GET /api/system/logs
Retrieve and query log entries.

**Query Parameters:**
- `boot` (optional): Boot ID
- `service` (optional): Service name
- `priority` (optional): Log level (0-7)
- `lines` (optional): Number of lines
- `follow` (optional): Follow log stream

#### GET /api/system/logs/boots
Get boot identifiers for log access.

#### GET /api/system/logs/services
Get available services to retrieve log entries from.

#### GET /api/system/logs/hci
Download HCI trace file for Bluetooth debugging.

#### GET /api/system/logs/web
Get the log-streaming web app configuration.

#### PUT /api/system/logs/web
Configure log-streaming web app.

#### GET /api/system/power
Get current system power mode and standby duration.

**Response:**
```json
{
  "mode": "NORMAL",
  "power_supply": true,
  "battery_level": 85,
  "standby_timeout_sec": 300
}
```

#### PUT /api/system/power
Set a power mode.

**Modes:** `NORMAL`, `LOW_POWER`, `STANDBY`

#### GET /api/system/power/battery
Get battery status.

**Response:**
```json
{
  "level": 85,
  "voltage_mv": 3950,
  "current_ma": -150,
  "temperature_c": 28,
  "status": "DISCHARGING"
}
```

#### GET /api/system/power/charger
Get battery charger information.

#### PUT /api/system/power/charger
👷 Enable or disable wireless charging.

#### GET /api/system/power/standby_inhibitors
Get standby inhibitors.

#### POST /api/system/power/standby_inhibitors
Create a standby inhibitor.

**Request Body:**
```json
{
  "id": "my-inhibitor",
  "reason": "Integration setup in progress",
  "type": "BLOCKING"
}
```

**Types:**
- `BLOCKING`: Prevents standby until removed
- `TEMPORARY`: Delays standby by specified time

#### DELETE /api/system/power/standby_inhibitors
Remove all standby inhibitors.

#### DELETE /api/system/power/standby_inhibitors/{id}
Remove a standby inhibitor.

#### GET /api/system/sensors/ambient_light
Get current ambient light reading.

**Response:**
```json
{
  "lux": 250
}
```

#### GET /api/system/update
Check if system update is available.

#### PUT /api/system/update
Force system update check.

#### POST /api/system/update/{updateId}
Perform system update.

#### GET /api/system/update/{updateId}
Get system update progress.

**Response:**
```json
{
  "state": "DOWNLOADING",
  "progress": 45,
  "total_size_mb": 250,
  "downloaded_mb": 112
}
```

#### GET /api/system/wifi
Get WiFi status.

**Response:**
```json
{
  "state": "CONNECTED",
  "ssid": "MyNetwork",
  "signal_strength": -45,
  "ip_address": "192.168.1.100",
  "mac_address": "AA:BB:CC:DD:EE:FF"
}
```

#### PUT /api/system/wifi
WiFi connection handling.

**Commands:**
- `DISCONNECT`: Disconnect WiFi
- `RECONNECT`: Reconnect WiFi
- `REASSOCIATE`: Force reassociation
- `ENABLE_ALL_NETWORKS`: Enable all networks
- `SAVE_CONFIG`: Save configuration

#### GET /api/system/wifi/scan
Get discovered WiFi access points.

#### PUT /api/system/wifi/scan
Start discovery of WiFi access points.

#### DELETE /api/system/wifi/scan
Stop discovery of WiFi access points.

#### GET /api/system/wifi/networks
Get configured WiFi networks.

#### POST /api/system/wifi/networks
Create a new WiFi network configuration.

**Request Body:**
```json
{
  "ssid": "MyNetwork",
  "password": "SecurePassword123"
}
```

⚠️ Only WPA-PSK and open networks are supported!

#### DELETE /api/system/wifi/networks
Delete all configured WiFi networks.

#### GET /api/system/wifi/networks/{wifiId}
Get WiFi network configuration.

#### PATCH /api/system/wifi/networks/{wifiId}
Modify a network configuration.

**Request Body:**
```json
{
  "password": "NewPassword456",
  "priority": 10
}
```

#### PUT /api/system/wifi/networks/{wifiId}
WiFi network connection handling.

**Commands:** `CONNECT`, `DISCONNECT`, `ENABLE`, `DISABLE`

#### DELETE /api/system/wifi/networks/{wifiId}
Delete a configured WiFi network.

---

## Common HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created successfully
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists or conflict
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

## Status Legend

- 🚀 Ready to use
- 🧪 Implemented and testing
- 🔍 Review & implementation
- 👷 Work in progress
- 🚧 Planned feature
- 💡 Idea / not yet official
