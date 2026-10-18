# Stage 3 slice 9 closure

Head `6bda90b91406b0aed79ba6582bf820ea40559325` integrated through PR #33 as main
`d5abb5495b28e8ec5a2b6f779c3adf173929ed04`, preserving complete tree
`d43fd3a977b725dbe7776f7adb0c7ab979dde32f` (1004 blobs). Full exact-head and
implementation-main campaigns pass: CTest 19/19, zero skips, 74 Python controls,
copy 30/30, previous curve 19/19, UV 81/81, node 7/7, one-unit selected lint,
probe/range formatting, inventory and strict repeated Eistute/Book regression.
All nine attempted states, measured shared incidences, acceptance/rejection,
189 CSV fields and 1,168/4,256 accepted triangles remain exact.

The base pointer-taking constructor now copies parameter values in independent
list nodes, preserving sampled-point correspondence in initialized parametric,
Bezier and Hermite copies. The original has 12 populated normal failures and
six populated calibration failures before denial; its other 12 control outcomes
are as expected. Nine repaired sweeps deny all 123 calibrated allocations with
unchanged source values/nodes/caller objects and complete successful retry.
All 18 normal numeric traces and six empty-sequence full traces match original.
Five populated parameter nodes are intentionally added per copy in these fixtures;
allocation counts are observations, not portable constants or performance claims.

Parameter values and observer containers are independent; physical sample/patch
objects remain borrowed. Both curve destruction orders are qualified only while
their actual external owners remain alive. No source consistency validation or
repair, implicit copying or clone-publication guarantee is added. Scientific
expressions, evaluation order and adaptation/acceptance/stopping policies remain
unchanged. See STAGE3_CURVE_COPY.md for reproduction; C07 and ADR-0010 define
the boundary.

## Explicit closure audit

- Code: one member initializer and two header comments define initialized,
  non-null pointer-taking copy behavior. No function type/class layout change.
  The new probe links nine real production units; the old collection target
  stays seven units with unchanged compiler/sanitizer/link option values.
  No formula, ordering, solver, input, vendor, threshold, policy, license,
  attribution or historical-source change. Extra parameter-node allocations
  and corrected populated-copy state are explicit behavior/resource changes.
- Tests: full implementation head/main pass CTest 19/19, zero skips and 74
  Python controls, copy 30/30, curve 19/19, UV 81/81 and node 7/7. Three types
  cover empty/forward/reverse sequences, five analytic position/derivative
  samples, signed arcs and five actual copied parameter/sample pairs per
  populated case. Independent list mutation, both curve destruction orders,
  unchanged external object state and exactly-once caller destruction pass.
  Nine calibrated constructor sweeps deny all 123 ordinals with unchanged
  source fields/nodes/objects and complete retry. Real ASan UAF, CRT leak and
  denial-hook controls respond; all prior negative controls remain required.
- Contracts: C07 limits independent container values/nodes versus borrowed
  physical objects and source preconditions. Inventory remains 123 C++ files
  (57 units, 66 headers), six CMake inputs, 22 contracts and 99 anchors.
  Lexical anchor presence is not the semantic proof. The known six-header
  cycle remains. Implicit copying and clone publication are not inferred.
- Documentation: plan, state, worklog, quality commands, architecture sequence,
  ADR-0010, original diagnostics and compact reports retain the current scope.
- Scientific scope: all 18 original/repaired normal numeric traces and six
  empty-copy full traces match. Populated sequence state intentionally changes.
  Eistute/Book each repeat twice and match entry/head/main over all nine attempted
  states, positive shared incidences, zero measured position gap, acceptance/
  rejection and 189 named CSV fields. Accepted steps stay 0/1, rejected Eistute
  2/3/4 and Book 2/3 remain visible; final triangles stay 1,168/4,256. No oracle,
  tolerance, scientific rule or shared-curve policy option is weakened/changed.
- Failure/coverage inventory: 12 original populated normal failures and six
  populated normal-calibration failures remain. Original populated denial
  coverage is unmeasured because calibration fails before injection; 12 other
  outcomes, including deliberate invalid controls, are as expected. Repaired
  empty copies measure seven and populated copies 17 instead of 12 allocations;
  prior two-parameter copy controls recalibrate from nine to 11. Counts are
  measured, not portable acceptance constants. Scoped CRT retention is zero;
  full-process leak freedom and LSan/UBSan are not claimed. Clone consumer
  publication/policy integration remains static review only.

## Retained evidence and documentation-only gates

stage3/curve_copy/head_qualification.json and main_qualification.json retain
complete implementation results, commands and raw-log identities. The common
source_identities.json identifies all 512 qualified files. Original normal/
failure traces, the 460-blob map and actual toolchains are retained. Deliberate-
negative raw diagnostic and large current instrument/CTest/JUnit logs remain
byte-for-byte local with hashes; no complete raw campaign archive is claimed.

This follow-up changes documentation/evidence only. Complete remote/local Git
tree and exact working bytes, all unchanged qualified source/tool/test/build/
input/contract identities, CTest 19/19 with zero skips and 74 controls, inventory
and whitespace/diff checks must pass on its exact head and again on final main.
Full numeric/instrument qualification already passed on those same compiled
inputs at exact implementation head/main. Final documentation commit/tree/log
identities go on the closure PR and issue #32, avoiding a self-referential
repository commit. No hosted check/status contexts or Actions are configured;
absent checks are not green hosted CI.

## Remaining work

Full stage 3 remains open with nine qualified slices. Next characterize
ownership/publication around curve clones and remaining constructor/mutation
paths, then shared sample ownership, initialization and rollback. The
CloneCurveForPatch/DisableSharedCurveSynchronization consumer is reviewed
statically only; its policy integration and post-copy publication are unqualified.
Implicit copy/assignment, inconsistent/null/uninitialized sources, general
observers, other helper/template/tree/mate paths, failed-tree observer consumption/
retry and full-process/parallel/LSan/UBSan remain open. Stages 0-2 stay closed;
stages 4-11 stay pending. Doxygen undocumented-API debt stays stage 8.
