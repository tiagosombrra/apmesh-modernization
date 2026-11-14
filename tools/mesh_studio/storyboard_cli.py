"""Command-line entry point for reproducible synthetic method storyboards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .storyboards import (render_all_quad_parity, render_anisotropy_story,
                          render_hybrid_story)

DEFAULT_HYBRID = Path(__file__).resolve().parent / "fixtures" / "cases" / "synthetic_quad_aft_transition.obj"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Produce synthetic method figures (SVG)")
    parser.add_argument("type", choices=("hybrid", "all-quad", "anisotropy", "all"))
    parser.add_argument("--output-dir", type=Path, default=Path("mesh_studio_figures"))
    parser.add_argument("--hybrid-fixture", type=Path, default=DEFAULT_HYBRID)
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    types = ("hybrid", "all-quad", "anisotropy") if args.type == "all" else (args.type,)
    outputs = {}
    for type_ in types:
        path = args.output_dir / (type_.replace("-", "_") + "_synthetic.svg")
        receipt = (render_hybrid_story(args.hybrid_fixture, path) if type_ == "hybrid" else
                   render_all_quad_parity(path) if type_ == "all-quad" else
                   render_anisotropy_story(path))
        outputs[type_] = {"svg": str(path), "sha256": receipt["svg_sha256"],
                          "panel_count": receipt["panel_count"],
                          "provenance": receipt["provenance"]}
    print(json.dumps(outputs, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
