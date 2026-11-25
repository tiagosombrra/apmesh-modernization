# Independent audit and native replay of portable mixed feedback

2026-11-25 Fortaleza. User-requested review of recent local Codex progress.
Latest canonical state reviewed: `e04db5dcceff769cc42e2c768d2cd52f706d10cd`.
Latest source reviewed, compiled and executed: draft PR 271,
`e470cbe2ccc249bb6b3ea39fcd1915e3066d941b`.
The review also executed the preceding PR 270 source `dc6025e8`.
[Machine-readable evidence](evidence/INDEPENDENT_FEEDBACK_AUDIT_20261125.json).

## Decision

Continue the relative geometric trigger qualification now selected in
[STATE.md](STATE.md). The portable entry has been implemented and replayed
on both development geometries; implementing it is no longer the next task.
Selection, previous-owner rejection, process recovery and native feedback are
reproducible within their stated scope. Scientific admission and two distinct
accepted mixed epochs remain open. No threshold, algorithm change, source merge,
or production promotion is made by this audit.

The canonical branch's progress remains documentary; experimental source resides
in draft PRs 263--271. Remote main remains
`ef40c0fc16e6913eb8941f2860ef0deb1ee6bd89`; the frozen TRI reference remains
`f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.
Unpushed changes on the user's Windows workstation were not accessible.
A concurrent canonical update was detected before writing this checkpoint.
The audit incorporated PR 271 and refreshed STATE and SESSION_LOG rather than
overwriting the new portable-source milestone.

## Fresh execution of exact PR 271

Built the application and original-source contract target with Linux GNU 14.2.0,
C++17 Release, CMake 3.31.6, MPI/OpenMP/LTO off and experimental QUAD on.
Python was 3.12.14. The tracked source remained unchanged.

- 30 Python controls passed: 17 generation metrics, four fixed-region comparisons,
  five conservative admission and four process recovery controls.
- Native source contracts passed six captures, including three reversed captures,
  and 54 negative controls.
- The existing grouping application suite passed eligible selection, forced
  native rejection with previous-owner/output preservation, fine-size veto,
  recovery of the three selections and both original tree-only feedback arms.
- The new portable suite ran CurvaBezier and Ribbed patch 12 through the same
  executable. Both successors staged. The altered Ribbed tree was rejected
  before feedback; the original source witnesses remained intact.
- All three source-file hashes and each successor OBJ hash match the prior MSVC
  receipt exactly. Both complete 48 x 48 paired comparison JSON objects also
  match the recorded MSVC measurements exactly.

| Reproduced portable measurement | CurvaBezier | Ribbed patch 12 |
| --- | ---: | ---: |
| Source TRI step | 3 | 2 |
| Faces | 732 to 796 | 547 to 648 |
| Nodes | 689 to 758 | 525 to 623 |
| Final TRI / QUAD | 99 / 697 | 74 / 574 |
| Contour intervals | 14 to 21 | 14 to 22 |
| Native leaves | 223 to 229 | 112 to 133 |
| Direct leaf edits | 2 | 7 |
| Capped face requests / total | 6 / 11 | 1 / 17 |
| Area-weighted geometric RMS48 | 0.011914927232780577 to 0.00807116489778796 | 0.027488072891660026 to 0.01736883885770502 |
| RMS reduction | 32.2601% | 36.8132% |
| Face growth | 8.7432% | 18.4644% |
| Minimum TRI angle | 1.41820 to 2.47223 degrees | 3.79134 to 6.32815 degrees |
| Minimum QUAD angle | 19.43861 to 18.56844 degrees | 26.18180 to 25.33562 degrees |

The portable successor SHA-256 values are:

- CurvaBezier: `e4cad6e9151acc412087074b11e31da69e5aa40261b824e092bb0daff056aad0`.
- Ribbed: `175542eba23f67e27fc7d573c962ad6f6c49c104bbbd225763b73cc46cde7b65`.

## Earlier grouped route also reproduced

Before the concurrent PR 271 publication, the same review built exact PR 270
and ran the same 30 Python controls, native source contracts and three grouping
outcomes. Additional directed executions reproduced:

| Prior grouped-route mode | Observed result |
| --- | --- |
| `tree` | Recovered-arm RMS48 increased 4.8437%, and minimum TRI/QUAD angles deteriorated. |
| `previous-search` | Typed XYZ, UV and connectivity exactly matched the recovered predecessor. |
| `curve-and-tree` | Ordinary smoothing rejected an inverted/collapsed UV QUAD after ten curve splits. |
| `guarded-curve-and-tree` | Staged the recorded 813-node/852-face successor, with the exact prior MSVC OBJ hash. |

That grouped route's RMS reduction of 69.4399% starts from a different
725-face predecessor. It is not the portable route's 732-face experiment.
The different reduction percentages must not be interpreted as a regression
without a matched predecessor comparison. Correctly rejected candidates are
negative-control outcomes, not successful generations.

## Hosted regression and memory evidence

All final PR 263--270 runs have four successful jobs.
For exact PR 271, [run 45583661335](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45583661335)
completed all four jobs successfully at the final read recorded in the receipt.
The earlier three-success/one-running observation was superseded by that verified
completion. The receipt records the exact job IDs and source revision.

The completed PR 271 jobs report 20 Linux standalone QUAD tests, 85 root CTests,
527 tooling tests, and exact frozen TRI comparison on five Eistute and four Book
states. OBJ bytes and acceptance fields match, with exact boundary regression
and verified incidence coverage. These complete hosted gates were inspected;
the audit environment did not repeat the full 85/20/527/frozen-reference matrix.

PR 271 adds the two-model portable suite to GCC, Windows and Clang
AddressSanitizer/UndefinedBehaviorSanitizer paths. The completed Linux log shows
the two portable cases both with GCC Release and with Clang ASan/UBSan and
`detect_leaks=1`. Source and successor hashes agree across those executions.
This materially closes the earlier missing sanitizer exercise for the portable
curve/tree/guarded reconstruction path.

A separate local instrumented PR 270 build compiled successfully, but its first
baseline process aborted: LeakSanitizer reported a fatal runtime error with
its ptrace incompatibility hint. The grouping test exited 1 after child SIGABRT.
The instrument log was retained; no suppression or relaxed rerun was used.
This was not an identified APMesh leak and was not a passing memory check.
The local limitation does not invalidate the completed hosted PR 271 portable
sanitizer result.

The PR 265 production-inventory failure was corrected by isolating the
experimental plan from production RuntimeConfig. The original inventory check
was retained and later passed; no weakened test was found.

## Remaining limits that affect the next decision

**Trigger and stopping.** The current sizing pilot still halves the selected
TRI and QUAD seed targets without requiring a positive geometric signal.
An isolated unit-plane diagnostic again yields three face and two curve requests.
The synthetic planar mesh is valid; the residual is zero at the indicator sites,
with only floating-point rounding in the independent common-grid comparison.
PR 271 parameterizes the actual surface evaluator but does not add a no-action
trigger. The relative residual study is appropriate next work; this audit
selects no tolerance.

**Regional shape.** Improved RMS does not imply uniformly improved elements.
The portable source receipt records CurvaBezier interior-QUAD minimum angles
64.40511 to 27.62607 degrees (624 to 684 faces in that class), as well as the
contour-edge QUAD decrease in the table. Ribbed's interior-TRI minimum decreases
26.57092 to 18.37052 degrees (two to sixteen faces in that class).
These are valid but degraded local shapes, not proof of invalid meshes.
A scientific admission rule must explicitly address them and mesh growth.

**Cost and reference choice.** The current CurvaBezier successor improves RMS
against original TRI by about 15.6%, using 796 versus 430 faces and 758 versus
223 nodes; its sampled maximum is about 0.576% worse than TRI. No general
efficiency or uniform superiority follows from the lower RMS. Use matched
face/node budgets or an error-versus-cost comparison for that claim.

**Realized size.** The bounded operation splits each actionable leaf/interval
once. The original receipt records six of seven CurvaBezier split intervals and
five of eight Ribbed intervals with at least one child still above the requested
arclength; worst ratios are 3.7876 and 1.6286. Refinement and balance do not
certify satisfaction of the physical size field.

**Native ancestry and shared sources.** The portable first predecessor is
recreated from a selected accepted TRI step. The successor's new requests are
measured but are not yet applied through two accepted mixed states with owned
curve/tree reentry. The shared-curve corner identity rejection remains open.
Separate native curve sample identity from patch-local corner ownership and
qualify that binding; coincident XYZ alone does not justify welding.

**Coverage.** The explicit grouped-candidate rejection/recovery suite remains
outside the hosted sanitizer block. Dedicated comparison/admission negative
suites and optional `--shared-source` are not invoked by the workflow.
The new portable test covers a different, now instrumented path.
An eventual integrated source revision requires its applicable gates; PR-head
checks do not qualify a future merge. Both geometries remain development cases.

## Concrete continuation

Follow the current checkpoint: qualify the relative geometric indicator with
an explicit experimental tolerance input and a flat no-action control.
Preserve scale checks, source binding and the measured candidate quality.
Align the actual tolerance, growth and regional admission before reserved cases.
Then reenter from the previous mixed successor's owned native curve/tree state
and demonstrate the two accepted mixed epochs required by issue 221.
Keep shared-curve source qualification and global mixed curvature as explicit
remaining gates. No further standalone audit is selected as the next work item.
