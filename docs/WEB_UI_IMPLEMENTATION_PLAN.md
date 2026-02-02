# Web UI Implementation Plan

## Overview

A responsive, single-page web application for controlling the OREI HDMI Matrix switch. The UI will be served directly from the driver's REST API server and provide real-time control and monitoring.

**Target Devices:**
- 📱 Mobile phones (320px - 480px)
- 📱 Tablets (768px - 1024px) - Primary target
- 🖥️ Desktops/Large monitors (1200px+)

---

## 1. Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Browser (Any Device)                        │
├─────────────────────────────────────────────────────────────────────┤
│  index.html  │  style.css  │  app.js                                │
│              │             │  ├── API Client                        │
│              │             │  ├── WebSocket Handler                 │
│              │             │  ├── UI Components                     │
│              │             │  └── State Manager                     │
└──────────────┴─────────────┴────────────────────────────────────────┘
                              │
                              ▼ HTTP + WebSocket
┌─────────────────────────────────────────────────────────────────────┐
│                    REST API Server (Port 8080)                      │
│  ├── /api/*           (existing endpoints)                          │
│  ├── /ws              (existing WebSocket)                          │
│  └── /web/*           (NEW: static file serving)                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      OREI Matrix (BK-808)                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. File Structure

```
web/
├── index.html          # Main SPA entry point
├── css/
│   ├── style.css       # Main styles
│   ├── components.css  # UI component styles
│   └── responsive.css  # Media queries & breakpoints
├── js/
│   ├── app.js          # Main application
│   ├── api.js          # REST API client
│   ├── websocket.js    # WebSocket handler
│   ├── state.js        # State management
│   └── components/
│       ├── matrix-grid.js      # Main routing grid
│       ├── input-panel.js      # Input status/naming
│       ├── output-panel.js     # Output status/settings
│       ├── presets-panel.js    # Preset management
│       ├── scenes-panel.js     # Scene management
│       ├── settings-panel.js   # System settings
│       └── toast.js            # Notifications
└── assets/
    ├── icons/          # SVG icons
    └── favicon.ico
```

---

## 3. UI Layout Design

### 3.1 Mobile Layout (< 768px)
```
┌─────────────────────────────┐
│  ☰  OREI Matrix Control     │  ← Hamburger menu
├─────────────────────────────┤
│  [Inputs] [Outputs] [More]  │  ← Tab navigation
├─────────────────────────────┤
│                             │
│   ┌─────────────────────┐   │
│   │ Input 1: Apple TV   │   │
│   │ → Output: 1, 3      │   │
│   └─────────────────────┘   │
│   ┌─────────────────────┐   │
│   │ Input 2: Xbox       │   │
│   │ → Output: 2         │   │
│   └─────────────────────┘   │
│         . . .               │
│                             │
├─────────────────────────────┤
│  Quick Actions              │
│  [All Off] [Scene ▼]        │
└─────────────────────────────┘
```

### 3.2 Tablet Layout (768px - 1199px)
```
┌──────────────────────────────────────────────────────────────────┐
│   🔲 OREI Matrix Control                    ⚙️  🔔  Connected 🟢  │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │                    ROUTING MATRIX                        │    │
│   │          Out 1    Out 2    Out 3    Out 4    ...        │    │
│   │  In 1     ●        ○        ●        ○                  │    │
│   │  In 2     ○        ●        ○        ○                  │    │
│   │  In 3     ○        ○        ○        ●                  │    │
│   │  ...                                                     │    │
│   └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│   ┌───────────────────┐  ┌───────────────────┐                   │
│   │  📥 INPUTS        │  │  📤 OUTPUTS       │                   │
│   │  ────────────     │  │  ────────────     │                   │
│   │  1: Apple TV  ✏️  │  │  1: Living Room   │                   │
│   │  2: Xbox      ✏️  │  │  2: Bedroom       │                   │
│   │  3: Cable     ✏️  │  │  3: Office        │                   │
│   │  4: Roku      ✏️  │  │  4: Kitchen       │                   │
│   └───────────────────┘  └───────────────────┘                   │
│                                                                   │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │  QUICK ACTIONS                                              │ │
│   │  [🎬 Movie Night] [🎮 Gaming] [📺 Watch TV] [➕ New Scene] │ │
│   └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 3.3 Desktop Layout (≥ 1200px)
```
┌────────────────────────────────────────────────────────────────────────────────┐
│   🔲 OREI Matrix Control                                    ⚙️  🔔  Connected 🟢 │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌────────────────────────────────────────────────┐  ┌───────────────────────┐ │
│  │              ROUTING MATRIX                     │  │   📤 OUTPUT DETAILS   │ │
│  │                                                 │  │   ─────────────────   │ │
│  │       Out1   Out2   Out3   Out4   Out5  ...    │  │   Selected: Output 1  │ │
│  │  In1   ●      ○      ●      ○      ○           │  │   Name: Living Room   │ │
│  │  In2   ○      ●      ○      ○      ○           │  │   Source: Input 1     │ │
│  │  In3   ○      ○      ○      ●      ○           │  │   ─────────────────   │ │
│  │  In4   ○      ○      ○      ○      ●           │  │   Audio: [Enabled ▼]  │ │
│  │  ...                                            │  │   HDR:   [Auto ▼]     │ │
│  │                                                 │  │   HDCP:  [Auto ▼]     │ │
│  └────────────────────────────────────────────────┘  └───────────────────────┘ │
│                                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌───────────────────────┐ │
│  │   📥 INPUTS          │  │   🎬 PRESETS         │  │   🎭 SCENES           │ │
│  │   ─────────────      │  │   ─────────────      │  │   ─────────────       │ │
│  │   1: Apple TV   ✏️   │  │   P1: All In1   ▶️   │  │   Movie Night    ▶️   │ │
│  │   2: Xbox       ✏️   │  │   P2: Gaming   ▶️   │  │   Gaming Mode    ▶️   │ │
│  │   3: Cable      ✏️   │  │   P3: Off      ▶️   │  │   [+ Save Current]    │ │
│  │   4: Roku       ✏️   │  │   [Save to P4]       │  │   [+ New Scene]       │ │
│  └──────────────────────┘  └──────────────────────┘  └───────────────────────┘ │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │  SYSTEM   LCD: [60s ▼]   EDID: [Configure...]   Power: [Cycle]  [Reboot] │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Component Specifications

### 4.1 Matrix Grid Component
The heart of the UI - an interactive routing matrix.

**Features:**
- Click any cell to route input → output
- Visual indication of active routes (filled circle)
- Hover states for touch/mouse feedback
- Color coding: active (green), inactive (gray), pending (yellow)
- Auto-scales: 8×8 on desktop, scrollable on mobile

**Touch Optimization:**
- Minimum touch target: 44×44px
- Swipe to scroll on small screens
- Long-press for output options

```javascript
// Matrix cell interaction
cell.onclick = () => routeInput(inputNum, outputNum);
cell.onlongpress = () => showOutputOptions(outputNum);
```

### 4.2 Input Panel Component
Display and manage input sources.

**Features:**
- List all 8 inputs with names
- Inline edit for renaming
- Show which outputs each input feeds
- Visual signal detection indicator (future)

### 4.3 Output Panel Component
Display and control output settings.

**Features:**
- List all 8 outputs
- Show current input source
- Quick audio mute toggle
- HDR/HDCP mode selectors (dropdown)
- Individual output control

### 4.4 Presets Panel Component
Hardware preset management.

**Features:**
- Show all 4 hardware presets
- One-tap recall
- Save current routing to preset
- Rename presets

### 4.5 Scenes Panel Component
Software scene management.

**Features:**
- List all saved scenes
- One-tap recall
- Create new scene (modal)
- Delete scene (with confirmation)
- Save current state as new scene

### 4.6 Settings Panel Component
System configuration.

**Features:**
- LCD timeout adjustment (slider + dropdown)
- EDID configuration per input (modal)
- Power cycle / Reboot buttons
- External audio routing controls
- Connection status indicator

### 4.7 Toast Notification Component
User feedback for actions.

**Features:**
- Success/Error/Info styles
- Auto-dismiss (3 seconds)
- Stack multiple notifications
- Touch to dismiss

---

## 5. State Management

### 5.1 Application State
```javascript
const appState = {
  // Connection
  connected: false,
  wsConnected: false,
  
  // Matrix info
  info: {
    model: "",
    firmwareVersion: "",
    inputCount: 8,
    outputCount: 8
  },
  
  // Current routing
  routing: {
    // output# -> input#
    1: 1,
    2: 2,
    3: 1,
    // ...
  },
  
  // Input names
  inputs: {
    1: { name: "Apple TV", enabled: true },
    2: { name: "Xbox", enabled: true },
    // ...
  },
  
  // Output states
  outputs: {
    1: { 
      name: "Living Room",
      input: 1,
      audioMuted: false,
      hdrMode: "auto",
      hdcpMode: "auto"
    },
    // ...
  },
  
  // Presets
  presets: {
    1: { name: "All Input 1", routing: {...} },
    // ...
  },
  
  // Scenes
  scenes: [
    { id: "abc123", name: "Movie Night", outputs: {...} }
  ],
  
  // UI state
  ui: {
    selectedOutput: null,
    selectedInput: null,
    activeTab: "matrix",
    sidebarOpen: false
  }
};
```

### 5.2 State Updates via WebSocket
```javascript
// Real-time updates from matrix
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'switch':
      updateRouting(data.output, data.input);
      break;
    case 'audio_mute':
      updateOutputAudio(data.output, data.muted);
      break;
    case 'preset_recall':
      refreshAllState();
      break;
  }
};
```

---

## 6. API Integration

### 6.1 REST API Client
```javascript
class MatrixAPI {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl || window.location.origin;
  }
  
  // Core operations
  async getInfo() { return this.get('/api/info'); }
  async getStatus() { return this.get('/api/status'); }
  async switchInput(output, input) { 
    return this.post(`/api/output/${output}/switch`, { input }); 
  }
  
  // Naming
  async setInputName(input, name) { 
    return this.post(`/api/input/${input}/name`, { name }); 
  }
  
  // Presets
  async recallPreset(id) { return this.post(`/api/preset/${id}/recall`); }
  async savePreset(id) { return this.post(`/api/preset/${id}/save`); }
  
  // Scenes
  async listScenes() { return this.get('/api/scenes'); }
  async recallScene(id) { return this.post(`/api/scene/${id}/recall`); }
  async saveCurrentAsScene(name) { 
    return this.post('/api/scene/save-current', { name }); 
  }
  
  // Settings
  async setLcdTimeout(seconds) { 
    return this.post('/api/system/lcd-timeout', { timeout: seconds }); 
  }
  async reboot() { return this.post('/api/system/reboot'); }
  
  // Helpers
  async get(path) {
    const res = await fetch(`${this.baseUrl}${path}`);
    return res.json();
  }
  
  async post(path, body = {}) {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    return res.json();
  }
}
```

### 6.2 WebSocket Client
```javascript
class MatrixWebSocket {
  constructor(onMessage, onStatusChange) {
    this.onMessage = onMessage;
    this.onStatusChange = onStatusChange;
    this.reconnectDelay = 1000;
  }
  
  connect() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    this.ws = new WebSocket(`${protocol}//${location.host}/ws`);
    
    this.ws.onopen = () => {
      this.onStatusChange(true);
      this.reconnectDelay = 1000;
    };
    
    this.ws.onmessage = (event) => {
      this.onMessage(JSON.parse(event.data));
    };
    
    this.ws.onclose = () => {
      this.onStatusChange(false);
      setTimeout(() => this.connect(), this.reconnectDelay);
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
    };
  }
}
```

---

## 7. CSS Design System

### 7.1 Design Tokens
```css
:root {
  /* Colors */
  --color-primary: #3b82f6;       /* Blue */
  --color-primary-dark: #2563eb;
  --color-success: #22c55e;       /* Green */
  --color-warning: #f59e0b;       /* Amber */
  --color-error: #ef4444;         /* Red */
  --color-neutral-50: #f8fafc;
  --color-neutral-100: #f1f5f9;
  --color-neutral-200: #e2e8f0;
  --color-neutral-700: #334155;
  --color-neutral-800: #1e293b;
  --color-neutral-900: #0f172a;
  
  /* Typography */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  
  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  
  /* Touch targets */
  --touch-target-min: 44px;
  
  /* Borders */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: var(--color-neutral-900);
    --bg-secondary: var(--color-neutral-800);
    --text-primary: var(--color-neutral-50);
    --text-secondary: var(--color-neutral-200);
  }
}
```

### 7.2 Responsive Breakpoints
```css
/* Mobile first approach */

