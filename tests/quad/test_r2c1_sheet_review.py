#!/usr/bin/env python3
"""R2c-1 review packets and fail-closed structural proposal checks.

Actual source-connected evidence is read from the R2c-0 CI artifacts.
This does NOT grant scientific approval, manifold twins, node sharing,
physical SubMesh publication, or an application QUAD mode.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

from audit_model_catalog import INPUT_MODELS
from test_r2c0_source_radial_incidence import (
    MODELS, MODEL_FILES, digest, pending_policy, require, sha,
    validate_pending_policy,
)

SCHEMA = "apmesh.quad.r2c1.read_only_sheet_review.v1"
HEX = re.compile(r"[0-9a-f]{64}\Z")
GROUP = re.compile(r"[a-z][a-z0-9_-]{1,47}\Z")
DRAFT_KINDS = ("UNDECIDED", "INDEPENDENT_CHARTS",
               "PAIR_CONTINUATION_PROPOSAL", "BRANCH_JUNCTION_PROPOSAL")


def canonical(obj: object) -> str:
    """Give identical typed JSON values an unambiguous comparison encoding."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def require_exact(value: object, expected: object, message: str) -> None:
    require(canonical(value) == canonical(expected), message)


def verify_source_record(record: dict) -> None:
    """Recheck mandatory R2c-0 invariants without trusting a policy string."""
    require(type(record) is dict and record["model"] in MODELS,
            "Unknown original model")
    valence, count = MODELS[record["model"]]
    require(type(record["radial_valence"]) is int and
            record["radial_valence"] == valence and
            len(record["original_radial_cycle"]) == valence and
            len(record["original_source_intervals"]) == count and
            record["interval_certificate"]["certified"] == valence * count and
            record["interval_certificate"]["count"] == valence * count and
            record["interval_certificate"]["inverted"] == 0 and
            record["interval_certificate"]["unresolved"] == 0 and
            record["automatic_sheet_pairing_enabled"] is False and
            record["physical_SubMesh_published"] is False and
            HEX.fullmatch(record["model_sha256"]) and
            HEX.fullmatch(record["source_log_sha256"]) and
            HEX.fullmatch(record["m4_graph_sha256"]),
            "Original source certificate or identity not qualified")
    cycle = record["original_radial_cycle"]
    identifiers = [(x["patch_index"], x["side"]) for x in cycle]
    require(len(set(identifiers)) == valence and
            len({x[0] for x in identifiers}) == valence and
            all(type(x["patch_index"]) is int and
                type(x["side"]) is int and
                0 <= x["patch_index"] < valence and
                0 <= x["side"] < 4 and
                type(x["curve_reversed"]) is bool and
                type(x["winding_sign"]) is int and
                x["winding_sign"] in (-1, 1) for x in cycle),
            "Radial cycle is incomplete, duplicated or incorrectly directed")
    previous = None
    for index, interval in enumerate(record["original_source_intervals"]):
        a, b = interval["original_parameters"]
        start, end = interval["original_source_node_ids"]
        require(interval["curve_index"] == record["source_curve_index"] and
                interval["interval_ordinal"] == index and
                0.0 <= a < b <= 1.0 and
                type(start) is int and type(end) is int and
                start > 0 and end > 0 and start != end and
                interval["interval_orientation"] ==
                "CERTIFIED_SIGNED_BERNSTEIN" and
                interval["physical_sheet_continuation"] == "UNDECIDED",
                "Source interval or provenance is unqualified")
        if previous is not None:
            require(previous[0] == a and previous[1] == start,
                    "Source intervals have a gap or discontinuous node identity")
        links = interval["radial_cycle"]
        require(len(links) == valence, "Incomplete interval radial cycle")
        for j, item in enumerate(cycle):
            expected = {
                **item,
                "radial_next": list(identifiers[(j + 1) % valence]),
                "manifold_twin": None,
                "node_sharing": "NOT_AUTHORIZED",
            }
            require_exact(links[j], expected,
                          "Invalid interval radial successor or unauthorized twin")
        previous = (b, end)
    require(record["original_source_intervals"][0]["original_parameters"][0] == 0 and
            previous[0] == 1,
            "Source interval endpoints do not cover the full original curve")


