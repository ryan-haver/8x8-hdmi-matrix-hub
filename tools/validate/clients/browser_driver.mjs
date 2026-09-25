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

const FLOW_STORAGE = { route: { 'matrix-view-mode': 'grid' } };

async function perform(msg) {
  const flow = FLOWS[msg.intent];
  if (!flow) return { unsupported: true };
  const { context, page, problems } = await newPage(FLOW_STORAGE[msg.intent] ?? {}, msg.forwardedFor);
  const steps = [];
  const screenshots = [];
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
    await shot('after');
  } catch (e) {
    error = `${e.name}: ${e.message.split('\n')[0]}`;
    await shot('error').catch(() => {});
  } finally {
    await context.close();
  }
  return { status, error, steps, screenshots, ...problems };
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
