#!/usr/bin/env python3
"""Bind original radial science and detached physical seam evidence for review.

This file can prepare reviewer evidence but cannot authorize physical welding,
halfedge twins, global non-manifold connectivity, or accepted QUAD production.
"""

import argparse
import csv
from copy import deepcopy
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path


MODELS = {
    "eistute": {"source_file": "input_models/eistute2.fixed.bp",
                "patches": 4, "curves": 13, "source_sites": 136,
                "source_nodes": 115, "valence": 4,
                "radial_source_intervals": 10, "shared_pairs": 6},
    "book": {"source_file": "input_models/book_v7a.bp",
             "patches": 28, "curves": 85, "source_sites": 936,
             "source_nodes": 747, "valence": 28,
             "radial_source_intervals": 12, "shared_pairs": 378},
}


def check(value, reason):
    if not value:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def strict_pending(packet):
    check(packet["schema"] == "apmesh.quad.r2c1.read_only_sheet_review.v1",
          "Wrong source reviewer packet schema")
    check(packet["review_status"] == "PENDING_ADVISOR_REVIEW"
          and packet["junction_kind"] == "UNDECIDED"
          and packet["reviewer_finding"] is None
          and packet["proposed_continuations"] == []
          and all(value is None for value in packet["questions"].values())
          and packet["scientific_admission"] is False
          and packet["physical_node_welding"] is False
          and packet["manifold_twin_authorized"] is False
          and packet["physical_SubMesh_published"] is False,
          "R2c12 source reviewer packet already claims unverified approval")
    return True


