# ADR-0008: commit parametric midpoint replacement after preparation

Status: candidate qualified; exact-head and post-merge gates required.
Issue #26. Classification: behavior-changing defect repair on allocation-failure
exits, preserving successful scientific computations. No scientific proposal.

## Reproduced boundary

Edge::makeParamMid originally deletes its owned midpoint before evaluating the
curve and allocating a replacement. Each of ten independently calibrated CRT
sweeps fails at the first denied allocation because the previous cache identity
and geometry are already lost. Four patch sides in both incidence directions
and two interior fallbacks are covered. The null-curve branch is a separate
no-op control, not a zero-allocation failure qualification.

## Decision and ownership

Prepare the new Vertex in a local unique_ptr and the normalized length in a
local double. Retain the old midpoint until both computations succeed, then
delete it, release the prepared midpoint into Edge ownership and commit length.
No extra heap metadata is allocated. Endpoints, curve association and other
edge state are unchanged; successful replacement invalidates old cache observers.
An exception preserves the previous owned midpoint and normalized length.

Old-cache destruction moves from before preparation to the final commit. Old
and new caches therefore coexist briefly; no peak-memory improvement is claimed.
Successful allocation count/order, midpoint/arc expressions, oriented intervals,
integration, bisection tolerance/stopping and the null/fallback policies remain.
The address of the replacement may differ because the old cache stays alive;
the public contract does not promise allocation-address reuse.

Curve coefficient and total-length state remain unchanged. The evaluator's
parameter matrix is mutable scratch and is outside the cache transaction.
No guarantee is added for all curve mutation, shared samples, arbitrary input
aliases, other setters or concurrent observer use.

## Independent qualification and limits

The actual production polynomial evaluator is initialized with coefficients
for x(t)=0.3t+0.6t^2+0.1t^3, y=z=0. Position, derivative, signed arc integral
and physical midpoint are checked against independent scalar expressions and
an 80-step monotone inverse. The midpoint bound follows the unchanged physical
residual TOLERANCE and minimum derivative 0.3; existing stricter orientation
controls remain unchanged. Original/repaired success traces must match in each
instrument, including all 11 edge branches, and allocation counts must match.

Ten sweeps deny 30 measured ordinals, requiring exactly one propagated denial,
unchanged cache identity/geometry, normalized length, endpoints/adjacency and
receiver state, followed by successful retry and exactly-once caller teardown.
Observed counts are three allocations per fixture, not portable constants.

Direct point/gradient, arc and midpoint curve operations show zero allocations
in these measured fixtures. Their numerical checks are real, but allocation-
failure coverage inside those operations remains explicitly unmeasured. The
previous deliberate allocation-hook, invalid-access and retained-block controls
remain required. ASan covers normal/invalid-access scenarios; CRT injects the
replacement failures and checks scoped retention. Full-process, parallel,
LSan/UBSan, other curve mutation, initialization and rollback remain open.
