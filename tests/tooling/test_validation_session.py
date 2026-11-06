"""Independent negative controls for local orchestration, identities and baseline coverage."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validation_session as session


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        for name in session.CANONICAL:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Canonical\n", encoding="utf-8")
        (self.root / "docs/PROJECT_STATE.md").write_text(
            "## Current checkpoint and active work\n\nKeep the current scope.\n", encoding="utf-8")
        (self.root / "docs/MODERNIZATION_PLAN.md").write_text(
            "## Current production priority\n\nPreserve every required gate.\n", encoding="utf-8")
        self.tests = [{"name": "tooling.controls", "command": ["python", "tests"]},
                      {"name": "application.mesh", "command": [str(self.root / "bin/probe.exe")]}]
        self.baseline = {"schema": 1, "ctest": self.tests, "unit_ids": ["existing.case"]}
        session.write_json(self.root / session.LOCAL / "validation-baseline.json", self.baseline)

    def tearDown(self):
        self.temporary.cleanup()

    def state(self, *args):
        return {"revision": "a" * 40, "base": "HEAD", "changes": {},
                "canonical": {name: session.digest(self.root / name) for name in session.CANONICAL}}

    def step(self, name, program, **kwargs):
        return {"id": name, "argv": [sys.executable, "-c", program], "timeout": 10, **kwargs}

    def chain(self, steps, final_check=None):
        return session.execute_steps(steps, self.root / "run", dict(os.environ), self.root, final_check)

    def sentinel(self):
        return self.step("sentinel", "from pathlib import Path; Path('mutation').write_text('bad')")

    def test_nonzero_prerequisite_blocks_mutation(self):
        result = self.chain([self.step("fail", "raise SystemExit(7)"), self.sentinel()])
        self.assertEqual(result["status"], "failed")
        self.assertEqual(len(result["steps"]), 1)
        self.assertFalse((self.root / "mutation").exists())

    def test_malformed_prerequisite_blocks_mutation(self):
        path = self.root / "prerequisite.json"
        path.write_text("not JSON", encoding="utf-8")
        result = self.chain([self.step("invalid", "pass", result_json=str(path)), self.sentinel()])
        self.assertEqual(result["status"], "failed")
        self.assertFalse((self.root / "mutation").exists())

    def test_bad_encoding_blocks_mutation(self):
        path = self.root / "prerequisite.json"
        path.write_bytes(b'\xff\xfe{"status":"passed"}')
        result = self.chain([self.step("invalid", "pass", result_json=str(path)), self.sentinel()])
        self.assertEqual(result["status"], "failed")
        self.assertFalse((self.root / "mutation").exists())

    def test_nonobject_prerequisite_blocks_mutation(self):
        path = self.root / "prerequisite.json"
        session.write_json(path, ["passed"])
        result = self.chain([self.step("invalid", "pass", result_json=str(path)), self.sentinel()])
        self.assertEqual(result["status"], "failed")
        self.assertFalse((self.root / "mutation").exists())

    def test_unmeasured_status_blocks_mutation(self):
        path = self.root / "prerequisite.json"
        session.write_json(path, {"status": "running"})
        result = self.chain([self.step("unknown", "pass", result_json=str(path)), self.sentinel()])
        self.assertEqual(result["status"], "failed")
        self.assertFalse((self.root / "mutation").exists())

    def test_successful_prerequisite_allows_next_step(self):
        path = self.root / "prerequisite.json"
        session.write_json(path, {"status": "passed"})
        result = self.chain([self.step("ready", "pass", result_json=str(path)),
                             self.step("next", "from pathlib import Path; Path('observed').write_text('yes')")])
        self.assertEqual(result["status"], "passed")
        self.assertEqual((self.root / "observed").read_text(), "yes")

    def test_final_check_runs_before_success_is_published(self):
        def fail():
            self.assertFalse((self.root / "run/report.json").exists())
            latest = sorted((self.root / "run").glob("progress-*.json"))[-1]
            self.assertEqual(session.read_json(latest)["status"], "running")
            raise ValueError("identity changed")
        result = self.chain([self.step("ready", "pass")], fail)
        self.assertEqual(result["status"], "failed")
        self.assertIn("identity changed", result["error"])

    def test_progress_readers_never_require_replacing_a_receipt(self):
        original = session.write_json
        def reject_replacement(path, value):
            if path.exists():
                raise PermissionError("An observer denies replacement of an existing receipt")
            original(path, value)
        with patch.object(session, "write_json", side_effect=reject_replacement):
            result = self.chain([self.step("first", "pass"), self.step("second", "pass")])
        self.assertEqual(result["status"], "passed")
        progress = sorted((self.root / "run").glob("progress-*.json"))
        self.assertEqual(len(progress), 4)
        self.assertTrue(all(session.read_json(path)["status"] == "running" for path in progress))
        self.assertEqual(session.read_json(self.root / "run/report.json")["status"], "passed")

    def test_timeout_stops_owned_process_and_later_steps(self):
        result = self.chain([self.step("slow", "import time; time.sleep(10)", timeout=0.1), self.sentinel()])
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["steps"][0]["exit_code"], 124)
        self.assertFalse((self.root / "mutation").exists())

    def test_interruption_reaps_descendants_before_releasing_lock(self):
        heartbeat = self.root / "heartbeat"
        child = "import pathlib,time; p=pathlib.Path('heartbeat'); " + \
                "exec('while True:\\n with p.open(\"ab\") as f: f.write(b\"x\")\\n time.sleep(0.02)')"
        parent = "import subprocess,sys; subprocess.Popen([sys.executable,'-c'," + repr(child) + "]).wait()"
        original_wait, original_stop = subprocess.Popen.wait, session.stop_process_tree
        interrupted = False
        def wait(process, timeout=None):
            nonlocal interrupted
            if not interrupted:
                interrupted = True
                deadline = time.monotonic() + 5
                while not heartbeat.exists() or heartbeat.stat().st_size == 0:
                    if time.monotonic() > deadline:
                        raise AssertionError("Descendant did not reach its independent heartbeat")
                    time.sleep(0.01)
                raise KeyboardInterrupt
            return original_wait(process, timeout=timeout)
        def stop(process, stream):
            self.assertTrue((self.root / session.LOCAL / "run.lock").exists())
            original_stop(process, stream)
            self.assertIsNotNone(process.poll())
        with patch.object(subprocess.Popen, "wait", new=wait), \
                patch.object(session, "stop_process_tree", side_effect=stop), \
                self.assertRaises(KeyboardInterrupt):
            with session.validation_lock(self.root):
                self.chain([self.step("parent", parent), self.sentinel()])
        self.assertFalse((self.root / session.LOCAL / "run.lock").exists())
        size = heartbeat.stat().st_size
        time.sleep(0.15)
        self.assertEqual(heartbeat.stat().st_size, size)
        self.assertFalse((self.root / "mutation").exists())
        self.assertEqual(session.read_json(self.root / "run/report.json")["status"], "failed")

    def test_unconfirmed_process_cleanup_preserves_lock(self):
        process = Mock(pid=1234)
        process.wait.side_effect = subprocess.TimeoutExpired("fixture", 0.1)
        with patch.object(session.subprocess, "Popen", return_value=process), \
                patch.object(session, "stop_process_tree", side_effect=session.ProcessCleanupError("unconfirmed")), \
                self.assertRaises(session.ProcessCleanupError):
            with session.validation_lock(self.root):
                self.chain([self.step("unconfirmed", "pass"), self.sentinel()])
        self.assertTrue((self.root / session.LOCAL / "run.lock").exists())
        self.assertFalse((self.root / "mutation").exists())

    def test_zero_exit_during_wait_cannot_report_success(self):
        process = Mock(pid=1234)
        process.wait.side_effect = SystemExit(0)
        with patch.object(session.subprocess, "Popen", return_value=process), \
                patch.object(session, "stop_process_tree") as stop, \
                self.assertRaises(SystemExit) as interrupted:
            with session.validation_lock(self.root):
                self.chain([self.step("interrupted", "pass"), self.sentinel()])
        self.assertEqual(interrupted.exception.code, 130)
        stop.assert_called_once()
        self.assertFalse((self.root / session.LOCAL / "run.lock").exists())
        self.assertFalse((self.root / "mutation").exists())

    def test_empty_or_invalid_steps_rejected_before_execution(self):
        for steps in ([], [self.step("../escape", "pass")],
                      [self.step("infinite", "pass", timeout=float("inf"))],
                      [self.step("nan", "pass", timeout=float("nan"))],
                      [self.step("boolean", "pass", timeout=True)],
                      [self.step("first", "pass"), {"id": "invalid", "argv": [], "timeout": 1}]):
            with self.subTest(steps=steps), self.assertRaises(ValueError):
                self.chain(steps)
        self.assertFalse((self.root / "run").exists())

    def test_concurrent_runner_is_rejected_and_owner_lock_preserved(self):
        with session.validation_lock(self.root):
            owner = session.read_json(self.root / session.LOCAL / "run.lock")
            with self.assertRaises(ValueError):
                with session.validation_lock(self.root):
                    self.fail("A second runner entered")
            self.assertEqual(session.read_json(self.root / session.LOCAL / "run.lock"), owner)
        self.assertFalse((self.root / session.LOCAL / "run.lock").exists())

    def test_runner_lock_released_after_failure(self):
        with self.assertRaises(RuntimeError):
            with session.validation_lock(self.root):
                raise RuntimeError("fixture failure")
        with session.validation_lock(self.root):
            self.assertTrue((self.root / session.LOCAL / "run.lock").exists())

    def test_failed_run_cannot_be_overwritten(self):
        self.chain([self.step("fail", "raise SystemExit(1)")])
        with self.assertRaises(FileExistsError):
            self.chain([self.step("ready", "pass")])

    def test_baseline_allows_explicit_superset(self):
        session.check_baseline(self.baseline, self.tests + [{"name": "new.test"}],
                               ["existing.case", "new.case"])

    def test_missing_required_ctest_is_rejected(self):
        with self.assertRaises(ValueError):
            session.check_baseline(self.baseline, self.tests[:1], ["existing.case"])

    def test_missing_required_unit_is_rejected(self):
        with self.assertRaises(ValueError):
            session.check_baseline(self.baseline, self.tests, ["replacement.case"])

    def test_empty_or_duplicate_baseline_cannot_qualify(self):
        with self.assertRaises(ValueError):
            session.check_baseline({}, [], [])
        with self.assertRaises(ValueError):
            session.check_baseline(self.baseline, self.tests * 2, ["existing.case"])
        with self.assertRaises(ValueError):
            session.check_baseline(self.baseline, self.tests, ["existing.case"] * 2)

    def plan(self, files):
        with patch.object(session, "test_inventory", return_value=self.tests), \
                patch.object(session, "unit_ids", return_value=["existing.case", "new.case"]), \
                patch.object(session, "identity", side_effect=self.state), \
                patch.object(session, "changes", return_value=files):
            return session.make_plan(self.root, "iteration")

    def test_document_iteration_never_removes_delivery_gates(self):
        plan = self.plan({"docs/note.md": "a" * 64})
        self.assertEqual(plan["iteration_selected"], [])
        self.assertEqual(set(plan["mandatory_tests"]), {x["name"] for x in self.tests})
        self.assertFalse(plan["delivery_eligible"])

    def test_tooling_iteration_keeps_complete_tooling_suite(self):
        plan = self.plan({"tools/quality.py": "a" * 64})
        self.assertEqual(plan["iteration_selected"], ["tooling.controls"])
        self.assertEqual(plan["new_unit_ids"], ["new.case"])

    def test_native_ctest_filter_selects_exact_names(self):
        names = ["application.mesh", "tooling.special+control"]
        decoys = ["applicationXmesh", "application.mesh.extra", "tooling.specialcontrol"]
        (self.root / "CTestTestfile.cmake").write_text("\n".join(
            f'add_test("{name}" "unused")' for name in names + decoys), encoding="utf-8")
        result = subprocess.run(["ctest", "--test-dir", str(self.root), "--show-only=json-v1",
                                 "-R", session.ctest_expression(names)], check=True,
                                capture_output=True, text=True, encoding="utf-8", timeout=10)
        self.assertEqual({row["name"] for row in json.loads(result.stdout)["tests"]}, set(names))

    def test_documentation_does_not_broaden_tooling_iteration(self):
        plan = self.plan({"tools/quality.py": "a" * 64, "docs/note.md": "b" * 64})
        self.assertEqual(plan["iteration_selected"], ["tooling.controls"])

    def test_local_links_require_existing_targets(self):
        path = self.root / "docs/link.md"
        path.write_text("[state](PROJECT_STATE.md) [web](https://example.invalid)\n", encoding="utf-8")
        value = session.check_links(self.root, {"docs/link.md": "a" * 64})
        self.assertEqual(value["local_targets"], 1)
        self.assertIn("fragments", value["scope"])
        path.write_text("[broken](absent.md)\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            session.check_links(self.root, {"docs/link.md": "a" * 64})

    def test_unknown_and_shared_header_impact_is_conservative(self):
        for name in ("unknown.bin", "include/shared.h", "CMakePresets.json",
                     "docs/architecture/contracts.json", "docs/tool.py"):
            with self.subTest(name=name):
                self.assertEqual(len(self.plan({name: "a" * 64})["iteration_selected"]), 2)

    def test_private_cpp_uses_actual_compiler_target(self):
        source = self.root / "tests/private.cpp"
        source.parent.mkdir(exist_ok=True)
        source.write_text("int main() {}\n", encoding="utf-8")
        session.write_json(self.root / "build/windows-gcc17/compile_commands.json",
                           [{"file": str(source), "output": "CMakeFiles/probe.dir/private.cpp.obj"}])
        self.assertEqual(self.plan({"tests/private.cpp": "a" * 64})["iteration_selected"],
                         ["application.mesh"])

    def test_foreign_or_missing_build_source_identity_is_rejected(self):
        directory = self.root / "build/fixture"
        directory.mkdir(parents=True)
        for text in ("# no source identity\n", f"CMAKE_HOME_DIRECTORY:INTERNAL={self.root / 'other'}\n"):
            (directory / "CMakeCache.txt").write_text(text, encoding="utf-8")
            with self.assertRaises(ValueError):
                session.verify_build_root(self.root, directory)
        (directory / "CMakeCache.txt").write_text(
            f"CMAKE_HOME_DIRECTORY:INTERNAL={self.root}\n", encoding="utf-8")
        session.verify_build_root(self.root, directory)

    def test_native_build_prevents_stale_artifact_regression_pass(self):
        directory = self.root / "build/fixture"
        env = session.command_environment(ROOT)
        (self.root / "CMakeLists.txt").write_text('''cmake_minimum_required(VERSION 3.20)
project(ArtifactIdentity NONE)
enable_testing()
add_custom_command(OUTPUT "${CMAKE_BINARY_DIR}/artifact.txt"
  COMMAND "${CMAKE_COMMAND}" -E copy "${CMAKE_SOURCE_DIR}/source.txt" "${CMAKE_BINARY_DIR}/artifact.txt"
  DEPENDS "${CMAKE_SOURCE_DIR}/source.txt")
add_custom_target(probe ALL DEPENDS "${CMAKE_BINARY_DIR}/artifact.txt")
add_test(NAME application.mesh COMMAND "${CMAKE_COMMAND}" -E compare_files
  "${CMAKE_SOURCE_DIR}/source.txt" "${CMAKE_BINARY_DIR}/artifact.txt")
''', encoding="utf-8")
        source = self.root / "source.txt"
        source.write_text("original\n", encoding="utf-8")
        def run(argv, check=True):
            return subprocess.run(argv, cwd=self.root, env=env, capture_output=True,
                                  timeout=30, check=check)
        run(["cmake", "-S", str(self.root), "-B", str(directory), "-G", "Ninja"])
        run(["cmake", "--build", str(directory)])
        source.write_text("changed\n", encoding="utf-8")
        newer = (directory / "artifact.txt").stat().st_mtime + 2
        os.utime(source, (newer, newer))
        self.assertNotEqual(run(["ctest", "--test-dir", str(directory)], check=False).returncode, 0)
        session.write_json(self.root / session.LOCAL / "environment.json",
                           {"schema": 1, "tools": {}, "build_dir": "build/fixture"})
        plan = {"schema": 1, "scope": "delivery", "identity": self.state(), "files": {},
                "mandatory_tests": ["application.mesh"], "iteration_selected": ["application.mesh"],
                "new_unit_ids": []}
        original_execute = session.execute_steps
        def native_steps(steps, *args, **kwargs):
            selected = [step for step in steps if step["id"] in ("build", "ctest")]
            self.assertEqual([step["id"] for step in selected], ["build", "ctest"])
            return original_execute(selected, *args, **kwargs)
        with patch.object(session, "identity", side_effect=self.state), \
                patch.object(session, "make_plan", return_value=plan), \
                patch.object(session, "command_environment", return_value=env), \
                patch.object(session, "execute_steps", side_effect=native_steps):
            result = session.run_plan(self.root, plan, self.root / "build/run")
        self.assertEqual(result["status"], "passed")
        self.assertEqual(source.read_bytes(), (directory / "artifact.txt").read_bytes())
        with (self.root / "CMakeLists.txt").open("a", encoding="utf-8") as stream:
            stream.write('add_test(NAME application.new COMMAND "${CMAKE_COMMAND}" -E true)\n')
        with patch.object(session, "identity", side_effect=self.state), \
                patch.object(session, "make_plan", return_value=plan), \
                patch.object(session, "command_environment", return_value=env), \
                patch.object(session, "execute_steps", side_effect=native_steps):
            changed = session.run_plan(self.root, plan, self.root / "build/run-grown")
        self.assertEqual(changed["status"], "failed")
        self.assertEqual([step["id"] for step in changed["steps"]], ["build"])
        self.assertIn("inventory", changed["steps"][0]["error"])

    def test_forged_or_stale_plan_stops_before_execution(self):
        plan = {"schema": 1, "scope": "delivery", "identity": self.state()}
        with patch.object(session, "identity", side_effect=self.state), \
                patch.object(session, "make_plan", return_value={**plan, "mandatory_tests": ["required"]}), \
                patch.object(session, "execute_steps") as execute:
            with self.assertRaises(ValueError):
                session.run_plan(self.root, plan, self.root / "build/run")
            execute.assert_not_called()
        with patch.object(session, "identity", return_value={}), self.assertRaises(ValueError):
            session.run_plan(self.root, plan, self.root / "build/run")

    def test_environment_is_per_child_and_handles_spaces(self):
        executable = self.root / "tools with spaces/tool.exe"
        executable.parent.mkdir()
        executable.write_bytes(b"fixture")
        session.write_json(self.root / session.LOCAL / "environment.json",
                           {"schema": 1, "tools": {"git": str(executable)}})
        original = os.environ.get("PATH")
        value = session.command_environment(self.root)
        self.assertTrue(value["PATH"].startswith(str(executable.parent)))
        self.assertEqual(os.environ.get("PATH"), original)

    def test_missing_configured_tool_does_not_fall_back(self):
        session.write_json(self.root / session.LOCAL / "environment.json",
                           {"schema": 1, "tools": {"git": str(self.root / "missing.exe")}})
        with self.assertRaises(ValueError):
            session.command_environment(self.root)

    def test_paths_cannot_escape_project(self):
        with self.assertRaises(ValueError):
            session.inside(self.root, "../outside")

    def test_summary_budget_integrity_and_staleness(self):
        with patch.object(session, "identity", side_effect=self.state):
            value = session.summary(self.root, "Local infrastructure only")
            self.assertLessEqual(value["bytes"], 6144)
            self.assertEqual(session.verify_summary(self.root), value)
            (self.root / "docs/PROJECT_STATE.md").write_text("changed\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                session.verify_summary(self.root)

    def test_summary_tampering_and_oversize_are_rejected(self):
        with patch.object(session, "identity", side_effect=self.state):
            session.summary(self.root)
            (self.root / session.LOCAL / "OPERATIONAL_SUMMARY.md").write_text("tampered\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                session.verify_summary(self.root)
            with self.assertRaises(ValueError):
                session.summary(self.root, "x" * 7000)

    def test_summary_requires_known_canonical_sections(self):
        (self.root / "docs/MODERNIZATION_PLAN.md").write_text("# Unknown layout\n", encoding="utf-8")
        with patch.object(session, "identity", side_effect=self.state), self.assertRaises(ValueError):
            session.summary(self.root)

    def evidence(self):
        path = self.root / "observed.json"
        path.write_text('{"observed":"positive"}\n', encoding="utf-8")
        axes = {key: session.fingerprint(key) for key in session.AXES}
        return {"schema": 1, "status": "passed", "kind": "measured", "gate_id": "fixture",
                "identity": axes, "artifacts": {"observed.json": session.digest(path)}}, axes

    def test_evidence_verifies_identity_without_granting_delivery(self):
        receipt, axes = self.evidence()
        value = session.verify_evidence(self.root, receipt, axes)
        self.assertEqual(value["scope"], "identity_only")
        self.assertFalse(value["delivery_eligible"])

    def test_each_evidence_identity_axis_invalidates_reuse(self):
        receipt, axes = self.evidence()
        for key in session.AXES:
            with self.subTest(axis=key), self.assertRaises(ValueError):
                session.verify_evidence(self.root, receipt, {**axes, key: "0" * 64})

    def test_failed_missing_and_modified_evidence_rejected(self):
        receipt, axes = self.evidence()
        for status in ("failed", "running", "timeout", "unmeasured"):
            with self.subTest(status=status), self.assertRaises(ValueError):
                session.verify_evidence(self.root, {**receipt, "status": status}, axes)
        with self.assertRaises(ValueError):
            session.verify_evidence(self.root, {**receipt, "artifacts": {}}, axes)
        (self.root / "observed.json").write_text("changed", encoding="utf-8")
        with self.assertRaises(ValueError):
            session.verify_evidence(self.root, receipt, axes)

    def test_scientific_zero_or_invalid_coverage_never_qualifies(self):
        receipt, axes = self.evidence()
        for count in (0, -1, "1", True):
            with self.subTest(count=count), self.assertRaises(ValueError):
                session.verify_evidence(self.root, {**receipt, "scientific": True,
                                                  "positive_boundaries": count}, axes)

    def test_hooks_are_bounded_and_do_not_store_private_payloads(self):
        with patch.object(session, "identity", side_effect=self.state):
            value = session.hook(self.root, {"hook_event_name": "SessionStart"})
        self.assertLessEqual(len(value["hookSpecificOutput"]["additionalContext"].encode()), 6144)
        value = session.hook(self.root, {"hook_event_name": "PostToolUse", "tool_name": "exec",
                                        "tool_input": "PRIVATE", "tool_response": "SECRET"})
        self.assertEqual(value, {})
        events = list((self.root / session.LOCAL / "telemetry").glob("*.json"))
        self.assertEqual(len(events), 1)
        text = events[0].read_text(encoding="utf-8")
        self.assertNotIn("SECRET", text)
        self.assertNotIn("PRIVATE", text)
        self.assertIsNone(json.loads(text)["duration_ms"])

    def test_unknown_hook_does_not_succeed(self):
        with self.assertRaises(ValueError):
            session.hook(self.root, {"hook_event_name": "Unsupported"})

    def test_metrics_do_not_invent_tokens_or_missing_durations(self):
        session.write_json(self.root / "build/validation-session/job/report.json",
                           {"schema": 1, "status": "failed", "steps": [
                               {"id": "doctor", "seconds": 2}, {"id": "doctor", "seconds": 3}]})
        value = session.metrics(self.root)
        self.assertEqual(value["failed_jobs"], 1)
        self.assertEqual(value["command_occurrences"], {"doctor": 2})
        self.assertEqual(value["command_seconds"], {"doctor": 5})
        self.assertEqual(value["model_tokens"], "unmeasured")
        self.assertIsNone(value["summary_bytes"])

    def test_metrics_preserve_unfinished_jobs_as_unmeasured(self):
        session.write_json(self.root / "build/validation-session/job/progress-0000.json",
                           {"schema": 1, "status": "running", "steps": []})
        value = session.metrics(self.root)
        self.assertEqual(value["unfinished_jobs"], 1)
        self.assertEqual(value["failed_jobs"], 0)
        self.assertEqual(value["jobs"], 0)


if __name__ == "__main__":
    unittest.main()
