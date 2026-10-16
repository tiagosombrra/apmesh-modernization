# Stage 3 slice 2: registered UV template ownership and teardown

Issue #11. Entry main: `0f2473622800907e2d15e1d5ab6216caedb36797`;
tree: `ddde9c8a1ebb930c2890b0cc098ec698beb1cf1c` (685 blobs).
Classification: demonstrated engineering lifetime/portability repairs, with no
observed scientific output change. The full stage 3 remains open.

## Entry audit and controlled reproduction

Remote main, eight branches, PRs, issues and checks were audited before writing.
No concurrent PR/work item or hosted workflows/checks existed. All 683 local
text blobs matched entry; two immutable remote-only publication binaries remain
preserved. Entry CTest 10/10 and Eistute/Book repetitions passed. Strict entry
comparison with the previous qualified slice also passes.

The narrow target compiles 14 actual UV/curve/numerical production units, without
stubs. Its original implementation/header/vendor snapshot contains 416 files,
all matched against pinned Git blobs. The final probe is shared by baseline,
candidate and normal CTest. Runtime diagnostics and source identities are
retained under `stage3/uv/`.

| Required case | Pinned original observation | Repaired observation |
| --- | --- | --- |
| Successful square generation | 104 faces, 24 templates; CRT zero retained blocks | Same counts, ASan pass, CRT zero retained blocks |
| Incomplete boundary and partially populated front | Valid cleanup control passes | Shared endpoints destroyed exactly once |
| Geometry-phase failure after actual templates | 1,363 CRT blocks / 61,584 bytes retained | Zero retained blocks/bytes |
| Exception unwind after actual templates | Same 1,363 blocks / 61,584 bytes | Zero retained blocks/bytes |
| Topology fallback failure after templates | Same 1,363 blocks / 61,584 bytes | Zero retained blocks/bytes |
| Standalone quadtree with untransferred templates | 1,515 blocks / 68,464 bytes retained | Zero retained blocks/bytes |
| Midpoint aliases an owned front endpoint | ASan heap-use-after-free; CRT process fails | Three endpoints destroyed once, no invalid access/leak |
| Destructor with every allocation denied | Controlled terminate exit 73 | Zero allocation attempts, normal completion |
| Actual observer-preparation allocation failures | Owner-transfer contract fails | First/middle/last measured sites throw to caller; all owners stay at source; CRT zero retained blocks |
| Ordered handoff and repeated empty handoff | Source owner views not consumed | Identical addresses and append order; no duplicate owners |

The current MSVC Debug transfer fixture observes 342 allocating operations and
injects three failures. This is a measured fixture count, not a portable library
invariant. Its allocation hook has a separate deliberate-allocation control.
Independent deliberate UAF/duplicate-endpoint deletion remain detected by ASan;
a deliberate Vertex leak is detected as three CRT blocks / 112 bytes. The same
unrelaxed runner reports the original **failed** and the repaired **26/26 passed**.

The square supplies normalized edge sizes normally provided by straight unit
curve integration. An early null-curve test fixture omitted those required sizes
and caused invalid refinement/abnormal exits; that failed setup is retained in
`fixture_setup_failure.json` and excluded from product-defect conclusions. The
qualified fixture generates template type counts **20,0,0,4,0,0**. It exercises
types 1 and 4; it does not qualify every template pattern.

## Repair and source audit

Quadtree now owns registered template output until the front commits ordered
owner lists using nonthrowing list splices. Allocating observer preparation
happens first. Quadtree cleans pending payload on failure/abandonment; successful
front ownership consumes those source lists exactly once. getMesh/getEdges/
getVertices are borrowed pointer views and are empty at the quadtree after
handoff. Every production consumer was reviewed: pre-fill observation and
post-fill leaf/template statistics retain their behavior.

Boundary/quadtree/front cleanup calls allocation-free DetachVertices. A Face
releases an endpoint-alias midpoint before dropping endpoint pointers, while
distinct caches remain owned. Legacy Face/Edge raw endpoint adoption outside
shared containers remains; Adapter old UV faces still rely on that behavior.
See [ADR-0003](../decisions/ADR-0003-registered-uv-template-ownership.md).

