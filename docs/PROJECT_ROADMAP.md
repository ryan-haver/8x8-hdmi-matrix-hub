# OREI HDMI Matrix Integration Hub - Project Roadmap

> **Vision**: A unified API bridge for home theatre equipment control, accessible from Unfolded Circle Remote 3, Flic smart buttons, Home Assistant, and future integrations.

---
## 🚀 CURRENT SESSION PROGRESS (January 22, 2026)

### ✅ Sprint 5 Complete - Profiles, CEC Macros & Web UI!

**All Sprints Complete:**
- ✅ Sprint 1: All 7 tasks complete
- ✅ Sprint 2: All 10 tasks complete  
- ✅ Sprint 3: All 4 tasks complete (Unit tests, Polling, Signal sensors, WebSocket)
- ✅ Sprint 4: All 6 tasks complete (EDID, LCD, Ext-Audio, Scenes)
- ✅ Sprint 5: All 6 tasks complete (Profiles, CEC Macros, Web UI, Profile Editor)

**Sprint 5 Features Implemented:**
- ✅ Profile system (replaces scenes with icons, macros, CEC config)
- ✅ CEC Macro system (multi-step command sequences with delays)
- ✅ Enhanced Web UI with Profile and Macro management
- ✅ Profile Editor UI (drag-drop outputs, CEC configuration)
- ✅ Macro Editor UI (step builder, command palette)
- ✅ Backward compatibility (auto-migration from scenes.json)

**Test Coverage (January 22, 2026):**
```
283 tests passing (68 config unit + 215 integration)
python -m pytest tests/ -v -k "not test_manual"
```

**API Version:** 2.10.0

**Entity Count: 58 total**
- 1 matrix remote, 8 preset buttons, 8 input CEC remotes
- 8 input signal sensors (shows "Active" or "No Signal")
- 1 power switch
- 8 output media players, 8 output CEC remotes
- 16 output sensors (connection + routing)

**Profile API Endpoints:**
- `GET /api/profiles` - List all profiles
- `GET/POST/PUT/DELETE /api/profile/{id}` - Profile CRUD
- `POST /api/profile/{id}/recall` - Apply profile to matrix
- `GET/POST /api/profile/{id}/cec` - Profile CEC configuration
- `GET/POST /api/profile/{id}/macros` - Profile macro assignments

**CEC Macro API Endpoints:**
- `GET /api/cec/macros` - List all macros
- `GET/POST/PUT/DELETE /api/cec/macro/{id}` - Macro CRUD
- `POST /api/cec/macro/{id}/execute` - Run macro
- `POST /api/cec/macro/{id}/test` - Validate macro

**WebSocket Features:**
- Endpoint: `ws://HOST:8080/ws`
- Events: `connected`, `routing_change`, `connection_change`, `signal_change`, `status_update`, `pong`, `error`
- Commands: `ping`, `get_status`

### Remaining Technical Debt

| ID | Issue | Priority | Notes |
|----|-------|----------|-------|
| TD-08 | Markdown lint warnings | Low | Cosmetic; blanks around headings |
| TD-09 | No OpenAPI/Swagger spec | Low | Would help external integrators |
| TD-10 | Hardcoded 8-port assumption | Low | Some OREI matrices have 4 ports |
| TD-12 | Duplicate drag code | Low | ~150 lines duplicated across 3 components |

### Recent Tech Debt Fixes (January 2026)

✅ **TD-R15 Resolved:** Created `Logger` utility to replace 32+ debug console.log statements
- Debug logging now toggleable via `localStorage.setItem('matrix-debug', 'true')`
- Cleaner console output in production
- Better categorization (API, WebSocket, State)

### Sprint 5 Complete! - Profiles & CEC Macros

✅ **Task #28 Complete:** Profile system (evolution of scenes)
- Profiles include: icon, outputs, CEC config, macro assignments
- Auto-migration from existing scenes.json
- Backward compatibility with scene API

✅ **Task #29 Complete:** CEC Macro system
- Multi-step command sequences with configurable delays
- Support for all CEC commands (power, navigation, playback, volume)
- Macro validation and testing endpoints

✅ **Task #30 Complete:** Web UI enhancements
- Profile management (create, edit, delete, recall)
- Macro management (create, edit, delete, execute)
- Profile Editor with drag-drop output configuration
- CEC configuration per profile

✅ **Task #31 Complete:** Comprehensive test coverage
- 68 unit tests for config.py classes
- 215 REST API integration tests
- 283 total tests passing

🎉 **Sprint 5 Complete!** Profile and Macro system fully implemented.

---
## 📋 DEVELOPMENT STANDARDS & QUALITY GATES

### Code Quality Checklist (Required for Each PR/Feature)

