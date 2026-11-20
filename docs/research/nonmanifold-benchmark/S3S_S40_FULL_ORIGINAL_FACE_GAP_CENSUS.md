# S3.S — Original S40 complete source/native incidence certificate and 26-face gap census

**Checkpoint:** 2026-11-17. **Category:** isolated research-only topology analysis. **No production C++ changes; no mesh or new Bézier patches generated.** Branch: `research/benchmark-corpus-reverse-patches`, draft PR #225.

## Original source and frozen baseline

- Authoritative external STEP: `cgg-bern/hex-me-if-you-can`, revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, `original/i25o_s40.step`.
- SHA-256 (byte-verified before import): `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`.
- Previous **integrated**, partial research BP: 126 patches; 17 of 43 original faces; 1,467 historical declarations / 1,349 active controls, plus deterministic compact representation. The S3.R BP SHA-256 is required to be `98ff4cbfad08ce3f587607fddf3bb5e1a3697e1513a8ca86889bb28406e4028d`.
- Neither the original third-party STEP nor derived control geometry is committed to the public repository. The original source and the private frozen S3.R BP are inputs to this checkpoint, not new outputs.

## Full original/native identity mapping: 43 faces, 117 edges, 77 vertices

The source/native reconciliation is no longer limited to the admitted planar candidates or their first ring. It performs a **whole-model source topology audit**:

1. Parse the original STEP `ADVANCED_FACE`, `FACE_BOUND`, `EDGE_LOOP`, `ORIENTED_EDGE`, `EDGE_CURVE` and `VERTEX_POINT` identities, retaining each original wire and 3D master curve type.
2. Import the pinned STEP with CadQuery/Open CASCADE, requiring `isValid()` and the fixed 43-face census. Build global `TopoDS_Face`/`TopoDS_Edge`/`TopoDS_Vertex` identity graphs.
3. Screen source-edge ↔ native-edge candidates using compatible master curve types and two original endpoint coordinates with **a fixed 1e-6-mm source/import screening tolerance**. This does not authorize coordinate welding or new patch acceptance.
4. Match all original faces to native faces by support type, per-wire edge counts, and a *full injective edge-set matching*. Require every source face to have exactly one eligible native face and global face bijection.
5. Resolve each original source edge to a unique native `TopoDS_Edge` using its **complete original incident face ID set**, mapped through the certified face bijection. This is essential: original circles `EDGE_CURVE #378` and `#1991` share endpoint locations and 3D curve types. Naive proximity would conflate them. Their native identities are distinct (0-based native edges 10 and 64).
6. Map original `VERTEX_POINT` IDs to native vertices using both bounded endpoint coordinates and **exact mapped incident edge sets**. Require a full vertex bijection. Reject all missing, ambiguous, or colliding assignments.

**Measured on the original model:** 43/43 faces; 117/117 edges; 77/77 vertices. **No original EDGE_CURVE has three or more distinct incident faces** (observed maximum 2), so S40 continues to be a manifold control. This certificate is a discrete identity/correspondence result, **not** a continuous geometric equivalence certificate of original curved STEP surfaces, nor proof of a 3+-sheet non-manifold test.

## Complete original face coverage and gap census

| Original source group | Face count |
|---|---:|
| Already represented by frozen S3.R BP | **17** |
| Unrepresented original `PLANE` faces | **17** |
| Unrepresented original `CYLINDRICAL_SURFACE` faces | **6** |
| Unrepresented `B_SPLINE_SURFACE_WITH_KNOTS` faces | **2** |
| Unrepresented `COMPLEX_RATIONAL_B_SPLINE_SURFACE` faces | **1** |
| **Total original source faces** | **43** |

Of the 26 unrepresented faces, **15** have at least one direct original `EDGE_CURVE` shared with an already-represented original face, and **11** are **two graph-edge hops** away. Every original face is reached by breadth-first traversal of the source face-incidence graph; no matching in this census uses coordinate-near sewing to infer adjacency.

### Original face-by-face private/public non-geometric inventory

