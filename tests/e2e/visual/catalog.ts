// UI state catalog (docs/REMEDIATION_PLAN.md §5.3, "Capture").
//
// One entry per reviewable UI element/state. The catalog IS the checklist of
// UI elements: a new component or state is not done until it has an entry.
// visual.spec.ts captures every entry at every viewport in the default theme
// (Tron Classic), and entries marked `themed` also in Neon, Royal and
// Vaporwave at desktop and kiosk-device sizes.
//
// Naming: <area>/<element>/<state>, e.g. matrix/grid/default,
// drawer/theme/customize, kiosk/presets/edit-mode.
//
// Rules for setups:
// - Only drive the UI the way a user (or the running app) would, or call the
//   app's own globals. Never change web/: the baseline captures today's UI,
//   bugs included. Where a state is only reachable through a broken or missing
//   trigger, the entry says so in `note`.
// - Never change hub data a later entry depends on. Hardware states (no
//   signal, unplugged cables, long names, errors) are produced by reshaping the
//   hub's responses in the browser (routes), not by editing the simulator.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, type Page } from '@playwright/test';
import type { ViewportName } from '../support/viewports';
import { failJson, mutateJson, okJson, releaseStatusFrames, settle, statusFramesReceived, type PrepareOptions } from '../support/ui';

export type Ctx = { page: Page; viewport: ViewportName };

export type CatalogEntry = {
  /** Hierarchical name; also the snapshot path. */
  name: string;
  /** What a reviewer should look at. */
  description: string;
  /** Which page to load. */
  page: 'ui' | 'kiosk';
  /** Also capture in the other three theme presets (desktop + kiosk-device viewports). */
  themed?: boolean;
  /** Restrict to these viewports (default: all; see tests/e2e/support/viewports.ts). */
  viewports?: ViewportName[];
  /** Browser setup before navigation (storage, WebSocket). */
  prepare?: PrepareOptions;
  /** Network shaping before navigation. */
  routes?: (page: Page) => Promise<void>;
  /** Wait for normal app readiness after load (default true). */
  ready?: boolean;
  /** Drive the UI into the state. */
  setup?: (ctx: Ctx) => Promise<void>;
  /** Scroll this element into view (centre) before capturing, for states below the fold. */
  scrollTo?: string;
  /** Extra selectors to mask (volatile content). */
  mask?: string[];
  /** Keep the pointer where setup left it (hover states). */
  keepPointer?: boolean;
  /** Known bug / reachability note shown in the gallery. */
  note?: string;
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const LONG_INPUTS = [
  'Living Room Apple TV 4K (2nd Gen) HDR',
  'PlayStation 5 Digital Edition — Den',
  'Office Gaming PC RTX 4090 DisplayPort',
  'Nintendo Switch OLED Dock Upstairs',
  'NVIDIA Shield TV Pro 2019 Media Room',
  'Kaleidescape Strato C Movie Server',
  'Analogue Pocket Dock + Super Nt Retro',
  'Security Camera NVR Multiview Feed 8',
];
const LONG_OUTPUTS = [
  'Living Room 85" OLED Television',
  'Soundbar Atmos 7.1.4 eARC Receiver',
  'Home Theater 4K Laser Projector',
  'Kitchen Under-Cabinet Monitor',
  'Primary Bedroom 65" QLED Television',
  'Patio Weatherproof Outdoor TV',
  'Basement Game Room Arcade Display',
  'Garage Workshop Monitor (Wall Mount)',
];
const LONG_PRESETS = [
  'Apple TV Everywhere (Movie Night)',
  'Shield Night — Upstairs & Downstairs',
  'PS5 Game Room + Projector Evening',
  'Retro Weekend Multiview Everywhere',
];

type Json = Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any

/** Reshape the hub's status responses so every input/output/preset has a long name. */
async function longNames(page: Page) {
  const inNames = Object.fromEntries(LONG_INPUTS.map((n, i) => [String(i + 1), n]));
  const outNames = Object.fromEntries(LONG_OUTPUTS.map((n, i) => [String(i + 1), n]));
  await mutateJson(page, '**/api/status', (b: Json) => {
    if (!b.data) return;
    b.data.input_names = inNames;
    b.data.output_names = outNames;
    for (let i = 0; i < LONG_PRESETS.length; i++) if (b.data.preset_names) b.data.preset_names[String(i + 1)] = LONG_PRESETS[i];
  });
  await mutateJson(page, '**/api/status/inputs', (b: Json) => {
    for (const p of b.data?.inputs ?? []) p.name = LONG_INPUTS[p.number - 1];
  });
  await mutateJson(page, '**/api/status/outputs', (b: Json) => {
    for (const p of b.data?.outputs ?? []) p.name = LONG_OUTPUTS[p.number - 1];
  });
  await mutateJson(page, '**/api/device-settings', (b: Json) => {
    for (const [k, v] of Object.entries(b.data?.inputs ?? {})) (v as Json).name = LONG_INPUTS[+k - 1];
    for (const [k, v] of Object.entries(b.data?.outputs ?? {})) (v as Json).name = LONG_OUTPUTS[+k - 1];
  });
  await mutateJson(page, '**/api/presets', (b: Json) => {
    for (const p of b.data?.presets ?? []) if (p.number <= LONG_PRESETS.length) p.name = LONG_PRESETS[p.number - 1];
  });
  await mutateJson(page, '**/api/shortcuts', (b: Json) => {
    for (const s of b.data?.shortcuts ?? []) if (s.id?.startsWith('user.')) s.name = s.label = `${s.label} — Living Room Evening Routine`;
  });
  await mutateJson(page, '**/api/profiles', (b: Json) => {
    for (const p of b.data?.profiles ?? []) p.name = `${p.name} with the Whole Family (Weekend Edition)`;
  });
}

/** No source signal on any input (sources off / standby). */
async function noSignal(page: Page) {
  await mutateJson(page, '**/api/status/inputs', (b: Json) => {
    for (const p of b.data?.inputs ?? []) {
      p.signalActive = false;
      p.inactive = true;
    }
  });
}

/** Every HDMI cable unplugged (inputs and outputs). */
async function cablesUnplugged(page: Page) {
  await mutateJson(page, '**/api/status/inputs', (b: Json) => {
    for (const p of b.data?.inputs ?? []) {
      p.signalActive = false;
      p.inactive = true;
      p.cableConnected = false;
      p.sourceDetected = false;
    }
  });
  await mutateJson(page, '**/api/status/outputs', (b: Json) => {
    for (const p of b.data?.outputs ?? []) {
      p.connected = false;
      p.cableConnected = false;
    }
  });
}

/** Every output routed to input 2 (AppleTV), as after "Route All" / preset 1. */
async function allToInput2(page: Page) {
  await mutateJson(page, '**/api/status', (b: Json) => {
    if (!b.data) return;
    b.data.routing = Object.fromEntries([1, 2, 3, 4, 5, 6, 7, 8].map((o) => [String(o), 2]));
    b.data.outputs = [2, 2, 2, 2, 2, 2, 2, 2];
  });
}

/** Hold a request forever (loading states). */
async function hang(page: Page, glob: string) {
  await page.route(glob, () => {
    /* never answered */
  });
}

async function abort(page: Page, glob: string) {
  await page.route(glob, (route) => route.abort('connectionrefused'));
}

const js = (page: Page, expr: string) => page.evaluate(expr);

/** Switch a /ui page tab the way a user does: click the visible tab button. */
async function tab(page: Page, name: 'matrix' | 'dashboard' | 'inputs' | 'outputs' | 'profiles') {
  await page.locator(`.tab-btn[data-tab="${name}"]:visible`).first().click();
  await settle(page, 400);
}

/** Open the Control Deck (side nav). */
async function deck(page: Page) {
  await page.locator('#menu-toggle').click();
  await page.locator('#side-nav-drawer.open').waitFor();
  await settle(page, 300);
}

/** Open a drawer from the Control Deck, as a user would. */
async function drawer(page: Page, button: string, root: string) {
  await deck(page);
  await page.locator(`#${button}`).click();
  await page.locator(root).first().waitFor({ state: 'visible' });
  await settle(page, 500);
}

const ROUTING = '#routing-drawer.open';
const PRESETS = '#presets-drawer.open';
const THEME = '.theme-drawer[aria-hidden="false"]';
const GENERAL = '#general-drawer.open';
const HARDWARE = '#hardware-drawer.open';
const INTERFACE = '#interface-drawer.open';
const SHORTCUTS = '#shortcuts-drawer.open';
const INTEGRATIONS = '#integrations-drawer.open';

/** Serve /api/profiles and /api/cec/macros into the in-memory state the main UI never fills (bug: state.profiles / state.cecMacros are never loaded). */
async function loadProfilesAndMacros(page: Page) {
  await page.evaluate(async () => {
    const w = window as any; // eslint-disable-line @typescript-eslint/no-explicit-any
    const profiles = (await (await fetch('/api/profiles')).json()).data?.profiles ?? [];
    const macros = (await (await fetch('/api/cec/macros')).json()).data?.macros ?? [];
    w.state.setProfiles(profiles);
    w.state.cecMacros = macros;
  });
}

/**
 * Profiles as the Profiles tab shows them after the user has created some: the
 * only data path is the browser state cache (see PROFILES_NOTE), so it is
 * seeded from the fixture profiles.
 */
function cachedProfiles(names?: (n: string) => string): Record<string, string> {
  const file = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'fixtures', 'data', 'profiles.json');
  const profiles = JSON.parse(fs.readFileSync(file, 'utf8')).profiles.map((p: Json) => ({
    ...p,
    name: names ? names(p.name) : p.name,
  }));
  // timestamp: one minute before the frozen test clock, so the 24 h cache is fresh.
  return { orei_state_cache: JSON.stringify({ scenes: profiles, timestamp: Date.UTC(2026, 8, 24, 11, 59, 0) }) };
}

