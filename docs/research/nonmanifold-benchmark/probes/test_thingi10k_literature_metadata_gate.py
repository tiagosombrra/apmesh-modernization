"""Hermetic adversarial tests with synthetic third-party catalog records."""
from __future__ import annotations

import csv
import io
import json
import unittest

from thingi10k_literature_metadata_gate import (
    ALL_IDS,
    BADIA_TRIANGLES,
    QUADWILD_IDS,
    audit_cohort,
    catalog_screen_pass,
    git_blob_sha1,
    license_review_gate,
)


def fixtures():
    """Create complete toy inputs with 23 unique literature IDs."""
    models = []
    for mid in sorted(ALL_IDS):
        models.append({
            "id": mid, "thing_id": mid + 1, "name": f"Synthetic-{mid}",
            "format": "stl", "license": "Creative Commons - Attribution",
            "faces": BADIA_TRIANGLES.get(mid, 42), "vertices": 22,
            "closed": True, "edge_manifold": True, "vertex_manifold": True,
            "single_component": True, "pwn": True, "degenerate_faces": False,
            "duplicated_faces": False,
        })
    fieldnames = ["thingi10k_file_id", "literature_cohort", "published_stl_triangles",
                  "individual_license_status", "source_mesh_hash_status",
                  "quad_result_pair_status", "apmesh_pipeline_status"]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    for mid in sorted(ALL_IDS):
        writer.writerow({
            "thingi10k_file_id": mid,
            "literature_cohort": "QUADWILD_FIG29" if mid in QUADWILD_IDS else "BADIA_FIG10_TABLE1",
            "published_stl_triangles": BADIA_TRIANGLES.get(mid, ""),
            "individual_license_status": "PER_ASSET_NOT_REVIEWED",
            "source_mesh_hash_status": "NOT_RETRIEVED",
            "quad_result_pair_status": "ARCHIVE_EXISTS_ID_PAIR_NOT_VERIFIED",
            "apmesh_pipeline_status": "NOT_RUN",
        })
    return models, stream.getvalue()


def execute(models, manifest, *, pinned=True):
    raw = json.dumps(models, sort_keys=True).encode()
    actual = git_blob_sha1(raw)
    return audit_cohort(raw, manifest.encode(), expected_blob_sha1=actual if pinned else "0" * 40)


class LiteratureMetadataGateTests(unittest.TestCase):
    def test_all_23_cohort_rows_validate_without_source_admission(self):
        m, c = fixtures()
        r = execute(m, c)
        self.assertEqual(r["cohort_size"], 23)
        self.assertEqual((r["quadwild_count"], r["badia_count"]), (12, 11))
        self.assertEqual(r["new_model_admissions"], 0)
        self.assertFalse(r["any_quad_result_pair_verified"])

    def test_pinned_catalog_blob_mismatch_rejected(self):
        m, c = fixtures()
        with self.assertRaisesRegex(ValueError, "blob differs"):
            execute(m, c, pinned=False)

    def test_missing_catalog_id_rejected(self):
        m, c = fixtures()
        with self.assertRaisesRegex(ValueError, "Not all 23"):
            execute(m[:-1], c)

    def test_duplicate_catalog_id_rejected(self):
        m, c = fixtures()
        with self.assertRaisesRegex(ValueError, "Repeated source file id"):
            execute(m + [m[0]], c)

    def test_bad_badia_triangle_count_rejected(self):
        m, c = fixtures()
        next(x for x in m if x["id"] == 293137)["faces"] = 293
        with self.assertRaisesRegex(ValueError, "metadata triangle count mismatch"):
            execute(m, c)

    def test_bad_published_triangle_count_rejected(self):
        m, c = fixtures()
        c = c.replace("293137,BADIA_FIG10_TABLE1,292", "293137,BADIA_FIG10_TABLE1,290")
        with self.assertRaisesRegex(ValueError, "Published Badia"):
            execute(m, c)

    def test_duplicate_manifest_row_rejected(self):
        m, c = fixtures()
        c = c + c.splitlines()[1] + "\n"
        with self.assertRaisesRegex(ValueError, "exactly 23"):
            execute(m, c)

    def test_false_admission_is_rejected(self):
        m, c = fixtures()
        c = c.replace("NOT_RUN", "PASS", 1)
        with self.assertRaisesRegex(ValueError, "cannot promote"):
            execute(m, c)

    def test_non_boolean_topology_declaration_rejected(self):
        m, c = fixtures()
        m[0]["closed"] = "true"
        with self.assertRaisesRegex(ValueError, "Non-boolean"):
            execute(m, c)

    def test_no_derivatives_is_legal_block(self):
        self.assertIn("NODERIVATIVES", license_review_gate("Creative Commons - Attribution - No Derivatives"))

    def test_noncommercial_is_legal_review(self):
        self.assertIn("NONCOMMERCIAL", license_review_gate("Attribution - Non-Commercial - Share Alike"))

    def test_sharealike_is_legal_review(self):
        self.assertIn("SHAREALIKE", license_review_gate("Creative Commons - Attribution - Share Alike"))

    def test_gpl_is_legal_review(self):
        self.assertIn("GPL", license_review_gate("GNU - GPL"))

    def test_declared_permissive_license_still_requires_review(self):
        self.assertIn("REVIEW_PENDING", license_review_gate("Creative Commons - Attribution"))

    def test_vertex_nonmanifold_rejected_as_clean(self):
        m, _ = fixtures()
        m[0]["vertex_manifold"] = False
        self.assertFalse(catalog_screen_pass(m[0]))

    def test_degenerate_or_duplicated_faces_rejected_as_clean(self):
        m, _ = fixtures()
        m[0]["degenerate_faces"] = True
        self.assertFalse(catalog_screen_pass(m[0]))
        m[0]["degenerate_faces"] = False
        m[0]["duplicated_faces"] = True
        self.assertFalse(catalog_screen_pass(m[0]))

    def test_open_or_multi_component_rejected_as_clean(self):
        m, _ = fixtures()
        m[0]["closed"] = False
        self.assertFalse(catalog_screen_pass(m[0]))
        m[0]["closed"] = True
        m[0]["single_component"] = False
        self.assertFalse(catalog_screen_pass(m[0]))


if __name__ == "__main__":
    unittest.main()
