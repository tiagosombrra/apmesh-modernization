#!/usr/bin/env python3
"""S40-F1: fail-closed six-edge source-conforming planar Bezier pilot.

The candidate is never admitted solely from generating an indexed BP. All
native CAD checks, reverse-curve lineage, and trim gates must pass separately.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math

from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.ElSLib import ElSLib
from OCP.GeomAbs import GeomAbs_Circle
from OCP.TopAbs import TopAbs_IN, TopAbs_ON
from OCP.gp import gp_Pnt, gp_Pnt2d, gp_Vec
import cadquery as cq
from scipy.optimize import minimize_scalar

from audit_analytic_bp import read_bp, surface
from s3c_step_source_gate import parse_entities, oriented_edges, coordinates
from s3r_s40_conforming_hole_join import _edge_adjacency, _side
from s3s_full_original_face_census import full_correspondence
from s3t_s40_planar_octagons import _coons_interior, _lerp
from s3y_s40_curved_planar_rings import quadrangulate, audit_native_patch_coverage
from s3i_joint_source_atlas import _serialize

SOURCE_SHA = 'b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b'
PARENT_SHA = 'af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177'
BUDGET_MM = 0.001
TARGETS = (1279, 1386)
TARGET_SOURCE_EDGES = {
    1279: {1139: 'LINE', 1284: 'LINE', 1002: 'LINE',
           1307: 'CIRCLE', 1336: 'CIRCLE', 1365: 'LINE'},
    1386: {1259: 'LINE', 1080: 'LINE', 1473: 'LINE',
           1392: 'LINE', 1415: 'CIRCLE', 1444: 'CIRCLE'},
}
EXPECTED_INHERITED_EDGES = {1279: frozenset((1139,1284,1002)),
                            1386: frozenset((1259,1080,1473))}


def validate_frozen(source, bp, manifest, budget=BUDGET_MM):
    """No post-hoc tolerance or parent substitution is accepted."""
    if budget != BUDGET_MM:
        raise ValueError('Original 0.001-mm pilot budget changed')
    if sha256(source).hexdigest() != SOURCE_SHA:
        raise ValueError('Original S40 STEP hash mismatch')
    if sha256(bp).hexdigest() != PARENT_SHA:
        raise ValueError('Accepted S3.Y BP hash mismatch')
    pts, patches = read_bp(bp.decode('utf-8'))
    if (len(pts), len(patches)) != (1665, 156):
        raise ValueError('Accepted S3.Y BP cardinality changed')
    if (manifest.get('selected_bp_sha256') != PARENT_SHA and
        manifest.get('candidate_bp_sha256') != PARENT_SHA and
        manifest.get('bp_sha256') != PARENT_SHA):
        raise ValueError('Accepted S3.Y manifest does not bind its original BP')
    adj = _edge_adjacency(patches)
    if (sum(len(v)==2 for v in adj.values()),sum(len(v)==1 for v in adj.values())) != (264,96):
        raise ValueError('Accepted S3.Y indexed seam census changed')
    return pts, patches


def cubic_point(net,t):
    """Evaluate a cubic Bezier edge without changing its control identity."""
    w=((1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3)
    return tuple(sum(w[j]*net[j][k] for j in range(4)) for k in range(3))


def distance(a,b):
    return math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))


def curve_distance(native_curve, p, *, divisions=48):
    """Locally optimize distance to the bounded original native curve."""
    a,b=native_curve.FirstParameter(),native_curve.LastParameter()
    if not math.isfinite(a+b) or b<=a:
        raise ValueError('Unbounded or degenerate STEP native curve')
    params=[a+(b-a)*i/divisions for i in range(divisions+1)]
    distances=[distance(native_curve.Value(t).Coord(),p) for t in params]
    imin=min(range(len(params)),key=lambda i:distances[i])
    lo=params[max(0,imin-1)];hi=params[min(divisions,imin+1)]
    def objective(t):
        q=native_curve.Value(t).Coord()
        return sum((q[i]-p[i])**2 for i in range(3))
    if lo==hi:return distances[imin]
    found=minimize_scalar(objective,bounds=(lo,hi),method='bounded',options={'xatol':1e-13})
    return min(distances[imin],math.sqrt(max(0.0,objective(found.x))))


def check_curve_fit(pts, ids, native_curve, *, samples=17, limit=BUDGET_MM):
    """Reject inherited/new curves whose sampled error exceeds frozen limit."""
    err=0.0
    for i in range(samples):
        x=cubic_point(tuple(pts[n] for n in ids),i/(samples-1))
        err=max(err,curve_distance(native_curve,x))
        if err>=limit:
            return err,False
    return err,True


def _unit(v):
    length=math.sqrt(sum(x*x for x in v))
    if length<=1e-14:
        raise ValueError('Degenerate source curve tangent')
    return tuple(x/length for x in v)


def circle_piece(curve,a,b):
    """Approximate one analytic circular arc with the tangent cubic formula."""
    if curve.GetType()!=GeomAbs_Circle:
        raise ValueError('Native source master curve is not a CIRCLE')
    if not 0 < b-a < math.pi:
        raise ValueError('Unbounded or reversed source circular segment')
    p0,p1=gp_Pnt(),gp_Pnt()
    v0,v1=gp_Vec(),gp_Vec()
    curve.D1(a,p0,v0);curve.D1(b,p1,v1)
    radius=curve.Circle().Radius()
    tangent0=_unit((v0.X(),v0.Y(),v0.Z()))
    tangent1=_unit((v1.X(),v1.Y(),v1.Z()))
    k=(4./3.)*radius*math.tan((b-a)/4.)
    a0=p0.Coord();a3=p1.Coord()
    controls=(a0,tuple(a0[i]+k*tangent0[i] for i in range(3)),
              tuple(a3[i]-k*tangent1[i] for i in range(3)),a3)
    return controls


def fit_circle_source_segments(curve, *, limit=BUDGET_MM):
    """Adapt circle segments until all sampled deviations fit predeclared error."""
    if curve.GetType()!=GeomAbs_Circle:
        raise ValueError('Noncircular original STEP edge in arc builder')
    lo,hi=curve.FirstParameter(),curve.LastParameter()
    span=hi-lo
    if not math.isfinite(span) or not 0<span<2*math.pi+1e-7:
        raise ValueError('Invalid native source circle parameter sweep')
    n=max(1,math.ceil(span/1.0))
    for _ in range(7):
        if n>64:break
        pieces=[];max_err=0.0;success=True
        for i in range(n):
            a=lo+span*i/n;b=lo+span*(i+1)/n
            controls=circle_piece(curve,a,b)
            for j in range(33):
                u=j/32
                p=cubic_point(controls,u)
                # Bezier u and native circle angle are not synchronized parameters.
                # Compare the physical point to the trimmed original edge instead.
                deviation=curve_distance(curve,p,divisions=64)
                max_err=max(max_err,deviation)
                if deviation>=limit*0.75:success=False
            pieces.append(controls)
        if success:return pieces,max_err
        n*=2
    raise ValueError('Cannot fit original circular edge under fixed 0.001-mm budget')


def indexed_open_sides(patches):
    """Collect only open edges, preserving their global integer control IDs."""
    adj=_edge_adjacency(patches)
    return [(pid,label,tuple(_side(patch,label)))
            for pid,patch in enumerate(patches) for label in ('bottom','right','top','left')
            if len(adj[tuple(sorted(_side(patch,label)))])==1]


def recover_inherited_source_chain(table, original_entry, native_curve, pts, open_sides):
    """Require original source vertex endpoints and unique exact indexed chain."""
    a=coordinates(table,original_entry['start_vertex_id'])
    b=coordinates(table,original_entry['end_vertex_id'])
    eligible=[]
    for pid,label,ids in open_sides:
        # Cheap source-endpoint/original-curve screen before the expensive audit.
        if min(distance(pts[ids[0]],a),distance(pts[ids[-1]],a),
               distance(pts[ids[0]],b),distance(pts[ids[-1]],b))>5e-4:
            # Potential interior split pieces are selected by the full curve screen below.
            mid=cubic_point(tuple(pts[k] for k in ids),0.5)
            if curve_distance(native_curve,mid,divisions=24)>BUDGET_MM:
                continue
        deviation,ok=check_curve_fit(pts,ids,native_curve,samples=9)
        if ok:eligible.append((pid,label,ids))
    starters=[(pid,label,ids if distance(pts[ids[0]],a)<1e-5 else tuple(reversed(ids)))
              for pid,label,ids in eligible if min(distance(pts[ids[0]],a),distance(pts[ids[-1]],a))<1e-5]
    if len(starters)!=1:
        raise ValueError('Original source shared edge has no unique indexed start')
    chosen=[starters[0]];seen={(chosen[0][0],chosen[0][1])}
    while distance(pts[chosen[-1][2][-1]],b)>=1e-5:
        endpoint=chosen[-1][2][-1]
        found=[(pid,label,ids if ids[0]==endpoint else tuple(reversed(ids)))
               for pid,label,ids in eligible if (pid,label) not in seen and endpoint in (ids[0],ids[-1])]
        if len(found)!=1:
            raise ValueError('Original source curve has missing/ambiguous indexed successor')
        chosen.append(found[0]);seen.add((found[0][0],found[0][1]))
    if len(chosen)!=len(eligible):
        raise ValueError('Unmatched or duplicate indexed source-curve segments')
    return chosen


def prebind_inherited_original_vertices(table, edges, recovered_chains, points, vertex_index):
    """Bind all original inherited endpoints before creating new curve controls.

    Original STEP edge-loop order is not a safe order in which to allocate
    global control indices: an unrepresented edge may precede its inherited
    neighbor. Preserving the inherited integer identity requires a full
    prepass across every inherited edge of each target face.
    """
    for edge in edges:
        eid = edge['edge_curve_id']
        if eid not in recovered_chains:
            continue
        chain = recovered_chains[eid]
        if not chain:
            raise ValueError('Inherited original source edge has no indexed segments')
        ids_chain = [tuple(row[2]) for row in chain]
        if any(len(ids) != 4 for ids in ids_chain):
            raise ValueError('Inherited source control side must be cubic')
        for vertex_id, control_id in (
            (edge['start_vertex_id'], ids_chain[0][0]),
            (edge['end_vertex_id'], ids_chain[-1][-1]),
        ):
            if not isinstance(control_id, int) or not 0 <= control_id < len(points):
                raise ValueError('Inherited STEP vertex points to an invalid global control')
            expected = coordinates(table, vertex_id)
            if distance(points[control_id], expected) >= 1e-5:
                raise ValueError('Inherited endpoint is not the original STEP vertex')
            if vertex_id in vertex_index and vertex_index[vertex_id] != control_id:
                raise ValueError('Original STEP vertex has conflicting global control IDs')
            vertex_index[vertex_id] = control_id
    return vertex_index


def _native_uv_state(face, xyz):
    plane=BRepAdaptor_Surface(face.wrapped).Plane()
    uv=ElSLib.Parameters_s(plane,gp_Pnt(*xyz))
    return BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State()


def _oriented_normal(a,b,c):
    ab=tuple(b[i]-a[i] for i in range(3));ac=tuple(c[i]-a[i] for i in range(3))
    return (ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0])


def build_source_candidate(source, native, parent, parent_manifest, *, faces=TARGETS):
    """Construct source-identified unadmitted candidate without parent modifications."""
    points,patches=validate_frozen(source,parent,parent_manifest)
    parent_pts=list(points);parent_patches=list(patches)
    table=parse_entities(source.decode())
    mapping=full_correspondence(source.decode(),native)
    open_sides=indexed_open_sides(patches)
    points=list(points);patches=list(patches)
    used_prior=set();source_vertices={};new_source_curves={};metadata={}
    all_new_source_segment_keys=set()
    for fid in faces:
        if fid not in TARGETS or str(fid) in metadata:
            raise ValueError('Unknown or duplicate source face')
        typ,wires=oriented_edges(table,fid)
        if typ!='PLANE' or len(wires)!=1 or len(wires[0])!=6:
            raise ValueError('Expected one six-curve original native planar boundary')
        edges=wires[0]
        if {e['edge_curve_id']:e['master_3d_curve'] for e in edges} != TARGET_SOURCE_EDGES[fid]:
            raise ValueError('Original target source-edge graph changed')
        if any(edges[i]['end_vertex_id']!=edges[(i+1)%6]['start_vertex_id'] for i in range(6)):
            raise ValueError('Original STEP wire is disconnected')
        indexed=[];edge_manifest={}
        # Prebind every old source endpoint before allocating any new index.
        inherited_chains = {}
        for e in edges:
            eid = e['edge_curve_id']
            if eid not in EXPECTED_INHERITED_EDGES[fid]:
                continue
            owners = mapping['owners'][eid]
            if len(owners) != 2 or fid not in owners:
                raise ValueError('Unexpected original inherited source edge owner count')
            curve = BRepAdaptor_Curve(mapping['native_edges'][mapping['edge_map'][eid]].wrapped)
            chain = recover_inherited_source_chain(table, e, curve, points, open_sides)
            for pid, label, ids in chain:
                if (pid, label) in used_prior:
                    raise ValueError('Already consumed original indexed side')
                used_prior.add((pid, label))
            inherited_chains[eid] = chain
        prebind_inherited_original_vertices(table, edges, inherited_chains,
                                             points, source_vertices)
        for e in edges:
            eid=e['edge_curve_id'];curve=BRepAdaptor_Curve(mapping['native_edges'][mapping['edge_map'][eid]].wrapped)
            owners=mapping['owners'][eid]
            if len(owners)!=2 or fid not in owners:
                raise ValueError('Unexpected original face/source edge owner count')
            if eid in EXPECTED_INHERITED_EDGES[fid]:
                chain=inherited_chains[eid]
                ids_chain=[ids for _,_,ids in chain]
                edge_manifest[str(eid)]={'kind':'inherited','segment_count':len(chain),
                   'prior_patch_sides':[[pid,label] for pid,label,_ in chain]}
            else:
                if eid in new_source_curves:
                    raise ValueError('New original source curve duplicated')
                if e['master_3d_curve']=='CIRCLE':
                    segments,max_dev=fit_circle_source_segments(curve)
                elif e['master_3d_curve']=='LINE':
                    p0=curve.Value(curve.FirstParameter()).Coord()
                    p3=curve.Value(curve.LastParameter()).Coord()
                    segments=[(p0,_lerp(p0,p3,1/3),_lerp(p0,p3,2/3),p3)]
                    max_dev=0.0
                else:
                    raise ValueError('Source edge curve type unsupported')
                start=coordinates(table,e['start_vertex_id'])
                end=coordinates(table,e['end_vertex_id'])
                if distance(segments[0][0],start)<1e-5 and distance(segments[-1][-1],end)<1e-5:
                    pass
                elif distance(segments[0][0],end)<1e-5 and distance(segments[-1][-1],start)<1e-5:
                    segments=[tuple(reversed(net)) for net in reversed(segments)]
                else:
                    raise ValueError('Native original curve direction fails STEP vertex identity')
                ids_chain=[]
                for seg_i,net in enumerate(segments):
                    ids=[]
                    for k in range(4):
                        vid=e['start_vertex_id'] if seg_i==0 and k==0 else (
                            e['end_vertex_id'] if seg_i==len(segments)-1 and k==3 else None)
                        if vid is not None and vid in source_vertices:
                            idx=source_vertices[vid]
                            if distance(points[idx],net[k])>1e-5:
                                raise ValueError('Existing vertex ID disagrees with original curve')
                        elif seg_i and k==0:
                            idx=ids_chain[-1][-1]
                        else:
                            idx=len(points);points.append(net[k])
                        if vid is not None:source_vertices[vid]=idx
                        ids.append(idx)
                    ids_chain.append(tuple(ids))
                new_source_curves[eid]=tuple(ids_chain)
                for ids in ids_chain:
                    key=tuple(sorted(ids))
                    if key in all_new_source_segment_keys:
                        raise ValueError('Duplicate original open source segment')
                    all_new_source_segment_keys.add(key)
                edge_manifest[str(eid)]={'kind':'new_original_source_curve','segment_count':len(segments),
                   'max_sampled_analytic_curve_deviation_mm':max_dev,
                   'future_join_key':f'original/EDGE_CURVE/#{eid}'}
            indexed.extend((eid,ids) for ids in ids_chain)
        if len(indexed)%2:
            # An odd boundary requires a canonical source-edge subdivision; do not
            # quietly introduce a T-junction or reindex previously accepted edges.
            raise ValueError('Odd inherited boundary-piece count requires explicit source split')
        if any(indexed[i][1][-1]!=indexed[(i+1)%len(indexed)][1][0]
               for i in range(len(indexed))):
            raise ValueError('Source-boundary corner control IDs are not closed')
        native_index=mapping['face_map'][fid]
        region=native.Faces()[native_index]
        cells,partition=quadrangulate(points,indexed,region,(len(indexed)-2)//2)
        side_map={frozenset((ids[0],ids[-1])):ids for _,ids in indexed}
        diagonals={};first_patch=len(patches)
        normal=region.normalAt().toTuple()
        for cell in cells:
            corners=list(cell)
            normal_geom=_oriented_normal(points[corners[0]],points[corners[1]],points[corners[3]])
            if sum(normal[i]*normal_geom[i] for i in range(3))<0:
                corners=[corners[0],corners[3],corners[2],corners[1]]
            borders=[]
            for j in range(4):
                a,b=corners[j],corners[(j+1)%4]
                key=frozenset((a,b))
                if key in side_map:ids=side_map[key]
                else:
                    if key not in diagonals:
                        low,high=sorted((a,b))
                        diagonals[key]=(low,len(points),len(points)+1,high)
                        points.extend((_lerp(points[low],points[high],1/3),
                                       _lerp(points[low],points[high],2/3)))
                    ids=diagonals[key]
                borders.append(tuple(ids if ids[0]==a else reversed(ids)))
            nets=_coons_interior([[points[k] for k in ids] for ids in borders])
            matrix=[[None]*4 for _ in range(4)]
            for col,k in enumerate(borders[0]):matrix[0][col]=k
            for row,k in enumerate(borders[1]):matrix[row][3]=k
            for col,k in enumerate(reversed(borders[2])):matrix[3][col]=k
            for row,k in enumerate(reversed(borders[3])):matrix[row][0]=k
            for row in (1,2):
                for col in (1,2):
                    matrix[row][col]=len(points);points.append(nets[row][col])
            patches.append(tuple(k for row in matrix for k in row))
        metadata[str(fid)]={'source_advanced_face_id':fid,'source_native_face_index':native_index,
           'first_patch':first_patch,'new_patches':len(cells),'source_boundary_segments':len(indexed),
           'source_edge_lineage':edge_manifest,'partition':partition}
    if patches[:len(parent_patches)]!=parent_patches or points[:len(parent_pts)]!=parent_pts:
        raise ValueError('Previously admitted S3.Y control net changed')
    adj=_edge_adjacency(patches)
    if any(len(v)>2 for v in adj.values()):
        raise ValueError('New exact indexed seam has overincidence')
    for pid,side in used_prior:
        if len(adj[tuple(sorted(_side(parent_patches[pid],side)))])!=2:
            raise ValueError('Inherited original source side failed to join')
    new_old=new_new=new_open=0
    for key,users in adj.items():
        if not any(pid>=156 for pid,_side_name,_ids in users):
            continue
        if len(users)==1:
            if key not in all_new_source_segment_keys:
                raise ValueError('New patch leaves an unexplained open side')
            new_open+=1
            continue
        if len(users)!=2 or users[0][0]==users[1][0]:
            raise ValueError('New patch has self-paired or overincident side')
        (a_pid,a_side,_),(b_pid,b_side,_)=users
        a_ids=tuple(_side(patches[a_pid],a_side))
        b_ids=tuple(_side(patches[b_pid],b_side))
        # Bottom/right traverse forward; top/left traverse reversed in CCW order.
        oriented_a=a_ids[::-1] if a_side in ('top','left') else a_ids
        oriented_b=b_ids[::-1] if b_side in ('top','left') else b_ids
        if oriented_a!=oriented_b[::-1]:
            raise ValueError('Source-indexed patch side orientation is inconsistent')
        if a_pid>=156 and b_pid>=156:new_new+=1
        else:new_old+=1
    if len(new_source_curves)!=6 or new_old!=len(used_prior) or new_open!=len(all_new_source_segment_keys):
        raise ValueError('Original source edge incidence ledger differs from candidate')
    if 4*(len(patches)-156)!=new_old+2*new_new+new_open:
        raise ValueError('Incomplete indexed topology for new planar patches')
    if sum(len(v)==2 for v in adj.values())!=264+new_old+new_new or sum(len(v)==1 for v in adj.values())!=96-new_old+new_open:
        raise ValueError('Global edge incidence census changed')
    candidate=_serialize(points,patches)
    receipt={'schema':'s40f1-source-indexed-six-sided-curved-planar-candidate-v1',
        'state':'UNADMITTED_UNTIL_ORIGINAL_NATIVE_AUDIT',
        'source_sha256':SOURCE_SHA,'parent_sha256':PARENT_SHA,
        'candidate_sha256':sha256(candidate.encode()).hexdigest(),
        'parent_patches':156,'new_patches':len(patches)-156,
        'candidate_patches':len(patches),'candidate_controls':len(points),
        'two_sided_exact_seams':sum(len(v)==2 for v in adj.values()),
        'new_to_old_exact_joins':new_old,'new_internal_exact_joins':new_new,
        'new_open_original_source_segments':new_open,
        'open_indexed_sides':sum(len(v)==1 for v in adj.values()),
        'source_faces':metadata,
        'canonical_new_source_edge_control_id_chains':{str(eid):[list(ids) for ids in chains]
                                                       for eid,chains in sorted(new_source_curves.items())},
        'native_trims_checked':False}
    return candidate,receipt


def audit_native(source, native, parent, manifest, candidate, receipt,
                 *, inside_grid=13, boundary_grid=31):
    """Independent original native plane trim gate (finite sampling, not proof)."""
    validate_native_sample_grids(inside_grid, boundary_grid)
    regenerated,baseline=build_source_candidate(source,native,parent,manifest)
    if candidate!=regenerated or receipt!=baseline:
        raise ValueError('Unverifiable candidate lineage or edited receipt')
    pts,patches=read_bp(candidate)
    summary={'status':'PASS_BOUNDED_SAMPLED_NATIVE_TRIM','inside_IN':0,'boundary_IN_or_ON':0,
        'boundary_OUT':0,'by_face':{},'continuous_hausdorff_certified':False,
        'apmesh_TRI_QUAD_executed':False}
    for fid in TARGETS:
        region=receipt['source_faces'][str(fid)]
        face=native.Faces()[region['source_native_face_index']]
        start=region['first_patch'];end=start+region['new_patches']
        inside=outside=boundary_pass=0
        plane=BRepAdaptor_Surface(face.wrapped).Plane()
        for patch in patches[start:end]:
            net=[pts[k] for k in patch]
            for i in range(inside_grid):
                for j in range(inside_grid):
                    p=surface(net,(i+.5)/inside_grid,(j+.5)/inside_grid)
                    if _native_uv_state(face,p)!=TopAbs_IN:
                        raise ValueError(f'Original native face #{fid} interior samples OUT')
                    if plane.Distance(gp_Pnt(*p))>1e-7:
                        raise ValueError('New original plane support deviation')
                    inside+=1
            for side in ('bottom','right','top','left'):
                ids=_side(patch,side)
                for i in range(boundary_grid):
                    p=cubic_point([pts[k] for k in ids],i/(boundary_grid-1))
                    if _native_uv_state(face,p) in (TopAbs_IN,TopAbs_ON):boundary_pass+=1
                    else:outside+=1
        summary['inside_IN']+=inside;summary['boundary_IN_or_ON']+=boundary_pass
        summary['boundary_OUT']+=outside
        coverage=audit_native_patch_coverage(face,pts,patches[start:end],boundary_density=41)
        summary['by_face'][str(fid)]={'interior_IN':inside,'boundary_IN_or_ON':boundary_pass,
                                     'boundary_OUT':outside,'candidate_patches':end-start,
                                     'sampled_native_coverage':coverage}
    if summary['boundary_OUT']:
        summary['status']='BLOCKED_NATIVE_TRIM'
    return summary


def require_native_pilot_pass(audit):
    """Keep an original-native rejection from returning a successful exit code.

    This only allows the experimental sampled CAD gate to proceed. It does
    not certify complete CAD equivalence or APMesh C++ mesh acceptance.
    """
    if not isinstance(audit, dict):
        raise ValueError('Missing original S40 native audit receipt')
    if audit.get('status') != 'PASS_BOUNDED_SAMPLED_NATIVE_TRIM':
        raise ValueError('Original STEP native trim was not admitted')
    if audit.get('boundary_OUT') != 0 or audit.get('inside_IN', 0) <= 0:
        raise ValueError('Original STEP native trim counts failed')
    if audit.get('boundary_IN_or_ON', 0) <= 0:
        raise ValueError('Native original boundary samples were not executed')
    by_face = audit.get('by_face')
    if not isinstance(by_face, dict) or set(by_face) != {'1279', '1386'}:
        raise ValueError('Original STEP native target-face evidence is incomplete')
    for fid in ('1279', '1386'):
        face = by_face[fid]
        if (not isinstance(face, dict) or face.get('boundary_OUT') != 0 or
                face.get('interior_IN', 0) <= 0 or face.get('boundary_IN_or_ON', 0) <= 0 or
                face.get('candidate_patches', 0) <= 0 or
                not isinstance(face.get('sampled_native_coverage'), dict)):
            raise ValueError(f'Original STEP native face #{fid} failed admission evidence')
        coverage = face['sampled_native_coverage']
        if coverage.get('continuous_coverage_certified') is not False:
            raise ValueError('Unsupported continuous CAD coverage certification claim')
        metrics = ('native_area_mm2', 'approximate_integrated_bp_area_mm2',
                   'min_sampled_oriented_jacobian', 'sampled_relative_area_difference',
                   'sampled_2d_patch_overlap_area', 'sampled_numerical_hole_area_mm2')
        for key in metrics:
            value = coverage.get(key)
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError(f'Original STEP native face #{fid} missing finite {key}')
        if (coverage['native_area_mm2'] <= 0 or
                coverage['approximate_integrated_bp_area_mm2'] <= 0 or
                coverage['min_sampled_oriented_jacobian'] <= 0 or
                not 0 <= coverage['sampled_relative_area_difference'] <= 1e-4 or
                not -1e-7 <= coverage['sampled_2d_patch_overlap_area'] <= 1e-5 or
                not 0 <= coverage['sampled_numerical_hole_area_mm2'] <= 1e-7):
            raise ValueError(f'Original STEP native face #{fid} coverage metrics failed')
    if sum(by_face[fid]['interior_IN'] for fid in ('1279', '1386')) != audit['inside_IN'] or \
            sum(by_face[fid]['boundary_IN_or_ON'] for fid in ('1279', '1386')) != audit['boundary_IN_or_ON']:
        raise ValueError('Original STEP native global and per-face sample counts differ')
    if audit.get('continuous_hausdorff_certified') is not False or \
            audit.get('apmesh_TRI_QUAD_executed') is not False:
        raise ValueError('Unsupported continuous or production mesh certification claim')
    return True


def validate_native_sample_grids(inside_grid, boundary_grid):
    """Prevent zero-sample and unbounded sampling options from bypassing a gate."""
    if any(type(v) is not int for v in (inside_grid, boundary_grid)):
        raise ValueError('Original STEP sampling grid must use integer densities')
    if not 3 <= inside_grid <= 33 or not 11 <= boundary_grid <= 161:
        raise ValueError('Invalid original STEP native sampling density')
    return True


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--original-step',type=Path,required=True)
    cli.add_argument('--selected-s3y-bp',type=Path,required=True)
    cli.add_argument('--selected-s3y-manifest',type=Path,required=True)
    cli.add_argument('--output',type=Path,required=True)
    args=cli.parse_args()
    args.output.mkdir(exist_ok=True,parents=True)
    try:
        original=args.original_step.read_bytes()
        bp=args.selected_s3y_bp.read_bytes()
        manifest=json.loads(args.selected_s3y_manifest.read_text())
        validate_frozen(original,bp,manifest)
        native=cq.importers.importStep(str(args.original_step)).val()
        candidate,receipt=build_source_candidate(original,native,bp,manifest)
        audit=audit_native(original,native,bp,manifest,candidate,receipt)
        # A rejected native trim must not produce exit status zero or an approved BP.
        require_native_pilot_pass(audit)
    except (ValueError, OSError, KeyError, IndexError, RuntimeError, TypeError, OverflowError) as exc:
        # Preserve an explicit rejection and never issue an accepted BP on failure.
        failure={'schema':'s40f1-fail-closed-native-checkpoint-v1',
                 'state':'BLOCKED_NO_NEW_FACE_ADMISSION',
                 'error_type':type(exc).__name__, 'reason':str(exc),
                 'selected_atlas_patches_unchanged':156,
                 'original_faces_represented_unchanged':22}
        (args.output/'s40f1_rejection.json').write_text(json.dumps(failure,indent=2)+'\n')
        print(json.dumps(failure,indent=2))
        raise SystemExit(3)
    filename='s40f1.BOUNDED_RESEARCH_CANDIDATE.bp'
    (args.output/filename).write_text(candidate)
    (args.output/'s40f1_manifest.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    (args.output/'s40f1_native_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'candidate':filename,'receipt':receipt,'native':audit},indent=2))

if __name__=='__main__':
    main()
