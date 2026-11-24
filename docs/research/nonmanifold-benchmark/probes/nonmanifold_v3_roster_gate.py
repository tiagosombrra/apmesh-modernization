"""Fail-closed scientific role gate for the non-manifold-first model roster."""

import argparse
import csv
import json
from pathlib import Path


COLUMNS = (
    "model_id", "priority", "origin_class", "original_source_edge_incidence_ge3",
    "verified_multisheet_incidence", "source_geometry_state", "bezier_atlas_state",
    "native_apmesh_tri_state", "role", "principal_blocker",
)

REQUIRED_MODELS = {
    "FOUR_SHEET_CURVED", "TSH249_POST_SEWING", "ORIGINAL_EXTERNAL_MULTISHEET",
    "S40", "M5", "S27", "M3", "THINGI10K_293137",
    "BOOK", "EISTUTE", "DECOR_SHELF",
    "T_JUNCTION", "CROSS_JUNCTION", "FOUR_SHEET_PLANAR",
}

NONMANIFOLD_PROVENANCE = {
    "N1_AUTHORED": "authored",
    "N1_DERIVED_AUTHORED": "authored",
    "N2_DERIVED_EXTERNAL": "derived",
    "N3_ORIGINAL_EXTERNAL": "unverified",
}

# The v3 snapshot is frozen; changing a scientific role requires a new evidence review.
EXPECTED_CLASSIFICATION = {
    "FOUR_SHEET_CURVED": ("P0-1", "N1_AUTHORED", "PRIMARY_NONMANIFOLD_CONTROL", "authored", 4),
    "TSH249_POST_SEWING": ("P0-2", "N2_DERIVED_EXTERNAL", "EXTERNAL_DERIVED_POSITIVE", "derived", 3),
    "ORIGINAL_EXTERNAL_MULTISHEET": ("P1", "N3_ORIGINAL_EXTERNAL", "REQUIRED_EXTERNAL_ORIGINAL_POSITIVE", "unverified", 0),
    "T_JUNCTION": ("P1", "N1_DERIVED_AUTHORED", "SECONDARY_NONMANIFOLD_CONTROL", "authored", 3),
    "CROSS_JUNCTION": ("P1", "N1_DERIVED_AUTHORED", "SECONDARY_NONMANIFOLD_CONTROL", "authored", 3),
    "FOUR_SHEET_PLANAR": ("P1", "N1_AUTHORED", "SECONDARY_NONMANIFOLD_CONTROL", "authored", 4),
    **{model: ("P3", "MANIFOLD_EXTERNAL", "MANIFOLD_CAD_CONTROL", "no", 0)
       for model in ("S40", "M5", "S27", "M3")},
    "THINGI10K_293137": ("P4", "MANIFOLD_STL_DERIVED", "MANIFOLD_STL_CONTROL", "no", 0),
    **{model: ("REGRESSION", "HISTORICAL_AUTHORED", "HISTORICAL_BASELINE", "authored", count)
       for model, count in (("BOOK", 28), ("EISTUTE", 4), ("DECOR_SHELF", 3))},
}
EXPECTED_NATIVE_TRI = {
    "THINGI10K_293137": "ACCEPTED_TRI_3504",
    "BOOK": "ARCHIVED_ACCEPTED",
    "EISTUTE": "ARCHIVED_ACCEPTED",
    "DECOR_SHELF": "ARCHIVED_PARTIAL_TIMEOUT",
}
EXPECTED_ATLAS = {
    "FOUR_SHEET_CURVED": "COMPLETE_4_PATCHES",
    "FOUR_SHEET_PLANAR": "COMPLETE_4_PATCHES",
    "TSH249_POST_SEWING": "NOT_COMPLETE",
    "ORIGINAL_EXTERNAL_MULTISHEET": "NOT_STARTED",
    "T_JUNCTION": "BOUNDED_5_PATCHES",
    "CROSS_JUNCTION": "BOUNDED_10_PATCHES",
    "S40": "PARTIAL_22_OF_43",
    "M5": "PARTIAL_8_OF_41",
    "S27": "NOT_INTEGRATED",
    "M3": "NOT_INTEGRATED",
    "THINGI10K_293137": "COMPLETE_876_FLAT_DERIVED_PATCHES",
    **{model: "HISTORICAL_COMPLETE" for model in ("BOOK", "EISTUTE", "DECOR_SHELF")},
}
EXPECTED_SOURCE = {
    "FOUR_SHEET_CURVED": "AUTHORED_OCCT_VERIFIED",
    "FOUR_SHEET_PLANAR": "CONTROL_OCCT_VERIFIED",
    "TSH249_POST_SEWING": "ORIGINAL_STEP_PINNED_AND_SEWING_OCCT_VERIFIED",
    "ORIGINAL_EXTERNAL_MULTISHEET": "NOT_LOCATED",
    **{model: "CONTROL_NATIVE_BREP_VERIFIED" for model in ("T_JUNCTION", "CROSS_JUNCTION")},
    **{model: "ORIGINAL_STEP_VALIDATED" for model in ("S40", "M5", "S27", "M3")},
    "THINGI10K_293137": "SOURCE_STL_PINNED",
    **{model: "HISTORICAL_ARTICLE_SOURCE" for model in ("BOOK", "EISTUTE", "DECOR_SHELF")},
}


