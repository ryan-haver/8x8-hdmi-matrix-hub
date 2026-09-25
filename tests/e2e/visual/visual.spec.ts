// Visual baselines for every UI catalog entry (docs/REMEDIATION_PLAN.md §5.3).
//
//   npm run visual:test     compare against the committed baselines (in the pinned container)
//   npm run visual:update   write new/changed baselines (in the pinned container)
//
// Matrix:
// - Tron Classic (default) x every catalog entry x the four viewport projects
//   (desktop, tablet, phone, kiosk; see tests/e2e/support/viewports.ts)
// - Neon, Royal, Vaporwave x entries marked `themed` (~key screens) x desktop
//   and kiosk (tests tagged @themed; the other projects grep them out)
// - one paused-frame snapshot with the Tron light-cycle background on
//
// Snapshots: tests/e2e/visual/__snapshots__/<project>/<entry name>.png, and
// .../<project>/themes/<preset>/<entry name>.png for the other presets.
//
// Determinism: fresh context per test, seeded localStorage, frozen Date,
// seeded Math.random, transitions/animations/caret disabled, Tron background
// off, pointer parked, fonts awaited, and simulator + hub reset before each
// test. Rendering only matches inside the pinned container image.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { CATALOG, type CatalogEntry } from './catalog';
import { expect, FIXED_TIME, openKiosk, openUi, parkPointer, preparePage, settle, test, THEMES, type ThemeName } from '../support/ui';
import type { ViewportName } from '../support/viewports';

/** Hub routes that only the running app should ever change; a capture that writes them would leak into later entries. */
const WRITE_GUARD = /\/api\/(ui\/preferences|dashboard\/cards|device-settings|shortcuts\/[^/]+\/(favorite|dashboard)|profile|v2\/scenes|cec\/macro)/;

test.describe.configure({ mode: 'default' });

/**
 * Catalog manifest next to the baselines (names, descriptions, notes, which
 * viewports/themes exist), read by tools/ui/build_gallery.mjs. Written whenever
 * snapshots may be written, so it always describes the committed baseline set.
 */
test.beforeAll(({}, info) => {
  if (info.config.updateSnapshots === 'none') return;
  const manifest = {
    generated_by: 'tests/e2e/visual/visual.spec.ts',
    themes: Object.keys(THEMES),
    viewports: ['desktop', 'tablet', 'phone', 'kiosk'],
    entries: [
      ...CATALOG.map((e) => ({
        name: e.name,
        page: e.page,
        description: e.description,
        note: e.note ?? null,
        themed: !!e.themed,
        viewports: e.viewports ?? null,
      })),
      {
        name: 'special/tron-background/paused-frame',
        page: 'ui',
        description: 'Tron light-cycle background enabled, one deterministic paused frame.',
        note: null,
        themed: false,
        viewports: ['desktop', 'kiosk'],
      },
    ],
  };
  const file = path.join(path.dirname(fileURLToPath(import.meta.url)), '__snapshots__', 'catalog.json');
  const body = `${JSON.stringify(manifest, null, 2)}\n`;
  fs.mkdirSync(path.dirname(file), { recursive: true });
  if (!fs.existsSync(file) || fs.readFileSync(file, 'utf8') !== body) fs.writeFileSync(file, body);
});

test.beforeEach(async ({ sim, page }) => {
  await sim.reset();
  // Captures must not mutate hub data: block writes to persisted hub state.
  await page.route(
    (url) => WRITE_GUARD.test(url.pathname),
    (route) => (route.request().method() === 'GET' ? route.fallback() : route.abort('blockedbyclient')),
  );
});

function snapshotName(entry: CatalogEntry, theme: ThemeName): string[] {
  const parts = entry.name.split('/');
  parts[parts.length - 1] += '.png';
  return theme === 'tron-classic' ? parts : ['themes', theme, ...parts];
}

async function capture(entry: CatalogEntry, theme: ThemeName, page: import('@playwright/test').Page, viewport: ViewportName) {
  await preparePage(page, { ...entry.prepare, theme });
  if (entry.routes) await entry.routes(page);
  if (entry.page === 'ui') await openUi(page, { ready: entry.ready });
  else await openKiosk(page, { ready: entry.ready });
  if (entry.setup) await entry.setup({ page, viewport });
  if (entry.scrollTo) {
    await page
      .locator(entry.scrollTo)
      .first()
      .evaluate((el) => el.scrollIntoView({ block: 'center', inline: 'nearest' }));
  }
  if (!entry.keepPointer) await parkPointer(page);
  await settle(page, 150);
  await expect(page).toHaveScreenshot(snapshotName(entry, theme), {
    mask: (entry.mask ?? []).map((s) => page.locator(s)),
    fullPage: false,
  });
}

for (const entry of CATALOG) {
  const viewports = entry.viewports;
  const skipReason = (viewport: ViewportName) =>
    viewports && !viewports.includes(viewport)
      ? viewports.length === 0
        ? `not capturable: ${entry.note ?? ''}`
        : `only captured at ${viewports.join(', ')}`
      : undefined;

  test(entry.name, async ({ page }, info) => {
    const vp = info.project.name as ViewportName;
    const reason = skipReason(vp);
    test.skip(!!reason, reason);
    if (entry.note) info.annotations.push({ type: 'note', description: entry.note });
    info.annotations.push({ type: 'description', description: entry.description });
    await capture(entry, 'tron-classic', page, vp);
  });

  if (entry.themed) {
    for (const theme of Object.keys(THEMES) as ThemeName[]) {
      if (theme === 'tron-classic') continue;
      test(`${entry.name} [${theme}] @themed`, async ({ page }, info) => {
        const vp = info.project.name as ViewportName;
        const reason = skipReason(vp);
        test.skip(!!reason, reason);
        info.annotations.push({ type: 'description', description: `${entry.description} (${theme} preset)` });
        await capture(entry, theme, page, vp);
      });
    }
  }
}

// One paused frame of the Tron light-cycle background (§5.3). The animation
// is driven by requestAnimationFrame + performance.now + Math.random; the page
// loads normally, then the clock is installed and paused, Math.random is
// reseeded, the background is started and advanced by a fixed amount of fake
// time, so the frame is the same on every run.
test('special/tron-background/paused-frame', async ({ page }, info) => {
  const vp = info.project.name as ViewportName;
  test.skip(vp !== 'desktop' && vp !== 'kiosk', 'captured at desktop and kiosk only');
  await preparePage(page, { realClock: true, storage: { 'matrix-view-mode': 'grid' } });
  await page.clock.install({ time: FIXED_TIME });
  await page.clock.resume();
  await openUi(page);
  await page.clock.pauseAt(new Date(FIXED_TIME.getTime() + 60 * 60 * 1000));
  await page.evaluate(() => {
    (window as unknown as { __e2eReseed: () => void }).__e2eReseed();
    (window as unknown as { TronBackground: { setEnabled: (b: boolean) => void } }).TronBackground.setEnabled(true);
  });
  await page.clock.runFor(6000);
  await parkPointer(page);
  await expect(page).toHaveScreenshot(['special', 'tron-background', 'paused-frame.png']);
});
