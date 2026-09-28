#!/usr/bin/env node
// Browser side of the `browser` validation client (tools/validate/clients/browser.py).
//
// Reads one JSON command per line on stdin, answers one JSON line on stdout:
//   {"id":1,"op":"start","baseURL":"http://127.0.0.1:18080","forwardedFor":"10.9.0.1","artifacts":"/abs/dir"}
//   {"id":2,"op":"perform","intent":"route","params":{"input":3,"output":1},"label":"routing.switch_one"}
//   {"id":3,"op":"stop"}
// -> {"id":N,"ok":true,"result":{...}} | {"id":N,"ok":false,"error":"..."}
//
// Every action gets a fresh browser context, the same deterministic page setup
// as the Playwright suites (tests/e2e/support/ui.ts: seeded localStorage, Tron
// background off, transitions disabled) and drives the UI the way a user does
// (Control Deck -> drawer -> button). The Python side then checks the
// simulator: a UI action is proven by the device state, not by the screenshot.
// Functions passed to page.evaluate/addInitScript/waitForFunction run in the page.
/* global window, document */
import { chromium } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline';

// Mirrors BASE_STORAGE in tests/e2e/support/ui.ts (first visit, no migration
// race, Tron background off).
const BASE_STORAGE = {
  orei_phase7_migration_done: 'true',
  orei_dashboard_config: JSON.stringify({
    pinnedWidgets: ['routing-dashboard'],
    hiddenMobileWidgets: [],
    widgetOrder: ['routing-dashboard'],
  }),
  tron_background_enabled: 'false',
};
const FREEZE_CSS = `*, *::before, *::after { transition-duration: 0s !important; transition-delay: 0s !important;
  animation-delay: 0s !important; caret-color: transparent !important; scroll-behavior: auto !important; }`;

let browser = null;
let cfg = null;

function send(obj) {
  process.stdout.write(JSON.stringify(obj) + '\n');
}

async function newPage(storage = {}, forwardedFor = null) {
  const context = await browser.newContext({
    baseURL: cfg.baseURL,
    viewport: { width: 1440, height: 900 },
    locale: 'en-US',
    timezoneId: 'UTC',
    colorScheme: 'dark',
    serviceWorkers: 'block',
    // One client address per action (like the Playwright suites): the hub rate
    // limits per client (60 requests / 10 s) and one /ui load uses a third of that.
    extraHTTPHeaders: { 'X-Forwarded-For': forwardedFor ?? cfg.forwardedFor },
  });
  const page = await context.newPage();
  const problems = { pageErrors: [], consoleErrors: [], apiCalls: [], apiRequestCount: 0 };
  page.on('pageerror', (e) => problems.pageErrors.push(`${e.name}: ${e.message}`));
  page.on('console', (m) => {
    if (m.type() === 'error') problems.consoleErrors.push(m.text());
  });
  page.on('response', (r) => {
    const req = r.request();
    const url = new URL(r.url());
    if (url.pathname.startsWith('/api/')) problems.apiRequestCount++;
    if (url.pathname.startsWith('/api/') && req.method() !== 'GET') {
      problems.apiCalls.push({ method: req.method(), path: url.pathname, body: req.postData(), status: r.status() });
    }
  });
  await page.addInitScript(
    ({ storage, css }) => {
      try {
        if (!sessionStorage.getItem('__validate_seeded')) {
          localStorage.clear();
          for (const [k, v] of Object.entries(storage)) localStorage.setItem(k, v);
          sessionStorage.setItem('__validate_seeded', '1');
        }
      } catch {
        /* storage unavailable */
      }
      const inject = () => {
        const style = document.createElement('style');
        style.textContent = css;
        document.head.appendChild(style);
      };
      if (document.head) inject();
      else document.addEventListener('DOMContentLoaded', inject, { once: true });
    },
    { storage: { ...BASE_STORAGE, ...storage }, css: FREEZE_CSS },
  );
  return { context, page, problems };
}

// Same readiness condition as waitForUiReady() in tests/e2e/support/ui.ts.
async function openUi(page, steps) {
  await page.goto('/ui');
  await page.waitForFunction(
    () =>
      !!window.app &&
      !!document.querySelector('#drawer-tab-settings-list li.tab-settings-item') &&
      !!window.cecTray &&
      window.state?.ui?.dataLoaded === true,
    undefined,
    { timeout: 20_000 },
  );
  await page.waitForTimeout(600);
  steps.push('open /ui and wait until the app has loaded its data');
}

