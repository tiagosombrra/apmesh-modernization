"""Adversarial controls for the local regression accounting contract."""

from pathlib import Path
import tempfile
import unittest

from run_research_regression import (BLOCKED, FAIL, PASS, compare_receipts, count_node_tests,
                                     count_python_tests, read_ctest_result, summarize)


class RegressionAccountingTests(unittest.TestCase):
    def test_success_requires_nonzero_tests(self):
        self.assertEqual(count_python_tests("Ran 4 tests in 0.001s\n\nOK\n", 0),
                         {"status": PASS, "tests": 4, "skips": 0})

    def test_zero_tests_is_failure(self):
        self.assertEqual(count_python_tests("Ran 0 tests in 0.001s\n\nOK\n", 0)["status"], FAIL)

    def test_skips_block_complete_pass(self):
        self.assertEqual(count_python_tests("Ran 4 tests in 0.001s\n\nOK (skipped=2)\n", 0)["status"], BLOCKED)

    def test_nonzero_status_overrides_output(self):
        self.assertEqual(count_python_tests("Ran 4 tests in 0.001s\n\nOK\n", 1)["status"], FAIL)

    def test_timeout_is_failure(self):
        self.assertEqual(count_python_tests("REGRESSION TIMEOUT", None)["status"], FAIL)

    def test_ambiguous_count_fails(self):
        self.assertEqual(count_python_tests("Ran 4 tests in 0.001s\nRan 4 tests in 0.001s\nOK\n", 0)["status"], FAIL)

    def test_failed_unittest_fails(self):
        self.assertEqual(count_python_tests("Ran 4 tests in 0.001s\nFAILED (failures=1)\n", 1)["status"], FAIL)

    def test_recovered_scope_never_passes(self):
        self.assertEqual(summarize([{"status": PASS}], "recovered", 80, 80), BLOCKED)

    def test_missing_module_never_passes(self):
        self.assertEqual(summarize([{"status": PASS}], "checkout", 80, 79), BLOCKED)

    def test_failure_overrides_blocker(self):
        self.assertEqual(summarize([{"status": BLOCKED}, {"status": FAIL}], "checkout", 80, 80), FAIL)

    def test_complete_accounting_passes(self):
        self.assertEqual(summarize([{"status": PASS}], "checkout", 80, 80), PASS)

    def test_ctest_missing_receipt_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(read_ctest_result(Path(temp) / "missing.xml", 0)["status"], FAIL)

    def test_ctest_empty_receipt_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "ctest.xml"
            p.write_text("<testsuite/>")
            self.assertEqual(read_ctest_result(p, 0)["status"], FAIL)

    def test_ctest_incomplete_inventory_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "ctest.xml"
            p.write_text("<testsuite><testcase name='one'/></testsuite>")
            self.assertEqual(read_ctest_result(p, 0)["status"], BLOCKED)

    def test_ctest_failures_are_not_success(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "ctest.xml"
            p.write_text("<testsuite><testcase><failure/></testcase></testsuite>")
            self.assertEqual(read_ctest_result(p, 0)["status"], FAIL)

    def test_ctest_skips_block_completion(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "ctest.xml"
            p.write_text("<testsuite>" + "<testcase/>" * 75 + "<testcase><skipped/></testcase></testsuite>")
            self.assertEqual(read_ctest_result(p, 0)["status"], BLOCKED)

    def test_ctest_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "ctest.xml"
            p.write_text("<testsuite>" + "<testcase/>" * 75 + "</testsuite>")
            self.assertEqual(read_ctest_result(p, 0)["status"], PASS)


    def test_ctest_malformed_receipt_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "ctest.xml"
            p.write_text("<invalid")
            self.assertEqual(read_ctest_result(p, 0)["status"], FAIL)

    def test_numeric_portability_budget(self):
        compare_receipts({"values": [1.0, True]}, {"values": [1.0 + 1e-10, True]})

    def test_receipt_shape_mismatch(self):
        with self.assertRaises(ValueError):
            compare_receipts({"values": [1.0]}, {"values": [1.0, 2.0]})

    def test_receipt_numeric_drift_rejected(self):
        with self.assertRaises(ValueError):
            compare_receipts([1.0], [1.001])

    def test_receipt_boolean_not_number(self):
        with self.assertRaises(ValueError):
            compare_receipts(True, 1)

    def test_node_nonempty_pass(self):
        log = "# tests 4\n# pass 4\n# fail 0\n# skipped 0\n"
        self.assertEqual(count_node_tests(log, 0)["status"], PASS)

    def test_node_skip_blocks(self):
        log = "# tests 4\n# pass 3\n# fail 0\n# skipped 1\n"
        self.assertEqual(count_node_tests(log, 0)["status"], BLOCKED)

    def test_node_zero_fails(self):
        log = "# tests 0\n# pass 0\n# fail 0\n# skipped 0\n"
        self.assertEqual(count_node_tests(log, 0)["status"], FAIL)

if __name__ == "__main__":
    unittest.main()
