# S40-F30 — Feature-locked Pareto improvement of a private derived QUAD surface

**Date:** 2026-11-23. **Repository:** `tiagosombrra/apmesh-modernization`, research branch `research/benchmark-corpus-reverse-patches`, Draft PR #225. **Classification:** source-pinned, externally derived computational experiment and research proposal; **not** a native APMesh QUAD feature, approved quadrangulation algorithm, scientific benchmark admission, or license clearance.

## Scope, audited inputs and source dependencies

This experiment is **strictly downstream** of the unchanged original C++ APMesh F27 TRI run, F28 source-topology stitched TRI, and F29 private derived four-sided patch recovery. All original `.stl`, `.stl.zip`, `.bp`, native `.obj`, full-precision incidence snapshots and F28/F29/F30 derived OBJ outputs remain **PRIVATE**, outside Git. The F27 two original native runs are revalidated by their actual config, binary digest, output provenance and successful process receipts before F30 is allowed to run. Their complete, original F28 and F29 derived outputs are regenerated and hash compared against private originals.

- Original Thingi10K #293137 STL SHA-256: `4a222346223cf2c207c34d7a3d4e8ea297b004ff862b06b6e4c7c2eeac9f761a` (292 TRI, closed, no known author CAD data).
- Research-derived indexed `.bp` SHA-256: `6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0` (876 planar bicubic Bézier patches, 7,886 controls).
- Actual unchanged native F27 TRI OBJ SHA-256: `145b40c2f542a9d1d18bcda6eccc01c8861be83d247418af96fa18b4c860c325` (3,504 TRI).
- F28 source-aware derived stitched TRI SHA-256: `b93995d1319e702649574044b2167fa01fe90644b1e5e02a295f3b47cdfdc46b`.
- F29 private derived recovered QUAD SHA-256: `e2687802ec3314178a973282a33ffd86d71ee8aaa87eed3d4976b266000cf548`, **38,834 bytes**, 876 QUAD, 878 V.
- F30 **new private, non-native** external QUAD artifact SHA-256: `7714c25de7774521d59157ba49e0733d315d462ab05117e2b578dcc57f596be4`, **39,150 bytes**. Two separate private processes with reversed source-native run order produced identical bytes; these geometry bytes are **not published**.

## Mathematical obstruction: the source-corner quality ceiling

For each original oriented STL triangle \((a,b,c)\), the F21/F22 input construction divides it into three four-sided sectors. The F29 quadrilateral associated with source vertex \(a\) is \((a,m_{ab},t,m_{ca})\), where \(m\) are fixed geometric edge midpoints and \(t\) is the original triangle centroid. The other two sectors are cyclic permutations.

