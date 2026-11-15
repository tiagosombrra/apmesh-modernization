# Scientific model strategy v2 — complex source geometry first

**Decision date:** 2026-11-15. **Classification:** scientific selection/protocol revision, not a modernization refactor, meshing algorithm change or approved paper dataset.

## Why the plan changed

The initial R2/R3 controls (three boxes, T/Cross, authored cubic sheets) verified STEP-contact screening, source-preserving topological construction, exact indexed BP shared curves, and the independent validators. They are necessary **test fixtures**, not persuasive end-to-end examples of a meshing method on representative challenging geometric objects. The preceding plan had unintentionally promoted *test development progress* in the user's visual narrative ahead of *scientific model relevance*. This is now corrected without deleting or invalidating those controls.

**Scientific selection must be driven by geometric variety, independently documented topology, identifiable origin, feature constraints, licensing, and actual generator acceptance — never visual complexity alone.** A complex CAD solid with at most two explicit face users per STEP edge must not be claimed as a non-manifold 3+-sheet model.

## Four distinct experimental populations

| Population | Admissible role | May support which paper claim? | Current state |
|---|---|---|---|
| HISTORICAL_NONMANIFOLD: Book / Eistute / Decor Shelf | frozen article baselines and regression, including existing source curve incidence | continuity with published TRI behavior only after accepted-state and exact baseline checks | existing article models; new qualification not run |
| RESEARCH_SYNTHETIC: authored three-box, four-sheet planar/curved, T/Cross controls | conversion and topology adversarial tests, development demonstrations | correctness of bounded operations, not generalization | R2/R3 controls measured; 63 research tests, no new TRI run |
| EXTERNAL_COMPLEX_GEOMETRY: HexMe/MAMBO and permitted CAD assets | challenge four-sided patch decomposition, curved geometry, trimming/seams and feature fidelity | geometry/representation/meshing robustness; **NOT non-manifold generalization by itself** | seven original STEP graphs directly screened, zero 3+-face explicit edges |
| EXTERNAL_CONFIRMED_MULTISHEET: independently sourced genuine 3+-sheet edge complexes | non-manifold generalization, with independent source/sheet/edge evidence | novel external non-manifold behavior only after all admission gates | **zero confirmed** — separate targeted discovery required |

The external positive population is a scientific **blocker**, not a quota to be filled by arbitrarily welding manifold solids. A physical multi-body contact may yield a reconstructed *derived* non-manifold control; keep its origin and intent separate from an original authored 3+-sheet B-Rep.

## Revised near-term order (subpackages, not replacement of R0–R7)

1. **S0 — Reproducible source/model shortlist.** Record exact IDs/metadata/rights and pin original CAD revisions; retain unsuccessful leads and prohibit duplicate MAMBO/HexMe sources. Output: `COMPLEX_CAD_SOURCE_SHORTLIST.csv` and this protocol.
2. **S1 — Real complex-model evidence.** Prioritize MAMBO **M5**, **S40**, **S27**, and **M3** for native import, shape type, unit scale, B-Rep validity, face/edge/shell ownership, boundary loops, geometric coincident-but-distinct edges, self-intersections, source feature curves, non-four-sided faces and trims. A first **reference-only STEP scan** is now measured, but the full native S1 gate is still open. M1, S8 and Quarter Torus are supplementary challenge/negative controls. Document machine-readable output and *source-specific* figures after opening the exact CAD bytes.
3. **S2 — Visual-source chain.** For each shortlisted source, produce three reviewable images from the actual pinned CAD: shaded CAD + source ID/scale, colored native faces/curves and incidence flags, and proposed patch graph/control nets. Never present tetrahedral volume dataset pictures or authored synthetic renders as APMesh surface-mesh outputs. All image slots remain PENDING until rendered against exact acquired source files; each image must carry source hash, view, renderer/kernel versions and caption.
4. **S3 — Complex geometry representation feasibility.** Per original face: planar/exact, polynomial bicubic/exact, analytic rational (cylinder/cone/torus: polynomial bicubic usually requires approximation), trimmed/non-four-sided (requires explicit partition), unsupported with cause. Freeze consistent units and a **geometry-approximation budget** before fitting. Canonical shared feature curves first, then surface fits; include failing/rejected cases. Do not silently collapse CAD topology or heal without an auditable decision.
5. **S4 — Independent external multi-sheet source search.** Locate a specifically authored CAD surface-complex example with an **actual** edge incident to at least three intended surface sheets. Check per-file rights, original topological graph, geometric curve, oriented sheets and source intent independently; no external positive is currently claimed.
6. **S5 — R4 bounded converter pilot.** Only after S1/S3 and admission, produce source -> feature graph -> four-sided decomposition -> common polynomial curve -> BP with versioned sidecar and geometry/identity oracles. Cases with holes, periodic topology, unsupported trims or unbounded curvature error are labeled UNSUPPORTED, not artificially repaired.
7. **S6 — R5 generator qualification, then R6 comparatives.** Freeze source BP/sidecar hashes, executable/configs, accepted versus rejected stages and full historical regression. Measure TRI, QUAD/TRI, all-quad and anisotropic outputs **only when each mode is available and qualified** and only for the same source surface complex, boundary constraints and declared tolerance. A volumetric HexMe tetrahedral reference is NOT a surface TRI/QUAD ground-truth quality comparator.
8. **S7 — R7 reproducibility and publication.** Freeze model roster, actual runs, failed conversions, negative results, license notices, source images, and separate geometric vs topological generalization conclusions. Holdout cases must be defined **before** analysis; M1/S8/Quarter Torus were already screened and cannot be represented as unseen holdouts.

