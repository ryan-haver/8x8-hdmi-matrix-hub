# Shaper Studio / NounProject API Reference

## Overview

Shaper Studio provides a proxy API to The Noun Project's icon library. This API is **publicly accessible** and requires no authentication.

## Base URL

```
https://icons.shapertools.com
```

## Endpoints

### Search Icons

```http
GET /search?iconquery={query}&limit={count}&next_page={cursor}
```

#### Parameters

| Parameter   | Type    | Required | Default | Description                              |
| ----------- | ------- | -------- | ------- | ---------------------------------------- |
| `iconquery` | string  | Yes      | -       | Search term (e.g., "playstation", "tv")  |
| `limit`     | integer | No       | 30      | Results per page (max 100)               |
| `next_page` | string  | No       | -       | Pagination cursor from previous response |

#### Headers

```http
Accept: application/json
```

> **Note**: The `Origin` header is optional. The API works with any origin or none.

#### Example Request

```bash
curl "https://icons.shapertools.com/search?iconquery=gaming&limit=10"
```

#### Response

```json
{
  "icons": [
    {
      "id": "8066803",
      "term": "Game",
      "attribution": "Game by Kael from Noun Project",
      "license_description": "creative-commons-attribution",
      "icon_url": "https://static.thenounproject.com/svg_clean/8066803.svg?Expires=...&Signature=...&Key-Pair-Id=...",
      "thumbnail_url": "https://static.thenounproject.com/png/8066803-200.png",
      "permalink": "/icon/game-8066803/",
      "tags": ["game", "gaming", "controller"],
      "styles": [{"style": "line", "line_weight": 10}],
      "collections": [...],
      "creator": {
        "name": "Kael",
        "username": "kael123",
        "permalink": "/creator/kael123/"
      }
    }
  ],
  "total": 82482,
  "generated_at": "2026-01-29 19:29:09.838233",
  "next_page": "31342E302C38303636383033",
  "usage_limits": {
    "monthly": {
      "limit": 400000,
      "usage": 54791
    }
  }
}
```

---

## Response Fields

### Top Level

| Field          | Type    | Description                        |
| -------------- | ------- | ---------------------------------- |
| `icons`        | array   | Array of icon objects              |
| `total`        | integer | Total matching icons for query     |
| `generated_at` | string  | Query timestamp (UTC)              |
| `next_page`    | string  | Pagination cursor (base64-encoded) |
| `usage_limits` | object  | API usage statistics               |

### Icon Object

| Field                 | Type   | Description                           |
| --------------------- | ------ | ------------------------------------- |
| `id`                  | string | Unique icon ID                        |
| `term`                | string | Primary search term                   |
| `attribution`         | string | Required CC-BY attribution text       |
| `license_description` | string | Always "creative-commons-attribution" |
| `icon_url`            | string | Signed URL to SVG file (time-limited) |
| `thumbnail_url`       | string | 200px PNG thumbnail URL               |
| `permalink`           | string | NounProject permalink                 |
| `tags`                | array  | Searchable tags                       |
| `styles`              | array  | Icon style info (line/solid, weight)  |
| `collections`         | array  | Collection memberships                |
| `creator`             | object | Creator info (name, username)         |

### Styles

Icons may have one of these styles:

| Style   | Description                                |
| ------- | ------------------------------------------ |
| `line`  | Outline/wireframe style with `line_weight` |
| `solid` | Filled/glyph style                         |

---

## Icon URLs

### SVG (Vector)

```
https://static.thenounproject.com/svg_clean/{id}.svg?Expires=...&Signature=...&Key-Pair-Id=...
```

- **Signed URLs** - Time-limited, typically valid for ~24 hours
- **CloudFront CDN** - Fast global delivery
- **No API call counted** - Downloads are free

### PNG Thumbnail

```
https://static.thenounproject.com/png/{id}-200.png
```

- 200x200 pixel preview
- Not signed (persistent URL)
- No API call counted

---

## Pagination

Use the `next_page` cursor for subsequent pages:

```bash
# First page
curl "https://icons.shapertools.com/search?iconquery=tv&limit=100"
# Response: { ..., "next_page": "31342E302C31303034303439" }

# Second page
curl "https://icons.shapertools.com/search?iconquery=tv&limit=100&next_page=31342E302C31303034303439"
```

---

## Rate Limits

| Metric        | Value                 |
| ------------- | --------------------- |
| Monthly limit | 400,000 requests      |
| Tracking      | Global (not per-user) |
| Reset         | Monthly               |

Check current usage in every response:

```json
"usage_limits": {
  "monthly": {
    "limit": 400000,
    "usage": 54791
  }
}
```

---

## Error Handling

| HTTP Code | Meaning                  |
| --------- | ------------------------ |
| 200       | Success                  |
| 400       | Invalid query parameters |
| 429       | Rate limit exceeded      |
| 500       | Server error             |

---

## Code Examples

### PowerShell

```powershell
$response = Invoke-RestMethod -Uri "https://icons.shapertools.com/search?iconquery=hdmi&limit=10"
$response.icons | ForEach-Object { Write-Host "$($_.id): $($_.term)" }
```

### JavaScript (Node.js)

```javascript
const response = await fetch(
  "https://icons.shapertools.com/search?iconquery=hdmi&limit=10",
);
const data = await response.json();
data.icons.forEach((icon) => console.log(`${icon.id}: ${icon.term}`));
```

### Python

```python
import requests
response = requests.get('https://icons.shapertools.com/search', params={'iconquery': 'hdmi', 'limit': 10})
for icon in response.json()['icons']:
    print(f"{icon['id']}: {icon['term']}")
```
