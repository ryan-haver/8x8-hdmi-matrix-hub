// UI functional flows against the simulator (WP-E1, docs/REMEDIATION_PLAN.md §4.7).
//
//   npm run test:e2e        (runs with the smoke project)
//
// One test (or a few) per register row fixed in WP-E1. Each drives the UI the
// way a user does and asserts the effect: the simulator state, the request the
// page sent, or what the page shows. Tests that change hub data (scenes,
// profiles) put it back afterwards through the hub API.
import { expect, openKiosk, openUi, preparePage, settle, test } from './support/ui';
import { hubApi } from './support/stack';
import type { Page } from '@playwright/test';

type Json = Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any

/** Answer the next window.prompt() with `value` (null = cancel) and return its message. */
function answerPrompt(page: Page, value: string | null): Promise<string> {
  return new Promise((resolve) => {
    page.once('dialog', async (dialog) => {
      const message = dialog.message();
      if (value === null) await dialog.dismiss();
      else await dialog.accept(value);
      resolve(message);
    });
  });
}

/** Text of every toast shown so far (the main UI's #toast-container). */
async function toasts(page: Page): Promise<string[]> {
  return page.locator('#toast-container .toast').evaluateAll((els) =>
    els.map((e) => `${[...e.classList].filter((c) => c !== 'toast').join(' ')}: ${e.querySelector('.toast-message')?.textContent ?? ''}`),
  );
}

async function openSettingsDrawer(page: Page, tab: 'profiles' | 'scenes' | 'system') {
  await page.evaluate((t) => {
    window.location.hash = `#settings/${t}`;
  }, tab);
  await page.locator('#settings-drawer.open').waitFor();
  await settle(page, 300);
}

async function mainTab(page: Page, name: 'matrix' | 'dashboard' | 'inputs' | 'outputs' | 'profiles') {
  await page.locator(`.tab-btn[data-tab="${name}"]:visible`).first().click();
  await settle(page, 400);
}

