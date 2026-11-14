# P2d-1b0 — two real native Quadtree refinement trials (preflight)

**Date:** 2026-11-14. **Starting point:** qualified P2d-1a physical
mixed residual (PR #226), 42 original retained QUAD/36 AFT TRI.
**Research gate:** [R3/M7 issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).

## Scope of actual native execution

For the original source Bezier patch in the disabled-by-default serial
application, first construct the same original 69-node, 78-face typed physical
candidate as P2d-1a, and compute its true source approximation residual on
the real physical QUAD (bilinear) and original AFT TRI (barycentric).

With **two fresh independent native** `Par2DJMesh::AFT::Quadtree`
instances, select the actual leaf containing (a) the worst QUAD residual
sample, and (b) the worst AFT TRI residual sample. Subdivide exactly the
selected existing physical-source cell by one level, rebalance using the
original `Quadtree::refineAccordingToNeighbors`, then recapture its native
leaf polygons and attempt real `EmitLeafQuads` UV-disk validation.

Record for both separate trials the original native cell ID, resulting true
leaf count, permitted QUAD UV domain area, emitted physical-QUAD chart
**topology** status, and explicit exception/rejection if the topology cannot
be emitted. Rejected trials are recorded as **rejections**, not silently
admitted or retried with relaxed topology checks.

This is an original native **tree mutation on temporary candidates**,
not just a changed configuration constant. Both trees are destroyed before
any physical OBJ publication, and the original physical mixed SubMesh
node/element pointers and complete observer list order must remain
unchanged. The real native source boundary remains the original
fixed16 control and no existing output is overwritten.

## Topological risk explicitly tested

The original native `CaptureLeafPolygons` excludes every leaf with any
missing neighbor. The P1 domain has 25% QUAD UV area. Subdividing a
boundary-adjacent source leaf may create a previously excluded interior
grandchild whose eligible QUAD region touches the original central QUAD
area at a **vertex but not an edge**. This may violate the connected-disk
contract. Such a trial must be rejected, never published as an acceptable
disconnected/nonmanifold QUAD patch; the result determines the next
stitching/rebalanced-band experiment.

The previously measured worst AFT residual is ~17.7 times the worst QUAD
residual. Consequently, a passing *interior-only* real tree refinement
does not demonstrate reduction of global geometric error or QUAD UV
area coverage.

## Strict scientific nonclaims

**No AFT exterior re-triangulation is performed for these new trees**,
no new physical typed mesh is built from either trial, no second accepted
SubMesh owner is committed, and no new output OBJ results from a proposed
trial. **`native_trial_refinements=2 actual_adaptive_epochs=0`** counts
two genuinely modified temporary trees, never two accepted adaptive epochs.

P2d-1b1 must attempt complete native original AFT and physical reconstruction
for both options, verify new UV/XYZ/area coverage and quality separately,
and reject/rollback as appropriate. P2d-2/3 requires an adviser-reviewed
objective and at least two distinct accepted **history-dependent** mixed
mesh generations. The original `Adapter::AdaptCurve`, nonmanifold
high-valence weld, literal 1993 Delaunay method, all-QUAD and anisotropy
remain independent open scientific gates.

## Required checks

Exact-branch Linux GCC / Windows MSVC native and application tests,
the independent Bernstein/OBJ oracle, accepted candidate identity /
observer preservation, explicit negative-trial topology record, Linux
ASan/UBSan/leak, 85 root CTest/527 Python tooling (unless separately
qualified inventory changes), frozen Eistute/Book TRI parity. Keep a
draft PR until the exact source SHA meets all gates.