| Category | Requirement | Verification |
|----------|-------------|--------------|
| **Testing** | Unit tests for new classes/functions | `pytest tests/ -v` passes |
| **Testing** | Integration tests for new API endpoints | Coverage includes happy path + error cases |
| **Testing** | Minimum 80% coverage for new code | `pytest --cov=src` |
| **Type Safety** | Type hints on all public functions | `mypy src/` (when enabled) |
| **Documentation** | Docstrings for public APIs | Google-style docstrings |
| **Documentation** | Update API_REFERENCE.md for new endpoints | Endpoint + request/response examples |
| **Documentation** | Update CHANGELOG section in roadmap | Date + summary of changes |
| **Code Style** | Follow existing patterns | Factory pattern for handlers, dataclasses for state |
| **Error Handling** | Proper HTTP status codes | 400 validation, 404 not found, 500 server error |
| **Error Handling** | Graceful degradation | Matrix disconnection doesn't crash server |

### Definition of Done (DoD)

A feature is **DONE** when:
- [ ] All acceptance criteria met
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] No regression in existing tests (`283+ tests passing`)
- [ ] Documentation updated (API_REFERENCE.md, roadmap)
- [ ] Code reviewed for patterns consistency
- [ ] Manual smoke test on Docker deployment

### Commit Message Format

```
[SPRINT-X] Category: Brief description

- Detail 1
- Detail 2

Closes #issue (if applicable)
```

Categories: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### Priority Matrix

| Priority | Criteria | SLA |
|----------|----------|-----|
| 🔴 **P0 - Critical** | Blocks functionality, security issue | Immediate |
| 🟠 **P1 - High** | Major feature, significant UX impact | Current sprint |
| 🟡 **P2 - Medium** | Enhancement, quality improvement | Next sprint |
| 🟢 **P3 - Low** | Nice-to-have, cosmetic | Backlog |

### Test Categories

| Type | Location | Purpose | Run Frequency |
|------|----------|---------|---------------|
| Unit | `tests/test_config.py` | Class/function isolation | Every commit |
| Integration | `tests/test_rest_api.py` | API endpoint behavior | Every commit |
| Manual | `tests/test_manual.py` | Real hardware validation | Pre-release |
| E2E | (future) | Full workflow validation | Pre-release |

---
## 🎯 PRIORITIZED ACTION ITEMS

### Sprint 1: Critical Fixes & Quick Wins ✅ COMPLETE
*Completed: All tasks done*

| # | Task | Impact | Effort | Status |
|---|------|--------|--------|--------|
| 1 | Add `psutil` to requirements.txt/pyproject.toml | 🔴 Blocks Windows | 2 min | ✅ |
| 2 | Move matrix credentials to environment variables | 🔴 Security | 15 min | ✅ |
| 3 | Add `/api/input/next` endpoint | 🔴 Unblocks Flic Twist | 30 min | ✅ |
| 4 | Add `/api/input/previous` endpoint | 🔴 Unblocks Flic Twist | 15 min | ✅ |
| 5 | Add `/api/output/{n}/source/{input}` endpoint for per-output switching | 🟡 Feature | 20 min | ✅ |
| 6 | Update FLIC_SETUP.md with complete documentation | 🟡 Documentation | 1 hr | ✅ |
| 7 | Update HOME_ASSISTANT.md with REST integration examples | 🟡 Documentation | 1 hr | ✅ |

### Sprint 2: Code Quality & New Features ✅ COMPLETE

*Completed: All tasks done*

| # | Task | Impact | Effort | Status |
|---|------|--------|--------|--------|
| 8 | Refactor duplicate CEC handler code (factory pattern) | 🟡 -200 lines | 1 hr | ✅ |
| 9 | Add connection retry with exponential backoff | 🟡 Reliability | 30 min | ✅ |
| 10 | Implement output stream enable/disable (from Control4 driver) | 🟢 Feature | 1 hr | ✅ |
| 11 | Implement HDCP/HDR/Scaler settings (from RTI driver) | 🟢 Feature | 2 hr | ✅ |
| 12 | Implement ARC control per output | 🟢 Feature | 1 hr | ✅ |
| 13 | Implement per-output audio mute | 🟢 Feature | 30 min | ✅ |
| 14 | Add CEC auto-enable before sending commands | 🟢 Reliability | 1 hr | ✅ |
| 15 | Implement preset save functionality | 🟢 Feature | 30 min | ✅ |
| 16 | Create `DriverState` dataclass to reduce globals | 🟡 Code Quality | 1 hr | ✅ |
| 17 | Add type hints to rest_api.py functions | 🟡 Code Quality | 30 min | ✅ |

### Sprint 3: Testing & Monitoring (Week 3) ✅ COMPLETE
*Completed: All 4 tasks done*

