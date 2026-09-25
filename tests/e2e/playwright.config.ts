// Playwright config for the web UI (docs/REMEDIATION_PLAN.md §5.3, Phase 0).
//
// Projects:
//   smoke                      smoke.spec.ts: /ui and /kiosk load, routing, WebSocket, axe
//   desktop | tablet | phone | kiosk
//                              visual.spec.ts: every catalog entry (tests/e2e/visual/catalog.ts)
//                              in the default preset; desktop and kiosk also run the
//                              @themed entries in the other three presets.
//
// The stack (simulator + hub, seeded data) is started by webServer via
// tests/e2e/support/start-stack.mjs on fixed ports.
//
// Visual baselines are generated ONLY in the pinned container
// (mcr.microsoft.com/playwright:v1.63.0-noble): `npm run visual:update`.
import { defineConfig, devices } from '@playwright/test';
import { HUB_URL, PORTS } from './support/ports.mjs';
import { VIEWPORTS } from './support/viewports';

const CI = !!process.env.CI;

const visualProject = (name: keyof typeof VIEWPORTS, themed: boolean) => ({
  name,
  testMatch: /visual\/visual\.spec\.ts$/,
  // Captures never change hub or simulator state (writes are blocked in the
  // spec, hub broadcasts are filtered per page), so they run in parallel.
  fullyParallel: true,
  // The smoke tests DO change simulator state; running them first (and
  // alone) keeps them from racing the captures. Skip with --no-deps.
  dependencies: ['smoke'],
  // Theme presets other than Tron Classic run on desktop and kiosk only (§5.3).
  ...(themed ? {} : { grepInvert: /@themed/ }),
  use: {
    ...devices['Desktop Chrome'],
    viewport: VIEWPORTS[name].viewport,
    deviceScaleFactor: 1,
    isMobile: VIEWPORTS[name].isMobile,
    hasTouch: VIEWPORTS[name].hasTouch,
    userAgent: VIEWPORTS[name].userAgent ?? devices['Desktop Chrome'].userAgent,
  },
});

export default defineConfig({
  testDir: '.',
  outputDir: '../../test-results',
  snapshotPathTemplate: '{testDir}/visual/__snapshots__/{projectName}/{arg}{ext}',
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
      // Per-pixel colour threshold (Playwright default); no pixel budget:
      // baselines are rendered in the same pinned container as CI.
      threshold: 0.2,
      maxDiffPixels: 0,
    },
  },
  reporter: [
    ['list'],
    ['html', { outputFolder: '../../playwright-report', open: 'never' }],
    ['json', { outputFile: '../../test-results/results.json' }],
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
    visualProject('desktop', true),
    visualProject('tablet', false),
    visualProject('phone', false),
    visualProject('kiosk', true),
  ],
});
