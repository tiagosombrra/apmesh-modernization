# P2d-1c2 — original AFT physical reconstruction from second native source-error bands

Date: 2026-11-14. Research branch based on integrated P2d-1c1
[PR #233](https://github.com/tiagosombrra/apmesh-modernization/pull/233), merge
`15a57f3604c9fc8b072762ed10f3219aa12c9ad7`. Full R3/M7
[#221](https://github.com/tiagosombrra/apmesh-modernization/issues/221) remains OPEN.

## Scope and provenance

The real 62-QUAD / 44 native-AFT-TRI / 93-physical-node staged first band
(P2d-1b2) has a *new* error-selected worst AFT triangle #103 with sample near
UV (0.8,0.1). Prior source patch P1 (42 QUAD/36 TRI) had a different worst
AFT triangle #74 near UV (0.2,0.1). Both stages use the original real
Bezier source mapping, but a **fixed16 research boundary**, not full
production `Adapter::AdaptCurve`.

For each of the four source-native second-stage variants, begin with a *fresh
real native* `Quadtree` rebuilt to the already-refined **28-leaf first
band**, then select the real latest error source cell and its actual
west/north neighbors. Apply native `subdivideToLevel`,
`refineAccordingToNeighbors`, `CaptureLeafPolygons` and `EmitLeafQuads`.
For every admissible native disk, `Generate(patch, false, factory)` rebuilds
two identical yet separately owned source trees: one for the original TRI
reference `makeTemplateBasedMesh` front and the other for the original
`OwnedQuadAftFront::AttemptExteriorTriangulation` around real QUAD templates.

Only a complete mapped Bezier typed `SubMesh` with genuine four-node
`research::QuadrilateralAdaptive`, three-node `TriangleAdaptive`,
verified original 16 boundary edges, UV disk, no overlap, true positive
facet orientation/quality and drained original AFT front is exported.
Candidates are **research-only, unaccepted** at:

- `<output>.west.second-band-candidate.obj`
- `<output>.north.second-band-candidate.obj`
- `<output>.both.second-band-candidate.obj`

The isolated `corner` proposal is always rejected without publication.
Any AFT failure is reported by explicit
`QUAD_SECOND_PHYSICAL_AFT_REJECTION variant=<...>`, never silently treated
as real successful QUAD/TRI physical reconstruction. Previous P1 and staged
first-band typed owners and observer pointers remain unchanged.

## Independent admission and comparisons

The original application regression
`tests/quad/test_controlled_application.py` must independently read every
real emitted OBJ, verify source Bernstein XYZ and mapped facet orientation,
topology and original 16 boundary edges, typed face counts, QUAD
four-corner signed Jacobians, positive physical warpage and actual QUAD
UV area (not merely face count). For every positive candidate it computes
the **same original 64×64 UV midpoint sample set** using the independent
Bernstein source and true four-node bilinear QUAD interpolation. Report
the maximum error, uniform UV RMS, source-differential area-weighted RMS,
physical QUAD scaled-Jacobian/warpage and actual QUAD/TRI/node counts.

**Do not silently reject a physically valid candidate just because one
numeric metric is worse:** error/quality/complexity balance requires an
explicit later scientifically reviewed selection policy, not a single
magic threshold. Keep competing west/north/both alternatives and real
native rejections. The test demands at least one valid second-stage
physical original-AFT candidate on the *pinned controlled model* and
rejects a false-positive successful run with no produced candidate.
Its common-grid errors are discrete diagnostics, **not** rigorous
continuous source-error bounds or FEM PDE error.

## Qualification

This source change is initially UNQUALIFIED: no native application CI
was observed at design/commit stage. Required exact SHA CI must run
actual Linux GCC, Windows MSVC, Linux ASan/UBSan/leak controlled
original native AFT and independent Python/Bernstein OBJ oracle,
85 root CTests, 527 tooling Python controls and Eistute/Book original
frozen TRI scientific byte/acceptance parity. Keep a draft PR and
preserve complete failed outcomes.

Even a fully valid **second-stage physical proposal is NOT an accepted
adaptive epoch**: no prior *accepted* mixed owner has been adopted
between generations, no strong-exception-safe atomic accepted mixed
graph publication, no full original curve adaptation/production budget
policy, and no two accepted distinct QUAD/TRI epochs.
`adaptive_epochs=0`. No global nonmanifold sheet/welding decision,
historical 1993 equivalence, all-QUAD or anisotropy.
Next P2d-1c3: independently compare multiple source/quality/complexity
objectives and separately specify the typed previous-accepted-owner
transaction with fault injection and reproducible scientific policy.
