# S3.U — Source-native post-octagon gap census for original industrial S40

**Date:** 2026-11-17. **Status:** bounded scientific feasibility evidence, research-only. No production C++ or QUAD changes, no new Bézier patch admission, no merge to main. Research branch `research/benchmark-corpus-reverse-patches`, draft PR #225.

## Original CAD and frozen atlas

- Upstream source: `cgg-bern/hex-me-if-you-can`, revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, original `i25o_s40.step`; raw SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`.
- Required native baseline: Open CASCADE/CadQuery import, **43** source/native faces, **117** source/native edges and **77** source/native vertices, independently correlated with source incidence disambiguation.
- Prior S3.T BP SHA-256 `988d8ed29867927f736838dde20db9efb358c0ee04a202a4f4810ae0e23aa40d`: **132 patches**, **1,527 declared controls**, **189** two-sided indexed seams, **150** open indexed sides, **19/43** original faces represented. S3.R 126-patch parent SHA-256 `98ff4cbfad08ce3f587607fddf3bb5e1a3697e1513a8ca86889bb28406e4028d` is verified and its original point and patch-index prefix preserved exactly in S3.T. Source hole `#218` remains preserved by this frozen lineage.
- This checkpoint **does not generate patches** or assume that all native CAD faces have yet been converted. Original third-party STEP bytes and original-derived BP control coordinates are **not committed to the public repository** pending redistribution-rights review.

## Complete remaining source face and connectivity audit

All source `ADVANCED_FACE` entities were independently matched one-to-one to native `TopoDS_Face`; original `EDGE_CURVE` and `VERTEX_POINT` bijections were recomputed and each original trimmed-wire edge count checked against native B-Rep.

| Metric | S3.S (after S3.R) | S3.U (after S3.T) |
| --- | ---: | ---: |
| Original S40 faces already represented | 17 | **19** |
| Original S40 faces still pending | 26 | **24** |
| Pending faces with direct original STEP edge incidence into atlas | 15 | **18** |
| Pending faces two source-edge hops from atlas | 11 | **6** |
| Admitted original source patches | 126 | **132** |

The **24 pending faces** classify as **15 planar**, **6 cylindrical**, **2 non-rational B-spline surfaces**, and **1 rational B-spline surface**. No original STEP edge has three or more distinct incident faces: S40 is still a **manifold control**, not a genuine non-manifold positive. This result is based on source `EDGE_CURVE` identity, not on near-coincident coordinates.

## Next source-identified admission candidates

| `ADVANCED_FACE` | Native index | Source boundary | Already represented neighbors | Decision |
| --- | ---: | --- | ---: | --- |
| `#17` | 0 | 4 edges: 2 LINE, 1 CIRCLE, 1 degree-5 3D B-spline (`#85`) | 4/4 | S3.V candidate; cubic approximation + exact indexed-seam gate required |
| `#2092` | 18 | 4 edges: 2 LINE, 1 CIRCLE, 1 degree-5 3D B-spline (`#2096`) | 4/4 | S3.V candidate; independent native original B-spline error check required |
| `#1279` | 9 | 6 edges: 4 LINE, 2 CIRCLE | 3/6 | Analytic-circle alternative with quad partition and edge controls |
| `#1386` | 10 | 6 edges: 4 LINE, 2 CIRCLE | 3/6 | Analytic-circle alternative with quad partition and edge controls |
| `#3269` | 35 | 5 LINE edges | 1/5 | Boundary subdivision required for an all-quad conforming disk |
| `#3485` | 38 | 5 LINE edges | 1/5 | Boundary subdivision required for an all-quad conforming disk |

For a simply connected planar region quadrangulated without hanging boundary nodes, **the boundary edge count must be even**, since every quadrilateral contributes four incidences and each interior edge is counted twice. Therefore `#3269` and `#3485` cannot be converted into conforming quadrilateral faces while leaving all five boundary segments unsplit. An additional original-edge subdivision propagated to neighbors, or an appropriate vertex-insertion strategy, is required. This parity condition is necessary, not sufficient for the existence of a quality quadrangulation.

### Direct native original B-spline support screening

