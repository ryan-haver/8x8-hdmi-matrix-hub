// Kiosk Control PIN Security E2E Tests (Phase 3 WP-F1).
// Verifies:
// - Kiosk loads with zero prompts when no CONTROL_PIN is configured.
// - When control_pin is configured, Kiosk prompts for Control PIN,
//   unlocks with remembered-device cookie (orei_device_token), executes route switch,
//   and remains unlocked across page reload without re-prompting.
// - Cleans up control_pin after execution.

import { expect, openKiosk, preparePage, settle, test } from './support/ui';
import { hubApi } from './support/stack';
import type { Page } from '@playwright/test';

async function enterKioskPin(page: Page, digits: string) {
  for (const d of digits) {
    await page.locator(`#passcodeModal [data-digit="${d}"]`).click();
  }
  await page.locator('#passcodeOkBtn').click();
}

test.describe('Kiosk Control PIN Security (Phase 3 WP-F1)', () => {
  test.afterEach(async ({ sim }, testInfo) => {
    // Ensure control_pin is cleared and simulator is reset after each test
    const hub = await hubApi(`10.250.${testInfo.workerIndex % 250}.254`);
    try {
      await hub.post('/api/auth/pin', { data: { level: 'control', pin: null } });
    } catch {
      // Ignore if hub is not reachable during teardown
    } finally {
      await hub.dispose();
    }
    await sim.reset();
  });

  test('Kiosk loads with zero prompts when no PIN is configured', async ({ page }) => {
    await preparePage(page);
    await openKiosk(page);

    // Passcode modal must not be displayed
    await expect(page.locator('#passcodeModal')).not.toHaveClass(/show/);
    await expect(page.locator('#passcode-modal')).not.toHaveClass(/show/);

    // Kiosk elements are interactive with 8 inputs and connected status
    await expect(page.locator('#kioskGrid .kiosk-btn')).toHaveCount(8);
    await expect(page.locator('#statusText')).toHaveText('Connected');

    // "Full UI" link exists and points to /ui
    const fullUiLink = page.locator('a.kiosk-settings-btn[href="/ui"]');
    await expect(fullUiLink).toBeVisible();
    await expect(fullUiLink).toHaveAttribute('href', '/ui');
  });

  test('When control_pin is set, Kiosk prompts for PIN, unlocks with orei_device_token cookie, executes switch, and stays unlocked on reload', async ({
    page,
    sim,
  }, testInfo) => {
    const hub = await hubApi(`10.250.${testInfo.workerIndex % 250}.35`);
    try {
      // 1. Set CONTROL_PIN on the hub
      const setPinRes = await hub.post('/api/auth/pin', {
        data: { level: 'control', pin: '5678' },
      });
      expect(setPinRes.ok()).toBeTruthy();

      const authStatus = await (await hub.get('/api/auth/status')).json();
      expect(authStatus.control_pin_set).toBe(true);

      // 2. Open Kiosk - should prompt for Control PIN
      await preparePage(page);
      await openKiosk(page);

      // Passcode modal should automatically appear
      await expect(page.locator('#passcodeModal')).toHaveClass(/show/);
      await expect(page.locator('#passcode-modal')).toHaveClass(/show/);
      await expect(page.locator('#passcodeModalTitle')).toContainText(/PIN|Passcode/i);
      await expect(page.locator('#passcodeInstruction')).toContainText(/Control PIN/i);

      // 3. Enter wrong PIN first to verify error handling
      const wrongPinPromise = page.waitForResponse(
        (r) => r.url().endsWith('/api/auth/unlock') && r.status() === 401
      );
      await enterKioskPin(page, '0000');
      await wrongPinPromise;
      await expect(page.locator('#kioskToast')).toHaveText(/Incorrect PIN/i);
      await expect(page.locator('#passcodeModal')).toHaveClass(/show/);

      // 4. Enter correct PIN (5678)
      const unlockPromise = page.waitForResponse(
        (r) => r.url().endsWith('/api/auth/unlock') && r.status() === 200
      );
      await enterKioskPin(page, '5678');
      await unlockPromise;

      // Modal should close upon successful unlock
      await expect(page.locator('#passcodeModal')).not.toHaveClass(/show/);
      await expect(page.locator('#passcode-modal')).not.toHaveClass(/show/);

      // 5. Verify the remembered-device cookie (orei_device_token) is set
      const cookies = await page.context().cookies();
      const deviceTokenCookie = cookies.find((c) => c.name === 'orei_device_token');
      expect(deviceTokenCookie, 'orei_device_token cookie must be set on unlock').toBeDefined();
      expect(deviceTokenCookie?.value).toBeTruthy();
      expect(deviceTokenCookie?.httpOnly).toBe(true);

      // 6. Execute a route switch (Input 5 -> All Outputs)
      await page.locator('#kioskGrid .kiosk-btn').nth(4).click(); // Input 5
      await page.locator('#routeToAllBtn').click();
      await page.locator('#routingApplyBtn').click();

      // Verify the matrix state switched to Input 5 for all outputs
      await expect
        .poll(async () => (await sim.state()).outputs.map((o) => o.source), { timeout: 10_000 })
        .toEqual([5, 5, 5, 5, 5, 5, 5, 5]);

      // 7. Reload page - verify it remains unlocked across page reload without re-prompting
      await page.reload();
      await settle(page, 600);

      await expect(page.locator('#kioskGrid .kiosk-btn')).toHaveCount(8);
      await expect(page.locator('#statusText')).toHaveText('Connected');

      // No passcode prompt on reload
      await expect(page.locator('#passcodeModal')).not.toHaveClass(/show/);
      await expect(page.locator('#passcode-modal')).not.toHaveClass(/show/);

      // Further route switch works without prompts
      await page.locator('#kioskGrid .kiosk-btn').nth(1).click(); // Input 2
      await page.locator('#routeToAllBtn').click();
      await page.locator('#routingApplyBtn').click();

      await expect
        .poll(async () => (await sim.state()).outputs.map((o) => o.source), { timeout: 10_000 })
        .toEqual([2, 2, 2, 2, 2, 2, 2, 2]);
      await expect(page.locator('#passcodeModal')).not.toHaveClass(/show/);
    } finally {
      // 8. Clean up by clearing control_pin
      await hub.post('/api/auth/pin', { data: { level: 'control', pin: null } });
      await hub.dispose();
    }
  });

  test('Mutating action prompts for Control PIN if not yet unlocked, then retries and succeeds', async ({
    page,
    sim,
  }, testInfo) => {
    const hub = await hubApi(`10.250.${testInfo.workerIndex % 250}.36`);
    try {
      // Set CONTROL_PIN
      await hub.post('/api/auth/pin', { data: { level: 'control', pin: '4321' } });

      await preparePage(page);
      await openKiosk(page);

      // Dismiss the initial prompt by clicking Cancel
      await expect(page.locator('#passcodeModal')).toHaveClass(/show/);
      await page.locator('#passcodeCancelBtn').click();
      await expect(page.locator('#passcodeModal')).not.toHaveClass(/show/);

      // Attempt a route switch
      await page.locator('#kioskGrid .kiosk-btn').nth(3).click(); // Input 4
      await page.locator('#routeToAllBtn').click();
      await page.locator('#routingApplyBtn').click();

      // Mutating apiCall should trigger the Control PIN prompt
      await expect(page.locator('#passcodeModal')).toHaveClass(/show/);

      // Enter the PIN to unlock and allow the action to retry
      const unlockPromise = page.waitForResponse(
        (r) => r.url().endsWith('/api/auth/unlock') && r.status() === 200
      );
      await enterKioskPin(page, '4321');
      await unlockPromise;
      await expect(page.locator('#passcodeModal')).not.toHaveClass(/show/);

      // Verify the route switch executed after unlock
      await expect
        .poll(async () => (await sim.state()).outputs.map((o) => o.source), { timeout: 10_000 })
        .toEqual([4, 4, 4, 4, 4, 4, 4, 4]);

      // Verify device cookie is set
      const cookies = await page.context().cookies();
      expect(cookies.some((c) => c.name === 'orei_device_token')).toBe(true);
    } finally {
      await hub.post('/api/auth/pin', { data: { level: 'control', pin: null } });
      await hub.dispose();
    }
  });
});
