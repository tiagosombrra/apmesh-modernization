# Thingi10K literature-backed QUAD benchmark — proposed research cohort

**Date:** 2026-11-20. **Decision:** retain all previously studied APMesh models; add a **non-replacing, independently classified** Thingi10K literature/QUAD comparison track. **Status:** LITERATURE_IDS_VERIFIED, **NOT ADMITTED FOR APMESH**, **NO NEW MESH OUTPUT**.

## Why this expands the scientific question

The 2026-11-14 R1 exploratory inventory contained 40 individual leads (29 HexMe, six Fusion Energy recipes, five explicitly broken Thingi10K file IDs). Those five Thingi10K entries were **negative parser cases**; they were not a scientifically representative Thingi10K geometric or quad benchmark. Later prioritizing the four MAMBO industrial originals (M5, S40, S27, M3) was useful for B-Rep/feature lineage but left prior published triangle-to-quad datasets unrepresented.

**New three-cohort structure (do not merge different geometries into one performance statistic):**
1. **Original CAD/Bézier scientific track:** M5/S40/S27/M3 plus original supplementary CADs; report partial Bézier conversion, source-curve identity and original STEP-trim checks. Remains manifold-only for these originals.
2. **Historical non-manifold APMesh regressions:** Book/Eistute/Decor Shelf and separately documented synthetic control cases; do not claim new execution unless rerun and accepted.
3. **Thingi10K triangular-input remeshing track:** independently sourced STL/triangular surface meshes; literature-linked quad reference(s) and a clearly separate conversion-to-APMesh feasibility gate. Failure to construct an admissible bicubic BP **counts as a negative outcome**, never silently removed.

The F13 Tsh249 true OCCT **post-sewing** triple-edge is another *derived repair benchmark*, not a naturally original-source 3+-incident `EDGE_CURVE`.

## Concrete literature roster: 23 distinct, presently candidate-only

The machine-readable [literature cohort manifest](THINGI10K_LITERATURE_COHORT.csv) freezes **23 distinct Thingi10K file IDs** in advance of running APMesh. Individual meshes, source hashes, per-object licenses, output pair matches, and actual APMesh feasibility remain **unverified**. No data/geometry or screenshots from restricted objects are embedded or redistributed.

### Cohort Q — 12 direct high-resolution QUAD reference models

