#!/usr/bin/env python3
"""Fail-closed STEP-vertex prebinding tests for S40-F2 (no private CAD)."""
from __future__ import annotations

import ast
import math
from pathlib import Path
import unittest

SOURCE = Path(__file__).with_name('s40f1_six_edge_planar_builder.py')
TREE = ast.parse(SOURCE.read_text(encoding='utf-8'))
NAMES = {'prebind_inherited_original_vertices', 'distance'}
HELPERS = [node for node in TREE.body
           if isinstance(node, ast.FunctionDef) and node.name in NAMES]
assert {x.name for x in HELPERS} == NAMES
ns = {'math': math}
exec(compile(ast.Module(body=HELPERS, type_ignores=[]), str(SOURCE), 'exec'), ns)
ns['coordinates'] = lambda table, vid: table[vid]


def entry(edge_id, start, end):
    return {'edge_curve_id': edge_id, 'start_vertex_id': start,
            'end_vertex_id': end}


class SourceVertexPrebindingTests(unittest.TestCase):
    def setUp(self):
        self.points = [(0., 0., 0.), (1., 0., 0.),
                       (2., 0., 0.), (3., 0., 0.),
                       (4., 0., 0.), (5., 0., 0.),
                       (6., 0., 0.)]
        self.table = {101: (0., 0., 0.), 102: (3., 0., 0.),
                      103: (6., 0., 0.)}
        self.chains = {71: [(9, 'bottom', (0, 1, 2, 3))],
                       72: [(10, 'top', (3, 4, 5, 6))]}
        self.edges = [entry(71, 101, 102), entry(72, 102, 103)]

    def prebind(self, edges=None, chains=None, points=None, table=None, prior=None):
        return ns['prebind_inherited_original_vertices'](
            self.table if table is None else table,
            self.edges if edges is None else edges,
            self.chains if chains is None else chains,
            self.points if points is None else points,
            {} if prior is None else prior,
        )

    def test_all_inherited_vertices_seeded(self):
        self.assertEqual(self.prebind(), {101: 0, 102: 3, 103: 6})

    def test_new_source_edge_before_inherited_is_prebound(self):
        # The source wire may contain a new edge before its inherited neighbor.
        source_order = [entry(99, 200, 102), self.edges[1], self.edges[0]]
        result = self.prebind(edges=source_order)
        self.assertEqual(result[102], 3)
        self.assertEqual(result[103], 6)

    def test_source_order_reversal_keeps_global_id_identity(self):
        self.assertEqual(self.prebind(), self.prebind(edges=list(reversed(self.edges))))

    def test_new_edge_not_in_inherited_cache_does_not_create_ids(self):
        result = self.prebind(edges=[entry(99, 200, 201)] + self.edges)
        self.assertEqual(len(result), 3)
        self.assertNotIn(200, result)

    def test_previously_bound_vertex_same_global_id_is_allowed(self):
        result = self.prebind(prior={102: 3})
        self.assertEqual(result[102], 3)

    def test_conflicting_existing_global_vertex_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'conflicting global control IDs'):
            self.prebind(prior={102: 4})

    def test_malformed_source_global_coordinate_is_rejected(self):
        table = dict(self.table)
        table[102] = (3.01, 0., 0.)
        with self.assertRaisesRegex(ValueError, 'not the original STEP vertex'):
            self.prebind(table=table)

    def test_invalid_global_index_is_rejected(self):
        bad = {71: [(9, 'bottom', (0, 1, 2, 200))], 72: self.chains[72]}
        with self.assertRaisesRegex(ValueError, 'invalid global control'):
            self.prebind(chains=bad)

    def test_negative_global_index_is_rejected(self):
        bad = {71: [(9, 'bottom', (0, 1, 2, -1))], 72: self.chains[72]}
        with self.assertRaisesRegex(ValueError, 'invalid global control'):
            self.prebind(chains=bad)

    def test_noninteger_global_index_is_rejected(self):
        bad = {71: [(9, 'bottom', (0, 1, 2, 3.0))], 72: self.chains[72]}
        with self.assertRaisesRegex(ValueError, 'invalid global control'):
            self.prebind(chains=bad)

    def test_empty_inherited_chain_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'no indexed segments'):
            self.prebind(chains={71: [], 72: self.chains[72]})

    def test_nonbicubic_segment_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'must be cubic'):
            self.prebind(chains={71: [(9, 'bottom', (0, 1, 3))],
                                 72: self.chains[72]})

    def test_reversed_index_chain_without_source_reversal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'not the original STEP vertex'):
            self.prebind(chains={71: [(9, 'bottom', (3, 2, 1, 0))],
                                 72: self.chains[72]})

    def test_duplicate_source_vertex_with_two_distinct_controls_is_rejected(self):
        # Coordinate-equal points are NOT sufficient to weld distinct IDs.
        points = self.points + [(3., 0., 0.)]
        chains = {71: self.chains[71],
                  72: [(10, 'top', (7, 4, 5, 6))]}
        with self.assertRaisesRegex(ValueError, 'conflicting global control IDs'):
            self.prebind(points=points, chains=chains)

    def test_control_coordinates_not_modified_by_prepass(self):
        original = list(self.points)
        self.prebind()
        self.assertEqual(self.points, original)

    def test_inherited_chains_not_modified_by_prepass(self):
        before = {k: list(v) for k, v in self.chains.items()}
        self.prebind()
        self.assertEqual(self.chains, before)


if __name__ == '__main__':
    unittest.main()
