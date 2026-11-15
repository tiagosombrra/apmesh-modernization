import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';

type Orbit = {
  frames_requested: number;
  frames_completed: number;
  wall_elapsed_ms: number;
  scripted_orbit_throughput_fps: number;
  frame_wall_p50_ms: number;
  frame_wall_p95_ms: number;
  frame_wall_max_ms: number;
  scope: string;
};
type Sample = {
  cells: number;
  synthetic: boolean;
  scripted_camera_orbit: {
    xyz: Orbit;
    uv: Orbit;
    heap_before_bytes: number | null;
    heap_after_bytes: number | null;
    heap_scope: string;
  } | null;
  last_picker_call: {
    space: 'xyz' | 'uv';
    source_face_id: number | null;
    hit: boolean;
    picker_wall_ms: number;
    scope: string;
  } | null;
};

async function stableReceipt(page: import('@playwright/test').Page, cells: number) {
  await expect.poll(async () => {
    const raw = await page.getByTestId('benchmark-receipt').innerText();
    const parsed = raw.trim() ? JSON.parse(raw) as Sample | null : null;
    return parsed?.cells ?? 0;
  }, { timeout: 150_000 }).toBe(cells);
  await expect(page.getByTestId('benchmark-status'))
    .toContainText('As duas cenas foram renderizadas', { timeout: 150_000 });
}

async function playwrightHeap(session: import('@playwright/test').CDPSession) {
  const response = await session.send('Performance.getMetrics') as {
    metrics: Array<{ name: string; value: number }>;
  };
  const vals = Object.fromEntries(response.metrics.map((v) => [v.name, v.value]));
  return {
    js_heap_used_bytes: vals.JSHeapUsedSize ?? null,
    js_heap_total_bytes: vals.JSHeapTotalSize ?? null,
    dom_nodes: vals.Nodes ?? null,
    scope: 'CHROMIUM_CDP_PERFORMANCE_METRICS_NOT_PROCESS_RAM_OR_GPU_MEMORY',
  };
}

test('R2.2: scripted orbit frame intervals and native vtkCellPicker latency at 50k synthetic QUAD',
  async ({ page }, testInfo) => {
    test.setTimeout(240_000);
    const cdp = await page.context().newCDPSession(page);
    await cdp.send('Performance.enable');
    await page.goto('/bench.html');
    await page.getByTestId('benchmark-cells').selectOption('50000');
    await stableReceipt(page, 50_000);
    const heapBefore = await playwrightHeap(cdp);
    await expect(page.getByTestId('benchmark-run-motion')).toBeEnabled();
    await page.getByTestId('benchmark-run-motion').click();
    await expect(page.getByTestId('benchmark-motion-status'))
      .toContainText('Medição concluída', { timeout: 150_000 });
    await expect.poll(async () => {
      const value = JSON.parse(await page.getByTestId('benchmark-receipt').innerText()) as Sample;
      return value.scripted_camera_orbit?.xyz.frames_completed ?? 0;
    }, { timeout: 150_000 }).toBe(24);

    const uv = page.getByTestId('viewport-uv');
    const rect = await uv.boundingBox();
    if (!rect) throw new Error('uv_viewport_not_found');
    await uv.click({ position: { x: rect.width / 2, y: rect.height / 2 } });
    await expect.poll(async () => {
      const value = JSON.parse(await page.getByTestId('benchmark-receipt').innerText()) as Sample;
      return value.last_picker_call?.hit ?? false;
    }, { timeout: 60_000 }).toBe(true);

    const receipt = JSON.parse(await page.getByTestId('benchmark-receipt').innerText()) as Sample;
    const xyz = receipt.scripted_camera_orbit?.xyz;
    const uvOrbit = receipt.scripted_camera_orbit?.uv;
    expect(receipt.synthetic).toBe(true);
    expect(receipt.cells).toBe(50_000);
    for (const orbit of [xyz, uvOrbit]) {
      expect(orbit).toBeTruthy();
      expect(orbit!.frames_completed).toBe(24);
      expect(orbit!.scripted_orbit_throughput_fps).toBeGreaterThan(0);
      expect(orbit!.frame_wall_p95_ms).toBeGreaterThanOrEqual(orbit!.frame_wall_p50_ms);
      expect(orbit!.scope).toContain('NOT_GPU_PRESENT_FPS');
    }
    expect(receipt.last_picker_call?.space).toBe('uv');
    expect(receipt.last_picker_call?.source_face_id).not.toBeNull();
    expect(receipt.last_picker_call!.picker_wall_ms).toBeGreaterThanOrEqual(0);
    expect(receipt.last_picker_call!.scope).toContain('NOT_END_TO_END_UI_LATENCY');
    const heapAfter = await playwrightHeap(cdp);
    expect(heapAfter.js_heap_used_bytes).toBeGreaterThan(0);
    const browserVersion = await page.evaluate(() => navigator.userAgent);
    const recorded = {
      schema: 'apmesh.meshstudio.r22.browser_interaction.v1',
      classification: 'SYNTHETIC_VIEWER_SCRIPTED_INTERACTION_NOT_APMESH_ALGORITHM_EVIDENCE',
      observed_on: 'Github Actions hosted Chromium; GPU model and RAM are not qualified',
      browser_user_agent: browserVersion,
      scene: { cells: receipt.cells, synthetic: receipt.synthetic },
      orbit_xyz: xyz,
      orbit_uv: uvOrbit,
      picker: receipt.last_picker_call,
      heap_before: heapBefore,
      heap_after: heapAfter,
      limitations: [
        'requestAnimationFrame_plus_render_wall_time_is_not_GPU_presented_FPS',
        'picking_measurement_excludes_React_commit_and_paint',
        'Chromium_CDP_heap_does_not_include_native_RAM_or_VRAM',
        'single_run_not_statistical_benchmark',
        '500k_not_automatically_qualified',
      ],
    };
    const bytes = JSON.stringify(recorded, null, 2) + '\n';
    await mkdir('test-results', { recursive: true });
    await writeFile('test-results/r22-50k-scripted-interaction.json', bytes, 'utf8');
    await testInfo.attach('r22-50k-scripted-interaction.json', {
      body: Buffer.from(bytes), contentType: 'application/json',
    });
    console.log('R22_SCRIPTED_50K=' + JSON.stringify({
      cells: receipt.cells,
      xyz_fps: xyz!.scripted_orbit_throughput_fps,
      uv_fps: uvOrbit!.scripted_orbit_throughput_fps,
      uv_pick_ms: receipt.last_picker_call?.picker_wall_ms,
      heap_before: heapBefore.js_heap_used_bytes,
      heap_after: heapAfter.js_heap_used_bytes,
    }));
  });

