"""Source-hash-bound API cache performance and stale-input rejection contracts."""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from . import web_api


class VerifiedSourceCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        web_api._verified_document.cache_clear()
        web_api._verified_quality.cache_clear()
        self.client = TestClient(web_api.app)

    def tearDown(self) -> None:
        web_api._verified_document.cache_clear()
        web_api._verified_quality.cache_clear()

    def test_repeated_face_requests_reuse_one_original_quality_analysis(self):
        with patch.object(web_api, "analyze_mesh", wraps=web_api.analyze_mesh) as observed:
            for index in (0, 1, 0):
                result = self.client.get(f"/api/v1/models/p1/faces/{index}")
                self.assertEqual(result.status_code, 200)
                self.assertEqual(result.json()["quality"]["index"], index)
            report = self.client.get("/api/v1/models/p1/quality")
            self.assertEqual(report.status_code, 200)
            observed.assert_called_once()

    def test_source_document_is_parsed_once_for_two_views_and_quality(self):
        with patch.object(web_api, "import_obj", wraps=web_api.import_obj) as observed:
            for url in (
                "/api/v1/models/p1/geometry?space=xyz",
                "/api/v1/models/p1/geometry?space=uv",
                "/api/v1/models/p1/faces/0",
                "/api/v1/models/p1/quality",
            ):
                self.assertEqual(self.client.get(url).status_code, 200)
            observed.assert_called_once()

    def test_same_filename_changed_bytes_never_reuse_cached_source(self):
        source = (Path(web_api.__file__).resolve().parent /
                  "fixtures/real_p1/accepted.obj")
        with tempfile.TemporaryDirectory(prefix="apmesh-web-cache-") as tmp:
            root = Path(tmp)
            target = root / "real_p1/accepted.obj"
            target.parent.mkdir(parents=True)
            shutil.copyfile(source, target)
            with patch.object(web_api, "ROOT", root):
                verified = self.client.get("/api/v1/models/p1/faces/0")
                self.assertEqual(verified.status_code, 200)
                # Mutate the exact file without renaming it or clearing caches.
                target.write_bytes(target.read_bytes() + b"\n# altered after validation\n")
                response = self.client.get("/api/v1/models/p1/faces/0")
                self.assertEqual(response.status_code, 409)
                self.assertEqual(response.json()["detail"], "source_sha_mismatch")

    def test_mutated_api_report_cannot_poison_canonical_cached_metrics(self):
        original = self.client.get("/api/v1/models/p1/faces/0").json()
        public_report = web_api.quality("p1")
        public_report["cells"][0]["physical_area"] = -123.0
        again = self.client.get("/api/v1/models/p1/faces/0").json()
        self.assertEqual(
            original["quality"]["physical_area"],
            again["quality"]["physical_area"])
        self.assertNotEqual(again["quality"]["physical_area"], -123.0)

    def test_unknown_id_still_fails_closed(self):
        self.assertEqual(
            self.client.get("/api/v1/models/unknown/faces/0").status_code,
            404)


if __name__ == "__main__":
    unittest.main()