def review_packet(record: dict) -> dict:
    verify_source_record(record)
    return {
        "schema": SCHEMA,
        "record_sha256": digest(record),
        "model": record["model"],
        "model_sha256": record["model_sha256"],
        "source_log_sha256": record["source_log_sha256"],
        "m4_graph_sha256": record["m4_graph_sha256"],
        "source_curve_index": record["source_curve_index"],
        "source_epoch": record["source_epoch"],
        "source_retry": record["source_retry"],
        "radial_valence": record["radial_valence"],
        "original_radial_cycle": deepcopy(record["original_radial_cycle"]),
        "original_source_intervals": deepcopy(record["original_source_intervals"]),
        "source_certificate": deepcopy(record["interval_certificate"]),
        "source_radial_sha256": digest({
            "cycle": record["original_radial_cycle"],
            "intervals": record["original_source_intervals"],
        }),
        "junction_kind": "UNDECIDED",
        "review_status": "PENDING_ADVISOR_REVIEW",
        "reviewer_finding": None,
        "proposed_continuations": [],
        "questions": {
            "sheet_or_branch_semantics": None,
            "per_incidence_sheet_identity": None,
            "orientation_and_normal_compatibility": None,
            "canonical_boundary_node_ownership": None,
            "source_interval_subdivision_policy": None,
        },
        "scientific_admission": False,
        "physical_node_welding": False,
        "manifold_twin_authorized": False,
        "physical_SubMesh_published": False,
    }


def validate_packet(record: dict, packet: object) -> dict:
    require(type(packet) is dict, "Review packet must be a JSON object")
    require_exact(packet, review_packet(record),
                  "Review packet differs from complete source-bound pending record")
    return {
        "source_integrity": True,
        "review_status": "PENDING_ADVISOR_REVIEW",
        "scientific_admission": False,
        "physical_node_welding": False,
        "physical_SubMesh_published": False,
    }


def proposal_template(packet: dict) -> dict:
    """A model-locked draft form, not a proposed factual sheet mapping."""
    return {
        "schema": "apmesh.quad.r2c1.unapproved_draft.v1",
        "review_packet_sha256": digest(packet),
        "model_sha256": packet["model_sha256"],
        "source_curve_index": packet["source_curve_index"],
        "source_epoch": packet["source_epoch"],
        "source_retry": packet["source_retry"],
        "proposal_status": "DRAFT_NOT_APPROVED",
        "junction_kind": "UNDECIDED",
        "groups": [],
        "reviewer_finding": None,
        "scientific_admission": False,
        "physical_node_welding": False,
        "manifold_twin_authorized": False,
        "physical_SubMesh_published": False,
    }


