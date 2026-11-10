# M1 bounded experimental point selectors — 2026-11-10

Status: **research-only proposal**. No historical point formula approved; M1 is still partial.

Two explicitly named and mutually exclusive numerical witness functions were added in a separate `apmesh_quad_experimental_point` static target:
- `ExperimentalPointRule::VertexArithmeticMean` — arithmetic mean over original polygon vertices.
- `ExperimentalPointRule::PolygonAreaCentroid` — convex polygon signed-area centroid, computed by local fan-triangle moments.

The API `ExperimentalInteriorPoint(polygon, rule, relative_tolerance)` requires the caller to supply a rule. There is **no default enumeration choice, environment variable, implicit call in `Subdivide`, hook installation, or connection to the TRI application**. The caller still supplies the point to the existing validated `UvMesh::Subdivide`. Invalid or unsupported geometry fails closed with `std::invalid_argument`.

Numerical scope: strictly convex CCW polygon, finite unique coordinates with positive relative-scale-dependent area, strictly interior returned point, translated local arithmetic to reduce cancellation, and explicit finite-output checks. This does not establish a robust predicate for arbitrary magnitudes, nonconvex polygons, or historical curvature-based patch quality. The two formulas may differ on otherwise valid convex polygons.

The independently pinned golden coordinates in the proposed 1993 Figure 7 transcription remain:
- T2 ABOW: vertex mean `(3/8,1/4)` vs area centroid `(7/18,2/9)`.
- T5 WSND: vertex mean `(1/4,5/8)` vs area centroid `(5/18,11/18)`.

The new standalone C++ test `quad.m1.experimental_point_witnesses` exercises both rules on all six proposed Figure 7 templates and their D4 transforms (96 candidate witness subdivisions), tests these independent golden values, scale/translation invariance, original input immutability and negative invalid/degenerate/tolerance conditions. The existing independent exact-rational Python oracle remains enabled. The standalone QUAD native test count increases from 5 to 6 on GCC/MSVC. This is **not** a claim of 96 production meshes, a signed-off graph transcription or a selected publication-quality point rule.

Scientific admission is withheld pending Bento/Creto's review of Figure 7 graph/order, the numerical point-selection rule and allowed degeneracy/boundary behavior. No positive `MESH_ELEMENT_KIND=quad_uv` is enabled; no UV→XYZ, physical four-node faces, shared patch boundaries, OpenMP runtime or sanitizer qualification is claimed.

## Exact-head qualification and integration receipt

- Scoped [PR #196](https://github.com/tiagosombrra/apmesh-modernization/pull/196), source `10065b24a7a4ae5a93dafc743a8324f5bf058975`, merged into research `quad-templates` as `720309b4b153b5695a5afcb81aa9a967a17aaa0e`; merge tree equals tested feature. Modernization `main` unchanged.
- [Pre-merge GitHub Actions #42851499408](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42851499408) **SUCCESS** four jobs: Linux GCC and Windows MSVC **6/6 native QUAD CTest each**, root TRI **78/78 CTest**, Python **527/527**, CLI rejects **7/7**, strict Eistute 5 and Book 4 states (OBJ bytes, acceptance, boundary incidence).
- [Post-merge #42853155958](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42853155958) in_progress at checkpoint; verify exact merge SHA before declaring postmerge closure.
- The final tests additionally reject concave, collinear and almost-degenerate input. No default scientific rule, no physical QUAD emission, no production behavioral change.
