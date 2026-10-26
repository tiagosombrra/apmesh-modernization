"""Reject incomplete or corrupted memory qualification observations."""

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from qualify_domain_uv_cache import analyze_case


def contracts():
    rows = ["warmup_complete"]
    for shape in range(3):
        for count in (1, 3, 8):
            for throwing in (0, 1):
                rows.append(f"sweep shape={shape} count={count} throw={throwing} allocations=6 denials=6 complete=1")
            rows.append(f"nonalloc shape={shape} faces={count} attempts=0")
        rows.append(f"append_denied shape={shape} prefix=2 unchanged=1")
    rows += [f"consumer mode={mode} cached_faces=2 alive_after_front=1" for mode in range(3)]
    return "\n".join(rows) + "\nCRT retained_blocks=0 retained_bytes=0\nPASS\n"


class DomainUvCacheOracleTests(unittest.TestCase):
    def test_complete_measured_matrix(self):
        result = analyze_case(contracts(), 0, "crt", "contracts")
        self.assertEqual((result["sweeps"], result["denials"], result["nonalloc_faces"]), (18, 108, 36))

    def test_missing_or_duplicate_window(self):
        for text in (contracts().replace("warmup_complete\n", ""), "warmup_complete\n" + contracts()):
            with self.subTest(text=text[:30]), self.assertRaises(ValueError):
                analyze_case(text, 0, "crt", "contracts")

    def test_crt_checkpoint_required_and_zero(self):
        for replacement in ("", "CRT retained_blocks=1 retained_bytes=8", "CRT retained_blocks=0 retained_bytes=8"):
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                analyze_case(contracts().replace("CRT retained_blocks=0 retained_bytes=0", replacement), 0, "crt", "contracts")

    def test_profile_swap_rejected(self):
        with self.assertRaises(ValueError):
            analyze_case(contracts(), 0, "asan", "contracts")

    def test_missing_denial_or_zero_allocations(self):
        for old, new in (("allocations=6 denials=6", "allocations=6 denials=5"),
                         ("allocations=6 denials=6", "allocations=0 denials=0"),
                         ("throw=1", "throw=0")):
            with self.subTest(new=new), self.assertRaises(ValueError):
                analyze_case(contracts().replace(old, new, 1), 0, "crt", "contracts")

    def test_nonempty_cleanup_required(self):
        with self.assertRaises(ValueError):
            analyze_case(contracts().replace("nonalloc shape=0 faces=1 attempts=0", "nonalloc shape=0 faces=0 attempts=0"), 0, "crt", "contracts")

    def test_prefix_and_real_consumer_required(self):
        for old in ("prefix=2 unchanged=1", "consumer mode=2 cached_faces=2 alive_after_front=1"):
            with self.subTest(old=old), self.assertRaises(ValueError):
                analyze_case(contracts().replace(old, "absent", 1), 0, "crt", "contracts")

    def test_uaf_requires_actual_signature_and_failure(self):
        text = "warmup_complete\nERROR: AddressSanitizer: heap-use-after-free\n"
        analyze_case(text, 1, "asan", "uaf")
        for changed, code in ((text, 0), (text.replace("heap-use-after-free", "unrelated-error"), 1)):
            with self.subTest(code=code), self.assertRaises(ValueError):
                analyze_case(changed, code, "asan", "uaf")

    def test_original_failure_requires_retention(self):
        text = "warmup_complete\noriginal_partial_denial=observed\nCRT retained_blocks=1 retained_bytes=8\n"
        analyze_case(text, 1, "crt", "original-partial")
        for changed, code in ((text, 0), (text.replace("blocks=1", "blocks=0"), 1),
                              (text.replace("original_partial_denial=observed", ""), 1)):
            with self.subTest(code=code), self.assertRaises(ValueError):
                analyze_case(changed, code, "crt", "original-partial")

    def test_live_inventory_and_scalar_coverage(self):
        lines = [f"live shape={shape} face={i} id={100+i} uv=0,0;1,0;0,1 mid=0.5,0.5 h=0.25 q=0.5"
                 for shape in range(3) for count in (1, 3, 8) for i in range(count)]
        text = "warmup_complete\n" + "\n".join(lines) + "\nPASS\n"
        self.assertEqual(len(analyze_case(text, 0, "asan", "live")["live_lines"]), 36)
        for changed in (text.replace(lines[0] + "\n", "", 1), text.replace("q=0.5", "q=nan", 1),
                        text.replace(" h=0.25", "", 1), text.replace(" uv=", " coordinates=", 1)):
            with self.subTest(changed=changed[:90]), self.assertRaises(ValueError):
                analyze_case(changed, 0, "asan", "live")


if __name__ == "__main__":
    unittest.main()
