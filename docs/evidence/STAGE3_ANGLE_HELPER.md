# Stage 3 slice 6: borrowed endpoints in the angle helper

Issue #23. Entry main `e488c64eecacf1af3d8ac0e47043e85e216f8370`, complete tree
`b1d5ae5dbc791cb6b622942fc6ce4b18c9fabfad` (828 blobs).
Classification: behavior-changing defect repair on allocation-failure exits;
successful scientific behavior is preserved. Full stage 3 remains open.

## Entry authority and baseline

The remote audit found 16 branches, no open PRs/issues, no check/status contexts
and no Actions runs before opening the sole active item #23. All 828 local
files matched their indexed Git blobs, including publication binaries. No
concurrent main change was observed. A 460-blob original production/header/vendor
snapshot was extracted from the entry revision and independently Git-blob
verified. The final probe compiles the same 14 actual UV/curve/numerical units
against original and repaired sources.

Fresh entry MSVC ASan/Debug CRT qualification passes UV 56/56 and node 7/7,
including deliberate UAF, shared deletion, retained-block and allocation-denial
controls. The serial entry CTest 15/15 and repeated Eistute/Book baseline are
the previous exact-main local continuation campaign at this same revision,
not a claim of a second fresh entry serial run. Entry identity was rechecked
before edits; its actual retained article outputs supply the strict baseline.

## Reproduction and bounded repair

Edge::angle(Vertex*, Vertex*) passes borrowed endpoints into a temporary Edge.
The original clears them only on successful return. Allocation failure during
later copied-Vertex construction/adjacency or final null-cache replacement
destroys caller vertices through the temporary's owning destructor.

The pinned original fails all ten new CRT sweeps with the explicit
`angle helper preserves every caller-owned endpoint` contract diagnostic. Its
previous 56 cases and both new successful ASan/CRT angle cases pass. The first
observed failing ordinal is 12 in every variant; no failed product case is
reclassified as an expected valid-case success.

The repair adds one automatic endpoint-detachment guard in edge.cpp and one
public borrowing-contract comment. The guard runs before the temporary Edge
destructor, allocates nothing and uses the existing noexcept detachment method.
All successful expressions, value copies, allocation order and destruction of
owned caches remain unchanged. See ADR-0007. The C11 architecture contract adds
this bounded exception guarantee; other helper and curve limits remain explicit.

| Caller adjacency | Endpoint branch | Observed allocation sites per sweep |
| --- | --- | ---: |
| Empty | Each of four shared-endpoint matches | 24 |
| Empty | Nonadjacent | 24 |
| Populated | Each of four shared-endpoint matches | 27 |
| Populated | Nonadjacent | 24 |

All **252 allocation ordinals** are denied exactly once across ten fresh-fixture
sweeps. Candidate cases require propagation, zero caller destruction, unchanged
caller coordinates/adjacency and receiver endpoints, cache identity/geometry,
ID and scalar state. A successful query after every caught failure qualifies
reuse only for this helper and these fixtures. Caller teardown destroys all four
endpoints exactly once. Valid CRT cases retain zero normal blocks/bytes.

Independent atan2 geometry for 3-4-5 triangles checks all four matching branches;
the fifth branch must return -1. Empty/populated adjacency are separate cases.
Original and candidate complete address-free success traces are identical in
each instrument, and all successful allocation counts match. Populated adjacent
cases have additional measured copy allocations; the nonadjacent branch does
not copy observers. Allocation counts are toolchain observations, not constants
enforced on a different standard-library implementation.

## Required delivery gates and commands

Normal CTest now contains **16 tests**, zero skips, including required
application.uv_angle_contracts and the unchanged 74 Python controls. Instrument
qualification contains **68 UV** cases and **seven previous node** cases.
The runner rejects empty/duplicate normal angle coverage and zero-denial sweeps.
Six-unit selected lint, explicit changed-range formatting, fresh inventory and
strict repeated Eistute/Book regression remain required. Inventory: 123 C++
files, five CMake inputs, 22 contracts and 95 source anchors; the inherited
six-header cycle and warning debt remain.

The native Windows serial application uses GCC 16.1.0, C++17 Release, Ninja,
MPI/OpenMP/LTO off and static MinGW runtime. LLVM format/tidy is 22.1.8.
Narrow instruments use MSVC 19.44.35229.0 with separate ASan RelWithDebInfo and
Debug CRT builds. ASan does not inject allocation denial here; CRT supplies that
experiment. No full-application, Linux LSan/UBSan or broad MSVC claim is made.

Command interfaces used by the local campaign, with the intended toolchain on
PATH (repeat_generation.repeat is called directly with the equivalent arguments):

