# Technique-preserving modernization plan

Source and immutable import: see PROVENANCE.md. This repository is the working
authority; PROJECT_STATE.md records the current work item and verified results.

Current status: stages 0-2 closed for measured scope; stage 3 slice 14
(#47, PR #48) is qualified.
Head `e61be31964558b2f3812d2d6341774ede96cc902` integrated through PR #48 as main
`4cc921ddf0bc5e069118540c1dd278f704abdeb3`, preserving complete tree
`93d7519b1c93222f78e95ba71f865bcb2d0e1cd0` (1597 blobs). Full exact-head and
implementation-main campaigns pass: CTest 24/24, zero skips, 74 controls;
samples 88/88, rebuild 117/117, snapshots 89/89, sync 73/73, adoption 53/53,
copy 30/30, curve 19/19, UV 81/81, node 7/7; actual new-unit lint, explicit
formatting/inventory and exact twice-repeated Eistute/Book regression. All nine
attempted OBJ/acceptance/rejection/incidence states, 189 CSV fields and
1,168/4,256 last-accepted triangles remain exact.

Original: 27 strict sweeps stop at parameter value/list-node changes, with later
ordinals/CRT retention unmeasured. Three retention-only sweeps reclaim reachable
partial state and finish with 32 retained blocks each over their denials, without
rollback/retry claims. Other 58 outcomes expected. Unique pending nodes, cache
changes, parameters and output are prepared before commit after return-list
construction. Thirty positive calibrated sweeps deny 702 allocations;
explicit actual MSVC list-move denial and final return-edge preservation pass.
All 54 normal complete traces match original. Existing cache entry nodes remain
stable; endpoint scalar/adjacency copy, reuse, aliases, sample/ID order remain.
Consumed IDs and evaluator scratch are not rolled back. Preparation changes
resource behavior/peak storage explicitly; no performance claim.

Both serial tails are verified byte-identical; original uses 14 pinned units
plus the unchanged tail adapter, candidate 15 actual units. Full old Adapter/
Generator instrumentation is not claimed. Only the new target consistently
disables optional NRVO and Debug iterator metadata, retaining actual heap and
negative controls. Valid 87-case preliminary coverage remains. Input/cache
nodes stay borrowed and caller collective result lifetime remains. C07/ADR-0015
delimit upstream sorting/selection, scratch, later Generator publication and
full Adapter/AdaptCurve/mesh rollback. Closed/reversed and overwrite fixtures
are policy/ownership controls, not geometric consistency certification. No
scientific formula/order, policy, tolerance, budget or verifier change. See
evidence/STAGE3_ADAPTER_SAMPLES_CLOSURE.md.

Full stage 3 remains open with fourteen qualified slices. Next characterize
Generator point-observer publication and collective sample ownership across
curve/surface refinement, then upstream/full adaptive retry/rollback over
parameters, patch/mesh observers and error/history/budget state, plus explicit
full CLI disabled synchronization. Construction-tail and paired-rebuild commits
are qualified narrow boundaries, not full Adapter/AdaptCurve/mesh transactions.
Evaluator scratch, remaining construction/mutation, generic/custom sources,
other helper/template/tree/mate paths, failed-tree observer consumption/retry
and full-process/parallel/LSan/UBSan stay open. Stages 0-2 remain closed for
measured scope; stages 4-11 pending. Doxygen API debt stays stage 8.

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
