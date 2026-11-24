# S3.Z.3 — Exact-rational Bernstein gate for shared circular-seam trials

**Checkpoint:** 2026-11-18. **Scope:** research-only numerical strengthening, hermetic tests. No STEP-native original CAD trial, no new admitted source face, no modification to the APMesh production C++ generator, and no original industrial 3+-incident nonmanifold positive.

## Frozen original S40 research state

The accepted **S3.Y** partial atlas remains **156 bicubic Bézier patches / 1,665 declared global controls / 264 two-sided indexed seams / 96 open indexed sides / 22 of 43 original STEP faces represented**. The approved source face `#3044` is unchanged. Faces `#1827` and `#1907` are still blocked. The previous candidate's 18 `OUT` source-trim samples per face are **historical S3.Y evidence, not a fresh S3.Z.3 native measurement**.

The fixed upstream model SHA-256 is `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`, from `cgg-bern/hex-me-if-you-can`, revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, `original/i25o_s40.step`. Private S3.W parent BP SHA-256 is `c826487d8cee76f6649100c59e5ce84fa6cb43c9004f53c68e3e565e86cdb174`, and S3.Y accepted child SHA-256 is `af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177`.

## New mathematical check

The previous S3.Z.2 original-native trial plan used a **floating-point-guarded Bernstein** estimate of radial deviation for each modified cylindrical bicubic patch. Its known narrow margin warrants a second, independent numerical gate. The new module `s3zc_exact_bernstein_radial_gate.py` evaluates the *same analytic bicubic control net*, **exactly over the IEEE-754 input numbers treated as rationals**.

For bicubic surface `P(u,v)`, cylinder axis point `O`, nonzero direction vector `D` (not assumed to have exactly unit binary norm), and radius `R`, evaluate

`Q(u,v) = ||P(u,v)-O||² - ((P(u,v)-O)·D)² / (D·D)`.

It is a polynomial with bi-degree `(6,6)`. Every input float is represented exactly by `fractions.Fraction.from_float`, and every coefficient of the tensor-product Bernstein net is computed with exact rational arithmetic. The degree-three polynomial product identity uses `C(3,i)C(3,j)/C(6,i+j)` in each parameter dimension. Exact de Casteljau midpoint subdivision yields rational Bernstein coefficient hulls over each subrectangle.

The **unmodified 0.001-mm experimental budget** is enforced with rational squared bounds:

`(R - 0.001)² <= Q(u,v) <= (R + 0.001)²`, for `R >= 0.001`.

If all coefficient hulls satisfy both inequalities, the algorithm certifies the radial envelope **for the float-defined analytic surface and cylinder**, throughout the parameter domain. If a subrectangle's entire hull lies outside, the procedure rejects. If the maximum depth (16) or processing resource limit (8,192 nodes) is exhausted while uncertain, it returns **INCONCLUSIVE** and blocks admission. There is no retrospective budget relaxation. The old floating-point-guarded test remains required **as an additional independent check**; the new exact test is a mandatory second check for each of the eight source-indexed circular-neighbor cylinder patches in the trial loop.

**Scope limitation:** exact rational calculations do **not** account for upstream STEP-to-OCP conversion uncertainty, a different CAD representation, error in native trim parameters, exact original source spline distance, Hausdorff distance to the full CAD shell, or a full trim-domain coverage theorem. Therefore the result is *not* a formal certificate of the original STEP CAD, even when this exact float-input gate passes. Native sidedness and original edge tests remain separate mandatory gates.

## Test and runtime evidence

- **83/83 hermetic tests PASS**, 0 fails, 0 skips: the previous 55 S3.Z/S3.Z.1/S3.Z.2 contracts plus **28 new S3.Z.3 tests**. Tests include exact numeric representation, independent OCP `gp_Cylinder` extraction, scaled-axis and translated-axis invariance, exact evaluation of the squared-radius polynomial at rational parameters, exact midpoint subdivision, in-budget/out-of-budget synthetic patches, deliberately narrow margin, non-finite/invalid controls and bounded-resource inconclusive behavior.
- All relevant Python modules compile successfully. Unit tests exercise an actual OCP `gp_Cylinder` synthetic primitive, but **do not** import the industrial original S40 `TopoDS_Face`.
- The input-readiness process returns **`BLOCKED_MISSING_OR_MISMATCHED_INPUT`** (exit code 3): the original STEP, private S3.W BP, private manifest and S3.Y public builder are not currently present in the runtime. CadQuery/OCP/NumPy/SciPy/Shapely are installed, but the lack of geometric source bytes prevents running any of the eight S3.Z control-displacement trials.
- **New original faces admitted: 0.** No candidate BP coordinates are generated or publicly committed. The S3.Y 156-patch child remains the accepted *bounded research pilot*.

## Private reproduction

The delivery ZIP contains the updated `s3z_s40_circular_seam_gate.py`, the new exact-rational module, all hermetic tests and the unchanged readiness checker. The published S3.Y builder and earlier probes must be on `PYTHONPATH` along with the package, and the original authorized STEP/BP must be made available privately.

```bash
python -m unittest -v \
  test_s3z_s40_circular_seam_gate \
  test_s3za_topology_scope \
  test_s3zb_oriented_seam_and_coons_gate \
  test_s3zb_private_readiness \
  test_s3zc_exact_bernstein_radial_gate

python s3zb_check_private_readiness.py \
  --original-step /private/original/i25o_s40.step \
  --s3w-bp /private/s3w/s40_spline_shared_repair.partial.bp \
  --s3w-manifest /private/s3w/s40_spline_shared_repair_manifest.json \
  --s3y-builder /private/research/s3y_s40_curved_planar_rings.py \
  --output /private/s3z3/readiness.json

# Execute only when the readiness receipt is READY_FOR_ORIGINAL_NATIVE_TRIAL.
python s3z_s40_circular_seam_gate.py \
  --original-step /private/original/i25o_s40.step \
  --s3w-bp /private/s3w/s40_spline_shared_repair.partial.bp \
  --s3w-manifest /private/s3w/s40_spline_shared_repair_manifest.json \
  --output /private/s3z3/native_trials.json
```

## Decision and next task

The new method is **accepted as a tested numerical gate, not as source-native S40 evidence**. Once the private inputs are attached, re-run all eight source-canonical circular-seam repair candidates, apply both full bicubic radial checks, retest native plane and cylinder trim membership, sample original circle `EDGE_CURVE`s, verify global indexing, Coons interiors, orientation, preservation of source hole `#218` and accepted face `#3044`, then independently audit any proposed new BP. No APMesh TRI/QUAD production result or protected-branch merge follows from these checks.
