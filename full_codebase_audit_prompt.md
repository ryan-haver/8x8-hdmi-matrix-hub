# Full Codebase Audit: 8x8 HDMI Matrix Hub

**Role**: Senior Software Architect & QA Lead  
**Task**: Perform a comprehensive, low-level audit of the entire 8x8 HDMI Matrix Hub codebase. This is a production system controlling physical hardware — rigor matters.

---

## 📋 Project Overview

This project integrates an 8x8 HDMI Matrix switcher (OEM HDCVT HDP-MXC88A platform, sold as OREI BK-808) with multiple control systems. The hardware communicates over HTTPS (CGI-based API on port 443) and Telnet (port 23).

### Architecture Summary

```
┌──────────────────────────────────────────────────────────────┐
│                    OREI BK-808 Hardware                       │
│                  (HTTPS:443 + Telnet:23)                     │
└──────────┬────────────────────────────┬──────────────────────┘
           │                            │
     ┌─────▼──────┐              ┌──────▼───────┐
     │ orei_matrix │              │ telnet_client│
     │ .py (93KB)  │              │  .py (33KB)  │
     └─────┬──────┘              └──────┬───────┘
           │                            │
     ┌─────▼────────────────────────────▼──────────────────────┐
     │                    Core Services Layer                   │
     │  config.py | scene_manager.py | cec_macros.py |         │
     │  cec_resolver.py | persistence.py | system_shortcuts.py │
     │  scene_execution.py | dashboard_layout.py | password.py │
     └─────┬────────────────────┬──────────────────────────────┘
           │                    │
     ┌─────▼──────┐     ┌──────▼───────────────────┐
     │  REST API   │     │  UC Driver (driver.py)   │
     │  (aiohttp)  │     │  (ucapi WebSocket)       │
     │  21 modules │     │  89KB, 2155 lines        │
     └─────┬──────┘     └──────┬───────────────────┘
           │                    │
     ┌─────▼──────┐     ┌──────▼───────────────────┐
     │  Web UI     │     │  Unfolded Circle Remote 3│
     │  50+ files  │     │                          │
     └─────┬──────┘     └──────────────────────────┘
           │
     ┌─────▼────────────────────────────┐
     │  External Consumers              │
     │  • Home Assistant HACS Component │
     │  • Flic Smart Buttons            │
     └─────────────────────────────────┘
```

### Deployment Model

- **Docker container** (Python 3.12-slim) — multi-stage build (api-only vs full)
- `run.py` is the unified entrypoint; feature-flags via env vars (`UC_ENABLED`, `WEBUI_ENABLED`)
- `run_server.py` is a standalone REST API entrypoint (no UC driver)
- Persistent config stored in `/data` (`UC_CONFIG_HOME`)
- GitHub Actions CI → Docker Hub publish

---

## 🗂️ Complete File Inventory

Read and audit **every file** listed below. Files are grouped by layer.

### Layer 1: Hardware Communication (THE FOUNDATION)

| File | Size | Description |
|------|------|-------------|
| `src/orei_matrix.py` | 93KB | Core hardware abstraction — HTTPS API client, HDCP/HDR/EDID/CEC control, output routing, presets, password auth, Telnet integration |
| `src/telnet_client.py` | 33KB | Async Telnet client for cable detection, CEC commands, real-time monitoring |
| `src/cec_commands.py` | 10KB | CEC command definitions and byte-level protocol |
| `src/cec_resolver.py` | 14KB | CEC address resolution and device discovery |

### Layer 2: Core Services

| File | Size | Description |
|------|------|-------------|
| `src/config.py` | 32KB | Configuration management, EDID mode mappings, hardware settings |
| `src/scene_manager.py` | 27KB | Scene (routing snapshot) CRUD and persistence |
| `src/scene_execution.py` | 20KB | Scene execution engine with CEC macro chaining |
| `src/cec_macros.py` | 17KB | CEC macro definitions, step execution, delay management |
| `src/system_shortcuts.py` | 26KB | System-wide shortcuts/quick-actions with ordering and favorites |
| `src/dashboard_layout.py` | 9KB | Dashboard card layout persistence and management |
| `src/persistence.py` | 7KB | Data directory resolution, file I/O helpers |
| `src/password.py` | 3KB | Matrix authentication credential management |
| `src/__init__.py` | 174B | Package init |

