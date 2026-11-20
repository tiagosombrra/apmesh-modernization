#!/usr/bin/env python3
"""Source-indexed candidate quadrangulation for three original S40 planar regions.

This research script never treats inherited cubic curves as exact STEP trim curves.
The native face classifier independently decides each candidate's admission.
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
from scipy.spatial import cKDTree
from shapely.geometry import Polygon
from shapely.ops import unary_union
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.ElSLib import ElSLib
from OCP.TopAbs import TopAbs_IN, TopAbs_ON
from OCP.gp import gp_Pnt, gp_Pnt2d

from audit_analytic_bp import read_bp, surface
from s3c_step_source_gate import parse_entities, oriented_edges, coordinates
from s3i_joint_source_atlas import _serialize
from s3r_s40_conforming_hole_join import _edge_adjacency, _side
from s3s_full_original_face_census import full_correspondence
from s3t_s40_planar_octagons import _coons_interior, _distance, _lerp
from s3v_s40_curved_planar_closure import _source_edge_closest

SOURCE_SHA = 'b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b'
BASELINE_SHA = 'c826487d8cee76f6649100c59e5ce84fa6cb43c9004f53c68e3e565e86cdb174'
BUDGET_MM = 0.001
FACE_TO_NATIVE = {1827: 15, 1907: 16, 3044: 29}
# These patch/side identities are frozen from the previous source-indexed atlas.
# Native original EDGE_CURVE association is checked independently afterwards.
SOURCE_SIDE_LINEAGE = {
    1827: {1523: ((55, 'bottom'),), 1807: ((5, 'left'),),
           252: ((109, 'bottom'),), 1834: ((45, 'bottom'),),
           1858: ((7, 'right'),), 1886: ((87, 'bottom'),)},
    1907: {1911: ((78, 'bottom'),), 1934: ((8, 'left'),),
           1962: ((27, 'bottom'),), 326: ((114, 'bottom'),),
           1778: ((4, 'right'),), 1593: ((63, 'bottom'),)},
    3044: {3048: ((10, 'right'),),
           3071: tuple((i, 'top') for i in range(23, 27)),
           2886: tuple((i, 'top') for i in range(11, 15)),
           2833: ((9, 'right'),),
           2942: tuple((i, 'top') for i in range(15, 19)),
           2994: tuple((i, 'top') for i in range(19, 23))},
}
EXPECTED_SEGMENTS = {1827: 6, 1907: 6, 3044: 18}
EXPECTED_QUADS = {1827: 2, 1907: 2, 3044: 8}


def check_inputs(source: bytes, parent: bytes, manifest: dict, budget: float):
    """Reject different source/parent bytes and any altered experimental budget."""
    if budget != BUDGET_MM:
        raise ValueError('Original geometric budget may not be relaxed')
    if sha256(source).hexdigest() != SOURCE_SHA or sha256(parent).hexdigest() != BASELINE_SHA:
        raise ValueError('Frozen original STEP or parent BP hash mismatch')
    if (manifest.get('repaired_bp_sha256') != BASELINE_SHA or
        manifest.get('combined_patches') != 148 or
        manifest.get('global_declared_control_points') != 1619 or
        manifest.get('original_step_218_hole_patch_ids_unchanged') is not True):
        raise ValueError('Frozen repaired-parent manifest is inconsistent')
    pts, patches = read_bp(parent.decode())
    if (len(pts), len(patches)) != (1619, 148):
        raise ValueError('Frozen parent BP cardinality invalid')
    return pts, patches


def _cubic(pts, ids, t):
    w=((1-t)**3,3*t*(1-t)**2,3*t*t*(1-t),t**3)
    return tuple(sum(w[i]*pts[ids[i]][axis] for i in range(4)) for axis in range(3))


def recover_source_sides(source: bytes, native, pts, patches, face_id: int, *, max_distance=.001):
    """Check exact indexed lineage against each unique original native STEP edge."""
    table=parse_entities(source.decode())
    mapping=full_correspondence(source.decode(),native)
    if mapping['face_map'][face_id] != FACE_TO_NATIVE[face_id]:
        raise ValueError('Original/native target face identity changed')
    support,wires=oriented_edges(table,face_id)
    if support!='PLANE' or len(wires)!=1 or len(wires[0])!=6:
        raise ValueError('Original target is not a six-edge planar outer face')
    wire=wires[0]
    if set(e['edge_curve_id'] for e in wire)!=set(SOURCE_SIDE_LINEAGE[face_id]):
        raise ValueError('Original target EDGE_CURVE set changed')
    if any(e['end_vertex_id']!=wire[(i+1)%6]['start_vertex_id'] for i,e in enumerate(wire)):
        raise ValueError('STEP source wire does not close')
    adjacency=_edge_adjacency(patches)
    ordered=[]
    edge_checks={}
    for entry in wire:
        eid=entry['edge_curve_id']
        source_owners=mapping['owners'][eid]
        if face_id not in source_owners or len(source_owners)!=2:
            raise ValueError('Original source edge incidence unexpectedly changed')
        curve=BRepAdaptor_Curve(mapping['native_edges'][mapping['edge_map'][eid]].wrapped)
        lo,hi=curve.FirstParameter(),curve.LastParameter()
        if not math.isfinite(lo+hi) or hi<=lo:
            raise ValueError('Native original edge has an invalid parameter range')
        samples=[curve.Value(lo+(hi-lo)*i/2048).Coord() for i in range(2049)]
        oracle=cKDTree(samples)
        available=[]
        max_sample_distance=0.0
        for patch_id,side in SOURCE_SIDE_LINEAGE[face_id][eid]:
            ids=_side(patches[patch_id],side)
            if len(adjacency[tuple(sorted(ids))])!=1:
                raise ValueError('Original source neighbor is not an open indexed BP side')
            for t in (0.,.25,.5,.75,1.):
                deviation=float(oracle.query(_cubic(pts,ids,t))[0])
                max_sample_distance=max(max_sample_distance,deviation)
                if deviation>=max_distance:
                    raise ValueError(f'Original STEP edge #{eid} does not match the pinned source side')
            available.append(ids)
        a=coordinates(table,entry['start_vertex_id'])
        b=coordinates(table,entry['end_vertex_id'])
        first=[(i,ids) for i,ids in enumerate(available) if
               min(_distance(pts[ids[0]],a),_distance(pts[ids[-1]],a))<1e-5]
        if len(first)!=1:
            raise ValueError('No unique original STEP edge start control')
        first_index,first_ids=first[0]
        available.pop(first_index)
        chain=[first_ids if _distance(pts[first_ids[0]],a)<1e-5 else first_ids[::-1]]
        while available:
            next_edge=[(i,ids) for i,ids in enumerate(available)
                       if chain[-1][-1] in (ids[0],ids[-1])]
            if len(next_edge)!=1:
                raise ValueError('Original STEP edge indexed chain is not unique')
            i,ids=next_edge[0]
            available.pop(i)
            chain.append(ids if chain[-1][-1]==ids[0] else ids[::-1])
        if _distance(pts[chain[-1][-1]],b)>1e-5:
            raise ValueError('Original STEP edge endpoint not preserved')
        ordered.extend((eid,ids) for ids in chain)
        edge_checks[str(eid)]={'segments':len(chain),'source_native_edge_index':mapping['edge_map'][eid],
                'native_sample_screen_max_distance_mm':max_sample_distance,
                'original_incident_face_count':len(source_owners)}
    if len(ordered)!=EXPECTED_SEGMENTS[face_id] or any(
            x[1][-1]!=y[1][0] for x,y in zip(ordered,ordered[1:]+ordered[:1])):
        raise ValueError('Original indexed source boundary incomplete')
    return ordered,edge_checks


def _convex(xy, *, eps=1e-11):
    crosses=[]
    for i in range(4):
        a,b,c=xy[i],xy[(i+1)%4],xy[(i+2)%4]
        crosses.append((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))
    return min(crosses)>eps or max(crosses)<-eps


def quadrangulate(pts,segments,native_face,required_count):
    """Find convex quadrilateral partitions with exact inherited boundary vertices."""
    plane=BRepAdaptor_Surface(native_face.wrapped).Plane()
    vertices=tuple(ids[0] for _,ids in segments)
    uv=tuple(ElSLib.Parameters_s(plane,gp_Pnt(*pts[i])) for i in vertices)
    original=Polygon(uv)
    if not original.is_valid or original.area<1e-5:
        raise ValueError('Inherited boundary polygon invalid or degenerate')
    n=len(vertices)
    @lru_cache(None)
    def solve(i,j):
        if j==i+1:return (0.,())
        if (j-i)%2==0:return None
        best=None
        for a in range(i+1,j-1,2):
            for b in range(a+1,j,2):
                q=(i,a,b,j)
                xy=[uv[z] for z in q]
                poly=Polygon(xy)
                if not poly.is_valid or not _convex(xy) or poly.area<1e-8 or not original.buffer(1e-6).covers(poly):
                    continue
                children=(solve(i,a),solve(a,b),solve(b,j))
                if any(c is None for c in children):continue
                lengths=[math.dist(xy[k],xy[(k+1)%4]) for k in range(4)]
                score=(max(lengths)/max(min(lengths),1e-10))**2+sum(c[0] for c in children)
                quads=tuple(z for child in children for z in child[1])+(q,)
                if best is None or score<best[0]:best=(score,quads)
        return best
    result=solve(0,n-1)
    if result is None or len(result[1])!=required_count:
        raise ValueError('No conforming convex quadrangulation with inherited vertices')
    area=sum(Polygon([uv[i] for i in q]).area for q in result[1])
    if abs(area-original.area)>1e-6:
        raise ValueError('Indexed polygon partition has gaps or overlapping area')
    return tuple(tuple(vertices[i] for i in q) for q in result[1]),{
        'projected_original_piecewise_linear_uv_area':original.area,
        'projected_quad_piecewise_linear_uv_area':area,
        'boundary_piece_count':n,
        'quadrilateral_count':len(result[1])}


def build_candidate(source: bytes, native, parent: bytes, manifest: dict,
                    *, faces=(1827,1907,3044), budget_mm=BUDGET_MM):
    """Construct candidate using existing indexed boundary controls verbatim."""
    if not faces or len(faces)!=len(set(faces)) or any(f not in FACE_TO_NATIVE for f in faces):
        raise ValueError('Invalid, repeated or unsupported original STEP target')
    pts,patches=check_inputs(source,parent,manifest,budget_mm)
    oldpts=list(pts); oldpatches=list(patches)
    details={};points=list(pts);new_patches=[]
    for face in faces:
        if face not in FACE_TO_NATIVE or face in details:
            raise ValueError('Unknown or duplicate original STEP target')
        segments,edge_checks=recover_source_sides(source,native,oldpts,oldpatches,face)
        cells,part=quadrangulate(oldpts,segments,native.Faces()[FACE_TO_NATIVE[face]],EXPECTED_QUADS[face])
        sides={frozenset((ids[0],ids[-1])):ids for _,ids in segments}
        if len(sides)!=len(segments):
            raise ValueError('Ambiguous inherited indexed source boundary')
        inner={};start=len(patches)+len(new_patches)
        normal=native.Faces()[FACE_TO_NATIVE[face]].normalAt().toTuple()
        for local,corners in enumerate(cells):
            corners=list(corners)
            p0,p1,p3=(points[k] for k in (corners[0],corners[1],corners[3]))
            tangent1=tuple(p1[k]-p0[k] for k in range(3))
            tangent2=tuple(p3[k]-p0[k] for k in range(3))
            cross=(tangent1[1]*tangent2[2]-tangent1[2]*tangent2[1],
                   tangent1[2]*tangent2[0]-tangent1[0]*tangent2[2],
                   tangent1[0]*tangent2[1]-tangent1[1]*tangent2[0])
            dot=sum(x*y for x,y in zip(cross,normal))
            if abs(dot)<1e-10:
                raise ValueError('Degenerate outward candidate patch')
            if dot<0:corners=[corners[0],corners[3],corners[2],corners[1]]
            edge_ids=[]
            for j in range(4):
                a,b=corners[j],corners[(j+1)%4];key=frozenset((a,b))
                if key in sides:
                    ids=sides[key]
                    ids=ids if ids[0]==a else ids[::-1]
                else:
                    if key not in inner:
                        low,high=sorted((a,b))
                        inner[key]=(low,len(points),len(points)+1,high)
                        points.extend((_lerp(points[low],points[high],1/3),
                                       _lerp(points[low],points[high],2/3)))
                    ids=inner[key]
                    ids=ids if ids[0]==a else ids[::-1]
                edge_ids.append(ids)
            net=_coons_interior([[points[k] for k in side] for side in edge_ids])
            grid=[[None]*4 for _ in range(4)]
            for col,index in enumerate(edge_ids[0]):grid[0][col]=index
            for row,index in enumerate(edge_ids[1]):grid[row][3]=index
            for col,index in enumerate(reversed(edge_ids[2])):grid[3][col]=index
            for row,index in enumerate(reversed(edge_ids[3])):grid[row][0]=index
            for row in (1,2):
                for col in (1,2):
                    grid[row][col]=len(points)
                    points.append(net[row][col])
            new_patches.append(tuple(index for row in grid for index in row))
        details[str(face)]={**part,'source_edge_checks':edge_checks,'first_new_patch':start,
                            'new_patch_count':len(cells),'new_diagonal_count':len(inner),
                            'original_source_edge_ids':list(edge_checks)}
    patches.extend(new_patches)
    join=_edge_adjacency(patches)
    if any(len(x)>2 for x in join.values()):
        raise ValueError('Candidate adds overincident indexed side')
    if any(x!=y for x,y in zip(patches[:len(oldpatches)],oldpatches)) or points[:len(oldpts)]!=oldpts:
        raise ValueError('Candidate unexpectedly modifies frozen previous patch/control')
    for f in faces:
        if any(len(join[tuple(sorted(_side(oldpatches[pid],side)))])!=2
               for items in SOURCE_SIDE_LINEAGE[f].values() for pid,side in items):
            raise ValueError('Original source boundary did not become exactly two-sided')
    body=_serialize(points,patches)
    receipt={'schema':'apmesh-s3y-original-s40-source-curved-planar-candidate-v1',
             'source_sha256':sha256(source).hexdigest(),'baseline_bp_sha256':sha256(parent).hexdigest(),
             'candidate_bp_sha256':sha256(body.encode()).hexdigest(),
             'old_patches':len(oldpatches),'added_patches':len(new_patches),
             'candidate_patch_count':len(patches),'candidate_control_count':len(points),
             'candidate_two_sided_indexed_seams':sum(len(x)==2 for x in join.values()),
             'candidate_open_indexed_sides':sum(len(x)==1 for x in join.values()),
             'faces':details,'classification':'CANDIDATE_NOT_NATIVE_ADMITTED'}
    return body,receipt


def audit_native_patch_coverage(face, control_points, patch_ids, *, boundary_density=41):
    """Check positive oriented Jacobians and sampled physical patch coverage.

    The geometric area comparison is a numerical screen, never a continuous
    trimmed-domain equivalence theorem or directed-rounding certificate.
    """
    if boundary_density < 21 or boundary_density > 161:
        raise ValueError('Invalid curved-boundary sampling density')
    from numpy.polynomial.legendre import leggauss
    params, weights = leggauss(12)
    params=(params+1.)/2.
    weights=weights/2.
    plane=BRepAdaptor_Surface(face.wrapped).Plane()
    normal=np.asarray(face.normalAt().toTuple())
    polygons=[]; area=0.; min_jac=float('inf')
    def bezier(t):
        return np.asarray(((1-t)**3,3*t*(1-t)**2,3*t*t*(1-t),t**3))
    def deriv(t):
        return np.asarray((-3*(1-t)**2,3*(1-t)**2-6*t*(1-t),
                           6*t*(1-t)-3*t*t,3*t*t))
    for patch in patch_ids:
        grid=np.asarray([control_points[k] for k in patch]).reshape(4,4,3)
        for i,u in enumerate(params):
            for j,v in enumerate(params):
                du=np.einsum('i,j,ijc->c',bezier(v),deriv(u),grid)
                dv=np.einsum('i,j,ijc->c',deriv(v),bezier(u),grid)
                jac=float(np.dot(np.cross(du,dv),normal))
                min_jac=min(min_jac,jac)
                if jac<=0.:
                    raise ValueError('Candidate has non-positive outward oriented Jacobian')
                area+=float(weights[i]*weights[j]*jac)
        positions=[]
        for side in ('bottom','right','top','left'):
            for k in range(boundary_density-1):
                t=k/(boundary_density-1)
                x,y={'bottom':(t,0.),'right':(1.,t),
                     'top':(1.-t,1.),'left':(0.,1.-t)}[side]
                p=surface(list(grid.reshape(16,3)),x,y)
                positions.append(ElSLib.Parameters_s(plane,gp_Pnt(*p)))
        poly=Polygon(positions)
        if not poly.is_valid or poly.area<=0.:
            raise ValueError('Candidate planar patch has invalid sampled boundary')
        polygons.append(poly)
    merged=unary_union(polygons)
    total_area=sum(p.area for p in polygons)
    overlap=total_area-merged.area
    if merged.geom_type!='Polygon' or overlap>1e-5:
        raise ValueError('Candidate patches overlap or form disconnected domains')
    numerical_hole_area=sum(Polygon(ring).area for ring in merged.interiors)
    if not merged.is_valid or numerical_hole_area>1e-7:
        raise ValueError('Candidate planar patch union has a material unintended hole')
    native_area=face.Area()
    if abs(area-native_area)>1e-4*native_area:
        raise ValueError('Candidate area differs excessively from original native face')
    return {'native_area_mm2':native_area,'approximate_integrated_bp_area_mm2':area,
            'sampled_integrated_area_difference_mm2':area-native_area,
            'sampled_relative_area_difference':abs(area-native_area)/native_area,
            'min_sampled_oriented_jacobian':min_jac,
            'sampled_2d_patch_overlap_area':overlap,
            'sampled_2d_union_component_count':1,
            'sampled_numerical_hole_area_mm2':numerical_hole_area,
            'continuous_coverage_certified':False}


def audit_candidate(source: bytes, native, parent: bytes, manifest:dict,
                    candidate: str, report: dict, *, budget_mm=BUDGET_MM,
                    interior_grid=9, boundary_grid=11):
    """Require source-native original curve and strict trimmed face classification."""
    if interior_grid<3 or interior_grid>25 or boundary_grid<3 or boundary_grid>51:
        raise ValueError('Sampling grid outside declared validation protocol')
    regenerated,proof=build_candidate(source,native,parent,manifest,faces=tuple(int(f) for f in report["faces"]),budget_mm=budget_mm)
    if regenerated!=candidate or proof!=report:
        raise ValueError('Candidate geometry or source proof modified')
    table=parse_entities(source.decode())
    pts,patches=read_bp(candidate)
    summary={'status':'PASS','native_interior_IN':0,'native_boundary_IN_or_ON':0,
             'native_boundary_OUT':0,'native_boundary_out_by_face':{},
             'max_plane_distance_mm':0.,'max_boundary_native_curve_distance_mm':0.,
             'original_native_curve_samples':0,'by_face':{},
             'experimental_budget_mm':BUDGET_MM,'continuous_trim_hausdorff_certified':False,
             'apmesh_cpp_tri_quad':'NOT_RUN'}
    mapping=full_correspondence(source.decode(),native)
    for face_id in [int(f) for f in report['faces']]:
        face=native.Faces()[FACE_TO_NATIVE[face_id]]
        plane=BRepAdaptor_Surface(face.wrapped).Plane()
        original_segments,_=recover_source_sides(source,native,*read_bp(parent.decode()),face_id)
        native_edge_samples=0;edge_dist=0
        for eid in sorted(set(eid for eid,_ in original_segments)):
            curve=BRepAdaptor_Curve(mapping['native_edges'][mapping['edge_map'][eid]].wrapped)
            lo,hi=curve.FirstParameter(),curve.LastParameter()
            for sid,ids in original_segments:
                if sid!=eid:continue
                for k in range(21):
                    dist=_source_edge_closest(curve,_cubic(pts,ids,k/20),sample_count=257);edge_dist=max(edge_dist,dist)
                    native_edge_samples+=1
        if edge_dist>BUDGET_MM:
            raise ValueError('Original source-native curve budget exceeded')
        per={'native_interior_IN':0,'native_boundary_IN_or_ON':0,'native_boundary_OUT':0,
             'native_original_edge_samples':native_edge_samples,
             'max_native_curve_distance_mm':edge_dist,'max_plane_distance_mm':0.}
        for patch in patches[report['faces'][str(face_id)]['first_new_patch']:
                             report['faces'][str(face_id)]['first_new_patch']+report['faces'][str(face_id)]['new_patch_count']]:
            net=[pts[i] for i in patch]
            for j in range(interior_grid):
                for k in range(interior_grid):
                    p=surface(net,(j+.5)/interior_grid,(k+.5)/interior_grid)
                    uv=ElSLib.Parameters_s(plane,gp_Pnt(*p))
                    if BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State()!=TopAbs_IN:
                        raise ValueError('Candidate patch interior outside original trimmed native face')
                    per['native_interior_IN']+=1
                    per['max_plane_distance_mm']=max(per['max_plane_distance_mm'],plane.Distance(gp_Pnt(*p)))
            for label in ('bottom','right','top','left'):
                ids=_side(patch,label)
                for k in range(boundary_grid):
                    p=_cubic(pts,ids,k/(boundary_grid-1))
                    uv=ElSLib.Parameters_s(plane,gp_Pnt(*p))
                    if BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State() in (TopAbs_IN,TopAbs_ON):
                        per['native_boundary_IN_or_ON']+=1
                    else:
                        per['native_boundary_OUT']+=1
        summary['native_interior_IN']+=per['native_interior_IN']
        summary['native_boundary_IN_or_ON']+=per['native_boundary_IN_or_ON']
        summary['native_boundary_OUT']+=per['native_boundary_OUT']
        summary['max_plane_distance_mm']=max(summary['max_plane_distance_mm'],per['max_plane_distance_mm'])
        summary['max_boundary_native_curve_distance_mm']=max(summary['max_boundary_native_curve_distance_mm'],edge_dist)
        summary['original_native_curve_samples']+=native_edge_samples
        per['area_and_orientation']=audit_native_patch_coverage(face,pts,patches[
            report['faces'][str(face_id)]['first_new_patch']:
            report['faces'][str(face_id)]['first_new_patch']+report['faces'][str(face_id)]['new_patch_count']])
        summary['by_face'][str(face_id)]=per
        if per['native_boundary_OUT']:
            summary['native_boundary_out_by_face'][str(face_id)]=per['native_boundary_OUT']
    if summary['max_plane_distance_mm']>1e-7:
        raise ValueError('Candidate leaves its analytic original plane')
    if summary['native_boundary_OUT']:
        summary['status']='BLOCKED_ORIGINAL_NATIVE_TRIM'
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-step',required=True)
    parser.add_argument('--baseline-bp',required=True)
    parser.add_argument('--baseline-manifest',required=True)
    parser.add_argument('--output-dir',required=True)
    parser.add_argument('--faces',nargs='+',type=int,default=[1827,1907,3044])
    parser.add_argument('--interior-grid',type=int,default=9)
    parser.add_argument('--boundary-grid',type=int,default=11)
    args=parser.parse_args()
    source=Path(args.source_step).read_bytes()
    parent=Path(args.baseline_bp).read_bytes()
    manifest=json.loads(Path(args.baseline_manifest).read_text())
    native=cq.importers.importStep(args.source_step).val()
    candidate,report=build_candidate(source,native,parent,manifest,faces=tuple(args.faces))
    audit=audit_candidate(source,native,parent,manifest,candidate,report,
                          interior_grid=args.interior_grid,boundary_grid=args.boundary_grid)
    output=Path(args.output_dir);output.mkdir(parents=True,exist_ok=True)
    (output/'s40_three_curved_planar.CANDIDATE.bp').write_text(candidate)
    (output/'candidate_manifest.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (output/'native_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'candidate':{k:v for k,v in report.items() if k!='faces'},'native_audit':audit},indent=2))


if __name__=='__main__':
    main()
