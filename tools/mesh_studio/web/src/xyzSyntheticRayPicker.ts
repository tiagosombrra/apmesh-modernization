/** Fast ray-to-original-cell lookup restricted to the verified SYNTHETIC heightfield. */
import type { MeshGeometry } from './contracts';

export const XYZ_PICKER_METHOD = 'SYNTHETIC_XYZ_GRID_RAY' as const;
export type XyzRayResult =
  | { kind: 'hit'; sourceFaceId: number; testedFaces: number }
  | { kind: 'miss'; testedFaces: number }
  | { kind: 'ambiguous'; testedFaces: number };
export interface XyzSyntheticPicker {
  readonly sourceFaceCount: number;
  readonly scope: typeof XYZ_PICKER_METHOD;
  pick(near: readonly number[], far: readonly number[], showQuad: boolean): XyzRayResult;
}

const EPS = 1e-8;
const EDGE_TOL = 2e-6;

/** Triangle intersection with an explicit edge-ambiguity flag. */
function triangleHit(vertices: Float32Array, a: number, b: number, c: number,
                     origin: number[], direction: number[]): { t: number; edge: boolean } | null {
  const ax = vertices[a * 3], ay = vertices[a * 3 + 1], az = vertices[a * 3 + 2];
  const ex = vertices[b * 3] - ax, ey = vertices[b * 3 + 1] - ay, ez = vertices[b * 3 + 2] - az;
  const fx = vertices[c * 3] - ax, fy = vertices[c * 3 + 1] - ay, fz = vertices[c * 3 + 2] - az;
  const hx = direction[1] * fz - direction[2] * fy;
  const hy = direction[2] * fx - direction[0] * fz;
  const hz = direction[0] * fy - direction[1] * fx;
  const det = ex * hx + ey * hy + ez * hz;
  if (Math.abs(det) < 1e-11) return null;
  const inv = 1 / det;
  const sx = origin[0] - ax, sy = origin[1] - ay, sz = origin[2] - az;
  const u = (sx * hx + sy * hy + sz * hz) * inv;
  if (u < -EPS || u > 1 + EPS) return null;
  const qx = sy * ez - sz * ey, qy = sz * ex - sx * ez, qz = sx * ey - sy * ex;
  const v = (direction[0] * qx + direction[1] * qy + direction[2] * qz) * inv;
  if (v < -EPS || u + v > 1 + EPS) return null;
  const t = (fx * qx + fy * qy + fz * qz) * inv;
  if (t < -EPS || t > 1 + EPS) return null;
  return { t, edge: u <= EDGE_TOL || v <= EDGE_TOL || (1 - u - v) <= EDGE_TOL };
}

function segmentBounds(origin: number[], direction: number[], min: number[], max: number[]): [number, number] | null {
  let lo = 0, hi = 1;
  for (let i = 0; i < 3; i += 1) {
    if (Math.abs(direction[i]) < 1e-14) {
      if (origin[i] < min[i] - EPS || origin[i] > max[i] + EPS) return null;
      continue;
    }
    const t0 = (min[i] - origin[i]) / direction[i];
    const t1 = (max[i] - origin[i]) / direction[i];
    lo = Math.max(lo, Math.min(t0, t1));
    hi = Math.min(hi, Math.max(t0, t1));
    if (hi < lo) return null;
  }
  return [lo, hi];
}

/**
 * Pure, 0-extra-index-memory 2D DDA over a structured synthetic 3D heightfield.
 * All source QUAD cells remain intact. General real meshes MUST use vtkCellPicker.
 */
