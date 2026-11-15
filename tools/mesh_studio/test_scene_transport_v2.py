"""Cross-language V2 display transport gates, negative inputs and bounded streams."""

from __future__ import annotations

import copy
import json
import struct
import unittest

from .scene_transport_v2 import (GeometryV2Error, HEADER, MAX_BYTES,
                                 pack_geometry_v2, prepare_geometry_v2,
                                 stream_geometry_v2, unpack_geometry_v2)


def example():
    return {
        'schema': 'apmesh.meshstudio.web.v1', 'source_sha256': 'a' * 64,
        'source_patch_ownership': 'unknown', 'coordinate_space': 'xyz',
        'triangles': 1, 'quads': 1, 'warning': 'Float32 visualization only',
        'points': [[0., 0., 0.], [1., 0., 0.], [0., 1., 0.],
                   [1., 1., 0.], [2., 1., 0.]],
        'cells': [[0, 1, 2], [1, 3, 4, 2]],
        'source_face_ids': [1, 0],
        'cell_types': ['triangle', 'quad'],
    }


class TransportV2Tests(unittest.TestCase):
    def test_tri_quad_are_not_triangulated(self):
        recovered = unpack_geometry_v2(pack_geometry_v2(example()))
        self.assertEqual(recovered['cells'], example()['cells'])
        self.assertEqual(recovered['source_face_ids'], [1, 0])
        self.assertEqual(recovered['cell_types'], ['triangle', 'quad'])

    def test_stream_does_not_materialize_32mb_response(self):
        payload = example()
        prepared = prepare_geometry_v2(payload)
        self.assertEqual(prepared.total_bytes, len(pack_geometry_v2(payload)))
        for chunk in (4096, 8192, 65536):
            with self.subTest(chunk=chunk):
                self.assertEqual(b''.join(stream_geometry_v2(prepared, chunk)),
                                 pack_geometry_v2(payload))

    def test_metadata_is_aligned(self):
        data = pack_geometry_v2(example())
        magic, meta_len, npts, nfaces, nwords, padding, flags = HEADER.unpack_from(data)
        self.assertEqual(magic, b'APMSH002')
        self.assertEqual((HEADER.size + meta_len + padding) % 4, 0)
        self.assertEqual((npts, nfaces, nwords), (5, 2, 9))
        self.assertEqual(flags, 0)

    def test_corrupted_body_is_rejected(self):
        data = bytearray(pack_geometry_v2(example()))
        data[-9] ^= 1
        with self.assertRaisesRegex(GeometryV2Error, 'binary_crc_mismatch'):
            unpack_geometry_v2(bytes(data))

    def test_bad_length_rejected(self):
        data = pack_geometry_v2(example())
        with self.assertRaisesRegex(GeometryV2Error, 'binary_length_mismatch'):
            unpack_geometry_v2(data[:-1])

    def test_invalid_source_face_ids_rejected(self):
        payload = example()
        payload['source_face_ids'] = [0, 0]
        with self.assertRaisesRegex(GeometryV2Error, 'invalid_source_face_permutation'):
            pack_geometry_v2(payload)

    def test_invalid_foreign_vertex_rejected(self):
        payload = example()
        payload['cells'][1][-1] = 999
        with self.assertRaisesRegex(GeometryV2Error, 'invalid_display_cell'):
            pack_geometry_v2(payload)

    def test_nan_and_overflow_rejected(self):
        for value in (float('nan'), float('inf'), 3.5e38):
            payload = example()
            payload['points'][0][0] = value
            with self.subTest(value=value), self.assertRaisesRegex(GeometryV2Error,
                                                                     'invalid_display_vertex'):
                pack_geometry_v2(payload)

    def test_limited_stream_chunk_size(self):
        prepared = prepare_geometry_v2(example())
        with self.assertRaisesRegex(GeometryV2Error, 'invalid_stream_chunk_budget'):
            list(stream_geometry_v2(prepared, 300))

    def test_real_source_sha_is_copied_not_made_up(self):
        p = example()
        p['source_sha256'] = '2' * 64
        recovered = unpack_geometry_v2(pack_geometry_v2(p))
        self.assertEqual(recovered['source_sha256'], '2' * 64)
        self.assertEqual(recovered['coordinate_space'], 'xyz')

    def test_source_bin_is_display_only(self):
        p = example()
        p['warning'] = 'Uncertified Float32 graphics only'
        recovered = unpack_geometry_v2(pack_geometry_v2(p))
        self.assertIn('Float32', recovered['warning'])


if __name__ == '__main__':
    unittest.main()
