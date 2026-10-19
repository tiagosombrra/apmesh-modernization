# Stage 3 slice 25: estimator construction ownership

Candidate qualified; full exact published-head and post-merge main gates remain required.

Entry main: `c6b6a21aaf5bcc298256cd28c1b477cb4291841d`.
Classification: behavior-changing resource-lifetime and invalid-input defect repair.
No scientific proposal; stage 3 remains open.

## Root cause and repair

InitialMeshEstimate created an unreachable MeshAdaptive that adopted the same
SubMesh it returned. The historical area wrapper adopted that result again; both
roots leaked. Static duplicate ownership does not prove an executed double delete.
Grid source nodes were copied by SetNoh; unpublished source nodes and every center
temporary leaked. Raw pending SubMesh/triangles also leaked on construction failure.

BuildInitialEstimateSubMesh now returns one unique physical mesh owner, without
a hidden Mesh. The raw compatibility method explicitly releases it to its caller.
Pending nodes retain local owners until first successful curve insertion; shared
corner aliases remain observers under the existing collective sample lifetime.
Physical nodes remain independent copies. Pending triangles stay owned through
FindUV/UV setup and enter AddElement by move. Only completed construction publishes
the patch observer. The caller must retire or rebind it before mesh destruction.
Failure is terminal: published sample prefixes stay with the caller's collective
lifetime; evaluator scratch, curve metadata and IDs are not rolled back.

All parameter additions, floating endpoint predicates, UV calls, element order,
formulas and ID assignment positions are preserved. In particular center IDs are
still assigned to the temporary after its copy: copied centers keep default
unsigned-long -1 IDs. No silent ID repair, reversal change, alternative generator,
CLI retry or scientific adaptation/acceptance/stopping change is introduced.

## Floating induction: actual correction and numerical evidence

The first required lint run failed with four FloatLoopCounter errors in the four
inherited loops; its full failing campaign is retained. No diagnostic is disabled
and no loop is merely disguised. Each loop now has an integer counter and a finite
ceiling of 2*(degree+1), while retaining the original floating predicate and exact
repeated-addition expression. Nonpositive degrees throw invalid_argument before
touching the patch. The scalar guard/ceiling uses explicit integer arithmetic;
static assertions require at most 31 value bits in int and at least 53 in double.

For a positive 32-bit degree, h=1/degree is greater than 2^-31. At parameters at
most 1, floating addition roundoff is far smaller than h/2. Each actual increment
therefore advances by more than h/2; after 2*(degree+1) increments the value is
past the original endpoint. The integer ceiling cannot truncate the valid legacy
sequence. The original floating predicate still determines endpoint inclusion.
This is a bounded engineering termination guard, not a new scientific budget or
a recomputed coordinate formula. Invalid inputs are rejected rather than allowed
to publish a zero-triangle degree-zero result or enter negative-degree induction.

The runner extracts the actual original and candidate outer loop headers and the
candidate guard/ceiling prefix into a small scalar comparison unit. Both inner
headers must match their respective outer header under variable renaming. GCC C++17
compares complete vectors of double object bits (not digest-only equality) for
degrees 1..512 and 1023/1024/4095/4096/10000/65535/65536/1000000: 520 degrees,
1040 nonempty sequences, all identical; the ceiling is never reached. A deliberate
index/degree coordinate-recomputation alternative is rejected at degree 10.
Three nonpositive scalar guards pass. Compilation/source/executable/log hashes and
per-degree counts/digests are retained with each memory qualification report.

The scalar test observes 228 center counts different from the nominal degree;
for example degree 9 and degree 1000000 preserve their historical endpoint omission.
Those counts are preserved negative/limited evidence, not approval of complete
non-power-of-two mesh construction. Changing endpoint inclusion or replacing
repeated addition with division/multiplication needs separate numerical analysis.
No performance, improved inverse accuracy or general extreme-mesh claim is made.

## Paired actual-construction evidence

The original snapshot contains 476 Git-blob-verified source/header/vendor files.
Its InitialMeshEstimate body is extracted into a minimal namespace/result adapter;
only its raw return is wrapped in unique_ptr so both experiments have the same
external caller owner. Hidden Mesh and leaked original temporaries are not
reclaimed by the adapter. Original source/function/adapter hashes are retained.
Actual Bezier/curve/physical mesh/node/triangle/sample-lifetime units are compiled
with it. Candidate instruments the actual production helper. Full historical
ChargeEstimateProcess/Generator translation units and wrapper orchestration are
not instrumented; the thin compatibility forwarding method is source-audited.

The 77 expected outcomes comprise 48 normal ASan/Debug CRT cases (plane/bilinear,
four fresh/alternating/initialized curve masks and degree 1/2/4), 24 complete CRT
allocation sweeps, two invalid-degree guard cases and real ASan UAF/CRT leak/hook
controls. The original has 48 CRT retention failures (24 normal and 24 exceptional
cleanup) plus two missing-zero-guard contract failures. Its 24 ASan normal runs
and three deliberate controls pass their measured criteria; ASan leak detection
is disabled, so those passes do not establish absence of leaks. Original guard
runs stop at the missing zero guard: negative-degree execution and final CRT
retention in those two aborted cases are unmeasured, not successful validation.
No original hidden-root double deletion/UAF is claimed.

Candidate passes 77/77 with 5128 actual denials across all 24 complete observed
sweeps, one per ordinal, propagating bad_alloc without later cleanup allocation.
Valid final CRT block/byte deltas are zero. Fixture setup and validation are outside
the hook. A collective sample owner releases published prefixes; failed construction
preserves the prior patch observer. Successful fixtures explicitly rebind it before
destroying the returned mesh. The invalid-degree cases reject 0/-1/INT_MIN while
preserving the preceding patch observer and ordered preexisting sample lists.
There is no exceptional CLI retry or external observer recovery claim.

