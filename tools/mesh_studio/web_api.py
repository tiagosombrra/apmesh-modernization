"""Versioned, read-only local API exposing verified mesh identity and geometry.

No arbitrary filesystem path or user-supplied external URL is admitted in R1.
Scientific verification remains in the original Python engine, not the UI.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .import_obj import import_obj
from .quality_analysis import analyze_mesh
from .scene_model import build_batch, face_detail, initial_scene

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


def load_document(model_id: str):
    """Check fixture identity on every request, even if a local file changed."""
    if model_id not in CATALOG:
        raise HTTPException(status_code=404, detail='unknown_model')
    relative, _, expected = CATALOG[model_id]
    path = ROOT / relative
    if not path.is_file() or sha256(path.read_bytes()).hexdigest() != expected:
        raise HTTPException(status_code=409, detail='source_sha_mismatch')
    return import_obj(path, auto_sidecar=False)


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


@app.get('/api/v1/models/{model_id}/faces/{face_id}')
def face(model_id: str, face_id: int):
    doc = load_document(model_id)
    if not 0 <= face_id < len(doc.faces):
        raise HTTPException(status_code=404, detail='unknown_face_id')
    result = face_detail(doc, face_id)
    result['quality'] = analyze_mesh(doc)['cells'][face_id]
    return result


@app.get('/api/v1/models/{model_id}/quality')
def quality(model_id: str):
    return analyze_mesh(load_document(model_id))