| # | Task | Impact | Effort | Status |
|---|------|--------|--------|--------|
| 18 | Create pytest unit tests with mocking | 🟡 Quality | 3 hr | ✅ |
| 19 | Add periodic status polling & entity updates | 🟢 UX | 2 hr | ✅ |
| 20 | Implement signal detection sensors (from `inactive` array) | 🟢 Feature | 1 hr | ✅ |
| 21 | Add WebSocket status push for real-time updates | 🟢 Feature | 2 hr | ✅ |

### Sprint 4: Advanced Features (Week 4+) ✅ COMPLETE
*From Control4/RTI drivers and API discovery*

| # | Task | Impact | Effort | Status |
|---|------|--------|--------|--------|
| 22 | Implement external audio matrix routing | 🟢 Feature | 2 hr | ✅ |
| 23 | Add EDID management per input | 🟢 Feature | 1 hr | ✅ |
| 24 | Implement LCD display timeout settings | 🟢 Feature | 30 min | ✅ |
| 25 | Add system reboot command | 🟢 Feature | 15 min | ✅ |
| 26 | Implement "route to all outputs" command | 🟢 Feature | 30 min | ✅ |
| 27 | Activity-based routing (scenes) | 🟢 Feature | 3 hr | ✅ |

### Sprint 5: Profiles, Macros & Web UI (Week 5) ✅ COMPLETE
*Enhanced user experience and automation*

| # | Task | Impact | Effort | Status |
|---|------|--------|--------|--------|
| 28 | Profile system (evolution of scenes) | 🟢 Feature | 4 hr | ✅ |
| 29 | CEC Macro system | 🟢 Feature | 3 hr | ✅ |
| 30 | Web UI enhancements (Profile/Macro editors) | 🟢 UX | 4 hr | ✅ |
| 31 | Comprehensive test coverage (283 tests) | 🟡 Quality | 3 hr | ✅ |

### Sprint 6: Flic Button + Profile Integration ✅ COMPLETE
*Physical button control for zones and profiles*

| # | Task | Impact | Effort | Status |
|---|------|--------|--------|--------|
| 32 | Flic Hub SDK integration guide | 🟡 Docs | 2 hr | ✅ |
| 33 | Zone-based profile configurations | 🟢 Feature | 2 hr | ✅ |
| 34 | Example macro sequences for Flic buttons | 🟢 Feature | 1 hr | ✅ |
| 35 | Multi-room button mapping guide | 🟡 Docs | 1 hr | ✅ |
| 36 | Flic Twist rotation → input cycling | 🟢 Feature | 1 hr | ✅ |
| 37 | Test with actual Flic hardware | 🟡 Validation | 2 hr | 🔲 |

**Sprint 6 Acceptance Criteria:**
- [x] FLIC_SETUP.md updated with Profile/Macro examples
- [x] At least 3 zone-based profile examples documented (Living Room, Bedroom, Office, Kids Room)
- [x] Flic Twist rotation documented with `/api/input/next` and SDK examples
- [x] Example JSON configurations for each button type
- [x] Flic Hub SDK integration guide with 4 example modules
- [ ] Hardware validation pending (needs physical Flic buttons)

### Sprint 7: Home Assistant HACS Component 🔲 NEXT
*Native HA integration with proper entities*

| # | Task | Impact | Effort | Status |
|---|------|--------|--------|--------|
| 38 | HACS component scaffold | 🟢 Feature | 2 hr | 🔲 |
| 39 | DataUpdateCoordinator for polling | 🟢 Feature | 2 hr | 🔲 |
| 40 | Select entities (output sources) | 🟢 Feature | 2 hr | 🔲 |
| 41 | Button entities (presets, profiles) | 🟢 Feature | 1 hr | 🔲 |
| 42 | Switch entities (power, ARC, mute) | 🟢 Feature | 1 hr | 🔲 |
| 43 | Binary sensors (connection, signal) | 🟢 Feature | 1 hr | 🔲 |
| 44 | Media player entities (CEC control) | 🟢 Feature | 2 hr | 🔲 |
| 45 | Config flow (UI-based setup) | 🟡 UX | 2 hr | 🔲 |
| 46 | HACS repository setup | 🟡 Release | 1 hr | 🔲 |

**Sprint 7 Acceptance Criteria:**
- [ ] `custom_components/orei_matrix/` structure complete
- [ ] All entities discoverable in HA UI
- [ ] Config flow allows IP/port configuration
- [ ] Integration tests for HA component
- [ ] HACS-compatible repository structure

### Sprint 8: API Documentation & Developer Experience 🔲 BACKLOG
*OpenAPI spec and developer tooling*

| # | Task | Impact | Effort | Status |
|---|------|--------|--------|--------|
| 47 | OpenAPI 3.0 specification | 🟡 Docs | 3 hr | 🔲 |
| 48 | Swagger UI integration | 🟡 DX | 1 hr | 🔲 |
| 49 | API versioning strategy | 🟡 Architecture | 1 hr | 🔲 |
| 50 | Postman collection export | 🟡 DX | 1 hr | 🔲 |
| 51 | SDK generation (Python client) | 🟢 Feature | 2 hr | 🔲 |

