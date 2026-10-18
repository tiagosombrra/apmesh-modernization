# Technique-preserving modernization plan

Source and immutable import: see PROVENANCE.md. This repository is the working
authority; PROJECT_STATE.md records the current work item and verified results.

Current status: stages 0-2 closed for measured scope; stage 3 slice 12
(#41, PR #42) is qualified.
Head `98528aeba68bb0b016b40eeeaff8d2bac6acc297` integrated through PR #42 as main
`358107faff5d6d2cdcd63eba12114abf7f7dc5ec`, preserving complete tree
`b39cd3b291f072983807828d4e3530fa6c9311f1` (1321 blobs). Full exact-head and
implementation-main campaigns pass: CTest 22/22, zero skips, 74 Python controls;
snapshots 89/89, synchronization 73/73, adoption 53/53, copy 30/30, curve 19/19,
UV 81/81 and node 7/7; actual new-unit lint, explicit formatting/inventory and
strict repeated Eistute/Book regression. All nine attempted OBJ/acceptance/
rejection/incidence states, 189 CSV fields and 1,168/4,256 triangles remain exact.

Original evidence: 12 sample-destruction sweeps stop at ordinal 6, four partial
list sweeps at ordinal 18; later ordinals and CRT retention in those 16 aborted
cases are unmeasured. Four empty-to-single sweeps finish with six retained blocks
each; other 69 outcomes are expected. Pending unique nodes and complete lists
precede nonallocating swaps, owner release and unique old-sample deletion.
Twenty-eight calibrated sweeps deny 536 observed allocations, preserve the
live graph/list nodes and permit retry. Complete normal original/repaired traces
match. Preparation changes allocation timing/counts/bytes/peak storage explicitly.

Generator calls the extracted actual operation at unchanged retry/rejection
sites. Original comparison uses 14 pinned units plus a verified lambda adapter,
candidate 15 actual units; the full old Generator translation unit is not
instrumented. New Debug CRT iterator metadata is consistently disabled; heap
checks, negative controls and previous targets remain. First-ID order/sharing,
zero node curvature/adjacency and success observer invalidation are explicit.
Parameters are neither captured nor restored; independent accepted mesh copies
remain unchanged in fixtures. Collective exclusive old-sample ownership and
nonthrowing destructors are required. C07/C12 and ADR-0013 delimit the contract.
No scientific formulas, float ordering, policies, tolerance, budgets or verifier
change. See evidence/STAGE3_CURVE_SNAPSHOTS_CLOSURE.md.

Full stage 3 remains open with twelve qualified slices. Next characterize
remaining sample construction/mutation and the full adaptive retry/rollback
boundary, including parameter pairing, patch observers, mesh/error/history/budget
state, then explicit full CLI synchronization-disabled integration. The point-graph
restoration is directly qualified for initialized collectively owned samples;
parameter and full mesh/acceptance rollback remain separate. Generic observers,
custom subclasses, inconsistent sources, other helper/template/tree/mate paths,
failed-tree observer consumption/retry and full-process/parallel/LSan/UBSan remain
open. Stages 0-2 stay closed for measured scope; stages 4-11 stay pending.
Doxygen undocumented-API debt stays stage 8.

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
