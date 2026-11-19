#!/usr/bin/env python3
"""Conservative STEP source-identity census for candidate non-manifold sheets.

A Part 21 marker or spatial edge overlap is not a shared EDGE_CURVE identity.
Only unique ADVANCED_FACE owners of the same original EDGE_CURVE count toward
source three-plus-sheet incidence. This probe does not perform OCCT sewing.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

MAX_INPUT = 20_000_000
MAX_RECORDS = 300_000
ENTITY = re.compile(r"^#(\d+)\s*=\s*([A-Za-z_][A-Za-z_0-9]*)\s*\((.*)\)$", re.S)
COMPLEX_ENTITY = re.compile(r"^#(\d+)\s*=\s*\(", re.S)
REF = re.compile(r"#(\d+)")
NUM = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?"
POINT = re.compile(r"^\s*'(?:(?:'')|[^'])*'\s*,\s*\(\s*("+NUM+r")\s*,\s*("+NUM+r")\s*,\s*("+NUM+r")\s*\)\s*$")


def data_records(data: bytes):
    """Tokenize source records without splitting quoted semicolons or comments."""
    if len(data) > MAX_INPUT:
        raise ValueError("STEP exceeds the conservative input-size limit")
    text = data.decode('latin-1')
    marker = re.search(r"(?im)^\s*DATA\s*;", text)
    if not marker:
        raise ValueError("Part 21 DATA section not found")
    pos = marker.end()
    quoted = False
    commented = False
    buf = []
    while pos < len(text):
        c = text[pos]
        n = text[pos + 1] if pos + 1 < len(text) else ''
        if commented:
            if c == '*' and n == '/':
                commented = False
                pos += 2
            else:
                pos += 1
            continue
        if not quoted and c == '/' and n == '*':
            commented = True
            pos += 2
            continue
        if c == "'":
            if quoted and n == "'":
                buf.extend((c, n))
                pos += 2
                continue
            quoted = not quoted
        if c == ';' and not quoted:
            rec = ''.join(buf).strip()
            if rec.upper() == 'ENDSEC':
                return
            if rec.upper().startswith('END-ISO-10303-21'):
                raise ValueError('Unterminated DATA section before Part 21 end marker')
            if rec:
                yield rec
            buf = []
        else:
            buf.append(c)
        pos += 1
    raise ValueError("Unterminated DATA section")


def parse_entities(data: bytes):
    """Parse simple Part 21 instances used by face/edge topology chains."""
    result = {}
    for index, record in enumerate(data_records(data), 1):
        if index > MAX_RECORDS:
            raise ValueError("Too many STEP DATA records")
        match = ENTITY.fullmatch(record)
        if match:
            number = int(match[1])
            etype = match[2].upper()
            content = match[3]
        else:
            complex_match = COMPLEX_ENTITY.match(record)
            if not complex_match:
                raise ValueError(f"Unsupported or invalid STEP instance: {record[:80]}")
            number = int(complex_match[1])
            etype = 'COMPLEX_INSTANCE'
            content = record[complex_match.end():]
        if number in result:
            raise ValueError(f"Duplicate STEP instance #{number}")
        result[number] = (etype, tuple(map(int, REF.findall(content))), content)
    if not result:
        raise ValueError("STEP contains no parsed entities")
    return result


def source_census(data: bytes):
    """Count distinct source faces per STEP EDGE_CURVE without epsilon-welding."""
    entities = parse_entities(data)
    faces = sorted(i for i, (kind, _, _) in entities.items() if kind == 'ADVANCED_FACE')
    if not faces:
        raise ValueError('No ADVANCED_FACE instances found')
    owners = defaultdict(set)
    uses = defaultdict(int)
    for face in faces:
        kind, face_refs, _ = entities[face]
        bounds = [i for i in face_refs if entities.get(i, ('',))[0] in ('FACE_BOUND', 'FACE_OUTER_BOUND')]
        if not bounds:
            raise ValueError(f'Face #{face} has no supported FACE_BOUND')
        for bound in bounds:
            loops = [i for i in entities[bound][1] if entities.get(i, ('',))[0] == 'EDGE_LOOP']
            if len(loops) != 1:
                raise ValueError(f'Face #{face} bound #{bound} has no unique EDGE_LOOP')
            for loop in loops:
                oriented = [i for i in entities[loop][1] if entities.get(i, ('',))[0] == 'ORIENTED_EDGE']
                if not oriented:
                    raise ValueError(f'Face #{face} loop #{loop} has no ORIENTED_EDGE')
                for oid in oriented:
                    edges = [i for i in entities[oid][1] if entities.get(i, ('',))[0] == 'EDGE_CURVE']
                    if len(edges) != 1:
                        raise ValueError(f'ORIENTED_EDGE #{oid} has no unique EDGE_CURVE')
                    edge = edges[0]
                    owners[edge].add(face)
                    uses[(face, edge)] += 1
    hist = dict(sorted(Counter(len(s) for s in owners.values()).items()))
    positive = [{'original_source_edge_curve_id': edge,
                 'original_source_face_ids': sorted(face_ids)}
                for edge, face_ids in sorted(owners.items()) if len(face_ids) >= 3]
    repeated = [{'original_source_face_id': face, 'edge_curve_id': edge, 'uses': n}
                for (face, edge), n in sorted(uses.items()) if n > 1]
    return {
        'schema': 'apmesh-external-step-original-edge-identity-v1',
        'source_sha256': sha256(data).hexdigest(),
        'source_face_count': len(faces),
        'source_edge_curve_count': sum(k == 'EDGE_CURVE' for k, _, _ in entities.values()),
        'used_original_edge_curve_count': len(owners),
        'source_incidence_histogram': {str(k): v for k, v in hist.items()},
        'source_edge_three_plus_count': len(positive),
        'three_plus_original_edges': positive,
        'repeat_uses_by_same_face': repeated,
        'classification': ('SOURCE_EDGE_NONMANIFOLD_POSITIVE_PENDING_NATIVE_AUDIT'
                           if positive else 'NO_THREE_PLUS_SOURCE_EDGE'),
        'step_marker_is_not_incidence_proof': True,
        'geometric_coincidence_or_sewing_counted_as_original_identity': False,
        'cad_native_import_executed': False,
        'apmesh_tri_quad_executed': False,
    }


def source_linear_edge(entities, edge_id):
    """Return exact source endpoint positions for a straight EDGE_CURVE."""
    kind, refs, _ = entities[edge_id]
    if kind != 'EDGE_CURVE':
        raise ValueError('Selected instance is not an EDGE_CURVE')
    verts = [i for i in refs if entities.get(i, ('',))[0] == 'VERTEX_POINT']
    lines = [i for i in refs if entities.get(i, ('',))[0] == 'LINE']
    if len(verts) != 2 or len(lines) != 1:
        raise ValueError(f'EDGE_CURVE #{edge_id} is not a simple source line')
    points = []
    for vertex in verts:
        ids = [i for i in entities[vertex][1] if entities.get(i, ('',))[0] == 'CARTESIAN_POINT']
        if len(ids) != 1:
            raise ValueError(f'Cannot resolve source VERTEX_POINT #{vertex}')
        match = POINT.fullmatch(entities[ids[0]][2])
        if not match:
            raise ValueError(f'Cannot parse exact Cartesian point #{ids[0]}')
        points.append(tuple(Fraction(s) for s in match.groups()))
    if points[0] == points[1]:
        raise ValueError('Degenerate source straight edge')
    return tuple(points)


def exact_common_collinear_overlap(data: bytes, edge_ids: tuple[int, ...]):
    """Measure a straight, three-way common overlap without merging identities."""
    if len(edge_ids) < 3 or len(set(edge_ids)) != len(edge_ids):
        raise ValueError('Select three or more distinct source EDGE_CURVE IDs')
    entities = parse_entities(data)
    intervals = [source_linear_edge(entities, e) for e in edge_ids]
    origin, other = intervals[0]
    direction = tuple(other[i] - origin[i] for i in range(3))
    axis = next(i for i in range(3) if direction[i] != 0)
    def projection(point):
        relative = tuple(point[i] - origin[i] for i in range(3))
        # Each component must agree with the same line parameter.
        t = relative[axis] / direction[axis]
        if any(relative[i] != t * direction[i] for i in range(3)):
            raise ValueError('Selected source edges are not exactly collinear')
        return t
    param_ranges = [sorted((projection(a), projection(b))) for a, b in intervals]
    low = max(pair[0] for pair in param_ranges)
    high = min(pair[1] for pair in param_ranges)
    common = max(Fraction(0), high - low)
    # Convert rational line parameters to the selected axis; expose only
    # an exact axis-coordinate span, not an uncertified Euclidean distance.
    base = origin[axis]
    coord_low = base + low * direction[axis]
    coord_high = base + high * direction[axis]
    return {
        'distinct_original_source_edge_ids': list(edge_ids),
        'axis': 'xyz'[axis],
        'original_axis_coordinate_interval': [str(min(coord_low, coord_high)),
                                             str(max(coord_low, coord_high))],
        'positive_three_way_source_line_overlap': common > 0,
        'shared_original_edge_curve_identity': False,
        'occt_sewing_executed': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--step', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--require-source-three-plus', action='store_true')
    parser.add_argument('--collinear-edges', type=int, nargs='+')
    args = parser.parse_args()
    raw = args.step.read_bytes()
    report = source_census(raw)
    if args.collinear_edges:
        report['selected_collinear_overlap'] = exact_common_collinear_overlap(raw, tuple(args.collinear_edges))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'classification': report['classification'],
                      'source_edge_three_plus_count': report['source_edge_three_plus_count']},
                     sort_keys=True))
    return 3 if args.require_source_three_plus and not report['source_edge_three_plus_count'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
