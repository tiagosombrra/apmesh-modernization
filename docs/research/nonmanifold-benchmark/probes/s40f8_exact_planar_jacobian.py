#!/usr/bin/env python3
"""Exact Bernstein enclosure of the signed Jacobian of indexed bicubic planar patches.

All decimal BP controls are treated as exact rational coordinates. The result
certifies only those decimal-defined patches, not the original STEP trimming.
"""
from __future__ import annotations

from fractions import Fraction
from math import comb
from hashlib import sha256
from pathlib import Path
import argparse
import json

BOUND_MM2 = Fraction(-5, 10**11)

F6_SHA256 = '72b8756c948a7a7da19c9f2a9a7099673e81a30573f19e4820abf27ba720f0a7'
FACE_IDS = (1279, 1279, 1386, 1386, 3269, 3269, 3485, 3485)
NORMALS = {1279: (0, 0, -1), 1386: (0, 0, -1), 3269: (1, 0, 0), 3485: (-1, 0, 0)}


def parse_decimal_bp(data: bytes):
    """Parse the original BP with exact decimal rational coordinates."""
    points, patches = [], []
    for line_no, raw in enumerate(data.decode('utf-8').splitlines(), 1):
        row = raw.split('//', 1)[0].strip()
        if not row:
            continue
        words = row.split()
        if words[0] == 'v' and len(words) == 4 and not patches:
            points.append(tuple(Fraction(w) for w in words[1:]))
        elif words[0] == 'p' and len(words) == 17:
            patch = tuple(int(v) for v in words[1:])
            if any(v < 0 or v >= len(points) for v in patch):
                raise ValueError(f'Invalid index at BP line {line_no}')
            patches.append(patch)
        else:
            raise ValueError(f'Invalid BP record at line {line_no}')
    if len(points) != 104 or len(patches) != 8:
        raise ValueError('Original S40-F6 private atlas cardinality changed')
    return points, patches


def bernstein_product(a, degree_a, b, degree_b):
    """Multiply two exact bivariate Bernstein polynomials."""
    au, av = degree_a
    bu, bv = degree_b
    cu, cv = au + bu, av + bv
    result = [[Fraction(0) for _ in range(cv + 1)] for _ in range(cu + 1)]
    for i in range(au + 1):
        for j in range(av + 1):
            if not a[i][j]:
                continue
            for k in range(bu + 1):
                for l in range(bv + 1):
                    if not b[k][l]:
                        continue
                    scale = Fraction(comb(au, i) * comb(bu, k), comb(cu, i+k)) * \
                            Fraction(comb(av, j) * comb(bv, l), comb(cv, j+l))
                    result[i+k][j+l] += a[i][j] * b[k][l] * scale
    return result


def jacobian_net(points, patch, normal):
    """Compute the exact bidegree-(5,5) Bernstein net of n dot (du cross dv)."""
    # The BP layout is row-major: point[j*4+i] is control (u=i,v=j).
    grid = [[points[patch[4*j+i]] for j in range(4)] for i in range(4)]
    du = [[[3*(grid[i+1][j][c]-grid[i][j][c]) for j in range(4)] for i in range(3)] for c in range(3)]
    dv = [[[3*(grid[i][j+1][c]-grid[i][j][c]) for j in range(3)] for i in range(4)] for c in range(3)]
    output = [[Fraction(0) for _ in range(6)] for _ in range(6)]
    for c in range(3):
        if normal[c] == 0:
            continue
        x,y = (c+1)%3,(c+2)%3
        pos = bernstein_product(du[x], (2,3), dv[y], (3,2))
        neg = bernstein_product(du[y], (2,3), dv[x], (3,2))
        for i in range(6):
            for j in range(6):
                output[i][j] += normal[c]*(pos[i][j]-neg[i][j])
    return output


def halve_curve(control):
    """Subdivide Bernstein controls at exactly t=1/2 using rational arithmetic."""
    levels = [list(control)]
    while len(levels[-1]) > 1:
        levels.append([(a+b)/2 for a,b in zip(levels[-1][:-1], levels[-1][1:])])
    return [level[0] for level in levels], [level[-1] for level in reversed(levels)]


def split_net(net, axis):
    """Subdivide a tensor-product Bernstein surface in one parameter."""
    if axis == 0:
        left, right = [[None]*len(net[0]) for _ in range(len(net))], [[None]*len(net[0]) for _ in range(len(net))]
        for j in range(len(net[0])):
            l, r = halve_curve([row[j] for row in net])
            for i in range(len(net)):
                left[i][j], right[i][j] = l[i], r[i]
    else:
        left, right = [], []
        for row in net:
            l, r = halve_curve(row)
            left.append(l)
            right.append(r)
    return left, right