def validate_model(root, radial_dir, review_dir, mesh_dir, name, spec):
    r2c0 = read_json(radial_dir / "r2c0_manifest.json")
    r2c1 = read_json(review_dir / "r2c1_review_manifest.json")
    check(r2c0["status"] ==
          "READ_ONLY_ORIGINAL_SOURCE_RADIAL_RINGS_NO_SHEET_APPROVAL"
          and r2c0["physical_nodes_welded"] is False
          and r2c0["physical_SubMesh_published"] is False
          and r2c1["scientific_admission"] is False
          and r2c1["physical_node_welding"] is False
          and r2c1["original_models"] == 2,
          "Legacy scientific packet no-weld protection failed")
    expected_name = name.capitalize()
    outcome = next(
        (item for item in r2c0["outcomes"] if
         item["model"].lower() == name), None)
    review = next(
        (item for item in r2c1["results"] if
         item["model"].lower() == name), None)
    check(outcome is not None and review is not None,
          "Missing original radial scientific record/reviewer decision packet")
    record_path = radial_dir / outcome["record"]
    packet_path = review_dir / review["review_packet"]
    record_bytes = record_path.read_bytes()
    packet_bytes = packet_path.read_bytes()
    check(sha(record_bytes) == outcome["record_sha256"] and
          sha(packet_bytes) == review["review_packet_sha256"],
          "Original radial record or reviewer packet bytes were altered")
    record, packet = json.loads(record_bytes), json.loads(packet_bytes)
    strict_pending(packet)

    source_bytes = (root / spec["source_file"]).read_bytes()
    source_hash = sha(source_bytes)
    check(packet["model"] == expected_name and
          record["model"] == expected_name and
          packet["model_sha256"] == source_hash ==
          record["model_sha256"] and
          packet["source_curve_index"] == record["source_curve_index"] and
          packet["radial_valence"] == spec["valence"] and
          len(packet["original_source_intervals"]) ==
          spec["radial_source_intervals"] and
          packet["original_radial_cycle"] == record["original_radial_cycle"],
          "R2c12 original source SHA, curve or radial identity differs")
    check(packet["source_log_sha256"] == record["source_log_sha256"] and
          packet["m4_graph_sha256"] == record["m4_graph_sha256"] and
          packet["source_epoch"] == record["source_epoch"] and
          packet["source_retry"] == record["source_retry"],
          "R2c12 original scientific epoch/graph provenance changed")

    atlas_path = mesh_dir / f"{name}_original_source_seam_atlas.csv"
    obj_path = mesh_dir / f"{name}_all_sides_detached_quad_aft.obj"
    manifest_path = mesh_dir / f"{name}_all_sides_detached_quad_aft.json"
    independent_path = mesh_dir / "r2c11_source_seam_atlas_verification.json"
    physical_manifest = read_json(manifest_path)
    physical_audit = read_json(independent_path)[name]
    check(physical_manifest["expected_model_sha256_from_r2c6_evidence_not_recomputed"]
          == source_hash and
          physical_manifest["original_patches"] == spec["patches"] and
          physical_manifest["cross_patch_welding"] is False and
          physical_manifest["global_scientific_mesh_approved"] is False and
          physical_audit["source_curves"] == spec["curves"] and
          physical_audit["unique_source_curve_points"] == spec["source_nodes"] and
          physical_audit["physical_obj_source_witnesses"] ==
          spec["source_sites"] and
          physical_audit["all_original_patch_sides"] ==
          spec["patches"] * 4 and
          physical_audit["shared_nonmanifold_curve_valence"] ==
          spec["valence"] and
          physical_audit["verified_shared_incidence_pairs"] ==
          spec["shared_pairs"] and
          physical_audit["per_patch_physical_ownership_preserved"] is True and
          physical_audit["globally_welded_or_scientifically_approved"] is False,
          "Independent exported native source atlas no-weld evidence differs")

    atlas_rows = list(csv.DictReader(
        atlas_path.open("r", encoding="utf-8", newline="")))
    check(len(atlas_rows) == spec["source_sites"],
          "Source atlas lost original adapted patch-side witnesses")
    source_curve = int(packet["source_curve_index"])
    selected = defaultdict(list)
    for row in atlas_rows:
        if int(row["curve_registry_index"]) == source_curve:
            selected[(int(row["patch_id"]), int(row["side"]))].append(row)
    actual_members = set(selected)
    radial_order = [(int(item["patch_index"]), int(item["side"]))
                    for item in packet["original_radial_cycle"]]
    check(set(radial_order) == actual_members and
          len(radial_order) == spec["valence"],
          "Separate adapted source and generator radial physical incidence disagree")

    sample_ranges = []
    source_node_pairs = []
    all_shared_points = set()
    for member in radial_order:
        rows = selected[member]
        check(len(rows) >= 3 and
              sum(int(r["is_terminal"]) for r in rows) == 1 and
              rows[-1]["is_terminal"] == "1",
              "Missing physical curve terminal/adapter samples")
        samples = sorted((float(r["source_parameter"]),
                          int(r["source_node_id"]),
                          (float(r["source_x"]),
                           float(r["source_y"]),
                           float(r["source_z"])))
                         for r in rows)
        check(samples[0][0] == 0.0 and samples[-1][0] == 1.0 and
              all(a[0] < b[0] for a, b in zip(samples, samples[1:])),
              "Incomplete original sample-parameter coverage")
        sample_ranges.append(len(samples) - 1)
        source_node_pairs.append((member, samples))
        all_shared_points.update((t, node) for t, node, _ in samples)
    check(len(set(sample_ranges)) == 1,
          "One physical source curve has incompatible patchwise subdivisions")
    source_params = sorted(all_shared_points)
    check(len(source_params) == sample_ranges[0] + 1,
          "Shared adapter curve sample node/parameter identities disagree")
    for _, sites in source_node_pairs[1:]:
        check(sites == source_node_pairs[0][1],
              "Physical shared source sites diverge in parameter/node/XYZ")
    pairwise = sum(1 for _ in itertools.combinations(radial_order, 2))
    check(pairwise == spec["shared_pairs"],
          "Original radial pair-comparison scope changed")
    original_radial_intervals = len(packet["original_source_intervals"])
    source_native_intervals = sample_ranges[0]
    # Different original sampling operations may produce different intervals;
    # neither node IDs nor source knots are joined across those epochs.
    check(original_radial_intervals > 0 and source_native_intervals > 0,
          "Missing independently sampled source intervals")

    output = {
        "schema": "apmesh.quad.r2c12.advisor_handoff_unapproved.v1",
        "model": name,
        "source_model_file": spec["source_file"],
        "source_model_sha256_recomputed": source_hash,
        "original_radial_review_packet_sha256": sha(packet_bytes),
        "original_radial_source_record_sha256": sha(record_bytes),
        "original_physical_obj_sha256": sha(obj_path.read_bytes()),
        "original_physical_manifest_sha256": sha(manifest_path.read_bytes()),
        "original_physical_source_atlas_sha256": sha(atlas_path.read_bytes()),
        "original_physical_atlas_audit_sha256": sha(independent_path.read_bytes()),
        "source_curve_registry_index": source_curve,
        "radial_model_source_epoch": packet["source_epoch"],
        "radial_model_source_retry": packet["source_retry"],
        "physical_adapter_sampling_scope":
            "independent two-pass Adapter research factor 1.0",
        "radial_original_generator_source_intervals": original_radial_intervals,
        "physical_research_adapter_source_intervals": source_native_intervals,
        "source_partitions_identical_across_epochs":
            original_radial_intervals == source_native_intervals
            and [interval["original_parameters"] for interval in
                 packet["original_source_intervals"]] ==
                [[source_params[i][0], source_params[i + 1][0]]
                 for i in range(source_native_intervals)],
        "cross_epoch_physical_node_identity_approved": False,
        "original_source_curve_radial_valence": spec["valence"],
        "original_shared_patch_sides": [
            {"patch_index": patch, "side": side}
            for patch, side in radial_order
        ],
        "verified_distinct_physical_adapter_source_sites":
            len(source_node_pairs[0][1]),
        "verified_shared_adapter_incidence_pairs": pairwise,
        "physical_obj_patch_groups": spec["patches"],
        "physical_obj_all_patches_disjoint": True,
        "independent_atlas_verified": True,
        "source_radial_signed_certificate_retained": True,
        "sheet_or_branch_semantics": None,
        "reviewer_identity": None,
        "reviewer_approval_evidence": None,
        "sheet_continuations": None,
        "canonical_node_ownership": None,
        "normal_orientation_compatibility": None,
        "subdivision_transfer_between_source_epochs": None,
        "original_1993_rule_approved": False,
        "scientific_admission": False,
        "physical_node_welding": False,
        "automatic_sheet_pairing_enabled": False,
        "manifold_twin_authorized": False,
        "production_quad_enabled": False,
        "review_status": "PENDING_INDEPENDENT_ADVISOR_REVIEW",
        "review_questions": [
            "Is the high-valence source a branching junction or separate sheets?",
            "Which patch:side incidences may represent continuous physical sheets?",
            "Which orientation and normal relations are scientifically intended?",
            "Which physical nodes may have common lifetime/ownership, if any?",
            "How should different source-curve sampling partitions be transferred?",
            "Who approves the exact source model SHA and accompanying evidence?"
        ],
    }
    return output


