# Mesh Studio V3 — scientific figure narratives for TRI, QUAD/TRI, all-QUAD and anisotropy

**Status 2026-11-14:** design only. The dedicated viewer branch `feature/mesh-studio-fixture-first-20261114` is separate from active QUAD code. `quad-templates` at source check `3beec583fd4b95717d62716d819dd4cd81b02239` records controlled P1 integrated; **all-QUAD and a true metric-tensor-driven adaptive generator are not currently qualified**. Do not infer their implementation from source research diagrams or a mock. No production source or UI is changed by this document.

## 1. Scientific experimental factors, not three mutually exclusive modes

Use a factorial design: **mesh topology** `TRI`, `QUAD_TRI`, `ALL_QUAD` crossed with **sizing strategy** `ISOTROPIC`, `ANISOTROPIC`. All six logical combinations may be represented by explicitly synthetic fixtures, but only real measured source executions can be labeled `source_measured` or accepted scientific results.

| Mesh topology | Isotropic | Anisotropic | Source status |
| --- | --- | --- | --- |
| TRI baseline | Historical published comparison | Synthetic control; future comparable real algorithm | Original TRI baseline exists |
| QUAD + AFT TRI | Real controlled P1 curved patch; no mixed adaptive epochs | Synthetic tensor-field demo; future implementation | P1 fixed sampling, not P2 adaptation |
| All-QUAD | Synthetic template and parity study | Synthetic tensor + template study | No qualified executable all-QUAD in the application |

**Do not mislabel:** A physical isotropic size target transformed into a distorted UV parameterization is not proof of a tensor anisotropic adaptation algorithm. Conversely, a mesh elongated in XYZ is not necessarily anisotropic in its prescribed metric; measure edge lengths against the actual source metric field.

## 2. New figure-stories by contribution

### Hybrid QUAD/TRI construction (method figure)

Capture real or explicitly staged states: source patch and boundary identity -> shared curve sampling -> quadtree leaves and 2:1 transitions -> selected QUAD templates -> physical owned QUAD interior -> active exterior AFT front -> individually inserted TRI -> complete typed hybrid patch -> UV-to-XYZ Bezier mapping -> per-element quality / recorded acceptance or rollback. Highlight the current operation with foreground colors and ghost the already completed elements. Label all synthetic stages as simulated; reconstructing intermediate states from a final mesh is a **posthoc visualization**, not an observed generator event.

### All-quad method figure

Show fixed boundary sampling, boundary edge parity and corner counts -> domain subdivision and singularity/valence planning -> template transition rules -> quad creation and possible rejection -> UV/XYZ validity and final all-quad element inventory. For any conforming quadrangulation of a topological disk with prescribed polygonal boundary, `4 F = 2 E_internal + E_boundary`; hence the boundary edge count must be **even**. This is a necessary condition, not a sufficient general-purpose algorithm. Do not resample a source shared curve to fix parity unless all incident patches accept the same canonical discretization. Separate extraordinary *mesh vertices* from *non-manifold original source curve valence*.

### Anisotropy / metric-driven method figure

Capture physical/UV coordinate frames, curvature/Hessian/sensor from true source (if available), prescribed or measured SPD metric tensor and provenance, metric ellipse at samples, eigenvalues/eigenvectors/principal scales, magnitude/ratio truncation and gradation, metric edge-length error, directional alignment of TRI/QUAD, actual refinement event and geometry validity. A synthetic tensor can illustrate the design without claiming it drove the current APMesh generator.

For a 2D tangent-domain symmetric-positive-definite metric `M`, report `ell_M(e) = sqrt(e^T M e)`. Illustrative constant `M=diag(16,1)` yields unit metric length for `e=(0.25,0)` and `(0,1)`; rotation tests require covariance. For physical 3D metric restricted to an immersed patch with full-rank differential `J`, source pullback is `M_uv=J^T M_xyz J`. Explicitly label the dimension/basis and metric units, and never invert a singular Jacobian or presume independent interpatch tensor compatibility.

### Fair method comparison

Always lock model geometric input, patch/curve interpretation, physical camera, crop, background/line width, color range, quality definition, units, metric version, software commit, random seed and hardware where timing is compared. Analyze both equal target geometric error and equal computational budget/element count as separate experiment views; show time/memory/element inventories. If an all-quad fixed boundary fails parity, present it as **infeasible under fixed boundary discretization**, not a generic failure of quadrangulation. Never hide rejected/non-monotone refinement epochs or use historical published TRI results as current QUAD experimental evidence.

## 3. Scientific core data model

`MeshDocument` stores immutable typed TRI/QUAD faces, local point identities and source curve ID; `MeshRun` captures input SHA, algorithm and metric mode with source revision and execution; `MetricField` carries SPD 2x2/3x3 values, basis, dimensions, units, source status and evaluation domains; `TechniqueEvent` distinguishes real observed event vs synthetic event vs posthoc inferred state; `SceneRecipe` contains camera, visibility, layer style, subfigure letters, annotations and sizes in millimeters; `ExperimentSet` links run inputs, acceptance/rejection, metrics and times. Do not store quality values computed by the viewer as if they were emitted by the original generator.

Use `SCENARIO_CATALOG_V3.json` as a **design catalog**, never as real test results. New fixtures proposed in the catalog are not yet generated or validated. Preserve the previous S0 16-case/10-valid/6-invalid corpus unchanged; add new scenario fixtures independently with a versioned manifest and deterministic hashes. Synthetic all-quad and metric fields must carry an unavoidable watermark/metadata tag.

## 4. Additional numerical and topology regression oracles

