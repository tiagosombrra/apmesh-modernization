"""Source-topology checks use toy Part 21 records, never third-party CAD payloads."""
from __future__ import annotations

import unittest
from external_step_source_incidence import (
    parse_entities, source_census, exact_common_collinear_overlap,
)


def synthetic(*, split_edges=False, missing=False, duplicate=False, same_face_twice=False):
    """Build three explicit faces referencing the same or distinct source edge."""
    lines = ["ISO-10303-21;", "DATA;",
             "#1=CARTESIAN_POINT('',(0,0,0));", "#2=CARTESIAN_POINT('',(6,0,0));",
             "#3=VERTEX_POINT('',#1);", "#4=VERTEX_POINT('',#2);",
             "#5=DIRECTION('',(1,0,0));", "#6=VECTOR('',#5,1);",
             "#7=LINE('',#1,#6);"]
    if not missing:
        lines.append("#8=EDGE_CURVE('edge; semicolon',#3,#4,#7,.T.);")
    for idx in range(3):
        eid = 8 if not split_edges else 20 + idx
        if split_edges:
            lines.append(f"#{eid}=EDGE_CURVE('edge{idx}',#3,#4,#7,.T.);")
        oe = 30 + idx
        loop = 40 + idx
        bound = 50 + idx
        face = 60 + idx
        lines += [f"#{oe}=ORIENTED_EDGE('',$,$,#{eid},.T.);",
                  f"#{loop}=EDGE_LOOP('',(#{oe}{',' + '#' + str(oe) if same_face_twice else ''}));",
                  f"#{bound}=FACE_OUTER_BOUND('',#{loop},.T.);",
                  f"#{face}=ADVANCED_FACE('face{idx}',(#{bound}),#5,.T.);"]
    if duplicate:
        lines.append("#60=ADVANCED_FACE('duplicate',(#50),#5,.T.);")
    return ('\n'.join(lines) + '\nENDSEC;\nEND-ISO-10303-21;\n').encode()


class SourceIncidenceTests(unittest.TestCase):
    def test_three_distinct_faces_same_original_edge_is_positive(self):
        report = source_census(synthetic())
        self.assertEqual(report['source_edge_three_plus_count'], 1)
        self.assertEqual(report['three_plus_original_edges'][0]['original_source_face_ids'], [60, 61, 62])

    def test_coincident_but_distinct_source_edge_ids_are_not_welded(self):
        report = source_census(synthetic(split_edges=True))
        self.assertEqual(report['source_edge_three_plus_count'], 0)
        self.assertEqual(report['source_incidence_histogram'], {'1': 3})

    def test_missing_edge_entity_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'unique EDGE_CURVE'):
            source_census(synthetic(missing=True))

    def test_duplicate_source_entity_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate STEP instance'):
            source_census(synthetic(duplicate=True))

    def test_duplicate_coedge_use_not_miscounted_as_another_face(self):
        report = source_census(synthetic(same_face_twice=True))
        self.assertEqual(report['source_edge_three_plus_count'], 1)
        self.assertEqual(len(report['repeat_uses_by_same_face']), 3)
        self.assertEqual(report['three_plus_original_edges'][0]['original_source_face_ids'], [60, 61, 62])

    def test_quoted_semicolon_survives_scanner(self):
        self.assertIn(8, parse_entities(synthetic()))

    def test_unterminated_data_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unterminated DATA'):
            source_census(synthetic().replace(b'ENDSEC;', b''))

    def test_exact_common_collinear_overlap_but_not_source_identity(self):
        raw = ("ISO-10303-21;\nDATA;\n" + '\n'.join([
            f"#{p}=CARTESIAN_POINT('',({x},0,0));" for p,x in [(1,0),(2,6),(3,2),(4,8),(5,4),(6,10)]])
            + '\n' + '\n'.join([f"#{v}=VERTEX_POINT('',#{p});" for v,p in [(11,1),(12,2),(13,3),(14,4),(15,5),(16,6)]])
            + "\n#20=DIRECTION('',(1,0,0));\n#21=VECTOR('',#20,1);\n#22=LINE('',#1,#21);\n"
            + '\n'.join([f"#{edge}=EDGE_CURVE('',#{a},#{b},#22,.T.);" for edge,a,b in [(30,11,12),(31,13,14),(32,15,16)]])
            + '\nENDSEC;\nEND-ISO-10303-21;\n').encode()
        result = exact_common_collinear_overlap(raw, (30,31,32))
        self.assertTrue(result['positive_three_way_source_line_overlap'])
        self.assertEqual(result['original_axis_coordinate_interval'], ['4', '6'])
        self.assertFalse(result['shared_original_edge_curve_identity'])

    def test_non_collinear_segments_rejected(self):
        raw = ("ISO-10303-21;\nDATA;\n#1=CARTESIAN_POINT('',(0,0,0));\n"
               "#2=CARTESIAN_POINT('',(6,0,0));\n#3=CARTESIAN_POINT('',(2,1,0));\n"
               "#4=CARTESIAN_POINT('',(8,0,0));\n#5=CARTESIAN_POINT('',(4,0,0));\n"
               "#6=CARTESIAN_POINT('',(10,0,0));\n"
               + ''.join(f"#{v}=VERTEX_POINT('',#{p});\n" for v,p in [(11,1),(12,2),(13,3),(14,4),(15,5),(16,6)])
               + "#20=DIRECTION('',(1,0,0));\n#21=VECTOR('',#20,1);\n#22=LINE('',#1,#21);\n"
               + ''.join(f"#{edge}=EDGE_CURVE('',#{a},#{b},#22,.T.);\n" for edge,a,b in [(30,11,12),(31,13,14),(32,15,16)])
               + "ENDSEC;\nEND-ISO-10303-21;\n").encode()
        with self.assertRaisesRegex(ValueError, 'not exactly collinear'):
            exact_common_collinear_overlap(raw, (30,31,32))


if __name__ == '__main__':
    unittest.main()
