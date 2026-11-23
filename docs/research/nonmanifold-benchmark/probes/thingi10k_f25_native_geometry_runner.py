#!/usr/bin/env python3
"""Build the original APMesh engine and measure its real Geometry from a private BP.

The original STL and derived BP are never copied into the repository, printed,
embedded in reports, or uploaded to CI artifacts. F25 does not execute TRI/QUAD.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import resource
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

REAL_BP_SHA256 = '6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0'
REAL_BP_SIZE = 538482
MODEL_COUNTS = (876, 1752, 0, 1752)
ROOT_FILES = (
    'CMakeLists.txt',
    'src/input_output/patch_reader.cpp',
    'src/input_output/control_patch_reader.cpp',
    'src/data/geometry.cpp',
    'src/data/point_adaptive.cpp',
    'include/data/geometry.h',
    'include/input_output/patch_reader.h',
)
PINNED_GIT_BLOBS = {
    'CMakeLists.txt': 'f44ced615dae35121da9d7c77652a4f37e393c47',
    'src/input_output/patch_reader.cpp': 'a00fa0c712ae31380e08e557be4d199abf5d40ea',
    'src/input_output/control_patch_reader.cpp': '30c0a28079165ed654c943e8be01737e98eeb5ad',
    'src/data/patch/patch_bezier.cpp': '828833ed50874141157d217e0a01ac345ee81a72',
    'src/data/patch/patch_coons.cpp': '0c7157facd94afbcdba0612271d1645b8f8ad969',
    'src/data/curve/curve_adaptive.cpp': '5d0ab4e099c95f67c5d86c992af4e441ae752325',
    'src/data/geometry.cpp': '411cff31f274f260eabf1d4e43e09e46c3c5a6a9',
    'src/data/point_adaptive.cpp': '92c77580d6778ee793c154d1f4f3dbe7e58ee34f',
}


def require(success: bool, message: str) -> None:
    if not success:
        raise ValueError(message)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def verify_checkout(root: Path) -> None:
    require(root.is_dir() and all((root / p).is_file() for p in ROOT_FILES),
            'Full original APMesh checkout is unavailable: no native Geometry claim')
    for path, expected in PINNED_GIT_BLOBS.items():
        require(git_blob(root / path) == expected,
                f'Native source drift in {path}; re-audit before running F25')


def verify_real_bp(path: Path) -> None:
    require(path.is_file() and path.stat().st_size == REAL_BP_SIZE,
            'Missing or wrong-sized original-model private BP')
    require(digest(path) == REAL_BP_SHA256, 'Original private BP SHA-256 changed')
    controls = patches = 0
    with path.open(encoding='utf-8') as f:
        for line in f:
            if line.startswith('v '):
                controls += 1
            elif line.startswith('p '):
                patches += 1
            else:
                raise ValueError('Private BP has a non-BP line')
    require((controls, patches) == (7886, 876), 'Original model record count changed')


def synthetic(path: Path, cases: int) -> tuple[int, int, int, int]:
    """Write independent planar bicubic squares; never use third-party coordinates."""
    require(cases in (1, 2), 'Only one or two synthetic patches are admitted')
    with path.open('x', encoding='utf-8') as f:
        for index in range(cases):
            start = 16 * index
            for j in range(4):
                for i in range(4):
                    f.write(f'v {index + i / 3:.17g} {j / 3:.17g} 0\n')
            f.write('p ' + ' '.join(str(start + i) for i in range(16)) + '\n')
    return (1, 4, 4, 0) if cases == 1 else (2, 7, 6, 1)


def reject_duplicate_fields(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        require(key not in result, 'Duplicated key in native evidence')
        result[key] = value
    return result


def parse_observation(raw: str, expected: tuple[int, int, int, int]) -> dict:
    lines = raw.splitlines()
    require(len(lines) == 1 and len(lines[0]) < 2000,
            'Unexpected output from original native probe')
    data = json.loads(lines[0], object_pairs_hook=reject_duplicate_fields,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
    require(type(data) is dict and data.get('schema') == 'apmesh-s40-f25-native-geometry-v1'
            and data.get('result') == 'PASS', 'Missing native proof schema')
    fields = ('patches', 'curves', 'boundary', 'shared')
    actual = tuple(data.get(name) for name in fields)
    require(all(type(v) is int and v >= 0 for v in actual), 'Invalid native curve counts')
    require(actual == expected and data.get('nonmanifold') == 0
            and data.get('sides') == 4 * expected[0],
            'Native patch/curve/observer counts do not match input')
    for field in ('load_ms', 'verify_ms'):
        value = data.get(field)
        require(type(value) in (int, float) and math.isfinite(value) and value >= 0,
                'Missing/nonfinite native timing')
    require(type(data.get('peak_rss_kib')) is int and data['peak_rss_kib'] > 0,
            'Missing native RSS observation')
    return data


def native_limits() -> None:
    # Apply CPU and virtual-memory caps only to the isolated native probe.
    cap_bytes = 2 * 1024 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (cap_bytes, cap_bytes))
    resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def run(command: list[str], *, timeout: int, cwd: Path | None = None,
        hide: bool = False, native: bool = False) -> tuple[subprocess.CompletedProcess, float]:
    start = time.monotonic()
    result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout, check=False,
                            preexec_fn=native_limits if native else None)
    elapsed = time.monotonic() - start
    if result.returncode:
        raise ValueError(f'F25 command failed: {command[0]} (exit={result.returncode}); '
                         f'no native result admitted; diagnostic={result.stderr[-1000:]}')
    if not hide:
        print(f'F25 stage {Path(command[0]).name}: PASS, elapsed {elapsed:.3f}s')
    return result, elapsed


def measure(root: Path, probe: Path, *, bp: Path | None,
            build_timeout: int = 900, native_timeout: int = 120) -> dict:
    verify_checkout(root)
    require(probe.is_file(), 'F25 original-native probe source absent')
    if bp is not None:
        verify_real_bp(bp)
    with tempfile.TemporaryDirectory(prefix='apmesh-f25-') as tmp:
        directory = Path(tmp)
        build = directory / 'build'
        configure = ['cmake', '-S', str(root), '-B', str(build),
                     '-DCMAKE_BUILD_TYPE=Release', '-DBUILD_TESTING=OFF',
                     '-DAP_MESH_USE_MPI=OFF', '-DAP_MESH_USE_OPENMP=OFF',
                     '-DAP_MESH_ENABLE_LTO=OFF']
        run(configure, timeout=90)
        _, build_seconds = run(['cmake', '--build', str(build), '--target',
                                'ap_mesh_engine', '-j', '2'], timeout=build_timeout)
        lib = build / 'libap_mesh_engine.a'
        require(lib.is_file() and lib.stat().st_size > 0,
                'Original compiled engine library is absent')
        executable = directory / 'native-geometry-probe'
        run(['c++', '-std=c++17', '-O2', '-I', str(root / 'include'),
             str(probe), str(lib), '-pthread', '-o', str(executable)], timeout=100)
        result_rows = []
        fixtures = []
        for count in (1, 2):
            fixture = directory / f'synthetic-{count}.bp'
            expected = synthetic(fixture, count)
            fixtures.append((f'synthetic-{count}', fixture, expected))
        if bp is not None:
            fixtures.append(('real-293137', bp, MODEL_COUNTS))
        for label, path, expected in fixtures:
            checks = []
            for _ in range(2):
                observed, wall = run([str(executable), str(path), *(str(x) for x in expected)],
                                      timeout=native_timeout, hide=True, native=True)
                data = parse_observation(observed.stdout, expected)
                checks.append({'load_ms': data['load_ms'],
                               'verify_ms': data['verify_ms'],
                               'peak_rss_kib': data['peak_rss_kib'],
                               'process_wall_ms': wall * 1000})
            result_rows.append({'case': label, 'expected_counts': dict(zip(
                ('patches', 'curves', 'boundary', 'shared'), expected)),
                                'repetitions': checks})
        return {'schema': 'apmesh-s40-f25-native-geometry-receipt-v1',
                'status': 'ORIGINAL_APMESH_NATIVE_GEOMETRY_EXECUTED',
                'build_seconds': round(build_seconds, 3),
                'production_source_git_blobs': PINNED_GIT_BLOBS,
                'private_real_293137_executed': bp is not None,
                'apmesh_tri_or_quad_mesher_executed': False,
                'cases': result_rows}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--probe', type=Path, default=Path(__file__).with_name(
        'thingi10k_f25_native_geometry_probe.cpp'))
    p.add_argument('--private-bp', type=Path)
    p.add_argument('--receipt', type=Path, required=True)
    args = p.parse_args()
    require(not args.receipt.exists(), 'Receipt exists; refusing overwrite')
    report = measure(args.root.resolve(), args.probe.resolve(),
                     bp=args.private_bp.resolve() if args.private_bp else None)
    with args.receipt.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'status': report['status'], 'cases': len(report['cases']),
                      'private_real_293137_executed': report['private_real_293137_executed']}))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        raise SystemExit(f'F25 blocked/failed: {exc}') from exc
