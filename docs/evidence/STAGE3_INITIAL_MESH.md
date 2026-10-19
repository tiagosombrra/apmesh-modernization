# Stage 3 slice 18: serial InitialMesh ownership

Status: qualified and integrated through PR #58.
Head `84e303da51a6ac4c6cf52dbbee7f5fb30c93696e`; implementation main `e398854bba9f06045b71dd1b965505872106d746`.
Complete tree `490a5c448c277dffb5229e2d2b51ff86574768d5` (1727 blobs), 546 protected inputs.
Entry main `d4fa37d8a77281027335bc70470f2dc1b0331d52`; 474 original source/header/
vendor blobs are Git-pinned. Historical source is unchanged.

## Reproduced cause and repair

SubMesh::SetNoh copies a supplied node and owns that independent copy. The
original InitialMesh allocates a central NodeAdaptive, supplies it to SetNoh
and never releases the source temporary. Eight ordinary successful CRT cases
each retain two blocks. An allocation failure after the raw SubMesh allocation
also leaks that pending mesh before it has any external owner.

The helper requires a valid patch with four curves and manager channels 0/1.
BuildInitialSubMesh is the actual serial construction body extracted into an
independently instrumentable production unit. It returns unique_ptr<SubMesh>.
The existing public raw-result method delegates and releases to its caller.
Pending mesh and triangles retain exclusive local owners until nonallocating
move transfer. The central source node is local and dies after its physical copy
is created. A corner source stays locally owned until its first successful
curve insertion, then belongs to the existing collective CurveSampleLifetime
scope. If a later insertion fails, that owner reclaims the published prefix.
Unpublished corner temporaries remain local. Triangle-constructor failure can
leave adjacency observers in pending nodes; pending-mesh destruction clears
those lists without dereferencing expired elements.

The existing five-node/four-triangle construction, u/v loop order, node and
element ID channels, triangle vertex/UV order, curve eligibility/reversal and
final patch/mesh observer publication are preserved. The patch's prior SubMesh
observer is unchanged on construction failure. Published curve prefixes, patch
evaluator scratch and consumed IDs are not rolled back; the CLI still terminates
on exceptional failure. No metadata recovery or new retry policy is introduced.

Classification: resource-lifetime defect repair with success-preserving
engineering extraction. No numerical formula, parameter-evaluation order, tolerance,
budget, synchronization, quadtree/template/front or acceptance/stopping change.
Allocation timing/deletion order and peak storage change; no efficiency claim.

## Bounded executed evidence

The probe compiles twenty actual candidate production units plus the probe.
Original: nineteen pinned units, the verbatim original method in a minimal
class/result interface adapter, and the same probe. This is not full Generator
translation-unit instrumentation. The actual wrapper/caller remains subject to
full serial application regression.

Two analytic Bezier surfaces (plane and bilinear height) and four curve layouts
cover all-new, alternating preinitialized curves in both directions, and all
preinitialized curves. Actual curve direction flags exercise reversal of newly
initialized lists while existing lists keep their source IDs/order. Physical
nodes are distinct objects from samples. Independent analytic coordinates,
ordered node/element IDs, triangle vertex/UV order, positive areas and physical
mesh survival after sample release are required.

Candidate: 27/27 expected outcomes, comprising sixteen ASan/CRT normal traces,
eight positive full CRT allocation sweeps and three deliberate UAF/leak/hook
controls. Sweeps deny all 400 observed allocations (54/50/46/50 per shape).
Every denial propagates once; attempts equal ordinal+1 through helper and
sample-owner unwinding, with zero retained blocks per fixture. The final denial
follows five node-channel and four element-channel requests. No ID rollback or
exceptional continuation is claimed.

Original: eight CRT normal cases fail with two retained central-temporary blocks
each. All eight allocation sweeps measure the first two ordinals: ordinal zero
is clean; ordinal one retains one pending-mesh block and stops the sweep. The
process retains three blocks including two from its separate normal calibration.
Later original ordinals are unmeasured. Other eleven outcomes are expected.
All sixteen complete numerical observation sequences match the candidate.
Raw CRT diagnostics and exit status intentionally differ; no raw-log equivalence
or Windows ASan leak coverage is claimed.

