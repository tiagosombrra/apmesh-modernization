# Accepted errors at serial stopping guards

Base: main `ab64af7c25c06090ab76b618de099f27549fe117` (PR #112).
Classification: behavior-changing accepted-state data-association defect repair.

Outer rejection restores the accepted mesh, local error vector and curve state,
but leaves attempted global/local scalar errors intact. The preserved diagnostic
observes three subsequent loop entries with stale scalars: Eistute twice and
Book once. Neither article naturally stops early at its frozen thresholds.
Six separate synthetic rejected-scalar controls expose false convergence labels;
two immediately-above controls continue. Nine states and 45 scientific artifacts
are exact in the observation-only copy. These controls are not physical results.

Serial loop entry now reads the committed `error_step_.back()` and the maximum
of the restored `last_submesh_error_`, preserving the existing zero for an empty
local vector. Initial global history is unconditionally populated before loop
entry; subsequent history entries are committed only by acceptance. The existing
`<=` comparisons, global-before-local order, stop labels and printed error values
refer to this accepted view. Attempted scalars are not overwritten. The parallel
selection retains its original scalar inputs; no parallel runtime qualification
is added. A reversible token comparison excludes all other Generator changes.

Initial caller checks pass a rejected global-below continuation, accepted global
and local equality, and empty local data. The immutable original caller fails six
stronger stopping contracts while four nonempty correct traces still pass. Eight
checker tests challenge original stopping, accepted provenance, restoration,
threshold drift/nonfinite values, equality/priority, labels and missing completion.
Initial checks do not qualify integration.

Required complete-caller gates use a reversible, compiled copy of the real
Generator, with no injection in normal runs. Separate rejected-error controls
inject below/equal/above scalars only after real rejection/reporting/restoration.
Separate accepted-error controls alter committed errors only at explicit test
checkpoints to exercise initialization, equality, above-limit continuation, empty
local data and post-acceptance convergence. Two branch controls force acceptance
only at steps 1/4 and extend the test limit to 5, exercising convergence on a new
accepted root after two consecutive rejections, archived and unarchived. A growth
control enters the existing synthetic `prev_error + 1.0` rejection path and tests
continuation despite a low rejected local cache. These are state/branch tests,
not production policy changes or solver-produced convergence measurements.

Require both production and observation-only Eistute/Book runs to preserve all
nine accepted/rejected mesh states and 45 scientific artifacts against PR #112
main. Strict acceptance, independently checked physical/UV quality and shared
boundaries must pass. No baseline, scientific criterion, directions, quadtree,
front, synchronization, retry, acceptance or intentional rejection memory changes.

Exact-head gates: C++17 build; 64/64 CTest, zero failures/skips and 172 Python
tests; all 26 normal/controlled caller cases; original controls; source token
preservation; analyzer, formatting, whitespace, contracts/inventory and staged/
remote review. Delivery results and command/source/input/executable/report hashes
belong to the PR and local `build/accepted-error-repair/` evidence. Required main
revalidation follows integration; an open PR is not an integration result.

Final reporting still exposes attempted scalar/metadata values and requires its
own audit. Natural provisional-progress paths, complete metadata rollback/resume,
ASan/CRT, whole-process, MPI/OpenMP, LSan/UBSan and stage closure remain unqualified.
Stage 3 stays open without a new qualified memory-slice count. The earlier
relative-area result remains negative; reverse directions remain unapproved.
