> **Historical upstream reference snapshot.** Source: [Unfolded Circle core-api](https://github.com/unfoldedcircle/core-api). The specification version and CC BY-SA 4.0 license recorded below apply to this snapshot; its exact source commit was not recorded. Consult the [pinned reference guide](UNFOLDED_CIRCLE.md) for current development references and [third-party notices](../../THIRD_PARTY_NOTICES.md) for attribution.

# Remote Two/3 WebSocket Core-API

**Version:** 0.31.0-beta  
**License:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)  
**Documentation:** https://www.unfoldedcircle.com/  
**Support:** https://github.com/unfoldedcircle/core-api/issues  

## Overview

The Unfolded Circle Remote Core-APIs consist of:
- This WebSocket API
- The [UCR REST Core-API](https://github.com/unfoldedcircle/core-api/tree/main/core-api/rest)

The remote-core service acts as WebSocket server. Whenever the remote enters standby it may choose to disconnect client connections.

The focus of the Core-APIs is to provide all functionality for the UI application and the web-configurator. They allow to interact with the Unfolded Circle remote-core service and take full control of its features.

The Core-APIs may also be used by other external systems and integration drivers, if specific configuration or interaction features are required, which are not present in the [UCR Integration-API](https://github.com/unfoldedcircle/core-api/tree/main/integration-api).

## API Versioning

The API is versioned according to [SemVer](https://semver.org/). The initial public release will be `1.0.0` once it is considered stable enough with some initial integration implementations and developer examples.

**Any major version zero (`0.y.z`) is for initial development and may change at any time!** Backward compatibility for minor releases is not yet established, anything MAY change at any time!

## WebSocket Connection

### Authentication

Interaction with the API requires an API-key, user account or a session cookie (see login operation in the REST Core-API).

#### Basic Authentication
A user account can be used with [basic authentication](https://en.wikipedia.org/wiki/Basic_access_authentication) in the WebSocket upgrade.

- **Header name:** `Authentication`
- **Value:** `Basic ` + base64 encoded value of `${username}:${password}`

#### API-key Authentication
If the session based login is not possible or the client needs to use an API-key, then the preferred way to establish an authenticated WebSocket connection is to provide the API-key in the header of the WebSocket connection.

- **Header name:** `API-KEY`
- **Value:** API key

API keys can be created with the REST API and the `auth/api_keys` endpoints.

#### Message Based Authentication
If the client cannot provide the API-key in the connection setup (e.g. a web browser), the server will send the `auth_required` message right after the connection is established.

The client must reply with the `auth` message containing the API-key.

- All other messages will be ignored, until the client successfully authenticates itself.
- The server will close an unauthenticated connection after a timeout of 15 seconds.

The server replies with the `authentication` event including the result code of the authentication:
- `200`: authentication succeeded, API can be used.
- `401`: invalid authentication and the connection will be closed.

## Key Messages

### System Commands

#### ping/pong
🚀 Application level based ping to determine whether connection is alive. Additional payload data may be included in `msg_data` which will be echoed by the server.

#### version
🚀 Get version information.

#### system
🚀 Get system information - hardware information about the device like serial number, model number and hardware revision.

#### system_cmd
🧪 Perform a system command like reboot or power-off.

The following system commands can be executed:
- `STANDBY`: Put the device into standby mode.
- `REBOOT`: Reboot the device.
- `POWER_OFF`: Switch off the device
- `RESTART`: Restart all applications.
- `RESTART_UI`: Restart the ui application.
- `RESTART_CORE`: Restart the core service application.

### Power Management

#### get_power_mode
🧪 Get current power mode, battery information and duration to enter standby.

Returns the current power mode of the device, if a power-supply is connected and the duration in seconds until the device will enter standby.

#### set_power_mode
🧪 Change the current power mode.

#### get_battery_charger
👷 Get battery charger information. Device features:
- `DOCK_CHARGING`: device can be charged in docking station (UCR2, UCR3).
- `WIRELESS_CHARGING`: device has wireless charging support (UCR3).

#### update_battery_charger
👷 Enable or disable wireless charging.

#### get_standby_inhibitors
🧪 Get standby inhibitors. Automatic system standby can be prevented with "standby inhibitors".

There are two types of inhibitors:
- **Temporary inhibitors** set a delay value for which the device doesn't go into standby.
- **Blocking inhibitors** will prevent the device to go into standby until the inhibitor is removed by the client.

#### create_standby_inhibitor
🧪 Create a standby inhibitor.

#### del_standby_inhibitor
🧪 Remove a standby inhibitor.

### Configuration Settings

#### get_configuration
🧪 Get all system settings.

#### get_button_cfg / set_button_cfg
🧪 Get/modify button settings including backlight configuration.

#### get_device_cfg / set_device_cfg
🧪 Get/modify remote device settings.

#### get_display_cfg / set_display_cfg
🧪 Get/modify display settings.

#### get_features_cfg / set_features_cfg
🧪 Get/modify feature flag settings.

#### get_haptic_cfg / set_haptic_cfg
🧪 Get/modify haptic settings.

#### get_localization_languages
🧪 Get stored translations or request available translations from the UI.

#### get_network_cfg / set_network_cfg
🧪 Get/modify network settings.

### Entity Management

#### get_entities
🧪 Search and retrieve configured entities. Returns all configured entities, optionally filtered by one or multiple entity types or integrations. Supports pagination and text search.

The `exclude` query parameter allows to exclude entities defined in an activity, macro, profile page or group.

#### get_available_entities
🧪 Retrieve the available entities provided by an integration.

⚠️ At the moment it's only possible to retrieve available entities from one integration at a time. `filter.integration_id` must be specified!

### Integration Management

#### get_integration_status
🧪 Retrieve an overview of the integration instances and their current connection state.

#### integration_cmd
🧪 Execute an integration command - Connect or disconnect integration instances.

If `integration_id` is specified, then the command only applies to the given integration, otherwise to all integration instances.

#### integration_driver_cmd
🧪 Execute an integration driver command - Start or stop integration drivers.

If `driver_id` is specified, then the command only applies to the given driver, otherwise to all integration drivers.

#### get_integration_driver_count / get_integration_drivers
🧪 Get total number and list of registered integration drivers.

#### register_integration_driver
🧪 Register a new integration driver.

#### get_integration_driver / update_integration_driver / delete_integration_driver
🧪 Retrieve, modify, or remove an integration driver.

#### get_integration_count / get_integrations
🧪 Get total number and list of integration instances.

#### create_integration / get_integration / update_integration / delete_integration
🧪 Create, get, modify, or remove an integration instance.

#### configure_entity_from_integration
🧪 Configure an available entity. Configure a new UC Remote entity from an available integration entity.

#### configure_entities_from_integration
🧪 Configure multiple available entities. If `entity_ids` is not provided or is empty, all entities from the integration are configured.

#### get_integration_discovery_status
🧪 Get external integration driver discovery status.

#### start_integration_discovery
🧪 Start discovery of external integration drivers with mDNS. By default the discovery automatically stops after 30 seconds.

#### stop_integration_discovery
🧪 Stop discovery of external integration drivers.

#### get_discovered_integration_driver
🧪 Get integration driver discovery information.

#### get_discovered_intg_driver_metadata
👷 Execute connection test and fetch metadata from discovered integration driver.

#### configure_discovered_integration_driver
🧪 Register a discovered integration driver.

#### get_integration_setup_processes
🧪 Get current integration setup processes.

#### setup_integration
🧪 Start setting up a new integration driver.

Request body:
- `name`: optional integration name. If not specified the name of the integration driver is used.
- `setup_data`: optional driver setting values corresponding to the driver's `setup_data_schema` object.
- `reconfigure`: set to true to reconfigure an already configured driver.

#### stop_all_integration_setups
🧪 Abort and remove all setup processes.

#### get_integration_setup_status
🧪 Get integration driver setup status.

Defined setup states:
- `SETUP`: setup is running and configuring the integration.
- `WAIT_USER_ACTION`: user input is required to continue the setup process.
- `OK`: setup process has been completed successfully.
- `ERROR`: the setup process failed.

#### set_integration_user_data
🧪 Provide requested integration setup data.

Defined user actions:
- `input_values`: if the user was requested to enter settings.
- `confirm`: response to the user action `confirmation`.

#### stop_integration_setup
🧪 Abort the integration driver setup process.

### Dock Management

#### get_dock_count / get_docks
🧪 Get total number and list of configured docks with their connection state.

#### get_dock_discovery_status
🧪 Get docking station discovery status.

#### start_dock_discovery
🧪 Start discovery of new docking stations over Bluetooth and mDNS.

#### exec_cmd_on_discovered_dock
🧪 Execute command on a discovered docking station (e.g., `IDENTIFY` to blink LED).

#### create_dock_setup
🧪 Start setting up a new docking station.

#### get_dock_setup_status / start_dock_setup / stop_dock_setup
🧪 Get status, start, or stop dock setup process.

### WiFi Management

#### get_wifi_status
🧪 Get WiFi status.

#### wifi_scan_start / wifi_scan_stop
🧪 Start/stop discovery of WiFi access points.

#### get_wifi_scan_status
🧪 Get discovered WiFi access points.

#### get_all_wifi_networks
🧪 Get configured WiFi networks.

#### add_wifi_network
🧪 Create a new WiFi network configuration. ⚠️ Only WPA-PSK and open networks are supported!

#### del_all_wifi_networks
🧪 Delete all configured WiFi networks.

#### get_wifi_network / update_wifi_network
🧪 Get or modify WiFi network configuration.

### Profile Management

#### get_profiles
🧪 Retrieve all profiles.

#### get_pages / get_page
🧪 Get all pages or a specific page of a profile.

#### get_groups / get_group
🧪 Get all groups or a specific group in a profile.

#### add_group / update_group / delete_group
🧪 Create, update, or delete a UI group.

## Integration States

### Driver State
- `NOT_CONFIGURED`
- `IDLE`
- `CONNECTING`
- `ACTIVE`
- `RECONNECTING`
- `ERROR`

### Integration State
- `NOT_CONFIGURED`
- `UNKNOWN`
- `IDLE`
- `CONNECTING`
- `CONNECTED`
- `DISCONNECTED`
- `RECONNECTING`
- `ACTIVE`
- `ERROR`

### Integration Driver Type
- `LOCAL`
- `EXTERNAL`

## Message Structure

All messages follow a common structure:
- **Request messages** include a `req_id` (request message ID) which is reflected in the response message.
- **Response messages** contain a `code` (result code) and optional error information.
- **Event messages** are asynchronous notifications sent by the server.

### Common Response Codes
- `200`: Success
- `400`: Invalid data in request body
- `401`: Authentication failed
- `404`: Resource not found
- `409`: Conflict (e.g., setup process already running)
- `422`: Unprocessable entity
- `503`: Service not available / Communication error

## Status Legend

- 🚀 Ready to use - feedback welcomed
- 🧪 API has been implemented and is currently being tested
- 🔍 API definition review & implementation
- 👷 API definition is work in progress, not ready yet for implementation
- 🚧 Planned feature and most likely not fully implemented in initial release
- 💡 Idea, not yet official part of API definition
