"""Exercise guarded branch advancement with real disposable Git repositories."""

import os
import contextlib
import io
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import checkout_qualified_main as delivery


class QualifiedMainCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="apmesh-checkout-")
        self.addCleanup(self.temporary.cleanup)
        self.outer = Path(self.temporary.name)
        self.root = self.outer / "repo"
        self.root.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.source = self.root / "source.cpp"
        self.source.write_text("int value = 1;\n", encoding="utf-8")
        self.git("add", ".")
        self.base = self.commit(self.git("write-tree"), [], "Base")
        self.git("update-ref", "refs/heads/main", self.base)
        self.git("switch", "-c", "candidate")
        self.source.write_text("int value = 2;\n", encoding="utf-8")
        (self.root / "new.hpp").write_text("#pragma once\n", encoding="utf-8")
        self.git("add", ".")
        self.head = self.commit(self.git("write-tree"), [self.base], "Qualified head")
        self.git("update-ref", "refs/heads/candidate", self.head)
        self.tree = self.git("rev-parse", self.head + "^{tree}")
        self.merged = self.commit(self.tree, [self.base, self.head], "Merged")
        self.git("update-ref", "refs/remotes/origin/main", self.merged)
        for name in ("source.cpp", "new.hpp"):
            os.utime(self.root / name, ns=(1700000000000000000, 1700000000000000000))

    def git(self, *args):
        return delivery.git(self.root, *args)

    def commit(self, tree, parents, message):
        arguments = ["commit-tree", tree]
        for parent in parents:
            arguments += ["-p", parent]
        return self.git(*arguments, "-m", message)

    def run_checkout(self, apply=False, merged=None):
        return delivery.checkout(self.root, self.base, self.head, merged or self.merged, apply)

    def test_plan_is_read_only(self):
        before = delivery.snapshot(self.root)
        self.assertEqual(self.run_checkout()["status"], "planned")
        self.assertEqual(self.git("rev-parse", "HEAD"), self.head)
        self.assertEqual(self.git("rev-parse", "main"), self.base)
        self.assertEqual(delivery.snapshot(self.root), before)

    def test_apply_preserves_existing_and_added_file_bytes_and_timestamps(self):
        before = delivery.snapshot(self.root)
        result = self.run_checkout(True)
        self.assertEqual(result["status"], "checked_out")
        self.assertEqual(self.git("rev-parse", "HEAD"), self.merged)
        self.assertEqual(self.git("symbolic-ref", "HEAD"), "refs/heads/main")
        self.assertEqual(delivery.snapshot(self.root), before)

    def test_old_checkout_sequence_rewrites_qualified_sources(self):
        before = delivery.snapshot(self.root)
        self.git("switch", "main")
        self.git("merge", "--ff-only", "origin/main")
        after = delivery.snapshot(self.root)
        self.assertEqual(before["source.cpp"][2], after["source.cpp"][2])
        self.assertNotEqual(before["source.cpp"][1], after["source.cpp"][1])
        self.assertNotEqual(before["new.hpp"][1], after["new.hpp"][1])

    def test_dirty_worktree_index_and_untracked_file_block_advancement(self):
        self.source.write_text("uncommitted\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.run_checkout(True)
        self.git("add", "source.cpp")
        with self.assertRaises(ValueError):
            self.run_checkout(True)
        self.source.write_text("int value = 2;\n", encoding="utf-8")
        self.git("add", "source.cpp")
        (self.root / "untracked").write_text("local\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.run_checkout(True)
        self.assertEqual(self.git("rev-parse", "main"), self.base)

    def test_wrong_remote_tree_and_parent_order_are_rejected(self):
        self.git("update-ref", "refs/remotes/origin/main", self.head)
        with self.assertRaises(ValueError):
            self.run_checkout(True)
        for tree, parents in ((self.git("rev-parse", self.base + "^{tree}"), [self.base, self.head]),
                              (self.tree, [self.head, self.base])):
            merged = self.commit(tree, parents, "Invalid merge")
            self.git("update-ref", "refs/remotes/origin/main", merged)
            with self.assertRaises(ValueError):
                self.run_checkout(True, merged)
        self.assertEqual(self.git("rev-parse", "main"), self.base)

    def test_main_in_another_worktree_blocks_advancement(self):
        self.git("worktree", "add", str(self.outer / "other"), "main")
        with self.assertRaises(ValueError):
            self.run_checkout(True)
        self.assertEqual(self.git("rev-parse", "main"), self.base)

    def test_compare_and_swap_preserves_a_concurrent_main_advance(self):
        concurrent = self.commit(self.tree, [self.base], "Concurrent main")
        original = delivery.git

        def raced(root, *args):
            if args[0] == "update-ref":
                original(root, "update-ref", "refs/heads/main", concurrent, self.base)
            return original(root, *args)

        with patch.object(delivery, "git", side_effect=raced), self.assertRaises(ValueError):
            self.run_checkout(True)
        self.assertEqual(self.git("rev-parse", "main"), concurrent)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.head)

    def test_normal_checkout_hook_is_not_bypassed(self):
        hooks = self.outer / "hooks"
        hooks.mkdir()
        marker = self.outer / "hook-ran"
        hook = hooks / "post-checkout"
        hook.write_text("#!/bin/sh\nprintf 'ran' > " + shlex.quote(marker.as_posix()) + "\n",
                        encoding="utf-8", newline="\n")
        hook.chmod(0o755)
        self.git("config", "core.hooksPath", str(hooks))
        self.run_checkout(True)
        self.assertEqual(marker.read_text(encoding="utf-8"), "ran")

    def test_cli_rejects_git_metadata_unignored_and_existing_receipts(self):
        existing = self.outer / "existing.json"
        existing.write_text("preserved", encoding="utf-8")
        blocked_parent = self.outer / "not-a-directory"
        blocked_parent.write_text("preserved", encoding="utf-8")
        for output in (self.root / ".git/new-receipt", self.root / "unignored.json", existing,
                       blocked_parent / "receipt.json"):
            arguments = ["checkout", "--root", str(self.root), "--base", self.base,
                         "--head", self.head, "--merge", self.merged, "--apply", "--output", str(output)]
            with self.subTest(output=output), patch.object(sys, "argv", arguments), \
                    contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(delivery.main(), 1)
            self.assertEqual(self.git("rev-parse", "main"), self.base)
        self.assertEqual(existing.read_text(encoding="utf-8"), "preserved")

    def test_linked_worktree_receipt_cannot_enter_common_git_metadata(self):
        linked = self.outer / "linked"
        self.git("worktree", "add", "-b", "linked-delivery", str(linked), self.head)
        output = self.root / ".git/common-receipt"
        arguments = ["checkout", "--root", str(linked), "--base", self.base, "--head", self.head,
                     "--merge", self.merged, "--apply", "--output", str(output)]
        with patch.object(sys, "argv", arguments), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(delivery.main(), 1)
        self.assertEqual(self.git("rev-parse", "main"), self.base)


if __name__ == "__main__":
    unittest.main()