def validate_roster(path: Path) -> dict:
    """Reject unsupported claims and preserve model-specific evidence distinctions."""
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != COLUMNS:
            raise ValueError("Invalid model roster schema")
        rows = list(reader)

    indexed = {}
    for row in rows:
        model = row["model_id"]
        if (set(row) != set(COLUMNS) or not model or model in indexed
                or any(not isinstance(value, str) or not value.strip() for value in row.values())):
            raise ValueError(f"Invalid, incomplete, or duplicate model row: {model}")
        indexed[model] = row

        kind = row["origin_class"]
        proven = row["original_source_edge_incidence_ge3"]
        incident = int(row["verified_multisheet_incidence"])
        if incident < 0:
            raise ValueError("Negative source incidence")
        classification = (row["priority"], kind, row["role"], proven, incident)
        if classification != EXPECTED_CLASSIFICATION.get(model):
            raise ValueError(f"Unaudited model classification or priority: {model}")
        if row["native_apmesh_tri_state"] != EXPECTED_NATIVE_TRI.get(model, "NOT_RUN"):
            raise ValueError(f"Native TRI claim does not match v3 evidence: {model}")
        if row["bezier_atlas_state"] != EXPECTED_ATLAS[model]:
            raise ValueError(f"Atlas status does not match v3 evidence: {model}")
        if row["source_geometry_state"] != EXPECTED_SOURCE[model]:
            raise ValueError(f"Source status does not match v3 evidence: {model}")

        if kind.startswith("MANIFOLD_"):
            if proven != "no" or incident != 0 or "NONMANIFOLD" in row["role"]:
                raise ValueError(f"Manifold model wrongly promoted as non-manifold: {model}")
        if kind in NONMANIFOLD_PROVENANCE and proven != NONMANIFOLD_PROVENANCE[kind]:
            raise ValueError(f"Source-original versus derived provenance conflated: {model}")
        if kind == "N3_ORIGINAL_EXTERNAL":
            if incident != 0 or row["native_apmesh_tri_state"] != "NOT_RUN":
                raise ValueError("External source-original non-manifold model falsely admitted")
        if kind in {"N1_AUTHORED", "N1_DERIVED_AUTHORED", "N2_DERIVED_EXTERNAL"} and incident < 3:
            raise ValueError(f"Claimed multi-sheet model lacks 3+ verified incidences: {model}")
        if kind == "HISTORICAL_AUTHORED" and row["priority"] != "REGRESSION":
            raise ValueError("Old article model promoted as new research model")

    if set(indexed) != REQUIRED_MODELS:
        raise ValueError(f"Missing compulsory tracked models: {sorted(REQUIRED_MODELS - indexed.keys())}")

    return {
        "schema": "apmesh-nonmanifold-first-plan-v3",
        "models": len(indexed),
        "new_native_apmesh_tri_nonmanifold_qualified": 0,
        "external_original_nonmanifold_qualified": 0,
        "top_priority": "FOUR_SHEET_CURVED",
        "manifold_s40_admitted_as_positive": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate_roster(args.roster), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
