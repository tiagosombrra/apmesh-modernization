#!/usr/bin/env python3
"""Synthetic adversarial topology tests for S3.Z source-canonical seam repair."""
import unittest

from s3z_s40_circular_seam_gate import (
    _indexed_side, _sides_by_original_indices, audit_global_repair_scope,
)


class S3ZGlobalSeamScopeTests(unittest.TestCase):
    def setUp(self):
        # Synthetic surfaces share exactly one four-control side with opposite
        # orientations; no source CAD, original BP, or geometry is serialized.
        self.old_patch = tuple(range(16))
        self.new_patch = (3, 16, 17, 18, 7, 19, 20, 21,
                          11, 22, 23, 24, 15, 25, 26, 27)
        self.parent_points = [(float(i),0.,0.) for i in range(16)]
        self.trial_points = self.parent_points+[(float(i),1.,0.) for i in range(16,28)]
        self.trial_points[7] = (7., 0.0002, 0.)
        self.trial_points[11] = (11., 0.0002, 0.)
        self.parents = [self.old_patch]
        self.children = [self.old_patch,self.new_patch]
        self.lineage = {1827:{1523:((0,'right'),)}}
        self.changed = {7,11}
        self.old_neighbor = {0}

    def check(self, **kwargs):
        args=dict(selected_points=self.parent_points,
                  selected_patches=self.parents, trial_points=self.trial_points,
                  joint_patches=self.children,moved_ids=self.changed,
                  inherited_side_lineage=self.lineage,
                  neighbor_old_patch_ids=self.old_neighbor,
                  bias_mm=0.0002,enforce_original_counts=False)
        args.update(kwargs)
        return audit_global_repair_scope(**args)

    def test_positive_exactly_two_sided_reversed_source_seam(self):
        r=self.check()
        self.assertEqual(r['global_two_sided_seams'],1)
        self.assertEqual(r['global_open_sides'],6)
        self.assertEqual(r['changed_prior_source_control_count'],2)
        self.assertEqual(r['joined_original_source_side_count'],1)
        self.assertEqual(r['affected_prior_source_patch_ids'],[0])

    def test_missing_new_original_side_rejected(self):
        altered=list(self.children)
        altered[1]=tuple(28 if v==3 else v for v in altered[1])
        with self.assertRaisesRegex(ValueError,'failed to join two sides'):
            self.check(joint_patches=altered)

    def test_wrong_orientation_with_same_global_ids_rejected(self):
        # Exactly shared four IDs, but same rather than reversed boundary sense.
        altered=list(self.children)
        p=list(altered[1]);p[0],p[4],p[8],p[12]=15,11,7,3
        altered[1]=tuple(p)
        with self.assertRaisesRegex(ValueError,'orientation'):
            self.check(joint_patches=altered)

    def test_unexpected_old_control_change_rejected(self):
        altered=list(self.trial_points)
        altered[1]=(1.,3.,0.)
        with self.assertRaisesRegex(ValueError,'mutation'):
            self.check(trial_points=altered)

    def test_out_of_range_shared_control_rejected(self):
        with self.assertRaisesRegex(ValueError,'outside'):
            self.check(moved_ids={7,99})

    def test_cylinder_patch_alias_rejected(self):
        old_second=tuple(range(28,44))
        old_second=old_second[:4]+(7,)+old_second[5:]
        with self.assertRaisesRegex(ValueError,'Untracked old patch'):
            self.check(selected_patches=[self.old_patch,old_second],
                       joint_patches=[self.old_patch,old_second,self.new_patch])

    def test_overincident_shared_source_edge_rejected(self):
        with self.assertRaisesRegex(ValueError,'Overincident'):
            self.check(joint_patches=self.children+[self.new_patch])

    def test_duplicate_source_lineage_rejected(self):
        with self.assertRaisesRegex(ValueError,'Repeated or aliased'):
            self.check(inherited_side_lineage={1827:{1523:((0,'right'),),
                                                      252:((0,'right'),)}})

    def test_unexpected_old_patch_reindexing_rejected(self):
        with self.assertRaisesRegex(ValueError,'indices changed'):
            self.check(joint_patches=[tuple(reversed(self.old_patch)),self.new_patch])

    def test_immutable_3044_rejected_when_aliasing_source_control(self):
        # A large synthetic parent intentionally aliases a changed control
        # inside immutable source face #3044's patch range.
        extra = [tuple(range(16*i,16*i+16)) for i in range(1,149)]
        old = [self.old_patch]+extra
        p = list(old[148]);p[0]=7;old[148]=tuple(p)
        # Candidate remains an exact old prefix, then adds a legal new side.
        with self.assertRaisesRegex(ValueError,'#3044'):
            self.check(selected_patches=old,joint_patches=old+[self.new_patch],
                       neighbor_old_patch_ids={0,148})

    def test_immutable_original_hole_rejected_when_shared_control_aliases(self):
        old = [self.old_patch]+[tuple(range(16*i,16*i+16)) for i in range(1,97)]
        target=list(old[96]);target[0]=7;old[96]=tuple(target)
        with self.assertRaisesRegex(ValueError,'#218'):
            self.check(selected_patches=old,joint_patches=old+[self.new_patch],
                       neighbor_old_patch_ids={0,96})

    def test_full_original_cardinality_is_mandatory_by_default(self):
        with self.assertRaisesRegex(ValueError,'seam counts or cardinality'):
            self.check(enforce_original_counts=True)

    def test_open_seams_one_or_two_only(self):
        m=_sides_by_original_indices(self.children)
        self.assertEqual(sorted({len(v) for v in m.values()}),[1,2])
        self.assertEqual(_indexed_side(self.old_patch,'right'),(3,7,11,15))
        with self.assertRaisesRegex(ValueError,'Unknown'):
            _indexed_side(self.old_patch,'diagonal')

    def test_zero_bias_means_unchanged_old_controls(self):
        trial=self.parent_points+self.trial_points[16:]
        self.assertEqual(self.check(trial_points=trial,bias_mm=0)['changed_prior_source_control_count'],0)

    def test_too_large_bias_rejected(self):
        with self.assertRaisesRegex(ValueError,'displacement'):
            self.check(bias_mm=0.01)


if __name__=='__main__':
    unittest.main()
