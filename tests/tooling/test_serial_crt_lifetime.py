import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from qualify_serial_crt_lifetime import inspect_lifetime, qualify_control
from qualify_reuse_crt_lifetime import inspect_reuse, qualify


def logs(late=False, retained=False):
    mode = 2 if late and retained else 1 if late else 0
    stdout = "LIFETIME_MAIN app_exit=0 iterator_level=2 attempts=0 denied=0 caught=0\n"
    stderr = (f"LIFETIME_ALLOCATION phase={'shutdown' if late else 'main'} observed=1 request=73 bytes=64\n"
              f"LIFETIME_OWNER destroyed=1 late_mode={mode}\nLIFETIME_DUMP_BEGIN\nDumping objects ->\n")
    if retained:
        stderr += "{73} normal block at 0x1234, 64 bytes long.\n Data: < > CD CD\n"
    stderr += ("Object dump complete.\nLIFETIME_DUMP_END\nLIFETIME_FINAL active=1 heap_valid=1 "
               f"normal_blocks_delta={int(retained)} normal_bytes_delta={64 * retained} "
               "client_blocks_delta=0 client_bytes_delta=0\n")
    return stdout, stderr


class ExecutableLifetimeControls(unittest.TestCase):
    def test_release_and_shutdown_release_require_actual_heap_allocation(self):
        for late, mode in ((False, "release"), (True, "late-release")):
            with self.subTest(mode=mode):
                qualify_control(mode, inspect_lifetime(*logs(late), 0))
                out, err = logs(late)
                with self.assertRaises(ValueError):
                    inspect_lifetime(out, err.replace("observed=1", "observed=0"), 0)

    def test_main_and_shutdown_retention_are_detected_despite_zero_native_exit(self):
        for late, mode in ((False, "retention"), (True, "late-retention")):
            with self.subTest(mode=mode):
                data = inspect_lifetime(*logs(late, True), 0)
                self.assertFalse(data["clean"])
                qualify_control(mode, data)

    def test_wrong_request_is_not_retention_calibration(self):
        out, err = logs(True, True)
        data = inspect_lifetime(out, err.replace("{73}", "{74}"), 0)
        with self.assertRaises(ValueError):
            qualify_control("late-retention", data)

    def test_missing_early_observer_or_wrong_destructor_order_is_not_clean(self):
        out, err = logs()
        for changed in (err.replace("active=1", "active=0"),
                        err.replace("LIFETIME_OWNER destroyed=1 late_mode=0\n", ""),
                        err.replace("LIFETIME_OWNER destroyed=1 late_mode=0\n", "")
                        + "LIFETIME_OWNER destroyed=1 late_mode=0\n"):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                inspect_lifetime(out, changed, 0)

    def test_newer_object_dump_overrides_zero_net_delta(self):
        out, err = logs(True, True)
        data = inspect_lifetime(out, err.replace("normal_blocks_delta=1", "normal_blocks_delta=0")
                                .replace("normal_bytes_delta=64", "normal_bytes_delta=0"), 0)
        self.assertFalse(data["clean"])

    def test_denial_requires_second_attempt_catch_and_clean_unwind(self):
        out, err = logs()
        out = out.replace("attempts=0 denied=0 caught=0", "attempts=2 denied=1 caught=1")
        qualify_control("denial", inspect_lifetime(out, err, 0))
        with self.assertRaises(ValueError):
            qualify_control("denial", inspect_lifetime(out.replace("caught=1", "caught=0"), err, 0))

    def test_truncated_duplicate_or_unknown_dump_cannot_pass(self):
        out, err = logs()
        for changed in (err + err, err.replace("LIFETIME_DUMP_END", "TRUNCATED"),
                        err.replace("Object dump complete.", "Unrecognized dump row")):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                inspect_lifetime(out, changed, 0)

    def test_signed_native_failure_matches_only_its_windows_process_code(self):
        out, err = logs()
        out = out.replace("app_exit=0", "app_exit=-1")
        data = inspect_lifetime(out, err, 0xffffffff)
        self.assertEqual(data["app_exit"], -1)
        self.assertTrue(data["clean"])
        for wrong in (0, 1, 0xfffffffe):
            with self.subTest(wrong=wrong), self.assertRaises(ValueError):
                inspect_lifetime(out, err, wrong)

    def test_raw_windows_line_endings_preserve_final_checkpoint_meaning(self):
        out, err = logs(True, True)
        data = inspect_lifetime(out.replace("\n", "\r\n"), err.replace("\n", "\r\n"), 0)
        qualify_control("late-retention", data)
        self.assertFalse(data["clean"])


