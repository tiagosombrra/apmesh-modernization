#!/usr/bin/env python3
"""Check private-original input readiness without exporting original CAD bytes.

Nonzero exit means no native trial may run. It is not a native validation.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from hashlib import sha256

from s3z_s40_circular_seam_gate import ORIGINAL_STEP_SHA, S3W_PARENT_SHA


def check_readiness(step, bp, manifest, builder, *, extra_requirements=()):
    """Only return diagnostic checks and required hashes, never file contents."""
    paths = {'original_step': Path(step), 's3w_parent_bp': Path(bp),
             's3w_manifest': Path(manifest), 's3y_builder_py': Path(builder)}
    expected = {'original_step': ORIGINAL_STEP_SHA, 's3w_parent_bp': S3W_PARENT_SHA}
    checks = {}
    for label, p in paths.items():
        exists = p.is_file()
        check = {'found': exists, 'path': str(p)}
        if exists and label in expected:
            check['hash_ok'] = sha256(p.read_bytes()).hexdigest() == expected[label]
            check['expected_sha256'] = expected[label]
        if exists and label == 's3w_manifest':
            try:
                obj = json.loads(p.read_text(encoding='utf-8'))
                check['manifest_hash_ok'] = (
                    obj.get('repaired_bp_sha256') == S3W_PARENT_SHA and
                    obj.get('source_sha256') == ORIGINAL_STEP_SHA and
                    obj.get('combined_patches') == 148
                )
            except (OSError, UnicodeError, ValueError, TypeError):
                check['manifest_hash_ok'] = False
        checks[label] = check
    dependencies = ('cadquery', 'OCP', 'numpy', 'scipy', 'shapely') + tuple(extra_requirements)
    libs = {name: importlib.util.find_spec(name) is not None for name in dependencies}
    ready = all(v['found'] and v.get('hash_ok', True) and
                v.get('manifest_hash_ok', True) for v in checks.values()) and all(libs.values())
    return {
        'schema': 'apmesh-s3z2-original-s40-private-input-readiness-v1',
        'status': 'READY_FOR_ORIGINAL_NATIVE_TRIAL' if ready else 'BLOCKED_MISSING_OR_MISMATCHED_INPUT',
        'checks': checks, 'python_dependencies': libs,
        'native_trial_executed': False,
        'accepted_new_original_faces': 0,
    }


def main():
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument('--original-step', required=True, type=Path)
    arg.add_argument('--s3w-bp', required=True, type=Path)
    arg.add_argument('--s3w-manifest', required=True, type=Path)
    arg.add_argument('--s3y-builder', required=True, type=Path)
    arg.add_argument('--output', type=Path)
    opt = arg.parse_args()
    result = check_readiness(opt.original_step, opt.s3w_bp, opt.s3w_manifest,opt.s3y_builder)
    text = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if opt.output:
        opt.output.parent.mkdir(parents=True, exist_ok=True)
        opt.output.write_text(text, encoding='utf-8')
    print(text)
    return 0 if result['status'] == 'READY_FOR_ORIGINAL_NATIVE_TRIAL' else 3


if __name__ == '__main__':
    raise SystemExit(main())