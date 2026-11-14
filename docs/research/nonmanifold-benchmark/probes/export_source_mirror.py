"""Locally reconstruct pinned Fusion Energy CadQuery input examples for screening.

Source mirror, not execution of the upstream repository; run in isolated R&D.
Pinned upstream: fusion-energy/model_benchmark_zoo@3a2e69fe62209e33a1e176d816609d69a2aebadc
"""
import argparse
from pathlib import Path
import json
import cadquery as cq
from step_structural_screen import screen


def make_assembly(name: str):
    """Mirror upstream cadquery_assembly construction and default parameters."""
    assy = cq.Assembly(name=name)
    if name == "three_touching_cuboids":
        w = 5.0
        for xyz in [(-w/2, w/2, 0), (w/2, w/2, 0), (-w/2, -w/2, 0)]:
            assy.add(cq.Workplane().transformed(offset=xyz).box(w, w, w))
    elif name == "t_junction":
        assy.add(cq.Workplane("XY").box(20, 5, 5))
        assy.add(cq.Workplane("XY").transformed(offset=(0, 7.5, 0)).box(5, 10, 5))
    elif name == "cross_junction":
        assy.add(cq.Workplane("XY").box(20, 4, 4))
        for y in (6, -6):
            assy.add(cq.Workplane("XY").transformed(offset=(0, y, 0)).box(4, 8, 4))
    elif name == "two_touching_cuboids":
        assy.add(cq.Workplane().box(10, 10, 10))
        assy.add(cq.Workplane().transformed(offset=(0, 7, 0)).box(10, 4, 10))
    elif name == "tangent_spheres":
        assy.add(cq.Workplane("XY").transformed(offset=(-5, 0, 0)).sphere(5))
        assy.add(cq.Workplane("XY").transformed(offset=(4, 0, 0)).sphere(4))
    else:
        raise ValueError(name)
    return assy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cases = (
        "three_touching_cuboids", "t_junction", "cross_junction",
        "two_touching_cuboids", "tangent_spheres"
    )
    for name in cases:
        path = args.output_dir / (name + ".step")
        make_assembly(name).export(str(path), exportType="STEP")
        report = screen(path.read_text(encoding="utf-8"))
        print(json.dumps({
            "model": name,
            "local_export_bytes": path.stat().st_size,
            "source_reproduction": "MIRRORED_UPSTREAM_DEFAULT_GEOMETRY",
            "step_structural_screen": report,
        }, sort_keys=True))


if __name__ == "__main__":
    main()