class AdaptiveReuseLifetimeControls(unittest.TestCase):
    def test_first_failed_control_preserves_streams_and_stops_before_models(self):
        from unittest.mock import patch
        from subprocess import CompletedProcess
        import json
        import tempfile
        out, err = logs()
        captures = [(out.encode('utf-8'), err.encode('utf-8')), (b'partial control\r\n', b'')]
        def process(arguments, **kwargs):
            stdout, stderr = captures.pop(0)
            kwargs['stdout'].write(stdout)
            kwargs['stdout'].flush()
            kwargs['stderr'].write(stderr)
            kwargs['stderr'].flush()
            return CompletedProcess(arguments, 0)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary = root / 'binary'
            binary.write_bytes(b'controller-only fixture, never executed')
            output = root / 'result'
            with patch('qualify_reuse_crt_lifetime.subprocess.run', side_effect=process) as launch:
                with self.assertRaises(ValueError):
                    qualify(binary, output, {})
            self.assertEqual(launch.call_count, 2)
            result = json.loads((output / 'report.json').read_text(encoding='utf-8'))
            self.assertEqual(result['status'], 'stopped_at_first_failure')
            self.assertEqual([row['case'] for row in result['cases']], ['release', 'global-release'])
            self.assertEqual((output / 'global-release.stdout').read_bytes(), b'partial control\r\n')
            self.assertEqual((output / 'global-release.stderr').read_bytes(), b'')

    def logs(self):
        main, stderr = logs()
        stderr = '\n'.join(line for line in stderr.splitlines()
                           if not line.startswith('LIFETIME_ALLOCATION ')) + '\n'
        rows = ('adaptive_reuse call=0 exit=0 archived=5 calls=14660 imax=1542\n'
                'adaptive_reuse call=1 exit=0 archived=5 calls=14660 imax=1542\n')
        return rows + main, stderr

    def test_two_complete_checked_calls_and_final_teardown(self):
        out, err = self.logs()
        result = inspect_reuse(out.replace('\n', '\r\n'), err.replace('\n', '\r\n'), 0, 5)
        self.assertEqual([row['index'] for row in result['calls']], [0, 1])
        self.assertTrue(result['lifetime']['clean'])

    def test_clean_teardown_without_second_call_is_not_qualification(self):
        out, err = self.logs()
        with self.assertRaises(ValueError):
            inspect_reuse('\n'.join(line for line in out.splitlines() if 'call=1' not in line), err, 0, 5)

    def test_duplicate_call_is_not_repeated_execution(self):
        out, err = self.logs()
        with self.assertRaises(ValueError):
            inspect_reuse(out.replace('call=1', 'call=0'), err, 0, 5)

    def test_native_failure_cannot_hide_behind_clean_final_heap(self):
        out, err = self.logs()
        with self.assertRaises(ValueError):
            inspect_reuse(out.replace('call=1 exit=0', 'call=1 exit=1'), err, 0, 5)

    def test_wrong_archive_inventory_is_rejected(self):
        out, err = self.logs()
        with self.assertRaises(ValueError):
            inspect_reuse(out.replace('call=1 exit=0 archived=5', 'call=1 exit=0 archived=4'), err, 0, 5)

    def test_counter_drift_is_rejected(self):
        out, err = self.logs()
        with self.assertRaises(ValueError):
            inspect_reuse(out.replace('call=1 exit=0 archived=5 calls=14660',
                                     'call=1 exit=0 archived=5 calls=14661'), err, 0, 5)

    def test_unknown_native_diagnostic_is_rejected(self):
        out, err = self.logs()
        with self.assertRaises(ValueError):
            inspect_reuse('unknown native diagnostic\n' + out, err, 0, 5)

    def test_retained_object_cannot_pass_with_two_complete_calls(self):
        out, _ = self.logs()
        _, err = logs(retained=True)
        with self.assertRaises(ValueError):
            inspect_reuse(out, err, 0, 5)


if __name__ == "__main__":
    unittest.main()
