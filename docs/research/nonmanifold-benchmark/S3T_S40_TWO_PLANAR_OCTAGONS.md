# S3.T — Original S40 planar octagon partition and source-indexed Bézier extension

**Date:** 2026-11-17. **Scope:** isolated scientific-research pilot for the original industrial S40 CAD, not a production APMesh meshing result. The research PR #225 remains a draft; no `main`, QUAD or production C++ code was modified.

## Frozen source and prerequisites

- Upstream: `cgg-bern/hex-me-if-you-can`, revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, `original/i25o_s40.step`, frozen raw SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`.
- Required S3.R original S40 BP: SHA-256 `98ff4cbfad08ce3f587607fddf3bb5e1a3697e1513a8ca86889bb28406e4028d`, 126 patches and 1,467 declared controls. The original hole in STEP face `#218` remains preserved. The S3.R BP's first 126 patch control nets and all original 1,467 positions are unchanged.
- Required S3.P canonical source-control registry: sorted/indented JSON SHA-256 `3c86bbadabd0689a93527a397560b36033e18f60db661b442eaa698f8b5c5bbe`, with 864 previously registered source-derived controls. This registry is necessary because the S3.R manifest by itself does not carry the canonical original edge-key map.
- Source/native mapping: the existing S3.S independently recomputed one-to-one correspondence for **43 source/native faces, 117 original/native edges and 77 vertices**, including edge-incidence disambiguation. Only the two selected source faces are admitted in this step.

## Original source topology and unique planar quadrangulation

The two new source `ADVANCED_FACE` regions are constant-Y `PLANE`s, each bounded by one genuine 8-edge STEP wire with eight distinct `LINE` `EDGE_CURVE`s, no hole and no nonlinear `PCURVE`.

| Source face | Native face index | Native oriented face normal | Original planar polygon area (mm²) | Source shared edges already indexed | New polygon partition |
| --- | ---: | --- | ---: | --- | --- |
| `#912` | 5 | +Y | 242.89192333128233 | `#916`, `#946`, `#974` | three convex quadrilaterals, two source-vertex diagonals |
| `#3737` | 42 | −Y | 932.8414433368824 | `#1234`, `#1185`, `#1109` | three convex quadrilaterals, two source-vertex diagonals |

The builder enumerates pairs of admissible vertex-to-vertex diagonals, rejects diagonals outside the source polygon, polygonizes their union with the eight original edges, requires exactly three convex quadrilaterals with pairwise disjoint interiors, and requires the quadrilateral areas to sum to the original polygon area within the fixed polygon tolerance. For **each** frozen source face, precisely one such admissible two-diagonal partition is found. It does not subdivide original exterior STEP edges or create replacement source vertices. The original `ADVANCED_FACE` orientation flag and supporting `PLANE` normal determine the oriented patch order; this prevents treating the two opposite-Y faces as having the same outward orientation.

Original shared boundary controls are identified by `vertex:<STEP VERTEX_POINT>` and `edge:<STEP EDGE_CURVE>:1/2` **integer IDs** from the frozen S3.P registry. New original exterior edge controls and new two-diagonal internal controls receive distinct source-derived symbolic keys. Only after these index identities are established is geometric coordinate consistency checked. The bicubic interior is formed from an exact cubic-boundary Coons construction, which reproduces all four source-indexed boundary curves; no coordinate-proximity welding is performed. This is a planar geometric representation, not a computed QUAD mesh.

## Original native BRep audit and measured result

The independent S3.T auditor reconstructs the entire generated BP from the pinned original source and manifests, checks the original 126-patch prefix, recomputes the S3.S native face/edge/vertex bijection, requires the correct original `TopoDS_Face` identity and orientation, classifies new patch samples against each *trimmed* native face via the native plane's UV parameters, and samples the real original native `BRepAdaptor_Curve` on all 16 distinct source edges.

