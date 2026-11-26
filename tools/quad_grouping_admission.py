"""Evaluate the conservative grouping rule on paired fixed-site reports.

This offline decision does not publish or accept an adaptive epoch.
"""
import argparse
import json
from math import isclose, isfinite
from pathlib import Path
from sys import float_info


def direction(before, after):
    if not all(isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)
               for value in (before, after)):
        raise ValueError("A comparison metric must be a finite number")
    if isclose(before, after, rel_tol=64 * float_info.epsilon, abs_tol=0):
        return 0
    return 1 if after > before else -1


def evaluate(coarse, fine):
    for side in ("baseline", "candidate"):
        if coarse[side]["sha256"] != fine[side]["sha256"]:
            raise ValueError("Sampling grids must describe the same mesh pair")
    if coarse["grid"] != 24 or fine["grid"] != 48 or coarse["region"] != fine["region"]:
        raise ValueError("Expected fixed 24 and 48 grids on the same region")
    old, new = coarse["baseline"], coarse["candidate"]
    vetoes = []
    disagreements = []
    errors = {}
    if not all(report["same_ordered_contour_edges"] is True for report in (coarse, fine)):
        vetoes.append("ordered_contour_changed")
    if direction(old["regional_shape"]["minimum_angle"], new["regional_shape"]["minimum_angle"]) != 1:
        vetoes.append("regional_minimum_angle_did_not_improve")
    for key in ("nodes", "faces", "max_adjacent_size_ratio", "max_regional_adjacent_size_ratio"):
        if direction(old[key], new[key]) > 0:
            vetoes.append(key + "_increased")
    for kind in ("TRI", "QUAD"):
        before = old["shape"]["by_kind"][kind]
        after = new["shape"]["by_kind"][kind]
        for metric in ("minimum_angle", "minimum_shape"):
            if before[metric] is None or after[metric] is None:
                vetoes.append(f"global_{kind}_{metric}_unavailable")
            elif direction(before[metric], after[metric]) < 0:
                vetoes.append(f"global_{kind}_{metric}_decreased")
    for region in ("regional_error", "global_error"):
        for metric in ("rms_source_area", "max_xyz"):
            key = f"{region}_{metric}"
            shifts = [direction(r["baseline"][region][metric], r["candidate"][region][metric])
                      for r in (coarse, fine)]
            errors[key] = shifts
            if shifts[0] != shifts[1]:
                disagreements.append(key)
            elif shifts[0] > 0:
                vetoes.append(key + "_increased")
    verdict = "reject" if vetoes else "inconclusive" if disagreements else "eligible"
    return dict(verdict=verdict, vetoes=vetoes, sampling_disagreements=disagreements,
                geometric_directions=errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("grid24", type=Path, help="Comparison report at grid 24")
    parser.add_argument("grid48", type=Path, help="Comparison report at grid 48")
    args = parser.parse_args()
    try:
        result = evaluate(json.loads(args.grid24.read_text(encoding="utf-8")),
                          json.loads(args.grid48.read_text(encoding="utf-8")))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
