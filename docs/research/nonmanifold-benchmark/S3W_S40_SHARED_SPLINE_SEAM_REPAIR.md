# S3.W — Original S40 shared cubic spline repair across native planar/cylinder trims

**Date:** 2026-11-17. **Classification:** bounded, experimental scientific proposal. This is neither a behavior-preserving production C++ refactor nor an APMesh TRI/QUAD result. The public research branch and draft PR #225 are the only proposed GitHub targets; `main` is protected. The original source STEP and STEP-derived indexed BP coordinates must remain private pending redistribution-rights review.

## Frozen provenance and failure being corrected

- Exact original STEP: `cgg-bern/hex-me-if-you-can`, revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, `original/i25o_s40.step`, raw SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`.
- Original S3.T source-indexed 132-patch BP: SHA-256 `988d8ed29867927f736838dde20db9efb358c0ee04a202a4f4810ae0e23aa40d`. This **frozen parent is preserved as a separate artifact**; it is not overwritten by the corrected child.
- Original S3.V **rejected** 148-patch candidate: SHA-256 `ba18b866fd70d25b8b9b116354c2673c0294efc6dba8e1e7dca48e8d6536070d`. Its independent original-native classification had **135 `OUT` boundary samples** (63 on source `EDGE_CURVE #85`, 72 on `#2096`). Exact global control sharing alone did not guarantee strict native trimming.
- Repaired S3.W **separate** 148-patch research BP: SHA-256 `c826487d8cee76f6649100c59e5ce84fa6cb43c9004f53c68e3e565e86cdb174`. Only the receipt and this hash, **not the derivative coordinate data**, are eligible for public repository publication.

## Source-canonical, two-sided correction

Original source `EDGE_CURVE #85` joins source planar face `ADVANCED_FACE #17` to cylindrical face `#1519` (7 indexed cubic pieces). Original source `EDGE_CURVE #2096` joins planar `#2092` to cylindrical `#2457` (8 indexed cubic pieces). Both original 3D master edges are degree-five B-splines. Every cubic side was already assigned global integer IDs by the previous cylinder/planar research atlas.

The S3.W builder reconstructs the exact S3.V candidate from immutable original STEP and BP hashes, then changes **only 30 existing shared cubic interior control coordinates** (two controls per one of the 15 original indexed segments). It determines the planar inward direction by the **original native trimmed-face classifier** at a small independent displacement probe; the displacement is **0.0011 mm in the source plane** for each interior control, with unchanged cubic endpoints and unchanged integer control IDs. Both the already-present cylindrical patches and the new planar patches therefore reference the **same corrected control coordinates**. This is an empirically selected coordinated boundary bias, **not** a proof of optimal approximation and not a changed native acceptance tolerance. The fixed experimental geometric budget remains **0.001 mm**; a control displacement is not itself the sampled geometric error.

- **15 previously admitted cylinder patches are geometrically modified**, original patch IDs `64,66,68,70,72,74,76,88–95`. Their global patch nets preserve integer index topology but must be natively re-audited.
- The remaining **117 old patches retain identical 16-control geometry**, including the **30 original source-hole patches** on face `#218` (IDs `96–125`). The original hole remains open.
- All 16 new planar patches retain their source indexed boundary segments, seven original spline segments on `#85`, eight on `#2096`, and their unique original native source-edge identities.
- Combined partial BP: **148 patches**, **1,619 declared global controls**, **239 two-sided exact indexed seams**, **114 open indexed sides**, representing **21 of 43 original source faces** in this *experimental approximate* sense. **22 original faces remain unrepresented.** Do not conflate this with a complete closed STEP BRep or a validated full-model APMesh mesh.

## Independent native evidence (fixed 0.001-mm pilot)

CadQuery 2.8.0, Open CASCADE/OCP 7.9.3.1, NumPy 2.3.5, SciPy 1.17 and Shapely 2.1 were used locally. The independent auditor reconstructs all geometry and hashes, verifies 43 native/source faces, 117 edges and 77 vertices, checks explicit global ID sharing and the exact 30-coordinate mutation ledger, and then rechecks **both incident faces**, rather than the new planar side alone.

