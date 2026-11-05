# Curvature cost and selected production scope

Disposition: documentation-only diagnosis and one engineering package selected;
no implementation, timing improvement or qualification is claimed. Starting head:
050a230bcb9bc86ca227ad6b6be82c137f7904bd. Supports the blocked S3-08 adaptive-reuse
prerequisite without closing a ledger row. No generation, stack capture, native
runtime control or regression campaign was launched for this decision.

## What the retained observations establish

The corrected first-call MSVC report records curvature_aux=50.2315 s, patch
reconstruction=82.6533 s and full_without_io=152.153 s. Slot 6 surrounds both
CurvatureAnalytical and CurvatureDiscrete construction, their four curvature
results and node scalar updates. Slot 7 accounts separately for error reduction.
The 50.2315 s cannot be assigned to either curvature implementation or to one
function. The fixed two-call process still times out at 300 s.

Historical timeout stacks at 10/60/290 s reach CurvatureAnalytical -> FindUV ->
Parameterize/CalculatePointUV and Eigen evaluation; the 290 s chain is inside
ErrorGlobal. A later unchanged-binary sample at 180 s reaches NodeAdaptive
destruction through Adjacent::ConfirmLeftAdjacency/GetElementLeft and discrete
adjacency sorting. Sparse scheduled samples are reachability, not runtime shares.

Byte comparison against both sampled source revisions finds curvature_analytical.cpp,
curvature_discrete.cpp and patch_bezier.cpp unchanged at the starting head.
adjacent.cpp has changed: exact triangles now use point snapshots. Its historical
GetNoh node-copy destruction therefore cannot diagnose that current fast path.
Analytical curvature already calls FindUV once per construction, followed by five
derivative evaluations using that result. Reusing stored mesh UV instead would
alter the established inverse-solver path. The prior operand-copy candidate stays
rejected; no Eigen rewrite, solver/tolerance/I_MAX change or numerical cache is
selected here.

## One selected package: transfer discrete-adjacency list nodes

CurvatureDiscrete::AdjacencySort copies the input observer list into a private
working list. It seeds its ordered list using push_back/pop_front. Each selected
left/right neighbor is then erased by Adjacent::GetElementLeft/GetElementRight
and inserted into the ordered list with push_back/push_front. These operations
deallocate and allocate a list node for the same borrowed element pointer.

Replace only those transfers with std::list::splice: seed at the destination tail,
left matches at its tail, right matches at its head. Transfer-capable Adjacent
operations must retain the same first-match scan and existing Confirm predicates;
keep the three-argument legacy getters' contracts. Both private lists use the same
standard allocator. Only private list-node ownership moves; elements remain
borrowed and the source NodeAdaptive observer list is untouched.

Retain the working-list copy, saved NodeAdaptive value, unconsumed entries, all
boundary/closed-fan decisions and the extra circular duplicate push_back. That
duplicate is a second incidence and must not be replaced by moving its first
entry. Empty-adjacency preconditions and failure recovery are separate obligations.
No geometry, comparison order, area/angle sum, concavity, curvature formula,
virtual fallback or acceptance/stopping policy changes are admitted.

Source-derived expectation: transferring r selected incidences removes r node
allocation/free pairs, including the seed. This is not a measured allocation
count or evidence that this work dominates the 50.2315 s phase. It does not predict
a speedup or resolution of the 300-second gate.

## Finite acceptance and stop rule

Implement in the two curvature units and Adjacent's header; reuse the existing
native fan fixtures and metrics probe. Require an independent frozen pre-change
ordering/scalar oracle: the current 60-case test compares two element dispatch
paths through the same CurvatureDiscrete and alone cannot detect a shared sorting
regression. Check first-match duplicates/unmatched entries, both transfer ends,
unchanged source observers, circular multiplicity, virtual dispatch and bitwise
mean/Gauss results. Use the existing real Debug CRT mechanism with a positive
allocation/free control to verify the bounded transfer saving and full release.

Require canonical C++17 GCC/checked-MSVC builds, scoped analysis, source-order
proof and the existing regression/frozen scientific checks. No new model, test
target or automatic 300-second rerun belongs to this package. Stop at the first
unexpected failure; preserve it without weakening the oracle. Changed allocation
failure ordinals require explicit treatment, not reuse as unchanged evidence.
The timed pair, revised-head Book, exact-delivery/main and Stage 3 gates remain.

Retained hashes, source-continuity comparison and compact historical stacks:
build/curvature-cost-selection/. This decision ends the diagnostic item; the next
item is the bounded production implementation above, not another source audit.
