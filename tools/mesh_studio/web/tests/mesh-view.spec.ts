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
