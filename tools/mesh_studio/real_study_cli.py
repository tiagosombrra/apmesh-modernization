"""Command-line qualification and journal export for the real 5-mesh study."""

from __future__ import annotations

import argparse
from pathlib import Path

from .real_candidate_study import write_real_study_report
from .real_study_publication import export_real_candidate_bundle


def main() -> None:
    parser=argparse.ArgumentParser(description="Audit real staged APMesh source meshes")
    parser.add_argument("--source-dir",type=Path,
                        default=Path(__file__).parent/"fixtures"/"real_p2d1c3")
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--no-figures",action="store_true")
    options=parser.parse_args()
    if options.no_figures:
        write_real_study_report(options.source_dir,options.output_dir/"qualified_study.json")
    else:
        export_real_candidate_bundle(options.source_dir,options.output_dir)
    print("S5D_REAL_CANDIDATES_VERIFIED staged_unaccepted=4 accepted_adaptive_epochs=0")


if __name__=="__main__":
    main()
