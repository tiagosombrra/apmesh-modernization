#!/usr/bin/env python3
"""Research-only original S40 #1986 orthogonal cylinder trim partition.

All source identity checks use pinned STEP EDGE_CURVE and PCURVE entities.
No coordinate welding, full-model atlas, or APMesh meshing is performed.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRepTools import BRepTools

from audit_analytic_bp import read_bp
from s3c_step_source_gate import SOURCES, COORDINATES, coordinates, entity, oriented_edges, parse_entities, refs
from s3g_cylindrical_source_constraints import _axis_support, _point
from s3i_joint_source_atlas import _serialize
from s3j_radial_support_enclosure import certify_patch
from s3k_native_uv_trim_gate import classify_patch
from s3l_s40_partial_cylinder_atlas import _native_source_edge, _source_prerequisites, construct_partial

FACE = 1986
SOURCE_GENERATORS = (222, 355, 2019, 2071)
SOURCE_CIRCLES = (1991, 1962, 2042, 1834)
PILOT_BUDGET_MM = .001
SOURCE_UV_TOL = 1e-8
CONTROL_TOL_MM = 1e-9


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def _add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def _scale(a, k):
    return tuple(x*k for x in a)


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def _norm(a):
    return math.sqrt(_dot(a, a))


def _source_digest(text):
    digest = sha256(text.encode('utf-8')).hexdigest()
    if digest != SOURCES['S40'][1]:
        raise ValueError('S3.N original S40 SHA-256 mismatch')
    return digest


def _source_frame(table):
    sid, origin, axis, radius = _axis_support(table, FACE)
    _, face_body = entity(table, FACE, 'ADVANCED_FACE')
    if refs(face_body)[-1] != sid:
        raise ValueError('Source cylindrical support reference changed')
    _, cyl = entity(table, sid, 'CYLINDRICAL_SURFACE')
    _, placement = entity(table, refs(cyl)[0], 'AXIS2_PLACEMENT_3D')
    axes = refs(placement)
    if len(axes) != 3:
        raise ValueError('Cylindrical original lacks explicit X basis')
    x = _point(table, axes[2], expected='DIRECTION')
    x = _scale(x, 1/_norm(x))
    y = _cross(axis, x)
    if abs(_dot(axis, x)) > 1e-10 or abs(_norm(y)-1) > 1e-10:
        raise ValueError('Source support frame not orthonormal')
    return {'id':sid, 'origin':origin, 'axis':axis,
            'x':x, 'y':y, 'radius':radius}


def _v(frame, P):
    return _dot(_sub(P, frame['origin']), frame['axis'])


def _u(frame, P):
    delta = _sub(P, frame['origin'])
    result = math.atan2(_dot(delta, frame['y']), _dot(delta, frame['x']))
    return result % (2*math.pi)


def _uv_point(frame, u, z):
    radial = _add(_scale(frame['x'], math.cos(u)),
                  _scale(frame['y'], math.sin(u)))
    return _add(_add(frame['origin'], _scale(frame['axis'], z)),
                _scale(radial, frame['radius']))


def _source_pcurve_axis(table, source_edge_id, support_id):
    _, edge = entity(table, source_edge_id, 'EDGE_CURVE')
    graph = refs(edge)
    _, wrapper = entity(table, graph[2], 'SURFACE_CURVE')
    matches = []
    for pcid in refs(wrapper)[1:]:
        kind, raw = entity(table, pcid)
        if kind != 'PCURVE' or refs(raw)[0] != support_id:
            continue
        _, repr_raw = entity(table, refs(raw)[1], 'DEFINITIONAL_REPRESENTATION')
        ctype, curve = entity(table, refs(repr_raw)[0])
        if ctype != 'LINE':
            raise ValueError('Source #1986 non-linear cylinder PCURVE unsupported')
        origin_id, direction_vector_id = refs(curve)
        _, p = entity(table, origin_id, 'CARTESIAN_POINT')
        _, vect = entity(table, direction_vector_id, 'VECTOR')
        _, d = entity(table, refs(vect)[0], 'DIRECTION')
        pm, dm = COORDINATES.search(p), COORDINATES.search(d)
        if not pm or not dm:
            raise ValueError('Malformed original UV parametric line')
        q = tuple(float(v) for v in pm[1].split(','))
        direction = tuple(float(v) for v in dm[1].split(','))
        if len(q) != 2 or len(direction) != 2:
            raise ValueError('Original PCURVE must be 2D')
        if abs(direction[0]) <= 1e-10 and abs(direction[1]) >= 1e-6:
            matches.append(('U', q[0], pcid))
        elif abs(direction[1]) <= 1e-10 and abs(direction[0]) >= 1e-6:
            matches.append(('V', q[1], pcid))
        else:
            raise ValueError('Source #1986 PCURVE not axial or circular')
    if len(matches) != 1:
        raise ValueError('Source #1986 edge lacks unique cylinder PCURVE')
    return matches[0]


def source_partition(text):
    """Recover the staircase from original native STEP line/circle identities."""
    digest = _source_digest(text)
    table = parse_entities(text)
    support, wires = oriented_edges(table, FACE)
    if support != 'CYLINDRICAL_SURFACE' or len(wires) != 1 or len(wires[0]) != 8:
        raise ValueError('S40 original #1986 source boundary topology changed')
    wire = wires[0]
    if {e['edge_curve_id'] for e in wire if e['master_3d_curve'] == 'LINE'} != set(SOURCE_GENERATORS):
        raise ValueError('Original #1986 generator source identities changed')
    if {e['edge_curve_id'] for e in wire if e['master_3d_curve'] == 'CIRCLE'} != set(SOURCE_CIRCLES):
        raise ValueError('Original #1986 circle source identities changed')
    frame = _source_frame(table)
    src_edges = []
    source_vertices = {}
    for e in wire:
        eid = e['edge_curve_id']
        axis, fixed, pcid = _source_pcurve_axis(table, eid, frame['id'])
        if axis != ('U' if eid in SOURCE_GENERATORS else 'V'):
            raise ValueError('Original STEP master curve and PCURVE axes disagree')
        points = [coordinates(table, e[k]) for k in ('start_vertex_id','end_vertex_id')]
        uv = []
        for vertex_id, point in zip((e['start_vertex_id'],e['end_vertex_id']), points):
            z, phi = _v(frame, point), _u(frame, point)
            # The source support crosses the 2*pi seam; preserve its declared UV branch.
            if axis == 'U':
                phi = fixed
                if abs(((phi-_u(frame, point)+math.pi)%(2*math.pi))-math.pi) > SOURCE_UV_TOL:
                    raise ValueError('Original source generator U contradicts 3D vertex')
            else:
                if abs(z-fixed) > SOURCE_UV_TOL:
                    raise ValueError('Original circle V contradicts 3D vertex')
                # Choose the actual native support U branch in [pi, 2*pi].
                candidates = (phi-2*math.pi, phi, phi+2*math.pi)
                phi = min(candidates, key=lambda x: max(math.pi-x, 0, x-2*math.pi))
                if phi < math.pi-SOURCE_UV_TOL or phi > 2*math.pi+SOURCE_UV_TOL:
                    raise ValueError('Circular arc end outside source native U branch')
            if vertex_id in source_vertices and math.dist(source_vertices[vertex_id]['xyz'], point)>1e-12:
                raise ValueError('Inconsistent original source vertex entity')
            source_vertices[vertex_id] = {'xyz':point, 'uv':(phi,z)}
            uv.append((phi,z))
        src_edges.append({'edge_id':eid,'curve':e['master_3d_curve'],
                          'pcurve_id':pcid,'fixed_axis':axis,'fixed_value':fixed,
                          'source_vertices':[e['start_vertex_id'],e['end_vertex_id']],
                          'uv_endpoints':uv})
    original_u = {row['edge_id']:row['fixed_value'] for row in src_edges if row['fixed_axis']=='U'}
    original_v = {row['edge_id']:row['fixed_value'] for row in src_edges if row['fixed_axis']=='V'}
    u0,u1,u2,u3 = (original_u[eid] for eid in (355,2019,2071,222))
    z0,z1,z2 = (original_v[eid] for eid in (2042,1962,1991))
    if not (u0<u1<u2<u3 and z0<z1<z2):
        raise ValueError('Original #1986 staircase ordering changed')
    if abs(original_v[1834]-z1)>SOURCE_UV_TOL:
        raise ValueError('Lower left/right circular traces disagree in STEP source')
    if abs(u0-math.pi)>SOURCE_UV_TOL or abs(u3-2*math.pi)>SOURCE_UV_TOL:
        raise ValueError('Original staircase periodic U envelope changed')
    # Verify original edges follow this eight-sided stepped polygon exactly.
    corners = [(u3,z1),(u3,z2),(u0,z2),(u0,z1),
               (u1,z1),(u1,z0),(u2,z0),(u2,z1)]
    expected_eids = [222,1991,355,1962,2019,2042,2071,1834]
    for idx,(edge,expected_eid) in enumerate(zip(src_edges, expected_eids)):
        if edge['edge_id']!=expected_eid:
            raise ValueError('Original STEP source wire order changed')
        for found, expected in zip(edge['uv_endpoints'],(corners[idx],corners[(idx+1)%8])):
            if math.dist(found,expected)>SOURCE_UV_TOL:
                raise ValueError(f'Original edge #{expected_eid} changes stepped UV geometry')
    return {'face_id':FACE,'source_sha256':digest,'frame':frame,
            'u_breaks':[u0,u1,u2,u3],'v_breaks':[z0,z1,z2],
            'source_edges':src_edges,'original_vertices':source_vertices,
            'source_wire_uv':corners,
            'source_expected_edge_ids':expected_eids}


def angular_grid(partition, middle_sectors):
    if type(middle_sectors) is not int or not 1<=middle_sectors<=32:
        raise ValueError('Middle sector count must be an integer between 1 and 32')
    a,b,c,d = partition['u_breaks']
    return [a]+[b+(c-b)*i/middle_sectors for i in range(middle_sectors+1)]+[d]


def rectangle_cells(partition, middle_sectors):
    """Partition a step polygon into conforming rectangles without T-junctions."""
    u = angular_grid(partition, middle_sectors)
    cells=[]
    # The upper band has left + middle + right strips.
    for i in range(len(u)-1):
        cells.append((i,1,u[i],u[i+1],partition['v_breaks'][1],partition['v_breaks'][2]))
    # The lower central tab has the identical U splits as the middle upper band.
    for i in range(1,len(u)-2):
        cells.append((i,0,u[i],u[i+1],partition['v_breaks'][0],partition['v_breaks'][1]))
    if len(cells)!=2*middle_sectors+2:
        raise AssertionError('Unexpected rectangle cell count')
    return cells


def _boundary_source_vertices(partition, middle_sectors):
    grid = angular_grid(partition, middle_sectors)
    zlist = partition['v_breaks']
    original={}
    for vertex_id,point in partition['original_vertices'].items():
        p=point['uv']
        for i,u in enumerate(grid):
            for j,z in enumerate(zlist):
                if abs(p[0]-u)<=SOURCE_UV_TOL and abs(p[1]-z)<=SOURCE_UV_TOL:
                    k=(i,j)
                    if k in original and original[k]!=vertex_id:
                        raise ValueError('Multiple original vertex identities on same source corner')
                    original[k]=vertex_id
    if len(original)!=8:
        raise ValueError('Source polygon original endpoint count changed')
    return original


def _linear_source_edge(table, partition, eid, row):
    _, raw=entity(table,eid,'EDGE_CURVE')
    a,b=refs(raw)[:2]
    P,Q=coordinates(table,a),coordinates(table,b)
    frame=partition['frame']
    za,zb = _v(frame,P),_v(frame,Q)
    if za<zb:
        low,high=P,Q
        edge_dir=1
        low_vertex,high_vertex=a,b
    else:
        low,high=Q,P
        edge_dir=-1
        low_vertex,high_vertex=b,a
    t=row/3
    point=tuple((1-t)*x+t*y for x,y in zip(low,high))
    key=(f'vertex:{low_vertex}' if row==0 else
         f'vertex:{high_vertex}' if row==3 else
         f'edge:{eid}:{row if edge_dir>0 else 3-row}')
    return key,point


def build_extension(source_text, baseline_bp, baseline_manifest, *, middle_sectors,
                    declared_budget_mm=PILOT_BUDGET_MM):
    """Append S40 #1986, reusing existing native planar source-edge controls."""
    partition=source_partition(source_text)
    if not math.isfinite(declared_budget_mm) or declared_budget_mm<=0:
        raise ValueError('Invalid independently fixed radial budget')
    if declared_budget_mm!=PILOT_BUDGET_MM:
        raise ValueError('S3.N pilot budget is fixed before sector selection')
    if baseline_manifest.get('source_sha256')!=partition['source_sha256']:
        raise ValueError('Baseline S3.L original source identity disagrees')
    if baseline_manifest.get('admitted_planar_faces')!=9 or baseline_manifest.get('admitted_cylinder_faces')!=4:
        raise ValueError('Baseline S3.L admitted source census changed')
    if baseline_manifest.get('patch_count')!=25 or baseline_manifest.get('control_count')!=320:
        raise ValueError('Baseline S3.L patch/control census changed')
    if sha256(baseline_bp.encode('utf-8')).hexdigest()!=baseline_manifest.get('bp_sha256'):
        raise ValueError('Baseline S3.L BP digest differs from recorded manifest')
    old_points,old_patches=read_bp(baseline_bp)
    registry=dict(baseline_manifest['control_key_to_id'])
    if sorted(registry.values())!=list(range(len(old_points))) or len(registry)!=len(old_points):
        raise ValueError('Baseline S3.L canonical key index invalid')
    points=list(old_points)
    patches=list(old_patches)
    frame=partition['frame']
    table=parse_entities(source_text)
    grid=angular_grid(partition,middle_sectors)
    zlist=partition['v_breaks']
    original_nodes=_boundary_source_vertices(partition,middle_sectors)
    all_cells=rectangle_cells(partition,middle_sectors)
    source_line_grid={
        (0,1):355, (len(grid)-1,1):222,
        (1,0):2019,(len(grid)-2,0):2071,
    }
    def intern(key,xyz):
        xyz=tuple(xyz)
        if not all(map(math.isfinite,xyz)):
            raise ValueError('Nonfinite original cylindrical control')
        if key in registry:
            idx=registry[key]
            if math.dist(points[idx],xyz)>CONTROL_TOL_MM:
                raise ValueError('Original canonical source key has inconsistent coordinates')
            return idx
        idx=len(points)
        registry[key]=idx
        points.append(xyz)
        return idx
    labels=[]
    source_generator_records={}
    for uindex,zindex,ua,ub,za,zb in all_cells:
        ids=[]
        du=ub-ua
        if du<=0 or du>math.pi/2+1e-10:
            raise ValueError('Cubic sector larger than permitted 90 degree wedge')
        for row in range(4):
            z=za+(zb-za)*row/3
            for col in range(4):
                phi=ua+du*col/3
                if col==0 or col==3:
                    phi=ua if col==0 else ub
                    unode=uindex+(1 if col==3 else 0)
                    own=source_line_grid.get((unode,zindex))
                    if own is not None:
                        key,P=_linear_source_edge(table,partition,own,row)
                        source_generator_records.setdefault(own,set()).add(key)
                    elif row in (0,3):
                        znode=zindex+(1 if row==3 else 0)
                        vid=original_nodes.get((unode,znode))
                        key=(f'vertex:{vid}' if vid is not None else
                             f's3n_uvnode:{FACE}:{unode}:{znode}')
                        P=(coordinates(table,vid) if vid is not None else
                           _uv_point(frame,phi,z))
                    else:
                        key=f's3n_uv_vline:{FACE}:{unode}:{zindex}:{row}'
                        P=_uv_point(frame,phi,z)
                elif row in (0,3):
                    znode=zindex+(1 if row==3 else 0)
                    key=f's3n_uv_hline:{FACE}:{uindex}:{znode}:{col}'
                    P=None
                else:
                    key=f's3n_uv_interior:{FACE}:{uindex}:{zindex}:{row}:{col}'
                    P=None
                if P is None:
                    A=_uv_point(frame,ua,z)
                    B=_uv_point(frame,ub,z)
                    scale=frame['radius']*du/3
                    ta=_scale(_add(_scale(frame['x'],-math.sin(ua)),
                                   _scale(frame['y'],math.cos(ua))),scale)
                    tb=_scale(_add(_scale(frame['x'],-math.sin(ub)),
                                   _scale(frame['y'],math.cos(ub))),scale)
                    P=(A,_add(A,ta),_sub(B,tb),B)[col]
                ids.append(intern(key,P))
        patches.append(tuple(ids))
        labels.append({'kind':'S3N_SOURCE_CYLINDER_ORTHOGONAL_RECTANGLE',
                       'source_advanced_face_id':FACE,'source_native_face_index':None,
                       'u_grid_index':uindex,'v_strip_index':zindex,
                       'native_uv_rectangle':[ua,ub,za,zb],
                       'control_vertex_ids':ids})
    total=len(labels)
    if total!=2*middle_sectors+2:
        raise AssertionError('Source decomposition produced unexpected patch count')
    # Each original axial generator must be represented by all four canonical controls.
    for eid in SOURCE_GENERATORS:
        expected={_linear_source_edge(table,partition,eid,k)[0] for k in range(4)}
        if source_generator_records.get(eid)!=expected:
            raise ValueError('An original source LINE boundary was lost')
    for eid in (2019,2071):
        keys=[_linear_source_edge(table,partition,eid,k)[0] for k in range(4)]
        if not all(k in baseline_manifest['control_key_to_id'] for k in keys):
            raise ValueError('Original planar anchored generator controls missing in baseline')
        for k in keys:
            if registry[k]!=baseline_manifest['control_key_to_id'][k]:
                raise ValueError('Original S40 planar/cylinder control identity was not reused')
    # Count each internal seam by global integer index, not coincident coordinates.
    new_patches=patches[len(old_patches):]
    edge_count={}
    for patch in new_patches:
        for group in ((patch[0],patch[1],patch[2],patch[3]),
                      (patch[12],patch[13],patch[14],patch[15]),
                      (patch[0],patch[4],patch[8],patch[12]),
                      (patch[3],patch[7],patch[11],patch[15])):
            canonical=tuple(sorted(group))
            edge_count[canonical]=edge_count.get(canonical,0)+1
    if any(v>2 for v in edge_count.values()):
        raise ValueError('Non-manifold patch seam introduced in original manifold control')
    internal=sum(v==2 for v in edge_count.values())
    if internal!=3*middle_sectors:
        # Upper band horizontal adjacency: K+1, lower band: K-1,
        # plus K horizontal shared edges along the stepped tab.
        raise ValueError('Generated source rectangle seam count inconsistent')
    bp=_serialize(points,patches)
    manifest={
        'schema':'apmesh-s3n-original-s40-step1986-orthogonal-partial-atlas-v1',
        'source_model':'S40','source_sha256':partition['source_sha256'],
        'face_id':FACE,'baseline_s3l_bp_sha256':baseline_manifest['bp_sha256'],
        'baseline_s3l_manifest_sha256':sha256(json.dumps(baseline_manifest,sort_keys=True).encode()).hexdigest(),
        'baseline_patch_count':len(old_patches),'baseline_control_count':len(old_points),
        'pilot_budget_mm':declared_budget_mm,'middle_sectors':middle_sectors,
        'u_breaks':partition['u_breaks'],'v_breaks':partition['v_breaks'],
        'source_wire_original_edge_ids':partition['source_expected_edge_ids'],
        'source_generator_edge_ids':list(SOURCE_GENERATORS),
        'source_circular_edge_ids':list(SOURCE_CIRCLES),
        'source_planar_anchored_generator_edge_ids':[2019,2071],
        'original_2d_wire_polygon':partition['source_wire_uv'],
        'added_patch_count':total,'combined_patch_count':len(patches),
        'combined_control_count':len(points),
        'derived_internal_indexed_seam_count':internal,
        'original_global_source_key_to_control_index':registry,
        'added_patches':labels,'combined_bp_sha256':sha256(bp.encode()).hexdigest(),
        'native_brep_audit':'NOT_RUN_ON_CONSTRUCTION',
        'continuous_native_trim_certified':False,
        'full_s40_cad_patch_atlas':False,'apmesh_tri_quad':'NOT_RUN',
        'genuine_original_nonmanifold_3plus':'NOT_ESTABLISHED'
    }
    return bp,manifest


