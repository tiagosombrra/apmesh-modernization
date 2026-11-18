import { expect, test } from '@playwright/test';

/** All browser fixtures below are synthetic and do not qualify real native TRI. */
function syntheticNativeScene(model: 'eistute' | 'book') {
  const n = model === 'eistute' ? 4 : 28;
  const groups = [0,1].map((t,ordinal) => ({
    ordinal,
    canonical_t:t,
    logical_id_relation:ordinal === 0
      ? 'different_native_logical_id_in_every_source_patch'
      : 'same_native_logical_id_in_all_source_patches',
    members:Array.from({length:n},(_,patch_slot)=>({
      patch_slot,edge_slot:3,
      native_node_id:ordinal === 0 ? 100+patch_slot : 200,
      original_xyz:[0,t,0],
      canonical_t:t,
      accepted_corner_cpp_owner_observed:ordinal === 0 ? true : null,
      accepted_corner_shared_cpp_pointer_with_earlier_patch:ordinal === 0 ? false : null,
    })),
  }));
  const id = {
    model, accepted_native_step:1,
    source_ndjson_sha256:'a'.repeat(64),
    original_model_input_sha256:'b'.repeat(64),
    original_config_sha256:'c'.repeat(64),
    original_stderr_sha256:'d'.repeat(64),
    source_patch_count:n, source_curve_count:model==='eistute'?13:85,
    original_adapter_provisional_close_events:n,
    accepted_corner_cpp_adjacency_count:n,
    accepted_corner_cpp_pointer_reuse_count:0,
    qualified_shared_source_curves:[{
      source_curve_slot:3,native_curve_id:503,
      patch_slots:Array.from({length:n},(_,i)=>i),
      sample_count:2,sample_groups:groups,
      pairwise_source_geometry_qualified:true,
      physical_node_welding_certified:false,
    }],
    source_geometry_is_separate_from_current_studio_viewports:true,
    original_native_node_ids_preserved:true,
    physical_node_welding_certified:false,
    cross_epoch_lineage_certified:false,
    continuous_geometric_error_bound_certified:false,
    scientific_lod_qualified:false,
  };
  const triangles=Array.from({length:n},(_,patch)=>{
    const angle = patch*2*Math.PI/n;
    return [
      patch,700+patch,0,5000+patch,
      [
        [100+patch,0,0,0,0,0],
        [200,0,1,0,0,1],
        [300+patch,Math.cos(angle),0.5,Math.sin(angle),1,0.5],
      ],
    ];
  });
  const scene={
    model, accepted_native_step:1,source_ndjson_sha256:'a'.repeat(64),
    native_source_patches:n,native_source_curves:model==='eistute'?13:85,
    native_tri_faces:n,source_patch_face_counts:Array(n).fill(1),
    native_faces:triangles,
    face_identity:'accepted_step_patch_slot_element_slot_and_native_element_id',
    corner_identity:'original_patch_local_native_node_id_xyz_uv',
    visual_transport_float32_only:true,
    independent_original_ndjson_sha_verified_before_export:true,
    original_node_ids_unchanged:true,
    patch_local_points_not_globally_welded:true,
    cross_epoch_lineage_certified:false,
    scientific_lod_qualified:false,
  };
  return { id,scene };
}

function example() {
  const entries=[syntheticNativeScene('eistute'),syntheticNativeScene('book')];
  return {
    schema:'apmesh.meshstudio.r2720.original_accepted_tri_scene.v1',
    scope:'ORIGINAL_NATIVE_ACCEPTED_TRI_SEPARATE_VISUAL_RESEARCH',
    identity:{
      schema:'apmesh.meshstudio.r2719.native_nonwelded_inspector.v1',
      scope:'ORIGINAL_COMPILED_ACCEPTED_TRI_SOURCE_SCOPED_READ_ONLY',
      documents:entries.map(x=>x.id),
      built_from_source_sha_pinned_native_audits:true,
      imported_browser_bundle_is_not_cryptographically_authenticated:true,
      original_native_node_ids_rewritten:false,
      new_globally_welded_node_ids_created:false,
      selected_local_attempt_lifetime_certified:false,
      scientific_lod_qualified:false,
    },
    scenes:entries.map(x=>x.scene),
    native_triangles_only:true,visual_float32_not_source_precision:true,
    source_face_ids_not_obj_ordinals:true,no_implicit_node_welding:true,
    no_cross_epoch_face_ancestry:true,scientific_lod_qualified:false,
  };
}

