# OREI HDMI Matrix Integration Hub - Master Index

> **Last Updated:** January 30, 2026 | **Version:** 2.10.0

This document serves as the central navigation hub for all project documentation. It consolidates roadmaps, design specs, API references, and implementation guides into a single organized structure.

---

## 🗺️ Quick Navigation

| Category             | Primary Document                                               | Purpose                              |
| -------------------- | -------------------------------------------------------------- | ------------------------------------ |
| **Project Overview** | [README.md](../README.md)                                      | Project introduction and quick start |
| **API Reference**    | [API_REFERENCE.md](API_REFERENCE.md)                           | Complete REST API documentation      |
| **Design Specs**     | [Routing Profiles Design](#design-specifications)              | UI/UX mockups and design system      |
| **Implementation**   | [WEB_UI_IMPLEMENTATION_PLAN.md](WEB_UI_IMPLEMENTATION_PLAN.md) | Frontend architecture                |
| **Roadmap**          | [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)                       | Sprint planning and progress         |

---

## 📋 Documentation Structure

### 1. Project Core

| Document                              | Location           | Description                                   |
| ------------------------------------- | ------------------ | --------------------------------------------- |
| [README.md](../README.md)             | `/README.md`       | Project overview, features, quick start guide |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | `/CONTRIBUTING.md` | Contribution guidelines                       |
| [LICENSE](../LICENSE)                 | `/LICENSE`         | License information                           |

### 2. Roadmaps & Planning

| Document                                                       | Location | Description                                             | Status      |
| -------------------------------------------------------------- | -------- | ------------------------------------------------------- | ----------- |
| [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)                       | `/docs/` | **Master roadmap** - Sprints 1-9, tech debt, change log | 🟢 Active   |
| [WEB_UI_IMPLEMENTATION_PLAN.md](WEB_UI_IMPLEMENTATION_PLAN.md) | `/docs/` | Frontend architecture, components, phases               | ✅ Complete |
| [IR_CONTROL_ROADMAP.md](IR_CONTROL_ROADMAP.md)                 | `/docs/` | IR blaster integration planning                         | 🔲 Future   |

### 3. API & Protocol Documentation

| Document                                                   | Location | Description                                   |
| ---------------------------------------------------------- | -------- | --------------------------------------------- |
| [API_REFERENCE.md](API_REFERENCE.md)                       | `/docs/` | REST API endpoints, request/response examples |
| [OREI_API_COMMANDS.md](OREI_API_COMMANDS.md)               | `/docs/` | Raw matrix protocol commands (from BK-808)    |
| [CEC_CONTROL_ARCHITECTURE.md](CEC_CONTROL_ARCHITECTURE.md) | `/docs/` | CEC command mapping and architecture          |

### 4. Integration Guides

| Document                                                                     | Location | Description                             |
| ---------------------------------------------------------------------------- | -------- | --------------------------------------- |
| [HOME_ASSISTANT.md](HOME_ASSISTANT.md)                                       | `/docs/` | Home Assistant REST/sensor integration  |
| [FLIC_SETUP.md](FLIC_SETUP.md)                                               | `/docs/` | Flic button configuration with profiles |
| [UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md](UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md) | `/docs/` | UC Remote 3 driver setup                |
| [DOCKER.md](DOCKER.md)                                                       | `/docs/` | Docker deployment instructions          |

### 5. Reference Materials

| Document                                               | Location | Description                         |
| ------------------------------------------------------ | -------- | ----------------------------------- |
| [vendor/README.md](vendor/README.md)                   | `/docs/vendor/` | Where to get the BK-808 manual, firmware, Control4/RTI drivers (not redistributed) |
| [remote3-rest-core-api.md](remote3-rest-core-api.md)   | `/docs/` | UC Remote 3 REST API reference      |
| [remote3-websocket-\*.md](.)                           | `/docs/` | UC Remote 3 WebSocket API reference |

---

## 🎨 Design Specifications

### Phase 1 Design (39 Mockups) ✅ APPROVED

All design mockups are stored in the knowledge base and referenced from the approved design document.

**Primary Design Document:**

- Knowledge Base: `orei_hdmi_matrix_integration/artifacts/design/routing_profiles_approved.md`

**Design System:**

- **Theme:** Premium Dark + Cyan Accents
- **Style:** Glassmorphism with glow effects
- **Background:** Tron-inspired circuit patterns
- **Typography:** System fonts with clear hierarchy

**Key Mockup Categories:**

| Category         | Count | Examples                                       |
| ---------------- | ----- | ---------------------------------------------- |
| Routing Profiles | 3     | Dashboard, Card Wizard, Profile Management     |
| Device Setup     | 5     | Input/Output Wizards, Icon Picker              |
| Scenes & CEC     | 3     | Scene Wizard, Macro Editor, Audio Panel        |
| UI Refresh       | 9     | Dashboard, Matrix Grid, Settings, CEC Controls |
| UX Patterns      | 15    | Navigation, Loading States, Dialogs, Recovery  |
| Supporting       | 6     | About, Presets, API Copy, Tablet Layout        |

---

## 🚀 Implementation Status

### Completed Phases (1-8)

| Phase | Name                | Status | Key Deliverables                                |
| ----- | ------------------- | ------ | ----------------------------------------------- |
| 1     | Backend Persistence | ✅     | Device settings API, JSON storage               |
| 2     | Theme Engine        | ✅     | CSS variables, glassmorphism utilities          |
| 3     | Core UI Refresh     | ✅     | Matrix grid, mobile nav, settings panel         |
| 4     | UX Infrastructure   | ✅     | Skeleton loaders, empty states, confirm dialogs |
| 5     | Device Setup        | ✅     | Setup wizard, multi-step flow                   |
| 6     | Routing Profiles    | ✅     | Context menus, profile management               |
| 7     | Advanced UX         | ✅     | Tooltips, keyboard shortcuts                    |
| 8     | Supporting Features | ✅     | About dialog, status indicators                 |

### Current Phase (9)

| Phase | Name                      | Status         | Focus                              |
| ----- | ------------------------- | -------------- | ---------------------------------- |
| 9     | Design System Unification | 🔄 In Progress | Tron aesthetic, sidebar navigation |

**Phase 9 Tasks:**

- [ ] Global CSS tokenization (align all components)
- [ ] Modal & form styling refresh
- [ ] Dashboard card glow/lift patterns
- [ ] Tron-style background patterns
- [ ] Sidebar navigation implementation
- [ ] Final animation polish

---

## 📁 Project Directory Structure

```
unfoldedcircle-orei-hdmi-matrix-integration/
├── docs/                    # All documentation
│   ├── MASTER_INDEX.md      # ← You are here
│   ├── PROJECT_ROADMAP.md   # Sprint planning
│   ├── API_REFERENCE.md     # REST API docs
│   └── ...                  # Other docs
├── src/                     # Python source
│   ├── driver.py            # UC integration driver
│   ├── orei_matrix.py       # Matrix control library
│   ├── rest_api/            # Modular REST API
│   └── config.py            # Configuration classes
├── web/                     # Web UI
│   ├── index.html           # SPA entry point
│   ├── css/                 # Stylesheets
│   │   ├── theme.css        # Design system tokens
│   │   ├── style.css        # Base styles
│   │   ├── components.css   # Component styles
│   │   └── ...
│   └── js/                  # JavaScript
│       ├── app.js           # Main application
│       ├── components/      # UI components
│       └── ...
├── tests/                   # Test suites
│   ├── test_config.py       # 68 unit tests
│   └── test_rest_api.py     # 215 integration tests
├── data/                    # Runtime data
│   ├── config_state.json    # Profiles, macros
│   └── device_settings.json # Custom names/icons
└── docker-compose.yml       # Container deployment
```

---

## 🔗 External Resources

### Knowledge Base (Antigravity)

| Resource       | Path                            | Description                    |
| -------------- | ------------------------------- | ------------------------------ |
| Main KI        | `orei_hdmi_matrix_integration/` | Consolidated project knowledge |
| Design Mockups | Conversation `5af83abb-*`       | 39 approved UI mockups         |
| Icon Library   | `noun_project_icon_scraper/`    | Icon scraping tooling          |

### APIs & Ports

| Service       | Port | Description                   |
| ------------- | ---- | ----------------------------- |
| REST API      | 8080 | HTTP API + WebSocket + Web UI |
| UC Driver     | 9095 | Unfolded Circle integration   |
| Matrix Device | 443  | OREI BK-808 (HTTPS)           |

---

## 📊 Test Coverage

```
Total: 283 tests
├── Unit Tests: 68 (test_config.py)
└── Integration: 215 (test_rest_api.py)

Run: python -m pytest tests/ -v -k "not test_manual"
```

---

## 🏷️ Version History

| Version | Date         | Highlights                   |
| ------- | ------------ | ---------------------------- |
| 2.10.0  | Jan 22, 2026 | Profiles, CEC Macros, Web UI |
| 2.9.0   | Jan 21, 2026 | Profile Editor, Macro Editor |
| 2.8.0   | Jan 20, 2026 | WebSocket status push        |
| 2.7.0   | Jan 19, 2026 | Signal detection sensors     |
| ...     | ...          | See PROJECT_ROADMAP.md       |

---

## 📝 Quick Commands

```bash
# Start development server
python run.py

# Run tests
python -m pytest tests/ -v

# Docker deployment
docker-compose up -d

# Access Web UI
open http://localhost:8080
```

---

## ❓ Need Help?

1. **API Questions:** See [API_REFERENCE.md](API_REFERENCE.md)
2. **Integration Setup:** See [HOME_ASSISTANT.md](HOME_ASSISTANT.md) or [FLIC_SETUP.md](FLIC_SETUP.md)
3. **Design Questions:** See mockups in Knowledge Base
4. **Development:** See [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)

---

_This index is the single source of truth for project documentation navigation._
