# S3.J — Guarded numerical Bernstein radial enclosure for partial CAD cylinder patches

**Classification:** isolated scientific research, not a production C++ change. **Date:** 2026-11-16.

## Scientific question

The previous S3.H/S3.I accepted a candidate polynomial bicubic cylinder fit under a declared *sampled* distance budget. A finite sample cannot bound the maximum between samples. Can a second, independently computed **continuous-parameter numeric enclosure** bound the radial deviation of these specially constructed, axially separable cubic cylinders without claiming an OCCT trimmed-face certificate?

**Bounded answer:** yes on the authored half-cylinder research control, provided every bicubic patch has constant radial controls along axial parameter rows, a linear axial component, all radial controls in the original source angular wedge, nonzero radius throughout, and its squared radial distance is processed as a degree-six polynomial in the Bernstein basis. The result is a *floating-point convex-hull enclosure plus declared numerical margin*, **not formally proven using directed-rounding interval arithmetic**. This does not certify the native CAD trim, original M5 import, a complete atlas, an external nonmanifold original or generated APMesh meshes.

## Mathematics and proof boundary

Let the planar radial cubic control vectors be \(P_0,\ldots,P_3\), expressed in the original source cylinder's orthonormal radial frame. Then

\[
C(t)=\sum_{i=0}^3 B_i^3(t)P_i, \qquad q(t)=\|C(t)\|^2-R^2=\sum_{k=0}^6 B_k^6(t)q_k,
\]

where

\[
q_k=\sum_{i+j=k}\frac{\binom{3}{i}\binom{3}{j}}{\binom{6}{k}}(P_i\cdot P_j)-R^2.
\]

By the convex-hull property, the exact polynomial \(q(t)\) lies between the minimum and maximum Bernstein coefficients on every subinterval. De Casteljau splits at \(t=1/2\) refine this interval without sampling the surface. When the lower radius remains positive, the extreme of \(|\sqrt{R^2+q}-R|\) on the computed coefficient interval is an upper bound for the exact polynomial radial deviation. The whole bicubic patch follows from axial separability and the convex-hull bound on nonseparable control residuals. A convex angular wedge (each patch at most 90 degrees) bounds directions of the radial cubic, but **does not establish a mapped trimmed OCCT face**.

All operations here are in binary floating point. A default **1e-9 mm heuristic margin** and the measured maximum nonseparable control residual are added before applying the predeclared budget. This protects against modest roundoff in the tests but is **not a proof of numerical interval containment under every floating-point platform**. A future stronger certificate needs directed-rounding/interval arithmetic and a native p-curve/trim-domain oracle.

## Reproduced local result

Input: author-generated half-cylinder STEP from the S3.I research package, radius 3 mm, axial height 4 mm, six cylindrical bicubic patches plus one exact planar patch. Its original source SHA-256 is checked by the runner. The new audit reads the existing original STEP source, indexed BP and S3.I manifest and **recomputes** the source geometry and individual patch bounds.

- Six cubic cylinder patches independently analyzed: **PASS** under the existing predeclared 0.001-mm pilot budget.
- Maximum guarded radial-support bound: approximately **0.000584520795 mm** (includes 1e-9-mm margin).
- Previous maximum independently sampled native trimmed cylinder distance: approximately **0.000584519795 mm**; the numerical-bound and native-distance quantities are *different metrics*.
- Negative controls check axial deformation, radial row deformation, wedge violation, original SHA mismatch, mismatched control IDs, duplicate face receipts and rehashed modified BP geometry.
- Original M5/S40 **native STEP import and source/native face identity correspondence are NOT RUN** in this environment, since pinned original STEP files were not mounted and direct container network resolution failed.

## Commands

From the research probe directory, with CadQuery, OCP and NumPy installed and the prior S3.I scripts on `PYTHONPATH`:

```sh
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p 'test_*.py' -v
python docs/research/nonmanifold-benchmark/probes/s3j_radial_support_enclosure.py \
  --step /external/author_half_cylinder.step \
  --bp /external/source_joint.partial.bp \
  --manifest /external/source_joint_manifest.json \
  --model SYNTHETIC --expected-sha256 EXACT_GENERATED_SOURCE_HASH \
  --budget-mm 0.001 --depth 8 --guard-mm 0.000000001 \
  --output build/research-s3j/synthetic_radial_enclosure.json
```

The runner requires the independently predeclared `--budget-mm` to match each manifest budget, preventing rehashed metadata from silently widening the threshold. It writes a success receipt only when the recomputed bound is within that declared budget; missing or mismatched source files and invalid geometry fail closed. The original M5 conditional gate, pending byte-identical source acquisition and S3.I native import, uses `--model M5` and does not accept a caller-selected alternative source digest.

## Admission gate and next action

**S3.J research control is measured. Original industrial native admission is still BLOCKED.** An analytic cylinder-support envelope must never be called a complete source-native trimming certificate. The concrete next steps are (1) acquire pinned M5/S40 original bytes externally and verify raw SHA-256, (2) run S3.E/S3.F/S3.I source/native mapping, (3) verify all source original p-curves and the native face's true UV region, (4) recompute the support enclosure on the **actual** joint BP and test exact source-boundary control identities, and (5) separately execute and independently validate admitted APMesh TRI before later QUAD comparisons. PR #225 remains draft and must not merge until source/native and production closure gates pass.

## Independent source-original M5 radial interval receipt

A separate connected-GitHub analysis re-read the **actual original STEP source text** at `cgg-bern/hex-me-if-you-can@8f00f02579037cc893042f2ee2c910b20e3fb1b0`, file `original/i05o_m5.step` (Git blob SHA-1 `d72e5e3cb3de9ebdec80253cfa9b57fa1b7132f7`). It recovered the two directed circular arcs through their original `ADVANCED_FACE`, `EDGE_LOOP`, `ORIENTED_EDGE`, `EDGE_CURVE`, `CIRCLE` and circle-axis-frame identities. Both source faces `#3493` and `#3976` show radius 2 mm and 2.102093169774461 rad angular span. This source-side independent calculation applies the same degree-six Bernstein polynomial enclosure to idealized cubic-Hermite angular controls at 8 subdivision levels; original M5 bytes were **not transferred into the native OCCT runtime** and the raw SHA-256 was **not recomputed in this GitHub connector calculation**.

| Angular sectors/face | Guarded upper bound (mm) | Predeclared pilot budget (mm) | Result for analytic source cylinder support |
|---:|---:|---:|---|
| 2 | 0.006239878152 | 0.001 | FAIL |
| 4 | 0.000395428370 | 0.001 | PASS |
| 6 | 0.000078310235 | 0.001 | PASS |

Both source faces have the same upper values because their radius and absolute angle agree. **This is a numerical bound for idealized cubic sectors on the original analytic support, not a tested bound for a newly created, original-imported M5 BP**. The independent upstream source identity and the detailed coefficients are recorded in [the machine-readable S3.J M5 source receipt](evidence/s3j/original_m5_bernstein_reference.json). A weaker sampled native trimmed-face distance from an author-generated *synthetic* cylinder must not be conflated with this original-source support bound.

## Executed local closure checks

The combined Python research test suite was run from the S3.I ZIP reference plus S3.J code in the local container: **151 tests discovered, 143 PASS, 8 SKIP, 0 FAIL**. The 18 new S3.J cases give 17 PASS and one original-input SKIP. All research Python scripts also passed `compileall`. The baseline reference alone gave 133 tests, 126 PASS and 7 SKIP. This is a run against the local code and has **not** been repeated against the final remote Git commit. Production C++ and frozen scientific three-model regression were NOT RUN.
