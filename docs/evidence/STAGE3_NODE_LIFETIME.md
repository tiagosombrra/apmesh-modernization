# Stage 3, slice 1: physical node copy boundary

This is the retained candidate checkpoint. Final exact-head/post-merge results
and work-item closure are recorded in [the slice audit](STAGE3_SLICE1_CLOSURE.md).

Work item: #8. Entry main: `6c56e307b1e932399c88ba961a9de40bf87ecbca`;
tree: `9c7dee056042e911ec1c19e2abced94da64b965e`.
Classification: demonstrated lifetime defect repair, with no observed scientific
output change. This closes only the bounded work item after integration and
post-merge qualification; stage 3 remains open.

## Defect, caller review and repair

SetNoh already created an independently owned NodeAdaptive, although the grouped
header comment promised raw-pointer adoption. The implicit copy also duplicated
borrowed element pointers. A real TriangleAdaptive was allocated, its node copied
through SetNoh, then the triangle deleted. Reading the copied node's element area
reproduced **heap-use-after-free** under MSVC AddressSanitizer. The failing
contract and symbolized diagnostics are retained in `stage3/baseline-*`.

The repair clears the copied observer list at this mesh ownership boundary.
ID, XYZ and all four curvature fields are preserved. The source remains
caller-owned; AddNoh(unique_ptr) retains its distinct transfer semantics. Local
triangle construction registers adjacency in the usual order. General
NodeAdaptive copy/assignment, TriangleAdaptive::GetNoh value snapshots,
TriangleAdaptive destruction and ReplaceNode are unchanged.

All six SetNoh call sites were reviewed: four in generator initial-mesh routes
(including conditional OpenMP) and two in charge estimation. These construct
fresh scalar nodes, so their copied adjacency is initially empty. Some original
nodes remain curve samples, while other originals are explicitly deleted or
still have ownership gaps. Adopting SetNoh arguments would therefore break the
existing independence contract. The source-proved center/estimator ownership
gaps remain for the sample/initialization lifecycle slice; this patch does not
claim to repair those leaks. No conditional OpenMP execution is qualified.

The only production changes are SubMesh implementation/header and explicit
formatting of those files. No formulas, thresholds, accumulation order, node
identity rules, curve partitions, quadtree/templates, front, acceptance or
stopping policy changed. No new mesh welding or alternative generator is added.

## Diagnostic qualification

The standalone `tests/memory` target compiles six actual production translation
units and the same probe used in normal CTest. MSVC 19.44.35229 x64,
RelWithDebInfo `/fsanitize=address /Zi` measures invalid accesses. A separate
Debug build uses CRT allocation snapshots around the complete scenario. GCC
16.1.0 serial C++17 Release remains the application regression toolchain;
CMake/CTest 4.4.3 and clang-format/tidy 22.1.8 are development tools.

| Observation | Original implementation | Repaired implementation |
| --- | --- | --- |
| Independent copy must start without foreign element observers | Contract fails | Pass |
| Destroy original triangle, then examine copied adjacency | ASan heap-use-after-free | Pass, empty adjacency |
| 200 copy/rebuild/move/replacement/teardown iterations | Fails at copied-adjacency contract | ASan pass; CRT zero retained blocks/bytes |
| Unique adoption preserves pointer identity and destroys once | Included in probe | Pass |
| Deliberate independent use-after-free | ASan detects | ASan still detects |
| Deliberate double free | ASan detects | ASan still detects |
| Deliberate leaked NodeAdaptive | Separate CRT control | CRT detects 3 blocks, 136 bytes |

The pinned original six implementation files were reconstructed under build,
using the final probe and compatible headers (the SubMesh header has only the
contract/comment correction). `baseline_reproduction.json` binds the original
executable and retained logs. `source_identities.json` and
`memory_qualification.json` bind current sources and both instrumented binaries.
ASan is not a leak detector in this Windows campaign. CRT retained-allocation
measurement is a justified narrow equivalent, not Linux LSan or UBSan coverage.
Full-application memory safety, allocation-failure injection and every exception
path remain unqualified. Legacy PointAdaptive signed-ID initialization produces
MSVC warning C4245; it is retained and is not suppressed.

