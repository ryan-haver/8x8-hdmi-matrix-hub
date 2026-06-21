# Phase 8: Unified Profile/Scene Architecture

> Spec version 1.0 — 2026-06-20

## Goals

1. Collapse Profiles, Quick Actions, Presets, and System Actions into a unified, modular architecture
2. All user-configurable things are either a **Profile** or a **Scene**
3. Scenes are ordered groupings of Profiles + System Actions
4. Conflict detection at scene-creation time, with per-scene override capability
5. Execution history tracked per Profile (last 7 days), tied to the Scene that triggered it
6. Password protection with inheritance — a Scene containing a protected Profile requires passcode

---

## Core Entities

### Profile

Atomic unit of work. Contains routing + per-output settings + CEC macro sequence.

```python
class Profile:
    id: str                           # stable identifier
    name: str
    icon: str                         # emoji

    # Per-output routing + settings
    outputs: {
        int: {                        # output number 1-8
            input: int,               # source input (1-8)
            enabled: bool,            # stream on/off
            hdcp: int,               # 1=1.4, 2=2.2, 3=follow
            hdr: int,               # 1=pass, 2=convert, 3=auto
            scaler: int,             # 0=pass, 1=4K, 2=8K
            arc: bool,               # ARC on/off
            audio_mute: bool,         # mute per output
        }
    }

    # CEC commands executed after routing is applied
    macros: [
        { command: str, params: dict }
    ]

    # Display flags
    favorite: bool
    dashboard_visible: bool
    dashboard_order: int

    # Password protection
    password_protected: bool
    passcode_hash: str               # bcrypt, never plaintext

    # Execution history (last 7 days)
    execution_log: [
        {
            timestamp: datetime,
            scene_id: str | None,
            scene_name: str | None,
            status: "success" | "error",
            error: str | None
        }
    ]
```

### Scene

Named grouping of Profiles and System Actions, executed in order.

```python
class Scene:
    id: str
    name: str
    icon: str

    # Ordered steps
    steps: [
        { type: "profile",  id: str },
        { type: "system_action", key: str, params: dict }
    ]

    # Per-scene overrides — disables settings in constituent Profiles
    # without modifying the Profiles themselves
    # Structure: { profile_id: { output_num: { setting_key: True } } }
    # The True value means "disabled for this Scene execution"
    overrides: {
        str: {                       # profile_id
            int: {                   # output_num
                str: bool            # setting_key: disabled
            }
        }
    }

    # Display flags
    favorite: bool
    dashboard_visible: bool
    dashboard_order: int

    # Password protection (inherits from contained Profiles)
    password_protected: bool         # true if any step is a protected Profile
    passcode_hash: str | None        # set if scene itself is protected

    # Execution state
    last_executed: datetime | None
    execution_history: [             # last 7 days
        {
            timestamp: datetime,
            status: "success" | "error",
            steps_completed: int,
            total_steps: int,
            error: str | None
        }
    ]
```

### SystemAction

Built-in matrix operations. Not persisted (except user preferences like rename/order). Hardcoded defaults, user can rename and reorder but not change behavior.

```
SystemAction {
    key: str                         # "mute_all_audio", "reboot", "beep_on", etc.
    label: str                       # user-editable display name
    icon: str                         # user-editable
    enabled: bool                    # can be disabled
    order: int                        # sort order in Settings list
}
```

#### SystemAction Key Inventory

**Routing templates:**
- `route_all_to_output` — route selected input to specific output (requires `output` param)
- `route_one_to_one` — mirrored routing for all 8 outputs
- `power_off_all` — standby all outputs
- `mute_all_audio` — mute all outputs
- `unmute_all_audio` — unmute all outputs

**System settings:**
- `beep_on` / `beep_off`
- `panel_lock_on` / `panel_lock_off`
- `lcd_timeout_<mode>` — timeout modes: off, 10s, 30s, 60s, always_on
- `system_reboot`

**Hardware presets:**
- `preset_recall_<n>` — recall preset 1-8 (n = 1-8)

---

## Data Files

| File | Contents |
|------|----------|
| `profiles.json` | List of all Profile objects |
| `scenes.json` | List of all Scene objects |
| `system_actions.json` | User prefs for SystemActions (renames, order, enabled) — not the actions themselves |

---

## Conflict Detection

### What is a conflict?

When a Scene contains two or more Profiles targeting the same output with **different non-default values** for any setting:

```
Profile A: output[1].hdcp = 2  (HDCP 2.2)
Profile B: output[1].hdcp = 1  (HDCP 1.4)
→ Conflict on output 1, setting hdcp
```

### Detection time

At **scene save / profile add time** — not at execution time.

### Conflict UI

When a conflict is detected, the API returns a conflict report:

