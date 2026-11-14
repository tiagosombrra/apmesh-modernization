# P2d-1b2 — full original native AFT physical reconstruction on the connected band

Date: 2026-11-14. Qualified base: P2d-1b1 PR #228,
original curved `Models3d::ModelCurvaBezier` in opt-in serial
fixed16 QUAD mode. Canonical [R3/M7 #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).

## Exact experiment

The previous real typed 42-QUAD/36-TRI physical candidate determines
the maximum AFT source residual. The fully qualified UV-only native
tree band (original source cells 6,7,9; 19->28 leaves; 62 emitted
QUAD UV elements and 0.328125 eligible QUAD UV area) is reconstructed
**twice in independent fresh native trees**, one to run the exact
original `makeTemplateBasedMesh` reference interface, the other
to supply real QUAD templates to original
`OwnedQuadAftFront::Seed/AttemptExteriorTriangulation`.

If and only if original native AFT drains the advancing front,
the staged physical result is built as a real owned typed
`SubMesh` of Bezier XYZ vertices, four-node
`research::QuadrilateralAdaptive` and three-node
`TriangleAdaptive`. Original source parameterization,
orientations, 16 source boundary edges, mixed Euler/connectedness
and native UV non-overlap gates remain enabled. A unique
`<output_prefix>.band-candidate.obj` file is a **research
candidate only**, never the accepted `<output_prefix>.obj`.

In case of native AFT failure, numerical degeneration, incomplete
seam or any failed physical stage, the partial candidate is
destroyed and an explicit `QUAD_BAND_PHYSICAL_REJECTION` is
reported; the original first physical candidate, Patch owner,
all its pointers and observer lists remain unchanged.

## Independent checks and scientific admission limits

A separate Python/Bernstein oracle must read candidate OBJ **only
when present**, assert valid mixed TRI/QUAD edges and original
boundary, independently recover source XYZ, verify 3D facet
orientation, QUAD signed corner quality, and recompute all
native C++ QUAD/Triangle bilinear/barycentric sampled source
approximation errors. Candidate and first accepted OBJ must
never be confused. On rejected proposals no candidate OBJ
may exist.

Even if a candidate passes all checks, **no adapted epoch
has been accepted**: the sample still uses the original
fixed16 source, no production `Adapter::AdaptCurve`,
no source-SHA-bound model-wide continuation policy, no
research error/complexity acceptance threshold, no
atomic transition to the second accepted `Patch`/
`SubMesh` history owner and no proof for two distinct
adaptive generations.

An accepted research transition requires later explicit
scientific review of physical error/complexity and quality
trade-offs, immutable before-after hashes and a fault-injected
transaction across the previous typed graph and outputs.
This bounded PR only opens the gate to assessing whether
native AFT is capable of consuming the connected boundary
band. Full R3/M7 remains open.

## Required CI

Exact candidate Linux GCC and Windows MSVC native contracts,
real opt-in application, controlled failure/rollback,
independent physical source and objective checks,
Linux ASan/UBSan/leak, default TRI Eistute/Book
frozen equivalence, 85 baseline CTests and 527 Python
tooling controls. Keep this PR draft until exact-source CI
and source-independent review pass.
