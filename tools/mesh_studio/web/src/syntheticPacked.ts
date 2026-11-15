/** Bounded synthetic graphics fixture, never a real APMesh scientific mesh. */
import type { MeshGeometry } from './contracts';

export function syntheticPackedScene(cells: number): {
  xyz: MeshGeometry; uv: MeshGeometry; generationMs: number;
} {
  if (![1_000, 50_000, 500_000].includes(cells)) throw new Error('synthetic_size_not_approved');
  const start = performance.now();
  const width = Math.floor(Math.sqrt(cells));
  const height = Math.ceil(cells / width);
  const pointCount = (width + 1) * (height + 1);
  const positions = new Float32Array(pointCount * 3);
  const flatUv = new Float32Array(pointCount * 3);
  for (let y = 0; y <= height; y += 1) {
    const v = y / height;
    for (let x = 0; x <= width; x += 1) {
      const u = x / width;
      const off = (y * (width + 1) + x) * 3;
      positions[off] = u;
      positions[off + 1] = v;
      positions[off + 2] = 0.08 * Math.sin(2 * Math.PI * u) * Math.cos(2 * Math.PI * v);
      flatUv[off] = u;
      flatUv[off + 1] = v;
    }
  }
  const polys = new Uint32Array(cells * 5);
  const faceIds = new Uint32Array(cells);
  const arities = new Uint8Array(cells);
  const offsets = new Uint32Array(cells + 1);
  let face = 0;
  for (let row = 0; row < height && face < cells; row += 1) {
    for (let col = 0; col < width && face < cells; col += 1) {
      const first = row * (width + 1) + col;
      const offset = face * 5;
      polys.set([4, first, first + 1, first + width + 2, first + width + 1], offset);
      faceIds[face] = face;
      arities[face] = 4;
      offsets[face] = offset;
      face += 1;
    }
  }
  offsets[cells] = cells * 5;
  const common = {
    schema: 'apmesh.meshstudio.web.v1', source_sha256: '0'.repeat(64),
    source_patch_ownership: 'NOT_APMESH_SOURCE',
    points: [], cells: [], source_face_ids: [], cell_types: [],
    triangles: 0, quads: cells,
    warning: 'SYNTHETIC VIEWER STRESS ONLY. Not a source experiment or accepted adaptive epoch.',
  };
  return {
    xyz: { ...common, coordinate_space: 'xyz',
      packed: { vertices: positions, polys, faceIds, arities, offsets } },
    uv: { ...common, coordinate_space: 'uv',
      packed: { vertices: flatUv, polys, faceIds, arities, offsets } },
    generationMs: performance.now() - start,
  };
}
