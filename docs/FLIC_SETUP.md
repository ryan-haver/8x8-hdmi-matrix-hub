# Flic Button Setup Guide

> **Status**: ✅ REST API v2.10.0 Available | Profiles & Macros Supported

This guide explains how to configure Flic smart buttons to control your OREI HDMI Matrix using the REST API. Includes advanced features like Profiles (room presets with CEC automation) and Macros (multi-step command sequences).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Supported Button Types](#supported-button-types)
- [Available API Endpoints](#available-api-endpoints)
- [Configuration Steps](#configuration-steps)
- [Basic Examples](#example-configurations)
- [Profiles Integration](#profiles-integration) ⭐ NEW
- [CEC Macros Integration](#cec-macros-integration) ⭐ NEW
- [Zone-Based Configurations](#zone-based-configurations) ⭐ NEW
- [Flic Hub SDK Integration](#flic-hub-sdk-integration) ⭐ NEW
- [Troubleshooting](#troubleshooting)

## Prerequisites

- OREI HDMI Matrix integration running (Docker or standalone)
- REST API running on port 8080
- Flic Hub (LR or Mini) with firmware updated
- Flic buttons (Original, Twist, or Duo)
- Flic app installed on your phone
- All devices on the same network

## Quick Start

1. Verify your REST API is running: `curl http://YOUR_IP:8080/api/status`
2. Note your API base URL: `http://YOUR_IP:8080`
3. Open Flic app → Select button → Choose action → Add Internet Request
4. Configure URL and method as shown in examples below

## Supported Button Types

### Flic Original / Flic 2
Single button with multiple click patterns:
- **Single click** - Primary action (e.g., switch to favorite input)
- **Double click** - Secondary action (e.g., switch to alternate input)
- **Hold** - Tertiary action (e.g., power off matrix)

### Flic Duo
Two buttons on one device:
- **Left button** - One action (e.g., previous input)
- **Right button** - Another action (e.g., next input)
- Each button supports click patterns (single, double, hold)

### Flic Twist (Recommended for Input Selection)
Rotary dial with button - **ideal for cycling through inputs**:
- **Rotate clockwise** - Next input (uses `/api/input/next`)
- **Rotate counter-clockwise** - Previous input (uses `/api/input/previous`)
- **Press** - Confirm/select action

## Available API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Get matrix status |
| `/api/input/{n}` | POST | Switch all outputs to input N |
| `/api/input/next?output=N` | POST | Cycle to next input on output N |
| `/api/input/previous?output=N` | POST | Cycle to previous input on output N |
| `/api/output/{n}/source` | POST | Set output N to input (body: `{"input": N}`) |
| `/api/preset/{n}` | POST | Recall preset N |
| `/api/preset/{n}/save` | POST | Save current routing to preset N |
| `/api/power/on` | POST | Power on matrix |
| `/api/power/off` | POST | Power off matrix |
| `/api/output/{n}/hdcp` | POST | Set HDCP mode (body: `{"mode": 1-5}`) |
| `/api/output/{n}/hdr` | POST | Set HDR mode (body: `{"mode": 1-3}`) |
| `/api/output/{n}/mute` | POST | Mute audio (body: `{"muted": true/false}`) |
| `/api/cec/input/{n}/power_on` | POST | Send CEC power on to input N |
| `/api/cec/input/{n}/power_off` | POST | Send CEC power off to input N |
| `/api/cec/input/{n}/play` | POST | Send CEC play to input N |
| `/api/cec/output/{n}/volume_up` | POST | CEC volume up on output N |
| `/api/cec/output/{n}/volume_down` | POST | CEC volume down on output N |
| `/api/cec/output/{n}/mute` | POST | CEC mute on output N |
| `/api/system/reboot` | POST | Reboot matrix |
| `/api/profiles` | GET | List all profiles |
| `/api/profile/{id}/recall` | POST | Recall profile (with CEC macros) |
| `/api/cec/macros` | GET | List all CEC macros |
| `/api/cec/macro/{id}/execute` | POST | Execute a CEC macro |

## Configuration Steps

### 1. Find Your API URL
Your REST API runs at: `http://YOUR_IP:8080` (replace YOUR_IP with your Docker host IP)

Example: `http://192.168.1.145:8080`

### 2. Open Flic App
1. Launch the Flic app
2. Select your button
3. Tap the action you want to configure (single click, double click, etc.)

### 3. Add Internet Request Action
1. Scroll to **Tools** section
2. Select **Internet Request**
3. Configure the request:

## Example Configurations

### Flic Original - Living Room Button

Best for: Quick switching between favorite inputs and power control

| Action | URL | Method | Description |
|--------|-----|--------|-------------|
| Single click | `http://192.168.1.145:8080/api/preset/2` | POST | AppleTV preset |
| Double click | `http://192.168.1.145:8080/api/preset/5` | POST | Shield preset |
| Hold | `http://192.168.1.145:8080/api/power/off` | POST | Power off matrix |

### Flic Duo - Gaming Setup

Best for: Quick toggle between two sources

| Button | Action | URL | Method | Description |
|--------|--------|-----|--------|-------------|
| Left | Single click | `http://192.168.1.145:8080/api/preset/6` | POST | PS5 |
| Right | Single click | `http://192.168.1.145:8080/api/preset/4` | POST | Switch |
| Left | Hold | `http://192.168.1.145:8080/api/cec/input/6/power_on` | POST | Power on PS5 |
| Right | Hold | `http://192.168.1.145:8080/api/cec/input/4/power_on` | POST | Power on Switch |

### Flic Duo - Input Navigation

Best for: Browsing through inputs on a specific output

| Button | Action | URL | Method | Description |
|--------|--------|-----|--------|-------------|
| Left | Single click | `http://192.168.1.145:8080/api/input/previous?output=1` | POST | Previous input on TV 1 |
| Right | Single click | `http://192.168.1.145:8080/api/input/next?output=1` | POST | Next input on TV 1 |

### Flic Twist - Input Selector (Recommended!)

Best for: Intuitive browsing and selection of inputs

| Action | URL | Method | Description |
|--------|-----|--------|-------------|
| Rotate CW | `http://192.168.1.145:8080/api/input/next?output=1` | POST | Next input |
| Rotate CCW | `http://192.168.1.145:8080/api/input/previous?output=1` | POST | Previous input |
| Press | `http://192.168.1.145:8080/api/status` | GET | Get current status |

**Note**: The `?output=1` parameter specifies which output to cycle. Change to `?output=2`, etc. for other TVs.

### Flic Twist - Volume Control

Best for: Controlling TV/soundbar volume via CEC

| Action | URL | Method | Description |
|--------|-----|--------|-------------|
| Rotate CW | `http://192.168.1.145:8080/api/cec/output/1/volume_up` | POST | Volume up |
| Rotate CCW | `http://192.168.1.145:8080/api/cec/output/1/volume_down` | POST | Volume down |
| Press | `http://192.168.1.145:8080/api/cec/output/1/mute` | POST | Mute toggle |

### Direct Input Control

For setting a specific output to a specific input:

```
URL: http://192.168.1.145:8080/api/output/1/source/3
Method: POST
Description: Sets Output 1 to Input 3
```

## CEC Control Examples

Control connected devices directly from Flic buttons via CEC:

### Media Control Button
```
URL: http://192.168.1.145:8080/api/cec/input/2/play
Method: POST
Description: Send play command to device on Input 2
```

### Power Control
```
URL: http://192.168.1.145:8080/api/cec/input/2/power_on
Method: POST
Description: Power on AppleTV on Input 2
```

## Advanced: Multi-Room Setup

For setups with multiple Flic buttons controlling different outputs:

### Living Room (Output 1)
| Button | Action | URL |
|--------|--------|-----|
| Twist | Rotate CW | `http://192.168.1.145:8080/api/input/next?output=1` |
| Twist | Rotate CCW | `http://192.168.1.145:8080/api/input/previous?output=1` |

### Bedroom (Output 2)
| Button | Action | URL |
|--------|--------|-----|
| Twist | Rotate CW | `http://192.168.1.145:8080/api/input/next?output=2` |
| Twist | Rotate CCW | `http://192.168.1.145:8080/api/input/previous?output=2` |

### Office (Output 3)
| Button | Action | URL |
|--------|--------|-----|
| Duo Left | Single | `http://192.168.1.145:8080/api/output/3/source/1` |
| Duo Right | Single | `http://192.168.1.145:8080/api/output/3/source/2` |

---

## Profiles Integration

Profiles are enhanced scene configurations that can include CEC automation macros. They're perfect for "one-button" room activation with Flic buttons.

### What is a Profile?

A Profile combines:
- **Input routing** - Which sources go to which outputs
- **Power-on macro** - CEC commands to run when activating (turn on TVs, switch inputs)
- **Power-off macro** - CEC commands for deactivation (turn off devices)
- **Icon** - Visual identifier in the web UI

### Creating Profiles for Flic

First, create profiles via the REST API or web UI:

```bash
# Create a "Movie Night" profile
curl -X POST http://192.168.1.145:8080/api/profile \
  -H "Content-Type: application/json" \
  -d '{
    "id": "movie-night",
    "name": "Movie Night",
    "icon": "🎬",
    "outputs": {
      "1": 2,  
      "2": 2   
    },
    "power_on_macro": "theater-on",
    "power_off_macro": "theater-off"
  }'
```

### Flic Button → Profile Examples

#### One-Button Room Activation

| Button | Action | URL | Method | Description |
|--------|--------|-----|--------|-------------|
| Flic 2 | Single | `http://192.168.1.145:8080/api/profile/movie-night/recall` | POST | Activate Movie Night |
| Flic 2 | Double | `http://192.168.1.145:8080/api/profile/gaming/recall` | POST | Switch to Gaming |
| Flic 2 | Hold | `http://192.168.1.145:8080/api/power/off` | POST | Power off everything |

#### Multi-Room Profile Buttons

| Room | Button | Profile URL |
|------|--------|-------------|
| Living Room | Flic Original | `/api/profile/living-room-tv/recall` |
| Bedroom | Flic Original | `/api/profile/bedroom-streaming/recall` |
| Office | Flic 2 | `/api/profile/work-mode/recall` |
| Theater | Flic Duo (Left) | `/api/profile/movie-night/recall` |
| Theater | Flic Duo (Right) | `/api/profile/sports/recall` |

### Profile Examples for Common Scenarios

#### Movie Night Profile
```json
{
  "id": "movie-night",
  "name": "Movie Night",
  "icon": "🎬",
  "outputs": {
    "1": 2,
    "2": 2
  },
  "power_on_macro": "theater-on",
  "power_off_macro": "all-off"
}
```
Flic URL: `http://192.168.1.145:8080/api/profile/movie-night/recall`

#### Gaming Profile
```json
{
  "id": "gaming",
  "name": "Gaming Mode",
  "icon": "🎮",
  "outputs": {
    "1": 6
  },
  "power_on_macro": "gaming-setup"
}
```
Flic URL: `http://192.168.1.145:8080/api/profile/gaming/recall`

#### Work From Home Profile
```json
{
  "id": "work-mode",
  "name": "Work Mode",
  "icon": "💼",
  "outputs": {
    "3": 3
  }
}
```
Flic URL: `http://192.168.1.145:8080/api/profile/work-mode/recall`

---

## CEC Macros Integration

CEC Macros allow you to chain multiple CEC commands with configurable delays. Perfect for complex automation sequences.

### What is a CEC Macro?

A macro is a sequence of CEC commands that execute in order:
- **Steps** - Individual CEC commands
- **Targets** - Which ports to send to (inputs or outputs)
- **Delays** - Wait time between steps (for device boot-up, etc.)

### Creating Macros for Flic

Create macros via REST API:

```bash
# Create a "Theater On" macro
curl -X POST http://192.168.1.145:8080/api/cec/macro \
  -H "Content-Type: application/json" \
  -d '{
    "id": "theater-on",
    "name": "Theater On",
    "steps": [
      {"command": "power_on", "targets": {"outputs": [1, 2]}, "delay_ms": 0},
      {"command": "power_on", "targets": {"inputs": [2]}, "delay_ms": 3000},
      {"command": "active_source", "targets": {"inputs": [2]}, "delay_ms": 1000}
    ]
  }'
```

### Flic Button → Macro Examples

#### Direct Macro Execution

| Button | Action | URL | Method | Description |
|--------|--------|-----|--------|-------------|
| Flic 2 | Single | `http://192.168.1.145:8080/api/cec/macro/theater-on/execute` | POST | Run theater startup |
| Flic 2 | Double | `http://192.168.1.145:8080/api/cec/macro/all-off/execute` | POST | Power off all devices |
| Flic 2 | Hold | `http://192.168.1.145:8080/api/cec/macro/system-reset/execute` | POST | Reset CEC states |

### Example Macro Sequences

#### Theater Startup Macro
```json
{
  "id": "theater-on",
  "name": "Theater Startup",
  "steps": [
    {"command": "power_on", "targets": {"outputs": [1, 2]}, "delay_ms": 0},
    {"command": "power_on", "targets": {"inputs": [2]}, "delay_ms": 5000},
    {"command": "active_source", "targets": {"inputs": [2]}, "delay_ms": 2000}
  ]
}
```
**What it does:**
1. Power on TV (output 1) and Soundbar (output 2)
2. Wait 5 seconds for displays to boot
3. Power on Apple TV (input 2)
4. Wait 2 seconds
5. Set Apple TV as active source

Flic URL: `http://192.168.1.145:8080/api/cec/macro/theater-on/execute`

#### All Devices Off Macro
```json
{
  "id": "all-off",
  "name": "All Off",
  "steps": [
    {"command": "standby", "targets": {"inputs": [1,2,3,4,5,6,7,8]}, "delay_ms": 0},
    {"command": "standby", "targets": {"outputs": [1,2,3,4,5,6,7,8]}, "delay_ms": 2000}
  ]
}
```
**What it does:**
1. Send standby to all source devices
2. Wait 2 seconds
3. Send standby to all TVs/displays

Flic URL: `http://192.168.1.145:8080/api/cec/macro/all-off/execute`

#### Gaming Session Macro
```json
{
  "id": "gaming-setup",
  "name": "Gaming Setup",
  "steps": [
    {"command": "power_on", "targets": {"outputs": [1]}, "delay_ms": 0},
    {"command": "power_on", "targets": {"inputs": [6]}, "delay_ms": 3000},
    {"command": "volume_up", "targets": {"outputs": [2]}, "delay_ms": 500},
    {"command": "volume_up", "targets": {"outputs": [2]}, "delay_ms": 200},
    {"command": "volume_up", "targets": {"outputs": [2]}, "delay_ms": 200}
  ]
}
```
**What it does:**
1. Power on gaming TV
2. Power on PS5 (input 6) after 3 seconds
3. Bump soundbar volume up 3 notches

Flic URL: `http://192.168.1.145:8080/api/cec/macro/gaming-setup/execute`

---

## Zone-Based Configurations

For multi-room setups, configure each zone with dedicated Flic buttons and zone-specific profiles.

### Zone Configuration Strategy

| Zone | Output(s) | Primary Button | Secondary Button |
|------|-----------|----------------|------------------|
| Living Room | 1, 2 | Flic Twist (input cycling) | Flic 2 (profiles) |
| Bedroom | 3 | Flic Original (preset switching) | - |
| Office | 4 | Flic Duo (work/personal toggle) | - |
| Kids Room | 5 | Flic 2 (parental controls) | - |
| Outdoor | 6 | Flic Original (simple on/off) | - |

### Living Room Zone (Outputs 1 & 2)

**Primary Control: Flic Twist**
| Action | URL | Description |
|--------|-----|-------------|
| Rotate CW | `/api/input/next?output=1` | Next source on TV |
| Rotate CCW | `/api/input/previous?output=1` | Previous source |
| Press | `/api/profile/living-room-default/recall` | Reset to default |

**Profile Control: Flic 2**
| Action | URL | Description |
|--------|-----|-------------|
| Single | `/api/profile/living-room-tv/recall` | Normal TV watching |
| Double | `/api/profile/living-room-gaming/recall` | Gaming mode |
| Hold | `/api/cec/macro/living-room-off/execute` | Power off zone |

**Create the profiles:**
```bash
# Living Room TV Profile
curl -X POST http://192.168.1.145:8080/api/profile \
  -d '{"id":"living-room-tv","name":"Living Room TV","outputs":{"1":2,"2":2},"power_on_macro":"lr-on"}'

# Living Room Gaming Profile  
curl -X POST http://192.168.1.145:8080/api/profile \
  -d '{"id":"living-room-gaming","name":"Living Room Gaming","outputs":{"1":6,"2":6},"power_on_macro":"lr-gaming-on"}'
```

### Bedroom Zone (Output 3)

**Simple Control: Flic Original**
| Action | URL | Description |
|--------|-----|-------------|
| Single | `/api/profile/bedroom-streaming/recall` | Streaming (Apple TV) |
| Double | `/api/profile/bedroom-cable/recall` | Cable TV |
| Hold | `/api/cec/output/3/standby` | TV off |

### Office Zone (Output 4)

**Dual Mode: Flic Duo**
| Button | Action | URL | Description |
|--------|--------|-----|-------------|
| Left | Single | `/api/profile/work-mode/recall` | Work computer |
| Right | Single | `/api/profile/personal-mode/recall` | Personal device |
| Left | Hold | `/api/output/4/source/3` | Quick switch to Input 3 |
| Right | Hold | `/api/output/4/source/4` | Quick switch to Input 4 |

### Kids Room Zone (Output 5)

**Controlled Access: Flic 2 with limited profiles**
| Action | URL | Description |
|--------|-----|-------------|
| Single | `/api/profile/kids-streaming/recall` | Kid-safe streaming |
| Double | `/api/profile/kids-gaming/recall` | Game console |
| Hold | `/api/cec/macro/kids-room-off/execute` | Bedtime - power off |

---

## Flic Hub SDK Integration

For advanced users, the Flic Hub SDK allows you to write custom JavaScript modules that run directly on the Flic Hub. This enables complex logic, state management, and more sophisticated integrations.

### Why Use the SDK?

| Feature | Internet Request | Flic Hub SDK |
|---------|------------------|--------------|
| Simple API calls | ✅ | ✅ |
| Conditional logic | ❌ | ✅ |
| State tracking | ❌ | ✅ |
| Chained actions | ❌ | ✅ |
| Local execution | ❌ | ✅ (faster) |
| Toggle behavior | ❌ | ✅ |
| Error handling | ❌ | ✅ |

### Setting Up the SDK

1. **Access Flic Hub IDE**: Go to `https://hubsdk.flic.io/`
2. **Connect your Hub**: Link via Flic app or direct IP
3. **Create new module**: Click "New Module"
4. **Paste code and save**

### SDK Example: Toggle Profile

This module toggles between two profiles with a single button press:

```javascript
// OREI Matrix Toggle Profile Module
// Toggles between Movie Night and Gaming profiles

var buttonManager = require("buttons");
var http = require("http");

var API_BASE = "http://192.168.1.145:8080";
var currentProfile = "movie-night";

buttonManager.on("buttonSingleOrDoubleClickOrHold", function(obj) {
    var button = buttonManager.getButton(obj.bdaddr);
    var clickType = obj.isSingleClick ? "single" : obj.isDoubleClick ? "double" : "hold";
    
    if (clickType === "single") {
        // Toggle between profiles
        currentProfile = (currentProfile === "movie-night") ? "gaming" : "movie-night";
        recallProfile(currentProfile);
    } else if (clickType === "double") {
        // Always go to movie night
        currentProfile = "movie-night";
        recallProfile(currentProfile);
    } else if (clickType === "hold") {
        // Power off everything
        executeOffMacro();
    }
});

function recallProfile(profileId) {
    http.makeRequest({
        url: API_BASE + "/api/profile/" + profileId + "/recall",
        method: "POST",
        headers: {"Content-Type": "application/json"}
    }, function(err, res) {
        if (err) {
            console.log("Error recalling profile: " + err);
        } else {
            console.log("Profile recalled: " + profileId);
        }
    });
}

function executeOffMacro() {
    http.makeRequest({
        url: API_BASE + "/api/cec/macro/all-off/execute",
        method: "POST"
    }, function(err, res) {
        console.log(err ? "Off macro failed" : "All devices off");
    });
}

console.log("OREI Matrix Toggle Module loaded");
```

### SDK Example: Input Cycling with Feedback

Track current input and provide feedback via button LED:

```javascript
// OREI Matrix Input Cycler with State Tracking

var buttonManager = require("buttons");
var http = require("http");

var API_BASE = "http://192.168.1.145:8080";
var OUTPUT = 1;  // Which output to control
var currentInput = 1;
var maxInputs = 8;

// Get initial state on startup
getStatus();

buttonManager.on("buttonSingleOrDoubleClickOrHold", function(obj) {
    var clickType = obj.isSingleClick ? "single" : obj.isDoubleClick ? "double" : "hold";
    
    if (clickType === "single") {
        // Next input
        currentInput = (currentInput % maxInputs) + 1;
        setInput(currentInput);
    } else if (clickType === "double") {
        // Previous input
        currentInput = currentInput > 1 ? currentInput - 1 : maxInputs;
        setInput(currentInput);
    } else if (clickType === "hold") {
        // Go to input 1 (favorite)
        currentInput = 1;
        setInput(1);
    }
});

function setInput(input) {
    http.makeRequest({
        url: API_BASE + "/api/output/" + OUTPUT + "/source/" + input,
        method: "POST"
    }, function(err, res) {
        console.log(err ? "Switch failed" : "Switched to input " + input);
    });
}

function getStatus() {
    http.makeRequest({
        url: API_BASE + "/api/status",
        method: "GET"
    }, function(err, res) {
        if (!err && res.statusCode === 200) {
            var data = JSON.parse(res.content);
            currentInput = data.outputs[OUTPUT - 1].source;
            console.log("Current input: " + currentInput);
        }
    });
}

console.log("OREI Matrix Input Cycler loaded");
```

### SDK Example: Zone Controller

Control multiple outputs as a zone:

```javascript
// OREI Matrix Zone Controller
// Controls Living Room (outputs 1 & 2) as a single zone

var buttonManager = require("buttons");
var http = require("http");

var API_BASE = "http://192.168.1.145:8080";
var ZONE_OUTPUTS = [1, 2];  // Living room TV and soundbar

var profiles = {
    "single": "living-room-tv",
    "double": "living-room-gaming", 
    "hold": null  // Power off
};

buttonManager.on("buttonSingleOrDoubleClickOrHold", function(obj) {
    var clickType = obj.isSingleClick ? "single" : obj.isDoubleClick ? "double" : "hold";
    
    if (clickType === "hold") {
        // Power off the zone
        powerOffZone();
    } else {
        // Recall profile
        var profile = profiles[clickType];
        if (profile) {
            recallProfile(profile);
        }
    }
});

function recallProfile(profileId) {
    http.makeRequest({
        url: API_BASE + "/api/profile/" + profileId + "/recall",
        method: "POST"
    }, function(err, res) {
        console.log(err ? "Profile failed" : "Zone activated: " + profileId);
    });
}

function powerOffZone() {
    // Send standby to each output in zone
    ZONE_OUTPUTS.forEach(function(output) {
        http.makeRequest({
            url: API_BASE + "/api/cec/output/" + output + "/standby",
            method: "POST"
        }, function(err) {
            console.log(err ? "Standby failed on output " + output : "Output " + output + " off");
        });
    });
}

console.log("Living Room Zone Controller loaded");
```

### SDK Example: Flic Twist Rotation Handler

Handle Twist rotations for smooth input cycling:

```javascript
// OREI Matrix Flic Twist Handler

var buttonManager = require("buttons");
var http = require("http");

var API_BASE = "http://192.168.1.145:8080";
var OUTPUT = 1;

buttonManager.on("buttonUpOrDown", function(obj) {
    // Handle button press/release
    if (obj.isUp === false) {
        // Button pressed - could trigger a confirmation or default action
        console.log("Twist pressed");
    }
});

buttonManager.on("buttonSingleOrDoubleClickOrHold", function(obj) {
    if (obj.isSingleClick) {
        // Single press - recall favorite profile
        recallProfile("default");
    } else if (obj.isDoubleClick) {
        // Double press - toggle power
        http.makeRequest({
            url: API_BASE + "/api/cec/output/" + OUTPUT + "/power_toggle",
            method: "POST"
        }, function() {});
    }
});

// For Flic Twist rotation events
buttonManager.on("buttonRotate", function(obj) {
    var direction = obj.direction;  // 1 = clockwise, -1 = counter-clockwise
    
    if (direction > 0) {
        nextInput();
    } else {
        previousInput();
    }
});

function nextInput() {
    http.makeRequest({
        url: API_BASE + "/api/input/next?output=" + OUTPUT,
        method: "POST"
    }, function(err) {
        console.log(err ? "Next failed" : "Next input");
    });
}

function previousInput() {
    http.makeRequest({
        url: API_BASE + "/api/input/previous?output=" + OUTPUT,
        method: "POST"
    }, function(err) {
        console.log(err ? "Previous failed" : "Previous input");
    });
}

function recallProfile(id) {
    http.makeRequest({
        url: API_BASE + "/api/profile/" + id + "/recall",
        method: "POST"
    }, function() {});
}

console.log("Flic Twist Handler loaded");
```

### Deploying SDK Modules

1. Save your module in the Flic Hub IDE
2. Assign buttons to the module
3. The module runs locally on the Hub (faster response)
4. Monitor logs in the IDE for debugging

---

## Troubleshooting

### Button press has no effect
1. Check that the Docker container is running:
   ```bash
   docker ps | grep orei
   ```
2. Test API directly:
   ```bash
   curl http://192.168.1.145:8080/api/status
   ```
3. Verify Flic Hub is on the same network as Docker host
4. Check Flic app shows button as "connected"
5. Check Docker logs:
   ```bash
   docker logs orei-matrix-integration
   ```

### Slow response
- The API should respond in under 1 second
- Check network connectivity between Flic Hub and Docker host
- Verify OREI Matrix is responding:
  ```bash
  curl -k https://192.168.1.100/cgi-bin/instr -d '{"comhead":"get system state"}'
  ```
- Check if matrix is powered on

### CEC command doesn't work
- Not all devices support all CEC commands
- PS3/PS4 have limited CEC support
- Older devices may not support CEC at all
- Try `power_on`/`power_off` first to test CEC connectivity
- Some TVs require CEC to be enabled in settings (often called "HDMI-CEC", "Anynet+", "Bravia Sync", etc.)

### Input cycling not working
- Ensure `?output=N` parameter is included in URL
- Verify output number is valid (1-8)
- Check matrix status to see current routing

## API Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 500 | Matrix communication error |

---

*Last updated: REST API v2.3.0*
