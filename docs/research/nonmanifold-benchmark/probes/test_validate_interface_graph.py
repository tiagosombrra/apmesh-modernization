"""Mutation controls that defeat the independent R2 graph checker."""
import copy
import json
import unittest
from interface_graph_probe import analyze
from validate_interface_graph import check


class IndependentGraphAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid = json.loads(json.dumps(analyze()))

    def test_valid_model(self):
        r = check(self.valid)
        self.assertEqual(r['model_admission'], 'NOT_GRANTED')
        self.assertEqual(r['sheets'], 4)

    def test_reject_duplicate_sheet(self):
        x = copy.deepcopy(self.valid)
        x['sheets'][3]['region_pair'] = x['sheets'][2]['region_pair']
        with self.assertRaisesRegex(ValueError,'Unknown/duplicate'):
            check(x)

    def test_reject_corrupt_curve(self):
        x = copy.deepcopy(self.valid)
        x['sheets'][0]['spine_boundary'][0][2] += 0.01
        with self.assertRaisesRegex(ValueError,'Curve identity drift'):
            check(x)

    def test_reject_stolen_source_face(self):
        x = copy.deepcopy(self.valid)
        x['sheets'][0]['source_faces'][0]['face_index'] = x['sheets'][1]['source_faces'][0]['face_index']
        with self.assertRaisesRegex(ValueError,'Source face reused'):
            check(x)

    def test_reject_inverted_interface_orientation(self):
        x = copy.deepcopy(self.valid)
        n=x['sheets'][0]['source_faces'][1]['normal']
        x['sheets'][0]['source_faces'][1]['normal']=[-a for a in n]
        with self.assertRaisesRegex(ValueError,'Non-opposing'):
            check(x)

    def test_reject_unjustified_native_topological_identity(self):
        x = copy.deepcopy(self.valid)
        x['original_topological_identity']['central_source_edge_shared_across_bodies'] = True
        with self.assertRaisesRegex(ValueError,'improperly merged'):
            check(x)

    def test_reject_false_approval(self):
        x = copy.deepcopy(self.valid)
        x['g2_admission'] = 'PASS'
        with self.assertRaisesRegex(ValueError,'Unexpected G2'):
            check(x)


if __name__ == '__main__':
    unittest.main()
