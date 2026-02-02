# CEC Control Architecture & Implementation Plan

## Overview

This document outlines the comprehensive CEC control system for the OREI Matrix Web UI, including the floating CEC tray, macros, profiles, and control zones. The implementation is designed to be modular and scalable, starting simple and building toward advanced features.

### Terminology

| Term | Definition | Current Code Name | Target Code Name |
|------|------------|-------------------|------------------|
| **CEC Tray** | Floating remote control with auto-detection | `cec-tray.js` | (no change) |
| **CEC Macro** | Saved sequence of CEC commands (power on/off sequences) | (not implemented) | `cec_macros.json` |
| **Profile** | Complete configuration: routing + output settings + CEC pinning + macros | `Scene` ⚠️ | `Profile` |
| **Control Zone** | Groups profiles for input/output sections; optional advanced layer | (not implemented) | `ControlZone` |
| **CEC Pinning** | Assigning specific CEC commands to specific devices | `CecConfig` | (no change) |

### Terminology Migration Status: ✅ COMPLETED (v2.10.0)

The codebase has been migrated from "Scene" to "Profile" terminology with full backward compatibility:

**Completed Changes:**
- ✅ `src/config.py`: Added `Profile`, `ProfileOutput` (alias), `ProfileManager` classes
- ✅ `src/config.py`: Auto-migration from `scenes.json` → `profiles.json` on first load
- ✅ `src/rest_api.py`: Added `/api/profiles/*` endpoints (primary API)
- ✅ `src/rest_api.py`: Kept `/api/scenes/*` endpoints for backward compatibility
- ✅ `web/js/api.js`: Added Profile API methods
- ✅ `web/js/state.js`: Added `profiles`, `activeProfile` with backward compatibility
- ✅ `web/index.html`: Updated UI labels to "Profiles"
- ✅ `web/js/components/scenes-panel.js`: Updated user-facing labels to "Profile"

**Backward Compatibility:**
- Scene API endpoints (`/api/scenes/*`) remain functional
- `SceneManager` class still exists with backward-compatible methods
- `state.scenes` and `state.activeScene` still work alongside new properties
- Existing `scenes.json` data automatically migrates to `profiles.json`

**Enhanced Profile Features:**
- Icon support (emoji/text display)
- Macro assignments (list of macro IDs)
- Power-on macro (auto-execute when profile recalled)
- Power-off macro (for future use)

---

## Table of Contents

