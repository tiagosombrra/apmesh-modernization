# Modernization work log

## 2026-10-20: stage 3 slice 31 candidate

Repair fresh-curve ownership and borrowed observer publication at the Bezier
constructor boundary, sharing the unchanged charge scope. Candidate 71outcomes
pass with 32complete sweeps/348 denials. Original 32 failures/208 partial denials remain
retained. 32 MSVC pairs and 16 GCC pairs preserve complete normal control/direction/
scalar traces; four numerical/lifetime mutations are rejected. 43 CTest/74 Python
and selected lint/format pass. Full exact-head/main delivery remains pending;
stage 3 stays open. See [construction audit](evidence/STAGE3_BEZIER_CONSTRUCTION.md).

## 2026-10-20: stage 3 slice 30 qualified

Stage 3 slice 30 is qualified. PR #82 integrates head `45ad4f7fc50bc6dcf8b730be69443801aea7ac43`
as main `181e2acc70746d7abb5f64a924fce6aed51313e8`, preserving complete tree `17fc7f2eae0f6d87a0ccb1a3df581cab32c62eb9`
(1916 blobs). Exact-head/main full gates pass on the same 589
protected inputs: CTest 42/42, zero skips, 74 Python controls, 26 memory batteries/
2677 expected outcomes, 1040 retained scalar sequences, selected lint/format/
inventory and exact repeated Eistute/Book accepted/rejected traces.

The sampler now has automatic points and bounded scratch, without nonexistent
derived casts. The new 725 outcomes include 330 sampled exception positions and
342 zero-allocation operations; 90 actual GCC pairs preserve scalar bits and
sample/inverse arguments. Four numerical mutations are rejected. Original 367
failures/358 expected outcomes and preliminary failures remain retained. See
[root cause and bounded closure](evidence/STAGE3_CURVATURE_SAMPLE.md).

Stage 3 remains open. Next audit remaining estimator helper/control-construction
lifetime. Arbitrary callbacks, internal solver exceptions, complete cache/metadata
rollback, malformed input/partial output and full-process/parallel/LSan/UBSan remain
unqualified. Stages 4-11 remain pending.

This ledger summarizes integrated engineering deliveries; detailed commands,
failures, hashes and limitations stay in the linked evidence records.