async function openDrawer(page, button, root, steps) {
  await page.locator('#menu-toggle').click();
  await page.locator('#side-nav-drawer.open').waitFor();
  await page.locator(`#${button}`).click();
  await page.locator(root).first().waitFor({ state: 'visible' });
  await page.waitForTimeout(300);
  steps.push(`open the Control Deck and the ${button.replace('drawer-', '').replace('-btn', '')} drawer`);
}

const waitForCall = (page, method, ...pathParts) =>
  page.waitForResponse(
    (r) => r.request().method() === method && pathParts.some((p) => new URL(r.url()).pathname.includes(p)),
    { timeout: 20_000 },
  );

const FLOWS = {
  async route(page, p, steps) {
    await openUi(page, steps);
    const cell = page.locator(`#matrix-grid .matrix-route[data-input="${p.input}"][data-output="${p.output}"]`);
    // The grid posts /api/output/{n}/source (matrix-grid.js handleCellClick).
    const call = waitForCall(page, 'POST', '/api/switch', `/api/output/${p.output}/source`);
    await cell.click();
    steps.push(`click the matrix grid cell input ${p.input} / output ${p.output}`);
    return call;
  },
  async route_all(page, p, steps) {
    await openUi(page, steps);
    await openDrawer(page, 'drawer-routing-btn', '#routing-drawer.open', steps);
    const call = waitForCall(page, 'POST', '/api/switch');
    await page.locator(`#routing-drawer .routing-btn[data-input="${p.input}"]`).click();
    steps.push(`click input ${p.input} in the Route To All drawer`);
    return call;
  },
  async preset_recall(page, p, steps) {
    await openUi(page, steps);
    await openDrawer(page, 'drawer-presets-btn', '#presets-drawer.open', steps);
    await page.locator(`#presets-drawer .preset-row[data-preset-number="${p.preset}"] .preset-expand-btn`).click();
    steps.push(`expand preset ${p.preset}`);
    const call = waitForCall(page, 'POST', `/api/preset/${p.preset}`);
    await page.locator(`#presets-drawer .btn-recall-preset[data-preset="${p.preset}"]`).click();
    steps.push(`click Recall on preset ${p.preset}`);
    return call;
  },
  async preset_rename(page, p, steps) {
    await openUi(page, steps);
    await openDrawer(page, 'drawer-presets-btn', '#presets-drawer.open', steps);
    await page.locator(`#presets-drawer .preset-row-edit-btn[data-preset="${p.preset}"]`).click();
    const input = page.locator(`#presets-drawer .preset-row[data-preset-number="${p.preset}"] .preset-rename-input`);
    await input.fill(p.name);
    steps.push(`click Rename on preset ${p.preset} and type "${p.name}"`);
    const call = waitForCall(page, 'POST', `/api/device-settings/preset/${p.preset}/name`);
    await page.locator(`#presets-drawer .preset-save-btn[data-preset="${p.preset}"]`).click();
    steps.push('click Save Name');
    return call;
  },
};

/** The response of the run request the flow is about: the one with the passcode, if there is one. */
const waitForRun = (page, pathPart, passcode) =>
  page.waitForResponse(
    (r) =>
      r.request().method() === 'POST' &&
      new URL(r.url()).pathname.endsWith(pathPart) &&
      (!passcode || (r.request().postData() ?? '').includes(passcode)),
    { timeout: 30_000 },
  );

async function openKiosk(page, steps) {
  await page.goto('/kiosk');
  await page.locator('#kioskGrid .kiosk-btn').nth(7).waitFor({ timeout: 20_000 });
  await page.locator('#statusText', { hasText: 'Connected' }).waitFor({ timeout: 20_000 });
  await page.waitForTimeout(600);
  steps.push('open /kiosk and wait until it shows the inputs');
}

