# Boundary, transition, and interior size gradation

22 November 2026, Fortaleza. The researcher requires the next mixed
adaptation stage to consider the interaction of curved and straight
contour intervals with the sizes used inside the patch. Preserve local
resolution differences while measuring abrupt changes and poor element
shape. This is a read-only analysis of the three reference Step 1-3
meshes and the [two-block trial Step 3](TWO_BLOCK_TEMPLATE_TRIAL_20261122.md).

## Measurement

Bind each oriented contour interval to its native source identity, physical
chord and exact adjacent element. Measure face size as the median of its
physical edge lengths. Starting with the face using that contour interval,
visit up to three face-to-face steps via shared edges. For each outgoing
link, divide the larger face size by the smaller. Report this graph
distance independently of the faces that touch an endpoint without using
any contour edge. Those vertex fans expose narrow TRI even when the face
using the original boundary edge is well shaped. Sample analytical
Gaussian curvature at the mean UV of the visited faces and compute distance
from the stored arc midpoint to each physical boundary chord. The Gaussian
samples indicate surface bending locally; neither metric defines a sizing
or acceptance threshold.

Each reference interval and each two-block interval passes the original
curve identity and oriented incidence audit, with 46 intervals across all
four meshes. The pair of Step 3 meshes has byte-identical source-site
records. The [evidence](evidence/MIXED_BOUNDARY_GRADATION_20261122.json)
stores every interval's chord, topology and measurement. It also retains
the full three-layer profile for both halves of the straight side adjacent
to the two-block modification.

## Findings

The junction between the curved side and either adjoining straight side
changes from 1.07 to 1.84 to 3.66 in incident chord ratio over Steps 1-3.
The curved Step 3 chords are approximately 0.273 physical units and the
straight chords are 1.000. Straight/straight junction chords retain a
ratio of 1.0. Curve chord deviation at the recorded arc midpoint is
zero on the straight sides, while the maximum on the curved side
decreases from 0.1041 at Step 1 to 0.0082 at Step 3.

The straight half interval at `u=0, v=0.5..0` next to the curved end has
an immediate face-size jump up to 2.05 in Step 3. The largest ratio within
three shared-edge steps is 5.40. Its equally long complementary
half has an immediate maximum of 1.69 and a maximum of 4.19 within three
steps. Maximum sampled absolute analytical Gaussian curvature rises from
approximately 0.017 on the owner face to 3.09 within three steps near the
curved end. The complementary half has values at most 0.143 along its
profile. These are local observations of the different surrounding
surface geometry on one patch, not isolated evidence of a causal
curvature-to-size transfer rule.

| Step 3, straight half next to the curved end | Reference | Two-block trial |
| --- | ---: | ---: |
| Physical contour chord | 1.000 | 1.000 |
| Largest immediate neighboring size ratio | 2.05 | 1.96 |
| Largest neighboring size ratio within three steps | 5.40 | 4.86 |
| Smallest angle among endpoint-only fan faces | 3.10° | 5.02° |

The two-block comparison changes the interior template layout with the
same contour. It shows that the interior can improve part of the transition.
Both snapshots retain a much coarser straight contour than the connected
interior faces near this interval.

## Required evaluation on the next adaptive comparison

Use both geometric demand and the sizes from the adjacent region when
defining curve and interior refinement. A straight interval may need
finer sampling next to a more curved portion, while the interior must
also grade out of small contour intervals. Carry the influence locally
and retain different densities where the geometry warrants them. Compare
chord transitions at junctions, shared-edge size ratios and worst shape by
element type, including the endpoint-only fan. Report physical approximation
error, node and element growth, and whether the actual previous mixed state
drives the next accepted state.

The legacy Adapter already has a triangle-neighbor size pass, with a 1.35
neighbor ratio step and a 1.18 inward growth limit on the target field,
and a patch-level curve/domain balance signal. These are reusable
candidate inputs for a typed mixed contract. The values operate on old
TRI target sizes or aggregate patch counts and have no automatic
interpretation as limits on measured emitted mixed edge ratios. Align
any resulting local two-way sizing rule before changing sampling or
refinement. The earlier one-interval curve split remained unexecuted.
The existing smoothing trial proposal remains pending, with this
gradation accounting to be retained in its comparison.

The diagnostic command was
`python build/quad-gradation-20261122/audit.py`. No C++ change, new native
generation or CTest/hosted check was run. Previous-mixed-state adaptive
admission remains open under
[issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).
