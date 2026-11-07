# Linux undefined-behavior and leak qualification

Observed production revision: `6a3d25e647c633b3f36520181a789a79d98e02d2`.
Classification: engineering-only test-observer repair and qualification of the existing L-UB/LEAK profile
in the [serial execution ledger](../architecture/SERIAL_EXECUTION_LEDGER.md).
No production, input, formula, evaluation order, acceptance, synchronization or
stopping rule changes. This is a required S3-09 dependency, not stage closure.
The [compact record](stage3/linux_ub_leak/summary.json) identifies the actual
artifacts, controls, failures, commands and remaining scope.

## Compiler and actual instruments

The environment is Ubuntu 24.04 x86_64 under WSL, Clang 18.1.3, libstdc++ 13.3
and C++17. The normal complete target builds in RelWithDebInfo with MPI, OpenMP,
LTO and BUILD_TESTING off. All 76 current production translation units compile;
the engine archive and CLI are both included. Existing warnings remain visible.
The reference build returns zero; no compiler diagnostic is suppressed for this
observation and no repository compiler preset changes.

The initial control link fails because libclang_rt.lsan-x86_64.a is absent.
Installing Ubuntu libclang-rt-18-dev repairs that environment dependency. The
next combined -fsanitize=undefined,leak control link still fails with unresolved
UBSan handlers. Both failures and their commands/raw output remain preserved;
neither attempt executes an application or control. A recorded disposition
qualifies separate UBSan and standalone LSan builds instead, retaining every
intended check. No handler stub, suppression, retry-to-green or extra runtime
library is substituted.

Both control builds use C++17, -O2, -g, -fno-omit-frame-pointer and
-fno-sanitize-recover=all. UBSan uses -fsanitize=undefined; LSan uses
-fsanitize=leak. Each executes an actual valid allocation/read/delete and defined
arithmetic control with exit zero and empty stderr. The deliberate signed-int
overflow exits 1 with its runtime-error diagnostic. The deliberate unreachable
allocation exits 23 with an actual 128-byte, one-object leak report. These are
expected detections, not production defects. The missing external-symbolizer
warnings remain in the negative-control logs; exact-artifact addr2line resolves
the recorded offsets to Overflow, Allocate and main offline. No process is
repeated for symbolization.

The complete application is built separately for each instrument, with the same
language/configuration and frame-pointer/nonrecovering flags. Actual compilation
databases contain 76 matching source groups for each target, zero excluded units
and the corresponding sanitizer flag in every group. Link commands, compiler,
runtime libraries, executable/archive hashes and source identities are retained.
LSan supplies allocation interception and exit-time reachability analysis; its
compile flag does not imply per-expression undefined-behavior instrumentation.

## Preserved compiler-reference comparison

The uninstrumented Clang executable runs the existing Eistute and Book article
configurations once each, with only input/output paths relocated and the unchanged
300-second per-process cap. Independent physical, UV and boundary verification
passes: nine states and 123 positive boundary comparisons, including the original
accepted/rejected traces. No new model or numerical threshold is used.

The initial comparison controller incorrectly mixes JSON-deserialized string
stage keys with native integer stage keys and stops at a mesh-coverage error.
Both completed verification reports retain all five Eistute states. Offline replay
with consistent serialized key types uses the unchanged strict comparator; no
application is repeated. Its actual raw comparison fails at exactly ten hash
fields: five OBJ hashes and five incidence-snapshot hashes. All metrics, decisions
and other compared fields agree. The failure remains a failed raw-byte comparison.

An explicit offline platform-encoding disposition proves all 25 Eistute and 20
Book scientific artifacts equal after CRLF-to-LF conversion only. No number,
ordering, field, whitespace other than those line endings, or tolerance is
normalized. Compatibility CSV fields also agree after excluding the existing
relocated model-path field; timing remains outside scientific equality. The raw
references and captures stay untouched. This is cross-platform text equivalence,
not a claim that Windows and Linux exports are byte-identical. Only the previously
unstarted Book process resumes after this disposition.

## Fixed caller inventory and scope

The first natural SP-02 case uses the existing aligned, two-sheet analytic fixture
and its fixed input hash. Both instruments pass actual process/owner teardown and
independent physical/UV/boundary checks. There is no failure injection, rejected
step or adaptive retry in this initial-only witness.

After the first witness, expansion uses only the already fixed SP-01..08 inventory
and original 10/60/300-second case caps. Invalid-input diagnostics/artifact absence,
real m/q exports, positive analytic boundaries, native rejection/retry and article
repetition remain independent oracles. Mode q uses the preceding real mode-m
geometry as its explicitly paired source; no q OBJ is fabricated. No-sync completion
does not establish synchronized-boundary coverage. Each child capture is preserved
before a later child can start; unexpected diagnostics or application outcomes
stop expansion.

The five existing SP-09/10 directed contexts use the separately built controlled
full caller and existing reversible observer preparation. They are controlled
terminal propagation/cleanup observations, not successful production meshes or a
Generator exception-recovery promise. Release, live/excluded/disabled observer,
actual allocation denial, nine payload cases and unwind controls precede them.
Failed CLI prefixes must still be rejected by the unchanged generation verifier.

