import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';

interface Orbit { frames_completed: number; wall_elapsed_ms: number;
  scripted_orbit_throughput_fps: number; frame_wall_p95_ms: number; scope: string; }
interface Receipt { cells: number; points: number; displayed_cells: number;
  preview_mode: 'FULL_ORIGINAL_FACES' | 'SPARSE_ORIGINAL_FACE_SUBSET_NOT_LOD';
  source_coverage: number; orbit_run_sequence: number;
  scripted_camera_orbit: { xyz: Orbit; uv: Orbit } | null;
  last_picker_call: { hit: boolean; source_face_id: number | null; picker_wall_ms: number; method: string } | null; }

async function getReceipt(page: import('@playwright/test').Page): Promise<Receipt | null> {
  const raw = await page.getByTestId('benchmark-receipt').innerText();
  return raw.trim() ? JSON.parse(raw) as Receipt | null : null;
}

async function sceneReady(page: import('@playwright/test').Page, rendered: number): Promise<void> {
  await expect.poll(async () => (await getReceipt(page))?.displayed_cells ?? 0,
    { timeout: 180_000 }).toBe(rendered);
  await expect(page.getByTestId('benchmark-status'))
    .toContainText('As duas cenas foram renderizadas', { timeout: 180_000 });
}

async function orbitRepeated(page: import('@playwright/test').Page, repeat: number): Promise<Array<{xyz: Orbit; uv: Orbit}>> {
  const samples: Array<{xyz: Orbit; uv: Orbit}> = [];
  for (let i = 1; i <= repeat; i += 1) {
    await page.getByTestId('benchmark-run-motion').click();
    await expect.poll(async () => (await getReceipt(page))?.orbit_run_sequence ?? 0,
      { timeout: 180_000 }).toBe(i);
    const current = await getReceipt(page);
    const orbit = current?.scripted_camera_orbit;
    expect(orbit).not.toBeNull();
    expect(orbit?.xyz.frames_completed).toBe(24);
    expect(orbit?.uv.frames_completed).toBe(24);
    expect(orbit?.xyz.scope).toContain('NOT_GPU_PRESENT_FPS');
    samples.push({xyz: orbit!.xyz, uv: orbit!.uv});
  }
  return samples;
}

function summarize(values: number[]) {
  const sorted = [...values].sort((a, b) => a - b);
  return { min: sorted[0], median: sorted[Math.floor(sorted.length / 2)], max: sorted[sorted.length - 1],
    samples: values };
}

test('R2.5 sparse preview preserves exact original QUAD source IDs and explicitly rejects LOD claim', async ({ page }) => {
  await page.goto('/bench.html');
  const result = await page.evaluate(async () => {
    const { syntheticPackedScene } = await import('/src/syntheticPacked.ts');
    const { sourceFacePreviewPair } = await import('/src/sourceFacePreview.ts');
    const { asVtkCells } = await import('/src/geometry.ts');
    const fixture = syntheticPackedScene(50_000);
    const pair = sourceFacePreviewPair(fixture.xyz, fixture.uv, 5_000);
    const g = pair.xyz.packed!;
    const original = fixture.xyz.packed!;
    const actualId = g.faceIds[4999];
    const originalIndex = Math.floor(4999 * 50_000 / 5_000);
    const origOffset = original.offsets[originalIndex];
    const faceOffset = g.offsets[4999];
    const connectivityEqual = Array.from(g.polys.subarray(faceOffset, faceOffset + 5)).join(',') ===
      Array.from(original.polys.subarray(origOffset, origOffset + 5)).join(',');
    const reusedVertices = g.vertices === original.vertices;
    const sameSourceMapping = g.faceIds === pair.uv.packed!.faceIds &&
      Array.from(g.polys).join(',') === Array.from(pair.uv.packed!.polys).join(',');
    const render = asVtkCells(pair.xyz, true, true);
    const trulyOriginal = render.sourceIds[4999] === original.faceIds[originalIndex];
    const differentUv = { ...fixture.uv, packed: { ...fixture.uv.packed!,
      polys: fixture.uv.packed!.polys.slice() } };
    // One face uses a distinct local UV vertex ID without changing original face ID.
    const firstUv = differentUv.packed.polys[1];
    differentUv.packed.polys[1] = differentUv.packed.polys[2];
    differentUv.packed.polys[2] = firstUv;
    const uvPair = sourceFacePreviewPair(fixture.xyz, differentUv, 5_000);
    const acceptsDistinctUvIndices = uvPair.uv.packed!.polys[1] === differentUv.packed.polys[1] &&
      uvPair.xyz.packed!.polys[1] !== uvPair.uv.packed!.polys[1];
    let failClosed = false;
    try { sourceFacePreviewPair(fixture.xyz, { ...fixture.uv, source_sha256: 'f'.repeat(64) }, 5000); }
    catch { failClosed = true; }
    return { actualId, originalId: original.faceIds[originalIndex], connectivityEqual,
      reusedVertices, sameSourceMapping, trulyOriginal, acceptsDistinctUvIndices, failClosed,
      coverage: pair.provenance.coverage_fraction,
      isLod: pair.provenance.is_lod, complete: pair.provenance.complete_surface,
      metricComparable: pair.provenance.scientific_quality_comparable };
  });
  expect(result.actualId).toBe(result.originalId);
  expect(result.connectivityEqual).toBe(true);
  expect(result.reusedVertices).toBe(true);
  expect(result.sameSourceMapping).toBe(true);
  expect(result.trulyOriginal).toBe(true);
  expect(result.failClosed).toBe(true);
  expect(result.acceptsDistinctUvIndices).toBe(true);
  expect(result.coverage).toBe(0.1);
  expect(result.isLod).toBe(false);
  expect(result.complete).toBe(false);
  expect(result.metricComparable).toBe(false);
});

