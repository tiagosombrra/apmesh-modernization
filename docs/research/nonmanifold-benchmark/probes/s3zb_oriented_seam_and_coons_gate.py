#!/usr/bin/env python3
"""S3.Z.2: strict oriented seam and Coons identity for proposed S40 patches.

This module does not infer original source incidence from coordinates or
certify native CAD geometry. It is an additional mandatory combinatorial gate.
"""
from __future__ import annotations

import math

from s3z_s40_circular_seam_gate import (
    JOINT_EXPECTED_CONTROLS, JOINT_EXPECTED_OPEN_SIDES,
    JOINT_EXPECTED_PATCHES, JOINT_EXPECTED_TWO_SIDED_SEAMS,
    SELECTED_S3Y_CONTROLS, SELECTED_S3Y_PATCHES,
    _indexed_side, _sides_by_original_indices, coons_interior,
)


def directed_boundary_indices(patch, side):
    """Use the actual CCW boundary direction, not raw patch-grid order.

    Raw top and left sides have the opposite orientation to a CCW traversal.
    This distinction matters when independently checking new internal joins.
    """
    indices = _indexed_side(patch, side)
    return indices[::-1] if side in ('top', 'left') else indices


def audit_new_surface_topology(
    prior_patches, proposed_patches, *, first_new=SELECTED_S3Y_PATCHES,
    enforce_s40_counts=True,
):
    """Require complete 2-sided, orientation-consistent closure of new faces.

    The old atlas may have open sides (a partial shell). No *new* patch may
    leave a hanging side, self-join, or join an old or new side same-direction.
    This is a combinatorial gate; native face sidedness must be audited later.
    """
    if len(prior_patches) != first_new:
        raise ValueError('Historical source-indexed patch-prefix size changed')
    if len(proposed_patches) < first_new:
        raise ValueError('Candidate removed previously admitted patches')
    if tuple(tuple(p) for p in prior_patches) != tuple(tuple(p) for p in proposed_patches[:first_new]):
        raise ValueError('Previously admitted patch indices changed')

    incidence = _sides_by_original_indices(proposed_patches)
    new_patch_ids = set(range(first_new, len(proposed_patches)))
    new_old = new_new = old_old = 0
    new_sides_checked = set()

    for shared_key, owners in incidence.items():
        if len(owners) > 2:
            raise ValueError('Overincident indexed interface')
        touching = any(pid in new_patch_ids for pid, _side, _idx in owners)
        if touching:
            if len(owners) != 2:
                raise ValueError('New candidate patch left an unpaired indexed boundary')
            (a_pid, a_side, _), (b_pid, b_side, _) = owners
            if a_pid == b_pid:
                raise ValueError('New candidate patch self-paired one of its boundaries')
            a = directed_boundary_indices(proposed_patches[a_pid], a_side)
            b = directed_boundary_indices(proposed_patches[b_pid], b_side)
            if a != b[::-1]:
                raise ValueError('New interface fails CCW-oriented boundary consistency')
            for pid, side, _ in owners:
                if pid in new_patch_ids:
                    marker = (pid, side)
                    if marker in new_sides_checked:
                        raise ValueError('Repeated new patch-side identity')
                    new_sides_checked.add(marker)
            if a_pid in new_patch_ids and b_pid in new_patch_ids:
                new_new += 1
            else:
                new_old += 1
        elif len(owners) == 2:
            old_old += 1

    if len(new_sides_checked) != 4 * len(new_patch_ids):
        raise ValueError('Candidate has an incomplete set of new indexed sides')
    expected_counts = (12, 2) if enforce_s40_counts else None
    if expected_counts is not None and (new_old, new_new) != expected_counts:
        raise ValueError('Unexpected original STEP side join or internal quadrilateral count')
    two = sum(len(owners) == 2 for owners in incidence.values())
    one = sum(len(owners) == 1 for owners in incidence.values())
    if enforce_s40_counts and (
        len(proposed_patches), two, one,
    ) != (JOINT_EXPECTED_PATCHES, JOINT_EXPECTED_TWO_SIDED_SEAMS, JOINT_EXPECTED_OPEN_SIDES):
        raise ValueError('Global S40 candidate cardinality or seam census changed')
    return {
        'new_old_join_count': new_old,
        'new_new_internal_join_count': new_new,
        'old_old_join_count': old_old,
        'new_oriented_sides_checked': len(new_sides_checked),
        'new_unpaired_sides': 0,
        'two_sided_seams': two,
        'open_indexed_sides': one,
    }


