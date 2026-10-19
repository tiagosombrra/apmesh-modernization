# Stage 3 slice 24: completed-triangle observer cleanup

PR #70 integrates head `7d22766e562669db283bedbf09fab59663546d18` as main
`78bc1ff045bcabebc3ac5536e53a1a87182ad365`, preserving complete tree `fc0ea5c79c4a6a42a78ce70b8a1f199c6fc8c71c`
(1805 blobs). Full exact-head/main campaigns pass with the same 559 protected
inputs: CTest 34/34, zero skips, 74 Python controls, nineteen memory batteries/
1137 expected outcomes, triangle lint/format/inventory and exact twice-repeated
Eistute/Book accepted/rejected traces.

Entry main: `1d3aeb55e2c0aaced170f206f07d2bee4661b92a`.
Classification: behavior-changing observer-lifetime defect repair; no scientific proposal.

## Root cause, lifetime audit and repair

TriangleAdaptive construction publishes its address in three node lists. The
completed object's destructor was empty. Deleting it, including destruction of
an argument consumed by failed SubMesh vector growth, left expired addresses in
live nodes. End-of-fixture node destruction cleared those list nodes, so zero
final Debug CRT retention concealed the live-graph defect. A separate actual-unit
ASan experiment traverses node adjacency after deletion and reproduces a real
heap-use-after-free in ElementAdaptive::GetArea on the original sources.

The destructor now removes matching this observers from each non-null current
vertex using the existing nonallocating NodeAdaptive removal method. This releases
only observer list nodes; it does not delete borrowed nodes or other elements.
Repeated vertices are idempotent, all-null default destruction is safe, and base
destruction runs after a controlled derived constructor throws. Copy/move value
transfer remains disabled. ReplaceNode already transfers exactly one observer
and updates the first matching vertex, so destruction follows the current nodes.
Constructor-failure rollback remains unchanged and separately qualified.

Borrowed nodes and valid lists must outlive the complete triangle, including its
virtual destructor. SubMesh already declares elements after node owners, releasing
elements first; slice 22 also repairs populated move assignment. Current production
registration calls occur only in TriangleAdaptive construction. Adapter and
initial/estimator paths construct triangles from physical nodes owned by SubMesh.
Serial Model releases complete meshes, while curve sample owners release distinct
sample objects rather than the copied physical vertices. Current fixtures retain
actual vertex owners until after triangle owners. This is a bounded source audit,
not full-process/parallel or external-client proof; see caller_audit.json.

No arbitrary protected vertex mutation, foreign copied observer-list cleanup or
expired raw pointer recovery is attempted. General NodeAdaptive value copying can
retain observers in nodes outside the triangle's current vertex set; those lists
are not globally scanned. No shared ownership, registry, metadata snapshot, CLI
retry or change to consumed IDs is added. Formulas, floating-point order, caches,
UVs, boundary synchronization, quadtree/templates, advancing-front reconstruction,
adaptation/acceptance/stopping, budgets and tolerances remain unchanged.

## Paired actual-unit evidence

Original snapshot: 476 Git-blob-verified source/include/vendor files at entry.
The same probe compiles six actual SubMesh, NodeAdaptive, PointAdaptive,
ElementAdaptive, TriangleAdaptive and VectorAdaptive units against original and
candidate, without an implementation adapter. MSVC ASan RelWithDebInfo and Debug
CRT use separate build directories and their existing target-specific settings.

The 36 expected outcomes comprise twenty normal ASan/CRT cases, eight CRT
nonallocating destruction cases, four positive CRT adoption-growth failure sweeps,
one ASan post-delete live-adjacency traversal and real ASan UAF/CRT leak/hook
controls. Ten normal layouts cover distinct/reversed vertices, each repeated pair
and all-repeated vertices, default emptiness, completed base cleanup after a derived
constructor throws, equivalent-coordinate replacement and merging into another
vertex. Two live parent triangles and interleaved null markers precede the new
triangle. The oracle requires exact original pointer order, physical list-node
identity and node IDs/coordinates/four curvature fields after deletion. Only an
exact matching state permits safe parent traversal and a fresh component triangle,
whose destruction must restore the same entry state. Cached initial area is
independently 0.5 or zero for repeated-node lifecycle guards; degenerate/merged
fixtures do not establish geometric validity or cache refresh.

The eight measured virtual destruction paths reject every allocation request
and require zero attempts. Setup, fresh construction, default-object allocation
and derived constructor failure setup are outside that claim. The positive hook
control independently denies one real allocation. Raw SetElement and owning
AddElement are each tested with empty/populated vectors. All four observed growth
ordinals are denied once, propagate bad_alloc without cleanup allocation, consume
the argument and restore exact prior live slots/observer list nodes. Live CRT
checkpoints require deletion of the triangle and three registration nodes: four
normal blocks released relative to the pending-argument checkpoint. Only after
restoration does the probe traverse live parents and adopt a fresh argument outside
the hook. This does not reuse the consumed object or add production CLI retry.

