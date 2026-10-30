# Geometry-phase ideal Vertex pending ownership

Base: qualified diagnostic main `cb84989849c969c7ed58b0737f5bf1ff84359be0`
(PR #124). Classification: behavior-changing exception-safety/ownership defect
repair with unchanged successful scientific behavior. Stage 3 remains open.

## Original failure and bounded repair

The [source-preserving diagnosis](IDEAL_VERTEX_OWNERSHIP_AUDIT.md) retains 5007
native outcomes, 1832 original unowned ideal retentions, actual borrowed-best
destruction and stale-observer controls, rejected pilots and executor/configuration
failures. Its explicit caller cleanup is separate from production qualification.

findBestVertex previously stored its new geometric ideal directly in best, which
later also denotes an adopted ideal or borrowed existing candidate. Throwing
interception, candidate-list and publication operations could leave the temporary
unowned; failure of innerVertices insertion also left a frontVertices observer.

The original makeIdealVertex expression now enters a dedicated pending unique_ptr
independent of best. Its nonallocating deleter removes matching frontVertices
observations before deleting the ideal. The five existing guard/selection deletion
points reset that owner. Successful innerVertices insertion immediately releases
it, preserving the later already-owned vertices-view failure state. The owner
never follows best when selection switches to a live borrowed candidate.

Reverse only the local owner/deleter, borrowed assignment, five retirement points
and release to recover every original production byte. Original ID consumption,
successful allocation/publication order, selection, angular temporaries and
committed Face prefixes remain unchanged. No formula, floating-point order,
tolerance, quadtree/template, front reconstruction or adaptation/acceptance/
stopping policy changes. No whole-operation rollback or retry is introduced.

## Measured native contracts and controls

Seven inherited direct-selector modes, two candidate orders and zero/one native
committed Face prefix produce 28 contexts per profile. Thirteen unchanged native
units and a reversibly observed front compile as C++17 under GCC, MSVC ASan and
actual Debug CRT. The ideal is (1,2), h=2. Modes cover adoption, existing selection,
near-base/intercepted/too-close rejection and empty/nonempty topology controls.
The prefix calls inherited makeMesh on a separate triangle before the target
window is armed. Native selector branches and criteria are not substituted.

Initial three-profile checks pass 6223 native outcomes: 3040 candidate and 3040
pinned-original calls, 84 unobserved candidate normal comparisons, 40 actual
borrowed-best destruction controls, 12 actual stale-observer controls and seven
independent denial/leak/UAF controls. All 1832 original retentions are reproduced
and rejected as candidate qualification. The 1832 matching candidate failures
execute the actual production deleter once, release the ideal with zero scoped
retention and attempt no allocation during cleanup. Both profiles with MSVC
include the empty adjacency-set allocation; byte counts remain ABI-specific.

All 3040 original observations and exits exactly match the sealed diagnosis.
Candidate/original pairs retain 84 exact normal and 2956 denial/window-state
comparisons outside the explicitly repaired pending fields. Four ASan stale
controls actually consume the freed ideal after omitting production observer
removal. The other eight observe the stale pointer without dereferencing it and
are rejected by the candidate contract. Forty original wrong-best cleanup
controls actually destroy a live borrowed candidate and exit before further
consumption; they do not establish completed teardown. The seven independent
controls require actual allocation denial, retained storage and ASan expired-read
detection. Windows ASan is not used as a leak detector.

Every denial checks live original vertex owners/adjacency, edge owner counts,
exact ID timing and committed Face identity/endpoints/midpoint/area. Twelve later
owner-adopted/view-publication failures remain separate. Borrowed selection after
ideal retirement retains the live borrower under later angular failures.
Thirty-four checker/source-preparation tests challenge retention, cleanup count/
allocation, stale observers, premature adoption, borrower and Face-prefix state,
selection and missing/ambiguous observation anchors. These bring local tooling
to 356 Python tests and add application.ideal_vertex_ownership (72 CTest entries).

## Exact delivery gates and limitations

Local commands, raw observations/logs, source/executable identities and source
reversal live under build/ideal-vertex-repair. Initial results are preparation;
require full regression on the exact delivery head and merged main before
integration is qualified. Each revision requires all 72 CTest entries with zero
failures/skips, 356 Python tests, the full 6223-outcome native matrix, independent
raw-inventory/diagnosis replay, source reversal and scoped production/positive-
fixture/header analysis. Require separate actual UAF/leak analyzer detections,
canonical formatting, whitespace, source inventory/contracts and staged-byte
checks. The initial formatting check rejected a line wrap in the new owner;
explicit formatting corrected it without changing other production bytes.
The historical failures and initial executables remain retained separately.

Fresh Eistute/Book runs must preserve nine scientific states, 45 artifacts,
accepted/rejected decisions, independently checked physical/UV quality and 123
positive boundary-incidence comparisons against qualified main. Preserve all 66
protected raw article inputs and prior negative/inconclusive evidence. Audit
remote main, branches, PRs and checks before publication/integration, and repeat
validation on exact main after merge. No hosted checks are configured.

The two edge-based guard modes use sparse frontVertices containing only the base
endpoints. They qualify those native guards, not a complete public advancing
front. The negative-distance guard remains unreached for this positive-height
horizontal-base fixture; its retirement replacement has source-reversal evidence
only. Arbitrary aliases/orientations, all tie branches, public/full geometric
makeMesh allocation-failure paths, retry/rollback, whole-process/parallel,
LSan/UBSan and performance/global quality remain unqualified. Successful frozen
application comparisons do not extend the focused failure-path coverage.

After delivery, the next separate item is a source-preserving diagnosis of ideal
Vertex lifetime through the public geometry-front caller, using unchanged native
selection and policy. Stage 3 remains open with 37 numbered qualified slices;
this repair adds none. Stages 0-2 remain closed for measured scope; stages 4-11
remain pending. The relative-area experiment remains negative and inverse-
direction trials remain unapproved/unexecuted.
