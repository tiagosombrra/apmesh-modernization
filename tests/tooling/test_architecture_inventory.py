"""Independent coverage and deliberately invalid controls for the static inventory."""

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("architecture_inventory", ROOT / "tools/inventory_architecture.py")
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


class ArchitectureInventoryTests(unittest.TestCase):
    def fixture(self, folder):
        root = Path(folder)
        (root / "include").mkdir()
        (root / "src").mkdir()
        (root / "include/value.h").write_text("struct Value {};\n", encoding="utf-8")
        (root / "src/main.cpp").write_text('#include "value.h"\nint main() { return 0; }\n', encoding="utf-8")
        return root

    def contract(self):
        return {"schema": "apmesh-architecture-contracts-v1", "contracts": [
            {"id": "sample", "statement": "Value exists", "limits": "Traceability only",
             "evidence": [{"path": "include/value.h", "anchor": "struct Value"}]}]}

    def test_coverage_detects_added_unit_and_changed_header(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = self.fixture(folder)
            first = inventory.inventory(root)
            self.assertEqual(first["summary"]["files"], 2)
            (root / "src/extra.cpp").write_text("int extra() { return 1; }\n", encoding="utf-8")
            (root / "include/value.h").write_text("struct Changed {};\n", encoding="utf-8")
            second = inventory.inventory(root)
            self.assertEqual(second["summary"]["translation_units"], 2)
            self.assertNotEqual(first["files"][0]["sha256"], second["files"][0]["sha256"])
            self.assertNotEqual(first, second)

    def test_empty_source_root_fails(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = self.fixture(folder)
            (root / "src/main.cpp").unlink()
            with self.assertRaisesRegex(ValueError, "Empty source root"):
                inventory.inventory(root)

    def test_comments_are_ignored_and_literal_line_is_exact(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = self.fixture(folder)
            (root / "src/main.cpp").write_text(
                '// #include "ghost.h"\n/* #include "missing.h" */\n\n#include "value.h"\n',
                encoding="utf-8")
            record = next(f for f in inventory.inventory(root)["files"] if f["path"] == "src/main.cpp")
            self.assertEqual(len(record["includes"]), 1)
            self.assertEqual(record["includes"][0]["line"], 4)
            self.assertEqual(record["includes"][0]["target"], "include/value.h")

    def test_cycle_is_reported_without_turning_it_into_runtime_proof(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = self.fixture(folder)
            (root / "include/value.h").write_text('#include "other.h"\n', encoding="utf-8")
            (root / "include/other.h").write_text('#include "value.h"\n', encoding="utf-8")
            result = inventory.inventory(root)
            self.assertEqual(result["potential_include_cycles"], [["include/other.h", "include/value.h"]])

    def test_contract_positive_and_missing_anchor_negative(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = self.fixture(folder)
            known = {"include/value.h", "src/main.cpp"}
            self.assertEqual(inventory.validate_contracts(root, self.contract(), known)["source_anchors"], 1)
            bad = self.contract()
            bad["contracts"][0]["evidence"][0]["anchor"] = "ImaginaryOwner"
            with self.assertRaisesRegex(ValueError, "Missing source anchor"):
                inventory.validate_contracts(root, bad, known)

    def test_unknown_or_outside_evidence_fails(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = self.fixture(folder)
            bad = self.contract()
            bad["contracts"][0]["evidence"][0]["path"] = "../outside.h"
            with self.assertRaisesRegex(ValueError, "Unknown source/build evidence"):
                inventory.validate_contracts(root, bad, {"include/value.h"})

    def test_empty_and_duplicate_contract_coverage_fails(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = self.fixture(folder)
            for bad in [{"schema": "apmesh-architecture-contracts-v1", "contracts": []}, self.contract()]:
                if bad["contracts"]:
                    bad["contracts"].append(copy.deepcopy(bad["contracts"][0]))
                with self.assertRaises(ValueError):
                    inventory.validate_contracts(root, bad, {"include/value.h"})

    def test_retained_production_inventory_and_contracts_are_current(self):
        retained = json.loads((ROOT / "docs/architecture/source_inventory.json").read_text(encoding="utf-8"))
        contracts = json.loads((ROOT / "docs/architecture/contracts.json").read_text(encoding="utf-8"))
        current = inventory.inventory(ROOT)
        current["contract_traceability"] = inventory.validate_contracts(
            ROOT, contracts, {f["path"] for f in current["files"] + current["build_inputs"]})
        self.assertEqual(retained, current)


if __name__ == "__main__":
    unittest.main()