Object.assign(FLOWS, {
  // Recall from the Profiles tab (web/js/components/scenes-panel.js), the way a
  // user does. A protected profile opens the passcode prompt, answered with
  // p.passcode or cancelled (see perform()).
  async profile_recall(page, p, steps) {
    if (p.via === 'kiosk') return kioskProfileRecall(page, p, steps);
    await openUi(page, steps);
    await page.locator('.tab-btn[data-tab="profiles"]:visible').first().click();
    await page.waitForTimeout(400);
    steps.push('open the Profiles tab');
    const call = p.passcode
      ? waitForRun(page, `/api/profile/${p.profile_id}/recall`, p.passcode)
      : waitForRun(page, `/api/profile/${p.profile_id}/recall`);
    await page.locator(`#scenes-list .recall-scene-btn[data-scene-id="${p.profile_id}"]`).click();
    steps.push(`click Activate on profile ${p.profile_id}`);
    return call;
  },
  // Run from its dashboard card when the layout has one, else from the Settings
  // drawer's Scenes tab (the drawer only opens through #settings/<tab>).
  async scene_run(page, p, steps) {
    await openUi(page, steps);
    await page.locator('.tab-btn[data-tab="dashboard"]:visible').first().click();
    await page.waitForTimeout(400);
    const card = page.locator(`#dashboard-cards-grid .dashboard-card-action[data-type="scene"][data-id="${p.scene_id}"]`);
    let button = card;
    if (await card.count()) {
      steps.push(`open the Dashboard tab; scene ${p.scene_id} has a card`);
    } else {
      await page.evaluate(() => {
        window.location.hash = '#settings/scenes';
      });
      await page.locator('#settings-drawer.open').waitFor();
      await page.waitForTimeout(300);
      button = page.locator(`#settings-drawer .execute-scene-btn[data-id="${p.scene_id}"]`);
      steps.push('open the Settings drawer on the Scenes tab (#settings/scenes)');
    }
    const call = waitForRun(page, `/api/v2/scenes/${p.scene_id}/execute`, p.passcode);
    await button.click();
    steps.push(`click Execute on scene ${p.scene_id}`);
    return call;
  },
  // Kiosk routing wizard (web/kiosk.html): tap an input, choose the output (or
  // "Route to All Outputs"), set the options, Apply. The flow ends when the last
  // output setting request has answered.
  async kiosk_route(page, p, steps) {
    await openKiosk(page, steps);
    const targets = p.output === 'all' ? 8 : 1;
    const settings = [];
    page.on('response', (r) => {
      if (/\/api\/output\/\d\/(hdcp|hdr|scaler|arc|mute)$/.test(new URL(r.url()).pathname)) settings.push(r);
    });
    await page.locator('#kioskGrid .kiosk-btn').nth(p.input - 1).click();
    await page.locator('#routingModal.show').waitFor();
    steps.push(`tap input ${p.input}`);
    if (p.output === 'all') await page.locator('#routeToAllBtn').click();
    else await page.locator(`#wizardOutputsList .wizard-option-btn[data-output="${p.output}"]`).click();
    await page.locator('#routingStep2').waitFor({ state: 'visible' });
    steps.push(p.output === 'all' ? 'choose "Route to All Outputs"' : `choose output ${p.output}`);
    await page.locator('#routingMuteAudio').setChecked(!!p.mute);
    await page.locator('#toggleAdvancedRouting').click();
    await page.locator('#routingArc').setChecked(!!p.arc);
    steps.push(`set "Mute output audio" ${p.mute ? 'on' : 'off'} and ARC ${p.arc ? 'on' : 'off'}`);
    const routed = waitForCall(page, 'POST', '/api/switch', p.output === 'all' ? '/api/switch' : `/api/output/${p.output}/source`);
    await page.locator('#routingApplyBtn').click();
    steps.push('click Apply Routing');
    const response = await routed;
    const deadline = Date.now() + 20_000;
    // UI-46: only the options that changed from their defaults (both boxes start unchecked) are sent.
    const expected = targets * ((p.mute ? 1 : 0) + (p.arc ? 1 : 0));
    while (settings.length < expected && Date.now() < deadline) await page.waitForTimeout(100);
    await page.waitForTimeout(500);
    const statuses = await Promise.all(settings.map(async (r) => `${new URL(r.url()).pathname} ${r.status()}`));
    steps.push(`the kiosk sent ${settings.length} output setting requests: ${statuses.filter((s) => !s.endsWith(' 200')).join(', ') || 'all 200'}`);
    return response;
  },
});

// Kiosk Profiles tab: tap the profile's slot; a PIN pad (UI-48) is answered with
// p.passcode digit by digit, or cancelled when there is none.
async function kioskProfileRecall(page, p, steps) {
  await openKiosk(page, steps);
  await page.locator('.kiosk-tab-btn[data-tab="profiles"]').click();
  await page.waitForTimeout(400);
  steps.push('open the kiosk Profiles tab');
  const call = waitForRun(page, `/api/profile/${p.profile_id}/recall`, p.passcode);
  await page.locator('#profilesGrid .kiosk-btn', { hasText: p.name }).click();
  steps.push(`tap the "${p.name}" slot`);
  const pad = page.locator('#passcodeModal.show');
  if (await pad.waitFor({ timeout: 3000 }).then(() => true, () => false)) {
    if (p.passcode) {
      for (const d of String(p.passcode)) await page.locator(`#passcodeModal [data-digit="${d}"]`).click();
      await page.locator('#passcodeOkBtn').click();
      steps.push('enter the passcode on the PIN pad and tap OK');
    } else {
      await page.locator('#passcodeCancelBtn').click();
      steps.push('tap Cancel on the PIN pad');
    }
  }
  return call;
}

