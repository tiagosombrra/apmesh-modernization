# Project state

Updated: 2026-10-18 (America/Fortaleza).
Scope: implementation modernization preserving the published technique.

## Completed in stage 0

- Private separate repository; canonical name is `tiagosombrra/apmesh-modernization`.
- Exact 513-blob publication import at `cbfb863fb014e798289d824e158f67922036a5e3`.
- Source commit and tree pinned; licenses, citation and historical README kept.
- Initial audit, validation status and unapplied candidate patch retained.
- English working agreement and complete stages 0-11 plan.
- EditorConfig, clang-format/tidy configurations, explicit local quality commands,
  optional staged-byte hook, CMake presets and meaningful CTest registration.
- Compatibility-report checker rejects empty or zero-comparison coverage.

## Delivery status

Stage 0 is integrated in PR #1 and locally validated. See
`docs/evidence/BOOTSTRAP_VALIDATION.md` for executed checks and limitations.
No automatic hosted workflows or paid Actions have been created.

## Completed in stage 1

PR #3 integrated the qualified head `fd59206497b12e3352fc8bea634702d7fe9eb8a9`
as main `b7bdda0a5ac035938bdaa3ea59ae8a5c587aa2b6`. Its tree is exactly the
qualified 632-blob tree. All required gates passed again after merge; issue #2
is closed. The documentation-only closure record preserves production/test/tool
source identities. See `docs/evidence/STAGE1_CLOSURE.md`.

Implemented: strict CLI/configuration/BP validation; independent accepted-state
OBJ/CSV/log and per-incidence verification; exact repeatability; deterministic
logical-edge smoothing order; coherent patch-incidence orientation through
control-net construction, coarse mesh and adaptive reconstruction; physical arc
mapping and corner-curve repair; corrected CSV header semantics.

Pre-merge and post-merge results: native Windows GCC 16.1.0 serial C++17 Release build
PASS; CTest **9/9 PASS, zero skipped**; 65 Python controls, 23 invalid-input
controls, 14 real orientation cases covering 44 attempted states, analytic
constructor/arc tests and actual analyzer scope controls PASS. Selected exporter
clang-tidy and changed C++ range formatting PASS. Vendor files are unchanged;
first-party diagnostics remain errors and full legacy warning debt is open.

Eistute and Book repeat exactly with fixed executable/configuration/command,
including all acceptance/CSV fields, OBJ and incidence snapshots. Every attempted
article state has positive shared-incidence coverage and zero measured position
gap. Both models accept steps 0 and 1. Last accepted triangles: Eistute 1,168;
Book 4,256. The Book change from 4,418 is an explicit corner-curve defect repair.
Raw previous-candidate comparisons remain failed and retained, including CSV
label corrections. Strict comparison to a reference with only the two minimal
CSV/corner fixes passes for both models. No oracle or tolerance was relaxed.

The previously required reversed-generation and CSV-schema failures are repaired.
Historical failures remain evidence. Current detailed results and source/input/
executable hashes: `docs/evidence/STAGE1_ORIENTATION_REPAIR.md` and
`docs/evidence/stage1/orientation/`. Earlier incidence and smoothing reports are
historical observations, not current gate status.

## Completed in stage 2

Issue #5 and PR #6 deliver the inventory. Qualified head
`3544c99501ceb5883795c4211215df8a5d01b23f` integrated as main
`071cba93a0074918d392bdfb28eba02c4acbb7bd`, preserving its exact 653-blob tree.
All required gates passed again after merge. The documentation-only closure
record preserves production/development/test/build/input identities; see
`docs/evidence/STAGE2_CLOSURE.md`. Stage 1 issue #2 remains closed.

Delivered: a reproducible inventory of all 122 production C++ files (57 units,
65 headers), three build inputs, 22 reviewed contracts and 78 source anchors;
physical/UV domain and identity/conversion maps, ownership/invalidation and
computation-duplication ledgers, one six-header include cycle, an engineering
ADR and a dependency-ordered repair sequence. Production/build/model/config/
vendor and existing verifier identities are unchanged.

Entry CTest 9/9 and its 65 Python controls passed. The candidate CTest is also
9/9 with zero skips, now including 73 Python controls after eight independent
inventory controls; the same suite passed on the published head and main. Fresh-build Eistute/Book repetitions and strict entry/
previous-stage comparisons pass for all nine attempted states, with positive
incidence coverage and named CSV audits. Selected exporter lint passes.

