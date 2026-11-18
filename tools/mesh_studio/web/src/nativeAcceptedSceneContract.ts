/** R2.7.20 accepted native C++ TRI source geometry, never OBJ or LOD. */
import { parseNativeIdentityManifest } from './nativeIdentityContract';
import type { NativeIdentityManifest } from './nativeIdentityContract';

export const NATIVE_ACCEPTED_SCENE_SCHEMA =
  'apmesh.meshstudio.r2720.original_accepted_tri_scene.v1' as const;

export type NativeCorner = [
  nativeNodeId: number, x: number, y: number, z: number, u: number, v: number,
];
export type NativeFace = [
  patchSlot: number, nativePatchId: number,
  elementSlot: number, nativeElementId: number,
  corners: [NativeCorner, NativeCorner, NativeCorner],
];
export interface NativeAcceptedScene {
  model: 'eistute' | 'book';
  accepted_native_step: number;
  source_ndjson_sha256: string;
  native_source_patches: number;
  native_source_curves: number;
  native_tri_faces: number;
  source_patch_face_counts: number[];
  native_faces: NativeFace[];
  face_identity: 'accepted_step_patch_slot_element_slot_and_native_element_id';
  corner_identity: 'original_patch_local_native_node_id_xyz_uv';
  visual_transport_float32_only: true;
  independent_original_ndjson_sha_verified_before_export: true;
  original_node_ids_unchanged: true;
  patch_local_points_not_globally_welded: true;
  cross_epoch_lineage_certified: false;
  scientific_lod_qualified: false;
}
export interface NativeSceneBundle {
  schema: typeof NATIVE_ACCEPTED_SCENE_SCHEMA;
  scope: 'ORIGINAL_NATIVE_ACCEPTED_TRI_SEPARATE_VISUAL_RESEARCH';
  identity: NativeIdentityManifest;
  scenes: NativeAcceptedScene[];
  native_triangles_only: true;
  visual_float32_not_source_precision: true;
  source_face_ids_not_obj_ordinals: true;
  no_implicit_node_welding: true;
  no_cross_epoch_face_ancestry: true;
  scientific_lod_qualified: false;
}

function check(ok: boolean, error: string): asserts ok {
  if (!ok) throw new Error(error);
}
function record(data: unknown): Record<string, unknown> {
  check(data !== null && typeof data === 'object' && !Array.isArray(data),
    'r2720_expected_object');
  return data as Record<string, unknown>;
}
function integer(value: unknown): value is number {
  return typeof value === 'number' && Number.isSafeInteger(value) && value >= 0;
}
function finite(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}

