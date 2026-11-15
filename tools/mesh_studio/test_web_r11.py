"""R1.1/R2 controls for visualization-only binary transport and source identity."""
from __future__ import annotations

from copy import deepcopy
import json
import math
import struct
import unittest

from fastapi.testclient import TestClient

from .scene_transport import (HEADER, MAGIC, SceneTransportError,
                              pack_geometry, unpack_geometry)
from .web_api import app, geometry


class BinaryTransportTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_transport_preserves_five_real_models_and_both_spaces(self):
        for name in ('p1', 'band', 'west', 'north', 'both'):
            for space in ('xyz', 'uv'):
                with self.subTest(model=name, space=space):
                    old = self.client.get(f'/api/v1/models/{name}/geometry?space={space}')
                    new = self.client.get(f'/api/v1/models/{name}/geometry.bin?space={space}')
                    self.assertEqual(old.status_code, 200)
                    self.assertEqual(new.status_code, 200)
                    self.assertEqual(new.headers['content-type'], 'application/vnd.apmesh.geometry.v1')
                    self.assertEqual(new.headers['x-source-sha256'], old.json()['source_sha256'])
                    result = unpack_geometry(new.content)
                    self.assertEqual(result['source_face_ids'], old.json()['source_face_ids'])
                    self.assertEqual(result['cells'], old.json()['cells'])
                    self.assertEqual(result['cell_types'], old.json()['cell_types'])
                    self.assertEqual(result['source_sha256'], old.json()['source_sha256'])
                    self.assertEqual(result['coordinate_space'], space)
                    self.assertEqual(len(result['points']), len(old.json()['points']))
                    for a, b in zip(result['points'], old.json()['points']):
                        self.assertLess(math.dist(a, b), 1e-5)
                    self.assertLess(len(new.content), len(old.content))

    def test_deterministic_wire_encoding(self):
        data = geometry('p1', 'uv')
        self.assertEqual(pack_geometry(data), pack_geometry(deepcopy(data)))
        self.assertEqual(unpack_geometry(pack_geometry(data))['source_face_ids'],
                         data['source_face_ids'])

    def test_bad_header_and_truncation_rejected(self):
        binary = pack_geometry(geometry('p1', 'xyz'))
        with self.assertRaises(SceneTransportError):
            unpack_geometry(b'BADMAGIC' + binary[8:])
        with self.assertRaises(SceneTransportError):
            unpack_geometry(binary[:-1])
        with self.assertRaises(SceneTransportError):
            unpack_geometry(binary[:15])
        self.assertEqual(HEADER.unpack_from(binary)[0], MAGIC)

    def test_source_id_or_type_mutation_fails_closed(self):
        real = geometry('p1', 'xyz')
        bad = deepcopy(real)
        bad['source_face_ids'][0] = bad['source_face_ids'][1]
        with self.assertRaisesRegex(SceneTransportError, 'invalid_source_face_ids'):
            pack_geometry(bad)
        bad = deepcopy(real)
        bad['cell_types'][0] = 'quad'
        with self.assertRaises(SceneTransportError):
            pack_geometry(bad)
        bad = deepcopy(real)
        bad['points'][0][0] = float('nan')
        with self.assertRaises(SceneTransportError):
            pack_geometry(bad)

    def test_binary_polygons_and_indices_are_rejected(self):
        binary = bytearray(pack_geometry(geometry('p1', 'uv')))
        _, meta_len, points, _, words = HEADER.unpack_from(binary)
        offset = HEADER.size + meta_len + points * 12
        struct.pack_into('<I', binary, offset, 99)
        with self.assertRaisesRegex(SceneTransportError, 'invalid_binary_polys'):
            unpack_geometry(binary)
        self.assertGreater(words, 0)

    def test_unknown_model_and_bad_space_do_not_return_bytes(self):
        for url, status in (
            ('/api/v1/models/unknown/geometry.bin', 404),
            ('/api/v1/models/p1/geometry.bin?space=physical', 422),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status)

    def test_binary_is_smaller_than_json_on_all_source_models(self):
        for name in ('p1','band','west','north','both'):
            json_data = geometry(name,'uv')
            wire = pack_geometry(json_data)
            self.assertLess(len(wire), len(json.dumps(json_data).encode('utf-8')) * 0.75)

    def test_render_transport_never_claims_float32_as_scientific_oracle(self):
        response = self.client.get('/api/v1/models/p1/geometry.bin?space=uv')
        self.assertEqual(response.headers['cache-control'], 'no-store')
        meta = unpack_geometry(response.content)
        self.assertIn('source_sha256', meta)
        self.assertIn('UV is per face corner', meta['warning'])


if __name__ == '__main__':
    unittest.main()