def validate_draft(packet: dict, proposal: object) -> dict:
    """Validate review syntax only. No API in R2c-1 grants approval."""
    require(type(proposal) is dict, "Review draft must be an object")
    required = proposal_template(packet)
    require(set(proposal) == set(required),
            "Missing/extra fields in scientific review draft")
    for key in required:
        if key in ("groups", "junction_kind"):
            continue
        require_exact(proposal[key], required[key],
                      "Review draft has stale source or forged approval field")
    require(type(proposal["groups"]) is list and
            proposal["junction_kind"] in DRAFT_KINDS,
            "Unknown proposed junction type")
    if proposal["junction_kind"] in ("UNDECIDED", "INDEPENDENT_CHARTS"):
        require(not proposal["groups"],
                "An undecided/disconnected junction cannot also have continuation groups")
    else:
        require(bool(proposal["groups"]),
                "Continuation proposal must state every affected incidence explicitly")
    cycle = packet["original_radial_cycle"]
    source_keys = [(x["patch_index"], x["side"]) for x in cycle]
    seen_members: set[tuple[int, int]] = set()
    seen_groups: set[str] = set()
    interval_ordinals = list(range(len(packet["original_source_intervals"])))
    for group in proposal["groups"]:
        require(type(group) is dict and set(group) ==
                {"group_id", "kind", "members", "interval_ordinals",
                 "orientation_relation", "node_owner_policy", "rationale"},
                "Incomplete or surprising sheet group fields")
        group_id = group["group_id"]
        require(type(group_id) is str and GROUP.fullmatch(group_id) and
                group_id not in seen_groups,
                "Duplicate or invalid proposed group identity")
        seen_groups.add(group_id)
        kind = group["kind"]
        require(kind in ("MANIFOLD_PAIR", "BRANCH_MULTI_SHEET"),
                "Unknown high-valence sheet group kind")
        require((kind == "MANIFOLD_PAIR") ==
                (proposal["junction_kind"] == "PAIR_CONTINUATION_PROPOSAL"),
                "Proposed group kind contradicts top-level junction kind")
        members = group["members"]
        require(type(members) is list and
                len(members) >= (2 if kind == "MANIFOLD_PAIR" else 3) and
                (kind != "MANIFOLD_PAIR" or len(members) == 2),
                "Invalid number of proposed incident sheets")
        keys = []
        for item in members:
            require(type(item) is dict and set(item) == {"patch_index", "side"} and
                    type(item["patch_index"]) is int and type(item["side"]) is int,
                    "Malformed proposed source patch/side")
            key = (item["patch_index"], item["side"])
            require(key in source_keys and key not in seen_members and
                    key not in keys,
                    "Missing, repeated, or fabricated source incidence")
            keys.append(key)
        require(keys == [key for key in source_keys if key in keys],
                "Proposed group must follow canonical original radial order")
        seen_members.update(keys)
        require_exact(group["interval_ordinals"], interval_ordinals,
                      "Any partial/overlapping source interval proposal is blocked")
        require(group["orientation_relation"] == "REQUIRES_SCIENTIFIC_REVIEW" and
                group["node_owner_policy"] == "UNASSIGNED" and
                type(group["rationale"]) is str and
                10 <= len(group["rationale"].strip()) <= 2048,
                "Draft cannot resolve normals, nodes, or invent a scientific rationale")
    return {
        "structural_review_candidate": True,
        "candidate_groups": len(proposal["groups"]),
        "scientific_admission": False,
        "physical_node_welding": False,
        "manifold_twin_authorized": False,
        "physical_SubMesh_published": False,
        "reason": "DRAFT_REQUIRES_INDEPENDENT_SCIENTIFIC_APPROVAL",
    }


def synthetic_draft(packet: dict) -> dict:
    """A deliberate TEST ONLY, never emitted as a real source sheet decision."""
    base = proposal_template(packet)
    base["junction_kind"] = "PAIR_CONTINUATION_PROPOSAL"
    first, second = packet["original_radial_cycle"][:2]
    base["groups"] = [{
        "group_id": "test-only-possible-pair",
        "kind": "MANIFOLD_PAIR",
        "members": [{"patch_index": x["patch_index"], "side": x["side"]}
                    for x in (first, second)],
        "interval_ordinals": list(range(len(packet["original_source_intervals"]))),
        "orientation_relation": "REQUIRES_SCIENTIFIC_REVIEW",
        "node_owner_policy": "UNASSIGNED",
        "rationale": "TEST ONLY: synthetic topology candidate, not a source model decision",
    }]
    return base


def expect_rejection(function, value: object, case: str) -> None:
    try:
        function(value)
    except (TypeError, ValueError, KeyError):
        return
    raise AssertionError(f"R2c1 source/policy mutation admitted: {case}")


