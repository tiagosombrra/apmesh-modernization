# Stage 3 slice 15 closure: Generator curve sample publication

Issue #50, implementation PR #51. Qualified head `7e9a36b80f6104bbe68724d462b71dc140149168` integrated
as main `943ccf7b6d85397af6297b69ee97423d2a46311d`, complete tree `42cd9c3124691b5426b515f713a60fd7dad1386d`
(1640 blobs). Both exact-revision full campaigns pass;
534 protected input bytes share SHA256 `60d61364d52ca31c4ae60a497ac176df448af679ee130ecabf325dff19ad2430`.

## Explicit closure audit

| Boundary | Result and remaining limitation |
| --- | --- |
| Code and ownership | Actual publication template preserves curve/surface/optional-rebuild sequence. Collective RAII owns newly returned lists before SetPoints copies. Parked originals and cache snapshot permit nonallocating restoration; cache entry nodes remain stable. Borrowed source/cache samples and final graph ownership remain explicit. Rebuild-deleted interiors are not consumed during cleanup. |
| Tests and controls | CTest 25/25, no skips, 74 Python controls. Publication 139/139: 54 normal, 27 positive sweeps/2403 denials, 54 upstream abort/restore/retry, four actual list-move/UAF/leak/hook controls. No allocations after any denied request; final denied publication follows all requested IDs. Analytic interiors, three curve types, grow/shrink/equal/no rebuild, alias/cache/closed/reversed/two-endpoint layouts, borrowed fields/adjacency and exact list/cache nodes measured. |
| Original failure inventory | 27 allocation sweeps and 54 aborts stop at partial-publication assertions; subsequent unsafe consumption, later ordinals and CRT retention are unmeasured. Other 58 outcomes expected. All 54 full normal logs match. Sixteen pinned units plus verified block adapter with controlled callbacks; not full historical Generator/Adapter instrumentation or upstream numerical selection. |
| Prior regression | Samples 88, rebuild 117, snapshots 89, sync 73, adoption 53, copy 30, curve 19, UV 81, node seven instrument outcomes all pass on exact implementation head and main. Deliberate negative controls remain required. |
| Contracts and documentation | C07/ADR-0016 define actual pass/default allocator/fixed comparator/no erase/no concurrent consumption constraints and borrowed/owned roles. C12 whole-rollback limitations remain. State, plan, ledger, sequence, quality, README and this audit updated; no parallel authority. |
| Tooling and history | New-unit read-only tidy, explicit format and inventory pass: 133 production files, 62 units, 71 headers; 22 contracts/113 anchors, existing six-header cycle retained. New target consistently disables optional NRVO and Debug iterator metadata; actual heap checks and prior settings remain. Initial configuration, fixture zero-ID assertion, preliminary pass and stale-inventory failures are retained, not relabeled. |
| Numerical/accepted/rejected states | Twice-repeated Eistute/Book results equal entry and head/main: all nine attempted OBJ/acceptance/rejection/incidence states, 189 CSV fields, positive shared-boundary coverage/zero gaps. Accepted steps 0/1; rejected Eistute 2/3/4, Book 2/3; final accepted triangles 1,168/4,256. No new entry campaign claimed; entry's 530 protected input hashes match prior qualification. |
| Scientific scope | Failure-path ownership/exception-consistency defect repair and success-preserving engineering consolidation. No formulas/float order/selection/synchronization/templates/front reconstruction/tolerance/budget/verifier/adaptation/acceptance/stopping changes. Distinct parametric/physical roles, historical/vendor sources and attribution preserved. |
| Resources | Working copies/cache snapshot and removed unused vector/late keep-set change allocation timing/counts/bytes/peak storage. Counts are calibrated observations, not portable constants, performance claims or scientific budgets. |
| Open inventory | Earlier successful curves/initial graph cleanup on later failure, upstream selection/evaluator scratch, whole Adapter/AdaptCurve/patch/mesh/error/history/budget/acceptance rollback, other helpers/custom sources/UV/tree/mate paths, failed-tree observer reuse, explicit disabled-sync full CLI, full-process/parallel/LSan/UBSan and stage-8 Doxygen API debt stay unqualified. |

