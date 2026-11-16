#!/usr/bin/env python3
"""S3.O: Source-anchored S40 #1519 spline-trim cylinder research pilot.

The source PCURVE footprint is certified before approximating the native face.
No production meshing, complete shell, or non-manifold source is claimed.
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
from OCP.BRepTools import BRepTools

from audit_analytic_bp import read_bp, surface
from s3c_step_source_gate import SOURCES, COORDINATES, coordinates, entity, oriented_edges, parse_entities, refs
from s3g_cylindrical_source_constraints import _axis_support, _point
from s3i_joint_source_atlas import _serialize
from s3j_radial_support_enclosure import certify_patch
from s3k_native_uv_trim_gate import classify_patch
from s3m_s40_complex_trim_inventory import inventory
from s3n_s40_orthogonal_trim import _dot, _sub, _add, _scale, _cross, _norm, _linear_source_edge, _uv_point

FACE = 1519
EXPECTED_SOURCE_EDGES = (1523, 1548, 85, 1570, 1593, 1616, 1644, 1753)
ORIGINAL_BSPLINE_EDGES = (85, 1644)
SOURCE_AXIAL_EDGES = (1548, 1570, 1616, 1753)
PREEXISTING_SEAMS = (1548, 1570)
SOURCE_UV_TOL = 1e-8
CONTROL_TOL_MM = 1e-8
PILOT_BUDGET_MM = .001


def _digest(source: str) -> str:
    digest = sha256(source.encode('utf-8')).hexdigest()
    if digest != SOURCES['S40'][1]:
        raise ValueError('Pinned original S40 source SHA-256 mismatch')
    return digest


def _frame(table):
    sid, origin, axis, radius = _axis_support(table, FACE)
    _, raw = entity(table, sid, 'CYLINDRICAL_SURFACE')
    _, place = entity(table, refs(raw)[0], 'AXIS2_PLACEMENT_3D')
    frame_refs = refs(place)
    if len(frame_refs) != 3:
        raise ValueError('Source cylinder frame is missing its X direction')
    x = _point(table, frame_refs[2], expected='DIRECTION')
    x = _scale(x, 1 / _norm(x))
    y = _cross(axis, x)
    if abs(_dot(axis, x)) > 1e-10 or abs(_norm(y)-1) > 1e-10:
        raise ValueError('Nonorthogonal original cylinder frame')
    if abs(radius-16.) > 1e-8:
        raise ValueError('Unexpected original cylinder radius')
    return {'id':sid, 'origin':origin, 'axis':axis, 'x':x, 'y':y, 'radius':radius}


def _uv(frame, xyz):
    delta = _sub(xyz, frame['origin'])
    z = _dot(delta, frame['axis'])
    angle = math.atan2(_dot(delta, frame['y']), _dot(delta, frame['x'])) % (2*math.pi)
    # Preserve the unique source branch on the interval [pi, 2*pi].
    if angle < math.pi/2:
        angle += 2*math.pi
    return (angle, z)


def _pcurve(table, eid, sid):
    _, edge = entity(table, eid, 'EDGE_CURVE')
    _, wrapped = entity(table, refs(edge)[2])
    matches=[]
    for pid in refs(wrapped)[1:]:
        typ, raw = entity(table, pid)
        if typ != 'PCURVE' or refs(raw)[0] != sid:
            continue
        _, repr_raw = entity(table, refs(raw)[1], 'DEFINITIONAL_REPRESENTATION')
        cid = refs(repr_raw)[0]
        kind, curve = entity(table, cid)
        if kind == 'LINE':
            start_id, vector_id = refs(curve)
            _, p = entity(table, start_id, 'CARTESIAN_POINT')
            _, vector = entity(table, vector_id, 'VECTOR')
            _, d = entity(table, refs(vector)[0], 'DIRECTION')
            if not COORDINATES.search(p) or not COORDINATES.search(d):
                raise ValueError('Malformed original LINE PCURVE')
            q = tuple(map(float, COORDINATES.search(p)[1].split(',')))
            direction = tuple(map(float, COORDINATES.search(d)[1].split(',')))
            if len(q)!=2 or len(direction)!=2:
                raise ValueError('Invalid PCURVE dimension')
            if abs(direction[0]) <= 1e-10 and abs(direction[1]) > .9:
                result=('U', q[0], 'LINE', [q])
            elif abs(direction[1]) <= 1e-10 and abs(direction[0]) > .9:
                result=('V', q[1], 'LINE', [q])
            else:
                raise ValueError('Source curve is not an axial/azimuthal PCURVE')
        elif kind == 'B_SPLINE_CURVE_WITH_KNOTS':
            degree_match = re.match(r"\s*''\s*,\s*(\d+)\s*,", curve)
            if not degree_match:
                raise ValueError('Missing source B-spline PCURVE degree')
            degree = int(degree_match[1])
            points = []
            for cp_id in refs(curve):
                cp_type, cp_raw = entity(table, cp_id)
                if cp_type != 'CARTESIAN_POINT':
                    continue
                match = COORDINATES.search(cp_raw)
                if not match:
                    raise ValueError('Malformed spline PCURVE control')
                point = tuple(map(float, match[1].split(',')))
                if len(point)!=2:
                    raise ValueError('Non-2D B-spline PCURVE control')
                points.append(point)
            if degree not in (1,3) or len(points)<degree+1:
                raise ValueError('Unsupported spline degree/control count')
            us = [p[0] for p in points]
            vs = [p[1] for p in points]
            if max(vs)-min(vs) > SOURCE_UV_TOL:
                raise ValueError('Source spline PCURVE is not constant axial V')
            if not (all(x<=y+1e-12 for x,y in zip(us,us[1:])) or
                    all(x>=y-1e-12 for x,y in zip(us,us[1:]))):
                raise ValueError('Nonmonotone source spline angular parameters')
            if abs(us[-1]-us[0]) < 1e-6:
                raise ValueError('Degenerate original source spline')
            result=('V', vs[0], f'BSPLINE_DEGREE_{degree}', points)
        else:
            raise ValueError(f'Unsupported source cylinder PCURVE {kind}')
        matches.append((pid,cid,result))
    if len(matches)!=1:
        raise ValueError('Missing or ambiguous original cylinder PCURVE')
    return matches[0]


def source_partition(source):
    """Derive the orthogonal step strictly from the pinned original spline PCURVEs."""
    digest = _digest(source)
    table = parse_entities(source)
    support,wires = oriented_edges(table, FACE)
    if support!='CYLINDRICAL_SURFACE' or len(wires)!=1 or len(wires[0])!=8:
        raise ValueError('Original face #1519 wire topology changed')
    if tuple(e['edge_curve_id'] for e in wires[0]) != EXPECTED_SOURCE_EDGES:
        raise ValueError('Original #1519 source EDGE_CURVE order changed')
    frame = _frame(table)
    original_vertices={}
    records=[]
    for edge in wires[0]:
        eid=edge['edge_curve_id']
        pid,cid,(fixed_axis,fixed_value,kind,cps)=_pcurve(table,eid,frame['id'])
        original_kind=edge['master_3d_curve']
        if eid in ORIGINAL_BSPLINE_EDGES:
            if original_kind!='B_SPLINE_CURVE_WITH_KNOTS' or kind!='BSPLINE_DEGREE_3':
                raise ValueError('Original B-spline boundary/provenance changed')
        elif eid in SOURCE_AXIAL_EDGES:
            if original_kind!='LINE' or kind!='LINE' or fixed_axis!='U':
                raise ValueError('Original generator PCURVE orientation changed')
        elif original_kind!='CIRCLE' or kind!='BSPLINE_DEGREE_1':
            raise ValueError('Original STEP circular trace/degree changed')
        start=coordinates(table,edge['start_vertex_id'])
        end=coordinates(table,edge['end_vertex_id'])
        pair=[_uv(frame,start),_uv(frame,end)]
        for vertex_id,xyz,uv in zip((edge['start_vertex_id'],edge['end_vertex_id']),(start,end),pair):
            if fixed_axis=='U':
                if abs(uv[0]-fixed_value)>SOURCE_UV_TOL:
                    raise ValueError('Original generator endpoint U mismatches PCURVE')
            elif abs(uv[1]-fixed_value)>SOURCE_UV_TOL:
                raise ValueError('Original circular/spline endpoint V mismatches PCURVE')
            if vertex_id in original_vertices and math.dist(original_vertices[vertex_id]['xyz'],xyz)>1e-12:
                raise ValueError('Original topological vertex identity changed')
            original_vertices[vertex_id]={'xyz':xyz,'uv':uv}
        if fixed_axis=='V':
            u_endpoints=sorted((pair[0][0],pair[1][0]))
            cp_endpoints=sorted((cps[0][0],cps[-1][0]))
            if max(abs(x-y) for x,y in zip(u_endpoints,cp_endpoints))>SOURCE_UV_TOL:
                raise ValueError('Original PCURVE spline endpoints contradict 3D vertices')
        records.append({'edge_id':eid,'curve_type_3d':original_kind,
                        'cylinder_pcurve_id':pid,'cylinder_pcurve_curve_id':cid,
                        'pcurve_type':kind,'pcurve_control_count':len(cps),
                        'fixed_axis':fixed_axis,'fixed_value':fixed_value,
                        'start_vertex_id':edge['start_vertex_id'],
                        'end_vertex_id':edge['end_vertex_id'],
                        'endpoint_uv':pair})
    by_id={r['edge_id']:r for r in records}
    u0=by_id[1753]['fixed_value']
    u1=by_id[1548]['fixed_value']
    u2=by_id[1570]['fixed_value']
    u3=by_id[1616]['fixed_value']
    z0=by_id[85]['fixed_value']
    z1=by_id[1523]['fixed_value']
    z2=by_id[1644]['fixed_value']
    if not (u0<u1<u2<u3 and z0<z1<z2 and abs(u0-math.pi)<SOURCE_UV_TOL
            and abs(u3-2*math.pi)<SOURCE_UV_TOL):
        raise ValueError('Original source spline-trim staircase not ordered')
    if abs(by_id[1593]['fixed_value']-z1)>SOURCE_UV_TOL:
        raise ValueError('Original split circle V disagree')
    corners=[(u0,z1),(u1,z1),(u1,z0),(u2,z0),
             (u2,z1),(u3,z1),(u3,z2),(u0,z2)]
    if len(original_vertices)!=8:
        raise ValueError('Original source corner count changed')
    for idx,edge in enumerate(records):
        expected=(corners[idx],corners[(idx+1)%8])
        if any(math.dist(p,q)>SOURCE_UV_TOL for p,q in zip(edge['endpoint_uv'],expected)):
            raise ValueError(f'Original source edge #{edge["edge_id"]} is not in derived UV contour')
    return {'source_sha256':digest,'face_id':FACE,'frame':frame,
            'source_edges':records,'original_vertices':original_vertices,
            'u_breaks':[u0,u1,u2,u3],'v_breaks':[z0,z1,z2],
            'source_wire_uv':corners,'source_wire_original_edge_ids':list(EXPECTED_SOURCE_EDGES)}


def _grid(partition, middle_sectors):
    if type(middle_sectors) is not int or not 1<=middle_sectors<=32:
        raise ValueError('Middle sector count must be integer [1,32]')
    u0,u1,u2,u3=partition['u_breaks']
    return [u0]+[u1+(u2-u1)*k/middle_sectors for k in range(middle_sectors+1)]+[u3]


def _cells(partition, middle_sectors):
    grid=_grid(partition,middle_sectors)
    z0,z1,z2=partition['v_breaks']
    return ([(i,1,grid[i],grid[i+1],z1,z2) for i in range(len(grid)-1)]
            +[(i,0,grid[i],grid[i+1],z0,z1) for i in range(1,len(grid)-2)])


def _area_check(partition,n):
    polygon=partition['source_wire_uv']
    area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1])))/2
    cells=_cells(partition,n)
    rectangles=sum((c[3]-c[2])*(c[5]-c[4]) for c in cells)
    if abs(area-rectangles)>1e-8:
        raise ValueError('Spline PCURVE-derived orthogonal domain not fully covered')
    for i,c in enumerate(cells):
        for d in cells[i+1:]:
            if max(0,min(c[3],d[3])-max(c[2],d[2]))*max(0,min(c[5],d[5])-max(c[4],d[4]))>1e-10:
                raise ValueError('Overlapping source UV rectangles')
    return area


def _node_ids(partition,n):
    grid=_grid(partition,n)
    values=partition['v_breaks']
    output={}
    for vid,obj in partition['original_vertices'].items():
        for i,u in enumerate(grid):
            for j,z in enumerate(values):
                if math.dist(obj['uv'],(u,z))<SOURCE_UV_TOL:
                    if (i,j) in output:
                        raise ValueError('Coincident distinct source vertices')
                    output[(i,j)]=vid
    if len(output)!=8:
        raise ValueError('Missing source original UV vertex')
    return output


def _boundary_eid(unode,znode,grid_len):
    # The fixed original axial edges are never subdivided by interpolation.
    return {(0,1):1753,(1,0):1548,(grid_len-2,0):1570,(grid_len-1,1):1616}.get((unode,znode))


def _angular_tangents(frame, u, delta):
    return _scale(_add(_scale(frame['x'],-math.sin(u)),
                       _scale(frame['y'], math.cos(u))),frame['radius']*delta/3)


def build_extension(source, baseline_bp, baseline_manifest, *, middle_sectors,
                    declared_budget_mm=PILOT_BUDGET_MM):
    partition=source_partition(source)
    if declared_budget_mm!=PILOT_BUDGET_MM:
        raise ValueError('S3.O pilot budget is fixed before angular partition selection')
    if baseline_manifest.get('source_model')!='S40' or baseline_manifest.get('source_sha256')!=partition['source_sha256']:
        raise ValueError('S3.O original source does not match S3.N baseline')
    if baseline_manifest.get('face_id')!=1986 or baseline_manifest.get('combined_patch_count')!=43 or baseline_manifest.get('combined_control_count')!=511:
        raise ValueError('Expected original S3.N 43-patch baseline')
    if sha256(baseline_bp.encode('utf-8')).hexdigest()!=baseline_manifest.get('combined_bp_sha256'):
        raise ValueError('Changed original S3.N BP or manifest')
    points,patches=read_bp(baseline_bp)
    registry=dict(baseline_manifest['original_global_source_key_to_control_index'])
    if len(points)!=511 or len(patches)!=43 or sorted(registry.values())!=list(range(len(points))):
        raise ValueError('Non-injective baseline indexed control registry')
    _area_check(partition,middle_sectors)
    frame=partition['frame']
    table=parse_entities(source)
    grid=_grid(partition,middle_sectors)
    zlist=partition['v_breaks']
    original_nodes=_node_ids(partition,middle_sectors)
    added=[]
    generator_keys=defaultdict(set)

    def intern(key,point):
        if not all(math.isfinite(t) for t in point):
            raise ValueError('Invalid non-finite Bézier point')
        if key in registry:
            idx=registry[key]
            if math.dist(points[idx],point)>CONTROL_TOL_MM:
                raise ValueError('Source canonical edge key differs from baseline coordinates')
            return idx
        idx=len(points)
        registry[key]=idx
        points.append(tuple(point))
        return idx

    for uindex,zindex,ua,ub,za,zb in _cells(partition,middle_sectors):
        du=ub-ua
        if not 0<du<=math.pi/2:
            raise ValueError('Source spline-trim patch angular width must be <=90deg')
        ids=[]
        for row in range(4):
            z=za+(zb-za)*row/3
            for col in range(4):
                at_u_endpoint=col in (0,3)
                at_z_endpoint=row in (0,3)
                unode=uindex+(col==3)
                znode=zindex+(row==3)
                original_generator=_boundary_eid(unode,zindex,len(grid)) if at_u_endpoint else None
                if original_generator is not None:
                    key,P=_linear_source_edge(table,partition,original_generator,row)
                    generator_keys[original_generator].add(key)
                elif at_u_endpoint and at_z_endpoint:
                    vertex_id=original_nodes.get((unode,znode))
                    if vertex_id is not None:
                        key=f'vertex:{vertex_id}'
                        P=coordinates(table,vertex_id)
                    else:
                        key=f's3o_uvnode:{FACE}:{unode}:{znode}'
                        P=_uv_point(frame,grid[unode],z)
                elif at_u_endpoint:
                    key=f's3o_uv_vline:{FACE}:{unode}:{zindex}:{row}'
                    P=_uv_point(frame,grid[unode],z)
                else:
                    if at_z_endpoint:
                        key=f's3o_uv_hline:{FACE}:{uindex}:{znode}:{col}'
                    else:
                        key=f's3o_uv_interior:{FACE}:{uindex}:{zindex}:{row}:{col}'
                    A=_uv_point(frame,ua,z)
                    B=_uv_point(frame,ub,z)
                    P=(A,_add(A,_angular_tangents(frame,ua,du)),
                       _sub(B,_angular_tangents(frame,ub,du)),B)[col]
                ids.append(intern(key,P))
        patches.append(tuple(ids))
        added.append({'source_advanced_face_id':FACE,
                      'kind':'S3O_SOURCE_SPLINE_PCURVE_ORTHOGONAL_RECTANGLE',
                      'u_grid_index':uindex,'v_strip_index':zindex,
                      'native_uv_rectangle':[ua,ub,za,zb],
                      'control_vertex_ids':ids})
    if len(added)!=2*middle_sectors+2:
        raise ValueError('Original spline trim changed expected patch count')
    for eid in SOURCE_AXIAL_EDGES:
        expected={_linear_source_edge(table,partition,eid,row)[0] for row in range(4)}
        if generator_keys.get(eid)!=expected:
            raise ValueError(f'Original generator #{eid} lost control identity')
    for eid in PREEXISTING_SEAMS:
        for row in range(4):
            key=_linear_source_edge(table,partition,eid,row)[0]
            if registry[key]!=baseline_manifest['original_global_source_key_to_control_index'].get(key):
                raise ValueError('Original adjacent planar/cylinder seam identity not reused')
    # The same integer identities, not tolerance welding, define every seam.
    counts=Counter()
    for patch in patches[43:]:
        for side in (patch[:4],patch[-4:],patch[0:16:4],patch[3:16:4]):
            counts[tuple(sorted(side))]+=1
    if max(counts.values())!=2 or sum(v==2 for v in counts.values())!=3*middle_sectors:
        raise ValueError('Nonconforming or non-manifold derived seam network')
    bp=_serialize(points,patches)
    manifest={'schema':'apmesh-s3o-s40-original-1519-spline-trim-partial-atlas-v1',
              'source_model':'S40','source_sha256':partition['source_sha256'],
              'face_id':FACE,'baseline_patch_count':43,'baseline_control_count':511,
              'baseline_bp_sha256':baseline_manifest['combined_bp_sha256'],
              'baseline_manifest_sha256':sha256(json.dumps(baseline_manifest,sort_keys=True).encode()).hexdigest(),
              'pilot_budget_mm':declared_budget_mm,'middle_sectors':middle_sectors,
              'original_wire_edge_curve_ids':list(EXPECTED_SOURCE_EDGES),
              'original_3d_spline_edge_ids':list(ORIGINAL_BSPLINE_EDGES),
              'original_source_generator_ids':list(SOURCE_AXIAL_EDGES),
              'source_planar_anchored_generator_ids':list(PREEXISTING_SEAMS),
              'source_uv_breaks':{'u':partition['u_breaks'],'v':partition['v_breaks']},
              'source_uv_polygon':partition['source_wire_uv'],
              'source_uv_parametric_area':_area_check(partition,middle_sectors),
              'added_patch_count':len(added),'combined_patch_count':len(patches),
              'combined_control_count':len(points),'internal_new_seams':sum(v==2 for v in counts.values()),
              'added_patches':added,'original_global_source_key_to_control_index':registry,
              'combined_bp_sha256':sha256(bp.encode('utf-8')).hexdigest(),
              'native_brep_audit':'NOT_RUN_ON_CONSTRUCTION',
              'full_original_atlas':False,'apmesh_tri_quad_meshing':'NOT_RUN'}
    return bp,manifest


def _native_edge_correspondence(partition,table,native,face_index):
    """Require eight distinct, uniquely endpoint-matched TopoDS_Edges."""
    face=native.Faces()[face_index]
    if face.geomType()!='CYLINDER' or len(face.Wires())!=1 or len(face.Edges())!=8:
        raise ValueError('Original native #1519 support/trim topology changed')
    native_edges=native.Edges()
    tolerance=max(1e-8,native.BoundingBox().DiagonalLength*1e-9)
    matches={}
    all_indices=[]
    for record in partition['source_edges']:
        eid=record['edge_id']
        pair=[partition['original_vertices'][record[k]]['xyz'] for k in ('start_vertex_id','end_vertex_id')]
        choices=[]
        for local in face.Edges():
            nverts=local.Vertices()
            if len(nverts)!=2:
                continue
            expected='BSPLINE' if eid in ORIGINAL_BSPLINE_EDGES else record['curve_type_3d']
            if local.geomType()!=expected:
                continue
            p=[tuple(v.Center().toTuple()) for v in nverts]
            error=min(max(math.dist(p[i],pair[i^flip]) for i in (0,1)) for flip in (0,1))
            if error<=tolerance:
                match_indices=[i for i,e in enumerate(native_edges) if e.wrapped.IsSame(local.wrapped)]
                if len(match_indices)!=1:
                    raise ValueError('Non-unique native global edge index')
                choices.append((match_indices[0],local,error))
        if len(choices)!=1:
            raise ValueError(f'Original STEP boundary #{eid} ambiguous in native face')
        idx,edge,residual=choices[0]
        incident=[i for i,f in enumerate(native.Faces()) if any(e.wrapped.IsSame(edge.wrapped) for e in f.Edges())]
        if len(incident)!=2 or face_index not in incident:
            raise ValueError('Original manifold source edge lacks two-sided native incidence')
        matches[eid]={'native_index':idx,'native_edge':edge,
                      'endpoint_distance_mm':residual,'native_incident_face_indices':incident}
        all_indices.append(idx)
    if len(set(all_indices))!=8:
        raise ValueError('Distinct original B-spline boundary IDs map to same native edge')
    return matches


def _native_boundary_distance(partition,vertices,added_patches,edge_map,*,budget):
    """Compare cubic indexed patch boundaries against each original native edge.

    Native 2D PCURVEs supply monotone U/V parameter inversion on the *actual*
    native TopoDS_Edge. This is independent from radial cylinder support checks.
    """
    frame=partition['frame']
    u=partition['u_breaks']
    z=partition['v_breaks']
    native_face=edge_map['native_face']
    rows=[]
    for source in partition['source_edges']:
        eid=source['edge_id']
        orig=edge_map[eid]['native_edge']
        c3=BRepAdaptor_Curve(orig.wrapped)
        c2=BRepAdaptor_Curve2d(orig.wrapped,native_face.wrapped)
        p0,p1=c2.FirstParameter(),c2.LastParameter()
        if abs(c3.FirstParameter()-p0)>1e-8 or abs(c3.LastParameter()-p1)>1e-8:
            raise ValueError('Original 3D and PCURVE edge parameter ranges disagree')
        horizontal=source['fixed_axis']=='V'
        fixed=source['fixed_value']
        a=source['endpoint_uv'][0][0 if horizontal else 1]
        b=source['endpoint_uv'][1][0 if horizontal else 1]
        lo,hi=sorted((a,b))
        error=0.0
        num=0
        # Every BP piece on the original polygon is visited. Internal seams
        # are excluded by the fixed original edge's exact UV parameter.
        for label in added_patches:
            ua,ub,za,zb=label['native_uv_rectangle']
            if horizontal:
                if not (abs(za-fixed)<SOURCE_UV_TOL or abs(zb-fixed)<SOURCE_UV_TOL):
                    continue
                if ua<lo-SOURCE_UV_TOL or ub>hi+SOURCE_UV_TOL:
                    continue
                # Horizontal source edge can only lie on the lower or upper
                # outer contour of a particular rectangular UV cell.
                if not ((abs(za-fixed)<SOURCE_UV_TOL and (abs(fixed-z[0])<SOURCE_UV_TOL or (abs(fixed-z[1])<SOURCE_UV_TOL and (ua<u[1] or ua>=u[2])))) or
                        (abs(zb-fixed)<SOURCE_UV_TOL and abs(fixed-z[2])<SOURCE_UV_TOL)):
                    continue
                param=1 if abs(zb-fixed)<SOURCE_UV_TOL else 0
            else:
                if not (abs(ua-fixed)<SOURCE_UV_TOL or abs(ub-fixed)<SOURCE_UV_TOL):
                    continue
                if za<lo-SOURCE_UV_TOL or zb>hi+SOURCE_UV_TOL:
                    continue
                param=1 if abs(ub-fixed)<SOURCE_UV_TOL else 0
            controls=[vertices[i] for i in label['control_vertex_ids']]
            for step in range(9):
                t=step/8
                U=ua+(ub-ua)*t if horizontal else fixed
                V=fixed if horizontal else za+(zb-za)*t
                # Parametric position need not use the original B-spline's
                # nonlinear knot parametrization. Invert the actual UV curve.
                target=U if horizontal else V
                aa,bb=p0,p1
                va=c2.Value(aa);vb=c2.Value(bb)
                qa=va.X() if horizontal else va.Y()
                qb=vb.X() if horizontal else vb.Y()
                if target<min(qa,qb)-SOURCE_UV_TOL or target>max(qa,qb)+SOURCE_UV_TOL:
                    raise ValueError('Patch boundary outside native original PCURVE extent')
                for _ in range(48):
                    mm=(aa+bb)*.5
                    q=c2.Value(mm)
                    qm=q.X() if horizontal else q.Y()
                    if (qm<target)==(qa<qb):
                        aa=mm
                    else:
                        bb=mm
                xyz=c3.Value((aa+bb)*.5)
                original=(xyz.X(),xyz.Y(),xyz.Z())
                predicted=surface(controls,t,param) if horizontal else surface(controls,param,t)
                deviation=math.dist(original,predicted)
                error=max(error,deviation)
                num+=1
        if num==0 or error>budget:
            raise ValueError(f'Original native source curve #{eid} coverage/distance not admitted ({num}, {error})')
        rows.append({'original_edge_curve_id':eid,'native_topods_edge_index':edge_map[eid]['native_index'],
                     'original_curve_type':source['curve_type_3d'],
                     'boundary_sample_count':num,'max_native_edge_distance_mm':error,
                     'native_incident_face_indices':edge_map[eid]['native_incident_face_indices']})
    return rows


def audit_original(source,native,baseline_bp,baseline_manifest,bp,manifest,
                   *,declared_budget_mm=PILOT_BUDGET_MM):
    """Independently recompute original-source and native-trim admission gates."""
    part=source_partition(source)
    if declared_budget_mm!=PILOT_BUDGET_MM or manifest.get('pilot_budget_mm')!=declared_budget_mm:
        raise ValueError('Pilot budget changed after patch generation')
    if manifest.get('source_sha256')!=part['source_sha256'] or manifest.get('face_id')!=FACE:
        raise ValueError('Original source/face manifest mismatch')
    if sha256(bp.encode('utf-8')).hexdigest()!=manifest.get('combined_bp_sha256'):
        raise ValueError('Indexed Bézier BP checksum mismatch')
    if sha256(baseline_bp.encode('utf-8')).hexdigest()!=manifest.get('baseline_bp_sha256'):
        raise ValueError('Previous S3.N baseline BP mismatch')
    if sha256(json.dumps(baseline_manifest,sort_keys=True).encode()).hexdigest()!=manifest.get('baseline_manifest_sha256'):
        raise ValueError('Previous S3.N baseline manifest mismatch')
    expected_bp,expected_manifest=build_extension(source,baseline_bp,baseline_manifest,
                                                 middle_sectors=manifest['middle_sectors'],
                                                 declared_budget_mm=declared_budget_mm)
    if bp!=expected_bp or manifest!=expected_manifest:
        raise ValueError('Source-anchored reconstructed BP/manifest recomputation mismatch')
    report=inventory(source,native)
    native_index=next(rec['native_face_index'] for rec in report['faces'] if rec['source_advanced_face_id']==FACE)
    if native_index!=12:
        raise ValueError('Certified original native face index changed')
    face=native.Faces()[native_index]
    if tuple(round(x,5) for x in BRepTools.UVBounds_s(face.wrapped)) != tuple(round(x,5) for x in (part['u_breaks'][0],part['u_breaks'][3],part['v_breaks'][0],part['v_breaks'][2])):
        raise ValueError('Source/native original cylindrical bounds disagree')
    table=parse_entities(source)
    edges=_native_edge_correspondence(part,table,native,native_index)
    edges['native_face']=face
    vertices,patches=read_bp(bp)
    additions=manifest['added_patches']
    if len(additions)!=len(patches)-43 or len(additions)!=2*manifest['middle_sectors']+2:
        raise ValueError('Expected exact original spline-trim patch inventory')
    stats=Counter()
    max_radial=max_projection=0.0
    for row in additions:
        ua,ub,za,zb=row['native_uv_rectangle']
        geo={'face_id':FACE,'frame':part['frame'],'zmin':za,'zmax':zb,
             'start_u':ua,'signed_sweep_rad':ub-ua}
        interval=certify_patch(vertices,row['control_vertex_ids'],geo,0,1)
        bound=interval['radial_support_error_upper_mm']
        if bound>declared_budget_mm:
            raise ValueError('Bernstein radial enclosure exceeds predeclared pilot budget')
        max_radial=max(max_radial,bound)
        classified=classify_patch(face,vertices,row['control_vertex_ids'],
                                  distance_budget_mm=declared_budget_mm)
        max_projection=max(max_projection,classified['max_native_cylinder_projection_distance_mm'])
        stats.update(classified['classification_histogram'])
    original_boundary=_native_boundary_distance(part,vertices,additions,edges,budget=declared_budget_mm)
    for eid in PREEXISTING_SEAMS:
        for j in range(4):
            key=_linear_source_edge(table,part,eid,j)[0]
            idx=baseline_manifest['original_global_source_key_to_control_index'].get(key)
            if idx is None or manifest['original_global_source_key_to_control_index'].get(key)!=idx:
                raise ValueError('Previously admitted original seam control index changed')
    if len(original_boundary)!=8:
        raise ValueError('Missing original spline/circle/line feature boundaries')
    n = manifest['middle_sectors']
    expected_piece_samples = {1523:9, 1548:9, 85:9*n, 1570:9,
                              1593:9, 1616:9, 1644:9*(n+2), 1753:9}
    if {row['original_edge_curve_id']:row['boundary_sample_count']
            for row in original_boundary} != expected_piece_samples:
        raise ValueError('Source B-spline boundary subdivision missing or duplicated')
    original_source_owners = defaultdict(set)
    for source_face_id,(kind,_) in table.items():
        if kind != 'ADVANCED_FACE':
            continue
        for source_wire in oriented_edges(table, source_face_id)[1]:
            for source_edge in source_wire:
                original_source_owners[source_edge['edge_curve_id']].add(source_face_id)
    for row in original_boundary:
        eid = row['original_edge_curve_id']
        if len(original_source_owners[eid]) != 2 or FACE not in original_source_owners[eid]:
            raise ValueError('Original source edge has no unique second-side source face')
        row['original_step_owner_face_ids'] = sorted(original_source_owners[eid])
    return {'schema':'apmesh-s3o-s40-native-1519-spline-trim-audit-v1',
            'source_sha256':part['source_sha256'],'original_face_id':FACE,
            'original_native_face_index':native_index,'original_radius_mm':16,
            'original_source_edge_curve_ids':list(EXPECTED_SOURCE_EDGES),
            'original_spline_edge_ids':list(ORIGINAL_BSPLINE_EDGES),
            'baseline_patch_count':43,'added_patch_count':len(additions),
            'combined_patch_count':len(patches),'combined_control_count':len(vertices),
            'derived_seams_verified':manifest['internal_new_seams'],
            'preexisting_planar_shared_edges_verified':list(PREEXISTING_SEAMS),
            'native_original_boundary_edges':original_boundary,
            'max_native_original_edge_sampled_distance_mm':max(x['max_native_edge_distance_mm'] for x in original_boundary),
            'max_guarded_radial_support_error_mm':max_radial,
            'max_native_cylinder_sampled_projection_error_mm':max_projection,
            'native_trim_classification_histogram':dict(sorted(stats.items())),
            'native_interior_sample_count':len(additions)*81,
            'native_boundary_sample_count':len(additions)*44,
            'budget_mm':declared_budget_mm,
            'native_trim_scope':'DISCRETE_NATIVE_FACE_CLASSIFICATION',
            'original_boundary_scope':'DISCRETE_ORIGINAL_3D_BSPLINE_CURVE_EVALUATION_VIA_NATIVE_PCURVE_INVERSION',
            'global_continuous_Hausdorff_certified':False,
            'apmesh_tri_quad':'NOT_RUN','full_atlas':False}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-step',type=Path,required=True)
    ap.add_argument('--baseline-bp',type=Path,required=True)
    ap.add_argument('--baseline-manifest',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--middle-sectors',type=int,default=7)
    ap.add_argument('--budget-mm',type=float,default=PILOT_BUDGET_MM)
    args=ap.parse_args()
    if sha256(args.source_step.read_bytes()).hexdigest()!=SOURCES['S40'][1]:
        raise ValueError('Original industrial S40 file byte hash drift')
    source=args.source_step.read_text('utf-8')
    _digest(source)
    baseline_bp=args.baseline_bp.read_text('utf-8')
    baseline_manifest=json.loads(args.baseline_manifest.read_text('utf-8'))
    native=cq.importers.importStep(str(args.source_step)).val()
    bp,manifest=build_extension(source,baseline_bp,baseline_manifest,
                                middle_sectors=args.middle_sectors,declared_budget_mm=args.budget_mm)
    audited=audit_original(source,native,baseline_bp,baseline_manifest,bp,manifest,
                           declared_budget_mm=args.budget_mm)
    args.output_dir.mkdir(exist_ok=True,parents=True)
    (args.output_dir/'s40_spline1519.partial.bp').write_text(bp,'utf-8')
    (args.output_dir/'s40_spline1519_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n','utf-8')
    (args.output_dir/'s40_spline1519_native_audit.json').write_text(json.dumps(audited,indent=2,sort_keys=True)+'\n','utf-8')
    print(json.dumps({'admission':'BOUNDED_EXPERIMENTAL_PARTIAL_ATLAS',
                      'added_patches':audited['added_patch_count'],
                      'total_patches':audited['combined_patch_count'],
                      'max_spline_edge_distance_mm':audited['max_native_original_edge_sampled_distance_mm']}))


if __name__=='__main__':
    main()
