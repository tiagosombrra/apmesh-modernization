/** Opt-in, tightly bounded main-thread XYZ picker, never a scientific source of geometry. */
import type { MeshGeometry } from './contracts';
import { buildXyzBvh, prepareBvhPayload } from './xyzBvh';
import type { BvhPick } from './xyzBvh';

export const MAIN_BVH_MAX_FACES = 2_048;
export const MAIN_BVH_MAX_VERTICES = 8_192;
export const MAIN_BVH_MAX_INPUT_BYTES = 1_048_576;
export const MAIN_BVH_METHOD = 'EXPERIMENTAL_XYZ_BVH_MAIN' as const;

export interface MainBvhProfile {
  sourceFaces: number;
  indexedFaces: number;
  excludedQuads: number;
  nodeCount: number;
  copiedInputBytes: number;
  preparationMs: number;
  indexBuildMs: number;
  totalBuildMs: number;
  scope: 'MAIN_THREAD_PREPARE_AND_BUILD_NOT_GPU_RSS_OR_SCIENTIFIC_GEOMETRY';
}

export interface MainBvhPicker {
  readonly profile: MainBvhProfile;
  pick(near: readonly number[], far: readonly number[], showTri: boolean, showQuad: boolean): BvhPick;
}

/**
 * Reject large or malformed storage before copying buffers or blocking the UI.
 * This is strictly an experimental small-mesh variant; no automatic dispatch.
 */
export function createBoundedXyzBvhMain(mesh: MeshGeometry): MainBvhPicker | null {
  if (mesh.coordinate_space !== 'xyz') return null;
  const faceCount = mesh.packed ? mesh.packed.faceIds.length : mesh.cells.length;
  const vertexCount = mesh.packed ? mesh.packed.vertices.length / 3 : mesh.points.length;
  if (!Number.isSafeInteger(faceCount) || faceCount < 1 || faceCount > MAIN_BVH_MAX_FACES ||
      !Number.isSafeInteger(vertexCount) || vertexCount < 3 || vertexCount > MAIN_BVH_MAX_VERTICES ||
      faceCount !== mesh.triangles + mesh.quads) return null;
  if (mesh.packed) {
    const {vertices, polys, offsets, arities, faceIds} = mesh.packed;
    const bytes = vertices.byteLength + polys.byteLength + offsets.byteLength +
      arities.byteLength + faceIds.byteLength;
    if (bytes > MAIN_BVH_MAX_INPUT_BYTES || polys.length > faceCount * 5 ||
        offsets.length !== faceCount + 1 || arities.length !== faceCount) return null;
  } else if (mesh.cells.some(c => c.length !== 3 && c.length !== 4)) {
    return null;
  }
  const started = performance.now();
  const payload = prepareBvhPayload(mesh);
  if (!payload) return null;
  const preparedAt = performance.now();
  const bytes = payload.vertices.byteLength + payload.polys.byteLength +
    payload.offsets.byteLength + payload.arities.byteLength + payload.sourceIds.byteLength;
  if (bytes > MAIN_BVH_MAX_INPUT_BYTES) return null;
  const index = buildXyzBvh(payload, {allowUnindexedWarpedQuads:true});
  if (!index) return null;
  const builtAt = performance.now();
  return {
    profile: {
      sourceFaces:index.faceCount,
      indexedFaces:index.indexedFaceCount,
      excludedQuads:index.excludedQuadCount,
      nodeCount:index.nodeCount,
      copiedInputBytes:bytes,
      preparationMs:preparedAt-started,
      indexBuildMs:builtAt-preparedAt,
      totalBuildMs:builtAt-started,
      scope:'MAIN_THREAD_PREPARE_AND_BUILD_NOT_GPU_RSS_OR_SCIENTIFIC_GEOMETRY',
    },
    pick(near,far,showTri,showQuad) {
      return index.pick(near,far,showTri,showQuad);
    },
  };
}
