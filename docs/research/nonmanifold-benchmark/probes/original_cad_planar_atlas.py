#!/usr/bin/env python3
"""Extract a bounded, source-identity-preserving planar quad BP atlas.

Research-only partial model extraction. Non-planar and trimmed faces are not fit,
sewn or marked as converted. An original model must have a pinned SHA-256.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt

SLOTS = ((0, 1, 2, 3), (3, 7, 11, 15), (12, 13, 14, 15), (0, 4, 8, 12))
SOURCES = {
    'M5': ('i05o_m5.step', '895f67c0669096b287077ac1bb56dad0e117cd96f78334d3129d783fd78b96cb'),
    'S40': ('i25o_s40.step', 'b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b'),
    'S27': ('i22o_s27.step', 'b4a60c43cabd3c72bf61d54a23f36e6e539ad985015d2a7c377885b5d170f8c5'),
    'M3': ('i03o_m3.step', 'c42862fa6bc1e94a9bb70e43a7dc9901aa5281d7b58de6ee4699494088286008'),
}


def same_index(shapes, candidate):
    """Use native TopoDS identity, never coordinate proximity."""
    return next((i for i, item in enumerate(shapes) if item.wrapped.IsSame(candidate.wrapped)), None)


def vector(point):
    return (point.x, point.y, point.z)


def lerp(a, b, t):
    return tuple((1 - t) * x + t * y for x, y in zip(a, b))


def bilinear(corners, u, v):
    """Degree-elevated bilinear polynomial; net is exact for planar quads."""
    return lerp(lerp(corners[0], corners[1], u),
                lerp(corners[3], corners[2], u), v)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def norm(v):
    return math.sqrt(dot(v, v))


def area_triangle(a, b, c):
    return 0.5 * norm(cross(sub(b, a), sub(c, a)))


def eligibility(face, length_scale):
    """Return ordered four native vertices and edges, or a named rejection."""
    if face.geomType() != 'PLANE':
        return None, 'NONPLANAR_SUPPORT'
    if len(face.Wires()) != 1:
        return None, 'TRIMMED_MULTIWIRE'
    wire = face.outerWire()
    edges, vertices = wire.Edges(), wire.Vertices()
    if len(edges) != 4 or len(vertices) != 4 or any(e.geomType() != 'LINE' for e in edges):
        return None, 'NOT_FOUR_STRAIGHT_SIDES'
    corners = [vector(v.Center()) for v in vertices]
    tol = max(1e-10, length_scale * 1e-11)
    if len({tuple(round(c/tol) for c in p) for p in corners}) != 4:
        return None, 'DEGENERATE_CORNERS'
    # Reject concave, self-intersecting and zero-Jacobian parameterizations.
    turns = []
    base_normal = cross(sub(corners[1], corners[0]), sub(corners[3], corners[0]))
    if norm(base_normal) <= tol * tol:
        return None, 'DEGENERATE_AREA'
    for i in range(4):
        a,b,c = corners[i],corners[(i+1)%4],corners[(i+2)%4]
        turns.append(dot(cross(sub(b,a),sub(c,b)),base_normal))
    if min(turns) <= tol * tol * max(norm(base_normal), tol):
        return None, 'NONCONVEX_OR_DEGENERATE'
    expected_area = area_triangle(corners[0], corners[1], corners[2]) + area_triangle(corners[0], corners[2], corners[3])
    if abs(expected_area-face.Area()) > max(1e-9, expected_area*1e-9):
        return None, 'TRIMMED_OR_AREA_MISMATCH'
    # Bind each ordered side to one actual source edge by native endpoint IDs.
    sides=[]
    for i in range(4):
        start, end = vertices[i], vertices[(i+1)%4]
        matching=[e for e in edges if len(e.Vertices())==2 and
                  any(v.wrapped.IsSame(start.wrapped) for v in e.Vertices()) and
                  any(v.wrapped.IsSame(end.wrapped) for v in e.Vertices())]
        if len(matching)!=1:
            return None, 'AMBIGUOUS_NATIVE_SIDE'
        sides.append(matching[0])
    return (vertices, corners, sides), None


def native_distance(face, point):
    vertex = BRepBuilderAPI_MakeVertex(gp_Pnt(*point)).Vertex()
    calc = BRepExtrema_DistShapeShape(vertex, face.wrapped)
    calc.Perform()
    if not calc.IsDone():
        raise RuntimeError('Native source face distance failed')
    return calc.Value()


def build_atlas(shape, model_id, source_sha256, *, sample_grid=(0, .25, .5, .75, 1)):
    """Build partial face atlas; every BP shared edge follows exact TopoDS IDs."""
    if not shape.isValid():
        raise ValueError('Invalid native BRep')
    length_scale = shape.BoundingBox().DiagonalLength
    if not math.isfinite(length_scale) or length_scale <= 0:
        raise ValueError('Invalid model size')
    source_vertices = shape.Vertices()
    source_edges = shape.Edges()
    controls, control_keys = [], {}
    patches, rejected = [], []
    native_max_distance = 0.0
    all_faces = shape.Faces()
    for face_id, face in enumerate(all_faces):
        eligible, reason = eligibility(face, length_scale)
        if reason:
            rejected.append({'source_face':face_id,'reason':reason,'support':face.geomType()})
            continue
        native_vertices, corners, native_sides=eligible
        vids = [same_index(source_vertices,v) for v in native_vertices]
        eids = [same_index(source_edges,e) for e in native_sides]
        if None in vids or None in eids:
            raise ValueError('Source identity missing from imported shape graph')
        # Side traversal is c0->c1, c1->c2, c2->c3, c3->c0.
        local_sides = ((0,1),(1,2),(2,3),(3,0))
        local_edge_keys={}
        for sid, (a,b) in enumerate(local_sides):
            e=eids[sid]
            for step in (1,2):
                canonical_step = step if vids[a] < vids[b] else 3-step
                local_edge_keys[(sid,step)] = ('edge',e,canonical_step)
        keys={
            (0,0):('vertex',vids[0]),(0,3):('vertex',vids[1]),
            (3,3):('vertex',vids[2]),(3,0):('vertex',vids[3]),
        }
        # Map the edge internal controls into the BP row-major 4x4 net.
        for step in (1,2):
            keys[(0,step)] = local_edge_keys[(0,step)]
            keys[(step,3)] = local_edge_keys[(1,step)]
            keys[(3,3-step)] = local_edge_keys[(2,step)]
            keys[(3-step,0)] = local_edge_keys[(3,step)]
        matrix=[]
        for row in range(4):
            for col in range(4):
                key=keys.get((row,col),('interior',face_id,row,col))
                xyz=bilinear(corners,col/3,row/3)
                if key in control_keys:
                    idx=control_keys[key]
                    if norm(sub(controls[idx],xyz)) > max(1e-9,length_scale*1e-9):
                        raise ValueError('Incompatible source controls on same TopoDS identity')
                else:
                    idx=len(controls)
                    controls.append(xyz)
                    control_keys[key]=idx
                matrix.append(idx)
        sides=[]
        # Slot 2 and 3 are reversed relative to the native wire walk.
        slot_edges=(eids[0],eids[1],eids[2],eids[3])
        for slot, offsets in enumerate(SLOTS):
            ids=[matrix[k] for k in offsets]
            sides.append({'slot':slot,'source_edge':slot_edges[slot],
                          'control_vertex_ids':ids})
        max_distance=0.0
        for u in sample_grid:
            for v in sample_grid:
                max_distance=max(max_distance,native_distance(face,bilinear(corners,u,v)))
        native_max_distance=max(native_max_distance,max_distance)
        patches.append({'source_face':face_id,'source_vertex_ids':vids,
                        'source_edge_ids':eids,'control_vertex_ids':matrix,
                        'sides':sides,'sampled_source_distance_mm':max_distance})
    lines=['// Partial exact planar quad atlas from pinned original CAD',
           '// NOT a full model, non-manifold positive, or accepted APMesh mesh']
    lines.extend('v '+' '.join(format(value,'.17g') for value in xyz) for xyz in controls)
    lines.extend('p '+' '.join(str(i) for i in p['control_vertex_ids']) for p in patches)
    bp='\n'.join(lines)+'\n'
    edge_uses=Counter(side['source_edge'] for p in patches for side in p['sides'])
    report={
        'schema':'apmesh-original-cad-partial-planar-atlas-v1',
        'scientific_scope':'PARTIAL_EXACT_PLANAR_SUBFACES_ONLY',
        'source_model':model_id,'source_sha256':source_sha256,'source_units':'mm',
        'source_face_count':len(all_faces),'converted_face_count':len(patches),
        'excluded_face_count':len(rejected),'exclusions':rejected,
        'source_edge_incidence_within_atlas':dict(sorted(Counter(edge_uses.values()).items())),
        'maximum_source_edge_incidence_in_atlas':max(edge_uses.values(),default=0),
        'unique_controls':len(controls),'native_max_sample_distance_mm':native_max_distance,
        'source_fit_status':'EXACT_PLANAR_BILINEAR_DEGREE_ELEVATION',
        'continuous_error_certificate':'ALGEBRAIC_PLANAR_QUAD_WITH_NATIVE_AREA_CHECK',
        'sample_grid':list(sample_grid),'patches':patches,
        'bp_sha256':sha256(bp.encode()).hexdigest(),
        'full_original_model_converted':len(rejected)==0,
        'independent_external_nonmanifold_admission':'NOT_GRANTED',
        'apmesh_generation':'NOT_RUN',
    }
    if len(patches)==0:
        report['source_fit_status']='NO_ADMITTED_FACES'
    return bp,report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',required=True,choices=sorted(SOURCES))
    parser.add_argument('--sources',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    filename,expected=SOURCES[args.model]
    path=args.sources/filename
    raw=path.read_bytes()
    digest=sha256(raw).hexdigest()
    if digest!=expected:
        raise ValueError('Original source SHA-256 does not match pinned model')
    shape=cq.importers.importStep(str(path)).val()
    bp,report=build_atlas(shape,args.model,digest)
    args.output.mkdir(parents=True,exist_ok=True)
    base=args.output/args.model.lower()
    (base.with_suffix('.partial.bp')).write_text(bp,encoding='utf8')
    (args.output/f'{args.model.lower()}.partial.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:report[k] for k in ('source_model','converted_face_count','excluded_face_count','unique_controls','native_max_sample_distance_mm','full_original_model_converted')},sort_keys=True))


if __name__=='__main__':
    main()
