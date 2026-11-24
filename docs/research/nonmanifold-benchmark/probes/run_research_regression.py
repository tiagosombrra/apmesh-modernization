"""Run bounded, local research regression without promoting partial coverage."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET


BASELINE = "92b8af3b9e73072d1122d82ed956f75b608ea5c1"
RESEARCH = Path("docs/research/nonmanifold-benchmark")
MIN_RESEARCH_MODULES = 80  # Frozen pre-consolidation Python inventory.
MIN_CTEST_ENTRIES = 75
PASS = "PASS"
FAIL = "FAIL"
BLOCKED = "BLOCKED"


def git_output(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def count_python_tests(log, returncode):
    """A clean process and a nonempty unittest result are both necessary."""
    counts = re.findall(r"^Ran (\d+) tests? in [0-9.]+s\s*$", log, re.M)
    if len(counts) != 1:
        return {"status": FAIL, "tests": 0, "skips": 0}
    total = int(counts[0])
    skipped = re.findall(r"\bskipped=(\d+)\b", log)
    skips = int(skipped[-1]) if skipped else 0
    okay = re.search(r"^OK(?: \([^\n]*\))?\s*$", log, re.M)
    status = PASS if returncode == 0 and okay and total > 0 and skips == 0 else (
        BLOCKED if returncode == 0 and okay and total > 0 and 0 < skips <= total else FAIL)
    return {"status": status, "tests": total, "skips": skips}


def run_step(output, name, cmd, cwd, timeout):
    start = time.monotonic()
    log_path = output / (name + ".log")
    try:
        proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              timeout=timeout, check=False)
        data = proc.stdout
        code = proc.returncode
        status = PASS if code == 0 else FAIL
    except subprocess.TimeoutExpired as error:
        data = (error.stdout or b"") + b"\nREGRESSION TIMEOUT\n"
        code, status = None, FAIL
    except OSError as error:
        data = (str(error) + "\n").encode()
        code, status = None, BLOCKED
    log_path.write_bytes(data)
    return {"name": name, "status": status, "returncode": code,
            "seconds": round(time.monotonic() - start, 3),
            "log": log_path.name, "log_sha256": hashlib.sha256(data).hexdigest()}


def check_checkout(root):
    """Reject a dirty or incomplete checkout; never infer coverage from a glob alone."""
    head = git_output(root, "rev-parse", "HEAD")
    top = Path(git_output(root, "rev-parse", "--show-toplevel")).resolve()
    if top != root or git_output(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Use an exact clean tracked repository checkout")
    paths = git_output(root, "ls-files", "--", str(RESEARCH / "probes")).splitlines()
    modules = {p for p in paths if Path(p).match("test_*.py")}
    frozen_paths = git_output(root, "ls-tree", "-r", "--name-only", BASELINE, "--", str(RESEARCH / "probes")).splitlines()
    frozen_modules = {p for p in frozen_paths if Path(p).match("test_*.py")}
    if len(frozen_modules) != MIN_RESEARCH_MODULES or not frozen_modules.issubset(modules):
        raise ValueError("The frozen research test inventory is missing or has unreviewed deletions")
    actual = {str(p.relative_to(root).as_posix()) for p in (root / RESEARCH / "probes").glob("test_*.py")}
    if len(modules) < MIN_RESEARCH_MODULES or modules != actual:
        raise ValueError(f"Incomplete Python test inventory: tracked={len(modules)}, actual={len(actual)}")
    if not (root / "CMakeLists.txt").is_file():
        raise ValueError("Missing production CMake entrypoint")
    return head, sorted(modules)


def privacy_check(root):
    """Check tracked paths; private geometry is never a regression dependency in Git."""
    entries = git_output(root, "ls-files").splitlines()
    suspect = []
    for entry in entries:
        name = Path(entry).name.lower()
        if (name.endswith((".step", ".stp", ".stl", ".bp", ".obj", ".zip")) and
                ("293137" in name or "thingi10k" in name or name.startswith(("i25o_s40", "tsh249", "bunny_passo")))):
            suspect.append(entry)
        if name.endswith("_incidences.json") and "bunny" in name:
            suspect.append(entry)
        if ".private." in name or name.startswith("private_") and name.endswith((".bp", ".obj", ".step")):
            suspect.append(entry)
    if suspect:
        raise ValueError(f"Private model path tracked: {suspect}")
    return {"name": "tracked_private_asset_gate", "status": PASS, "tracked_paths": len(entries)}


def read_ctest_result(path, returncode):
    if not path.is_file():
        return {"status": FAIL, "tests": 0, "skips": 0}
    try:
        suite = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return {"status": FAIL, "tests": 0, "skips": 0}
    cases = list(suite.iter("testcase"))
    failures = sum(case.find("failure") is not None or case.find("error") is not None for case in cases)
    skips = sum(case.find("skipped") is not None for case in cases)
    status = FAIL if returncode != 0 or failures or not cases else (
        BLOCKED if skips or len(cases) < MIN_CTEST_ENTRIES else PASS)
    return {"status": status, "tests": len(cases), "skips": skips, "failures": failures}


def compare_receipts(expected, actual, key="root"):
    """Use the frozen F31 numerical portability contract, not exact float text equality."""
    if type(expected) != type(actual):
        raise ValueError(f"Receipt type differs at {key}")
    if isinstance(expected, dict):
        if expected.keys() != actual.keys():
            raise ValueError(f"Receipt keys differ at {key}")
        for name in expected:
            compare_receipts(expected[name], actual[name], f"{key}.{name}")
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            raise ValueError(f"Receipt list length differs at {key}")
        for index, (left, right) in enumerate(zip(expected, actual)):
            compare_receipts(left, right, f"{key}[{index}]")
    elif isinstance(expected, float):
        if not math.isclose(expected, actual, abs_tol=1e-8, rel_tol=1e-9):
            raise ValueError(f"Receipt number differs at {key}")
    elif expected != actual:
        raise ValueError(f"Receipt value differs at {key}")


def verify_historical_receipts(root):
    """Preserve unique source and receipt gates from the retired F27-F31 workflows."""
    import thingi10k_f31_real_model_readiness as readiness
    import thingi10k_f31_synthetic_generalization as synthetic

    probes = root / RESEARCH / "probes"
    source = (probes / "thingi10k_f27_native_tri_evidence.py").read_bytes()
    git_blob = hashlib.sha1(f"blob {len(source)}\0".encode() + source).hexdigest()
    if git_blob != "12f4d3d0f90fa0fb99893fe823f8b9e216d3e3a8":
        raise ValueError("Frozen F27 scientific auditor changed")
    evidence = root / RESEARCH / "evidence/thingi10k"
    def load(name):
        return json.loads((evidence / name).read_text(encoding="utf-8"))
    original = load("thingi10k_f31_generated_synthetic_generalization_receipt.json")
    compare_receipts(original, synthetic.produce_receipt(root))
    if load("thingi10k_f31_real_model_readiness_delta_receipt.json") != readiness.produce(root):
        raise ValueError("Frozen real-model readiness receipt differs")
    f29 = load("thingi10k_f29_real_derived_patch_quad_receipt.json")
    f30 = load("thingi10k_f30_final_real_pareto_receipt.json")
    independent = load("thingi10k_f30_external_trimesh_receipt.json")
    gates = [
        f29["native_original_quad_generator_executed"] is False,
        f29["scientific_reference_comparison_admitted"] is False,
        f29["published_source_or_derived_geometry"] is False,
        f30["schema"] == "apmesh-s40-f30-feature-locked-pareto-center-v1",
        f30["native_quad_generator_executed"] is False,
        f30["native_apmesh_engine_or_exporter_changed"] is False,
        f30["scientific_benchmark_admitted"] is False,
        f30["published_original_or_private_derived_geometry"] is False,
        f30["quad_topology"]["faces"] == 876,
        f30["optimized_quality"]["count_min_angle_below_30_deg"] <= f30["baseline_quality"]["count_min_angle_below_30_deg"],
        f30["optimized_quality"]["count_max_angle_above_150_deg"] <= f30["baseline_quality"]["count_max_angle_above_150_deg"],
        f30["optimized_quality"]["mean_min_scaled_jacobian"] > f30["baseline_quality"]["mean_min_scaled_jacobian"],
        independent["native_apmesh_quad_generator_executed"] is False,
        independent["original_geometry_or_derived_OBJ_published"] is False,
        independent["exact_face_connectivity_and_order_retained"] is True,
    ]
    if not all(gates):
        raise ValueError("Frozen F29/F30 derived QUAD evidence contract changed")
    print("Frozen F27/F29/F30/F31 receipt gates PASS (not private real-model replays)")


def count_node_tests(log, returncode):
    """Reject zero, skipped, or incomplete Node TAP results."""
    def metric(name):
        hits = re.findall(rf"^# {name} (\d+)\s*$", log, re.M)
        return int(hits[0]) if len(hits) == 1 else None
    tests, passed, failed, skipped = (metric(k) for k in ("tests", "pass", "fail", "skipped"))
    if returncode != 0 or tests is None or tests <= 0 or failed != 0 or passed is None or skipped is None:
        status = FAIL
    elif skipped or passed != tests:
        status = BLOCKED
    else:
        status = PASS
    return {"status": status, "tests": tests or 0, "skips": skipped or 0}


def summarize(steps, scope, expected, present):
    """An incomplete inventory or skipped test prevents a complete pass."""
    if any(step["status"] == FAIL for step in steps):
        return FAIL
    if scope != "checkout" or present < expected or any(step["status"] != PASS for step in steps):
        return BLOCKED
    return PASS


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output", type=Path, required=True, help="Fresh private directory outside the checkout")
    parser.add_argument("--scope", choices=("checkout", "recovered"), default="checkout")
    parser.add_argument("--module-timeout", type=int, default=300)
    parser.add_argument("--build-timeout", type=int, default=3600)
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args(argv)
    root, output = args.root.resolve(), args.output.resolve()
    if output.exists() or output == root or root in output.parents:
        parser.error("Output must be a fresh directory outside the repository")
    if min(args.module_timeout, args.build_timeout, args.jobs) <= 0:
        parser.error("Timeouts and job count must be positive")
    output.mkdir(parents=True, exist_ok=False)
    probes = root / RESEARCH / "probes"
    steps = []
    head = None
    expected = MIN_RESEARCH_MODULES
    modules = []
    try:
        if args.scope == "checkout":
            head, modules = check_checkout(root)
            expected = len(modules)
            steps.append(privacy_check(root))
        else:
            modules = sorted(str(p.relative_to(root).as_posix()) for p in probes.glob("test_*.py"))
            steps.append({"name": "checkout_identity_and_native_scope", "status": BLOCKED,
                          "reason": "Recovered subset is not a complete Git checkout"})
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        steps.append({"name": "checkout_preflight", "status": BLOCKED, "reason": str(error)})
        head, modules = None, []
    if not modules:
        steps.append({"name": "research_python_inventory", "status": BLOCKED, "reason": "No modules discovered"})
    for rel in modules:
        module = Path(rel).name
        step = run_step(output, Path(module).stem, [sys.executable, "-m", "unittest", "discover",
                        "-s", str(probes), "-p", module, "-v"], root, args.module_timeout)
        if step["status"] != BLOCKED:
            step.update(count_python_tests((output / step["log"]).read_text(errors="replace"), step["returncode"]))
        step["family"] = "research_python"
        steps.append(step)
    if args.scope == "checkout" and head and modules:
        # Preserve distinct historical evidence gates that were formerly duplicated across workflows.
        step = run_step(output, "native_quad_capability", [sys.executable, str(probes / "thingi10k_f29_quad_capability_and_recovery.py"),
                        "--source-root", str(root)], root, args.module_timeout)
        steps.append(step)
        steps.append(run_step(output, "historical_receipts", [sys.executable, "-c",
            "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
            "from run_research_regression import verify_historical_receipts; verify_historical_receipts(Path(sys.argv[2]))",
            str(probes), str(root)], root, args.module_timeout))
        node_test = probes / "test_thingi10k_zip_audit.cjs"
        if node_test.is_file():
            node_step = run_step(output, "research_node", ["node", "--test", str(node_test)], root, args.module_timeout)
            if node_step["status"] != BLOCKED:
                node_step.update(count_node_tests((output / node_step["log"]).read_text(errors="replace"), node_step["returncode"]))
            steps.append(node_step)
        else:
            steps.append({"name": "research_node", "status": BLOCKED, "reason": "Tracked Node test missing"})
        # CTest includes the production Python tooling group; do not count it twice.
        build = output / "build"
        step = run_step(output, "cmake_configure", ["cmake", "-S", str(root), "-B", str(build),
                        "-DCMAKE_BUILD_TYPE=Release", "-DBUILD_TESTING=ON", "-DAP_MESH_USE_MPI=OFF",
                        "-DAP_MESH_USE_OPENMP=OFF", "-DAP_MESH_ENABLE_LTO=OFF"], root, args.module_timeout)
        steps.append(step)
        if step["status"] == PASS:
            step = run_step(output, "cmake_build", ["cmake", "--build", str(build), "--config", "Release",
                            "--parallel", str(args.jobs)], root, args.build_timeout)
            steps.append(step)
            if step["status"] == PASS:
                junit = output / "ctest.xml"
                step = run_step(output, "ctest", ["ctest", "--test-dir", str(build), "-C", "Release",
                                "--output-on-failure", "--no-tests=error", "--timeout", str(args.module_timeout),
                                "--output-junit", str(junit)], root, args.build_timeout)
                if step["status"] != BLOCKED:
                    step.update(read_ctest_result(junit, step["returncode"]))
                steps.append(step)
        if not any(s["name"] == "ctest" for s in steps):
            steps.append({"name": "ctest", "status": BLOCKED, "reason": "Build not completed"})
    else:
        steps.extend({"name": name, "status": BLOCKED, "reason": "Complete checkout unavailable"}
                     for name in ("native_quad_capability", "historical_receipts", "research_node", "ctest"))
    result = {"schema": "apmesh-research-regression-v1", "scope": args.scope, "head": head,
              "frozen_inventory_reference": BASELINE, "python": sys.version.split()[0],
              "research_modules": len(modules), "expected_research_modules_at_least": expected,
              "research_python_tests": sum(s.get("tests", 0) for s in steps if s.get("family") == "research_python"),
              "research_python_skips": sum(s.get("skips", 0) for s in steps if s.get("family") == "research_python"),
              "steps": steps, "status": summarize(steps, args.scope, expected, len(modules)),
              "scientific_model_admitted": False,
              "private_original_model_replay_certified": False}
    (output / "receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "steps"}, sort_keys=True))
    return {PASS: 0, FAIL: 1, BLOCKED: 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
