#!/usr/bin/env python3
"""Qualify completed Bezier observer retirement and Geometry destruction order."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def qualify(asan, crt, runtime, output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy()
    environment["PATH"] = str(runtime) + os.pathsep + environment.get("PATH", "")
    environment["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
    modes = ["contracts", "geometry-destroy", "geometry-move-construct",
             "geometry-move-assign", "geometry-self-move", "geometry-move-consume",
             "sync-0", "sync-1", "consume-expired"]
    modes += [f"trace-{layout}-{shape}" for layout in range(3) for shape in range(2)]
    modes += [f"normal-{layout}-{shape}-{victim}-{seed}" for layout in range(3)
              for shape in range(2) for victim in range(3) for seed in range(2)]
    cases = [(instrument, executable, mode, None)
             for instrument, executable in [("asan", asan), ("crt", crt)] for mode in modes]
    cases += [("crt", crt, f"noalloc-{layout}-{victim}-{seed}", None)
              for layout in range(3) for victim in range(3) for seed in range(2)]
    cases += [("crt", crt, "noalloc-move", None)]
    cases += [(instrument, executable, "prefix-negative-control", None)
              for instrument, executable in [("asan", asan), ("crt", crt)]]
    cases += [("asan", asan, "use-after-free", "heap-use-after-free"),
              ("crt", crt, "leak", "retained-blocks"),
              ("crt", crt, "allocation-hook-control", None)]
    assert len(cases) == 126, "Review the fixed qualification inventory"
    results = []
    for instrument, executable, mode, diagnostic in cases:
        log = output / f"{instrument}-{mode}.log"
        timed_out = False
        with log.open("xb") as stream:
            try:
                process = subprocess.run([str(executable.resolve()), mode], cwd=output,
                    env=environment, stdout=stream, stderr=subprocess.STDOUT, timeout=30)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                exit_code, timed_out = None, True
        data = log.read_bytes()
        text = data.decode("utf-8", errors="replace")
        retained = re.findall(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
        if diagnostic == "heap-use-after-free":
            passed = exit_code not in [None, 0] and "ERROR: AddressSanitizer:" in text and diagnostic in text
        elif diagnostic == "retained-blocks":
            passed = exit_code == 1 and len(retained) == 1 and int(retained[0][0]) > 0
        else:
            passed = exit_code == 0 and "PASS" in text and "ERROR: AddressSanitizer:" not in text
            if instrument == "crt":
                passed = passed and retained == [("0", "0")]
            if mode == "contracts" or mode.startswith(("normal-", "sync-")) or mode == "consume-expired":
                rows = re.findall(r"observer_retired=victim:(\d) restored:(\d) curves:(\d+)", text)
                expected = 576 if mode == "contracts" else 16 if mode.startswith("normal-") else 1
                passed = passed and len(rows) == expected and all(row[1] == "1" for row in rows)
                if mode == "contracts":
                    geometry = [line for line in text.splitlines() if line.startswith("observer_geometry=")]
                    passed = (passed and len(geometry) == 5
                              and all("old_order:1 new_order:1 identities:1" in line for line in geometry))
            elif mode.startswith("trace-"):
                passed = (passed and text.count("observer_live_patch=") == 96
                          and text.count("observer_incidence=") == 384
                          and text.count("observer_scalar=") == 2592)
            elif mode.startswith("geometry-"):
                passed = passed and "old_order:1 new_order:1 identities:1" in text
            elif mode.startswith("noalloc-"):
                passed = passed and text.count("observer_noalloc=attempts:0 denied:0 restored:1") == 1
            elif mode == "prefix-negative-control":
                passed = passed and "observer_prefix_control=rejected" in text
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
        row = {"instrument": instrument, "mode": mode, "exit_code": exit_code,
               "timed_out": timed_out, "passed": bool(passed), "expected_diagnostic": diagnostic,
               "log_sha256": hashlib.sha256(data).hexdigest(), "retained": retained,
               "observations": [line for line in text.splitlines() if line.startswith("observer_")]}
        results.append(row)
        print(json.dumps({key: value for key, value in row.items() if key != "observations"}), flush=True)
    report = {"status": "passed" if all(row["passed"] for row in results) else "failed",
        "expected_outcomes": 126, "cases": results,
        "zero_allocation_operations": sum(row["passed"] and row["mode"].startswith("noalloc-")
                                           for row in results),
        "executables": {label: {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                        for label, path in [("asan", asan), ("crt", crt)]},
        "scope": "Actual Bezier, curve, Geometry and synchronization units. Three incidence layouts, two surfaces, all 16 directions, three retirement positions, empty/populated prefixes and repeated/null observers. Require stable removal of every matching current-incidence observer, preserved foreign entries and Geometry dependent retirement before curves during destruction, move construction, populated move assignment and self move. Nineteen denial-enabled operations must allocate nothing; actual hook/UAF/leak and independent prefix controls remain mandatory. Live numerical traces are separate and retire registrations while patches are alive for the original comparison. Curves must outlive patches; manual curve-first deletion, arbitrary ReplaceCurve/publications, copied curve observers, Hermite patch retirement, SubMesh observer lifetime, cache/metadata/acceptance rollback and full-process/parallel/LSan/UBSan remain unqualified. Repeated slots and degenerate order fixtures are lifetime guards, not geometric validity. ASan leaks are disabled; static Debug CRT independently supplies terminal retention."}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["asan", "crt", "runtime", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    report = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps({key: report[key] for key in ["status", "expected_outcomes", "zero_allocation_operations"]}))
    raise SystemExit(report["status"] != "passed")
