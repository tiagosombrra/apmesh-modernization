"""Reproduce original Model hazards with independent instruments, not repair qualification."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--asan', required=True, type=Path)
parser.add_argument('--crt', required=True, type=Path)
parser.add_argument('--runtime', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
source = Path(__file__).resolve().parent
root = source.parents[3]
args.output.mkdir(exist_ok=False)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save():
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


environment = dict(os.environ)
environment['PATH'] = str(args.runtime.resolve()) + os.pathsep + environment['PATH']
environment['ASAN_OPTIONS'] = 'detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1'
report = {'status': 'running', 'classification': 'original Model hazard reproduction only',
          'observed_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode().strip(),
          'working_tree_status': subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=root).decode().splitlines(),
          'executables': {name: {'path': str(path.resolve()), 'sha256': sha(path)}
                          for name, path in [('asan', args.asan), ('crt', args.crt)]},
          'recipe': {p.name: sha(p) for p in [source / 'probe.cpp', source / 'CMakeLists.txt', Path(__file__)]},
          'production_inputs': {str(p.relative_to(root)).replace('\\', '/'): sha(p)
                                for base in ['src', 'include', 'libs']
                                for p in sorted((root / base).rglob('*')) if p.is_file()},
          'cases': []}
for instrument, modes in [
        ('crt', ['normal', 'leak-control', 'cleanup-empty', 'cleanup-seeded', 'failed-empty', 'failed-seeded']),
        ('asan', ['normal', 'uaf-control', 'copy-construct', 'copy-assign', 'rvalue-construct',
                  'rvalue-assign', 'duplicate-adoption'])]:
    for mode in modes:
        command = [str(getattr(args, instrument).resolve()), mode]
        process = subprocess.run(command, cwd=root, env=environment, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, timeout=30)
        log = args.output / f'{instrument}-{mode}.log'
        log.write_bytes(process.stdout)
        row = {'instrument': instrument, 'mode': mode, 'argv': command, 'exit_code': process.returncode,
               'log_sha256': sha(log), 'expectation_met': False}
        report['cases'].append(row)
        save()
        assert b'traits copy_ctor=1 copy_assign=1 rvalue_ctor=1 rvalue_assign=1 nothrow_rvalue=0' in process.stdout, mode
        if instrument == 'crt':
            match = re.search(rb'CRT retained_blocks=(\d+) retained_bytes=(\d+)', process.stdout)
            assert match, mode
            row['retained_blocks'], row['retained_bytes'] = map(int, match.groups())
            if mode in {'normal', 'cleanup-empty', 'cleanup-seeded'}:
                assert process.returncode == 0 and row['retained_blocks'] == row['retained_bytes'] == 0, mode
            else:
                assert process.returncode == 1 and row['retained_blocks'] > 0 and row['retained_bytes'] > 0, mode
            if mode.startswith(('failed-', 'cleanup-')):
                assert b'append_failure=1 denials=1' in process.stdout and b'destroyed=0' in process.stdout, mode
                expected_prefix = b'prefix=1' if mode.endswith('seeded') else b'prefix=0'
                assert expected_prefix in process.stdout, mode
            row['observations'] = process.stdout.decode('utf-8', errors='replace').splitlines()
        elif mode == 'normal':
            assert process.returncode == 0 and b'normal_meshes=2 nodes_destroyed=6' in process.stdout, mode
        else:
            assert process.returncode != 0, mode
            match = re.search(rb'ERROR: AddressSanitizer: (heap-use-after-free|attempting double-free)', process.stdout)
            assert match, mode
            row['asan_diagnostic'] = match.group(1).decode()
            if mode in {'copy-assign', 'rvalue-assign'}:
                assert b'assignment_old_payload_destroyed=0' in process.stdout, mode
        row['expectation_met'] = True
        save()
        print(json.dumps({k: row[k] for k in ['instrument', 'mode', 'exit_code', 'expectation_met']}), flush=True)
crt = {r['mode']: r for r in report['cases'] if r['instrument'] == 'crt'}
for mode in ['failed-empty', 'failed-seeded']:
    assert (crt[mode]['retained_blocks'], crt[mode]['retained_bytes']) == (
        crt['leak-control']['retained_blocks'], crt['leak-control']['retained_bytes']), mode
assert len(report['cases']) == 13 and all(r['expectation_met'] for r in report['cases'])
report['status'] = 'original hazards reproduced; no repaired candidate qualified'
report['limits'] = ('Four implicit-copy/rvalue operations and unsupported duplicate adoption reproduce actual ASan errors. '
                    'Two first-growth append denials reproduce caller-style pending-owner retention, with independent '
                    'caller-cleanup controls. Not a complete allocation sweep, parallel caller execution, numerical '
                    'regression, accepted/rejected policy validation, full-process, LSan or UBSan qualification. '
                    'A successful reproduction driver is not a repaired-model memory-safety pass.')
save()
print(report['status'])
