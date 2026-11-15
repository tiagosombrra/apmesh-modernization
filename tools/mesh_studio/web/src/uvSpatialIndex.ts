/** Optional UV-only binning. Ambiguous/unsupported geometry MUST use vtkCellPicker. */
import type { MeshGeometry } from './contracts';

export type UvQuery =
  | { kind: 'hit'; sourceFaceId: number; testedFaces: number }
  | { kind: 'miss'; testedFaces: number }
  | { kind: 'ambiguous'; testedFaces: number };

export interface UvIndex {
  readonly faceCount: number;
  readonly gridSize: number;
  pick(u: number, v: number, triangles: boolean, quads: boolean): UvQuery;
}

const MAX_INDEXED_FACES = 150_000;
const MAX_GRID = 128;
const MAX_REFERENCES = 1_000_000;
const EPSILON = 1e-10;

function inConvexPolygon(points: number[][], corners: number[], u: number, v: number): boolean {
  let sign = 0;
  for (let i = 0; i < corners.length; i += 1) {
    const a = points[corners[i]];
    const b = points[corners[(i + 1) % corners.length]];
    const cross = (b[0] - a[0]) * (v - a[1]) - (b[1] - a[1]) * (u - a[0]);
    if (Math.abs(cross) <= EPSILON) continue;
    const next = cross > 0 ? 1 : -1;
    if (sign && sign !== next) return false;
    sign = next;
  }
  return sign !== 0;
}

/**
 * Never infer patch ownership from UV coincidences. On overlapping charts,
 * unsupported cells or shared edges, return ambiguous and use the native picker.
 */
export function buildUvSpatialIndex(mesh: MeshGeometry): UvIndex | null {
  if (mesh.coordinate_space !== 'uv' || mesh.cells.length === 0 ||
      mesh.cells.length > MAX_INDEXED_FACES ||
      mesh.source_face_ids.length !== mesh.cells.length ||
      mesh.cell_types.length !== mesh.cells.length) return null;
  let minX = Infinity; let minY = Infinity;
  let maxX = -Infinity; let maxY = -Infinity;
  for (const point of mesh.points) {
    if (point.length !== 3 || point.some((n) => !Number.isFinite(n)) || Math.abs(point[2]) > 1e-8) return null;
    minX = Math.min(minX, point[0]); maxX = Math.max(maxX, point[0]);
    minY = Math.min(minY, point[1]); maxY = Math.max(maxY, point[1]);
  }
  const deltaX = maxX - minX; const deltaY = maxY - minY;
  if (deltaX <= 0 || deltaY <= 0) return null;
  const gridSize = Math.min(MAX_GRID, Math.max(4, Math.ceil(Math.sqrt(mesh.cells.length) / 2)));
  const bins = new Map<number, number[]>();
  const ranges: Array<[number, number, number, number]> = [];
  const clampedBin = (coordinate: number, min: number, delta: number) =>
    Math.max(0, Math.min(gridSize - 1, Math.floor((coordinate - min) / delta * gridSize)));
  let references = 0;
  if (new Set(mesh.source_face_ids).size !== mesh.cells.length ||
      mesh.source_face_ids.some((id) => !Number.isSafeInteger(id) || id < 0)) return null;
  for (let faceId = 0; faceId < mesh.cells.length; faceId += 1) {
    const corners = mesh.cells[faceId];
    if ((corners.length !== 3 && corners.length !== 4) ||
        corners.length !== (mesh.cell_types[faceId] === 'quad' ? 4 : 3) ||
        !corners.every((id) => Number.isSafeInteger(id) && id >= 0 && id < mesh.points.length)) {
      return null;
    }
    const points = corners.map((id) => mesh.points[id]);
    // A concave or self-intersecting polygon is not eligible for this fast path.
    let orientation = 0;
    for (let edge = 0; edge < points.length; edge += 1) {
      const a = points[edge], b = points[(edge + 1) % points.length];
      const c = points[(edge + 2) % points.length];
      const cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]);
      if (Math.abs(cross) <= EPSILON) return null;
      const direction = cross > 0 ? 1 : -1;
      if (orientation && orientation !== direction) return null;
      orientation = direction;
    }
    const bx0 = Math.min(...points.map((p) => p[0]));
    const bx1 = Math.max(...points.map((p) => p[0]));
    const by0 = Math.min(...points.map((p) => p[1]));
    const by1 = Math.max(...points.map((p) => p[1]));
    if (bx0 === bx1 || by0 === by1) return null;
    ranges.push([bx0, bx1, by0, by1]);
    const ix0 = clampedBin(bx0, minX, deltaX);
    const ix1 = clampedBin(bx1, minX, deltaX);
    const iy0 = clampedBin(by0, minY, deltaY);
    const iy1 = clampedBin(by1, minY, deltaY);
    references += (ix1 - ix0 + 1) * (iy1 - iy0 + 1);
    if (references > MAX_REFERENCES) return null;
    for (let y = iy0; y <= iy1; y += 1) for (let x = ix0; x <= ix1; x += 1) {
      const key = y * gridSize + x;
      const bucket = bins.get(key);
      if (bucket) bucket.push(faceId);
      else bins.set(key, [faceId]);
    }
  }
  return {
    faceCount: mesh.cells.length,
    gridSize,
    pick(u: number, v: number, triangles: boolean, quads: boolean): UvQuery {
      if (!Number.isFinite(u) || !Number.isFinite(v)) return { kind: 'ambiguous', testedFaces: 0 };
      if (u < minX - EPSILON || u > maxX + EPSILON ||
          v < minY - EPSILON || v > maxY + EPSILON) return { kind: 'miss', testedFaces: 0 };
      const x = clampedBin(u, minX, deltaX), y = clampedBin(v, minY, deltaY);
      const bucket = bins.get(y * gridSize + x) ?? [];
      let chosen: number | null = null;
      let candidates = 0;
      for (const faceId of bucket) {
        const kind = mesh.cell_types[faceId];
        if ((kind === 'triangle' && !triangles) || (kind === 'quad' && !quads)) continue;
        const [x0, x1, y0, y1] = ranges[faceId];
        if (u < x0 - EPSILON || u > x1 + EPSILON ||
            v < y0 - EPSILON || v > y1 + EPSILON) continue;
        candidates += 1;
        if (inConvexPolygon(mesh.points, mesh.cells[faceId], u, v)) {
          const id = mesh.source_face_ids[faceId];
          if (chosen !== null && chosen !== id) return { kind: 'ambiguous', testedFaces: candidates };
          chosen = id;
        }
      }
      return chosen === null ? { kind: 'miss', testedFaces: candidates } :
        { kind: 'hit', sourceFaceId: chosen, testedFaces: candidates };
    },
  };
}
