"""Isolated topology and numeric tests; no external CAD rights assumptions."""
import unittest

import cadquery as cq
from original_cad_planar_atlas import build_atlas, eligibility, bilinear


class PlanarAtlasTests(unittest.TestCase):
    def test_box_exact_shared_edge_identity(self):
        bp,r=build_atlas(cq.Workplane('XY').box(2,3,4).val(),'SYNTHETIC','local')
        self.assertEqual(r['converted_face_count'],6)
        self.assertEqual(r['excluded_face_count'],0)
        self.assertEqual(r['unique_controls'],56)
        self.assertEqual(r['source_edge_incidence_within_atlas'],{2:12})
        self.assertLess(r['native_max_sample_distance_mm'],1e-8)
        self.assertEqual(sum(l.startswith('p ') for l in bp.splitlines()),6)
        self.assertEqual(r['apmesh_generation'],'NOT_RUN')
        # Every native source edge must have identical (or reversed) four IDs.
        sides={}
        for p in r['patches']:
            for s in p['sides']:
                sides.setdefault(s['source_edge'],[]).append(s['control_vertex_ids'])
        for pair in sides.values():
            self.assertEqual(len(pair),2)
            self.assertIn(pair[0],(pair[1],list(reversed(pair[1]))))

    def test_nonplanar_cylinder_excluded(self):
        s=cq.Workplane('XY').cylinder(2,1).val()
        _,r=build_atlas(s,'SYNTHETIC','local')
        self.assertGreater(r['excluded_face_count'],0)
        self.assertIn('NONPLANAR_SUPPORT',{e['reason'] for e in r['exclusions']})
        self.assertFalse(r['full_original_model_converted'])

    def test_not_four_sides(self):
        f=cq.Workplane('XY').polyline([(0,0),(3,0),(1,2)]).close().extrude(1).val().Faces()[-1]
        self.assertEqual(eligibility(f,10)[1],'NOT_FOUR_STRAIGHT_SIDES')

    def test_concave_quad_rejected(self):
        face=cq.Workplane('XY').polyline([(0,0),(2,0),(.5,.5),(0,2)]).close().extrude(1).val().Faces()[-1]
        self.assertEqual(eligibility(face,10)[1],'NONCONVEX_OR_DEGENERATE')

    def test_hole_excluded(self):
        f=cq.Workplane('XY').rect(4,4).rect(1,1).extrude(1).val()
        multi=[x for x in f.Faces() if len(x.Wires())>1]
        self.assertTrue(multi)
        self.assertEqual(eligibility(multi[0],10)[1],'TRIMMED_MULTIWIRE')

    def test_bilinear_corners(self):
        c=((0,0,0),(2,0,0),(3,2,0),(-1,2,0))
        self.assertEqual(bilinear(c,0,0),c[0])
        self.assertEqual(bilinear(c,1,0),c[1])
        self.assertEqual(bilinear(c,1,1),c[2])
        self.assertEqual(bilinear(c,0,1),c[3])

    def test_nearby_but_distinct_faces_never_weld(self):
        a=cq.Workplane('XY').box(1,1,1).val()
        b=cq.Workplane('XY').box(1,1,1).translate((1+1e-10,0,0)).val()
        two=cq.Compound.makeCompound([a,b])
        _,r=build_atlas(two,'SYNTHETIC','local')
        self.assertEqual(r['converted_face_count'],12)
        self.assertEqual(r['unique_controls'],112)
        self.assertEqual(r['source_edge_incidence_within_atlas'],{2:24})

    def test_preserve_synthetic_classification(self):
        _,r=build_atlas(cq.Workplane('XY').box(1,1,1).val(),'SYNTHETIC','local')
        self.assertEqual(r['scientific_scope'],'PARTIAL_EXACT_PLANAR_SUBFACES_ONLY')
        self.assertEqual(r['independent_external_nonmanifold_admission'],'NOT_GRANTED')


class IndependentAtlasAuditTests(unittest.TestCase):
    def test_independent_source_distance(self):
        from audit_original_cad_planar_atlas import audit
        shape=cq.Workplane('XY').box(2,3,4).val()
        bp,manifest=build_atlas(shape,'SYNTHETIC','synthetic-sha')
        result=audit(shape,bp,manifest,source_sha256='synthetic-sha')
        self.assertEqual(result['validated_patches'],6)
        self.assertEqual(result['independent_sample_count'],294)
        self.assertLess(result['maximum_native_distance_mm'],1e-8)

    def test_tampered_control_rejected(self):
        from audit_original_cad_planar_atlas import audit
        shape=cq.Workplane('XY').box(2,3,4).val()
        bp,manifest=build_atlas(shape,'SYNTHETIC','synthetic-sha')
        tampered=bp.replace('v -1', 'v -8',1)
        self.assertNotEqual(tampered,bp)
        with self.assertRaisesRegex(ValueError,'checksum'):
            audit(shape,tampered,manifest,source_sha256='synthetic-sha')

    def test_forged_topology_rejected(self):
        from audit_original_cad_planar_atlas import audit
        shape=cq.Workplane('XY').box(2,3,4).val()
        bp,manifest=build_atlas(shape,'SYNTHETIC','synthetic-sha')
        manifest['patches'][0]['sides'][0]['source_edge']=999
        with self.assertRaisesRegex(ValueError,'edge ID'):
            audit(shape,bp,manifest,source_sha256='synthetic-sha')


if __name__=='__main__':
    unittest.main()