Latest delivery: stage 3 slice 30 (PR #82); see the final ledger row.

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
| 2026-10-18, stage 3 slice 15 | #50, PR #51; head 7e9a36b80f6104bbe68724d462b71dc140149168, main 943ccf7b6d85397af6297b69ee97423d2a46311d; evidence/STAGE3_CURVE_PUBLICATION_HANDOFF_CLOSURE.md | Per-curve collective RAII publication, exact list/cache rollback and retry; head/main CTest 25/25, publication 139/139, 2403 denials, nine prior batteries and model traces exact; full-loop ownership and full rollback remain open |
| 2026-10-19, stage 3 slice 16 | #53, PR #54; head 8eaeb09fa8137ed32dea5549b4ac07b923d5bac2, main 186ef0251f460f3139baedae4ed77f30a2b9695b; evidence/STAGE3_CURVE_SAMPLE_GRAPH_CLOSURE.md | Retain initial collective graph until complete-loop commit, exact point/parameter graph rollback and cleanup across prefixes; head/main CTest 26/26, graph 156/156, 8118 denials, ten prior batteries and exact model traces; orchestration/mesh rollback remains open |
| 2026-10-19, stage 3 slice 17 | PR #56; head 06f4bfd40cff9f09c527777169c5fcf8d053e0c7, main 9703536b21d8d3f02dbe7fbd9f83d3260f461aad; evidence/STAGE3_CURVE_SAMPLE_LIFETIME.md | Scoped published-sample ownership repairs terminal-exception leaks and allocating final cleanup; CTest 27/27, lifecycle 53/53, eleven prior batteries, exact model traces; full-process/unpublished constructors remain open |
| 2026-10-19, stage 3 slice 18 | PR #58; head 84e303da51a6ac4c6cf52dbbee7f5fb30c93696e, main e398854bba9f06045b71dd1b965505872106d746; evidence/STAGE3_INITIAL_MESH.md | Actual serial constructor owns pending resources and releases center copy source; CTest 28/28, constructor 27/27/400 denials, twelve prior batteries and exact model traces; general raw mesh adoption remains open |
| 2026-10-19, stage 3 slice 19 | PR #60; head bebe4f5273719304fd00967bfaf7ae74de63f351, main e04a76a6103af5af5b116447c63c4de1ee047a0c; evidence/STAGE3_MESH_ADOPTION.md | Consume SubMesh ownership before growth/negative return; CTest 29/29, mesh 36/36 with six denials, thirteen prior batteries and exact model traces; raw element adoption remains open |
| 2026-10-19, stage 3 slice 20 | PR #62; head dcf6941e944fcd3bf268e7f9a8ecef4f87735d75, main 40106ede082614429639566c64ca3689a7d62c4b; evidence/STAGE3_ELEMENT_ADOPTION.md | Consume raw elements before vector allocation through owning AddElement; CTest 30/30, element 31/31/eight denials, fourteen prior batteries and exact model traces; constructor adjacency and live-graph reuse remain open |
| 2026-10-19, stage 3 slice 21 | PR #64; head a6da72630db2747194982e1a2b77cd3203536408, main 6cf041333b83a01f1c081df82620d12f00995d4b; evidence/STAGE3_TRIANGLE_CONSTRUCTION.md | Remove failed constructor observers without allocation; exact list-node restoration for 48 denials, triangle 39/39, CTest 31/31, fifteen prior batteries and exact model traces; ordinary destruction and mesh owner ordering remain open |
| 2026-10-19, stage 3 slice 22 | PR #66; head 88c285e5ac193e7c45fe688cec05867e5243dbdd, main 79bad64023ab1ddd54eda76930df47ff2986f765; evidence/STAGE3_SUBMESH_LIFETIME.md | Retire elements before node replacement; twelve ordering failures/derived observer UAF reproduced, SubMesh 28/28 with eight zero-allocation paths, CTest 32/32, sixteen prior batteries and exact model traces; triangle deregistration remains open |
| 2026-10-19, stage 3 slice 23 | PR #68; head f29018fea3d3490358396381cea1dc7967aaf1ac, main 4dd41510180ac0fa10e9a3f083552fe1f3c13a2c; evidence/STAGE3_TRIANGLE_OBSERVER.md | Stable triangle address identity and first-match list-node transfer; 26 original failures, observer 35/35/eight zero-allocation paths, CTest 33/33, seventeen prior batteries and exact model traces; ordinary destruction/cache refresh remain open |
| 2026-10-19, stage 3 slice 24 | PR #70; head 7d22766e562669db283bedbf09fab59663546d18, main 78bc1ff045bcabebc3ac5536e53a1a87182ad365; evidence/STAGE3_TRIANGLE_LIFETIME.md | Remove completed triangle observers while borrowed nodes live; original ASan UAF/31 cleanup failures, lifetime 36/36/eight zero-allocation paths/four adoption denials, stricter prior adoption oracle, CTest 34/34 and exact model traces; estimator roots/full-process memory remain open |
| 2026-10-19, stage 3 slice 25 | PR #72; head 6ba8ec1c95d783e0dc6c0c7c8fc33575bc90bdd7, main fdf65970dfad6898c88438a1017fa4bd34239d27; evidence/STAGE3_ESTIMATE_MESH.md | One estimator construction owner; actual-unit 77/77 and 5128 denials, 1040 exact scalar sequences, nonpositive guards, repaired required floating-loop lint, CTest 35/35, 1214 instrument outcomes and exact model traces; caller roots/full-process memory remain open |
| 2026-10-19, stage 3 slice 26 | PR #74; head 82261a7e305bcde0920ecca0dcb9d7a50893ecc9, main 96ed6ae03906d1385135276b1781f67ea59d9363; evidence/STAGE3_TRIANGLE_COUNT.md | Own temporary triangle-count mesh and fresh samples, restore prior patch observer and exact borrowed list nodes; 159/159, 9014 denials, 168 paired counts, CTest 36/36, 1373 outcomes and exact model traces; area/error callers and full-process memory remain open |

Current status: stages 0-2 closed; stage 3 in progress with twenty-six qualified
slices; stages 4-11 pending. Next repair estimator area/error roots and explicit
patch/sample lifetime without changing numerical selection policy. General mesh/
cache/foreign observer validity and full-process/parallel memory remain open.
| 2026-10-19, stage 3 slice 27 | PR #76; head 387cf4d94eebb06a3203727ae97bffdbb5e5f1eb, main c905baa3738db4059ecce4c4b896b8753de43daa; evidence/STAGE3_ERROR_ESTIMATE.md | Temporary evaluator root/vector released; CTest 37/37, 1421 instrument outcomes, 156062 new allocation denials, 270 paired policy decisions, exact repeated article traces; original retention/tooling failures preserved; area orchestration next |
| 2026-10-20, stage 3 slice 28 | PR #78; head d36f71c19278547ec897d5c96a7cc37e2884c6bc, main 4ea63f2118c9cccf8968676125bb3794d7a79bd0; evidence/STAGE3_TRIANGLE_AREA.md | Temporary area Mesh/fresh sample owners and previous patch restoration; CTest 39/39, 1763 outcomes, 30942 new denials, exact paired area/degree/exception traces and repeated article runs; original failures preserved; input/control-point roots next |
| 2026-10-20, stage 3 slice 29 | PR #80; head 86e5555b2d2590c9ab382842e4a0b0cb3005b0e5, main 42f8e62eee04e99a566f499651c477bd2cb47345; evidence/STAGE3_CHARGE_INPUT.md | Unique reader/pending owners, automatic controls, exclusive observer-suffix cleanup and reader badbit propagation; head/main 41 CTest, 74 Python controls, 1952 expected instrument outcomes, 2787 new allocation denials, 48 exact paired traces and article regression; original 155 failures and DLL CRT/reader/link preflights retained; helper scratch/full-process remain open |
| 2026-10-20, stage 3 slice 30 | PR #82; head 45ad4f7fc50bc6dcf8b730be69443801aea7ac43, main 181e2acc70746d7abb5f64a924fce6aed51313e8; evidence/STAGE3_CURVATURE_SAMPLE.md | Automatic curvature samples, no nonexistent derived casts, bounded scratch; 42 CTest, 74 Python controls, 2677 memory outcomes, 342 zero-allocation operations, 90 exact sample pairs and article regression. Original 367 failures retained; stage 3 and full-process scope remain open |
