# Stage 3 slice 17: serial curve-sample lifetime

Status: qualified and integrated through PR #56.
Head `06f4bfd40cff9f09c527777169c5fcf8d053e0c7`; implementation main `9703536b21d8d3f02dbe7fbd9f83d3260f461aad`.
Complete tree `7efe095ab635e3e8e1b42cab30403adddc4d295a` (1710 blobs) and 542 protected inputs match.
Entry main: `4a504556f08b6abbe078236c1b6eb2136ef9c537` (472 pinned source/header/
vendor blobs). Earlier integrated qualification remains the baseline.

## Root cause and required failure behavior

The current CLI catches exceptions outside Generator execution and terminates.
There is no local exceptional retry that consumes partially updated Generator
metadata. Numerical candidate rejection/retry follows explicit policy branches.
This repair therefore requires safe release on termination, not recovery of
metadata or a new retry policy.

Curve point lists are observers. Generator collectively releases their distinct
sample objects only in its final block, after report writing. An exception before
that block skips release; Geometry and CurveAdaptive destruction do not own these
samples. The cleanup itself constructs an unordered_set and can fail allocation
before releasing objects. Restoring a point graph does not supply its final owner.

The pinned original uses the verbatim final cleanup block in an interface adapter
with no automatic destructor cleanup, matching the absence of a production scope
owner. This is a controlled call boundary, not the full Generator translation
unit or a full CLI failure injection. Original report: 36/53 contract failures;
terminal abort, inner failure and heap denial leave five/nine initial objects
undestroyed. Debug CRT measures ten/eighteen retained blocks in each corresponding
case. All twelve normal observed logs match the repaired logs byte for byte.

## Repair and classification

CurveSampleLifetime owns the collective lifetime of currently published serial
samples while borrowing Geometry, which outlives it. It is installed before
serial initialization/adaptation, and explicitly releases at the existing final
cleanup location. Its destructor also releases on unwinding after inner graph
guards restore their state. Release clears every shared alias before deleting
each sample once, then clears the lists. It performs no allocations; repeated
release on empty lists is harmless. Geometry controls and independent physical
mesh copies retain their existing owners. Parallel cleanup remains unchanged.

Classification: behavior-changing resource-lifetime defect repair. No metadata
copies/recovery, exception swallowing, hidden retry or scientific policy change.
All numerical formulas, floating-point order, parameter selection, synchronization,
templates/front, tolerances, budgets and acceptance/stopping rules are unchanged.
Teardown changes deletion order, allocation counts and resource timing. Alias
scanning can take quadratic time in the number of samples; no efficiency claim.

## Executed bounded instruments

The new probe compiles twenty-one actual candidate production units plus the
probe; original uses twenty pinned units plus the verbatim cleanup adapter.
Existing graph/publication/sample/rebuild operations are actual production code.
Three initialized curve types use shared non-manifold or distinct endpoints.
Independent physical mesh copies and their triangle observers survive release.

The 53 required outcomes comprise twelve normal ASan/CRT traces, twelve terminal
abort outcomes, twelve failures after one/two committed curve prefixes and inner
graph unwinding, six CRT releases under denied-allocation hooks, six actual CRT
heap failures before teardown, two explicit empty/repeat guards and three
deliberate ASan UAF/CRT leak/allocation-hook controls. Candidate: 53/53 expected;
valid CRT cases retain zero blocks/bytes. Positive heap failures propagate once;
attempts remain one during unwinding. Explicit release makes zero allocation
attempts on positive populated fixtures. Zero-allocation teardown is not a
positive allocation-denial sweep; the independent hook control remains required.

Configure `tests/curve_memory` in separate ASan/Debug directories with
AP_MESH_CURVE_ASAN on/off. Original also sets AP_MESH_CURVE_SOURCE_ROOT to the
pinned archive and AP_MESH_SAMPLE_LIFETIME_HEADER to the retained adapter. Build
curve_sample_lifetime_probe in RelWithDebInfo/Debug, then run:

```powershell
python tools/qualify_curve_sample_lifetime.py --asan build/s17a/RelWithDebInfo/curve_sample_lifetime_probe.exe --crt build/s17d/Debug/curve_sample_lifetime_probe.exe --runtime 'C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64' --output build/s17-candidate-lifetime
```

Use a new output directory per run. Raw original/candidate reports and logs are
under build/s17-original-lifetime and build/s17-candidate-lifetime. An initial
probe compile error (const observer accessor) is retained separately and is not
counted as successful evidence. Only the new target disables optional NRVO and
Debug iterator metadata consistently; actual heap instrumentation remains.

## Closure audit and known findings

Exact-head and implementation-main campaigns pass the full GCC serial build, CTest 27/27 with
zero skips and 74 Python controls, all eleven prior memory batteries (852
outcomes) and the new 53-outcome battery. Read-only new-unit lint, explicit
formatting, whitespace and architecture freshness pass: 137 production files,
64 translation units, 73 headers, 22 contracts/119 anchors, with the existing
six-header cycle unchanged. Twice-repeated Eistute/Book comparisons preserve all
nine attempted accepted/rejected OBJ/incidence states, 189 CSV fields and
1,168/4,256 last-accepted triangles exactly.

Full reports and raw command/case logs were hash-checked again before delivery.
Compact candidate/head/main reports, complete case inventories/outcomes and raw
SHA256 identities are retained in stage3/curve_sample_lifetime. The documentation
closure preserves all 542 compiled/tool/test/build/input/contract identities;
full instrument/numerical results remain tied to the unchanged implementation
inputs, without claiming a fresh full campaign for documentation-only commits.

| Audit scope | Result |
| --- | --- |
| Code and ownership | One serial published-sample owner; alias removal precedes deletion; allocation-free terminal release; inner graph guards unwind first |
| Tests and instruments | Exact head/main CTest 27/27, zero skips, 74 Python controls, twelve batteries/905 expected outcomes, deliberate UAF/leak/hook controls |
| Contracts | C07 and ADR-0018 specify geometry lifetime, collective exclusive sample ownership and independent physical mesh copies |
| Documentation | Plan/state/worklog/quality, source inventory and raw-hash evidence describe the measured boundary and remaining failures |
| Scientific scope | All nine accepted/rejected OBJ/incidence states, 189 CSV fields and last-accepted triangle counts remain exact; no formula/policy/tolerance/budget change |
| Known failure/coverage inventory | InitialMesh temporary/pending ownership finding recorded below; unpublished allocations, whole-process/parallel/LSan/UBSan and logical rejection remain open |

Stage 3 remains open; only this measured slice is qualified.

Unpublished allocations, arbitrary constructor failures, other owners/custom
destructors, whole-process/parallel/LSan/UBSan and full CLI exceptional execution
remain unqualified. Source inspection also identifies a separate InitialMesh
central-node temporary copied into SubMesh without visible local ownership or
release; dynamic isolation and repair are the next constructor work item, not a
claim of coverage by this owner. Metadata/history/error/acceptance recovery and
evaluator scratch restoration are not supplied or required by this fatal CLI
exception boundary. Logical candidate rejection remains a separate audit scope.
