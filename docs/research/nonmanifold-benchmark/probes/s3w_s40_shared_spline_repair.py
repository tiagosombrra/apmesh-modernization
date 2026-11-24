#!/usr/bin/env python3
"""S3.W: source-canonical two-sided repair of original S40 spline seams.

This bounded research pilot adjusts only the 30 already shared interior cubic
control IDs of source edges #85 and #2096. It does not fit independent curves,
change native CAD, relax the fixed geometric budget, or change APMesh C++.
All modified original-derived control coordinates remain private.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import argparse
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.spatial import cKDTree
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.ElSLib import ElSLib
from OCP.TopAbs import TopAbs_IN, TopAbs_ON, TopAbs_OUT
from OCP.gp import gp_Pnt, gp_Pnt2d

from audit_analytic_bp import read_bp, surface
from s3c_step_source_gate import parse_entities
from s3i_joint_source_atlas import _serialize
from s3q_s40_hole_preserving_island import source_partition
from s3r_s40_conforming_hole_join import _edge_adjacency, _side
from s3s_full_original_face_census import full_correspondence
from s3v_s40_curved_planar_closure import (
    BASELINE_SHA, BUDGET_MM, EXPECTED_NATIVE, SOURCE_SHA,
    _normal, _source_edge_closest, audit_native as audit_s3v,
    build_extension, source_boundary_sides, verify_source_and_atlas,
)

ORIGINAL_S3V_CANDIDATE_SHA = 'ba18b866fd70d25b8b9b116354c2673c0294efc6dba8e1e7dca48e8d6536070d'
# This is a control-point displacement, NOT a changed geometric error budget.
CONTROL_BIAS_MM = 0.0011
FIXED_BUDGET_MM = 0.001
INWARD_PROBE_MM = 0.01
SPLINE_SEAMS = ((17, 85, 1519, 12), (2092, 2096, 2457, 22))
EXPECTED_AFFECTED_OLD_PATCHES = (64, 66, 68, 70, 72, 74, 76, 88, 89, 90, 91, 92, 93, 94, 95)
EXPECTED_GLOBAL_SEAMS = 239
EXPECTED_OPEN_SIDES = 114


def _unit(v):
    length = math.sqrt(sum(x*x for x in v))
    if length < 1e-15:
        raise ValueError('Degenerate original cubic boundary tangent')
    return tuple(x/length for x in v)


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1],
            a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def _curve_point(points, ids, t):
    w = ((1-t)**3, 3*t*(1-t)**2, 3*t*t*(1-t), t**3)
    return tuple(sum(w[j]*points[ids[j]][axis] for j in range(4)) for axis in range(3))


def _state_on_plane(native_face, point):
    plane = BRepAdaptor_Surface(native_face.wrapped).Plane()
    uv = ElSLib.Parameters_s(plane, gp_Pnt(*point))
    return BRepClass_FaceClassifier(native_face.wrapped, gp_Pnt2d(*uv), 1e-7).State()


def _source_seams(face_id, edge_id, table, points, patches):
    adjacency = _edge_adjacency(patches)
    return [ids for eid, ids in source_boundary_sides(face_id, table, points, patches, adjacency)
            if eid == edge_id]


def _bias_shared_controls(source, previous_bp, previous_manifest, native, *,
                          bias_mm=CONTROL_BIAS_MM, budget_mm=FIXED_BUDGET_MM):
    """Return the sole source-identified control mutation and its audit lineage."""
    if bias_mm != CONTROL_BIAS_MM or budget_mm != FIXED_BUDGET_MM:
        raise ValueError('Declared displacement or original geometry budget was modified')
    table, previous_points, previous_patches = verify_source_and_atlas(
        source, previous_bp, previous_manifest, budget_mm)
    candidate, predecessor = build_extension(source, previous_bp, previous_manifest, native)
    if sha256(candidate.encode()).hexdigest() != ORIGINAL_S3V_CANDIDATE_SHA:
        raise ValueError('Frozen unadmitted S3.V candidate differs from its exact source lineage')
    points, patches = read_bp(candidate)
    if (len(points), len(patches)) != (1619, 148) or points[:1527] != previous_points:
        raise ValueError('Unexpected original candidate BP indexing')
    changed = set()
    seam_details = {}
    old_points = tuple(points)
    for original_face_id, edge_id, cylinder_source_face, cylinder_native_id in SPLINE_SEAMS:
        native_plane = native.Faces()[EXPECTED_NATIVE[original_face_id]]
        if native_plane.geomType() != 'PLANE':
            raise ValueError('Original planar source owner is no longer a plane')
        normal = native_plane.normalAt().toTuple()
        segments = _source_seams(original_face_id, edge_id, table, previous_points, previous_patches)
        if len(segments) != (7 if edge_id == 85 else 8):
            raise ValueError('Changed original source spline segmentation')
        for side in segments:
            if len(side) != 4:
                raise ValueError('Malformed cubic source side')
            for j in (1, 2):
                control = side[j]
                if control in changed or control >= 1527 or control in (side[0],side[-1]):
                    raise ValueError('Shared original source control is ambiguous')
                t = j/3
                pa = _curve_point(old_points, side, t-1e-4)
                pb = _curve_point(old_points, side, t+1e-4)
                tangent = _unit(tuple(pb[k]-pa[k] for k in range(3)))
                inward = _unit(_cross(normal, tangent))
                midpoint = _curve_point(old_points, side, .5)
                plus = tuple(midpoint[k]+INWARD_PROBE_MM*inward[k] for k in range(3))
                minus = tuple(midpoint[k]-INWARD_PROBE_MM*inward[k] for k in range(3))
                plus_in = _state_on_plane(native_plane, plus) == TopAbs_IN
                minus_in = _state_on_plane(native_plane, minus) == TopAbs_IN
                if plus_in == minus_in:
                    raise ValueError('Original native trim inward direction is ambiguous')
                if minus_in:
                    inward = tuple(-x for x in inward)
                old = old_points[control]
                points[control] = tuple(old[k]+bias_mm*inward[k] for k in range(3))
                changed.add(control)
        seam_details[str(edge_id)] = {
            'source_planar_face': original_face_id,
            'source_cylindrical_face': cylinder_source_face,
            'original_native_cylinder_index': cylinder_native_id,
            'source_piece_count': len(segments),
            'shared_interior_controls_modified': 2*len(segments),
            'source_endpoints_unchanged': True,
        }
    if len(changed) != 30:
        raise ValueError('Expected exactly thirty changed shared source controls')
    # Compare every affected source patch; do not conceal old-net modifications.
    affected = tuple(k for k, patch in enumerate(previous_patches)
                     if any(idx in changed for idx in patch))
    if affected != EXPECTED_AFFECTED_OLD_PATCHES:
        raise ValueError('Unexpected historic source patch is affected by the repair')
    if any(idx in changed for patch in patches[96:126] for idx in patch):
        raise ValueError('Original STEP #218 inner hole lineage was changed')
    adj = _edge_adjacency(patches)
    two = sum(len(x)==2 for x in adj.values())
    one = sum(len(x)==1 for x in adj.values())
    if (two,one) != (EXPECTED_GLOBAL_SEAMS,EXPECTED_OPEN_SIDES):
        raise ValueError('Global indexed edge conformity was lost')
    result = _serialize(points,patches)
    receipt = {
        'schema':'apmesh-s3w-original-s40-coordinated-spline-repair-v1',
        'classification':'BOUNDED_ORIGINAL_CAD_SCIENTIFIC_PILOT',
        'source_sha256':SOURCE_SHA,
        'baseline_s3t_bp_sha256':BASELINE_SHA,
        'original_s3v_candidate_sha256':ORIGINAL_S3V_CANDIDATE_SHA,
        'repaired_bp_sha256':sha256(result.encode()).hexdigest(),
        'shared_control_displacement_mm':CONTROL_BIAS_MM,
        'unchanged_original_geometric_budget_mm':BUDGET_MM,
        'modified_existing_original_patches':list(affected),
        'modified_shared_original_control_count':30,
        'unchanged_original_patch_count':117,
        'original_step_218_hole_patch_ids_unchanged':True,
        'new_original_face_ids':[17,2092],
        'original_faces_represented_if_native_admitted':21,
        'source_original_face_count':43,
        'combined_patches':148,
        'global_declared_control_points':1619,
        'two_sided_global_control_seams':two,
        'open_indexed_sides':one,
        'original_source_spline_edges':seam_details,
        'independently_native_checked':False,
        'formal_directed_rounding_proof':False,
        'apmesh_cpp_tri_quad':'NOT_RUN',
        'production_cpp_regression':'NOT_RUN',
    }
    return result, receipt


# Bernstein product weights for the radial squared-distance bi-degree (6, 6).
_PRODUCT_WEIGHTS = [[math.comb(3,i)*math.comb(3,j)/math.comb(6,i+j)
                     for j in range(4)] for i in range(4)]


def radial_squared_tensor_net(net, native_cylinder):
    """Build Bernstein coefficients of squared radial residual over [0,1]^2."""
    origin=native_cylinder.Location()
    axis=native_cylinder.Axis().Direction()
    o=np.array((origin.X(),origin.Y(),origin.Z()),dtype=np.float64)
    d=np.array((axis.X(),axis.Y(),axis.Z()),dtype=np.float64)
    p=np.asarray(net,dtype=np.float64).reshape(4,4,3)
    offsets=p-o
    radial=offsets-(offsets@d)[...,None]*d
    coefficients=np.zeros((7,7),dtype=np.float64)
    for i in range(4):
        for j in range(4):
            for a in range(4):
                for b in range(4):
                    coefficients[i+a,j+b] += (_PRODUCT_WEIGHTS[i][a] * _PRODUCT_WEIGHTS[j][b] *
                        float(radial[i,j]@radial[a,b]))
    coefficients -= native_cylinder.Radius()**2
    return coefficients


def _bisect_bernstein(net, axis):
    block=np.moveaxis(net,axis,0)
    levels=[block]
    while len(levels[-1])>1:
        levels.append((levels[-1][:-1]+levels[-1][1:])/2)
    left=np.stack([v[0] for v in levels])
    right=np.stack([v[-1] for v in reversed(levels)])
    return np.moveaxis(left,0,axis),np.moveaxis(right,0,axis)


def bound_bicubic_cylinder_radial_mm(net, cylinder, *, budget_mm=BUDGET_MM,
                                     depth_limit=12, guard_mm=1e-9):
    """Float-guarded tensor Bernstein full-support bound, not interval proof."""
    if budget_mm!=BUDGET_MM or not isinstance(depth_limit,int) or not 0<=depth_limit<=12:
        raise ValueError('Modified original numeric budget or invalid depth limit')
    pending=[(radial_squared_tensor_net(net,cylinder),0)]
    max_bound=0.0;leaves=0;deepest=0
    radius=cylinder.Radius()
    while pending:
        coefficients,depth=pending.pop()
        qmin=float(coefficients.min());qmax=float(coefficients.max())
        if radius*radius+qmin<0:
            raise ValueError('Invalid or degenerate radial polynomial')
        lo=math.sqrt(radius*radius+qmin);hi=math.sqrt(radius*radius+qmax)
        bound=max(abs(radius-lo),abs(radius-hi))+guard_mm
        if bound<=budget_mm or depth==depth_limit:
            max_bound=max(max_bound,bound);leaves+=1;deepest=max(deepest,depth)
        else:
            x,y=_bisect_bernstein(coefficients,depth%2)
            pending.extend(((x,depth+1),(y,depth+1)))
    return {'upper_mm':max_bound,'pass':max_bound<=budget_mm,
            'subdivided_leaves':leaves,'deepest_bisection':deepest}


def _native_cylinder_state(face, point):
    cylinder=BRepAdaptor_Surface(face.wrapped).Cylinder()
    uv=ElSLib.Parameters_s(cylinder,gp_Pnt(*point))
    state=BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State()
    return state,cylinder


def _analytic_cylinder_distance(cylinder, point):
    axis=cylinder.Axis().Direction();origin=cylinder.Location()
    d=(axis.X(),axis.Y(),axis.Z());o=(origin.X(),origin.Y(),origin.Z())
    displacement=tuple(point[i]-o[i] for i in range(3))
    z=sum(displacement[i]*d[i] for i in range(3))
    return abs(math.sqrt(sum((displacement[i]-z*d[i])**2 for i in range(3)))-cylinder.Radius())


def _cubic_derivatives(net,u,v,delta=1e-5):
    du=tuple((surface(net,u+delta,v)[i]-surface(net,u-delta,v)[i])/(2*delta)
             for i in range(3))
    dv=tuple((surface(net,u,v+delta)[i]-surface(net,u,v-delta)[i])/(2*delta)
             for i in range(3))
    return _cross(du,dv)


def _closest_source_curve_samples(curve, samples):
    """Dense sampled curve-to-native estimates via nearest-parameter minimization."""
    lo,hi=curve.FirstParameter(),curve.LastParameter()
    if not (math.isfinite(lo+hi) and hi>lo):
        raise ValueError('Invalid original native B-spline parameter bounds')
    pars=np.linspace(lo,hi,4097)
    native=np.array([(curve.Value(float(t)).X(),curve.Value(float(t)).Y(),curve.Value(float(t)).Z())
                     for t in pars])
    tree=cKDTree(native)
    distances=[]
    for pos in samples:
        p=np.array(pos)
        _,nearest=tree.query(p)
        left=float(pars[max(0,nearest-3)]);right=float(pars[min(len(pars)-1,nearest+3)])
        def squared(parameter):
            q=curve.Value(float(parameter))
            return float(np.sum((p-np.array((q.X(),q.Y(),q.Z())))**2))
        opt=minimize_scalar(squared,bounds=(left,right),method='bounded',options={'xatol':1e-13})
        distances.append(math.sqrt(max(0.0,min(squared(opt.x),squared(left),squared(right)))))
    return max(distances)


def sampled_bicubic_area_mm2(net, native_normal, *, quadrature_order=10):
    """Integrate positive patch Jacobians; this is not a coverage theorem."""
    nodes,weights=np.polynomial.legendre.leggauss(quadrature_order)
    nodes=(nodes+1)/2
    weights=weights/2
    area=0.0
    min_signed_jacobian=float('inf')
    for i,u in enumerate(nodes):
        for j,v in enumerate(nodes):
            vec=_cubic_derivatives(net,float(u),float(v))
            signed=sum(vec[k]*native_normal[k] for k in range(3))
            if signed<=0:
                raise ValueError('New source planar patch has a folded or inverted Jacobian')
            min_signed_jacobian=min(min_signed_jacobian,signed)
            area+=float(weights[i]*weights[j])*math.sqrt(sum(t*t for t in vec))
    return area,min_signed_jacobian


def audit_repaired_original(source, previous_bp, previous_manifest, native,
                            repaired_bp, repaired_receipt, *, budget_mm=BUDGET_MM):
    """Independent original-native gate for both incident sides and the true hole."""
    expected,expected_receipt=_bias_shared_controls(
        source,previous_bp,previous_manifest,native,budget_mm=budget_mm)
    if repaired_bp!=expected or repaired_receipt!=expected_receipt:
        raise ValueError('Altered repaired BP or forged original-source repair receipt')
    old_pts,old_patches=read_bp(previous_bp.decode())
    pts,patches=read_bp(repaired_bp)
    original_candidate,original_receipt=build_extension(source,previous_bp,previous_manifest,native)
    old_all_pts,old_all_patches=read_bp(original_candidate)
    if patches!=old_all_patches:
        raise ValueError('Changed source-canonical indexed topology')
    changed={i for i,(a,b) in enumerate(zip(old_all_pts,pts)) if a!=b}
    if len(changed)!=30 or any(i>=1527 for i in changed):
        raise ValueError('Unexpected changed source control inventory')
    if any(i in changed for patch in patches[96:126] for i in patch):
        raise ValueError('Hole preserving source patch geometry was changed')
    affected=tuple(i for i,p in enumerate(old_patches) if any(j in changed for j in p))
    if affected != EXPECTED_AFFECTED_OLD_PATCHES:
        raise ValueError('Unanticipated previously certified cylinder changes')
    if any(pts[k]!=old_all_pts[k] for k in range(len(pts)) if k not in changed):
        raise ValueError('Original unaffected source control was altered')
    adjacency=_edge_adjacency(patches)
    if (sum(len(v)==2 for v in adjacency.values()),sum(len(v)==1 for v in adjacency.values()))!=(239,114):
        raise ValueError('Invalid source-canonical shared side adjacency')
    mapping=full_correspondence(source.decode(),native)
    original_table=parse_entities(source.decode())
    outcome={
        'schema':'apmesh-s3w-original-s40-native-shared-seam-audit-v1',
        'source_sha256':SOURCE_SHA,
        'repaired_bp_sha256':sha256(repaired_bp.encode()).hexdigest(),
        'classification':'NOT_ADMITTED_UNTIL_ALL_GATES_PASS',
        'original_native_face_count':len(mapping['face_map']),
        'original_native_edge_count':len(mapping['edge_map']),
        'original_native_vertex_count':len(mapping['vertex_map']),
        'modified_old_patch_count':len(affected),
        'original_other_old_patch_nets_unchanged':132-len(affected),
        'modified_source_control_count':len(changed),
        'indexed_two_sided_seams':239,
        'open_indexed_sides':114,
        'original_source_hole_OUT_samples':0,
        'planar_original_interior_IN':0,
        'planar_original_boundary_IN_or_ON':0,
        'planar_original_boundary_OUT':0,
        'dense_planar_spline_boundary_IN_or_ON':0,
        'dense_planar_spline_boundary_OUT':0,
        'dense_cylinder_spline_boundary_IN_or_ON':0,
        'dense_cylinder_spline_boundary_OUT':0,
        'modified_cylinder_native_IN_or_ON_samples':0,
        'modified_cylinder_native_OUT_samples':0,
        'maximum_original_curve_distance_mm':0.0,
        'maximum_original_spline_dense_curve_distance_mm':0.0,
        'maximum_native_cylinder_sampled_radial_mm':0.0,
        'maximum_guarded_bivariate_bernstein_radial_mm':0.0,
        'maximum_planar_support_mm':0.0,
        'planar_area_results_mm2':{},
        'spline_original_edge_results':{},
        'pilot_budget_mm':BUDGET_MM,
        'changed_budget':False,
        'source_derived_coordinates_publicly_committed':False,
        'full_original_s40_shell_reconstructed':False,
        'original_three_plus_incidence_positive':False,
        'apmesh_cpp_tri_quad':'NOT_RUN',
        'continuous_trimmed_hausdorff_certified':False,
        'formal_directed_rounding_interval_proof':False,
    }
    # Re-run native UV on both newly represented planes with unchanged tolerance.
    for face_id,edge_id,cyl_src_id,cyl_native_id in SPLINE_SEAMS:
        face=native.Faces()[EXPECTED_NATIVE[face_id]]
        cylinder_face=native.Faces()[cyl_native_id]
        source_sides=source_boundary_sides(face_id,original_table,old_pts,old_patches,
                                          _edge_adjacency(old_patches))
        plane=BRepAdaptor_Surface(face.wrapped).Plane()
        normal=face.normalAt().toTuple()
        new_start=132 if face_id==17 else 140
        repaired_patch_area=0.0
        minimum_oriented_jacobian=float('inf')
        for patch in patches[new_start:new_start+8]:
            net=[pts[k] for k in patch]
            area,minimum=sampled_bicubic_area_mm2(net,normal)
            repaired_patch_area+=area
            minimum_oriented_jacobian=min(minimum_oriented_jacobian,minimum)
            a=_normal(net[0],net[3],net[12])
            if sum(a[k]*normal[k] for k in range(3))<=0:
                raise ValueError('Repaired native planar outward orientation changed')
            for iu in range(1,10):
                for iv in range(1,10):
                    p=surface(net,iu/10,iv/10)
                    if _state_on_plane(face,p)!=TopAbs_IN:
                        raise ValueError('Repaired planar interior outside original native trim')
                    outcome['planar_original_interior_IN']+=1
                    outcome['maximum_planar_support_mm']=max(
                        outcome['maximum_planar_support_mm'],plane.Distance(gp_Pnt(*p)))
            for side in ('bottom','top','left','right'):
                for k in range(11):
                    t=k/10
                    u,v={'bottom':(t,0.),'top':(t,1.),'left':(0.,t),'right':(1.,t)}[side]
                    p=surface(net,u,v)
                    if _state_on_plane(face,p) in (TopAbs_IN,TopAbs_ON):
                        outcome['planar_original_boundary_IN_or_ON']+=1
                    else:
                        outcome['planar_original_boundary_OUT']+=1
        outcome['planar_area_results_mm2'][str(face_id)]={
            'sampled_integrated_bp_area_mm2':repaired_patch_area,
            'original_native_face_area_mm2':face.Area(),
            'sampled_absolute_area_difference_mm2':abs(repaired_patch_area-face.Area()),
            'minimum_sampled_positive_jacobian_mm2':minimum_oriented_jacobian,
        }
        for original_eid,side in source_sides:
            original_native_edge=mapping['native_edges'][mapping['edge_map'][original_eid]]
            original_curve=BRepAdaptor_Curve(original_native_edge.wrapped)
            for k in range(11):
                p=_curve_point(pts,side,k/10)
                dist=_source_edge_closest(original_curve,p)
                outcome['maximum_original_curve_distance_mm']=max(
                    outcome['maximum_original_curve_distance_mm'],dist)
        spline_sides=[side for eid,side in source_sides if eid==edge_id]
        samples=[]
        for side in spline_sides:
            for k in range(101):
                pos=_curve_point(pts,side,k/100)
                samples.append(pos)
                if _state_on_plane(face,pos) in (TopAbs_IN,TopAbs_ON):
                    outcome['dense_planar_spline_boundary_IN_or_ON']+=1
                else:
                    outcome['dense_planar_spline_boundary_OUT']+=1
                native_state,_=_native_cylinder_state(cylinder_face,pos)
                if native_state in (TopAbs_IN,TopAbs_ON):
                    outcome['dense_cylinder_spline_boundary_IN_or_ON']+=1
                else:
                    outcome['dense_cylinder_spline_boundary_OUT']+=1
        source_curve=BRepAdaptor_Curve(
            mapping['native_edges'][mapping['edge_map'][edge_id]].wrapped)
        dense_dist=_closest_source_curve_samples(source_curve,samples)
        outcome['maximum_original_spline_dense_curve_distance_mm']=max(
            outcome['maximum_original_spline_dense_curve_distance_mm'],dense_dist)
        outcome['spline_original_edge_results'][str(edge_id)]={
            'source_planar_face':face_id,'source_cylinder_face':cyl_src_id,
            'source_cubic_segments':len(spline_sides),'dense_original_native_curve_samples':len(samples),
            'dense_max_sampled_original_curve_distance_mm':dense_dist,
        }
        # Only the 15 affected old cylinder patches require re-auditing;
        # 117 older patches retain their exact 16-control nets and geometry.
        edge_keys={tuple(sorted(side)) for side in spline_sides}
        affected_for_face=[i for i,patch in enumerate(old_patches)
                           if any(tuple(sorted(_side(patch,label))) in edge_keys
                                  for label in ('bottom','top','left','right'))]
        if len(affected_for_face)!=len(spline_sides):
            raise ValueError('Unexpected original STEP shared cylinder patch graph')
        cylinder=BRepAdaptor_Surface(cylinder_face.wrapped).Cylinder()
        for patch_id in affected_for_face:
            new_net=[pts[k] for k in patches[patch_id]]
            old_net=[old_pts[k] for k in old_patches[patch_id]]
            radial=bound_bicubic_cylinder_radial_mm(new_net,cylinder)
            if not radial['pass']:
                raise ValueError('Modified old cylinder exceeds unchanged radial budget')
            outcome['maximum_guarded_bivariate_bernstein_radial_mm']=max(
                outcome['maximum_guarded_bivariate_bernstein_radial_mm'],radial['upper_mm'])
            for u in range(11):
                for v in range(11):
                    p=surface(new_net,u/10,v/10)
                    state,_=_native_cylinder_state(cylinder_face,p)
                    if state in (TopAbs_IN,TopAbs_ON):
                        outcome['modified_cylinder_native_IN_or_ON_samples']+=1
                    else:
                        outcome['modified_cylinder_native_OUT_samples']+=1
                    dist=_analytic_cylinder_distance(cylinder,p)
                    outcome['maximum_native_cylinder_sampled_radial_mm']=max(
                        outcome['maximum_native_cylinder_sampled_radial_mm'],dist)
            for u,v in ((.2,.2),(.5,.5),(.8,.8),(.25,.75),(.75,.25)):
                old_axis=_cubic_derivatives(old_net,u,v)
                new_axis=_cubic_derivatives(new_net,u,v)
                cos=sum(old_axis[k]*new_axis[k] for k in range(3)) / (
                    math.sqrt(sum(z*z for z in old_axis))*math.sqrt(sum(z*z for z in new_axis)))
                if cos < 0.999:
                    raise ValueError('Modified original cylinder normal or Jacobian was inverted')
    if outcome['maximum_planar_support_mm']>1e-7:
        raise ValueError('Original planar support has changed')
    if (outcome['planar_original_boundary_OUT'] or outcome['dense_planar_spline_boundary_OUT'] or
        outcome['dense_cylinder_spline_boundary_OUT'] or outcome['modified_cylinder_native_OUT_samples']):
        raise ValueError('Original native trim membership remains blocked')
    if any(outcome[k] > BUDGET_MM for k in (
        'maximum_original_curve_distance_mm',
        'maximum_original_spline_dense_curve_distance_mm',
        'maximum_native_cylinder_sampled_radial_mm',
        'maximum_guarded_bivariate_bernstein_radial_mm')):
        raise ValueError('Original native geometry is outside the immutable pilot budget')
    # The preserved original #218 hole remains OUT, not merely an empty BP label.
    source_hole=source_partition(source.decode())
    u=source_hole['breakpoints_u'];v=source_hole['breakpoints_v']
    original_holed=native.Faces()[1]
    for i in range(1,8):
        for j in range(1,8):
            x=u[2]+(u[3]-u[2])*i/8
            y=v[1]+(v[3]-v[1])*j/8
            if BRepClass_FaceClassifier(original_holed.wrapped,
                     gp_Pnt2d(x,y),1e-7).State()!=TopAbs_OUT:
                raise ValueError('Original S40 #218 inner hole is not excluded')
            outcome['original_source_hole_OUT_samples']+=1
    if (outcome['original_native_face_count'],outcome['original_native_edge_count'],
        outcome['original_native_vertex_count'])!=(43,117,77):
        raise ValueError('Original native STEP topology census changed')
    if (outcome['planar_original_interior_IN'],outcome['planar_original_boundary_IN_or_ON'],
        outcome['original_source_hole_OUT_samples'],outcome['modified_cylinder_native_IN_or_ON_samples'])!=(1296,704,49,1815):
        raise ValueError('Incomplete or silently skipped native sample coverage')
    outcome['classification']='PASS_BOUNDED_NATIVE_GEOMETRY_AND_INDEXED_SEAMS'
    outcome['admitted_research_patch_count']=148
    outcome['represented_original_source_faces']=21
    outcome['unrepresented_original_source_faces']=22
    return outcome


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--source-step',type=Path,required=True)
    cli.add_argument('--baseline-bp',type=Path,required=True)
    cli.add_argument('--baseline-manifest',type=Path,required=True)
    cli.add_argument('--output-dir',type=Path,required=True)
    args=cli.parse_args()
    source=args.source_step.read_bytes()
    bp=args.baseline_bp.read_bytes()
    manifest=json.loads(args.baseline_manifest.read_text())
    native=cq.importers.importStep(str(args.source_step)).val()
    combined,receipt=_bias_shared_controls(source,bp,manifest,native)
    audit=audit_repaired_original(source,bp,manifest,native,combined,receipt)
    output=args.output_dir
    output.mkdir(parents=True,exist_ok=True)
    (output/'s40_spline_shared_repair.partial.bp').write_text(combined)
    (output/'s40_spline_shared_repair_manifest.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    (output/'s40_spline_shared_repair_native_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'patches':148,'represented_faces':21,'native':audit},indent=2,sort_keys=True))


if __name__=='__main__':
    main()
