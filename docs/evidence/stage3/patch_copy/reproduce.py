"""Measure original detached patch-copy observations; do not qualify a complete clone or repair."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--gcc', type=Path, required=True)
parser.add_argument('--asan', type=Path, required=True)
parser.add_argument('--crt', type=Path, required=True)
parser.add_argument('--runtime', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
source = Path(__file__).resolve().parent
root = source.parents[3]
args.output.mkdir(exist_ok=False)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save():
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n',
                                          encoding='utf-8', newline='\n')


environment = dict(os.environ)
environment['PATH'] = str(args.runtime.resolve()) + os.pathsep + environment['PATH']
environment['ASAN_OPTIONS'] = 'detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1'
report = {'status': 'running', 'classification': 'original C22 audit; no production repair',
          'observed_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root,
                                                       text=True).strip(),
          'working_tree_status': subprocess.check_output(['git', 'status', '--porcelain=v1'],
                                                         cwd=root, text=True).splitlines(),
          'executables': {name: {'path': str(getattr(args, name).resolve()),
                                 'sha256': sha(getattr(args, name))} for name in ['gcc', 'asan', 'crt']},
          'recipe': {p.name: sha(p) for p in [source / 'probe.cpp', source / 'CMakeLists.txt',
                                             source / 'inventory.py', Path(__file__)]},
          'production_inputs': {str(p.relative_to(root)).replace('\\', '/'): sha(p)
                                for base in ['src', 'include', 'libs']
                                for p in sorted((root / base).rglob('*')) if p.is_file()},
          'cases': []}
modes = [('base', [])] + [('bezier', [str(shape), str(mask)]) for shape in range(2) for mask in range(16)]
modes += [('hermite', [str(shape)]) for shape in range(2)] + [('oracle-controls', [])]
try:
    for instrument in ['gcc', 'asan', 'crt']:
        scenarios = modes + ([('leak-control', [])] if instrument == 'crt' else
                             [('uaf-control', [])] if instrument == 'asan' else [])
        for mode, extra in scenarios:
            name = '-'.join([instrument, mode, *extra])
            command = [str(getattr(args, instrument).resolve()), mode, *extra]
            process = subprocess.run(command, cwd=root, env=environment, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, timeout=30)
            log = args.output / (name + '.log')
            log.write_bytes(process.stdout)
            row = {'instrument': instrument, 'mode': mode, 'arguments': extra, 'argv': command,
                   'log': log.name, 'log_sha256': sha(log), 'exit_code': process.returncode,
                   'expectation_met': False}
            report['cases'].append(row)
            save()
            data = process.stdout
            if mode == 'uaf-control':
                assert process.returncode != 0 and b'ERROR: AddressSanitizer: heap-use-after-free' in data
                row['diagnostic'] = 'actual heap-use-after-free in independent broken control'
            elif mode == 'leak-control':
                match = re.search(rb'CRT retained_blocks=(\d+) retained_bytes=(\d+)', data)
                assert match and process.returncode == 1
                row['retained_blocks'], row['retained_bytes'] = map(int, match.groups())
                assert row['retained_blocks'] > 0 and row['retained_bytes'] > 0
            else:
                assert process.returncode == 0 and b'ERROR: AddressSanitizer:' not in data
                if instrument == 'crt':
                    assert b'CRT retained_blocks=0 retained_bytes=0' in data
                if mode == 'base':
                    assert b'base_id_only=1 null_source=1 submesh_detached=1' in data
                elif mode == 'oracle-controls':
                    assert b'oracle_challenges=2 rejected=2' in data
                else:
                    assert b'evaluated_vectors=175' in data and data.count(b'xyz=') == 175
                    assert b'curves=0 submesh=0 incidence_unchanged=1' in data
                    row.update(paired_vectors=175, paired_scalar_values=525, analytic_points=25)
            row['expectation_met'] = True
            save()
        print(instrument, len(scenarios), 'expected observations', flush=True)
    assert len(report['cases']) == 110 and all(case['expectation_met'] for case in report['cases'])
    report.update(status='original bounded observations reproduced; no complete clone or repair qualified',
                  defined_cases=108, independent_instrument_controls=2,
                  paired_vectors=sum(case.get('paired_vectors', 0) for case in report['cases']),
                  paired_scalar_values=sum(case.get('paired_scalar_values', 0) for case in report['cases']),
                  analytic_points=sum(case.get('analytic_points', 0) for case in report['cases']),
                  limits='No indeterminate Bezier basis/load metadata or Hermite direction member is evaluated. '
                         'Their initialization omissions are source-only observations. Hermite source incidence '
                         'is explicitly removed before teardown. No complete clone, null derived source, failed '
                         'allocation sweep, FindUV, caller execution, scientific policy, full-process, parallel, '
                         'LSan or UBSan qualification. These are original observations, not a new repaired battery.')
except Exception as error:
    report.update(status='failed; retained original audit evidence', error=str(error))
    save()
    raise
save()
print(report['status'])
