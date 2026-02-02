# Unfolded Circle Integration Development Guide

## Overview
This document provides comprehensive information about developing integrations for Unfolded Circle Remote Two/3 devices using the Python integration library.

## Key Concepts

### 1. Integration Architecture

**Two Entity Storage Systems:**
- **`available_entities`**: Entities that CAN be added to the remote (defined during setup)
- **`configured_entities`**: Entities actively subscribed to by the remote (what the user actually uses)

**Critical Flow:**
1. Setup phase → populate `api.available_entities`
2. User subscribes to entities on remote → entities automatically copied to `api.configured_entities`
3. Commands come to entities in `configured_entities`

### 2. Setup Flow Lifecycle

The setup process follows this sequence:

```python
# 1. DriverSetupRequest - Initial setup or reconfiguration
async def handle_driver_setup(msg: ucapi.DriverSetupRequest) -> ucapi.SetupAction:
    # msg.reconfigure tells you if this is a new setup or reconfiguration
    # msg.setup_data contains user input from setup_data_schema
    
    # CRITICAL: Clear entities if not reconfiguring
    if not msg.reconfigure:
        api.available_entities.clear()
        api.configured_entities.clear()
    
    # Connect to your device, create entities, add to available_entities
    
    return ucapi.SetupComplete()  # Or RequestUserInput for multi-step

# 2. Optional: UserDataResponse for multi-step setup
async def handle_user_data(msg: ucapi.UserDataResponse) -> ucapi.SetupAction:
    # msg.input_values contains data from previous step
    return ucapi.SetupComplete()  # Or another RequestUserInput

# 3. AbortDriverSetup - User canceled
# msg.error indicates why (OTHER = user canceled, TIMEOUT = timed out)
```

**Setup Return Actions:**
- `SetupComplete()` - Setup successful
- `SetupError(error_type=IntegrationSetupError.OTHER)` - Setup failed  
- `RequestUserInput(title, settings)` - Need more user input (multi-step)
- `RequestUserConfirmation(title, header, footer)` - Need user to confirm something

### 3. Entity Lifecycle

**Adding Entities:**
```python
# During setup, create and add to available_entities
entity = ucapi.Remote(
    identifier="unique_id",  # Must be unique
    name="Display Name",
    features=[ucapi.remote.Features.ON_OFF, ucapi.remote.Features.SEND_CMD],
    attributes={ucapi.remote.Attributes.STATE: "ON"},
    simple_commands=["CMD1", "CMD2"],
    cmd_handler=my_command_handler
)
api.available_entities.add(entity)
```

**Subscription Flow:**
- Remote calls `subscribe_events` with entity IDs →
- Library automatically copies from `available_entities` to `configured_entities` →
- `Events.SUBSCRIBE_ENTITIES` event fires with list of entity IDs

**Entity Commands:**
```python
async def cmd_handler(entity, cmd_id, params, websocket) -> ucapi.StatusCodes:
    # entity: The actual entity object
    # cmd_id: Command identifier (e.g., "on", "send_cmd")
    # params: Optional dict with command parameters
    # websocket: Connection (for directed events)
    
    if cmd_id == "send_cmd":
        command = params.get("command")  # Get the actual command
        # Do something with it
    
    # Update entity state if needed
    api.configured_entities.update_attributes(
        entity.id,
        {ucapi.remote.Attributes.STATE: "ON"}
    )
    
    return ucapi.StatusCodes.OK
```

### 4. Device State Management

**Device States:**
- `CONNECTED` - Ready and connected
- `CONNECTING` - Establishing connection
- `DISCONNECTED` - Not connected
- `ERROR` - Error state

**Always set device state on connect:**
```python
@api.listens_to(ucapi.Events.CONNECT)
async def on_connect():
    await api.set_device_state(ucapi.DeviceStates.CONNECTED)
```

### 5. Remote Entity Specifics

**Features:**
- `ON_OFF` - Has on/off commands
- `TOGGLE` - Has toggle command
- `SEND_CMD` - Can send custom commands

**Commands:**
- `ON`, `OFF`, `TOGGLE` - State commands
- `SEND_CMD` - Send a simple command (params: {"command": "CMD_NAME"})
- `SEND_CMD_SEQUENCE` - Send command sequence (params: {"sequence": [...], "delay": ms})

**UI Pages:**
```python
from ucapi.ui import UiPage, Size, create_ui_text

page = UiPage(
    page_id="main",
    name="Main Page",
    grid=Size(width=4, height=6),  # 4 columns, 6 rows
    items=[
        create_ui_text(
            text="Button Label",
            x=0, y=0,  # Grid position
            cmd="COMMAND_NAME",  # simple_command to execute
            size=Size(2, 1)  # 2 wide, 1 tall
        )
    ]
)
```

**Button Mapping:**
```python
from ucapi.ui import Buttons, create_btn_mapping

# Map physical remote buttons to commands
# Note: Buttons enum is for PHYSICAL buttons on the remote
# NOT digit buttons (those don't exist in ui.Buttons)
mappings = [
    create_btn_mapping(Buttons.HOME, "HOME"),  # Short press
    create_btn_mapping(Buttons.POWER, "ON", "OFF"),  # Short and long press
]
```

