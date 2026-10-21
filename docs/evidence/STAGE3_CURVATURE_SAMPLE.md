# Stage 3 slice 30: automatic curvature sample lifetime

Status: candidate checks pass; exact published-head and post-merge full gates pending.
Entry main: `50ba13492de0bae355a158a254be8621d24a5518`.
Classification: resource-lifetime/invalid-cast defect repair, with engineering-only
extraction, fixed bounded scratch storage and local spelling/diagnostic migration.
No scientific proposal. Stage 3 remains open; stages 4-11 remain pending.

## Cause and repair

CalculateKaMedioPatch allocated each PointAdaptive and immediately overwrote its
pointer with a local value address. The heap objects became unreachable. Actual
Debug CRT measurements retain 4/9/17/25 blocks (160/360/680/1000 bytes) per normal
call, or 12/27/51/75 blocks over three calls. These are real retained objects,
not an inferred whole-application leak count. All three measured surfaces agree.

The pointer then underwent a PointAdaptive-to-NodeAdaptive downcast even though
the object was not a NodeAdaptive and CurvatureAnalytical accepts PointAdaptive.
Automatic PointAdaptive values now pass directly to that API. No owner escapes
and ordinary/exceptional scope exit releases all local values. No shared owner,
production callback seam or new numerical implementation is introduced.

The original points-sized VLA only used a prefix of at most 25 elements. The new
standard-library array has 25 automatic entries. As before, only the populated
prefix is read; no uninitialized unused entries are consumed. Counts below 4
return zero; counts above 25 perform no sampling and return zero divided by the
requested count. Between-level counts retain their historical sample set and
requested-count denominator. No sample validation or selection policy is added.
Unbounded old stack reservation for extreme positive counts is removed; original
INT_MAX execution is unmeasured. The existing early diagnostic is translated.

## Preservation and measured evidence

A strict independent token audit normalizes only these storage/cast/spelling,
comment and diagnostic edits. All sample positions/order, branches, fallback
threshold, arithmetic, accumulation and denominator must match. Four deliberate
mutations (denominator, threshold, position and accumulation ordering) are rejected.
Area/radius helper bodies remain byte-identical. The small sampler unit compiles
with MSVC C++17; other historical numerical VLAs remain stage 4 debt.

Candidate results: 725 expected instrument outcomes; 330 sampled forward/inverse
exception positions and 342 measured zero-allocation operations. Actual ASan UAF,
Debug CRT leak and denied-allocation controls are required. ASan leak detection is
disabled; its clean exit alone never establishes leak freedom. Debug CRT measures
normal and exceptional lifetime independently, with the explicitly qualified static
runtime. Integer extremes and threshold gaps are also exercised on the repaired path.

The same 725-case original battery has 367 failures and 358 expected outcomes:
24 normal CRT retention failures, one CRT aggregate retention failure and 342
zero-allocation failures. Those old allocation-denial cases abort before terminal
retention measurement; no successful unwinding or later observation is inferred.
The original MSVC-only adapter changes only VLA extent to 25; its overwritten
allocations, invalid downcasts, formulas and control flow remain intact.

Ninety paired GCC C++17 invocations compile the actual original VLA sampler and
actual repaired unit, covering plane, saddle and convex control nets; all threshold
regions, repeats and bounded out-of-range counts. Ordered forward/inverse arguments
and scalar IEEE bits agree exactly. Planar curvature is independently required to
be zero. Observed correspondence does not make the original invalid cast defined.
Compact case/log identities and negative findings are retained in
[curvature_sample](stage3/curvature_sample/). Full raw local logs remain under build.

## Required delivery gates

Exact published-head and implementation-main must each pass build, CTest 42/42
with zero skips and 74 Python controls, all prior 25 memory batteries plus this
new battery (26 batteries/2677 expected outcomes), all 1040 retained scalar
sequences, 90 paired sampler traces and 48 actual/controlled charge traces,
selected lint, explicit format/whitespace, fresh architecture inventory and exact
repeated Eistute/Book accepted/rejected OBJ/incidence/boundary/acceptance and
independent CSV comparisons. Protected production/tool/test/build/input/contract
identities, complete Git tree and all command/case/raw-child log hashes must match.
No merge precedes those exact-head gates; main is then requalified. Unavailable,
failed or zero-observation gates block integration and bounded closure.

```powershell
. ./build/local-env.ps1
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
python tools/audit_curvature_sample.py --original-root build/s30-original --candidate-root .
python tools/qualify_curvature_sample.py --asan build/s30qa/RelWithDebInfo/curvature_sample_probe.exe --crt build/s30qd/Debug/curvature_sample_probe.exe --runtime '<qualified MSVC runtime>' --output '<new output directory>'
python tools/compare_curvature_sample.py --original build/s30og/curvature_sample_probe.exe --candidate build/s30qg/curvature_sample_probe.exe --original-root build/s30-original --candidate-root . --output '<new output directory>'
```

## Closure inventory and limits

Code: one actual sampler unit, explicit automatic values/storage, no invalid
sample downcasts; actual caller links that unit. Tests: instrument controls,
exception/zero-allocation coverage, independent token mutations, actual numerical
pairs and required full regression. Contract C24 and fresh architecture inventory
record the domain and unchanged unusual denominator behavior. Preliminary missing
probe dependencies and observer-bound failure are retained, not relabeled success.

No formulas, floating-point order, tolerances, budgets, synchronization,
quadtree/templates, advancing-front reconstruction or adaptation/acceptance/stopping
policy is changed. No performance, scientific superiority or C++23/Eigen-removal
claim. Samples borrow a live patch and exclusively mutate its existing numerical
scratch through actual methods. Arbitrary overriding callbacks, solver-internal
exceptions, full cache/metadata rollback, malformed loaders, partial writer output,
other helper/constructor roots and full-process/parallel/LSan/UBSan remain open.
The next single audit after bounded closure is remaining estimator helper and
control-construction lifetime; stage 3 itself is not closed by this repair.
