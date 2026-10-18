# Technique-preserving modernization plan

Source and immutable import: see PROVENANCE.md. This repository is the working
authority; PROJECT_STATE.md records the current work item and verified results.

Current status: stages 0-2 closed for measured scope; stage 3 slice 11
(#38, PR #39) is qualified.
Head `ce139f7d46b30daee365dfe5b1608183eb0d02c5` integrated through PR #39 as main
`43e0309d6408601cd13e130cfa9668f35596ab67`, preserving complete tree
`7bb0b34a537202eef24b7b354d91823b84cd6c36` (1199 blobs). Full exact-head and
implementation-main campaigns pass: CTest 21/21, zero skips, 74 Python controls;
synchronization 73/73, adoption 53/53, copy 30/30, curve 19/19, UV 81/81, node
7/7; actual two-unit lint, explicit formatting/inventory and strict repeated
Eistute/Book regression. All nine OBJ/acceptance/rejection/incidence states,
189 CSV fields and 1,168/4,256 accepted triangles remain exact.

Original evidence reproduces 12 partial graph failures at denied ordinal 1
(further ordinals unmeasured) and four helper retention failures; 57 other control
outcomes are as expected. Pending unique owners and ordered batch preparation
permit per-original-curve commit, coherent prefixes and whole-operation retry.
Twenty calibrated sweeps deny 484 observed allocations; full normal reported
traces match. Preparation deliberately changes allocation timing/counts/bytes.
Actual dynamic types, line/patch geometry, incidence orientation, repeated edges,
null filtering, mixed/non-Coons behavior and external ownership are checked.

The serial entry delegates to the actual extracted production operation. Original
comparison uses 12 pinned production units plus a hash-verified function adapter,
not the full old generator translation unit. The new Debug CRT target consistently
disables iterator proxies to avoid their allocation in noexcept construction,
matching serial/ASan layouts; heap checks, negative controls and prior targets
remain unchanged. Invalid first-fixture, standard-mode, iterator and lint failures
are retained with explicit interpretation. One Hermite destructor override
unblocks unchanged lint rules. No formula, ordering, incidence policy, tolerance,
budget, verifier or adaptation/acceptance/stopping change. C03/C07 and ADR-0012
record the measured boundary. See evidence/STAGE3_CURVE_PUBLICATION_CLOSURE.md.

Full stage 3 remains open with eleven qualified slices. Next characterize
shared-sample initialization and adaptive snapshot/restore/failure handling,
remaining constructors/mutations and explicit full CLI synchronization-disabled
integration. The extracted clone/publication operation is directly qualified
for the documented initialized graph fixtures; whole-operation atomicity and
adaptive rollback are separate. Generic observers/custom subclasses, inconsistent
sources, other helper/template/tree/mate paths, failed-tree observer consumption/
retry and full-process/parallel/LSan/UBSan remain open. Stages 0-2 stay closed for
measured scope; stages 4-11 stay pending. Doxygen API debt stays stage 8.

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

## Active stage 3 slice 12 (#41): transactional curve sample restoration

The original restoration deletes current samples before allocating replacements.
Twelve original sweeps stop at denied ordinal 6 because live samples were deleted;
four stop at ordinal 18 because a live list was partially published. Later
ordinals and CRT retention in those 16 aborted cases are unmeasured; the probe
stops before unsafe observer consumption. Four empty-to-single sweeps complete
with six retained blocks each. Other 69 of 89 outcomes are as expected.

Capture/restoration now live in a narrow production unit used by the same
Generator call sites. Pending unique NodeAdaptive owners and complete prepared
lists precede direct nonallocating swaps, owner release and unique old-sample
deletion. Allocation failure preserves the complete live point graph and list
nodes; subsequent retry succeeds. Success preserves first-encounter ID/XYZ,
order, sharing and zero node curvature/adjacency. Conflicting duplicate-ID input
is a policy-preservation control, not approval of that identity convention.
Parameter lists are not captured/restored. Current samples must be collectively
exclusively owned/deletable through the curves. Successful restoration invalidates
their observers. Independent accepted mesh copies remain unchanged in fixtures;
full mesh, patch binding, budget, error/history and acceptance rollback remain open.

Candidate gates pass: CTest 22/22, zero skips, 74 Python controls; snapshots
89/89 with 536 denials across 28 calibrated sweeps. Prior synchronization
73/73, adoption 53/53, copy 30/30, curve 19/19, UV 81/81 and node 7/7 pass.
Full normal original/repaired traces match. Actual new-unit read-only lint,
explicit formatting and inventory pass. Both article models repeat twice with
all nine OBJ/acceptance/rejection/incidence states and 189 CSV fields exact;
last-accepted triangles remain 1,168/4,256. Published-head/main gates remain.

Original comparison uses 14 pinned production units plus hash-verified lambda
bodies in an adapter, not the full old generator translation unit. Candidate
instruments 15 actual units. Only the new Debug CRT target consistently disables
iterator proxies; actual heap, failure and deliberate negative controls remain.
Preparation changes allocation timing/counts/bytes and peak live storage, with
no performance claim. Classification: ownership/exception-consistency defect
repairs plus engineering extraction. No formula, floating-point order, tolerance,
budget, verifier, synchronization or adaptation/acceptance/stopping policy change.
Full stage 3 stays open. See evidence/STAGE3_CURVE_SNAPSHOTS.md and ADR-0013.
