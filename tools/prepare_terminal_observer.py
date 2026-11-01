#!/usr/bin/env python3
"""Prepare reversible test-only interception of the actual Adapter AFT calls."""

import argparse
import hashlib
import json
from pathlib import Path


def prepare(root: Path, output: Path) -> dict:
    root, output = root.resolve(), output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    specifications = [
        ("src/adapter/adapter.cpp", "adapter.cpp", "avanco.execute(mesh_old)",
         "terminal_observer::Execute(avanco, mesh_old)", 2,
         '#include "execute_observer.h"\n'),
        ("tests/typed_domain_failure_fixture.h", "typed_domain_failure_fixture.h",
         '#include "domain_candidate_fixture.h"', '#include "allocation_observer.h"', 1, ""),
    ]
    records = []
    for source, name, old, new, count, prefix in specifications:
        original = (root / source).read_bytes()
        text = original.decode("utf-8")
        if text.count(old) != count or new in text:
            raise ValueError(f"Unexpected terminal observer source: {source}")
        generated = prefix + text.replace(old, new)
        restored = generated[len(prefix):].replace(new, old)
        if restored.encode("utf-8") != original:
            raise ValueError(f"Terminal observer does not reverse exactly: {source}")
        extra_replacements = 0
        if name == "typed_domain_failure_fixture.h":
            allocation = "std::make_unique<SubMesh>()"
            external = "std::unique_ptr<SubMesh>(TerminalControlAllocateSubMesh())"
            if generated.count(allocation) != 1 or external in generated:
                raise ValueError("Unexpected native unwind allocation control")
            generated = generated.replace(allocation, external)
            if generated.replace(external, allocation)[len(prefix):].replace(new, old).encode("utf-8") != original:
                raise ValueError("Native unwind allocation control does not reverse exactly")
            extra_replacements = 1
        data = generated.encode("utf-8")
        (output / name).write_bytes(data)
        records.append({"source": source, "generated": name, "replacements": count + extra_replacements,
                        "source_sha256": hashlib.sha256(original).hexdigest(),
                        "generated_sha256": hashlib.sha256(data).hexdigest(),
                        "exact_byte_reversal": True})
    report = {"status": "passed", "files": records,
              "scope": "Test-only AFT call interception and allocation observer dependency; all remaining source bytes exact"}
    (output / "preparation.json").write_text(json.dumps(report, indent=2) + "\n",
                                            encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root, args.output)))
