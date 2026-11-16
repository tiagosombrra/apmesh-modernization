# S3.K — Byte-pinned original CAD import, indexed partial BP and native UV-trim audit

**Date:** 2026-11-16. **Classification:** isolated scientific research, not production C++ modernization. Research branch `research/benchmark-corpus-reverse-patches`; draft PR #225. Original third-party STEP files and their direct BP derivatives are **not committed** pending redistribution-rights review.

## Major change from S3.A–S3.J

All **four** original `cgg-bern/hex-me-if-you-can` HexMe/MAMBO STEP files, from frozen revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, became available as *actual local bytes* for this checkpoint. They were transferred only for the local analysis, with any intermediate private text documents deleted. Their normalized source bytes were admitted **only after matching the pre-existing frozen raw SHA-256**. Original sources stayed outside the research repository. This is not a substitution with box, T, or author-generated cylinder fixtures.

| Original | Frozen SHA-256 | Source faces | Independently audited exact planar BP patches | Original candidate-to-excluded interfaces correlated natively | Excluded first-ring native neighbor face IDs | Native cylinder support faces crosschecked |
|---|---|---:|---:|---:|---:|---:|
| M5 `i05o_m5.step` | `895f67c0669096b287077ac1bb56dad0e117cd96f78334d3129d783fd78b96cb` | 41 | 6 | 20 | 7 | 2 |
| S40 `i25o_s40.step` | `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b` | 43 | 9 | 32 | 18 | 8 |
| S27 `i22o_s27.step` | `b4a60c43cabd3c72bf61d54a23f36e6e539ad985015d2a7c377885b5d170f8c5` | 52 | 20 | 60 | 14 | 4 |
| M3 `i03o_m3.step` | `c42862fa6bc1e94a9bb70e43a7dc9901aa5281d7b58de6ee4699494088286008` | 60 | 10 | 40 | 23 | 15 |
| **Total** | — | **196** | **45** | **152** | **62** | **29** |

S3.C batch, S3.E original source-to-native candidate/edge correspondence, S3.F original first-ring `ADVANCED_FACE`↔`TopoDS_Face` mapping, and S3.G native support checks returned successful reports for all four originals. **These outputs remain partial source-certified surface evidence, not a complete manifold or non-manifold model atlas.** The 62 first-ring identities are model-local distinct original face IDs. No mesh-generation acceptance is asserted.

## M5 source-to-native joint BP milestone

The actual pinned M5 source `ADVANCED_FACE #3493` and `#3976` were uniquely mapped to imported cylindrical native faces, connected to their admitted planar neighbors by **four original `EDGE_CURVE` generator identities**, and processed by the S3.I integrated builder. The predeclared experimental budget is **0.001 mm** (not advisor-approved publication tolerance):

| Sectors per cylinder face | Accepted source geometry pilot | Original BP patches (6 planar + cylinders) | Original global controls (4-sector option) | Independent sampled native trimmed-face distance (mm) | S3.J guarded analytic radial support upper (mm) |
|---:|---|---:|---:|---:|---:|
| 2 | **REJECTED** (0.00624 mm sampled > budget) | not emitted by fail-closed S3.I | — | — | — |
| 4 | **PASS** | **14** | **176** | **0.0003954273703** | **0.0003954283703** |
| 6 | **PASS** | **18** | not claimed as 176 | **0.0000783092353** | **0.0000783102353** |

For four sectors: 6 source planar faces and 2 source cylinders are represented; **33 of 41 original faces remain unrepresented**. Four shared source generator edges reuse **16 exact indexed control IDs** across planar and curved BP patches. Global shared-control identity has been independently audited, not established by coordinate-near welding. Both original cylindrical native faces are the same radius 2 mm, and each selected oriented source angular sweep is 2.102093169774461 rad.

## New S3.K: independent native OCCT trimmed-face UV membership

`probes/s3k_native_uv_trim_gate.py` imports the *same pinned STEP* natively and recomputes the previous source-to-native, shared-control, sampled native-distance, and Bernstein radial-support audits. For each bicubic cylinder patch, it computes native cylindrical parameters using `ElSLib.Parameters_s(gp_Cylinder, gp_Pnt)` and checks membership in the actual trimmed `TopoDS_Face` using `BRepClass_FaceClassifier`; 2π periodic U equivalents are checked explicitly rather than assuming an unwrapped domain. It also checks sampled point-to-native-cylinder distance and covers the native trim UV bounding interval without observed segment gaps.

On the original M5 four-sector configuration:

- **648/648 interior samples:** classified `IN`.
- **352/352 boundary samples:** classified either `IN` (108 samples) or `ON` (244 samples); zero `OUT`.
- **Two source faces:** `#3493` and `#3976`, each with original native UV bounds approximately `[π, 5.243685823365] × [-7.5,7.5]`; the patch-union bounds agree within tolerance, without sampled U gaps.
- **Native pointwise cylinder projection maximum:** `0.0003954273703068376 mm`.
- **Guarded numeric radial support bound:** `0.0003954283703068445 mm`.
- The six-sector original M5 configuration also passed: 972 interior + 528 boundary samples, maximum native projection deviation `0.0000783092353257144 mm` (see machine-readable receipt for the exact measured value).