### Layer 3: REST API (21 modules)

| File | Size | Description |
|------|------|-------------|
| `src/rest_api/__init__.py` | 4KB | Package init, lazy imports, public API surface |
| `src/rest_api/app.py` | 22KB | aiohttp application factory, route registration, server lifecycle |
| `src/rest_api/core.py` | 12KB | Health, status, info, inputs/outputs endpoints |
| `src/rest_api/control.py` | 17KB | Routing, preset, power, input cycling endpoints |
| `src/rest_api/outputs.py` | 24KB | Per-output configuration (HDCP, HDR, EDID, mute, enable) |
| `src/rest_api/cec.py` | 18KB | CEC command endpoints |
| `src/rest_api/audio.py` | 16KB | Audio routing and control endpoints |
| `src/rest_api/macros.py` | 11KB | CEC macro CRUD and execution endpoints |
| `src/rest_api/profiles.py` | 25KB | Profile management and recall endpoints |
| `src/rest_api/scenes.py` | 12KB | Scene management endpoints (v1) |
| `src/rest_api/scenes_v2.py` | 17KB | Scene management endpoints (v2) |
| `src/rest_api/settings.py` | 4KB | System settings endpoints |
| `src/rest_api/system.py` | 3KB | System reboot, beep, panel lock |
| `src/rest_api/system_shortcuts.py` | 12KB | System shortcuts REST endpoints |
| `src/rest_api/dashboard_layout.py` | 7KB | Dashboard layout REST endpoints |
| `src/rest_api/device_settings.py` | 25KB | Device settings persistence and endpoints |
| `src/rest_api/static.py` | 14KB | Static file serving and web UI hosting |
| `src/rest_api/websocket.py` | 4KB | WebSocket broadcast for real-time updates |
| `src/rest_api/utils.py` | 16KB | Shared utilities, state management, rate limiting |
| `src/rest_api/themes.py` | 6KB | Theme management and persistence |
| `src/rest_api/ui.py` | 4KB | UI preference persistence |

### Layer 4: Unfolded Circle Remote 3 Integration

| File | Size | Description |
|------|------|-------------|
| `src/driver.py` | 89KB | UC driver — entity creation, command handlers, polling, mDNS, reconnection |
| `src/integrations/unfolded_circle/adapter.py` | 8KB | API client adapter for OreiMatrix compatibility |
| `src/integrations/unfolded_circle/api_client.py` | 17KB | REST API client for remote UC driver mode |
| `src/integrations/unfolded_circle/entities.py` | 12KB | Entity factory functions with dependency injection |
| `src/integrations/unfolded_circle/__init__.py` | 772B | UC integration package init |
| `src/integrations/__init__.py` | 35B | Integrations package init |
| `driver.json` | 1.5KB | UC driver metadata and setup schema |

### Layer 5: Home Assistant HACS Component

| File | Size | Description |
|------|------|-------------|
| `custom_components/orei_matrix/__init__.py` | 4KB | Entry setup, service registration, unload |
| `custom_components/orei_matrix/config_flow.py` | 2KB | Config flow with connection validation |
| `custom_components/orei_matrix/coordinator.py` | 3KB | DataUpdateCoordinator with parallel API fetches |
| `custom_components/orei_matrix/select.py` | 4KB | Output source selector entities |
| `custom_components/orei_matrix/switch.py` | 7KB | Power, mute, and stream switches |
| `custom_components/orei_matrix/button.py` | 4KB | Preset recall and reboot buttons |
| `custom_components/orei_matrix/binary_sensor.py` | 4KB | Input signal and output connection sensors |
| `custom_components/orei_matrix/const.py` | 295B | Constants |
| `custom_components/orei_matrix/manifest.json` | 343B | HACS manifest |
| `custom_components/orei_matrix/strings.json` | 500B | Config flow translations |
| `custom_components/orei_matrix/services.yaml` | 2KB | Service definitions |

### Layer 6: Web UI (Frontend)