## Bounded first cohort and reasons

**MAMBO M5 (`i05o_m5.step`)** — first geometric challenge: 41 ADVANCED_FACE; planes, 17 cylindrical surfaces, 10 conical surfaces and one toroidal surface. Supports a credible test of curved and trimmed patch approximation with feature constraints. **No explicit 3+-face edge observed.**

**MAMBO S40 (`i25o_s40.step`)** — second: 43 ADVANCED_FACE, including **two `B_SPLINE_SURFACE_WITH_KNOTS` entities** and 14 cylinders. Forces native surface degree/knot/trim inspection rather than treating every face as one 4x4 polynomial patch. **No explicit 3+-face edge observed.**

**MAMBO S27 (`i22o_s27.step`)** — third: 52 ADVANCED_FACE / 144 EDGE_CURVE, all with two distinct face users in the limited graph. High feature/adjacency density control; **not** external non-manifold positive.

**MAMBO M3 (`i03o_m3.step`)** — fourth: 60 ADVANCED_FACE, 169 EDGE_CURVE (ten single-face reference uses and 159 two-face uses); surface variety is mostly planar/cylindrical. The ten single-face uses need native shell/seam examination; do not classify invalid or nonmanifold from this count.

**Secondary S8 / M1** — 34/42 faces and 94/114 edges; S8 includes cylinders and M1 surfaces of revolution. **Quarter Torus** — 12 faces, 33 explicit edges, multiple shell-based model entities and 21 single-face uses; select as a representation/periodicity negative/adversarial rather than an industrial showcase.

**Attractive but blocked by rights:** GrabCAD Turbo, truck tire, Alcoa bracket (declared GrabCAD Terms); DLR-F6 (rights marked unknown). No redistribution, generated preview publication or benchmark incorporation until individual terms and permitted usages are reviewed.

## Admission decisions and review matrix

For each original input, label G1 rights/provenance, G2 intended native topology and source semantics, G3 four-sided bicubic feasibility, G4 geometry error, G5 experimental discrimination, G6 reproducibility, G7 actual accepted APMesh generation. Values: PASS / FAIL / BLOCKED / NOT_RUN with separate evidence pointers.

The minimum R3/R4 geometric research report contains CAD face support type, edge-loop count and orientation, periodic seam flags, trimmed boundary count, approximation status/budget in normalized and physical units, feature-curve compatibility with exact control ID identities, number of patches per original face, max sampled error plus convergence plot, failure numerator/denominator, and screenshots from the real model.

The minimum R5 output report contains requested stage, accepted/rejected state, boundary curve incidence and global node equivalence from the independent checker, mesh type and metric validity. Comparing mesh algorithms with different geometry approximations without explicitly reporting the difference is prohibited.

## Non-goals for this revision

No model download or raw CAD redistributions committed, no new fake/illustrative CAD render, no new native CAD acceptance claim from the static scanner, no `.bp` generated from the shortlisted complex CAD models, no new APMesh TRI/QUAD outputs, no PR merge, no validation of the original Thingi10K corrupt assets. The legacy R2/R3 synthetic controls remain available for regression; they are not discarded.