/** Validate one offline native report. This does not hash raw original NDJSON. */
export function parseNativeAcceptedScene(text: string): NativeSceneBundle {
  check(text.length >= 10 && text.length <= 9_000_000,
    'r2720_bounded_native_scene_file_required');
  const obj = record(JSON.parse(text) as unknown);
  check(obj.schema === NATIVE_ACCEPTED_SCENE_SCHEMA &&
    obj.scope === 'ORIGINAL_NATIVE_ACCEPTED_TRI_SEPARATE_VISUAL_RESEARCH' &&
    obj.native_triangles_only === true &&
    obj.visual_float32_not_source_precision === true &&
    obj.source_face_ids_not_obj_ordinals === true &&
    obj.no_implicit_node_welding === true &&
    obj.no_cross_epoch_face_ancestry === true &&
    obj.scientific_lod_qualified === false,
  'r2720_native_scene_scope_or_scientific_exclusions_forged');

  const identity = parseNativeIdentityManifest(JSON.stringify(obj.identity));
  const scenes = obj.scenes;
  check(Array.isArray(scenes) && scenes.length === identity.documents.length &&
    scenes.length >= 1 && scenes.length <= 8,
  'r2720_scene_identity_document_count_mismatch');

  const known = new Map(identity.documents.map(d =>
    [d.model + ':' + d.accepted_native_step, d]));
  const seen = new Set<string>();
  for (const rawScene of scenes) {
    const s = record(rawScene);
    const key = String(s.model) + ':' + String(s.accepted_native_step);
    const source = known.get(key);
    check(source !== undefined && !seen.has(key) &&
      s.source_ndjson_sha256 === source.source_ndjson_sha256 &&
      s.native_source_patches === source.source_patch_count &&
      s.native_source_curves === source.source_curve_count &&
      s.face_identity === 'accepted_step_patch_slot_element_slot_and_native_element_id' &&
      s.corner_identity === 'original_patch_local_native_node_id_xyz_uv' &&
      s.visual_transport_float32_only === true &&
      s.independent_original_ndjson_sha_verified_before_export === true &&
      s.original_node_ids_unchanged === true &&
      s.patch_local_points_not_globally_welded === true &&
      s.cross_epoch_lineage_certified === false &&
      s.scientific_lod_qualified === false,
    'r2720_scene_source_hash_or_original_identity_mismatch');
    seen.add(key);

    const patchCount = source.source_patch_count;
    const faces = s.native_faces;
    const counts = s.source_patch_face_counts;
    check(Array.isArray(counts) && counts.length === patchCount &&
      counts.every(integer) &&
      Array.isArray(faces) && faces.length > 0 && faces.length <= 12_000 &&
      integer(s.native_tri_faces) && s.native_tri_faces === faces.length &&
      counts.reduce((a: number,b: number) => a + b, 0) === faces.length,
    'r2720_native_source_face_or_patch_count_mismatch');
    const measured = Array<number>(patchCount).fill(0);
    const patchNativeIds = new Map<number,number>();
    const slots = new Set<string>();
    for (const face of faces) {
      check(Array.isArray(face) && face.length === 5 &&
        integer(face[0]) && face[0] < patchCount &&
        integer(face[1]) && integer(face[2]) && integer(face[3]) &&
        Array.isArray(face[4]) && face[4].length === 3,
      'r2720_not_an_original_native_triangle');
      const patchSlot: number = face[0];
      const previousPatchId = patchNativeIds.get(patchSlot);
      check(previousPatchId === undefined || previousPatchId === face[1],
        'r2720_original_patch_native_id_changed');
      patchNativeIds.set(patchSlot, face[1]);
      const keySlot = patchSlot + ':' + face[2];
      check(!slots.has(keySlot) && face[2] < counts[patchSlot],
        'r2720_repeated_or_out_of_range_original_element_slot');
      slots.add(keySlot);
      measured[patchSlot] += 1;
      for (const corner of face[4]) {
        check(Array.isArray(corner) && corner.length === 6 &&
          integer(corner[0]) && corner.slice(1).every(finite) &&
          corner[4] >= -1e-9 && corner[4] <= 1 + 1e-9 &&
          corner[5] >= -1e-9 && corner[5] <= 1 + 1e-9,
        'r2720_native_corner_not_source_uv_xyz_and_id');
      }
    }
    check(counts.every((count: number,p: number) =>
      count === measured[p] && count > 0),
    'r2720_original_source_patch_face_slots_incomplete');
    // Source curve corner IDs are correlated only when the original accepted
    // native node and patch slot occur in a true accepted TRI face.
    for (const curve of source.qualified_shared_source_curves) {
      for (const group of curve.sample_groups) {
        for (const member of group.members) {
          const found = faces.some(face => face[0] === member.patch_slot &&
            face[4].some(corner => corner[0] === member.native_node_id &&
              Math.abs(corner[1] - member.original_xyz[0]) <= 1e-9 &&
              Math.abs(corner[2] - member.original_xyz[1]) <= 1e-9 &&
              Math.abs(corner[3] - member.original_xyz[2]) <= 1e-9));
          check(found, 'r2720_original_native_seam_sample_missing_from_accepted_faces');
        }
      }
    }
  }
  check(seen.size === known.size, 'r2720_missing_actual_native_accepted_scene');
  return obj as unknown as NativeSceneBundle;
}
