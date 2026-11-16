/** Experimental, bounded source-face BVH. Geometry is display Float32, never a scientific oracle. */
import type { MeshGeometry } from './contracts';

export const BVH_MAX_FACES = 100_000;
export const BVH_METHOD = 'EXPERIMENTAL_XYZ_BVH_WORKER' as const;
const LEAF_FACES = 8;
const HIT_EPS = 1e-8;
const TIE_EPS = 2e-7;
const EDGE_EPS = 2e-6;

export interface BvhPayload {
  vertices: Float32Array;
  polys: Uint32Array;
  offsets: Uint32Array;
  arities: Uint8Array;
  sourceIds: Uint32Array;
}
export type BvhPick =
  | { kind: 'hit'; sourceFaceId: number; testedFaces: number }
  | { kind: 'miss' | 'ambiguous'; testedFaces: number };

/** Copy the visualization buffers before transfer; never detach VTK or source-owned arrays. */
export function prepareBvhPayload(mesh: MeshGeometry): BvhPayload | null {
  if (mesh.coordinate_space !== 'xyz') return null;
  const count = mesh.packed ? mesh.packed.faceIds.length : mesh.cells.length;
  if (count === 0 || count > BVH_MAX_FACES || count !== mesh.triangles + mesh.quads) return null;
  if (mesh.packed) {
    return {
      vertices: mesh.packed.vertices.slice(), polys: mesh.packed.polys.slice(),
      offsets: mesh.packed.offsets.slice(), arities: mesh.packed.arities.slice(),
      sourceIds: mesh.packed.faceIds.slice(),
    };
  }
  if (mesh.cells.length !== mesh.source_face_ids.length || mesh.cells.length !== mesh.cell_types.length) return null;
  const vertices = new Float32Array(mesh.points.length * 3);
  for (let i = 0; i < mesh.points.length; i += 1) {
    if (mesh.points[i].length !== 3 || mesh.points[i].some(v => !Number.isFinite(v))) return null;
    vertices.set(mesh.points[i], i * 3);
  }
  const totalWords = mesh.cells.reduce((sum, cell) => sum + cell.length + 1, 0);
  const polys = new Uint32Array(totalWords), offsets = new Uint32Array(count + 1);
  const arities = new Uint8Array(count), sourceIds = new Uint32Array(count);
  let word = 0;
  for (let i = 0; i < count; i += 1) {
    const corners = mesh.cells[i];
    if ((corners.length !== 3 && corners.length !== 4) ||
        (corners.length === 3 ? 'triangle' : 'quad') !== mesh.cell_types[i]) return null;
    if (!Number.isSafeInteger(mesh.source_face_ids[i]) || mesh.source_face_ids[i] < 0 ||
        mesh.source_face_ids[i] > 0xffffffff) return null;
    offsets[i] = word;
    arities[i] = corners.length;
    sourceIds[i] = mesh.source_face_ids[i];
    polys[word++] = corners.length;
    for (const vertex of corners) {
      if (!Number.isSafeInteger(vertex) || vertex < 0 || vertex >= mesh.points.length) return null;
      polys[word++] = vertex;
    }
  }
  offsets[count] = word;
  return { vertices, polys, offsets, arities, sourceIds };
}

interface BvhNode {
  min: [number, number, number];
  max: [number, number, number];
  start: number;
  end: number;
  left: number;
  right: number;
}
export interface BvhIndex {
  readonly faceCount: number;
  readonly nodeCount: number;
  pick(near: readonly number[], far: readonly number[], showTri: boolean, showQuad: boolean): BvhPick;
}

