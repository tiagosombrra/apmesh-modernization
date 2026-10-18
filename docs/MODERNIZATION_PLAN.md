# Technique-preserving modernization plan

Source and immutable import: see PROVENANCE.md. This repository is the working
authority; PROJECT_STATE.md records the current work item and verified results.

Current status: stages 0-2 closed for measured scope; stage 3 slice 13
(#44, PR #45) is qualified.
Head `ffdde7248564c8e072138d9673871baa4f13e217` integrated through PR #45 as main
`3e628e6445b2638ff73a51fa8bb1a9aed440647c`, preserving complete tree
`66f74c1b6d564e15a115db635a2b4856ee90a6aa` (1474 blobs). Full exact-head and
implementation-main campaigns pass: CTest 23/23, zero skips, 74 Python controls;
rebuild 117/117, snapshots 89/89, sync 73/73, adoption 53/53, copy 30/30,
curve 19/19, UV 81/81, node 7/7; actual new-unit lint, explicit formatting/
inventory and strict twice-repeated Eistute/Book regression. All nine attempted
OBJ/acceptance/rejection/incidence states, 189 CSV fields and 1,168/4,256
last-accepted triangles remain exact.

Original: 24 sweeps stop at first deleted-live-sample failure (per-case ordinals
11-28), with later ordinals/CRT retention unmeasured. Three two-endpoint sweeps
finish with 48 retained blocks each across their denied allocations; other 90
outcomes expected. Pending owned nodes and complete paired lists precede direct
nonallocating swaps and old-interior deletion. Thirty-six calibrated sweeps
deny 597 allocations, preserving both lists/nodes/samples and supporting
retry. All 78 normal full logs match original. IDs consumed before failure stay
consumed; retry uses subsequent IDs. Successful formulas, parameter/index order,
endpoint reuse and ID requests remain. Preparation changes allocation resource
behavior/peak storage explicitly, without a performance claim.

Original uses 12 pinned units plus verified lambda/two manager-context
substitutions; candidate 13 actual units. Full old Generator-TU instrumentation
is not claimed. New Debug CRT iterator metadata is consistently disabled with
actual heap/negative controls retained; previous targets stay unchanged. Valid
108-outcome and 117-outcome zero-start records are retained. Final fixtures
explicitly initialize intended nonzero manager start and retain zero/null cases;
no manager source change. C07/ADR-0014 require distinct exclusively deletable
interiors and preserve shared endpoints. Removed-sample/list observers are
invalidated on success. Curve observer publication, full AdaptCurve and full
mesh/acceptance rollback remain outside this helper. No scientific formulas,
floating-point order, policy, budgets, tolerance or verifier change. See
evidence/STAGE3_CURVE_REBUILD_CLOSURE.md.

Full stage 3 remains open with thirteen qualified slices. Next characterize
sample owner transfer and point-observer publication in Adapter/AdaptCurve,
then full adaptive retry/rollback across parameters, patch/mesh observers and
error/history/budget state, plus explicit full CLI disabled synchronization.
Paired helper commit and snapshot point-graph restoration are qualified narrow
boundaries; full AdaptCurve and whole-mesh/acceptance transactions are separate.
Remaining constructors/mutations, generic/custom sources, other helper/template/
tree/mate paths, failed-tree observer consumption/retry and full-process/parallel/
LSan/UBSan remain open. Stages 0-2 stay closed for measured scope; stages 4-11
stay pending. Doxygen undocumented-API debt stays stage 8.

Earlier delivery histories and scope limits remain in PROJECT_STATE.md,
WORKLOG.md and the unchanged evidence records. Architecture: see
`architecture/MESH_ARCHITECTURE.md` and `architecture/REFACTOR_SEQUENCE.md`.

| Stage | Scope | Completion evidence |
|---|---|---|
| 0 | Separate private repository; immutable import, provenance, audit and local quality commands | Exact source-tree import; build; tooling tests; published plan and limitations |
| 1 | Trustworthy regression and errors | Missing/empty/invalid input fails; candidate/rejected/accepted states distinguished; independent negative controls; zero coverage rejected |
| 2 | Mesh and architecture inventory | Map CRABMesh and physical/parametric mesh concepts, ownership, identity, conversions, duplicate computations and dependencies |
| 3 | Memory and lifecycle repairs | Construction/replacement/rejection/restoration/failure/repeated runs; qualified ASan/LSan/UBSan or justified equivalent; deliberate positive/negative controls |
| 4 | Portable modern C++ and build | Remove VLAs/extensions; qualify GCC/Clang/MSVC; review initialization/conversions; C++23 target qualified against C++17 reference; sanitizers enabled |
| 5 | Replace Eigen's actual subset | Fixed-size standard-library math; analytic, aliasing and differential tests; point/derivative/curvature/mesh/acceptance regressions; remove vendored Eigen afterward |
| 6 | Integrate CRABMesh responsibilities | Library plus thin CLI, explicit context, reduced globals; consolidate genuine duplication; preserve 2D/3D mapping and algorithm sequence |
| 7 | English identifiers and interfaces | Classes/functions/variables/files/comments/messages translated in batches; terminology map; versioned compatibility for configs/reports/CLI |
| 8 | Doxygen and architecture documentation | Ownership, domains, units, orientation, failures and article correspondence documented; generated pages reviewed; warnings resolved |
| 9 | Measured efficiency | Correct clocks, repeated comparable profiling; prove improvements without reduced coverage or changed criteria |
| 10 | Integrated qualification | Same revision passes memory, regression, portability, documentation, negative inputs and supported serial/OpenMP coverage; MPI separately qualified |
| 11 | Freeze modernized baseline | Identified reproducible release with inputs, commands, toolchain, outcomes, limitations and advisor-ready engineering/scientific change ledger |

English, tests and contracts accompany each touched component; stages 7 and 8
are comprehensive closure reviews. Stages 3/4 may alternate to unblock memory
tools, with one active work item at a time. No broad rewrite before stage 2.

## Mandatory stage closure

Every stage ends with an audit and regression before it can be marked complete:

1. Recheck remote main, branches, PRs and checks for concurrent work.
2. Review the code delta, scientific invariants, contracts and documentation.
3. Challenge coverage with independent positive and deliberately broken controls;
   inspect accepted, rejected, retry and rollback evidence where applicable.
4. Run the required regression on the exact delivery revision. Retain commands,
   source/input/executable identities, results, failures and coverage limits.
5. Keep the stage open when a required gate fails or lacks observations. Fix the
   cause without weakening the assertion or silently replacing its oracle.
6. Integrate only when required gates pass, then validate main again. Update the
   state and evidence before beginning the next stage.

This closure rule was explicitly requested by the user on 2026-10-15 Fortaleza.
It reduces the chance of unnoticed errors; it is not a claim of exhaustive proof.

## Test program

- Analytic geometry: curves, patches, derivatives, area, normal and curvature.
- Fixed-size linear algebra: dimensions, multiplication, transposition, aliasing,
  singular/degenerate cases and numerically difficult examples.
- Ownership/connectivity: valid indices, identity, orientation, observer lifetime,
  adjacencies and invalidation of derived caches.
- Shared boundaries: every incidence, reversed orientation and non-manifold
  junctions; a zero-comparison report is unmeasured, never a positive result.
- Adaptation: accepted/rejected candidates, rollback, retry and stopping traces.
- Inputs/outputs: absent, empty, malformed, invalid configuration, unwritable
  output; no success with an empty mesh caused by a failed input.
- Independent mesh checks and intentionally corrupt fixtures to test checkers.
- Memory: leak controls, undefined behavior, repeated rebuilding and peak memory.
- Determinism: repetitions and serial/OpenMP under explicit comparison budgets.

Do not replace scientific regression with golden byte counts alone. Separate
archived publication artifacts from executable accepted-state outcomes. Store
failed cases, not only successes. Large campaigns stay local; retain compact
reports and hashes in Git.

## Architecture and dependency direction

Inventory before abstraction: geometry and numerical primitives; topology and
mesh ownership; boundary adaptation; existing CRABMesh interior generation;
adaptive orchestration; independent evaluation and IO; thin CLI. Dependencies
must point toward stable geometry/data contracts. Geometry must not perform
process-level IO. Avoid a universal mesh class or gratuitous interface layers.

The target is no mandatory third-party production dependency for serial runs.
Compiler, CMake, Python test tooling, Doxygen and analyzers remain development
tools. MPI/OpenMP are optional and reported separately. Preserve license and
authorship records when integrating components.

## Automation rollout

Use EditorConfig, explicit whitespace repair, clang-format, selective clang-tidy,
CTest, compilation databases, local sanitizer campaigns and Doxygen. Enforce
rules on changed code in reviewed batches; inventory legacy debt without hiding
it behind disabled checks. Never auto-apply semantic modernization fixes.
No paid Actions, hosted workflows or dependency auto-updaters are configured.
Details, commands and primary-source rationale: QUALITY_AUTOMATION.md.

## Active stage 3 slice 14 (#47): serial adapter sample publication

The two serial Adapter construction tails are byte-identical. Original strict
sweeps stop at first parameter value/list-node mutation in 27 cases; later
ordinals and their CRT retention are unmeasured. Three separate retention-only
sweeps reclaim reachable partial original state and finish with 32 retained
blocks each across their denied allocations, without a rollback/retry claim.
Other 58 of 88 original outcomes are expected.

Both methods now delegate their unchanged captured points and selected parameters
to the same actual production helper. Pending unique nodes, parameters, cache
changes and output lists are prepared first. A scope-success guard commits after
return-list construction succeeds; failure during an allocating return move
keeps parameters/cache unchanged. Prepared map nodes merge without allocation,
existing cache entry nodes stay stable, parameters swap and owners release.
Borrowed inputs/cache nodes stay alive. Endpoint scalar/adjacency copy, cached
reuse, closed aliases, alias overwrites, sample values/order and successful ID
requests remain exact. Consumed IDs and evaluator scratch are not rolled back.

Candidate gates pass: CTest 24/24, zero skips, 74 Python controls; samples 88/88,
702 denials across 30 positive sweeps, including an explicit actual MSVC
list-move allocation control. Optional NRVO is disabled consistently only for
the new target, alongside non-debug iterator metadata in Debug CRT; actual heap
and negative controls remain. All 54 complete normal original/repaired logs match.
Analytic curved geometry, source/cache borrowing, cache entry identity, endpoint
adjacency/scalars, return-edge preservation and retry are checked. Prior rebuild
117, snapshots 89, sync 73, adoption 53, copy 30, curve 19, UV 81 and node seven
outcomes all pass. Actual new-unit read-only lint, explicit formatting/inventory
and exact twice-repeated Eistute/Book regression pass across nine attempted
states, 189 CSV fields and 1,168/4,256 accepted triangles. Head/main gates remain.

Original comparison uses 14 pinned units and the unchanged verified tail from
both serial methods, candidate 15 actual units; full old Adapter/Generator
translation units are not instrumented. Valid 87-case preliminary reports remain
retained; final 88-case coverage adds the explicit move-allocation control.
The caller retains collective lifetime authority for newly created returned
nodes; cache/source nodes are borrowed. Upstream sorting/parameter selection,
evaluator scratch, later Generator point publication and full Adapter/AdaptCurve/
mesh rollback stay outside this helper. Endpoint adjacency observers stay copied,
without owning their elements. Full-process/parallel/LSan/UBSan stay open.

Classification: ownership/exception-consistency defect repairs plus verified
engineering consolidation. Preparation changes allocation timing/counts/bytes/
peak storage, without a performance claim. No formula, numerical order, policy,
budget, tolerance, verifier or acceptance/stopping change. Full stage 3 stays
open. See evidence/STAGE3_ADAPTER_SAMPLES.md and ADR-0015.
