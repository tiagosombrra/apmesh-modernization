#!/usr/bin/env python3
"""Qualify native first-edge pending ownership and preserve original failures."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import tempfile

CONTEXTS = list(itertools.product((0, 1), repeat=4))
CLEANUP_FIELDS = {'owned', 'cleanup_calls', 'cleanup_allocations'}
FAILURE_FIELDS = CLEANUP_FIELDS | {'freed', 'mid_freed', 'adjacent_a', 'adjacent_c',
                                  'pending_adjacent', 'retained_blocks', 'retained_bytes'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def analyze(d, code, context, ordinal, total, original=False):
    require(tuple(context) in CONTEXTS and total in (9, 11), 'Unsupported native fixture or allocation inventory')
    require(0 <= ordinal <= total, 'Unsupported allocation denial')
    front, geometry, _, prefix = context
    ctor = total - 6
    require(d['context'] == list(context) and d['target'] == ordinal, 'Wrong native case identity')
    require(d['owned'] == int(not original), 'Wrong pending-owner source variant')
    require(d['entered'] == 1 and d['before_id'] == 0 and d['before_owners'] == 4 + 3 * prefix, 'Missing first-edge window or prefix')
    require(d['borrowed'] == 4 + 3 * prefix and d['destroyed'] == ([1, 1, 1, 0] if prefix else [0, 0, 0, 0]) + [1, 1, 1, 1], 'Borrowed endpoints or exactly-once owner retirement differ')
    require(d['last_edge'] == int(ordinal != 1) and d['edge_id'] == (-1 if 0 < ordinal <= ctor else 1), 'Original new-expression ID timing differs')
    require(d['cleanup_allocations'] == 0, 'Production cleanup allocated')
    if ordinal == 0:
        require(code == 0 and d['threw'] == d['denied'] == 0 and d['status'] == (5 if geometry else 6), 'Normal native status differs')
        require(d['phase'] == 7 and d['attempts'] == total and d['cleanup_calls'] == 0, 'Normal allocation/cleanup timing differs')
        require(d['retained_blocks'] == d['retained_bytes'] == 0, 'Normal execution retained storage')
        require(d['owners'] == d['views'] == 5 + 3 * prefix and d['mesh'] == d['faces'] == 2 + prefix, 'Normal ownership/Face publication differs')
        require(d['face_order'] == prefix * 123000000 + (567785 if front else 567578), 'Native Face order differs')
        require(d['front'] == (0 if front else 3) and d['rejected'] == d['queue_pending'] == d['free_edges'] == 0, 'Normal front/free state differs')
        require(d['adjacent_a'] == d['adjacent_c'] == 3 and d['pending_adjacent'] == 2 and d['last_face'] == 2 + prefix, 'Normal endpoint adjacency or IDs differ')
        require(d['cell'] == d['cell_pending'] == d['owner_pending'] == d['view_pending'] == d['freed'] == d['mid_freed'] == 1, 'Normal adoption/cache retirement differs')
        return 'normal'
    phase = 0 if ordinal <= ctor else ordinal - ctor
    cleanup = int(not original and 0 < phase < 4)
    require(d['threw'] == d['denied'] == 1 and d['status'] == -1 and d['attempts'] == ordinal and d['phase'] == phase, 'Missing calibrated native denial/propagation')
    require(d['cleanup_calls'] == cleanup, 'Pending cleanup did not execute exactly when required')
    require(d['mesh'] == d['faces'] == d['last_face'] == prefix and d['face_order'] == 123 * prefix, 'Committed Face prefix changed')
    require(d['owners'] == 4 + 3 * prefix + (phase >= 4) and d['views'] == 4 + 3 * prefix + (phase >= 5), 'Owner/view publication timing differs')
    require(d['owner_pending'] == (phase >= 4) and d['view_pending'] == (phase >= 5), 'Published pending identity differs')
    require(d['adjacent_a'] == 2 + (phase >= 2 and not cleanup) and d['adjacent_c'] == 2 + (phase >= 3 and not cleanup), 'Endpoint adjacency was not preserved or cleaned')
    require(d['pending_adjacent'] == (0 if cleanup or phase == 0 else int(phase >= 2) + int(phase >= 3)), 'Expired pending adjacency remains')
    require(d['front'] == 3 + (phase == 6 and front) and d['rejected'] == (phase == 6 and not front), 'Original active queue state differs')
    require(d['queue_pending'] == (phase == 6) and d['cell'] == d['cell_pending'] == 0 and d['free_edges'] == 4 + (phase >= 4), 'Original queue/cell/free-state publication differs')
    retained = bool(original and 0 < phase < 4)
    require(code == int(retained), 'Unexpected native process exit')
    expected = ((3, 272) if total == 9 else (5, 296)) if retained else (0, 0)
    require((d['retained_blocks'], d['retained_bytes']) == expected, 'Original retention or candidate release differs')
    require(d['freed'] == d['mid_freed'] == int(phase >= 4 or cleanup), 'Actual pending Edge/cache release differs')
    return ('original pending ownership failed' if retained else 'nonallocating pending cleanup' if cleanup
            else 'construction unwind' if phase == 0 else 'owned partial publication')


def qualify(exe, output, original=None, broken=None, stale=None, runtime=None, asan=False):
    output.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    if runtime:
        env['PATH'] = str(runtime.resolve()) + os.pathsep + env.get('PATH', '')
    if asan:
        env['ASAN_OPTIONS'] = 'detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1'
    r = {'status': 'running', 'cases': [], 'executables': {}, 'normal_comparisons': 0,
         'denial_comparisons': 0, 'nonallocating_cleanups': 0, 'original_failed_contracts': 0,
         'wrong_deleter_detections': 0, 'stale_adjacency_detections': 0, 'instrument_controls': 0}
    for label, binary in [('candidate', exe), ('original', original), ('broken', broken), ('stale', stale)]:
        if binary:
            r['executables'][label] = {'path': str(binary.resolve()), 'sha256': hashlib.sha256(binary.read_bytes()).hexdigest()}

    def run(binary, label, context, ordinal, action=0):
        argv = [str(binary.resolve()), *map(str, context), str(ordinal), str(action)]
        name = f'{label}-' + ''.join(map(str, context)) + f'-{ordinal}-{action}.log'
        with (output / name).open('xb') as log:
            p = subprocess.run(argv, cwd=Path(__file__).resolve().parents[1], env=env, stdout=log, stderr=subprocess.STDOUT, timeout=20)
        raw = (output / name).read_bytes()
        c = {'label': label, 'context': list(context), 'ordinal': ordinal, 'action': action,
             'argv': argv, 'exit': p.returncode, 'log': name, 'log_sha256': hashlib.sha256(raw).hexdigest()}
        r['cases'].append(c)
        return c, raw.decode(errors='replace').replace('\r\n', '\n')

    try:
        totals = {}
        candidates = {}
        for label, binary in [('candidate', exe)] + ([('original', original)] if original else []):
            for context in CONTEXTS:
                first, text = run(binary, label, context, 0)
                first['observation'] = json.loads(text)
                total = first['observation']['attempts']
                require(total in (9, 11), 'Unsupported native allocation calibration')
                if label == 'candidate':
                    totals[context] = total
                else:
                    require(total == totals[context], 'Original/candidate allocations differ')
                for ordinal in range(total + 1):
                    if ordinal == 0:
                        c = first
                    else:
                        c, text = run(binary, label, context, ordinal)
                        c['observation'] = json.loads(text)
                    d = c['observation']
                    c['contract'] = analyze(d, c['exit'], context, ordinal, total, label == 'original')
                    if label == 'candidate':
                        candidates[(context, ordinal)] = d
                        r['nonallocating_cleanups'] += d['cleanup_calls']
                    else:
                        r['original_failed_contracts'] += c['contract'] == 'original pending ownership failed'
                        excluded = FAILURE_FIELDS if total - 6 < ordinal < total - 2 else CLEANUP_FIELDS
                        peer = candidates[(context, ordinal)]
                        require({k:v for k,v in d.items() if k not in excluded} == {k:v for k,v in peer.items() if k not in excluded}, 'Native preservation comparison differs')
                        r['normal_comparisons' if ordinal == 0 else 'denial_comparisons'] += 1
        for context in CONTEXTS:
            total = totals[context]
            ctor = total - 6
            if broken:
                for ordinal in range(ctor + 1, ctor + 4):
                    c, text = run(broken, 'broken', context, ordinal)
                    require(c['exit'] == 4 and text == f'borrowed_endpoint_destroyed=4 phase={ordinal-ctor} denied=1\n', 'Actual invalid-deleter damage was not detected')
                    c['contract'] = 'actual borrower destruction detected'
                    r['wrong_deleter_detections'] += 1
            if stale:
                for ordinal in (ctor + 2, ctor + 3):
                    c, text = run(stale, 'stale', context, ordinal, int(asan))
                    if asan:
                        require(c['exit'] != 0 and 'ERROR: AddressSanitizer: heap-use-after-free' in text and 'ReadEdgeId' in text, 'Actual stale-adjacency access was not detected')
                    else:
                        d = json.loads(text)
                        c['observation'] = d
                        require(c['exit'] == 0 and d['pending_adjacent'] == ordinal - ctor - 1, 'Native expired-adjacency observation missing')
                        try:
                            analyze(d, c['exit'], context, ordinal, total)
                        except ValueError:
                            pass
                        else:
                            raise ValueError('Invalid detach-only deleter passed the ownership checker')
                    c['contract'] = 'actual expired adjacency detected'
                    r['stale_adjacency_detections'] += 1
        for name in ['denial-control', 'leak-control'] + (['uaf-control'] if asan else []):
            c, text = run(exe, 'control', (0, 0, 0, 0), name)
            if name == 'uaf-control':
                require(c['exit'] != 0 and 'ERROR: AddressSanitizer: heap-use-after-free' in text, 'Actual ASan instrument control missing')
            else:
                d = json.loads(text)
                c['observation'] = d
                valid = (c['exit'] == 0 and d['threw'] == d['denied'] == d['attempts'] == 1 and d['retained_blocks'] == d['retained_bytes'] == 0) if name == 'denial-control' else (c['exit'] == 1 and d['retained_blocks'] == (1 if totals[(0,0,0,0)] == 9 else 2) and d['retained_bytes'] > 0)
                require(valid, 'Independent allocation instrument control missing')
            c['contract'] = 'independent invalid instrument detected'
            r['instrument_controls'] += 1
        r.update(status='passed', native_outcomes=len(r['cases']))
    except Exception as error:
        r.update(status='failed', failure=repr(error))
        raise
    finally:
        (output / 'report.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    return r


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('exe', 'original', 'broken', 'stale', 'runtime', 'output'):
        p.add_argument('--' + name, type=Path, required=name in ('exe', 'output'))
    p.add_argument('--asan-control', action='store_true')
    p.add_argument('--repeatable-output', action='store_true')
    args = p.parse_args()
    if args.repeatable_output:
        args.output.mkdir(parents=True, exist_ok=True)
        args.output = Path(tempfile.mkdtemp(prefix='run-', dir=args.output)) / 'evidence'
    result = qualify(args.exe, args.output, args.original, args.broken, args.stale, args.runtime, args.asan_control)
    print(json.dumps({k:v for k,v in result.items() if k not in ('cases', 'executables')}))
