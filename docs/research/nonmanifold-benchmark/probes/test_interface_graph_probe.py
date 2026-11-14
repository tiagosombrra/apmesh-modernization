"""Native-kernel positive and negative controls for source-preserving interface graph."""
import unittest
import tempfile
from pathlib import Path
import cadquery as cq
from interface_graph_probe import analyze, make_solids, find_spine, COORD_ABS_BUDGET


class ThreeCuboidInterfaceGraphTests(unittest.TestCase):
    def test_four_sheet_graph_retains_three_distinct_sources(self):
        report = analyze()
        self.assertEqual(report['reconstructed_spatial_curve']['incident_sheet_count'],4)
        self.assertFalse(report['original_topological_identity']['central_source_edge_shared_across_bodies'])
        self.assertEqual(report['original_topological_identity']['central_source_face_uses'],6)
        self.assertEqual(report['original_topological_identity']['central_source_edges'],3)
        self.assertTrue(report['analytic_region_oracle']['passed'])
        self.assertNotEqual(report['g2_admission'],'PASS')

    def test_four_correct_region_pairs_and_areas(self):
        report=analyze()
        self.assertEqual([s['region_pair'] for s in report['sheets']],
           [['A','B'],['A','C'],['B','VOID'],['C','VOID']])
        self.assertEqual([s['area'] for s in report['sheets']], [25.0]*4)
        self.assertEqual([len(s['source_faces']) for s in report['sheets']],[2,2,1,1])

    def test_central_spine_source_curves_have_separate_ids(self):
        solids=make_solids()
        _, edges=find_spine(solids,5.,COORD_ABS_BUDGET)
        self.assertEqual(len(edges),3)
        self.assertFalse(edges['A'][0].wrapped.IsSame(edges['B'][0].wrapped))
        self.assertFalse(edges['A'][0].wrapped.IsSame(edges['C'][0].wrapped))
        self.assertFalse(edges['B'][0].wrapped.IsSame(edges['C'][0].wrapped))

    def test_nearly_coincident_edge_must_not_be_welded(self):
        with self.assertRaisesRegex(ValueError,'Expected one three-body'):
            analyze(shifts={'B':(2e-5,0,0)})

    def test_missing_region_edge_must_not_be_accepted(self):
        with self.assertRaisesRegex(ValueError,'Expected one three-body'):
            analyze(shifts={'C':(0,-0.1,0)})

    def test_native_step_export_import_graph_preservation(self):
        source=make_solids()
        with tempfile.TemporaryDirectory() as directory:
            model_path=Path(directory)/'three_cuboids.step'
            assembly=cq.Assembly(name='three_touching_cuboids')
            for key in ('A','B','C'):
                assembly.add(source[key])
            assembly.export(str(model_path), exportType='STEP')
            imported=cq.importers.importStep(str(model_path)).val().Solids()
            self.assertEqual(len(imported),3)
            restored={}
            for solid in imported:
                x,y,_=solid.Center().toTuple()
                if x<0 and y>0: label='A'
                elif x>0 and y>0: label='B'
                elif x<0 and y<0: label='C'
                else: raise AssertionError('Unexpected imported solid centroid')
                self.assertNotIn(label,restored)
                restored[label]=solid
            report=analyze(source_solids=restored)
            self.assertEqual(report['reconstructed_spatial_curve']['incident_sheet_count'],4)
            self.assertEqual([s['region_pair'] for s in report['sheets']], [['A','B'],['A','C'],['B','VOID'],['C','VOID']])

    def test_nonfinite_source_parameters_rejected(self):
        with self.assertRaisesRegex(ValueError,'Width'):
            analyze(width=float('nan'))

    def test_near_exact_contact_perturbation_must_not_create_new_junction(self):
        with self.assertRaisesRegex(ValueError,'Expected one three-body'):
            analyze(shifts={'B':(1e-8,0,0)})


if __name__=='__main__':
    unittest.main()
