"""Reject source drift and prove byte-reversible portable test interception."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from prepare_terminal_observer import prepare


class TerminalObserverPreparationTests(unittest.TestCase):
    def test_exact_source_and_fixture_reversal(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            result = prepare(ROOT, output)
            self.assertEqual([row["replacements"] for row in result["files"]], [2, 1])
            self.assertTrue(all(row["exact_byte_reversal"] for row in result["files"]))
            self.assertEqual(json.loads((output / "preparation.json").read_text()), result)
            generated = (output / "typed_domain_failure_fixture.h").read_bytes()
            original = (ROOT / "tests/typed_domain_failure_fixture.h").read_bytes()
            self.assertEqual(generated.replace(b'allocation_observer.h',
                                               b'domain_candidate_fixture.h'), original)

    def test_missing_or_extra_call_is_refused(self):
        for count in (1, 3):
            with self.subTest(count=count), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "src/adapter").mkdir(parents=True)
                (root / "src/adapter/adapter.cpp").write_text("avanco.execute(mesh_old)\n" * count)
                with self.assertRaises(ValueError):
                    prepare(root, root / "generated")

    def test_already_intercepted_source_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src/adapter").mkdir(parents=True)
            (root / "src/adapter/adapter.cpp").write_text(
                "avanco.execute(mesh_old)\n" * 2 + "terminal_observer::Execute(avanco, mesh_old)")
            with self.assertRaises(ValueError):
                prepare(root, root / "generated")

    def test_fixture_dependency_drift_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src/adapter").mkdir(parents=True)
            (root / "src/adapter/adapter.cpp").write_text("avanco.execute(mesh_old)\n" * 2)
            (root / "tests").mkdir()
            (root / "tests/typed_domain_failure_fixture.h").write_text("unexpected dependency")
            with self.assertRaises(ValueError):
                prepare(root, root / "generated")


if __name__ == "__main__":
    unittest.main()
