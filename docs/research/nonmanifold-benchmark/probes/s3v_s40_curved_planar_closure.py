#!/usr/bin/env python3
"""S3.V: bounded source-native planar closing patches on original S40.

The source curves, topology, and previously indexed cubic boundary controls are
immutable inputs. No proximity-welding or independent replacement cubic fitting.
This is isolated feasibility code, not an APMesh TRI/QUAD generator.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math

import cadquery as cq
from shapely.geometry import Polygon
from scipy.optimize import minimize_scalar
from OCP.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.ElSLib import ElSLib
from OCP.TopAbs import TopAbs_IN, TopAbs_ON
from OCP.gp import gp_Pnt, gp_Pnt2d

from audit_analytic_bp import read_bp, surface
from s3c_step_source_gate import SOURCES, coordinates, oriented_edges, parse_entities
from s3i_joint_source_atlas import _serialize
from s3r_s40_conforming_hole_join import _edge_adjacency, _side
from s3s_full_original_face_census import full_correspondence
from s3t_s40_planar_octagons import _coons_interior, _distance, _lerp

SOURCE_SHA = SOURCES['S40'][1]
BASELINE_SHA = '988d8ed29867927f736838dde20db9efb358c0ee04a202a4f4810ae0e23aa40d'
TARGETS = (17, 2092)
EXPECTED_NATIVE = {17: 0, 2092: 18}
BUDGET_MM = 0.001
BOUNDARY_ENDPOINT_MM = 1e-4
PLANAR_SUPPORT_MM = 1e-7
# These source-adjacent patch IDs were certified against the frozen S3.T BP and
# validated original STEP EDGE_CURVE adjacency. The corresponding controls are
# inherited verbatim, never recreated or welded by spatial proximity.
SOURCE_SIDE_PATCH_IDS = {
    17: {21: tuple(range(96, 105)), 57: (6,), 85: tuple(range(64, 77, 2)), 193: (3,)},
    2092: {2096: tuple(range(88, 96)), 2201: (7,), 2042: tuple(range(47, 55)), 2223: (8,)},
}
SOURCE_NEIGHBOR_FACES = {
    17: {21: 218, 57: 1800, 85: 1519, 193: 1773},
    2092: {2096: 2457, 2201: 2403, 2042: 1986, 2223: 2430},
}
EXPECTED_SUBDIVISIONS = {17: (9, 1, 7, 1), 2092: (8, 1, 8, 1)}


def verify_source_and_atlas(source: bytes, previous_bp: bytes, previous_manifest: dict, budget_mm=BUDGET_MM):
    """Enforce source byte identity and the entire admitted S3.T BP lineage."""
    if budget_mm != BUDGET_MM:
        raise ValueError('Experimental tolerance modification is forbidden')
    if sha256(source).hexdigest() != SOURCE_SHA:
        raise ValueError('Original S40 source SHA mismatch')
    if sha256(previous_bp).hexdigest() != BASELINE_SHA:
        raise ValueError('Frozen S3.T BP SHA mismatch')
    if (previous_manifest.get('new_bp_sha256') != BASELINE_SHA or
        previous_manifest.get('joined_patches') != 132 or
        previous_manifest.get('joined_control_count') != 1527 or
        previous_manifest.get('source_original_faces_represented') != 19 or
        previous_manifest.get('global_open_indexed_sides') != 150 or
        previous_manifest.get('source_inner_hole_retained') is not True):
        raise ValueError('Original S3.T manifest changed')
    points, patches = read_bp(previous_bp.decode('utf-8'))
    if len(points) != 1527 or len(patches) != 132:
        raise ValueError('Frozen S3.T BP cardinality changed')
    return parse_entities(source.decode('utf-8')), points, patches


def source_boundary_sides(face_id, table, points, patches, adjacency):
    """Recover every oriented source-edge segment from pinned indexed BP sides.

    The prescribed patch lineage comes from source-face ownership in the
    previously audited S3.R/S3.T atlas. A geometric proximity check merely
    validates those original identities after selection; it never allocates IDs.
    """
    kind, wires = oriented_edges(table, face_id)
    if kind != 'PLANE' or len(wires) != 1 or len(wires[0]) != 4:
        raise ValueError('Target is not a four-edged original planar face')
    wire = wires[0]
    ids = [e['edge_curve_id'] for e in wire]
    if set(ids) != set(SOURCE_SIDE_PATCH_IDS[face_id]):
        raise ValueError('Original source boundary EDGE_CURVE identities changed')
    if [e['end_vertex_id'] for e in wire] != [wire[(i+1)%4]['start_vertex_id'] for i,e in enumerate(wire)]:
        raise ValueError('Original source wire orientation is broken')
    all_segments = []
    for e in wire:
        eid = e['edge_curve_id']
        available = []
        for patch_id in SOURCE_SIDE_PATCH_IDS[face_id][eid]:
            candidates = [(side, _side(patches[patch_id], side)) for side in ('bottom', 'top', 'left', 'right')]
            open_candidates = [idx for _,idx in candidates if len(adjacency[tuple(sorted(idx))]) == 1]
            if e['master_3d_curve'] == 'LINE':
                start = coordinates(table,e['start_vertex_id']); end = coordinates(table,e['end_vertex_id'])
                open_candidates = [idx for idx in open_candidates if
                                   min(_distance(points[idx[0]],start)+_distance(points[idx[-1]],end),
                                       _distance(points[idx[-1]],start)+_distance(points[idx[0]],end)) < 2*BOUNDARY_ENDPOINT_MM]
            else:
                # A curved side of the specified previously certified patch is
                # its unsplit V-min boundary. Confirm its source curve separately
                # through native BRep curves before admission.
                open_candidates = [idx for idx in open_candidates if idx == _side(patches[patch_id],'bottom')]
            if len(open_candidates) != 1:
                raise ValueError(f'Source curve #{eid} has ambiguous inherited side on patch #{patch_id}')
            available.append(open_candidates[0])
        if len(available) != len(set(tuple(z) for z in available)):
            raise ValueError('Duplicate source boundary side')
        start_point = coordinates(table, e['start_vertex_id'])
        end_point = coordinates(table, e['end_vertex_id'])
        starts = [i for i,z in enumerate(available) if min(_distance(points[z[0]],start_point),
                       _distance(points[z[-1]],start_point)) < BOUNDARY_ENDPOINT_MM]
        if len(starts) != 1:
            raise ValueError(f'Source curve #{eid} has {len(starts)} start anchors')
        first = available.pop(starts[0]); first = first if _distance(points[first[0]],start_point) < BOUNDARY_ENDPOINT_MM else first[::-1]
        chain=[first]
        while available:
            found = [(i,z) for i,z in enumerate(available) if chain[-1][-1] in (z[0],z[-1])]
            if len(found)!=1:
                raise ValueError(f'Original source #{eid} has disconnected or ambiguous indexed segments')
            i,z=found[0];available.pop(i)
            chain.append(z if z[0] == chain[-1][-1] else z[::-1])
        if _distance(points[chain[-1][-1]],end_point) >= BOUNDARY_ENDPOINT_MM:
            raise ValueError(f'Original source edge #{eid} has wrong final endpoint')
        all_segments.extend([(eid,ids) for ids in chain])
    if len(all_segments)!=18 or any(a[1][-1]!=b[1][0] for a,b in zip(all_segments,all_segments[1:]+all_segments[:1])):
        raise ValueError('The original 18-segment indexed boundary is not closed')
    actual=tuple(sum(1 for eid,_ in all_segments if eid==e['edge_curve_id']) for e in wire)
    if actual != EXPECTED_SUBDIVISIONS[face_id]:
        raise ValueError('Source-indexed edge subdivision profile changed')
    return all_segments


def _convex(coordinates):
    cr=[]
    for i in range(4):
        a,b,c = coordinates[i], coordinates[(i+1)%4], coordinates[(i+2)%4]
        cr.append((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))
    return min(cr)>1e-9 or max(cr)<-1e-9


def quadrangulate_source_boundary(points, segments, native_face):
    """Find eight convex quads using only existing original boundary vertices."""
    plane = BRepAdaptor_Surface(native_face.wrapped).Plane()
    vertices = tuple(ids[0] for _,ids in segments)
    uv = tuple(ElSLib.Parameters_s(plane,gp_Pnt(*points[i])) for i in vertices)
    original = Polygon(uv)
    if not original.is_valid or original.area < 1e-6:
        raise ValueError('Original indexed trim-boundary polygon is invalid')
    n=len(vertices)

    @lru_cache(None)
    def solve(i,j):
        if j==i+1:return (0.0,())
        if (j-i)%2==0:return None
        best=None
        for a in range(i+1,j-1,2):
            for b in range(a+1,j,2):
                q_ids=(i,a,b,j)
                xy=[uv[z] for z in q_ids]
                polygon=Polygon(xy)
                if (not polygon.is_valid or not _convex(xy) or polygon.area<1e-8 or
                    not original.buffer(1e-6).covers(polygon)):
                    continue
                children=(solve(i,a),solve(a,b),solve(b,j))
                if any(c is None for c in children):continue
                lengths=[math.dist(xy[z],xy[(z+1)%4]) for z in range(4)]
                weight = (max(lengths)/max(min(lengths),1e-8))**2 + \
                    .01*polygon.area/max(min(lengths)**2,1e-10) + sum(child[0] for child in children)
                quads=tuple(q for child in children for q in child[1])+(q_ids,)
                if best is None or weight<best[0]:best=(weight,quads)
        return best
    solution=solve(0,n-1)
    if solution is None or len(solution[1]) != 8:
        raise ValueError('Original source polygon has no admissible eight-quad partition')
    cells=tuple(tuple(vertices[i] for i in q) for q in solution[1])
    area = sum(Polygon([uv[i] for i in q]).area for q in solution[1])
    if abs(area-original.area)>1e-6:
        raise ValueError('Uncovered or overlapping parameter-space quadrilateral area')
    return cells, {'source_uv_polygon_area': original.area,'source_quad_uv_area':area,
                   'source_uv_polygon_vertices':len(vertices),
                   'source_octagonal_partition_count':len(cells),
                   'source_quad_original_control_ids':[list(row) for row in cells]}


def _normal(a,b,c):
    u=tuple(b[i]-a[i] for i in range(3)); v=tuple(c[i]-a[i] for i in range(3))
    return (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])


def build_extension(source: bytes, baseline: bytes, baseline_manifest: dict, native, *, budget_mm=BUDGET_MM):
    """Append index-conforming Coons patches; reject every mismatched prior side."""
    table,old_points,old_patches=verify_source_and_atlas(source,baseline,baseline_manifest,budget_mm)
    correspondence=full_correspondence(source.decode('utf-8'),native)
    adjacency=_edge_adjacency(old_patches)
    points=list(old_points)
    patches=list(old_patches)
    faces={}
    for face_id in TARGETS:
        if correspondence['face_map'].get(face_id) != EXPECTED_NATIVE[face_id]:
            raise ValueError('Source/native face identity changed')
        face=native.Faces()[EXPECTED_NATIVE[face_id]]
        if face.geomType() != 'PLANE' or len(face.Wires()) != 1:
            raise ValueError('Original native target is not a single outer planar wire')
        wire=oriented_edges(table,face_id)[1][0]
        for eid,owner in SOURCE_NEIGHBOR_FACES[face_id].items():
            if correspondence['owners'][eid] != {face_id,owner}:
                raise ValueError('Original source EDGE_CURVE owner identity changed')
        segments=source_boundary_sides(face_id,table,old_points,old_patches,adjacency)
        cells,details=quadrangulate_source_boundary(old_points,segments,face)
        by_pair={frozenset((ids[0],ids[-1])):tuple(ids) for _,ids in segments}
        diagonal_keys={}
        face_start=len(patches)
        normal=face.normalAt().toTuple()
        for local,corners in enumerate(cells):
            a,b,c,d=(points[i] for i in corners)
            cross=_normal(a,b,d)
            if sum(cross[i]*normal[i] for i in range(3)) < 0:
                corners=(corners[0],corners[3],corners[2],corners[1])
            if abs(sum(_normal(points[corners[0]],points[corners[1]],points[corners[3]])[i]*normal[i]
                       for i in range(3))) < 1e-9:
                raise ValueError('Source quadrilateral has incorrect or degenerate outward orientation')
            side_ids=[]
            for i in range(4):
                va,vb=corners[i],corners[(i+1)%4]
                key=frozenset((va,vb))
                if key in by_pair:
                    ids=by_pair[key]
                    if ids[0]!=va:ids=ids[::-1]
                else:
                    if key not in diagonal_keys:
                        p=points[va];q=points[vb]
                        canonical=(va,vb) if va<vb else (vb,va)
                        a1,b1=(points[z] for z in canonical)
                        diagonal_keys[key]=(canonical[0],len(points),len(points)+1,canonical[1])
                        points.extend((_lerp(a1,b1,1/3),_lerp(a1,b1,2/3)))
                    ids=diagonal_keys[key]
                    if ids[0]!=va:ids=ids[::-1]
                side_ids.append(ids)
            net=_coons_interior(tuple(tuple(points[z] for z in ids) for ids in side_ids))
            grid=[[None]*4 for _ in range(4)]
            for col,k in enumerate(side_ids[0]):grid[0][col]=k
            for row,k in enumerate(side_ids[1]):grid[row][3]=k
            for col,k in enumerate(reversed(side_ids[2])):grid[3][col]=k
            for row,k in enumerate(reversed(side_ids[3])):grid[row][0]=k
            for row in (1,2):
                for col in (1,2):
                    grid[row][col]=len(points);points.append(net[row][col])
            patches.append(tuple(k for row in grid for k in row))
        faces[str(face_id)]={**details,
              'source_edge_curve_ids':[e['edge_curve_id'] for e in wire],
              'source_edge_segment_counts':{str(e['edge_curve_id']):sum(sid==e['edge_curve_id'] for sid,_ in segments)
                                            for e in wire},
              'new_patch_start_id':face_start,
              'new_patch_count':len(cells),
              'new_internal_diagonal_count':len(diagonal_keys)}
    joined=_edge_adjacency(patches)
    two=sum(len(x)==2 for x in joined.values())
    one=sum(len(x)==1 for x in joined.values())
    if (len(patches),len(points),two,one)!=(148,1619,239,114):
        raise ValueError(f'Unexpected source-indexed global seam counts: {(len(patches),len(points),two,one)}')
    for old,now in zip(old_patches,patches[:132]):
        if old!=now:raise ValueError('Previously admitted original patches were modified')
    body=_serialize(points,patches)
    receipt={'schema':'apmesh-s3v-original-s40-curved-planar-closure-v1',
             'source_sha256':sha256(source).hexdigest(),
             'baseline_bp_sha256':BASELINE_SHA,
             'new_bp_sha256':sha256(body.encode('utf-8')).hexdigest(),
             'old_patches':132,'new_patches':16,'combined_patches':len(patches),
             'old_global_controls':1527,'combined_global_controls':len(points),
             'represented_original_faces':21,'total_original_faces':43,
             'global_two_sided_indexed_seams':two,'global_open_indexed_sides':one,
             'original_hole_218_preserved':True,
             'source_patch_first_132_nets_unchanged':True,
             'native_samples_run':False,'budget_mm':BUDGET_MM,
             'faces':faces,
             'continuous_trim_Hausdorff_certified':False,
             'apmesh_cpp_tri_quad':'NOT_RUN',
             'production_cpp_regression':'NOT_RUN'}
    return body,receipt


def _source_edge_closest(curve, position, sample_count=513):
    """Independently approximate distance to an original native BRep curve.

    This numerical minimization is sampled evidence, not an interval certificate.
    """
    lo,hi=curve.FirstParameter(),curve.LastParameter()
    if not math.isfinite(lo+hi) or not hi>lo:
        raise ValueError('Original native edge has invalid parameter interval')
    intervals=sample_count-1
    values=[]
    for k in range(sample_count):
        p=curve.Value(lo+(hi-lo)*k/intervals)
        values.append(_distance(position,(p.X(),p.Y(),p.Z())))
    minimum=min(range(sample_count),key=lambda k:values[k])
    a=lo+(hi-lo)*max(0,minimum-2)/intervals
    b=lo+(hi-lo)*min(intervals,minimum+2)/intervals
    def dist_sq(t):
        p=curve.Value(float(t))
        return sum((position[i]-x)**2 for i,x in enumerate((p.X(),p.Y(),p.Z())))
    opt=minimize_scalar(dist_sq,bounds=(a,b),method='bounded',options={'xatol':1e-13})
    return min(values[minimum],math.sqrt(max(0.0,opt.fun)))


def audit_native(source,baseline,baseline_manifest,native,joined_bp: str,receipt:dict):
    """Fail-closed native audit: trace inherited curves outside strict trim.

    Candidate controls are not admitted when any original face boundary sample
    is classified OUT. Proximity within the pilot budget is reported separately
    and must never be substituted for strict trimmed-face membership.
    """
    expected,regenerated=build_extension(source,baseline,baseline_manifest,native)
    if expected!=joined_bp or regenerated!=receipt:
        raise ValueError('Original source/recomputed BP/manifest mismatch')
    correspondence=full_correspondence(source.decode('utf-8'),native)
    pts,patches=read_bp(joined_bp)
    table=parse_entities(source.decode())
    original_pts,original_patches=read_bp(baseline.decode('utf-8'))
    if pts[:len(original_pts)]!=original_pts or patches[:132]!=original_patches:
        raise ValueError('Original source atlas prefix was modified')
    result={'status':'NOT_ADMITTED','new_face_ids':list(TARGETS),'original_source_sha256':SOURCE_SHA,
            'candidate_bp_sha256':receipt['new_bp_sha256'],
            'native_interior_IN':0,'native_boundary_IN_or_ON':0,
            'native_boundary_OUT':0,'native_strict_boundary_OUT_by_original_edge':{},
            'native_strict_boundary_OUT_on_derived_diagonal':0,
            'native_original_edge_samples':0,
            'maximum_original_native_edge_distance_mm':0.0,
            'max_native_plane_support_distance_mm':0.0,
            'native_edge_types':{},'per_face':{},
            'strict_native_trim_membership_pass':False,
            'within_original_experimental_1e-3_mm_curve_budget':False,
            'continuous_trim_hausdorff_certified':False,
            'apmesh_tri_quad_generated':False}
    out_edge_counts=Counter()
    for face_id in TARGETS:
        face=native.Faces()[EXPECTED_NATIVE[face_id]]
        plane=BRepAdaptor_Surface(face.wrapped).Plane()
        normal=face.normalAt().toTuple()
        segments=source_boundary_sides(face_id,table,original_pts,original_patches,
                                       _edge_adjacency(original_patches))
        original_side_to_edge={tuple(sorted(side)):eid for eid,side in segments}
        stat={'original_source_edge_count':len(set(eid for eid,_ in segments)),
              'source_boundary_piece_count':len(segments),
              'native_interior_IN':0,'native_boundary_IN_or_ON':0,
              'native_boundary_OUT':0,'native_original_curve_samples':0,
              'max_original_edge_distance_mm':0.0,
              'native_original_edge_max_distance_mm':{}}
        first=receipt['faces'][str(face_id)]['new_patch_start_id']
        for patch in patches[first:first+8]:
            net=[pts[k] for k in patch]
            c=_normal(net[0],net[3],net[12])
            if sum(c[i]*normal[i] for i in range(3)) <= 0:
                raise ValueError('Original native outward face orientation mismatch')
            for iu in range(1,10):
                for iv in range(1,10):
                    p=surface(net,iu/10,iv/10)
                    uv=ElSLib.Parameters_s(plane,gp_Pnt(*p))
                    state=BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State()
                    if state!=TopAbs_IN:
                        raise ValueError('New planar patch interior extends outside the native trim')
                    stat['native_interior_IN']+=1
                    result['max_native_plane_support_distance_mm']=max(
                        result['max_native_plane_support_distance_mm'],plane.Distance(gp_Pnt(*p)))
            for label in ('bottom','top','left','right'):
                side=_side(patch,label)
                source_eid=original_side_to_edge.get(tuple(sorted(side)))
                for k in range(11):
                    t=k/10
                    p=surface(net,*({'bottom':(t,0.),'top':(t,1.),'left':(0.,t),'right':(1.,t)}[label]))
                    uv=ElSLib.Parameters_s(plane,gp_Pnt(*p))
                    state=BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State()
                    if state in (TopAbs_IN,TopAbs_ON):
                        stat['native_boundary_IN_or_ON']+=1
                    else:
                        stat['native_boundary_OUT']+=1
                        if source_eid is None:
                            result['native_strict_boundary_OUT_on_derived_diagonal']+=1
                        else:
                            out_edge_counts[source_eid]+=1
                    result['max_native_plane_support_distance_mm']=max(
                        result['max_native_plane_support_distance_mm'],plane.Distance(gp_Pnt(*p)))
        # Source/native edge association is unique in the frozen full STEP graph.
        for eid in sorted({eid for eid,_ in segments}):
            native_edge=correspondence['native_edges'][correspondence['edge_map'][eid]]
            curve=BRepAdaptor_Curve(native_edge.wrapped)
            source_curve=next(e['master_3d_curve'] for e in oriented_edges(table,face_id)[1][0]
                              if e['edge_curve_id']==eid)
            result['native_edge_types'][str(eid)]=source_curve
            for part_id,side in segments:
                if part_id!=eid:continue
                net=[pts[k] for k in side]
                for k in range(11):
                    t=k/10
                    p=tuple(sum(w*net[j][axis] for j,w in enumerate(
                        ((1-t)**3,3*t*(1-t)**2,3*t*t*(1-t),t**3))) for axis in range(3))
                    dist=_source_edge_closest(curve,p)
                    stat['max_original_edge_distance_mm']=max(stat['max_original_edge_distance_mm'],dist)
                    stat['native_original_curve_samples']+=1
                    key=str(eid)
                    stat['native_original_edge_max_distance_mm'][key]=max(
                        stat['native_original_edge_max_distance_mm'].get(key,0.0),dist)
        result['native_interior_IN']+=stat['native_interior_IN']
        result['native_boundary_IN_or_ON']+=stat['native_boundary_IN_or_ON']
        result['native_boundary_OUT']+=stat['native_boundary_OUT']
        result['native_original_edge_samples']+=stat['native_original_curve_samples']
        result['maximum_original_native_edge_distance_mm']=max(
            result['maximum_original_native_edge_distance_mm'],stat['max_original_edge_distance_mm'])
        result['per_face'][str(face_id)]=stat
    result['native_strict_boundary_OUT_by_original_edge']={str(k):out_edge_counts[k] for k in sorted(out_edge_counts)}
    if result['max_native_plane_support_distance_mm']>PLANAR_SUPPORT_MM:
        raise ValueError('New source patches are not on their original support planes')
    if result['maximum_original_native_edge_distance_mm']>BUDGET_MM:
        raise ValueError('Inherited source-curve approximation exceeds original pilot budget')
    result['within_original_experimental_1e-3_mm_curve_budget']=True
    if result['native_strict_boundary_OUT_on_derived_diagonal']:
        raise ValueError('New internal derived diagonal exits native trimmed face')
    result['strict_native_trim_membership_pass']=(result['native_boundary_OUT']==0)
    result['status']='PASS' if result['strict_native_trim_membership_pass'] else 'BLOCKED_NATIVE_TRIM_BOUNDARY'
    return result


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--source-step',type=Path,required=True)
    cli.add_argument('--baseline-bp',type=Path,required=True)
    cli.add_argument('--baseline-manifest',type=Path,required=True)
    cli.add_argument('--output-dir',type=Path,required=True)
    opt=cli.parse_args()
    source=opt.source_step.read_bytes();baseline=opt.baseline_bp.read_bytes()
    baseline_manifest=json.loads(opt.baseline_manifest.read_text())
    native=cq.importers.importStep(str(opt.source_step)).val()
    bp,receipt=build_extension(source,baseline,baseline_manifest,native)
    audit=audit_native(source,baseline,baseline_manifest,native,bp,receipt)
    opt.output_dir.mkdir(parents=True,exist_ok=True)
    (opt.output_dir/'s40_curved_planar.CANDIDATE_NOT_ADMITTED.bp').write_text(bp)
    (opt.output_dir/'s40_curved_planar_candidate_manifest.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    (opt.output_dir/'s40_curved_planar_native_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'candidate_patches':receipt['combined_patches'],'native':audit},indent=2))


if __name__=='__main__':
    main()
