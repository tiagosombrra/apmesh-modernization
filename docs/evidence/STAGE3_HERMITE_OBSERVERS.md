# Stage 3 slice 36: completed Hermite observer retirement

Classification: behavior-changing lifetime defect repair; no scientific change.
Status: candidate, full exact published-head and post-merge qualification pending.
Preflight: 53/53 CTest, zero failures/skips, including 74 Python controls.
Source base: `6669a29e03e868ecaa781e6da2a5299a19ddeae5` (PR #97 audit).

## Boundary and implementation

The original [caller/source audit](STAGE3_HERMITE_OBSERVER_AUDIT.md) retains
25 literal constructions and nine actual expired-observer ASan consumptions.
Only the completed PatchHermite destructor declaration/body changes in production.
It invokes the existing RemovePatchObservers(this) for each current nonnull
borrowed curve. That existing stable erase removes every matching pointer and
preserves all other values in order, including duplicate foreign pointers/nulls.
Repeated current slots are harmless. The patch does not own or delete the curves.
All 486 other production files match the immutable 488-file source archive.

Current borrowed curves must remain live through patch destruction. Existing
Geometry patch-before-curve destruction and temporary/swap move assignment are
reused without modification. Empty default and initialized detached-copy topology
have no observers to remove; null current slots are ignored without numeric reads.
No constructor, payload initialization, formula, floating-point order, public
signature/layout, synchronization, tolerance, budget, front/template or
adaptation/acceptance/stopping policy changes. See C29 and ADR-0037.

## Focused observations

The [compact report](stage3/hermite_retirement/focused.json) retains executable,
raw-log and original-input identities, all 153 candidate outcomes and original
failures. The standalone tests/hermite_observer_memory recipe compiles eighteen
actual production units plus the probe under explicit GCC/MSVC C++17. MSVC ASan
and static Debug CRT use the established runtime/iterator/NRVO probe settings.
Compiler/Eigen diagnostics remain visible; no warning is suppressed.

The focused candidate passes 153 expected outcomes. Contracts cover 576 retirement
observations across three incidence layouts, two surfaces, first/middle/last
retirement, empty/populated prefixes and all sixteen constructor flag combinations.
Nine modes actually consume all surviving nonnull patch IDs. Five Geometry modes
measure destruction, move construction, populated move assignment, self move and
old-destination curve use during patch destruction. Empty/default/detached/null-slot
cases preserve other registrations. Twenty-two operations run with allocation
denial enabled and make zero allocation attempts. A separate real allocation is
denied; independent actual ASan UAF, CRT leak, prefix-count and same-count order
corruption controls work. Every defined CRT case retains zero blocks/bytes.

Running the same stronger battery against immutable original production preserves
125 failed qualification outcomes and 28 other expected outcomes. The original
report remains failed; nine consume modes reproduce actual heap-use-after-free.
Only three empty-topology operations meet the original nonallocation/observer
contract. Original zero retention is not a valid-observer result.

Six nonempty live original/candidate trace pairs per GCC/MSVC ASan/static CRT
instrument agree: eighteen pairs, 108864 scalar-bit observations, including
Parameterize, Qu, Qv, Quu, Quv, Qvu and Qvv plus patch IDs and live incidence.
Distinct-curve plane/bilinear fixture values also match independent analytic
expressions within 1e-12. Repeated-slot fixtures measure lifetime and preservation,
not geometric validity. Registrations are explicitly cleared while patches remain
alive for original terminal comparison; retirement is tested separately.
Eight independent source mutations (removal, target, null branch, iteration,
allocation, numeric formula, control copy and direction default) are rejected.
The existing detached-copy guard normalizes only this exact separately checked
destructor delta and still rejects all eight earlier mutations.

Focused measurements precede explicit whitespace-only formatting of the new
probe. The first MSVC pair attempt produced no child output because the pair
executor omitted an explicit runtime PATH. That attempt is retained locally in
build/s36-focused-pairs-asan and disclosed in focused.json. The executor now
requires --runtime; the six previously uncompleted ASan and six CRT pairs passed.
The already completed 153-case memory batteries and GCC pairs were not repeated
to repair that preparation error. Full delivery campaigns must rebuild all six
probes from the exact formatted revision; no binary equality across builds is
claimed. The formatter changed only the new probe; its change exit code stopped
the shell before configuration, which was then continued explicitly. The focused
quality process reached tidy coverage: 1 files with the unchanged checks/filters;
PowerShell returned a nonzero wrapper status after formatting native stderr. That
wrapper result remains retained. Exact-head direct-subprocess exit codes are
required before treating the delivery static-analysis gate as passed.

## Commands and required delivery

```powershell
cmake -S tests/hermite_observer_memory -B build/s36qg -G Ninja -DCMAKE_CXX_COMPILER=C:/msys64/ucrt64/bin/c++.exe -DCMAKE_MAKE_PROGRAM=C:/msys64/ucrt64/bin/ninja.exe -DCMAKE_BUILD_TYPE=Release
cmake -S tests/hermite_observer_memory -B build/s36qa -G "Visual Studio 17 2022" -A x64 -DAP_MESH_HERMITE_OBSERVER_ASAN=ON
cmake -S tests/hermite_observer_memory -B build/s36qd -G "Visual Studio 17 2022" -A x64
cmake --build build/s36qg --parallel 2
cmake --build build/s36qa --config RelWithDebInfo --parallel 2
cmake --build build/s36qd --config Debug --parallel 2
python tools/qualify_hermite_observers.py --asan build/s36qa/RelWithDebInfo/hermite_observer_probe.exe --crt build/s36qd/Debug/hermite_observer_probe.exe --runtime "C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64" --output build/s36-new-memory
python tools/audit_hermite_observers.py --candidate-root .
```

Build equivalent original probes with AP_MESH_HERMITE_OBSERVER_SOURCE_ROOT
pointing to a Git-verified archive of the source base. Then invoke
compare_hermite_observers.py with --original, --candidate, --original-root,
--candidate-root, --runtime and a new --output directory for each instrument.
Do not overwrite completed report directories or relabel original failures.

Two required CTest registrations preserve the prior 51 tests, for 53 total and
74 existing Python controls. Delivery requires all prior 31 memory batteries/
3157 outcomes plus this 153-case battery (32/3310 total), 1040 retained scalar
sequences, twice-repeated exact Eistute/Book accepted/rejected/OBJ/incidence/CSV
traces, architecture/contracts, local quality, environment/checkout identities,
and fresh remote main/branch/PR/status/check audits. Required gates must pass on
the exact published head before merge and again on main. Candidate focused
results alone do not qualify the slice or close Stage 3.

## Remaining obligations

Failed Hermite construction can publish observers without completing an object;
its derived destructor is not invoked. Constructor rollback remains unqualified.
Failed consuming adoption and fresh-curve caller preparation require their own
allocation/failure measurements. Copied/foreign observer lists and arbitrary
current-curve rebinding, curve-first destruction, SubMesh observers, complete
loader/adaptive rollback, broader models/external clients and full-process/
parallel/LSan/UBSan remain open. Configured article traces do not execute every
Hermite source root or demonstrate a current CLI failure. Next work must select
one root from the finite closure inventory after this candidate is qualified.
Stage 3 remains open; stages 4-11 remain pending.
