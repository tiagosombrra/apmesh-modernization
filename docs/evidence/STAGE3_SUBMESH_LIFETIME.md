# Stage 3 slice 22: preserve SubMesh element-before-node lifetime

Candidate qualified; exact published-head and post-merge main gates remain pending.

Entry main: `3ad6cb28cd183fe1adc7604de6e92dd28fd0e50a`.
Classification: behavior-changing engineering lifetime defect repair.

## Root cause and repair

SubMesh declares node owners before element owners. Normal destruction reverses
this order and releases elements before nodes. Defaulted move assignment instead
assigns members in declaration order, destroying destination nodes before its
elements. An element destructor is consequently unable to consume its borrowed
nodes during populated replacement. Current TriangleAdaptive destruction is empty;
the observed ASan failure uses a counted actual triangle subclass that reads its
three node observers. This demonstrates the owner-order defect, not a claim that
the current empty production triangle destructor performs that read.

Explicit move assignment first clears old elements while both graphs' nodes are
alive, then moves node and element vectors and copies the incoming patch observer
value. A self-address guard preserves populated self-move. No element/node object
is relocated, no new shared ownership is introduced and no allocation is needed.
Ordinary destruction and move construction retain their existing correct order.
The source's patch observer value is preserved, as before; external Patch observers
of either SubMesh address are not rebound automatically.

Elements must borrow nodes owned by their own graph or independently live external
nodes, and destructors must not throw. Incoming elements borrowing nodes owned by
the replaced destination do not satisfy this lifetime contract. No automatic
triangle deregistration, full-graph recovery, duplicate adoption or CLI retry.
Formulas, floating-point evaluation order, boundary synchronization, quadtree/
templates, advancing-front reconstruction, adaptation, budgets, tolerances,
acceptance and stopping policies are unchanged. Explicit formatting is limited
to the SubMesh header/unit and the new probe.

## Reproduction and measured scope

Original snapshot: 476 Git-blob-verified source/include/vendor files at entry.
Original and candidate use the same probe and six actual production units:
SubMesh, NodeAdaptive, PointAdaptive, ElementAdaptive, TriangleAdaptive and
VectorAdaptive. Separate MSVC ASan RelWithDebInfo and Debug CRT builds are used.

Eight layouts exercise ordinary populated destruction, move construction,
assignment to empty and populated destinations, populated self-move, empty and
node-only incoming graphs, and repeated vertices/interleaved null slots. Tests
check address/order identity, node IDs/coordinates/four curvature fields, element
IDs/UV/analytic area, observer sequence/multiplicity, returned assignment address,
moved-from vector emptiness and unchanged opaque patch observer values. Patch
tokens are comparison-only; no Patch object is fabricated or dereferenced.
Repeated vertices are lifecycle guards, not geometric-validity evidence.

The 28 expected outcomes comprise sixteen normal ASan/CRT cases, eight CRT
operations that reject every allocation request, one ASan borrowed-node-read
experiment and actual UAF/leak/allocation-hook controls. No-allocation scopes
include operation validation and final graph teardown; all eight require zero
attempts. The hook control separately observes and denies one real allocation.
These are nonallocating paths, not eight positive allocation-denial sweeps.

Original: twelve ordering failures (four populated-destination variants in normal
ASan/CRT and nonallocating CRT modes), plus an ASan heap-use-after-free when the
derived triangle destructor reads its already-deleted nodes. The other fifteen
outcomes are expected. Valid original CRT cases retain zero final blocks, which
does not establish correct destruction order. Candidate passes all 28 outcomes,
including safe borrowed-node reads and zero retained CRT blocks. Eight previously
passing complete normal observation sequences remain identical. Self-move already
passes on the measured MSVC library; the explicit guard establishes the contract
without claiming an original measured self-move failure.

## Commands and preparation finding

