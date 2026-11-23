#!/usr/bin/env python3
"""Audit the real original APMesh TRI stage independently, keeping model data private.

The source STL, derived BP, generated OBJ, and full-precision incidence snapshot
must stay outside a public Git repository. This module emits numerical receipts.
A native accepted stage is not a scientific benchmark admission.
"""
from __future__ import annotations

import argparse
import os
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import resource
import struct
import subprocess
import time
import zipfile

ZIP_GIT_BLOB = '359c26b16664e9ba8d2415ca065a85bd27504d5f'
STL_SHA256 = '4a222346223cf2c207c34d7a3d4e8ea297b004ff862b06b6e4c7c2eeac9f761a'
BP_SHA256 = '6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0'
NATIVE_CLI_SHA256 = '9ee068d7c0809476d37b77fb8d8bef4cbede21db5efe68ed2a3b13343b5b401f'
F27_BUILD_COMMIT = '56d793bfe611b7352d9cd4f8dc6f5e025f5b84b0'
MODEL_ID = 293137
OUTPUTS = ('bunny_passo_0_malha_0.obj', 'bunny_passo_0_incidences.json',
           'bunny_passo_0_acceptance_accepted.log', 'bunny_n.process__metrics_rank_-1.csv')
NATIVE_PROFILE = (
    ('BUILD_DIR', 'build'), ('NUM_PROCESSES', '1'), ('NUM_THREADS', '1'),
    ('WRITE_MODE', 'h'), ('USE_TEMPLATE', 'y'),
    ('ADAPTIVE_MODE', 'research_debug'), ('ADAPTIVE_INTENSITY', '0.02'),
    ('ADAPTIVE_QUALITY_PRIORITY', '0.95'), ('ADAPTIVE_MAX_STEPS', '2'),
    ('ADAPTIVE_TARGET_GROWTH', '1.05'), ('CURVE_POINT_MIN', '3'),
    ('CURVE_POINT_MAX', '16'), ('PATCH_QUADTREE_DEPTH_STEP1', '2'),
    ('PATCH_QUADTREE_DEPTH_STEPN', '2'), ('AFT_LOCAL_POSTPROCESS_PASSES', '0'),
    ('ENABLE_HYBRID_RECONSTRUCTION', '0'), ('EPSYLON', '0.0000001'),
    ('TOL_LOCAL', '0.0000001'),
)


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode('ascii') + data).hexdigest()


def parse_source(source_zip: Path) -> list[tuple[tuple[float, float, float], ...]]:
    require(source_zip.is_file() and source_zip.stat().st_size == 7073,
            'Missing/resized original mirror ZIP')
    require(git_blob(source_zip.read_bytes()) == ZIP_GIT_BLOB,
            'Original archive Git blob identity differs')
    with zipfile.ZipFile(source_zip) as archive:
        require(archive.namelist() == ['293137.stl'], 'Unrecognized ZIP contents')
        info = archive.getinfo('293137.stl')
        require(info.file_size == 14684 and info.compress_type == zipfile.ZIP_DEFLATED,
                'Wrong STL member layout')
        binary = archive.read('293137.stl')
    require(hashlib.sha256(binary).hexdigest() == STL_SHA256,
            'Original STL SHA-256 differs from F16/F22')
    require(struct.unpack_from('<I', binary, 80)[0] == 292, 'Source triangle count changed')
    triangles = []
    for face_index in range(292):
        raw = struct.unpack_from('<9f', binary, 84 + face_index * 50 + 12)
        tri = tuple(tuple(float(v) for v in raw[j:j + 3]) for j in (0, 3, 6))
        require(all(math.isfinite(v) for p in tri for v in p), 'Nonfinite source triangle')
        triangles.append(tri)
    return triangles


