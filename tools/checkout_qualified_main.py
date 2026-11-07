#!/usr/bin/env python3
"""Fast-forward an already merged main without rewriting the qualified file tree."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def git(root, *arguments):
    process = subprocess.run(["git", "-C", str(root), *arguments], capture_output=True,
                             text=True, encoding="utf-8", timeout=30)
    if process.returncode:
        raise ValueError("Git operation failed: " + arguments[0] + ": " + process.stderr.strip())
    return process.stdout.strip()


def clean(root):
    if git(root, "status", "--porcelain", "--untracked-files=normal"):
        raise ValueError("Qualified main checkout requires a clean index and worktree")


def unused_main_elsewhere(root):
    for block in git(root, "worktree", "list", "--porcelain", "-z").split("\0\0"):
        fields = dict(value.split(" ", 1) for value in block.split("\0") if " " in value)
        if fields.get("branch") == "refs/heads/main" and Path(fields["worktree"]).resolve() != root:
            raise ValueError("Main is checked out in another worktree")


def snapshot(root):
    result = {}
    for entry in git(root, "ls-files", "--stage", "-z").split("\0"):
        if not entry:
            continue
        metadata, name = entry.split("\t", 1)
        mode, _, stage = metadata.split()
        path = root / name
        if mode not in ("100644", "100755") or stage != "0" or path.is_symlink():
            raise ValueError("Only regular, resolved tracked files are supported: " + name)
        if not path.resolve().is_relative_to(root) or not path.is_file():
            raise ValueError("Tracked file is missing or outside the worktree: " + name)
        stat = path.stat()
        result[name] = [stat.st_size, stat.st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest()]
    if not result:
        raise ValueError("Empty tracked-file inventory is not qualification")
    return result


def checkout(root, base, head, merged, apply=False):
    root = root.resolve()
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("Use the exact repository worktree root")
    for revision in (base, head, merged):
        if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", revision):
            raise ValueError("Explicit full commit hashes are required")
        if git(root, "rev-parse", "--verify", revision + "^{commit}") != revision:
            raise ValueError("Commit identity did not resolve exactly")
    clean(root)
    unused_main_elsewhere(root)
    if git(root, "rev-parse", "HEAD") != head:
        raise ValueError("Current HEAD is not the qualified delivery head")
    if git(root, "rev-parse", "refs/heads/main") != base:
        raise ValueError("Local main advanced; inspect it before checkout")
    if git(root, "rev-parse", "refs/remotes/origin/main") != merged:
        raise ValueError("Fetched origin/main is not the audited merge")
    if git(root, "rev-list", "--parents", "-n", "1", merged).split() != [merged, base, head]:
        raise ValueError("Merge parents differ from the audited base and delivery head")
    tree = git(root, "rev-parse", head + "^{tree}")
    if git(root, "rev-parse", merged + "^{tree}") != tree:
        raise ValueError("Merged tree differs from the qualified delivery tree")
    before = snapshot(root)
    fingerprint = hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest()
    result = {"status": "planned", "base": base, "head": head, "main": merged, "tree": tree,
              "tracked_files": len(before), "file_state_sha256": fingerprint,
              "scope": "Local checkout only; caller owns remote merge authorization and exact-head/main gates"}
    if not apply:
        return result
    clean(root)
    unused_main_elsewhere(root)
    # Compare-and-swap protects concurrent advances; no reset, force or stash is used.
    git(root, "update-ref", "-m", "Fast-forward main to audited qualified merge",
        "refs/heads/main", merged, base)
    git(root, "switch", "main")
    if git(root, "rev-parse", "HEAD") != merged:
        raise ValueError("Main checkout did not reach the audited merge")
    clean(root)
    if snapshot(root) != before:
        raise ValueError("Tracked bytes or timestamps changed; inspect the retained state")
    result.update(status="checked_out", tracked_bytes_and_mtimes_preserved=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--merge", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.output and args.output.exists():
            raise ValueError("Receipt already exists; do not overwrite it or retry blindly")
        if args.output:
            output = args.output.resolve()
            git_directory = Path(git(args.root, "rev-parse", "--absolute-git-dir")).resolve()
            common_directory = Path(git(args.root, "rev-parse", "--git-common-dir"))
            if not common_directory.is_absolute():
                common_directory = args.root.resolve() / common_directory
            common_directory = common_directory.resolve()
            if output.is_relative_to(git_directory) or output.is_relative_to(common_directory):
                raise ValueError("Receipt cannot overwrite Git metadata")
            if output.is_relative_to(args.root.resolve()):
                relative = output.relative_to(args.root.resolve()).as_posix()
                if git(args.root, "ls-files", "--", relative):
                    raise ValueError("Receipt cannot overwrite a tracked file")
                try:
                    git(args.root, "check-ignore", "--", relative)
                except ValueError:
                    raise ValueError("A receipt inside the worktree must use an ignored path") from None
            # Catch invalid/unwritable output directories before advancing any ref.
            output.parent.mkdir(parents=True, exist_ok=True)
        result = checkout(args.root, args.base, args.head, args.merge, args.apply)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print("Qualified main checkout failed: " + str(error), file=sys.stderr)
        return 1
    if args.output:
        try:
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(result, indent=2) + "\n")
        except OSError as error:
            print("Checkout completed but receipt publication failed; inspect refs before retry: "
                  + str(error), file=sys.stderr)
            return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
