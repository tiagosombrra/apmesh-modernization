# P2d-1b1 — native three-leaf connected boundary refinement band

Date: 2026-11-14. Parent: qualified P2d-1b0 PR #227.
Authoritative R3/M7 science issue: [#221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).

## Motivation and falsifiable claim

The actual one-cell source-tree edit selected by the highest-error
AFT TRI face in the controlled curved Bezier patch (native cell #6,
UV near (0.2, 0.1)) enlarged eligible QUAD UV area from 0.25 to
0.265625, but `EmitLeafQuads` correctly **rejected** the chart with
`Boundary vertex is not manifold`: a newly included boundary subcell
touches the original interior QUAD disk only at one vertex.

This trial tests a restricted source-compatible alternative:
on a **fresh original native Quadtree**, select the lower-left
source leaf containing the genuine maximum AFT error sample and
its two edge-adjacent level-2 source leaves one cell east and north,
toward the original interior QUAD region. Subdivide all three
real original leaves by one level and invoke the original native
`refineAccordingToNeighbors` 2:1 balance pass. Capture original
leaf polygons and attempt `EmitLeafQuads` for a connected,
non-self-overlapping admitted UV disk with the original boundary
and vertex-mean experimental interior point rule.

This is **not** an input-independent band algorithm: the exact
corner-source source depth, chart orientation, source cell ID #6
and fixed16 policy are checked. A failure is recorded explicitly
as a rejected trial, not bypassed through weakened manifold checks.

## What is and is not actually produced

The existing opt-in application still generates and eventually
publishes only its original typed 42 QUAD + 36 native AFT TRI
physical first candidate. The three-leaf trial takes only its
genuine measured AFT error sample and creates a **separate native
temporary Quadtree**. Its real source leaf IDs, mutations, resulting
leaf count, QUAD UV candidate area, number of emitted UV quads,
and disk status are reported. If the native emission is invalid,
the exact refusal is retained.

**No exterior AFT retriangulation, physical XYZ reconstruction,
new typed SubMesh, original `AdaptCurve` execution, accepted mesh
history, adaptive epoch or OBJ publication is performed for the
new band.** All earlier candidate owner pointers and observer
lists must remain identical; the original physical OBJ hash and
independent source oracle remain unchanged.
The log explicitly reports `actual_aft_retriangulations=0`
and `adaptive_epochs=0`, even if the band proves topologically viable.

## Required test and next steps

The independent Python application test must corroborate original
AFT sample provenance (face #74), three unique original source
cells, at least nine extra native leaves, preservation of the
physical candidate owner and a strict rejection reason on any
failed disk. The **qualified empirical result** is not to be
inferred before exact candidate CI. Linux/Windows native + real
application, ASan/UBSan/leak, strict frozen Eistute/Book TRI and
85 root CTests/527 Python controls are required.

If the band passes UV topology, a separate P2d-1b2 delivery
must reuse the **actual refined tree** to select/seed real
original AFT and construct a fully typed physical QUAD/TRI
candidate, then independently compare source-contour fidelity,
UV area, 3D quality, errors, and failure rollback. Only after
such gates can two real adaptive accepted epochs be considered.
Full R3/M7 is OPEN.
