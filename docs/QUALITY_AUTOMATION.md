# Local quality automation

## Local coordination and impact planning

`python tools/quality.py doctor` inventories every required tool and returns nonzero
for missing tools, failed version commands, launch errors or version-query timeouts.
UNAVAILABLE means not found on PATH; it does not prove absence from the machine.
No tool is installed and no global environment is changed by the diagnostic.

The optional `tools/validation_session.py` adapter calls these existing controls.
Its local execution profile and qualified test-ID baseline are kept under the
ignored `build/validation-session/local/` directory. Typical entry points are:

```text
python tools/validation_session.py environment
python tools/validation_session.py summary --task "Current authorized work item"
python tools/validation_session.py check-summary
python tools/validation_session.py plan --scope iteration
python tools/validation_session.py plan --scope delivery --output build/delivery-plan.json
python tools/validation_session.py run --plan build/delivery-plan.json
python tools/validation_session.py metrics
```

Plans retain every qualified baseline test ID and report added unit cases.
Incremental selection is feedback only. Unknown/shared impact is conservative;
delivery scope runs the complete discovered baseline/superset without skipped tests.
A passed adapter run qualifies only its stated local regression scope. Additional
canonical package gates, fresh remote checks, exact-head/main validation and stage
closure obligations remain mandatory. The adapter never publishes or integrates.

Operational views are derived from canonical source hashes and rejected when stale.
Evidence verification checks explicit identity axes and artifact hashes; it is not
a replacement for the existing scientific or memory checkers. Expected negatives,
zero coverage and failed overall reports must retain their actual dispositions.
UTF-8 plan artifacts are written explicitly; avoid shell-dependent text redirection.
Runners hold an exclusive local process lock. After interruption, inspect its recorded
process before manually clearing a stale lock; automatic recovery never starts a retry.

The unchanged versioned pre-commit can be invoked through the adapter's `pre-commit`
action with the local child-process environment. Any hook registration is a local
opt-in; it must preserve staged-byte validation and native approval controls.

## Cumulative candidate regression and plan audit

The [2026-11-05 audit](evidence/PLAN_REGRESSION_AUDIT.md) records the complete
75-entry CTest inventory/391 nested controls, canonical incremental GCC/MSVC
builds with unchanged qualified binaries, current checked-MSVC native/invalid
input/CRT controls and static analysis of all ten cumulative changed translation
units plus their headers. Frozen/reuse GCC Eistute/Book and one checked-MSVC pair
per existing model pass; each MSVC pair retains the total 300-second cap. No retry,
new scientific model, disabled check or production change is used.

The full Doxygen command fails with 2,718 diagnostics and remains documentation
debt; no diagnostic is suppressed. Earlier complete-process ASan results retain
their artifact scopes. Required current delivery/main gates, full-process CRT/
UB/leak, parallel and remaining caller obligations are not waived by this audit.
Reuse runtime evidence only after checking source/input/compiler/binary/control
identities; record a documentation-only delta explicitly. A new dependency or
failed required check invalidates only the evidence it actually affects.

## fillMesh pointer membership

The [membership package](evidence/FILL_MESH_MEMBERSHIP.md) reuses the UV probe's
transfer-order fixture and original scans calibrated before production edits.
Require twelve pointer-sequence/owner cases and twelve repeated empty transfers
on GCC/checked MSVC, preserving prefix duplicates, null entries, equal-value
distinct identities and candidate order. Reuse the real CRT hook: deny each of
the measured successful-path allocations, require one propagated bad_alloc,
unchanged source owners, ordered observer prefixes and a complete retry with
zero retention. Preserve the rejected unordered_set/debug-proxy abort and its
stack; do not disable iterator checks. Require both C++17 builds, existing
75 CTest/391 controls, unchanged native markers, frozen GCC Eistute's five states/
25 exact artifacts/15 boundaries, source-scope proof, analysis, explicit format,
inventory/contracts and staged/remote review. No new long MSVC pair, Book or
scientific campaign; timing and integration remain open.

## Bezier FindUV array scratch

The [local scratch package](evidence/FINDUV_ARRAY_SCRATCH.md) requires a frozen
Eigen solver calibrated on GCC/MSVC before production edits, unchanged afterward.
Reuse the existing metrics target for 75 bounded affine/degenerate/nonfinite and
real-fixture cases per ABI: analytic expectations, exact UV bits, virtual-call
sequence, final public scratch, scoped counters and diagnostics must agree.
Keep the one-bit comparator negative control and original source-guard mutations.
Historical copy/observer guards reverse only one declaration, 35 accesses and two
swaps, then require the entire compact previous solver hash. Outside policy and
numerical changes must still fail. Preserve initial failed regression/calibration
records. Require C++17 GCC/checked-MSVC builds, existing 75 CTest/391 Python controls,
frozen GCC Eistute 25 exact artifacts/15 boundaries, scoped analysis admitting the
reference header, source reversal, format, inventory/contracts and staged/remote
review. No long MSVC pair, Book run, Eigen deletion or performance qualification.

## Discrete curvature adjacency transfers

The [splice package](evidence/CURVATURE_ADJACENCY_TRANSFERS.md) requires a frozen
pre-change sorter independent of the new transfer path. Retain its before-fix
GCC/MSVC results, binaries and source proof; the 60 existing fan fixtures give
120 exact/virtual curvature comparisons per ABI. Require 912 direct transfer
checks including first-match duplicate identity, destination head/tail and 48
unmatched searches. Keep the oracle unchanged after calibration. Reuse the Debug
CRT mechanism on open/closed versions of the same fan: positive real allocation/
free control, exact scalar payloads, unchanged observers and complete release.
Require canonical C++17 GCC/checked-MSVC builds, existing 75 CTest/389 controls,
frozen GCC Eistute 25 exact artifacts/15 independent boundaries, scoped analysis
including both headers, source reversal, formatting, inventory/contracts and
staged/remote review. No new model, CTest target, long MSVC pair or Book run.
Allocation failure ordinals changed; do not promote old denial observations to
revised-path qualification. Timed reuse and exact-delivery/main gates stay open.

## Contiguous AFT face incidences

The [storage package](evidence/AFT_CONTIGUOUS_INCIDENCES.md) requires canonical
C++17 GCC/checked-MSVC builds, existing 75 CTest/389 nested controls and the same
smoothing-adjacency fixture on both ABIs. Compare ordered membership across the
container boundary; preserve cancellation, duplicate entries, repeated endpoints,
null/missing keys, live values and rebuilt scopes. Use one actual Debug CRT
allocation comparison on that unchanged fixture, with a positive allocation/free
control and complete release. Do not infer whole-process savings or speedup from
this local count. Reverse only AFT incidence container/iterator types and one
alias; all other implementation tokens remain identical modulo formatting.
Require scoped analysis including the modified header, frozen GCC Eistute's
25 exact artifacts/15 independent boundaries, contracts/inventory and staged/
remote review. Observe only the fixed MSVC Eistute reuse pair under its unchanged
300-second total cap after preflight. Stop on first unexpected failure; preserve
old negative evidence. No retry, Book run, new model or test target. Broader reuse,
Book and exact-head/main gates remain mandatory before integration.

## Serial timing intervals

The [diagnostic repair](evidence/SERIAL_TIMING_INTERVALS.md) requires a reproduced
old failure, existing native metrics controls and 75 CTest/389 Python controls.
Seed only local timer timestamps during real error evaluation; require balanced
6/7 intervals and bitwise unchanged error/node curvatures. Check early full-start
through a rejected-input call and retain the rejected slow built-in fixture.
Run both compiler builds and native controls, plus frozen GCC Eistute with exact
science artifacts and positive boundaries. Require realistic runtime totals and
curvature/error partitions bounded by the full interval. Reverse only admitted
serial timer operations; retain scientific and parallel tokens, clock provider
and watchdog. Reuse the unchanged long-run negative evidence without a new MSVC
pair or Book campaign. Require scoped analysis, formatting, contracts/inventory,
staged/remote checks; integration and broader timing/recovery remain open.

## AFT edge-count lookups

The [hash-count package](evidence/AFT_EDGE_COUNT_LOOKUPS.md) reuses canonical
C++17 GCC/checked-MSVC builds and 75 CTest/389 controls. Share the existing AFT
fixture between both native probes and check 65 empty/duplicate-mask/reversed-order/
swapped-endpoint cases against known boundary/transition/internal counts. Preserve
all original loop, increment, lookup and numerical tokens beyond the admitted
container/equality/hash/reservation changes. Require frozen GCC Eistute, scoped
analysis, explicit formatting, inventory/contracts and staged/remote checks.
Observe only one new-binary MSVC Eistute pair under the same total 300 s cap;
keep its incomplete second call and all earlier failures. No retry, Book run,
new scientific model, test target or relaxed oracle. Integration remains blocked.

## Curvature vertex points

The [point-access package](evidence/CURVATURE_VERTEX_POINTS.md) reuses canonical
C++17 GCC/checked-MSVC builds and 75 CTest/389 controls. Extend only the existing
native metrics control: 60 planar/curved, boundary/closed and insertion-order
cases require exact adjacency/concavity and bitwise curvature/point results,
unchanged observers, live snapshots and virtual extension fallback. Reverse the
86 admitted bindings and wrappers to retain every original algorithm token.
Reuse the CRT hook with real allocations, a positive new/delete control and
unchanged observers; qualify the measured comparison separately from process
timing. Keep frozen GCC Eistute and one fixed new-binary MSVC pair under the
unchanged total 300-second cap. A second-call timeout remains a failed required
gate; no retry or new model. Require scoped analysis, format/token, contracts,
inventory and staged/remote checks. Book and full integration remain open.

## Temporary AFT face adjacency index

The [scoped index](evidence/AFT_FACE_ADJACENCY_INDEX.md) reuses canonical C++17
GCC/checked-MSVC builds, 75 CTest/389 nested controls and the existing adjacency
probe. Check original scan order, duplicate entries, repeated endpoints, missing
keys and live values. Preserve all remaining AFT implementation tokens except
index bindings and const iterators. Reuse unchanged negative controls; run only
Eistute for frozen GCC comparison and one checked-MSVC observation under the same
total 300-second cap. Preserve old partial output and binary/configuration hashes.
The completed first call is independently checked; a second-call timeout still
blocks adaptive qualification and integration. Book remains unmeasured on this
candidate. Require scoped analysis, explicit format/token, inventory/contracts,
staged and remote checks. No new model, target, cap or instrument campaign.

## Adaptive generator reuse

The [consistency-state repair](evidence/ADAPTIVE_GENERATOR_REUSE.md) requires two
calls per existing Eistute/Book article profile through the existing metrics
probe, on GCC and MSVC. Compare GCC against frozen output and MSVC's second call
against its independently checked fresh first call. Preserve exact scientific
artifacts, traces, IDs and positive boundaries; keep ABI-specific evidence distinct.
The first MSVC head stopped at an empty diagonal-neighbor access; four fatal
stacks constrain the added list preconditions. Keep Debug iterator checks and
require revised-head/main gates; no new model or instrument campaign.

## Serial generator reuse

The [archive isolation repair](evidence/SERIAL_GENERATOR_REUSE.md) adds one fixed
successful reuse sequence to the existing metrics control and compiles that same
probe against the canonical MSVC engine. Existing exact-head/main regression and
science gates apply; unchanged isolated destructor evidence is reused by identity.
No new CTest target or instrument campaign. Adaptive reuse/recovery remain open.

## Replaced curve observers

The [P4 replacement repair](evidence/REPLACED_CURVE_OBSERVERS.md) adds two focused
cases to the existing observer probe and requires thirteen ASan/CRT outcomes,
including the existing synchronization/UAF/leak/hook controls. Exact observer
order, repeated slots, caller-managed destination publication, scalar bits and
zero-allocation retirement are checked. Existing exact-head/main regression and
scientific gates remain; no new target, model or full-process campaign.

