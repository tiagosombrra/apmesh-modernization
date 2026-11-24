# S3.V — Original S40 source-indexed curved-planar closure candidate and strict trim blocker

**Date:** 2026-11-17. **Classification:** research-only feasibility, **NOT ADMITTED**. The APMesh C++ production generator, protected `main`, QUAD branch and TRI/QUAD meshing process were not modified or executed. Draft PR #225 remains the review boundary.

## Frozen original and previous atlas

- Third-party original: `cgg-bern/hex-me-if-you-can`, revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, `original/i25o_s40.step`, SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`.
- Previously admitted S3.T source-indexed BP SHA-256 `988d8ed29867927f736838dde20db9efb358c0ee04a202a4f4810ae0e23aa40d`: **132 patches, 1,527 declared controls, 189 indexed two-sided seams, 150 open indexed sides, 19 of 43 source faces represented**. The source hole in `ADVANCED_FACE #218` remains preserved.
- The original STEP was obtained through an authorized private research transfer and normalized to its **byte-exact pinned hash** before native import. The source STEP and all control coordinate derivatives are excluded from the public repository. A private candidate BP and local viewer are available only in the attached research package, pending redistribution-rights review.

## Why independently fitting new cubic curves would be wrong

Original planar faces `ADVANCED_FACE #17` and `#2092` each have exactly four original `EDGE_CURVE` entities and **four source-native face neighbors already represented in S3.T**. The two degree-five master 3D B-splines (`#85` and `#2096`) have already been approximated in the previously admitted cylindrical BP. Re-fitting those curves independently and welding merely by coordinate proximity would break the source-canonical global control identity.

The S3.V builder therefore inherits the exact **integer cubic control side IDs** from the pinned previous patches. Original source/native face correspondence covers 43 faces, 117 edges and 77 vertices. Source EDGE_CURVE owners and the previously frozen patch-side lineage are both validated; geometry is only a secondary consistency check.

| Proposed new original face | Native `TopoDS_Face` | Source edge IDs in oriented wire order | Existing cubic boundary segments | New planar cubic patches |
| --- | ---: | --- | --- | ---: |
| `#17` | 0 | `#21` circle, `#57` line, `#85` degree-five B-spline, `#193` line | **9 + 1 + 7 + 1 = 18** | 8 |
| `#2092` | 18 | `#2096` degree-five B-spline, `#2201` line, `#2042` circle, `#2223` line | **8 + 1 + 8 + 1 = 18** | 8 |

A deterministic dynamic-programming quadrangulation creates **eight convex quads per face** using only already indexed original boundary endpoints, with seven new internal diagonals per face. The original source-indexed exterior controls and the old 132 patch nets are unchanged. The patch interiors use planar cubic Coons construction with exactly indexed side controls.

The **unadmitted candidate** contains **148 patches, 1,619 global controls, 239 indexed two-sided seams and 114 open indexed sides**. Its BP SHA-256 is `ba18b866fd70d25b8b9b116354c2673c0294efc6dba8e1e7dca48e8d6536070d`.

The combinatorial polygonization uses chords of the indexed boundary end points; its approximate area is **482.30037718 mm²** for `#17` and **477.43984841 mm²** for `#2092`. These are **not** the true native trimmed face areas (approximately 488.65714528 and 488.65708886 mm²). Equality of *chord-polygon* area and quad area proves only that the chosen topological partition covers the chord polygon. It is not a continuous CAD trim coverage theorem.

## Independent original native BRep audit: strict rejection

| Original native gate | Observed result |
| --- | ---: |
| Original native faces targeted | 2 |
| Source/native original edges uniquely mapped | 8 |
| Candidate patch interior samples | **1,296 `IN`** |
| Boundary samples, total | 704 |
| Boundary samples `IN` or `ON` | **569** |
| Boundary samples `OUT` | **135 — FAIL** |
| `OUT` from original B-spline edge `#85` | **63** |
| `OUT` from original B-spline edge `#2096` | **72** |
| `OUT` from new internal diagonals | **0** |
| Samples against 8 original native `BRepAdaptor_Curve`s | **396** |
| Maximum sampled original edge deviation across all boundaries | **0.00089266861645 mm** |
| `#85` maximum sampled source-curve distance | **0.00068289305639 mm** |
| `#2096` maximum sampled source-curve distance | **0.00051413977639 mm** |
| Maximum sampled native plane support deviation | **1.04 × 10⁻¹² mm** |
| Fixed prior research pilot budget | **0.001 mm** |
| Strict original trimmed-face membership | **REJECTED** |
| New source faces admitted to atlas | **0** |

