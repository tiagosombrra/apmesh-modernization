#!/usr/bin/env python3
"""Hermetic negative and positive tests for the F27 code-only scientific checker."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

import thingi10k_f27_native_tri_evidence as f27

TETRA = [(0, 2, 1), (0, 1, 3), (0, 3, 2), (1, 2, 3)]


class TopologyTests(unittest.TestCase):
    def test_01_tetra_is_closed_and_spherical(self):
        r = f27.topology(4, TETRA)
        self.assertEqual((r['components'], r['boundary_edges'], r['euler']), (1, 0, 2))
        self.assertEqual((r['vertex_link_cycles'], r['nonmanifold_vertex_links']), (4, 0))

    def test_02_two_disconnected_tetrahedra(self):
        r = f27.topology(8, TETRA + [tuple(v + 4 for v in x) for x in TETRA])
        self.assertEqual((r['components'], r['euler'], r['vertex_link_cycles']), (2, 4, 8))

    def test_03_open_disk_is_not_a_closed_mesh(self):
        r = f27.topology(4, [(0, 1, 2), (0, 2, 3)])
        self.assertEqual((r['components'], r['euler'], r['boundary_edges']), (1, 1, 4))
        self.assertEqual((r['vertex_link_paths'], r['nonmanifold_vertex_links']), (4, 0))

    def test_04_independent_triangles_remain_disconnected(self):
        r = f27.topology(6, [(0, 1, 2), (3, 4, 5)])
        self.assertEqual((r['components'], r['boundary_edges']), (2, 6))

    def test_05_orientation_conflict_is_detected(self):
        r = f27.topology(4, [(0, 1, 2), (0, 1, 3)])
        self.assertEqual(r['winding_conflicts'], 1)

    def test_06_high_incidence_is_detected(self):
        r = f27.topology(5, [(0, 1, 2), (1, 0, 3), (0, 1, 4)])
        self.assertEqual(r['high_incidence_edges'], 1)

    def test_07_bow_tie_vertex_link_is_detected(self):
        r = f27.topology(5, [(0, 1, 2), (0, 3, 4)])
        self.assertEqual(r['nonmanifold_vertex_links'], 1)

    def test_08_duplicate_face_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            f27.topology(3, [(0, 1, 2), (1, 2, 0)])

    def test_09_repeated_vertex_in_face_rejected(self):
        with self.assertRaises(ValueError):
            f27.topology(3, [(0, 1, 1)])

    def test_10_negative_index_rejected(self):
        with self.assertRaises(ValueError):
            f27.topology(3, [(0, -1, 2)])

    def test_11_out_of_range_index_rejected(self):
        with self.assertRaises(ValueError):
            f27.topology(3, [(0, 1, 3)])

    def test_12_nonpositive_vertex_count_rejected(self):
        with self.assertRaises(ValueError):
            f27.topology(0, [])

    def test_13_exact_coordinate_weld_changes_only_connectivity(self):
        vertices = [(0., 0., 0.), (1., 0., 0.), (0., 1., 0.),
                    (0., 0., 0.), (0., 1., 0.), (-1., 0., 0.)]
        faces = [(0, 1, 2), (3, 4, 5)]
        raw = f27.topology(len(vertices), faces)
        welded, dropped = f27.welded_by_exact_exported_xyz(vertices, faces)
        self.assertEqual((raw['components'], welded['components'], dropped), (2, 1, 2))
        self.assertEqual(len(faces), welded['faces'])

    def test_14_nearby_but_distinct_coordinates_are_not_welded(self):
        vertices = [(0., 0., 0.), (1., 0., 0.), (0., 1., 0.),
                    (0., 0., 1e-12), (0., 1., 0.), (-1., 0., 0.)]
        faces = [(0, 1, 2), (3, 4, 5)]
        _, dropped = f27.welded_by_exact_exported_xyz(vertices, faces)
        self.assertEqual(dropped, 1)


class GeometryAndInputTests(unittest.TestCase):
    def test_15_quality_of_equilateral_triangle_is_one(self):
        value = f27.triangle_quality(((0., 0.), (1., 0.), (.5, math.sqrt(3)/2)))
        self.assertAlmostEqual(value, 1., places=12)

    def test_16_quality_of_right_isosceles_triangle(self):
        value = f27.triangle_quality(((0., 0.), (1., 0.), (0., 1.)))
        self.assertAlmostEqual(value, .8284271247461901, places=12)

    def test_17_degenerate_triangle_rejected(self):
        with self.assertRaises(ValueError):
            f27.triangle_quality(((0., 0.), (1., 0.), (2., 0.)))

    def test_18_zero_edges_rejected(self):
        with self.assertRaises(ValueError):
            f27.triangle_quality(((0., 0.), (0., 0.), (0., 0.)))

    def test_19_duplicate_json_field_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"a":1,"a":2}', object_pairs_hook=f27.unique_object)

    def test_20_bad_zip_rejected_without_source_promotion(self):
        with tempfile.TemporaryDirectory() as temp:
            z = Path(temp)/'sample.zip'
            z.write_bytes(b'not a valid original ZIP')
            with self.assertRaises(ValueError):
                f27.parse_source(z)

    def test_21_false_original_zip_blob_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            z = Path(temp)/'source.zip'
            with ZipFile(z, 'w', compression=ZIP_DEFLATED) as stream:
                stream.writestr('293137.stl', b'bad')
            with self.assertRaises(ValueError):
                f27.parse_source(z)

    def test_22_wrong_bp_digest_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'trial.bp'
            p.write_bytes(b'x' * 538482)
            with self.assertRaises(ValueError):
                f27.parse_bp(p)

    def test_23_fake_accepted_state_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'trial.log'
            p.write_text('step=0\naccepted=0\n')
            with self.assertRaises(ValueError):
                f27.parse_acceptance(p)

    def test_24_duplicate_accepted_log_key_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'trial.log'
            p.write_text('step=0\nstep=0\naccepted=1\n')
            with self.assertRaises(ValueError):
                f27.parse_acceptance(p)

    def test_25_rejected_budget_cannot_be_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'trial.log'
            p.write_text('step=0\naccepted=1\nbudget_final_status=rejected\n')
            with self.assertRaises(ValueError):
                f27.parse_acceptance(p)

    def test_26_malformed_metric_header_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'data.csv'
            p.write_text('step,nodes,nodes\n0,1,2\n')
            with self.assertRaises(ValueError):
                f27.parse_metrics(p)

    def test_27_multiple_metric_rows_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'data.csv'
            p.write_text('step,nodes\n0,1\n1,2\n')
            with self.assertRaises(ValueError):
                f27.parse_metrics(p)

    def test_28_valid_minimal_obj_is_parsed(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'a.obj'
            p.write_text('# generated\nv 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n')
            vertices, faces = f27.parse_obj(p)
            self.assertEqual((len(vertices), faces), (3, [(0, 1, 2)]))

    def test_29_obj_nan_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'a.obj'
            p.write_text('v nan 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n')
            with self.assertRaises(ValueError):
                f27.parse_obj(p)

    def test_30_obj_quad_face_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'a.obj'
            p.write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\nv 1 1 0\nf 1 2 3 4\n')
            with self.assertRaises(ValueError):
                f27.parse_obj(p)

    def test_31_obj_forward_reference_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'a.obj'
            p.write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 4\n')
            with self.assertRaises(ValueError):
                f27.parse_obj(p)

    def test_32_obj_slash_reference_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'a.obj'
            p.write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1/1 2/2 3/3\n')
            with self.assertRaises(ValueError):
                f27.parse_obj(p)

    def test_33_unsupported_obj_record_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'a.obj'
            p.write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\nvt 0 0\nf 1 2 3\n')
            with self.assertRaises(ValueError):
                f27.parse_obj(p)

    def test_34_empty_obj_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'a.obj'
            p.write_text('# empty\n')
            with self.assertRaises(ValueError):
                f27.parse_obj(p)

    def test_35_hash_gate_uses_original_git_object_framing(self):
        self.assertEqual(f27.git_blob(b''), 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')

    def test_36_repeats_only_pass_with_identical_artifact_bytes(self):
        row = {'status': 'NATIVE_TRI_STAGE0_ACCEPTED_INDEXED_TOPOLOGY_NOT_GLOBALLY_STITCHED',
               'artifact_sha256': {'obj': 'abc'}, 'native_obj_indexed_topology': {},
               'exact_xyz_welded_topology_diagnostic_not_native_output': {},
               'quality': {}, 'geometry': {}, 'original_stl_tri_quality': {}}
        self.assertTrue(f27.compare_runs(row, row.copy())['four_scientific_artifact_hashes_byte_identical'])
        altered = copy.deepcopy(row)
        altered['artifact_sha256'] = {'obj': 'def'}
        with self.assertRaises(ValueError):
            f27.compare_runs(row, altered)

    def test_37_repeat_quality_change_rejected(self):
        row = {'status': 'NATIVE_TRI_STAGE0_ACCEPTED_INDEXED_TOPOLOGY_NOT_GLOBALLY_STITCHED',
               'artifact_sha256': {'obj': 'abc'}, 'native_obj_indexed_topology': {},
               'exact_xyz_welded_topology_diagnostic_not_native_output': {},
               'quality': {'minimum': .2}, 'geometry': {}, 'original_stl_tri_quality': {}}
        altered = copy.deepcopy(row)
        altered['quality']['minimum'] = .3
        with self.assertRaises(ValueError):
            f27.compare_runs(row, altered)

    def test_38_empty_source_faces_not_admitted_as_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            with self.assertRaises(ValueError):
                f27.inspect(path, path, path)


class NativeProvenanceTests(unittest.TestCase):
    def test_39_profile_contains_only_frozen_input_and_output_relocation(self):
        data = f27.input_config(Path('/private/original.bp'), Path('/private/run'))
        self.assertIn('INPUT_MODEL=/private/original.bp\n', data)
        self.assertIn('OUTPUT_PREFIX=/private/run/bunny\n', data)
        self.assertIn('ADAPTIVE_MAX_STEPS=2\n', data)
        self.assertIn('WRITE_MODE=h\n', data)
        self.assertEqual(data.count('=') , len(f27.NATIVE_PROFILE) + 2)

    def test_40_relative_source_path_not_allowed(self):
        with self.assertRaises(ValueError):
            f27.input_config(Path('model.bp'), Path('/private/run'))

    def test_41_relative_run_path_not_allowed(self):
        with self.assertRaises(ValueError):
            f27.input_config(Path('/private/source.bp'), Path('output'))

    def test_42_missing_real_process_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            with self.assertRaises(ValueError):
                f27.verify_native_process_record(run, Path('/private/model.bp'))

    def test_43_process_nonzero_code_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            bp = Path('/private/model.bp')
            config = run/'case.conf'
            config.write_text(f27.input_config(bp, run))
            (run/'stdout.log').write_bytes(b'output')
            (run/'stderr.log').write_bytes(b'error')
            receipt = {'status': 'completed', 'native_exit_code': 1,
                       'binary_sha256': f27.NATIVE_CLI_SHA256,
                       'bp_sha256': f27.BP_SHA256,
                       'config_sha256': f27.sha256(config),
                       'stdout_sha256': f27.sha256(run/'stdout.log'),
                       'stderr_sha256': f27.sha256(run/'stderr.log'),
                       'wall_seconds': 1.0}
            (run/'process.json').write_text(json.dumps(receipt))
            with self.assertRaises(ValueError):
                f27.verify_native_process_record(run, bp)

    def test_44_process_stdout_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            bp = Path('/private/model.bp')
            config = run/'case.conf'
            config.write_text(f27.input_config(bp, run))
            (run/'stdout.log').write_bytes(b'original')
            (run/'stderr.log').write_bytes(b'')
            receipt = {'status': 'completed', 'native_exit_code': 0,
                       'binary_sha256': f27.NATIVE_CLI_SHA256,
                       'bp_sha256': f27.BP_SHA256,
                       'config_sha256': f27.sha256(config),
                       'stdout_sha256': f27.sha256(run/'stdout.log'),
                       'stderr_sha256': f27.sha256(run/'stderr.log'),
                       'wall_seconds': 1.0}
            (run/'process.json').write_text(json.dumps(receipt))
            (run/'stdout.log').write_bytes(b'altered')
            with self.assertRaises(ValueError):
                f27.verify_native_process_record(run, bp)

    def test_45_process_config_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            bp = Path('/private/model.bp')
            (run/'case.conf').write_text(f27.input_config(bp, run).replace(
                'ADAPTIVE_INTENSITY=0.02', 'ADAPTIVE_INTENSITY=0.99'))
            (run/'process.json').write_text('{}')
            with self.assertRaises(ValueError):
                f27.verify_native_process_record(run, bp)

    def test_46_unverified_binary_cannot_launch_original_engine(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate = root/'binary'
            candidate.write_bytes(b'not an original engine binary')
            with self.assertRaises(ValueError):
                f27.run_original_cli(candidate, root/'private.bp', root/'run')
            self.assertFalse((root/'run').exists())

    def test_47_changed_original_quality_denies_repetition(self):
        row = {'status': 'NATIVE_TRI_STAGE0_ACCEPTED_INDEXED_TOPOLOGY_NOT_GLOBALLY_STITCHED',
               'artifact_sha256': {'obj': 'abc'}, 'native_obj_indexed_topology': {},
               'exact_xyz_welded_topology_diagnostic_not_native_output': {},
               'quality': {}, 'geometry': {}, 'original_stl_tri_quality': {'mean': .7}}
        changed = copy.deepcopy(row)
        changed['original_stl_tri_quality']['mean'] = .71
        with self.assertRaises(ValueError):
            f27.compare_runs(row, changed)


if __name__ == '__main__':
    unittest.main()
