"""Check analytic prefix completion separately from guard-only and refused cases."""
from pathlib import Path
import argparse
import itertools
import json
import math
import subprocess
import time
import uuid

CONTEXTS = list(itertools.product((2, 4), (0, 15), (0, 1), (0,)))
CONTROL = (2, 0, 0, 1)
PROGRESS = ['gerou a quadtree', 'refinou a quadtree', 'gerou malha por templates']
OBSERVATION_ONLY = {'presorts', 'sort_reads', 'preflights', 'reads'}


def require_contract(observation, context, *, observed=True, profile='gcc'):
    """Keep historical refusal parsing separate from the current required matrix."""
    contract = check(observation, context, observed=observed, profile=profile)
    if tuple(context) == CONTROL:
        required = 'actual input preflight refusal'
    elif context[0] == 4 or context[2] == 1:
        required = 'completed nonempty native prefix'
    else:
        required = 'completed guard-only prefix; no template coverage'
    if contract != required:
        raise ValueError(f'Required native prefix contract not satisfied: {tuple(context)}; '
                         f'expected {required}; observed {contract}')
    return contract


def parse_output(text):
    """Preserve and recognize only the exact native progress prefix."""
    marker = '{"context":'
    if text.count(marker) != 1:
        raise ValueError('Missing or duplicate native prefix observation')
    start = text.index(marker)
    progress = text[:start].splitlines()
    if progress not in [PROGRESS[:n] for n in range(4)]:
        raise ValueError('Unexpected native diagnostic before prefix observation')
    result = json.loads(text[start:])
    if result['status'] == 'prefix_completed' and progress != PROGRESS:
        raise ValueError('Completed prefix lacks native stage progress')
    if result['status'] == 'prefix_refused':
        expected = [] if result['reason'] == 'normalized_boundary_size' else PROGRESS[:2]
        if progress != expected:
            raise ValueError('Refused prefix has inconsistent native stage progress')
    return result


def graph(j):
    rows = j['leaves']
    assert rows and len({r['id'] for r in rows}) == len(rows)
    index = {r['id']: r for r in rows}
    area = 0.0
    links = interior = 0
    for row in rows:
        x, y, xx, yy = row['box']
        assert all(math.isfinite(v) for v in row['box'])
        assert 0 <= x < xx <= 1 and 0 <= y < yy <= 1
        assert xx - x == yy - y == 2.0 ** (-row['level'])
        area += (xx - x) * (yy - y)
        expected = [[] for _ in range(4)]
        for other in rows:
            if row['id'] == other['id']:
                continue
            a, b, aa, bb = other['box']
            horizontal = min(xx, aa) - max(x, a)
            vertical = min(yy, bb) - max(y, b)
            assert horizontal <= 0 or vertical <= 0
            for d, touching, overlap in [(0, y == bb, horizontal), (1, xx == a, vertical),
                                         (2, yy == b, horizontal), (3, x == aa, vertical)]:
                if touching and overlap > 0:
                    expected[d].append(other['id'])
        for d, actual in enumerate(row['neighbors']):
            assert set(actual) == set(expected[d]) and len(actual) <= 2
            assert len(actual) == len(set(actual))
            ordered = sorted(actual, key=lambda i: index[i]['box'][0 if d % 2 == 0 else 1],
                             reverse=d >= 2)
            assert actual == ordered
            assert all(abs(row['level'] - index[i]['level']) <= 1 for i in actual)
            links += len(actual)
        interior += all(row['neighbors'])
    assert area == 1 and links == j['cardinal_links'] and interior == j['interior_leaves']
    return sum((r['box'][2] - r['box'][0]) ** 2 for r in rows if all(r['neighbors']))