## Common Patterns

### Minimal Integration
```python
import asyncio
import ucapi

loop = asyncio.new_event_loop()
api = ucapi.IntegrationAPI(loop)

async def setup_handler(msg: ucapi.SetupDriver) -> ucapi.SetupAction:
    if isinstance(msg, ucapi.DriverSetupRequest):
        # Clear existing
        api.available_entities.clear()
        api.configured_entities.clear()
        
        # Create entity
        entity = ucapi.Button("btn1", "My Button", cmd_handler=my_handler)
        api.available_entities.add(entity)
        
        return ucapi.SetupComplete()
    return ucapi.SetupError()

async def my_handler(entity, cmd_id, params, websocket):
    return ucapi.StatusCodes.OK

@api.listens_to(ucapi.Events.CONNECT)
async def on_connect():
    await api.set_device_state(ucapi.DeviceStates.CONNECTED)

loop.run_until_complete(api.init("driver.json", setup_handler))
loop.run_forever()
```

### With External Device Connection
```python
_device = None  # Global device connection

async def setup_handler(msg: ucapi.SetupDriver) -> ucapi.SetupAction:
    global _device
    
    if isinstance(msg, ucapi.DriverSetupRequest):
        if not msg.reconfigure:
            api.available_entities.clear()
            api.configured_entities.clear()
        
        # Connect to device
        host = msg.setup_data.get("host")
        _device = MyDevice(host)
        await _device.connect()
        
        # Create entities based on device capabilities
        # ...
        
        return ucapi.SetupComplete()
    return ucapi.SetupError()
```

## Important Rules

### DO:
1. **Always clear entities** on first setup (not reconfigure)
2. **Always set device state** in `on_connect` handler
3. **Add entities to `available_entities`** during setup
4. **Let the library manage `configured_entities`** (automatic from subscriptions)
5. **Handle `reconfigure` flag properly** (don't clear on reconfigure)
6. **Return appropriate StatusCodes** from command handlers
7. **Update entity attributes** when state changes

### DON'T:
1. **Don't manually add to `configured_entities`** (library does this on subscription)
2. **Don't use DIGIT buttons** from `ui.Buttons` (they don't exist - use MediaPlayer.Commands instead)
3. **Don't forget to handle AbortDriverSetup** in setup handler
4. **Don't create entities without command handlers** (unless they're read-only sensors)
5. **Don't modify available_entities** after setup is complete
6. **Don't forget the driver runs continuously** (not request-response)

## Debugging Tips

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check What The Remote Sees
```python
# Log available entities
_LOG.debug("Available: %s", api.available_entities.get_all())

# Log configured entities
_LOG.debug("Configured: %s", list(api.configured_entities._storage.keys()))
```

### Common Issues

**"Data already exists"**
- Old integration instance still registered on remote
- Solution: Delete ALL instances from remote, restart driver, re-add

**Entities not appearing**
- Not added to `available_entities` during setup
- Setup didn't return `SetupComplete()`
- Check logs for setup errors

**Commands not working**
- Entity not in `configured_entities` (user didn't subscribe)
- Command handler returning wrong status code
- Command name doesn't match `simple_commands` list

**Setup keeps failing**
- Exception in setup handler
- Network/device connection failing  
- Forgot to return `SetupAction` from handler
- Setup taking too long (timeout)

## File Structure

```
my-integration/
├── driver.py              # Main entry point
├── driver.json           # Driver metadata with setup_data_schema
├── orei_matrix.py        # Device-specific logic
├── requirements.txt      # Dependencies
└── README.md
```

## Driver Metadata (driver.json)

```json
{
  "driver_id": "unique_driver_id",
  "version": "0.1.0",
  "min_core_api": "0.21.0",
  "name": {"en": "My Integration"},
  "icon": "uc:integration",
  "description": {"en": "Integration description"},
  "developer": {
    "name": "Developer Name",
    "url": "https://github.com/..."
  },
  "home_page": "https://...",
  "release_date": "2026-01-13",
  "port": 9090,
  "setup_data_schema": {
    "title": {"en": "Setup"},
    "settings": [
      {
        "id": "host",
        "label": {"en": "IP Address"},
        "field": {"text": {"value": "192.168.1.100"}}
      },
      {
        "id": "port",
        "label": {"en": "Port"},
        "field": {"number": {"value": 443, "min": 1, "max": 65535}}
      }
    ]
  }
}
```

## References

- **Core API Documentation**: https://github.com/unfoldedcircle/core-api
- **Python Library**: https://github.com/unfoldedcircle/integration-python-library
- **Entity Documentation**: https://unfoldedcircle.github.io/core-api/entities/
- **Examples**: See library's `examples/` directory

## Integration Examples

- Android TV: https://github.com/unfoldedcircle/integration-androidtv
- Apple TV: https://github.com/unfoldedcircle/integration-appletv  
- Denon AVR: https://github.com/unfoldedcircle/integration-denonavr

---

**Last Updated**: January 13, 2026
**Library Version**: v0.5.1
**Author**: Based on Unfolded Circle documentation and examples
