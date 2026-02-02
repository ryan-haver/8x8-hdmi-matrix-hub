# NounProject Icon Tool

A powerful CLI and Web tool for searching and downloading icons from The Noun Project via the Shaper Studio proxy API.

## Features

- 🔍 **Search** 6M+ icons from The Noun Project
- 📥 **Bulk download** SVGs with concurrent queue
- 🔒 **Proxy support** (PIA SOCKS5 + custom)
- 🔄 **Proxy rotation** (round-robin, random, least-used)
- 💾 **Local catalog** with SQLite metadata storage
- 🌐 **REST API** for external app integration
- 🖥️ **Web UI** with real-time progress

## Quick Start

```bash
# Install
cd noun-project-tool
npm install

# CLI - Search icons
node cli/index.js search "gaming" --limit 20

# CLI - Download icons
node cli/index.js download --query "hdmi" --limit 10 -o ./icons

# CLI - Bulk scrape
node cli/index.js scrape --terms "tv,gaming,projector" --download

# Web server
node web/server.js
# Open http://localhost:3000
```

## CLI Commands

```bash
npicon search <query>     # Search for icons
npicon download           # Download icons by query or ID
npicon scrape             # Bulk scrape by search terms
npicon stats              # Show catalog and API statistics
npicon config             # Manage proxy configuration
```

## REST API

The web server exposes a REST API for integration:

| Endpoint            | Method   | Description                |
| ------------------- | -------- | -------------------------- |
| `/api/search`       | GET      | Search icons               |
| `/api/search/save`  | POST     | Search and save to catalog |
| `/api/catalog`      | GET      | Query local catalog        |
| `/api/download`     | POST     | Queue downloads            |
| `/api/download/:id` | GET      | Get job status             |
| `/api/stats`        | GET      | Get statistics             |
| `/api/usage`        | GET      | Get API usage              |
| `/api/proxy`        | GET/POST | Manage proxies             |

See [docs/rest-api.md](docs/rest-api.md) for full documentation.

## Proxy Configuration

```bash
# Add PIA proxy
node cli/index.js config --pia username:password

# Add custom proxy
node cli/index.js config --add-proxy socks5://user:pass@host:1080

# Set rotation strategy
node cli/index.js config --strategy round-robin
```

## Documentation

- [API Reference](docs/api-reference.md) - Shaper Studio API details
- [Usage Tracking](docs/usage-tracking.md) - What counts as API calls
- [REST API](docs/rest-api.md) - Local server endpoints
- [Implementation Plan](docs/implementation-plan.md) - Architecture overview

## License

Icons from The Noun Project are **CC-BY licensed** - attribution required.
