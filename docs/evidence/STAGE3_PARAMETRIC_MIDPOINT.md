# Stage 3 slice 7: parametric midpoint replacement

Issue #26. Entry main `b4090d05ff5ba11b64db3561f7ad38244145325a`, complete
tree `8bd9ab4b49b12e8a0ef2db2745c1eb731d59be7d` (864 blobs). Classification:
behavior-changing defect repair on allocation-failure exits. Full stage 3 stays
open; this is not a scientific proposal.

## Authority, entry and original

Remote audit found 18 branches, no open PRs/issues, check/status contexts or
Actions runs before the sole active item #26 was opened. All 864 working files,
including publication binaries, match indexed Git blobs. Original production,
headers and vendor were extracted at entry and all 460 blobs verified. Both
original and repaired targets compile the same final probe against 14 actual
UV/curve/numerical production units; no replacement curve or mesh generator is
introduced. The fixture initializes the actual polynomial evaluator through its
public coefficient setter and invokes its actual integration/bisection methods.

Fresh entry qualification passes the previous UV 68/68 and node 7/7 instrument
controls. Serial comparison reuses retained slice-6 implementation-main article
outputs; the complete compiled/tool/test/build/input/contract identities are
unchanged on entry documentation-main b4090d0. Its exact 16-test CTest and source
audit already pass. This is not a claim of a second fresh entry serial campaign.

The original fails all ten new CRT sweeps: at ordinal zero the old midpoint
has already been deleted. The explicit diagnostic is
`failed parametric replacement preserves midpoint identity and normalized length`.
Its previous 68 controls, both new normal instrument cases and the direct curve
allocation observation pass. Deliberately invalid prior controls retain their
expected failures/diagnostics; they are not valid application executions.

## Repair and measured contracts

Only edge.cpp and its contract header change in production. A local unique_ptr
owns the prepared midpoint and a double stores prepared normalized length.
After complete preparation, the old midpoint is deleted and both values commit.
Allocation failure preserves the previous cache identity/geometry and length,
caller endpoints/adjacency and receiver ID/scalar state. Every caught failure
is followed by a successful replacement; caller endpoints are destroyed once.

Destruction of the previous cache is deliberately delayed until commit. Old and
new cache objects coexist during preparation; allocation address reuse and peak
memory are not promised. All successful allocation counts and allocation order,
midpoint/arc expressions, incidence direction, integration/bisection operations,
tolerances, stopping and null/fallback behavior are preserved. Curve scratch
parameters remain mutable and are outside the transaction. See ADR-0008 and C11.

| Cases | Coverage | Observed allocations per sweep |
| --- | --- | ---: |
| Variants 0-7 | Four patch sides, both curve-incidence directions | 3 each |
| Variants 8-9 | Interior fallback, both association directions | 3 each |
| Variant 10 | Null curve: old midpoint/length remain unchanged | No failure sweep |

Ten sweeps deny all **30 measured ordinals**, exactly once each, in fresh
fixtures. Original/candidate counts must match; these are MSVC observations,
not constants required of another compiler. Valid CRT scenarios require zero
normal retained blocks/bytes. No arbitrary curve exception or failed-tree
reuse/observer-consumption claim follows from successful replacement retry.

## Independent numerical and instrument coverage

For x(t)=0.3t+0.6t^2+0.1t^3 on a straight physical curve, five position and
gradient samples, signed arc integrals and a physical midpoint are checked
against independent scalar formulas and an 80-step inverse. Direct position/
gradient/integral bounds are 1e-12. The midpoint bound is the unchanged solver
TOLERANCE divided by the independent minimum derivative 0.3. Existing constructor,
orientation and corner controls keep their original stricter bounds unchanged.
All 11 normal replacement cases and complete address-free original/candidate
traces must agree separately in ASan and Debug CRT.

Measured direct point/gradient, arc and midpoint operations observe **zero
allocations**. They supply numerical observations only; allocation-failure
coverage inside those operations is explicitly **unmeasured**. Required prior
allocation-hook denial, UAF/shared deletion and retained-block controls still
prove the instruments respond. No zero-denial sweep is accepted as qualification.

Current candidate inventory: CTest **17** with zero skips and 74 Python controls;
UV **81** instrument cases; previous node **7** cases. Required
application.uv_parametric_contracts checks five analytic samples, four sides in
both directions, interior fallback and null-curve behavior. The runner rejects
empty, duplicate or missing normal-case coverage and zero-denial failure sweeps.
Selected lint retains six real AFT units with unchanged rules; changed production
ranges and the complete probe are formatted explicitly. Inventory contains 123
C++ files, five CMake inputs, 22 contracts and 96 anchors. Legacy warning debt
and the six-header include cycle remain.

