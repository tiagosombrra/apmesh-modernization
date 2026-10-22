#!/usr/bin/env python3
"""Qualify initialized detached copies, defined payload, nonallocation and actual controls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def qualify(asan, crt, runtime, output):
    output.mkdir(parents=True, exist_ok=False)
    environment = dict(os.environ)
    environment['PATH'] = str(runtime.resolve()) + os.pathsep + environment.get('PATH', '')
    environment['ASAN_OPTIONS'] = 'detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1'
    modes = [('contracts', []), ('base', [])]
    modes += [('bezier', [str(shape), str(mask)]) for shape in range(2) for mask in range(16)]
    modes += [('hermite', [str(shape)]) for shape in range(2)]
    cases = [(name, exe, mode, extra) for name, exe in [('asan', asan), ('crt', crt)] for mode, extra in modes]
    cases += [('crt', crt, f'noalloc-{index}', []) for index in range(12)]
    controls = {'basis-control': 'initialized Bezier basis', 'metadata-control': 'zero detached metadata',
                'topology-control': 'detached topology', 'direction-control': 'initialized Hermite directions'}
    cases += [(name, exe, mode, []) for name, exe in [('asan', asan), ('crt', crt)] for mode in controls]
    cases += [('asan', asan, 'uaf-control', []), ('crt', crt, 'leak-control', []), ('crt', crt, 'hook-control', [])]
    report = {'status': 'running', 'cases': [], 'executables': {
        name: {'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        for name, path in [('asan', asan), ('crt', crt)]}}

    def save():
        (output/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')

    try:
        for instrument, executable, mode, extra in cases:
            name = '-'.join([instrument, mode, *extra])
            process = subprocess.run([str(executable.resolve()), mode, *extra], env=environment,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
            log = output/(name+'.log')
            log.write_bytes(process.stdout)
            text = process.stdout.decode('utf-8', errors='replace')
            retained = re.search(r'CRT retained_blocks=(\d+) retained_bytes=(\d+)', text)
            if mode in controls:
                passed = process.returncode == 2 and 'Detached patch-copy contract failed: '+controls[mode] in text
            elif mode == 'uaf-control':
                passed = process.returncode != 0 and 'ERROR: AddressSanitizer: heap-use-after-free' in text
            elif mode == 'leak-control':
                passed = process.returncode == 1 and retained is not None and int(retained[1]) > 0 and int(retained[2]) > 0
            else:
                passed = process.returncode == 0 and 'PASS' in text and 'ERROR: AddressSanitizer:' not in text
                if instrument == 'crt':
                    passed = passed and retained is not None and int(retained[1]) == int(retained[2]) == 0
                if mode.startswith('noalloc-'):
                    passed = passed and f'patch_copy_noalloc={mode[8:]},attempts:0' in text
                elif mode == 'hook-control':
                    passed = passed and 'patch_copy_hook=detected' in text
                elif mode in {'bezier', 'hermite'}:
                    passed = passed and text.count('xyz=') == 175 and 'evaluated_vectors=175' in text
                elif mode == 'contracts':
                    passed = passed and text.count('xyz=') == 5950 and text.count('evaluated_vectors=175') == 34
            row = {'instrument': instrument, 'mode': '-'.join([mode, *extra]),
                   'exit_code': process.returncode, 'passed': bool(passed), 'log': log.name,
                   'log_sha256': hashlib.sha256(process.stdout).hexdigest(),
                   'retained_blocks': int(retained[1]) if retained else None,
                   'retained_bytes': int(retained[2]) if retained else None,
                   'observations': [line for line in text.splitlines() if line.startswith(
                       ('patch_copy_', 'base_id_only', 'bezier shape=', 'hermite shape=', 'evaluated_vectors='))]}
            report['cases'].append(row)
            save()
            if not passed:
                raise ValueError('Required detached-copy case failed: '+name)
        assert len(report['cases']) == 95
        report.update(status='passed', zero_allocation_operations=12, rejected_runtime_corruptions=8,
                      positive_instrument_controls=3,
                      scope='Sixteen actual production units. Initialized Bezier basis, zero detached metadata '
                            'without source metadata reads, true internal Hermite flags, preserved defined numeric '
                            'payload and detached topology, repeated copies and source/copy retirement. Twelve '
                            'actual nonallocating copy/retirement observations and working denial/UAF/leak/oracle '
                            'controls. Live initialized sources only; no complete clone, default/control-only/null '
                            'source, caller preparation, ordinary Hermite retirement, external/parallel/full-process '
                            'or LSan/UBSan qualification.')
    except Exception as error:
        report.update(status='failed', error=str(error))
        save()
        raise
    save()
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['asan', 'crt', 'runtime', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    result = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps({key: value for key, value in result.items() if key not in {'cases', 'executables'}}))