Per-curve publication now parks original point/parameter list nodes after all
entry preparation, snapshots cache values and owns both returned lists before
allocating point-observer copies. The curve pass, surface pass and optional
target rebuild retain their order and numerical inputs. Rollback erases only new
cache keys, restores existing values in place, deduplicates/deletes new samples
without allocation and restores original point/parameter nodes. Entry samples
and preexisting cache values stay borrowed, including shared endpoints. Rebuild
may already have deleted discarded surface interiors; rollback never consumes
those stale curve observers. Commit deletes superseded first-pass samples and
transfers final samples to the existing collective graph lifetime. The unused
result-vector storage and late allocating keep-set are removed explicitly.

Publication 139/139: 54 normal ASan/CRT outcomes, 27 positive calibrated sweeps
denying 2403 allocations, 54 controlled upstream abort/restore/retry outcomes,
and four list-move/UAF/leak/hook controls. Every denied ordinal propagates once;
attempts equal ordinal+1, requiring allocation-free rollback. Final denied
publication follows all expected ID requests, including growth/shrink/equal/no
rebuild, cached/closed/reversed/two-endpoint and alias-overwrite fixtures across
three actual curve types. Independent interior polynomial geometry and borrowed
scalar/adjacency state, point/parameter/cache entry identity and successful retry
are required. Consumed IDs stay consumed; cached two-endpoint first passes
correctly request zero. All 54 normal complete original/repaired traces match.

Original: 27 allocation sweeps and 54 controlled upstream aborts stop at the
first partial-publication assertion; later unsafe observer consumption, later
ordinals and CRT retention in aborted cases are unmeasured. Other 58 outcomes
are expected. Sixteen pinned production units plus a verified publication-block
adapter are compared against seventeen actual candidate units plus the actual
publication template. Callbacks use actual sample/rebuild units, controlled
parameters and a controlled upstream point-list reversal; full historical
Generator/Adapter TUs and upstream numerical selection are not instrumented.
Original unused storage is rebound to a one-curve vector initialized within the
fixture operation; allocation timing/counts/bytes/peak storage change explicitly,
without a performance claim. Only the new target consistently disables optional
NRVO and Debug iterator metadata, retaining actual CRT heap and negative controls.

Required prior batteries: samples 88/88, rebuild 117/117, snapshots 89/89,
sync 73/73, adoption 53/53, copy 30/30, curve 19/19, UV 81/81, node 7/7.
CTest 25/25, zero skips, 74 Python controls; new-unit read-only lint, explicit
formatting and inventory pass (133 production files, 62 units, 71 headers;
22 contracts/113 anchors; existing six-header cycle retained). Two repetitions
per Eistute/Book preserve all nine attempted OBJ/acceptance/rejection/incidence
states, 189 CSV fields and 1,168/4,256 last-accepted triangles exactly.

Classification: behavior-changing ownership/exception-consistency defect repair
on failure paths, with success-preserving engineering consolidation. No scientific
formula, float order, numerical selection, synchronization, quadtree/templates,
front reconstruction, tolerance, budget, verifier or adaptation/acceptance/stopping
change. Source/history/licenses are preserved. C07 and ADR-0016 delimit this
boundary; evaluator scratch, previous successful curves, initial graph cleanup
and full Adapter/AdaptCurve/patch/mesh/history/budget rollback remain unqualified.

Full stage 3 remains open with fifteen qualified slices. Next address collective
sample ownership and cleanup across the complete AdaptCurve loop, including
earlier committed curves and the initial graph when a later curve fails; then
upstream/full adaptive retry and rollback across parameters, patch/mesh observers
and error/history/budget/acceptance state, plus explicit full CLI disabled
synchronization. Per-curve publication is a measured boundary, not a whole
Adapter/AdaptCurve/mesh transaction. Evaluator scratch, other constructors,
custom sources, helper/template/tree/mate paths, failed-tree observer reuse and
full-process/parallel/LSan/UBSan remain open. Stages 0-2 stay closed for measured
scope; stages 4-11 pending. Doxygen undocumented-API debt remains stage 8.

Reports, commands, source/executable identities, original extraction and raw-log
hashes live under stage3/curve_publication/. Exact documentation-head/main must
preserve all 534 compiled/tool/test/build/input/contract identities and pass
complete Git/working-byte audit, rebuild/CTest 25/25/no skips/74 controls and
inventory/whitespace gates. Retained full head/main numerical/instrument campaigns
remain tied to unchanged inputs; no fresh such execution is claimed for this
documentation-only follow-up. Final hashes/receipts belong on the PRs/issue to
avoid self-referential evidence commits.
