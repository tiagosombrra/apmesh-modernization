# Stage 3 slice 16 closure: complete curve sample graph ownership

Issue #53, implementation PR #54. Exact head `8eaeb09fa8137ed32dea5549b4ac07b923d5bac2` integrated
as main `186ef0251f460f3139baedae4ed77f30a2b9695b`, complete tree `0aef3cdf1d5fb1cb9075062cebfb74f68106dabf`
(1678 blobs). Full head/main campaigns pass with 538
protected input files, SHA256 `66fb9782f442a3a5bd8f054e7ff571b33ca9bdce81f507a9a48ff88838032f33`.

## Explicit closure audit

| Boundary | Result and remaining limitation |
| --- | --- |
| Code/ownership | Whole serial scope prepares equivalent working lists and initial set before parking original nodes. Initial samples stay alive across all curve prefixes. Inner guards unwind before outer cache/alias cleanup and unique deletion of new graph samples. Original point/parameter nodes/sharing restore without allocation. Successful full commit retires original samples once; final graph retains caller lifetime. Fixed topology, no competing owners and actual qualified inner operations required. |
| Tests/controls | CTest 26/26/no skips/74 controls; graph 156/156, 8118 calibrated denials over 18 sweeps, 36 normal traces with repeated operations, 78 early/prefix/surface abort/restore/retry outcomes, 18 retention-only cases, two empty-graph guards and four actual list-move/UAF/leak/hook controls. Final denial occurs after three committed curves/all ID requests; every denied request propagates once with no later rollback allocations. |
| Graph/domain coverage | Four curves, actual parametric/Bezier/Hermite and mixed graphs, non-manifold/shared/reversed/closed/distinct/two-endpoint layouts, all prefix lengths and a later graph from actual samples. Independent polynomial interiors, sampled-node fields/adjacency, exact original point/parameter nodes and independent physical SubMesh copies/triangle observers measured. Empty graph is guard-only; closed/reversed fixtures preserve policy/ownership without geometric consistency certification. |
| Original failures | 18 allocation sweeps and 60 controlled aborts stop at partial restoration assertions; later ordinals/unsafe consumption and aborted-case CRT retention unmeasured. Eighteen independent retention-only experiments reclaim current reachable samples and leave 1-6 orphans/3-12 CRT blocks each; no original rollback/retry claim. Other 60 outcomes expected. All 36 normal full observed logs match. |
| Provenance/instrument | 470 pinned source/header/vendor blobs and verbatim initial-capture/final-retirement blocks verified. Nineteen original units plus interface adapter, twenty actual candidate units, actual inner helpers/controlled callbacks. Full historical Generator/Adapter TUs/upstream numerical selection not instrumented. New optional NRVO/Debug iterator-metadata settings consistent; actual heap checks and previous target settings retained. |
| Prior gates | Publication 139, samples 88, rebuild 117, snapshots 89, sync 73, adoption 53, copy 30, curve 19, UV 81, node seven all pass on exact implementation head/main with deliberate negative controls. |
| Contracts/docs/quality | C07/ADR-0017 distinguish graph lifetime from orchestration rollback. State, plan, ledger, sequence, quality and README consolidated. Actual new-unit read-only tidy and explicit formatting/inventory/whitespace pass: 135 files, 63 units, 72 headers, 22 contracts/117 anchors; existing six-header cycle remains. Fixture compilation failures and the preliminary PowerShell diagnostic remain recorded without importing a gate pass. Compact reports retain outcomes/commands/hashes; full raw local reports/logs retain observations. |
| Numerical regression | Two repetitions per Eistute/Book; all nine attempted OBJ/acceptance/rejection/incidence states and 189 CSV fields exact to entry and head/main, positive shared coverage/zero gaps. Accepted steps 0/1; rejected Eistute 2/3/4, Book 2/3; final accepted triangles 1,168/4,256. Entry reused the prior full qualification after verifying all 534 entry input hashes; no fresh entry campaign claimed. |
| Scientific scope/resources | Behavior-changing lifecycle/exception-consistency repair with success-preserving engineering consolidation. No formulas/float order/selection/synchronization/templates/front/tolerance/budget/verifier/adaptation/acceptance/stopping change. Working copies/set/capture lifetime/cache cleanup change resource timing/counts/bytes/peak storage; no performance or unchanged-allocation claim. Historical/vendor sources/licenses and parametric/physical roles preserved. |
| Open inventory | Consumed IDs/evaluator scratch and orchestration metadata/targets/error/history/budget/patch/mesh/acceptance rollback, whole adaptive retry, explicit disabled-sync full CLI, other construction/custom sources/UV/tree/mate paths and failed-tree reuse, full-process/parallel/LSan/UBSan and stage-8 Doxygen API debt remain unqualified. |

