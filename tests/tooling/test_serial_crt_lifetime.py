import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from qualify_serial_crt_lifetime import inspect_lifetime, qualify_control


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


if __name__ == "__main__":
    unittest.main()
