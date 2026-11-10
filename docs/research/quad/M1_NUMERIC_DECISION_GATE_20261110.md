# M1 numerical interior-point policy — decision record for Bento / Creto
**Date:** 2026-11-10. **Status:** open scientific decision, not an implementation specification.

## Evidence available now

The normalized schematic reconstruction proposes the six source patterns in Figure 7 order **T1, T2, T4, T3, T5, T6**, yielding **4, 11, 12, 8, 11, 16** theoretical quadrilateral subdivisions of their intermediate polygons. The new [executable exact-rational checker](../../../tests/quad/test_m1_figure7_oracle.py) and the existing [C++ UV emitter tests](../../../tests/quad/uv_contracts.cpp) validate this proposed interpretation under D4 symmetries. The Python checker is independently implemented but both artifacts depend on a human-transcribed graph; neither constitutes a second independent visual reading of the scanned paper.

Source provenance: Joaquim Bento Cavalcante Neto, Marcelo Tilio Monteiro de Carvalho and Luiz Fernando Martha, VI SIBGRAPI, 1993, p. 288, Figure 7; recorded local scan SHA-256 `49d297e24c1b8695e18c6d1307aa4ccbc39f14e265d251b840a16560aca98dc5`. The Drive copy has **not** been byte-hash verified against the scan.

## The unresolved mathematics

The surrounding text refers to a polygon centroid but does not specify which numerical formula or its behavior for a nonconvex/degenerate patch. The rational fixture demonstrates a real difference even on the agreed *schematic* coordinates:

| Proposed intermediate polygon | Mean of vertices | Signed-area centroid |
| --- | --- | --- |
| T2, A-B-O-W | (3/8, 1/4) | (7/18, 2/9) |
| T5, W-S-N-D | (1/4, 5/8) | (5/18, 11/18) |

On a convex polygon either point is interior; neither is an approved reconstruction of the 1993 algorithm. For a general nonconvex polygon a centroid may lie outside, and the current `Subdivide` routine requires strictly convex CCW input and a strictly interior caller-provided point.

The current production `MESH_ELEMENT_KIND=quad_uv` remains fail-closed. The isolated `UvMesh::Subdivide` research emitter has **caller-supplied** interior points. Its passing tests do not imply a chosen policy or a complete physical quadrilateral mesh.

## Decisions to record explicitly with the advisers

1. **Primary-source topology:** confirm the six Figure 7 polygon cycles, the non-obvious printed order `T1,T2,T4,T3,T5,T6`, and the absence of a junction O in T5 before treating the table as an approved historical oracle.
2. **Numerical point rule:** explicitly prefer vertex mean, signed-area centroid, a different historical formula, or a quality-constrained selector. Record its equation and analytic expected values for T2 ABOW and T5 WSND. Avoid choosing merely because both test witnesses passed.
3. **Admissible geometry:** state whether only strictly convex, consistently CCW source polygons are allowed; define behavior for nonconvex, collapsed, collinear, nonfinite and boundary-adjacent cases.
4. **Normalization and symmetry:** decide affine-translation, scale and D4 invariance requirements, including reflection winding and numerical tolerances.
5. **Boundary target (separate M5 decision):** select quad-dominant boundary triangulation or an all-quad strategy. The 1993 source does not guarantee all-quad boundary elements.
6. **Physical and ownership gates (M4–M7):** define UV→XYZ mapping, four-node face identity, normal/area quality, shared-curve neighbor synchronization, rollback/destruction and sanitizer obligations.

## Proposed next code acceptance gate (conditional on decisions)

Implement a narrow `PolygonPointSelector` candidate **only in research code**. Verify with independent exact expected coordinates, D4 transforms, strict interior/convexity and symmetry, the six pattern topology counts, 16 split masks and malformed negative inputs. Compare research output against an independently specified oracle rather than using the implementation as its own expected value. Require all native Linux/MSVC QUAD CTests, full TRI 78 CTest and 527 Python, Eistute/Book frozen OBJ/acceptance/boundary parity, post-merge exact SHA and preservation of `main`.

**Scientific status at this checkpoint:** M1 documentary graph has new executable corroboration, but M1 remains **PARTIAL** pending adviser confirmation and numerical-policy approval. M2/M3 remain partial; M4 onward not qualified. Do not publish physical QUAD results based on these test witnesses.

## Experimental code status — 2026-11-10

The two candidates now have independent C++ implementations in [experimental_point_rule.h](../../../research/quad/experimental_point_rule.h) and [experimental_point_rule.cpp](../../../research/quad/experimental_point_rule.cpp). The code **requires an explicit rule argument**; neither proposal becomes a runtime default, historical claim, or production change. Native Linux/MSVC CTest and frozen TRI reference equivalence passed in [PR #196](https://github.com/tiagosombrra/apmesh-modernization/pull/196), exact candidate Actions [#42851499408](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42851499408). This engineering evidence supports the computation of two precisely named alternatives; it **does not** resolve the mathematical/historical choice in this decision record.

For the next adviser meeting, the minimal approval record should identify: the approved Figure 7 graph/column mapping, rule equation, polygon orientation and convexity preconditions, the intended degeneracy/tolerance behavior, T2 ABOW and T5 WSND analytic expected values, and whether the desired boundary target is all-QUAD or QUAD-dominant. Until those are recorded, M1 remains PARTIAL, even though both test-only candidates execute correctly.
