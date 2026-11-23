# One native child-arc subdivision at the worst Ribbed QUAD

Recorded 2026-11-23 Fortaleza. The researcher approves only the
[proposed QUAD-edge test](RIBBED_LIMITING_CHILD_ARC_20261123.md).
Compare one isolated MSVC Debug C++17 reconstruction against
the retained [residual-only control](RIBBED_PREFRONT_SHAPE_TARGET_20261123.md).
Use the same guarded Step 2, existing residual requests, quadtree
cap 4, area-centroid templates, 1993-style mixed front and guarded
smoothing. See the [receipt](evidence/RIBBED_SINGLE_QUAD_EDGE_SPLIT_20261123.json)
for source, image, log and mesh hashes.

The build succeeds in 7.34 s. One native application exits zero
in 37.00 s within 180 s. Its guarded Step 2 and all five ordinary
prefix OBJs match their references. The physical size traces,
native curve dispatch for the original intervals, tree requests,
capped request and final tree leaf ledger are byte-identical to
the control. Both use 133 balanced leaves and the same one
capped request at depth 4.

The additional native split acts on child 13 of original interval
7, side 1. It adds only the archived native midpoint
at parameter 0.94042301864940081. All 22 old ordered contour
site identities and UV/XYZ coordinates survive. The old arc
1.0202140236282629 divides into 0.510138742512811 and
0.510075281115463, both within the 0.62666374011172654 request.
Unchanged output contours, except the single new point, and
oriented connectivity equivalence for the typed final output
are checked independently.

## Measured element shape and size

| Measurement | 22-segment control | 23-segment experiment |
| --- | ---: | ---: |
| Nodes | 623 | 624 |
| TRI | 74 | 75 |
| QUAD | 574 | 574 |
| Worst QUAD angle before smoothing (degrees) | 25.34 | 26.06 |
| Worst QUAD angle after smoothing (degrees) | 25.34 | 26.26 |
| Worst TRI angle before and after smoothing (degrees) | 6.33 | 6.33 |
| Worst final TRI shape q | 0.18955 | 0.18955 |
| Worst final QUAD scaled corner Jacobian | 0.32333 | 0.32333 |
| Largest adjacent face-size ratio | 5.67 | 5.67 |
| Final area-weighted XYZ RMS on 576 common sites | 0.01730327 | 0.01726722 |
| Final largest sampled XYZ deviation | 0.10280772 | 0.10280772 |

Use positive UV overlap with the two old limiting faces to
measure their local coverage. The old QUAD region is 61.04
percent covered by a QUAD of 47.68 degrees and 38.96 percent
covered by a TRI of 25.11 degrees, unchanged by guarded smoothing.
The minimum angle over either type in that region therefore
changes from 25.34 to 25.11 degrees. Both global QUAD minima move
to different places (before and after smoothing). The original
limiting TRI region contains the same TRI and minimum angle.
This is a small increase in global QUAD minimum angle with a
local TRI/QUAD trade-off and no improvement in the other measured
shape minima or largest size jump.

The original unguarded 22-segment control fails its first pass
on a UV QUAD. With this one extra point the unguarded comparison and
the guarded experiment each complete five valid passes. Independent
frame checks verify oriented topology, fixed contour, analytic lift
and physical corner shapes in all ten frames. The paired metrics
in the table compare the guarded outputs.

## Disposition

Retain the one-point result as a valid experimental observation.
Neither a general second-split policy nor a mixed acceptance
decision is established. There are zero accepted mixed epochs.
Full native regression, hosted checks, CRT/sanitizers, shared
boundary adaptation and mixed global curvature remain outside
this trial.

Next read the template-edge classification and prospective front
shape choices at the unchanged 6.33-degree TRI, with its satisfied
contour targets. Use those observations to align a bounded local
change before any further reconstruction. Keep the measured
single-split benefit and local penalty visible in the comparison.
