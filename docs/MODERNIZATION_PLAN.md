# Technique-preserving modernization plan

Source and immutable import: see PROVENANCE.md. This repository is the working
authority; PROJECT_STATE.md records the current work item and verified results.

Current status: stages 0-2 are integrated and closed for measured scope.
Stage 3 slice 6 (#23, PR #24) is qualified.
Head `da684dd6a2a1fefe709fc8906cce837da4b2ea24` integrated through PR #24 as main
`1d7d5992d90f09d8cf7747d9023d9b39ef3d089b`, preserving complete tree
`f3d634588529e0ff9dec3121ae2c1aa3d215bedc` (853 blobs). Full exact-head and
implementation-main campaigns pass: CTest 16/16, zero skips, 74 Python controls,
UV 68/68, node 7/7, six-unit lint, changed-range formatting, fresh inventory and
strict repeated Eistute/Book regression. All nine attempted states, acceptance/
rejection, measured incidence results, 189 CSV fields and 1,168/4,256 last
accepted triangles remain exact.

Ten calibrated CRT sweeps deny 252 allocations through four endpoint matches
and nonadjacency with empty/populated observers. The original fails all ten
while its prior 56 and both new normal cases pass. A local guard detaches the
temporary angle edge on unwind; caller ownership/state and successful helper
reuse after failure are qualified. Original/candidate success traces and all
allocation counts match. No scientific expression, ordering, policy, input,
verifier, tolerance or vendor changes. This documentation-only follow-up
preserves every qualified production/tool/test/build/input/contract identity.
See evidence/STAGE3_ANGLE_HELPER_CLOSURE.md and ADR-0007.

The wider stage 3 remains open with six qualified slices. Next characterize
remaining helper/mutation and curve-internal allocation failures, then
parametric midpoint replacement and sample/initialization/rollback ownership.
Other setters/templates/tree/mate paths, general copied observers, failed-tree
observer consumption/retry, full-process and parallel/LSan/UBSan qualification
remain open. Stages 0-2 stay closed; stages 4-11 remain pending.

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

## Active stage 3 slice 7 (#26): parametric midpoint replacement

Candidate CTest 17/17, 74 controls, UV 81/81, node 7/7, six-unit lint,
formatting, inventory and strict repeated Eistute/Book entry regression pass.
Ten original failed replacement sweeps now preserve cache/caller state through
all 30 allocation denials and successful retry. Destruction of the old cache
is delayed to commit; successful arithmetic, allocation counts and outputs
remain exact. Direct curve examples observe zero allocations and do not qualify
internal allocation failure. Exact head/main gates remain required; full stage
3 stays open. See evidence/STAGE3_PARAMETRIC_MIDPOINT.md and ADR-0008.