/* Small (default) - phones */
.container { padding: var(--space-4); }

/* Medium - tablets */
@media (min-width: 768px) {
  .container { padding: var(--space-6); }
  .matrix-grid { grid-template-columns: repeat(8, 1fr); }
  .panel-row { display: flex; gap: var(--space-4); }
}

/* Large - desktops */
@media (min-width: 1200px) {
  .container { max-width: 1400px; margin: 0 auto; }
  .main-layout { display: grid; grid-template-columns: 2fr 1fr; }
}

/* Extra large - large monitors */
@media (min-width: 1600px) {
  .matrix-cell { min-width: 80px; min-height: 80px; }
}
```

---

## 8. Implementation Phases

### Phase 1: Foundation (2 hours)
1. **Static file serving** - Add route to rest_api.py
2. **HTML skeleton** - Basic structure with all containers
3. **CSS foundation** - Reset, tokens, basic layout
4. **API client** - Core fetch wrapper

**Deliverable:** Blank page loads, can make API calls

### Phase 2: Matrix Grid (1.5 hours)
1. **Grid component** - Render 8×8 matrix
2. **Click handling** - Route on click
3. **State display** - Show active routes
4. **Responsive scaling** - Scroll on mobile

**Deliverable:** Functional routing grid

### Phase 3: Input/Output Panels (1.5 hours)
1. **Input list** - Names, edit capability
2. **Output list** - Status, current source
3. **Output controls** - Audio, HDR, HDCP dropdowns
4. **Panel layout** - Responsive side-by-side/stacked

**Deliverable:** Full input/output management

### Phase 4: Presets & Scenes (1 hour)
1. **Preset buttons** - Recall, save
2. **Scene list** - With recall/delete
3. **Save scene modal** - Name input
4. **Responsive layout** - Cards on mobile

**Deliverable:** Full preset/scene control

### Phase 5: System Controls (45 min)
1. **Settings panel** - LCD, EDID, power
2. **Header bar** - Status, connection indicator
3. **Toast notifications** - Action feedback

**Deliverable:** Complete system settings

### Phase 6: WebSocket & Polish (1 hour)
1. **WebSocket integration** - Real-time updates
2. **Loading states** - Spinners, skeletons
3. **Error handling** - User-friendly messages
4. **Animations** - Smooth transitions
5. **PWA basics** - Manifest, icons

**Deliverable:** Production-ready UI

---

## 9. Server-Side Changes

### 9.1 Static File Serving
Add to `rest_api.py`:

```python
from aiohttp import web
import os

