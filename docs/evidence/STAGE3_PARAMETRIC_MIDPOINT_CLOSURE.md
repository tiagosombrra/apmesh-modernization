# Stage 3 slice 7 closure

Head `4781226726bd36d7ff64afb273ed53c37630b6f3` integrated through PR #27 as main
`61dc86ecaeede57ec838a5bb754f237b2013085a`, preserving complete tree
`ac04e95600a403e12952fb68f84a5e6c5a8abaa6` (889 blobs). Exact-head and
implementation-main complete campaigns pass: CTest 17/17, zero skips, 74 Python
controls, UV 81/81, node 7/7, six-unit lint, range formatting, inventory and
strict repeated Eistute/Book regression. All nine states, acceptance/rejection,
measured incidences, 189 CSV fields and 1,168/4,256 accepted triangles remain
exact. The original fails ten replacement sweeps; all 30 measured denials now
preserve cache/caller state and permit successful retry. Original/repaired
normal traces and successful allocation counts match.

The midpoint and normalized length prepare locally before commit. Old-cache
destruction is deliberately delayed; old/new caches coexist briefly, without
an address-reuse or peak-memory promise. Arithmetic, oriented intervals,
integration/bisection tolerances/stopping and null/fallback policies remain.
Curve evaluation scratch stays mutable. Three direct numerical operation
scopes observe zero allocations, explicitly leaving their internal allocation-
failure coverage unmeasured. This is an exceptional-exit defect repair, not a
scientific change. See ADR-0008 and STAGE3_PARAMETRIC_MIDPOINT.md for
reproduction and repair.

## Explicit closure audit

- Code: one production implementation prepares and commits the two cached
  values; the header defines failure stability and successful observer
  invalidation. Delayed destruction and briefly overlapping cache lifetimes
  are explicit. No input, vendor, formula, solver, policy, verifier or public
  signature changes. Historical source, licenses and attribution remain.
- Tests: implementation head and main pass the complete 17-test inventory,
  zero skips, 74 Python controls, 81 UV and seven node instrument cases.
  Eleven normal edge variants, five analytic curve samples, signed integrals,
  inverse midpoint and all 30 calibrated denials are measured. Previous
  deliberate UAF/shared deletion, leak and denial controls retain their intended
  diagnostics. The ten original failures remain; the other 71 control outcomes,
  including deliberate invalid controls, are as expected.
- Contracts: C11 limits the cache transaction and mutable curve scratch.
  Inventory remains 123 C++ files, five CMake inputs, 22 contracts and 96 anchors.
  Zero observed allocations in three direct curve scopes are observations;
  internal allocation-failure qualification remains unmeasured.
- Documentation: state, plan, worklog, quality commands, architecture boundary,
  ADR-0008 and this consolidated record preserve completed scope and limitations.
- Scientific scope: original/repaired normal traces and allocation counts match.
  All nine article states and acceptance/rejection, positive shared-incidence
  coverage and 189 named CSV fields match entry and head/main. Accepted steps
  stay 0/1; rejected Eistute 2/3/4 and Book 2/3 remain visible. Final accepted
  triangles remain 1,168/4,256. No tolerance or acceptance rule was relaxed.
- Failure/coverage inventory: original allocation failure loses its cache at
  the first denied ordinal in all ten sweeps. The repaired case preserves cache
  identity/geometry, normalized length, caller/edge state and successful retry.
  Scoped CRT retention is zero; full-process leak freedom is not claimed.
  Other curve failure and shared sample/initialization/rollback scopes remain.
  Doxygen's undocumented-member failure stays stage-8 debt.

## Retained reports and documentation-only qualification

stage3/parametric_midpoint/head_qualification.json and main_qualification.json
retain full implementation campaigns and raw-report/log identities. The common
source_identities.json records every qualified input. Original failed cases,
normal traces, the 460-blob snapshot map and actual toolchains are retained.
Verbose CTest/JUnit and large raw instrument logs remain local with hashes;
they are not described as fully archived files.

This documentation-only follow-up preserves every qualified production/tool/
test/build/input/contract identity. Its complete published Git tree and exact
working bytes must match; CTest 17/17 with zero skips and 74 controls, inventory
and unchanged-input checks must pass on its exact head and again on final main.
Full numerical/instrument qualification already passed on unchanged compiled
inputs at the exact implementation head and main. Final documentation hashes,
tree and log identities are recorded on the closure PR and issue #26 to avoid a
self-referential repository commit. No hosted checks or Actions are configured.

## Remaining work

Full stage 3 remains open with seven qualified slices. Next characterize other
curve mutation/constructor/setter failures, then shared sample ownership,
initialization and rollback. General observers, other helper/template/tree/mate
paths, failed-tree observer consumption/retry and full-process/parallel/LSan/
UBSan qualification remain open. Stages 0-2 stay closed; stages 4-11 stay pending.
