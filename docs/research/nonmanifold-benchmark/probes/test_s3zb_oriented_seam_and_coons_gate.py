#!/usr/bin/env python3
"""Adversarial geometry-agnostic S3.Z.2 seam orientation and Coons tests."""
import math
import unittest

from s3zb_oriented_seam_and_coons_gate import (
    directed_boundary_indices, audit_new_surface_topology,
    audit_new_coons_nets, audit_final_candidate,
)


class S3Z2OrientedSeamTests(unittest.TestCase):
    def setUp(self):
        # Four previously admitted patches enclose one candidate patch.
        # Their grid-ordered shared edges are identical, while the actual
        # counterclockwise boundary traversal must be reversed.
        self.new = tuple(range(16))
        self.old = []
        next_id = 16
        for side, positions in (
            ('top', (0,1,2,3)),
            ('left', (3,7,11,15)),
            ('bottom', (12,13,14,15)),
            ('right', (0,4,8,12)),
        ):
            data = list(range(next_id, next_id + 16))
            next_id += 16
            locations = {
                'bottom':(0,1,2,3),'top':(12,13,14,15),
                'left':(0,4,8,12),'right':(3,7,11,15),
            }[side]
            for at, value in zip(locations,positions):
                data[at]=value
            self.old.append(tuple(data))
        self.proposed=self.old+[self.new]

    def check(self, **kwargs):
        args=dict(prior_patches=self.old,proposed_patches=self.proposed,
                  first_new=4,enforce_s40_counts=False)
        args.update(kwargs)
        return audit_new_surface_topology(**args)

    def test_full_four_sided_closure(self):
        r=self.check()
        self.assertEqual(r['new_old_join_count'],4)
        self.assertEqual(r['new_new_internal_join_count'],0)
        self.assertEqual(r['new_oriented_sides_checked'],4)
        self.assertEqual(r['new_unpaired_sides'],0)

    def test_top_and_left_grid_sides_are_direction_reversed(self):
        self.assertEqual(directed_boundary_indices(self.new,'bottom'),(0,1,2,3))
        self.assertEqual(directed_boundary_indices(self.new,'right'),(3,7,11,15))
        self.assertEqual(directed_boundary_indices(self.new,'top'),(15,14,13,12))
        self.assertEqual(directed_boundary_indices(self.new,'left'),(12,8,4,0))

    def test_reverse_raw_grid_is_not_a_valid_orientation_rule(self):
        self.assertEqual(self.old[0][12:16],self.new[0:4])
        self.assertEqual(directed_boundary_indices(self.old[0],'top'),
                         directed_boundary_indices(self.new,'bottom')[::-1])

    def test_same_four_controls_with_wrong_orientation_rejected(self):
        wrong=list(self.proposed)
        p=list(wrong[0]);p[12:16]=p[12:16][::-1]
        wrong[0]=tuple(p)
        with self.assertRaisesRegex(ValueError,'CCW-oriented'):
            self.check(prior_patches=wrong[:4],proposed_patches=wrong)

    def test_unpaired_new_side_rejected(self):
        wrong=list(self.proposed)
        p=list(wrong[0]);p[13]=9999
        wrong[0]=tuple(p)
        with self.assertRaisesRegex(ValueError,'unpaired'):
            self.check(prior_patches=wrong[:4],proposed_patches=wrong)

    def test_new_patch_self_pair_rejected(self):
        # A repeated side is invalid even when indexed by the same controls.
        corrupt = list(self.proposed)
        p=list(corrupt[-1]);p[12:16]=p[0:4]
        corrupt[-1]=tuple(p)
        with self.assertRaises(ValueError):
            self.check(proposed_patches=corrupt)

    def test_old_patch_reindexing_rejected(self):
        altered=list(self.proposed)
        altered[0]=tuple(reversed(altered[0]))
        with self.assertRaisesRegex(ValueError,'Previously admitted'):
            self.check(proposed_patches=altered)

    def test_extra_duplicate_new_patch_fails(self):
        with self.assertRaisesRegex(ValueError,'Overincident'):
            self.check(proposed_patches=self.proposed+[self.new])

    def test_s40_counts_default_is_hard_gate(self):
        with self.assertRaises(ValueError):
            self.check(enforce_s40_counts=True)

    def test_cannot_shift_new_patch_start(self):
        with self.assertRaisesRegex(ValueError,'prefix size'):
            self.check(first_new=3)


