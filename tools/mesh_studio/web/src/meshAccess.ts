/** Typed display accessors; do not infer patches or reconstitute source float64. */
import type { MeshGeometry } from './contracts';

export function meshPointCount(mesh: MeshGeometry): number {
  return mesh.packed ? mesh.packed.vertices.length / 3 : mesh.points.length;
}

export function meshFaceCount(mesh: MeshGeometry): number {
  return mesh.packed ? mesh.packed.faceIds.length : mesh.cells.length;
}

export function meshFaceIds(mesh: MeshGeometry): ReadonlyArray<number> | Uint32Array {
  return mesh.packed?.faceIds ?? mesh.source_face_ids;
}

export function meshFaceIdAt(mesh: MeshGeometry, index: number): number {
  return mesh.packed ? mesh.packed.faceIds[index] : mesh.source_face_ids[index];
}

export function meshFaceIndex(mesh: MeshGeometry, sourceId: number): number {
  return mesh.packed ? mesh.packed.faceIds.indexOf(sourceId) : mesh.source_face_ids.indexOf(sourceId);
}

export function meshFaceArity(mesh: MeshGeometry, index: number): number {
  return mesh.packed ? mesh.packed.arities[index] : mesh.cells[index].length;
}

export function meshCellKind(mesh: MeshGeometry, index: number): 'triangle' | 'quad' {
  if (mesh.packed) return mesh.packed.arities[index] === 3 ? 'triangle' : 'quad';
  return mesh.cell_types[index];
}

export function meshFaceCorners(mesh: MeshGeometry, index: number): number[] {
  if (!mesh.packed) return mesh.cells[index];
  const begin = mesh.packed.offsets[index];
  const arity = mesh.packed.arities[index];
  return Array.from(mesh.packed.polys.subarray(begin + 1, begin + 1 + arity));
}

export function meshPointAt(mesh: MeshGeometry, index: number): number[] {
  if (!mesh.packed) return mesh.points[index];
  const offset = index * 3;
  return [mesh.packed.vertices[offset], mesh.packed.vertices[offset + 1],
    mesh.packed.vertices[offset + 2]];
}
