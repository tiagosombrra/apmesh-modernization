"""Headless publication-preview CLI: true source mesh, raster 3D PNG only."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .import_obj import import_obj
from .scene_model import initial_scene, load_scene, with_visibility
from .scene_vtk import screenshot_3d


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Render an explicitly rasterized 3D source mesh PNG')
    parser.add_argument('obj', type=Path)
    parser.add_argument('--png', type=Path, required=True)
    parser.add_argument('--scene', type=Path)
    parser.add_argument('--hide-tri', action='store_true')
    parser.add_argument('--hide-quad', action='store_true')
    parser.add_argument('--no-edges', action='store_true')
    parser.add_argument('--width', type=int, default=1100)
    parser.add_argument('--height', type=int, default=830)
    args = parser.parse_args(argv)
    try:
        doc = import_obj(args.obj)
        state = (load_scene(args.scene, doc) if args.scene is not None
                 else initial_scene(doc))
        state = with_visibility(doc, state,
                                triangles=False if args.hide_tri else None,
                                quads=False if args.hide_quad else None,
                                edges=False if args.no_edges else None)
        result = screenshot_3d(doc, args.png, state=state,
                               width=args.width, height=args.height)
        print(f"RASTER_3D_PNG cells={result['visible_cells']} "
              f"sha256={result['png_sha256']} output={args.png}")
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'Render failed: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
