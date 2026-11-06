import sys
import json
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from qualify_serial_crt_static import (
    analyze_existing, attribute, digest, inspect_trace, qualify_control, require_captured_artifact,
)


def logs(release_phase=None):
    stdout = "STATIC_CRT app_exit=0 heap_valid=1 iterator_level=2 denied=0 errors=0\n"
    stderr = (
        "CRT_WATCH request=73 bytes=64\n"
        "CRT_FRAME kind=allocation request=73 rva=0x123 module=probe.exe\n"
        "STATIC_CRT_DUMP_BEGIN\nDumping objects ->\n"
        "{73} normal block at 0x1234, 64 bytes long.\n Data: < > CD CD\n"
        "Object dump complete.\nSTATIC_CRT_DUMP_END\n"
        "CRT_STATE name=entry_return phase=1 blocks=1 bytes=64 errors=0 reallocations=0\n")
    for phase, name in ((3, "after_lazy_statics"), (4, "after_executable_statics")):
        if release_phase == phase - 1:
            stderr += (f"CRT_FREE request=73 phase={release_phase} bytes=64\n"
                       "CRT_FRAME kind=release request=73 rva=0x456 module=probe.exe\n")
        remaining = release_phase is None or release_phase >= phase
        stderr += (f"CRT_STATE name={name} phase={phase} blocks={int(remaining)} "
                   f"bytes={64 * remaining} errors=0 reallocations=0\n")
    if release_phase == 4:
        stderr += ("CRT_FREE request=73 phase=4 bytes=64\n"
                   "CRT_FRAME kind=release request=73 rva=0x456 module=runtime.dll\n")
    return stdout, stderr


class StaticTeardownControls(unittest.TestCase):
    def test_executable_static_release_is_distinguished_from_entry_retention(self):
        trace = inspect_trace(*logs(3), 0)
        qualify_control("static-release-control", trace)
        self.assertTrue(trace["released_all_observed_requests"])

    def test_deliberate_leak_remains_unqualified_after_exit(self):
        trace = inspect_trace(*logs(), 0)
        qualify_control("static-leak-control", trace)
        self.assertFalse(trace["released_all_observed_requests"])
        with self.assertRaises(ValueError):
            qualify_control("static-release-control", trace)

    def test_runtime_release_can_follow_executable_statics(self):
        trace = inspect_trace(*logs(4), 0)
        self.assertEqual(trace["states"][-1]["blocks"], 1)
        self.assertTrue(trace["released_all_observed_requests"])

    def test_unknown_request_or_different_size_is_not_release_evidence(self):
        out, err = logs(3)
        for replacement in ("CRT_FREE request=74 phase=3 bytes=64", "CRT_FREE request=73 phase=3 bytes=63"):
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                inspect_trace(out, err.replace("CRT_FREE request=73 phase=3 bytes=64", replacement), 0)

    def test_heap_or_observer_failure_is_not_clean(self):
        out, err = logs(3)
        for replacement in (out.replace("heap_valid=1", "heap_valid=0"), out.replace("errors=0", "errors=1")):
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                inspect_trace(replacement, err, 0)

    def test_net_difference_cannot_replace_independent_dump(self):
        out, err = logs(3)
        for replacement in (err.replace("{73}", "{74}"), err.replace("64 bytes long", "63 bytes long"),
                            err.replace("STATIC_CRT_DUMP_END", "TRUNCATED")):
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                inspect_trace(out, replacement, 0)

    def test_missing_or_duplicate_boundary_does_not_qualify(self):
        out, err = logs(3)
        state = "CRT_STATE name=after_executable_statics phase=4 blocks=0 bytes=0 errors=0 reallocations=0\n"
        for replacement in (err.replace(state, ""), err + state):
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                inspect_trace(out, replacement, 0)

    def test_incomplete_stack_or_reallocation_blocks_attribution(self):
        out, err = logs(3)
        for replacement in (err.replace("CRT_FRAME kind=release", "MISSING_FRAME"),
                            err.replace("CRT_FRAME kind=allocation", "MISSING_FRAME"),
                            err.replace("reallocations=0", "reallocations=1")):
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                inspect_trace(out, replacement, 0)

    def test_ptr_aux_requires_its_actual_static_destructor(self):
        out, err = logs(3)
        trace = inspect_trace(out, err.replace("64", "8"), 0)
        symbols = {"probe.exe": {
            "0x123": [{"FunctionName": "std::vector<class CurveAdaptiveParametric *>::resize"}],
            "0x456": [{"FunctionName": "dynamic atexit destructor for 'ptr_aux'"}],
        }}
        self.assertEqual(attribute(trace, symbols)["groups"], {"ptr_aux_storage": {"blocks": 1, "bytes": 8}})
        symbols["probe.exe"]["0x456"] = [{"FunctionName": "unrelated static destructor"}]
        self.assertIn("unattributed", attribute(trace, symbols)["groups"])

    def test_unavailable_external_symbols_are_explicitly_retained(self):
        trace = inspect_trace(*logs(3), 0)
        result = attribute(trace, {})
        self.assertEqual(result["requests"][0]["owner"], "unattributed")
        self.assertEqual(result["requests"][0]["allocation_stack"][0]["symbol_status"],
                         "unresolved_external_frame")

    def test_registered_symbol_artifact_is_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            symbols = folder / "captured-symbols.json"
            symbols.write_text("[]", encoding="utf-8")
            require_captured_artifact(folder, {symbols.name: digest(symbols)}, symbols)

    def test_replaced_registered_symbol_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            symbols = folder / "captured-symbols.json"
            symbols.write_text("[]", encoding="utf-8")
            artifacts = {symbols.name: digest(symbols)}
            symbols.write_text('[{"ModuleName":"same-executable.exe","Symbol":"forged"}]', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "registered captured artifact"):
                require_captured_artifact(folder, artifacts, symbols)

    def test_external_symbol_file_is_rejected_even_with_identical_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / "capture"
            folder.mkdir()
            symbols = folder / "captured-symbols.json"
            symbols.write_text("[]", encoding="utf-8")
            external = root / symbols.name
            external.write_bytes(symbols.read_bytes())
            with self.assertRaisesRegex(ValueError, "captured artifact directory"):
                require_captured_artifact(folder, {symbols.name: digest(symbols)}, external)

    def test_analysis_rejects_unregistered_symbols_before_using_their_module_names(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            registered = folder / "captured-symbols.json"
            registered.write_text("[]", encoding="utf-8")
            substituted = folder / "substituted-symbols.json"
            substituted.write_text('[{"ModuleName":"same-executable.exe"}]', encoding="utf-8")
            report = folder / "report.json"
            report.write_text(json.dumps({"artifacts": {registered.name: digest(registered)}}), encoding="utf-8")
            result = folder / "attribution.json"
            with self.assertRaisesRegex(ValueError, "registered captured artifact"):
                analyze_existing(report, substituted, result)
            self.assertFalse(result.exists())


if __name__ == "__main__":
    unittest.main()
