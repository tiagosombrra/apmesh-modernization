#!/usr/bin/env python3
"""Compare nonempty live patch/incidence/scalar traces before retirement."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

from audit_hermite_observers import audit


def compare(original, candidate, original_root, candidate_root, output, runtime):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    preservation = audit(candidate_root, original_root)
    environment = os.environ.copy()
    environment["PATH"] = str(runtime.resolve()) + os.pathsep + environment.get("PATH", "")
    environment["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
    cases = []
    for layout in range(3):
        for shape in range(2):
            mode = f"trace-{layout}-{shape}"
            observations, invocations = {}, {}
            for label, executable in [("original", original), ("candidate", candidate)]:
                log = output / f"{label}-{mode}.log"
                with log.open("xb") as stream:
                    process = subprocess.run([str(executable.resolve()), mode], cwd=output,
                        env=environment, stdout=stream, stderr=subprocess.STDOUT, timeout=30)
                data = log.read_bytes()
                if process.returncode or b"PASS" not in data or b"ERROR: AddressSanitizer:" in data:
                    failure = {"status": "failed", "label": label, "mode": mode,
                               "exit_code": process.returncode, "log": log.name,
                               "log_sha256": hashlib.sha256(data).hexdigest()}
                    (output / "failure.json").write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
                    raise ValueError(f"Failed actual live trace: {label}-{mode}; exit {process.returncode}")
                rows = [line for line in data.decode("utf-8").splitlines() if line.startswith("observer_")]
                for prefix, count in [("observer_live_patch=", 96), ("observer_incidence=", 384),
                                      ("observer_scalar=", 6048)]:
                    if sum(line.startswith(prefix) for line in rows) != count:
                        raise ValueError(f"Incomplete positive trace: {label}-{mode}-{prefix}")
                observations[label] = rows
                invocations[label] = {"log": log.name, "exit_code": process.returncode,
                                      "sha256": hashlib.sha256(data).hexdigest()}
            if observations["original"] != observations["candidate"]:
                raise ValueError(f"Actual live numerical/incidence trace changed: {mode}")
            cases.append({"mode": mode, "observations": observations["candidate"],
                          "invocations": invocations})
    report = {"status": "passed", "paired_traces": len(cases), "live_patches": 576,
              "incidence_observations": 2304, "scalar_observations": 36288,
              "preservation": preservation, "cases": cases,
              "executables": {label: {"path": str(path.resolve()),
                                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                              for label, path in [("original", original), ("candidate", candidate)]},
              "scope": "Actual C++17 production units: three incidence layouts, two surfaces, all "
                       "constructor flag combinations and empty/populated prefixes. Parameterize/Qu/Qv/Quu/Quv/Qvu/Qvv scalar bits, "
                       "patch IDs and live incidence must match. Registrations are cleared while patches "
                       "are alive for the original comparison; destruction and Geometry order require "
                       "the separate memory campaign. Repeated curve slots are lifetime guards, not "
                       "geometric validity or scientific adequacy evidence."}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["original", "candidate", "original-root", "candidate-root", "output", "runtime"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = compare(args.original, args.candidate, args.original_root, args.candidate_root, args.output, args.runtime)
    print(json.dumps({key: result[key] for key in ["status", "paired_traces", "scalar_observations"]}))
