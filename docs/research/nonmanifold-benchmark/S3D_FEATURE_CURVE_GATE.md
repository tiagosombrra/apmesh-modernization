# S3.D — Canonical original CAD feature curves before curved-surface fitting

**Scope:** independent research subsystem; no production C++ algorithm changes, no original STEP redistribution, no accepted APMesh mesh, and no externally admitted 3+-sheet source complex. Date: 2026-11-16. Source originals: `cgg-bern/hex-me-if-you-can`, pinned Git revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`.

## Original source results

A direct, connector-backed traversal of four unchanged original STEP entity texts associated original candidate four-sided planar `ADVANCED_FACE` entities, their `EDGE_CURVE` entities, canonical topological vertices, and the excluded neighboring face. The original entity reference remains the identity; coincident but distinct curves were NOT welded.

| Model | Candidate-to-excluded source edges | Excluded planar neighbor | Excluded cylindrical neighbor | Distinct source vertex IDs within those interfaces | Global canonical control records | Maximum endpoint-to-master-LINE residual (mm) |
|---|---:|---:|---:|---:|---:|---:|
| M5 | 20 | 16 | 4 | 20 | 60 | 1.848491343065882e-12 |
| S40 | 32 | 20 | 12 | 32 | 96 | 5.049636154402834e-10 |
| S27 | 60 | 52 | 8 | 56 | 176 | 2.8929456704065194e-10 |
| M3 | 40 | 20 | 20 | 40 | 120 | 2.3366190032970214e-11 |
| **Total** | **152** | **108** | **44** | **148 model-local IDs** | **452** | — |

**All 152 interface source master curves are `LINE`**. This allows an exact cubic degree elevation of each individual straight source segment, independently of whether its excluded neighboring surface can be represented by a four-sided bicubic patch. For endpoints \(A,B\), canonical cubic controls are \(P_i=(1-i/3)A+(i/3)B\), \(i=0,1,2,3\). Bernstein degree elevation gives \(C(t)=(1-t)A+tB\) exactly in real arithmetic. Finite STEP coordinate/line definitions and floating-point evaluation have independently measured residuals, not a continuous global CAD-to-patch surface certificate.

The direct STEP checker evaluated seven de Casteljau sample parameters for each source edge. Maximum parameter-matched line-to-cubic residuals were 1.831e-15 mm (M5), 1.465e-14 mm (S40), 1.589e-14 mm (S27), 7.944e-15 mm (M3). These values are limited source-entity numerical oracles, not native OCCT imported-edge checks. The most restrictive source endpoint-to-master-line discrepancy measured was ~5.05e-10 mm in S40.

## Controlled construction code

The isolated `probes/s3d_canonical_feature_curves.py` builds a research JSON feature-curve sidecar for an acquired, pinned raw STEP input. Each original vertex entity has one global endpoint control record; each original EDGE_CURVE has two dedicated internal controls, preserving source topological identities. Source face use directions are tracked and a reversed local side references the same four global controls in reverse order. No output is called a BP patch because individual boundary curves alone do not satisfy the 16-control surface grammar.

`audit()` verifies a sidecar checksum, exact source interface ownership and edge identity, shared source vertex control indices, directed side IDs and independently evaluated de Casteljau point-to-segment distances against the master source line. It shares the STEP *entity parser* with the builder; this is a separate numeric and identity audit, not a wholly independent topology parser or native CAD cross-check.

### Reproduction

From repository root (requires the same S3.C Python support modules), with separately acquired and SHA-256-pinned original files in `/external/mambo/sources`:

```sh
python docs/research/nonmanifold-benchmark/probes/s3d_canonical_feature_curves.py --model M5 --sources /external/mambo/sources --output build/research-s3d/m5_feature_curves.json
python docs/research/nonmanifold-benchmark/probes/s3d_canonical_feature_curves.py --model S40 --sources /external/mambo/sources --output build/research-s3d/s40_feature_curves.json
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p 'test_s3d_*.py' -v
```

No original STEP bytes were available as local files during this delivery, so these original-model *Python* construction commands were **NOT RUN**. The original-source quantitative audit above was executed separately through direct access to the pinned upstream STEP content. Existing S3.C native conversion batch remains blocked by missing source files in this environment.

## Validation and negative cases

S3.D directed local tests: 9 total, **8 PASS and 1 explicit SKIP**, including original source ID preservation, no false welding of almost coincident solids, 4 straight boundary curves in an authored source-graph fixture, reversed sides, mutated IDs and altered controls with recomputed sidecar checksum. The complete locally available S3.A/B/C/D research suite: **55 tests, 53 PASS, 2 SKIP**, zero failures. This is not a 55-test production regression or exact-head CMake/CTest validation.

## Required next scientific gates

1. Execute the pinned source STEP files under OCCT/CadQuery and explicitly map source ADVANCED_FACE/EDGE_CURVE IDs onto imported native TopoDS identities. Raw source SHA-256 and recorded importer/toolchain must agree.
2. Reuse original canonical straight edge controls as constraints of the candidate planar BP patch and each adjacent trimmed/curved face; demonstrate both side orientations and no numerical cracks. The 108 excluded planar neighbors may have holes or many-sided trims; the 44 excluded cylindrical neighbors require valid four-sided decomposition and rational-to-polynomial approximation with budgets set before fitting.
3. Inspect original nonstraight edges elsewhere in the models, including conical/toroidal and S40 rational B-spline faces. Do NOT extrapolate the 152 linear interface result to every source curve.
4. Independently audit geometric approximation with converging samples and state clearly whether continuous bounds exist. Reject cases with unstable or unresolved trims. Never substitute arbitrary filling patches for excluded regions.
5. Only after a complete qualified atlas and G1–G7 gates may the frozen TRI generator be run; QUAD/TRI/all-quad/anisotropy remain separately qualified future methods. External authored non-manifold 3+-sheet original remains unverified.

**Delivery decision:** source-graph edge census and analytic exact-line cubic feasibility measured; S3.D source-original local Python/OCCT gate and curved-surface coupling remain **OPEN**. Research PR stays draft; no merge into main.
