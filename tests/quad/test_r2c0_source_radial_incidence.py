#!/usr/bin/env python3
"""R2c-0: source-linked interval radial incidence, never physical seam welding.

Consume the native original GeneratorAdaptive source report and independently
validated M4 PatchReader hypergraphs. The same verified Bézier interval result
is linked by original source curve and patch/side identity. Radial neighbors
are read-only; they are never manifold twins or accepted node co-owners.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import re

from audit_model_catalog import INPUT_MODELS

MODELS = {"Eistute": (4, 10), "Book": (28, 12)}
MODEL_FILES = {"Eistute": "eistute", "Book": "book"}
CENTER_RULES = ("vertex_mean", "area_centroid")
HEX_SHA = re.compile(r"[0-9a-f]{64}\Z")


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(obj: object) -> str:
    return sha(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                          allow_nan=False).encode("utf-8"))


def fields(line: str) -> dict[str, str]:
    match = re.match(r"^(?:\\d+: )?([A-Z0-9_]+) (.+)$", line.strip())
    require(match is not None, "Missing actual native source marker")
    parts = {}
    for item in match.group(2).split():
        key, sep, value = item.partition("=")
        require(bool(sep) and key not in parts, "Duplicate/malformed native field")
        parts[key] = value
    return parts


def parse_log(source_log: Path) -> dict[int, dict[str, dict[str, str]]]:
    reports: dict[int, dict[str, dict[str, str]]] = {}
    prefixes = {
        "R2C0_ORIGINAL_SOURCE_RING": "ring",
        "R2B2_SHARED_SHEET_BERNSTEIN": "proof",
        "R2B2_SHARED_SHEET_SECTORS": "sector",
        "R2B2_SHARED_CURVE_MODEL": "source",
    }
    for line in source_log.read_text(encoding="utf-8").splitlines():
        text = re.sub(r"^\\d+: ", "", line.strip())
        kind = next((key for key in prefixes if text.startswith(key + " ")), None)
        if kind is None:
            continue
        data = fields(text)
        require("patches" in data, "Native marker lacks patch count")
        count = int(data["patches"])
        require(count in (4, 28), "Unknown native model size")
        by_model = reports.setdefault(count, {})
        name = prefixes[kind]
        require(name not in by_model, "Duplicate real native source marker")
        by_model[name] = data
    require(set(reports) == {4, 28}, "Both original generator models required")
    require(all(set(r) == set(prefixes.values()) for r in reports.values()),
            "Incomplete actual native source/proof/radial evidence")
    return reports


def source_record(graph: dict, reports: dict[int, dict],
                  model: str, root: Path, graph_sha: str,
                  log_sha: str) -> dict:
    valence, interval_count = MODELS[model]
    native = reports[valence]
    source, proof, sectors = (native[k] for k in ("ring", "proof", "sector"))
    expected_model_path = root / INPUT_MODELS[model][0]
    model_sha = sha(expected_model_path.read_bytes())
    require(graph["source_sha256"] == model_sha and
            graph["model"] == model and graph["patch_count"] == valence and
            graph["no_node_adoption_or_weld"] is True and
            graph["high_valence_sheet_policy_approved"] is False,
            "M4 original model identity or no-weld provenance changed")
    high = [c for c in graph["curves"] if c["degree"] > 2]
    require(len(high) == 1 and high[0]["degree"] == valence,
            "Unexpected original nonmanifold curve census")
    curve = high[0]
    require(int(source["curve_index"]) == curve["curve_id"] and
            int(source["patches"]) == valence and
            int(source["original_intervals"]) == interval_count and
            int(proof["original_intervals"]) == interval_count and
            int(proof["adjacent_pairs"]) == valence and
            int(proof["pair_intervals_checked"]) == valence * interval_count and
            int(proof["certified_pair_intervals"]) == valence * interval_count and
            int(proof["inverted_pair_intervals"]) == 0 and
            int(proof["inconclusive_pair_intervals"]) == 0 and
            int(proof["interval_order_certified"]) == 1 and
            int(proof["negative_controls"]) == 1 and
            proof["reason"] == "strict_positive_bernstein_bounds" and
            float(proof["smallest_positive_lower"]) > 0 and
            int(proof["automatic_sheet_pairing_enabled"]) == 0 and
            int(source["interval_order_certified"]) == 1 and
            int(source["no_welding"]) == 1 and
            int(source["epoch"]) == int(native["source"]["coherent_epoch"]) and
            int(source["retry"]) == int(native["source"]["coherent_retry"]) and
            int(sectors["source_geometry_admitted"]) == 1 and
            int(sectors["radial_coincident_pairs"]) == 0 and
            int(sectors["automatic_sheet_pairing_enabled"]) == 0 and
            int(proof["patches"]) == valence,
            "Original source interval proof or coherent epoch not qualified")
    parameters = [float(x) for x in source["parameters"].split(",")]
    node_ids = [int(x) for x in source["node_ids"].split(",")]
    require(len(parameters) == len(node_ids) == interval_count + 1 and
            parameters[0] == 0.0 and parameters[-1] == 1.0 and
            all(math.isfinite(x) for x in parameters) and
            all(0 <= a < b <= 1 for a, b in zip(parameters, parameters[1:])) and
            all(n > 0 for n in node_ids) and len(set(node_ids)) == len(node_ids),
            "Original curve subdivisions or provenance nodes malformed")
    order_text = source["radial_order"].split(",")
    require(source["radial_order"] == sectors["radial_order"],
            "Interval order differs from real source sector witness")
    incidence = {(i["patch"], i["side"]): i for i in curve["incidences"]}
    require(len(incidence) == len(curve["incidences"]) == valence,
            "Duplicate physical source curve incidence")
    order = []
    for pair in order_text:
        match = re.fullmatch(r"(\\d+):(\\d+)", pair)
        require(match is not None, "Invalid radial patch/side identity")
        key = tuple(int(x) for x in match.groups())
        require(key in incidence and key not in
                {(x["patch_index"], x["side"]) for x in order},
                "Fabricated or repeated radial incidence")
        source_side = incidence[key]
        require(isinstance(source_side["curve_reversed"], bool) and
                source_side["winding_sign"] in (-1, 1),
                "Malformed physical source direction")
        order.append({
            "patch_index": key[0], "side": key[1],
            "curve_reversed": source_side["curve_reversed"],
            "winding_sign": source_side["winding_sign"],
        })
    require(len(order) == valence and
            int(sectors["angular_adjacent_pairs"]) == valence and
            int(sectors["curve_incidences"]) == valence,
            "Original radial ring did not cover every source patch side")
    intervals = []
    for index, (a, b) in enumerate(zip(parameters, parameters[1:])):
        links = []
        for at, item in enumerate(order):
            next_item = order[(at + 1) % len(order)]
            links.append({
                **item,
                "radial_next": [next_item["patch_index"], next_item["side"]],
                "manifold_twin": None,
                "node_sharing": "NOT_AUTHORIZED",
            })
        intervals.append({
            "curve_index": curve["curve_id"],
            "interval_ordinal": index,
            "original_parameters": [a, b],
            "original_source_node_ids": [node_ids[index], node_ids[index+1]],
            "radial_cycle": links,
            "interval_orientation": "CERTIFIED_SIGNED_BERNSTEIN",
            "physical_sheet_continuation": "UNDECIDED",
        })
    return {
        "model": model,
        "model_sha256": model_sha,
        "m4_graph_sha256": graph_sha,
        "source_log_sha256": log_sha,
        "source_curve_index": curve["curve_id"],
        "source_curve_id": int(source["curve_id"]),
        "source_epoch": int(source["epoch"]),
        "source_retry": int(source["retry"]),
        "radial_valence": valence,
        "original_source_intervals": intervals,
        "original_radial_cycle": order,
        "interval_certificate": {
            "count": valence * interval_count,
            "certified": valence * interval_count,
            "unresolved": 0,
            "inverted": 0,
            "minimum_oriented_lower": float(proof["smallest_positive_lower"]),
            "wide_reference_pairs": int(proof["wide_reference_pairs"]),
        },
        "automatic_sheet_pairing_enabled": False,
        "physical_SubMesh_published": False,
    }


def pending_policy(record: dict) -> dict:
    return {
        "schema_version": 1,
        "model_sha256": record["model_sha256"],
        "curve_index": record["source_curve_index"],
        "source_epoch": record["source_epoch"],
        "source_retry": record["source_retry"],
        "junction_kind": "UNDECIDED",
        "approval_status": "PENDING_ADVISOR_REVIEW",
        "incidences": [
            {
                "patch_index": item["patch_index"],
                "side": item["side"],
                "reversed": item["curve_reversed"],
                "sheet_id": None,
                "node_sharing_policy": "UNDECIDED",
            }
            for item in record["original_radial_cycle"]
        ],
        "approved_continuations": [],
        "evidence": {
            "source_log_sha256": record["source_log_sha256"],
            "radial_cycle_sha256": digest({
                "cycle": record["original_radial_cycle"],
                "intervals": record["original_source_intervals"],
            }),
            "m4_graph_sha256": record["m4_graph_sha256"],
        },
    }


def validate_pending_policy(record: dict, policy: object) -> dict:
    expected = pending_policy(record)
    require(type(policy) is dict and set(policy) == set(expected),
            "Policy has missing or unrecognized fields")
    for name in expected:
        require(type(policy[name]) is type(expected[name]) and
                policy[name] == expected[name],
                f"Unapproved or stale source-bound policy field: {name}")
    return {"schema_valid": True, "scientific_admission": False,
            "physical_node_welding": False, "reason": "PENDING_ADVISOR_REVIEW"}


def test_negative_controls(record: dict) -> int:
    policy = pending_policy(record)
    require(validate_pending_policy(record, policy)["scientific_admission"] is False,
            "Unreviewed source policy was scientifically admitted")
    mutations = [
        ("model_sha256", "0"*64),
        ("curve_index", policy["curve_index"] + 1),
        ("source_epoch", policy["source_epoch"] + 1),
        ("source_retry", policy["source_retry"] + 1),
        ("junction_kind", "MANIFOLD"),
        ("approval_status", "SCIENTIFICALLY_APPROVED"),
        ("approved_continuations", [[0, 1]]),
        ("incidences", []),
        ("incidences", policy["incidences"] + policy["incidences"][:1]),
        ("evidence", {}),
        ("schema_version", 2),
    ]
    count = 0
    for field, changed in mutations:
        invalid = deepcopy(policy)
        invalid[field] = changed
        try:
            validate_pending_policy(record, invalid)
        except ValueError:
            count += 1
        else:
            raise AssertionError(f"Unapproved policy mutation accepted: {field}")
    for field, changed in (
        ("patch_index", 1000000),
        ("side", 8),
        ("sheet_id", "fabricated-sheet"),
        ("node_sharing_policy", "SHARE"),
        ("reversed", not policy["incidences"][0]["reversed"]),
    ):
        invalid = deepcopy(policy)
        invalid["incidences"][0][field] = changed
        try:
            validate_pending_policy(record, invalid)
        except ValueError:
            count += 1
        else:
            raise AssertionError(f"Unapproved incidence mutation accepted: {field}")
    for field in expected_hashes():
        invalid = deepcopy(policy)
        invalid["evidence"][field] = "0"*64
        try:
            validate_pending_policy(record, invalid)
        except ValueError:
            count += 1
        else:
            raise AssertionError(f"Forged source hash accepted: {field}")
    return count


def expected_hashes() -> tuple[str, ...]:
    return ("source_log_sha256", "radial_cycle_sha256", "m4_graph_sha256")


def run(root: Path, graph_directory: Path,
        source_log: Path, output_directory: Path) -> dict:
    log_bytes = source_log.read_bytes()
    reports = parse_log(source_log)
    manifest_path = graph_directory / "m4_sheet_incidence_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest["status"] ==
            "SOURCE_LINKED_PATCH_CURVE_INCIDENCE_GRAPH_NO_WELDING" and
            manifest["actual_node_welding"] is False and
            manifest["approved_scientific_sheet_policy"] is False,
            "Native source-linked M4 graph manifest not qualified")
    outcome = []
    negative_count = 0
    for name, (valence, intervals) in MODELS.items():
        model_key = MODEL_FILES[name]
        records = []
        for center in CENTER_RULES:
            filename = f"sheet_graph_{model_key}_{center}.json"
            target = graph_directory / filename
            raw = target.read_bytes()
            item = next((x for x in manifest["outcomes"]
                         if x["model"] == name and x["center_rule"] == center),
                        None)
            require(item is not None and item["json"] == filename and
                    item["sha256"] == sha(raw),
                    "Physical source graph differs from original M4 manifest")
            graph = json.loads(raw)
            records.append(source_record(graph, reports, name,
                                         root, sha(raw), sha(log_bytes)))
        a, b = records
        for key in ("model_sha256", "source_curve_index", "source_curve_id",
                    "source_epoch", "source_retry", "radial_valence",
                    "original_source_intervals", "original_radial_cycle",
                    "interval_certificate"):
            require(a[key] == b[key],
                    "Experimental center rule changed original radial source")
        require(len(a["original_source_intervals"]) == intervals and
                a["radial_valence"] == valence,
                "R2c-0 source interval record count is incomplete")
        policy = pending_policy(a)
        outcome_status = validate_pending_policy(a, policy)
        controls = test_negative_controls(a)
        negative_count += controls
        output_directory.mkdir(parents=True, exist_ok=True)
        record_path = output_directory / f"r2c0_{model_key}_radial_incidence.json"
        policy_path = output_directory / f"r2c0_{model_key}_pending_policy.json"
        record_path.write_text(json.dumps(a, indent=2, allow_nan=False)+"\\n",
                               encoding="utf-8")
        policy_path.write_text(json.dumps(policy, indent=2)+"\\n",
                               encoding="utf-8")
        outcome.append({
            "model": name, "source_curve_index": a["source_curve_index"],
            "source_intervals": intervals,
            "radial_valence": valence,
            "verified_source_interval_adjacencies": intervals * valence,
            "policy": outcome_status["reason"],
            "negative_controls": controls,
            "record": record_path.name,
            "policy_template": policy_path.name,
            "record_sha256": sha(record_path.read_bytes()),
            "policy_sha256": sha(policy_path.read_bytes()),
        })
    result = {
        "schema": "apmesh.quad.r2c0.source_radial_incidence.v1",
        "status": "READ_ONLY_ORIGINAL_SOURCE_RADIAL_RINGS_NO_SHEET_APPROVAL",
        "source_log_sha256": sha(log_bytes),
        "m4_manifest_sha256": sha(manifest_path.read_bytes()),
        "outcomes": outcome,
        "negative_controls_rejected": negative_count,
        "radial_next_is_topological_twin": False,
        "automatic_sheet_pairing_enabled": False,
        "physical_nodes_welded": False,
        "physical_SubMesh_published": False,
        "production_quad_enabled": False,
    }
    (output_directory / "r2c0_manifest.json").write_text(
        json.dumps(result, indent=2, allow_nan=False)+"\\n", encoding="utf-8")
    print(f"R2C0_SOURCE_INCIDENCE models=2 source_intervals=22 "
          f"adjacencies=376 negative_controls={negative_count} "
          "radial_records=source_verified node_welding=0 "
          "scientific_sheet_approval=0 physical_SubMesh_published=0")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--graph-directory", type=Path, required=True)
    parser.add_argument("--source-log", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    run(args.root.resolve(), args.graph_directory.resolve(),
        args.source_log.resolve(), args.directory.resolve())
