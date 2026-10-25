#!/usr/bin/env python3
"""Check attempt exports against mesh counts and native acceptance observations."""

import argparse
import csv
import json
import math
from pathlib import Path

from verify_generation import inspect_mesh, read_acceptance

LOG_NAMES = {"elements_prev": "elements_previous", "error_prev": "error_global_previous"}


def number(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Non-finite attempt metric")
    return result


def one(paths):
    paths = list(paths)
    if len(paths) != 1:
        raise ValueError("Expected exactly one artifact per attempt")
    return paths[0]


def audit(root):
    with one(root.glob("*_metrics_rank_-1.csv")).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("Missing or duplicate metrics header")
        rows = list(reader)
    if not rows:
        raise ValueError("No attempt observations")
    differences, accepted_steps, rejected_steps = [], [], []
    previous_elements = None
    previous_error = None
    compared = 0
    for step, row in enumerate(rows):
        if None in row or any(value is None for value in row.values()) or row["step"] != str(step):
            raise ValueError("Malformed or nonconsecutive attempt row")
        acceptance = read_acceptance(one(root.glob(f"*_passo_{step}_acceptance_*.log")))
        accepted = acceptance["accepted"] == "1"
        if acceptance["step"] != str(step) or acceptance["accepted"] not in ("0", "1") or (step == 0 and not accepted):
            raise ValueError("Invalid attempt acceptance state")
        count = inspect_mesh(one(root.glob(f"*_passo_{step}_malha_{step}.obj")))["triangles"]
        analysis = {}
        names = {"elements_previous", "elements_delta", "element_growth_factor", "actual_element_growth",
                 "actual_growth_step", "acceptance_score", "error_global_previous"}
        for line in one(root.glob(f"*_passo_{step}_qualite_{step}_rank_-1.log")).read_text(encoding="utf-8").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                if key in names:
                    if key in analysis:
                        raise ValueError("Duplicate attempt analysis field")
                    analysis[key] = value
        if step == 0:
            previous_elements, previous_error = count, number(row["error"])
        delta = max(count - previous_elements, 0)
        growth = count / previous_elements
        expected = {"elements_prev": previous_elements, "elements_delta": delta,
                    "element_growth_factor": growth, "actual_element_growth": growth,
                    "actual_growth_step": growth, "acceptance_score": number(acceptance["acceptance_score"]),
                    "error_prev": previous_error}
        for field, value in expected.items():
            for kind, actual in (("csv", row[field]), ("analysis", analysis[LOG_NAMES.get(field, field)])):
                compared += 1
                matches = (number(actual) == value if field in ("elements_prev", "elements_delta")
                           else math.isclose(number(actual), value, rel_tol=1e-5, abs_tol=1e-6))
                if not matches:
                    differences.append({"step": step, "field": field, "export": kind,
                                        "actual": number(actual), "expected": value})
        for kind, actual in (("csv", row["elements"]), ("acceptance", acceptance["element_growth_factor"])):
            expected_value = count if kind == "csv" else growth
            compared += 1
            matches = (number(actual) == expected_value if kind == "csv"
                       else math.isclose(number(actual), expected_value, rel_tol=1e-5, abs_tol=1e-6))
            if not matches:
                differences.append({"step": step, "field": "elements" if kind == "csv" else "element_growth_factor",
                                    "export": kind, "actual": number(actual), "expected": expected_value})
        if accepted:
            previous_elements, previous_error = count, number(row["error"])
            accepted_steps.append(step)
        else:
            rejected_steps.append(step)
    return {"status": "failed" if differences else "passed", "attempts": len(rows),
            "accepted_steps": accepted_steps, "rejected_steps": rejected_steps,
            "compared_values": compared, "differences": differences,
            "limits": "Curvature errors are not independently recomputed; retry/count fields have exporter fixture controls."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = audit(args.run)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({key: value for key, value in report.items() if key != "differences"}))
        raise SystemExit(0 if report["status"] == "passed" else 1)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Attempt metric audit failed: {error}\n")
