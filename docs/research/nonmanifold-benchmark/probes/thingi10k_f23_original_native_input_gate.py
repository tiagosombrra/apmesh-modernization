#!/usr/bin/env python3
"""Run the pinned original APMesh C++ BP validator on a private original-model candidate.

This does not instantiate Geometry, construct curves, or execute the mesher.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import resource
import shutil
import subprocess
import tempfile
import time

ORIGINAL_VALIDATION_HEADER_GIT_BLOB = 'bc7988e862383f2f264f9d3a2a7691fe5c028592'
ORIGINAL_WRAPPER_GIT_BLOB = 'b8bb3be6d1d28a3500a05c620c0be4bfef6b0989'
ORIGINAL_293137_BP_SHA256 = '6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0'
ORIGINAL_293137_BP_SIZE = 538482
EXPECTED_CONTROLS = 7886
EXPECTED_PATCHES = 876
SUCCESS_LINE = 'apmesh-original-bp-header-validation-pass\n'


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode('ascii') + data).hexdigest()


def file_sha256(path: Path) -> str:
    hash_ = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            hash_.update(chunk)
    return hash_.hexdigest()


def pinned_sources(root: Path) -> tuple[Path, Path]:
    header = root / 'include/input_output/input_validation.h'
    wrapper = root / 'docs/research/nonmanifold-benchmark/probes/thingi10k_f22_native_header_integration.cpp'
    require(header.is_file() and wrapper.is_file(), 'Original APMesh header/wrapper is missing')
    require(git_blob_sha1(header.read_bytes()) == ORIGINAL_VALIDATION_HEADER_GIT_BLOB,
            'Original APMesh header differs from the audited research revision')
    require(git_blob_sha1(wrapper.read_bytes()) == ORIGINAL_WRAPPER_GIT_BLOB,
            'Original F22 C++ wrapper differs from its pinned revision')
    return header, wrapper


def count_bp(path: Path) -> tuple[int, int]:
    vertices = patches = 0
    with path.open('r', encoding='utf-8') as handle:
        for line in handle:
            if line.startswith('v '):
                vertices += 1
            elif line.startswith('p '):
                patches += 1
            else:
                raise ValueError('Unexpected private BP record')
    return vertices, patches


def verify_private_bp(path: Path) -> dict:
    require(path.is_file() and path.stat().st_size == ORIGINAL_293137_BP_SIZE,
            'Original private candidate BP is missing or wrong-sized')
    sha = file_sha256(path)
    require(sha == ORIGINAL_293137_BP_SHA256, 'Original private candidate BP SHA-256 mismatch')
    controls, patches = count_bp(path)
    require(controls == EXPECTED_CONTROLS and patches == EXPECTED_PATCHES,
            'Original candidate BP model counts do not match F22')
    return {'bp_sha256': sha, 'bp_bytes': ORIGINAL_293137_BP_SIZE,
            'bp_controls': controls, 'bp_patches': patches}


def limit_child() -> None:
    # Limit only the C++ validator process, not the compiler.
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def execute(root: Path, candidate: Path, compiler: str, repetitions: int,
            timeout_seconds: float = 6.0) -> dict:
    header, wrapper = pinned_sources(root)
    candidate_data = verify_private_bp(candidate)
    require(1 <= repetitions <= 5, 'Repetition count must be between 1 and 5')
    require(0.5 <= timeout_seconds <= 30.0, 'Invalid per-run timeout')
    cxx = shutil.which(compiler)
    require(cxx is not None, 'No native C++17 compiler was found')
    with tempfile.TemporaryDirectory(prefix='apmesh-f23-native-') as temp:
        executable = Path(temp) / 'original_bp_validation'
        argv = [cxx, '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic',
                '-I' + str(root / 'include'), str(wrapper), '-o', str(executable)]
        compile_start = time.perf_counter()
        built = subprocess.run(argv, capture_output=True, text=True, timeout=60, check=False)
        compile_seconds = time.perf_counter() - compile_start
        require(built.returncode == 0 and executable.is_file(),
                'Native C++17 compilation failed: ' + built.stderr[-2500:])
        runs = []
        for _ in range(repetitions):
            run_start = time.perf_counter()
            ran = subprocess.run([str(executable), str(candidate)],
                                 capture_output=True, text=True, timeout=timeout_seconds,
                                 check=False, preexec_fn=limit_child)
            wall_seconds = time.perf_counter() - run_start
            require(ran.returncode == 0 and ran.stdout == SUCCESS_LINE and not ran.stderr,
                    'Original APMesh C++ header rejected the original private BP')
            runs.append({'exit_code': ran.returncode, 'stdout': ran.stdout.rstrip('\n'),
                         'wall_seconds': round(wall_seconds, 6)})
        return {
            'schema': 'apmesh-f23-original-native-header-only-v1',
            'model_id': 293137,
            'header_git_blob_sha1': git_blob_sha1(header.read_bytes()),
            'wrapper_git_blob_sha1': git_blob_sha1(wrapper.read_bytes()),
            'compiler': Path(cxx).name,
            'compiler_version': subprocess.run([cxx, '--version'], capture_output=True,
                                               text=True, timeout=5, check=True).stdout.splitlines()[0],
            'compile_flags': ['-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic'],
            'compile_seconds': round(compile_seconds, 6),
            'wall_clock_only': True,
            'max_address_space_mib': 256,
            'per_run_timeout_seconds': timeout_seconds,
            'runs': runs,
            **candidate_data,
            'original_cpp_input_validator_executed': True,
            'original_cpp_geometry_loader_executed': False,
            'original_cpp_shared_curves_observed': False,
            'original_cpp_tri_mesh_generated': False,
            'original_cpp_quad_mesh_generated': False,
            'redistribution_permission_verified': False,
            'scientific_reference_pair_admitted': False,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument('--private-bp', required=True, type=Path)
    parser.add_argument('--compiler', default='c++')
    parser.add_argument('--repeat', type=int, default=3)
    parser.add_argument('--output', required=True, type=Path)
    options = parser.parse_args()
    if options.output.exists():
        parser.error('Refusing to overwrite an existing F23 audit receipt')
    try:
        report = execute(options.repo_root, options.private_bp, options.compiler, options.repeat)
        with options.output.open('x', encoding='utf-8') as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write('\n')
        print(json.dumps({k: v for k, v in report.items() if k != 'runs'}, indent=2))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        parser.exit(2, f'F23 original C++ native-header audit failed: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
