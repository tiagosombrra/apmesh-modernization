"""Headless regressions for the optional S4 desktop bridge and real VTK renderer."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import tempfile
import unittest

from .import_obj import import_obj
from .scene_model import (CameraPose, SceneError, SceneState, build_batch,
                          face_detail, initial_scene, load_scene, parse_scene,
                          scene_json, select_face, visible_face_ids,
                          with_visibility, write_scene)

ROOT = Path(__file__).parent
P1 = ROOT / 'fixtures' / 'real_p1' / 'accepted.obj'
SYN = ROOT / 'fixtures' / 'cases' / 'synthetic_quad_aft_transition.obj'


class SceneModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = import_obj(P1)
        cls.state = initial_scene(cls.doc)

    def test_default_visibility_identity(self):
        self.assertEqual(len(visible_face_ids(self.doc, self.state)), 78)
        self.assertEqual(self.state.source_sha256,
                         'cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0')

    def test_layer_filter_original_face_ids_not_group_patch_ids(self):
        state = with_visibility(self.doc, self.state, triangles=False)
        self.assertEqual(visible_face_ids(self.doc, state), tuple(range(42)))
        tri = with_visibility(self.doc, self.state, quads=False)
        self.assertEqual(visible_face_ids(self.doc, tri), tuple(range(42, 78)))
        self.assertEqual(self.doc.groups, ('QUAD', 'TRI_AFT'))

    def test_both_layer_off_is_empty_scene_not_fake_geometry(self):
        state = with_visibility(self.doc, self.state, triangles=False, quads=False)
        self.assertEqual(visible_face_ids(self.doc, state), ())
        self.assertEqual(build_batch(self.doc, state, coordinates='xyz',
                                     element_type='quad').number_of_cells, 0)

    def test_original_xyz_points_are_not_welded(self):
        quads = build_batch(self.doc, self.state, coordinates='xyz', element_type='quad')
        triangles = build_batch(self.doc, self.state, coordinates='xyz', element_type='triangle')
        self.assertEqual(len(quads.points), 69)
        self.assertEqual(len(triangles.points), 69)
        self.assertEqual(len(quads.faces), 42)
        self.assertEqual(len(triangles.faces), 36)
        self.assertEqual(quads.source_face_ids, tuple(range(42)))
        self.assertEqual(triangles.source_face_ids, tuple(range(42, 78)))
        self.assertEqual(sum(len(f) for f in quads.faces), 168)
        self.assertTrue(all(len(face) == 4 for face in quads.faces))

    def test_uv_corner_splits_are_explicit_and_identity_is_preserved(self):
        quad = build_batch(self.doc, self.state, coordinates='uv', element_type='quad')
        tri = build_batch(self.doc, self.state, coordinates='uv', element_type='triangle')
        self.assertEqual(len(quad.points), 168)
        self.assertEqual(len(tri.points), 108)
        self.assertEqual(quad.source_face_ids, tuple(range(42)))
        self.assertEqual(tri.source_face_ids, tuple(range(42, 78)))
        self.assertTrue(all(p[2] == 0 for p in quad.points + tri.points))

    def test_uv_seam_keeps_distinct_corner_coordinates(self):
        original = self.doc
        faces = list(original.faces)
        same_node = faces[0].vertices[0]
        alternative = next(i for i, face in enumerate(faces[1:], 1)
                           if same_node in face.vertices)
        f = faces[alternative]
        mutable = list(f.uv)
        local_corner = f.vertices.index(same_node)
        mutable[local_corner] = (0.123, 0.456)
        faces[alternative] = replace(f, uv=tuple(mutable))
        changed = replace(original, faces=tuple(faces))
        # The scene model represents incoming per-corner UV without claiming
        # a new valid source geometry or overwriting a shared XYZ node.
        batch = build_batch(changed, self.state, coordinates='uv', element_type=f.element_type)
        index = batch.source_face_ids.index(alternative)
        point = batch.points[index * len(f.vertices) + local_corner]
        self.assertEqual(point, (0.123, 0.456, 0.0))
        self.assertEqual(changed.points[same_node], original.points[same_node])

    def test_nonexistent_uv_is_not_invented(self):
        faces = tuple(replace(face, uv=None) for face in self.doc.faces)
        changed = replace(self.doc, faces=faces)
        quad = build_batch(changed, self.state, coordinates='uv', element_type='quad')
        self.assertEqual(len(quad.points), 0)
        self.assertEqual(quad.number_of_cells, 0)
        self.assertEqual(build_batch(changed, self.state, coordinates='xyz',
                                     element_type='quad').number_of_cells, 42)

    def test_selected_face_and_hidden_selection(self):
        chosen = select_face(self.doc, self.state, 54)
        self.assertEqual(chosen.selected_face, 54)
        selected = build_batch(self.doc, chosen, coordinates='xyz',
                               element_type='triangle', selected_only=True)
        self.assertEqual(selected.source_face_ids, (54,))
        self.assertEqual(len(selected.faces), 1)
        hidden = with_visibility(self.doc, chosen, triangles=False)
        self.assertIsNone(hidden.selected_face)
        with self.assertRaisesRegex(SceneError, 'selected_face_not_visible'):
            select_face(self.doc, hidden, 54)

    def test_source_face_description_has_provenance_and_no_false_quality(self):
        face = face_detail(self.doc, 45)
        self.assertEqual(face['source_face_id'], 45)
        self.assertEqual(face['group'], 'TRI_AFT')
        self.assertEqual(face['quality_status'], 'NOT_CERTIFIED_BY_VIEWER')
        self.assertFalse(face['synthetic'])
        self.assertEqual(len(face['xyz']), 3)
        with self.assertRaises(SceneError):
            face_detail(self.doc, 9999)

    def test_invalid_scene_queries_fail_closed(self):
        with self.assertRaises(SceneError):
            build_batch(self.doc, self.state, coordinates='geodesic', element_type='quad')
        with self.assertRaises(SceneError):
            visible_face_ids(self.doc, SceneState('0'*64))
        with self.assertRaises(SceneError):
            select_face(self.doc, self.state, -5)

    def test_camera_pose_and_provenance_roundtrip(self):
        camera = CameraPose((1.4, -1.1, 2.7), (0., 0., .3),
                            (0., 0., 1.), 1.9, False)
        chosen = replace(select_face(self.doc, self.state, 3),
                         camera_xyz=camera,
                         camera_uv=CameraPose((.5, .5, 3.), (.5, .5, 0.),
                                              (0., 1., 0.), .9, True))
        raw = scene_json(chosen)
        self.assertEqual(parse_scene(raw, self.doc), chosen)
        self.assertEqual(raw, scene_json(parse_scene(raw, self.doc)))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'scene.json'
            write_scene(path, chosen)
            self.assertEqual(load_scene(path, self.doc), chosen)
            with self.assertRaises(FileExistsError):
                write_scene(path, chosen)

    def test_invalid_camera_and_active_content_in_recipe(self):
        with self.assertRaises(SceneError):
            CameraPose((1., 0., 0.), (0., 0., 0.), (1., 0., 0.), 1., False)
        with self.assertRaises(SceneError):
            CameraPose((1., 0., 0.), (0., 0., 0.), (0., 0., 1.), float('nan'), False)
        with self.assertRaises(SceneError):
            CameraPose((1., 0., 0.), (0., 0., 0.), (0., 0., 1.), 0., False)
        payload = json.loads(scene_json(self.state))
        payload['state']['unexpected'] = '__import__("os")'
        with self.assertRaises(SceneError):
            parse_scene(json.dumps(payload), self.doc)
        payload['state'].pop('unexpected')
        payload['state']['source_sha256'] = '0'*64
        with self.assertRaisesRegex(SceneError, 'scene_source_mismatch'):
            parse_scene(json.dumps(payload), self.doc)

    def test_bad_serialized_flags_and_hidden_face(self):
        raw = json.loads(scene_json(self.state))
        raw['state']['show_tri'] = 'yes'
        with self.assertRaises(SceneError):
            parse_scene(json.dumps(raw), self.doc)
        raw['state']['show_tri'] = False
        raw['state']['selected_face'] = 44
        with self.assertRaises(SceneError):
            parse_scene(json.dumps(raw), self.doc)

    def test_synthetic_vs_real_provenance_unambiguous(self):
        syn = import_obj(SYN)
        self.assertTrue(syn.synthetic)
        self.assertFalse(self.doc.synthetic)
        self.assertNotEqual(syn.source_sha256, self.doc.source_sha256)

    def test_runtime_desktop_dependencies_are_optional(self):
        from . import desktop_app
        self.assertTrue(callable(desktop_app.launch))
        if not all(importlib.util.find_spec(x) for x in ('PySide6','pyvista','pyvistaqt')):
            with self.assertRaisesRegex(RuntimeError, 'Desktop dependencies unavailable'):
                desktop_app.launch()


@unittest.skipIf(os.name == 'nt' and os.getenv('APMESH_CI_HEADLESS_NO_OPENGL') == '1',
                 'Windows hosted CI lacks qualified WGL/OSMesa; workstation GPU gate OPEN')
@unittest.skipUnless(importlib.util.find_spec('vtkmodules'), 'VTK unavailable')
class VtkAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = import_obj(P1)
        cls.state = initial_scene(cls.doc)

    def test_actual_vtk_polydata_preserves_typed_face_id_array(self):
        from .scene_vtk import as_vtk_polydata, make_vtk_actors
        actors = make_vtk_actors(self.doc, self.state, coordinates='xyz')
        self.assertEqual([kind for kind, _ in actors], ['quad', 'triangle'])
        self.assertEqual([m.GetNumberOfCells() for _, m in actors], [42, 36])
        self.assertEqual([m.GetNumberOfPoints() for _, m in actors], [69, 69])
        self.assertEqual([m.GetCellData().GetArray('source_face_id').GetValue(0)
                          for _, m in actors], [0, 42])
        self.assertEqual([m.GetCell(0).GetNumberOfPoints() for _, m in actors], [4, 3])

    def test_vtk_uv_is_original_per_corner_not_xyz(self):
        from .scene_vtk import make_vtk_actors
        actors = make_vtk_actors(self.doc, self.state, coordinates='uv')
        self.assertEqual([mesh.GetNumberOfPoints() for _, mesh in actors], [168, 108])
        self.assertTrue(all(mesh.GetBounds()[-1] == 0 for _, mesh in actors))

    def test_vtk_visibility_filters_and_face_id(self):
        from .scene_vtk import make_vtk_actors
        state = with_visibility(self.doc, self.state, triangles=False)
        self.assertEqual([name for name, _ in make_vtk_actors(self.doc, state,
                                                              coordinates='xyz')], ['quad'])

    def test_native_offscreen_vtk_render_real_p1_is_explicitly_raster(self):
        from .scene_vtk import screenshot_3d
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'render.png'
            result = screenshot_3d(self.doc, path, width=800, height=630)
            self.assertEqual(result['image_format'], 'PNG_RASTER_3D_NOT_VECTOR')
            self.assertEqual(result['visible_cells'], 78)
            self.assertEqual(result['quads'], 42)
            self.assertEqual(result['triangles'], 36)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), result['png_sha256'])
            self.assertTrue(path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))
            self.assertEqual(json.loads(path.with_suffix('.audit.json').read_text())['input_sha256'],
                             self.doc.source_sha256)
            with self.assertRaises(FileExistsError):
                screenshot_3d(self.doc, path, width=800, height=630)

    def test_native_offscreen_can_filter_quads_without_synthesizing_triangles(self):
        from .scene_vtk import screenshot_3d
        with tempfile.TemporaryDirectory() as tmp:
            state = with_visibility(self.doc, self.state, triangles=False)
            report = screenshot_3d(self.doc, Path(tmp)/'quad.png', state=state,
                                   width=680, height=560)
            self.assertEqual((report['visible_cells'], report['quads'], report['triangles']),
                             (42, 42, 0))

    def test_invalid_or_empty_renders_are_rejected(self):
        from .scene_vtk import screenshot_3d
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.png'
            with self.assertRaisesRegex(ValueError, 'unsupported_image_size'):
                screenshot_3d(self.doc, path, width=10)
            state = with_visibility(self.doc, self.state, triangles=False, quads=False)
            with self.assertRaisesRegex(ValueError, 'no_visible_cells'):
                screenshot_3d(self.doc, path, state=state)


if __name__ == '__main__':
    unittest.main()
