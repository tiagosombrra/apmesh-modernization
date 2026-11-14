# Mesh Studio — fixture-first product charter

Date: 2026-11-14. Branch: `feature/mesh-studio-fixture-first-20261114`, created from verified `quad-templates` SHA `d39bbc447f88e179c3c4ee674bd9309f59c18eed` (research PR #217 integration). **No production QUAD/TRI source changes or scientific merge are authorized by this planning branch.**

## Decision

Develop an offline-first APMesh surface mesh analysis and journal-figure tool independently from the generator. Keep initial files under `tools/mesh_studio/` and `docs/mesh-studio/` on this dedicated branch. Preserve `main`, the QUAD source branch and active local Codex worktrees. Use a separate git worktree. Consider a standalone repository only after the first working figure pipeline.

## Architecture

1. Core domain model independent of rendering: typed TRI/QUAD cells, XYZ, corner UV, patch-local owners, source curve identities, accepted/rejected epochs, metrics and source hashes.
2. Versioned adapters: standard OBJ, exact legacy APMesh OBJ dialect, patch-grouped research OBJ, then meshio-backed VTU/MSH/XDMF; do not infer global sheet welding from identical coordinates.
3. Numerical layer with explicit metric version, units, geometry domain and independent analytic oracles. Do not merge TRI and QUAD quality distributions without a justified comparable definition.
4. Desktop preview with PySide6, pyvistaqt, VTK; headless plotting with NumPy and Matplotlib; separate true-vector 2D SVG/PDF backend, distinct from raster/hybrid VTK 3D export.
5. Publication engine: declarative reproducible recipes for camera, clipping, patch colors, heatmap scale, subfigure labels and journal physical size. Export SVG/PDF/PGF, PNG/TIFF and LaTeX insertion with PDF XObject/font audit.

## Seed corpus (synthetic, no actual paper results)

Prepare 16 deterministic standard-library-generated fixtures: valid single TRI/QUAD, TRI/QUAD grids, analytically curved Bezier-representable grid, one interior QUAD + 8 exterior AFT-like TRI, four separately owned logical shared-curve fans of valence 2/3/4/28; and six deliberately invalid cases: concave UV despite convex XYZ, reversed TRI, repeated vertex, foreign OBJ index, NaN coordinate, and fan-wide shared-curve sample mismatch. Also prepare eight explicitly simulated accepted/rejected epoch CSV rows with non-monotone error.

Fixture generator and independent source-contract validator were executed locally *outside this Git branch*: 16 cases = 10 expected positive + 6 expected negative; all 8 fabricated history rows verified. Manifest stable across regeneration, SHA-256 `dccd142254b17401f2f0c5c5f31b67483fb82f8e2f83e2e68ef1ab248a638ccc`. Fixture files are still to be imported into this branch by the isolated Codex worktree; this committed charter is NOT a claim that remote fixture code or viewer implementation has been delivered.

## Finite release gates

| Gate | Minimum deliverable |
| --- | --- |
| S0 — fixture preparation | Store local provided generator/cases/validator in this branch; require exact 10/6 diagnostics and deterministic regeneration |
| S1 — usable first figure | Separate standard/legacy OBJ adapters and domain model; render one real typed mock with a pure vector SVG/CLI plus exact recipe; reject malformed input |
| S2 — defensible metrics | Typed TRI/QUAD metric engine, analytic curved controls, UV/XYZ topology checks, independent numeric oracles |
| S3 — desktop visualization | PySide6/PyVista 3D, linked UV/XYZ camera controls, patch filtering, Windows/Linux viewport smoke tests |
| S4 — comparative science | Multi-method/epoch figures with accepted/rejected markers, provenance, aligned axes and explicit units |
| S5 — publication | Multi-panel PDF/SVG/PGF, verified vector/raster classification, fonts, LaTeX smoke test, journal preset |
| S6 — distributable | Offline executable, resource limits, package licenses, fuzzing and measured performance |

## External evidence behind critical choices

- `vtkMeshQuality` warns most quad estimators are intended for planar quads: https://vtk.org/doc/nightly/html/classvtkMeshQuality.html
- PyVista `save_graphic` defaults to rasterized 3D: https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.save_graphic
- Meshio supports cell/point metadata and time series: https://github.com/nschloe/meshio
- PGF can create LaTeX resource pressure for large vector files: https://matplotlib.org/stable/users/explain/text/pgf.html
- Publication comparison design: QuadriFlow https://web.stanford.edu/~jingweih/papers/quadriflow/ and Instant Meshes https://rgl.epfl.ch/publications/Jakob2015Instant

## Next safe Codex action

Open a separate worktree from this branch; read `AGENTS.md` and this charter. Import the provided synthetic fixture package into `tools/mesh_studio/fixtures/` without touching source-generator paths. Regenerate/check all cases, then build a headless `MeshDocument` + strict OBJ importer and one true-vector mock figure, before designing the extensive desktop interface. Report exact code changed and tests actually run; no blind merge to `quad-templates`.
