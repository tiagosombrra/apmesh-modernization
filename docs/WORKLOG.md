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
| 2026-10-18, stage 3 slice 12 | #41, PR #42; head 98528aeba68bb0b016b40eeeaff8d2bac6acc297, main 358107faff5d6d2cdcd63eba12114abf7f7dc5ec; evidence/STAGE3_CURVE_SNAPSHOTS_CLOSURE.md | Prepared complete sample graph before restoration; head/main CTest 22/22, snapshots 89/89, prior instruments pass, 536 denials and exact model regression; parameter/full adaptive rollback remain open |
| 2026-10-18, stage 3 slice 13 | #44, PR #45; head ffdde7248564c8e072138d9673871baa4f13e217, main 3e628e6445b2638ff73a51fa8bb1a9aed440647c; evidence/STAGE3_CURVE_REBUILD_CLOSURE.md | Prepare paired target rebuild before swaps/deletion; head/main CTest 23/23, rebuild 117/117, prior instruments pass, 597 denials and exact model regression; consumed IDs, later curve observer publication/full rollback remain separate |
| 2026-10-18, stage 3 slice 14 | #47, PR #48; head e61be31964558b2f3812d2d6341774ede96cc902, main 4cc921ddf0bc5e069118540c1dd278f704abdeb3; evidence/STAGE3_ADAPTER_SAMPLES_CLOSURE.md | Prepare serial Adapter samples/cache/parameters and commit after return construction; head/main CTest 24/24, samples 88/88, 702 denials, prior gates and model regression exact; upstream scratch/selection, Generator publication and full rollback remain open |

Current status: stages 0-2 closed; stage 3 in progress with fourteen qualified
slices; stages 4-11 pending.

Full stage 3 remains open with fourteen qualified slices. Next characterize
Generator point-observer publication and collective sample ownership across
curve/surface refinement, then upstream/full adaptive retry/rollback over
parameters, patch/mesh observers and error/history/budget state, plus explicit
full CLI disabled synchronization. Construction-tail and paired-rebuild commits
are qualified narrow boundaries, not full Adapter/AdaptCurve/mesh transactions.
Evaluator scratch, remaining construction/mutation, generic/custom sources,
other helper/template/tree/mate paths, failed-tree observer consumption/retry
and full-process/parallel/LSan/UBSan stay open. Stages 0-2 remain closed for
measured scope; stages 4-11 pending. Doxygen API debt stays stage 8.

No full-application memory-safety claim is made.

[Current state](PROJECT_STATE.md), [plan](MODERNIZATION_PLAN.md),
[slice 14 closure](evidence/STAGE3_ADAPTER_SAMPLES_CLOSURE.md).
