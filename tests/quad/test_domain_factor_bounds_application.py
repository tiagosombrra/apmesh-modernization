"""Compare the opt-in domain-factor repair with the original native workflow."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import uuid

from test_controlled_application import require
from test_real_boundary_application import audit, audit_history, negative_controls
from boundary_pair_inventory import audit_pair_inventory


def run(exe, directory, name, bounded, coarse, rollback=False):
    prefix = directory / name
    root = Path(__file__).resolve().parents[2]
    text = (root / "configs/quad/curved_patch_original_curves.conf").read_text()
    text = text.replace("OUTPUT_PREFIX=build/quad_original_curves",
                        "OUTPUT_PREFIX=" + prefix.as_posix())
    if bounded:
        text = text.replace("curved_bezier_original_curves_vertex_mean_v1",
                            "curved_bezier_bounded_domain_vertex_mean_v1")
    if coarse:
        text += "\nPATCH_FACTOR_MIN=1.5\nPATCH_FACTOR_MAX=1.5\n"
    if rollback:
        text += "\nQUAD_VERIFY_ROLLBACK=1\n"
    conf = prefix.with_suffix(".conf")
    conf.write_text(text)
    command = [str(exe), "--config", str(conf)]
    process = subprocess.run(command, cwd=directory, capture_output=True, timeout=180)
    prefix.with_suffix(".stdout").write_bytes(process.stdout)
    prefix.with_suffix(".stderr").write_bytes(process.stderr)
    require(process.returncode == int(rollback),
            f"Domain-bound application failed: {name}, exit={process.returncode}, {directory}")
    archive = Path(str(prefix) + ".steps")
    manifest = list(csv.DictReader((archive / "manifest.csv").open()))
    require([int(row["step"]) for row in manifest] == [0, 1, 2, 3],
            "Incomplete domain-bound generation history")
    accepted = [row for row in manifest if row["reference_tri_accepted"] == "1"]
    require(prefix.with_suffix(".obj").read_bytes() ==
            (archive / accepted[-1]["quad_tri_obj"]).read_bytes(),
            "Primary output lost its last accepted TRI source")
    trace = list(csv.DictReader((archive / "curve_stages.csv").open()))
    for final in (row for row in trace if row["stage"] == "final_budget"):
        surface = [row for row in trace if row["stage"] == "surface_pass" and
                   all(row[key] == final[key] for key in ("step", "epoch", "retry", "curve"))]
        require(len(surface) == 1 and surface[0]["parameters"] == final["parameters"],
                "Research repair clipped original curve parameters")
    records = []
    for row in manifest[1:]:
        for key in ("tri_obj", "quad_tri_obj"):
            record = audit(archive / row[key])
            require(record["reference_tri_accepted"] == bool(int(row["reference_tri_accepted"])),
                    "OBJ source acceptance disagrees with manifest")
            if key == "quad_tri_obj":
                records.append(record)
    domain = list(csv.DictReader(Path(str(prefix) + "_domain_adaptation.csv").open()))
    factors = {int(row["step"]): float(row["factor_disc_global"]) for row in domain}
    objects = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in archive.glob("*.obj")}
    if not coarse:
        audit_history(prefix, "original_curvature")
    if coarse and bounded:
        require(factors[1] == 1.5 and factors[2] == 1.5,
                "Configured factor bounds were bypassed at domain generation")
        negatives = directory / (name + "-negative")
        negatives.mkdir()
        require(negative_controls(archive / manifest[2]["quad_tri_obj"], negatives) == 9,
                "Source/topology corruption controls were not executed")
    if rollback:
        require(b"QUAD_REAL_BOUNDARY_ROLLBACK previous_nonempty=1 preserved=1" in process.stdout,
                "Missing nonempty owner rollback witness")
    pair_inventory = audit_pair_inventory(archive)
    pair_negatives = 0
    if coarse and bounded:
        require(sum(row["topology_candidates"] for row in pair_inventory) > 0,
                "Missing actual AFT pair coverage")
        original_pairs = (archive / "boundary_pair_candidates.csv").read_bytes()
        with (archive / "boundary_pair_candidates.csv").open() as stream:
            reader = csv.DictReader(stream)
            fields, original_rows = reader.fieldnames, list(reader)
        for index, alteration in enumerate(("selection_status", "step", "quad_a", "duplicate")):
            rows = [dict(row) for row in original_rows]
            if alteration == "duplicate":
                rows.append(dict(rows[0]))
            else:
                rows[0][alteration] = {"selection_status": "selected", "step": "999999",
                                       "quad_a": "999999999"}[alteration]
            forged = directory / f"{name}-pair-negative-{index}.csv"
            with forged.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            try:
                audit_pair_inventory(archive, forged)
            except AssertionError:
                pair_negatives += 1
            else:
                raise AssertionError("Forged boundary pair inventory was accepted")
        require((archive / "boundary_pair_candidates.csv").read_bytes() == original_pairs,
                "Pair audit changed original diagnostics")
    return {"objects": objects, "domain_factors": factors, "mixed_steps": records,
            "pair_inventory": pair_inventory,
            "pair_inventory_negative_controls": pair_negatives,
            "accepted_steps": [int(row["step"]) for row in accepted]}, archive


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--directory", required=True, type=Path)
    args = parser.parse_args()
    out = args.directory.resolve() / ("run-" + uuid.uuid4().hex)
    out.mkdir(parents=True)
    results = {}
    for name, bounded, coarse, rollback in (
            ("original-default", False, False, False),
            ("bounded-default", True, False, False),
            ("original-coarse", False, True, False),
            ("bounded-coarse", True, True, False),
            ("bounded-rollback", True, True, True)):
        results[name], _ = run(args.exe.resolve(), out, name, bounded, coarse, rollback)
    require(results["original-default"] == results["bounded-default"],
            "Repair changed the original in-range control")
    require(results["bounded-coarse"] == results["bounded-rollback"],
            "Rollback changed the bounded-domain results")
    old, new = results["original-coarse"], results["bounded-coarse"]
    require(old["domain_factors"][2] == 1.0,
            "Missing original step2 bound-violation witness")
    require(old["mixed_steps"][0] == new["mixed_steps"][0],
            "Repair changed the first step before the conflicting override")
    require(new["mixed_steps"][1]["nodes"] < old["mixed_steps"][1]["nodes"],
            "Bounded factor did not reduce the reproduced step2 growth")
    report = {"schema": "apmesh.quad.domain_factor_bounds.v1", "cases": results,
              "mixed_adaptive_epochs": 0, "scientific_adoption": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