test.describe('WP-E1 UI flows', () => {
  test.afterEach(async ({ sim }) => {
    await sim.reset();
  });

  // ----- UI-01: passcode flow ------------------------------------------------

  test('UI-01: running a protected profile from the Settings drawer asks for the passcode and applies it', async ({
    page,
    sim,
    pageProblems,
  }) => {
    await preparePage(page);
    await openUi(page);
    await openSettingsDrawer(page, 'profiles');
    const prompt = answerPrompt(page, '1234');
    const recall = page.waitForResponse((r) => r.url().endsWith('/api/profile/kids_gaming/recall') && r.request().postData()?.includes('1234') === true);
    await page.locator('#settings-drawer .execute-profile-btn[data-id="kids_gaming"]').click();
    expect(await prompt).toMatch(/passcode/i);
    expect((await recall).status()).toBe(200);
    // kids_gaming routes input 6 to output 1.
    await expect.poll(async () => (await sim.state()).outputs[0].source).toBe(6);
    await expect.poll(() => toasts(page)).toContainEqual(expect.stringMatching(/^success: .*Kids Gaming|^success: Profile/));
    expect(pageProblems.pageErrors).toEqual([]);
  });

  test('UI-01: a wrong passcode is reported and changes nothing', async ({ page, sim }) => {
    await preparePage(page);
    await openUi(page);
    await openSettingsDrawer(page, 'profiles');
    const prompt = answerPrompt(page, '9999');
    const recall = page.waitForResponse((r) => r.url().endsWith('/api/profile/kids_gaming/recall') && !!r.request().postData()?.includes('9999'));
    await page.locator('#settings-drawer .execute-profile-btn[data-id="kids_gaming"]').click();
    await prompt;
    expect((await recall).status()).toBe(403);
    await expect.poll(() => toasts(page)).toContainEqual(expect.stringMatching(/^error: .*(invalid|wrong).*passcode/i));
    expect((await sim.state()).outputs[0].source).toBe(2);
  });

  test('UI-01: cancelling the passcode prompt sends nothing', async ({ page, sim }) => {
    await preparePage(page);
    await openUi(page);
    await openSettingsDrawer(page, 'profiles');
    const recalls: string[] = [];
    page.on('request', (r) => {
      if (r.url().endsWith('/api/profile/kids_gaming/recall')) recalls.push(r.postData() ?? '');
    });
    const prompt = answerPrompt(page, null);
    await page.locator('#settings-drawer .execute-profile-btn[data-id="kids_gaming"]').click();
    await prompt;
    await settle(page, 500);
    // Only the first attempt (no passcode) went out.
    expect(recalls.length).toBe(1);
    expect((await sim.state()).outputs[0].source).toBe(2);
  });

  test('UI-01: a protected scene card on the dashboard asks for the passcode and runs the scene', async ({ page, sim }) => {
    await preparePage(page);
    await openUi(page);
    await mainTab(page, 'dashboard');
    const card = page.locator('#dashboard-cards-grid .dashboard-card-action[data-type="scene"][data-id="scene_kidslocked"]');
    await expect(card).toBeVisible();
    const prompt = answerPrompt(page, '1234');
    const run = page.waitForResponse((r) => r.url().endsWith('/api/v2/scenes/scene_kidslocked/execute') && !!r.request().postData()?.includes('1234'));
    await card.click();
    expect(await prompt).toMatch(/passcode/i);
    expect((await run).status()).toBe(200);
    // scene_kidslocked: profile kids_gaming (input 6 -> output 1), then route input 6 to output 1.
    await expect.poll(async () => (await sim.state()).outputs[0].source).toBe(6);
  });

  test('UI-01: a protected profile card on the dashboard asks for the passcode', async ({ page, sim }) => {
    await preparePage(page);
    // The seeded layout has a card for movie_night only; show kids_gaming's card instead.
    await page.route('**/api/dashboard/layout', async (route) => {
      const response = await route.fetch();
      const body = (await response.json()) as Json;
      body.data.cards = [{ type: 'profile', id: 'kids_gaming', order: 0 }];
      await route.fulfill({ response, json: body });
    });
    await openUi(page);
    await mainTab(page, 'dashboard');
    const card = page.locator('#dashboard-cards-grid .dashboard-card-action[data-type="profile"][data-id="kids_gaming"]');
    await expect(card).toBeVisible();
    const prompt = answerPrompt(page, '1234');
    await card.click();
    expect(await prompt).toMatch(/passcode/i);
    await expect.poll(async () => (await sim.state()).outputs[0].source).toBe(6);
  });

  test('UI-04: API requests time out instead of hanging forever', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    await page.route('**/api/info', () => {
      /* never answered */
    });
    const result = await page.evaluate(async () => {
      const t0 = Date.now();
      try {
        await (window as any).api.get('/api/info', { timeout: 500 }); // eslint-disable-line @typescript-eslint/no-explicit-any
        return { ok: true, ms: performance.now() };
      } catch (e: any) { // eslint-disable-line @typescript-eslint/no-explicit-any
        return { ok: false, name: e.name, status: e.status, code: e.code, ms: Date.now() - t0 };
      }
    });
    expect(result).toMatchObject({ ok: false, name: 'ApiError', status: 0, code: 'timeout' });
  });

  test('UI-01: API errors carry the HTTP status and the hub error code', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    const err = await page.evaluate(async () => {
      try {
        await (window as any).api.recallProfile('kids_gaming'); // eslint-disable-line @typescript-eslint/no-explicit-any
        return null;
      } catch (e: any) { // eslint-disable-line @typescript-eslint/no-explicit-any
        return { name: e.name, status: e.status, code: e.code };
      }
    });
    expect(err).toEqual({ name: 'ApiError', status: 403, code: 'passcode_required' });
  });

  // ----- VAL-11: partial runs --------------------------------------------------

  test('VAL-11: a scene that ran only partly is reported as a partial run, not silently', async ({ page, sim }, info) => {
    const hub = await hubApi(`10.250.${info.workerIndex % 250}.9`);
    const original = (await (await hub.get('/api/v2/scenes/scene_goodnight01')).json()).data.scene;
    // Same setup as the validation scenario scenes.partial_failure: step 2 names a profile that does not exist.
    const edited = await hub.put('/api/v2/scenes/scene_goodnight01', {
      data: { steps: [{ type: 'system_action', id: 'mute_all_audio' }, { type: 'profile', id: 'no_such_profile' }] },
    });
    expect(edited.ok(), await edited.text()).toBeTruthy();
    try {
      await preparePage(page);
      await openUi(page);
      await openSettingsDrawer(page, 'scenes');
      const run = page.waitForResponse((r) => r.url().endsWith('/api/v2/scenes/scene_goodnight01/execute'));
      await page.locator('#settings-drawer .execute-scene-btn[data-id="scene_goodnight01"]').click();
      expect((await run).status()).toBe(207);
      await expect.poll(() => toasts(page)).toContainEqual(expect.stringMatching(/^warning: .*1 of 2/));
      expect(await toasts(page)).not.toContainEqual(expect.stringMatching(/^success:/));
      await expect.poll(async () => (await sim.state()).outputs[0].audio_mute).toBe(1);
    } finally {
      await hub.put('/api/v2/scenes/scene_goodnight01', { data: { steps: original.steps } });
      await hub.dispose();
    }
  });

  test('VAL-11: a profile recall that applied only some outputs is reported as partial', async ({ page }) => {
    await preparePage(page);
    // The hub's 207 body for a partly applied recall (rest_api/profiles.py handle_recall_profile).
    await page.route('**/api/profile/game_day/recall', (route) =>
      route.fulfill({
        status: 207,
        contentType: 'application/json',
        json: {
          success: false,
          data: {
            profile: 'Game Day',
            applied: ['Output 1 → Input 5', 'Output 2 → Input 5'],
            failed_outputs: [3],
            errors: ['Output 3: mute not applied'],
            power_on_macro: null,
          },
          error: 'Output 3: mute not applied',
        },
      }),
    );
    await openUi(page);
    await openSettingsDrawer(page, 'profiles');
    await page.locator('#settings-drawer .execute-profile-btn[data-id="game_day"]').click();
    await expect.poll(() => toasts(page)).toContainEqual(expect.stringMatching(/^warning: .*Output 3/));
    expect(await toasts(page)).not.toContainEqual(expect.stringMatching(/^success:/));
  });

  // ----- UI-27: profiles and dashboard load -------------------------------------

  test('UI-27: the Profiles tab lists the hub profiles and recalls one', async ({ page, sim }) => {
    await preparePage(page);
    await openUi(page);
    await mainTab(page, 'profiles');
    // Pinned profiles from tests/e2e/fixtures/data/profiles.json (Retro Hour is unpinned).
    await expect(page.locator('#scenes-list .scene-card .scene-name')).toHaveText(['Movie Night', 'Game Day', 'Kids Gaming']);
    await page.locator('#scenes-list .recall-scene-btn[data-scene-id="game_day"]').click();
    await expect.poll(async () => (await sim.state()).outputs.slice(0, 3).map((o) => o.source)).toEqual([5, 5, 5]);
  });

  test('UI-27: the app loads profiles and CEC macros, so the dashboard shows their cards on load', async ({ page }) => {
    await preparePage(page);
    await openUi(page); // delays /api/dashboard/layout by 400 ms (tests/e2e/support/ui.ts)
    const loaded = await page.evaluate(() => {
      const s = (window as any).state; // eslint-disable-line @typescript-eslint/no-explicit-any
      return { profiles: s.profiles.map((p: Json) => p.id), macros: s.cecMacros.map((m: Json) => m.id) };
    });
    expect(loaded.profiles).toEqual(expect.arrayContaining(['movie_night', 'game_day', 'kids_gaming', 'retro_hour']));
    expect(loaded.macros).toEqual(expect.arrayContaining(['macro_tv_on']));
    await mainTab(page, 'dashboard');
    for (const key of ['scene:scene_movienight01', 'preset:2', 'system_shortcut:builtin.mute_all_audio', 'profile:movie_night', 'macro:macro_tv_on']) {
      await expect(page.locator(`#dashboard-cards-grid .dashboard-card[data-card-key="${key}"]`)).toBeVisible();
    }
  });

  // ----- UI-26: scene editor ----------------------------------------------------

  test('UI-26: the scene editor saves a new scene', async ({ page }, info) => {
    await preparePage(page);
    await openUi(page);
    await openSettingsDrawer(page, 'scenes');
    await page.locator('#settings-drawer .create-scene-btn').first().click();
    await page.locator('#scene-editor-modal.open').waitFor();
    await page.locator('#scene-editor-body input[type="text"]').first().fill('E2E Test Scene');
    const created = page.waitForResponse((r) => r.url().endsWith('/api/v2/scenes') && r.request().method() === 'POST');
    await page.locator('#scene-editor-save').click();
    const res = await created;
    const body = (await res.json()) as Json;
    const hub = await hubApi(`10.250.${info.workerIndex % 250}.10`);
    try {
      expect(res.status(), JSON.stringify(body)).toBe(201);
      expect(body.data.scene.name).toBe('E2E Test Scene');
      expect(await toasts(page)).not.toContainEqual(expect.stringMatching(/name is required/));
    } finally {
      if (body?.data?.scene?.id) await hub.delete(`/api/v2/scenes/${body.data.scene.id}`);
      await hub.dispose();
    }
  });

  // ----- UI-28: runtime errors ---------------------------------------------------

  test('UI-28: moving the pointer, the CEC tray FAB and the API button throw no errors; the API button opens on the first click', async ({
    page,
    pageProblems,
  }) => {
    await preparePage(page);
    await openUi(page);
    await page.mouse.move(10, 10);
    await page.mouse.move(700, 400);
    await page.locator('.cec-tray-fab').first().click();
    await settle(page, 400);
    await page.keyboard.press('Escape');
    await mainTab(page, 'profiles');
    await page.locator('#scenes-list .api-copy-btn').first().click();
    await expect(page.locator('#api-copy-modal')).toHaveClass(/open/);
    expect(pageProblems.pageErrors).toEqual([]);
  });

  // ----- UI-17: CEC tray listener leak -----------------------------------------

  test('UI-17: picking a CEC tray target does not leave a document click listener behind', async ({ page }) => {
    await preparePage(page);
    await page.addInitScript(() => {
      const w = window as any; // eslint-disable-line @typescript-eslint/no-explicit-any
      w.__docClickListeners = 0;
      const add = document.addEventListener.bind(document);
      const remove = document.removeEventListener.bind(document);
      document.addEventListener = ((type: string, fn: any, opts?: any) => { // eslint-disable-line @typescript-eslint/no-explicit-any
        if (type === 'click') w.__docClickListeners++;
        return add(type, fn, opts);
      }) as typeof document.addEventListener;
      document.removeEventListener = ((type: string, fn: any, opts?: any) => { // eslint-disable-line @typescript-eslint/no-explicit-any
        if (type === 'click') w.__docClickListeners--;
        return remove(type, fn, opts);
      }) as typeof document.removeEventListener;
    });
    await openUi(page);
    await page.locator('.cec-tray-fab').first().click();
    await settle(page, 300);
    const before = await page.evaluate(() => (window as any).__docClickListeners); // eslint-disable-line @typescript-eslint/no-explicit-any
    for (let i = 0; i < 3; i++) {
      await page.locator('#cec-tray [data-target="navigation"]').first().click();
      await page.locator('.cec-target-selector').waitFor();
      await settle(page, 50);
      await page.locator('.cec-target-selector .target-option[data-type="auto"]').click();
      await expect(page.locator('.cec-target-selector')).toHaveCount(0);
      await settle(page, 50);
    }
    const after = await page.evaluate(() => (window as any).__docClickListeners); // eslint-disable-line @typescript-eslint/no-explicit-any
    expect(after).toBe(before);
  });

  // ----- UI-30: modals and drawers ------------------------------------------------

  test('UI-30: opening the Settings drawer on the Scenes or System tab highlights that tab', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    for (const tabName of ['scenes', 'system', 'profiles'] as const) {
      await page.evaluate((t) => (window as any).settingsDrawer.open(t), tabName); // eslint-disable-line @typescript-eslint/no-explicit-any
      await expect(page.locator('#settings-drawer .drawer-tab-btn.active')).toHaveAttribute('data-tab', tabName);
    }
  });

  test('UI-30: the Hardware drawer shows the device values', async ({ page, sim }) => {
    await sim.patch({ system: { lcd_timeout: 2, beep: 0 }, ext_audio: { mode: 1 } });
    await preparePage(page);
    await openUi(page);
    await page.locator('#menu-toggle').click();
    await page.locator('#side-nav-drawer.open').waitFor();
    await page.locator('#drawer-hardware-btn').click();
    await page.locator('#hardware-drawer.open').waitFor();
    await expect(page.locator('#hardware-lcd-timeout')).toHaveValue('2');
    await expect(page.locator('#hardware-beep-enabled')).not.toBeChecked();
    await expect(page.locator('#hardware-ext-audio-mode')).toHaveValue('1');
  });

  test('UI-30/UI-43: the profile CEC dialog opens visible, unobstructed and with the profile CEC targets', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    // No button calls it (UI-45): open it the way the app would (ScenesPanel.openCecConfig).
    await page.evaluate(() => (window as any).app.components.scenesPanel.openCecConfig('movie_night')); // eslint-disable-line @typescript-eslint/no-explicit-any
    const modal = page.locator('#scene-cec-modal');
    await expect(modal).toBeVisible();
    await expect(page.locator('#cec-scene-name')).toHaveText('Movie Night');
    // movie_night's stored CEC config (tests/e2e/fixtures/data/profiles.json) is shown, not the empty default.
    await expect(page.locator('#scene-cec-modal .target-chip')).not.toHaveCount(0);
    // Nothing covers the dialog: the title and the Save button are the topmost elements where they are drawn.
    for (const sel of ['#scene-cec-modal .settings-modal-header h3, #scene-cec-modal h3', '#cec-save-btn']) {
      await page.locator(sel).first().scrollIntoViewIfNeeded();
      const covered = await page.locator(sel).first().evaluate((el) => {
        const r = el.getBoundingClientRect();
        const top = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
        return !(top && (el === top || el.contains(top)));
      });
      expect(covered, `${sel} is covered`).toBe(false);
    }
  });

  test('API-25 (read side): the CEC dialog labels targets stored as "input:2" and as "input_2"', async ({ page }) => {
    await preparePage(page);
    // movie_night stores the colon form (tests/e2e/fixtures/data/profiles.json); make one category use the
    // underscore form the resolver writes, so both are on screen.
    await page.route('**/api/profile/movie_night/cec', async (route) => {
      if (route.request().method() !== 'GET') return route.fallback();
      const response = await route.fetch();
      const b = (await response.json()) as Json;
      b.data.cec_config.playback_targets = ['input_2'];
      await route.fulfill({ response, json: b });
    });
    await openUi(page);
    await page.evaluate(() => (window as any).app.components.scenesPanel.openCecConfig('movie_night')); // eslint-disable-line @typescript-eslint/no-explicit-any
    await expect(page.locator('#scene-cec-modal')).toBeVisible();
    const chips = (cat: string) => page.locator(`#targets-${cat} .target-chip .chip-label`);
    // Seed names: input 2 AppleTV, output 1 TV, output 2 Soundbar.
    await expect(chips('navigation')).toHaveText(['Input 2 · AppleTV']);
    await expect(chips('playback')).toHaveText(['Input 2 · AppleTV']);
    await expect(chips('volume')).toHaveText(['Output 2 · Soundbar']);
    await expect(chips('power_on')).toHaveText(['Input 2 · AppleTV', 'Output 1 · TV']);
    await expect(page.locator('#scene-cec-modal .target-chip.input-target')).toHaveCount(4);
    await expect(page.locator('#scene-cec-modal')).not.toContainText('NaN');
  });

  // ----- UI-27: dashboard cards look and order ----------------------------------------

  test('UI-27: dashboard cards render as styled cards in a panel after the pinned widgets', async ({ page }) => {
    await preparePage(page, {
      storage: {
        orei_dashboard_config: JSON.stringify({
          pinnedWidgets: ['routing-dashboard', 'cec-remote'],
          hiddenMobileWidgets: [],
          widgetOrder: ['routing-dashboard', 'cec-remote'],
        }),
      },
    });
    await openUi(page);
    await mainTab(page, 'dashboard');
    await expect(page.locator('#dashboard-cards-grid .dashboard-card')).not.toHaveCount(0);
    // The pinned widgets keep their stored order; the cards panel comes after them, also when a widget
    // is rendered after the cards (the CEC tray registers its widget late; re-pinning renders it again).
    const order = () =>
      page.locator('#dashboard-widgets > *').evaluateAll((els) =>
        els.map((e) => (e as HTMLElement).dataset.widgetId ?? (e.classList.contains('dashboard-cards-container') ? 'cards' : e.className)),
      );
    expect(await order()).toEqual(['routing-dashboard', 'cec-remote', 'cards']);
    await page.evaluate(() => {
      const dm = (window as any).dashboardManager; // eslint-disable-line @typescript-eslint/no-explicit-any
      dm.unpinWidget('cec-remote');
      dm.pinWidget('cec-remote');
    });
    expect(await order()).toEqual(['routing-dashboard', 'cec-remote', 'cards']);
    // Panel and cards are drawn with the card surface (LOOK_AND_FEEL §3), not as bare text.
    const look = (sel: string) =>
      page.locator(sel).first().evaluate((el) => {
        const cs = getComputedStyle(el);
        return { bg: cs.backgroundColor, radius: parseFloat(cs.borderTopLeftRadius), border: parseFloat(cs.borderTopWidth) };
      });
    for (const sel of ['.dashboard-cards-container', '#dashboard-cards-grid .dashboard-card']) {
      const s = await look(sel);
      expect(s.bg, `${sel} background`).not.toBe('rgba(0, 0, 0, 0)');
      expect(s.radius, `${sel} radius`).toBeGreaterThanOrEqual(8);
      expect(s.border, `${sel} border`).toBeGreaterThanOrEqual(1);
    }
    // The action button sits inside its card, right-aligned (not loose under the title).
    const card = page.locator('#dashboard-cards-grid .dashboard-card[data-card-key="scene:scene_movienight01"]');
    const [cardBox, actionBox] = await Promise.all([card.boundingBox(), card.locator('.dashboard-card-action').boundingBox()]);
    expect(actionBox!.y).toBeGreaterThanOrEqual(cardBox!.y);
    expect(actionBox!.y + actionBox!.height).toBeLessThanOrEqual(cardBox!.y + cardBox!.height);
    expect(actionBox!.x + actionBox!.width).toBeGreaterThan(cardBox!.x + cardBox!.width - 80);
  });

  // ----- after WP-C2: UI-03 / UI-29 / UI-04 / UI-30 / kiosk polling ---------------------

  test('UI-03/UI-29: the header shows a distinct "reconnecting" state while the WebSocket retries', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    const header = page.locator('#header-title-text');
    await expect(header).toHaveClass(/connected/);
    const colour = () => header.evaluate((el) => getComputedStyle(el).borderTopColor);
    const connectedColour = await colour();
    // Drop the hub socket and keep the client in its retry wait (1 h).
    await page.evaluate(() => {
      const w = (window as any).app.ws; // eslint-disable-line @typescript-eslint/no-explicit-any
      w.reconnectDelay = 3_600_000;
      w.ws.close();
    });
    await expect(header).toHaveClass(/reconnecting/);
    await expect(header).not.toHaveClass(/(^|\s)(connected|disconnected)(\s|$)/);
    await expect(header).toHaveAttribute('title', /reconnecting/i);
    const reconnectingColour = await colour();
    // The disconnected look (matrix not reachable), for comparison.
    await page.evaluate(() => (window as any).state.setMatrixLink?.({ connected: false, state: 'disconnected' })); // eslint-disable-line @typescript-eslint/no-explicit-any
    await page.evaluate(() => {
      const w = (window as any).app.ws; // eslint-disable-line @typescript-eslint/no-explicit-any
      w.status = 'disconnected';
      (window as any).app.updateConnectionStatus(); // eslint-disable-line @typescript-eslint/no-explicit-any
    });
    await expect(header).toHaveClass(/disconnected/);
    const disconnectedColour = await colour();
    expect(new Set([connectedColour, reconnectingColour, disconnectedColour]).size, JSON.stringify({ connectedColour, reconnectingColour, disconnectedColour })).toBe(3);
  });

  test('UI-29: the grid shows "Loading matrix" until the first status, never a made-up routing', async ({ page }) => {
    await preparePage(page, { storage: { 'matrix-view-mode': 'grid' } }); // WebSocket status snapshots are dropped
    let release: () => void = () => {};
    const held = new Promise<void>((r) => (release = r));
    await page.route('**/api/status', async (route) => {
      await held;
      await route.fallback();
    });
    await page.goto('/ui');
    await page.waitForFunction(() => !!(window as any).app); // eslint-disable-line @typescript-eslint/no-explicit-any
    await settle(page, 1500);
    await expect(page.locator('#matrix-grid .matrix-loading')).toContainText('Loading matrix');
    await expect(page.locator('#matrix-grid .matrix-route')).toHaveCount(0);
    release();
    await expect(page.locator('#matrix-grid .matrix-route')).toHaveCount(64);
    await expect(page.locator('#matrix-grid .matrix-route[data-input="2"][data-output="1"]')).toHaveClass(/active/);
  });

  test('UI-29: when the matrix is unreachable the grid says so instead of a made-up routing', async ({ page }) => {
    await preparePage(page, { storage: { 'matrix-view-mode': 'grid' } });
    await page.route('**/api/status', (route) =>
      route.fulfill({ status: 503, contentType: 'application/json', json: { success: false, data: null, error: 'Matrix not connected' } }),
    );
    await openUi(page, { ready: false });
    await page.waitForFunction(() => (window as any).state?.ui?.dataLoaded === true, undefined, { timeout: 20_000 }); // eslint-disable-line @typescript-eslint/no-explicit-any
    await expect(page.locator('#matrix-grid')).toContainText('Matrix not reachable');
    await expect(page.locator('#matrix-grid .matrix-route')).toHaveCount(0);
  });

  test('UI-04: a preset recall shows one toast on the page that recalled it and none on other pages', async ({ page, sim, browser }, info) => {
    await preparePage(page, { storage: { 'matrix-view-mode': 'grid' } });
    await openUi(page);
    // Another client recalls preset 3 (PS5 everywhere) through the hub.
    const hub = await hubApi(`10.250.${info.workerIndex % 250}.11`);
    try {
      expect((await hub.post('/api/preset/3')).ok()).toBeTruthy();
    } finally {
      await hub.dispose();
    }
    await expect(page.locator('#matrix-grid .matrix-route[data-input="6"][data-output="1"]')).toHaveClass(/active/, { timeout: 15_000 });
    await settle(page, 800);
    expect(await toasts(page)).toEqual([]);
    // This page recalls preset 2 from the Presets drawer: its own toast only.
    await page.locator('#menu-toggle').click();
    await page.locator('#side-nav-drawer.open').waitFor();
    await page.locator('#drawer-presets-btn').click();
    await page.locator('#presets-drawer.open').waitFor();
    await page.locator('#presets-drawer .preset-row[data-preset-number="2"] .preset-expand-btn').click();
    await page.locator('#presets-drawer .btn-recall-preset[data-preset="2"]').click();
    await expect.poll(async () => (await sim.state()).outputs[0].source).toBe(5);
    await settle(page, 1500);
    expect(await toasts(page)).toEqual(['success: Preset 2 recalled']);
    void browser;
  });

  test('UI-30: the About dialog shows the WebSocket and matrix link from the app state', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    await page.evaluate(() => (window as any).AboutDialog.show()); // eslint-disable-line @typescript-eslint/no-explicit-any
    await page.locator('.about-dialog.about-dialog--visible').waitFor();
    await expect(page.locator('#status-websocket')).toHaveText('Connected');
    await expect(page.locator('#status-matrix')).toHaveText('Connected');
    // The model row shows the matrix's model (/api/info, as in the header), not a generic name.
    const model = await page.evaluate(() => (window as any).state.info.model); // eslint-disable-line @typescript-eslint/no-explicit-any
    expect(model).toBeTruthy();
    await expect(page.locator('#status-model')).toHaveText(model);
  });

  test('UI-24: the kiosk stays live from the WebSocket and does not poll the status routes', async ({ page, sim }) => {
    await preparePage(page);
    await openKiosk(page);
    const reads: string[] = [];
    page.on('request', (r) => {
      const p = new URL(r.url()).pathname;
      if (r.method() === 'GET' && /^\/api\/status(\/|$)/.test(p)) reads.push(p);
    });
    // A change behind the hub's back reaches the kiosk through the hub's event stream.
    await sim.patch({ outputs: { '2': { source: 4 } } });
    await expect(page.locator('#outputStatusGrid .output-tile').nth(2).locator('.output-tile-input')).toHaveText('4', { timeout: 15_000 });
    await page.waitForTimeout(6000);
    expect(reads).toEqual([]);
  });

  // ----- UI-50 / UI-49: card polish, Settings drawer lists ----------------------------

  test('UI-50: the Dashboard Cards header is one line and a locked card shows one small lock', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    await mainTab(page, 'dashboard');
    await expect(page.locator('#dashboard-cards-grid .dashboard-card')).not.toHaveCount(0);
    // The title is one line, like the other widget headers, and the header is no taller than a widget header
    // plus the height difference of its button (28 px add button vs the 22 px unpin button).
    const header = await page.evaluate(() => {
      const title = document.querySelector('.dashboard-cards-container .dashboard-widget-title span')!;
      const range = document.createRange();
      range.selectNodeContents(title);
      const h = (sel: string) => document.querySelector(sel)!.getBoundingClientRect().height;
      return {
        titleLines: new Set([...range.getClientRects()].map((r) => Math.round(r.top))).size,
        cards: h('.dashboard-cards-container .dashboard-widget-header'),
        routing: h('.dashboard-widget[data-widget-id="routing-dashboard"] .dashboard-widget-header'),
      };
    });
    expect(header.titleLines, JSON.stringify(header)).toBe(1);
    expect(header.cards - header.routing, JSON.stringify(header)).toBeLessThanOrEqual(6);
    // The protected scene: exactly one lock indicator, text-sized and centred.
    const card = page.locator('#dashboard-cards-grid .dashboard-card[data-card-key="scene:scene_kidslocked"]');
    const info = await card.evaluate((el) => {
      const name = el.querySelector('.dashboard-card-title') as HTMLElement;
      const locks = [...el.querySelectorAll('svg')].filter((s) => !s.closest('.dashboard-card-unpin'));
      const lockText = (el.querySelector('.dashboard-card-icon')?.textContent ?? '') + name.textContent;
      const r = locks[0]?.getBoundingClientRect();
      const slot = locks[0]?.parentElement?.getBoundingClientRect();
      return {
        svgLocks: locks.length,
        emojiLocks: (lockText.match(/🔒|🔐/g) ?? []).length,
        size: r ? Math.max(r.width, r.height) : 0,
        offCentre: r && slot ? Math.abs(r.top + r.height / 2 - (slot.top + slot.height / 2)) : 99,
      };
    });
    expect(info.svgLocks + info.emojiLocks, JSON.stringify(info)).toBe(1);
    expect(info.size).toBeLessThanOrEqual(20);
    expect(info.offCentre).toBeLessThanOrEqual(2);
  });

  test('UI-50: the kiosk PIN pad digits and delete key are large enough to read', async ({ page }) => {
    await preparePage(page);
    await openKiosk(page);
    await page.locator('.kiosk-tab-btn[data-tab="profiles"]').click();
    await settle(page, 300);
    await page.locator('#profilesGrid .kiosk-btn', { hasText: 'Kids Gaming' }).click();
    await page.locator('#passcodeModal.show').waitFor();
    await page.locator('#passcodeModal [data-digit="1"]').click();
    const sizes = await page.evaluate(() => ({
      dots: parseFloat(getComputedStyle(document.getElementById('passcodeDisplay')!).fontSize),
      back: parseFloat(getComputedStyle(document.querySelector('#passcodePad [data-pin-action="back"]')!).fontSize),
      digit: parseFloat(getComputedStyle(document.querySelector('#passcodePad [data-digit="1"]')!).fontSize),
    }));
    expect(sizes.dots, JSON.stringify(sizes)).toBeGreaterThanOrEqual(28);
    expect(sizes.back, JSON.stringify(sizes)).toBeGreaterThanOrEqual(22);
    await page.locator('#passcodeCancelBtn').click();
  });

  test('UI-49: Settings drawer items are one card row: name and meta left, actions right', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    for (const t of ['profiles', 'scenes', 'system'] as const) {
      await openSettingsDrawer(page, t);
      const rows = await page.locator('#settings-drawer .settings-list-item').evaluateAll((items) =>
        items.map((el) => {
          const name = el.querySelector('.item-name')!.getBoundingClientRect();
          const buttons = [...el.querySelectorAll('.item-actions button')].map((b) => b.getBoundingClientRect());
          const cs = getComputedStyle(el);
          const centre = (r: DOMRect) => r.top + r.height / 2;
          return {
            name: el.querySelector('.item-name')!.textContent,
            oneRow: buttons.every((b) => Math.abs(centre(b) - centre(name)) <= 12 && b.left > name.right),
            surface: cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && parseFloat(cs.borderTopLeftRadius) >= 8,
          };
        }),
      );
      expect(rows.length, t).toBeGreaterThan(0);
      for (const r of rows) expect(r, `${t}: ${r.name}`).toMatchObject({ oneRow: true, surface: true });
    }
  });

  // ----- UI-31: theme presets ------------------------------------------------------

  test('UI-31: each theme preset has its own edit button', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    await page.locator('#menu-toggle').click();
    await page.locator('#side-nav-drawer.open').waitFor();
    await page.locator('#drawer-theme-btn').click();
    await page.locator('.theme-drawer[aria-hidden="false"]').waitFor();
    await expect(page.locator('.theme-preset-grid > *')).toHaveCount(4);
    for (let i = 0; i < 4; i++) {
      await expect(page.locator(`.theme-preset-slot[data-preset-index="${i}"] .preset-edit-btn[data-edit-index="${i}"]`)).toHaveCount(1);
    }
    const slot = page.locator('.theme-preset-slot[data-preset-index="0"]');
    await slot.hover();
    await slot.locator('.preset-edit-btn').click();
    await expect(page.locator('#color-customization')).not.toHaveClass(/hidden/);
    await expect(page.locator('.preset-name-input')).toHaveValue('Tron Classic');
  });

  // ----- UI-37: display CEC keys ------------------------------------------------------

  test('UI-37: the CEC remote for a display offers only the keys a display supports', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    await mainTab(page, 'outputs');
    await page.locator('#outputs-list .io-card[data-output="1"] .cec-btn').click();
    const dd = page.locator('.cec-dropdown');
    await dd.waitFor();
    const cmds = await dd.locator('.cec-cmd-btn').evaluateAll((els) => els.map((e) => (e as HTMLElement).dataset.cmd));
    // GET /api/cec/output/{n}/capabilities: power_on, power_off, mute, volume_down, volume_up (+ active).
    expect(cmds.sort()).toEqual(['mute', 'power_off', 'power_on', 'volume_down', 'volume_up']);
    await page.keyboard.press('Escape');
    await page.mouse.click(5, 5);
    await mainTab(page, 'inputs');
    await page.locator('#inputs-list .io-card[data-input="2"] .cec-btn').click();
    await expect(page.locator('.cec-dropdown .cec-cmd-btn[data-cmd="up"]')).toBeVisible();
  });

  test('UI-37: the kiosk CEC remote hides the D-pad for the display', async ({ page }) => {
    await preparePage(page);
    await openKiosk(page);
    await page.locator('#outputStatusGrid .output-tile').nth(0).click();
    await page.locator('#cecRemoteModal.show').waitFor();
    await expect(page.locator('#cecRemoteModal [data-cmd="up"]')).toBeVisible();
    await page.locator('#btnTargetDisplay').click();
    await expect(page.locator('#cecRemoteModal [data-cmd="up"]')).toBeHidden();
    await expect(page.locator('#cecRemoteModal [data-cmd="menu"]')).toBeHidden();
    await expect(page.locator('#cecRemoteModal [data-cmd="volume_up"]')).toBeVisible();
  });

  // ----- UI-23..25: kiosk -----------------------------------------------------------

  /** Output setting requests (HDCP/HDR/scaler/ARC/mute) the kiosk sends. */
  function outputSettingRequests(page: Page) {
    const sent: Array<{ path: string; status: number; body: string | null }> = [];
    page.on('response', (r) => {
      const p = new URL(r.url()).pathname;
      if (/\/api\/output\/\d\/(hdcp|hdr|scaler|arc|mute)$/.test(p)) sent.push({ path: p, status: r.status(), body: r.request().postData() });
    });
    return sent;
  }

  /** Every output field except the routing, to prove "nothing else changed". */
  const settingsOf = (outputs: Array<Record<string, unknown>>) => outputs.map(({ source: _source, ...rest }) => rest); // eslint-disable-line @typescript-eslint/no-unused-vars

  test('UI-46: kiosk route-all with untouched options changes only the routing (the soundbar keeps its scaler)', async ({
    page,
    sim,
  }) => {
    await sim.patch({ outputs: { '0': { audio_mute: 1 }, '1': { arc: 1 } } });
    const before = (await sim.state()).outputs;
    expect(before[1].scaler).toBe(4); // seed: output 2 is the audio-only soundbar
    await preparePage(page);
    await openKiosk(page);
    const sent = outputSettingRequests(page);
    await page.locator('#kioskGrid .kiosk-btn').nth(4).click();
    await page.locator('#routeToAllBtn').click();
    await page.locator('#toggleAdvancedRouting').click(); // looking is not changing
    await page.locator('#routingApplyBtn').click();
    await expect.poll(async () => (await sim.state()).outputs.map((o) => o.source), { timeout: 10_000 }).toEqual([5, 5, 5, 5, 5, 5, 5, 5]);
    await settle(page, 1500);
    expect(sent, 'output settings sent').toEqual([]);
    expect(settingsOf((await sim.state()).outputs)).toEqual(settingsOf(before));
  });

  test('UI-23/UI-46: kiosk sends only the options the user changed, with the values the hub reads', async ({ page, sim }) => {
    const before = (await sim.state()).outputs;
    await preparePage(page);
    await openKiosk(page);
    const sent = outputSettingRequests(page);
    await page.locator('#kioskGrid .kiosk-btn').nth(2).click();
    await page.locator('#wizardOutputsList .wizard-option-btn[data-output="3"]').click();
    await page.locator('#routingMuteAudio').check();
    await page.locator('#toggleAdvancedRouting').click();
    await page.locator('#routingHdrMode').selectOption({ label: 'SDR' });
    await page.locator('#routingApplyBtn').click();
    await expect.poll(async () => (await sim.state()).outputs[2].source, { timeout: 10_000 }).toBe(3);
    await expect.poll(() => sent.length, { timeout: 10_000 }).toBe(2);
    await settle(page, 1000);
    expect(sent.map((r) => `${r.path} ${r.body} ${r.status}`).sort()).toEqual([
      '/api/output/3/hdr {"mode":2} 200',
      '/api/output/3/mute {"muted":true} 200',
    ]);
    const after = (await sim.state()).outputs;
    expect(after[2].audio_mute).toBe(1);
    expect(after[2].hdr).toBe(1); // API HDR 2 (HDR to SDR) = device code 1
    // Nothing else changed on any output.
    const expected = settingsOf(before);
    expected[2] = { ...expected[2], audio_mute: 1, hdr: 1 };
    expect(settingsOf(after)).toEqual(expected);
  });

  // ----- UI-48: kiosk passcode -------------------------------------------------------

  /** Kiosk Profiles tab: tap the slot showing `name`. */
  async function kioskProfileSlot(page: Page, name: string) {
    await page.locator('.kiosk-tab-btn[data-tab="profiles"]').click();
    await settle(page, 300);
    await page.locator('#profilesGrid .kiosk-btn', { hasText: name }).click();
  }

  async function kioskPin(page: Page, digits: string) {
    for (const d of digits) await page.locator(`#passcodeModal [data-digit="${d}"]`).click();
  }

  test('UI-48: the kiosk asks for the passcode of a protected profile and applies it', async ({ page, sim }) => {
    await preparePage(page);
    await openKiosk(page);
    await kioskProfileSlot(page, 'Kids Gaming');
    await expect(page.locator('#passcodeModal')).toHaveClass(/show/);
    await expect(page.locator('#passcodeModal')).toContainText('Kids Gaming');
    await kioskPin(page, '1234');
    await expect(page.locator('#passcodeDisplay')).toHaveText('••••');
    const recall = page.waitForResponse((r) => r.url().endsWith('/api/profile/kids_gaming/recall') && !!r.request().postData()?.includes('1234'));
    await page.locator('#passcodeOkBtn').click();
    expect((await recall).status()).toBe(200);
    await expect(page.locator('#passcodeModal')).not.toHaveClass(/show/);
    await expect.poll(async () => (await sim.state()).outputs[0].source).toBe(6);
    await expect(page.locator('#kioskToast')).toHaveText('Profile activated');
  });

  test('UI-48: a wrong kiosk passcode says "Invalid passcode"; cancel sends nothing', async ({ page, sim }) => {
    await preparePage(page);
    await openKiosk(page);
    const recalls: string[] = [];
    page.on('request', (r) => {
      if (r.url().endsWith('/api/profile/kids_gaming/recall')) recalls.push(r.postData() ?? '');
    });
    await kioskProfileSlot(page, 'Kids Gaming');
    await kioskPin(page, '9999');
    await page.locator('#passcodeOkBtn').click();
    await expect(page.locator('#kioskToast')).toHaveText('Invalid passcode');
    await expect(page.locator('#kioskToast')).toHaveClass(/error/);
    expect((await sim.state()).outputs[0].source).toBe(2);
    await settle(page, 2800); // let the toast go
    await kioskProfileSlot(page, 'Kids Gaming');
    await expect(page.locator('#passcodeModal')).toHaveClass(/show/);
    await page.locator('#passcodeCancelBtn').click();
    await expect(page.locator('#passcodeModal')).not.toHaveClass(/show/);
    await settle(page, 500);
    // attempt 1: no passcode, 9999; attempt 2: no passcode, then cancelled
    expect(recalls.map((b) => (b.includes('9999') ? '9999' : '-'))).toEqual(['-', '9999', '-']);
    expect((await sim.state()).outputs[0].source).toBe(2);
  });

  // ----- UI-45: profile CEC targets ----------------------------------------------------

  test('UI-45: the profile editor has a CEC button that opens the CEC dialog for that profile', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    await mainTab(page, 'profiles');
    await page.locator('#save-scene-btn').click(); // new profile: nothing to configure yet
    await page.locator('#profile-editor-modal.visible').waitFor();
    await expect(page.locator('#open-cec-config-btn')).toBeHidden();
    await page.locator('#cancel-profile-btn').click();
    await expect(page.locator('#profile-editor-modal')).not.toHaveClass(/visible/);
    await page.locator('#scenes-list .edit-scene-btn[data-scene-id="movie_night"]').click();
    await page.locator('#profile-editor-modal.visible').waitFor();
    const button = page.locator('#open-cec-config-btn');
    await expect(button).toBeVisible();
    await button.click();
    await expect(page.locator('#scene-cec-modal')).toBeVisible();
    await expect(page.locator('#cec-scene-name')).toHaveText('Movie Night');
    await expect(page.locator('#targets-navigation .chip-label')).toHaveText(['Input 2 · AppleTV']);
  });

  test('UI-45: after a profile is recalled the CEC tray sends to that profile\'s CEC targets', async ({ page }) => {
    await preparePage(page);
    // Game Day's CEC config (the fixture has none): navigation goes to input 6 (PS5).
    await page.route('**/api/profile/game_day/cec', (route) =>
      route.request().method() === 'GET'
        ? route.fulfill({
            status: 200,
            contentType: 'application/json',
            json: {
              success: true,
              data: {
                profile_id: 'game_day',
                cec_config: {
                  nav_targets: ['input:6'], playback_targets: ['input:6'], volume_targets: ['output:2'],
                  power_on_targets: [], power_off_targets: [], auto_resolved: false,
                },
              },
              error: null,
            },
          })
        : route.fallback(),
    );
    await openUi(page);
    await openSettingsDrawer(page, 'profiles');
    const cecLoaded = page.waitForResponse((r) => r.url().endsWith('/api/profile/game_day/cec'));
    await page.locator('#settings-drawer .execute-profile-btn[data-id="game_day"]').click();
    await cecLoaded;
    await page.keyboard.press('Escape');
    await page.evaluate(() => (window as any).settingsDrawer.close()); // eslint-disable-line @typescript-eslint/no-explicit-any
    await page.locator('.cec-tray-fab').click();
    await page.locator('#cec-tray.expanded').waitFor();
    // The recall's own routing_change events (outputs 1-3 -> input 5) arrive over the WebSocket
    // and must not drop the profile's CEC targets.
    await page.waitForFunction(() => [1, 2, 3].every((o) => (window as any).state.routing[o] === 5), undefined, { timeout: 15_000 }); // eslint-disable-line @typescript-eslint/no-explicit-any
    await settle(page, 300);
    await expect(page.locator('#cec-tray.expanded [data-target="navigation"] .target-abbrev').first()).toHaveText('PS5');
    const sent = page.waitForRequest((r) => /\/api\/cec\/(input|output)\/\d\/up$/.test(new URL(r.url()).pathname));
    await page.locator('#cec-tray.expanded [data-cmd="up"]:visible').first().click();
    expect(new URL((await sent).url()).pathname).toBe('/api/cec/input/6/up');
  });

  test('UI-24: kiosk status tiles come from the real status routes', async ({ page, pageProblems }) => {
    await preparePage(page);
    const missing: string[] = [];
    page.on('response', (r) => {
      if (r.status() === 404 && new URL(r.url()).pathname.startsWith('/api/')) missing.push(new URL(r.url()).pathname);
    });
    await openKiosk(page);
    await settle(page, 1000);
    expect(missing).toEqual([]);
    expect(pageProblems.consoleErrors).toEqual([]);
    // Seed: input 2 (AppleTV) has a signal, input 1 (PS3) has none.
    await expect(page.locator('#kioskGrid .kiosk-btn').nth(1)).toHaveClass(/status-signal/);
    await expect(page.locator('#kioskGrid .kiosk-btn').nth(0)).not.toHaveClass(/status-signal/);
  });

  test('UI-25: the kiosk profile wizard opens with the hub macros', async ({ page, pageProblems }) => {
    await preparePage(page);
    await openKiosk(page);
    await page.locator('.kiosk-tab-btn[data-tab="profiles"]').click();
    await page.locator('#kioskEditBtn').click();
    await page.locator('#kioskEditBtn.active').waitFor();
    await page.locator('#profilesGrid .kiosk-btn').first().click();
    await page.locator('#slotMapperModal.show').waitFor();
    await page.locator('#slotMappingList > *').first().click();
    await expect(page.locator('#profileModal')).toHaveClass(/show/);
    const macroOptions = await page.locator('#profilePowerOnMacro option').allTextContents();
    expect(macroOptions.map((t) => t.trim())).toEqual(['None', 'TV + Apple TV On', 'All Off', 'Soundbar Volume +3']);
    expect(pageProblems.pageErrors).toEqual([]);
  });

  test('UI-25: the kiosk routing wizard "Next" on step 1 goes to the options step', async ({ page }) => {
    await preparePage(page);
    await openKiosk(page);
    await page.locator('#kioskGrid .kiosk-btn').nth(1).click();
    await page.locator('#wizardOutputsList .wizard-option-btn[data-output="2"]').click();
    await expect(page.locator('#routingStep2')).toBeVisible();
    await page.locator('#routingPrevBtn').click();
    await expect(page.locator('#routingStep1')).toBeVisible();
    await page.locator('#routingNextBtn').click();
    await expect(page.locator('#routingStep2')).toBeVisible();
  });

  // ----- SEC-07 / SEC-08: escaping ------------------------------------------------------

  test('SEC-07: escapeHtml escapes quotes for attribute contexts', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    const out = await page.evaluate(() => (window as any).Helpers.escapeHtml(`<a href="x" title='y'>&</a>`)); // eslint-disable-line @typescript-eslint/no-explicit-any
    expect(out).toBe('&lt;a href=&quot;x&quot; title=&#39;y&#39;&gt;&amp;&lt;/a&gt;');
  });

  const EVIL = `x"><img src=x onerror="window.__xss=(window.__xss||0)+1">`;

  test('SEC-08: hostile names and icons render as text in the main UI', async ({ page }) => {
    await preparePage(page);
    const evil = (b: Json, list: string, fields: string[]) => {
      for (const item of b.data?.[list] ?? []) for (const f of fields) item[f] = EVIL;
    };
    await page.route('**/api/profiles', async (route) => {
      const response = await route.fetch();
      const b = (await response.json()) as Json;
      evil(b, 'profiles', ['name', 'icon', 'id']);
      await route.fulfill({ response, json: b });
    });
    await page.route('**/api/v2/scenes', async (route) => {
      const response = await route.fetch();
      const b = (await response.json()) as Json;
      evil(b, 'scenes', ['name', 'icon']);
      await route.fulfill({ response, json: b });
    });
    await page.route('**/api/shortcuts', async (route) => {
      const response = await route.fetch();
      const b = (await response.json()) as Json;
      evil(b, 'shortcuts', ['name', 'label', 'icon']);
      await route.fulfill({ response, json: b });
    });
    await page.route('**/api/cec/macros', async (route) => {
      const response = await route.fetch();
      const b = (await response.json()) as Json;
      evil(b, 'macros', ['name', 'icon']);
      await route.fulfill({ response, json: b });
    });
    await openUi(page);
    for (const t of ['profiles', 'scenes', 'system'] as const) await openSettingsDrawer(page, t);
    await page.keyboard.press('Escape');
    await mainTab(page, 'profiles');
    await mainTab(page, 'dashboard');
    for (const [btn, root] of [
      ['drawer-shortcuts-btn', '#shortcuts-drawer.open'],
      ['drawer-integrations-btn', '#integrations-drawer.open'],
    ]) {
      await page.locator('#menu-toggle').click();
      await page.locator('#side-nav-drawer.open').waitFor();
      await page.locator(`#${btn}`).click();
      await page.locator(root).waitFor();
      await settle(page, 300);
      await page.keyboard.press('Escape');
    }
    await settle(page, 500);
    expect(await page.evaluate(() => (window as any).__xss ?? 0)).toBe(0); // eslint-disable-line @typescript-eslint/no-explicit-any
    expect(await page.locator('img[src="x"]').count()).toBe(0);
  });

  test('SEC-08: hostile names and icons render as text in the kiosk', async ({ page }) => {
    await preparePage(page);
    const hostile = async (glob: string, list: string, fields: string[]) =>
      page.route(glob, async (route) => {
        const response = await route.fetch();
        const b = (await response.json()) as Json;
        for (const item of b.data?.[list] ?? []) for (const f of fields) item[f] = EVIL;
        await route.fulfill({ response, json: b });
      });
    await hostile('**/api/profiles', 'profiles', ['name', 'icon']);
    await hostile('**/api/shortcuts', 'shortcuts', ['name', 'label', 'icon']);
    await hostile('**/api/presets', 'presets', ['name']);
    await hostile('**/api/cec/macros', 'macros', ['name']);
    await page.route('**/api/status', async (route) => {
      const response = await route.fetch();
      const b = (await response.json()) as Json;
      for (const k of Object.keys(b.data?.input_names ?? {})) b.data.input_names[k] = EVIL;
      for (const k of Object.keys(b.data?.output_names ?? {})) b.data.output_names[k] = EVIL;
      await route.fulfill({ response, json: b });
    });
    await openKiosk(page, { ready: false });
    await settle(page, 1500);
    for (const t of ['presets', 'shortcuts', 'profiles'] as const) {
      await page.locator(`.kiosk-tab-btn[data-tab="${t}"]`).click();
      await settle(page, 300);
    }
    // Routing wizard (output names) and profile wizard (macro and input names).
    await page.locator('.kiosk-tab-btn[data-tab="routing"]').click();
    await page.locator('#kioskGrid .kiosk-btn').nth(1).click();
    await settle(page, 300);
    await page.locator('#routingModalCloseBtn').click();
    await page.locator('.kiosk-tab-btn[data-tab="profiles"]').click();
    await page.locator('#kioskEditBtn').click();
    await page.locator('#profilesGrid .kiosk-btn').first().click();
    await page.locator('#slotMapperModal.show').waitFor();
    await page.locator('#slotMappingList > *').first().click();
    await settle(page, 500);
    expect(await page.evaluate(() => (window as any).__xss ?? 0)).toBe(0); // eslint-disable-line @typescript-eslint/no-explicit-any
    expect(await page.locator('img[src="x"]').count()).toBe(0);
  });

  // ----- UI-44 / UI-51 / UI-52 / UI-53 ------------------------------------------------

  // ----- UI-55 / UI-57 (owner decision 2026-10-09): widgets are pinned, never dashboard cards ----------

  test('UI-55/UI-57: the hub drops stored widget cards; each widget shows once and the cards panel holds items only', async ({
    page,
  }, info) => {
    const hub = await hubApi(`10.250.${info.workerIndex % 250}.12`);
    // The seed layout (tests/e2e/fixtures/data/dashboard_layout.json) is a stored pre-UI-57 layout: the
    // aggregate_widget cards every install was seeded with (cec-tray, routing-dashboard, quick-actions,
    // orders 0-2), then seven item cards (orders 3-9). The hub drops the three when it loads the file and
    // renumbers the rest from 0. (Other flows may append cards later in a run, so only the stored seven
    // are checked by position.)
    const layout = await (await hub.get('/api/dashboard/layout')).json();
    expect(layout.data.cards.slice(0, 7).map((c: Json) => `${c.type}:${c.id}:${c.order}`)).toEqual([
      'scene:scene_movienight01:0',
      'scene:scene_kidslocked:1',
      'preset:2:2',
      'system_shortcut:builtin.mute_all_audio:3',
      'system_shortcut:user.a1b2c3d4e5f6:4',
      'profile:movie_night:5',
      'macro:macro_tv_on:6',
    ]);
    expect(layout.data.cards.filter((c: Json) => c.type === 'aggregate_widget')).toEqual([]);
    expect((await hub.post('/api/dashboard/cards', { data: { type: 'aggregate_widget', id: 'cec-tray' } })).status()).toBe(400);

    await preparePage(page);
    await openUi(page);
    await mainTab(page, 'dashboard');
    await expect(page.locator('#dashboard-cards-grid .dashboard-card').first()).toBeVisible();
    // Only item cards in the panel; the pinned Routing widget once.
    await expect(page.locator('#dashboard-cards-grid .dashboard-card-widget')).toHaveCount(0);
    await expect(page.locator('#dashboard-widgets > .dashboard-widget[data-widget-id="routing-dashboard"]')).toHaveCount(1);
    await expect(page.locator('#dashboard-widgets .routing-btn')).toHaveCount(8);
  });

  test('UI-57: a first visit pins every widget it registers, once each', async ({ page }) => {
    // No saved dashboard config: a browser's first visit. The CEC tray registers its widget ~100 ms after the
    // Routing drawer; before UI-57 the first registration saved the config and the CEC Remote was not pinned.
    await preparePage(page, { storage: { orei_dashboard_config: null } });
    await openUi(page);
    await mainTab(page, 'dashboard');
    const pinned = page.locator('#dashboard-widgets > .dashboard-widget');
    await expect(pinned).toHaveCount(2);
    expect(await pinned.evaluateAll((els) => els.map((e) => (e as HTMLElement).dataset.widgetId))).toEqual([
      'routing-dashboard',
      'cec-remote',
    ]);
    // One CEC Remote on the page: its control ids are unique again.
    await expect(page.locator('[id="cec-widget-dpad"]')).toHaveCount(1);
    await expect(page.locator('#dashboard-cards-grid .dashboard-card-widget')).toHaveCount(0);
    const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('orei_dashboard_config') ?? '{}'));
    expect(saved.pinnedWidgets).toEqual(['routing-dashboard', 'cec-remote']);
  });

  test('UI-51: a cec_command event never changes the output stream; it is kept apart as the last CEC power command', async ({
    page,
  }) => {
    await preparePage(page);
    await openUi(page);
    const r = await page.evaluate(() => {
      const w = window as any; // eslint-disable-line @typescript-eslint/no-explicit-any
      const s = w.state;
      const streams = () => Object.fromEntries(Object.entries(s.outputs).map(([k, o]) => [k, (o as Json).enabled]));
      const before = streams();
      let outputEvents = 0;
      s.on('outputs', () => outputEvents++);
      // The contract's cec_command events (docs/api/WEBSOCKET.md), and the handler called directly.
      w.app.handleWebSocketMessage({ type: 'cec_command', data: { type: 'output', port: 1, command: 'power_off' } });
      w.app.handleWebSocketMessage({ type: 'cec_command', data: { type: 'input', port: 2, command: 'power_on', name: 'AppleTV' } });
      w.app.handleCecCommand({ type: 'output', port: 2, command: 'power_off' });
      return { before, after: streams(), outputEvents, record: s.cecPowerCommands };
    });
    expect(r.after).toEqual(r.before);
    expect(Object.values(r.before)).toContain(true);
    expect(r.outputEvents).toBe(0);
    expect(r.record).toMatchObject({
      'output:1': { type: 'output', port: 1, command: 'power_off' },
      'input:2': { type: 'input', port: 2, command: 'power_on' },
      'output:2': { type: 'output', port: 2, command: 'power_off' },
    });
    // Nothing new is shown for it (a visible indicator is an owner decision, D5).
    expect(await toasts(page)).toEqual([]);
  });

  /** Computed look of the rows matching `sel`, and whether their actions sit right of the name on one row. */
  async function rowLook(page: Page, sel: string, name: string, actions: string) {
    return page.locator(sel).evaluateAll(
      (items, [nameSel, actionSel]) =>
        items.map((el) => {
          const n = el.querySelector(nameSel)!.getBoundingClientRect();
          const acts = [...el.querySelectorAll(actionSel)].map((b) => b.getBoundingClientRect());
          const cs = getComputedStyle(el);
          const centre = (r: DOMRect) => r.top + r.height / 2;
          const box = el.getBoundingClientRect();
          return {
            text: el.querySelector(nameSel)!.textContent?.trim(),
            oneRow: acts.length > 0 && acts.every((b) => Math.abs(centre(b) - centre(n)) <= 12 && b.left > n.right),
            actionRight: acts.length > 0 && acts.every((b) => b.right > box.right - 80),
            surface: cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && parseFloat(cs.borderTopLeftRadius) >= 8,
            top: box.top,
            bottom: box.bottom,
          };
        }),
      [name, actions],
    );
  }

  /** A close button drawn like the app's glass icon buttons: no native face, no border. */
  async function expectGlassClose(page: Page, sel: string) {
    const look = await page.locator(sel).evaluate((el) => {
      const cs = getComputedStyle(el);
      return { bg: cs.backgroundColor, borderStyle: cs.borderTopStyle };
    });
    expect(look, sel).toEqual({ bg: 'rgba(0, 0, 0, 0)', borderStyle: 'none' });
  }

  /** The active theme's accent colour as computed RGB. */
  async function accentColor(page: Page) {
    return page.evaluate(() => {
      const probe = document.createElement('span');
      probe.style.color = 'var(--accent)';
      document.body.appendChild(probe);
      const c = getComputedStyle(probe).color;
      probe.remove();
      return c;
    });
  }

  test('UI-52: the Add Card picker has tab-styled tabs and one row per item; its close button is a glass icon button', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    await mainTab(page, 'dashboard');
    await page.locator('#add-dashboard-card-btn').click();
    await page.locator('#dashboard-card-picker.visible').waitFor();
    // Tabs look like the app's other tabs (Settings drawer): no native button face, accent underline when active.
    const accent = await accentColor(page);
    const tabs = await page.locator('#dashboard-card-picker .picker-tab-btn').evaluateAll((els) =>
      els.map((b) => {
        const cs = getComputedStyle(b);
        return {
          active: b.classList.contains('active'),
          bg: cs.backgroundColor,
          top: cs.borderTopWidth,
          bottom: cs.borderBottomWidth,
          bottomColor: cs.borderBottomColor,
          color: cs.color,
          row: Math.round(b.getBoundingClientRect().top),
        };
      }),
    );
    for (const t of tabs) {
      expect(t.bg, JSON.stringify(t)).toBe('rgba(0, 0, 0, 0)');
      expect(t.top, JSON.stringify(t)).toBe('0px');
      expect(t.bottom, JSON.stringify(t)).toBe('2px');
      if (t.active) expect([t.color, t.bottomColor]).toEqual([accent, accent]);
      else expect(t.color).not.toBe(accent);
    }
    expect(new Set(tabs.map((t) => t.row)).size, 'tabs on one line').toBe(1);
    for (const t of ['profiles', 'scenes', 'presets', 'shortcuts', 'macros']) {
      await page.locator(`#dashboard-card-picker .picker-tab-btn[data-tab="${t}"]`).click();
      await settle(page, 200);
      const rows = await rowLook(page, '#picker-content .picker-item', '.picker-item-name', '.picker-add-btn, .picker-item-badge');
      expect(rows.length, t).toBeGreaterThan(0);
      for (const r of rows) expect(r, `${t}: ${r.text}`).toMatchObject({ oneRow: true, actionRight: true, surface: true });
      for (let i = 1; i < rows.length; i++) expect(rows[i].top, `${t}: rows overlap`).toBeGreaterThanOrEqual(rows[i - 1].bottom);
    }
    await expectGlassClose(page, '#dashboard-card-picker .modal-close-btn');
  });

  test('UI-52: the profile editor and CEC dialog close buttons are glass icon buttons', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    await mainTab(page, 'profiles');
    await page.locator('#scenes-list .edit-scene-btn[data-scene-id="movie_night"]').click();
    await page.locator('#profile-editor-modal.visible').waitFor();
    await expectGlassClose(page, '#profile-editor-modal .modal-close-btn');
    await page.locator('#open-cec-config-btn').click();
    await expect(page.locator('#scene-cec-modal')).toBeVisible();
    await expectGlassClose(page, '#scene-cec-modal .modal-close-btn');
  });

  test('UI-56: the Settings drawer close button is a glass icon button like the other drawers\' close buttons', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    await openSettingsDrawer(page, 'profiles');
    const close = '#settings-drawer .drawer-header .drawer-close-btn';
    await expectGlassClose(page, close);
    // Same box, shape and colour as a glass icon button (btn-icon, e.g. the Routing drawer's close) in the same header.
    const [own, reference] = await page.locator(close).evaluate((el) => {
      const probe = document.createElement('button');
      probe.className = 'btn-icon';
      probe.innerHTML = el.innerHTML;
      el.parentElement!.appendChild(probe);
      const look = (b: Element) => {
        const cs = getComputedStyle(b);
        const r = b.getBoundingClientRect();
        return { w: Math.round(r.width), h: Math.round(r.height), radius: cs.borderTopLeftRadius, color: cs.color, cursor: cs.cursor };
      };
      const out = [look(el), look(probe)];
      probe.remove();
      return out;
    });
    expect(own).toEqual(reference);
  });

  test('UI-58: a tall dialog stays between the fixed header and the bottom tab bar', async ({ page }) => {
    await preparePage(page);
    // The kiosk tablet (800 px high) and a phone: the scene editor with the seed's three steps and an override
    // is taller than the space below the header on both.
    for (const viewport of [{ width: 1340, height: 800 }, { width: 390, height: 844 }]) {
      await page.setViewportSize(viewport);
      await openUi(page);
      await openSettingsDrawer(page, 'scenes');
      await page.locator('#settings-drawer .edit-scene-btn[data-id="scene_movienight01"]').click();
      await expect(page.locator('#scene-editor-modal')).toHaveClass(/open/);
      await settle(page, 300);
      const box = await page.evaluate(() => {
        const rect = (sel: string) => document.querySelector(sel)!.getBoundingClientRect();
        const tabs = rect('.mobile-tabs');
        // The tab bar is at the bottom on phones; from 768 px it sits in the header.
        const tabsAtBottom = getComputedStyle(document.querySelector('.mobile-tabs')!).position === 'fixed' && tabs.top > window.innerHeight / 2;
        const dialog = rect('#scene-editor-modal .modal-content');
        return {
          headerBottom: rect('.header').bottom,
          limit: tabsAtBottom ? tabs.top : window.innerHeight,
          top: dialog.top,
          bottom: dialog.bottom,
          scrolls: document.querySelector('#scene-editor-modal .modal-content')!.scrollHeight > dialog.height,
        };
      });
      const label = `${viewport.width}x${viewport.height}: ${JSON.stringify(box)}`;
      expect(box.top, label).toBeGreaterThanOrEqual(box.headerBottom);
      expect(box.bottom, label).toBeLessThanOrEqual(box.limit);
      expect(box.scrolls, `${label}: the content is taller than the space, so it scrolls inside the dialog`).toBe(true);
    }
  });

  test('UI-53: the scene editor fields, checkbox, steps and overrides are styled like the rest of the app', async ({ page }) => {
    await preparePage(page);
    await openUi(page);
    await openSettingsDrawer(page, 'scenes');
    await page.locator('#settings-drawer .edit-scene-btn[data-id="scene_movienight01"]').click();
    await expect(page.locator('#scene-editor-modal')).toHaveClass(/open/);
    await page.locator('#scene-password-protected').check();
    const accent = await accentColor(page);
    const look = await page.evaluate(() => {
      const field = (sel: string) => {
        const cs = getComputedStyle(document.querySelector(sel)!);
        return { bg: cs.backgroundColor, border: cs.borderTopColor, radius: cs.borderTopLeftRadius, font: cs.fontFamily, color: cs.color };
      };
      const box = document.querySelector('#scene-password-protected')!;
      return {
        body: getComputedStyle(document.body).fontFamily,
        name: field('#scene-editor-name'),
        desc: field('#scene-desc'),
        pass: field('#scene-passcode'),
        checkbox: { accent: getComputedStyle(box).accentColor, size: box.getBoundingClientRect().width },
      };
    });
    // Description and passcode look like the Name field (not a native monospace textarea or a white box).
    expect(look.desc, JSON.stringify(look)).toEqual(look.name);
    expect(look.pass, JSON.stringify(look)).toEqual(look.name);
    expect(look.desc.font).toBe(look.body);
    // The checkbox is drawn in the accent colour at the app's checkbox size (macro checkboxes, 18 px).
    expect(look.checkbox.accent).toBe(accent);
    expect(look.checkbox.size).toBeGreaterThanOrEqual(18);
    // Steps are distinct card rows: name and type left, remove button right, on one row.
    const steps = await rowLook(page, '#scene-steps-list .step-item', '.step-name', '.remove-step-btn');
    expect(steps.length).toBe(3);
    for (const r of steps) expect(r, r.text).toMatchObject({ oneRow: true, actionRight: true, surface: true });
    for (let i = 1; i < steps.length; i++) expect(steps[i].top - steps[i - 1].bottom).toBeGreaterThanOrEqual(4);
    // The step type is secondary text next to the name, not the same run of text.
    const typeVsName = await page.locator('#scene-steps-list .step-item').first().evaluate((el) => {
      const n = getComputedStyle(el.querySelector('.step-name')!);
      const t = getComputedStyle(el.querySelector('.step-type')!);
      return { nameSize: parseFloat(n.fontSize), typeSize: parseFloat(t.fontSize), nameColor: n.color, typeColor: t.color };
    });
    expect(typeVsName.typeSize).toBeLessThan(typeVsName.nameSize);
    expect(typeVsName.typeColor).not.toBe(typeVsName.nameColor);
    // An override is one row with its clear button on the right.
    const overrides = await rowLook(page, '#scene-editor-modal .override-item', '.override-desc', '.clear-override-btn');
    expect(overrides.length).toBeGreaterThan(0);
    for (const r of overrides) expect(r, r.text).toMatchObject({ oneRow: true, actionRight: true, surface: true });
    await expectGlassClose(page, '#scene-editor-modal .modal-close');
  });
});
