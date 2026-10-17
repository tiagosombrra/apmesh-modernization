# Modernization work log

This ledger summarizes integrated engineering deliveries; detailed commands,
failures, hashes and limitations stay in the linked evidence records.

| Delivery | Integrated record | Result and continuity |
| --- | --- | --- |
| Stage 0 | PR #1; PROVENANCE.md and evidence/BOOTSTRAP_VALIDATION.md | Separate immutable publication import, local quality infrastructure and plan |
| Stage 1 | PR #3 and closure #4; evidence/STAGE1_CLOSURE.md | Independent regression, explicit orientation/corner/order/CSV repairs; exact qualified reference |
| Stage 2 | PR #6 and closure #7; evidence/STAGE2_CLOSURE.md | Complete production inventory, ownership/domain contracts, ADR and repair sequence; no production delta |
| 2026-10-16, stage 3 slice 1 | #8, PR #9; head 6c6c2f2d50f5870fd92e4edbc91fc5d901a1cd22, main e30fa99a8ea6da709f3943e8975efb31d9610b1d | Reproduced and repaired SetNoh foreign-adjacency UAF; CTest 10/10, 74 Python controls, ASan/CRT 7/7, exact Eistute/Book head/main regression |
| 2026-10-16, stage 3 slice 2 | #11, PR #12; head a5fb2cd0d7ebbe6dc10f98689f4d6caa60419c0c, main 5bfcadaaa2172c297448c9870c0f468feeae8f4a; evidence/STAGE3_UV_CLOSURE.md | Registered-template failure leaks, midpoint-alias UAF and allocating teardown repaired; exact tree 706 blobs; head/main CTest 11/11, 74 Python controls, UV 26/26, node 7/7, exact Eistute/Book regression |
| 2026-10-16, stage 3 slice 3 | #14, PR #15; head fce74915755d1535b89dbd280cbc1ba3813f9b91, main 68ef4db735d3c478215815128309c6bdd7a8e90c; evidence/STAGE3_UV_ALLOCATION_CLOSURE.md | Edge/front allocation retention, partial failed cache state and Face alias UAF repaired; exact 737-blob tree; head/main CTest 12/12, UV 35/35, node 7/7, 53 measured primitive failure sites and exact article regression |
| 2026-10-17, stage 3 slice 4 | #17, PR #18; head ef89fd9d3305a9ed4c88548df086540d00bbadd3, main da3eed2dc351cfe1a82b117d686164686c738d95; evidence/STAGE3_UV_REGISTRATION_CLOSURE.md | Pending Boundary/template registration and Face::quality unwind repaired; missing-quadtree queries throw; 784-blob tree; head/main CTest 14/14, UV 49/49, node 7/7, 1,361 allocation failures, exact article/UV traces |
| 2026-10-17, stage 3 slice 5 | #20, PR #21; head 4f0c9bed6d1d1a52b6cdab88a26a9323040614f9, main 83eefa8c6006cc39dcdc35d463b8611d6f038538; evidence/STAGE3_UV_TREE_CLOSURE.md | Root extents and midpoint construction guarded until adoption; 818-blob tree; head/main CTest 15/15, UV 56/56, node 7/7, 3,470 allocation failures and exact tree/scientific traces |
| 2026-10-17, stage 3 slice 6 | #23, PR #24; head da684dd6a2a1fefe709fc8906cce837da4b2ea24, main 1d7d5992d90f09d8cf7747d9023d9b39ef3d089b; evidence/STAGE3_ANGLE_HELPER_CLOSURE.md | Angle-helper borrowed endpoints survive allocation failure; head/main CTest 16/16, UV 68/68, node 7/7, 252 allocation denials, unchanged angle traces/counts and exact article regression |
| 2026-10-17, stage 3 slice 7 | #26, PR #27; head 4781226726bd36d7ff64afb273ed53c37630b6f3, main 61dc86ecaeede57ec838a5bb754f237b2013085a; evidence/STAGE3_PARAMETRIC_MIDPOINT_CLOSURE.md | Transactional midpoint/length replacement; head/main CTest 17/17, UV 81/81, node 7/7, 30 allocation denials, exact normal traces/counts and article regression; direct curve allocation failure remains unmeasured |

Current status: stages 0-2 closed; stage 3 in progress with seven qualified
slices; stages 4-11 pending.

Full stage 3 remains open with seven qualified slices. Next characterize other
curve mutation/constructor/setter failures, then shared sample ownership,
initialization and rollback. General observers, other helper/template/tree/mate
paths, failed-tree observer consumption/retry and full-process/parallel/LSan/
UBSan qualification remain open. Stages 0-2 stay closed; stages 4-11 stay pending.

No full-application memory-safety claim is made.

[Current state](PROJECT_STATE.md), [plan](MODERNIZATION_PLAN.md),
[slice 7 closure](evidence/STAGE3_PARAMETRIC_MIDPOINT_CLOSURE.md).

## Active stage 3 slice 8 (#29): curve collection transactions

The original SetPoints and UpdateParameters partially overwrite populated live
lists when growth allocation fails (ordinal 7 in both measured fixtures).
The other 17 original instrument cases behave as expected, including deliberate
invalid controls. Each setter now swaps its already prepared by-value input.
Allocation failure preserves live values/nodes and caller lvalue inputs;
successful replacement invalidates old list-element observers. Borrowed objects
remain caller-owned. Redundant copy allocations and successful node reuse
intentionally change; old list nodes are destroyed after swap.

Candidate CTest 18/18, zero skips, 74 Python controls, curve 19/19, previous UV
81/81 and node 7/7 pass. Fourteen independently calibrated sweeps deny all 76
measured ordinals; normal ordered value/pointer traces match the original.
Two-unit selected lint, formatting, inventory and strict repeated Eistute/Book
entry regression pass, preserving all nine states, measured incidences,
acceptance/rejection, 189 CSV fields and 1,168/4,256 accepted triangles.
Exact published-head and implementation-main campaigns remain required.

This is an exceptional-exit defect repair. The two setters are independent,
not a joint point/parameter transaction. Pointer-taking copy controls qualify
unwind, observers and selected initialized scalar/coefficient state; the current
parametric constructor omits the parameter sequence, which remains a separate
semantic finding. Derived constructors, other mutation, shared sample ownership,
initialization/rollback, general observers and full-process/parallel/LSan/UBSan
remain open. Full stage 3 remains open. See evidence/STAGE3_CURVE_COLLECTIONS.md
and ADR-0009. Doxygen undocumented-API debt remains stage 8.
