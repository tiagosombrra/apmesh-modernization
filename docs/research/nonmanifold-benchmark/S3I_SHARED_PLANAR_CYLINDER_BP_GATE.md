# S3.I — Source-identical shared planar/cylinder bicubic BP gate

**Date:** 2026-11-16. **Classification:** isolated scientific research, **not** production C++ code, Stage 3, QUAD integration, or an admitted original MAMBO CAD atlas.

## Research question

After S3.H proved approximate polynomial bicubic representations for constrained cylindrical source faces, can admitted STEP planar quads and their directly adjacent cylindrical faces share the **same exact integer BP control IDs** on original `EDGE_CURVE` generator boundaries, while both the original STEP and the newly imported OCCT `TopoDS` identities are rechecked?

**Bounded answer:** YES, on an author-constructed half-cylinder STEP imported into Open CASCADE 7.9/CadQuery 2.8. An independent check validates source/native face and edge identity, first-ring source `ADVANCED_FACE` IDs, original shared cubic control keys, native planar face distance, and sampled distance to the actual **trimmed** native cylindrical face. **Original M5/S40 native execution remains NOT RUN** because the original industrial STEP assets were not mountable in this runtime. No imported original M5 patches, complete CAD atlas, genuine external 3+-incident source, or APMesh TRI/QUAD output are claimed.

## Corrected source STEP PCURVE handling

Some OCCT STEP exporters represent the original generator's exact constant-U 2D straight line as a **nonperiodic, clamped, two-pole degree-one `B_SPLINE_CURVE_WITH_KNOTS`**, rather than `LINE`. The former S3.H parser rejected such valid source curves. The restricted S3.H probe now accepts either a constant-U `LINE` or this explicitly checked linear spline (degree one, two poles, knot multiplicities `(2,2)`, strictly increasing finite knot interval, nonperiodic, same U at poles, finite nonzero V span). Arbitrary nonlinear, rational, higher-degree, or non-clamped splines remain outside this gate. Adversarial checks reject a forged degree-two curve.

## Joint construction

`probes/s3i_joint_source_atlas.py` performs, in sequence:

1. Validate the original source raw SHA-256 before import. Known MAMBO models use frozen per-model digests; synthetic sources require explicit caller-provided hashes.
2. Recompute S3.E unique planar `ADVANCED_FACE` / `EDGE_CURVE` to `TopoDS` mappings, then S3.F exact original first-ring excluded-neighbor mappings and certificates. No geometry-proximity-based welding is used.
3. Degree-elevate eligible source-planar four-edge faces to indexed bilinear bicubic 4×4 control nets with **original** `VERTEX_POINT` and `EDGE_CURVE` canonical IDs. Audit the source-bound planar patches against actual imported native faces.
4. Construct original-identity-anchored S3.H cylinder patches from the same input STEP, subject to a prespecified sampled error budget, and independently verify their original source cylinder geometry and derived seams.
5. Intern both kinds of patch controls into a **single** BP vertex table keyed by `vertex:<STEP-ID>` and `edge:<STEP-ID>:1/2`. Validate **identical integer control indices** at every selected original plane/cylinder generator interface, including reversal of an original edge direction. Derived partition seams remain distinct from source edges.
6. Independently reparse BP data, recompute native source identities, and sample distances to the **actual native trimmed** planar and cylindrical faces. Reject a corrupted BP, forged source-to-native identity, or interior cylinder perturbation even when the BP checksum is recomputed. Only write research outputs after all required checks pass.

### Measured local synthetic native STEP

Source: author-generated, original research control: half-cylinder radius 3 mm and height 4 mm with a planar diametral quad, two additional planar end caps, and one trimmed cylindrical face. Byte-identical fixture SHA-256 in the local receipt: `bba9a7b0ff363a541aa4d5e696ad8bb368d40904d3445f0d25afc98ae9b170db`.

