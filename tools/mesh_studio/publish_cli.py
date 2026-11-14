"""Render a bound real P1 figure for LaTeX without Qt or OpenGL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .publication import export_p1_paper_figure


def main(argv: list[str] | None = None) -> int:
    root=Path(__file__).parent/'fixtures'/'real_p1'
    p=argparse.ArgumentParser(description='Export real-source audited 2D paper figure')
    p.add_argument('--obj',type=Path,default=root/'accepted.obj')
    p.add_argument('--generator-report',type=Path,default=root/'generator_report.json')
    p.add_argument('--output-dir',required=True,type=Path)
    args=p.parse_args(argv)
    print(json.dumps(export_p1_paper_figure(args.obj,args.generator_report,args.output_dir),
                     sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
