"""Require failed calibration to preserve raw output and prevent directed launches."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import qualify_terminal_crt_lifetime as runner


class TerminalCrtLifetimeTests(unittest.TestCase):
    def test_fixed_inventory_rejects_missing_duplicate_changed_contexts_and_caps(self):
        ledger = json.loads((ROOT / "docs/evidence/stage3/serial_execution/ledger.json").read_text())
        self.assertEqual(len(runner.fixed_contexts(ledger)), 2)
        for mutation in ("missing", "duplicate", "context", "cap"):
            changed = json.loads(json.dumps(ledger))
            groups = [case for case in changed["cases"] if case["id"] in ("SP-09", "SP-10")]
            if mutation == "missing":
                changed["cases"].remove(groups[0])
            elif mutation == "duplicate":
                changed["cases"].append(groups[0])
            elif mutation == "context":
                groups[0]["contexts"][0]["patch"] = 1
            else:
                groups[0]["timeout_seconds_each"] = 301
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                runner.fixed_contexts(changed)

    def run_failed_calibration(self, failure):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            executable = folder / "probe.exe"
            executable.write_bytes(b"isolated runner fixture")
            output = folder / "observation"
            launches = []

            def launch(command, **kwargs):
                launches.append(command)
                kwargs["stdout"].write(b"retained native prefix\r\n")
                kwargs["stderr"].write(b"abort() has been called\r\n")
                if failure == "timeout":
                    raise subprocess.TimeoutExpired(command, 10)
                return subprocess.CompletedProcess(command, 3)

            with patch.object(sys, "argv", ["runner", "--exe", str(executable), "--output", str(output)]), \
                    patch.object(runner.subprocess, "run", side_effect=launch), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(runner.main(), 1)
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(report["status"], "stopped_at_first_unexpected_failure")
            self.assertEqual(len(launches), 1)
            self.assertEqual(report["cases"], [])
            self.assertEqual(report["controls"][0]["status"], "failed")
            self.assertEqual((output / "lifetime-release/stdout.log").read_bytes(),
                             b"retained native prefix\r\n")
            self.assertEqual((output / "lifetime-release/stderr.log").read_bytes(),
                             b"abort() has been called\r\n")
            self.assertIn("lifetime-release/stderr.log", report["artifacts"])
            if failure != "timeout":
                self.assertEqual(report["controls"][0]["exit_code"], 3)

    def test_aborted_calibration_cannot_start_directed_contexts(self):
        self.run_failed_calibration("abort")

    def test_timeout_cannot_start_later_controls_or_directed_contexts(self):
        self.run_failed_calibration("timeout")


if __name__ == "__main__":
    unittest.main()
