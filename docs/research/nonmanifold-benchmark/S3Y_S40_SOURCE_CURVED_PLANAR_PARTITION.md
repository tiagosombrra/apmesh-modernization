# S3.Y — Original industrial S40: source-indexed curved planar closure and fail-closed selection

**Date:** 2026-11-17. **Classification:** isolated scientific research proposal; not a production C++ refactor or APMesh TRI/QUAD execution. Research branch `research/benchmark-corpus-reverse-patches`, draft PR #225. The protected `main` and the original mesher remain unchanged.

## Frozen CAD/atlas provenance

- Original external HexMe/MAMBO S40 STEP, upstream revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, file `original/i25o_s40.step`, original raw SHA-256 **`b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`**.
- Native Open CASCADE correspondence: **43 original faces**, **117 original edges**, **77 original vertices**. All three targets map to uniquely source-correlated native faces, not visually proximate tessellation faces.
- Frozen admitted S3.W input: **148 source-indexed cubic Bézier patches**, **1,619 declared controls**, **239 two-sided indexed seams**, 114 open sides, **21/43 original STEP faces represented**. BP SHA-256 **`c826487d8cee76f6649100c59e5ce84fa6cb43c9004f53c68e3e565e86cdb174`**.
- No third-party STEP bytes or derived BP coordinates are included in the public source repository. The private research package can contain derived indexed BP coordinates for authorized examination, subject to third-party redistribution-rights review.

## Three source candidates: preserve the original six-edge topology

| Original `ADVANCED_FACE` | Unique native face | Frozen inherited source edge segments | Quads candidate | Original-native boundary `OUT` samples (11 samples per patch side) | Admission |
| --- | ---: | ---: | ---: | ---: | --- |
| `#1827` | 15 | 6 | 2 | **18** | **BLOCKED**: existing circle approximations leave strict original planar trim |
| `#1907` | 16 | 6 | 2 | **18** | **BLOCKED**: existing circle approximations leave strict original planar trim |
| `#3044` | 29 | 18 (four source circles × four cubic pieces + two source lines) | 8 | **0** | **PASS** within explicit sampled pilot gates |

Every source edge has exactly two original STEP incident faces. The builder reuses a frozen list of **original source edge -> prior patch ID / side** identities and independently checks those source IDs against unique imported `TopoDS_Edge` identities, original STEP endpoint vertices and each native curve. It never welds points by geometric proximity. The inherited open sides are chained using **existing global integer endpoint IDs**, checked against the original source wire direction and canonical source vertices.

Original `#3044` source edges, each independently native-matched: `#3048` (`LINE`, 1 piece), `#3071` (`CIRCLE`, 4), `#2886` (`CIRCLE`, 4), `#2833` (`LINE`, 1), `#2942` (`CIRCLE`, 4), and `#2994` (`CIRCLE`, 4). The source/native native edge indexes are 96, 97, 90, 88, 92, and 94 respectively. The 18 inherited cubic boundary pieces were partitioned by a convex quadrilateral dynamic-programming solver into **8 quadrilateral patches using seven newly indexed internal diagonals**. A degree-three planar Coons net preserves the four inherited source-ID boundary curves exactly for each patch. In the projected chord-polygon model the eight quads have disjoint interiors and their areas sum to the chord-polygon area; **chord-polygon area is not the actual curved native area**.

## Admitted bounded candidate on `#3044`

The **S3.Y selected child** is produced separately from the rejected joint 160-patch candidate. The original 148 patches and original 1,619 controls remain an exact unchanged prefix of the S3.Y child. The original holed face `#218` and the S3.W repaired shared B-spline controls remain unchanged.

