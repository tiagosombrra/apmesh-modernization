#!/usr/bin/env python3
"""Explicit local formatting, lint and test entry points; no production dependency."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CPP = {".cpp", ".cc", ".cxx", ".h", ".hpp"}
TEXT = CPP | {".py", ".md", ".txt", ".cmake", ".json", ".yml", ".yaml", ".conf"}
SPECIAL = {".editorconfig", ".clang-format", ".clang-tidy", ".gitignore", "Doxyfile"}
EXCLUDED = {".git", "libs", "reference", "input_models", "paper", "assets", "build", "results"}


def run(command: list[str], *, capture: bool = False,
        timeout: float | None = None) -> subprocess.CompletedProcess:
    """Execute argument vectors without a shell and preserve failure codes."""
    return subprocess.run(command, cwd=ROOT, check=True, capture_output=capture, timeout=timeout)


def tool(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise ValueError(f"Required tool is unavailable: {name}")
    return found


def doctor() -> int:
    """Inventory every required tool; missing and broken tools fail the check."""
    failures = 0
    for name in ("git", "cmake", "ctest", "ninja", "clang-format", "clang-tidy", "doxygen"):
        executable = shutil.which(name)
        print(f"{name}: {executable or 'UNAVAILABLE (not found on PATH)'}")
        if not executable:
            failures += 1
            continue
        try:
            run([executable, "--version"], timeout=10)
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            failures += 1
            print(f"{name}: BROKEN ({error})", file=sys.stderr)
    return int(failures != 0)


def allowed(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return not any(part in EXCLUDED or part.startswith("build-") for part in relative.parts)


def select(paths: list[str], base: str | None, *, cpp: bool = False) -> list[Path]:
    """Select first-party tracked or explicit files; empty coverage is an error."""
    if paths:
        names = paths
    elif base:
        names = run([tool("git"), "diff", "--name-only", "-z", "--diff-filter=ACMRT", base,
                     "--"], capture=True).stdout.decode("utf-8").split("\0")
    else:
        names = run([tool("git"), "ls-files", "-z"], capture=True).stdout.decode("utf-8").split("\0")
    selected = set()
    for name in filter(None, names):
        candidate = ROOT / name
        if candidate.is_symlink():
            raise ValueError(f"Symbolic links are not valid quality inputs: {name}")
        path = candidate.resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError(f"Path is outside the repository: {name}")
        if not allowed(path):
            if paths:
                raise ValueError(f"Excluded historical/vendor/generated input: {name}")
            continue
        supported = path.suffix in (CPP if cpp else TEXT) or (not cpp and path.name in SPECIAL)
        if supported:
            if not path.is_file():
                raise ValueError(f"Input file is missing: {name}")
            selected.add(path)
    if not selected:
        raise ValueError("No applicable files selected; validation has no coverage")
    return sorted(selected)


def normalized(data: bytes, *, markdown: bool = False) -> bytes:
    """Normalize text; retain Markdown's meaningful two-space hard line breaks."""
    text = data.decode("utf-8")
    if "\0" in text:
        raise ValueError("Binary content is not a whitespace input")
    lines = []
    for line in text.splitlines():
        clean = line.rstrip(" \t")
        if markdown and clean and line.endswith("  "):
            clean += "  "
        lines.append(clean)
    return ("\n".join(lines).rstrip("\n") + "\n" if lines else "").encode("utf-8")


def whitespace(paths: list[Path], fix: bool) -> int:
    dirty = []
    for path in paths:
        data = path.read_bytes()
        clean = normalized(data, markdown=path.suffix == ".md")
        if data != clean:
            dirty.append(path)
            if fix:
                path.write_bytes(clean)
            print(f"{'Fixed' if fix else 'Whitespace differs'}: {path.relative_to(ROOT)}")
    print(f"Whitespace coverage: {len(paths)} files; differences: {len(dirty)}")
    return int(bool(dirty) and not fix)


def compilation_sources(build: Path) -> set[Path]:
    """Require real translation units, rather than accepting an empty database."""
    database = json.loads((build / "compile_commands.json").read_text(encoding="utf-8"))
    result = set()
    for entry in database:
        directory = Path(entry["directory"])
        path = (directory / entry["file"]).resolve()
        if path.is_relative_to(ROOT) and allowed(path) and path.suffix in {".cpp", ".cc", ".cxx"}:
            result.add(path)
    if not result:
        raise ValueError("Compilation database has no first-party translation units")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["doctor", "whitespace", "format", "tidy", "test", "docs"])
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--base", help="Git revision used to select changed files")
    parser.add_argument("--fix", action="store_true", help="Explicitly change whitespace or formatting")
    parser.add_argument("--build", default="build/local-serial")
    args = parser.parse_args()
    if args.fix and args.action not in {"whitespace", "format"}:
        parser.error("--fix is supported only for whitespace and format")
    if args.action == "doctor":
        return doctor()
    if args.action in {"whitespace", "format", "tidy"}:
        files = select(args.paths, args.base, cpp=args.action != "whitespace")
        if args.action == "whitespace":
            return whitespace(files, args.fix)
        if args.action == "format":
            formatter = tool("clang-format")
            for path in files:
                run([formatter, "--style=file", *(["-i"] if args.fix else ["--dry-run", "--Werror"]), str(path)])
        else:
            available = compilation_sources(ROOT / args.build)
            if not all(path in available for path in files):
                raise ValueError("Select compiled translation units for tidy; headers are checked through their consumers")
            analyzer = tool("clang-tidy")
            for path in files:
                run([analyzer, "-p", str(ROOT / args.build), str(path)])
        print(f"{args.action} coverage: {len(files)} files")
    elif args.action == "test":
        run([tool("ctest"), "--test-dir", str(ROOT / args.build), "--output-on-failure", "--no-tests=error"])
    elif args.action == "docs":
        run([tool("doxygen"), "Doxyfile"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        print(f"Quality command failed: {error}", file=sys.stderr)
        raise SystemExit(1)