def check(j, context, *, observed=True, profile='gcc'):
    assert tuple(j['context']) == tuple(context)
    assert tuple(context) in CONTEXTS + [CONTROL]
    divisions, _, old, control = context
    assert j['configuration'] == [1, 0.0001, -1, 1]
    assert j['old_faces'] == 2 * old and j['old_h'] == (0.25 if old else 0)
    assert j['teardown'] == j['curves_live'] == 1
    assert j['iterator_level'] == (2 if profile == 'crt' else -1)
    assert j['boundary'][:2] == [4 * divisions, 4 * divisions]
    if control:
        assert observed and j['status'] == 'prefix_refused'
        assert j['reason'] == 'normalized_boundary_size' and j['refusal_tag'] == -1
        assert j['presorts'] == j['preflights'] == j['geometry_entries'] == 0
        assert j['reads'] == [0, 0] and j['leaves'] == [] and j['templates'] == [0, 0, 0, 0]
        return 'actual input preflight refusal'
    if j['status'] == 'prefix_refused':
        assert observed and j['geometry_entries'] == 0
        assert j['reason'] in ('empty_neighbor_read', 'null_neighbor_read', 'foreign_neighbor_read')
        assert j['refusal_tag'] >= 0 and j['presorts'] == j['preflights'] == 1
        graph(j)
        return 'refused native prefix; not qualified'
    assert j['status'] == 'prefix_completed' and j['reason'] == 'none' and j['refusal_tag'] == -1
    assert j['geometry_entries'] == 1
    assert j['boundary'][2] == 4 and 0 <= j['boundary'][3] <= 0.0002
    if observed:
        assert j['presorts'] == j['preflights'] == 1
    else:
        assert j['presorts'] == j['preflights'] == j['sort_reads'] == 0 and j['reads'] == [0, 0]
    area = graph(j)
    vertices, edges, faces, measured_area = j['templates']
    assert j['ids'] == [4 * divisions + vertices, 4 * divisions + edges, faces]
    assert j['views'][1] == j['views'][2] >= 4 * divisions
    assert 4 * divisions <= j['views'][0] <= 4 * divisions + vertices
    assert math.isfinite(measured_area) and abs(measured_area - area) <= 1e-12
    if faces:
        assert vertices > 0 and edges > 0 and area > 0
        if observed:
            assert all(v > 0 for v in j['reads'])
        return 'completed nonempty native prefix'
    assert vertices == edges == faces == measured_area == j['interior_leaves'] == 0
    return 'completed guard-only prefix; no template coverage'


def compare(a, b):
    assert {k: v for k, v in a.items() if k not in OBSERVATION_ONLY} == {
        k: v for k, v in b.items() if k not in OBSERVATION_ONLY}


def run_cases(exe, unobserved, output, profile='gcc'):
    import hashlib
    output.mkdir(parents=True, exist_ok=False)
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    report = {'status': 'running', 'profile': profile, 'cases': [], 'qualified_contexts': [],
              'guard_only_contexts': [], 'refused_contexts': [],
              'executables': {k: {'path': str(p), 'sha256': sha(p)} for k, p in
                              [('observed', exe), ('unobserved', unobserved)]}}
    try:
        for context in CONTEXTS + [CONTROL]:
            pair = {}
            for label, binary in [('observed', exe), ('unobserved', unobserved)]:
                argv = [str(binary), *map(str, context)]
                result = subprocess.run(argv, capture_output=True, timeout=30)
                name = label + '-' + '-'.join(map(str, context)) + '.log'
                (output / name).write_bytes(result.stdout + result.stderr)
                case = {'label': label, 'context': list(context), 'argv': argv,
                        'exit': result.returncode, 'log': name, 'sha256': sha(output / name)}
                report['cases'].append(case)
                assert result.returncode == 0, (context, label, result.returncode)
                j = parse_output((result.stdout + result.stderr).decode('utf-8'))
                case['observation'] = j
                contract = require_contract(j, context, observed=label == 'observed', profile=profile)
                case['contract'] = contract
                pair[label] = j
                if label == 'observed':
                    if 'not qualified' in contract or context == CONTROL:
                        report['refused_contexts'].append(list(context))
                        break
                    key = 'qualified_contexts' if contract == 'completed nonempty native prefix' else 'guard_only_contexts'
                    report[key].append(list(context))
                else:
                    compare(pair['observed'], j)
        assert len(report['cases']) == 17, 'Required native prefix inventory is incomplete'
        assert len(report['qualified_contexts']) == 6 and len(report['guard_only_contexts']) == 2
        assert report['refused_contexts'] == [list(CONTROL)]
        assert len({(tuple(row['context']), row['label']) for row in report['cases']}) == 17
        report.update(status='prefix_fixture_checked', native_outcomes=len(report['cases']),
                      retirement_measurements=0, finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    except Exception as error:
        report.update(status='failed', failure=repr(error))
        raise
    finally:
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--unobserved', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile', choices=('gcc', 'crt'), default='gcc')
    parser.add_argument('--repeatable-output', action='store_true')
    args = parser.parse_args()
    folder = args.output / ('run-' + uuid.uuid4().hex) if args.repeatable_output else args.output
    result = run_cases(args.exe.resolve(), args.unobserved.resolve(), folder.resolve(), args.profile)
    print(json.dumps({k: v for k, v in result.items() if k not in ('cases', 'executables')}))
