#!/usr/bin/env python3
"""Compare nonempty initialized numeric/topology observations against original detached copies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

from audit_patch_copy import audit


def compare(original, candidate, original_root, candidate_root, runtime, output):
    output.mkdir(parents=True, exist_ok=False)
    preservation = audit(candidate_root, original_root)
    environment = dict(os.environ)
    environment['PATH'] = str(runtime.resolve())+os.pathsep+environment.get('PATH', '')
    environment['ASAN_OPTIONS'] = 'detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1'
    modes = [('base', [])] + [('bezier', [str(shape), str(mask)]) for shape in range(2) for mask in range(16)]
    modes += [('hermite', [str(shape)]) for shape in range(2)]
    report = {'status': 'running', 'preservation': preservation, 'cases': [], 'executables': {
        name: {'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        for name, path in [('original', original), ('candidate', candidate)]}}
    try:
        for mode, extra in modes:
            name = '-'.join([mode, *extra])
            observations, invocations = {}, {}
            for label, executable in [('original', original), ('candidate', candidate)]:
                process = subprocess.run([str(executable.resolve()), mode, *extra], env=environment,
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
                filename = label+'-'+name+'.log'
                (output/filename).write_bytes(process.stdout)
                invocations[label] = {'log': filename, 'exit_code': process.returncode,
                                      'sha256': hashlib.sha256(process.stdout).hexdigest()}
                assert process.returncode == 0 and b'ERROR: AddressSanitizer:' not in process.stdout
                observations[label] = [line for line in process.stdout.decode().splitlines() if line.startswith(
                    ('xyz=', 'evaluated_vectors=', 'base_id_only=', 'bezier shape=', 'hermite shape='))]
                assert observations[label]
                if mode != 'base':
                    assert len([line for line in observations[label] if line.startswith('xyz=')]) == 175
            assert observations['original'] == observations['candidate']
            report['cases'].append({'mode': name, 'invocations': invocations,
                                    'observation_count': len(observations['candidate']),
                                    'observations_sha256': hashlib.sha256('\n'.join(observations['candidate']).encode()).hexdigest()})
            (output/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
        assert len(report['cases']) == 35
        report.update(status='passed', paired_traces=35, paired_xyz_vectors=5950,
                      paired_scalar_values=17850, analytic_points_per_executable=850,
                      scope='Defined original/candidate detached ID/control/transformed-matrix/scratch, numeric '
                            'XYZ/derivative and incidence observations. Original omitted basis/metadata/direction '
                            'fields are never evaluated. Same-build pairs; no cross-compiler equality or complete clone.')
    except Exception as error:
        report.update(status='failed', error=str(error))
        (output/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
        raise
    (output/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['original', 'candidate', 'original-root', 'candidate-root', 'runtime', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    result = compare(args.original, args.candidate, args.original_root, args.candidate_root, args.runtime, args.output)
    print(json.dumps({key: value for key, value in result.items() if key not in {'cases', 'executables', 'preservation'}}))
