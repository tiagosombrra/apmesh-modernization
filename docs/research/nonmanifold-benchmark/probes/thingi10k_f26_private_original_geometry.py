#!/usr/bin/env python3
"""Execute the exact author-data-derived BP with a hash-bound original APMesh probe.

The input STL/BP is third-party-derived and never copied into a public report.
The native binary must be built from the full original APMesh engine, outside
this workstation, and transferred as a code-only GitHub Actions artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import time

ORIGINAL_BP_SHA256 = '6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0'
ORIGINAL_BP_BYTES = 538482
EXPECTED_BP_CONTROLS = 7886
EXPECTED_PATCHES = 876
EXPECTED_CURVES = 1752
EXPECTED_SHARED = 1752
EXPECTED_BOUNDARY = 0
EXPECTED_SIDES = 3504
OBSERVATION_SCHEMA = 'apmesh-s40-f25-native-geometry-v1'
REPORT_SCHEMA = 'apmesh-s40-f26-original-private-native-geometry-v1'
SOURCE_GITHUB = 'tiagosombrra/apmesh-modernization'
SOURCE_COMMIT = '73e46748c294af0f390a907a11445645e279fc12'


def require(ok: bool, explanation: str) -> None:
    if not ok:
        raise ValueError(explanation)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify_private_bp(bp: Path) -> None:
    require(bp.is_file() and bp.stat().st_size == ORIGINAL_BP_BYTES,
            'Missing or resized original-model private BP')
    require(sha256(bp) == ORIGINAL_BP_SHA256,
            'Private BP digest differs from F22 reproducible original candidate')
    controls = patches = 0
    with bp.open('r', encoding='utf-8') as contents:
        for row in contents:
            if row.startswith('v '):
                controls += 1
            elif row.startswith('p '):
                patches += 1
            else:
                raise ValueError('Unexpected original-model BP record')
    require((controls, patches) == (EXPECTED_BP_CONTROLS, EXPECTED_PATCHES),
            'Original-model BP vertex/patch records changed')


def unique_pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, 'Duplicate native JSON field')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('Nonfinite JSON constant: ' + value)


def verify_native_observation(text: str) -> dict:
    rows = text.splitlines()
    require(len(rows) == 1 and len(rows[0]) <= 3000,
            'Native probe did not produce one bounded JSON record')
    receipt = json.loads(rows[0], object_pairs_hook=unique_pairs,
                         parse_constant=reject_constant)
    require(type(receipt) is dict and receipt.get('schema') == OBSERVATION_SCHEMA
            and receipt.get('result') == 'PASS', 'Original native result did not PASS')
    expected = {
        'patches': EXPECTED_PATCHES,
        'curves': EXPECTED_CURVES,
        'boundary': EXPECTED_BOUNDARY,
        'shared': EXPECTED_SHARED,
        'nonmanifold': 0,
        'sides': EXPECTED_SIDES,
        'matched_control_sides': EXPECTED_SIDES,
    }
    for field, value in expected.items():
        require(type(receipt.get(field)) is int and receipt[field] == value,
                'Native engine geometry/curve mismatch: ' + field)
    reversed_sides = receipt.get('reversed_control_sides')
    require(type(reversed_sides) is int and 0 <= reversed_sides <= EXPECTED_SIDES,
            'Invalid native control orientation count')
    for key in ('parse_ms', 'load_ms', 'verify_ms'):
        value = receipt.get(key)
        require(type(value) in (int, float) and math.isfinite(value) and value >= 0,
                'Native time measurement missing/nonfinite: ' + key)
    require(type(receipt.get('peak_rss_kib')) is int and receipt['peak_rss_kib'] > 0,
            'Native peak RSS measurement is missing')
    return receipt


def limit_child() -> None:
    # Limit the isolated engine binary, never the Python driver or compiler.
    max_memory = 2 * 1024 ** 3
    resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))
    resource.setrlimit(resource.RLIMIT_CPU, (180, 180))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def private_run(binary: Path, bp: Path, expected_binary_sha256: str,
                *, runs: int = 2, timeout_seconds: int = 240) -> dict:
    require(os.name == 'posix', 'Native replay is supported on Linux/POSIX only')
    require(binary.is_file() and binary.stat().st_size > 1000,
            'Missing original-engine native executable')
    require(len(expected_binary_sha256) == 64 and
            all(c in '0123456789abcdef' for c in expected_binary_sha256),
            'Malformed original binary SHA-256')
    require(sha256(binary) == expected_binary_sha256,
            'Native executable digest differs from authenticated GitHub artifact')
    verify_private_bp(bp)
    require(runs == 2, 'Evidence requires exactly two independent native processes')
    args = [str(binary.resolve()), str(bp.resolve()), str(EXPECTED_PATCHES),
            str(EXPECTED_CURVES), str(EXPECTED_BOUNDARY), str(EXPECTED_SHARED)]
    observations = []
    for index in range(runs):
        started = time.monotonic()
        proc = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=timeout_seconds,
                              check=False, preexec_fn=limit_child)
        wall = (time.monotonic() - started) * 1000
        require(proc.returncode == 0,
                'Native original engine process failed, exit=' + str(proc.returncode)
                + '; diagnostic=' + proc.stderr[-250:])
        parsed = verify_native_observation(proc.stdout)
        require(not proc.stderr.strip(), 'Native engine emitted unexpected diagnostic')
        observations.append({
            'run': index + 1,
            'parse_ms': parsed['parse_ms'],
            'load_ms': parsed['load_ms'],
            'verify_ms': parsed['verify_ms'],
            'peak_rss_kib': parsed['peak_rss_kib'],
            'reversed_control_sides': parsed['reversed_control_sides'],
            'process_wall_ms': round(wall, 3),
        })
    require(sha256(bp) == ORIGINAL_BP_SHA256,
            'Private BP changed during native execution')
    require(observations[0]['reversed_control_sides'] ==
            observations[1]['reversed_control_sides'],
            'Native original curve orientation count differs across runs')
    return {
        'schema': REPORT_SCHEMA,
        'status': 'ORIGINAL_APMESH_NATIVE_GEOMETRY_REAL_293137_EXECUTED',
        'source_repo': SOURCE_GITHUB,
        'source_commit_with_binary_workflow': SOURCE_COMMIT,
        'original_private_bp_sha256': ORIGINAL_BP_SHA256,
        'original_private_bp_bytes': ORIGINAL_BP_BYTES,
        'native_binary_sha256': expected_binary_sha256,
        'patches': EXPECTED_PATCHES,
        'curves': EXPECTED_CURVES,
        'boundary_curves': EXPECTED_BOUNDARY,
        'shared_curves': EXPECTED_SHARED,
        'patch_side_incidence': EXPECTED_SIDES,
        'matched_control_sides': EXPECTED_SIDES,
        'real_native_reader_file_patches_executed': True,
        'real_native_geometry_observer_identity_verified': True,
        'tri_mesher_executed': False,
        'quad_mesher_executed': False,
        'scientific_apmesh_reference_pair_admitted': False,
        'private_original_or_derived_geometry_published': False,
        'runs': observations,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native-executable', type=Path, required=True)
    p.add_argument('--private-bp', type=Path, required=True)
    p.add_argument('--native-sha256', type=str, required=True)
    p.add_argument('--report', type=Path, required=True)
    args = p.parse_args(argv)
    require(not args.report.exists(), 'Existing report may not be overwritten')
    report = private_run(args.native_executable, args.private_bp, args.native_sha256)
    with args.report.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps({
        'status': report['status'],
        'runs': len(report['runs']),
        'curves': report['curves'],
        'shared_curves': report['shared_curves'],
        'tri_mesher_executed': False,
    }))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        raise SystemExit('F26 blocked/failed: ' + str(exc)) from exc
