# Fixed-contour corner obstruction on CurvaBezier

The starting point is the [native straight-side split trial](NATIVE_STRAIGHT_SIDE_SPLIT_20261126.md).
Its 743-face mesh has 24 certified curve samples, with two QUAD on the
straight side at 44.956273 and 44.967441 degrees. A 45-degree regional
target and the 22.5-degree QUAD safety floor play separate roles.

## Fixed-connectivity projection

A read-only search moves each of the four interior vertices of the two
target QUAD separately. It tests 360 directions per vertex, from a
fraction of the shortest incident UV edge to one quarter of that edge.
In each crossing direction, 36 bisection iterations locate the first
sampled crossing of 45 degrees. The lift uses the analytic Bézier net.
Neighborhood checks use the five guarded scores, physical facet
alignment, the safety floors, and article S and relative pair residual
on the affected advance QUAD. The 2,709 angle-crossing probes yield
zero moves that preserve the article screen and the neighborhood scores.
The two vertices farther from the corner cannot lift the physical
corner angle because neither supplies a ray of that angle.

| Measurement | Native operation 17 projection | Native operation 20 projection |
| --- | ---: | ---: |
| Interior node ID | 839 | 886 |
| Shortest sampled physical displacement to 45° | 0.000225384 | 0.000167853 |
| Adjacent advance QUAD S in UV, before | 1.500000 | 1.500000 |
| Adjacent advance QUAD S in UV, after | 1.500445 | 1.500994 |
| Area-weighted geometric RMS, 48 × 48 | 0.003674218 | 0.003674212 |
| Maximum geometric deviation, 48 × 48 | 0.018789543 | 0.018789048 |
| Below-safety-floor faces | 23 | 23 |

Both projected OBJ files keep all 24 contour sites, certified IDs and
coordinates, all face incidences, and the carriers and measured sizes
for the seven requests. The changed faces have no measured overlap
above the existing UV tolerance, and the full chart remains covered.
The largest adjacent size ratio remains 4.850910955. The native split
control has geometric RMS 0.003674192 and maximum 0.018789543 on the
same samples. Both projections lower the below-target contour QUAD
count from seven to six in the profile replay. The remaining three
profile blockers persist. Operation 17 worsens the worst adjacent QUAD
edge ratio. Operation 20 worsens both the worst adjacent QUAD corner
Jacobian and edge ratio. Neither projected mesh is eligible.

## Why a joint displacement cannot repair this connectivity

At each UV corner, the two original QUAD partition the 90-degree
angle. The article condition S ≤ 1.5 gives each QUAD a corner angle
of at least 45 degrees in UV. Thus the common edge must stay on the
UV bisector. This conclusion also holds if the other interior
vertices move with the shared vertex.

Write the common vertex as (t, 1−t) at the left corner and (1−t, 1−t)
at the right corner, with 0 < t < 1. Let Y be the positive distance
along the physical straight-side ray, X the transverse in-plane
component, and Z the height. The independent Bézier control net gives

- Y = 3t/2 + 3t²/2 − t³.
- X = Y − (3/2)t⁴(1−t).
- Z = (9/2)t³(1−t)³ on the left, and (9/2)t⁴(1−t)² on the right.

The 45-degree condition would require X² + Z² ≥ Y². Since X ≥ 0
and Y ≥ 3t/2, the difference Y² − X² is at least (9/4)t⁵(1−t).
The ratio of Z² to that lower bound is at most 3125/5184 on the
left and 9/64 on the right. Both are strictly less than one. The
physical angle on the straight-side QUAD is therefore strictly
below 45 degrees everywhere on the admissible bisector. An exact
rational check binds the formulas to the stored net and verifies the
inequality at 126 interior samples. The bound provides the conclusion
between samples. This obstruction applies to these corners and this
connectivity. It does not exclude a different mesh topology.

## Existing-site layout search

The existing directed local layout enumerator checks edge-connected
patches containing both affected QUAD at each corner. It retains the
directed patch perimeter and every existing site. The search allows up
to six original faces, 14 sites, and eight replacement faces, within
the fixed global growth allowance. It checks safety floors, S for
each replacement QUAD, and archived size requests. A successful layout
would need to meet the unchanged regional angle and shape targets of
both exterior edges for their resulting face types.

| Operation | Patches checked | Floor-valid layouts | Both corner-edge targets met |
| --- | ---: | ---: | ---: |
| 17 | 262 | 2,882 | 0 |
| 20 | 134 | 1,301 | 0 |

One additional patch is outside the search scope. No per-patch
state or layout cap is reached. The existing pair gives the best
minimum target margin at each corner. Larger patches and additional
sites remain unmeasured.

## Verification and handoff

Both diagnostic commands exit successfully on the bound local
archive. The [receipt](evidence/FIXED_CONTOUR_CORNER_OBSTRUCTION_20261126.json)
includes script and artifact hashes, exact native input and profile,
per-face changes, and the 24 × 24 and 48 × 48 comparisons. The four
checks for the unchanged [PR 297 source](https://github.com/tiagosombrra/apmesh-modernization/pull/297)
remain green on its exact revision. No new compiler, native generation,
CTest, or full Python suite runs belong to this diagnostic. Zero mixed
adaptive epochs are accepted.

Use the 24-site archive as the CurvaBezier control. Compare the
eight residual far-below-target straight-side TRI at birth with the
existing Ribbed Bracket transition trace. Test whether the physical
edge-length and available-height relation identifies the same
interface mechanism before projecting a common intervention.
