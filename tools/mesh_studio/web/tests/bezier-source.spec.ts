import { expect, test } from '@playwright/test';
import type { Page } from '@playwright/test';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const EXAMPLE_PATH = fileURLToPath(new URL('../src/fixtures/four_sheet_curved.bp', import.meta.url));
const EXAMPLE_BYTES = readFileSync(EXAMPLE_PATH);
const EXAMPLE_SHA256 = 'b1b6610b63f10dfe91e84fc8de85d8cbb8b9bdb50a7b0ecdbc95efd89b64fdd4';

async function openExample(page: Page) {
  await page.goto('/?workspace=bezier');
  await expect(page.getByTestId('bezier-control-count')).toHaveText('52');
  await expect(page.getByTestId('bezier-viewport').locator('canvas').first()).toBeVisible();
}

async function setParameterToPointTwo(page: Page) {
  const slider = page.getByTestId('bezier-parameter');
  await expect(slider).toHaveValue('0.25');
  await slider.focus();
  // Exercise the real range input through its keyboard interaction.
  for (let step = 0; step < 5; step += 1) await slider.press('ArrowLeft');
  await expect(page.getByTestId('bezier-t')).toHaveText('0.20');
}

function duplicateSharedControlIds(): Buffer {
  const lines = EXAMPLE_BYTES.toString('utf8').trimEnd().split('\n');
  const controls = lines.filter(line => line.startsWith('v '));
  const firstPatch = lines.findIndex(line => line.startsWith('p '));
  const patches = lines.slice(firstPatch);
  // Retain every coordinate token while giving P1 four distinct control IDs.
  patches[1] = patches[1].split(/\s+/).map((token, index) =>
    index > 0 && Number(token) < 4 ? String(52 + Number(token)) : token).join(' ');
  return Buffer.from([...lines.slice(0, firstPatch), ...controls.slice(0, 4), ...patches].join('\n') + '\n');
}

test('opens the authenticated Four-Sheet source with its real browser preview', async ({ page }) => {
  const errors: string[] = [];
  const apiRequests: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => { if (request.url().includes('/api/')) apiRequests.push(request.url()); });
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  expect(createHash('sha256').update(EXAMPLE_BYTES).digest('hex')).toBe(EXAMPLE_SHA256);
  await openExample(page);
  await expect(page.getByTestId('workspace-bezier')).toHaveAttribute('aria-current', 'page');
  await expect(page.getByTestId('bezier-patch-count')).toHaveText('4');
  await expect(page.getByTestId('bezier-curve-count')).toHaveText('13');
  await expect(page.getByTestId('bezier-max-incidence')).toHaveText('4');
  await expect(page.getByTestId('bezier-provenance')).toHaveText('Matches the Four-Sheet reference');
  await expect(page.getByTestId('bezier-sha256')).toHaveText(EXAMPLE_SHA256);
  await expect(page.getByTestId('bezier-viewport')).toHaveAttribute('data-source-patches', '4');
  await expect(page.getByText('Display triangles are only a rendering approximation.', { exact: false })).toBeVisible();
  expect(errors).toEqual([]);
  expect(apiRequests).toEqual([]);
});

test('normalizes extreme finite coordinates before rendering without changing source identity', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await openExample(page);
  const vertices = Array.from({ length: 16 }, (_, index) =>
    `v ${((index % 4) / 3 - 0.5) * 1e308} ${(Math.floor(index / 4) / 3 - 0.5) * 1e308} 0`);
  const bytes = Buffer.from([...vertices, `p ${Array.from({ length: 16 }, (_, index) => index).join(' ')}`].join('\n'));
  await page.getByTestId('bezier-file').setInputFiles({ name: 'extreme.bp', mimeType: 'text/plain', buffer: bytes });
  await expect(page.getByTestId('bezier-filename')).toHaveText('extreme.bp');
  await expect(page.getByTestId('bezier-control-count')).toHaveText('16');
  await expect(page.getByTestId('bezier-viewport')).toHaveAttribute('data-source-patches', '1');
  await expect(page.getByTestId('bezier-viewport').locator('canvas').first()).toBeVisible();
  await expect(page.getByTestId('bezier-sha256')).toHaveText(createHash('sha256').update(bytes).digest('hex'));
  await expect(page.getByRole('alert')).toHaveCount(0);
  expect(errors).toEqual([]);
});

