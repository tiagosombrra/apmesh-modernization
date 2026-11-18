#!/usr/bin/env python3
"""Build a private, source-indexed four-face S40 Bézier island without parent joins.

F5 face geometry and its exact indexed BP are preserved numerically. Two new
five-LINE source faces receive one explicitly registered source-edge subdivision
and exactly two convex quadrilateral patches each. This is an isolated pilot;
original native STEP admission and production meshing remain separate gates.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.ElSLib import ElSLib
from OCP.TopAbs import TopAbs_IN, TopAbs_ON
from OCP.gp import gp_Pnt, gp_Pnt2d
from shapely.geometry import Polygon
from shapely.ops import unary_union

import s40f5_original_source_analytic_pilot as f5

SOURCE_SHA = f5.SOURCE_STEP_SHA256
F5_BP_SHA = '2fd7d00234aea44aefdca4fce12f8dd8b2e9397122c366ed025c77bff714810d'
F6_SPEC_SHA = '356d508c4b14f02bbc63f391e40128c41cdf0e170bfb219282594feaa792e671'
F6_SCHEMA = 'apmesh-s40f6-pinned-source-five-line-vertical-faces-v1'
EXPECTED_EDGES = {3269: (3273, 1392, 1057, 813, 3299),
                  3485: (3489, 1497, 1030, 1365, 3515)}
F5_SHARED = {3269: 1392, 3485: 1365}
FROZEN_S3Y_EDGES = {3269: (1057,), 3485: (1030,)}
GEOMETRIC_BUDGET_MM = 0.001


def load_f6_spec(path):
    """Accept only the byte-locked source-derived private geometry specification."""
    contents = Path(path).read_bytes()
    if hashlib.sha256(contents).hexdigest() != F6_SPEC_SHA:
        raise ValueError('Private source-derived F6 specification hash mismatch')
    data = json.loads(contents)
    if data.get('schema') != F6_SCHEMA or data.get('origin_sha256') != SOURCE_SHA:
        raise ValueError('Incorrect original STEP or F6 source specification schema')
    if set(data['faces']) != {'3269', '3485'}:
        raise ValueError('Unexpected original face inventory')
    result = {}
    for key, raw in data['faces'].items():
        fid = int(key)
        if (raw['support_type'] != 'PLANE' or len(raw['vertices']) != 5 or
                len(set(raw['vertices'])) != 5 or len(raw['coordinates']) != 5 or
                len(raw['edges']) != 5 or
                tuple(e[0] for e in raw['edges']) != EXPECTED_EDGES[fid] or
                any(e[1] != 'LINE' for e in raw['edges']) or
                raw['shared_f5_source_edge'] != F5_SHARED[fid] or
                tuple(raw['prior_s3y_source_edges']) != FROZEN_S3Y_EDGES[fid]):
            raise ValueError('Original source face provenance changed')
        axis = tuple(float(v) for v in raw['plane_axis'])
        loc = tuple(float(v) for v in raw['plane_location'])
        xyz = [tuple(float(q) for q in p) for p in raw['coordinates']]
        if (not all(math.isfinite(q) for p in xyz for q in p) or
                not all(math.isfinite(q) for q in axis + loc) or
                abs(sum(q*q for q in axis) - 1) > 1e-12):
            raise ValueError('Nonfinite or malformed original plane')
        if any(abs(sum((p[i] - loc[i]) * axis[i] for i in range(3))) > 1e-8 for p in xyz):
            raise ValueError('STEP source vertex outside declared original support plane')
        result[fid] = raw
    return result


def read_indexed_bp(source):
    """Parse the independent indexed BP grammar with strict global references."""
    points, patches = [], []
    for no, line in enumerate(source.splitlines(), 1):
        line = line.split('//', 1)[0].strip()
        if not line:
            continue
        fields = line.split()
        if fields[0] == 'v' and len(fields) == 4:
            xyz = tuple(float(v) for v in fields[1:])
            if not all(math.isfinite(x) for x in xyz):
                raise ValueError('Nonfinite BP control')
            points.append(xyz)
        elif fields[0] == 'p' and len(fields) == 17:
            ids = tuple(int(v) for v in fields[1:])
            if any(v < 0 or v >= len(points) for v in ids):
                raise ValueError('Invalid forward or out-of-bounds indexed BP control')
            patches.append(ids)
        else:
            raise ValueError(f'Invalid BP line {no}')
    if not patches:
        raise ValueError('Empty BP')
    return points, patches


def side_ids(patch, name):
    """Extract raw row-major control orders from a bicubic patch."""
    return tuple({'bottom': patch[0:4], 'right': patch[3::4],
                  'top': patch[12:16], 'left': patch[::4]}[name])


def original_vertex_registry(points, f5_sidecar):
    """Bind original STEP vertex IDs, never coordinate proximity, to BP IDs."""
    lookup = {}
    for fid, body in f5.SOURCE_DATA.items():
        for j, source_id in enumerate(body['vertices']):
            # The edge ID and original source order, not a coordinate search,
            # identify the existing global point index.
            edge_id = str(body['edges'][j][0])
            ids = f5_sidecar['source_edge_control_id_chains'][edge_id]
            candidate = ids[0]
            expected = tuple(float(x) for x in body['coordinates'][j])
            if points[candidate] != expected:
                raise ValueError('Existing original vertex/control identity mismatch')
            if source_id in lookup and lookup[source_id] != candidate:
                raise ValueError('Source vertex aliases distinct global IDs')
            lookup[source_id] = candidate
    return lookup


def _signed_cross(a, b, c):
    return (b[0]-a[0])*(c[1]-b[1]) - (b[1]-a[1])*(c[0]-b[0])


def _project(p):
    """Use the native YZ chart on original X-constant vertical support planes."""
    return (p[1], p[2])


def _is_strictly_convex_quad(poly, orientation, *, epsilon=1e-9):
    values = [_signed_cross(poly[i], poly[(i+1) % 4], poly[(i+2) % 4])
              for i in range(4)]
    return all(orientation * v > epsilon for v in values)


def select_source_split(body, *, excluded_source_edges):
    """Find a two-quad split without touching already indexed source interfaces.

    The split is placed on a whole original pending LINE EDGE_CURVE. Each
    candidate is checked against polygon coverage and strict quad convexity.
    """
    original = [_project(x) for x in body['coordinates']]
    polygon = Polygon(original)
    if not polygon.is_valid or polygon.area <= 1e-5:
        raise ValueError('Original source pentagon is invalid')
    signed = sum(x[0]*original[(i+1) % 5][1] -
                 original[(i+1) % 5][0]*x[1] for i, x in enumerate(original)) / 2
    if abs(signed) < 1e-5:
        raise ValueError('Original source face has zero oriented area')
    orientation = 1 if signed > 0 else -1
    proposals = []
    for split_at, (eid, kind) in enumerate(body['edges']):
        if eid in excluded_source_edges:
            continue
        if kind != 'LINE':
            raise ValueError('A source curved EDGE_CURVE cannot be implicitly split')
        pts = [tuple(x) for x in body['coordinates']]
        a, b = pts[split_at], pts[(split_at + 1) % 5]
        mid = tuple((x+y)/2 for x,y in zip(a,b))
        pts.insert(split_at + 1, mid)
        uv = [_project(p) for p in pts]
        for start in range(3):
            first = tuple((start+j) % 6 for j in range(4))
            second = tuple((start+3+j) % 6 for j in range(4))
            axy = [uv[j] for j in first]
            bxy = [uv[j] for j in second]
            if not (_is_strictly_convex_quad(axy, orientation) and
                    _is_strictly_convex_quad(bxy, orientation)):
                continue
            poly_a, poly_b = Polygon(axy), Polygon(bxy)
            union = unary_union((poly_a, poly_b))
            if (union.geom_type != 'Polygon' or
                    abs(poly_a.area+poly_b.area-polygon.area) > 1e-7 or
                    abs(union.area - polygon.area) > 1e-7 or
                    union.symmetric_difference(polygon).area > 1e-7):
                continue
            def aspect(q):
                edges = [math.dist(q[j], q[(j+1) % 4]) for j in range(4)]
                return max(edges)/min(edges)
            score = max(aspect(axy),aspect(bxy))
            proposals.append((score, eid, start, split_at, pts, first, second))
    if not proposals:
        raise ValueError('No conforming two-quad partition respecting source interfaces')
    proposals.sort(key=lambda x: (x[0],x[1],x[2]))
    score, eid, start, split_at, pts, first, second = proposals[0]
    return {'split_edge_id': eid, 'split_edge_position': split_at,
            'virtual_source_midpoint': pts[split_at+1],
            'expanded_points': pts, 'quads': (first, second),
            'objective_max_side_aspect_ratio': score,
            'source_original_face_area': polygon.area}


def cubic_line(a, b):
    return (a, tuple((2*a[k]+b[k])/3 for k in range(3)),
            tuple((a[k]+2*b[k])/3 for k in range(3)), b)


def coons_indexed(points, sides, append):
    """Create interior controls with boundary IDs reused verbatim."""
    net = [[None]*4 for _ in range(4)]
    for col, idx in enumerate(sides[0]):net[0][col]=idx
    for row, idx in enumerate(sides[1]):net[row][3]=idx
    for col, idx in enumerate(reversed(sides[2])):net[3][col]=idx
    for row, idx in enumerate(reversed(sides[3])):net[row][0]=idx
    for row in (1,2):
        v=row/3
        for col in (1,2):
            u=col/3
            left,right=points[net[row][0]],points[net[row][3]]
            bottom,top=points[net[0][col]],points[net[3][col]]
            tl,tr=points[net[0][0]],points[net[0][3]]
            bl,br=points[net[3][0]],points[net[3][3]]
            bilinear=[(1-v)*((1-u)*tl[k]+u*tr[k])+v*((1-u)*bl[k]+u*br[k]) for k in range(3)]
            q=tuple((1-u)*left[k]+u*right[k]+(1-v)*bottom[k]+v*top[k]-bilinear[k]
                    for k in range(3))
            net[row][col]=append(q)
    return tuple(idx for row in net for idx in row)


def _directed_side(patch,name):
    ids=side_ids(patch,name)
    return ids[::-1] if name in ('top','left') else ids


def audit_global_incidence(points, patches, patch_faces, source_sides, expected_internal):
    """Check all old/new seams, including CCW reversal and source-boundary lineage."""
    incident = defaultdict(list)
    for i, patch in enumerate(patches):
        if len(patch)!=16 or any(j<0 or j>=len(points) for j in patch):
            raise ValueError('Invalid indexed patch')
        for name in ('bottom','right','top','left'):
            ids=side_ids(patch,name)
            key=tuple(sorted(ids))
            incident[key].append({'pid':i,'name':name,'ids':ids,
                                  'ccw':_directed_side(patch,name)})
    if any(len(users)>2 for users in incident.values()):
        raise ValueError('Unexpected 3+-incident or duplicated indexed BP side')
    internal=[v for v in incident.values() if len(v)==2]
    open_sides=[v[0] for v in incident.values() if len(v)==1]
    if len(internal)!=expected_internal:
        raise ValueError('Indexed internal/source seam count differs from construction contract')
    for a,b in internal:
        if a['ccw']!=b['ccw'][::-1]:
            raise ValueError('Shared indexed seam has inconsistent CCW orientation')
    registered={tuple(sorted(ids)):key for key,ids in source_sides.items()}
    if len(registered)!=len(source_sides):
        raise ValueError('Duplicate exact source indexed side was declared')
    if len(open_sides)!=len(registered):
        raise ValueError('Some original source side remains unregistered')
    if any(tuple(sorted(x['ids'])) not in registered for x in open_sides):
        raise ValueError('An open side has no original STEP source-edge segment identity')
    for side in open_sides:
        source_key=registered[tuple(sorted(side['ids']))]
        if source_key.startswith('new:') and side['pid']<4:
            raise ValueError('New source edge was used by previous accepted F5 patch')
    return {'patches':len(patches),'declared_global_controls':len(points),
            'two_sided_seams':len(internal),'open_source_indexed_sides':len(open_sides),
            'source_boundary_segment_keys':sorted(source_sides),
            'all_internal_seams_ccw_reversed':True}


def native_surrogate_audit(body, selected, points, patches, *, density=15, boundary_density=51):
    """Check native surrogate trim and planar oriented Jacobian, not original STEP."""
    source=[cq.Vector(*p) for p in body['coordinates']]
    edges=[cq.Edge.makeLine(source[i],source[(i+1)%5]) for i in range(5)]
    face=cq.Face.makeFromWires(cq.Wire.assembleEdges(edges))
    if not face.isValid():
        raise ValueError('Original-source-reconstructed pentagon invalid in OCCT')
    unit=tuple(body['plane_axis'])
    normal=face.normalAt().toTuple()
    if sum(a*b for a,b in zip(unit,normal))<0.999999:
        raise ValueError('Original source face plane normal or vertex order changed')
    plane=BRepAdaptor_Surface(face.wrapped).Plane()
    inside=on_or_in=outside=0;min_jac=float('inf');max_jac=float('-inf')
    from numpy.polynomial.legendre import leggauss
    xx,ww=leggauss(12);xx=(xx+1)/2;ww=ww/2
    def b(t):return ((1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3)
    def d(t):return (-3*(1-t)**2,3*(1-t)**2-6*t*(1-t),6*t*(1-t)-3*t*t,3*t*t)
    calculated_area=0.
    for patch in patches:
        coord=[points[i] for i in patch]
        net=np.asarray(coord).reshape((4,4,3))
        for a in range(density):
            for c in range(density):
                p=f5._point_surface(net,(a+0.5)/density,(c+0.5)/density)
                uv=ElSLib.Parameters_s(plane,gp_Pnt(*p))
                state=BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State()
                if state!=TopAbs_IN:raise ValueError('New patch interior OUT of source-reconstructed native face')
                inside+=1
        for name in ('bottom','right','top','left'):
            chain=side_ids(patch,name)
            for k in range(boundary_density):
                p=f5._point_cubic([points[j] for j in chain],k/(boundary_density-1))
                uv=ElSLib.Parameters_s(plane,gp_Pnt(*p))
                state=BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State()
                if state in (TopAbs_IN,TopAbs_ON):on_or_in+=1
                else:outside+=1
        for i,u in enumerate(xx):
            for j,v in enumerate(xx):
                du=np.einsum('i,j,ijc->c',b(v),d(u),net)
                dv=np.einsum('i,j,ijc->c',d(v),b(u),net)
                jac=float(np.dot(np.cross(du,dv),unit))
                min_jac=min(min_jac,jac);max_jac=max(max_jac,jac)
                if jac<=1e-10:
                    raise ValueError('Source-reconstructed patch has wrong Jacobian sign')
                calculated_area+=float(ww[i]*ww[j]*jac)
    area=face.Area()
    if outside or abs(calculated_area-area)>1e-6*area:
        raise ValueError('New indexed quad region fails native surrogate coverage/area')
    return {'surrogate_face_area':area,'integrated_bp_area':calculated_area,
            'absolute_area_difference':abs(calculated_area-area),
            'interior_IN':inside,'boundary_IN_ON':on_or_in,'boundary_OUT':outside,
            'minimum_oriented_jacobian':min_jac,'maximum_oriented_jacobian':max_jac,
            'sampled_only':True,'original_full_STEP_imported':False}


def build_four_face_island(f5_spec, f6_spec):
    """Run the two source-derived gates and preserve frozen F5 indexed prefix."""
    f5.load_private_source_spec(f5_spec)
    f6=load_f6_spec(f6_spec)
    old_bp,sidecar=f5.build_indexed_surrogate()
    if hashlib.sha256(old_bp.encode('utf-8')).hexdigest()!=F5_BP_SHA:
        raise ValueError('Frozen original S40-F5 parent BP bytes differ')
    points,patches=read_indexed_bp(old_bp)
    if len(points)!=56 or len(patches)!=4:
        raise ValueError('Incorrect original F5 indexed cardinality')
    previous_points=tuple(points);previous_patches=tuple(patches)
    src_vertex=original_vertex_registry(points,sidecar)
    source_sides={'old:'+key:tuple(value) for key,value in
                  sidecar['source_edge_control_id_chains'].items()}
    new_patch_faces=[1279,1279,1386,1386]
    new_report={};declared_edge_owners={}
    def append(p):
        pt=tuple(float(x) for x in p)
        if not all(math.isfinite(x) for x in pt):raise ValueError('Nonfinite candidate control')
        idx=len(points);points.append(pt);return idx
    for fid,body in sorted(f6.items()):
        side_by_original={int(k):tuple(v) for k,v in sidecar['source_edge_control_id_chains'].items()}
        for j,v in enumerate(body['vertices']):
            coords=tuple(body['coordinates'][j])
            if v in src_vertex:
                if points[src_vertex[v]]!=coords:raise ValueError('An original STEP vertex changes coordinates at F5/F6 interface')
            else:src_vertex[v]=append(coords)
        skip=set([body['shared_f5_source_edge'],*body['prior_s3y_source_edges']])
        selected=select_source_split(body,excluded_source_edges=skip)
        split_id=selected['split_edge_id'];split_at=selected['split_edge_position']
        virt=append(selected['virtual_source_midpoint'])
        expanded_source_ids=list(body['vertices'])
        expanded_source_ids.insert(split_at+1,('source_edge_mid',split_id))
        local_to_global=[]
        for ident in expanded_source_ids:
            local_to_global.append(virt if isinstance(ident,tuple) else src_vertex[ident])
        source_boundary=[];split_seen=0
        for j,(eid,kind) in enumerate(body['edges']):
            source_boundary.append((eid,0))
            if eid==split_id:
                source_boundary.append((eid,1));split_seen+=1
        if split_seen!=1 or len(source_boundary)!=6:
            raise ValueError('Original STEP source boundary split count mismatch')
        edge_lookup={}
        for j,(eid,segment) in enumerate(source_boundary):
            a,b=local_to_global[j],local_to_global[(j+1)%6]
            if eid in side_by_original:
                if segment!=0 or eid==split_id:
                    raise ValueError('Previously indexed source edge cannot be subdivided')
                old=side_by_original[eid]
                if (a,b)==(old[0],old[-1]):ids=old
                elif (a,b)==(old[-1],old[0]):ids=old[::-1]
                else:raise ValueError('Inherited original source edge has mismatched endpoint IDs')
                if (eid==body['shared_f5_source_edge']) != (eid in F5_SHARED.values()):
                    raise ValueError('Unexpected reused source-edge owner')
                # The formerly open F5 source side becomes paired at this face.
                source_sides.pop('old:'+str(eid), None)
            else:
                c=cubic_line(points[a],points[b])
                ids=(a,append(c[1]),append(c[2]),b)
            key=f'new:{eid}:{segment}'
            # Source segments already present in F5 must retain their old keys.
            if eid not in side_by_original:source_sides[key]=ids
            edge_lookup[(j,(j+1)%6)]=ids
            declared_edge_owners[(fid,eid,segment)]=(a,b)
        quads=selected['quads']
        da,db=quads[0][0],quads[0][3]
        # The common diagonal is the (first vertex, fourth vertex) of q1.
        left,right=local_to_global[da],local_to_global[db]
        diagonal=cubic_line(points[left],points[right])
        diag_ids=(left,append(diagonal[1]),append(diagonal[2]),right)
        face_new=[]
        for quad in quads:
            sides=[]
            for u,v in zip(quad,quad[1:]+quad[:1]):
                if (u,v) in edge_lookup:
                    ids=edge_lookup[(u,v)]
                elif (v,u) in edge_lookup:
                    ids=edge_lookup[(v,u)][::-1]
                elif (local_to_global[u],local_to_global[v])==(left,right):
                    ids=diag_ids
                elif (local_to_global[u],local_to_global[v])==(right,left):
                    ids=diag_ids[::-1]
                else:
                    raise ValueError('New patch boundary unregistered or nonconforming')
                sides.append(ids)
            patch=coons_indexed(points,sides,append)
            face_new.append(patch);patches.append(patch);new_patch_faces.append(fid)
        stats=native_surrogate_audit(body,selected,points,face_new)
        new_report[str(fid)]={'split_source_edge_id':split_id,
                              'split_source_edge_segments':2,
                              'quadrilaterals':len(face_new),
                              'partition_max_side_aspect_ratio':selected['objective_max_side_aspect_ratio'],
                              'source_pentagon_area_2d':selected['source_original_face_area'],
                              'native_surrogate_audit':stats,
                              'shared_prior_f5_source_edge_id':F5_SHARED[fid],
                              'unsplit_prior_s3y_source_edges':list(FROZEN_S3Y_EDGES[fid])}
    if (tuple(points[:56])!=previous_points or tuple(patches[:4])!=previous_patches):
        raise ValueError('Prior four-patch source F5 pilot was changed')
    incidence=audit_global_incidence(points,patches,new_patch_faces,source_sides,6)
    if len(patches)!=8 or len(points)!=104 or incidence['open_source_indexed_sides']!=20:
        raise ValueError('Final four-face source island cardinality unexpected')
    blob='\n'.join([
        '// S40-F6 original-source-derived private four-face island, NOT S3.Y joined',
        '// Third-party-derived BP controls remain in private research package',
        *('v '+' '.join(format(x,'.17g') for x in p) for p in points),
        *('p '+' '.join(str(i) for i in patch) for patch in patches)])+'\n'
    receipt={'schema':'apmesh-s40f6-four-source-face-isolated-bp-v1',
             'step_original_sha256_reference':SOURCE_SHA,
             'f5_original_bp_sha256':F5_BP_SHA,
             'f6_source_private_spec_sha256':F6_SPEC_SHA,
             'new_reconstructed_faces':new_report,
             'face_ids_per_patch':new_patch_faces,
             'source_segment_ids':source_sides,
             'bp_sha256':hashlib.sha256(blob.encode('utf-8')).hexdigest(),
             'indexed_audit':incidence,
             'original_step_native_import':False,
             'parent_S3Y_joined':False,
             'newly_admitted_original_source_faces':0,
             'continuous_cad_coverage_certified':False,
             'apmesh_tri_quad_executed':False}
    return blob,receipt


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--f5-source-spec',required=True)
    cli.add_argument('--f6-source-spec',required=True)
    cli.add_argument('--output-dir',required=True)
    args=cli.parse_args()
    bp,receipt=build_four_face_island(args.f5_source_spec,args.f6_source_spec)
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/'s40f6_four_face_source_island.PRIVATE.bp').write_text(bp)
    (out/'s40f6_source_island.PRIVATE.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'state':'ISOLATED_SOURCE_ANALYTIC_FOUR_FACE_NOT_ADMITTED',
                      'patches':receipt['indexed_audit']['patches'],
                      'controls':receipt['indexed_audit']['declared_global_controls'],
                      'source_faces':[1279,1386,3269,3485],
                      'source_faces_newly_admitted_to_S3Y':0},sort_keys=True))


if __name__=='__main__':main()
