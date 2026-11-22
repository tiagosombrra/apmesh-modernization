/** R2.7.19 explicit local native identity, never an inferred welded topology. */

export const NATIVE_INSPECTOR_SCHEMA =
  'apmesh.meshstudio.r2719.native_nonwelded_inspector.v1' as const;
const HEX64 = /^[a-f0-9]{64}$/;

export interface NativeLocalMember {
  patch_slot: number;
  edge_slot: number;
  native_node_id: number;
  canonical_t: number;
  original_xyz: [number, number, number];
  accepted_corner_cpp_owner_observed: boolean | null;
  accepted_corner_shared_cpp_pointer_with_earlier_patch: boolean | null;
}
export interface NativeSampleGroup {
  ordinal: number;
  canonical_t: number;
  logical_id_relation:
    'same_native_logical_id_in_all_source_patches' |
    'different_native_logical_id_in_every_source_patch' |
    'mixed_reused_native_logical_ids';
  members: NativeLocalMember[];
}
export interface NativeSharedSourceCurve {
  source_curve_slot: number;
  native_curve_id: number;
  patch_slots: number[];
  sample_count: number;
  sample_groups: NativeSampleGroup[];
  pairwise_source_geometry_qualified: true;
  physical_node_welding_certified: false;
}
export interface NativeInspectorDocument {
  model: 'eistute' | 'book';
  accepted_native_step: number;
  source_ndjson_sha256: string;
  original_model_input_sha256: string;
  original_config_sha256: string;
  original_stderr_sha256: string;
  source_patch_count: number;
  source_curve_count: number;
  original_adapter_provisional_close_events: number;
  accepted_corner_cpp_adjacency_count: number;
  accepted_corner_cpp_pointer_reuse_count: number;
  qualified_shared_source_curves: NativeSharedSourceCurve[];
  source_geometry_is_separate_from_current_studio_viewports: true;
  original_native_node_ids_preserved: true;
  physical_node_welding_certified: false;
  cross_epoch_lineage_certified: false;
  continuous_geometric_error_bound_certified: false;
  scientific_lod_qualified: false;
}
export interface NativeIdentityManifest {
  schema: typeof NATIVE_INSPECTOR_SCHEMA;
  scope: 'ORIGINAL_COMPILED_ACCEPTED_TRI_SOURCE_SCOPED_READ_ONLY';
  documents: NativeInspectorDocument[];
  built_from_source_sha_pinned_native_audits: true;
  imported_browser_bundle_is_not_cryptographically_authenticated: true;
  original_native_node_ids_rewritten: false;
  new_globally_welded_node_ids_created: false;
  selected_local_attempt_lifetime_certified: false;
  scientific_lod_qualified: false;
}

function check(ok: boolean, reason: string): asserts ok {
  if (!ok) throw new Error(reason);
}
function object(value: unknown): Record<string, unknown> {
  check(value !== null && typeof value === 'object' && !Array.isArray(value),
    'native_inspector_expected_object');
  return value as Record<string, unknown>;
}
function array(value: unknown, max: number): unknown[] {
  check(Array.isArray(value) && value.length <= max,
    'native_inspector_unbounded_array');
  return value as unknown[];
}
function integer(value: unknown, max: number): value is number {
  return typeof value === 'number' && Number.isSafeInteger(value) &&
    value >= 0 && value <= max;
}
function finite(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}
function isSha(value: unknown): value is string {
  return typeof value === 'string' && HEX64.test(value);
}
function xyz3(value: unknown): value is [number, number, number] {
  return Array.isArray(value) && value.length === 3 && value.every(finite);
}

/**
 * Structural constraints only. Without the original native NDJSON bytes,
 * this local browser import does NOT independently authenticate its SHA.
 */
