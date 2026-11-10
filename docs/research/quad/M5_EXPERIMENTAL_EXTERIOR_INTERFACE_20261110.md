# M5 — C++ Quadtree QUAD / experimental exterior TRI interface — 2026-11-10

**Status:** Research-only topology gate, **NOT historical Delaunay/contraction**, not a physical hybrid APMesh generation mode.

The authoritative native artifact from [PR #199](https://github.com/tiagosombrra/apmesh-modernization/pull/199) contains a real C++ Quadtree, 19 leaves, seven included QUAD leaves, twelve excluded boundary leaves and **42 UV QUAD, area 0.25**. The new `quad.m5.experimental_exterior_interface` native CTest first executes that actual C++ emitter, then reads its exact `tree_regions.csv` and `quads_*.obj`. It **preserves** all 42 native quadrilaterals, adds **60 actual experimental UV triangles** using a cell-center fan on the twelve exterior rectangles and outputs both `hybrid_experimental_vertex_mean.obj` and `hybrid_experimental_area_centroid.obj`.

The algorithm explicitly reuses all available C++ midpoint coordinates and Quadtree leaf corners to split external edges consistently. Its full disk contract checks **area 0.25 QUAD + 0.75 TRI = 1.0**, 20 oppositely oriented shared QUAD/TRI interface edges forming one closed loop of length 2, 16 outer square boundary edges, positive orientation, single disk Euler characteristic, no duplicate vertices, no hanging points, and four deliberately invalid mutations. The two experimental point rules produce identical topology while retaining different QUAD coordinates.

The CTest writes `experimental_hybrid.svg`, `quad_tri_interface.csv`, both OBJ and `experimental_hybrid_manifest.json`. These source-bound outputs will be uploaded by Linux CI. Native **11/11 QUAD CTest** and the full frozen TRI/CLI/science gates are required on the exact PR head before merge.

**Methodological limitation:** cell-center fan triangulation is not the historical 1993 algorithm by Bento/Carvalho/Martha. The intended 1993 mode uses Delaunay and contour contraction, which has not been recreated in this code path. No numerical point rule was approved by Bento/Creto. There is no UV→XYZ, physical quadrilateral lifecycle, multipatch conformity, production dispatch, rollback or all-QUAD extension. The green M5 experiment is evidence of interface feasibility, **not of historical fidelity or M5 closure**.

Next: consult the original algorithm and existing Delaunay/contour implementation and replace the experimental fan in a distinct reviewed research PR, preserving the established native C++ QUAD geometry and seam-independent verification. The reproduction-hybrid-first and selectable-all-QUAD-second order remains unchanged.

## Exact-head review and native-output evidence — 2026-11-10

- Candidate `d30bc0e7457aecfafe6264dfc0961e8bd57d009e`, [Actions #42898041678](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42898041678) **SUCCESS 4/4 jobs**. QUAD GCC/MSVC 11/11 each; TRI 78/78; tooling 527/527; CLI rejects 7/7; Eistute five and Book four strictly retain OBJ byte identity, acceptance and boundary coverage.
- [PR #200](https://github.com/tiagosombrra/apmesh-modernization/pull/200) reviewed and merged to research `quad-templates` as `8a088cb58e89794c1cc22e8f62221fef2dd3dae4`; exact merge tree equals tested feature. Modernization `main` unchanged.
- [Native Linux artifact #13801072358](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42898041678/artifacts/13801072358) was downloaded and independently inspected: both combined OBJ variants have 81 vertices, 42 source C++ QUAD and 60 experimental TRI, single 20-edge seam and unit UV area. This confirms **actual CI-produced output**, not merely local drawings. [Evidence JSON](evidence/M5_EXPERIMENTAL_EXTERIOR_INTERFACE_20261110.json) stores qualification.
- [Postmerge #42899687132](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42899687132) in_progress at checkpoint; exact SHA result not yet declared final.

## Post-merge exact regression closure — 2026-11-10

The [exact merged-SHA Actions #42899687132](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42899687132) completed **SUCCESS** all four mandatory jobs: native QUAD 11/11 on GCC/MSVC, full TRI 78/78, tooling 527/527, CLI 7/7, Eistute 5/Book 4 scientific parity. [Evidence](evidence/M5_EXPERIMENTAL_EXTERIOR_INTERFACE_20261110.json) now records the final conclusion rather than the preceding in-progress checkpoint.

**Next-source warning:** the current examined APMesh exterior code is in `AdvancingFront` and `Boundary` classes, which does not establish a historical Delaunay/contraction implementation. Analyze the original 1993 procedure and advisers' scientific point behavior explicitly before replacing this **experimental** center-fan test. Do not downgrade validation, claim physical hybrid, or enable all-QUAD by default.