class S3Z2CoonsIdentityTests(unittest.TestCase):
    def setUp(self):
        self.points=[(i/3,j/3,0.) for j in range(4) for i in range(4)]
        self.patch=tuple(range(16))

    def audit(self, **kwargs):
        values=dict(original_points=[],candidate_points=self.points,
                    patches=[self.patch],first_new=0,enforce_s40_counts=False)
        values.update(kwargs)
        return audit_new_coons_nets(**values)

    def test_exact_planar_coons_interior(self):
        r=self.audit()
        self.assertEqual(r['coons_interiors_checked'],4)
        self.assertLess(r['max_coons_identity_error_mm'],1e-14)
        self.assertFalse(r['continuous_trimmed_CAD_equivalence_certified'])

    def test_changed_interior_is_rejected(self):
        altered=list(self.points);altered[5]=(1/3,1/3,0.00001)
        with self.assertRaisesRegex(ValueError,'differs'):
            self.audit(candidate_points=altered)

    def test_nonfinite_interior_rejected(self):
        altered=list(self.points);altered[6]=(math.nan,1/3,0)
        with self.assertRaisesRegex(ValueError,'nonfinite'):
            self.audit(candidate_points=altered)

    def test_duplicate_interior_id_rejected(self):
        p=list(self.patch);p[9]=5
        with self.assertRaisesRegex(ValueError,'aliases'):
            self.audit(patches=[tuple(p)])

    def test_boundary_interior_alias_rejected(self):
        p=list(self.patch);p[5]=1
        with self.assertRaisesRegex(ValueError,'aliases'):
            self.audit(patches=[tuple(p)])

    def test_previous_control_interior_alias_rejected(self):
        with self.assertRaisesRegex(ValueError,'previously admitted'):
            self.audit(original_points=self.points[:8])

    def test_nonexistent_control_index_rejected(self):
        p=list(self.patch);p[5]=99
        with self.assertRaises((ValueError,IndexError)):
            self.audit(patches=[tuple(p)])

    def test_cannot_relax_coons_tolerance(self):
        with self.assertRaisesRegex(ValueError,'relaxed'):
            self.audit(tolerance_mm=.0001)

    def test_invalid_control_cardinality_rejected(self):
        with self.assertRaisesRegex(ValueError,'cardinalities'):
            self.audit(enforce_s40_counts=True)

    def test_interior_reused_as_another_new_patch_boundary_rejected(self):
        second=list(range(16,32))
        second[0]=5
        data=list(self.points)+[(10+i/3,0.,0.) for i in range(16)]
        with self.assertRaisesRegex(ValueError,'aliases'):
            self.audit(candidate_points=data,patches=[self.patch,tuple(second)])


if __name__=='__main__':
    unittest.main()

class S3Z2NewInternalEdgeTests(unittest.TestCase):
    def setUp(self):
        # A pair of adjacent new quads shares one vertical, source-independent
        # Coons subdivision side, with six prior exterior faces around them.
        def gid(x,y): return y*7+x
        self.left = tuple(gid(x,y) for y in range(4) for x in range(4))
        self.right = tuple(gid(x+3,y) for y in range(4) for x in range(4))
        prior=[]
        next_id=28
        for patch,new_side,old_side in (
            (self.left,'bottom','top'), (self.left,'top','bottom'),
            (self.left,'left','right'), (self.right,'bottom','top'),
            (self.right,'top','bottom'),(self.right,'right','left'),
        ):
            ids=list(range(next_id,next_id+16));next_id+=16
            locations={'bottom':(0,1,2,3),'top':(12,13,14,15),
                       'left':(0,4,8,12),'right':(3,7,11,15)}[old_side]
            boundary={'bottom':patch[:4],'top':patch[12:16],
                      'left':patch[::4],'right':patch[3::4]}[new_side]
            for pos,idx in zip(locations,boundary):ids[pos]=idx
            prior.append(tuple(ids))
        self.prior=prior
        self.joint=prior+[self.left,self.right]

    def test_new_new_internal_seam_is_oriented(self):
        result=audit_new_surface_topology(self.prior,self.joint,first_new=6,enforce_s40_counts=False)
        self.assertEqual(result['new_new_internal_join_count'],1)
        self.assertEqual(result['new_old_join_count'],6)
        self.assertEqual(result['new_oriented_sides_checked'],8)

    def test_internal_new_new_seam_wrong_orientation_rejected(self):
        # Changing the right patch's common edge orientation is not allowed,
        # even if all four global indices remain the same unordered set.
        modified=list(self.joint);r=list(self.right)
        edge=(r[0],r[4],r[8],r[12])
        for pos,idx in zip((0,4,8,12),edge[::-1]):r[pos]=idx
        modified[-1]=tuple(r)
        with self.assertRaises((ValueError,IndexError)):
            audit_new_surface_topology(self.prior,modified,first_new=6,enforce_s40_counts=False)
