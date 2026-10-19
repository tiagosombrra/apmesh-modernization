# Stage 3 slice 23: stable triangle identity and observer replacement

Candidate qualified; exact published-head and post-merge main qualification remain pending.

Entry main: `83e6f5a591274602e1702b3d47d9e9736b511124`.
Classification: behavior-changing observer-consistency defect repair and
engineering API tightening. No scientific proposal.

## Root causes and chosen contract

Node adjacency stores non-owning triangle addresses. The implicit triangle copy
constructor/assignment copied vertex pointers and caches without publishing the
new address in those node lists. Move expressions were accepted through copying:
the existing user-declared destructor suppresses implicit move special members.
An actual original-unit experiment constructs, copies, move-expresses and assigns
triangles with area 0.5, while only the original address appears in adjacency.
This is a missing identity relation, even though final node cleanup retains no
heap blocks. No expired observer is dereferenced in that experiment.

TriangleAdaptive now explicitly deletes copy/move construction and assignment.
An owned triangle keeps its identity/address; moving unique_ptr owners, SubMesh
and MeshAdaptive does not move triangle objects. Current production searches find
no direct triangle value-copy/move consumers and no ReplaceNode consumers beyond
declaration/definition. This is a static lexical audit, not proof about aliases,
external clients or every conditional build. API tightening may require changes
in unobserved callers. Implementing allocating copy/move adjacency publication
would add a second ownership/identity contract without a measured consumer need.

The old ReplaceNode changed the first n1/n2/n3 matching raw pointer without
removing its old observer or publishing one at the destination. The repair finds
the same first matching slot, transfers exactly one existing physical list node
from the old node to the destination tail using std::list::splice, then commits
the vertex pointer. MoveElementObserverTo returns false without mutation when
no registration exists. Standard allocator lists permit this nonallocating
transfer. The list node's address, all other entries/order/null markers and
repeated-vertex multiplicities survive. Moving all matching values would be
incorrect when other vertices still refer to the old node.

Same-node and absent-node replacements remain no-ops. A matched null destination
throws invalid_argument, and a matched empty/default vertex or missing registration
throws logic_error before mutation. Those diagnostic paths may allocate exception
storage and are outside the zero-allocation claim. Both nodes must be live with
valid lists, the matched registration must exist and destructors must not throw.
The method cannot make an expired raw node pointer safe.

Triangle ID, all three UV tuples, cached normal/area/angles and node scalar state
are unchanged. No formula, floating-point order, tolerance, budget, boundary
synchronization, quadtree/template/front, adaptation/acceptance/stopping or CLI
retry policy changes. This is an observer/topology operation; cached geometry is
not asserted valid after a coordinate-changing replacement. Cache refresh remains
a separate audited issue. Ordinary triangle destruction is still empty and does
not unregister. Arbitrary protected vertex mutation/subclasses can violate this
contract; the change does not qualify those paths or failed-adoption graph reuse.

## Actual-unit evidence

Original: 476 Git-blob-verified source/include/vendor files at entry main. The
same probe compiles five actual NodeAdaptive, PointAdaptive, ElementAdaptive,
TriangleAdaptive and VectorAdaptive units from original/candidate sources, without
an implementation adapter. Separate MSVC ASan RelWithDebInfo and Debug CRT builds
keep their existing target-specific iterator settings.

The 35 expected outcomes comprise twenty normal ASan/CRT replacement cases,
eight CRT zero-allocation paths, identity and default-state guards under both
instruments, and real ASan UAF/CRT leak/allocation-hook controls. Replacement
variants cover each vertex, a repeated pair, all-repeated vertices, merging into
an existing vertex, same/absent no-ops, missing registration and null destination.
Fixtures include two live parent triangles and interleaved null markers. The
oracle checks complete observer pointer order and physical list-node addresses,
first-match vertex pointers, node IDs/four curvature fields, triangle ID/all UVs
and every cached field. Initial area is independently 0.5 or zero for repeated
vertex guards. Cache preservation compares double object bytes, including existing
NaN payloads in degenerate guards; this is not a geometric validity claim.