## Toolchain, commands and delivery gates

Native Windows GCC 16.1.0, C++17 Release, Ninja, MPI/OpenMP/LTO off, static MinGW
runtime; LLVM 22.1.8. Actual narrow instruments use MSVC 19.44.35229.0 with
separate ASan RelWithDebInfo and Debug CRT builds. These do not qualify the
whole application for MSVC, Linux LSan/UBSan or arbitrary allocation failures.

Commands use the established ignored windows-gcc17 preset, isolated from the
preserved MSVC cache. Its compiler, Ninja and C++17/serial options are recorded
in the slice-6 local-environment evidence. Relevant interfaces:

```text
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose --output-junit <fresh-phase>/ctest.xml
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
cmake -S tests/uv_memory -B build/u7a -G "Visual Studio 17 2022" -A x64 -DAP_MESH_UV_ASAN=ON
cmake --build build/u7a --config RelWithDebInfo --parallel 2
cmake -S tests/uv_memory -B build/u7d -G "Visual Studio 17 2022" -A x64
cmake --build build/u7d --config Debug --parallel 2
python tools/qualify_uv_lifetime.py --asan build/u7a/RelWithDebInfo/uv_lifetime_probe.exe --crt build/u7d/Debug/uv_lifetime_probe.exe --runtime <MSVC-bin/Hostx64/x64> --output <fresh-phase>/uv
python tools/qualify_node_lifetime.py --asan build/n6a/RelWithDebInfo/node_lifetime_probe.exe --crt build/n6d/Debug/node_lifetime_probe.exe --runtime <MSVC-bin/Hostx64/x64> --output <fresh-phase>/node
python tools/quality.py tidy src/crab_mesh/aft/advancing_front.cpp src/crab_mesh/aft/boundary.cpp src/crab_mesh/aft/edge.cpp src/crab_mesh/aft/face.cpp src/crab_mesh/aft/quadtree.cpp src/crab_mesh/aft/quadtree_cell.cpp --build build/windows-gcc17
clang-format --dry-run --Werror tests/uv_memory/probe.cpp
clang-format --output-replacements-xml --lines=542:614 src/crab_mesh/aft/edge.cpp
clang-format --output-replacements-xml --lines=115:116 include/crab_mesh/aft/edge.h
```

Original builds use u7oa/u7od with identical flags and final probe, setting
AP_MESH_UV_SOURCE_ROOT to the verified snapshot. Node sources are unchanged.
The campaign invokes repeat_generation.repeat directly with the established
executable/model/fresh-output/300-second interface. Both models require two
exact repetitions and strict entry comparison over all nine attempted states,
positive incidence coverage, zero measured position gap, unchanged accepted
steps 0/1 and rejected Eistute 2/3/4 and Book 2/3. Final accepted triangles stay
1,168/4,256 and 189 separately audited named CSV fields must agree.

Exact published-head and post-merge complete campaigns remain required before
slice closure. The public reports retain source/input/executable/toolchain and
raw-log hashes, full case inventories and failed original diagnostics. Large
instrument and verbose CTest/JUnit logs remain local with hashes. No hosted
checks or paid Actions are configured. No oracle, tolerance or policy is relaxed.

## Remaining boundary

Audit code, tests, C11, documentation, scientific scope and failure/coverage
limits before closure. Other curve mutations and constructor/setter failures,
shared sample/initialization/rollback ownership, general observers, other helper/
template/tree/mate paths and full-process/parallel/LSan/UBSan remain open.
The zero-allocation numerical examples do not close curve-internal failure
qualification. Doxygen 1.18.0 undocumented-API debt stays in stage 8.

## Candidate outcome

All candidate delivery gates pass with no skips: CTest 17/17, 74 Python
controls, UV 81/81, node 7/7, six-unit selected lint, formatting, inventory,
exact repeated generation and strict entry comparisons. The normal scientific
outputs remain unchanged despite the explicit delay of old-cache destruction.
Application SHA-256: `04bbfdb9d4d9aa38e6c5c50a1e382af9162fe6a1df1c64dbb2e30d547c891ac9`.
Qualified input identity: `5bbab057eaa92a9c2de31d7c15319b4ad617e5e8c53da02fa3cfce838e6d7a44`.
Full candidate and original failed reports, successful traces and exact source
maps are retained in stage3/parametric_midpoint/. Published-head/main campaigns
remain required before closure.
