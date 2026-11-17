# S3.R — Original S40 #218 conforming join by source-identity de Casteljau propagation

**Date:** 2026-11-16. **Classification:** isolated scientific research; no production C++ modification, Stage 3 or QUAD change, or claim of accepted APMesh mesh. Research branch `research/benchmark-corpus-reverse-patches`, draft PR #225. The third-party STEP original and its derived BP coordinates are not committed pending distribution-rights review.

## Exact source and immutability

- Upstream original: `cgg-bern/hex-me-if-you-can`, immutable revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, `original/i25o_s40.step`; byte-level SHA-256: `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`. Raw bytes were independently verified before importing with CadQuery 2.8.0 / OCP 7.9.3.1.
- Original S3.P source-indexed 77-patch BP frozen SHA-256: `c7aa9f71e05d340ad99af6d087011e7f722e5fd2f19bbc87ab39f716845d1ce9`; its JSON manifest canonical serialized SHA-256: `3c86bbadabd0689a93527a397560b36033e18f60db661b442eaa698f8b5c5bbe`.
- Original S3.Q 30-patch isolated holed-face BP was independently rebuilt and required to exactly match its existing manifest before the join.
- The public research repository stores only first-party builder, tests, this document, and a **non-geometric** execution receipt. Neither third-party STEP nor derived BP control coordinates or the CAD tessellation are publicly redistributed.

## Why merely connecting the four obvious edges was insufficient

Original `ADVANCED_FACE #218`, source cylinder radius 25 mm, has one outer and **one genuine inner wire**, with 8 + 4 distinct original `EDGE_CURVE` identities. The source hole must remain open. The S3.Q candidate split original generator edges `#222`, `#281`, `#303`, and `#355` into two cubic boundary pieces, while the previous 77-patch atlas represented each as one cubic. Joining those directly would create T-junctions in the indexed control topology.

The S3.R solver builds an adjacency graph from **existing integer Bézier side-control IDs**, identifies each original `EDGE_CURVE` and its unique previous boundary side via the pinned source control registry, and computes its split parameter from the original source axial break. It propagates the split through any neighboring existing patch where the affected side must stay conforming. An inherited opposite-side adjacency requires the same split (or its reversed parameter). Unexpected conflicting split parameters, ambiguous source edges, unsupported double-axis splitting, changed source or manifest hashes, or an altered error budget raise an error instead of emitting a BP.

Measured closure: **19 of the existing 77 patches** require one de Casteljau subdivision each:

| Old parent patch IDs | Split direction | Number | Root original source edge |
| --- | --- | ---: | --- |
| `3,4` | U | 2 | `#303`, `#281` respectively |
| `25–29` | V | 5 | `#355` |
| `30–34` | V | 5 | `#222` |
| `52–55` | V | 4 | `#281` |
| `56–58` | V | 3 | `#303` |
| **Total** | — | **19** | **4 seed edges** |

The affected original faces include the previously represented cylindrical faces `#1986` and `#1519`, as well as planar patches corresponding to original adjacent faces `#1800` and `#1773`. These changes **only reparameterize** the existing bicubic surfaces. Original existing control IDs remain unchanged; new split-edge controls receive source-edge/control-lineage keys, not geometrically welded IDs. Source generator interior controls which become superseded are retained in the frozen prefix of the control array for provenance; they are not misrepresented as active unsplit sides.

## Combined private BP: actual original native results

| Evidence | Measured result |
| --- | ---: |
| Previously admitted partial atlas | **77 patches / 864 global controls / 16 original faces** |
| Previously admitted patches after 19 conforming splits | **96** |
| S3.Q holed face `#218` added | **30 patches** |
| **Combined conforming research BP** | **126 patches / 1,467 declared controls (1,349 active, 118 retained historical IDs)** |
| Active controls referenced by the combined BP | **1,349** |
| Historical original controls retained but no longer referenced | **118** |
| Compact consumer-oriented BP controls, with explicit old→new ID map | **1,349** |
| Original CAD faces covered | **17 / 43**; **26 remain unrepresented** |
| Global indexed BP seams of exactly two sides | **179** |
| Global indexed BP open side segments (partial atlas) | **146** |
| Original STEP generator join identities with two new pieces on both sides | **4 / 4**, 8 matching side pairs |
| Original source/native hole boundary edges | **4 / 4**; total outer+inner source/native edges **12 / 12** |
| Native hole center samples `OUT` | **49 / 49** |
| Holed-face interior samples `IN` | **2,430 / 2,430** |
| Holed-face boundary samples `IN/ON` | **1,320 / 1,320** |
| Original neighboring cylinder retopology children rechecked natively | **34** (`#1986`: 20; `#1519`: 14) |
| Neighboring child native interior samples `IN` | **1,666 / 1,666** |
| Neighboring child boundary samples `IN/ON` | **1,224 / 1,224** |
| Maximum difference between old and de Casteljau-reparameterized surfaces, sampled (mm) | **2.01e-14** |
| Maximum source/native original edge sampled deviation on holed face (mm) | **0.000606799408** |
| Holed-face guarded numeric radial support upper estimate (mm) | **0.000606800645** |
| Neighbor child maximum sampled native cylinder projection deviation (mm) | **0.000892668647** |
| Predeclared experimental geometric budget (mm) | **0.001** |