Successful transfer cases perform a second first-match replacement to test the
live modified topology. After merging equal vertices, registration list nodes
are not uniquely associated with vertex slots; the oracle follows the documented
first-matching observer transfer rather than claiming an inverse list-node mapping.
The eight CRT valid/no-op operations reject all allocation requests and require
zero attempts, including both replacements and their observer/cache checks.
Fixture setup/final owner teardown and invalid-argument exception paths are not
inside these scopes. The hook control independently denies one actual allocation;
zero-attempt cases are not described as positive allocation-denial sweeps.

Original fails 26 outcomes: sixteen normal topology/guard cases, six valid
nonallocating topology cases and four identity/default guard cases. The remaining
nine outcomes are expected; four complete normal no-op observation sequences
match candidate. Every valid original CRT case retains zero final blocks despite
the inconsistent live relation. Candidate passes 35/35 with zero final valid CRT
retention. Original sources/reports and full raw log hashes are preserved.

## Reproduction commands

```powershell
. ./build/local-env.ps1
cmake -S tests/mesh_memory -B build/s23a -G "Visual Studio 17 2022" -A x64 -DAP_MESH_MESH_ASAN=ON
cmake --build build/s23a --config RelWithDebInfo --target triangle_observer_probe --parallel 2
cmake -S tests/mesh_memory -B build/s23d -G "Visual Studio 17 2022" -A x64
cmake --build build/s23d --config Debug --target triangle_observer_probe --parallel 2
python tools/qualify_triangle_observer.py --asan build/s23a/RelWithDebInfo/triangle_observer_probe.exe --crt build/s23d/Debug/triangle_observer_probe.exe --runtime "C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64" --output build/triangle-observer-qualification
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
python tools/quality.py tidy src/data/node_adaptive.cpp src/data/triangle_adaptive.cpp --build build/windows-gcc17
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
```

Use fresh output directories. Original builds override AP_MESH_ADOPTION_SOURCE_ROOT
with the verified snapshot. Windows ASan leak detection is disabled; Debug CRT
measures normal-block retention. All prior targets, including the earlier node
boundary, are rebuilt from current sources. Explicit selected formatting,
whitespace and inventory freshness are checked before full qualification. Legacy
compiler warnings remain visible; selected production lint is not a repository-
wide clean-warning claim. No diagnostic suppressions or relaxed gates.

## Closure audit and remaining inventory

- Code: explicit stable address identity and first-vertex/list-node transfer;
  constructor failure cleanup and qualified SubMesh ownership ordering retained.
- Tests: CTest 33/33, zero skips, 74 Python controls; eighteen memory batteries/
  1101 expected outcomes. Actual deliberate memory/hook controls remain required.
- Contracts/inventory: C05 states the identity, replacement preconditions, no-op/
  rejection behavior and unchanged cache limit. Inventory is 139 production files,
  65 units, 74 headers, 22 contracts/132 anchors; existing include cycle unchanged.
- Scientific scope: twice-repeated Eistute/Book preserves every accepted/rejected
  OBJ byte and exact incidence/acceptance comparison against entry. Five plus
  four mesh states are compared. Independent CSV audits compare 189 fields against
  raw logs, zero differences. Accepted steps 0/1; Eistute rejects 2/3/4, Book 2/3;
  last accepted triangle counts 1168/4256. No numerical acceptance expansion.
- Coverage limits: no ordinary triangle deregistration or exceptional adoption
  graph reuse, coordinate/cache refresh, arbitrary subclass/protected-field safety,
  general node-copy repair, conditional/external-client compatibility, full-process/
  parallel/LSan/UBSan qualification. Estimator hidden/duplicate roots, other
  constructors and logical rejection remain open. Deferred complete metadata
  snapshots are not revived.

Stage 3 remains open. Next qualify completed-triangle destruction and failed-
adoption observer cleanup under the stable identity/replacement contract, retaining
negative evidence and the existing SubMesh owner ordering. Stages 0-2 stay closed
for measured scope; stages 4-11 pending. No hosted Actions/workflows are added.
Zero configured status/check contexts means absent hosted validation, not green CI.
Compact reports under stage3/triangle_observer preserve full case inventories,
source identities and log SHA256; full raw logs remain local.
