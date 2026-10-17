# Security Policy

This hub is software that runs on **your** network — on a Raspberry Pi, a mini PC or
a Docker host on your home or lab LAN. It exposes one HTTP port (**8080** by default:
REST API, web UI at `/ui`, kiosk at `/kiosk`) and, only when `UC_ENABLED=true`, one
WebSocket port (**9095**) for the Unfolded Circle Remote 3 integration.

There is no account system, no cloud service and no telemetry. Everything is
configured locally and stored in the data directory.

---

## Threat model: home and lab LAN

### Intended deployment

* A device you own, on a network you own, reachable from your own devices (phone,
  tablet, laptop, Flic button, Home Assistant).
* Trusted clients: the web UI in your browser, the kiosk tablet, the Home Assistant
  integration, the Flic integration, a Remote 3 you paired yourself.
* The OREI matrix itself is on the same LAN and is reached by the hub, not by you.

### What the two-level PIN system protects against

* **Accidental and casual changes on the LAN.** Another device, a guest, a script,
  or a mis-typed automation can switch inputs or recall presets, but cannot re-point
  the matrix host, change its credentials, edit EDID/HDCP/HDR/scaler settings, create
  or delete profiles and scenes, or reboot the hub — unless it holds an admin session.
* **Cross-site requests from a browser.** A page in another tab (or on another site
  the browser is logged in to) cannot drive the hub: mutating requests must be
  same-origin, must carry `Content-Type: application/json`, and are refused
  otherwise.
* **DNS rebinding.** A web page cannot reach the hub through a rebound DNS name,
  because the `Host` header must be an IP literal, `localhost`, `*.local`,
  `host.docker.internal`, or a name you listed in `ALLOWED_HOSTS`.
* **Credential exfiltration through SSRF.** The hub cannot be talked into sending
  the stored matrix password to an address you did not intend: changing the matrix
  host requires re-entering the password *and* a target in a private range that is
  not loopback, link-local or a cloud metadata endpoint.

### What the PINs do **not** replace

The PINs are a **tripwire against accidents and casual LAN access**. They are not an
internet-facing authentication system and they are not a substitute for transport
security. In particular:

* **No TLS.** The hub speaks plain HTTP. A PIN sent over HTTP is readable by anyone
  on the path. TLS termination is the job of a reverse proxy or a VPN.
* **No per-user identity.** There is one admin PIN and one control PIN. There are no
  accounts, no passwords, no sessions per user, no audit trail of who did what.
* **No internet-facing auth.** An `ADMIN_PIN` is a 4–8 digit number with an
  exponential lockout. It is not a substitute for a real identity provider.
* **No protection for the matrix's own credentials at rest.** They live in the data
  directory so the hub can reconnect unattended; protect that directory (filesystem
  permissions, encrypted disk, backups).

> ### ⚠️ Do not expose port 8080 (or port 9095) directly to the internet
>
> Use a VPN (e.g. **WireGuard** or **Tailscale**) or an **authenticating reverse
> proxy with HTTPS** (nginx, Caddy, Traefik, …) in front of the hub. Port forwarding
> 8080 or 9095 to the open internet hands your matrix control to anyone who can guess
> an IP, with no TLS and no real authentication.

---

## Two-level access model

| Level | Covers | Default | When a PIN is set |
| --- | --- | --- | --- |
| **Control** | Status, routing, preset recall, running profiles/scenes/shortcuts/macros, CEC, matrix power | **Open** — kiosk, Flic and Home Assistant work with zero setup | Only if `CONTROL_PIN` is set. Browsers/kiosks unlock once and are remembered; Home Assistant and Flic use an API key. |
| **Admin** | Settings, matrix host & credentials, creating/editing/deleting profiles/scenes/macros/shortcuts, integrations config, EDID/HDCP/HDR/scaler, reboot, dashboard layout editing | Open until an admin PIN exists; the web UI recommends setting one | Requires an admin session (30-minute idle timeout, "Lock" button). |

### Control level

