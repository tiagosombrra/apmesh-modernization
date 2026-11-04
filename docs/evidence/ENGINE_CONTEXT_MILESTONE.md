# Internal serial engine/context milestone

Classification: documentation-only engineering consolidation. Reviewed baseline:
PR #153 main `84fff0d2344429aaf61f9bae5c109b86c35fddad`. This closes the bounded
internal serial engine/configuration/CLI milestone when the six exit criteria
below are sealed on this delivery head and merged main. Stage 3 and the complete
stage 6 remain open; the ten stage 3 ledger dispositions are unchanged.

## Delivered boundary and exit criteria

| ID | Objective criterion | Evidence / disposition |
| --- | --- | --- |
| EC-01 | CLI delegates to an internal linkable engine; canonical GCC/MSVC C++17 serial builds include the actual production units. | APMesh::Engine aliases ap_mesh_engine; thin CLI and existing consumers link it. PR #153 exact-head/main build reports are reused by unchanged source, build configuration and executable identity. |
| EC-02 | Synchronous execution takes a typed request; configuration/identity are value-owned, with documented compatibility behavior. | GenerationRequest, GenerationContext and deleted generator copy/move operations remain qualified by the existing native controls. The raw argv bridge and missing-group live fallback remain available. |
| EC-03 | Every declared context group has explicit raw/effective state and owner/observer boundaries; no scientific expression/order change is inferred from migration. | Eleven groups contain 181 fields, plus four identity/output fields. Stable updates remain local to the owning generator; Adapter borrows stationary state and trees/fronts own their published copies. Prior source-reversal and native evidence retain each group's scope. |
| EC-04 | The existing numerical, boundary and negative-control reference remains valid on the delivered production code. | Reuse PR #153: 75 CTest/385 nested controls; nine scientific states, 45 exact artifacts, 123 boundary comparisons; 23 invalid MSVC controls and one analytic state with one positive boundary comparison. Current delivery reruns the existing CTest gate; unchanged scientific/MSVC/native/instrument observations are reused by identity. |
| EC-05 | Remaining state and unsupported claims are explicit; the original closure/failure inventory remains visible. | The original consolidation classified 203 definitions; the current matrix tracks 201 active definitions and two retired dormant registries, plus named auxiliary statics and caller protocol. All ten stage 3 rows keep their dispositions: three bounded-qualified, seven partial/open. |
| EC-06 | Exact delivery head and merged main pass required quality/contracts/CTest/identity checks, with remote state audited. | Required for this consolidation. The PR and local build/engine-context-milestone integration seal record revisions, commands, hashes, evidence reuse and final disposition. Missing/failing required checks block this bounded closure. |

EC-01..05 are established at the reviewed baseline and unchanged source. EC-06
is the final delivery gate; successful local tests alone do not establish merge
or main qualification. After sealing EC-06, this milestone has no automatic
configuration-migration or instrument-campaign successor.

## Admitted execution protocol

Use the canonical serial C++17 profile with MPI/OpenMP disabled. The measured
full-generation cases use one process/thread. Run the entire sequence serially:

1. Load and validate configuration through LoadRuntimeConfig.
2. ApplyRuntimeConfig updates process state and retains its existing clamps and
   hybrid/template projection. MakeGenerationContext then copies both explicit
   configuration fields and current applied process values.
3. Construct a fresh stationary GeneratorAdaptive with that context and an owned
   GenerationRequest. Execute is synchronous; Timer and borrowed observers must
   remain live through their documented use.
4. Retire the generator and associated local owners after the run. Preserve the
   existing terminal-versus-logical-retry contract; a terminal failure introduces
   no same-generator recovery guarantee.

The CLI admits `ap_mesh --config <file>`. The internal raw Execute bridge retains
its existing valid-layout precondition. Other public generation/estimation and
low-level callers retain their individual contracts and open coverage assignments.
The library is an internal build target, without an installed SDK or stable ABI.

ApplyRuntimeConfig/MakeGenerationContext is not a pure request factory: defaults
and several captured values depend on live process state. The qualified path is
serialized end to end. A full context captures the named groups; a partial/default
context deliberately reads live globals for missing groups. Native interleaving
controls establish bounded setting/output ownership, not safe concurrent or
repeated complete generations in one process. Callers must not infer those claims
from value ownership or from a fresh generator alone.

## Remaining process state

The [complete matrix](../architecture/ENGINE_CONTEXT_STATE.json) classifies every
definition in runtime_state.cpp against the actual aggregate factory. It is a
reviewed source inventory, not a percentage of modernization or a race-freedom
proof. The original consolidation retained all 203 definitions. Subsequent
[dormant registry retirement](DORMANT_RUNTIME_REGISTRIES.md) leaves 201 active
definitions: 185 have a context binding and 16 do not; two removals are recorded.
Capturing an input does not remove its legacy definition or prove that every
alternate consumer uses the context.

