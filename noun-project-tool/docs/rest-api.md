# REST API Reference

The NounProject Icon Tool provides a REST API for external app integration.

## Base URL

```
http://localhost:3000/api
```

## Endpoints

### Health Check

```
GET /api/health
```

Returns `{ "status": "ok", "timestamp": "..." }`

---

### Search Icons

```
GET /api/search?q={query}&limit={n}&style={line|solid}&page={cursor}
```

| Param   | Required | Default | Description                |
| ------- | -------- | ------- | -------------------------- |
| `q`     | Yes      | -       | Search term                |
| `limit` | No       | 30      | Results per page (max 100) |
| `style` | No       | -       | Filter: "line" or "solid"  |
| `page`  | No       | -       | Pagination cursor          |

**Response:**

```json
{
  "success": true,
  "query": "gaming",
  "total": 82482,
  "count": 30,
  "nextPage": "abc123...",
  "usage": { "usage": 55000, "limit": 400000 },
  "icons": [{ "id": "...", "term": "...", "iconUrl": "...", ... }]
}
```

---

### Search & Save to Catalog

```
POST /api/search/save
Content-Type: application/json

{ "query": "hdmi", "limit": 50, "style": "line" }
```

---

### Get Catalog Icons

```
GET /api/catalog?q={search}&limit={n}&offset={n}&downloaded={true|false}
```

---

### Get Single Icon

```
GET /api/catalog/:id
```

---

### Queue Downloads

```
POST /api/download
Content-Type: application/json

{ "query": "gaming", "limit": 50, "outputDir": "./icons" }
// OR
{ "ids": ["123", "456"], "outputDir": "./icons" }
```

**Response:**

```json
{ "success": true, "jobId": "1234567890", "queued": 50 }
```

---

### Get Download Status

```
GET /api/download/:jobId
```

**Response:**

```json
{
  "success": true,
  "jobId": "...",
  "status": "running|completed",
  "progress": { "done": 25, "total": 50, "percent": 50 }
}
```

---

### Get Statistics

```
GET /api/stats
```

---

### Get API Usage

```
GET /api/usage
```

---

### Proxy Management

```
GET /api/proxy          # Get proxy status
POST /api/proxy         # Add proxy
  { "url": "socks5://..." }
  // OR
  { "pia": { "username": "...", "password": "..." } }
```

---

## WebSocket

Connect to `ws://localhost:3000/ws` for real-time download progress updates.

```javascript
const ws = new WebSocket("ws://localhost:3000/ws");
ws.onmessage = (e) => {
  const data = JSON.parse(e.data);
  if (data.type === "progress") {
    console.log(data.downloads); // [{ jobId, progress }]
  }
};
```

---

## CORS

All endpoints support CORS for browser-based integrations.
