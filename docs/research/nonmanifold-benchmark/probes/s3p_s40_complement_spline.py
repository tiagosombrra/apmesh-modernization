#!/usr/bin/env python3
"""S3.P: Pinned S40 #2457 complementary half-cylinder B-spline trim pilot.

The source/native curve identity and individual edge trim are checked before
admission; all published receipts are nongeometric research evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Curve2d
from OCP.BRepTools import BRepTools

from audit_analytic_bp import read_bp, surface
from s3c_step_source_gate import SOURCES, coordinates, entity, oriented_edges, parse_entities, refs
from s3g_cylindrical_source_constraints import _axis_support, _point
from s3i_joint_source_atlas import _serialize
from s3j_radial_support_enclosure import certify_patch
from s3k_native_uv_trim_gate import classify_patch
from s3m_s40_complex_trim_inventory import inventory
from s3n_s40_orthogonal_trim import _add, _cross, _dot, _linear_source_edge, _norm, _scale, _sub, _uv_point
from s3o_s40_spline_trim import _pcurve, _angular_tangents

FACE = 2457
BASELINE_FACE = 1519
EDGES = (2309, 2251, 1616, 1911, 2434, 2096, 2407, 1886, 1753)
SPLINE_EDGES = (2309, 2251, 2096)
GENERATOR_EDGES = (1616, 2434, 2407, 1753)
EXISTING_SEAMS = (1616, 1753)
SOURCE_UV_TOL = 1e-8
CONTROL_TOL_MM = 1e-8
BUDGET_MM = .001


def _frame(table):
    sid, origin, axis, radius = _axis_support(table, FACE)
    _,raw = entity(table,sid,'CYLINDRICAL_SURFACE')
    _,place = entity(table,refs(raw)[0],'AXIS2_PLACEMENT_3D')
    frame_refs = refs(place)
    if len(frame_refs)!=3 or abs(radius-16.)>1e-8:
        raise ValueError('S3.P source support frame/radius mismatch')
    x = _point(table,frame_refs[2],expected='DIRECTION')
    x = _scale(x,1/_norm(x))
    y = _cross(axis,x)
    if abs(_dot(x,axis))>1e-10 or abs(_norm(y)-1)>1e-10:
        raise ValueError('S3.P nonorthogonal cylinder frame')
    return {'id':sid,'origin':origin,'axis':axis,'x':x,'y':y,'radius':radius}


def _uv(frame,P):
    delta=_sub(P,frame['origin'])
    theta=math.atan2(_dot(delta,frame['y']),_dot(delta,frame['x']))%(2*math.pi)
    if theta<math.pi/2:
        theta+=2*math.pi
    return (theta,_dot(delta,frame['axis']))


def source_partition(source):
    if sha256(source.encode('utf-8')).hexdigest()!=SOURCES['S40'][1]:
        raise ValueError('Pinned original S40 SHA-256 mismatch')
    table=parse_entities(source)
    support,wires=oriented_edges(table,FACE)
    if support!='CYLINDRICAL_SURFACE' or len(wires)!=1 or len(wires[0])!=9:
        raise ValueError('Original #2457 STEP topology drift')
    if tuple(x['edge_curve_id'] for x in wires[0])!=EDGES:
        raise ValueError('Original #2457 EDGE_CURVE order drift')
    frame=_frame(table)
    records=[];nodes={}
    for source_edge in wires[0]:
        eid=source_edge['edge_curve_id']
        pid,cid,(axis,fixed,kind,control)=_pcurve(table,eid,frame['id'])
        typ=source_edge['master_3d_curve']
        if eid in SPLINE_EDGES:
            if typ!='B_SPLINE_CURVE_WITH_KNOTS' or axis!='V' or kind!='BSPLINE_DEGREE_3':
                raise ValueError('Original #2457 3D/2D spline identity changed')
        elif eid in GENERATOR_EDGES:
            if typ!='LINE' or axis!='U' or kind!='LINE':
                raise ValueError('Original #2457 original generator changed')
        elif typ!='CIRCLE' or axis!='V' or kind not in ('BSPLINE_DEGREE_1','LINE'):
            raise ValueError('Original #2457 short arc changed')
        ids=(source_edge['start_vertex_id'],source_edge['end_vertex_id'])
        xyz=[coordinates(table,id) for id in ids]
        uv=[_uv(frame,P) for P in xyz]
        for ident,P,U in zip(ids,xyz,uv):
            if abs(U[0 if axis=='U' else 1]-fixed)>SOURCE_UV_TOL:
                raise ValueError('Original #2457 source PCURVE/3D endpoint mismatch')
            if ident in nodes and math.dist(nodes[ident]['xyz'],P)>1e-12:
                raise ValueError('Original #2457 topological vertex identity changed')
            nodes[ident]={'xyz':P,'uv':U}
        if axis=='V' and kind.startswith('BSPLINE'):
            angles=sorted([uv[0][0],uv[1][0]])
            controls=sorted([control[0][0],control[-1][0]])
            if max(abs(a-b) for a,b in zip(angles,controls))>SOURCE_UV_TOL:
                raise ValueError('S3.P source spline endpoints mismatch original vertices')
        records.append({'edge_id':eid,'start_vertex_id':ids[0],'end_vertex_id':ids[1],
                        'endpoint_uv':uv,'fixed_axis':axis,'fixed_value':fixed,
                        'curve_type_3d':typ,'cylinder_pcurve_id':pid,
                        'cylinder_pcurve_curve_id':cid,'pcurve_type':kind,
                        'pcurve_control_count':len(control)})
    e={r['edge_id']:r for r in records}
    u0=e[1616]['fixed_value']
    um=e[2434]['fixed_value']
    ut=e[2309]['endpoint_uv'][1][0]
    ur=e[2407]['fixed_value']
    u3=e[1753]['fixed_value']
    z0=e[2096]['fixed_value']
    z1=e[1911]['fixed_value']
    z2=e[2309]['fixed_value']
    if not (abs(u0-math.pi)<1e-8 and u0<um<ut<ur<u3
            and abs(u3-2*math.pi)<1e-8 and z0<z1<z2
            and abs(e[2251]['fixed_value']-z2)<1e-8
            and abs(e[1886]['fixed_value']-z1)<1e-8):
        raise ValueError('S3.P source nine-edge UV step geometry changed')
    corners=[(u3,z2),(ut,z2),(u0,z2),(u0,z1),(um,z1),
             (um,z0),(ur,z0),(ur,z1),(u3,z1)]
    if len(nodes)!=9:
        raise ValueError('Nine original source vertices required')
    for i,row in enumerate(records):
        if max(math.dist(a,b) for a,b in zip(row['endpoint_uv'],
                   [corners[i],corners[(i+1)%9]]))>SOURCE_UV_TOL:
            raise ValueError(f'Original source edge #{row["edge_id"]} not on derived UV polygon')
    # The opposite X reference frame means geometrically complementary halves,
    # despite similar local UV coordinate intervals.
    _,legacy_place=entity(table,refs(entity(table,_frame_of(table,BASELINE_FACE),'CYLINDRICAL_SURFACE')[1])[0],'AXIS2_PLACEMENT_3D')
    old_x=_point(table,refs(legacy_place)[2],expected='DIRECTION')
    old_x=_scale(old_x,1/_norm(old_x))
    if abs(_dot(frame['x'],old_x)+1)>1e-10:
        raise ValueError('Source #1519/#2457 angular frames are not opposing')
    return {'source_sha256':SOURCES['S40'][1],'face_id':FACE,'frame':frame,'source_edges':records,
            'original_vertices':nodes,'u_breaks':[u0,um,ut,ur,u3],
            'v_breaks':[z0,z1,z2],'source_wire_uv':corners,
            'source_wire_original_edge_ids':list(EDGES),
            'source_opposite_reference_x_dot':_dot(frame['x'],old_x)}


def _frame_of(table,fid):
    sid,_,_,_=_axis_support(table,fid)
    return sid


def grid(partition,left_sectors,right_sectors):
    if type(left_sectors)!=int or type(right_sectors)!=int or not 1<=left_sectors<=32 or not 1<=right_sectors<=32:
        raise ValueError('Sector counts must be integers [1,32]')
    u0,u1,ut,u2,u3=partition['u_breaks']
    return ([u0]
            +[u1]
            +[u1+(ut-u1)*i/left_sectors for i in range(1,left_sectors+1)]
            +[ut+(u2-ut)*i/right_sectors for i in range(1,right_sectors+1)]
            +[u3])


def cells(partition,left_sectors,right_sectors):
    values=grid(partition,left_sectors,right_sectors)
    z0,z1,z2=partition['v_breaks']
    return ([(i,1,values[i],values[i+1],z1,z2) for i in range(len(values)-1)]
            +[(i,0,values[i],values[i+1],z0,z1) for i in range(1,len(values)-2)])


def _area(partition,left,right):
    polygon=partition['source_wire_uv']
    area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1])))/2
    pieces=cells(partition,left,right)
    sumarea=sum((u1-u0)*(z1-z0) for _,_,u0,u1,z0,z1 in pieces)
    if abs(area-sumarea)>1e-8:
        raise ValueError('UV partition has lost or duplicated source area')
    for i,c in enumerate(pieces):
        for d in pieces[i+1:]:
            if max(0,min(c[3],d[3])-max(c[2],d[2]))*max(0,min(c[5],d[5])-max(c[4],d[4]))>1e-10:
                raise ValueError('UV partition overlaps')
    return area


def _original_nodes(partition,left,right):
    u=grid(partition,left,right);z=partition['v_breaks'];result={}
    for vid,P in partition['original_vertices'].items():
        candidates=[(i,j) for i,a in enumerate(u) for j,b in enumerate(z)
                    if math.dist((a,b),P['uv'])<SOURCE_UV_TOL]
        if len(candidates)!=1 or candidates[0] in result:
            raise ValueError('Original vertex does not map uniquely to one UV grid node')
        result[candidates[0]]=vid
    if len(result)!=9:
        raise ValueError('Original source corner count lost')
    return result


def _boundary_generator(i,j,ngrid):
    return {(0,1):1616,(1,0):2434,(ngrid-2,0):2407,(ngrid-1,1):1753}.get((i,j))


def build_extension(source,baseline_bp,baseline_manifest,*,left_sectors=2,right_sectors=6,
                    declared_budget_mm=BUDGET_MM):
    part=source_partition(source)
    if declared_budget_mm!=BUDGET_MM:
        raise ValueError('S3.P pilot budget may not be relaxed')
    if baseline_manifest.get('source_model')!='S40' or baseline_manifest.get('source_sha256')!=part['source_sha256']:
        raise ValueError('S3.P previous original BP source identity mismatch')
    if baseline_manifest.get('face_id')!=BASELINE_FACE or baseline_manifest.get('combined_patch_count')!=59:
        raise ValueError('S3.P requires the original S3.O 59-patch baseline')
    if sha256(baseline_bp.encode('utf-8')).hexdigest()!=baseline_manifest.get('combined_bp_sha256'):
        raise ValueError('S3.P changed original prior BP checksum')
    points,patches=read_bp(baseline_bp)
    registry=dict(baseline_manifest['original_global_source_key_to_control_index'])
    if len(points)!=681 or len(patches)!=59 or sorted(registry.values())!=list(range(len(points))):
        raise ValueError('S3.P baseline BP control registry not injective')
    uv_area=_area(part,left_sectors,right_sectors)
    u=grid(part,left_sectors,right_sectors);z=part['v_breaks']
    original_nodes=_original_nodes(part,left_sectors,right_sectors)
    table=parse_entities(source);added=[];generator_keys=defaultdict(set)
    def intern(key,P):
        if not all(math.isfinite(x) for x in P):
            raise ValueError('Non-finite Bézier control')
        if key in registry:
            idx=registry[key]
            if math.dist(points[idx],P)>CONTROL_TOL_MM:
                raise ValueError('Original canonical source control disagrees across faces')
            return idx
        idx=len(points);registry[key]=idx;points.append(tuple(P));return idx
    for ui,zi,ua,ub,za,zb in cells(part,left_sectors,right_sectors):
        du=ub-ua
        if not 0<du<=math.pi/2:
            raise ValueError('Original S3.P angular sector is too broad')
        ids=[]
        for row in range(4):
            v=za+(zb-za)*row/3
            for col in range(4):
                unode=ui+(col==3);znode=zi+(row==3)
                at_u=col in (0,3);at_z=row in (0,3)
                generator=_boundary_generator(unode,zi,len(u)) if at_u else None
                if generator is not None:
                    key,P=_linear_source_edge(table,part,generator,row)
                    generator_keys[generator].add(key)
                elif at_u and at_z:
                    vid=original_nodes.get((unode,znode))
                    key=f'vertex:{vid}' if vid is not None else f's3p_uvnode:{FACE}:{unode}:{znode}'
                    P=coordinates(table,vid) if vid is not None else _uv_point(part['frame'],u[unode],v)
                elif at_u:
                    key=f's3p_uv_vline:{FACE}:{unode}:{zi}:{row}'
                    P=_uv_point(part['frame'],u[unode],v)
                else:
                    key=(f's3p_uv_hline:{FACE}:{ui}:{znode}:{col}' if at_z else
                         f's3p_uv_interior:{FACE}:{ui}:{zi}:{row}:{col}')
                    A=_uv_point(part['frame'],ua,v);B=_uv_point(part['frame'],ub,v)
                    P=(A,_add(A,_angular_tangents(part['frame'],ua,du)),
                       _sub(B,_angular_tangents(part['frame'],ub,du)),B)[col]
                ids.append(intern(key,P))
        patches.append(tuple(ids))
        added.append({'source_advanced_face_id':FACE,
                      'kind':'S3P_SOURCE_SPLINE_SPLIT_TOP_ORTHOGONAL_RECTANGLE',
                      'u_grid_index':ui,'v_strip_index':zi,
                      'native_uv_rectangle':[ua,ub,za,zb],
                      'control_vertex_ids':ids})
    expected_new=2*(left_sectors+right_sectors)+2
    if len(added)!=expected_new:
        raise ValueError('S3.P missed original split-top rectangular pieces')
    for eid in GENERATOR_EDGES:
        expect={_linear_source_edge(table,part,eid,row)[0] for row in range(4)}
        if generator_keys.get(eid)!=expect:
            raise ValueError(f'Lost original generator #{eid} controls')
    for eid in EXISTING_SEAMS:
        for row in range(4):
            key=_linear_source_edge(table,part,eid,row)[0]
            if key not in baseline_manifest['original_global_source_key_to_control_index'] or registry[key]!=baseline_manifest['original_global_source_key_to_control_index'][key]:
                raise ValueError('Original shared source generator controls not reused')
    counts=Counter()
    for patch in patches[59:]:
        for side in (patch[:4],patch[-4:],patch[0:16:4],patch[3:16:4]):
            counts[tuple(sorted(side))]+=1
    if max(counts.values(),default=0)!=2 or sum(q==2 for q in counts.values())!=3*(left_sectors+right_sectors):
        raise ValueError('Invalid indexed internal seam network')
    bp=_serialize(points,patches)
    manifest={'schema':'apmesh-s3p-s40-original-2457-partial-atlas-v1',
              'source_model':'S40','source_sha256':part['source_sha256'],'face_id':FACE,
              'baseline_patch_count':59,'baseline_control_count':681,
              'baseline_bp_sha256':baseline_manifest['combined_bp_sha256'],
              'baseline_manifest_sha256':sha256(json.dumps(baseline_manifest,sort_keys=True).encode()).hexdigest(),
              'pilot_budget_mm':declared_budget_mm,'left_sectors':left_sectors,'right_sectors':right_sectors,
              'original_wire_edge_curve_ids':list(EDGES),'original_spline_edge_ids':list(SPLINE_EDGES),
              'original_source_generator_ids':list(GENERATOR_EDGES),'preexisting_generator_seams':list(EXISTING_SEAMS),
              'source_uv_breaks':{'u':part['u_breaks'],'v':z},
              'source_uv_polygon':part['source_wire_uv'],'source_uv_parametric_area':uv_area,
              'added_patch_count':len(added),'combined_patch_count':len(patches),
              'combined_control_count':len(points),'internal_new_seams':sum(q==2 for q in counts.values()),
              'added_patches':added,'original_global_source_key_to_control_index':registry,
              'combined_bp_sha256':sha256(bp.encode('utf-8')).hexdigest(),
              'native_brep_audit':'NOT_RUN_ON_CONSTRUCTION','full_original_atlas':False,
              'apmesh_tri_quad_meshing':'NOT_RUN'}
    return bp,manifest


def _native_boundary_map(part,table,native,native_index):
    face=native.Faces()[native_index]
    if face.geomType()!='CYLINDER' or len(face.Wires())!=1 or len(face.Edges())!=9:
        raise ValueError('Native #2457 source face topology drift')
    native_edges=native.Edges()
    tol=max(1e-8,native.BoundingBox().DiagonalLength*1e-9)
    output={}
    for row in part['source_edges']:
        eid=row['edge_id']
        endpts=[part['original_vertices'][row[k]]['xyz'] for k in ('start_vertex_id','end_vertex_id')]
        choices=[]
        for e in face.Edges():
            verts=e.Vertices()
            if len(verts)!=2:continue
            expect='BSPLINE' if eid in SPLINE_EDGES else row['curve_type_3d']
            if e.geomType()!=expect:continue
            coords=[tuple(v.Center().toTuple()) for v in verts]
            err=min(max(math.dist(coords[i],endpts[i^flip]) for i in (0,1)) for flip in (0,1))
            if err<=tol:
                candidates=[i for i,n in enumerate(native_edges) if e.wrapped.IsSame(n.wrapped)]
                if len(candidates)!=1:raise ValueError('Native edge index ambiguous')
                choices.append((candidates[0],e,err))
        if len(choices)!=1:raise ValueError(f'Original #2457 source native edge #{eid} ambiguous')
        idx,e,err=choices[0]
        incident=[i for i,f in enumerate(native.Faces()) if any(a.wrapped.IsSame(e.wrapped) for a in f.Edges())]
        if len(incident)!=2 or native_index not in incident:
            raise ValueError('Missing manifold native two-sided edge')
        output[eid]={'native_edge':e,'native_index':idx,'endpoint_distance_mm':err,'incident':incident}
    if len({r['native_index'] for r in output.values()})!=9:
        raise ValueError('Original nine source edges map to duplicate native edge')
    for eid in EXISTING_SEAMS:
        if 12 not in output[eid]['incident']:
            raise ValueError('Expected original spline-cylinder neighbor missing')
    return output


def _boundary_pieces(part,additions):
    """Identify exactly once-used UV sides, then match original source curves."""
    edges=[]
    for ridx,row in enumerate(additions):
        ua,ub,za,zb=row['native_uv_rectangle']
        edges.extend([(ridx,'bottom','V',za,ua,ub),
                      (ridx,'top','V',zb,ua,ub),
                      (ridx,'left','U',ua,za,zb),
                      (ridx,'right','U',ub,za,zb)])
    def key(x):return (x[2],)+tuple(round(a,10) for a in x[3:])
    counts=Counter(key(e) for e in edges)
    boundary=[e for e in edges if counts[key(e)]==1]
    if any(n not in (1,2) for n in counts.values()):
        raise ValueError('Unmatched, duplicate or >2 UV rectangle sides')
    rows={}
    assigned=[]
    for orig in part['source_edges']:
        fixed=orig['fixed_value'];axis=orig['fixed_axis']
        coord=0 if axis=='V' else 1
        lo,hi=sorted((orig['endpoint_uv'][0][coord],orig['endpoint_uv'][1][coord]))
        matched=[e for e in boundary if e[2]==axis and abs(e[3]-fixed)<=SOURCE_UV_TOL and e[4]>=lo-SOURCE_UV_TOL and e[5]<=hi+SOURCE_UV_TOL]
        segments=sorted((e[4],e[5]) for e in matched)
        if not segments or abs(segments[0][0]-lo)>SOURCE_UV_TOL or abs(segments[-1][1]-hi)>SOURCE_UV_TOL:
            raise ValueError(f'Original boundary #{orig["edge_id"]} not fully covered')
        if any(abs(a[1]-b[0])>SOURCE_UV_TOL for a,b in zip(segments,segments[1:])):
            raise ValueError(f'Original boundary #{orig["edge_id"]} has overlap/gap')
        rows[orig['edge_id']]=matched
        assigned.extend(matched)
    if len(assigned)!=len(boundary) or len(set(assigned))!=len(boundary):
        raise ValueError('Original UV boundary is not in bijection with rectangle outer sides')
    return rows, len(boundary)


def _native_edge_distance(part,points,additions,original_edges,boundary_rows,face,budget):
    output=[]
    for orig in part['source_edges']:
        eid=orig['edge_id'];e=original_edges[eid]['native_edge']
        c3=BRepAdaptor_Curve(e.wrapped);c2=BRepAdaptor_Curve2d(e.wrapped,face.wrapped)
        lo,hi=c2.FirstParameter(),c2.LastParameter()
        if abs(c3.FirstParameter()-lo)>1e-8 or abs(c3.LastParameter()-hi)>1e-8:
            raise ValueError('Original 3D/2D native edge parameter intervals differ')
        along_u=orig['fixed_axis']=='V'
        a=c2.Value(lo);b=c2.Value(hi)
        start=a.X() if along_u else a.Y();end=b.X() if along_u else b.Y()
        if abs(end-start)<1e-12:
            raise ValueError('Degenerate original native PCURVE')
        maxerr=0.0;samples=0
        for ridx,side,_,_,_,_ in boundary_rows[eid]:
            row=additions[ridx];ua,ub,za,zb=row['native_uv_rectangle']
            ctrl=[points[i] for i in row['control_vertex_ids']]
            for k in range(9):
                t=k/8
                target=(ua+(ub-ua)*t) if along_u else (za+(zb-za)*t)
                if target<min(start,end)-SOURCE_UV_TOL or target>max(start,end)+SOURCE_UV_TOL:
                    raise ValueError('Sampled BP boundary outside native original edge range')
                A,B=lo,hi
                for _ in range(48):
                    mid=.5*(A+B);val=c2.Value(mid)
                    at=val.X() if along_u else val.Y()
                    if (at<target)==(start<end):A=mid
                    else:B=mid
                native=c3.Value(.5*(A+B))
                actual=tuple(native.Coord())
                if side=='bottom':guess=surface(ctrl,t,0)
                elif side=='top':guess=surface(ctrl,t,1)
                elif side=='left':guess=surface(ctrl,0,t)
                elif side=='right':guess=surface(ctrl,1,t)
                else:raise ValueError('Unknown boundary side')
                maxerr=max(maxerr,math.dist(actual,guess));samples+=1
        if not samples or maxerr>budget:
            raise ValueError(f'Native edge #{eid} does not fit original source budget')
        output.append({'original_edge_curve_id':eid,
                       'native_topods_edge_index':original_edges[eid]['native_index'],
                       'curve_type':orig['curve_type_3d'],
                       'boundary_piece_count':len(boundary_rows[eid]),
                       'boundary_sample_count':samples,
                       'max_sampled_3d_edge_distance_mm':maxerr,
                       'native_incident_face_indices':original_edges[eid]['incident']})
    return output


def audit_original(source,native,baseline_bp,baseline_manifest,bp,manifest,*,declared_budget_mm=BUDGET_MM):
    if declared_budget_mm!=BUDGET_MM or manifest.get('pilot_budget_mm')!=declared_budget_mm:
        raise ValueError('Pilot budget changes are prohibited')
    part=source_partition(source)
    if manifest.get('face_id')!=FACE or manifest.get('source_sha256')!=part['source_sha256']:
        raise ValueError('Source STEP identity mismatch')
    if sha256(bp.encode('utf-8')).hexdigest()!=manifest.get('combined_bp_sha256'):
        raise ValueError('BP checksum mismatch')
    if sha256(baseline_bp.encode('utf-8')).hexdigest()!=manifest.get('baseline_bp_sha256'):
        raise ValueError('Baseline BP checksum mismatch')
    if sha256(json.dumps(baseline_manifest,sort_keys=True).encode()).hexdigest()!=manifest.get('baseline_manifest_sha256'):
        raise ValueError('Baseline manifest mismatch')
    expected_bp,expected_manifest=build_extension(source,baseline_bp,baseline_manifest,
                      left_sectors=manifest['left_sectors'],right_sectors=manifest['right_sectors'],
                      declared_budget_mm=declared_budget_mm)
    if bp!=expected_bp or manifest!=expected_manifest:
        raise ValueError('Recomputed source-BP/manifest mismatch')
    native_report=inventory(source,native)
    native_index=next(r['native_face_index'] for r in native_report['faces'] if r['source_advanced_face_id']==FACE)
    other_index=next(r['native_face_index'] for r in native_report['faces'] if r['source_advanced_face_id']==BASELINE_FACE)
    if native_index!=22 or other_index!=12:
        raise ValueError('Source/native S40 face correspondence changed')
    f=native.Faces()[native_index];other=native.Faces()[other_index]
    if abs(f.Area()-other.Area())>1e-5:
        raise ValueError('Complementary cylinder half-face trimmed areas disagree')
    if math.dist(tuple(f.Center().toTuple()),tuple(other.Center().toTuple()))<1:
        raise ValueError('Complementary faces geometrically coincide')
    if max(abs(a-b) for a,b in zip(BRepTools.UVBounds_s(f.wrapped),
                                  (part['u_breaks'][0],part['u_breaks'][-1],part['v_breaks'][0],part['v_breaks'][-1])))>SOURCE_UV_TOL:
        raise ValueError('Native source #2457 trimmed UV box changed')
    t=parse_entities(source)
    source_map=_native_boundary_map(part,t,native,native_index)
    boundary_rows,num_sides=_boundary_pieces(part,manifest['added_patches'])
    points,patches=read_bp(bp)
    if len(patches)-59!=manifest['added_patch_count']:
        raise ValueError('Unexpected original patch count')
    stats=Counter();maxradial=0.0;maxproject=0.0
    for added in manifest['added_patches']:
        ua,ub,za,zb=added['native_uv_rectangle']
        geom={'face_id':FACE,'frame':part['frame'],'zmin':za,'zmax':zb,
              'start_u':ua,'signed_sweep_rad':ub-ua}
        interval=certify_patch(points,added['control_vertex_ids'],geom,0,1)
        if interval['radial_support_error_upper_mm']>declared_budget_mm:
            raise ValueError('Bernstein radial enclosure exceeds fixed source budget')
        maxradial=max(maxradial,interval['radial_support_error_upper_mm'])
        sampled=classify_patch(f,points,added['control_vertex_ids'],distance_budget_mm=declared_budget_mm)
        maxproject=max(maxproject,sampled['max_native_cylinder_projection_distance_mm'])
        stats.update(sampled['classification_histogram'])
    original_edges=_native_edge_distance(part,points,manifest['added_patches'],source_map,boundary_rows,f,declared_budget_mm)
    for eid in EXISTING_SEAMS:
        for row in range(4):
            key=_linear_source_edge(t,part,eid,row)[0]
            if baseline_manifest['original_global_source_key_to_control_index'].get(key)!=manifest['original_global_source_key_to_control_index'].get(key):
                raise ValueError('Cross-cylinder canonical source seam modified')
    return {'schema':'apmesh-s3p-s40-original-2457-complement-native-audit-v1',
            'source_sha256':part['source_sha256'],'source_face_id':FACE,
            'native_face_index':native_index,'neighbor_native_face_index':other_index,
            'source_x_axes_dot':part['source_opposite_reference_x_dot'],
            'native_centroid_separation_mm':math.dist(tuple(f.Center().toTuple()),tuple(other.Center().toTuple())),
            'source_uv_area':_area(part,manifest['left_sectors'],manifest['right_sectors']),
            'baseline_patch_count':59,'new_patches':len(manifest['added_patches']),
            'combined_patch_count':len(patches),'global_controls':len(points),
            'source_edge_count':len(EDGES),'source_boundary_side_pieces':num_sides,
            'source_native_boundary_rows':original_edges,
            'source_split_top_3d_bspline_edges':list(SPLINE_EDGES),
            'shared_source_original_generator_edges':list(EXISTING_SEAMS),
            'shared_original_indexed_control_references':8,
            'new_integer_internal_seams':manifest['internal_new_seams'],
            'native_interior_sample_count':len(manifest['added_patches'])*81,
            'native_boundary_sample_count':len(manifest['added_patches'])*44,
            'native_trim_histogram':dict(sorted(stats.items())),
            'max_guarded_radial_support_error_mm':maxradial,
            'max_native_cylinder_sampled_projection_error_mm':maxproject,
            'max_original_native_boundary_sampled_distance_mm':max(x['max_sampled_3d_edge_distance_mm'] for x in original_edges),
            'fixed_pilot_budget_mm':declared_budget_mm,
            'complete_original_s40_atlas':False,'full_continuous_hausdorff_certificate':False,
            'accepted_apmesh_tri_quad':'NOT_RUN'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-step',type=Path,required=True)
    ap.add_argument('--baseline-bp',type=Path,required=True)
    ap.add_argument('--baseline-manifest',type=Path,required=True)
    ap.add_argument('--left-sectors',type=int,default=2)
    ap.add_argument('--right-sectors',type=int,default=6)
    ap.add_argument('--budget-mm',type=float,default=BUDGET_MM)
    ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args()
    if sha256(args.source_step.read_bytes()).hexdigest()!=SOURCES['S40'][1]:
        raise ValueError('Pinned source STEP bytes changed')
    source=args.source_step.read_text('utf-8')
    old=args.baseline_bp.read_text('utf-8')
    meta=json.loads(args.baseline_manifest.read_text('utf-8'))
    native=cq.importers.importStep(str(args.source_step)).val()
    bp,manifest=build_extension(source,old,meta,
              left_sectors=args.left_sectors,right_sectors=args.right_sectors,
              declared_budget_mm=args.budget_mm)
    receipt=audit_original(source,native,old,meta,bp,manifest,declared_budget_mm=args.budget_mm)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'s40_complement2457.partial.bp').write_text(bp,'utf-8')
    (args.output_dir/'s40_complement2457_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n','utf-8')
    (args.output_dir/'s40_complement2457_native_audit.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n','utf-8')
    print(json.dumps({'admission':'BOUNDED_ORIGINAL_PARTIAL_ATLAS',
            'added_patches':receipt['new_patches'],'total_patches':receipt['combined_patch_count'],
            'max_native_edge_distance_mm':receipt['max_original_native_boundary_sampled_distance_mm']}))


if __name__=='__main__':
    main()
