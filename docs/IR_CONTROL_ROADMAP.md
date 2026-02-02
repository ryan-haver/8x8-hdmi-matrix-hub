# IR Control System Roadmap

## Executive Summary

This document outlines the architecture and implementation plan for adding IR (Infrared) control capabilities to the OREI HDMI Matrix integration. The goal is to control non-networked devices (TVs, receivers, cable boxes, projectors, etc.) across multiple rooms using IR extenders/transmitters connected to the network.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Design Goals](#design-goals)
3. [**BLOCKERS - Must Resolve Before Development**](#blockers---must-resolve-before-development)
4. [Remote 3 Built-in IR Integration](#remote-3-built-in-ir-integration)
5. [Architecture Overview](#architecture-overview)
6. [IR Transport Layer](#ir-transport-layer)
7. [Device Abstraction Layer](#device-abstraction-layer)
8. [IR Code Management](#ir-code-management)
9. [Room/Zone Management](#roomzone-management)
10. [Integration Points](#integration-points)
11. [Implementation Phases](#implementation-phases)
12. [Technical Challenges](#technical-challenges)
13. [Hardware Recommendations](#hardware-recommendations)

---

## Problem Statement

### Current State
- The OREI BK-808 matrix controls HDMI routing between sources and displays
- Switching an input on the matrix doesn't automatically control the connected devices
- Many home AV devices (TVs, receivers, projectors) don't have network control
- IR remains the universal control method for most consumer electronics

### Desired State
- When a scene is activated, automatically:
  - Switch the matrix to the correct routing
  - Power on the appropriate TV/display
  - Set the receiver to the correct input
  - Control volume, power, and other functions
- Provide room-by-room control independent of matrix scenes
- Support ad-hoc IR commands for any device

---

## Design Goals

### 1. Hardware Agnostic
Support multiple IR transmitter hardware:
- **Network-based**: Global Caché iTach, Broadlink RM4 Pro, Tuya-based devices
- **USB-based**: USB-UIRT, FLIRC (limited), Arduino-based solutions
- **Embedded**: Some HDMI matrices have IR passthrough (investigate BK-808)
- **Future**: ESPHome-based DIY solutions, Home Assistant integrations

### 2. Protocol Agnostic  
Support all major IR protocols:
- **NEC** (most common - LG, Samsung, many others)
- **RC5/RC6** (Philips, Microsoft MCE)
- **Sony SIRC** (12, 15, 20-bit variants)
- **Samsung** (proprietary format)
- **Panasonic** (48-bit)
- **JVC**, **Sharp**, **Denon**, **Pioneer**, etc.

### 3. Device Agnostic
Abstract device control into capabilities:
- Don't hardcode "Samsung TV" - model as "Display with Power, Volume, Input"
- Use capability-based device profiles
- Support custom device definitions

### 4. Extensible
- Plugin architecture for new IR transmitter hardware
- JSON-based device profiles (community shareable)
- Learning mode for unknown devices
- Pronto Hex code import

### 5. Reliable
- IR is one-way (no feedback) - implement state tracking
- Retry logic for critical commands (power on)
- Command queuing to prevent IR collision

---

## BLOCKERS - Must Resolve Before Development

> ⚠️ **These items MUST be resolved before IR development can begin.**

### BLOCKER 1: IR Hardware Selection & Inventory

**Status**: 🔴 BLOCKED

**Description**: Need to determine what IR blaster hardware to use for development and deployment.

**Current State**:
- May have existing IR hardware available
- May need to purchase new hardware
- Need to inventory what's currently available

**Required Actions**:
- [ ] Inventory existing IR hardware (make, model, capabilities)
- [ ] Test existing hardware for compatibility
- [ ] Determine if additional hardware needed
- [ ] Select primary development hardware
- [ ] Document hardware setup and placement per zone

**Questions to Answer**:
1. What IR blasters/extenders do you currently have?
2. What brands/models are they?
3. Are they network-connected, USB, or RF-based?
4. Where are they physically located (which rooms)?
5. Do they support learning mode?

**Resolution Criteria**: Hardware inventory complete, primary dev hardware selected and tested.

---

### BLOCKER 2: OREI BK-808 IR Capabilities Investigation

**Status**: 🔴 BLOCKED

**Description**: The BK-808 reportedly has IR receiver and IR blaster capabilities. This must be documented before development to understand:
- Can we leverage built-in IR instead of (or in addition to) external blasters?
- What are the limitations?
- Is there API access to the IR features?

**Current State**:
- User believes BK-808 has IR receiver and blaster
- No documentation reviewed yet
- No testing performed

**Required Actions**:
- [ ] Review BK-808 manual for IR specifications
- [ ] Locate IR receiver/blaster ports on the unit
- [ ] Test IR receiver - can matrix learn IR codes?
- [ ] Test IR blaster - can matrix send IR commands?
- [ ] Check HTTP API for IR-related endpoints
- [ ] Determine if IR pass-through on HDMI exists
- [ ] Document all findings

**Questions to Answer**:
1. Where are the IR ports physically located on the BK-808?
2. Does the web interface have IR configuration pages?
3. Are there API endpoints like `/api/ir/*` or similar?
4. Can IR commands be routed per-output?
5. What's the IR blaster range/power?

**Documentation to Review**:
- BK-808 User Manual (IR section)
- BK-808 Control4 Driver (may reveal IR capabilities)
- BK-808 RTI Driver (may reveal IR capabilities)
- HTTP API exploration

**Resolution Criteria**: Full understanding of BK-808 IR capabilities documented, with decision on whether to use built-in IR.

---

### BLOCKER 3: Remote 3 IR Integration Research

**Status**: 🟡 NEEDS RESEARCH (see next section for details)

**Description**: The Unfolded Circle Remote 3 has a built-in IR blaster. We should leverage this for:
- Line-of-sight IR control from the remote itself
- Fallback when network blasters unavailable
- Learning IR codes directly from original remotes

**Required Actions**:
- [ ] Review UC Integration API for IR capabilities
- [ ] Determine if integrations can send IR via the remote
- [ ] Understand IR learning API
- [ ] Document IR code format used by Remote 3
- [ ] Test IR transmission from integration commands

**Resolution Criteria**: Clear understanding of how to use Remote 3 IR from our integration.

---

## Remote 3 Built-in IR Integration

> 📍 **This section documents how to leverage the Remote 3's built-in IR capabilities.**

### Overview

The Unfolded Circle Remote 3 has:
- **IR Blaster**: Sends IR commands directly from the remote
- **IR Receiver**: Can learn IR codes from other remotes
- **Wide-angle coverage**: ~180° horizontal coverage

This provides **line-of-sight control** wherever the user is pointing the remote.

### Why Use Remote 3 IR?

| Use Case | Benefit |
|----------|---------|
| **Direct Control** | User points remote at TV → IR sent immediately |
| **No Network Dependency** | Works even if network blasters offline |
| **Learning Mode** | Learn codes from any original remote |
| **Fallback** | Backup when zone blasters fail |
| **Simple Setup** | No additional hardware in some rooms |

### Integration API Research Required

Based on the Unfolded Circle documentation, we need to research:

#### 1. IR Entity Type

The UC API likely has an IR entity type. We need to verify:

```python
# Hypothetical - needs verification from UC API docs
class IREntity:
    entity_type = "ir"  # or "remote"?
    
    # Capabilities to investigate:
    # - send_ir: Send an IR code
    # - learn_ir: Enter learning mode
    # - ir_codes: Store/retrieve codes
```

#### 2. Sending IR Commands

Our integration may be able to request IR transmission:

```python
# Hypothetical API - needs verification
async def send_ir_command(code: str, format: str = "pronto"):
    """
    Request Remote 3 to send IR command.
    
    Questions:
    - Does the integration API support this?
    - Or is IR only for "remote" entity types?
    - Can we trigger IR from a media_player entity command?
    """
    pass
```

#### 3. IR Learning Flow

For learning mode:

```python
# Hypothetical flow - needs verification
async def learn_ir_code():
    """
    1. Integration requests Remote 3 enter learning mode
    2. User presses button on original remote
    3. Remote 3 captures IR signal
    4. Remote 3 returns captured code to integration
    5. Integration stores code for future use
    """
    pass
```

#### 4. Documentation to Review

- [ ] [remote3-websocket-integration-api.md](remote3-websocket-integration-api.md) - Check for IR methods
- [ ] [remote3-rest-core-api.md](remote3-rest-core-api.md) - Check for IR endpoints
- [ ] UC Developer Documentation - IR section
- [ ] UC Python Integration Library - IR support

### Architecture with Remote 3 IR

```
┌─────────────────────────────────────────────────────────────────┐
│                     Unfolded Circle Remote 3                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     Built-in IR Blaster                      │ │
│  │              (Line-of-sight, ~180° coverage)                 │ │
│  └──────────────────────────┬──────────────────────────────────┘ │
│                              │                                   │
│  ┌──────────────────────────┴──────────────────────────────────┐ │
│  │                     Remote 3 Firmware                        │ │
│  │              Handles IR sending/learning                     │ │
│  └──────────────────────────┬──────────────────────────────────┘ │
└─────────────────────────────┼───────────────────────────────────┘
                              │ WebSocket API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   OREI Integration (this project)                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                      IR Controller                           │ │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌────────────────┐ │ │
│  │  │ Remote 3 IR     │ │ Network Blaster │ │ BK-808 IR      │ │ │
│  │  │ Transport       │ │ Transport       │ │ Transport      │ │ │
│  │  │ (line-of-sight) │ │ (per-zone)      │ │ (if available) │ │ │
│  │  └─────────────────┘ └─────────────────┘ └────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Hybrid IR Strategy

We should support **multiple IR paths** that can be used together:

| IR Source | Best For | Limitations |
|-----------|----------|-------------|
| **Remote 3 IR** | Current room, direct control | Line-of-sight only |
| **Network Blasters** | Other rooms, automation | Requires hardware per zone |
| **BK-808 IR** (TBD) | Matrix-connected devices | May be limited/unavailable |

### Command Routing Logic

```python
async def send_device_command(zone_id: str, device_id: str, command: str):
    """
    Smart IR routing based on context.
    """
    zone = get_zone(zone_id)
    device = get_device(device_id)
    ir_code = device.get_command(command)
    
    # Priority 1: Zone-specific network blaster (most reliable)
    if zone.has_network_blaster:
        success = await zone.blaster.send(ir_code)
        if success:
            return True
    
    # Priority 2: BK-808 built-in IR (if available and applicable)
    if zone.matrix_output and bk808_has_ir:
        success = await bk808.send_ir(zone.matrix_output, ir_code)
        if success:
            return True
    
    # Priority 3: Remote 3 IR (fallback, requires line-of-sight)
    # Only if user is likely in the target zone
    if zone.is_current_location:
        success = await remote3.send_ir(ir_code)
        if success:
            return True
    
    return False
```

### Implementation Notes

1. **Remote 3 IR as "Transport"**: Implement `Remote3IRTransport` class following `IRTransport` interface

2. **Entity Mapping**: IR commands may need to be exposed as entity commands:
   - `media_player.living_room_tv` → POWER button sends IR

3. **Learning UI**: Web UI should have "Learn from Remote 3" option

4. **Code Storage**: Codes learned via Remote 3 stored in same format as network blaster codes

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Unfolded Circle Remote 3                     │
│                    (or Web UI / REST API)                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OREI Integration Driver                     │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │ Matrix Ctrl │  │ Scene Engine │  │     IR Controller       │ │
│  │  (existing) │  │  (existing)  │  │       (NEW)             │ │
│  └─────────────┘  └──────────────┘  └───────────┬─────────────┘ │
└─────────────────────────────────────────────────┼───────────────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    │                             │                             │
                    ▼                             ▼                             ▼
┌───────────────────────────┐  ┌───────────────────────────┐  ┌───────────────────────────┐
│   IR Transport Adapter    │  │   IR Transport Adapter    │  │   IR Transport Adapter    │
│   (Global Caché iTach)    │  │   (Broadlink RM4 Pro)     │  │   (USB-UIRT / Serial)     │
└─────────────┬─────────────┘  └─────────────┬─────────────┘  └─────────────┬─────────────┘
              │                              │                              │
              ▼                              ▼                              ▼
        ┌───────────┐                  ┌───────────┐                  ┌───────────┐
        │ IR Blaster│                  │ IR Blaster│                  │ IR Blaster│
        │ (Room 1)  │                  │ (Room 2)  │                  │ (Room 3)  │
        └───────────┘                  └───────────┘                  └───────────┘
              │                              │                              │
              ▼                              ▼                              ▼
        ┌───────────┐                  ┌───────────┐                  ┌───────────┐
        │    TV     │                  │    TV     │                  │ Projector │
        │  Receiver │                  │ Soundbar  │                  │  Receiver │
        └───────────┘                  └───────────┘                  └───────────┘
```

---

## IR Transport Layer

### Abstract Interface

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class IRFormat(Enum):
    """Supported IR code formats."""
    PRONTO_HEX = "pronto"       # Universal Pronto format
    RAW_TIMING = "raw"          # Raw timing data (microseconds)
    NEC = "nec"                 # NEC protocol (address + command)
    RC5 = "rc5"                 # Philips RC5
    RC6 = "rc6"                 # Philips RC6 (MCE)
    SONY_SIRC = "sony"          # Sony SIRC
    SAMSUNG = "samsung"         # Samsung protocol
    GLOBAL_CACHE = "gc"         # Global Caché sendir format


@dataclass
class IRCode:
    """Represents an IR command."""
    format: IRFormat
    data: str                   # The actual IR code data
    frequency: int = 38000      # Carrier frequency (Hz), typically 38kHz
    repeat: int = 1             # Number of times to send
    name: Optional[str] = None  # Human-readable name
    

class IRTransport(ABC):
    """Abstract base class for IR transmitter hardware."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this transport."""
        pass
    
    @property
    @abstractmethod
    def transport_type(self) -> str:
        """Type identifier (e.g., 'global_cache', 'broadlink')."""
        pass
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the IR transmitter."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the IR transmitter."""
        pass
    
    @abstractmethod
    async def send_ir(self, code: IRCode, port: int = 1) -> bool:
        """
        Send an IR command.
        
        :param code: The IR code to send
        :param port: Output port (for multi-port devices)
        :return: True if command was sent successfully
        """
        pass
    
    @abstractmethod
    async def learn_ir(self, timeout: float = 10.0) -> Optional[IRCode]:
        """
        Enter learning mode and capture an IR code.
        
        :param timeout: How long to wait for IR signal
        :return: Captured IR code, or None if timeout/error
        """
        pass
    
    @property
    @abstractmethod
    def supports_learning(self) -> bool:
        """Whether this transport supports IR learning."""
        pass
    
    @property
    @abstractmethod
    def num_ports(self) -> int:
        """Number of IR output ports."""
        pass
```

### Planned Transport Implementations

| Transport | Priority | Notes |
|-----------|----------|-------|
| **Global Caché iTach IP2IR** | P1 | Industry standard, very reliable |
| **Global Caché Flex** | P1 | Newer GC hardware |
| **Broadlink RM4 Pro** | P2 | Affordable, widely available |
| **Tuya IR Blaster** | P3 | Many brands, uses Tuya protocol |
| **USB-UIRT** | P3 | USB-based, needs host machine |
| **ESPHome IR** | P3 | DIY option via Home Assistant |
| **MQTT Generic** | P4 | For custom/DIY solutions |

### Global Caché Implementation Example

```python
class GlobalCacheTransport(IRTransport):
    """
    Global Caché iTach / Flex IR transmitter.
    
    Uses TCP connection on port 4998.
    Protocol: ASCII-based, e.g., "sendir,1:1,1,38000,1,69,..."
    """
    
    def __init__(self, host: str, port: int = 4998):
        self.host = host
        self.port = port
        self._reader = None
        self._writer = None
        self._connected = False
    
    @property
    def name(self) -> str:
        return f"Global Caché @ {self.host}"
    
    @property
    def transport_type(self) -> str:
        return "global_cache"
    
    async def connect(self) -> bool:
        try:
            self._reader, self._writer = await asyncio.open_connection(
                self.host, self.port
            )
            self._connected = True
            return True
        except Exception as e:
            _LOG.error("Failed to connect to Global Caché: %s", e)
            return False
    
    async def send_ir(self, code: IRCode, port: int = 1) -> bool:
        """
        Send IR using Global Caché sendir command.
        
        Format: sendir,<module>:<port>,<id>,<freq>,<repeat>,<offset>,<on1>,<off1>,...
        """
        if not self._connected:
            return False
        
        # Convert code to GC format if needed
        gc_data = self._to_gc_format(code)
        
        command = f"sendir,1:{port},1,{gc_data}\r"
        self._writer.write(command.encode())
        await self._writer.drain()
        
        # Wait for response
        response = await asyncio.wait_for(
            self._reader.readline(), 
            timeout=2.0
        )
        
        return response.startswith(b"completeir")
    
    async def learn_ir(self, timeout: float = 10.0) -> Optional[IRCode]:
        """Enter learning mode on Global Caché."""
        if not self._connected:
            return None
        
        # Send get_IRL command to start learning
        self._writer.write(b"get_IRL,1:1\r")
        await self._writer.drain()
        
        try:
            response = await asyncio.wait_for(
                self._reader.readline(),
                timeout=timeout
            )
            
            if response.startswith(b"IR Learner"):
                # Parse the learned code
                return self._parse_gc_learned(response)
        except asyncio.TimeoutError:
            return None
        
        return None
```

---

## Device Abstraction Layer

### Device Capabilities Model

Rather than modeling specific devices, we model **capabilities**:

```python
from enum import Enum, auto
from typing import Set

class DeviceCapability(Enum):
    """What a device can do."""
    POWER = auto()           # Power on/off/toggle
    POWER_DISCRETE = auto()  # Separate on and off commands
    VOLUME = auto()          # Volume up/down
    VOLUME_DISCRETE = auto() # Set specific volume level
    MUTE = auto()            # Mute toggle
    MUTE_DISCRETE = auto()   # Separate mute on/off
    INPUT_SELECT = auto()    # Change input source
    CHANNEL = auto()         # Channel up/down/direct
    NAVIGATION = auto()      # Arrow keys, OK, back, menu
    PLAYBACK = auto()        # Play, pause, stop, FF, RW
    COLOR_BUTTONS = auto()   # Red, green, yellow, blue
    NUMBER_PAD = auto()      # 0-9 digit entry
    

class DeviceType(Enum):
    """Categories of devices."""
    TV = "tv"
    PROJECTOR = "projector"
    RECEIVER = "receiver"
    SOUNDBAR = "soundbar"
    CABLE_BOX = "cable_box"
    STREAMING_BOX = "streaming_box"
    BLU_RAY = "blu_ray"
    GAME_CONSOLE = "game_console"
    GENERIC = "generic"


@dataclass
class DeviceProfile:
    """
    Defines a controllable device's IR capabilities.
    
    Designed to be serializable to/from JSON for sharing.
    """
    id: str                          # Unique identifier
    name: str                        # Display name
    manufacturer: str                # e.g., "Samsung", "LG"
    model: str                       # e.g., "UN65TU8000"
    device_type: DeviceType
    capabilities: Set[DeviceCapability]
    commands: dict[str, IRCode]      # Command name -> IR code
    
    # Optional metadata
    notes: str = ""
    contributor: str = ""            # Who created this profile
    verified: bool = False           # Community verified?
    
    def to_dict(self) -> dict:
        """Serialize for JSON storage."""
        return {
            "id": self.id,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "device_type": self.device_type.value,
            "capabilities": [c.name for c in self.capabilities],
            "commands": {
                name: {
                    "format": code.format.value,
                    "data": code.data,
                    "frequency": code.frequency,
                    "repeat": code.repeat,
                }
                for name, code in self.commands.items()
            },
            "notes": self.notes,
            "contributor": self.contributor,
            "verified": self.verified,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DeviceProfile":
        """Deserialize from JSON."""
        commands = {}
        for name, code_data in data.get("commands", {}).items():
            commands[name] = IRCode(
                format=IRFormat(code_data["format"]),
                data=code_data["data"],
                frequency=code_data.get("frequency", 38000),
                repeat=code_data.get("repeat", 1),
                name=name,
            )
        
        return cls(
            id=data["id"],
            name=data["name"],
            manufacturer=data.get("manufacturer", "Unknown"),
            model=data.get("model", "Unknown"),
            device_type=DeviceType(data.get("device_type", "generic")),
            capabilities={
                DeviceCapability[c] for c in data.get("capabilities", [])
            },
            commands=commands,
            notes=data.get("notes", ""),
            contributor=data.get("contributor", ""),
            verified=data.get("verified", False),
        )
```

### Standard Command Names

To ensure interoperability, we define standard command names:

```python
# Power commands
POWER_TOGGLE = "power_toggle"
POWER_ON = "power_on"
POWER_OFF = "power_off"

# Volume commands  
VOLUME_UP = "volume_up"
VOLUME_DOWN = "volume_down"
MUTE_TOGGLE = "mute_toggle"
MUTE_ON = "mute_on"
MUTE_OFF = "mute_off"

# Input commands (use input_hdmi1, input_hdmi2, etc.)
INPUT_HDMI1 = "input_hdmi1"
INPUT_HDMI2 = "input_hdmi2"
# ...

# Navigation
NAV_UP = "nav_up"
NAV_DOWN = "nav_down"
NAV_LEFT = "nav_left"
NAV_RIGHT = "nav_right"
NAV_OK = "nav_ok"
NAV_BACK = "nav_back"
NAV_MENU = "nav_menu"
NAV_HOME = "nav_home"

# Playback
PLAY = "play"
PAUSE = "pause"
STOP = "stop"
FAST_FORWARD = "fast_forward"
REWIND = "rewind"
SKIP_NEXT = "skip_next"
SKIP_PREV = "skip_prev"

# Channel
CHANNEL_UP = "channel_up"
CHANNEL_DOWN = "channel_down"

# Numbers
DIGIT_0 = "digit_0"
DIGIT_1 = "digit_1"
# ... through digit_9
```

---

## IR Code Management

### Code Sources

1. **Built-in Database**
   - Common devices with verified codes
   - Shipped with the integration
   - Updated via releases

2. **User-Learned Codes**
   - Captured via learning mode
   - Stored in user's config directory
   - Can be exported/shared

3. **Imported Codes**
   - Pronto Hex files (.ccf, .txt)
   - Global Caché database exports
   - LIRC database imports
   - JSON device profile imports

4. **Online Databases** (future)
   - Integration with community databases
   - IRDB (https://irdb.tk/)
   - Pronto Files database

### Code Storage Structure

```
config/
├── ir_devices/
│   ├── living_room_tv.json        # User's devices
│   ├── bedroom_receiver.json
│   └── custom/
│       └── weird_projector.json   # Learned/custom devices
├── ir_database/
│   ├── samsung_tv.json            # Built-in profiles
│   ├── lg_tv.json
│   ├── sony_tv.json
│   ├── denon_receiver.json
│   └── manifest.json              # Index of all profiles
└── ir_learned/
    └── raw_codes.json             # Unassigned learned codes
```

### Example Device Profile (JSON)

```json
{
  "id": "samsung_tu8000_series",
  "name": "Samsung TU8000 Series TV",
  "manufacturer": "Samsung",
  "model": "UN*TU8000*",
  "device_type": "tv",
  "capabilities": [
    "POWER",
    "VOLUME",
    "MUTE",
    "INPUT_SELECT",
    "NAVIGATION",
    "NUMBER_PAD"
  ],
  "commands": {
    "power_toggle": {
      "format": "pronto",
      "data": "0000 006D 0022 0003 00A9 00A8 0015 003F 0015 003F 0015 003F 0015 0015 0015 0015 0015 0015 0015 0015 0015 0015 0015 003F 0015 003F 0015 003F 0015 0015 0015 0015 0015 0015 0015 0015 0015 0015 0015 0015 0015 003F 0015 0015 0015 0015 0015 0015 0015 0015 0015 0015 0015 0015 0015 0040 0015 0015 0015 003F 0015 003F 0015 003F 0015 003F 0015 003F 0015 003F 0015 0702 00A9 00A8 0015 0015 0015 0E6E",
      "frequency": 38000,
      "repeat": 1
    },
    "volume_up": {
      "format": "samsung",
      "data": "07:07:07",
      "frequency": 38000
    },
    "volume_down": {
      "format": "samsung",
      "data": "07:07:0B",
      "frequency": 38000
    },
    "mute_toggle": {
      "format": "samsung",
      "data": "07:07:0F",
      "frequency": 38000
    },
    "input_hdmi1": {
      "format": "pronto",
      "data": "...",
      "frequency": 38000
    }
  },
  "notes": "Works for all 2020 Samsung TU8000 series. Some commands may vary for older models.",
  "contributor": "community",
  "verified": true
}
```

---

## Room/Zone Management

### Concept

A **Zone** represents a physical location with:
- One or more IR transmitters (same or different)
- One or more controllable devices
- Association with matrix outputs

```python
@dataclass
class IRZone:
    """A physical zone with IR-controllable devices."""
    
    id: str                              # Unique identifier
    name: str                            # "Living Room", "Master Bedroom"
    
    # IR transmitter(s) for this zone
    transmitters: list[ZoneTransmitter]  # May have multiple for coverage
    
    # Devices in this zone
    devices: list[ZoneDevice]
    
    # Link to matrix output (optional)
    matrix_output: Optional[int] = None  # Output 1-8 on OREI
    

@dataclass
class ZoneTransmitter:
    """An IR transmitter assigned to a zone."""
    
    transport_id: str        # References an IRTransport instance
    port: int = 1            # Which port on multi-port devices
    description: str = ""    # "Behind TV", "Ceiling mounted"
    

@dataclass  
class ZoneDevice:
    """A device within a zone."""
    
    id: str                  # Unique device instance ID
    profile_id: str          # References a DeviceProfile
    transmitter_id: str      # Which transmitter controls this device
    transmitter_port: int    # Which port on that transmitter
    
    # Optional device-specific overrides
    custom_commands: dict[str, IRCode] = field(default_factory=dict)
    
    # State tracking (IR is one-way, so we track assumed state)
    assumed_power: Optional[bool] = None
    assumed_input: Optional[str] = None
    assumed_mute: Optional[bool] = None
```

### Zone Configuration Example

```json
{
  "zones": [
    {
      "id": "living_room",
      "name": "Living Room",
      "matrix_output": 1,
      "transmitters": [
        {
          "transport_id": "gc_main",
          "port": 1,
          "description": "Behind entertainment center"
        }
      ],
      "devices": [
        {
          "id": "living_room_tv",
          "profile_id": "samsung_tu8000_series",
          "transmitter_id": "gc_main",
          "transmitter_port": 1
        },
        {
          "id": "living_room_receiver",
          "profile_id": "denon_avr_x3700h",
          "transmitter_id": "gc_main",
          "transmitter_port": 1
        }
      ]
    },
    {
      "id": "master_bedroom",
      "name": "Master Bedroom",
      "matrix_output": 2,
      "transmitters": [
        {
          "transport_id": "broadlink_bedroom",
          "port": 1,
          "description": "On nightstand"
        }
      ],
      "devices": [
        {
          "id": "bedroom_tv",
          "profile_id": "lg_oled_cx",
          "transmitter_id": "broadlink_bedroom",
          "transmitter_port": 1
        }
      ]
    }
  ]
}
```

---

## Integration Points

### 1. Scene Integration

Extend existing scenes to include IR actions:

```python
@dataclass
class SceneIRAction:
    """IR command to execute as part of a scene."""
    
    zone_id: str             # Which zone
    device_id: str           # Which device in zone
    command: str             # Command name (e.g., "power_on")
    delay_ms: int = 0        # Delay before this command
    condition: Optional[str] = None  # e.g., "if_power_off"


@dataclass
class EnhancedScene:
    """Scene with matrix routing AND IR actions."""
    
    id: str
    name: str
    
    # Matrix routing (existing)
    outputs: dict[int, SceneOutput]
    
    # IR actions (new)
    ir_actions: list[SceneIRAction] = field(default_factory=list)
    
    # Execution order
    ir_before_matrix: bool = False  # Run IR before or after matrix switch
```

**Example Scene: "Movie Night"**
```json
{
  "id": "movie_night",
  "name": "Movie Night",
  "outputs": {
    "1": {"input": 3, "enabled": true},
    "2": {"input": 3, "enabled": false}
  },
  "ir_actions": [
    {"zone_id": "living_room", "device_id": "living_room_tv", "command": "power_on", "delay_ms": 0},
    {"zone_id": "living_room", "device_id": "living_room_receiver", "command": "power_on", "delay_ms": 500},
    {"zone_id": "living_room", "device_id": "living_room_receiver", "command": "input_hdmi1", "delay_ms": 2000}
  ],
  "ir_before_matrix": false
}
```

### 2. REST API Extensions

```
# Zone Management
GET    /api/ir/zones                    # List all zones
POST   /api/ir/zones                    # Create zone
GET    /api/ir/zones/{zone_id}          # Get zone details
PUT    /api/ir/zones/{zone_id}          # Update zone
DELETE /api/ir/zones/{zone_id}          # Delete zone

# Transport Management  
GET    /api/ir/transports               # List IR transmitters
POST   /api/ir/transports               # Add transmitter
GET    /api/ir/transports/{id}/test     # Test transmitter connection
DELETE /api/ir/transports/{id}          # Remove transmitter

# Device Profiles
GET    /api/ir/profiles                 # List available device profiles
GET    /api/ir/profiles/{id}            # Get profile details
POST   /api/ir/profiles                 # Create custom profile
PUT    /api/ir/profiles/{id}            # Update profile
POST   /api/ir/profiles/import          # Import from file

# Device Instances
GET    /api/ir/devices                  # List all configured devices
POST   /api/ir/devices                  # Add device to zone
DELETE /api/ir/devices/{id}             # Remove device

# Command Execution
POST   /api/ir/send                     # Send IR command
{
  "zone_id": "living_room",
  "device_id": "living_room_tv",
  "command": "power_toggle"
}

POST   /api/ir/send/raw                 # Send raw IR code
{
  "transport_id": "gc_main",
  "port": 1,
  "code": {
    "format": "pronto",
    "data": "0000 006D ..."
  }
}

# Learning
POST   /api/ir/learn                    # Start learning mode
{
  "transport_id": "gc_main",
  "timeout": 10
}

GET    /api/ir/learn/{session_id}       # Check learning result
```

### 3. Unfolded Circle Integration

Expose IR devices as UC entities:

```python
# New entity types for IR-controlled devices

class IRDeviceEntity:
    """Represents an IR device as a UC entity."""
    
    def __init__(self, zone_device: ZoneDevice, profile: DeviceProfile):
        self.zone_device = zone_device
        self.profile = profile
    
    def get_entity_definition(self) -> dict:
        """Generate UC entity definition."""
        features = []
        
        if DeviceCapability.POWER in self.profile.capabilities:
            features.append("on_off")
        if DeviceCapability.VOLUME in self.profile.capabilities:
            features.append("volume")
        if DeviceCapability.MUTE in self.profile.capabilities:
            features.append("mute")
        
        return {
            "entity_id": f"ir_{self.zone_device.id}",
            "entity_type": "media_player",
            "name": {
                "en": self.profile.name
            },
            "features": features,
        }
```

---

## Implementation Phases

### Phase 1: Foundation (4-6 weeks)

**Goal**: Basic IR sending capability with one transport type

- [ ] Define IR abstractions (`IRCode`, `IRTransport`, `IRFormat`)
- [ ] Implement Global Caché transport (most reliable)
- [ ] Basic REST API for sending raw IR codes
- [ ] Configuration storage for transports
- [ ] Unit tests with mock transport

**Deliverables**:
- Can send IR commands via Global Caché
- REST endpoint: `POST /api/ir/send/raw`
- Transport configuration persists

### Phase 2: Device Profiles (3-4 weeks)

**Goal**: Device abstraction and code database

- [ ] Device profile data model
- [ ] JSON profile loader/saver  
- [ ] Built-in profiles for common devices (10-20)
- [ ] Profile management REST API
- [ ] Web UI for browsing profiles

**Deliverables**:
- Can select "Samsung TV" and send "power_on"
- Initial device profile library
- Profile editor in Web UI

### Phase 3: Zone Management (3-4 weeks)

**Goal**: Multi-room organization

- [ ] Zone data model
- [ ] Zone configuration REST API
- [ ] Device-to-zone assignment
- [ ] Zone management Web UI
- [ ] Link zones to matrix outputs

**Deliverables**:
- Configure which devices are in which rooms
- Associate IR zones with matrix outputs
- Zone overview in Web UI

### Phase 4: Scene Integration (2-3 weeks)

**Goal**: Unified scene control

- [ ] Extend Scene model with IR actions
- [ ] Scene execution engine with IR
- [ ] Delay/sequencing support
- [ ] Scene editor with IR actions
- [ ] Activity support (macros)

**Deliverables**:
- Scenes can power on TV, switch input, etc.
- Web UI for adding IR actions to scenes

### Phase 5: Learning Mode (2-3 weeks)

**Goal**: Learn IR codes from remotes

- [ ] IR learning protocol per transport
- [ ] Learning session management
- [ ] Web UI learning wizard
- [ ] Code validation/testing
- [ ] Export learned codes

**Deliverables**:
- Point remote at blaster, capture code
- Assign captured code to device profile
- Export/share learned codes

### Phase 6: Additional Transports (ongoing)

**Goal**: Support more IR hardware

- [ ] Broadlink RM4 Pro transport
- [ ] USB-UIRT transport  
- [ ] Tuya/Smart Life transport
- [ ] ESPHome via Home Assistant
- [ ] MQTT generic transport

**Deliverables**:
- Support for 3+ transport types
- Auto-discovery where possible

### Phase 7: Advanced Features (future)

- [ ] State tracking and feedback simulation
- [ ] Macro/activity support
- [ ] IR code import (Pronto files, LIRC)
- [ ] Online database integration
- [ ] Diagnostic tools (IR signal analysis)
- [ ] Scheduling (turn off all TVs at midnight)

---

## Technical Challenges

### 1. One-Way Communication

**Problem**: IR is fire-and-forget. No acknowledgment that the device received the command.

**Mitigations**:
- **State Tracking**: Track assumed state based on commands sent
- **Retry Logic**: Send critical commands multiple times
- **Power Queries**: For devices with discrete on/off, can infer state
- **CEC Polling**: Use HDMI CEC for power state where available

### 2. Timing and Collision

**Problem**: Sending IR commands too quickly can cause missed commands or interference.

**Mitigations**:
- **Command Queue**: Queue commands with configurable gaps
- **Per-Zone Queues**: Different zones can send simultaneously
- **Minimum Gap**: Enforce 100-300ms between commands to same zone
- **Priority System**: Power commands get priority over volume

```python
class IRCommandQueue:
    """Manages IR command timing to prevent collisions."""
    
    MIN_GAP_MS = 150  # Minimum gap between commands
    
    async def queue_command(
        self, 
        zone_id: str, 
        code: IRCode, 
        priority: int = 0
    ) -> asyncio.Future:
        """Queue a command for execution."""
        pass
```

### 3. IR Code Compatibility

**Problem**: Same device can have different IR codes by region, year, or variant.

**Mitigations**:
- **Learning Mode**: Always allow learning device-specific codes
- **Profile Variants**: Support regional/year variants in profiles
- **Fuzzy Matching**: Model patterns like "Samsung TV 2018-2022"
- **Community Verification**: Mark profiles as verified/unverified

### 4. Multi-Device Zones

**Problem**: One IR blaster might control multiple devices (TV + receiver in same line of sight).

**Mitigations**:
- **Device-Specific Codes**: Use manufacturer-specific protocols
- **Multiple Blasters**: Support multiple transmitters per zone
- **Directional Blasters**: Document blaster placement
- **IR Sticky Cables**: Single-device IR emitters that attach to device

### 5. Network Reliability

**Problem**: Network-connected IR blasters can go offline.

**Mitigations**:
- **Health Checks**: Periodic connectivity tests
- **Reconnection Logic**: Automatic reconnect on failure
- **Command Buffering**: Buffer commands during brief outages
- **Status Reporting**: Surface transport status in UI

---

## Hardware Recommendations

### Recommended: Global Caché iTach Flex

**Pros**:
- Industry standard, very reliable
- Excellent learning capability
- Multiple port options (1, 3 ports)
- Power over Ethernet (PoE) option
- Well-documented protocol

**Cons**:
- Higher cost (~$100-200)
- Requires wired ethernet

**Best for**: Primary/critical zones, professional installations

### Budget Option: Broadlink RM4 Pro

**Pros**:
- Affordable (~$40-60)
- WiFi connected
- Also supports RF 433MHz
- Good mobile app for testing

**Cons**:
- Cloud-dependent setup (can work locally after)
- Reliability slightly lower than GC
- Protocol reverse-engineered

**Best for**: Secondary rooms, budget installations

### DIY Option: ESP32 + IR LED

**Pros**:
- Very cheap (~$10-15)
- Fully customizable
- ESPHome integration
- No cloud dependencies

**Cons**:
- Requires DIY skills
- Assembly required
- Limited range without amplifier

**Best for**: Makers, additional zones, experimentation

### Comparison Matrix

| Feature | Global Caché | Broadlink RM4 | ESP32 DIY |
|---------|--------------|---------------|-----------|
| Cost | $$$ | $$ | $ |
| Reliability | ★★★★★ | ★★★☆☆ | ★★★★☆ |
| Setup Ease | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |
| Learning | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| Multi-port | Yes (up to 3) | No | DIY |
| Protocol | Open | Proprietary | Open |
| PoE | Optional | No | DIY |

---

## API Version Planning

These features would be released across API versions:

| Version | Features |
|---------|----------|
| 2.9.0 | IR Transport framework, Global Caché support |
| 2.10.0 | Device profiles, profile database |
| 2.11.0 | Zone management, zone-output linking |
| 2.12.0 | Scene integration with IR actions |
| 2.13.0 | Learning mode |
| 3.0.0 | Full IR ecosystem (breaking changes if needed) |

---

## Open Questions

1. ~~**BK-808 IR Passthrough**: Does the OREI BK-808 have IR passthrough on HDMI? Worth investigating.~~ → **Moved to BLOCKER 2**

2. ~~**UC Remote 3 IR**: The Remote 3 has built-in IR. Should we integrate with that, or focus on network IR blasters?~~ → **YES - See Remote 3 Integration section**

3. **CEC Integration**: Should CEC commands be part of this IR system, or separate?

4. **Activity vs Scene**: Should "Activities" (multi-step macros with feedback) be distinct from "Scenes"?

5. **Database Hosting**: Should we host a community device profile database?

---

## Next Steps

> ⚠️ **BLOCKED**: The following steps cannot proceed until blockers are resolved.

### Pre-Development (Resolve Blockers)

1. **🔴 BLOCKER 1**: Inventory existing IR hardware
   - List all IR blasters/extenders currently owned
   - Note make/model/location of each
   - Test connectivity and functionality

2. **🔴 BLOCKER 2**: Investigate BK-808 IR capabilities
   - Review manual and control drivers
   - Physical inspection of IR ports
   - API exploration for IR endpoints
   - Document findings

3. **🟡 BLOCKER 3**: Research Remote 3 IR API
   - Review UC WebSocket integration docs
   - Check for IR send/learn capabilities
   - Prototype simple IR send test

### Post-Blocker Resolution

4. **Select Primary IR Architecture**
   - Based on blocker findings, decide:
     - BK-808 IR primary? Secondary? Not used?
     - Remote 3 IR primary? Fallback only?
     - Network blasters needed? Which rooms?

5. **Prototype Phase 1**
   - Build basic IR transport for selected hardware
   - Test with simple device (TV power toggle)

6. **Define MVP Scope**
   - Minimal viable feature set
   - Which zones/devices for initial release

---

## References

- [Global Caché API Documentation](https://www.globalcache.com/files/docs/API-GC-100.pdf)
- [Broadlink Python Library](https://github.com/mjg59/python-broadlink)
- [IRDB - IR Code Database](https://irdb.tk/)
- [Pronto Hex Format](http://www.remotecentral.com/features/irdisp2.htm)
- [LIRC - Linux Infrared Remote Control](https://www.lirc.org/)
- [ESPHome IR Component](https://esphome.io/components/remote_transmitter.html)

---

*Document Version: 1.1*  
*Last Updated: January 20, 2026*  
*Author: Integration Development Team*

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-20 | Added BLOCKERS section, Remote 3 IR integration details |
| 1.0 | 2026-01-20 | Initial roadmap document |
