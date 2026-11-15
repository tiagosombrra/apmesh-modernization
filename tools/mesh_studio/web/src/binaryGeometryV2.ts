/** APMSH002: bounded little-endian zero-copy Float32 display transport. */
import type { MeshGeometry, Space } from './contracts';

const MAGIC = 'APMSH002';
const SCHEMA = 'apmesh.meshstudio.geometry.bin.v2';
const MAX_BYTES = 32 * 1024 * 1024;
const MAX_META = 4096;
const HEADER_SIZE = 32;

export function crc32(bytes: Uint8Array): number {
  let crc = 0xFFFFFFFF;
  for (let i = 0; i < bytes.length; i += 1) {
    crc ^= bytes[i];
    for (let bit = 0; bit < 8; bit += 1) {
      crc = ((crc >>> 1) ^ ((crc & 1) ? 0xEDB88320 : 0)) >>> 0;
    }
  }
  return (crc ^ 0xFFFFFFFF) >>> 0;
}

/** Return typed views into the response buffer; never inflate million-vertex JS arrays. */
export function decodeGeometryV2(buffer: ArrayBuffer, expectedSpace: Space): MeshGeometry {
  if (buffer.byteLength <= HEADER_SIZE + 4 || buffer.byteLength > MAX_BYTES) {
    throw new Error('invalid_v2_size');
  }
  const data = new DataView(buffer);
  const bytes = new Uint8Array(buffer);
  const magic = String.fromCharCode(...bytes.subarray(0, 8));
  if (magic !== MAGIC) throw new Error('invalid_v2_magic');
  const metaLength = data.getUint32(8, true);
  const pointCount = data.getUint32(12, true);
  const faceCount = data.getUint32(16, true);
  const wordCount = data.getUint32(20, true);
  const padding = data.getUint32(24, true);
  const flags = data.getUint32(28, true);
  if (!metaLength || metaLength > MAX_META || !pointCount || !faceCount ||
      pointCount > 3_000_000 || faceCount > 2_000_000 || flags !== 0 ||
      padding !== (4 - (metaLength % 4)) % 4) {
    throw new Error('invalid_v2_header');
  }
  const expected = HEADER_SIZE + metaLength + padding + pointCount * 12 +
    wordCount * 4 + faceCount * 5 + 4;
  if (expected !== buffer.byteLength) throw new Error('invalid_v2_length');
  const claimedCrc = data.getUint32(buffer.byteLength - 4, true);
  if (claimedCrc !== crc32(bytes.subarray(0, buffer.byteLength - 4))) {
    throw new Error('invalid_v2_crc');
  }
  const metadata = JSON.parse(new TextDecoder('utf-8', { fatal: true })
    .decode(bytes.subarray(HEADER_SIZE, HEADER_SIZE + metaLength))) as {
      schema?: string; wire_schema?: string; source_sha256?: string;
      source_patch_ownership?: string; coordinate_space?: string;
      triangles?: number; quads?: number; warning?: string;
    };
  if (metadata.wire_schema !== SCHEMA ||
      metadata.schema !== 'apmesh.meshstudio.web.v1' ||
      metadata.coordinate_space !== expectedSpace ||
      typeof metadata.source_sha256 !== 'string' ||
      !/^[0-9a-f]{64}$/.test(metadata.source_sha256) ||
      typeof metadata.triangles !== 'number' || !Number.isSafeInteger(metadata.triangles) ||
      typeof metadata.quads !== 'number' || !Number.isSafeInteger(metadata.quads) ||
      (metadata.triangles ?? 0) + (metadata.quads ?? 0) !== faceCount) {
    throw new Error('invalid_v2_origin');
  }
  for (let i = 0; i < padding; i += 1) {
    if (bytes[HEADER_SIZE + metaLength + i] !== 0) throw new Error('invalid_v2_padding');
  }
  // The header is 32-byte aligned and padding preserves 4-byte alignment.
  const pointStart = HEADER_SIZE + metaLength + padding;
  const polyStart = pointStart + pointCount * 12;
  const idsStart = polyStart + wordCount * 4;
  const arityStart = idsStart + faceCount * 4;
  const vertices = new Float32Array(buffer, pointStart, pointCount * 3);
  const polys = new Uint32Array(buffer, polyStart, wordCount);
  const faceIds = new Uint32Array(buffer, idsStart, faceCount);
  const arities = new Uint8Array(buffer, arityStart, faceCount);
  const offsets = new Uint32Array(faceCount + 1);
  const seen = new Uint8Array(faceCount);
  for (let i = 0; i < vertices.length; i += 1) {
    if (!Number.isFinite(vertices[i])) throw new Error('invalid_v2_coordinate');
  }
  let cursor = 0;
  let triangles = 0;
  let quads = 0;
  for (let index = 0; index < faceCount; index += 1) {
    const id = faceIds[index];
    if (id >= faceCount || seen[id]) throw new Error('invalid_v2_original_face_id');
    seen[id] = 1;
    const arity = arities[index];
    if (!(arity === 3 || arity === 4) || cursor + arity + 1 > wordCount ||
        polys[cursor] !== arity) throw new Error('invalid_v2_cell_arity');
    offsets[index] = cursor;
    const current = new Set<number>();
    for (let corner = 1; corner <= arity; corner += 1) {
      const point = polys[cursor + corner];
      if (point >= pointCount || current.has(point)) throw new Error('invalid_v2_cell_index');
      current.add(point);
    }
    cursor += arity + 1;
    if (arity === 3) triangles += 1;
    else quads += 1;
  }
  offsets[faceCount] = cursor;
  if (cursor !== wordCount || triangles !== metadata.triangles || quads !== metadata.quads) {
    throw new Error('invalid_v2_inventory');
  }
  return {
    schema: metadata.schema, source_sha256: metadata.source_sha256,
    source_patch_ownership: metadata.source_patch_ownership ?? 'UNKNOWN_FROM_OBJ',
    coordinate_space: expectedSpace,
    // These empty arrays indicate packed storage; all readers use meshAccess.
    points: [], cells: [], source_face_ids: [], cell_types: [],
    packed: { vertices, polys, faceIds, arities, offsets },
    triangles, quads,
    warning: metadata.warning ?? 'Float32 display only; no scientific source certification',
  };
}
