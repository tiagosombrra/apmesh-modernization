import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';

// These tests exercise a real Chromium module Worker, not the Node-only BVH index.
test('R2.7 opt-in BVH worker keeps source buffers and resolves depth-aware face IDs', async ({ page }) => {
  await page.goto('/bench.html');
  const result = await page.evaluate(async () => {
    const { createXyzBvhWorker } = await import('/src/xyzBvhClient.ts');
    const packed = {
      vertices: new Float32Array([
        0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0,
        0, 0, 1, 1, 0, 1, 0, 1, 1,
      ]),
      polys: new Uint32Array([4, 0, 1, 2, 3, 3, 4, 5, 6]),
      offsets: new Uint32Array([0, 5, 9]),
      arities: new Uint8Array([4, 3]),
      faceIds: new Uint32Array([903, 11]),
    };
    const geometry = {
      schema: 'apmesh.meshstudio.browser_test.v1',
      source_sha256: '0'.repeat(64),
      source_patch_ownership: 'NOT_APMESH_SOURCE',
      coordinate_space: 'xyz' as const,
      points: [], cells: [], source_face_ids: [], cell_types: [],
      triangles: 1, quads: 1, warning: 'SYNTHETIC_TEST_ONLY',
      packed,
    };
    const sourceBefore = {
      vertices: Array.from(packed.vertices), faceIds: Array.from(packed.faceIds),
      polys: Array.from(packed.polys),
    };
    const client = createXyzBvhWorker(geometry);
    if (!client) throw new Error('BVH worker was not created for qualified planar fixture');
    try {
      const ready = await client.ready;
      if (!ready) return { ready, sourceBefore, sourceAfter: null };
      const front = await client.pick([0.23, 0.37, 3], [0.23, 0.37, -1], true, true);
      const quadOnly = await client.pick([0.23, 0.37, 3], [0.23, 0.37, -1], false, true);
      const fromBehind = await client.pick([0.23, 0.37, -1], [0.23, 0.37, 3], true, true);
      const boundary = await client.pick([0, 0.37, 3], [0, 0.37, -1], true, true);
      const hidden = await client.pick([0.23, 0.37, 3], [0.23, 0.37, -1], false, false);
      return {
        ready, front, quadOnly, fromBehind, boundary, hidden,
        sourceBefore,
        sourceAfter: {
          vertices: Array.from(packed.vertices), faceIds: Array.from(packed.faceIds),
          polys: Array.from(packed.polys),
        },
      };
    } finally {
      client.dispose();
    }
  });
  expect(result.ready).toBe(true);
  expect(result.sourceAfter).toEqual(result.sourceBefore);
  expect(result.front).toMatchObject({ kind: 'hit', sourceFaceId: 11 });
  expect(result.quadOnly).toMatchObject({ kind: 'hit', sourceFaceId: 903 });
  expect(result.fromBehind).toMatchObject({ kind: 'hit', sourceFaceId: 903 });
  expect(result.boundary).toMatchObject({ kind: 'ambiguous' });
  expect(result.hidden).toMatchObject({ kind: 'miss' });
});

test('R2.7 real P1 worker qualification is fail-closed and source-preserving', async ({ page }) => {
  await page.goto('/?xyzPicker=bvh');
  const xyz = page.getByTestId('viewport-xyz');
  await expect(xyz.locator('canvas').first()).toBeVisible();
  await expect.poll(() => xyz.getAttribute('data-bvh-ready'), { timeout: 25_000 })
    .toMatch(/^(true|false)$/);

  const appReady = await xyz.getAttribute('data-bvh-ready');
  const real = await page.evaluate(async () => {
    const { studyApi } = await import('/src/api.ts');
    const { createXyzBvhWorker } = await import('/src/xyzBvhClient.ts');
    const geometry = await studyApi.geometry('p1', 'xyz');
    const ids = Array.from(geometry.packed!.faceIds);
    const sourceSha = geometry.source_sha256;
    const client = createXyzBvhWorker(geometry);
    const qualified = client ? await client.ready : false;
    client?.dispose();
    return {
      qualified, sourceSha, sourceFaceCount: ids.length,
      sourceFaceIdsPreserved: ids.every((v, i) => geometry.packed!.faceIds[i] === v),
      typedCounts: [geometry.quads, geometry.triangles],
      originalBuffersAttached: (geometry.packed?.vertices.byteLength ?? 0) > 0,
    };
  });
  expect(real.sourceSha).toMatch(/^[0-9a-f]{64}$/);
  expect(real.sourceFaceCount).toBe(78);
  expect(real.typedCounts).toEqual([42, 36]);
  expect(real.sourceFaceIdsPreserved).toBe(true);
  expect(real.originalBuffersAttached).toBe(true);
  expect(appReady).toBe(String(real.qualified));
});