def _parametric_partition_proof(partition, middle_sectors):
    """Verify rectangle disjointness and polygon area from original STEP PCURVEs."""
    cells=rectangle_cells(partition,middle_sectors)
    polygon=partition['source_wire_uv']
    area=.5*abs(sum(a[0]*b[1]-b[0]*a[1]
                      for a,b in zip(polygon,polygon[1:]+polygon[:1])))
    rectangular=sum((ub-ua)*(zb-za) for _,_,ua,ub,za,zb in cells)
    for i,a in enumerate(cells):
        for b in cells[i+1:]:
            overlap_u=max(0.,min(a[3],b[3])-max(a[2],b[2]))
            overlap_z=max(0.,min(a[5],b[5])-max(a[4],b[4]))
            if overlap_u*overlap_z>1e-10:
                raise ValueError('Proposed source UV rectangles have positive overlap')
    if abs(area-rectangular)>1e-7:
        raise ValueError('Original STEP trim area is not covered by rectangle union')
    return {'source_polygon_area_parametric':area,
            'partition_area_parametric':rectangular,
            'union_without_positive_area_overlap':True,
            'analytical_coverage_of_original_orthogonal_uv_polygon':True}


def _native_original_edges(table, native_shape, original_face_id):
    """Map the eight original source boundaries to unique native TopoDS edges."""
    from original_cad_planar_atlas import same_index
    from collections import defaultdict
    owners=defaultdict(set)
    for fid,(kind,_) in table.items():
        if kind!='ADVANCED_FACE':
            continue
        _,wires=oriented_edges(table,fid)
        for wire in wires:
            for x in wire:
                owners[x['edge_curve_id']].add(fid)
    _,wires=oriented_edges(table,FACE)
    original_edge_data=[]
    native_all=native_shape.Edges()
    local_edges=native_shape.Faces()[original_face_id].Edges()
    if len(local_edges)!=8:
        raise ValueError('Original source/native #1986 edge count no longer equals eight')
    tolerance=max(1e-8,native_shape.BoundingBox().DiagonalLength*1e-9)
    for item in wires[0]:
        eid=item['edge_curve_id']
        points=[coordinates(table,item[key]) for key in ('start_vertex_id','end_vertex_id')]
        candidates=[]
        for edge in local_edges:
            if edge.geomType()!=item['master_3d_curve'] or len(edge.Vertices())!=2:
                continue
            native_points=[tuple(float(x) for x in
                           (vertex.Center().x,vertex.Center().y,vertex.Center().z))
                           for vertex in edge.Vertices()]
            residual=min(max(math.dist(native_points[k],points[j^k])
                             for k in range(2)) for j in (0,1))
            if residual<=tolerance:
                candidates.append((same_index(native_all,edge),edge,residual))
        if len(candidates)!=1 or candidates[0][0] is None:
            raise ValueError(f'Unmatched/ambiguous original native EDGE_CURVE #{eid}')
        native_idx,native_edge,residual=candidates[0]
        incident=[i for i,face in enumerate(native_shape.Faces())
                  if any(other.wrapped.IsSame(native_edge.wrapped) for other in face.Edges())]
        if len(incident)!=2 or original_face_id not in incident:
            raise ValueError(f'Original S40 edge #{eid} lacks two-sided manifold adjacency')
        if len(owners[eid])!=2 or FACE not in owners[eid]:
            raise ValueError(f'Original STEP edge #{eid} source incidence changed')
        original_edge_data.append({'original_edge_curve_id':eid,
                                   'original_master_curve':item['master_3d_curve'],
                                   'original_source_owner_face_ids':sorted(owners[eid]),
                                   'native_topods_edge_index':native_idx,
                                   'native_incident_face_indices':incident,
                                   'endpoint_max_distance_mm':residual,
                                   'native_edge':native_edge})
    if len({record['native_topods_edge_index'] for record in original_edge_data})!=8:
        raise ValueError('Original eight source edges map to repeated native edge IDs')
    return original_edge_data


