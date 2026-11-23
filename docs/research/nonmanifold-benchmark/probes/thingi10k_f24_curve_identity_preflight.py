#!/usr/bin/env python3
"""Independently audit a PRIVATE original-derived BP against pinned APMesh curve rules.

This is a source-inspected mathematical preflight, not an execution of Geometry.
Only count/hash receipts may be published; never redistribute original mesh bytes.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from itertools import product
import hashlib
import json
import math
from pathlib import Path

PRIVATE_BP_SHA256 = '6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0'
PRIVATE_BP_BYTES = 538482
AMBIENT_EPSYLON_DEFAULT = 1e-7
READER_POINT_INTERN_EPSYLON = 1e-7
GRID_THRESHOLDS = (1e-7, 1e-5, 1e-3, 1e-2, 1e-1)
# Input reader's geometric curve order: bottom, right, top, left.
READER_SIDES = ((0, 1, 2, 3), (3, 7, 11, 15), (12, 13, 14, 15), (0, 4, 8, 12))
# Counterclockwise boundary order for the same four sides; top and left reverse.
BOUNDARY_SIDES = ((0, 1, 2, 3), (3, 7, 11, 15), (15, 14, 13, 12), (12, 8, 4, 0))
CPP_GIT_BLOBS = {
    'Geometry::VerifyCurveGeometry': '411cff31f274f260eabf1d4e43e09e46c3c5a6a9',
    'PointAdaptive::operator==': '92c77580d6778ee793c154d1f4f3dbe7e58ee34f',
    'PatchReader::ReaderFilePatches': 'a00fa0c712ae31380e08e557be4d199abf5d40ea',
    'runtime_state': 'd21ceb3397c7825bb50534be072261908c9b0e49',
    'runtime_config': '21438cd2f2921508832cdd833ed8eca067fb3bfd',
}
NEIGHBORS = tuple(product((-1, 0, 1), repeat=3))


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def read_bp(path: Path, *, private_identity: bool = False):
    require(path.is_file() and 0 < path.stat().st_size <= 2_000_000,
            'Missing, empty or oversized BP')
    if private_identity:
        require(path.stat().st_size == PRIVATE_BP_BYTES and sha256(path) == PRIVATE_BP_SHA256,
                'Original derived private BP bytes do not match F22')
    vertices, patches = [], []
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        tokens = line.split()
        require(tokens and line[0] in ('v', 'p') and not line.startswith((' ', '\t')),
                f'Malformed or unsupported BP line {n}')
        if tokens[0] == 'v':
            require(len(tokens) == 4, f'BP control arity at line {n}')
            point = tuple(map(float, tokens[1:]))
            require(all(math.isfinite(x) for x in point), f'Nonfinite BP control at line {n}')
            vertices.append(point)
        elif tokens[0] == 'p':
            require(len(tokens) == 17, f'BP patch arity at line {n}')
            ids = tuple(int(x) for x in tokens[1:])
            require(all(0 <= i < len(vertices) for i in ids),
                    f'Patch refers to a missing or future control at line {n}')
            patches.append(ids)
        else:
            raise ValueError(f'Unsupported BP record at line {n}')
    require(vertices and patches, 'Incomplete BP')
    return vertices, patches


def curve_controls(vertices, patch, side):
    return tuple(vertices[patch[k]] for k in side)


def canonical(curve):
    return min(curve, curve[::-1])


def curve_groups(vertices, patches):
    groups = defaultdict(list)
    for pi, patch in enumerate(patches):
        for side in range(4):
            c = curve_controls(vertices, patch, BOUNDARY_SIDES[side])
            groups[canonical(c)].append((pi, side, c))
    return groups


def within(a, b, threshold):
    return all(abs(x - y) <= threshold for x, y in zip(a, b))


def curves_approximately_equal(a, b, threshold):
    return (all(within(x, y, threshold) for x, y in zip(a, b)) or
            all(within(x, y, threshold) for x, y in zip(a, b[::-1])))


def bucket(point, threshold):
    return tuple(math.floor(x / threshold) for x in point)


def near_distinct_points(vertices, threshold):
    require(threshold > 0 and math.isfinite(threshold), 'Invalid tolerance')
    unique = tuple(set(vertices))
    grid = defaultdict(list)
    pairs = 0
    for pt in unique:
        b = bucket(pt, threshold)
        for delta in NEIGHBORS:
            for other in grid.get(tuple(b[i] + delta[i] for i in range(3)), ()):
                if within(pt, other, threshold):
                    pairs += 1
        grid[b].append(pt)
    return pairs


def near_distinct_curves(curves, threshold):
    require(threshold > 0 and math.isfinite(threshold), 'Invalid tolerance')
    # Both endpoints are indexed to avoid missing orientation-reversed matches.
    grid = defaultdict(set)
    pairs = 0
    for index, curve in enumerate(curves):
        candidates = set()
        for endpoint in (curve[0], curve[-1]):
            b = bucket(endpoint, threshold)
            for delta in NEIGHBORS:
                candidates.update(grid.get(tuple(b[i] + delta[i] for i in range(3)), ()))
        for i in candidates:
            if curves_approximately_equal(curve, curves[i], threshold):
                pairs += 1
        for endpoint in (curve[0], curve[-1]):
            grid[bucket(endpoint, threshold)].add(index)
    return pairs


def linear_curve_lookup_count(vertices, patches):
    # Reconstruct deterministic successful-match order from the C++ source's
    # four VerifyCurveGeometry calls. This counts visited curve entries, not CPU time.
    positions = {}
    count = 0
    visited = 0
    maximum = 0
    for patch in patches:
        for side in READER_SIDES:
            key = canonical(curve_controls(vertices, patch, side))
            if key in positions:
                search = positions[key] + 1
            else:
                search = len(positions)
                positions[key] = len(positions)
            visited += search
            maximum = max(maximum, search)
            count += 1
    return {'lookup_calls': count, 'linear_curve_candidates_visited': visited,
            'maximum_curve_candidates_visited_single_call': maximum,
            'curves_assuming_no_false_epsilon_matches': len(positions)}


def analyze(vertices, patches, *, require_closed=False):
    groups = curve_groups(vertices, patches)
    hist = Counter(len(group) for group in groups.values())
    invalid_orientation = sum(
        len(group) == 2 and group[0][2] != group[1][2][::-1]
        for group in groups.values()
    )
    if require_closed:
        require(len(vertices) == len(set(vertices)), 'Original candidate has duplicated BP controls')
        require(hist == {2: len(groups)} and invalid_orientation == 0,
                'Original candidate has unpaired or wrongly oriented shared edges')
        require(len(patches) == 876 and len(vertices) == 7886 and len(groups) == 1752,
                'Original F22 candidate patch/control/curve counts changed')
    distinct_curves = list(groups)
    tolerances = {}
    for t in GRID_THRESHOLDS:
        tolerances[f'{t:.0e}'] = {
            'distinct_control_pairs_approximately_equal': near_distinct_points(vertices, t),
            'distinct_curve_pairs_approximately_equal': near_distinct_curves(distinct_curves, t),
        }
    if require_closed:
        require(all(row['distinct_control_pairs_approximately_equal'] == 0 and
                    row['distinct_curve_pairs_approximately_equal'] == 0
                    for row in tolerances.values()),
                'Risk of tolerance-based false merge in original source curve semantics')
    return {
        'bp_control_records': len(vertices),
        'bp_patches': len(patches),
        'bp_curve_side_uses': 4 * len(patches),
        'geometrically_distinct_exact_curves': len(groups),
        'curve_incidence_histogram': dict(sorted((str(k), v) for k, v in hist.items())),
        'two_sided_groups_with_nonopposite_boundary_orientation': invalid_orientation,
        'epsylon_collision_screen': tolerances,
        'indexed_bp_successful_id_comparisons_under_original_find_control':
            sum(i + 1 for patch in patches for i in patch),
        **linear_curve_lookup_count(vertices, patches),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-bp', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Refusing to overwrite prior F24 receipt')
    try:
        vertices, patches = read_bp(args.private_bp, private_identity=True)
        details = analyze(vertices, patches, require_closed=True)
        report = {
            'schema': 'apmesh-f24-original-bp-curve-identity-source-preflight-v1',
            'model_id': 293137,
            'private_bp_sha256': PRIVATE_BP_SHA256,
            'source_cpp_git_blob_sha1': CPP_GIT_BLOBS,
            'default_epsylon_from_runtime_state': AMBIENT_EPSYLON_DEFAULT,
            'bp_point_intern_epsilon_from_reader': READER_POINT_INTERN_EPSYLON,
            'scope': 'INDEPENDENT_PYTHON_ORIGINAL_BP_PREFLIGHT_NOT_ORIGINAL_CPP_GEOMETRY_EXECUTION',
            'original_cpp_reader_or_geometry_executed': False,
            'native_mesher_executed': False,
            'scientific_model_admitted': False,
            'source_or_derivative_rights_cleared': False,
            **details,
        }
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(report, stream, sort_keys=True, indent=2)
            stream.write('\n')
        print(json.dumps({k: v for k, v in report.items() if k not in ('source_cpp_git_blob_sha1',)},
                         sort_keys=True, indent=2))
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(2, f'F24 curve preflight blocked: {exc}\n')


if __name__ == '__main__':
    main()
