"""Headless versioned experiment-run validation and scientific-eligibility audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .experiment_ingest import (ExperimentIngestError, qualify_experiment,
                                scientific_matrix_from_qualified)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--repository-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    # Validation must complete before opening any output file.
    try:
        result = qualify_experiment(args.manifest, repository_root=args.repository_root)
        matrix = scientific_matrix_from_qualified((result,))
    except (ExperimentIngestError, OSError, ValueError) as exc:
        parser.exit(2, f"Experiment rejected: {exc}\n")
    if args.output_dir.exists():
        parser.error("output directory already exists; overwrite is not allowed")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / "qualified_run.json").write_text(
        json.dumps(result.as_receipt(), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n")
    (args.output_dir / "scientific_matrix.json").write_text(
        json.dumps(matrix, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps({"grade": result.evidence_grade, "run_id": result.run_id,
                      "comparison_eligible": result.figure_comparison_eligible,
                      "output_dir": str(args.output_dir)}, sort_keys=True))


if __name__ == "__main__":
    main()
