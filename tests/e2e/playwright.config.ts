// Playwright config for the web UI (docs/REMEDIATION_PLAN.md §5.3, Phase 0).
//
// Projects:
//   smoke                      smoke.spec.ts: /ui and /kiosk load, routing, WebSocket, axe
//   flows                      flows.spec.ts (after smoke): UI functional flows (WP-E1: passcode,
//                              partial runs, profiles, dashboard, kiosk, CEC remotes, escaping)
//   desktop | tablet | phone | kiosk-tab-a11 | kiosk-iphone16promax
//                              visual.spec.ts: every catalog entry (tests/e2e/visual/catalog.ts)
//                              in the default preset; desktop and the two kiosk devices
//                              also run the @themed entries in the other three presets.
//                              Sizes in tests/e2e/support/viewports.ts (kiosk-tab-a11 is
//                              PROVISIONAL until its CSS viewport is confirmed on the device).
//
// The stack (simulator + hub, seeded data) is started by webServer via
// tests/e2e/support/start-stack.mjs on fixed ports.
//
// Visual baselines are generated ONLY in the pinned container
// (mcr.microsoft.com/playwright:v1.63.0-noble): `npm run visual:update`.
import { defineConfig, devices } from '@playwright/test';
import { HUB_URL, PORTS } from './support/ports.mjs';
import { THEMED_VIEWPORTS, VIEWPORTS, VISUAL_VIEWPORTS, type ViewportName } from './support/viewports';

const CI = !!process.env.CI;

const visualProject = (name: ViewportName) => ({
  name,
  // visual.spec.ts: screenshots; status-colours.spec.ts: computed status colours (TST-10)
  testMatch: /visual\/(visual|status-colours)\.spec\.ts$/,
  // Captures never change hub or simulator state (writes are blocked in the
  // spec, hub broadcasts are filtered per page), so they run in parallel.
  fullyParallel: true,
  // The smoke and flow tests DO change simulator state; running them first (and
  // alone) keeps them from racing the captures. Skip with --no-deps.
  dependencies: ['flows'],
  // Theme presets other than Tron Classic run on desktop and the kiosk devices only (§5.3).
  ...((THEMED_VIEWPORTS as readonly ViewportName[]).includes(name) ? {} : { grepInvert: /@themed/ }),
  use: {
    ...devices['Desktop Chrome'],
    // The HTML report already has expected/actual/diff; traces for ~800
    // captures cost memory and disk for little extra.
    trace: 'off' as const,
    viewport: VIEWPORTS[name].viewport,
    ...('screen' in VIEWPORTS[name] ? { screen: VIEWPORTS[name].screen } : {}),
    deviceScaleFactor: VIEWPORTS[name].deviceScaleFactor,
    isMobile: VIEWPORTS[name].isMobile,
    hasTouch: VIEWPORTS[name].hasTouch,
    userAgent: VIEWPORTS[name].userAgent ?? devices['Desktop Chrome'].userAgent,
  },
});

// Output locations can be redirected (absolute paths). The container runner
// uses this to write inside the container and copy back once at the end:
// Docker Desktop bind mounts on Windows intermittently fail concurrent writes
// with ENOMEM.
const OUTPUT_DIR = process.env.E2E_OUTPUT_DIR ?? '../../test-results';
const REPORT_DIR = process.env.E2E_REPORT_DIR ?? '../../playwright-report';
const SNAPSHOT_DIR = process.env.E2E_SNAPSHOT_DIR ?? '{testDir}/visual/__snapshots__';

export default defineConfig({
  testDir: '.',
  outputDir: OUTPUT_DIR,
  snapshotPathTemplate: `${SNAPSHOT_DIR}/{projectName}/{arg}{ext}`,
  // One stack is shared by all tests. Smoke tests (which change simulator
  // state) run serially in one worker before any capture; captures run in
  // parallel. Each test resets the simulator state it depends on.
  fullyParallel: false,
  workers: Number(process.env.E2E_WORKERS ?? 4),
  retries: 0,
  forbidOnly: CI,
  timeout: 60_000,
  expect: {
    timeout: 10_000,
    toHaveScreenshot: {
      animations: 'disabled',
      caret: 'hide',
      scale: 'css',
      // Per-pixel colour threshold (pixelmatch YIQ distance); no pixel budget:
      // baselines are rendered in the same pinned container as CI, where
      // re-renders are deterministic. TST-10: Playwright's default 0.2 let a
      // status colour change pass (#ef4444 red vs the orange standby colour
      // is ~0.13 even on solid pixels; the header pill and kiosk dot changing
      // red <-> orange passed). 0.05 catches it at >= 40% pixel coverage.
      // Baselines that drifted below 0.2 before this change keep 0.2 until
      // re-approved: STALE_BASELINES in visual/visual.spec.ts.
      threshold: 0.05,
      maxDiffPixels: 0,
    },
  },
  reporter: [
    ['list'],
    ['html', { outputFolder: REPORT_DIR, open: 'never' }],
    ['json', { outputFile: `${OUTPUT_DIR}/results.json` }],
  ],
  use: {
    baseURL: HUB_URL,
    locale: 'en-US',
    timezoneId: 'UTC',
    colorScheme: 'dark',
    reducedMotion: 'no-preference',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    serviceWorkers: 'block',
  },
  webServer: {
    command: 'node tests/e2e/support/start-stack.mjs',
    cwd: '../..',
    url: `${HUB_URL}/api/health`,
    timeout: 90_000,
    reuseExistingServer: !CI && !process.env.PLAYWRIGHT_CONTAINER,
    stdout: 'pipe',
    stderr: 'pipe',
    env: { E2E_API_PORT: String(PORTS.api) },
  },
  projects: [
    {
      name: 'smoke',
      testMatch: /smoke\.spec\.ts$/,
      use: { ...devices['Desktop Chrome'], viewport: VIEWPORTS.desktop.viewport },
    },
    {
      // UI functional flows (flows.spec.ts, WP-E1). After the smoke tests, not
      // beside them: both change the one shared simulator, and a smoke test that
      // waits on a front-panel change must not see another file reset it.
      name: 'flows',
      testMatch: /flows\.spec\.ts$/,
      dependencies: ['smoke'],
      use: { ...devices['Desktop Chrome'], viewport: VIEWPORTS.desktop.viewport },
    },
    ...VISUAL_VIEWPORTS.map(visualProject),
  ],
});
