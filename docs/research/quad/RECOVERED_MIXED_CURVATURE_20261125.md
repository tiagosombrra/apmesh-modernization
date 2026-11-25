# Curvature and size requests on the recovered CurvaBezier mesh

Recorded 2026-11-25 Fortaleza. [Commands, identities and numeric receipt](evidence/RECOVERED_MIXED_CURVATURE_20261125.json).

Run the exact PR 267 grouping and recovery on CurvaBezier Step 3, retry 0.
Move the selected copy aside and restore it from the recorded OBJ and front.
Its byte identity matches the archived eligible mesh. Compare the restored
TRI/QUAD, its mixed predecessor and the original TRI control with the same
nodal quadratic-jet probe from PR 243. Check both approved support experiments,
bounded expansion and a complete second neighborhood. Probe coefficients and
curvatures agree with the independent QR audit and all 54 forged records are
rejected across the six mesh/policy pairs. Both existing native/independent
CTest groups pass. This diagnostic comparison evaluates analytic K and H
at the actual embedded UV sites. The original TRI global curvature policy
is separate from fitting the same diagnostic on its TRI mesh.

## Accuracy by region

The recovered mesh has 683 valid estimates under each support choice.
The transition group contains the interior vertices of faces incident on
a contour vertex. The boundary group has 14 unchanged contour sites.
The medians below describe absolute differences in inverse-square model
units for Gaussian K and inverse model units for mean H.

| Group | Bounded K | Complete second ring K | Bounded H | Complete second ring H |
| --- | ---: | ---: | ---: | ---: |
| Whole patch, 683 nodes | 0.0004503 | 0.0014892 | 0.0015156 | 0.0052398 |
| Boundary, 14 nodes | 1.3093 | 1.4976 | 1.6817 | 0.9987 |
| Transition, 98 nodes | 0.007985 | 0.005896 | 0.05560 | 0.07894 |
| Interior, 571 nodes | 0.0002157 | 0.0007702 | 0.0008598 | 0.0027916 |

Using a complete second neighborhood improves the median of boundary H
and transition K, while degrading boundary K, transition H and both
interior medians. The boundary maximum errors persist with both policies.
Comparing predecessor and recovered meshes at exactly the same UV, the
median change in absolute error on the 14 contour points is zero for K
and H under both policies. The frozen grouping footprint contains only
one vertex in the final meshes, so any zonal claim there requires more nodes.
The output gives full diagnostic coverage. Boundary accuracy remains open,
along with the global mixed curvature aggregate and its acceptance rule.

## Read-only handoff to the existing geometric sizing pilot

Replay the previously approved sampled geometric residual and three
gradation passes from each final mixed OBJ. Both meshes produce the same
13 physical face requests, with exactly equal physical sizes and exactly
equal UV positions, mapping to the same eight distinct native leaf boxes
in their corresponding front traces. Face indices differ because the
grouping changes the mesh topology. The recovered mesh is directly
consumable by this existing request calculation. The observed local
improvement alone produces no difference in the requested leaves for this
case. Feasibility under the depth cap, native reconstruction and acceptance
are still unmeasured at this point.

## Next action

Exercise a bounded native trial driven by the recovered mesh's already
measured geometric requests, preserving the native limits and maintaining
a matched predecessor control. Report actionable and saturated requests and
retain the previous mesh on failure. Separate the pilot's geometric sizing
from the unqualified curvature estimator. A scientific rule for counting
an accepted mixed epoch remains required under issue 221.

No change to the generator, estimator or thresholds is included here.
PRs 243, 265, 266 and 267 each have four successful hosted checks on their
own heads. No new integration or accepted mixed adaptive cycle.