def run(args):
    target = args.output_directory
    target.mkdir(parents=True, exist_ok=True)
    manifest = {"schema": "apmesh.quad.r2c12.handoff_manifest.v1",
                "advisor_approval": False,
                "physical_node_welding": False,
                "all_models": []}
    for name, spec in MODELS.items():
        evidence = validate_model(args.root, args.radial_directory,
                                  args.review_directory,
                                  args.mesh_directory, name, spec)
        filename = f"r2c12_{name}_advisor_handoff.json"
        raw = json.dumps(evidence, sort_keys=True, indent=2,
                         allow_nan=False) + "\n"
        (target / filename).write_text(raw, encoding="utf-8")
        manifest["all_models"].append({
            "name": name,
            "source_model_sha256": evidence["source_model_sha256_recomputed"],
            "radial_curve_index": evidence["source_curve_registry_index"],
            "original_generator_intervals":
                evidence["radial_original_generator_source_intervals"],
            "physical_adapter_intervals":
                evidence["physical_research_adapter_source_intervals"],
            "review_status": evidence["review_status"],
            "packet": filename,
            "packet_sha256": sha(raw.encode("utf-8")),
            "physical_node_welding": False,
        })
    (target / "r2c12_handoff_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print("R2C12_MODEL_BOUND_ADVISOR_HANDOFF",
          json.dumps(manifest["all_models"], sort_keys=True),
          "scientific_admission=0 physical_node_welding=0")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    for argument in ("root", "radial_directory", "review_directory",
                     "mesh_directory", "output_directory"):
        parser.add_argument("--" + argument.replace("_", "-"),
                            type=Path, required=True)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