Actual MSVC compilation initially failed because NOMINMAX followed winsock2,
which can already define Windows min/max macros, and because __LONG_MAX__ is a
GCC extension. The Windows guard now precedes both Windows headers; LONG_MAX
provides the standard bound. A GCC static_assert proves LONG_MAX == __LONG_MAX__
in this toolchain. Original sources are instrumented with the two explicit
compatibility defines; repaired builds need neither. Both targets enable /EHsc.
These are minimal stage 4 prerequisites, not full-application MSVC or C++23
qualification. Build blockers and flags are retained in the evidence manifest.

The first full selected lint run failed on 32 nullptr and nine override
diagnostics. A reviewed batch updates 41 pointer-only source lines and seven
related headers; all existing override relationships remain. No clang-tidy
automatic fixes or diagnostic suppressions were used. The final five selected
production units and their first-party headers pass the unchanged lint rules.
Legacy/vendor/check-filter warning debt remains; no repository-wide lint pass
is claimed. Changed production ranges and the whole new probe pass formatting.

The production scope is five implementation files, seven AFT headers and the
Windows definitions header. Template-selection implementation, formulas,
thresholds, ordering, curve partitions, physical mapping, front/smoothing,
adaptation/acceptance/stopping policies and all independent numerical verifiers
are preserved. Explicit formatting accompanies the reviewed changes.

## Candidate validation and commands

GCC 16.1.0 serial C++17 Release, MPI/OpenMP/LTO off; CMake/CTest 4.4.3.
MSVC 19.44.35229 ASan RelWithDebInfo and separate Debug CRT. CTest **11/11**,
zero skips, **74 Python controls**, existing invalid-input/orientation/analytic/
verifier-negative/analyzer-scope controls and the new UV lifecycle probe pass.
The probe runs ten fresh repetitions of six scenarios, then transfer/alias
contracts. The previous node boundary also passes all seven instrumented cases.

Eistute and Book repeat exactly twice and compare strictly to entry for all nine
attempted states. Positive shared-incidence coverage, zero measured position
gap, all OBJ and acceptance/CSV/incidence results are retained. Both accept steps
0/1; last accepted triangles remain **1,168 / 4,256**. Named CSV audits compare
**189 fields** with zero differences. No tolerance or oracle was relaxed.
Current application SHA-256:
`6cbb57bbfed033ebf5b8b11a359a628fbf92b1d1273fab357ca94511f026a8e8`.
Source inventory: 122 production C++ files, five CMake inputs, 22 contracts and
83 anchors. [Final candidate report](stage3/uv/final_qualification.json).

```text
cmake -S tests/uv_memory -B build/uv-msvc -G "Visual Studio 17 2022" -A x64 -DAP_MESH_UV_ASAN=ON
cmake --build build/uv-msvc --config RelWithDebInfo
cmake -S tests/uv_memory -B build/uv-crt -G "Visual Studio 17 2022" -A x64
cmake --build build/uv-crt --config Debug
python tools/qualify_uv_lifetime.py --asan build/uv-msvc/RelWithDebInfo/uv_lifetime_probe.exe --crt build/uv-crt/Debug/uv_lifetime_probe.exe --runtime <MSVC-bin/Hostx64/x64> --output <fresh-directory>
cmake --preset local-serial
cmake --build --preset local-serial
ctest --preset local-serial --output-on-failure
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
python tools/quality.py tidy src/crab_mesh/aft/advancing_front.cpp src/crab_mesh/aft/boundary.cpp src/crab_mesh/aft/edge.cpp src/crab_mesh/aft/face.cpp src/crab_mesh/aft/quadtree.cpp --build build/local-serial
python tools/repeat_generation.py --exe build/local-serial/bin/ap_mesh.exe --model <eistute|book> --output <fresh-directory> --report <report.json>
```

## Closure boundary and remaining work

Code, contracts, tests, source identities, source inventory, scientific scope
and failure inventory are audited at this candidate checkpoint. Exact published
head and post-merge gates are still required before work-item closure. Large CRT
object dumps stay local with raw hashes; compact diagnostic excerpts and failed
baseline status are retained. Missing ASan leak coverage is not treated as a
pass: separate CRT retained-block measurements provide the bounded evidence.

Next qualify allocation failures during UV object creation before registration
and constructor/setter replacement. Adapter temporary scopes, curve sample/
initialization ownership, rollback, same-front execute reuse, mate/root sharing,
generic node adjacency and cache mutation, full-process leaks, parallel modes,
Linux LSan/UBSan, all template patterns, Decor Shelf and every internal retry
remain open. Stages 4-11 remain pending for their full scope.
