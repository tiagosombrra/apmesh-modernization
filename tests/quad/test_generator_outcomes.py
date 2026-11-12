#!/usr/bin/env python3
"""Run a real serial GeneratorAdaptive with research-only global outcome hooks."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory


def run(executable: Path, root: Path, model: str) -> None:
    source = root / "configs" / model / "article.conf"
    config_text = source.read_text(encoding="utf-8")
    input_match = re.search(r"^INPUT_MODEL=(.+)$", config_text, flags=re.MULTILINE)
    if input_match is None:
        raise AssertionError("Pinned input model is missing")
    model_path = (root / input_match.group(1).strip()).resolve()
    if not model_path.is_file():
        raise FileNotFoundError(model_path)

    with TemporaryDirectory(prefix="apmesh-m3-6c-") as temp:
        work = Path(temp)
        config_text = re.sub(
            r"^INPUT_MODEL=.+$",
            lambda _: f"INPUT_MODEL={model_path.as_posix()}",
            config_text,
            flags=re.MULTILINE,
        )
        config_text = re.sub(
            r"^OUTPUT_PREFIX=.+$",
            lambda _: f"OUTPUT_PREFIX={(work / model).as_posix()}",
            config_text,
            flags=re.MULTILINE,
        )
        config = work / "research.conf"
        config.write_text(config_text, encoding="utf-8", newline="\n")
        result = subprocess.run(
            [str(executable.resolve()), str(config)],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        markers = [
            line for line in result.stdout.splitlines()
            if line.startswith("real_generator_outcomes=")
        ]
        shared = [
            line for line in result.stdout.splitlines()
            if line.startswith("R2B2_SHARED_CURVE_MODEL ")
        ]
        if result.returncode != 0 or len(markers) != 1 or len(shared) != 1:
            raise AssertionError(
                f"Generator research probe failed: rc={result.returncode}, "
                f"markers={markers}, shared={shared}, "
                f"stdout_tail={result.stdout[-5000:]!r}, "
                f"stderr_tail={result.stderr[-5000:]!r}"
            )

        # Require source-derived, coherent and nonzero real interface evidence.
        # CTest success does NOT classify rejected interfaces as conforming.
        fields = dict(re.findall(r"([a-z_]+)=([^\s]+)", shared[0]))
        expected_patches = 4 if model == "eistute" else 28
        required = (
            "patches", "shared_curves", "coherent_epoch_patches",
            "shared_compared", "shared_matched", "shared_rejected",
            "shared_unobserved", "shared_geometry_matched",
            "shared_geometry_rejected", "sheet_policy_pending",
            "same_orientation_pairs", "opposite_orientation_pairs",
            "negative_controls", "global_mixed_model_admitted",
        )
        if any(field not in fields for field in required):
            raise AssertionError(f"Missing source interface evidence: {shared[0]!r}")
        compared = int(fields["shared_compared"])
        matched = int(fields["shared_matched"])
        rejected = int(fields["shared_rejected"])
        geometry_matched = int(fields["shared_geometry_matched"])
        geometry_rejected = int(fields["shared_geometry_rejected"])
        if not (
            int(fields["patches"]) == expected_patches
            and int(fields["shared_curves"]) > 0
            and int(fields["coherent_epoch_patches"]) > 1
            and compared > 0
            and matched + rejected == compared
            and geometry_matched + geometry_rejected == compared
            and (int(fields["same_orientation_pairs"])
                 + int(fields["opposite_orientation_pairs"])) > 0
            and int(fields["negative_controls"]) == 1
            and int(fields["global_mixed_model_admitted"]) == 0
        ):
            raise AssertionError(f"Unqualified or empty source audit: {shared[0]!r}")
        print(shared[0])
        print(markers[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--model", default="eistute", choices=["eistute", "book"])
    args = parser.parse_args()
    run(args.exe, args.root.resolve(), args.model)
