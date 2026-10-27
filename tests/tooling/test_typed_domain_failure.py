"""Reject misclassified, copied, incomplete or falsely successful domain failures."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from typed_domain_failure_case import validate_cli, validate_library, validate_types


def types():
    return "\n".join(f"typed_error case={i} status_bytes={n} payload=1 identity=1 allocations=0"
                     for i, n in enumerate([0, 17, 257] * 3)) + "\ntyped_unwind_hook attempts=1 denied=1\ntyped_error_contracts=9 complete=1\n"


LIBRARY = "typed_library patches=4 target=1 calls=2 changed_before=1 detached=4 nonnull_after_owner=0 samples=0 allocations=0 unwind_allocations=0 denied=0 payload=1\n"
CLI = "Typed domain control: step=2 patch=1\n" * 2 + "Error: domain generation failed (step=2, patch=1, retry=0, status=generation_failed)\nTyped CLI unwind allocations=0\n"


class TypedDomainFailureOracleTests(unittest.TestCase):
    def test_complete_types(self):
        validate_types(0, types())

    def test_missing_payload_identity_or_nonempty_status(self):
        for old, new in (("status_bytes=257", "status_bytes=0"), ("payload=1", "payload=0"),
                         ("identity=1", "identity=0"), ("allocations=0", "allocations=1")):
            with self.subTest(new=new), self.assertRaises(ValueError):
                validate_types(0, types().replace(old, new, 1))

    def test_hook_and_completion_required(self):
        for text in (types().replace("typed_unwind_hook attempts=1 denied=1", ""),
                     types() + "typed_error_contracts=9 complete=1\n", types().split("\n", 1)[1]):
            with self.subTest(text=text[-60:]), self.assertRaises(ValueError):
                validate_types(0, text)

    def test_actual_library_context(self):
        validate_library(0, LIBRARY, "eistute")

    def test_library_requires_cleanup_attempts_and_payload(self):
        for old, new in (("calls=2", "calls=1"), ("changed_before=1", "changed_before=0"),
                         ("detached=4", "detached=0"), ("payload=1", "payload=0"),
                         ("unwind_allocations=0", "unwind_allocations=1")):
            with self.subTest(new=new), self.assertRaises(ValueError):
                validate_library(0, LIBRARY.replace(old, new), "eistute")

    def test_exact_cli_status_and_classification(self):
        validate_cli(1, CLI, 1, 2)
        for code, text in ((0, CLI), (4294967295, CLI), (1, CLI + "Error: input or configuration failure: other\n")):
            with self.subTest(code=code), self.assertRaises(ValueError):
                validate_cli(code, text, 1, 2)

    def test_cli_context_count_and_single_diagnostic(self):
        for text in (CLI.replace("retry=0", "retry=1"), CLI.replace("status=generation_failed", "status=ok"),
                     CLI + "Error: domain generation failed\n", CLI.split("\n", 1)[1]):
            with self.subTest(text=text[-60:]), self.assertRaises(ValueError):
                validate_cli(1, text, 1, 2)

    def test_cli_requires_nonallocating_unwind(self):
        with self.assertRaises(ValueError):
            validate_cli(1, CLI.replace("unwind allocations=0", "unwind allocations=1"), 1, 2)


if __name__ == "__main__":
    unittest.main()
