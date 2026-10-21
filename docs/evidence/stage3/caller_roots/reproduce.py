"""Require original reader retention and working CRT controls; not a repair gate."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--executable', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
source = Path(__file__).resolve().parent
root = source.parents[3]
fixture = source / 'one_patch.bp'
args.output.mkdir(exist_ok=False)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

report = {'status': 'running', 'classification': 'original defect reproduction only',
          'observed_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode().strip(),
          'executable_sha256': sha(args.executable), 'fixture_sha256': sha(fixture),
          'probe_source_sha256': sha(source / 'probe.cpp'),
          'cmake_sha256': sha(source / 'CMakeLists.txt'), 'cases': []}
for mode in ['clean', 'leak-control', 'unique-loader', 'direct', 'geometry', 'repeat']:
    command = [str(args.executable.resolve()), mode, str(fixture)]
    process = subprocess.run(command, cwd=root, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=30)
    log = args.output / (mode + '.log')
    log.write_bytes(process.stdout)
    match = re.search(rb'CRT retained_blocks=(\d+) retained_bytes=(\d+)', process.stdout)
    if not match:
        raise RuntimeError('Missing actual Debug CRT observation: ' + mode)
    blocks, size = map(int, match.groups())
    report['cases'].append({'mode': mode, 'argv': command, 'exit_code': process.returncode,
                            'retained_blocks': blocks, 'retained_bytes': size,
                            'log_sha256': sha(log),
                            'observations': process.stdout.decode('utf-8', errors='replace').splitlines()})
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
cases = {case['mode']: case for case in report['cases']}
for mode in ['clean', 'unique-loader']:
    assert cases[mode]['exit_code'] == 0 and cases[mode]['retained_blocks'] == 0, mode
for mode in ['leak-control', 'direct', 'geometry', 'repeat']:
    assert cases[mode]['exit_code'] == 1 and cases[mode]['retained_blocks'] > 0, mode
assert cases['direct']['retained_blocks'] == cases['leak-control']['retained_blocks'] == 1
assert cases['direct']['retained_bytes'] == cases['leak-control']['retained_bytes']
assert cases['geometry']['retained_blocks'] == cases['repeat']['retained_blocks'] == 2
assert any('first=1 second=2 same_first=1' in row for row in cases['repeat']['observations'])
report['status'] = 'original retention defects reproduced; no repaired candidate qualified'
report['scope'] = ('One valid patch, actual full production reader TU and isolated static Debug CRT. '
                   'No allocation-failure, malformed/rejected, broader-model, ASan, whole-process, '
                   'parallel, LSan or UBSan qualification.')
(args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
print(report['status'])
