import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from qualify_serial_crt import inspect_observer, qualify_control


def output(*, blocks=0, byte_count=0, allocations=1, denied=0, caught=0):
    return (f"SERIAL_CRT app_exit=0 heap_valid=1 iterator_level=2 allocations={allocations} "
            f"denied={denied} caught={caught} normal_blocks_delta={blocks} "
            f"normal_bytes_delta={byte_count} client_blocks_delta=0 client_bytes_delta=0\n")


def dump(retained=False):
    objects = "{73} normal block at 000001ABCDEF, 64 bytes long.\n Data: < > CD CD\n" if retained else ""
    return ("SERIAL_CRT_DUMP_BEGIN\nDumping objects ->\n" + objects
            + "Object dump complete.\nSERIAL_CRT_DUMP_END\n")


class SerialCrtControls(unittest.TestCase):
    def test_clean_release(self):
        data = inspect_observer(output(), dump())
        qualify_control("release-control", 0, data)

    def test_real_leak_requires_both_accounting_and_dump(self):
        data = inspect_observer(output(blocks=1, byte_count=64), dump(True))
        qualify_control("leak-control", 2, data)
        for text in (dump(), dump(True).replace("64 bytes", "63 bytes")):
            with self.subTest(text=text), self.assertRaises(ValueError):
                qualify_control("leak-control", 2, inspect_observer(output(blocks=1, byte_count=64), text))

    def test_balanced_retention_is_detected(self):
        data = inspect_observer(output(), dump(True))
        self.assertFalse(data["clean"])
        qualify_control("replacement-control", 0, data)
        with self.assertRaises(ValueError):
            qualify_control("release-control", 0, data)

    def test_hook_requires_actual_denial_and_catch(self):
        qualify_control("hook-control", 0, inspect_observer(output(denied=1, caught=1), dump()))
        for text in (output(), output(denied=1), output(allocations=2, denied=1, caught=1)):
            with self.subTest(text=text), self.assertRaises(ValueError):
                qualify_control("hook-control", 0, inspect_observer(text, dump()))

    def test_missing_truncated_unknown_or_duplicate_dumps_are_rejected(self):
        for text in ("", dump() + dump(), dump().replace("DUMP_END", "TRUNCATED"),
                     dump().replace("Object dump complete.", "Unrecognized report")):
            with self.subTest(text=text), self.assertRaises(ValueError):
                inspect_observer(output(), text)

    def test_missing_or_duplicate_checkpoint_is_rejected(self):
        for text in ("", output() + output(), output().replace("heap_valid=1 ", ""),
                     output().replace("iterator_level=2", "iterator_level=0"),
                     output(allocations=0)):
            with self.subTest(text=text), self.assertRaises(ValueError):
                inspect_observer(text, dump())

    def test_runtime_diagnostic_is_not_clean(self):
        with self.assertRaises(ValueError):
            inspect_observer(output(), dump() + "Debug Assertion Failed\n")

    def test_negative_net_delta_is_not_clean(self):
        data = inspect_observer(output(blocks=-1, byte_count=-64), dump())
        self.assertFalse(data["clean"])
        with self.assertRaises(ValueError):
            qualify_control("release-control", 0, data)


if __name__ == "__main__":
    unittest.main()