### Sprint 9: Advanced Automation 🔲 FUTURE
*Scheduling, MQTT, and extended integrations*

| # | Task | Impact | Effort | Status |
|---|------|--------|--------|--------|
| 52 | Schedule engine (cron-like) | 🟢 Feature | 4 hr | 🔲 |
| 53 | MQTT broker integration | 🟢 Feature | 3 hr | 🔲 |
| 54 | Webhook support (outgoing) | 🟢 Feature | 2 hr | 🔲 |
| 55 | Multi-matrix support | 🟢 Feature | 4 hr | 🔲 |
| 56 | 4-port matrix configuration | 🟡 Compat | 2 hr | 🔲 |

---
## 🚀 QUICK REFERENCE: What to Work On Next

### Immediate Priority (Sprint 6)
1. **Flic Hub SDK guide** - Document how to configure Flic Hub to call our API
2. **Zone profiles** - Create example profiles for Living Room, Bedroom, etc.
3. **Macro examples** - Power-on sequences, movie night automation

### Next Up (Sprint 7)
1. **HACS component** - Native Home Assistant integration

### Backlog (Sprint 8+)
1. OpenAPI/Swagger documentation
2. Scheduling engine
3. MQTT integration

---

## 🔧 Technical Debt & Known Issues

*Tracked issues to address in future sprints*

### High Priority (Address in Sprint 4)

| ID | Issue | Location | Sprint | Notes |
|----|-------|----------|--------|-------|
| - | (All high priority items resolved) | - | - | - |

### Medium Priority (Address in Sprint 4-5)

| ID | Issue | Location | Sprint | Notes |
|----|-------|----------|--------|-------|
| - | (All medium priority items resolved) | - | - | ✅ TD-04, TD-07 moved to Resolved |

### Low Priority (Future)

| ID | Issue | Location | Sprint | Notes |
|----|-------|----------|--------|-------|
| TD-08 | Markdown lint warnings | `docs/*.md` | - | Cosmetic; blanks around headings, code fences (mostly in reference docs) |
| TD-09 | No OpenAPI/Swagger spec | `rest_api.py` | Future | Would help external integrators |
| TD-10 | Hardcoded 8-port assumption | Multiple files | Future | Some OREI matrices have 4 ports |
| TD-12 | Duplicate drag code across 3 components | `cec-tray.js`, `quick-actions-drawer.js`, `route-all-drawer.js` | Future | ~150 lines duplicated, could use shared mixin/utility in future refactor |

### Resolved ✅

| ID | Issue | Resolution | Sprint |
|----|-------|------------|--------|
| TD-R15 | Excessive console.log statements | Created Logger utility with debug toggle; replaced 32+ console.logs | TD Sprint |
| TD-R1 | CEC handler duplication | Factory pattern `create_cec_command_handler()` | Sprint 2 |
| TD-R2 | No connection retry | Exponential backoff with jitter | Sprint 2 |
| TD-R3 | Missing psutil dependency | Added to requirements.txt | Sprint 1 |
| TD-R4 | Global state sprawl | Introduced `DriverState` dataclass (partial) | Sprint 2 |
| TD-R5 | `route_input_to_all_outputs` calling undefined method | Fixed to use `switch_input` with correct args | Sprint 2 |
| TD-R6 | Docs out of date with v2.2.0 endpoints | Updated HOME_ASSISTANT.md and FLIC_SETUP.md | Sprint 2 |
| TD-R10 | Unused `_writer` attribute | Removed from `orei_matrix.py` | Sprint 3 |
| TD-R11 | Inconsistent preset vs input naming | Renamed to `_input_names`, fixed semantic confusion | Sprint 3 |
| TD-R7 | No unit tests with mocking | 27 pytest unit tests with AsyncMock | Sprint 3 |
| TD-R8 | No integration test suite | 31 aiohttp integration tests (including WebSocket) | Sprint 3 |
| TD-R9 | Manual hardware tests breaking CI | Added pytest skip markers | Sprint 3 |
| TD-R12 | No request rate limiting | Added sliding window rate limiter (30 req/10s) | Sprint 3 |
| TD-R13 | DriverState dataclass underutilized | Added accessor functions `get_state()`, `get_matrix()`, `set_matrix()`, `set_input_names()`, `set_output_names()` | Sprint 3 |
| TD-R14 | Missing error recovery for WebSocket | Added automatic reconnection with exponential backoff (5s-60s) | Sprint 3 |

---

## 📊 Project Status Overview

