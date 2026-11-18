"""Replay prospective mixed-front commits independently of the C++ owner."""
import argparse
from collections import Counter
import copy
import csv
import json
import math
from pathlib import Path
import subprocess
import uuid

from independent_common_grid import load_physical_obj
from test_controlled_application import require
from test_real_boundary_application import audit

EPS = 1e-14


def cross(uv, a, b, c):
    x, y, z = (uv[i] for i in (a, b, c))
    return (y[0]-x[0])*(z[1]-x[1])-(y[1]-x[1])*(z[0]-x[0])


def edges(face):
    return list(zip(face, face[1:]+face[:1]))


def inside(uv, tri, p):
    return all(cross(uv, a, b, p) > EPS for a, b in edges(tri))


def crosses(uv, edge, other):
    a, b = edge
    c, d = other
    def opposite(x, y):
        return (x > EPS and y < -EPS) or (y > EPS and x < -EPS)
    return opposite(cross(uv, a, b, c), cross(uv, a, b, d)) and opposite(
        cross(uv, c, d, a), cross(uv, c, d, b))


def valid(uv, front, tri, excluded):
    if len(set(tri)) != 3 or cross(uv, *tri) <= EPS:
        return False
    point = [sum(uv[v][k] for v in tri)/3 for k in range(2)]
    # Independent ray parity for the remaining domain, including interior holes.
    ray = sum((uv[a][1] > point[1]) != (uv[b][1] > point[1]) and
              point[0] < (uv[b][0]-uv[a][0])*(point[1]-uv[a][1]) /
              (uv[b][1]-uv[a][1]) + uv[a][0] for a, b in front)
    if ray % 2 != 1:
        return False
    for p in {v for edge in front for v in edge} - set(tri):
        if inside(uv, tri, p):
            return False
        for a, b in edges(tri):
            if abs(cross(uv, a, b, p)) <= EPS and all(
                    min(uv[a][k], uv[b][k]) <= uv[p][k] <= max(uv[a][k], uv[b][k])
                    for k in range(2)):
                return False
    if any((b, a) in front or any(crosses(uv, (a, b), e) for e in front)
           for a, b in edges(tri)):
        return False
    return not excluded or not (
        any(inside(uv, tri, p) for p in excluded) or
        any(inside(uv, excluded, p) for p in tri) or
        any(crosses(uv, a, b) for a in edges(tri) for b in edges(excluded)))


def best_candidates(uv, front, leaves, base, excluded=None):
    def in_box(v, box):
        return all(box[k] <= uv[v][k] <= box[k+2] for k in range(2))
    cells = {i for i, box in enumerate(leaves) if any(in_box(v, box) for v in base)}
    active = {v for e in front for v in e} - set(base)
    for _ in range(2):
        cells |= {j for j, box in enumerate(leaves) if any(
            all(leaves[i][k] <= box[k+2] and box[k] <= leaves[i][k+2]
                for k in range(2)) for i in cells)}
        candidates = [v for v in active if any(in_box(v, leaves[i]) for i in cells) and
                      valid(uv, front, [*base, v], excluded)]
        if candidates:
            return candidates
    return []


def angle(uv, base, vertex):
    a, b = ([uv[i][k]-uv[vertex][k] for k in range(2)] for i in base)
    return math.atan2(abs(a[0]*b[1]-a[1]*b[0]), sum(x*y for x, y in zip(a, b)))


def shape(uv, quad):
    if any(cross(uv, quad[i], quad[(i+1) % 4], quad[(i-1) % 4]) <= EPS for i in range(4)):
        return None
    # Cosine-law angles independently verify the vector atan2 implementation.
    angles = []
    for i, vertex in enumerate(quad):
        prev, nxt = quad[(i-1) % 4], quad[(i+1) % 4]
        a, b, c = math.dist(uv[vertex], uv[prev]), math.dist(uv[vertex], uv[nxt]), math.dist(uv[prev], uv[nxt])
        angles.append(math.degrees(math.acos(max(-1, min(1, (a*a+b*b-c*c)/(2*a*b))))))
    return 1 + max(abs(a-90) for a in angles)/90


