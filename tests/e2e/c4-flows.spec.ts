// WP-C4: saved profile conflicts and wait-step editing through the shipped UI.
import { expect, openUi, preparePage, test } from './support/ui';
import { hubApi } from './support/stack';

test('WP-C4: edit a scene, reject an invalid wait, save a valid wait', async ({ page }) => {
  const hub = await hubApi('10.250.0.42');
  const before = (await (await hub.get('/api/v2/scenes/scene_goodnight01')).json()).data.scene;
  try {
    await preparePage(page);
    await openUi(page);
    await page.evaluate(() => { window.location.hash = '#settings/scenes'; });
    await page.locator('#settings-drawer .edit-scene-btn[data-id="scene_goodnight01"]').click();
    await expect(page.locator('#scene-editor-modal')).toHaveClass(/open/);
    await expect(page.locator('#settings-drawer')).not.toHaveClass(/open/);
    await page.locator('#scene-editor-name').fill('Good Night with wait');
    await page.locator('#add-wait-step-btn').click();
    const waitEditor = page.locator('.editor-shell');
    await page.getByLabel('Wait duration in seconds').fill('31');
    await waitEditor.getByRole('button', { name: 'Save', exact: true }).click();
    await expect(waitEditor.getByRole('alert')).toContainText('Wait must be between 0.5 and 30 seconds');
    await expect(page.locator('#scene-steps-list .step-item')).toHaveCount(2);
    await page.getByLabel('Wait duration in seconds').fill('0.5');
    await waitEditor.getByRole('button', { name: 'Save', exact: true }).click();
    await expect(waitEditor).toHaveCount(0);
    await expect(page.locator('#scene-steps-list')).toContainText('0.5 seconds');
    await expect(page.locator('#scene-editor-name')).toHaveValue('Good Night with wait');
    const saved = page.waitForResponse((r) => r.request().method() === 'PUT' && r.url().endsWith('/api/v2/scenes/scene_goodnight01'));
    await page.locator('#scene-editor-save').click();
    expect((await saved).status()).toBe(200);
    const scene = (await (await hub.get('/api/v2/scenes/scene_goodnight01')).json()).data.scene;
    expect(scene.name).toBe('Good Night with wait');
    expect(scene.steps[2]).toEqual({ type: 'wait', id: '', params: { seconds: 0.5 } });
  } finally {
    await hub.put('/api/v2/scenes/scene_goodnight01', { data: before });
    await hub.dispose();
  }
});

test('WP-C4: removing a wait removes exactly one step after repeated editor renders', async ({ page }) => {
  await preparePage(page);
  await openUi(page);
  await page.evaluate(() => { window.location.hash = '#settings/scenes'; });
  await page.locator('#settings-drawer .edit-scene-btn[data-id="scene_goodnight01"]').click();
  await page.locator('#scene-editor-modal.open').waitFor();
  await page.locator('#add-wait-step-btn').click();
  await page.getByLabel('Wait duration in seconds').fill('0.5');
  await page.locator('.editor-shell').getByRole('button', { name: 'Save', exact: true }).click();
  await page.locator('#add-macro-step-btn').click();
  await page.getByRole('combobox').fill('macro_volume_up');
  await page.getByRole('combobox').press('Enter');
  await expect(page.locator('#scene-steps-list .step-item')).toHaveCount(4);
  await page.locator('.remove-step-btn[data-index="2"]').click();
  await expect(page.locator('#scene-steps-list .step-item')).toHaveCount(3);
  await expect(page.locator('#scene-steps-list')).toContainText('Soundbar Volume +3');
});
