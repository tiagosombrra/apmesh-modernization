"""Run the portable native feedback trial on the two development geometries."""

import argparse
from pathlib import Path
import sys

from audit_model_catalog import parse_bp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from quad_portable_feedback_trial import run


def ribbed_fixture(destination):
    raw = (ROOT / "input_models/ribbed_bracket_nm_decor.bp").read_text(encoding="utf-8")
    points, patches = parse_bp(raw)
    controls = [points[i] for i in patches[12]]
    records = ["v " + " ".join(format(x, ".17g") for x in point) for point in controls]
    records.append("p " + " ".join(map(str, range(16))))
    destination.write_text("\n".join(records) + "\n", encoding="ascii")
    return str(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    exe = args.exe.resolve(strict=True)
    directory = args.directory.resolve()
    directory.mkdir(parents=True)
    cases = (("curva", "builtin:curva_bezier", 3, False),
             ("ribbed", ribbed_fixture(directory / "ribbed original patch.bp"), 2, True))
    image = None
    for name, model, step, negative in cases:
        result = run(exe, directory / name, model, step, negative)
        successor = result["successor"]
        if image is not None and image != result["engine_sha256"]:
            raise ValueError("Development cases used different application images")
        image = result["engine_sha256"]
        if (successor["status"] != "staged" or successor["segments_after"] <= successor["segments_before"]
                or successor["requests"] <= 0 or successor["direct_leaf_edits"] <= 0
                or result["mixed_adaptive_epochs"] != 0
                or (negative and result.get("foreign_tree_control") != "rejected_before_feedback")):
            raise ValueError(f"Missing portable native feedback evidence for {name}: {successor}")
        print(name, result["source_sha256"], successor, flush=True)

    quiet = run(exe, directory / "relative-no-action", cases[1][1], cases[1][2],
                relative_tolerance=1)
    if (quiet["successor"]["status"] != "no_action" or quiet["face_requests"]
            or quiet["curve_requests"] or quiet["mixed_adaptive_epochs"] != 0
            or (directory / "relative-no-action/successor.steps").exists()
            or quiet["source_sha256"] != result["source_sha256"]):
        raise ValueError("Relative threshold control did not retain only the original source")
    print("relative-no-action", quiet["source_sha256"], quiet["successor"], flush=True)


if __name__ == "__main__":
    main()
