# Cross-model short-base transition test

Compare the [743-face CurvaBezier archive](NATIVE_STRAIGHT_SIDE_SPLIT_20261126.md)
with the [541-face Ribbed Bracket archive](FRONT_BIRTH_SHAPE_TRIAL_20261126.md)
from the same PR 297 source. Also bind the earlier
[23-site Ribbed front replay](RIBBED_LIMITING_TRI_FRONT_TRACE_20261123.md)
as a historical check on the mechanism. The quality profile, physical
angle floor of 15 degrees for TRI, and article UV condition S ≤ 1.5
for QUAD remain in force.

## Cause recorded at birth

For each TRI with exactly one contour vertex, take the opposite side
as the base and bind its owner and active front state. Measure its
physical length L, perpendicular height h, and foot offset d from
its midpoint. The other relevant length is the shorter of the two
certified contour chords incident to the apex.

For a hypothetical symmetric change of base width at fixed midpoint,
direction, and apex, a minimum angle θ requires the half-width r to
satisfy both bounds:

- r ≥ √((h / sin θ)² + d²) − h cot θ, from the apex angle.
- r ≤ h cot θ − |d|, from the smaller base angle.

This interval classifies the footprint. It is not a proposed rule
for moving template vertices. The Bézier map would need to be
evaluated again for any changed UV geometry.

| Observation at birth, physical units | CurvaBezier straight side | Ribbed current |
| --- | ---: | ---: |
| TRI with one contour vertex inspected | 18 | 38 |
| Below the TRI safety floor | 8 | 13 |
| Short base owned by a template | 6 | 13 |
| Short base length | 0.06845–0.06973 | 0.12500–0.25001 |
| Altitude above that template base | 0.09929–0.09932 | 0.53023–1.03827 |
| Shorter contour chord / template base | 7.17–7.30 | 2.00–4.00 |
| Width multiplier required at the archived midpoint, minimum | 1.47–2.44 | 1.11–1.26 |

Every one of these 19 short-base cases has only one acceptable
apex in the independent UV and physical validity replay of its
archived active front. None of those choices meets the physical
floor. The historical Ribbed operation 27 reproduces its 6.32815-degree
limit, with three valid apices and a minimum hypothetical width
multiplier of 2.38 at the selected midpoint. A single global ratio
of contour-chord length to template-base length would miss that the
same physical mechanism occurs at ratios as low as 2.00 in Ribbed.

The two other CurvaBezier failures at operations 102 and 103 have
no original seed owner on the base. For each, the lateral offset
already exceeds h cot θ. Its fixed-center interval is empty. This
is a distinct low-height and alignment problem, excluded from the
short-base repair projection. The existing immediate-parent
template grouping screen also refuses all 19 short-base cases
because the eligible seeded sibling sets are incomplete.

## Common one-layer closure projection

Reuse the existing directed patch enumeration and local tiler.
Visit the remaining short-base failures from worst final angle.
Each region contains the target and an adjacent template layer.
Use the first conforming replacement within the existing search
and growth budgets. Preserve the ordered perimeter, the analytic
contour and node IDs, the optional introduced Ribbed point, and
coordinates of every retained node. An interior site can retire
only when all its incident faces are part of the replacement.
Selected regions have disjoint face sets.

Check shape, S, facet orientation, area and overlap at both the
archived birth and smoothed positions. Check every request incident
to a changed face at either position using the native after-smoothing
rule. Keep all previously met requests on the completed mesh.
Stitch the combined
projection into each original mesh and replay the frozen
profile with the exact predecessor and common 24 × 24 and
48 × 48 sites.

| Whole-mesh measurement | CurvaBezier control → projection | Ribbed control → projection |
| --- | ---: | ---: |
| Selected disjoint regions | 4 | 7 |
| Persistent diagnosed TRI repaired | 6 of 6 | 8 of 11 |
| Faces below any physical floor | 23 → 17 | 12 → 4 |
| Worst angle in a replacement, both stages | 15.70° | 16.44° |
| Faces | 743 → 743 | 541 → 546 |
| QUAD | 661 → 653 | 483 → 464 |
| Largest adjacent physical size ratio | 4.85 → 4.85 | 4.84 → 4.46 |
| Area-weighted geometric RMS at 48 × 48 | 0.003674192 → 0.003674364 | 0.020102640 → 0.020078941 |
| Maximum sampled geometric deviation at 48 × 48 | 0.018789543 → 0.018789543 | 0.107484106 → 0.107484106 |

Each selected region retires one fully enclosed interior site.
Control and projection preserve 24 and 26 contour sites, and four
and 11 satisfied physical requests, respectively. There are three
protected requests incident to the Ribbed replacements. A preliminary
projection that checked only previously met requests on final
faces reached two remaining Ribbed floor failures. Applying the
native incident-request rule changes the admissible regions and
leaves four. The ordered search leaves operations 44, 56 and 82
unresolved. A different selection order remains unmeasured.
The loss of QUAD counts is part of this measured trade-off.

Both combined projections retain the same admission blockers as
their respective controls, including at least one physical-floor
block. Neither profile admits a mixed epoch. The evidence covers
two development surfaces, with no reserved case or shared curve.
The geometry RMS is a positional measure. The global mixed-curvature
error remains open.

## Verification and next action

Both read-only Python commands complete on the bound archives.
The [receipt](evidence/CROSS_MODEL_SHORT_BASE_TRANSITION_20261126.json)
records input and output hashes, tested apices, both angle constraints,
per-region replacements, and the whole-mesh check. The existing four
hosted jobs for [PR 297](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45806459734)
pass at source 0ad5b7bd. This round has no new native generation,
build, CTest or production source change.

The next scientific decision is whether to test an opt-in native
batch of disjoint local repairs on the same two controls. Apply
the existing closure, fixed contour, and shape checks to the
whole batch, with complete rollback on failure. Measure the same
face counts, geometric error and request coverage, and retain all
unchanged profile decisions. Full-profile eligibility, shared
curves, owner reentry, reserved cases and two consecutive accepted
mixed epochs remain open.
