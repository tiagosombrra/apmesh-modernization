# ADR-0015: prepare serial adapter samples before cache/parameter publication

Status: candidate qualified; exact published-head and implementation-main gates required.
Issue #47. Classification: ownership/exception-consistency defect repairs plus
engineering consolidation of two byte-identical serial construction tails.

The original publishes parameters before allocating clones/interiors/output and
incrementally inserts raw endpoint values/aliases into the cache. Strict sweeps
stop in 27 cases at first parameter value/list-node change, before consuming
invalid observers. Subsequent ordinals and CRT retention in those aborted cases
are unmeasured. Three retention-only sweeps reclaim every reachable new pointer
and permit partial original state without a rollback/retry claim; they finish
with 32 retained CRT blocks each across all their denied allocations. Other 58
original outcomes are expected. Endpoint cloning and interior construction can
lose unowned nodes independently of the measured early publication failure.

Prepare copied parameters, pending unique nodes, all list nodes and a map of
desired cache changes before touching live parameters/cache. Resolve front then
back against the original cache and staged new entries, preserving closed alias
reuse. Copy endpoint nodes with exactly the original scalar/adjacency semantics;
sample interiors at the same parameters and request IDs in the same order.
Stage both source mappings and current-endpoint self-alias overwrites. During
commit, assign values in existing cache entries, merge remaining prepared map
nodes, swap parameter lists and release node owners. Default allocators match;
the fixed pointer comparator cannot throw and no commit operation allocates.
Existing cache entry nodes remain stable on success and failure.

A named return list can require an allocating move when optional NRVO is not
performed. Committing before return would therefore leave a failure window.
A local scope-success guard records std::uncaught_exceptions() and commits in
its nonthrowing destructor only after return construction succeeds. When return
construction throws, it skips commit and pending owners clean up. The two actual
Adapter methods return the helper's prvalue directly, with mandatory C++17
elision at those forwarding boundaries. The new target consistently disables
optional NRVO only for this qualification. An actual MSVC std::list move denial
control observes the allocation and preserved move source; strict final denials
occur after all expected ID requests and still preserve parameters/cache.

Inputs and cached samples remain borrowed. The caller retains collective lifetime
authority for unique newly created result nodes; the cache is not a separate
owner. Endpoint adjacency remains copied, without owning its observed elements.
Consumed IDs and mutable evaluator scratch are not rolled back. The boundary
begins after upstream point sorting/parameter selection, with initialized actual
parametric/Bezier/Hermite curves, at least two captured points/selected parameters,
NodeAdaptive endpoints/cache values and a live manager. Curve point observers are
not published here. Full Adapter/AdaptCurve/mesh rollback, invalid/custom sources,
allocator/comparator substitution, ID overflow/wrapping and parallel use remain
outside the measured contract. Distinct parametric and physical roles remain.

Original comparison: 14 Git-pinned production units plus an exact tail adapter,
both serial source tails verified equal; no body substitution or full historical
Adapter/Generator instrumentation. Candidate: 15 actual units. New Debug CRT
disables iterator metadata consistently while retaining actual heap checks and
all negative controls; no level-2 recovery or cross-compiler ABI claim. Valid
87-case preliminary reports remain retained before the explicit return control.

Candidate 88/88, 702 injected ordinals/30 positive sweeps; all 54 full normal
traces match original with independent x=t,y=t*(1-t) analytic samples. Prior
eight batteries, CTest 24/24/zero skips/74 controls, actual new-unit read-only
lint, explicit formatting/inventory and exact twice-repeated default models pass.
Preparation changes allocation timing/counts/bytes/peak storage; no performance
claim. No numerical formulas/order, sorting/selection, boundary synchronization,
quadtree/templates/front, tolerance, budget, verifier or acceptance/stopping
policy changes. Full stage 3 and stage-8 API documentation stay open.