Source review records the node copy/adoption contradiction, copied adjacency,
manual endpoint detachment, rollback observer invalidation, patch-copy and cache
mutation limits, and the build macro/routing gap. These are differentiated from
newly reproduced runtime defects. No new memory or parallel qualification is
claimed. Architecture: `docs/architecture/MESH_ARCHITECTURE.md`; decisions and
next-slice priorities: `docs/architecture/REFACTOR_SEQUENCE.md` and
`docs/decisions/ADR-0001-mesh-domains-and-lifetimes.md`.

Current audit and exact-head/post-merge evidence:
`docs/evidence/STAGE2_ARCHITECTURE_AUDIT.md`, `docs/evidence/STAGE2_CLOSURE.md`
and `docs/evidence/stage2/`.

## Stage 3 in progress: slice 1 qualified (#8, PR #9)

Qualified head `6c6c2f2d50f5870fd92e4edbc91fc5d901a1cd22` integrated as main
`e30fa99a8ea6da709f3943e8975efb31d9610b1d`, preserving the exact 674-blob tree.
All required gates passed again after merge. This documentation-only follow-up
preserves qualified production/tool/test/build/input identities. See
`docs/evidence/STAGE3_SLICE1_CLOSURE.md` and `docs/WORKLOG.md`.

The first bounded slice repairs a reproduced ASan heap-use-after-free: SetNoh
copied foreign element observers into a new mesh node. It now preserves scalar
state while clearing those observers; local triangles rebuild adjacency. The
header explicitly distinguishes copying from unique/raw ownership adoption.
General node copies and triangle removal/replacement remain outside this slice.

Candidate, exact-head and main gates: CTest 10/10, zero skips; 74 Python controls; selected SubMesh
lint/formatting; seven qualified ASan/Debug CRT cases including deliberate UAF,
double-free and leak controls. Repeated Eistute/Book and strict entry/stage-2
comparisons are exact across all nine attempted states, preserving 1,168/4,256
last-accepted triangles and measured shared-incidence coverage. See
`docs/evidence/STAGE3_NODE_LIFETIME.md` and `docs/evidence/stage3/`.

Slice 1 is complete for its measured boundary; the full stage 3 remains open.
## Stage 3 slice 2 qualified (#11, PR #12)

Head `a5fb2cd0d7ebbe6dc10f98689f4d6caa60419c0c` integrated as main
`5bfcadaaa2172c297448c9870c0f468feeae8f4a`, preserving the exact 706-blob tree
`306907d63f893767736bddfd995cf313f1bfcf8f`. Exact-head and post-merge CTest
11/11, 74 Python controls, 26 UV ASan/CRT cases, seven previous node cases,
selected lint/formatting and strict repeated Eistute/Book regression pass.
Registered UV templates have a single owner through failure and ordered
transfer; endpoint teardown allocates nothing and handles midpoint aliases.
Both models retain 1,168/4,256 last-accepted triangles, exact OBJ/acceptance/
incidence results and 189 matching named CSV fields. No scientific policy,
independent verifier, input or vendor changed. The documentation closure
preserves all qualified production/tool/test/build/input identities; see
`docs/evidence/STAGE3_UV_CLOSURE.md`, the failed original and ADR-0003.
Only this measured slice is closed; the wider stage 3 remains open.

Next bounded scope: allocation failure before UV registration and
constructor/setter replacement. Curve sample/rollback ownership, other UV
exceptions, generic adjacency and cache mutation, full process leaks and
parallel paths still need qualification.
Stage 4 may unblock actual instrumentation barriers. Keep one active item.

## Stage 3 slice 3 qualified (#14, PR #15)

Head `fce74915755d1535b89dbd280cbc1ba3813f9b91` integrated as main
`68ef4db735d3c478215815128309c6bdd7a8e90c`, preserving tree
`2bb4359687579a9069e162b228228dea2b1197be` (737 blobs). Exact-head and
implementation-main gates pass: CTest 12/12, zero skips, 74 Python controls,
UV 35/35, node 7/7, five-unit selected lint, changed-range formatting, inventory
and strict repeated Eistute/Book regression. Last accepted meshes remain
1,168/4,256 triangles with 189 matching CSV fields and positive incidence
coverage. All scientific policies and independent numerical verifiers remain.