## Execution-owned FindUV statistics

The [diagnostic package](evidence/FIND_UV_EXECUTION_STATISTICS.md) requires existing
GCC/MSVC C++17 builds, 75 CTest/389 controls, nine scientific states/45 exact artifacts/
123 boundaries and real MSVC CLI checks on exact head/main. Keep all thirteen
prior native markers and require the new FindUV marker. Check actual Bezier/Hermite
normal/I_MAX calls, ten coordinate bit comparisons, nested/unwound scopes, foreign
aggregates, message cadence, typed/raw executions, snapshots and failed-call reset.
Retain the first unsupported Hermite-output control failure and its correction to
the existing Bezier fixture. Compare fresh CLI FindUV summaries with PR #157.
Reverse only recording/scoping/serial-summary bindings; retain all solver and policy
tokens, aggregate increments and the original global I_MAX ordinal. Reuse unchanged
production analysis; analyze the corrected probe on its final source. Require
explicit format/token, whitespace, inventory/contracts and staged/remote gates.
Four historical source guards normalize only pinned recording slots/header,
retaining their immutable bases, comparisons and original negative mutations.
Four new Python controls reject relocation/numerical/helper tampering; all original
385 controls remain. No new CTest target, model or instrument campaign;
parallel/recovery limits remain.

## Dormant runtime registry retirement

The [retirement](evidence/DORMANT_RUNTIME_REGISTRIES.md) reuses existing exact-head/
main GCC/MSVC C++17 builds, 75 CTest/385 controls, nine frozen scientific states,
45 exact artifacts/123 boundaries and MSVC CLI observations. Add no test target or
instrument campaign. Complete source comparisons permit only the two dormant set
definitions/declarations, set include and geometry forward-declaration removals;
all other production, tests, build settings, models and configurations remain exact.
Check zero first-party consumers/references, 201 unchanged ordered initializers,
185 context bindings, 16 uncaptured symbols and two named retirements. Analyze
the actual runtime-state/runtime-config commands and changed header once, preserve
flags, explicitly check formatting tokens, whitespace, inventory/contracts and
staged/remote gates. Stop at the first unexpected failure and retain its record.

## Book CMake run aliases

The [recipe repair](evidence/BOOK_CMAKE_RUN_RECIPES.md) changes only three
convenience commands and documentation. Regenerate canonical GCC/MSVC serial
build graphs, inspect all three Ninja command graph entries and twelve MSVC commands,
and require unchanged C++/tests/config/model, compiler commands, application and
prior-report identities. Reuse the nine-state/45-artifact/123-boundary scientific
reference and MSVC CLI observations from PR #155. Run existing 75 CTest/385 controls,
whitespace, contracts/inventory and staged/remote gates on exact head and main.
No new scientific model, three-profile campaign, CTest target, C++ compilation or
static-analysis run is required for the unchanged code. Any failed identity or
command/gate blocks delivery; retain the original rejected positional invocation.

## Serial attempt metadata ownership

The [attempt-state package](evidence/GENERATOR_ATTEMPT_STATE.md) requires the existing
75 CTest/385 controls, GCC/MSVC C++17 builds, nine-state/45-artifact/123-boundary
reference and real MSVC CLI checks on exact head/main. Reuse candidate/snapshot
targets with conflicting globals and attempts 0/5, keeping local repair labels,
selection/ID oracles and negative controls. Reverse only the two serial call
argument bindings; preserve mirror writes, parallel code and all other production.
Require scoped analysis using actual compilation commands, explicit token-checked
format, whitespace, contracts/inventory and staged/remote gates. Preserve the first
snapshot fixture failure and its specific expectation-order correction. No new
model, instrument campaign, target or scientific criterion.

## Internal serial engine/context milestone consolidation

The [consolidation](evidence/ENGINE_CONTEXT_MILESTONE.md) is documentation-only.
Require source/test/build/input identity, the complete 203-definition matrix,
actual factory-field binding checks, all six milestone exit dispositions and the
unchanged stage 3 ledger. Reuse PR #153 GCC/MSVC builds, 13 native markers, nine
scientific states/45 exact artifacts/123 boundary comparisons and actual MSVC CLI
controls by executable/source/report hashes. Reuse historical instrument observations
only within their original profiles; original failures remain intact. Run existing
75 CTest/385 nested controls, whitespace, contracts/inventory, staged and remote
checks on exact delivery head and merged main. No C++ file, test, CMake setting,
fixture or scientific oracle changes, so no rebuild/static-analysis or fresh
scientific/instrument/MSVC process campaign is needed. A changed dependency or
failed required identity check stops evidence reuse and blocks closure. Local
integration evidence records both newly run and reused gates explicitly.

## Serial synchronization, reconstruction and diagnostics

The [serial flow lot](evidence/SERIAL_FLOW_CONTEXT.md) reuses 75 CTest/385 nested
Python controls, C++17 GCC/MSVC builds, the frozen nine-state/45-artifact/123-boundary
reference and real MSVC CLI controls on exact head/main. Require all prior native
markers plus four cases: owned scalar/string capture, retired source, foreign
globals, actual shared-curve graph changes and diagnostic presence/metadata. Check
Adapter debug values, y/n/empty/long literal modes, unconfigured legacy fallback
and four value snapshots after generator retirement. Native report checks measure
gates/metadata; the existing reference retains full-generation scientific evidence.
Source reversal restores generator/Adapter/AFT bodies, predicates, synchronization
slot, exact template literal and phase, debug writer arguments and report formats.
Parser/apply/defaults, hybrid-off projection and other production stay unchanged.
Analyze each actual production compilation command once plus the existing probe
with flags unchanged. Require explicit token-checked format, whitespace, inventory/
contracts and staged/remote gates. No new scientific model, target or instrument
campaign is added; remaining global state and stage obligations stay visible.

## Advancing-front and postprocess controls

The [AFT lot](evidence/AFT_CONTEXT.md) reuses 75 CTest/385 nested Python controls,
C++17 GCC/MSVC builds, the frozen nine-state/45-artifact/123-boundary reference and
real MSVC CLI controls on exact head/main. Require all prior markers plus three
cases: 15 raw/15 stable exact double representations, one pass-count integer,
retired source, foreign globals, constructor factor/iteration/phi binding and
36 actual poor-region smoothing outputs. All stable cases must move a vertex;
the two raw enabled cases must differ from disabled foreign controls. Three
configured fronts must retain values/results after generator retirement. Native
unit data is bounded to a fixed UV square fan and single-pass smoothing; full
loop/selection decisions retain the existing reference. Source reversal restores
the complete generator/Adapter/AFT bodies, stable assignment and constructor order.
Parser/apply/defaults, the existing smoothing clamp, shared geometric tolerance,
inactive constructor tolerance and other production stay unchanged. Analyze each
actual production compilation command once plus the existing probe with flags
unchanged. Explicit touched-file formatting is separately token-checked. Require
whitespace, inventory/contracts and staged/remote gates. No new scientific model,
target or instrument campaign is added.

## Remaining generation acceptance controls

The [acceptance lot](evidence/ACCEPTANCE_CONTEXT.md) reuses 75 CTest/385 nested
Python controls, C++17 GCC/MSVC builds, the frozen nine-state/45-artifact/123-boundary
accepted/rejected reference and real MSVC CLI controls on exact head/main. Require
all prior native markers plus three cases: 66 exact double representations, four
integer fields, retired sources, live legacy fallback, foreign-global negatives,
30 actual growth-penalty outputs and six real accepted/rejected report labels.
Native reports check the owned mode; full decision traces use the existing frozen
reference. Source reversal restores the complete generator body, original growth
formula and three call positions with exact parameter/getter bindings. Match whole
accessor identifiers when reversing; preserve the initial local suffix-match
refusal. Parser/apply/defaults/other production stay unchanged. Analyze each actual
production compilation command once plus the existing probe with unchanged flags.
Require explicit token-checked formatting, whitespace, inventory/contracts and
staged/remote gates. No new model, target or instrument campaign is added.

## Patch and group consistency controls

The [patch consistency lot](evidence/PATCH_CONSISTENCY_CONTEXT.md) reuses 75 CTest/
385 nested Python controls, C++17 GCC/MSVC builds, the frozen nine-state/45-artifact/
123-boundary reference and real MSVC CLI controls on exact head/main. Require all
prior markers plus three cases: 33 raw/33 stable double representations, seven
integer fields, retired sources, live legacy fallback, foreign-global negative
controls and intermediate/final effective modes. Compare 144 actual regularizer
outputs for steps 2/3 before/after stable updates: budgets, h, depth, group IDs,
dispersion, penalty and active status. Foreign controls must form a positive
two-patch group, clamp and change the outputs. Source reversal restores the complete
generator body and both assignments in their original positions. Parser/apply/
defaults and other production stay unchanged. Analyze each actual production
compilation command once plus the existing probe, with flags unchanged. Require
explicit token-checked format, whitespace, inventory/contracts and staged/remote
gates. No new target, model or instrument campaign is introduced.

## Patch generation and refinement controls

The [patch generation lot](evidence/PATCH_GENERATION_CONTEXT.md) reuses 75 CTest/
385 nested Python controls, C++17 GCC/MSVC builds, the frozen nine-state/45-artifact/
123-boundary reference and real MSVC CLI controls on exact head/main. Require all
prior native markers plus three patch cases: 84 raw/84 stable exact double
representations, nine integer fields, retired sources, foreign-global negative
controls and 36 actual adaptation/smoothing factor outputs. Check three factory
fields against RuntimeConfig and the other 34 against existing process values.
Source reversal must restore the complete generator body, 13 ordered stable
writes in their three original blocks and every formula/branch/literal, with
unchanged parser/apply/defaults/other production. Analyze the two touched production
units and existing probe once each with unchanged canonical compilation commands.
Require explicit token-checked formatting, whitespace, inventory/contracts and
staged/remote gates. The initial foreign-control setup selected the discrete branch and failed its
required output difference. That failure is retained; only its mode changes to the
existing continuous branch, with production and exact oracles unchanged.

No new target, model or instrument campaign is introduced.

## Quadtree limits and saturation controls

The [quadtree lot](evidence/QUADTREE_CONTROLS_CONTEXT.md) reuses 75 CTest/385 nested
Python controls, C++17 GCC/MSVC builds, nine-state/45-artifact/123-boundary reference
and real MSVC CLI controls on exact head/main. Require prior markers plus three
quadtree cases: 27 raw/27 stable exact double representations, ten integer fields,
42 depth results, nine real face-subdivision/template-stat observations and three
value snapshots after generator retirement. Retain legacy and foreign-global
negative controls. Source reversal must preserve complete generator/Adapter/tree/
cell expression/order/literal tokens modulo settings and explicit depth inputs.
Keep the original failed build logs. Analyze each touched production translation
unit with its unchanged ap_mesh_engine compilation command once, plus the existing
native probe command; retain the initial repeated-command partial log. Formatting
of touched legacy tree files is explicit and token-checked. Require unchanged
parser/apply/defaults/other production, inventory/contracts and staged/remote gates.
No new scientific input, native target or standalone instrument campaign is added.

## Curve discretization and point budgets

The [curve lot](evidence/CURVE_CONTROLS_CONTEXT.md) reuses 75 CTest/385 nested
Python controls, C++17 GCC/MSVC builds, nine-state/45-artifact/123-boundary reference
and real MSVC CLI controls on exact head/main. Require prior markers plus three
curve cases: 33 raw/33 stable double representations, six integer fields, source
retirement, conflicting globals, intermediate/final mode updates, 18 actual point
targets and 12 owned Adapter factor observations. The independent factor pair,
point clamp order and legacy writes must remain intact. Source reversal permits
only named reads, two original updates and the point-limiter method boundary;
complete generator/Adapter formula/order/literal tokens and synchronization flow
must match. Require unchanged parser/apply/defaults/other production, scoped
analysis over the complete touched context header, explicit format/whitespace,
inventory/contracts and staged/remote gates. Retain preparation-reader corrections;
no scientific model, native target or instrument campaign is added.