def parse_bp(bp: Path) -> None:
    require(bp.is_file() and bp.stat().st_size == 538482 and sha256(bp) == BP_SHA256,
            'Original-model BP digest/size mismatch')
    controls = patches = 0
    for line in bp.read_text(encoding='utf-8').splitlines():
        if line.startswith('v '):
            controls += 1
        elif line.startswith('p '):
            patches += 1
        else:
            raise ValueError('Unexpected original-model BP record')
    require((controls, patches) == (7886, 876), 'Original-model BP count mismatch')


def vec(a, b):
    return tuple(x - y for x, y in zip(a, b))


def dot(a, b):
    return math.fsum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def area(a, b, c):
    n = cross(vec(b, a), vec(c, a))
    return math.sqrt(dot(n, n)) / 2


def triangle_quality(points):
    edges = sorted((math.dist(points[0], points[1]),
                    math.dist(points[1], points[2]),
                    math.dist(points[2], points[0])), reverse=True)
    scale = edges[0]
    require(scale > 0 and math.isfinite(scale), 'Nonfinite/zero triangle')
    x, y, z = (length / scale for length in edges)
    product = (x + (y + z)) * (z - (x - y)) * (z + (x - y)) * (x + (y - z))
    require(product > 0 and z > 0, 'Degenerate exported triangle')
    return product / ((x + y + z) * x * y * z)


def parse_obj(path: Path):
    require(path.is_file() and 0 < path.stat().st_size <= 10_000_000,
            'Missing/oversized OBJ')
    vertices, faces = [], []
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        columns = line.split()
        if columns[0] == 'v':
            require(len(columns) == 4, 'Malformed OBJ vertex')
            p = tuple(float(v) for v in columns[1:])
            require(all(map(math.isfinite, p)), 'Nonfinite OBJ vertex')
            vertices.append(p)
        elif columns[0] == 'f':
            require(len(columns) == 4 and all(re.fullmatch(r'[1-9][0-9]*', i)
                                                    for i in columns[1:]),
                    'Only unambiguous positive triangular vertex indices are supported')
            f = tuple(int(i) - 1 for i in columns[1:])
            require(len(set(f)) == 3 and all(0 <= i < len(vertices) for i in f),
                    'Invalid or repeated OBJ face index')
            faces.append(f)
        else:
            raise ValueError('Unsupported OBJ record')
    require(vertices and faces, 'Empty OBJ')
    return vertices, faces


def topology(vertex_count: int, faces: list[tuple[int, int, int]]) -> dict:
    require(vertex_count > 0, 'Invalid vertex census')
    pairs = defaultdict(list)
    links = [defaultdict(set) for _ in range(vertex_count)]
    seen_faces = set()
    parent = list(range(vertex_count))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for face in faces:
        require(len(face) == 3 and len(set(face)) == 3 and
                all(type(v) is int and 0 <= v < vertex_count for v in face),
                'Invalid triangle topology')
        signature = tuple(sorted(face))
        require(signature not in seen_faces, 'Duplicate indexed triangle')
        seen_faces.add(signature)
        for j in range(3):
            v = face[j]
            u, w = face[(j + 1) % 3], face[(j + 2) % 3]
            links[v][u].add(w)
            links[v][w].add(u)
        for j in range(3):
            a, b = face[j], face[(j + 1) % 3]
            pairs[(min(a, b), max(a, b))].append((a, b))
            parent[find(a)] = find(b)
    edges = Counter(len(uses) for uses in pairs.values())
    conflicts = sum(1 for uses in pairs.values() if len(uses) == 2 and
                    uses[0] != uses[1][::-1])
    components = len({find(i) for i in range(vertex_count)})
    cycles = paths = bad_links = 0
    for ring in links:
        if not ring:
            bad_links += 1
            continue
        remaining = set(ring)
        pending = [remaining.pop()]
        while pending:
            current = pending.pop()
            for other in ring[current]:
                if other in remaining:
                    remaining.remove(other)
                    pending.append(other)
        degrees = Counter(len(neighbors) for neighbors in ring.values())
        if remaining:
            bad_links += 1
        elif len(degrees) == 1 and degrees.get(2, 0) == len(ring) and len(ring) >= 3:
            cycles += 1
        elif degrees.get(1, 0) == 2 and degrees.get(2, 0) == len(ring) - 2:
            paths += 1
        else:
            bad_links += 1
    return {'vertices': vertex_count, 'edges': len(pairs), 'faces': len(faces),
            'components': components, 'boundary_edges': edges.get(1, 0),
            'manifold_edges': edges.get(2, 0),
            'high_incidence_edges': sum(n for degree, n in edges.items() if degree > 2),
            'winding_conflicts': conflicts,
            'vertex_link_cycles': cycles, 'vertex_link_paths': paths,
            'nonmanifold_vertex_links': bad_links,
            'euler': vertex_count - len(pairs) + len(faces)}


