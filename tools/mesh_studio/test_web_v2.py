"""Read-only streaming V2 API regression against the original source JSON."""

from __future__ import annotations

import math
import unittest
from fastapi.testclient import TestClient

from .scene_transport_v2 import unpack_geometry_v2
from .web_api import app


class StreamingSourceTransportTests(unittest.TestCase):
    def setUp(self):
        self.api = TestClient(app)

    def test_p1_original_face_ids_and_tri_quad_inventory(self):
        for space in ('xyz', 'uv'):
            with self.subTest(space=space):
                r = self.api.get(f'/api/v1/models/p1/geometry.v2.bin?space={space}')
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r.headers['content-type'],
                                 'application/vnd.apmesh.geometry.v2')
                self.assertEqual(r.headers['x-visualization-only'],
                                 'float32-not-scientific-source')
                self.assertEqual(int(r.headers['content-length']), len(r.content))
                decoded = unpack_geometry_v2(r.content)
                original = self.api.get(f'/api/v1/models/p1/geometry?space={space}').json()
                self.assertEqual(decoded['source_sha256'], original['source_sha256'])
                self.assertEqual(decoded['source_face_ids'], original['source_face_ids'])
                self.assertEqual(decoded['cells'], original['cells'])
                self.assertEqual(decoded['triangles'], 36)
                self.assertEqual(decoded['quads'], 42)
                self.assertEqual(len(decoded['points']), len(original['points']))
                self.assertTrue(all(math.isclose(a, b, abs_tol=2e-7, rel_tol=2e-7)
                                    for p, q in zip(decoded['points'], original['points'])
                                    for a, b in zip(p, q)))

    def test_v2_all_staged_remain_unaccepted_by_catalog(self):
        catalog = {x['id']: x for x in self.api.get('/api/v1/models').json()['models']}
        for model in ('band', 'west', 'north', 'both'):
            with self.subTest(model=model):
                r = self.api.get(f'/api/v1/models/{model}/geometry.v2.bin?space=uv')
                self.assertEqual(r.status_code, 200)
                decoded = unpack_geometry_v2(r.content)
                self.assertEqual(len(decoded['cells']), catalog[model]['quads']+
                                 catalog[model]['triangles'])
                self.assertEqual(decoded['source_sha256'], catalog[model]['sha256'])
                self.assertEqual(catalog[model]['accepted_adaptive_epochs'], 0)
                self.assertEqual(catalog[model]['source_status'], 'STAGED_UNACCEPTED')

    def test_no_arbitrary_filesystem_or_unknown_coordinate_space(self):
        self.assertEqual(self.api.get('/api/v1/models/not-a-model/geometry.v2.bin').status_code, 404)
        self.assertEqual(self.api.get('/api/v1/models/p1/geometry.v2.bin?space=none').status_code, 422)
        self.assertEqual(self.api.post('/api/v1/models/p1/geometry.v2.bin').status_code, 405)

    def test_v1_remains_readable(self):
        r = self.api.get('/api/v1/models/p1/geometry.bin?space=xyz')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.content.startswith(b'APMSH001'))


if __name__ == '__main__':
    unittest.main()