## Element budget controls

The [budget lot](evidence/ELEMENT_BUDGET_CONTEXT.md) reuses 75 CTest/385 nested
Python controls, C++17 GCC/MSVC builds, nine-state/45-artifact/123-boundary reference
and real MSVC CLI controls on exact head/main. Require prior markers plus three
budget cases: 72 raw/72 stable exact double representations, eight integer fields,
source retirement, foreign-global negative controls, five local/global overrides
and 18 outputs of the actual target limiter. Stable comparisons must use the same
raw case on both paths; retain the original failed setup/source/identity. The
existing metric/scientific oracles are unchanged. Source reversal permits only
the 32 reads, five exact ordered stable assignments and explicit target bounds.
Require unchanged parser/apply/defaults/other production, scoped analysis, explicit
format/whitespace, inventory/contracts and staged/remote gates. No new model,
test target or standalone instrument campaign is required.

## Adaptation settings and effective adjustments

The [adaptation lot](evidence/ADAPTATION_CONTEXT.md) reuses the existing 75 CTest/
385 nested Python controls, C++17 GCC/MSVC builds, nine-state/45-artifact/
123-boundary reference and real MSVC CLI controls on exact head/main. Require all
prior native markers plus three adaptation cases: 12 raw and 12 stable exact
double representations, source retirement, foreign-global negative controls,
local/global override paths and 18 bit-exact outputs of the actual rate limiter.
Retain original metrics and scientific oracles. Reverse only four read bindings
and the four original stable assignments; verify unchanged per-attempt arithmetic,
clamps, order and literals, parser/apply/defaults and other production. Require
scoped analysis, explicit format/whitespace, inventory/contracts and staged/remote
gates. No new model, test target or standalone instrument campaign is required.

## Stopping/retry criteria context

The [stopping/retry lot](evidence/STOP_RETRY_CONTEXT.md) uses the existing
75 CTest entries/385 Python controls, C++17 GCC/MSVC builds, nine-state frozen
reference (45 exact artifacts/123 boundary comparisons) and real MSVC CLI controls
on exact head/main. Require prior markers plus the new native criteria marker:
three cases/27 exact double representations, copied/retired source, conflicting
globals, local effective promotion and two legacy update paths. Keep the original
metric oracle and negative controls. Source reversal permits only the named read
accessors and promotion helper at the original update point; comparisons, loop
ordering, arithmetic and diagnostic literals must match. Require unchanged parser/
apply/global defaults/other production, scoped analysis, explicit format/whitespace,
contracts/inventory and staged/remote gates. No new model or instrument campaign.

## Adaptive-policy configuration context

The [policy context lot](evidence/ADAPTIVE_POLICY_CONTEXT.md) uses the existing
75 CTest entries/385 Python controls, C++17 GCC/MSVC builds, frozen nine-state/
45-artifact/123-boundary scientific reference and real MSVC CLI controls on exact
head/main. Require prior native markers plus the policy marker: four differential
cases, 28 exact double representations, retired source, conflicting globals and
default/identity-only compatibility. The metric oracle is unchanged. Reverse only
the six generator input bindings and Adapter's explicit raw-policy argument;
require identical formula/ordering tokens, unchanged parser/apply/global defaults,
scoped analysis, explicit format/whitespace, inventory/contracts and staged/remote
checks. No new test target, scientific input or instrument campaign is required.

## Typed engine execution request

The [typed request lot](evidence/TYPED_GENERATION_REQUEST.md) reuses the existing
75 CTest entries/385 Python controls, C++17 GCC/MSVC builds, nine-state scientific
reference (45 exact artifacts/123 boundary comparisons) and real MSVC CLI controls
on exact head/main. Require the existing ownership marker and the new native
request marker (three typed and two raw-bridge reader failures, including empty
path and owned-context precedence), without changing the metric oracle. Verify
the seven historical CLI transcript values in existing scientific executions.
Source reversal permits only the named request/count/input bindings and transcript
relocation. Require scoped analysis, explicit formatting, whitespace, inventory/
contracts, staged and remote checks. No new instrument or model campaign is added.

## Owned generation identity/output

The [generation context lot](evidence/GENERATION_CONTEXT.md) uses the existing
75 CTest entries and 385 Python controls. Require the native metrics marker for
two owned identities, retired source and three interleaved outputs, plus the
unchanged metric oracle, nine-state/45-artifact/123-boundary scientific comparison,
GCC/MSVC builds and existing MSVC CLI controls on exact head/main. Check source
reversal modulo identity access substitutions, scoped analysis and all standard
format/inventory/contracts/identity/remote gates. No standalone instrument or new
scientific matrix is required; historical ASan evidence keeps its artifact scope.

## Serial engine production package

The [engine/runtime extraction](evidence/SERIAL_ENGINE.md) uses existing validation:
C++17 GCC/MSVC canonical builds, 75 CTest entries/385 nested controls, affected
real MSVC invalid/analytic CLI checks and the frozen nine-state Eistute/Book
reference (45 exact artifacts/123 boundary comparisons) on delivery head/main.
Require token/order preservation for extracted defaults/parser/application/CLI,
scoped analysis, format, inventory/contracts and source/input/remote identity.
No new test matrix or standalone instrument is required for this package. Reuse
unchanged native tests and keep historical instrument limitations explicit.

## Portable terminal observer requalification

The [qualified terminal observer](evidence/SERIAL_ASAN_TERMINAL_REQUALIFICATION.md)
requires actual external SubMesh allocation, one uncaught exception/attempt/denial,
the unchanged payload/CLI/library oracles and all five fixed contexts. Verify
/fsanitize=address, /EHsc and /we4530 on all 74 actual compiler groups. Preserve
both failed qualifications and original source/fixture/control identities.
Require exact-head/main 75 CTest entries with zero failures/skips and 385 nested
Python controls, scoped read-only analysis, formatting/whitespace, contracts/
inventory, source/input/runtime/prior-seal and remote/staged checks. Reuse the
single successful five-context measurement and unchanged nine-state GCC report
(45 exact artifacts, 123 boundary comparisons); do not rebuild or repeat native
campaigns for delivery. Earlier natural-process flags do not qualify exception
unwinding. Other instruments and Stage 3 closure remain open.

## Remaining fixed serial ASan production cases

The [SP-06..08 checkpoint](evidence/SERIAL_ASAN_REMAINING.md) reuses the qualified
73-unit artifact for exactly five fixed processes with unchanged 300-second caps.
Require source/input/runtime/application/prior-seal identity, both positive
repeatability/boundary reports, normal no-sync return and every process/log hash.
Documentation head/main must pass the existing 75 CTest entries and 380 nested
Python controls, whitespace, inventory/contracts and staged/remote checks. Reuse
the unchanged prior nine-state/45-artifact/123-boundary GCC scientific report by
identity. Do not rebuild, recalibrate instruments or repeat native production
observations for this documentation delivery. SP-09/10 portability, other
instruments and Stage 3 closure remain open.

## Allocation-free face quality

The [quality scratch correction](evidence/FACE_QUALITY_SCRATCH.md) requires paired
original/candidate GCC, MSVC/ASan and checked Debug values: 846 rows and 4,230
exact quality/public-center scalar bits per profile, preserved caller graph,
actual zero-allocation/denial calls and independent real hook detections. The
original must fail the zero-allocation contract. The legacy CRT quality scenario
requires two real calls plus its independent hook marker and zero retention;
zero-of-zero failure sweeps are not qualification. Other denial gates stay fixed.

Require exact-head/main 75 CTest entries (zero failures/skips) with 380 nested
Python controls, frozen GCC Eistute/Book nine states/45 exact artifacts/123
boundary comparisons, scoped analysis/formatting, source/input/contracts/inventory,
whitespace and staged/remote checks. Retain original timeout, diagnosis and failed
reference-path preparation. Reuse the single successful 60-second-capped ASan
SP-05 by source/tool/artifact identity; do not expand the ASan campaign or repeat
that witness for unchanged documentation. Allocation counts/timing change; no
scientific criterion, public center ownership or stage closure changes.

## First complete serial ASan witness

The [bounded P3 checkpoint](evidence/SERIAL_ASAN_SP02.md) records the actual
73-unit MSVC/ASan build, working release/expired-access controls and one natural
initial-only SP-02 process with positive independent boundary comparisons.
Documentation head/main must preserve non-documentation/source/input/runtime/
application/control identities and the prior P1/P2 seals, replay actual compiler
commands and controls/results, and pass whitespace, inventory/contracts, staged/
remote checks and existing 74 CTest/380 nested Python controls without skips.
Reuse the single native ASan observation by identity; do not rebuild the unchanged
target or repeat SP-02 for documentation. Control source snapshots are data in
the compact JSON evidence, not a new central target or application mode.
Remaining production cases, directed observer portability, CRT/LSan/UBSan and
parallel coverage stay open. An expected UAF control is detection evidence;
only an unexpected failure stops expansion. No full-process leak claim follows.

## Fixed serial execution ledger

P2's [execution ledger](architecture/SERIAL_EXECUTION_LEDGER.md) and machine case
inventory require unchanged non-documentation bytes, inputs, application hashes,
P1 scientific/instrument seals, case/recipe/source replay, whitespace,
architecture/contracts and staged/remote identity. Require the existing 74 CTest
entries with zero failures/skips and 380 nested Python controls on exact head and
main. Do not rebuild unchanged applications, rerun article/instrument campaigns,
add native targets or treat planned observations as measured for this specification.

P3 starts with complete MSVC/ASan/control qualification and one natural SP-02
case, then a first-failure stop/classification. The fixed ten groups and three
instrument profiles are not a Cartesian-product run authorization before tool
qualification. Preserve every missing full-entry/terminal-observer/UB/leak gate;
Debug success and repeated subprocesses establish neither leak accounting nor
same-Generator reuse. The finite remaining assignments do not waive Stage 3 gates.

## Complete serial MSVC C++17 build prerequisite

`windows-msvc-serial` configures/builds the real complete Debug ap_mesh target.
The [bounded build evidence](evidence/MSVC_SERIAL_CPP17_BUILD.md) requires actual
C++17/checked-iterator native observations, the existing real CLI invalid/analytic
controls, exact source reversal and GCC Eistute/Book preservation (nine states,
45 exact artifacts and 123 boundary comparisons) on delivery head and main.
`application.serial_cpp17_portability` reuses curve_orientation_probe and adds
one focused entry for the unchanged pi value, defined quadrature orders 3/4 and
typed scratch count/payload forwarding. Require 74 CTest entries with zero
failures/skips and the existing 380 nested Python controls. No production mode,
extra duplicate native target or new allocation-denial matrix is introduced.
Changed-line/new-header analysis, explicit scoped formatting, whitespace,
inventory/contracts, raw-input/source and staged/remote identity remain gates.
Original compiler/preparation failures stay retained. No MPI/OpenMP runtime,
unsupported quadrature, whole-process sanitizer or C++23 qualification follows.

## Consolidated execution policy

The current [stage audit](evidence/STAGE3_CONSOLIDATION_AUDIT.md) controls task
selection through the ten-row closure ledger and five delivery packages. This
policy changes no test inventory, assertion, scientific criterion or required
qualification scope. Existing detailed gates below still apply to their changes.

- During edits, run checks affected by the actual change. A completed identical
  revision/check is reused unless a changed dependency or unresolved failure
  justifies repetition.
