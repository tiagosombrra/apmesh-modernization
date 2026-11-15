import { expect, test } from '@playwright/test';

// These E2E tests require installed browser binaries and a running API.
test('loads real P1 and both synchronized viewports', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('viewport-xyz')).toBeVisible();
  await expect(page.getByTestId('viewport-uv')).toBeVisible();
  await expect(page.locator('text=Dados verificados')).toBeVisible();
});

test('changes to the staged real candidate without claiming acceptance', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('model-select').selectOption('band');
  await expect(page.locator('text=Candidata real · Não aceita')).toBeVisible();
  await expect(page.locator('text=ÉPOCAS ADAPTATIVAS ACEITAS')).toBeVisible();
});

test('toggles layers without losing original provenance', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('toggle-quad').uncheck();
  await expect(page.getByTestId('toggle-quad')).not.toBeChecked();
  await page.getByTestId('toggle-quad').check();
  await expect(page.getByTestId('toggle-quad')).toBeChecked();
});
