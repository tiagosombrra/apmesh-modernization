#!/usr/bin/env python3
"""Check the exact pinned original C++17 BP validator against hermetic BP fixtures."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import thingi10k_f23_original_native_input_gate as gate


class OriginalHeaderNativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ.get('APMESH_F23_REPO_ROOT',
                        Path(__file__).resolve().parents[4]))
        gate.pinned_sources(cls.root)
        cls.tmp = tempfile.TemporaryDirectory(prefix='apmesh-f23-fixtures-')
        cls.output = Path(cls.tmp.name) / 'original_header'
        src = cls.root / 'docs/research/nonmanifold-benchmark/probes/thingi10k_f22_native_header_integration.cpp'
        built = subprocess.run(['c++', '-std=c++17', '-O2', '-Wall', '-Wextra',
                                '-pedantic', '-I' + str(cls.root / 'include'),
                                str(src), '-o', str(cls.output)],
                               capture_output=True, text=True, timeout=30)
        if built.returncode != 0:
            raise AssertionError('Original native header did not compile: ' + built.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self._counter = 0

    @staticmethod
    def controls():
        return ''.join(f'v {i} {i%3} {i%5}\n' for i in range(16))

    @staticmethod
    def patch():
        return 'p ' + ' '.join(map(str, range(16))) + '\n'

    @classmethod
    def canonical(cls):
        return cls.controls() + cls.patch()

    def run_source(self, source: str | None, should_pass: bool):
        self._counter += 1
        bp = Path(self.tmp.name) / f'candidate_{self.id().split(".")[-1]}_{self._counter}.bp'
        if source is not None:
            bp.write_text(source, encoding='utf-8')
        p = subprocess.run([str(self.output), str(bp)],
                           capture_output=True, text=True, timeout=5)
        if should_pass:
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(p.stdout, gate.SUCCESS_LINE)
            self.assertEqual(p.stderr, '')
        else:
            self.assertEqual(p.returncode, 2, p.stdout)
            self.assertIn('Native header validation failed:', p.stderr)
            self.assertEqual(p.stdout, '')

    def test_01_canonical_valid(self):
        self.run_source(self.canonical(), True)

    def test_02_comments_and_blank_lines_valid(self):
        self.run_source('# F23 synthetic valid\n\n' + self.canonical() + '// comment\n', True)

    def test_03_crlf_valid(self):
        self.run_source(self.canonical().replace('\n', '\r\n'), True)

    def test_04_repeated_patches_grammar_valid(self):
        self.run_source(self.canonical() + self.patch(), True)

    def test_05_one_vertex_reused_grammar_valid_but_not_geometry_proof(self):
        self.run_source('v 0 0 0\np ' + '0 '*15 + '0\n', True)

    def test_06_missing_file_rejected(self):
        self.run_source(None, False)

    def test_07_empty_file_rejected(self):
        self.run_source('', False)

    def test_08_only_vertices_rejected(self):
        self.run_source(self.controls(), False)

    def test_09_only_patches_rejected(self):
        self.run_source(self.patch(), False)

    def test_10_comment_only_rejected(self):
        self.run_source('# no geometry\n// no geometry\n', False)

    def test_11_indented_vertex_rejected(self):
        self.run_source('  '+self.canonical(), False)

    def test_12_indented_patch_rejected(self):
        self.run_source(self.controls()+'\t'+self.patch(), False)

    def test_13_invalid_record_rejected(self):
        self.run_source(self.canonical()+'x 1 2 3\n', False)

    def test_14_short_vertex_rejected(self):
        self.run_source('v 1 2\n'+self.canonical(), False)

    def test_15_vertex_nan_rejected(self):
        self.run_source('v nan 2 3\n'+self.canonical(), False)

    def test_16_vertex_inf_rejected(self):
        self.run_source('v inf 2 3\n'+self.canonical(), False)

    def test_17_short_patch_rejected(self):
        self.run_source(self.controls()+'p '+' '.join(map(str, range(15)))+'\n', False)

    def test_18_negative_index_rejected(self):
        self.run_source(self.controls()+'p '+' '.join(map(str, range(15)))+' -1\n', False)

    def test_19_index_out_of_range_rejected(self):
        self.run_source(self.controls()+'p '+' '.join(map(str, range(15)))+' 16\n', False)

    def test_20_extra_index_rejected(self):
        self.run_source(self.canonical().rstrip('\n')+' 0\n', False)

    def test_21_patch_before_controls_rejected(self):
        self.run_source(self.patch()+self.controls(), False)

    def test_22_vertex_extra_field_rejected(self):
        self.run_source(self.controls()+'v 1 2 3 4\n'+self.patch(), False)

    def test_23_patch_trailing_junk_rejected(self):
        self.run_source(self.canonical().rstrip('\n')+' nonsense\n', False)

    def test_24_vertex_trailing_junk_rejected(self):
        self.run_source(self.controls()+'v 1 2 3 nonsense\n'+self.patch(), False)

    def test_25_overflowing_patch_integer_rejected(self):
        self.run_source(self.controls()+'p '+' '.join(['0']*15 + ['9'*40])+'\n', False)

    def test_26_overflowing_vertex_float_rejected(self):
        self.run_source('v 1e9999 2 3\n'+self.canonical(), False)

    def test_27_header_git_blob_pinned(self):
        original, wrapper = gate.pinned_sources(self.root)
        self.assertEqual(gate.git_blob_sha1(original.read_bytes()),
                         gate.ORIGINAL_VALIDATION_HEADER_GIT_BLOB)
        self.assertEqual(gate.git_blob_sha1(wrapper.read_bytes()),
                         gate.ORIGINAL_WRAPPER_GIT_BLOB)

    def test_28_wrong_private_bp_size_refused(self):
        bp = Path(self.tmp.name) / 'wrong_private.bp'
        bp.write_text(self.canonical())
        with self.assertRaisesRegex(ValueError, 'missing or wrong-sized'):
            gate.verify_private_bp(bp)

    def test_29_private_bp_sha_binds_bytes(self):
        bp = Path(self.tmp.name) / 'right_sized_wrong_contents.bp'
        bp.write_bytes(b'x'*gate.ORIGINAL_293137_BP_SIZE)
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            gate.verify_private_bp(bp)

    def test_30_invalid_repetitions_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Repetition count'):
            # One valid candidate is needed before validating requested repetitions.
            # Fake this isolated argument boundary without reusing private geometry.
            original = gate.verify_private_bp
            try:
                gate.verify_private_bp = lambda _: {'bp_sha256': 'synthetic'}
                gate.execute(self.root, Path('/private-not-used'), 'c++', 0)
            finally:
                gate.verify_private_bp = original

    def test_31_modified_header_refused(self):
        modified = Path(self.tmp.name) / 'mutated_repo'
        h = modified / 'include/input_output/input_validation.h'
        w = modified / 'docs/research/nonmanifold-benchmark/probes/thingi10k_f22_native_header_integration.cpp'
        h.parent.mkdir(parents=True, exist_ok=True)
        w.parent.mkdir(parents=True, exist_ok=True)
        src_h, src_w = gate.pinned_sources(self.root)
        h.write_bytes(src_h.read_bytes() + b'\n')
        w.write_bytes(src_w.read_bytes())
        with self.assertRaisesRegex(ValueError, 'header differs'):
            gate.pinned_sources(modified)

    def test_32_modified_wrapper_refused(self):
        modified = Path(self.tmp.name) / 'mutated_wrapper_repo'
        h = modified / 'include/input_output/input_validation.h'
        w = modified / 'docs/research/nonmanifold-benchmark/probes/thingi10k_f22_native_header_integration.cpp'
        h.parent.mkdir(parents=True, exist_ok=True)
        w.parent.mkdir(parents=True, exist_ok=True)
        src_h, src_w = gate.pinned_sources(self.root)
        h.write_bytes(src_h.read_bytes())
        w.write_bytes(src_w.read_bytes()+b'\n')
        with self.assertRaisesRegex(ValueError, 'wrapper differs'):
            gate.pinned_sources(modified)


if __name__ == '__main__':
    unittest.main(verbosity=2)
