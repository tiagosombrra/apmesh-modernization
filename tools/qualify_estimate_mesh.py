#!/usr/bin/env python3
"""Qualify estimator mesh construction and unpublished resource ownership."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def qualify_iterations(reference, output):
    """Compare actual extracted induction headers without constructing huge meshes."""
    current = Path(__file__).resolve().parents[1] / "src/estimate/initial_mesh_estimate.cpp"
    original = reference.read_text(encoding="utf-8")
    original = original[original.index("SubMesh* ChargeEstimateProcess::InitialMeshEstimate("):]
    original = original[:original.index("bool ChargeEstimateProcess::CalculateErroEstimative")]
    candidate = current.read_text(encoding="utf-8")
    pattern = r"for\s*\([^;]+;[^;]+;[^{]+?\)\s*\{"
    old_headers = re.findall(pattern, original)
    new_headers = re.findall(pattern, candidate)
    old_outer = [h for h in old_headers if "double v" in h]
    old_inner = [h for h in old_headers if "double u" in h]
    new_outer = [h for h in new_headers if "std::uint64_t row" in h]
    new_inner = [h for h in new_headers if "std::uint64_t column" in h]
    normalize = lambda text: re.sub(r"\s+", "", text)
    if not all(len(headers) == 2 for headers in [old_outer, old_inner, new_outer, new_inner]):
        raise ValueError("Expected exactly four original and four bounded induction headers")
    for outer, inner in zip(old_outer + new_outer, old_inner + new_inner):
        renamed = re.sub(r"\bv\b", "u", re.sub(r"\brow\b", "column", outer))
        if normalize(renamed) != normalize(inner):
            raise ValueError("Inner and outer parameter sequences differ")
    start = candidate.index("{", candidate.index("BuildInitialEstimateSubMesh(")) + 1
    prefix = candidate[start:candidate.index("  int idv =", start)]
    initializers = re.findall(r"(?m)^  (?:double )?v = ([^;]+);", candidate)
    if len(initializers) != 2:
        raise ValueError("Expected actual grid and center parameter initializers")
    record = " std::uint64_t bits; std::memcpy(&bits, &v, sizeof(bits)); values.push_back(bits); }\n"
    code = """#include <cstdint>