The original runner stays failed with Edge/front construction retention,
partially changed failed cache replacement and a Face endpoint-alias UAF.
Both Face constructors are passing controls. Local owners now prepare caches
and Boundary adoption before commit. All 53 measured primitive allocation
failures unwind without retention and preserve the required live/caller state.
This documentation-only closure preserves every qualified production/tool/test/
build/input/vendor identity. See `docs/evidence/STAGE3_UV_ALLOCATION_CLOSURE.md`
and ADR-0004; the wider stage 3 remains open with three qualified slices.

Next bounded scope: template arrays/object creation before registration and
Boundary registration, followed by other setters/helper temporaries, then curve
sample/initialization ownership and rollback. Full-process and parallel memory
qualification, other template patterns and same-front reuse remain open.

## Stage 3 slice 4 qualified (#17, PR #18)

Head `ef89fd9d3305a9ed4c88548df086540d00bbadd3` integrated through PR #18 as main
`da3eed2dc351cfe1a82b117d686164686c738d95`, preserving tree `465fea56b1267644c352b1200250dc033b062188`
(784 blobs). Exact-head and implementation-main gates pass: CTest 14/14, zero
skips, 74 Python controls, UV 49/49, node 7/7, six-unit selected lint,
changed-range formatting, inventory and strict Eistute/Book regression.
Eight new sweeps inject 1,361 allocation failures; both missing-quadtree
subdivision overloads are independently qualified. Successful UV geometry,
IDs, registration order and allocation counts match the pinned original.
All nine scientific mesh states and acceptance/incidence results remain exact;
last accepted meshes retain 1,168/4,256 triangles and 189 matching CSV fields.
The original fails 12 of the 49 cases while its previous 35 remain passing.

Boundary guards pending registration and commits contour/IDs after success.
TemplateStorage owns unregistered suffixes while Quadtree owns adopted prefixes.
Face::quality protects borrowed endpoints during allocation failure. Missing
quadtree context throws std::logic_error without changing valid subdivision
criteria. Template failure is qualified for destruction, not retry or observer
consumption. Original failures, fixture/build/lint failures and an encoding
repair remain recorded. No scientific formula, threshold, input or vendor
changed. This documentation-only follow-up preserves every qualified
production/tool/test/build/input/vendor identity.

The wider stage 3 remains open with four qualified slices. Next qualify
earlier tree generation/subdivision, remaining mutation/helper and curve
internal scopes, then sample/initialization/rollback ownership. Other template
patterns, full-process and parallel/LSan/UBSan scope remain open.

See `evidence/STAGE3_UV_REGISTRATION_CLOSURE.md` and ADR-0005.

## Stage 3 slice 5 qualified (#20, PR #21)

Head `4f0c9bed6d1d1a52b6cdab88a26a9323040614f9` integrated through PR #21 as main
`83eefa8c6006cc39dcdc35d463b8611d6f038538`, preserving tree `fa76355260fad7184d236f5680dac3ea67e5b6b6`
(818 blobs). Exact-head and implementation-main full campaigns pass: CTest
15/15 with zero skips, 74 Python controls, UV 56/56, node 7/7, six-unit selected
lint, changed-range formatting, fresh inventory and strict Eistute/Book
regression. All nine attempted states, 189 CSV fields, acceptance/incidence
results and 1,168/4,256 last-accepted triangles remain exact.

Five calibrated sweeps inject 3,470 allocation failures across initial root,
uniform subdivision, boundary-edge/old-face generation and actual neighbor
refinement. The original fails all five; its previous 49 cases and both new
success traces pass. Candidate success traces and allocation counts match
original; valid cases retain zero normal CRT blocks/bytes. Root bounds and
midpoint construction are locally owned until complete adoption. Only two
production implementation files change; no scientific expression or policy
changes. See ADR-0006 and `evidence/STAGE3_UV_TREE_CLOSURE.md`.

The wider stage 3 remains open with five qualified slices. Next characterize
remaining mutation/helper temporaries and curve-internal allocation failures,
then sample/initialization/rollback ownership. Other tree/mate/setter paths,
same-tree retry/observer consumption after failure, other templates and
full-process/parallel/LSan/UBSan qualification remain open. Stages 0-2 are
closed for measured scope; stages 4-11 remain pending.