- Before integration, run the required full regression on the exact delivery
  head, then on merged main. This remains required by the working agreement.
- Run a large memory/science campaign only for an invalidated dependency, a named
  required missing observation or a justified controlled response to a failure.
  Preserve original positive/negative controls and every failed attempt.
- Admit a work item with closure row, concrete output, affected gates and stop
  decision. After refusal/zero reach, classify the gap before another experiment;
  do not automatically create a successor source-audit PR.
- Report 74 CTest entries with 380 Python controls nested in tooling.controls.
  Test counts and anchor counts are inventories, not modernization progress.

For this consolidation, observe the unchanged current regression once, preserve
prior instrument/scientific reports by identity, and perform the required exact
delivery-head/main regression and documentation/inventory checks. A single full
serial MSVC compiler observation identifies actual blockers; it is not sanitizer
qualification, and failure remains a blocker for S3-09. No new native allocation
campaign, scientific model run, fixture, test target or assertion is added.

## Front-edge provenance source audit

The [cell/midpoint audit](evidence/FRONT_EDGE_CELL_MIDPOINT_PROVENANCE.md)
changes only documentation and source-fact artifacts. Require 73 existing CTest
entries and 380 Python tests on exact head/main, all 85 scoped anchors across six
files, the eight-slot map and five native order groups to replay. Verify unchanged
non-documentation tracked files, all fixtures, application identity, 66 protected
raw inputs and prior sealed source/native records. Do not repeat a custom native
campaign. Whitespace, inventory/contracts, staged-byte/metadata and fresh remote
main/branches/PR/check audits remain gates. Conditional exact-geometry bounds and
source registration alone qualify no selected-exterior witness, border retirement,
generated-base execution, exception/retry or broader scientific result.

## Selected-ideal domain source audit

The [source-only audit](evidence/SELECTED_IDEAL_DOMAIN_CONDITIONS.md) adds
documentation and hashed source facts, with no production, fixture, test-target
or contract change. Its exact-head/main gates retain 73 CTest entries and 380
Python tests, including existing negative controls. Require all 71 scoped source
anchors and their native ordering to replay, all non-documentation tracked files,
application identity and 66 raw inputs to remain unchanged, and the prior native
geometry/prefix seals and raw reports to remain immutable. Replay the existing
records without repeating a custom geometry campaign. Whitespace, inventory/
contracts, staged bytes/metadata and remote main/branches/PR/checks remain gates.
Source predicates and passing documentation gates qualify no retirement witness,
exception path, broader caller domain or scientific result.

## Normal geometry observation after the admitted prefix

The [bounded geometry observation](evidence/ANALYTIC_GEOMETRY_OBSERVATION.md)
is documentation evidence, with no new production/test target or contract.
Require the existing 73 CTest entries and 380 Python tests on exact head/main,
the 15-outcome checked-CRT prefix inventory and 16 separate normal GCC/CRT
geometry outcomes. All eight observed/unobserved pairs must agree on geometry
status, ordered views, endpoint IDs, positions, Faces and remaining queues.
Require unchanged admitted-prefix observations, reversible source insertions,
raw/executable/source hashes and scoped diagnostic-fixture/header analysis.
Fourteen report-corruption controls challenge the reader without injecting any
native failure. Zero selected new ideals and zero retirements remain a coverage
limit; empty second-pass entry does not qualify rejected-edge selection.
Preserve production, prior evidence, protected inputs and scientific policy.

## Analytic native template-prefix gate

`application.analytic_template_prefix` exercises eight analytic configurations
and one missing-curve control. Four contexts create a nonempty prefix and match
the unobserved native source; two are guard-only and three are explicit refusals.
Require 73 CTest entries and 380 Python tests, including 24 new checker/source-
preparation controls, plus the same 15-process inventory in actual checked CRT
with iterator level 2. [Scope and delivery gates](evidence/ANALYTIC_TEMPLATE_PREFIX.md)
require topology/area/ID/observer checks, actual preflight refusal, source reversal,
scoped fixture/header analysis, unchanged production/science and exact-head/main
regression. The public geometry-entry cut performs no selection or retirement.

## Geometry-phase ideal Vertex pending-owner gate

`application.ideal_vertex_ownership` calls the inherited native selector in seven
modes, two candidate orders and zero/one committed Face prefix. Complete denial
sweeps require zero pending retention, actual nonallocating production cleanup,
live borrowed vertices/adjacency/prefixes and original ID/publication timing.
Delivery requires 72 CTest entries and 356 Python tests (34 new checker/source
controls), the 6223-outcome three-profile matrix and exact head/main scientific
and tooling gates. Require 1832 original failures and matching production
cleanups, 3040 unchanged original observations, actual borrowed-best destruction,
production stale-observer omission and independent denial/leak/UAF controls.
[Scope and gates](evidence/IDEAL_VERTEX_OWNERSHIP.md) preserve sparse-front and
unreached-guard limits. Separate deliberately invalid UAF/leak units require
their own analyzer detections; neither belongs to positive-fixture analysis.

## Second new-edge pending-owner gate

`application.second_edge_ownership` calls native makeMesh/selection across 32
contexts with an existing or freshly adopted first edge. Complete second-edge
denials require live borrower/adjacency, first-edge/Face-prefix preservation,
actual cache release and zero production-cleanup allocation attempts. Delivery
requires 71 CTest entries and 322 Python tests, including 36 new checker/source-
preparation controls. The three-profile matrix requires 2663 native outcomes,
preserving 288 original failures, 96 exact normal and 992 denial comparisons.
Require actual plain-deleter/stale-adjacency controls and separate invalid UAF/
leak analyzer detections. [Scope and exact-head/main gates](evidence/SECOND_EDGE_OWNERSHIP.md)
keep earlier vertex creation/adoption, broader topology and retry unqualified.

## First new-edge pending-owner gate

`application.first_edge_ownership` checks native selection, complete first-edge
allocation denials, actual nonallocating cleanup, live endpoint/adjacency/prefix
state and original publication timing. Delivery requires 70 CTest entries and
286 Python tests, including 31 first-edge checker/preparation controls and three
marker-scope regression controls. The three-profile
matrix requires 1335 native outcomes and preserves 144 original failed contracts.
Actual plain-deleter and detach-only controls remain separate from repaired
behavior; ASan invalid reads are required for the latter in its measured profile.
[Scope and exact-head/main gates](evidence/FIRST_EDGE_OWNERSHIP.md) retain the
initial observer-span preparation failure and the second-edge/retry limitations.
Isolated retained-storage and expired-access units require actual analyzer
detections; neither belongs to the positive-fixture analysis gate.

## Three-edge shortcut Face gate

`application.shortcut_face_ownership` checks the actual public exact-three branch,
all scoped allocations, native owner/adjacency/prefix state and nonallocating
pending cleanup. The delivery requires 69 CTest entries and 252 Python tests.
Keep fewer-than-three guards separate from Face publication coverage and retain
the original failures and actual wrong-deleter detections. [Scope and gates](evidence/THREE_EDGE_FACE_OWNERSHIP.md)
require exact-head qualification and fresh main validation after merge.
The deliberately invalid retained-storage and expired-access units require their
own analyzer detections; neither belongs to the positive-fixture analysis gate.

## Geometry-phase marker ownership gate

`application.front_marker_lifetime` checks actual native geometry-front marker
creation, publication, retirement and measured downstream failures. The delivery
requires 68 CTest entries and 232 Python tests. Require original failed contracts,
nonallocating cleanup, live owner/adjacency/prefix checks and actual invalid
observer/premature-deletion detections. [Scope and exact-head/main gates](evidence/FRONT_MARKER_OWNERSHIP.md)
keep public-wrapper, later-selector and full recovery limits explicit.

## Pending Face publication gate

`application.face_adoption_ownership` checks actual native selection/publication,
live endpoint owners/adjacency, committed prefixes and failed allocation timing.
The delivery requires 67 CTest entries and 218 Python tests. Original retention,
invalid-deleter and instrument controls remain separate from repaired behavior.
[Scope and exact-head/main gates](evidence/PENDING_FRONT_FACES.md) define supported
topology/prepared geometry and preserve the initial executor expectation failure.

## Interception Face borrower gate

`application.front_face_borrowers` adds the native local borrower contract.
The delivery requires 66 CTest entries and 206 Python tests. Require every
calibrated denial, actual adjacency and consuming live callers, original failed
contracts, exact normal cache/release traces and independent instruments.
[Scope and exact-head/main gates](evidence/FRONT_FACE_BORROWERS.md) preserve the
deliberately invalid control and distinguish guard-only cases from coverage.

## Angular selection ownership gate

`application.front_angle_ownership` calls actual native angular selection in five
nonempty layouts and denies every calibrated temporary allocation. Original and
repaired instrument campaigns, numerical/order comparison, negative controls,
exact-head scientific requirements and coverage limits are defined in
[the bounded evidence](evidence/FRONT_ANGLE_TEMPORARIES.md). Preserve each CTest
invocation in its own evidence subdirectory; never replace earlier failures.
Stage 3 remains open.

## Actual accepted steps in final serial reports

The report-identity repair keeps 64 CTest entries and adds ten checker tests
(182 Python tests). `tests/final_report_case.py` requires actual accepted IDs,
nonempty exact field coverage, finite values and unchanged serialized scalars.
Challenge original ordinal labels, missing/duplicate/unordered ledgers and rows,
scalar drift and CRLF/LF input. Actual caller gates separately cover production
articles, archived/unarchived gaps and consecutive acceptance, an uninjected
initial plane, and two corrupt-ledger copies. The missing ledger must fail rather
than print a fabricated ID; duplicate IDs must be detected by the report checker.
See [delivery gates](evidence/ACCEPTED_STEP_REPORTING.md). Controlled acceptance
and corruption cases are separate from scientific results and memory guarantees.

## Accepted errors at serial stopping guards

The serial loop-entry repair keeps the existing 64 CTest entries and adds eight
trace-checker controls (172 Python tests). `tests/stopping_error_case.py` checks
actual caller accepted-history/local-error provenance, continuation or convergence,
global-first equality, terminal labels and complete nonempty observations.
Complete-caller qualification separately exercises rejected scalar boundary
controls, accepted-error controls, initial empty data, archived/unarchived later
acceptance and growth rejection. Synthetic branch/state controls are not solver-
produced convergence or scientific quality results. Require original failures,
exact frozen science, source preservation, caller analysis and exact-head/main
gates in [the repair evidence](evidence/ACCEPTED_ERROR_STOPPING.md).

## Explicit accepted mesh root

GNU serial adds `application.accepted_mesh_root` (64 CTest entries).
Twenty-two scope cases cover archived/unarchived owners, normal rejection/commit,
failure before/during/after construction, foreign/null observers, allocation
denial, consecutive rejections, retries and acceptance after rejection. Require
native release-control detection. Eight checker controls bring Python tooling to
164. Complete caller checks separately cover CLI h/m/q, an unarchived library
entry, controlled accept/reject sequences, original accepted-root rejection and
real unarchived terminal cleanup. Empty/unsupported CLI modes remain invalid;
those preparation failures are not numerical validation. Require full source/
header tooling and exact-head/main scientific/identity gates described in
[the repair evidence](evidence/ACCEPTED_MESH_ROOT.md); later rejected candidates
change and original strict equality must not be reported as passing.

## Selected candidate structural snapshots

