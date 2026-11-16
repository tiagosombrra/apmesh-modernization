import { expect, test } from '@playwright/test';

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
