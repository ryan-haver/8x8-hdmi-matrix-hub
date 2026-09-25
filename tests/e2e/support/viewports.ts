// The four capture viewports from docs/REMEDIATION_PLAN.md §5.3.
// deviceScaleFactor is 1 everywhere to keep the baselines small.
export const VIEWPORTS = {
  desktop: {
    viewport: { width: 1440, height: 900 },
    isMobile: false,
    hasTouch: false,
    userAgent: undefined as string | undefined,
  },
  tablet: {
    // iPad-class landscape.
    viewport: { width: 1024, height: 768 },
    isMobile: false,
    hasTouch: true,
    userAgent: undefined as string | undefined,
  },
  phone: {
    // iPhone 12-15 class portrait.
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true,
    userAgent:
      'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
  },
  kiosk: {
    // TODO: update to the real kiosk device resolution when known (§5.3
    // "kiosk device resolution"); 1280x800 is a common wall-tablet size.
    viewport: { width: 1280, height: 800 },
    isMobile: false,
    hasTouch: true,
    userAgent: undefined as string | undefined,
  },
} as const;

export type ViewportName = keyof typeof VIEWPORTS;