| Phase | Component | Status | Priority |
|-------|-----------|--------|----------|
| 1.0 | Unfolded Circle Integration | ✅ Complete | - |
| 1.1 | CEC Control | ✅ Complete | - |
| 2.0 | REST API Foundation | ✅ Complete | - |
| 2.1 | Flic Button Integration | ✅ Complete | - |
| 2.2 | Advanced Matrix Control | ✅ Complete | - |
| 2.3 | Code Quality Improvements | ✅ Complete | - |
| 2.4 | Profiles & CEC Macros | ✅ Complete | - |
| 2.5 | Web UI (Profile/Macro Editors) | ✅ Complete | - |
| 2.6 | Flic + Profiles Integration | ✅ Complete | - |
| 3.0 | Home Assistant Integration | 🟡 REST Ready | Medium |
| 3.1 | HACS Custom Component | 🔲 Sprint 7 | Medium |
| 3.2 | Alexa (via HA) | 🔲 Planned | Low |
| 4.0 | Scheduling & Automation | 🔲 Future | Low |
| 4.1 | Web Dashboard (React/Vue) | 🔲 Future | Low |
| 4.2 | MQTT Integration | 🔲 Future | Low |

---

## Phase 1: Unfolded Circle Integration ✅ COMPLETE

### 1.0 Core Driver
- [x] WebSocket server on port 9095
- [x] mDNS discovery for Remote 3
- [x] Static `driver_url` for fast reconnection
- [x] Docker containerization
- [x] Configuration persistence
- [x] 8 preset buttons with dynamic names
- [x] Matrix remote entity with UI pages

### 1.1 CEC Control
- [x] CEC command mapping (19 commands)
- [x] Input device CEC control (PS3, AppleTV, etc.)
- [x] Output device CEC control (TVs)
- [x] Per-input CEC remote entities
- [x] Navigation UI pages
- [x] Playback UI pages

---

## Phase 2: REST API & External Integrations

### 2.0 REST API Foundation ✅ COMPLETE
**Goal**: HTTP API for external integrations (Flic, Home Assistant, scripts)

#### Endpoints Implemented:
| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/status` | Matrix status (power, routing, names) | ✅ |
| GET | `/api/status/full` | Comprehensive status from all endpoints | ✅ |
| GET | `/api/status/outputs` | Detailed output status (HDCP, HDR, connection) | ✅ |
| GET | `/api/status/inputs` | Detailed input status (signal detection) | ✅ |
| GET | `/api/status/cec` | CEC enabled status per port | ✅ |
| GET | `/api/status/system` | System settings (beep, lock, mode) | ✅ |
| GET | `/api/status/device` | Device/firmware information | ✅ |
| GET | `/api/presets` | List all presets with names | ✅ |
| POST | `/api/preset/{1-8}` | Recall a preset | ✅ |
| POST | `/api/switch` | Route input to output | ✅ |
| POST | `/api/power/on` | Power on matrix | ✅ |
| POST | `/api/power/off` | Power off matrix | ✅ |
| GET | `/api/inputs` | List inputs with names | ✅ |
| GET | `/api/outputs` | List outputs with names | ✅ |
| POST | `/api/cec/input/{n}/{cmd}` | CEC to input device | ✅ |
| POST | `/api/cec/output/{n}/{cmd}` | CEC to output device | ✅ |
| GET | `/api/health` | Health check endpoint | ✅ |
| GET | `/api/cec/commands` | List available CEC commands | ✅ |
| GET | `/api` | API documentation | ✅ |
| POST | `/api/system/beep` | Enable/disable system beep | ✅ |
| POST | `/api/system/panel_lock` | Lock/unlock front panel | ✅ |

#### Endpoints Needed (Sprint 1):
| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/api/input/next` | Cycle to next input on primary output | 🔲 |
| POST | `/api/input/previous` | Cycle to previous input on primary output | 🔲 |
| POST | `/api/output/{n}/source` | Set source for specific output | 🔲 |

### 2.1 Flic Button Integration 🟡 ENHANCED FOR PROFILES
**Goal**: Control zones, profiles, and CEC macros from Flic buttons

#### Button Types & Capabilities:
| Button | Actions | Best Use Case |
|--------|---------|---------------|
| **Flic Original** | Click, Double-click, Hold | Room-specific profile switching |
| **Flic Duo** | Left click, Right click, Both click | Two-zone control or profile pairs |
| **Flic Twist** | Rotate CW/CCW, Press | Input cycling + profile recall |

#### Zone-Based Configuration (Per Room):
| Location | Button | Action | API Endpoint | Use Case |
|----------|--------|--------|--------------|----------|
| Living Room | Original | Click | `POST /api/profile/living_room_tv/recall` | TV + soundbar on, route AppleTV |
| Living Room | Original | Double | `POST /api/profile/living_room_gaming/recall` | Route PS5, gaming audio preset |
| Living Room | Original | Hold | `POST /api/cec/macro/living_room_off/execute` | Power off TV + all devices |
| Bedroom | Original | Click | `POST /api/profile/bedroom_streaming/recall` | Bedroom TV + Shield |
| Bedroom | Original | Hold | `POST /api/cec/macro/bedroom_off/execute` | Power off bedroom zone |