Control is the "TV remote" level: what you do dozens of times a day.

* **Open by default.** Kiosk mode, the Flic integration and the Home Assistant
  integration work with **zero configuration** — no PIN, no key, no login.
* **Optionally gated** with `CONTROL_PIN` (or by toggling the control lock in
  settings). While it is set, a Control request needs one of:
  * an **unlocked session cookie** (`orei_session`) from `POST /api/auth/unlock`
    with `{"level": "control", "pin": "…"}`;
  * a **remembered device** cookie (`orei_device_token`), set when the browser or
    kiosk asked to be remembered. Remembered devices are listed and revocable at
    `GET`/`DELETE /api/auth/devices`;
  * an **API key** sent as the `X-API-Key` request header, or as `?key=…` on the
    query string (convenient for Flic's simple requests; the value is redacted from
    logs). Keys are created, listed and revoked at `/api/auth/api-keys`, and can also
    come from the environment as `API_KEY` / `CONTROL_API_KEY`.
* With no control PIN configured, **no key is needed at all** — every control route
  is open, exactly as before.

### Admin level

Admin is the "household settings" level.

* Admin routes (settings, matrix host and credentials, profile/scene/macro/shortcut
  creation and deletion, EDID/HDCP/HDR/scaler, integrations, reboot, dashboard
  layout) require an **admin session** once an admin PIN exists.
* The PIN is **4–8 digits**, hashed with **PBKDF2-HMAC-SHA256** (600,000 iterations,
  16-byte random salt per PIN) and never stored or logged in the clear. Hashing and
  verification run in a thread so a burst of wrong PINs cannot stall the hub.
* Unlock with `POST /api/auth/unlock` `{"level": "admin", "pin": "…"}`. The hub sets
  an `orei_session` cookie that is **`HttpOnly`** and **`SameSite=Strict`**, so page
  scripts cannot read it and it is not sent on cross-site requests. The session
  expires after **30 minutes idle** (each request refreshes the window) and can be
  ended at any time with `POST /api/auth/lock` or the web UI's "Lock" button.
* WebSocket connections inherit the level of the cookie that opened them; admin-only
  WebSocket commands are rejected without an admin session.
* **Brute force:** after **5 wrong attempts** the PIN entry point locks out with an
  exponential backoff (doubling from a second up to a one-hour cap) and answers
  `429 Too Many Requests`. A correct PIN resets the counter.
* The Admin PIN is set on first run in the web UI (skippable), via `ADMIN_PIN`, or
  later through `POST /api/auth/pin` — which itself requires the **current** admin
  PIN when one is already set.
* Automation that cannot hold a cookie may send the admin PIN per request in the
  `X-Admin-PIN` header instead; it is subject to the same lockout as the unlock form.

---

## PIN recovery

There is no email address, no recovery code and no cloud account.

To reset a forgotten admin PIN:

1. Stop the hub (or restart the container).
2. Start it once with **`ADMIN_PIN_RESET=true`** in the environment:

   ```bash
   ADMIN_PIN_RESET=true docker compose up -d
   ```

3. The stored admin PIN hash is deleted at start-up; the hub comes up with the Admin
   level open again so you can set a new PIN in the web UI.
4. **Remove the variable and restart** so the next start does not clear a PIN you
   have just set. While `ADMIN_PIN_RESET=true` is present in the environment, a PIN
   given in `ADMIN_PIN` is ignored too.

Remembered devices and API keys are not removed by a reset; revoke them from
settings (`/api/auth/devices`, `/api/auth/api-keys`) or delete the data directory's
`security.json`.

---

## Per-item profile and scene PINs

These are independent of the Admin PIN and exist so a single household member (or a
guest) can be allowed to run a scene without being able to change anything else.

* **Setting and removing a PIN:** `POST`/`PUT` on a profile or a v2 scene accepts
  `passcode` (4–8 digits) to set or change it, and `remove_passcode: true`,
  `passcode: null`/`""` or `password_protected: false` to clear it. Setting and
  clearing are mutually exclusive in one request.