| Geometric/topological check | Measured original-S40 result |
| --- | ---: |
| Previous S3.W partial BP | 148 patches, 1,619 controls, 21/43 source faces |
| New original `#3044` region | **8** patches, **46** new global controls |
| **Combined bounded research BP** | **156 patches, 1,665 declared controls, 22/43 source faces represented** |
| Exact two-sided integer-indexed seams | **264** (previous 239 + 18 original shared source segments + 7 new diagonals) |
| Open indexed sides in still-incomplete original CAD | **96** (previous 114 − 18 now joined original source segments) |
| Original native trimmed-face interior samples | **2,312/2,312 `IN`** |
| Original native trimmed-face boundary samples | **992/992 `IN/ON`, zero `OUT`** |
| Original native boundary-curve samples | **378** |
| Maximum sampled original native boundary deviation | **0.0005559481871036685 mm** |
| Maximum sampled planar-support deviation | **5.3291e-15 mm** |
| Native source `#3044` surface area | **578.4690049407732 mm²** |
| Approximate 12×12 Gauss–Legendre Bézier area | **578.4522687647700 mm²** |
| Signed sampled/integrated area difference | **−0.016736176003178116 mm²** (absolute relative ≈ **0.002893%**) |
| Minimum sampled outward oriented Jacobian | **0.22367256684432757** |
| Sampled projected patch overlap area | **3.41e-13 mm²** (floating point noise) |
| Sampled spurious numerical hole area | **3.95e-14 mm²** (floating point noise) |
| Fixed experimental geometric budget | **0.001 mm, not relaxed** |
| Selected child private BP SHA-256 | `af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177` |

The planarity, boundary matching, outward Jacobian and finite native trim classification were checked independently of mere equality of global indices. The source-native envelope remains **sampled**, not a formal continuous trimmed Hausdorff proof, exact physical area equivalence or directed-rounding interval theorem. Parent and child are **partial surface representations**, not original complete CAD solids. S40 has no 3+-incident original edge and is a **manifold** industrial control.

## Explicit rejected joint candidate

The full three-face construction would have **160 patches** and **1,685 controls** with 278 exact two-sided integer seams, but still reports **36 native boundary `OUT` samples**, all on `#1827`/`#1907`, despite a maximum sampled source-curve deviation within 0.001 mm. The joint candidate **MUST NOT** replace the selected 156-patch child or be described as admitted. A geometric fit-budget pass alone does not permit replacing native trimmed-domain membership. Next S3.Z: investigate **coordinated original-edge curve correction on both incident faces** for the two blocked sides; independently check the old neighboring curved faces and any thin bivariate radial margins before admitting any new region.

## Reproducible tests and their scope

Using original CadQuery/Open CASCADE, NumPy, SciPy and Shapely, the current directed tests completed as three independent processes against exactly the same S40 original and frozen S3.W parent:

- S3.W prior regression: **36/36 PASS**, no skips.
- S3.X prior native gap/margin regression: **23/23 PASS**, no skips.
- S3.Y targeted original S40 positive/negative suite: **31/31 PASS**, no skips.
- **Total: 90/90 directed tests PASS** in three processes. This is **not** a full S3.A–S3.Y, C++ APMesh or mesh-generation regression.

The S3.Y tests cover source/baseline hashes; original face and native edge bijection; each original inherited side control lineage; exact unchanged prior control/patch prefix; exact globally indexed interface closure; positive orientation and 12×12 Gauss–Legendre approximate area; no material interior overlap or new hole; source/native curve fit; original trimmed UV membership; and adversarial modified source, parent, manifest, budget, repeated or unknown targets. They also assert the correct strict native rejection of `#1827` and `#1907`.

For authorized private originals:

```bash
export APMESH_ORIGINAL_CAD_DIR=/private/originals
export APMESH_S3V_PRIVATE_DIR=/private/s3w-bp
cd docs/research/nonmanifold-benchmark/probes
python -m unittest -q test_s3y_s40_curved_planar_rings
python s3y_s40_curved_planar_rings.py \
  --source-step "$APMESH_ORIGINAL_CAD_DIR/i25o_s40.step" \
  --baseline-bp "$APMESH_S3V_PRIVATE_DIR/s40_spline_shared_repair.partial.bp" \
  --baseline-manifest "$APMESH_S3V_PRIVATE_DIR/s40_spline_shared_repair_manifest.json" \
  --faces 3044 --interior-grid 17 --boundary-grid 31 \
  --output-dir /private/s3y/3044
```

**Scientific and production boundaries:** No execution of the real APMesh TRI/QUAD mesher, no C++ production regression, no 43/43 original atlas, no formal directed-rounding interval proof, and no genuine original industrial non-manifold positive is claimed. Keep research PR #225 draft; do not merge into `main` without additional advisor-defined scientific gates.
