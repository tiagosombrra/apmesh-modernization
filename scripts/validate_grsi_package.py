#!/usr/bin/env python3
from __future__ import annotations

import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_PREPRINT_BYTES = 100 * 1024 * 1024

REQUIRED_FILES = [
    "README.md",
    "GRSI_SUBMISSION.txt",
    "GRSI_LIABILITY.txt",
    "INSTALL_WINDOWS.txt",
    "DATA_PROVENANCE.md",
    "GRSI_FORM_VALUES.txt",
    "LICENSE",
    "THIRD_PARTY_LICENSES.md",
    "reproduce_eistute_windows.bat",
    "reproduce_eistute_linux.sh",
    "docs/GRSI_REVIEW_GUIDE.md",
    "assets/grsi_representative.png",
    "paper/preprint.pdf",
    "reference/eistute_stage4.obj",
    "reference/eistute_metrics.csv",
    "reference/eistute_stage4.json",
    "scripts/verify_reference.py",
    "scripts/verify_eistute.py",
]


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        signature = stream.read(8)
        if signature != b"\x89PNG\r\n\x1a\n":
            raise ValueError("not a PNG file")
        length = struct.unpack(">I", stream.read(4))[0]
        chunk_type = stream.read(4)
        if chunk_type != b"IHDR" or length < 8:
            raise ValueError("missing PNG IHDR")
        width, height = struct.unpack(">II", stream.read(8))
        return width, height


def read_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def tracked_files() -> set[str]:
    try:
        completed = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return set()
    return {
        line.strip().replace("\\", "/")
        for line in completed.stdout.splitlines()
        if line.strip()
    }


def main() -> None:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing required file: {relative}")

    image_path = ROOT / "assets/grsi_representative.png"
    if image_path.is_file():
        try:
            dimensions = png_dimensions(image_path)
            if dimensions != (250, 250):
                errors.append(
                    f"representative image is {dimensions[0]}x{dimensions[1]}, "
                    "expected 250x250"
                )
        except ValueError as exc:
            errors.append(f"invalid representative image: {exc}")

    preprint_path = ROOT / "paper/preprint.pdf"
    if preprint_path.is_file():
        with preprint_path.open("rb") as stream:
            if stream.read(5) != b"%PDF-":
                errors.append("paper/preprint.pdf does not have a valid PDF signature")
        if preprint_path.stat().st_size > MAX_PREPRINT_BYTES:
            errors.append(
                "paper/preprint.pdf exceeds the GRSI form limit of 100 MB"
            )

    liability = ROOT / "GRSI_LIABILITY.txt"
    if liability.is_file():
        text = liability.read_text(encoding="utf-8")
        if "[INSERT SUBMISSION DATE]" in text or '[TYPE "CONFIRMED"' in text:
            errors.append(
                "GRSI_LIABILITY.txt still contains author-confirmation placeholders"
            )

    provenance = ROOT / "DATA_PROVENANCE.md"
    if provenance.is_file():
        text = provenance.read_text(encoding="utf-8")
        if "Author confirmation required before submission" in text:
            errors.append(
                "DATA_PROVENANCE.md still requires the author to select and confirm "
                "the applicable provenance option"
            )

    eistute_config_path = ROOT / "configs/eistute/article.conf"
    if eistute_config_path.is_file():
        config = read_config(eistute_config_path)
        if config.get("ADAPTIVE_MAX_STEPS") != "4":
            errors.append(
                "configs/eistute/article.conf must set ADAPTIVE_MAX_STEPS=4 "
                "for the Figure 7 states 0-4"
            )

    tracked = tracked_files()
    generated_tracked = sorted(
        path
        for path in tracked
        if "/__pycache__/" in f"/{path}/"
        or path.endswith((".pyc", ".pyo", ".pyd"))
    )
    if generated_tracked:
        errors.append(
            "generated Python files are tracked by Git: "
            + ", ".join(generated_tracked)
        )

    if "PATCH_CONTENTS.txt" in tracked or (ROOT / "PATCH_CONTENTS.txt").exists():
        errors.append(
            "PATCH_CONTENTS.txt is an internal packaging note and must not be "
            "included in the submission repository"
        )

    if errors:
        print("GRSI package validation found unresolved items:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("GRSI repository package structure verified.")
    print("Representative image verified: 250x250 PNG.")
    print("Author preprint verified: valid PDF under 100 MB.")
    print("Eistute stage range verified: 0-4.")
    print("No generated Python bytecode or internal patch note is tracked.")


if __name__ == "__main__":
    main()
