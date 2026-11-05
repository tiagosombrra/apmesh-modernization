"""Reject recording relocation and helper changes without relaxing historical guards."""

import importlib
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from audit_find_uv_recording import compact, restore_find_uv_recording, validate_find_uv_header
from audit_find_uv_scratch import restore_find_uv_scratch


def candidate(kind="Bezier"):
    return (
        '#include "data/patch/find_uv_statistics.h"\nextern unsigned int I_MAX;\n'
        f'tuple<double, double> Patch{kind}::FindUV(const PointAdaptive& point) {{'
        'apmesh::diagnostics::RecordFindUvCall();'
        'double delta = 0.65;'
        'if (iter >= I_MAX) { const unsigned long long hit = '
        'apmesh::diagnostics::RecordFindUvImaxExit(); } return {delta, delta}; }')


class FindUvRecordingTests(unittest.TestCase):
    def test_scratch_roundtrip_and_rejected_solver_mutations(self):
        name = "src/data/patch/patch_bezier.cpp"
        baseline = subprocess.check_output(
            ["git", "show", f"836df73fb973971b73c021f288a00966aed65e6d:{name}"], cwd=ROOT).decode()
        source = (ROOT / name).read_text(encoding="utf-8")
        self.assertEqual(compact(restore_find_uv_scratch(source)), compact(baseline))
        self.assertEqual(restore_find_uv_scratch(baseline), baseline)
        mutations = [
            ("matrix[1][1]", "matrix[2][1]"),
            ("matrix[k].swap(matrix[0])", "matrix[k].swap(matrix[1])"),
            ("matrix[2][j] - A_20", "matrix[2][j] + A_20"),
            ("fabs(pivot) < TOLERANCE", "fabs(pivot) <= TOLERANCE"),
            ("iter >= I_MAX", "iter > I_MAX"),
            ("matrix[0][0]", "matrix(0, 0)"),
            ("RecordFindUvCall();", "RecordFindUvCall();RecordFindUvCall();"),
        ]
        for before, after in mutations:
            self.assertIn(before, source)
            with self.subTest(mutation=before), self.assertRaises(ValueError):
                restore_find_uv_scratch(source.replace(before, after, 1))

    def test_historical_guards_reject_scratch_and_external_policy_mutations(self):
        name = "src/data/patch/patch_bezier.cpp"
        for module_name in ("audit_patch_copy", "audit_bezier_observers"):
            module = importlib.import_module(module_name)
            originals = {file: subprocess.check_output(
                ["git", "show", f"{module.BASE}:{file}"], cwd=ROOT).decode() for file in module.FILES}
            candidates = {file: (ROOT / file).read_text(encoding="utf-8") for file in module.FILES}
            module.verify(originals, candidates)
            for before, after in (("matrix[k].swap(matrix[0])", "matrix[k].swap(matrix[1])"),
                                  ("kFindUvDamping = 0.65", "kFindUvDamping = 0.66"),
                                  ("kFindUvParamTol = 1e-5", "kFindUvParamTol = 1e-4")):
                self.assertIn(before, candidates[name])
                changed = dict(candidates)
                changed[name] = changed[name].replace(before, after, 1)
                with self.subTest(guard=module_name, mutation=before), self.assertRaises(ValueError):
                    module.verify(originals, changed)

    def test_exact_binding_and_legacy_path(self):
        for kind in ("Bezier", "Hermite"):
            expected = (
                'extern unsigned int I_MAX;'
                'extern std::atomic<unsigned long long> FINDUV_TOTAL_CALLS;'
                'extern std::atomic<unsigned long long> FINDUV_IMAX_EXITS;'
                f'tuple<double, double> Patch{kind}::FindUV(const PointAdaptive& point) {{'
                'FINDUV_TOTAL_CALLS.fetch_add(1ULL, std::memory_order_relaxed);'
                'double delta = 0.65;'
                'if (iter >= I_MAX) { const unsigned long long hit = '
                '1ULL + FINDUV_IMAX_EXITS.fetch_add(1ULL, std::memory_order_relaxed); }'
                'return {delta, delta}; }')
            self.assertEqual(compact(restore_find_uv_recording(candidate(kind))), compact(expected))
            self.assertEqual(restore_find_uv_recording(expected), expected)

    def test_reject_missing_duplicate_changed_and_relocated_recording(self):
        source = candidate()
        call = "apmesh::diagnostics::RecordFindUvCall();"
        variants = [
            source.replace(call, ""),
            source.replace(call, call * 2),
            source.replace(call, "apmesh::diagnostics::RecordFindUvCall(2);"),
            source.replace(call, "").replace("if (iter", call + "if (iter"),
            source.replace("if (iter >= I_MAX)", "if (iter > I_MAX)"),
        ]
        for changed in variants:
            with self.assertRaises(ValueError):
                restore_find_uv_recording(changed)

    def test_numerical_change_is_not_normalized(self):
        baseline = restore_find_uv_recording(candidate())
        changed = restore_find_uv_recording(candidate().replace("0.65", "0.66"))
        self.assertNotEqual(changed, baseline)

    def test_all_historical_audits_reject_modified_header(self):
        validate_find_uv_header(ROOT, [candidate()])
        for name in ("audit_hermite_construction", "audit_hermite_observers",
                     "audit_patch_copy", "audit_bezier_observers"):
            module = importlib.import_module(name)
            names = getattr(module, "FILES", [getattr(module, "FILE", "")])
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                for name in names:
                    target = root / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((ROOT / name).read_bytes())
                header = root / "include/data/patch/find_uv_statistics.h"
                header.parent.mkdir(parents=True, exist_ok=True)
                header.write_text("modified helper", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "FindUV recording header differs"):
                    module.audit(root, ROOT)
