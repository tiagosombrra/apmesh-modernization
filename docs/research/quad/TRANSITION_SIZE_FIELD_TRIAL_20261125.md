# Add one physical transition seed to the existing graded size field

[Draft PR 285](https://github.com/tiagosombrra/apmesh-modernization/pull/285)
at `d0c9bd10c52b7cd67c53c94783c04e33781d274f` enables this research
rule through `--transition-size-feedback`. The native engine image from
PR 284 and its existing sizes, template dispatcher, advancing front and
smoothing are reused. This is a bounded scientific proposal for single
patches, not an adopted adaptive policy.

An active geometric request is necessary to start the supplemental rule.
From the bound mixed predecessor, consider each TRI with one contour
vertex and a QUAD sharing the opposite edge. Examine its two incident
contour intervals. Rank intervals with no existing request by physical
arc length divided by the opposite physical QUAD edge. Use the existing
gradation ratio of 1.35 as the threshold. Choose the greatest ratio
with source interval and face order as tie rules. Start from the larger
of half the original arc and 1.35 times the QUAD edge. Grade the seed
using the existing three passes and the same factor; use the pointwise
minimum of the supplemental and geometric fields. This can create more
than one curve or leaf request. The native path still makes one binary
curve split per interval and at most one direct level per actionable leaf
under the existing depth cap. The requested physical size is a target.

Both paired arms use the bound ungrouped controls of the
[common contour split trial](COMMON_TRANSITION_CONTOUR_SPLIT_20261125.md).
The geometry-only face and curve requests and the prior extra certified
interval remain as recorded. This isolates the effect of the supplemental
field without a conflict with protected group plans. The controls keep
their earlier geometric settings: CurvaBezier uses its recorded relative
tolerance and Ribbed its recorded absolute selection. The supplemental
rule is identical in both models. Both start with the exact same source
TRI, mixed predecessor and original tree as their paired counterpart.

| Metric | CurvaBezier control → trial | Ribbed Bracket control → trial |
| --- | ---: | ---: |
| Certified contour segments | 17 → 20 | 23 → 27 |
| Final faces | 788 → 865 | 648 → 706 |
| Growth relative to bound predecessor | 7.65% → 18.17% | 18.46% → 29.07% |
| Final transition TRI below the floor | 47 → 35 | 22 → 26 |
| Worst final transition TRI | 2.47° → 4.24° | 6.69° → 6.69° |
| Worst final interior TRI | 4.43° → 4.43° | 18.37° → 12.54° |
| Largest adjacent physical size ratio | 8.66 → 5.06 | 5.54 → 5.54 |
| Area-weighted geometric RMS on the 48 × 48 grid | 0.0081815 → 0.0031697 | 0.0173285 → 0.0097524 |
| Maximum geometric deviation on the 48 × 48 grid | 0.0441922 → 0.0186840 | 0.1074959 → 0.0515128 |

The control and candidate errors use identical analytic sample sites.
The adopted comparison threshold is still 15° for TRI and the growth
limit is still 10 percent. Both native outputs stage and fail the
frozen admission profile. The Ribbed control is already above budget.

The initial size ratios for the selected intervals are 17.59 and 8.84.
The graded targets exceed what the binary or one-level operations can
deliver at several sites. Five of six new CurvaBezier face requests
and three of eight new Ribbed face requests remain above target at
birth, using the smallest incident face at each site. One of three new
CurvaBezier intervals and three of four new Ribbed intervals have a
child arc above target. Three added CurvaBezier face requests are
capped at the native depth. The capped request count and the measured
oversize count are different quantities.

In CurvaBezier, both limiting transition TRI meet the selected contour
interval. The candidate limit uses the newly added point. In Ribbed,
the original limiting TRI is born at the same UV coordinates before
and after, outside the new contour intervals. The selection by largest
size ratio chooses a distinct area. This explains the unchanged local
angle in the measured meshes, while extra elements elsewhere improve
the geometry error.

## Validation and next step

Six Python sizing controls and ten progressive admission controls
pass. The first test fixture had every interval already requested; it
now verifies the no-duplicate outcome. The native comparisons ran on
the retained MSVC 19.44 x64 Debug C++17 image. Seven artifacts match
the earlier ungrouped run byte for byte in each control. Independent
curve integration verifies the actual child sizes. The normal portable
CLI stages and assesses Ribbed using the new switch; it is distinct
from the matched pair because it omits the earlier extra split.
The earlier Windows article rollback gate is not requalified here.
[PR 285 hosted run](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45708114543)
was pending. [Native evidence](evidence/TRANSITION_SIZE_FIELD_TRIAL_20261125.json)
records commands, hashes, per-region metrics and unmet sizes.

Next align selection that prioritizes the region limiting quality and a
realizable subset of discrete requests within the frozen budget. Compare
with the retained grouped controls that fit the budget before projecting
a new native plan. Preserve existing geometry requests and protected
group rules. No accepted mixed adaptive cycle, shared-curve or reserved
model qualification. Global mixed curvature error remains pending.
