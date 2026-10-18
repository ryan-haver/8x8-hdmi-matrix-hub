# Hub Configuration & Environment Variable Reference

> **Specification Reference**: `src/hub/env.py` (DI-12), `run.py`, `src/persistence.py`, `src/orei_matrix.py`, `src/rest_api/` (DOC-12).

This document is the authoritative reference for every environment variable read by the 8x8 HDMI Matrix Hub, including canonical hub settings, opt-in integration settings, deprecated aliases, retired flags, and low-level transport, security, and runtime tuning parameters.

---

## 1. Runtime Entrypoint & Architecture Overview

The single runtime entrypoint for Docker containers and local executions is [`run.py`](../run.py):

```bash
python run.py                     # Core hub only (UC_ENABLED defaults to false)
UC_ENABLED=true python run.py     # Core hub + Unfolded Circle Remote integration (port 9095)
python run.py healthcheck         # Exit 0 when http://127.0.0.1:${API_PORT}/api/health answers 200
```

### Shipped Runtime vs. Canonical Hub Framework Modules

- **Current Shipped Runtime (`run.py`, `src/driver.py`, `src/rest_api/`)**:
  - When `UC_ENABLED=false` (default), `run.py::run_core()` constructs `OreiMatrix` and `RestApiServer` directly and serves the REST API, WebSocket stream (`/ws`), OpenAPI 3.1 specification (`/api/openapi.json`), Swagger UI (`/api/docs`), Web UI (`/ui`), and Kiosk UI (`/kiosk`) on `API_PORT` without importing `ucapi`.
  - When `UC_ENABLED=true`, `run.py::run_uc_driver()` verifies that `ucapi` is installed, applies `UC_DRIVER_URL` metadata overrides if set, and delegates execution to `src/driver.py` (running the UC Remote integration and REST API in one process).
  - `src/rest_api/integrations.py` currently imports the Flic compatibility module (`hub.integrations.flic` at `src/hub/integrations/flic`) directly for `/api/integrations/flic/*`.
- **Canonical Environment Schema & Tested Framework Modules (`src/hub/`)**:
  - `src/hub/env.py` defines the canonical environment specification (`CORE_ENV_VARS`, `INTEGRATION_ENV_VARS`, `ENV_ALIASES`, `RETIRED_ENV_VARS`) and `resolve_hub_env()`.
  - `src/hub/core/matrix_service.py` (`MatrixService`), `src/hub/domain/action_runner.py` (`ActionRunner`), `src/hub/integrations/base.py` (`IntegrationLoader`), and `src/hub/integrations/hub_client.py` (`HubClient`) are implemented and tested library/framework modules; wiring `run.py` and REST/UC handlers to instantiate `MatrixService`, `ActionRunner`, and `IntegrationLoader` (including `FLIC_ENABLED` and `HA_DISCOVERY_ENABLED` startup lifecycle) is tracked as pending integration work.

---

## 2. Precedence & Boolean Parsing Rules

### Canonical vs. Alias Precedence (`resolve_hub_env` / `resolve_env`)

1. **Canonical names always win** over deprecated aliases.
2. **Only non-empty values count** (`VAR=""` or whitespace-only is treated as unset).
3. If the canonical variable is unset and one or more aliases are set, the **first non-empty alias** in declaration order is used and a startup deprecation warning is logged: `<ALIAS> -> use <CANONICAL>`.
4. If both the canonical variable and an alias are set to **different** values, the canonical value is used and `<ALIAS> ignored (<CANONICAL> is set)` is logged.
5. Setting a **retired** variable logs `<VAR> is ignored (<reason>)` once at startup and has no effect on behavior.

### Boolean Values

Boolean environment variables accept (case-insensitively, stripped of surrounding whitespace):
- **True**: `1`, `true`, `yes`, `on` (`src/hub/env.py::TRUE_VALUES`)
- **False**: `0`, `false`, `no`, `off` (`src/hub/env.py::FALSE_VALUES`)
- Empty, unset, or unrecognized values fall back to the variable's documented default.

---

## 3. Canonical Core Hub Variables (`CORE_ENV_VARS`)

