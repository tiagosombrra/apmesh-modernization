#!/usr/bin/env python3
"""Compare actual original/repaired curvature bits and sample order with GCC."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from audit_curvature_sample import audit


def compare(original, candidate, original_root, candidate_root, output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    preservation = audit(original_root, candidate_root)
    records = []
    # The original VLA is retained. Do not execute INT_MAX on that old stack.
    for shape in range(3):
        for count in [-1, 0, 3, 4, 5, 8, 9, 10, 16, 17, 18, 24, 25, 26, 100]:
            for repeats in [1, 3]:
                mode = f"normal-{shape}-{count}-{repeats}"
                traces, invocations = {}, {}
                for label, executable in [("original", original), ("candidate", candidate)]:
                    log = output / f"{label}-{mode}.log"
                    with log.open("xb") as stream:
                        process = subprocess.run([str(executable.resolve()), mode], cwd=output,
                            stdout=stream, stderr=subprocess.STDOUT, timeout=30)
                    data = log.read_bytes()
                    if process.returncode or b"PASS" not in data:
                        raise ValueError(f"Required actual sampler trace failed: {label}-{mode}")
                    traces[label] = [line for line in data.decode("utf-8").splitlines() if line.startswith("sample_")]
                    if sum(line.startswith("sample_result=") for line in traces[label]) != repeats:
                        raise ValueError("Missing sampler results")
                    invocations[label] = {"log": log.name, "exit_code": process.returncode,
                                         "sha256": hashlib.sha256(data).hexdigest()}
                if traces["original"] != traces["candidate"]:
                    raise ValueError(f"Changed ordered sample/inverse/scalar bit trace: {mode}")
                records.append({"mode": mode, "observations": traces["candidate"], "invocations": invocations})
    if len(records) != 90:
        raise ValueError("Incomplete paired sampler inventory")
    report = {"status": "passed", "paired_traces": len(records), "preservation": preservation,
              "scope": "GCC C++17 actual original VLA sampler versus actual repaired unit; 90 paired traces on 3 surfaces, all threshold regions, repeats and bounded out-of-range counts. Exact scalar bits and forward/inverse sample arguments. Original INT_MAX stack allocation is deliberately unmeasured. The original contains invalid downcasts; observed agreement is not original defined-behavior qualification.",
              "cases": records}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["original", "candidate", "original-root", "candidate-root", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = compare(args.original, args.candidate, args.original_root, args.candidate_root, args.output)
    print(json.dumps({"status": result["status"], "paired_traces": result["paired_traces"]}))
