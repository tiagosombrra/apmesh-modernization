# APMesh Mesh Studio — Master Plan V4: scientific viewer, metrics, method stories and publications

**Date:** 2026-11-14. **Research repository:** tiagosombrra/apmesh-modernization. **Isolated Studio branch source head:** 1a3345fbb28244a677751f5e6531407ca0524568. **Source QUAD head at audit:** 3beec583fd4b95717d62716d819dd4cd81b02239. **Frozen production main:** f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94.

**Status:** architecturally audited implementation plan, not a working Studio application or certified viewer regression. New application code, GUI, vector publication and real imported P1 outputs remain OPEN. The existing synthetic archive was independently rerun twice outside this Git branch and has NOT been installed or committed to Studio.

## 1. Product decision and strict branch isolation

Deliver an offline-first, scientifically reproducible Mesh Studio with five independently useful capabilities: (1) Viewer for XYZ/UV geometry, (2) Analyzer for typed quality and topology, (3) Technique Storyboard showing partial method states, (4) Experiment Comparator with provenance, and (5) Publication Composer for paper/thesis figures and LaTeX.

The first working deliverable must be a strict importer and a reproducible true-vector 2D/UV figure, NOT a large Qt shell. Keep the initial new files within tools/mesh_studio and docs/mesh-studio. Use a separate Git worktree: never switch, clean, reset, rebase or overwrite the active QUAD Codex workspace. Do not touch src, include, original baseline, generator configs, main or canonical QUAD state. A standalone repository is a later decision, after a genuine figure MVP and stable interchange schema; the current branch is already isolated.

## 2. Exact-state audit and verified/unverified distinctions

| Finding | Severity | Required correction |
| --- | --- | --- |
| Studio branch has only documents and a V3 design catalog; no working app or new CI | P0 | Deliver S0/S1 source code and runnable tests before another planning-only iteration |
| V1 synthetic ZIP externally exists but is not in Git | P0 | Import unchanged and test generator plus validator, then commit to Studio |
| V3 lists 18 future scenarios, 11 figure recipes and 21 events, but NOT runnable test cases | P0 | Represent design vs generated vs actually measured as different states |
| Legacy original src/input_output/write_obj_file.cpp emits project-specific OBJ rows and raw node IDs | P1 | Explicit legacy dialect parser with diagnostics, never guess global OBJ numbering |
| Controlled P1 real source PR217 accepted 42 QUAD, 36 native AFT TRI, 69 physical nodes, 16 boundary intervals, v/vt and cell groups | P1 | Reuse as first real Studio integration input after synthetic import passes |
| Larger PR214 research detached patch meshes are NOT source-approved global welded meshes | P1 | Preserve patch-local node ownership and original curve logical incidence; no coordinate-based welding |
| No source runtime event tracing API | P1 | Mark initial stories as synthetic; later add opt-in read-only event export in a separately reviewed generator PR |
| VTK planar-quad metric caveats and PyVista 3D raster default | P1 | Independent equation registry and separately proven vector-only 2D renderer |
| All-QUAD and anisotropic generators are not scientifically qualified | P0 | Synthetic design/figures only until real exact-generator execution and scientific review |
| Windows Qt/VTK delivery, licensing and GPU portability unproven | P2 | Version/ABI/license inventory and real Windows/Linux packaging gates |

The existing V1 archive was regenerated and independently validated twice: fixture_audit=PASS valid=10 negative=6 total=16 experiment_rows=8 synthetic_only=true. Deterministic manifest SHA-256: dccd142254b17401f2f0c5c5f31b67483fb82f8e2f83e2e68ef1ab248a638ccc. This is a fixture **contract** test, not a Studio importer or figure test. No local full C++ generator CTest was executed by this Studio planning activity. Source P1 postmerge CI #43588588497 passed 4/4 and remains generator-only evidence.

## 3. Scientific study design: topology crossed with sizing policy