```json
{
  "success": false,
  "error": "scene_has_conflicts",
  "conflicts": [
    {
      "output": 1,
      "setting": "hdcp",
      "profiles": [
        { "id": "profile_a", "name": "Profile A", "value": 2 },
        { "id": "profile_b", "name": "Profile B", "value": 1 }
      ]
    }
  ]
}
```

The client shows each conflict with checkboxes — user checks which profiles' settings should be **disabled** (overridden) in this scene.

### Override structure

Checking "disable Profile A's hdcp setting" creates:

```python
overrides = {
    "profile_a": {
        1: { "hdcp": True }    # True = disabled
    }
}
```

During scene execution, when Profile A is applied, the `hdcp` setting for output 1 is skipped (the matrix's current value is left unchanged).

### Default values (no conflict)

If all profiles set `hdcp = 3` (follow) for output 1, that's not a conflict — they all agree.

---

## Password Protection

### Rules

1. Any Profile or Scene can be password-protected
2. A Scene containing at least one password-protected Profile **must also be password-protected** (enforced at save time)
3. When a Scene is executed, if the Scene or any of its Profile steps are protected → passcode prompt required
4. System Actions are never password-protected

### Inheritance behavior

If Scene B contains Profile A (protected):
- Scene B must have `password_protected = True` and a `passcode_hash`
- Entering the Scene's passcode allows the full Scene to execute (including Profile A)
- Profile A cannot be added to any Scene unless the Scene is protected
- If Profile A is unprotected, it can be added to Scene B (unprotected) freely

### REST API flow

```
POST /api/scene/{id}/execute
→ 403 {"error": "passcode_required", "requires_scene_passcode": true}

POST /api/scene/{id}/execute
Body: {"passcode": "1234"}
→ 200 {"success": true, "execution_id": "..."}
```

### Passcode storage

- Plaintext passcode never stored
- `passcode_hash` = bcrypt hash of the PIN
- 4-8 digit numeric PIN

### Forgot passcode

No recovery. User must delete and recreate the Profile or Scene.

---

## Execution Engine

### Scene execution order

1. Validate passcode if protected
2. For each step in `steps` (in order):
   a. If step is a Profile:
      - Load the Profile
      - Apply routing to matrix
      - Apply each output setting **unless** that setting is overridden for this scene
      - Execute each macro in order
      - Log execution result to Profile's `execution_log`
   b. If step is a SystemAction:
      - Call the corresponding matrix API method
      - No profile logging (SystemActions are stateless)
3. Record scene execution in `scene.execution_history`
4. On error: log error, notify via WebSocket, continue to next step

### Error handling

- If a step fails, execution continues to the next step
- Error is logged in both the Scene's execution history and the Profile's execution log
- WebSocket event emitted: `{"type": "scene_execution_error", "scene_id": "...", "step": n, "error": "..."}`
- REST API returns 200 with `{"success": false, "steps_completed": n, "total_steps": m, "error": "..."}`

### No rollback

Matrix state is not reverted on error. If a Scene fails partway, the user may need to manually correct state.

---

## UI Structure

### Settings Drawer (replaces Quick Actions drawer)

Organized in tabs:

**Profiles tab**
- List all profiles
- Create / edit / delete / recall

**Scenes tab**
- List all scenes
- Create / edit / delete / execute
- Conflict resolution UI

**System Settings tab**
- Matrix settings: beep, panel lock, LCD timeout, reboot
- CEC bulk settings
- Input/output naming
- EDID management

**System Actions tab**
- The 5 routing templates + hardware preset recalls
- Can be renamed, reordered, disabled
- (These are not stored as separate entities — they are templates executed via SystemAction steps in Scenes)

### Dashboard

- Profile cards: tap to recall, long-press for edit
- Scene cards: tap to execute, long-press for edit, expand to see constituent profiles
- Cards sorted by `dashboard_order`
- Add Card button → picker shows all non-dashboard_visible Profiles and Scenes

### Profiles Editor

- Output routing grid
- Per-output settings accordion
- CEC macro sequence builder
- Password protection toggle
- Execution history log

### Scenes Editor

- Step list: drag to reorder, add Profile or System Action
- Conflict detection: shown inline when conflicts exist
- Override checkboxes per conflict
- Password protection (auto-suggested if scene contains protected profiles)
- Execution history log

---

## Backend Changes

### New modules

| File | Responsibility |
|------|----------------|
| `src/scene_manager.py` | CRUD + execution engine for Scene |
| `src/system_actions.py` | SystemAction definitions + executor |
| `src/scene_execution.py` | Conflict detection + override application logic |
| `src/password.py` | Passcode hashing + verification |

### Modified modules

| File | Change |
|------|--------|
| `src/config.py` | Add `execution_log` + `password_protected` + `passcode_hash` to Profile class |
| `src/cec_macros.py` | MacroManager unchanged |
| `src/system_shortcuts.py` | Deprecated — functionality moved to Scene + SystemActions |
| `src/dashboard_layout.py` | Card rendering unified for Profile and Scene types |
| `src/rest_api/profiles.py` | Add password-protected endpoints |
| `src/rest_api/scenes.py` | New — scene CRUD + execute endpoints |
| `src/rest_api/system_actions.py` | New — system action execute endpoints |
| `src/rest_api/__init__.py` | Wire new routes |
| `src/persistence.py` | `get_data_dir()` unchanged |

### API Routes

```
Profiles:
  GET/POST           /api/profiles
  GET/PUT/DELETE     /api/profile/{id}
  POST               /api/profile/{id}/recall
  POST               /api/profile/{id}/execute      ← accepts optional passcode
  GET                /api/profile/{id}/execution-log

Scenes:
  GET/POST           /api/scenes
  GET/PUT/DELETE     /api/scene/{id}
  POST               /api/scene/{id}/execute       ← accepts optional passcode
  GET                /api/scene/{id}/execution-history
  POST               /api/scene/{id}/validate      ← conflict check

System Actions:
  GET                /api/system-actions            ← list with user prefs
  POST               /api/system-action/{key}/execute
  PUT                /api/system-action/{key}      ← update label/icon/order/enabled
```

### Deprecations

| Old | Replacement |
|-----|------------|
| `SystemShortcutManager` + `system_shortcuts.json` | `Scene` + `scenes.json` + `system_actions.json` |
| `favorite` on SystemShortcut | `favorite` on Scene |
| `dashboard_visible` on SystemShortcut | `dashboard_visible` on Scene |
| Quick Actions drawer | Scenes tab in Settings drawer |
| Presets (hardware, separate) | Scene with single `preset_recall_N` step |

---

## Frontend Changes

### State (`web/js/state.js`)

- Merge `system_shortcuts` into `scenes` + `profiles`
- `dashboardCards` = union of `dashboard_visible` profiles and scenes
- New: `sceneEditor`, `profileEditor`, `conflictResolver`

### API (`web/js/api.js`)

- `POST /api/scene/{id}/execute`
- `GET /api/scene/{id}/execution-history`
- `POST /api/scene/{id}/validate`
- `GET/POST /api/system-actions`
- `PUT /api/system-action/{key}`
- Passcode prompt handling in execute flows

### Components

| Component | Change |
|-----------|--------|
| `dashboard-manager.js` | Handle Scene card type, expand/collapse |
| `profile-editor.js` | Add execution log panel, password toggle |
| `scenes-panel.js` | New — scene CRUD UI |
| `scene-editor.js` | New — step builder, conflict resolver |
| `system-settings-panel.js` | New — system settings tab content |
| `system-actions-panel.js` | New — system actions tab content |
| `quick-actions-drawer.js` | Deprecated — replaced by Settings drawer with tabs |
| `presets-panel.js` | Deprecated — presets are now scenes with preset_recall_N step |

### Routing

Settings drawer with tabs replaces Quick Actions drawer. Routes:
- `#settings/profiles`
- `#settings/scenes`
- `#settings/system`
- `#settings/actions`

---

## Testing Plan

### New test files

| File | Coverage |
|------|----------|
| `tests/test_scene_manager.py` | Scene CRUD, conflict detection, override application |
| `tests/test_system_actions.py` | SystemAction executor |
| `tests/test_password.py` | Hash, verify, inheritance validation |
| `tests/test_scene_execution.py` | Execution engine, error handling, history logging |
| `tests/test_rest_api.py` | Scene + SystemAction API endpoints (extend existing) |

### Test matrix

- Profile only → scene only → scene with overrides
- Password-protected profile in unprotected scene (should fail at save)
- Password-protected profile in protected scene (should succeed)
- Conflict detection: 2 profiles, same output, different hdcp
- Override: disable one profile's setting
- Execution history: 7-day retention boundary
- Passcode verification: correct / incorrect / missing

---

## Migration

No migration needed — Phase 7 was never released. Fresh start with new data model.

Existing Phase 7 data files (`profiles.json`, `scenes.json`, `cec_macros.json`, `system_shortcuts.json`, `dashboard_layout.json`) are discarded.

---

## Scope Boundaries

**In scope:**
- Unified Profile + Scene data model
- Scene execution engine with conflict detection
- Password protection with inheritance
- SystemActions as scene steps
- Dashboard unified for profiles + scenes
- Settings drawer with tabs replacing Quick Actions drawer

**Out of scope (Phase 8):**
- Scheduling / cron-like execution
- MQTT
- Multi-matrix support
- EDID management UI (beyond what exists)
- Ext-audio matrix UI (beyond what exists)
- HACS component