export function buildSyntheticXyzRayPicker(mesh: MeshGeometry): XyzSyntheticPicker | null {
  if (mesh.coordinate_space !== 'xyz' || !mesh.packed ||
      mesh.source_sha256 !== '0'.repeat(64) ||
      mesh.source_patch_ownership !== 'NOT_APMESH_SOURCE' ||
      mesh.quads !== 500_000 || mesh.triangles !== 0) return null;
  const data = mesh.packed, count = 500_000;
  const width = Math.floor(Math.sqrt(count));
  const height = Math.ceil(count / width);
  const coords = data.vertices;
  if (coords.length !== (width + 1) * (height + 1) * 3 ||
      data.polys.length !== count * 5 || data.faceIds.length !== count ||
      data.arities.length !== count || data.offsets.length !== count + 1) return null;
  // Strict one-time source-layout qualification. No source-geometry claims are inferred.
  let minZ = Infinity, maxZ = -Infinity;
  for (let i = 0; i < coords.length / 3; i += 1) {
    const x = i % (width + 1), y = Math.floor(i / (width + 1));
    const off = i * 3;
    if (Math.abs(coords[off] - x / width) > 2e-6 ||
        Math.abs(coords[off + 1] - y / height) > 2e-6 ||
        !Number.isFinite(coords[off + 2])) return null;
    minZ = Math.min(minZ, coords[off + 2]);
    maxZ = Math.max(maxZ, coords[off + 2]);
  }
  for (let i = 0; i < count; i += 1) {
    const cell = i * 5;
    const first = Math.floor(i / width) * (width + 1) + (i % width);
    if (data.faceIds[i] !== i || data.arities[i] !== 4 ||
        data.offsets[i] !== cell || data.polys[cell] !== 4 ||
        data.polys[cell + 1] !== first || data.polys[cell + 2] !== first + 1 ||
        data.polys[cell + 3] !== first + width + 2 ||
        data.polys[cell + 4] !== first + width + 1) return null;
  }
  if (data.offsets[count] !== data.polys.length) return null;
  return {
    sourceFaceCount: count, scope: XYZ_PICKER_METHOD,
    pick(near, far, showQuad): XyzRayResult {
      if (!showQuad) return { kind: 'miss', testedFaces: 0 };
      if (near.length < 3 || far.length < 3 ||
          !near.every(Number.isFinite) || !far.every(Number.isFinite)) {
        return { kind: 'ambiguous', testedFaces: 0 };
      }
      const origin = [near[0], near[1], near[2]];
      const direction = origin.map((v, i) => far[i] - v);
      if (Math.hypot(...direction) < 1e-10) return { kind: 'ambiguous', testedFaces: 0 };
      const bounds = segmentBounds(origin, direction, [0, 0, minZ - 1e-5], [1, 1, maxZ + 1e-5]);
      if (!bounds) return { kind: 'miss', testedFaces: 0 };
      const [tStart, tEnd] = bounds;
      // A ray collinear with a source grid edge cannot be assigned to one face.
      if ((Math.abs(direction[0]) < 1e-12 &&
           Math.abs(origin[0] * width - Math.round(origin[0] * width)) < 2e-5) ||
          (Math.abs(direction[1]) < 1e-12 &&
           Math.abs(origin[1] * height - Math.round(origin[1] * height)) < 2e-5)) {
        return { kind: 'ambiguous', testedFaces: 0 };
      }
      const stepX = Math.sign(direction[0]), stepY = Math.sign(direction[1]);
      const x0 = origin[0] + direction[0] * Math.min(tEnd, tStart + 1e-8);
      const y0 = origin[1] + direction[1] * Math.min(tEnd, tStart + 1e-8);
      let cellX = Math.max(0, Math.min(width - 1, Math.floor(x0 * width)));
      let cellY = Math.max(0, Math.min(height - 1, Math.floor(y0 * height)));
      const nextTX = () => stepX === 0 ? Infinity :
        (((stepX > 0 ? cellX + 1 : cellX) / width) - origin[0]) / direction[0];
      const nextTY = () => stepY === 0 ? Infinity :
        (((stepY > 0 ? cellY + 1 : cellY) / height) - origin[1]) / direction[1];
      let tested = 0, selected: number | null = null, bestT = Infinity, ambiguity = false;
      for (let i = 0; i <= width + height + 4; i += 1) {
        if (cellX < 0 || cellX >= width || cellY < 0 || cellY >= height) break;
        const index = cellY * width + cellX;
        if (index < count) {
          tested += 1;
          const offset = index * 5;
          const a = data.polys[offset + 1], b = data.polys[offset + 2];
          const c = data.polys[offset + 3], d = data.polys[offset + 4];
          for (const hit of [triangleHit(coords, a, b, c, origin, direction),
                             triangleHit(coords, a, c, d, origin, direction)]) {
            if (!hit || hit.t < tStart - EPS || hit.t > tEnd + EPS) continue;
            if (hit.edge) ambiguity = true;
            if (Math.abs(hit.t - bestT) < 2e-7 && selected !== null && selected !== index) ambiguity = true;
            if (hit.t < bestT) { bestT = hit.t; selected = index; }
          }
        }
        const tx = nextTX(), ty = nextTY();
        const next = Math.min(tx, ty);
        if (next > tEnd + EPS || !Number.isFinite(next)) break;
        if (Math.abs(tx - ty) < 1e-10) { cellX += stepX; cellY += stepY; ambiguity = true; }
        else if (tx < ty) cellX += stepX;
        else cellY += stepY;
      }
      if (ambiguity) return { kind: 'ambiguous', testedFaces: tested };
      return selected === null ? { kind: 'miss', testedFaces: tested } :
        { kind: 'hit', sourceFaceId: data.faceIds[selected], testedFaces: tested };
    },
  };
}
