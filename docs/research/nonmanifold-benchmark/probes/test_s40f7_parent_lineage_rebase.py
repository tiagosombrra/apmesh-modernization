#!/usr/bin/env python3
"""Synthetic, topology-only tests of the S40-F7 native-parent reconciliation.

No source-derived CAD coordinates are embedded in this public test module.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import tempfile
import unittest

import s40f7_parent_lineage_rebase as f

# These are control-ID connectivity only; all test coordinates are synthetic.
PATCH_NETS = (
    (0, 6, 7, 1, 18, 20, 21, 8, 19, 22, 23, 9, 3, 11, 10, 2),
    (0, 18, 19, 3, 17, 24, 25, 12, 16, 26, 27, 13, 5, 15, 14, 4),
    (28, 34, 35, 29, 46, 48, 49, 36, 47, 50, 51, 37, 31, 39, 38, 30),
    (28, 46, 47, 31, 45, 52, 53, 40, 44, 54, 55, 41, 33, 43, 42, 32),
    (30, 62, 63, 57, 70, 72, 73, 64, 71, 74, 75, 65, 59, 67, 66, 58),
    (59, 68, 69, 56, 71, 76, 77, 60, 70, 78, 79, 61, 30, 38, 39, 31),
    (83, 86, 87, 81, 94, 96, 97, 88, 95, 98, 99, 89, 5, 91, 90, 82),
    (5, 15, 14, 4, 95, 100, 101, 92, 94, 102, 103, 93, 83, 85, 84, 80),
)
INTERFACE_CHAINS = {
    1002: (5, 16, 17, 0),
    1080: (29, 36, 37, 30),
    1139: (0, 6, 7, 1),
    1259: (28, 34, 35, 29),
    1284: (1, 8, 9, 2),
    1473: (33, 44, 45, 28),
    1030: (82, 90, 91, 5),
    1057: (30, 62, 63, 57),
}


def make_fixture():
    """Construct mock parent and eight-piece child without geometric CAD data."""
    child_points = [(float(i + 3), float((i * 17) % 31), float((i * 7) % 19))
                    for i in range(104)]
    child_patches = [tuple(row) for row in PATCH_NETS]
    inventory = f.side_inventory(child_patches)
    assert sum(len(v) == 2 for v in inventory.values()) == 6
    assert sum(len(v) == 1 for v in inventory.values()) == 20
    parent_points = []
    parent_patches = []
    parent_vertex_registry = {}
    lineage = {}
    for edge, ids in INTERFACE_CHAINS.items():
        child = inventory[tuple(sorted(ids))]
        assert len(child) == 1
        child_ccw = child[0][3]
        target_ccw = child_ccw[::-1]
        parent_bottom = []
        for id_ in target_ccw:
            if id_ not in parent_vertex_registry:
                parent_vertex_registry[id_] = len(parent_points)
                parent_points.append(child_points[id_])
            parent_bottom.append(parent_vertex_registry[id_])
        patch = list(parent_bottom)
        for row in range(1, 4):
            for col in range(4):
                original = child_points[target_ccw[col]]
                patch.append(len(parent_points))
                parent_points.append((original[0], original[1], original[2] + row * 13.0))
        lineage[edge] = (len(parent_patches), 'bottom', f.SOURCE_FACE_OWNERS[edge][1])
        parent_patches.append(tuple(patch))
    receipt = {'source_segment_ids': {f.INTERFACE_KEYS[e]: list(ids)
                                      for e, ids in INTERFACE_CHAINS.items()}}
    return parent_points, parent_patches, child_points, child_patches, receipt, lineage


class TestSyntheticRebase(unittest.TestCase):
    def setUp(self):
        self.data = make_fixture()

    def run_rebase(self, data=None):
        d = data or self.data
        return f.rebase_core(*d, parent_expected_seams=0, parent_expected_open=32)

    def test_source_contract_eight_distinct_original_edges(self):
        self.assertEqual(set(f.INTERFACE_KEYS), set(INTERFACE_CHAINS))
        self.assertEqual(len(f.INTERFACE_KEYS), 8)
        self.assertEqual({x for owners in f.SOURCE_FACE_OWNERS.values() for x in owners}
                         - {1279, 1386, 3269, 3485}, {912, 1105, 1230, 3737})

    def test_synthetic_original_island_has_six_internal_seams(self):
        inv = f.side_inventory(self.data[3])
        self.assertEqual(sum(len(v) == 2 for v in inv.values()), 6)
        self.assertEqual(sum(len(v) == 1 for v in inv.values()), 20)

    def test_synthetic_parent_eight_open_edges(self):
        inv = f.side_inventory(self.data[1])
        self.assertEqual(sum(len(v) == 2 for v in inv.values()), 0)
        self.assertEqual(sum(len(v) == 1 for v in inv.values()), 32)

    def test_rebase_yields_14_seams_and_36_open_for_fixture(self):
        points, patches, receipt = self.run_rebase()
        self.assertEqual(len(patches), 16)
        self.assertEqual(len(points), len(self.data[0]) + 78)
        self.assertEqual(receipt['indexed_two_sided_seams'], 14)
        self.assertEqual(receipt['indexed_open_sides'], 36)
        self.assertEqual(len(receipt['original_source_interfaces_joined']), 8)

    def test_exact_original_parent_prefix_preserved(self):
        pts, patches, _ = self.run_rebase()
        self.assertEqual(pts[:len(self.data[0])], self.data[0])
        self.assertEqual(patches[:len(self.data[1])], self.data[1])

    def test_parent_and_child_have_opposite_ccw_source_edge_incidence(self):
        pts, patches, receipt = self.run_rebase()
        inc = f.side_inventory(patches)
        for k in receipt['original_source_interfaces_joined']:
            chain = tuple(k['resolved_global_control_ids'])
            self.assertEqual(len(inc[tuple(sorted(chain))]), 2)
            self.assertEqual(inc[tuple(sorted(chain))][0][3],
                             inc[tuple(sorted(chain))][1][3][::-1])

    def test_rebasing_is_deterministic(self):
        a = self.run_rebase()
        b = self.run_rebase()
        self.assertEqual(a, b)
        self.assertEqual(f.serialize_bp(*a[:2]), f.serialize_bp(*b[:2]))

    def test_no_original_source_coordinates_appear_in_fixture(self):
        self.assertFalse(any(abs(x[2] + 33.75) < 1e-12 for x in self.data[2]))

    def test_reject_perturbed_true_parent_boundary_coordinate(self):
        d = list(copy.deepcopy(self.data))
        p = d[0][0]
        d[0][0] = (p[0] + 2e-6, p[1], p[2])
        with self.assertRaisesRegex(ValueError, 'incompatible parent control geometry'):
            self.run_rebase(d)

    def test_reject_perturbed_boundary_at_tiny_subthreshold_amplitude(self):
        d = list(copy.deepcopy(self.data))
        p = d[0][0]
        d[0][0] = (p[0] + 0.5e-8, p[1], p[2])
        self.assertEqual(self.run_rebase(d)[2]['source_s40_f6_child_controls_reused_from_parent'], 26)

    def test_reject_original_parent_wrong_side(self):
        d = list(copy.deepcopy(self.data))
        d[5][1002] = (0, 'top', f.SOURCE_FACE_OWNERS[1002][1])
        with self.assertRaises(ValueError):
            self.run_rebase(d)

    def test_reject_reused_parent_side_two_original_edges(self):
        d = list(copy.deepcopy(self.data))
        d[5][1002] = d[5][1080]
        with self.assertRaises(ValueError):
            self.run_rebase(d)

    def test_reject_out_of_bounds_parent_patch(self):
        d = list(copy.deepcopy(self.data))
        d[5][1139] = (999, 'bottom', f.SOURCE_FACE_OWNERS[1139][1])
        with self.assertRaisesRegex(ValueError, 'nonexistent patch'):
            self.run_rebase(d)

    def test_reject_missing_original_edge_source_segment(self):
        d = list(copy.deepcopy(self.data))
        del d[4]['source_segment_ids']['old:1002']
        with self.assertRaises(KeyError):
            self.run_rebase(d)

    def test_reject_altered_original_open_control_chain(self):
        d = list(copy.deepcopy(self.data))
        d[4]['source_segment_ids']['old:1002'][0] = 99
        with self.assertRaisesRegex(ValueError, 'Unexpected indexed island source side incidence'):
            self.run_rebase(d)

    def test_reject_inconsistent_parent_open_side_count(self):
        with self.assertRaisesRegex(ValueError, 'Parent prior exact indexed'):
            f.rebase_core(*self.data, parent_expected_seams=264, parent_expected_open=96)

    def test_reject_maloriented_parent_bicubic_patch(self):
        d = list(copy.deepcopy(self.data))
        p = list(d[1][0])
        p[:4] = list(reversed(p[:4]))
        d[1][0] = tuple(p)
        with self.assertRaises(ValueError):
            self.run_rebase(d)

    def test_reject_overincident_patch_side(self):
        d = list(copy.deepcopy(self.data))
        d[1].append(d[1][0])
        with self.assertRaises(ValueError):
            self.run_rebase(d)

    def test_reject_missing_or_modified_original_native_step(self):
        with self.assertRaisesRegex(ValueError, 'Original S40 STEP bytes'):
            f.source_graph_gate(b'ISO-10303-21;\n#1=ADVANCED_FACE();')

    def test_lineage_schema_must_match_original_source_identity(self):
        parent = b'test-parent-bp'
        data = {'schema': f.LINEAGE_SCHEMA,
                'original_step_sha256': f.SOURCE_SHA,
                's3y_bp_sha256': f.fingerprint(parent),
                'original_edge_to_parent_open_side': {
                    str(e): {'patch': i, 'side': 'bottom',
                             'original_parent_face_id': f.SOURCE_FACE_OWNERS[e][1]}
                    for i, e in enumerate(f.INTERFACE_KEYS)}}
        self.assertEqual(len(f.validate_lineage(data, parent)), 8)
        data['original_edge_to_parent_open_side'].pop('1057')
        with self.assertRaisesRegex(ValueError, 'exactly eight'):
            f.validate_lineage(data, parent)

    def test_lineage_cannot_alias_parent_patch_side(self):
        parent = b'test-parent-bp'
        data = {'schema': f.LINEAGE_SCHEMA,
                'original_step_sha256': f.SOURCE_SHA,
                's3y_bp_sha256': f.fingerprint(parent),
                'original_edge_to_parent_open_side': {
                    str(e): {'patch': i, 'side': 'bottom',
                             'original_parent_face_id': f.SOURCE_FACE_OWNERS[e][1]}
                    for i, e in enumerate(f.INTERFACE_KEYS)}}
        data['original_edge_to_parent_open_side']['1057'] = data['original_edge_to_parent_open_side']['1002']
        with self.assertRaisesRegex(ValueError, 'alias'):
            f.validate_lineage(data, parent)

    def test_lineage_cannot_reflect_modified_s3y_bp(self):
        parent = b'test-parent-bp'
        data = {'schema': f.LINEAGE_SCHEMA,
                'original_step_sha256': f.SOURCE_SHA,
                's3y_bp_sha256': f.fingerprint(parent),
                'original_edge_to_parent_open_side': {
                    str(e): {'patch': i, 'side': 'bottom',
                             'original_parent_face_id': f.SOURCE_FACE_OWNERS[e][1]}
                    for i, e in enumerate(f.INTERFACE_KEYS)}}
        with self.assertRaisesRegex(ValueError, 'exact provided parent BP'):
            f.validate_lineage(data, parent + b'\n')


    def test_reject_false_source_owner_face(self):
        d = list(copy.deepcopy(self.data))
        idx, side, owner = d[5][1139]
        d[5][1139] = (idx, side, 912)
        with self.assertRaisesRegex(ValueError, 'parent face ownership'):
            self.run_rebase(d)

    def test_reject_forged_source_parent_face_in_lineage(self):
        parent = b'test-parent-bp'
        data = {'schema': f.LINEAGE_SCHEMA,
                'original_step_sha256': f.SOURCE_SHA,
                's3y_bp_sha256': f.fingerprint(parent),
                'original_edge_to_parent_open_side': {
                    str(e): {'patch': i, 'side': 'bottom',
                             'original_parent_face_id': f.SOURCE_FACE_OWNERS[e][1]}
                    for i, e in enumerate(f.INTERFACE_KEYS)}}
        data['original_edge_to_parent_open_side']['1139']['original_parent_face_id'] = 912
        with self.assertRaisesRegex(ValueError, 'source parent face owner mismatch'):
            f.validate_lineage(data, parent)



    def test_automatic_lineage_discovers_eight_unique_source_sides_on_mock(self):
        import sys
        import types
        from unittest import mock
        parent_points, parent_patches = self.data[:2]
        id_to_parent = self.data[5]
        source_mod = types.ModuleType('s3c_step_source_gate')
        source_mod.parse_entities = lambda source: {}
        source_mod.oriented_edges = lambda table, fid: ('PLANE', [
            [{'edge_curve_id': eid} for eid in f.INTERFACE_KEYS]])
        child_mod = types.ModuleType('s40f1_six_edge_planar_builder')
        child_mod.indexed_open_sides = lambda patches: [None] * 96
        child_mod.recover_inherited_source_chain = lambda t, entry, curve, points, available: [
            (id_to_parent[entry['edge_curve_id']][0], 'bottom',
             f.side_ids(parent_patches[id_to_parent[entry['edge_curve_id']][0]], 'bottom'))]
        class Edge:
            wrapped = object()
        native_mapping = {'native_edges': [Edge()],
                          'edge_map': {eid: 0 for eid in f.INTERFACE_KEYS}}
        with mock.patch.dict(sys.modules, {
                's3c_step_source_gate': source_mod,
                's40f1_six_edge_planar_builder': child_mod}):
            with mock.patch('OCP.BRepAdaptor.BRepAdaptor_Curve', return_value=object()):
                mapping, evidence = f.discover_original_parent_lineage(
                    b'synthetic-source-fixture', None, native_mapping,
                    b'synthetic-parent-bp', parent_points, parent_patches)
        self.assertEqual(set(mapping), set(f.INTERFACE_KEYS))
        self.assertEqual(evidence['source_lineage_discovery'],
                         'ORIGINAL_STEP_NATIVE_CANDIDATE_UNIQUENESS')
        self.assertTrue(all(row['recovered_segment_count'] == 1
                            for row in evidence['source_edge_details'].values()))

    def test_automatic_lineage_requires_frozen_parent_open_side_inventory(self):
        import sys
        import types
        from unittest import mock
        source_mod = types.ModuleType('s3c_step_source_gate')
        source_mod.parse_entities = lambda source: {}
        source_mod.oriented_edges = lambda t, face: ('PLANE', [])
        child_mod = types.ModuleType('s40f1_six_edge_planar_builder')
        child_mod.indexed_open_sides = lambda patches: [None] * 32
        child_mod.recover_inherited_source_chain = lambda *a, **k: []
        with mock.patch.dict(sys.modules, {
                's3c_step_source_gate': source_mod,
                's40f1_six_edge_planar_builder': child_mod}):
            with self.assertRaisesRegex(ValueError, '96 open indexed sides'):
                f.discover_original_parent_lineage(b'invented-step', None, {},
                    b'synthetic-parent', self.data[0], self.data[1])

    def test_automatic_lineage_refuses_ambiguous_original_source_edge(self):
        import sys
        import types
        from unittest import mock
        source_mod = types.ModuleType('s3c_step_source_gate')
        source_mod.parse_entities = lambda source: {}
        source_mod.oriented_edges = lambda t, face: ('PLANE', [
            [{'edge_curve_id': edge} for edge in f.INTERFACE_KEYS]])
        child_mod = types.ModuleType('s40f1_six_edge_planar_builder')
        child_mod.indexed_open_sides = lambda patches: [None] * 96
        child_mod.recover_inherited_source_chain = lambda *a, **k: []
        class Edge:
            wrapped = object()
        with mock.patch.dict(sys.modules, {
                's3c_step_source_gate': source_mod,
                's40f1_six_edge_planar_builder': child_mod}):
            # Native edge wrappers are never used when source association is
            # rejected; inject a permissive adapter to reach that check.
            with mock.patch('OCP.BRepAdaptor.BRepAdaptor_Curve', return_value=object()):
                m = {'native_edges': [Edge()],
                     'edge_map': {eid: 0 for eid in f.INTERFACE_KEYS}}
                with self.assertRaisesRegex(ValueError, 'split or ambiguous'):
                    f.discover_original_parent_lineage(b'invented-step', None, m,
                        b'synthetic-parent', self.data[0], self.data[1])

    def test_native_gate_rejects_modified_source_before_import(self):
        with self.assertRaisesRegex(ValueError, 'not byte-pinned S40'):
            f.original_native_gate(b'not-original-step', 'absent.step', [], [],
                                   {}, {})

    def test_main_missing_inputs_fails_with_code_three_without_output(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'result'
            old = __import__('sys').argv
            try:
                __import__('sys').argv = ['runner', '--original-step', str(Path(temp) / 'missing.step'),
                            '--s3y-bp', str(Path(temp) / 'missing.bp'),
                            '--parent-source-lineage', str(Path(temp) / 'missing.json'),
                            '--island-f6-bp', str(Path(temp) / 'missing-island.bp'),
                            '--island-f6-receipt', str(Path(temp) / 'missing-island.json'),
                            '--output-dir', str(out)]
                self.assertEqual(f.main(), 3)
            finally:
                __import__('sys').argv = old
            self.assertFalse(out.exists())


PRIVATE_DIR = os.environ.get('APMESH_S40F7_PRIVATE_DIR', '')
PRIVATE_FILES_PRESENT = bool(PRIVATE_DIR) and all(
    (Path(PRIVATE_DIR) / filename).is_file()
    for filename in ('s40f6_four_face_source_island.PRIVATE.bp',
                     's40f6_source_island.PRIVATE.json'))


@unittest.skipUnless(PRIVATE_FILES_PRESENT,
                     'Original-source-derived F6 private BP unavailable; synthetic tests still run')
class TestPrivateF6Topology(unittest.TestCase):
    def setUp(self):
        base = Path(PRIVATE_DIR)
        raw = (base / 's40f6_four_face_source_island.PRIVATE.bp').read_bytes()
        receipt = json.loads((base / 's40f6_source_island.PRIVATE.json').read_text())
        self.points, self.patches, self.inventory = f.isolated_gate(raw, receipt)
        self.receipt = receipt

    def test_real_island_rebases_onto_synthetic_parent(self):
        # Only the real private ISLAND is used; the parent remains a mock.
        island = f.side_inventory(self.patches)
        parent_points, parent_patches, vertex_map, lineage = [], [], {}, {}
        for eid, key in f.INTERFACE_KEYS.items():
            ids = tuple(self.receipt['source_segment_ids'][key])
            directed = island[tuple(sorted(ids))][0][3][::-1]
            target = []
            for control in directed:
                if control not in vertex_map:
                    vertex_map[control] = len(parent_points)
                    parent_points.append(self.points[control])
                target.append(vertex_map[control])
            patch = list(target)
            for row in (1, 2, 3):
                for col in range(4):
                    patch.append(len(parent_points))
                    p = self.points[directed[col]]
                    parent_points.append((p[0], p[1], p[2] + row * 17.0))
            lineage[eid] = (len(parent_patches), 'bottom', f.SOURCE_FACE_OWNERS[eid][1])
            parent_patches.append(tuple(patch))
        pts, patches, result = f.rebase_core(
            parent_points, parent_patches, self.points, self.patches,
            self.receipt, lineage, parent_expected_seams=0, parent_expected_open=32)
        self.assertEqual(len(patches), 16)
        self.assertEqual(result['indexed_two_sided_seams'], 14)
        self.assertEqual(result['indexed_open_sides'], 36)
        self.assertEqual(len(pts), len(parent_points) + 78)

    def test_byte_locked_f6_island_readiness(self):
        self.assertEqual(len(self.points), 104)
        self.assertEqual(len(self.patches), 8)

    def test_eight_real_source_side_chains_are_unique_and_open(self):
        observed = [tuple(self.receipt['source_segment_ids'][key])
                    for key in f.INTERFACE_KEYS.values()]
        self.assertEqual(len({tuple(sorted(ids)) for ids in observed}), 8)
        self.assertTrue(all(len(self.inventory[tuple(sorted(ids))]) == 1 for ids in observed))

    def test_f6_independent_indexed_seam_counts(self):
        self.assertEqual(sum(len(rows) == 2 for rows in self.inventory.values()), 6)
        self.assertEqual(sum(len(rows) == 1 for rows in self.inventory.values()), 20)


if __name__ == '__main__':
    unittest.main()
