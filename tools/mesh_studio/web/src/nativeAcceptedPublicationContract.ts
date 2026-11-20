/** Verify source-bound original-native SVG/manifest against the loaded scene.
 * This check cannot replace the CI's independent original C++ NDJSON audit.
 */
import type { NativeSceneBundle } from './nativeAcceptedSceneContract';

const SCHEMA = 'apmesh.meshstudio.v52.original_native_accepted_publication.v1';
const VECTOR_SCHEMA = 'apmesh.meshstudio.v52.original_native_accepted_uv_vector.v1';
const SVG_NS = 'http://www.w3.org/2000/svg';

export interface NativeAcceptedVector {
  model: 'eistute' | 'book';
  step: number;
  filename: string;
  sourceSha: string;
  svgSha: string;
  file: File;
}

function check(condition: unknown, reason: string): asserts condition {
  if (!condition) throw new Error(reason);
}
export async function sha256File(file: File): Promise<string> {
  const bytes = await file.arrayBuffer();
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest),
    v => v.toString(16).padStart(2, '0')).join('');
}

function validateSvg(xmlString: string, scene: NativeSceneBundle['scenes'][number],
  figure: Record<string, unknown>): void {
  check(!/<!DOCTYPE|<!ENTITY/i.test(xmlString), 'v52_forbidden_xml_entities');
  const parsed = new DOMParser().parseFromString(xmlString, 'image/svg+xml');
  const root = parsed.documentElement;
  check(root.localName === 'svg' && root.namespaceURI === SVG_NS &&
    parsed.querySelector('parsererror') === null &&
    root.getAttribute('data-schema') === VECTOR_SCHEMA &&
    root.getAttribute('data-model') === scene.model &&
    root.getAttribute('data-original-accepted-step') === String(scene.accepted_native_step) &&
    root.getAttribute('data-original-source-ndjson-sha256') === scene.source_ndjson_sha256 &&
    root.getAttribute('data-physical-welding-certified') === 'false' &&
    root.getAttribute('data-scientific-lod-qualified') === 'false',
  'v52_svg_native_source_identity_invalid');

  const allowed = new Set(['svg','title','desc','rect','text','g','polygon','circle']);
  for (const element of Array.from(parsed.querySelectorAll('*'))) {
    check(element.namespaceURI === SVG_NS && allowed.has(element.localName),
      'v52_svg_contains_active_or_raster_node');
    for (const attr of Array.from(element.attributes)) {
      const name = attr.name.toLowerCase(), value = attr.value.toLowerCase();
      check(!name.startsWith('on') && !name.endsWith('href') &&
        !value.includes('url(') && !value.includes('data:'),
      'v52_svg_contains_active_or_external_attribute');
    }
  }
  const expected = new Map(scene.native_faces.map(face => [
    String(face[0])+':'+String(face[2])+':'+String(face[3]), face,
  ]));
  const seen = new Set<string>(), panels = new Set<number>();
  const counts = Array(scene.native_source_patches).fill(0) as number[];
  const cols = scene.model === 'eistute' ? 2 : 7;
  const cellW = cols === 2 ? 440 : 210, cellH = cols === 2 ? 325 : 230;
  const size = cols === 2 ? 270 : 158;

  for (const element of Array.from(parsed.querySelectorAll('g[data-original-patch-slot]'))) {
    const patch = Number(element.getAttribute('data-original-patch-slot'));
    check(Number.isSafeInteger(patch) && patch >= 0 &&
      patch < scene.native_source_patches && !panels.has(patch) &&
      element.getAttribute('data-original-face-count') ===
        String(scene.source_patch_face_counts[patch]),
    'v52_svg_original_patch_panel_invalid');
    panels.add(patch);
  }
  for (const element of Array.from(parsed.querySelectorAll('polygon'))) {
    const patch = Number(element.getAttribute('data-original-patch-slot'));
    const slot = Number(element.getAttribute('data-original-element-slot'));
    const nativeId = Number(element.getAttribute('data-native-element-id'));
    const key = String(patch)+':'+String(slot)+':'+String(nativeId);
    const face = expected.get(key);
    check(face && !seen.has(key) &&
      element.getAttribute('data-native-patch-id') === String(face[1]) &&
      element.getAttribute('data-original-native-node-ids') ===
        face[4].map(node=>node[0]).join(','),
    'v52_svg_native_face_key_or_node_mismatch');
    const uv = element.getAttribute('data-original-local-uv')?.split(';')
      .map(pair=>pair.split(',').map(Number));
    check(uv && uv.length === 3 &&
      uv.every((p,i)=>p.length === 2 && p[0] === face[4][i][4] &&
        p[1] === face[4][i][5]),
    'v52_svg_original_native_corner_uv_mismatch');
    const row = Math.floor(patch/cols), col = patch%cols;
    const x0 = 35 + col*cellW + (cellW-size)/2;
    const y0 = 108 + row*cellH + 38;
    const points = element.getAttribute('points')?.trim().split(/\s+/)
      .map(p=>p.split(',').map(Number));
    check(points && points.length === 3 && points.every((p,i)=>
      p.length === 2 &&
      Math.abs(p[0] - (x0+size*face[4][i][4])) <= 1e-7 &&
      Math.abs(p[1] - (y0+size*(1-face[4][i][5]))) <= 1e-7),
    'v52_svg_visual_points_not_from_native_uv');
    seen.add(key);
    counts[patch] += 1;
  }
  check(expected.size === scene.native_tri_faces &&
    seen.size === expected.size && panels.size === scene.native_source_patches &&
    counts.every((count,p)=>count === scene.source_patch_face_counts[p]),
  'v52_svg_native_face_patch_inventory_incomplete');
  check(parsed.querySelectorAll('circle[data-original-source-sample-ordinal]').length ===
    figure.observed_source_curve_sample_marker_count,
  'v52_svg_native_curve_sample_marker_inventory_mismatch');
}