Create six logical experimental cells: TRI, QUAD+TRI, ALL-QUAD crossed with isotropic and anisotropic sizing. Mark a missing real technique as NOT_AVAILABLE rather than plotting fake zero quality. Do not call anisotropy a cell topology. A distorted UV parameterization or elongated physical elements are not evidence that a tensor metric drove an actual adaptive algorithm.

Comparison constraints: same exact model content SHA, boundary treatment, geometry source, accepted epoch definition, reference metric equation and version, units, camera and physical zoom, color scale and raw data provenance. Compare equal geometric error targets and equal work/element budgets as separate analyses. Declare hardware and repeated-measurement protocol for timing/memory. Preserve rejected and non-monotonic candidate stages. Keep historical published TRI datasets separate from newer QUAD generated outputs.

## 4. Selected software architecture and why

Choose Python, NumPy, meshio, Matplotlib, PyVista/VTK, PySide6 plus pyvistaqt, pytest, Ruff and static type checking, with release-specific reproducible dependency locks. Domain model, adapters, metric engine, topological checker, timeline, figure recipe and headless CLI MUST NOT import Qt, VTK or require a GPU. PyVista/VTK is an optional S4 desktop 3D backend, not the scientific truth source. Matplotlib or a controlled SVG path renderer supplies true-vector UV/2D scenes and plots. Use ParaView and Gmsh as independent reference tools rather than recreating all their existing visualization features.

Alternative assessment:
- ParaView/pvpython: strong programmable pipelines, state files and scientific field filters; less suitable as the custom source-curve and publication UX.
- Gmsh: a strong scientific mesh and metric-field comparison baseline, not an authority on explicit APMesh multi-incident curve identities.
- Polyscope: rapid interactive inspection, but does not replace stable journal figure recipes/LaTeX.
- Three.js/React: possible future browser frontend, but would add duplicated numerical/rendering contracts and offline GPU complexity in S0–S3.
- Blender: optional high-quality aesthetic renderer, not an independent numerical oracle or first-line scientific paper vector output.

Version-pinning is based on actual Windows/Linux integration testing, not latest-version assumption. Qt for Python's community licensing and packaging obligations must be reviewed for shipped executables; no font files are redistributed.

## 5. Canonical scientific domain contracts

Use versioned schemas and immutable records:

- MeshDocument: typed TRI/QUAD faces, original per-element/per-corner identity, XYZ, UV PER CORNER where seams occur, patch-local node owner, original source curve ID, topology_scope, units and missing-data provenance. Never silently triangulate a QUAD in the canonical document.
- PatchTopology: source patch IDs, logical shared curve incidence, side orientation, canonical source sample parameters, physical owners and independently recorded welding approval. Same XYZ is not identity.
- MetricField: symmetric SPD matrices (2x2 surface/UV, 3x3 physical), basis and metric frame, units, sampling points, eigenpairs, source provenance, algorithm source revision and measure versions.
- TechniqueEvent: event_id, run_id, sequence, typed stage/status, graph parent, changed cell IDs, snapshot and delta hashes, observed vs simulated vs posthoc-inferred provenance.
- ExperimentRun: input SHA, generator commit, configuration/seed/hardware, topology and sizing policy, epoch acceptance status, computational cost, quality/geometry error definitions.
- SceneRecipe: deterministic camera/projection, clipping, color scales, physical dimensions, font/style, layer visibility, panel layout and textual annotations.
- FigurePackage: output files, recipe, raw tabular data, source hashes, metric registry and editor/vector audit receipt.

No best-effort guessing of missing source control points, global patch sheets, Bezier Jacobians, or original curve topology from generic OBJ. Format conversions must return a loss report for fields that cannot be represented.

## 6. Import and external-file security

S1 accepts standard Wavefront OBJ records (v/vt/vn/f/g, independent vertex/texture indices and legal relative indexes), explicit legacy APMesh OBJ dialect and the newer real P1 grouped QUAD/TRI OBJ. Preserve original cell type and patch owner in the canonical document. Subsequent VTU, Gmsh MSH 4.1 and XDMF time-series adapters can use meshio, with sidecar metadata when required.

