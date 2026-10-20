# Stage 3 slice 29: charge input ownership

Candidate full gates pass. Exact published-head and post-merge main qualification remain required; stage 3 retains twenty-eight qualified slices until both pass.

Entry main: `11d721a693ada96de959abd0f455d6b2ea1460a3` (implementation #78, closure #79).
Classification: resource-lifetime and allocation-failure defect repairs, with
engineering-only caller/reader extraction and an explicit probe-runtime change.
No scientific proposal. Stage 3 remains open; stages 4-11 pending.

## Root cause and ownership boundary

LoaderBPFile allocated control-only patches into raw member fields, leaked its
trailing unused patch and exposed accumulated raw aliases across calls. Its
destructor reclaimed none. ChargeEstimate then overwrote each loaded pointer
with a reconstructed patch and leaked sixteen heap VertexAdaptive controls per
patch. The reader and reconstructed patch could also be lost on exceptions.

The reader now returns an independent list of unique control-patch owners per
call. The sole production caller is updated; this is an explicit source/API and
cross-call ownership-contract change, not a blanket compatibility claim. A local
owner covers each in-progress/trailing patch, list insertion and return move.
Other legacy reader methods keep their existing contracts and remain separate.

ChargeEstimate uses an automatic reader, retains every input owner, creates its
sixteen coordinate-only VertexAdaptive values automatically in the original
order, and owns each reconstructed patch until Geometry consumes it. Curves own
copies of the controls; the historical coordinate-only construction still gives
the copied vertices ID zero. No borrowed input point becomes a Geometry owner.

PatchBezier publishes itself into four curve observer vectors before construction
can finish. PatchObserverScope captures their preceding lengths before that
constructor. On construction, evaluation or consuming Geometry adoption failure,
it truncates only the exclusively appended suffixes without allocating or
deleting patches. This also handles an already consumed/destroyed pending patch
without dereferencing it. Committing Geometry adoption disarms the scope before
output-list and curvature insertion. Geometry retains committed curve/patch
prefixes after failure; this is resource safety, not complete logical rollback.

## Reader allocation-failure repair

An actual denied allocation caused stream extraction to fail internally, leaving
fewer than three coordinates; unchecked v[0..2] then crashed. A native PDB stack
locates the access at the reader's PointAdaptive construction. The reader now
enables badbit exceptions on its file and row streams. Resource failures propagate
before coordinate indexing; ordinary EOF/failbit behavior and valid legacy BP
record interpretation remain unchanged. Malformed/incomplete user records,
missing-index semantics and the other legacy loaders are not newly qualified.
Empty/missing/no-name reads are guards only, not positive mesh validation.

## Numerical and ordering preservation

Preserve the sixteen coordinate getters/constructions, four curve lookup and
insertion sequences (including repeated matching calls), patch constructor
arguments and default orientation, area argument 4, curvature argument 25,
triangle-area formula, extrema else-if behavior, accumulation, TRIANGLE_MEDIO,
writer invocation, stable descending GetKaMedio sorting and timer ordering.
The comparator's historical name does not make this triangle-count sorting.
The independent mechanical source review also checks all sixteen construction
arguments, all four matching/insertion blocks, the complete arithmetic/order
tail, all six timer calls and ordinary parser operations after explicitly
normalizing only the listed ownership/badbit/diagnostic changes. Its hashes and
normalization scope remain retained; it is not an independent human review.

The full unchanged CalculateKaMedioPatch/CalculateAreaPatch/
CalculateAreaTriangleMedioRad region has an exact original/repaired SHA256.
Twenty-four controlled and twenty-four actual-helper paired invocations retain
all control coordinates/IDs, curve incidence, returned order, scalar IEEE bits,
curvature counts and normal writer bytes. Cases include single and three-patch
curved/adjacent/repeated fixtures, pre-existing null/repeated observer prefixes,
stable ties and three repeated calls. Actual helpers compile as their full GCC
translation unit; this correspondence does not establish their scratch-memory
safety or remove historical downcast/VLA concerns. No formula, floating-point
order, tolerance, budget, synchronization, front/template or acceptance/stopping
policy changes. Earlier scalar/factory and analytic oracles remain required.

## Instrumentation and negative evidence

The new memory battery requires 189 expected outcomes, twenty complete allocation
sweeps/2787 denied ordinals, live Geometry observer-prefix checks and zero
normal-block/byte deltas after each denied fixture's owners unwind. ASan UAF,
CRT leak and actual allocation-hook controls must detect their deliberate defects.
The writer and read paths are included. Return-move coverage disables optional
NRVO for this target; empty discovery and zero-denial intervals fail.
An independent closure check requires attempts=ordinal+1 for every propagated
allocation failure, proving no further measured allocation while unwinding.
Internally absorbed stream failures may continue allocating during normal work;
their rows remain distinct and do not establish successful export.

Memory probes compile the actual small reader/caller, actual classes and graph/
timer/exporter dependencies with MSVC. Only the unchanged estimator constructor/
destructor is exactly extracted from its VLA-containing historical unit. Three
existing numerical members have controlled definitions only in the test target,
forcing exceptions at every first/second/third evaluation position. There is no
production callback seam. The separate GCC target compiles the actual complete
numerical unit and supplies the independent nonempty correspondence observations.

The original snapshot verifies all 484 production/header/vendor Git blobs at the
entry revision. Exact extracted original caller/reader/lifetime/lookup bodies and
their hashes are retained. The same 189 original outcomes contain 155 failures
and 34 expected controls. ReadReuse intentionally rejects the old accumulated/raw
return contract. Direct reader tests explicitly delete the returned historical
raw controls but still expose the trailing patch leak; the original caller has
no such reclamation. Original exception cases expose stale curve observers.
Original allocation sweeps stop at their first mismatch/crash; later ordinals
remain unmeasured. ASan with leak detection disabled is not leak freedom.

An initial target link omitted actual exporter graph dependencies; actual Node,
Element, Triangle, Mesh and SubMesh units repair that target without stubs. The
reader crash and eight subsequent DLL Debug STL writer-sweep aborts are retained.
An experimental Debug ASan build did not observe the CRT hook and is unavailable
fault evidence, not a zero-allocation success.

The first full-candidate inventory rejected 40 discovered tests where 41 were
required, despite every discovered case passing: conditional real-helper test
registration preceded target definition. Moving that registration after the
target fixes discovery. The retained CMake inventory was then stale and its gate
also rejected the candidate. Refresh the deterministic inventory explicitly;
require the exact prior 39 names plus both new names before accepting the full
campaign. Both failed preflights and the repaired discovery remain retained.

An independent application-free standard-stream control reproduces the DLL
Debug CRT abort: one of four measured allocation denials aborts. With the static
Debug CRT, its single measured denial does not abort; the stream internally
absorbs it (caught=0). The new probe explicitly uses /MTd with iterator level zero
in every Debug unit, while RelWithDebInfo ASan keeps /MD. Both original/repaired
static import inventories are retained and reject a DLL Debug CRT. This is a
documented qualifier configuration change, not a production writer workaround
or suppressed denial. All twenty complete repaired sweeps are rerun under it.

Writer streams may internally absorb a denial and leave partial/stale output.
The failure gate measures memory and live observers; it does not certify
successful export, atomic file replacement or caller error reporting. Normal
writer bytes are compared separately. No original failure is relabeled green,
and no timeout, tolerance, budget or required test is silently relaxed.

## Required regression and closure audit

The full campaign builds GCC serial C++17, requires 41/41 CTest with zero skips
and 74 Python controls, all previous 1763 outcomes plus the new 189, 1040 nonempty
scalar sequences at 520 degrees with the rejected recomputation control, eight
selected production lint units, explicit format/whitespace/inventory and exact
twice-repeated Eistute/Book traces. Every accepted/rejected OBJ, incidence,
boundary and acceptance state and the independent 189 CSV fields remain checked.
Exact delivery revisions retain command, input, executable, tree and raw-log
identities. No automatic or paid hosted workflow is introduced; zero configured
remote checks means absence of hosted validation.

Code audit: unique input/pending owners and consuming Geometry adoption have no
raw ownership gap; observer teardown is nonallocating and never reads a destroyed
pending object. Tests challenge normal/repeated/throwing/denied paths and the
original failures. C23 records the explicit return-contract change and observer
preconditions; C06/C07 and the earlier batteries remain unchanged and required.
The inventory covers 149 files, 72 units, 77 headers, 23 contracts/152 anchors and
the existing one include cycle. Documentation retains failures and limits.
Scientific audit: all three numerical helper bodies and their paired outcomes
are exact; no new scientific claim or advisor-gated policy change is made.

Known limits: live non-null Geometry/timer and borrowed curves, exclusive suffix
publication and no intermediate/concurrent observer consumption are required.
Arbitrary callbacks, foreign publications, degenerate within-patch curve alias
layouts, malformed parser records, full geometry/cache validity and complete
metadata/error/history/ID/budget/mesh/acceptance rollback or CLI retry are not
qualified. Curvature-helper overwritten PointAdaptive allocations remain a
separate known root. Full historical MSVC units retain VLA blockers; full-process,
parallel, LSan and UBSan remain unqualified. Allocation timing/counts change;
there is no performance or unchanged-allocation claim. This bounded slice cannot
close stage 3 or authorize stages 4-11/scientific extensions.

## Reproduction and retained records

Use the qualified local toolchain before every command. The retained JSON contains
the complete argv, source/executable identities and raw-log hashes. Configure
tests/curve_memory in separate MSVC ASan RelWithDebInfo, static Debug CRT and GCC
directories; AP_MESH_CURVE_SOURCE_ROOT selects the Git-verified original snapshot.
The extractor rejects changed source boundaries instead of substituting methods.

```powershell
. ./build/local-env.ps1
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose --output-junit build/stage3-charge.xml
python tools/quality.py tidy src/estimate/charge_input_estimate.cpp src/input_output/control_patch_reader.cpp src/data/curve/curve_adaptive.cpp --build build/windows-gcc17
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
```

Use tools/qualify_charge_input.py with --asan/--crt/--runtime/--output and
tools/compare_charge_input.py with --original/--candidate/--original-root/
--candidate-root/--kind/--output as recorded in the campaign. Candidate, exact
head/main, original, failed DLL preflight, native reader stack, independent stream
control and source/toolchain identities remain in stage3/charge_input. Large raw
ordinal/control/incidence observations remain local with counts/hashes retained.
