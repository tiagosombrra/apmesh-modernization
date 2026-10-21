# Technique-preserving modernization plan

Source and immutable import: see PROVENANCE.md. This repository is the working
authority; PROJECT_STATE.md records the current work item and verified results.

Current work: stage 3 slice 32, completed Bezier observer retirement and dependent
Geometry ordering. Bounded prepublication qualification passes: 45 CTest, 74
Python controls, 28 memory batteries/2874 expected outcomes and exact repeated
article traces on 598 protected inputs. Required published-head confirmation is
recorded in the review PR; integration/main qualification remain pending. Slice
31 below remains the last integrated baseline. The [stage 3 closure inventory](architecture/STAGE3_CLOSURE_INVENTORY.md)
maps the finite remaining obligations and their required evidence without reopening
qualified slices or treating future portability/numerical work as completed.

Stage 3 slice 31 is qualified. PR #84 integrates head `c94ed17373abc04c9bbb5359a4ea686a44b886f3`
as main `1bc4038ad55a6b5fce7ec99db3fc5b200016ea69`, preserving complete tree `d950dbb0a49e4a4ec8109a6d4feefa360d5c10a2`
(1933 blobs). Exact-head/main full gates pass on the same 594
protected inputs: CTest 43/43, zero skips, 74 Python controls, 27 memory batteries/
2748 expected outcomes, 1040 retained scalar sequences, selected lint/format/
inventory and exact repeated Eistute/Book accepted/rejected traces.

Fresh Bezier curves now have local unique owners until construction succeeds;
failed borrowed-curve construction restores exclusively appended observer suffixes.
The unchanged scope is shared with charge estimation. The new 71 outcomes cover
32 complete sweeps/348 allocation denials; 16 actual GCC and 32 MSVC trace pairs
preserve scalar bits, controls, directions and live incidence. Four independent
mutations are rejected. Original 32 failed partial sweeps/208 observed denials and
39 other expected outcomes, including a zero-retention observer defect, remain
retained. See [root cause and bounded closure](evidence/STAGE3_BEZIER_CONSTRUCTION.md).

Stage 3 remains open. Next audit completed patch observer lifetime and caller
curve/patch destruction ordering. Successful fresh-curve caller adoption,
ordinary deregistration, arbitrary publications, cache/metadata/acceptance
rollback and full-process/parallel/LSan/UBSan remain unqualified. Remaining
estimator quadrature VLA/domain and interpolation singularity findings are retained
without new numerical policies or a demonstrated current serial failure.
Stages 4-11 remain pending.

Previous qualified baseline: slice 30, implementation #82 and closure #83,
final main `b908ecd384dea4877186fb8cb167444da5c2173d`; see [curvature sample audit](evidence/STAGE3_CURVATURE_SAMPLE.md).

Stages 0-2 remain closed for their measured scope. Stage 3 remains open; stages
4-11 are pending. This repair preserves formulas, floating-point order, numerical
selection, synchronization, templates/front reconstruction, tolerances, budgets
and adaptation/acceptance/stopping policies. Allocation timing/counts can change
when ownership defects are repaired; no unchanged-allocation or performance
claim follows from memory qualification.

Qualified inner operations do not establish whole adaptive atomicity. Remaining
work includes other construction/caller roots, custom sources, helper/template/
tree/mate paths, foreign and failed-tree observers, geometry/cache validity,
logical rejection and full metadata/error/history/budget/patch/mesh/acceptance
rollback or CLI retry. Consumed IDs are not rewound. Full-process, parallel,
LSan and UBSan remain unqualified; complete extreme/non-power-of-two meshes and
arbitrary callback publications are outside the bounded fixtures. C06/C07 and
their linked decisions retain fixed-topology, exclusive ownership, borrowing,
inner-operation and nonthrowing-destruction preconditions. Doxygen API debt stays
in stage 8; full historical MSVC translation units still have VLA blockers.

Detailed delivery history, commands, negative evidence and scope limits remain
in [PROJECT_STATE.md](PROJECT_STATE.md), [WORKLOG.md](WORKLOG.md) and their unchanged
evidence records. Architecture and repair ordering remain in
[MESH_ARCHITECTURE.md](architecture/MESH_ARCHITECTURE.md) and
[REFACTOR_SEQUENCE.md](architecture/REFACTOR_SEQUENCE.md).

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