Reject or diagnose malformed faces, zero/out-of-range references, duplicate corners, inverted UV where required, missing texture coordinates, NaN/Inf, unsupported polygons, ambiguous owner semantics, physically coincident patch-local vertices, malformed group nesting, huge files, ZIP traversal, ZIP bombs and mismatched source hashes. Never execute pickle, embedded code, eval or scripts from a model/recipe. Add configurable resource quotas and precise source-line errors.

## 7. Numeric/scientific metrics with independent oracles

Triangle metrics: 3D facet area, min/max physical angle, edge ratios, orientation against known source surface normal, typed per-cell histograms and percentiles. One illustrative normalized planar triangle mean-ratio metric is q = 4 sqrt(3) A/(a^2+b^2+c^2). It is NOT automatically the paper's historical q; verify that exact formula before reporting a match.

Quad metrics: four signed UV corner turns, distinct corners, edge incidence, winding, area and triangulation policy, warpage, planar shape and reference Jacobian-based distortion. VTK explicitly warns that, apart from EDGE_RATIO, its quadrilateral quality estimators are intended for planar quadrilaterals; therefore apply metric-specific source assumptions and independent curved Bezier tests. A positive face normal dot at finitely many samples cannot prove global continuous surface Jacobian orientation or absence of self-intersections.

Anisotropic metrics: M symmetric SPD with eigenvalues > 0; for a constant 2D field ell_M(e) = sqrt(e^T M e). For varying field use declared numerical quadrature along edges. Separate physical xyz metric from its parametric pullback M_uv = J^T M_xyz J when full-rank source differential J exists. Require units, metric frame, anisotropy bound, eigenvector alignment, transformed metric length and metamorphic rotation covariance. Synthetic M=diag(16,1) gives metric unit length along (0.25,0) and (0,1); reject non-SPD and singular cases.

Topology: indexed edge incidence and opposite shared orientation by patch; Euler where chart assumptions apply, interior/boundary separation, fan-wide source curve sample compatibility, no implicit welding, disconnected component visibility. For conforming all-quad surfaces with each interior edge incident to two quads and each boundary edge to one, 4F=2E_interior+E_boundary, so total boundary edge count is necessarily even. This alone does not ensure existence of a valid full quadrangulation, cannot authorize source boundary resampling and is not generalized to unsupported non-manifold edge incidence. Distinguish a mesh vertex's extraordinary valence from source curve multi-patch incidence.

Report separate TRI/QUAD distributions; only combine score scales if a rigorously common metric has been proved. Report missing/invalid/unevaluated separately from zeros.

## 8. Technique Storyboard: research explanation as a first-class product

Provide actual observed runtime events only after a reviewed generator trace schema exists; initially label all mock sequences SIMULATED. Reconstructed stages inferred from final mesh are explicitly POSTHOC, never OBSERVED.

Hybrid QUAD/TRI story: original patch and curves -> canonical boundary samples -> graded quadtree -> selected templates -> emitted interior QUAD -> remaining AFT front -> native exterior TRI -> complete typed hybrid -> UV-to-XYZ physical surface -> oriented quality and accepted/rollback state.

All-quad story: fixed source boundary and edge parity -> constraints/patch subdivision -> singularity and valence placement -> 2:1 transition templates -> creation/rejection -> no-TRI final inventory -> UV/XYZ and quality certification. All-quad publication requires zero actual TRI in source emitted output, not merely rendering TRI edges as quads. Explicitly demonstrate an odd-boundary impossibility under the documented conditions.

Anisotropic story: actual or synthetic curvature/sensor -> prescribed tensor SPD and physical/UV frame -> eigenpairs/metric ellipses -> gradation/clipping -> directional refinement actions -> metric length and element alignment -> quality and accepted/rejected decisions. Never present a synthetic tensor as the source APMesh adaptive metric implementation.

Non-manifold story: side-by-side two-, three-, four- and 28-incident source curve fans; exploded and assembled views, canonical sample reuse, patch-local physical IDs, deliberate broken compatibility. No global sheet pairing is implied.