Rows show only source entity IDs, native local indices, support type, wire-edge counts, graph distance and boundary master curve kinds — **no original STEP bytes, BP controls, or CAD tessellation coordinates**.

| STEP source face | 0-based native face index | Surface | Edges per source wire | Atlas hops | Direct atlas interfaces | 3D edge kinds |
|---|---:|---|---|---:|---:|---|
| `#912` | 5 | `PLANE` | [8] | 1 | 3 | LINE:8 |
| `#3737` | 42 | `PLANE` | [8] | 1 | 3 | LINE:8 |
| `#17` | 0 | `PLANE` | [4] | 1 | 4 | B_SPLINE_CURVE_WITH_KNOTS:1, CIRCLE:1, LINE:2 |
| `#2092` | 18 | `PLANE` | [4] | 1 | 4 | B_SPLINE_CURVE_WITH_KNOTS:1, CIRCLE:1, LINE:2 |
| `#1827` | 15 | `PLANE` | [6] | 1 | 6 | CIRCLE:4, LINE:2 |
| `#1907` | 16 | `PLANE` | [6] | 1 | 6 | CIRCLE:4, LINE:2 |
| `#3044` | 29 | `PLANE` | [6] | 1 | 6 | CIRCLE:4, LINE:2 |
| `#3269` | 35 | `PLANE` | [5] | 2 | 0 | LINE:5 |
| `#3485` | 38 | `PLANE` | [5] | 2 | 0 | LINE:5 |
| `#1279` | 9 | `PLANE` | [6] | 1 | 1 | CIRCLE:2, LINE:4 |
| `#1386` | 10 | `PLANE` | [6] | 1 | 1 | CIRCLE:2, LINE:4 |
| `#2469` | 23 | `PLANE` | [4] | 2 | 0 | B_SPLINE_CURVE_WITH_KNOTS:1, LINE:3 |
| `#3134` | 32 | `PLANE` | [4] | 2 | 0 | B_SPLINE_CURVE_WITH_KNOTS:1, LINE:3 |
| `#859` | 4 | `PLANE` | [4] | 1 | 1 | B_SPLINE_CURVE_WITH_KNOTS:2, CIRCLE:1, LINE:1 |
| `#2243` | 19 | `PLANE` | [2, 3] | 1 | 5 | B_SPLINE_CURVE_WITH_KNOTS:3, CIRCLE:2 |
| `#3183` | 33 | `CYLINDRICAL_SURFACE` | [4] | 2 | 0 | CIRCLE:2, LINE:2 |
| `#3237` | 34 | `CYLINDRICAL_SURFACE` | [4] | 2 | 0 | CIRCLE:2, LINE:2 |
| `#3319` | 36 | `CYLINDRICAL_SURFACE` | [4] | 2 | 0 | B_SPLINE_CURVE_WITH_KNOTS:1, CIRCLE:1, LINE:2 |
| `#3402` | 37 | `CYLINDRICAL_SURFACE` | [4] | 2 | 0 | B_SPLINE_CURVE_WITH_KNOTS:1, CIRCLE:1, LINE:2 |
| `#3683` | 40 | `CYLINDRICAL_SURFACE` | [4] | 2 | 0 | B_SPLINE_CURVE_WITH_KNOTS:1, CIRCLE:1, LINE:2 |
| `#3710` | 41 | `CYLINDRICAL_SURFACE` | [4] | 2 | 0 | B_SPLINE_CURVE_WITH_KNOTS:1, CIRCLE:1, LINE:2 |
| `#2545` | 24 | `PLANE` | [5, 6] | 1 | 6 | B_SPLINE_CURVE_WITH_KNOTS:1, CIRCLE:6, LINE:4 |
| `#3535` | 39 | `PLANE` | [13] | 2 | 0 | B_SPLINE_CURVE_WITH_KNOTS:4, CIRCLE:2, LINE:7 |
| `#1493` | 11 | `B_SPLINE_SURFACE_WITH_KNOTS` | [4] | 1 | 1 | B_SPLINE_CURVE_WITH_KNOTS:1, LINE:3 |
| `#807` | 3 | `B_SPLINE_SURFACE_WITH_KNOTS` | [4] | 1 | 1 | B_SPLINE_CURVE_WITH_KNOTS:3, LINE:1 |
| `#556` | 2 | `COMPLEX_RATIONAL_B_SPLINE_SURFACE` | [8] | 1 | 1 | B_SPLINE_CURVE_WITH_KNOTS:5, LINE:3 |