async function upload(page: import('@playwright/test').Page, payload: unknown) {
  await page.getByTestId('r2720-import').setInputFiles({
    name:'SYNTHETIC-R2720-NOT-NATIVE-SCIENTIFIC.json',
    mimeType:'application/json',buffer:Buffer.from(JSON.stringify(payload)),
  });
}

test('R2.7.20 viewer is absent unless explicitly enabled, P1 views unchanged',async({page})=>{
  await page.goto('/');
  await expect(page.getByTestId('r2720-panel')).toHaveCount(0);
  await page.goto('/?nativeScene=1');
  await expect(page.getByTestId('r2720-panel')).toBeVisible();
  await expect(page.getByTestId('r2720-empty')).toBeVisible();
  await expect(page.getByTestId('viewport-xyz')).toBeVisible();
  await expect(page.getByTestId('viewport-uv')).toBeVisible();
});

test('R2.7.20 synthetic TRI source import keeps XYZ and patch-local UV distinct',async({page})=>{
  await page.goto('/?nativeScene=1');
  await upload(page,example());
  await expect(page.getByTestId('r2720-tri-count')).toHaveText('4');
  await expect(page.getByTestId('r2720-viewport-xyz')
    .locator('canvas').first()).toBeVisible();
  await expect(page.getByTestId('r2720-viewport-uv')
    .locator('canvas').first()).toBeVisible();
  await expect(page.getByTestId('r2720-viewport-xyz')).toHaveAttribute(
    'data-native-accepted-faces','4');
  await expect(page.getByTestId('r2720-viewport-uv')).toHaveAttribute(
    'data-native-accepted-faces','1');
  await expect(page.getByTestId('r2720-source-node-id')).toHaveText('100');
  await page.getByTestId('r2720-patch').selectOption('2');
  await expect(page.getByTestId('r2720-source-node-id')).toHaveText('102');
  await page.getByTestId('r2720-highlight-source-sample').click();
  await expect(page.getByTestId('r2720-native-element-id')).toHaveText('5002');
  await expect(page.getByTestId('r2720-corners').locator('tbody tr')).toHaveCount(3);
  await expect(page.getByTestId('r2720-linked-samples')).toContainText('nó 102');
  await expect(page.getByTestId('r2720-source-sha')).toHaveText('a'.repeat(64));
});

test('R2.7.20 Book has all 28 original patch-scoped TRI and real ID tuples',async({page})=>{
  await page.goto('/?nativeScene=1');
  await upload(page,example());
  await page.getByTestId('r2720-model').selectOption('1');
  await expect(page.getByTestId('r2720-tri-count')).toHaveText('28');
  await expect(page.getByTestId('r2720-viewport-xyz')).toHaveAttribute(
    'data-native-accepted-faces','28');
  await page.getByTestId('r2720-patch').selectOption('27');
  await expect(page.getByTestId('r2720-source-node-id')).toHaveText('127');
  await page.getByTestId('r2720-highlight-source-sample').click();
  await expect(page.getByTestId('r2720-native-element-id')).toHaveText('5027');
});

test('R2.7.20 rejects forged native face ID, source SHA and welding semantics',async({page})=>{
  await page.goto('/?nativeScene=1');
  const forged=example();
  forged.scenes[0].source_ndjson_sha256='f'.repeat(64);
  await upload(page,forged);
  await expect(page.getByTestId('r2720-error')).toContainText('source_hash');
  await expect(page.getByTestId('r2720-viewport-xyz')).toHaveCount(0);

  const duplicate=example();
  duplicate.scenes[0].native_faces.push(
    duplicate.scenes[0].native_faces[0]);
  duplicate.scenes[0].native_tri_faces++;
  duplicate.scenes[0].source_patch_face_counts[0]++;
  await upload(page,duplicate);
  await expect(page.getByTestId('r2720-error')).toContainText('repeated_or_out_of_range');

  const welded=example();
  welded.no_implicit_node_welding=false;
  await upload(page,welded);
  await expect(page.getByTestId('r2720-error')).toContainText('scope_or_scientific_exclusions');
});


