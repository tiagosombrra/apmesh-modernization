#!/usr/bin/env python3
"""Cross-check CSV control columns against their named per-stage analysis log."""

import argparse
import csv
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path

CONTROL_FIELDS = (
    "adaptation_relaxation", "retry_enabled", "local_budget_mode", "target_element_growth",
    "target_elements_step", "actual_elements_step", "target_growth_step", "actual_growth_step",
    "actual_element_growth", "step_efficiency", "local_progress_coverage", "improved_top_patches",
    "top_patch_candidate_count", "generation_control_mode", "consistency_regularization_active",
    "patch_budget_dispersion", "patch_h_dispersion", "actual_patch_element_dispersion",
    "curve_balance_dispersion", "patch_consistency_penalty", "budget_driver_mode",
)


def equal_value(first, second):
    try:
        a, b = Decimal(first), Decimal(second)
        return a.is_finite() and b.is_finite() and a == b
    except InvalidOperation:
        return first == second


def audit(root: Path):
    paths = list(root.glob("*_metrics_rank_-1.csv"))
    if len(paths) != 1:
        raise ValueError("Expected exactly one serial metrics CSV")
    with paths[0].open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("Missing or duplicate metrics header")
        rows = list(reader)
    if not rows:
        raise ValueError("No metric rows to audit")
    differences, seen = [], set()
    for row in rows:
        step = int(row["step"])
        if step in seen or step < 0 or None in row or any(v is None for v in row.values()):
            raise ValueError("Malformed or duplicate metric row")
        seen.add(step)
        logs = list(root.glob(f"*_passo_{step}_qualite_{step}_rank_-1.log"))
        if len(logs) != 1:
            raise ValueError("Expected one named analysis log per metric row")
        values = {}
        for line in logs[0].read_text(encoding="utf-8").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                if key in CONTROL_FIELDS:
                    if key in values:
                        raise ValueError("Ambiguous analysis field")
                    values[key] = value
        for key in CONTROL_FIELDS:
            if key not in row or key not in values:
                raise ValueError(f"Missing control field {key}")
            if not equal_value(row[key], values[key]):
                differences.append({"step": step, "field": key, "csv": row[key], "analysis_log": values[key]})
    return {"status": "failed" if differences else "passed", "rows": len(rows),
            "compared_fields": len(rows) * len(CONTROL_FIELDS), "differences": differences}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = audit(args.run)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({k: v for k, v in report.items() if k != "differences"}))
        raise SystemExit(0 if report["status"] == "passed" else 1)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Metric schema audit failed: {error}\n")
