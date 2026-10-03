// Status indicator colours, state by state (TST-10, docs/REMEDIATION_PLAN.md §5.3).
//
// The screenshot comparison is a per-pixel colour threshold, which is a weak
// check for a thin, glowing 1 px pill border or a 6 px tile edge: the header
// pill changing from red to orange once passed `visual:test`. These tests read
// the computed colour of each status indicator in each of its states and
// compare it with the approved colour below, so a colour-only change fails
// here whatever the screenshots do. They read styles only, so they do not
// depend on rendering and cannot be flaky over pixels.
//
// Runs in every visual project (playwright.config.ts), as part of
// `npm run visual:test`. The tables below are approved look-and-feel
// (docs/ui/LOOK_AND_FEEL.md and the committed baselines): changing a status
// colour means changing it here too, in a reviewed change, like a baseline.
import { expect, test, mutateJson, failJson, openKiosk, openUi, preparePage, settle, THEMES, type ThemeName } from '../support/ui';
import type { Locator, Page } from '@playwright/test';

/** Secondary hue of each preset (LOOK_AND_FEEL §2.2): the standby colour is hsl(secondary, 85%, 55%). */
const SECONDARY_H: Record<ThemeName, number> = { 'tron-classic': 25, neon: 80, royal: 45, vaporwave: 330 };

/**
 * Main UI header pill (#header-title-text): border and text colour per state.
 * connected / disconnected use --color-success / --color-danger from style.css,
 * which override the derived theme tokens, so they do not follow the preset
 * (LOOK_AND_FEEL §9, raw colours); reconnecting (UI-03) is the preset's standby colour.
 */
const HEADER: Record<'connected' | 'reconnecting' | 'disconnected', (t: ThemeName) => string> = {
  connected: () => '#22c55e',
  reconnecting: (t) => `hsl(${SECONDARY_H[t]} 85% 55%)`,
  disconnected: () => '#ef4444',
};

/** Kiosk palette (web/kiosk.html :root; the kiosk ignores the theme presets, UI-34). */
const KIOSK = {
  dotConnected: '#22c55e',
  dotDisconnected: '#ef4444',
  // Input tile status bar (.kiosk-btn::before) per status class
  'status-signal': '#22c55e',
  'status-cable': '#f59e0b',
  'status-disconnected': '#ef4444',
  'status-unknown': '#64748b',
  active: '#ffffff',
  // Output footer tile border
  outputConnected: '#22c55e',
  outputDisconnected: 'transparent',
} as const;

/** How the browser serialises `css` as a computed colour (e.g. "rgb(34, 197, 94)"). */
async function resolve(page: Page, css: string): Promise<string> {
  return page.evaluate((c) => {
    const el = document.createElement('div');
    el.style.color = c;
    if (!el.style.color) throw new Error(`not a colour: ${c}`);
    document.body.appendChild(el);
    const out = getComputedStyle(el).color;
    el.remove();
    return out;
  }, css);
}

function computed(loc: Locator, prop: string, pseudo?: string): Promise<string> {
  return loc.evaluate((el, [p, ps]) => getComputedStyle(el, ps ?? null).getPropertyValue(p), [prop, pseudo] as const);
}

/** Wait until `prop` of `loc` (or its pseudo-element) is the approved colour. */
async function expectColour(loc: Locator, prop: string, css: string, what: string, pseudo?: string) {
  const want = await resolve(loc.page(), css);
  await expect.poll(() => computed(loc, prop, pseudo), { message: `${what}: ${prop} should be ${css} (${want})`, timeout: 5000 }).toBe(want);
}

test.beforeEach(async ({ sim }) => {
  await sim.reset();
});

for (const theme of Object.keys(THEMES) as ThemeName[]) {
  const tag = theme === 'tron-classic' ? '' : ' @themed';
  test(`status colours: header pill connected / reconnecting / disconnected [${theme}]${tag}`, async ({ page }) => {
    await preparePage(page, { theme });
    await openUi(page);
    const pill = page.locator('#header-title-text');
    const check = async (state: keyof typeof HEADER) => {
      await expect(pill).toHaveClass(new RegExp(`(^|\\s)${state}(\\s|$)`));
      for (const prop of ['border-top-color', 'color']) await expectColour(pill, prop, HEADER[state](theme), `header pill ${state} [${theme}]`);
    };

    await check('connected');
    // The hub reports the matrix unreachable while the WebSocket stays up.
    await page.evaluate(() => {
      const w = window as any; // eslint-disable-line @typescript-eslint/no-explicit-any
      w.state.setMatrixLink({ connected: false, state: 'disconnected' });
      w.app.updateConnectionStatus();
    });
    await check('disconnected');
    // The WebSocket drops and the client waits to retry (1 h), as after a hub restart.
    await page.evaluate(() => {
      const w = (window as any).app.ws; // eslint-disable-line @typescript-eslint/no-explicit-any
      w.reconnectDelay = 3_600_000;
      w.ws.close();
    });
    await check('reconnecting');
  });
}