def replay(data, obj, directory=None):
    xyz, uv, output = obj
    require(data['schema'] == 'apmesh.quad.article_front.v1' and
            data['vertices'] == [list(p) for p in uv], 'Foreign article source sites')
    seed = data['seed_faces']
    require(seed and all(len(f) == 4 for f in seed), 'Missing actual template interior')
    used = Counter(e for face in seed for e in edges(face))
    exterior = [(b, a) for (a, b), n in used.items() if used[b, a] == 0]
    all_uses = Counter(e for face in output for e in edges(face))
    outer = [e for e in all_uses if all_uses[e[::-1]] == 0]
    front = Counter(outer + exterior)
    committed = list(seed)
    selected, rejected, competing = 0, 0, 0
    for index, step in enumerate(data['commits']):
        before = list(map(tuple, step['before']))
        require(Counter(before) == front and all(n == 1 for n in front.values()),
                'Missing, duplicate or premature contour update')
        tri = step['best']
        require(tuple(tri[:2]) == before[0], 'Best triangle does not use selected base')
        candidates = best_candidates(uv, before, data['leaves'], tri[:2])
        require(tri[2] in candidates and angle(uv, tri[:2], tri[2]) >=
                max(angle(uv, tri[:2], v) for v in candidates)-1e-12,
                'Wrong existing-node neighborhood/max-angle choice')
        eligible = []
        for side, item in enumerate(step['alternatives']):
            require(item['side'] == side, 'Missing or reordered prospective alternative')
            base = [tri[2], tri[1]] if side == 0 else [tri[0], tri[2]]
            options = best_candidates(uv, before, data['leaves'], base, tri)
            if not options:
                require(item['triangle'] == [0, 0, 0] and not item['eligible'],
                        'Invented prospective neighbor')
                continue
            other = item['triangle'][2]
            require(item['triangle'][:2] == base and other in options and
                    angle(uv, base, other) >= max(angle(uv, base, v) for v in options)-1e-12,
                    'Prospective neighbor was chosen from a committed TRI mesh')
            quad = [tri[0], tri[1], other, tri[2]] if side == 0 else [*tri, other]
            require(item['quad'] == quad, 'Wrong prospective union cycle')
            score = shape(uv, quad)
            is_eligible = score is not None and score <= 1.5+1e-13
            require(item['eligible'] == is_eligible, 'Wrong planar shape classification')
            if score is not None:
                require(math.isclose(score, item['score'], abs_tol=2e-13), 'Wrong S score')
            if is_eligible:
                eligible.append((item['score'], side, quad))
            else:
                rejected += 1
        competing += len(eligible) == 2
        winner = min(eligible) if eligible else None
        require(step['selected_side'] == (-1 if winner is None else winner[1]) and
                step['polygon'] == (tri if winner is None else winner[2]), 'Wrong precommit winner')
        selected += winner is not None
        for a, b in edges(step['polygon']):
            if front[a, b]:
                del front[a, b]
            else:
                require(not front[b, a], 'Duplicate polygonal front insertion')
                front[b, a] = 1
        committed.append(step['polygon'])
        if directory:
            px, pu, pf = load_physical_obj(directory/f'commit_{index+1}.obj')
            require(px == xyz and pu == uv and pf == list(map(tuple, committed)), 'Commit OBJ differs from actual history')
    require(not front and Counter(map(tuple, committed)) == Counter(map(tuple, output)),
            'Unfinished contour or foreign final elements')
    return dict(commits=len(data['commits']), selected_quads=selected,
                retained_triangles=len(data['commits'])-selected, rejected_unions=rejected,
                competing_alternatives=competing)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--existing-prefix', type=Path)
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=True)
    prefix = args.existing_prefix or args.directory/f'article-{uuid.uuid4().hex}'
    if not args.existing_prefix:
        config = Path('configs/quad/curved_patch_article_front.conf').read_text()
        conf = args.directory/'article.conf'
        conf.write_text(config.replace('OUTPUT_PREFIX=build/quad_article_front', f'OUTPUT_PREFIX={prefix.as_posix()}'))
        run = subprocess.run([str(args.exe.resolve()), '--config', str(conf)], capture_output=True, timeout=180)
        (args.directory/'application.stdout').write_bytes(run.stdout)
        (args.directory/'application.stderr').write_bytes(run.stderr)
        require(run.returncode == 0, 'Article application failed')
    directory = Path(str(prefix)+'.steps')
    rows = list(csv.DictReader((directory/'manifest.csv').open()))
    require([int(r['step']) for r in rows] == [0, 1, 2, 3], 'Missing source generation stages')
    reports = []
    saved = None
    for row in rows[1:]:
        obj_path = directory/row['quad_tri_obj']
        native = audit(obj_path)
        history = directory/(obj_path.stem.removesuffix('_quad_tri')+'_article_front')
        data = json.loads((history/'front.json').read_text())
        obj = load_physical_obj(obj_path)
        report = replay(data, obj, history)
        reports.append(dict(step=int(row['step']), **native, **report))
        if saved is None:
            saved = data, obj
    require(all(r['selected_quads'] and r['retained_triangles'] for r in reports),
            'The real stages did not exercise mixed prospective generation')
    data, obj = saved
    corruptions = []
    for field in ('before', 'best', 'polygon', 'alternatives'):
        broken = copy.deepcopy(data)
        if field == 'before': broken['commits'][0][field].pop()
        elif field == 'best': broken['commits'][0][field][2] = broken['commits'][0][field][0]
        elif field == 'polygon': broken['commits'][0][field].reverse()
        else: broken['commits'][0][field].reverse()
        corruptions.append(broken)
    chosen = next(i for i, s in enumerate(data['commits']) if s['selected_side'] >= 0)
    for field in ('selected_side', 'score', 'eligible'):
        broken = copy.deepcopy(data)
        step = broken['commits'][chosen]
        if field == 'selected_side': step[field] = -1
        else: step['alternatives'][step['selected_side']][field] = 99 if field == 'score' else False
        corruptions.append(broken)
    broken = copy.deepcopy(data)
    broken['commits'].pop()
    corruptions.append(broken)
    for broken in corruptions:
        try: replay(broken, obj)
        except (AssertionError, KeyError, ValueError, IndexError): continue
        raise AssertionError('Forged prospective trace was accepted')
    rollback_verified = False
    if not args.existing_prefix:
        rollback_prefix = args.directory/f'rollback-{uuid.uuid4().hex}'
        rollback_conf = args.directory/'rollback.conf'
        rollback_conf.write_text(config.replace('OUTPUT_PREFIX=build/quad_article_front',
            f'OUTPUT_PREFIX={rollback_prefix.as_posix()}')+'\nQUAD_VERIFY_ROLLBACK=1\n')
        failure = subprocess.run([str(args.exe.resolve()), '--config', str(rollback_conf)],
                                 capture_output=True, timeout=180)
        (args.directory/'rollback.stdout').write_bytes(failure.stdout)
        (args.directory/'rollback.stderr').write_bytes(failure.stderr)
        require(failure.returncode == 1 and
                b'QUAD_REAL_BOUNDARY_ROLLBACK previous_nonempty=1 preserved=1' in failure.stdout,
                'Article candidate failed to preserve the existing owner on rejection')
        audit(Path(str(rollback_prefix)+'.obj'))
        rollback_verified = True
    report = dict(schema='apmesh.quad.article_application.v1', stages=reports,
                  rejected_forgeries=len(corruptions), rollback_verified=rollback_verified,
                  mixed_adaptive_epochs=0)
    (args.directory/'article_report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
