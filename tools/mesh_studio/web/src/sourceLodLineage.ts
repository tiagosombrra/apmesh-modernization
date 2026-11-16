/** A complete source-face partition for a POSSIBLE future LOD; no geometric LOD is created. */
import type { MeshGeometry } from './contracts';
import { meshFaceCount, meshFaceIds } from './meshAccess';

export const LINEAGE_SCHEMA = 'apmesh.meshstudio.source_face_partition.v1' as const;
export interface SourceFacePartition {
  readonly schema: typeof LINEAGE_SCHEMA;
  readonly source_sha256: string;
  readonly source_face_count: number;
  readonly aggregate_count: number;
  readonly offsets: Uint32Array;
  readonly original_face_ids: Uint32Array;
  readonly covers_every_original_face_exactly_once: true;
  readonly aggregate_geometry_defined: false;
  readonly is_geometric_lod: false;
  readonly metric_comparable: false;
  readonly classification: 'SYNTHETIC_STRUCTURED_GRID_ONLY';
}

/** Verify a bijective partition. A coarse group is NOT a valid geometric element. */
export function verifyFacePartition(sourceFaceIds: Uint32Array, offsets: Uint32Array,
                                    flatFaceIds: Uint32Array): void {
  const count = sourceFaceIds.length;
  if (count === 0 || count > 1_000_000 || offsets.length < 2 ||
      offsets.length > count + 1 || offsets[0] !== 0 ||
      offsets[offsets.length - 1] !== count || flatFaceIds.length !== count) {
    throw new Error('invalid_partition_inventory');
  }
  const ownership = new Map<number, number>();
  for (let i = 0; i < count; i += 1) {
    const id = sourceFaceIds[i];
    if (ownership.has(id)) throw new Error('duplicate_original_source_face');
    ownership.set(id, i);
  }
  const visited = new Uint8Array(count);
  for (let group = 0; group + 1 < offsets.length; group += 1) {
    const start = offsets[group], end = offsets[group + 1];
    if (start >= end || end > count) throw new Error('empty_or_overlapping_group_range');
    for (let i = start; i < end; i += 1) {
      const id = flatFaceIds[i];
      const original = ownership.get(id);
      if (original === undefined) throw new Error('foreign_original_face_id');
      if (visited[original]) throw new Error('duplicate_aggregate_ownership');
      visited[original] = 1;
    }
  }
  if (visited.some((value) => value !== 1)) throw new Error('uncovered_source_face');
}

/**
 * Tile a known, synthetic ROW-MAJOR QUAD grid into disjoint groups. This is
 * an identity/provenance exercise; no patch ownership or surface quality is inferred.
 */
export function syntheticGridFacePartition(mesh: MeshGeometry, stride = 8): SourceFacePartition {
  const count = meshFaceCount(mesh);
  const width = Math.floor(Math.sqrt(count));
  const height = Math.ceil(count / width);
  if (mesh.coordinate_space !== 'xyz' || !mesh.packed ||
      mesh.source_sha256 !== '0'.repeat(64) ||
      mesh.source_patch_ownership !== 'NOT_APMESH_SOURCE' ||
      ![1_000, 50_000, 500_000].includes(count) ||
      !Number.isSafeInteger(stride) || stride < 2 || stride > 64 ||
      mesh.triangles !== 0 || mesh.quads !== count ||
      mesh.packed.faceIds.length !== count ||
      mesh.packed.arities.length !== count ||
      mesh.packed.offsets.length !== count + 1) {
    throw new Error('unqualified_synthetic_grid_partition');
  }
  const ids = meshFaceIds(mesh);
  for (let i = 0; i < count; i += 1) {
    if (ids[i] !== i || mesh.packed.arities[i] !== 4 ||
        mesh.packed.offsets[i] !== i * 5 || mesh.packed.polys[i * 5] !== 4) {
      throw new Error('synthetic_grid_order_mismatch');
    }
  }
  if (mesh.packed.offsets[count] !== count * 5 ||
      mesh.packed.vertices.length !== (width + 1) * (height + 1) * 3) {
    throw new Error('synthetic_grid_geometry_mismatch');
  }
  const groupsX = Math.ceil(width / stride);
  const groupsY = Math.ceil(height / stride);
  const offsets: number[] = [0];
  const originalFaceIds = new Uint32Array(count);
  let cursor = 0;
  for (let gy = 0; gy < groupsY; gy += 1) {
    for (let gx = 0; gx < groupsX; gx += 1) {
      const start = cursor;
      for (let y = gy * stride; y < Math.min((gy + 1) * stride, height); y += 1) {
        for (let x = gx * stride; x < Math.min((gx + 1) * stride, width); x += 1) {
          const faceIndex = y * width + x;
          if (faceIndex >= count) continue;
          originalFaceIds[cursor++] = ids[faceIndex];
        }
      }
      if (cursor > start) offsets.push(cursor);
    }
  }
  if (cursor !== count) throw new Error('missing_original_faces');
  const groupedOffsets = Uint32Array.from(offsets);
  verifyFacePartition(Uint32Array.from(ids), groupedOffsets, originalFaceIds);
  return {
    schema: LINEAGE_SCHEMA, source_sha256: mesh.source_sha256,
    source_face_count: count, aggregate_count: groupedOffsets.length - 1,
    offsets: groupedOffsets, original_face_ids: originalFaceIds,
    covers_every_original_face_exactly_once: true,
    aggregate_geometry_defined: false, is_geometric_lod: false,
    metric_comparable: false, classification: 'SYNTHETIC_STRUCTURED_GRID_ONLY',
  };
}
