#!/usr/bin/env python3
"""Independently audit native UV trim membership of source-indexed BP patches.

Research only: sparse-to-dense UV classification is NOT a certified continuous
trim/topology equivalence, and neither this module nor upstream probes mesh CAD.
Original third-party STEP sources must stay external to the research repository.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.BRepTools import BRepTools
from OCP.ElSLib import ElSLib
from OCP.TopAbs import TopAbs_IN, TopAbs_ON, TopAbs_OUT
from OCP.gp import gp_Pnt, gp_Pnt2d

from audit_analytic_bp import read_bp, surface
from s3c_step_source_gate import SOURCES
from s3i_joint_source_atlas import independently_check_joint
from s3j_radial_support_enclosure import audit_joint


class NativeTrimRejection(ValueError):
    """An original imported face cannot admit the proposed patch UV footprint."""


def _uv_member(native_face, cylinder, point, bounds, uv_tolerance):
    """Classify a spatial point in the original trimmed native face's UV domain.

    ElSLib computes the analytic cylindrical parameter, independently from
    source STEP PCURVE parsing. Periodic equivalents are tried explicitly.
    """
    u, v = ElSLib.Parameters_s(cylinder, gp_Pnt(*point))
    umin, umax, vmin, vmax = bounds
    if not all(math.isfinite(value) for value in (u, v, *bounds)):
        raise NativeTrimRejection('Nonfinite cylinder/native UV parameters')
    matches = []
    for k in range(-2, 3):
        uk = u + k*2*math.pi
        if not (umin-uv_tolerance <= uk <= umax+uv_tolerance):
            continue
        state = BRepClass_FaceClassifier(
            native_face.wrapped, gp_Pnt2d(uk, v), uv_tolerance).State()
        if state == TopAbs_IN:
            matches.append(('IN', uk, v))
        elif state == TopAbs_ON:
            matches.append(('ON', uk, v))
        elif state != TopAbs_OUT:
            raise NativeTrimRejection('Native UV classifier returned an unknown state')
    if not matches:
        raise NativeTrimRejection('Source patch UV point lies OUTSIDE native trimmed face')
    matches.sort(key=lambda x: (x[0] != 'IN', abs(x[1]-(umin+umax)/2)))
    return matches[0]


def classify_patch(native_face, vertices, patch_ids, *, interior_grid=9,
                   boundary_grid=11, native_tolerance=1e-7,
                   distance_budget_mm=.001):
    """Recompute BP/native surface membership and projection from source controls."""
    if native_face.geomType() != 'CYLINDER':
        raise NativeTrimRejection('Expected imported native cylindrical face')
    if any(not isinstance(n, int) or n < 3 or n > 99
           for n in (interior_grid, boundary_grid)):
        raise ValueError('UV grid sizes must be integers between 3 and 99')
    if not (math.isfinite(native_tolerance) and 0 < native_tolerance <= 1e-3):
        raise ValueError('Invalid native UV classifier tolerance')
    if not (math.isfinite(distance_budget_mm) and distance_budget_mm > 0):
        raise ValueError('Invalid geometric distance budget')
    if len(patch_ids) != 16 or any(not isinstance(i,int) or i < 0 or i >= len(vertices) for i in patch_ids):
        raise ValueError('Malformed indexed bicubic patch')
    controls = [vertices[i] for i in patch_ids]
    adaptor = BRepAdaptor_Surface(native_face.wrapped, True)
    cylinder = adaptor.Cylinder()
    bounds = BRepTools.UVBounds_s(native_face.wrapped)
    observed = Counter()
    us,vs=[],[]
    maximum = 0.0
    def check(u,v,interior):
        nonlocal maximum
        point = surface(controls,u,v)
        state, U, V = _uv_member(native_face,cylinder,point,bounds,native_tolerance)
        if interior and state != 'IN':
            raise NativeTrimRejection('Interior BP sample classified ON, not IN, in native trim')
        on_surface = adaptor.Value(U,V)
        deviation = math.dist(point,(on_surface.X(),on_surface.Y(),on_surface.Z()))
        maximum = max(maximum,deviation)
        if deviation > distance_budget_mm + native_tolerance:
            raise NativeTrimRejection('Native cylinder projection exceeds fixed distance budget')
        observed['INTERIOR_'+state if interior else 'BOUNDARY_'+state] += 1
        us.append(U)
        vs.append(V)
    for row in range(interior_grid):
        v=(row+1)/(interior_grid+1)
        for col in range(interior_grid):
            u=(col+1)/(interior_grid+1)
            check(u,v,True)
    for k in range(boundary_grid):
        t=k/(boundary_grid-1)
        for u,v in ((t,0.),(t,1.),(0.,t),(1.,t)):
            check(u,v,False)
    return {
        'native_trim_bounds_uv': [float(x) for x in bounds],
        'observed_patch_uv_bounds': [min(us),max(us),min(vs),max(vs)],
        'source_support_type': 'CYLINDER',
        'classification_histogram': dict(sorted(observed.items())),
        'max_native_cylinder_projection_distance_mm': maximum,
        'interior_sample_count': interior_grid**2,
        'boundary_sample_count': 4*boundary_grid,
        'native_trim_scope': 'DISCRETE_OCCT_BREPCLASS_FACECLASSIFIER_WITH_PERIODIC_U_EQUIVALENTS',
        'continuous_trim_topology_certified': False,
    }


def audit_native_joint(step_text, native_shape, bp, manifest, *, model,
                       source_sha256, declared_budget_mm,
                       interior_grid=9, boundary_grid=11, uv_tolerance=1e-7):
    """Admit only source-authenticated, already independently audited joint BP."""
    if sha256(step_text.encode('utf-8')).hexdigest() != source_sha256:
        raise ValueError('Original STEP source SHA-256 mismatch')
    if model in SOURCES and SOURCES[model][1] != source_sha256:
        raise ValueError('Pinned original industrial STEP SHA-256 mismatch')
    if sha256(bp.encode('utf-8')).hexdigest() != manifest.get('bp_sha256'):
        raise ValueError('Original indexed BP checksum mismatch')
    if manifest.get('source_sha256') != source_sha256 or manifest.get('source_model') != model:
        raise ValueError('Original BP manifest source identity mismatch')
    joint = independently_check_joint(step_text,native_shape,bp,manifest,
                                     model=model,source_sha256=source_sha256)
    radial = audit_joint(step_text,bp,manifest,model=model,
                         source_sha256=source_sha256,
                         declared_budget_mm=declared_budget_mm)
    if not radial['same_numeric_budget_guarded_radial_support_pass']:
        raise NativeTrimRejection('Guarded radial cylinder budget was not met')
    vertices, patches = read_bp(bp)
    if len(patches) != len(manifest['patches']):
        raise ValueError('Missing original BP patch identity entries')
    native_faces=native_shape.Faces()
    face_groups=defaultdict(list)
    records=[]
    for indices,metadata in zip(patches,manifest['patches']):
        if metadata['kind'] != 'SOURCE_CYLINDER_APPROX_CANDIDATE':
            continue
        source_face=metadata['source_face_id']
        native_index=metadata['source_native_face_index']
        if not isinstance(native_index,int) or not 0 <= native_index < len(native_faces):
            raise ValueError('Original source/native face index invalid')
        sampled = classify_patch(native_faces[native_index], vertices, indices,
                    interior_grid=interior_grid,boundary_grid=boundary_grid,
                    native_tolerance=uv_tolerance,
                    distance_budget_mm=declared_budget_mm)
        out={'source_advanced_face_id': source_face,
             'source_native_face_index': native_index,
             'derived_patch_segment':metadata['local_segment'],
             **sampled}
        records.append(out)
        face_groups[source_face].append(out)
    if not records:
        raise ValueError('No original cylinder surfaces present in partial BP')
    envelopes=[]
    for face_id,patch_results in sorted(face_groups.items()):
        trimmed_bounds=patch_results[0]['native_trim_bounds_uv']
        if any(item['native_trim_bounds_uv'] != trimmed_bounds for item in patch_results):
            raise NativeTrimRejection('Source face changed native trimmed UV bounds')
        # The bounding rectangle is a necessary, not sufficient, coverage gate.
        # Discrete classification is additionally required on every sample.
        umin,umax,vmin,vmax=trimmed_bounds
        observed=[item['observed_patch_uv_bounds'] for item in patch_results]
        found=[min(x[0] for x in observed),max(x[1] for x in observed),
               min(x[2] for x in observed),max(x[3] for x in observed)]
        if max(abs(a-b) for a,b in zip(found,trimmed_bounds))>10*uv_tolerance:
            raise NativeTrimRejection('Patch union does not cover native trimmed UV bounds')
        spans=sorted((x[0],x[1]) for x in observed)
        for (_,prev_end),(next_start,_) in zip(spans,spans[1:]):
            if next_start-prev_end>10*uv_tolerance:
                raise NativeTrimRejection('Patch segments leave a gap in source native U interval')
        envelopes.append({'source_advanced_face_id':face_id,
                          'native_trimmed_uv_bounds':trimmed_bounds,
                          'observed_patch_union_uv_bounds':found,
                          'segments_checked':len(patch_results),
                          'no_sampled_U_interval_gaps':True})
    return {
        'schema':'apmesh-s3k-original-native-cylindrical-uv-trim-sampled-audit-v1',
        'source_model':model,'source_raw_sha256':source_sha256,
        'bp_sha256':sha256(bp.encode('utf-8')).hexdigest(),
        'original_face_ids':sorted(face_groups),
        'cylindrical_bp_patch_count':len(records),
        'native_interior_uv_samples':sum(x['interior_sample_count'] for x in records),
        'native_boundary_uv_samples':sum(x['boundary_sample_count'] for x in records),
        'maximum_native_projection_distance_mm':max(x['max_native_cylinder_projection_distance_mm'] for x in records),
        'fixed_budget_mm':declared_budget_mm,
        'joint_original_controls_checked':joint['shared_original_generator_control_ids_checked'],
        'guarded_radial_support_bound_mm':radial['maximum_guarded_radial_support_error_upper_mm'],
        'native_face_coverage_envelopes':envelopes,
        'patch_results':records,
        'native_uv_claim':'DISCRETE_TRIM_MEMBERSHIP_ONLY_NOT_CONTINUOUS_CERTIFICATE',
        'full_original_CAD_atlas':False,
        'apmesh_tri_quad_generation':'NOT_RUN',
        'original_nonmanifold_3plus_admission':'NOT_ESTABLISHED',
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--step',type=Path,required=True)
    p.add_argument('--bp',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--model',required=True)
    p.add_argument('--expected-sha256')
    p.add_argument('--budget-mm',type=float,required=True)
    p.add_argument('--interior-grid',type=int,default=9)
    p.add_argument('--boundary-grid',type=int,default=11)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    raw=a.step.read_bytes();digest=sha256(raw).hexdigest()
    if a.model in SOURCES:
        if digest!=SOURCES[a.model][1]:
            raise ValueError('Pinned original industrial source digest mismatch')
    elif a.model=='SYNTHETIC':
        if not a.expected_sha256 or digest!=a.expected_sha256:
            raise ValueError('Synthetic STEP must supply its actual --expected-sha256')
    else:
        raise ValueError('Unknown source model')
    manifest=json.loads(a.manifest.read_text(encoding='utf-8'))
    shape=cq.importers.importStep(str(a.step)).val()
    report=audit_native_joint(raw.decode('utf-8'),shape,a.bp.read_text(encoding='utf-8'),manifest,
                model=a.model,source_sha256=digest,declared_budget_mm=a.budget_mm,
                interior_grid=a.interior_grid,boundary_grid=a.boundary_grid)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('source_model','original_face_ids','cylindrical_bp_patch_count','native_interior_uv_samples','native_boundary_uv_samples','maximum_native_projection_distance_mm','guarded_radial_support_bound_mm')},sort_keys=True))


if __name__=='__main__':
    main()