def welded_by_exact_exported_xyz(vertices, faces):
    index, original_to_new = {}, []
    for point in vertices:
        if point not in index:
            index[point] = len(index)
        original_to_new.append(index[point])
    welded_faces = [tuple(original_to_new[v] for v in f) for f in faces]
    welded = topology(len(index), welded_faces)
    return welded, len(vertices) - len(index)


def unique_object(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, 'Duplicate receipt field')
        result[k] = v
    return result


def parse_acceptance(path: Path):
    require(path.is_file() and path.stat().st_size < 15_000, 'Missing acceptance log')
    parsed = {}
    for line in path.read_text().splitlines():
        if '=' not in line:
            continue
        k, v = line.split('=', 1)
        require(k not in parsed, 'Duplicate acceptance field')
        parsed[k] = v
    require(parsed.get('step') == '0' and parsed.get('accepted') == '1' and
            parsed.get('budget_final_status') != 'rejected',
            'APMesh stage 0 is not genuinely accepted')
    return parsed


def parse_metrics(path: Path):
    require(path.is_file() and path.stat().st_size < 50_000, 'Missing metrics CSV')
    with path.open(newline='', encoding='utf-8') as source:
        reader = csv.DictReader(source)
        require(reader.fieldnames and len(set(reader.fieldnames)) == len(reader.fieldnames),
                'Ambiguous metric CSV header')
        rows = list(reader)
    require(len(rows) == 1 and rows[0].get('step') == '0',
            'Unexpected/partial step 0 metrics')
    require(None not in rows[0] and all(v is not None for v in rows[0].values()),
            'Truncated metric row')
    return rows[0]


