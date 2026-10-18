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
| 2026-10-17, stage 3 slice 8 | #29, PR #30; head 2c7edff9070810ea8e27574e4449aeebf369824e, main 587c91923b48d7f55414df720d29bcb1d2dacc11; evidence/STAGE3_CURVE_COLLECTIONS_CLOSURE.md | Per-list prepared-input commit; head/main CTest 18/18, curve 19/19, UV 81/81, node 7/7, 76 allocation denials, exact ordered traces/article regression; paired update and full value-copy semantics remain open |

Current status: stages 0-2 closed; stage 3 in progress with eight qualified
slices; stages 4-11 pending.

Full stage 3 remains open with eight qualified slices. Next characterize the
remaining curve constructor/mutation contracts, including the pointer-taking
parametric constructor's omitted parameter sequence, before shared sample
ownership, initialization and rollback. Current constructor controls qualify
unwind, borrowed collections and selected initialized scalar/coefficient state;
full value-copy semantics are not claimed. General observers, joint updates,
other helpers/templates/tree/mate paths, failed-tree observer consumption/retry
and full-process/parallel/LSan/UBSan qualification remain open. Stages 0-2 stay
closed; stages 4-11 stay pending. Doxygen undocumented-API debt stays stage 8.

No full-application memory-safety claim is made.

[Current state](PROJECT_STATE.md), [plan](MODERNIZATION_PLAN.md),
[slice 8 closure](evidence/STAGE3_CURVE_COLLECTIONS_CLOSURE.md).

## Active stage 3 slice 9 (#32): initialized curve copy parameters

The original pointer-taking parametric constructor copies sample observers but
omits their parameter sequence; Bezier and Hermite copies inherit the loss.
Twelve populated normal cases fail in ASan/CRT, and six populated constructor
sweeps stop at their normal calibration contract before denying allocations.
The other 12 original outcomes are as expected, including invalid controls.
A standard-list member initializer now copies the parameter values independently.
Physical samples and patches remain borrowed; no source consistency repair,
implicit copy/assignment or clone-publication guarantee is added.

Candidate CTest 19/19, zero skips, 74 Python controls, new copy 30/30, previous
curve 19/19, UV 81/81 and node 7/7 pass. Nine independently calibrated sweeps
deny all 123 measured ordinals, preserving full initialized source state/nodes,
caller objects and successful retry. All 18 original/repaired normal numeric
traces match; empty-sequence full traces remain exact. Five analytic position/
derivative samples and signed arcs, actual populated point/parameter traversal,
independent lists and both destruction orders are checked. Selected one-unit
lint, formatting, inventory and repeated strict Eistute/Book entry regression
pass with all nine states, acceptance/rejection, measured incidences, 189 CSV
fields and 1,168/4,256 accepted triangles exact. Populated copies deliberately
allocate five additional parameter nodes in these fixtures; counts are not
portable constants. Exact published-head and implementation-main gates remain.

This is a behavior-changing copy-state defect repair, not a scientific proposal.
Clone publication, other construction/mutation, implicit copying, shared sample
ownership, initialization/rollback, general observers and full-process/parallel/
LSan/UBSan remain open. Stage 3 stays open. See evidence/STAGE3_CURVE_COPY.md and
ADR-0010. Doxygen undocumented-API debt remains stage 8.
