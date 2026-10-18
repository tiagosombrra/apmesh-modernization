# Stage 3 slice 12 closure: transactional curve sample restoration

Updated 2026-10-18 (America/Fortaleza). Issue #41; implementation PR #42.
Qualified head `98528aeba68bb0b016b40eeeaff8d2bac6acc297` integrated as main
`358107faff5d6d2cdcd63eba12114abf7f7dc5ec`, preserving tree `b39cd3b291f072983807828d4e3530fa6c9311f1`
(1321 blobs). Full head/main campaigns pass. This follow-up
preserves 522 qualified compiled/tool/test/build/input/contract identities,
SHA256 `039584946812d2b0b87fc568383e89fa1503de852315598ae095b986669eb50f`.
Commands, hashes, source extraction and failed/passing reports are under
stage3/curve_snapshots/. Final documentation-head/main receipts belong on the
PRs/issue to avoid a self-referential evidence commit chain.

## Explicit closure audit

| Boundary | Result and limitation |
| --- | --- |
| Code | Extract ordered capture and restoration, retaining Generator call order. Unique pending nodes and complete lists precede direct list swaps, release and unique old-sample deletion. Nonallocating commit for built-in initialized curves/nonthrowing samples; failure preserves all current sample/list-node identities and retry succeeds. |
| Ownership | Curve lists remain observers; the caller must have exclusive lifetime authority to delete all current samples exposed through them. Existing raw sample ownership convention remains on success, with old sample/list observers invalidated. No competing-owner/custom-destructor guarantee. |
| Original failures | Fourteen pinned units plus verified lambda adapter, not full original Generator-TU instrumentation. Twelve sweeps stop at ordinal 6 after destroying samples; four at ordinal 18 after partial list publication. Subsequent ordinals and CRT retention in those 16 aborted cases are unmeasured. Four empty-to-single sweeps complete with six retained blocks each. Other 69 outcomes expected. Raw failure logs or exact local hashes are retained without normalizing tool dumps. |
| Tests | CTest 22/22, zero skips, 74 Python controls. Snapshots 89/89: 56 normal capture/restore, two guard outcomes, 28 positive calibrated sweeps/536 denials and three deliberate hook/UAF/leak controls. Four actual curve kinds, shared/repeated/reversed references, conflicting duplicate IDs, empty/populated transitions, exact first-ID/XYZ order/aliases, old-node deletion, zero node curvature/adjacency, unchanged parameters/evaluators, failure list-node identity and retry/repeated success. Empty/null/count controls are not positive graph coverage. |
| Prior gates | Synchronization 73/73, adoption 53/53, copy 30/30, curve 19/19, UV 81/81 and node 7/7 pass on exact implementation head/main. |
| Instrument scope | Candidate uses 15 actual units, including independent accepted SubMesh copies and actual Triangle adjacency. New Debug CRT iterator metadata is consistently disabled, retaining heap checks/negative controls; previous targets unchanged. Neither full-process memory qualification nor cross-compiler ABI/iterator-level-2 recovery is claimed. |
| Contracts/quality/docs | C07/C12 and ADR-0013 define graph transaction and limits. Actual new-unit read-only lint, explicit new-file/delegate-range formatting and inventory pass: 127 production files, 59 units, 68 headers, 22 contracts/104 anchors; existing six-header cycle remains. State, plan, worklog, sequence, quality, README and this consolidated audit updated. |
| Resources | Preparation changes allocation timing/counts/bytes and peak live storage. Counts are measured, not portable constants; no performance claim. Capture's calibrated counts and all normal full logs match original. |
| Regression | Two repetitions per article model; all nine attempted OBJ/acceptance/rejection/incidence states, positive measured shared coverage/zero gaps and 189 named CSV fields exact to entry and head/main. Accepted steps 0/1; rejected Eistute 2/3/4 and Book 2/3; final accepted triangles 1,168/4,256. |
| Scientific scope | No formula, floating-point order, boundary synchronization, quadtree/templates/front, verifier, input, tolerance, budget or adaptation/acceptance/stopping change. Failure-path defect repairs and engineering extraction only. |
| Open inventory | Parameters are neither captured nor restored. Independent accepted mesh copies are unchanged in fixtures; complete mesh/patch binding/error/history/budget/acceptance rollback remains unqualified. Remaining constructors/mutations, generic observers/custom sources, full CLI disabled synchronization, other UV/tree/mate paths, failed-tree observer consumption/retry, full-process/parallel/LSan/UBSan and stage-8 Doxygen API debt remain open. |

Full stage 3 remains open with twelve qualified slices; stages 4-11 stay pending.
Historical/vendor sources and independent numerical verifiers are preserved.
Exact documentation-head/post-merge main must pass full Git/working-byte and
unchanged 522-file identities, rebuild/CTest 22/22/zero skips/74 controls,
inventory/whitespace and retained full head/main campaign identities. No fresh
numerical/instrument execution is claimed for documentation-only changes.
