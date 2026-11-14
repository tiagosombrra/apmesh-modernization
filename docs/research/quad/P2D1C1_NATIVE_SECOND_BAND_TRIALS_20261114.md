# P2d-1c1 — actual native Quadtree alternatives after the first physical band

Date: 2026-11-14. Stacked on draft [P2d-1c0 PR232](https://github.com/tiagosombrra/apmesh-modernization/pull/232), whose source-grid oracle independently bounds topology; the first physical QUAD/AFT candidate and same-site source-error audit are in merged [PR229](https://github.com/tiagosombrra/apmesh-modernization/pull/229) and [PR231](https://github.com/tiagosombrra/apmesh-modernization/pull/231).

## Real source provenance and code path

The first full original native AFT physical candidate has 93 nodes, 62 actual QUAD and 44 original AFT TRI; its **measured new worst AFT error** is face103 near UV (0.8,0.1), not the earlier P1 face74 near (0.2,0.1).

In the original opt-in `ap_mesh` controlled real Bezier application, the **same existing 28-leaf connected three-cell first band is rebuilt** by `TrialConnectedAftBand(previous_original_error)`, then one distinct fresh native tree per alternative selects a real lower-right level-2 `QuadtreeCell` from the *current candidate's error sample* and resolves actual native west/north neighbors. This is **not** a new independent fixed template in place of the first refined tree. Exact source original dyadic coordinates, original native ID witnesses, object pointer/observer preservation, and three new/valid source-cell edit counts are asserted.

Four alternative proposed native Quadtree source modifications are executed with original `QuadtreeCell::subdivideToLevel`, original `refineAccordingToNeighbors`, `CaptureLeafPolygons` and `EmitLeafQuads`:

| Variant | Additional level-2 source-grid cells | Independent predicted leaves | Independent eligible UV area | Required native status |
| --- | --- | ---: | ---: | --- |
| corner | (3,0) | 31 | 22/64 = 34.375% | Reject disconnected/diagonal island |
| west | (3,0), (2,0) | 34 | 24/64 = 37.5% | Attempt native disk |
| north | (3,0), (3,1) | 34 | 24/64 = 37.5% | Attempt native disk |
| both | (3,0), (2,0), (3,1) | 37 | 26/64 = 40.625% | Attempt native disk |

The Python controlled-application regression validates four actual source-C++ native outcomes against `research/quad/p2d_next_band_dyadic.py` (independent from the native tree), including measured second source face/UV provenance, distinct native IDs, expected leaf count lower bound, UV area, genuine native emission or explicit refusal and original physical owner/node observer identity. An island must never be accepted; at least one bridge must genuinely emit a native disk before this scoped experiment can pass.

## Nonclaims and next gate

This is a **native source-domain trial only**. Actual second native exterior AFT physical TRI reconstruction, mapped Bezier 3D QUAD/TRI candidate, publication/rollback as a new `Patch/SubMesh` owner, two accepted previous-state-driven epochs, scientifically chosen error/quality/complexity acceptance criteria, full production `AdaptCurve` and historical1993 method are **not implemented**. No global nonmanifold Eistute/Book welding or all-QUAD/anisotropy is claimed. Must log `actual_second_aft_retriangulations=0 adaptive_epochs=0`.

Run exact-feature Linux/Windows native and complete application/independent source oracle, Linux ASan/UBSan/leak, 85 root CTests, 527 Python tooling and frozen Eistute/Book TRI scientific parity. **CI is not prequalified merely because this source exists**; any failed actual AFT/UV topology result must be retained and classified, not bypassed. Keep draft until qualified.

**P2d-1c2** after this gate: use each physically viable new native source tree for original `OwnedQuadAftFront` and typed Bezier XYZ output, independently measure same-site error against the first staged candidate, min scaled-Jacobian/warpage, element complexity and source boundary, then prepare an explicit scientific acceptance policy and strong-exception owner transaction. [R3/M7 issue221](https://github.com/tiagosombrra/apmesh-modernization/issues/221) remains OPEN.
