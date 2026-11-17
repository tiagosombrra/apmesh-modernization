#!/usr/bin/env python3
"""S3.T: source-identified convex quadrangulation of original S40 planar faces.

Research-only. Uses the frozen S3.R atlas and S3.P control-key registry;
retains all source edge identities and fails closed on non-conforming seams.
The output is an original-derived private BP, not an APMesh TRI/QUAD mesh.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import itertools
import json
import math
from pathlib import Path

import cadquery as cq
from shapely.geometry import LineString, Polygon
from shapely.ops import polygonize, unary_union
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.ElSLib import ElSLib
from OCP.TopAbs import TopAbs_IN, TopAbs_ON
from OCP.gp import gp_Pnt, gp_Pnt2d

from audit_analytic_bp import read_bp, surface
from s3c_step_source_gate import SOURCES, COORDINATES, coordinates, entity, oriented_edges, parse_entities, refs
from s3i_joint_source_atlas import _serialize
from s3r_s40_conforming_hole_join import _edge_adjacency, _side
from s3s_full_original_face_census import full_correspondence, source_gate

FACE_IDS = (912, 3737)
SOURCE_EDGES_SHARED = {912: (916, 946, 974), 3737: (1234, 1185, 1109)}
EXPECTED_NATIVE_FACE = {912: 5, 3737: 42}
EXPECTED_SOURCE_BOUNDS = {912: 8, 3737: 8}
PINNED_BP_SHA = "98ff4cbfad08ce3f587607fddf3bb5e1a3697e1513a8ca86889bb28406e4028d"
PINNED_S3P_MANIFEST_SHA = "3c86bbadabd0689a93527a397560b36033e18f60db661b442eaa698f8b5c5bbe"
BUDGET_MM = .001
STRICT_PLANAR_TOL_MM = 1e-7
INDEX_COORD_TOL_MM = 1e-8
POLYGON_TOL = 1e-8


def _distance(a, b):
    return math.dist(a, b)


def _lerp(a, b, t):
    return tuple((1-t)*x+t*y for x, y in zip(a, b))


def _check_pins(step: bytes, baseline_bp: bytes, baseline_manifest: dict,
                registry_manifest: dict, budget_mm: float):
    text, _ = source_gate(step)
    if budget_mm != BUDGET_MM:
        raise ValueError('Original geometric budget cannot be changed')
    if sha256(baseline_bp).hexdigest() != PINNED_BP_SHA:
        raise ValueError('S3.R original BP SHA changed')
    if (baseline_manifest.get('joined_bp_sha256') != PINNED_BP_SHA or
        baseline_manifest.get('joined_patch_count') != 126 or
        baseline_manifest.get('source_original_face_coverage') != 17 or
        baseline_manifest.get('source_inner_hole_retained') is not True):
        raise ValueError('S3.R original atlas manifest inconsistent')
    manifest_text = (json.dumps(registry_manifest, indent=2, sort_keys=True) + '\n').encode()
    if sha256(manifest_text).hexdigest() != PINNED_S3P_MANIFEST_SHA:
        raise ValueError('Original S3.P source-key registry manifest changed')
    if registry_manifest.get('source_sha256') != SOURCES['S40'][1]:
        raise ValueError('Original source key registry belongs to another STEP')
    if len(registry_manifest.get('original_global_source_key_to_control_index', {})) != 864:
        raise ValueError('Frozen source-key registry incomplete')
    return text


def _convex_quad(xy):
    signs=[]
    for i in range(4):
        a,b,c = xy[i],xy[(i+1)%4],xy[(i+2)%4]
        cross=(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])
        signs.append(cross)
    return min(signs)>1e-8 or max(signs)<-1e-8


def _recover_partition(table: dict, face_id: int):
    """Exhaustively find a unique convex three-quad partition with two old-vertex diagonals."""
    support, wires = oriented_edges(table, face_id)
    if support != 'PLANE' or len(wires) != 1 or len(wires[0]) != 8:
        raise ValueError('Original target must have exactly one 8-edge planar wire')
    wire = wires[0]
    if len({e['edge_curve_id'] for e in wire}) != 8 or any(e['master_3d_curve'] != 'LINE' for e in wire):
        raise ValueError('Original face has unsupported or repeated source master edges')
    vertices=[e['start_vertex_id'] for e in wire]
    if len(set(vertices)) != 8 or any(e['end_vertex_id'] != vertices[(i+1)%8] for i,e in enumerate(wire)):
        raise ValueError('Source face edges do not form an oriented closed octagon')
    coords=[tuple(coordinates(table, vid)) for vid in vertices]
    if max(x[1] for x in coords)-min(x[1] for x in coords)>1e-8:
        raise ValueError('S3.T targets are not constant-Y planes')
    xy=[(p[0],p[2]) for p in coords]
    polygon=Polygon(xy)
    if not polygon.is_valid or polygon.area<=1e-7:
        raise ValueError('Original planar face polygon not valid')
    valid_diagonals=[]
    for i,j in itertools.combinations(range(8),2):
        if j==i+1 or (i==0 and j==7):
            continue
        line=LineString((xy[i],xy[j]))
        if polygon.buffer(1e-9).covers(line) and polygon.contains(line.interpolate(.5, normalized=True)):
            valid_diagonals.append((i,j,line))
    solutions=[]
    perimeter=[LineString((xy[i],xy[(i+1)%8])) for i in range(8)]
    for one,two in itertools.combinations(valid_diagonals,2):
        pieces=[p for p in polygonize(unary_union(perimeter+[one[2],two[2]]))
                if p.area>1e-8 and polygon.buffer(1e-9).covers(p)]
        if len(pieces)!=3 or abs(sum(q.area for q in pieces)-polygon.area)>POLYGON_TOL:
            continue
        quads=[]
        for p in pieces:
            if len(p.exterior.coords)!=5 or not p.is_valid:
                break
            indices=[]
            for xy_point in p.exterior.coords[:-1]:
                exact=[i for i,orig in enumerate(xy) if _distance(xy_point, orig)<1e-9]
                if len(exact)!=1:
                    break
                indices.append(exact[0])
            if len(indices)!=4 or not _convex_quad([xy[i] for i in indices]):
                break
            quads.append(tuple(vertices[i] for i in indices))
        if len(quads)==3:
            solutions.append((tuple(sorted((one[:2],two[:2]))),tuple(sorted(quads))))
    if len(solutions)!=1:
        raise ValueError(f'Original face #{face_id} has {len(solutions)} admissible three-quad partitions')
    diagonals=tuple((vertices[i],vertices[j]) for i,j in solutions[0][0])
    # Source ADVANCED_FACE orientation reverses the underlying PLANE normal.
    support_id=refs(entity(table,face_id,'ADVANCED_FACE')[1])[-1]
    placement_id=refs(entity(table,support_id,'PLANE')[1])[0]
    axis_id=refs(entity(table,placement_id,'AXIS2_PLACEMENT_3D')[1])[1]
    normal_raw=entity(table,axis_id,'DIRECTION')[1]
    match=COORDINATES.search(normal_raw)
    if match is None:raise ValueError('Source plane lacks a valid normal')
    source_normal=tuple(float(x) for x in match[1].split(','))
    face_raw=entity(table,face_id,'ADVANCED_FACE')[1]
    sign=1 if face_raw.strip().endswith('.T.') else -1 if face_raw.strip().endswith('.F.') else 0
    if not sign:raise ValueError('Original STEP face orientation invalid')
    intended=tuple(sign*x for x in source_normal)
    oriented_quads=[]
    for quad in solutions[0][1]:
        a,b,c,d=(coords[vertices.index(v)] for v in quad)
        u=tuple(b[i]-a[i] for i in range(3));v=tuple(d[i]-a[i] for i in range(3))
        normal=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        dot=sum(normal[i]*intended[i] for i in range(3))
        if abs(dot)<1e-8:raise ValueError('Degenerate original oriented quadrilateral')
        oriented_quads.append(tuple(quad if dot>0 else (quad[0],quad[3],quad[2],quad[1])))
    edge_by_corners={frozenset((e['start_vertex_id'],e['end_vertex_id'])):e['edge_curve_id'] for e in wire}
    return {'face_id':face_id,'vertices':vertices,'edge_ids':[e['edge_curve_id'] for e in wire],
            'quad_vertices':tuple(oriented_quads),'diagonals':diagonals,'edge_by_corners':edge_by_corners,
            'planar_area_mm2':polygon.area,'coords':dict(zip(vertices,coords)), 'polygon':polygon}


def _canonical_keys(table, part, va, vb):
    boundary_id=part['edge_by_corners'].get(frozenset((va,vb)))
    if boundary_id is not None:
        original=refs(entity(table,boundary_id,'EDGE_CURVE')[1]);
        if (va,vb)==tuple(original[:2]):
            return (f'vertex:{va}',f'edge:{boundary_id}:1',f'edge:{boundary_id}:2',f'vertex:{vb}')
        if (va,vb)==tuple(original[:2][::-1]):
            return (f'vertex:{va}',f'edge:{boundary_id}:2',f'edge:{boundary_id}:1',f'vertex:{vb}')
        raise ValueError('Source EDGE_CURVE vertices differ from source wire')
    ends=tuple(sorted((va,vb)))
    if ends not in {tuple(sorted(d)) for d in part['diagonals']}:
        raise ValueError('Quad has a side not supported by an original edge or certified diagonal')
    ids=(f'internal:{part["face_id"]}:{ends[0]}:{ends[1]}:1',
         f'internal:{part["face_id"]}:{ends[0]}:{ends[1]}:2')
    if (va,vb)!=ends:
        ids=ids[::-1]
    return (f'vertex:{va}',*ids,f'vertex:{vb}')


def _coons_interior(edges):
    """Construct degree-three planar Coons control nets from indexed cubic boundary curves."""
    net=[[None]*4 for _ in range(4)]
    for c,pt in enumerate(edges[0]):net[0][c]=pt
    for r,pt in enumerate(edges[1]):net[r][3]=pt
    for c,pt in enumerate(reversed(edges[2])):net[3][c]=pt
    for r,pt in enumerate(reversed(edges[3])):net[r][0]=pt
    for r in (1,2):
        s=r/3
        for c in (1,2):
            t=c/3
            left=net[r][0];right=net[r][3]
            bottom=net[0][c];top=net[3][c]
            bilinear=tuple((1-s)*((1-t)*net[0][0][i]+t*net[0][3][i])+
                           s*((1-t)*net[3][0][i]+t*net[3][3][i]) for i in range(3))
            net[r][c]=tuple((1-t)*left[i]+t*right[i]+(1-s)*bottom[i]+s*top[i]-bilinear[i]
                            for i in range(3))
    return net


def build_extension(step: bytes, baseline_bp: bytes, baseline_manifest: dict,
                    registry_manifest: dict, *, budget_mm=BUDGET_MM):
    text=_check_pins(step,baseline_bp,baseline_manifest,registry_manifest,budget_mm)
    table=parse_entities(text)
    vertices,patches=read_bp(baseline_bp.decode('utf-8'))
    if len(patches)!=126 or len(vertices)!=1467:
        raise ValueError('Wrong frozen baseline patch/control cardinality')
    registry=dict(registry_manifest['original_global_source_key_to_control_index'])
    for key,index in registry.items():
        if not isinstance(index,int) or not 0<=index<len(vertices):
            raise ValueError('Original source registry has invalid global index')
    points=list(vertices);new_patches=[];parts={}
    old_adjacency=_edge_adjacency(patches)
    for face in FACE_IDS:
        part=_recover_partition(table,face)
        parts[face]=part
        if set(SOURCE_EDGES_SHARED[face]) != (set(part['edge_ids']) &
            {int(k.split(':')[1]) for k in registry if k.startswith('edge:')}):
            raise ValueError('Frozen previously represented STEP boundary set changed')
        for eid in SOURCE_EDGES_SHARED[face]:
            ends=refs(entity(table,eid,'EDGE_CURVE')[1])[:2]
            ids=(registry[f'vertex:{ends[0]}'],registry[f'edge:{eid}:1'],
                 registry[f'edge:{eid}:2'],registry[f'vertex:{ends[1]}'])
            if len(old_adjacency.get(tuple(sorted(ids)),[]))!=1:
                raise ValueError('Original shared STEP edge is not one unsplit open BP side')
        for local_patch,quad in enumerate(part['quad_vertices']):
            # Shapely polygonize yields counterclockwise XY; XZ maps to -Y normal.
            corners=quad
            sides=[(corners[i],corners[(i+1)%4]) for i in range(4)]
            side_keys=[_canonical_keys(table,part,*x) for x in sides]
            local_ids=[];local_xyz=[]
            for side in side_keys:
                sid=[];xyz=[]
                for k,key in enumerate(side):
                    if key not in registry:
                        if k in (0,3):
                            vid=int(key.split(':')[1]); pos=part['coords'][vid]
                        else:
                            p0=points[registry[side[0]]] if side[0] in registry else part['coords'][int(side[0].split(':')[1])]
                            p3=points[registry[side[3]]] if side[3] in registry else part['coords'][int(side[3].split(':')[1])]
                            pos=_lerp(p0,p3,k/3)
                        registry[key]=len(points);points.append(tuple(pos))
                    sid.append(registry[key]);xyz.append(points[registry[key]])
                local_ids.append(sid);local_xyz.append(xyz)
            net=_coons_interior(local_xyz)
            grid=[[None]*4 for _ in range(4)]
            for c,index in enumerate(local_ids[0]):grid[0][c]=index
            for r,index in enumerate(local_ids[1]):grid[r][3]=index
            for c,index in enumerate(reversed(local_ids[2])):grid[3][c]=index
            for r,index in enumerate(reversed(local_ids[3])):grid[r][0]=index
            for r in (1,2):
                for c in (1,2):
                    key=f'planar-interior:{face}:{local_patch}:{r}:{c}'
                    if key in registry:raise ValueError('Original interior source key collision')
                    registry[key]=len(points);points.append(net[r][c]);grid[r][c]=registry[key]
            new_patches.append(tuple(idx for row in grid for idx in row))
    joined_patches=patches+new_patches
    adjacency=_edge_adjacency(joined_patches)
    if len(joined_patches)!=132:
        raise ValueError('Expected six additional quadrilateral patches')
    if sum(len(v)==2 for v in adjacency.values())!=189 or sum(len(v)==1 for v in adjacency.values())!=150:
        raise ValueError('Original source conforming topology does not close')
    for face in FACE_IDS:
        for eid in SOURCE_EDGES_SHARED[face]:
            ends=refs(entity(table,eid,'EDGE_CURVE')[1])[:2]
            idx=[registry[f'vertex:{ends[0]}'],registry[f'edge:{eid}:1'],
                 registry[f'edge:{eid}:2'],registry[f'vertex:{ends[1]}']]
            if len(adjacency[tuple(sorted(idx))])!=2:
                raise ValueError('Source shared generator did not acquire two sides')
    body=_serialize(points,joined_patches)
    original_hash=sha256(baseline_bp).hexdigest()
    summary={'schema':'apmesh-s3t-original-s40-source-octagon-quads-v1',
             'source_sha256':sha256(step).hexdigest(),
             'baseline_bp_sha256':original_hash,
             'new_bp_sha256':sha256(body.encode('utf-8')).hexdigest(),
             'original_face_ids':list(FACE_IDS),
             'source_to_original_face_ids':{str(f):parts[f]['edge_ids'] for f in FACE_IDS},
             'source_quad_vertex_ids':{str(f):[list(q) for q in parts[f]['quad_vertices']] for f in FACE_IDS},
             'source_internal_diagonal_vertex_ids':{str(f):[list(d) for d in parts[f]['diagonals']] for f in FACE_IDS},
             'source_polygon_area_mm2':{str(f):parts[f]['planar_area_mm2'] for f in FACE_IDS},
             'shared_source_edge_curve_ids':{str(f):list(SOURCE_EDGES_SHARED[f]) for f in FACE_IDS},
             'previous_patches':126,'new_patches':6,'joined_patches':len(joined_patches),
             'previous_control_count':len(vertices),'joined_control_count':len(points),
             'global_two_sided_indexed_seams':189,'global_open_indexed_sides':150,
             'source_original_faces_represented':19,'source_original_faces_total':43,
             'source_inner_hole_retained':True,
             'original_s3r_prefix_patches_unmodified':True,
             'numerical_budget_mm':budget_mm,
             'original_adjacency_proof':'original EDGE_CURVE keys from frozen S3.P registry',
             'continuous_trim_hausdorff_certified':False,
             'apmesh_tri_quad_generation':'NOT_RUN','production_cpp_regression':'NOT_RUN'}
    return body,summary


def _eval_cubic(points, t):
    weights=((1-t)**3,3*t*(1-t)**2,3*t*t*(1-t),t**3)
    return tuple(sum(weights[i]*points[i][axis] for i in range(4)) for axis in range(3))


def audit_original(step: bytes, native, baseline_bp: bytes, baseline_manifest: dict,
                   registry_manifest: dict, joined_bp: str, receipt: dict):
    """Recompute original source partition, indexed BP, and trimmed native oracle."""
    regenerated,control=build_extension(step,baseline_bp,baseline_manifest,registry_manifest)
    if receipt != control or joined_bp != regenerated:
        raise ValueError('Original source, native-independent BP and receipt mismatch')
    text=step.decode('utf-8')
    mapping=full_correspondence(text,native)
    for face_id,expected in EXPECTED_NATIVE_FACE.items():
        if mapping['face_map'].get(face_id)!=expected:
            raise ValueError('Source/native face STEP mapping is not frozen')
    verts,patches=read_bp(joined_bp)
    src_v,src_p=read_bp(baseline_bp.decode('utf-8'))
    if verts[:len(src_v)]!=src_v or patches[:len(src_p)]!=src_p:
        raise ValueError('Native audit detected a changed original atlas prefix')
    stats={'native_interior_samples':0,'native_boundary_samples':0,
           'source_boundary_curve_samples':0,'max_planar_surface_distance_mm':0.0,
           'max_native_source_edge_distance_mm':0.0,
           'unique_source_native_edges':0}
    for rank,face_id in enumerate(FACE_IDS):
        face=native.Faces()[mapping['face_map'][face_id]]
        if face.geomType()!='PLANE' or len(face.Wires())!=1:
            raise ValueError('Wrong native trimmed planar face or unexpected hole')
        plane=BRepAdaptor_Surface(face.wrapped).Plane()
        native_normal=face.normalAt().toTuple()
        for patch in patches[126+rank*3:126+(rank+1)*3]:
            coords=[verts[i] for i in patch]
            e1=tuple(coords[3][i]-coords[0][i] for i in range(3))
            e2=tuple(coords[12][i]-coords[0][i] for i in range(3))
            cross=(e1[1]*e2[2]-e1[2]*e2[1],e1[2]*e2[0]-e1[0]*e2[2],
                   e1[0]*e2[1]-e1[1]*e2[0])
            if sum(cross[i]*native_normal[i] for i in range(3)) <= 0:
                raise ValueError('Source-backed patch orientation disagrees with native face')
            for row in range(1,10):
                v=row/10
                for col in range(1,10):
                    u=col/10
                    pt=surface(coords,u,v)
                    uv=ElSLib.Parameters_s(plane,gp_Pnt(*pt))
                    state=BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State()
                    if state!=TopAbs_IN:raise ValueError('Planar patch interior outside native trimmed face')
                    distance=plane.Distance(gp_Pnt(*pt))
                    stats['max_planar_surface_distance_mm']=max(stats['max_planar_surface_distance_mm'],distance)
                    stats['native_interior_samples']+=1
            for k in range(11):
                t=k/10
                for u,v in ((t,0.),(t,1.),(0.,t),(1.,t)):
                    pt=surface(coords,u,v)
                    uv=ElSLib.Parameters_s(plane,gp_Pnt(*pt))
                    state=BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State()
                    if state not in (TopAbs_IN,TopAbs_ON):
                        raise ValueError('Source planar patch boundary outside original trim')
                    stats['max_planar_surface_distance_mm']=max(
                        stats['max_planar_surface_distance_mm'],plane.Distance(gp_Pnt(*pt)))
                    stats['native_boundary_samples']+=1
        table=mapping['table']; part=_recover_partition(table,face_id)
        seen=set()
        for e in part['edge_ids']:
            original_edge=mapping['native_edges'][mapping['edge_map'][e]]
            if not original_edge.wrapped.IsSame(native.Edges()[mapping['edge_map'][e]].wrapped):
                raise ValueError('Original STEP edge differs from audited native BRep')
            if mapping['edge_map'][e] in seen:
                raise ValueError('Original face boundaries mapped to duplicate native edges')
            seen.add(mapping['edge_map'][e])
            adaptor=BRepAdaptor_Curve(original_edge.wrapped)
            first=adaptor.FirstParameter();last=adaptor.LastParameter()
            ee=refs(entity(table,e,'EDGE_CURVE')[1])[:2]
            curve_endpoints=[tuple(coordinates(table,z)) for z in ee]
            a=adaptor.Value(first);b=adaptor.Value(last)
            native_forward=_distance((a.X(),a.Y(),a.Z()),curve_endpoints[0]) < _distance((b.X(),b.Y(),b.Z()),curve_endpoints[0])
            idx=registry_manifest['original_global_source_key_to_control_index']
            own_keys=[f'vertex:{ee[0]}',f'edge:{e}:1',f'edge:{e}:2',f'vertex:{ee[1]}']
            # For previously unrepresented edges, identify the new side on the boundary
            # by exact original endpoint coordinates and per-source face ownership.
            matches=[]
            for patch in patches[126+rank*3:126+(rank+1)*3]:
                for side in ('bottom','top','left','right'):
                    ids=_side(patch,side)
                    start,end=(verts[ids[0]],verts[ids[-1]])
                    if (max(_distance(start,curve_endpoints[0]),_distance(end,curve_endpoints[1]))<INDEX_COORD_TOL_MM
                        or max(_distance(start,curve_endpoints[1]),_distance(end,curve_endpoints[0]))<INDEX_COORD_TOL_MM):
                        matches.append(ids)
            if len(matches)!=1:
                raise ValueError(f'Original STEP boundary #{e} has {len(matches)} matching indexed BP sides')
            ids=matches[0]
            net=[verts[i] for i in ids]
            reversed_net=_distance(net[0],curve_endpoints[0])>_distance(net[-1],curve_endpoints[0])
            if reversed_net:net=net[::-1]
            if e in SOURCE_EDGES_SHARED[face_id]:
                canonical=[idx[k] for k in own_keys]
                if tuple(ids)!=tuple(canonical) and tuple(ids)!=tuple(canonical[::-1]):
                    raise ValueError('Original source edge index identity was not preserved')
            for sample in range(11):
                t=sample/10
                pt=_eval_cubic(net,t)
                native_t=(first+t*(last-first)) if native_forward else (last-t*(last-first))
                target=adaptor.Value(native_t)
                d=_distance(pt,(target.X(),target.Y(),target.Z()))
                stats['max_native_source_edge_distance_mm']=max(stats['max_native_source_edge_distance_mm'],d)
                if d>STRICT_PLANAR_TOL_MM:
                    raise ValueError('Source/native original edge distance exceeds strict planar gate')
                stats['source_boundary_curve_samples']+=1
        stats['unique_source_native_edges']+=len(seen)
    if stats['max_planar_surface_distance_mm']>STRICT_PLANAR_TOL_MM:
        raise ValueError('Native plane deviation exceeded strict planar gate')
    return {'status':'PASS','source_step_face_ids':list(FACE_IDS),**stats,
            'strict_planar_tolerance_mm':STRICT_PLANAR_TOL_MM,
            'research_budget_mm':BUDGET_MM,
            'native_face_bijection_count':43,
            'native_edge_bijection_count':117,
            'native_vertex_bijection_count':77}


def cli():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-step',type=Path,required=True)
    parser.add_argument('--baseline-bp',type=Path,required=True)
    parser.add_argument('--baseline-manifest',type=Path,required=True)
    parser.add_argument('--source-registry-manifest',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--budget-mm',type=float,default=BUDGET_MM)
    args=parser.parse_args()
    source=args.source_step.read_bytes();bp=args.baseline_bp.read_bytes()
    manifest=json.loads(args.baseline_manifest.read_text('utf8'))
    registry=json.loads(args.source_registry_manifest.read_text('utf8'))
    joined,receipt=build_extension(source,bp,manifest,registry,budget_mm=args.budget_mm)
    native=cq.importers.importStep(str(args.source_step)).val()
    audit=audit_original(source,native,bp,manifest,registry,joined,receipt)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'s40_planar_octagons.partial.bp').write_text(joined,encoding='utf8')
    (args.output_dir/'s40_planar_octagons_manifest.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    (args.output_dir/'s40_planar_octagons_native_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'atlas_patches':receipt['joined_patches'], 'control_count':receipt['joined_control_count'], **audit},sort_keys=True))

if __name__=='__main__':cli()
