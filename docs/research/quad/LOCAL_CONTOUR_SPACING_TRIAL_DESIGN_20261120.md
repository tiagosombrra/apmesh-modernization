# Local contour spacing trial design

20 November 2026, Fortaleza. The active transition issue is the gap between
the native curve partition and the exposed quadtree templates. The previous
[front-order experiment](MIXED_TRANSITION_SHAPE_20261120.md) retained the same
physical mesh and three narrow triangles. This document specifies the
next comparison on the same native `curva_bezier` fixed-`1.5` history.

## Locate the native interval

The Step 3 witness comes from the left side `u=0`, curve 3 with no
parameter reversal. The original curve-only pass emits `0|1`; the surface
pass and final partition emit `0|0.5|1`. The relevant oriented mesh interval
runs from `(0, 0.5)` to `(0, 0)`. The curve length is 1 in physical units
on this straight interval. The native source record stores the arc midpoint
at `(0, 0.272552490234375)`. The physical midpoint is approximately
`(0.4999905, -1, 0)`, leaving approximately half a unit on either side.
Its UV coordinates are unequal halves because the curve parameter has a
nonuniform relationship to arc length.

The exposed template edge `[13, 349]` runs from `(0.125, 0.125)` to
`(0.125, 0.15625)`, is 0.04731 long in physical space and lies on leaves
0.0625 wide in UV. As a geometric illustration, joining the stored midpoint
to that same edge would raise the triangle's smallest physical angle
from 1.42 to 8.43 degrees and lower its longest-to-shortest edge ratio from
15.08 to 5.91. This is one hypothetical triangle on fixed archived geometry.
A new native domain and front are free to choose another connection.

## Proposed bounded comparison

1. Use the same fixed-`1.5` configuration and one local isolated research
   application invocation. On Step 3, first attempt, identify curve 3
   and the exact native binary-tree leaf `[0, 0.5]` after the surface pass
   and existing neighbor restriction. Preserve the rest of that partition.
2. Run `BinTree::Subdivide(CurveAdaptiveParametric*)` once on that leaf.
   It calls the existing arc-length midpoint operator. Apply the existing
   `BinTree::Restrict` to restore adjacent-level constraints and verify
   the expected result `0|0.272552490234375|0.5|1`. Use the existing
   `BuildCurveSamples` publication so native identity, ordering and curve
   ownership remain under the same contracts. Guard the intervention
   to the isolated research case.
3. Let native TRI regenerate the source domain from this partition and
   retain the real acceptance or rejection. Replay the actual chosen
   quadtree with the existing clearance, seeds, mixed-front rules and
   fixed-contour smoothing. The TRI control and its default configuration
   stay the reference. The experimental TRI source can produce a different
   domain or reject Step 3. The clearance formula stays fixed and its
   effective width changes with the new lengths.
4. Bind both Step 3 attempt-zero records to source TRI status and counts.
   Verify Steps 0–2 and the untargeted curve intervals, the extra sample,
   and contour identity/incidence in the candidate. Compare published and
   rejected states, tree/seed/count changes, angles and shape/size tails
   by element type and region, and sampled XYZ error. Record native
   global curvature error for TRI with source-count binding. Require
   evidence that the shape gain is not just a transfer of the worst element
   to another face or region before considering promotion.

The researcher decision determines whether the new local rule can run.
The [preparation receipt](evidence/LOCAL_CONTOUR_SPACING_TRIAL_DESIGN_20261120.json)
binds the archive bytes, the original curve-stage partitions and computed
geometry. No new native scientific execution is recorded in this receipt.
