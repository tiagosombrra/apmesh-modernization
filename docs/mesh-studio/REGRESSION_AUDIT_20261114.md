# Mesh Studio — bounded audit and regression gates (initial state)

Date: 2026-11-14. The original generator and publication data are read-only references. This document is an audit of **existing inputs and proposed testing**, not a completed regression of a non-existent Mesh Studio GUI.

## Existing repository audit

- `src/input_output/write_obj_file.cpp`: original OBJ output includes model-specific nonstandard metadata rows and TRI element casts. S1 must explicitly support tested legacy dialect and standard mixed-face OBJ; not silently ignore all unknown lines.
- `tests/quad/tree_visual_export.cpp`: original C++ research Quadtree produces SVG/OBJ/CSV and an audit manifest. Boundary-excluded leaves are *not* filled AFT TRI. Reuse as a differential fixture.
- Research draft PR #214: patch-local disconnected physical QUAD/TRI Eistute/Book sources and original UV/Bezier samples; never infer global welding/accepted epochs.
- Production baseline PR #217 merged at this branch base; exact source postmerge CI was in progress during branch creation, not an inherited Mesh Studio qualification.
- Published Sombra et al., *Computers & Graphics* 139 (2026), figures 5–10: Book/Eistute/Decor Shelf evolution, quality, error and non-monotone stages. Present quantitative provenance and rejection markers.
- Existing prior HTML Canvas viewer is a UX prototype, not a scientific metrics or fully vector exporter.

## Independently tested synthetic input truth

Local standard-library generator + checker, performed before remote fixture import: **10 valid, 6 invalid (16 total) and 8 synthetic stage rows**; SHA-256 reproducibility on the manifest verified: `dccd142254b17401f2f0c5c5f31b67483fb82f8e2f83e2e68ef1ab248a638ccc`.

Positive sets: planar TRI; planar QUAD; TRI and QUAD grids; curved analytical parametric grid; QUAD/AFT-inspired annulus with 1 QUAD + 8 TRI; and distinct patch-local valence-2, -3, -4, -28 shared logical curve fans.

Expected negatives: physical square with concave UV; reverse-wound triangle; repeated QUAD corner; out-of-range face index; nonfinite raw vertex coordinate; mismatched shared-curve samples.

## Mandatory regression matrix (NOT YET EXECUTED)

| Area | Tests required before closure |
| --- | --- |
| Import/schema | OBJ standard/legacy/parser dialect; positive+negative fixtures; strict mixed face type and corner UV; missing metadata, NaN, index 0/negative/out-of-range, files too large and malformed |
| Geometry/topology | UV/XYZ differential signs, corner turns, physical area/orientation, quad/tri seam, patch owner and nonmanifold logical curve fan, repeated or orphaned faces |
| Numerical science | Analytic triangle/quad oracles, curved parametric differential normals, cross-tool checks against VTK/Gmsh where definitions really match; missing/NaN policy |
| Comparison | 8 synthetic epoch records with rejected/non-monotone errors; unit and score compatibility; stable fixed axes and legends, no fabricated measured values |
| Figure | No `<image>` inside purported true-vector SVG; PDF XObject/fonts/physical size audit; valid embedded LaTeX, no clipped labels; identify raster/hybrid 3D honestly |
| GUI/CI | PySide6/VTK compatible pinned Windows/Linux versions, offscreen snapshots, repeated open/close ownership, CLI headless without Qt; application/golden tests |
| Security/performance | Resource caps, no pickle/script injection/ZIP traversal, 1k/50k/500k cells measured with memory/log, Windows executable smoke and dependency SBOM |

Do not claim full native APMesh CTest, original Book/Eistute/Decor Shelf regeneration, PyVista rendering, PDF/LaTeX vector proof or Windows packaging at this stage. None has been executed for the new viewer branch. A source historical CI result only proves the source code under its own exact SHA.

## Review perspectives

- Geometry researcher: do not equate 2D UV convexity to physical curved-patch validity.
- Principal scientist: make synthetic versus actual results unmistakable and preserve raw sources and exact formula names.
- Software architect: domain/data/metrics independent from Qt and VTK; keep renderer pluggable.
- Python/Qt engineer: guard event loop, OpenGL backend, explicit ownership and dependency ABI.
- QA engineer: fail closed, preserve independent numerical oracles, adversarial corpus and source hashes.
- Editorial researcher: physically sized journals, grayscale/colorblind-safe palette, credible line/text sizes and audited vector content.
- Security/release engineer: strict input limits, offline operation, pinned dependencies and packaged Windows validation.

Next gate S0: install the fixture archive and record exact resulting commit, local output, controls and limitations. Do not merge this planning branch automatically.