test('R2.7.21 native Eistute source seam is real TRI edges in XYZ and patch-local UV',async({page})=>{
  await page.goto('/?nativeScene=1');
  await upload(page,example());
  await expect(page.getByTestId('r2721-segment-count')).toHaveText('4');
  await expect(page.getByTestId('r2721-patch-count')).toHaveText('4');
  await expect(page.getByTestId('r2720-viewport-xyz')).toHaveAttribute(
    'data-native-seam-segments','4');
  await expect(page.getByTestId('r2720-viewport-uv')).toHaveAttribute(
    'data-native-seam-segments','1');
  await expect(page.getByTestId('r2720-viewport-xyz')).toHaveAttribute(
    'data-native-seam-patch-incidences','4');
  await page.getByTestId('r2720-patch').selectOption('2');
  await expect(page.getByTestId('r2720-source-node-id')).toHaveText('102');
  await expect(page.getByTestId('r2720-native-element-id')).toHaveText('5002');
  await expect(page.getByTestId('r2721-selection-scope')).toContainText('incidente');
  await page.getByTestId('r2720-sample').focus();
  await page.keyboard.press('ArrowRight');
  await expect(page.getByTestId('r2720-source-node-id')).toHaveText('200');
  await expect(page.getByTestId('r2720-viewport-xyz')).toHaveAttribute(
    'data-native-selected-sample','1');
  await expect(page.getByTestId('r2720-viewport-uv')).toHaveAttribute(
    'data-native-selected-sample','1');
});

test('R2.7.21 retains all 28 native Book source patches without fake welding',async({page})=>{
  await page.goto('/?nativeScene=1');
  await upload(page,example());
  await page.getByTestId('r2720-model').selectOption('1');
  await expect(page.getByTestId('r2721-patch-count')).toHaveText('28');
  await expect(page.getByTestId('r2721-segment-count')).toHaveText('28');
  await expect(page.getByTestId('r2720-viewport-xyz')).toHaveAttribute(
    'data-native-seam-segments','28');
  await page.getByTestId('r2720-patch').selectOption('27');
  await expect(page.getByTestId('r2720-source-node-id')).toHaveText('127');
  await expect(page.getByTestId('r2720-native-element-id')).toHaveText('5027');
  await expect(page.getByTestId('r2720-viewport-uv')).toHaveAttribute(
    'data-native-seam-segments','1');
  await expect(page.getByTestId('r2721-curve')).toHaveValue('0');
});

test('R2.7.21 refuses invented seam chords when original nodes are not adjacent TRI vertices',async({page})=>{
  await page.goto('/?nativeScene=1');
  const forged=example();
  const target=forged.scenes[0];
  target.native_faces[0][4][1]=[9001,0.5,0,0,0.5,0];
  target.native_faces.push([
    0,700,1,9501,
    [[200,0,1,0,0,1],[9002,1,0.4,0,1,0.4],[9003,0.7,0.9,0,0.7,0.9]],
  ]);
  target.source_patch_face_counts[0]++;
  target.native_tri_faces++;
  await upload(page,forged);
  await expect(page.getByTestId('r2720-error'))
    .toContainText('r2721_source_sample_segment_not_native_accepted_tri_edge');
  await expect(page.getByTestId('r2720-viewport-xyz')).toHaveCount(0);
  await expect(page.getByTestId('r2720-viewport-uv')).toHaveCount(0);
});

test('R2.7.21 never displays source seam overlay without explicit native scene opt-in',async({page})=>{
  await page.goto('/');
  await expect(page.getByTestId('r2721-seam-proof')).toHaveCount(0);
  await expect(page.getByTestId('r2720-viewport-xyz')).toHaveCount(0);
  await expect(page.getByTestId('viewport-xyz')).toBeVisible();
});
