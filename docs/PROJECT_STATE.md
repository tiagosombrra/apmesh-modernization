# Project state

## Current checkpoint and active work

Reviewed production main: `84fff0d2344429aaf61f9bae5c109b86c35fddad` (PR #153).
Exact consolidation head/main status is recorded by its PR and local integration seal.
The [consolidated audit](evidence/STAGE3_CONSOLIDATION_AUDIT.md) replaced the
automatic sequence of root-border microaudits with five finite work packages.

| Stage | Current disposition |
| --- | --- |
| 0-2 | Closed for their measured scope |
| 3: memory and lifecycle | Open; 37 historical numbered slices, with later bounded repairs recorded separately |
| 4-11 | Pending; P1 supplies a bounded stage 4 compiler prerequisite for stage 3 instruments |

P1 delivered the demonstrated complete serial MSVC build repair. The actual
full ap_mesh target builds with C++17 and Debug iterator checks, without excluded
source units. The existing pi definition and automatically owned replacements
for runtime-sized scratch arrays resolve the observed blockers in three source
files. Formulas, expression order, inputs and scientific policies are preserved.
Stack scratch becomes dynamically allocated storage; no unchanged-allocation or
MPI exception guarantee is claimed. The original compiler failure remains intact.

Build the executable with `cmake --preset windows-msvc-serial` followed by
`cmake --build --preset windows-msvc-serial`. The output is
`build/windows-msvc-serial/bin/Debug/ap_mesh.exe`. This is a development artifact;
whole-process sanitizer, Release distribution, MPI/OpenMP and C++23 qualification
remain outside this delivery. [Build scope and evidence](evidence/MSVC_SERIAL_CPP17_BUILD.md)
record the commands and limitations.

P1 exact head/main passed 74 CTest entries without failures/skips, with 380
Python controls nested in tooling.controls, focused native and real MSVC CLI
controls, nine Eistute/Book states, 45 exact scientific artifacts and 123 boundary
comparisons. PR #134 and its local integration seal identify revisions/artifacts.
P2 preserves that evidence by identity; it does not repeat or relabel it.

P2 fixes the [serial execution ledger](architecture/SERIAL_EXECUTION_LEDGER.md):
ten groups using existing inputs/controls, explicit owner/observer roots,
terminal-versus-logical-retry decisions, and three instrument applicability
profiles. It names 32 nominal production launches and five directed caller cases;
these are a future finite inventory, not new memory observations. Output-mode
variants, no-sync lifetime, same-process reuse and external Geometry remain
distinct. Debug compilation is not leak accounting. The ledger retains every
open closure assignment and stops expansion at the first instrument/caller failure.

P2 exact head/main passed 74 CTest entries and 380 nested Python controls, source/
input/application/prior-evidence identity, recipe replay, architecture/contracts,
whitespace and staged/remote checks. PR #135 retains its exact identities.

P3's [first complete MSVC/ASan observation](evidence/SERIAL_ASAN_SP02.md) passed
at PR #135 main. All 73 native units compiled with ASan in C++17 RelWithDebInfo.
The actual release control passed and the actual expired read was detected.
Natural SP-02 ran once, returned zero and passed independent physical/UV/analytic
and boundary checks: accepted initial step 0, two patches, eight triangles and
one positive shared-boundary comparison, without an ASan diagnostic. There was
no rejected/adaptive retry state. This is bounded complete-process evidence,
not whole inventory, leak, CRT/LSan/UBSan or parallel qualification.

The next fixed campaign passed SP-01/03/04 but stopped at SP-05's 60-second cap.
One bounded CPU/stack observation localized an allocation hot path in Face::quality.
The [scratch correction](evidence/FACE_QUALITY_SCRATCH.md) changes one production
file to coordinate-only temporaries, retaining arithmetic and comparison order.
GCC, MSVC/ASan and checked Debug each preserve 4,230 scalar bits over 846 paired
rows, while quality allocations fall from 12/24/36 to zero. Actual denial controls
remain required. Public owning center APIs and all scientific policies are fixed.

Candidate SP-05 then completes once in 13.0484 seconds under the same 60-second
cap: accepted 0/1, rejected 2/3, retry 1, eight positive boundary comparisons and
no ASan diagnostic. The original three-state prefix retains 16 exact artifacts
and three exact metrics rows. Original failed processes remain failed evidence.
No other ASan production case was added in that correction. PR #137 passed its
exact-head/main 75 CTest/380 nested controls and frozen nine-state GCC regression
(45 exact artifacts, 123 boundary comparisons), plus scoped source/resource gates.

The [remaining fixed ASan production observations](evidence/SERIAL_ASAN_REMAINING.md)
now pass SP-06..08 with that same rebuilt artifact, without further compilation.
Exactly five processes complete below their unchanged 300-second caps, all with
empty stderr. Eistute and Book each repeat twice with exact OBJ/acceptance/boundary
comparisons, the prescribed accepted/rejected steps and 246 positive boundary
comparisons total. The existing no-sync configuration returns zero through normal
CLI teardown; it does not qualify synchronized boundaries. Other instrument and
caller obligations remain open.

The [terminal observer requalification](evidence/SERIAL_ASAN_TERMINAL_REQUALIFICATION.md)
now passes. An external actual SubMesh allocation and explicit counters exposed
the missing /EHsc exception semantics (C4530). The standalone test target now
requires /EHsc and treats C4530 as an error; all 74 instrumented groups are checked.
Four prerequisites pass, including nine typed payload rows and one actual
unwind allocation denied with one uncaught exception. Only then do all five
fixed SP-09/10 contexts pass their exact CLI/library oracles, without unexpected
ASan diagnostics. Original failed artifacts remain failed and intact.
Production, scientific policies and original fixture/oracle files are unchanged.
Earlier natural ASan records retain their actual flags; they do not establish
exception unwinding. No canonical application campaign is repeated.

The [closure ledger](architecture/STAGE3_CLOSURE_INVENTORY.md) still has ten
inherited obligations: three have bounded qualification and seven remain
partial/open. P1 removes the compiler prerequisite, not the S3-09 complete-process
memory obligation. No required observation is waived and no stage is closed.

## Consolidated internal serial engine/context milestone

The [milestone contract](evidence/ENGINE_CONTEXT_MILESTONE.md) fixes six objective
exit criteria, the admitted synchronous caller protocol and the explicit remaining
state boundary. Implementation criteria are established at PR #153; current exact-
head/main gates and the integration seal close this bounded milestone. The internal
engine, typed request, owned identity and eleven control groups are delivered.
The [complete runtime matrix](architecture/ENGINE_CONTEXT_STATE.json) maps all 203
preserved definitions: 185 have context bindings (181 group fields plus four
identity/output fields), and 18 remain uncaptured. EPSYLON and legacy I/O also
retain consumers beyond their captured roles. No global-removal percentage,
pure factory, reentrant engine or repeated-generation safety is claimed.

Current scientific/native/MSVC/instrument evidence is reused by unchanged source,
executable, build-configuration and report identity. This documentation-only
consolidation runs existing head/main CTest and quality/contracts/remote checks,
without production/test/fixture changes or new campaigns. Stage 3 and full stage 6
remain open; all ten stage 3 row dispositions stay unchanged. The next concrete
production dependency is attempt metadata ownership (global step/retry duplicated
from existing generator state), with the existing trace/ID oracles. Precision and
parallel/instrument obligations retain their separate boundaries. Legacy positional
CMake convenience recipes are explicitly recorded as an unresolved workflow item.

## Delivered production context: serial flow controls

PR #153 delivers the [serial flow group](evidence/SERIAL_FLOW_CONTEXT.md): four
switches and the literal template mode. Graph operations, applied hybrid projection,
diagnostic predicates/formats and the exact template comparison/phase are preserved.
Fronts own template string copies; missing groups retain live legacy reads. The
qualified four native cases and exact head/main scientific/delivery evidence keep
their original bounded scope. String copying can allocate; no recovery promise.

## Delivered production context: advancing-front and postprocess controls

The [AFT context](evidence/AFT_CONTEXT.md) owns six active ratio/smoothing/
postprocess controls copied from already-applied process state. The existing
ApplyRuntimeConfig clamp remains the sole CLI smoothing clamp; the double-to-
unsigned constructor conversion stays in place. One stable write still sets
postprocess passes to 2 at its original position. A pinned effective generator
value is observed by Adapter; each front owns a copy of three postprocess values.
Raw context remains unchanged. Missing settings and unconfigured standalone
fronts keep live globals. Three cases in the existing native probe check 15 raw/
15 stable double representations, constructor binding/conversion, 36 real poor-
region smoothing outputs and three snapshots after generator retirement. Reuse
the existing scientific/delivery regression without a new model, target or
instrument campaign. Shared TOLERANCE_AFT and the inactive constructor tolerance
argument retain their exact behavior; tolerance propagation is outside this lot.
Other runtime globals remain serialized. Stage 3/6 and memory/recovery/parallel
obligations remain open.

## Delivered production context: remaining generation acceptance controls

The [acceptance context](evidence/ACCEPTANCE_CONTEXT.md) owns the remaining 26
scoring/growth/small-gain/efficiency acceptance controls captured from current
process values. The group has no stable writes, so it needs no effective override
copy. The growth penalty receives five explicit inputs at its three original call
positions. All arithmetic, comparisons, short-circuit decisions and report spelling
are preserved. Missing settings retain live global reads. Three native cases in
the existing probe check 66 exact double representations, four integer fields,
source retirement, foreign globals, 30 actual growth-penalty outputs and six real
acceptance reports. The local source-reversal driver was corrected to distinguish
AcceptanceMode from the suffix of ConsistencyAcceptanceMode; production and the
reversal oracle stay unchanged. Reuse the existing nine-state accepted/rejected
scientific regression and delivery gates without a new model, target or instrument
campaign. Remaining AFT/runtime globals still require serialization; Stage 3/6,
whole-process memory and recovery/parallel obligations remain open.

## Delivered production context: patch and group consistency controls

The [patch consistency context](evidence/PATCH_CONSISTENCY_CONTEXT.md) owns 18
equivalence/group-limit/consistency-acceptance controls captured from current
process values. Parsing, defaults and scientific expressions remain unchanged.
Two stable mode writes keep their original positions around curve consistency;
lazy separate effective state preserves the first update and raw configuration.
Absent settings retain live global reads/writes. Three cases in the existing
native probe check 33 raw/33 stable double representations, seven integer fields,
source retirement, foreign globals, intermediate/final modes and 144 real
regularizer results over steps 2/3. Foreign controls must produce an actual
two-patch group, clamping and different outputs. Dormant controls stay dormant.
Reuse the existing scientific/delivery regression without a new model, target or
instrument campaign. Other acceptance/AFT controls remain shared and serialized;
Stage 3/6, full-generation reuse/recovery and memory/parallel obligations stay open.

## Delivered production context: patch generation and refinement controls

The [patch generation context](evidence/PATCH_GENERATION_CONTEXT.md) owns 37
generation/refinement/spatial/micro controls. The factory captures three
RuntimeConfig fields and 34 existing process values without parser/default changes.
Thirteen stable writes retain their values/order in three blocks at the original
positions; separate effective instance state preserves earlier updates and raw
configuration. Scalar consumers retain formulas, branch/diagnostic spelling,
selection, acceptance and stopping policies. Absent settings keep live global
reads and original writes. Three cases in the existing native metrics probe check
84 raw/84 stable double representations, nine integer fields, retired sources,
foreign globals and 36 actual adaptation/smoothing factor results. The unchanged
scientific regression remains required; no new model, target or instrument
campaign. Patch consistency, acceptance and other shared controls still require
serialization. Stage 3/6 and full recovery/concurrency/memory obligations stay open.

## Delivered production context: quadtree limits and saturation controls

The [quadtree context](evidence/QUADTREE_CONTROLS_CONTEXT.md) owns 19 depth,
saturation and quality controls. Four stable writes retain their original values
and distinct positions in a pinned effective generator value. Adapter observes
that value through an explicit live/stationary borrow, retaining its original
one-argument/default constructor paths. Each generated quadtree owns a copy of
three quality controls; cells consult their existing tree observer. Standalone
trees without settings retain live global reads. Depth estimation/resolution,
subdivision, template statistics and all scientific expressions keep their tokens.
Three native cases check 27 raw/27 stable doubles, ten integer fields, 42 depth
results, nine real subdivision/template-stat observations and three tree snapshots
after generator retirement. The original missing-declaration build failure and
partial repeated-command analysis are retained. Canonical analysis uses each
actual production command once, plus the existing probe command with flags intact.
Require the existing delivery/scientific regression; other shared controls and
Stage 3/6 obligations remain open.

## Delivered production context: curve discretization and point budgets

The [curve controls context](evidence/CURVE_CONTROLS_CONTEXT.md) owns 17 values:
adaptation weights/sensitivity, point budgets/limits, curve consistency and the
external/internal discretization pair. The factory captures nine RuntimeConfig
fields and eight process values, with no new parser keys/default normalization.
Two stable mode updates retain their original distinct positions in a shared
effective instance copy; the second preserves the first adjustment. Raw context
stays unchanged. Adapter observes the stationary context for its independent
factor pair; no square root is recomputed when capturing either value. The point
limiter keeps its original min/max order. Three native cases check 33 raw/33 stable
double representations, six integer fields, retired source, foreign globals,
18 actual point targets and 12 owned Adapter factor observations. Existing
synchronization/publication/rollback flow and scientific formulas stay unchanged.
Require the existing delivery/scientific regression. Remaining patch/quadtree
controls and global mutations still require serialization; no stage closure.

## Delivered production context: element budget controls

The [element budget context](evidence/ELEMENT_BUDGET_CONTEXT.md) owns 32 controls:
step limits/pressure/retry scaling, patch-local budgets, element growth/target
limits and patch allocation. The factory samples their existing process values;
no parser key, default or validation changes. Five stable-mode flags keep their
values/order/location in separate effective instance state. Raw context remains
unchanged; absent settings retain live global reads and the five original writes.
The target limiter receives explicit effective bounds with unchanged arithmetic.
Existing budget pressure/counter/target members and all branch/acceptance/retry
expressions remain intact. Three native cases check 72 raw/72 stable exact double
representations, eight integer fields, source retirement, foreign globals and
18 real target-clamp outputs. The original failed native control setup is retained;
both legacy comparisons now start from the same raw case, without changing their
oracles. Reuse the existing delivery/scientific regression. Curve-point, quadtree,
generation/refinement controls and other shared state still require serialization.

## Delivered production context: adaptation settings and effective adjustments

The [adaptation context](evidence/ADAPTATION_CONTEXT.md) owns relaxation, maximum
delta and lower/upper factor bounds copied from RuntimeConfig. Stable overrides
use a separate optional instance value; the raw context remains unchanged. The
four original assignments keep their values/order/location. Existing per-attempt
relaxation/delta members and retry/scaling expressions stay intact. Generator
domain, smoothing, rate-limit and curve-factor reads use the same effective bounds.
Contexts without adaptation settings retain live global reads and stable writes.
The existing native metrics probe checks three cases, source retirement,
conflicting globals, 12 raw/12 stable exact double representations and 18 outputs
from the actual rate-limit function, including legacy negative/update controls.
Use the existing delivery/scientific regression; no new model/instrument campaign.
Budget/refinement controls and other mutations remain shared and serialized.

## Delivered production context: stopping/retry criteria ownership

The [stopping/retry context](evidence/STOP_RETRY_CONTEXT.md) owns eleven generator
criteria: global/local error targets, minimum improvement, patience, retry count/
shrink, two growth limits and three saturation thresholds. The factory captures
six RuntimeConfig values and five current legacy thresholds. Decisions and
reports consume the same owned values without changing expressions or literals.
Stable mode still promotes retries with max(1,count) at the original point;
owned criteria use separate effective instance state, while legacy criteria retain
the global update. Default/identity-only/adaptive-only contexts keep live reads.
The existing native metrics probe checks three criteria cases, 27 exact double
representations, source retirement, conflicting globals and both promotion paths.
Use the existing scientific/delivery regression; no new instrument campaign.
Geometric EPSYLON uses, relaxation/budget controls and remaining shared state stay
unchanged and serialized. This does not close Stage 3 or stage 6.

## Delivered production context: adaptive-policy configuration ownership

The [adaptive-policy context](evidence/ADAPTIVE_POLICY_CONTEXT.md) owns the six
inputs used to build the generator's policy: mode, adaptive/legacy step limits,
intensity, quality priority and target growth. MakeGenerationContext snapshots
validated configuration plus the current legacy STEPS value. The generator uses
these inputs in its original formulas; its Adapter borrows the same raw mode,
intensity and quality priority for domain decisions. No clamp moves into the
factory. A missing policy snapshot preserves live global reads for default and
identity-only callers. The existing metrics probe checks four policy cases,
28 exact double representations, source retirement, conflicting globals and
both compatibility paths. Use the existing delivery/scientific regression;
other controls, runtime mutations and numerical globals remain shared/serialized.

## Delivered production boundary: typed engine execution

The [typed generation request](evidence/TYPED_GENERATION_REQUEST.md) replaces
the CLI's synthetic string/pointer vectors with process/thread counts and an
optional owned fallback input path. The motor consumes values directly; the
historical argument transcript stays at the CLI boundary. Execute(char*[]) remains
a compatibility wrapper. Owned context input still takes precedence; a missing
fallback path retains the built-in model and an empty path remains a file input.
Numerical configuration, scientific control flow and parallel routing are fixed.
The existing metrics probe checks typed/legacy input routing and exception/log
behavior; use the existing delivery regression, without another instrument campaign.
This removes an internal textual protocol, not the remaining numerical globals.

## Delivered production context: owned generation identity/output

The [generation context lot](evidence/GENERATION_CONTEXT.md) owns input identity,
output prefix, write mode and literal process suffix in each explicit generator.
The CLI uses this path; the serial reader and generator outputs consume owned
strings, while the Adapter observes the same context for domain logs. The owner
is immovable and outlives that borrow. The existing metrics probe checks two
identities after their source is changed/retired and interleaves three real report
writes against conflicting globals. The default constructor preserves live legacy
reads. Numerical policies and unmigrated globals still require serialization.
Use the existing delivery regression and scientific reference; no new instrument
campaign is introduced. The typed execution lot above removes the textual caller
protocol; numerical/runtime-state migration still needs its own bounded contract.

## Delivered production boundary: serial engine and thin CLI

The [serial engine package](evidence/SERIAL_ENGINE.md) replaces the automatic
CRT-instrument successor. It delivers APMesh::Engine, an independently linkable
internal static target; a separate configuration/state module; and a five-line
CLI. Existing consumers stop including main.cpp and share the production engine.
The three principal targets compile 78 source units instead of 219; this is a
build-graph count, not a timing benchmark. The 203 global initializers and the
configuration/CLI bodies retain their exact tokens and order. Legacy global state
still requires serialized calls. Require the existing exact-head/main regression
and scientific reference; do not add a separate instrument campaign.

The bounded 2026 milestone is this reusable serial engine/configuration/CLI
boundary with preserved C++17 behavior. It is a stage 6 prerequisite supporting
S3-05 caller work, not closure of Stage 3 or the whole modernization roadmap.
Identity/output ownership and typed execution are delivered above. The active
context lots add policy, criteria, adaptation, budgets, curves and tree controls; further migration needs a
separate bounded caller contract.

## Retained instrument obligations for closure

Complete-process CRT checkpoints still require actual clean release, deliberate
retained-storage and allocation-hook controls. Schedule instrument work when it
blocks a named production delivery or mandatory closure, not as an automatic
successor to every passing observation. SP-09/10 now have their five bounded MSVC/ASan terminal
observations; complete-process retained-storage/UB and remaining caller obligations
are still open. Do not repeat the unchanged terminal contexts for delivery.
SP-06..08 now pass; earlier observations retain their measured artifact identities.
Preserve/classify the first unexpected failure and stop expansion. Do not create
another source-only successor audit or repeat identical qualified observations
without a changed dependency. Other instruments, same-Generator reuse, caller
contracts and all remaining closure obligations stay unqualified until measured
or explicitly justified.
Follow the [five work packages](architecture/REFACTOR_SEQUENCE.md). Completion is
measured by resolved obligations or repaired defects, not test or PR counts.

The outside-root ideal retirement remains unreached/unqualified under S3-06.
Its automatic successor microaudit is superseded; all refusals, excluded events
and prior records remain intact. Reopen measurement only with an admissible
history or a named required closure experiment and a finite decision/stop rule.

Fixtures, baselines, MPI/OpenMP routing and scientific criteria are unchanged.
Complete prior checkpoints remain verbatim in
[PROJECT_STATE_HISTORY.md](PROJECT_STATE_HISTORY.md); their historical next-work
paragraphs are not an active queue.
