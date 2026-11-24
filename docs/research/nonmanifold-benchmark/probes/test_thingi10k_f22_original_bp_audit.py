"""Hermetic input-negative and C++ boundary tests; real author mesh remains external."""
from __future__ import annotations
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from thingi10k_f22_original_bp_audit import read_bp, original_triangles
from thingi10k_f21_piecewise_linear_bezier import source_edges, build_patch_domain, serialize_bp

ROOT = Path(__file__).resolve().parent
CPP = ROOT / 'thingi10k_f22_independent_cpp_bp_probe.cpp'


def tetra_bp():
    vertices = [(0.,0.,0.), (1.,0.,0.), (0.,1.,0.), (0.,0.,1.)]
    faces = [(0,2,1), (0,1,3), (1,2,3), (2,0,3)]
    edges, _ = source_edges(vertices, faces)
    report, controls, patches = build_patch_domain(vertices, faces, edges)
    return serialize_bp(controls, patches), report


class InputContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)/'candidate.bp'
        self.content, self.report = tetra_bp()
        self.path.write_bytes(self.content)

    def parse(self, content=None):
        if content is not None:
            self.path.write_bytes(content)
        return read_bp(self.path, hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_01_tetrahedron_valid_bp(self):
        v,p=self.parse()
        self.assertEqual((len(v),len(p)),(110,12))
    def test_02_expected_euler(self):
        self.assertEqual(self.report['euler'],2)
        self.assertEqual(self.report['patch_edges'],24)
    def test_03_hash_tamper_rejected(self):
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            read_bp(self.path,'f'*64)
    def test_04_nonexistent_rejected(self):
        with self.assertRaisesRegex(ValueError,'Missing'):
            read_bp(Path(self.tmp.name)/'gone.bp','f'*64)
    def test_05_unknown_record_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unsupported'):
            self.parse(self.content + b'faces 1\n')
    def test_06_nonfinite_coordinate_rejected(self):
        with self.assertRaisesRegex(ValueError,'Nonfinite'):
            self.parse(self.content.replace(b'v 0 0 0',b'v nan 0 0',1))
    def test_07_negative_index_rejected(self):
        rows=self.content.decode().splitlines()
        pos=next(i for i,r in enumerate(rows) if r.startswith('p '))
        tokens=rows[pos].split();tokens[1]='-1';rows[pos]=' '.join(tokens)
        with self.assertRaisesRegex(ValueError,'Invalid indexed'):
            self.parse(('\n'.join(rows)+'\n').encode())
    def test_08_forward_index_rejected(self):
        rows=self.content.decode().splitlines()
        pos=next(i for i,r in enumerate(rows) if r.startswith('p '))
        tokens=rows[pos].split();tokens[-1]='9999999';rows[pos]=' '.join(tokens)
        with self.assertRaisesRegex(ValueError,'Invalid indexed'):
            self.parse(('\n'.join(rows)+'\n').encode())
    def test_09_short_patch_rejected(self):
        rows=self.content.decode().splitlines()
        pos=next(i for i,r in enumerate(rows) if r.startswith('p '))
        rows[pos]=' '.join(rows[pos].split()[:-1])
        with self.assertRaisesRegex(ValueError,'Wrong number'):
            self.parse(('\n'.join(rows)+'\n').encode())
    def test_10_extra_index_rejected(self):
        with self.assertRaisesRegex(ValueError,'Wrong number'):
            self.parse(self.content+b'p '+' '.join('0' for _ in range(17)).encode()+b'\n')
    def test_11_missing_original_zip_rejected(self):
        with self.assertRaisesRegex(ValueError,'Missing original'):
            original_triangles(Path(self.tmp.name)/'source.stl.zip')
    def test_12_wrong_original_zip_rejected(self):
        self.path.write_bytes(b'not original')
        with self.assertRaisesRegex(ValueError,'Missing original'):
            original_triangles(self.path)


@unittest.skipUnless(shutil.which('g++'), 'C++ compiler unavailable')
class IndependentCppContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.binary = Path(cls.tmp.name)/'probe'
        subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-pedantic',
                        str(CPP),'-o',str(cls.binary)],check=True,capture_output=True,text=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.tmpcase=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpcase.cleanup)
        self.case=Path(self.tmpcase.name)/'case.bp'
        self.bp,_=tetra_bp()

    def run_cpp(self, bp=None):
        self.case.write_bytes(self.bp if bp is None else bp)
        return subprocess.run([str(self.binary),str(self.case)],text=True,capture_output=True)

    def test_13_valid_tetra_cpp(self):
        r=self.run_cpp()
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('"paired_edges":24',r.stdout)
    def test_14_cpp_rejects_bad_index(self):
        r=self.run_cpp(self.bp+b'p 999999 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15\n')
        self.assertEqual(r.returncode,2)
    def test_15_cpp_rejects_orphan_boundary(self):
        rows=self.bp.splitlines()
        r=self.run_cpp(b'\n'.join(rows[:-1])+b'\n')
        self.assertEqual(r.returncode,2)
        self.assertIn('Unpaired',r.stderr)
    def test_16_cpp_rejects_modified_seam(self):
        rows=self.bp.decode().splitlines()
        p=next(i for i,x in enumerate(rows) if x.startswith('p '))
        toks=rows[p].split();toks[2]='0';rows[p]=' '.join(toks)
        r=self.run_cpp(('\n'.join(rows)+'\n').encode())
        self.assertEqual(r.returncode,2)
    def test_17_cpp_rejects_unbounded_data(self):
        r=self.run_cpp(b'v 0 0 0\nv 1 1 1\np 0 0 0\n')
        self.assertEqual(r.returncode,2)
    def test_18_cpp_rejects_missing_input(self):
        r=subprocess.run([str(self.binary),str(self.case)],capture_output=True,text=True)
        self.assertEqual(r.returncode,2)

if __name__=='__main__':
    unittest.main()
