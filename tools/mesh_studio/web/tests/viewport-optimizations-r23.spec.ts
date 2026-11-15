import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';

test('R2.3 reuses typed vertex/cell buffers and preserves original source face IDs', async ({ page }) => {
  await page.goto('/bench.html');
  const audit = await page.evaluate(async () => {
    const geometry = await import('/src/geometry.ts');
    const g = {
      schema: 'apmesh.meshstudio.web.v1', source_sha256: '0'.repeat(64),
      source_patch_ownership: 'NOT_APMESH_SOURCE', coordinate_space: 'uv',
      points: [[0,0,0],[1,0,0],[1,1,0],[0,1,0],[2,0,0],[2,1,0]],
      cells: [[0,1,2,3],[1,4,5,2]], source_face_ids: [41,87],
      cell_types: ['quad','quad'], triangles: 0, quads: 2, warning: 'synthetic fixture',
    } as import('/src/contracts.ts').MeshGeometry;
    const first = geometry.asVtkCells(g, true, true);
    const second = geometry.asVtkCells(g, true, true);
    const empty = geometry.asVtkCells(g, false, false);
    const again = geometry.asVtkCells(g, true, true);
    const stable = first === second && first === again &&
      first.points === geometry.vtkPointBuffer(g) && first.points === empty.points;
    const originalIDs = first.sourceIds.join(',') === '41,87';
    const exactElements = Array.from(first.polys).join(',') ===
      '4,0,1,2,3,4,1,4,5,2';
    const faceColors = first.colorBytes.length === 8;
    const closed = empty.polys.length === 0 && empty.sourceIds.length === 0;
    return { stable, originalIDs, exactElements, faceColors, closed };
  });
  expect(audit).toEqual({ stable: true, originalIDs: true, exactElements: true,
    faceColors: true, closed: true });
});

test('R2.3 spatial UV index is exact on nonoverlapping cells and refuses overlap', async ({ page }) => {
  await page.goto('/bench.html');
  const audit = await page.evaluate(async () => {
    const { buildUvSpatialIndex } = await import('/src/uvSpatialIndex.ts');
    const g = {
      schema: 'apmesh.meshstudio.web.v1', source_sha256: '0'.repeat(64),
      source_patch_ownership: 'NOT_APMESH_SOURCE', coordinate_space: 'uv',
      points: [[0,0,0],[1,0,0],[1,1,0],[0,1,0],[2,0,0],[2,1,0]],
      cells: [[0,1,2,3],[1,4,5,2]], source_face_ids: [41,87],
      cell_types: ['quad','quad'], triangles: 0, quads: 2, warning: 'synthetic fixture',
    } as import('/src/contracts.ts').MeshGeometry;
    const index = buildUvSpatialIndex(g)!;
    const a = index.pick(0.42, 0.49, true, true);
    const b = index.pick(1.42, 0.49, true, true);
    const filtered = index.pick(0.42, 0.49, true, false);
    const edge = index.pick(1, 0.4, true, true);
    const exterior = index.pick(-1, 0.4, true, true);
    const overlap = buildUvSpatialIndex({ ...g, cells: [[0,1,2,3],[0,1,2,3]] })!;
    return { a,b,filtered,edge,exterior,overlap:overlap.pick(0.42,0.49,true,true) };
  });
  expect(audit.a).toMatchObject({ kind: 'hit', sourceFaceId: 41 });
  expect(audit.b).toMatchObject({ kind: 'hit', sourceFaceId: 87 });
  expect(audit.filtered.kind).toBe('miss');
  expect(audit.edge.kind).toBe('ambiguous');
  expect(audit.exterior.kind).toBe('miss');
  expect(audit.overlap.kind).toBe('ambiguous');
});

test('R2.3 50k UV face picking preserves scientific IDs and records selected algorithm',
  async ({ page }, testInfo) => {
    test.setTimeout(180_000);
    await page.goto('/bench.html');
    await page.getByTestId('benchmark-cells').selectOption('50000');
    await expect.poll(async () => {
      const raw = await page.getByTestId('benchmark-receipt').innerText();
      const data = raw.trim() ? JSON.parse(raw) as { cells?: number } | null : null;
      return data?.cells ?? 0;
    }, { timeout: 150_000 }).toBe(50_000);
    await expect(page.getByTestId('benchmark-status')).toContainText('As duas cenas foram renderizadas');
    const uv = page.getByTestId('viewport-uv');
    const rect = await uv.boundingBox();
    if (!rect) throw new Error('uv_viewport_missing');
    await uv.click({ position: { x: rect.width * 0.473, y: rect.height * 0.519 } });
    await expect.poll(async () => {
      const sample = JSON.parse(await page.getByTestId('benchmark-receipt').innerText()) as {
        last_picker_call?: { method?: string; source_face_id?: number | null };
      };
      return sample.last_picker_call?.source_face_id ?? null;
    }, { timeout: 30_000 }).not.toBeNull();
    const sample = JSON.parse(await page.getByTestId('benchmark-receipt').innerText());
    const picked = sample.last_picker_call;
    expect(picked.method).toBe('UV_SPATIAL_INDEX');
    expect(picked.source_face_id).toBeGreaterThanOrEqual(0);
    // Compare the native picker on exactly the same UV screen pixel and camera.
    await page.getByTestId('benchmark-native-picker').check();
    await uv.click({ position: { x: rect.width * 0.473, y: rect.height * 0.519 } });
    await expect.poll(async () => {
      const next = JSON.parse(await page.getByTestId('benchmark-receipt').innerText()) as {
        last_picker_call?: { method?: string };
      };
      return next.last_picker_call?.method;
    }, { timeout: 30_000 }).toBe('VTK_CELL_PICKER');
    const native = JSON.parse(await page.getByTestId('benchmark-receipt').innerText()).last_picker_call;
    expect(native.source_face_id).toBe(picked.source_face_id);

    await expect(page.getByTestId('selected-xyz')).toContainText(`Face #${picked.source_face_id}`);
    await expect(page.getByTestId('selected-uv')).toContainText(`Face #${picked.source_face_id}`);
    const report = {
      schema: 'apmesh.meshstudio.r23.viewer_optimization.v1',
      classification: 'SYNTHETIC_INTERACTION_NOT_GENERATOR_METRICS',
      sample_cells: sample.cells, point_count: sample.points,
      picker: picked,
      native_picker_same_camera: native,
      constraints: ['no_GPA_CPU_fps_benchmark', 'no_source_patch_inference',
        'index_never_welds_vertices', 'fallback_on_ambiguous_uv_chart',
        '500k_not_qualified', 'single_run_not_statistics'],
    };
    const text = JSON.stringify(report, null, 2) + '\n';
    await mkdir('test-results', { recursive: true });
    await writeFile('test-results/r23-50k-uv-picking.json', text, 'utf8');
    await testInfo.attach('r23-50k-uv-picking.json', {
      body: Buffer.from(text), contentType: 'application/json',
    });
    console.log('R23_50K_UV_PICK=' + JSON.stringify({
      method: picked.method, elapsed_ms: picked.picker_wall_ms,
      native_ms: native.picker_wall_ms, same_original_id: native.source_face_id === picked.source_face_id,
      tested: picked.spatial_candidates_tested, id: picked.source_face_id,
    }));
  });