test('ignores a stale file read when a newer import finishes first', async ({ page }) => {
  await openExample(page);
  await page.evaluate((oldLength) => {
    const original = File.prototype.arrayBuffer;
    const digest = crypto.subtle.digest.bind(crypto.subtle);
    const state = window as unknown as { releaseOldRead?: () => void; oldDigestFinished?: Promise<void> };
    let completed!: () => void;
    state.oldDigestFinished = new Promise<void>(resolve => { completed = resolve; });
    crypto.subtle.digest = async (algorithm, data) => {
      const result = await digest(algorithm, data);
      if (data.byteLength === oldLength) completed();
      return result;
    };
    File.prototype.arrayBuffer = async function () {
      if (this.name === 'old-source.bp') await new Promise<void>(resolve => { state.releaseOldRead = resolve; });
      return original.call(this);
    };
  }, EXAMPLE_BYTES.byteLength);
  await page.getByTestId('bezier-file').setInputFiles({ name: 'old-source.bp', mimeType: 'text/plain', buffer: EXAMPLE_BYTES });
  const newer = Buffer.concat([EXAMPLE_BYTES, Buffer.from('// New selected source\n')]);
  await page.getByTestId('bezier-file').setInputFiles({ name: 'new-source.bp', mimeType: 'text/plain', buffer: newer });
  await expect(page.getByTestId('bezier-filename')).toHaveText('new-source.bp');
  await page.evaluate(async () => {
    const state = window as unknown as { releaseOldRead: () => void; oldDigestFinished: Promise<void> };
    state.releaseOldRead();
    await state.oldDigestFinished;
    // Wait for the stale continuation and React's commit, not an arbitrary timer.
    await new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
  });
  await expect(page.getByTestId('bezier-sha256')).toHaveText(createHash('sha256').update(newer).digest('hex'));
  await expect(page.getByTestId('bezier-filename')).toHaveText('new-source.bp');
});

test('maps canonical t onto reversed P1 and changes rendered patch visibility', async ({ page }) => {
  await openExample(page);
  await page.getByTestId('bezier-incidence-1-3').getByRole('button').click();
  await expect(page.getByTestId('bezier-incidence-1-3')).toContainText('Reversed');
  await expect(page.getByTestId('bezier-local-t')).toHaveText('local t = 0.75');
  await setParameterToPointTwo(page);
  await expect(page.getByTestId('bezier-local-t')).toHaveText('local t = 0.80');
  const pointLabel = await page.getByTestId('bezier-point').innerText();
  expect(pointLabel).toMatch(/^C\(t\) = \([^)]+\)$/);
  const coordinates = pointLabel.match(/^C\(t\) = \(([^)]+)\)$/)![1].split(',').map(Number);
  // These values come from the authored analytic spine at t = 0.2.
  expect(coordinates[0]).toBeCloseTo(0.064, 10);
  expect(coordinates[1]).toBeCloseTo(-0.0288, 10);
  expect(coordinates[2]).toBeCloseTo(-1.5, 10);
  const canvas = page.getByTestId('bezier-viewport').locator('canvas').first();
  const visibleImage = await canvas.screenshot();
  await page.getByTestId('bezier-patch-2').uncheck();
  await expect(page.getByTestId('bezier-patch-2')).not.toBeChecked();
  await expect.poll(async () => (await canvas.screenshot()).equals(visibleImage)).toBe(false);
  await page.getByTestId('bezier-patch-2').check();
  await expect(page.getByTestId('bezier-patch-2')).toBeChecked();
});

