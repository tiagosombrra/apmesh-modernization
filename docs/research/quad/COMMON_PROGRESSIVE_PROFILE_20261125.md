# Common numerical profile for progressive TRI/QUAD feedback

2026-11-25 Fortaleza. [Executable profile](profiles/progressive_admission_development_v1.json).
[Replay evidence](evidence/COMMON_PROGRESSIVE_PROFILE_20261125.json).

## Fixed development profile

Freeze the values before replay. Use the same bytes for every case and
the same targets at the contour edge, at the contour-vertex transition
and in the interior. The profile evaluates an isolated Bézier patch.

| Item | Required for an intermediate candidate | Target for stopping |
| --- | --- | --- |
| Physical minimum TRI angle | 15° | 30° |
| TRI shape score | 0.125 | 0.25 |
| Physical minimum QUAD angle | 22.5° | 45° |
| QUAD scaled corner Jacobian | 0.25 | 0.50 |
| Source-area-weighted geometric RMS | At least 2% relative reduction on both grids | 0.005 model length units or lower on both grids |
| Maximum sampled geometric distance | No increase on either grid | 0.020 model length units or lower on both grids |
| Face cost | At most 10% growth from the predecessor and at most 1,000 faces in the patch | Same bounds |

The target columns use the lower guidance values in the published
[Cubit TRI metrics](https://www.sandia.gov/files/cubit/15.4/help_manual/WebHelp/mesh_generation/mesh_quality_assessment/triangular_metrics.htm)
and [Cubit QUAD metrics](https://www.sandia.gov/files/cubit/15.3/help_manual/WebHelp/mesh_generation/mesh_quality_assessment/quadrilateral_metrics.htm)
for angle and shape. The TRI score is the reciprocal of the normalized
Frobenius condition number for a linear TRI. The APMesh QUAD measure uses
the analytic patch normal at each corner and retains its own definition.
[Verdict technical report, sections 4.4 and 4.12](https://doi.org/10.2172/901967).
The intermediate floors are one half of the targets, chosen as an explicit
development margin for progressive acceptance. Shape and geometric error
remain separate because a lower interpolation error alone does not establish
acceptable element conditioning. These are research requirements and have
no solver-specific qualification. [Shewchuk's conditioning analysis](https://people.eecs.berkeley.edu/~jrs/papers/elem.pdf).

The 2% cut-off requires a meaningful relative improvement on both grids.
The 10% rate bounds cumulative growth over two committed successors to
21%. The 1,000-face absolute limit bounds this single-patch campaign. The
geometric stopping targets are declared study tolerances, with four times
the RMS allowance for the sampled peak. They use the native model length
unit, so re-expressing a surface at a different numerical scale would
require a corresponding change of the absolute tolerances. These numerical
choices are experimental and were fixed independently of which archives
would be considered eligible.

A candidate below a final regional target must preserve or improve the
predecessor's minimum and must not increase the count or proportion of faces
below that target. A newly populated group must meet the target. Every
candidate element must satisfy its safety floors. The existing geometric
comparison uses grids of 24 × 24 and 48 × 48 common UV sites. Meeting
the geometric targets alone cannot stop the experiment as qualified.

## Observed on four certified native archives

| Case | Native mixed faces, predecessor → candidate | RMS reduction at 48 × 48 | Max deviation at 48 × 48 | Transition TRI below safety, predecessor → candidate | Disposition |
| --- | ---: | ---: | ---: | ---: | --- |
| CurvaBezier screened | 732 → 779 | 23.80% | 0.04419 | 68/94 → 57/92 | Blocked |
| CurvaBezier grouped | 732 → 754 | 24.57% | 0.04419 | 68/94 → 55/90 | Blocked |
| CurvaBezier refined | 732 → 789 | 24.34% | 0.04419 | 68/94 → 61/97 | Blocked |
| Ribbed Bracket screened | 547 → 648 | 36.83% | 0.10750 | 37/53 → 23/51 | Blocked |

A transition TRI in this table touches the contour at a vertex and uses
no contour edge. The population counts a face once if either angle or
shape falls below its safety floor. The four archives improve RMS by at
least 2% and reduce the sampled maximum on both grids. All remain below
the 1,000-face ceiling. Ribbed adds 101 faces, exceeding the per-cycle
budget at 18.46%.

CurvaBezier's refined variant removes the interior TRI class and meets
both interior QUAD targets. It still has a transition TRI at 2.27° and
a contour-edge QUAD at 19.44°. Ribbed's worst transition TRI improves
from 3.79° to 6.33° from its own predecessor. Interior TRI remain above
the safety floors but their minimum deteriorates and the number below
the final target increases from two to ten. The evidence retains all
regional blockers and both sampled error comparisons.

The native trace locates the lowest-angle transition TRI at operation 36
on all three CurvaBezier fronts, and operation 26 on Ribbed. Their angles
are already 2.27° and 6.33° at birth and remain identical after smoothing.
The largest ratio between the worst TRI's median edge length and that of
an edge-adjacent face is 8.93 on CurvaBezier and 5.67 on Ribbed at birth.
No transition TRI becomes sub-floor during guarded smoothing on these
archives. Smoothing moves three Ribbed TRI above the floors. These
observations place the common residual problem before smoothing, in the
boundary-to-template transition during reconstruction.

## Scope and continuation

The archived no-request case reports no action. The old selective Ribbed
archive is refused due to its missing native subdivision certificate.
The two directed CurvaBezier variants use their retained native receipts
and plan rows. The first trace attempt assumed identical export order.
The corrected pairing uses oriented face connectivity and matches each
worst TRI to its recorded birth operation.

The profile SHA-256 is
`57dd50497f14d187b8310af38ba4f263798dbf503378943d8c118cc4d14912e7`.
Ten progressive-assessment tests pass locally on the exact assessor tree.
The four [PR 279 exact-head checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45671619225)
pass. There was no new native generation, accepted mixed epoch or reserved
case in this replay.

Use this profile to compare the next common transition-sizing trial.
Trace how the physical size requests at the contour and nearby interior
are realized by boundary splitting and template sizes before the AFT
closes the transition. Require the same rule on both development models
and measure the quality already at birth. Keep native owner reentry,
shared-curve conformity, the reserved corpus and the global mixed
curvature estimator as pending gates.