def snapshot_area_and_correspondence(path: Path, source_triangles, obj_vertices,
                                     obj_faces) -> dict:
    require(path.is_file() and 0 < path.stat().st_size <= 10_000_000,
            'Missing/oversized full-precision native incidence snapshot')
    snapshot = json.loads(path.read_text(encoding='utf-8'),
                          object_pairs_hook=unique_object,
                          parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    require(snapshot.get('schema') == 'apmesh-incidence-v1' and snapshot.get('step') == 0,
            'Unexpected native snapshot schema/stage')
    patches = snapshot.get('patches')
    require(isinstance(patches, list) and len(patches) == 876,
            'Missing original patch coverage in snapshot')
    full_area = original_area = max_relative_face_area_error = 0.0
    max_plane = max_barycentric_violation = 0.0
    flipped = 0
    predicted_obj_vertices, predicted_obj_faces = [], []
    node_map = {}
    for ti, source_tri in enumerate(source_triangles):
        a, b, c = source_tri
        e1, e2 = vec(b, a), vec(c, a)
        normal = cross(e1, e2)
        nn = math.sqrt(dot(normal, normal))
        require(nn > 0, 'Degenerate source STL triangle')
        d11, d12, d22 = dot(e1, e1), dot(e1, e2), dot(e2, e2)
        den = d11 * d22 - d12 * d12
        require(den > 0, 'Invalid source barycentric frame')
        area_i = 0.0
        for pi in range(3 * ti, 3 * ti + 3):
            patch = patches[pi]
            require(patch['index'] == pi and len(patch['nodes']) == 5 and
                    len(patch['faces']) == 4 and len(patch['curves']) == 4 and
                    len(patch['control_points']) == 16,
                    'Incomplete patch snapshot')
            local_nodes = {}
            for node in patch['nodes']:
                require(len(node) == 4 and type(node[0]) is int and node[0] > 0 and
                        node[0] not in node_map, 'Unexpected duplicated node identity')
                pos = tuple(node[1:4])
                require(all(type(x) in (int, float) and math.isfinite(x) for x in pos),
                        'Nonfinite native node')
                local_nodes[node[0]] = pos
                node_map[node[0]] = len(predicted_obj_vertices)
                # The production OBJ writer uses default six significant digits.
                predicted_obj_vertices.append(tuple(float(format(x, '.6g')) for x in pos))
            for native_face in patch['faces']:
                require(len(native_face) == 4, 'Malformed native snapshot face')
                corners = native_face[1:]
                require(all(len(row) == 6 and row[0] in local_nodes for row in corners),
                        'Native face lacks a local node')
                pts = []
                indices = []
                for corner in corners:
                    node_id = corner[0]
                    pos = tuple(corner[3:6])
                    require(pos == local_nodes[node_id], 'Native face disagrees with node XYZ')
                    pts.append(pos)
                    indices.append(node_map[node_id])
                predicted_obj_faces.append(tuple(indices))
                nface = cross(vec(pts[1], pts[0]), vec(pts[2], pts[0]))
                if dot(nface, normal) <= 0:
                    flipped += 1
                area_i += area(*pts)
                for point in pts:
                    d = vec(point, a)
                    max_plane = max(max_plane, abs(dot(d, normal)) / nn)
                    rhs1, rhs2 = dot(d, e1), dot(d, e2)
                    u = (rhs1 * d22 - rhs2 * d12) / den
                    v = (rhs2 * d11 - rhs1 * d12) / den
                    max_barycentric_violation = max(max_barycentric_violation,
                                                    max(0.0, -u, -v, u + v - 1))
        a0 = area(a, b, c)
        original_area += a0
        full_area += area_i
        max_relative_face_area_error = max(max_relative_face_area_error,
                                           abs(area_i - a0) / a0)
    require(predicted_obj_vertices == obj_vertices and
            predicted_obj_faces == obj_faces,
            'Native high-precision snapshot is not exactly the original exported OBJ')
    require(flipped == 0 and max_plane < 1e-9 and
            max_barycentric_violation < 1e-9 and
            max_relative_face_area_error < 1e-9,
            'Native generated physical triangles deviate from source facets')
    return {'original_surface_area': original_area,
            'native_full_precision_surface_area': full_area,
            'absolute_area_difference': abs(full_area - original_area),
            'max_relative_original_facet_area_error': max_relative_face_area_error,
            'max_point_to_source_triangle_plane_distance': max_plane,
            'max_barycentric_outside_source_triangle': max_barycentric_violation,
            'opposite_source_facet_orientation_faces': flipped,
            'all_native_faces_and_nodes_reconciled_with_exported_obj': True}


def inspect(source_zip: Path, bp: Path, run: Path) -> dict:
    source_triangles = parse_source(source_zip)
    parse_bp(bp)
    require(run.is_dir(), 'Missing private native execution folder')
    all_files = sorted(p for p in run.iterdir() if p.is_file())
    require(0 < len(all_files) <= 30 and all(p.stat().st_size <= 10_000_000
                                             for p in all_files),
            'Excessive/missing native output files')
    objpath, snapshotpath, acceptedpath, metricpath = (run / p for p in OUTPUTS)
    obj_vertices, obj_faces = parse_obj(objpath)
    require(len(obj_vertices) == 4380 and len(obj_faces) == 3504,
            'Unexpected model native OBJ vertex/face counts')
    raw = topology(len(obj_vertices), obj_faces)
    welded, duplicates = welded_by_exact_exported_xyz(obj_vertices, obj_faces)
    require(raw == {'vertices': 4380, 'edges': 7008, 'faces': 3504,
                    'components': 876, 'boundary_edges': 3504, 'manifold_edges': 3504,
                    'high_incidence_edges': 0, 'winding_conflicts': 0,
                    'vertex_link_cycles': 876, 'vertex_link_paths': 3504,
                    'nonmanifold_vertex_links': 0, 'euler': 876},
            'Raw OBJ index-level topology disagrees with observed native output')
    require(welded == {'vertices': 1754, 'edges': 5256, 'faces': 3504,
                       'components': 1, 'boundary_edges': 0, 'manifold_edges': 5256,
                       'high_incidence_edges': 0, 'winding_conflicts': 0,
                       'vertex_link_cycles': 1754, 'vertex_link_paths': 0,
                       'nonmanifold_vertex_links': 0, 'euler': 2}
            and duplicates == 2626,
            'Coordinate-welded topology disagrees with the original genus-zero graph')
    accepted, metrics = parse_acceptance(acceptedpath), parse_metrics(metricpath)
    require(int(metrics['nodes']) == len(obj_vertices) and
            int(metrics['elements']) == len(obj_faces) and
            int(metrics['unique_edges']) == raw['edges'] and
            int(metrics['boundary_edges']) == raw['boundary_edges'] and
            int(metrics['nonmanifold_edges']) == 0,
            'APMesh metrics are inconsistent with independent raw OBJ graph')
    quality = [triangle_quality(tuple(obj_vertices[i] for i in f)) for f in obj_faces]
    qmin, qmean = min(quality), math.fsum(quality) / len(quality)
    poor_percent = 100 * sum(x < .30 for x in quality) / len(quality)
    require(abs(qmin - float(metrics['quality_min'])) < 2e-4 and
            abs(qmean - float(metrics['quality_mean'])) < 2e-4 and
            abs(poor_percent - float(metrics['poor_ratio_lt_0_30'])) < .002 and
            abs(qmin - float(accepted['quality_min_3d'])) < 2e-4 and
            abs(qmean - float(accepted['quality_mean_3d'])) < 2e-4,
            'Published quality fields disagree with independent OBJ geometry')
    source_match = snapshot_area_and_correspondence(snapshotpath, source_triangles,
                                                     obj_vertices, obj_faces)
    require(float(metrics['error']) == 0.0, 'Observed initial stage was not flat-curvature zero')
    source_quality = [triangle_quality(tri) for tri in source_triangles]
    return {'schema': 'apmesh-s40-f27-original-tri-stage0-audit-v1',
            'status': 'NATIVE_TRI_STAGE0_ACCEPTED_INDEXED_TOPOLOGY_NOT_GLOBALLY_STITCHED',
            'source_model_id': MODEL_ID, 'original_stl_sha256': STL_SHA256,
            'original_bp_sha256': BP_SHA256,
            'original_source_commit_native_cli': F27_BUILD_COMMIT,
            'original_native_cli_sha256': NATIVE_CLI_SHA256,
            'accepted_stages': [0], 'rejected_stages': [],
            'source_facets': len(source_triangles), 'native_triangles': len(obj_faces),
            'original_stl_tri_quality': {'min': min(source_quality),
                'mean': math.fsum(source_quality) / len(source_quality),
                'below_0_30_count': sum(x < .3 for x in source_quality),
                'below_0_30_percent': 100 * sum(x < .3 for x in source_quality) / len(source_quality)},
            'native_obj_indexed_topology': raw,
            'exact_xyz_welded_topology_diagnostic_not_native_output': welded,
            'duplicate_index_vertices_with_exact_same_exported_xyz': duplicates,
            'quality': {'2r_over_R_min_obj': qmin, '2r_over_R_mean_obj': qmean,
                        'below_0_30_count': sum(x < .30 for x in quality),
                        'below_0_30_percent': poor_percent},
            'geometry': source_match,
            'artifact_sha256': {name: sha256(run / name) for name in OUTPUTS},
            'native_stage0_accepted_by_engine': True,
            'native_global_stitching_verified': False,
            'scientific_benchmark_admitted': False,
            'asset_license_independently_cleared': False}


def compare_runs(a: dict, b: dict) -> dict:
    require(a['status'] == b['status'], 'Native attempts disagree in status')
    require(a['artifact_sha256'] == b['artifact_sha256'],
            'Native accepted stage 0 is not byte-for-byte repeatable')
    for key in ('native_obj_indexed_topology',
                'exact_xyz_welded_topology_diagnostic_not_native_output',
                'quality', 'geometry', 'original_stl_tri_quality'):
        require(a[key] == b[key], f'Native repeats disagree in {key}')
    return {'native_repetitions': 2, 'same_binary_and_input': True,
            'four_scientific_artifact_hashes_byte_identical': True,
            'admitted_as_original_native_execution': True,
            'admitted_as_fair_scientific_benchmark': False}




def input_config(bp: Path, workdir: Path) -> str:
    """Lock every runtime setting; only the isolated input/output paths may vary."""
    require(bp.is_absolute() and workdir.is_absolute(),
            'Private input and output roots must be absolute')
    lines = [('INPUT_MODEL', str(bp)), ('OUTPUT_PREFIX', str(workdir / 'bunny'))]
    lines.extend(NATIVE_PROFILE)
    return ''.join(f'{key}={value}\n' for key, value in lines)


def verify_native_process_record(run: Path, bp: Path) -> dict:
    """Require an actual zero-exit native process, not just plausible output files."""
    config = run / 'case.conf'
    receipt = run / 'process.json'
    require(config.is_file() and receipt.is_file(), 'Missing original CLI process/config evidence')
    require(config.read_text(encoding='utf-8') == input_config(bp, run),
            'Original CLI configuration differs from the frozen F27 profile')
    r = json.loads(receipt.read_text(encoding='utf-8'),
                   object_pairs_hook=unique_object)
    require(type(r) is dict and r.get('native_exit_code') == 0 and
            r.get('status') == 'completed' and r.get('binary_sha256') == NATIVE_CLI_SHA256 and
            r.get('bp_sha256') == BP_SHA256 and
            r.get('config_sha256') == sha256(config) and
            r.get('stdout_sha256') == sha256(run/'stdout.log') and
            r.get('stderr_sha256') == sha256(run/'stderr.log'),
            'Native process provenance or successful exit is not established')
    require(type(r.get('wall_seconds')) in (float, int) and
            math.isfinite(r['wall_seconds']) and r['wall_seconds'] > 0,
            'Native process execution time is absent/nonfinite')
    return r


def constrain_native_child() -> None:
    """Bound a serial scientific executable in an isolated POSIX child."""
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 ** 3, 2 * 1024 ** 3))
    resource.setrlimit(resource.RLIMIT_CPU, (180, 180))
    resource.setrlimit(resource.RLIMIT_FSIZE, (64 * 1024 ** 2, 64 * 1024 ** 2))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def run_original_cli(binary: Path, bp: Path, workdir: Path) -> dict:
    require(os.name == 'posix', 'Original static Linux executable requires POSIX')
    require(binary.is_file() and sha256(binary) == NATIVE_CLI_SHA256,
            'Native original C++ executable identity is not established')
    parse_bp(bp)
    require(not workdir.exists(), 'Refusing to overwrite an existing private execution')
    workdir.mkdir(parents=True, mode=0o700)
    config = workdir / 'case.conf'
    with config.open('x', encoding='utf-8') as stream:
        stream.write(input_config(bp, workdir))
    start = time.monotonic()
    with (workdir/'stdout.log').open('xb') as stdout, (workdir/'stderr.log').open('xb') as stderr:
        try:
            process = subprocess.run([str(binary), '--config', str(config)],
                                     cwd=workdir, stdout=stdout, stderr=stderr,
                                     check=False, timeout=150, preexec_fn=constrain_native_child)
            code = process.returncode
            status = 'completed'
        except subprocess.TimeoutExpired:
            code = None
            status = 'timeout'
    report = {'schema': 'apmesh-s40-f27-private-native-process-v1',
              'status': status, 'native_exit_code': code,
              'binary_sha256': sha256(binary), 'bp_sha256': sha256(bp),
              'config_sha256': sha256(config),
              'stdout_sha256': sha256(workdir/'stdout.log'),
              'stderr_sha256': sha256(workdir/'stderr.log'),
              'wall_seconds': time.monotonic() - start,
              'resource_limits': {'cpu_seconds': 180, 'virtual_memory_gib': 2,
                                  'output_file_cap_mib': 64, 'timeout_seconds': 150}}
    with (workdir/'process.json').open('x', encoding='utf-8') as out:
        json.dump(report, out, indent=2, sort_keys=True)
        out.write('\n')
    require(code == 0 and status == 'completed',
            'Original native mesher did not complete successfully; no scientific admission')
    return report