```text
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose --output-junit <fresh-phase>/ctest.xml
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
cmake -S tests/uv_memory -B build/u6a -G "Visual Studio 17 2022" -A x64 -DAP_MESH_UV_ASAN=ON
cmake --build build/u6a --config RelWithDebInfo --parallel 2
cmake -S tests/uv_memory -B build/u6d -G "Visual Studio 17 2022" -A x64
cmake --build build/u6d --config Debug --parallel 2
python tools/qualify_uv_lifetime.py --asan build/u6a/RelWithDebInfo/uv_lifetime_probe.exe --crt build/u6d/Debug/uv_lifetime_probe.exe --runtime <MSVC-bin/Hostx64/x64> --output <fresh-phase>/uv
python tools/qualify_node_lifetime.py --asan build/n6a/RelWithDebInfo/node_lifetime_probe.exe --crt build/n6d/Debug/node_lifetime_probe.exe --runtime <MSVC-bin/Hostx64/x64> --output <fresh-phase>/node
python tools/quality.py tidy src/crab_mesh/aft/advancing_front.cpp src/crab_mesh/aft/boundary.cpp src/crab_mesh/aft/edge.cpp src/crab_mesh/aft/face.cpp src/crab_mesh/aft/quadtree.cpp src/crab_mesh/aft/quadtree_cell.cpp --build build/windows-gcc17
clang-format --dry-run --Werror tests/uv_memory/probe.cpp
clang-format --output-replacements-xml --lines=474:477 src/crab_mesh/aft/edge.cpp
clang-format --output-replacements-xml --lines=101:101 include/crab_mesh/aft/edge.h
python tools/repeat_generation.py --exe build/windows-gcc17/bin/ap_mesh.exe --model <eistute|book> --output <fresh-phase>/<model> --report <fresh-report.json>
```

windows-gcc17 is an ignored local preset inheriting local-serial with a separate
GCC build directory, explicit CMAKE_CXX_STANDARD=17, compiler/Ninja paths and the
same serial flags. It preserves the existing MSVC local-serial cache. Node
standalone build commands follow STAGE3_NODE_LIFETIME.md with build/n6a/n6d.
Original builds use build/u6oa/u6od, the same flags and final probe, with
AP_MESH_UV_SOURCE_ROOT pointing to the verified entry snapshot.

Each article model requires two exact repetitions and strict entry comparison
over all nine attempted states, positive shared-incidence coverage and zero
measured gap. Acceptance remains steps 0/1; rejected Eistute steps 2/3/4 and Book
steps 2/3 remain visible. Last accepted triangles must stay 1,168/4,256 and all
189 independently named CSV fields must match. No oracle/tolerance change.

## Candidate results

The complete local candidate passes CTest 16/16, zero skips, 74 Python controls,
UV 68/68, node 7/7, six-unit selected lint, all selected formatting checks and
inventory. Eistute/Book each repeat twice and match entry over all nine attempted
states with measured incidence coverage, unchanged acceptance/rejection and
1,168/4,256 final accepted triangles. All 189 named CSV fields pass the separate
analysis-log audit. Candidate executable SHA-256:
`68cf0e9985ff314502e7146dc76eb02d9a863d63c73a0166d93c9f2f20398d83`.
The qualification-input identity digest is
`07e509f2a985fdcf36542da2b986cc86fb157cfa0afc9d16bdd64afe42b50452`.
See stage3/angle_helper/candidate_qualification.json and source_identities.json.
This identifies the earlier working candidate. Published-head and post-merge
validation subsequently passed; the closure record preserves those identities.

## Failure history, audit and remaining scope

The original failed allocation cases and positive successful traces are retained
separately. The first local candidate collector could not recognize a completed
selected-lint coverage marker because PowerShell redirection encoded the log as
UTF-16. A second collection attempt exposed the same encoding issue. The
collector now decodes that raw log correctly; only hash-verified passing gates
with unchanged inputs were reused, then remaining gates continued. Both failed
collection records and hashes remain evidence. The actual selected lint passes;
no diagnostic, assertion, timeout or scientific policy was relaxed.
The retained candidate lint text is an explicitly whitespace-normalized UTF-8
derivative; its original UTF-16 raw hash remains in the qualification record.

Code, tests, C11 contract, source inventory, documentation, scientific scope and
failure/coverage limits are reviewed together. Complete exact-head and implementation-main
campaigns subsequently passed; see STAGE3_ANGLE_HELPER_CLOSURE.md. Compact reports and source/
input/executable/log identities are retained under stage3/angle_helper/; large
raw campaigns remain local with hashes rather than being described as complete
archived logs.
Verbose CTest logs and JUnit files remain in their local phase directories;
the public reports retain their hashes, exact test inventory and outcomes.

Doxygen 1.18.0 is installed. The submitted initial documentation run failed on
undocumented members; it is not a documentation pass or a new memory failure.
Comprehensive documentation remains stage 8 with warnings still enforced.

Next characterize remaining helper/mutation scopes and curve-internal allocation
failures, then parametric midpoint replacement and sample/initialization/rollback
ownership. General copied observers, other setters/templates/tree/mate paths,
failed-tree observer consumption/retry, full-process and parallel/LSan/UBSan
qualification remain open. Stages 0-2 stay closed; stages 4-11 stay pending.