test('exports all sixteen declared incidences with source hash and observation scope', async ({ page }) => {
  await openExample(page);
  const pendingDownload = page.waitForEvent('download');
  await page.getByTestId('bezier-export').click();
  const download = await pendingDownload;
  expect(download.suggestedFilename()).toBe(`bezier_source_${EXAMPLE_SHA256.slice(0, 12)}_incidences.csv`);
  const path = await download.path();
  if (!path) throw new Error('Incidence CSV was not downloaded.');
  const [header, ...rows] = readFileSync(path, 'utf8').trimEnd().split('\n').map(line => line.split(','));
  expect(header).toEqual(['source_sha256', 'topology_basis', 'curve_id', 'control_ids',
    'patch_count', 'patch_id', 'side', 'reversed', 'orientation_ambiguous']);
  expect(rows).toHaveLength(16);
  expect(rows.every(row => row[0] === EXAMPLE_SHA256 && row[1] === 'DECLARED_BP_CONTROL_IDS')).toBe(true);
  expect(new Set(rows.map(row => row[2])).size).toBe(13);
  const shared = rows.filter(row => row[4] === '4');
  expect(shared).toHaveLength(4);
  expect(shared.every(row => row[3] === '0 1 2 3')).toBe(true);
  expect(shared.map(row => row[5]).sort()).toEqual(['0', '1', '2', '3']);
  expect(shared.find(row => row[5] === '1')?.slice(6)).toEqual(['3', 'true', 'false']);
});

test('rejects a malformed upload without stale inventory and recovers with the example', async ({ page }) => {
  await openExample(page);
  await page.getByTestId('bezier-file').setInputFiles({
    name: 'truncated.bp', mimeType: 'text/plain', buffer: Buffer.from('v 0 0 0\np 0\n'),
  });
  await expect(page.getByTestId('bezier-error')).toContainText('16 control indices');
  await expect(page.getByTestId('bezier-control-count')).toHaveCount(0);
  await expect(page.getByTestId('bezier-export')).toBeDisabled();
  await page.getByTestId('bezier-load-example').click();
  await expect(page.getByTestId('bezier-error')).toHaveCount(0);
  await expect(page.getByTestId('bezier-control-count')).toHaveText('52');
  await expect(page.getByTestId('bezier-curve-count')).toHaveText('13');
  await expect(page.getByTestId('bezier-export')).toBeEnabled();
});

test('keeps equal coordinates with duplicate control IDs topologically distinct', async ({ page }) => {
  await openExample(page);
  const bytes = duplicateSharedControlIds();
  await page.getByTestId('bezier-file').setInputFiles({
    name: 'duplicate-identities.bp', mimeType: 'text/plain', buffer: bytes,
  });
  await expect(page.getByTestId('bezier-control-count')).toHaveText('56');
  await expect(page.getByTestId('bezier-patch-count')).toHaveText('4');
  await expect(page.getByTestId('bezier-curve-count')).toHaveText('14');
  await expect(page.getByTestId('bezier-max-incidence')).toHaveText('3');
  await expect(page.getByTestId('bezier-incidence-1-3')).toHaveCount(0);
  await expect(page.getByTestId('bezier-provenance')).toHaveText('Local source · fingerprint calculated');
  await expect(page.getByTestId('bezier-sha256')).toHaveText(createHash('sha256').update(bytes).digest('hex'));
});

test('retains a local source and selected parameter across workspace navigation and browser back', async ({ page }) => {
  await openExample(page);
  const bytes = Buffer.concat([EXAMPLE_BYTES, Buffer.from('// Local review copy; no native generation.\n')]);
  await page.getByTestId('bezier-file').setInputFiles({
    name: 'local-review.bp', mimeType: 'text/plain', buffer: bytes,
  });
  await expect(page.getByTestId('bezier-filename')).toHaveText('local-review.bp');
  await expect(page.getByTestId('bezier-provenance')).toHaveText('Local source · fingerprint calculated');
  await expect(page.getByTestId('bezier-sha256')).toHaveText(createHash('sha256').update(bytes).digest('hex'));
  await expect(page.getByRole('link', { name: 'View the pinned source' })).toHaveCount(0);
  await page.getByTestId('bezier-incidence-1-3').getByRole('button').click();
  await setParameterToPointTwo(page);
  await page.getByTestId('bezier-patch-2').uncheck();
  await page.getByTestId('workspace-native').click();
  await expect(page).toHaveURL(/workspace=native/);
  await expect(page.getByRole('heading', { name: 'Eistute & Book', exact: true })).toBeVisible();
  await page.goBack();
  await expect(page).toHaveURL(/workspace=bezier/);
  await expect(page.getByTestId('bezier-filename')).toHaveText('local-review.bp');
  await expect(page.getByTestId('bezier-local-t')).toHaveText('local t = 0.80');
  await expect(page.getByTestId('bezier-patch-2')).not.toBeChecked();
  await expect(page.getByTestId('bezier-viewport').locator('canvas').first()).toBeVisible();
  await page.getByTestId('workspace-mesh').click();
  await expect(page.getByTestId('viewport-uv').locator('canvas').first()).toBeVisible();
  await page.goBack();
  await expect(page.getByTestId('bezier-filename')).toHaveText('local-review.bp');
  await expect(page.getByTestId('bezier-t')).toHaveText('0.20');
});

