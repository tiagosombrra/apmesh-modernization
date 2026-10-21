# Technique-preserving modernization plan

Source and immutable import: see PROVENANCE.md. This repository is the working
authority; PROJECT_STATE.md records the current work item and verified results.

Current bounded work: stage 3 slice 33, serial-reader control ownership.

The candidate migrates LoaderBezierPatchFile to independent unique control
results and local pending ownership. ReaderFilePatches retains parsed controls
and consumes a separate unique reconstructed patch through Geometry. Three
badbit masks propagate resource failures before partial record indexing. This
is a behavior-changing lifetime/failure defect repair with no scientific policy
change or consolidation with the distinct charge parser.

Focused qualification passes 131 expected outcomes, sixteen complete CRT sweeps/
2731 actual allocation denials, eight nonempty GCC live pairs and six rejected
preservation mutations. The original retains 72 failed/59 other expected outcomes,
all sixteen partial sweeps and 240 observed denials; later original ordinals remain
unmeasured. No complete-reader rollback/retry or full-process safety is claimed.
See [the bounded evidence](evidence/STAGE3_SERIAL_READER.md), C27 and ADR-0034.

Full exact published-head and post-merge gates remain pending: 47 CTest entries,
74 Python controls, all 29 memory batteries/3005 expected outcomes, preserved
analytic/scalar/model traces and local/remote quality/identity checks. Slice 33
is not qualified. The full stage 3 and stages 4-11 remain open; Model/copy,
MPI/Hermite and other finite rows retain their separate pending dispositions.
Earlier "next" paragraphs below are historical checkpoints.

Stage 3 slice 32 is qualified within its measured boundary. PR #86 integrates
head `7307bdab7c7f4c835218fd3c80d8ad8b458538aa` as main
`cce8927dd2a69edbbddfb4b51c7a6f8ecf201edf`, preserving complete tree
`b1d1fd64c7f4924c5ba3180cb5623eb6aac9dcf5` (1951 blobs). Exact-head gates pass
all 107 commands. Post-merge main completed 106 local commands before a final
remote API connection timeout; a separately recorded terminal continuation now
passes the complete remote tree/branch/PR/check audit, environment and exact
checkout checks. The original failed report remains unchanged and hash-linked.

Both implementation revisions retain the same 598 protected inputs: 45/45 CTest,
zero failures/skips, 74 Python controls, 28 memory batteries/2874 expected outcomes,
1040 retained scalar sequences and exact twice-repeated Eistute/Book accepted/
rejected/incidence/CSV traces. Independent command/case/child-log/artifact/source
checks pass; all 56 current memory executable identities match main evidence.
The new battery passes 126 outcomes and 19 no-allocation operations, with six
GCC and twelve MSVC live pairs and six rejected preservation mutations. Original
103 failed outcomes, 23 other expected outcomes and two actual ASan UAF
reproductions remain retained. See [bounded closure evidence](evidence/STAGE3_BEZIER_OBSERVERS.md).

Stage 3 remains open. Next single item: audit successful fresh-curve caller
adoption and remaining loader/Model/copy roots. Hermite retirement, arbitrary
replacement/copied observers, cache/metadata/acceptance rollback and complete-
process/parallel/LSan/UBSan remain unqualified. Stages 4-11 remain pending.
The [finite closure inventory](architecture/STAGE3_CLOSURE_INVENTORY.md) retains
each obligation and its required evidence. No scientific policy changes.

Previous qualified baseline: slice 31, implementation #84 and closure #85;
see [construction evidence](evidence/STAGE3_BEZIER_CONSTRUCTION.md).

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
