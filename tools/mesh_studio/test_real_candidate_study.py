"""Adversarial and analytic S5d tests for source-bound candidate comparisons."""

from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from .real_candidate_study import (
    ORDER, STAGED, OBJ_HASHES, StudyIntegrityError, _dominates,
    _geometry_checks, _inverse_quad, _pareto_profiles, _triangle_weights,
    _uniform_sample_metrics, qualify_real_study, write_real_study_report,
)
from .real_study_publication import export_real_candidate_bundle
from .import_obj import import_obj

FIXTURES=Path(__file__).parent/"fixtures"/"real_p2d1c3"


class RealStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=qualify_real_study(FIXTURES)
        cls.real=cls.result["physical_candidates"]

    def test_real_original_and_four_candidate_sources(self):
        self.assertEqual(list(self.real),list(ORDER))
        self.assertEqual(len(self.real),5)

    def test_sha256_each_real_obj(self):
        for name,digest in OBJ_HASHES.items():
            with self.subTest(mesh=name):
                self.assertEqual(sha256((FIXTURES/(name+".obj")).read_bytes()).hexdigest(),digest)

    def test_staged_are_not_accepted_epochs(self):
        self.assertEqual(self.real["control"]["state"],"controlled_nonadaptive_output")
        self.assertTrue(all(self.real[name]["state"]=="staged_unaccepted" for name in STAGED))
        self.assertEqual(self.result["scientific_status"]["accepted_adaptive_epochs"],0)

    def test_real_mesh_type_inventory(self):
        expected={"control":(69,42,36),"band":(93,62,44),"west":(109,75,50),
                  "north":(107,71,54),"both":(117,82,52)}
        for name,counts in expected.items():
            g=self.real[name]["geometry"]
            self.assertEqual((g["nodes"],g["quads"],g["triangles"]),counts)
            self.assertEqual(g["elements"],g["quads"]+g["triangles"])

    def test_same_source_4096_midpoints(self):
        for name in ORDER:
            e=self.real[name]["same_site_error"]
            self.assertEqual(e["sample_count"],4096)
            self.assertEqual(e["quad_sites"]+e["tri_sites"],4096)

    def test_reference_same_site_errors(self):
        expected={"control":.015981265663966727,"band":.011810324643012932,
                  "west":.009960083459157833,"north":.00923331923514389,
                  "both":.009155128673187646}
        for name,value in expected.items():
            with self.subTest(name=name):
                self.assertAlmostEqual(self.real[name]["same_site_error"]["rms_source_area"],value,12)

    def test_real_quad_coverage_is_area_not_quad_count(self):
        expected={"control":.25,"band":.328125,"west":.375,
                  "north":.375,"both":.40625}
        for name,area in expected.items():
            self.assertAlmostEqual(self.real[name]["geometry"]["quad_uv_area"],area,12)
        self.assertNotEqual(self.real["west"]["geometry"]["quads"],
                            self.real["north"]["geometry"]["quads"])

    def test_pareto_uv_area_north_dominates_west(self):
        p=self.result["pareto_evidence"]["profiles"]["uv_area_profile"]
        self.assertEqual(p["nondominated"],["band","both","north"])
        self.assertEqual(p["dominated_by"]["west"],["north"])

    def test_pareto_quad_count_changes_front(self):
        p=self.result["pareto_evidence"]["profiles"]["quad_count_profile"]
        self.assertEqual(p["nondominated"],["band","both","north","west"])
        self.assertEqual(p["dominated_by"]["west"],[])
        self.assertIn("quads",p["objectives"])

    def test_source_original_not_in_staged_pareto(self):
        p=self.result["pareto_evidence"]["profiles"]
        for profile in p.values():
            self.assertNotIn("control",profile["nondominated"])

    def test_source_fixed_boundary_and_indexed_disk(self):
        for name in ORDER:
            g=self.real[name]["geometry"]
            self.assertEqual(g["boundary_edges"],16)
            self.assertEqual(g["indexed_euler_characteristic"],1)
            self.assertGreater(g["quad_tri_seam_edges"],0)

    def test_no_cross_method_anisotropy_or_all_quad(self):
        self.assertFalse(self.result["scientific_status"]["real_all_quad_generator_certified"])
        self.assertFalse(self.result["scientific_status"]["real_anisotropic_generator_certified"])

    def test_one_controlled_run_not_five_independent_replications(self):
        self.assertTrue(self.result["scientific_status"]["not_a_statistical_multi_run_comparison"])
        self.assertEqual(self.result["provenance"]["original_actions_run"],43664129060)

    def test_missing_source_report_is_rejected(self):
        with tempfile.TemporaryDirectory() as dirname:
            path=Path(dirname)
            for name in ORDER:shutil.copyfile(FIXTURES/(name+".obj"),path/(name+".obj"))
            with self.assertRaisesRegex(StudyIntegrityError,"missing_or_large_original_report"):
                qualify_real_study(path)

    def test_forged_report_sha_is_rejected(self):
        with tempfile.TemporaryDirectory() as dirname:
            path=Path(dirname)
            shutil.copytree(FIXTURES,path,dirs_exist_ok=True)
            file=path/"generator_report.json"
            file.write_text(file.read_text()+" ",encoding="utf-8")
            with self.assertRaisesRegex(StudyIntegrityError,"original_generator_report_sha_mismatch"):
                qualify_real_study(path)

    def test_mutated_obj_sha_is_rejected(self):
        with tempfile.TemporaryDirectory() as dirname:
            path=Path(dirname)
            shutil.copytree(FIXTURES,path,dirs_exist_ok=True)
            file=path/"west.obj"
            file.write_text(file.read_text()+"# mutated\n",encoding="utf-8")
            with self.assertRaisesRegex(StudyIntegrityError,"source_candidate_sha_mismatch_west"):
                qualify_real_study(path)

    def test_forged_digest_does_not_bypass_bezier_oracle(self):
        with tempfile.TemporaryDirectory() as dirname:
            path=Path(dirname)
            shutil.copytree(FIXTURES,path,dirs_exist_ok=True)
            file=path/"control.obj"
            lines=file.read_text().splitlines()
            for i,line in enumerate(lines):
                if line.startswith("v "):
                    tokens=line.split()
                    tokens[1]=str(float(tokens[1])+0.004)
                    lines[i]=" ".join(tokens)
                    break
            file.write_text("\n".join(lines)+"\n",encoding="utf-8")
            fakehash=sha256(file.read_bytes()).hexdigest()
            report_path=path/"generator_report.json"
            forged_report=json.loads(report_path.read_text())
            forged_report["OBJ_sha256"]=fakehash
            report_path.write_text(json.dumps(forged_report),encoding="utf-8")
            report_hash=sha256(report_path.read_bytes()).hexdigest()
            with patch.dict(OBJ_HASHES,{"control":fakehash}):
                with patch("tools.mesh_studio.real_candidate_study.SOURCE_REPORT_SHA256",report_hash):
                    with self.assertRaisesRegex(StudyIntegrityError,"bezier_vertex_position_mismatch"):
                        qualify_real_study(path)

    def test_forged_source_report_metric_fails_recomputed_grid(self):
        with tempfile.TemporaryDirectory() as dirname:
            path=Path(dirname)
            shutil.copytree(FIXTURES,path,dirs_exist_ok=True)
            file=path/"generator_report.json"
            fake=json.loads(file.read_text())
            fake["same_site_source_error"]["fixed_64x64_original"]["rms_uv"]+=0.01
            file.write_text(json.dumps(fake),encoding="utf-8")
            dig=sha256(file.read_bytes()).hexdigest()
            with patch("tools.mesh_studio.real_candidate_study.SOURCE_REPORT_SHA256",dig):
                with self.assertRaisesRegex(StudyIntegrityError,"mismatched_control_rms_uv"):
                    qualify_real_study(path)

    def test_invalid_pareto_nan_rejected(self):
        records={name:{"nodes":105,"quads":60,"elements":120,
                       "rms_source_area":.01,"max_xyz":.02,"quad_uv_area":.4,
                       "min_scaled_jacobian":.56,"min_warpage_cosine":.99} for name in STAGED}
        records["west"]["rms_source_area"]=math.nan
        with self.assertRaisesRegex(StudyIntegrityError,"nonfinite_pareto_measurement"):
            _pareto_profiles(records)

    def test_invalid_pareto_missing_objective_rejected(self):
        records={name:{"nodes":105,"quads":60,"elements":120,
                       "rms_source_area":.01,"max_xyz":.02,"quad_uv_area":.4,
                       "min_scaled_jacobian":.56,"min_warpage_cosine":.99} for name in STAGED}
        del records["west"]["nodes"]
        with self.assertRaisesRegex(StudyIntegrityError,"invalid_pareto_objectives"):
            _pareto_profiles(records)

    def test_invalid_pareto_candidate_inventory_rejected(self):
        with self.assertRaisesRegex(StudyIntegrityError,"invalid_pareto_candidate_set"):
            _pareto_profiles({"north":{}})

    def test_pareto_identical_vectors_do_not_dominate(self):
        item={"max_xyz":.01,"rms_source_area":.02}
        self.assertFalse(_dominates(item,item,{"max_xyz":"min","rms_source_area":"min"}))

    def test_pareto_illegal_direction_rejected(self):
        with self.assertRaisesRegex(StudyIntegrityError,"invalid_pareto_direction"):
            _dominates({"max_xyz":1},{"max_xyz":2},{"max_xyz":"unknown"})

    def test_barycentric_and_bilinear_reference(self):
        self.assertEqual(_triangle_weights([(0,0),(1,0),(0,1)],.25,.25),(.5,.25,.25))
        weights=_inverse_quad([(0,0),(1,0),(1,1),(0,1)],.25,.75)
        self.assertAlmostEqual(sum(weights),1,12)
        self.assertTrue(all(w>0 for w in weights))

    def test_bilinear_nonconvergent_geometry_rejected(self):
        with self.assertRaises(StudyIntegrityError):
            _inverse_quad([(0,0),(1,0),(0,0),(0,1)],.5,.5)

    def test_grid_count_not_arbitrary_divisor(self):
        doc=import_obj(FIXTURES/"west.obj",auto_sidecar=False)
        _,uv=_geometry_checks(doc)
        with self.assertRaisesRegex(StudyIntegrityError,"unapproved_common_sample_grid"):
            _uniform_sample_metrics(doc,uv,32)

    def test_deterministic_source_qualification_json(self):
        with tempfile.TemporaryDirectory() as dirname:
            p=Path(dirname)
            a=write_real_study_report(FIXTURES,p/"a.json")
            b=write_real_study_report(FIXTURES,p/"b.json")
            self.assertEqual(a,b)
            self.assertEqual((p/"a.json").read_bytes(),(p/"b.json").read_bytes())

    def test_vector_bundle_and_latex_manifests(self):
        with tempfile.TemporaryDirectory() as dirname:
            p=Path(dirname)
            r=export_real_candidate_bundle(FIXTURES,p)
            self.assertTrue(r["vector_audits"]["real_candidate_gallery"]["pdf"]["vector_only_no_image_xobjects"])
            self.assertTrue(r["vector_audits"]["real_candidate_pareto"]["svg"]["vector_only"])
            self.assertEqual(r["observed_adaptive_epochs"],0)
            self.assertEqual((p/"candidate_metrics.csv").read_text().count("\n"),6)
            self.assertIn("figure*",(p/"include.tex").read_text())


if __name__=="__main__":
    unittest.main()