An earlier invalid probe fixture used one manager channel and transposed its
control-net coordinates. Production configures two channels. Its raw ASan
overflow/oracle failures and binary identities are archived separately as harness
errors, not production defects or qualification evidence. The corrected probe
uses actual separate node/element channels and independent surface coordinates.
The earlier six-fixture instrument reports are also preserved separately from
the final eight-fixture qualification.

Configure tests/curve_memory in separate ASan/Debug directories using
AP_MESH_CURVE_SOURCE_ROOT and AP_MESH_CURVE_ASAN. For the original, additionally
set AP_MESH_INITIAL_MESH_IMPLEMENTATION to the retained verbatim adapter. Build
initial_mesh_probe in RelWithDebInfo/Debug and execute:

```powershell
python tools/qualify_initial_mesh.py --asan build/s18a/RelWithDebInfo/initial_mesh_probe.exe --crt build/s18d/Debug/initial_mesh_probe.exe --runtime 'C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64' --output build/s18-candidate-initial
```

Use a new output directory for each run. Raw reports/logs remain in
build/s18-original-initial and build/s18-candidate-initial, with failed fixtures
in build/s18-preliminary-invalid-fixture. New-target NRVO and Debug iterator
settings match the previous bounded instruments; actual heap controls remain.

The first complete campaign was blocked by the actual analyzer's inherited
floating-point loop-counter diagnostic. Its failed report and raw lint log are
preserved. The constructor now enumerates {0.0, 1.0} directly, with v outermost
and u innermost: the same four exactly representable (v,u) inputs in the same
order. Only counter arithmetic disappears; numerical parameter evaluation,
formulas and acceptance rules are unchanged. No analyzer filter or warning
suppression was added. Full instrument/numerical regression is rerun after this
source change.

## Closure audit and remaining findings

Exact-head and implementation-main campaigns pass full GCC build, CTest 28/28,
zero skips, 74 Python controls, twelve prior memory batteries (905 expected
outcomes) and the new 27-outcome/400-denial constructor battery. New-unit lint,
explicit formatting, inventory and whitespace pass: 139 production files, 65
units, 74 headers, 22 contracts/121 anchors; the existing six-header cycle stays.
Twice-repeated Eistute/Book comparisons preserve all nine accepted/rejected OBJ/
incidence states, 189 CSV fields and 1,168/4,256 last-accepted triangles exactly.
Every full command/case raw log hash was rechecked before delivery.

Compact candidate/head/main reports, all case identities/outcomes and raw SHA256
are retained in stage3/initial_mesh. Documentation closure keeps all 546 compiled/
tool/test/build/input/contract identities unchanged, retaining full instrument/
numerical evidence against those inputs without claiming a fresh full campaign
for documentation-only commits.

| Audit scope | Result |
| --- | --- |
| Code and ownership | Exclusive pending mesh/element/temporary owners; first successful sample publication transfers to collective owner; completed patch observer only |
| Tests/instruments | Exact head/main CTest 28/28, 74 Python controls, thirteen batteries/932 expected outcomes; all 400 constructor allocation denials and deliberate controls |
| Contracts | C07/ADR-0019 specify valid patch/four curves, two ID channels, collective sample ownership, pending-node adjacency teardown and presized raw handoff |
| Documentation | Plan/state/worklog/quality, source inventory, negative evidence and exact-head/main records agree on measured scope |
| Scientific scope | Same four exact corner inputs/order, formulas, vertex/UV/ID order and acceptance/stopping rules; sixteen numeric traces and full model regression exact |
| Failure/coverage inventory | General raw mesh adoption, OpenMP initialization, other constructors, logical rejection and whole-process/parallel/LSan/UBSan remain open |

Only this measured slice is qualified; stage 3 remains open.

Fixture construction, arbitrary/custom patches, other constructors, general
MeshAdaptive raw adoption, parallel/OpenMP initialization and whole-process/
LSan/UBSan remain unqualified. The actual serial initial-mesh caller uses valid
indices in a presized MeshAdaptive, so its raw-result handoff does not allocate.
General InsertSubMeshAdaptive/ByPosition can grow storage before adopting a raw
argument (and ignores a negative position); isolate that ownership boundary next.
Logical candidate-rejection audit remains separate from terminal cleanup.
