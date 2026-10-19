# Stage 3 slice 19: MeshAdaptive raw SubMesh adoption

Status: qualified and integrated through PR #60.
Head `bebe4f5273719304fd00967bfaf7ae74de63f351`; implementation main `e04a76a6103af5af5b116447c63c4de1ee047a0c`.
Complete tree `ffdfa4677b419b8ef4fef30ad3312257f142dcd5` (1740 blobs); 549 protected inputs.
Entry main: `26d13456b60699786f5697c91b38f6734252fd61`.

## Cause, contract and bounded repair

The two raw insertion methods promise ownership transfer, but the original
append constructs its unique_ptr only inside vector emplacement, after possible
allocation. Positional insertion resizes before wrapping its argument and returns
without adopting it for a negative position. An allocation exception therefore
abandons the pending object; a negative index abandons it on ordinary return.

Both methods now create a local unique_ptr immediately on entry. Growth failure
destroys the relinquished argument and preserves every existing slot. A negative
position leaves the container unchanged and destroys the consumed argument.
Successful insertion moves the owner, preserving object address, ordering,
replacement and sparse/null slots. No shared ownership or metadata snapshots.
Successful replacement/removal still invalidates foreign observers; callers must
rebind them. A failed argument is destroyed and cannot be reused.

The production call-site audit finds six positional generator calls and four
append calls in charge estimation. Generator indices are nonnegative; the
qualified serial initialization uses a presized valid slot. This does not qualify
all callers for exceptional execution or establish that all raw arguments are
uniquely owned. In particular, InitialMeshEstimate allocates an unreachable raw
MeshAdaptive, adopts sub and returns sub without transferring the hidden owner.
CalculateAreaTriangleMedio adopts that result again; CalculateNumbersTriangle
returns only its count without releasing the graph. These are static source
findings, not measured leak totals. The Generator charge-estimation entry is
USE_MPI-conditional; no production calls to those two historical numeric wrappers
were found. Arbitrary API safety or dead-code elimination is not established.
The unchanged source identity and findings are retained in
stage3/mesh_adoption/caller_findings.json. Estimator root ownership requires a
separate repair/qualification; constructor failure before insertion remains
outside this boundary.

Classification: behavior-changing resource-lifetime defect repair. No formula,
floating-point order, boundary synchronization, quadtree/template/front,
tolerance, budget, adaptation, acceptance or stopping change. Deletion timing
changes intentionally on failed/invalid insertion; no performance claim.
The only production formatting operation explicitly selects the changed mesh
header/unit; no repository-wide style operation or diagnostic suppression.

## Actual-unit reproduction and qualification

The original snapshot has 476 source/header/vendor blobs verified against entry
Git objects. Both instruments compile the actual seven production units
(MeshAdaptive, SubMesh, NodeAdaptive, PointAdaptive, ElementAdaptive,
TriangleAdaptive, VectorAdaptive) and the same probe; no implementation adapter.
The candidate compiles those actual current units. MSVC ASan RelWithDebInfo and
Debug CRT use separate directories. Debug iterator metadata is consistently
disabled only for this new target, with actual heap and negative controls.

Eleven normal fixtures cover empty/full append, empty/populated sparse positional
growth, populated replacement, presized insertion, -1/INT_MIN, null append,
null sparse growth and null replacement. Actual SubMesh owns three counted
polymorphic nodes and one counted actual triangle. Checks require analytic area
0.5, original node/element adjacency identity, stable adopted addresses, all
other populated/empty slots, old graph destruction, element-before-node release,
move construction/assignment and removal. The SubMesh destructor is nonvirtual;
the test never deletes a derived SubMesh through its base pointer. A stack-only
MeshAdaptive subclass exposes capacity to force growth without assuming vendor
capacity policy.

The dedicated inventory contains 36 outcomes: 22 normal ASan/CRT cases, six
positive allocation sweeps, five nonallocating insertion paths and deliberate
ASan UAF/CRT leak/allocation-hook controls. Each growth calibration observes one
allocation. Every observed ordinal is denied once; the bad_alloc must propagate
and attempts must equal ordinal+1 through unwinding. Existing graphs and all
slots remain intact, while the argument is destroyed once. No exceptional reuse
or retry is promised. Null-growth cases measure actual vector failure without
claiming positive pending-object destruction coverage.

