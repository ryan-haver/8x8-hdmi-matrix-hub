# Docker Deployment Guide

## Quick Start

### Build and run locally:
```bash
# Build the Docker image
docker build -t uc-orei-hdmi-matrix .

# Run with host networking (required for mDNS discovery)
docker run -d \
  --name uc-orei-hdmi-matrix \
  --network host \
  --restart unless-stopped \
  -v $(pwd)/data:/data \
  uc-orei-hdmi-matrix
```

### Or use Docker Compose (recommended):
```bash
# Start the integration
docker-compose up -d

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down
```

## Deployment Options

### Option 1: Synology NAS (Docker Package)
1. Copy project files to your NAS
2. Open Docker package
3. Build image from Dockerfile or import
4. Create container with:
   - Network: Use same network as Docker host
   - Volume: `/data` → persistent storage location
5. The integration will auto-start on NAS boot

### Option 2: Raspberry Pi / Linux Server
```bash
# Clone or copy project
cd ~/uc-integrations/orei-hdmi-matrix

# Build and start
docker-compose up -d

# Enable Docker to start on boot
sudo systemctl enable docker
```

### Option 3: Portainer (Web UI management)
1. Install Portainer on your Docker host
2. Create a stack from the docker-compose.yml
3. Manage via web interface

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