GNU serial adds `application.candidate_snapshots` (63 CTest entries).
Forty actual caller cases require independent/reused-cache selection, paired
scalar/region exports, sequential replacement, epsilon/dense-curve fallback,
missing statistics and native owner cleanup when long-status copying fails.
Eight checker controls bring Python tooling to 156. Existing thirty-two ownership
cases now require improved repair selection even with a reused slot; original
alias rejection is retained as negative evidence. Require original, alias-first
and export-cache mutation rejection, full caller/fixture/header analysis and
source-preservation checks. Article gates preserve meshes/boundaries/decisions
while independently explaining the four changed artifacts and six derived-value
differences; the original strict comparison still fails and is not relabeled.
See [delivery scope](evidence/CANDIDATE_STRUCTURAL_SNAPSHOTS.md).

## Typed serial terminal domain failure

GNU serial builds add `application.typed_domain_failure` (62 CTest entries).
`tests/typed_domain_failure_case.py` requires nine payload/identity/move-lifetime
cases, a working allocation-during-unwind denial control, two real library
false-result paths and three actual CLI paths (Book patch 0, Eistute patches
0/1). Require unchanged attempt counts, context, one diagnostic, status 1,
cleared owned links/samples and no additional global operator-new attempt during
unwinding. Failed CLI prefixes must be rejected by the generation verifier.
Eight checker controls bring Python tooling to 148. Original exit must fail all
five integration cases; the prior generic catch must be rejected independently
with the real CLI observer. Require full Adapter/main/fixture and test-header
tidy, explicit canonical formatting with source preservation, inventory/staged
gates and fresh exact-head/main article comparison. See [scope and limitations](evidence/TYPED_DOMAIN_FAILURE.md).

## Serial domain failure observers

GNU serial builds add `application.domain_observer_cleanup` (61 CTest entries).
`tests/domain_observer_case.py` requires twelve nonempty active/retained/mixed
owner layouts, both traversal orders, duplicate/null/foreign observations,
repeated cleanup and identical rethrow under operator-new denial, plus a working
native allocation hook. Actual Book patch-0 and Eistute patch-1 AFT failures
require all owned links null at the external catch and after owner destruction,
empty curve lists, identical exception object and zero additional C++ allocation
attempts. Inactive test modes delegate to production. Eight checker controls
bring Python tooling to 140. Require rejection of the original Generator, the
immutable terminal-audit observer, full caller/consumer and test-header tidy,
format/inventory/staged gates and fresh exact-head/main article comparisons.
Scope is GNU serial; see [remaining limits](evidence/DOMAIN_FAILURE_OBSERVERS.md).

## Serial domain candidate ownership

GNU serial builds add `application.domain_candidate_contracts` (60 CTest entries).
`attempt_metrics_probe` links explicit Adapter/stat/insertion/allocation/release
wrappers; inactive modes delegate to production. `DomainCandidateFixture` is a
friend fixture that seeds private state without a public runtime control API.
The actual caller and native SubMesh/nodes/triangles execute 32 cases: three
branches, keep/discard, normal/before/during/after/failed-adoption paths, plus two
native-style aliased-stat cases. `tests/domain_candidate_case.py` requires the
complete ordered matrix and an actual suppressed-release detection. Eight
corruption tests plus four extraction controls bring Python tooling to 132. The
serial evaluator extractor accepts the exact original or wrapped return-type
signature and rejects missing/ambiguous boundaries. Require actual Eistute step-4
937-node/1796-triangle release observations and fresh exact-head/main article
comparison, full caller/fixture tidy, explicit full-file format with lexical
preservation, whitespace, inventory and staged gates. Qualification is GNU
serial exact-address observation; no new ASan/CRT or memory-slice claim follows.
See [scope and limits](evidence/DOMAIN_CANDIDATE_OWNERSHIP.md).

## Serial temporary UV cache ownership

`application.domain_uv_cache_contracts` adds one gate (59 total GNU serial CTest
entries). `tests/domain_cache_memory` compiles fourteen actual native units with
C++17; use `AP_MESH_CACHE_SOURCE_ROOT` and optional `AP_MESH_CACHE_ASAN` for isolated
MSVC builds. Debug uses CRT heap checkpoints with `_ITERATOR_DEBUG_LEVEL=0`;
ASan and CRT independently calibrate their real allocation counts.
`tools/qualify_domain_uv_cache.py --asan <exe> --crt <exe> --runtime <directory>
--output <fresh-directory>` requires twelve expected outcomes: contracts, live/
original-live and hook controls per instrument, actual ASan UAF, actual CRT leak
and two original retention failures. Ten checker corruption tests bring Python
tooling to 120 tests. Require full adapter/fixture tidy and format, inventory,
unchanged scientific inputs, actual Book exception release observations and
fresh exact-head/main article regression. This is bounded cache qualification;
see [remaining lifecycle limits](evidence/DOMAIN_UV_CACHE.md).

## Serial terminal domain-failure status

GNU serial builds add `application.domain_failure_status` (58 CTest entries).
The existing actual-production `attempt_metrics_probe` links an AFT wrapper;
only its new explicit failure mode forces step 2, patch 0 to return false.
`tests/domain_failure_case.py` retains Book's one call and Eistute's existing
two attempts, requires exact status 1 and terminal context, and rejects success,
crashes or unrelated errors. Four status-oracle controls bring Python tooling
to 110 tests. This test-only GNU ABI mechanism is not enabled for other compilers,
MPI or OpenMP; no corresponding qualification is claimed. Required delivery
checks include full adapter/fixture tidy, changed-line format, fresh exact-head/
main article comparisons and existing local gates. Original cleanup failures
remain unqualified in [the evidence](evidence/DOMAIN_FAILURE_STATUS.md).

## Physical and UV-quality report verification

`tools/verify_generation.py <run> --require-boundary-coverage --report <report>`
checks five physical-quality CSV fields against validated, full-precision XYZ
incidence snapshots: minimum/mean 2r/R and percentages below 0.30, at least 0.60
and at least 0.80. It also checks all ten UV-quality fields: minimum, 5th/50th/
95th percentiles, maximum, mean, sample standard deviation and the same three
percentages. UV percentiles use linear positions p*(n-1); single-sample deviation
is zero. Native binary64-epsilon zero-sentinel guards are outside the independent
nondegenerate UV metric qualification and fail verification without modifying
the mesh. Reports include exact triangle counts per threshold and poor
counts per patch. The CSV uses percentages, not fractions. Six-significant-digit
serialization is accounted for separately from the 1e-10 arithmetic comparison
budget. A triangle within that arithmetic budget of a threshold leaves its count
unqualified and fails verification; this does not change mesh acceptance.
Without snapshots, legacy OBJ/log checks remain available but full-precision
physical/UV quality coverage is explicitly unavailable. Required strict boundary
verification requires snapshots and includes both quality checks.
Physical controls and twelve UV analytic/corruption controls plus integration
bring the tooling total to 106 tests. The UV distributions distinguish sample
from population deviation, interpolated from nearest-rank percentiles, and UV
from XYZ shape. Reuse retained article output for verifier-only changes.
See [evidence and limits](evidence/PHYSICAL_QUALITY_ORACLE.md).

## Hermite constructor rollback

application.hermite_construction_contracts and tooling.hermite_construction_preservation
retain the prior 53 CTest entries (55 total). tests/hermite_construction_memory
builds actual production with AP_MESH_HERMITE_CONSTRUCTION_SOURCE_ROOT and optional
AP_MESH_HERMITE_CONSTRUCTION_ASAN. tools/qualify_hermite_construction.py requires
--asan, --crt, --runtime and a fresh --output directory. Require all 82 expected
outcomes, original CRT rejection, eight constructor preservation mutations and
the existing retirement/copy mutations. Live numerical pairs and prior regression
remain required for delivery. See evidence/STAGE3_HERMITE_CONSTRUCTION.md.


## Completed Hermite observer retirement (PR #98)

The required application.hermite_observer_contracts and
tooling.hermite_observer_preservation add two gates, retaining the earlier 51.
The isolated actual-production C++17 probe requires 153 ASan/static CRT outcomes,
22 denial-enabled nonallocating operations, working UAF/leak/hook and independent
prefix/order corruption controls. Eight source mutations must be rejected.
Six nonempty original/candidate live trace pairs per GCC/MSVC instrument compare
all seven point/derivative vectors and incidence. Prior batteries and exact-head/
main regression remain required. Exact implementation head/main pass all 150
commands, 53/53 CTest, 74 Python controls, 32 batteries/3310 expected outcomes,
1040 scalar sequences and exact repeated article traces on the same 618 inputs.
The documentation closure repeats applicable exact-head/main gates without
changing those inputs; no cross-build binary equality is assumed. See
[scope and commands](evidence/STAGE3_HERMITE_OBSERVERS.md).

## Original Hermite observer retirement audit

The standalone [recipe and runner](evidence/STAGE3_HERMITE_OBSERVER_AUDIT.md)
compile seventeen actual production units in explicit GCC/MSVC C++17 builds.
Require all 83 original expectations, including nine actual expired-observer
ASan failures, independent UAF/leak/oracle controls, stable cleanup reference
observations and the 25-construction literal inventory. This is reproduction,
not a new qualified memory battery. Preserve all 613 protected inputs and
51 CTest/74 Python controls; repeat applicable exact audit head/main gates.

## Initialized detached patch-copy repair

The new application.detached_patch_copy_contracts and
tooling.detached_patch_copy_preservation retain all prior 49 tests (51 total).
The actual sixteen-unit probe requires 95 ASan/static CRT outcomes, twelve
nonallocation observations, working instrument/oracle controls and 105 live
C++17 original/candidate pairs. Eight preservation mutations are rejected.
Earlier constructor/observer guards retain their four/six controls and normalize
only the exact separately checked copy prefix. Full exact-head/main gates remain
required; see [evidence and limits](evidence/STAGE3_DETACHED_PATCH_COPY.md).

## Pointer-taking patch-copy audit (C22)

The standalone [C22 recipe and runner](evidence/STAGE3_PATCH_COPY_AUDIT.md)
compile sixteen actual production units in explicit GCC/MSVC C++17 builds.
Require 110 original observations: 108 defined cases, an actual ASan UAF control
and a positive CRT leak control; retain all failures and indeterminate-field
limits. This adds no repaired battery or CTest. The 49 CTest/74 Python inventory,
608 protected inputs and exact audit head/main local/remote gates remain required.

## Model ownership repair

Required application.model_ownership_contracts and tooling.model_ownership_preservation
add two gates to the previous 47-test inventory. tests/model_memory compiles
Model and fourteen actual dependency units. tools/qualify_model_ownership.py
requires 57 expected ASan/static Debug CRT outcomes, eight complete allocation
sweeps, twelve nonallocating operations and real UAF/leak/hook/order/adjacency
controls. tools/compare_model_ownership.py requires five nonempty live pairs per
compiler/instrument against a Git-verified original. The preservation guard
rejects six independent mutations. Full exact-head/main prior regression,
accepted/rejected traces and remote audits remain required; see
[evidence and commands](evidence/STAGE3_MODEL_OWNERSHIP.md).

## Original Model ownership reproduction

The standalone [Model audit](evidence/STAGE3_MODEL_ROOT_AUDIT.md) compiles fifteen
actual production units plus the probe in separate MSVC ASan/static Debug CRT
builds. Its driver requires thirteen original reproduction outcomes, including
working normal/leak/UAF/hook controls, four copy/rvalue errors, two failed-append
retention cases with independent caller-cleanup controls, and unsupported duplicate
adoption. Driver success is reproduction evidence, not repaired-model validation.
No production input or existing test inventory changes. The 47 CTest/74 Python
controls and source-equivalence/local/remote gates remain required on exact
audit head and main. See the audit for commands and explicit limits.

## Serial-reader control ownership (PR #89)