| File | Size | Description |
|------|------|-------------|
| `web/index.html` | 32KB | Main web UI |
| `web/kiosk.html` | 31KB | Kiosk mode UI (tablet-optimized) |
| `web/js/app.js` | 29KB | Application bootstrap, initialization |
| `web/js/api.js` | 23KB | REST API client |
| `web/js/state.js` | 38KB | Global state management |
| `web/js/websocket.js` | 9KB | WebSocket client for real-time updates |
| `web/js/constants.js` | 4KB | Frontend constants |
| `web/js/tron-background.js` | 38KB | Animated background effect |
| `web/js/utils/dashboard-manager.js` | 44KB | Dashboard card management |
| `web/js/utils/floatable.js` | 15KB | Drag-and-drop system |
| `web/js/utils/icon-library.js` | 82KB | SVG icon registry |
| `web/js/utils/helpers.js` | 4KB | General utility functions |
| `web/js/utils/logger.js` | 5KB | Frontend logging |
| `web/js/utils/api-copy.js` | 17KB | **INVESTIGATE** — appears to be a copy of api.js |
| `web/js/utils/overlay-manager.js` | 4KB | Modal/overlay management |
| `web/js/utils/focus-trap.js` | 4KB | Accessibility focus trapping |
| `web/js/components/` | 38 files | UI components (listed separately) |
| `web/js/components/dashboard-cards/renderers.js` | 10KB | Dashboard card rendering |
| `web/css/style.css` | 24KB | Base styles |
| `web/css/theme.css` | 51KB | Theme system |
| `web/css/components.css` | 148KB | Component styles |
| `web/css/responsive.css` | 16KB | Responsive breakpoints |
| `web/css/cec-tray.css` | 25KB | CEC tray styles |
| `web/css/icon-picker.css` | 10KB | Icon picker styles |

**Web UI Components** (38 files in `web/js/components/`):
`about-dialog.js`, `cec-controls.js`, `cec-macro-editor.js`, `cec-tray.js` (67KB!), `confirm-dialog.js`, `context-menu.js`, `dashboard-card-picker.js`, `debug-panel.js`, `empty-state.js`, `general-drawer.js`, `hardware-drawer.js`, `icon-picker.js`, `input-panel.js`, `input-settings-modal.js`, `interface-drawer.js`, `keyboard-shortcuts.js`, `matrix-grid.js`, `output-panel.js`, `output-settings-modal.js`, `presets-drawer.js`, `presets-panel.js`, `profile-editor.js`, `profile-manager.js`, `quick-actions-drawer.js`, `routing-drawer.js`, `scene-cec-modal.js`, `scene-editor.js`, `scenes-panel.js`, `settings-drawer.js`, `settings-panel.js`, `setup-wizard.js`, `shortcuts-drawer.js`, `side-nav-drawer.js`, `skeleton-loader.js`, `system-shortcuts-panel.js`, `theme-drawer.js`, `toast.js`, `tooltip.js`

### Layer 7: Infrastructure & Configuration

| File | Size | Description |
|------|------|-------------|
| `Dockerfile` | 3KB | Multi-stage Docker build |
| `docker-compose.yml` | 3KB | Compose stack definition |
| `run.py` | 5KB | Unified entrypoint |
| `run_server.py` | 5KB | Standalone API server entrypoint |
| `setup.py` | 1.5KB | Package setup |
| `pyproject.toml` | 2KB | Build config, dependencies, tool config |
| `requirements.txt` | 411B | Core dependencies |
| `requirements-uc.txt` | 451B | UC-specific dependencies |
| `.github/workflows/docker-publish.yml` | 3KB | CI/CD pipeline |
| `.dockerignore` | 363B | Docker ignore rules |
| `.gitignore` | 814B | Git ignore rules |
| `.gitleaks.toml` | 394B | Secret scanning config |
| `driver.json` | 1.5KB | UC driver metadata |

### Layer 8: Test Suite

