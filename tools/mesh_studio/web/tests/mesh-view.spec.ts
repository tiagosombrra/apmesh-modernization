import { expect, test } from '@playwright/test';

// These E2E tests require installed browser binaries and a running API.
test('loads real P1 and both synchronized viewports', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('viewport-xyz')).toBeVisible();
  await expect(page.getByTestId('viewport-uv')).toBeVisible();
  await expect(page.locator('text=Dados verificados')).toBeVisible();
  await expect(page.getByTestId('viewport-xyz').locator('canvas').first()).toBeVisible();
  await expect(page.getByTestId('viewport-uv').locator('canvas').first()).toBeVisible();
  await page.screenshot({ path: 'test-results/mesh-studio-r1.png', fullPage: true });
});

test('changes to the staged real candidate without claiming acceptance', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('model-select').selectOption('band');
  await expect(page.locator('text=Candidata real · Não aceita')).toBeVisible();
  await expect(page.getByText('ÉPOCAS ADAPTATIVAS ACEITAS', { exact: true })).toBeVisible();
});

test('toggles layers without losing original provenance', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('toggle-quad').uncheck();
  await expect(page.getByTestId('toggle-quad')).not.toBeChecked();
  await page.getByTestId('toggle-quad').check();
  await expect(page.getByTestId('toggle-quad')).toBeChecked();
});

test('picks one real source face in UV and updates the scientific inspector', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('viewport-uv').locator('canvas').first()).toBeVisible();
  const host = page.getByTestId('viewport-uv');
  const rect = await host.boundingBox();
  if (!rect) throw new Error('missing_uv_viewport');
  await host.click({ position: { x: rect.width / 2, y: rect.height / 2 } });
  await expect(page.getByText('ORIGINAL SOURCE FACE ID', { exact: true })).toBeVisible();
  await expect(page.locator('.face-id')).toContainText('#');
});

test('uses source-bound binary scenes rather than copying scientific JSON vertices', async ({ page }) => {
  const binaryPaths: string[] = [];
  page.on('response', (response) => {
    if (response.url().includes('/geometry.v2.bin?space=')) binaryPaths.push(response.url());
  });
  await page.goto('/');
  await expect(page.getByTestId('viewport-xyz').locator('canvas').first()).toBeVisible();
  await expect(page.getByTestId('viewport-uv').locator('canvas').first()).toBeVisible();
  // React's development StrictMode may intentionally repeat effect requests.
  expect(binaryPaths.filter((p) => p.includes('space=xyz')).length).toBeGreaterThanOrEqual(1);
  expect(binaryPaths.filter((p) => p.includes('space=uv')).length).toBeGreaterThanOrEqual(1);
});

test('selects the exact same original source face in both viewports', async ({ page }) => {
  await page.goto('/');
  const host = page.getByTestId('viewport-uv');
  await expect(host.locator('canvas').first()).toBeVisible();
  const bounds = await host.boundingBox();
  if (!bounds) throw new Error('missing_uv_viewport');
  await host.click({ position: { x: bounds.width / 2, y: bounds.height / 2 } });
  const original = await page.locator('.face-id').innerText();
  await expect(page.getByTestId('selected-xyz')).toHaveText(`Face ${original}`);
  await expect(page.getByTestId('selected-uv')).toHaveText(`Face ${original}`);
  await page.getByTestId('toggle-edges').uncheck();
  await expect(page.locator('.face-id')).toHaveText(original);
  await page.getByTestId('toggle-edges').check();
  await expect(page.locator('.face-id')).toHaveText(original);
});

test('camera state remains stable across filter toggles and is tied to source SHA', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('save-cameras')).toBeEnabled();
  await page.getByTestId('save-cameras').click();
  await expect(page.getByTestId('camera-status')).toContainText('SHA-256');
  const original = await page.evaluate(() => {
    const key = Object.keys(localStorage).find((v) => v.startsWith('apmesh.meshstudio.camera.v1.'));
    if (!key) throw new Error('camera_key_missing');
    return { key, value: JSON.parse(localStorage.getItem(key)!) };
  });
  expect(original.value.camera_xyz.position).toHaveLength(3);
  expect(original.value.camera_uv.position).toHaveLength(3);
  await page.getByTestId('toggle-quad').uncheck();
  await page.getByTestId('toggle-quad').check();
  await page.getByTestId('toggle-edges').uncheck();
  await page.getByTestId('save-cameras').click();
  const after = await page.evaluate((key) => JSON.parse(localStorage.getItem(key)!), original.key);
  expect(after.camera_xyz.position).toEqual(original.value.camera_xyz.position);
  expect(after.camera_uv.position).toEqual(original.value.camera_uv.position);
  await page.getByTestId('reset-cameras').click();
  await page.getByTestId('restore-cameras').click();
  await expect(page.getByTestId('camera-status')).toContainText('restaurados');
  await page.evaluate((key) => {
    const record = JSON.parse(localStorage.getItem(key)!);
    record.source_sha256 = '0'.repeat(64);
    localStorage.setItem(key, JSON.stringify(record));
  }, original.key);
  await page.getByTestId('restore-cameras').click();
  await expect(page.getByTestId('camera-status')).toContainText('inválida');
});

test('does not restore a camera recipe from a different real source model', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('save-cameras').click();
  await page.getByTestId('model-select').selectOption('north');
  await expect(page.getByTestId('save-cameras')).toBeEnabled();
  await page.getByTestId('restore-cameras').click();
  await expect(page.getByTestId('camera-status')).toContainText('ausente');
});
