#!/usr/bin/env python3
"""Classify source-STL incidence invariants without geometry healing or mesh claims."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

QUADWILD_IDS = (44503, 128001, 58012, 61394, 67792, 69975, 81877, 94884,
                230923, 364256, 423069, 498974)
BADIA_IDS = (252119, 293137, 35269, 37266, 37881, 441708, 47076,
             550964, 551021, 65904, 96457)
PINNED_MIRROR_REVISIONS = {
    1: "2d6f82c6f7934f23b051daf2b19e918c62d30d7b",
    2: "ab50a098405dc2dfcf882e87dab3811b5ea8ce92",
    3: "626090c1a0bca7e31fe6c1cb5aede8541b16a7b7",
}
EXPECTED_TREE_SHA = {
    "1": "273d0a4ef6191be5a55ae54be37a285e235bfc83",
    "2": "e618767837922a374b56c48a7be956425ec6f617",
    "3": "d7006757ed730043b237ceedb1452c25342ee860",
}

REQUIRED = (
    "source_triangles", "source_unique_exact_vertices", "source_unique_exact_edges",
    "edge_incidence_histogram", "boundary_edges", "two_face_edges",
    "three_plus_edges", "raw_duplicate_triangles", "zero_area_triangles",
    "edge_winding_conflicts", "vertex_connected_components", "vertex_link_interior",
    "vertex_link_boundary", "vertex_link_singular",
)


def topology_invariants(topology: dict) -> dict:
    """Check combinatorial identities and conditionally derive orientable genus."""
    if not isinstance(topology, dict):
        raise ValueError("Topology must be an object")
    for key in REQUIRED:
        if key not in topology:
            raise ValueError(f"Missing topology field: {key}")
    for key in REQUIRED:
        if key == "edge_incidence_histogram":
            continue
        val = topology[key]
        if type(val) is not int or val < 0:
            raise ValueError(f"Nonnegative integer required: {key}")
    n_faces = topology["source_triangles"]
    n_edges = topology["source_unique_exact_edges"]
    n_verts = topology["source_unique_exact_vertices"]
    if not n_faces or not n_edges or not n_verts:
        raise ValueError("Nonempty source triangle complex required")
    hist = topology["edge_incidence_histogram"]
    if not isinstance(hist, dict) or not hist:
        raise ValueError("Missing nonempty edge incidence histogram")
    counts = Counter()
    for key, val in hist.items():
        if not re.fullmatch(r"[1-9][0-9]*", str(key)) or type(val) is not int or val < 0:
            raise ValueError("Invalid edge incidence histogram entry")
        counts[int(key)] = val
    if sum(counts.values()) != n_edges:
        raise ValueError("Edge total differs from incidence histogram")
    if sum(degree * count for degree, count in counts.items()) != 3 * n_faces:
        raise ValueError("Triangle-corner edge uses inconsistent with incidence histogram")
    if counts[1] != topology["boundary_edges"] or counts[2] != topology["two_face_edges"]:
        raise ValueError("Edge incidence class counts inconsistent")
    if sum(v for k, v in counts.items() if k >= 3) != topology["three_plus_edges"]:
        raise ValueError("Three-plus incidence count inconsistent")
    if (
        topology["vertex_link_interior"] + topology["vertex_link_boundary"]
        + topology["vertex_link_singular"] != n_verts
    ):
        raise ValueError("Vertex link category totals inconsistent")
    bad = []
    checks = {
        "closed": topology["boundary_edges"] == 0,
        "edge_manifold": topology["three_plus_edges"] == 0,
        "one_component": topology["vertex_connected_components"] == 1,
        "vertex_manifold": topology["vertex_link_singular"] == 0
        and topology["vertex_link_boundary"] == 0,
        "nondegenerate": topology["zero_area_triangles"] == 0,
        "nonduplicated": topology["raw_duplicate_triangles"] == 0,
        "oriented_two_face_edges": topology["edge_winding_conflicts"] == 0,
        "all_vertex_links_closed_cycles": topology["vertex_link_interior"] == n_verts,
    }
    bad = [key for key, passed in checks.items() if not passed]
    chi = n_verts - n_edges + n_faces
    if bad:
        return {
            "source_mesh_euler_characteristic_raw": chi,
            "closed_connected_orientable_surface_screen": "NOT_PROVED",
            "applicable_genus": None,
            "failed_conditions": bad,
            "interpretation": "Raw Euler number is not a surface genus certificate",
        }
    numerator = 2 - chi
    if numerator < 0 or numerator % 2:
        raise ValueError("Closed connected orientable surface has impossible Euler/genus parity")
    return {
        "source_mesh_euler_characteristic_raw": chi,
        "closed_connected_orientable_surface_screen": "COMBINATORIAL_PASS",
        "applicable_genus": numerator // 2,
        "failed_conditions": [],
        "interpretation": (
            "Genus of exact-coordinate reconstructed source triangle complex, "
            "not an independent continuous geometric or CAD-topology proof"
        ),
    }


def verify_snapshot(snapshot: dict) -> dict:
    """Validate a frozen seven-source receipt and retain the full 23-file denominator."""
    if snapshot.get("schema") != "apmesh-thingi10k-f17-source-git-tree-v1":
        raise ValueError("Unexpected frozen manifest schema")
    entries = snapshot.get("source_archives")
    audits = snapshot.get("raw_stl_audits")
    if not isinstance(entries, list) or len(entries) != 23:
        raise ValueError("Exactly 23 literature source archive entries required")
    if not isinstance(audits, list) or len(audits) != 7:
        raise ValueError("Exactly seven raw source STL audits required at F17")
    if snapshot.get("source_archive_git_tree_sha1") != EXPECTED_TREE_SHA:
        raise ValueError("Pinned Git source tree identity changed")
    by_id = {}
    for e in entries:
        i = e.get("thingi10k_file_id")
        if type(i) is not int or i in by_id or i <= 0:
            raise ValueError("Invalid or duplicate source file ID")
        if not re.fullmatch(r"[0-9a-f]{40}", e.get("zip_git_blob_sha1", "")):
            raise ValueError("Archive blob must be pinned")
        if type(e.get("zip_bytes")) is not int or e["zip_bytes"] <= 0:
            raise ValueError("Archive size must be pinned")
        if e.get("literature_cohort") not in ("QUADWILD_FIG29", "BADIA_FIG10_TABLE1"):
            raise ValueError("Invalid literature cohort")
        if e.get("individual_license_independently_approved") is not False:
            raise ValueError("Premature license approval")
        if e.get("quadwild_per_id_output_pair_verified") is not False:
            raise ValueError("Premature QuadWild pair claim")
        if e.get("apmesh_mesh_generated") is not False:
            raise ValueError("Premature APMesh completion claim")
        expected_cohort = ("QUADWILD_FIG29" if i in QUADWILD_IDS else
                           "BADIA_FIG10_TABLE1" if i in BADIA_IDS else None)
        if e["literature_cohort"] != expected_cohort:
            raise ValueError("Unexpected frozen literature ID/cohort")
        number = e.get("mirror_repository_number")
        if type(number) is not int or number not in PINNED_MIRROR_REVISIONS:
            raise ValueError("Missing known pinned mirror repository")
        if e.get("mirror_archive_repository") != f"larsbrubaker/Thingi10K-meshes-{number}":
            raise ValueError("Mirror repository/name mismatch")
        if e.get("mirror_pinned_commit") != PINNED_MIRROR_REVISIONS[number]:
            raise ValueError("Mirror commit is not immutable/pinned")
        if e.get("source_archive_relative_path") != f"meshes/{i}.stl.zip":
            raise ValueError("Unexpected source mesh archive path")
        by_id[i] = e
    if set(by_id) != set(QUADWILD_IDS) | set(BADIA_IDS):
        raise ValueError("Frozen 23-ID literature roster changed")
    if sum(x["literature_cohort"] == "QUADWILD_FIG29" for x in entries) != 12:
        raise ValueError("QuadWild denominator changed")
    if sum(x["literature_cohort"] == "BADIA_FIG10_TABLE1" for x in entries) != 11:
        raise ValueError("Badia denominator changed")
    expected_ids = (293137, 37881, 61394, 58012, 47076, 550964, 96457)
    if tuple(e.get("thingi10k_file_id") for e in audits) != expected_ids:
        raise ValueError("F16+F17 audited identifiers/order changed")
    genus = {}
    for audit in audits:
        i = audit["thingi10k_file_id"]
        origin = by_id[i]
        if not re.fullmatch(r"[0-9a-f]{64}", audit.get("raw_stl_sha256", "")):
            raise ValueError(f"Raw STL hash absent for {i}")
        if audit.get("zip_git_blob_sha1") != origin["zip_git_blob_sha1"]:
            raise ValueError(f"Archive identity mismatch for {i}")
        if audit.get("zip_bytes") != origin["zip_bytes"]:
            raise ValueError(f"Archive byte size mismatch for {i}")
        metrics = topology_invariants(audit.get("topology"))
        if audit["topology"]["source_triangles"] != origin["original_stl_triangles_catalog"]:
            raise ValueError(f"Triangle count mismatch for {i}")
        genus[str(i)] = metrics
    if genus["61394"]["applicable_genus"] is not None:
        raise ValueError("Adversarial source cannot have certified surface genus")
    return {
        "manifest_entries": len(entries),
        "audited_original_stl_files": len(audits),
        "quadwild_source_genus_proved_for": [
            idv for idv in QUADWILD_IDS
            if str(idv) in genus and genus[str(idv)]["applicable_genus"] is not None
        ],
        "topology_invariants": genus,
        "status": "SOURCE_ARCHIVE_PINNED_AND_SEVEN_STL_CHECKED_NO_REFERENCE_QUAD_OR_APMESH",
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--snapshot", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    opts = p.parse_args(argv)
    src = opts.snapshot.read_bytes()
    if len(src) > 1_000_000:
        raise ValueError("Frozen source snapshot too large")
    report = verify_snapshot(json.loads(src))
    opts.output.parent.mkdir(parents=True, exist_ok=True)
    with opts.output.open("x", encoding="utf-8") as dest:
        json.dump(report, dest, sort_keys=True, indent=2)
        dest.write("\n")
    print(json.dumps({key: report[key] for key in ("manifest_entries", "audited_original_stl_files", "status")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
