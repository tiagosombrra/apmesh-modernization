/** R2.7.21 original sampled source seam = existing accepted TRI edges only. */
import type { NativeAcceptedScene, NativeFace } from './nativeAcceptedSceneContract';
import type { NativeSharedSourceCurve } from './nativeIdentityContract';

export type V3 = [number, number, number];
export type V2 = [number, number];

export interface NativeSeamSegment {
  patchSlot: number;
  startOrdinal: number;
  startNodeId: number;
  endNodeId: number;
  xyzStart: V3;
  xyzEnd: V3;
  uvStart: V2;
  uvEnd: V2;
}
export interface NativeSeamSample {
  patchSlot: number;
  ordinal: number;
  nativeNodeId: number;
  xyz: V3;
  uv: V2;
}
export interface NativeSeamTrace {
  sourceCurveSlot: number;
  patchSlots: number[];
  samples: NativeSeamSample[];
  segments: NativeSeamSegment[];
  verifiedOriginalNativeTriangleEdgeCount: number;
  noGlobalWeldingInferred: true;
}

function assertNative(ok: boolean, message: string): asserts ok {
  if (!ok) throw new Error(message);
}

function close(a: readonly number[], b: readonly number[], tol = 1e-9): boolean {
  return a.length === b.length && a.every((value,i) =>
    Number.isFinite(value) && Number.isFinite(b[i]) && Math.abs(value-b[i]) <= tol);
}

interface Vertex {
  xyz: V3;
  uv: V2;
}

/** Independent original node and edge index; never weld coincident XYZ. */
export function buildNativeSeamTrace(
  scene: NativeAcceptedScene, curve: NativeSharedSourceCurve,
): NativeSeamTrace {
  const nodes = new Map<string,Vertex>();
  const edges = new Set<string>();
  const edgeKey = (patch: number, a: number, b: number) =>
    patch + ':' + Math.min(a,b) + ':' + Math.max(a,b);
  for (const face of scene.native_faces) {
    const patch = face[0];
    for (let k=0;k<3;k++) {
      const node = face[4][k];
      const key = patch + ':' + node[0];
      const xyz: V3 = [node[1],node[2],node[3]];
      const uv: V2 = [node[4],node[5]];
      const old = nodes.get(key);
      assertNative(!old || (close(old.xyz,xyz) && close(old.uv,uv)),
        'r2721_original_patch_local_native_node_coordinates_conflict');
      nodes.set(key,{xyz,uv});
      const next = face[4][(k+1)%3];
      assertNative(node[0] !== next[0],
        'r2721_degenerate_accepted_native_triangle_edge');
      edges.add(edgeKey(patch,node[0],next[0]));
    }
  }
  const members = curve.sample_groups.map(group =>
    new Map(group.members.map(member => [member.patch_slot,member])));
  const segments: NativeSeamSegment[] = [];
  const samples: NativeSeamSample[] = [];
  for (const patch of curve.patch_slots) {
    for (let ordinal=0;ordinal<members.length;ordinal++) {
      const source = members[ordinal].get(patch);
      assertNative(source !== undefined,
        'r2721_missing_original_shared_source_patch_sample');
      const owned = nodes.get(patch+':'+source.native_node_id);
      assertNative(owned !== undefined &&
        close(owned.xyz,source.original_xyz),
      'r2721_sample_is_not_original_accepted_native_node');
      samples.push({
        patchSlot:patch,ordinal,nativeNodeId:source.native_node_id,
        xyz:[...owned.xyz],uv:[...owned.uv],
      });
      if(ordinal===0) continue;
      const prev = members[ordinal-1].get(patch);
      assertNative(prev !== undefined && prev.native_node_id !== source.native_node_id &&
        edges.has(edgeKey(patch,prev.native_node_id,source.native_node_id)),
      'r2721_source_sample_segment_not_native_accepted_tri_edge');
      const before = nodes.get(patch+':'+prev.native_node_id);
      assertNative(before !== undefined,'r2721_missing_original_edge_start');
      segments.push({
        patchSlot:patch,startOrdinal:ordinal-1,
        startNodeId:prev.native_node_id,endNodeId:source.native_node_id,
        xyzStart:[...before.xyz],xyzEnd:[...owned.xyz],
        uvStart:[...before.uv],uvEnd:[...owned.uv],
      });
    }
  }
  assertNative(segments.length === curve.patch_slots.length *
    (curve.sample_groups.length-1),
  'r2721_incomplete_original_native_seam_edge_incidences');
  return {
    sourceCurveSlot:curve.source_curve_slot,
    patchSlots:[...curve.patch_slots],
    samples,segments,
    verifiedOriginalNativeTriangleEdgeCount:segments.length,
    noGlobalWeldingInferred:true,
  };
}

/** A clicked face only links to samples belonging to the same native patch. */
export function sourceSampleOrdinalsOnFace(
  face: NativeFace, curve: NativeSharedSourceCurve,
): number[] {
  const ordinals: number[] = [];
  curve.sample_groups.forEach((group,ordinal) => {
    const member = group.members.find(m => m.patch_slot === face[0]);
    if(member && face[4].some(node =>
      node[0] === member.native_node_id &&
      close(node.slice(1,4),member.original_xyz))) ordinals.push(ordinal);
  });
  return ordinals;
}

export function firstActualNativeFaceForSample(
  scene: NativeAcceptedScene, curve: NativeSharedSourceCurve,
  patchSlot: number, ordinal: number,
): number | null {
  const member = curve.sample_groups[ordinal]?.members.find(m =>
    m.patch_slot === patchSlot);
  if(!member) return null;
  const index=scene.native_faces.findIndex(face =>
    face[0] === patchSlot && face[4].some(node =>
      node[0] === member.native_node_id &&
      close(node.slice(1,4),member.original_xyz)));
  return index >= 0 ? index : null;
}