#### Flic Duo Configurations:
| Location | Button | Action | API Endpoint | Use Case |
|----------|--------|--------|--------------|----------|
| Hallway | Duo | Left | `POST /api/profile/all_off/recall` | Whole house off |
| Hallway | Duo | Right | `POST /api/profile/movie_night/recall` | Multi-room movie setup |
| Hallway | Duo | Both | `POST /api/cec/macro/all_power_on/execute` | Power on all displays |

#### Flic Twist Configurations:
| Location | Button | Action | API Endpoint | Use Case |
|----------|--------|--------|--------------|----------|
| Coffee Table | Twist | Rotate CW | `POST /api/input/next?output=1` | Cycle through inputs |
| Coffee Table | Twist | Rotate CCW | `POST /api/input/previous?output=1` | Cycle backwards |
| Coffee Table | Twist | Press | `POST /api/profile/quick_switch/recall` | Toggle between two favorites |

#### Creative Automation Examples:

**"Movie Night" Button (Flic Original):**
1. Click → `POST /api/profile/movie_night/recall`
   - Routes AppleTV to living room TV (output 1)
   - Routes same source to soundbar (output 2)
   - Executes power-on macro (TV + soundbar + AppleTV)
   
2. Double-click → `POST /api/cec/macro/dim_lights_play/execute`
   - (Future: integrate with smart lights)
   - Sends CEC PLAY to AppleTV

3. Hold → `POST /api/cec/macro/movie_night_off/execute`
   - Power off TV, soundbar, AppleTV in sequence

**"Gaming Mode" Button (Flic Original):**
1. Click → `POST /api/profile/gaming/recall`
   - Routes PS5 to TV with game mode EDID
   - Disables soundbar ARC, uses TV speakers for low latency

**"Input Dial" (Flic Twist on coffee table):**
- Rotate to cycle inputs on primary display
- Press to toggle between "last two" sources

#### Sprint 6 Tasks:
| # | Task | Impact | Status |
|---|------|--------|--------|
| 32 | Flic Hub SDK integration guide | 🟡 Docs | 🔲 |
| 33 | Profile-aware Flic configurations | 🟢 Feature | 🔲 |
| 34 | Example macro sequences for Flic | 🟢 Feature | 🔲 |
| 35 | Zone-based button mapping guide | 🟡 Docs | 🔲 |
| 36 | Test with actual Flic hardware | 🟡 Validation | 🔲 |

#### API Endpoints Ready for Flic:
- ✅ `POST /api/profile/{id}/recall` - Recall any profile
- ✅ `POST /api/cec/macro/{id}/execute` - Run any macro
- ✅ `POST /api/input/next?output={n}` - Cycle inputs
- ✅ `POST /api/input/previous?output={n}` - Cycle backwards
- ✅ `POST /api/preset/{1-8}` - Recall hardware presets
- ✅ `POST /api/switch` - Direct routing control
- ✅ `POST /api/power/on` and `/api/power/off` - Matrix power

### 2.2 Advanced Matrix Control 🔲 PLANNED
**Goal**: Implement remaining OREI API capabilities discovered from Control4/RTI drivers

#### Output Settings (from RTI/Control4 drivers):
| Feature | API Command | UC Entity | Status |
|---------|-------------|-----------|--------|
| Output Stream On/Off | `set output stream` | Switch | 🔲 |
| HDCP Mode (1.4/2.2/Auto) | `set hdcp mode` | Select | 🔲 |
| HDR Mode (Pass/Convert/Auto) | `set hdr mode` | Select | 🔲 |
| Scaler Mode (4K/1080p/Pass) | `set scaler mode` | Select | 🔲 |
| ARC Enable/Disable | `set arc` | Switch | 🔲 |
| Audio Mute per Output | `set audio mute` | Switch | 🔲 |

#### Input Settings:
| Feature | API Command | UC Entity | Status |
|---------|-------------|-----------|--------|
| EDID Mode per Input | `set input edid` | Select | ✅ |
| Signal Detection | `get input status` | Sensor | 🔲 |

#### System Settings:
| Feature | API Command | UC Entity | Status |
|---------|-------------|-----------|--------|
| Preset Save | `set routing save` | Button | 🔲 |
| LCD Display Timeout | `set lcd on time` | Select | ✅ |
| System Reboot | `set reboot` | Button | 🔲 |

