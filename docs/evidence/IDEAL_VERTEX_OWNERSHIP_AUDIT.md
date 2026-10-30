# Geometry-phase ideal Vertex ownership diagnosis

This is an engineering diagnosis with unchanged production source, tests,
formulas, ordering and scientific policy. No ownership repair or repaired-memory
qualification is included. Baseline: PR #123 main
`cf7ab68e5e7a9d2b3467c861bf967f86bb393023`. Its 71 CTest/322 Python tests,
2663 native outcomes, nine scientific states/45 artifacts and 123 boundary
comparisons remain preserved; this documentation delivery does not rerun or
claim new scientific experiments.

## Actual ownership boundary

In findBestVertex, geometry-phase best receives the raw result of makeIdealVertex.
That helper obtains Edge::normal's new Vertex, scales it by the cell height and
adds the edge midpoint. The measured ideal is (1,2), with h=2. The same best
variable later serves three different roles: unadopted ideal, adopted ideal and
borrowed existing candidate. It is not a stable ownership token.

Allocations in the local list, candidate/interception operations and list
publication can throw while the ideal has no owner. The successful adoption
order is setId(++lastVertexId), frontVertices observer, innerVertices owner,
vertices view. Failure of the first publication retains the ideal; failure of
the second also leaves the front observer. Failure of the third already has an
innerVertices owner and the fixture's normal destructor retires the ideal.

Existing selection deletes the ideal before assigning a borrowed best and
constructing the qualified angular temporaries. Those later failures do not
retain the ideal. Unconditional deletion of best on exception destroys a live
borrower. Near-base, intercepted-ideal and too-close guards retire the ideal
normally. The negative-distance guard was not reached: for the horizontal base
and positive cell height, the ideal-centered radius-h disk touches the base and
does not contain below-base candidates. This is a fixture coverage limit,
not a global reachability result.

## Measured native evidence

The standalone C++17 fixture exposes the inherited findBestVertex without
overriding it. It prepares the native quadtree through subdivideToLevel(2), a
horizontal base and owned native vertices/edges. Seven modes, two candidate
orders and zero/one committed Face prefix produce 28 contexts per profile.
The prefix calls inherited makeMesh on a separate triangle before observation
is armed. No target-selector denial is injected into that prefix.

Modes cover ideal adoption, existing selection, near-base rejection,
intercepted-ideal rejection, too-close rejection, and empty/nonempty topology
controls. The two edge-based guard modes intentionally provide a sparse
frontVertices list containing only the base endpoints; they measure those
native guards, not a full public advancing-front state. Existing selection
compares two candidates with distinct angles and selects the same vertex in
both orders. These direct-selector fixtures do not qualify full geometric
makeMesh integration, public-wrapper sorting, arbitrary aliases or tie behavior.

| Observation | Verified outcomes |
| --- | ---: |
| Normal observed/unobserved pairs | 84 |
| Original allocation denials | 2872 |
| Beyond-window normal controls | 84 |
| Original unowned ideal retentions | 1832 |
| Explicit caller cleanups without allocation | 1832 |
| Already-owned view-publication failures | 12 |
| Geometric borrowed-selection failures after ideal retirement | 40 |
| Actual borrowed-best destruction detections | 40 |
| Actual stale-front-observer ASan reads | 4 |
| Independent denial/leak/UAF instrument controls | 7 |
| Rejected observation corruptions | 31592 |
| Rejected source-anchor corruptions | 32 |

There are 5007 verified native outcomes: 168 normal calibration calls and 4839
matrix calls. All calibrated allocation ordinals are denied individually, with
one beyond-window control per context/profile. Retentions comprise 64 GCC and
884 per MSVC profile; 892 occur without a Face prefix and 940 with one. GCC
retains one block/80 bytes; MSVC ASan and CRT retain two blocks/88 bytes, including
the empty adjacency-set allocation. These values are profile/ABI-specific.
ASan checks actual invalid reads; leak observations use the scoped allocation
ledger or CRT heap checkpoints, not an unavailable leak sanitizer.

Every measured denial checks live original vertex owners, adjacency, unchanged
edge owners and the committed Face's identity/endpoints/midpoint/area. Explicit
caller cleanup removes any matching unadopted front/view observations before
deleting the ideal. It attempts no allocation, and all 1832 cleanups retain zero
scoped storage. This is a diagnostic control, not production cleanup. Wrong-best
deletion actually destroys the borrowed candidate; observer omission actually
reads the freed ideal through frontVertices under ASan. Twelve owning-list
success/view-failure states remain separate from pending-ownership failures.

## Source preservation and failed preparation

Production source SHA-256:
`3ff81c2cbace49c73de8e0eca1e35bac07c5a5aeb4f5d75e33f636d443b816bc`.
The copied native source has 16 reversible observation edits. Unique anchors
fail closed on 32 missing/duplicate-anchor corruptions; exact reversal recovers
the original source. Normal outcomes and selected coordinates/IDs agree with
the unobserved source in all 84 comparisons. All tracked inputs, the preceding
repair's evidence/application and 66 protected raw article files are unchanged
at the diagnosis seal. No historical source repository is modified.

Local artifacts remain under build/ideal-vertex-ownership-audit. Commands are
recorded in profiles-build.json and final-build.json; calibration/report.json,
matrix-qualified/report.json and verification.json retain native observations,
executable/source/log hashes, complete inventories and checker controls.
[The compact tracked seal](stage3/ideal_vertex_ownership/summary.json) identifies
the exact verification artifact.

The initial GCC configuration lacked Ninja on PATH; the failed configuration
and attempted build logs remain preserved. The qualified toolchain PATH was
then used explicitly. rejected-pilot-1 retains a prefix-observation error and an
interception fixture that did not reach its intended guard. Those pilots are
not qualification. The initial matrix stopped after 71 outcomes because its
wrong-deletion message check expected LF rather than Windows CRLF. The actual
control exited with the required borrower-destruction diagnostic. Its original
report, checker and logs remain immutable; the corrected executor reuses those
71 exact hashed outcomes and continues in matrix-qualified. No failed result is
discarded or described as a repaired candidate.

## Next repair and delivery gates

The next single repair must keep a dedicated exclusive owner independent of
best, starting before the first later throwing operation. Retire that owner at
the original guard/existing-selection points. Keep it through front observer
publication, remove that observer on failed adoption before deleting the ideal,
and release immediately after innerVertices insertion. Never delete borrowed
best and never apply pending cleanup after owner adoption. Preserve original
ID consumption, allocation/publication order, successful selection, committed
prefixes and later already-owned partial states; do not add general retry or
rollback. That implementation would be a behavior-changing exception-safety/
ownership defect repair, preserving successful scientific behavior.

Require complete native sweeps, actual nonallocating production cleanup,
borrower/adjacency/prefix checks, original failures and actual invalid controls,
exact normal comparisons and full exact-head regression/scientific/tooling
gates. Merge only after required gates pass; repeat them on exact main. This
diagnosis does not substitute for those repair gates.

This documentation-only delivery requires 71 CTest contracts and 322 Python
tests on its exact head and merged main, whitespace/inventory/staged checks,
sealed native evidence, unchanged production/application/raw inputs and fresh
remote main/branch/PR/check audits. No hosted checks are configured. Stage 3
remains open with 37 numbered qualified slices; no new slice, full-process
lifetime, numerical quality or performance claim is made.
