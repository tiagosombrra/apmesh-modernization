#!/usr/bin/env python3
"""Exercise native angular selection and every measured temporary allocation."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile


def analyze(data, code, layout, ordinal, total, original=False):
    """Reject incomplete traces; original retention is a failed unwind contract."""
    expected_id = 302 if layout == 2 else 301
    if data['layout'] != layout or data['mode'] != str(ordinal):
        raise ValueError('Wrong native case identity')
    if data['profile'] not in ('native-allocation-observer', 'msvc-debug-crt'):
        raise ValueError('Unknown allocation observation profile')
    if total < 2 or total % 2 or data['geometry'] != int(layout == 4) or data['entered'] != 1:
        raise ValueError('Missing positive native allocation/phase coverage')
    if data['attempts'] != (ordinal or total) or data['denied'] != int(ordinal > 0):
        raise ValueError('Incomplete allocation sweep or denial did not occur')
    if data['threw'] != int(ordinal > 0) or data['finished'] != int(ordinal == 0):
        raise ValueError('Exception propagation or normal completion mismatch')
    built = (ordinal - 1) // (total // 2) if ordinal else 2
    retained = bool(original and ordinal > total // 2)
    if data['constructed'] != built or data['released'] != (0 if retained else built):
        raise ValueError('Temporary lifetime observation is incomplete')
    expected_order = [1, 2] if not ordinal else [1, 0] if built and not retained else [0, 0]
    if data['release_order'] != expected_order:
        raise ValueError('Successful release order or unwind release changed')
    if retained:
        if code != 1 or data['retained_blocks'] <= 0 or data['retained_bytes'] <= 0:
            raise ValueError('Original failed clean-unwind contract was not reproduced')
    elif code != 0 or data['retained_blocks'] != 0 or data['retained_bytes'] != 0:
        raise ValueError('Measured temporary storage remains after fixture teardown')
    if ordinal:
        if (data['found'], data['selected_id'], data['observed_id'], data['values']) != (0, -1, -1, [0]*5):
            raise ValueError('Incomplete selection unexpectedly published on failure')
    else:
        x, y = [(0.5, 1), (0.75, 0.75), (0.25, 0.75), (0.25, 0.7), (0.5, 0.75)][layout]
        angle_x = 0.25 if layout == 1 else x
        angle = math.acos((angle_x*(angle_x-1)+y*y) /
                          (math.hypot(angle_x, y)*math.hypot(1-angle_x, y)))
        expected = [-x, -y, 1-x, -y, angle]
        if (data['found'], data['selected_id'], data['observed_id']) != (1, expected_id, expected_id):
            raise ValueError('Actual selected candidate changed')
        if len(data['values']) != 5 or any(not math.isfinite(v) or not math.isclose(v, e, rel_tol=1e-14, abs_tol=1e-14)
                                           for v, e in zip(data['values'], expected)):
            raise ValueError('Independent vector or angle observation differs')
    return {'clean_unwind_contract': 'failed' if retained else 'passed'}


def qualify(exe, output, original=None, runtime=None, asan_control=False):
    output.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy()
    if runtime:
        environment['PATH'] = str(runtime.resolve()) + os.pathsep + environment.get('PATH', '')
    if asan_control:
        environment['ASAN_OPTIONS'] = 'detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1'
    report = {'status': 'running', 'cases': [], 'original_failed_unwind_contracts': 0,
              'executables': {}, 'scope': 'Native angular pair only; no whole-process or LSan claim'}

    def run(binary, label, layout, mode):
        name = f'{label}-{layout}-{mode}.log'
        command = [str(binary.resolve()), str(layout), str(mode)]
        with (output / name).open('xb') as stream:
            process = subprocess.run(command, env=environment, stdout=stream, stderr=subprocess.STDOUT, timeout=30)
        raw = (output / name).read_bytes()
        record = {'command': command, 'exit_code': process.returncode, 'log': name,
                  'log_sha256': hashlib.sha256(raw).hexdigest(), 'label': label}
        report['cases'].append(record)
        text = raw.decode('utf-8', errors='replace')
        if mode == 'uaf-control':
            if process.returncode == 0 or 'ERROR: AddressSanitizer: heap-use-after-free' not in text:
                raise ValueError('Actual AddressSanitizer negative control was not detected')
            record['expected_detection'] = True
            return None
        if 'ERROR: AddressSanitizer:' in text:
            raise ValueError('Unexpected AddressSanitizer error')
        data = json.loads(text)
        record['observation'] = data
        return record

    try:
        normal = {}
        for label, binary in [('candidate', exe)] + ([('original', original)] if original else []):
            report['executables'][label] = {'path': str(binary.resolve()), 'sha256': hashlib.sha256(binary.read_bytes()).hexdigest()}
            for layout in range(5):
                first = run(binary, label, layout, 0)
                total = first['observation']['attempts']
                first.update(analyze(first['observation'], first['exit_code'], layout, 0, total))
                if label == 'candidate':
                    normal[layout] = first['observation']
                elif first['observation'] != normal[layout]:
                    raise ValueError('Original/candidate normal observations are not exact')
                for ordinal in range(1, total+1):
                    item = run(binary, label, layout, ordinal)
                    item.update(analyze(item['observation'], item['exit_code'], layout, ordinal, total, label == 'original'))
                    report['original_failed_unwind_contracts'] += item['clean_unwind_contract'] == 'failed'
        for mode in ('leak-control', 'denial-control'):
            item = run(exe, 'control', 0, mode)
            d = item['observation']
            if mode == 'leak-control':
                valid = item['exit_code'] == 1 and d['retained_blocks'] > 0 and d['retained_bytes'] > 0 and d['attempts'] > 0
            else:
                valid = item['exit_code'] == 0 and d['denied'] == d['attempts'] == d['threw'] == 1 and d['retained_blocks'] == d['retained_bytes'] == 0
            if not valid or d['entered'] != 1:
                raise ValueError('Independent retention/allocation-hook control failed')
            item['expected_detection'] = True
        if asan_control:
            run(exe, 'control', 0, 'uaf-control')
        report.update(status='passed', candidate_layouts=5, normal_traces_exact=5 if original else 0,
                      expected_outcomes=len(report['cases']))
    except Exception as error:
        report.update(status='failed', failure=repr(error))
        raise
    finally:
        (output / 'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--original', type=Path)
    parser.add_argument('--runtime', type=Path)
    parser.add_argument('--asan-control', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repeatable-output', action='store_true')
    args = parser.parse_args()
    if args.repeatable_output:
        args.output.mkdir(parents=True, exist_ok=True)
        # Keep every invocation, including failures, without replacing prior logs.
        parent = args.output
        args.output = Path(tempfile.mkdtemp(prefix='run-', dir=parent)) / 'evidence'
    result = qualify(args.exe, args.output, args.original, args.runtime, args.asan_control)
    print(json.dumps({key: result[key] for key in ('status', 'expected_outcomes', 'original_failed_unwind_contracts')}))
