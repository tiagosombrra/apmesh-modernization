# S3.P — Original S40 `ADVANCED_FACE #2457`: complementary source cylinder and split B-spline trim

**Date:** 2026-11-16. **Classification:** isolated scientific feasibility, research-only. The original production C++ mesh generator, historical frozen baselines, Stage 3, QUAD and main are not modified. The research PR #225 must remain draft pending advisor review and separate full scientific admission.

## Immutable industrial provenance

- Source repository: `cgg-bern/hex-me-if-you-can`, revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`.
- Original source path `original/i25o_s40.step`, original SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`; exact original raw bytes were admitted before native import.
- Source target: `ADVANCED_FACE #2457`, cylindrical source support `#1632`, original/native face index 22, radius 16 mm, one nine-edge outer wire, no inner hole. The original reference frame has the opposite X direction of the already represented `ADVANCED_FACE #1519`, native face index 12, on the **same physical cylinder axis**. Dot product of their X reference directions is exactly -1 within the source's decimal precision; their distinct native face centroids are approximately 20.957302498 mm apart. **Local UV intervals match, but their physical surface halves do not coincide.** The source and native boundary edges `#1616` and `#1753` belong to both faces.

## Nine original boundary identities — no coordinate welding

| Original source `EDGE_CURVE` | Original master curve | Source cylinder `PCURVE` | New Bézier boundary pieces |
| --- | --- | --- | ---: |
| `#2309` | 3D B-spline | degree-3 B-spline, 47 control points | 7 |
| `#2251` | 3D B-spline | degree-3 B-spline, 25 control points | 3 |
| `#1616` | axial line, shared with `#1519` | line | 1 |
| `#1911` | original circle arc | degree-1 B-spline | 1 |
| `#2434` | axial line | line | 1 |
| `#2096` | 3D B-spline | degree-3 B-spline, 47 control points | 8 |
| `#2407` | axial line | line | 1 |
| `#1886` | original circle arc | line | 1 |
| `#1753` | axial line, shared with `#1519` | line | 1 |

The original wire order and each original oriented endpoint pair are mandatory; nine distinct STEP edges match nine different native `TopoDS_Edge` identities with two-sided native incidence. Original boundary pieces account for all 24 singly owned UV rectangle sides. Every original curve is independently evaluated via its native 3D `BRepAdaptor_Curve` and its native 2D `BRepAdaptor_Curve2d`, inverting the monotone parametric trace for piecewise sampled comparisons. Unlike an ideal-cylinder-only distance test, this checks the original 3D B-spline boundaries.

## Trim decomposition and constrained controls

The nine original vertices define an orthogonal staircase in the source's local cylinder UV domain, with angular range approximately `pi..2*pi` and axial range `-16.5..16.5 mm`. The upper source B-spline is **split at original vertex #2252**, at approximately U=3.964626352 rad. The lower central tab spans approximately U=3.459416358..5.965361603 rad and axial V=-16.5..-10.5 mm. The upper band extends from V=-10.5 to 16.5 mm.

The original upper split vertex **is not removed or welded**. The pilot partitions the angular middle using two intervals over the left top-spline section and six over the right, plus the two outer strips. Both upper and lower bands use the same angular grid to maintain an indexed conforming network:

- Upper band: ten tensor-product polynomial bicubic patches.
- Lower central tab: eight tensor-product bicubic patches.
- Combined source `#2457`: **18 patches**, **24 new internal indexed seams**, no redundant or missing source UV area detected.
- Original source generatrices `#1616` and `#1753`: all four Bézier controls per edge retain **exactly the original global BP integer identities** from the already admitted `#1519` side. The total atlas has 77 patches and 864 distinct global controls, representing **16 of 43 original S40 source faces**. The other 27 source faces remain excluded.

The experimental error budget **0.001 mm** was fixed before angular partition selection. The alternative `(2,5)` sector partition is rejected by the Bernstein radial-support gate. The `(2,6)` configuration passes; no post hoc increase of the budget is permitted.

## Native Open CASCADE results on the original, byte-verified STEP

| Scientific pilot gate | Measured result |
| --- | ---: |
| Original source/natively imported target face | `#2457` / native face index 22 |
| Previous 59-patch atlas | Recomputed and SHA-checked before extension |
| Admitted new patches | **18** |
| Combined partial BP | **77 patches, 864 global control vertices** |
| Original STEP/native boundary edge bijection | **9 of 9** |
| Original 3D B-splines measured independently | **3 of 3** |
| Original shared seam edge IDs to `#1519` | `#1616`, `#1753`, all eight control references reused |
| Additional indexed internal seams | **24** |
| Native sampled interior UV classification | **1,458/1,458 IN** |
| Native sampled boundary UV classification | **792/792 IN or ON** |
| Maximum sampled original native boundary-curve distance | **0.0005142049726892852 mm** |
| Maximum sampled native cylinder projection distance | **0.0005142061576931257 mm** |
| Guarded numerical Bernstein radial-support bound | **0.0005142073031326918 mm** |
| Fixed experimental pilot budget | **0.001 mm** |

### Test and reproducibility evidence

**S3.P directed unit tests:** 16/16 PASS. **S3.M+S3.N+S3.O+S3.P directed research regression:** 61/61 PASS, with original byte-verified S40 STEP mounted locally. Negative controls reject wrong source SHA, changed baseline control registry, tampered BP and manifest, relaxed budgets, incorrect native boundary bijection and the insufficient sector count. The **full historical research suite and production C++ acceptance suite were not run in this checkpoint**.

Run in the research probe directory with CadQuery/OCP/NumPy installed, with the rights-cleared pinned S40 STEP outside the public repo and the private S3.O BP/manifest:

```bash
export APMESH_ORIGINAL_CAD_DIR=/external/s40-source
export APMESH_MAMBO_SOURCE_DIR=/external/s40-source
python -m unittest -q test_s3m_s40_complex_trim_inventory test_s3n_s40_orthogonal_trim test_s3o_s40_spline_trim test_s3p_s40_complement_spline
python s3p_s40_complement_spline.py \
  --source-step /external/s40-source/i25o_s40.step \
  --baseline-bp /private/s3o/private_bp/s40_spline1519.partial.bp \
  --baseline-manifest /private/s3o/private_bp/s40_spline1519_manifest.json \
  --left-sectors 2 --right-sectors 6 --budget-mm 0.001 \
  --output-dir /private/s3p-output
```

## Limitations and next gates

- The accepted evidence consists of original source identities, unique native B-Rep correspondences, same-index seams, sampled curve deviations, sampled trimmed UV membership and a guarded floating-point Bernstein support bound. The latter is **not a directed-rounding formal continuous certificate**. Neither global trimmed Hausdorff distance nor semantic APMesh BP acceptance has been established.
- Existing BP patches are partial and do not cover the remaining 27 source faces. In particular `ADVANCED_FACE #218` contains a genuine internal trim loop; **S3.Q must preserve that hole**, not replace it with a filled rectangle.
- No imported original 3+-incident multi-sheet non-manifold positive, complete shell BP atlas, approved original-source redistribution, accepted APMesh TRI/QUAD generation, or C++ production regression is implied.
- Do not commit original industrial STEP bytes, private derivative BP coordinates, or original CAD tessellations to public GitHub until redistribution rights are independently reviewed. Keep the private user research package separate.

**Research PR #225 remains draft, no merge to `main`.**