For the *original* degree-5 native B-spline boundary curves (33 equally spaced native-parameter samples per edge), the maximum distances from their parent original `PLANE` supports were:

- `#17`, source `EDGE_CURVE #85`: **3.987032926033862 × 10^-12 mm**.
- `#2092`, source `EDGE_CURVE #2096`: **3.299671647027935 × 10^-11 mm**.

These are sampled **original-curve-to-plane** deviations. They **do not bound** any newly fitted cubic Bézier curve, do **not** establish curve-to-curve approximation, and do **not** prove that the 132-patch atlas can accept these edges with matching global control IDs. The original degree-5 B-spline should not be replaced by a straight segment or treated as a degree-3 polynomial without evidence. The frozen pilot budget is 0.001 mm, not an adviser-approved final tolerance.

## S3.V implementation gate

1. Reconstruct the original `#17` and `#2092` boundary orientations and their respective original native `BRepAdaptor_Curve` / `PCURVE` parameterizations. Preserve **all four original STEP edge identities**, which already belong to other represented source faces.
2. Adaptively approximate degree-5 3D B-spline and circular boundaries by compatible cubic segments under the **predeclared** 0.001-mm pilot budget. Verify error against native source curves, not just supporting planes, with independent dense sampling and a conservative numerical upper bound when available.
3. Resolve any existing BP boundary subdivision conflicts by exact integer control-lineage propagation; never weld coordinates by proximity or claim seamless joining based on a near-zero geometric gap.
4. Require non-overlapping patch UV coverage within the **trimmed native face**, correct outward orientation, exact two-sided indexed seams, preserved #218 inner hole and unchanged older control nets except for certified de Casteljau reparameterization.
5. Report the failure cases separately. No admission to the source atlas and no change to the original 132-patch baseline unless every gate passes. The original external genuine 3+-sheet non-manifold example and APMesh TRI/QUAD production regression remain independent open obligations.

## Validation boundary

- New S3.U source-native tests: **25/25 passed** with the byte-frozen original S40.
- S3.S–S3.U complete directed selection: **70/70 passed**, zero skip/fail.
- Independent S3.M–S3.R selection: **128/128 passed**, zero skip/fail.
- An initial one-shot S3.M–S3.U invocation did not terminate within the configured execution limit and is **not** claimed as an all-in-one green run. Subsequent two independently executed, disjoint selections cover **198 directed test cases**, both green. The separate S3.A–S3.L legacy suite and production C++ suites were not rerun.
- Tests include forged STEP hashes, S3.T / S3.R BP modification, manifest and budget alteration, incorrect native shape, false source-edge lineage, and forged receipt hashes including rehashed altered reports.

### Reproduction (authorized original source, kept outside public repo)

Use CadQuery 2.8/OCP 7.9, NumPy and Shapely 2.x with the supplied original source and S3.T/S3.R private BP artifacts:

```bash
export APMESH_ORIGINAL_CAD_DIR=/path/to/licensed/originals
export APMESH_S3T_PRIVATE_DIR=/path/to/private_bp
cd docs/research/nonmanifold-benchmark/probes
python -m unittest -v test_s3u_s40_post_octagon_gap_census
python s3u_s40_post_octagon_gap_census.py \
  --source-step "$APMESH_ORIGINAL_CAD_DIR/i25o_s40.step" \
  --baseline-bp "$APMESH_S3T_PRIVATE_DIR/s40_planar_octagons.partial.bp" \
  --baseline-manifest "$APMESH_S3T_PRIVATE_DIR/s40_planar_octagons_manifest.json" \
  --s3r-bp "$APMESH_S3T_PRIVATE_DIR/s40_218_conforming.partial.bp" \
  --s3r-manifest "$APMESH_S3T_PRIVATE_DIR/s40_218_conforming_manifest.json" \
  --output /private/research/s3u/original_s40_gap_census.json
```

The repository may retain the first-party script/tests, this document, and a non-geometric receipt only. An offline native-CAD tessellation viewer and the inherited private BP are for private evaluation, not source redistribution or proof of APMesh TRI/QUAD meshing.