The pinned original fails ten contract outcomes: two negative-index cases per
instrument, four nonnull allocation-failure cases, and two negative nonallocating
cases. Each measured failing CRT case retains 13 blocks/672 bytes for one pending
physical graph. The 26 other outcomes are expected. Eighteen normal successful
observation sequences (including three null layouts per instrument) are compared
against the candidate; the negative-index cleanup intentionally changes.

The first probe build failed because its CRT-only hook used Windows TRUE/FALSE
macros without a Windows header. The hook now returns the required integer 1/0.
Incomplete raw output is preserved locally and classified as a harness failure,
not production evidence. A preliminary 33-outcome run was retained separately
before adding null-replacement and explicit post-move checks. Final reproduction
uses the complete final probe.

## Reproduction commands

```powershell
. ./build/local-env.ps1
cmake -S tests/mesh_memory -B build/s19a -G "Visual Studio 17 2022" -A x64 -DAP_MESH_MESH_ASAN=ON
cmake --build build/s19a --config RelWithDebInfo --target mesh_adoption_probe --parallel 2
cmake -S tests/mesh_memory -B build/s19d -G "Visual Studio 17 2022" -A x64
cmake --build build/s19d --config Debug --target mesh_adoption_probe --parallel 2
python tools/qualify_mesh_adoption.py --asan build/s19a/RelWithDebInfo/mesh_adoption_probe.exe --crt build/s19d/Debug/mesh_adoption_probe.exe --runtime "C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64" --output build/mesh-adoption-qualification
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
python tools/quality.py tidy src/data/mesh/mesh_adaptive.cpp --build build/windows-gcc17
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
```

Use fresh output directories. To reproduce the original, safely export and verify
the pinned Git source/include/libs snapshot and set AP_MESH_ADOPTION_SOURCE_ROOT
to it in separate original ASan/CRT builds; compile the same probe.
Windows ASan leak detection is disabled; leak measurements come from Debug CRT.

## Closure audit and remaining findings

Exact published-head and implementation-main full campaigns pass: GCC serial
C++17 Release build, CTest 29/29 (zero skips, 74 Python controls), fourteen memory
batteries/968 expected outcomes, selected mesh-unit lint, explicit formatting,
architecture freshness and whitespace. The new actual-unit battery passes
36/36, all six observed growth allocation denials and five nonallocating paths;
all valid CRT cases retain zero blocks/bytes. Eighteen original/repaired normal
successful observations match. The original ten failures remain negative evidence.

Both full campaigns repeat Eistute/Book twice, preserving all nine attempted
accepted/rejected OBJ/incidence states, 189 CSV fields and 1,168/4,256 last-accepted
triangles exactly. Inventory: 139 production files, 65 units, 74 headers, 22
contracts/124 anchors; the existing six-header cycle is unchanged.

Candidate/head/main compact reports retain every command, outcome identity and
raw log SHA256. Documentation closure preserves all 549 compiled/tool/test/build/
input/contract identities and retains full instrument/numerical evidence against
those inputs; no fresh full numerical/memory campaign is claimed for documentation
commits. Exact documentation head/main build, CTest and complete Git/working-byte
checks are required. Zero configured remote checks means absence of hosted gates,
not a green hosted test campaign.

| Audit scope | Result |
| --- | --- |
| Code | Entry owners precede both growth and negative return; argument consumed on every valid path |
| Tests | Actual graph identity/area/adjacency/destruction, all observed growth ordinals, nonallocating paths and real negative controls; full exact-head/main gates pass |
| Contracts | C04 and ADR-0020 specify consumption, exclusive actual SubMesh arguments and foreign observer limits |
| Documentation | Original defects, harness compile failure, final source identities/commands and coverage limits retained |
| Scientific scope | No formula/order/selection change; exact full accepted/rejected article traces pass |
| Known failures/coverage | Ten original failures retained; candidate required gates pass; whole stage 3 remains open with limits below |

Stage 3 remains open. The estimator hidden root/duplicate adoption finding remains
open and dynamically unqualified. Next isolate SubMesh::SetElement raw element adoption:
its emplacement can allocate before constructing the owner. AddElement already
accepts an owning unique_ptr and is a distinct, safe entry point; SetNoh copies a
borrowed source and must not be reinterpreted as adoption. Other constructors,
OpenMP initialization, logical rejection audit, whole-process/parallel/LSan/UBSan
and remaining node/topology observer operations are unqualified. Duplicate
adoption, polymorphic SubMesh deletion, extreme allocation sizes and arbitrary
custom subclasses/allocators are outside the valid contract.
