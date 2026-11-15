import { expect, test } from '@playwright/test';

// These measurements are synthetic browser visualization observations only.
test('R2: renderer completes 1k and 50k QUAD and maintains filter control', async ({ page }) => {
  test.setTimeout(180_000);
  await page.goto('/bench.html');
  await expect(page.getByTestId('benchmark-status')).toContainText('As duas cenas foram renderizadas', { timeout: 60_000 });
  await expect(page.getByTestId('viewport-xyz').locator('canvas').first()).toBeVisible();
  await expect(page.getByTestId('viewport-uv').locator('canvas').first()).toBeVisible();
  const first = JSON.parse(await page.getByTestId('benchmark-receipt').innerText()) as {
    cells: number; synthetic: boolean; xyz_first_render_ms: number; uv_first_render_ms: number;
  };
  expect(first.cells).toBe(1_000);
  expect(first.synthetic).toBe(true);
  expect(first.xyz_first_render_ms).toBeGreaterThan(0);
  expect(first.uv_first_render_ms).toBeGreaterThan(0);
  await page.getByTestId('benchmark-cells').selectOption('50000');
  await expect(page.getByTestId('benchmark-status')).toContainText('As duas cenas foram renderizadas', { timeout: 150_000 });
  const second = JSON.parse(await page.getByTestId('benchmark-receipt').innerText()) as {
    cells: number; points: number; synthetic: boolean; render_scope: string;
    xyz_first_render_ms: number; uv_first_render_ms: number;
    gpu_memory_bytes: null; frame_rate_fps: null;
  };
  expect(second.cells).toBe(50_000);
  expect(second.points).toBeGreaterThan(50_000);
  expect(second.synthetic).toBe(true);
  expect(second.xyz_first_render_ms).toBeGreaterThan(0);
  expect(second.uv_first_render_ms).toBeGreaterThan(0);
  expect(second.gpu_memory_bytes).toBeNull();
  expect(second.frame_rate_fps).toBeNull();
  expect(second.render_scope).toContain('SYNTHETIC');
  await page.getByTestId('benchmark-quad-filter').uncheck();
  await expect(page.getByTestId('benchmark-quad-filter')).not.toBeChecked();
  await page.getByTestId('benchmark-quad-filter').check();
  await expect(page.getByTestId('benchmark-quad-filter')).toBeChecked();
  await page.getByTestId('benchmark-edge-filter').check();
  await expect(page.getByTestId('benchmark-edge-filter')).toBeChecked();
  const receipt = await page.getByTestId('benchmark-receipt').innerText();
  await page.evaluate((text) => {
    const blob = new Blob([text], { type: 'application/json' });
    // Keep JSON diagnostic local in the browser, with no network upload.
    if (!blob.size) throw new Error('empty_benchmark_receipt');
  }, receipt);
});