#include <cstring>
#include <cstdio>
#include <limits>
#include <stdexcept>
#include <vector>
using Sequence = std::vector<std::uint64_t>;
Sequence Original(int degree, bool center) {
  Sequence values;
  if (center) {
""" + old_outer[1] + record + "  } else {\n" + old_outer[0] + record + "  }\n  return values;\n}\n"
    code += "Sequence Candidate(int degree, bool center) {\n" + prefix + "\nSequence values;\ndouble v = " + initializers[0] + ";\nif (center) {\nv = " + initializers[1] + ";\n" + new_outer[1] + record
    code += "} else {\n" + new_outer[0] + record + "}\nif (values.size() >= iteration_limit) throw std::runtime_error(\"Integer ceiling reached\");\nreturn values;\n}\n"
    code += r'''
unsigned long long Digest(const Sequence& values) {
  unsigned long long hash = 14695981039346656037ULL;
  for (auto value : values) { hash ^= value; hash *= 1099511628211ULL; }
  return hash;
}
int main() {
  std::vector<int> degrees;
  for (int degree = 1; degree <= 512; ++degree) degrees.push_back(degree);
  for (int degree : {1023, 1024, 4095, 4096, 10000, 65535, 65536, 1000000}) degrees.push_back(degree);
  for (int degree : degrees) {
    auto old_grid = Original(degree, false), grid = Candidate(degree, false);
    auto old_centers = Original(degree, true), centers = Candidate(degree, true);
    if (grid.empty() || centers.empty() || old_grid != grid || old_centers != centers) return 1;
    std::printf("iteration degree=%d grid=%zu centers=%zu grid_digest=%llu center_digest=%llu equal=1\n",
                degree, grid.size(), centers.size(), Digest(grid), Digest(centers));
  }
  for (int degree : {0, -1, std::numeric_limits<int>::min()}) {
    bool caught = false;
    try { auto result = Candidate(degree, false); }
    catch (const std::invalid_argument&) { caught = true; }
    if (!caught) return 2;
  }
  Sequence recomputed;
  for (int index = 0; index <= 10; ++index) {
    const double value = static_cast<double>(index) / 10;
    std::uint64_t bits; std::memcpy(&bits, &value, sizeof(bits)); recomputed.push_back(bits);
  }
  if (Original(10, false) == recomputed) return 3;
  std::puts("iteration_control integer_recomputation_rejected=1 nonpositive_guards=3");
}
'''
    source = output / "iteration_comparison.cpp"
    source.write_text(code, encoding="utf-8", newline="\n")
    executable = output / ("iteration_comparison.exe" if os.name == "nt" else "iteration_comparison")
    command = ["g++", "-std=c++17", "-O2", str(source.resolve()), "-o", str(executable.resolve())]
    if os.name == "nt":
        command += ["-static", "-static-libgcc", "-static-libstdc++"]
    compiled = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    (output / "iteration_compile.log").write_bytes(compiled.stdout)
    compiled.check_returncode()
    process = subprocess.run([str(executable.resolve())], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=30)
    (output / "iteration.log").write_bytes(process.stdout)
    process.check_returncode()
    text = process.stdout.decode("utf-8")
    rows = re.findall(r"iteration degree=(\d+) grid=(\d+) centers=(\d+) grid_digest=(\d+) center_digest=(\d+) equal=1", text)
    if len(rows) != 520 or "integer_recomputation_rejected=1 nonpositive_guards=3" not in text:
        raise ValueError("Incomplete parameter sequence inventory or negative controls")
    return {
        "status": "passed", "degree_cases": 520, "compared_nonempty_sequences": 1040,
        "comparison": "Full vectors of IEEE double object bits, not digest-only equality; integer ceiling never reached.",
        "scope": "Actual extracted original/candidate outer induction headers and actual candidate guard/ceiling prefix; inner headers independently checked identical under variable renaming. Scalar sampling only, not complete high-degree mesh construction.",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "reference_sha256": hashlib.sha256(reference.read_bytes()).hexdigest(),
        "candidate_sha256": hashlib.sha256(current.read_bytes()).hexdigest(),
        "compile_argv": command, "compile_log_sha256": hashlib.sha256(compiled.stdout).hexdigest(),
        "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
        "log_sha256": hashlib.sha256(process.stdout).hexdigest(),
        "integer_recomputation_negative_control": "rejected",
        "nonpositive_guards": 3,
        "observed_center_count_different_from_degree": [int(row[0]) for row in rows if row[2] != row[0]],
        "rows": [{"degree": int(row[0]), "grid_count": int(row[1]), "center_count": int(row[2]),
                  "grid_digest": row[3], "center_digest": row[4]} for row in rows],
    }


def qualify(asan, crt, runtime, output, iteration_reference):
    output.mkdir(parents=True, exist_ok=False)
    iterations = qualify_iterations(iteration_reference, output)
    environment = dict(os.environ)
    environment["PATH"] = str(runtime.resolve()) + os.pathsep + environment.get("PATH", "")
    environment["ASAN_OPTIONS"] = "halt_on_error=1:abort_on_error=0:detect_leaks=0"
    instruments = [("asan", asan), ("crt", crt)]
    fixtures = [f"{shape}-{layout}-{degree}" for shape in range(2) for layout in range(4) for degree in [1, 2, 4]]
    cases = [(instrument, executable, "normal-" + fixture, None)
             for instrument, executable in instruments for fixture in fixtures]
    cases += [("crt", crt, "failure-" + fixture, None) for fixture in fixtures]
    cases += [(instrument, executable, "invalid-degree", None)
              for instrument, executable in instruments]
    cases += [("asan", asan, "use-after-free", "heap-use-after-free"),
              ("crt", crt, "leak", "retained-blocks"),
              ("crt", crt, "allocation-hook-control", None)]
    results = []
    for instrument, executable, mode, diagnostic in cases:
        process = subprocess.run([str(executable.resolve()), mode], env=environment,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        data = process.stdout
        (output / f"{instrument}-{mode}.log").write_bytes(data)
        text = data.decode("utf-8", errors="replace")
        retained = re.search(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
        if diagnostic == "heap-use-after-free":
            passed = (process.returncode != 0 and "ERROR: AddressSanitizer:" in text
                      and diagnostic in text)
        elif diagnostic == "retained-blocks":
            passed = process.returncode == 1 and retained is not None and int(retained[1]) > 0
        else:
            passed = (process.returncode == 0 and "PASS" in text
                      and "ERROR: AddressSanitizer:" not in text)
            if instrument == "crt":
                passed = passed and retained is not None and int(retained[1]) == int(retained[2]) == 0
            if mode.startswith("normal-"):
                shape, layout, degree = map(int, mode.split("-")[1:])
                seeded = 4 if layout == 2 else 0 if layout == 0 else 2
                passed = (passed and len(re.findall(r"^estimate_node=", text, re.M)) == (degree + 1)**2 + degree**2
                          and len(re.findall(r"^estimate_triangle=", text, re.M)) == 4 * degree**2
                          and len(re.findall(r"^estimate_sample=", text, re.M)) == seeded * 2 + (4 - seeded) * (degree + 1))
            elif mode.startswith("failure-"):
                calibration = re.search(r"estimate_measured=shape:\d layout:\d degree:\d allocations:(\d+)", text)
                summary = re.search(r"estimate_failure_sites=shape:\d layout:\d degree:\d denied:(\d+)/(\d+)", text)
                denials = re.findall(r"estimate_denied=shape:\d layout:\d degree:\d ordinal:(\d+) retained:(\d+)", text)
                passed = (passed and calibration is not None and summary is not None
                          and int(calibration[1]) > 0 and summary[1] == summary[2] == calibration[1]
                          and len(denials) == int(calibration[1])
                          and [int(row[0]) for row in denials] == list(range(len(denials)))
                          and all(row[1] == "0" for row in denials))
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
            elif mode == "invalid-degree":
                passed = passed and len(re.findall(r"^estimate_degree_guard=degree:-?\d+ unchanged:1\r?$", text, re.M)) == 3
        results.append({
            "instrument": instrument, "mode": mode, "exit_code": process.returncode,
            "passed": bool(passed), "log_sha256": hashlib.sha256(data).hexdigest(),
            "retained_blocks": int(retained[1]) if retained else None,
            "retained_bytes": int(retained[2]) if retained else None,
            "observations": [line for line in text.splitlines()
                             if line.startswith(("estimate_", "allocation_hook_control="))],
        })
        print(json.dumps({key: value for key, value in results[-1].items()
                          if key != "observations"}), flush=True)
    report = {
        "status": "passed" if all(case["passed"] for case in results) else "failed",
        "parameter_iteration": iterations,
        "scope": "Actual estimator construction unit with real Bezier, node, triangle, SubMesh and curve lifetime units. "
                 "Original uses a Git-verified extracted InitialMeshEstimate body with a minimal owning-result adapter, "
                 "not the full ChargeEstimateProcess or Generator TU. Planar/bilinear degree 1/2/4 fixtures, "
                 "four curve initialization masks, exact ordered traces and complete observed CRT allocation sweeps. "
                 "Published sample prefixes remain with the caller collective lifetime; patch publication only on success. "
                 "Caller must rebind patch before mesh destruction. Fixture restores it explicitly. "
                 "Nonpositive-degree guards cover 0/-1/INT_MIN; the original stops at its missing zero guard, so its negative-degree execution is unmeasured. "
                 "Scalar iteration separately compares actual extracted headers at 520 positive degrees, including non-powers of two. "
                 "No whole-process, caller-wrapper lifetime, extreme complete meshes, parallel or retry qualification.",
        "executables": {name: {"path": str(path.resolve()),
                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                        for name, path in instruments},
        "cases": results,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ["asan", "crt", "runtime", "output", "iteration-reference"]:
        parser.add_argument("--" + flag, type=Path, required=True)
    args = parser.parse_args()
    report = qualify(args.asan, args.crt, args.runtime, args.output, args.iteration_reference)
    print(json.dumps({"status": report["status"], "cases": len(report["cases"])}))
    raise SystemExit(0 if report["status"] == "passed" else 1)
