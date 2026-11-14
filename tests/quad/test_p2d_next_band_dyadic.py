"""Bounded negative/positive oracle for a second QUAD/AFT connected band."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "research" / "quad"))
from p2d_next_band_dyadic import (FIRST_BAND, SECOND_SOURCE_SAMPLE, candidate_bands,
                                  inspect_band, source_coarse_cell, _vertex_link_manifold)


class SecondConnectedBandDyadicTest(unittest.TestCase):
    def test_first_band_reproduction(self):
        baseline = inspect_band()
        self.assertEqual(baseline.leaves, 28)
        self.assertEqual(baseline.quad_uv_tiles, 21)
        self.assertEqual(baseline.uv_area, 21/64)
        self.assertTrue(baseline.admitted_disk)

    def test_source_is_second_physical_candidate_error(self):
        self.assertEqual(source_coarse_cell(SECOND_SOURCE_SAMPLE), (3, 0))
        self.assertNotIn((3, 0), FIRST_BAND)

    def test_one_cell_island_is_rejected(self):
        alone = inspect_band(((3, 0),))
        self.assertEqual((alone.leaves, alone.quad_uv_tiles), (31, 22))
        self.assertFalse(alone.connected)
        self.assertFalse(alone.vertex_manifold)
        self.assertFalse(alone.admitted_disk)

    def test_two_distinct_minimal_bridge_choices(self):
        trials = candidate_bands()
        accepted_two = [r for r in trials if len(r.selected) == 2 and r.admitted_disk]
        self.assertEqual([r.selected for r in accepted_two],
                         [((2, 0), (3, 0)), ((3, 0), (3, 1))])
        for item in accepted_two:
            self.assertEqual((item.leaves, item.quad_uv_tiles, item.uv_area),
                             (34, 24, 24/64))
        self.assertEqual(sum(not r.admitted_disk for r in trials), 1)

    def test_three_cell_bridge_expands_more_area(self):
        complete = inspect_band(((3, 0), (2, 0), (3, 1)))
        self.assertTrue(complete.admitted_disk)
        self.assertEqual((complete.leaves, complete.quad_uv_tiles, complete.uv_area),
                         (37, 26, 26/64))
        self.assertGreater(complete.uv_area, 21/64)

    def test_negative_inputs_and_diagonal_vertex(self):
        for site in [(-0.1, 0.1), (float('nan'), 0.2), (0.8, 1.0), (0.1,)]:
            with self.subTest(site=site), self.assertRaises(ValueError):
                source_coarse_cell(site)
        for cells in [((1, 1),), ((3, 0), (3, 0)), ((4, 1),)]:
            with self.subTest(cells=cells), self.assertRaises(ValueError):
                inspect_band(cells)
        self.assertFalse(_vertex_link_manifold({(0, 0), (1, 1)}))


if __name__ == "__main__":
    unittest.main()