Commands, from repository root (put CMake/GCC and the MSVC ASan DLL directory on
PATH as appropriate):

```text
cmake -S tests/memory -B build/stage3-node-msvc -G "Visual Studio 17 2022" -A x64 -DAP_MESH_NODE_ASAN=ON
cmake --build build/stage3-node-msvc --config RelWithDebInfo
cmake -S tests/memory -B build/stage3-node-crt -G "Visual Studio 17 2022" -A x64
cmake --build build/stage3-node-crt --config Debug
python tools/qualify_node_lifetime.py --asan build/stage3-node-msvc/RelWithDebInfo/node_lifetime_probe.exe --crt build/stage3-node-crt/Debug/node_lifetime_probe.exe --runtime <MSVC-bin/Hostx64/x64> --output <fresh-diagnostic-directory>
cmake --preset local-serial
cmake --build --preset local-serial
ctest --preset local-serial --output-on-failure
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
python tools/quality.py tidy src/data/mesh/sub_mesh.cpp --build build/local-serial
clang-format --dry-run --Werror tests/memory/probe.cpp include/data/mesh/sub_mesh.h src/data/mesh/sub_mesh.cpp
```

## Entry and candidate regression

Remote audit found main unchanged, six branches, no open PRs/issues, zero Actions
runs and zero check runs. All 658 local text blobs matched the 660-blob remote
tree; the two remote-only immutable publication binaries remain preserved.
Issue #8 was then opened as the only active work item. There are no hosted
workflows; local gates are mandatory and are not substituted by missing checks.

Entry CTest: 9/9, zero skips. Candidate CTest: **10/10, zero skips**, including
74 Python controls (one new nested-test CMake inventory control), 23 real invalid
inputs, 14 orientation generation controls/44 attempted states and the new
physical node lifecycle probe. Existing analytic orientation, independent
verifier negatives and actual lint-scope controls remain enabled. Selected
SubMesh clang-tidy and explicit changed-file formatting pass.

Eistute and Book were each repeated twice before and after the repair. All
generated OBJ, acceptance/CSV fields and incidence snapshots repeat exactly.
Strict candidate-versus-entry and entry-versus-stage-2-main comparisons pass for
all nine attempted states. Positive shared-incidence coverage and zero measured
position gap are retained. Both accept steps 0 and 1; the final accepted meshes
remain Eistute **1,168** and Book **4,256** triangles. Named CSV audits compare
105 and 84 fields with zero differences. No tolerance or oracle was relaxed.

For each model, the executed command was:

```text
python tools/repeat_generation.py --exe build/local-serial/bin/ap_mesh.exe --model <eistute|book> --output <fresh-run-directory> --report <report.json>
```

Independent verify_run(require_boundary=True), compare_runs and CSV audit results
are retained in `stage3/candidate_regression.json`. Source config/model and
executable hashes are recorded by the existing run metadata. The application
entry executable is `aa02aa970dfa277d1e4590bb31d46a3ec35f8f36734accd7d2bfbf08027d1301`;
candidate is `b1244378f7638d4508df04d76e091615a62158d76a5a1f7068b1079321d46adf`.
Different PE hashes do not imply changed scientific output or reproducible builds.

## Closure audit and remaining stage scope

The reviewed contracts now distinguish scalar copying from adoption, and the
source inventory includes the isolated test CMake input: 122 production C++
files, four build inputs, 22 contracts and 79 anchors. Historical stage 2
evidence is unchanged. The current architecture map and follow-up sequence are
updated; an inventory pass proves freshness/traceability, not semantic safety.

This slice's required gates pass at the candidate checkpoint. Published-head
and post-merge qualification must still be recorded before issue closure.
The next bounded slice is UV front/edge/face teardown under normal, partial and
failed generation, with deliberate ownership diagnostics. Curve sample and
rollback ownership, retained accepted meshes, UV exception cleanup, generic
node snapshots, triangle removal/replacement/cache invalidation and full process
leaks remain open. Decor Shelf generation, internal retry instrumentation,
parallel modes, portability/C++23, Eigen removal and stages 4-11 are not qualified
by this delivery. Legacy zero-group compatibility summaries remain unmeasured;
independent incidence snapshots supply the measured boundary coverage.
