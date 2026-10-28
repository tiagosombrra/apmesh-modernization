"""Challenge angular ownership observations and fail-closed source preparation."""
from copy import deepcopy
import math
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
sys.path.insert(0, str(ROOT / 'tools'))
from front_angle_case import analyze
from prepare_front_angle_probe import prepare


def normal():
    return dict(layout=0, mode='0', profile='native-allocation-observer', geometry=0,
                entered=1, finished=1, attempts=2, denied=0, threw=0, found=1,
                selected_id=301, observed_id=301, constructed=2, released=2,
                release_order=[1, 2], values=[-0.5, -1, 0.5, -1, math.acos(0.6)],
                retained_blocks=0, retained_bytes=0)


class FrontAngleTests(unittest.TestCase):
    def rejected(self, **changes):
        data = normal()
        data.update(changes)
        with self.assertRaises(ValueError):
            analyze(data, 0, 0, 0, 2)

    def test_nonempty_normal(self):
        self.assertEqual(analyze(normal(), 0, 0, 0, 2)['clean_unwind_contract'], 'passed')

    def test_identity(self):
        for key, value in [('layout', 1), ('mode', '1'), ('selected_id', 302), ('observed_id', -1)]:
            self.rejected(**{key: value})

    def test_phase_and_entry(self):
        self.rejected(geometry=1)
        self.rejected(entered=0)

    def test_empty_allocation_coverage(self):
        for total in (0, 1, 3):
            with self.assertRaises(ValueError):
                analyze(normal(), 0, 0, 0, total)

    def test_lifetime_and_order(self):
        for changes in (dict(constructed=0), dict(released=1), dict(release_order=[2, 1])):
            self.rejected(**changes)

    def test_retention(self):
        self.rejected(retained_blocks=1, retained_bytes=80)

    def test_scalar_corruption(self):
        for values in ([0]*5, [float('nan')]*5, [float('inf')]*5, [-0.5, -1]):
            self.rejected(values=values)

    def test_profile_and_exit(self):
        self.rejected(profile='unmeasured')
        with self.assertRaises(ValueError):
            analyze(normal(), 1, 0, 0, 2)

    def test_denial_and_original_failure(self):
        d = normal()
        d.update(mode='2', finished=0, denied=1, threw=1, found=0, selected_id=-1,
                 observed_id=-1, constructed=1, released=1, release_order=[1, 0], values=[0]*5)
        self.assertEqual(analyze(d, 0, 0, 2, 2)['clean_unwind_contract'], 'passed')
        for changes in (dict(denied=0), dict(threw=0), dict(attempts=3), dict(found=1)):
            corrupt = deepcopy(d)
            corrupt.update(changes)
            with self.assertRaises(ValueError):
                analyze(corrupt, 0, 0, 2, 2)
        d.update(released=0, release_order=[0, 0], retained_blocks=1, retained_bytes=80)
        with self.assertRaises(ValueError):
            analyze(d, 1, 0, 2, 2)
        self.assertEqual(analyze(d, 1, 0, 2, 2, original=True)['clean_unwind_contract'], 'failed')

    def test_owned_observer_reversible(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            result = prepare(ROOT, folder / 'observed.cpp', folder / 'report.json')
            self.assertEqual(result['reversible_edits'], 4)
            self.assertTrue(result['owned_temporaries'])

    def test_raw_observer_reversible(self):
        text = ('#include "../../../include/crab_mesh/aft/advancing_front.h"\n'
                '    Vertex *v1 = new Vertex(1, 2);\n    Vertex *v2 = new Vertex(3, 4);\n'
                '    delete v1;\n    delete v2;\n')
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            source = folder / 'raw.cpp'
            source.write_text(text)
            result = prepare(ROOT, folder / 'observed.cpp', folder / 'report.json', source)
            self.assertFalse(result['owned_temporaries'])
            self.assertEqual(source.read_text(), text)

    def test_missing_or_duplicate_anchor(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            source = folder / 'bad.cpp'
            original = (ROOT / 'src/crab_mesh/aft/advancing_front.cpp').read_text()
            for text in (original + original, original.replace('v1.reset();', 'v1.release();')):
                source.write_text(text)
                with self.assertRaises(ValueError):
                    prepare(ROOT, folder / 'observed.cpp', folder / 'report.json', source)
                self.assertFalse((folder / 'observed.cpp').exists())


if __name__ == '__main__':
    unittest.main()