| Disposition | Names / boundary | Required next dependency |
| --- | --- | --- |
| Captured inputs | 181 fields in adaptive policy, stop/retry, adaptation, element budgets, curves, quadtree, patch generation, consistency, acceptance, AFT and serial flow; four identity/output fields. | Preserve raw/effective semantics, independent discretization values, configured consumers, legacy fallback and published value/observer lifetimes. No automatic extra migration is required to close this bounded milestone. |
| Captured plus shared precision | EPSYLON is a stop/retry input and still serves PointAdaptive equality. | Distinguish physical/parametric units and consumers before any precision isolation. No blanket tolerance unification or value change is authorized. |
| Captured plus legacy I/O | INPUT_MODEL, NAME_MODEL, NUMBER_PROCESS and WRITE_MESH still serve default/alternate readers, writers and timer/estimation helpers. | Delimit each actual caller before promising whole-call-graph isolation; keep S3-05/07/10 open. |
| Uncaptured precision (5) | DELTA, TOLERANCE, TOLERANCE_CURVATURE, TOLERANCE_AFT, I_MAX. AFT's constructor tolerance argument remains inactive. | Audit units, geometric predicates and convergence contracts before propagation. Scientific changes require explicit alignment. |
| Uncaptured execution (3) | RANK_MPI, SIZE_MPI, MAX_THREADS. | Explicit serial/parallel execution ownership and separately qualified routing; this milestone authorizes no MPI/OpenMP change. |
| Attempt compatibility mirrors (2) | ADAPTIVE_CURRENT_STEP and ADAPTIVE_CURRENT_RETRY retain original writes and optional parallel reads. | [Serial dependence removed](GENERATOR_ATTEMPT_STATE.md): Adapter receives existing generator-owned step/retry values. Definitions remain uncaptured, not serial inputs. |
| Uncaptured estimation (2) | TRIANGLE_MEDIO and ESTIMATIVE_TOLERANCE remain in estimation helpers. | Preserve units and caller semantics; broader estimation/load paths remain outside this measured entry boundary. |
| Uncaptured timing (2) | TIME_READ_FILE and MAX_TIME. | Separate timing ownership from scientific criteria; correct-clock/profiling obligations remain in their stages. |
| Diagnostic compatibility aggregates (2) | FINDUV_TOTAL_CALLS and FINDUV_IMAX_EXITS remain cumulative atomics and supply the original I_MAX message ordinal. | [FindUV execution state](FIND_UV_EXECUTION_STATISTICS.md) now owns serial counts and CLI summaries; direct/parallel callers retain aggregate behavior. The separately inventoried thread-local observer is a scoped same-thread borrow, not a whole-engine concurrency guarantee. |
| Retired dormant registries (2) | LIST_ALL_POINTS_MODEL and LIST_ALL_SUB_MESH_MODEL had no internal consumers. Both definitions/declarations and header dependencies are removed. | Preserve named retirement evidence and internal source-interface scope; no global-freedom or external ABI claim. |

Additional named first-party statics include the scoped FindUV thread-local observer,
the quadtree debug sequence, the
translation-unit-local method-notice table and optional MPI communicator lifetime
state. Commented-out static scratch in Edge is not active state. Immutable local
constants and external/third-party internals are outside this explicit-definition
inventory. Lexical occurrences can refer to shadowing members, so they are not
runtime reachability evidence. The matrix and local evidence preserve that limit.

## Closure review and dependency decision

Code, build settings, tests, input fixtures and scientific oracles are unchanged
by this consolidation. Existing source, executable, prior-seal and report hashes
support evidence reuse. Contracts and documentation now distinguish captured
inputs from remaining mutable state and from full stage closure. Historical
failed observations remain failed; no zero-coverage path is relabeled qualified.

S3-01/05/06/07/08/09/10 remain partial/open for supported-caller ownership,
observer/cache validity, failed-tree/selection paths, orchestration/rollback,
complete-process instruments and input-domain coverage. CRT/leak/UB, repeated
complete execution and parallel obligations remain in the existing ledgers.
The bounded outside-root observations keep their original negative/zero-reach
scope. No generic instrument expansion follows this document.

At consolidation, three legacy run_book_v5_fix_* CMake recipes supplied positional
arguments although RunApplication admitted only --config. This was a source-level
workflow mismatch, not a new numerical observation; those recipes are not part of
the qualified entry protocol. The subsequent [Book recipe repair](BOOK_CMAKE_RUN_RECIPES.md) resolves usability
as three documented aliases of the unchanged supported Book article configuration.
No positional parameter translation or scientific configuration change is made.

The admitted attempt metadata dependency is now [implemented](GENERATOR_ATTEMPT_STATE.md):
serial Adapter arguments use existing generator state, preserving global mirror
writes and optional parallel reads. This supports S3-08 without closing it.
The original consolidation was documentation-only; this subsequent engineering
package retains its own exact-head/main build, regression and delivery seal.
The subsequent Book recipe repair closes that independent workflow debt.
