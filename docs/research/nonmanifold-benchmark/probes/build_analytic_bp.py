#!/usr/bin/env python3
"""Construct a four-patch analytic bicubic BP fixture from a verified R2 graph.

This is a research-only analytic reconstruction, not general CAD conversion.
All four patches reuse the same four canonical BP vertex indices for C0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from validate_interface_graph import check as check_r2

SIDES = ((0, 1, 2, 3), (3, 7, 11, 15), (12, 13, 14, 15), (0, 4, 8, 12))


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def construct(graph: dict) -> tuple[str, dict]:
    """Return a parseable BP and provenance sidecar without calling a CAD fitter."""
    check_r2(graph)
    width = graph['geometry']['width']
    zmin, zmax = graph['reconstructed_spatial_curve']['endpoints'][0][2], graph['reconstructed_spatial_curve']['endpoints'][1][2]
    if not math.isclose(zmax - zmin, width, rel_tol=0, abs_tol=1e-10):
        raise ValueError('Noncanonical source spine length')
    vertices = [(0.0, 0.0, zmin + width * row / 3.0) for row in range(4)]
    patches = []
    side_records = []
    source_to_patches = []
    for patch_index, sheet in enumerate(graph['sheets']):
        rx, ry = sheet['radial_xy']
        rnorm = math.hypot(rx, ry)
        if not math.isclose(rnorm, width / 2, rel_tol=0, abs_tol=1e-10):
            raise ValueError('Unexpected source sheet radial extent')
        dx, dy = 2.0 * rx, 2.0 * ry
        control_ids = []
        for row in range(4):
            for col in range(4):
                if col == 0:
                    control_ids.append(row)
                else:
                    # The control net of a ruled planar surface is an exact
                    # bicubic degree-elevation of a bilinear parameterization.
                    u = col / 3.0
                    vertices.append((dx * u, dy * u, zmin + width * row / 3.0))
                    control_ids.append(len(vertices) - 1)
        sidemap = []
        for slot, offsets in enumerate(SIDES):
            curve_id = 'C0' if slot == 3 else f'P{patch_index}:S{slot}'
            ids = [control_ids[j] for j in offsets]
            sidemap.append({'slot': slot, 'curve_id': curve_id,
                            'canonical_direction': 'z_ascending' if slot == 3 else 'local_uv',
                            'control_vertex_ids': ids})
        patches.append({'patch_index': patch_index,
                        'region_pair': sheet['region_pair'],
                        'control_vertex_ids': control_ids,
                        'source_faces': sheet['source_faces'],
                        'sides': sidemap})
        side_records.extend({'patch_index': patch_index, **record} for record in sidemap)
        source_to_patches.append({'patch_index': patch_index, 'source_face_uses': sheet['source_faces']})
    if len(vertices) != 52:
        raise ValueError('Unexpected BP vertex budget')
    if any(p['sides'][3]['control_vertex_ids'] != [0, 1, 2, 3] for p in patches):
        raise ValueError('Shared central curve index identity is not canonical')
    rows = [
        '// Controlled analytic four-sheet non-manifold BP pilot',
        '// Source: R2 geometrical interface graph, not an admitted external model',
    ]
    rows.extend('v ' + ' '.join(format(value, '.17g') for value in vertex) for vertex in vertices)
    rows.extend('p ' + ' '.join(map(str, patch['control_vertex_ids'])) for patch in patches)
    bp = '\n'.join(rows) + '\n'
    manifest = {
        'schema': 'apmesh-r3-bicubic-control-pilot-v1',
        'scientific_scope': 'ANALYTIC_PLANAR_CONTROL_ONLY_NOT_GENERAL_CAD_CONVERTER',
        'source_scope': graph['scope'],
        'g2_external_admission': 'NOT_GRANTED',
        'g3_representation_scope': 'ANALYTIC_PLANAR_EXACT_ONLY',
        'coordinate_unit': graph['geometry']['coordinate_unit'],
        'patch_count': len(patches),
        'unique_control_vertex_count': len(vertices),
        'unique_curve_count': len(set(side['curve_id'] for side in side_records)),
        'common_curve': {'curve_id': 'C0', 'control_vertex_ids': [0, 1, 2, 3],
                         'incident_patches': [0, 1, 2, 3],
                         'local_side': 3, 'local_parameter': 'v_ascending',
                         'source_spatial_endpoints': graph['reconstructed_spatial_curve']['endpoints']},
        'patches': patches,
        'source_to_patches': source_to_patches,
        'bp_sha256': _digest(bp.encode('utf-8')),
        'native_brep_required_for_full_r3_gate': True,
        'apmesh_generation': 'NOT_RUN',
    }
    return bp, manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--graph', type=Path, required=True)
    parser.add_argument('--out-bp', type=Path, required=True)
    parser.add_argument('--out-sidecar', type=Path, required=True)
    args = parser.parse_args()
    graph = json.loads(args.graph.read_text(encoding='utf-8'))
    bp, manifest = construct(graph)
    args.out_bp.parent.mkdir(parents=True, exist_ok=True)
    args.out_sidecar.parent.mkdir(parents=True, exist_ok=True)
    args.out_bp.write_text(bp, encoding='utf-8')
    args.out_sidecar.write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'bp': str(args.out_bp), 'sidecar': str(args.out_sidecar),
                      'sha256': manifest['bp_sha256'], 'patches': manifest['patch_count'],
                      'unique_controls': manifest['unique_control_vertex_count']}))


if __name__ == '__main__':
    main()