| Native gate | Observed result |
| --- | ---: |
| Previously `OUT` original S3.V boundary samples | 135/704 |
| Repaired new planar interior UV samples | **1,296/1,296 `IN`** |
| Repaired new planar boundary UV samples | **704/704 `IN/ON`; zero `OUT`** |
| Dense 101-point-per-segment planar spline boundary | **1,515/1,515 `IN/ON`; zero `OUT`** |
| Same dense samples on incident original cylinders | **1,515/1,515 `IN/ON`; zero `OUT`** |
| Re-audited samples on 15 modified older cylinder patches | **1,815/1,815 `IN/ON`; zero `OUT`** |
| Original inner-hole classifier samples on `#218` | **49/49 `OUT`** |
| Maximum sampled native distance over all eight original boundary edges | **0.00089266861645 mm** |
| Maximum dense sampled native B-spline distance over both edges | **0.00065864763021 mm** (`#85`: **0.000256782871 mm**; `#2096`: **0.000658647630 mm**) |
| Maximum sampled radial cylinder deviation on modified old patches | **0.000682896792 mm** |
| Maximum guarded numeric **bivariate** Bernstein radial support enclosure over modified cylinder patches | **0.00098052395411 mm** |
| Maximum new planar-support deviation | **1.0357e-12 mm** |
| Predeclared experimental geometry budget | **0.001 mm, unchanged** |

The radial enclosure now uses the full bicubic tensor-product **degree-(6,6) Bernstein polynomial** of squared distance to the analytic original cylinder, adaptive two-axis de Casteljau subdivision and a fixed `1e-9 mm` floating-point margin. This is materially different from reusing the old single-angular-parameter certificate on a no-longer-axially-separable patch. **It is not a directed-rounding formal interval certificate.** The smallest final radial margin is approximately `1.95e-5 mm`; it should be re-evaluated for floating-point/platform reproducibility and independently certified before any final scientific publication claim.

Independent Gauss–Legendre area/Jacobian samples confirmed **positive orientation** on the 16 new planar patches and approximate area differences relative to the two source native faces: **0.02802 mm²** for `#17` and **0.04520 mm²** for `#2092` (both below 0.01% of their approximately 488.657 mm² native areas). These differences are **not zero**: the reconstructed patches still approximate the STEP trim. Sampled area conformity does not establish an exact area, complete BRep homeomorphism, global nonoverlap, or continuous trimmed-face Hausdorff certificate. Source-native sidedness is checked at the stated finite point grids and should be challenged with adversarial adaptive sampling.

## Tests, negative controls and closure limitations

- **S3.W new tests:** **36 PASS, 0 FAIL, 0 SKIP**, original pinned STEP and both native incident surfaces. They cover exact source/native hashes; original S3.V failure reproduced; exact control and old-patch lineage; original hole; shared integer seams; native interior/boundary/dense spline and cylinder classification; guarded bivariate Bernstein enclosure; sampled native edge distance and area/Jacobian checks; and adversarial source, BP, manifest, bias, tolerance, forged receipts, wrong shape and corrupted radial controls.
- **Current independent directed regressions:** S3.S–S3.U **70 PASS**, S3.V **30 PASS**, S3.W **36 PASS**: **136 directed cases**, zero failures/skips in three independently completed invocations. A one-shot S3.S–S3.W invocation exceeded the execution limit and must not be marked as one-shot green. The separate S3.M–S3.R frozen 128-pass evidence remains historic; S3.A–S3.L legacy full suite and production C++ / TRI / QUAD suites were **not rerun** on this delivery.
- **Research-only admission:** The 148-patch child now passes this bounded set of native geometry/topology checks. The old frozen 132-patch parent must remain available for regression, and the original 148-patch S3.V rejected candidate must remain labeled rejected. The child **does not** replace the CAD original, nor does it prove complete original CAD coverage, solver acceptance, or a genuine original industrial 3+-incident non-manifold case. Source S40 remains a **manifold control**.

### Reproduction

Supply the authorized byte-pinned original STEP and the private original S3.T BP plus manifest outside public Git. From the research probes directory:

```bash
export APMESH_ORIGINAL_CAD_DIR=/private/originals
export APMESH_S3V_PRIVATE_DIR=/private/s3t
python -m unittest -v test_s3w_s40_shared_spline_repair
python s3w_s40_shared_spline_repair.py \
  --source-step "$APMESH_ORIGINAL_CAD_DIR/i25o_s40.step" \
  --baseline-bp "$APMESH_S3V_PRIVATE_DIR/s40_planar_octagons.partial.bp" \
  --baseline-manifest "$APMESH_S3V_PRIVATE_DIR/s40_planar_octagons_manifest.json" \
  --output-dir /private/s3w-original-native
```

**Next S3.X:** Reclassify the remaining 22 source faces, then prioritize additional conforming original STEP patch islands. Before treating this pilot as a publication-grade CAD reconstruction, independently validate the source-edge approximation envelope, full trimmed-face coverage and the narrow numeric Bernstein margin. Keep actual APMesh TRI/QUAD meshing and a true industrial 3+-incident original as separate mandatory gates. **Keep PR #225 draft; no merge to `main`.**
