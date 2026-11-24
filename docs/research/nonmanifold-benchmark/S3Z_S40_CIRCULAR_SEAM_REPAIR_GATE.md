# S3.Z — S40 original: shared circular-seam repair gate (not admitted)

**17 November 2026 — Research-only preflight; no new CAD-native execution in this checkpoint.** Keep PR #225 draft and protected `main` unchanged. Do not count the experimental repair as an accepted atlas until it passes the original native gates.

## Verified inherited S3.Y result

The admitted selective S3.Y child contains **156 source-indexed bicubic patches, 1,665 declared controls, 264 exact two-sided indexed seams, 96 open sides and 22/43 represented STEP faces**. Original S40 is a manifold control, not an original 3+-incident non-manifold positive. The byte-pinned source is `original/i25o_s40.step` at upstream revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`. S3.W parent BP SHA-256 is `c826487d8cee76f6649100c59e5ce84fa6cb43c9004f53c68e3e565e86cdb174`; the selected S3.Y child SHA-256 is `af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177`.

The rejected *joint* S3.Y candidate contains 160 patches and has **36 original planar-boundary OUT samples**: 18 on face `#1827` and 18 on `#1907`. This is the previous S3.Y evidence, not a new S3.Z native measurement. Only `#3044` was admitted in S3.Y.

## Proposed source-canonical correction

Two source planar faces remain blocked. Each has four original CIRCLE and two original LINE edges. Target original circular `EDGE_CURVE` IDs:

- `#1827`: `#1523`, `#252`, `#1834`, `#1886`.
- `#1907`: `#1911`, `#1962`, `#326`, `#1593`.

A local exploratory Python gate, delivered privately with this checkpoint, reconstructs S3.Y from exact original STEP/BP hashes, matches every source-identified inherited cubic edge, and tests fixed control-bias candidates from 0 to 0.0014 mm. These values are **coordinate displacement trials**, not geometry tolerances: the historical **0.001-mm geometric error budget is unchanged**.

The gate moves only two interior controls of each of the eight source-canonical cubic circles, using the direction inferred from the real original planar trim classifier. Both incident sides reuse those **same integer global control IDs**. It recomputes the four newly constructed planar Coons interiors, checks the original `#3044` child and hole `#218` remain unmodified, and requires:
1. Unique source/native `EDGE_CURVE` owners, permitted adjacent CYLINDER support and fully pinned inherited patch-side lineage.
2. Native planar and cylindrical `IN/ON` for dense source-arc samples; source/native curve deviation within the fixed budget.
3. Positive new-planar Jacobians, bounded area mismatch, `IN/ON` for all sampled candidate interiors and boundaries, and no indexed hanging seams.
4. Native `IN/ON` on each affected earlier cylindrical patch, with a guarded full-bicubic Bernstein radial bound below the fixed budget; explicit rejection on ambiguity.
5. A separate independent regression of previous admitted patches and source `#218` hole before promoting any candidate.

**Admission remains blocked.** The local research routine produces *trial receipts only*, does not publish source-derived coordinates or a repaired 160-patch BP, and does not claim a continuous trimmed-Hausdorff certificate, APMesh TRI/QUAD generation or production C++ regression.

## What was actually run

This checkpoint ran **13 hermetic directed Python unit tests, 13 PASS / 0 FAIL**, checking original and parent hash gates, unchanged budget, source edge ID sets, Bernstein cubic math, inward direction (including ambiguity and reversal), Coons boundary preservation and index-overlap protection. Python compilation passed. **Original S40-native S3.Z trial runs were not executed in the current environment because the original STEP and private BP files were not mounted.** Historical 31/31 S3.Y tests were previously reported but are not counted as S3.Z executions.

For a future original run, supply authorized private source/BP and the published `s3y_s40_curved_planar_rings.py`, then run the separate S3.Z private pilot. If every candidate fails, preserve the selected **156-patch, 22-face** child and investigate conforming source-edge subdivision instead of relaxing tolerances.

No branch merge, release, production or solver certification is authorized by this preflight.
