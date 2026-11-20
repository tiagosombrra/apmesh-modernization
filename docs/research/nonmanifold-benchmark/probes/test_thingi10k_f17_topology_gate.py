"""Hermetic checks for Euler/genus gating and fail-closed literature status."""
import copy
import unittest
from thingi10k_f17_topology_gate import (
    topology_invariants, verify_snapshot, QUADWILD_IDS, BADIA_IDS,
    EXPECTED_TREE_SHA, PINNED_MIRROR_REVISIONS,
)


def base(v=4, e=6, f=4):
    """Return a consistent orientable triangulated sphere fixture."""
    return {
        'source_triangles': f, 'source_unique_exact_vertices': v,
        'source_unique_exact_edges': e, 'edge_incidence_histogram': {'2': e},
        'boundary_edges': 0, 'two_face_edges': e, 'three_plus_edges': 0,
        'raw_duplicate_triangles': 0, 'zero_area_triangles': 0,
        'edge_winding_conflicts': 0, 'vertex_connected_components': 1,
        'vertex_link_interior': v, 'vertex_link_boundary': 0,
        'vertex_link_singular': 0,
    }


def sample_snapshot():
    """Create a 23-entry mocked roster and seven consistent toy source models."""
    ids = list(QUADWILD_IDS + BADIA_IDS)
    audited = [293137, 37881, 61394, 58012, 47076, 550964, 96457]
    files = []
    audits = []
    for n, idv in enumerate(ids):
        t = base()
        if idv == 61394:
            # Two tetrahedral shells sharing a spatially indexed vertex.
            t.update(source_triangles=8, source_unique_exact_vertices=7,
                     source_unique_exact_edges=12, edge_incidence_histogram={'2': 12},
                     two_face_edges=12, vertex_link_interior=6, vertex_link_singular=1)
        entry = {
            'thingi10k_file_id': idv,
            'literature_cohort': 'QUADWILD_FIG29' if idv in QUADWILD_IDS else 'BADIA_FIG10_TABLE1',
            'zip_git_blob_sha1': '%040x' % (idv + 1), 'zip_bytes': 99 + idv,
            'mirror_archive_repository': 'larsbrubaker/Thingi10K-meshes-1',
            'mirror_repository_number': 1,
            'mirror_pinned_commit': PINNED_MIRROR_REVISIONS[1],
            'source_archive_relative_path': f'meshes/{idv}.stl.zip',
            'original_stl_triangles_catalog': t['source_triangles'],
            'individual_license_independently_approved': False,
            'quadwild_per_id_output_pair_verified': False, 'apmesh_mesh_generated': False,
        }
        files.append(entry)
        if idv in audited:
            audits.append({'thingi10k_file_id': idv, 'zip_git_blob_sha1': entry['zip_git_blob_sha1'],
                           'zip_bytes': entry['zip_bytes'], 'raw_stl_sha256': '%064x' % (idv + 1),
                           'topology': t})
    return {'schema': 'apmesh-thingi10k-f17-source-git-tree-v1',
            'source_archive_git_tree_sha1': EXPECTED_TREE_SHA,
            'source_archives': files,
            'raw_stl_audits': sorted(audits, key=lambda x: audited.index(x['thingi10k_file_id']))}


