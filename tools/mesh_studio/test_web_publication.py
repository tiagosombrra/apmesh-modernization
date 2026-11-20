"""Web publication exports must be original source-bound pure 2D vector figures."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from fastapi.testclient import TestClient

from . import web_api
from .svg_figure import URI


class OriginalWebVectorPublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(web_api.app)

    def _audit(self, model: str, expected_status: str) -> None:
        response = self.client.get(f"/api/v1/models/{model}/publication.svg")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "image/svg+xml")
        self.assertEqual(response.headers["x-source-sha256"],
                         web_api.CATALOG[model][2])
        self.assertEqual(response.headers["x-source-status"], expected_status)
        self.assertEqual(sha256(response.content).hexdigest(),
                         response.headers["x-vector-figure-sha256"])
        self.assertIn("attachment; filename=", response.headers["content-disposition"])
        self.assertIn(web_api.CATALOG[model][2][:12],
                      response.headers["content-disposition"])
        root = ET.fromstring(response.content)
        self.assertEqual(root.tag, f"{{{URI}}}svg")
        self.assertEqual(root.attrib["width"], "155mm")
        self.assertEqual(root.attrib["height"], "120mm")
        forbidden = {"image", "script", "foreignObject", "filter", "use", "feImage"}
        names = [node.tag.rsplit("}", 1)[-1] for node in root.iter()]
        self.assertFalse(set(names) & forbidden)
        for node in root.iter():
            for key, val in node.attrib.items():
                self.assertFalse(key.endswith("href") or key.startswith("on") or
                                 "url(" in val)
        self.assertEqual(names.count("polygon"),
                         web_api.load_document(model).triangles +
                         web_api.load_document(model).quads)
        metadata = root.find(f"{{{URI}}}metadata")
        self.assertIsNotNone(metadata)
        source = json.loads(metadata.text or "")
        self.assertEqual(source["source_sha256"], web_api.CATALOG[model][2])
        self.assertEqual(source["source_status"], expected_status)
        self.assertEqual(source["accepted_adaptive_epochs"], 0)
        self.assertFalse(source["scientific_lod_qualified"])
        self.assertFalse(source["source_surface_continuously_certified"])
        self.assertEqual(source["render_class"], "source_uv_vector_2d")

        again = self.client.get(f"/api/v1/models/{model}/publication.svg")
        self.assertEqual(response.content, again.content)

    def test_original_controlled_p1_is_vector_only_and_provenance_bound(self):
        self._audit("p1", "CONTROLLED_PHYSICAL_GENERATION")

    def test_staged_band_is_clearly_labeled_unaccepted(self):
        self._audit("band", "STAGED_UNACCEPTED")
        r = self.client.get("/api/v1/models/band/publication.svg")
        self.assertIn(b"NOT AN ACCEPTED ADAPTIVE EPOCH", r.content)

    def test_unknown_model_cannot_control_output_filename_or_read_path(self):
        for model in ("../../../../secret", "missing", "test.svg"):
            with self.subTest(model=model):
                r = self.client.get(
                    f"/api/v1/models/{model}/publication.svg")
                self.assertIn(r.status_code, (404, 422))

    def test_changed_pinned_model_cannot_export_stale_cached_figure(self):
        original = (Path(web_api.__file__).resolve().parent /
                    "fixtures/real_p1/accepted.obj")
        with tempfile.TemporaryDirectory(prefix="apmesh-v5-uv-") as temporary:
            root = Path(temporary)
            path = root / "real_p1/accepted.obj"
            path.parent.mkdir(parents=True)
            shutil.copyfile(original, path)
            with patch.object(web_api, "ROOT", root):
                valid = self.client.get("/api/v1/models/p1/publication.svg")
                self.assertEqual(valid.status_code, 200)
                path.write_bytes(path.read_bytes() + b"\n# changed model\n")
                invalid = self.client.get("/api/v1/models/p1/publication.svg")
                self.assertEqual(invalid.status_code, 409)
                self.assertEqual(invalid.json()["detail"], "source_sha_mismatch")


if __name__ == "__main__":
    unittest.main()
