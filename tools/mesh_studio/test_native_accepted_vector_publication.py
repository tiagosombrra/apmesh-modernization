"""Synthetic-only adversarial contracts for true original-native vector publisher.

The real original source qualification occurs separately in the native C++
CI job. Synthetic fixtures here cannot certify Eistute, Book or physical LOD.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from tools.mesh_studio.native_accepted_scene import project_accepted_faces
from tools.mesh_studio.native_accepted_vector_publication import (
    _load_verified_scene, _tag, _qualified_sample_markers,
    render_source_accepted_uv_svg, verify_svg_original_face_identity,
)
from tools.mesh_studio.test_verify_native_lineage import synthetic_receipt
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


def native_synthetic_vector_fixture(model: str = "eistute") -> tuple[dict, dict]:
    scene = project_accepted_faces(synthetic_receipt(model), model, "a" * 64)
    for face in scene["native_faces"]:
        # Deliberately rebuild each synthetic UV triangle as nondegenerate.
        for node, (u,v) in zip(face[4], ((0.0,0.0),(1.0,0.0),(0.0,1.0))):
            node[4:] = [u,v]
    patches = scene["native_source_patches"]
    groups = []
    for ordinal in range(2):
        members = []
        for face in scene["native_faces"]:
            patch = face[0]
            node = face[4][ordinal]
            members.append({
                "patch_slot": patch, "native_node_id": node[0],
                "original_xyz": node[1:4], "canonical_t": float(ordinal),
            })
        groups.append({
            "ordinal": ordinal, "canonical_t": float(ordinal),
            "members": members,
        })
    source = {
        "model": model, "accepted_native_step": 1,
        "source_ndjson_sha256": "a"*64,
        "original_model_input_sha256": "b"*64,
        "original_config_sha256": "c"*64,
        "source_patch_count": patches,
        "source_curve_count": scene["native_source_curves"],
        "scientific_lod_qualified": False,
        "physical_node_welding_certified": False,
        "cross_epoch_lineage_certified": False,
        "qualified_shared_source_curves": [{
            "source_curve_slot": 3, "patch_slots": list(range(patches)),
            "sample_count": 2, "sample_groups": groups,
            "physical_node_welding_certified": False,
        }],
    }
    return scene, source


class NativeAcceptedPublicationSyntheticContracts(unittest.TestCase):
    def test_two_model_shape_controls_preserve_all_original_tri_keys(self):
        for model, patches in (("eistute", 4), ("book", 28)):
            with self.subTest(model=model):
                scene, source = native_synthetic_vector_fixture(model)
                svg, audit = render_source_accepted_uv_svg(scene, source)
                self.assertTrue(svg.startswith(b"<?xml"))
                self.assertEqual(audit["original_native_tri_faces"], patches)
                self.assertEqual(audit["observed_source_curve_sample_marker_count"],
                                 patches*2)
                self.assertEqual(audit["original_source_patch_count"], patches)
                self.assertFalse(audit["scientific_lod_qualified"])
                root = ET.fromstring(svg)
                self.assertEqual(len(root.findall(f".//{_tag('polygon')}")), patches)
                self.assertEqual(len(root.findall(f".//{_tag('circle')}")), patches*2)
                self.assertEqual(audit["svg_sha256"], sha256(svg).hexdigest())
                self.assertIsNone(verify_svg_original_face_identity(svg, scene, audit))
                same_svg, same_report = render_source_accepted_uv_svg(scene, source)
                self.assertEqual(svg, same_svg)
                self.assertEqual(audit, same_report)

    def test_repeated_native_node_id_in_same_patch_with_disagreeing_uv_fails(self):
        scene, source = native_synthetic_vector_fixture()
        # Force another original corner to reuse the ID but not its coordinates.
        scene["native_faces"][0][4][1][0] = scene["native_faces"][0][4][0][0]
        with self.assertRaisesRegex(
                NativeLineageValidationError, "v52_native_same_patch_node"):
            render_source_accepted_uv_svg(scene, source)

    def test_forged_scientific_lod_and_source_sha_are_rejected(self):
        scene, source = native_synthetic_vector_fixture()
        for role in ("scene", "source"):
            with self.subTest(role=role):
                s, i = deepcopy(scene), deepcopy(source)
                (s if role == "scene" else i)["scientific_lod_qualified"] = True
                with self.assertRaises(NativeLineageValidationError):
                    render_source_accepted_uv_svg(s, i)
        source["source_ndjson_sha256"] = "f"*64
        with self.assertRaises(NativeLineageValidationError):
            render_source_accepted_uv_svg(scene, source)

    def test_missing_source_curve_sample_native_corner_fails_closed(self):
        scene, source = native_synthetic_vector_fixture()
        source["qualified_shared_source_curves"][0]["sample_groups"][0][
            "members"][0]["native_node_id"] = 999_000
        with self.assertRaisesRegex(
                NativeLineageValidationError, "v52_source_curve_sample_missing"):
            render_source_accepted_uv_svg(scene, source)

    def test_wrong_source_curve_xyz_not_even_a_marker(self):
        scene, source = native_synthetic_vector_fixture()
        source["qualified_shared_source_curves"][0]["sample_groups"][0][
            "members"][0]["original_xyz"] = [999, 999, 999]
        with self.assertRaisesRegex(
                NativeLineageValidationError, "v52_shared_curve_sample_forged"):
            render_source_accepted_uv_svg(scene, source)

    def test_duplicate_original_patch_element_key_fails(self):
        scene, source = native_synthetic_vector_fixture()
        clone = deepcopy(scene["native_faces"][0])
        scene["native_faces"].insert(1, clone)
        scene["native_tri_faces"] += 1
        scene["source_patch_face_counts"][0] += 1
        with self.assertRaisesRegex(
                NativeLineageValidationError, "v52_native_patch_face_key"):
            render_source_accepted_uv_svg(scene, source)

    def test_degenerate_or_out_of_source_uv_bounds_fails(self):
        for mode in ("degenerate", "outbound", "nan"):
            with self.subTest(mode=mode):
                scene, source = native_synthetic_vector_fixture()
                corner = scene["native_faces"][0][4][2]
                corner[4:] = ([0.5, 0.0] if mode == "degenerate" else
                              [2.0, 0.5] if mode == "outbound" else
                              [float("nan"), 0.0])
                with self.assertRaises(NativeLineageValidationError):
                    render_source_accepted_uv_svg(scene, source)

    def test_xml_svg_doctype_raster_and_active_external_refs_refused(self):
        scene, source = native_synthetic_vector_fixture()
        svg, original = render_source_accepted_uv_svg(scene, source)
        for poisoned in (
            svg.replace(b"<?xml", b"<!DOCTYPE x><?xml", 1),
            svg.replace(b"</svg>", b"<image href='https://bad.example/x'/></svg>"),
            svg.replace(b"</svg>", b"<script>bad()</script></svg>"),
        ):
            with self.subTest(poison=poisoned[:35]):
                record = dict(original, svg_sha256=sha256(poisoned).hexdigest())
                with self.assertRaises((ValueError, NativeLineageValidationError,
                                        ET.ParseError, KeyError)):
                    verify_svg_original_face_identity(poisoned, scene, record)

    def test_missing_svg_triangle_rejected_even_with_updated_digest(self):
        scene, source = native_synthetic_vector_fixture()
        svg, manifest = render_source_accepted_uv_svg(scene, source)
        root = ET.fromstring(svg)
        panel = root.find(f".//{_tag('g')}")
        self.assertIsNotNone(panel)
        tri = panel.find(_tag("polygon"))
        self.assertIsNotNone(tri)
        panel.remove(tri)
        altered = ET.tostring(root, encoding="utf-8")
        with self.assertRaisesRegex(
                NativeLineageValidationError, "v52_original_svg_face_patch"):
            verify_svg_original_face_identity(
                altered, scene, dict(manifest, svg_sha256=sha256(altered).hexdigest()))

    def test_standalone_visual_json_does_not_self_attest_source_cpp(self):
        scene, source = native_synthetic_vector_fixture()
        record = {
            "scenes": [scene], "identity": {"documents": [source]},
            "claim": "real native C++ source",
        }
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "fake-r2720.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            with patch(
                "tools.mesh_studio.native_accepted_vector_publication.generate_original_scene_bundle",
                return_value={"scenes": []},
            ):
                with self.assertRaisesRegex(
                        NativeLineageValidationError,
                        "v52_visual_sidecar_not_same_original_source"):
                    _load_verified_scene(Path(name), path)


if __name__ == "__main__":
    unittest.main()
