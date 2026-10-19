# Stage 3 slice 20: SubMesh raw element adoption

Status: candidate; exact-head and implementation-main qualification pending.
Entry main: `e3b6514d0dc9c8ce1b9c3544bbdb9771113957eb`.

## Cause and ownership repair

SetElement previously emplaced a raw pointer into vector<unique_ptr<ElementAdaptive>>.
The vector can allocate before constructing that owner. If allocation fails,
the relinquished argument is abandoned. AddElement already takes an owning
argument by value and correctly destroys it on failure.

SetElement now delegates through AddElement(std::unique_ptr<ElementAdaptive>(element)).
Ownership is established before allocation. Success preserves object address,
ordered insertion, existing slots, numerical fields and null-slot behavior.
Failure destroys the consumed argument once and preserves existing owned slots.
There is no new ownership concept, shared ownership, metadata snapshot or retry.
SetNoh remains a borrowed-source copy operation with distinct semantics.

Classification: behavior-changing resource-lifetime defect repair. No formula,
floating-point order, boundary synchronization, quadtree/templates/front,
budget, tolerance, adaptation, acceptance or stopping change. Deletion timing
on failure intentionally changes; no unchanged-allocation/performance claim.
Explicit formatting selects only the changed production header/unit and new probe.

## Constructor observers and terminal boundary

TriangleAdaptive registers itself in three node adjacency lists before adoption.
Its destructor does not remove those entries. Consequently, destruction of a
failed argument can leave an expired last observer until the enclosing private
mesh is destroyed. This also occurs with the already owning AddElement entry.
The repair does not establish exceptional adjacency reuse or restore the graph.

The driver gives the complete fixture a scope owner. It checks existing owned
node/element identities and the live adjacency prefix without reading or
dereferencing the failed argument observer. That owner automatically unwinds
before the outside driver handles bad_alloc. All elements and nodes are then
destroyed without allocation; node list destruction clears observer entries
without dereferencing them. No manual fallback cleanup, exceptional retry or
production recovery policy is added. The CLI's terminal-exception policy stays.

Failures inside TriangleAdaptive construction before entry, general triangle
removal/ReplaceNode/observer lifetime and populated SubMesh move assignment are
not qualified by this insertion repair. These constraints prevent a terminal
resource-cleanup result from being presented as live-graph rollback.

## Actual-unit evidence

The original source/include/vendor snapshot contains 476 Git-verified blobs at
entry main. Both versions compile the actual six production units (SubMesh,
NodeAdaptive, PointAdaptive, ElementAdaptive, TriangleAdaptive, VectorAdaptive)
with the same probe; no implementation adapter. Separate MSVC ASan
RelWithDebInfo and Debug CRT builds consistently disable debug iterator metadata
only for this target. Original and candidate checks use actual heap controls.

The new inventory has 31 outcomes: sixteen normal ASan/CRT cases, eight complete
positive allocation sweeps, four measured spare-storage paths, and actual ASan
UAF/CRT leak/hook controls. Raw/owning APIs each cover empty/populated and
nonnull/null insertion. Null cases are semantic guards, not positive triangle
coverage. Real triangles have independent area 0.5, checked coordinates, IDs,
UV and ordered adjacency/slots. Move construction preserves addresses; counted
polymorphic destructors require each triangle before its nodes, once each.

Growth and spare-storage prefixes are discovered by counting actual allocations
in the actual SubMesh container; the probe does not assume a vendor capacity
sequence. The qualified CRT measures populated growth at prefix one and spare
storage at prefix five. Each growth case has one observed allocation; all eight
ordinals are denied once. Attempts equal ordinal+1 through full terminal owner
unwinding, with zero retained blocks/bytes in every valid candidate CRT case.
Four nonallocating paths attempt zero allocations with denial armed.

The original fails exactly two outcomes: raw nonnull growth in empty/populated
meshes. Each retains one triangle block/160 bytes after terminal fixture teardown.
The other 29 outcomes are expected, including the already owning API. All sixteen
complete normal observed sequences match; cleanup on raw insertion failure is
the deliberate behavior change.

Static call-site audit: nine raw element insertions remain, one in Adapter's
reconstruction, four in the OpenMP initial constructor and four in the estimator.
They supply newly constructed triangles. The current serial initial helper and
another Adapter path already use AddElement. This is not full caller exception,
constructor-before-entry or estimator-root qualification. The hidden estimator
owner/duplicate adoption finding retained in STAGE3_MESH_ADOPTION.md remains open.

## Commands

```powershell
. ./build/local-env.ps1
cmake -S tests/mesh_memory -B build/s20a -G "Visual Studio 17 2022" -A x64 -DAP_MESH_MESH_ASAN=ON
cmake --build build/s20a --config RelWithDebInfo --target element_adoption_probe --parallel 2
cmake -S tests/mesh_memory -B build/s20d -G "Visual Studio 17 2022" -A x64
cmake --build build/s20d --config Debug --target element_adoption_probe --parallel 2
python tools/qualify_element_adoption.py --asan build/s20a/RelWithDebInfo/element_adoption_probe.exe --crt build/s20d/Debug/element_adoption_probe.exe --runtime "C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64" --output build/element-adoption-qualification
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
python tools/quality.py tidy src/data/mesh/sub_mesh.cpp --build build/windows-gcc17
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
```

Use fresh output directories. Original reproduction uses the Git-verified entry
snapshot through AP_MESH_ADOPTION_SOURCE_ROOT in separate original builds and
the same probe. Windows ASan leak detection is disabled; Debug CRT supplies
retention measurements. No Windows ASan leak coverage is claimed.

## Retained environment failure

The first complete candidate attempt passed CTest 30/30 and the 999 instrument
outcomes, then failed the required lint gate because its shell had not loaded
build/local-env.ps1 and clang-tidy was absent from PATH. It did not run model
regression and is not successful qualification. Its report/log hashes and failure
are retained. The corrected full run loads the qualified local tool directories;
no source, diagnostics, budgets or acceptance requirements are relaxed.

## Delivery gates and closure audit

Candidate full campaign passes GCC build, CTest 30/30 (zero skips, 74 Python
controls), all fifteen batteries/999 expected outcomes, selected SubMesh-unit
lint/format/inventory and twice-repeated exact Eistute/Book accepted/rejected
comparisons. The new battery passes 31/31, eight complete growth denials and
four measured spare-storage paths; valid CRT cases retain zero blocks/bytes.
Exact published-head and post-merge main gates remain required before integration.
The new required CTest is
application.element_adoption_contracts; all fourteen prior batteries remain.
Compact reports, outcomes, command/raw-log hashes, toolchain and frozen inputs
are retained under stage3/element_adoption.

| Audit scope | Current result |
| --- | --- |
| Code | Raw entry delegates through existing owning argument before allocation |
| Tests | Actual-unit 31/31 outcomes; complete full/exact delivery pending |
| Contracts | C04/C05 and ADR-0021 require exclusive arguments and terminal teardown, without graph reuse |
| Documentation | Cause, original failures, constructor-observer limit and commands retained |
| Scientific scope | No formula/order/policy change; full accepted/rejected regression required |
| Known failures/coverage | Original two leaks retained; required unmeasured delivery gates block integration |

Stage 3 remains open. Next isolate TriangleAdaptive construction/adjacency
registration under allocation failure. Estimator hidden/duplicate ownership,
other constructors, populated mesh move assignment, logical rejection audit,
whole-process/parallel/LSan/UBSan and stages 4-11 remain open. Duplicate adoption,
arbitrary element subclasses/allocators and extreme allocation sizes are outside
the qualified valid contract.
