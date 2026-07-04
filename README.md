# 8x8 HDMI Matrix Hub

> A unified API bridge for controlling 8x8 HDMI Matrix switches from Unfolded Circle Remote 3, Flic smart buttons, Home Assistant, and more.

## 🔌 Compatible Devices

This integration supports **8x8 HDMI 2.1 matrix switches based on the HDCVT HDP-MXC88A platform**. These switches are sold under multiple brand names but share identical hardware, firmware, and control protocols—making them fully interchangeable from a software perspective.

### Why So Many Brands?

The **HDCVT HDP-MXC88A** is an OEM (Original Equipment Manufacturer) product that is white-labeled and sold by various AV equipment companies. This means:

- ✅ **Same hardware** - Identical internal components and build
- ✅ **Same firmware** - Same web interface and control protocol
- ✅ **Same API** - HTTP/Telnet commands work across all brands
- ✅ **Same features** - 8K60Hz, 4K120Hz, HDMI 2.1, HDCP 2.3, Dolby Vision, etc.

### Supported Models

| Brand                  | Model         | Product Page                                                                                                                              | Status        |
| ---------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| **OREI**               | BK-808        | [orei.com/bk-808](https://orei.com/products/8k-8x8-hdmi-matrix-switcher-4k-120hz-hdcp-2-3-hdr-edid-dolby-vision-atmos-downscaling-bk-808) | ✅ **Tested** |
| HDCVT (OEM)            | HDP-MXC88A    | [hdcvt.com](https://www.hdcvt.com/HDMIMatrix/328.html)                                                                 | 🔲 Untested   |
| Simplified MFG         | M88-8K        | [simplifiedmfg.com](https://www.simplifiedmfg.com/simplified-products/m88-8k)                                                                            | 🔲 Untested   |
| BZBGEAR                | BG-8K-88MA    | [bzbgear.com](https://bzbgear.com/product/bg-8k-88ma-8x8-8k-uhd-hdmi-2-1-matrix-switcher-with-auto-downscaling-audio-de-embedding-8k60-4k120-and-vrr-fva-allm-support/)             | 🔲 Untested   |
| WolfPack (HDTV Supply) | HDTVHDPMXC88A | [hdtvsupply.com](https://www.hdtvsupply.com/wolfpack-8k-60-hz-8x8-hdmi-matrix-switch.html)                                                               | 🔲 Untested   |
| A-NeuVideo             | ANI-8-8K60-S  | [a-neuvideo.com](https://www.a-neuvideo.com/shop/product_info.php?products_id=269)                                                                            | 🔲 Untested   |

> [!NOTE]
> If you have one of the untested models and can confirm compatibility, please [open an issue](../../issues) to help us update this list!

### Hardware Requirements

- HDMI 2.1 8x8 Matrix Switch (one of the compatible models above)
- Network connectivity (HTTPS on port 443)
- Control interface: Web GUI, RS-232, or TCP/IP

## 🎯 Features

### ✅ Implemented

- **Unfolded Circle Remote 3 Integration**
  - 8 preset buttons with dynamic names from matrix
  - Matrix remote entity with preset selection UI
  - CEC control for all 8 inputs (navigation, playback, power)
  - Per-input CEC remote entities
  - Fast reconnection via static driver URL

- **REST API (v2.10.0)** ✅
  - Full matrix control via HTTP endpoints
  - WebSocket for real-time status updates
  - Rate limiting and CORS support
  - Comprehensive error handling

- **Advanced Output Control**
  - HDCP mode selection (1.4, 2.2, follow sink/source)
  - HDR mode (passthrough, HDR→SDR, auto)
  - Scaler settings (4K/8K downscaling)
  - ARC control per output
  - Audio mute per output

- **EDID Management**
  - Per-input EDID configuration
  - Copy EDID from connected displays
  - Support for 4K60 HDR, 8K, Atmos

- **External Audio Routing**
  - Independent audio matrix control
  - Bind to input/output or matrix mode
  - Per-output audio source selection

- **Profiles (Activity-Based Routing)**
  - Save named routing configurations
  - Include HDR/HDCP/audio settings, CEC macros, and power automation
  - Recall profiles with single command
  - Unlimited profiles (vs. 8 hardware presets)
  - Backward compatible with legacy "Scenes" terminology

- **Docker Deployment**
  - Containerized for easy deployment
  - Persistent configuration across restarts
  - Health checks and auto-restart

- **Flic Smart Button Integration**
  - Internet Request template support for Flic Original / Flic 2 (single/double clicks, holds)
  - Flic Duo zone-based multi-room button and profile mapping
  - Flic Twist rotation-to-cycling HDMI inputs mapping (`/api/input/next` and `/api/input/previous`)
  - Flic Twist press actions for volume, CEC, and mute controls
  - Pre-built Flic Hub SDK Javascript templates for in-hub custom modules

- **CEC Macro System**
  - Custom multi-step CEC command sequences (power on/off, volume, inputs, delays)
  - Test/dry-run capabilities via API
  - Integration with Profiles for room-level automated startup/shutdown sequences


- **Home Assistant Custom HACS Component**
  - UI-based config flow (setup via IP address & port)
  - Output source routing `select` entities mapping to custom input names
  - Switch controls for matrix power, audio mute, and output stream enable/disable
  - Button controls to recall presets 1-8 and reboot the device
  - Binary sensors for input active video signals and output display connection status
  - Custom native service integrations (`recall_preset`, `switch_input`, `send_cec_command`)

### 🔲 Coming Soon

- Alexa voice control (via HA)
- Flic hardware validation (pending hardware)
- OpenAPI 3.0 specification & Swagger UI integration
- Automated scheduling engine (cron-like profile triggers)
- Outgoing webhook support and MQTT broker integration


## 📚 Documentation

| Document                                       | Description                           |
| ---------------------------------------------- | ------------------------------------- |
| [Project Roadmap](docs/PROJECT_ROADMAP.md)     | Development phases, progress tracking |
| [API Reference](docs/API_REFERENCE.md)         | REST API v2.7.0 documentation         |
| [Home Assistant](docs/HOME_ASSISTANT.md)       | HA integration guide with examples    |
| [OREI API Commands](docs/OREI_API_COMMANDS.md) | Matrix protocol reference             |
| [Flic Setup](docs/FLIC_SETUP.md)               | Flic button configuration             |

## 🚀 Quick Start

### Docker (Recommended)

```bash
# Full mode - UC integration + REST API + Web UI
docker-compose up -d
docker logs -f hdmi-matrix-hub
```

#### Deployment Modes

| Mode         | Command                                | Use Case                        |
| ------------ | -------------------------------------- | ------------------------------- |
| **Full**     | `docker-compose up`                    | UC Remote + API + Web UI        |
| **API-only** | `docker-compose --profile api-only up` | HA/MQTT without UC dependencies |

### Manual Installation

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows

# Full mode (with UC Remote support)
pip install -r requirements-uc.txt
python run.py

# API-only mode (no UC dependencies)
pip install -r requirements.txt
UC_ENABLED=false python run.py
```

### Environment Variables

| Variable        | Default         | Description                                      |
| --------------- | --------------- | ------------------------------------------------ |
| `MATRIX_HOST`   | `192.168.0.100` | Matrix IP address (canonical name)                |
| `MATRIX_DATA_DIR` | _(none)_       | Data directory for profiles, macros, settings      |
| `API_PORT`      | `8080`          | REST API port                                    |
| `UC_ENABLED`    | `true`          | Enable UC integration                            |
| `WEBUI_ENABLED` | `true`          | Enable Web UI                                    |
| `LOG_LEVEL`     | `INFO`          | Logging verbosity                                |

> **Note**: `OREI_HOST` and `OREI_API_PORT` are deprecated. Use `MATRIX_HOST` and `API_PORT` instead.

## 📁 Project Structure

```
├── src/
│   ├── driver.py              # Main UC integration driver
│   ├── orei_matrix.py         # Matrix control library
│   ├── telnet_client.py       # Async Telnet client (CEC, cable detection)
│   ├── config.py              # Configuration management
│   ├── scene_manager.py       # Scene/profile persistence
│   ├── scene_execution.py     # Scene execution engine
│   ├── cec_macros.py          # CEC macro definitions
│   ├── cec_commands.py        # CEC byte-level protocol
│   ├── cec_resolver.py        # CEC address resolution
│   ├── system_shortcuts.py    # Quick-action shortcuts
│   ├── dashboard_layout.py    # Dashboard card layout
│   ├── persistence.py         # Data directory resolution
│   ├── password.py            # PIN-based passcode hashing
│   ├── _file_io.py           # File I/O utilities
│   ├── _task_supervisor.py   # Task supervision and error handling
│   ├── _telnet_proto.py      # Telnet protocol implementation
│   ├── rest_api/              # REST API server (22 modules)
│   │   ├── app.py             # aiohttp application factory
│   │   ├── control.py         # Routing and power endpoints
│   │   ├── outputs.py         # Per-output settings (HDCP, HDR, EDID)
│   │   ├── cec.py             # CEC command endpoints
│   │   ├── macros.py          # CEC macro CRUD and execution
│   │   ├── profiles.py        # Profile management
│   │   ├── scenes.py          # Scene API (v1, backward compat)
│   │   ├── scenes_v2.py       # Scene API (v2, Phase 8)
│   │   ├── websocket.py       # WebSocket broadcast
│   │   └── ...                # (14 more modules)
│   └── integrations/          # Modular integration modules
│       └── unfolded_circle/   # UC Remote integration
│           ├── api_client.py  # REST API client
│           ├── entities.py    # UC entity factories
│           └── adapter.py     # OreiMatrix adapter
├── custom_components/         # Home Assistant HACS component
│   └── orei_matrix/
├── web/                       # Web UI dashboard
├── docs/                      # Documentation
├── tests/                     # Test suite (24 files)
├── run.py                     # Main entry point
├── run_server.py              # Standalone API server
├── Dockerfile                 # Multi-stage build
├── docker-compose.yml         # Deployment profiles
├── requirements.txt           # Core dependencies
└── requirements-uc.txt        # UC-specific dependencies
```

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────┐
│ Remote 3        │────▶│                      │────▶│             │
│ (WebSocket:9095)│     │   Integration Hub    │     │ OREI Matrix │
├─────────────────┤     │                      │     │ (HTTPS:443) │
│ Flic Buttons    │────▶│  ┌────────────────┐  │     │             │
│ (REST:8080)     │     │  │ orei_matrix.py │  │     │  - Presets  │
├─────────────────┤     │  │ (Control Lib)  │  │     │  - Routing  │
│ Home Assistant  │────▶│  └────────────────┘  │     │  - CEC      │
│ (REST:8080)     │     │                      │     │             │
└─────────────────┘     └──────────────────────┘     └─────────────┘
```

## 📡 Ports

| Port | Protocol  | Purpose                      |
| ---- | --------- | ---------------------------- |
| 9095 | WebSocket | Unfolded Circle integration  |
| 8080 | HTTP      | REST API (Flic, HA, scripts) |

---

## Original Setup Instructions

### Prerequisites

- Unfolded Circle Remote Two or Remote 3 (optional, for UC integration)
- Compatible 8x8 HDMI Matrix (see [Compatible Devices](#-compatible-devices) above)
- Matrix and integration hub on the same network
- Python 3.11 or newer (for local development)

## Installation

### External Integration (Development/Testing)

1. Clone or download this repository to your computer:

   ```bash
   git clone <repository-url>
   cd unfoldedcircle-orei-hdmi-matrix-integration
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

3. Run the integration driver:

   ```bash
   python src/driver.py
   ```

4. On your Remote 3:
   - Go to **Settings** → **Integrations**
   - Add a new integration
   - Select **OREI HDMI Matrix**
   - Enter the IP address of your OREI BK-808 (default: 192.168.0.100)
   - Enter the HTTPS port (default: 443)

## Configuration

### Finding Your Matrix IP Address

1. On the OREI BK-808 front panel, navigate to **IP INFO**
2. Note the IP address displayed (e.g., 192.168.0.100)
3. Use this IP address during integration setup

### Preset Names

The integration automatically queries your matrix for input device names. If you've named your inputs on the matrix (e.g., "PS5", "AppleTV", "Computer"), these names will appear on the preset buttons in the Remote 3 UI.

To change preset names:

1. Use the OREI matrix's web interface or front panel to rename inputs
2. Restart the integration driver or reconfigure the integration
3. New names will be fetched automatically

## Usage

### Using the Remote Entity

1. Add the **OREI Matrix** remote entity to an activity
2. The touchscreen will display 8 preset buttons with device names
3. Tap any button to instantly recall that preset

### Using Preset Buttons

1. Add individual **Preset X** button entities to your activities
2. Press a button to recall the corresponding preset
3. Combine with other entities for complex automations

## Technical Details

### Connection Protocol

- **Primary Protocol**: HTTPS (JSON over HTTP POST) — port 443
- **Secondary Protocol**: Telnet (port 23) — for CEC commands and cable detection
- **Endpoint**: `/cgi-bin/instr`
- **Authentication**: Username `Admin`, Password `admin` (defaults, configurable via `OREI_USER`/`OREI_PASSWORD` env vars)

### Supported Commands

The matrix uses JSON commands over HTTPS:

- **Login**: `{"comhead":"login","user":"Admin","password":"admin"}`
- **Recall Preset**: `{"comhead":"preset set","language":0,"index":<1-8>}`
- **Get Video Status**: `{"comhead":"get video status","language":0}`
- **Switch Input**: `{"comhead":"video switch","language":0,"source":[<output>,<input>]}`
- **Power On/Off**: `{"comhead":"set poweronoff","language":0,"power":<0|1>}`
- **EDID Management**: Per-input EDID configuration
- **HDCP/HDR Control**: Per-output HDCP mode, HDR passthrough/conversion
- **Audio**: External audio matrix routing, per-output mute
- **CEC**: Consumer Electronics Control via Telnet or HTTP fallback

### Entity Types

The integration creates:

1. **Remote Entity** (`remote.orei_matrix`)
   - Type: Remote
   - Features: Send commands, preset selection UI
   - State: ON/UNAVAILABLE

2. **Button Entities** (`button.preset_1` through `button.preset_8`)
   - Type: Button
   - Action: Recall corresponding preset

## Troubleshooting

### Integration Shows "Unavailable"

1. Verify the matrix IP address in the IP INFO menu
2. Ensure the matrix and Remote are on the same network
3. Check that port 443 is accessible
4. Try pinging the matrix IP from your network
5. Restart both the matrix and the integration

### Scene Not Changing

**Problem**: Button press doesn't change the scene

**Solutions**:

1. Verify scenes are configured on the matrix
2. Check the integration logs for error messages
3. Ensure the matrix is powered on
4. Try manually recalling the scene from the matrix front panel
5. Reconnect the integration

### Logs

To view integration logs:

```bash
# If running as external integration
python3 driver.py
```

Logs will show connection status, commands sent, and any errors.

## Advanced Usage

### Creating Macros

Combine scene recall with other actions:

1. In the Remote UI, create a new macro
2. Add a "OREI Matrix Scene X" button press
3. Add other commands (e.g., turn on TV, switch receiver input)
4. Assign to a custom button

### Activity Integration

Include the OREI Matrix in activities:

1. Create a new activity (e.g., "Watch Movies")
2. Add the OREI Matrix remote entity
3. Set a default scene to load when starting the activity
4. Configure scene changes for different activity states

## Development

### Project Structure

```
unfoldedcircle-orei-hdmi-matrix-integration/
├── driver.py           # Main integration driver
├── driver.json         # Driver metadata and configuration
├── orei_matrix.py      # OREI Matrix control library
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Adding Features

To add more functionality:

1. Extend the `OreiMatrix` class in `orei_matrix.py`
2. Add new command methods following the existing pattern
3. Update the driver to expose new commands

### Testing

Test the integration:

```bash
# Run the driver with debug logging
python3 driver.py
```

Connect your Remote 3 and test scene recall functionality.

## Command Reference

### OREI BK-808 Command Format

Based on the user manual and common OREI matrix protocols:

| Function               | Command Format      | Example             |
| ---------------------- | ------------------- | ------------------- |
| Recall Scene           | `s recall scene X!` | `s recall scene 1!` |
| Save Scene             | `s save scene X!`   | `s save scene 3!`   |
| Route Input to Output  | `s in X out Y!`     | `s in 1 out 5!`     |
| All Outputs Same Input | `s in X out all!`   | `s in 2 out all!`   |

**Note**: Commands are case-sensitive and must end with `!`

## FAQ

**Q: Can I control individual input/output routing?**  
A: Yes! Use `POST /api/output/{output}/source` to route any input to any output, or `POST /api/switch` to switch all outputs.

**Q: How many scenes can I save?**  
A: 8 hardware presets, plus unlimited software profiles via the `/api/profiles` API with full routing, CEC macros, and power automation.

**Q: Can I use RS-232 instead of TCP/IP?**  
A: The integration uses TCP/IP. For RS-232, connect the Remote 3 dock's 3.5mm port to the matrix and use the generic RS-232 integration.

**Q: Will this work with other OREI matrix models?**  
A: This integration is designed for the BK-808. Other models may use different commands.

**Q: Can I rename the scenes?**  
A: Currently, scenes are labeled 1-8. Custom naming can be added in a future update.

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the OREI BK-808 user manual
3. Check Unfolded Circle community forums
4. Review integration logs for error messages

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This integration is provided as-is under the Mozilla Public License Version 2.0.

## Credits

- Based on the [Unfolded Circle Integration API](https://github.com/unfoldedcircle/integration-python-library)
- Inspired by the [Denon AVR integration](https://github.com/unfoldedcircle/integration-denonavr)
- Created for the Unfolded Circle Remote Two/3 community

## Version History

### v2.10.0 (Current)
- Profiles with CEC macro support and power automation
- CEC Macros — multi-step command sequences with delays
- Device Settings — persistent per-device names, icons, colors
- Themes and UI Preferences persistence
- Home Assistant HACS component with config flow
- Enhanced CEC capabilities API
- Dashboard layout management (Phase 7)
- Security hardening — SSRF protection, TLS verification, non-root Docker

### v2.9.0
- CEC Macros system — save and execute multi-step CEC commands
- Macro favorites and dashboard visibility

### v2.8.0
- Web UI dashboard with real-time WebSocket updates
- `/api/info` endpoint, debug panel

### v2.7.0
- Scenes (activity-based routing configurations)
- Scene CEC auto-resolution

### v2.6.0
- External audio matrix routing
- Independent audio source selection per output

### v2.5.0
- EDID management per input
- LCD timeout settings

### v2.0.0
- Initial REST API release
- Flic smart button support
- WebSocket real-time status updates

## Future Enhancements

Planned features for future releases:

- [ ] Alexa voice control (via Home Assistant)
- [ ] OpenAPI 3.0 specification & Swagger UI
- [ ] Automated scheduling engine (cron-like profile triggers)
- [ ] MQTT broker integration
- [ ] Outgoing webhook support

---

**Enjoy your OREI BK-808 HDMI Matrix integration!** 🎬
