# Coordinated native contour and template sizing trial

2026-11-25 Fortaleza. [Projection, native results and lineage](evidence/COORDINATED_TRANSITION_SIZING_20261125.json).

## One common grouping rule

Use the two [split-only candidates](COMMON_TRANSITION_CONTOUR_SPLIT_20261125.md)
as the controls. They already realize one extra native binary split.
From each original screened limiting TRI, locate the leaf supplying
its exposed template edge. Project the immediate parent of that leaf
in the split-only tree. Require four leaf children, an interior parent,
positive native template clearance, global 2:1 edge balance, and the
existing grouping guard for all requests in the parent and side-adjacent
leaves. Require the existing template dispatcher to replace the short
edge by a longer one below the realized contour arc length. The same
rule selects both parents by observed topology.

| Projection | CurvaBezier | Ribbed Bracket |
| --- | ---: | ---: |
| Projected historical template | T5 | T2 |
| Realized leaves before → after grouping | 226 → 223 | 133 → 130 |
| Supporting physical edge before → after | 0.05467 → 0.10695 | 0.12500 → 0.25000 |
| Longest child arc / supporting edge, before → after | 9.15 → 4.68 | 4.00 → 2.00 |
| Seed QUAD in grouped block before → after | 16 → 11 | 16 → 11 |

Append one existing `group_feedback_parent` directive to each
split-only plan. The retained native application verifies the same
predecessor, request trace and contour certificate byte for byte.
The comparison removes exactly four child leaves and adds their parent
in each case. Both projected template boundary edges and both sets of
11 parent seed QUADs appear in the native birth mesh. Reuse the exact
PR 278 MSVC x64 Debug C++17 executable and the PR 279 assessor.
No numerical policy, generator source or profile is modified.

## Native results relative to the split-only controls

| Final measurement | CurvaBezier | Ribbed Bracket |
| --- | ---: | ---: |
| Certified contour segments | 17 → 17 | 23 → 23 |
| Total elements | 788 → 782 | 648 → 635 |
| Minimum transition TRI angle | 2.47° → 2.47° | 6.69° → 6.86° |
| Transition TRI below the safety floors | 47 → 47 | 22 → 19 |
| Minimum interior TRI angle | 4.43° → 7.89° | 18.37° → 18.37° |
| Interior TRI below the safety floors | 4 → 3 | 0 → 0 |
| Largest adjacent size ratio | 8.66 → 8.66 | 5.54 → 5.51 |
| Area-weighted RMS at 2,304 common sites | 0.00818150 → 0.00818118 | 0.01732849 → 0.01734660 |
| Maximum sampled deviation at 2,304 common sites | 0.04419218 → 0.04419218 | 0.10749591 → 0.10748411 |

Both runs stage. CurvaBezier improves the poorest interior TRI
while retaining its transition blockers. Ribbed reduces the number
of poor transition TRI and its sampled maximum, with an RMS increase
of approximately 0.10% versus the split-only control. Both still
reduce RMS and the sampled maximum versus their exact mixed predecessor.
Ribbed's growth falls from 18.46% to 16.09%, above the frozen 10%
limit. CurvaBezier stays within its growth budget. The profile blocks
both because of shape, and also blocks Ribbed because of growth.

The remaining failures are spread along the transition. In the
coordinated CurvaBezier, 44 of the 47 sub-floor transition TRI were
born using a template edge as their active base. Of the 47, 46 share
at least one edge with a seed QUAD. On Ribbed all 19 remaining
sub-floor transition TRI have a template edge as their active base.
The worst final angle is already present at birth at operation 109
on CurvaBezier and operation 47 on Ribbed. These observations support
measuring the size mismatch along the transition before the front
closes. Limiting the adjustment to one parent leaves multiple
affected template edges untreated.

## Verification and next action

The initial projection passed the clearance metadata object instead
of its scalar factor. The corrected audit reads the factor from the
archived policy and verifies both joint projections. Ten local
progressive tests and all four retained hosted checks on each of
PRs 278 and 279 pass on their exact source revisions. The validation
planner lacks its local baseline receipt. Two directed native runs
complete in approximately 57 and 36 seconds, followed by exact source,
contour, tree and mesh comparisons.

Next examine the physical spacing of the entire contour-to-template
interface before advancing-front closure. Use the existing protected
grouping and binary subdivision to project a bounded set of changes
against the same growth and regional quality controls. Prioritize the
measured deficit across all affected edges, with the same rule on both
models. No accepted mixed epoch, reserved case, shared-curve validation
or global mixed-curvature qualification.
