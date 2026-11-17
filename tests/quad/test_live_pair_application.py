"""Independently replay live pair decisions against the retained original AFT scaffold."""
import argparse
from collections import Counter
import csv
import json
import math
from pathlib import Path
import subprocess
import uuid

from independent_common_grid import load_physical_obj, common_grid_source_error
from test_controlled_application import require
from test_real_boundary_application import audit
from test_m4_real_model_hybrid import golden


def delta(a, b):
    return tuple(x-y for x, y in zip(a, b))


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def norm(a):
    return math.sqrt(dot(a, a))


def independently_measure(cycle, xyz, uv):
    for i, a in enumerate(cycle):
        b, c = cycle[(i+1) % 4], cycle[(i+3) % 4]
        determinant = ((uv[b][0]-uv[a][0])*(uv[c][1]-uv[a][1]) -
                       (uv[b][1]-uv[a][1])*(uv[c][0]-uv[a][0]))
        if not math.isfinite(determinant) or determinant <= 1e-14:
            return "rejected_uv", None, None
    angles, lengths = [], []
    for i, a in enumerate(cycle):
        x = delta(xyz[cycle[(i+1) % 4]], xyz[a])
        y = delta(xyz[cycle[(i+3) % 4]], xyz[a])
        _, du, dv = golden(*uv[a])
        normal = cross(du, dv)
        nx, ny, nn = norm(x), norm(y), norm(normal)
        if not (nx > 1e-14 and ny > 1e-14 and nn > 1e-12):
            return "rejected_physical", None, None
        scaled = dot(cross(x, y), normal)/(nx*ny*nn)
        if not math.isfinite(scaled) or not (1e-12 < scaled <= 1+1e-12):
            return "rejected_physical", None, None
        angles.append(math.degrees(math.atan2(norm(cross(x, y)), dot(x, y))))
        lengths.append(nx)
    a, b, c, d = (xyz[i] for i in cycle)
    first, second = cross(delta(b, a), delta(c, a)), cross(delta(c, a), delta(d, a))
    denominator = norm(first)*norm(second)
    if denominator <= 1e-14 or not (0 < dot(first, second)/denominator <= 1+1e-12):
        return "rejected_physical", None, None
    score = 1 + max(abs(angle-90) for angle in angles)/90
    return ("eligible" if score <= 1.5 else "rejected_shape"), score, max(lengths)/min(lengths)


