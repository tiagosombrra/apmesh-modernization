# S3.Q — Original S40 `ADVANCED_FACE #218`: hole-preserving isolated Bézier island

**Date:** 2026-11-16. **Classification:** bounded scientific research, not C++ production modernization, a full CAD conversion, a connected conforming atlas, or an APMesh meshing result. Branch `research/benchmark-corpus-reverse-patches`, draft PR #225. The prior 77-patch S3.P atlas remains the last globally indexed admitted partial atlas.

## Pinned original CAD and native support

- Upstream: `cgg-bern/hex-me-if-you-can` at immutable revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`.
- Source: `original/i25o_s40.step`, frozen byte-level SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`. Actual local STEP bytes were hash-checked before Open CASCADE import. The raw original STEP is NOT redistributed or committed.
- Original `ADVANCED_FACE #218`, original `CYLINDRICAL_SURFACE #45`, 25 mm radius, native face index **1** through independent first-ring correspondence. Exactly **two original topological wires**: outer loop of eight original edges and **one genuine inner loop** of four distinct original edges. All 12 source edges uniquely match distinct imported native `TopoDS_Edge` objects, each with two incident faces in this *manifold* control.
- Original outer `EDGE_CURVE` IDs in source order: `#222`, `#252`, `#281`, `#21`, `#303`, `#326`, `#355`, `#378`.
- Original inner `EDGE_CURVE` IDs: `#411`, `#440`, `#473`, `#500`. `#411` and `#500` use original 3D B-spline masters and degree-2 source-cylinder `PCURVE` representations, with their original split-edge identities preserved. Their very small nonconstant 2D coordinate residuals are treated as bounded *source* discrepancies, not silently promoted to exact straight original curves. One original inner spline endpoint is approximately **1.405507e-7 mm** from the exact analytic cylinder support; it is **not** claimed to coincide exactly with that support.

## Explicit topology-preserving UV partition

The original source `PCURVE` geometry and source vertex identities define a stepped outer orthogonal domain and a separate interior rectangle. The candidate island subtracts the actual inner region before constructing any patches. Its horizontal angular bands use the fixed subdivision `(1, 2, 5, 2, 1)`; the vertical bands use the five original breakpoints formed by the outer axial limits, outer step, and inner top/bottom limits.

The 30 resulting rectangular UV cells have nonoverlapping interiors and total parametric area equal to **outer source parametric area minus original inner-loop area** (tolerance `1e-7 rad·mm`). Their explicit index keys yield **336 local control points** and **38 integer-indexed internal seams**. None of these counts includes the original 77-patch atlas. An intentionally inserted rectangle covering the hole is rejected by the area and hole-exclusion gates.

The four-sector trial on the wider inner angular interval failed the unchanged **0.001 mm experimental** radial budget at approximately **0.001269206 mm**. Five angular sectors were admitted at approximately **0.000520304 mm** for that trial; the maximum across all proposed cells is higher because other original bands also contribute radial approximation. These are bounded experimental numerics, not advisor-approved final publication tolerances.

## Original S40 native evidence

| Gate | Executed result |
| --- | ---: |
| Candidate **isolated** bicubic patches on `#218` | **30** |
| Isolated control points | **336** |
| Isolated exact integer-indexed internal seams | **38** |
| Original source ↔ native outer boundary edges | **8 of 8**, distinct |
| Original source ↔ native inner boundary edges | **4 of 4**, distinct |
| Native `BRepClass_FaceClassifier` samples strictly inside the original inner hole | **49 OUT / 49** |
| Interior samples on all candidate patches | **2,430 IN / 2,430** |
| Candidate patch boundary samples | **1,320 IN/ON / 1,320** |
| Maximum sampled distance to actual native source boundary, including both B-splines | **0.000606799408 mm** |
| Maximum sampled cylinder projection error | **0.000606799361 mm** |
| Guarded floating-point Bernstein radial support upper estimate | **0.000606800361 mm** |
| Fixed experimental absolute error budget | **0.001 mm** |

The original 3D B-spline curves are sampled as **native BRep curves**, independently of the analytic cylinder-support computation. The radial upper estimate is computed using the Bernstein convex-hull property with a fixed heuristic floating-point margin, **not directed-rounding formal interval certification**. All hole and B-Rep trim checks are discrete samples, **not a continuous homeomorphism or Hausdorff theorem**.

