#!/usr/bin/env python3
"""Local validation coordination; canonical contracts and approvals stay authoritative."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import unittest
from urllib.parse import unquote
import uuid

import quality

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ("AGENTS.md", "docs/PROJECT_STATE.md", "docs/MODERNIZATION_PLAN.md",
             "docs/QUALITY_AUTOMATION.md")
TOOLS = ("git", "cmake", "ctest", "ninja", "clang-format", "clang-tidy", "doxygen")
AXES = {"source", "build", "inputs", "oracles", "instrument", "environment", "contracts"}
SUMMARY_LIMIT = 6144
LOCAL = "build/validation-session/local"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def inside(root: Path, name: str) -> Path:
    path = root / name
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Path is outside the project or a symlink: {name}")
    return path.resolve()


def git(root: Path, *args) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True,
                                   encoding="utf-8", timeout=30).strip()


def profile(root: Path) -> dict:
    path = root / LOCAL / "environment.json"
    value = read_json(path) if path.exists() else {"schema": 1, "tools": {}}
    if value.get("schema") != 1 or not isinstance(value.get("tools"), dict):
        raise ValueError("Invalid local environment profile")
    if set(value["tools"]) - set(TOOLS):
        raise ValueError("Unknown tool in local environment profile")
    return value


def command_environment(root: Path) -> dict:
    """Prepend explicitly configured tool locations only in the child environment."""
    value = profile(root)
    directories = []
    for name, filename in value["tools"].items():
        executable = Path(filename)
        if not executable.is_absolute() or not executable.is_file():
            raise ValueError(f"Configured tool is missing or not absolute: {name}")
        directory = str(executable.parent)
        if directory not in directories:
            directories.append(directory)
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join(directories + [env.get("PATH", "")])
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def changes(root: Path, base: str) -> dict:
    names = set(git(root, "diff", "--name-only", "-z", "--diff-filter=ACDMRTUXB",
                    base, "--").split("\0"))
    names.update(git(root, "ls-files", "--others", "--exclude-standard", "-z").split("\0"))
    return {name: digest(path) if (path := inside(root, name)).is_file() else "deleted"
            for name in sorted(filter(None, names))}


def identity(root: Path, base: str = "HEAD") -> dict:
    local = {}
    for name in (LOCAL + "/environment.json", LOCAL + "/validation-baseline.json"):
        path = inside(root, name)
        local[name] = digest(path) if path.is_file() else "missing"
    return {"revision": git(root, "rev-parse", "HEAD"),
            "tree": git(root, "rev-parse", "HEAD^{tree}"),
            "canonical": {name: digest(inside(root, name)) for name in CANONICAL},
            "changes": changes(root, base), "local": local,
            "coordinator": digest(Path(__file__)), "base": base}


def summary(root: Path, task: str = "Unbound: read the current user request") -> dict:
    state = identity(root)
    rows = ["# Operational view (derived; not project authority)", "",
            f"Task: {task}", f"Recorded revision: {state['revision']}",
            f"Working changes: {len(state['changes'])}", "",
            "Read canonical current checkpoints before work; histories answer named questions.",
            "User scope and native permissions outrank this view. No new task is authorized here.",
            "Keep one work item; do not start scientific work or publish from a cached status.",
            "Preserve formulas, ordering, synchronization, selection and stopping policies.",
            "Missing tools, zero coverage, failed prefixes and absent instruments are not passes.",
            "Delivery requires its exact-head/main gates and fresh remote checks.", "",
            "## Canonical sources"]
    rows.extend(f"- {name}: {value}" for name, value in state["canonical"].items())
    for name, heading in (("docs/PROJECT_STATE.md", "Current checkpoint and active work"),
                          ("docs/MODERNIZATION_PLAN.md", "Current production priority")):
        text = inside(root, name).read_text(encoding="utf-8")
        match = re.search(r"^## " + re.escape(heading) + r"\s*\n(.*?)(?=^#{1,3} |\Z)",
                          text, re.M | re.S)
        if not match:
            raise ValueError(f"Canonical summary section is absent: {name}: {heading}")
        rows.extend(["", f"## Source excerpt: {name}",
                     match[1].strip()[:850]])
    rows.extend(["", "## Execution routing",
                 "python tools/validation_session.py plan --scope iteration",
                 "python tools/validation_session.py run --scope delivery",
                 "The delivery plan retains every baseline test. Package-specific gates remain additional.",
                 "No push, merge, new scientific configuration or format fix is provided by this adapter.",
                 "A prior seal describes its own revision/scope, not current working-tree qualification."])
    text = "\n".join(rows) + "\n"
    if len(text.encode("utf-8")) > SUMMARY_LIMIT:
        raise ValueError("Operational view exceeds its byte budget")
    target = inside(root, LOCAL + "/OPERATIONAL_SUMMARY.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    receipt = {"schema": 1, "identity": state, "sha256": digest(target),
               "bytes": len(text.encode("utf-8")), "task": task}
    write_json(inside(root, LOCAL + "/summary.json"), receipt)
    return receipt


def verify_summary(root: Path) -> dict:
    value = read_json(inside(root, LOCAL + "/summary.json"))
    if value.get("schema") != 1 or value.get("identity") != identity(root):
        raise ValueError("Operational view is stale; regenerate from canonical sources")
    if value.get("sha256") != digest(inside(root, LOCAL + "/OPERATIONAL_SUMMARY.md")):
        raise ValueError("Operational view content changed")
    return value


def unit_ids(root: Path) -> list[str]:
    def flatten(suite):
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                yield from flatten(test)
            else:
                yield test.id()
    names = sorted(flatten(unittest.TestLoader().discover(str(root / "tests/tooling"))))
    if not names or any("_FailedTest" in name for name in names):
        raise ValueError("Tooling discovery is empty or contains import failures")
    return names


def test_inventory(root: Path) -> list[dict]:
    directory = inside(root, profile(root).get("build_dir", "build/windows-gcc17"))
    result = subprocess.run(["ctest", "--test-dir", str(directory), "--show-only=json-v1"],
                            cwd=root, env=command_environment(root), check=True,
                            capture_output=True, text=True, encoding="utf-8", timeout=30)
    tests = json.loads(result.stdout)["tests"]
    if not tests or len({test["name"] for test in tests}) != len(tests):
        raise ValueError("Empty or duplicate CTest inventory")
    return tests


def check_baseline(baseline: dict, tests: list[dict], units: list[str]):
    required = {test["name"] for test in baseline.get("ctest", [])}
    old_units = set(baseline.get("unit_ids", []))
    if baseline.get("schema") != 1 or not required or not old_units:
        raise ValueError("Missing qualified test baseline")
    if len({test["name"] for test in tests}) != len(tests) or len(set(units)) != len(units):
        raise ValueError("Duplicate test identities")
    missing = required - {test["name"] for test in tests}
    missing_units = old_units - set(units)
    if missing or missing_units:
        raise ValueError(f"Required tests removed: {sorted(missing | missing_units)}")


def affected_targets(root: Path, paths: list[str]) -> set[str] | None:
    """Read actual compiler metadata; uncertainty requests conservative coverage."""
    directory = inside(root, profile(root).get("build_dir", "build/windows-gcc17"))
    database = directory / "compile_commands.json"
    if not database.is_file() or any(name.endswith((".h", ".hpp")) for name in paths):
        return None
    targets = set()
    for name in paths:
        entries = [row for row in read_json(database)
                   if Path(row["file"]).resolve() == inside(root, name)]
        if not entries:
            return None
        for row in entries:
            match = re.search(r"CMakeFiles[/\\]([^/\\]+)\.dir", row.get("output", ""))
            if not match or "engine" in match[1]:
                return None
            targets.add(match[1])
    return targets


def make_plan(root: Path, scope: str, base: str = "HEAD") -> dict:
    baseline = read_json(inside(root, LOCAL + "/validation-baseline.json"))
    tests, units = test_inventory(root), unit_ids(root)
    check_baseline(baseline, tests, units)
    files = changes(root, base)
    all_names = sorted(test["name"] for test in tests)
    selected, reason = all_names, "unmapped or shared impact: conservative full coverage"
    names = [name for name in files if not name.endswith(".md")]
    if not names:
        selected, reason = [], "documentation scope; no regression qualification inferred"
    elif all(name.startswith("tests/tooling/") or name in
             ("tools/quality.py", "tools/validation_session.py") for name in names):
        selected, reason = ["tooling.controls"], "tooling code: existing complete tooling suite"
    elif all(name.endswith((".cpp", ".cc", ".cxx", ".h", ".hpp")) for name in names):
        targets = affected_targets(root, names)
        if targets:
            selected = sorted(test["name"] for test in tests if test.get("command") and
                              Path(test["command"][0]).stem in targets)
            if not selected:
                selected = all_names
            else:
                reason = "actual private-target compiler metadata; mandatory delivery union retained"
    if not set(selected) <= set(all_names):
        raise ValueError("Selected test is absent from current inventory")
    return {"schema": 1, "scope": scope, "identity": identity(root, base), "files": files,
            "iteration_selected": selected, "selection_reason": reason,
            "mandatory_tests": all_names, "baseline_tests": len(baseline["ctest"]),
            "unit_ids": units, "new_unit_ids": sorted(set(units) - set(baseline["unit_ids"])),
            "stage_closure": False, "delivery_eligible": False,
            "additional_package_gates": "Read canonical package requirements; not inferred or waived",
            "additional_scientific_execution": False, "publication_authorized": False}


def check_links(root: Path, files: dict) -> dict:
    documents, targets = 0, 0
    for name, state in files.items():
        if not name.endswith(".md") or state == "deleted":
            continue
        path = inside(root, name)
        documents += 1
        for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            target = match[1].strip("<>").split("#", 1)[0]
            if not target or re.match(r"^[a-zA-Z][\w+.-]*:", target):
                continue
            resolved = (path.parent / unquote(target)).resolve()
            if not resolved.is_relative_to(root) or not resolved.exists():
                raise ValueError(f"Missing or outside local link: {name}: {target}")
            targets += 1
    return {"status": "passed" if documents else "not_applicable", "documents": documents,
            "local_targets": targets, "scope": "local target existence; fragments and URLs unmeasured"}


def execute_steps(steps: list[dict], output: Path, env: dict, cwd: Path,
                  final_check=None) -> dict:
    """Execute sequentially; any failure stops the chain and remains in the record."""
    if not steps or any(not re.fullmatch(r"[a-z][a-z0-9-]{0,40}", step.get("id", "")) or
                        not isinstance(step.get("argv"), list) or not step["argv"] or
                        not all(isinstance(arg, str) for arg in step["argv"]) or
                        type(step.get("timeout")) not in (int, float) or
                        not math.isfinite(step["timeout"]) or step["timeout"] <= 0
                        for step in steps):
        raise ValueError("Empty or invalid execution steps")
    output.mkdir(parents=True, exist_ok=False)
    record = {"schema": 1, "status": "running", "steps": []}
    for index, step in enumerate(steps):
        started = time.monotonic()
        row = {"id": step["id"], "argv": step["argv"], "status": "running"}
        record["steps"].append(row)
        write_json(output / "report.json", record)
        try:
            with (output / f"{index:02d}-{step['id']}.log").open("xb") as stream:
                flags = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
                process = subprocess.Popen(step["argv"], cwd=cwd, env=env, stdout=stream,
                                           stderr=subprocess.STDOUT, **flags)
                try:
                    code = process.wait(timeout=step["timeout"])
                except subprocess.TimeoutExpired:
                    if os.name == "nt":
                        killer = Path(os.environ["SystemRoot"]) / "System32/taskkill.exe"
                        subprocess.run([str(killer), "/PID", str(process.pid), "/T", "/F"],
                                       stdout=stream, stderr=subprocess.STDOUT, check=False, timeout=15)
                    else:
                        os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=15)
                    row["exit_code"] = 124
                    raise
            row["exit_code"] = code
            if code != 0:
                raise ValueError(f"Step failed: {step['id']} (exit {code})")
            if step.get("result_json"):
                parsed = read_json(Path(step["result_json"]))
                if not isinstance(parsed, dict) or parsed.get("status") != "passed":
                    raise ValueError("Missing or invalid prerequisite status")
            row["status"] = "passed"
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            row.update(status="failed", error=str(error))
            record["status"] = "failed"
        finally:
            row["seconds"] = time.monotonic() - started
            write_json(output / "report.json", record)
        if record["status"] == "failed":
            return record
    try:
        if final_check:
            final_check()
        record["status"] = "passed"
    except Exception as error:
        record.update(status="failed", error=str(error))
    write_json(output / "report.json", record)
    return record


@contextmanager
def validation_lock(root: Path):
    """Prevent concurrent runners from modifying the same existing test artifacts."""
    path = inside(root, LOCAL + "/run.lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        stream = path.open("x", encoding="utf-8")
    except FileExistsError as error:
        raise ValueError("Validation runner is locked; inspect the recorded process before manual recovery") from error
    try:
        with stream:
            json.dump({"pid": os.getpid(), "started": time.time()}, stream)
        yield
    finally:
        path.unlink()


def run_plan(root: Path, plan: dict, output: Path) -> dict:
    with validation_lock(root):
        return _run_plan(root, plan, output)


def ctest_expression(names: list[str]) -> str:
    # CTest uses CMake's regular expressions, which do not support (?:...).
    return "^(" + "|".join(re.escape(name) for name in names) + ")$"


def _run_plan(root: Path, plan: dict, output: Path) -> dict:
    if plan.get("schema") != 1 or plan.get("scope") not in ("iteration", "delivery"):
        raise ValueError("Unknown validation plan")
    if plan.get("identity") != identity(root, plan["identity"]["base"]):
        raise ValueError("Validation plan is stale")
    # Regenerate eligibility; a hand-edited plan cannot remove mandatory tests.
    current = make_plan(root, plan["scope"], plan["identity"]["base"])
    if current != plan:
        raise ValueError("Validation plan differs from current mandatory coverage")
    if not output.resolve().is_relative_to((root / "build").resolve()):
        raise ValueError("Validation output must remain under the project build directory")
    steps = [{"id": "doctor", "argv": [sys.executable, "tools/quality.py", "doctor"], "timeout": 90}]
    text_files = [name for name, value in plan["files"].items() if value != "deleted" and
                  (Path(name).suffix in quality.TEXT or Path(name).name in quality.SPECIAL)]
    if text_files:
        steps.append({"id": "whitespace", "argv": [sys.executable, "tools/quality.py", "whitespace", *text_files], "timeout": 60})
    if any(name.endswith(".md") and value != "deleted" for name, value in plan["files"].items()):
        steps.append({"id": "links", "argv": [sys.executable, "tools/validation_session.py", "check-links", "--base", plan["identity"]["base"]], "timeout": 30})
    steps.append({"id": "architecture", "argv": [sys.executable, "tools/inventory_architecture.py", "--output", "docs/architecture/source_inventory.json", "--contracts", "docs/architecture/contracts.json", "--check"], "timeout": 60})
    selected = plan["mandatory_tests"] if plan["scope"] == "delivery" else plan["iteration_selected"]
    directory = inside(root, profile(root).get("build_dir", "build/windows-gcc17"))
    if selected:
        expression = ctest_expression(selected)
        steps.append({"id": "ctest", "argv": ["ctest", "--test-dir", str(directory), "-R", expression,
                     "--output-on-failure", "--stop-on-failure", "--no-tests=error", "--output-junit", str(output / "ctest.xml")], "timeout": 900})
    def validate_result():
        if identity(root, plan["identity"]["base"]) != plan["identity"]:
            raise ValueError("Source identity changed during validation")
        if selected:
            import xml.etree.ElementTree as ET
            xml = ET.parse(output / "ctest.xml").getroot()
            cases = list(xml.iter("testcase"))
            if {case.attrib["name"] for case in cases} != set(selected) or len(cases) != len(selected) or any(list(xml.iter(tag)) for tag in ("failure", "error", "skipped")):
                raise ValueError("Executed inventory differs or contains failures/skips")
    record = execute_steps(steps, output, command_environment(root), root, validate_result)
    record.update(scope="local_regression", plan_scope=plan["scope"], stage_closure=False,
                  delivery_eligible=False, selected_tests=selected, new_unit_ids=plan["new_unit_ids"])
    write_json(output / "plan.json", plan)
    write_json(output / "report.json", record)
    return record


def verify_evidence(root: Path, receipt: dict, expected: dict) -> dict:
    if receipt.get("schema") != 1 or receipt.get("status") != "passed":
        raise ValueError("Evidence is missing, failed or unmeasured")
    if set(expected) != AXES or any(not re.fullmatch(r"[0-9a-f]{64}", v) for v in expected.values()):
        raise ValueError("Incomplete evidence identity")
    if receipt.get("identity") != expected:
        raise ValueError("Evidence identity changed")
    if receipt.get("kind") not in ("measured", "negative-control") or not receipt.get("gate_id"):
        raise ValueError("Unknown evidence scope")
    boundaries = receipt.get("positive_boundaries", 0)
    if receipt.get("scientific") and (receipt.get("kind") != "measured" or
            type(boundaries) is not int or boundaries <= 0):
        raise ValueError("Scientific evidence has no positive boundary coverage")
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        raise ValueError("Evidence artifacts are absent")
    for name, value in artifacts.items():
        if digest(inside(root, name)) != value:
            raise ValueError(f"Evidence artifact changed: {name}")
    return {"status": "verified", "scope": "identity_only", "gate_id": receipt["gate_id"], "receipt_digest": fingerprint(receipt),
            "stage_closure": False, "delivery_eligible": False}


def pre_commit(root: Path) -> int:
    # Invoke the unchanged versioned hook, with a per-process override preventing recursion.
    result = subprocess.run(["git", "-c", "core.hooksPath=.githooks", "hook", "run", "pre-commit"],
                            cwd=root, env=command_environment(root), timeout=60, check=False)
    return result.returncode


def hook(root: Path, event: dict) -> dict:
    name = event.get("hook_event_name")
    if name == "SessionStart":
        summary(root)
        text = inside(root, LOCAL + "/OPERATIONAL_SUMMARY.md").read_text(encoding="utf-8")
        return {"hookSpecificOutput": {"hookEventName": name, "additionalContext": text}}
    if name == "PostToolUse":
        # Never store raw arguments, tool results, prompts or environment variables.
        tool_name = str(event.get("tool_name", "unknown"))
        duration = event.get("duration_ms")
        row = {"schema": 1, "timestamp": time.time(),
               "tool": tool_name if re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", tool_name) else "unknown",
               "duration_ms": duration if type(duration) in (int, float) and math.isfinite(duration) and duration >= 0 else None}
        write_json(inside(root, LOCAL + "/telemetry/" + uuid.uuid4().hex + ".json"), row)
        return {}
    raise ValueError("Unsupported hook event")


def metrics(root: Path) -> dict:
    events = [read_json(path) for path in (root / LOCAL / "telemetry").glob("*.json")]
    occurrences, seconds, jobs = {}, {}, []
    for path in sorted((root / "build/validation-session").glob("*/report.json")):
        record = read_json(path)
        if record.get("schema") != 1 or not isinstance(record.get("steps"), list):
            raise ValueError("Unknown validation telemetry schema")
        jobs.append(record["status"])
        for row in record["steps"]:
            name = row["id"]
            occurrences[name] = occurrences.get(name, 0) + 1
            seconds[name] = seconds.get(name, 0) + row.get("seconds", 0)
    view = root / LOCAL / "OPERATIONAL_SUMMARY.md"
    return {"events": len(events), "timed_events": sum(row.get("duration_ms") is not None for row in events),
            "jobs": len(jobs), "failed_jobs": jobs.count("failed"),
            "command_occurrences": occurrences, "command_seconds": seconds,
            "canonical_bytes": sum((root / name).stat().st_size for name in CANONICAL),
            "summary_bytes": view.stat().st_size if view.exists() else None,
            "model_tokens": "unmeasured",
            "scope": "Local metadata and byte proxies; repeated commands are not automatically waste"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("environment", "summary", "check-summary", "check-links", "plan", "run", "verify-evidence", "pre-commit", "hook", "metrics"))
    parser.add_argument("--scope", choices=("iteration", "delivery"), default="iteration")
    parser.add_argument("--base", default="HEAD")
    parser.add_argument("--task", default="Unbound: read the current user request")
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--identity", type=Path)
    parser.add_argument("--output", help="New UTF-8 plan artifact; existing files are not overwritten")
    args = parser.parse_args()
    if args.output and args.action != "plan":
        parser.error("--output is supported only for plan")
    if args.action == "pre-commit":
        return pre_commit(ROOT)
    if args.action == "environment":
        env = command_environment(ROOT)
        import shutil
        value = {"tools": {name: shutil.which(name, path=env["PATH"]) for name in TOOLS}, "global_environment_changed": False}
        if not all(value["tools"].values()):
            raise ValueError("Required tools remain unavailable in the local execution profile")
    elif args.action == "summary":
        generated = summary(ROOT, args.task)
        value = {"status": "generated", "bytes": generated["bytes"], "sha256": generated["sha256"],
                 "view": str(ROOT / LOCAL / "OPERATIONAL_SUMMARY.md")}
    elif args.action == "check-summary":
        generated = verify_summary(ROOT)
        value = {"status": "valid", "bytes": generated["bytes"], "sha256": generated["sha256"]}
    elif args.action == "check-links":
        value = check_links(ROOT, changes(ROOT, args.base))
    elif args.action in ("plan", "run"):
        value = read_json(args.plan) if args.plan else make_plan(ROOT, args.scope, args.base)
        if args.action == "run":
            output = ROOT / "build/validation-session" / (str(time.time_ns()) + "-" + uuid.uuid4().hex[:8])
            value = run_plan(ROOT, value, output)
            print(json.dumps({"status": value["status"], "report": str(output / "report.json"),
                              "selected_tests": len(value["selected_tests"]), "delivery_eligible": False}))
            return int(value["status"] != "passed")
        target = inside(ROOT, args.output or LOCAL + "/last-plan.json")
        if args.output and target.exists():
            raise FileExistsError("Plan artifact already exists")
        write_json(target, value)
        value = {"status": "planned", "scope": value["scope"], "report": str(target),
                 "iteration_tests": len(value["iteration_selected"]),
                 "mandatory_tests": len(value["mandatory_tests"]),
                 "new_unit_cases": len(value["new_unit_ids"]), "reason": value["selection_reason"],
                 "delivery_eligible": False}
    elif args.action == "verify-evidence":
        if not args.receipt or not args.identity:
            raise ValueError("Evidence verification requires receipt and expected identity files")
        value = verify_evidence(ROOT, read_json(args.receipt), read_json(args.identity))
    elif args.action == "hook":
        payload = sys.stdin.buffer.read(65537)
        if len(payload) > 65536:
            raise ValueError("Hook input exceeds its budget")
        value = hook(ROOT, json.loads(payload.decode("utf-8")))
    else:
        value = metrics(ROOT)
    print(json.dumps(value, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        print(f"Validation session failed: {error}", file=sys.stderr)
        raise SystemExit(1)
