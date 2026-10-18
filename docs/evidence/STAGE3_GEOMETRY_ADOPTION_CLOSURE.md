# Stage 3 slice 10 closure: Geometry adoption

Updated 2026-10-18 (America/Fortaleza). Issue #35; implementation PR #36.

Qualified head `249c561ec10f5d3766b0d1be71ed52d09e6420ec` integrated as implementation-main
`4e23bd00e457e68056ff956869732b1872f04822`, preserving complete tree
`4f6e71bf48933dfae637d6a200d9e2236734eb1e` (1083 blobs).
Both full exact-revision campaigns pass; this documentation-only follow-up
preserves every qualified compiled/tool/test/build/input/contract identity:
514 files, SHA256 `655549219b478af14e5faef61972af262467f77d490eb95de2548a74c9f7ddae`.
Reports, commands, source/argument/executable identities and raw failure hashes:
stage3/geometry_adoption/. Final documentation-head/main receipts are recorded
on the PRs and issue to avoid a self-referential evidence-commit chain.

## Explicit closure audit

| Boundary | Result and limits |
| --- | --- |
| Code | Raw InsertCurve/InsertPatch delegate through pending unique_ptr owners. Failure consumes/destroys the argument, preserves existing entries and permits fresh-argument retry. Success identity/order/allocation counts/null slots are unchanged. No interface/layout/growth policy or numerical delta. |
| Tests | CTest 20/20, zero skipped; 74 Python controls. New adoption 53/53: 32 normal cases, two null controls, 16 positive-calibration sweeps and three instrument controls. All 16 observed ordinals denied once; original fails eight raw scopes with positive retention while 45 other outcomes are expected. |
| Prior instruments | Copy 30/30, curve 19/19, UV 81/81, node 7/7 remain required and pass on head and main. ASan invalid access, CRT leak and hook controls are required; Windows ASan is not LSan/UBSan. |
| Source/ownership | Actual initialized parametric/Bezier/Hermite pointer-copy constructors prepare pending objects before measured adoption. External sample/patch values and identities, existing owner prefixes, normal geometry and exactly-once destruction are checked. Argument construction itself is outside adoption denial sweeps. |
| Contracts | C03, header failure/ownership preconditions and ADR-0011 match the directly measured boundary. Aliased/duplicate adoption is invalid. No deep sample clone, generic observer lifetime or multi-object transaction is promised. |
| Quality | Actual Geometry clang-tidy unit passes in both compiled configurations; new probe and changed ranges formatted explicitly. Initial failed formatting XML/reports are retained. No suppression or repository-wide fix. Fresh inventory: 123 production files, 57 units, 66 headers, 22 contracts/100 anchors; existing six-header cycle remains. |
| Regression | Eistute/Book each repeated twice; strict entry and head/main comparisons pass for all nine attempted states, all OBJ/acceptance/rejection/incidences, positive measured shared coverage/zero gaps, 189 named CSV fields and final accepted triangles 1,168/4,256. Accepted 0/1; rejected Eistute 2/3/4 and Book 2/3. |
| Scientific scope | Formulas, floating-point order, tolerances, budgets, independent verifiers, synchronization, quadtree/templates/front and adaptation/acceptance/stopping policy unchanged. This is a failure-path ownership defect repair, not a scientific proposal. |
| Documentation | Plan/state/worklog, README, quality, C03, ADR and evidence agree. Generated Doxygen still fails undocumented APIs; stage 8 is not closed. |
| Open inventory | CloneCurveForPatch/DisableSharedCurveSynchronization helper/policy integration and graph transaction/rollback remain statically reviewed only. Earlier clone allocations, remaining constructors/mutations, implicit copies, shared samples/initialization, general observers, other UV/tree/mate paths, failed-tree observer consumption/retry, full-process/parallel/LSan/UBSan stay unqualified. |

Full stage 3 stays open with ten measured slices. Stages 0-2 remain closed for
their measured scope; stages 4-11 remain pending. The historical repository,
vendor, model/configuration inputs and independent numerical verifiers are preserved.

This follow-up must pass exact documentation-head and post-merge main gates:
complete remote/local Git tree and working-byte identity, unchanged qualified
514-file map, rebuild/CTest 20/20 with zero skips and 74 Python controls,
fresh inventory, whitespace and retained full implementation-head/main report
identity. No new numerical/instrument campaign is needed for unchanged inputs;
the qualification is inherited explicitly, not represented as a fresh run.
