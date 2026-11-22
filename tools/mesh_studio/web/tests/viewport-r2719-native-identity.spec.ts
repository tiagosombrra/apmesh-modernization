import { expect, test } from '@playwright/test';

/**
 * Synthetic browser input tests only. No staged mesh or fixture is promoted
 * into a genuine accepted native Eistute/Book research observation.
 */
function syntheticManifest(model: 'eistute' | 'book') {
  const count = model === 'eistute' ? 4 : 28;
  const samples = [0, 0.5, 1].map((t, ordinal) => ({
    ordinal,
    canonical_t: t,
    logical_id_relation: ordinal === 0
      ? 'different_native_logical_id_in_every_source_patch'
      : 'same_native_logical_id_in_all_source_patches',
    members: Array.from({ length: count }, (_, patch_slot) => ({
      patch_slot, edge_slot: 3,
      native_node_id: ordinal === 0 ? 100 + patch_slot : 500 + ordinal,
      canonical_t: t,
      original_xyz: [t, 0, 0],
      accepted_corner_cpp_owner_observed: ordinal === 0 ? true : null,
      accepted_corner_shared_cpp_pointer_with_earlier_patch: ordinal === 0 ? false : null,
    })),
  }));
  return {
    schema: 'apmesh.meshstudio.r2719.native_nonwelded_inspector.v1',
    scope: 'ORIGINAL_COMPILED_ACCEPTED_TRI_SOURCE_SCOPED_READ_ONLY',
    built_from_source_sha_pinned_native_audits: true,
    imported_browser_bundle_is_not_cryptographically_authenticated: true,
    original_native_node_ids_rewritten: false,
    new_globally_welded_node_ids_created: false,
    selected_local_attempt_lifetime_certified: false,
    scientific_lod_qualified: false,
    documents: [{
      model, accepted_native_step: 1,
      source_ndjson_sha256: 'a'.repeat(64),
      original_model_input_sha256: 'b'.repeat(64),
      original_config_sha256: 'c'.repeat(64),
      original_stderr_sha256: 'd'.repeat(64),
      source_patch_count: count,
      source_curve_count: model === 'eistute' ? 13 : 85,
      original_adapter_provisional_close_events: count * 3,
      accepted_corner_cpp_adjacency_count: count,
      accepted_corner_cpp_pointer_reuse_count: 0,
      source_geometry_is_separate_from_current_studio_viewports: true,
      original_native_node_ids_preserved: true,
      physical_node_welding_certified: false,
      cross_epoch_lineage_certified: false,
      continuous_geometric_error_bound_certified: false,
      scientific_lod_qualified: false,
      qualified_shared_source_curves: [{
        source_curve_slot: 3, native_curve_id: 1003,
        patch_slots: Array.from({ length: count }, (_, i) => i),
        sample_count: samples.length, sample_groups: samples,
        pairwise_source_geometry_qualified: true,
        physical_node_welding_certified: false,
      }],
    }],
  };
}

async function upload(page: import('@playwright/test').Page, payload: unknown) {
  await page.getByTestId('r2719-import').setInputFiles({
    name: 'synthetic-local-input-NOT-SCIENTIFIC.json',
    mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(payload)),
  });
}

test('R2.7.19 opt-in is absent by default and does not replace current P1 viewports', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('r2719-inspector')).toHaveCount(0);
  await page.goto('/?nativeInspector=1');
  await expect(page.getByTestId('r2719-inspector')).toBeVisible();
  await expect(page.getByTestId('viewport-xyz')).toBeVisible();
  await expect(page.getByTestId('viewport-uv')).toBeVisible();
  await expect(page.getByTestId('r2719-empty')).toBeVisible();
});

test('R2.7.19 source fan selects local IDs without welding or mixing viewports', async ({ page }) => {
  await page.goto('/?nativeInspector=1');
  await upload(page, syntheticManifest('eistute'));
  await expect(page.getByTestId('r2719-source-fan')).toHaveAttribute('aria-label',
    /4 patches/);
  await expect(page.getByTestId('r2719-members-table').locator('tbody tr')).toHaveCount(4);
  await page.getByTestId('r2719-patch-2').click();
  await expect(page.getByTestId('r2719-member')).toContainText('102');
  await expect(page.getByTestId('r2719-member')).toContainText('Observado');
  await expect(page.getByTestId('r2719-source-sha')).toHaveText('a'.repeat(64));
  await page.getByTestId('r2719-sample').focus();
  await page.keyboard.press('ArrowRight');
  await expect(page.getByTestId('r2719-member')).toContainText('501');
  await expect(page.getByTestId('r2719-member')).toContainText('Não observado nesta amostra');
  await expect(page.getByTestId('viewport-xyz')).toBeVisible();
});

test('R2.7.19 keeps all 28 incident Book source patches in a nonmanifold fan', async ({ page }) => {
  await page.goto('/?nativeInspector=1');
  await upload(page, syntheticManifest('book'));
  await expect(page.getByTestId('r2719-members-table').locator('tbody tr')).toHaveCount(28);
  await page.getByTestId('r2719-patch-27').click();
  await expect(page.getByTestId('r2719-member')).toContainText('127');
  await expect(page.getByTestId('r2719-source-fan')).toHaveAttribute('aria-label', /28 patches/);
});

test('R2.7.19 refuses fake welding flags and structurally incomplete source membership', async ({ page }) => {
  await page.goto('/?nativeInspector=1');
  const forged = syntheticManifest('book');
  forged.documents[0].physical_node_welding_certified = true;
  await upload(page, forged);
  await expect(page.getByTestId('r2719-error')).toContainText('unqualified');
  await expect(page.getByTestId('r2719-members-table')).toHaveCount(0);

  const incomplete = syntheticManifest('eistute');
  incomplete.documents[0].qualified_shared_source_curves[0].sample_groups[0].members.pop();
  await upload(page, incomplete);
  await expect(page.getByTestId('r2719-error')).toContainText('missing_original_patch_member');
  await expect(page.getByTestId('r2719-members-table')).toHaveCount(0);
});
