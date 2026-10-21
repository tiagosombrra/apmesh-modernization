# Stage 3 slice 31: Bezier construction lifetime

Status: candidate checks pass; exact published-head/main gates pending.
Entry main: `b908ecd384dea4877186fb8cb167444da5c2173d` (implementation #82, closure #83).
Classification: resource-lifetime and failed-constructor observer defect repairs,
with engineering-only sharing of the existing scope. No scientific proposal.
Stage 3 remains open; stages 4-11 remain pending.

## Root causes and repair

The sixteen-point constructor created four curves directly inside raw observer
vector insertions. If insertion failed, the just-created curve had no owner;
later constructor failures could also lose already inserted curves. A failed
most-derived constructor does not run its own destructor. The original measured
first denial at ordinal 4 retains three normal blocks/544 bytes. Four local unique
owners now cover all curve construction, insertion and original matrix operations.
Only successful completion releases them to the established external owner.
No reserve, reordered construction, shared ownership or numerical rewrite is used.

The curve-based constructor borrows live Bezier curves and appends this to their
observer vectors before it finishes. A later allocation failure destroyed the
incomplete patch but left expired observers. The selected original ordinal 6 has
zero terminal retained heap bytes yet fails the live prefix check. Resource
retention alone would miss that defect. A scope now restores exclusively appended
suffixes on any C++ constructor failure and commits only after matrix construction.
Existing parents/null markers/order remain; vector capacity is not rolled back.

The identical four-curve scope is shared with charge estimation. Its original
wider construction/evaluation/adoption interval remains intact; a failed
constructor can trigger both scopes idempotently. Neither scope dereferences an
expired pending patch, deletes a borrowed curve or allocates during cleanup.
Borrowed curves and their prefix must remain live, with exclusive publication.

## Preservation and actual evidence

A token audit compares the complete original/repaired Bezier implementation,
normalizing only storage/factory/scope edits, includes/comments/spacing. Public
class layout/API, all control/curve/direction order and every matrix/expression
and remaining method token match. Scope placement must precede publication and
cover the complete constructor. The shared scope and charge caller are token-
identical after namespace qualification. Four independent control-order, matrix,
direction and early-commit mutations are rejected.

The new candidate battery passes 71 expected outcomes, 32 complete allocation sweeps
and 348 actual denials. All observed attempts equal ordinal+1 on failure, proving
no measured normal-block allocation during unwinding. Borrowed prefix values are
checked before fixture destruction; zero terminal retention is measured after
its owners are destroyed. This does not assert zero retained vector capacity
while borrowed curves are still alive. Normal cases bundle all 16 direction masks
and repeated calls rather than reporting each as an unrelated top-level test.

All 32 original sweeps fail and stop at their first leak or observer mismatch;
39 other expected outcomes pass. Only 208 original denials are observed, so later
ordinals are unmeasured. Full raw logs and executable/source identities remain
local; compact case/log hashes are retained in
[bezier_construction](stage 3/bezier_construction/). Actual ASan UAF, independent
Debug CRT leak/denial and an extra-observer negative oracle are required. ASan
leaks are disabled; Debug CRT supplies retention. Separate ASan /MD and Debug
/MTd targets use matching units and the previously qualified iterator ABI.

Thirty-two MSVC ASan/CRT normal trace pairs and 16 GCC C++17 pairs agree exactly.
The GCC pairs execute 512 constructors per executable and compare 13824 scalar
observations and 8192 control-coordinate/ID records, plus direction flags and live
incidence. Repeated curve slots are lifetime guards, not geometric validity.

## Remaining estimator helper audit

InterpolateControlPointsCurve has automatic point values and a returned owning
vector. No production call site was found beyond its definition; no additional
heap-lifetime defect was established. Its singular/out-of-range diagnostics fall
through into arithmetic; no numerical-domain policy change is made here.
CalculateAreaTriangleMedioRad uses automatic scalars; zero-curvature/nonfinite
semantics are preserved and are not newly qualified scientific behavior.
CalculateAreaPatch initializes quadrature tables only for 3 and 4; its five-point
case is empty and other positive counts may read uninitialized data. The sole
production call uses 4. Its VLAs and unsupported-count domain belong to the
separate portability/domain-validation work; they are retained as unresolved
static findings, not a demonstrated current serial failure or successful test.

## Required delivery and closure inventory

Exact published head and implementation main must each pass 43 CTest/74 Python,
zero skips, all prior 26 batteries plus this one (27 batteries/2748 expected outcomes),
1040 retained scalar sequences, 90 sampler pairs, 48 charge pairs, 16 GCC constructor
pairs, 32 MSVC constructor pairs, selected lint, explicit changed-line formatting,
fresh architecture inventory and exact repeated Eistute/Book accepted/rejected
OBJ/incidence/boundary/acceptance and independent CSV comparisons. All protected
production/tool/test/build/input/contract identities and complete command/case/
raw-child log hashes must match. No required gate is removed or relaxed. Full
numerical regression is scheduled before the long allocation sweeps for earlier
feedback, using the same commands and limits. Main is requalified after merge.

```powershell
. ./build/local-env.ps1
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
python tools/audit_bezier_construction.py --original-root build/s31-original --candidate-root .
python tools/qualify_bezier_construction.py --asan build/s31qa/RelWithDebInfo/bezier_construction_probe.exe --crt build/s31qd/Debug/bezier_construction_probe.exe --runtime '<qualified MSVC runtime>' --output '<new directory>'
python tools/compare_bezier_construction.py --original build/s31og/bezier_construction_probe.exe --candidate build/s31qg/bezier_construction_probe.exe --original-root build/s31-original --candidate-root . --output '<new directory>'
```

Code, tests, contract C25, the shared scope, ADR 0032 and this audit cover the same
construction boundary. Failure findings and coverage limits remain explicit.
Successful point-based callers must still adopt all four curves; failure after
constructor return is not made atomic. The harness owns fresh curves and retires
successful registrations while patches are alive. Ordinary completed patch
observer deregistration, other loader/Model/copy/cache/caller roots, metadata/
acceptance rollback and full-process/parallel/LSan/UBSan remain open. The next
single audit after this delivery is completed patch observer lifetime and caller
curve/patch destruction ordering. No performance, C++23, Eigen-removal or
scientific superiority claim follows.
