#!/usr/bin/env python3
"""Compare actual original/repaired constructor control and numerical traces."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from audit_bezier_construction import audit


def compare(original, candidate, original_root, candidate_root, output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    preservation = audit(original_root, candidate_root)
    records = []
    for kind in range(4):
        for shape in range(2):
            for seed in range(2):
                mode = f"normal-{kind}-{shape}-{seed}"
                traces, invocations = {}, {}
                for label, executable in [("original", original), ("candidate", candidate)]:
                    log = output / f"{label}-{mode}.log"
                    with log.open("xb") as stream:
                        process = subprocess.run([str(executable.resolve()), mode], cwd=output,
                            stdout=stream, stderr=subprocess.STDOUT, timeout=30)
                    data = log.read_bytes()
                    if process.returncode or b"PASS" not in data:
                        raise ValueError(f"Required constructor trace failed: {label}-{mode}")
                    traces[label] = [line for line in data.decode("utf-8").splitlines() if line.startswith("bezier_")]
                    if sum(line.startswith("bezier_scalar=") for line in traces[label]) != 864:
                        raise ValueError("Missing positive numerical observations")
                    if sum(line.startswith("bezier_control=") for line in traces[label]) != 512:
                        raise ValueError("Missing control coordinate/ID observations")
                    invocations[label] = {"log": log.name, "exit_code": process.returncode,
                                         "sha256": hashlib.sha256(data).hexdigest()}
                if traces["original"] != traces["candidate"]:
                    raise ValueError(f"Changed actual control/direction/incidence/scalar trace: {mode}")
                records.append({"mode": mode, "observations": traces["candidate"], "invocations": invocations})
    if len(records) != 16:
        raise ValueError("Incomplete paired constructor inventory")
    report = {"status": "passed", "paired_traces": len(records), "constructor_calls_per_executable": 512,
        "scalar_observations": 13824, "control_observations": 8192, "preservation": preservation,
        "cases": records, "executables": {label: {"path": str(path.resolve()),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for label, path in [("original", original), ("candidate", candidate)]},
        "scope": "Actual GCC C++17 constructors/dependencies, 16 paired scenarios each containing all16 direction masks and two successive constructions. Exact curve control coordinates/IDs, direction flags, live observer checks, Parameterize/Qu/Qv scalar bits. Repeated slots are lifetime guards, not geometric validity; no analytic validity, performance, ordinary destruction/deregistration or whole-process qualification follows."}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["original", "candidate", "original-root", "candidate-root", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    r = compare(args.original, args.candidate, args.original_root, args.candidate_root, args.output)
    print(json.dumps({"status": r["status"], "paired_traces": r["paired_traces"], "scalar_observations": r["scalar_observations"]}))
