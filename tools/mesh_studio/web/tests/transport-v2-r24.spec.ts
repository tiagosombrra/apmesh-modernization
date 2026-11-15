import { expect, test } from '@playwright/test';

// These are source-bound byte-contract tests, NOT scientific mesh-quality proofs.
test('R2.4 V2 typed transfer matches verified real P1 original face IDs in both spaces', async ({ page }) => {
  await page.goto('/');
  const report = await page.evaluate(async () => {
    const { decodeGeometryV2 } = await import('/src/binaryGeometryV2.ts');
    const { meshFaceCount, meshFaceCorners, meshFaceIds, meshPointCount } =
      await import('/src/meshAccess.ts');
    const perSpace = [];
    for (const space of ['xyz', 'uv'] as const) {
      const response = await fetch(`/api/v1/models/p1/geometry.v2.bin?space=${space}`);
      if (!response.ok) throw new Error('real_v2_response_failed');
      const original = await (await fetch(`/api/v1/models/p1/geometry?space=${space}`)).json();
      const packed = decodeGeometryV2(await response.arrayBuffer(), space);
      const faceIds = Array.from(meshFaceIds(packed));
      perSpace.push({
        space,
        sourceMatches: packed.source_sha256 === original.source_sha256 &&
          response.headers.get('X-Source-SHA256') === packed.source_sha256,
        count: meshFaceCount(packed), points: meshPointCount(packed),
        originalIds: faceIds.join(',') === original.source_face_ids.join(','),
        exactNativeFaces: faceIds.every((_, i) =>
          meshFaceCorners(packed, i).join(',') === original.cells[i].join(',')),
        zeroNestedRehydration: packed.points.length === 0 && packed.cells.length === 0 &&
          packed.packed!.vertices instanceof Float32Array &&
          packed.packed!.polys instanceof Uint32Array,
      });
    }
    return perSpace;
  });
  for (const result of report) {
    expect(result.sourceMatches).toBe(true);
    expect(result.count).toBe(78);
    expect(result.points).toBeGreaterThan(0);
    expect(result.originalIds).toBe(true);
    expect(result.exactNativeFaces).toBe(true);
    expect(result.zeroNestedRehydration).toBe(true);
  }
});

test('R2.4 rejects CRC mismatch, truncated payload, mismatched coordinate space', async ({ page }) => {
  await page.goto('/');
  const validations = await page.evaluate(async () => {
    const { decodeGeometryV2 } = await import('/src/binaryGeometryV2.ts');
    const response = await fetch('/api/v1/models/p1/geometry.v2.bin?space=xyz');
    const bytes = await response.arrayBuffer();
    let badCrc = false;
    const changed = bytes.slice(0);
    new Uint8Array(changed)[changed.byteLength - 6] ^= 1;
    try { decodeGeometryV2(changed, 'xyz'); } catch { badCrc = true; }
    let truncated = false;
    try { decodeGeometryV2(bytes.slice(0, -1), 'xyz'); } catch { truncated = true; }
    let wrongSpace = false;
    try { decodeGeometryV2(bytes, 'uv'); } catch { wrongSpace = true; }
    return { badCrc, truncated, wrongSpace };
  });
  expect(validations).toEqual({ badCrc: true, truncated: true, wrongSpace: true });
});

test('R2.4 actual Mesh Studio P1 loads V2 and picks linked scientific face', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Dados verificados')).toBeVisible();
  await expect(page.getByTestId('viewport-xyz').locator('canvas').first()).toBeVisible();
  await expect(page.getByTestId('viewport-uv').locator('canvas').first()).toBeVisible();
  const uv = page.getByTestId('viewport-uv');
  const rect = await uv.boundingBox();
  if (!rect) throw new Error('missing_uv_canvas');
  await uv.click({ position: { x: rect.width/2, y: rect.height/2 } });
  await expect(page.locator('.face-id')).toContainText('#');
  const face = (await page.locator('.face-id').innerText()).trim();
  await expect(page.getByTestId('selected-xyz')).toContainText(face);
  await expect(page.getByTestId('selected-uv')).toContainText(face);
});

test('R2.4 500k packed fixture reuses original face IDs without 500k nested arrays', async ({ page }) => {
  test.setTimeout(120_000);
  await page.goto('/bench.html');
  const result = await page.evaluate(async () => {
    const { syntheticPackedScene } = await import('/src/syntheticPacked.ts');
    const { meshFaceCount, meshFaceCorners, meshPointCount } = await import('/src/meshAccess.ts');
    const { asVtkCells, vtkPointBuffer } = await import('/src/geometry.ts');
    const sample = syntheticPackedScene(500_000);
    const packed = sample.xyz.packed!;
    const draw = asVtkCells(sample.xyz, false, true);
    const reused = asVtkCells(sample.xyz, false, true);
    return {
      nfaces: meshFaceCount(sample.xyz),
      npoints: meshPointCount(sample.xyz),
      lastFace: meshFaceCorners(sample.xyz, 499_999),
      nativeQuadWords: draw.polys.length,
      sourceId: draw.sourceIds[499_999],
      noNestedObjects: sample.xyz.points.length === 0 && sample.xyz.cells.length === 0,
      reusedVtkWords: draw.polys === packed.polys && reused.polys === draw.polys,
      reusedPoints: vtkPointBuffer(sample.xyz) === packed.vertices,
      sameConnectBothViews: sample.uv.packed!.polys === packed.polys,
    };
  });
  expect(result.nfaces).toBe(500_000);
  expect(result.npoints).toBeGreaterThan(500_000);
  expect(result.lastFace).toHaveLength(4);
  expect(result.nativeQuadWords).toBe(2_500_000);
  expect(result.sourceId).toBe(499_999);
  expect(result.noNestedObjects).toBe(true);
  expect(result.reusedVtkWords).toBe(true);
  expect(result.reusedPoints).toBe(true);
  expect(result.sameConnectBothViews).toBe(true);
});