def audit_decisions(source, mixed, seed, rows, scope):
    xyz, uv, source_faces = source
    out_xyz, out_uv, output = mixed
    require(xyz == out_xyz and uv == out_uv, "Pairing changed source nodes or UVs")
    require(all(len(face) == 4 for face in source_faces[:seed]) and
            all(len(face) == 3 for face in source_faces[seed:]), "Invalid source scaffold types")
    by_current = {}
    for row in rows:
        require(all(row[key] == scope[key] for key in ('step', 'epoch', 'retry',
                    'domain_generation', 'reference_tri_accepted')), "Foreign live source scope")
        by_current.setdefault(int(row['second_source_face'])-1, []).append(row)
    edges, consumed, selected, statuses = {}, set(), [], Counter()
    for current in range(seed, len(source_faces)):
        triangle, expected = source_faces[current], []
        for side in range(3):
            a, b, opposite = triangle[side], triangle[(side+1) % 3], triangle[(side+2) % 3]
            key = tuple(sorted((a, b)))
            if key not in edges:
                edges[key] = current, a, b, opposite
                continue
            old, old_a, old_b, old_opposite = edges[key]
            require((old_a, old_b) == (b, a), "Scaffold winding differs")
            cycle = [old_a, opposite, old_b, old_opposite]
            start = cycle.index(min(cycle))
            cycle = cycle[start:] + cycle[:start]
            expected.append((old, side, cycle))
        actual = by_current.pop(current, [])
        require(len(actual) == len(expected), "Missing/extra live alternatives")
        eligible = []
        for row, (old, side, cycle) in zip(actual, expected):
            require(int(row['first_source_face'])-1 == old and int(row['front_order']) == side and
                    [int(row[key])-1 for key in ('quad_a', 'quad_b', 'quad_c', 'quad_d')] == cycle,
                    "Live alternative has foreign source/order/cycle")
            classification, score, ratio = independently_measure(cycle, xyz, uv)
            status = row['status']
            statuses[status] += 1
            if old in consumed:
                require(status == 'already_paired', "Previously consumed TRI reused")
            elif classification == 'eligible':
                require(status in ('selected', 'not_selected'), "Valid alternative misclassified")
                require(abs(float(row['S_xyz'])-score) < 1e-13 and
                        abs(float(row['edge_ratio'])-ratio) < 1e-12,
                        "Reported physical rank differs from independent XYZ")
                eligible.append((row, old, side, cycle))
            else:
                require(status == classification, "Rejected alternative misclassified")
                if score is not None:
                    require(abs(float(row['S_xyz'])-score) < 1e-13, "Rejected score forged")
            require(status == 'selected' or int(row['final_face']) == 0,
                    "Unselected alternative claims a final face")
        if eligible:
            winner = min(eligible, key=lambda item: (float(item[0]['S_xyz']),
                         float(item[0]['edge_ratio']), item[2], item[1], item[3]))
            require(sum(item[0]['status'] == 'selected' for item in eligible) == 1 and
                    winner[0]['status'] == 'selected', "Live winner violates ranking")
            row, old, _, cycle = winner
            require(current not in consumed and old not in consumed, "Duplicate pair consumption")
            consumed.update((current, old))
            selected.append(tuple(cycle))
            require(int(row['final_face']) == seed + len(selected), "Wrong paired QUAD provenance")
    require(not by_current, "Trace contains a foreign triangle invocation")
    expected_output = source_faces[:seed] + selected + [source_faces[i] for i in
                      range(seed, len(source_faces)) if i not in consumed]
    require(output == expected_output, "Actual physical faces differ from live selected origins")
    return len(selected), dict(statuses)