## Open blockers and limitations

- Stages 0-2 are closed for their measured scope. Stage 3 is in progress and
  stages 4-11 remain pending;
  architecture inventory is not dynamic memory, parallel or portability
  qualification. Broad numerical and generated-documentation work remains open.
- Legacy compatibility summaries still compare zero groups when synchronized.
  Independent incidence evidence now measures actual sheets and does not treat
  that legacy zero as proof of compatibility.
- Ownership findings, timers, duplicate mesh representations, VLAs and warning
  debt remain. No full-application leak-free claim is justified.
- Eigen remains; CRABMesh consolidation, complete English renaming, generated
  Doxygen review, C++23 qualification and performance work remain open.
- The archived-artifact test is not a new accepted-mesh generation experiment.
- Earlier remote validation used the GitHub connector after Git DNS
  failure; the local continuation now uses working Git and GitHub CLI access. Earlier source validation excluded the two
  publication binaries; the current local continuation verifies the complete
  checkout, including those artifacts, against indexed Git blobs.

## Continuation rule

One work item at a time. Every delivery records scope, reviewed changes,
executed checks, toolchain, failures and next step. Recheck remote authority
before writing and after integration. Scientific algorithm changes wait for
explicit advisor alignment.

## Stage 3 slice 6 qualified (#23, PR #24)

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

Doxygen 1.18.0 is installed; the submitted initial run fails on undocumented
members. Comprehensive documentation remains stage 8 with strict warnings.

## Stage 3 slice 7 qualified (#26, PR #27)

Head `4781226726bd36d7ff64afb273ed53c37630b6f3` integrated through PR #27 as main
`61dc86ecaeede57ec838a5bb754f237b2013085a`, preserving complete tree
`ac04e95600a403e12952fb68f84a5e6c5a8abaa6` (889 blobs). Exact-head and
implementation-main complete campaigns pass: CTest 17/17, zero skips, 74 Python
controls, UV 81/81, node 7/7, six-unit lint, range formatting, inventory and
strict repeated Eistute/Book regression. All nine states, acceptance/rejection,
measured incidences, 189 CSV fields and 1,168/4,256 accepted triangles remain
exact. The original fails ten replacement sweeps; all 30 measured denials now
preserve cache/caller state and permit successful retry. Original/repaired
normal traces and successful allocation counts match.

The midpoint and normalized length prepare locally before commit. Old-cache
destruction is deliberately delayed; old/new caches coexist briefly, without
an address-reuse or peak-memory promise. Arithmetic, oriented intervals,
integration/bisection tolerances/stopping and null/fallback policies remain.
Curve evaluation scratch stays mutable. Three direct numerical operation
scopes observe zero allocations, explicitly leaving their internal allocation-
failure coverage unmeasured. This is an exceptional-exit defect repair, not a
scientific change. See evidence/STAGE3_PARAMETRIC_MIDPOINT_CLOSURE.md and ADR-0008.

Full stage 3 remains open with seven qualified slices. Next characterize other
curve mutation/constructor/setter failures, then shared sample ownership,
initialization and rollback. General observers, other helper/template/tree/mate
paths, failed-tree observer consumption/retry and full-process/parallel/LSan/
UBSan qualification remain open. Stages 0-2 stay closed; stages 4-11 stay pending.

## Stage 3 slice 8 qualified (#29, PR #30)

Head `2c7edff9070810ea8e27574e4449aeebf369824e` integrated through PR #30 as main
`587c91923b48d7f55414df720d29bcb1d2dacc11`, preserving complete tree
`914030fb831c060cfe980c912b3aa5eec0ecb776` (942 blobs). Full exact-head and
implementation-main campaigns pass: CTest 18/18, zero skips, 74 Python controls,
curve 19/19, UV 81/81, node 7/7, two-unit lint, range/probe formatting, inventory
and strict repeated Eistute/Book regression. All nine attempted states, measured
shared incidences, acceptance/rejection, 189 CSV fields and 1,168/4,256 final
accepted triangles remain exact.

