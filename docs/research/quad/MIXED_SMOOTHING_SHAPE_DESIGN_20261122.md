# Local smoothing shape acceptance design

22 November 2026, Fortaleza. The current goal is a mixed mesh whose own last
accepted state drives subsequent adaptation while producing well-shaped TRI and
QUAD wherever the geometry and target sizes permit. This work item isolates a
quality loss in the current five-pass UV smoothing. It uses the archived
fixed-`1.5` original article-front Step 2 and the
[two-block Step 3](TWO_BLOCK_TEMPLATE_TRIAL_20261122.md).

## Recorded moves and local measurements

All contour coordinates and face connectivity agree through the five archived
passes. For each nonzero first-pass move, test that displacement on the starting
geometry with the other vertices fixed. Evaluate a full move and the fractions
1/2, 1/4 and 1/8 as separate geometric queries. Lift each tested location onto
the analytic surface. These are incident-element measurements on one frozen
frame; no alternative smoothing pass or candidate mesh is constructed.

- The Step 3 limiting TRI with fixed corner `(1, 1)` goes from 6.95° to
  2.59° in the recorded first pass and ends at 1.87°. Moving node 286
  alone by the full recorded displacement yields 2.61°. At one eighth of
  the displacement the triangle itself measures 6.46°, and the incident
  QUAD minima and edge ratio still worsen. The other moving corner node
  also worsens at least one incident shape statistic at each tested length.
- The Step 2 boundary QUAD goes from 25.85° with corner Jacobian 0.423 to
  16.24° and 0.158 in the recorded first pass. Moving node 48 alone by
  the full displacement drops that corner Jacobian to 0.142. Halving
  this move keeps the witness at 25.85° and 0.423, while its incident TRI
  minimum area-based quality improves from 0.367 to 0.512 and the largest
  incident QUAD edge ratio falls from 9.24 to 6.78.

| First-pass local observations | Step 2 | Two-block Step 3 |
| --- | ---: | ---: |
| Interior vertices with a nonzero recorded move | 179 | 112 |
| At least one shape-preserving fraction using TRI q, QUAD J and QUAD edge ratios | 89 | 8 |
| At least one preserving those scores and minimum angles | 79 | 8 |
| Full / half / quarter / eighth among the latter (longest first) | 52 / 21 / 4 / 2 | 4 / 2 / 1 / 1 |

The counts compare each observation to the same pass-start snapshot.
Other moves would change each decision in a sequential candidate. The
checks reject a local orientation, convexity or shape failure in this
diagnostic. A complete pass must also validate global geometry. Step 3
already has 557 stationary interior nodes in the recorded first pass.
The strict proposed gate may preserve good starting shapes and suppress
much of the recorded geometric-error gain.

## Proposed comparison requiring scientific alignment

Use the same mixed connectivity and original contour for both archives.
Keep five passes and the existing mean of distinct incident neighbors in UV.
At the beginning of each pass compute all targets using a single frozen
geometry. Visit interior vertices in ascending recorded ID, and test the
line segment from its still-current position to its target at fractions
1, 1/2, 1/4 and 1/8. Try each tentative position using the immediately
current incident faces after earlier accepted moves. Re-lift to physical
space using the existing analytic surface mapping.

For each incident element type present, protect the minimum physical angle.
Protect the minimum TRI area-to-edge shape score, the minimum signed QUAD
corner Jacobian and the maximum QUAD edge ratio. Accept the first locally
valid move for which all these statistics are at least as good and one
improves. Treat differences at most `1e-12 * max(1, abs(old), abs(new))`
as floating-point ties in each statistic. No accepted trial leaves a node
off the analytic surface. If no trial qualifies, keep the node in place.
Retain the existing complete-pass validity checks. A geometric rejection
restores that pass atomically to its previous positions and is recorded;
engineering or resource failures still propagate. Keep the original
five-pass smoother as the reference.

Run one comparison of the same two real pre-smoothing archives, avoiding
rerunning unrelated generators. Record accepted fractions, blocked moves
and pass rejections. Report minima, tails and fractions with severe elements,
per-type TRI/QUAD shape and adjacent element size ratios by region, plus
sampled physical RMS and maximum deviation. Verify that the contour,
connectivity and node counts are identical. These are diagnostics on the
already generated states; sampled geometric RMS retains its existing meaning.

## Adaptive completion target

The current mixed workflow inherits the adaptive TRI sizes. The archived
curved contour interval count is 2, 4 and 8 on Steps 1-3, and all three
straight sides keep two intervals each. Over those steps the archived
median exposed template edge decreases from 0.125 to 0.0625 to 0.03125 in
UV. This shows varying subdivision in the source history. The mixed
workflow has zero accepted epochs driven by a previous mixed mesh.

The [adaptive milestone](https://github.com/tiagosombrra/apmesh-modernization/issues/221)
requires a qualified mixed curvature/quality evaluation, an owned accepted
mixed state that demonstrably drives the next curve size and quadtree/AFT
reconstruction, and strong acceptance/rollback. Validate at least two
distinct accepted mixed epochs with provenance, monitored quality, error
and size gradation. Preserve the original curve sampling and default TRI
controls as reference. This gate distinguishes smoothing quality on a
fixed-connectivity mesh from using that mesh's own error to drive the next
refinement or coarsening. The research queue should return to the adaptive
feedback contract after the bounded smoothing item.

The [receipt](evidence/MIXED_SMOOTHING_SHAPE_DESIGN_20261122.json) binds the
archived frames and local calculations. The documented command is
`python build/quad-smoothing-policy-20261122/audit.py`. No generator or
native test was run for this design checkpoint. The proposed rule awaits
explicit scientific alignment.