* **The current PIN is always required** to change or remove an existing PIN, and to
  delete a protected item. Supply it as `current_passcode` in the body, or in the
  `X-Passcode` request header when the request has no body (a `DELETE`, for example).
* **Inheritance:** a scene that uses a protected profile inherits that profile's PIN.
  Checking the PIN for a scene therefore needs the profile map, so an inherited PIN
  cannot be side-stepped by running the scene directly.
* **Where the PIN is asked for:** `POST /api/profile/{id}/recall`,
  `POST /api/scene/{id}/recall` and `POST /api/v2/scenes/{id}/execute`. A missing PIN
  answers `403 passcode_required`, a wrong one `403 invalid_passcode`, and a locked
  item `429 passcode_locked` with a `Retry-After` header.
* **Storage:** PINs are stored as PBKDF2 hashes (`pbkdf2_sha256$…`) and are **never
  serialized to clients** — API responses carry `password_protected: true/false`
  only.
* **Attempt limiter:** wrong PINs are counted per item. The fifth locks the item for
  30 s, then 2 min, 10 min, 30 min and one hour; only one guess an hour gets
  through, so a 4-digit PIN takes months to brute force. PBKDF2 runs in a thread, so
  the event loop never stalls on a burst of guesses.

---

## Always-on protections

These are active whether or not any PIN is configured. They cannot be switched off
from the web UI.

### Browser request protection (CSRF / cross-site requests)

* Every mutating `/api/` request (`POST`, `PUT`, `DELETE`, `PATCH`) must present a
  same-origin `Origin` or `Referer`; a foreign origin is refused with
  `403 Cross-origin mutation denied`. This is what stops a page in another browser
  tab from operating your matrix.
* A request with a body must use `Content-Type: application/json`; anything else is
  refused with `415 JSON Content-Type required`. A cross-site HTML form can only send
  `application/x-www-form-urlencoded`, `multipart/form-data` or `text/plain`, so the
  guard holds even when no origin header is present.
* CORS is same-origin by default. Add extra browser origins with
  `CORS_ALLOWED_ORIGINS` (comma-separated; `*` allows any) and the hub echoes
  `Vary: Origin` so caches cannot serve a wrong-origin response. The allowed request
  headers are `Content-Type`, `X-API-Key` and `X-Admin-PIN`.
* WebSocket upgrades get the same `Origin` check (`403 WebSocket Origin denied`).

### DNS-rebinding `Host` header guard

Every request's `Host` header must be an **IP literal**, `localhost`,
`host.docker.internal`, a `*.local` name, or a name listed in `ALLOWED_HOSTS`.
Anything else is refused with `421 Unrecognized Host; add it to ALLOWED_HOSTS`, so a
browser tricked by a rebound DNS name cannot reach the hub. If you serve the hub
under a real hostname, add it once:

```bash
ALLOWED_HOSTS=matrix.example.lan,hub.home.example
```

### Matrix host SSRF guard and credential protection

* `POST /api/settings/matrix-host` is an **admin action**, and it **always requires
  re-entering the current matrix password** when the host changes — even when no
  admin PIN is set. A stored password is never sent to a new host, so a redirecting
  or spoofed address cannot harvest it.
* The target is **resolved first, then validated**: every returned address (including
  IPv4-mapped IPv6) must be inside a private unicast range — `10.0.0.0/8`,
  `172.16.0.0/12`, `192.168.0.0/16`, `fc00::/7` (plus the documentation ranges
  `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`).
* **Loopback, link-local (`169.254.0.0/16`, which is where cloud metadata endpoints
  live), unspecified and multicast addresses are always refused**, whatever the
  hostname resolves to. Ports must be an integer in `1–65535`. Only if you really
  need a matrix outside your LAN can you opt in per address range with
  `ALLOW_PUBLIC_MATRIX_HOST=true`.