The source edge distances were evaluated independently against the original native curves by numerical nearest-parameter minimization. They are **sampled minimum-distance estimates**, not certified global Hausdorff bounds. `BRepClass_FaceClassifier` uses a fixed `1e-7`-parameter classification tolerance. The original degree-five B-spline approximations inherited from the S3.O and S3.P cylindrical surfaces cross the native face boundary by a small amount on the planar side. This explains why even an exactly indexed seam and a sub-0.001-mm geometric deviation are insufficient for this gate.

The previous `0.001 mm` pilot budget is **not relaxed after observing the `OUT` classifications**. We explicitly do not substitute a proximity-within-budget rule for the mandatory native trimmed-face membership criterion. The two new faces are **not admitted**, despite successful intermediate geometry/topology checks. The authoritative S3.T atlas remains **132 patches and 19/43 original faces**.

## Tests and evidence

- **30 S3.V original-source directed tests passed** with the byte-frozen STEP, original BP and private manifest. They include source/registry tampering, changed fixed budget, patch-side lineage, wrong source-edge owners, duplicate/missing sides, adversarial BP/receipt modification, preservation of old 132 patches and hole, and explicit failure to admit the candidate when native boundary samples are `OUT`.
- **45/45 S3.S–S3.T tests passed** and independently **55/55 S3.U–S3.V passed**, zero failures/skips in either run: **100 directed tests** over the four stages, using exact original STEP bytes. An attempted all-in-one S3.S–S3.V invocation exceeded its execution limit without a completed receipt; it is **not** represented as passing. Earlier S3.M–S3.R scientific evidence remains frozen from its separate checkpoints and was not rerun in this S3.V delivery.
- No production C++ regression, TRI or QUAD generation, true industrial 3+-incident source mesh case, complete S40 shell or formal directed-rounded error certificate is claimed.

## Next gated repair: S3.W

1. Inspect the exact original native `B_SPLINE_CURVE_WITH_KNOTS` and `PCURVE` parameter traces for source edges `#85` and `#2096`, and classify signed deviations on each source face side. Re-run their existing S3.O/S3.P native curve/UV tests as a baseline.
2. Seek **coordinated source-identity-indexed shared-boundary remediation**, not independent fitting: any control movement or subdivision must update both incident source patches with identical control IDs and propagate downstream conformity via the existing graph. Alternative numerical/tolerance policies require prior advisor agreement, not retrospective relabeling of rejected samples.
3. Before admission, require `IN/ON` for **all** native original boundary sample points on both planar and cylindrical sides, native edge-distance budget, valid patch orientation, full 132-patch prior-lineage audit including de Casteljau changes if used, and the original hole `#218` preserved.
4. Keep the failed candidate BP private and marked `CANDIDATE_NOT_ADMITTED`; do not count 148 patches as a verified atlas or merge PR #225.

### Reproduction

Use the attached private research ZIP with CadQuery 2.8 / OCP 7.9, NumPy, SciPy and Shapely 2.x. Supply the authorized pinned original outside public Git:

```bash
export APMESH_ORIGINAL_CAD_DIR=/authorized/originals
export APMESH_S3V_PRIVATE_DIR=/private/s3t-atlas
cd code
python -m unittest -v test_s3v_s40_curved_planar_closure
python s3v_s40_curved_planar_closure.py \
  --source-step "$APMESH_ORIGINAL_CAD_DIR/i25o_s40.step" \
  --baseline-bp "$APMESH_S3V_PRIVATE_DIR/s40_planar_octagons.partial.bp" \
  --baseline-manifest "$APMESH_S3V_PRIVATE_DIR/s40_planar_octagons_manifest.json" \
  --output-dir /private/s3v-candidate
```

**Disposition:** reproducible candidate geometry built and strictly blocked; previous admitted atlas unchanged. Stage 3 production and advisor-governed scientific admission remain separate.