test('R2.7 original P1 XYZ click agrees with native VTK at the same pixel', async ({ page }, info) => {
  test.setTimeout(60_000);
  await page.goto('/?xyzPicker=bvh');
  const xyz = page.getByTestId('viewport-xyz');
  await expect(xyz.locator('canvas').first()).toBeVisible();
  await expect.poll(() => xyz.getAttribute('data-bvh-ready'), { timeout: 25_000 })
    .toMatch(/^(true|false)$/);
  const qualified = (await xyz.getAttribute('data-bvh-ready')) === 'true';
  const box = await xyz.boundingBox();
  if (!box) throw new Error('real_p1_xyz_bounds_missing');

  // A real source face must be selected; never accept a background miss as A/B evidence.
  const probes = [
    [0.50, 0.50], [0.46, 0.50], [0.54, 0.50],
    [0.50, 0.46], [0.50, 0.54], [0.42, 0.42],
    [0.58, 0.58], [0.58, 0.42], [0.42, 0.58],
  ];
  let selected: { x: number; y: number; id: number; method: string | null } | null = null;
  for (const [fx, fy] of probes) {
    const x = box.width * fx, y = box.height * fy;
    await xyz.click({ position: { x, y } });
    try {
      await expect(page.locator('.face-id')).toBeVisible({ timeout: 850 });
    } catch {
      continue;
    }
    const idText = await page.locator('.face-id').innerText();
    if (!/^#\d+$/.test(idText)) continue;
    selected = { x, y, id: Number(idText.slice(1)),
      method: await xyz.getAttribute('data-last-picker-method') };
    break;
  }
  expect(selected, 'A/B comparison requires a physical P1 source-face hit').not.toBeNull();
  expect(['VTK_CELL_PICKER', 'EXPERIMENTAL_XYZ_BVH_WORKER']).toContain(selected!.method);
  if (!qualified) expect(selected!.method).toBe('VTK_CELL_PICKER');

  const originalSha = await page.locator('.model-foot code').getAttribute('title');
  await page.goto('/');
  const native = page.getByTestId('viewport-xyz');
  await expect(native.locator('canvas').first()).toBeVisible();
  await native.click({ position: { x: selected!.x, y: selected!.y } });
  await expect(page.locator('.face-id')).toHaveText('#' + selected!.id, { timeout: 10_000 });
  expect(await native.getAttribute('data-last-picker-method')).toBe('VTK_CELL_PICKER');

  const receipt = {
    schema: 'apmesh.meshstudio.r27.real_p1_xyz_pick_ab.v1',
    classification: 'CONTROLLED_REAL_P1_UI_PICK_CONSISTENCY_NOT_GPU_PERFORMANCE',
    original_source_sha256: originalSha,
    original_source_face_id: selected!.id,
    opt_in_worker_qualified: qualified,
    opt_in_selection_method: selected!.method,
    reference_method: 'VTK_CELL_PICKER',
    same_source_face_id: true,
    same_relative_pixel: { x: selected!.x, y: selected!.y },
    caveats: [
      'single_sample_from_real_p1_not_full_geometric_or_patch_qualification',
      'vtk_cell_picker_is_a_behavioral_reference_not_scientific_surface_oracle',
      'hosted_chromium_not_real_windows_gpu_validation',
      'no_end_to_end_ui_paint_or_ram_vram_measurement',
    ],
  };
  await mkdir('test-results', { recursive: true });
  const json = JSON.stringify(receipt, null, 2) + '\n';
  await writeFile('test-results/r27-real-p1-xyz-pick-ab.json', json, 'utf8');
  await info.attach('r27-real-p1-xyz-pick-ab.json',
    { body: Buffer.from(json), contentType: 'application/json' });
  console.log('R27_REAL_P1_XYZ_AB=' + JSON.stringify(receipt));
});

test('R2.7.1 controlled real P1 indexes TRI only while curved QUAD remains VTK-owned', async ({ page }) => {
  await page.goto('/?xyzPicker=bvh');
  const xyz = page.getByTestId('viewport-xyz');
  await expect(xyz.locator('canvas').first()).toBeVisible();
  await expect.poll(() => xyz.getAttribute('data-bvh-ready'), { timeout: 25_000 }).toBe('true');
  expect(await xyz.getAttribute('data-bvh-indexed-faces')).toBe('36');
  expect(await xyz.getAttribute('data-bvh-excluded-quads')).toBe('42');
  const evidence = await page.evaluate(async () => {
    const { studyApi } = await import('/src/api.ts');
    const { createXyzBvhWorker } = await import('/src/xyzBvhClient.ts');
    const source = await studyApi.geometry('p1', 'xyz');
    const packed = source.packed!;
    const ownedVertexBytes = packed.vertices.byteLength;
    const originalIds = Array.from(packed.faceIds);
    const worker = createXyzBvhWorker(source);
    if (!worker || !await worker.ready) throw new Error('real_P1_tri_worker_not_ready');
    try {
      let tested = 0, matches = 0, mismatches = 0, visibleQuadFallback = 0;
      for (let face = 0; face < packed.faceIds.length; face += 1) {
        if (packed.arities[face] !== 3) continue;
        const start = packed.offsets[face];
        const point = (corner: number): [number, number, number] => {
          const id = packed.polys[start + 1 + corner] * 3;
          return [packed.vertices[id], packed.vertices[id + 1], packed.vertices[id + 2]];
        };
        const [a, b, c] = [point(0), point(1), point(2)];
        const centroid: [number, number, number] = [
          (a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3,
          (a[2] + b[2] + c[2]) / 3,
        ];
        const e = b.map((v,i) => v - a[i]), f = c.map((v,i) => v - a[i]);
        const normal = [e[1]*f[2]-e[2]*f[1], e[2]*f[0]-e[0]*f[2],
          e[0]*f[1]-e[1]*f[0]];
        const length = Math.hypot(...normal);
        if (length <= 1e-12) throw new Error('unexpected_degenerate_source_tri');
        const near = centroid.map((v,i) => v + normal[i] / length * .002) as [number,number,number];
        const far = centroid.map((v,i) => v - normal[i] / length * .002) as [number,number,number];
        const hit = await worker.pick(near,far,true,false);
        const fallback = await worker.pick(near,far,true,true);
        tested += 1;
        if (hit.kind === 'hit' && hit.sourceFaceId === packed.faceIds[face]) matches += 1;
        else mismatches += 1;
        if (fallback.kind === 'ambiguous') visibleQuadFallback += 1;
      }
      return {
        coverage: worker.coverage(),
        tested, matches, mismatches, visibleQuadFallback,
        originalSourceBufferIntact: packed.vertices.byteLength === ownedVertexBytes,
        originalIdsIntact: originalIds.every((v,i) => packed.faceIds[i] === v),
        sourceHash: source.source_sha256,
      };
    } finally {
      worker.dispose();
    }
  });
  expect(evidence.coverage).toEqual({
    sourceFaces: 78, indexedFaces: 36, excludedQuadFaces: 42,
  });
  expect(evidence.tested).toBe(36);
  expect(evidence.matches).toBe(36);
  expect(evidence.mismatches).toBe(0);
  expect(evidence.visibleQuadFallback).toBe(36);
  expect(evidence.originalSourceBufferIntact).toBe(true);
  expect(evidence.originalIdsIntact).toBe(true);
  expect(evidence.sourceHash).toBe(
    'cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0');
});
