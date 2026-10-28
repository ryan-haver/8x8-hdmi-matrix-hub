# Hub Configuration & Environment Variable Reference

> **Implementation sources**: `hub.cli`, `hub.runtime.config`, `hub.runtime.composition`, `src/persistence.py`, `src/orei_matrix.py`, and `src/rest_api/`.

This document is the operator reference for runtime variables, deprecated aliases, retired flags, and low-level transport/security tuning parameters. `hub.cli` and the installed `orei-matrix-driver` console entry point resolve settings for the shared runtime; see [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## 1. Runtime Entrypoint & Architecture Overview

The single runtime entrypoint for Docker containers and local executions is [`run.py`](../run.py):

```bash
python run.py                     # Core hub only (UC_ENABLED defaults to false)
UC_ENABLED=true python run.py     # Core hub + Unfolded Circle Remote integration (port 9095)
python run.py healthcheck         # Exit 0 when http://127.0.0.1:${API_PORT}/api/health answers 200
```

### Shared Runtime

- **Runtime entry and services (`run.py`, `hub.cli`, `src/rest_api/`)**:
  - `run.py` is a compatibility wrapper around `hub.cli`; the installed `orei-matrix-driver` command uses the same runtime.
  - Both UC modes compose one matrix client, `MatrixService`, persistence barrier, REST/WebSocket server and integration loader. The REST/UI server starts before matrix connect.
  - `FLIC_ENABLED` controls whether Flic registration/list routes and its registry are loaded. `HA_DISCOVERY_ENABLED` controls optional HA discovery. UC disabled means no UC/`ucapi` import or listener.
- **Runtime packages (`src/hub/`)**:
  - `hub.runtime.config` resolves matrix addresses; `hub.runtime.composition` wires `MatrixService`, `ActionRunner`, `HubClientLocal`, persistence and integrations into startup.
  - `hub.cli` normalizes environment aliases and provides the source and installed entry points. Its rules, rather than `hub.env`'s framework inventory, govern runtime behavior.

Implementation references include `src/hub/core/matrix_service.py`,
`src/hub/domain/action_runner.py`, `src/hub/integrations/base.py`,
`src/hub/integrations/hub_client.py`, and the Flic adapter under
`src/hub/integrations/flic`. `src/hub/env.py` remains a framework environment
inventory; the runtime parser and defaults are in `hub.cli`.

---

## 2. Precedence & Boolean Parsing Rules

### Canonical vs. Alias Precedence (`hub.cli.resolve_env`)

1. **Canonical names always win** over deprecated aliases.
2. **Only non-empty values count** (`VAR=""` or whitespace-only is treated as unset).
3. If the canonical variable is unset and one or more aliases are set, the **first non-empty alias** in declaration order is used and a startup deprecation warning is logged: `<ALIAS> -> use <CANONICAL>`.
4. If both the canonical variable and an alias are set to **different** values, the canonical value is used and `<ALIAS> ignored (<CANONICAL> is set)` is logged.
5. Setting a **retired** variable logs `<VAR> is ignored (<reason>)` once at startup and has no effect on behavior.

### Boolean Values

Boolean environment variables accept (case-insensitively, stripped of surrounding whitespace):
- **True**: `1`, `true`, `yes`, `on` (trimmed, case-insensitive)
- **False**: `0`, `false`, `no`, `off` (trimmed, case-insensitive)
- Empty, unset, or unrecognized values fall back to the variable's documented default.

`FLIC_ENABLED` preserves its historical enabled default for an unrecognized
nonblank spelling and logs a warning. UC and HA discovery use the normal false
default.

---

## 3. Core Runtime Variables

Runtime settings are parsed by `hub.cli.load_settings()`; some transport and
security variables are read directly by their owning modules and are listed
in §7.

| Variable | Default | Runtime fallback | Choices / Type | Secret | Deprecated Aliases | Description |
|----------|----------------------------|---------------------------------------|----------------|--------|--------------------|-------------|
| `MATRIX_HOST` | `None` | UC off: explicit, saved setup, then `192.168.0.100`; UC on: saved setup, explicit bootstrap, else unconfigured | Hostname / IP | `false` | `OREI_HOST` | Matrix IP or host name. In UC mode an environment address is not persisted automatically. |
| `MATRIX_PORT` | `"443"` | `443` (`1`–`65535`) | Integer port | `false` | `OREI_PORT` | HTTPS port of the matrix's web API. |
| `MATRIX_USER` | `"Admin"` | `"Admin"` | String | `false` | — | User name for the matrix's Telnet command interface. |
| `MATRIX_PASSWORD` | `None` | `"admin"` (via `OREI_PASSWORD` in `orei_matrix.py`) | String | `true` | — | Password for the matrix's Telnet command interface. |
| `MATRIX_VERIFY_TLS` | `"false"` | `false` (via `OREI_VERIFY_SSL` in `orei_matrix.py`) | `true`, `false` | `false` | — | Verify the matrix's HTTPS certificate. |
| `API_PORT` | `"8080"` | `8080` (`1`–`65535`) | Integer port | `false` | `REST_API_PORT`, `OREI_API_PORT` | Port for the REST API, the web UI and the kiosk. |
| `DATA_DIR` | `None` | Docker image `/data`; local config/data defaults are separate | Directory path | `false` | `MATRIX_DATA_DIR` | Explicit directory exported through compatibility aliases; see the path precedence section. Installed wheels require a writable explicit path. |
| `LOG_LEVEL` | `"INFO"` | `"INFO"` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `false` | — | Root log level for the hub. |
| `ADMIN_PIN` | `None` | Unset (no admin PIN required) | String | `true` | — | PIN for the web admin. Unset means no admin session. |
| `CONTROL_PIN` | `None` | Unset (no control PIN required) | String | `true` | — | Optional second PIN that unlocks control-level access only. |
| `ALLOWED_HOSTS` | `None` | IP literals, `localhost`, `host.docker.internal`, `*.local` always allowed | Comma-separated hostnames | `false` | — | Comma-separated Host header values accepted in addition to IPs and localhost. |
| `CORS_ALLOWED_ORIGINS` | `None` | Same-origin always allowed | Comma-separated origins or `*` | `false` | — | Comma-separated allowed origins, or `'*'`. Same-origin is always allowed. |

---

## 4. Integration Variables

The shared runtime loader uses these flags and defaults:

| Variable | Default (`src/hub/env.py`) | Choices / Type | Secret | Deprecated Aliases | Description & Runtime Notes |
|----------|----------------------------|----------------|--------|--------------------|-----------------------------|
| `UC_ENABLED` | `"false"` | `true`, `false` | `false` | — | Start the Unfolded Circle Remote integration. A disabled integration is never imported. |
| `UC_INTEGRATION_HTTP_PORT` | `"9095"` | Integer port (`1`–`65535`) | `false` | `UC_PORT` | WebSocket port the Remote 3 integration listens on. |
| `UC_INTEGRATION_INTERFACE` | `None` | IPv4/IPv6 bind address | `false` | — | Bind address for the integration; also the address published by mDNS. Unset binds all interfaces. |
| `UC_DISABLE_MDNS_PUBLISH` | `"false"` | `true`, `false` | `false` | `UC_DISABLE_MDNS` | Do not announce the integration over mDNS (bridge networking). |
| `UC_CONFIG_HOME` | `None` | Directory path | `false` | — | Remote configuration/state directory. Defaults to explicit `DATA_DIR`; source local development defaults to project `config`. |
| `UC_DRIVER_URL` | `None` | `ws://...` or `wss://...` URL | `false` | — | `ws://` or `wss://` URL the Remote should dial, when mDNS cannot reach it. Validated by `run.py::load_settings()`. |
| `UC_AUTH_TOKEN` | `None` | String | `true` | — | Shared token the Remote presents to the hub (falls back to `ADMIN_PIN`). |
| `FLIC_ENABLED` | `"true"` | `true`, `false` | `false` | — | Load Flic registration/list routes and registry. Explicit false/0/no/off disables them; an unknown nonblank value warns and retains enabled default. |
| `HA_DISCOVERY_ENABLED` | `"false"` | `true`, `false` | `false` | — | Start optional Home Assistant mDNS discovery. Manual HACS setup remains available when disabled. |

---

## 5. Deprecated Aliases (`ENV_ALIASES`)

Defined in `src/hub/env.py::ENV_ALIASES` and `run.py::ENV_ALIASES`:

| Deprecated Alias | Canonical Variable | Startup Warning Logged |
|------------------|--------------------|------------------------|
| `OREI_HOST` | `MATRIX_HOST` | `OREI_HOST -> use MATRIX_HOST` |
| `OREI_PORT` | `MATRIX_PORT` | `OREI_PORT -> use MATRIX_PORT` |
| `REST_API_PORT` | `API_PORT` | `REST_API_PORT -> use API_PORT` |
| `OREI_API_PORT` | `API_PORT` | `OREI_API_PORT -> use API_PORT` |
| `MATRIX_DATA_DIR` | `DATA_DIR` | `MATRIX_DATA_DIR -> use DATA_DIR` |
| `UC_PORT` | `UC_INTEGRATION_HTTP_PORT` | `UC_PORT -> use UC_INTEGRATION_HTTP_PORT` |
| `UC_DISABLE_MDNS` | `UC_DISABLE_MDNS_PUBLISH` | `UC_DISABLE_MDNS -> use UC_DISABLE_MDNS_PUBLISH` |

> **Compatibility Export (`hub.cli::export_env`)**: Startup exports resolved settings under names consumed by existing transport and persistence modules. In particular, `DATA_DIR` supplies the default `UC_CONFIG_HOME`; data stores resolve via `MATRIX_DATA_DIR`, then `UC_CONFIG_HOME/data`, then project `data`. Explicit config and data paths may remain separate.

---

## 6. Retired & Ignored Variables (`RETIRED_ENV_VARS`)

Defined in `src/hub/env.py::RETIRED_ENV_VARS` and `run.py::RETIRED_ENV`:

| Retired Variable | Behavior | Reason Logged at Startup |
|------------------|----------|--------------------------|
| `USE_MODULAR` | Ignored | `USE_MODULAR is ignored (the mode follows UC_ENABLED)` |
| `WEBUI_ENABLED` | Ignored | `WEBUI_ENABLED is ignored (the web UI and kiosk are part of the core and always served)` |
| `REST_API_ENABLED` | Ignored when set to `false` | `REST_API_ENABLED=false is ignored (the REST API is the core and always runs)` |

---

## 7. Direct Transport, Security & Runtime Tuning Variables

As documented in `src/hub/env.py`, several low-level transport, security, and module-specific variables are read directly from `os.environ` by their respective modules rather than acting as aliases of canonical hub variables.

### 7.1 Matrix Hardware Transport (`src/orei_matrix.py`)

| Variable | Default | Type | Secret | Description |
|----------|---------|------|--------|-------------|
| `OREI_USER` | `"Admin"` | String | `false` | HTTP/Telnet login username used directly by `OreiMatrix`. |
| `OREI_PASSWORD` | `"admin"` | String | `true` | HTTP/Telnet login password used directly by `OreiMatrix`. |
| `OREI_VERIFY_SSL` | `"false"` | Boolean (`true`/`false`) | `false` | Verify the matrix HTTPS certificate in `OreiMatrix` (`true` enables normal TLS verification). |
| `MATRIX_TLS_FINGERPRINT` | `""` | Hex SHA-256 string | `false` | Pin the matrix leaf TLS certificate SHA-256 fingerprint (colons/spaces stripped). Takes precedence over `MATRIX_CA_CERT` and `OREI_VERIFY_SSL`. *(Note: `SECURITY.md` also refers to this concept as `OREI_TLS_FINGERPRINT`; `src/orei_matrix.py` reads `MATRIX_TLS_FINGERPRINT`.)* |
| `MATRIX_CA_CERT` | `""` | File path | `false` | Path to a custom CA certificate bundle (PEM) used to verify the matrix's HTTPS certificate. |
| `OREI_TELNET_PORT` | `"23"` | Integer (`1`–`65535`) | `false` | Matrix Telnet port (used when `telnet_port` is not explicitly passed or saved in `config_state.json`). Invalid values fall back to `23`. |
| `OREI_AUTO_RECONNECT` | `"true"` | Boolean (`true`/`false`) | `false` | Automatically reconnect to the matrix when the connection drops. |
| `OREI_USE_TELNET_CEC` | `"false"` | Boolean (`true`/`false`) | `false` | Prefer Telnet (`s cec ...!`) over HTTP for CEC commands when Telnet is connected. |
| `OREI_MAX_RETRIES` | `"5"` | Integer (`1`–`20`) | `false` | Maximum connection/command retry attempts (clamped to `1..20`). |
| `OREI_RETRY_DELAY` | `"1.0"` | Float (`0.1`–`30.0`) | `false` | Initial backoff delay in seconds between retries (clamped to `0.1..30.0`). |
| `OREI_MAX_RETRY_DELAY` | `"60.0"` | Float (`1.0`–`300.0`) | `false` | Maximum backoff delay in seconds between retries (clamped to `1.0..300.0`). |
| `OREI_CEC_CACHE_TTL` | `"300"` | Integer (`0`–`86400`) | `false` | TTL in seconds for cached CEC status reads (clamped to `0..86400`). |
| `OREI_STATUS_CACHE_TTL` | `"3.0"` | Float (`0.0`–`60.0`) | `false` | TTL in seconds for cached matrix status and preset slot reads (clamped to `0.0..60.0`). |

### 7.2 REST API, Security, Rate Limiting & WebSocket (`src/rest_api/` & `src/password.py`)

| Variable | Module | Default | Type | Secret | Description |
|----------|--------|---------|------|--------|-------------|
| `ADMIN_PIN_RESET` | `src/rest_api/security.py` | `"false"` | Boolean (`true`/`false`) | `false` | When `"true"`, clears any persisted `admin_pin` in `security.json` on startup and skips hashing `ADMIN_PIN`. |
| `API_KEY` | `src/rest_api/security.py` | `None` | String | `true` | Environment-configured control-level API key accepted via `X-API-Key` or `?key=`. |
| `CONTROL_API_KEY` | `src/rest_api/security.py` | `None` | String | `true` | Alternate environment-configured control-level API key accepted via `X-API-Key` or `?key=`. |
| `MATRIX_PASSWORD_ITERATIONS` | `src/password.py` | `"600000"` | Integer (`>= 100000`) | `false` | PBKDF2-HMAC-SHA256 iteration count for hashing PINs and profile passcodes (minimum `100,000`). |
| `ALLOW_PUBLIC_MATRIX_HOST` | `src/rest_api/settings.py` | `"false"` | Boolean (`true`/`false`, `1`, `yes`) | `false` | Allow `POST /api/settings/matrix-host` to target non-RFC1918/non-local IP addresses (SSRF guard override). |
| `TRUST_PROXY_HEADERS` | `src/rest_api/utils.py` | `"false"` | Boolean (`true`/`false`) | `false` | Trust `X-Forwarded-For` from reverse proxies listed in `TRUSTED_PROXY_IPS` for rate-limiting client identification. |
| `TRUSTED_PROXY_IPS` | `src/rest_api/utils.py` | `""` | Comma-separated IPs | `false` | Comma-separated proxy IP addresses allowed to supply `X-Forwarded-For` when `TRUST_PROXY_HEADERS=true`. |
| `RATE_LIMIT_READ_REQUESTS` | `src/rest_api/utils.py` | `"300"` | Integer | `false` | Maximum `GET` requests per 60-second window per client IP (`0` disables read rate limiting; write rate limit is fixed at `60`/min). |
| `STATUS_POLL_INTERVAL` | `hub/runtime/composition.py` | `"5"` | Number (seconds) | `false` | Shared runtime refresh interval. If unset, `POLLING_INTERVAL` is used as fallback; invalid values use 5 seconds. |
| `MAX_WS_CLIENTS` | `src/rest_api/websocket.py` | `"32"` | Integer (`>= 1`) | `false` | Maximum concurrent WebSocket clients allowed on `/ws` (additional connections receive HTTP `503`). |

### 7.3 Remote & Integration Helper Variables (`src/hub/integrations/`)

| Variable | Module | Default | Type | Secret | Description |
|----------|--------|---------|------|--------|-------------|
| `POLLING_INTERVAL` | `hub/runtime/composition.py` | unset | Number (seconds) | `false` | Fallback refresh interval when `STATUS_POLL_INTERVAL` is unset. |
| `POLLING_ENABLED` | Legacy `src/driver.py` | n/a | n/a | `false` | The legacy driver is not the runtime entry path; this setting no longer controls shared runtime refresh. |
| `HUB_URL` | `src/hub/integrations/hub_client.py` | `"http://127.0.0.1:8080"` | URL | `false` | Base URL used by `HubClient.from_env()` to connect to the core hub REST/WebSocket API. |
| `HUB_API_KEY` | `src/hub/integrations/hub_client.py` | `None` | String | `true` | API key used by `HubClient.from_env()` (falls back to `API_KEY` or `CONTROL_API_KEY`). |
| `HOST_IP` | `src/hub/integrations/homeassistant` | `None` | IPv4 address | `false` | Explicit LAN IPv4 address advertised by the Home Assistant mDNS discovery service (checked after `UC_INTEGRATION_INTERFACE`, before `API_HOST`). |
| `API_HOST` | `src/hub/integrations/homeassistant` | `None` | IPv4 address | `false` | Fallback LAN IPv4 address checked by `homeassistant` if `UC_INTEGRATION_INTERFACE` and `HOST_IP` are unset. |
| `HA_DISCOVERY_SERVICE_NAME` | `src/hub/integrations/homeassistant` | `"OREI HDMI Matrix Hub"` | String | `false` | Instance name advertised under `_orei-hdmi-matrix._tcp.local.` by the Home Assistant mDNS publisher. |

---

## 8. Persistent Storage Resolution (`hub.runtime.composition`, `src/persistence.py`)

`persistence.get_data_dir()` resolves the persistent data directory using the following precedence:

1. `MATRIX_DATA_DIR` (populated from explicit `DATA_DIR` by startup, or set directly)
2. `UC_CONFIG_HOME/data`
3. `<project_root>/data` (local development fallback; Docker images set `DATA_DIR=/data`)

Configuration remains separate: `UC_CONFIG_HOME` is authoritative for
`config_state.json`, and explicit `DATA_DIR` also supplies its default. With
neither in source development, configuration is project `config`. Data stores
resolve as listed above. The startup migration barrier validates managed data
before managers load it and stops on unsafe or ambiguous inputs. Installed
packages require an explicit writable `DATA_DIR` or `MATRIX_DATA_DIR`.
