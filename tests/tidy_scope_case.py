#!/usr/bin/env python3
"""Exercise actual clang-tidy diagnostics across first-party and vendor headers."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def main():
    analyzer = shutil.which("clang-tidy")
    if not analyzer:
        raise ValueError("Required clang-tidy is unavailable")
    results = []
    with tempfile.TemporaryDirectory(dir=ROOT) as directory:
        root = Path(directory)
        for folder in ("include", "libs", "src"):
            (root / folder).mkdir()
        (root / "libs/vendor.h").write_text("inline int* vendor_pointer() { return 0; }\n")
        (root / "include/bridge.h").write_text('#include "../libs/vendor.h"\n')
        header = root / "include/first_party.h"
        source = root / "src/scope.cpp"
        for name, header_text, source_text, expected_failure in [
            ("lexical_vendor_path", "inline int* local_pointer() { return nullptr; }\n",
             "int main() { return 0; }\n", False),
            ("first_party_header", "inline int* local_pointer() { return 0; }\n",
             "int main() { return 0; }\n", True),
            ("first_party_source", "inline int* local_pointer() { return nullptr; }\n",
             "int* source_pointer() { return 0; }\n", True),
        ]:
            header.write_text(header_text)
            source.write_text('#include "../include/bridge.h"\n'
                              '#include "../include/first_party.h"\n' + source_text)
            process = subprocess.run(
                [analyzer, f"--config-file={ROOT / '.clang-tidy'}", str(source),
                 "--", "-std=c++17"], capture_output=True, text=True)
            output = process.stdout + process.stderr
            if bool(process.returncode) != expected_failure:
                raise ValueError(f"Unexpected scope result for {name}:\n{output}")
            if expected_failure and "modernize-use-nullptr" not in output:
                raise ValueError(f"Expected first-party diagnostic is missing:\n{output}")
            if "vendor.h:" in output:
                raise ValueError(f"Vendor header was classified as first-party:\n{output}")
            results.append({"control": name, "exit_code": process.returncode,
                            "expected_diagnostic_failure": expected_failure})
    print(json.dumps({"status": "passed", "controls": results}, indent=2))


if __name__ == "__main__":
    main()
