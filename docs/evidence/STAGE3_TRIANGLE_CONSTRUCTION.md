# Stage 3 slice 21: triangle construction and observer registration

Status: candidate; exact-head and implementation-main qualification pending.
Entry main: `b4177dd031a16bc748099c7db9a6dbf562228908`.

## Root cause and repair

The parameterized TriangleAdaptive constructor appends this to n1/n2/n3
adjacency lists in sequence. If a later allocation throws, new releases the
unfinished object's storage, but its destructor does not run. The already
published observers then refer to an object that was never fully constructed.
Final node destruction clears those list nodes, so an end-of-process leak check
alone misses this live-graph failure.

The constructor now catches construction exceptions, removes matching this
observers from all three live nodes without allocation and rethrows. The new
NodeAdaptive::RemoveElementObserver erases matching non-owning pointer entries;
it does not delete elements. Repeated vertices require no separate ownership
concept. Erasure preserves every unrelated list node, value/order/null marker
and node scalar field. A fresh object address must not already be registered.

Success retains the original n1/n2/n3 registration, angle1/angle2/angle3, normal
and area evaluation order. No formula, floating-point order, boundary sync,
quadtree/template/front, tolerances, budgets, adaptation/acceptance/stopping or
CLI retry change. Classification: behavior-changing exception-consistency repair.
Explicit formatting is limited to the node/triangle headers/units and new probe;
old identifiers/comments are not presented as a repository-wide translation.

Ordinary destruction of a successfully constructed triangle is unchanged and
does not unregister. Thus later failed element adoption still requires the
terminal teardown qualified in slice 20. Constructor restoration does not imply
general graph reuse after element destruction, ReplaceNode/copies/moves, or full
adaptive rollback. Nodes must be live and non-null with valid existing lists.

## Actual-unit evidence

The original snapshot has 476 Git-verified source/include/vendor blobs at entry
main. Original and candidate compile the actual five NodeAdaptive, PointAdaptive,
ElementAdaptive, TriangleAdaptive and VectorAdaptive units with the same probe;
no implementation adapter. MSVC ASan RelWithDebInfo and Debug CRT use separate
directories and consistent debug iterator settings only for this target.

Six vertex layouts cover distinct/reversed vertices, each repeated pair position
and all-identical vertices. Each has empty lists and populated lists containing
two actual live parent triangles with interleaved null markers. The oracle keeps
parent pointer order, physical list-node addresses, node IDs/coordinates and all
four curvature fields. Analytic area is 0.5 for distinct/reversed layouts and
zero for repeated-node lifecycle guards. Degenerate guards do not establish
geometric validity. Normal observations include adjacency multiplicities/IDs,
cached area and the same ordered angle evaluations.

The dedicated inventory contains 39 outcomes: 24 normal ASan/CRT observations,
twelve positive complete CRT allocation sweeps and deliberate ASan UAF/CRT leak/
hook controls. Every fixture calibrates four allocations: triangle storage and
the three list nodes. All 48 observed ordinals are denied once. Attempts equal
ordinal+1 through cleanup; candidate live and final CRT increments are zero.
Every denial preserves exact prior list-node/scalar identity before traversal
of live prior observers and a fresh component construction outside the hook.
This explicit test operation does not add production retry or ID rollback.

Original: all twelve sweeps fail restoration. Ordinals zero/one remain clean;
ordinals two/three leave one/two partial registrations (24/48 incremental live
bytes). All four ordinals are measured in independent fresh fixtures; there is
no unsafe traversal/fresh construction after a mismatching original state.
Final fixture destruction retains zero CRT blocks in those experiments, which
is not successful live-graph restoration. The other 27 outcomes are expected;
all 24 complete normal observation sequences match. Candidate passes 39/39.

## Commands and retained preparation findings

```powershell
. ./build/local-env.ps1
cmake -S tests/mesh_memory -B build/s21a -G "Visual Studio 17 2022" -A x64 -DAP_MESH_MESH_ASAN=ON
cmake --build build/s21a --config RelWithDebInfo --target triangle_construction_probe --parallel 2
cmake -S tests/mesh_memory -B build/s21d -G "Visual Studio 17 2022" -A x64
cmake --build build/s21d --config Debug --target triangle_construction_probe --parallel 2
python tools/qualify_triangle_construction.py --asan build/s21a/RelWithDebInfo/triangle_construction_probe.exe --crt build/s21d/Debug/triangle_construction_probe.exe --runtime "C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64" --output build/triangle-construction-qualification
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
python tools/quality.py tidy src/data/node_adaptive.cpp src/data/triangle_adaptive.cpp --build build/windows-gcc17
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
```

Use fresh outputs. Original builds set AP_MESH_ADOPTION_SOURCE_ROOT to the safely
exported, Git-verified entry snapshot and compile the same probe. Windows ASan
leak detection is disabled; Debug CRT measures live/final allocation increments.
The older node-lifetime target is explicitly rebuilt against current sources.

Explicit formatting changed spacing in one existing lexical inventory anchor;
the first inventory refresh failed and the reviewed literal anchor was corrected.
An initial orchestration runner was interrupted before test execution when review
found the new CTest count incorrectly copied into the unchanged prior 30-case
curve-copy inventory. Only that runner was stopped; its active CMake build was
allowed to finish normally. The prior expectation remains 30. Incomplete logs
and both preparation findings are preserved separately; neither is qualification.
No source diagnostic, test requirement or numerical acceptance rule was relaxed.

## Delivery gates and closure audit

Candidate full campaign passes GCC build, CTest 31/31 (zero skips, 74 Python
controls), all sixteen batteries/1038 expected outcomes, selected node/triangle
lint/format/inventory and twice-repeated exact Eistute/Book accepted/rejected
comparisons. The new battery passes 39/39, all 48 observed allocation denials,
exact old list-node/scalar restoration and safe live-observer/fresh-construction
checks. Exact published-head and implementation-main gates remain required.
New required CTest:
application.triangle_construction_contracts. The fifteen previous batteries
remain required. Compact reports, original outcomes, raw-log hashes, toolchain
and frozen inputs are retained under stage3/triangle_construction.

| Audit scope | Current result |
| --- | --- |
| Code | Narrow nonallocating observer erasure and failed-constructor cleanup; original success order preserved |
| Tests | Actual-unit 39/39, all 48 observed allocation denials; full/exact delivery pending |
| Contracts | C04/C05 and ADR-0022 distinguish constructor restoration from ordinary destruction/adoption failure |
| Documentation | Original partial publication, zero final leak limitation and preparation findings retained |
| Scientific scope | No formula/order/policy change; full accepted/rejected model regression required |
| Known failures/coverage | Original twelve failing sweeps retained; unmeasured required delivery gates block integration |

Stage 3 remains open. Next audit triangle destruction/observer lifetime together
with SubMesh destruction/move ordering before adding automatic deregistration.
ReplaceNode/copy/move semantics, estimator hidden/duplicate ownership, other
constructors, logical rejection, whole-process/parallel/LSan/UBSan and stages
4-11 remain open. Null/uninitialized sources, invalid stale input lists, arbitrary
subclasses/allocators and extreme sizes are outside the qualified valid contract.
