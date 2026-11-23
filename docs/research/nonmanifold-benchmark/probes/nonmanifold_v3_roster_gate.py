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
}

NONMANIFOLD_PROVENANCE = {
    "N1_AUTHORED": "authored",
    "N1_DERIVED_AUTHORED": "authored",
    "N2_DERIVED_EXTERNAL": "derived",
    "N3_ORIGINAL_EXTERNAL": "unverified",
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
        if not model or model in indexed or any(value is None or not value.strip() for value in row.values()):
            raise ValueError(f"Invalid, incomplete, or duplicate model row: {model}")
        indexed[model] = row

        kind = row["origin_class"]
        proven = row["original_source_edge_incidence_ge3"]
        incident = int(row["verified_multisheet_incidence"])
        if incident < 0:
            raise ValueError("Negative source incidence")

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

    if not REQUIRED_MODELS.issubset(indexed):
        raise ValueError(f"Missing compulsory tracked models: {sorted(REQUIRED_MODELS - indexed.keys())}")

    curved = indexed["FOUR_SHEET_CURVED"]
    if curved["verified_multisheet_incidence"] != "4" or curved["native_apmesh_tri_state"] != "NOT_RUN":
        raise ValueError("Four-Sheet Curved native-TRI milestone overclaimed")
    tsh = indexed["TSH249_POST_SEWING"]
    if tsh["origin_class"] != "N2_DERIVED_EXTERNAL" or tsh["bezier_atlas_state"] != "NOT_COMPLETE":
        raise ValueError("Tsh249 derived-source or atlas-completeness claim overpromoted")
    s40 = indexed["S40"]
    if s40["bezier_atlas_state"] != "PARTIAL_22_OF_43":
        raise ValueError("S40 partial original CAD atlas falsely declared complete")
    thing = indexed["THINGI10K_293137"]
    if thing["native_apmesh_tri_state"] != "ACCEPTED_TRI_3504":
        raise ValueError("Historical original native TRI receipt no longer matches roster")

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