export function parseNativeIdentityManifest(text: string): NativeIdentityManifest {
  check(text.length > 0 && text.length <= 800_000, 'native_inspector_file_size_limit');
  const root = object(JSON.parse(text) as unknown);
  check(root.schema === NATIVE_INSPECTOR_SCHEMA &&
    root.scope === 'ORIGINAL_COMPILED_ACCEPTED_TRI_SOURCE_SCOPED_READ_ONLY' &&
    root.built_from_source_sha_pinned_native_audits === true &&
    root.imported_browser_bundle_is_not_cryptographically_authenticated === true &&
    root.original_native_node_ids_rewritten === false &&
    root.new_globally_welded_node_ids_created === false &&
    root.selected_local_attempt_lifetime_certified === false &&
    root.scientific_lod_qualified === false,
  'native_inspector_source_scope_or_no_welding_flags_invalid');
  const documents = array(root.documents, 8);
  check(documents.length > 0, 'native_inspector_empty_source_documents');
  const seenDocuments = new Set<string>();
  for (const candidate of documents) {
    const d = object(candidate);
    const model = d.model;
    check(model === 'eistute' || model === 'book', 'native_inspector_unknown_real_model');
    check(integer(d.accepted_native_step, 100_000) && d.accepted_native_step > 0 &&
      d.source_patch_count === (model === 'eistute' ? 4 : 28) &&
      d.source_curve_count === (model === 'eistute' ? 13 : 85),
    'native_inspector_original_model_or_epoch_mismatch');
    const key = model + ':' + d.accepted_native_step;
    check(!seenDocuments.has(key), 'native_inspector_duplicate_original_accepted_step');
    seenDocuments.add(key);
    for (const field of ['source_ndjson_sha256','original_model_input_sha256',
      'original_config_sha256','original_stderr_sha256']) {
      check(isSha(d[field]), 'native_inspector_missing_original_sha_' + field);
    }
    check(integer(d.original_adapter_provisional_close_events, 100_000) &&
      integer(d.accepted_corner_cpp_adjacency_count, 1024) &&
      d.accepted_corner_cpp_adjacency_count === d.source_patch_count &&
      d.accepted_corner_cpp_pointer_reuse_count === 0 &&
      d.source_geometry_is_separate_from_current_studio_viewports === true &&
      d.original_native_node_ids_preserved === true &&
      d.physical_node_welding_certified === false &&
      d.cross_epoch_lineage_certified === false &&
      d.continuous_geometric_error_bound_certified === false &&
      d.scientific_lod_qualified === false,
    'native_inspector_unqualified_original_source_or_pointer_scope');
    const curves = array(d.qualified_shared_source_curves, 64);
    check(curves.length > 0, 'native_inspector_no_original_shared_curves');
    const seenCurves = new Set<number>();
    for (const candidateCurve of curves) {
      const curve = object(candidateCurve);
      check(integer(curve.source_curve_slot, d.source_curve_count as number - 1) &&
        integer(curve.native_curve_id, Number.MAX_SAFE_INTEGER) &&
        !seenCurves.has(curve.source_curve_slot as number),
      'native_inspector_invalid_original_source_curve');
      seenCurves.add(curve.source_curve_slot as number);
      check(curve.pairwise_source_geometry_qualified === true &&
        curve.physical_node_welding_certified === false,
      'native_inspector_original_source_curve_not_nonwelded');
      const patches = array(curve.patch_slots, d.source_patch_count as number);
      check(patches.length >= 2 && patches.every(p =>
        integer(p, d.source_patch_count as number - 1)) &&
        new Set(patches).size === patches.length,
      'native_inspector_source_patch_incidence_invalid');
      const samples = array(curve.sample_groups, 4096);
      check(integer(curve.sample_count, 4096) && samples.length === curve.sample_count &&
        samples.length >= 2, 'native_inspector_incomplete_sampled_curve');
      let previousT = -1;
      samples.forEach((rawSample, ordinal) => {
        const sample = object(rawSample);
        check(sample.ordinal === ordinal && finite(sample.canonical_t) &&
          (sample.canonical_t as number) >= -1e-9 &&
          (sample.canonical_t as number) <= 1 + 1e-9 &&
          (sample.canonical_t as number) > previousT &&
          ['same_native_logical_id_in_all_source_patches',
            'different_native_logical_id_in_every_source_patch',
            'mixed_reused_native_logical_ids'].includes(String(sample.logical_id_relation)),
        'native_inspector_sample_order_or_identity_class_invalid');
        previousT = sample.canonical_t as number;
        const members = array(sample.members, patches.length);
        check(members.length === patches.length,
          'native_inspector_missing_original_patch_member');
        const seen = new Set<number>(), ids = new Set<number>();
        let refXYZ: [number, number, number] | null = null;
        for (const rawMember of members) {
          const member = object(rawMember);
          check(integer(member.patch_slot, d.source_patch_count as number - 1) &&
            patches.includes(member.patch_slot) && !seen.has(member.patch_slot as number) &&
            integer(member.edge_slot, 3) &&
            integer(member.native_node_id, Number.MAX_SAFE_INTEGER) &&
            finite(member.canonical_t) &&
            Math.abs((member.canonical_t as number) -
              (sample.canonical_t as number)) <= 1e-9 &&
            xyz3(member.original_xyz),
          'native_inspector_original_member_identity_or_xyz_invalid');
          seen.add(member.patch_slot as number);
          ids.add(member.native_node_id as number);
          const xyz = member.original_xyz as [number,number,number];
          if (refXYZ === null) refXYZ = xyz;
          else {
            // Bounded browser comparison is a diagnostic, not continuous welding.
            const delta = Math.hypot(...xyz.map((v, i) => v - refXYZ![i]));
            check(delta <= 1e-5, 'native_inspector_original_xyz_nonconcordant');
          }
          const owns = member.accepted_corner_cpp_owner_observed;
          const aliased = member.accepted_corner_shared_cpp_pointer_with_earlier_patch;
          const actualCorner = ordinal === 0 && member.edge_slot === 3 &&
            Math.abs(sample.canonical_t as number) <= 1e-9;
          check(actualCorner ? owns === true && aliased === false :
            owns === null && aliased === null,
          'native_inspector_invented_cpp_pointer_witness');
        }
        const declared = sample.logical_id_relation;
        const observed = ids.size === 1 ? 'same_native_logical_id_in_all_source_patches' :
          ids.size === patches.length ? 'different_native_logical_id_in_every_source_patch' :
          'mixed_reused_native_logical_ids';
        check(declared === observed, 'native_inspector_forged_original_logical_id_class');
      });
    }
  }
  return root as unknown as NativeIdentityManifest;
}