For every modified center \(t'\) restricted to the interior of the **same source triangle**, the two QUAD segments incident on the original vertex \(a\) remain collinear with the original source edges \(ab\) and \(ac\). Thus the original source angle \(\theta_a\) remains **exactly** a corner angle of the corresponding QUAD. It follows that, for any optimizer that retains these vertices, edge midpoints and three-sector topology:

\[
\min_{q}\theta_{\min}(q) \;\le\; \min_{\mathrm{STL\ corners}}\theta,
\qquad
\min_{q}J_{\min}(q) \;\le\; \min_{\mathrm{STL\ corners}}\sin\theta.
\]

These are **upper bounds on the maximum attainable global minimum**, *not lower bounds on arbitrary candidate-mesh quality*. For this pinned model, both F29 and F30 already attain those ceilings: **1.1052825555°** and **0.01928962331**, respectively. No center-only optimization can improve either worst-case value. In the original triangle geometry, **121 original facet corners** lie below 30°, **9** below 10°, and **4** above 150°; these are unavoidable lower bounds on the corresponding number of bad QUAD sector faces when the source corner remains fixed. Other, center-controlled corners are improvable.

## Exact constrained search and hard acceptance rules

F30 changes **one internal point per original STL triangle** (never moves any original source vertex, edge midpoint, interpatch seam, or sharp source edge). It evaluates **171** deterministic interior rational barycentric candidates of denominator 20 for each source facet. Candidate centers are constructed in original STL XYZ, remain strictly inside the triangle, and must yield **three convex, planar, correctly oriented quadrilaterals** on the same facet with preserved summed area (relative bound `1e-11`). The three QUAD keep the exact F29 connectivity; no source face is paired with a different facet.

A candidate is admitted **only when all three individual QUAD sectors** are at least as good as the previous accepted configuration in all of:

- minimum interior angle not reduced, up to `1e-10°` arithmetic guard;
- maximum interior angle not increased, up to `1e-10°` guard;
- minimum corner scaled Jacobian not reduced, up to `1e-12` guard.

At least one of those indicators must **meaningfully improve** (`1e-6°` or `1e-8` scaled Jacobian). Candidate order is fixed. The algorithm is a **finite Pareto-monotone greedy search**; it does **not** establish a globally optimal center position, an optimality certificate, a fair comparison with native quadrangulators, a new mathematical shape-quality theory or a new APMesh native mesher. A distinct, more aggressive unconstrained search could yield better means while making some individual quads worse; that variant is **not** admitted in F30.

## Real private F29 vs F30 result (full original STL precision)

| Dimensionless/angle indicator | F29 baseline | F30 strictly non-regressing candidate |
|---|---:|---:|
| Recovered QUAD / vertices / edges | 876 / 878 / 1,752 | **876 / 878 / 1,752** |
| Mean of per-QUAD minimum scaled Jacobians | **0.59806082285** | **0.67297475172** |
| Global minimum corner scaled Jacobian | 0.01928962331 | **0.01928962331 (immutable ceiling)** |
| Mean of per-QUAD minimum corner angles | 45.2481° | **49.6338°** |
| Global minimum corner angle | 1.10528° | **1.10528° (immutable ceiling)** |
| Global maximum corner angle | 178.82520° | **176.90212°** |
| QUAD with min corner angle < 30° | 159 / 876 (18.15%) | **126 / 876 (14.38%)** |
| QUAD with min corner angle < 10° | 11 / 876 (1.26%) | **11 / 876 (1.26%)** |
| QUAD with max corner angle > 150° | 160 / 876 (18.26%) | **20 / 876 (2.28%)** |
| Native mesher QUAD implementation/execution | No | **No** |

The mean per-QUAD minimum scaled Jacobian increased by **12.526% relative**, the count below 30° fell by **33/159 = 20.75%**, and the count above 150° fell by **140/160 = 87.5%**. All those comparisons use **the same 876 fixed-topology QUAD** and the same facet-local, source-derived geometry, not the original F27 TRI `2r/R` metric.

- Original STL facets with relocated internal centers: **189 / 292**; remaining **103 / 292** unchanged.
- Maximum center displacement / maximum length of its own original triangle edge: **0.1302112**. Mean normalized displacement over all facets: **0.0459746**.
- Original STL edge midpoint and source-vertex positions changed: **0**. Source edges: **438/438** preserved as **876** boundary segments; sharp STL edges with signed-normal dihedral at least 30°: **205/205**, representing **410** retained split segments.
- Quad connectivity unchanged, one orientable closed component, no free/nonmanifold edges or disconnected vertex links, Euler characteristic **2**, genus zero under those conditions. The summed **full-precision** QUAD area remains **29,490.715496607303 square original-source units**, equal to the source STL to the evaluated numerical tolerance.
- No smoothing of sharp edges, no changes to original production C++, and **no proof of global freedom from self-intersections**. A swept-triangle or exact-predicate intersection audit remains a separate gate.

## Repetitions, independent check and export precision

Two separate private F30 CLI processes were run with **reversed F27 original native-output order**, using the two separately produced F29 private QUAD files. They emitted identical output SHA-256 (`7714c25d...596be4`), and independently reproduced all full-precision quality/provenance checks. Neither the private OBJ nor any source mesh was copied to GitHub.

An optional **Trimesh 4.11.1** verifier independently read both private four-sided OBJ files, verified exact unchanged four-node face records, **189 changed exported vertex rows**, identical vertex count (878), one closed connected orientable body, 1,752 triangles after Trimesh internal splitting, Euler 2 and positive volume. Because OBJ XYZ are six-significant-digit rounded, the F29→F30 exported area and volume differ by only **3.32×10⁻¹¹** and **1.42×10⁻⁸** relative, respectively. The full-precision STL source-facet partition is exactly preserved within machine precision; rounded OBJ volume changes are **not** CAD-surface validation. Neither Trimesh nor the source proof certifies a global no-intersection condition.

## Protocol criteria for an eventual native QUAD proposal

1. **Hard topology admission:** no illegal seam/feature unions; closed, orientable surface; correct facet/crease correspondence; no singular links, self-overlaps, nonmanifold edges or malformed indices. An intersection test would still have to be added.
2. **Geometric hard constraints:** maintain exact user-specified feature edges, finite non-inverted quads, planar source-facet adherence for piecewise-linear specimens and independently bounded area/volume drift. Any movement of an original geometric feature or switch to approximation must be separately admitted.
3. **Shape-quality acceptance:** report global minimum and distribution of corner-scaled Jacobian, lower/upper corner-angle tails and their denominators; distinguish immutable source-angle ceilings from improvable center-controlled distortions. Do not substitute TRI `2r/R` for QUAD quality.
4. **Regression contracts:** no degradation per QUAD of the three chosen shape indicators for this conservative baseline; reproduce original reference files and privacy-safe receipts. A different algorithm or altered corner/feature policy requires a new versioned experimental contract.
5. **Scientific controls:** use rights-cleared, multiple source models, original QUAD-generating executable/output pairs, comparable geometry and sampling resolution, repeated performance/quality runs and advisor-approved methodology. No original model or matched QuadWild literature reference is admitted here.

**Next research gate (F31):** discuss with professors Creto and Bento whether to implement a **native, explicitly experimental QUAD element/export/generator module**, and whether constrained center relocation is scientifically relevant to the research goals. Prioritize source-independent quality criteria and multiple datasets over fitting the existing single #293137 input. `main`, frozen S40/M5/M3 baselines and all native F27/F28/F29 outputs remain unmodified.

## Public code and reproducibility without third-party data

- `probes/thingi10k_f30_feature_locked_quad_center_optimizer.py`: source-pinned, deterministic, authorization-checked private replay and Pareto center search.
- `probes/test_thingi10k_f30_feature_locked_quad_center_optimizer.py`: **60** isolated synthetic and rejection tests with no original-model data.
- `probes/thingi10k_f30_optional_trimesh_crosscheck.py`: optional external library check on private derived files.
- `evidence/thingi10k/thingi10k_f30_final_real_pareto_receipt.json`: coordinate-free numerical original-model receipt.
- `evidence/thingi10k/thingi10k_f30_external_trimesh_receipt.json`: coordinate-free external check.
- `.github/workflows/research-f30-quad-quality-pareto.yml`: code-only CI for F27–F30 sources and strict private-geometry exclusion.

Use the F30 Python CLI only with an **authorized private copy** of the original Thingi10K source zip, BP and two F27 native process runs, plus the verified F28/F29 derived files; the program **refuses to overwrite** an existing F30 output or receipt. No public test embeds the original STL/BP or vertex coordinates of #293137.
