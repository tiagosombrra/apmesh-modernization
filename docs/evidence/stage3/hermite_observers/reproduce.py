"""Observe original Hermite retirement hazards; successful reproduction is not a repair pass."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[3]
BASE = '21542d8e739d98604b68fa92414332c694f4642d'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['gcc', 'asan', 'crt', 'runtime', 'output']:
        parser.add_argument('--' + name, required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False)
    archive = subprocess.check_output(['git', 'archive', BASE, 'src', 'include', 'libs'], cwd=ROOT)
    production = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as contents:
        for member in contents.getmembers():
            if member.isfile():
                value = hashlib.sha256(contents.extractfile(member).read()).hexdigest()
                assert sha(ROOT / member.name) == value, member.name
                production[member.name] = value
    assert len(production) == 488
    report = {
        'status': 'running', 'classification': 'engineering-only original hazard reproduction',
        'source_base': BASE,
        'observed_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'working_tree_status': subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=ROOT, text=True).splitlines(),
        'production_inputs': production,
        'recipe': {p.name: sha(p) for p in [SOURCE / 'probe.cpp', SOURCE / 'CMakeLists.txt',
                                           SOURCE / 'inventory.py', Path(__file__)]},
        'executables': {name: {'path': str(getattr(args, name).resolve()), 'sha256': sha(getattr(args, name))}
                        for name in ['gcc', 'asan', 'crt']}, 'cases': []}

    def save():
        (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')

    environment = dict(os.environ)
    environment['PATH'] = str(args.runtime.resolve()) + os.pathsep + environment['PATH']
    environment['ASAN_OPTIONS'] = 'detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1'
    defined = [['default'], ['geometry'], ['oracle']]
    defined += [['live', str(layout)] for layout in range(3)]
    defined += [[mode, str(layout), str(victim)] for mode in ['inventory', 'cleanup']
                for layout in range(3) for victim in range(3)]
    invocations = [(instrument, mode) for instrument in ['gcc', 'crt', 'asan'] for mode in defined]
    invocations += [('asan', ['consume', str(layout), str(victim)])
                    for layout in range(3) for victim in range(3)]
    invocations += [('asan', ['uaf-control']), ('crt', ['leak-control'])]
    try:
        for instrument, mode in invocations:
            command = [str(getattr(args, instrument).resolve()), *mode]
            name = instrument + '-' + '-'.join(mode) + '.log'
            process = subprocess.run(command, cwd=ROOT, env=environment, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, timeout=30)
            log = args.output / name
            log.write_bytes(process.stdout)
            row = {'instrument': instrument, 'mode': mode, 'argv': command, 'exit_code': process.returncode,
                   'log': name, 'log_sha256': sha(log), 'expectation_met': False}
            report['cases'].append(row)
            save()
            if mode[0] in {'consume', 'uaf-control'}:
                assert instrument == 'asan' and process.returncode != 0, name
                assert b'ERROR: AddressSanitizer: heap-use-after-free' in process.stdout, name
                row['asan_diagnostic'] = 'heap-use-after-free'
                if mode[0] == 'consume':
                    expected = [12, 8, 6][int(mode[1])]
                    assert f'stale_observers={expected}'.encode() in process.stdout, name
                    assert b'consume_observers=1 expected_expired=1' in process.stdout, name
                    row['stale_observers'] = expected
            elif mode[0] == 'leak-control':
                assert instrument == 'crt' and process.returncode == 1, name
            else:
                assert process.returncode == 0, name
                if mode[0] in {'cleanup', 'inventory'}:
                    expected = 0 if mode[0] == 'cleanup' else [12, 8, 6][int(mode[1])]
                    assert f'stale_observers={expected}'.encode() in process.stdout, name
                    row['stale_observers'] = expected
                    if mode[0] == 'cleanup':
                        assert b'consume_observers=1 expected_expired=0' in process.stdout, name
                        assert b'observer_id_sum=' in process.stdout, name
                if mode[0] == 'live':
                    assert b'evaluated_points=75 constructor_publications=12' in process.stdout, name
                if mode[0] == 'oracle':
                    assert b'oracle_corruptions=2 rejected=2' in process.stdout, name
            if instrument == 'crt':
                match = re.search(rb'CRT retained_blocks=(\d+) retained_bytes=(\d+)', process.stdout)
                assert match, name
                row['retained_blocks'], row['retained_bytes'] = map(int, match.groups())
                if mode[0] == 'leak-control':
                    assert row['retained_blocks'] > 0 and row['retained_bytes'] > 0, name
                else:
                    assert row['retained_blocks'] == row['retained_bytes'] == 0, name
            row['expectation_met'] = True
            save()
        assert len(report['cases']) == 83 and all(c['expectation_met'] for c in report['cases'])
        report.update(status='original hazards reproduced; no repaired candidate qualified',
                      defined_observations=72, original_expired_observer_asan_failures=9,
                      independent_instrument_controls=2, live_evaluated_points=675,
                      source_files_unchanged=488,
                      limits='Completed initialized Hermite patches and live borrowed curves only. '
                             'Paired/all-repeated slots are lifetime fixtures, not valid surface claims. '
                             'Zero CRT retention does not prove observer validity. No failed-construction/adoption '
                             'sweep, actual Adapter/Generator execution, complete CLI, foreign/copied observer list, '
                             'ReplaceCurve, numerical differential regression, parallel, LSan or UBSan qualification.')
    except Exception as error:
        report.update(status='failed', error=str(error))
        save()
        raise
    save()
    print(json.dumps({k: v for k, v in report.items()
                      if k not in {'cases', 'production_inputs', 'executables', 'recipe', 'working_tree_status'}}))


if __name__ == '__main__':
    main()
