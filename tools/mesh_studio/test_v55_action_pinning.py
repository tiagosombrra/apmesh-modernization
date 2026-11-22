"""Fail closed on mutable or unexpected action sources in Studio research CI."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = {
    ".github/workflows/mesh-studio-validation.yml": 41,
    ".github/workflows/mesh-studio-fast-web.yml": 4,
    ".github/workflows/mesh-studio-lock-bootstrap.yml": 6,
}
APPROVED_ACTIONS = {
    "actions/checkout": "11d5960a326750d5838078e36cf38b85af677262",
    "actions/setup-python": "a26af69be951a213d495a4c3e4e4022e16d87065",
    "actions/setup-node": "49933ea5288caeca8642d1e84afbd3f7d6820020",
    "actions/upload-artifact": "ea165f8d65b6e75b540449e92b4886f43607fa02",
    "actions/download-artifact": "d3f86a106a0bac45b974a628896c90dbdf5c8093",
}
USES_LINE = re.compile(r"^\s*(?:-\s+)?uses:\s*(\S+)(?:\s+#.*)?$")
ACTION_REF = re.compile(r"^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([0-9a-f]{40})$")


def inspect_action_pins(source: str) -> Counter[str]:
    """Check every GitHub Actions 'uses' reference, not just expected ones."""
    counts: Counter[str] = Counter()
    for number, line in enumerate(source.splitlines(), start=1):
        if not re.match(r"^\s*(?:-\s+)?uses:\s*", line):
            continue
        use = USES_LINE.fullmatch(line)
        if not use:
            raise ValueError(f"unparseable_action_reference:{number}")
        ref = ACTION_REF.fullmatch(use.group(1))
        if not ref:
            raise ValueError(f"mutable_or_non_sha_action_reference:{number}")
        action, sha = ref.groups()
        if APPROVED_ACTIONS.get(action) != sha:
            raise ValueError(f"unreviewed_action_or_sha:{number}")
        counts[action] += 1
    if not counts:
        raise ValueError("missing_reviewed_action_references")
    return counts


class StudioV55ActionPinTests(unittest.TestCase):
    def test_actual_workflows_pin_every_action_to_verified_commit(self):
        for relative_path, expected_uses in WORKFLOWS.items():
            with self.subTest(workflow=relative_path):
                actual = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertEqual(sum(inspect_action_pins(actual).values()), expected_uses)
                self.assertIn("feature/mesh-studio-v55-pinned-actions-20261122", actual)

    def test_mutable_action_tags_and_branches_are_rejected(self):
        for ref in ("actions/checkout@v4", "actions/checkout@main",
                    "actions/checkout@latest", "actions/checkout@11d5960a"):
            with self.subTest(ref=ref):
                with self.assertRaisesRegex(ValueError, "mutable_or_non_sha"):
                    inspect_action_pins("    - uses: " + ref)

    def test_unapproved_source_or_rewritten_sha_is_rejected(self):
        for ref in ("unknown/checkout@11d5960a326750d5838078e36cf38b85af677262",
                    "actions/checkout@" + "0" * 40):
            with self.subTest(ref=ref):
                with self.assertRaisesRegex(ValueError, "unreviewed_action_or_sha"):
                    inspect_action_pins("    - uses: " + ref)

    def test_comment_is_not_part_of_pinned_ref(self):
        self.assertEqual(inspect_action_pins(
            "- uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4"
        )["actions/checkout"], 1)

    def test_empty_workflow_does_not_pass(self):
        with self.assertRaisesRegex(ValueError, "missing_reviewed_action_references"):
            inspect_action_pins("steps: []")


if __name__ == "__main__":
    unittest.main()
