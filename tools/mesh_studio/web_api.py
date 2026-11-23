"""Versioned, read-only local API exposing verified mesh identity and geometry.

No arbitrary filesystem path or user-supplied external URL is admitted in R1.
Scientific verification remains in the original Python engine, not the UI.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from .import_obj import MAX_SOURCE_BYTES, import_obj
from .quality_analysis import analyze_mesh
from .scene_model import build_batch, face_detail, initial_scene
from .scene_transport import pack_geometry, SceneTransportError
from .scene_transport_v2 import prepare_geometry_v2, stream_geometry_v2, GeometryV2Error
from .svg_figure import URI as SVG_URI, audit_svg, render_uv_svg, write_canonical_svg
from .local_loopback_guard import LocalLoopbackGuard

SCHEMA = 'apmesh.meshstudio.web.v1'
ROOT = Path(__file__).resolve().parent / 'fixtures'
CATALOG = {
    'p1': ('real_p1/accepted.obj', 'CONTROLLED_PHYSICAL_GENERATION',
           'cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0'),
    'band': ('real_p2d1c3/band.obj', 'STAGED_UNACCEPTED',
             '76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6'),
    'west': ('real_p2d1c3/west.obj', 'STAGED_UNACCEPTED',
             'ca08918f6d71fa672de22a72eb6fef7c106c90c7fd02d40cb19852972b4274ee'),
    'north': ('real_p2d1c3/north.obj', 'STAGED_UNACCEPTED',
              '6eb4faedeaab44fbfa3d4cb2ca1ea618a3dca513dc241871c57bcc7eae26d500'),
    'both': ('real_p2d1c3/both.obj', 'STAGED_UNACCEPTED',
             'b77afb530724f38ff81f0f3e7f06fca6c8dc0cb4a15562ce933a4013724bd36c'),
}

app = FastAPI(title='APMesh Mesh Studio read-only research service', version='0.1.0',
              docs_url='/api/docs', openapi_url='/api/openapi.json')
# The browser development server uses Vite proxy; no permissive public CORS.
app.add_middleware(CORSMiddleware,
                   allow_origins=['http://127.0.0.1:5173', 'http://localhost:5173'],
                   allow_credentials=False, allow_methods=['GET'], allow_headers=['Accept'])


@lru_cache(maxsize=8)
def _verified_document(path: Path, expected_sha256: str):
    """Parse only once per exact source path and source hash in each process."""
    document = import_obj(path, auto_sidecar=False)
    if document.source_sha256 != expected_sha256:
        raise HTTPException(status_code=409, detail='source_sha_mismatch')
    return document


@lru_cache(maxsize=8)
def _verified_quality(path: Path, expected_sha256: str):
    """Reuse deterministic full-mesh metrics without changing the scientific oracle."""
    return analyze_mesh(_verified_document(path, expected_sha256))


def load_document(model_id: str):
    """Rehash the current fixture on every request before using cached results."""
    if model_id not in CATALOG:
        raise HTTPException(status_code=404, detail='unknown_model')
    relative, _, expected = CATALOG[model_id]
    path = ROOT / relative
    if (not path.is_file() or
            path.stat().st_size > MAX_SOURCE_BYTES or
            sha256(path.read_bytes()).hexdigest() != expected):
        raise HTTPException(status_code=409, detail='source_sha_mismatch')
    return _verified_document(path, expected)


@app.get('/api/v1/health')
def health():
    return {'schema': SCHEMA, 'status': 'READY', 'mode': 'READ_ONLY_LOCAL_RESEARCH'}


@app.get('/api/v1/models')
def models():
    entries = []
    for key in CATALOG:
        doc = load_document(key)
        entries.append({'id': key, 'sha256': doc.source_sha256,
                        'triangles': doc.triangles, 'quads': doc.quads,
                        'points': len(doc.points),
                        'source_status': CATALOG[key][1],
                        'accepted_adaptive_epochs': 0,
                        'source_patch_ownership': 'UNKNOWN_FROM_OBJ'})
    return {'schema': SCHEMA, 'models': entries,
            'study_scope': 'ONE_SOURCE_MODEL_STAGED_MESH_CANDIDATES_NOT_REPEATED_RUNS'}


@app.get('/api/v1/models/{model_id}/geometry')
def geometry(model_id: str, space: str = Query('xyz', pattern='^(xyz|uv)$')):
    doc = load_document(model_id)
    state = initial_scene(doc)
    cells = []
    points: list[list[float]] = []
    source_ids = []
    cell_types = []
    if space == 'xyz':
        points = [list(x) for x in doc.points]
    for element in ('triangle', 'quad'):
        batch = build_batch(doc, state, coordinates=space, element_type=element)
        if space == 'uv':
            start = len(points)
            points.extend([list(p) for p in batch.points])
            cells.extend([[start + n for n in face] for face in batch.faces])
        else:
            cells.extend([list(face) for face in batch.faces])
        source_ids.extend(batch.source_face_ids)
        cell_types.extend([element] * len(batch.faces))
    if len(source_ids) != len(doc.faces):
        raise HTTPException(status_code=409, detail='missing_uv_or_face_identity')
    if set(source_ids) != set(range(len(doc.faces))):
        raise HTTPException(status_code=409, detail='missing_original_face_id')
    return {'schema': SCHEMA, 'source_sha256': doc.source_sha256,
            'source_patch_ownership': doc.patch_ownership,
            'coordinate_space': space, 'points': points, 'cells': cells,
            'source_face_ids': list(source_ids), 'cell_types': cell_types,
            'triangles': doc.triangles, 'quads': doc.quads,
            'warning': 'UV is per face corner. Geometry is indexed by source face IDs.'}


@app.get('/api/v1/models/{model_id}/geometry.bin')
def binary_geometry(model_id: str, space: str = Query('xyz', pattern='^(xyz|uv)$')):
    """Return a bounded little-endian rendering transport, never scientific float64 data."""
    payload = geometry(model_id, space)
    payload['warning'] += ' Positions are float32 display data, never the numerical source oracle.'
    try:
        wire = pack_geometry(payload)
    except SceneTransportError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return Response(content=wire, media_type='application/vnd.apmesh.geometry.v1',
                    headers={'Cache-Control': 'no-store',
                             'X-Source-SHA256': payload['source_sha256']})


@app.get('/api/v1/models/{model_id}/geometry.v2.bin')
def binary_geometry_v2(model_id: str, space: str = Query('xyz', pattern='^(xyz|uv)$')):
    """Bounded streamed Float32 view data with exact original source-face mapping."""
    payload = geometry(model_id, space)
    payload['warning'] += ' Float32 is a visualization transport, not the numerical source oracle.'
    try:
        prepared = prepare_geometry_v2(payload)
    except GeometryV2Error as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return StreamingResponse(
        stream_geometry_v2(prepared), media_type='application/vnd.apmesh.geometry.v2',
        headers={'Cache-Control': 'no-store', 'Content-Length': str(prepared.total_bytes),
                 'X-Source-SHA256': payload['source_sha256'],
                 'X-Visualization-Only': 'float32-not-scientific-source'})



@app.get('/api/v1/models/{model_id}/publication.svg')
def publication_svg(model_id: str):
    """Serve the independently audited, pure-vector UV figure for a pinned source.

    This is the original imported source mesh, never a manufactured adaptive
    epoch or a shaded 3D raster export. No filesystem path is user-controlled.
    """
    document = load_document(model_id)
    source_status = CATALOG[model_id][1]
    with TemporaryDirectory(prefix='apmesh-v5-source-figure-') as temporary:
        path = Path(temporary) / 'source_uv.svg'
        receipt = render_uv_svg(document, path, width_mm=155, height_mm=120)
        root = ET.parse(path).getroot()
        for item in root.iter(f'{{{SVG_URI}}}text'):
            if item.attrib.get('y') == '684':
                item.text = ('STAGED CANDIDATE — NOT AN ACCEPTED ADAPTIVE EPOCH'
                             if source_status == 'STAGED_UNACCEPTED'
                             else 'CONTROLLED ORIGINAL — NO ADAPTIVE EPOCH')
        ET.SubElement(root, f'{{{SVG_URI}}}metadata').text = json.dumps({
            'schema': 'apmesh.meshstudio.v5.web_source_uv_publication.v1',
            'source_sha256': document.source_sha256,
            'source_status': source_status,
            'source_kind': document.source_kind,
            'accepted_adaptive_epochs': 0,
            'source_patch_ownership': document.patch_ownership,
            'render_class': receipt['render_class'],
            'physical_size_mm': [155, 120],
            'source_surface_continuously_certified': False,
            'scientific_lod_qualified': False,
        }, sort_keys=True, separators=(',', ':'))
        write_canonical_svg(root, path)
        audit = audit_svg(path, expected_faces=len(document.faces))
        if not audit['vector_only'] or audit['raster_image_count'] != 0:
            raise HTTPException(status_code=409, detail='unqualified_svg')
        output = path.read_bytes()
    output_sha = sha256(output).hexdigest()
    filename = f'apmesh_{model_id}_{document.source_sha256[:12]}_uv_source.svg'
    return Response(
        content=output, media_type='image/svg+xml',
        headers={
            'Cache-Control': 'no-store',
            'Content-Disposition': f'attachment; filename="{filename}"',
            'X-Source-SHA256': document.source_sha256,
            'X-Source-Status': source_status,
            'X-Vector-Figure-SHA256': output_sha,
            'X-Visualization-Only': 'source-uv-not-continuous-surface-or-lod',
        })


@app.get('/api/v1/models/{model_id}/faces/{face_id}')
def face(model_id: str, face_id: int):
    doc = load_document(model_id)
    if not 0 <= face_id < len(doc.faces):
        raise HTTPException(status_code=404, detail='unknown_face_id')
    result = face_detail(doc, face_id)
    result['quality'] = dict(_verified_quality(ROOT / CATALOG[model_id][0],
                                              doc.source_sha256)['cells'][face_id])
    return result


@app.get('/api/v1/models/{model_id}/quality')
def quality(model_id: str):
    document = load_document(model_id)
    # Return an isolated report, never the mutable canonical cached source.
    return deepcopy(_verified_quality(ROOT / CATALOG[model_id][0],
                                      document.source_sha256))


# Only the local launcher exposes the guarded ASGI instance.
# Legacy research TestClient contracts continue using the bare FastAPI app.
local_app = LocalLoopbackGuard(app)
