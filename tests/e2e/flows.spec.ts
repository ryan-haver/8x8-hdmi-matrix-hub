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

  test('UI-23: kiosk route-all applies the options as chosen (mute unchecked leaves audio on, ARC off) with valid values', async ({
    page,
    sim,
  }) => {
    await sim.patch({ outputs: { '0': { audio_mute: 1 }, '1': { arc: 1 } } });
    await preparePage(page);
    await openKiosk(page);
    const settings: Array<{ path: string; status: number; body: string | null }> = [];
    page.on('response', (r) => {
      const p = new URL(r.url()).pathname;
      if (/\/api\/output\/\d\/(hdcp|hdr|scaler|arc|mute)$/.test(p)) settings.push({ path: p, status: r.status(), body: r.request().postData() });
    });
    await page.locator('#kioskGrid .kiosk-btn').nth(4).click();
    await page.locator('#routeToAllBtn').click();
    await page.locator('#routingApplyBtn').click();
    await expect.poll(async () => (await sim.state()).outputs.map((o) => o.source), { timeout: 10_000 }).toEqual([5, 5, 5, 5, 5, 5, 5, 5]);
    await expect.poll(() => settings.length, { timeout: 10_000 }).toBe(40);
    expect(settings.filter((s) => s.status !== 200), 'rejected output settings').toEqual([]);
    const outputs = (await sim.state()).outputs;
    expect(outputs.map((o) => o.audio_mute)).toEqual([0, 0, 0, 0, 0, 0, 0, 0]);
    expect(outputs.map((o) => o.arc)).toEqual([0, 0, 0, 0, 0, 0, 0, 0]);
  });

  test('UI-23: kiosk "Mute output audio" mutes the chosen output only', async ({ page, sim }) => {
    await preparePage(page);
    await openKiosk(page);
    await page.locator('#kioskGrid .kiosk-btn').nth(2).click();
    await page.locator('#wizardOutputsList .wizard-option-btn[data-output="3"]').click();
    await page.locator('#routingMuteAudio').check();
    await page.locator('#routingApplyBtn').click();
    await expect.poll(async () => (await sim.state()).outputs[2].source, { timeout: 10_000 }).toBe(3);
    await expect.poll(async () => (await sim.state()).outputs[2].audio_mute, { timeout: 10_000 }).toBe(1);
    expect((await sim.state()).outputs.map((o) => o.audio_mute)).toEqual([0, 0, 1, 0, 0, 0, 0, 0]);
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
});
