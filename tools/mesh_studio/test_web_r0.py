"""Independent R0 source ownership, immutability and read-only API gates."""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from .import_obj import MeshImportError, import_obj
from .web_api import app, CATALOG

FIXTURES = Path(__file__).resolve().parent / 'fixtures'


class R0ResearchContracts(unittest.TestCase):
    def _real_sidecar(self, obj_path: Path, original: dict, *, model=None):
        payload = json.loads(json.dumps(original))
        payload.update({'schema': 'apmesh.meshstudio.real_patch.v1',
                        'synthetic': False,
                        'obj_sha256': sha256(obj_path.read_bytes()).hexdigest(),
                        'source_model_sha256': '1'*64,
                        'generator_commit': '2'*40,
                        'patches': [{'patch_id': p, 'source_surface_id': f'surface:{p}'}
                                    for p in sorted({f['patch_id'] for f in payload['faces']})]})
        if model:
            payload.update(model)
        return payload

    def test_nested_curve_is_immutable(self):
        doc = import_obj(FIXTURES/'cases/synthetic_shared_curve_fan3.obj')
        with self.assertRaises(TypeError):
            doc.source_curves[0]['curve_id'] = 'spoof'
        with self.assertRaises(TypeError):
            doc.source_curves[0]['by_patch_xyz']['patch_0'] = 'spoof'
        with self.assertRaises(TypeError):
            doc.source_curves[0]['by_patch_xyz']['patch_0'][0][0] = 123
        self.assertEqual(doc.source_curves[0]['curve_id'], 'shared_axis_0')
        self.assertEqual(len(doc.semantic_metadata_sha256 or ''), 64)
        with self.assertRaises(FrozenInstanceError):
            doc.source_curves = ()

    def test_real_patch_preserves_distinct_source_owners(self):
        original = FIXTURES/'cases/synthetic_shared_curve_fan3.obj'
        meta = json.loads(original.with_suffix('.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            obj = Path(tmp)/'source.obj'
            obj.write_bytes(original.read_bytes())
            payload = self._real_sidecar(obj,meta)
            sidecar = obj.with_suffix('.json')
            sidecar.write_text(json.dumps(payload))
            doc = import_obj(obj)
            self.assertFalse(doc.synthetic)
            self.assertEqual(doc.source_kind, 'real_patch_sidecar')
            self.assertEqual(len(doc.source_patches), 3)
            self.assertEqual(len(doc.source_curves[0]['incident_patches']), 3)
            self.assertNotEqual(doc.semantic_metadata_sha256, doc.source_sha256)
            self.assertTrue(all(f.patch_id in doc.source_patches for f in doc.faces))

    def test_invalid_real_patch_claim_rejected(self):
        original = FIXTURES/'cases/synthetic_shared_curve_fan3.obj'
        meta = json.loads(original.with_suffix('.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            obj = Path(tmp)/'source.obj';obj.write_bytes(original.read_bytes())
            for override, expected in [
                ({'source_model_sha256': 'wrong'}, 'invalid_source_model_hash'),
                ({'patches':[{'patch_id':'foreign','source_surface_id':'x'}]}, 'face_sidecar_mismatch'),
                ({'obj_sha256': '0'*64}, 'source_sha_mismatch')
            ]:
                obj.with_suffix('.json').write_text(json.dumps(self._real_sidecar(obj,meta,model=override)))
                with self.subTest(expected=expected), self.assertRaises(MeshImportError) as ctx:
                    import_obj(obj)
                self.assertEqual(ctx.exception.code, expected)

    def test_real_curve_alias_rejected(self):
        original=FIXTURES/'cases/synthetic_shared_curve_fan3.obj'
        meta=json.loads(original.with_suffix('.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            obj=Path(tmp)/'source.obj';obj.write_bytes(original.read_bytes())
            payload=self._real_sidecar(obj,meta)
            payload['curves'][0]['incident_patches'].append('foreign')
            obj.with_suffix('.json').write_text(json.dumps(payload))
            with self.assertRaises(MeshImportError) as ctx:
                import_obj(obj)
            self.assertEqual(ctx.exception.code, 'invalid_curve_incidence')


class R1ServiceTests(unittest.TestCase):
    def setUp(self):
        self.client=TestClient(app)

    def test_known_catalog_and_status(self):
        r=self.client.get('/api/v1/models')
        self.assertEqual(r.status_code,200)
        catalog=r.json()['models']
        self.assertEqual(set(x['id'] for x in catalog),set(CATALOG))
        self.assertEqual(set(x['accepted_adaptive_epochs'] for x in catalog),{0})
        self.assertEqual({x['source_status'] for x in catalog}, {'CONTROLLED_PHYSICAL_GENERATION','STAGED_UNACCEPTED'})

    def test_p1_xyz_uv_have_identical_source_face_id_sets(self):
        xyz=self.client.get('/api/v1/models/p1/geometry?space=xyz').json()
        uv=self.client.get('/api/v1/models/p1/geometry?space=uv').json()
        self.assertEqual(xyz['source_sha256'],uv['source_sha256'])
        self.assertEqual(set(xyz['source_face_ids']),set(uv['source_face_ids']))
        self.assertEqual(len(xyz['cells']),78)
        self.assertEqual(xyz['triangles'],36)
        self.assertEqual(xyz['quads'],42)
        self.assertEqual(len(xyz['points']),69)
        self.assertEqual(len(uv['points']),36*3+42*4)

    def test_rejected_queries_and_paths(self):
        for path,code in [('/api/v1/models/../geometry',404),
                          ('/api/v1/models/wrong/geometry',404),
                          ('/api/v1/models/p1/geometry?space=invalid',422),
                          ('/api/v1/models/p1/faces/10000',404)]:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code,code)

    def test_source_face_detail_and_quality_agree(self):
        item=self.client.get('/api/v1/models/p1/faces/0').json()
        self.assertEqual(item['source_face_id'],0)
        self.assertEqual(item['source_sha256'],CATALOG['p1'][2])
        self.assertEqual(item['quality']['index'],0)
        self.assertEqual(item['quality_status'],'NOT_CERTIFIED_BY_VIEWER')

    def test_all_staged_have_complete_view_geometry(self):
        for model in ('band','west','north','both'):
            with self.subTest(model=model):
                r=self.client.get(f'/api/v1/models/{model}/geometry?space=uv')
                self.assertEqual(r.status_code,200)
                d=r.json()
                self.assertEqual(len(d['cells']),d['triangles']+d['quads'])
                self.assertEqual(len(set(d['source_face_ids'])),len(d['cells']))

    def test_cors_cannot_be_public_star(self):
        r=self.client.options('/api/v1/models',headers={'Origin':'https://malicious.example','Access-Control-Request-Method':'GET'})
        self.assertNotEqual(r.headers.get('access-control-allow-origin'),'*')
        self.assertNotEqual(r.headers.get('access-control-allow-origin'),'https://malicious.example')


if __name__ == '__main__':
    unittest.main()
