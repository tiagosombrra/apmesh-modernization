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
        radial = [
            line for line in result.stdout.splitlines()
            if line.startswith("R2B2_SHARED_SHEET_SECTORS ")
        ]
        all_patches = [
            line for line in result.stdout.splitlines()
            if line.startswith("R2B2_ALL_PATCH_RESULT ")
        ]
        all_summary = [
            line for line in result.stdout.splitlines()
            if line.startswith("R2B2_ALL_PATCH_MODEL ")
        ]
        if (result.returncode != 0 or len(markers) != 1
                or len(shared) != 1 or len(radial) != 1
                or len(all_summary) != 1):
            raise AssertionError(
                f"Generator research probe failed: rc={result.returncode}, "
                f"markers={markers}, shared={shared}, radial={radial}, "
                f"all_summary={all_summary}, all_patch_count={len(all_patches)}, "
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
            "shared_geometry_rejected", "shared_source_ids_matched",
            "shared_source_ids_rejected", "shared_node_id_mismatch_pairs",
            "shared_node_id_mismatch_sites",
            "shared_node_id_mismatch_endpoints",
            "shared_node_id_mismatch_interiors",
            "sheet_policy_pending",
            "same_orientation_pairs", "opposite_orientation_pairs",
            "negative_controls", "owner_endpoint_negative_controls",
            "global_mixed_model_admitted",
        )
        if any(field not in fields for field in required):
            raise AssertionError(f"Missing source interface evidence: {shared[0]!r}")
        compared = int(fields["shared_compared"])
        matched = int(fields["shared_matched"])
        rejected = int(fields["shared_rejected"])
        geometry_matched = int(fields["shared_geometry_matched"])
        geometry_rejected = int(fields["shared_geometry_rejected"])
        source_ids_matched = int(fields["shared_source_ids_matched"])
        source_ids_rejected = int(fields["shared_source_ids_rejected"])
        if not (
            int(fields["patches"]) == expected_patches
            and int(fields["shared_curves"]) > 0
            and int(fields["coherent_epoch_patches"]) > 1
            and compared > 0
            and matched + rejected == compared
            and geometry_matched + geometry_rejected == compared
            and source_ids_matched + source_ids_rejected == compared
            and (int(fields["same_orientation_pairs"])
                 + int(fields["opposite_orientation_pairs"])) > 0
            and int(fields["negative_controls"]) == 1
            and int(fields["owner_endpoint_negative_controls"]) == 1
            and int(fields["global_mixed_model_admitted"]) == 0
        ):
            raise AssertionError(f"Unqualified or empty source audit: {shared[0]!r}")
        if (int(fields["shared_node_id_mismatch_endpoints"])
                + int(fields["shared_node_id_mismatch_interiors"])
                != int(fields["shared_node_id_mismatch_sites"])):
            raise AssertionError(f"Source IDs have inconsistent classification: {shared[0]!r}")

        sector_fields = dict(re.findall(r"([a-z_]+)=([^\s]+)", radial[0]))
        sector_required = (
            "patches", "high_valence_curves", "curve_incidences",
            "angular_adjacent_pairs", "radial_coincident_pairs",
            "minimum_cyclic_angle", "max_patch_curve_xyz_error",
            "source_geometry_admitted", "automatic_sheet_pairing_enabled",
            "negative_controls", "reason", "radial_order",
        )
        if any(field not in sector_fields for field in sector_required):
            raise AssertionError(f"Missing real source radial sector evidence: {radial[0]!r}")
        if not (
            int(sector_fields["patches"]) == expected_patches
            and int(sector_fields["high_valence_curves"]) > 0
            and int(sector_fields["curve_incidences"]) == expected_patches
            and int(sector_fields["angular_adjacent_pairs"]) == expected_patches
            and int(sector_fields["negative_controls"]) == 1
            and int(sector_fields["automatic_sheet_pairing_enabled"]) == 0
            and len(sector_fields["radial_order"].split(",")) == expected_patches
        ):
            raise AssertionError(f"Invalid real source sector observation: {radial[0]!r}")

        # Every original model patch must be observed in a SINGLE source
        # epoch. A rejected UV/AFT/XYZ candidate remains a rejected scientific
        # result even when CTest passes: never turn coverage into admission.
        summary = dict(re.findall(r"([A-Za-z_]+)=([^\s]+)", all_summary[0]))
        all_fields = (
            "expected", "observed", "coherent_epoch", "coherent_retry",
            "uv_accepted", "uv_rejected", "physical_accepted",
            "physical_rejected", "full_patch_coverage",
            "global_mixed_model_admitted", "physical_SubMesh_published",
        )
        if any(key not in summary for key in all_fields):
            raise AssertionError(f"Missing full-model source evidence: {all_summary[0]!r}")
        physical_positive = 0
        uv_positive = 0
        unique_patches: set[int] = set()
        if len(all_patches) != expected_patches:
            raise AssertionError(
                f"Every source patch must have a measured outcome: "
                f"{len(all_patches)} vs {expected_patches}"
            )
        for line in all_patches:
            values = dict(re.findall(r"([a-z_]+)=([^\s]+)", line))
            required_patch = (
                "patch", "source_sites", "source_leaves", "quad_faces",
                "exterior_triangles", "uv_admitted", "physical_admitted",
                "physical_facets", "rejection",
            )
            if any(key not in values for key in required_patch):
                raise AssertionError(f"Missing native patch evidence: {line!r}")
            patch = int(values["patch"])
            uv_ok = int(values["uv_admitted"])
            physical_ok = int(values["physical_admitted"])
            if not (
                0 <= patch < expected_patches
                and patch not in unique_patches
                and int(values["source_sites"]) > 4
                and int(values["source_leaves"]) > 0
                and uv_ok in (0, 1) and physical_ok in (0, 1)
                and physical_ok <= uv_ok
                and (values["rejection"] == "none") == (physical_ok == 1)
                and (
                    physical_ok == 0
                    or int(values["physical_facets"]) ==
                        2 * int(values["quad_faces"]) +
                        int(values["exterior_triangles"])
                )
            ):
                raise AssertionError(f"Invalid individual source patch admission: {line!r}")
            unique_patches.add(patch)
            uv_positive += uv_ok
            physical_positive += physical_ok
        if not (
            len(unique_patches) == expected_patches
            and int(summary["expected"]) == expected_patches
            and int(summary["observed"]) == expected_patches
            and int(summary["coherent_epoch"]) == int(fields["coherent_epoch"])
            and int(summary["coherent_retry"]) == int(fields["coherent_retry"])
            and int(summary["uv_accepted"]) == uv_positive
            and int(summary["uv_rejected"]) == expected_patches - uv_positive
            and int(summary["physical_accepted"]) == physical_positive
            and int(summary["physical_rejected"]) ==
                expected_patches - physical_positive
            and int(summary["full_patch_coverage"]) == 1
            and int(summary["global_mixed_model_admitted"]) == 0
            and int(summary["physical_SubMesh_published"]) == 0
        ):
            raise AssertionError(f"Inconsistent full-model source counts: {all_summary[0]!r}")

        # Geometric sector admission is a separate scientific marker. Do not
        # convert an ambiguous real radial configuration into a CTest pass.
        for measured_patch in all_patches:
            print(measured_patch)
        print(all_summary[0])
        print(shared[0])
        print(radial[0])
        print(markers[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--model", default="eistute", choices=["eistute", "book"])
    args = parser.parse_args()
    run(args.exe, args.root.resolve(), args.model)