| Mechanism | Essential synthetic cases | Independent acceptance rule |
| --- | --- | --- |
| All-quad | 2x2 valid grid, even boundary transitions, odd fixed boundary | Zero TRI, every QUAD has four distinct nodes, closed incidence, positive UV local winding, even boundary parity |
| UV vs XYZ | UV-valid physically folded quad, curved Bezier analytic source | Reject physical invalidity and mark unverified continuous global Jacobian if only discrete sampling tested |
| Anisotropic SPD | Diagonal, rotated, varying, indefinite and singular metrics | Positive eigenvalues, symmetry, rotate-covariant metric lengths, reject non-SPD; flag unbounded metric ratios |
| Field adaptation | Scalar physical isotropic vs distorted UV, prescribed anisotropic field | Never call isotropic pullback algorithmic anisotropy; compare metric edges with prescribed source metric only |
| Shared curve | Valence 2, 3, 4, 28 and opposed tensor demands | Canonical sample equality and patch-local owner IDs; no implicit welding or tensor arbitration |
| Storyboard | Original generator event, deliberately synthetic event, posthoc geometry inference | Provenance flag in exported figure+manifest; cannot visually suggest unobserved runtime steps |
| Experiment | Two actual runs plus rejected candidates; mixed element inventories | Reject missing units, metric definition/version or source hash; show negative/rejected results explicitly |
| Publication | 2D SVG/PGF, hybrid 3D PDF, figure at single/two-column width | True-vector output inspected for embedded raster; hybrid marked; same scene recipe replay and LaTeX smoke |

## 5. Updated implementation order (parallel to source QUAD work)

**S0 (existing plan):** versioned base synthetic fixture generator/checker, strict typed input model, manifest; no renderer dependency.

**S1 (first implementation):** headless OBJ adapters and one camera-locked true-vector 2D story with TRI vs hybrid and explicit simulated stage labels; record exact model IDs and a replayable recipe. Neither QT/VTK installation nor a GUI is a prerequisite.

**S1b (NEW and early):** first **six-panel technique storyboard** including boundary sampling, quadtree, QUAD region, remaining AFT front, TRI completion, UV/XYZ lift. Accept versioned scripted snapshots or explicit simulation; preserve distinction. Add two-panel even/odd all-quad parity schematic and two-panel SPD metric ellipse / oriented elements. All illustrations are synthetic until actual source event capture is integrated.

**S2:** add separate TRI quality, QUAD UV/XYZ, 2x2 SPD metric-domain quality and source curve topology oracles; cross-check formulas against independent references.

**S3:** introduce optional PySide6 + VTK/PyVista 3D with synchronized UV/XYZ views, selective stage replay and GPU offscreen audits. Headless rendering and analysis must remain independent.

**S4:** multi-mesh factorial comparisons across 3 topology x 2 sizing cells; let missing implementations show explicit `not_available`; generate quality histograms, cumulative distributions, metric-alignment, error vs resource Pareto and accepted/rejected epoch plots.

**S5:** reproducible journal-ready multi-panel print figures SVG/PDF/PGF and companion manifest/LaTeX snippets with trustworthy font/vector audits, source hashes and experiment references.

**S6:** release offline Windows/Linux with pinned license audit, fuzzed bounded input, repeated GUI open/close tests and memory/cell-count profiles.

Optional generator instrumentation: later a **separate reviewed PR against the appropriate QUAD experimental branch** may add opt-in read-only event serialization. Do not modify source production directly from this viewer branch; first ensure event schema and CLI-only fixture storyboard work.

## 6. Evidence sources and advisor review questions

- Gmsh manual, anisotropic background mesh tutorial t17 (tensor field, BAMG): https://gmsh.info/doc/texinfo/#t17
- Knupp, *Algebraic Mesh Quality Metrics*, SIAM J Sci Comput (2000): https://doi.org/10.1137/S1064827500371499
- Cubit quadrilateral measures including warpage, scaled Jacobian: https://www.sandia.gov/files/cubit/15.8/help_manual/WebHelp/mesh_generation/mesh_quality_assessment/quadrilateral_metrics.htm
- All-quad parity and singularity constraints in *A robust combinatorial approach to reduce singularities in quadrilateral meshes*: https://www.sciencedirect.com/science/article/pii/S0010448516300793
- *Boundary constrained quadrilateral mesh generation based on domain decomposition and templates* (2024): https://www.sciencedirect.com/science/article/pii/S004579492400004X
- *Anisotropic metric-based mesh adaptation for ice flow modelling* (2025): https://gmd.copernicus.org/articles/18/4023/2025/
- PyVista `save_graphic` raster behavior: https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.save_graphic
- Primary historical comparison: Sombra et al., *Computers & Graphics* 139 (2026), 104707, https://doi.org/10.1016/j.cag.2026.104707

Ask scientific advisors before claiming: which literal historical Bento templates are required, what all-quad parity policy may alter source boundary samples, which physical metric field and cross-patch reconciliation rule is approved, and which metrics truly measure anisotropic alignment rather than XY appearance? Keep open until accepted explicitly.

## 7. Codex handoff

Continue inside the separate `feature/mesh-studio-fixture-first-20261114` worktree. Read `AGENTS.md`, `BRANCH_CHARTER_20261114.md`, `REGRESSION_AUDIT_20261114.md`, this document and the versioned scenario JSON. Preserve the existing S0 fixtures and verify that proposed new V3 cases are **not implemented yet**. Implement S0→S1→S1b in small coherent commits: typed import, six-panel narrative mock, even/odd all-quad topology, SPD metric ellipse and numeric oracles. Never present synthetic results as actual source evidence, never modify `src/`, `include/`, `quad-templates` or `main`. Record real commands and regressions before claiming figure validity; no auto-merge.
