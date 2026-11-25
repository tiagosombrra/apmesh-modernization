# Common trial of one additional native contour division

2026-11-25 Fortaleza. [Measured inputs and outcomes](evidence/COMMON_TRANSITION_CONTOUR_SPLIT_20261125.json).

## Requested and realized sizes

Bind the screened CurvaBezier Step 3 and Ribbed Bracket patch 12 Step 2
archives to their exact original TRI, mixed predecessor, native tree and
certificate. Reproduce every original physical request. Independently
integrate the original and realized arc lengths. For a face request on a
shared edge, compare every incident face and count nonattainment only if
even the smallest is above the target. Face size is median physical edge
length. The earlier seed and construction procedure remains in force.

| Observation | CurvaBezier | Ribbed Bracket |
| --- | ---: | ---: |
| Requested face sites larger than target at native birth | 3/7 | 8/17 |
| Requested curve intervals with at least one child longer than target | 2/2 | 5/8 |
| Short template edge at limiting front operation, model length units | 0.05467 | 0.12500 |
| Size of the seed QUAD / generated TRI next to that edge | 0.05737 / 0.51230 | 0.18828 / 1.06685 |
| Largest unrequested adjacent contour arc, model length units | 1.00000 | 1.00033 |
| That arc divided by seed QUAD size | 17.43 | 5.31 |

Both limiting triangles start at an exposed template edge and reach a
contour vertex. The preceding source tree has no direct face request in
either supporting leaf. Each area has a long contour interval with no
curve request. An unrelated request can be capped, and a requested edit
can produce cells larger than the target. These counters describe
different conditions and both are observed.

## One rule and two native comparisons

For each bound screened control, use the lowest-angle transition TRI
and its incident seed QUAD. Of the two realized contour arcs incident
to that TRI's contour vertex, consider those still unsplit that exceed
1.35 times the seed QUAD's median physical edge length. Request one
original binary division on the largest ratio, breaking an exact tie
by source interval order. The existing pilot supplies the 1.35 factor.
This is a bounded diagnostic rule on a staged control, with no
model-specific coordinates or interval IDs in the selection rule.

The rule selects original interval 8 on CurvaBezier and 1 on Ribbed.
Append one `curve` request to each retained native plan. The selected
arcs split into lengths approximately 0.50000 and 0.50016 units,
respectively. The largest resulting child is still 8.72 and 2.66 times
the original seed QUAD scale. Curve order and all predecessor samples
are certified by the native path. Original face requests, ordered
realized leaves, source artifacts, front selection, smoothing and the
common profile are preserved. Two genuine native candidates stage
using the same retained MSVC x64 Debug C++17 image from PR 278.

| Control → extra split | CurvaBezier | Ribbed Bracket |
| --- | ---: | ---: |
| Certified contour segments | 16 → 17 | 22 → 23 |
| Total elements | 779 → 788 | 648 → 648 |
| Worst transition TRI angle at birth and final | 2.27° → 2.47° | 6.33° → 6.69° |
| Transition TRI below the frozen safety floors at birth | 57 → 47 | 26 → 25 |
| Largest adjacent final size ratio | 8.93 → 8.66 | 5.67 → 5.54 |
| Area-weighted geometric RMS at 2,304 common sites | 0.00907903 → 0.00818150 | 0.01736485 → 0.01732849 |
| Maximum geometric deviation at 2,304 common sites | 0.04419218 → 0.04419218 | 0.10749591 → 0.10749591 |

The original worst TRI is absent from both new native birth meshes.
The new worst TRI on Ribbed is born against the same template edge
using the newly inserted contour vertex. On CurvaBezier, a different
part of the transition limits the result. The final minimum interior
TRI angle drops from 14.36° in the control to 4.43° with the extra split.
The geometry improves in both models, with sampled RMS reductions
of 9.89% and 0.21% relative to the screened candidates. Both staged
candidates are blocked by the unchanged progressive profile. Ribbed
still exceeds growth relative to its own mixed predecessor at 18.46%.

## Scope and next action

The two runs complete in approximately 97 and 58 seconds including
assessment, against their immutable archived input. The native source
and image are reused. Local progressive controls pass 10/10 on the
exact PR 279 assessor tree, whose four hosted checks pass. The local
validation planner lacks its baseline receipt. The bounded directed
native runs and exact artifact checks supply the reported evidence.

The two results show a modest repeatable effect from one division.
They also expose the remaining size gap and the shift of some poor
elements into the CurvaBezier interior. Keep the frozen profile.
Next project a common sizing correction that can adjust the supporting
template scale as well as contour intervals, with 2:1 tree balance
and protection of active size requests. Assess the entire transition
and adjacent interior before native adoption. No accepted mixed epoch,
reserved-model run or global mixed-curvature qualification.
