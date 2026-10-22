#!/usr/bin/env python3
"""Compare nonempty live Model observations using actual original/candidate units."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

from audit_model_ownership import audit


def compare(original, candidate, original_root, candidate_root, output, runtime=None):
    output.mkdir(parents=True, exist_ok=False)
    environment = dict(os.environ)
    if runtime:
        environment["PATH"] = str(runtime.resolve()) + os.pathsep + environment.get("PATH", "")
    environment["ASAN_OPTIONS"] = "halt_on_error=1:abort_on_error=0:detect_leaks=0"
    cases = []
    for mode in ["lifetime"] + [f"trace-{i}" for i in range(4)]:
        invocations, observations = {}, {}
        for label, executable in [("original", original), ("candidate", candidate)]:
            child = subprocess.run([str(executable.resolve()), mode], env=environment,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
            log = label+"-"+mode+".log"
            (output/log).write_bytes(child.stdout)
            text = child.stdout.decode("utf-8", errors="replace")
            if child.returncode or "PASS" not in text or "ERROR: AddressSanitizer:" in text:
                raise ValueError("Live comparison child failed: "+log)
            observations[label] = [line for line in text.splitlines() if line.startswith("model_")]
            if not observations[label]:
                raise ValueError("Zero live Model observations: "+log)
            invocations[label] = {"log": log, "exit_code": child.returncode, "sha256": hashlib.sha256(child.stdout).hexdigest()}
        if observations["original"] != observations["candidate"]:
            raise ValueError("Model payload, coordinate, ID, adjacency, order or borrowing trace differs: "+mode)
        cases.append({"mode": mode, "invocations": invocations, "observations": observations["candidate"]})
    report = {"status": "passed", "paired_traces": len(cases), "cases": cases,
              "executables": {label: {"path": str(executable.resolve()), "sha256": hashlib.sha256(executable.read_bytes()).hexdigest()}
                              for label, executable in [("original", original), ("candidate", candidate)]},
              "preservation": audit(candidate_root, original_root),
              "scope": "Original raw API and candidate raw API with empty/seeded/nonempty/null inputs, actual coordinates/IDs, analytic area, live local adjacency, borrowed geometry and reverse lifetime. Candidate owning handoffs and moves are separately instrumented. No whole-application or parallel claim."}
    (output/"report.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ["original", "candidate", "original-root", "candidate-root", "output"]:
        parser.add_argument("--"+flag, type=Path, required=True)
    parser.add_argument("--runtime", type=Path)
    args = parser.parse_args()
    report = compare(args.original, args.candidate, args.original_root, args.candidate_root, args.output, args.runtime)
    print(json.dumps({"status": report["status"], "paired_traces": report["paired_traces"]}))