Pietroni, Nuvoli, Alderighi, Cignoni, Tarini. *Reliable Feature-Line Driven Quad-Remeshing*, ACM TOG 40(4), article 155 (2021), DOI [10.1145/3450626.3459941](https://doi.org/10.1145/3450626.3459941). **Figure 29 + Table 1** identify twelve Thingi10K models with **published QUAD output statistics**:

| Thingi10K file ID | Published output quads #F | Published irregular vertices #I | Published AD (degrees) | Published ED (%) | Published mean scaled Jacobian |
|---:|---:|---:|---:|---:|---:|
| 44503 | 19130 | 829 | 0.28 | 13.11 | 0.95 |
| 128001 | 56162 | 3917 | 14.44 | 19.14 | 0.93 |
| 58012 | 113879 | 7977 | 15.49 | 12.28 | 0.93 |
| 61394 | 37730 | 1685 | 20.82 | 19.22 | 0.87 |
| 67792 | 16735 | 490 | 14.55 | 13.78 | 0.95 |
| 69975 | 22563 | 938 | 16.44 | 15.99 | 0.92 |
| 81877 | 35305 | 1835 | 19.62 | 15.99 | 0.92 |
| 94884 | 47466 | 3479 | 21.85 | 20.07 | 0.89 |
| 230923 | 45398 | 2108 | 22.66 | 30.57 | 0.87 |
| 364256 | 68905 | 6654 | 18.04 | 16.14 | 0.91 |
| 423069 | 60624 | 4123 | 23.79 | 41.29 | 0.85 |
| 498974 | 380068 | 32241 | 19.86 | 16.02 | 0.89 |

Original source [paper PDF and published table](https://air.unimi.it/retrieve/32ad6586-c047-4408-96ed-fae7dddcd187/3450626.3459941.pdf). **These numerical values are QUADWILD AUTHORS' FIGURE 29 RESULTS, never new APMesh measurements.** The published `#F` counts **output quad faces**, not input STL triangles. `#I` describes non-4-valence output vertices under the article's conventions; boundary treatment must match before comparing. `AD`, `ED` and `SJ` definitions/aggregation must be independently reproduced from original output before making numerical ranking claims.

The publication reports pure-quad conforming output preserving feature-lines through an internal possibly nonrectangular/T-junction layout. An **irregular patch layout** is not the same thing as an **irregular final quad cell**. Its model population is predominantly repaired/triangulated **surface input**, not an original industrial B-Rep with exact source edge identity.

**Publishable data location:** the author's [quadmesh.cloud quad-remeshing dataset](https://www.quadmesh.cloud/) and the Thingi10K dataset's [`Thingi10K_quadwild_npz.tar.gz` archive](https://huggingface.co/datasets/Thingi10K/Thingi10K/blob/main/Thingi10K_quadwild_npz.tar.gz) (**4.4 GB**). The latter advertises remote SHA-256 `79d213585fce31c61f661221266c967b26c5eb446e394d2022280f5a02399011` at inspection. **Neither the 4.4GB archive nor its individual twelve entries was downloaded or checked here.** Presence of an aggregate archive is not proof of an exact paired output for each listed ID; require a per-ID input-output byte-verified join.

For a small *engineering smoke test only*, prioritize morphologically different IDs `44503` (slender/elongated), `61394` (mechanical), `81877` (perforations), `94884` (lattice), `423069` (sculptural) and `498974` (heavy lattice). This is a **non-random convenience pilot**, and the **full frozen twelve-ID cohort** remains the reporting denominator; failures may not be excluded.

### Cohort G — 11 published diverse geometry controls, NOT published quad baselines

Badia, Martorell, Verdugo. *Geometrical discretisations for unfitted finite elements on explicit boundary representations*, *Journal of Computational Physics* (2022). [arXiv 2110.01378](https://arxiv.org/abs/2110.01378). **Figure 10 and Table 1** give the following IDs and original STL face counts:

- `252119` — 49950 STL triangles (paper-reported).
- `293137` — 292 STL triangles (paper-reported).
- `35269` — 40246 STL triangles (paper-reported).
- `37266` — 29472 STL triangles (paper-reported).
- `37881` — 3400 STL triangles (paper-reported).
- `441708` — 112402 STL triangles (paper-reported).
- `47076` — 1532 STL triangles (paper-reported).
- `550964` — 6156 STL triangles (paper-reported).
- `551021` — 348128 STL triangles (paper-reported).
- `65904` — 157726 STL triangles (paper-reported).
- `96457` — 1634 STL triangles (paper-reported).

These inputs were used for robust geometric discretisation/intersection on closed manifold STL surfaces. **They are NOT previously published APMesh or quad quality results**, so can evaluate conversion feasibility and complexity under our pipeline, but never populate a fake `published_quad_reference` column. The original article analyses about 4,732 successfully processed eligible models; this is evidence of a filtered manifold-oriented **geometric robustness** experiment, not non-manifold quad meshing.

### Other quadrangulation context — aggregate evidence, not exact matching samples

Fang, Bao, Tong, Desbrun, Huang. *Quadrangulation through Morse-Parameterization Hybridization* (SIGGRAPH 2018) [addendum on Thingi10K](https://www.geometry.caltech.edu/pubs/FBTDH18_addendum.pdf): tests on 7,929 connected input meshes, using frame-field target edge size 2% of bounding-box size, reporting scaled Jacobian and feature-line Hausdorff. **No exact per-ID model pair has been verified here**; do not equate these batch statistics with APMesh runs. QuadriFlow and Instant Meshes are alternative comparison families, but do not populate result values without matched reproducible outputs.

## Define which QUAD is being compared

| Comparison axis | QuadWild published case | APMesh research obligation |
|---|---|---|
| Input representation | Triangle surface input; sharp creases estimated from mesh | Four-sided polynomial bicubic patches (.bp) after a distinct STL→features→surface-partition→fit stage, or mark unsupported |
| Result representation | Conforming pure-quad surface mesh | Explicitly label actually supported TRI, mixed TRI/QUAD or QUAD variants on the same accepted input; **no assumption all-quad is implemented** |
| Feature constraints | Feature-line alignment in output, article-defined threshold | Explicit source-segment/feature correspondence and deviation to source STL plus index identity where available |
| Geometric fidelity | Output against exact same input triangle mesh | Sampled bidirectional Hausdorff/RMS and feature deviation normalized by input bounding-box diagonal; no CAD analytic ground truth can be inferred from STL |
| Quality | #quads, #irregular, AD, ED, SJ | Equal objective definitions, boundary conventions and comparable output size/target resolution; include normals, inverted elements and structural validity |
| Topology | Primarily manifold surface output | Independently count edge incidents and components; actual 3+-sheet topology is separately evaluated, not inferred from dataset labels |
| Cost | Authors' published timing on their own machines | Record pipeline stages separately (source cleanup, reverse patching, APMesh generation); fair timing requires local rerun of comparators |

The APMesh method and QuadWild solve **not automatically identical problems**. In particular, two different representations and extra conversion cost preclude a fair unqualified "better/worse" claim from the published Table 1 values alone.

## Admission and reproducibility gates

- **T0 — Per-asset rights:** resolve Thingiverse/Thingi10K object-specific `license`, author and attribution. Dataset code Apache-2.0 and QuadWild software GPL-3.0 **do not grant blanket redistribution rights to original models or derivative outputs**.
- **T1 — Immutable source identity:** retrieve only permitted source STL/OBJ, file ID, original author/metadata, SHA-256, format, units and triangulation count; preserve both original and any automatically cleaned/normalized mesh as distinct hashed artifacts.
- **T2 — Independent topology:** count connected components, boundary edges, vertex-link singularities, exact indexed 3+-face edges, duplicate/coincident triangles, self-intersections, degeneracy; clarify any conversion/repair.
- **T3 — Published QUAD pair:** extract 12 QuadWild output IDs from permissible archived dataset, independently compare their input IDs/hashes, quad face topology and recompute Table 1 definitions, noting article-version differences.
- **T4 — Reverse-Bezier feasibility:** feature segmentation, chart/patch layout, shared cubic interface control identity, 4-sidedness, valid Jacobian, bounded approximation error. Reject if not representable within predeclared tolerance rather than auto-welding faces or hiding failures.
- **T5 — Actual APMesh accepted meshing:** freeze executable/commit, inputs/parameters, run full accepted-state TRI / supported mixed / QUAD modes, independent output checker, max/RMS error, boundary incidence, #elements, quality histograms, performance.
- **T6 — Paired comparisons:** same original input, identical units, same feature definition where feasible, equalized output count/resolution, paired quality distributions and confidence intervals; **report 12/12 attempts and all blocked cases**, plus separately evaluate the 11 G controls.
- **T7 — 3+-sheet stress:** an original intentional 3+-incident source edge is a separate required positive class; a mere non-manifold Thingi10K label or self-intersection does not satisfy it.

## Next concrete deliverable and safeguards

The CSV is a **literature-grounded roster**, not an admission certificate. Next, query *per-ID* dataset metadata and rights, use the six-item smoke test, verify the exact QuadWild per-ID archives, determine which inputs the APMesh pipeline can represent, and add selected geometric previews with clear source attribution. Preserve historical Book/Eistute/Decor Shelf and all four selected original MAMBO models. Keep PR #225 DRAFT; no `main` merge or claim of executed comparative APMesh results without actual runs.

## Adjacent high-order Bézier literature (not a Thingi10K QUAD reference)

Martorell and Badia, *High order unfitted finite element discretizations for explicit boundary representations*, **Journal of Computational Physics** (2024), [DOI 10.1016/j.jcp.2024.113127](https://doi.org/10.1016/j.jcp.2024.113127), also uses CAD B-Rep and Bézier patch approximations for higher-order unfitted geometric integration. It is technically relevant to the **CAD→Bézier approximation and geometric-fidelity** discussion, but **is not an established pure-quad surface-mesh comparator** for these 23 Thingi10K IDs. Keep it as an adjacent method and do not collapse its high-order integration errors into quad shape-quality scores.

## S40-F15 — 2026-11-20: actual pinned catalog metadata join for 23 Thingi10K literature IDs

[Full 23-ID per-file metadata report](THINGI10K_CATALOG_METADATA_AUDIT_2026-11-20.md), [CSV](THINGI10K_CATALOG_METADATA_23.csv), and [JSON evidence](evidence/thingi10k/thingi10k_source_catalog_metadata_audit_2026-11-20.json) use a pinned 9,997-record public Thingi10K **metadata catalog**, not raw STL geometry. **23/23 named file IDs resolved**, including license declarations and topology flags; **11/11 Badia source triangle counts agree with published counts**. Only **4/12** QuadWild cases pass the *catalog-only* conservative closed/manifold/single-component/oriented/no-degenerate/no-duplicate flag screen; **9/11** Badia controls pass. The **No Derivatives** declaration of #230923 and NC/GPL/SA obligations are unresolved per-file rights gates. Primary metadata-screened QuadWild pilots: #67792 and #94884; small Badia controls #293137 and #37881; explicit adversarial QuadWild #61394. The complete 12+11 denominator is retained. **17/17 hermetic Python gate tests passed**, but the Python gate has not been locally run on all original catalog bytes; the full remote catalog was independently parsed and joined in the linked research audit. No original mesh bytes, licensed outputs, verified individual author permissions, numerical QUAD pairs, BP conversion or APMesh accepted mesh were obtained. Do not upgrade statuses or merge the draft PR.
