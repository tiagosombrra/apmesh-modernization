#!/usr/bin/env python3
"""Independently audit a research four-sheet bicubic BP and its R3 sidecar.

Uses its own strict BP reader and independent de Casteljau evaluator.
Optional native BRep comparison checks the generated samples lie on source faces.
Does not import or invoke the BP producer.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

EXPECTED_PAIRS = (('A', 'B'), ('A', 'C'), ('B', 'VOID'), ('C', 'VOID'))
SLOTS = ((0, 1, 2, 3), (3, 7, 11, 15), (12, 13, 14, 15), (0, 4, 8, 12))
BUDGET = 2e-12


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_bp(text: str) -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]:
    """Implement the indexed BP grammar independently of the input generator."""
    vertices = []
    patches = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        line = line.split('//', 1)[0].split('#', 1)[0].strip()
        if not line:
            continue
        fields = line.split()
        if fields[0] == 'v':
            require(len(fields) == 4, f'Invalid vertex at {line_number}')
            point = tuple(float(x) for x in fields[1:])
            require(all(math.isfinite(x) for x in point), 'Nonfinite control')
            vertices.append(point)
        elif fields[0] == 'p':
            require(len(fields) == 17, f'Invalid patch at {line_number}')
            ids = tuple(int(x) for x in fields[1:])
            require(all(0 <= x < len(vertices) for x in ids), 'Forward/out-of-range control reference')
            patches.append(ids)
        else:
            raise ValueError('Invalid BP record')
    require(bool(patches), 'Empty BP')
    return vertices, patches


def casteljau(points, parameter):
    """Evaluate a cubic vector Bezier with de Casteljau subdivision."""
    remaining = [list(row) for row in points]
    while len(remaining) > 1:
        remaining = [[(1 - parameter) * a + parameter * b for a, b in zip(x, y)]
                     for x, y in zip(remaining, remaining[1:])]
    return tuple(remaining[0])


def surface(control_net, u, v):
    rows = [casteljau(control_net[4 * i:4 * i + 4], u) for i in range(4)]
    return casteljau(rows, v)


def audit(bp_text: str, sidecar: dict, native_brep=None) -> dict:
    """Audit exact control-sharing, topology, geometry, shape agreement and status."""
    vertices, patches = read_bp(bp_text)
    require(sidecar.get('schema') == 'apmesh-r3-bicubic-control-pilot-v1', 'Sidecar schema mismatch')
    require(hashlib.sha256(bp_text.encode('utf-8')).hexdigest() == sidecar.get('bp_sha256'), 'BP digest mismatch')
    require(len(vertices) == 52 and len(patches) == 4, 'Wrong four-patch fixture size')
    require(sidecar.get('patch_count') == 4 and sidecar.get('unique_control_vertex_count') == 52, 'Sidecar count drift')
    require(sidecar.get('g2_external_admission') == 'NOT_GRANTED', 'External admission overclaim')
    require(sidecar.get('apmesh_generation') == 'NOT_RUN', 'Generator execution overclaim')
    common = sidecar['common_curve']
    require(common['curve_id'] == 'C0' and common['control_vertex_ids'] == [0, 1, 2, 3], 'Missing canonical source curve')
    require(common['local_side'] == 3 and common['incident_patches'] == [0, 1, 2, 3], 'Wrong common incidence')
    require(len(sidecar['patches']) == 4, 'Missing patch metadata')
    require(len(sidecar['source_to_patches']) == 4, 'Missing source map')
    source_faces = set()
    unique_curves = set()
    hist = Counter()
    global_controls = set()
    max_geometry_error = 0.0
    native_max_error = None
    native_shapes = None
    if native_brep is not None:
        # Do not use the generator's source graph to decide which shape is expected.
        # Identify the four plane faces independently from the actual BRep centers.
        faces = native_brep.Faces()
        require(native_brep.isValid() and len(faces) == 4, 'Invalid native control BRep')
        native_shapes = {}
        for face in faces:
            ctr = face.Center()
            n = math.hypot(ctr.x, ctr.y)
            require(n > 0, 'Ambiguous native face center')
            axis = (round(ctr.x / n), round(ctr.y / n))
            require(axis not in native_shapes, 'Duplicate native radial face')
            native_shapes[axis] = face
        native_max_error = 0.0
    for pindex, (record, ids) in enumerate(zip(sidecar['patches'], patches)):
        require(record['patch_index'] == pindex and record['control_vertex_ids'] == list(ids), 'Patch index map mismatch')
        require(tuple(record['region_pair']) == EXPECTED_PAIRS[pindex], 'Wrong source region pair')
        require(len(ids) == len(set(ids)) == 16, 'Duplicate control within patch')
        require(tuple(ids[x] for x in SLOTS[3]) == (0, 1, 2, 3), 'Common edge references do not match')
        source = record['source_faces']
        require({x['body'] for x in source} == set(EXPECTED_PAIRS[pindex]) - {'VOID'}, 'Source provenance mismatch')
        for f in source:
            key = (f['body'], f['face_index'])
            require(key not in source_faces, 'Source face repeated across multiple patches')
            source_faces.add(key)
        require(len(record['sides']) == 4, 'Missing sides')
        for slot, offset in enumerate(SLOTS):
            s = record['sides'][slot]
            require(s['slot'] == slot and s['control_vertex_ids'] == [ids[x] for x in offset], 'Side control drift')
            if slot == 3:
                require(s['curve_id'] == 'C0' and s['canonical_direction'] == 'z_ascending', 'Wrong canonical central side')
            else:
                require(s['curve_id'] == f'P{pindex}:S{slot}', 'Wrong external boundary label')
            hist[s['curve_id']] += 1
            unique_curves.add(s['curve_id'])
        net = [vertices[x] for x in ids]
        ray = {'A/B': (0., 5.), 'A/C': (-5., 0.),
               'B/VOID': (5., 0.), 'C/VOID': (0., -5.)}['/'.join(record['region_pair'])]
        samples = (0., 0.125, 0.25, 0.5, 0.75, 0.875, 1.)
        for u in samples:
            for v in samples:
                observed = surface(net, u, v)
                expected = (u * ray[0], u * ray[1], -2.5 + 5. * v)
                error = max(abs(x-y) for x,y in zip(observed, expected))
                max_geometry_error = max(max_geometry_error, error)
                require(error <= BUDGET, 'Planar BP geometry differs from independent analytic oracle')
                if native_shapes and 0 < u < 1 and 0 < v < 1:
                    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
                    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
                    from OCP.gp import gp_Pnt
                    wanted = (round(ray[0]/5), round(ray[1]/5))
                    target = native_shapes.get(wanted)
                    require(target is not None, 'Missing native BRep radial face')
                    probe = BRepBuilderAPI_MakeVertex(gp_Pnt(*observed)).Vertex()
                    calc = BRepExtrema_DistShapeShape(probe, target.wrapped)
                    calc.Perform()
                    require(calc.IsDone(), 'Failed native BRep distance evaluation')
                    native_error = calc.Value()
                    native_max_error = max(native_max_error, native_error)
                    require(native_error <= 1e-9, 'BP surface is not on native BRep face')
        global_controls.update(ids)
    require(len(source_faces) == 6, 'Incomplete source-face mapping')
    require(len(global_controls) == 52, 'Unexpected unused/shared controls')
    require(len(unique_curves) == 13 and hist['C0'] == 4 and all(n == 1 for c,n in hist.items() if c != 'C0'), 'Wrong side-curve incidence')
    require(sidecar['unique_curve_count'] == 13, 'Incorrect sidecar distinct-curve count')
    require(all(vertices[x][:2] == (0., 0.) for x in range(4)), 'Shared curve has nonzero XY coordinates')
    require([vertices[x][2] for x in range(4)] == [-2.5, -2.5 + 5. / 3., -2.5 + 2. * 5. / 3., 2.5], 'Shared curve control mismatch')
    return {
        'schema': 'apmesh-r3-independent-analytic-audit-v1',
        'result': 'CONTROL_FIXTURE_CONSISTENT',
        'patches': 4,
        'unique_control_vertices': 52,
        'unique_curves': 13,
        'common_curve_incidence': 4,
        'shared_control_indices': [0, 1, 2, 3],
        'analytical_sample_max_abs_error': max_geometry_error,
        'native_brep_sample_max_distance': native_max_error,
        'source_face_uses': len(source_faces),
        'sample_points_per_patch': 49,
        'classification': 'CONTROL_ONLY_NOT_GENERATOR_QUALIFIED',
        'g2_external_admission': 'NOT_GRANTED',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bp', type=Path, required=True)
    parser.add_argument('--sidecar', type=Path, required=True)
    parser.add_argument('--native-brep', type=Path)
    args = parser.parse_args()
    native = None
    if args.native_brep:
        import cadquery as cq
        native = cq.Shape.importBrep(str(args.native_brep))
    result = audit(args.bp.read_text(encoding='utf-8'),
                   json.loads(args.sidecar.read_text(encoding='utf-8')), native)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