test('status colours: kiosk connection dot connected / disconnected', async ({ page }) => {
  await preparePage(page);
  await openKiosk(page);
  const dot = page.locator('#statusDot');
  await expect(dot).toHaveClass(/(^|\s)connected(\s|$)/);
  await expectColour(dot, 'background-color', KIOSK.dotConnected, 'kiosk dot connected');

  const fresh = await page.context().newPage();
  await preparePage(fresh, { noWebSocket: true });
  await failJson(fresh, '**/api/status', 503, 'Matrix not connected');
  await openKiosk(fresh, { ready: false });
  await expect(fresh.locator('#statusText')).toHaveText('Disconnected');
  await expect(fresh.locator('#statusDot')).not.toHaveClass(/(^|\s)connected(\s|$)/);
  await expectColour(fresh.locator('#statusDot'), 'background-color', KIOSK.dotDisconnected, 'kiosk dot disconnected');
});

test('status colours: kiosk input tile status bars, every status', async ({ page }) => {
  // Inputs 1-2 signal, 3-4 cable but no signal, 5-6 unplugged, 7-8 unknown (no cable report).
  const want = ['status-signal', 'status-signal', 'status-cable', 'status-cable', 'status-disconnected', 'status-disconnected', 'status-unknown', 'status-unknown'] as const;
  await preparePage(page);
  await mutateJson(page, '**/api/status/inputs', (b) => {
    const inputs = ((b.data as { inputs?: Record<string, unknown>[] } | undefined)?.inputs ?? []) as Record<string, unknown>[];
    for (const p of inputs) {
      const s = want[Number(p.number) - 1];
      p.signalActive = s === 'status-signal';
      p.cableConnected = s === 'status-unknown' ? undefined : s !== 'status-disconnected';
    }
  });
  // No input carries every output, so no tile is "active" (its bar would be white).
  await mutateJson(page, '**/api/status', (b) => {
    const data = b.data as { routing?: Record<string, number> } | undefined;
    if (data) data.routing = Object.fromEntries([1, 2, 3, 4, 5, 6, 7, 8].map((o) => [String(o), o]));
  });
  await openKiosk(page);
  const tiles = page.locator('#kioskGrid .kiosk-btn');
  for (const [i, status] of want.entries()) {
    const tile = tiles.nth(i);
    await expect(tile, `input ${i + 1}`).toHaveClass(new RegExp(`(^|\\s)${status}(\\s|$)`));
    await expectColour(tile, 'background-color', KIOSK[status], `kiosk input ${i + 1} status bar (${status})`, '::before');
  }
});

test('status colours: kiosk active tile status bar', async ({ page }) => {
  await preparePage(page);
  await mutateJson(page, '**/api/status', (b) => {
    const data = b.data as { routing?: Record<string, number> } | undefined;
    if (data) data.routing = Object.fromEntries([1, 2, 3, 4, 5, 6, 7, 8].map((o) => [String(o), 2]));
  });
  await openKiosk(page);
  const tile = page.locator('#kioskGrid .kiosk-btn').nth(1);
  await expect(tile).toHaveClass(/(^|\s)active(\s|$)/);
  await expectColour(tile, 'background-color', KIOSK.active, 'kiosk active tile status bar', '::before');
});

test('status colours: kiosk output footer connected / disconnected', async ({ page }) => {
  await preparePage(page);
  await mutateJson(page, '**/api/status/outputs', (b) => {
    const outputs = ((b.data as { outputs?: Record<string, unknown>[] } | undefined)?.outputs ?? []) as Record<string, unknown>[];
    for (const p of outputs) {
      const on = Number(p.number) <= 4;
      p.connected = on;
      p.cableConnected = on;
    }
  });
  await openKiosk(page);
  await settle(page, 300);
  const tiles = page.locator('#outputStatusGrid .output-tile');
  await expect(tiles).toHaveCount(8);
  for (let i = 0; i < 8; i++) {
    const tile = tiles.nth(i);
    const on = i < 4;
    await expect(tile, `output ${i + 1}`).toHaveClass(new RegExp(`(^|\\s)${on ? 'connected' : 'disconnected'}(\\s|$)`));
    await expectColour(tile, 'border-top-color', on ? KIOSK.outputConnected : KIOSK.outputDisconnected, `kiosk output ${i + 1} border (${on ? 'connected' : 'disconnected'})`);
    await expect.poll(() => computed(tile, 'opacity'), { message: `kiosk output ${i + 1} opacity` }).toBe(on ? '1' : '0.4');
  }
});