class GenusGateTests(unittest.TestCase):
    def test_tetrahedron_is_genus_zero(self):
        t = topology_invariants(base())
        self.assertEqual((t['source_mesh_euler_characteristic_raw'], t['applicable_genus']), (2, 0))

    def test_torus_is_genus_one(self):
        t = topology_invariants(base(7, 21, 14))
        self.assertEqual((t['source_mesh_euler_characteristic_raw'], t['applicable_genus']), (0, 1))

    def test_high_genus_is_valid_when_structurally_supported(self):
        t = topology_invariants(base(9090, 27510, 18340))
        self.assertEqual(t['applicable_genus'], 41)

    def test_invalid_odd_euler_for_regular_closed_rejected(self):
        with self.assertRaisesRegex(ValueError, 'impossible Euler'):
            topology_invariants(base(5, 6, 4))

    def test_incidence_triples_corner_uses(self):
        x = base()
        x['edge_incidence_histogram'] = {'2': 5, '3': 1}
        with self.assertRaisesRegex(ValueError, 'corner edge uses'):
            topology_invariants(x)

    def test_manifold_edge_count_forgery(self):
        x = base()
        x['two_face_edges'] = 5
        with self.assertRaisesRegex(ValueError, 'class counts'):
            topology_invariants(x)

    def test_singular_vertex_blocks_genus(self):
        x = base()
        x['vertex_link_interior'] = 3
        x['vertex_link_singular'] = 1
        self.assertIsNone(topology_invariants(x)['applicable_genus'])

    def test_open_edge_blocks_genus(self):
        x = base()
        x['source_unique_exact_edges'] = 6
        x['edge_incidence_histogram'] = {'1': 2, '2': 4}
        x['boundary_edges'] = 2
        x['two_face_edges'] = 4
        x['source_triangles'] = 4
        # A fabricated 4-face assignment cannot use fewer than 12 edge incidences.
        with self.assertRaisesRegex(ValueError, 'corner edge uses'):
            topology_invariants(x)

    def test_duplicate_triangle_blocks_genus(self):
        x = base()
        x['raw_duplicate_triangles'] = 1
        self.assertIn('nonduplicated', topology_invariants(x)['failed_conditions'])

    def test_zero_area_blocks_genus(self):
        x = base()
        x['zero_area_triangles'] = 1
        self.assertIsNone(topology_invariants(x)['applicable_genus'])

    def test_multiple_components_blocks_genus(self):
        x = base()
        x['vertex_connected_components'] = 2
        self.assertIsNone(topology_invariants(x)['applicable_genus'])

    def test_corrupt_link_total_rejected(self):
        x = base()
        x['vertex_link_interior'] = 3
        with self.assertRaisesRegex(ValueError, 'link category totals'):
            topology_invariants(x)

    def test_accepts_frozen_roster_and_preserves_adversarial(self):
        report = verify_snapshot(sample_snapshot())
        self.assertEqual(report['manifest_entries'], 23)
        self.assertEqual(report['audited_original_stl_files'], 7)
        self.assertIsNone(report['topology_invariants']['61394']['applicable_genus'])

    def test_rejects_changed_unmeasured_model_id(self):
        s = sample_snapshot()
        s['source_archives'][-1]['thingi10k_file_id'] = 888888
        with self.assertRaisesRegex(ValueError, 'Unexpected frozen literature ID'):
            verify_snapshot(s)

    def test_rejects_wrong_git_tree_identity(self):
        s = sample_snapshot()
        s['source_archive_git_tree_sha1'] = {'1': 'x'}
        with self.assertRaisesRegex(ValueError, 'Git source tree'):
            verify_snapshot(s)

    def test_rejects_source_repo_path_substitution(self):
        s = sample_snapshot()
        s['source_archives'][0]['source_archive_relative_path'] = 'meshes/anything.stl.zip'
        with self.assertRaisesRegex(ValueError, 'source mesh archive path'):
            verify_snapshot(s)

    def test_rejects_missing_roster_id(self):
        s = sample_snapshot()
        s['source_archives'].pop()
        with self.assertRaisesRegex(ValueError, 'Exactly 23'):
            verify_snapshot(s)

    def test_rejects_early_apmesh_claim(self):
        s = sample_snapshot()
        s['source_archives'][0]['apmesh_mesh_generated'] = True
        with self.assertRaisesRegex(ValueError, 'Premature APMesh'):
            verify_snapshot(s)

    def test_rejects_wrong_archive_digest(self):
        s = sample_snapshot()
        s['raw_stl_audits'][0]['zip_git_blob_sha1'] = 'a'*40
        with self.assertRaisesRegex(ValueError, 'Archive identity mismatch'):
            verify_snapshot(s)

    def test_rejects_wrong_triangle_count(self):
        s = sample_snapshot()
        next(e for e in s['source_archives'] if e['thingi10k_file_id'] == 293137)['original_stl_triangles_catalog'] += 1
        with self.assertRaisesRegex(ValueError, 'Triangle count mismatch'):
            verify_snapshot(s)

    def test_rejects_incomplete_hash(self):
        s = sample_snapshot()
        s['raw_stl_audits'][0]['raw_stl_sha256'] = 'none'
        with self.assertRaisesRegex(ValueError, 'Raw STL hash'):
            verify_snapshot(s)


if __name__ == '__main__':
    unittest.main()
