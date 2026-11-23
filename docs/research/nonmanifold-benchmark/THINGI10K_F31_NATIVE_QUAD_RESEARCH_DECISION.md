# S40-F31 — Native QUAD research RFC, generated-surface generalization and real-source admission

**Date:** 2026-11-23. **Repository:** `tiagosombrra/apmesh-modernization`, branch `research/benchmark-corpus-reverse-patches`, Draft PR #225. **Classification:** methodological research decision and code-only computational experiment. **NO native APMesh QUAD algorithm has been implemented or executed.** There is no permission to distribute the original or derived Thingi10K #293137 geometry, and no matched reference-output benchmark has been scientifically admitted.

## 1. Scope and evidence inherited without requalification

- **F17–F20:** historical 23-member original-input corpus: 12 QuadWild examples and 11 Badia input examples; seven raw STL topology audits. It records neither per-asset redistribution clearance nor actual matched author QUAD member/verified output pairs. The frozen F20 manifest remains immutable.
- **F27:** original compiled APMesh C++ `ap_mesh` accepted actual **3,504 TRI** at stage 0 for source-derived 876-patch input #293137. Its exported OBJ has per-patch node-index seams, not a globally closed indexed topology.
- **F28:** an **external** source-curve-aware derivative correctly reconnects the TRI indexes, reconstructing a closed genus-zero surface, with source-sharp creases preserved. This is not native APMesh exporter output.
- **F29:** an **external** inverse of the known 3-four-corner-patches-per-source-triangle decomposition yielded 876 QUAD; native `WRITE_MODE=q` only emits quality reports. The original C++ physical and advancing-front element types remain triangular.
- **F30:** an **external, fixed-topology, strictly Pareto-nonregressing** repositioning of private patch centers improves average shape while keeping STL vertices and feature-edge midpoints. The original private output is not shared. The global minimum quality is capped by fixed source corners, and the full-precision source surface is piecewise planar rather than an authored freeform CAD surface.

