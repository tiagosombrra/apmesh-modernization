# M5 — C++ Quadtree QUAD / experimental exterior TRI interface — 2026-11-10

**Status:** Research-only topology gate, **NOT historical Delaunay/contraction**, not a physical hybrid APMesh generation mode.

The authoritative native artifact from [PR #199](https://github.com/tiagosombrra/apmesh-modernization/pull/199) contains a real C++ Quadtree, 19 leaves, seven included QUAD leaves, twelve excluded boundary leaves and **42 UV QUAD, area 0.25**. The new `quad.m5.experimental_exterior_interface` native CTest first executes that actual C++ emitter, then reads its exact `tree_regions.csv` and `quads_*.obj`. It **preserves** all 42 native quadrilaterals, adds **60 actual experimental UV triangles** using a cell-center fan on the twelve exterior rectangles and outputs both `hybrid_experimental_vertex_mean.obj` and `hybrid_experimental_area_centroid.obj`.

The algorithm explicitly reuses all available C++ midpoint coordinates and Quadtree leaf corners to split external edges consistently. Its full disk contract checks **area 0.25 QUAD + 0.75 TRI = 1.0**, 20 oppositely oriented shared QUAD/TRI interface edges forming one closed loop of length 2, 16 outer square boundary edges, positive orientation, single disk Euler characteristic, no duplicate vertices, no hanging points, and four deliberately invalid mutations. The two experimental point rules produce identical topology while retaining different QUAD coordinates.

The CTest writes `experimental_hybrid.svg`, `quad_tri_interface.csv`, both OBJ and `experimental_hybrid_manifest.json`. These source-bound outputs will be uploaded by Linux CI. Native **11/11 QUAD CTest** and the full frozen TRI/CLI/science gates are required on the exact PR head before merge.

**Methodological limitation:** cell-center fan triangulation is not the historical 1993 algorithm by Bento/Carvalho/Martha. The intended 1993 mode uses Delaunay and contour contraction, which has not been recreated in this code path. No numerical point rule was approved by Bento/Creto. There is no UV→XYZ, physical quadrilateral lifecycle, multipatch conformity, production dispatch, rollback or all-QUAD extension. The green M5 experiment is evidence of interface feasibility, **not of historical fidelity or M5 closure**.

Next: consult the original algorithm and existing Delaunay/contour implementation and replace the experimental fan in a distinct reviewed research PR, preserving the established native C++ QUAD geometry and seam-independent verification. The reproduction-hybrid-first and selectable-all-QUAD-second order remains unchanged.