test('R2.5 opt-in repeated 500k viewer orbit, selection and partial-preview resource gate',
  async ({ page, context }, testInfo) => {
    test.skip(process.env.APMESH_R25_500K !== '1', 'R2.5 controlled 500k is opt-in and not a routine science gate');
    test.setTimeout(300_000);
    const cdp = await context.newCDPSession(page);
    await cdp.send('Performance.enable');
    const heap = async () => {
      const metrics = (await cdp.send('Performance.getMetrics')).metrics;
      const entries = Object.fromEntries(metrics.map(x => [x.name, x.value]));
      return { used_js_heap_bytes: entries.JSHeapUsedSize ?? null,
        allocated_js_heap_bytes: entries.JSHeapTotalSize ?? null,
        dom_nodes: entries.Nodes ?? null };
    };
    await page.goto('/bench.html');
    await page.getByTestId('benchmark-cells').selectOption('500000');
    await sceneReady(page, 500_000);
    expect((await getReceipt(page))?.cells).toBe(500_000);
    const heapBefore = await heap();
    const complete = await orbitRepeated(page, 3);
    const uv = page.getByTestId('viewport-uv');
    const rect = await uv.boundingBox();
    if (!rect) throw new Error('missing_uv_screen');
    await uv.click({ position: { x: rect.width * .473, y: rect.height * .519 } });
    await expect.poll(async () => (await getReceipt(page))?.last_picker_call?.hit ?? false,
      { timeout: 90_000 }).toBe(true);
    const picker = (await getReceipt(page))!.last_picker_call;
    expect(picker?.source_face_id).not.toBeNull();
    expect(picker?.picker_wall_ms).toBeGreaterThanOrEqual(0);
    await expect(page.getByTestId('selected-xyz')).toContainText(`Face #${picker?.source_face_id}`);
    await expect(page.getByTestId('selected-uv')).toContainText(`Face #${picker?.source_face_id}`);
    const heapFull = await heap();
    await page.getByTestId('benchmark-preview').check();
    await sceneReady(page, 50_000);
    const partialReceipt = await getReceipt(page);
    expect(partialReceipt?.cells).toBe(500_000);
    expect(partialReceipt?.source_coverage).toBe(.1);
    expect(partialReceipt?.preview_mode).toBe('SPARSE_ORIGINAL_FACE_SUBSET_NOT_LOD');
    const partial = await orbitRepeated(page, 3);
    const heapPreview = await heap();
    const record = {
      schema: 'apmesh.meshstudio.r25.controlled_chromium.v1',
      classification: 'SYNTHETIC_RENDERING_AND_ORIGINAL_FACE_SUBSET_NOT_APMESH_GENERATOR',
      source_hash: '0'.repeat(64), original_cells: 500_000,
      rendered_full_cells: 500_000, rendered_subset_cells: 50_000,
      subset_coverage: .1, subset_is_lod: false, subset_is_complete_surface: false,
      timings: {
        full_xyz_scripted_fps: summarize(complete.map(x=>x.xyz.scripted_orbit_throughput_fps)),
        full_uv_scripted_fps: summarize(complete.map(x=>x.uv.scripted_orbit_throughput_fps)),
        preview_xyz_scripted_fps: summarize(partial.map(x=>x.xyz.scripted_orbit_throughput_fps)),
        preview_uv_scripted_fps: summarize(partial.map(x=>x.uv.scripted_orbit_throughput_fps)),
        full_xyz_p95_ms: summarize(complete.map(x=>x.xyz.frame_wall_p95_ms)),
        preview_xyz_p95_ms: summarize(partial.map(x=>x.xyz.frame_wall_p95_ms)),
      },
      full_view_picker: picker,
      memory: { before: heapBefore, after_full: heapFull, after_partial: heapPreview,
        scope: 'CDP_JS_HEAP_ONLY_NOT_TOTAL_PROCESS_RAM_OR_VRAM' },
      limitations: ['single_runner_three_repeated_scripted_orbits_not_independent_GPU_replicates',
        'not_presented_FPS_or_human_navigation_latency',
        'partial_preview_has_holes_and_does_not_cover_source_surface',
        'partial_preview_cannot_support_mesh_quality_or_anisotropy_claims',
        'no_scientific_multi_patch_lineage_or_500k_native_generator_evidence',
        'real_Windows_GPU_and_memory_monitoring_still_open'],
    };
    const body = JSON.stringify(record, null, 2) + String.fromCharCode(10);
    await mkdir('test-results', { recursive: true });
    await writeFile('test-results/r25-500k-controlled-navigation.json', body, 'utf8');
    await testInfo.attach('r25-500k-controlled-navigation.json', { body: Buffer.from(body), contentType: 'application/json' });
    console.log('R25_500K_NAVIGATION=' + JSON.stringify({
      full_xyz: record.timings.full_xyz_scripted_fps.median,
      full_uv: record.timings.full_uv_scripted_fps.median,
      partial_xyz: record.timings.preview_xyz_scripted_fps.median,
      partial_uv: record.timings.preview_uv_scripted_fps.median,
      picked_source_id: picker?.source_face_id,
      native_js_heap_bytes: heapFull.used_js_heap_bytes,
    }));
  });
