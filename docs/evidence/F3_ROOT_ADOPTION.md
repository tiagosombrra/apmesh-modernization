# F3 initial quadtree root adoption

Classification: behavior-changing defect repair on an allocation-failure exit.
Entry is PR #179 main `c9b26cc462ae041089f5c036a45ce7a49743e205`.
The [compact record](stage3/f3_root_adoption/summary.json) binds the original
failure, current source/images, native results and remaining package obligations.
This delivery addresses one admitted operation in F3-02 and records the current
F3-01/F3-03 boundaries. F3 and Stage 3 remain open.

## Ownership and admitted operation

The roles below come from the current destructors and assignments, before the
setter repair. They describe implementation obligations, not newly promised
arbitrary alias or replacement support.

| Relationship | Current owner / observer and limit |
| --- | --- |
| Default AdvancingFront | Owns its Quadtree; its Boundary pointer observes the boundary owned by that tree. |
| Pointer-taking AdvancingFront | Destructor deletes the supplied Quadtree. Its separately assigned Boundary is observed; correspondence with the tree is not checked. |
| Quadtree with nonnull Boundary | Deletes that boundary, its root cell and the root minimum/maximum vertices. Cell children/midpoints are owned recursively by cells. |
| Quadtree with null Boundary | Still deletes its root cell, but does not delete root minimum/maximum. The historical mate comment describes shared endpoints/boundary, not permission to delete the same root cell twice. |
| Front/tree setBoundary and front setQuadtree | Raw assignments; displaced owners and foreign/mismatched graphs have no new lifetime guarantee. |
| Quadtree setRoot | Assumes the supplied cell after successful adoption and registers borrowed leaves. It does not retire a displaced root. Null assignment retains its historical leaf behavior. |
| Template lists | Tree owns pending template vertices/edges/faces; front owns the transferred lists after TransferTemplateMesh. Cell/front views borrow. |

The admitted graph is exactly the existing TreeFixture stage 1 arrangement: one
boundary vertex, a tree owning that boundary, a caller-owned root cell borrowing
caller-owned (0,0)/(1,1) endpoints, and an initially null tree root with no leaves.
All three pending owners are released only after setRoot succeeds. No replacement
root, shared cell, mate graph, new model, forced selector or parameter search is
introduced to obtain coverage.

## Original failure and production repair

The original setter assigned its root before constructing/traversing the breadth
queue and rebuilding leaves. The first measured Debug CRT denial therefore left
the tree pointing to the root still owned by the caller. The original native
contract exits 1 with root_published_after_denial=1. It stops before destroying
the invalid double-owner arrangement; this establishes premature publication,
not an independently observed double-delete or complete old-ordinal sweep.

The repair builds a local leaf list, preserving the original breadth-first child
order, then swaps that complete observer list into place and assigns the root.
An exception before commit leaves the original tree state untouched. Successful
adoption preserves pointer identity; null assignment and displaced-root lifetime
semantics are unchanged. No formula, scientific ordering or policy changes.
The production diff is confined to setRoot, and explicit formatting makes no
additional production change.

Debug CRT measures four allocations in the original successful initial adoption
and six in the repaired operation. These are measured costs, not portable budgets
or a performance improvement. Every current ordinal is denied once in each of
two fresh histories: abandon the pending owners, or retry this helper and adopt
the exact same root/endpoints. All 12 denials propagate std::bad_alloc; root and
leaves remain unpublished after failure, and final normal CRT blocks/bytes are
zero. This permits retry only of this initial helper, not of failed generation.

## Finite current validation

The existing application.uv_tree_contracts target includes successful adoption
and exact pointer/leaf checks. Original/current complete tree traces match byte
for byte under MSVC ASan and checked Debug CRT, including the five existing tree
generation/refinement histories. Separate current native gates require:

- 20 expected ASan/CRT outcomes: tree, lifecycle, registration and unowned-cell
  contracts; the initial-adoption sweep; existing allocation hook, allocation-free
  teardown, complete transfer-membership sweep and five tree-denial sweeps; actual
  UAF/shared-delete/leak negative controls.
- Six original analytic UV contexts under checked MSVC: 17 prefix outcomes and
  12 completed calls with exact observed/unobserved topology, IDs, positive area,
  native smoothing and pointer transfer into emptied source owners. Current GCC
  repeats this required matrix through its existing CTest entry. Guard-only and
  missing-curve outcomes retain their distinct classifications.
- Fresh Eistute/Book comparisons under GCC and MSVC using the original inputs,
  caps, independent boundary checks and frozen accepted/rejected traces. A changed
  application image is not qualified through an old executable hash.
- Configured analysis of the full production unit and all added positive fixture
  lines with actual GCC/checked-MSVC compile metadata. Deliberate invalid probe
  modes remain negative evidence outside the positive analysis scope.
- All 75 CTest / 526 Python on exact delivery head and merged main, architecture,
  contracts, whitespace, fresh remote checks and guarded same-tree main checkout.

The first local controller marked the successful root sweep failed because it
tested concatenated stdout/stderr for a final PASS: expected CRT denial messages
followed stdout. Its report and both streams remain unchanged. Independent raw
reclassification requires exit 0, all 12 actual denials, unpublished state and zero
retention. Only the 11 unstarted cases continue; no completed native child is
repeated. An unstarted analysis tool-path error is separately retained before
selecting the configured absolute executable. No diagnostic, cap or gate is relaxed.

## Closure audit and remaining package

Code: initial root adoption now commits ownership only after observer preparation.
Tests/contracts: successful identity and order, abandonment, helper-local retry,
terminal template cleanup and actual negative controls remain distinct.
Documentation: this record, the finite register, state/plan, quality requirements,
closure inventory, sequence and C10 describe the same bounded operation.
Scientific scope: 521 other protected source/build/input files and 43 original
retained-block artifacts stay exact; changed native application images require
fresh frozen comparisons. No alternative generator, arithmetic, acceptance,
boundary synchronization or smoothing policy changes.

F3-01 retains only its six admitted successful caller contexts and boundary-state
guards. F3-02 remains partial: replacing owners, pointer-constructor mismatches
and mate/shared endpoint destruction orders need an admitted native history and
independent observation. F3-03 preserves destruction after actual allocation
failure and the existing injected public geometry false-return, exception and
topology-failure controls; those injections are not naturally reached scientific
rejections, and safe destruction does not prove whole-tree query/retry/rollback.
F5 retains orchestration/recovery obligations. F3-04 remains admission-blocked,
with prior zero reach and rejected calibration preserved. F2 corpus dependencies,
F4 observers, whole-process instruments/domain/parallel and final F8 stay open.

The local build/f3-root-adoption/delivery/integration-verification.json receipt
must bind actual final head/main results before this bounded repair is integrated.
This document alone does not close the package, an original row or Stage 3.
