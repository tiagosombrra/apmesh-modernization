# Stage 3 slice 26: temporary triangle-count ownership

PR #74 integrates head `82261a7e305bcde0920ecca0dcb9d7a50893ecc9` as main
`96ed6ae03906d1385135276b1781f67ea59d9363`, preserving complete tree `51b0e00ec92c84d832ac83a08f65261ccba4d5df`
(1840 blobs). Full exact-head/main gates pass against the same 567
protected inputs: CTest 36/36, zero skips, 74 Python controls, twenty-one memory
batteries/1373 expected outcomes, the retained 1040 scalar sequence comparisons,
count/factory lint, format/inventory and exact twice-repeated Eistute/Book traces.

Entry main: `3834d59bd03229c5cf70c4ddad073f5e2f4c74ac`.
Classification: behavior-changing resource-lifetime defect repair, no scientific proposal.
Stage 3 remains open; area/error estimator ownership is the next bounded item.

## Root cause and repair

CalculateNumbersTriangle discarded the raw SubMesh returned by InitialMeshEstimate
after reading its element count. The preceding construction slice had removed the
hidden MeshAdaptive, but this caller still retained no owner for its physical mesh.
It also left the patch pointing at that temporary mesh and kept its fresh sample
publications in curves. Simply deleting the mesh would leave a dangling patch
observer; releasing every Geometry sample would wrongly delete borrowed preexisting
objects. Both the physical mesh and the selective sample lifetime require an owner.

The public compatibility method now delegates to CountEstimateTriangles. One
unique_ptr owns the temporary SubMesh. A private TriangleCountScope captures the
preceding patch observer, four borrowed curves and which point lists were empty
on entry, without allocation. The existing construction factory appends only fresh
samples to those initially empty lists; it skips every initially nonempty list.
The scope therefore owns exactly these fresh published samples, including partial
prefixes on failure, while borrowing every preexisting sample and parameter list.

On exit the scope restores the prior patch observer, clears all aliases of each
owned sample in its captured owner lists, deletes each object once and clears only
those initially empty lists. Repeated curve pointers and repeated corner aliases
are handled without allocation. Captured initially nonempty point lists and all
parameter lists remain untouched, retaining physical list-node identity. No global
registry or shared_ptr is introduced. The general CurveSampleLifetime has different
semantics: it owns all current Geometry samples, whereas counting must preserve
borrowed entry samples. This private boundary intentionally does not substitute
one lifetime for the other or create a second application-wide authority.

The unique mesh variable is declared before its scope guard. Exit restores the
patch and releases fresh samples before destroying the physical mesh; SetNoh owns
independent copied nodes, so those mesh vertices do not depend on curve sample
objects. Constructor-failure unwinding destroys the factory's private mesh before
the outer count scope releases its published sample prefix. Actual triangle/SubMesh
destruction already follows the qualified observer/node ordering.

The returned long count, construction/evaluation order, IDs, floating recurrence,
UV inversion and all scientific policies remain unchanged. Counting now restores
the caller's entry lifetime state rather than leaving temporary objects published.
PatchBezier evaluator scratch and global call counters are not rolled back; no
snapshot of application metadata, exception retry, numerical recovery, acceptance
change or alternative generator is added. Area/error wrappers remain unchanged.

## Paired actual-source evidence

The original snapshot contains 478 Git-blob-verified source/header/vendor files at
entry. Its CalculateNumbersTriangle body is copied verbatim except the minimal
class qualifier. A minimal InitialMeshEstimate interface performs the same owned-
builder release as the entry compatibility method; the adapter does not reclaim
the original result or samples. Original source/function/adapter hashes are kept.
Actual construction, Bezier/curve, physical node/triangle/SubMesh and sample-lifetime
units are compiled with it. Candidate instruments the actual production count unit.
The whole historical ChargeEstimateProcess translation unit/constructor, area/error
wrappers and Generator orchestration are not instrumented. The final thin public
forwarding method is source-audited, without changing its signature or class ABI.