def certify_strict_sign(net, *, max_depth=12):
    """Prove strict positivity by exact Bernstein convex-hull subdivisions.

    This is a sufficient criterion. A negative result is inconclusive rather
    than proof of a fold unless a strictly negative enclosure is obtained.
    """
    pending = [(net, 0)]
    checked = 0
    leaves = 0
    lower = None
    upper = None
    deepest = 0
    while pending:
        patch, depth = pending.pop()
        checked += 1
        values = [v for row in patch for v in row]
        lo, hi = min(values), max(values)
        deepest = max(deepest, depth)
        if hi <= 0:
            return {'status':'NONPOSITIVE_CERTIFIED', 'nodes_visited':checked, 'depth':depth,
                    'certified_nonpositive_upper_bound':float(hi)}
        if lo > 0:
            leaves += 1
            lower = lo if lower is None else min(lower, lo)
            upper = hi if upper is None else max(upper, hi)
            continue
        if depth >= max_depth:
            return {'status':'INCONCLUSIVE', 'nodes_visited':checked, 'depth':depth,
                    'mixed_coefficient_min':float(lo), 'mixed_coefficient_max':float(hi)}
        for child in split_net(patch, depth%2):
            pending.append((child,depth+1))
    return {'status':'CERTIFIED_POSITIVE', 'nodes_visited':checked, 'leaf_boxes':leaves,
            'max_depth':deepest, 'strict_lower_bound_mm2':float(lower),
            'upper_bound_mm2':float(upper)}


def audit_f6(data, *, max_depth=12):
    """Check exact original F6 SHA and prove the signed-Jacobian certificate."""
    if sha256(data).hexdigest() != F6_SHA256:
        raise ValueError('Pinned private S40-F6 BP SHA-256 mismatch')
    points, patches = parse_decimal_bp(data)
    output = []
    for patch_index, patch in enumerate(patches):
        face_id=FACE_IDS[patch_index]
        net=jacobian_net(points, patch, NORMALS[face_id])
        result=certify_strict_sign(net, max_depth=max_depth)
        corners = {'u0v0':net[0][0], 'u1v0':net[5][0],
                   'u0v1':net[0][5], 'u1v1':net[5][5]}
        all_bernstein = [value for row in net for value in row]
        # An exact Bernstein convex hull bounds J(u,v) over the entire square,
        # irrespective of sparse sampling or any native CAD import.
        exact_lower = min(all_bernstein)
        if exact_lower < BOUND_MM2:
            raise ValueError('F6 Jacobian falls below the predeclared -5e-11 mm2 enclosure')
        neg = [key for key,value in corners.items() if value < 0]
        zero = [key for key,value in corners.items() if value == 0]
        # A negative corner yields a negative Jacobian in an arbitrarily
        # small nonempty neighborhood by continuity. It cannot be accepted
        # as a strictly orientation-preserving closed bicubic parameterization.
        if neg:
            classification = 'EXACT_NEGATIVE_CORNER_STRICT_GATE_FAIL'
        elif zero:
            classification = 'EXACT_ZERO_CORNER_STRICT_GATE_FAIL'
        elif result['status'] == 'CERTIFIED_POSITIVE':
            classification = 'CERTIFIED_STRICT_POSITIVE'
        else:
            classification = 'STRICT_GATE_INCONCLUSIVE'
        output.append({'patch_index':patch_index,
                       'original_source_face_id':face_id,
                       'classification':classification,
                       'corner_jacobian_signs':{
                           key: 'negative' if value < 0 else 'zero' if value == 0
                           else 'positive' for key,value in corners.items()},
                       'minimum_corner_jacobian_mm2':float(min(corners.values())),
                       'exact_bernstein_lower_bound_mm2':float(exact_lower),
                       'certified_J_greater_than_minus_5e_minus_11_mm2':True,
                       'corners_have_exact_negative':bool(neg),
                       'corners_have_exact_zero':bool(zero), **result})
    return {'schema':'apmesh-s40f8-exact-bernstein-planar-jacobian-v1',
            'input_bp_sha256':F6_SHA256, 'patches':len(patches),'faces':sorted(set(FACE_IDS)),
            'certificates':output,
            'all_jacobians_bounded_below_minus_5e_minus_11_mm2':True,
            'all_jacobians_strictly_positive':all(r['classification']=='CERTIFIED_STRICT_POSITIVE' for r in output),
            'original_cad_natively_audited':False,
            'joined_with_s3y':False, 'new_faces_admitted':0}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-f6-bp',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--max-depth',type=int,default=12)
    args=parser.parse_args()
    if args.max_depth < 0 or args.max_depth > 18:
        parser.error('max-depth must belong to [0,18]')
    report=audit_f6(args.private_f6_bp.read_bytes(),max_depth=args.max_depth)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='certificates'},sort_keys=True))
    return 0 if report['all_jacobians_strictly_positive'] else 3

if __name__ == '__main__':
    raise SystemExit(main())