## Controlled allocator integration repair

The original controlled UBSan target passes all five directed contexts. Its
standalone LSan counterpart fails at link: both the runtime and the fixture define
six strong allocation/deallocation symbols. No LSan directed process starts from
that failed build. The original directory, objects, commands and failed report
remain preserved.

The test-only AP_MESH_TERMINAL_ALLOCATOR_WRAP option is off by default and rejects
platforms outside qualified Linux x86_64 Clang. GNU link wrapping routes compiled
scalar/array allocation and sized/unsized deallocation calls through the observer,
then forwards to the runtime's own functions. The array allocation observer retains
its original single scalar-delegate observation. No weak symbol, duplicate-definition
link flag, replacement runtime or disabled detector is used. The option affects
only three test sources; no production compilation definition changes. The final
controlled target has 78 compilation groups, including 75 production units and
the reversible Adapter substitution, rather than the CLI entry point.

Native controls require all six routes, four actual allocation/deallocation pairs
and two caught denials, as well as the original live/excluded/disabled observer,
real SubMesh unwind denial and nine typed payload cases. A named standalone
deliberately invalid source must produce an actual four-byte LSan leak. Allocation
wrapping covers the compiled caller; it does not promise denial interception inside
arbitrary precompiled shared libraries. LSan reachability accounting remains
independent of the allocation-attempt counter.

The first wrapped LSan negative capture exits 23 and detects the expected four
bytes, but the controller requires an unavailable stdout marker and stops. Exact
artifact symbolization attributes the allocation to TerminalControlLeak offline;
only the five unstarted directed contexts resume. The final control explicitly
flushes its marker before expected runtime termination. No failed capture is
overwritten or called an initially successful controller run.

Read-only static analysis also rejects a write through a zero-size allocation
in the initial new forms control. Its revised pointer observation never accesses
zero-size storage. The deliberate leak is separated into its explicitly invalid
control source. LLVM 22.1.8 analyzes both valid default/wrapped source branches
without diagnostics, while its unchanged analyzer detects the deliberate leak
in the invalid control. No check, warning policy or suppression is changed.
The unsupported LLVM 18 header-filter configuration and an initial Windows
compiler-probe failure without the canonical child PATH remain recorded; actual
analysis uses the existing qualified tooling/environment.

Default-OFF active source lines in the existing three fixture files remain exact
against the observed base after removing only the new conditional blocks and blank
lines. CMake has only the explicit opt-in block added. The default Windows/GNU/MSVC
observer behavior is therefore retained; its source proof and actual unsupported-
MSVC option rejection are recorded. Final wrapped artifacts require new controls
and all five directed contexts for each instrument. Existing unmodified production
and scientific observations are reused by their unchanged identities.

## Delivery and remaining obligations

The final fixed observations pass in both profiles:

| Observation | UBSan | LSan |
| --- | --- | --- |
| Unmodified SP-01..08 processes, including first SP-02 | 32 | 32 |
| Final controlled SP-09/10 contexts | 5 | 5 |
| Actual scalar/array forms and denial control | passed | passed |
| Final release/observer/type prerequisites | passed | passed |
| Instrumented article states, both repetitions | 18 | 18 |
| Exact raw scientific artifact pairs against uninstrumented Clang | 90 | 90 |
| Positive article boundary comparisons, both repetitions | 246 | 246 |

All five final contexts per profile retain their original typed/owner/sample/
attempt/unwind oracles. The actual four-byte final LSan control exits 23, emits
its flushed marker and produces its expected leak report. Completed unmodified
production/scientific processes are not repeated for the fixture repair. All 522
protected production/build/input files and their timestamps, four qualified
Windows executables/archives and all 43 original retained-block artifacts remain
unchanged. The architecture inventory changes only the terminal CMake hash;
35 contracts, 276 anchors and the 164-file production inventory remain intact.

Require the full 75 CTest / 495 Python baseline on exact delivery head and merged
main, unchanged production/input/source/oracle identities, retained instrument and
scientific captures, architecture/contracts/whitespace and fresh remote audits.
Documentation delivery reuses qualified binaries and completed observations by
identity; it does not rerun scientific or instrument processes. The guarded
qualified-tree checkout and receipt remain required before main validation.

The original three bounded-qualified/seven partial-open Stage 3 dispositions stay.
Conservative leak reachability, arbitrary heaps, runtime/DLL/parallel behavior,
broader callers and input domain, mutation/foreign observers, failed-tree reuse,
exception recovery and outside-root ideal retirement retain their independent
obligations. No absent diagnostic is a proof of general safety, no zero boundary
count is a boundary pass, and no bounded instrument phase closes the whole stage.

Instrument/linking references: [UBSan](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html),
[standalone LSan](https://clang.llvm.org/docs/LeakSanitizer.html) and the
[upstream combined-driver report](https://github.com/llvm/llvm-project/issues/138982).
The local commands and actual failures, rather than an inferred upstream cause,
establish the disposition for this artifact.
