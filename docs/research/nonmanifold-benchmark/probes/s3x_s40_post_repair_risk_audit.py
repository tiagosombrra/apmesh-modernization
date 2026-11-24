#!/usr/bin/env python3
"""S3.X source-native gap and repaired-seam robustness audit (research only).

The original STEP and the repaired BP are SHA-pinned. The outputs contain no
third-party STEP, reconstructed control points, or derivative CAD geometry.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.TopAbs import TopAbs_IN, TopAbs_ON

from audit_analytic_bp import read_bp, surface
from s3c_step_source_gate import parse_entities
from s3r_s40_conforming_hole_join import _edge_adjacency
from s3s_full_original_face_census import full_correspondence
from s3u_s40_post_octagon_gap_census import (
    _distance_to_admitted, _source_boundary_owners,
    classify_post_octagon,
)
from s3v_s40_curved_planar_closure import source_boundary_sides
from s3w_s40_shared_spline_repair import (
    EXPECTED_AFFECTED_OLD_PATCHES, SPLINE_SEAMS,
    _analytic_cylinder_distance, _curve_point, _native_cylinder_state,
    _state_on_plane, bound_bicubic_cylinder_radial_mm,
)

ORIGINAL_SHA = 'b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b'
PARENT_SHA = '988d8ed29867927f736838dde20db9efb358c0ee04a202a4f4810ae0e23aa40d'
REPAIRED_SHA = 'c826487d8cee76f6649100c59e5ce84fa6cb43c9004f53c68e3e565e86cdb174'
S3R_SHA = '98ff4cbfad08ce3f587607fddf3bb5e1a3697e1513a8ca86889bb28406e4028d'
BUDGET_MM = 0.001
REPAIRED_FACES = {17, 2092}
GAP_TOTAL = 22
SEAM_SEGMENTS = {85: 7, 2096: 8}
MODIFIED_CYLINDER_FACE_BY_PATCH = {
    **{k: 12 for k in (64, 66, 68, 70, 72, 74, 76)},
    **{k: 22 for k in range(88, 96)},
}


def check_pinned_inputs(original: bytes, parent: bytes, repaired: bytes,
                        parent_manifest: dict, repaired_manifest: dict,
                        s3r: bytes, s3r_manifest: dict, budget_mm: float = BUDGET_MM):
    """Fail closed on all historical input changes and any budget relaxation."""
    if budget_mm != BUDGET_MM:
        raise ValueError('The S3.X experimental geometry budget is immutable')
    for label, data, expected in (
        ('STEP', original, ORIGINAL_SHA), ('S3.T BP', parent, PARENT_SHA),
        ('S3.W BP', repaired, REPAIRED_SHA), ('S3.R BP', s3r, S3R_SHA),
    ):
        if sha256(data).hexdigest() != expected:
            raise ValueError(f'{label} SHA-256 mismatch')
    if (parent_manifest.get('new_bp_sha256') != PARENT_SHA or
        repaired_manifest.get('repaired_bp_sha256') != REPAIRED_SHA or
        repaired_manifest.get('source_sha256') != ORIGINAL_SHA or
        repaired_manifest.get('baseline_s3t_bp_sha256') != PARENT_SHA or
        s3r_manifest.get('source_sha256') != ORIGINAL_SHA or
        s3r_manifest.get('joined_bp_sha256') != S3R_SHA):
        raise ValueError('Unexpected atlas lineage in original manifest')
    old_points, old_patches = read_bp(parent.decode('utf-8'))
    points, patches = read_bp(repaired.decode('utf-8'))
    if (len(old_points), len(old_patches), len(points), len(patches)) != (1527, 132, 1619, 148):
        raise ValueError('Original atlas cardinality changed')
    if patches[:132] != old_patches:
        raise ValueError('Previously indexed patch topology changed')
    changed = {i for i in range(len(old_points)) if old_points[i] != points[i]}
    if len(changed) != 30 or any(i >= 1527 for i in changed):
        raise ValueError('Unexpected historical control mutation inventory')
    affected = {i for i, patch in enumerate(old_patches) if changed.intersection(patch)}
    if affected != set(EXPECTED_AFFECTED_OLD_PATCHES):
        raise ValueError('Original old-cylinder mutation lineage changed')
    adjacency = _edge_adjacency(patches)
    if (sum(len(v) == 2 for v in adjacency.values()),
        sum(len(v) == 1 for v in adjacency.values())) != (239, 114):
        raise ValueError('Repaired partial atlas indexed seams changed')
    if any(len(v) > 2 for v in adjacency.values()):
        raise ValueError('Indexed seam is overincident')
    return old_points, old_patches, points, patches


def classify_repaired_gap(original: bytes, native, parent: bytes,
                          parent_manifest: dict, s3r: bytes, s3r_manifest: dict):
    """Recompute 22 gaps from source-native incidence, not visual proximity."""
    prior = classify_post_octagon(original, native, parent, parent_manifest,
                                  s3r, s3r_manifest)
    mapping = full_correspondence(original.decode('utf-8'), native)
    existing = set(prior['covered_source_face_ids'])
    if len(existing) != 19 or existing.intersection(REPAIRED_FACES):
        raise ValueError('Source-native represented-face provenance invalid')
    admitted = existing | REPAIRED_FACES
    neighbors = _source_boundary_owners(mapping)
    hops = _distance_to_admitted(neighbors, admitted, mapping['source_faces'])
    owners = mapping['owners']
    rows = []
    for old in prior['pending_faces']:
        face_id = old['source_advanced_face_id']
        if face_id in REPAIRED_FACES:
            continue
        source_edges = {e['edge_curve_id'] for wire in mapping['source_faces'][face_id][1]
                        for e in wire}
        directly_shared = sorted(e for e in source_edges if (owners[e] - {face_id}) & admitted)
        row = {
            'source_advanced_face_id': face_id,
            'native_face_index': old['native_face_index'],
            'support_type': old['source_support_type'],
            'source_wire_edge_counts': old['source_wire_edge_counts'],
            'inner_wire_count': old['inner_wire_count'],
            'original_boundary_edge_count': old['source_boundary_edge_count'],
            'original_master_curve_histogram': old['3d_master_curve_histogram'],
            'already_indexed_incident_original_edges': len(directly_shared),
            'already_indexed_incident_source_edge_ids': directly_shared,
            'original_edge_hops_to_repaired_atlas': hops[face_id],
            'partition_preflight': old['partition_preflight'],
            'status': 'NOT_GENERATED_OR_ADMITTED',
        }
        if len(directly_shared) > len(source_edges):
            raise ValueError('Incorrect original STEP edge incidence')
        rows.append(row)
    rows.sort(key=lambda r: (
        0 if (r['support_type'] == 'PLANE' and r['inner_wire_count'] == 0) else 1,
        -r['already_indexed_incident_original_edges'],
        r['original_boundary_edge_count'],
        r['source_advanced_face_id'],
    ))
    if len(rows) != GAP_TOTAL or len(admitted) != 21:
        raise ValueError('S3.W admitted source face count inconsistent')
    if len({r['source_advanced_face_id'] for r in rows} | admitted) != 43:
        raise ValueError('Original source faces were lost or counted twice')
    if any(v > 2 for v in (len(owners[e]) for e in owners)):
        raise ValueError('Original manifold source face incidence changed')
    return {
        'corresponded_original_faces': len(mapping['face_map']),
        'corresponded_original_edges': len(mapping['edge_map']),
        'corresponded_original_vertices': len(mapping['vertex_map']),
        'represented_original_faces': len(admitted),
        'represented_original_face_ids': sorted(admitted),
        'remaining_original_faces': len(rows),
        'pending_original_support_histogram': dict(sorted(Counter(
            row['support_type'] for row in rows).items())),
        'remaining_direct_adjacency_count': sum(bool(r['already_indexed_incident_original_edges']) for r in rows),
        'remaining_edge_hop_histogram': dict(sorted(Counter(str(r['original_edge_hops_to_repaired_atlas'])
                                                     for r in rows).items())),
        'source_original_three_plus_incidence_edges': sum(len(v) >= 3 for v in owners.values()),
        'topology_front_candidates': [r['source_advanced_face_id'] for r in rows
                                      if r['support_type'] == 'PLANE' and
                                      r['already_indexed_incident_original_edges'] >= 6 and
                                      r['original_boundary_edge_count'] == 6],
        'pending_original_faces': rows,
    }


def stress_shared_spline_seams(original: bytes, native, parent: bytes, repaired: bytes,
                               *, segment_grid: int = 129, interior_grid: int = 15):
    """Challenge both trimmed native sides and all fifteen modified supports.

    Finite sample classifications and floating Bernstein bounds are not a
    continuous trimmed-surface equivalence or formal directed-rounding proof.
    """
    if segment_grid < 3 or segment_grid > 257 or interior_grid < 3 or interior_grid > 33:
        raise ValueError('Invalid sampling density')
    previous_pts, previous_patches = read_bp(parent.decode('utf-8'))
    pts, patches = read_bp(repaired.decode('utf-8'))
    table = parse_entities(original.decode('utf-8'))
    adjacency = _edge_adjacency(previous_patches)
    planar_pass = cylindrical_pass = 0
    sampled_radial_max = 0.
    original_seams = {}
    # Use original symbolic STEP edge IDs; do not infer seams by spatial welding.
    for original_face, edge_id, _, native_cyl in SPLINE_SEAMS:
        sides = [ids for eid, ids in source_boundary_sides(
            original_face, table, previous_pts, previous_patches, adjacency) if eid == edge_id]
        if len(sides) != SEAM_SEGMENTS[edge_id]:
            raise ValueError('Original source spline segmentation changed')
        source_plane = native.Faces()[0 if original_face == 17 else 18]
        source_cylinder = native.Faces()[native_cyl]
        for side in sides:
            for i in range(segment_grid):
                p = _curve_point(pts, side, i / (segment_grid - 1))
                if _state_on_plane(source_plane, p) not in (TopAbs_IN, TopAbs_ON):
                    raise ValueError(f'Corrected STEP spline #{edge_id} outside native plane trim')
                planar_pass += 1
                state, _ = _native_cylinder_state(source_cylinder, p)
                if state not in (TopAbs_IN, TopAbs_ON):
                    raise ValueError(f'Corrected STEP spline #{edge_id} outside native cylinder trim')
                cylindrical_pass += 1
        original_seams[str(edge_id)] = {
            'original_source_planar_face': original_face,
            'original_source_cylindrical_face': 1519 if edge_id == 85 else 2457,
            'source_indexed_cubic_segments': len(sides),
            'sampled_both_native_sides': len(sides) * segment_grid,
            'outside_trim_samples': 0,
        }
    numeric_bounds = {}
    total_interior = 0
    for patch_id, native_face_index in MODIFIED_CYLINDER_FACE_BY_PATCH.items():
        face = native.Faces()[native_face_index]
        cylinder = BRepAdaptor_Surface(face.wrapped).Cylinder()
        net = [pts[j] for j in patches[patch_id]]
        radial = bound_bicubic_cylinder_radial_mm(net, cylinder)
        if not radial['pass'] or radial['upper_mm'] > BUDGET_MM:
            raise ValueError('Modified cylinder exceeds immutable support budget')
        numeric_bounds[str(patch_id)] = radial['upper_mm']
        for iu in range(interior_grid):
            for iv in range(interior_grid):
                # Interior-only nodes avoid treating native boundary tolerance as interior.
                p = surface(net, (iu + .5) / interior_grid, (iv + .5) / interior_grid)
                state, _ = _native_cylinder_state(face, p)
                if state not in (TopAbs_IN, TopAbs_ON):
                    raise ValueError(f'Modified STEP cylinder patch {patch_id} samples OUT')
                sampled_radial_max = max(sampled_radial_max, _analytic_cylinder_distance(cylinder, p))
                total_interior += 1
    maximum_bound = max(numeric_bounds.values())
    return {
        'sample_grid_samples_per_original_cubic_segment': segment_grid,
        'corrected_spline_planar_trim_in_or_on': planar_pass,
        'corrected_spline_cylinder_trim_in_or_on': cylindrical_pass,
        'corrected_spline_out_samples': 0,
        'source_spline_seams': original_seams,
        'modified_prior_cylinder_patch_count': len(MODIFIED_CYLINDER_FACE_BY_PATCH),
        'modified_prior_cylinder_interior_samples': total_interior,
        'modified_prior_cylinder_out_samples': 0,
        'max_sampled_radial_mm': sampled_radial_max,
        'max_float_guarded_bernstein_radial_mm': maximum_bound,
        'fixed_budget_mm': BUDGET_MM,
        'float_guarded_remaining_margin_mm': BUDGET_MM - maximum_bound,
        'radial_bounds_per_patch_mm': numeric_bounds,
        'formal_interval_bound': False,
        'continuous_trimmed_surface_equivalence': False,
    }


def audit_s3x(original: bytes, native, parent: bytes, parent_manifest: dict,
              repaired: bytes, repaired_manifest: dict,
              s3r: bytes, s3r_manifest: dict, *, budget_mm: float = BUDGET_MM,
              segment_grid: int = 129, interior_grid: int = 15):
    """Re-evaluate original source-native census and seam robustness independently."""
    check_pinned_inputs(original, parent, repaired, parent_manifest, repaired_manifest,
                        s3r, s3r_manifest, budget_mm)
    gap = classify_repaired_gap(original, native, parent, parent_manifest, s3r, s3r_manifest)
    stress = stress_shared_spline_seams(original, native, parent, repaired,
                                      segment_grid=segment_grid, interior_grid=interior_grid)
    return {
        'schema': 'apmesh-s3x-original-s40-source-native-audit-v1',
        'source_sha256': sha256(original).hexdigest(),
        'repaired_atlas_sha256': sha256(repaired).hexdigest(),
        'research_patch_count': 148,
        'declared_global_control_count': 1619,
        'indexed_two_sided_seams': 239,
        'indexed_open_sides': 114,
        'gap': gap,
        'stress': stress,
        'classification': 'PASS_BOUNDED_SAMPLED_AUDIT_NO_NEW_BP_ADMISSION',
        'apmesh_tri_quad_executed': False,
        'production_cpp_regression_executed': False,
    }


def public_summary(report):
    """Exclude all original-derived control coordinates from the public receipt."""
    return {k: v for k, v in report.items() if k != 'gap'} | {
        'gap': {k: v for k, v in report['gap'].items() if k != 'pending_original_faces'},
        'pending_face_summary': [{k: v for k, v in row.items()
                                  if k not in ('already_indexed_incident_source_edge_ids',)}
                                 for row in report['gap']['pending_original_faces']],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-step', type=Path, required=True)
    parser.add_argument('--private-bp', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--segment-grid', type=int, default=129)
    parser.add_argument('--interior-grid', type=int, default=15)
    args = parser.parse_args()
    directory = args.private_bp
    original = args.source_step.read_bytes()
    parent = (directory / 's40_planar_octagons.partial.bp').read_bytes()
    repaired = (directory / 's40_spline_shared_repair.partial.bp').read_bytes()
    s3r = (directory / 's40_218_conforming.partial.bp').read_bytes()
    parent_manifest = json.loads((directory / 's40_planar_octagons_manifest.json').read_text())
    repaired_manifest = json.loads((directory / 's40_spline_shared_repair_manifest.json').read_text())
    s3r_manifest = json.loads((directory / 's40_218_conforming_manifest.json').read_text())
    # Verify source bytes before CAD import.
    check_pinned_inputs(original, parent, repaired, parent_manifest, repaired_manifest,
                        s3r, s3r_manifest)
    native = cq.importers.importStep(str(args.source_step)).val()
    report = audit_s3x(original, native, parent, parent_manifest, repaired,
                       repaired_manifest, s3r, s3r_manifest,
                       segment_grid=args.segment_grid, interior_grid=args.interior_grid)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / 'original_s40_s3x_private_native_report.json').write_text(
        json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (args.output_dir / 'original_s40_s3x_public_nongeometric_receipt.json').write_text(
        json.dumps(public_summary(report), indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('classification', 'research_patch_count')},
                     sort_keys=True))
    print('pending:', report['gap']['remaining_original_faces'],
          'modified radial bound:', report['stress']['max_float_guarded_bernstein_radial_mm'])


if __name__ == '__main__':
    main()