def _boundary_coverage_and_distance(partition,manifest,vertices,patches,native_edge_rows,
                                   *,fixed_budget_mm):
    """Cover every source curve interval with BP border pieces, using native edges."""
    from audit_analytic_bp import surface
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    from OCP.gp import gp_Pnt
    from collections import defaultdict
    source=partition['source_edges']
    candidate_patches=patches[manifest['baseline_patch_count']:]
    labels=manifest['added_patches']
    mapped={record['original_edge_curve_id']:record for record in native_edge_rows}
    coverage=defaultdict(list)
    maxdist=0.
    per_edge={}
    for row in source:
        eid=row['edge_id'];axis=row['fixed_axis'];constant=row['fixed_value']
        endpoint_data=row['uv_endpoints'];coordinate_index=1 if axis=='U' else 0
        low,high=sorted(point[coordinate_index] for point in endpoint_data)
        candidates=[]
        for ids,meta in zip(candidate_patches,labels):
            ua,ub,za,zb=meta['native_uv_rectangle']
            if axis=='U':
                for u,local_edge in ((ua,0),(ub,3)):
                    if abs(u-constant)<=SOURCE_UV_TOL and abs(za-low)<=SOURCE_UV_TOL and abs(zb-high)<=SOURCE_UV_TOL:
                        candidates.append((za,zb,ids,'u',local_edge))
            else:
                for z,local_edge in ((za,0),(zb,3)):
                    if abs(z-constant)<=SOURCE_UV_TOL and ua>=low-SOURCE_UV_TOL and ub<=high+SOURCE_UV_TOL:
                        candidates.append((ua,ub,ids,'v',local_edge))
        candidates.sort(key=lambda entry:entry[0])
        if not candidates or abs(candidates[0][0]-low)>SOURCE_UV_TOL or abs(candidates[-1][1]-high)>SOURCE_UV_TOL:
            raise ValueError(f'Original STEP edge #{eid} is not fully covered by boundary patches')
        for left,right in zip(candidates,candidates[1:]):
            if abs(left[1]-right[0])>SOURCE_UV_TOL:
                raise ValueError(f'Original STEP edge #{eid} has boundary gap or overlap')
        observed=0.
        native_edge=mapped[eid]['native_edge']
        for _,_,ids,direction,local_edge in candidates:
            net=[vertices[i] for i in ids]
            for k in range(9):
                t=k/8
                xyz=surface(net,local_edge/3,t) if direction=='u' else surface(net,t,local_edge/3)
                witness=BRepBuilderAPI_MakeVertex(gp_Pnt(*xyz)).Vertex()
                distance=BRepExtrema_DistShapeShape(witness,native_edge.wrapped)
                distance.Perform()
                if not distance.IsDone():
                    raise ValueError('Native original EDGE_CURVE distance solver failed')
                observed=max(observed,distance.Value())
                if observed>fixed_budget_mm+1e-7:
                    raise ValueError(f'Original edge #{eid} curve approximation exceeds budget')
        maxdist=max(maxdist,observed)
        per_edge[eid]={'original_source_edge_curve_id':eid,
                       'native_topods_edge_index':mapped[eid]['native_topods_edge_index'],
                       'original_master_curve':row['curve'],
                       'indexed_boundary_subsegments':len(candidates),
                       'boundary_samples':9*len(candidates),
                       'maximum_sampled_distance_to_trimmed_native_edge_mm':observed}
    if set(per_edge)!={row['edge_id'] for row in source}:
        raise ValueError('Original STEP source boundary inventory incomplete')
    return per_edge,maxdist

