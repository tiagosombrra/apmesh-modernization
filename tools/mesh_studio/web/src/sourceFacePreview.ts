/** A display-only, sparse subset of ORIGINAL faces, never a topology-preserving LOD. */
import type { MeshGeometry, PackedMeshData } from './contracts';
import { meshFaceCount } from './meshAccess';

export const PREVIEW_SCHEMA = 'apmesh.meshstudio.partial_original_faces.v1';
export type PreviewProvenance = {
  schema: typeof PREVIEW_SCHEMA;
  source_sha256: string;
  original_faces: number;
  shown_original_faces: number;
  coverage_fraction: number;
  source_face_ids_exact: true;
  changes_source_connectivity: false;
  complete_surface: false;
  scientific_quality_comparable: false;
  is_lod: false;
  warning: string;
};
export interface PreviewPair {
  xyz: MeshGeometry;
  uv: MeshGeometry;
  provenance: PreviewProvenance;
}

/** Show fewer ORIGINAL elements without fabricating coarse faces or source ownership. */
export function sourceFacePreviewPair(
  xyz: MeshGeometry, uv: MeshGeometry, requestedFaces: number,
): PreviewPair {
  if (xyz.coordinate_space !== 'xyz' || uv.coordinate_space !== 'uv' ||
      xyz.source_sha256 !== uv.source_sha256 ||
      !/^[0-9a-f]{64}$/.test(xyz.source_sha256) ||
      xyz.source_patch_ownership !== uv.source_patch_ownership ||
      !xyz.packed || !uv.packed) throw new Error('preview_source_mismatch');
  const base: PackedMeshData = xyz.packed;
  const other: PackedMeshData = uv.packed;
  const count = meshFaceCount(xyz);
  if (!Number.isSafeInteger(requestedFaces) || requestedFaces < 100 ||
      requestedFaces > 100_000 || count <= requestedFaces || count > 1_000_000 ||
      count !== meshFaceCount(uv) ||
      base.vertices.length % 3 !== 0 || other.vertices.length % 3 !== 0 ||
      base.faceIds.length !== base.arities.length ||
      base.offsets.length !== count + 1 ||
      other.faceIds.length !== count || other.arities.length !== count ||
      other.offsets.length !== count + 1) throw new Error('invalid_preview_inventory');
  if (!base.faceIds.every((id, i) => id === other.faceIds[i]) ||
      !base.arities.every((arity, i) => arity === other.arities[i])) {
    throw new Error('preview_xyz_uv_identity_mismatch');
  }
  // Each chosen cell remains byte-for-byte the same original vertex-index sequence.
  const sourceIds = new Uint32Array(requestedFaces);
  const arities = new Uint8Array(requestedFaces);
  const offsets = new Uint32Array(requestedFaces + 1);
  const xyzPolys = new Uint32Array(requestedFaces * 5);
  const uvPolys = new Uint32Array(requestedFaces * 5);
  let cursor = 0;
  let triangles = 0;
  let quads = 0;
  for (let i = 0; i < requestedFaces; i += 1) {
    const sourceIndex = Math.floor(i * count / requestedFaces);
    const start = base.offsets[sourceIndex];
    const end = base.offsets[sourceIndex + 1];
    const uvStart = other.offsets[sourceIndex];
    const uvEnd = other.offsets[sourceIndex + 1];
    const arity = base.arities[sourceIndex];
    if ((arity !== 3 && arity !== 4) ||
        end - start !== arity + 1 || uvEnd - uvStart !== end - start ||
        base.polys[start] !== arity || other.polys[uvStart] !== arity ||
        end > base.polys.length || uvEnd > other.polys.length) {
      throw new Error('preview_invalid_original_connectivity');
    }
    for (let k = 0; k <= arity; k += 1) {
      const xyzIndex = base.polys[start + k];
      const uvIndex = other.polys[uvStart + k];
      if ((k > 0 && xyzIndex >= base.vertices.length / 3) ||
          (k > 0 && uvIndex >= other.vertices.length / 3) ||
          !Number.isSafeInteger(xyzIndex) || !Number.isSafeInteger(uvIndex)) {
        throw new Error('preview_invalid_source_vertex_index');
      }
      // XYZ and per-corner UV may have entirely different local vertex IDs.
      xyzPolys[cursor + k] = xyzIndex;
      uvPolys[cursor + k] = uvIndex;
    }
    sourceIds[i] = base.faceIds[sourceIndex];
    arities[i] = arity;
    offsets[i] = cursor;
    cursor += arity + 1;
    if (arity === 3) triangles += 1;
    else quads += 1;
  }
  offsets[requestedFaces] = cursor;
  const xyzExactPolys = xyzPolys.subarray(0, cursor);
  const uvExactPolys = uvPolys.subarray(0, cursor);
  const warning = 'PARTIAL ORIGINAL FACE SUBSET. HOLES EXPECTED. NOT A COMPLETE SURFACE, NOT LOD, NOT SCIENTIFIC QUALITY.';
  const provenance: PreviewProvenance = {
    schema: PREVIEW_SCHEMA, source_sha256: xyz.source_sha256,
    original_faces: count, shown_original_faces: requestedFaces,
    coverage_fraction: requestedFaces / count,
    source_face_ids_exact: true, changes_source_connectivity: false,
    complete_surface: false, scientific_quality_comparable: false,
    is_lod: false, warning,
  };
  const build = (original: MeshGeometry, connectivity: Uint32Array): MeshGeometry => ({
    ...original, points: [], cells: [], source_face_ids: [], cell_types: [],
    triangles, quads, warning,
    packed: { vertices: original.packed!.vertices, polys: connectivity,
      faceIds: sourceIds, arities, offsets },
  });
  return { xyz: build(xyz, xyzExactPolys), uv: build(uv, uvExactPolys), provenance };
}