The 159 expected outcomes comprise 84 normal ASan/Debug CRT cases (plane/bilinear,
seven layouts, degree 1/2/4), 42 actual-wrapper allocation sweeps, 28 repeated-call
cases, two invalid-degree guard cases and real ASan UAF/CRT leak/hook controls.
Seven layouts cover fresh, each alternating mask, all preexisting lists, shared
borrowed endpoints with a live parent triangle, repeated curve incidences and a
null preceding patch observer. Every fixture also owns a distinct preceding physical
mesh with three nodes and a live half-area triangle. Every actual curve receives
a nonempty parameter list, including when its point list starts empty; this is a
deliberate independent-metadata lifetime fixture, not geometric consistency proof.
Borrowed lists include null entries; shared borrowed nodes have IDs, seven scalar
fields and actual null/parent element observer list nodes.

After each call, the oracle requires exact preceding patch observer/ID/area state,
curve identity, ordered sample pointers and physical point-list nodes, ordered
parameter values/list nodes, borrowed node IDs/coordinates/four curvature fields,
and ordered element observer values/list nodes. The preceding physical graph must
remain traversable; only after observer equality is established does the probe
traverse it through the patch. Empty borrowed lists/null preceding observers are
guards alongside nonempty real graphs, never substituted for all coverage.

Independent analytic counts are 4*degree^2. All 168 returned values in the normal
and three-call repetition observations match the original exactly: 84 normal and
84 repeated degree 1/2/4 results. Lifetime observations intentionally change from
unrestored to restored. This is not a claim that complete original/repaired state
traces are identical. Repeated counts are fresh serial component invocations after
successful return, not retries after allocation failure or a production CLI policy.
Invalid-degree cases preserve the existing factory's 0/-1/INT_MIN rejection and
the complete borrowed graph; the construction guard is not changed by this slice.

## Allocation failures and original limitations

Candidate passes all 159 outcomes, all 42 complete observed actual-wrapper sweeps
and 9014 injected denials. Calibration and fixture/snapshot setup are separately
identified. Each ordinal must deny one real allocation, propagate bad_alloc and
perform no subsequent allocation during unwinding. Live normal-block/byte deltas
are measured after the hook ends but before fixture teardown, with the preceding
mesh and borrowed sample graph alive; both deltas are zero and exact observer
restoration is required. Valid terminal CRT block/byte deltas are also zero.
The new scope introduces no extra observed allocation in the 42 first-call entry
calibrations: original/repaired counts match exactly. Resource lifetimes and later
repeated-call allocation behavior intentionally change; no performance, unchanged
peak-storage or global allocation-behavior claim is made.

Original fails 154 outcomes: 84 normal lifetimes, 28 repeated-call lifetimes and
42 failure cases. Its two existing invalid-degree guards and three real controls
are expected. Original normal/repeated calls always leave the patch observer on
their unowned temporary, and CRT retains their private physical graphs after
fixture sample cleanup. The fixture's collective sample owner cleans reachable
published samples only when the fixture ends; this does not repair the method's
live boundary or reclaim its lost physical mesh. ASan lifetime mismatches do not
claim an original demonstrated UAF; the genuine UAF is the separate deliberate
instrument control. No whole-process memory conclusion is inferred.

An original successful sweep calibration itself leaks its private mesh and fails
observer restoration, so original terminal CRT deltas include calibration retention.
This is recorded explicitly, not misattributed solely to failed calls. Per-denial
live checkpoints independently measure exceptional cleanup. Thirty original sweeps
stop at a live newly published sample-prefix mismatch; later ordinals are unmeasured.
Twelve all-preexisting/shared-borrowed sweeps finish every denied ordinal with their
borrowed graph restored, but still fail the successful-calibration/terminal leak
criterion. No complete original exception sweep is described as a new failure of
the previously qualified constructor. Candidate must independently satisfy complete
calibration restoration, all live ordinals and terminal cleanup.

The positive allocation-hook control denies one actual allocation. The deliberate
CRT leak and ASan heap-use-after-free controls must fail with their actual measured
diagnostics. Zero tests, skipped instrumentation or rejected candidates are never
reported as successful coverage. Original negatives remain preserved.

The first documentation closure audit stopped on a local verifier inventory error:
the new CTest count of 36 had incorrectly replaced the unchanged triangle observer
battery's required count of 35. Build/CTest 36/36 and the full implementation
head/main reports were already passing; the retained observer battery contains
all 35 required outcomes. The single checker predicate is restored to its exact
existing component inventory. The failed revision/report, command/log hashes and
before/after checker hashes are retained in documentation_inventory_failure.json.
No test is removed, no production or protected input changes, and no gate is waived.
Exact documentation head/main audits are repeated with all 21 explicit battery
inventories and all 567 protected identities required unchanged.

