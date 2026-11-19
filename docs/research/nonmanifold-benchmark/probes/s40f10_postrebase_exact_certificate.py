#!/usr/bin/env python3
"""Certify exact orientation of the eight S40-F9 patches AFTER S3.Y reindexing.

This is a fail-closed, geometry-only certificate for the decimal-defined final
164-patch BP. It does not certify source STEP trim, continuous CAD error,
validity of all parent patches, or any APMesh TRI/QUAD output.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256

from s40f8_exact_planar_jacobian import (
    FACE_IDS,
    NORMALS,
    certify_strict_sign,
    jacobian_net,
)

PARENT_PATCHES = 156
JOINED_PATCHES = 164
JOINED_CONTROLS = 1743


def _parse_joined_exact(data: bytes):
    """Parse serialized BP decimals as rationals, rejecting malformed data."""
    points = []
    patches = []
    for line_number, original in enumerate(data.decode("utf-8").splitlines(), 1):
        record = original.split("//", 1)[0].strip()
        if not record:
            continue
        tokens = record.split()
        if tokens[0] == "v" and len(tokens) == 4 and not patches:
            points.append(tuple(Fraction(item) for item in tokens[1:]))
        elif tokens[0] == "p" and len(tokens) == 17:
            indices = tuple(int(item) for item in tokens[1:])
            if any(index < 0 or index >= len(points) for index in indices):
                raise ValueError(f"Out-of-bounds patch control at line {line_number}")
            patches.append(indices)
        else:
            raise ValueError(f"Unsupported BP record at line {line_number}")
    if len(points) != JOINED_CONTROLS or len(patches) != JOINED_PATCHES:
        raise ValueError("Joined BP must contain exactly 1743 controls and 164 patches")
    return points, patches


def certify_postrebase_eight(data: bytes) -> dict:
    """Prove J > 0 on each joined F9 patch using serialized decimal controls."""
    points, patches = _parse_joined_exact(data)
    certificates = []
    for local_index, face_id in enumerate(FACE_IDS):
        joined_index = PARENT_PATCHES + local_index
        net = jacobian_net(points, patches[joined_index], NORMALS[face_id])
        proof = certify_strict_sign(net, max_depth=12)
        if proof["status"] != "CERTIFIED_POSITIVE":
            raise ValueError(
                f"Joined patch {joined_index} (STEP face #{face_id}) "
                "has no exact strict-positive Jacobian certificate"
            )
        certificates.append({
            "joined_patch_index": joined_index,
            "original_step_face_id": face_id,
            "status": proof["status"],
            "strict_lower_bound_mm2": proof["strict_lower_bound_mm2"],
            "nodes_visited": proof["nodes_visited"],
        })
    return {
        "schema": "apmesh-s40f10-postrebase-exact-jacobian-v1",
        "status": "CERTIFIED_STRICT_POSITIVE_POSTREBASE_DECIMAL_BP",
        "joined_bp_sha256": sha256(data).hexdigest(),
        "joined_patch_count": JOINED_PATCHES,
        "joined_control_count": JOINED_CONTROLS,
        "new_source_patch_indices": list(range(PARENT_PATCHES, JOINED_PATCHES)),
        "certified_postrebase_patch_count": len(certificates),
        "certificates": certificates,
        "parent_156_patch_regularities_certified": False,
        "original_step_native_trim_or_continuous_hausdorff_certified": False,
        "apmesh_tri_quad_executed": False,
    }
