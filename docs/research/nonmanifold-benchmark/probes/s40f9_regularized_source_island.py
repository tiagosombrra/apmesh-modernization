#!/usr/bin/env python3
"""Repair the frozen F6 source-island corner folds with a submicron inward bias.

This constructs an isolated candidate, never a certified original STEP atlas.
The pinned F6 BP remains untouched. The output retains original STEP source-edge
lineage, all eight inherited S3.Y interface control chains, and patch indices.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math
import sys

import numpy as np
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.ElSLib import ElSLib
from OCP.TopAbs import TopAbs_IN, TopAbs_ON
from OCP.gp import gp_Pnt, gp_Pnt2d

import s40f5_original_source_analytic_pilot as f5
import s40f6_four_face_source_island as f6
import s40f8_exact_planar_jacobian as exact

F6_SHA = '72b8756c948a7a7da19c9f2a9a7099673e81a30573f19e4820abf27ba720f0a7'
F5_SPEC_SHA = '81c50cee156de79a10883643fa75da52b1c07a528ad0f06ad256156cf1fd9e7a'
F6_SPEC_SHA = '356d508c4b14f02bbc63f391e40128c41cdf0e170bfb219282594feaa792e671'
SOURCE_SHA = 'b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b'
INWARD_HANDLE_BIAS_MM = 0.0001
BUDGET_MM = 0.001
FACES = (1279,1279,1386,1386,3269,3269,3485,3485)
CIRCULAR_SOURCE_EDGES = (1307,1336,1415,1444)
PARENT_INTERFACE_SOURCE_KEYS = (
    'old:1002','old:1080','old:1139','old:1259',
    'old:1284','old:1473','new:1030:0','new:1057:0')


def read_pins(original_bp: bytes, original_receipt: dict,
              source_f5_spec: bytes, source_f6_spec: bytes):
    """Reject any replacement or incongruent private source before editing."""
    if sha256(original_bp).hexdigest()!=F6_SHA:
        raise ValueError('F6 frozen BP source digest mismatch')
    if sha256(source_f5_spec).hexdigest()!=F5_SPEC_SHA:
        raise ValueError('Pinned F5 source geometry digest mismatch')
    if sha256(source_f6_spec).hexdigest()!=F6_SPEC_SHA:
        raise ValueError('Pinned F6 source geometry digest mismatch')
    if (original_receipt.get('schema')!='apmesh-s40f6-four-source-face-isolated-bp-v1' or
        original_receipt.get('bp_sha256')!=F6_SHA or
        original_receipt.get('step_original_sha256_reference')!=SOURCE_SHA or
        tuple(original_receipt.get('face_ids_per_patch',()))!=FACES or
        original_receipt.get('parent_S3Y_joined') is not False or
        original_receipt.get('newly_admitted_original_source_faces')!=0):
        raise ValueError('Frozen source island manifest differs')
    old=exact.audit_f6(original_bp)
    rejected=[c['patch_index'] for c in old['certificates']
              if c['classification']!='CERTIFIED_STRICT_POSITIVE']
    if rejected!=[0,1,3]:
        raise ValueError('Previous exact-Jacobian evidence no longer reproduces')
    pts,patches=f6.read_indexed_bp(original_bp.decode('utf-8'))
    if (len(pts),len(patches))!=(104,8):
        raise ValueError('Incorrect frozen island structure')
    registry=original_receipt.get('source_segment_ids')
    if (not isinstance(registry,dict) or len(registry)!=20 or
        set(registry)!=set(original_receipt['indexed_audit']['source_boundary_segment_keys'])):
        raise ValueError('Original indexed source-edge registry incomplete')
    return pts,patches,registry


def _coons_interior_from_boundaries(points: list[tuple[float,...]], patch: tuple[int,...]):
    """Recompute interior controls while never changing an indexed patch edge."""
    grid=[[points[patch[4*r+c]] for c in range(4)] for r in range(4)]
    new={}
    for row in (1,2):
        v=row/3
        for col in (1,2):
            u=col/3
            left,right=grid[row][0],grid[row][3]
            bottom,top=grid[0][col],grid[3][col]
            tl,tr=grid[0][0],grid[0][3]
            bl,br=grid[3][0],grid[3][3]
            bilinear=tuple((1-v)*((1-u)*tl[k]+u*tr[k])+
                           v*((1-u)*bl[k]+u*br[k]) for k in range(3))
            new[patch[row*4+col]]=tuple(
                (1-u)*left[k]+u*right[k]+(1-v)*bottom[k]+v*top[k]-bilinear[k]
                for k in range(3))
    return new


def _indexed_side_audit(points,patches,registry):
    """Require source-registered open edges and reversed exact indexed seams."""
    users=defaultdict(list)
    for pid,patch in enumerate(patches):
        for name in ('bottom','right','top','left'):
            ids=f6.side_ids(patch,name)
            if len(ids)!=4 or len(set(ids))!=4:
                raise ValueError('Degenerate indexed boundary side')
            ccw=ids[::-1] if name in ('top','left') else ids
            users[tuple(sorted(ids))].append((pid,ids,ccw))
    if any(len(v)>2 for v in users.values()):
        raise ValueError('Three-plus indexed side incidence')
    closed=[u for u in users.values() if len(u)==2]
    open_=[u[0] for u in users.values() if len(u)==1]
    if (len(closed),len(open_))!=(6,20):
        raise ValueError('Indexed seams/open-side count changed')
    for a,b in closed:
        if a[2]!=b[2][::-1]:
            raise ValueError('Indexed seam orientation reversed incorrectly')
    if {tuple(sorted(x[1])) for x in open_}!={tuple(sorted(y)) for y in registry.values()}:
        raise ValueError('Original source edge registration incomplete')
    for index in range(len(points)):
        if not all(math.isfinite(x) for x in points[index]):
            raise ValueError('Nonfinite global control point')
    return {'two_sided_indexed_seams':6,'open_registered_source_sides':20,
            'reversed_two_sided_seams':True}


def regularize_frozen_f6(original_bp: bytes, original_receipt: dict,
                         source_f5_spec: bytes, source_f6_spec: bytes,
                         *, bias_mm=INWARD_HANDLE_BIAS_MM):
    """Move only source-circular handles and Coons interiors; preserve topology."""
    if bias_mm!=INWARD_HANDLE_BIAS_MM:
        raise ValueError('Experimental F9 inward bias cannot be relaxed or changed')
    old_points,patches,registry=read_pins(original_bp,original_receipt,
                                         source_f5_spec,source_f6_spec)
    f5_spec=json.loads(source_f5_spec)
    f6_spec=json.loads(source_f6_spec)
    if (f5_spec.get('origin_sha256')!=SOURCE_SHA or
        f6_spec.get('origin_sha256')!=SOURCE_SHA or
        set(map(int,f5_spec['faces']))!={1279,1386} or
        set(map(int,f6_spec['faces']))!={3269,3485}):
        raise ValueError('Source face data not from expected STEP')
    points=list(old_points)
    changed_handles=[]
    for face_id in (1279,1386):
        spec=f5_spec['faces'][str(face_id)]
        centers={int(k):v for k,v in spec['circle_centers'].items()}
        for eid,kind in spec['edges']:
            if kind!='CIRCLE':continue
            if eid not in CIRCULAR_SOURCE_EDGES:
                raise ValueError('Unknown circular STEP edge')
            chain=tuple(registry['old:'+str(eid)])
            if len(chain)!=4 or len(set(chain))!=4:
                raise ValueError('Source arc not a single cubic indexed side')
            center=tuple(centers[eid]); a=old_points[chain[0]]; b=old_points[chain[3]]
            for ctrl,endpoint in ((chain[1],a),(chain[2],b)):
                radial=tuple((center[k]-endpoint[k])/6 for k in range(3))
                if abs(sum(x*x for x in radial)-1)>1e-7:
                    raise ValueError('Source circular edge radius changed')
                points[ctrl]=tuple(old_points[ctrl][k]+bias_mm*radial[k] for k in range(3))
                changed_handles.append(ctrl)
    if len(changed_handles)!=8 or len(set(changed_handles))!=8:
        raise ValueError('Incomplete new circular source handles')
    changed_interiors=[]
    for patch in patches[:4]:
        for idx,pt in _coons_interior_from_boundaries(points,patch).items():
            points[idx]=pt
            changed_interiors.append(idx)
    if len(changed_interiors)!=16 or len(set(changed_interiors))!=16:
        raise ValueError('Incomplete four-face Coons control recomputation')
    edited=set(changed_handles)|set(changed_interiors)
    if any(points[i]!=old_points[i] for i in range(104) if i not in edited):
        raise ValueError('Original source vertex or inherited control changed')
    # Every published S3.Y interface remains numerically identical.
    for key in PARENT_INTERFACE_SOURCE_KEYS:
        for i in registry[key]:
            if points[i]!=old_points[i]:
                raise ValueError('Previously represented S3.Y source side altered')
    incidence=_indexed_side_audit(points,patches,registry)
    serialized='\n'.join([
        '// S40-F9 original STEP source-derived regularized private island; NOT joined to S3.Y',
        '// F6 byte-frozen parent remains untouched; submicron inward circle-handle bias',
        *('v '+' '.join(format(x,'.17g') for x in p) for p in points),
        *('p '+' '.join(map(str,patch)) for patch in patches)
    ])+'\n'
    return serialized,{'schema':'apmesh-s40f9-regularized-four-face-source-island-v1',
         'classification':'ISOLATED_ANALYTIC_CANDIDATE_NOT_ORIGINAL_NATIVE_ADMITTED',
         'source_original_sha256':SOURCE_SHA,'original_f6_bp_sha256':F6_SHA,
         'candidate_bp_sha256':sha256(serialized.encode()).hexdigest(),
         'patch_count':len(patches),'control_count':len(points),
         'unchanged_parent_interface_source_keys':list(PARENT_INTERFACE_SOURCE_KEYS),
         'source_segment_ids':registry,'face_ids_per_patch':list(FACES),
         'interior_original_source_vertex_ids_unchanged':True,
         'edited_circular_handle_control_ids':changed_handles,
         'recomputed_coons_interior_control_ids':changed_interiors,
         'fixed_inward_offset_mm':bias_mm,'original_f6_preserved_immutable':True,
         'source_indexed_incidence':incidence,'parent_s3y_joined':False,
         'original_step_native_import_executed':False,'source_faces_newly_admitted':0}


def _surface_approx_net(points,patch):
    """Convert indexed controls into a four-row source patch for OCCT checks."""
    return [[points[patch[4*j+i]] for i in range(4)] for j in range(4)]


def _surrogate_faces(f5_spec, f6_spec):
    """Construct actual OCCT face objects from pinned source-derived geometry."""
    loaded=f5.load_private_source_spec(f5_spec)
    native={}
    for fid in (1279,1386):
        native[fid]=f5.reconstruct_face(fid)[0]
    data=json.loads(Path(f6_spec).read_bytes())
    for fid in (3269,3485):
        raw=data['faces'][str(fid)]
        xyz=[cq.Vector(*p) for p in raw['coordinates']]
        edges=[cq.Edge.makeLine(xyz[i],xyz[(i+1)%len(xyz)]) for i in range(len(xyz))]
        face=cq.Face.makeFromWires(cq.Wire.assembleEdges(edges))
        if not face.isValid():
            raise ValueError('Invalid original-source reconstructed vertical face')
        normal=face.normalAt().toTuple()
        if sum(normal[k]*raw['plane_axis'][k] for k in range(3))<.99999:
            raise ValueError('Surrogate vertical face normal mismatch')
        native[fid]=face
    return native


def _oriented_jacobian(points,patch,unit,u,v):
    """Evaluate oriented Jacobian at one point without certification claims."""
    net=np.array(_surface_approx_net(points,patch))
    b=lambda t: np.array(((1-t)**3,3*t*(1-t)**2,3*t*t*(1-t),t**3))
    d=lambda t: np.array((-3*(1-t)**2,3*(1-t)**2-6*t*(1-t),6*t*(1-t)-3*t*t,3*t*t))
    du=np.einsum('i,j,ijc->c',b(v),d(u),net)
    dv=np.einsum('i,j,ijc->c',d(v),b(u),net)
    return float(np.dot(np.cross(du,dv),unit))


def audit_candidate(candidate_bp: bytes, original_bp: bytes, original_receipt: dict,
                    f5_source_spec_path: str | Path, f6_source_spec_path: str | Path,
                    *, density=15,boundary_density=51):
    """Require exact J, indexed seams and source-derived native-surrogate checks."""
    if density<5 or density>31 or boundary_density<11 or boundary_density>101:
        raise ValueError('Surrogate audit resolution changed outside protocol')
    f5_bytes=Path(f5_source_spec_path).read_bytes()
    f6_bytes=Path(f6_source_spec_path).read_bytes()
    regenerated,sidecar=regularize_frozen_f6(original_bp,original_receipt,f5_bytes,f6_bytes)
    if candidate_bp!=regenerated.encode():
        raise ValueError('Candidate BP differs from deterministic pinned source-based regeneration')
    points,patches=f6.read_indexed_bp(candidate_bp.decode())
    rat_points,rat_patches=exact.parse_decimal_bp(candidate_bp)
    if patches!=rat_patches:
        raise ValueError('Numerical and exact BP parsers disagree')
    original_points,orig_patches=f6.read_indexed_bp(original_bp.decode())
    if patches!=orig_patches:
        raise ValueError('Indexed patch control topology changed')
    strict=[]
    for pid,patch in enumerate(rat_patches):
        face_id=FACES[pid]
        net=exact.jacobian_net(rat_points,patch,exact.NORMALS[face_id])
        certificate=exact.certify_strict_sign(net,max_depth=12)
        if certificate['status']!='CERTIFIED_POSITIVE':
            raise ValueError(f'Original-source island patch {pid} is not strictly regular')
        strict.append({'patch_id':pid,'face_id':face_id,
                       'exact_decimal_jacobian_certificate':certificate})
    faces=_surrogate_faces(f5_source_spec_path,f6_source_spec_path)
    tally={str(fid):{'interior_IN':0,'boundary_IN_or_ON':0,'boundary_OUT':0,
                     'sampled_min_oriented_jacobian_mm2':float('inf'),
                     'integrated_area_mm2':0.,'native_surrogate_area_mm2':float(face.Area()),
                     'relative_area_difference':None}
           for fid,face in faces.items()}
    quad_u,weights=np.polynomial.legendre.leggauss(12)
    quad_u=(quad_u+1)/2;weights=weights/2
    for pid,patch in enumerate(patches):
        fid=FACES[pid];face=faces[fid]
        plane=BRepAdaptor_Surface(face.wrapped).Plane()
        unit=np.array(exact.NORMALS[fid],dtype=float)
        per=tally[str(fid)]
        net=_surface_approx_net(points,patch)
        for r in range(density):
            for c in range(density):
                pt=f5._point_surface(net,(c+.5)/density,(r+.5)/density)
                uv=ElSLib.Parameters_s(plane,gp_Pnt(*pt))
                if BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State()!=TopAbs_IN:
                    raise ValueError(f'Face #{fid} candidate interior not IN in reconstructed native-surrogate trim')
                per['interior_IN']+=1
        for label in ('bottom','right','top','left'):
            ids=f6.side_ids(patch,label)
            control=[points[x] for x in ids]
            for k in range(boundary_density):
                pt=f5._point_cubic(control,k/(boundary_density-1))
                uv=ElSLib.Parameters_s(plane,gp_Pnt(*pt))
                if BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State() in (TopAbs_IN,TopAbs_ON):
                    per['boundary_IN_or_ON']+=1
                else:
                    per['boundary_OUT']+=1
        for r,u in enumerate(quad_u):
            for c,v in enumerate(quad_u):
                jac=_oriented_jacobian(points,patch,unit,u,v)
                if jac<=0:
                    raise ValueError('Gaussian Jacobian unexpectedly non-positive')
                per['sampled_min_oriented_jacobian_mm2']=min(per['sampled_min_oriented_jacobian_mm2'],jac)
                per['integrated_area_mm2']+=weights[r]*weights[c]*jac
    for face_id in tally:
        per=tally[face_id]
        per['relative_area_difference']=abs(per['integrated_area_mm2']-per['native_surrogate_area_mm2'])/per['native_surrogate_area_mm2']
        if per['relative_area_difference']>1e-4 or per['boundary_OUT']:
            raise ValueError(f'Reconstructed original-source face #{face_id} area or trim mismatch')
    radial=[]
    f5_json=json.loads(f5_bytes)
    for fid in (1279,1386):
        circle_centers={int(e):p for e,p in f5_json['faces'][str(fid)]['circle_centers'].items()}
        for eid in CIRCULAR_SOURCE_EDGES:
            if eid not in circle_centers:continue
            chain=original_receipt['source_segment_ids']['old:'+str(eid)]
            curve=[points[i] for i in chain]
            cert=f5.exact_radial_bernstein_certificate(curve,circle_centers[eid])
            # The radial enclosure is continuous for the decimal-defined BP.
            if (cert['lower_radial_bound_mm']<6-BUDGET_MM or
                cert['upper_radial_bound_mm']>6+BUDGET_MM):
                raise ValueError('Bounded source circular deviation exceeds 0.001 mm')
            native_surrogate_edge=f5.reconstruct_face(fid)[1][eid]
            adaptor=BRepAdaptor_Curve(native_surrogate_edge.wrapped)
            low,high=adaptor.FirstParameter(),adaptor.LastParameter()
            if not (math.isfinite(low+high) and high>low):
                raise ValueError('Invalid reconstructed source-arc parameter domain')
            forward_dist=0.;reverse_dist=0.
            for sample in range(65):
                t=sample/64
                bp_point=f5._point_cubic(curve,t)
                def squared_to_edge(v):
                    return sum((x-y)**2 for x,y in zip(bp_point,adaptor.Value(low+(high-low)*v).Coord()))
                forward_dist=max(forward_dist,math.sqrt(f5._minimize_1d(squared_to_edge)))
                curve_point=adaptor.Value(low+(high-low)*t).Coord()
                def squared_to_bp(v):
                    return sum((x-y)**2 for x,y in zip(curve_point,f5._point_cubic(curve,v)))
                reverse_dist=max(reverse_dist,math.sqrt(f5._minimize_1d(squared_to_bp)))
            if max(forward_dist,reverse_dist)>=BUDGET_MM:
                raise ValueError('Bidirectional sampled edge-to-Bezier fit exceeds budget')
            radial.append({'source_edge_id':eid,
                           'max_sampled_bp_to_original_analytic_edge_mm':forward_dist,
                           'max_sampled_original_analytic_edge_to_bp_mm':reverse_dist,
                           'exact_float_input_radial_enclosure':cert})
    return {'classification':'STRICT_REGULARITY_AND_SOURCE_SURROGATE_PASS_NOT_ORIGINAL_STEP_NATIVE',
            'original_f6_bp_sha256':F6_SHA,
            'repaired_candidate_bp_sha256':sha256(candidate_bp).hexdigest(),
            'fixed_budget_mm':BUDGET_MM,'fixed_inward_control_handle_bias_mm':INWARD_HANDLE_BIAS_MM,
            'patches':len(patches),'global_controls':len(points),
            'strictly_positive_entire_domain_patch_count':len(strict),
            'continuous_exact_decimal_bernstein_proofs':strict,
            'native_surrogate_by_face':tally,
            'four_source_arc_radial_certificates':radial,
            'all_eight_parent_interface_source_chains_unchanged':True,
            'six_indexed_seams_reversed':True,
            'source_original_full_step_native_import':False,
            'joined_with_original_s3y':False,
            'new_source_faces_native_admitted':0,
            'apmesh_tri_quad_executed':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--f6-bp',type=Path,required=True)
    parser.add_argument('--f6-manifest',type=Path,required=True)
    parser.add_argument('--f5-source-spec',type=Path,required=True)
    parser.add_argument('--f6-source-spec',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    out=args.output_dir
    try:
        bp=args.f6_bp.read_bytes()
        receipt=json.loads(args.f6_manifest.read_bytes())
        source=args.f5_source_spec.read_bytes()
        vertical=args.f6_source_spec.read_bytes()
        candidate,manifest=regularize_frozen_f6(bp,receipt,source,vertical)
        audit=audit_candidate(candidate.encode(),bp,receipt,args.f5_source_spec,args.f6_source_spec)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as error:
        print(json.dumps({'classification':'BLOCKED_NO_ORIGINAL_NATIVE_ADMISSION',
                          'candidate_emitted':False,'error':type(error).__name__+': '+str(error),
                          'new_original_source_faces_admitted':0},sort_keys=True),file=sys.stderr)
        return 3
    out.mkdir(parents=True,exist_ok=True)
    (out/'s40f9_four_face_regularized.PRIVATE.bp').write_text(candidate)
    (out/'s40f9_private_candidate_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    (out/'s40f9_private_exact_and_surrogate_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'classification':audit['classification'],
                      'all_strictly_positive':audit['strictly_positive_entire_domain_patch_count']==8,
                      'new_original_step_faces_admitted':0,
                      'bp_sha256':audit['repaired_candidate_bp_sha256']},sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
