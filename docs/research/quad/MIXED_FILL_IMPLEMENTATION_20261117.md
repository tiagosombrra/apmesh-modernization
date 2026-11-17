# Integrated mixed fill: implementation alignment - 2026-11-17

Classification: opt-in research implementation of the user-delegated
[physical-angle pairing policy](https://github.com/tiagosombrra/apmesh-modernization/blob/3cf8d215a712ef3dca6808ff22f7dec7d17e8d75/docs/research/quad/MIXED_FILL_PAIR_POLICY_20261117.md),
with an engineering-only empty-by-default AFT triangle observer. Default TRI and
previous QUAD cases retain their numerical selection, curves, quadtree/templates,
front reconstruction and adaptation/acceptance/stopping contracts. No stage
closure, merge, formal advisor sign-off or literal1993 identity is asserted.

## Live capability

`curved_bezier_live_pairs_vertex_mean_v1` is a separate serial experimental case.
It uses the same real source curves and native tree as the existing bounded-
domain case. `configs/quad/curved_patch_live_pairs.conf` fixes that source factor
at1.5; it introduces no new factor, point trimming or accepted-state controller.

The original AdvancingFront invokes a synchronous observer immediately after
owning each new triangle, in both ordinary geometry/topology emission and the
three-edge geometry shortcut. Endpoint pointers are borrowed for the call only;
no callback preserves the ordinary path. An observer exception aborts the
one-shot AFT attempt; its partial owner must be discarded, not resumed/published.

The research selector retains value site/triangle IDs and oriented edge uses.
At each triangle commit it evaluates available, previously emitted adjacent TRI
alternatives. Existing positive UV corner determinants and physical signed
corner/split-normal predicates precede S_XYZ<=1.5. Rank by minimum physical S,
then exact-tie edge ratio, current triangle edge order, source triangle and node
IDs. Each TRI is consumed at most once; unmatched valid TRI remain. No completed-
mesh matcher or lookahead to triangles that do not exist yet is used.

The original AFT TRI scaffold remains intact for frontier construction and its
coverage/overlap audit. Selection does not change the original vertex/edge
trajectory. This is bounded incremental pairing of that live trajectory; it is
not proof of every geometrical choice in the historical contraction algorithm.

## Physical ownership and source identities

Build one new owned physical candidate from native seed QUADs, selected AFT-pair
QUADs and unmatched TRI. Seed QUADs retain LeafPolygonOrigin; paired QUADs have
separate source-TRI pair provenance, never fabricated native-leaf origins.
Preserve original UV/XYZ, source node IDs and ordered shared-curve intervals.
Check facet/typed incidence, source boundary, oriented seam, coverage, Euler disk
and connectedness before the existing whole-SubMesh publication operation.
An injected failure after construction but before publication destroys only the
new candidate; retain the prior nonempty owner, observers and published output.
There is no mutation of two already-published physical TRI elements in place.

## Reviewable generation histories

Every source step still includes initial/accepted/rejected TRI and mixed OBJ.
The new case also exports an `_aft_source.obj` with the unchanged seed QUAD/TRI
scaffold. `live_pair_candidates.csv` records step/epoch/retry/domain identity,
source scaffold face IDs, current edge order, oriented four-node cycle, validity/
shape rejection, selected/not-selected/consumed status, physical score, edge ratio
and final paired face ID. `live_pair_stages.csv` reports seed/paired/retained
counts. OBJ AFT-pair comments independently identify the two source faces.

Existing boundary_pair_candidates/stages CSVs remain completed-source topology
inventories with selected0; the new-case scope says live selection is separate.
No-seed initial TRI is not an exterior AFT pairing success or an accepted mixed
epoch. Empty pair counts are reported as such, not used as success evidence.

## Validation and remaining scope

Native contracts cover shape/parameterization witnesses, bad physical/UV inputs,
competing alternatives, exact ties, malformed incidence and the shortcut/cleared/
throwing observer. Independent Python reconstructs every actual source candidate,
compares XYZ shape/validity, checks chosen ordering and disjoint consumption,
rebuilds expected physical faces and source provenance, and rejects forged IDs,
scores, final faces and generation/acceptance lineage. Normal/unpaired/rollback
histories compare original geometry, source intervals and owner preservation.
Same-site fixed-grid Bernstein error describes generated output; it is not an
acceptance rule, continuous error bound, global optimum or convergence proof.

Read canonical STATE.md and the session evidence for exact executed profiles,
source SHA, failures, regression and remote checks. A source inventory or prior
revision's85-test result does not qualify this selector. Preserve negative logs.

One active capability remains integrated mixed filling. Next, after its review
and applicable qualification, evaluate actual mixed accepted-state/error feedback,
then local curve/transition/interior balance. Source adaptation remains TRI-driven
and mixed_adaptive_epochs=0. M1 center identity, full M5/R3/M7, Doxygen/full CRT,
independent review and integration remain separate open obligations.