export async function verifyNativeVectorPackage(
  files: File[], scene: NativeSceneBundle, sceneFileSha: string,
): Promise<NativeAcceptedVector[]> {
  check(/^[a-f0-9]{64}$/.test(sceneFileSha) &&
    files.length === scene.scenes.length+1,
  'v52_incomplete_original_vector_upload');
  const manifestFile = files.find(f=>f.name === 'manifest.json');
  check(manifestFile && manifestFile.size > 20 && manifestFile.size <= 256_000,
    'v52_manifest_missing_or_oversized');
  const manifest = JSON.parse(await manifestFile.text()) as Record<string, unknown>;
  check(manifest.schema === SCHEMA &&
    manifest.classification === 'ORIGINAL_ACCEPTED_CPP_TRI_SOURCE_VERIFIED_PATCH_UV_VECTOR' &&
    manifest.source_scene_bundle_sha256 === sceneFileSha &&
    manifest.source_cpp_raw_ndjson_reaudited === true &&
    manifest.native_triangles_only === true &&
    manifest.original_physical_node_welding_certified === false &&
    manifest.cross_epoch_face_lineage_certified === false &&
    manifest.continuous_geometric_error_bound_certified === false &&
    manifest.scientific_lod_qualified === false &&
    Array.isArray(manifest.figures) &&
    manifest.figures.length === scene.scenes.length,
  'v52_manifest_not_bound_to_imported_original_native_scene');
  const figureRecords = manifest.figures as Record<string, unknown>[];
  const result: NativeAcceptedVector[] = [];
  const joined = new Set<string>();
  for (const native of scene.scenes) {
    const sourceIdentity = scene.identity.documents.find(d=>
      d.model === native.model &&
      d.accepted_native_step === native.accepted_native_step &&
      d.source_ndjson_sha256 === native.source_ndjson_sha256);
    const record = figureRecords.find(f=>
      f.model === native.model && f.accepted_native_step === native.accepted_native_step);
    check(sourceIdentity && record, 'v52_native_original_source_record_missing');
    const key = native.model+':'+String(native.accepted_native_step);
    check(!joined.has(key), 'v52_native_original_scene_record_duplicated');
    joined.add(key);
    const actualMarkerCount = sourceIdentity.qualified_shared_source_curves.reduce(
      (count,curve)=>count+curve.sample_groups.reduce(
        (total,group)=>total+group.members.length,0),0);
    check(record.original_source_ndjson_sha256 === native.source_ndjson_sha256 &&
      record.original_model_input_sha256 === sourceIdentity.original_model_input_sha256 &&
      record.original_config_sha256 === sourceIdentity.original_config_sha256 &&
      record.original_native_tri_faces === native.native_tri_faces &&
      record.original_source_patch_count === native.native_source_patches &&
      record.original_source_curve_count === native.native_source_curves &&
      JSON.stringify(record.original_patch_face_counts) ===
        JSON.stringify(native.source_patch_face_counts) &&
      JSON.stringify(record.source_shared_curve_slots) ===
        JSON.stringify(sourceIdentity.qualified_shared_source_curves
          .map(c=>c.source_curve_slot).sort((a,b)=>a-b)) &&
      record.observed_source_curve_sample_marker_count === actualMarkerCount &&
      record.physical_node_welding_certified === false &&
      record.scientific_lod_qualified === false,
    'v52_native_original_figure_receipt_unmatched');
    const filename = native.model+'-accepted-step'+String(native.accepted_native_step)+'-uv.svg';
    check(record.svg_filename === filename &&
      typeof record.svg_sha256 === 'string' &&
      /^[a-f0-9]{64}$/.test(record.svg_sha256),
    'v52_native_original_figure_filename_or_sha_invalid');
    const file = files.find(f=>f.name === filename);
    check(file && file.size > 500 && file.size <= 12_000_000 &&
      record.svg_size_bytes === file.size,
    'v52_native_original_svg_missing_or_oversized');
    check(await sha256File(file) === record.svg_sha256,
      'v52_native_original_vector_bytes_changed');
    validateSvg(await file.text(), native, record);
    result.push({model:native.model,step:native.accepted_native_step,
      filename,sourceSha:native.source_ndjson_sha256,
      svgSha:record.svg_sha256,file});
  }
  check(result.length === scene.scenes.length &&
    figureRecords.every(f=>joined.has(String(f.model)+':'+String(f.accepted_native_step))),
  'v52_unmatched_original_native_figure_record');
  return result;
}
