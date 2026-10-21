#!/usr/bin/env python3
"""Measure the bounded full serial-reader lifetime with actual CRT allocation denials."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixtures(output):
    directory = output / "fixtures"
    directory.mkdir()
    paths = []
    for shape in range(4):
        rows = []
        count = 1 if shape < 2 else 3
        for patch in range(count):
            for v in range(4):
                for u in range(4):
                    x, y = patch + u / 3, v / 3
                    z = 0 if shape == 0 else (x*x + y*y)/8
                    rows.append(f"v {x:.17g} {y:.17g} {z:.17g}")
        for patch in range(count):
            indices = list(range(patch*16, patch*16+16))
            if shape == 3 and patch == 2:
                indices = [v*4 + 3-u for v in range(4) for u in range(4)]
            rows.append("p " + " ".join(map(str, indices)))
        path = directory / f"{shape}.bp"
        path.write_text("\n".join(rows)+"\n", encoding="utf-8", newline="\n")
        paths.append(path)
    valid = paths[0].read_text(encoding="utf-8")
    failures = {"empty": "", "indent": " " + valid, "nonfinite": valid.replace("v 0 0 0", "v nan 0 0", 1),
                "index": valid.replace("p 0 1", "p 999 1"),
                "arity": valid.rsplit(" ", 1)[0]+"\n", "tail": valid+"v 0 0 0 extra\n",
                "unknown": valid+"unknown\n"}
    rejected = []
    for label, content in failures.items():
        path = directory / (label+".bp")
        path.write_text(content, encoding="utf-8", newline="\n")
        rejected.append(path)
    rejected.append(directory / "missing.bp")
    return paths, rejected


def qualify(asan, crt, runtime, output, original=False):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    paths, rejected = fixtures(output)
    environment = dict(os.environ)
    environment["PATH"] = str(runtime.resolve())+os.pathsep+environment.get("PATH", "")
    environment["ASAN_OPTIONS"] = "halt_on_error=1:abort_on_error=0:detect_leaks=0"
    cases = []

    def invoke(executable, mode, path, log, extra=None):
        command = [str(executable.resolve()), mode, str(path)] + ([str(extra)] if extra else [])
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 env=environment, timeout=30)
        target = output / log
        target.write_bytes(process.stdout)
        return {"argv": command, "exit_code": process.returncode, "timed_out": False, "log": log,
                "log_sha256": digest(target)}, process.stdout

    def record(instrument, mode, data, invocation, expected=True, invocations=None):
        passed = invocation["exit_code"] == 0 and b"PASS\n" in data.replace(b"\r\n", b"\n")
        if instrument == "crt":
            passed &= b"CRT retained_blocks=0 retained_bytes=0" in data
        if mode == "use-after-free":
            passed = invocation["exit_code"] != 0 and b"heap-use-after-free" in data and b"AddressSanitizer" in data
        elif mode == "leak":
            match = re.search(rb"CRT retained_blocks=(\d+) retained_bytes=(\d+)", data)
            passed = invocation["exit_code"] != 0 and match is not None and all(int(x)>0 for x in match.groups())
        elif mode == "allocation-hook-control":
            passed &= b"allocation_hook_control=detected" in data
        elif mode.startswith("prefix-negative-control"):
            passed &= b"serial_prefix_control=rejected" in data
        elif mode.startswith("reject"):
            passed &= b"serial_rejected=caught:1 live:1" in data
        passed = bool(passed and expected)
        case = {"instrument": instrument, "mode": mode, "passed": passed,
                "exit_code": invocation["exit_code"], "log_sha256": invocation["log_sha256"],
                "observations": [x for x in data.decode("utf-8",errors="replace").splitlines()
                                 if x.startswith(("serial_", "CRT "))]}
        if invocations is not None:
            case["invocations"] = invocations
        cases.append(case)

    for instrument, executable in [("asan", asan), ("crt", crt)]:
        for shape, path in enumerate(paths):
            modes = ["read", "reuse", "contracts", "prefix-negative-control"]
            modes += [f"normal-{operation}-{seed}" for operation in range(2) for seed in range(2)]
            modes += [f"trace-1-{seed}" for seed in range(2)]
            for actual in modes:
                label = f"{actual}-shape{shape}"
                invocation, data = invoke(executable, actual, path, instrument+"-"+label+".log")
                record(instrument, label, data, invocation)
        for number, path in enumerate(rejected):
            for actual in ["reject", "reject-seeded"]:
                label = f"{actual}-{number}"
                invocation, data = invoke(executable, actual, paths[0], instrument+"-"+label+".log", path)
                record(instrument, label, data, invocation)
    for instrument, executable, mode in [("asan", asan, "use-after-free"), ("crt", crt, "leak"),
                                          ("crt", crt, "allocation-hook-control")]:
        invocation, data = invoke(executable, mode, paths[0], instrument+"-"+mode+".log")
        record(instrument, mode, data, invocation)
    denials = 0
    complete_sweeps = 0
    for shape, path in enumerate(paths):
        for operation in range(2):
            for seed in range(2):
                mode = f"failure-{shape}-{operation}-{seed}"
                label = "crt-"+mode
                calibration, data = invoke(crt, f"calibrate-{operation}-{seed}", path, label+"-calibration.log")
                match = re.search(rb"serial_measured=allocations:(\d+)", data)
                total = int(match[1]) if match else 0
                invocations = [calibration]
                combined = data
                expected = total>0 and calibration["exit_code"]==0
                observed = []
                for first in range(0, total, 32):
                    child, raw = invoke(crt, f"failure-{operation}-{seed}-{first}", path, label+f"-{first}.log")
                    combined += raw
                    invocations.append(child)
                    events = re.findall(rb"serial_denied=ordinal:(\d+) blocks:(\d+) bytes:(\d+)", raw)
                    trials = re.findall(rb"serial_trial=ordinal:(\d+) attempts:(\d+) denied:(\d+) caught:(\d+) complete:(\d+) live:(\d+)", raw)
                    actual = [int(x[0]) for x in events]
                    observed += actual
                    expected &= actual==list(range(first,min(first+32,total)))
                    expected &= [int(x[0]) for x in trials if int(x[0])>=0]==actual
                    expected &= re.findall(rb"serial_measured=allocations:(\d+)",raw)==[str(total).encode()]
                    expected &= all(int(x[1])==0 and int(x[2])==0 for x in events)
                    expected &= all(int(x[2])==1 and int(x[3])>0 and int(x[5])==1 for x in trials if int(x[0])>=0)
                    expected &= child["exit_code"]==0
                    if child["exit_code"]!=0:
                        break
                expected &= observed==list(range(total))
                combined_path = output/(label+".log")
                combined_path.write_bytes(combined)
                synthetic = {"exit_code": 0 if expected else 1, "log_sha256": digest(combined_path)}
                record("crt", mode, combined, synthetic, expected, invocations)
                cases[-1].update(calibrated_allocations=total, measured_denials=len(observed),
                                 complete_sweep=bool(expected), later_ordinals_unmeasured=total-len(observed))
                denials += len(observed)
                complete_sweeps += bool(expected)
    if len(cases)!=131:
        raise ValueError(f"Required case inventory differs: {len(cases)}")
    result = {"status": "passed" if all(case["passed"] for case in cases) else "failed",
              "cases": cases, "complete_sweeps": complete_sweeps, "allocation_denials": denials,
              "executables": {"asan": {"path": str(asan.resolve()), "sha256": digest(asan)},
                              "crt": {"path": str(crt.resolve()), "sha256": digest(crt)}},
              "fixtures": {str(p.relative_to(output)): digest(p) for p in paths+rejected if p.exists()},
              "original_recording": original,
              "scope": "Full serial reader TU; bounded four surfaces, live committed prefixes, independent owning results, eight rejected input classes and complete CRT sweeps. Partial Geometry commit is permitted; no whole-reader rollback, retry, complete CLI/parallel/LSan/UBSan or other loaders are qualified. ASan leak detection disabled; static Debug CRT measures retention. Original failed sweeps stop at first failed chunk; later ordinals remain unmeasured."}
    (output/"report.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ["asan","crt","runtime","output"]:
        parser.add_argument("--"+name,type=Path,required=True)
    parser.add_argument("--record-original",action="store_true")
    args=parser.parse_args()
    result=qualify(args.asan,args.crt,args.runtime,args.output,args.record_original)
    print(json.dumps({key:result[key] for key in ["status","complete_sweeps","allocation_denials"]}))
    raise SystemExit(0 if result["status"]=="passed" else 1)
