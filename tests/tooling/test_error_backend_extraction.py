"""Retain exact evaluator extraction across canonical signature wrapping."""

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from extract_error_estimate_backend import extract

ROOT = Path(__file__).resolve().parents[2]
BOUNDARY = "std::unique_ptr<Performer::IdManager> GeneratorAdaptive::MakeIdManager("
PREFIX = "GeneratorAdaptive::GeneratorAdaptive() {}\ndouble GeneratorAdaptive::ErrorGlobal(int x) {\n  return Nj;\n}\n"


class ErrorBackendExtractionTests(unittest.TestCase):
    def fixture(self, root, source):
        generator = root / "src/generator/generator_adaptive.cpp"
        charge = root / "src/estimate/charge_estimate_process.cpp"
        generator.parent.mkdir(parents=True)
        charge.parent.mkdir(parents=True)
        generator.write_text(source, encoding="utf-8")
        charge.write_text("ChargeEstimateProcess::ChargeEstimateProcess() {}\nChargeEstimateProcess::~ChargeEstimateProcess() {}", encoding="utf-8")

    def test_original_and_wrapped_signature_preserve_body(self):
        outputs = []
        for boundary in (BOUNDARY, BOUNDARY.replace("> Generator", ">\nGenerator")):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.fixture(root, PREFIX + boundary + ") {}")
                record = extract(root, root / "backend.cpp")
                outputs.append(((root / "backend.cpp").read_bytes(), record["evaluator_sha256"]))
        self.assertEqual(outputs[0], outputs[1])

    def test_missing_ambiguous_or_prior_boundary_rejected(self):
        for source in (PREFIX + BOUNDARY.replace("MakeIdManager", "Other"),
                       PREFIX + BOUNDARY + ") {}\n" + BOUNDARY + ") {}",
                       BOUNDARY + ") {}\n" + PREFIX):
            with self.subTest(source=source[-50:]), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.fixture(root, source)
                with self.assertRaises(AssertionError):
                    extract(root, root / "backend.cpp")

    def test_damaged_evaluator_end_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root, PREFIX.replace("return Nj;", "return 0;") + BOUNDARY + ") {}")
            with self.assertRaises(AssertionError):
                extract(root, root / "backend.cpp")

    def test_actual_source_keeps_explicit_scope(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "backend.cpp"
            record = extract(ROOT, output)
            text = output.read_text(encoding="utf-8")
            self.assertIn("double GeneratorAdaptive::ErrorGlobal(", text)
            self.assertNotIn("GeneratorAdaptive::MakeIdManager(", text)
            self.assertIn("not the full generator TU", record["scope"])


if __name__ == "__main__":
    unittest.main()
