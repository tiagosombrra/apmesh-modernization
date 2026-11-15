"""Independent finite-grid QUAD/TRI multi-objective comparison.

This is a reproducible dominance diagnostic, never an adaptive acceptance
policy, universal quality threshold or permission to replace a Patch owner.
"""
import math

COMMON = {
    "max_xyz": "min",
    "rms_source_area": "min",
    "elements": "min",
    "nodes": "min",
    "quad_uv_area": "max",
    "min_scaled_jacobian": "max",
    "min_warpage_cosine": "max",
}
PROFILES = {
    "uv_area_profile": dict(COMMON),
    "quad_count_profile": {**COMMON, "quads": "max"},
}
REQUIRED = frozenset({*COMMON, "quads", "triangles"})


def _check_records(records):
    if not isinstance(records, dict) or not records:
        raise ValueError("Missing measured physical mesh profiles")
    for name, entry in records.items():
        if not isinstance(name, str) or not name or not isinstance(entry, dict):
            raise ValueError("Invalid physical candidate identity")
        if set(entry) != REQUIRED:
            raise ValueError("Missing, foreign or unmeasured physical comparison fields")
        for field, value in entry.items():
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError("Nonfinite or nonnumeric measured comparison")
            if field in ("nodes", "quads", "triangles", "elements"):
                if type(value) is not int or value <= 0:
                    raise ValueError("Invalid physical mesh element/node count")
            elif field == "quad_uv_area":
                if not 0 < value < 1:
                    raise ValueError("Invalid source QUAD UV area fraction")
            elif value <= 0:
                raise ValueError("Non-positive physical source quality/error")
        if entry["quads"] + entry["triangles"] != entry["elements"]:
            raise ValueError("Mixed element count does not match typed faces")


def _dominates(a, b, directions, tol=1e-12):
    # All compared source-error measurements share the same original UV sites.
    strictly_better = False
    for key, direction in directions.items():
        av, bv = a[key], b[key]
        if direction == "min":
            if av > bv + tol:
                return False
            strictly_better |= av < bv - tol
        elif direction == "max":
            if av < bv - tol:
                return False
            strictly_better |= av > bv + tol
        else:
            raise ValueError("Unknown optimization direction")
    return strictly_better


def audit_pareto_profiles(records):
    """Compute both scoped fronts without selecting or adopting a mesh."""
    _check_records(records)
    order = sorted(records)
    profiles = {}
    for name, directions in PROFILES.items():
        domination = {
            target: [other for other in order if other != target and
                     _dominates(records[other], records[target], directions)]
            for target in order
        }
        profiles[name] = {
            "objective_directions": dict(directions),
            "nondominated": [target for target in order if not domination[target]],
            "dominated_by": domination,
        }
    return {"source": "independent_common_4096_uv_sites",
            "profiled_not_scientifically_accepted": True,
            "adaptive_epochs": 0, "measurements": records, "profiles": profiles}
