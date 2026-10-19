# Stage 3 slice 27: temporary error evaluator ownership

Candidate full gates pass; exact published-head and post-merge main qualification remain required. Stage 3 retains twenty-six qualified slices until both pass.

Entry main: `35e608162e17c04c21f1a8f3817aac885262bca5`.
Classification: behavior-changing resource-lifetime defect repair. Required header
override declarations and serial include qualification are engineering-only.
No scientific proposal; stage 3 remains open. Next repair area estimation roots
with explicit patch/sample lifetime and unchanged degree/error selection.

## Root cause and repair

CalculateErroEstimative allocated one GeneratorAdaptive for each call and never
deleted it. Its serial ErrorGlobal also stores a submesh-error vector in that
object. The caller now has one unique_ptr owner, released on return or exception.
The actual caller is isolated in src/estimate/error_estimate.cpp; its public legacy
symbol, serial/OpenMP dispatch, comparison order and thresholds are preserved.
The mesh and timer remain borrowed. No shared ownership, fallback or retry is added.

The strict error < minor_error_ comparison still selects the supplied degree;
minor_error_ itself is deliberately not updated. The inclusive error <= tolerance
comparison still stops evaluation. This preserves historical equality/NaN/infinity
behavior rather than silently repairing a selection policy. Area orchestration,
its evaluation-before-degree-cap order and final minor_degree_ selection are unchanged.
Timer values and partially written node curvatures are not rolled back on failure.

## Instrumented scope and paired evidence

The 480-blob original src/include/libs snapshot is Git verified at entry. The
original caller body is extracted verbatim. Candidate instrumentation compiles
the complete actual caller unit and dependency units with the actual class layout.
The generator constructor/serial ErrorGlobal and estimator constructor/destructor
bodies are extracted exactly and compared across all four probe builds. Complete
historical generator/estimator TUs contain MSVC-unsupported VLAs and are not
instrumented as whole units. GCC separately builds the complete serial application.

Five layouts (plane, saddle, parabolic cylinder, empty mesh and two submeshes) at
degrees 1/2/4 supply 30 normal ASan/CRT cases. Nine repeated policy evaluations per
fixture produce 270 paired decisions, with identical complete reference/policy/
per-node curvature-bit observations. Plane/empty errors are independently zero;
curved errors are nonzero. Equality, adjacent doubles, NaN and infinities are exercised.
The direct unchanged evaluator is a differential reference, not an independent
proof of the curvature formula or scientific selection policy.

Fifteen complete allocation sweeps cover 156062 observed allocation ordinals.
Each child covers at most 32 consecutive ordinals within the unchanged 30-second
limit; the runner verifies exact nonempty interval union, one denial/no later
allocation, zero live/final CRT blocks/bytes, borrowed physical graph identity
and unchanged selection fields on exceptions. The graph is reused within an
interval; partial node-curvature/timer effects are allowed, not rolled back.
Successful calibration allocations match all fifteen original/repaired pairs.
Three real ASan UAF/CRT leak/allocation-hook controls bring the new inventory to 48.

Original evidence retains 30 CRT retention failures and eighteen expected outcomes.
Each original successful nonempty evaluation retains its evaluator and vector;
an empty evaluation retains its evaluator. Calibration retention is included in
terminal CRT measurements. Per-denial checkpoints independently detect live
retention in twelve nonempty sweeps, which stop before later unmeasured ordinals.
The three empty sweeps complete their single exceptional allocation boundary but
retain their successful calibration evaluator. Original ASan normal success has
leak detection disabled and does not establish leak freedom. No hidden-root UAF
or full-process leak-freedom conclusion is inferred.

## Failures and required tooling repair

The first MSVC probe build failed because the existing CurvatureDiscrete requires
M_PI. The dedicated target requests _USE_MATH_DEFINES before cmath, preserving
the existing constant; no production formula or warning suppression changed.
The initial unpartitioned failure-0-2 sweep timed out at 30 seconds after the
smaller sweep passed. Its available logs and missing interrupted stdout are
recorded explicitly. Nonoverlapping intervals preserve all allocation ordinals
and the same per-child timeout; no hidden retry or relaxed budget is used.

A superseded preliminary run, built before the header repair, was stopped while
the full frozen-input candidate campaign independently repeated the battery.
Its partial logs/binary identities and incomplete coverage are retained in
preliminary_stop.json; no complete preliminary success is claimed or reused.

The new caller's first strict lint failed on 63 inherited override declarations
and unconditional omp.h inclusion in the serial header. An explicit bounded
six-header batch adds compiler-checked override specifiers without changing
signatures or bodies. The generator header reads definitions before including
omp.h only for USE_OPENMP. Retained preflight/exported diagnostics and per-file
before/after hashes document this repair; no clang-tidy --fix or suppression was used.
The existing architecture cycle remains one: 144 files, 68 TUs, 76 headers,
22 contracts and 144 anchors. Enabled OpenMP runtime behavior remains unqualified.

## Commands, closure audit and limitations

Run `. ./build/local-env.ps1` before local commands. Configure the dedicated
tests/curve_memory target in isolated MSVC ASan RelWithDebInfo and Debug CRT
directories, then run tools/qualify_error_estimate.py with --asan, --crt,
--runtime and a fresh --output directory. AP_MESH_CURVE_SOURCE_ROOT and
AP_MESH_ERROR_ESTIMATE_IMPLEMENTATION select the verified original snapshot/body.
The retained reports enumerate complete commands, revisions, source identities,
executables, child intervals, controls and raw log hashes.

Full gates require serial C++17 build, CTest 37/37 with zero skips/74 Python
controls, all 1421 expected outcomes across twenty-two batteries, the retained
1040 scalar comparisons at 520 degrees and the rejected recomputation control,
selected factory/count/evaluator lint, new-file format, inventory/whitespace,
and twice-repeated Eistute/Book traces. All nine accepted/rejected OBJ states,
incidences, acceptance/boundary inventories and independent 189-field CSV audit
must match. Complete remote/local trees, indexed/working bytes and all 571
protected identities must match on the exact delivery revisions. Zero configured
hosted checks is absence of hosted validation, not green CI.

Code, tests, C06 observer/borrowing contract and this audit describe the same scope.
Area Mesh roots and patch/sample lifetime, arbitrary callbacks, evaluator cache
rollback, foreign observers, extreme/non-power-of-two complete meshes, logical
rejection, full-process/parallel/LSan/UBSan remain open. Stages 4-11 remain pending.
Documentation closure repeats exact-tree build/CTest/inventory/identity checks;
no fresh full instrument/numerical campaign is claimed for documentation-only trees.
