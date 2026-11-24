# S3.G — Original cylindrical generator constraints and native-support gate

**Date:** 2026-11-16. **Classification:** isolated scientific feasibility work. The production C++ generator, frozen historical Book/Eistute/Decor comparators, Stage 3 and the QUAD branch are untouched. This stage does **not** claim converted MAMBO cylinder patches or APMesh mesh acceptance.

## Objective and source provenance

Study the 44 original candidate-planar-to-excluded-cylinder `EDGE_CURVE` identities from M5, S40, S27 and M3, using the original STEP entity graph at immutable `cgg-bern/hex-me-if-you-can` revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`. Identify *axial generator* constraints and only then identify cylindrical faces whose topology is compatible with a possible constrained tensor-product bicubic decomposition.

The original STEP source text was inspected via the GitHub connector and *independent reference-side calculations* were performed on the original `CYLINDRICAL_SURFACE`, `AXIS2_PLACEMENT_3D`, `VERTEX_POINT` and `EDGE_CURVE` records. The original STEP bytes **were not mounted or natively imported** into the local OCCT runtime during S3.G, and their original raw SHA-256 was **not recomputed by this connector-only inspection**. Upstream Git blob SHA-1 and pinned commit identify these examined source texts. Previous S1 byte-level hashes remain a separately documented prerequisite to local original-native execution. No raw third-party STEP body is committed to this repo.

## Source graph geometric results

All examined candidate-to-cylinder edges are original straight master `LINE` edges and match the cylinder's 3D axis direction and radius within a predeclared source numeric consistency threshold `max(1e-8 mm, 1e-9 × max(1, radius, edge length) mm)`; this is **not a bicubic fitting tolerance**.

| Model | Original plane-cylinder edge identities | Distinct adjacent cylinder face IDs | Simple two-generator, one-wire four-edge source rectangle *candidates* | Other/trim-complex cylinder faces | Max radial endpoint residual (mm) | Max axis-transverse edge displacement (mm) |
|---|---:|---:|---:|---:|---:|---:|
| M5 | 4 | 2 | 2 | 0 | 1.288e-13 | 0 |
| S40 | 12 | 8 | 0 | 8 | 4.080e-11 | 6.938e-11 |
| S27 | 8 | 4 | 2 | 2 | 1.435e-10 | 0 |
| M3 | 20 | 15 | 4 | 11 | 2.384e-12 | 0 |
| **Total** | **44** | **29** | **8** | **21** | — | — |

**M5:** The two source cylinder faces `ADVANCED_FACE #3493` and `#3976` each contain one four-edge trim wire with two straight axial generators and two circular boundaries. Both anchored generator spans match. The *minor radial angle* between anchored directions is approximately **2.10209317 rad**, so even the shorter arc requires at least two <=90-degree angular pieces. The actual trimmed parametric sweep, interior versus exterior arc selection, source p-curves and native face orientation are still unverified in this runtime. Therefore these are **source topology candidates**, not accepted BP surfaces.

**S40:** The eight directly adjacent cylinder faces are not admitted by this rectangular source gate. The first four have eight or more trim edges and/or multiple wires or spline edge components; the remaining four have four-edge wires but only one of the two source generators anchored to a selected planar patch. A source-only straight-line boundary is insufficient to infer the other boundary or the correct trimmed cylindrical region. Arbitrary closure or coordinate welding is prohibited.

**S27/M3:** Retained as secondary complexity controls, not substitutes for M5/S40 or a true original non-manifold positive.

Read the evidence independently: [topological original-cylinder screens](evidence/s3g/original_cylinder_source_topology.json) and [independent source-axis numeric oracle](evidence/s3g/original_cylinder_source_axis_oracle.json). Both distinguish source-graph checks from native OCCT validation and APMesh execution.

## S3.G code and actual native control test

The first-party source-only probe is `probes/s3g_cylindrical_source_constraints.py`. It computes source generator direction/radius residuals, original face wire counts, exact source edge IDs, two-anchor consistency, common axial bounds, the lower-bound number of quarter-circle angular sections, explicit rejection causes, and checksums. No control point or source entity is merged by proximity.

The `--native` mode recomputes the existing S3.E and S3.F source-edge and excluded-neighbor `ADVANCED_FACE` ↔ `TopoDS_Face` correspondence before checking **native cylinder radius, axis direction, and axis-line location** against the source STEP support. A mismatch raises an exception, and no result file is produced. A successful support-level check still does not certify the actual UV trim, p-curve mapping, adjacent bicubic Bézier net, sampled geometric fit, continuous error bound or a generated mesh.

On an author-constructed half-cylinder STEP (four source/native faces, two original plane-cylinder generator anchors), `--native` passed: one original neighboring cylinder STEP face mapped to one native cylinder face, radius 3 mm, zero observed radius/axis-position deviation, and two verified source edge anchors. [Synthetic test receipt](evidence/s3g/synthetic_native_support_receipt.json) is **not original industrial evidence**.

### Reproduce with the existing research probes

Run from the research probe directory or set `PYTHONPATH` to the directory, with CadQuery, OCP and NumPy installed:

```sh
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p 'test_*.py' -v
python docs/research/nonmanifold-benchmark/probes/s3g_cylindrical_source_constraints.py --model M5 --source-step /external/mambo/sources/i05o_m5.step --native --output build/research-s3g/m5_source_native.json
python docs/research/nonmanifold-benchmark/probes/s3g_cylindrical_source_constraints.py --model S40 --source-step /external/mambo/sources/i25o_s40.step --native --output build/research-s3g/s40_source_native.json
```

The two original commands are **NOT RUN** in this environment because the original industrial STEP files are not available locally; do not interpret them as completed native tests. For an unrelated author-constructed source, pass `--model SYNTHETIC --expected-sha256 ACTUAL_HASH` to enable the explicitly pinned synthetic run.

## Directed test results and blocking gates

The full research probe suite actually executed locally: **96 tests discovered, 91 passed, 5 explicitly skipped, 0 failed**. Of those, the 16 new S3.G tests had 15 PASS and 1 SKIP; test controls include source generator classification, original/native support agreement in an author-generated STEP, source checksum, forged evidence with recomputed checksum, radius/axis corruption, strict source SHA admission, and fail-closed CLI. This is NOT the full production/scientific C++ regression or a check on the final remote commit.

S3.G is a **bounded source screen and a synthetic native-support verification**, not completion of the original industrial CAD mesh milestone. Remaining gates:

1. Obtain rights-cleared, byte-identical original M5/S40 STEP *outside* the source repository, verify SHA-256 and run S3.E/S3.F/S3.G natively, reporting every unmatched `ADVANCED_FACE` and `EDGE_CURVE` rather than repairing them silently.
2. On M5 `#3493/#3976`, resolve the native trimmed U/V domain and original edge p-curve orientation. Construct patch subdivisions with **original generator control IDs shared exactly** with the planar BP atlas, independently audit maximum source-surface deviations under predeclared numerical budgets, and record any rejected subdivision.
3. On S40, develop a feature-curve-first trim decomposition for multiply wired, split-edge, and rational B-spline-adjacent surfaces. Do not convert them as simple four-edge rectangles based on a source-axis residual alone.
4. Continue the distinct external *original* 3+-incident multi-sheet BRep search. MAMBO manifold complexity is a control, not a genuine non-manifold positive.
5. Only after an independently audited admissible BP atlas exists, run and validate accepted APMesh TRI and later, conditionally, QUAD/anisotropic comparisons.

**Research PR #225 remains draft; do not merge to main without exact-head local acceptance tests and advisor scientific review.**