const PROFILES_NOTE =
  'The Profiles tab only shows profiles from the browser state cache: app.js:591 reads /api/v2/scenes with the wrong response path, and the tab never calls /api/profiles.';

// ---------------------------------------------------------------------------
// Catalog
// ---------------------------------------------------------------------------

export const CATALOG: CatalogEntry[] = [
  // ===== App shell / header ================================================
  {
    name: 'app/header/disconnected',
    page: 'ui',
    description: 'Header when the WebSocket cannot connect: red title pill, generic title.',
    prepare: { noWebSocket: true },
    ready: false,
    setup: async ({ page }) => {
      await page.waitForFunction(() => (window as any).state?.ui?.dataLoaded === true, undefined, { timeout: 20_000 }); // eslint-disable-line @typescript-eslint/no-explicit-any
      await settle(page, 600);
    },
  },
  {
    name: 'app/matrix-unreachable',
    page: 'ui',
    description: 'Hub up but the matrix is not answering: every status call returns 503 (as the hub does when the matrix is disconnected).',
    routes: async (page) => {
      await failJson(page, '**/api/status', 503, 'Matrix not connected');
      await failJson(page, '**/api/status/**', 503, 'Matrix not connected');
      await failJson(page, '**/api/info', 503, 'Matrix not connected');
      await failJson(page, '**/api/power/on', 503, 'Matrix not connected');
      await failJson(page, '**/api/presets', 503, 'Matrix not connected');
    },
    ready: false,
    setup: async ({ page }) => settle(page, 2500),
    note: 'No error is shown: the header stays green (it only reflects the WebSocket) and the grid shows a made-up 1:1 routing with default output names.',
  },
  {
    name: 'app/header/reconnecting',
    page: 'ui',
    description: 'WebSocket closed after a good start (hub restarted): header after the socket drops, while it retries.',
    setup: async ({ page }) => {
      await js(page, `window.state.setWsConnected(false)`);
      await settle(page, 300);
    },
    note: 'There is no distinct "reconnecting" visual: websocket.js tracks a reconnecting status but app.js never renders it, so this is the plain disconnected header over loaded data.',
  },

  {
    name: 'app/ws-status-refresh/output-names',
    page: 'ui',
    description: 'Matrix grid after the hub\'s background status broadcast arrives (what a user sees ~100 ms after load).',
    prepare: { wsStatus: 'hold', storage: { 'matrix-view-mode': 'grid' } },
    // Warm the hub's output-status cache so this page load triggers the broadcast.
    routes: async (page) => {
      await page.request.get('/api/status/outputs');
    },
    setup: async ({ page }) => {
      await expect.poll(() => statusFramesReceived(page), { timeout: 10_000 }).toBeGreaterThan(0);
      // Deliver it after the page has applied its REST data (the usual order;
      // if it arrives first, the REST response wins and names stay correct).
      releaseStatusFrames(page);
      await settle(page, 400);
    },
    note: 'Hub bug: every GET /api/status/outputs with a warm cache broadcasts a refresh whose outputs_detail names come from the hub name cache, empty in modular mode (src/rest_api/core.py:115 via outputs.py:59), so TV/Soundbar become "Output 1/2" (unless the broadcast happens to arrive before the REST response). All other entries drop these broadcasts to stay deterministic.',
  },

  // ===== Matrix ============================================================
  {
    name: 'matrix/grid/default',
    page: 'ui',
    themed: true,
    description: 'Routing matrix, grid view, seeded simulator (8 named inputs/outputs, mixed routing, signal on 2/5/6).',
    prepare: { storage: { 'matrix-view-mode': 'grid' } },
  },
  {
    name: 'matrix/cards/default',
    page: 'ui',
    themed: true,
    description: 'Routing matrix, cards view (output cards with route selector, CEC and settings buttons).',
    prepare: { storage: { 'matrix-view-mode': 'cards' } },
  },
  {
    name: 'matrix/grid/all-to-one',
    page: 'ui',
    description: 'Grid with every output on input 2 (after Route All / preset recall).',
    prepare: { storage: { 'matrix-view-mode': 'grid' } },
    routes: allToInput2,
  },
  {
    name: 'matrix/grid/no-signal',
    page: 'ui',
    description: 'All sources idle: cables in, no signal (standby colours on labels).',
    prepare: { storage: { 'matrix-view-mode': 'grid' } },
    routes: noSignal,
  },
  {
    name: 'matrix/grid/cables-unplugged',
    page: 'ui',
    description: 'Every input and output cable unplugged (disconnected colours).',
    prepare: { storage: { 'matrix-view-mode': 'grid' } },
    routes: cablesUnplugged,
  },
  {
    name: 'matrix/cards/cables-unplugged',
    page: 'ui',
    description: 'Cards view with every cable unplugged.',
    prepare: { storage: { 'matrix-view-mode': 'cards' } },
    routes: cablesUnplugged,
  },
  {
    name: 'matrix/grid/long-names',
    page: 'ui',
    description: 'Grid with long input/output names (overflow and truncation).',
    prepare: { storage: { 'matrix-view-mode': 'grid' } },
    routes: longNames,
  },
  {
    name: 'matrix/cards/long-names',
    page: 'ui',
    description: 'Cards view with long input/output names.',
    prepare: { storage: { 'matrix-view-mode': 'cards' } },
    routes: longNames,
  },
  {
    name: 'matrix/grid/route-pending',
    page: 'ui',
    description: 'A route click waiting for the matrix (pending cell).',
    prepare: { storage: { 'matrix-view-mode': 'grid' } },
    routes: async (page) => {
      await hang(page, '**/api/switch**');
      await hang(page, '**/api/output/*/source');
    },
    setup: async ({ page }) => {
      await page.locator('#matrix-grid .matrix-route[data-input="3"][data-output="1"]').click();
      await settle(page, 300);
    },
  },
  {
    name: 'matrix/grid/status-pending',
    page: 'ui',
    description: 'Matrix while the first /api/status request is still pending.',
    prepare: { storage: { 'matrix-view-mode': 'grid' } },
    routes: (page) => hang(page, '**/api/status'),
    ready: false,
    setup: async ({ page }) => settle(page, 1500),
    note: 'No loading indicator: the grid shows a made-up 1:1 routing and default names until status arrives (the "Loading matrix..." spinner exists only in the pre-JS HTML). The same happens when the matrix is unreachable (app/matrix-unreachable).',
  },
  {
    name: 'matrix/grid/cell-hover',
    page: 'ui',
    viewports: ['desktop'],
    description: 'Pointer hovering an inactive grid cell.',
    prepare: { storage: { 'matrix-view-mode': 'grid' } },
    keepPointer: true,
    setup: async ({ page }) => {
      await page.locator('#matrix-grid .matrix-route[data-input="4"][data-output="3"]').hover();
      await settle(page, 200);
    },
  },
  {
    name: 'matrix/grid/cell-focus',
    page: 'ui',
    viewports: ['desktop'],
    description: 'Keyboard focus on a grid cell (focus ring).',
    prepare: { storage: { 'matrix-view-mode': 'grid' } },
    setup: async ({ page }) => {
      await page.locator('#matrix-grid .matrix-route[data-input="4"][data-output="3"]').focus();
      await settle(page, 200);
    },
  },
  {
    name: 'matrix/cards/routing-sheet',
    page: 'ui',
    description: 'Output card route selector: the "Select Input Source" bottom sheet.',
    prepare: { storage: { 'matrix-view-mode': 'cards' } },
    setup: async ({ page }) => {
      await page.locator('#matrix-mobile-view .io-card-route-selector[data-output="1"]').click();
      await page.locator('#mobile-routing-sheet.open').waitFor();
      await settle(page, 400);
    },
  },

  // ===== Dashboard =========================================================
  {
    name: 'dashboard/default',
    page: 'ui',
    themed: true,
    description: 'Dashboard as it loads: Routing widget pinned; server cards not rendered yet ("No cards yet").',
    setup: async ({ page }) => tab(page, 'dashboard'),
    note: 'Seeded dashboard cards do not render on load: dashboard-manager.js renders cards from a 100 ms timer before /api/dashboard/layout arrives, and nothing re-renders afterwards.',
  },
  {
    name: 'dashboard/cards/all-types',
    page: 'ui',
    description: 'Every dashboard card type (scene, locked scene, preset, built-in and user shortcut, profile, macro, aggregate widgets) once cards are rendered.',
    setup: async ({ page }) => {
      await tab(page, 'dashboard');
      await loadProfilesAndMacros(page);
      await js(page, `(async () => { await window.state.loadDashboardLayout(); window.dashboardManager.renderCards(); })()`);
      await settle(page, 300);
      await page.locator('.dashboard-cards-container').evaluate((el) => el.scrollIntoView({ block: 'start' }));
      await settle(page, 200);
    },
    note: 'Needs an app-state nudge: profile and macro cards need state.profiles/state.cecMacros, which the main UI never loads; aggregate_widget cards render empty (renderer reads card.widget_id).',
  },
  {
    name: 'dashboard/cards/empty',
    page: 'ui',
    description: 'Dashboard cards area with no cards.',
    routes: (page) => okJson(page, '**/api/dashboard/layout', { version: 1, cards: [] }),
    setup: async ({ page }) => {
      await tab(page, 'dashboard');
      await page.locator('.dashboard-cards-container').evaluate((el) => el.scrollIntoView({ block: 'start' }));
      await settle(page, 200);
    },
  },
  {
    name: 'dashboard/widgets/cec-remote',
    page: 'ui',
    description: 'Dashboard with the CEC remote widget pinned next to the Routing widget.',
    prepare: {
      storage: {
        orei_dashboard_config: JSON.stringify({
          pinnedWidgets: ['routing-dashboard', 'cec-remote'],
          hiddenMobileWidgets: [],
          widgetOrder: ['routing-dashboard', 'cec-remote'],
        }),
      },
    },
    setup: async ({ page }) => tab(page, 'dashboard'),
  },
  ...(['profiles', 'scenes', 'presets', 'shortcuts', 'macros'] as const).map(
    (t): CatalogEntry => ({
      name: `dashboard/card-picker/${t}`,
      page: 'ui',
      description: `"Add card" picker, ${t} tab.`,
      setup: async ({ page }) => {
        await tab(page, 'dashboard');
        await page.locator('#add-dashboard-card-btn').click();
        await page.locator('#dashboard-card-picker.visible').waitFor();
        await page.locator(`#dashboard-card-picker .picker-tab-btn[data-tab="${t}"]`).click();
        await settle(page, 400);
      },
      note:
        t === 'profiles' || t === 'macros'
          ? `Always empty today: state.${t === 'profiles' ? 'profiles' : 'cecMacros'} is never loaded by the main UI.`
          : undefined,
    }),
  ),

  // ===== Inputs ============================================================
  {
    name: 'inputs/list/default',
    page: 'ui',
    themed: true,
    description: 'Inputs tab: 8 input cards with icons, signal/cable status, CEC and settings buttons.',
    setup: async ({ page }) => tab(page, 'inputs'),
  },
  {
    name: 'inputs/list/no-signal',
    page: 'ui',
    description: 'Inputs tab with no source signal anywhere.',
    routes: noSignal,
    setup: async ({ page }) => tab(page, 'inputs'),
  },
  {
    name: 'inputs/list/cables-unplugged',
    page: 'ui',
    description: 'Inputs tab with every cable unplugged.',
    routes: cablesUnplugged,
    setup: async ({ page }) => tab(page, 'inputs'),
  },
  {
    name: 'inputs/list/long-names',
    page: 'ui',
    description: 'Inputs tab with long names.',
    routes: longNames,
    setup: async ({ page }) => tab(page, 'inputs'),
  },
  {
    name: 'inputs/list/loading-skeleton',
    page: 'ui',
    description: 'Input cards skeleton loader.',
    setup: async ({ page }) => {
      await tab(page, 'inputs');
      await js(page, `SkeletonLoader.show(document.getElementById('inputs-list'), { type: 'io-card', count: 4 })`);
      await settle(page, 200);
    },
    note: 'Not reachable in normal use: the skeleton only shows when state has no inputs, and state always starts with 8 defaults.',
  },
  {
    name: 'inputs/card/hover',
    page: 'ui',
    viewports: ['desktop'],
    description: 'Pointer hovering an input card.',
    keepPointer: true,
    setup: async ({ page }) => {
      await tab(page, 'inputs');
      await page.locator('#inputs-list .io-card[data-input="2"]').hover();
      await settle(page, 200);
    },
  },

  // ===== Outputs ===========================================================
  {
    name: 'outputs/list/default',
    page: 'ui',
    themed: true,
    description: 'Outputs tab: 8 output cards (TV and Soundbar connected, others no display).',
    setup: async ({ page }) => tab(page, 'outputs'),
  },
  {
    name: 'outputs/list/cables-unplugged',
    page: 'ui',
    description: 'Outputs tab with every display unplugged.',
    routes: cablesUnplugged,
    setup: async ({ page }) => tab(page, 'outputs'),
  },
  {
    name: 'outputs/list/long-names',
    page: 'ui',
    description: 'Outputs tab with long names.',
    routes: longNames,
    setup: async ({ page }) => tab(page, 'outputs'),
  },

  // ===== Profiles ==========================================================
  {
    name: 'profiles/list/empty',
    page: 'ui',
    description: 'Profiles tab as it loads today (empty, even though the hub has 4 profiles).',
    setup: async ({ page }) => tab(page, 'profiles'),
    note: PROFILES_NOTE,
  },
  {
    name: 'profiles/list/populated',
    page: 'ui',
    themed: true,
    description: 'Profiles tab with profiles (pinned ones shown, incl. a passcode-protected profile).',
    prepare: { storage: cachedProfiles() },
    setup: async ({ page }) => tab(page, 'profiles'),
    note: PROFILES_NOTE,
  },
  {
    name: 'profiles/list/long-names',
    page: 'ui',
    description: 'Profiles tab with long profile names.',
    prepare: { storage: cachedProfiles((n) => `${n} with the Whole Family (Weekend Edition)`) },
    setup: async ({ page }) => tab(page, 'profiles'),
    note: PROFILES_NOTE,
  },
  {
    name: 'profiles/manager/populated',
    page: 'ui',
    description: 'Manage Profiles panel (pinned/unpinned lists).',
    prepare: { storage: cachedProfiles() },
    setup: async ({ page }) => {
      await tab(page, 'profiles');
      await page.locator('#manage-profiles-btn').click();
      await page.locator('.profile-manager-panel.open').waitFor();
      await settle(page, 400);
    },
    note: PROFILES_NOTE,
  },
  {
    name: 'profiles/manager/empty',
    page: 'ui',
    description: 'Manage Profiles panel with no profiles.',
    setup: async ({ page }) => {
      await tab(page, 'profiles');
      await page.locator('#manage-profiles-btn').click();
      await page.locator('.profile-manager-panel.open').waitFor();
      await settle(page, 400);
    },
  },
  {
    name: 'profiles/api-endpoint-modal',
    page: 'ui',
    description: 'Profile "API endpoint" modal (URL + curl snippet for Flic/automation).',
    prepare: { storage: cachedProfiles() },
    setup: async ({ page }) => {
      await tab(page, 'profiles');
      // The first click throws before opening (see note); a second click opens it.
      await page.locator('#scenes-list .api-copy-btn').first().click();
      await page.locator('#scenes-list .api-copy-btn').first().click();
      await page.locator('#api-copy-modal.open').waitFor();
      await settle(page, 300);
    },
    note: 'The first click on the API button throws and opens nothing: createModal (api-copy.js:134) queries .api-modal-backdrop inside itself and gets null; the second click works. The URLs hard-code port 8080 (api-copy.js:13), wrong when the hub runs on another port (here 18080).',
  },

  // ===== Control Deck ======================================================
  {
    name: 'deck/default',
    page: 'ui',
    themed: true,
    description: 'Control Deck (side nav): utility buttons and Personalize Tabs list.',
    setup: async ({ page }) => deck(page),
  },
  {
    name: 'deck/personalize-tabs',
    page: 'ui',
    description: 'Control Deck scrolled to the Personalize Tabs list (pin / reorder).',
    setup: async ({ page }) => {
      await deck(page);
      await page.locator('#drawer-tab-settings-list').evaluate((el) => el.scrollIntoView({ block: 'end' }));
      await settle(page, 200);
    },
  },
  {
    name: 'deck/button-hover',
    page: 'ui',
    viewports: ['desktop'],
    description: 'Pointer hovering a Control Deck button.',
    keepPointer: true,
    setup: async ({ page }) => {
      await deck(page);
      await page.locator('#drawer-presets-btn').hover();
      await settle(page, 200);
    },
  },

  // ===== Drawers ===========================================================
  {
    name: 'drawer/routing/default',
    page: 'ui',
    description: 'Route To All drawer: input buttons with signal status.',
    setup: async ({ page }) => drawer(page, 'drawer-routing-btn', ROUTING),
  },
  {
    name: 'drawer/routing/all-active',
    page: 'ui',
    description: 'Route To All drawer when every output is on one input (active badge).',
    routes: allToInput2,
    setup: async ({ page }) => drawer(page, 'drawer-routing-btn', ROUTING),
  },
  {
    name: 'drawer/routing/routing-in-progress',
    page: 'ui',
    description: 'Route To All button while the switch request is in flight (loading).',
    routes: (page) => hang(page, '**/api/switch**'),
    setup: async ({ page }) => {
      await drawer(page, 'drawer-routing-btn', ROUTING);
      await page.locator('#routing-drawer .routing-btn[data-input="3"]').click();
      await settle(page, 300);
    },
  },
  {
    name: 'drawer/presets/default',
    page: 'ui',
    themed: true,
    description: 'Presets drawer: 8 presets (names from device settings + matrix).',
    setup: async ({ page }) => drawer(page, 'drawer-presets-btn', PRESETS),
  },
  {
    name: 'drawer/presets/expanded',
    page: 'ui',
    description: 'Presets drawer with a preset expanded (routing editor, recall/overwrite/save).',
    setup: async ({ page }) => {
      await drawer(page, 'drawer-presets-btn', PRESETS);
      await page.locator('#presets-drawer .preset-row[data-preset-number="2"] .preset-expand-btn').click();
      await settle(page, 300);
    },
  },
  {
    name: 'drawer/presets/rename',
    page: 'ui',
    description: 'Presets drawer, renaming a preset (inline input).',
    setup: async ({ page }) => {
      await drawer(page, 'drawer-presets-btn', PRESETS);
      await page.locator('#presets-drawer .preset-row-edit-btn[data-preset="1"]').click();
      await settle(page, 300);
    },
  },
  {
    name: 'drawer/presets/active',
    page: 'ui',
    description: 'Presets drawer with the last recalled preset highlighted.',
    setup: async ({ page }) => {
      await js(page, `window.state.setActivePreset(1)`);
      await drawer(page, 'drawer-presets-btn', PRESETS);
    },
  },
  {
    name: 'drawer/presets/long-names',
    page: 'ui',
    description: 'Presets drawer with long preset names.',
    routes: longNames,
    setup: async ({ page }) => drawer(page, 'drawer-presets-btn', PRESETS),
  },
  {
    name: 'drawer/presets/loading',
    page: 'ui',
    description: 'Presets drawer while presets load.',
    routes: (page) => hang(page, '**/api/presets'),
    setup: async ({ page }) => drawer(page, 'drawer-presets-btn', PRESETS),
  },
  {
    name: 'drawer/presets/error',
    page: 'ui',
    description: 'Presets drawer when presets fail to load.',
    routes: (page) => abort(page, '**/api/presets'),
    setup: async ({ page }) => drawer(page, 'drawer-presets-btn', PRESETS),
  },
  {
    name: 'drawer/theme/default',
    page: 'ui',
    themed: true,
    description: 'Theme drawer: four presets, hover glow preference, card opacity, reset.',
    setup: async ({ page }) => drawer(page, 'drawer-theme-btn', THEME),
  },
  {
    name: 'drawer/theme/customize',
    page: 'ui',
    description: 'Theme drawer editing a preset (hue swatches, name).',
    setup: async ({ page }) => {
      await drawer(page, 'drawer-theme-btn', THEME);
      // A real click lands on edit button 3, which overlaps button 0 (see note).
      await page.locator('.theme-drawer .preset-edit-btn[data-edit-index="0"]').dispatchEvent('click');
      await page.locator('#color-customization:not(.hidden)').waitFor();
      await settle(page, 300);
    },
    note: "theme-drawer.js:122-136 nests the edit <button> inside the preset <button>; the parser splits them, so the edit buttons render as separate grid items that overlap: a click on the first preset's edit button hits the fourth's.",
  },
  {
    name: 'drawer/theme/low-opacity',
    page: 'ui',
    description: 'Card opacity at 40% (LOOK_AND_FEEL §3: surfaces must stay legible from 0.4 to 1.0).',
    prepare: { storage: { card_opacity: '0.4' } },
    setup: async ({ page }) => drawer(page, 'drawer-theme-btn', THEME),
  },
  {
    name: 'drawer/general/default',
    page: 'ui',
    description: 'General drawer: system info, matrix IP, connection test result.',
    setup: async ({ page }) => {
      await drawer(page, 'drawer-general-btn', GENERAL);
      await page.locator('#general-matrix-connection-status').filter({ hasNotText: 'Testing' }).waitFor();
      await settle(page, 300);
    },
  },
  {
    name: 'drawer/general/connection-error',
    page: 'ui',
    description: 'General drawer when the connection test fails.',
    routes: (page) => failJson(page, '**/api/settings/test-connection', 200, 'Connection refused (192.168.0.100:443)'),
    setup: async ({ page }) => {
      await drawer(page, 'drawer-general-btn', GENERAL);
      await settle(page, 800);
    },
  },
  {
    name: 'drawer/hardware/default',
    page: 'ui',
    description: 'Hardware drawer: LCD timeout, beep, external audio, power controls.',
    setup: async ({ page }) => drawer(page, 'drawer-hardware-btn', HARDWARE),
    note: 'Shows HTML defaults, not the device values: settings-panel.js loadCurrentSettings never runs (its #settings-btn trigger does not exist).',
  },
  {
    name: 'drawer/interface/default',
    page: 'ui',
    description: 'Interface drawer: CEC tray position, light-cycle animation, reduce glow, debug panel, kiosk link.',
    setup: async ({ page }) => drawer(page, 'drawer-interface-btn', INTERFACE),
  },
  {
    name: 'drawer/shortcuts/default',
    page: 'ui',
    themed: true,
    description: 'Shortcuts drawer: built-in and user shortcuts grouped by category, with favourite/dashboard/run buttons.',
    setup: async ({ page }) => drawer(page, 'drawer-shortcuts-btn', SHORTCUTS),
  },
  {
    name: 'drawer/shortcuts/scrolled-end',
    page: 'ui',
    description: 'Shortcuts drawer scrolled to the end (System / LCD groups, user shortcuts).',
    setup: async ({ page }) => drawer(page, 'drawer-shortcuts-btn', SHORTCUTS),
    scrollTo: '#shortcuts-drawer .shortcut-row >> nth=-1',
  },
  {
    name: 'drawer/shortcuts/rename',
    page: 'ui',
    description: 'Shortcuts drawer, renaming a shortcut.',
    setup: async ({ page }) => {
      await drawer(page, 'drawer-shortcuts-btn', SHORTCUTS);
      await page.locator('#shortcuts-drawer .shortcut-edit-btn').first().click();
      await settle(page, 300);
    },
  },
  {
    name: 'drawer/shortcuts/long-names',
    page: 'ui',
    description: 'Shortcuts drawer with long user-shortcut names.',
    routes: longNames,
    setup: async ({ page }) => drawer(page, 'drawer-shortcuts-btn', SHORTCUTS),
  },
  {
    name: 'drawer/shortcuts/empty',
    page: 'ui',
    description: 'Shortcuts drawer with no shortcuts.',
    routes: (page) => okJson(page, '**/api/shortcuts', { shortcuts: [] }),
    setup: async ({ page }) => drawer(page, 'drawer-shortcuts-btn', SHORTCUTS),
  },
  {
    name: 'drawer/shortcuts/loading',
    page: 'ui',
    description: 'Shortcuts drawer while shortcuts load.',
    setup: async ({ page }) => {
      await hang(page, '**/api/shortcuts');
      await drawer(page, 'drawer-shortcuts-btn', SHORTCUTS);
    },
  },
  {
    name: 'drawer/shortcuts/error',
    page: 'ui',
    description: 'Shortcuts drawer when shortcuts fail to load.',
    setup: async ({ page }) => {
      await abort(page, '**/api/shortcuts');
      await drawer(page, 'drawer-shortcuts-btn', SHORTCUTS);
    },
  },
  {
    name: 'drawer/integrations/flic',
    page: 'ui',
    themed: true,
    description: 'Integrations drawer, Flic Buttons tab (default): generator for button actions.',
    setup: async ({ page }) => drawer(page, 'drawer-integrations-btn', INTEGRATIONS),
  },
  {
    name: 'drawer/integrations/flic-cec',
    page: 'ui',
    description: 'Integrations drawer, Flic tab with a CEC command target (extra port row).',
    setup: async ({ page }) => {
      await drawer(page, 'drawer-integrations-btn', INTEGRATIONS);
      await page.locator('#flic-target-type').selectOption('cec');
      await settle(page, 300);
    },
    scrollTo: '#flic-cec-port-row',
  },
  {
    name: 'drawer/integrations/flic-profile',
    page: 'ui',
    description: 'Integrations drawer, Flic tab with a profile target.',
    setup: async ({ page }) => {
      await drawer(page, 'drawer-integrations-btn', INTEGRATIONS);
      await page.locator('#flic-target-type').selectOption('profile');
      await settle(page, 300);
    },
    scrollTo: '#flic-dynamic-inputs',
    note: 'Always warns "No Profiles created yet" because state.profiles is never loaded (integrations-drawer.js:526).',
  },
  {
    name: 'drawer/integrations/home-assistant',
    page: 'ui',
    description: 'Integrations drawer, Home Assistant tab (HACS setup + YAML generator).',
    setup: async ({ page }) => {
      await drawer(page, 'drawer-integrations-btn', INTEGRATIONS);
      await page.locator('#integrations-drawer .drawer-tab-btn[data-tab="ha"]').click();
      await settle(page, 300);
    },
  },
  {
    name: 'drawer/integrations/flic-generated-request',
    page: 'ui',
    description: 'Integrations drawer, Flic tab scrolled to the generated request (method, URL, body, SDK code).',
    setup: async ({ page }) => drawer(page, 'drawer-integrations-btn', INTEGRATIONS),
    scrollTo: '#flic-sdk-code-block',
  },
  {
    name: 'drawer/integrations/home-assistant-yaml',
    page: 'ui',
    description: 'Integrations drawer, Home Assistant tab scrolled to the REST command YAML generator.',
    setup: async ({ page }) => {
      await drawer(page, 'drawer-integrations-btn', INTEGRATIONS);
      await page.locator('#integrations-drawer .drawer-tab-btn[data-tab="ha"]').click();
      await settle(page, 300);
    },
    scrollTo: '#ha-yaml-output',
  },
  {
    name: 'drawer/integrations/unfolded-circle',
    page: 'ui',
    description: 'Integrations drawer, Unfolded Circle tab.',
    setup: async ({ page }) => {
      await drawer(page, 'drawer-integrations-btn', INTEGRATIONS);
      await page.locator('#integrations-drawer .drawer-tab-btn[data-tab="uc"]').click();
      await settle(page, 300);
    },
  },
  {
    name: 'drawer/settings/profiles',
    page: 'ui',
    description: 'Settings drawer (Phase 8), Profiles tab as it renders today (empty).',
    setup: async ({ page }) => {
      await js(page, `window.settingsDrawer.open('profiles')`);
      await settle(page, 500);
    },
    note: 'No button opens this drawer (only a #settings/<tab> hash change). The Profiles tab is always empty: state.profiles is never loaded.',
  },
  {
    name: 'drawer/settings/profiles-populated',
    page: 'ui',
    description: 'Settings drawer, Profiles tab with profiles (execute / favourite buttons).',
    setup: async ({ page }) => {
      await loadProfilesAndMacros(page);
      await js(page, `window.settingsDrawer.open('profiles')`);
      await settle(page, 500);
    },
    note: 'Needs state.profiles, which the app never loads; filled from /api/profiles here.',
  },
  {
    name: 'drawer/settings/scenes',
    page: 'ui',
    description: 'Settings drawer, Scenes tab (v2 scenes incl. a passcode-protected one).',
    setup: async ({ page }) => {
      await js(page, `window.settingsDrawer.open('scenes')`);
      await settle(page, 500);
    },
  },
  {
    name: 'drawer/settings/scenes-empty',
    page: 'ui',
    description: 'Settings drawer, Scenes tab with no scenes (create button).',
    routes: (page) => okJson(page, '**/api/v2/scenes', { scenes: [] }),
    setup: async ({ page }) => {
      await js(page, `window.settingsDrawer.open('scenes')`);
      await settle(page, 500);
    },
  },
  {
    name: 'drawer/settings/system',
    page: 'ui',
    description: 'Settings drawer, System tab (system actions by group).',
    setup: async ({ page }) => {
      await js(page, `window.settingsDrawer.open('system')`);
      await settle(page, 500);
    },
  },
  {
    name: 'drawer/stacked/deck-and-presets',
    page: 'ui',
    viewports: ['desktop', 'tablet', 'kiosk-tab-a11'],
    description: 'Control Deck and a right-side drawer open together (wide screens keep both).',
    setup: async ({ page }) => {
      await drawer(page, 'drawer-presets-btn', PRESETS);
      await page.locator('#side-nav-drawer.open').waitFor();
    },
  },

  // ===== Modals & dialogs ==================================================
  {
    name: 'modal/input-settings/default',
    page: 'ui',
    description: 'Input settings modal: name, icon, EDID, CEC, signal info.',
    setup: async ({ page }) => {
      await tab(page, 'inputs');
      await page.locator('#inputs-list .io-card[data-input="2"] .settings-btn').click();
      await page.locator('#input-settings-modal.visible').waitFor();
      await settle(page, 400);
    },
  },
  {
    name: 'modal/input-settings/icon-suggestion',
    page: 'ui',
    description: 'Input settings with the icon suggestion that appears after typing a known device name.',
    setup: async ({ page }) => {
      await tab(page, 'inputs');
      await page.locator('#inputs-list .io-card[data-input="8"] .settings-btn').click();
      await page.locator('#input-settings-modal.visible').waitFor();
      await page.locator('#input-name-field').fill('Xbox Series X');
      await page.locator('#input-icon-suggestion:not(.hidden)').waitFor();
      await settle(page, 300);
    },
  },
  {
    name: 'modal/input-settings/long-name',
    page: 'ui',
    description: 'Input settings modal for an input with a long name.',
    routes: longNames,
    setup: async ({ page }) => {
      await tab(page, 'inputs');
      await page.locator('#inputs-list .io-card[data-input="1"] .settings-btn').click();
      await page.locator('#input-settings-modal.visible').waitFor();
      await settle(page, 400);
    },
  },
  {
    name: 'modal/output-settings/default',
    page: 'ui',
    themed: true,
    description: 'Output settings modal: name, icon, enable, HDR/HDCP/scaler, ARC, mute, CEC.',
    setup: async ({ page }) => {
      await tab(page, 'outputs');
      await page.locator('#outputs-list .io-card[data-output="1"] .output-settings-btn').click();
      await page.locator('#output-settings-modal.visible').waitFor();
      await settle(page, 400);
    },
    note: 'HDR/HDCP selects may render blank: state defaults are the string "auto" (output-settings-modal.js:320).',
  },
  {
    name: 'modal/output-settings/disconnected-display',
    page: 'ui',
    description: 'Output settings for an output with no display connected.',
    setup: async ({ page }) => {
      await tab(page, 'outputs');
      await page.locator('#outputs-list .io-card[data-output="5"] .output-settings-btn').click();
      await page.locator('#output-settings-modal.visible').waitFor();
      await settle(page, 400);
    },
  },
  {
    name: 'modal/icon-picker/default',
    page: 'ui',
    description: 'Icon picker (all categories, current icon selected).',
    setup: async ({ page }) => {
      await tab(page, 'inputs');
      await page.locator('#inputs-list .io-card[data-input="2"] .settings-btn').click();
      await page.locator('#input-settings-modal.visible').waitFor();
      await page.locator('#input-icon-btn').click();
      await page.locator('#icon-picker-modal.visible').waitFor();
      await settle(page, 500);
    },
  },
  {
    name: 'modal/icon-picker/category',
    page: 'ui',
    description: 'Icon picker filtered to the Gaming category.',
    setup: async ({ page }) => {
      await js(page, `window.iconPicker.open('playstation-5', () => {})`);
      await page.locator('#icon-picker-modal.visible').waitFor();
      // The picker focuses its search box 100 ms after opening; let that
      // happen before the click so focus always ends on the category button.
      await settle(page, 400);
      await page.locator('.icon-picker-category-btn[data-category="gaming"]').click();
      await settle(page, 400);
    },
  },
  {
    name: 'modal/icon-picker/no-results',
    page: 'ui',
    description: 'Icon picker search with no results.',
    setup: async ({ page }) => {
      await js(page, `window.iconPicker.open('generic-input', () => {})`);
      await page.locator('#icon-picker-modal.visible').waitFor();
      await page.locator('#icon-picker-search').fill('zzzz');
      await settle(page, 500);
    },
  },
  {
    name: 'modal/icon-picker/recent',
    page: 'ui',
    description: 'Icon picker with recently used icons.',
    prepare: { storage: { orei_recent_icons: JSON.stringify(['apple-tv-ext', 'playstation-5', 'television', 'soundbar']) } },
    setup: async ({ page }) => {
      await js(page, `window.iconPicker.open('generic-input', () => {})`);
      await page.locator('#icon-picker-modal.visible').waitFor();
      await settle(page, 500);
    },
  },
  {
    name: 'modal/icon-picker/loading',
    page: 'ui',
    description: 'Icon picker skeleton.',
    setup: async ({ page }) => {
      await js(page, `window.iconPicker.open('generic-input', () => {}); window.iconPicker.showSkeleton()`);
      await settle(page, 300);
    },
  },
  {
    name: 'modal/save-profile/legacy',
    page: 'ui',
    description: 'Legacy "Save Profile" modal (index.html #save-scene-modal).',
    setup: async ({ page }) => {
      await js(page, `document.getElementById('save-scene-modal').setAttribute('aria-hidden', 'false')`);
      await settle(page, 300);
    },
    note: 'Unreachable in normal use (fallback path only); captured because it ships in index.html.',
  },
  ...(['general', 'hardware', 'interface'] as const).map(
    (t): CatalogEntry => ({
      name: `modal/settings-legacy/${t}`,
      page: 'ui',
      description: `Legacy tabbed Settings modal, ${t} tab.`,
      setup: async ({ page }) => {
        await js(page, `window.app.components.settingsPanel.open()`);
        await page.locator(`#settings-modal .settings-tab-btn[data-tab="${t}"]`).click();
        await settle(page, 800);
      },
      note: 'Unreachable: its trigger #settings-btn does not exist (settings-panel.js:29). Replaced by the General/Hardware/Interface drawers.',
    }),
  ),
  {
    name: 'dialog/confirm/reboot',
    page: 'ui',
    description: 'Confirm dialog (danger variant) from Hardware → Reboot.',
    setup: async ({ page }) => {
      await drawer(page, 'drawer-hardware-btn', HARDWARE);
      await page.locator('#hardware-reboot-btn').click();
      await page.locator('.confirm-dialog.confirm-dialog--visible').waitFor();
      await settle(page, 400);
    },
    note: 'Renders under the Hardware drawer: .confirm-dialog z-index 500 < drawer 1040.',
  },
  {
    name: 'dialog/confirm/power-cycle',
    page: 'ui',
    description: 'Confirm dialog (warning variant) from Hardware → Power Cycle.',
    setup: async ({ page }) => {
      await drawer(page, 'drawer-hardware-btn', HARDWARE);
      await page.locator('#hardware-power-cycle-btn').click();
      await page.locator('.confirm-dialog.confirm-dialog--visible').waitFor();
      await settle(page, 400);
    },
  },
  {
    name: 'dialog/confirm/default',
    page: 'ui',
    description: 'Confirm dialog, default variant, on its own.',
    setup: async ({ page }) => {
      await js(page, `void window.ConfirmDialog.confirm({ title: 'Delete profile?', message: 'Movie Night will be removed. This cannot be undone.', confirmText: 'Delete', cancelText: 'Cancel', variant: 'default' })`);
      await page.locator('.confirm-dialog.confirm-dialog--visible').waitFor();
      await settle(page, 400);
    },
  },
  {
    name: 'dialog/about/default',
    page: 'ui',
    description: 'About dialog (version, status, keyboard link).',
    setup: async ({ page }) => {
      await js(page, `AboutDialog.show()`);
      await page.locator('.about-dialog.about-dialog--visible').waitFor();
      await settle(page, 800);
    },
    note: 'No UI trigger. Always shows WebSocket "Disconnected" (about-dialog.js:167 reads a missing state.wsStatus).',
  },
  {
    name: 'dialog/keyboard-shortcuts',
    page: 'ui',
    description: 'Keyboard shortcuts help overlay.',
    setup: async ({ page }) => {
      await js(page, `KeyboardShortcuts.showHelp()`);
      await page.locator('.shortcut-help.shortcut-help--visible').waitFor();
      await settle(page, 400);
    },
    note: 'Pressing "?" never opens it (registered without shift, keyboard-shortcuts.js:53).',
  },
  {
    name: 'dialog/setup-wizard/connection',
    page: 'ui',
    description: 'Setup wizard, step 1 (matrix connection).',
    setup: async ({ page }) => {
      await js(page, `void SetupWizard.connectionSetup(() => {})`);
      await page.locator('.setup-wizard.setup-wizard--visible').waitFor();
      await settle(page, 400);
    },
    note: 'Never shown automatically; nothing in the app opens it.',
  },
  {
    name: 'dialog/setup-wizard/validation-error',
    page: 'ui',
    description: 'Setup wizard with an invalid IP.',
    setup: async ({ page }) => {
      await js(page, `void SetupWizard.connectionSetup(() => {})`);
      await page.locator('.setup-wizard.setup-wizard--visible').waitFor();
      await page.locator('.setup-wizard input[name="host"]').fill('');
      await page.locator('.setup-wizard__next').click();
      await page.locator('.setup-wizard__error--visible').waitFor();
      await settle(page, 200);
    },
  },
  {
    name: 'dialog/setup-wizard/testing',
    page: 'ui',
    description: 'Setup wizard, step 2 (testing connection).',
    setup: async ({ page }) => {
      await js(page, `void SetupWizard.connectionSetup(() => {})`);
      await page.locator('.setup-wizard.setup-wizard--visible').waitFor();
      await page.locator('.setup-wizard input[name="host"]').fill('192.168.0.100');
      await page.locator('.setup-wizard__next').click();
      await settle(page, 400);
    },
  },
  {
    name: 'dialog/context-menu/profile',
    page: 'ui',
    description: 'Context menu for a profile.',
    setup: async ({ page }) => {
      await js(page, `ContextMenu.forProfile({ id: 'movie_night', name: 'Movie Night' }).show(240, 200)`);
      await page.locator('.context-menu.context-menu--visible').waitFor();
      await settle(page, 300);
    },
    note: 'Not wired to any UI.',
  },
  {
    name: 'dialog/context-menu/output',
    page: 'ui',
    description: 'Context menu for an output.',
    setup: async ({ page }) => {
      await js(page, `ContextMenu.forOutput({ number: 1, name: 'TV' }).show(240, 200)`);
      await page.locator('.context-menu.context-menu--visible').waitFor();
      await settle(page, 300);
    },
    note: 'Not wired to any UI.',
  },
  {
    name: 'dialog/tooltip',
    page: 'ui',
    viewports: ['desktop'],
    description: 'Tooltip (the only [data-tooltip] is the About dialog keyboard link).',
    keepPointer: true,
    setup: async ({ page }) => {
      await js(page, `AboutDialog.show()`);
      await page.locator('.about-dialog.about-dialog--visible').waitFor();
      await settle(page, 600);
      await js(page, `Tooltip.show(document.querySelector('.about-dialog__keyboard'))`);
      await page.locator('#tooltip.tooltip--visible').waitFor();
      await settle(page, 300);
    },
  },
  {
    name: 'dialog/scene-cec',
    page: 'ui',
    description: 'Scene CEC configuration modal (targets per category).',
    setup: async ({ page }) => {
      await js(page, `(async () => { await window.sceneCecModal.open({ id: 'movie_night', name: 'Movie Night' }); document.getElementById('scene-cec-modal').classList.add('visible'); })()`);
      await settle(page, 600);
    },
    note: 'Invisible in the app: scene-cec-modal.js:204 sets aria-hidden only, but the overlay needs .visible; it also has no UI trigger. Forced visible here.',
  },
  {
    name: 'dialog/passcode-prompt',
    page: 'ui',
    description: 'Passcode prompt for a protected scene/profile.',
    viewports: [],
    note: 'Not capturable: the passcode prompt is a native window.prompt() (settings-drawer.js showPasscodePrompt), which screenshots do not include, and its automatic trigger never fires (api.js errors carry no .status).',
  },

  // ===== Editors ===========================================================
  {
    name: 'editor/profile/new',
    page: 'ui',
    themed: true,
    description: 'Profile editor, new profile (icon, name, routing preview, macros, passcode).',
    setup: async ({ page }) => {
      await tab(page, 'profiles');
      await page.locator('#save-scene-btn').click();
      await page.locator('#profile-editor-modal.visible').waitFor();
      await settle(page, 600);
    },
  },
  {
    name: 'editor/profile/validation-error',
    page: 'ui',
    description: 'Profile editor after saving with no name.',
    setup: async ({ page }) => {
      await tab(page, 'profiles');
      await page.locator('#save-scene-btn').click();
      await page.locator('#profile-editor-modal.visible').waitFor();
      await page.locator('#profile-name').fill('');
      await page.locator('#save-profile-btn').click();
      await settle(page, 400);
    },
    note: 'The warning toast (z-index 300) renders under the modal.',
  },
  {
    name: 'editor/profile/passcode',
    page: 'ui',
    description: 'Profile editor with passcode protection switched on.',
    setup: async ({ page }) => {
      await tab(page, 'profiles');
      await page.locator('#save-scene-btn').click();
      await page.locator('#profile-editor-modal.visible').waitFor();
      // Let the editor's own 100 ms autofocus happen first.
      await settle(page, 400);
      await page.locator('#profile-name').fill('Kids Gaming');
      await page.locator('#profile-password-protected').check({ force: true });
      await page.locator('#profile-password-fields').waitFor();
      await settle(page, 300);
    },
    // Deterministic scroll (the check() click may or may not scroll the modal).
    scrollTo: '#profile-password-fields',
  },
  {
    name: 'editor/profile/edit',
    page: 'ui',
    description: 'Profile editor, editing an existing profile (macros, power macros, delete button).',
    setup: async ({ page }) => {
      await page.evaluate(async () => {
        const w = window as any; // eslint-disable-line @typescript-eslint/no-explicit-any
        const profiles = (await (await fetch('/api/profiles')).json()).data.profiles;
        await w.profileEditor.openEdit(profiles.find((p: { id: string }) => p.id === 'movie_night'));
      });
      await page.locator('#profile-editor-modal.visible').waitFor();
      await settle(page, 800);
    },
    note: 'The UI edit path (Profiles tab → edit) fetches /api/v2/scenes/{id} and fails; opened with the editor API here.',
  },
  {
    name: 'editor/profile/edit-bottom',
    page: 'ui',
    description: 'Profile editor scrolled to routing preview, macros, passcode and execution history.',
    setup: async ({ page }) => {
      await page.evaluate(async () => {
        const w = window as any; // eslint-disable-line @typescript-eslint/no-explicit-any
        const profiles = (await (await fetch('/api/profiles')).json()).data.profiles;
        await w.profileEditor.openEdit(profiles.find((p: { id: string }) => p.id === 'movie_night'));
      });
      await page.locator('#profile-editor-modal.visible').waitFor();
      await settle(page, 800);
    },
    scrollTo: '#profile-execution-log',
  },
  {
    name: 'editor/scene/new',
    page: 'ui',
    description: 'Scene editor, new scene (from the Settings drawer Scenes tab).',
    setup: async ({ page }) => {
      await js(page, `window.settingsDrawer.open('scenes')`);
      await settle(page, 400);
      await page.locator('#settings-drawer .create-scene-btn').first().click();
      await page.locator('#scene-editor-modal.open').waitFor();
      await settle(page, 500);
    },
    note: 'Opens behind the Settings drawer (.modal z-index 200 < drawer 1040).',
  },
  {
    name: 'editor/scene/new-standalone',
    page: 'ui',
    description: 'Scene editor on its own (no drawer over it).',
    setup: async ({ page }) => {
      await js(page, `window.sceneEditor.open(null)`);
      await page.locator('#scene-editor-modal.open').waitFor();
      await settle(page, 500);
    },
  },
  {
    name: 'editor/scene/edit',
    page: 'ui',
    description: 'Scene editor editing "Movie Night" (macro, profile and system-action steps; override).',
    setup: async ({ page }) => {
      await js(page, `window.sceneEditor.open('scene_movienight01')`);
      await page.locator('#scene-editor-modal.open').waitFor();
      await settle(page, 800);
    },
  },
  {
    name: 'editor/scene/passcode',
    page: 'ui',
    description: 'Scene editor editing the passcode-protected scene.',
    setup: async ({ page }) => {
      await js(page, `window.sceneEditor.open('scene_kidslocked')`);
      await page.locator('#scene-editor-modal.open').waitFor();
      await settle(page, 800);
    },
  },
  {
    name: 'editor/scene/validation-error',
    page: 'ui',
    description: 'Scene editor after Save: "Scene name is required".',
    setup: async ({ page }) => {
      await js(page, `window.sceneEditor.open('scene_movienight01')`);
      await page.locator('#scene-editor-modal.open').waitFor();
      await settle(page, 500);
      await page.locator('#scene-editor-save').click();
      await settle(page, 400);
    },
    note: 'Always fails validation: scene-editor.js:90 renders a duplicate id="scene-name" and save() reads the hidden legacy input.',
  },
  {
    name: 'editor/scene/conflicts',
    page: 'ui',
    description: 'Scene editor showing profile setting conflicts.',
    setup: async ({ page }) => {
      await js(page, `window.sceneEditor.open(null)`);
      await page.locator('#scene-editor-modal.open').waitFor();
      await js(
        page,
        `(() => { const e = window.sceneEditor; e.conflicts = [{ output: 1, setting: 'hdr', profiles: [{ id: 'movie_night', name: 'Movie Night', value: 1 }, { id: 'game_day', name: 'Game Day', value: 2 }] }]; e.render(); })()`,
      );
      await settle(page, 400);
    },
    note: 'Normally reached only through prompt()-driven step adds; conflicts injected into the editor here.',
  },
  {
    name: 'editor/cec-macro/list',
    page: 'ui',
    description: 'CEC macro editor, macro list.',
    setup: async ({ page }) => {
      await js(page, `cecMacroEditor.open()`);
      await page.locator('#cec-macro-modal.visible').waitFor();
      await settle(page, 600);
    },
    note: 'No working UI trigger ("Create a macro" uses window.cecMacroEditor, which is undefined).',
  },
  {
    name: 'editor/cec-macro/empty',
    page: 'ui',
    description: 'CEC macro editor with no macros.',
    routes: (page) => okJson(page, '**/api/cec/macros', { macros: [] }),
    setup: async ({ page }) => {
      await js(page, `cecMacroEditor.open()`);
      await page.locator('#cec-macro-modal.visible').waitFor();
      await settle(page, 600);
    },
  },
  {
    name: 'editor/cec-macro/edit',
    page: 'ui',
    description: 'CEC macro editor editing a two-step macro.',
    setup: async ({ page }) => {
      await js(page, `cecMacroEditor.open()`);
      await page.locator('#cec-macro-modal.visible').waitFor();
      await page.locator('#cec-macro-modal .macro-item[data-id="macro_tv_on"] .btn-edit').click();
      await page.locator('#cec-macro-modal .macro-edit-view').waitFor({ state: 'visible' });
      await settle(page, 600);
    },
  },
  {
    name: 'editor/cec-macro/validation-error',
    page: 'ui',
    description: 'New CEC macro saved without a name.',
    setup: async ({ page }) => {
      await js(page, `cecMacroEditor.open()`);
      await page.locator('#cec-macro-modal.visible').waitFor();
      await page.locator('#new-macro-btn').click();
      await page.locator('#add-step-btn').click();
      await page.locator('#save-macro-btn').click();
      await settle(page, 400);
    },
  },

  // ===== CEC ===============================================================
  {
    name: 'cec-remote/output-1',
    page: 'ui',
    themed: true,
    description: 'CEC remote opened from the TV output tile (display CEC: power, navigation, volume).',
    setup: async ({ page }) => {
      await tab(page, 'outputs');
      await page.locator('#outputs-list .io-card[data-output="1"] .cec-btn').click();
      await page.locator('.cec-dropdown').waitFor();
      await settle(page, 300);
    },
  },
  {
    name: 'cec-remote/input-2',
    page: 'ui',
    description: 'CEC remote opened from the Apple TV input tile (source CEC incl. playback).',
    setup: async ({ page }) => {
      await tab(page, 'inputs');
      await page.locator('#inputs-list .io-card[data-input="2"] .cec-btn').click();
      await page.locator('.cec-dropdown').waitFor();
      await settle(page, 300);
    },
  },
  {
    name: 'cec-remote/matrix-card',
    page: 'ui',
    description: 'CEC remote opened from a routing card in the matrix cards view.',
    prepare: { storage: { 'matrix-view-mode': 'cards' } },
    setup: async ({ page }) => {
      await page.locator('#matrix-mobile-view .card-cec-btn[data-output="1"]').click();
      await page.locator('.cec-dropdown').waitFor();
      await settle(page, 300);
    },
  },
  {
    name: 'cec-tray/fab',
    page: 'ui',
    description: 'Floating CEC tray button (collapsed).',
    setup: async ({ page }) => {
      await page.locator('#cec-tray .cec-tray-fab').waitFor();
    },
  },
  {
    name: 'cec-tray/expanded',
    page: 'ui',
    themed: true,
    description: 'CEC tray expanded: target buttons, power, D-pad (wide) or trackpad (narrow), playback, volume.',
    setup: async ({ page }) => {
      await page.locator('#cec-tray .cec-tray-fab').click();
      await page.locator('#cec-tray.expanded').waitFor();
      await settle(page, 400);
    },
    note: 'Clicking the FAB throws an uncaught TypeError (cec-tray.js:1186 queries .target-name; markup uses .target-abbrev). The panel still opens.',
  },
  {
    name: 'cec-tray/target-selector',
    page: 'ui',
    description: 'CEC tray target selector (choose navigation device).',
    setup: async ({ page }) => {
      await page.locator('#cec-tray .cec-tray-fab').click();
      await page.locator('#cec-tray.expanded').waitFor();
      await page.locator('#cec-tray .cec-header-target-btn[data-target="navigation"]').click();
      await page.locator('.cec-target-selector').waitFor();
      await settle(page, 300);
    },
  },
  {
    name: 'cec-tray/bottom-left',
    page: 'ui',
    viewports: ['desktop'],
    description: 'CEC tray expanded at the bottom-left position (Interface setting).',
    prepare: { storage: { orei_cec_tray_position: 'bottom-left' } },
    setup: async ({ page }) => {
      await page.locator('#cec-tray .cec-tray-fab').click();
      await page.locator('#cec-tray.expanded').waitFor();
      await settle(page, 400);
    },
  },

  // ===== Toasts ============================================================
  ...(['success', 'error', 'warning', 'info'] as const).map(
    (t): CatalogEntry => ({
      name: `toast/${t}`,
      page: 'ui',
      description: `${t} toast.`,
      setup: async ({ page }) => {
        const msg = {
          success: 'Routed AppleTV to all outputs',
          error: 'Failed to route all: Matrix not connected',
          warning: 'At least one tab must remain pinned',
          info: 'Enter the matrix IP address',
        }[t];
        await js(page, `window.toast.show(${JSON.stringify(msg)}, '${t}', 0)`);
        await settle(page, 300);
      },
    }),
  ),
  {
    name: 'toast/stacked',
    page: 'ui',
    description: 'Several toasts at once.',
    setup: async ({ page }) => {
      await js(
        page,
        `window.toast.show('Refreshing...', 'info', 0); window.toast.show('Refreshed', 'success', 0); window.toast.show('CEC: power_on failed for TV', 'error', 0)`,
      );
      await settle(page, 300);
    },
  },

  // ===== Components and debug =============================================
  {
    name: 'component/empty-state/all-presets',
    page: 'ui',
    description: 'EmptyState component presets (connection lost, no scenes/inputs/outputs, no search results).',
    setup: async ({ page }) => {
      await tab(page, 'profiles');
      await js(
        page,
        `(() => { const el = document.getElementById('scenes-list'); el.innerHTML = ''; for (const p of ['connectionLost', 'noScenes', 'noInputs', 'noOutputs', 'searchNoResults']) { const d = document.createElement('div'); el.appendChild(d); EmptyState.fromPreset(p).mount(d); } })()`,
      );
      await settle(page, 300);
    },
    note: 'The EmptyState component is never used by the app; mounted into the Profiles list to review it.',
  },
  {
    name: 'debug/fab',
    page: 'ui',
    description: 'Debug panel toggle button (Interface → Show Debug Panel).',
    prepare: { storage: { 'debug-fab-visible': 'true' } },
  },
  ...(['state', 'routing', 'names', 'logs'] as const).map(
    (t): CatalogEntry => ({
      name: `debug/panel/${t}`,
      page: 'ui',
      description: `Debug panel, ${t} tab.`,
      prepare: { storage: { 'debug-fab-visible': 'true' } },
      setup: async ({ page }) => {
        await page.locator('#debug-toggle').click();
        await page.locator('#debug-panel.open').waitFor();
        await page.locator(`#debug-panel .debug-tab[data-tab="${t}"]`).click();
        await settle(page, 300);
      },
      // The logs tab lists API responses in arrival order, which varies.
      mask: t === 'logs' ? ['#debug-logs'] : [],
    }),
  ),

  // ===== Kiosk =============================================================
  ...(['routing', 'presets', 'shortcuts', 'profiles'] as const).flatMap((t): CatalogEntry[] => [
    {
      name: `kiosk/${t}/default`,
      page: 'kiosk',
      themed: t === 'routing',
      description: `Kiosk ${t} tab (tiles, header, output status footer).`,
      setup: async ({ page }) => kioskTab(page, t),
      note:
        t === 'routing'
          ? 'Input tiles are all "unknown" grey and footer tiles all dimmed: kiosk.html:2514 polls /api/inputs/status and /api/outputs/status, which 404. The kiosk does not follow the theme presets.'
          : undefined,
    },
    {
      name: `kiosk/${t}/edit-mode`,
      page: 'kiosk',
      description: `Kiosk ${t} tab in Edit Layout mode.`,
      setup: async ({ page }) => {
        await kioskTab(page, t);
        await kioskEdit(page);
      },
    },
  ]),
  {
    name: 'kiosk/routing/long-names',
    page: 'kiosk',
    description: 'Kiosk routing tiles and footer with long names.',
    routes: longNames,
  },
  {
    name: 'kiosk/presets/long-names',
    page: 'kiosk',
    description: 'Kiosk presets with long names.',
    routes: longNames,
    setup: async ({ page }) => kioskTab(page, 'presets'),
  },
  {
    name: 'kiosk/routing/all-to-one',
    page: 'kiosk',
    description: 'Kiosk routing with every output on one input (active tile and badge).',
    routes: allToInput2,
  },
  {
    name: 'kiosk/routing/tile-pressed',
    page: 'kiosk',
    description: 'Kiosk input tile while pressed (touch feedback).',
    keepPointer: true,
    setup: async ({ page }) => {
      const box = await page.locator('#kioskGrid .kiosk-btn').nth(1).boundingBox();
      if (!box) throw new Error('tile not visible');
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await page.mouse.down();
      await settle(page, 200);
    },
  },
  {
    name: 'kiosk/shortcuts/empty-slots',
    page: 'kiosk',
    description: 'Kiosk shortcuts with no slots assigned (placeholders).',
    prepare: { storage: { kiosk_shortcuts: JSON.stringify(Array(8).fill(null)) } },
    setup: async ({ page }) => kioskTab(page, 'shortcuts'),
  },
  {
    name: 'kiosk/profiles/empty-slots',
    page: 'kiosk',
    description: 'Kiosk profiles with no slots assigned (placeholders).',
    prepare: { storage: { kiosk_profiles: JSON.stringify(Array(8).fill(null)) } },
    setup: async ({ page }) => kioskTab(page, 'profiles'),
  },
  {
    name: 'kiosk/routing-modal/step-1',
    page: 'kiosk',
    themed: true,
    description: 'Kiosk routing wizard, step 1: choose outputs (Route to all / single output).',
    setup: async ({ page }) => {
      await page.locator('#kioskGrid .kiosk-btn').nth(4).click();
      await page.locator('#routingModal.show').waitFor();
      await settle(page, 400);
    },
    note: 'The Next button on step 1 has no handler (kiosk.html:1357).',
  },
  {
    name: 'kiosk/routing-modal/step-2',
    page: 'kiosk',
    description: 'Kiosk routing wizard, step 2: audio options.',
    setup: async ({ page }) => {
      await page.locator('#kioskGrid .kiosk-btn').nth(4).click();
      await page.locator('#routingModal.show').waitFor();
      await page.locator('#wizardOutputsList .wizard-option-btn[data-output="1"]').click();
      await page.locator('#routingStep2').waitFor({ state: 'visible' });
      await settle(page, 300);
    },
  },
  {
    name: 'kiosk/routing-modal/advanced',
    page: 'kiosk',
    description: 'Kiosk routing wizard, step 2 with advanced output settings.',
    setup: async ({ page }) => {
      await page.locator('#kioskGrid .kiosk-btn').nth(4).click();
      await page.locator('#routingModal.show').waitFor();
      await page.locator('#routeToAllBtn').click();
      await page.locator('#routingStep2').waitFor({ state: 'visible' });
      await page.locator('#toggleAdvancedRouting').click();
      await settle(page, 300);
    },
    note: 'HDR/scaler/HDCP option values do not match the API (kiosk.html:1329-1346); Apply always mutes outputs and turns ARC on.',
  },
  {
    name: 'kiosk/cec-remote/output-1',
    page: 'kiosk',
    themed: true,
    description: 'Kiosk CEC remote drawer for the TV (source/display target, D-pad, playback, volume, power).',
    setup: async ({ page }) => {
      await page.locator('#outputStatusGrid .output-tile').nth(0).click();
      await page.locator('#cecRemoteModal.show').waitFor();
      await settle(page, 400);
    },
  },
  {
    name: 'kiosk/cec-remote/display-target',
    page: 'kiosk',
    description: 'Kiosk CEC remote targeting the display (playback hidden).',
    setup: async ({ page }) => {
      await page.locator('#outputStatusGrid .output-tile').nth(0).click();
      await page.locator('#cecRemoteModal.show').waitFor();
      await page.locator('#btnTargetDisplay').click();
      await settle(page, 300);
    },
  },
  {
    name: 'kiosk/preset-config',
    page: 'kiosk',
    description: 'Kiosk preset configuration (rename / save current routing).',
    setup: async ({ page }) => {
      await kioskTab(page, 'presets');
      await kioskEdit(page);
      await page.locator('#presetsGrid .kiosk-btn').nth(0).click();
      await page.locator('#presetConfigModal.show').waitFor();
      await settle(page, 300);
    },
  },
  {
    name: 'kiosk/slot-mapper/shortcut',
    page: 'kiosk',
    description: 'Kiosk slot mapper for a shortcut slot (choose a shortcut).',
    setup: async ({ page }) => {
      await kioskTab(page, 'shortcuts');
      await kioskEdit(page);
      await page.locator('#shortcutsGrid .kiosk-btn').nth(0).click();
      await page.locator('#slotMapperModal.show').waitFor();
      await settle(page, 300);
    },
  },
  {
    name: 'kiosk/slot-mapper/shortcut-empty',
    page: 'kiosk',
    description: 'Kiosk slot mapper when there are no shortcuts.',
    routes: (page) => okJson(page, '**/api/shortcuts', { shortcuts: [] }),
    prepare: { storage: { kiosk_shortcuts: JSON.stringify(Array(8).fill(null)) } },
    setup: async ({ page }) => {
      await kioskTab(page, 'shortcuts');
      await kioskEdit(page);
      await page.locator('#shortcutsGrid .kiosk-btn').nth(0).click();
      await page.locator('#slotMapperModal.show').waitFor();
      await settle(page, 300);
    },
  },
  {
    name: 'kiosk/slot-mapper/profile',
    page: 'kiosk',
    description: 'Kiosk slot mapper for an empty profile slot (create new / choose profile).',
    setup: async ({ page }) => {
      await kioskTab(page, 'profiles');
      await kioskEdit(page);
      await page.locator('#profilesGrid .kiosk-btn').nth(5).click();
      await page.locator('#slotMapperModal.show').waitFor();
      await settle(page, 300);
    },
  },
  ...([1, 2, 3] as const).map(
    (step): CatalogEntry => ({
      name: `kiosk/profile-wizard/step-${step}`,
      page: 'kiosk',
      description: ['', 'Profile wizard step 1: name and icon.', 'Profile wizard step 2: routing per output.', 'Profile wizard step 3: power on/off macros.'][step],
      // Work around kiosk.html:2469 (reads data.data instead of data.data.macros,
      // then macros.map throws and the wizard never opens).
      routes: (page) =>
        mutateJson(page, '**/api/cec/macros', (b: Json) => ({ ...b, data: b.data?.macros ?? [] })),
      setup: async ({ page }) => {
        await kioskTab(page, 'profiles');
        await kioskEdit(page);
        await page.locator('#profilesGrid .kiosk-btn').nth(5).click();
        await page.locator('#slotMapperModal.show').waitFor();
        await page.locator('#slotMappingList .slot-mapping-item').first().click();
        await page.locator('#profileModal.show').waitFor();
        if (step >= 2) {
          await page.locator('#profileNameInput').fill('Date Night');
          await page.locator('#profileNextBtn').click();
        }
        if (step >= 3) await page.locator('#profileNextBtn').click();
        await settle(page, 300);
      },
      note: 'Unreachable today: the wizard throws before opening (kiosk.html:2469/2216, /api/cec/macros shape). Captured with the macros response reshaped to what the kiosk expects.',
    }),
  ),
  {
    name: 'kiosk/toast/success',
    page: 'kiosk',
    description: 'Kiosk toast (shown when entering edit mode).',
    setup: async ({ page }) => {
      await page.locator('#kioskEditBtn').click();
      await page.locator('#kioskToast.show').waitFor();
      await settle(page, 150);
    },
  },
  {
    name: 'kiosk/disconnected',
    page: 'kiosk',
    description: 'Kiosk when the hub reports the matrix unreachable on first load (red status, empty grids).',
    prepare: { noWebSocket: true },
    routes: (page) => failJson(page, '**/api/status', 503, 'Matrix not connected'),
    ready: false,
    setup: async ({ page }) => {
      await page.locator('#statusText', { hasText: 'Disconnected' }).waitFor();
      await settle(page, 400);
    },
  },
];

