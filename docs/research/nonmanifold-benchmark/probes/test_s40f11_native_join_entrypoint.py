"""Hermetic F9 CLI tests: no original STEP files or CAD model are used."""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from test_s40f11_atomic_candidate_delivery import valid_report
from s40f11_atomic_candidate_delivery import BP_NAME, RECEIPT_NAME


def load_entrypoint_without_private_dependencies():
    """Load the real CLI source while replacing irrelevant native modules."""
    stubs = {name: types.ModuleType(name) for name in (
        "s40f7_parent_lineage_rebase", "s40f9_independent_certificate",
        "s40f9_regularized_source_island",
    )}
    source = Path(__file__).with_name("s40f9_native_join_gate.py")
    with patch.dict(sys.modules, stubs):
        spec = importlib.util.spec_from_file_location("s40f9_native_join_gate_f11_test", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


def cli_args(output_path: Path):
    """Provide placeholder inputs; all private native imports are mocked."""
    parameters = (
        "original-step", "s3y-bp", "original-f6-bp", "original-f6-manifest",
        "f9-bp", "f9-manifest", "original-f5-spec", "original-f6-spec",
    )
    args = ["s40f9_native_join_gate.py"]
    for key in parameters:
        args += ["--" + key, "/nonexistent/private-" + key]
    args += ["--output-dir", str(output_path)]
    return args


class NativeJoinEntrypointTests(unittest.TestCase):
    def test_preexisting_candidate_blocks_before_private_import(self):
        mod = load_entrypoint_without_private_dependencies()
        with TemporaryDirectory() as root:
            dest = Path(root) / "candidate"
            dest.mkdir()
            (dest / BP_NAME).write_text("existing run\n")
            err = io.StringIO()
            with patch.object(mod, "private_f9_native_trial", side_effect=AssertionError("must never run")) as private:
                with patch.object(sys, "argv", cli_args(dest)), redirect_stderr(err):
                    self.assertEqual(mod.main(), 3)
                private.assert_not_called()
            message = json.loads(err.getvalue())
            self.assertTrue(message["output_destination_preexisting"])
            self.assertFalse(message["new_candidate_emitted_this_run"])
            self.assertEqual((dest / BP_NAME).read_text(), "existing run\n")

    def test_missing_original_private_input_does_not_emit_candidate(self):
        mod = load_entrypoint_without_private_dependencies()
        with TemporaryDirectory() as root:
            dest = Path(root) / "candidate"
            err = io.StringIO()
            with patch.object(mod, "private_f9_native_trial", side_effect=FileNotFoundError("private STEP missing")):
                with patch.object(sys, "argv", cli_args(dest)), redirect_stderr(err):
                    self.assertEqual(mod.main(), 3)
            message = json.loads(err.getvalue())
            self.assertFalse(message["output_destination_preexisting"])
            self.assertEqual(message["new_source_faces_admitted"], 0)
            self.assertFalse(dest.exists())

    def test_successful_synthetic_flow_labels_candidate_not_admission(self):
        mod = load_entrypoint_without_private_dependencies()
        with TemporaryDirectory() as root:
            dest = Path(root) / "candidate"
            bp = "// synthetic candidate\n"
            out = io.StringIO()
            with patch.object(mod, "private_f9_native_trial", return_value=(bp, valid_report(bp))):
                with patch.object(sys, "argv", cli_args(dest)), redirect_stdout(out):
                    self.assertEqual(mod.main(), 0)
            message = json.loads(out.getvalue())
            self.assertEqual(message["candidate_original_source_faces"], 26)
            self.assertEqual(message["new_source_faces_homologated"], 0)
            self.assertFalse(message["apmesh_cpp_tri_quad_executed"])
            self.assertEqual((dest / BP_NAME).read_text(), bp)
            self.assertTrue((dest / RECEIPT_NAME).exists())


if __name__ == "__main__":
    unittest.main()
