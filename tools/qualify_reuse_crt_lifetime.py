#!/usr/bin/env python3
"""Qualify the fixed two-call adaptive history through executable-static teardown."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

from qualify_serial_crt_lifetime import inspect_lifetime, qualify_control
from validation_session import command_environment
from verify_generation import compare_runs, verify_run

ROOT = Path(__file__).resolve().parents[1]
CONTROLS = ('release', 'global-release', 'late-release', 'retention', 'late-retention', 'denial')
REUSE = re.compile(r'adaptive_reuse call=(\d+) exit=(-?\d+) archived=(\d+) calls=(\d+) imax=(\d+)')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def inspect_reuse(stdout, stderr, exit_code, expected_archives):
    lifetime = inspect_lifetime(stdout, stderr, exit_code)
    if (exit_code or not lifetime['clean'] or lifetime['late_mode'] or
            lifetime['observed_allocations'] or lifetime['attempts'] or
            lifetime['denied'] or lifetime['caught']):
        raise ValueError('Adaptive reuse lacks clean, unmodified executable-lifetime accounting')
    lines = stdout.splitlines()
    matches = [REUSE.fullmatch(line) for line in lines if not line.startswith('LIFETIME_MAIN ')]
    if len(matches) != 2 or any(match is None for match in matches):
        raise ValueError('Missing, duplicate or unknown adaptive reuse observation')
    rows = [tuple(map(int, match.groups())) for match in matches]
    if (expected_archives <= 0 or [row[0] for row in rows] != [0, 1] or
            any(row[1] != 0 or row[2] != expected_archives or row[3] <= 0 for row in rows) or
            rows[0][3:] != rows[1][3:]):
        raise ValueError('Native call order, completion, archives or execution counters differ')
    return {'lifetime': lifetime, 'calls': [dict(zip(
        ('index', 'exit', 'archived', 'finduv_calls', 'imax_exits'), row)) for row in rows]}


def verify_pair(reference, folder, metadata, expected):
    baseline = verify_run(reference, require_boundary=True)
    hashes = {p.name: digest(p) for p in reference.iterdir() if p.is_file()}
    outcomes = []
    for index, name in enumerate(('first', 'second')):
        output = folder / name
        write(output / 'process.json', dict(metadata, status='completed', exit_code=0, call_index=index))
        measured = verify_run(output, require_boundary=True)
        comparison = compare_runs(baseline, measured)
        exact = []
        for filename in hashes:
            old, new = reference / filename, output / filename
            if not (old.suffix in ('.obj', '.csv') or filename.endswith('_incidences.json') or '_acceptance_' in filename):
                continue
            if filename.endswith('_runtime_summary.csv'):
                continue
            if filename.endswith('_compatibility_summary.csv'):
                def values(path):
                    with path.open(encoding='utf-8', newline='') as stream:
                        return [{k: v for k, v in row.items() if k != 'model'} for row in csv.DictReader(stream)]
                if values(old) != values(new):
                    raise ValueError('Relocated compatibility fields changed')
            else:
                if old.read_bytes() != new.read_bytes():
                    raise ValueError('Scientific artifact changed: ' + filename)
                exact.append(filename)
        counts = (len(measured['meshes']), len(exact),
                  sum(row['compared_incidences'] for row in measured['boundary_incidences'].values()))
        if counts != expected:
            raise ValueError('Required scientific coverage differs: ' + repr(counts))
        write(output / 'verification.json', measured)
        write(output / 'comparison.json', comparison)
        outcomes.append({'index': index, 'states': counts[0], 'exact_artifacts': exact,
                         'positive_boundaries': counts[2], 'accepted': measured['accepted_steps'],
                         'rejected': measured['rejected_steps']})
    if hashes != {p.name: digest(p) for p in reference.iterdir() if p.is_file()}:
        raise ValueError('Reference artifacts changed during qualification')
    return outcomes


def qualify(executable, output, references):
    output.mkdir(parents=True, exist_ok=False)
    env = command_environment(ROOT)
    report = {'status': 'running', 'executable_sha256': digest(executable), 'cases': []}

    def native(name, arguments, cap):
        row = {'case': name, 'argv': [str(executable), *map(str, arguments)], 'cap_seconds': cap}
        report['cases'].append(row)
        paths = [output / (name + suffix) for suffix in ('.stdout', '.stderr')]
        started = time.monotonic()
        with paths[0].open('xb') as stdout, paths[1].open('xb') as stderr:
            try:
                process = subprocess.run(row['argv'], cwd=ROOT, env=env, stdout=stdout, stderr=stderr, timeout=cap)
                row['exit'] = process.returncode
            except subprocess.TimeoutExpired:
                row['status'] = 'timeout'
                raise
            finally:
                row['seconds'] = time.monotonic() - started
                row['streams'] = {p.name: digest(p) for p in paths}
        print(json.dumps({'case': name, 'exit': row['exit'], 'seconds': row['seconds']}), flush=True)
        return row, paths[0].read_text(encoding='utf-8'), paths[1].read_text(encoding='utf-8')

    try:
        for mode in CONTROLS:
            row, stdout, stderr = native(mode, ['--lifetime-control', mode], 10)
            data = inspect_lifetime(stdout, stderr, row['exit'])
            qualify_control(mode, data)
            row.update(status='control_qualified', observation=data)
        for model, expected in [('eistute', (5, 25, 15)), ('book', (4, 20, 108))]:
            case = output / model
            case.mkdir()
            source = ROOT / 'configs' / model / 'article.conf'
            text = source.read_text(encoding='utf-8')
            input_path = (ROOT / re.search(r'^INPUT_MODEL=(.+)$', text, re.M)[1].strip()).resolve()
            text = re.sub(r'^INPUT_MODEL=.*$', 'INPUT_MODEL=' + input_path.as_posix(), text, flags=re.M)
            text = re.sub(r'^OUTPUT_PREFIX=.*$', 'OUTPUT_PREFIX=' + (case / 'live' / model).as_posix(), text, flags=re.M)
            config = case / 'article.conf'
            config.write_text(text, encoding='utf-8', newline='\n')
            metadata = {'model': model, 'executable_sha256': report['executable_sha256'],
                        'source_config_sha256': digest(source), 'input_model': str(input_path),
                        'input_model_sha256': digest(input_path), 'relocated_keys': ['INPUT_MODEL', 'OUTPUT_PREFIX']}
            write(case / 'launch.json', dict(metadata, config_sha256=digest(config), cap_seconds=300))
            row, stdout, stderr = native(model, ['--adaptive-reuse-config', config, case], 300)
            row['input_metadata'] = metadata
            row['observation'] = inspect_reuse(stdout, stderr, row['exit'], expected[0])
            row['science'] = verify_pair(references[model], case, metadata, expected)
            if digest(source) != metadata['source_config_sha256'] or digest(input_path) != metadata['input_model_sha256']:
                raise ValueError('Scientific source/input identity changed during qualification')
            row['status'] = 'complete_reuse_qualified'
        if digest(executable) != report['executable_sha256']:
            raise ValueError('Executable identity changed during qualification')
        report['status'] = 'fixed_reuse_lifetime_qualified'
    except Exception as error:
        report.update(status='stopped_at_first_failure', failure=repr(error))
        raise
    finally:
        write(output / 'report.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reference-eistute', type=Path, required=True)
    parser.add_argument('--reference-book', type=Path, required=True)
    args = parser.parse_args()
    result = qualify(args.exe.resolve(), args.output.resolve(),
                     {'eistute': args.reference_eistute.resolve(), 'book': args.reference_book.resolve()})
    print(json.dumps({'status': result['status'], 'cases': len(result['cases'])}))
