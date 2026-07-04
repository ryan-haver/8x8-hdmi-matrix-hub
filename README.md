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

### 🔲 Coming Soon

- Home Assistant custom HACS component
- Alexa voice control (via HA)

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

| Variable        | Default         | Description           |
| --------------- | --------------- | --------------------- |
| `MATRIX_HOST`   | `192.168.0.100` | Matrix IP address     |
| `API_PORT`      | `8080`          | REST API port         |
| `UC_ENABLED`    | `true`          | Enable UC integration |
| `WEBUI_ENABLED` | `true`          | Enable Web UI         |
| `LOG_LEVEL`     | `INFO`          | Logging verbosity     |

## 📁 Project Structure

```
├── src/
│   ├── driver.py              # Main UC integration driver
│   ├── orei_matrix.py         # Matrix control library
│   ├── rest_api/              # REST API server
│   └── integrations/          # Modular integration modules
│       └── unfolded_circle/   # UC Remote integration
│           ├── api_client.py  # REST API client
│           ├── entities.py    # UC entity factories
│           └── adapter.py     # OreiMatrix adapter
├── web/                       # Web UI dashboard
├── docs/                      # Documentation
├── run.py                     # Main entry point
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

- **Protocol**: HTTPS (JSON over HTTP POST)
- **Default Port**: 443
- **Endpoint**: `/cgi-bin/instr`
- **Authentication**: Username `Admin`, Password `admin`

### Supported Commands

The OREI BK-808 uses JSON commands over HTTPS:

- **Login**: `{"comhead":"login","user":"Admin","password":"admin"}`
- **Recall Preset**: `{"comhead":"preset set","language":0,"index":<1-8>}`
- **Get Video Status**: `{"comhead":"get video status","language":0}`
- **Switch Input**: `{"comhead":"video switch","language":0,"source":[<output>,<input>]}`
- **Power On/Off**: `{"comhead":"set poweronoff","language":0,"power":<0|1>}`

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
A: The current version focuses on scene recall. Individual routing can be added in future versions.

**Q: How many scenes can I save?**  
A: The OREI BK-808 supports 8 preset scenes.

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

### v0.1.0 (2026-01-12)

- Initial release
- Scene recall functionality (1-8)
- TCP/IP control via Telnet
- Remote entity with touchscreen UI
- Individual scene button entities
- Basic connection management

## Future Enhancements

Planned features for future releases:

- [ ] Individual input/output routing control
- [ ] Scene save functionality from Remote
- [ ] Custom scene names
- [ ] Real-time status feedback
- [ ] EDID management
- [ ] CEC control integration
- [ ] Web GUI automation
- [ ] RS-232 control option

---

**Enjoy your OREI BK-808 HDMI Matrix integration!** 🎬