type Vec3 = [number, number, number];
const subtract = (a: Vec3, b: Vec3): Vec3 => [a[0]-b[0], a[1]-b[1], a[2]-b[2]];
const cross = (a: Vec3, b: Vec3): Vec3 => [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
const dot = (a: Vec3, b: Vec3) => a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
const norm = (v: Vec3) => Math.hypot(...v);

function triangleIntersection(points: Vec3[], direction: Vec3, origin: Vec3, a: number, b: number, c: number):
    { t: number; edge: boolean } | null {
  const v0 = points[a], e1 = subtract(points[b], v0), e2 = subtract(points[c], v0);
  const p = cross(direction, e2), determinant = dot(e1, p);
  if (Math.abs(determinant) < 1e-14) return null;
  const inv = 1 / determinant, from = subtract(origin, v0);
  const u = dot(from, p) * inv;
  if (u < -HIT_EPS || u > 1 + HIT_EPS) return null;
  const q = cross(from, e1), v = dot(direction, q) * inv;
  if (v < -HIT_EPS || u + v > 1 + HIT_EPS) return null;
  const t = dot(e2, q) * inv;
  if (!Number.isFinite(t) || t < -HIT_EPS || t > 1 + HIT_EPS) return null;
  return { t, edge: u <= EDGE_EPS || v <= EDGE_EPS || 1 - u - v <= EDGE_EPS };
}

function intersectBox(origin: Vec3, direction: Vec3, node: BvhNode, limit: number): boolean {
  let entry = 0, exit = Math.min(1, limit);
  for (let axis = 0; axis < 3; axis += 1) {
    const lo = node.min[axis] - 1e-7, hi = node.max[axis] + 1e-7;
    if (Math.abs(direction[axis]) < 1e-14) {
      if (origin[axis] < lo || origin[axis] > hi) return false;
      continue;
    }
    const t0 = (lo - origin[axis]) / direction[axis];
    const t1 = (hi - origin[axis]) / direction[axis];
    entry = Math.max(entry, Math.min(t0, t1));
    exit = Math.min(exit, Math.max(t0, t1));
    if (entry > exit) return false;
  }
  return true;
}

/**
 * All-or-nothing qualification: malformed connectivity, duplicate IDs, distorted QUADs,
 * degenerate faces and unsafe values fail closed. Input vertices remain patch-local.
 */
export function buildXyzBvh(data: BvhPayload): BvhIndex | null {
  const { vertices, polys, offsets, arities, sourceIds } = data;
  const count = sourceIds.length;
  if (!count || count > BVH_MAX_FACES || vertices.length % 3 !== 0 ||
      offsets.length !== count + 1 || arities.length !== count || offsets[0] !== 0 ||
      offsets[count] !== polys.length || vertices.length === 0 ||
      !Array.from(vertices).every(Number.isFinite) ||
      new Set(sourceIds).size !== count) return null;
  const pointCount = vertices.length / 3;
  const bounds = new Float32Array(count * 6), centroids = new Float32Array(count * 3);
  const corners = new Uint32Array(count * 4);
  for (let face = 0; face < count; face += 1) {
    const arity = arities[face], begin = offsets[face];
    if ((arity !== 3 && arity !== 4) || begin + arity + 1 !== offsets[face + 1] ||
        polys[begin] !== arity) return null;
    const pts: Vec3[] = [];
    const distinct = new Set<number>();
    for (let c = 0; c < arity; c += 1) {
      const id = polys[begin + 1 + c];
      if (id >= pointCount || distinct.has(id)) return null;
      distinct.add(id);
      corners[face * 4 + c] = id;
      pts.push([vertices[id * 3], vertices[id * 3 + 1], vertices[id * 3 + 2]]);
    }
    const edge0 = subtract(pts[1], pts[0]), edge1 = subtract(pts[2], pts[0]);
    const n = cross(edge0, edge1), lenN = norm(n);
    const extent = Math.max(...pts.flatMap((p, i) => pts.map((q, j) => i === j ? 0 : norm(subtract(p,q)))));
    if (!(extent > 0) || lenN <= 1e-10 * extent * extent) return null;
    if (arity === 4) {
      // Flat, strictly convex QUADs only. A warped or bow-tie face uses native VTK.
      if (Math.abs(dot(n, subtract(pts[3], pts[0]))) > 1e-5 * lenN * extent) return null;
      const other = cross(subtract(pts[2], pts[0]), subtract(pts[3], pts[0]));
      if (dot(n, other) <= 0 || norm(other) <= 1e-10 * extent * extent) return null;
      for (let i = 0; i < 4; i += 1) {
        const e0 = subtract(pts[(i + 1) % 4], pts[i]);
        const e1 = subtract(pts[(i + 2) % 4], pts[(i + 1) % 4]);
        if (dot(cross(e0, e1), n) <= 1e-10 * lenN * extent * extent) return null;
      }
    }
    for (let axis = 0; axis < 3; axis += 1) {
      const values = pts.map(p => p[axis]), lo = Math.min(...values), hi = Math.max(...values);
      bounds[face * 6 + axis] = lo;
      bounds[face * 6 + axis + 3] = hi;
      centroids[face * 3 + axis] = (lo + hi) / 2;
    }
  }
  const order = Array.from({ length: count }, (_, i) => i);
  const nodes: BvhNode[] = [];
  const build = (start: number, end: number): number => {
    const min: Vec3 = [Infinity, Infinity, Infinity], max: Vec3 = [-Infinity, -Infinity, -Infinity];
    for (let i = start; i < end; i += 1) {
      const face = order[i];
      for (let a = 0; a < 3; a += 1) {
        min[a] = Math.min(min[a], bounds[face*6+a]);
        max[a] = Math.max(max[a], bounds[face*6+a+3]);
      }
    }
    const id = nodes.length;
    nodes.push({ min, max, start, end, left: -1, right: -1 });
    if (end-start > LEAF_FACES) {
      const extents = max.map((x, axis) => x-min[axis]);
      const axis = extents.indexOf(Math.max(...extents));
      const sorted = order.slice(start, end).sort((a,b) => centroids[a*3+axis]-centroids[b*3+axis] || a-b);
      for (let i=0;i<sorted.length;i+=1) order[start+i] = sorted[i];
      const middle = start + Math.floor((end-start)/2);
      nodes[id].left = build(start, middle);
      nodes[id].right = build(middle, end);
    }
    return id;
  };
  build(0, count);
  return {
    faceCount: count, nodeCount: nodes.length,
    pick(near, far, showTri, showQuad): BvhPick {
      if (near.length !== 3 || far.length !== 3 ||
          !near.every(Number.isFinite) || !far.every(Number.isFinite)) return {kind:'ambiguous',testedFaces:0};
      const origin: Vec3 = [near[0],near[1],near[2]], direction: Vec3 =
        [far[0]-near[0],far[1]-near[1],far[2]-near[2]];
      if (norm(direction) <= 1e-12) return {kind:'ambiguous',testedFaces:0};
      let best = Infinity, selected: number | null = null, tied = false, boundary = false, tested = 0;
      const stack = [0];
      while (stack.length) {
        const node = nodes[stack.pop()!];
        if (!intersectBox(origin, direction, node, best + TIE_EPS)) continue;
        if (node.left !== -1) { stack.push(node.left, node.right); continue; }
        for (let i = node.start; i < node.end; i += 1) {
          const face = order[i], arity = arities[face];
          if ((arity === 3 && !showTri) || (arity === 4 && !showQuad)) continue;
          tested += 1;
          const ps: Vec3[] = [];
          for (let k = 0; k < arity; k += 1) {
            const v = corners[face*4+k];
            ps.push([vertices[v*3],vertices[v*3+1],vertices[v*3+2]]);
          }
          const hits = [triangleIntersection(ps,direction,origin,0,1,2)];
          if (arity === 4) hits.push(triangleIntersection(ps,direction,origin,0,2,3));
          for (const hit of hits) {
            if (!hit) continue;
            if (hit.t < best - TIE_EPS) {
              best = hit.t; selected = face; tied = false; boundary = hit.edge;
            } else if (Math.abs(hit.t-best) <= TIE_EPS) {
              if (selected !== face) tied = true;
              boundary ||= hit.edge;
            }
          }
        }
      }
      if (tied || boundary) return {kind:'ambiguous',testedFaces:tested};
      if (selected === null) return {kind:'miss',testedFaces:tested};
      return {kind:'hit',sourceFaceId:sourceIds[selected],testedFaces:tested};
    },
  };
}