* Matrix credentials are configurable from the Remote 3 setup, the web UI settings
  and the environment, and are **never logged**: a redaction filter rewrites every
  `password` value in the matrix log to `***REDACTED***`, and the Remote
  integration adds `auth_token`, `pin` and `current_password` to ucapi's own
  secret-key list.

### TLS certificate verification and pinning

The hub's connection to the matrix is HTTPS. Verification options:

| Variable | Effect |
| --- | --- |
| `OREI_VERIFY_SSL` | `true` verifies the matrix certificate against the system trust store. Default `false`, because most OREI matrices use a self-signed certificate. |
| `MATRIX_CA_CERT` | Path to a CA bundle that signs the matrix certificate (takes precedence over `OREI_VERIFY_SSL`). |
| `MATRIX_TLS_FINGERPRINT` | A SHA-256 fingerprint (colons allowed) to pin the matrix certificate. Pinning wins over a custom CA and opts in to verification even with `OREI_VERIFY_SSL=false`; an invalid fingerprint fails at start-up. |

`OREI_CA_CERT` and `OREI_TLS_FINGERPRINT` are the planned `OREI_*` names for the
last two variables (the env-var unification in `docs/REMEDIATION_PLAN.md` §4.2/§4.4);
today set `MATRIX_CA_CERT` / `MATRIX_TLS_FINGERPRINT`.

### Rate limiting, connection caps and proxy trust

* **Rate limiting** is per client IP with a sliding window: 60 writes per 10 s
  (`RATE_LIMIT_READ_REQUESTS`, default 300, for reads). Static assets, `/ui`,
  `/kiosk`, `/api/health` and WebSockets are not limited. A limited client gets
  `429 Rate limit exceeded. Please slow down.`
* **WebSocket cap:** at most `MAX_WS_CLIENTS` (default 32) live clients; beyond that
  the hub answers `503 WebSocket client limit reached` instead of growing without
  bound. Sockets use aiohttp heartbeats and dead clients are dropped.
* **Proxy headers:** `X-Forwarded-For` is ignored unless you set
  `TRUST_PROXY_HEADERS=true`, and even then only when the peer address is inside
  `TRUSTED_PROXY_IPS` (comma-separated IPs or CIDR blocks). Otherwise the rate
  limiter and the attempt limiters key on the real peer address, so a client cannot
  spoof its way past them.

### Static file root containment

Files under `/css`, `/js` and `/assets` are resolved first (`resolve()`, following
symlinks) and must still be inside the `web/` directory (`is_relative_to`). `..`
segments, encoded traversal, absolute and drive-qualified paths and symlinks pointing
elsewhere are all refused with `403 Forbidden`; directory listings are never
returned.

### Correlation-ID error hygiene

Unhandled failures never reach the client. The hub answers
`Internal server error (ref: <8-hex-correlation-id>)` and writes that same
correlation ID (the `X-Error-Id` value) together with the full traceback to its
log. Quote the `ref` value in a bug report — it is the only handle you need, while
paths, hostnames, firmware versions and stack traces stay in the log.

---

## Unfolded Circle Remote 3 integration (port 9095, UC-02)

With `UC_ENABLED=true` the hub also serves the Remote 3 integration on **9095**.

* **Set a token.** `UC_AUTH_TOKEN` (or, when it is not set, `ADMIN_PIN`) is the
  integration's shared secret. When one of them is present the hub advertises
  `pwd` in its mDNS driver record, so the Remote asks for the setup token during
  pairing and verifies it before anything else happens; a missing or wrong token
  fails the setup with `AUTHORIZATION_ERROR`. Without a token, the Remote can still
  change the matrix address, but only by re-entering the current matrix password.
* **Verify it end to end.** Pair the Remote once with the token set; the Remote
  stores it and sends it afterwards. Treat a token change as a re-pair.
