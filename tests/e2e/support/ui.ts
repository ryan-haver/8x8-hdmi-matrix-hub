// Page harness shared by the smoke and visual specs: deterministic page setup,
// app readiness waits and API response shaping. Nothing here changes web/;
// it only controls the browser (storage, clock, network) around the app.
import { expect, test as base, type Page, type Route, type TestInfo } from '@playwright/test';
import { Sim } from './stack';

/** Frozen wall-clock time for every page (Date only; timers keep running). */
export const FIXED_TIME = new Date('2026-09-24T12:00:00Z');

/** Theme presets as stored by web/js/components/theme-drawer.js (index into theme_presets). */
export const THEMES = {
  'tron-classic': 0,
  neon: 1,
  royal: 2,
  vaporwave: 3,
} as const;
export type ThemeName = keyof typeof THEMES;

/**
 * localStorage every page starts from (a fresh context per test). Mirrors a
 * first visit, pinned down where the app would otherwise race:
 * - orei_phase7_migration_done: skip the one-time migration (it deletes
 *   orei_dashboard_config and can POST favourites).
 * - orei_dashboard_config: what a first visit ends up with. Without it the
 *   widgets auto-pin in registration order, which races with the 100 ms
 *   cecTray timer; routing-dashboard is the one that wins on a first visit.
 * - tron_background_enabled=false: the default, set explicitly (§5.3).
 */
export const BASE_STORAGE: Record<string, string> = {
  orei_phase7_migration_done: 'true',
  orei_dashboard_config: JSON.stringify({
    pinnedWidgets: ['routing-dashboard'],
    hiddenMobileWidgets: [],
    widgetOrder: ['routing-dashboard'],
  }),
  tron_background_enabled: 'false',
};

/** CSS that removes motion and the text caret (in addition to Playwright's animations: 'disabled'). */
export const FREEZE_CSS = `
*, *::before, *::after {
  transition-duration: 0s !important;
  transition-delay: 0s !important;
  animation-delay: 0s !important;
  caret-color: transparent !important;
  scroll-behavior: auto !important;
}
`;

export type PrepareOptions = {
  theme?: ThemeName;
  /** Extra localStorage entries (merged over BASE_STORAGE); null removes a key. */
  storage?: Record<string, string | null>;
  /** Keep the real clock (the Tron snapshot installs its own paused clock). */
  realClock?: boolean;
  /** Replace window.WebSocket with one that never connects (disconnected header/status). */
  noWebSocket?: boolean;
  /**
   * Hub "status" broadcasts on the WebSocket. Default 'drop'.
   *
   * Every GET /api/status/outputs with a warm cache makes the hub broadcast a
   * background refresh to ALL open pages (src/rest_api/outputs.py:59), so
   * pages would re-render at times set by other tests, and response shaping
   * done with page.route (long names, no signal, ...) would be overwritten.
   * The broadcast also resets output names to "Output N" (hub bug: _format_outputs
   * uses the hub's name cache, empty in modular mode). 'drop' keeps each page
   * on its own REST data; 'pass' lets them through (see catalog entry
   * app/ws-status-refresh/output-names).
   */
  wsStatus?: 'drop' | 'pass';
};

const wsStatusFrames = new WeakMap<Page, { count: number }>();

/** Number of hub "status" broadcasts the page has received (wsStatus: 'pass'). */
export function statusFramesReceived(page: Page) {
  return wsStatusFrames.get(page)?.count ?? 0;
}

/**
 * Deterministic page setup; call before the first navigation.
 * - localStorage seeded once per page (sessionStorage flag), so reloads keep state
 * - Math.random seeded (mulberry32), Date frozen at FIXED_TIME
 * - transitions and caret disabled
 */
