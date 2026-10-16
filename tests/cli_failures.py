"""Exercise invalid CLI/configuration/model input against the real executable."""

import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def verify_failures(executable: Path, workspace: Path) -> list[dict]:
    workspace.mkdir(parents=True, exist_ok=True)
    valid_vertices = "".join(f"v {i % 4} {i // 4} 0\n" for i in range(16))
    valid_model = valid_vertices + "p " + " ".join(str(i) for i in range(16)) + "\n"
    models = {"missing_model": None, "empty_model": "", "unknown_record": "garbage\n",
              "short_vertex": "v 0 0\n", "extra_coordinate": "v 0 0 0 1\n",
              "nan_coordinate": "v nan 0 0\n", "short_patch": valid_vertices + "p 0\n",
              "out_of_bounds_patch": valid_vertices + "p " + " ".join(["16"] * 16) + "\n",
              "negative_patch_index": valid_vertices + "p " + " ".join(["-1"] * 16) + "\n",
              "no_patches": valid_vertices, "indented_record": " v 0 0 0\n"}
    settings = {"bad_config_syntax": "NOT A SETTING\n", "unknown_key": "NUM_THEADS=1\n",
                "invalid_integer": "NUM_THREADS=1.5\n", "zero_threads": "NUM_THREADS=0\n",
                "invalid_float": "EPSYLON=1e-7junk\n", "nan_float": "EPSYLON=nan\n",
                "infinite_float": "EPSYLON=inf\n", "invalid_mode": "WRITE_MODE=garbage\n",
                "duplicate_key": "NUM_THREADS=1\nNUM_THREADS=2\n"}
    results = []
    with tempfile.TemporaryDirectory(dir=workspace) as temporary:
        folder = Path(temporary)
        model = folder / "model.bp"
        config = folder / "config.conf"
        for name in [*models, *settings, "missing_config", "missing_arguments", "extra_arguments"]:
            case = folder / name
            case.mkdir()
            content = models[name] if name in models else valid_model
            if model.exists():
                model.unlink()
            if content is not None:
                model.write_text(content, encoding="utf-8")
            base = f"INPUT_MODEL={model.as_posix()}\nOUTPUT_PREFIX={(case/'mesh').as_posix()}\n"
            config.write_text(base + settings.get(name, ""), encoding="utf-8")
            args = ["--config", str(config)]
            if name == "missing_config":
                args = ["--config", str(folder / "absent.conf")]
            elif name == "missing_arguments":
                args = []
            elif name == "extra_arguments":
                args.append("unexpected")
            process = subprocess.run([str(executable.resolve()), *args], cwd=ROOT,
                                     capture_output=True, timeout=10)
            record = {"case": name, "exit_code": process.returncode,
                      "diagnostic": process.stderr.decode(errors="replace").strip(),
                      "generated_artifacts": len(list(case.iterdir()))}
            results.append(record)
            if process.returncode == 0 or "Error:" not in record["diagnostic"] or record["generated_artifacts"]:
                raise ValueError(f"Invalid input was not rejected cleanly: {record}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = verify_failures(args.exe, args.workspace)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Passed {len(report)} real-executable invalid-input controls")
