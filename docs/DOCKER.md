# Docker Deployment Guide

## Quick Start

### Build and run locally:
```bash
# Build the Docker image
docker build -t uc-orei-hdmi-matrix .

# Run with host networking (required for mDNS discovery)
# The -v flag controls where on the HOST persistent state lives.
docker run -d \
  --name uc-orei-hdmi-matrix \
  --network host \
  --restart unless-stopped \
  -v /your/chosen/host/path:/data \
  -e MATRIX_DATA_DIR=/data \
  uc-orei-hdmi-matrix
```

### Or use Docker Compose (recommended):
```bash
# Start with the default persistent path (./data on the host)
docker-compose up -d

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down
```

## Persistent Storage Configuration

All user-addressable state — device settings, themes, UI preferences, scenes,
profiles, CEC macros, and driver state — is stored under `/data` inside the
container. You control where on the **host** this volume lives by setting the
`MATRIX_DATA_DIR` variable.

### Where each kind of state lives

| Path inside `/data`          | What it contains                                              |
| ---------------------------- | ------------------------------------------------------------- |
| `config_state.json`          | Matrix host / IP, driver state                                |
| `driver.lock`                | Single-instance lock file                                     |
| `device_settings.json`       | Per-input/output names, icons, and colors                     |
| `themes.json`                | Active theme preset and custom theme values                   |
| `ui_preferences.json`        | Pinned tabs and tab ordering in the Web UI                    |
| `config/cec_macros.json`     | User-defined CEC button macros                                |
| `config/profiles.json`       | Saved activity routing profiles                               |
| `config/scenes.json`         | Legacy scenes (kept for backward compatibility)               |

### Choosing a host path

There are three ways to set `MATRIX_DATA_DIR`:

1. **Inline environment variable** (one-off):

   ```bash
   MATRIX_DATA_DIR=/srv/matrix-config docker-compose up -d
   ```

2. **Shell export** (persists for the session):

   ```bash
   export MATRIX_DATA_DIR=/Volumes/nas/matrix
   docker-compose up -d
   ```

3. **`.env` file** in the project root (recommended for permanent setups):

   ```ini
   # .env
   MATRIX_DATA_DIR=/srv/matrix-config
   ```

   Docker Compose reads this automatically — no need to edit
   `docker-compose.yml`.

### Common deployment patterns

**Local development (default):**
```ini
# .env
MATRIX_DATA_DIR=./data
```
This stores state next to the `docker-compose.yml`. Easy to back up with `tar`.

**Network-attached storage (NAS):**
```ini
# .env
MATRIX_DATA_DIR=/Volumes/nas/matrix-config
```
State survives even if the Docker host fails. Use this for production.

**Synology / QNAP NAS via bind mount:**
```ini
# .env
MATRIX_DATA_DIR=/volume1/docker/matrix-config
```

**Unraid (using `/mnt/user`):**
```ini
# .env
MATRIX_DATA_DIR=/mnt/user/appdata/matrix-config
```

### Migrating from a previous version

Earlier versions hardcoded some files to a project-local `data/` directory.
On first start of the new version, the application automatically migrates
the following legacy files into the configured `MATRIX_DATA_DIR`:

- `device_settings.json`
- `themes.json`
- `ui_preferences.json`

The original files are left in place (copied, not moved) so you can verify
the migration succeeded before deleting them.

### Verifying your configuration

The REST API exposes the resolved storage layout at
`GET /api/system/storage` so you can confirm the container is using the
expected host path.

```bash
curl http://localhost:8080/api/system/storage
```

```json
{
  "data_dir": "/data",
  "config_dir": "/data/config",
  "matrix_data_dir_env": "/data",
  "uc_config_home_env": "/data"
}
```

## Deployment Options

### Option 1: Synology NAS (Docker Package)
1. Copy project files to your NAS
2. Open Docker package
3. Build image from Dockerfile or import
4. Create container with:
   - Network: Use same network as Docker host
   - Volume: `/data` → persistent storage location (your `MATRIX_DATA_DIR`)
5. Set the `MATRIX_DATA_DIR` environment variable to match
6. The integration will auto-start on NAS boot

### Option 2: Raspberry Pi / Linux Server
```bash
# Clone or copy project
cd ~/uc-integrations/orei-hdmi-matrix

# Set your persistent path
export MATRIX_DATA_DIR=/srv/matrix-config

# Build and start
docker-compose up -d

# Enable Docker to start on boot
sudo systemctl enable docker
```

### Option 3: Portainer (Web UI management)
1. Install Portainer on your Docker host
2. Create a stack from the docker-compose.yml
3. Add `MATRIX_DATA_DIR` under "Environment variables" in the stack config
4. Add a volume mount that points to the same host path
5. Manage via web interface

### Option 4: Home Assistant OS (if running HA)
Some users run a separate Docker host alongside HA, or use 
the SSH & Web Terminal add-on to run custom containers.

## Multi-Integration Setup

For running multiple Unfolded Circle integrations:

```
~/uc-integrations/
├── orei-hdmi-matrix/      # Port 9095
│   ├── Dockerfile
│   ├── driver.py
│   └── data/
├── denon-avr/             # Port 9096
│   ├── Dockerfile
│   ├── driver.py
│   └── data/
├── lg-tv/                 # Port 9097
│   └── ...
└── docker-compose.yml     # Orchestrates all integrations
```

Use `docker-compose.multi.yml` as a template for managing all 
integrations from a single compose file.

## Important: Network Mode

**Why `network_mode: host` is required:**

The Unfolded Circle Remote 3 discovers integrations via mDNS 
(multicast DNS) on your local network. Docker's default bridge 
networking isolates container network traffic, preventing mDNS 
packets from reaching the Remote 3.

Using `network_mode: host` allows the container to:
- Broadcast mDNS announcements on your LAN
- Be discovered by the Remote 3
- Receive incoming WebSocket connections from the Remote

**Limitation:** Each integration needs a unique port (9095, 9096, etc.) 
since they all share the host's network namespace.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UC_CONFIG_HOME` | `/data` | Directory for persistent config |
| `UC_DISABLE_MDNS_PUBLISH` | `false` | Disable mDNS if using static IP |
| `UC_INTEGRATION_INTERFACE` | `0.0.0.0` | Network interface to bind |
| `UC_INTEGRATION_HTTP_PORT` | `9095` | WebSocket server port |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## Troubleshooting

### Integration not discovered by Remote 3
- Ensure `network_mode: host` is set
- Check that port 9095 isn't blocked by firewall
- Verify mDNS/Bonjour is working on your network

### Container keeps restarting
```bash
# Check logs
docker logs uc-orei-hdmi-matrix

# Common issues:
# - Port already in use (another container or process)
# - mDNS name conflict (wait 30s after stopping old instance)
# - Configuration file corruption
```

### Reset configuration
```bash
# Remove saved config and restart
docker-compose down
rm data/config_state.json
docker-compose up -d
```

## Updates

To update the integration:

```bash
# Pull latest changes (if using git)
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```