def run(exe, directory, name, paired=True, rollback=False):
    root = Path(__file__).resolve().parents[2]
    prefix = directory/name
    config = (root/'configs/quad/curved_patch_live_pairs.conf').read_text()
    config = config.replace('OUTPUT_PREFIX=build/quad_live_pairs', 'OUTPUT_PREFIX='+prefix.as_posix())
    if not paired:
        config = config.replace('curved_bezier_live_pairs_vertex_mean_v1',
                                'curved_bezier_bounded_domain_vertex_mean_v1')
    if rollback:
        config += '\nQUAD_VERIFY_ROLLBACK=1\n'
    conf = prefix.with_suffix('.conf')
    conf.write_text(config)
    process = subprocess.run([str(exe), '--config', str(conf)], cwd=directory,
                             capture_output=True, timeout=180)
    prefix.with_suffix('.stdout').write_bytes(process.stdout)
    prefix.with_suffix('.stderr').write_bytes(process.stderr)
    require(process.returncode == int(rollback), f"Live pair execution failed: {prefix}")
    if rollback:
        require(b'QUAD_REAL_BOUNDARY_ROLLBACK previous_nonempty=1 preserved=1' in process.stdout,
                "Missing nonempty paired-owner rollback")
    archive = Path(str(prefix)+'.steps')
    manifest = list(csv.DictReader((archive/'manifest.csv').open()))
    require([int(row['step']) for row in manifest] == [0, 1, 2, 3], "Missing generation steps")
    accepted = [row for row in manifest if row['reference_tri_accepted'] == '1']
    require(prefix.with_suffix('.obj').read_bytes() ==
            (archive/accepted[-1]['quad_tri_obj']).read_bytes(), "Rejected state published")
    return prefix, archive, manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    directory = args.directory.resolve()/('run-'+uuid.uuid4().hex)
    directory.mkdir(parents=True)
    exe = args.exe.resolve()
    _, old_archive, old_manifest = run(exe, directory, 'unpaired', paired=False)
    _, archive, manifest = run(exe, directory, 'paired')
    _, rollback_archive, rollback_manifest = run(exe, directory, 'rollback', rollback=True)
    require(manifest == rollback_manifest, "Rollback changed paired history")
    events = list(csv.DictReader((archive/'live_pair_candidates.csv').open()))
    stages = list(csv.DictReader((archive/'live_pair_stages.csv').open()))
    require(len(stages) == 4, "Missing live stage accounting")
    report = []
    rejected_controls = 0
    for old, row, stage in zip(old_manifest, manifest, stages):
        require(all(stage[key] == row[key] for key in ('step', 'epoch', 'retry',
                'domain_generation', 'reference_tri_accepted')), "Live stage lineage differs")
        file = row['quad_tri_obj']
        current, original = archive/file, old_archive/old['quad_tri_obj']
        require(current.read_bytes() == (rollback_archive/file).read_bytes(), "Rollback mesh differs")
        if row['step'] == '0':
            require(current.read_bytes() == original.read_bytes(), "Initial source changed")
            continue
        audit(current)
        audit(original)
        scaffold = load_physical_obj(archive/file.replace('_quad_tri.obj', '_aft_source.obj'))
        require(scaffold == load_physical_obj(original), "Original AFT geometry/order changed")
        scoped = [event for event in events if all(event[key] == row[key] for key in
                  ('step', 'epoch', 'retry', 'domain_generation', 'reference_tri_accepted'))]
        origins = [tuple(map(int, line.split()[2:])) for line in current.read_text().splitlines()
                   if line.startswith('# aft_pair_origin ')]
        require(origins == [(int(event['final_face']), int(event['first_source_face']),
                            int(event['second_source_face'])) for event in scoped
                           if event['status'] == 'selected'], "Physical OBJ pair provenance differs")
        selected, statuses = audit_decisions(scaffold, load_physical_obj(current),
                                            int(stage['seed_quads']), scoped, row)
        require(selected == int(stage['selected_pairs']) and
                int(stage['aft_source_triangles']) == 2*selected + int(stage['retained_triangles']),
                "Live pair accounting differs")
        report.append({'step': int(row['step']), 'selected_pairs': selected, 'statuses': statuses,
                       'mixed_nodes': int(row['nodes']), 'quads': int(row['quads']),
                       'triangles': int(row['triangles']),
                       'unpaired_fixed_grid_error': common_grid_source_error(original, grid=24),
                       'paired_fixed_grid_error': common_grid_source_error(current, grid=24)})
        if selected and not rejected_controls:
            for field, value in [('first_source_face', '999999'), ('quad_a', '999999'),
                                 ('S_xyz', '0'), ('final_face', '999999'),
                                 ('domain_generation', '999999'),
                                 ('reference_tri_accepted', '0')]:
                forged = [dict(event) for event in scoped]
                target = next(event for event in forged if event['status'] == 'selected')
                target[field] = value
                try:
                    audit_decisions(scaffold, load_physical_obj(current), int(stage['seed_quads']), forged, row)
                except (AssertionError, IndexError, ValueError):
                    rejected_controls += 1
                else:
                    raise RuntimeError('Forged live decision passed: '+field)
    require(any(row['selected_pairs'] > 0 for row in report) and rejected_controls == 6,
            "No actual selected QUAD or insufficient negative controls")
    summary = {'schema': 'apmesh.quad.live_pair_application.v1', 'steps': report,
               'forged_records_rejected': rejected_controls, 'nonempty_rollback': True,
               'original_aft_scaffold_preserved': True, 'mixed_adaptive_epochs': 0}
    (directory/'report.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