Compose storyboards with 2–12 panels, deterministic cameras/zoom, highlighted current operation, subdued previous states, journal letters, scale bars, insets and readable labels. Preserve scene recipe and figure data so a paper can regenerate exactly the same argument.

## 9. Figure catalog and editorial quality

Minimum article figures: (F01) matched TRI vs hybrid vs all-quad meshes, (F02) hybrid build pipeline, (F03) even/odd fixed-boundary all-quad parity, (F04) quad transition and extraordinary vertices, (F05) scalar isotropic size versus SPD ellipses, (F06) tensor-alignment diagnostic, (F07) physical UV distortion versus genuinely prescribed metric, (F08) fan-wide source compatibility, (F09) type-separated quality heatmaps/distributions, (F10) accepted/rejected epochs and error vs elements, (F11) fixed-budget/target-error method comparison. A figure cannot assert a nonexistent source algorithm result; when measured data are absent show NOT_AVAILABLE or a visibly synthetic explanatory panel.

Provide presets: publication single/double column, thesis, presentation, monochrome and print-accessible palette. Physical panel widths in millimeters, font and line weight as final print size, common camera/scale/colormap, zoom callouts, legend and epsilon/range definitions.

Two separate export promises:
1. True-vector 2D/UV/chart SVG/PDF/PGF proven by parsing SVG image/raster constructs and PDF image XObjects/forms, supported by render/LaTeX smoke checks.
2. High-quality 3D screenshots or hybrid PDF/SVG, truthfully marked HYBRID. PyVista save_graphic raster=True is its default for 3D props; a PDF extension alone proves nothing. Do not promise arbitrary 3D shadowed geometry as truly vector. Hidden-line 3D wireframe export needs separate visibility/clipping verification.

A FigurePackage should include figure.svg/pdf (and optional png/tiff), figure.recipe.json, figure.audit.json, table.csv, provenance.json and include.tex with no unlicensed fonts redistributed.

## 10. Fixture hierarchy and regression campaigns

L0 runnable external V1 archive: 16 independently rechecked synthetic cases (10 accept, six deliberate reject), eight fake epoch rows with rejected nonmonotonic candidate. Manifest SHA-256 dccd142254b17401f2f0c5c5f31b67483fb82f8e2f83e2e68ef1ab248a638ccc. STILL NOT IN GIT. Negative cases: concave UV/convex XYZ, reversed TRI winding, repeated QUAD vertex, foreign OBJ index, NaN, shared curve mismatch. Positives include planar TRI/QUAD, a Bezier-representable polynomial patch, one QUAD+8 TRI schematic, fan2/3/4/28 with disjoint physical ownership.

L1 proposed V3 design (18 scenarios), NOT YET RUNNABLE: isotropic TRI/hybrid/all-quad, all-quad fixed boundary even/odd, positive and negative SPD, rotated and varying metrics, UV-positive XYZ-folded quad, source fan tensor conflict and simulated acceptance/rejection. Publish separate deterministic fixture generator, truth registry and exact fixture checksums; never overwrite original L0 oracles to fit a new parser.

L2 real source P1 (after S1): run explicitly opt-in ap_mesh original curved ModelCurvaBezier; import exact OBJ with 42 real QUAD, 36 real AFT TRI, 69 nodes and 16 boundary edges; verify original v/vt/groups against independent source oracle, no mixed adaptive epochs. Source PR217 postmerge 4/4 CI is NOT a Studio qualification.

L3 published TRI sources: Book, Eistute, Decor Shelf paper/reproducible data, with provenance distinction between original published measurements, a new reproduced run and viewer-reprocessed metrics.

L4 future all-quad/anisotropic genuine source runs after approved algorithms and shared-curve policy, with no data fabrication and no implicit global node welding at high source incidence.

Mandatory adversarial families: hostile OBJ indexes/UV seams, nonfinite floats, degen faces, edge valence and winding, physically invalid but UV-positive faces, indefinite metric, odd boundary under fixed all-quad conditions, mismatched shared samples, corrupted event lineage, acceptance-status loss, raster incorrectly tagged as vector.

