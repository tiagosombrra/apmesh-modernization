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
| 2026-10-18, stage 3 slice 9 | #32, PR #33; head 6bda90b91406b0aed79ba6582bf820ea40559325, main d5abb5495b28e8ec5a2b6f779c3adf173929ed04; evidence/STAGE3_CURVE_COPY_CLOSURE.md | Initialized pointer-taking copies preserve parameter pairing; head/main CTest 19/19, copy 30/30, curve 19/19, UV 81/81, node 7/7, 123 denials, unchanged numeric/article traces; clone publication and implicit copying remain open |
| 2026-10-18, stage 3 slice 10 | #35, PR #36; head 249c561ec10f5d3766b0d1be71ed52d09e6420ec, main 4e23bd00e457e68056ff956869732b1872f04822; evidence/STAGE3_GEOMETRY_ADOPTION_CLOSURE.md | Guard raw Geometry arguments before allocation; head/main CTest 20/20, adoption 53/53, copy 30/30, curve 19/19, UV 81/81, node 7/7, 16 denials, unchanged normal traces/allocation counts and exact article regression; helper/policy integration remains open |
| 2026-10-18, stage 3 slice 11 | #38, PR #39; head ce139f7d46b30daee365dfe5b1608183eb0d02c5, main 43e0309d6408601cd13e130cfa9668f35596ab67; evidence/STAGE3_CURVE_PUBLICATION_CLOSURE.md | Pending clone ownership and per-curve publication/retry; head/main CTest 21/21, sync 73/73, prior instruments pass, 484 denials and exact model regression; full CLI disabled-policy and adaptive rollback remain open |

Current status: stages 0-2 closed; stage 3 in progress with eleven qualified
slices; stages 4-11 pending.

Full stage 3 remains open with eleven qualified slices. Next characterize
shared-sample initialization and adaptive snapshot/restore/failure handling,
remaining constructors/mutations and explicit full CLI synchronization-disabled
integration. The extracted clone/publication operation is directly qualified
for the documented initialized graph fixtures; whole-operation atomicity and
adaptive rollback are separate. Generic observers/custom subclasses, inconsistent
sources, other helper/template/tree/mate paths, failed-tree observer consumption/
retry and full-process/parallel/LSan/UBSan remain open. Stages 0-2 stay closed for
measured scope; stages 4-11 stay pending. Doxygen API debt stays stage 8.

No full-application memory-safety claim is made.

[Current state](PROJECT_STATE.md), [plan](MODERNIZATION_PLAN.md),
[slice 11 closure](evidence/STAGE3_CURVE_PUBLICATION_CLOSURE.md).

## Active stage 3 slice 12 (#41): transactional curve sample restoration

The original restoration deletes current samples before allocating replacements.
Twelve original sweeps stop at denied ordinal 6 because live samples were deleted;
four stop at ordinal 18 because a live list was partially published. Later
ordinals and CRT retention in those 16 aborted cases are unmeasured; the probe
stops before unsafe observer consumption. Four empty-to-single sweeps complete
with six retained blocks each. Other 69 of 89 outcomes are as expected.

Capture/restoration now live in a narrow production unit used by the same
Generator call sites. Pending unique NodeAdaptive owners and complete prepared
lists precede direct nonallocating swaps, owner release and unique old-sample
deletion. Allocation failure preserves the complete live point graph and list
nodes; subsequent retry succeeds. Success preserves first-encounter ID/XYZ,
order, sharing and zero node curvature/adjacency. Conflicting duplicate-ID input
is a policy-preservation control, not approval of that identity convention.
Parameter lists are not captured/restored. Current samples must be collectively
exclusively owned/deletable through the curves. Successful restoration invalidates
their observers. Independent accepted mesh copies remain unchanged in fixtures;
full mesh, patch binding, budget, error/history and acceptance rollback remain open.

Candidate gates pass: CTest 22/22, zero skips, 74 Python controls; snapshots
89/89 with 536 denials across 28 calibrated sweeps. Prior synchronization
73/73, adoption 53/53, copy 30/30, curve 19/19, UV 81/81 and node 7/7 pass.
Full normal original/repaired traces match. Actual new-unit read-only lint,
explicit formatting and inventory pass. Both article models repeat twice with
all nine OBJ/acceptance/rejection/incidence states and 189 CSV fields exact;
last-accepted triangles remain 1,168/4,256. Published-head/main gates remain.

Original comparison uses 14 pinned production units plus hash-verified lambda
bodies in an adapter, not the full old generator translation unit. Candidate
instruments 15 actual units. Only the new Debug CRT target consistently disables
iterator proxies; actual heap, failure and deliberate negative controls remain.
Preparation changes allocation timing/counts/bytes and peak live storage, with
no performance claim. Classification: ownership/exception-consistency defect
repairs plus engineering extraction. No formula, floating-point order, tolerance,
budget, verifier, synchronization or adaptation/acceptance/stopping policy change.
Full stage 3 stays open. See evidence/STAGE3_CURVE_SNAPSHOTS.md and ADR-0013.
