# S3.N — Original S40 #1986 source-anchored orthogonal trim decomposition

**Date:** 2026-11-16. **Classification:** bounded research-only scientific proposal. This work changes neither the APMesh production C++ generator nor any Stage 3/QUAD branch. The research PR #225 remains a draft.

## Original source and native target

- Source: `cgg-bern/hex-me-if-you-can`, revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, original `i25o_s40.step`.
- Frozen byte-level SHA-256: `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`, recomputed and admitted before native import.
- STEP target: `ADVANCED_FACE #1986`, imported source-to-native face index **17**, `CYLINDRICAL_SURFACE`, radius **25 mm**, a single outer wire with eight `EDGE_CURVE` entities; no inner wire and no spline PCURVE on this face.
- The eight original source boundary identities are four `LINE` generators (`#222`, `#355`, `#2019`, `#2071`) and four `CIRCLE` arcs (`#1991`, `#1962`, `#2042`, `#1834`). No source identities are merged by proximity.

## Derivation from source PCURVEs

The eight oriented source edges form a stepped orthogonal polygon in the cylinder's original UV domain. Rounded bounds: `u = [π, 3.342950574392, 6.081827386377, 2π]`, `v = [-16.5, -10.5, 16.5]` (the exact original finite-precision values are extracted on every run, never guessed from these rounded illustrations).

The domain is the union of an upper band spanning the complete U interval for `v∈[-10.5,16.5]`, and a lower central tab on `u∈[3.342950574392,6.081827386377]`, `v∈[-16.5,-10.5]`. The upper band is subdivided into a left strip, eight middle sectors, and a right strip; the lower tab has the **same eight middle U sectors**. This yields **18 conforming rectangular parameter patches** and **24 new internal global-indexed seams**. The 2D polygon and rectangular-union parameter area agree at approximately `101.2562625184136 rad·mm`; all pairwise rectangle interiors are disjoint. This is a parametric-area and orthogonal-polygon coverage check, not a physical area or full BRep homeomorphism certificate.

The original circle `#1991` is represented by 10 polynomial boundary pieces and `#2042` by eight; each of `#1962` and `#1834` uses one. The four original axial generators each remain one full edge with exactly four canonical indexed controls. Derived subdivisions retain their source original curve provenance, and derived seams have separate keys.

### Source/native original edge correspondence

| Original source edge | Native edge index | Original master curve | Number of represented boundary pieces |
|---|---:|---|---:|
| `#222` | 4 | `LINE` | 1 |
| `#1991` | 64 | `CIRCLE` | 10 |
| `#355` | 9 | `LINE` | 1 |
| `#1962` | 63 | `CIRCLE` | 1 |
| `#2019` | 65 | `LINE` | 1 |
| `#2042` | 66 | `CIRCLE` | 8 |
| `#2071` | 67 | `LINE` | 1 |
| `#1834` | 58 | `CIRCLE` | 1 |

Each original boundary maps uniquely to a distinct native `TopoDS_Edge`; each of those native edges was observed with two incident source/native faces in the original manifold control. Original shared generator `#2019` connects to planar `ADVANCED_FACE #2430`, and `#2071` connects to planar `#2403`; the combined indexed BP reuses **the eight existing global control indices** of these two source edges, without welding geometrically close controls.

## Measured native outcomes

The S3.L baseline (nine source planar faces and four previously admitted source cylinders) is **recomputed byte-for-byte from the original STEP**, not merely trusted from its sidecar, before extending the BP. Previous partial BP: 25 patches, 320 controls. New original S40 partial BP: **43 patches, 511 distinct global controls**, representing **14 of 43 original `ADVANCED_FACE` entities**; **29 remain unrepresented**.

A fixed experimental numeric radial budget of **0.001 mm** was applied before the trials. Seven middle sectors were rejected by the radial-support enclosure (approximately `0.001522 mm`). Eight middle sectors were admitted:

- Guarded Bernstein radial support upper estimate: **`0.0008926699965751233 mm`**.
- Maximum sampled point-to-imported-native-cylinder projection distance: **`0.0008926686467705835 mm`**.
- Maximum sampled distance to the **actual original trimmed native edge** across 216 total source-boundary samples: **`0.0008926686383052053 mm`**.
- **1,458** native trimmed UV interior sample checks and **792** boundary checks; all were admitted by native face classification.
- **Eight** original source edges, each unique in the native graph; **24** new internal seams by equality of BP integer control indices. Two original plane-cylinder generators retain their eight prior global control IDs.

The Bernstein numeric radial result uses floating-point polynomial coefficients, the convex-hull property, recursive subdivision and an explicit heuristic margin. It does **not** constitute a directed-rounding formal numerical certificate, a continuous bound for the complete trimmed BRep, a full Hausdorff-equivalence proof, or an advisor-approved final meshing tolerance. Discrete UV membership and original edge proximity are additional independent gates but remain sample-based.

## Reproduce (private, pinned original)

Use CadQuery 2.8, OCP, NumPy and the same-directory S3.A–S3.M research probes. Keep the original STEP file and any STEP-derived BP outside the public Git repository pending the redistribution-rights review. The command verifies the original SHA before importing or writing results:

```bash
python docs/research/nonmanifold-benchmark/probes/s3n_s40_orthogonal_trim.py \
  --source-step /external/mambo/sources/i25o_s40.step \
  --baseline-bp /private/s3l/s40_second_ring.partial.bp \
  --baseline-manifest /private/s3l/s40_second_ring_manifest.json \
  --middle-sectors 8 --budget-mm 0.001 \
  --output-dir /private/s3n/s40_step1986
```

Run directed tests with `APMESH_ORIGINAL_CAD_DIR=/external/mambo/sources` and `APMESH_MAMBO_SOURCE_DIR=/external/mambo/sources`:

```bash
python -m unittest -v \
  test_s3m_s40_complex_trim_inventory \
  test_s3n_s40_orthogonal_trim
```

**Actually executed directed tests:** 19 S3.N tests PASS and nine S3.M tests PASS (**28/28, zero skipped and zero failed**), with frozen original S40 mounted. Controls reject modified source SHA, incorrect budgets, too-coarse sectors, original boundary omissions, forged manifests, forged valid BP with recalculated hash and changed source controls.

**Accumulated entire-suite attempt:** the combined research unittest discovery exceeded the available execution interval and was interrupted. **No new cumulative 198/207-style passing count is claimed**. The earlier S3.L 179/179 evidence remains a different, previously completed scope. Neither the full C++ production regression nor APMesh accepted TRI/QUAD generation ran in S3.N.

## Deliverable and next gate

A new offline Plotly 3D viewer separates the complete original S40 CAD tessellation, the previous 25-patch atlas and the new 18-patch source face. A true UV plot shows all 18 rectangles and the eight original source `EDGE_CURVE` IDs. These visualizations are for inspection, **not** proof of APMesh mesh generation. Source STEP bytes are not redistributed.

**Next S3.O candidate:** source-first treatment of the split B-spline boundaries of S40 `ADVANCED_FACE #1519`, then `#2457`. The separate `#218` source/native inner hole must remain intact. Full CAD coverage, external original three-or-more-sheet non-manifold admission, production and scientific C++ regressions, accepted APMesh TRI/QUAD, mentor review and main merge remain OPEN.
