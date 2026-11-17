"""R2.7.14 read-only original shared-source-curve incidence audit.

This is a graph of source curve ownership from real accepted native TRI
snapshots, not a proof of physical node welding or LOD ancestry.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

from .audit_retained_native_lineage import audit_retained_directory
from .verify_native_lineage import (
    SOURCE_MODELS, decode_ndjson, require, sha256_file, validate_lineage_records,
)

SCHEMA = "apmesh.meshstudio.r2714.accepted_native_source_curve_adjacency.v1"


def analyze_source_incidences(records: list[dict]) -> dict:
    """Classify exact source-curve incidence without guessing geometric seams."""
    first = records[0]
    source_curve_count = first["source_curve_count"]
    patches = [record for record in records if record.get("type") == "patch"]
    by_curve: dict[int, list[dict]] = defaultdict(list)
    for patch in patches:
        for edge in patch["source_curves"]:
            by_curve[edge["source_curve_slot"]].append({
                "patch_slot": patch["patch_slot"],
                "edge_slot": edge["edge_slot"],
                "reversed": edge["reversed"],
                "native_curve_id": edge["native_curve_id"],
                "reported_curve_patch_observers": edge["reported_curve_patch_observers"],
            })

    require(set(by_curve) == set(range(source_curve_count)),
            "incomplete_original_source_curve_incidence")
    rows = []
    shared_patch_pairs: dict[tuple[int, int], list[int]] = defaultdict(list)
    class_counts = {"single_patch": 0, "two_patch": 0, "three_or_more_patches": 0}
    repeated_patch_incidence = []
    reported_observer_disagreements = []

    for slot in sorted(by_curve):
        incidences = sorted(
            by_curve[slot], key=lambda edge: (edge["patch_slot"], edge["edge_slot"]))
        owners = sorted({edge["patch_slot"] for edge in incidences})
        ids = {edge["native_curve_id"] for edge in incidences}
        require(len(ids) == 1, "original_source_curve_id_disagreement")
        if len(owners) == 1:
            class_counts["single_patch"] += 1
        elif len(owners) == 2:
            class_counts["two_patch"] += 1
        else:
            class_counts["three_or_more_patches"] += 1
        if len(owners) != len(incidences):
            repeated_patch_incidence.append(slot)
        observers = sorted({edge["reported_curve_patch_observers"]
                            for edge in incidences})
        if len(observers) != 1 or observers[0] != len(owners):
            reported_observer_disagreements.append({
                "source_curve_slot": slot,
                "reported_observers": observers,
                "unique_source_patches": len(owners),
            })
        if len(owners) >= 2:
            for i, left in enumerate(owners):
                for right in owners[i + 1:]:
                    shared_patch_pairs[(left, right)].append(slot)
        rows.append({
            "source_curve_slot": slot,
            "native_curve_id": next(iter(ids)),
            "unique_owner_patch_slots": owners,
            "incidences": incidences,
            "incidence_count": len(incidences),
        })

    return {
        "source_patch_count": len(patches),
        "source_curve_count": source_curve_count,
        "total_source_curve_incidences": sum(len(r["incidences"]) for r in rows),
        "source_curve_ownership_classes": class_counts,
        "source_curve_slots_with_repeated_same_patch_incidence": repeated_patch_incidence,
        "source_curve_observer_count_disagreements": reported_observer_disagreements,
        "source_patch_pair_adjacencies": [
            {"patch_slots": [left, right], "shared_source_curve_slots": sorted(slots)}
            for (left, right), slots in sorted(shared_patch_pairs.items())
        ],
        "source_curve_incidences": rows,
        "shared_curve_geometry_or_welded_node_continuity_verified": False,
        "cross_epoch_face_curve_descendants_verified": False,
    }


def audit_source_adjacency(directory: Path) -> dict:
    """Revalidate original raw data and its independent source-bound summary."""
    retained = audit_retained_directory(directory)
    models = {}
    for model in SOURCE_MODELS:
        report = json.loads(
            (directory / ("r2712-" + model + "-native-lineage-audit.json"))
            .read_text(encoding="utf-8"))
        accepted = []
        for snapshot in report["accepted_snapshots"]:
            original = directory / snapshot["raw_native_ndjson_artifact_name"]
            records = decode_ndjson(original.read_bytes())
            validated = validate_lineage_records(records, model)
            require(validated["accepted_step"] == snapshot["accepted_step"] and
                    sha256_file(original) == snapshot["source_file_sha256"],
                    "original_native_source_snapshot_changed")
            graph = analyze_source_incidences(records)
            require(graph["source_patch_count"] == SOURCE_MODELS[model][0],
                    "source_patch_ownership_graph_incomplete")
            accepted.append({
                "accepted_step": validated["accepted_step"],
                "original_native_ndjson_sha256": snapshot["source_file_sha256"],
                "source_adjacency": graph,
            })
        require([row["accepted_step"] for row in accepted] ==
                retained["original_native_models"][model]["accepted_native_steps"],
                "original_accepted_epoch_scope_changed")
        models[model] = {
            "original_native_accepted_snapshots": accepted,
            "source_curve_adjacency_audited": True,
            "physical_node_welding_certified": False,
            "cross_epoch_lineage_certified": False,
        }
    return {
        "schema": SCHEMA,
        "evidence_class": "REAL_NATIVE_SOURCE_INCIDENCE_NOT_PHYSICAL_WELDING",
        "original_models": models,
        "source_retained_evidence_revalidated": True,
        "scientific_lod_qualified": False,
        "physical_gpu_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = audit_source_adjacency(args.directory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    compact = {
        model: [{
            "step": item["accepted_step"],
            "source_curves": item["source_adjacency"]["source_curve_count"],
            "source_pair_count": len(item["source_adjacency"]["source_patch_pair_adjacencies"]),
            "shared_two_patch_curves": item["source_adjacency"][
                "source_curve_ownership_classes"]["two_patch"],
            "three_or_more_patch_curves": item["source_adjacency"][
                "source_curve_ownership_classes"]["three_or_more_patches"],
        } for item in details["original_native_accepted_snapshots"]]
        for model, details in result["original_models"].items()
    }
    print("R2714_ORIGINAL_SOURCE_ADJACENCY=" + json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
