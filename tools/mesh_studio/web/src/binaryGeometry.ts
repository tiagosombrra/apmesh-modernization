import type { MeshGeometry, Space } from './contracts';

const MAGIC = 'APMSH001';
const MAX_BYTES = 32 * 1024 * 1024;
const MAX_META = 4096;

/** Decode transport-only Float32 geometry; Python remains the numerical authority. */
export function decodeGeometry(buffer: ArrayBuffer, expectedSpace: Space): MeshGeometry {
  if (buffer.byteLength < 24 || buffer.byteLength > MAX_BYTES) throw new Error('invalid_binary_size');
  const bytes = new Uint8Array(buffer);
  const header = new DataView(buffer);
  const magic = String.fromCharCode(...bytes.slice(0, 8));
  if (magic !== MAGIC) throw new Error('invalid_binary_magic');
  const metaLength = header.getUint32(8, true);
  const pointCount = header.getUint32(12, true);
  const faceCount = header.getUint32(16, true);
  const polyWords = header.getUint32(20, true);
  if (!metaLength || metaLength > MAX_META || !pointCount || !faceCount ||
      pointCount > 3_000_000 || faceCount > 2_000_000) throw new Error('invalid_binary_dimensions');
  const expected = 24 + metaLength + pointCount * 12 + polyWords * 4 + faceCount * 5;
  if (expected !== buffer.byteLength) throw new Error('invalid_binary_length');
  const metaText = new TextDecoder('utf-8', { fatal: true }).decode(bytes.slice(24, 24 + metaLength));
  const metadata = JSON.parse(metaText) as Partial<MeshGeometry> & { wire_schema?: string };
  const schema = metadata.schema;
  const sourceSha = metadata.source_sha256;
  if (metadata.wire_schema !== 'apmesh.meshstudio.geometry.bin.v1' ||
      metadata.coordinate_space !== expectedSpace ||
      typeof sourceSha !== 'string' || !/^[0-9a-f]{64}$/.test(sourceSha) ||
      schema !== 'apmesh.meshstudio.web.v1') throw new Error('invalid_binary_origin');
  let offset = 24 + metaLength;
  const points: number[][] = [];
  for (let i = 0; i < pointCount; i += 1) {
    const point = [header.getFloat32(offset, true), header.getFloat32(offset + 4, true),
      header.getFloat32(offset + 8, true)];
    if (!point.every(Number.isFinite)) throw new Error('nonfinite_render_vertex');
    points.push(point);
    offset += 12;
  }
  const words: number[] = [];
  for (let i = 0; i < polyWords; i += 1) {
    words.push(header.getUint32(offset, true));
    offset += 4;
  }
  const ids: number[] = [];
  for (let i = 0; i < faceCount; i += 1) {
    ids.push(header.getUint32(offset, true));
    offset += 4;
  }
  const idSet = new Set(ids);
  if (idSet.size !== faceCount || ids.some((id) => id >= faceCount)) throw new Error('invalid_source_face_ids');
  const cells: number[][] = [];
  const cell_types: MeshGeometry['cell_types'] = [];
  let at = 0;
  for (let i = 0; i < faceCount; i += 1) {
    const arity = header.getUint8(offset + i);
    if ((arity !== 3 && arity !== 4) || at >= words.length || words[at] !== arity ||
        at + arity >= words.length) throw new Error('invalid_binary_faces');
    const face = words.slice(at + 1, at + 1 + arity);
    if (face.some((id) => id >= pointCount) || new Set(face).size !== arity) throw new Error('invalid_face_indices');
    cells.push(face);
    cell_types.push(arity === 3 ? 'triangle' : 'quad');
    at += arity + 1;
  }
  if (at !== words.length ||
      cell_types.filter((kind) => kind === 'triangle').length !== metadata.triangles ||
      cell_types.filter((kind) => kind === 'quad').length !== metadata.quads) {
    throw new Error('invalid_element_inventory');
  }
  return {
    schema,
    source_sha256: sourceSha,
    source_patch_ownership: metadata.source_patch_ownership ?? 'UNKNOWN_FROM_OBJ',
    coordinate_space: expectedSpace,
    points, cells, source_face_ids: ids, cell_types,
    triangles: metadata.triangles ?? 0, quads: metadata.quads ?? 0,
    warning: metadata.warning ?? 'Float32 visualization, not scientific geometry.',
  };
}