def main() -> None:
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument('--source-zip', type=Path, required=True)
    arg.add_argument('--bp', type=Path, required=True)
    arg.add_argument('--first', type=Path)
    arg.add_argument('--second', type=Path)
    arg.add_argument('--binary', type=Path)
    arg.add_argument('--replay-root', type=Path)
    arg.add_argument('--receipt', type=Path, required=True)
    args = arg.parse_args()
    require(not args.receipt.exists(), 'Evidence receipt already exists')
    require((args.replay_root is None) == (args.binary is None),
            'Replay must specify both original binary and a private output root')
    if args.replay_root:
        require(args.replay_root.is_absolute() and not args.replay_root.exists(),
                'Replay output root must be a new absolute private path')
        args.replay_root.mkdir(mode=0o700, parents=True)
        args.first = args.replay_root / 'native-attempt-1'
        args.second = args.replay_root / 'native-attempt-2'
        run_original_cli(args.binary.resolve(), args.bp.resolve(), args.first)
        run_original_cli(args.binary.resolve(), args.bp.resolve(), args.second)
    require(args.first is not None and args.second is not None and
            args.first.resolve() != args.second.resolve(),
            'Requires two independent original-native run folders')
    one_process = verify_native_process_record(args.first, args.bp.resolve())
    two_process = verify_native_process_record(args.second, args.bp.resolve())
    first = inspect(args.source_zip, args.bp, args.first)
    second = inspect(args.source_zip, args.bp, args.second)

    result = first.copy()
    result['reproducibility'] = compare_runs(first, second)
    result['bounded_native_processes'] = [
        {'return_code': p['native_exit_code'], 'wall_seconds': p['wall_seconds'],
         'stdout_sha256': p['stdout_sha256'], 'stderr_sha256': p['stderr_sha256']}
        for p in (one_process, two_process)]
    result['frozen_engine_settings'] = dict(NATIVE_PROFILE)
    result['original_native_binary_build_workflow'] = 'https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45164751761'

    with args.receipt.open('x', encoding='utf-8') as out:
        json.dump(result, out, indent=2, sort_keys=True, allow_nan=False)
        out.write('\n')
    print(json.dumps({'status': result['status'], 'native_triangles': result['native_triangles'],
                      'source_facets': result['source_facets'],
                      'indexed_components': result['native_obj_indexed_topology']['components'],
                      'welded_components': result['exact_xyz_welded_topology_diagnostic_not_native_output']['components'],
                      'quality_below_0_30_percent': result['quality']['below_0_30_percent']}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        raise SystemExit(f'F27 scientific evidence gate failed: {exc}') from exc
