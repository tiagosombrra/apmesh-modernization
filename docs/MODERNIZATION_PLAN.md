# Technique-preserving modernization plan

Source and immutable import: see PROVENANCE.md. This repository is the working
authority; PROJECT_STATE.md records the current work item and verified results.

Current status: stages 0-2 closed for measured scope; stage 3 slice 22
(PR #66) is qualified at head `88c285e5ac193e7c45fe688cec05867e5243dbdd` and main
`79bad64023ab1ddd54eda76930df47ff2986f765`. All exact-head/main gates pass; stage 3 remains open.
Next establish triangle special-member/replacement observer semantics, then
qualify completed-triangle destruction. Owner ordering does not itself repair
triangle deregistration or full-process memory. See [audit](evidence/STAGE3_SUBMESH_LIFETIME.md).

Previous qualified baseline: stages 0-2 closed for measured scope; stage 3 slice 21
(PR #64) is qualified at head `a6da72630db2747194982e1a2b77cd3203536408` and main
`6cf041333b83a01f1c081df82620d12f00995d4b`. All exact-head/main gates pass; stage 3 remains open.
Next audit triangle destruction/observer lifetime with SubMesh owner ordering.
Constructor restoration does not qualify ordinary destruction, failed adoption
of completed triangles or full CLI retry. See [audit](evidence/STAGE3_TRIANGLE_CONSTRUCTION.md).

Previous qualified baseline: stages 0-2 closed for measured scope; stage 3 slice 20
(PR #62) is qualified at head `dcf6941e944fcd3bf268e7f9a8ecef4f87735d75` and main
`40106ede082614429639566c64ca3689a7d62c4b`. All exact-head/main gates pass; stage 3 remains open.
Next isolate TriangleAdaptive construction/adjacency registration under allocation
failure. Terminal element adoption does not qualify live-graph reuse or constructor
failure before entry. See [scope and closure audit](evidence/STAGE3_ELEMENT_ADOPTION.md).

Previous qualified baseline: stages 0-2 closed for measured scope; stage 3 slice 19
(PR #60) is qualified at head `bebe4f5273719304fd00967bfaf7ae74de63f351` and main
`e04a76a6103af5af5b116447c63c4de1ee047a0c`. All exact-head/main gates pass; stage 3 remains open.
Next isolate SubMesh raw element adoption. MeshAdaptive insertion qualification
does not cover element insertion, OpenMP constructors or whole-process memory.
See [scope and closure audit](evidence/STAGE3_MESH_ADOPTION.md).

Previous qualified baseline: stages 0-2 closed for measured scope; stage 3 slice 18
(PR #58) is qualified at head `84e303da51a6ac4c6cf52dbbee7f5fb30c93696e` and main
`e398854bba9f06045b71dd1b965505872106d746`. All exact-head/main gates pass; stage 3 remains open.
Next isolate general MeshAdaptive raw adoption. The measured initial-mesh repair
does not qualify OpenMP constructors, raw adoption or whole-process memory.
See [scope and closure audit](evidence/STAGE3_INITIAL_MESH.md).

Previous qualified baseline: stages 0-2 closed for measured scope; stage 3 slice 17
(PR #56) is qualified at head `06f4bfd40cff9f09c527777169c5fcf8d053e0c7` and implementation main
`9703536b21d8d3f02dbe7fbd9f83d3260f461aad`. All exact-head/main gates pass; stage 3 remains open.
Next isolate InitialMesh temporary/pending ownership. Published-sample terminal
release does not establish full-process memory or exceptional metadata recovery.
See [scope and closure audit](evidence/STAGE3_CURVE_SAMPLE_LIFETIME.md).

Previous qualified baseline: stages 0-2 closed for measured scope; stage 3 slice 16
(#53, PR #54) is qualified.
Head `8eaeb09fa8137ed32dea5549b4ac07b923d5bac2` integrated as main `186ef0251f460f3139baedae4ed77f30a2b9695b` through PR #54,
preserving complete tree `0aef3cdf1d5fb1cb9075062cebfb74f68106dabf` (1678 blobs).
Full exact-head and implementation-main campaigns pass with the same 538
qualified compiled/tool/test/build/input/contract identities.

CurveSampleGraphTransaction now spans serial AdaptCurve preparation/policy and
the complete curve loop. All equivalent working point/parameter lists and the
deduplicated initial sample inventory are prepared before original nodes are
parked. Initial sample objects remain alive across successful per-curve prefixes.
After inner guards unwind, failure clears the operation-local cache, clears every
new shared graph alias before deletion, reclaims each new sample once without
allocating and restores every original point/parameter list node and shared
object. Success retires initial samples once after the complete loop, in the
existing unordered-set capture/iteration convention, and leaves final graph
lifetime with the caller. Per-curve sampling/publication/rebuild code is unchanged.

Graph qualification passes 156/156 outcomes: 36 complete normal ASan/CRT traces
(two visible operations each), 18 positive allocation sweeps/8118 denials,
78 controlled abort/restore/retry outcomes, 18 retention-only cases, two explicit
empty-graph guards and four actual list-move/UAF/leak/hook controls. Every denied
allocation propagates once; attempts equal ordinal+1, requiring no rollback
allocation. Final denial follows three committed curves and all expected ID
requests. Four-curve fixtures cover three initialized actual curve types and
mixed graphs, shared non-manifold/closed/reversed/distinct/two-endpoint layouts,
prefix lengths one through four, inner surface failure, early failure, actual
analytic interior samples, independent physical mesh copies/adjacency and a
later operation whose initial samples were generated by actual production code.
Original point/parameter list nodes, all sample fields/sharing and successful
retry are checked. Consumed IDs stay consumed; evaluator scratch and orchestration
metadata are not rolled back. Empty geometry is guard-only, not positive coverage.

Original: 18 strict allocation sweeps and 60 controlled aborts stop at partial
graph-restoration assertions. Later ordinals/unsafe observer consumption and CRT
retention in those aborted cases are unmeasured. Eighteen separate retention-only
experiments reclaim current reachable graph samples only and leave 1-6 orphaned
entry samples, with 3-12 retained CRT blocks each. They make no restoration/retry
claim. Other 60 original outcomes are expected. All 36 normal full observed logs
match repaired logs. Verbatim original capture/retirement blocks wrap the original
map/set storage with 19 Git-pinned production units; candidate uses 20 actual
units. The controlled driver calls actual per-curve publication/sample/rebuild
operations, not full historical Generator/Adapter TUs or upstream selection.

CTest 26/26, zero skips and 74 Python controls; all ten prior batteries pass:
publication 139, samples 88, rebuild 117, snapshots 89, synchronization 73,
adoption 53, copy 30, curve 19, UV 81, node seven. Read-only new-unit lint,
explicit formatting and inventory pass: 135 production files, 63 units, 72 headers,
22 contracts/117 anchors; existing six-header cycle retained. Twice-repeated
Eistute/Book comparisons preserve all nine attempted OBJ/acceptance/rejection/
incidence states, 189 CSV fields and 1,168/4,256 last-accepted triangles exactly.
Only the new target consistently disables optional NRVO/Debug iterator metadata;
actual heap checks/negative controls and prior target settings remain unchanged.

Classification: behavior-changing lifecycle/exception-consistency defect repair,
with success-preserving engineering consolidation. Preparation/capture lifetime
and cache cleanup intentionally change allocation timing/counts/bytes/peak storage;
no unchanged-allocation or performance claim. No scientific formula/float order,
numerical selection, synchronization, templates/front, tolerance, budgets, verifier
or adaptation/acceptance/stopping change. C07/ADR-0017 require fixed topology,
initialized parametric curves, collectively exclusively deletable samples without
competing geometry-control/physical mesh owners, qualified inner operations and
nonthrowing destructors. Full metadata/error/history/budget and patch/mesh/
acceptance rollback, evaluator scratch and full-process memory stay unqualified.

Full stage 3 remains open with sixteen qualified slices. Next characterize
the remaining orchestration rollback boundary: curve adaptation metadata and
targets, evaluator scratch, patch/mesh observers, error/history/budget/acceptance
state and whole adaptive retry/rejection, then explicit full CLI disabled
synchronization. Complete point/parameter graph rollback is qualified for the
measured serial operations; it is not full Adapter/AdaptCurve/mesh atomicity.
Other constructors, custom sources, helper/template/tree/mate paths, failed-tree
observer reuse and full-process/parallel/LSan/UBSan remain open. Stages 0-2 stay
closed for measured scope; stages 4-11 pending. Doxygen API debt stays stage 8.

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
