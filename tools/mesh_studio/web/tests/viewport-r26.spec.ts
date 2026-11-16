import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';

/** No rendered aggregate is ever presented as a scientific LOD. */
test('R2.6 exact 500k source partition and reject duplicate, foreign and uncertified ownership', async ({ page }) => {
  await page.goto('/bench.html');
  const actual = await page.evaluate(async () => {
    const { syntheticPackedScene } = await import('/src/syntheticPacked.ts');
    const { syntheticGridFacePartition, verifyFacePartition } = await import('/src/sourceLodLineage.ts');
    const { buildSyntheticXyzRayPicker } = await import('/src/xyzSyntheticRayPicker.ts');
    const scene = syntheticPackedScene(500_000);
    const lineage = syntheticGridFacePartition(scene.xyz, 8);
    const picker = buildSyntheticXyzRayPicker(scene.xyz);
    const fullIds = scene.xyz.packed!.faceIds;
    const badIds = lineage.original_face_ids.slice();
    badIds[4] = badIds[3];
    let rejectedDuplicate = false;
    try { verifyFacePartition(fullIds, lineage.offsets, badIds); }
    catch { rejectedDuplicate = true; }
    let rejectedReal = false;
    try { syntheticGridFacePartition({ ...scene.xyz, source_sha256: 'b'.repeat(64) }); }
    catch { rejectedReal = true; }
    const center = picker?.pick([.381, .427, 2], [.381, .427, -2], true);
    return {
      count: lineage.source_face_count, groups: lineage.aggregate_count,
      linked: lineage.original_face_ids.length,
      complete: lineage.covers_every_original_face_exactly_once,
      geometricLod: lineage.is_geometric_lod,
      metricComparable: lineage.metric_comparable,
      verified: rejectedDuplicate && rejectedReal,
      center,
    };
  });
  expect(actual.count).toBe(500_000);
  expect(actual.groups).toBeGreaterThan(7_000);
  expect(actual.linked).toBe(500_000);
  expect(actual.complete).toBe(true);
  expect(actual.geometricLod).toBe(false);
  expect(actual.metricComparable).toBe(false);
  expect(actual.verified).toBe(true);
  expect(actual.center?.kind).toBe('hit');
  expect(actual.center?.testedFaces).toBeLessThan(8);
});

interface Pick { space: string; hit: boolean; source_face_id: number | null;
  method: string; picker_wall_ms: number; spatial_candidates_tested: number | null; }
interface Receipt { cells: number; displayed_cells: number; last_picker_call: Pick | null;
  source_face_partition: { original_faces: number; aggregate_groups: number;
    covered_original_faces: number; complete: boolean; is_lod: boolean } | null; }
const getReceipt = async (page: import('@playwright/test').Page) =>
  JSON.parse(await page.getByTestId('benchmark-receipt').innerText()) as Receipt | null;

test('R2.6 opt-in bounded 500k XYZ picker A/B and lineage receipt', async ({ page }, info) => {
  test.skip(process.env.APMESH_R26_500K !== '1', 'Expensive synthetic R2.6 stress; independent diagnostic workflow');
  test.setTimeout(300_000);
  await page.goto('/bench.html');
  await page.getByTestId('benchmark-cells').selectOption('500000');
  await expect.poll(async () => (await getReceipt(page))?.displayed_cells ?? 0,
    { timeout: 180_000 }).toBe(500_000);
  await expect(page.getByTestId('benchmark-status'))
    .toContainText('As duas cenas foram renderizadas', { timeout: 180_000 });

  await page.getByTestId('benchmark-audit-lineage').click();
  await expect.poll(async () => (await getReceipt(page))?.source_face_partition?.covered_original_faces ?? 0,
    { timeout: 60_000 }).toBe(500_000);
  const provenance = (await getReceipt(page))?.source_face_partition;
  expect(provenance?.complete).toBe(true);
  expect(provenance?.is_lod).toBe(false);

  const xyz = page.getByTestId('viewport-xyz');
  const rect = await xyz.boundingBox();
  if (!rect) throw new Error('missing_xyz_view');
  let fast: Pick | null = null, xy: { x: number; y: number } | null = null;
  for (const [u, v] of [[.473,.519],[.386,.457],[.548,.565],[.614,.488],[.448,.622]]) {
    const at = { x: rect.width*u, y: rect.height*v };
    await xyz.click({position:at});
    const p = (await getReceipt(page))?.last_picker_call;
    if (p?.hit && p.method === 'SYNTHETIC_XYZ_GRID_RAY') { fast = p;xy=at;break; }
  }
  expect(fast, 'At least one off-boundary pick must use the qualified fast synthetic path').not.toBeNull();
  expect(fast!.spatial_candidates_tested).toBeLessThan(1_500);
  await expect(page.getByTestId('selected-uv')).toContainText(`Face #${fast!.source_face_id}`);
  await page.getByTestId('benchmark-native-picker').check();
  await xyz.click({position:xy!});
  await expect.poll(async () => (await getReceipt(page))?.last_picker_call?.method,
    { timeout: 90_000 }).toBe('VTK_CELL_PICKER');
  const native = (await getReceipt(page))?.last_picker_call;
  expect(native?.source_face_id).toBe(fast!.source_face_id);
  const receipt = {
    schema:'apmesh.meshstudio.r26.xyz_picking_and_partition.v1',
    classification:'SYNTHETIC_500K_XYZ_INDEX_ONLY_NOT_APMESH_OR_SCIENTIFIC_LOD',
    cells:500_000,
    original_source_face_id:fast!.source_face_id,
    synthetic_xyz_fast_picker:fast,
    native_vtk_picker_same_view_and_pixel:native,
    complete_source_face_partition:provenance,
    caveats:['single_hosted_linux_chromium_not_windows_hardware',
      'synchronous_picker_call_not_end_to_end_react_paint',
      'grid_ray_qualification_restricts_to_exact_synthetic_heightfield',
      'all_real_models_keep_native_vtk_picker',
      'complete_partition_does_not_define_coarse_geometry_or_an_actual_LOD'],
  };
  const content = JSON.stringify(receipt,null,2) + String.fromCharCode(10);
  await mkdir('test-results',{recursive:true});
  await writeFile('test-results/r26-500k-xyz-picking-lineage.json',content,'utf8');
  await info.attach('r26-500k-xyz-picking-lineage.json',{body:Buffer.from(content),contentType:'application/json'});
  console.log('R26_500K_XYZ='+JSON.stringify({sourceId:fast!.source_face_id,
    fastMs:fast!.picker_wall_ms,nativeMs:native!.picker_wall_ms,
    candidateFaces:fast!.spatial_candidates_tested,sourceFacesMapped:provenance?.covered_original_faces}));
});
