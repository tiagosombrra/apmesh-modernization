"""Source-bound, bounded, streamed Float32 display geometry (APMSH002).

The source OBJ and its exact SHA-256 remain the scientific authority. This
wire layout is intentionally not the numerical mesh interchange format.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
import struct
import zlib
from collections.abc import Iterator, Mapping

MAGIC = b'APMSH002'
SCHEMA = 'apmesh.meshstudio.geometry.bin.v2'
HEADER = struct.Struct('<8sIIIIII')
MAX_BYTES = 32 * 1024 * 1024
MAX_META = 4096
DEFAULT_CHUNK_BYTES = 64 * 1024
SOURCE_SCHEMA = 'apmesh.meshstudio.web.v1'


class GeometryV2Error(ValueError):
    """Invalid source identity, bounds, layout, or display geometry."""


@dataclass(frozen=True)
class PreparedV2:
    """Validated inputs and a known transfer length; source arrays stay owned."""

    payload: Mapping
    header: bytes
    metadata: bytes
    padding: bytes
    total_bytes: int
    point_count: int
    face_count: int
    poly_words: int


def _require(value: bool, reason: str) -> None:
    if not value:
        raise GeometryV2Error(reason)


def prepare_geometry_v2(payload: Mapping) -> PreparedV2:
    """Prevalidate all input before streaming starts and cap total wire bytes."""
    try:
        points = payload['points']
        cells = payload['cells']
        ids = payload['source_face_ids']
        kinds = payload['cell_types']
        count = len(cells)
        _require(0 < count <= 2_000_000 and 0 < len(points) <= 3_000_000,
                 'invalid_scene_dimensions')
        _require(len(ids) == count and len(kinds) == count,
                 'invalid_scene_inventory')
        _require(all(type(i) is int and 0 <= i < count for i in ids) and
                 len(set(ids)) == count, 'invalid_source_face_permutation')
        _require(all(isinstance(p, (list, tuple)) and len(p) == 3 and
                     all(type(n) in (int, float) and math.isfinite(n) and
                         abs(n) <= 3e37 for n in p) for p in points),
                 'invalid_display_vertex')
        ntri = nquad = poly_words = 0
        for face, kind in zip(cells, kinds):
            arity = 3 if kind == 'triangle' else 4 if kind == 'quad' else 0
            _require(arity > 0 and len(face) == arity and len(set(face)) == arity and
                     all(type(index) is int and 0 <= index < len(points)
                         for index in face), 'invalid_display_cell')
            ntri += arity == 3
            nquad += arity == 4
            poly_words += arity + 1
        _require(type(payload['triangles']) is int and
                 type(payload['quads']) is int and
                 ntri == payload['triangles'] and nquad == payload['quads'],
                 'mismatched_display_inventory')
        sha = payload['source_sha256']
        _require(isinstance(sha, str) and len(sha) == 64 and
                 all(c in '0123456789abcdef' for c in sha), 'invalid_source_sha')
        _require(payload['schema'] == SOURCE_SCHEMA and
                 payload['coordinate_space'] in ('xyz', 'uv'), 'invalid_display_schema')
        metadata = {key: payload[key] for key in
                    ('schema', 'source_sha256', 'source_patch_ownership',
                     'coordinate_space', 'triangles', 'quads', 'warning')}
        metadata['wire_schema'] = SCHEMA
        meta = json.dumps(metadata, sort_keys=True, separators=(',', ':'),
                          ensure_ascii=False, allow_nan=False).encode('utf-8')
        _require(0 < len(meta) <= MAX_META, 'invalid_metadata_size')
        padding = bytes((-len(meta)) % 4)
        total = (HEADER.size + len(meta) + len(padding) +
                 12 * len(points) + 4 * poly_words + 5 * count + 4)
        _require(total <= MAX_BYTES, 'display_transport_size_limit')
        header = HEADER.pack(MAGIC, len(meta), len(points), count,
                             poly_words, len(padding), 0)
        return PreparedV2(payload, header, meta, padding, total,
                          len(points), count, poly_words)
    except (KeyError, TypeError, ValueError, OverflowError, struct.error) as exc:
        if isinstance(exc, GeometryV2Error):
            raise
        raise GeometryV2Error('invalid_geometry_v2_input') from exc


def stream_geometry_v2(prepared: PreparedV2,
                       chunk_bytes: int = DEFAULT_CHUNK_BYTES) -> Iterator[bytes]:
    """Produce CRC-guarded wire chunks without one full payload byte copy."""
    _require(type(chunk_bytes) is int and
             4096 <= chunk_bytes <= 1024 * 1024 and chunk_bytes % 4 == 0,
             'invalid_stream_chunk_budget')
    crc = 0
    sent = 0

    def emit(data: bytes) -> bytes:
        nonlocal crc, sent
        crc = zlib.crc32(data, crc)
        sent += len(data)
        return data

    yield emit(prepared.header)
    yield emit(prepared.metadata + prepared.padding)
    payload = prepared.payload

    def pack_chunks(rows, packer: struct.Struct):
        pending = bytearray()
        for row in rows:
            if isinstance(row, (tuple, list)):
                pending.extend(packer.pack(*row))
            else:
                pending.extend(packer.pack(row))
            if len(pending) >= chunk_bytes:
                yield bytes(pending)
                pending.clear()
        if pending:
            yield bytes(pending)

    for part in pack_chunks(payload['points'], struct.Struct('<fff')):
        yield emit(part)
    # Preserve cells as native TRI/QUAD; never fan-triangulate a QUAD.
    poly_buffer = bytearray()
    for face in payload['cells']:
        poly_buffer.extend(struct.pack('<I', len(face)))
        for point_index in face:
            poly_buffer.extend(struct.pack('<I', point_index))
        if len(poly_buffer) >= chunk_bytes:
            yield emit(bytes(poly_buffer))
            poly_buffer.clear()
    if poly_buffer:
        yield emit(bytes(poly_buffer))
    for part in pack_chunks(payload['source_face_ids'], struct.Struct('<I')):
        yield emit(part)
    arities = bytearray()
    for kind in payload['cell_types']:
        arities.append(3 if kind == 'triangle' else 4)
        if len(arities) >= chunk_bytes:
            yield emit(bytes(arities))
            arities.clear()
    if arities:
        yield emit(bytes(arities))
    yield struct.pack('<I', crc)
    _require(sent + 4 == prepared.total_bytes, 'stream_length_invariant_failed')


def pack_geometry_v2(payload: Mapping, chunk_bytes: int = DEFAULT_CHUNK_BYTES) -> bytes:
    """Materialize the stream only for bounded verification and unit tests."""
    return b''.join(stream_geometry_v2(prepare_geometry_v2(payload), chunk_bytes))


def unpack_geometry_v2(data: bytes) -> dict:
    """Independent server-side decoder used as a cross-language golden oracle."""
    _require(HEADER.size + 4 < len(data) <= MAX_BYTES, 'invalid_binary_size')
    magic, meta_len, points, faces, words, pad, flags = HEADER.unpack_from(data)
    _require(magic == MAGIC and flags == 0 and 0 < meta_len <= MAX_META and
             0 <= pad <= 3 and pad == (-meta_len) % 4 and
             0 < points <= 3_000_000 and 0 < faces <= 2_000_000,
             'invalid_binary_header')
    expected = HEADER.size + meta_len + pad + points*12 + words*4 + faces*5 + 4
    _require(expected == len(data), 'binary_length_mismatch')
    _require(zlib.crc32(data[:-4]) == struct.unpack_from('<I', data, len(data)-4)[0],
             'binary_crc_mismatch')
    try:
        metadata = json.loads(data[HEADER.size:HEADER.size + meta_len])
        _require(metadata['wire_schema'] == SCHEMA and
                 metadata['schema'] == SOURCE_SCHEMA and
                 metadata['coordinate_space'] in ('xyz', 'uv') and
                 isinstance(metadata['source_sha256'], str) and
                 len(metadata['source_sha256']) == 64, 'invalid_binary_provenance')
        _require(data[HEADER.size+meta_len:HEADER.size+meta_len+pad] == bytes(pad),
                 'invalid_binary_padding')
        position = HEADER.size + meta_len + pad
        vertex_list = [list(struct.unpack_from('<fff', data, position + 12*i))
                       for i in range(points)]
        position += points*12
        polys = struct.unpack_from('<' + str(words) + 'I', data, position)
        position += words*4
        ids = list(struct.unpack_from('<' + str(faces) + 'I', data, position))
        position += faces*4
        arities = data[position:position + faces]
        _require(len(set(ids)) == faces and all(0 <= i < faces for i in ids),
                 'invalid_binary_face_identity')
        _require(all(math.isfinite(value) for row in vertex_list for value in row),
                 'invalid_binary_coordinates')
        cells = []
        cursor = 0
        for arity in arities:
            _require(arity in (3, 4) and cursor + arity + 1 <= words and
                     polys[cursor] == arity, 'invalid_binary_arity')
            face = list(polys[cursor+1:cursor+1+arity])
            _require(len(set(face)) == arity and all(v < points for v in face),
                     'invalid_binary_indices')
            cells.append(face)
            cursor += arity + 1
        _require(cursor == words and arities.count(3) == metadata['triangles'] and
                 arities.count(4) == metadata['quads'], 'invalid_binary_counts')
        metadata.pop('wire_schema')
        return {**metadata, 'points': vertex_list, 'cells': cells,
                'source_face_ids': ids,
                'cell_types': ['triangle' if n == 3 else 'quad' for n in arities]}
    except (KeyError, TypeError, ValueError, OverflowError, struct.error) as exc:
        if isinstance(exc, GeometryV2Error):
            raise
        raise GeometryV2Error('invalid_binary_payload') from exc
