# Implementation Plan: NounProject Icon Tool

## Overview

A dual-interface tool (CLI + Web) for searching and bulk downloading icons from The Noun Project via the Shaper Studio proxy API, with optional proxy rotation for IP anonymization.

---

## Phase 1: Core Library (Node.js) ⏱️ 2-3 hours

### API Client Module

```
lib/
├── api-client.js      # Shaper API wrapper
├── proxy-pool.js      # Proxy rotation manager
├── download-queue.js  # Concurrent download handler
└── catalog.js         # Metadata & caching
```

**Features:**

- [x] Search icons with pagination
- [ ] Proxy support (HTTP/SOCKS5)
- [ ] Proxy rotation strategies (round-robin, random, least-used)
- [ ] Rate limiting & retry logic
- [ ] Metadata caching (SQLite)

---

## Phase 2: CLI Tool ⏱️ 2-3 hours

```bash
npicon search "playstation" --limit 50 --style line
npicon download --ids 8150530,7448289 --output ./icons
npicon scrape --terms "tv,gaming" --limit 100 --download
npicon config proxy --add socks5://user:pass@host:port
npicon config proxy --rotate round-robin
npicon stats  # Show usage statistics
```

**Technology:** Node.js + Commander.js

---

## Phase 3: Web UI ⏱️ 3-4 hours

### Backend (Express.js)

```
web/
├── server.js          # Express entry point
├── routes/
│   ├── search.js      # Search API proxy
│   ├── download.js    # Download management
│   └── settings.js    # Configuration
└── websocket.js       # Real-time progress
```

### Frontend (Vanilla JS)

```
web/public/
├── index.html
├── css/
│   └── styles.css
└── js/
    ├── app.js
    ├── search.js
    ├── download-queue.js
    └── settings.js
```

**Pages:**
| Page | Features |
|------|----------|
| Search | Real-time search, style filters, grid results |
| Queue | Download progress, pause/resume |
| Catalog | Browse saved icons |
| Settings | Proxy config, rate limits |

---

## Phase 4: Proxy Integration ⏱️ 2 hours

### PIA SOCKS5 Proxies

```javascript
const PIA_SERVERS = [
  "us-california.privacy.network:1080",
  "us-newyorkcity.privacy.network:1080",
  "us-chicago.privacy.network:1080",
  // ... 50+ locations
];

// Authentication
`socks5://${PIA_USER}:${PIA_PASS}@${server}`;
```

### Rotation Strategies

| Strategy    | Description                          |
| ----------- | ------------------------------------ |
| Round-robin | Cycle through proxies in order       |
| Random      | Random proxy per request             |
| Least-used  | Prefer proxies with lowest hit count |
| Sticky      | Same proxy for session duration      |

### Configuration

```json
// config/proxies.json
{
  "enabled": true,
  "strategy": "round-robin",
  "pia": {
    "username": "pXXXXXXXX",
    "password": "...",
    "servers": ["us-california", "us-newyorkcity"]
  },
  "custom": ["socks5://user:pass@proxy1.example.com:1080"]
}
```

---

## File Structure

```
noun-project-tool/
├── README.md
├── package.json
├── cli/
│   ├── index.js           # CLI entry point
│   └── commands/
│       ├── search.js
│       ├── download.js
│       ├── scrape.js
│       └── config.js
├── lib/
│   ├── api-client.js
│   ├── proxy-pool.js
│   ├── download-queue.js
│   └── catalog.js
├── web/
│   ├── server.js
│   ├── routes/
│   └── public/
├── scripts/
│   └── scrape-shaper-icons.ps1  # Legacy PowerShell
├── docs/
│   ├── api-reference.md
│   ├── usage-tracking.md
│   └── implementation-plan.md
├── config/
│   └── proxies.json.example
└── data/
    ├── catalog.db          # SQLite metadata
    └── icons/              # Downloaded SVGs
```

---

## Technology Stack

| Component     | Technology                           |
| ------------- | ------------------------------------ |
| Runtime       | Node.js 18+                          |
| CLI Framework | Commander.js                         |
| Web Server    | Express.js                           |
| WebSocket     | ws                                   |
| Proxy         | socks-proxy-agent, https-proxy-agent |
| Queue         | p-queue                              |
| Database      | better-sqlite3                       |
| HTTP Client   | node-fetch / axios                   |

---

## API Cost Analysis

| Action            | API Calls | Downloads |
| ----------------- | --------- | --------- |
| Search 100 icons  | 1         | 0         |
| Paginate 10 pages | 10        | 0         |
| Download 100 SVGs | 0         | 100       |

**Monthly Budget (400K calls):**

- 10 proxies × 10K calls each = 100K safe budget
- At 100 icons/call = 10M potential icons

---

## Security Considerations

- Store proxy credentials in environment variables
- Never log full proxy URLs (mask passwords)
- Rate limit to avoid triggering abuse detection
- Respect CC-BY licensing requirements

---

## Next Steps

1. [ ] Initialize Node.js project with dependencies
2. [ ] Implement core API client with proxy support
3. [ ] Build CLI commands
4. [ ] Create web interface
5. [ ] Test with PIA proxy rotation