The original partially overwrites live values in both populated-growth setter
cases at denied ordinal 7. Each setter now swaps its prepared input, preserving
live values/nodes and lvalue caller inputs on failure. Fourteen setter/copy
sweeps deny 76 calibrated allocations with preserved state and successful retry. Original/repaired normal ordered traces match. Successful
allocation counts and node reuse deliberately change: the second copy is removed
and old nodes are destroyed after swap. Borrowed points/patches remain external
owners' responsibility; old element observers are invalidated on success.

This exceptional-exit defect repair changes no scientific expression, ordering,
input, tolerance or adaptation/acceptance/stopping policy. Three explicit local
override annotations unblock unchanged lint rules; failed setup and lint logs
remain retained. C07/ADR-0009 limit the two independent transactions; they do
not form a joint point/parameter update. See evidence/STAGE3_CURVE_COLLECTIONS_CLOSURE.md.

Full stage 3 remains open with eight qualified slices. Next characterize the
remaining curve constructor/mutation contracts, including the pointer-taking
parametric constructor's omitted parameter sequence, before shared sample
ownership, initialization and rollback. Current constructor controls qualify
unwind, borrowed collections and selected initialized scalar/coefficient state;
full value-copy semantics are not claimed. General observers, joint updates,
other helpers/templates/tree/mate paths, failed-tree observer consumption/retry
and full-process/parallel/LSan/UBSan qualification remain open. Stages 0-2 stay
closed; stages 4-11 stay pending. Doxygen undocumented-API debt stays stage 8.

## Stage 3 slice 9 qualified (#32, PR #33)

Head `6bda90b91406b0aed79ba6582bf820ea40559325` integrated through PR #33 as main
`d5abb5495b28e8ec5a2b6f779c3adf173929ed04`, preserving complete tree
`d43fd3a977b725dbe7776f7adb0c7ab979dde32f` (1004 blobs). Full exact-head and
implementation-main campaigns pass: CTest 19/19, zero skips, 74 Python controls,
copy 30/30, previous curve 19/19, UV 81/81, node 7/7, one-unit selected lint,
probe/range formatting, inventory and strict repeated Eistute/Book regression.
All nine attempted states, measured shared incidences, acceptance/rejection,
189 CSV fields and 1,168/4,256 accepted triangles remain exact.

The base pointer-taking constructor now copies parameter values in independent
list nodes, preserving sampled-point correspondence in initialized parametric,
Bezier and Hermite copies. The original has 12 populated normal failures and
six populated calibration failures before denial; its other 12 control outcomes
are as expected. Nine repaired sweeps deny all 123 calibrated allocations with
unchanged source values/nodes/caller objects and complete successful retry.
All 18 normal numeric traces and six empty-sequence full traces match original.
Five populated parameter nodes are intentionally added per copy in these fixtures;
allocation counts are observations, not portable constants or performance claims.

Parameter values and observer containers are independent; physical sample/patch
objects remain borrowed. Both curve destruction orders are qualified only while
their actual external owners remain alive. No source consistency validation or
repair, implicit copying or clone-publication guarantee is added. Scientific
expressions, evaluation order and adaptation/acceptance/stopping policies remain
unchanged. See evidence/STAGE3_CURVE_COPY_CLOSURE.md, C07 and ADR-0010.

Full stage 3 remains open with nine qualified slices. Next characterize
ownership/publication around curve clones and remaining constructor/mutation
paths, then shared sample ownership, initialization and rollback. The
CloneCurveForPatch/DisableSharedCurveSynchronization consumer is reviewed
statically only; its policy integration and post-copy publication are unqualified.
Implicit copy/assignment, inconsistent/null/uninitialized sources, general
observers, other helper/template/tree/mate paths, failed-tree observer consumption/
retry and full-process/parallel/LSan/UBSan remain open. Stages 0-2 stay closed;
stages 4-11 stay pending. Doxygen undocumented-API debt stays stage 8.

## Stage 3 slice 10 qualified (#35, PR #36)

Head `249c561ec10f5d3766b0d1be71ed52d09e6420ec` integrated through PR #36 as main
`4e23bd00e457e68056ff956869732b1872f04822`, preserving complete tree
`4f6e71bf48933dfae637d6a200d9e2236734eb1e` (1083 blobs). Full exact-head and
implementation-main campaigns pass: CTest 20/20, zero skips, 74 Python controls,
adoption 53/53, copy 30/30, curve 19/19, UV 81/81, node 7/7, one-unit Geometry
lint, explicit probe/range formatting, inventory and strict repeated Eistute/Book
regression. All nine attempted states, OBJ, acceptance/rejection, measured shared
incidences, 189 CSV fields and 1,168/4,256 last-accepted triangles remain exact.

