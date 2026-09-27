// The capture viewports from docs/REMEDIATION_PLAN.md §5.3: desktop, tablet,
// phone, plus one project per real kiosk device the owner uses (owner
// decision 2026-09-25: kiosk devices vary; these two are the test devices).
//
// deviceScaleFactor is 1 except where a kiosk device's real ratio is known;
// screenshots are taken at CSS scale (`scale: 'css'` in playwright.config.ts),
// so every baseline is viewport-sized regardless of the ratio.
import { devices } from '@playwright/test';

type Viewport = {
  viewport: { width: number; height: number };
  /** Physical screen size in CSS pixels (window.screen), when it differs from the viewport. */
  screen?: { width: number; height: number };
  deviceScaleFactor: number;
  isMobile: boolean;
  hasTouch: boolean;
  userAgent: string | undefined;
};

const IPHONE_16_PRO_MAX = devices['iPhone 16 Pro Max'];

export const VIEWPORTS = {
  desktop: {
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
    isMobile: false,
    hasTouch: false,
    userAgent: undefined,
  },
  tablet: {
    // iPad-class landscape.
    viewport: { width: 1024, height: 768 },
    deviceScaleFactor: 1,
    isMobile: false,
    hasTouch: true,
    userAgent: undefined,
  },
  phone: {
    // iPhone 12-15 class portrait.
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 1,
    isMobile: true,
    hasTouch: true,
    userAgent:
      'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
  },
  'kiosk-tab-a11': {
    // Samsung Galaxy Tab A11 (SM-X133), 8.7", 1340x800 panel, landscape,
    // Android Chrome.
    // PROVISIONAL: the browser's CSS viewport is not confirmed; this uses the
    // panel resolution at deviceScaleFactor 1. Confirm with
    // whatismyviewport.com on the device (in the kiosk browser mode actually
    // used), then update viewport/deviceScaleFactor here and re-baseline this
    // project (`npm run visual:update -- --project=kiosk-tab-a11`).
    viewport: { width: 1340, height: 800 },
    deviceScaleFactor: 1,
    isMobile: true,
    hasTouch: true,
    // Android tablets' Chrome omits the "Mobile" token; Chromium version as in
    // Playwright 1.63's Android device descriptors.
    userAgent:
      'Mozilla/5.0 (Linux; Android 15; SM-X133) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.8010.12 Safari/537.36',
  },
  'kiosk-iphone16promax': {
    // Apple iPhone 16 Pro Max, portrait. User agent, screen and scale factor
    // from Playwright 1.63's "iPhone 16 Pro Max" descriptor. Its viewport
    // (440x763) is Safari with the browser bars showing; the kiosk uses the
    // full 440x956 CSS screen (owner decision 2026-09-25, source: the
    // webmobilefirst.com device list, 440x956 @3x), as when the page runs
    // full screen from the home screen. Rendered by Chromium like every
    // other project (the descriptor's defaultBrowserType is not used).
    viewport: { width: 440, height: 956 },
    screen: IPHONE_16_PRO_MAX.screen,
    deviceScaleFactor: IPHONE_16_PRO_MAX.deviceScaleFactor,
    isMobile: IPHONE_16_PRO_MAX.isMobile,
    hasTouch: IPHONE_16_PRO_MAX.hasTouch,
    userAgent: IPHONE_16_PRO_MAX.userAgent,
  },
} satisfies Record<string, Viewport>;

export type ViewportName = keyof typeof VIEWPORTS;

/** The real kiosk devices (one Playwright project each). */
export const KIOSK_VIEWPORTS = ['kiosk-tab-a11', 'kiosk-iphone16promax'] as const satisfies readonly ViewportName[];

/** Viewports that also capture the @themed entries in the other three presets (§5.3). */
export const THEMED_VIEWPORTS = ['desktop', ...KIOSK_VIEWPORTS] as const satisfies readonly ViewportName[];

/** Every visual project, in gallery/CI order. */
export const VISUAL_VIEWPORTS = Object.keys(VIEWPORTS) as ViewportName[];
