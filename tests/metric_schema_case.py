#!/usr/bin/env python3
"""Audit an actual executable's metric columns using an analytic aligned case."""

import argparse
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_metric_schema import audit
from boundary_orientation_case import run_control


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    args.workspace.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="run-", dir=args.workspace)).resolve()
    control = run_control(args.exe.resolve(), workspace, "aligned", False, 2)
    report = audit(workspace / "aligned")
    report["geometry_control"] = control["status"]
    report_path = workspace / "metric_schema_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "geometry_control": control["status"],
                      "differences": len(report["differences"]), "report": str(report_path)}))
    raise SystemExit(0 if report["status"] == "passed" and control["status"] == "passed" else 1)
