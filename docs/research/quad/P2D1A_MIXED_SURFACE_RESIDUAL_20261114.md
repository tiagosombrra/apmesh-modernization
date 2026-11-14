# P2d-1a — real physical mixed surface residual and native leaf attribution

Date: 2026-11-14. Parent: P2d-0 metadata preflight (#223). Canonical
R3/M7 science gate: [#221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).

## What actually runs in ap_mesh

The existing opt-in serial fixed16/vertex-mean Bezier application constructs
the **same one-shot, real 42-QUAD + 36 native-AFT TRI** typed physical
candidate as P1 and P2a/b/c. Before its nonoverwriting OBJ export, P2d-1a
now computes a physical source-surface interpolation error for every real
3- or 4-node ElementAdaptive using the originally evaluated Bezier
\`PatchBezier::Parameterize\`.

For a physical TRI, the local interpolant at UV barycentric weights
\`(w0,w1,w2)\` is \`Σ wk * XYZ_k\`; the source location is the matching
\`Σ wk * UV_k\`. The fixed transparent quadrature rule has four samples:
\`(1/3,1/3,1/3), (0.6,0.2,0.2)\` and its two cyclic rotations.

For a physical QUAD **no triangle conversion occurs**. The local
interpolant uses the genuine four-corner bilinear weights
\`((1-s)(1-t), s(1-t), st, (1-s)t)\`. Source UV is the *same bilinear*
weighted sum of the four UV corners. The fixed sample nodes are the
bilinear center and four interior quarter locations.

The indicator is the Euclidean XYZ distance to the original source
surface at each sample, in the model's physical length unit.
The report stores maximum source residual by type, global maximum,
sampled RMS, sample count, and the **earliest face index** attaining
the largest QUAD residual (stable tie-break). The selected face's
existing, original \`InteriorTemplateSelection::quad_face_origins\`
provides the actual native quadtree cell ID, leaf ordinal and depth.
This is a *read-only leaf selection from the previously constructed
physical mesh*. There is **no quadtree mutation**, re-AFT, adaptive
reconstruction or accepted epoch in this delivery.

## Independent checks

- Strict Linux/Windows C++17 native contracts: a known curved polynomial
  source, a planar zero-residual source, deterministic tie selection, and
  **14 malformed negative controls**, including stale vertex indices,
  missing element types, nonfinite source and coordinate mutations.
- Real Linux/Windows opt-in app: independent Python parses only exported
  OBJ UV/XYZ/faces and evaluates the separately versioned analytic
  Bernstein source \`golden()\`, with the explicit bilinear and barycentric
  weights. It checks all reported error values, sample count, selected
  face/sample UV and identical metrics after the existing physical
  publication rollback.
- Inherited P2a clone/fault injection, P2b mixed vertex topology and
  angle defect, P2c positive physical QUAD corner Jacobian / warpage,
  immutable output behavior, ASan/UBSan/leak, frozen TRI equivalence
  and native/root CTest / Python tooling remain required gates.
- Strict build/source inventory must be regenerated from the **actual**
  modified CMakeLists and checked; a hash update is not a waiver.

## Scientific limitations and next real adaptation

A finite fixed sparse quadrature residual is an **indicator**, not a
certified maximum surface error or best error estimator. One sample
array per element is not an approved stopping tolerance, the
original source boundary still has exactly 16 fixed intervals and
there is no approved 1993 point rule, high-valence weld, all-QUAD
or anisotropy. A larger QUAD residual does not by itself prove that
refining its source leaf improves global error or mesh efficiency.
No normalized cross-model error metric or error/complexity tradeoff
has been approved. \`real_tree_edits=0 adaptive_epochs=0\` is mandated.

P2d-1b must use the accepted previous-mesh residual to select a
**new genuine native Quadtree refinement**, run the original AFT and
typed physical reconstruction again, reject unchanged topology, and
compare independently measured before/after errors. P2d-2/3 then
require a reviewed acceptance policy, explicit actual owner/observer
transaction and **two distinct accepted adapted** QUAD/TRI epochs.
These are distinct future deliveries and the R3/M7 issue stays open.
