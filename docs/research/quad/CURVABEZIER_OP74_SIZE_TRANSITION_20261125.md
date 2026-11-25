# CurvaBezier operation 74 and the physical transition at leaf 148

2026-11-25 Fortaleza. [Machine-readable evidence](evidence/CURVABEZIER_OP74_SIZE_TRANSITION_20261125.json).

## Origin of the limiting face

The read-only analysis binds the grouped CurvaBezier Step 3 output from
[PR 278](https://github.com/tiagosombrra/apmesh-modernization/pull/278),
head `e93205007b8f937b72d7b612694cbc8091c637dc`. All four exact-head
hosted jobs passed, including the original TRI equivalence checks.

The limiting interior TRI is born at operation 74 and shares an edge of
0.053825 model units with the template from leaf 148. Its other edges
measure 0.136866 and 0.166590. The neighboring template has a median
physical edge of 0.059163, versus 0.136866 in the limiting TRI and
0.166590 in the neighboring transition TRI on the opposite side. The
active edge separates level-4 leaf 148 from level-3 leaf 154. Leaf 154
touches the source contour and receives no template. The limiting face's
source residual divided by its median edge is only 0.009460. This is
measured after reconstruction and neither reinterprets the actual source
seed list nor changes the existing request trigger.

Across all 74 archived front states in which that edge is active, the
best possible local TRI angle at birth is 17.09 degrees, the angle that
was obtained. No shape-eligible QUAD uses the edge in those recorded
states. At operation 74 the chosen apex is the only valid one even when
all active vertices are considered. A different order could visit other
states. The archived trajectory offers no more suitable closure on this
edge.

## Local checks at fixed topology or fixed positions

Seventeen connected cavities of up to five generated faces form a simple
boundary with all their existing vertices. Nineteen nonidentity
reconnections preserve the face counts by region and are valid at the
recorded birth and final positions. None meets the existing angle and
shape diagnostic floors.

The five existing guarded smoothing passes improve the target from
17.09 to 18.16 degrees. An analytic-geometry sweep tests each of its
three nodes independently at UV offsets on a 1/2048 grid inside a radius
of 0.03125. The sweep preserves connectivity and compares the five
incident-neighborhood score components used by the native guard. Some
positions clear the two TRI floors when only local physical validity is
checked. None does so with the measured neighborhood score guard.
The largest guarded single-vertex improvement on the sampled stencil
reaches 18.52 degrees. The sweep is a diagnostic on three single-vertex
stencils. It does not establish a native alternative smoothing rule or
exclude simultaneous movements.

## Projected refinement of the coarser neighbor

Refining leaf 154 on the ungrouped screened control yields four level-4
children and keeps projected edge-wise 2:1 balance. The two children
touching the curve stay outside template dispatch. The two inner children
pass the existing analytic-contour clearance check, with a positive
minimum margin of about 0.00799 in UV. The original 16 contour sites and
their ordering are retained in this projection. The selected request
site (0.09375, 0.796875) belongs strictly inside predecessor face 636
(zero-based) and to leaf 154. The reference physical size, 0.059163, is
the measured median edge of the adjacent template QUAD. The existing
native request path would add one level at this location. Its projected
leaf count changes from 226 to 229 with the existing requests included.

The already tested grouping refuses a finer request in a neighboring
leaf. The proposed native trial therefore starts on the ungrouped
screened control. It would add one request and keep the existing
certificate, pair screen, smoother, and diagnostic floors. Compare the
entire native stage, including the two new template cells, region
quality, sampled error, and growth. The prediction about cells provides
no claim about the quality of the actual front closure. Alignment on
the native trial is pending. No new native mesh or admitted mixed epoch
in this diagnostic.
