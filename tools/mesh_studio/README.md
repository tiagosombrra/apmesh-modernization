# APMesh Mesh Studio — scientific inspection and publication modules S0–S5

This project is isolated under `tools/mesh_studio/`, with no generator production changes.

## Initial research-safe deliverables

- Synthetic immutable V1 fixture corpus and standalone oracle in `fixtures/`.
- Scientific typed `MeshDocument` with source vertices, typed TRI/QUAD faces, per-corner UV and explicit patch/source provenance.
- Bounded Wavefront OBJ importer with distinct legacy APMesh counting dialect and synthetic JSON sidecars.
- Headless vector-only SVG figure generation using actual source UV coordinates. An SVG with raster data or active content fails audit.
- Regression against 10 known-valid and 6 deliberate-invalid synthetic cases, parser mutations and figure deterministic reproduction.

```sh
python tools/mesh_studio/fixtures/generate.py
python tools/mesh_studio/fixtures/validate.py
python -m unittest tools.mesh_studio.test_studio -v
python -m tools.mesh_studio.cli \
  tools/mesh_studio/fixtures/cases/synthetic_quad_aft_transition.obj \
  --svg build/mesh-studio/synthetic_hybrid_uv.svg
```

All generated synthetic results must remain explicitly labeled **SYNTHETIC**, not reported as output from the actual APMesh generator. The original source `P1` model, real all-quad algorithm, anisotropic generator, vector PDF, GUI and scientific multi-epoch comparison are *not* claimed by this S0/S1 starter.

A generic OBJ lacking UV is parsed for geometry, but is not silently projected to fake UV coordinates. The importer does not infer source curve topology or model-global welding from coincident XYZ positions.

## S1b: reproducible synthetic technique storyboards

The three new storyboards are **synthetic instructional scenes**, not a capture
of generator execution, nor results measured in the paper. They are standalone
SVG path/polygon/ellipse vector drawings and require no Qt/VTK/GPU:

```bash
python -m unittest tools.mesh_studio.test_studio tools.mesh_studio.test_storyboards -v
python -m tools.mesh_studio.fixtures.validate
python -m tools.mesh_studio.storyboard_cli all --output-dir figures/mesh_studio
```

The command generates:

- `hybrid_synthetic.svg`: six illustrated stages of the existing 1-QUAD/8-TRI fixture, including a separate biquadratic *synthetic* lift in the last panel; the quadtree and front stages are **simulated** rather than recorded AFT operations.
- `all_quad_synthetic.svg`: actual 2x2 quad-grid boundary incidence (8 boundary edges) compared with a **fixed** five-edge disk where conforming all-quad is impossible under stated assumptions; necessary, not sufficient, existence criterion.
- `anisotropy_synthetic.svg`: exact unit ellipses for the prescribed synthetic metrics `I` and `diag(16,1)`; no APMesh anisotropic adapter is claimed.

Each `.svg` has an adjacent `.audit.json` with SHA-256, panel count, provenance
and the mathematical control data. SVG passes the existing raster/active-content
check, but **no PDF/PGF/LaTeX export has been qualified**. PNG files included
with the release example are previews, not the publication originals.

The metric example uses `Metric2D` defined in `metric2d.py`; original field
frame, units, tensor source and rotation must be supplied when real APMesh
measurements eventually become available. Local geometry is not a proof of
continuous physical Jacobian validity. All-quad and tensor-driven adaptation
remain scientific development goals, not released generator modes.

## S2: independently testable physical/UV quality and indexed topology

No Qt, VTK, NumPy or GPU is needed to analyze the initial fixture corpus.
The analysis API never silently converts a QUAD into TRI elements in the
canonical mesh. For a nonplanar QUAD its reported area is explicitly the sum
of the two discrete facets along diagonal `(0, 2)`, **not** the original
curved surface area. A planar Jacobian score is `null` for nonplanar cells.

```bash
python -m unittest \
  tools.mesh_studio.test_studio \
  tools.mesh_studio.test_storyboards \
  tools.mesh_studio.test_quality_analysis -v
python -m tools.mesh_studio.analyze_cli \
  tools/mesh_studio/fixtures/cases/synthetic_quad_aft_transition.obj \
  --output build/mesh-studio/synthetic_hybrid_quality.json \
  --metric-diagonal 16 1
```

`quality_analysis.analyze_mesh()` reports normalized triangle mean-ratio
(shape only), physical facet area, planar-QUAD minimum scaled Jacobian,
relative coplanarity, indexed topology and separate distributions. The
historical article's triangle quality score is **not automatically equal**
to the independently defined mean ratio here. No common TRI+QUAD quality
average is produced.

An optional `source_normal(u,v)` callback audits physical facet orientation
only at the two facet centroids of a QUAD; it does not prove global
orientation of a Bezier surface. The callback and optional 2D SPD field are
caller-supplied, not authenticated measurements of the generator. An
anisotropic field must explicitly declare `metric_frame='uv'`, and the
example CLI metric is labeled USER_SUPPLIED_NOT_ORIGINAL_GENERATOR_FIELD.

OBJ groups are **not necessarily patch IDs**. In the controlled P1 export,
`QUAD` and `TRI_AFT` classify cells of the same source patch. The topology
report therefore contains group-local connectivity and an additional joined
**indexed** face-complex assessment when no patch-owner sidecar exists.
Neither indexed joining nor coincident XYZ values authorize welding of
nonmanifold source sheets. Synthetic multi-patch examples use validated
sidecar ownership to prevent accidental global identity inference.

