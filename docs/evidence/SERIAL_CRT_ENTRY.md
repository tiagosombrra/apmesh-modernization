# Complete-entry checked-CRT observation

The original failed entry-return observation below remains preserved. The
[static-teardown follow-up](SERIAL_CRT_STATIC_TEARDOWN.md) now attributes all 150
requests and observes their natural release in a separately identified diagnostic;
it does not retroactively replace the original checkpoint or its failed report.

## Admission and bounded execution

Entry main: `1ec01ada2a52e05009698ae18ccb0b7130680349` (PR #166).
Classification: engineering-only test instrumentation for the existing required
S3-09 W-CRT observation, contributing to S3-01/05/08 within its measured scope.
The completed [cache admission](P4_CACHE_MUTATION_ADMISSION.md) remains negative;
this independent required instrument gate does not reopen its source-audit chain.

The concrete output is a checked-Debug observer linked to the complete existing
serial engine and calling RunApplication through its actual config entry. Its
checkpoint spans Execute-local Geometry, outer Generator and Timer teardown.
Production, numerical inputs, formulas, ordering and scientific policies are
unchanged. C++17, Debug DLL CRT, iterator level 2 and exception unwinding remain.

Before a production case, require actual 64-byte allocation/release, deliberate
64-byte retention, equal-sized baseline retirement/new retention and an actual
denied allocation caught as bad_alloc. The balanced-retention negative control
must be detected even with zero net heap delta. Always retain the CRT newer-live-
block dump, signed normal/client deltas and raw stdout/stderr; do not subtract
unexplained runtime retention. The checkpoint anchor remains live through the
dump, then retires outside the measured interval.

Only after these controls pass, run the existing SP-02 aligned two-sheet analytic
control once through the unchanged boundary_orientation_case.run_control recipe,
with its 60-second limit and independent physical/UV/positive-boundary checker.
Stop at the first unexpected build, instrument, application or checker failure;
retain it without retry, suppression, larger cap or expansion to other cases.

```text
cmake -S tests/serial_crt -B build/p3-serial-crt-entry/native -G "Visual Studio 17 2022" -A x64
cmake --build build/p3-serial-crt-entry/native --config Debug --target serial_crt_probe --parallel 2
python tools/qualify_serial_crt.py --exe build/p3-serial-crt-entry/native/bin/Debug/serial_crt_probe.exe --output build/p3-serial-crt-entry/observation
```

The build retains the existing 600-second bound. The runner requires a fresh
output directory, preserves raw logs and writes a final report even on an
observed failure. No Eistute/Book or additional scientific campaign is admitted
by this work item. Complete-process instrument coverage, all other cases and
Stage 3 remain open until their own required observations are measured.

## Results and stop decision

The [compact record](stage3/serial_crt_entry/summary.json) binds the local build,
observer and failed production observation. The complete 75-unit engine builds
once in 132.030628 seconds, with two jobs and the unchanged 600-second bound.
Generated Debug project metadata confirms C++17, MultiThreadedDebugDLL, /EHsc,
C4530 as an error and no iterator override. The probe requires iterator level 2.

All four actual controls pass their prescribed oracles. Release leaves no newer
live block; deliberate retention reports exactly one 64-byte block; balanced
retention reports that same newer live block despite zero net deltas; the real
allocation hook denies one allocation, propagates bad_alloc and leaves no block.
Expected control exits 2 and 0 are retained separately from production success.

The one SP-02 RunApplication call returns 0 with a valid CRT heap, 6,172 observed
allocation attempts and no injected denial. After its local owner teardown, both
signed accounting and the newer-object dump report **150 normal blocks / 7,456
bytes still live**. Client deltas are zero. The observer returns 2 and the overall
observation fails. Its boundary-only diagnostic retains two patches, eight
triangles and one positive shared-boundary comparison. Full independent mesh/UV
verification rejects the nonzero process status; it is not recorded as passed.
No other production case or repeat is run.

This is entry-return retention, not attribution of 150 leaks or observation after
all process-static destructors. The dump includes configuration-key strings and
two 128-byte path buffers. Source inspection identifies function-static key sets
in [input validation](../../include/input_output/input_validation.h) and global
path owners assigned by [ApplyRuntimeConfig](../../src/application/runtime_config.cpp).
Those owners survive RunApplication; source similarity alone does not assign
every dumped block. The remaining 8-byte block also has no established owner.
No bytes are subtracted, no warm-up hides initialization and no cleanup is added
to production merely to make the observer green.

**Stop expansion.** The next bounded dependency is to attribute the retained
requests and observe the required static-owner teardown boundary, with explicit
positive/negative controls, before another production execution. Explain every
residual; repair production only after demonstrating an unowned supported path.
The current result does not qualify SP-02 W-CRT, full-process memory or Stage 3.

## Tooling validation and delivery limits

Eight new checker controls pass; the complete Python suite passes 449 controls.
The initial suite correctly rejected the missing nested-CMake inventory entry;
its log is preserved and the inventory is updated without changing contracts.
An initial metadata preflight assumed /we4530 would appear in AdditionalOptions;
CMake encodes it as TreatSpecificWarningsAsErrors=4530. That preflight failure
and its corrected interpretation are preserved without rebuilding or changing
flags, before the first native control. Formatting and whitespace are checked
explicitly. No diagnostic is suppressed.

The working package is local and unqualified for delivery because its required
native observation fails. No commit, publication or merge is made. The existing
75-CTest exact-head/main delivery gates have not been rerun for this candidate;
the 75/441 results on PR #166 main remain evidence of that unchanged revision.
Unchanged scientific evidence retains its own scope and identities. All ten
Stage 3 dispositions remain: three bounded-qualified and seven partial/open.

## Authorized static-teardown follow-up

The follow-up preserves the original executable, PDB, build receipts, stdout,
stderr, scientific artifacts and failed report byte for byte. Their 43 recorded
artifact hashes are verified before work and again at the end. Original observer
sources are additionally copied locally before extending the test CMake project.
The new output root is build/p3-serial-crt-static; it never reuses the original
observation directory. Source classification predicts that the three immutable
configuration-key sets account for 147 blocks / 7,192 bytes. This prediction is
not request attribution or release evidence.

The test-only static observer captures allocation stacks by CRT request number
into fixed, bounded POD storage. It matches entry-return live requests to the
independent CRT dump, identifies the two actual global path allocations, and
observes their frees through natural executable/runtime teardown. Windows-handle
logging remains active after C++ stream owners retire. A lib-priority final
observer and an earlier atexit callback expose the executable-global and lazy-
static boundaries; actual owning-static and deliberately unowned controls must
calibrate their ordering. An actual key-set-only control must account for its
complete 147-block prediction and natural release. Unknown requests, trace
overflow, reentrant callbacks, reallocations or unmatched frees block attribution.

Only after these controls pass, one same-input SP-02 diagnostic may run with the
unchanged 60-second bound and a fresh output path. It retains the original failure
as the entry-return observation and does not rerun Eistute/Book or expand cases.
Stop at the first unexpected failure. No manual global cleanup, warmed production
entry, subtracted retention, production repair or stage closure is authorized by
the instrument. The question is release of the observed requests; allocations
created later during shutdown retain their own unmeasured scope.