| Gate | Observed original S40 result |
| --- | ---: |
| Previous integrated source BP | 126 patches / 1,467 declared controls / 17 original faces |
| S3.T patches added | **6** (3 on each face) |
| **New integrated partial BP** | **132 patches / 1,527 declared controls / 19 of 43 original faces** |
| Newly declared controls | 60; 1,409 active overall; 118 inherited historical controls remain inactive |
| Existing patches retopologized | 0 |
| Global exactly two-sided indexed seams | **189** (179 prior + 6 source joins + 4 new internal diagonals) |
| Global open indexed sides | **150** (incomplete original CAD atlas) |
| New source edge identities independently mapped | 16/16 |
| Native trimmed-face interior samples | **486/486 IN** |
| Native trimmed-face boundary samples | **264/264 IN or ON** |
| Original native boundary-curve samples | **176** |
| Maximum new-patch plane-support sampled distance | **2.940237502212347e-10 mm** |
| Maximum original source/native edge sampled deviation | **1.209999878592805e-10 mm** |
| Predeclared strict planar-check tolerance | 1e-7 mm |
| Prior experimental global geometry budget (unchanged) | 0.001 mm |
| Source holed face #218 preserved | YES, unchanged inherited control nets |

These distances are **sampled**. Neither continuous native trimmed-surface Hausdorff equivalence nor formally directed-rounding interval certification follows. The global 0.001-mm pilot is not an advisor-approved publication tolerance. The S40 CAD itself remains a **manifold** control, not a source with verified 3+-incident edges.

## Regression, adversarial controls and reproducibility

- S3.T targeted tests: **28 PASS, 0 FAIL, 0 SKIP**. The tests cover immutable source/baseline/registry hashes; convex unique polygonization; exact original integer control sharing; count of newly added patches; oriented native face normals; unchanged S3.R patch prefix and preserved hole; native original edge and face identity; native trimmed face UV membership; error budget; and negative controls for modified source, parent BP, registry, budget, receipt, generated BP, hole provenance and wrong native BRep.
- Directed cumulative S3.R + S3.S + S3.T: **82 PASS, 0 FAIL, 0 SKIP** with the original S40 STEP.
- Extended original-S40 S3.M–S3.T research selection: **173/173 PASS, 0 FAIL, 0 SKIP** after supplying the optional S3.Q historical 77-patch baseline. The first run found two missing *local intermediary files*; once mounted, the entire expanded selection completed successfully in 33.342 seconds. The separate S3.A–S3.L legacy suite and production C++ regressions were not rerun.
- No production C++ regression or real APMesh TRI/QUAD mesh generation is claimed.

Install Python 3, CadQuery 2.8/Open CASCADE (OCP), NumPy, and Shapely 2.x, supply the **authorized** original STEP file outside the public repository, and run from the package's `code/` directory:

```bash
python s3t_s40_planar_octagons.py \
  --source-step /private/original/i25o_s40.step \
  --baseline-bp /private/s3r/s40_218_conforming.partial.bp \
  --baseline-manifest /private/s3r/s40_218_conforming_manifest.json \
  --source-registry-manifest /private/s3p/s40_complement2457_manifest.json \
  --output-dir /private/s3t/result
```

The builder rejects a changed 0.001-mm experimental budget rather than accepting a later relaxed tolerance. Source original STEP bytes and the newly derived original BP coordinates are intentionally **not committed publicly** until redistribution rights are reviewed; the user's private ZIP may contain the derived BP, manifest and visualizer but not the third-party STEP.

## Next bounded S3.U priorities

1. Update the S3.S gap census with the S3.T source face identities: **24** S40 original faces remain unrepresented. Recompute direct first-ring priorities without assuming the previous candidate graph stayed unchanged.
2. Consider other planar polygon regions and their split-edge conforming propagation before additional curved or spline surfaces; reject ambiguous edge owners, unsupported holes and self-intersecting partitions.
3. Build a separate genuine industrial multi-sheet 3+-incident non-manifold positive; S40/M5 original manifold controls do not establish this claim.
4. Keep the full original atlas, APMesh TRI/QUAD accepted meshing, continuous error certification, C++ regressions and advisor scientific review as separate open gates. PR #225 remains draft; do not merge to `main`.