Original fails 31 outcomes: eighteen normal cleanup/derived/replacement cases,
eight nonallocating cleanup cases, four failed-adoption cleanup sweeps and the
actual expired-observer ASan traversal. Two default guard cases and three deliberate
controls are expected. Valid original CRT experiments retain zero final blocks;
that is not successful live-graph cleanup. Partial original states are measured
without traversal or fresh construction, except the separately isolated ASan
post-delete traversal. Candidate passes 36/36 with exact restoration, eight zero-
allocation paths, all four positive adoption denials/fresh adoptions and zero
final valid CRT retention. Its post-delete traversal consumes six live half-area
parent observations, total area 3.0, rather than vacuous empty coverage.

## Strengthened prior oracle

The earlier 31-case element-adoption probe intentionally permitted a final expired
argument observer and qualified terminal owner unwinding only. Its current failure
oracle now requires adjacency count equal to the exact existing live prefix before
rethrow. This is stricter than the previous prefix-plus-consumed-argument allowance;
no test is dropped or relaxed. Normal observation sequences, growth denials,
destruction counts and memory controls remain required. The current runner states
the updated scope. Historical stage-20 original reports retain their own probe,
source scope and raw log hashes; their two raw-ownership leaks remain negative
evidence. The new current-entry paired probe independently isolates destructor
cleanup and fresh adoption with the same probe on both versions. The entry probe
Git blob/SHA256 and audit are retained in caller_audit.json.

## Commands

```powershell
. ./build/local-env.ps1
cmake -S tests/mesh_memory -B build/s24a -G "Visual Studio 17 2022" -A x64 -DAP_MESH_MESH_ASAN=ON
cmake --build build/s24a --config RelWithDebInfo --target triangle_lifetime_probe --parallel 2
cmake -S tests/mesh_memory -B build/s24d -G "Visual Studio 17 2022" -A x64
cmake --build build/s24d --config Debug --target triangle_lifetime_probe --parallel 2
python tools/qualify_triangle_lifetime.py --asan build/s24a/RelWithDebInfo/triangle_lifetime_probe.exe --crt build/s24d/Debug/triangle_lifetime_probe.exe --runtime "C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64" --output build/triangle-lifetime-qualification
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
python tools/quality.py tidy src/data/triangle_adaptive.cpp --build build/windows-gcc17
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
```

Use fresh output directories. Original builds override AP_MESH_ADOPTION_SOURCE_ROOT
with the verified snapshot. Windows ASan leak detection is disabled; CRT normal-
block checkpoints are separate. All previous targets are rebuilt against current
sources before their probes. Explicit selected formatting, whitespace and inventory
freshness preflight full qualification. Legacy compiler warnings remain visible;
selected lint is not a repository-wide clean-warning claim. No suppressed diagnostics
or relaxed execution/numerical requirements.

## Closure audit and known remaining scope

- Code/ownership: completed triangle cleanup removes its own current-vertex
  registrations while nodes remain alive; no node/element ownership changes.
- Tests: CTest 34/34, zero skips, 74 Python controls; nineteen batteries/1137
  expected outcomes, including the strengthened 31-case adoption failure oracle.
- Contracts/inventory: C04/C05 and SubMesh API comments state live node lifetime,
  completed cleanup and bounded fresh adoption. Inventory remains 139 production
  files, 65 units, 74 headers, 22 contracts/133 anchors and the same include cycle.
- Scientific scope: twice-repeated Eistute/Book compares five/four accepted and
  rejected OBJ/incidence states against entry with identical bytes and exact
  acceptance/boundaries. Independent CSV audits compare 189 fields to raw logs,
  zero differences. Accepted steps 0/1, Eistute rejects 2/3/4, Book 2/3; last
  accepted triangle counts 1168/4256. No numerical acceptance expansion.
- Remaining: estimator hidden/duplicate mesh roots, general foreign observer
  copies, arbitrary protected mutation/subclasses and invalid external lifetimes,
  cache refresh, other constructors, logical rejection and whole-process/parallel/
  LSan/UBSan qualification. No metadata/error/history/ID rollback or full CLI retry
  is established. Deferred complete metadata snapshots are not revived.

Stage 3 remains open with bounded component qualifications. Next isolate estimator
hidden/duplicate mesh ownership before broader memory closure. Stages 0-2 remain
closed for measured scope; stages 4-11 pending. No hosted Actions/workflows are added.
Zero configured status/check contexts means absent hosted validation, not green CI.
Compact case/source inventories and log SHA256 are retained under stage3/triangle_lifetime;
full raw logs remain local.