export async function preparePage(page: Page, opts: PrepareOptions = {}) {
  const storage: Record<string, string | null> = {
    ...BASE_STORAGE,
    active_preset_index: String(THEMES[opts.theme ?? 'tron-classic']),
    ...opts.storage,
  };
  await page.addInitScript(
    ({ storage, css, noWebSocket }) => {
      try {
        if (!sessionStorage.getItem('__e2e_seeded')) {
          localStorage.clear();
          for (const [k, v] of Object.entries(storage)) {
            if (v === null) localStorage.removeItem(k);
            else localStorage.setItem(k, v);
          }
          sessionStorage.setItem('__e2e_seeded', '1');
        }
      } catch {
        /* storage unavailable */
      }
      // Seeded PRNG so anything random (the Tron background) is repeatable.
      let seed = 0x5eed1234;
      (window as unknown as { __e2eReseed: () => void }).__e2eReseed = () => {
        seed = 0x5eed1234;
      };
      Math.random = () => {
        seed |= 0;
        seed = (seed + 0x6d2b79f5) | 0;
        let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      };
      if (noWebSocket) {
        // A socket that fails to connect, like a hub whose /ws is unreachable.
        const Closed = class {
          static CONNECTING = 0;
          static OPEN = 1;
          static CLOSING = 2;
          static CLOSED = 3;
          readyState = 3;
          onopen: unknown = null;
          onclose: ((e: unknown) => void) | null = null;
          onerror: ((e: unknown) => void) | null = null;
          onmessage: unknown = null;
          constructor() {
            setTimeout(() => {
              this.onerror?.(new Event('error'));
              this.onclose?.({ code: 1006, reason: '', wasClean: false });
            }, 0);
          }
          send() {}
          close() {}
          addEventListener() {}
          removeEventListener() {}
        };
        (window as unknown as { WebSocket: unknown }).WebSocket = Closed;
      }
      const inject = () => {
        const style = document.createElement('style');
        style.setAttribute('data-e2e', 'freeze');
        style.textContent = css;
        document.head.appendChild(style);
      };
      if (document.head) inject();
      else document.addEventListener('DOMContentLoaded', inject, { once: true });
    },
    { storage, css: FREEZE_CSS, noWebSocket: !!opts.noWebSocket },
  );
  if (!opts.realClock) await page.clock.setFixedTime(FIXED_TIME);

  if (!opts.noWebSocket) {
    const counter = { count: 0 };
    wsStatusFrames.set(page, counter);
    const drop = (opts.wsStatus ?? 'drop') === 'drop';
    await page.routeWebSocket(/\/ws$/, (ws) => {
      const server = ws.connectToServer();
      server.onMessage((message) => {
        if (typeof message === 'string' && /^\s*\{\s*"event"\s*:\s*"status"/.test(message)) {
          counter.count++;
          if (drop) return;
        }
        ws.send(message);
      });
    });
  }
}

/** Wait until the main UI has finished its startup sequence (see web/js/app.js init()). */
export async function waitForUiReady(page: Page) {
  await page.waitForFunction(
    () => {
      const w = window as unknown as {
        app?: unknown;
        cecTray?: unknown;
        state?: { ui?: { dataLoaded?: boolean } };
      };
      return (
        !!w.app &&
        !!document.querySelector('#drawer-tab-settings-list li.tab-settings-item') &&
        !!w.cecTray &&
        w.state?.ui?.dataLoaded === true
      );
    },
    undefined,
    { timeout: 20_000 },
  );
  await settle(page, 600);
}

export type OpenUiOptions = {
  /** Wait for app readiness (disable for states where loading never completes). */
  ready?: boolean;
};

/**
 * Load /ui.
 *
 * /api/dashboard/layout is delayed by 400 ms: the dashboard renders its cards
 * from a 100 ms timer that usually fires before this response arrives
 * (dashboard-manager.js), so a fast local hub could otherwise win that race
 * and render cards a real client normally does not show on load.
 */
export async function openUi(page: Page, opts: OpenUiOptions = {}) {
  await page.route('**/api/dashboard/layout', async (route) => {
    await new Promise((r) => setTimeout(r, 400));
    await route.fallback();
  });
  await page.goto('/ui');
  if (opts.ready !== false) await waitForUiReady(page);
  else await settle(page, 1500);
}

/** Load /kiosk and wait for its first render (web/kiosk.html init()). */
export async function openKiosk(page: Page, opts: { ready?: boolean } = {}) {
  await page.goto('/kiosk');
  if (opts.ready !== false) {
    await expect(page.locator('#kioskGrid .kiosk-btn')).toHaveCount(8, { timeout: 20_000 });
    await expect(page.locator('#statusText')).toHaveText('Connected');
  }
  await settle(page, 600);
}

/** Let pending timers, rAF callbacks and network responses land. */
export async function settle(page: Page, ms = 300) {
  // Bounded: some states deliberately hold a request open forever.
  await page.waitForLoadState('networkidle', { timeout: 3000 }).catch(() => {});
  await page.evaluate(
    (ms) =>
      new Promise<void>((resolve) =>
        setTimeout(() => requestAnimationFrame(() => requestAnimationFrame(() => resolve())), ms),
      ),
    ms,
  );
  await page.evaluate(() => document.fonts.ready.then(() => undefined));
}

/** Move the pointer off the page so no :hover style leaks into a capture. */
export async function parkPointer(page: Page) {
  await page.mouse.move(-10, -10).catch(async () => {
    const vp = page.viewportSize();
    await page.mouse.move(0, (vp?.height ?? 800) - 1);
  });
}

type Json = Record<string, unknown>;

/**
 * Serve the hub's real response for `glob` with `mutate` applied to its JSON
 * body. Used for states that depend on matrix hardware (no signal, unplugged
 * cables, long names) without changing the simulator shared by all tests.
 */
export async function mutateJson(page: Page, glob: string, mutate: (body: Json) => void | Json) {
  await page.route(glob, async (route: Route) => {
    const response = await route.fetch();
    const body = (await response.json()) as Json;
    const replaced = mutate(body) ?? body;
    await route.fulfill({ response, json: replaced });
  });
}

/** Answer `glob` with a fixed status and JSON body (the hub's error envelope by default). */
export async function failJson(page: Page, glob: string, status = 503, error = 'Matrix not connected') {
  await page.route(glob, (route) =>
    route.fulfill({ status, contentType: 'application/json', json: { success: false, data: null, error } }),
  );
}

/** Answer `glob` with a successful envelope around `data`. */
export async function okJson(page: Page, glob: string, data: unknown) {
  await page.route(glob, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', json: { success: true, data, error: null } }),
  );
}

let requestCounter = 0;
/** A unique client address per test, so each test has its own hub rate-limit bucket. */
function forwardedFor(info: TestInfo) {
  const n = requestCounter++;
  return `10.${(info.workerIndex % 250) + 1}.${Math.floor(n / 250) % 250}.${(n % 250) + 1}`;
}

export type E2EFixtures = {
  sim: Sim;
  /** Uncaught page errors and console errors seen during the test. */
  pageProblems: { pageErrors: string[]; consoleErrors: string[] };
};

export const test = base.extend<E2EFixtures, { simWorker: Sim }>({
  extraHTTPHeaders: async ({}, use, testInfo) => {
    await use({ 'X-Forwarded-For': forwardedFor(testInfo) });
  },
  simWorker: [
    async ({}, use) => {
      const sim = await Sim.create();
      await use(sim);
      await sim.dispose();
    },
    { scope: 'worker' },
  ],
  sim: async ({ simWorker }, use) => {
    await use(simWorker);
  },
  pageProblems: async ({ page }, use) => {
    const problems = { pageErrors: [] as string[], consoleErrors: [] as string[] };
    page.on('pageerror', (e) => problems.pageErrors.push(`${e.name}: ${e.message}`));
    page.on('console', (m) => {
      if (m.type() === 'error') problems.consoleErrors.push(m.text());
    });
    await use(problems);
  },
});

export { expect };