# In create_rest_app():
web_dir = os.path.join(os.path.dirname(__file__), '..', 'web')

# Serve index.html at /
app.router.add_get('/', lambda r: web.FileResponse(os.path.join(web_dir, 'index.html')))

# Serve static files
app.router.add_static('/css/', os.path.join(web_dir, 'css'))
app.router.add_static('/js/', os.path.join(web_dir, 'js'))
app.router.add_static('/assets/', os.path.join(web_dir, 'assets'))
```

### 9.2 CORS Headers (if needed for dev)
```python
@web.middleware
async def cors_middleware(request, handler):
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
```

---

## 10. Testing Plan

### 10.1 Device Testing Matrix
| Device | Resolution | Browser | Status |
|--------|------------|---------|--------|
| iPhone SE | 375×667 | Safari | ⬜ |
| iPhone 14 | 390×844 | Safari | ⬜ |
| iPad | 768×1024 | Safari | ⬜ |
| iPad Pro | 1024×1366 | Safari | ⬜ |
| Android Phone | 360×800 | Chrome | ⬜ |
| Android Tablet | 800×1280 | Chrome | ⬜ |
| Desktop | 1920×1080 | Chrome | ⬜ |
| Desktop | 2560×1440 | Firefox | ⬜ |

### 10.2 Functional Tests
- [ ] Matrix routing works
- [ ] Input renaming persists
- [ ] Preset recall/save works
- [ ] Scene create/recall/delete works
- [ ] WebSocket updates reflect immediately
- [ ] Reconnection after disconnect
- [ ] All dropdowns functional
- [ ] Toast notifications appear
- [ ] Dark mode works

### 10.3 Performance Targets
- First contentful paint: < 1s
- Time to interactive: < 2s
- No layout shift after load

---

## 11. Future Enhancements

### Phase 2 (Post-MVP)
- 🎨 Theme customization (colors)
- 📱 PWA: Installable, offline indicator
- 🔐 Optional authentication
- 📊 Usage statistics dashboard
- 🎙️ Voice control integration
- 🔄 Undo/redo for routing changes

### Phase 3 (Advanced)
- 📺 Input preview thumbnails (if supported)
- ⏰ Scheduled scenes (time-based automation)
- 🔗 URL deep links for specific views
- 🌐 Multi-matrix support

---

## 12. Effort Estimate Summary

| Phase | Description | Time |
|-------|-------------|------|
| 1 | Foundation | 2h |
| 2 | Matrix Grid | 1.5h |
| 3 | Input/Output Panels | 1.5h |
| 4 | Presets & Scenes | 1h |
| 5 | System Controls | 45m |
| 6 | WebSocket & Polish | 1h |
| **Total** | **MVP Complete** | **~8h** |

---

## 13. Success Criteria

✅ **Functional Requirements:**
- All routing operations work
- All settings accessible
- Works on phone, tablet, and desktop
- Real-time updates via WebSocket

✅ **Quality Requirements:**
- Touch-friendly (44px+ targets)
- Fast load time (< 2s)
- No horizontal scroll on mobile
- Clear visual feedback on actions

✅ **User Experience:**
- Intuitive without documentation
- One-tap for common actions
- Visual matrix is immediately understandable
