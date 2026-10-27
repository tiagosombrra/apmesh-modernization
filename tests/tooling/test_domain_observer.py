"""Reject false observer cleanup, zero coverage and exception replacement."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from domain_observer_case import expected_helpers, validate_failure, validate_helpers


def helpers():
    return "\n".join(f"domain_observers layout={l} reverse={v} rethrow={r} owners={o} owned_links={n} foreign_links=2 null_links=2 null_patches=1 attempts=0 identity=1"
                     for l, v, r, o, n in expected_helpers()) + "\ndomain_observer_hook attempts=1 denied=1\ndomain_observer_contracts=12 complete=1\n"


FAILURE = "domain_failure patches=4 target=1 live_before=4 changed_before=1 null_after=4 nonnull_after_owner=0 samples_after=0 attempts=0 denied=0 identity=1\n"


class DomainObserverOracleTests(unittest.TestCase):
    def test_complete_nonempty_matrix(self):
        validate_helpers(0, helpers())

    def test_missing_or_duplicate_layout_rejected(self):
        lines = helpers().splitlines()
        for changed in ("\n".join(lines[1:]), lines[0] + "\n" + helpers()):
            with self.subTest(changed=changed[:50]), self.assertRaises(ValueError):
                validate_helpers(0, changed)

    def test_foreign_null_zero_owner_or_allocation_rejected(self):
        for old, new in (("foreign_links=2", "foreign_links=1"), ("null_links=2", "null_links=0"),
                         ("owners=2", "owners=0"), ("attempts=0", "attempts=1")):
            with self.subTest(new=new), self.assertRaises(ValueError):
                validate_helpers(0, helpers().replace(old, new, 1))

    def test_hook_and_completion_required_once(self):
        for changed in (helpers().replace("hook attempts=1 denied=1", "hook attempts=0 denied=0"),
                        helpers().replace("domain_observer_contracts=12 complete=1", ""),
                        helpers() + "domain_observer_contracts=12 complete=1\n"):
            with self.subTest(changed=changed[-70:]), self.assertRaises(ValueError):
                validate_helpers(0, changed)

    def test_actual_failure_summary(self):
        validate_failure(0, FAILURE, "eistute")

    def test_retained_or_missing_partial_publication_rejected(self):
        for old, new in (("null_after=4", "null_after=0"), ("nonnull_after_owner=0", "nonnull_after_owner=4"),
                         ("changed_before=1", "changed_before=0"), ("live_before=4", "live_before=0")):
            with self.subTest(new=new), self.assertRaises(ValueError):
                validate_failure(0, FAILURE.replace(old, new), "eistute")

    def test_exception_identity_allocation_or_process_failure_rejected(self):
        for code, changed in ((1, FAILURE), (0, FAILURE.replace("identity=1", "identity=0")),
                              (0, FAILURE.replace("attempts=0", "attempts=1")),
                              (0, FAILURE + "Domain observer failure: other\n")):
            with self.subTest(code=code), self.assertRaises(ValueError):
                validate_failure(code, changed, "eistute")

    def test_model_and_duplicate_summary_rejected(self):
        for text, model in ((FAILURE, "book"), (FAILURE + FAILURE, "eistute")):
            with self.subTest(model=model), self.assertRaises(ValueError):
                validate_failure(0, text, model)


if __name__ == "__main__":
    unittest.main()
