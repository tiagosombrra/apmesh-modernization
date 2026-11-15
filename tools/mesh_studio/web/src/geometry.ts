/** Versioned, cacheable visualization buffers; never modify scientific coordinates. */
import type { MeshGeometry } from './contracts';
import { meshCellKind, meshFaceCount, meshFaceCorners, meshFaceIdAt, meshPointCount } from './meshAccess';

export interface RenderCells {
  points: Float32Array;
  polys: Uint32Array;
  colorBytes: Uint8Array;
  sourceIds: number[] | Uint32Array;
}

interface Prepared {
  points: Float32Array;
  variants: Map<number, RenderCells>;
}

// Cache is owned by the immutable geometry object identity and released by GC.
const cache = new WeakMap<MeshGeometry, Prepared>();
const QUAD_COLOR = [51, 151, 177, 255] as const;
const TRI_COLOR = [224, 168, 94, 255] as const;

function prepare(payload: MeshGeometry): Prepared {
  const cached = cache.get(payload);
  if (cached) return cached;
  if (payload.packed) {
    const packed = payload.packed;
    if (packed.vertices.length % 3 !== 0 || packed.faceIds.length !== packed.arities.length ||
        packed.offsets.length !== packed.faceIds.length + 1) {
      throw new Error('invalid_typed_geometry');
    }
    const result: Prepared = { points: packed.vertices, variants: new Map() };
    cache.set(payload, result);
    return result;
  }
  if (payload.cells.length !== payload.source_face_ids.length ||
      payload.cells.length !== payload.cell_types.length ||
      payload.points.length === 0) {
    throw new Error('invalid_cell_identity');
  }
  const points = new Float32Array(payload.points.length * 3);
  for (let i = 0; i < payload.points.length; i += 1) {
    const vertex = payload.points[i];
    if (vertex.length !== 3 || vertex.some((v) => !Number.isFinite(v))) {
      throw new Error('invalid_visual_vertex');
    }
    const offset = i * 3;
    points[offset] = vertex[0];
    points[offset + 1] = vertex[1];
    points[offset + 2] = vertex[2];
  }
  const result: Prepared = { points, variants: new Map() };
  cache.set(payload, result);
  return result;
}

/** Reuses one typed XYZ/UV point buffer for the entire lifetime of the model. */
export function vtkPointBuffer(payload: MeshGeometry): Float32Array {
  return prepare(payload).points;
}

/** Build filtered, original-face-ID-preserving VTK cell arrays exactly once. */
export function asVtkCells(
  payload: MeshGeometry, showTriangle: boolean, showQuad: boolean,
): RenderCells {
  const prepared = prepare(payload);
  const mask = (showTriangle ? 1 : 0) | (showQuad ? 2 : 0);
  const prior = prepared.variants.get(mask);
  if (prior) return prior;
  if (payload.packed && (payload.triangles === 0 || showTriangle) &&
      (payload.quads === 0 || showQuad)) {
    const typed = payload.packed;
    const colors = new Uint8Array(typed.faceIds.length * 4);
    for (let i = 0; i < typed.faceIds.length; i += 1) {
      colors.set(typed.arities[i] === 4 ? QUAD_COLOR : TRI_COLOR, i * 4);
    }
    const result = { points: prepared.points, polys: typed.polys,
      colorBytes: colors, sourceIds: typed.faceIds };
    prepared.variants.set(mask, result);
    return result;
  }
  let faceCount = 0;
  let wordCount = 0;
  for (let i = 0; i < meshFaceCount(payload); i += 1) {
    const kind = meshCellKind(payload, i);
    if (kind !== 'triangle' && kind !== 'quad') throw new Error('invalid_cell_type');
    if ((kind === 'triangle' && !showTriangle) || (kind === 'quad' && !showQuad)) continue;
    const corners = meshFaceCorners(payload, i);
    if (corners.length !== (kind === 'triangle' ? 3 : 4)) throw new Error('invalid_cell_arity');
    if (!corners.every((v) => Number.isSafeInteger(v) && v >= 0 && v < meshPointCount(payload))) {
      throw new Error('foreign_cell_index');
    }
    const originalId = meshFaceIdAt(payload, i);
    if (!Number.isSafeInteger(originalId) || originalId < 0) throw new Error('invalid_source_face_id');
    faceCount += 1;
    wordCount += corners.length + 1;
  }
  const polys = new Uint32Array(wordCount);
  const colorBytes = new Uint8Array(faceCount * 4);
  const sourceIds = new Array<number>(faceCount);
  let word = 0;
  let outputFace = 0;
  for (let i = 0; i < meshFaceCount(payload); i += 1) {
    const kind = meshCellKind(payload, i);
    if ((kind === 'triangle' && !showTriangle) || (kind === 'quad' && !showQuad)) continue;
    const corners = meshFaceCorners(payload, i);
    polys[word] = corners.length;
    word += 1;
    for (const pointId of corners) {
      polys[word] = pointId;
      word += 1;
    }
    colorBytes.set(kind === 'quad' ? QUAD_COLOR : TRI_COLOR, outputFace * 4);
    sourceIds[outputFace] = meshFaceIdAt(payload, i);
    outputFace += 1;
  }
  const result = { points: prepared.points, polys, colorBytes, sourceIds };
  prepared.variants.set(mask, result);
  return result;
}