def audit_original(step_text, native_shape, baseline_bp, baseline_manifest,
                   combined_bp, manifest, *, declared_budget_mm,
                   interior_grid=9,boundary_grid=11):
    """Recompute the source partition, all identities, native trim and radial bounds."""
    digest=_source_digest(step_text)
    if manifest.get('source_sha256')!=digest:
        raise ValueError('Changed source hash in combined S40 atlas manifest')
    if declared_budget_mm!=PILOT_BUDGET_MM or declared_budget_mm!=manifest.get('pilot_budget_mm'):
        raise ValueError('The geometric budget cannot be widened after construction')
    if sha256(combined_bp.encode()).hexdigest()!=manifest.get('combined_bp_sha256'):
        raise ValueError('Combined BP SHA-256 mismatch')
    expected_bp,expected_manifest=build_extension(
        step_text,baseline_bp,baseline_manifest,
        middle_sectors=manifest['middle_sectors'],declared_budget_mm=declared_budget_mm)
    if combined_bp!=expected_bp or manifest!=expected_manifest:
        raise ValueError('S3.N BP and manifest disagree with independent source recomputation')
    original_bp, original_manifest=construct_partial(
        step_text,native_shape,model='S40',source_sha256=digest,
        sectors=4,sampled_budget_mm=PILOT_BUDGET_MM)
    if baseline_bp!=original_bp or baseline_manifest!=original_manifest:
        raise ValueError('Baseline S3.L BP is not recomputable from frozen original CAD')
    _,_,planar,ring=_source_prerequisites(
        step_text,native_shape,model='S40',source_sha256=digest)
    if FACE not in ring:
        raise ValueError('Original complex #1986 face not source/native mapped')
    native_id=ring[FACE]
    face=native_shape.Faces()[native_id]
    if face.geomType()!='CYLINDER' or len(face.Wires())!=1:
        raise ValueError('Original native #1986 cylinder source trim changed')
    frame=source_partition(step_text)['frame']
    native_bounds=tuple(map(float,BRepTools.UVBounds_s(face.wrapped)))
    ub=manifest['u_breaks'];vb=manifest['v_breaks']
    if max(abs(x-y) for x,y in zip(native_bounds,
             (ub[0],ub[-1],vb[0],vb[-1])))>SOURCE_UV_TOL:
        raise ValueError('Original #1986 native UV bounding envelope changed')
    table=parse_entities(step_text)
    tol=max(1e-8,native_shape.BoundingBox().DiagonalLength*1e-9)
    native_edges=[]
    for eid in (2019,2071):
        # Actual owning face is verified from native source graph, not assumed order.
        _,wires=oriented_edges(table,FACE)
        owner_candidates=[]
        for faceid,record in table.items():
            if record[0]=='ADVANCED_FACE' and faceid!=FACE:
                _,facewires=oriented_edges(table,faceid)
                if any(edge['edge_curve_id']==eid for wire in facewires for edge in wire):
                    owner_candidates.append(faceid)
        if len(owner_candidates)!=1 or owner_candidates[0] not in planar:
            raise ValueError('Original shared axial generator lacks unique admitted planar owner')
        found=_native_source_edge(native_shape.Faces(),native_shape.Edges(),table,eid,
                     [native_id,planar[owner_candidates[0]]],tol)
        native_edges.append({'original_edge_curve_id':eid,
                             'original_planar_owner_face_id':owner_candidates[0],
                             'native_topods_edge_index':found,
                             'shared_source_control_ids':[
            manifest['original_global_source_key_to_control_index'][
                _linear_source_edge(table,source_partition(step_text),eid,k)[0]]
                for k in range(4)]})
    vertices,patches=read_bp(combined_bp)
    if len(patches)!=manifest['combined_patch_count'] or len(vertices)!=manifest['combined_control_count']:
        raise ValueError('S3.N indexed BP census mismatch')
    maximum_radial=0
    maximum_native_projection=0
    checked_interior=0
    checked_boundary=0
    for ids,meta in zip(patches[manifest['baseline_patch_count']:],manifest['added_patches']):
        if list(ids)!=meta['control_vertex_ids']:
            raise ValueError('Source partial BP/control-index mapping changed')
        ua,ub,za,zb=meta['native_uv_rectangle']
        geometry={'frame':frame,'face_id':FACE,'start_u':ua,
                  'signed_sweep_rad':ub-ua,'zmin':za,'zmax':zb}
        analytic=certify_patch(vertices,ids,geometry,0,1)
        maximum_radial=max(maximum_radial,analytic['radial_support_error_upper_mm'])
        if maximum_radial>declared_budget_mm:
            raise ValueError('Original cylindrical patch radial enclosure exceeds budget')
        sample=classify_patch(face,vertices,ids,interior_grid=interior_grid,
                              boundary_grid=boundary_grid,distance_budget_mm=declared_budget_mm)
        maximum_native_projection=max(maximum_native_projection,
            sample['max_native_cylinder_projection_distance_mm'])
        checked_interior+=sample['interior_sample_count']
        checked_boundary+=sample['boundary_sample_count']
    area_proof=_parametric_partition_proof(
        source_partition(step_text),manifest['middle_sectors'])
    native_source_edges=_native_original_edges(table,native_shape,native_id)
    curve_coverage,max_edge_distance=_boundary_coverage_and_distance(
        source_partition(step_text),manifest,vertices,patches,native_source_edges,
        fixed_budget_mm=declared_budget_mm)
    return {
        'schema':'apmesh-s3n-original-S40-native-1986-orthogonal-trim-audit-v1',
        'source_sha256':digest,'face_id':FACE,'native_face_index':native_id,
        'new_patches':len(manifest['added_patches']),
        'total_partial_bp_patches':len(patches),
        'global_controls':len(vertices),
        'original_cylinder_source_edges_checked':len(native_source_edges),
        'original_boundary_curve_coverage':list(curve_coverage.values()),
        'original_native_boundary_edges_in_source':[
           {k:v for k,v in record.items() if k!='native_edge'}
           for record in native_source_edges],
        'maximum_native_original_boundary_sampled_distance_mm':max_edge_distance,
        'source_orthogonal_domain_partition_proof':area_proof,
        'source_planar_native_shared_edges_checked':native_edges,
        'derived_indexed_internal_seams':manifest['derived_internal_indexed_seam_count'],
        'native_trim_interior_samples':checked_interior,
        'native_trim_boundary_samples':checked_boundary,
        'max_guarded_bernstein_radial_support_error_mm':maximum_radial,
        'max_native_projected_distance_mm':maximum_native_projection,
        'predeclared_pilot_budget_mm':declared_budget_mm,
        'source_original_face_coverage':14,
        'unrepresented_original_faces':29,
        'complete_original_cad_atlas':False,
        'continuous_uv_coverage_certified':False,
        'apmesh_tri_quad':'NOT_RUN',
        'production_cpp_regression':'NOT_RUN',
        'native_trim_sampled_gate':'PASS'
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-step',type=Path,required=True)
    p.add_argument('--baseline-bp',type=Path,required=True)
    p.add_argument('--baseline-manifest',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--middle-sectors',type=int,default=6)
    p.add_argument('--budget-mm',type=float,default=PILOT_BUDGET_MM)
    args=p.parse_args()
    source=args.source_step.read_bytes()
    text=source.decode('utf-8')
    _source_digest(text)
    base=args.baseline_bp.read_text('utf-8')
    base_report=json.loads(args.baseline_manifest.read_text('utf-8'))
    combined,manifest=build_extension(text,base,base_report,
        middle_sectors=args.middle_sectors,declared_budget_mm=args.budget_mm)
    native=cq.importers.importStep(str(args.source_step)).val()
    audit=audit_original(text,native,base,base_report,combined,manifest,
                         declared_budget_mm=args.budget_mm)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'s40_step1986.partial.bp').write_text(combined,encoding='utf-8')
    (args.output_dir/'s40_step1986_manifest.json').write_text(
        json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    (args.output_dir/'s40_step1986_native_audit.json').write_text(
        json.dumps(audit,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'patches_added':manifest['added_patch_count'],
                      'patch_count':manifest['combined_patch_count'],
                      'control_count':manifest['combined_control_count'],
                      'radial_upper_mm':audit['max_guarded_bernstein_radial_support_error_mm'],
                      'native_distance_mm':audit['max_native_projected_distance_mm']},sort_keys=True))


if __name__=='__main__':
    main()
