# API Usage Tracking Analysis

## Summary

The Shaper Studio icon API tracks usage globally with a **400,000 request/month** limit.

> **Key Finding**: Only search queries count as API calls. SVG downloads are FREE.

---

## What Counts as an API Call?

| Action        | Domain                      | Counts? | Cost |
| ------------- | --------------------------- | ------- | ---- |
| Search query  | `icons.shapertools.com`     | ✅ YES  | +1   |
| SVG download  | `static.thenounproject.com` | ❌ NO   | 0    |
| PNG thumbnail | `static.thenounproject.com` | ❌ NO   | 0    |
| Pagination    | `icons.shapertools.com`     | ✅ YES  | +1   |

---

## Test Results (2026-01-29)

### Test 1: Search Query Count

```
Search with limit=5:  +1 API call
Search with limit=50: +1 API call
```

**Conclusion**: The `limit` parameter does NOT affect API call count.

### Test 2: SVG Downloads

```
Before 3 SVG downloads: 54789
After 3 SVG downloads:  54789 (unchanged)
After check query:      54790 (+1 for the check)
```

**Conclusion**: SVG downloads do NOT count against the API limit.

---

## Usage Tracking Characteristics

| Characteristic        | Observation                                     |
| --------------------- | ----------------------------------------------- |
| **Tracking scope**    | Global (not per-user or per-account)            |
| **Authentication**    | None required (works without cookies or tokens) |
| **Origin header**     | Ignored (works with any origin or none)         |
| **Reset period**      | Monthly                                         |
| **Real-time updates** | Yes (each response shows current count)         |

---

## Optimization Strategies

### Maximize Efficiency

| Strategy                             | Impact                    |
| ------------------------------------ | ------------------------- |
| Use `limit=100`                      | Best results per API call |
| Cache search results                 | Avoid redundant queries   |
| Download all SVGs from single search | Downloads are free        |
| Use pagination wisely                | Each page costs 1 call    |

### Cost Comparison

| Goal: Get 1,000 icons        | API Calls | Downloads |
| ---------------------------- | --------- | --------- |
| ❌ 100 searches × 10 results | 100       | 1,000     |
| ✅ 10 searches × 100 results | 10        | 1,000     |

### Monthly Budget Planning

| Usage Pattern               | API Calls/Month | Remaining |
| --------------------------- | --------------- | --------- |
| Light (research)            | 1,000           | 399,000   |
| Moderate (regular scraping) | 10,000          | 390,000   |
| Heavy (full library scan)   | 50,000          | 350,000   |

---

## Response Structure

Every API response includes usage data:

```json
{
  "icons": [...],
  "usage_limits": {
    "monthly": {
      "limit": 400000,
      "usage": 54791
    }
  }
}
```

---

## Practical Example

To download 5,000 icons efficiently:

```powershell
# 50 API calls (not 5,000!)
$terms = @("tv", "gaming", "computer", "audio", "video")  # 5 terms
$terms | ForEach-Object {
    # 10 pages × 100 icons = 1,000 icons per term
    # 10 API calls per term
    for ($page = 0; $page -lt 10; $page++) {
        $results = Search-Icons -Query $_ -Limit 100 -Page $page
        $results.icons | Download-Svg  # FREE!
    }
}

# Total: 50 API calls + 5,000 free downloads
```

---

## Monitoring

Track your usage in real-time:

```powershell
$r = Invoke-RestMethod "https://icons.shapertools.com/search?iconquery=check&limit=1"
$used = $r.usage_limits.monthly.usage
$limit = $r.usage_limits.monthly.limit
Write-Host "Usage: $used / $limit ($([math]::Round($used/$limit*100, 1))%)"
```