| Measurement | Actual result |
|---|---:|
| Original STEP `ADVANCED_FACE` count | 4 |
| Uniquely mapped native planar four-edge candidates | 1 |
| Original neighboring cylindrical source faces used | 1 |
| Source native first-ring excluded-neighbor faces mapped | 3 |
| Indexed planar bicubic patches | 1 |
| Indexed cylindrical bicubic patches | 6 |
| **Combined indexed BP patches** | **7** |
| **Unique global BP controls** | **84** |
| Original source generator `EDGE_CURVE` IDs reused by plane + cylinder | 2 |
| Original shared source boundary control indices verified | **8** |
| Maximum independently sampled native planar face distance | `8.042e-14 mm` |
| Maximum independently sampled native trimmed cylinder face distance | **`0.000584520 mm`** |
| Sampled native cylindrical distances (independent audit) | **726** |
| Prespecified absolute sampled cylinder budget | `0.001 mm` |
| Four-cylinder-segment negative control | **FAIL as expected** (outside budget) |
| Six-cylinder-segment control | **PASS in bounded sampled scope** |
| Complete original industrial STEP native admission | **NOT RUN** |
| Native cylindrical UV and PCURVE continuous trim certificate | **NOT CERTIFIED** |
| Accepted APMesh TRI/QUAD generation | **NOT RUN** |

The native closest-face metric is sampled and does not prove a continuous Hausdorff error bound or a globally watertight original industrial CAD atlas. The test shape is a **manifold control**, not a real non-manifold multi-sheet source.

## Reproduction and original-only conditional gate

From the repo root, with Python, CadQuery, OCP, NumPy:

```bash
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p 'test_*.py' -v
python docs/research/nonmanifold-benchmark/probes/s3i_joint_source_atlas.py \
  --source-step /external/synthetic_half_cylinder.step --model SYNTHETIC \
  --expected-sha256 <EXACT_SYNTHETIC_RAW_SHA256> \
  --cylinder-faces 17 --sectors 6 --sampled-budget-mm 0.001 \
  --output build/research-s3i/synthetic
```

The synthetic STEP generator is contained in `test_s3i_joint_source_atlas.py`. Since independently exported STEP bytes may differ, derive the exact digest from **the actual generated bytes**, and derive the correct face ID from the source-entity screen rather than relying on the example ID.

For M5, **only after acquiring the raw original source bytes from the pinned upstream revision outside Git**:

```bash
python docs/research/nonmanifold-benchmark/probes/s3i_joint_source_atlas.py \
  --source-step /external/mambo/sources/i05o_m5.step --model M5 \
  --cylinder-faces 3493 3976 --sectors 4 --sampled-budget-mm 0.001 \
  --output build/research-s3i/m5
```

This command is a **conditional, NOT RUN original-input gate** in the current execution. The exact source SHA-256 is pinned and validated by the code; upstream original STEP bytes are not stored in the branch or redistributable package. If all gates pass, it would produce six source-planar patches plus eight cylindrical patches, still only **eight of M5's 41 source CAD faces** and a total of 14 partial BP patches. Its original-cylinder native face geometric errors and first-ring correspondences must be reported, not assumed.

## Test receipt and closure status

Full local research probe suite: **133 tests, 126 PASS, 7 SKIP, 0 FAIL**. S3.I contributes 18 discovered directed cases (17 PASS, one explicit M5 original-input SKIP). The remaining skips belong to previous original-asset gates. Tamper controls cover a source SHA mismatch, rehashed interior control deformation, forged source feature control keys, forged native face indices, changed B-spline degree, duplicate source cylinder identity, excessive sector error, and a fail-closed CLI.

The actual research branch's **final remote exact-head** full test suite, the C++ production regression and accepted APMesh mesh outputs were **NOT RUN** in this Python container. Keep PR #225 draft and do not merge until code/test/scientific closure gates pass on the actual head, and advisors approve the scientific scope.

**Next S3.J decision:** prioritize obtaining and byte-verifying the real M5/S40 STEP files into the execution environment. Run the S3.E/S3.F/S3.G/S3.H/S3.I native oracles on M5 `#3493/#3976` and independently identify any source/native ambiguity, UV trim discrepancy, global control incompatibility and actual per-patch native-distance failures. Only then expand trimmed S40 decomposition and discuss APMesh TRI/QUAD benchmark admission.