Defined in `src/hub/env.py::CORE_ENV_VARS` (`kind="core"`):

| Variable | Default (`src/hub/env.py`) | Runtime Fallback (`run.py` / Modules) | Choices / Type | Secret | Deprecated Aliases | Description |
|----------|----------------------------|---------------------------------------|----------------|--------|--------------------|-------------|
| `MATRIX_HOST` | `None` | Saved `config_state.json` `host`, else `192.168.0.100` | Hostname / IP | `false` | `OREI_HOST` | IP address or host name of the OREI matrix. |
| `MATRIX_PORT` | `"443"` | `443` (`1`–`65535`) | Integer port | `false` | `OREI_PORT` | HTTPS port of the matrix's web API. |
| `MATRIX_USER` | `"Admin"` | `"Admin"` | String | `false` | — | User name for the matrix's Telnet command interface. |
| `MATRIX_PASSWORD` | `None` | `"admin"` (via `OREI_PASSWORD` in `orei_matrix.py`) | String | `true` | — | Password for the matrix's Telnet command interface. |
| `MATRIX_VERIFY_TLS` | `"false"` | `false` (via `OREI_VERIFY_SSL` in `orei_matrix.py`) | `true`, `false` | `false` | — | Verify the matrix's HTTPS certificate. |
| `API_PORT` | `"8080"` | `8080` (`1`–`65535`) | Integer port | `false` | `REST_API_PORT`, `OREI_API_PORT` | Port for the REST API, the web UI and the kiosk. |
| `DATA_DIR` | `None` | `<project_root>/data` (Docker image sets `/data`) | Directory path | `false` | `MATRIX_DATA_DIR` | Directory for every persistent file the hub writes. |
| `LOG_LEVEL` | `"INFO"` | `"INFO"` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `false` | — | Root log level for the hub. |
| `ADMIN_PIN` | `None` | Unset (no admin PIN required) | String | `true` | — | PIN for the web admin. Unset means no admin session. |
| `CONTROL_PIN` | `None` | Unset (no control PIN required) | String | `true` | — | Optional second PIN that unlocks control-level access only. |
| `ALLOWED_HOSTS` | `None` | IP literals, `localhost`, `host.docker.internal`, `*.local` always allowed | Comma-separated hostnames | `false` | — | Comma-separated Host header values accepted in addition to IPs and localhost. |
| `CORS_ALLOWED_ORIGINS` | `None` | Same-origin always allowed | Comma-separated origins or `*` | `false` | — | Comma-separated allowed origins, or `'*'`. Same-origin is always allowed. |

---

## 4. Canonical Opt-in Integration Variables (`INTEGRATION_ENV_VARS`)

Defined in `src/hub/env.py::INTEGRATION_ENV_VARS` (`kind="integration"`):

| Variable | Default (`src/hub/env.py`) | Choices / Type | Secret | Deprecated Aliases | Description & Runtime Notes |
|----------|----------------------------|----------------|--------|--------------------|-----------------------------|
| `UC_ENABLED` | `"false"` | `true`, `false` | `false` | — | Start the Unfolded Circle Remote integration. A disabled integration is never imported. |
| `UC_INTEGRATION_HTTP_PORT` | `"9095"` | Integer port (`1`–`65535`) | `false` | `UC_PORT` | WebSocket port the Remote 3 integration listens on. |
| `UC_INTEGRATION_INTERFACE` | `None` | IPv4/IPv6 bind address | `false` | — | Bind address for the integration; also the address published by mDNS. Unset binds all interfaces. |
| `UC_DISABLE_MDNS_PUBLISH` | `"false"` | `true`, `false` | `false` | `UC_DISABLE_MDNS` | Do not announce the integration over mDNS (bridge networking). |
| `UC_CONFIG_HOME` | `None` | Directory path | `false` | — | Integration state directory (defaults to `DATA_DIR`). |
| `UC_DRIVER_URL` | `None` | `ws://...` or `wss://...` URL | `false` | — | `ws://` or `wss://` URL the Remote should dial, when mDNS cannot reach it. Validated by `run.py::load_settings()`. |
| `UC_AUTH_TOKEN` | `None` | String | `true` | — | Shared token the Remote presents to the hub (falls back to `ADMIN_PIN`). |
| `FLIC_ENABLED` | `"false"` | `true`, `false` | `false` | — | Accept button registrations from a Flic Hub (`IntegrationLoader` framework variable; `/api/integrations/flic/*` routes are currently registered directly in `rest_api`). |
| `HA_DISCOVERY_ENABLED` | `"false"` | `true`, `false` | `false` | — | Publish the hub to Home Assistant over mDNS/zeroconf (`IntegrationLoader` / `hub.integrations.homeassistant` framework variable; not yet wired into `run.py` startup). |

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

