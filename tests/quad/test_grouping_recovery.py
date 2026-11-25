"""Exercise process interruption on both sides of the grouping selection record."""

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

TOOLS = Path(__file__).resolve().parents[2] / "tools"
sys.path.insert(0, str(TOOLS))
import quad_grouping_trial as trial


class GroupingRecoveryTests(unittest.TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.out = Path(folder.name)
        original_curve = b"# source_site 0 original-interval\n"
        for path, data in (
            (trial.BASELINE, original_curve+b"# original specimen\n"),
            (trial.CANDIDATE, original_curve+b"# grouped specimen\n"),
            (trial.BASELINE_FRONT, b'{"leaves": [3, 4]}\n'),
            (trial.CANDIDATE_FRONT, b'{"leaves": [2]}\n'),
        ):
            target = self.out/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        self.selected = self.out/"selected.obj"
        self.prior = (self.out/trial.BASELINE).read_bytes()
        self.candidate = (self.out/trial.CANDIDATE).read_bytes()
        trial.finish(self.out, {"schema": trial.SCHEMA, "status": "baseline_ready",
            "baseline_sha256": trial.digest(self.out/trial.BASELINE),
            "baseline_front_sha256": trial.digest(self.out/trial.BASELINE_FRONT)}, trial.BASELINE)

    def interrupt(self, filename):
        child = """
import json, os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import quad_grouping_trial as runner
def stop_at(path, payload):
    if path.name == sys.argv[3]:
        os._exit(73)
    original_write(path, payload)
out = Path(sys.argv[2])
record = json.loads((out/"result.json").read_text(encoding="utf-8"))
record.update(status="eligible_candidate_selected", decision={"verdict": "eligible"},
              candidate_sha256=runner.digest(out/runner.CANDIDATE))
original_write = runner.write_bytes
runner.write_bytes = stop_at
runner.finish(out, record, runner.CANDIDATE)
"""
        result = subprocess.run([sys.executable, "-c", child, str(TOOLS), str(self.out), filename],
                                capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 73, result.stderr.decode(errors="replace"))

    def test_interruption_before_selection_commit_recovers_baseline(self):
        self.interrupt("result.json")
        self.selected.unlink()
        result = trial.recover(self.out)
        self.assertEqual(result["status"], "baseline_ready")
        self.assertEqual(self.selected.read_bytes(), self.prior)

    def test_interruption_after_selection_commit_recovers_candidate(self):
        self.interrupt("selected.obj")
        self.assertEqual(self.selected.read_bytes(), self.prior)
        result = trial.recover(self.out)
        self.assertEqual(result["status"], "eligible_candidate_selected")
        self.assertEqual(self.selected.read_bytes(), self.candidate)
        self.assertEqual(trial.recover(self.out), result)

    def test_tampered_mesh_or_front_does_not_replace_selected_obj(self):
        self.interrupt("selected.obj")
        for path in (trial.CANDIDATE, trial.CANDIDATE_FRONT, trial.BASELINE_FRONT):
            with self.subTest(path=path):
                item = self.out/path
                original = item.read_bytes()
                item.write_bytes(b"tampered\n")
                with self.assertRaisesRegex(ValueError, "recorded hash"):
                    trial.recover(self.out)
                self.assertEqual(self.selected.read_bytes(), self.prior)
                item.write_bytes(original)

    def test_unrecognized_selection_format_is_rejected(self):
        (self.out/"result.json").write_text('{"selected_source": "unknown"}', encoding="ascii")
        with self.assertRaisesRegex(ValueError, "Unsupported grouping selection record"):
            trial.recover(self.out)
        self.assertEqual(self.selected.read_bytes(), self.prior)


if __name__ == "__main__":
    unittest.main()