1. [Architecture Layers](#architecture-layers)
2. [Detailed Requirements](#detailed-requirements)
3. [CEC Floating Tray](#cec-floating-tray)
4. [CEC Macros](#cec-macros)
5. [Profiles](#profiles)
6. [Control Zones](#control-zones)
7. [UI Organization](#ui-organization)
8. [Storage Structure](#storage-structure)
9. [Implementation Phases](#implementation-phases)
10. [API Endpoints](#api-endpoints)
11. [Code Structure](#code-structure)

---

## Detailed Requirements

> **Note:** This section captures the detailed requirements discussed during planning. These are the authoritative specifications for each feature.

### CEC Floating Tray Requirements

| Requirement | Description |
|-------------|-------------|
| **Auto-detection** | Automatically detect CEC targets based on currently configured input routing |
| **Fallback prompt** | If auto-detection isn't possible, prompt user to select input device to pin |
| **On-demand switching** | Simple way to select input device on-the-fly |
| **Profile-specific pinning** | Support scene/profile-specific CEC pinning that overrides auto-detection |
| **Output precedence** | Output pinning gives precedence to pinned scenes or defined configuration states |
| **Device names** | Display device names (input name = device name) for clarity |
| **Multi-profile support** | When multiple profiles/zones are active, allow user to select which one to control |
| **Expanded pinning** | On larger tablets, allow pinning the opened/expanded state |
| **Dynamic detection** | When pinned expanded, dynamically detect which CEC controls are needed based on active profile/zone |
| **Button group pinning** | Different button groups target different devices (e.g., Nav→Input, Volume→Output) |

#### Button Group Targeting (Core Concept)

Each CEC button group can be pinned to a different device:

| Button Group | Default Target | Example |
|--------------|----------------|---------|
| 🎮 Navigation (D-pad, Menu, Back) | Active input device | Apple TV on Input 1 |
| ⏯️ Playback (Play, Pause, Stop) | Active input device | Apple TV on Input 1 |
| 🔊 Volume (Up, Down, Mute) | Configured output device | Soundbar on Output 2 |
| 🔌 Power On/Off | Configurable (input, output, or both) | TV + Soundbar + Apple TV |

### CEC Macros Requirements

| Requirement | Description |
|-------------|-------------|
| **Standalone operation** | Macros work independently, outside of zone/profile context |
| **Profile assignment** | Macros can be assigned to profiles for quick access |
| **Power sequences** | Primary use case is power-on/power-off sequences across multiple devices |
| **Delays** | Support configurable delays between commands |
| **Execution sources** | Executable from UI, from profiles (quick-access buttons), or via API |

### Profile Requirements

| Requirement | Description |
|-------------|-------------|
| **Standalone operation** | Profiles work without Control Zones enabled |
| **Complete configuration** | Profiles include: routing, output settings, input settings, CEC pinning, assigned macros |
| **Output settings scope** | Per-output: HDR mode, HDCP mode, Scaler, ARC enable, Audio mute, Video enable |
| **CEC auto-detection** | Auto-detect CEC targets from routing if not explicitly pinned |
| **Activation** | Can be activated/deactivated on demand |
| **Consistency** | Defined states remain consistent unless explicitly changed |
| **Flexibility** | User can have multiple profiles configured for different use cases |

### Control Zone Requirements

| Requirement | Description |
|-------------|-------------|
| **Optional feature** | Control Zones are optional - users can use Profiles directly by default |
| **Enable toggle** | User must enable Control Zones feature to use them |
| **Profile grouping** | Zones assign profiles to Input Section and Output Section |
| **Multiple active** | Multiple zones can be active simultaneously |
| **Conflict detection** | System must detect and prompt user about conflicting settings between active zones |
| **Conflict resolution** | User should be prompted that a zone with conflicting settings will be disabled |
| **Independence** | Different zones operate on different outputs (e.g., Living Room on 1-2, Bedroom on 3) |

### UI Organization Requirements

| Requirement | Description |
|-------------|-------------|
| **Mobile optimization** | Core tabs + overflow menu + floating action button |
| **Desktop full access** | Full tab bar + pinned CEC panel option |
| **Overflow menu** | "More" (⋯) button for less-used tabs |
| **Slide-up reveal** | Bottom menu slides up to expose additional buttons |
| **Customizable tabs** | User can drag-and-drop or define which tabs are visible vs in overflow |
| **Adaptive screen** | If screen large enough, "More" button not visible (all tabs fit) |
| **Adaptive learning** | Track frequently-used tabs and promote them to visible area |
| **Debug location** | Debug console accessed from Settings menu, persists when opened until X clicked |
| **FAB positioning** | Customizable position (bottom-right, bottom-left, or hidden) |
| **Pinned expanded** | On larger screens, CEC tray can be pinned in expanded state |
| **Multi-profile selector** | When multiple profiles/zones active, tray shows selector to choose which to control |

### Current User Setup (Reference)

> This reflects the user's actual configuration and informs our default behaviors:

- **Output 1**: TV - video output, ARC/eARC intentionally disabled
- **Output 2**: Soundbar - audio only (video disabled), receives audio
- **Use case**: Separate video and audio paths for optimal quality

---

## Architecture Layers

The CEC control system is built in layers, each functional independently but integrating when combined:

```
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 3: CONTROL ZONES (Optional Advanced Layer)                   │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ Zone: "Living Room"                                            │ │
│  │   ├── Input Section  → Assigned Profile (e.g., "Streaming")   │ │
│  │   └── Output Section → Assigned Profile (e.g., "Surround")    │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  • Multiple zones can be active simultaneously                      │
│  • Conflict detection prompts user when settings overlap            │
│  • Zones group logical input/output combinations                    │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
                              │ (optional assignment)
                              │
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 2: PROFILES (Core Feature - works standalone)                │
│  ┌─────────────────────────┐  ┌─────────────────────────┐          │
│  │ "Movie Mode"            │  │ "Gaming Mode"           │          │
│  │ ├── Routing config      │  │ ├── Routing config      │          │
│  │ ├── Output settings     │  │ ├── Output settings     │          │
│  │ │   ├── HDR mode        │  │ │   ├── HDR mode        │          │
│  │ │   ├── HDCP mode       │  │ │   ├── HDCP mode       │          │
│  │ │   ├── Scaler          │  │ │   ├── Scaler          │          │
│  │ │   ├── ARC enable      │  │ │   ├── ARC enable      │          │
│  │ │   ├── Audio mute      │  │ │   ├── Audio mute      │          │
│  │ │   └── Video enable    │  │ │   └── Video enable    │          │
│  │ ├── CEC pinning         │  │ ├── CEC pinning         │          │
│  │ │   ├── Nav target      │  │ │   ├── Nav target      │          │
│  │ │   ├── Volume target   │  │ │   ├── Volume target   │          │
│  │ │   └── Power targets   │  │ │   └── Power targets   │          │
│  │ └── Assigned macros     │  │ └── Assigned macros     │          │
│  └─────────────────────────┘  └─────────────────────────┘          │
│  • Profiles work standalone without zones                           │
│  • Auto-detect CEC targets from routing if not explicitly pinned    │
│  • Can be activated/deactivated on demand                           │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
                              │ (can be assigned to profiles)
                              │
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 1: CEC MACROS (Foundation - works standalone)                │
│  ┌─────────────────────────┐  ┌─────────────────────────┐          │
│  │ "Power On Theater"      │  │ "All Devices Off"       │          │
│  │ ├── Power on Input 1    │  │ ├── Power off Output 1  │          │
│  │ ├── Power on Output 1   │  │ ├── Power off Output 2  │          │
│  │ ├── Power on Output 2   │  │ ├── Power off Input 1   │          │
│  │ └── (delay: 500ms)      │  │ └── Power off Input 2   │          │
│  └─────────────────────────┘  └─────────────────────────┘          │
│  • Macros are reusable command sequences                            │
│  • Can include delays between commands                              │
│  • Executable from UI, profiles, or API                             │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────────┐
│  FOUNDATION: CEC FLOATING TRAY (Always Available)                   │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ 🎮 Unified CEC Remote                                         │ │
│  │ ├── Power: On/Off (targets auto-detected or pinned)          │ │
│  │ ├── Navigation: D-pad, Menu, Back (→ active input device)    │ │
│  │ ├── Playback: Play/Pause/Stop/etc (→ active input device)    │ │
│  │ └── Volume: Up/Down/Mute (→ configured output device)        │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  • Floating button, expandable to full remote                       │
│  • Auto-detects targets from current routing                        │
│  • Shows device names for clarity                                   │
│  • Pinnable to different screen positions                           │
│  • On larger screens, can be pinned in expanded state               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## CEC Floating Tray

### Concept

A floating action button (FAB) that expands into a unified CEC remote control. The tray intelligently targets devices based on current routing, active profile, or user selection.

### Behavior

#### Default (Auto-Detection)
1. **Navigation/Playback controls** → Target the input device routed to the "primary" output
2. **Volume controls** → Target the output device configured for audio (e.g., soundbar on Output 2)
3. **Power controls** → Target both input and relevant outputs

#### With Profile Active
- Use CEC pinning from the active profile
- If multiple profiles active, show selector in tray header

#### Manual Override
- User can tap device name to select different target on-the-fly
- Override persists for session or until profile change

### UI States

```
┌─────────────────────────────────────────────────────────────────┐
│  COLLAPSED STATE (FAB)                                          │
│                                                                  │
│                                                    ┌────┐       │
│                                                    │ 🎮 │       │
│                                                    └────┘       │
│                                                                  │
│  • Shows as floating button                                      │
│  • Position: bottom-right (default), customizable                │
│  • Tap to expand                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  EXPANDED STATE (Mobile)                                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ CEC Remote                                            ✕   │  │
│  │ ─────────────────────────────────────────────────────────│  │
│  │ Nav: Apple TV (Input 1)        Vol: Soundbar (Output 2)  │  │
│  │ ─────────────────────────────────────────────────────────│  │
│  │                                                           │  │
│  │  [POWER ON]  [POWER OFF]                                 │  │
│  │                                                           │  │
│  │           [▲]                      [🔊+]                 │  │
│  │      [◀] [OK] [▶]                  [🔇]                  │  │
│  │           [▼]                      [🔊−]                 │  │
│  │                                                           │  │
│  │  [⏮] [⏪] [▶] [⏸] [⏹] [⏩] [⏭]                          │  │
│  │                                                           │  │
│  │  [MENU]  [BACK]                                          │  │
│  │ ─────────────────────────────────────────────────────────│  │
│  │ Macros: [Movie Night ▶] [All Off ▶]                      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PINNED EXPANDED STATE (Tablet/Desktop)                          │
│                                                                  │
│  ┌─────────────────────┐  ┌───────────────────────────────────┐ │
│  │                     │  │ CEC Remote              ⚙️  📌   │ │
│  │                     │  │ ───────────────────────────────── │ │
│  │    Matrix Grid      │  │ Active: Movie Mode Profile        │ │
│  │    or other         │  │ Nav: Apple TV    Vol: Soundbar    │ │
│  │    content          │  │ ───────────────────────────────── │ │
│  │                     │  │                                   │ │
│  │                     │  │  [Power]  [D-Pad]  [Volume]       │ │
│  │                     │  │  [Playback Controls]              │ │
│  │                     │  │  [Macros]                         │ │
│  └─────────────────────┘  └───────────────────────────────────┘ │
│                                                                  │
│  • Can be pinned to side panel                                   │
│  • Stays expanded while pinned                                   │
│  • Updates dynamically with routing changes                      │
└─────────────────────────────────────────────────────────────────┘
```

### Pinning Options

Users can customize the tray position:

| Position | Description |
|----------|-------------|
| `bottom-right` | Default FAB position |
| `bottom-left` | Alternative FAB position |
| `top-right` | Near settings area |
| `panel-right` | Pinned expanded panel (tablet/desktop) |
| `panel-left` | Pinned expanded panel (tablet/desktop) |
| `hidden` | Access only from menu |

### Device Target Display

The tray header shows current targets with device names:

```
Nav: Apple TV (Input 1)  |  Vol: Soundbar (Output 2)
     ↑ tap to change          ↑ tap to change
```

Tapping a device name shows a dropdown to select different device:

```
┌─────────────────────────┐
│ Select Navigation Target│
│ ────────────────────────│
│ ● Apple TV (Input 1)    │  ← Current
│ ○ PS5 (Input 2)         │
│ ○ Cable Box (Input 3)   │
│ ○ Chromecast (Input 4)  │
│ ────────────────────────│
│ ○ Auto-detect           │
└─────────────────────────┘
```

---

## CEC Macros

### Concept

CEC Macros are saved sequences of CEC commands that can be executed with a single tap. They're the building blocks for automation.

### Data Structure

```typescript
interface CECMacro {
  id: string;                    // Unique identifier
  name: string;                  // Display name
  icon?: string;                 // Optional emoji/icon
  description?: string;          // Optional description
  commands: CECCommand[];        // Ordered list of commands
  createdAt: string;             // ISO timestamp
  updatedAt: string;             // ISO timestamp
}

interface CECCommand {
  type: 'input' | 'output';      // Target type
  port: number;                  // Port 1-8
  command: string;               // Command name (power_on, power_off, etc.)
  delay?: number;                // Delay AFTER this command (ms)
}
```

### Example Macros

```json
{
  "id": "macro_movie_night",
  "name": "Movie Night",
  "icon": "🎬",
  "description": "Power on TV, soundbar, and Apple TV",
  "commands": [
    { "type": "output", "port": 1, "command": "power_on" },
    { "type": "output", "port": 2, "command": "power_on", "delay": 1000 },
    { "type": "input", "port": 1, "command": "power_on", "delay": 500 }
  ]
}
```

```json
{
  "id": "macro_all_off",
  "name": "All Off",
  "icon": "🔌",
  "description": "Power off all connected devices",
  "commands": [
    { "type": "output", "port": 1, "command": "power_off" },
    { "type": "output", "port": 2, "command": "power_off" },
    { "type": "input", "port": 1, "command": "power_off" },
    { "type": "input", "port": 2, "command": "power_off" }
  ]
}
```

### Macro Editor UI

```
┌─────────────────────────────────────────────────────────────────┐
│ Create CEC Macro                                          ✕     │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│ Name: [Movie Night________________]                              │
│ Icon: [🎬 ▼]                                                    │
│ Description: [Power on theater devices______________]           │
│                                                                  │
│ Commands:                                                        │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 1. [Output ▼] [1 - Living Room TV ▼] [Power On ▼] [⋮]      │ │
│ │    └─ Delay after: [0___] ms                                │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ 2. [Output ▼] [2 - Soundbar ▼] [Power On ▼] [⋮]            │ │
│ │    └─ Delay after: [1000_] ms                               │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ 3. [Input ▼] [1 - Apple TV ▼] [Power On ▼] [⋮]             │ │
│ │    └─ Delay after: [500__] ms                               │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ [+ Add Command]                                                  │
│                                                                  │
│ ─────────────────────────────────────────────────────────────── │
│ [Test Macro]                    [Cancel]  [Save Macro]          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Profiles

### Concept

Profiles save a complete configuration state including routing, output settings, and CEC control pinning. Profiles can be activated standalone or assigned to Control Zones.

### Data Structure

```typescript
interface Profile {
  id: string;                    // Unique identifier
  name: string;                  // Display name
  icon?: string;                 // Optional emoji/icon
  description?: string;          // Optional description
  
  // Routing configuration
  routing?: {
    [outputNum: number]: number; // output -> input mapping
  };
  
  // Output settings
  outputSettings?: {
    [outputNum: number]: OutputSettings;
  };
  
  // CEC control pinning
  cecPinning: {
    navigation: CECTarget;       // D-pad, menu, back
    playback: CECTarget;         // Play, pause, stop, etc.
    volume: CECTarget;           // Volume up/down, mute
    power: CECPowerTargets;      // Power on/off targets
  };
  
  // Associated macros (quick access in tray)
  macros?: string[];             // Macro IDs
  
  // Metadata
  isActive?: boolean;            // Currently active
  createdAt: string;
  updatedAt: string;
}

interface OutputSettings {
  enabled?: boolean;             // Video output enabled
  audioMuted?: boolean;          // Audio muted
  arcEnabled?: boolean;          // ARC enabled
  hdrMode?: number;              // HDR mode (0-4)
  hdcpMode?: number;             // HDCP mode (0-3)
  scalerMode?: number;           // Scaler mode (1-6)
}

interface CECTarget {
  type: 'auto' | 'input' | 'output';
  port?: number;                 // Required if type != 'auto'
}

interface CECPowerTargets {
  inputs: number[];              // Input ports to control
  outputs: number[];             // Output ports to control
}
```

### Example Profile

```json
{
  "id": "profile_movie_mode",
  "name": "Movie Mode",
  "icon": "🎬",
  "description": "TV + Soundbar with Apple TV",
  
  "routing": {
    "1": 1,
    "2": 1
  },
  
  "outputSettings": {
    "1": {
      "enabled": true,
      "audioMuted": true,
      "arcEnabled": false,
      "hdrMode": 0
    },
    "2": {
      "enabled": true,
      "audioMuted": false,
      "arcEnabled": true,
      "hdrMode": 0
    }
  },
  
  "cecPinning": {
    "navigation": { "type": "auto" },
    "playback": { "type": "auto" },
    "volume": { "type": "output", "port": 2 },
    "power": {
      "inputs": [1],
      "outputs": [1, 2]
    }
  },
  
  "macros": ["macro_movie_night", "macro_all_off"]
}
```

### Profile Activation

When a profile is activated:

1. **Apply routing** (if defined)
2. **Apply output settings** (if defined)
3. **Update CEC tray targets** based on pinning
4. **Show associated macros** in tray quick-access

### Auto-Detection Logic

When `cecPinning.navigation` or `cecPinning.playback` is set to `auto`:

1. Look at profile's routing configuration
2. Find the input routed to the "primary" output (Output 1 by default)
3. Use that input as the CEC target

When no profile is active, use current live routing state.

---

## Control Zones

### Concept

Control Zones are an optional advanced layer that groups profiles for input and output sections. This allows complex multi-profile configurations while managing conflicts.

### Data Structure

```typescript
interface ControlZone {
  id: string;                    // Unique identifier
  name: string;                  // Display name (e.g., "Living Room")
  icon?: string;                 // Optional emoji/icon
  description?: string;          // Optional description
  
  // Profile assignments
  inputProfile?: string;         // Profile ID for input section
  outputProfile?: string;        // Profile ID for output section
  
  // Zone-specific overrides
  outputs: number[];             // Which outputs belong to this zone
  
  // State
  isActive: boolean;             // Zone currently active
  
  // Metadata
  createdAt: string;
  updatedAt: string;
}
```

### Example Control Zones

```json
{
  "id": "zone_living_room",
  "name": "Living Room",
  "icon": "🏠",
  "outputs": [1, 2],
  "inputProfile": "profile_streaming",
  "outputProfile": "profile_surround_audio",
  "isActive": true
}
```

```json
{
  "id": "zone_bedroom",
  "name": "Bedroom",
  "icon": "🛏️",
  "outputs": [3],
  "inputProfile": "profile_cable_tv",
  "outputProfile": null,
  "isActive": true
}
```

### Conflict Detection

When activating a zone or profile, check for conflicts:

```typescript
interface Conflict {
  type: 'output_overlap' | 'setting_conflict';
  message: string;
  zoneA: string;
  zoneB: string;
  outputs?: number[];
}
```

**Output Overlap:** Two active zones claiming the same output
```
⚠️ Conflict Detected
Zone "Living Room" and "Guest Mode" both use Output 1.
[Deactivate Living Room] [Deactivate Guest Mode] [Cancel]
```

**Setting Conflict:** Same output with different settings in active profiles
```
⚠️ Setting Conflict
Output 1 has different HDR settings in active profiles:
- Movie Mode: HDR Auto
- Gaming Mode: HDR Passthrough
[Use Movie Mode] [Use Gaming Mode] [Cancel]
```

---

## UI Organization

### Mobile Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ OREI Matrix Control                    [🔄] [≡]             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│                                                                  │
│                        MAIN CONTENT                              │
│                    (based on active tab)                         │
│                                                                  │
│                                                                  │
│                                                ┌────┐            │
│                                                │ 🎮 │  ← FAB    │
│                                                └────┘            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ [Matrix] [Inputs] [Outputs] [Scenes] [⋯]                    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  "More" menu (⋯) contains:                                       │
│  • Presets                                                       │
│  • CEC Settings                                                  │
│  • Settings                                                      │
│                                                                  │
│  Debug console: Accessed from Settings, persists when opened     │
└─────────────────────────────────────────────────────────────────┘
```

### Tablet/Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ OREI Matrix Control   [Matrix][Inputs][Outputs][Scenes][Presets]    │ │
│ │                                      [CEC Config][Settings] [🔄]    │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ ┌────────────────────────────────────┐  ┌─────────────────────────────┐ │
│ │                                    │  │ CEC Remote        ⚙️  📌    │ │
│ │                                    │  │ ──────────────────────────  │ │
│ │          MAIN CONTENT              │  │ Profile: Movie Mode         │ │
│ │                                    │  │ Nav: Apple TV               │ │
│ │                                    │  │ Vol: Soundbar               │ │
│ │                                    │  │ ──────────────────────────  │ │
│ │                                    │  │ [Power] [Nav] [Vol]         │ │
│ │                                    │  │ [Playback]                  │ │
│ │                                    │  │ [Macros]                    │ │
│ └────────────────────────────────────┘  └─────────────────────────────┘ │
│                                            ↑ Pinned CEC panel           │
│                                                                          │
│  Debug console: Toggles from Settings, can be docked bottom or side     │
└─────────────────────────────────────────────────────────────────────────┘
```

### Tab Bar Behavior

**Mobile (5 visible + overflow):**
```
[Matrix] [Inputs] [Outputs] [Scenes] [⋯]
                                      │
                                      ▼
                              ┌─────────────┐
                              │ Presets     │
                              │ CEC Config  │
                              │ Settings    │
                              └─────────────┘
```

**Future Enhancement: Adaptive Learning**
- Track which tabs user accesses most
- Automatically promote frequently-used tabs to visible area
- Store preferences in localStorage

**Future Enhancement: Manual Customization**
- Drag-and-drop tab reordering
- Pin favorite tabs
- Settings to configure visible tabs

### Debug Console

**Behavior:**
- Accessed from Settings menu
- Once opened, persists as overlay/panel
- Click X to close
- Can be minimized to a small indicator
- On desktop: dockable to bottom or side

---

## Storage Structure

### File Organization

```
data/
├── config_state.json         # Existing: connection, names
├── scenes.json               # Existing: routing scenes
├── cec_macros.json           # NEW: CEC Macros
└── profiles.json             # NEW: Profiles + Control Zones
```

### cec_macros.json

```json
{
  "version": 1,
  "macros": [
    {
      "id": "macro_movie_night",
      "name": "Movie Night",
      "icon": "🎬",
      "commands": [...]
    }
  ]
}
```

### profiles.json

```json
{
  "version": 1,
  "profiles": [
    {
      "id": "profile_movie_mode",
      "name": "Movie Mode",
      ...
    }
  ],
  "controlZones": [
    {
      "id": "zone_living_room",
      "name": "Living Room",
      ...
    }
  ],
  "settings": {
    "cecTrayPosition": "bottom-right",
    "cecTrayPinned": false,
    "defaultProfile": null,
    "controlZonesEnabled": false
  }
}
```

### localStorage Keys

```javascript
// UI preferences (browser-specific)
localStorage['orei_cec_tray_position']     // FAB position
localStorage['orei_cec_tray_pinned']       // Expanded and pinned
localStorage['orei_tab_order']             // Custom tab ordering
localStorage['orei_tab_usage']             // Tab usage statistics
localStorage['orei_debug_open']            // Debug console state
localStorage['orei_debug_position']        // Debug dock position
```

---

## Implementation Phases

### Phase 1A: Floating CEC Tray (Foundation)

**Goal:** Unified CEC remote with auto-detection

**Tasks:**
1. Create `cec-tray.js` component
   - Floating action button (FAB)
   - Expandable remote panel
   - Auto-detect targets from current routing
   - Device name display with tap-to-change
   
2. Add `cec-tray.css` styles
   - FAB styling
   - Expanded panel layout
   - Responsive design (mobile/tablet/desktop)
   - Position customization
   
3. Update `state.js`
   - Track CEC tray state
   - Store target selections
   - Provide routing-based auto-detection
   
4. Add position settings
   - Settings UI for tray position
   - Pin/unpin option for larger screens

**Deliverables:**
- Floating CEC tray with all controls
- Auto-detection of CEC targets
- Manual target override
- Position customization

---

### Phase 1B: CEC Macros

**Goal:** Create and execute CEC command sequences

**Tasks:**
1. Create `cec_macros.json` storage
   
2. Add REST API endpoints
   - `GET /api/cec/macros` - List all macros
   - `POST /api/cec/macros` - Create macro
   - `PUT /api/cec/macros/{id}` - Update macro
   - `DELETE /api/cec/macros/{id}` - Delete macro
   - `POST /api/cec/macros/{id}/execute` - Run macro
   
3. Create `cec-macro-editor.js` component
   - Macro list view
   - Create/edit modal
   - Command builder UI
   - Test execution
   
4. Integrate with CEC tray
   - Show macro quick-access buttons
   - Execute macros from tray

**Deliverables:**
- Macro CRUD API
- Macro editor UI
- Macro execution
- Tray integration

---

### Phase 2: Profiles

**Goal:** Save and apply complete configurations

**Tasks:**
1. Create `profiles.json` storage
   
2. Add REST API endpoints
   - `GET /api/profiles` - List profiles
   - `POST /api/profiles` - Create profile
   - `PUT /api/profiles/{id}` - Update profile
   - `DELETE /api/profiles/{id}` - Delete profile
   - `POST /api/profiles/{id}/activate` - Apply profile
   - `POST /api/profiles/{id}/deactivate` - Deactivate profile
   
3. Create profile editor UI
   - Profile list view
   - Create/edit modal
   - Routing configuration
   - Output settings per output
   - CEC pinning configuration
   - Macro assignment
   
4. Update CEC tray
   - Show active profile
   - Apply profile CEC pinning
   - Quick profile switcher

**Deliverables:**
- Profile CRUD API
- Profile editor UI
- Profile activation/deactivation
- CEC tray profile integration

---

### Phase 3: Control Zones

**Goal:** Group profiles for multi-zone configurations

**Tasks:**
1. Extend `profiles.json` with zones
   
2. Add REST API endpoints
   - `GET /api/zones` - List zones
   - `POST /api/zones` - Create zone
   - `PUT /api/zones/{id}` - Update zone
   - `DELETE /api/zones/{id}` - Delete zone
   - `POST /api/zones/{id}/activate` - Activate zone
   - `POST /api/zones/{id}/deactivate` - Deactivate zone
   
3. Create zone editor UI
   - Zone list view
   - Create/edit modal
   - Output assignment
   - Profile assignment (input/output sections)
   
4. Conflict detection
   - Check for output overlap
   - Check for setting conflicts
   - User prompts for resolution
   
5. Settings toggle
   - Enable/disable Control Zones feature
   - When disabled, just use profiles

**Deliverables:**
- Zone CRUD API
- Zone editor UI
- Conflict detection and resolution
- Feature toggle

---

### Phase 4: UI Refinements

**Goal:** Polish navigation and customization

**Tasks:**
1. Tab bar improvements
   - "More" overflow menu implementation
   - Tab usage tracking
   - Adaptive tab promotion (learning)
   
2. Tab customization
   - Drag-and-drop reordering
   - Pin/hide tabs
   - Settings UI for customization
   
3. Debug console improvements
   - Move to Settings access
   - Dockable panel
   - Minimize/maximize
   
4. Responsive refinements
   - Test all screen sizes
   - Optimize layouts
   - Performance optimization

**Deliverables:**
- Polished tab navigation
- Customization options
- Improved debug console
- Responsive design

---

## API Endpoints

### CEC Macros

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cec/macros` | List all macros |
| POST | `/api/cec/macros` | Create new macro |
| GET | `/api/cec/macros/{id}` | Get macro details |
| PUT | `/api/cec/macros/{id}` | Update macro |
| DELETE | `/api/cec/macros/{id}` | Delete macro |
| POST | `/api/cec/macros/{id}/execute` | Execute macro |

### Profiles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profiles` | List all profiles |
| POST | `/api/profiles` | Create new profile |
| GET | `/api/profiles/{id}` | Get profile details |
| PUT | `/api/profiles/{id}` | Update profile |
| DELETE | `/api/profiles/{id}` | Delete profile |
| POST | `/api/profiles/{id}/activate` | Activate profile |
| POST | `/api/profiles/{id}/deactivate` | Deactivate profile |
| GET | `/api/profiles/active` | Get active profiles |

### Control Zones

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/zones` | List all zones |
| POST | `/api/zones` | Create new zone |
| GET | `/api/zones/{id}` | Get zone details |
| PUT | `/api/zones/{id}` | Update zone |
| DELETE | `/api/zones/{id}` | Delete zone |
| POST | `/api/zones/{id}/activate` | Activate zone |
| POST | `/api/zones/{id}/deactivate` | Deactivate zone |
| GET | `/api/zones/active` | Get active zones |
| GET | `/api/zones/conflicts` | Check for conflicts |

---

## Implementation Status

### ✅ Phase 1A: Floating CEC Tray (COMPLETE)

**Completed Files:**
- `web/js/components/cec-tray.js` - Floating CEC remote component (933 lines)
- `web/js/components/cec-controls.js` - CEC control button handlers
- `web/css/cec-tray.css` - CEC tray styling with scene indicator
- `web/js/state.js` - Added CEC tray state management + activeScene tracking
- `web/index.html` - Integrated CSS/JS files, added position setting
- `web/js/components/settings-panel.js` - Added position selector handling

**Features Implemented:**
- ✅ Floating action button (FAB) with TV icon
- ✅ Expandable panel with full remote controls:
  - Power On/Off buttons
  - D-pad navigation (Up, Down, Left, Right, OK, Menu, Back)
  - Playback controls (Play, Pause, Stop, Previous, Next, Rewind, Fast Forward)
  - Volume controls (Up, Down, Mute)
- ✅ Auto-detection of CEC targets from current routing
- ✅ Manual target override via dropdown selectors (tap device name to change)
- ✅ Device names displayed in tray header
- ✅ Position customization (bottom-right, bottom-left, top-right)
- ✅ Pin functionality for larger screens
- ✅ Persistent settings via localStorage
- ✅ Active scene/profile indicator in tray header
- ✅ Scene-based CEC config integration (uses scene CEC settings when profile active)
- ✅ Clears active scene when routing changes manually

**NOT YET Implemented (from Requirements):**
- ⚠️ Multi-profile selector (when multiple profiles active, show selector)
- ⚠️ Fallback prompt when auto-detection fails

**Known Issues / TODO:**
- ⚠️ **CEC Command Testing Required**: Power on/off commands work correctly (sends to TV and soundbar), but menu navigation, volume, and other CEC commands need testing and debugging for all device types.
- ⚠️ **CEC Enable Requirement (LIKELY ROOT CAUSE)**: HAR data shows CEC must be enabled per-port (`inputindex`/`outputindex` arrays). Currently only Input 2 and Output 1 have CEC enabled on your matrix. Power commands may work as broadcast, but navigation commands likely need CEC enabled on the specific port.
  - **Fix**: Either auto-enable CEC on ports before sending commands, or add UI to enable CEC per port
  - **Investigation**: Test enabling CEC on a port, then send navigation command
- ~~Desktop: CEC tray overlaps with debug menu~~ ✅ RESOLVED - Debug moved to bottom-left
- Need to verify CEC command mappings match what devices expect
- May need device-specific CEC command variations

### 🔄 Phase 1B: CEC Macros (NOT STARTED)

**Priority: HIGH** - Enables power automation sequences

**Files to Create:**
- `src/cec_macros.py` - Macro storage and execution
- `data/cec_macros.json` - Macro storage file
- `web/js/components/cec-macro-editor.js` - Macro CRUD UI

**TODO:**
- [ ] Create CEC macro storage (cec_macros.json)
- [ ] Create macro CRUD REST API endpoints
- [ ] Create macro editor UI component
- [ ] Add quick-access macro buttons to CEC tray

### ✅ Phase 2: Profile-Based CEC Config (PARTIAL)

**⚠️ Terminology Issue:** The codebase currently uses "Scene" but should use "Profile". Migration is tracked in Priority 2.

**Current Implementation (using Scene terminology):**

**Completed Files:**
- `src/config.py` - Scene, SceneOutput, CecConfig dataclasses
- `src/cec_commands.py` - CEC command definitions (POWER_ON, POWER_OFF, NAV commands, PLAYBACK, VOLUME)
- `src/cec_resolver.py` - Auto-resolution logic for CEC targets based on output configuration
- `web/js/components/scene-cec-modal.js` - Modal UI for editing scene CEC configuration
- `web/js/components/scenes-panel.js` - Modified to call `state.setActiveScene(scene)` on recall
- `tests/test_cec_resolver.py` - Unit tests for CEC resolver (9 tests passing)

**CecConfig Schema (per Scene/Profile):**
```json
{
  "nav_targets": ["output_2"],
  "playback_targets": ["output_2"],
  "volume_targets": ["output_1"],
  "power_on_targets": ["output_1", "output_2"],
  "power_off_targets": ["output_1", "output_2"],
  "auto_resolved": true
}
```

**Features Implemented:**
- ✅ CEC config stored per scene in `scenes.json`
- ✅ Auto-resolution based on output scaler modes:
  - Volume priority: audio_only (scaler=4) > ARC-enabled > first output
  - Power targets: all outputs in the routing
  - Nav/Playback: first connected output
- ✅ Manual override UI via Scene CEC Modal
- ✅ Active scene indicator in CEC tray title
- ✅ Scene clearing when routing changes manually

**Gap Analysis - Missing vs Document Requirements:**

| Requirement | Status | Notes |
|-------------|--------|-------|
| `id`, `name` | ✅ | Implemented in Scene |
| `icon`, `description` | ❌ NOT IMPLEMENTED | Add to Scene dataclass |
| `routing` | ✅ | Via SceneOutput.input |
| `outputSettings.enabled` | ✅ | SceneOutput.enabled |
| `outputSettings.audioMuted` | ✅ | SceneOutput.audio_mute |
| `outputSettings.hdrMode` | ✅ | SceneOutput.hdr_mode |
| `outputSettings.hdcpMode` | ✅ | SceneOutput.hdcp_mode |
| `outputSettings.arcEnabled` | ❌ NOT IMPLEMENTED | Add to SceneOutput |
| `outputSettings.scalerMode` | ❌ NOT IMPLEMENTED | Add to SceneOutput |
| `cecPinning.navigation` | ✅ | CecConfig.nav_targets |
| `cecPinning.playback` | ✅ | CecConfig.playback_targets |
| `cecPinning.volume` | ✅ | CecConfig.volume_targets |
| `cecPinning.power` | ✅ | CecConfig.power_on/off_targets |
| `macros[]` | ❌ NOT IMPLEMENTED | Depends on Phase 1B |
| `isActive` | ⚠️ PARTIAL | Frontend only (state.js) |

**TODO to Complete Phase 2:**
- [ ] Add `icon` and `description` fields to Scene dataclass
- [ ] Add `arc_enabled` and `scaler_mode` fields to SceneOutput dataclass
- [ ] Update Scene editor UI to support new fields
- [ ] Add `macros[]` field to Scene (after Phase 1B complete)
- [ ] Persist active profile ID in backend

### ⏳ Phase 3: Control Zones (NOT STARTED)

**Concept:** Control Zones are an optional advanced layer that groups profiles for input and output sections. Users can use Profiles directly without enabling Control Zones.

**Key Requirements (from Detailed Requirements section):**
- Optional feature with enable toggle in Settings
- Zones assign profiles to Input Section and Output Section
- Multiple zones can be active simultaneously
- Conflict detection when settings overlap between active zones
- User prompted to disable conflicting zone

**Data Model:**
```typescript
interface ControlZone {
  id: string;
  name: string;
  icon?: string;
  outputs: number[];           // Which outputs belong to this zone
  inputProfile?: string;       // Profile ID for input section
  outputProfile?: string;      // Profile ID for output section  
  isActive: boolean;
}
```

**TODO:**
- [ ] Add `controlZonesEnabled` setting toggle
- [ ] Create zones storage in profiles.json
- [ ] Create zone CRUD REST API endpoints
- [ ] Create zone editor UI component
- [ ] Implement conflict detection logic
- [ ] Add conflict resolution UI (prompt user which zone to disable)
- [ ] Update CEC tray to respect active zone settings

### 🔄 Phase 4: UI Refinements (PARTIAL)

**Completed:**
- ✅ Debug menu moved to bottom-left (no longer overlaps CEC tray)

**NOT STARTED - Tab Bar Improvements:**
- [ ] Bottom menu slides up to expose additional buttons
- [ ] Show max 5 tabs on mobile, remainder in "⋯" overflow menu  
- [ ] If screen large enough, hide "More" button (all tabs fit)
- [ ] Track frequently-used tabs in localStorage
- [ ] Implement adaptive tab promotion (frequently used tabs move to visible area)
- [ ] Drag-and-drop tab reordering
- [ ] User can define which tabs are visible vs in overflow
- [ ] Pin favorite tabs

**NOT STARTED - Debug Console Redesign:**
- [ ] Remove floating debug button
- [ ] Add "Debug Console" option in Settings panel
- [ ] Debug persists as overlay/panel once opened until X clicked
- [ ] Make debug panel dockable (bottom or side of screen)
- [ ] Add minimize to small indicator**NOT STARTED:**
- [ ] Tab bar overflow menu for mobile (5 visible + "⋯" overflow)
- [ ] Frequently-used tab tracking
- [ ] Adaptive tab promotion
- [ ] Debug console access from Settings menu
- [ ] Dockable debug panel (bottom or side)
- [ ] Debug minimize/maximize functionality

---

## Code Structure

### JavaScript Files (Current State)

```
web/js/
├── components/
│   ├── cec-tray.js           # ✅ Floating CEC remote
│   ├── cec-controls.js       # ✅ CEC control button handlers
│   ├── scene-cec-modal.js    # ✅ Scene CEC configuration modal
│   ├── scenes-panel.js       # ✅ Modified for activeScene tracking
│   ├── debug-panel.js        # ✅ Modified - now bottom-left
│   ├── cec-macro-editor.js   # ⏳ TODO: Macro CRUD UI
│   ├── zone-editor.js        # ⏳ TODO: Zone CRUD UI (Phase 3)
│   └── cec-settings-panel.js # ⏳ TODO: CEC configuration tab
├── state.js                  # ✅ CEC tray + activeScene state
```

### CSS Files (Current State)

```
web/css/
├── cec-tray.css              # ✅ CEC tray + scene indicator styles
├── cec-editors.css           # ⏳ TODO: Macro/zone editor styles
```

### Python Backend (Current State)

```
src/
├── rest_api.py               # ✅ CEC endpoints added
├── cec_commands.py           # ✅ CEC command definitions
├── cec_resolver.py           # ✅ Auto-resolution for CEC targets
├── cec_macros.py             # ⏳ TODO: Macro storage and execution
└── zones.py                  # ⏳ TODO: Zone management (Phase 3)
```

### Test Files (Current State)

```
tests/
├── test_cec_resolver.py      # ✅ 9 unit tests for CEC resolver
```

### Data Files (Current State)

```
data/
├── scenes.json               # ✅ Stores scene CEC config per scene
├── cec_macros.json           # ⏳ TODO: Macro storage
```

---

## Summary

This architecture provides:

1. **Immediate Value:** Floating CEC tray with auto-detection works standalone
2. **Building Blocks:** Macros enable power automation
3. **Configuration Saving:** Scene-based CEC config captures complete states
4. **Advanced Grouping:** Control Zones enable multi-profile scenarios
5. **Scalable UI:** Overflow menu and customization handle growing features
6. **Clean Separation:** Each layer works independently but integrates smoothly

The phased implementation ensures each feature is fully functional before building the next layer.

---

## Prioritized Action Items

### Priority 1: CEC Macros (Phase 1B)
**Estimated Effort:** Medium | **Value:** High | **Status:** NOT STARTED

Macros enable automated power-on/power-off sequences, which users frequently need. Completing this unlocks the `macros[]` field for Profiles.

**Tasks:**
1. Create `data/cec_macros.json` storage file
2. Create `src/cec_macros.py` with CRUD operations and execution logic
3. Add REST endpoints: `GET/POST/PUT/DELETE /api/cec/macros`, `POST /api/cec/macros/{id}/execute`
4. Create `web/js/components/cec-macro-editor.js` UI component
5. Add quick-access macro buttons to CEC tray panel

**Macro Schema:**
```json
{
  "id": "power_on_theater",
  "name": "Theater Power On",
  "icon": "🎬",
  "steps": [
    { "command": "POWER_ON", "targets": ["output_1", "output_2"], "delay_ms": 0 },
    { "command": "POWER_ON", "targets": ["input_3"], "delay_ms": 2000 }
  ]
}
```

---

### Priority 2: Complete Profile Data Model + Terminology Migration (Phase 2 Gap)
**Estimated Effort:** Medium | **Value:** High | **Status:** NOT STARTED

Fill in the missing fields AND rename Scenes → Profiles throughout the codebase.

**Part A: Terminology Migration (Scenes → Profiles):**

| File | Change |
|------|--------|
| `src/config.py` | `Scene` → `Profile`, `SceneOutput` → `ProfileOutput`, `SceneManager` → `ProfileManager` |
| `src/rest_api.py` | `/api/scenes/*` → `/api/profiles/*` (keep aliases for backward compat) |
| `data/scenes.json` | Migrate to `data/profiles.json` (auto-detect and migrate on load) |
| `web/js/components/scenes-panel.js` | Rename to `profiles-panel.js`, update all references |
| `web/js/components/scene-cec-modal.js` | Rename to `profile-cec-modal.js`, update all references |
| `web/js/state.js` | `activeScene` → `activeProfile`, `setActiveScene` → `setActiveProfile` |
| `web/index.html` | Update script references and tab labels |
| `tests/` | Update test files to use Profile terminology |

**Part B: Add Missing Profile Fields:**

Backend Tasks (`src/config.py`):
1. Add to `Profile` dataclass:
   - `icon: str | None = None`
   - `description: str | None = None`
   - `macros: list[str] = field(default_factory=list)` (macro IDs)
2. Add to `ProfileOutput` dataclass:
   - `arc_enabled: bool | None = None`
   - `scaler_mode: int | None = None`
3. Update `to_dict()` and `from_dict()` for both classes
4. Add active profile tracking to backend (not just frontend)

**Part C: Frontend Updates:**
1. Update profile editor modal to include icon picker and description field
2. Update profile editor to show ARC and scaler mode settings
3. Add macro assignment UI (after Priority 1 complete)

---

### Priority 3: Tab Bar Overflow Menu (Phase 4)
**Estimated Effort:** Medium | **Value:** Medium | **Status:** NOT STARTED

Mobile UX improvement - currently all tabs may not fit on small screens.

**Tasks:**
1. Detect viewport width and number of tabs
2. Show max 5 tabs on mobile, remainder in "⋯" overflow menu
3. Track frequently-used tabs in localStorage
4. Implement adaptive tab promotion (frequently used tabs move to visible area)

**Implementation Notes:**
- Add `web/js/components/tab-overflow.js`
- Modify `web/js/components/navigation.js` to use overflow component
- Add CSS for overflow dropdown menu

**Tab Overflow UI:**
```
[Matrix] [Inputs] [Outputs] [Profiles] [⋯]
                                        │
                                        ▼
                                ┌─────────────┐
                                │ Presets     │
                                │ CEC Config  │
                                │ Settings    │
                                └─────────────┘
```

---

### Priority 4: Debug Console Redesign (Phase 4)
**Estimated Effort:** Low | **Value:** Low | **Status:** NOT STARTED

Move debug from floating button to Settings menu for cleaner UI.

**Tasks:**
1. Remove floating debug button from bottom-left
2. Add "Debug Console" option in Settings panel
3. Make debug panel dockable (bottom or side of screen)
4. Add minimize/maximize toggle

**Implementation Notes:**
- Modify `web/js/components/settings-panel.js` to add debug toggle
- Modify `web/js/components/debug-panel.js` for docking behavior
- Add dock position to localStorage settings

---

### Priority 5: Control Zones (Phase 3)
**Estimated Effort:** High | **Value:** Medium | **Status:** NOT STARTED

Group multiple profiles together for complex multi-room scenarios.

**Use Cases:**
- "Whole House Movie Mode" - activates Living Room + Bedroom profiles together
- Zone-based power management - turn off all devices in a zone
- Input/Output section profiles - separate CEC settings for different parts of the system

**Tasks:**
1. Extend `profiles.json` with zones structure
2. Add REST API endpoints for zone CRUD
3. Create zone editor UI
4. Implement conflict detection (output overlap, setting conflicts)
5. Add feature toggle in Settings

**Control Zone Schema:**
```json
{
  "id": "zone_living_room",
  "name": "Living Room",
  "icon": "🏠",
  "outputs": [1, 2],
  "inputProfile": "profile_streaming",
  "outputProfile": "profile_surround_audio",
  "isActive": true
}
```

---

## Implementation Roadmap

```
┌─────────────────────────────────────────────────────────────────────┐
│ COMPLETED                                                           │
├─────────────────────────────────────────────────────────────────────┤
│ ✅ Phase 1A: Floating CEC Tray                                     │
│ ✅ Phase 2 (Partial): Profile CEC Config (nav, playback, volume,   │
│                       power targets, auto-resolution)               │
│ ✅ Debug menu position fix                                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PRIORITY 1: CEC Macros                                              │
│ • Backend: cec_macros.py, cec_macros.json                          │
│ • API: /api/cec/macros CRUD + execute                              │
│ • UI: Macro editor, tray integration                               │
│ • Unlocks: macros[] field for Profiles                             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PRIORITY 2: Complete Profile Data Model                             │
│ • Add icon, description to Scene                                    │
│ • Add arc_enabled, scaler_mode to SceneOutput                      │
│ • Add macros[] to Scene                                             │
│ • Active profile persistence                                        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PRIORITY 3: Tab Bar Overflow                                        │
│ • Mobile: 5 visible + overflow                                      │
│ • Usage tracking                                                    │
│ • Adaptive promotion                                                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PRIORITY 4: Debug Console Redesign                                  │
│ • Move to Settings menu                                             │
│ • Dockable panel                                                    │
│ • Minimize/maximize                                                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PRIORITY 5: Control Zones                                           │
│ • Zone CRUD API                                                     │
│ • Zone editor UI                                                    │
│ • Conflict detection                                                │
│ • Multi-profile activation                                          │
└─────────────────────────────────────────────────────────────────────┘
```