The new required application.serial_reader_contracts and
tooling.serial_reader_preservation complement the existing 45 tests. The actual
full-reader probe requires 131 ASan/static CRT outcomes and sixteen complete
allocation-denial sweeps, with actual UAF/leak/hook/prefix controls and eight
rejected input classes. tools/audit_serial_reader.py rejects six independent
mutations and preserves all other parser/header/validation tokens. Eight GCC and
sixteen MSVC nonempty live pairs preserve controls, IDs, incidence/directions and
evaluated scalar bits. Full implementation exact-head/main gates pass: 47 CTest,
74 Python controls, 29 memory batteries/3005 expected outcomes and exact repeated
article traces. No whole-reader rollback/retry or full-process claim follows.
See [commands and original failures](evidence/STAGE3_SERIAL_READER.md).

## Original caller-root reproduction

[The caller-root audit](evidence/STAGE3_CALLER_ROOT_AUDIT.md) includes a standalone
Debug CRT recipe compiling the actual complete serial reader and fifteen other
production units. Its six original scenarios require two zero-retention controls,
one detected deliberate leak and three nonzero original reader defect outcomes.
The driver verifies reproduction, not a repaired loader. It is not part of the
28 qualified repair batteries and does not establish allocation-failure, malformed
input, ASan, whole-process or parallel safety. Existing 45 CTest/74 Python controls
and all prior exact-head/main gates remain required for future repairs.

## Completed Bezier observer retirement (PR #86)

The repair adds required application.bezier_observer_contracts and
tooling.bezier_observer_preservation. Normal contracts include 576 retirement
observations and five Geometry destruction/move/self-move scenarios. The isolated
tools/qualify_bezier_observers.py requires 126 expected outcomes, 19 measured
zero-allocation operations and real UAF/leak/hook and prefix-corruption controls.
tools/compare_bezier_observers.py requires six nonempty actual trace pairs per
compiler/instrument; tools/audit_bezier_observers.py rejects six independent
mutations and protects every other production token. The previous constructor
audit still rejects its four mutations, allowing only the exact separately
checked retirement destructor. No required gate is relaxed. The full prepublication
campaign passes with 45 CTest, 74 Python controls, 28 batteries/2874 expected
outcomes and exact repeated article traces on 598 protected inputs. Exact
published-head qualification passes all 107 commands. Implementation main passed
106 local commands before a retained terminal API timeout; a separate explicit
continuation completes the remote tree/branch/PR/check, environment and exact
checkout gates. All 598 protected inputs remain unchanged. The original failed
report remains failed and hash-linked; no completed numerical/instrument battery
was rerun to recover the network-only failure. Commands and scope are in
[the observer evidence](evidence/STAGE3_BEZIER_OBSERVERS.md).

## Bezier construction lifetime (PR #84)

Stage 3 slice 31 adds application.bezier_construction_contracts.
tools/qualify_bezier_construction.py requires 71 expected outcomes, 32 complete
allocation sweeps/348 actual denials and actual UAF/leak/denial/prefix controls.
tools/compare_bezier_construction.py requires 16 actual GCC pairs (512 constructors
per executable, 13824 scalar and 8192 control-coordinate/ID observations);
32 MSVC normal trace pairs also agree. tools/audit_bezier_construction.py preserves
public layout, complete numerical tokens, scope and charge caller semantics and
rejects four independent mutations. Original 32 failed partial sweeps/208 denials
and 39 other expected outcomes remain retained. Exact-head/main gates pass:
43 CTest, 74 Python controls, zero skips and 27 batteries/2748 expected outcomes.
Normal construction keeps external curve ownership; borrowed live curves and
exclusive suffix publication are preconditions. Successful caller adoption,
ordinary deregistration and full-process/parallel qualification remain open.
See [commands and scope](evidence/STAGE3_BEZIER_CONSTRUCTION.md).

## Automatic curvature samples (PR #82)

Stage 3 slice 30 adds application.curvature_sample_contracts.
tools/qualify_curvature_sample.py requires 725 outcomes, 330 sampled forward/inverse
exception positions, 342 zero-allocation operations and actual UAF/leak/denial
controls. tools/compare_curvature_sample.py requires 90 actual GCC paired traces;
tools/audit_curvature_sample.py preserves all numerical tokens and rejects four
mutations. The original MSVC VLA-extent adapter is explicit; GCC retains the old
VLA. Original 367 failures and initial probe findings remain retained. Exact-head/
main full gates pass: 42 CTest, 74 Python controls, zero skips and all previous
batteries plus the new one (26/2677 outcomes). Caller-level boundaries, valid
fixtures and bounded lifetime only; other helper/callback/internal-solver paths
and full-process/parallel/LSan/UBSan remain open. See
[commands and scope](evidence/STAGE3_CURVATURE_SAMPLE.md).

## Charge input ownership (PR #80)

Stage 3 slice 29 adds application.charge_input_contracts and
application.charge_input_real_numbers. tools/qualify_charge_input.py requires
189 expected outcomes, twenty complete sweeps/2787 allocation denials,
live owned observer prefixes and real UAF/leak/hook controls. The Debug target
explicitly uses the independently challenged static CRT; failed DLL/reader/link
preflights remain retained. tools/compare_charge_input.py requires 24 controlled
and 24 actual-helper nonempty paired traces with exact controls/IDs, scalar bits,
incidence, stable order and normal writer bytes. Full exact-head/main CTest is
41/41 with 74 Python controls, zero skips and all 1952 memory outcomes. This is
bounded ownership, not helper scratch, malformed-input, partial-output or whole-
process qualification. See [commands and limits](evidence/STAGE3_CHARGE_INPUT.md).

## Temporary area mesh ownership (PR #78)

Stage 3 slice 28 adds application.triangle_area_contracts and
application.triangle_area_real_error with tools/qualify_triangle_area.py. Separate
controlled/actual-error targets require 311/31 outcomes, 56 complete allocation
sweeps/30942 denials, 280 exact paired results/448 evaluation steps, 84 actual-
error paired results and independent analytic areas. Negative controls and all
original failures remain preserved. Use --kind real for actual-error integration.
Full exact-head/main qualification passes for bounded serial lifetime; stage 3
and full-process/parallel memory remain open. See [commands and limits](evidence/STAGE3_TRIANGLE_AREA.md).

## Temporary error evaluator (PR #76)

Stage 3 slice 27 adds application.error_estimate_contracts and
tools/qualify_error_estimate.py. Actual caller/class/dependency units plus exact
constructor/serial ErrorGlobal extraction require 48 outcomes, fifteen complete
allocation sweeps/156062 denials and 270 paired policy decisions with exact
curvature-bit traces. All ordinal intervals retain the 30-second limit. Original
30 CRT retention failures and preliminary compiler/lint/timeout findings remain
recorded. Full exact-head/main gates pass for the bounded serial scope; area
orchestration and full-process/parallel memory remain open. See
[commands and limits](evidence/STAGE3_ERROR_ESTIMATE.md).

## Temporary triangle counting (PR #74)

Stage 3 slice 26 adds application.triangle_count_contracts and
tools/qualify_triangle_count.py. The actual-helper ASan/CRT runner requires 159
outcomes, 42 full allocation sweeps/9014 denials, exact borrowed point/parameter/
adjacency list-node restoration, preceding physical graph traversal, repeated
calls and existing invalid-degree guards. The original calibrations themselves
leak; per-denial live deltas independently measure exceptional cleanup. Thirty
original sweeps stop at a live mismatch; twelve complete exception sweeps still
retain their successful calibration mesh. No original limit is relabeled green.
Full exact-head/main gates pass; area/error wrappers and full-process memory
remain separate. See [commands and limits](evidence/STAGE3_TRIANGLE_COUNT.md).

## Estimator construction (PR #72)

Stage 3 slice 25 adds application.estimate_mesh_contracts and
tools/qualify_estimate_mesh.py. Separate actual-helper ASan/CRT builds require
77 outcomes, 24 complete allocation sweeps/5128 denials, 0/-1/INT_MIN guards
and real memory/hook controls. A GCC scalar adapter extracts actual induction
headers/guard prefix and requires 1040 bitwise-equal nonempty sequences at 520
degrees, plus a rejected index/degree recomputation control. Caller root lifetime,
complete non-power-of-two/extreme meshes and full-process memory remain outside
scope. Earlier floating-loop lint errors are repaired without suppression;
exact-head/main gates pass. See [commands and limits](evidence/STAGE3_ESTIMATE_MESH.md).

## Completed triangle lifetime (PR #70)

Stage 3 slice 24 adds application.triangle_lifetime_contracts and
tools/qualify_triangle_lifetime.py. The six-actual-unit ASan/Debug CRT runner
requires 36 outcomes: exact current-vertex observer cleanup, virtual/derived/
repeated/replaced/default lifetime, eight nonallocating destruction paths, four
positive raw/owning adoption denials and real memory/hook controls. The earlier
31-case element-adoption failure oracle now requires an exact live prefix; its
historical terminal-only negative reports are retained with their original scope.
Full exact-head/main gates pass; borrowed nodes must outlive destruction. See
[commands and limits](evidence/STAGE3_TRIANGLE_LIFETIME.md).

## Triangle identity and observer replacement (PR #68)

Stage 3 slice 23 adds application.triangle_observer_contracts and
tools/qualify_triangle_observer.py. The five-actual-unit ASan/Debug CRT runner
requires 35 outcomes: first-match distinct/repeated/merged vertex transfers,
unchanged cache/ID/UV/list-node state, identity/default/missing/null guards,
eight measured zero-allocation operations and real UAF/leak/hook controls.
Full exact-head/main gates pass. Destruction and geometry-cache refresh remain
separate; see [commands and limits](evidence/STAGE3_TRIANGLE_OBSERVER.md).

## Registered Patch/SubMesh retirement

P4 extends the existing SubMesh lifetime runner with three observations for
registered observer retirement: 31 outcomes on seven actual units. Both owner
orders, history/list removal, rebind/moves and a measured zero-allocation check
are included. The existing metrics probe also exercises the real external-
Geometry and Execute-local-Geometry normal callers on the unchanged reader
fixture. Exact-head/main scientific and existing negative controls remain
required. [Scope and commands](evidence/PATCH_SUBMESH_RETIREMENT.md).

## SubMesh lifetime ordering (PR #66)

Stage 3 slice 22 adds application.submesh_lifetime_contracts and
tools/qualify_submesh_lifetime.py. The six-actual-unit ASan/Debug CRT runner
requires 28 outcomes: eight graph layouts, eight measured zero-allocation
operations, a borrowed-node destructor read and real UAF/leak/hook controls.
Full exact-head/main gates pass. Ordinary triangle deregistration and full-
process memory remain separate; see [commands and limits](evidence/STAGE3_SUBMESH_LIFETIME.md).

## Triangle construction boundary (PR #64)

Stage 3 slice 21 adds application.triangle_construction_contracts and
tools/qualify_triangle_construction.py. The actual-unit ASan/Debug CRT runner
requires 39 outcomes, twelve complete sweeps/48 allocation denials, exact old
list-node/scalar identity and live-observer/fresh-construction checks only after
restoration. Repeated vertices are lifecycle guards, not geometric validity.
Ordinary destruction/adoption failure and full CLI retry remain separate.
Full exact-head/main delivery gates pass; stage 3 remains open. See [commands and limits](evidence/STAGE3_TRIANGLE_CONSTRUCTION.md).

## Element adoption boundary (PR #62)

Stage 3 slice 20 adds application.element_adoption_contracts and
tools/qualify_element_adoption.py. Separate actual-unit MSVC ASan/CRT builds
require 31 outcomes: raw/owning nonnull/null cases, eight complete positive
allocation sweeps, four measured spare-storage paths and real UAF/leak/hook
controls. Fixture owners unwind before terminal failure handling; no expired
argument observer is consumed and no graph-reuse/rollback claim is made.
Full exact-head/main delivery gates pass; stage 3 stays open. See [commands and limits](evidence/STAGE3_ELEMENT_ADOPTION.md).

