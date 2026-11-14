"""Run deterministic mesh-quality analysis without a GUI or VTK dependency."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .import_obj import import_obj
from .metric2d import Metric2D
from .quality_analysis import analyze_mesh


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit original TRI/QUAD geometry and indexed topology")
    parser.add_argument("obj", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--metric-diagonal", type=float, nargs=2, metavar=("MU", "MV"))
    args = parser.parse_args(argv)
    metric = Metric2D(args.metric_diagonal[0],0,args.metric_diagonal[1]) if args.metric_diagonal else None
    report = analyze_mesh(import_obj(args.obj),metric_field=metric,metric_frame="uv" if metric else None)
    if metric is not None:
        report["metric_provenance"]="USER_SUPPLIED_NOT_ORIGINAL_GENERATOR_FIELD"
    data = json.dumps(report, indent=2, sort_keys=True,allow_nan=False)+"\n"
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(data,encoding="utf-8")
    print(json.dumps({"output":str(args.output),"cells":report["cell_inventory"],"synthetic":report["synthetic"]},sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
