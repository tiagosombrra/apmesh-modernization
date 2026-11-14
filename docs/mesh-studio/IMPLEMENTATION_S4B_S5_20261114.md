# Mesh Studio S4b gate + S5 publication pilot — scoped delivery

Date: 2026-11-14. Parent Studio branch: `feature/mesh-studio-fixture-first-20261114`.
This is an isolated viewer feature. No `main`, `quad-templates`, TRI or QUAD generator files are modified.

## S4b: GUI execution is NOT QUALIFIED in this container

- S4a's existing 74 Python tests and genuine VTK offscreen raster rendering pass.
- PySide6, PyVista and PyVistaQt are unavailable locally, and the package index has no matching packages in this environment. `python -m tools.mesh_studio.desktop_app --smoke-output ...` exits **2** and does not create a fake PASS.
- `tools/mesh_studio/desktop_smoke.py` adds an actual-Qt gate on future Windows/Linux developer machines: both panes visible, source 78 cells, TRI-only/QUAD-only Qt toggles, original-ID selection via spinbox and VTK picking callback, camera recipe roundtrip, camera reset, screenshot and window close.
- **Open:** Native window launch and repeated close/reopen, real screen click picking, resource/driver stability, Qt/VTK ABI, and packaging in qualified Windows and Linux installations. Never label this S4b complete until those experiments run.

### Required external commands

```bash
python -m pip install -r tools/mesh_studio/requirements-desktop.in
# Linux desktop or xvfb-run with a functioning OpenGL/GLX stack
xvfb-run -a python -m tools.mesh_studio.desktop_app --smoke-output build/mesh-studio/qt-smoke.json
# Windows Powershell (in an interactive desktop)
python -m tools.mesh_studio.desktop_app --smoke-output build/mesh-studio/qt-smoke.json
```

A `PASS_PROGRAMMATIC_GUI_SMOKE` receipt alone does not prove physical mouse-pick behavior; supplement with on-screen interaction and at least five reopen/close cycles. Record drivers, Qt/PySide6/PyVista/VTK versions, OS, screenshots and faults.

## S5: scientifically bounded first real-source editorial figure

Based exclusively on exact original PR #217 `accepted.obj` SHA-256 `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0` and the original `generator_report.json`. Original Bezier control-net, indexed topology, physical facet sample normals and source CI attribution are reverified via the independent S3 oracle before any output.

Actual input: 69 XYZ nodes, 42 mapped QUAD, 36 native AFT TRI, 16 outer boundary and 20 QUAD/TRI seam edges. Source `fixed16/vertex_mean` is a **bounded one-shot generator demonstration, not isotropic/aniso adaptation and not a multi-epoch history**.

Output `figure.pdf` and `figure.svg` measure 178 x 108 mm and contain a real, per-corner UV mesh, the 36 independent Studio TRI mean-ratio quality scores and original source inventory. The 42 curved nonplanar QUAD cells are **not assigned a planar scaled-Jacobian score**. Diagram, graph and labels are all vectors, not a PNG screenshot inside PDF.

The `comparison_matrix.json` has all six topology x sizing cells explicitly `NOT_AVAILABLE` and records the P1 controlled result *outside* this factorial matrix. Comparable runs require source model hash, matching metric equation/units, compatible evidence type and accepted status; rejected candidates remain visible, but never enter a winning score. This avoids fabricated cross-method comparisons.

The package contains: `figure.pdf`, `figure.svg`, `figure.recipe.json`, `triangle_quality.csv`, `comparison_matrix.json`, `source_oracle.json`, `publication.audit.json` and `include.tex`. A two-column LaTeX `figure*` example embeds the PDF at native double-column size.

## Scientific and technical regression contract

- No silently synthetic, resized or replaced source geometry.
- No combined average across incompatible TRI/QUAD metrics.
- P1 is not a demonstrated anisotropic, isotropic adaptive, all-quad or accepted multi-epoch algorithm.
- OBJ source bit flip or altered generator receipt fails **before** export.
- SVG image/script/remote references and PDF raster image objects are rejected.
- Paper dimensions, fonts and figure vector path inventory are machine-audited.
- Consecutive renders with the tested environment have identical SHA-256 across all delivered artifacts.
- LaTeX `pdflatex` smoke is an independently executed test when the executable is available.

### Status boundary

S4b GUI actual runtime: **BLOCKED / NOT RUN**.
S5 first scholarly real-source figure: **IMPLEMENTED AND LOCALLY VERIFIED**, subject to exact code and execution receipts. This is not a complete S5 multi-method study or release packaging.

Next: perform native Qt GUI qualification, then extend S5 to multi-model/multi-run comparisons only when genuine matching source experiments and metric definitions are available. Real all-QUAD and tensor anisotropy remain open scientific generator work.
