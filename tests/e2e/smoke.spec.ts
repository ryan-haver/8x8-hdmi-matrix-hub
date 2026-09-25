// Smoke E2E against the simulator (TST-04, docs/REMEDIATION_PLAN.md Phase 0).
//
//   npm run test:e2e
//
// - /ui and /kiosk load with no uncaught page errors. Console errors the
//   current UI already produces are listed in KNOWN_CONSOLE_ERRORS; a new one
//   fails the test.
// - Routing a source to an output through the UI changes the simulator.
// - The WebSocket connects.
// - An axe scan per page; violations are attached to the report but do not
//   fail the run (they become blocking in Phase 5).
import AxeBuilder from '@axe-core/playwright';
import { expect, openKiosk, openUi, preparePage, test } from './support/ui';

/**
 * Console errors the unmodified UI logs during these flows. Recorded so the
 * smoke test stays green on today's UI but catches new errors; remove entries
 * as the underlying bugs are fixed. Matched as substrings.
 */
const KNOWN_CONSOLE_ERRORS: Array<{ page: 'ui' | 'kiosk'; text: string; why: string }> = [
  {
    page: 'kiosk',
    text: 'Failed to load resource: the server responded with a status of 404',
    why: 'kiosk.html:2514-2515 polls /api/inputs/status and /api/outputs/status, which do not exist (real routes: /api/status/inputs|outputs)',
  },
];

/**
 * Uncaught errors the unmodified UI throws on user interaction (loading the
 * pages throws none, and the load tests require exactly that).
 */
export const KNOWN_PAGE_ERRORS: Array<{ text: string; why: string }> = [
  {
    text: 'e.target.closest is not a function',
    why: 'tooltip.js:25-28 listens for mouseenter/focus on document in the capture phase; when the pointer enters the page the target is `document`, which has no closest() (tooltip.js:35)',
  },
];

function unknownPageErrors(errors: string[]) {
  return errors.filter((e) => !KNOWN_PAGE_ERRORS.some((k) => e.includes(k.text)));
}

function unknownErrors(errors: string[], pageName: 'ui' | 'kiosk') {
  return errors.filter((e) => !KNOWN_CONSOLE_ERRORS.some((k) => k.page === pageName && e.includes(k.text)));
}

async function axeReport(page: import('@playwright/test').Page, name: string) {
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
  const summary = results.violations.map((v) => ({
    id: v.id,
    impact: v.impact,
    help: v.help,
    nodes: v.nodes.length,
    helpUrl: v.helpUrl,
  }));
  await test.info().attach(`axe-${name}.json`, {
    body: JSON.stringify({ summary, violations: results.violations }, null, 2),
    contentType: 'application/json',
  });
  test.info().annotations.push({
    type: 'axe',
    description: `${name}: ${results.violations.length} rule violations, ${summary.reduce((n, v) => n + v.nodes, 0)} nodes (${summary
      .map((v) => `${v.id}×${v.nodes}`)
      .join(', ')})`,
  });
  return results.violations;
}

test.describe('smoke', () => {
  test.afterEach(async ({ sim }) => {
    // Leave the shared simulator as the next test expects it.
    await sim.reset();
  });

  test('/ui loads without page errors, connects the WebSocket and passes an axe scan (report-only)', async ({
    page,
    pageProblems,
  }) => {
    await preparePage(page);
    const wsOpened = page.waitForEvent('websocket', (ws) => ws.url().endsWith('/ws'));
    await openUi(page);
    const ws = await wsOpened;
    expect(ws.isClosed()).toBe(false);
    await expect(page.locator('#header-title-text')).toHaveClass(/connected/);
    await expect(page.locator('#header-title-text')).not.toHaveClass(/disconnected/);
    await expect(page.locator('#header-title-text')).toHaveText('BK-808');
    await expect(page.locator('#matrix-grid .matrix-route')).toHaveCount(64);

    await axeReport(page, 'ui');
    expect(pageProblems.pageErrors, 'uncaught page errors').toEqual([]);
    expect(unknownErrors(pageProblems.consoleErrors, 'ui'), 'unexpected console errors').toEqual([]);
  });

  test('/kiosk loads without page errors, connects the WebSocket and passes an axe scan (report-only)', async ({
    page,
    pageProblems,
  }) => {
    await preparePage(page);
    const wsOpened = page.waitForEvent('websocket', (ws) => ws.url().endsWith('/ws'));
    await openKiosk(page);
    const ws = await wsOpened;
    expect(ws.isClosed()).toBe(false);
    await expect(page.locator('#statusDot')).toHaveClass(/connected/);
    await expect(page.locator('#outputStatusGrid .output-tile')).toHaveCount(8);

    await axeReport(page, 'kiosk');
    expect(pageProblems.pageErrors, 'uncaught page errors').toEqual([]);
    expect(unknownErrors(pageProblems.consoleErrors, 'kiosk'), 'unexpected console errors').toEqual([]);
    test.info().annotations.push({
      type: 'known-console-errors',
      description: pageProblems.consoleErrors.join(' | ') || 'none',
    });
  });

  test('routing an input to an output in the matrix grid changes the simulator', async ({ page, sim, pageProblems }) => {
    await preparePage(page, { storage: { 'matrix-view-mode': 'grid' } });
    await openUi(page);
    // Seed state: output 1 (TV) shows input 2 (AppleTV).
    expect((await sim.state()).outputs[0].source).toBe(2);

    const cell = page.locator('#matrix-grid .matrix-route[data-input="3"][data-output="1"]');
    await cell.click();
    await expect.poll(async () => (await sim.state()).outputs[0].source, { timeout: 10_000 }).toBe(3);
    await expect(cell).toHaveClass(/active/);
    await expect(page.locator('#matrix-grid .matrix-route[data-input="2"][data-output="1"]')).not.toHaveClass(/active/);
    // The other outputs are untouched.
    expect((await sim.state()).outputs.map((o) => o.source)).toEqual([3, 2, 1, 1, 5, 6, 1, 1]);
    expect(unknownPageErrors(pageProblems.pageErrors), 'unexpected page errors').toEqual([]);
    expect(unknownErrors(pageProblems.consoleErrors, 'ui'), 'unexpected console errors').toEqual([]);
  });

  test('routing an input to all outputs from the kiosk changes the simulator', async ({ page, sim, pageProblems }) => {
    await preparePage(page);
    await openKiosk(page);
    await page.locator('#kioskGrid .kiosk-btn').nth(4).click(); // input 5 (Shield)
    await page.locator('#routeToAllBtn').click();
    await page.locator('#routingApplyBtn').click();
    await expect.poll(async () => (await sim.state()).outputs.map((o) => o.source), { timeout: 10_000 }).toEqual([
      5, 5, 5, 5, 5, 5, 5, 5,
    ]);
    // Known kiosk bug: Apply also mutes every target and turns ARC on, whatever
    // the checkboxes say (kiosk.html:1957/1964 send {enable}/{mute}; the hub reads
    // enabled/muted, defaulting to true). Recorded so a fix shows up here.
    const outputs = (await sim.state()).outputs;
    test.info().annotations.push({
      type: 'known-bug',
      description: `kiosk route-all apply: audio_mute=${outputs.map((o) => o.audio_mute).join(',')} arc=${outputs
        .map((o) => o.arc)
        .join(',')}`,
    });
    expect(unknownPageErrors(pageProblems.pageErrors), 'unexpected page errors').toEqual([]);
  });
});
