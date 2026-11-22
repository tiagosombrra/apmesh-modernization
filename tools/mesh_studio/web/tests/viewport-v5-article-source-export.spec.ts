import { expect, test } from '@playwright/test';
import { createHash } from 'node:crypto';

test('V5 real P1 user exports audited UV vector art from the same selected original source', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('.main-status')).toHaveText('Dados verificados');
  const link = page.getByTestId('v5-source-uv-export');
  await expect(link).toBeVisible();
  await expect(link).toHaveAttribute('href', '/api/v1/models/p1/publication.svg');

  const [download] = await Promise.all([
    page.waitForEvent('download'),
    link.click(),
  ]);
  expect(download.suggestedFilename()).toBe(
    'apmesh_p1_cbf6cd6308ba_uv_source.svg');

  const response = await page.request.get('/api/v1/models/p1/publication.svg');
  expect(response.status()).toBe(200);
  expect(response.headers()['content-type']).toContain('image/svg+xml');
  const bytes = await response.body();
  expect(response.headers()['x-source-sha256']).toBe(
    'cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0');
  expect(response.headers()['x-vector-figure-sha256']).toBe(
    createHash('sha256').update(bytes).digest('hex'));
  const text = bytes.toString('utf8');
  expect(text).toContain('<svg');
  expect(text).toContain('CONTROLLED ORIGINAL');
  expect(text).not.toContain('<image');
  expect(text).toContain('scientific_lod_qualified');
});

test('V5 staged source publication can never look like accepted original adaptive epoch', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('model-select').selectOption('band');
  await expect(page.locator('.main-status')).toHaveText('Dados verificados');
  const link = page.getByTestId('v5-source-uv-export');
  await expect(link).toHaveAttribute('href', '/api/v1/models/band/publication.svg');
  const response = await page.request.get('/api/v1/models/band/publication.svg');
  expect(response.status()).toBe(200);
  expect(response.headers()['x-source-status']).toBe('STAGED_UNACCEPTED');
  const text = await response.text();
  expect(text).toContain('NOT AN ACCEPTED ADAPTIVE EPOCH');
  expect(text).toContain('scientific_lod_qualified');
});

test('V5 genuine original TRI study is discoverable and isolated from P1 by default', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('r2720-panel')).toHaveCount(0);
  const toggle = page.getByTestId('v5-toggle-native-tri');
  await expect(toggle).toBeVisible();
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-expanded', 'true');
  await expect(page.getByTestId('r2720-panel')).toBeVisible();
  await expect(page.getByTestId('r2720-empty')).toBeVisible();
  await expect(page.getByTestId('viewport-xyz')).toBeVisible();
  await toggle.click();
  await expect(page.getByTestId('r2720-panel')).toHaveCount(0);
  await page.goto('/?nativeScene=1');
  await expect(page.getByTestId('r2720-panel')).toBeVisible();
  await page.getByTestId('v5-toggle-native-tri').click();
  await expect(page.getByTestId('r2720-panel')).toHaveCount(0);
});

test('V5 read-only source viewer requests no external font or third-party network resources', async ({ page }) => {
  const external: string[] = [];
  page.on('request', (request) => {
    const address = new URL(request.url());
    if ((address.protocol === 'http:' || address.protocol === 'https:') &&
        address.hostname !== '127.0.0.1' && address.hostname !== 'localhost') {
      external.push(request.url());
    }
  });
  await page.goto('/');
  await expect(page.locator('.main-status')).toHaveText('Dados verificados');
  await expect(page.getByTestId('viewport-xyz').locator('canvas').first()).toBeVisible();
  await expect(page.getByTestId('viewport-uv').locator('canvas').first()).toBeVisible();
  expect(external).toEqual([]);
});

