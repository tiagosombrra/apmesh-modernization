#!/usr/bin/env python3
"""Check staged bytes, including partially staged files, without rewriting them."""

import subprocess
import sys
from pathlib import Path

import quality


def main():
    names = quality.run([quality.tool("git"), "diff", "--cached", "--name-only", "-z",
                         "--diff-filter=ACMRT", "--"], capture=True).stdout.decode("utf-8").split("\0")
    count = 0
    for name in filter(None, names):
        path = (quality.ROOT / name).resolve()
        if not path.is_relative_to(quality.ROOT) or not quality.allowed(path):
            continue
        if path.suffix not in quality.TEXT and path.name not in quality.SPECIAL:
            continue
        # Inspect the index rather than a potentially different working copy.
        data = quality.run([quality.tool("git"), "show", f":{name}"], capture=True).stdout
        if data != quality.normalized(data, markdown=path.suffix == ".md"):
            raise ValueError(f"Staged whitespace differs: {name}")
        if path.suffix in quality.CPP:
            result = subprocess.run([quality.tool("clang-format"), "--style=file",
                                     f"--assume-filename={path}"], input=data,
                                    capture_output=True, check=True, cwd=quality.ROOT)
            if result.stdout != data:
                raise ValueError(f"Staged C++ format differs: {name}")
        count += 1
    print(f"Pre-commit: {count} applicable staged files checked")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"Pre-commit failed: {error}", file=sys.stderr)
        raise SystemExit(1)
