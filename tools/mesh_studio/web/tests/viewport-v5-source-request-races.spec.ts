import { expect, test } from '@playwright/test';

test('V5 rapid model switches abort obsolete source streams without stale geometry', async ({ page }) => {
  let reachedBandEndpoint = 0;
  let releaseFirstInterception: (() => void) | undefined;
  const firstBandRequestCompleted = new Promise<void>((resolve) => {
    releaseFirstInterception = resolve;
  });

  await page.goto('/');
  await expect(page.getByTestId('viewport-xyz').locator('canvas').first()).toBeVisible();
  await expect(page.getByTestId('viewport-uv').locator('canvas').first()).toBeVisible();
  await expect(page.locator('.main-status')).toHaveText('Dados verificados');

  await page.route('**/api/v1/models/band/geometry.v2.bin?space=*', async (route) => {
    reachedBandEndpoint += 1;
    // Deliberately keep an older source request alive during a model switch.
    await new Promise((resolve) => setTimeout(resolve, 650));
    try {
      await route.continue();
    } catch {
      // An aborted browser fetch may have disposed this intercepted route.
    } finally {
      releaseFirstInterception?.();
    }
  });

  const pendingBand = page.waitForRequest(
    (request) => request.url().includes('/api/v1/models/band/geometry.v2.bin?space='),
  );
  await page.getByTestId('model-select').selectOption('band');
  await pendingBand;
  await page.getByTestId('model-select').selectOption('p1');
  await expect(page.locator('.main-status')).toHaveText('Dados verificados');
  await firstBandRequestCompleted;

  // A late Band response must never replace the source-verified P1 display.
  await expect(page.getByTestId('model-select')).toHaveValue('p1');
  await expect(page.locator('.main-status')).toHaveText('Dados verificados');
  await expect(page.locator('.main-content [role="alert"]')).toHaveCount(0);
  await expect(page.getByTestId('viewport-xyz').locator('canvas').first()).toBeVisible();
  await expect(page.getByTestId('viewport-uv').locator('canvas').first()).toBeVisible();
  expect(reachedBandEndpoint).toBeGreaterThanOrEqual(1);
});

test('V5 interrupted original source-face inspection cannot survive model change', async ({ page }) => {
  let intercepts = 0;
  await page.goto('/');
  await expect(page.getByTestId('viewport-uv').locator('canvas').first()).toBeVisible();

  await page.route('**/api/v1/models/p1/faces/*', async (route) => {
    intercepts += 1;
    await new Promise((resolve) => setTimeout(resolve, 600));
    try {
      await route.continue();
    } catch {
      // Expected when the source-scoped AbortController cancels the request.
    }
  });
  const requested = page.waitForRequest(
    (request) => request.url().includes('/api/v1/models/p1/faces/'),
  );
  const host = page.getByTestId('viewport-uv');
  const bounds = await host.boundingBox();
  if (!bounds) throw new Error('missing_source_uv_viewport');
  await host.click({ position: { x: bounds.width / 2, y: bounds.height / 2 } });
  await requested;
  await page.getByTestId('model-select').selectOption('band');
  await expect(page.locator('.main-status')).toHaveText('Dados verificados');
  await expect(page.locator('.face-id')).toHaveCount(0);
  await expect(page.getByText('Selecione uma face', { exact: true })).toBeVisible();
  expect(intercepts).toBeGreaterThanOrEqual(1);
});