```powershell
. ./build/local-env.ps1
cmake -S tests/mesh_memory -B build/s22a -G "Visual Studio 17 2022" -A x64 -DAP_MESH_MESH_ASAN=ON
cmake --build build/s22a --config RelWithDebInfo --target submesh_lifetime_probe --parallel 2
cmake -S tests/mesh_memory -B build/s22d -G "Visual Studio 17 2022" -A x64
cmake --build build/s22d --config Debug --target submesh_lifetime_probe --parallel 2
python tools/qualify_submesh_lifetime.py --asan build/s22a/RelWithDebInfo/submesh_lifetime_probe.exe --crt build/s22d/Debug/submesh_lifetime_probe.exe --runtime "C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64" --output build/submesh-lifetime-qualification
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
python tools/quality.py tidy src/data/mesh/sub_mesh.cpp --build build/windows-gcc17
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
```

Use fresh output directories. Original builds set AP_MESH_ADOPTION_SOURCE_ROOT
to the safely exported Git-verified entry snapshot. ASan leak detection is disabled
on Windows; Debug CRT measures final normal-block retention separately. All prior
targets are rebuilt from current sources before their retained contract probes.

The first observation recognizer anchored at end-of-line without accepting CRLF,
incorrectly rejecting successful Windows observations. Both original/candidate
reports, exit codes and raw log identities are preserved in recognizer_failure.json
and local archived directories. The recognizer now accepts optional CR before LF;
identity/order/retention predicates and production sources were not relaxed.
Fresh complete runs use the corrected recognizer. The first full candidate
campaign passed all 1066 expected instrument outcomes but stopped at the required
whitespace gate on an extra final blank line in the added CMake target. It did
not execute numerical generation and is not a qualified delivery. The report,
diagnostic and hashes are retained in whitespace_failure.json and the local
archive. Explicit documented whitespace normalization removes that line; the
next run correctly stopped at inventory freshness because the CMake SHA256 had
changed while the retained generated inventory had not been refreshed. That
failed pre-CTest run and diagnostic are retained in inventory_failure.json.
Regenerating the derived inventory and preflighting all three textual gates
precedes the fresh full campaign, with unchanged requirements. Existing MSVC sscanf deprecation
and legacy signedness/build warnings are not suppressed or counted as clean lint.
Required selected production-unit lint passes independently.

## Closure audit and remaining inventory

- Code/ownership: old elements are retired before old node owners; self-move,
  null slots, identity and nonallocating teardown have bounded dynamic evidence.
- Tests: CTest 32/32, zero skips, 74 Python controls; seventeen memory batteries/
  1066 expected outcomes. Deliberate negative controls remain mandatory.
- Contracts/inventory: C04 describes ordering/preconditions and no Patch rebinding;
  C05 keeps ordinary triangle observer removal separate. Inventory remains 139
  production files, 65 units, 74 headers, 22 contracts/129 anchors and the same
  pre-existing include cycle.
- Numerical/scientific scope: twice-repeated Eistute/Book compares every accepted
  and rejected OBJ/incidence state and 189 CSV fields against qualified entry.
  Accepted steps 0/1; Eistute rejects 2/3/4, Book 2/3; final triangle counts
  1168/4256. No scientific proposal or expanded acceptance claim.
- Caller audit: static current first-party searches find pointer construction/
  adoption and no production direct SubMesh/Triangle value moves or copies.
  ReplaceNode occurs only in declaration/definition; it does not maintain
  adjacency. Static search is not an external-API or alias proof. See caller_audit.json.
- Remaining: ordinary completed-triangle destruction leaves expired adjacency;
  implicit triangle copy/move and protected vertex mutation/ReplaceNode need an
  explicit registration contract before safe automatic removal. Slice 20 still
  qualifies terminal adoption failure only. Estimator hidden/duplicate roots,
  other constructors, logical rejection and full-process/parallel/LSan/UBSan remain
  open. Do not revive deferred complete metadata snapshots.

Stage 3 remains open. Next establish triangle special-member/replacement observer
semantics, then qualify completed-triangle destruction against that contract.
Stages 0-2 remain closed for measured scope; stages 4-11 pending. No hosted Actions
or workflows were added. Zero configured status/check contexts means absent hosted
validation, not green CI. Evidence in stage3/submesh_lifetime retains compact full
case inventories and log SHA256; full raw logs remain local.
