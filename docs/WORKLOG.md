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

Current status: stages 0-2 closed; stage 3 in progress with three qualified
slices; stages 4-11 pending. Original failures, diagnostics and the initial
missing-header build failure remain recorded. The documentation-only closure
preserves all qualified source/tool/test/build/input identities. Next:
template arrays/object creation before registration and Boundary registration,
then other setters/helper temporaries, curve samples/initialization and rollback.
Active #17 candidate: pending Boundary/template registration, Face::quality
unwind and null-owner query guards. CTest 14/14, UV 49/49, node 7/7, 1,361 new
allocation failures, six-unit lint and exact article/UV trace regression pass.
Published-head and post-merge gates remain before closure. Failed original and
fixture/build/lint failures remain evidence; see STAGE3_UV_REGISTRATION.md.
No full-application memory-safety claim is made.

[Current state](PROJECT_STATE.md), [plan](MODERNIZATION_PLAN.md),
[slice 3 closure](evidence/STAGE3_UV_ALLOCATION_CLOSURE.md).