The model-readiness delta in F31 is **not** an edit to F17/F20. It records one newly executed native TRI model (#293137) and one external derived QUAD study on that same model, and **zero native QUAD runs and zero accepted matched literature comparison pairs**. The pinned historical source CSV and actual F27/F30 numerical receipts are checked by Git blob before the new ledger is issued.

## 2. Frozen F30 algorithm on nine generated, topology-diverse closed surfaces

All surfaces below are **newly generated mathematical fixtures** in code, with no Thingi10K or CAD geometry. The Python F30 source Git blob `69e184d62032fa47ab03e5f71ba9979c3e4eea31` is verified before measurement; the search grid, metric definitions and per-quad Pareto non-regression constraints are **unchanged**. Faces are not smoothed, merged across source triangles, or altered in connectivity. Two generated toroidal inputs test genus 1; seven other generated inputs test genus 0. The generated three-QUAD-per-TRI surface is checked for paired/opposed edge incidences, connected vertex links, orientability, connected components and Euler/genus before shape comparisons.

| Generated case | Genus | Source TRI | Derived QUAD | Changed centers | Mean min-corner SJ before | After | QUAD min angle < 30° before → after |
|---|---:|---:|---:|---:|---:|---:|---:|
| Regular tetrahedron | 0 | 4 | 12 | 0 | 0.8660 | 0.8660 | 0 → 0 |
| Distorted tetrahedron | 0 | 4 | 12 | 0 | 0.8631 | 0.8631 | 0 → 0 |
| Regular octahedron | 0 | 8 | 24 | 0 | 0.8660 | 0.8660 | 0 → 0 |
| Stretched octahedron | 0 | 8 | 24 | 8 | 0.6330 | 0.7229 | 0 → 0 |
| Triangulated cube | 0 | 12 | 36 | 12 | 0.6714 | 0.7013 | 0 → 0 |
| Icosahedron | 0 | 20 | 60 | 0 | 0.8660 | 0.8660 | 0 → 0 |
| Capped prism | 0 | 32 | 96 | 16 | 0.5777 | 0.6725 | 32 → 16 |
| Torus | 1 | 192 | 576 | 192 | 0.5242 | 0.6723 | 144 → 144 |
| Corrugated torus | 1 | 192 | 576 | 192 | 0.5269 | 0.6721 | 132 → 132 |
| **Total** | mixed | **472** | **1,416** | **420** | — | — | — |

**Summary:** five of nine generated shapes show improvement in mean per-QUAD corner-minimum scaled Jacobian; four remain unchanged. **Unweighted mean of case means:** 0.710481 → 0.766907 (+7.94% relative). **QUAD-count-weighted mean:** 0.560544 → 0.688553 (+22.84% relative). The weighted average is dominated by the two large toroidal cases; it must **not** be presented as nine independent real-asset improvements. On both tori, counts of quads with minimum angle below 30° remain unchanged because many bad angles are inherited from fixed source corners. The positive results partly follow from the no-regression acceptance criterion by construction. The cases are intentionally nonblind and were not selected independently by a third party.

The output receipt contains no private original mesh/derived geometry. Negative controls reject open edges, nonmanifold edges, flipped orientation, pinched vertex links, disconnected components, a false genus, vertex aliases and **two topologically distinct closed surfaces coinciding in XYZ**. Exact original F30 semantics and model identity tagging prevent accidental admission of a hypothetical coordinate-welded surface.

**What the synthetic corpus DOES NOT establish:** new STL/real CAD generalization, results for independent source licenses, self-intersection-free arbitrary surfaces, successful native C++ QUAD execution, competitive QuadWild quality, 3D curved/high-order Jacobians, real-generation time/performance, or restoration of intentionally authored nonmanifold CAD junctions.

## 3. Formal metric contract and fairness policy

**Shape of a four-corner planar QUAD.** For each corner, use the signed normal-consistent cross product of its two incident edges, normalized by their lengths, and report the **minimum corner scaled Jacobian**; also record minimum and maximum internal corner angles. Do not substitute native TRI `2r/R`. Where high-order curved QUAD elements are proposed later, add Jacobian samples at center/Gauss points and a separate warpage/planarity metric; the planar corner score alone is not a high-order quality certificate. Sources: [Sandia Cubit quadrilateral metrics](https://cubit.sandia.gov/files/cubit/16.02/help_manual/WebHelp/mesh_generation/mesh_quality_assessment/quadrilateral_metrics.htm); [Knupp, Algebraic Mesh Quality Metrics](https://www.sciencedirect.com/science/article/pii/S0168874X02000707).

**Geometry/topology hard gates:** exact per-asset provenance and distribution rights; closed/orientable vertex links except where the research intentionally targets verified nonmanifold CAD; no duplicate/degenerate/inverted cells; explicit corner/curve IDs across seams; original crease graph preserved within a declared tolerance; bounded Hausdorff-type distance on independently sampled source geometry; source feature angles, connectivity/Euler/genus, volume/area; independently checked self-intersections as a **separate missing** gate. No global XYZ weld without a true source-topology identity mapping.

**Comparable reference gate:** pair identical **original source geometry**, explicit preprocessing, comparable target density/edge counts, unit scaling, allowed feature constraints, convexity/warpage rules and matched meanings for scaled Jacobian/angle deviation/edge-length deviation/irregular-vertex ratio. Report per-model distributions, rejection/timeout counts, confidence intervals or paired repeats, both failed and successful runs, source and generated artifact hashes. Comparisons to methods taking an STL directly must be labeled non-equivalent when APMesh uses an externally constructed 876-patch piecewise-planar Bézier domain. QuadWild's original work uses a feature-aligned cross-field, T-junction handling and an internal pure-QUAD tessellation rather than an equivalent three-sector patch inverse: [Pietroni et al. 2021](https://doi.org/10.1145/3450626.3459941), [official code/method](https://github.com/nicopietroni/quadwild).

**Scientific study design:** preregister shape-quality primary metric and threshold tails, use macro per-model aggregation and size-weighted aggregation separately, compare locked parameter settings, include topological genus and anisotropic/small-feature strata and negative cases. Do not exclude failed source conversion, omitted controls, licensing blockers or runtime failures from denominators. License of an open-source code repository does **not** establish distribution rights for every source or benchmark derivative; Qt/Gurobi/GPL dependencies in external baselines must be reviewed before redistribution/integration.

## 4. Options for a native QUAD capability (proposal, NOT approval)

| Option | Scope | Engineering risk | Scientific contribution / limitation |
|---|---|---|---|
| **A — Typed QUAD container/exporter first** | Experimental `QuadrilateralAdaptive`, four-corner incidence, safe ownership, isolated OBJ writer, separate quality metrics, feature constraints; no mesher change | Low–medium | Converts an audited external candidate into a verifiable typed native result, but **not** an independently generated QUAD; must carry its provenance |
| **B — Patch-local native QUAD generation** | Dedicated opt-in research module for Bézier patch UV: compatible boundary discretization, pure-QUAD cells, Jacobian checks, shared-curve orientation, rollback on failure | Medium–high | First credible native APMesh QUAD generator on suitable four-sided domains; must reject incompatible or unproven junctions |
| **C — Global feature-aligned quadrangulation** | Cross-field/trace/patch-layout or quad-dominant algorithm with singularities, geometric constraints and nonmanifold branch handling | High / distinct research track | Potentially comparable to modern remeshers only with matched sources, full validation and an independently measurable claim |

**Recommended sequence:** do not implement C prematurely. Seek advisors' decision whether native QUAD is a core research objective or an ancillary experimental analysis. If approved, stage **A** as an independent, tested branch or module without changing TRI output; then specify and validate B on original authored four-sided Bézier sources before any integration. Require a decision on whether the thesis prioritizes *shared/nonmanifold Bézier curves and TRI/QUAD coupling* or *general remeshing from triangulated surfaces*; these are different research questions.

### Suggested technical interface (not implemented)

```cpp
// Illustrative research proposal only; no new production API has been committed.
struct ResearchQuadCell {
    std::array<ULInt, 4> node_ids;
    unsigned int patch_index;
    std::array<unsigned int, 4> source_curve_incidence_ids;
};

struct ResearchQuadAdmission {
    bool oriented_and_noninverted;
    bool shared_curve_samples_match;
    bool respects_feature_graph;
    bool passes_jacobian_sampling;
};
```

An implementation would need memory/observer ownership contracts mirroring `MeshAdaptive`, immutable per-patch UV orientation, explicit distinction between curved-map Jacobian and physical XY(Z) mesh quality, timeouts/rollback and a representation for nonmanifold CAD sheets that does not assume exactly two incidences per curve.

## 5. Advisor decision checklist and next research gates

1. **Scope question:** Is the paper/thesis contribution primarily APMesh generation on authored Bézier sheets with shared/nonmanifold curves, or STL remeshing / QUAD quality optimization? Avoid conflating these domains.
2. **Native acceptance:** Approve option A, B or neither; decide if an external mesh can be imported into native containers without falsely labelling its geometry generator as native.
3. **Original CAD models:** Select an authored 4-sided Bézier control model with verified sharing/orientation (or request one), distinct from the piecewise-planar STL conversion, and establish its explicit source rights.
4. **Third-party reference:** Request/locate an exact author-output QUAD member for pinned #58012 and another candidate; verify output member hash, legal reuse and source topology before citing per-model comparisons. Preserve #61394 as a negative unless its nonmanifold semantics are independently established.
5. **Evaluation:** Freeze signed scaled-Jacobian sample policy, planarity/warpage, feature and source-distance budgets, target density and stop criteria; perform paired 3+ repeated runs and report failures.
6. **No production changes until independent sign-off.** PR #225 remains Draft and the frozen M3/M5/S40 tests remain unaffected.

## 6. Files, independently checked statuses, and non-admissions

- `probes/thingi10k_f31_synthetic_generalization.py`: generated closed genus-zero/genus-one surfaces, strict topological checks, frozen F30 shape optimization, public aggregate receipt only.
- `probes/test_thingi10k_f31_synthetic_generalization.py`: **55** shape, edge-link/genus, adversarial topology, scale/rotation, pinning and anti-false-promotion controls.
- `probes/thingi10k_f31_real_model_readiness.py`: hash-lock F17 CSV, F27/F30 receipts and emit a **new versioned** 23-model readiness status, without modifying F17–F20.
- `probes/test_thingi10k_f31_real_model_readiness.py`: **31** controls for historical snapshot preservation, false license/reference/native claim rejection and honest one-model advancement.
- `evidence/thingi10k/thingi10k_f31_generated_synthetic_generalization_receipt.json`: code-only generated data, 9/472/1,416 denominator.
- `evidence/thingi10k/thingi10k_f31_real_model_readiness_delta_receipt.json`: metadata-only real cohort, 23 cases; no mesh bytes or publication admission.
- `.github/workflows/research-f31-native-quad-proposal-gates.yml`: verifies full F27–F31 hermetic tests, pinned source and output numeric consistency, frozen 23-model cohort, and exclusion of original/derived geometry.

**Stop here unless approved:** no new C++ QUAD generator, no changes to `main`, no model assets in Git, and no benchmark admission. The next operation should be the advisor decision and independent authorization/provenance collection, not automatic promotion of the single #293137 study.
