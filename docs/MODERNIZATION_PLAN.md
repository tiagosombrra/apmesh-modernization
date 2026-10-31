# Technique-preserving modernization plan

## Current stage and completion route

Stages 0-2 retain measured closure. Stage 3 remains open; stages 4-11 remain
pending. The 37 numbered slices are historical component qualifications, not a
percentage of completion. Later production repairs retain their own evidence.

The active [consolidated audit](evidence/STAGE3_CONSOLIDATION_AUDIT.md) replaces
the earlier sequence of local next-audit paragraphs. Work is controlled by the
ten-row [closure ledger](architecture/STAGE3_CLOSURE_INVENTORY.md) and five
[delivery packages](architecture/REFACTOR_SEQUENCE.md), one active item at a time.
Three ledger rows have bounded qualification; seven remain partial/open.
There is no stage closure until every required disposition and applicable gate
is measured on the delivery revision and main. Historical limits are preserved.

P1 implements the [complete serial MSVC C++17 build](evidence/MSVC_SERIAL_CPP17_BUILD.md)
through the existing pi definition and standard RAII scratch buffers. Require
its exact-head/main canonical builds, focused native/real CLI checks and frozen
GCC scientific reference. This is the permitted bounded stage 4 prerequisite;
full-process memory and complete Stage 4 remain unqualified.

Next single implementation: P2, the supported executable/input/caller and terminal-
versus-retry ledger, reusing existing executable controls before freezing P3's
whole-process instrument inventory. Follow with remaining supported-caller repairs
and final closure audit. No new model or scientific policy is authorized.

Every task must name a closure row, concrete output, minimal affected gates and
stop decision before work. A source-only investigation with no admissible witness
or reproduced supported defect records the open gap and stops its automatic
successor chain. It does not become qualified, disappear from the ledger or
authorize changing inputs/selection to force coverage. Required gates remain.

Run focused checks during implementation and full regression on the exact
delivery head and merged main. Retain successful identical-revision evidence;
repeat large campaigns only for a changed dependency, a named missing required
gate or a justified response to a recorded failure. Preserve negative controls.
These rules organize execution without changing scientific acceptance criteria.

All previous checkpoints are preserved verbatim in
[MODERNIZATION_PLAN_HISTORY.md](MODERNIZATION_PLAN_HISTORY.md). Current state is
in [PROJECT_STATE.md](PROJECT_STATE.md). Historical next-work paragraphs are not
an active task list. The original stage definitions and closure rules follow.

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