## Critical explicit **rejection of premature global joining**

The prior S3.P BP contains **77** accepted partial-atlas patches, **864** indexed controls, representing **16 of the 43** original S40 faces. It has source-canonical four-control unsplit generators. The new `#218` rectangular partition necessarily splits four of those original generator segments into **two** pieces each:

| Original shared source edge | Other original source face | Prior generator representation | S3.Q candidate representation | Integration |
| --- | ---: | ---: | ---: | --- |
| `#222` | `#1986` (cylinder, already represented) | 1 cubic edge | 2 cubic pieces | **BLOCKED** |
| `#281` | `#1800` (plane, already represented) | 1 cubic edge | 2 cubic pieces | **BLOCKED** |
| `#303` | `#1773` (plane, already represented) | 1 cubic edge | 2 cubic pieces | **BLOCKED** |
| `#355` | `#1986` (cylinder, already represented) | 1 cubic edge | 2 cubic pieces | **BLOCKED** |

The checker verifies the old BP hash, the old source-canonical control index identities, and each new two-piece boundary. It **does not weld by coordinate proximity, change the existing source registry, pretend that a T-junction is conforming, or add the new island to the accepted partial atlas**. The arithmetic number 77+30=107 is a *hypothetical* total and must NOT be reported as an admitted 107-patch BP. The joined admitted state is **still 77 patches / 16 source faces**, with one additional isolated 30-patch source-native candidate.

## Directed tests and independent blocks

- **30/30 S3.Q tests PASS** with the byte-pinned original S40 and original 77-patch S3.P baseline provided. They test source hash, dual wires, quadratic source PCURVEs, source-to-native edge bijection, hole center `OUT`, all patch interior `IN`, actual original boundary curves, radial support, unique indexed seams, tampered BP or manifest, artificial hole fill, changed numeric budget, wrong STEP, wrong native shape, and explicit nonconforming prior-indexed join refusal.
- **91/91 directed tests PASS**, no skips, for S3.M–S3.Q with both environment variables `APMESH_ORIGINAL_CAD_DIR` and `APMESH_MAMBO_SOURCE_DIR` set to the same authorized original STEP directory.
- These are **directed Python research tests**. Full production C++ regression, complete old S3.A–S3.P Python regression, external true three-plus incident non-manifold source admission, full closed CAD atlas, and APMesh TRI/QUAD execution are **NOT RUN / NOT ESTABLISHED** at this checkpoint.

## Reproduction (private original source)

Run with CadQuery 2.8, OCP 7.9, NumPy and first-party research probe dependencies:

```bash
export APMESH_ORIGINAL_CAD_DIR=/private/hexme/original
export APMESH_MAMBO_SOURCE_DIR=/private/hexme/original
export APMESH_S3Q_BASELINE_BP=/private/s3p/s40_complement2457.partial.bp
export APMESH_S3Q_BASELINE_MANIFEST=/private/s3p/s40_complement2457_manifest.json
python -m unittest -q test_s3m_s40_complex_trim_inventory test_s3n_s40_orthogonal_trim test_s3o_s40_spline_trim test_s3p_s40_complement_spline test_s3q_s40_hole_preserving_island
python s3q_s40_hole_preserving_island.py \
  --source-step /private/hexme/original/i25o_s40.step \
  --baseline-bp /private/s3p/s40_complement2457.partial.bp \
  --baseline-manifest /private/s3p/s40_complement2457_manifest.json \
  --budget-mm 0.001 --output-dir /private/s3q/island218
```

Original third-party STEP and BP control coordinates are NOT committed to the public GitHub repository. The separate private research package contains the island BP, earlier private partial BP, full original-native test receipt, and offline CAD viewer only for the researcher's own inspection.

## Next bounded stage S3.R

Conformingly split the original indexed generator cubic controls `#222/#281/#303/#355`, propagating those splits through the admitted native source faces `#1986`, `#1800`, and `#1773` while preserving all other original feature controls and shared source identities. Use exact de Casteljau cubic subdivision and a fail-closed global seam auditor. Re-run native trim, original spline boundary, radial support and hole exclusion across the *combined* atlas. Only then may the new face be considered for the common indexed BP. Genuine original 3+-incident non-manifold support and APMesh TRI/QUAD scientific evidence remain separate, unresolved objectives.

**PR #225 remains draft. No merge to `main`.**
