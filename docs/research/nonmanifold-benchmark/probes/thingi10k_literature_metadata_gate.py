#!/usr/bin/env python3
"""Audit a frozen Thingi10K literature cohort against pinned catalog metadata.

The catalog is third-party metadata, not a substitute for mesh-byte topology,
rights verification, a quad result pair, or an APMesh mesh-generation run.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from collections import Counter
from pathlib import Path

PINNED_CATALOG_BLOB_SHA1 = "ac376cc8604436f9460cac39b5171ce8d99b2e74"
PINNED_CATALOG_COMMIT = "6c29395a9c14766eb04a9a27746f681e2eb584c7"
QUADWILD_IDS = frozenset((44503, 128001, 58012, 61394, 67792, 69975,
                          81877, 94884, 230923, 364256, 423069, 498974))
BADIA_TRIANGLES = {
    252119: 49950, 293137: 292, 35269: 40246, 37266: 29472,
    37881: 3400, 441708: 112402, 47076: 1532, 550964: 6156,
    551021: 348128, 65904: 157726, 96457: 1634,
}
ALL_IDS = QUADWILD_IDS | BADIA_TRIANGLES.keys()
REQUIRED_CATALOG_FIELDS = (
    "id", "thing_id", "name", "license", "format", "faces", "vertices",
    "closed", "edge_manifold", "vertex_manifold", "single_component",
    "pwn", "degenerate_faces", "duplicated_faces",
)
BOOLEAN_FIELDS = (
    "closed", "edge_manifold", "vertex_manifold", "single_component",
    "pwn", "degenerate_faces", "duplicated_faces",
)


def git_blob_sha1(raw: bytes) -> str:
    """Hash actual Git blob bytes, never a raw-file SHA-1 impersonating Git."""
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def license_review_gate(license_label: str) -> str:
    """Conservative metadata-only legal triage; never grants redistribution."""
    normalized = license_label.casefold()
    if "no derivatives" in normalized or "no-derivatives" in normalized:
        return "REVIEW_NODERIVATIVES_BEFORE_RECONSTRUCTION_OR_PUBLICATION"
    if "non-commercial" in normalized or "noncommercial" in normalized:
        return "REVIEW_NONCOMMERCIAL_RESTRICTIONS"
    if "gnu" in normalized or "gpl" in normalized:
        return "REVIEW_GPL_OBLIGATIONS"
    if "share alike" in normalized or "share-alike" in normalized:
        return "REVIEW_SHAREALIKE_OBLIGATIONS"
    return "DECLARED_ATTRIBUTION_LICENSE_INDEPENDENT_REVIEW_PENDING"


def catalog_screen_pass(m: dict) -> bool:
    """Screen metadata flags only; no assumption of geometric soundness."""
    return (all(m[k] is True for k in ("closed", "edge_manifold",
                "vertex_manifold", "single_component", "pwn"))
            and all(m[k] is False for k in ("degenerate_faces", "duplicated_faces")))


def audit_cohort(catalog_bytes: bytes, cohort_csv_bytes: bytes,
                 *, expected_blob_sha1: str = PINNED_CATALOG_BLOB_SHA1) -> dict:
    """Require all 23 independently named inputs and the pinned catalog bytes."""
    if len(catalog_bytes) > 8_000_000:
        raise ValueError("Catalog exceeds the conservative size bound")
    actual_blob = git_blob_sha1(catalog_bytes)
    if actual_blob != expected_blob_sha1:
        raise ValueError("Catalog Git blob differs from frozen metadata evidence")
    source = json.loads(catalog_bytes.decode("utf-8"))
    if not isinstance(source, list):
        raise ValueError("Expected an array of source model metadata")
    matching = {}
    for entry in source:
        if not isinstance(entry, dict) or "id" not in entry:
            raise ValueError("Malformed source catalog record")
        model_id = entry["id"]
        if type(model_id) is not int:
            raise ValueError("Nonintegral source file id")
        if model_id not in ALL_IDS:
            continue
        if model_id in matching:
            raise ValueError("Repeated source file id")
        for field in REQUIRED_CATALOG_FIELDS:
            if field not in entry:
                raise ValueError(f"Missing source catalog field: {field}")
        if any(type(entry[k]) is not bool for k in BOOLEAN_FIELDS):
            raise ValueError("Non-boolean topology declaration")
        if (type(entry["faces"]) is not int or entry["faces"] <= 0
                or type(entry["vertices"]) is not int or entry["vertices"] <= 0
                or type(entry["thing_id"]) is not int or entry["thing_id"] <= 0
                or not isinstance(entry["license"], str)
                or not entry["license"].strip()
                or not isinstance(entry["name"], str)
                or not entry["name"].strip()
                or not isinstance(entry["format"], str)
                or entry["format"].lower() != "stl"):
            raise ValueError("Invalid catalog model fields")
        matching[model_id] = entry
    if set(matching) != set(ALL_IDS):
        raise ValueError("Not all 23 literature model IDs occur in source catalog")

    reader = csv.DictReader(io.StringIO(cohort_csv_bytes.decode("utf-8-sig")))
    required = ("thingi10k_file_id", "literature_cohort", "published_stl_triangles",
                "individual_license_status", "source_mesh_hash_status",
                "quad_result_pair_status", "apmesh_pipeline_status")
    if not reader.fieldnames or any(k not in reader.fieldnames for k in required):
        raise ValueError("Missing cohort manifest columns")
    cohort = list(reader)
    model_ids = [int(row["thingi10k_file_id"]) for row in cohort]
    if len(cohort) != 23 or set(model_ids) != set(ALL_IDS):
        raise ValueError("Literature cohort must have exactly 23 unique frozen model IDs")
    if len(set(model_ids)) != len(model_ids):
        raise ValueError("Duplicate literature model ID")

    joined = []
    for row in cohort:
        mid = int(row["thingi10k_file_id"])
        m = matching[mid]
        expected_cohort = "QUADWILD_FIG29" if mid in QUADWILD_IDS else "BADIA_FIG10_TABLE1"
        if row["literature_cohort"] != expected_cohort:
            raise ValueError(f"Literature cohort mismatch for {mid}")
        if mid in BADIA_TRIANGLES:
            if int(row["published_stl_triangles"]) != BADIA_TRIANGLES[mid]:
                raise ValueError(f"Published Badia triangle count differs for {mid}")
            if m["faces"] != BADIA_TRIANGLES[mid]:
                raise ValueError(f"Badia source metadata triangle count mismatch for {mid}")
        if (row["individual_license_status"] != "PER_ASSET_NOT_REVIEWED"
                or row["source_mesh_hash_status"] != "NOT_RETRIEVED"
                or row["quad_result_pair_status"] != "ARCHIVE_EXISTS_ID_PAIR_NOT_VERIFIED"
                or row["apmesh_pipeline_status"] != "NOT_RUN"):
            raise ValueError("A metadata-only run cannot promote unexecuted gates")
        clean = catalog_screen_pass(m)
        joined.append({
            "file_id": mid,
            "thing_id": m["thing_id"],
            "name": m["name"],
            "license_declaration": m["license"],
            "license_review_gate": license_review_gate(m["license"]),
            "source_faces_catalog": m["faces"],
            "source_vertices_catalog": m["vertices"],
            "source_format_catalog": m["format"],
            "source_topology_flags_catalog": {k: m[k] for k in BOOLEAN_FIELDS},
            "catalog_topology_clean_screen": clean,
            "literature_cohort": expected_cohort,
            "published_badia_input_triangles_match_catalog": (
                True if mid in BADIA_TRIANGLES else None),
            "source_mesh_bytes_validated": False,
            "individual_license_independently_verified": False,
            "quad_output_pair_verified": False,
            "apmesh_run_executed": False,
        })
    result = {
        "schema": "apmesh-thingi10k-literature-metadata-audit-v1",
        "status": "METADATA_CATALOG_AUDITED_NO_SOURCE_OR_QUAD_ADMISSION",
        "catalog_git_blob_sha1": actual_blob,
        "catalog_git_commit": PINNED_CATALOG_COMMIT,
        "cohort_size": len(joined),
        "quadwild_count": len(QUADWILD_IDS),
        "badia_count": len(BADIA_TRIANGLES),
        "quadwild_clean_catalog_flag_count": sum(x["catalog_topology_clean_screen"] for x in joined if x["literature_cohort"] == "QUADWILD_FIG29"),
        "badia_clean_catalog_flag_count": sum(x["catalog_topology_clean_screen"] for x in joined if x["literature_cohort"] == "BADIA_FIG10_TABLE1"),
        "license_declarations": dict(sorted(Counter(x["license_declaration"] for x in joined).items())),
        "models": joined,
        "all_source_mesh_bytes_validated": False,
        "any_quad_result_pair_verified": False,
        "any_apmesh_quad_executed": False,
        "new_model_admissions": 0,
    }
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-json", type=Path, required=True)
    parser.add_argument("--cohort-csv", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)
    if os.path.lexists(args.receipt):
        parser.error("Receipt path must not exist; no overwrite")
    receipt = audit_cohort(args.catalog_json.read_bytes(), args.cohort_csv.read_bytes())
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    with args.receipt.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, sort_keys=True, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({k: receipt[k] for k in (
        "status", "cohort_size", "quadwild_count", "badia_count",
        "quadwild_clean_catalog_flag_count", "badia_clean_catalog_flag_count",
        "new_model_admissions")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
