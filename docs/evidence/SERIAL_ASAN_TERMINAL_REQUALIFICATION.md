# Portable terminal observer requalification and fixed contexts

Classification: engineering-only test instrumentation/configuration repair.
Production, original fixtures, Python terminal oracles, inputs and scientific
policies are unchanged. Entry is draft PR #139 head
`b35ef8fc17e1cb68a45686423bdf75eae2f74ee8`, based on PR #138 main. This contributes
bounded terminal observations to S3-01/05/08/09, without closing Stage 3.

## Demonstrated blocker and repair

The [first failed qualification](SERIAL_ASAN_TERMINAL_OBSERVER.md) remains intact.
The repaired generated fixture replaces only its unwind control's unused
make_unique expression with an external SubMesh factory. The factory explicitly
calls ordinary operator new, constructs the actual SubMesh in that storage and
releases the storage if construction throws. The successful control holds the
returned object in unique_ptr and checks its live empty native mesh before normal
destruction. This preserves actual allocation/ownership instead of relying on an
allocation expression that may be eliminated. It is test-only instrumentation.

The original typed fixture stays unchanged. Reversible preparation changes only
its allocation-observer include and that one control allocation expression. Its
exception payloads, catch, attempts==1/denied==1/unwind_attempts==1 assertion,
completion markers and CLI/library oracles remain unchanged. Five preparer tests
check exact restoration and reject source, interception and allocation-site drift.

An initial instrumented build with the explicit factory still failed before any
directed context. The new counters were calls=0, uncaught=-1, attempts=0, denied=0.
The compiler had emitted C4530, and all 74 actual commands lacked /EHsc: the global
CMAKE_CXX_FLAGS=/fsanitize=address setting had replaced the usual exception flags.
The factory passed outside unwinding, but its destructor control was not reached
during unwinding. That failed executable, commands and logs remain preserved in
build/p3-msvc-asan-terminal-unwind; no directed case was admitted from it.

The standalone test target now requires /EHsc explicitly and promotes C4530 to an
error. A separate build uses identical native test/generated sources with the
corrected exception configuration. All 74 compiler groups carry /fsanitize=address,
/EHsc and /we4530. These represent all 73 production units plus allocation
instrumentation; the actual CLI main body is embedded under a test-only name.
No warning is suppressed and no numerical/compiler arithmetic policy changes.

## Requalification and fixed observations

The qualified executable is retained at
build/p3-msvc-asan-terminal-ehsc/application/RelWithDebInfo/terminal_observer_probe.exe,
SHA-256 `a6fe1fa2f933261ebe5ba21e0a011d8bc58edcbb575e4668e8185c6b612e1455`.
The original standalone configure/build recipe remains valid; the target itself
now supplies the required exception semantics even when global flags are set.

All four prerequisites pass their unchanged ten-second caps: actual release;
deliberate real heap-use-after-free detected by ASan; live AFT selection/exclusion/
disabled-selector and independent allocation denial; and all nine typed payload
rows plus the actual unwind allocation control. The latter records exactly one
factory call, one uncaught exception, one allocation attempt and one denial. The
previous assertion and required completion markers pass. The original failed
artifact remains failed; it is not promoted by the corrected result.

Only then does `python build/p3-msvc-asan-terminal-ehsc/observe.py` execute each
of the five fixed contexts once, sequentially, with ASAN_OPTIONS=halt_on_error=1,
the unchanged 300-second cap and only input/output path relocation:

| Context at step 2 | Expected result and observation | Wall seconds |
| --- | --- | --- |
| SP-09 Book patch 0 | CLI status 1; one false-result attempt; exact typed diagnostic once; zero unwind allocations; checker refuses to classify the failed prefix as successful generation. | 13.2930 |
| SP-09 Eistute patch 0 | CLI status 1; two attempts; same exact terminal/failed-prefix oracles. | 11.7186 |
| SP-09 Eistute patch 1 | CLI status 1; two attempts; same exact terminal/failed-prefix oracles. | 11.8898 |
| SP-10 Book patch 0 | Harness status 0 after typed catch; one attempt; 28 owned patch observers detached; zero remaining owner links/samples/allocations. | 13.1438 |
| SP-10 Eistute patch 1 | Harness status 0 after typed catch; two attempts; one prior changed patch; four owned patch observers detached; zero remaining owner links/samples/allocations. | 11.5540 |

No context has an unexpected ASan diagnostic. All prescribed payload, attempt,
classification, live external-Geometry, sample cleanup and nonallocating owner
teardown assertions pass. CLI status 1 is the expected terminal control outcome,
not successful mesh generation. There is no recovery, retry-after-exception or
same-Generator reuse claim. No context or native scientific campaign is added.

## Delivery and limits

The [compact record](stage3/serial_asan_terminal_requalification/summary.json) and
local build/p3-msvc-asan-terminal-ehsc seal bind inputs, source, runtime, commands,
compiler flags, executable/PDB, all control/context logs, exact reversibility and
the two preserved failed qualifications. Scoped read-only analysis passes on the
new observer C++ units/headers; legacy diagnostic debt is outside that scope.

Require exact-head/main 75 CTest entries without failures/skips and 385 nested
Python controls, formatting/whitespace, source/input/prior-evidence identity,
architecture/contracts and staged/remote audits. Reuse the unchanged prior GCC
nine-state scientific reference: 45 exact artifacts and 123 boundary comparisons.
Do not repeat the five ASan contexts or rebuild the unchanged probe for delivery.

The canonical production executable is not rebuilt here. Earlier natural ASan
observations retain their actual flags/artifact scopes and do not establish
exception unwinding. This corrected full-caller observer qualifies only the five
named terminal contexts. Complete-process CRT/LSan/UBSan, same-Generator reuse,
broader mutation/foreign-owner domains and parallel qualification remain open.
Stage 3 retains three bounded and seven partial/open closure rows. Next bounded
P3 dependency: qualify the complete-process CRT observer with actual release,
deliberate retained-storage and allocation-hook controls before fixed cases.
