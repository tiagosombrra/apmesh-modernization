"""Bounded, versioned little-endian wire transport for visualization-only meshes.

Float32 coordinates are rendering approximations, not scientific source data.
The original validated OBJ and its SHA-256 remain the scientific authority.
"""
from __future__ import annotations

from array import array
import json
import math
import struct
import sys

MAGIC = b'APMSH001'
HEADER = struct.Struct('<8sIIII')
MAX_SCENE_BYTES = 32 * 1024 * 1024
MAX_META_BYTES = 4096


class SceneTransportError(ValueError):
    """Reject inconsistent, overlarge or malformed visualization data."""


def _packed(values: list[int] | list[float], kind: str) -> bytes:
    result = array(kind, values)
    if result.itemsize != 4:
        raise SceneTransportError('unsupported_word_size')
    if sys.byteorder != 'little':
        result.byteswap()
    return result.tobytes()


def pack_geometry(payload: dict) -> bytes:
    """Serialize exact source face IDs and explicit TRI/QUAD arities."""
    try:
        points = payload['points']
        cells = payload['cells']
        ids = payload['source_face_ids']
        kinds = payload['cell_types']
        n = len(cells)
        if not points or not cells or n != len(ids) or n != len(kinds):
            raise SceneTransportError('invalid_cell_inventory')
        if n >= 2**32 or len(points) >= 2**32:
            raise SceneTransportError('geometry_overflow')
        if any(type(i) is not int or i < 0 or i >= n for i in ids) or set(ids) != set(range(n)):
            raise SceneTransportError('invalid_source_face_ids')
        if any(len(p) != 3 or any(not math.isfinite(float(x)) for x in p) for p in points):
            raise SceneTransportError('invalid_point_coordinate')
        flat_points = [float(x) for p in points for x in p]
        if any(abs(x) > 3e37 for x in flat_points):
            raise SceneTransportError('coordinate_float32_overflow')
        polys: list[int] = []
        face_types: list[int] = []
        for face, kind in zip(cells, kinds):
            arity = {'triangle': 3, 'quad': 4}.get(kind)
            if arity is None or len(face) != arity or len(set(face)) != arity:
                raise SceneTransportError('invalid_cell_arity')
            if any(type(v) is not int or v < 0 or v >= len(points) for v in face):
                raise SceneTransportError('invalid_cell_vertex')
            polys.extend((arity, *face))
            face_types.append(arity)
        if sum(v == 3 for v in face_types) != payload['triangles'] or sum(v == 4 for v in face_types) != payload['quads']:
            raise SceneTransportError('mismatched_element_counts')
        source_sha = payload['source_sha256']
        if not isinstance(source_sha, str) or len(source_sha) != 64 or any(c not in '0123456789abcdef' for c in source_sha):
            raise SceneTransportError('invalid_source_sha')
        metadata = {key: payload[key] for key in ('schema', 'source_sha256', 'source_patch_ownership',
                                                   'coordinate_space', 'triangles', 'quads', 'warning')}
        metadata['wire_schema'] = 'apmesh.meshstudio.geometry.bin.v1'
        meta = json.dumps(metadata, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
        if len(meta) > MAX_META_BYTES:
            raise SceneTransportError('metadata_limit')
        # Validate expected size before assembling large arrays.
        expected = HEADER.size + len(meta) + len(flat_points) * 4 + len(polys) * 4 + n * 5
        if expected > MAX_SCENE_BYTES:
            raise SceneTransportError('scene_transport_size_limit')
        binary = (HEADER.pack(MAGIC, len(meta), len(points), n, len(polys)) + meta +
                  _packed(flat_points, 'f') + _packed(polys, 'I') +
                  _packed(ids, 'I') + bytes(face_types))
        if len(binary) != expected:
            raise SceneTransportError('scene_transport_length_mismatch')
        return binary
    except (KeyError, TypeError, OverflowError, ValueError, struct.error) as exc:
        if isinstance(exc, SceneTransportError):
            raise
        raise SceneTransportError('invalid_scene_transport_input') from exc


def unpack_geometry(data: bytes) -> dict:
    """Independently parse the wire bytes for tests and cross-language oracles."""
    if len(data) < HEADER.size or len(data) > MAX_SCENE_BYTES:
        raise SceneTransportError('invalid_binary_size')
    magic, length, point_count, face_count, word_count = HEADER.unpack_from(data)
    if magic != MAGIC or not (0 < length <= MAX_META_BYTES) or not point_count or not face_count:
        raise SceneTransportError('invalid_binary_header')
    expected = HEADER.size + length + 12 * point_count + 4 * word_count + 5 * face_count
    if expected != len(data):
        raise SceneTransportError('binary_length_mismatch')
    offset = HEADER.size
    try:
        metadata = json.loads(data[offset:offset+length]); offset += length
        if metadata.get('wire_schema') != 'apmesh.meshstudio.geometry.bin.v1':
            raise SceneTransportError('invalid_binary_schema')
        points = [list(struct.unpack_from('<fff', data, offset+12*i)) for i in range(point_count)]
        offset += point_count * 12
        words = struct.unpack_from(f'<{word_count}I', data, offset)
        offset += word_count * 4
        source_ids = list(struct.unpack_from(f'<{face_count}I', data, offset))
        offset += face_count * 4
        types = data[offset:]
        cells = []
        cursor = 0
        for arity in types:
            if arity not in (3, 4) or cursor + 1 + arity > word_count or words[cursor] != arity:
                raise SceneTransportError('invalid_binary_polys')
            cells.append(list(words[cursor+1:cursor+1+arity]));cursor += 1+arity
        if cursor != word_count or set(source_ids) != set(range(face_count)):
            raise SceneTransportError('invalid_binary_identity')
        if any(not all(math.isfinite(x) for x in p) for p in points):
            raise SceneTransportError('invalid_binary_coordinates')
        if any(i >= point_count for face in cells for i in face):
            raise SceneTransportError('invalid_binary_indices')
        result = dict(metadata)
        result.pop('wire_schema', None)
        result.update(points=points, cells=cells, source_face_ids=source_ids,
                      cell_types=['triangle' if t == 3 else 'quad' for t in types])
        if result['triangles'] != types.count(3) or result['quads'] != types.count(4):
            raise SceneTransportError('invalid_binary_counts')
        return result
    except (ValueError, TypeError, KeyError, OverflowError, struct.error, UnicodeError) as exc:
        if isinstance(exc, SceneTransportError):
            raise
        raise SceneTransportError('invalid_binary_payload') from exc
