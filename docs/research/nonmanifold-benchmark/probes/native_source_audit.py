#!/usr/bin/env python3
"""Evidence-first Open CASCADE audit and native STEP surface gallery.

Only original pinned CAD files are imported. No model is reclassified as
non-manifold or converted into APMesh BP from render-only evidence.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import cadquery as cq
import vtk
from PIL import Image, ImageDraw, ImageFont
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer, TopExp
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool

ROOT = Path(os.environ.get('APMESH_REAL_CAD_WORKSPACE', Path(__file__).parent))
SOURCE_DIR = ROOT / 'sources'
RESULT_DIR = ROOT / 'output'
RESULT_DIR.mkdir(parents=True, exist_ok=True)
REV = '8f00f02579037cc893042f2ee2c910b20e3fb1b0'
CASES = {
    'M5': ('i05o_m5.step', 'd72e5e3cb3de9ebdec80253cfa9b57fa1b7132f7'),
    'S40': ('i25o_s40.step', '917ef72a0a91b8b3e7d16e8009a1b1655154174a'),
    'S27': ('i22o_s27.step', '48ada34a4d2fb038ff91131300c6262a9faec217'),
    'M3': ('i03o_m3.step', 'e472dd5b717b2fdbc7d2bd3e030a856a257d0cb3'),
}
# Fixed source-type categories are printed, not interpreted as mesh element types.
TYPES = {
    'PLANE': (0.69, 0.75, 0.82),
    'CYLINDER': (0.25, 0.56, 0.82),
    'CONE': (0.92, 0.55, 0.25),
    'TORUS': (0.61, 0.44, 0.84),
    'BSPLINE': (0.30, 0.74, 0.60),
    'OTHER': (0.82, 0.35, 0.57),
}


def font(size: int, bold: bool = False):
    folders = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold
        else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for path in folders:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def sha_git(path: Path):
    return subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()


def incident_faces(shape):
    """Count DISTINCT Open CASCADE face users of each exact native edge object."""
    group = []
    repeated_uses = 0
    faces = shape.Faces()
    for i, face in enumerate(faces):
        local = []
        explorer = TopExp_Explorer(face.wrapped, TopAbs_EDGE)
        while explorer.More():
            edge = explorer.Current()
            same = next((z for z in local if z.IsSame(edge)), None)
            if same is not None:
                repeated_uses += 1
            else:
                local.append(edge)
            explorer.Next()
        for edge in local:
            found = next((g for g in group if g[0].IsSame(edge)), None)
            if found is None:
                found = [edge, set()]
                group.append(found)
            found[1].add(i)
    return group, repeated_uses


def face_record(face, index):
    wires = face.Wires()
    wire_lengths = [len(w.Edges()) for w in wires]
    geom = face.geomType()
    # One planar four-linear-edge loop is a restricted candidate, not proof
    # of a kernel-independent exact BP feature-boundary mapping.
    straight_quad = (geom == 'PLANE' and len(wires) == 1
                     and wire_lengths == [4]
                     and all(edge.geomType() == 'LINE' for edge in wires[0].Edges())
                     and len(face.Vertices()) == 4)
    ctr = face.Center()
    return {
        'index': index, 'geometry_type': geom,
        'area_native_units_squared': face.Area(),
        'wire_count': len(wires),
        'wire_edge_counts': wire_lengths,
        'unique_face_vertices': len(face.Vertices()),
        'planar_four_straight_sides_candidate': straight_quad,
        'center_xyz': [ctr.x, ctr.y, ctr.z],
    }


def type_colored_mesh(shape, tolerance):
    """Retessellate ORIGINAL CAD faces, carrying surface type color scalars."""
    append = vtk.vtkAppendPolyData()
    rgb_by_cell = []
    for face in shape.Faces():
        poly = face.toVtkPolyData(tolerance=tolerance, angularTolerance=0.15)
        if not poly.GetNumberOfCells():
            continue
        append.AddInputData(poly)
        rgb = TYPES.get(face.geomType(), TYPES['OTHER'])
        rgb_by_cell.extend([tuple(round(255 * v) for v in rgb)] * poly.GetNumberOfCells())
    append.Update()
    output = vtk.vtkPolyData()
    output.ShallowCopy(append.GetOutput())
    scalars = vtk.vtkUnsignedCharArray()
    scalars.SetName('source_face_type_rgb')
    scalars.SetNumberOfComponents(3)
    for rgb in rgb_by_cell:
        scalars.InsertNextTuple3(*rgb)
    if scalars.GetNumberOfTuples() != output.GetNumberOfCells():
        raise ValueError('Native face-to-mesh attribute alignment error')
    output.GetCellData().SetScalars(scalars)
    return output


def real_edge_wireframe(shape):
    """Sample actual native CAD edges; do not display triangulation edges."""
    points = vtk.vtkPoints()
    line_cells = vtk.vtkCellArray()
    for edge in shape.Edges():
        try:
            count = 2 if edge.geomType() == 'LINE' else 35
            samples = edge.sample(count)[0]
            if len(samples) < 2:
                continue
            polyline = vtk.vtkPolyLine()
            polyline.GetPointIds().SetNumberOfIds(len(samples))
            for idx, sample in enumerate(samples):
                pid = points.InsertNextPoint(sample.x, sample.y, sample.z)
                polyline.GetPointIds().SetId(idx, pid)
            line_cells.InsertNextCell(polyline)
        except Exception:
            continue
    output = vtk.vtkPolyData()
    output.SetPoints(points)
    output.SetLines(line_cells)
    return output


def render(shape, title: str, output_path: Path, *, colored=False, size=(780, 680)):
    diag = shape.BoundingBox().DiagonalLength
    tolerance = max(0.03, diag * 0.004)
    mesh = type_colored_mesh(shape, tolerance) if colored else shape.toVtkPolyData(
        tolerance=tolerance, angularTolerance=0.15)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(mesh)
    if colored:
        mapper.ScalarVisibilityOn()
        mapper.SetColorModeToDirectScalars()
        mapper.SetScalarModeToUseCellData()
    else:
        mapper.ScalarVisibilityOff()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.73, 0.81, 0.89)
    actor.GetProperty().SetAmbient(0.16)
    actor.GetProperty().SetDiffuse(0.75)
    actor.GetProperty().SetSpecular(0.20)
    actor.GetProperty().SetSpecularPower(22)
    actor.GetProperty().SetInterpolationToPhong()
    edge_mapper = vtk.vtkPolyDataMapper()
    edge_mapper.SetInputData(real_edge_wireframe(shape))
    edge_actor = vtk.vtkActor()
    edge_actor.SetMapper(edge_mapper)
    edge_actor.GetProperty().SetColor(0.17, 0.25, 0.34)
    edge_actor.GetProperty().SetLineWidth(1.2)
    edge_actor.GetProperty().SetOpacity(0.82)
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.98, 0.985, 0.99)
    renderer.AddActor(actor)
    renderer.AddActor(edge_actor)
    light = vtk.vtkLight()
    light.SetLightTypeToSceneLight()
    light.SetPosition(1, 2, 5)
    light.SetFocalPoint(0, 0, 0)
    light.SetIntensity(0.65)
    renderer.AddLight(light)
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.AddRenderer(renderer)
    window.SetSize(*size)
    window.SetMultiSamples(4)
    renderer.ResetCamera()
    camera = renderer.GetActiveCamera()
    camera.SetParallelProjection(True)
    camera.Azimuth(40 if title != 'S40' else 28)
    camera.Elevation(28 if title != 'M3' else 18)
    camera.Roll(-5 if title == 'S40' else 0)
    renderer.ResetCamera()
    renderer.ResetCameraClippingRange()
    window.Render()
    grab = vtk.vtkWindowToImageFilter()
    grab.SetInput(window)
    grab.ReadFrontBufferOff()
    grab.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(output_path))
    writer.SetInputConnection(grab.GetOutputPort())
    writer.Write()
    if not output_path.exists() or output_path.stat().st_size < 2000:
        raise RuntimeError('Offscreen native CAD rendering failed')
    return {'source_face_mesh_cells': mesh.GetNumberOfCells(),
            'wireframe_source_edge_count': len(shape.Edges()),
            'linear_tessellation_deflection': tolerance,
            'renderer': 'VTK 9.6.2 offscreen using CadQuery/Open CASCADE STEP importer',
            'camera_azimuth_deg': 40 if title != 'S40' else 28,
            'camera_elevation_deg': 28 if title != 'M3' else 18}


def caption_image(label, report, source_png, color_png):
    w, h = 1580, 815
    out = Image.new('RGB', (w, h), (249, 251, 254))
    draw = ImageDraw.Draw(out)
    header = (label + ' | MAMBO original CAD / HexMe')
    draw.text((34, 22), header, fill=(26, 40, 57), font=font(31, True))
    short = report['raw_sha256'][:16]
    draw.text((34, 68), f"STEP original  •  SHA-256 {short}…  •  {report['faces']} faces / {report['edges']} edges (incl. degenerate)", fill=(73, 88, 106), font=font(18))
    images = [Image.open(source_png).convert('RGB'), Image.open(color_png).convert('RGB')]
    for i, img in enumerate(images):
        x = 15 + i * 780
        out.paste(img, (x, 102))
    draw.text((30, 782), 'ORIGINAL CAD — shaded STEP solid', fill=(47, 66, 84), font=font(18, True))
    draw.text((820, 782), 'ORIGINAL CAD — support surface classification', fill=(47, 66, 84), font=font(18, True))
    dest = RESULT_DIR / f'{label.lower()}_source_cad.png'
    out.save(dest, optimize=True)
    return dest


def audit_one(label, name, sha):
    p = SOURCE_DIR/name
    if sha_git(p) != sha:
        raise ValueError(f'Original Git blob did not match {name}')
    src_hash = sha256(p.read_bytes()).hexdigest()
    wp = cq.importers.importStep(str(p))
    shape = wp.val()
    faces = shape.Faces()
    native_edges, repeats = incident_faces(shape)
    native_map = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape.wrapped, TopAbs_EDGE, native_map)
    degenerate_count = sum(BRep_Tool.Degenerated_s(TopoDS.Edge_s(native_map.FindKey(i)))
                           for i in range(1, native_map.Extent()+1))
    if native_map.Extent() != len(native_edges):
        raise ValueError('BRep face traversal differs from topological edge map')
    if native_map.Extent() - degenerate_count != len(shape.Edges()):
        raise ValueError('CadQuery nondegenerate edge count disagrees with BRep graph')
    if b'SI_UNIT(.MILLI.,.METRE.)' not in p.read_bytes():
        raise ValueError('Pinned STEP does not declare millimetre length units')
    hist = Counter(len(item[1]) for item in native_edges)
    face_records = [face_record(f, i) for i, f in enumerate(faces)]
    bounds = shape.BoundingBox()
    result = {
        'model_id': label,
        'source_file': name,
        'source_repo': 'cgg-bern/hex-me-if-you-can',
        'source_revision': REV,
        'source_blob_sha1': sha,
        'raw_sha256': src_hash,
        'raw_bytes': p.stat().st_size,
        'importer': 'CadQuery 2.8.0 / OCP 7.9.3.1 / OCCT STEPControl',
        'shape_type': shape.ShapeType(),
        'valid_native_cad': bool(shape.isValid()),
        'solids': len(shape.Solids()),
        'shells': len(shape.Shells()),
        'faces': len(faces),
        'edges': len(native_edges),
        'nondegenerate_edges': len(shape.Edges()),
        'native_degenerate_edges': degenerate_count,
        'source_length_unit': 'millimetre (STEP LENGTH_UNIT SI_UNIT .MILLI. .METRE.)',
        'vertices': len(shape.Vertices()),
        'volume_native_units_cubed': shape.Volume(),
        'surface_area_native_units_squared': shape.Area(),
        'bounding_box_native_units': {
            'xmin': bounds.xmin, 'xmax': bounds.xmax,
            'ymin': bounds.ymin, 'ymax': bounds.ymax,
            'zmin': bounds.zmin, 'zmax': bounds.zmax,
            'diagonal': bounds.DiagonalLength,
        },
        'surface_geom_types': dict(Counter(f.geomType() for f in faces)),
        'edge_types': dict(Counter(e.geomType() for e in shape.Edges())),
        'face_to_exact_topods_edge_incidence_histogram': dict(sorted(hist.items())),
        'explicit_native_edge_three_plus_distinct_faces': sum(n for k,n in hist.items() if k >= 3),
        'repeated_native_oriented_edge_uses_within_face': repeats,
        'outer_and_hole_trim_wire_counts': dict(Counter(len(f.Wires()) for f in faces)),
        'planar_four_straight_edge_candidate_face_count': sum(f['planar_four_straight_sides_candidate'] for f in face_records),
        'source_face_records': face_records,
        'topology_status': 'NATIVE_SOURCE_BREP_INSPECTED_NO_3PLUS_TOPODS_EDGE',
        'independent_multisheet_admission': 'NOT_GRANTED',
        'bicubic_fit': 'NOT_RUN',
        'apmesh_tri_quad_generation': 'NOT_RUN',
    }
    if not result['valid_native_cad'] or result['solids'] != 1:
        raise RuntimeError(f'Unexpected model validity for {name}')
    src_img = RESULT_DIR / f'{label.lower()}_shaded.png'
    clr_img = RESULT_DIR / f'{label.lower()}_support_types.png'
    result['rendering'] = {
        'shaded': render(shape, label, src_img),
        'face_geometry': render(shape, label, clr_img, colored=True),
    }
    result['rendered_from_actual_source_sha256'] = src_hash
    dest = RESULT_DIR / f'{label.lower()}_native_receipt.json'
    dest.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    panel = caption_image(label, result, src_img, clr_img)
    print(label, 'DONE', {
        'sha': src_hash, 'valid': result['valid_native_cad'],
        'solid': result['solids'], 'faces': result['faces'], 'edges': result['edges'],
        'face_supports': result['surface_geom_types'],
        'topology_hist': result['face_to_exact_topods_edge_incidence_histogram'],
        'planar_candidate': result['planar_four_straight_edge_candidate_face_count'],
        'panel': str(panel)
    }, flush=True)
    return result


def make_gallery(results):
    gallery = Image.new('RGB', (1660, 1450), (247, 249, 252))
    d = ImageDraw.Draw(gallery)
    d.text((40, 22), 'MAMBO / HexMe — real CAD models imported from original STEP', fill=(22, 38, 58), font=font(31, True))
    d.text((40, 68), 'Open CASCADE native B-Rep validation | shaded render + source face geometry classification', fill=(79, 96, 116), font=font(18))
    sub = {'M5':'cone / cylinder / torus', 'S40':'B-spline / cylinder / plane', 'S27':'dense mechanical features', 'M3':'many cylindrical features'}
    for index, report in enumerate(results):
        label = report['model_id']
        row, col = divmod(index, 2)
        px, py = 40 + col * 820, 126 + row * 616
        tile = Image.new('RGB', (790, 584), 'white')
        td = ImageDraw.Draw(tile)
        td.rounded_rectangle((0,0,789,583), radius=18, outline=(223,230,239), width=2)
        td.text((20,15), f'{label}  |  {sub[label]}', font=font(22, True), fill=(35, 52, 72))
        td.text((20,51), f"{report['faces']} faces • {report['edges']} edges • SHA-256 {report['raw_sha256'][:12]}...",font=font(16),fill=(89,106,124))
        shaded=Image.open(RESULT_DIR / f'{label.lower()}_shaded.png').convert('RGB')
        color=Image.open(RESULT_DIR / f'{label.lower()}_support_types.png').convert('RGB')
        for i, im in enumerate([shaded, color]):
            im=im.resize((388, 445))
            tile.paste(im,(7+394*i,82))
        td.text((18,545),'Original solid',font=font(16,True),fill=(44,62,80))
        td.text((415,545),'CAD face-support types',font=font(16,True),fill=(44,62,80))
        gallery.paste(tile,(px,py))
    legend_y=1380
    lg=ImageDraw.Draw(gallery)
    lg.text((40,legend_y),'FACE SUPPORT:',font=font(17,True),fill=(45,60,80))
    x=215
    for name,color in TYPES.items():
        if name=='OTHER':continue
        rgb=tuple(round(v*255) for v in color)
        lg.rounded_rectangle((x,legend_y+1,x+19,legend_y+19),radius=4,fill=rgb)
        lg.text((x+26,legend_y),name,font=font(16),fill=(50,67,83))
        x+=160
    lg.text((40,1415),'Source CAD / feature inspection only — these are NOT TRI, QUAD or all-quad meshes generated by APMesh.',font=font(15),fill=(89,97,112))
    path=RESULT_DIR/'mambo_originals_native_gallery.png'
    gallery.save(path,optimize=True)
    return path


if __name__ == '__main__':
    results=[]
    for label,(name,git_blob) in CASES.items():
        results.append(audit_one(label,name,git_blob))
    path=make_gallery(results)
    summary={r['model_id']:{k:r[k] for k in ('raw_sha256','faces','edges','solids','valid_native_cad','surface_geom_types','face_to_exact_topods_edge_incidence_histogram','planar_four_straight_edge_candidate_face_count')} for r in results}
    (RESULT_DIR/'native_source_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print('GALLERY',path,'SIZE',path.stat().st_size,flush=True)