def audit_new_coons_nets(
    original_points, candidate_points, patches, *,
    first_new=SELECTED_S3Y_PATCHES, tolerance_mm=2e-11,
    enforce_s40_counts=True,
):
    """Require all new interior controls equal the cubic Coons reconstruction.

    Existing prior points must be audited for changes by the earlier S3.Z.1
    mutation ledger. This function rejects independent replacement interiors,
    non-finite values, boundary/interior aliases and reused new interior IDs.
    """
    if not math.isfinite(tolerance_mm) or not 0 <= tolerance_mm <= 2e-11:
        raise ValueError('Coons identity tolerance cannot be relaxed')
    if len(candidate_points) < len(original_points):
        raise ValueError('Candidate removed inherited global controls')
    if enforce_s40_counts and (
        len(original_points), len(candidate_points), len(patches), first_new,
    ) != (
        SELECTED_S3Y_CONTROLS, JOINT_EXPECTED_CONTROLS,
        JOINT_EXPECTED_PATCHES, SELECTED_S3Y_PATCHES,
    ):
        raise ValueError('Frozen original S40 source-indexed cardinalities changed')
    prior_boundary_points = {i for patch in patches[:first_new] for i in patch}
    all_new_boundary_points = {
        i for patch in patches[first_new:] for name in ('bottom','right','top','left')
        for i in _indexed_side(patch,name)
    }
    checked_new_interiors = set()
    max_deviation = 0.0
    for patch_id in range(first_new, len(patches)):
        patch = patches[patch_id]
        for idx in patch:
            if not 0 <= idx < len(candidate_points):
                raise ValueError('Candidate indexed a nonexistent control')
        bottom = tuple(candidate_points[i] for i in _indexed_side(patch, 'bottom'))
        right = tuple(candidate_points[i] for i in _indexed_side(patch, 'right'))
        top = tuple(candidate_points[i] for i in reversed(_indexed_side(patch, 'top')))
        left = tuple(candidate_points[i] for i in reversed(_indexed_side(patch, 'left')))
        expected = coons_interior((bottom, right, top, left))
        boundary = {idx for label in ('bottom','right','top','left')
                    for idx in _indexed_side(patch,label)}
        for row in (1, 2):
            for col in (1, 2):
                idx = patch[4*row+col]
                if (idx in all_new_boundary_points or idx in boundary or
                    idx in checked_new_interiors or idx in prior_boundary_points):
                    raise ValueError('New Coons interior control aliases an existing patch boundary')
                if idx < len(original_points):
                    raise ValueError('New planar Coons interior overwrote a previously admitted control')
                checked_new_interiors.add(idx)
                point = candidate_points[idx]
                if len(point) != 3 or not all(math.isfinite(x) for x in point):
                    raise ValueError('New planar Coons interior is nonfinite or malformed')
                error = max(abs(point[k]-expected[row][col][k]) for k in range(3))
                if error > tolerance_mm:
                    raise ValueError('New interior differs from source-boundary cubic Coons interpolation')
                max_deviation = max(max_deviation, error)
    expected_count = 4 * (len(patches)-first_new)
    if len(checked_new_interiors) != expected_count:
        raise ValueError('Missing unique new Coons interior controls')
    return {
        'coons_interiors_checked': len(checked_new_interiors),
        'max_coons_identity_error_mm': max_deviation,
        'new_patch_count': len(patches)-first_new,
        'continuous_trimmed_CAD_equivalence_certified': False,
    }


def audit_final_candidate(prior_points, prior_patches, candidate_points, candidate_patches):
    """Produce a non-geometric combinatorial gate receipt for external native trial."""
    topology = audit_new_surface_topology(prior_patches, candidate_patches)
    coons = audit_new_coons_nets(prior_points, candidate_points, candidate_patches)
    return {'schema': 'apmesh-s3z2-original-s40-indexed-orientation-coons-gate-v1',
            'status': 'TOPOLOGY_ONLY_NOT_ADMITTED',
            'topology': topology, 'coons': coons,
            'source_native_face_classifier_executed': False,
            'original_CAD_mesh_generated': False}