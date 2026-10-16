#!/usr/bin/env python3
"""Validate measured compatibility; empty coverage never proves conformity."""

import argparse
import csv
import math
from pathlib import Path


def validate(path: Path, tolerance: float = 0.0) -> int:
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("Tolerance must be finite and nonnegative")
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError("Compatibility report contains no observations")
    for row in rows:
        compared = int(row["compared_groups"])
        desynchronized = int(row["desynchronized_groups"])
        mean = float(row["compat_error_mean"])
        maximum = float(row["compat_error_max"])
        if compared <= 0:
            raise ValueError("Compatibility is unmeasured: compared_groups <= 0")
        if desynchronized != 0:
            raise ValueError("Desynchronized or invalid group count")
        if not all(math.isfinite(value) and value >= 0 for value in [mean, maximum]):
            raise ValueError("Compatibility errors must be finite and nonnegative")
        if mean > maximum or maximum > tolerance:
            raise ValueError("Compatibility error exceeds the declared tolerance or is inconsistent")
    return len(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--tolerance", type=float, default=0.0)
    args = parser.parse_args()
    try:
        print(f"Validated {validate(args.report, args.tolerance)} measured report rows")
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Compatibility validation failed: {error}\n")
