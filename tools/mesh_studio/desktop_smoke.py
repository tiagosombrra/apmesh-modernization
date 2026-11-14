"""Bounded, real Qt smoke harness; FAIL CLOSED if the GUI cannot be exercised.

This runner is invoked only inside an installed PySide6/PyVistaQt application.
Programmatic picking verifies the VTK-to-OBJ ID mapping; it does not claim
that a physical mouse click was independently calibrated on every platform.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import traceback

from .scene_model import load_scene, write_scene, visible_face_ids


def run_gui_smoke(window, destination: Path) -> bool:
    """Exercise actual Qt widgets, two VTK panes, filtering and camera persistence."""
    result = {
        "schema": "apmesh.meshstudio.qt_smoke.v1",
        "status": "FAIL",
        "source_sha256": window._document.source_sha256,
        "checks": [],
        "limits": ["Programmatic face selection is not a physical mouse-pick qualification."],
    }
    try:
        from .scene_vtk import as_vtk_polydata
        from .scene_model import build_batch
        import pyvista as pv

        checks = result["checks"]
        assert window.isVisible() and window._xyz.isVisible() and window._uv.isVisible()
        checks.append("visible_dual_panes")
        assert len(visible_face_ids(window._document, window._scene)) == 78
        checks.append("original_78_cells")

        window._tri_box.setChecked(False)
        assert len(visible_face_ids(window._document, window._scene)) == 42
        window._tri_box.setChecked(True)
        window._quad_box.setChecked(False)
        assert len(visible_face_ids(window._document, window._scene)) == 36
        window._quad_box.setChecked(True)
        checks.append("qt_toggle_callbacks_and_cell_filters")

        window._face_id.setValue(45)
        assert window._scene.selected_face == 45
        assert 'TRI_AFT' in window._info.toPlainText()
        checks.append("qt_spinbox_original_face_selection")

        # Exercise the same event callback used by PyVista element picking.
        picked = pv.wrap(as_vtk_polydata(build_batch(
            window._document, window._scene, coordinates='xyz',
            element_type='triangle', selected_only=True)))
        window._on_picked(picked)
        assert window._scene.selected_face == 45
        checks.append("vtk_cell_data_pick_callback")

        window._capture_cameras()
        scene = window._scene
        assert scene.camera_xyz is not None and scene.camera_uv is not None
        view_path = destination.with_suffix('.scene.json')
        write_scene(view_path, scene)
        assert load_scene(view_path, window._document) == scene
        checks.append("two_camera_recipe_roundtrip")

        window._reset_cameras()
        window._scene = load_scene(view_path, window._document)
        window._render_ready = False
        window._draw()
        checks.append("reset_and_restore_actual_renderers")

        raster = destination.with_suffix('.png')
        if raster.exists():
            raise FileExistsError(raster)
        window._xyz.screenshot(str(raster))
        data = raster.read_bytes()
        assert data.startswith(b'\x89PNG\r\n\x1a\n') and len(data) > 1000
        result["raster_png_sha256"] = hashlib.sha256(data).hexdigest()
        checks.append("actual_vtk_qt_screenshot_raster_only")

        result["status"] = "PASS_PROGRAMMATIC_GUI_SMOKE"
    except Exception as exc:
        result["error"] = str(exc)
        result["traceback"] = traceback.format_exc(limit=5)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x', encoding='utf-8') as out:
        json.dump(result, out, indent=2, sort_keys=True)
        out.write('\n')
    return result["status"] == "PASS_PROGRAMMATIC_GUI_SMOKE"
