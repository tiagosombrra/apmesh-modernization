"""Optional desktop user interface for inspectable TRI/QUAD geometry.

This module is intentionally importable without Qt, PyVista or an OpenGL
context. GUI dependencies are loaded only by launch().
"""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
import os
from pathlib import Path
import sys

from .import_obj import MeshImportError, import_obj
from .scene_model import (CameraPose, SceneError, build_batch, face_detail,
                          initial_scene, load_scene, select_face, scene_json,
                          visible_face_ids, with_visibility, write_scene)


def launch(obj_path: Path | str | None = None, *,
           smoke_output: Path | str | None = None) -> int:
    """Start an explicit desktop session; never initialize Qt during import."""
    os.environ.setdefault('QT_API', 'pyside6')
    try:
        from PySide6 import QtCore, QtGui, QtWidgets
        import pyvista as pv
        from pyvistaqt import QtInteractor
    except ImportError as exc:
        raise RuntimeError(
            'Desktop dependencies unavailable. Install PySide6, pyvista and '
            'pyvistaqt in a compatible graphical Python environment. '
            'Headless import/metrics/SVG commands remain available.'
        ) from exc
    from .scene_vtk import as_vtk_polydata
    from .quality_analysis import analyze_mesh, QualityError

    class MeshStudioWindow(QtWidgets.QMainWindow):
        """Two native renderers, with optional source-preserving cell selection."""

        def __init__(self, obj_file: Path):
            super().__init__()
            self.setWindowTitle('APMesh Mesh Studio — Scientific Mesh Inspection')
            self.resize(1510, 910)
            self._document = import_obj(obj_file)
            self._scene = initial_scene(self._document)
            self._file = Path(obj_file)
            self._render_ready = False
            self._quality_cells = None
            self._quality_error = None
            self._setup_widgets()
            self._draw(reset=True)

        def _setup_widgets(self) -> None:
            root = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
            root.setChildrenCollapsible(False)
            self._xyz = QtInteractor(root)
            self._uv = QtInteractor(root)
            root.addWidget(self._xyz)
            root.addWidget(self._uv)
            root.setSizes([760, 640])
            self.setCentralWidget(root)

            dock = QtWidgets.QDockWidget('Inspect / Layers / Source', self)
            dock.setObjectName('mesh_studio_inspector')
            dock.setAllowedAreas(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea |
                                 QtCore.Qt.DockWidgetArea.RightDockWidgetArea)
            self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, dock)
            container = QtWidgets.QWidget()
            panel = QtWidgets.QVBoxLayout(container)
            panel.setContentsMargins(12, 12, 12, 12)
            panel.setSpacing(10)
            self._source = QtWidgets.QLabel()
            self._source.setWordWrap(True)
            self._source.setTextInteractionFlags(
                QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
            panel.addWidget(self._source)

            group = QtWidgets.QGroupBox('Cell layers')
            vertical = QtWidgets.QVBoxLayout(group)
            self._tri_box = QtWidgets.QCheckBox('TRI / AFT')
            self._quad_box = QtWidgets.QCheckBox('QUAD')
            self._edges_box = QtWidgets.QCheckBox('Show indexed edges')
            self._tri_box.setChecked(True)
            self._quad_box.setChecked(True)
            self._edges_box.setChecked(True)
            for checkbox in (self._tri_box, self._quad_box, self._edges_box):
                vertical.addWidget(checkbox)
                checkbox.toggled.connect(self._on_visibility)
            panel.addWidget(group)

            chooser = QtWidgets.QGroupBox('Face selection')
            form = QtWidgets.QFormLayout(chooser)
            self._face_id = QtWidgets.QSpinBox()
            self._face_id.setSpecialValueText('None')
            self._face_id.setRange(-1, max(-1, len(self._document.faces)-1))
            self._face_id.setValue(-1)
            self._face_id.valueChanged.connect(self._on_face_spin)
            form.addRow('Source face ID', self._face_id)
            panel.addWidget(chooser)

            self._info = QtWidgets.QPlainTextEdit()
            self._info.setReadOnly(True)
            self._info.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
            self._info.setPlaceholderText('Select a face to inspect original indices, XYZ, UV and provenance.')
            panel.addWidget(self._info, stretch=1)
            dock.setWidget(container)

            tb = QtWidgets.QToolBar('Mesh commands')
            tb.setMovable(False)
            self.addToolBar(tb)
            for label, callback in [
                ('Open OBJ', self._open_obj),
                ('Reset cameras', self._reset_cameras),
                ('Save view recipe', self._save_scene),
                ('Load view recipe', self._load_scene),
                ('Capture 3D PNG', self._export_png),
            ]:
                action = QtGui.QAction(label, self)
                action.triggered.connect(callback)
                tb.addAction(action)
            self._source.setText(self._source_label())
            self.statusBar().showMessage('Real or synthetic input is displayed without source topology welding.')

        def _source_label(self) -> str:
            doc = self._document
            source = 'SYNTHETIC' if doc.synthetic else 'IMPORTED SOURCE — NOT GLOBAL CERTIFICATION'
            return (f'{source}\n{self._file.name}\n'
                    f'OBJ SHA-256 {doc.source_sha256}\n'
                    f'{doc.triangles} TRI / {doc.quads} QUAD / {len(doc.points)} points\n'
                    f'Patch ownership: {doc.patch_ownership} (never inferred from cell groups)')

        def _camera(self, renderer) -> CameraPose:
            camera = renderer.camera
            return CameraPose(tuple(camera.position), tuple(camera.focal_point),
                              tuple(camera.up), float(camera.parallel_scale),
                              bool(camera.GetParallelProjection()))

        def _capture_cameras(self) -> None:
            if self._render_ready:
                self._scene = replace(self._scene,
                                      camera_xyz=self._camera(self._xyz),
                                      camera_uv=self._camera(self._uv))

        @staticmethod
        def _apply_camera(renderer, pose: CameraPose | None) -> None:
            if pose is None:
                return
            camera = renderer.camera
            camera.position = pose.position
            camera.focal_point = pose.focal_point
            camera.up = pose.view_up
            camera.parallel_scale = pose.parallel_scale
            camera.SetParallelProjection(int(pose.parallel))
            renderer.renderer.ResetCameraClippingRange()

        def _draw(self, *, reset: bool = False) -> None:
            if not reset:
                self._capture_cameras()
            self._xyz.clear()
            self._uv.clear()
            count_xyz, count_uv = 0, 0
            for viewer, frame in ((self._xyz, 'xyz'), (self._uv, 'uv')):
                viewer.set_background('white')
                for element_type, color in (('quad', '#3A9BB8'), ('triangle', '#D0D7DE')):
                    batch = build_batch(self._document, self._scene,
                                        coordinates=frame, element_type=element_type)
                    if not batch.number_of_cells:
                        continue
                    vtk_mesh = as_vtk_polydata(batch)
                    mesh = pv.wrap(vtk_mesh)
                    viewer.add_mesh(mesh, color=color, show_edges=self._scene.show_edges,
                                    edge_color='#26384A', line_width=0.8,
                                    pickable=True, name=f'{frame}-{element_type}')
                    if frame == 'xyz':
                        count_xyz += batch.number_of_cells
                    else:
                        count_uv += batch.number_of_cells
                if frame == 'xyz':
                    viewer.add_text('PHYSICAL XYZ — shaded preview (not vector)',
                                    position='upper_left', font_size=10, color='#243748')
                    viewer.reset_camera()
                    if reset:
                        viewer.view_isometric()
                        viewer.reset_camera()
                    self._apply_camera(viewer, self._scene.camera_xyz)
                else:
                    viewer.add_text('SOURCE UV — per-corner, no implicit seams welded',
                                    position='upper_left', font_size=10, color='#243748')
                    if count_uv:
                        viewer.view_xy()
                        viewer.enable_parallel_projection()
                        viewer.reset_camera()
                    else:
                        viewer.add_text('UV data unavailable: no inferred coordinates',
                                        position='lower_left', font_size=10, color='#A64545')
                    self._apply_camera(viewer, self._scene.camera_uv)
                viewer.render()
            self._render_ready = True
            for viewer in (self._xyz, self._uv):
                try:
                    viewer.disable_picking()
                except (AttributeError, RuntimeError):
                    pass
                # Cell picking returns an extracted one-cell mesh with copied
                # source_face_id cell data, preserving the original OBJ identity.
                viewer.enable_element_picking(callback=self._on_picked,
                                              mode='cell', show=False,
                                              show_message=False,
                                              left_clicking=False)
            self._paint_selection()
            self.statusBar().showMessage(f'{count_xyz} visible XYZ cells / {count_uv} UV cells; right-click a face to inspect.')

        def _on_picked(self, picked) -> None:
            try:
                ids = picked.cell_data['source_face_id']
                if len(ids) != 1:
                    raise SceneError('ambiguous_pick')
                face_id = int(ids[0])
                self._scene = select_face(self._document, self._scene, face_id)
            except (AttributeError, KeyError, TypeError, IndexError, ValueError) as exc:
                self.statusBar().showMessage(f'Picking did not provide a unique source face: {exc}')
                return
            self._face_id.blockSignals(True)
            self._face_id.setValue(face_id)
            self._face_id.blockSignals(False)
            self._paint_selection()

        def _paint_selection(self) -> None:
            face_id = self._scene.selected_face
            for viewer, frame in ((self._xyz, 'xyz'), (self._uv, 'uv')):
                viewer.remove_actor(f'selection-{frame}', render=False)
                if face_id is not None:
                    kind = self._document.faces[face_id].element_type
                    selection = build_batch(self._document, self._scene,
                                            coordinates=frame, element_type=kind,
                                            selected_only=True)
                    if selection.number_of_cells:
                        viewer.add_mesh(pv.wrap(as_vtk_polydata(selection)),
                                        style='wireframe', color='#E78B18',
                                        line_width=5, pickable=False,
                                        name=f'selection-{frame}')
                viewer.render()
            if face_id is None:
                self._info.clear()
            else:
                detail = face_detail(self._document, face_id)
                if self._quality_cells is None and self._quality_error is None:
                    try:
                        self._quality_cells = analyze_mesh(self._document)["cells"]
                    except (QualityError, ValueError) as exc:
                        self._quality_error = str(exc)
                if self._quality_cells is not None:
                    detail["studio_derived_metrics"] = self._quality_cells[face_id]
                    detail["metric_provenance"] = "STUDIO_DERIVED_NO_SOURCE_SURFACE_ORACLE"
                elif self._quality_error is not None:
                    detail["metric_error"] = self._quality_error
                self._info.setPlainText(json.dumps(detail, indent=2, sort_keys=True))

        def _on_face_spin(self, value: int) -> None:
            try:
                self._scene = select_face(self._document, self._scene,
                                          None if value == -1 else value)
            except SceneError:
                self.statusBar().showMessage('Selected face is hidden; enable its layer first.')
                self._face_id.blockSignals(True)
                self._face_id.setValue(-1)
                self._face_id.blockSignals(False)
                self._scene = select_face(self._document, self._scene, None)
            self._paint_selection()

        def _on_visibility(self) -> None:
            self._scene = with_visibility(self._document, self._scene,
                                          triangles=self._tri_box.isChecked(),
                                          quads=self._quad_box.isChecked(),
                                          edges=self._edges_box.isChecked())
            self._face_id.blockSignals(True)
            self._face_id.setValue(self._scene.selected_face
                                   if self._scene.selected_face is not None else -1)
            self._face_id.blockSignals(False)
            self._draw()

        def _open_obj(self) -> None:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Open OBJ mesh', str(self._file.parent), 'Wavefront OBJ (*.obj)')
            if not filename:
                return
            try:
                document = import_obj(filename)
            except (OSError, ValueError, MeshImportError) as exc:
                QtWidgets.QMessageBox.warning(self, 'Invalid mesh', str(exc))
                return
            self._document = document
            self._quality_cells = None
            self._quality_error = None
            self._file = Path(filename)
            self._scene = initial_scene(document)
            self._render_ready = False
            self._face_id.blockSignals(True)
            self._face_id.setRange(-1, max(-1, len(document.faces)-1))
            self._face_id.setValue(-1)
            self._face_id.blockSignals(False)
            self._tri_box.blockSignals(True)
            self._quad_box.blockSignals(True)
            self._edges_box.blockSignals(True)
            self._tri_box.setChecked(True)
            self._quad_box.setChecked(True)
            self._edges_box.setChecked(True)
            for cb in (self._tri_box, self._quad_box, self._edges_box):
                cb.blockSignals(False)
            self._source.setText(self._source_label())
            self._draw(reset=True)

        def _reset_cameras(self) -> None:
            self._scene = replace(self._scene, camera_xyz=None, camera_uv=None)
            self._draw(reset=True)

        def _save_scene(self) -> None:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Save camera/layer recipe', '', 'Mesh Studio JSON (*.json)')
            if not filename:
                return
            self._capture_cameras()
            try:
                write_scene(filename, self._scene)
            except (OSError, SceneError) as exc:
                QtWidgets.QMessageBox.warning(self, 'Cannot save recipe', str(exc))

        def _load_scene(self) -> None:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Load camera/layer recipe', '', 'Mesh Studio JSON (*.json)')
            if not filename:
                return
            try:
                candidate = load_scene(filename, self._document)
            except (OSError, ValueError, SceneError) as exc:
                QtWidgets.QMessageBox.warning(self, 'Invalid recipe', str(exc))
                return
            self._scene = candidate
            for box, value in ((self._tri_box, candidate.show_tri),
                               (self._quad_box, candidate.show_quad),
                               (self._edges_box, candidate.show_edges)):
                box.blockSignals(True)
                box.setChecked(value)
                box.blockSignals(False)
            self._face_id.blockSignals(True)
            self._face_id.setValue(candidate.selected_face
                                   if candidate.selected_face is not None else -1)
            self._face_id.blockSignals(False)
            self._render_ready = False
            self._draw()

        def _export_png(self) -> None:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Save raster screenshot (NOT vector)', '', 'PNG image (*.png)')
            if not filename:
                return
            target = Path(filename)
            receipt = target.with_suffix('.audit.json')
            if target.exists() or receipt.exists():
                QtWidgets.QMessageBox.warning(self, 'File already exists',
                                               'Refusing to overwrite an existing image or audit.')
                return
            self._capture_cameras()
            self._xyz.screenshot(filename)
            import hashlib
            evidence = {
                'schema': 'apmesh.meshstudio.desktop_screenshot.v1',
                'source_sha256': self._document.source_sha256,
                'synthetic': self._document.synthetic,
                'image_type': 'RASTER_3D_PNG_NOT_VECTOR',
                'scene': json.loads(scene_json(self._scene)),
                'png_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            }
            receipt.write_text(json.dumps(evidence, sort_keys=True, indent=2) + '\n', encoding='utf-8')
            self.statusBar().showMessage('Saved RASTER PNG + audit; use the SVG pipeline for vector UV figures.')

        def closeEvent(self, event) -> None:
            self._xyz.close()
            self._uv.close()
            super().closeEvent(event)

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    default = Path(__file__).parent / 'fixtures' / 'real_p1' / 'accepted.obj'
    window = MeshStudioWindow(Path(obj_path) if obj_path is not None else default)
    window.show()
    if smoke_output is None:
        return app.exec()

    # This gate is deliberately not considered executed without real Qt/VTK.
    from .desktop_smoke import run_gui_smoke
    status = {"pass": False}

    def run_smoke_once() -> None:
        try:
            status["pass"] = run_gui_smoke(window, Path(smoke_output))
        finally:
            window.close()
            app.quit()

    QtCore.QTimer.singleShot(200, run_smoke_once)
    app.exec()
    return 0 if status["pass"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Open APMesh Mesh Studio desktop XYZ/UV preview')
    parser.add_argument('--obj', type=Path, help='Source Wavefront OBJ file (default: real P1)')
    parser.add_argument('--smoke-output', type=Path, help='Run bounded Qt GUI smoke and write JSON evidence')
    args = parser.parse_args(argv)
    try:
        return launch(args.obj, smoke_output=args.smoke_output)
    except (RuntimeError, OSError, ValueError) as exc:
        print(f'Mesh Studio desktop unavailable: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
