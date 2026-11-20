"""R2.7.34: read-only genuine original source curve object and selected TRI seam audit.

No pointer addresses are serialized. Real Adapter returns are precommit; pairwise
XYZ boundary diagnostics never certify source welding or global adaptive LOD.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path

from .native_controlled_sensitivity import git_blob
from .native_selected_tri_return import (
    ROLES,
    attest as attest_r2733,
    audit as audit_r2733,
    parse_original_tri_bytes,
    parse_real_adapter_returns,
    _read,
)
from .verify_native_lineage import (
    decode_ndjson, require,
)

SCHEMA = "apmesh.meshstudio.r2734.original_source_curve_object_and_provisional_tri_seam.v1"
PROTOCOL = (
    "docs/mesh-studio/"
    "R2_7_34_PREREGISTERED_SOURCE_CURVE_IDENTITY_AND_SELECTED_TRI_SEAMS_20261120.md"
)
PROBE = "tests/quad/generator_selected_curve_seam_probe.cpp"
PROTOCOL_BLOB = "d0c7f8fcbd148a4406d48f80d1fc51e43177c94e"
PROBE_BLOB = "c493b62ba7be2c8aecdd6078fe9b4238322d7a15"
UV_TOL = 1.0e-8
MAX_SAMPLE_POINTS = 200_000


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def attest(root: Path) -> dict:
    """Pin original scientific C++ and this distinct non-address-leaking probe."""
    existing = attest_r2733(root)
    for path, blob in ((PROTOCOL, PROTOCOL_BLOB), (PROBE, PROBE_BLOB)):
        raw = _read(root / path, 100_000)
        require(len(blob) == 40 and git_blob(raw) == blob,
                "r2734_preregistered_source_or_original_curve_observer_drift")
        existing[path] = {"git_blob": blob, "sha256": _sha(raw)}
    probe = _read(root / PROBE, 100_000)
    cmake = _read(root / "CMakeLists.txt", 150_000)
    require(
        b"OriginalCurveObjectOrdinal(curve)" in probe and
        b"source_object_group" in probe and
        b"source_endpoint_xyz" in probe and
        b"__real__ZN7Adapter11AdaptDomainEP10PatchCoonsPN9Performer9IdManagerEddiiii" in probe and
        b"LINKER:--wrap=_ZN7Adapter11AdaptDomainEP10PatchCoonsPN9Performer9IdManagerEddiiii" in cmake and
        b"target_link_options(quad_generator_selected_curve_seam_probe" in cmake and
        b"reinterpret_cast<std::uintptr_t>" not in probe and
        b"static_cast<std::uintptr_t>" not in probe and
        b"%p" not in probe,
        "r2734_source_pointer_equality_not_exactly_opt_in_and_address_free",
    )
    return existing


def accepted_canonical_source_incidence(raw: bytes) -> dict[int, tuple]:
    """Read *accepted step-1* CAD source slots, never rejected step-4 faces."""
    rows = decode_ndjson(raw)
    head = next((x for x in rows if x.get("type") == "accepted_commit"), None)
    require(head is not None and head.get("step") == 1 and
            head.get("source_curve_count") == 13 and
            head.get("source_patch_count") == 4,
            "r2734_only_original_source_step1_curve_geometry_is_canonical")
    patches = [row for row in rows if row.get("type") == "patch"]
    require(len(patches) == 4 and
            {p.get("patch_slot") for p in patches} == set(range(4)),
            "r2734_original_accepted_source_patch_incidence_incomplete")
    member = defaultdict(list)
    for patch in patches:
        curves = patch.get("source_curves")
        require(type(curves) is list and len(curves) == 4,
                "r2734_original_accepted_source_patch_not_four_sided")
        for side, edge in enumerate(curves):
            slot = edge.get("source_curve_slot")
            require(edge.get("edge_slot") == side and
                    type(slot) is int and 0 <= slot < 13 and
                    type(edge.get("reversed")) is bool,
                    "r2734_forged_original_accepted_source_curve_slot")
            member[slot].append((patch["patch_slot"], side,
                                 edge["reversed"]))
    require(set(member) == set(range(13)),
            "r2734_accepted_source_curve_slot_inventory_changed")
    signatures = {slot: tuple(sorted(values))
                  for slot, values in member.items()}
    require(len(set(signatures.values())) == 13 and
            sorted(map(len, signatures.values())) == [1] * 12 + [4],
            "r2734_canonical_accepted_curve_incidence_signatures_ambiguous")
    return signatures


def tri_source_edge_geometry(raw: bytes, returned: dict) -> dict:
    """Recover native face edge incidence and UV-side XYZ from true Adapter TRI."""
    # Reuse the earlier independent original post-AFT TRI ID/UV validation.
    basic = parse_original_tri_bytes(raw, returned)
    rows = [json.loads(line) for line in raw.splitlines()]
    header = rows[0]
    curves = header["source_curves"]
    require(len(curves) == 4, "r2734_selected_patch_has_no_four_curve_edges")
    for edge in curves:
        group = edge.get("source_object_group")
        coords = edge.get("source_endpoint_xyz")
        require(type(group) is int and 0 <= group < 100 and
                type(coords) is list and len(coords) == 2 and
                all(type(x) is list and len(x) == 3 and
                    all(type(v) in (int, float) and math.isfinite(v) for v in x)
                    for x in coords),
                "r2734_original_source_curve_object_or_xyz_not_observed")
    edge_incidence = defaultdict(list)
    for face in rows[1:-1]:
        vertices = face["vertices"]
        for j in range(3):
            a, b = vertices[j], vertices[(j + 1) % 3]
            key = tuple(sorted((a["native_node_id"], b["native_node_id"])))
            edge_incidence[key].append((a, b))
            require(len(edge_incidence[key]) <= 2,
                    "r2734_selected_tri_local_nonmanifold_edge")
    free = [pair[0] for pair in edge_incidence.values()
            if len(pair) == 1]
    sides = {i: {"xyz": set(), "edges": 0} for i in range(4)}
    unclassified = 0
    multiply_classified = 0
    for a, b in free:
        ua, va = a["uv"]
        ub, vb = b["uv"]
        tests = (
            abs(va) <= UV_TOL and abs(vb) <= UV_TOL,
            abs(ua - 1) <= UV_TOL and abs(ub - 1) <= UV_TOL,
            abs(va - 1) <= UV_TOL and abs(vb - 1) <= UV_TOL,
            abs(ua) <= UV_TOL and abs(ub) <= UV_TOL,
        )
        indexes = [i for i, yes in enumerate(tests) if yes]
        if not indexes:
            unclassified += 1
        elif len(indexes) > 1:
            multiply_classified += 1
        else:
            side = sides[indexes[0]]
            side["edges"] += 1
            side["xyz"].add(tuple(float(v) for v in a["xyz"]))
            side["xyz"].add(tuple(float(v) for v in b["xyz"]))
    require(sum(x["edges"] for x in sides.values()) +
            unclassified + multiply_classified == len(free),
            "r2734_original_selected_tri_boundary_edge_accounting_lost")
    require(len(free) <= 3 * returned["faces"],
            "r2734_native_boundary_edge_count_exceeds_faces")
    return {
        "curves": curves,
        "sides": sides,
        "free_edges": len(free),
        "unclassified_free_edges": unclassified,
        "multiply_classified_free_edges": multiply_classified,
        "prior_native_tri_geometry": basic,
    }


def _nearest_xyz(source: set[tuple], other: set[tuple]) -> tuple[float, float]:
    """Finite, source-unit nearest-vertex distances without coordinate welding."""
    require(len(source) >= 2 and len(other) >= 2 and
            len(source) <= MAX_SAMPLE_POINTS and
            len(other) <= MAX_SAMPLE_POINTS,
            "r2734_selected_source_curve_side_missing_or_oversized")
    minima = []
    for x in source:
        minimum = min(math.dist(x, y) for y in other)
        require(math.isfinite(minimum), "r2734_nonfinite_native_xyz_distance")
        minima.append(minimum)
    return max(minima), sum(minima) / len(minima)


def symmetric_seam_pair(a: set[tuple], b: set[tuple]) -> dict:
    """Descriptive XYZ nearest neighbors: not a continuous Hausdorff bound."""
    worst_a, mean_a = _nearest_xyz(a, b)
    worst_b, mean_b = _nearest_xyz(b, a)
    # The original double coordinates are parsed from the native ASCII
    # setprecision(17) source; hex representations distinguish even signed zero.
    hex_a = {tuple(float(value).hex() for value in p) for p in a}
    hex_b = {tuple(float(value).hex() for value in p) for p in b}
    return {
        "owner_a_xyz_vertex_count": len(a),
        "owner_b_xyz_vertex_count": len(b),
        "max_vertex_to_vertex_xyz_distance":
            max(worst_a, worst_b),
        "mean_a_to_b_nearest_xyz": mean_a,
        "mean_b_to_a_nearest_xyz": mean_b,
        "exact_double_vertex_set_equal": hex_a == hex_b,
        "exact_double_vertex_jaccard":
            len(hex_a & hex_b) / len(hex_a | hex_b),
        "no_continuous_geometric_hausdorff_bound": True,
        "no_physical_source_node_welding_asserted": True,
    }


def observed_original_curve_groups(
        step4: list[dict], original_source: dict[int, tuple]) -> dict:
    """Map real original pointer groups onto original accepted source slots by
    complete (patch, edge, orientation) signatures, never native ID=0.
    """
    members = defaultdict(set)
    seen_edge = defaultdict(set)
    by_observation = defaultdict(list)
    for observation in step4:
        row = observation["return"]
        curves = observation["geometry"]["curves"]
        for edge_slot, curve in enumerate(curves):
            group = curve["source_object_group"]
            member = (row["patch"], edge_slot, curve["reversed"])
            members[group].add(member)
            seen_edge[(row["patch"], edge_slot)].add(group)
            by_observation[group].append({
                "return_index": row["return_index"],
                "patch": row["patch"], "edge_slot": edge_slot,
                "source_curve_points": curve["source_curve_points"],
                "endpoint_xyz": curve["source_endpoint_xyz"],
            })
    require(len(members) == 13 and
            set(members) == set(range(13)) and
            all(len(groups) == 1 for groups in seen_edge.values()) and
            len(seen_edge) == 16,
            "r2734_native_source_curve_object_group_unstable_or_incomplete")
    observed_signatures = {group: tuple(sorted(value))
                           for group, value in members.items()}
    reverse = {signature: slot for slot, signature in original_source.items()}
    require(len(reverse) == 13 and
            set(observed_signatures.values()) == set(reverse),
            "r2734_cpp_pointer_equality_group_not_canonical_source_curve")
    mapping = {group: reverse[signature]
               for group, signature in observed_signatures.items()}
    return {
        "source_object_group_to_original_accepted_curve_slot": {
            str(group): slot for group, slot in sorted(mapping.items())
        },
        "original_source_curve_membership": {
            str(reverse[signature]): [
                {"patch": patch, "edge": edge, "reversed": reversed_flag}
                for patch, edge, reversed_flag in signature]
            for signature in observed_signatures.values()
        },
        "source_curve_ownership_signatures_match_actual_accepted_step1": True,
        "original_unique_source_objects_seen": 13,
        "shared_source_original_curve_slots": [
            slot for slot, sig in original_source.items() if len(sig) > 1],
        "source_original_curve_cpp_pointer_address_serialized": False,
        "original_native_curve_id_not_an_identity_key": True,
    }


def analyze_one_role(out: Path, role: str) -> dict:
    """Re-open actual original curve/selected TRI raw bytes and complete cohort."""
    folder = out / role
    raw_accepted = _read(folder / "accepted_step_1_retry_0.ndjson",
                         30_000_000)
    canonical = accepted_canonical_source_incidence(raw_accepted)
    stdout = _read(folder / "original-wrapper-stdout.log", 3_000_000)
    returns = parse_real_adapter_returns(stdout)
    selected = []
    for returned in returns:
        if returned["step"] != 4:
            continue
        raw = _read(
            folder / "selected_post_aft_tri" / returned["file"], 80_000_000)
        selected.append({
            "return": returned,
            "geometry": tri_source_edge_geometry(raw, returned),
            "raw_sha256": _sha(raw),
        })
    require(len(selected) == 16 and
            set(x["return"]["patch"] for x in selected) == set(range(4)),
            "r2734_source_selected_original_step4_return_count_missing")
    identity = observed_original_curve_groups(selected, canonical)
    by_curve = {int(group): int(slot) for group, slot in
                identity["source_object_group_to_original_accepted_curve_slot"].items()}
    outer_by_patch = defaultdict(list)
    for observation in selected:
        r = observation["return"]
        outer_by_patch[(r["outer_epoch"], r["outer_retry"],
                        r["patch"])].append(observation)
    by_cohort = defaultdict(dict)
    for (epoch, outer_retry, patch), seq in outer_by_patch.items():
        require(len(seq) == 2, "r2734_original_outer_patch_regeneration_order_incomplete")
        seq.sort(key=lambda x: x["return"]["return_index"])
        for which, item in enumerate(seq):
            key = (epoch, outer_retry, which)
            require(patch not in by_cohort[key],
                    "r2734_source_outer_selected_patch_duplicate")
            by_cohort[key][patch] = item
    require(len(by_cohort) == 4 and
            all(set(c) == set(range(4)) for c in by_cohort.values()),
            "r2734_four_original_source_selected_cohorts_incomplete")

    all_pairs = []
    for (epoch, outer_retry, which), patches in sorted(by_cohort.items()):
        for source_slot, owners in sorted(canonical.items()):
            if len(owners) < 2:
                continue
            for (pa, ea, _), (pb, eb, _) in itertools.combinations(owners, 2):
                a = patches[pa]["geometry"]["sides"][ea]
                b = patches[pb]["geometry"]["sides"][eb]
                comparison = {
                    "source_curve_slot": source_slot,
                    "original_global_epoch": epoch,
                    "original_global_retry": outer_retry,
                    "per_patch_adapter_return_occurrence": which,
                    "patch_a": pa, "edge_a": ea,
                    "patch_b": pb, "edge_b": eb,
                    "return_index_a": patches[pa]["return"]["return_index"],
                    "return_index_b": patches[pb]["return"]["return_index"],
                    "source_edge_count_a": a["edges"],
                    "source_edge_count_b": b["edges"],
                }
                if len(a["xyz"]) >= 2 and len(b["xyz"]) >= 2:
                    comparison["status"] = "measured_source_selected_local_xyz"
                    comparison.update(symmetric_seam_pair(a["xyz"], b["xyz"]))
                else:
                    comparison["status"] = "unsupported_missing_source_boundary"
                    comparison["source_vertices_a"] = len(a["xyz"])
                    comparison["source_vertices_b"] = len(b["xyz"])
                all_pairs.append(comparison)
    require(len(all_pairs) == 4 * 6 and
            all(x["source_curve_slot"] == 3 for x in all_pairs),
            "r2734_original_shared_source_curve_fan_pair_count_changed")
    measured = [p for p in all_pairs
                if p["status"] == "measured_source_selected_local_xyz"]
    boundary_summary = {
        "selected_post_aft_return_count": 16,
        "per_return_boundary_free_edge_counts": [
            {
                "return_index": item["return"]["return_index"],
                "patch": item["return"]["patch"],
                "outer_epoch": item["return"]["outer_epoch"],
                "outer_retry": item["return"]["outer_retry"],
                "free_edges": item["geometry"]["free_edges"],
                "unclassified": item["geometry"]["unclassified_free_edges"],
                "multiply_classified":
                    item["geometry"]["multiply_classified_free_edges"],
                "side_segment_counts": {
                    str(edge): g["edges"]
                    for edge, g in item["geometry"]["sides"].items()},
                "raw_original_tri_sha256": item["raw_sha256"],
            } for item in selected],
        "total_unclassified_original_native_local_free_edges":
            sum(item["geometry"]["unclassified_free_edges"]
                for item in selected),
        "total_multiply_classified_original_native_local_free_edges":
            sum(item["geometry"]["multiply_classified_free_edges"]
                for item in selected),
    }
    return {
        "role": role,
        "original_source_accepted_step1_canonical_curve_count": 13,
        "original_accepted_source_step1_sha256": _sha(raw_accepted),
        "source_curve_identity": identity,
        "original_observed_original_source_native_curve_ids": sorted({
            curve["native_curve_id"] for item in selected for curve in
            item["geometry"]["curves"]}),
        "local_selected_return_boundary_diagnostics": boundary_summary,
        "source_shared_curve_fan_pairwise_selected_seam_diagnostics": all_pairs,
        "total_true_source_fan_pair_comparisons": len(all_pairs),
        "total_measurable_source_selected_pairs": len(measured),
        "total_unqualified_missing_boundary_pairs": len(all_pairs) - len(measured),
        "max_observed_discrete_xyz_pair_distance":
            max((p["max_vertex_to_vertex_xyz_distance"] for p in measured),
                default=None),
        "exact_source_xyz_vertex_set_match_pairs":
            sum(p["exact_double_vertex_set_equal"] for p in measured),
        "shared_curve_geometry_is_source_native_provisional_not_global_commit": True,
        "shared_curve_original_cpp_pointer_address_leaked": False,
        "cross_patch_original_cpp_node_welding_qualified": False,
        "continuous_original_surface_hausdorff_error_qualified": False,
        "scientific_lod_qualified": False,
    }


def audit(root: Path, out: Path) -> dict:
    """Require native R2.7.33 full raw scientific parity first."""
    source = attest(root.resolve())
    original = audit_r2733(root, out)
    require(original["global_original_acceptance_and_scientific_output_parity_qualified"] is True
            and original["scientific_lod_qualified"] is False,
            "r2734_original_cpp_selected_tri_source_parity_not_qualified")
    roles = {role: analyze_one_role(out, role) for role in ROLES}
    return {
        "schema": SCHEMA,
        "original_cpp_source_and_research_observer_attestation": source,
        "underlying_r2733_native_tri_and_parity_source_verified": True,
        "original_source_real_cpp_two_process_roles": list(ROLES),
        "role_measurements": roles,
        "source_curve_identity_attested_without_native_curve_id_assumption": True,
        "shared_source_curve_fan_not_reduced_to_manifold_pair": True,
        "original_native_global_accepted_steps_per_process": [1],
        "source_selected_local_not_global_commit": True,
        "source_shared_boundary_xyz_discrete_only_not_continuous_error": True,
        "physical_source_curve_node_welding_not_certified": True,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--selected-directory", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    require(not a.output.exists(), "r2734_source_original_audit_report_must_be_new")
    result = audit(a.root, a.selected_directory)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(
        json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8")
    print("R2734_SOURCE_CURVE_IDENTITY_AND_DISCRETE_SELECTED_TRI_SEAMS=" +
          json.dumps({
              role: {
                  "mapped_original_source_curves": result[
                      "role_measurements"][role][
                      "source_curve_identity"][
                      "original_unique_source_objects_seen"],
                  "observed_provisional_selected_tri_returns": 16,
                  "actual_shared_curve_side_pairs": result[
                      "role_measurements"][role][
                      "total_true_source_fan_pair_comparisons"],
                  "measurable_discrete_xyz_pairs": result[
                      "role_measurements"][role][
                      "total_measurable_source_selected_pairs"],
                  "exact_xyz_vertex_set_match_pairs": result[
                      "role_measurements"][role][
                      "exact_source_xyz_vertex_set_match_pairs"],
                  "lod": False,
              } for role in ROLES
          }, sort_keys=True))


if __name__ == "__main__":
    main()
