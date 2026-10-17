# Stage 3 slice 8: curve collection transactions

Issue #29. Entry main b7b96b8d397d754606423694e73a5bc46b9f2134, complete tree
cd9fefbe5315397fa39a9cd62f5b14d24f64c8f4 (900 blobs). Exceptional-exit defect
repair; no scientific proposal. Remote audit found 20 branches, no open PRs or
issues, no check/status contexts or Actions runs before opening the sole item.
All entry working bytes match Git. Original production/header/vendor snapshot
contains 460 verified blobs; the historical repository is untouched.

## Entry, original and repair

Fresh entry UV 81/81 and node 7/7 controls pass. Entry serial baseline reuses
retained slice-7 implementation-main 61dc86ecaeede57ec838a5bb754f237b2013085a
article outputs: all 507 qualified inputs are unchanged on entry documentation-
main b7b96b8. Its exact CTest and complete checkout already pass. No second fresh
entry serial generation is claimed.

Both populated-growth original setter cases fail at denied ordinal 7, with
`failed collection replacement preserves ordered live values`. The other 17
instrument outcomes, including deliberate invalid controls, are as expected.
The two collection setter bodies and their contract comments change in
production; three existing local distance-function overrides become explicit
to satisfy unchanged lint rules. Each setter swaps its prepared by-value list.
There is no formula, floating-point ordering, input, solver, vendor, verifier,
tolerance, adaptation/acceptance/stopping, template/front or source attribution
change. C07 and ADR-0009 define the ownership and exception boundary.

Preparation failure preserves live ordered values/nodes, caller lvalue inputs,
point ID/XYZ, curve ID/length/coefficients and patch identity. Retry succeeds.
Successful list-element iterators/references are invalidated; the container
reference survives. Borrowed point/patch objects remain caller-owned and are
destroyed once by their actual owners. Null and repeated point observers are
preserved, not deduplicated. Empty, shrink, equal-size, clear and self-alias
behavior remain visible. Rvalue success is measured separately from lvalue
denial sweeps. Point and parameter replacements remain independent transactions.

The second copy is deliberately removed. Original/repaired successful list
allocation counts and list-node reuse are not claimed identical. Old nodes
are destroyed after swap at function exit. Reviewed serial callers in Adapter
and Generator do not consume old element iterators across replacement calls;
general external observer compatibility is not qualified.

## Measured inventory

| Scope | Original counts | Repaired counts | Failure qualification |
| --- | --- | --- | --- |
| Each setter: populated growth, empty growth | 10, 12 | 7, 7 | Original populated growth fails; all repaired ordinals pass |
| Each setter: shrink, equal-size, clear, self-alias | 4, 5, 2, 5 | 4, 5, 2, 5 | All calibrated ordinals pass |
| Base/parametric pointer-taking copy | 7, 9 | 7, 9 | Positive unwind controls; caller state retained |
| Each setter: rvalue input | Normal ordered-result control | Same normal trace | Not an allocation-failure sweep |

Counts are MSVC observations, not portable constants. The 14 independently
calibrated sweeps deny 76 actual ordinals (60 setters, 16 constructors), exactly
once each, in fresh fixtures. Zero-denial sweeps are rejected. There are 14 normal
setter variants and two normal copy controls per instrument. Curve qualification
has 19 cases, including deliberate ASan UAF, CRT retained-block and denial-hook
controls. Prior UV 81 and node seven cases remain required. Scoped valid CRT
retention is zero; Windows ASan does not measure LSan or full-process leaks.

The new probe compiles seven actual curve/point/patch/numerical production units,
without a replacement curve implementation. Constructor assertions concern
borrowed collections and initialized scalar/coefficient state only. Static review
shows the pointer-taking parametric constructor omits parameters_; its full
value-copy semantics, implicit copy/assignment and derived constructors remain
open. No numeric/allocation-failure qualification is inferred from that omission.

Candidate CTest 18/18, zero skips and 74 Python controls pass, including the new
application.curve_collection_contracts. Selected lint covers both actual curve
implementations and their compiled configurations with unchanged rules. New
probe and changed production ranges are explicitly formatted. Production
inventory remains 123 C++ files (57 units, 66 headers), now six CMake inputs,
22 contracts and 98 anchors; the known six-header cycle remains.