## Closure audit and regression

- Code: one actual temporary mesh owner, one private selective sample lifetime,
  explicit borrowed patch/curve/sample boundaries and no ownership import from core.
- Tests: 159 new expected outcomes/42 complete sweeps/9014 denials/168 paired count
  values, repeated calls, invalid inputs and real memory/hook controls. All 1214
  prior outcomes and 1040 existing scalar sequence comparisons remain required.
- Contracts: C06 records selective ownership and fixed-topology/actual-publication
  assumptions. Inventory is 143 files, 67 translation units, 76 headers, 22
  contracts and 141 source anchors; the existing include cycle is unchanged.
- Documentation: plan/state/worklog and this consolidated evidence identify exact
  delivery revisions, original limitations, scientific scope and the next item.
- Scientific scope: formulas, floating order, IDs, boundary synchronization,
  quadtree/templates/front, adaptation/acceptance/stopping, budgets and tolerances
  remain unchanged. Lifetime changes are explicit behavior-changing defect repairs.
- Required regression: GCC serial C++17 build, CTest 36/36 with zero skips and
  74 Python controls, twenty-one batteries/1373 expected outcomes, existing 1040
  scalar comparisons, strict count/factory lint, explicit formatting and whitespace,
  architecture freshness and complete Git/working-byte identity audits.

Eistute and Book run twice under unchanged budgets. All nine accepted/rejected OBJ
states match slice-25 main byte for byte, with exact incidence/boundary/acceptance
and independent 189-field CSV/raw-log audits. Accepted steps remain 0/1; Eistute
rejects 2/3/4 and Book 2/3, with final accepted triangles 1168/4256. Serial MPI-
disabled runs do not invoke the historical counting caller; direct actual-helper
tests supply its measured evidence. Required gates must pass on the exact published
head and again on merged main. Documentation-only closure repeats build/CTest/
inventory and complete Git/byte checks with all 567 protected identities frozen;
it retains the full instrument/numerical evidence against unchanged inputs without
claiming fresh full campaigns for documentation-only revisions.

## Remaining scope and next item

Stage 3 remains open. Next repair CalculateAreaTriangleMedio's raw Mesh root,
replacement/patch/sample lifetime and CalculateErroEstimative's leaked Generator
with numerical-policy evidence. Those methods and minor-error/degree selection
are unchanged and unqualified here. The public raw construction compatibility
method remains available with its explicit owner-transfer contract.

Counting requires a live patch/four non-null curves, fixed topology, exclusively
deletable newly published factory samples and unchanged initially nonempty lists.
Arbitrary/custom patch callbacks that alter captured lists, competing ownership,
concurrent consumption, invalid preexisting observers, evaluator scratch rollback,
complete extreme/non-power-of-two mesh validity, general cache/foreign observer
semantics, logical rejection, parallel/full-process/LSan/UBSan and broader compiler
qualification remain open. Repeated incidence, null markers and independently
seeded parameter lists establish lifetime properties, not geometric validity.
Stages 4-11 remain pending; no C++23 qualification or Eigen-removal claim is made.

## Commands and retained reports

```powershell
. ./build/local-env.ps1
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
python tools/quality.py tidy src/estimate/initial_mesh_estimate.cpp src/estimate/triangle_count_estimate.cpp --build build/windows-gcc17
python tools/qualify_triangle_count.py --asan build/s26a/RelWithDebInfo/triangle_count_probe.exe --crt build/s26d/Debug/triangle_count_probe.exe --runtime "C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64" --output build/count-review
```

Configure tests/curve_memory in separate MSVC ASan RelWithDebInfo and Debug CRT
directories; AP_MESH_CURVE_ASAN applies only to ASan. For original evidence pin
AP_MESH_CURVE_SOURCE_ROOT to the verified entry snapshot and
AP_MESH_TRIANGLE_COUNT_IMPLEMENTATION to its verified adapter. Windows/Linux
caches remain separate. Per-case/command hashes, compact live-state/sweep records,
478 original blobs, extraction and toolchain are under stage3/triangle_count.
Full raw logs/ordinal records remain local under ignored build, with content hashes.
Before delivery and after merge audit remote main, every branch, open PRs/issues,
status/check contexts and Actions. Zero configured checks means absent hosted
validation, not green CI. No paid or automatic hosted workflow is introduced.