CurveSampleGraphTransaction now spans serial AdaptCurve preparation/policy and
the complete curve loop. All equivalent working point/parameter lists and the
deduplicated initial sample inventory are prepared before original nodes are
parked. Initial sample objects remain alive across successful per-curve prefixes.
After inner guards unwind, failure clears the operation-local cache, clears every
new shared graph alias before deletion, reclaims each new sample once without
allocating and restores every original point/parameter list node and shared
object. Success retires initial samples once after the complete loop, in the
existing unordered-set capture/iteration convention, and leaves final graph
lifetime with the caller. Per-curve sampling/publication/rebuild code is unchanged.

Graph qualification passes 156/156 outcomes: 36 complete normal ASan/CRT traces
(two visible operations each), 18 positive allocation sweeps/8118 denials,
78 controlled abort/restore/retry outcomes, 18 retention-only cases, two explicit
empty-graph guards and four actual list-move/UAF/leak/hook controls. Every denied
allocation propagates once; attempts equal ordinal+1, requiring no rollback
allocation. Final denial follows three committed curves and all expected ID
requests. Four-curve fixtures cover three initialized actual curve types and
mixed graphs, shared non-manifold/closed/reversed/distinct/two-endpoint layouts,
prefix lengths one through four, inner surface failure, early failure, actual
analytic interior samples, independent physical mesh copies/adjacency and a
later operation whose initial samples were generated by actual production code.
Original point/parameter list nodes, all sample fields/sharing and successful
retry are checked. Consumed IDs stay consumed; evaluator scratch and orchestration
metadata are not rolled back. Empty geometry is guard-only, not positive coverage.

Original: 18 strict allocation sweeps and 60 controlled aborts stop at partial
graph-restoration assertions. Later ordinals/unsafe observer consumption and CRT
retention in those aborted cases are unmeasured. Eighteen separate retention-only
experiments reclaim current reachable graph samples only and leave 1-6 orphaned
entry samples, with 3-12 retained CRT blocks each. They make no restoration/retry
claim. Other 60 original outcomes are expected. All 36 normal full observed logs
match repaired logs. Verbatim original capture/retirement blocks wrap the original
map/set storage with 19 Git-pinned production units; candidate uses 20 actual
units. The controlled driver calls actual per-curve publication/sample/rebuild
operations, not full historical Generator/Adapter TUs or upstream selection.

CTest 26/26, zero skips and 74 Python controls; all ten prior batteries pass:
publication 139, samples 88, rebuild 117, snapshots 89, synchronization 73,
adoption 53, copy 30, curve 19, UV 81, node seven. Read-only new-unit lint,
explicit formatting and inventory pass: 135 production files, 63 units, 72 headers,
22 contracts/117 anchors; existing six-header cycle retained. Twice-repeated
Eistute/Book comparisons preserve all nine attempted OBJ/acceptance/rejection/
incidence states, 189 CSV fields and 1,168/4,256 last-accepted triangles exactly.
Only the new target consistently disables optional NRVO/Debug iterator metadata;
actual heap checks/negative controls and prior target settings remain unchanged.

Classification: behavior-changing lifecycle/exception-consistency defect repair,
with success-preserving engineering consolidation. Preparation/capture lifetime
and cache cleanup intentionally change allocation timing/counts/bytes/peak storage;
no unchanged-allocation or performance claim. No scientific formula/float order,
numerical selection, synchronization, templates/front, tolerance, budgets, verifier
or adaptation/acceptance/stopping change. C07/ADR-0017 require fixed topology,
initialized parametric curves, collectively exclusively deletable samples without
competing geometry-control/physical mesh owners, qualified inner operations and
nonthrowing destructors. Full metadata/error/history/budget and patch/mesh/
acceptance rollback, evaluator scratch and full-process memory stay unqualified.

Full stage 3 remains open with sixteen qualified slices. Next characterize
the remaining orchestration rollback boundary: curve adaptation metadata and
targets, evaluator scratch, patch/mesh observers, error/history/budget/acceptance
state and whole adaptive retry/rejection, then explicit full CLI disabled
synchronization. Complete point/parameter graph rollback is qualified for the
measured serial operations; it is not full Adapter/AdaptCurve/mesh atomicity.
Other constructors, custom sources, helper/template/tree/mate paths, failed-tree
observer reuse and full-process/parallel/LSan/UBSan remain open. Stages 0-2 stay
closed for measured scope; stages 4-11 pending. Doxygen API debt stays stage 8.

Compact head/main reports, command/case inventory, source/executable identities,
original extraction and full raw-log hashes are under stage3/curve_sample_graph/.
Complete fresh raw local reports retain all observations under recorded SHA256.
Documentation-only exact head/main must preserve all 538 protected compiled/
tool/test/build/input/contract identities and pass complete Git/working-byte
audit, rebuild/CTest 26/26/no skips/74 controls and inventory/whitespace. Retained
full numerical/instrument campaigns remain tied to unchanged inputs; no fresh
such execution is claimed for documentation-only changes. Final hashes/receipts
belong on the PRs/issue, avoiding self-referential evidence commits.