Eight original raw-adoption failures retain their relinquished argument; the
other 45 outcomes are as expected. Both raw curve/patch overloads now form a
pending unique owner before container allocation. Sixteen calibrated sweeps
deny all 16 observed allocations, preserving existing objects and source state,
destroying the failed argument exactly once and requiring a fresh-object retry.
All 34 normal original/repaired traces and successful allocation counts match;
null-slot semantics remain. Counts are observations, not portable promises.

This is an ownership failure-path defect repair. No formula, operation order,
policy, tolerance, budget, numerical verifier, vendor or historical source change.
C03 and ADR-0011 distinguish Geometry adoption from helper/policy integration and
multi-object transactions. Initial format-gate failures remain retained; explicit
changed-function formatting passes without suppression. See
evidence/STAGE3_GEOMETRY_ADOPTION_CLOSURE.md.

Full stage 3 remains open with ten qualified slices. Next characterize the
generator clone consumer/transaction boundary and remaining constructor/mutation
paths, then shared sample ownership, initialization and rollback. Geometry
adoption is directly qualified; CloneCurveForPatch and the synchronization-disabled
policy remain statically reviewed only, without a graph-publication/rollback
guarantee. Implicit copy/assignment, inconsistent/null/uninitialized clone sources,
generic observers, other helper/template/tree/mate paths, failed-tree observer
consumption/retry and full-process/parallel/LSan/UBSan remain open. Stages 0-2
stay closed; stages 4-11 stay pending. Doxygen undocumented-API debt stays stage 8.

## Stage 3 slice 11 qualified (#38, PR #39)

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

## Stage 3 slice 12 qualified (#41, PR #42)

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

## Stage 3 slice 13 qualified (#44, PR #45)

Head `ffdde7248564c8e072138d9673871baa4f13e217` integrated through PR #45 as main
`3e628e6445b2638ff73a51fa8bb1a9aed440647c`, preserving complete tree
`66f74c1b6d564e15a115db635a2b4856ee90a6aa` (1474 blobs). Full exact-head and
implementation-main campaigns pass: CTest 23/23, zero skips, 74 Python controls;
rebuild 117/117, snapshots 89/89, sync 73/73, adoption 53/53, copy 30/30,
curve 19/19, UV 81/81, node 7/7; actual new-unit lint, explicit formatting/
inventory and strict twice-repeated Eistute/Book regression. All nine attempted
OBJ/acceptance/rejection/incidence states, 189 CSV fields and 1,168/4,256
last-accepted triangles remain exact.

Original: 24 sweeps stop at first deleted-live-sample failure (per-case ordinals
11-28), with later ordinals/CRT retention unmeasured. Three two-endpoint sweeps
finish with 48 retained blocks each across their denied allocations; other 90
outcomes expected. Pending owned nodes and complete paired lists precede direct
nonallocating swaps and old-interior deletion. Thirty-six calibrated sweeps
deny 597 allocations, preserving both lists/nodes/samples and supporting
retry. All 78 normal full logs match original. IDs consumed before failure stay
consumed; retry uses subsequent IDs. Successful formulas, parameter/index order,
endpoint reuse and ID requests remain. Preparation changes allocation resource
behavior/peak storage explicitly, without a performance claim.

Original uses 12 pinned units plus verified lambda/two manager-context
substitutions; candidate 13 actual units. Full old Generator-TU instrumentation
is not claimed. New Debug CRT iterator metadata is consistently disabled with
actual heap/negative controls retained; previous targets stay unchanged. Valid
108-outcome and 117-outcome zero-start records are retained. Final fixtures
explicitly initialize intended nonzero manager start and retain zero/null cases;
no manager source change. C07/ADR-0014 require distinct exclusively deletable
interiors and preserve shared endpoints. Removed-sample/list observers are
invalidated on success. Curve observer publication, full AdaptCurve and full
mesh/acceptance rollback remain outside this helper. No scientific formulas,
floating-point order, policy, budgets, tolerance or verifier change. See
evidence/STAGE3_CURVE_REBUILD_CLOSURE.md.

