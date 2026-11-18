#!/usr/bin/env python3
"""Exact-rational Bernstein radial envelope over explicitly supplied IEEE-754 floats.

The result is mathematically exact for the submitted finite binary float control
values and axis/radius components, not for uncertainties in native CAD import,
source BRep tolerances, Hausdorff distance, or continuous trimmed face coverage.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb, isfinite


PILOT_BUDGET = Fraction(1, 1000)


def _fraction(number):
    """Interpret a finite IEEE-754 value as its exact rational value."""
    if isinstance(number, bool):
        raise ValueError("Boolean is not a valid numeric coordinate")
    if isinstance(number, Fraction):
        result = number
    elif isinstance(number, int):
        result = Fraction(number)
    elif isinstance(number, float) and isfinite(number):
        result = Fraction.from_float(number)
    else:
        raise ValueError("Coordinate is not a finite real IEEE-754 value")
    return result


def _xyz(value):
    if len(value) != 3:
        raise ValueError("Vector must have three coordinates")
    return tuple(_fraction(q) for q in value)


@lru_cache(maxsize=16)
def _product_weights():
    return tuple(tuple(Fraction(comb(3, i) * comb(3, j), comb(6, i+j))
                       for j in range(4)) for i in range(4))


def cylinder_squared_radius_net(control_points, axis_origin, axis_direction, radius):
    """Compute the exact 7x7 bi-degree-(6,6) radial squared Bernstein net.

    The original cylinder direction need not be represented as a perfectly
    normalized binary vector: project using (V dot D)^2/(D dot D).
    """
    if len(control_points) != 16:
        raise ValueError("Exactly sixteen bicubic controls are required")
    origin = _xyz(axis_origin)
    direction = _xyz(axis_direction)
    radius = _fraction(radius)
    if radius <= 0:
        raise ValueError("Original cylinder radius must be positive")
    norm2 = sum(d*d for d in direction)
    if norm2 <= 0:
        raise ValueError("Degenerate native cylinder direction")
    vectors = [tuple(p[k]-origin[k] for k in range(3)) for p in map(_xyz,control_points)]
    projections = [sum(p[k]*direction[k] for k in range(3)) for p in vectors]
    weights = _product_weights()
    result = [[Fraction(0) for _ in range(7)] for _ in range(7)]
    for i in range(4):
        for j in range(4):
            row = i*4+j
            for k in range(4):
                for l in range(4):
                    col = k*4+l
                    dot = sum(vectors[row][p]*vectors[col][p] for p in range(3))
                    radial2 = dot-projections[row]*projections[col]/norm2
                    result[i+k][j+l] += weights[i][k]*weights[j][l]*radial2
    return tuple(tuple(row) for row in result), radius


def _split_half(coefficients, axis):
    """Split a degree-six Bernstein net at 1/2 using exact de Casteljau."""
    if axis not in (0,1):
        raise ValueError("Only two source parameter axes are supported")
    tensor = [list(row) for row in coefficients]
    if axis == 1:
        tensor = [list(row) for row in zip(*tensor)]
    levels = [tensor]
    while len(levels[-1]) > 1:
        prev = levels[-1]
        levels.append([[ (prev[i][k]+prev[i+1][k])/2 for k in range(7)]
                       for i in range(len(prev)-1)])
    first = [list(level[0]) for level in levels]
    second = [list(level[-1]) for level in reversed(levels)]
    if axis == 1:
        first = [list(row) for row in zip(*first)]
        second = [list(row) for row in zip(*second)]
    return tuple(tuple(row) for row in first),tuple(tuple(row) for row in second)


def certify_cylinder_radial(control_points, origin, direction, radius,
                            *, budget=PILOT_BUDGET, max_depth=16, max_nodes=8192):
    """Conservatively certify radius error <= 0.001 via exact squared bands.

    An inconclusive result MUST block CAD admission. The non-overlap of the
    float-defined radial polynomial and the forbidden band is exact rational
    arithmetic. It does not include any uncertainty around the input floats.
    """
    if _fraction(budget) != PILOT_BUDGET:
        raise ValueError("Original 0.001 mm geometric budget may not be changed")
    if not isinstance(max_depth,int) or not 0 <= max_depth <= 22:
        raise ValueError("Invalid maximum exact Bernstein subdivision depth")
    if not isinstance(max_nodes,int) or not 1 <= max_nodes <= 65536:
        raise ValueError("Invalid exact Bernstein node resource budget")
    net, r = cylinder_squared_radius_net(control_points, origin, direction, radius)
    floor = (r-PILOT_BUDGET)**2 if r >= PILOT_BUDGET else Fraction(0)
    ceil = (r+PILOT_BUDGET)**2
    remaining = [(net,0)]
    leaves = 0
    nodes = 0
    worst_depth = 0
    worst_lower = None
    worst_upper = None
    status = 'CERTIFIED_WITHIN_FLOAT_DEFINED_CYLINDER'
    while remaining:
        if nodes >= max_nodes:
            status = "INCONCLUSIVE_EXACT_BERNSTEIN_RESOURCE_LIMIT"
            break
        patch,depth = remaining.pop()
        nodes += 1
        values = [v for row in patch for v in row]
        low, high = min(values),max(values)
        worst_lower = low if worst_lower is None else min(worst_lower,low)
        worst_upper = high if worst_upper is None else max(worst_upper,high)
        if floor <= low and high <= ceil:
            leaves += 1
            worst_depth = max(worst_depth,depth)
            continue
        if low > ceil or high < floor:
            status = 'CERTIFIED_OUTSIDE_GEOMETRIC_BUDGET'
            break
        if depth == max_depth:
            status = 'INCONCLUSIVE_EXACT_BERNSTEIN_DEPTH_LIMIT'
            break
        left,right = _split_half(patch,depth%2)
        remaining.extend(((left,depth+1),(right,depth+1)))
    return {
        'status': status,
        'passed': status == 'CERTIFIED_WITHIN_FLOAT_DEFINED_CYLINDER',
        'exact_rational_arithmetic_over_input_floats':True,
        'native_cad_input_uncertainty_certified':False,
        'continuous_original_trimmed_face_certified':False,
        'source_model_3plus_nonmanifold_verified':False,
        'fixed_budget_mm':'0.001',
        'subdivision_leaves_verified':leaves,
        'subdivision_nodes_visited':nodes,
        'max_subdivision_nodes':max_nodes,
        'deepest_verified_level':worst_depth,
        'termination_depth_limit':max_depth,
    }


def native_cylinder_components(cylinder):
    """Extract geometry as plain floats without claiming native BRep certainty."""
    origin = cylinder.Location()
    axis = cylinder.Axis().Direction()
    return ((float(origin.X()),float(origin.Y()),float(origin.Z())),
            (float(axis.X()),float(axis.Y()),float(axis.Z())),
            float(cylinder.Radius()))


def require_exact_native_cylinder_envelope(control_points, cylinder, *, max_depth=16):
    """Mandatory fail-closed exact-rational gate for a native gp_Cylinder.

    Input floats are interpreted exactly; this does not certify uncertainty
    in their derivation from the original STEP source.
    """
    origin,direction,radius = native_cylinder_components(cylinder)
    receipt = certify_cylinder_radial(control_points,origin,direction,radius,
                                      max_depth=max_depth)
    if not receipt['passed']:
        raise ValueError('Exact rational radial gate failed: '+receipt['status'])
    return receipt
