"""Headless Mesh Studio command line entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .import_obj import import_obj
from .svg_figure import audit_svg, render_uv_svg, save_receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="APMesh Mesh Studio headless scientific importer")
    parser.add_argument("obj", type=Path, help="Wavefront OBJ file (optionally paired with synthetic JSON)")
    parser.add_argument("--sidecar", type=Path, help="Explicit source sidecar JSON")
    parser.add_argument("--svg", type=Path, help="Create a pure vector UV figure")
    parser.add_argument("--width-mm", type=float, default=155.0)
    parser.add_argument("--height-mm", type=float, default=120.0)
    args = parser.parse_args(argv)
    document = import_obj(args.obj, args.sidecar)
    summary = {"source_name": document.source_name, "source_sha256": document.source_sha256,
               "synthetic": document.synthetic, "source_kind": document.source_kind,
               "triangles": document.triangles, "quads": document.quads,
               "vertices": len(document.points), "groups": list(document.groups),
               "source_curves": len(document.source_curves)}
    if args.svg:
        receipt = render_uv_svg(document, args.svg,
                                width_mm=args.width_mm, height_mm=args.height_mm)
        receipt.update(audit_svg(args.svg, expected_faces=len(document.faces)))
        save_receipt(receipt, args.svg.with_suffix(".audit.json"))
        summary["vector_figure"] = str(args.svg)
        summary["vector_audit"] = receipt["vector_only"]
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