The report is suitable for measurement and diagnostic presentation, not yet
scientific certification. Vector figure generation remains S1/S1b. Source
P1 integration, actual recorded adaptive epochs, all-quad execution,
tensor-driven generation, PDF/PGF publishing and desktop GUI remain open.


## S3: controlled real P1 source integration (not a synthetic fixture)

The exact PR #217 `accepted.obj` from the successful Linux/Windows source CI is
checked into `fixtures/real_p1/`. The original OBJ has 69 physical nodes, 42
interior QUAD and 36 native original AFT TRI; the 16-edge outer boundary and
20-edge QUAD/TRI interface are independently audited. Its original SHA-256 is
`cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.

Run the source control-net oracle, geometry, connectivity, quality and **real**
UV publication figure from the repository root:

```bash
python -m tools.mesh_studio.real_p1_cli --output-dir /tmp/apmesh-real-p1-figure
python -m unittest tools.mesh_studio.test_studio tools.mesh_studio.test_storyboards tools.mesh_studio.test_quality_analysis tools.mesh_studio.test_real_p1 -v
```

The output is a true-vector UV SVG, a repeatable JSON scientific audit and a
SHA-256 manifest. It is **not** a 3D shaded vector export, continuous Jacobian
certificate, accepted hybrid adaptive history, global non-manifold welded mesh,
all-quad result or anisotropic method output. The TRI and QUAD groups classify
**element types**, not two different physical source patches.


## S4: optional physical XYZ / source UV desktop viewer

The **headless** `scene_model.py` preserves original source IDs, separate TRI/QUAD
faces, per-corner UV and camera/visibility recipes pinned to the input OBJ SHA.
`scene_vtk.py` and `render3d_cli.py` provide native VTK 3D previews **as raster
PNGs**, with audit JSON. Do not label these screenshots vector figures.

```sh
python -m unittest tools.mesh_studio.test_desktop_stage -v
python -m tools.mesh_studio.render3d_cli \
  tools/mesh_studio/fixtures/real_p1/accepted.obj \
  --png build/mesh-studio/p1_real_xyz.png
```

The optional GUI source is available in `desktop_app.py` (PySide6 + PyVistaQt),
with 3D/UV linked face IDs, TRI/QUAD toggles, camera recipes and interactive
cell inspection. Install only after resolving and validating exact Qt/VTK
version constraints on the target host:

```sh
python -m pip install -r tools/mesh_studio/requirements-desktop.in
python -m tools.mesh_studio.desktop_app --obj tools/mesh_studio/fixtures/real_p1/accepted.obj
```

**Qualification limit:** Native VTK EGL rendered successfully and all S4 headless
tests passed. A PySide6/PyVista/pyvistaqt desktop run was NOT executable in this
environment, so interactive cell picking, Qt ABI and close/reopen memory behavior
are UNQUALIFIED until an actual GUI smoke run. See
`docs/mesh-studio/IMPLEMENTATION_S4_20261114.md`.

## S4b: bounded Qt GUI qualification gate (not passed without Qt)

S4a remains verified by VTK headless rendering and scene-model regression.
The **actual** PySide6/PyVista/PyVistaQt window is a separate, pending gate.
The automated S4b smoke below opens two Qt-backed VTK panes, toggles the source
face layers, selects an indexed face via Qt and the VTK cell-data callback,
preserves camera recipes, renders a screenshot, then closes the widgets.
It does **not** claim to calibrate a physical mouse click, or provide an
independent repeat-open/close Windows GPU endurance qualification.

```bash
python -m pip install -r tools/mesh_studio/requirements-desktop.in
# Linux with Xvfb/GLX availability:
xvfb-run -a python -m tools.mesh_studio.desktop_app \
  --obj tools/mesh_studio/fixtures/real_p1/accepted.obj \
  --smoke-output build/mesh-studio/qt-smoke.json
```

On Windows, invoke the same Python command in a regular desktop session without
`xvfb-run`. A PASS receipt is emitted **only after** real PySide6 and both VTK
widgets execute; missing dependencies return exit code 2, with no false PASS.
The programmatic pick callback is distinct from real physical mouse selection,
which still requires a separate interactive acceptance test.

## S5 pilot: publication-grade vector figure and experiment registry

Install the optional publication dependencies independently of the GUI:

```bash
python -m pip install -r tools/mesh_studio/requirements-publishing.in
python -m tools.mesh_studio.publish_cli --output-dir build/mesh-studio/paper-figure
python -m unittest tools.mesh_studio.test_publication -v
```

The source-bound command uses the **real PR #217 controlled P1** OBJ and its
verified generator receipt. It produces a journal-width (178 x 108 mm) PDF,
SVG, LaTeX `figure*` insertion snippet, CSV of 36 source TRI Studio-computed
mean-ratio scores, a replayable JSON recipe, a PDF/SVG structural audit and an
explicit six-cell topology x sizing comparison registry.

No qualified tensor-driven or all-QUAD results exist yet. The real fixed16
P1 source is deliberately **outside** the isotropic/anisotropic factorial
comparison, rather than being misrepresented as isotropic adaptation.
Nonplanar original Bézier QUAD cells are not given a planar scaled-Jacobian
score; the source's continuous surface validity is still not certified.

The SVG/PDF output is vector-only, not a three-dimensional shaded render.
Verification checks PDF image XObjects and inline images, SVG `<image>`/script
and remote asset references, actual physical paper size and embedded PDF fonts.
The PDF and SVG remain byte-for-byte reproducible in the qualified local
Python/Matplotlib environment, but release builds must pin their own tested
dependency versions. The LaTeX smoke uses `pdflatex` when available.
