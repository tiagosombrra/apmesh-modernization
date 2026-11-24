"""Positive, manifold-mode and tolerance controls for native OCCT sewing."""
import tempfile
from pathlib import Path
import unittest
import cadquery as cq
from interface_graph_probe import analyze
from nonmanifold_sewing_probe import construct


class NonmanifoldSewingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph=analyze()

    def test_four_faces_share_same_real_native_edge(self):
        report,_=construct(self.graph)
        self.assertTrue(report['kernel_valid'])
        self.assertEqual(report['faces'],4)
        self.assertEqual(report['shared_four_incident_edge_count'],1)
        self.assertEqual(report['multiple_edges_reported_by_sewing'],1)
        self.assertEqual(report['max_edge_incidence'],4)
        self.assertEqual(report['shared_edge_length'],5)
        self.assertEqual(report['classification'],'CONSTRUCTED_CAD_SURFACE_COMPLEX_NOT_APMESH_BP')
        self.assertEqual(report['g2_external_admission'],'NOT_GRANTED')

    def test_regular_manifold_mode_does_not_share_four(self):
        report,_=construct(self.graph,nonmanifold=False)
        self.assertEqual(report['shared_four_incident_edge_count'],0)
        self.assertLess(report['max_edge_incidence'],4)

    def test_gap_larger_than_sewing_tolerance_rejected_as_four_way_shared(self):
        report,_=construct(self.graph,displace_sheet='A/B',offset=2e-5)
        self.assertEqual(report['shared_four_incident_edge_count'],0)
        self.assertLess(report['max_edge_incidence'],4)

    def test_nonmanifold_native_brep_roundtrip(self):
        report,shape=construct(self.graph)
        with tempfile.TemporaryDirectory() as temp:
            file=Path(temp)/'four_sheet_complex.brep'
            shape.exportBrep(str(file))
            imported=cq.Shape.importBrep(str(file))
            self.assertTrue(imported.isValid())
            self.assertEqual(len(imported.Faces()),4)
            groups=[]
            for i,face in enumerate(imported.Faces()):
                for edge in face.Edges():
                    found=next((p for p in groups if p[0].wrapped.IsSame(edge.wrapped)),None)
                    if found is None:
                        found=[edge,set()];groups.append(found)
                    found[1].add(i)
            self.assertEqual(len([e for e,faces in groups if len(faces)==4]),1)


if __name__ == '__main__':
    unittest.main()