async function kioskTab(page: Page, t: 'routing' | 'presets' | 'shortcuts' | 'profiles') {
  if (t !== 'routing') await page.locator(`.kiosk-tab-btn[data-tab="${t}"]`).click();
  await page.locator(`.kiosk-tab-btn[data-tab="${t}"].active`).waitFor();
  await settle(page, 400);
  await page.evaluate(() => {
    const c = document.getElementById('kioskSwipeContainer');
    if (c) c.scrollLeft = 0;
  });
}

/** Enter kiosk edit mode and wait for its toast to go away. */
async function kioskEdit(page: Page) {
  await page.locator('#kioskEditBtn').click();
  await page.locator('#kioskEditBtn.active').waitFor();
  await page.waitForFunction(() => !document.getElementById('kioskToast')?.classList.contains('show'), undefined, {
    timeout: 6000,
  });
  await settle(page, 200);
}

/** Validate names once at import: unique, lower-case, hierarchical. */
for (const [i, e] of CATALOG.entries()) {
  if (!/^[a-z0-9-]+(\/[a-z0-9-]+)+$/.test(e.name)) throw new Error(`bad catalog entry name ${e.name}`);
  if (CATALOG.findIndex((o) => o.name === e.name) !== i) throw new Error(`duplicate catalog entry ${e.name}`);
}