| File | Size | Description |
|------|------|-------------|
| `tests/conftest.py` | 12KB | Shared fixtures |
| `tests/test_rest_api.py` | 102KB | REST API tests (largest test file) |
| `tests/test_config.py` | 37KB | Configuration tests |
| `tests/test_orei_matrix.py` | 17KB | Hardware abstraction tests |
| `tests/test_cec_macros.py` | 20KB | CEC macro tests |
| `tests/test_driver.py` | 18KB | UC driver tests |
| `tests/test_persistence.py` | 17KB | Persistence layer tests |
| `tests/test_device_settings_presets.py` | 15KB | Device settings tests |
| `tests/test_integrations_adapter.py` | 13KB | UC adapter tests |
| `tests/test_scene_execution.py` | 13KB | Scene execution tests |
| `tests/test_scene_manager.py` | 12KB | Scene manager tests |
| `tests/test_dashboard_layout.py` | 12KB | Dashboard layout tests |
| `tests/test_error_paths.py` | 11KB | Error handling tests |
| `tests/test_connection.py` | 7KB | Connection tests |
| `tests/test_rest_themes_ui.py` | 7KB | Theme/UI tests |
| `tests/test_system_shortcuts.py` | 7KB | System shortcuts tests |
| `tests/test_cec_resolver.py` | 5KB | CEC resolver tests |
| `tests/test_all_features.py` | 4KB | Feature integration tests |
| `tests/test_all_formats.py` | 5KB | Format handling tests |
| `tests/test_hacs_integration.py` | 3KB | HA integration tests |
| `tests/test_http_vs_https.py` | 3KB | HTTP/HTTPS tests |
| `tests/test_password.py` | 2KB | Password tests |
| `tests/test_input_names.py` | 1KB | Input naming tests |
| `tests/test_manual.py` | 5KB | Manual test helpers |

### Layer 9: Documentation

| File | Size | Description |
|------|------|-------------|
| `README.md` | 19KB | Project README |
| `CONTRIBUTING.md` | 2KB | Contribution guidelines |
| `docs/API_REFERENCE.md` | 27KB | REST API reference |
| `docs/CEC_CONTROL_ARCHITECTURE.md` | 69KB | CEC system design doc |
| `docs/HOME_ASSISTANT.md` | 17KB | HA integration guide |
| `docs/UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md` | 11KB | UC integration guide |
| `docs/FLIC_SETUP.md` | 27KB | Flic button setup guide |
| `docs/DOCKER.md` | 8KB | Docker deployment guide |
| `docs/WEB_UI_IMPLEMENTATION_PLAN.md` | 31KB | Web UI design spec |
| `docs/PROJECT_ROADMAP.md` | 34KB | Project roadmap |
| `docs/PHASE_8_SPEC.md` | 15KB | Phase 8 specification |
| `docs/IR_CONTROL_ROADMAP.md` | 49KB | IR control future plans |
| `docs/OREI_API_COMMANDS.md` | 18KB | OEM API command reference |
| `docs/MASTER_INDEX.md` | 11KB | Documentation index |

### Layer 10: Utility Scripts & Archive

| File | Description |
|------|-------------|
| `scripts/discover_api.py` | API endpoint discovery tool |
| `scripts/test_telnet.py` | Telnet connection tester |
| `scripts/test_telnet_client.py` | Telnet client tester |
| `scripts/run_webui_test.py` | Web UI test runner |
| `scripts/start_webui.py` | Dev web UI launcher |
| `scripts/restart_driver.ps1` | Windows driver restart script |
| `scripts/convert-icons-to-svg.js` | Icon conversion tool |
| `archive/mock-server.js` | Mock server for development |
| `config/cec_macros.json` | Default CEC macro definitions |
| `config/profiles.json` | Default profile definitions |
| `config/scenes.json` | Default scene definitions |

---

## 🎯 Audit Dimensions

Evaluate every file against ALL of the following dimensions:

### 1. FUNCTIONAL CORRECTNESS
- Do API endpoints match documentation? Cross-reference `docs/API_REFERENCE.md` against actual route registrations in `src/rest_api/app.py`.
- Are REST API response shapes consistent across all endpoints? (Do all return `{success, data, error}`?)
- Does the Web UI's `api.js` call endpoints that actually exist in the backend?
- Does the HA coordinator's data structure match what entity classes expect?
- Do CEC macro step definitions match what the execution engine supports?
- Are scene v1 and scene v2 APIs redundant? Is one deprecated?

### 2. DEAD CODE & UNUSED FILES
- Is `web/js/utils/api-copy.js` a dead copy of `api.js`?
- Are there unused REST API routes registered but never called from any frontend?
- Are there Python functions/classes that are defined but never imported or called?
- Is `archive/` properly excluded from Docker builds and tests?
- Are `scripts/` utilities functional or stale?
- Is `run_server.py` still maintained alongside `run.py`? Are they divergent?
- Is `src/config_state.json` and `src/driver.lock` committed by accident? (These look like runtime artifacts.)