def check_negative_controls(record: dict, packet: dict) -> dict:
    negatives = 0
    pack_changes = [
        ("model_sha256", "0"*64),
        ("source_log_sha256", "0"*64),
        ("m4_graph_sha256", "0"*64),
        ("record_sha256", "0"*64),
        ("source_radial_sha256", "0"*64),
        ("source_curve_index", packet["source_curve_index"] + 1),
        ("source_epoch", packet["source_epoch"] + 1),
        ("source_retry", packet["source_retry"] + 1),
        ("radial_valence", packet["radial_valence"] + 1),
        ("review_status", "SCIENTIFICALLY_APPROVED"),
        ("reviewer_finding", {"reviewer": "fabricated"}),
        ("junction_kind", "BRANCH"),
        ("proposed_continuations", [{"fabricated": True}]),
        ("physical_node_welding", True),
        ("manifold_twin_authorized", True),
        ("physical_SubMesh_published", True),
    ]
    for key, changed in pack_changes:
        bad = deepcopy(packet)
        bad[key] = changed
        expect_rejection(lambda x: validate_packet(record, x), bad,
                         "packet." + key)
        negatives += 1
    for label, mutate in [
        ("missing_incidence", lambda p: p["original_radial_cycle"].pop()),
        ("reversed_flag", lambda p: p["original_radial_cycle"][0].update(
            curve_reversed=not p["original_radial_cycle"][0]["curve_reversed"])),
        ("duplicate_side", lambda p: p["original_radial_cycle"].append(
            deepcopy(p["original_radial_cycle"][0]))),
        ("forged_radial_next", lambda p: p["original_source_intervals"][0][
            "radial_cycle"][0].update(radial_next=[9999, 0])),
        ("forged_source_node", lambda p: p["original_source_intervals"][0][
            "original_source_node_ids"].__setitem__(0, 0)),
        ("ambiguous_review_questions", lambda p: p["questions"].update(
            canonical_boundary_node_ownership="SHARED")),
    ]:
        bad = deepcopy(packet)
        mutate(bad)
        expect_rejection(lambda x: validate_packet(record, x), bad,
                         "packet." + label)
        negatives += 1
    draft = synthetic_draft(packet)
    positive = validate_draft(packet, draft)
    require(positive["structural_review_candidate"] and
            not positive["scientific_admission"] and
            not positive["physical_node_welding"] and
            not positive["manifold_twin_authorized"],
            "Synthetic topological candidate must never grant physical rights")
    changes = [
        ("review_packet_sha256", "0"*64),
        ("model_sha256", "0"*64),
        ("source_curve_index", packet["source_curve_index"] + 1),
        ("source_epoch", packet["source_epoch"] + 1),
        ("source_retry", packet["source_retry"] + 1),
        ("proposal_status", "SCIENTIFICALLY_APPROVED"),
        ("reviewer_finding", "pretend-reviewed"),
        ("scientific_admission", True),
        ("physical_node_welding", True),
        ("manifold_twin_authorized", True),
        ("physical_SubMesh_published", True),
        ("junction_kind", "INDEPENDENT_CHARTS"),
    ]
    for key, changed in changes:
        bad = deepcopy(draft)
        bad[key] = changed
        expect_rejection(lambda x: validate_draft(packet, x), bad,
                         "draft." + key)
        negatives += 1
    group_cases = [
        ("no_group", lambda g: g.pop()),
        ("duplicate_group", lambda g: g.append(deepcopy(g[0]))),
        ("missing_member", lambda g: g[0]["members"].pop()),
        ("repeated_member", lambda g: g[0]["members"].append(
            deepcopy(g[0]["members"][0]))),
        ("wrong_patch", lambda g: g[0]["members"][0].update(patch_index=999)),
        ("wrong_side", lambda g: g[0]["members"][0].update(side=7)),
        ("swapped_members", lambda g: g[0]["members"].reverse()),
        ("wrong_interval", lambda g: g[0]["interval_ordinals"].pop()),
        ("repeated_interval", lambda g: g[0]["interval_ordinals"].append(0)),
        ("fabricated_interval", lambda g: g[0]["interval_ordinals"].append(999)),
        ("node_owner_bypass", lambda g: g[0].update(node_owner_policy="SHARED")),
        ("normal_bypass", lambda g: g[0].update(orientation_relation="APPROVED")),
        ("empty_rationale", lambda g: g[0].update(rationale="")),
        ("wrong_kind", lambda g: g[0].update(kind="BRANCH_MULTI_SHEET")),
    ]
    for case, mutation in group_cases:
        bad = deepcopy(draft)
        mutation(bad["groups"])
        expect_rejection(lambda x: validate_draft(packet, x), bad,
                         "draft." + case)
        negatives += 1
    # Source record mutation cannot be promoted via an otherwise valid packet.
    bad_record = deepcopy(record)
    bad_record["original_source_intervals"][0]["radial_cycle"][0][
        "manifold_twin"] = [0, 1]
    expect_rejection(lambda x: validate_packet(x, packet), bad_record,
                     "source.forced_manifold_twin")
    negatives += 1
    return {"negative_controls_rejected": negatives,
            "synthetic_draft_structurally_checked": True,
            "synthetic_draft_scientifically_admitted": False}


