# S3.X — Original industrial S40: post-repair gap census and narrow-margin native audit

**Date:** 2026-11-17. **Classification:** isolated doctoral research, not a C++ APMesh production change or a closed CAD/mesh result. The research PR #225 stays draft; protected `main`, QUAD and TRI execution are out of scope.

## Immutable original and prior Bézier artifacts

- Original third-party source: `cgg-bern/hex-me-if-you-can`, frozen revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, `original/i25o_s40.step`; SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`.
- Original S3.T 132-patch parent BP SHA-256: `988d8ed29867927f736838dde20db9efb358c0ee04a202a4f4810ae0e23aa40d`.
- Separate original S3.W repaired child BP SHA-256: `c826487d8cee76f6649100c59e5ce84fa6cb43c9004f53c68e3e565e86cdb174`.
- Original S3.R ancestor BP SHA-256: `98ff4cbfad08ce3f587607fddf3bb5e1a3697e1513a8ca86889bb28406e4028d`.
- The S3.W child contains **148 source-indexed bicubic patches, 1,619 declared control points, 239 exactly two-sided indexed seams and 114 open indexed sides**, representing **21 of the 43** original source faces within its bounded experimental admission. Exactly 30 shared control coordinates were changed on 15 previous cylinder patches; no original hole controls were changed.

## Recomputed original STEP ↔ native BRep topology

The source-native bijection is recomputed, not inferred from the displayed CAD tessellation: **43 original/native faces, 117 original/native edges, 77 original/native vertices**. All original `EDGE_CURVE` incidence is matched. The 22 source faces absent from the research BP are individually identified, with the following support types:

| Support | Remaining original source faces |
| --- | ---: |
| `PLANE` | 13 |
| `CYLINDRICAL_SURFACE` | 6 |
| `B_SPLINE_SURFACE_WITH_KNOTS` | 2 |
| Rational B-spline surface | 1 |
| **Total** | **22** |

Of the 22 pending faces, **16 are one original STEP edge away from an admitted face** and 6 are two original edges away. No original source edge has 3+ incident faces. **S40 is a manifold benchmark control, not a positive original non-manifold test.** No new BP patch is generated in S3.X.

### Next bounded source-native conversion: S3.Y

Three original planar faces are particularly connected. Each has one six-edge outer wire and all **six original `EDGE_CURVE` objects shared with the admitted atlas**:

| Original `ADVANCED_FACE` | Original edge composition | Already represented neighbors / edges | Decision |
| --- | --- | ---: | --- |
| `#1827` | 4 original CIRCLE + 2 LINE | 6/6 | Next source-indexed six-side closure candidate |
| `#1907` | 4 original CIRCLE + 2 LINE | 6/6 | Next source-indexed six-side closure candidate |
| `#3044` | 4 original CIRCLE + 2 LINE | 6/6 | Next source-indexed six-side closure candidate |

The original source IDs and native incidences are matched but **the exact BP cubic side segmentation, native trimmed-plane inclusion, polygon coverage and possible de Casteljau propagation are not yet certified** for these faces. Six original shared STEP edges do not imply that one bicubic patch can cover the hexagonal source region. The independent alternative `#1279/#1386` has six edges, only two circular edges each and three already represented source edges each. Remaining five-edge candidates `#3269/#3485` still require conforming subdivision before any all-quad partition, by boundary parity.

## Independent stress test of the narrow S3.W spline-envelope margin

The repaired original source B-splines `EDGE_CURVE #85` (seven cubic pieces, source plane `#17` ↔ cylinder `#1519`) and `#2096` (eight pieces, source plane `#2092` ↔ cylinder `#2457`) were *rechecked* against BOTH original trimmed native owners. New denser fixed-parameter sampling:

| S3.X native check | Actual result |
| --- | ---: |
| Cubic boundary samples: 129 nodes × 15 segments | **1,935**, all `IN` or `ON` on original native planar faces |
| Same 1,935 boundary samples on original native cylindrical faces | **1,935**, all `IN` or `ON` |
| Interior stress samples on 15 geometrically changed previous cylinders | **3,375**, all `IN` or `ON` |
| Maximum sampled cylinder radial distance | **0.000682866290 mm** |
| Maximum float-guarded full-bicubic (6,6) Bernstein radial upper estimate | **0.000980523954105 mm** |
| Unchanged experimental radial budget | **0.001000000000000 mm** |
| **Remaining numerical margin** | **0.000019476045895 mm** (approx. 19.48 nm) |

All 15 modified original cylinder patch nets were re-evaluated against the original native `BRepAdaptor_Surface` and the same bivariate radial enclosure routine, with the existing heuristic floating guard. This is denser **finite sampling** and a **floating-point Bernstein numerical estimate** only: the margin is small and is **not** an outward-directed interval-rounding certificate, a global exact Hausdorff bound for all trimmed faces, or a proof of complete coverage. The source-derived control points are deliberately excluded from the public receipt.

## Reproducible directed validation and negative controls

- New S3.X tests: **23/23 PASS**: original and three ancestor BP hash gates, unique source-native topology, 21/22 partition, face-type and adjacency histograms, six-sided candidates, true source manifold control, revised spline sidedness, bivariate Bernstein slack and no false formal-proof/meshing claims, tampered STEP/BP/manifest, altered budget, wrong BRep and invalid sampling grids.
- Directed regressions completed separately against the pinned original source: **70/70 S3.S–S3.U**, **30/30 S3.V**, **36/36 S3.W**, **23/23 S3.X**. **159/159 executed across four bounded invocations, 0 fail, 0 skip**. The single combined process exceeded its configured execution timeout and is not reported as green.
- Full original S3.A–S3.R historical regression, production C++ checks and actual APMesh TRI/QUAD generation were not rerun for this S3.X checkpoint. The published S3.W and earlier bounded research evidence remain separate.
- Closure decision: **accept S3.X as a bounded native *audit* and next-candidate selection only**. No source face is newly admitted, no original model is claimed closed and no merge to `main` is authorized.

### Reproduction with the authorized original retained privately

```bash
export APMESH_ORIGINAL_CAD_DIR=/private/verified-originals
export APMESH_S3V_PRIVATE_DIR=/private/previous-stage-bp
export PYTHONPATH=docs/research/nonmanifold-benchmark/probes
python -m unittest -q test_s3x_s40_post_repair_risk_audit
python docs/research/nonmanifold-benchmark/probes/s3x_s40_post_repair_risk_audit.py \
  --source-step "$APMESH_ORIGINAL_CAD_DIR/i25o_s40.step" \
  --private-bp "$APMESH_S3V_PRIVATE_DIR" \
  --segment-grid 129 --interior-grid 15 \
  --output-dir /private/audit-s3x
```

The authorized original STEP and its original-derived BP must remain outside public GitHub until redistribution rights are reviewed. The user-visible private research ZIP does **not** include the STEP bytes; visual CAD tessellation is for inspection, not APMesh TRI/QUAD evidence.