> **Compatibility Export (`run.py::export_env`)**: At startup, `run.py` exports resolved canonical values back into `os.environ` under both canonical names (`API_PORT`, `DATA_DIR`, `MATRIX_PORT`, `MATRIX_HOST`, `UC_CONFIG_HOME`, `UC_INTEGRATION_HTTP_PORT`, `UC_DISABLE_MDNS_PUBLISH`, `UC_ENABLED`) and legacy module names (`REST_API_PORT`, `REST_API_ENABLED="true"`, `MATRIX_DATA_DIR`) so internal modules read consistent values.

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
| `STATUS_POLL_INTERVAL` | `src/rest_api/events.py` | `"5"` | Integer (seconds) | `false` | Interval in seconds between background matrix status polls for the `/ws` event stream (`0` disables periodic polling). |
| `MAX_WS_CLIENTS` | `src/rest_api/websocket.py` | `"32"` | Integer (`>= 1`) | `false` | Maximum concurrent WebSocket clients allowed on `/ws` (additional connections receive HTTP `503`). |

### 7.3 UC Driver & Integration Helper Variables (`src/driver.py` & `src/hub/integrations/`)

| Variable | Module | Default | Type | Secret | Description |
|----------|--------|---------|------|--------|-------------|
| `POLLING_INTERVAL` | `src/driver.py` | `"30"` | Integer (`>= 5`) | `false` | Interval in seconds for the UC driver's background status watchdog poll (minimum `5` seconds). |
| `POLLING_ENABLED` | `src/driver.py` | `"true"` | Boolean (`true`/`false`) | `false` | Enable or disable the UC driver's periodic status watchdog loop. |
| `HUB_URL` | `src/hub/integrations/hub_client.py` | `"http://127.0.0.1:8080"` | URL | `false` | Base URL used by `HubClient.from_env()` to connect to the core hub REST/WebSocket API. |
| `HUB_API_KEY` | `src/hub/integrations/hub_client.py` | `None` | String | `true` | API key used by `HubClient.from_env()` (falls back to `API_KEY` or `CONTROL_API_KEY`). |
| `HOST_IP` | `src/hub/integrations/homeassistant` | `None` | IPv4 address | `false` | Explicit LAN IPv4 address advertised by the Home Assistant mDNS discovery service (checked after `UC_INTEGRATION_INTERFACE`, before `API_HOST`). |
| `API_HOST` | `src/hub/integrations/homeassistant` | `None` | IPv4 address | `false` | Fallback LAN IPv4 address checked by `homeassistant` if `UC_INTEGRATION_INTERFACE` and `HOST_IP` are unset. |
| `HA_DISCOVERY_SERVICE_NAME` | `src/hub/integrations/homeassistant` | `"OREI HDMI Matrix Hub"` | String | `false` | Instance name advertised under `_orei-hdmi-matrix._tcp.local.` by the Home Assistant mDNS publisher. |

---

## 8. Persistent Storage Resolution (`src/persistence.py`)

`persistence.get_data_dir()` resolves the persistent data directory using the following precedence:

1. `MATRIX_DATA_DIR` (populated from `DATA_DIR` by `run.py::export_env()`, or set directly)
2. `UC_CONFIG_HOME`
3. `<project_root>/data` (local development fallback; Docker images set `DATA_DIR=/data`)

At startup, `run.py::check_writable()` verifies that `DATA_DIR` and `UC_CONFIG_HOME` exist and can be written to, exiting with code `2` and a `chown` remediation message if permissions are insufficient.
