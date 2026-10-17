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

### 3. Setup Authentication (UC-02)

The integration WebSocket listens on TCP **9095** (`driver.json` → `port`, overridable
with `UC_INTEGRATION_HTTP_PORT`) and answers on every network interface, so the setup
conversation must be authorized and the port itself should be firewalled.

**Setup token — `UC_AUTH_TOKEN` (or `ADMIN_PIN` as fallback secret)**

Set `UC_AUTH_TOKEN` in the hub's environment and the driver:

- advertises **`pwd: true`** in the driver metadata (the mDNS TXT record), so the Remote
  asks for a password instead of running an unauthenticated setup;
- adds a **"Hub setup token"** field to the setup page instead of the matrix-password
  field; and
- requires the token on **every** `DriverSetupRequest` — a first setup *and* a
  reconfigure. A missing or wrong token returns
  `ucapi.SetupError(error_type=ucapi.IntegrationSetupError.AUTHORIZATION_ERROR)` and
  changes nothing on the hub.

```yaml
# docker-compose.yml (hub service)
environment:
  UC_ENABLED: "true"
  UC_AUTH_TOKEN: "<long random secret>"
```

The Remote sends the token with the address:

```
DriverSetupRequest  setup_data = {"host": "192.168.1.100", "port": 443, "auth_token": "…"}
```

The driver accepts it as `auth_token`, `token`, or `pin`, compares it with
`hmac.compare_digest`, and never logs it: `auth_token`, `token`, `pin`, and
`current_password` are added to ucapi's sensitive-key list, so the value is redacted in
the Remote's message log as well as in the driver's own logs.

If `ADMIN_PIN` is set and `UC_AUTH_TOKEN` is not, the admin PIN doubles as the setup
token — one secret for both. Prefer a dedicated `UC_AUTH_TOKEN` so the PIN can be
changed or cleared without re-provisioning every Remote. A token change likewise
requires re-entering it on each Remote (`pwd` is advertised at startup).

**Without a token: the current matrix password guards address changes**

With no token set, the setup page keeps the **"Current matrix password (when changing
address)"** field. Changing the matrix host or port then requires re-entering that
matrix's password; a missing or wrong value returns `AUTHORIZATION_ERROR` and the
running configuration stays untouched. The stored password is never sent to a new
address: the driver first checks the target answers, then asks for that matrix's login.

**Network: firewall port 9095**

The token protects *setup*, not the transport — anything that can reach TCP 9095 can
still subscribe to the entities and control the matrix. Restrict the port to the
Remote's IP, in the file that matches how the hub runs:

```yaml
# docker-compose.uc-bridge.yml (bridge networking): replace the published
# port so 9095 is reachable on the hub's LAN address only.
services:
  hdmi-matrix-hub:
    ports:
      - "192.168.1.20:${UC_HOST_PORT:-9095}:9095"   # Remote 3 only
      # was: "${UC_HOST_PORT:-9095}:9095"  (every interface)
```

```bash
# docker-compose.uc-host.yml (host networking): 9095 is the host's own port,
# so the firewall is the only place to restrict it.
sudo ufw allow from 192.168.1.60 to any port 9095 proto tcp   # the Remote
sudo ufw deny 9095/tcp                                        # everyone else
```

Apply the rule on the host that actually terminates the port — with host networking that
is the Docker host itself, not the container. A Remote on another subnet or VLAN should
reach the hub over a VPN rather than through an open port. If you change the port the
hub advertises, keep `UC_DRIVER_URL` in step: it is the `driver_url` the Remote is
registered with, and it must name the address you just allowed.

### 4. Entity Lifecycle

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

### 5. Device State Management

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

### 6. Remote Entity Specifics

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
8. **Require a setup token** (`UC_AUTH_TOKEN`) and keep the setup token redacted from logs

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

**`AUTHORIZATION_ERROR` on the Remote**
- `UC_AUTH_TOKEN` (or `ADMIN_PIN`) is set on the hub and the Remote sent no token or the
  wrong one — enter the **"Hub setup token"** on the setup page; a reconfigure needs it
  too, not just the first setup.
- The token was changed on the hub, so Remotes still hold the old value. Keep the token
  stable, or re-enter it on every Remote after changing it.
- No token is configured, but the matrix address was changed: re-enter the **current
  matrix password** in the field the setup page shows.
- Hub log lines: `Setup: authorization token missing or invalid` or
  `Setup: current matrix password required to change its address`.
- Note that a port-9095 firewall rule blocking the Remote produces the same "setup does
  nothing" symptom from the Remote's side — check reachability before changing tokens.

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

`"port"` is the integration WebSocket port the Remote connects to (the OREI hub uses
9095; `UC_INTEGRATION_HTTP_PORT` overrides it). The hub does not put `"pwd"` or the
token field in `driver.json`: when `UC_AUTH_TOKEN`/`ADMIN_PIN` is set, the driver adds
`pwd: true` and the **Hub setup token** field to the published metadata at startup —
see [Setup Authentication](#3-setup-authentication-uc-02).

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
**Library Version**: v0.7.0 (pinned in requirements-uc.txt, pyproject.toml, setup.py; UC-15)
**Author**: Based on Unfolded Circle documentation and examples
