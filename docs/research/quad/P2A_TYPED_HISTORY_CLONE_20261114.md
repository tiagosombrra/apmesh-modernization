# P2a — Typed QUAD/TRI history-clone admission gate (research)

Date: 2026-11-14. Base: canonical `quad-templates` after PR #217.

## Precise scope

This change adds a **real in-memory owned** mixed `SubMesh` clone rehearsal to the
existing default-OFF, serial, fixed16/vertex-mean curved Bézier application case.
It does not make a second adaptive mesh, refine the accepted tree, call
`GeneratorAdaptive` or `Adapter::AdaptCurve`, publish a multi-patch model, or
claim an accepted QUAD adaptive epoch.

Before and after a transient `Patch::SetSubMesh` rebind, the probe checks:

- 69 physical `NodeAdaptive` objects and every reconstructed
  `TriangleAdaptive` / `research::QuadrilateralAdaptive` against their
  explicit 3-/4-vertex topology and stored UV parameter correspondence;
- stable node IDs and copied analytical/discrete curvature scalar fields;
- typed element identities, independent node/element addresses and physical
  area equivalence;
- complete, local and duplicate-free node-to-element observer incidence;
- exception-safe restoration of the original `Patch` forward observer;
- deterministic failure **after seven cloned elements** have registered their
  observers, with full partial-graph teardown and unchanged accepted graph;
- original accepted node/element addresses and observer sequences restored
  after the transient clone is destroyed.

The original non-overwriting OBJ export remains unchanged. The textual gate
`QUAD_TYPED_HISTORY_CLONE accepted_clone=1 partial_failure_rollback=1
source_observers_preserved=1 adaptive_epochs=0` is verified by
`tests/quad/test_controlled_application.py`, alongside its existing
independent Bézier/UV/XYZ, original-boundary and file-rollback controls.

## What cannot be claimed

Passing P2a only qualifies the **typed history ownership prerequisite** in one
controlled curved chart. A clone of the same 78 faces cannot count as a new
adaptive state. The original configuration's QUAD/TRI counts, 16 boundary
segments, AFT exterior, source curves and default TRI path remain unchanged.
No continuous Jacobian, positive-metric quadrilateral Jacobian, memory-fault
campaign, general input geometry or Windows CRT lifecycle proof is added.

## P2/R3 remaining acceptance contract

1. Represent successive accepted mixed `SubMesh` owners with an explicit
   attempt/epoch ID; distinguish candidates, rejection and commit.
2. Drive at least two **different accepted** mixed meshes using estimates or
   quality of the previous accepted mesh; keep the original curve/boundary
   policy and pin the adaptation estimator before scientific comparisons.
3. Dispatch curvature, quality, reconstruction, smoothing and export by actual
   element type, not assumed three-node `TriangleAdaptive` slots.
4. Enforce global patch-local UV coverage, physical geometry, numerical
   quality, identity, observer, rollback and nonoverwriting output gates in
   **each** accepted epoch, with independent negative controls.
5. Run exact-revision Linux/Windows native and application tests, frozen TRI
   Eistute/Book scientific equivalence, root CTest/Python and sanitizer tests.
   Keep the PR draft until these gates qualify the actual tested SHA.

Neither approved high-valence sheet welding, literal 1993 centroid/Delaunay,
all-QUAD nor anisotropy is implied.
