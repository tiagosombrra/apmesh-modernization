#!/usr/bin/env python3
"""Source-derived, standalone two-face Bézier research pilot for original S40.

This rebuilds exact analytic planar/line/circle entities identified in the pinned
STEP without importing the complete original STEP or claiming parent BP joins.
The outputs are independent native OCP surrogate faces, not original TopoDS faces.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import cadquery as cq
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.ElSLib import ElSLib
from OCP.TopAbs import TopAbs_IN, TopAbs_ON
from OCP.gp import gp_Pnt, gp_Pnt2d
from scipy.optimize import minimize_scalar

SOURCE_STEP_SHA256 = "b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b"
PRIVATE_SPEC_SHA256 = "81c50cee156de79a10883643fa75da52b1c07a528ad0f06ad256156cf1fd9e7a"
FIXED_BUDGET_MM = 0.001
CIRCLE_HANDLE_INWARD_OFFSET_MM = 0.0007
SOURCE_DATA = {}


def load_private_source_spec(path):
    """Load source-derived geometry kept outside the public research repository."""
    global SOURCE_DATA
    source_bytes=Path(path).read_bytes()
    if hashlib.sha256(source_bytes).hexdigest()!=PRIVATE_SPEC_SHA256:
        raise ValueError("Source-derived private specification SHA256 mismatch")
    raw=json.loads(source_bytes)
    if raw.get("schema")!="apmesh-s40f5-pinned-source-analytic-faces-v1" or raw.get("origin_sha256")!=SOURCE_STEP_SHA256:
        raise ValueError("Unpinned source analytic specification")
    ids={int(k) for k in raw["faces"]}
    if ids!={1279,1386}:raise ValueError("Source face identifiers changed")
    parsed={}
    for fid,body in raw["faces"].items():
        body["circle_centers"]={int(k):v for k,v in body["circle_centers"].items()}
        parsed[int(fid)]=body
    SOURCE_DATA=parsed
    return SOURCE_DATA


def _distance(a, b):
    return math.dist(a, b)


def _point_cubic(net, u):
    v = 1-u
    w = (v**3, 3*u*v*v, 3*u*u*v, u**3)
    return tuple(sum(w[i]*net[i][k] for i in range(4)) for k in range(3))


def _line_cubic(p, q):
    return (p, tuple((2*p[i]+q[i])/3 for i in range(3)),
            tuple((p[i]+2*q[i])/3 for i in range(3)), q)


def _unit(vector):
    L = math.sqrt(sum(x*x for x in vector))
    if not L or not math.isfinite(L):
        raise ValueError("Degenerate analytic circle vector")
    return tuple(x/L for x in vector)


def _circle_angles(p, q, c):
    a = math.atan2(p[1]-c[1], p[0]-c[0])
    b = math.atan2(q[1]-c[1], q[0]-c[0])
    # STEP axis is (0,0,-1); the intended bounded arcs traverse clockwise.
    while b > a:
        b -= 2*math.pi
    sweep = a-b
    if not 0 < sweep < math.pi:
        raise ValueError(f"Source arc has unexpected sweep: {sweep}")
    return a, b, sweep


def _circle_cubic_inward(p, q, center, *, inset=CIRCLE_HANDLE_INWARD_OFFSET_MM):
    a, b, sweep = _circle_angles(p, q, center)
    radius = 6.
    if abs(math.hypot(p[0]-center[0], p[1]-center[1])-radius) > 1e-7:
        raise ValueError("Source circle start outside pinned radius")
    if abs(math.hypot(q[0]-center[0], q[1]-center[1])-radius) > 1e-7:
        raise ValueError("Source circle end outside pinned radius")
    if abs(sweep-math.pi/4) > 1e-7:
        raise ValueError("Source arc differs from pinned 45-degree sweep")
    handle = 4*radius*math.tan(sweep/4)/3 - inset
    if not 0 < handle < radius:
        raise ValueError("Invalid inward control handle")
    # Tangent for decreasing polar angle is (-dy, dx) with sign reversed.
    t0 = _unit((p[1]-center[1], -(p[0]-center[0]), 0.))
    t1 = _unit((q[1]-center[1], -(q[0]-center[0]), 0.))
    c1 = tuple(p[k]+handle*t0[k] for k in range(3))
    c2 = tuple(q[k]-handle*t1[k] for k in range(3))
    middle_angle = (a+b)/2
    middle = (center[0]+radius*math.cos(middle_angle),
              center[1]+radius*math.sin(middle_angle), center[2])
    edge = cq.Edge.makeThreePointArc(cq.Vector(*p), cq.Vector(*middle), cq.Vector(*q))
    return (p, c1, c2, q), edge


def reconstruct_face(face_id):
    if face_id not in SOURCE_DATA:
        raise ValueError("Unknown original source face")
    data = SOURCE_DATA[face_id]
    verts=data["coordinates"]
    curves={}; source_edges={}; physical=[]
    for i, (eid, kind) in enumerate(data["edges"]):
        p, q=verts[i],verts[(i+1)%6]
        if kind=="LINE":
            controls=_line_cubic(p,q)
            edge=cq.Edge.makeLine(cq.Vector(*p),cq.Vector(*q))
        elif kind=="CIRCLE":
            controls,edge=_circle_cubic_inward(p,q,data["circle_centers"][eid])
        else:
            raise ValueError("Unsupported source master curve")
        curves[eid]=controls;source_edges[eid]=edge;physical.append(edge)
    wire=cq.Wire.assembleEdges(physical)
    face=cq.Face.makeFromWires(wire)
    if not face.isValid() or not wire.isValid():
        raise ValueError("Source-derived analytic face is not a valid trimmed BRep")
    face_normal=face.normalAt().toTuple()
    pinned_axis=data["plane_axis"]
    if sum(face_normal[i]*pinned_axis[i] for i in range(3))<0.999999:
        raise ValueError("Source-derived face normal differs from original STEP support")
    if _distance(face.Center().toTuple(),data["coordinates"][0]) < 1:
        raise ValueError("Degenerate source-derived face")
    return face,source_edges,curves


def build_face_patches(face_id):
    face,source_edges,curves=reconstruct_face(face_id)
    coords=SOURCE_DATA[face_id]["coordinates"]
    index_by_edge={ (i,(i+1)%6):eid for i,(eid,_) in enumerate(SOURCE_DATA[face_id]["edges"])}
    def make_patch(quad):
        sides=[]
        for a,b in zip(quad,quad[1:]+quad[:1]):
            if (a,b) in index_by_edge: sides.append(curves[index_by_edge[(a,b)]])
            elif (b,a) in index_by_edge: sides.append(tuple(reversed(curves[index_by_edge[(b,a)]])))
            elif frozenset((a,b))==frozenset((0,3)):sides.append(_line_cubic(coords[a],coords[b]))
            else:raise ValueError("Unrecognized patch edge")
        net=[[None]*4 for _ in range(4)]
        for i,p in enumerate(sides[0]):net[0][i]=p
        for i,p in enumerate(sides[1]):net[i][3]=p
        for i,p in enumerate(reversed(sides[2])):net[3][i]=p
        for i,p in enumerate(reversed(sides[3])):net[i][0]=p
        for i in (1,2):
            v=i/3
            for j in (1,2):
                u=j/3
                L,R,B,T=net[i][0],net[i][3],net[0][j],net[3][j]
                bilinear=[(1-v)*((1-u)*net[0][0][k]+u*net[0][3][k])+
                           v*((1-u)*net[3][0][k]+u*net[3][3][k]) for k in range(3)]
                net[i][j]=tuple((1-u)*L[k]+u*R[k]+(1-v)*B[k]+v*T[k]-bilinear[k] for k in range(3))
        return tuple(tuple(x for x in row) for row in net),sides
    return face,source_edges,curves,[make_patch([0,1,2,3]),make_patch([0,3,4,5])]



def exact_radial_bernstein_certificate(net, center, *, radius=6,
                                       max_depth=16, max_nodes=4096):
    """Bound float-defined cubic radial distance over the whole curve domain.

    Exact rational arithmetic applies only to the supplied IEEE-754 control
    coordinates, not to the original STEP kernel or the CAD trim classifier.
    """
    if len(net)!=4 or len(center)!=3:
        raise ValueError('Invalid radial certificate input')
    frac=lambda x:Fraction.from_float(float(x))
    q=[[frac(net[i][k])-frac(center[k]) for k in (0,1)] for i in range(4)]
    coefficients=[]
    for k in range(7):
        coefficient=Fraction(0)
        for i in range(4):
            j=k-i
            if not 0<=j<=3:continue
            product=sum(q[i][axis]*q[j][axis] for axis in range(2))
            coefficient+=Fraction(math.comb(3,i)*math.comb(3,j),math.comb(6,k))*product
        coefficients.append(coefficient)
    R=Fraction(radius);eps=Fraction(1,1000)
    lo,hi=(R-eps)**2,(R+eps)**2
    # A separate radial near-interior envelope supports the planar trim tests.
    near_upper=(R+Fraction(1,10000000))**2
    def split_mid(poly):
        levels=[poly]
        while len(levels[-1])>1:
            previous=levels[-1]
            levels.append([(previous[i]+previous[i+1])/2 for i in range(len(previous)-1)])
        return ([level[0] for level in levels],
                [level[-1] for level in reversed(levels)])
    seen=0;worst_min=None;worst_max=None;stack=[(coefficients,0)]
    while stack:
        coeff,depth=stack.pop();seen+=1
        if seen>max_nodes:
            raise ValueError('Rational certificate resource cap exceeded')
        minimum=min(coeff);maximum=max(coeff)
        if minimum>=lo and maximum<=hi and maximum<=near_upper:
            if worst_min is None or minimum<worst_min:worst_min=minimum
            if worst_max is None or maximum>worst_max:worst_max=maximum
            continue
        if depth>=max_depth:
            raise ValueError('Rational radial support remains inconclusive')
        left,right=split_mid(coeff)
        stack.extend(((left,depth+1),(right,depth+1)))
    return {'status':'RATIONAL_FLOAT_INPUT_SUPPORT_PASS',
            'visited_subintervals':seen,
            'lower_radial_bound_mm':math.sqrt(float(worst_min)),
            'upper_radial_bound_mm':math.sqrt(float(worst_max)),
            'continuous_float_defined_radial_support_only':True,
            'original_step_face_coverage_certified':False}

def _point_surface(net, u, v):
    bu=((1-u)**3,3*(1-u)**2*u,3*(1-u)*u*u,u**3)
    bv=((1-v)**3,3*(1-v)**2*v,3*(1-v)*v*v,v**3)
    return tuple(sum(bv[j]*bu[i]*net[j][i][k] for i in range(4) for j in range(4)) for k in range(3))


def _area_quadrature(net, intervals=12):
    x,w=np.polynomial.legendre.leggauss(intervals)
    grid=(x+1)/2;weight=w/2
    def derivative_weights(t):
        return (-3*(1-t)**2, 3*(1-t)**2-6*t*(1-t), 6*t*(1-t)-3*t*t, 3*t*t)
    def b(t):return ((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t,t**3)
    alln=np.array(net)
    a=0.;minimum=float('inf');maximum=float('-inf')
    for i,v in enumerate(grid):
        for j,u in enumerate(grid):
            du=np.einsum('i,j,ijc->c',b(v),derivative_weights(u),alln)
            dv=np.einsum('i,j,ijc->c',derivative_weights(v),b(u),alln)
            jac=float(np.cross(du,dv)[2])
            minimum=min(minimum,jac);maximum=max(maximum,jac)
            a+=weight[i]*weight[j]*abs(jac)
    return a,minimum,maximum


def _minimize_1d(f):
    xs=np.linspace(0,1,65)
    ys=[f(float(t)) for t in xs]
    idx=int(np.argmin(ys));a=max(0,(idx-1)/64);b=min(1,(idx+1)/64)
    opt=minimize_scalar(f,bounds=(a,b),method='bounded',options={'xatol':1e-12})
    return min(ys[idx],float(f(opt.x)))


def audit_face(face_id, *, interior_grid=15, boundary_grid=51, arc_samples=257):
    face,source_edges,curves,patches=build_face_patches(face_id)
    plane=BRepAdaptor_Surface(face.wrapped).Plane()
    native_positive=face.normalAt().toTuple()
    inside=boundary=out=0;gaps=[];orient=[];patch_areas=[]
    for net,sides in patches:
        for i in range(interior_grid):
            for j in range(interior_grid):
                pt=_point_surface(net,(i+0.5)/interior_grid,(j+0.5)/interior_grid)
                uv=ElSLib.Parameters_s(plane,gp_Pnt(*pt))
                state=BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State()
                if state!=TopAbs_IN:
                    raise ValueError(f"Interior sample OUT of source-derived face #{face_id}: {state}")
                inside+=1
        for side in sides:
            for i in range(boundary_grid):
                pt=_point_cubic(side,i/(boundary_grid-1))
                uv=ElSLib.Parameters_s(plane,gp_Pnt(*pt))
                state=BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State()
                if state in (TopAbs_IN,TopAbs_ON):boundary+=1
                else:out+=1
        a,mn,mx=_area_quadrature(net)
        patch_areas.append(a);orient.append((mn,mx))
    if out:raise ValueError(f"Source-derived face #{face_id} has {out} boundary OUT samples")
    if not all(mn<0 and mx<0 for mn,mx in orient):
        raise ValueError("Sampled patch orientation inconsistent with original -Z normal")
    area=float(face.Area());appr=sum(patch_areas)
    if abs(appr-area)/area>1e-4:
        raise ValueError(f"Source-derived native area mismatched: {appr} vs {area}")
    # Validate internal diagonal as the same oriented patch curve.
    diagonal1=patches[0][1][3]
    diagonal2=patches[1][1][0]
    if diagonal1!=tuple(reversed(diagonal2)):
        raise ValueError("Artificial diagonal is not shared with reverse orientation")
    for eid,kind in SOURCE_DATA[face_id]['edges']:
        if kind!="CIRCLE":continue
        controls=curves[eid];edge=source_edges[eid]
        c=BRepAdaptor_Curve(edge.wrapped)
        lo,hi=c.FirstParameter(),c.LastParameter()
        # Bidirectional sampled Hausdorff-type audit, not a continuous theorem.
        target_to_approx=0.;approx_to_target=0.
        for i in range(arc_samples):
            t=i/(arc_samples-1)
            pt=_point_cubic(controls,t)
            def target_distance(x):return sum((a-b)**2 for a,b in zip(pt,c.Value(lo+(hi-lo)*x).Coord()))
            approx_to_target=max(approx_to_target,math.sqrt(_minimize_1d(target_distance)))
            xyz=c.Value(lo+(hi-lo)*t).Coord()
            def approx_distance(x):return sum((a-b)**2 for a,b in zip(xyz,_point_cubic(controls,x)))
            target_to_approx=max(target_to_approx,math.sqrt(_minimize_1d(approx_distance)))
        if max(target_to_approx,approx_to_target)>FIXED_BUDGET_MM:
            raise ValueError(f"Circle #{eid} exceeds original budget")
        radial=exact_radial_bernstein_certificate(controls,SOURCE_DATA[face_id]['circle_centers'][eid])
        gaps.append({'edge':eid,'max_sampled_curve_to_bp_mm':target_to_approx,
                     'max_sampled_bp_to_curve_mm':approx_to_target,
                     'exact_radial_float_input_certificate':radial})
    return {'source_face_id':face_id,'state':'SOURCE_ANALYTIC_SURROGATE_PASS',
            'native_step_import':False,'source_geometry_canonical_ids':list(x for x,_ in SOURCE_DATA[face_id]['edges']),
            'source_face_reference_sha256':SOURCE_STEP_SHA256,
            'bezier_patch_count':2,'native_surrogate_area_mm2':area,
            'sampled_gauss_bp_area_mm2':appr,
            'relative_area_difference':abs(appr-area)/area,
            'native_surrogate_interior_IN_samples':inside,
            'native_surrogate_boundary_IN_ON_samples':boundary,
            'native_surrogate_boundary_OUT_samples':out,
            'sampled_patch_jacobian_range':orient,'sampled_arc_errors':gaps,
            'continuous_native_STEP_or_hausdorff_certified':False,
            'source_analytic_surrogate_only':True,
            'candidate_parent_bp_joined':False}



def build_indexed_surrogate():
    """Create a standalone BP with true indexed internal seams, not S3.Y joins.

    Every original source edge is separately registered by source EDGE_CURVE ID.
    The private user may later map inherited edges to the old 156-patch atlas.
    """
    if set(SOURCE_DATA)!={1279,1386}:
        raise ValueError("Unverified source analytic specification")
    vertices=[]; patches=[]; vertex_ids={}; edge_controls={}; internal_seams={}
    patch_face_ids=[]
    def append(x):
        index=len(vertices)
        if not all(math.isfinite(float(t)) for t in x):
            raise ValueError("Invalid BP control")
        vertices.append(tuple(float(t) for t in x))
        return index
    for fid in sorted(SOURCE_DATA):
        d=SOURCE_DATA[fid]
        native, native_edges, curves, generated=build_face_patches(fid)
        source_vertices=d['vertices']
        for j,source_id in enumerate(source_vertices):
            if source_id in vertex_ids:
                if vertices[vertex_ids[source_id]]!=tuple(d['coordinates'][j]):
                    raise ValueError("Original STEP vertex reused with different coordinates")
            else:
                vertex_ids[source_id]=append(d['coordinates'][j])
        for j,(eid,kind) in enumerate(d['edges']):
            a=vertex_ids[source_vertices[j]];b=vertex_ids[source_vertices[(j+1)%6]]
            if eid in edge_controls:raise ValueError("Duplicate source EDGE_CURVE identity")
            net=curves[eid]
            edge_controls[eid]=(a,append(net[1]),append(net[2]),b)
        diag=(0,3)
        a=vertex_ids[source_vertices[0]];b=vertex_ids[source_vertices[3]]
        key=f'face:{fid}:original_source_vertex_diagonal:0-3'
        internal_seams[key]=(a,append(_line_cubic(vertices[a],vertices[b])[1]),
                             append(_line_cubic(vertices[a],vertices[b])[2]),b)
        edge_lookup={(j,(j+1)%6):eid for j,(eid,kind) in enumerate(d['edges'])}
        for quad,original in zip(((0,1,2,3),(0,3,4,5)),generated):
            outer=[]
            for i in range(4):
                x,y=quad[i],quad[(i+1)%4]
                if (x,y) in edge_lookup:ids=edge_controls[edge_lookup[x,y]]
                elif (y,x) in edge_lookup:ids=tuple(reversed(edge_controls[edge_lookup[y,x]]))
                elif (x,y)==diag:ids=internal_seams[key]
                elif (y,x)==diag:ids=tuple(reversed(internal_seams[key]))
                else:raise ValueError('Unidentified source/diagonal boundary')
                outer.append(ids)
            matrix=[[None]*4 for _ in range(4)]
            for col,k in enumerate(outer[0]):matrix[0][col]=k
            for row,k in enumerate(outer[1]):matrix[row][3]=k
            for col,k in enumerate(reversed(outer[2])):matrix[3][col]=k
            for row,k in enumerate(reversed(outer[3])):matrix[row][0]=k
            for row in (1,2):
                for col in (1,2):
                    idx=append(original[0][row][col])
                    matrix[row][col]=idx
            flat=tuple(k for row in matrix for k in row)
            for row in range(4):
                for col in range(4):
                    p=vertices[matrix[row][col]];q=original[0][row][col]
                    if _distance(p,q)>1e-12:
                        raise ValueError('Indexed patch differs from independently built Coons patch')
            patches.append(flat);patch_face_ids.append(fid)
    sides=defaultdict(list)
    def side(net,name):
        return tuple({'bottom':net[:4],'right':net[3::4],
                      'top':net[12:16],'left':net[::4]}[name])
    for pid,patch in enumerate(patches):
        for label in ('bottom','right','top','left'):
            edge=side(patch,label)
            sides[tuple(sorted(edge))].append((pid,label,edge))
    internal=[users for users in sides.values() if len(users)==2]
    opens=[users[0] for users in sides.values() if len(users)==1]
    if len(patches)!=4 or len(vertices)!=56 or len(internal)!=2 or len(opens)!=12:
        raise ValueError('Indexed pilot incidence cardinality changed')
    if any(len(users)>2 for users in sides.values()):
        raise ValueError('Unsupported nonmanifold indexed side')
    for users in internal:
        (a,na,ia),(b,nb,ib)=users
        # Convert raw net edge orders to CCW perimeter orders.
        oa=ia[::-1] if na in ('top','left') else ia
        ob=ib[::-1] if nb in ('top','left') else ib
        if oa!=ob[::-1] or patch_face_ids[a]!=patch_face_ids[b]:
            raise ValueError('Indexed internal seam direction/face identity mismatch')
    indexed_edges={tuple(sorted(ids)):eid for eid,ids in edge_controls.items()}
    if set(tuple(sorted(ids)) for _,_,ids in opens)!=set(indexed_edges):
        raise ValueError('Pilot has an open side without original STEP edge identity')
    serialized='\n'.join([
        '// S40-F5 original-source-derived standalone bicubic analytical pilot; not a joined S3.Y atlas',
        '// BP control nets are private STEP derivatives; no production meshing claim',
        *('v '+' '.join(format(x,'.17g') for x in p) for p in vertices),
        *('p '+' '.join(map(str,net)) for net in patches)])+'\n'
    sidecar={'state':'ISOLATED_SOURCE_ANALYTIC_NOT_S3Y_ADMITTED',
             'source_STEP_sha256_pinned':SOURCE_STEP_SHA256,
             'bp_sha256':hashlib.sha256(serialized.encode()).hexdigest(),
             'patches':len(patches),'global_control_points':len(vertices),
             'two_sided_internal_seams':len(internal),'open_source_edges':len(opens),
             'source_edge_control_id_chains':{str(k):list(v) for k,v in edge_controls.items()},
             'original_source_face_per_patch':patch_face_ids,
             'explicit_indexed_parent_S3Y_joins':0,
             'source_faces_counted_as_admitted':0}
    return serialized,sidecar

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    parser.add_argument('--source-spec',required=True)
    parser.add_argument('--isolated-bp',required=True)
    args=parser.parse_args()
    load_private_source_spec(args.source_spec)
    reports=[audit_face(fid) for fid in sorted(SOURCE_DATA)]
    serialized,sidecar=build_indexed_surrogate()
    Path(args.isolated_bp).parent.mkdir(parents=True,exist_ok=True)
    Path(args.isolated_bp).write_text(serialized)
    receipt={'schema':'apmesh-s40f5-source-analytic-standalone-v1',
             'source_file_sha256':SOURCE_STEP_SHA256,
             'faces':reports,'indexed_candidate':sidecar,'newly_admitted_original_faces':0,
             'frozen_original_s3y_atlas':{'patches':156,'faces':22,'controls':1665}}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'state':'SOURCE_ANALYTIC_SURROGATE_PASS',
                      'faces':[(v['source_face_id'],v['bezier_patch_count']) for v in reports],
                      'admitted_new_faces':0},sort_keys=True))


if __name__=='__main__':main()