test('shows pending integrity during geometry loading and unavailable after failure', async ({ page }) => {
  let release!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  await page.route('**/api/v1/models/*/geometry.v2.bin?*', async route => {
    await gate;
    await route.abort('failed');
  });
  await page.goto('/?workspace=mesh');
  const integrity = page.getByTestId('mesh-integrity');
  await expect(integrity).toHaveAttribute('data-state', 'pending');
  await expect(integrity).not.toContainText('SHA-256 conferido');
  release();
  await expect(integrity).toHaveAttribute('data-state', 'unavailable');
  await expect(integrity).toHaveText('Source verification unavailable');
  await expect(integrity).not.toContainText('SHA-256 conferido');
});

test('does not retain a verified integrity label after a late catalog failure', async ({ page }) => {
  let release!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  await page.route('**/api/v1/models', async route => {
    await gate;
    await route.abort('failed');
  });
  await page.goto('/?workspace=mesh');
  await expect(page.getByTestId('viewport-uv').locator('canvas').first()).toBeVisible();
  release();
  await expect(page.getByTestId('mesh-integrity')).toHaveAttribute('data-state', 'unavailable');
  await expect(page.getByTestId('mesh-integrity')).not.toContainText('SHA-256 conferido');
});

test('selects a specific side when one patch uses the same declared curve twice', async ({ page }) => {
  await openExample(page);
  // This deliberately repeated boundary is an inspection control, not an admitted model.
  const vertices = Array.from({ length: 16 }, (_, index) => `v ${index % 4} ${Math.floor(index / 4)} 0`);
  const bytes = Buffer.from([...vertices, 'p 0 1 2 3 1 5 6 7 2 9 10 11 3 13 14 15'].join('\n') + '\n');
  await page.getByTestId('bezier-file').setInputFiles({
    name: 'repeated-patch-side.bp', mimeType: 'text/plain', buffer: bytes,
  });
  await expect(page.getByTestId('bezier-max-incidence')).toHaveText('1');
  const bottom = page.getByTestId('bezier-incidence-0-0');
  const left = page.getByTestId('bezier-incidence-0-3');
  await bottom.getByRole('button').click();
  await expect(bottom).toHaveAttribute('data-selected', 'true');
  await expect(left).toHaveAttribute('data-selected', 'false');
  await expect(page.getByRole('img', { name: 'Patch 0 UV chart, v = 0', exact: true })).toBeVisible();
  await left.getByRole('button').click();
  await expect(left).toHaveAttribute('data-selected', 'true');
  await expect(bottom).toHaveAttribute('data-selected', 'false');
  await expect(page.getByRole('img', { name: 'Patch 0 UV chart, u = 0', exact: true })).toBeVisible();
});

test('keeps the source workspace within a 390px viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openExample(page);
  await expect(page.getByTestId('bezier-export')).toBeVisible();
  await expect(page.getByTestId('bezier-incidence-1-3')).toBeVisible();
  const dimensions = await page.evaluate(() => ({
    viewport: window.innerWidth,
    document: document.documentElement.scrollWidth,
    body: document.body.scrollWidth,
  }));
  expect(dimensions.document).toBeLessThanOrEqual(dimensions.viewport + 1);
  expect(dimensions.body).toBeLessThanOrEqual(dimensions.viewport + 1);
});