### 3. CODE QUALITY & MAINTAINABILITY
- Identify files over 500 lines that should be split.
- Find duplicated logic across layers (e.g., entity creation in `driver.py` vs `entities.py`).
- Check for consistent error handling patterns (bare `except Exception` vs typed catches).
- Look for f-string usage in logging calls (should use `%s` lazy formatting).
- Identify hardcoded IPs, ports, or credentials.
- Check for proper async patterns (no blocking calls in async functions).
- Review import organization and circular dependency risks.

### 4. INTEGRATION COHERENCE
- **UC Driver**: Is the entity set created in `driver.py` (direct mode) functionally equivalent to what `entities.py` (API mode) creates? Are they kept in sync?
- **HA Component**: Does the HA component's REST API calls match the actual REST API endpoints? (HA calls `/api/status`, `/api/output/status`, `/api/input/status` — do those routes exist?)
- **Flic**: Does `FLIC_SETUP.md` accurately reflect the current REST API routes?
- **Web UI**: Does the frontend's `api.js` hit the same endpoints documented in `API_REFERENCE.md`?
- **WebSocket**: Is the WebSocket broadcast in `rest_api/websocket.py` connected to the frontend's `websocket.js`? Are the event types consistent?

### 5. TEST COVERAGE GAPS
- Which source files have NO corresponding test file?
- Are there REST API endpoints with no test coverage?
- Do tests use proper async mocking or do they rely on `MagicMock` where `AsyncMock` is needed?
- Is the test for `test_hacs_integration.py` actually runnable? (It skips if homeassistant isn't installed — does it ever run in CI?)
- Are there test files in `scripts/` that duplicate tests in `tests/`?

### 6. SECURITY & OPERATIONAL SAFETY
- Is the matrix password stored in plaintext in `config_state.json`?
- Are there any endpoints that accept user input without validation/sanitization?
- Is rate limiting applied consistently across all mutating endpoints?
- Does the Docker health check actually verify application health (not just port binding)?
- Are secrets (passwords, tokens) excluded from Docker images and git?
- Does `.gitleaks.toml` cover all credential patterns in the codebase?

### 7. DOCUMENTATION ACCURACY
- Does the API_REFERENCE.md list all currently registered routes?
- Are there routes in the code not documented?
- Are there documented routes that don't exist in the code?
- Is the README.md feature list accurate for the current state of the codebase?
- Are installation/setup instructions in docs/DOCKER.md correct?

---

## 📤 Expected Output Format

Compile your findings into a structured report with:

### Section 1: Architecture Assessment
- High-level architecture diagram (mermaid)
- Layer dependency analysis
- Identified architectural smells

### Section 2: Findings Table

For each finding:

| ID | Severity | Layer | File(s) | Title | Description |
|----|----------|-------|---------|-------|-------------|

Severity levels:
- 🔴 **Critical**: Breaking bugs, data loss risks, security vulnerabilities
- 🟠 **High**: Functional bugs, integration mismatches, missing error handling
- 🟡 **Medium**: Code quality, maintainability, dead code, test gaps
- 🟢 **Low**: Naming, style, minor improvements

### Section 3: Dead Code Inventory
List every file, function, class, route, or variable that is confirmed dead (defined but never used).

### Section 4: Integration Compatibility Matrix

| Integration | Status | Issues Found | Risk Level |
|-------------|--------|--------------|------------|
| UC Remote 3 | | | |
| Home Assistant | | | |
| Flic Buttons | | | |
| Web UI | | | |
| Docker | | | |

### Section 5: Test Coverage Map

| Source File | Test File | Coverage Level | Gaps |
|-------------|-----------|----------------|------|

### Section 6: Prioritized Action Plan
Sorted by severity and effort, with specific code-level recommendations.

---

## ⚠️ Critical Rules

1. **Read every file** — do not skip files or summarize from filenames alone.
2. **Cross-reference across layers** — the most valuable findings come from mismatches between what the backend provides and what consumers expect.
3. **Verify, don't assume** — if the docs say an endpoint exists, confirm it's in `app.py`'s route table. If a function is exported, confirm it's imported somewhere.
4. **Prioritize actionable findings** — "this could be better" is less useful than "this is broken because X doesn't match Y."
5. **Include exact file paths and line numbers** for every finding.
6. **Provide diffs** for any suggested code changes.