test('R2.2 optional bounded 500k synthetic browser stress, no physics or GPU certification',
  async ({ page }, testInfo) => {
    test.skip(process.env.APMESH_R22_500K !== '1', '500k stress is opt-in; not a routine CI gate');
    test.setTimeout(300_000);
    await page.goto('/bench.html');
    await page.getByTestId('benchmark-cells').selectOption('500000');
    await stableReceipt(page, 500_000);
    const sample = JSON.parse(await page.getByTestId('benchmark-receipt').innerText()) as Sample;
    expect(sample.synthetic).toBe(true);
    expect(sample.cells).toBe(500_000);
    const receipt = sample as Sample & {
      points: number; generation_ms: number; xyz_first_render_ms: number | null;
      uv_first_render_ms: number | null; render_scope: string;
    };
    expect(receipt.xyz_first_render_ms).toBeGreaterThan(0);
    expect(receipt.uv_first_render_ms).toBeGreaterThan(0);
    const session = await page.context().newCDPSession(page);
    await session.send('Performance.enable');
    const cdpm = await session.send('Performance.getMetrics');
    const metrics = Object.fromEntries(cdpm.metrics.map((v) => [v.name, v.value]));
    const evidence = {
      schema: 'apmesh.meshstudio.r24.synthetic500k_first_render.v1',
      classification: 'SYNTHETIC_TYPED_BUFFER_TWO_VIEW_FIRST_RENDER_NOT_APMESH_GENERATOR',
      source_sha256: '0'.repeat(64),
      cells: receipt.cells,
      points: receipt.points,
      xyz_first_render_ms: receipt.xyz_first_render_ms,
      uv_first_render_ms: receipt.uv_first_render_ms,
      synthetic_generation_ms: receipt.generation_ms,
      chrome_js_heap_used_bytes: metrics.JSHeapUsedSize ?? null,
      chrome_js_heap_total_bytes: metrics.JSHeapTotalSize ?? null,
      scope: receipt.render_scope,
      caveats: ['single_hosted_chromium_execution_not_statistical_replication',
        'first_render_callback_not_sustained_GPU_frame_presentation',
        'memory_excludes_process_native_RAM_and_VRAM',
        'not_a_source_APMesh_algorithm_run',
        'not_all_quad_generator_scientific_evidence',
        'no_adaptive_epoch_or_LOD_source_map_qualified'],
    };
    const body = JSON.stringify(evidence, null, 2) + String.fromCharCode(10);
    await mkdir('test-results', { recursive: true });
    await writeFile('test-results/r24-500k-typed-first-render.json', body, 'utf8');
    await testInfo.attach('r24-500k-typed-first-render.json', {
      body: Buffer.from(body), contentType: 'application/json',
    });
    console.log('R24_500K_TYPED=' + JSON.stringify({
      cells: evidence.cells, points: evidence.points,
      xyz_ms: evidence.xyz_first_render_ms, uv_ms: evidence.uv_first_render_ms,
      js_heap_bytes: evidence.chrome_js_heap_used_bytes,
    }));
  });