## Mesh adoption boundary (PR #60)

Stage 3 slice 19 adds application.mesh_adoption_contracts and
tools/qualify_mesh_adoption.py. The runner requires 36 outcomes: actual graph
identity/adjacency/area/destruction checks, six full positive growth sweeps,
five nonallocating paths and deliberate ASan UAF/CRT leak/hook controls.
Configure tests/mesh_memory in separate MSVC ASan/Debug CRT directories; use
AP_MESH_ADOPTION_SOURCE_ROOT for a Git-verified original source snapshot.
Full exact-head/main delivery gates pass; stage 3 remains open. See [commands and limits](evidence/STAGE3_MESH_ADOPTION.md).

## Initial-mesh ownership boundary (PR #58)

Stage 3 slice 18 adds application.initial_mesh_contracts and
tools/qualify_initial_mesh.py. The runner requires 27 outcomes, including eight
full observed allocation sweeps (400 denials), actual analytic/ordered mesh
checks and deliberate ASan UAF/CRT leak/hook controls. The actual constructor
unit and prior sample lifetime owner are instrumented together; full CLI failure
injection and general mesh adoption remain outside scope. Full exact-head/main delivery gates
pass; stage 3 remains open. See [scope and commands](evidence/STAGE3_INITIAL_MESH.md).

## Serial sample lifetime boundary (PR #56)

Stage 3 slice 17 adds application.curve_sample_lifetime_contracts and
tools/qualify_curve_sample_lifetime.py. The bounded ASan/Debug CRT runner requires
53 outcomes, including actual heap denial, zero-allocation teardown on populated
graphs, inner graph unwinding and deliberate UAF/leak/hook controls. The scoped
owner supplies terminal resource cleanup, not metadata recovery. Full exact-head
and implementation-main qualification pass; the whole stage remains open. See
[scope and commands](evidence/STAGE3_CURVE_SAMPLE_LIFETIME.md).

## Purpose and current limits

These commands automate repeatable checks; they do not certify the full
application. Stages 1 and 2 are integrated and closed for their measured scope.
Stage 3 slices 1-31 are integrated with qualified node, UV, curve collection,
initialized curve copy, Geometry adoption, clone publication and point-graph
snapshot restoration, paired target rebuild, serial adapter construction and
per-curve Generator sample-publication, complete sample-graph and terminal
sample-lifetime, serial initial-construction and physical mesh and terminal element adoption and failed-constructor registration and SubMesh owner-ordering and triangle identity/replacement/completed-lifetime and estimator-construction and scoped triangle-count targets.
Later slices add temporary error/area mesh ownership, charge inputs, automatic
curvature samples and Bezier construction failure lifetime. The last integrated
CTest passes 43/43 with zero skips and 74 Python controls,
including real invalid inputs, orientation, metric schema, independent verifier
negative controls, architecture freshness and actual analyzer scope controls.
Exact Eistute/Book repetition and shared-incidence regression pass. Earlier
orientation/schema/lint failures are repaired and retained as historical
evidence in `evidence/STAGE1_CLOSURE.md`. They are not current failing gates.
Selected lint scopes pass unchanged diagnostic rules; legacy warning/style debt,
full-application memory qualification and broad portability remain open.


Requirements: Python >=3.10, Git, CMake >=3.21 and Ninja for presets. The imported
code still targets C++17. GCC/Clang/MSVC qualification and C++23 migration are
stage 4. LLVM format/tidy and Doxygen are development tools, not runtime libs.
Record actual versions in each validation report; formatter-version changes
require a separate reviewed formatting change.

```sh
python tools/quality.py doctor
cmake --preset local-serial
cmake --build --preset local-serial --parallel 2
ctest --preset local-serial
python tools/quality.py test
```

Use a terminal with the intended compiler, Ninja and LLVM tools on PATH.
On Windows, an MSYS2 UCRT64 GCC terminal is one qualified bootstrap path; do
not silently switch compilers in an existing build directory.

## Reproduce the qualified Windows C++17 configuration

The delivery convenience preset `windows-gcc17` and `build/local-env.ps1` are
local ignored files. The equivalent explicit configuration below does not depend
on either file. Use a separate build directory if another compiler already owns
the cache. The recorded toolchain is native Windows UCRT64 GCC 16.1.0,
CMake/CTest 4.4.3, Ninja 1.13.2 and LLVM format/tidy 22.1.8. This retains the
historical GNU C++17 extensions; it is not complete stage 4 qualification.

```powershell
$env:PATH = 'C:\Program Files\CMake\bin;C:\msys64\ucrt64\bin;' + $env:PATH
cmake -S . -B build/windows-gcc17 -G Ninja `
  -DCMAKE_CXX_COMPILER=C:/msys64/ucrt64/bin/c++.exe `
  -DCMAKE_MAKE_PROGRAM=C:/msys64/ucrt64/bin/ninja.exe `
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON `
  -DCMAKE_CXX_STANDARD=17 -DCMAKE_CXX_STANDARD_REQUIRED=ON `
  -DAP_MESH_USE_OPENMP=OFF -DAP_MESH_USE_MPI=OFF -DAP_MESH_ENABLE_LTO=OFF `
  -DAP_MESH_ENABLE_WARNINGS=ON -DAP_MESH_DISABLE_STRICT_ALIASING=ON `
  -DAP_MESH_STATIC_MINGW_RUNTIME=ON -DBUILD_TESTING=ON