Independent analytic checks require grid/center/triangle counts, ordered IDs,
plane/bilinear coordinates, zero initial curvature, exact triangle registration
identity in physical nodes, ordered copied vertex values, positive triangle areas
and planar unit area. Every complete ordered node/adjacency/triangle/area/UV/sample
observation matches the original exactly across all 48 normal cases. Existing
samples retain identity/order and remain distinct from copied physical nodes.
The public GetNoh copies a value; its temporary address is never used as node identity.

## Regression and closure audit

Required full gates: GCC serial C++17 build, CTest 35/35 with zero skips and 74
Python controls; twenty memory batteries/1214 expected outcomes; 1040 independent
scalar sequence comparisons with a real rejected alternative; selected estimator
lint, explicit new-file formatting, whitespace and architecture freshness. The
inventory has 141 files, 66 translation units, 75 headers, 22 contracts and 138
source anchors. The existing include cycle is unchanged. C06 records the owner,
sample/patch observer boundary, positive-degree ceiling and invalid-input guards.

Twice-repeated Eistute/Book runs retain all nine accepted/rejected OBJ states byte
for byte against slice-24 main, exact boundary incidence/acceptance, and an independent
189-field CSV/raw-log audit. Eistute rejects steps 2/3/4, Book 2/3; accepted steps
remain 0/1 and final accepted triangles 1168/4256. These serial MPI-disabled runs
do not invoke estimator construction: direct actual-helper tests supply that evidence.

Code, tests, contracts, documentation, scientific scope and known failure/coverage
inventory are explicitly audited here. No failing or unmeasured required gate is
waived for delivery. Exact published-head and post-merge main reports are required
before closure; documentation-only follow-up repeats build/CTest/inventory and
complete Git/working-byte audits with every compiled/tool/test/input identity frozen.
No fresh full numerical/instrument run is claimed for documentation-only revisions.

## Retained preliminary failures

The first probe compile incorrectly took the address returned by copying GetNoh
(MSVC C2102); it now checks ordered values and actual registration identity. The
first normal oracle imposed unsupported UV residual <1e-7 and failed on original
and candidate. Actual FindUV uses damping 0.65 and a 1e-5 parameter-step stop; the
identity-x/y fixture derives residual <=(1-0.65)*1e-5 plus roundoff. It still requires
all original/candidate UV traces to match exactly. Production tolerance, historical
acceptance and inverse accuracy are unchanged; preliminary failed reports are kept.

An observation-capture prefix initially used initial_ rather than estimate_. The
campaign refused the missing sweep observations. The prefix is repaired and the
differential check explicitly rejects empty observation vectors. This failed
campaign is retained; zero-comparison coverage is never accepted. The first full
candidate then retained four actual required lint failures despite passing its
other 1212 outcomes/model comparisons; bounded induction repairs their cause.
A subsequent preliminary invocation refused an existing output directory before
running any case; that valid prior 75-case record was archived under a verified
build path. No data was overwritten, no diagnostic suppressed, and no hidden
retry/fallback or relaxed production acceptance rule was introduced.

## Remaining scope and next item

Stage 3 stays open with twenty-five bounded slices once the required head/main
gates pass. Next repair historical estimator caller-owned Mesh/SubMesh/Generator
roots with explicit patch/sample lifetime. The factory no longer double-owns its
result, but CalculateAreaTriangleMedio, CalculateNumbersTriangle and
CalculateErroEstimative still retain raw roots. Their full numerical orchestration,
minor-error/degree policy and wrapper observer lifetime are unqualified here.
The visible ChargeEstimate entry is MPI-conditional and calls the radial estimator;
source search finds the mesh-estimator callers in their historical definitions.
That static observation is not global dead-code or execution proof.

Full non-power-of-two/extreme mesh validity, arbitrary patches, evaluator scratch,
sample/metadata rollback, copied foreign observers, cache refresh, logical rejection,
parallel/full-process/LSan/UBSan and general external node lifetimes remain open.
Stages 4-11 are pending. No scientific proposal, alternative generator, C++23
qualification, Eigen removal or full-application memory certification is inferred.

## Commands and evidence retention

```powershell
. ./build/local-env.ps1
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
python tools/quality.py tidy src/estimate/initial_mesh_estimate.cpp --build build/windows-gcc17
python tools/qualify_estimate_mesh.py --asan build/s25a/RelWithDebInfo/estimate_mesh_probe.exe --crt build/s25d/Debug/estimate_mesh_probe.exe --runtime "C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64" --iteration-reference build/s25-original/src/estimate/charge_estimate_process.cpp --output build/estimate-review
```

Configure tests/curve_memory in separate MSVC ASan RelWithDebInfo and Debug CRT
directories; AP_MESH_CURVE_ASAN applies only to ASan. Pin original source via
AP_MESH_CURVE_SOURCE_ROOT and verified extracted implementation via
AP_MESH_ESTIMATE_MESH_IMPLEMENTATION. Never mix Windows/Linux caches.

See stage3/estimate_mesh for per-case results/log hashes, source identities,
original blobs/extraction, preliminary failures and toolchain. Full raw logs stay
under ignored build; compact trace hashes/counts preserve identity without copying
thousands of lines. Remote main/branches/PRs/status/checks/Actions are audited before
each delivery and after merge. Zero hosted checks means absent hosted validation,
not green CI. No paid/automatic hosted workflow is introduced.
