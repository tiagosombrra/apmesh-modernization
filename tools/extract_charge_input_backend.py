#!/usr/bin/env python3
"""Extract exact historical caller/reader bodies for bounded original comparison.

Current probes compile the real small caller/reader units. Their unchanged
estimator constructor/destructor are extracted because the remaining historical
estimator unit contains MSVC-unsupported VLAs. Numerical members are controlled
only in the memory target; the GCC numerical target compiles their actual unit.
"""

import argparse
import hashlib
import json
from pathlib import Path


def extract(root, output):
    charge_path = root / "src/estimate/charge_estimate_process.cpp"
    reader_path = root / "src/input_output/patch_reader.cpp"
    charge = charge_path.read_text(encoding="utf-8")
    reader = reader_path.read_text(encoding="utf-8")
    destructor = "ChargeEstimateProcess::~ChargeEstimateProcess() {}"
    start = charge.index("ChargeEstimateProcess::ChargeEstimateProcess()")
    lifetime = charge[start:charge.index(destructor, start) + len(destructor)].rstrip() + "\n\n"
    assert lifetime.count("{}") == 2, "Constructor layout changed; review scope"
    output.mkdir(parents=True, exist_ok=True)
    parts = {"lifetime": lifetime}
    if not (root / "src/estimate/charge_input_estimate.cpp").exists():
        def between(text, first, last):
            begin = text.index(first)
            return text[begin:text.index(last, begin)]
        parts["caller"] = between(charge, "static bool SortByNt(",
                                   "std::vector<PointAdaptive> ChargeEstimateProcess::InterpolateControlPointsCurve(")
        reader_destructor = "PatchReader::~PatchReader() {\n  // delete patch;\n}\n"
        assert reader_destructor in reader, "Reader destructor changed; review scope"
        parts["reader_constructor"] = between(reader, "PatchReader::PatchReader()",
                                               "std::list<PatchHermite*> PatchReader::LoaderBPFileHermite()")
        parts["reader_destructor"] = reader_destructor
        parts["reader"] = between(reader, "std::list<PatchBezier*> PatchReader::LoaderBPFile(",
                                   "std::list<PatchBezier*> PatchReader::LoaderOBJFile()")
        parts["lookup"] = between(reader, "PointAdaptive PatchReader::GetPointVectorControlPoints(",
                                   "std::list<PatchBezier*> PatchReader::ParsePatchesBezier()")
    outputs = {"lifetime.cpp": '#include "estimate/charge_estimate_process.h"\n' + lifetime}
    if "caller" in parts:
        outputs["caller.cpp"] = '#include "estimate/charge_estimate_process.h"\nextern std::string INPUT_MODEL;\n' + parts["caller"]
        outputs["reader.cpp"] = '#include "input_output/patch_reader.h"\n' + "".join(parts[key] for key in ["reader_constructor", "reader_destructor", "reader", "lookup"])
    for name, text in outputs.items():
        (output / name).write_text(text, encoding="utf-8", newline="\n")
    record = {"sources": {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
                           for path in [charge_path, reader_path]},
              "parts": {name: {"sha256": hashlib.sha256(text.encode()).hexdigest(), "text": text}
                        for name, text in parts.items()},
              "outputs": {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in outputs}}
    (output / "extraction.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(extract(arguments.root, arguments.output)))