#### Audio Matrix (External Audio Outputs):
| Feature | API Command | UC Entity | Status |
|---------|-------------|-----------|--------|
| Ext-Audio Mode | `set ext-audio mode` | Select | 🔲 |
| Ext-Audio Source | `set ext-audio source` | MediaPlayer | 🔲 |
| Ext-Audio Enable | `set ext-audio enable` | Switch | 🔲 |

#### CEC Improvements:
| Feature | Description | Status |
|---------|-------------|--------|
| Auto-enable CEC | Enable CEC on port before sending commands | 🔲 |
| CEC Status Sync | Query CEC enabled status, update UC entities | 🔲 |
| "Active Source" CEC | Tell TV to switch to matrix input | 🔲 |

### 2.3 Code Quality Improvements 🔲 PLANNED
**Goal**: Improve maintainability, reliability, and developer experience

#### Critical Fixes:
- [ ] **Add `psutil` to dependencies** (blocks Windows installs)
- [ ] **Move credentials to environment variables** (security)
  ```python
  # Current (hardcoded):
  login_cmd = {"user": "Admin", "password": "admin"}
  # Target (env vars):
  user = os.environ.get("OREI_USER", "Admin")
  password = os.environ.get("OREI_PASSWORD", "admin")
  ```

#### Refactoring:
- [ ] Extract CEC handler factory to reduce ~200 lines of duplication
- [ ] Create `DriverState` dataclass to encapsulate global state
- [ ] Add consistent type hints across all modules
- [ ] Create error decorator for REST API connection checks

#### Reliability:
- [ ] Add connection retry with exponential backoff
- [ ] Implement periodic status polling (every 30s)
- [ ] Add WebSocket status push for entity updates

#### Testing:
- [ ] Create pytest fixtures with mocked HTTP responses
- [ ] Add unit tests for `orei_matrix.py` (80%+ coverage)
- [ ] Add integration tests for REST API endpoints
- [ ] Add error path testing

---

## Phase 3: Home Assistant Integration 🔲 PLANNED

### 3.0 Home Assistant REST Integration (Quick Start)
**Goal**: Get HA working immediately with existing REST API

```yaml
# configuration.yaml - Example REST Commands
rest_command:
  orei_preset_gaming:
    url: "http://192.168.1.145:8080/api/preset/1"
    method: POST
  orei_preset_streaming:
    url: "http://192.168.1.145:8080/api/preset/2"
    method: POST
  orei_power_off:
    url: "http://192.168.1.145:8080/api/power/off"
    method: POST
  orei_cec_play:
    url: "http://192.168.1.145:8080/api/cec/input/{{ input }}/play"
    method: POST

# Example REST Sensors
sensor:
  - platform: rest
    name: "OREI Matrix Status"
    resource: "http://192.168.1.145:8080/api/status"
    value_template: "{{ value_json.data.power }}"
    json_attributes_path: "$.data"
    json_attributes:
      - routing
      - input_names
      - output_names

# Example Template Sensors
template:
  - sensor:
      - name: "TV Current Input"
        state: >
          {% set routing = state_attr('sensor.orei_matrix_status', 'routing') %}
          {% set names = state_attr('sensor.orei_matrix_status', 'input_names') %}
          {{ names[routing[0] - 1] if routing else 'Unknown' }}
```

### 3.1 HACS Custom Component (Full Integration)
**Goal**: Native HA integration with proper entities

#### Entity Types:
| Entity | Type | Description |
|--------|------|-------------|
| `select.orei_output_1_source` | Select | Input selection for Output 1 |
| `button.orei_preset_1` | Button | Recall preset 1 |
| `media_player.orei_input_2` | Media Player | CEC control for AppleTV |
| `switch.orei_matrix_power` | Switch | Matrix power on/off |
| `switch.orei_output_1_stream` | Switch | Output 1 video enable |
| `binary_sensor.orei_output_1_connected` | Binary Sensor | Display detected |
| `binary_sensor.orei_input_3_signal` | Binary Sensor | Signal present |
| `select.orei_output_1_hdcp` | Select | HDCP mode selection |

#### Directory Structure:
```
custom_components/orei_matrix/
├── __init__.py
├── manifest.json
├── config_flow.py
├── const.py
├── coordinator.py      # DataUpdateCoordinator for polling
├── button.py
├── select.py
├── switch.py
├── media_player.py
├── binary_sensor.py
└── sensor.py
```

### 3.2 Alexa Integration (via Home Assistant)
**Goal**: Voice control through Alexa

#### Example Phrases:
- *"Alexa, turn on PS5"* → Recalls PS5 preset
- *"Alexa, switch to Apple TV"* → Routes AppleTV to TV
- *"Alexa, pause the Shield"* → CEC pause to Shield
- *"Alexa, turn off the matrix"* → Power off

---

## Phase 4: Future Enhancements 🔮

