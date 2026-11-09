#!/usr/bin/env python3
"""Exercise fail-closed mesh selection through the real CLI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def run_case(executable: Path, extra: str, expected: str, template: str = "y") -> None:
    with TemporaryDirectory(prefix="apmesh-m3-dispatch-") as temporary:
        root = Path(temporary)
        config = root / "input.conf"
        output = root / "forbidden-output"
        config.write_text(
            "INPUT_MODEL=unread-fixture.bp\n"
            f"OUTPUT_PREFIX={output.as_posix()}\n"
            f"USE_TEMPLATE={template}\n"
            + extra,
            encoding="utf-8",
        )
        process = subprocess.run(
            [str(executable), "--config", str(config)],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if process.returncode == 0 or expected not in process.stderr:
            raise AssertionError(
                f"Expected {expected!r}, got status {process.returncode}, "
                f"stdout={process.stdout!r}, stderr={process.stderr!r}"
            )
        if output.exists() or list(root.iterdir()) != [config]:
            raise AssertionError("Rejected mesh mode unexpectedly produced output")


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: test_m3_dispatch.py PATH_TO_AP_MESH")
    executable = Path(sys.argv[1]).resolve()
    if not executable.is_file():
        raise FileNotFoundError(executable)
    cases = [
        ("MESH_ELEMENT_KIND=quad_uv\n", "requires an approved interior-point policy", "y"),
        ("MESH_ELEMENT_KIND=quad_uv\n", "requires an approved interior-point policy", "n"),
        ("MESH_ELEMENT_KIND=quad\n", "Unsupported configuration value for MESH_ELEMENT_KIND", "y"),
        ("MESH_ELEMENT_KIND=TRI\n", "Unsupported configuration value for MESH_ELEMENT_KIND", "y"),
        ("MESH_ELEMENT_KIND=\n", "Empty configuration value for MESH_ELEMENT_KIND", "y"),
        ("MESH_ELEMENT_KIND=tri\nMESH_ELEMENT_KIND=tri\n", "Duplicate configuration key: MESH_ELEMENT_KIND", "y"),
        ("UNKNOWN_MESH_SELECTOR=quad_uv\n", "Unknown configuration key", "y"),
    ]
    for extra, expected, template in cases:
        run_case(executable, extra, expected, template)
    print(f"m3_dispatch_rejection_cases={len(cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