cmake --build build/windows-gcc17 --parallel 2
ctest --test-dir build/windows-gcc17 --output-on-failure --no-tests=error
```

MSVC ASan/Debug CRT probes use separate Visual Studio build directories as
documented in the bounded evidence. Do not configure their caches with GCC or
treat the production Release contracts as an instrumented memory campaign.

## Whitespace and formatting

EditorConfig defines spaces, UTF-8 and LF, with batch-file line endings handled
by editors. The whitespace command is for selected supported first-party text
files. It preserves Markdown hard breaks, rejects binary content and normalizes
selected text to LF. Do not select historical batch files for that operation.

```sh
python tools/quality.py whitespace tools/quality.py docs/PROJECT_STATE.md
python tools/quality.py whitespace --fix tools/quality.py
python tools/quality.py format src/data/mesh/sub_mesh.cpp
python tools/quality.py format --fix src/data/mesh/sub_mesh.cpp
python tools/quality.py format --base main
```

Without --fix, files are never rewritten. Explicit missing/outside/vendor inputs,
empty selections, missing tools and command failures fail the check. Changed
selection covers tracked working-tree differences against --base; untracked
files must be selected explicitly or staged. The hook checks INDEX bytes so
unstaged fixes cannot conceal a bad staged version.

clang-format uses a repository file, preserves include order and avoids comment
reflow to reduce the initial diff. Adoption is batch-wise; the whole historical
tree is not reformatted during bootstrap.

## Static analysis

```sh
python tools/quality.py tidy src/data/mesh/sub_mesh.cpp --build build/local-serial
```

Select compiled translation units. Headers are analyzed through consumers.
The command requires a nonempty first-party compilation database and applies
clang-analyzer, selected bugprone, modernize and performance checks. Diagnostics
fail the selected scope. No --fix mode exists for tidy; ownership, overrides,
renames, noexcept, const and container changes require reviewed evidence.
Do not use automatic global fixes or add NOLINT merely to silence findings.

The vendor header exclusion also applies to lexical include/../../libs paths
that otherwise match the first-party header filter. Checks and warnings-as-errors
remain unchanged. Required CTest tooling.tidy_header_scope invokes the actual
analyzer with a vendor positive control and first-party header/source negative
controls. Missing clang-tidy or lost first-party diagnostics fails the test.
LLVM 22.1.8 is qualified; other versions must support ExcludeHeaderFilterRegex.
Selected exporter lint coverage is not a full legacy lint-clean claim.


## Architecture inventory freshness

```sh
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
```

The deterministic lexical inventory covers every first-party production C++
file and hashes the CMake inputs. Eight positive/negative controls, including
retained-inventory freshness, run through normal tooling CTest. The source
anchor checker establishes traceability only; ownership conclusions require
human code review and dynamic safety requires qualified instruments. Conditional
includes are potential dependencies, not active-preprocessor or runtime proof.
Regenerate explicitly without --check only after reviewing actual source changes.

## Optional local pre-commit hook

```sh
git config core.hooksPath .githooks
```

The opt-in hook checks supported staged first-party text and clang-format for
staged C++. It never modifies files, installs packages or calls a network service.
It is a fast guard, not a substitute for build, tests or scientific regression.

## Architecture and numerical rules

Prefer RAII, explicit ownership, const-correct interfaces, value types and narrow
responsibilities. Use unique_ptr for exclusive dynamic ownership and borrowed
references/pointers for observers with documented lifetime. Avoid speculative
shared_ptr, global mutable configuration, unchecked indexing, C-style casts,
VLAs and duplicated formulas with different undocumented conventions.

Do not infer topological identity from floating-point proximity. Do not change
tolerances, accumulation order, solver policy or enable fast-math under the label
of formatting. Benchmark only after clock qualification and compare equivalent
accepted results. A lint pass does not validate numerical stability or topology.

## Memory and documentation

After portability repairs, qualify GCC/Clang ASan+UBSan, Linux LSan and platform
equivalents, including negative controls and repeated rejection/rebuild paths.
Windows ASan alone does not establish Linux leak coverage. Never claim memory
safety beyond the cases and instruments run.

Stage 3 adds a standalone physical node/submesh/triangle target under
`tests/memory`, also registered in normal CTest as application.node_lifetime.
MSVC ASan and separate Debug CRT builds are qualified by
`tools/qualify_node_lifetime.py`, including deliberately invalid controls. The
runner rejects absent diagnostics and nonzero valid-case exits. Commands and
scope limits: [node lifetime evidence](evidence/STAGE3_NODE_LIFETIME.md).

Slice 2 adds `tests/uv_memory` and required CTest application.uv_lifetime,
compiling 14 actual production units. `tools/qualify_uv_lifetime.py` requires
the original 26 ASan/Debug CRT cases, including invalid access/leak controls,
pending-template cleanup, ordered ownership transfer, midpoint aliases and
allocation-denied teardown/transfer preparation. The same runner fails the
pinned original. The bounded results do not qualify arbitrary allocation failure,
every template pattern or the full application. Commands and exact-head closure
requirements: [UV lifetime evidence](evidence/STAGE3_UV_LIFETIME.md).

Slice 3 extends the same runner to 35 cases and adds required CTest
application.uv_primitive_contracts (12 total CTest entries). It measures every
observed allocation ordinal in Edge construction, both Face constructors,
default front construction and Edge/Face setVertices. Failed replacement must
preserve endpoints, cache identity/geometry and scalar state. Endpoint-alias
replacement and normal geometry are separate ASan/CRT controls. The pinned
original fails; candidate, exact-head and implementation-main results are recorded in
[primitive allocation evidence](evidence/STAGE3_UV_ALLOCATION.md). This bounded
scope leaves template/Boundary registration, other setters and full-application
allocation failure qualification open.

```sh
python tools/quality.py docs
```

Doxygen is configured to report undocumented APIs and fail on warnings. Doxygen 1.18.0 is installed, but the initial documentation gate fails on
undocumented members. Complete API coverage and generated-page review remain
stage 8; a config file or installed tool is not generated-documentation validation.

## Pending registration qualification

Slice 4 extends the same runner to 49 cases and normal CTest to 14 entries.
Eight new sweeps deny 1,361 measured allocations in Boundary registration,
quality temporaries and prepared template creation. Missing-cell-context
queries throw std::logic_error; owned-cell numerical criteria are unchanged.
Selected lint covers six production units. The Boundary null-curve fixture
permits retry; failed templates are qualified for destruction only. See
[evidence](evidence/STAGE3_UV_REGISTRATION.md) for instruments and limits.

## Primary references reviewed 2026-10-15

- https://clang.llvm.org/docs/ClangFormatStyleOptions.html - repository style file.
- https://clang.llvm.org/extra/clang-tidy/ - compilation database and diagnostics.
- https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines - RAII, ownership,
  resource safety, interfaces and separation of responsibilities.
- https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html - shared presets.
- https://cmake.org/cmake/help/latest/manual/ctest.1.html - test discovery/execution.
- https://clang.llvm.org/docs/AddressSanitizer.html - instrumentation and limits.
- https://www.doxygen.nl/manual/config.html - API extraction and warning controls.

These are engineering references, not a proof that legacy code follows them.

## Tree construction qualification (#20)

Slice 5 introduced required application.uv_tree_contracts: 15 CTest tests at that boundary,
74 Python controls, 56 UV instrument cases and seven previous node cases.
Five independently calibrated CRT sweeps inject 3,470 allocation failures,
covering root, uniform subdivision, edge/old-face generation and real neighbor
refinement. Full original/candidate success traces and allocation counts must
match. Failed-tree destruction is qualified; retries and observer consumption
are not. See `evidence/STAGE3_UV_TREE.md` and ADR-0006.

## Angle-helper borrowed endpoints (#23)

Slice 6 adds required application.uv_angle_contracts: 16 CTest tests,
74 Python controls, 68 UV instrument cases and seven previous node cases.
Ten calibrated CRT sweeps deny 252 allocations through four endpoint-match
branches and the nonadjacent branch with empty/populated adjacency. They require
caller ownership/state, receiver cache/scalar state and successful query reuse
after every caught failure. ASan/CRT normal traces and successful allocation
counts match the original; the original fails all ten new sweeps. Prior 56
instrument controls remain required. See evidence/STAGE3_ANGLE_HELPER.md and
ADR-0007 for exact commands, diagnostic history and limits.

Doxygen 1.18.0 is now installed locally. The submitted initial documentation
run fails on undocumented APIs; this remains a stage-8 failure inventory, not
a documentation pass. Warning enforcement is unchanged.

## Parametric midpoint replacement (#26)

Slice 7 adds required application.uv_parametric_contracts: 17 CTest
entries, 74 Python controls, 81 UV instrument cases and seven previous node
cases. Eleven normal variants cover four sides/both directions, interior
fallback and null-curve no-op; ten CRT sweeps deny 30 allocations and require
unchanged cache identity/geometry and length, caller state and successful retry.
Normal success traces and successful allocation counts match the original.
Actual curve position/gradient, signed arc and midpoint have independent
analytic controls. Their three measured operation scopes observe zero
allocations; this is explicitly unmeasured curve-internal failure coverage.
See evidence/STAGE3_PARAMETRIC_MIDPOINT.md and ADR-0008 for commands and limits.

## Curve collection replacement (#29)

Slice 8 adds application.curve_collection_contracts, taking CTest to 18
entries with zero skips and 74 Python controls. The separate seven-production-
unit curve probe qualifies 19 ASan/CRT cases, including 14 normal setter variants,
two pointer-taking copy constructors and 76 allocation denials in 14 sweeps.
Prior UV 81/81 and node 7/7 controls remain required. Selected lint covers the
two actual curve implementation units with unchanged diagnostic rules.
List-node invalidation and independent per-list transactions are explicit.
See evidence/STAGE3_CURVE_COLLECTIONS.md and ADR-0009 for commands and limits.

## Initialized pointer-taking curve copies (#32)

Slice 9 adds application.curve_copy_contracts, taking CTest to 19 entries
with zero skips and 74 Python controls. The new nine-production-unit copy probe
qualifies 30 ASan/CRT cases across parametric/Bezier/Hermite types and empty,
forward/reversed sampled sequences. Nine positive-calibration sweeps deny 123
allocations, preserve source values/nodes/objects and require successful retry.
The prior curve 19, UV 81 and node seven cases remain required. Earlier curve
copy calibration now includes the newly preserved parameter nodes; fixed prior
allocation counts are not acceptance constants. Read-only lint covers the actual
changed parametric unit in its compiled configurations. See ADR-0010 and
evidence/STAGE3_CURVE_COPY.md for reproduction, original failures and limits.

## Geometry adoption (#35)

Required application.geometry_adoption_contracts takes CTest to 20 entries
with 74 Python controls. The ten-production-unit probe and
tools/qualify_geometry_adoption.py require 53 ASan/Debug CRT outcomes: 32 normal
type/destination/overload cases, two null-slot controls, 16 calibrated sweeps
(16 measured allocation denials), and deliberate UAF/leak/hook controls.
Previous copy 30, curve 19, UV 81 and node seven cases stay required. Selected
lint analyzes the actual Geometry unit; explicit formatting is confined to the
new probe and changed production/header ranges. Raw original failure dumps
retain tool-produced bytes locally with hashes, without whitespace suppression.
See ADR-0011 and evidence/STAGE3_GEOMETRY_ADOPTION.md for commands and limits.

## Curve clone publication (#38)

application.curve_synchronization_contracts takes CTest to 21 entries with
74 Python controls. tools/qualify_curve_synchronization.py requires 73 outcomes:
50 normal/guard ASan/CRT cases, 20 calibrated sweeps (484 allocation denials)
and three deliberate access/leak/hook controls. Existing adoption 53, copy 30,
curve 19, UV 81 and node seven cases remain required. The candidate compiles
13 actual production units, including real PatchBezier and the extracted
operation; the original comparison compiles 12 pinned units and a verified
function adapter. It is not full historical-generator instrumentation.

Only this new MSVC target uses /permissive- and Debug _ITERATOR_DEBUG_LEVEL=0,
consistently across all its units. MSVC level 2 allocates an iterator proxy in
vector's noexcept default constructor and terminates at denied ordinal 0.
That instrument failure is retained; iterator-metadata recovery is unqualified.
CRT heap retention, all observed production allocation denials and deliberate
controls remain required. ASan/serial Release use non-debug container layouts.
No previous target, diagnostic filter or scientific gate is weakened. Selected
lint required one explicit Hermite destructor override; the failed report is
retained. See ADR-0012 and evidence/STAGE3_CURVE_PUBLICATION.md.

## Curve snapshot restoration (#41)

application.curve_snapshot_contracts brings CTest to 22 entries, retaining
74 Python controls. tools/qualify_curve_snapshots.py requires 89 outcomes:
56 normal capture/restore, two guard, 28 calibrated allocation sweeps (536
denials) and three deliberate ASan/CRT/hook controls. Compile candidate target
curve_snapshot_probe from tests/curve_memory with AP_MESH_CURVE_SOURCE_ROOT set to
this checkout and AP_MESH_CURVE_ASAN enabled/disabled for separate ASan/Debug
CRT build directories. Debug iterator metadata is consistently disabled only
for the new target; CRT heap checks remain. Run the runner with --asan, --crt,
--runtime and a new --output directory. Previous six instrument batteries remain
required. Original evidence uses 14 pinned units and the verified lambda adapter;
candidate uses 15 actual units. This is not full-process memory qualification.

## Paired target-count curve rebuild (#44)

application.curve_rebuild_contracts brings CTest to 23 required entries with
74 Python controls. tools/qualify_curve_rebuild.py requires 117 outcomes:
78 ASan/CRT normal cases, 36 positive calibrated sweeps (597 denials) and
three deliberate UAF/leak/hook controls. Candidate target curve_rebuild_probe
compiles 13 actual production units; original comparison uses 12 pinned units
plus the verified lambda adapter with explicit ID-manager context substitutions.
Configure tests/curve_memory in separate build directories using
AP_MESH_CURVE_SOURCE_ROOT and AP_MESH_CURVE_ASAN; the original additionally sets
AP_MESH_REBUILD_IMPLEMENTATION. Build RelWithDebInfo for ASan and Debug for CRT;
run the runner with --asan, --crt, --runtime and a new --output. The new Debug
target consistently disables iterator metadata and retains actual CRT heap
checks. Previous seven batteries remain required; whole-process/parallel memory
qualification remains open. No-op/empty controls are explicit guards.

## Serial adapter sample construction (#47)

application.curve_samples_contracts brings CTest to 24 entries with 74 Python
controls. tools/qualify_curve_samples.py requires 88 outcomes: 54 normal ASan/CRT,
27 strict allocation sweeps, three retention-only sweeps (702 denials over
all 30 positive calibrations), three deliberate UAF/leak/hook controls and one
explicit MSVC list-move allocation-denial control. The new curve_samples_probe
target disables optional NRVO consistently (/Zc:nrvo- or -fno-elide-constructors)
to test return construction before commit. Debug CRT uses non-debug iterator
metadata and actual heap checks; all earlier targets retain their settings.
Configure tests/curve_memory in separate directories with AP_MESH_CURVE_SOURCE_ROOT
and AP_MESH_CURVE_ASAN; original additionally uses AP_MESH_SAMPLES_IMPLEMENTATION.
Build RelWithDebInfo/Debug and run the runner with --asan, --crt, --runtime and
a new --output directory. Original: 14 pinned units plus the verified identical
serial tail; candidate: 15 actual units. Previous eight batteries remain required.
Retention-only cases do not establish preservation/retry. Upstream whole-adapter,
Generator publication and full-process memory qualification remain open.

## Generator per-curve publication (#50)

Required application.curve_publication_contracts brings CTest to 25 entries with
74 Python controls. Build curve_publication_probe from tests/curve_memory in
separate ASan RelWithDebInfo and Debug CRT directories using
AP_MESH_CURVE_SOURCE_ROOT and AP_MESH_CURVE_ASAN. The original additionally sets
AP_MESH_PUBLICATION_HEADER to the retained verified publication-block adapter.
Run tools/qualify_curve_publication.py with --asan, --crt, --runtime and a new
--output directory. Require all 139 outcomes and 2403 denials across
27 positive sweeps, including allocation-free rollback and post-rebuild final
publication. Source/cache borrowing, exact entry point/parameter/cache nodes,
consumed IDs, successful retry, analytic interiors and deliberate controls remain
required. Optional NRVO and Debug iterator metadata are disabled consistently
only for the new target; actual heap checks and nine prior batteries remain.
Seventeen actual candidate units plus the actual template; original sixteen
pinned units plus a verified block adapter with parameter-controlled callbacks.
This is not full old Generator/Adapter or full-process memory instrumentation.
See evidence/STAGE3_CURVE_PUBLICATION_HANDOFF.md and ADR-0016.

## Complete curve sample graph lifetime (#53)

Required application.curve_sample_graph_contracts brings CTest to 26 entries and
74 Python controls. Build curve_sample_graph_probe from tests/curve_memory in
separate ASan RelWithDebInfo/Debug CRT directories, setting AP_MESH_CURVE_SOURCE_ROOT
and AP_MESH_CURVE_ASAN. Original additionally sets AP_MESH_SAMPLE_GRAPH_HEADER to
the retained verified capture/retirement adapter. Run
tools/qualify_curve_sample_graph.py with --asan, --crt, --runtime and a new --output
directory. Require 156 outcomes/8118 calibrated denials, exact restoration/
retry, allocation-free rollback and separate retention-only measurements.
Twenty actual candidate units plus probe; original nineteen pinned units plus
probe and the verbatim original blocks. Optional NRVO/Debug iterator metadata
are disabled consistently only for the new target; actual heap checks and all
ten prior batteries stay required. Empty graph is an explicit guard. Complete
point/parameter graph qualification does not establish full orchestration/mesh
rollback. Compact retained reports include command/case inventory and raw hashes;
complete raw local reports/logs retain all per-ordinal observations. See
evidence/STAGE3_CURVE_SAMPLE_GRAPH.md and ADR-0017.