### 4.0 Advanced Features (from Control4/RTI Analysis)
- [x] Activity-based routing (Profiles with icons, CEC, macros) ✅
- [ ] Scheduling (auto-switch inputs at specific times)
- [ ] Web dashboard UI (React/Vue rewrite)
- [ ] MQTT support for IoT devices

### 4.1 Voice Assistants
- [ ] Google Home integration
- [ ] Apple HomeKit via HomeKit Bridge
- [ ] Native Alexa skill (without HA)

### 4.2 Hardware Expansion
- [ ] Support for other HDMI matrix brands
- [x] Audio matrix support (separate audio routing) - ✅ Implemented in Sprint 4
- [ ] AV receiver integration

---

## 🗂️ Workspace Structure

```
unfoldedcircle-orei-hdmi-matrix-integration/
├── src/
│   ├── __init__.py
│   ├── driver.py           # Main UC integration driver
│   ├── orei_matrix.py      # OREI matrix control library
│   ├── rest_api.py         # REST API server (87 endpoints)
│   └── config.py           # Configuration: Profiles, Scenes, Macros, CEC
├── tests/
│   ├── conftest.py         # Pytest fixtures with mock_matrix
│   ├── test_config.py      # 68 unit tests for config classes
│   ├── test_rest_api.py    # 215 integration tests
│   ├── test_all_features.py
│   ├── test_all_formats.py
│   ├── test_connection.py
│   └── test_manual.py      # Hardware validation (skipped in CI)
├── docs/
│   ├── PROJECT_ROADMAP.md      # This file
│   ├── API_REFERENCE.md        # REST API documentation
│   ├── OREI_API_COMMANDS.md    # Matrix protocol reference
│   ├── FLIC_SETUP.md           # Flic button configuration
│   ├── HOME_ASSISTANT.md       # HA integration guide
│   ├── DOCKER.md               # Docker deployment
│   └── BK-808 Control4 Driver/ # Reference drivers
├── data/                   # Runtime config (Docker volume)
│   └── config_state.json   # Profiles, macros, CEC configs
├── driver.json             # UC driver metadata
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 📝 Development Notes

### Current Configuration
- **Docker Host**: 192.168.1.145
- **UC Integration Port**: 9095
- **REST API Port**: 8080
- **OREI Matrix IP**: 192.168.0.100
- **OREI Matrix Port**: 443 (HTTPS)

### Input Device Mapping
| Input | Device | CEC Support |
|-------|--------|-------------|
| 1 | PS3 | ⚠️ Limited |
| 2 | AppleTV | ✅ Good |
| 3 | Computer | ❌ None |
| 4 | Switch | ⚠️ Limited |
| 5 | Shield | ✅ Good |
| 6 | PS5 | ✅ Good |
| 7 | Analogue | ❌ None |
| 8 | TBD | ❓ Unknown |

### Output Device Mapping
| Output | Device | CEC | ARC |
|--------|--------|-----|-----|
| 1 | TV | ✅ | ✅ |
| 2 | Soundbar | ✅ | ❌ |
| 3-8 | Unused | - | - |

### API Command Reference (from Control4/RTI Drivers)
See [OREI_API_COMMANDS.md](OREI_API_COMMANDS.md) for complete protocol documentation.

| Category | Verified | Implemented | Discovered |
|----------|----------|-------------|------------|
| Auth | 1 | 1 | 0 |
| Status | 7 | 7 | 0 |
| Control | 5 | 3 | 2 |
| CEC | 2 | 2 | 0 |
| Output Settings | 6 | 0 | 6 |
| Ext-Audio | 3 | 0 | 3 |
| System | 2 | 0 | 2 |
| **Total** | **26** | **13** | **13** |

---

## 🔄 Change Log

### January 22, 2026
- **Sprint 5 Complete:** Profiles, CEC Macros, Web UI enhancements
- **Test Coverage:** 283 tests (68 unit + 215 integration)
- Added Development Standards & Quality Gates section
- Added Sprint 6-9 planning with acceptance criteria
- Enhanced Flic integration section with zone-based examples
- Added Definition of Done (DoD) checklist
- Added priority matrix and commit message format
- Fixed `ProfileManager.update_profile_cec_config()` bug found via testing
- Updated API version to 2.10.0

### January 14, 2026
- Added prioritized Sprint 1-4 action items
- Added Phase 2.2 (Advanced Matrix Control) based on Control4/RTI driver analysis
- Added Phase 2.3 (Code Quality Improvements) from code review
- Expanded Phase 3 with detailed HA REST integration examples
- Added API command inventory from driver analysis
- Updated workspace structure to reflect current layout

### January 13, 2026
- Completed Phase 2.0 REST API v2.0
- Added extended status endpoints
- Added system control endpoints (beep, panel lock)

### January 12, 2026
- Completed Phase 1.0 and 1.1
- Docker deployment working
- CEC control functional

---

*Last Updated: January 22, 2026*
