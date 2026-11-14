# Mesh Studio S4: two-view desktop candidate and real XYZ rendering

Date: 2026-11-14. Delivery branch: `feature/mesh-studio-fixture-first-20261114`.

## Scope actually implemented

- Added headless `scene_model.py`: immutable TRI/QUAD scene layers; per-cell source ID; original XYZ indices; **per-corner UV with explicit duplication**; face detail; strict camera/visibility recipes bound to the original OBJ SHA-256. No Qt/VTK import in the scene model.
- Added optional `scene_vtk.py`: actual VTK polygons retaining `source_face_id` cell data, and offscreen *raster* PNG visualization with provenance/audit JSON. Source TRI and QUAD remain independent native cells.
- Added `render3d_cli.py`: headless full XYZ rendering, layer filtering, source-bound scene recipes, refusal of overwrites and explicit raster disclosure.
- Added `desktop_app.py`: optional PySide6 + pyvistaqt two-view desktop, physical XYZ and source UV, TRI/QUAD layers and edges, original-face picker and ID-based selection, per-cell Studio quality details with distinct metric provenance, camera recipe persistence, safe OBJ open, raster PNG capture and audit.
- Added 21 independent headless/VTK tests and expanded documentation and dependency candidate constraints.

## Exact real source

`tools/mesh_studio/fixtures/real_p1/accepted.obj` is the real PR #217 controlled Bezier P1 file, SHA-256 `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.

Input: 69 source XYZ nodes, 42 original QUAD, 36 original native-AFT TRI, 78 indexed faces, and per-corner UV. VTK native offscreen EGL rendering is an independently executed integration result; it does not prove that a Qt window works. VTK screenshot is `PNG_RASTER_3D_NOT_VECTOR`, not a print-ready vector figure. The previous actual-source UV SVG is the vector path and remains unchanged.

## Local execution record

- Existing S0–S3 suite: 53 passed before changes.
- New S4 headless scene and VTK suite: 21 passed including native EGL offscreen 3D screenshot and masked-QUAD-only image.
- Combined S0–S4 suite: **74 tests passed** on Python 3.13 and VTK 9.6.2 in the provided environment; no tests were ignored in that command.
- Real OBJ source inventory and `source_face_id` VTK cell metadata tested; also negative camera, visibility, invalid recipe, nonwelding and missing UV checks.
- Headless 3D screenshot from actual P1 generated with source audit. GPU/driver pixel determinism is *not* claimed.
- PySide6, PyVista, and pyvistaqt **NOT installed** in this environment; their installation attempt failed due to unavailable package network. Therefore **interactive desktop startup, real cell-picking and Qt shutdown/ABI** are **UNQUALIFIED**. No fake green GUI result.
- No Windows build, desktop packaging, macOS, cross-platform VTK screenshot equality, journal PDF or new source generator CTest was executed.

## Reproduce headless checks

From repository root:

```sh
python -m unittest tools.mesh_studio.test_studio tools.mesh_studio.test_storyboards tools.mesh_studio.test_quality_analysis tools.mesh_studio.test_real_p1 tools.mesh_studio.test_desktop_stage -v
python -m tools.mesh_studio.fixtures.validate
python -m tools.mesh_studio.render3d_cli tools/mesh_studio/fixtures/real_p1/accepted.obj --png build/mesh-studio/p1_xyz_preview.png
```

The output parent must exist. The output PNG and `p1_xyz_preview.audit.json` must **not** exist, to avoid silent overwrites.

Optional desktop run, **only in an environment with tested Qt/VTK ABI and graphics**:

```sh
python -m pip install -r tools/mesh_studio/requirements-desktop.in
python -m tools.mesh_studio.desktop_app --obj tools/mesh_studio/fixtures/real_p1/accepted.obj
```

The `.in` package ranges are candidates, **not a qualified lockfile**. Validate on the actual release Python/Qt/VTK versions and capture an exact lock. If dependencies are missing, desktop CLI exits 2 with a diagnostic, while headless tools remain importable.

## Technical constraints and open review gates

1. Do not treat `QUAD`/`TRI_AFT` OBJ groups as different source patches or authorize global welding across nonmanifold sheets.
2. UV is represented by per-face-corner coordinates; duplicate UV positions do not imply distinct physical source nodes and duplicated physical positions do not imply one node.
3. Selected face reports use independent Studio metrics **without certified source normal**, never claim global physical Jacobian/surface validity.
4. The optional PyVista `enable_element_picking` callback depends on Qt/VTK. Verify that extracted `source_face_id` survives actual mouse picking on Windows and Linux before closing full S4.
5. In S4b, run genuine Qt desktop smoke tests: first open, two-view draw, filter toggles, one 3D pick, one UV pick, selected-cell metrics, scene JSON save/load, invalid source rejection, screenshot/audit, repeated open/close, memory/ABI and GPU fallback.
6. No new generator or original `main`, `quad-templates`, production CMake, or scientific source files were edited by this stage.

Classification: **S4a delivered (headless VTK + desktop implementation); S4b GUI runtime qualification remains open**. Next after Qt qualification is S5 measured multi-mesh comparison and publication pipeline.
