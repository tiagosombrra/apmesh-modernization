# Native trace of the limiting CurvaBezier interior triangle

2026-11-25 Fortaleza. [Draft PR 274](https://github.com/tiagosombrra/apmesh-modernization/pull/274)
head `84113d9c375a1bdd89fbe4f653d4787dab86241d`.
[Machine-readable trace receipt](evidence/GUARDED_INTERIOR_FRONT_TRACE_20261125.json).

## Reproduction

Retain the guarded birth front, active directed edges, seed cycles and
prospective TRI/QUAD decisions. The normal article frame schema remains in
place for unguarded histories. The guarded archive keeps native smoothing
frames and pass decisions in its existing directory.

One directed MSVC invocation replays the source and full input plan of
the [selective CurvaBezier candidate](RELATIVE_MIXED_TRIGGER_20261125.md).
The original TRI, mixed predecessor, native tree, candidate OBJ, pre-
and post-smoothing frames and pass log reproduce byte for byte.
The independent polygon replay checks all 112 commits and refuses an
injected reversal of the recorded active edge. The two-model portable
suite matches the exported ordered cycles to native birth geometry.
The standard article application, six native source captures with 54
negative controls and 39 Python tests pass locally.

## The operation that creates the limiting face

Operation 83 creates physical face 751 at a seed QUAD edge. Its base is
the UV segment from (0.125, 0.84375) to (0.125, 0.875), on seed QUAD 208.
The advancing front has 44 directed edges and 43 active vertices. Only
two apices satisfy the current validity conditions even when all active
vertices are examined. Both are already in the local candidate pool.
They give minimum physical angles of 6.37 and 6.95 degrees. The original
UV opposite-angle rule chooses the first. The only convex prospective
union at that state has S = 1.65596. None meets S <= 1.5.

The short edge is active in all 83 measured prefix states. Its eligible
QUAD is available before operations 1 through 13. At operation 13,
the existing chosen outer base can itself produce the same QUAD from
additional local pairs. Nine apices are valid for that base; the first
TRI chosen by the current rule misses the eligible pair. The alternative
has S = 1.50 under both the angle-check methods and a minimum physical
angle of 41.86 degrees. The original native TRI at operation 13 has
a 12.49-degree minimum and removes this local opportunity. An independent
scan finds operation 13 is the first possible change when complementing
the search in the unchanged prefix. A new full run is needed to assess
all subsequent effects.

## Decision and next check

The researcher approves a controlled experiment on this same input.
When the existing base decision would retain a TRI, inspect remaining
local triangle pairs on that base, without expanding the original
search window or reordering edges. Select the lowest S among eligible
QUAD pairs. Use deterministic ties and retain the original TRI if
none qualifies. Keep the curve, quadtree, templates, shape limit and
smoothing. Compare the actual first changed operation, native validity,
regional shape, geometric error, growth and elapsed time. No policy
for reserved cases or scientific acceptance is adopted.