## Regression and commands

Native Windows GCC 16.1.0 serial C++17 Release, MPI/OpenMP/LTO off and static
MinGW runtime; LLVM 22.1.8. Separate MSVC 19.44.35229.0 ASan RelWithDebInfo and
Debug CRT builds remain isolated from the GCC preset and preserved MSVC cache.
Toolchain and actual configurations are retained. Reproduction interfaces:

```text
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose --output-junit <fresh-phase>/ctest.xml
cmake -S tests/curve_memory -B build/c8a -G "Visual Studio 17 2022" -A x64 -DAP_MESH_CURVE_ASAN=ON
cmake --build build/c8a --config RelWithDebInfo --parallel 2
cmake -S tests/curve_memory -B build/c8d -G "Visual Studio 17 2022" -A x64
cmake --build build/c8d --config Debug --parallel 2
python tools/qualify_curve_collections.py --asan build/c8a/RelWithDebInfo/curve_collection_probe.exe --crt build/c8d/Debug/curve_collection_probe.exe --runtime <MSVC-bin/Hostx64/x64> --output <fresh-phase>/curve
python tools/quality.py tidy src/data/curve/curve_adaptive.cpp src/data/curve/curve_adaptive_parametric.cpp --build build/windows-gcc17
clang-format --dry-run --Werror tests/curve_memory/probe.cpp
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
```

Original c8oa/c8od builds use the same final probe with AP_MESH_CURVE_SOURCE_ROOT
set to the verified original snapshot. Prior UV targets are rebuilt because they
consume the repaired curve units. Node production inputs are unchanged.
Two repetitions per article model use repeat_generation.repeat with the existing
300-second interface, strict boundary verification and independent CSV audit.
All nine attempted states, positive shared-incidence coverage, zero measured
position gap, acceptance/rejection and 189 named CSV fields match entry exactly.
Accepted steps stay 0/1, rejected Eistute 2/3/4 and Book 2/3 remain visible;
last accepted triangles remain 1,168/4,256. No acceptance criterion is relaxed.

## Setup failures, retained evidence and remaining gates

Both first original instrument builds failed because the new probe included
Windows before the established winsock2/windows include ordering. Their raw
UTF-16 identities and readable derivatives remain in setup_failure_inventory.json.
The aggregate shell's zero exit followed log reads and was not MSBuild success.
Removing that redundant probe include repairs setup; no production header,
diagnostic rule or assertion is suppressed. Corrected original builds were then
rebuilt against the final probe and both original defect failures reproduced.

The first candidate required lint gate failed on three missing override
annotations in the legacy local DistanceFunction (min/max/f). CTest 18/18 and
all curve/UV/node controls already passed, but that campaign stopped before
article generation and is not a qualification pass. Its failed report and raw
tidy log are retained as candidate_lint_failure.json and candidate-lint-failure.log.
Adding only those three override annotations and refreshing the source inventory
unblocked the unchanged analyzer rules. The complete fresh candidate campaign
then passed; no hidden retry of unchanged failed sources is claimed.

Compact candidate/entry/original reports, all original raw case logs, snapshot
maps and toolchains are retained in stage3/curve_collections/. Large candidate
instrument and verbose CTest/JUnit logs remain local with hashes. Exact published-
head and implementation-main complete campaigns remain required before closure.
No hosted checks or Actions are configured. Audit code/tests/contracts/docs,
scientific scope and the failure/coverage inventory before closing this item.

Other curve constructor/mutation contracts, the parametric copy parameter
sequence, shared samples, initialization/rollback, general observers, joint
transactions and full-process/parallel/LSan/UBSan remain open. Stages 0-2 stay
closed; full stage 3 remains open; stages 4-11 remain pending. Doxygen 1.18.0
undocumented-API debt stays in stage 8.

Candidate input identity: `bb9dd855eb009e45ee9f27947ee159dda47aeacf16d88caac23ceb171ff91e01`.
Application SHA-256: `ad3cee6210c2a865c94422a98a70d682140cc351ce836ef5002f2066d46b085b`.