* **Firewall port 9095 to the Remote.** Port 9095 is a device-to-device integration
  port, not a web port. Restrict it at the firewall/router to the IP address of the
  Remote 3 (and, if you like, the hub's own subnet). Anyone who can reach 9095 and
  knows the token can operate the matrix.
* `UC_DRIVER_URL` lets you advertise a specific `ws://host:port` when mDNS cannot be
  used (bridge networking); `UC_DISABLE_MDNS_PUBLISH=true` turns the mDNS
  advertisement off.

---

## Environment variables that change the security posture

| Variable | Default | What it does |
| --- | --- | --- |
| `ADMIN_PIN` | unset | Sets the admin PIN (4–8 digits, PBKDF2-HMAC-SHA256). Unset ⇒ admin routes are open. |
| `ADMIN_PIN_RESET` | unset | `true` clears the stored admin PIN at start-up (recovery). |
| `CONTROL_PIN` | unset | Sets the control PIN. Unset ⇒ control routes are open and no API key is needed. |
| `API_KEY` / `CONTROL_API_KEY` | unset | Extra API keys accepted as `X-API-Key` / `?key=`. |
| `ALLOWED_HOSTS` | unset | Extra `Host` names accepted by the DNS-rebinding guard. |
| `CORS_ALLOWED_ORIGINS` | unset | Extra browser origins (comma-separated, or `*`). Same-origin only by default. |
| `TRUST_PROXY_HEADERS` | `false` | Trust `X-Forwarded-For`. Only combine with `TRUSTED_PROXY_IPS`. |
| `TRUSTED_PROXY_IPS` | unset | IPs/CIDRs whose forwarded client address is honoured. |
| `MAX_WS_CLIENTS` | `32` | Maximum live WebSocket clients. |
| `RATE_LIMIT_READ_REQUESTS` | `300` | Read requests per 10 s per client (writes are 60). |
| `ALLOW_PUBLIC_MATRIX_HOST` | `false` | Permit a globally-routable matrix address (SSRF guard escape hatch). |
| `OREI_VERIFY_SSL` | `false` | Verify the matrix TLS certificate. |
| `MATRIX_CA_CERT` / `OREI_CA_CERT` | unset | CA bundle that signs the matrix certificate. |
| `MATRIX_TLS_FINGERPRINT` / `OREI_TLS_FINGERPRINT` | unset | SHA-256 fingerprint to pin the matrix certificate. |
| `UC_AUTH_TOKEN` | unset (falls back to `ADMIN_PIN`) | Shared secret the Remote 3 must present on **9095**. |
| `UC_ENABLED` | `false` | Start the Remote 3 integration (port **9095**). |
| `API_PORT` | `8080` | Port of the REST API, web UI and kiosk. |
| `DATA_DIR` | module default | Where `security.json` (PIN hashes, remembered devices, API-key hashes) is stored. |

---

## Reporting a vulnerability

Please report security issues **privately** — not in a public issue, discussion or
pull request.

1. Open the repository's security advisory form:
   <https://github.com/ryan-haver/8x8-hdmi-matrix-hub/security/advisories/new>
   (choose "Report a vulnerability"). Use the **Private vulnerability reporting**
   link on the repository's Security tab if you prefer not to use the form above.
2. Include, as far as you can:
   * the hub version or commit, and how you run it (Docker image, `python run.py`);
   * the configuration involved (is `ADMIN_PIN`/`CONTROL_PIN`/`UC_AUTH_TOKEN` set? is
     the hub behind a reverse proxy?);
   * the exact request(s) or steps to reproduce, and what you observed;
   * the `ref:` correlation ID and the matching hub log lines with passwords
     removed, if the issue involves a 500.
3. You will get an acknowledgement, and a fix or a mitigation plan, in the advisory
   thread. Please give us a reasonable window to ship a fix before disclosing.

Out of scope for security reports: missing hardening that this document already
describes as absent (for example plain HTTP on 8080), attacks that require physical
or root access to the hub or the host, and reports against the OREI matrix firmware
or the Unfolded Circle Remote 3 themselves — report those to their vendors.

**Supported versions.** Security fixes land on the latest release of the `main`
branch; older tags are not patched. Check out `main`, rebuild and redeploy.
