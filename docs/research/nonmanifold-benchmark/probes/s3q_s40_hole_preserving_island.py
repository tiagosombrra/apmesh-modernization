#!/usr/bin/env python3
"""S3.Q: preserve the original S40 #218 inner wire in an isolated BP candidate.

This pilot intentionally does NOT join the existing S3.P 77-patch atlas.
The original long generator edges in that atlas require explicit subdivision
before global indexed conformity can be demonstrated.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import re

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Curve2d
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.BRepTools import BRepTools
from OCP.TopAbs import TopAbs_OUT, TopAbs_IN
from OCP.gp import gp_Pnt2d

from audit_analytic_bp import read_bp, surface
from s3c_step_source_gate import SOURCES, COORDINATES, coordinates, entity, oriented_edges, parse_entities, refs
from s3g_cylindrical_source_constraints import _axis_support, _point
from s3i_joint_source_atlas import _serialize
from s3j_radial_support_enclosure import certify_patch
from s3k_native_uv_trim_gate import classify_patch
from s3n_s40_orthogonal_trim import _add, _cross, _dot, _norm, _scale, _sub, _uv_point
from s3m_s40_complex_trim_inventory import inventory

FACE_ID = 218
SOURCE_SUPPORT = 45
RADIUS = 25.0
EXTERIOR = (222, 252, 281, 21, 303, 326, 355, 378)
INTERIOR = (411, 440, 473, 500)
SPLINES = (411, 500)
PREEXISTING_GENERATORS = (222, 281, 303, 355)
SEGMENTS = (1, 2, 5, 2, 1)
BUDGET_MM = 0.001
SOURCE_UV_TOL = 1e-8


def _source_sha(source: str) -> str:
    digest = sha256(source.encode('utf-8')).hexdigest()
    if digest != SOURCES['S40'][1]:
        raise ValueError('S3.Q requires the pinned unmodified original S40 source')
    return digest


def _frame(table):
    sid, origin, axis, radius = _axis_support(table, FACE_ID)
    if sid != SOURCE_SUPPORT or abs(radius-RADIUS)>1e-9:
        raise ValueError('Original S40 #218 cylinder support changed')
    _,body=entity(table,sid,'CYLINDRICAL_SURFACE')
    _,place=entity(table,refs(body)[0],'AXIS2_PLACEMENT_3D')
    x=_point(table,refs(place)[2],expected='DIRECTION')
    x=_scale(x,1/_norm(x))
    y=_cross(axis,x)
    if abs(_dot(x,axis))>1e-10 or abs(_norm(y)-1)>1e-10:
        raise ValueError('Nonorthonormal original cylinder frame')
    return {'id':sid,'origin':origin,'axis':axis,'x':x,'y':y,'radius':radius}


def _uv(frame, xyz):
    d=_sub(xyz,frame['origin'])
    angle=math.atan2(_dot(d,frame['y']),_dot(d,frame['x']))%(2*math.pi)
    if angle < math.pi/2:
        angle += 2*math.pi
    return (angle, _dot(d,frame['axis']))


def _pcurve(table, edge_id, support_id):
    _,body=entity(table,edge_id,'EDGE_CURVE')
    _,wrapped=entity(table,refs(body)[2])
    matches=[]
    for pid in refs(wrapped)[1:]:
        kind,raw=entity(table,pid)
        if kind!='PCURVE' or refs(raw)[0]!=support_id:
            continue
        _,r=entity(table,refs(raw)[1],'DEFINITIONAL_REPRESENTATION')
        cid=refs(r)[0]
        kind,raw=entity(table,cid)
        if kind=='LINE':
            center_id,vec_id=refs(raw)
            _,center=entity(table,center_id,'CARTESIAN_POINT')
            _,vraw=entity(table,vec_id,'VECTOR')
            _,direction=entity(table,refs(vraw)[0],'DIRECTION')
            q=tuple(map(float,COORDINATES.search(center)[1].split(',')))
            d=tuple(map(float,COORDINATES.search(direction)[1].split(',')))
            if len(q)!=2 or len(d)!=2:
                raise ValueError('Malformed original 2D PCURVE')
            if abs(d[0])<1e-10 and abs(d[1])>.9: axis='U'; fixed=q[0]
            elif abs(d[1])<1e-10 and abs(d[0])>.9: axis='V'; fixed=q[1]
            else: raise ValueError('Original PCURVE is not axis-aligned')
            controls=[q]; degree=1
        elif kind=='B_SPLINE_CURVE_WITH_KNOTS':
            degree=int(re.match(r"\s*''\s*,\s*(\d+)\s*,",raw)[1])
            if degree!=2:
                raise ValueError('Only the pinned quadratic inner PCURVE is supported')
            controls=[]
            for idx in refs(raw):
                kind2, p=entity(table,idx)
                if kind2=='CARTESIAN_POINT':
                    point=tuple(map(float,COORDINATES.search(p)[1].split(',')))
                    if len(point)!=2: raise ValueError('Invalid 2D spline control')
                    controls.append(point)
            if len(controls)!=3:raise ValueError('Unexpected quadratic inner PCURVE control count')
            us=[p[0] for p in controls];vs=[p[1] for p in controls]
            if max(us)-min(us)<SOURCE_UV_TOL and max(vs)-min(vs)>1:
                axis='U';fixed=us[0];along=vs
            elif max(vs)-min(vs)<SOURCE_UV_TOL and max(us)-min(us)>1:
                axis='V';fixed=vs[0];along=us
            else:raise ValueError('Quadratic inner PCURVE is not source-orthogonal')
            if not (all(a<=b+1e-12 for a,b in zip(along,along[1:])) or
                    all(a>=b-1e-12 for a,b in zip(along,along[1:]))):
                raise ValueError('Nonmonotone quadratic source boundary')
        else:
            raise ValueError('Unexpected original PCURVE type')
        matches.append({'pcurve_id':pid,'curve_id':cid,'kind':kind,'degree':degree,
                        'fixed_axis':axis,'fixed_value':fixed,'controls':controls})
    if len(matches)!=1:
        raise ValueError('Missing or ambiguous original native-cylinder PCURVE')
    return matches[0]


def source_partition(source):
    digest=_source_sha(source)
    table=parse_entities(source)
    support,wires=oriented_edges(table,FACE_ID)
    if support!='CYLINDRICAL_SURFACE' or len(wires)!=2 or tuple(len(w) for w in wires)!=(8,4):
        raise ValueError('Original #218 hole-bearing topology changed')
    if tuple(x['edge_curve_id'] for x in wires[0])!=EXTERIOR or tuple(x['edge_curve_id'] for x in wires[1])!=INTERIOR:
        raise ValueError('Original #218 source edge loop identities changed')
    frame=_frame(table)
    rows=[];vertices={};loops=[]
    for wi,wire in enumerate(wires):
        corners=[]
        for edge in wire:
            eid=edge['edge_curve_id']; info=_pcurve(table,eid,frame['id'])
            expected='B_SPLINE_CURVE_WITH_KNOTS' if eid in SPLINES else 'CIRCLE' if eid in (252,21,326,378,440) else 'LINE'
            if edge['master_3d_curve']!=expected:
                raise ValueError(f'Unexpected original 3D curve kind #{eid}')
            if eid in SPLINES and info['kind']!='B_SPLINE_CURVE_WITH_KNOTS':
                raise ValueError('Original hole spline PCURVE has changed')
            if eid not in SPLINES and info['kind']!='LINE':
                raise ValueError('Unexpected original non-spline PCURVE')
            ids=[edge['start_vertex_id'],edge['end_vertex_id']]
            uv=[_uv(frame,coordinates(table,i)) for i in ids]
            along_index=0 if info['fixed_axis']=='U' else 1
            for i,param in zip(ids,uv):
                if abs(param[along_index]-info['fixed_value'])>SOURCE_UV_TOL:
                    raise ValueError('Original PCURVE and 3D endpoint mismatch')
                if i in vertices and math.dist(vertices[i]['uv'],param)>SOURCE_UV_TOL:
                    raise ValueError('Inconsistent STEP vertex identity')
                vertices[i]={'uv':param,'xyz':coordinates(table,i)}
            corners.append(uv[0])
            rows.append({'edge_id':eid,'wire':'HOLE' if wi else 'EXTERIOR',
                         'original_3d_curve_kind':expected,
                         'start_vertex_id':ids[0],'end_vertex_id':ids[1],
                         'endpoint_uv':uv,**info})
        loops.append(corners)
    e={r['edge_id']:r for r in rows}
    outer_u=[e[k]['fixed_value'] for k in (222,281,303,355)]
    hole_u=[e[411]['fixed_value'],e[473]['fixed_value']]
    outer_z=[e[k]['fixed_value'] for k in (21,252,378)]
    hole_z=[e[500]['fixed_value'],e[440]['fixed_value']]
    u=[outer_u[0],outer_u[1],hole_u[0],hole_u[1],outer_u[2],outer_u[3]]
    z=[outer_z[0],hole_z[0],outer_z[1],hole_z[1],outer_z[2]]
    if not all(a<b for a,b in zip(u,u[1:])) or not all(a<b for a,b in zip(z,z[1:])):
        raise ValueError('Source hole UV rectangle ordering changed')
    if abs(u[0]-math.pi)>1e-8 or abs(u[-1]-2*math.pi)>1e-8:
        raise ValueError('Unexpected source cylinder angular interval')
    if len(vertices)!=12:
        raise ValueError('Original #218 must retain twelve distinct STEP vertices')
    for wi,corners in enumerate(loops):
        if len(corners)!=(8 if wi==0 else 4):
            raise ValueError('Source loop length changed')
    return {'schema':'apmesh-s3q-original-218-source-with-inner-loop-v1',
            'source_sha256':digest,'face_id':FACE_ID,'frame':frame,
            'source_edges':rows,'original_vertices':vertices,
            'breakpoints_u':u,'breakpoints_v':z,
            'source_wires_uv':loops,'hole_present':True}


def grid(part,sectors=SEGMENTS):
    if tuple(sectors)!=SEGMENTS:
        raise ValueError('This pilot requires the predeclared sectors (1,2,5,2,1)')
    breaks=part['breakpoints_u']
    U=[breaks[0]]
    for k,n in enumerate(sectors):
        for i in range(1,n+1):
            U.append(breaks[k]+(breaks[k+1]-breaks[k])*i/n)
    return U


def cells(part):
    U=grid(part); V=part['breakpoints_v']
    indices=[1,3,8,10]
    # Six vertical bands are selected by the outer shell minus the actual hole.
    rects=[]
    for j in range(4):
        for i in range(len(U)-1):
            keep=(j==0 and 1<=i<10 or j==1 and (1<=i<3 or 8<=i<10)
                  or j==2 and (i<3 or i>=8) or j==3)
            if keep:
                rects.append((i,j,U[i],U[i+1],V[j],V[j+1]))
    if len(rects)!=30:
        raise ValueError('Original hole decomposition did not yield 30 source rectangles')
    return rects


def _shoelace(polygon):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1])))/2


def verify_uv_partition(part, rects=None):
    rects=cells(part) if rects is None else rects
    outer_area=_shoelace(part['source_wires_uv'][0]); hole_area=_shoelace(part['source_wires_uv'][1])
    area=sum((c[3]-c[2])*(c[5]-c[4]) for c in rects)
    if abs((outer_area-hole_area)-area)>1e-7:
        raise ValueError('The original hole was filled or source outer area lost')
    for k,a in enumerate(rects):
        for b in rects[k+1:]:
            overlap=max(0,min(a[3],b[3])-max(a[2],b[2]))*max(0,min(a[5],b[5])-max(a[4],b[4]))
            if overlap>1e-10:
                raise ValueError('Overlapping source-hole rectangles')
    u=part['breakpoints_u'];z=part['breakpoints_v']
    hole_test=((u[2]+u[3])/2,(z[1]+z[3])/2)
    if any(a<=hole_test[0]<=b and c<=hole_test[1]<=d for _,_,a,b,c,d in rects):
        raise ValueError('Internal hole center was filled')
    return {'original_outer_parametric_area':outer_area,'original_inner_hole_parametric_area':hole_area,
            'expected_source_parametric_area':outer_area-hole_area,
            'partition_parametric_area':area,'interior_count':len(rects),
            'interior_hole_center_uv':list(hole_test),'hole_not_filled':True}


def _point_at(f,u,v):
    return _uv_point(f,u,v)


def build_island(source, *, sectors=SEGMENTS, declared_budget_mm=BUDGET_MM):
    if declared_budget_mm!=BUDGET_MM:
        raise ValueError('Pilot budget cannot be changed')
    part=source_partition(source)
    U=grid(part,sectors);V=part['breakpoints_v']; regions=cells(part)
    area=verify_uv_partition(part,regions)
    vertices=[];registry={};patches=[];descriptors=[]
    def intern(key, p):
        if key in registry:
            i=registry[key]
            if math.dist(vertices[i],p)>1e-8:raise ValueError('Inconsistent indexed control on shared seam')
            return i
        idx=len(vertices);registry[key]=idx;vertices.append(tuple(p));return idx
    f=part['frame']
    for idx,(i,j,ua,ub,za,zb) in enumerate(regions):
        span=ub-ua
        if not 0<span<=math.pi/2:raise ValueError('Original source angular piece too large')
        patch=[]
        for row in range(4):
            axial=za+(zb-za)*row/3
            for col in range(4):
                P0=_point_at(f,ua,axial); P3=_point_at(f,ub,axial)
                tangent0=_scale(_add(_scale(f['x'],-math.sin(ua)),_scale(f['y'],math.cos(ua))),f['radius']*span/3)
                tangent1=_scale(_add(_scale(f['x'],-math.sin(ub)),_scale(f['y'],math.cos(ub))),f['radius']*span/3)
                P=(P0,_add(P0,tangent0),_sub(P3,tangent1),P3)[col]
                if col in (0,3) and row in (0,3): key=f's3q_node:{FACE_ID}:{i+(col==3)}:{j+(row==3)}'
                elif col in (0,3):key=f's3q_vline:{FACE_ID}:{i+(col==3)}:{j}:{row}'
                elif row in (0,3):key=f's3q_hline:{FACE_ID}:{i}:{j+(row==3)}:{col}'
                else:key=f's3q_interior:{FACE_ID}:{i}:{j}:{row}:{col}'
                patch.append(intern(key,P))
        patches.append(tuple(patch))
        descriptors.append({'source_face_id':FACE_ID,'source_uv_rectangle':[ua,ub,za,zb],
                            'grid_u_index':i,'grid_v_index':j,'control_indices':patch})
    incidence=Counter()
    for patch in patches:
        for side in (patch[:4],patch[-4:],patch[::4],patch[3::4]):
            incidence[tuple(sorted(side))]+=1
    if set(incidence.values())!={1,2}:
        raise ValueError('Invalid BP indexed side adjacency')
    bp=_serialize(vertices,patches)
    manifest={'schema':'apmesh-s3q-original-s40-218-isolated-hole-bp-v1',
              'source_sha256':part['source_sha256'],'source_model':'S40',
              'original_face_id':FACE_ID,'pilot_budget_mm':declared_budget_mm,
              'original_outer_edge_ids':list(EXTERIOR),'original_inner_edge_ids':list(INTERIOR),
              'original_hole_preserved':True,'source_uv_breakpoints':{'u':part['breakpoints_u'],'v':V},
              'source_uv_area_audit':area,'added_patches':descriptors,
              'island_patch_count':len(patches),'island_control_count':len(vertices),
              'island_internal_indexed_seam_count':sum(x==2 for x in incidence.values()),
              'source_indexed_control_keys':registry,'island_bp_sha256':sha256(bp.encode()).hexdigest(),
              'joint_77_patch_atlas':'BLOCKED_BY_PREEXISTING_EDGE_SUBDIVISION',
              'preexisting_generator_edges_requiring_conforming_split':list(PREEXISTING_GENERATORS),
              'original_s40_face_coverage_prior':16,'apmesh_tri_quad':'NOT_RUN'}
    return bp,manifest


def _boundary_sides(part, additions):
    rows=[]
    for k,row in enumerate(additions):
        u0,u1,v0,v1=row['source_uv_rectangle']
        rows.extend([(k,'bottom','V',v0,u0,u1), (k,'top','V',v1,u0,u1),
                     (k,'left','U',u0,v0,v1),(k,'right','U',u1,v0,v1)])
    ident=lambda e:(e[2],)+tuple(round(x,8) for x in e[3:])
    count=Counter(ident(e) for e in rows)
    if not set(count.values()).issubset({1,2}):
        raise ValueError('Non-manifold seam in isolated BP')
    frontier=[e for e in rows if count[ident(e)]==1]
    original={};used=[]
    for ed in part['source_edges']:
        axis=ed['fixed_axis'];fixed=ed['fixed_value']
        varying=1 if axis=='U' else 0
        a,b=sorted((ed['endpoint_uv'][0][varying],ed['endpoint_uv'][1][varying]))
        matched=[e for e in frontier if e[2]==axis and abs(e[3]-fixed)<SOURCE_UV_TOL
                 and e[4]>=a-SOURCE_UV_TOL and e[5]<=b+SOURCE_UV_TOL]
        matched.sort(key=lambda x:x[4]);segments=[(e[4],e[5]) for e in matched]
        if not segments or abs(segments[0][0]-a)>SOURCE_UV_TOL or abs(segments[-1][1]-b)>SOURCE_UV_TOL:
            raise ValueError(f'Original #{ed["edge_id"]} boundary is incomplete')
        if any(abs(segments[i][1]-segments[i+1][0])>SOURCE_UV_TOL for i in range(len(segments)-1)):
            raise ValueError(f'Original #{ed["edge_id"]} has a gap')
        original[ed['edge_id']]=matched
        used.extend(matched)
    if len(used)!=len(frontier) or len(set(used))!=len(frontier):
        raise ValueError('Outer/inner original frontier not in bijection with candidate BP')
    return original,frontier


def _native_edges(part,shape,native_index):
    face=shape.Faces()[native_index]
    if face.geomType()!='CYLINDER' or len(face.Wires())!=2 or len(face.Edges())!=12:
        raise ValueError('Original #218 native face with inner wire unavailable')
    outer=BRepTools.OuterWire_s(face.wrapped)
    if sum(w.wrapped.IsSame(outer) for w in face.Wires())!=1:
        raise ValueError('Original native outer wire not unique')
    edges=shape.Edges();matches={};tolerance=max(1e-8,shape.BoundingBox().DiagonalLength*1e-9)
    for row in part['source_edges']:
        eid=row['edge_id']
        src=[part['original_vertices'][row[k]]['xyz'] for k in ('start_vertex_id','end_vertex_id')]
        expected='BSPLINE' if eid in SPLINES else row['original_3d_curve_kind']
        candidates=[]
        for edge in face.Edges():
            if edge.geomType()!=expected or len(edge.Vertices())!=2:continue
            v=[tuple(x.Center().toTuple()) for x in edge.Vertices()]
            gap=min(max(math.dist(v[k],src[k^flip]) for k in (0,1)) for flip in (0,1))
            if gap<tolerance:
                idx=[i for i,c in enumerate(edges) if edge.wrapped.IsSame(c.wrapped)]
                if len(idx)!=1:raise ValueError('Unresolved native edge index')
                candidates.append((idx[0],edge,gap))
        if len(candidates)!=1:raise ValueError(f'Original #{eid} has ambiguous native edge')
        ni,edge,gap=candidates[0]
        incid=[i for i,f in enumerate(shape.Faces()) if any(edge.wrapped.IsSame(e.wrapped) for e in f.Edges())]
        if len(incid)!=2 or native_index not in incid:
            raise ValueError('Original edge is not two-sided on manifold control')
        matches[eid]={'edge':edge,'native_idx':ni,'gap':gap,'incident':incid}
    if len({r['native_idx'] for r in matches.values()})!=12:
        raise ValueError('Duplicate source-to-native edge correspondence')
    return matches


def _boundary_distance(part,verts,patches,native_edges,boundaries,native_face,budget):
    stats=[]
    for row in part['source_edges']:
        eid=row['edge_id'];edge=native_edges[eid]['edge']
        c2=BRepAdaptor_Curve2d(edge.wrapped,native_face.wrapped)
        c3=BRepAdaptor_Curve(edge.wrapped)
        start,end=c2.FirstParameter(),c2.LastParameter()
        xidx=1 if row['fixed_axis']=='U' else 0
        xstart=c2.Value(start).Y() if xidx==1 else c2.Value(start).X()
        xend=c2.Value(end).Y() if xidx==1 else c2.Value(end).X()
        if abs(xend-xstart)<1e-11:raise ValueError('Native source edge PCURVE is degenerate')
        samples=0; maxerr=0
        for k,side,_,_,lo,hi in boundaries[eid]:
            controls=[verts[t] for t in patches[k]]
            for it in range(9):
                frac=it/8
                target=lo+(hi-lo)*frac
                if not min(xstart,xend)-SOURCE_UV_TOL<=target<=max(xstart,xend)+SOURCE_UV_TOL:
                    raise ValueError('Candidate boundary exceeds original native edge parameter')
                a,b=start,end
                for _ in range(42):
                    mid=(a+b)/2
                    v=c2.Value(mid)
                    m=v.Y() if xidx==1 else v.X()
                    if (m<target)==(xstart<xend):a=mid
                    else:b=mid
                P=c3.Value((a+b)/2)
                original=tuple(P.Coord())
                if side=='bottom':q=surface(controls,frac,0)
                elif side=='top':q=surface(controls,frac,1)
                elif side=='left':q=surface(controls,0,frac)
                else:q=surface(controls,1,frac)
                gap=math.dist(original,q);maxerr=max(maxerr,gap);samples+=1
        if not samples or maxerr>budget:
            raise ValueError(f'Original native edge #{eid} exceeds pilot boundary budget ({maxerr})')
        stats.append({'source_edge_id':eid,'wire':row['wire'],
                      'native_edge_index':native_edges[eid]['native_idx'],
                      'native_incident_face_indices':native_edges[eid]['incident'],
                      'original_3d_curve_kind':row['original_3d_curve_kind'],
                      'bp_boundary_piece_count':len(boundaries[eid]),
                      'native_boundary_sample_count':samples,
                      'max_sampled_native_3d_edge_distance_mm':maxerr})
    return stats


def audit_original(source,native,bp,manifest,*,budget_mm=BUDGET_MM):
    if budget_mm!=BUDGET_MM or manifest.get('pilot_budget_mm')!=budget_mm:
        raise ValueError('Changed original budget')
    part=source_partition(source)
    if manifest.get('source_sha256')!=part['source_sha256'] or manifest.get('original_face_id')!=FACE_ID:
        raise ValueError('Original source identity mismatch')
    if sha256(bp.encode()).hexdigest()!=manifest.get('island_bp_sha256'):
        raise ValueError('Altered isolated BP')
    regenerated,expected=build_island(source,declared_budget_mm=budget_mm)
    if regenerated!=bp or expected!=manifest:
        raise ValueError('Forged manifest or original control registry')
    report=inventory(source,native)
    native_index=next(x['native_face_index'] for x in report['faces'] if x['source_advanced_face_id']==FACE_ID)
    if native_index!=1:raise ValueError('Unexpected original #218 native face identity')
    native_face=native.Faces()[native_index]
    vertices,patches=read_bp(bp)
    if len(patches)!=30 or len(vertices)!=manifest['island_control_count']:
        raise ValueError('BP patch inventory mismatch')
    boundaries,frontier=_boundary_sides(part,manifest['added_patches'])
    native_edges=_native_edges(part,native,native_index)
    edge_stats=_boundary_distance(part,vertices,patches,native_edges,boundaries,native_face,budget_mm)
    cylinder=[];max_radial=0;max_projection=0;totals=Counter()
    for k,row in enumerate(manifest['added_patches']):
        u0,u1,z0,z1=row['source_uv_rectangle']
        geom={'frame':part['frame'],'face_id':FACE_ID,'zmin':z0,'zmax':z1,'start_u':u0,'signed_sweep_rad':u1-u0}
        certificate=certify_patch(vertices,patches[k],geom,0,1)
        if certificate['radial_support_error_upper_mm']>budget_mm:
            raise ValueError('S3.Q cylinder radial support exceeds pilot budget')
        native_result=classify_patch(native_face,vertices,patches[k],
                      distance_budget_mm=budget_mm,interior_grid=9,boundary_grid=11)
        totals.update(native_result['classification_histogram'])
        max_projection=max(max_projection,native_result['max_native_cylinder_projection_distance_mm'])
        max_radial=max(max_radial,certificate['radial_support_error_upper_mm'])
        cylinder.append({'source_face_id':FACE_ID,'patch_id':k,
                         'source_uv_rectangle':row['source_uv_rectangle'],
                         'radial_upper_mm':certificate['radial_support_error_upper_mm'],
                         'sampled_native_projection_mm':native_result['max_native_cylinder_projection_distance_mm']})
    # A representative set of hole samples must all be OUT in the native face.
    u=part['breakpoints_u'];v=part['breakpoints_v']
    hole_states=[]
    for i in range(1,8):
        for j in range(1,8):
            x=u[2]+(u[3]-u[2])*i/8
            y=v[1]+(v[3]-v[1])*j/8
            state=BRepClass_FaceClassifier(native_face.wrapped,gp_Pnt2d(x,y),1e-7).State()
            if state!=TopAbs_OUT:raise ValueError('Original native hole was filled')
            hole_states.append('OUT')
    result={'schema':'apmesh-s3q-s40-original-hole-native-island-audit-v1',
            'source_sha256':part['source_sha256'],'native_face_index':native_index,
            'source_advanced_face_id':FACE_ID,'source_support_radius_mm':RADIUS,
            'original_inner_wire_preserved':True,'original_outer_edge_count':8,
            'original_inner_edge_count':4,'original_source_native_edge_mappings':edge_stats,
            'island_bp_sha256':manifest['island_bp_sha256'],'island_patch_count':30,
            'island_controls':len(vertices),'island_internal_seams':manifest['island_internal_indexed_seam_count'],
            'native_hole_OUT_samples':len(hole_states),'native_patch_classification_histogram':dict(totals),
            'maximum_guarded_bernstein_radial_bound_mm':max_radial,
            'maximum_sampled_native_cylinder_projection_distance_mm':max_projection,
            'maximum_sampled_native_trimmed_edge_distance_mm':max(r['max_sampled_native_3d_edge_distance_mm'] for r in edge_stats),
            'pilot_budget_mm':budget_mm,
            'combined_original_atlas':False,
            'blocked_integration':'FOUR_PREEXISTING_SOURCE_EDGES_REQUIRE_CONFORMING_SUBDIVISION',
            'blocked_edge_ids':list(PREEXISTING_GENERATORS),
            'native_uv_audit_scope':'DISCRETE_ONLY_NOT_CONTINUOUS_TRIM_CERTIFICATION',
            'apmesh_tri_quad_mesh':'NOT_RUN'}
    return result



def audit_nonconforming_join(source, island_manifest, baseline_bp, baseline_manifest):
    """Prove that four original generator edges require a source-aware split.

    This does not combine the meshes or weld controls by coordinate proximity.
    An original one-piece cubic cannot be joined conformingly to the proposed
    two-piece boundary without retopologizing its already admitted neighbor.
    """
    part = source_partition(source)
    if baseline_manifest.get('source_model')!='S40' or baseline_manifest.get('source_sha256')!=part['source_sha256']:
        raise ValueError('Prior atlas source does not match the pinned original')
    if (baseline_manifest.get('combined_patch_count')!=77 or
            baseline_manifest.get('combined_control_count')!=864):
        raise ValueError('Missing S3.P 77-patch immutable prior atlas')
    if sha256(baseline_bp.encode()).hexdigest()!=baseline_manifest.get('combined_bp_sha256'):
        raise ValueError('Prior source-indexed BP has changed')
    if island_manifest.get('original_face_id')!=FACE_ID:
        raise ValueError('Wrong isolated candidate for the original join')
    pts,patches=read_bp(baseline_bp)
    if len(patches)!=77 or len(pts)!=864:
        raise ValueError('Prior indexed BP count has changed')
    registry=baseline_manifest['original_global_source_key_to_control_index']
    boundaries,_=_boundary_sides(part,island_manifest['added_patches'])
    original={r['edge_id']:r for r in part['source_edges']}
    records=[]
    for eid in PREEXISTING_GENERATORS:
        edge=original[eid]
        keys=[f'vertex:{edge["start_vertex_id"]}',f'edge:{eid}:1',
              f'edge:{eid}:2',f'vertex:{edge["end_vertex_id"]}']
        indices=[registry.get(key) for key in keys]
        if any(n is None for n in indices) or len(set(indices))!=4:
            raise ValueError(f'Prior generator #{eid} lost original canonical controls')
        current=boundaries[eid]
        if len(current)!=2:
            raise ValueError(f'Original #{eid} does not require the expected two-piece split')
        records.append({'source_edge_curve_id':eid,'prior_full_edge_control_ids':indices,
                        'prior_generator_cubic_piece_count':1,
                        'new_island_boundary_piece_count':len(current),
                        'source_curves_are_conforming':False,
                        'required_action':'SPLIT_PREEXISTING_SOURCE_CUBIC_AND_REINDEX_BOTH_SIDES'})
    return {'source_model':'S40','prior_accepted_patch_count':77,
            'isolated_hole_patch_count':island_manifest['island_patch_count'],
            'blocked_original_interfaces':records,'combined_atlas_is_conforming':False,
            'combined_patch_count_not_admitted':77+island_manifest['island_patch_count']}


def source_spline_endpoint_deviation(part):
    """Measure original STEP vertices against the exact cylindrical support."""
    f=part['frame']
    records=[]
    for eid in SPLINES:
        row=next(r for r in part['source_edges'] if r['edge_id']==eid)
        for ident in (row['start_vertex_id'],row['end_vertex_id']):
            P=part['original_vertices'][ident]['xyz'];d=_sub(P,f['origin'])
            a=_dot(d,f['axis']);rad=_sub(d,_scale(f['axis'],a))
            records.append({'source_edge_id':eid,'vertex_id':ident,
                            'source_support_radial_endpoint_residual_mm':abs(_norm(rad)-f['radius'])})
    return records


def pilot_angular_bound(part, center_sectors):
    """Audit one analytic representative of the widest original hole wedge."""
    if not type(center_sectors)==int or not 1<=center_sectors<=12:
        raise ValueError('Invalid trial sector count')
    f=part['frame'];u0,u1=part['breakpoints_u'][2:4]
    lo,hi=part['breakpoints_v'][3:5]
    du=(u1-u0)/center_sectors
    P0=_point_at(f,u0,lo);P3=_point_at(f,u0+du,lo)
    T0=_scale(_add(_scale(f['x'],-math.sin(u0)),_scale(f['y'],math.cos(u0))),f['radius']*du/3)
    T1=_scale(_add(_scale(f['x'],-math.sin(u0+du)),_scale(f['y'],math.cos(u0+du))),f['radius']*du/3)
    p=[P0,_add(P0,T0),_sub(P3,T1),P3]
    controls=[]
    for k in range(4):
        controls.extend([_add(a,_scale(f['axis'],(hi-lo)*k/3)) for a in p])
    geom={'frame':f,'face_id':FACE_ID,'zmin':lo,'zmax':hi,
          'start_u':u0,'signed_sweep_rad':du}
    evidence=certify_patch(controls,list(range(16)),geom,0,1)
    return evidence['radial_support_error_upper_mm']

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--source-step',required=True)
    cli.add_argument('--output-dir',required=True)
    cli.add_argument('--budget-mm',type=float,default=BUDGET_MM)
    cli.add_argument('--baseline-bp')
    cli.add_argument('--baseline-manifest')
    args=cli.parse_args()
    path=Path(args.source_step)
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=SOURCES['S40'][1]:
        raise ValueError('Original S40 byte-level SHA-256 mismatch')
    src=raw.decode('utf-8')
    island,manifest=build_island(src,declared_budget_mm=args.budget_mm)
    native=cq.importers.importStep(str(path)).val()
    evidence=audit_original(src,native,island,manifest,budget_mm=args.budget_mm)
    evidence['source_spline_endpoint_support_residuals']=source_spline_endpoint_deviation(source_partition(src))
    evidence['central_angular_trial_upper_mm']={'4':pilot_angular_bound(source_partition(src),4),
                                                 '5':pilot_angular_bound(source_partition(src),5)}
    if bool(args.baseline_bp)!=bool(args.baseline_manifest):
        raise ValueError('Both previous BP and manifest must be supplied for the join blocker')
    if args.baseline_bp:
        prior=Path(args.baseline_bp).read_text('utf-8')
        prior_manifest=json.loads(Path(args.baseline_manifest).read_text('utf-8'))
        evidence['prior_atlas_join_check']=audit_nonconforming_join(src,manifest,prior,prior_manifest)
    folder=Path(args.output_dir)
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'s40_face218_hole.isolated.bp').write_text(island,encoding='utf-8')
    (folder/'s40_face218_hole_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    (folder/'s40_face218_hole_native_receipt.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in evidence.items() if k not in ('original_source_native_edge_mappings',)},indent=2))


if __name__=='__main__':
    main()