The provenance-preserving array **declares 1,467 control points, of which 1,349 are active**. The remaining **118 unused control points** are exclusively old S3.P declarations superseded by exact de Casteljau subdivision. Their historical original indices are retained in the first 864 declarations so existing source controls and their lineage remain auditable. A separate deterministic **compact BP with 1,349 declared and active controls** deletes those 118 inactive declarations, supplies an explicit old-to-new integer ID mapping, and preserves every patch control net exactly; it is a consumer-oriented derivative rather than the authoritative historical-ID atlas. Source-identified split controls are shared on both sides of all eight joined original-edge pieces. The continuity check audits equality of **integer indices**; coordinate distance is used only as a consistency/rejection test after source identity is established.

## Execution and explicit limitations

The S3.R builder emits a combined indexed polynomial bicubic `.bp`, a separately compacted `.bp`, an explicit compact-ID map and a scientific manifest only after every original source-input hash, cardinality, original side lineage and resulting topology check passes. A **separate native re-auditor** recomputes the BP, verifies old-surface invariance, reruns original S3.Q native source-edge and hole checks, recomputes the new holed-face boundary/native UV/radial gates, and checks the 34 affected old cylinder children directly on the original native BRep.

Local original-source tests: **37/37 new S3.R PASS**. Cumulative *directed* S3.M–S3.R: **128/128 PASS**, zero skips, zero failures, using the frozen original S40 STEP and the private original-derived parent BP. This is **not** the entire S3.A–S3.R regression or any C++ production scientific regression. Results and original derivative coordinates are preserved privately. A viewer offline displays the whole original S40 CAD, 96 reparameterized prior patches, and 30 joined holed-face patches; the viewer tessellates surfaces for inspection and is **not** an APMesh TRI/QUAD mesh.

**Important bounded scope:** Although the partial atlas is conforming at its indexed two-sided seams, it is still **not a complete closed 43-face S40 surface**, nor a mathematically continuous certificate of the trimmed hole domain, a directed-rounding interval-bound theorem, an original external 3+-incident non-manifold positive, or evidence of meshing/acceptance by the APMesh C++ engine. The Bernstein bound is evaluated in floating-point arithmetic with an explicit heuristic margin, and native UV/edge checks are sampled. The 0.001-mm budget is an experimental pilot, not an advisor-approved acceptance threshold.

## Reproduction

Install the first-party S3.A–S3.R probe dependencies together with CadQuery/OCP. Provide the original third-party STEP **privately**, outside any redistributed package, and the frozen S3.P and S3.Q BP/JSON fixtures:

```bash
export APMESH_ORIGINAL_CAD_DIR=/private/hexme/original
export APMESH_MAMBO_SOURCE_DIR=/private/hexme/original
export APMESH_S3Q_BASELINE_BP=/private/s3r/private_bp/s40_previous_77_patches.partial.bp
export APMESH_S3Q_BASELINE_MANIFEST=/private/s3r/private_bp/s40_previous_77_patches_manifest.json
export APMESH_S3R_PRIVATE_DIR=/private/s3r/private_bp
python -m unittest -q test_s3m_s40_complex_trim_inventory test_s3n_s40_orthogonal_trim test_s3o_s40_spline_trim test_s3p_s40_complement_spline test_s3q_s40_hole_preserving_island test_s3r_s40_conforming_hole_join
python s3r_s40_conforming_hole_join.py \
  --original-step "$APMESH_ORIGINAL_CAD_DIR/i25o_s40.step" \
  --prior-bp "$APMESH_S3R_PRIVATE_DIR/s40_previous_77_patches.partial.bp" \
  --prior-manifest "$APMESH_S3R_PRIVATE_DIR/s40_previous_77_patches_manifest.json" \
  --island-bp "$APMESH_S3R_PRIVATE_DIR/s40_face218_hole.isolated.bp" \
  --island-manifest "$APMESH_S3R_PRIVATE_DIR/s40_face218_hole_manifest.json" \
  --output-dir /private/s3r/result
```

## Next bounded research gate — S3.S

With **17/43 original S40 faces** now represented conformingly in a partial source-indexed BP, audit **all** original source `ADVANCED_FACE` classes, classify unrepresented regions by geometry and trim complexity, and select a bounded next-face reconstruction rather than claiming full model closure. Require new source-native identity, original boundary constraints, source spline geometry, copied or split control lineage, native trimmed UV, budget and negative tests before any new original face admission. Separately continue the search for an **actual original non-manifold multi-sheet positive**, and only after a scientifically admissible atlas attempt APMesh TRI/QUAD production and quality measurements. Keep PR #225 draft; do not merge to `main` without advisor review and exact-head scientific regression.