def run(root: Path, directory: Path, output: Path) -> dict:
    manifest_path = directory / "r2c0_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest["status"] ==
            "READ_ONLY_ORIGINAL_SOURCE_RADIAL_RINGS_NO_SHEET_APPROVAL" and
            manifest["negative_controls_rejected"] == 38 and
            manifest["physical_nodes_welded"] is False and
            manifest["physical_SubMesh_published"] is False and
            manifest["automatic_sheet_pairing_enabled"] is False and
            len(manifest["outcomes"]) == len(MODELS),
            "R2c0 source manifest or no-weld gate changed")
    output.mkdir(parents=True, exist_ok=True)
    results = []
    total_controls = 0
    total_intervals = 0
    total_radials = 0
    for name, (valence, intervals) in MODELS.items():
        outcome = next((x for x in manifest["outcomes"]
                        if x["model"] == name), None)
        require(outcome is not None and outcome["radial_valence"] == valence
                and outcome["source_intervals"] == intervals,
                "Missing original source curve record from R2c0")
        raw_record = (directory / outcome["record"]).read_bytes()
        raw_policy = (directory / outcome["policy_template"]).read_bytes()
        require(outcome["record_sha256"] == sha(raw_record) and
                outcome["policy_sha256"] == sha(raw_policy),
                "Edited original source record or pending policy bytes")
        record = json.loads(raw_record)
        pending = json.loads(raw_policy)
        model_path = root / INPUT_MODELS[name][0]
        require(sha(model_path.read_bytes()) == record["model_sha256"] and
                record["source_log_sha256"] == manifest["source_log_sha256"],
                "Original scientific model or native log identity changed")
        status = validate_pending_policy(record, pending)
        require(status["scientific_admission"] is False,
                "Unapproved R2c0 policy was promoted")
        packet = review_packet(record)
        checked = validate_packet(record, packet)
        require(checked["source_integrity"] and
                not checked["scientific_admission"],
                "R2c1 packet status was promoted")
        negatives = check_negative_controls(record, packet)
        total_controls += negatives["negative_controls_rejected"]
        total_intervals += len(packet["original_source_intervals"])
        total_radials += packet["radial_valence"] * len(
            packet["original_source_intervals"])
        filename = f"r2c1_{MODEL_FILES[name]}_review_packet.json"
        destination = output / filename
        destination.write_text(json.dumps(packet, indent=2, allow_nan=False) +
                               "\n", encoding="utf-8")
        results.append({
            "model": name,
            "curve_index": record["source_curve_index"],
            "radial_valence": valence,
            "original_intervals": intervals,
            "source_radial_edges": intervals * valence,
            "negative_controls_rejected": negatives["negative_controls_rejected"],
            "review_status": "PENDING_ADVISOR_REVIEW",
            "review_packet": filename,
            "review_packet_sha256": sha(destination.read_bytes()),
            "scientific_admission": False,
            "physical_node_welding": False,
        })
    # Every retained control must remain observable: 49 per original model.
    require(total_intervals == 22 and total_radials == 376 and
            total_controls == 98 and
            all(x["negative_controls_rejected"] == 49 for x in results),
            "R2c1 source or adversarial policy coverage incomplete")
    receipt = {
        "schema": SCHEMA,
        "status": "SOURCE_BOUND_REVIEW_PACKET_AND_DRAFT_STRUCTURE_ONLY",
        "r2c0_manifest_sha256": sha(manifest_path.read_bytes()),
        "original_models": 2,
        "original_curve_intervals": total_intervals,
        "radial_source_adjacencies": total_radials,
        "negative_controls_rejected": total_controls,
        "synthetic_proposals_are_tests_not_model_decisions": True,
        "results": results,
        "all_reviewer_findings": None,
        "scientific_admission": False,
        "automatic_sheet_pairing_enabled": False,
        "physical_node_welding": False,
        "physical_SubMesh_published": False,
        "production_quad_enabled": False,
    }
    (output / "r2c1_review_manifest.json").write_text(
        json.dumps(receipt, indent=2, allow_nan=False)+"\n",
        encoding="utf-8")
    print(f"R2C1_SHEET_REVIEW source_models=2 original_intervals={total_intervals} "
          f"radial_adjacencies={total_radials} "
          f"negative_controls={total_controls} "
          "draft_structure_only=1 advisor_approved=0 "
          "node_welding=0 physical_SubMesh_published=0")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--r2c0-directory", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    run(args.root.resolve(), args.r2c0_directory.resolve(),
        args.directory.resolve())