This is a *heuristic* ordering, not scientific acceptance. The priority score favors previously represented original neighbor edges and boundary types with fewer curved or spline constraints, and penalizes inner wires and split boundaries. Scores do not compare surface area, Jacobian conditioning, actual quadtree adaptations, mesh element quality, or numerical robustness of a not-yet-built decomposition.

## Next research stage S3.T — candidate-first planar decomposition

**Preferred first candidates:** original `ADVANCED_FACE #912` (native face 5) and `#3737` (native face 42).

- Each is a true original **planar** face with one outer wire, **eight original `LINE` boundary edges**, no spline/arc master boundaries, and **no inner wire**.
- Each shares exactly three original source interfaces with already represented planar faces `#1105`, `#1181`, and `#1230`.
- The original eight-edge polygon is **not** a simple four-edge rectangle. It has angled corners and must be decomposed into valid planar quadrangular source-conforming patches; do not replace it with a bounding rectangle or remove vertices.
- Next implementation must reuse existing global control IDs of original common edges or propagate exact de Casteljau subdivision into the neighboring source BP, then independently verify original wire coverage, patch interior disjointness, native UV membership, original edge proximity, both-sided integer seams, and unchanged prior patches.
- Curved planar boundaries `#17`, `#2092`, `#1827`, `#1907`, `#3044`, plus six excluded cylinders and three true B-spline supports, remain in the subsequent queue, with technical risks recorded in the JSON inventory.

## Executed testing and closure limitations

- New S3.S full source/native negative and positive tests: **17/17 PASS**.
- Complementary old S3.R + new S3.S selection: **54/54 PASS** with the frozen original S40 and previous real BP.
- Cumulative S3.M–S3.S selection: **145 discovered, 143 PASS, 2 SKIP** when optional S3.Q earlier baseline inputs were not set. Both optional S3.Q tests were previously validated in their own earlier checkpoint. A second attempt enabling them exceeded a 120-second execution limit while reaching the final S3.S tests without a recorded error; **it is NOT an all-green completion and must not be described as 145/145 PASS**.
- No C++ production regression, accepted APMesh TRI/QUAD mesh, full original 43-face atlas, continuous Hausdorff/trim proof, or original 3+-sheet non-manifold example is established by S3.S.
- Public PR #225 remains draft and `main` untouched. The principal S3.S deliverable is the source/native correspondence code, 26-face gap taxonomy, and machine-readable **non-geometric** receipt. No new patch was admitted.

## Reproduce (private source and prior BP)

Requires Python 3, CadQuery 2.8, Open CASCADE/OCP, and first-party S3.A–S3.R probe modules from the prior private research package.

```sh
export APMESH_ORIGINAL_CAD_DIR=/path/to/authorized-originals
export APMESH_MAMBO_SOURCE_DIR=/path/to/authorized-originals
export APMESH_S3R_BASELINE_BP=/path/to/private/s40_218_conforming.partial.bp
export APMESH_S3R_BASELINE_MANIFEST=/path/to/private/s40_218_conforming_manifest.json
python -m unittest -v test_s3s_full_original_face_census
python s3s_full_original_face_census.py \
  --source-step "$APMESH_ORIGINAL_CAD_DIR/i25o_s40.step" \
  --baseline-bp "$APMESH_S3R_BASELINE_BP" \
  --baseline-manifest "$APMESH_S3R_BASELINE_MANIFEST" \
  --output /private/output/s3s_original_native_census.json
```

All first-party code/comments/docs are English and restricted to research probes. A public non-geometric receipt is safe for reviewing prioritization. The private original STEP is deliberately excluded from both ZIP and GitHub.
