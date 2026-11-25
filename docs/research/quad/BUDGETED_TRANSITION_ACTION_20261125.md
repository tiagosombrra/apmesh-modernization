# Prioritize a realizable native transition action within the face budget

[Draft PR 286](https://github.com/tiagosombrra/apmesh-modernization/pull/286)
at `7ec6cc137f8a1abe32cde69c86b4465c099b7e29` adds a read-only planner
for grouped fixed-vertex controls. It binds the original mixed mesh,
the existing requests and the ungrouped native tree used to protect
grouped cells. It ranks transition TRI below the frozen safety floors
by final physical minimum angle, then TRI shape and face order.

At each TRI with an exposed template edge, first consider an unsplit
original interval incident to the same contour vertex. Its arc must
exceed 1.35 times the short edge. The proposal uses one existing
binary subdivision. If the curve action is unavailable, consider
grouping four original leaf siblings at the short template edge.
Preserve disjoint previous groups, native 2:1 balance and the existing
protection of every request inside the parent or on a neighboring leaf.
Require a longer projected support edge for an interior group.
For a contour parent, use the existing front handoff and require the
short template edge to disappear. The first ranked, affordable action
becomes the sole addition to the native plan.

## Face upper bound

For a connected conforming chart disk with TRI and QUAD,
`T + 2Q = 2V - B - 2`. Thus its face count is bounded by
`2Vmax - B - 2 - Qmin`. All nodes in this fixed-vertex trial come from
seed template sites and the certified contour. With one new curve
split, omit the original interval's clearance condition when estimating
the maximum set of newly seedable cells. All previously seeded cells
stay, which supplies a lower bound for the number of QUAD. With a
grouped replacement and fixed curve, project both seed sites and
seed QUAD on the grouped tree. Verify the old projection against
the native record, then verify the upper bound against the actual
candidate. This bound does not predict the exact face count or quality.

## Native results

Both comparisons reuse the [combined grouped controls](CONTOUR_TEMPLATE_HANDOFF_20261125.md)
and the native C++17/MSVC engine from PR 284. All pre-existing geometric
requests, subdivisions and template groups are preserved. The original
mixed predecessors have 732 and 547 faces. The profile allows up to
805 and 601 faces, respectively.

| Metric | CurvaBezier control → trial | Ribbed Bracket control → trial |
| --- | ---: | ---: |
| Selected action | One split, interval 9 | One protected contour group |
| Selected TRI rank | 1 | 14 |
| Projected candidate upper bound / profile maximum | 771 / 805 | 556 / 601 |
| Native final faces | 704 → 731 | 538 → 534 |
| Certified contour segments | 17 → 18 | 23 → 23 |
| Worst TRI angle in the selected footprint | 3.15° → 5.42° | 13.58° → 15.86° |
| Worst TRI angle across the transition | 3.15° → 3.25° | 8.06° → 8.06° |
| Transition TRI below the frozen floors | 37 → 30 | 14 → 12 |
| Area-weighted geometric RMS, 48 × 48 | 0.007765 → 0.006626 | 0.017874 → 0.020301 |

The local metrics include final faces with positive UV intersection
with the original selected TRI. CurvaBezier uses one native midpoint
on the unsplit original arc, producing arc lengths 0.49999 and 0.50001
with identical grouped leaves. Ribbed excludes the parent from
template dispatch, changes the seed count from 455 to 451 and removes
the observed short template edge. Ribbed RMS rises 13.6 percent
relative to the grouped control. Both still reduce geometric error
relative to their own mixed predecessors and pass the size budget.
Both remain blocked on whole-mesh shape. Zero mixed epochs were accepted.

The Ribbed 8.06° TRI uses a template group protected by four geometric
requests. Its incident original intervals have both already been
subdivided. A read-only child-interval projection finds two candidate
subdivisions, each with a conservative cap of 557 faces. The equal-arc
point above the template edge produces a 13.19° TRI in a fixed-edge
calculation; the other point produces 0.93°. Neither is a full native
prediction or passes the TRI floor in this calculation. The native
plan currently accepts only one split per original interval.

## Validation and next action

Six Python sizing and ten admission controls pass. The projection is
deterministic on both archives and refuses a mismatched ungrouped
source without producing a plan. Both native candidates realize their
selected actions. Exact-Ribbed control publication succeeds. The fresh
CurvaBezier control writes eight artifacts that match the archived
control byte for byte, but Windows denies the rename of its pending
directory. The run is failed and the directory is left intact.
The matched control from PR 284 at the same executable hash remains
the published baseline. The previous rollback gate remains open.
[PR 286 hosted checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45709796800)
were in progress. The [evidence packet](evidence/BUDGETED_TRANSITION_ACTION_20261125.json)
retains commands, file hashes, per-region measurements and the failed
control receipt.

Next align whether to support one further certified subdivision of
a child interval, retaining original and inserted samples. First
verify the native request and certificate semantics against that
target. The shared curve, reserved cases, native rollback
qualification and global mixed-curvature error remain open.
