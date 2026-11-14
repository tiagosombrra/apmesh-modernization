"""Optional VTK bridge; the scientific core never imports VTK or Qt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .model import MeshDocument
from .scene_model import (CameraPose, GeometryBatch, SceneState,
                          build_batch, initial_scene, scene_json)


def as_vtk_polydata(batch: GeometryBatch):
    """Preserve original per-cell face ID and native triangle/quad polygons."""
    from vtkmodules.vtkCommonCore import vtkIdTypeArray, vtkPoints
    from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkPolyData

    points = vtkPoints()
    points.SetDataTypeToDouble()
    for xyz in batch.points:
        points.InsertNextPoint(*xyz)
    faces = vtkCellArray()
    source_ids = vtkIdTypeArray()
    source_ids.SetName('source_face_id')
    for face, source_id in zip(batch.faces, batch.source_face_ids, strict=True):
        faces.InsertNextCell(len(face))
        for vertex_id in face:
            faces.InsertCellPoint(vertex_id)
        source_ids.InsertNextValue(source_id)
    poly = vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(faces)
    poly.GetCellData().AddArray(source_ids)
    return poly


def make_vtk_actors(document: MeshDocument, state: SceneState, *, coordinates: str):
    """Return typed (element type, vtkPolyData) pairs, excluding empty groups."""
    result = []
    for kind in ('quad', 'triangle'):
        batch = build_batch(document, state, coordinates=coordinates, element_type=kind)
        if batch.number_of_cells:
            result.append((kind, as_vtk_polydata(batch)))
    return result


def screenshot_3d(document: MeshDocument, destination: Path | str, *,
                  state: SceneState | None = None, width: int = 1100,
                  height: int = 830) -> dict:
    """Render a real XYZ screenshot. The output is raster PNG, NOT vector PDF.

    Requires a functional VTK EGL/OSMesa/OpenGL environment. The PNG may vary
    by GPU and driver; no cross-platform byte-identity is claimed.
    """
    from vtkmodules.vtkRenderingCore import (vtkActor, vtkPolyDataMapper,
                                             vtkRenderer, vtkRenderWindow, vtkWindowToImageFilter)
    from vtkmodules.vtkIOImage import vtkPNGWriter
    import vtkmodules.vtkRenderingOpenGL2  # noqa: F401

    output = Path(destination)
    if output.exists() or output.with_suffix('.audit.json').exists():
        raise FileExistsError(str(output))
    if not (320 <= width <= 4096 and 320 <= height <= 4096):
        raise ValueError('unsupported_image_size')
    state = state or initial_scene(document)
    renderer = vtkRenderer()
    renderer.SetBackground(1.0, 1.0, 1.0)
    scene_count = 0
    for kind, mesh in make_vtk_actors(document, state, coordinates='xyz'):
        mapper = vtkPolyDataMapper()
        mapper.SetInputData(mesh)
        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*( (0.28, 0.62, 0.72) if kind == 'quad'
                                        else (0.83, 0.85, 0.88)))
        actor.GetProperty().SetEdgeColor(0.18, 0.24, 0.30)
        actor.GetProperty().SetEdgeVisibility(bool(state.show_edges))
        actor.GetProperty().SetLineWidth(0.8)
        renderer.AddActor(actor)
        scene_count += mesh.GetNumberOfPolys()
    if scene_count == 0:
        raise ValueError('no_visible_cells')
    window = vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(width, height)
    window.AddRenderer(renderer)
    renderer.ResetCamera()
    if state.camera_xyz is None:
        # Deliberately oblique, so curved source geometry is visibly 3D.
        camera = renderer.GetActiveCamera()
        camera.Azimuth(33.0)
        camera.Elevation(28.0)
        camera.OrthogonalizeViewUp()
        renderer.ResetCameraClippingRange()
    if state.camera_xyz is not None:
        cam = renderer.GetActiveCamera()
        p = state.camera_xyz
        cam.SetPosition(*p.position)
        cam.SetFocalPoint(*p.focal_point)
        cam.SetViewUp(*p.view_up)
        cam.SetParallelProjection(int(p.parallel))
        cam.SetParallelScale(p.parallel_scale)
        renderer.ResetCameraClippingRange()
    window.Render()
    capture = vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetInputBufferTypeToRGB()
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtkPNGWriter()
    writer.SetFileName(str(output))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    if not output.is_file() or output.stat().st_size < 100:
        raise RuntimeError('vtk_render_failed')
    payload = {
        'schema': 'apmesh.meshstudio.raster_preview.v1',
        'input_sha256': document.source_sha256,
        'synthetic': document.synthetic,
        'image_format': 'PNG_RASTER_3D_NOT_VECTOR',
        'visible_cells': scene_count,
        'quads': sum(f.element_type=='quad' for f in document.faces if state.show_quad),
        'triangles': sum(f.element_type=='triangle' for f in document.faces if state.show_tri),
        'png_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'camera_recipe_sha256': hashlib.sha256(scene_json(state).encode()).hexdigest(),
        'hardware_independent_bytes': False,
    }
    audit_path = output.with_suffix('.audit.json')
    with audit_path.open('x', encoding='utf-8') as stream:
        json.dump(payload, stream, sort_keys=True, indent=2)
        stream.write('\n')
    return payload