**Important distinction:** the numerical Bernstein control-polynomial enclosure is a guarded floating-point support bound, **not** a formally directed-rounding interval proof. The BRepClass classification is **discrete native trim-membership evidence**, **not** proof of global continuous trim topology, a full trimmed-surface Hausdorff bound, or multi-face watertight closure. Partial M5 BP is not a complete model. The other 33 excluded M5 faces still block an accepted full-model mesh; S40's eight first-ring cylinders have complex trims that this bounded rectangle converter does not silently admit.

## Original-enabled regression and discovered dormant test defect

Re-running the prior 151-case research suite with real source assets exposed one dormant test-only defect: `test_s3d_canonical_feature_curves.py` invoked the independent auditor using `expected_model="SYNTHETIC"` even when testing pinned original `M5/S40/S27/M3` inputs. The test is corrected to pass the actual original model and frozen digest. Three previous unconditional source-absence skips in S3.E/F/G were changed into conditional tests which **run the original M5 and S40 native gates if sources are available, and skip only if genuinely absent**. No production scientific policy was changed.

After adding 13 S3.K directed UV-trim tests and the four test-only corrections, the full locally executed research suite reported **164 discovered, 164 passed, 0 skipped, 0 failed** with all four original files present. Without the original files, conditional tests should still skip explicitly rather than claim to pass. Tests reject invalid original hash, forged BP hash, externally widened budgets, wrong face support, radially consistent but **angularly outside trimmed face** controls, axially translated controls, and malformed UV sampling inputs.

Environment used: Python 3.13.5, CadQuery 2.8.0, `cadquery-ocp` 7.9.3.1.1, NumPy 2.3.5. The **full production C++/CTest scientific regression was not executed**; this research branch must not be merged solely on the strength of these Python tests.

## Reproduce without redistributing third-party STEP assets

Acquire original source bytes separately under the upstream's applicable license and place them outside the research repository. For a local clone of the original repository, checkout its immutable revision, then copy the four STEP originals to an external `sources` directory. Verify the fixed SHA-256 before execution.

```sh
export APMESH_MAMBO_SOURCE_DIR=/external/mambo/sources
export APMESH_REAL_CAD_WORKSPACE=/external/mambo
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p 'test_*.py' -v
python docs/research/nonmanifold-benchmark/probes/s3c_original_batch.py --sources "$APMESH_MAMBO_SOURCE_DIR" --output build/research-s3k/original-planar --models M5 S40 S27 M3
python docs/research/nonmanifold-benchmark/probes/s3i_joint_source_atlas.py --source-step "$APMESH_MAMBO_SOURCE_DIR/i05o_m5.step" --model M5 --cylinder-faces 3493 3976 --sectors 4 --sampled-budget-mm 0.001 --output build/research-s3k/m5-joint
python docs/research/nonmanifold-benchmark/probes/s3j_radial_support_enclosure.py --step "$APMESH_MAMBO_SOURCE_DIR/i05o_m5.step" --bp build/research-s3k/m5-joint/source_joint.partial.bp --manifest build/research-s3k/m5-joint/source_joint_manifest.json --model M5 --budget-mm 0.001 --output build/research-s3k/m5-radial.json
python docs/research/nonmanifold-benchmark/probes/s3k_native_uv_trim_gate.py --step "$APMESH_MAMBO_SOURCE_DIR/i05o_m5.step" --bp build/research-s3k/m5-joint/source_joint.partial.bp --manifest build/research-s3k/m5-joint/source_joint_manifest.json --model M5 --budget-mm 0.001 --output build/research-s3k/m5-native-uv.json
```

The S3.K gate *fails closed* before writing output when its source, BP, geometric or trim tests fail. Derived experimental BP files can be retained in a **private local evidence package**, but are not committed as third-party-derived industrial geometry pending rights review.

## Closure and next gate (S3.L)

- S3.K original byte identity/import, original face/edge mapping, 45 partial planar patches, and original M5 eight-cylinder-patch native UV sampled audit: **MEASURED in declared scope**.
- S40 original eight source-adjacent cylinders: **NOT ADMITTED**, require feature-curve-first partition of multiply trimmed/split-edge faces; prioritize S40 original source-native face/loop UV segmentation, with negative controls.
- Complete original CAD patch atlas, globally watertight shared-curve topology, original 3+-sheet non-manifold positive, accepted APMesh TRI/QUAD, full C++ production regression, formal continuous distance bounds and advisor-approved scientific tolerance: **OPEN**.
- Draft PR #225 is isolated; retain it as draft and do not merge to `main` until the repository's exact-head/production/scientific gates and advisor review permit it.