const FLOW_STORAGE = { route: { 'matrix-view-mode': 'grid' } };

/** Toasts the page shows: main UI (#toast-container) and kiosk (#kioskToast). */
async function shownToasts(page) {
  return page
    .evaluate(() => {
      const main = [...document.querySelectorAll('#toast-container .toast')].map((t) => {
        const kind = ['success', 'error', 'warning', 'info'].find((k) => t.classList.contains(k)) ?? 'info';
        return `${kind}: ${t.querySelector('.toast-message')?.textContent ?? ''}`;
      });
      // The kiosk toast keeps its last message after it hides (2.5 s): report it as shown.
      const kiosk = document.getElementById('kioskToast');
      if (kiosk?.textContent.trim()) {
        const kind = ['success', 'error', 'warning', 'info'].find((k) => kiosk.classList.contains(k)) ?? 'info';
        main.push(`${kind}: ${kiosk.textContent.trim()}`);
      }
      return main;
    })
    .catch(() => []);
}

async function perform(msg) {
  const flow = FLOWS[msg.intent];
  if (!flow) return { unsupported: true };
  const { context, page, problems } = await newPage(FLOW_STORAGE[msg.intent] ?? {}, msg.forwardedFor);
  const steps = [];
  const screenshots = [];
  // window.prompt / confirm: a passcode prompt is answered with params.passcode,
  // or cancelled when the scenario gives none (UI-01).
  const dialogs = [];
  page.on('dialog', async (dialog) => {
    dialogs.push(dialog.message());
    const passcode = msg.params?.passcode;
    if (dialog.type() === 'prompt' && passcode) {
      steps.push(`answer the prompt "${dialog.message()}" with the passcode`);
      await dialog.accept(String(passcode));
    } else {
      steps.push(`cancel the ${dialog.type()} "${dialog.message()}"`);
      await dialog.dismiss();
    }
  });
  let toasts; // what the page shows at the end (set on success and on error)
  const shot = async (tag) => {
    // Per-action directory next to the evidence record, else the run's artifacts dir.
    const dir = msg.artifacts ?? cfg.artifacts;
    if (!dir) return;
    fs.mkdirSync(dir, { recursive: true });
    const file = msg.artifacts ? path.join(dir, `${tag}.png`) : path.join(dir, `${msg.label ?? msg.intent}-${tag}.png`);
    await page.screenshot({ path: file });
    screenshots.push(file);
  };
  let status = null;
  let error = null;
  try {
    const response = await flow(page, msg.params ?? {}, steps);
    status = response.status();
    steps.push(`the page sent ${response.request().method()} ${new URL(response.url()).pathname} -> HTTP ${status}`);
    await page.waitForLoadState('networkidle', { timeout: 3000 }).catch(() => {});
    await page.waitForTimeout(500);
    toasts = await shownToasts(page);
    if (toasts.length) steps.push(`the page shows: ${toasts.join(' | ')}`);
    await shot('after');
  } catch (e) {
    error = `${e.name}: ${e.message.split('\n')[0]}`;
    toasts = await shownToasts(page);
    await shot('error').catch(() => {});
  } finally {
    await context.close();
  }
  return { status, error, steps, screenshots, toasts, dialogs, ...problems };
}

const rl = readline.createInterface({ input: process.stdin });
rl.on('line', async (line) => {
  let msg;
  try {
    msg = JSON.parse(line);
  } catch {
    return;
  }
  try {
    if (msg.op === 'start') {
      cfg = msg;
      browser = await chromium.launch();
      send({ id: msg.id, ok: true, result: { browser: `chromium ${browser.version()}` } });
    } else if (msg.op === 'perform') {
      send({ id: msg.id, ok: true, result: await perform(msg) });
    } else if (msg.op === 'stop') {
      if (browser) await browser.close();
      send({ id: msg.id, ok: true, result: {} });
      process.exit(0);
    }
  } catch (e) {
    send({ id: msg.id, ok: false, error: `${e.name}: ${e.message}` });
  }
});
