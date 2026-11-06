# Retained CRT request attribution and static teardown

Entry main: `1ec01ada2a52e05009698ae18ccb0b7130680349` (PR #166).
Classification: engineering-only instrument correction and bounded S3-09
observation. Production, numerical inputs, scientific formulas, ordering and
policies are unchanged. The [original entry-return record](SERIAL_CRT_ENTRY.md)
and its failed accounting remain preserved, rather than relabeled as clean.

## Result

The [compact record](stage3/serial_crt_static_teardown/summary.json) accounts for
all 150 entry-return requests in the separately identified diagnostic process.

| Owner | Blocks | Bytes | Observed release boundary |
| --- | ---: | ---: | --- |
| Three configuration-key sets | 147 | 7,192 | Natural function-static destructors, before the early-main atexit callback |
| INPUT_MODEL buffer | 1 | 128 | Executable-global destruction |
| NAME_MODEL buffer | 1 | 128 | Executable-global destruction |
| ptr_aux vector storage | 1 | 8 | Executable-global destruction |
| Total | 150 | 7,456 | Every watched request has one observed free |

At entry return, the diagnostic reproduces 150 blocks / 7,456 bytes. After lazy
statics it has three blocks / 264 bytes. After executable statics, all watched
requests are freed: zero blocks / zero bytes. No subtraction, artificial global
cleanup or production-entry warm-up obtains this outcome.

The allocation stack for the 8-byte block reaches
[GeneratorAdaptive::Generator](../../src/generator/generator_adaptive.cpp), at
ptr_aux.resize(size_thread, nullptr). Its release stack reaches the generated
dynamic atexit destructor for ptr_aux. The vector is defined in
[curve_adaptive_parametric.cpp](../../src/data/curve/curve_adaptive_parametric.cpp).
The result concerns the vector's storage; it does not establish lifetime safety
of every borrowed CurveAdaptiveParametric pointer stored by other callers.

The two global path buffers are identified by their actual data pointers and
CRT request numbers while their [runtime-state owners](../../src/application/runtime_state.cpp)
remain live. Allocation stacks for all 147 other requests reach the actual
[ValidateConfigValue](../../include/input_output/input_validation.h) static key
sets. Their natural frees precede the lazy-static checkpoint. A separate real
key-set-only control confirms exactly 147 blocks / 7,192 bytes and their release.

## Calibration and reproduction identities

Five native controls precede the single diagnostic: actual allocation/release,
an owning global, deliberately unowned retained storage, allocation denial with
bad_alloc and the real lazy-static key sets. The owner control releases its
64-byte allocation between the calibrated boundaries. The deliberate retention
survives process exit in the request census and remains an expected negative,
despite its native exit 0; no zero exit substitutes for memory accounting.

The instrument uses the unchanged complete 75-unit serial engine, MSVC C++17
Debug DLL CRT, iterator level 2 and /EHsc with C4530 as an error. A separate
lib-priority observer translation unit registers before normal user-priority
owners; actual native controls verify the required ordering. MSVC's C4073 notice
for that explicit initialization priority is retained, not suppressed.
Fixed POD request/stack storage and raw Windows-handle logging remain usable
through owner destruction. The independent CRT dump must match the watched
request/size pairs exactly. Overflow, reentrant callbacks, ambiguous reallocations,
unknown requests and missing/duplicate frees or stacks are failures.

The one diagnostic uses the same generated SP-02 input SHA-256
`41eb3c5216ad11452f467321a23c3e32fd10a75f85f538ce9e2c70bb28651444`, a new process,
new observer executable and fresh output directory, retaining the unchanged
60-second bound. Independent physical/UV/boundary verification passes: accepted
step 0, two patches, eight triangles and one positive shared-boundary comparison.
The incidence snapshot SHA-256 is identical to the original retained snapshot.
All 150 request-ordinal/size pairs also match the original. Request ordinals are
process-local: this is a reproduction correspondence, not shared allocation
identity or a retroactive observation of the original process's shutdown.

The 43 recorded original artifact hashes are checked before and after the
follow-up, including the original executable/PDB, build metadata, raw logs,
scientific artifacts and failed report. The original observation is untouched.
Local follow-up artifacts are under build/p3-serial-crt-static; the original
build/p3-serial-crt-entry directory is not used as an output destination.

## Preserved failures and controlled corrections

The first follow-up build fails before any native case: observer include order
exposes Windows numeric-limit macros to the validation header, and changing
init_seg within one translation unit triggers C2356. Its sources, logs, metadata
and classification are retained under failed-build. Reordered test includes and
a separate final-observer translation unit repair those instrument defects.
The revised build takes 4.336143 seconds and preserves the already built engine
archive byte for byte. No production source or compiler flag is changed.

All five native controls and the one diagnostic then complete. A batch symbol
lookup stops because the private ntdll.pdb is unavailable. That failure remains
in the original follow-up report. Complete executable/PDB symbol records had
already been captured before that failure. Offline analysis of those records
and immutable raw logs attributes every watched allocation and release; it
launches no new native process. Windows-private frames remain explicitly
unresolved module/RVA records. They are not claimed as qualified private symbols
and are not needed to identify these executable-owned allocations.

```text
cmake -S tests/serial_crt -B build/p3-serial-crt-static/native -G "Visual Studio 17 2022" -A x64
cmake --build build/p3-serial-crt-static/native --config Debug --target serial_crt_static_probe --parallel 2
python tools/qualify_serial_crt_static.py --exe <static-probe> --symbolizer <local-llvm-symbolizer> --original build/p3-serial-crt-entry/observation/report.json --output <fresh-output>
python tools/qualify_serial_crt_static.py --analyze-existing <captured-report> --executable-symbols <captured-executable-symbol-records> --output <new-attribution-report>
```

## Scope and remaining gates

The requested retained-request attribution and natural-release question is
resolved locally. No production leak repair is demonstrated or required by
these 150 blocks. The original entry-return failure remains valid at its earlier
checkpoint. This evidence does not qualify allocations first created during
shutdown, all process heaps, arbitrary inputs/callers, another instrument, other
SP cases or complete Stage 3. All ten ledger dispositions remain unchanged:
three bounded-qualified and seven partial/open. There is no automatic campaign
or successor source audit.

The conservative existing local iteration passes all 75 CTest entries without
failures, disabled tests or skips, including 459 Python controls (ten new static-
teardown checker cases). Its report is local
build/validation-session/1793992862715373000-9f583f38/report.json. The unchanged
native GCC build, doctor, whitespace, local links and architecture/contracts also
pass; scoped clang-format checks pass on both new observer units. The first
follow-up build failure and unavailable private Windows symbols remain failures
in their own records. No repeated large scientific/instrument campaign obtains
the ordinary regression result.

The initial local closure receipt records those iteration results and original-
artifact hashes. Exact delivery-head/main results are retained separately under
build/p3-serial-crt-static/delivery; no main qualification follows from iteration
or head results. Mandatory complete-process CRT/UB/leak, remaining supported
callers and parallel coverage remain open; no successor campaign is selected.

## Delivery review

Review identified two test-instrument gaps. Offline symbol input now must match
the captured artifact's registered path and hash, in addition to the executable
module identity. Four new negative/positive integrity controls cover replacement,
external/unregistered files and the original registered capture. Offline replay
of the preserved native trace still attributes and releases all 150 requests;
no native production execution is added.

Read-only analysis identified possible baseline retention for an invalid initial-
observer invocation. Baseline/anchor storage now has explicit unique ownership,
and replacement allocation requires exactly one scenario argument. The revised
checked-MSVC target passes its four original instrument controls and one invalid-
invocation rejection. The static-teardown executable and engine archive remain
byte-identical. Analysis of all three observer units passes with the unchanged
repository check configuration; the initial failed analysis log is preserved.
No suppression or production repair is introduced. The delivery baseline remains
75 CTest entries, now with 463 Python controls; final results and revision/tree
identities belong to the separate exact-head/main gate records.