## 11. Delivery gates with executable outcomes, not documentation volume

| Stage | Required implementation | Closure evidence |
| --- | --- | --- |
| S0 Fixtures and schema | Import V1 archive into Studio branch; deterministic generator/validator plus typed MeshDocument schema | 16/16 expected statuses, 10 positive/6 negative, eight history rows, unchanged manifest digest, synthetic labeling, CI |
| S1 Headless importer and first figure | Explicit standard/legacy/P1 OBJ adapters, semantic roundtrip, pure SVG UV rendering CLI | All V1 cases, no silent face/UV/source-identity loss, one independently audited raster-free SVG, no Qt/VTK dependency |
| S1b Narrative starter | Six-panel hybrid story, all-quad boundary parity example, SPD tensor ellipse comparison | Three replayable true-vector synthetic stories with visible SIMULATED provenance and negative controls |
| S2 Independent geometry and metric core | TRI/QUAD physical and UV metrics, reference Bezier oracle, topology, SPD metric calculations, distributions | Separate definitions and independent analytic/mutation tests; rejects invalid, no unsupported mixed score |
| S3 Real P1 bridge | Import genuine controlled P1 runtime output plus a published TRI dataset | Reproduce P1 42/36/69/16, original model attribution and no adaptive history assertion; truthful real figure |
| S4 3D desktop | PySide6/PyVista preview, layer selection, picking, clip/zoom and linked UV/XYZ cameras | Windows/Linux startup, repeated open/close, saved/loaded camera, headless CI unaffected, driver fallback |
| S5 Comparator + editorial | 3x2 result matrix, acceptance histories, charts and print-ready SVG/PDF/PGF | NOT_AVAILABLE correctly displayed, consistent metric frame/scales, true-vector audits, embedded text fonts and compiling LaTeX snippet |
| S6 Real event capture | Opt-in read-only source generator instrumentation in a distinct reviewed QUAD PR, Studio event adapter | Each source event tied to exact run/source SHA and topology; unchanged default TRI scientific controls; real observed vs inferred distinction |
| S7 Release qualification | Windows offline distribution, Linux headless package, SBOM, license review, bounded parsers and benchmarks | Real smoke tests and reproducible hardware/size profiles for 1k, 50k, 500k cells; no unsupported performance claim |

Use short reviewable PRs in order: S0 fixtures/schema; S1 importer/vector CLI; S1b storyboards; S2 numeric engine; S3 P1 source integration; S4 Qt viewer; S5 journal pipeline; S6 event protocol; S7 release. Do not open all PRs at once or auto-merge. S6 source instrumentation is NOT authorized from this isolated Studio code branch; it must follow source generator research review and preservation rules.

## 12. CI and operational regression contract

Layered CI: fixture manifest/negative diagnostics -> parser/typed semantics/mutation cases -> topology/math/analytic oracle -> pure SVG/PDF/LaTeX source audits -> VTK offscreen -> Qt Windows/Linux smoke -> packaging/resource limits.

Tests must include rotated tensor covariance, non-monotonic rejected epochs, same camera/colormap comparison, no malicious recipe execution, no ZIP traversal/zip bombs, absent metric states, no lost per-corner UV data, no global welding and no raster-disguised SVG/PDF. Keep numeric oracles independent from renderer and source generator. A screenshot hash alone cannot certify geometry; use semantic mesh/facet/metric summaries as the primary invariant.

At every stage: review code; numerical and topology contracts; negative test evidence; scientific attribution; documentation and release/privacy/security inventory. Report exact commit, commands/toolchain, run result and tests not executed. Do not relax oracles or change scientific source conventions to make CI green. Root APMesh production baseline is unaffected by Studio work; source CI is re-run only when a generator cross-branch integration is actually proposed.

## 13. Multi-role audit and risk gates

