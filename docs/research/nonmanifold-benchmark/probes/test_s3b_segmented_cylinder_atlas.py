"""Positive and negative controls for explicit derived-seam indexed BP atlases."""
import copy
import json
import unittest

from s3b_cylindrical_bicubic_pilot import synthetic_quarter_cylinder
from s3b_segmented_cylinder_atlas import construct, independent_audit


class SegmentedCylinderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=synthetic_quarter_cylinder()
        cls.results={}
        for count in (1,2,4,8):
            cls.results[count]=construct(cls.source,count,absolute_budget_mm=.01,
                                         relative_budget=.01,source_label='SYNTHETIC')

    def test_counts_and_derived_seams(self):
        for count,(bp,manifest) in self.results.items():
            with self.subTest(count=count):
                self.assertEqual(manifest['patch_count'],count)
                self.assertEqual(manifest['unique_control_vertices'],12*count+4)
                self.assertEqual(manifest['derived_shared_seams'],count-1)
                self.assertTrue(manifest['all_segments_meet_budget'])
                self.assertEqual(sum(x.startswith('p ') for x in bp.splitlines()),count)
                self.assertEqual(manifest['apmesh_generation'],'NOT_RUN')

    def test_actual_shared_index_identity(self):
        for count,(bp,manifest) in self.results.items():
            with self.subTest(count=count):
                seams={}
                for record in manifest['patches']:
                    for side in record['sides']:
                        if side['provenance']=='DERIVED_PARTITION_SEAM':
                            seams.setdefault(side['curve_id'],[]).append(side['control_vertex_ids'])
                self.assertEqual(len(seams),count-1)
                for uses in seams.values():
                    self.assertEqual(len(uses),2)
                    self.assertIn(uses[0],(uses[1],uses[1][::-1]))

    def test_independent_original_cad_oracle(self):
        for count,(bp,manifest) in self.results.items():
            with self.subTest(count=count):
                report=independent_audit(self.source,bp,manifest)
                self.assertEqual(report['sample_count'],count*35*35)
                self.assertEqual(report['derived_seams_checked'],count-1)
                self.assertTrue(report['audit_budget_pass'])
                self.assertEqual(report['continuous_distance_bound'],'NOT_CERTIFIED')

    def test_refinement_decreases_sampled_error(self):
        errors=[self.results[n][1]['maximum_pointwise_sampled_error_mm'] for n in (1,2,4,8)]
        self.assertEqual(errors,sorted(errors,reverse=True))
        self.assertLess(errors[-1],3e-6)
        self.assertGreater(errors[0],9e-3)

    def test_strict_budget_preserves_failure(self):
        _,manifest=construct(self.source,1,absolute_budget_mm=1e-5,
                             relative_budget=.01,source_label='SYNTHETIC')
        self.assertFalse(manifest['all_segments_meet_budget'])
        self.assertGreater(manifest['maximum_pointwise_sampled_error_mm'],1e-5)

    def test_mutated_bp_rejected_by_digest(self):
        bp,manifest=self.results[2]
        with self.assertRaisesRegex(ValueError,'digest'):
            independent_audit(self.source,bp.replace('v 3 ', 'v 8 ',1),manifest)

    def test_forged_seam_rejected(self):
        bp,manifest=self.results[2]
        tampered=copy.deepcopy(manifest)
        first=next(x for x in tampered['patches'][0]['sides'] if x['curve_id']=='derived_u_seam_1')
        first['control_vertex_ids'][0]=999
        with self.assertRaisesRegex(ValueError,'Sidecar/BP'):
            independent_audit(self.source,bp,tampered)

    def test_invalid_segment_counts(self):
        for count in (0,-1,65):
            with self.subTest(count=count),self.assertRaisesRegex(ValueError,'Segment count'):
                construct(self.source,count,absolute_budget_mm=.01,
                          relative_budget=.01,source_label='SYNTHETIC')


if __name__=='__main__':
    unittest.main()
