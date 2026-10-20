#!/usr/bin/env python3
"""Compare nonempty charge traces and unchanged actual numerical helper bodies."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from qualify_charge_input import fixtures


def compare(original, candidate, original_root, candidate_root, output, kind):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    paths, _ = fixtures(output)
    source_names = ["double ChargeEstimateProcess::CalculateKaMedioPatch(",
                    "double ChargeEstimateProcess::CalculateAreaPatch(",
                    "double ChargeEstimateProcess::CalculateAreaTriangleMedioRad("]
    helper_bodies = {}
    for label, root in [("original", original_root), ("candidate", candidate_root)]:
        source = (root / "src/estimate/charge_estimate_process.cpp").read_text(encoding="utf-8")
        source = source[source.index(source_names[0]):source.index("long ChargeEstimateProcess::CalculateNumbersTriangle(")]
        helper_bodies[label] = hashlib.sha256(source.encode()).hexdigest()
    if helper_bodies["original"] != helper_bodies["candidate"]:
        raise ValueError("Numerical helper bodies changed; review the comparison scope")
    records = []
    for shape, path in enumerate(paths):
        for seed in range(2):
            for mode in ["normal", "repeat", "writer"]:
                scenario = f"{mode}-{shape}-{seed}"
                traces, artifacts = {}, {}
                invocations = {}
                for label, executable in [("original", original), ("candidate", candidate)]:
                    directory = output / f"{label}-{scenario}"
                    directory.mkdir()
                    log = directory / "run.log"
                    with log.open("xb") as stream:
                        process = subprocess.run([str(executable.resolve()), scenario, str(path)],
                                                 cwd=directory, stdout=stream, stderr=subprocess.STDOUT,
                                                 timeout=30)
                    data = log.read_bytes()
                    if process.returncode or b"PASS" not in data:
                        raise ValueError(f"Required {kind} trace failed: {label}-{scenario}")
                    traces[label] = [line for line in data.decode("utf-8").splitlines() if line.startswith("charge_")]
                    counts = 1 if shape < 2 else 3
                    repeats = 3 if mode == "repeat" else 1
                    if sum(line.startswith("charge_control=") for line in traces[label]) != 16 * counts * repeats:
                        raise ValueError("Missing positive control-point observations")
                    artifacts[label] = {file.name: hashlib.sha256(file.read_bytes()).hexdigest()
                                        for file in directory.glob("*_analise_curvature_patches.log")}
                    if mode == "writer" and len(artifacts[label]) != 1:
                        raise ValueError("Writer produced no comparable report")
                    invocations[label] = {"log": str(log.relative_to(output)),
                                          "sha256": hashlib.sha256(data).hexdigest(), "exit_code": process.returncode}
                if traces["original"] != traces["candidate"] or artifacts["original"] != artifacts["candidate"]:
                    raise ValueError(f"Changed {kind} ordered scalar/control/incidence/writer trace: {scenario}")
                records.append({"scenario": scenario, "observations": traces["candidate"],
                                "artifacts": artifacts["candidate"], "invocations": invocations})
    if len(records) != 24:
        raise ValueError("Incomplete nonempty paired trace inventory")
    report = {"status": "passed", "kind": kind, "paired_traces": len(records),
              "numerical_helper_sha256": helper_bodies,
              "scope": "24 original/repaired normal/repeated/writer invocations, four valid positive BP fixtures and two initial Geometry layouts. Exact control coordinates/IDs, curve incidence, stable returned order, scalar IEEE bits, retained curvatures count and actual writer bytes. The actual kind compiles the full unchanged numerical estimator unit with GCC; this is numerical correspondence, not helper scratch memory or undefined-behavior qualification. The controlled kind forces existing member results only in its test target. No scientific policy change or malformed-input qualification.",
              "executables": {label: {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                              for label, path in [("original", original), ("candidate", candidate)]},
              "cases": records}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ["original", "candidate", "original-root", "candidate-root", "output"]:
        parser.add_argument("--" + flag, type=Path, required=True)
    parser.add_argument("--kind", choices=["actual", "controlled"], required=True)
    args = parser.parse_args()
    result = compare(args.original, args.candidate, args.original_root, args.candidate_root, args.output, args.kind)
    print(json.dumps({"status": result["status"], "kind": result["kind"], "paired_traces": result["paired_traces"]}))
