#!/usr/bin/env python3
"""Reconcile original APMesh TRI patch seams by source topology, not XYZ welding.

Only explicit shared native curve incidences may merge vertex IDs. The source STL,
private BP, original OBJ and full-precision snapshot are never written to Git.
The stitched OBJ is a NEW private derivative, not an original APMesh export.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys

import thingi10k_f27_native_tri_evidence as f27

UVS = ((0., 0.), (1., 0.), (1., 1.), (0., 1.), (.5, .5))
CORNERS = ((0., 0.), (1., 0.), (1., 1.), (0., 1.))
# Each list travels around the patch perimeter in positive contour order.
BOUNDARIES = ((0, 1, 2, 3), (3, 7, 11, 15), (15, 14, 13, 12), (12, 8, 4, 0))
EDGE_UV = (((0., 0.), (1., 0.)), ((1., 0.), (1., 1.)),
           ((1., 1.), (0., 1.)), ((0., 1.), (0., 0.)))
ORIGINAL_STL_EDGES = 438
ORIGINAL_STL_FACETS = 292
EXPECTED_PATCHES = 876
EXPECTED_NATIVE_VERTICES = 4380
EXPECTED_STITCHED_VERTICES = 1754
EXPECTED_NATIVE_TRIANGLES = 3504
EXPECTED_SHARED_CURVES = 1752
EXPECTED_SHARP30 = 205
MAX_NATIVE_CORNER_EVAL_ABS = 1e-11
MAX_NATIVE_SEAM_EVAL_ABS = 1e-11


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def edge_key(a, b):
    return tuple(sorted((tuple(a), tuple(b))))


def source_tag(triangle, sector, uv, triangle_id, patch_id):
    """Identify one node by an original topological entity, never XYZ alone."""
    a, b, c = triangle
    v = (a, b, c)
    base = v[sector]
    succeeding = v[(sector + 1) % 3]
    previous = v[(sector + 2) % 3]
    center = tuple((x + y + z) / 3 for x, y, z in zip(a, b, c))
    if uv == (0., 0.):
        return ('vertex', base), base
    if uv == (1., 0.):
        return ('edge', edge_key(base, succeeding)), tuple(
            (x + y) / 2 for x, y in zip(base, succeeding))
    if uv == (1., 1.):
        return ('centroid', triangle_id), center
    if uv == (0., 1.):
        return ('edge', edge_key(base, previous)), tuple(
            (x + y) / 2 for x, y in zip(base, previous))
    if uv == (.5, .5):
        # The center of each bilinear patch remains interior and independent.
        return ('patch_interior', patch_id), None
    raise ValueError('Unsupported native UV for the pinned F27 initial TRI topology')


class DisjointSets:
    def __init__(self, count):
        self.parent = list(range(count))
        self.rank = [0] * count
        self.merges = 0

    def find(self, i):
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1
        self.merges += 1


def identify_patch_nodes(patch, source_triangle, obj_slice, patch_id):
    """Map every original native node to exact UV, original topology and OBJ index."""
    require(type(patch) is dict and patch['index'] == patch_id and
            len(patch['nodes']) == 5 and len(patch['faces']) == 4 and
            len(patch['curves']) == 4 and len(patch['control_points']) == 16,
            'Missing or ambiguous source patch coverage')
    node = {}
    for offset, entry in enumerate(patch['nodes']):
        require(len(entry) == 4 and type(entry[0]) is int and
                entry[0] > 0 and entry[0] not in node,
                'Invalid or duplicate original node identity')
        xyz = tuple(entry[1:4])
        require(all(type(x) in (int, float) and math.isfinite(x) for x in xyz),
                'Non-finite native node')
        require(tuple(float(format(x, '.6g')) for x in xyz) == obj_slice[offset],
                'OBJ coordinate differs from native full-precision node')
        node[entry[0]] = {'xyz': xyz, 'index': 5 * patch_id + offset}
    uv_by_node = {}
    seen_face_nodes = set()
    for face in patch['faces']:
        require(len(face) == 4 and len({row[0] for row in face[1:]}) == 3,
                'Malformed native triangular face')
        for row in face[1:]:
            require(len(row) == 6 and row[0] in node,
                    'Unexpected native face node reference')
            ident, uv, xyz = row[0], tuple(row[1:3]), tuple(row[3:6])
            require(xyz == node[ident]['xyz'], 'Full-precision face/node disagreement')
            require(uv in UVS and (ident not in uv_by_node or uv_by_node[ident] == uv),
                    'Inconsistent or unsupported native UV mapping')
            uv_by_node[ident] = uv
            seen_face_nodes.add(ident)
    require(seen_face_nodes == set(node) and set(uv_by_node.values()) == set(UVS),
            'Incomplete or duplicated native UV control coverage')
    by_uv = {}
    tri_i = patch_id // 3
    sec = patch_id % 3
    for ident, item in node.items():
        uv = uv_by_node[ident]
        tag, expected = source_tag(source_triangle, sec, uv, tri_i, patch_id)
        if expected is not None:
            item['source_corner_error'] = max(abs(x-y) for x, y in zip(item['xyz'], expected))
            require(item['source_corner_error'] <= MAX_NATIVE_CORNER_EVAL_ABS,
                    'Native corner does not coincide with original STL entity')
        else:
            item['source_corner_error'] = 0.0
            require(item['xyz'] not in {source_tag(source_triangle, sec, c, tri_i, patch_id)[1]
                                        for c in CORNERS},
                    'Patch interior center degenerates into a source corner')
        item['tag'] = tag
        by_uv[uv] = item
    control = patch['control_points']
    for uv, idx in (((0., 0.), 0), ((1., 0.), 3),
                    ((1., 1.), 15), ((0., 1.), 12)):
        require(all(abs(x-y) <= MAX_NATIVE_CORNER_EVAL_ABS
                    for x, y in zip(control[idx], by_uv[uv]['xyz'])),
                'Original native corner and Bezier control disagree')
    return by_uv


def reconcile_curves(vertices, faces, patches, source_triangles):
    """Derive a vertex remap ONLY from confirmed source curve incidences."""
    require(len(patches) == 3 * len(source_triangles) and
            len(vertices) == 5 * len(patches) and
            len(faces) == 4 * len(patches),
            'Unexpected original source-to-native TRI coverage')
    by_curve = defaultdict(list)
    max_source_corner_error = 0.0
    max_fullprecision_seam_endpoint_disagreement = 0.0
    max_c0_control_disagreement = 0.0
    tags = [None] * len(vertices)
    native_full_xyz = [None] * len(vertices)
    source_patch_of_face = []
    for pi, patch in enumerate(patches):
        map_uv = identify_patch_nodes(patch, source_triangles[pi//3],
                                      vertices[5*pi:5*pi+5], pi)
        for uv, item in map_uv.items():
            tags[item['index']] = item['tag']
            native_full_xyz[item['index']] = item['xyz']
            max_source_corner_error = max(max_source_corner_error, item['source_corner_error'])
        # Native exporter emits the original snapshot's four faces in patch order.
        local_ids = {entry[0]: 5*pi+i for i, entry in enumerate(patch['nodes'])}
        require([tuple(local_ids[row[0]] for row in face[1:])
                 for face in patch['faces']] == faces[4*pi:4*pi+4],
                'Original OBJ faces disagree with native incidence snapshot')
        source_patch_of_face.extend([pi//3] * 4)
        for side, cid in enumerate(patch['curves']):
            require(type(cid) is int and cid >= 0, 'Invalid native curve identity')
            endpoints = tuple(map_uv[uv] for uv in EDGE_UV[side])
            boundary_controls = tuple(tuple(patch['control_points'][j]) for j in BOUNDARIES[side])
            by_curve[cid].append((pi, side, endpoints, boundary_controls))
    require(all(tag is not None for tag in tags), 'Missing native source labels')
    dsu = DisjointSets(len(vertices))
    orientations = Counter()
    for cid, incidences in by_curve.items():
        require(len(incidences) == 2 and incidences[0][0] != incidences[1][0],
                'Open or nonmanifold original Bezier curve incidence')
        (_, _, ends1, cps1), (_, _, ends2, cps2) = incidences
        # A closed oriented contour must traverse the shared curve oppositely.
        control_difference = max(abs(x-y)
                                 for left, right in zip(cps1, cps2[::-1])
                                 for x, y in zip(left, right))
        max_c0_control_disagreement = max(max_c0_control_disagreement, control_difference)
        require(control_difference <= MAX_NATIVE_SEAM_EVAL_ABS,
                'Native shared curve is not opposite oriented C0')
        orientations['opposite'] += 1
        for member in ends1:
            matches = [other for other in ends2
                       if other['tag'] == member['tag'] and
                       all(abs(x-y) <= MAX_NATIVE_SEAM_EVAL_ABS
                           for x, y in zip(other['xyz'], member['xyz']))]
            require(len(matches) == 1, 'Ambiguous/mismatched original seam endpoint')
            other = matches[0]
            require(member['tag'] == other['tag'],
                    'Identical XYZ but DIFFERENT source entity: prohibited false seam weld')
            endpoint_difference = max(abs(x-y) for x, y in zip(other['xyz'], member['xyz']))
            max_fullprecision_seam_endpoint_disagreement = max(
                max_fullprecision_seam_endpoint_disagreement, endpoint_difference)
            require(vertices[member['index']] == vertices[other['index']],
                    'Native seam differs at exported coordinate precision')
            dsu.union(member['index'], other['index'])
    rep_to_indices = defaultdict(list)
    for i in range(len(vertices)):
        rep_to_indices[dsu.find(i)].append(i)
    for members in rep_to_indices.values():
        require(len({tags[i] for i in members}) == 1 and
                len({vertices[i] for i in members}) == 1 and
                all(all(abs(x-y) <= MAX_NATIVE_SEAM_EVAL_ABS
                        for x,y in zip(native_full_xyz[members[0]], native_full_xyz[i]))
                    for i in members),
                'Unauthorized transitive merge changed source topology or XYZ')
    by_tag = defaultdict(set)
    by_full_xyz = defaultdict(set)
    by_exported_xyz = defaultdict(set)
    for members in rep_to_indices.values():
        r = dsu.find(members[0])
        by_tag[tags[members[0]]].add(r)
        by_full_xyz[native_full_xyz[members[0]]].add(r)
        by_exported_xyz[vertices[members[0]]].add(r)
    require(all(len(components) == 1 for components in by_tag.values()),
            'Shared topological source vertex was not connected via native curves')
    require(all(len(components) == 1 for components in by_full_xyz.values()),
            'Different source entities share identical full-precision XYZ')
    require(all(len(components) == 1 for components in by_exported_xyz.values()),
            'Rounded OBJ XYZ would collide across UNCONNECTED source entities')
    label_to_new = {}
    new_vertices = []
    original_to_new = []
    new_tags = []
    new_full_xyz = []
    representatives = []
    for i in range(len(vertices)):
        r = dsu.find(i)
        if r not in label_to_new:
            label_to_new[r] = len(new_vertices)
            new_vertices.append(vertices[i])
            new_tags.append(tags[i])
            new_full_xyz.append(native_full_xyz[i])
            representatives.append(i)
        original_to_new.append(label_to_new[r])
    stitched_faces = [tuple(original_to_new[v] for v in f) for f in faces]
    require(all(len(set(f)) == 3 for f in stitched_faces),
            'Source-aware stitching collapsed a native triangle')
    return {'vertices': new_vertices, 'faces': stitched_faces,
            'original_to_new': original_to_new, 'representatives': representatives,
            'tags': new_tags, 'full_xyz': new_full_xyz,
            'native_face_source_triangles': source_patch_of_face,
            'curve_count': len(by_curve), 'merges': dsu.merges,
            'unique_source_entities': len(by_tag),
            'coord_only_false_alias_groups': sum(len(v) > 1 for v in by_exported_xyz.values()),
            'native_boundary_orientations': dict(orientations),
            'max_source_corner_deviation': max_source_corner_error,
            'max_native_seam_endpoint_disagreement': max_fullprecision_seam_endpoint_disagreement,
            'max_native_shared_control_disagreement': max_c0_control_disagreement}


def validate_original_feature_edges(source_triangles, result, snapshot):
    """Assert all original STL creases survive, as two oppositely shared segments."""
    original_edge_faces = defaultdict(list)
    source_normals = []
    for ti, tri in enumerate(source_triangles):
        a, b, c = tri
        n = f27.cross(f27.vec(b, a), f27.vec(c, a))
        m = math.sqrt(f27.dot(n, n))
        require(m > 0, 'Degenerate original facet')
        source_normals.append(tuple(x/m for x in n))
        for i in range(3):
            original_edge_faces[edge_key(tri[i], tri[(i+1)%3])].append(ti)
    require(len(original_edge_faces) == ORIGINAL_STL_EDGES and
            all(len(v) == 2 for v in original_edge_faces.values()),
            'Unanticipated input STL edge incidence')
    tag_to_index = dict((key, i) for i, key in enumerate(result['tags']))
    require(len(tag_to_index) == len(result['tags']), 'Distinct source tags were collapsed')
    faces = result['faces']
    incident = defaultdict(list)
    for fi, face in enumerate(faces):
        for i in range(3):
            incident[tuple(sorted((face[i], face[(i+1)%3])))].append(fi)
    # Full precision snapshot face normals are compared to their original source facets.
    native_normals = []
    for patch in snapshot['patches']:
        for face in patch['faces']:
            p = [tuple(row[3:6]) for row in face[1:]]
            n = f27.cross(f27.vec(p[1], p[0]), f27.vec(p[2], p[0]))
            m = math.sqrt(f27.dot(n, n))
            require(m > 0, 'Degenerate full-precision native triangle')
            native_normals.append(tuple(x/m for x in n))
    require(len(native_normals) == len(faces), 'Missing original native normal coverage')
    sharp_count = 0
    max_normal_angular_residual = 0.0
    max_dihedral_residual = 0.0
    for edge, parents in original_edge_faces.items():
        unit1, unit2 = (source_normals[i] for i in parents)
        original_angle = math.degrees(math.acos(max(-1.0, min(1.0, f27.dot(unit1, unit2)))))
        if original_angle >= 30.0:
            sharp_count += 1
        v1, v2 = (tag_to_index[('vertex', p)] for p in edge)
        midpoint = tag_to_index[('edge', edge)]
        for a, b in ((v1, midpoint), (midpoint, v2)):
            native_faces = incident.get(tuple(sorted((a, b))), [])
            require(len(native_faces) == 2 and
                    {result['native_face_source_triangles'][idx] for idx in native_faces} == set(parents),
                    'Original STL crease segment is missing, overshared, or crosses a wrong facet')
            observed_normals = [native_normals[fi] for fi in native_faces]
            for fi, n in zip(native_faces, observed_normals):
                expected = source_normals[result['native_face_source_triangles'][fi]]
                cos = max(-1., min(1., f27.dot(n, expected)))
                normal_angle = math.degrees(math.acos(cos))
                max_normal_angular_residual = max(max_normal_angular_residual, normal_angle)
            pair_cos = max(-1., min(1., f27.dot(observed_normals[0], observed_normals[1])))
            actual_angle = math.degrees(math.acos(pair_cos))
            max_dihedral_residual = max(max_dihedral_residual, abs(actual_angle - original_angle))
    require(sharp_count == EXPECTED_SHARP30 and
            max_normal_angular_residual <= 1e-4 and max_dihedral_residual <= 1e-4,
            'Original STL sharp features have not survived without normal smoothing')
    return {'original_stl_edges': len(original_edge_faces),
            'original_crease_edge_segments_confirmed': 2*len(original_edge_faces),
            'source_dihedral_at_least_30_deg': sharp_count,
            'derived_crease_segments_at_least_30_deg': 2*sharp_count,
            'max_normal_direction_residual_deg': max_normal_angular_residual,
            'max_source_to_derived_dihedral_residual_deg': max_dihedral_residual,
            'source_crease_endpoints_changed': 0,
            'smoothing_applied': False}


def derived_obj_bytes(original: Path, result: dict) -> bytes:
    """Preserve every original textual coordinate and face order; remap ONLY indices."""
    lines = original.read_text(encoding='utf-8').splitlines()
    originals = [s for s in lines if s.startswith('v ')]
    require(len(originals) == len(result['original_to_new']),
            'Derived writer cannot reconcile original OBJ vertex coverage')
    header = ['# Experimental topology-aware stitched OBJ; NOT original APMesh output',
              '# Source original OBJ SHA256 ' + f27.sha256(original),
              '# Vertex identity: original STL entity and native shared curve incidence',
              '# Coordinates and TRI faces unchanged; remap only vertex indices']
    exported = [originals[i] for i in result['representatives']]
    faces = ['f ' + ' '.join(str(v + 1) for v in face) for face in result['faces']]
    return ('\n'.join(header + exported + faces) + '\n').encode('utf-8')


def evaluate_run(zip_path: Path, bp: Path, run: Path):
    # Re-apply all independent F27 STL, native output, quality and process gates.
    f27.verify_native_process_record(run, bp)
    prior = f27.inspect(zip_path, bp, run)
    source = f27.parse_source(zip_path)
    vertices, faces = f27.parse_obj(run / 'bunny_passo_0_malha_0.obj')
    snapshot = json.loads((run / 'bunny_passo_0_incidences.json').read_text(),
                          object_pairs_hook=f27.unique_object,
                          parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
    result = reconcile_curves(vertices, faces, snapshot['patches'], source)
    raw = f27.topology(len(vertices), faces)
    repaired = f27.topology(len(result['vertices']), result['faces'])
    require(raw == prior['native_obj_indexed_topology'],
            'Original indexed topology changed unexpectedly')
    require(len(result['vertices']) == EXPECTED_STITCHED_VERTICES and
            result['curve_count'] == EXPECTED_SHARED_CURVES and
            result['merges'] == 2626 and len(result['faces']) == EXPECTED_NATIVE_TRIANGLES,
            'Original-model topological stitch census differs from F27')
    require((repaired['vertices'], repaired['edges'], repaired['faces'],
             repaired['components'], repaired['euler'], repaired['boundary_edges'],
             repaired['winding_conflicts'], repaired['nonmanifold_vertex_links'],
             repaired['high_incidence_edges']) ==
            (1754, 5256, 3504, 1, 2, 0, 0, 0, 0),
            'Source-aware derived OBJ is not a connected orientable closed sphere')
    diagnostic, dupes = f27.welded_by_exact_exported_xyz(vertices, faces)
    require(diagnostic == repaired and dupes == result['merges'],
            'Coordinate-only diagnostic disagrees with strictly source-topology stitching')
    original_quality = [f27.triangle_quality(tuple(vertices[i] for i in f)) for f in faces]
    derived_quality = [f27.triangle_quality(tuple(result['vertices'][i] for i in f))
                       for f in result['faces']]
    require(original_quality == derived_quality and len(original_quality) == 3504,
            'Topology remap changed any physical TRI shape/quality')
    features = validate_original_feature_edges(source, result, snapshot)
    exported = derived_obj_bytes(run/'bunny_passo_0_malha_0.obj', result)
    return prior, result, raw, repaired, features, exported


def run_private(zip_path: Path, bp: Path, first: Path, second: Path,
                output_dir: Path, public_receipt: Path) -> dict:
    require(first.resolve() != second.resolve() and first.is_dir() and second.is_dir(),
            'Independent original native runs are required')
    require(not output_dir.exists() and not public_receipt.exists(),
            'No overwrite of private derivative or public receipt')
    # Compute both full validations before publishing a new derivative anywhere.
    a = evaluate_run(zip_path, bp, first)
    b = evaluate_run(zip_path, bp, second)
    require(f27.compare_runs(a[0], b[0])['four_scientific_artifact_hashes_byte_identical'],
            'Original native source evidence did not repeat byte-identically')
    require(a[-1] == b[-1], 'New derived OBJ is not byte-identical across repeats')
    (prior, result, raw, sewn, features, obj) = a
    native_obj = first/'bunny_passo_0_malha_0.obj'
    report = {
        'schema': 'apmesh-s40-f28-source-topology-stitch-v1',
        'status': 'DERIVED_TOPOLOGY_STITCH_VALIDATED_NOT_ORIGINAL_NATIVE_EXPORT',
        'source_original_stl_sha256': f27.STL_SHA256,
        'private_input_bp_sha256': f27.BP_SHA256,
        'original_native_cli_sha256': f27.NATIVE_CLI_SHA256,
        'original_native_obj_sha256': f27.sha256(native_obj),
        'private_derived_obj_sha256': hashlib.sha256(obj).hexdigest(),
        'private_derived_obj_bytes': len(obj),
        'original_native_obj_indexed': raw,
        'source_incidence_derived_obj_indexed': sewn,
        'source_curve_incidence_count': result['curve_count'],
        'authorized_native_vertex_id_merges': result['merges'],
        'source_topology_entity_count': result['unique_source_entities'],
        'false_alias_groups_at_exported_obj_precision': result['coord_only_false_alias_groups'],
        'source_feature_preservation': features,
        'native_triangle_quality': prior['quality'],
        'full_precision_source_control_numerical_bounds': {
            'max_corner_source_deviation': result['max_source_corner_deviation'],
            'max_shared_native_endpoint_disagreement': result['max_native_seam_endpoint_disagreement'],
            'max_opposite_shared_bezier_control_disagreement': result['max_native_shared_control_disagreement'],
            'validation_componentwise_tolerance': MAX_NATIVE_SEAM_EVAL_ABS},
        'derived_triangle_quality': prior['quality'],
        'every_exported_face_and_vertex_position_preserved': True,
        'native_accepted_tri_execution_reproducible': True,
        'private_derived_obj_reproducible': True,
        'no_automatic_coordinate_welding': True,
        'no_smoothing_or_new_vertex_positions': True,
        'native_cli_source_modified': False,
        'published_third_party_geometry': False,
        'scientific_benchmark_admitted': False,
        'license_cleared': False,
        'quad_mesh_generated': False,
    }
    # Restrict all geometry and transformation mapping to a private local folder.
    output_dir.mkdir(mode=0o700, parents=True)
    with (output_dir/'293137_derived_source_seam_stitched.obj').open('xb') as fd:
        fd.write(obj)
    with (output_dir/'original_to_derived_private_mapping.json').open('x') as fd:
        json.dump({'original_native_obj_sha256': report['original_native_obj_sha256'],
                   'private_derived_obj_sha256': report['private_derived_obj_sha256'],
                   'native_index_zero_based_to_derived_index_zero_based': result['original_to_new']},
                  fd, separators=(',', ':'))
        fd.write('\n')
    with public_receipt.open('x', encoding='utf-8') as fd:
        json.dump(report, fd, indent=2, sort_keys=True, allow_nan=False)
        fd.write('\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-zip', type=Path, required=True)
    parser.add_argument('--private-bp', type=Path, required=True)
    parser.add_argument('--first-native-run', type=Path, required=True)
    parser.add_argument('--second-native-run', type=Path, required=True)
    parser.add_argument('--private-derived-output', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    r = run_private(args.source_zip, args.private_bp, args.first_native_run,
                    args.second_native_run, args.private_derived_output, args.receipt)
    print(json.dumps({'status': r['status'],
                      'original_components': r['original_native_obj_indexed']['components'],
                      'derived_components': r['source_incidence_derived_obj_indexed']['components'],
                      'source_sharp_edges': r['source_feature_preservation']['source_dihedral_at_least_30_deg'],
                      'private_derived_obj_sha256': r['private_derived_obj_sha256']}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, IndexError, TypeError, OSError) as e:
        raise SystemExit(f'F28 source-seam gate refused: {e}') from e