Software architect: fail if Qt/VTK leaks into core. Geometry scientist: fail if UV validity is mislabeled complete curved XYZ validity or source nodes are welded. Anisotropic metric reviewer: fail if SPD/basis/unit/source field are missing. Research integrity reviewer: fail if mock, posthoc reconstruction and observed generator event are conflated. QA engineer: fail if parser drops geometry or negative regression passes erroneously. Editorial reviewer: fail if a PDF embeds raster but is labeled fully vector or font/crop/LaTeX output is unacceptable. Security engineer: fail if model import executes code or has unbounded memory/ZIP traversal. User reviewer: fail if a first-time user cannot load an included sample and understand validity/provenance.

Prioritize these risks: scope creep and GUI-first delivery; fake method measurements; topological identity loss; planar QUAD quality applied to curved surfaces; false vector export; Qt/VTK GPU/ABI issues; uncontrolled dependency licenses; incomplete legacy OBJ; branch divergence; endlessly growing fixtures unrelated to implemented work.

## 14. First concrete Codex work queue

(1) Inspect branch HEAD and staged/unstaged work. Add a separate worktree from feature/mesh-studio-fixture-first-20261114, preserving existing QUAD worktree. Read AGENTS.md, BRANCH_CHARTER, REGRESSION_AUDIT, V3 scenario catalog and this V4 plan.

(2) Install the existing externally supplied V1 ZIP under tools/mesh_studio/fixtures; independently regenerate and rerun 10/6 validator + eight fake events, check manifest digest and no source-generator paths changed. Commit only S0 with exact CI if available.

(3) Implement immutable typed MeshDocument and strict standard/legacy/P1 OBJ adapters with precise negative diagnostics; preserve per-corner v/vt and no hidden triangulation/welding.

(4) Make one reproducible pure-vector UV SVG figure from the synthetic hybrid, its structured scene recipe and audit. Build a six-panel simulated QUAD/AFT story, even/odd all-quad parity and SPD ellipse panel. These are S1/S1b testable deliverables, not a GUI.

(5) Only then import real source P1 generated OBJ and verify exact typed counts/provenance. Build numeric TRI/QUAD/SPD gates and headless plot figures before optional PySide6/VTK user interface.

No automatic merge, destructive reset, production TRI/QUAD edit, fake real data or new scientific statement is authorized. Deliver actual code, executed tests, failures and next functional blocker, not another documentation-only checkpoint.

## 15. Reference sources and scope

Primary internal science: Sombra, Cavalcante-Neto and Vidal, Computers & Graphics 139 (2026) 104707, https://doi.org/10.1016/j.cag.2026.104707, and the separate SIBGRAPI 1993 templates study (not evidence of current all-quad or anisotropic generation).

Benchmark visualization and field narratives: QuadriFlow https://web.stanford.edu/~jingweih/papers/quadriflow/; Instant Field-Aligned Meshes https://rgl.epfl.ch/publications/Jakob2015Instant; Knupp algebraic mesh metrics https://doi.org/10.1137/S1064827500371499; Bishop quadrilateral boundary parity https://www.math.stonybrook.edu/~bishop/papers/quadPSLG.pdf.

Tools and production cautions: Gmsh anisotropic t17 https://gmsh.info/doc/texinfo/#t17; VTK planar QUAD restrictions https://vtk.org/doc/nightly/html/classvtkMeshQuality.html; meshio https://github.com/nschloe/meshio; PyVista 3D export https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.save_graphic; Matplotlib PGF https://matplotlib.org/stable/gallery/userdemo/pgf_preamble_sgskip.html; ParaView state/figures https://docs.paraview.org/en/latest/UsersGuide/savingResults.html; PySide6 license https://doc.qt.io/qtforpython-6/commercial/index.html; Elsevier artwork https://www-prod.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/artwork-formats-checklist; pikepdf image audit https://pikepdf.readthedocs.io/en/latest/topics/images.html.

**Final boundary:** this plan and the synthetic mock contract are real completed planning/audit outputs. The Studio importer, SVG output, scientific quality engine, 3D viewer, PDF publisher, source event recorder and Windows executable are still unimplemented. A runtime qualification claim requires direct executable evidence at its own exact commit.
