import { expect, Page, test } from '@playwright/test';

async function waitForUiReady(page: Page): Promise<void> {
    await page.goto('/ui');
    await page.waitForFunction(() => Boolean((window as unknown as { api?: unknown }).api));
    await expect(page.locator('#inputs-grid .skeleton-card')).toHaveCount(0);
    await expect(page.locator('#outputs-grid .skeleton-card')).toHaveCount(0);
}

async function resetAuthState(page: Page, knownPins: string[] = ['2468', '1357', '9999']): Promise<void> {
    const statusRes = await page.request.get('/api/auth/status');
    if (!statusRes.ok()) return;
    const status = await statusRes.json();

    if (status.admin_pin_set) {
        for (const pin of knownPins) {
            const clearControl = await page.request.post('/api/auth/pin', {
                data: { level: 'control', pin: '', current_pin: pin },
            });
            const clearAdmin = await page.request.post('/api/auth/pin', {
                data: { level: 'admin', pin: '', current_pin: pin },
            });
            if (clearAdmin.ok() || clearControl.ok()) break;
        }
    } else if (status.control_pin_set) {
        await page.request.post('/api/auth/pin', {
            data: { level: 'control', pin: '' },
        });
    }
    await page.request.post('/api/auth/lock', { data: {} });
}

test.describe('Two-level security auth & Admin PIN UI lifecycle', () => {
    test.afterEach(async ({ page }) => {
        await resetAuthState(page);
    });

    test('sets Admin PIN, prompts and unlocks on UI admin action, locks session, requires unlock again, and clears PIN', async ({
        page,
    }) => {
        await resetAuthState(page);
        await waitForUiReady(page);

        // 1. Set an Admin PIN via /api/auth/pin
        const setPinRes = await page.request.post('/api/auth/pin', {
            data: { level: 'admin', pin: '2468' },
        });
        expect(setPinRes.status()).toBe(200);
        const setPinBody = await setPinRes.json();
        expect(setPinBody.admin_pin_set).toBe(true);

        // Verify session starts locked (level: none)
        const initialStatus = await (await page.request.get('/api/auth/status')).json();
        expect(initialStatus.admin_pin_set).toBe(true);
        expect(initialStatus.session_level).toBe('none');

        // 2. Open General Settings drawer in /ui and attempt an admin action (Test Matrix Connection)
        await page.locator('#menu-toggle').click();
        await page.locator('#side-nav-drawer.open').waitFor();
        await page.locator('#drawer-general-btn').click();
        await expect(page.locator('#general-drawer')).toHaveClass(/open/);
        await expect(page.locator('#general-auth-admin-pin-status')).toHaveText('Configured');
        await expect(page.locator('#general-auth-session-status')).toHaveText('Locked');

        // Queue dialog answer for the Admin PIN prompt
        const prompts: string[] = [];
        const onFirstDialog = async (dialog: import('@playwright/test').Dialog) => {
            prompts.push(dialog.message());
            await dialog.accept('2468');
        };
        page.once('dialog', onFirstDialog);

        const unlockResponsePromise = page.waitForResponse(
            (res) => res.url().includes('/api/auth/unlock') && res.request().method() === 'POST'
        );
        const testConnSuccessPromise = page.waitForResponse(
            (res) =>
                res.url().includes('/api/settings/test-connection') &&
                res.request().method() === 'POST' &&
                res.status() === 200
        );

        await page.locator('#general-matrix-host-test').click();

        const unlockRes = await unlockResponsePromise;
        expect(unlockRes.status()).toBe(200);
        const testConnRes = await testConnSuccessPromise;
        expect(testConnRes.status()).toBe(200);
        expect(prompts.length).toBe(1);
        expect(prompts[0]).toMatch(/admin pin/i);

        // Verify session is now unlocked as admin
        await expect(page.locator('#general-auth-session-status')).toHaveText('Admin unlocked');
        const unlockedStatus = await (await page.request.get('/api/auth/status')).json();
        expect(unlockedStatus.session_level).toBe('admin');

        // 3. Lock the session via the UI Lock Session button (POST /api/auth/lock)
        await page.locator('#general-auth-lock-btn').click();
        await expect(page.locator('#general-auth-session-status')).toHaveText('Locked');

        const lockedStatus = await (await page.request.get('/api/auth/status')).json();
        expect(lockedStatus.session_level).toBe('none');

        // Verify admin routes require unlocking again (dismissing prompt rejects with admin_pin_required)
        page.once('dialog', async (dialog) => {
            prompts.push(dialog.message());
            await dialog.dismiss();
        });

        const rejectedErr = await page.evaluate(async () => {
            const w = window as unknown as {
                api: { post: (path: string, body: Record<string, unknown>) => Promise<unknown> };
            };
            try {
                await w.api.post('/api/settings/test-connection', {});
                return null;
            } catch (e: unknown) {
                const err = e as { name?: string; status?: number; code?: string; level?: string };
                return {
                    name: err.name,
                    status: err.status,
                    code: err.code,
                    level: err.level,
                };
            }
        });
        expect(rejectedErr).toEqual({
            name: 'ApiError',
            status: 401,
            code: 'admin_pin_required',
            level: 'admin',
        });
        expect(prompts.length).toBe(2);

        // Unlock again on retry when user supplies PIN
        page.once('dialog', async (dialog) => {
            prompts.push(dialog.message());
            await dialog.accept('2468');
        });
        const retryResult = await page.evaluate(async () => {
            const w = window as unknown as {
                api: { post: (path: string, body: Record<string, unknown>) => Promise<{ success?: boolean }> };
            };
            return w.api.post('/api/settings/test-connection', {});
        });
        expect(retryResult?.success).toBe(true);
        expect(prompts.length).toBe(3);

        // 4. Clear the Admin PIN at test end via the UI Remove Admin PIN button
        await page.locator('#general-admin-pin-clear').click();
        await expect(page.locator('#general-auth-admin-pin-status')).toHaveText('Not set');
        await expect(page.locator('#general-auth-session-status')).toHaveText('Open');

        const finalStatus = await (await page.request.get('/api/auth/status')).json();
        expect(finalStatus.admin_pin_set).toBe(false);
        expect(finalStatus.control_pin_set).toBe(false);
    });

    test('manages Control PIN, remembered devices, and API keys with escaped names in General Drawer', async ({
        page,
    }) => {
        await resetAuthState(page);
        await waitForUiReady(page);

        await page.locator('#menu-toggle').click();
        await page.locator('#side-nav-drawer.open').waitFor();
        await page.locator('#drawer-general-btn').click();
        await expect(page.locator('#general-drawer')).toHaveClass(/open/);

        // Set Control PIN via General Settings drawer UI
        await page.locator('#general-control-pin-input').fill('1357');
        await page.locator('#general-control-pin-save').click();
        await expect(page.locator('#general-auth-control-pin-status')).toHaveText('Configured');

        // Trigger a control action via RunAction.runProfileOrScene while session is locked;
        // verify it prompts for Control PIN, unlocks with remember_device: true, and retries
        page.once('dialog', async (dialog) => {
            await dialog.accept('1357');
        });
        const recallOutcome = await page.evaluate(async () => {
            const w = window as unknown as {
                state?: { profiles?: Array<{ id: string; name: string }> };
                RunAction: {
                    runProfileOrScene: (
                        kind: 'profile' | 'scene',
                        id: string,
                        opts?: { name?: string }
                    ) => Promise<{ status: string }>;
                };
            };
            const firstProfile = w.state?.profiles?.[0] || { id: 'movie_night', name: 'Movie Night' };
            return w.RunAction.runProfileOrScene('profile', firstProfile.id, { name: firstProfile.name });
        });
        expect(['ok', 'partial']).toContain(recallOutcome.status);

        // Refresh drawer auth lists and verify remembered device appears and can be revoked
        await page.evaluate(() =>
            (window as unknown as { generalDrawer: { loadAuthStatus: () => Promise<void> } }).generalDrawer.loadAuthStatus()
        );
        const revokeDeviceBtn = page.locator('#general-auth-devices-list [data-revoke-device-id]').first();
        await expect(revokeDeviceBtn).toBeVisible();
        await revokeDeviceBtn.click();
        await expect(page.locator('#general-auth-devices-list')).toContainText('No remembered devices');

        // Create an API key with special HTML characters to verify Helpers.escapeHtml escaping
        await page.locator('#general-api-key-name-input').fill('<script>Key</script>');
        await page.locator('#general-api-key-create-btn').click();
        await expect(page.locator('#general-api-key-created-value')).toBeVisible();
        await expect(page.locator('#general-api-keys-list')).toContainText('<script>Key</script>');

        // Revoke the API key
        const revokeKeyBtn = page.locator('#general-api-keys-list [data-revoke-key-id]').first();
        await expect(revokeKeyBtn).toBeVisible();
        await revokeKeyBtn.click();
        await expect(page.locator('#general-api-keys-list')).toContainText('No API keys');

        // Clear Control PIN via UI
        await page.locator('#general-control-pin-clear').click();
        await expect(page.locator('#general-auth-control-pin-status')).toHaveText('Not set');
    });
});