Full stage 3 remains open with thirteen qualified slices. Next characterize
sample owner transfer and point-observer publication in Adapter/AdaptCurve,
then full adaptive retry/rollback across parameters, patch/mesh observers and
error/history/budget state, plus explicit full CLI disabled synchronization.
Paired helper commit and snapshot point-graph restoration are qualified narrow
boundaries; full AdaptCurve and whole-mesh/acceptance transactions are separate.
Remaining constructors/mutations, generic/custom sources, other helper/template/
tree/mate paths, failed-tree observer consumption/retry and full-process/parallel/
LSan/UBSan remain open. Stages 0-2 stay closed for measured scope; stages 4-11
stay pending. Doxygen undocumented-API debt stays stage 8.

## Stage 3 slice 14 qualified (#47, PR #48)

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

## Active stage 3 slice 15 (#50): Generator curve sample publication

Per-curve publication now parks original point/parameter list nodes after all
entry preparation, snapshots cache values and owns both returned lists before
allocating point-observer copies. The curve pass, surface pass and optional
target rebuild retain their order and numerical inputs. Rollback erases only new
cache keys, restores existing values in place, deduplicates/deletes new samples
without allocation and restores original point/parameter nodes. Entry samples
and preexisting cache values stay borrowed, including shared endpoints. Rebuild
may already have deleted discarded surface interiors; rollback never consumes
those stale curve observers. Commit deletes superseded first-pass samples and
transfers final samples to the existing collective graph lifetime. The unused
result-vector storage and late allocating keep-set are removed explicitly.

Publication 139/139: 54 normal ASan/CRT outcomes, 27 positive calibrated sweeps
denying 2403 allocations, 54 controlled upstream abort/restore/retry outcomes,
and four list-move/UAF/leak/hook controls. Every denied ordinal propagates once;
attempts equal ordinal+1, requiring allocation-free rollback. Final denied
publication follows all expected ID requests, including growth/shrink/equal/no
rebuild, cached/closed/reversed/two-endpoint and alias-overwrite fixtures across
three actual curve types. Independent interior polynomial geometry and borrowed
scalar/adjacency state, point/parameter/cache entry identity and successful retry
are required. Consumed IDs stay consumed; cached two-endpoint first passes
correctly request zero. All 54 normal complete original/repaired traces match.

Original: 27 allocation sweeps and 54 controlled upstream aborts stop at the
first partial-publication assertion; later unsafe observer consumption, later
ordinals and CRT retention in aborted cases are unmeasured. Other 58 outcomes
are expected. Sixteen pinned production units plus a verified publication-block
adapter are compared against seventeen actual candidate units plus the actual
publication template. Callbacks use actual sample/rebuild units, controlled
parameters and a controlled upstream point-list reversal; full historical
Generator/Adapter TUs and upstream numerical selection are not instrumented.
Original unused storage is rebound to a one-curve vector initialized within the
fixture operation; allocation timing/counts/bytes/peak storage change explicitly,
without a performance claim. Only the new target consistently disables optional
NRVO and Debug iterator metadata, retaining actual CRT heap and negative controls.

Required prior batteries: samples 88/88, rebuild 117/117, snapshots 89/89,
sync 73/73, adoption 53/53, copy 30/30, curve 19/19, UV 81/81, node 7/7.
CTest 25/25, zero skips, 74 Python controls; new-unit read-only lint, explicit
formatting and inventory pass (133 production files, 62 units, 71 headers;
22 contracts/113 anchors; existing six-header cycle retained). Two repetitions
per Eistute/Book preserve all nine attempted OBJ/acceptance/rejection/incidence
states, 189 CSV fields and 1,168/4,256 last-accepted triangles exactly.

Classification: behavior-changing ownership/exception-consistency defect repair
on failure paths, with success-preserving engineering consolidation. No scientific
formula, float order, numerical selection, synchronization, quadtree/templates,
front reconstruction, tolerance, budget, verifier or adaptation/acceptance/stopping
change. Source/history/licenses are preserved. C07 and ADR-0016 delimit this
boundary; evaluator scratch, previous successful curves, initial graph cleanup
and full Adapter/AdaptCurve/patch/mesh/history/budget rollback remain unqualified.

Exact published-head and implementation-main gates remain required. Full stage 3
stays open; the next boundary is complete-loop ownership and adaptive rollback.
