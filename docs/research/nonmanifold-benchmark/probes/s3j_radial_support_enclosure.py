#!/usr/bin/env python3
"""Guarded Bernstein enclosure for source-identified bicubic cylinder patches.

This is a research-only *analytic cylinder support* check. It is not a
continuous native trimmed-face Hausdorff certificate or APMesh mesh acceptance.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

from audit_analytic_bp import read_bp
from s3c_step_source_gate import SOURCES
from s3h_source_cylinder_bp import face_geometry


def _dot(a, b):
    return math.fsum(x*y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def _slice_coefficients(radial_controls, radius):
    """Get the degree-six Bernstein net of |cubic(t)|^2 - radius^2."""
    result = []
    for k in range(7):
        terms = [
            math.comb(3, i)*math.comb(3, k-i)/math.comb(6, k)
            * _dot(radial_controls[i], radial_controls[k-i])
            for i in range(4) if 0 <= k-i <= 3
        ]
        result.append(math.fsum((*terms, -radius*radius)))
    return result


def _split_half(net):
    """Subdivide a Bernstein polynomial at t=1/2 by de Casteljau."""
    rows = [list(net)]
    while len(rows[-1]) > 1:
        prev = rows[-1]
        rows.append([(a+b)/2 for a, b in zip(prev[:-1], prev[1:])])
    return [row[0] for row in rows], [row[-1] for row in reversed(rows)]


def _squared_enclosure(coefficients, depth):
    """Use the convex-hull property on recursively refined intervals."""
    if not isinstance(depth, int) or not 0 <= depth <= 12:
        raise ValueError('Subdivision depth must be an integer in [0, 12]')
    intervals = [coefficients]
    for _ in range(depth):
        intervals = [child for net in intervals for child in _split_half(net)]
    return min(min(net) for net in intervals), max(max(net) for net in intervals)


def _radial_enclosure(qmin, qmax, radius):
    if qmin <= -radius*radius:
        raise ValueError('Radial polynomial may vanish; no angular certificate')
    low = math.sqrt(max(0.0, radius*radius + qmin))
    high = math.sqrt(radius*radius + qmax)
    return max(abs(low-radius), abs(high-radius))


def _near(value, reference, tolerance):
    return abs(value-reference) <= tolerance


def certify_patch(vertices, patch, geometry, segment, segments, *, depth=8,
                  numerical_guard_mm=1e-9):
    """Enclose the analytic radial error on an axially separable bicubic patch.

    In exact arithmetic the Bernstein coefficient interval bounds the entire
    polynomial over the full parameter interval. This implementation uses
    floating point and an explicit heuristic margin; it is NOT a formal proof
    with directed-rounding interval arithmetic.
    """
    if not isinstance(segment, int) or not isinstance(segments, int) or not (0 <= segment < segments):
        raise ValueError('Invalid patch segment or segment count')
    if not (math.isfinite(numerical_guard_mm) and numerical_guard_mm >= 1e-9):
        raise ValueError('Numerical margin must be finite and positive')
    if len(patch) != 16:
        raise ValueError('Malformed indexed bicubic patch')
    if any(not isinstance(i, int) or i < 0 or i >= len(vertices) for i in patch):
        raise ValueError('BP references an invalid control vertex')
    f = geometry['frame']
    origin = f['origin']
    axis = f['axis']
    x = f['x']
    y = f['y']
    radius = f['radius']
    zmin = geometry['zmin']
    zmax = geometry['zmax']
    if not (math.isfinite(radius) and radius > 0 and zmax > zmin):
        raise ValueError('Malformed source cylindrical frame')
    coords = [[vertices[patch[4*row+col]] for col in range(4)] for row in range(4)]
    radial = []
    max_control_residual = 0.0
    z_tolerance = max(1e-9, 1e-10 * max(1, abs(zmin), abs(zmax), zmax-zmin))
    for row in range(4):
        expected_z = zmin + (zmax-zmin)*row/3
        for col in range(4):
            P = _sub(coords[row][col], origin)
            z = _dot(P, axis)
            if not _near(z, expected_z, z_tolerance):
                raise ValueError('Patch is not axially linear in native STEP cylinder frame')
            R = (_dot(P, x), _dot(P, y))
            if row == 0:
                radial.append(R)
            elif math.dist(R, radial[col]) > z_tolerance:
                raise ValueError('Patch radial controls vary across axial rows')
            ideal = tuple(origin[k] + expected_z*axis[k]
                          + radial[col][0]*x[k] + radial[col][1]*y[k]
                          for k in range(3))
            deviation = math.dist(coords[row][col], ideal)
            max_control_residual = max(max_control_residual, deviation)
            if deviation > 2*z_tolerance:
                raise ValueError('Source frame is not orthonormal for patch controls')
    start = geometry['start_u'] + geometry['signed_sweep_rad']*segment/segments
    delta = geometry['signed_sweep_rad']/segments
    theta = abs(delta)
    if not (0 < theta <= math.pi/2 + 1e-10):
        raise ValueError('Angular patch outside admitted <=90 degree wedge')
    sign = 1 if delta > 0 else -1
    c, s = math.cos(start), math.sin(start)
    cos_delta, sin_delta = math.cos(theta), math.sin(theta)
    # The cone between two rays of angular separation <=90 degrees is convex.
    # All cubic controls must lie in that cone; a convex combination stays in it.
    wedge_tol = max(1e-11, 1e-10*radius)
    for q in radial:
        forward = q[0]*c + q[1]*s
        side = sign*(-q[0]*s+q[1]*c)
        if side < -wedge_tol or forward*sin_delta-side*cos_delta < -wedge_tol:
            raise ValueError('Cubic radial controls leave the original source angular wedge')
    coefficients = _slice_coefficients(radial, radius)
    qmin, qmax = _squared_enclosure(coefficients, depth)
    bound = (_radial_enclosure(qmin, qmax, radius)
             + max_control_residual + numerical_guard_mm)
    return {
        'schema': 'apmesh-s3j-bernstein-support-enclosure-v1',
        'source_face_id': geometry['face_id'],
        'patch_segment': segment,
        'source_angle_rad': [start, start+delta],
        'source_radius_mm': radius,
        'source_axial_extent_mm': [zmin, zmax],
        'degree_of_squared_radial_polynomial': 6,
        'bernstein_subdivision_depth': depth,
        'bernstein_squared_radius_residual_min_mm2': qmin,
        'bernstein_squared_radius_residual_max_mm2': qmax,
        'numerical_guard_mm': numerical_guard_mm,
        'max_nonseparable_control_residual_mm': max_control_residual,
        'radial_support_error_upper_mm': bound,
        'axially_separable_bicubic_verified': True,
        'radial_controls_inside_source_angular_wedge': True,
        'continuous_source_support_scope': 'NUMERICAL_BERNSTEIN_CONVEX_HULL_WITH_FLOAT_GUARD',
        'formal_directed_rounding_interval_proof': False,
        'native_trimmed_face_distance': 'NOT_CERTIFIED',
        'apmesh_generation': 'NOT_RUN',
    }


def audit_joint(step_text, bp, manifest, *, model, source_sha256,
                declared_budget_mm, depth=8, numerical_guard_mm=1e-9):
    """Recompute each joint-cylinder patch enclosure from the source geometry."""
    if not (math.isfinite(declared_budget_mm) and declared_budget_mm > 0):
        raise ValueError('Externally declared budget must be finite and positive')
    if sha256(step_text.encode('utf-8')).hexdigest() != source_sha256:
        raise ValueError('Original STEP source digest mismatch')
    if model in SOURCES and source_sha256 != SOURCES[model][1]:
        raise ValueError('Pinned original source digest mismatch')
    if sha256(bp.encode('utf-8')).hexdigest() != manifest.get('bp_sha256'):
        raise ValueError('Indexed joint BP digest mismatch')
    if manifest['source_model'] != model or manifest['source_sha256'] != source_sha256:
        raise ValueError('Manifest source binding mismatch')
    vertices, patches = read_bp(bp)
    if len(patches) != manifest['generated_partial_bp_patch_count']:
        raise ValueError('BP patch inventory mismatch')
    if len(patches) != len(manifest['patches']):
        raise ValueError('Joint patch metadata mismatch')
    if any(list(patch) != meta['control_vertex_ids']
           for patch, meta in zip(patches, manifest['patches'])):
        raise ValueError('BP patch control ids disagree with source metadata')
    controls = []
    observed_faces = set()
    for entry in manifest['cylinder_fit_receipts']:
        faceid = entry['face_id']
        if faceid in observed_faces:
            raise ValueError('Duplicate cylindrical face receipts')
        observed_faces.add(faceid)
        geo = face_geometry(step_text, face_id=faceid, model=model,
                            source_sha256=source_sha256,
                            require_anchored=(model in SOURCES))
        labels = [(patch, meta) for patch, meta in zip(patches, manifest['patches'])
                  if meta['kind'] == 'SOURCE_CYLINDER_APPROX_CANDIDATE'
                  and meta['source_face_id'] == faceid]
        if len(labels) != entry['segment_count']:
            raise ValueError('Missing or duplicated source cylindrical patch segments')
        indexes = [meta['local_segment'] for patch, meta in labels]
        if sorted(indexes) != list(range(len(indexes))):
            raise ValueError('Nonconsecutive or duplicated source cylindrical patch indices')
        for patch, label in labels:
            controls.append(certify_patch(vertices, patch, geo,
                           label['local_segment'], len(labels), depth=depth,
                           numerical_guard_mm=numerical_guard_mm))
    cylinder_labels = [meta for meta in manifest['patches']
                       if meta['kind'] == 'SOURCE_CYLINDER_APPROX_CANDIDATE']
    if len(cylinder_labels) != len(controls):
        raise ValueError('Unreported cylinder patches in indexed BP')
    allowed = [entry['source_fit_audit']['prespecified_budget_mm']
               for entry in manifest['cylinder_fit_receipts']]
    if not allowed or not controls:
        raise ValueError('No verified cylindrical patch evidence to audit')
    if any(budget != declared_budget_mm for budget in allowed):
        raise ValueError('Manifest budget disagrees with externally declared budget')
    limit = declared_budget_mm
    maximum = max(x['radial_support_error_upper_mm'] for x in controls)
    return {
        'schema': 'apmesh-s3j-joint-analytic-support-gate-v1',
        'source_model': model, 'source_sha256': source_sha256,
        'joint_bp_sha256': sha256(bp.encode('utf-8')).hexdigest(),
        'cylinder_patch_count': len(controls),
        'cylinder_original_face_ids': sorted(set(x['source_face_id'] for x in controls)),
        'patches': controls,
        'maximum_guarded_radial_support_error_upper_mm': maximum,
        'predeclared_sampled_budget_mm': limit,
        'same_numeric_budget_guarded_radial_support_pass': maximum <= limit,
        'continuous_support_scope': 'NUMERICAL_BERNSTEIN_ENCLOSURE_NOT_FORMAL_INTERVAL_PROOF',
        'original_m5_native_brep_import': 'NOT_ESTABLISHED_BY_THIS_GATE',
        'original_native_face_trim': 'NOT_CERTIFIED',
        'original_external_nonmanifold': 'NOT_ESTABLISHED',
        'apmesh_mesh_generation': 'NOT_RUN',
    }


def run(step_file, bp_file, manifest_file, output, *, model, declared_budget_mm,
        expected_sha256=None, depth=8, numerical_guard_mm=1e-9):
    original = Path(step_file).read_bytes()
    sha = sha256(original).hexdigest()
    if model in SOURCES:
        if sha != SOURCES[model][1]:
            raise ValueError('Pinned original STEP SHA-256 mismatch')
    elif sha != expected_sha256:
        raise ValueError('Synthetic STEP requires an exact caller-pinned SHA-256')
    bp = Path(bp_file).read_text(encoding='utf-8')
    manifest = json.loads(Path(manifest_file).read_text(encoding='utf-8'))
    receipt = audit_joint(original.decode('utf-8'), bp, manifest, model=model,
                          source_sha256=sha, declared_budget_mm=declared_budget_mm, depth=depth,
                          numerical_guard_mm=numerical_guard_mm)
    if not receipt['same_numeric_budget_guarded_radial_support_pass']:
        raise ValueError('Guarded radial cylinder support bound exceeds predeclared budget')
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--step',type=Path,required=True)
    p.add_argument('--bp',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--model',required=True)
    p.add_argument('--expected-sha256')
    p.add_argument('--budget-mm',type=float,required=True,help='Externally fixed pilot budget in mm')
    p.add_argument('--depth',type=int,default=8)
    p.add_argument('--guard-mm',type=float,default=1e-9)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    outcome=run(args.step,args.bp,args.manifest,args.output,model=args.model,
                declared_budget_mm=args.budget_mm,
                expected_sha256=args.expected_sha256,depth=args.depth,
                numerical_guard_mm=args.guard_mm)
    print(json.dumps({k:outcome[k] for k in ('source_model','cylinder_patch_count',
                                              'maximum_guarded_radial_support_error_upper_mm',
                                              'same_numeric_budget_guarded_radial_support_pass')},sort_keys=True))


if __name__=='__main__':
    main()
